"""
Task model and schemas for task management.

Defines SQLAlchemy model for tasks and Pydantic schemas for API validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from pydantic import BaseModel, Field, ConfigDict

from app.db.session import Base


class Task(Base):
    """SQLAlchemy model for tasks."""
    
    __tablename__ = "tasks"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True
    )  # pending, planning, executing, verifying, completed, failed
    priority = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, default=dict)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)


# Pydantic schemas for API validation
class TaskBase(BaseModel):
    """Base task schema with common fields."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: str = Field(..., min_length=1, description="Detailed task description")
    priority: int = Field(default=0, ge=0, le=10, description="Task priority (0-10)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    
    model_config = ConfigDict(extra="forbid")
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(pending|planning|executing|verifying|completed|failed)$")
    priority: Optional[int] = Field(None, ge=0, le=10)
    metadata: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    error: Optional[str] = None


class TaskResponse(TaskBase):
    """Schema for task responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None


class TaskListResponse(BaseModel):
    """Schema for paginated task list responses."""
    
    tasks: list[TaskResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

# Made with Bob
