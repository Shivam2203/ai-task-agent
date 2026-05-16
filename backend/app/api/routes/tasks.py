"""
Task management API endpoints.

Provides CRUD operations for tasks and agent execution.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.task import Task, TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.core.agent.graph import agent_executor
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


async def execute_task_background(task_id: str, task_description: str, db: AsyncSession):
    """
    Background task to execute agent workflow.
    
    Args:
        task_id: Task identifier
        task_description: Task description
        db: Database session
    """
    try:
        logger.info(f"Starting background execution for task: {task_id}")
        
        # Update task status to planning
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if task:
            task.status = "planning"
            await db.commit()
        
        # Execute agent workflow
        result = await agent_executor.execute_task(
            task_id=str(task_id),
            task_description=task_description
        )
        
        # Update task with results
        if task:
            task.status = result.get("status", "completed")
            task.result = result.get("final_result")
            task.error = result.get("error")
            task.metadata = {
                "iterations": result.get("iterations"),
                "plan": result.get("plan"),
                "verification": result.get("verification")
            }
            await db.commit()
            
        logger.info(f"Background execution complete for task: {task_id}")
        
    except Exception as e:
        logger.error(f"Error in background task execution: {e}")
        # Update task with error
        if task:
            task.status = "failed"
            task.error = str(e)
            await db.commit()


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task and start agent execution.
    
    Args:
        task: Task creation data
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Created task
    """
    try:
        # Create task in database
        db_task = Task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            status="pending",
            metadata=task.metadata
        )
        
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        
        logger.info(f"Task created: {db_task.id}")
        
        # Start agent execution in background
        background_tasks.add_task(
            execute_task_background,
            str(db_task.id),
            task.description,
            db
        )
        
        return db_task
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a task by ID.
    
    Args:
        task_id: Task identifier
        db: Database session
        
    Returns:
        Task details
    """
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List tasks with pagination and filtering.
    
    Args:
        skip: Number of tasks to skip
        limit: Maximum number of tasks to return
        status: Filter by status
        db: Database session
        
    Returns:
        Paginated list of tasks
    """
    try:
        # Build query
        query = select(Task)
        
        if status:
            query = query.where(Task.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(Task)
        if status:
            count_query = count_query.where(Task.status == status)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get tasks
        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        return TaskListResponse(
            tasks=tasks,
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            has_more=(skip + limit) < total
        )
        
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a task.
    
    Args:
        task_id: Task identifier
        task_update: Task update data
        db: Database session
        
    Returns:
        Updated task
    """
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update fields
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        await db.commit()
        await db.refresh(task)
        
        logger.info(f"Task updated: {task_id}")
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a task.
    
    Args:
        task_id: Task identifier
        db: Database session
    """
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        await db.delete(task)
        await db.commit()
        
        logger.info(f"Task deleted: {task_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
