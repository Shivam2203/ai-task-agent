"""
Agent state model and schemas for tracking agent execution.

Stores the state of agent workflow execution for each task.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from pydantic import BaseModel, Field, ConfigDict

from app.db.session import Base


class AgentState(Base):
    """SQLAlchemy model for agent execution states."""
    
    __tablename__ = "agent_states"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(PGUUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    state_type = Column(String(50), nullable=False, index=True)  # planning, executing, verifying
    state_data = Column(JSON, nullable=False, default=dict)
    iteration = Column(String(50), default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AgentStep(Base):
    """SQLAlchemy model for individual agent steps."""
    
    __tablename__ = "agent_steps"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(PGUUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    step_type = Column(String(50), nullable=False)  # plan, execute, verify, tool_call
    step_number = Column(String(50), nullable=False)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, running, completed, failed
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


# Pydantic schemas
class AgentStateBase(BaseModel):
    """Base agent state schema."""
    
    task_id: UUID
    state_type: str = Field(..., pattern="^(planning|executing|verifying)$")
    state_data: Dict[str, Any] = Field(default_factory=dict)
    iteration: int = Field(default=0, ge=0)


class AgentStateCreate(AgentStateBase):
    """Schema for creating agent state."""
    pass


class AgentStateResponse(AgentStateBase):
    """Schema for agent state responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime


class AgentStepBase(BaseModel):
    """Base agent step schema."""
    
    task_id: UUID
    step_type: str
    step_number: int
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"
    error: Optional[str] = None


class AgentStepCreate(AgentStepBase):
    """Schema for creating agent step."""
    pass


class AgentStepResponse(AgentStepBase):
    """Schema for agent step responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None

# Made with Bob
