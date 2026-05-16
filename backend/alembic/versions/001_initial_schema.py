"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-05-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
    )
    
    # Create indexes for tasks
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_created_at', 'tasks', ['created_at'])
    
    # Create agent_states table
    op.create_table(
        'agent_states',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('state_type', sa.String(50), nullable=False),
        sa.Column('state_data', postgresql.JSON(), nullable=False),
        sa.Column('iteration', sa.String(50), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for agent_states
    op.create_index('ix_agent_states_task_id', 'agent_states', ['task_id'])
    op.create_index('ix_agent_states_state_type', 'agent_states', ['state_type'])
    
    # Create agent_steps table
    op.create_table(
        'agent_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('step_type', sa.String(50), nullable=False),
        sa.Column('step_number', sa.String(50), nullable=False),
        sa.Column('input_data', postgresql.JSON(), nullable=True),
        sa.Column('output_data', postgresql.JSON(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for agent_steps
    op.create_index('ix_agent_steps_task_id', 'agent_steps', ['task_id'])
    op.create_index('ix_agent_steps_status', 'agent_steps', ['status'])
    
    # Create embeddings table for pgvector
    op.create_table(
        'embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', sa.String(), nullable=True),  # Will be vector type
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for embeddings
    op.create_index('ix_embeddings_task_id', 'embeddings', ['task_id'])
    
    # Add vector column and index (requires pgvector extension)
    op.execute('ALTER TABLE embeddings ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)')
    op.execute('CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')


def downgrade() -> None:
    op.drop_table('embeddings')
    op.drop_table('agent_steps')
    op.drop_table('agent_states')
    op.drop_table('tasks')
    op.execute('DROP EXTENSION IF EXISTS vector')

# Made with Bob
