"""
LangGraph workflow definition for the agent.

Creates a StateGraph that orchestrates the planning, execution, and verification cycle.
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any

from app.core.agent.state import AgentState, create_initial_state
from app.core.agent.nodes import (
    planning_node,
    execution_node,
    verification_node,
    should_continue
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_agent_graph() -> StateGraph:
    """
    Create the agent workflow graph.
    
    The graph follows this flow:
    1. Planning: Analyze task and create execution plan
    2. Execution: Execute the planned steps
    3. Verification: Verify results and determine if complete
    4. Decision: Continue (re-plan) or End
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planning", planning_node)
    workflow.add_node("execution", execution_node)
    workflow.add_node("verification", verification_node)
    
    # Set entry point
    workflow.set_entry_point("planning")
    
    # Add edges
    workflow.add_edge("planning", "execution")
    workflow.add_edge("execution", "verification")
    
    # Add conditional edge from verification
    workflow.add_conditional_edges(
        "verification",
        should_continue,
        {
            "continue": "planning",  # Re-plan based on verification
            "end": END  # Task complete or max iterations reached
        }
    )
    
    # Compile the graph
    compiled_graph = workflow.compile()
    
    logger.info("Agent graph created and compiled")
    
    return compiled_graph


class AgentExecutor:
    """
    Executor for running the agent workflow.
    
    Provides a high-level interface for executing tasks through the agent graph.
    """
    
    def __init__(self):
        """Initialize the agent executor."""
        self.graph = create_agent_graph()
        logger.info("AgentExecutor initialized")
    
    async def execute_task(
        self,
        task_id: str,
        task_description: str,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Execute a task through the agent workflow.
        
        Args:
            task_id: Unique task identifier
            task_description: Description of the task to complete
            max_iterations: Maximum number of planning-execution cycles
            
        Returns:
            Final agent state with results
            
        Example:
            ```python
            executor = AgentExecutor()
            result = await executor.execute_task(
                task_id="task-123",
                task_description="Create a Python function to calculate factorial"
            )
            print(result["final_result"])
            ```
        """
        logger.info(f"Starting task execution: {task_id}")
        
        # Create initial state
        initial_state = create_initial_state(
            task_id=task_id,
            task_description=task_description,
            max_iterations=max_iterations
        )
        
        try:
            # Execute the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            logger.info(f"Task execution complete: {task_id}")
            
            return {
                "task_id": task_id,
                "status": "completed" if final_state.get("verification_passed") else "failed",
                "final_result": final_state.get("final_result"),
                "iterations": final_state.get("iteration_count"),
                "plan": final_state.get("plan"),
                "execution_results": final_state.get("execution_results"),
                "verification": final_state.get("verification_status"),
                "error": final_state.get("error"),
            }
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e),
                "final_result": None
            }
    
    async def execute_task_stream(
        self,
        task_id: str,
        task_description: str,
        max_iterations: int = 5
    ):
        """
        Execute a task and stream intermediate results.
        
        Args:
            task_id: Unique task identifier
            task_description: Description of the task
            max_iterations: Maximum iterations
            
        Yields:
            State updates as the agent progresses
        """
        logger.info(f"Starting streaming task execution: {task_id}")
        
        initial_state = create_initial_state(
            task_id=task_id,
            task_description=task_description,
            max_iterations=max_iterations
        )
        
        try:
            # Stream execution
            async for state in self.graph.astream(initial_state):
                yield {
                    "task_id": task_id,
                    "state": state,
                    "timestamp": None  # Add timestamp if needed
                }
            
            logger.info(f"Streaming task execution complete: {task_id}")
            
        except Exception as e:
            logger.error(f"Error in streaming execution for task {task_id}: {e}")
            yield {
                "task_id": task_id,
                "error": str(e),
                "status": "error"
            }


# Global agent executor instance
agent_executor = AgentExecutor()

# Made with Bob
