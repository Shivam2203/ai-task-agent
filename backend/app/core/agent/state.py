"""
Agent state definition for LangGraph workflow.

Defines the state structure that flows through the agent graph.
"""
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from operator import add


class AgentState(TypedDict):
    """
    State structure for the agent workflow.
    
    This state is passed between nodes in the LangGraph workflow
    and accumulates information as the agent progresses.
    """
    
    # Task information
    task_id: str
    task_description: str
    
    # Messages history (accumulated)
    messages: Annotated[List[Dict[str, str]], add]
    
    # Planning phase
    plan: Optional[Dict[str, Any]]
    plan_steps: List[Dict[str, Any]]
    
    # Execution phase
    execution_results: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    
    # Verification phase
    verification_status: Optional[Dict[str, Any]]
    verification_passed: bool
    
    # Control flow
    iteration_count: int
    max_iterations: int
    should_continue: bool
    
    # Final output
    final_result: Optional[str]
    error: Optional[str]


def create_initial_state(
    task_id: str,
    task_description: str,
    max_iterations: int = 5
) -> AgentState:
    """
    Create initial agent state for a new task.
    
    Args:
        task_id: Unique task identifier
        task_description: Description of the task to complete
        max_iterations: Maximum number of iterations allowed
        
    Returns:
        Initial agent state
    """
    return AgentState(
        task_id=task_id,
        task_description=task_description,
        messages=[],
        plan=None,
        plan_steps=[],
        execution_results=[],
        tool_calls=[],
        verification_status=None,
        verification_passed=False,
        iteration_count=0,
        max_iterations=max_iterations,
        should_continue=True,
        final_result=None,
        error=None,
    )

# Made with Bob
