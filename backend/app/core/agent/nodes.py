"""
Agent workflow nodes for planning, execution, and verification.

Implements the core logic for each phase of the agent workflow.
"""
import json
from typing import Dict, Any

from app.core.agent.state import AgentState
from app.core.llm.watsonx_client import watsonx_client
from app.core.llm.tools import tool_executor
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def planning_node(state: AgentState) -> AgentState:
    """
    Planning node: Generate a detailed plan for task completion.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with plan
    """
    logger.info(f"Planning node - Task: {state['task_id']}, Iteration: {state['iteration_count']}")
    
    task_description = state["task_description"]
    previous_results = state.get("execution_results", [])
    
    # Build planning prompt
    prompt = f"""You are an AI task planning assistant. Analyze the following task and create a detailed execution plan.

Task: {task_description}

"""
    
    if previous_results:
        prompt += f"""Previous execution results:
{json.dumps(previous_results, indent=2)}

Based on the previous results, refine the plan to address any issues or complete remaining work.

"""
    
    prompt += """Create a detailed plan with the following structure:
1. Break down the task into clear, actionable steps
2. For each step, specify:
   - Step number and description
   - Required tools or actions
   - Expected outcome
   - Dependencies on previous steps

Respond in JSON format:
{
  "analysis": "Brief analysis of the task",
  "steps": [
    {
      "step_number": 1,
      "description": "Step description",
      "action": "tool_name or action type",
      "expected_outcome": "What should result from this step",
      "dependencies": []
    }
  ],
  "success_criteria": "How to determine if the task is complete"
}
"""
    
    try:
        # Generate plan using Granite
        response = await watsonx_client.generate(prompt)
        
        # Parse JSON response
        plan = json.loads(response)
        
        # Update state
        state["plan"] = plan
        state["plan_steps"] = plan.get("steps", [])
        state["messages"].append({
            "role": "assistant",
            "content": f"Plan created with {len(plan.get('steps', []))} steps"
        })
        
        logger.info(f"Plan created with {len(plan.get('steps', []))} steps")
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse plan JSON: {e}")
        state["plan"] = {
            "analysis": "Failed to parse plan",
            "steps": [],
            "success_criteria": "Unknown"
        }
        state["error"] = f"Planning error: {str(e)}"
    except Exception as e:
        logger.error(f"Planning error: {e}")
        state["error"] = f"Planning error: {str(e)}"
    
    return state


async def execution_node(state: AgentState) -> AgentState:
    """
    Execution node: Execute the planned steps.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with execution results
    """
    logger.info(f"Execution node - Task: {state['task_id']}")
    
    plan_steps = state.get("plan_steps", [])
    
    if not plan_steps:
        logger.warning("No plan steps to execute")
        state["error"] = "No plan steps available for execution"
        return state
    
    execution_results = []
    
    for step in plan_steps:
        step_num = step.get("step_number", 0)
        description = step.get("description", "")
        action = step.get("action", "")
        
        logger.info(f"Executing step {step_num}: {description}")
        
        try:
            # Determine if this is a tool call or direct execution
            if action in ["search", "python_exec", "web_search"]:
                # Execute tool
                result = await execute_tool_step(step, state)
            else:
                # Execute with LLM
                result = await execute_llm_step(step, state)
            
            execution_results.append({
                "step_number": step_num,
                "description": description,
                "result": result,
                "status": "completed" if result.get("success") else "failed"
            })
            
            # Add to tool calls if it was a tool
            if action in ["search", "python_exec", "web_search"]:
                state["tool_calls"].append({
                    "tool": action,
                    "input": step,
                    "output": result
                })
            
        except Exception as e:
            logger.error(f"Error executing step {step_num}: {e}")
            execution_results.append({
                "step_number": step_num,
                "description": description,
                "result": {"success": False, "error": str(e)},
                "status": "failed"
            })
    
    state["execution_results"] = execution_results
    state["messages"].append({
        "role": "assistant",
        "content": f"Executed {len(execution_results)} steps"
    })
    
    logger.info(f"Execution complete: {len(execution_results)} steps")
    
    return state


async def execute_tool_step(step: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
    """
    Execute a step that requires a tool.
    
    Args:
        step: Step definition
        state: Current agent state
        
    Returns:
        Tool execution result
    """
    action = step.get("action", "")
    description = step.get("description", "")
    
    # Prepare tool input based on action type
    if action == "python_exec":
        # Extract code from description or generate it
        tool_input = {"code": description}
    elif action in ["search", "web_search"]:
        tool_input = {"query": description}
    else:
        tool_input = {"input": description}
    
    # Execute tool
    result = await tool_executor.execute(action, tool_input)
    return result


async def execute_llm_step(step: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
    """
    Execute a step using the LLM.
    
    Args:
        step: Step definition
        state: Current agent state
        
    Returns:
        LLM execution result
    """
    description = step.get("description", "")
    expected_outcome = step.get("expected_outcome", "")
    
    prompt = f"""Execute the following step:

Step: {description}
Expected Outcome: {expected_outcome}

Task Context: {state['task_description']}

Provide a detailed response for this step."""
    
    try:
        response = await watsonx_client.generate(prompt)
        return {
            "success": True,
            "output": response
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def verification_node(state: AgentState) -> AgentState:
    """
    Verification node: Verify task completion and quality.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with verification results
    """
    logger.info(f"Verification node - Task: {state['task_id']}")
    
    task_description = state["task_description"]
    plan = state.get("plan", {})
    execution_results = state.get("execution_results", [])
    
    # Build verification prompt
    prompt = f"""You are an AI verification assistant. Verify if the task has been completed successfully.

Task: {task_description}

Plan:
{json.dumps(plan, indent=2)}

Execution Results:
{json.dumps(execution_results, indent=2)}

Analyze the results and determine:
1. Has the task been completed successfully?
2. What is the quality of the results?
3. Are there any issues or improvements needed?
4. Should the agent continue with refinements or is the task complete?

Respond in JSON format:
{{
  "task_complete": true/false,
  "quality_score": 0-100,
  "issues": ["list of issues if any"],
  "improvements": ["list of suggested improvements"],
  "summary": "Brief summary of verification",
  "final_result": "The final result or output of the task"
}}
"""
    
    try:
        response = await watsonx_client.generate(prompt)
        verification = json.loads(response)
        
        state["verification_status"] = verification
        state["verification_passed"] = verification.get("task_complete", False)
        
        if verification.get("task_complete"):
            state["final_result"] = verification.get("final_result", "Task completed")
            state["should_continue"] = False
        else:
            state["should_continue"] = state["iteration_count"] < state["max_iterations"]
        
        state["messages"].append({
            "role": "assistant",
            "content": f"Verification: {verification.get('summary', 'Complete')}"
        })
        
        logger.info(f"Verification complete: {verification.get('task_complete', False)}")
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse verification JSON: {e}")
        state["verification_status"] = {
            "task_complete": False,
            "quality_score": 0,
            "issues": ["Failed to parse verification"],
            "summary": "Verification parsing error"
        }
        state["error"] = f"Verification error: {str(e)}"
    except Exception as e:
        logger.error(f"Verification error: {e}")
        state["error"] = f"Verification error: {str(e)}"
    
    # Increment iteration count
    state["iteration_count"] += 1
    
    return state


def should_continue(state: AgentState) -> str:
    """
    Determine if the agent should continue or end.
    
    Args:
        state: Current agent state
        
    Returns:
        "continue" to re-plan, "end" to finish
    """
    # Check if task is complete
    if state.get("verification_passed", False):
        logger.info("Task verified as complete")
        return "end"
    
    # Check if max iterations reached
    if state["iteration_count"] >= state["max_iterations"]:
        logger.warning(f"Max iterations ({state['max_iterations']}) reached")
        state["final_result"] = "Task incomplete: Maximum iterations reached"
        return "end"
    
    # Check for errors
    if state.get("error"):
        logger.error(f"Error in workflow: {state['error']}")
        return "end"
    
    # Continue if should_continue flag is set
    if state.get("should_continue", True):
        logger.info(f"Continuing to iteration {state['iteration_count'] + 1}")
        return "continue"
    
    return "end"

# Made with Bob
