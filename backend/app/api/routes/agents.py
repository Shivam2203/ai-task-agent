"""
Agent-specific API endpoints.

Provides endpoints for agent status and control.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.agent_state import AgentState, AgentStep
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/status/{task_id}")
async def get_agent_status(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get agent execution status for a task.
    
    Args:
        task_id: Task identifier
        db: Database session
        
    Returns:
        Agent status and execution history
    """
    try:
        # Get agent states
        states_result = await db.execute(
            select(AgentState)
            .where(AgentState.task_id == task_id)
            .order_by(AgentState.created_at.desc())
        )
        states = states_result.scalars().all()
        
        # Get agent steps
        steps_result = await db.execute(
            select(AgentStep)
            .where(AgentStep.task_id == task_id)
            .order_by(AgentStep.step_number)
        )
        steps = steps_result.scalars().all()
        
        return {
            "task_id": str(task_id),
            "states": [
                {
                    "id": str(state.id),
                    "state_type": state.state_type,
                    "iteration": state.iteration,
                    "created_at": state.created_at.isoformat(),
                    "state_data": state.state_data
                }
                for state in states
            ],
            "steps": [
                {
                    "id": str(step.id),
                    "step_type": step.step_type,
                    "step_number": step.step_number,
                    "status": step.status,
                    "started_at": step.started_at.isoformat(),
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "input_data": step.input_data,
                    "output_data": step.output_data,
                    "error": step.error
                }
                for step in steps
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting agent status for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/{task_id}")
async def execute_agent(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger agent execution for a task.
    
    Args:
        task_id: Task identifier
        db: Database session
        
    Returns:
        Execution status
    """
    try:
        from app.models.task import Task
        from app.core.agent.graph import agent_executor
        
        # Get task
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Execute agent
        execution_result = await agent_executor.execute_task(
            task_id=str(task_id),
            task_description=task.description
        )
        
        # Update task
        task.status = execution_result.get("status", "completed")
        task.result = execution_result.get("final_result")
        task.error = execution_result.get("error")
        await db.commit()
        
        return {
            "task_id": str(task_id),
            "status": execution_result.get("status"),
            "message": "Agent execution completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
