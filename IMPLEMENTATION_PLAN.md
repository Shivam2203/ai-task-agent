# AI Task Completion Agent - Implementation Plan

## Project Overview

A full-stack AI Task Completion Agent that can plan, execute, and verify tasks autonomously using:
- **Backend**: FastAPI (Python)
- **Frontend**: React (TypeScript)
- **Database**: PostgreSQL with pgvector extension
- **Vector Store**: ChromaDB
- **LLM**: IBM watsonx.ai Granite models
- **Agent Framework**: LangGraph
- **Deployment**: Local development environment

## System Architecture

```mermaid
graph TB
    subgraph Frontend
        A[React UI] --> B[Task Input]
        A --> C[Task Monitor]
        A --> D[Results Display]
    end
    
    subgraph Backend
        E[FastAPI Server] --> F[WebSocket Handler]
        E --> G[REST API Endpoints]
        G --> H[Task Manager]
        H --> I[LangGraph Agent]
    end
    
    subgraph Agent Workflow
        I --> J[Planning Node]
        J --> K[Execution Node]
        K --> L[Verification Node]
        L --> M{Task Complete?}
        M -->|No| J
        M -->|Yes| N[Return Results]
    end
    
    subgraph Data Layer
        O[PostgreSQL + pgvector] --> P[Task History]
        O --> Q[Vector Embeddings]
        R[ChromaDB] --> S[Document Store]
        R --> T[Semantic Search]
    end
    
    subgraph AI Services
        U[watsonx.ai] --> V[Granite LLM]
        V --> W[Text Generation]
        V --> X[Embeddings]
    end
    
    A --> E
    F --> A
    I --> U
    I --> O
    I --> R
```

## Detailed Implementation Steps

### Phase 1: Project Foundation

#### 1.1 Project Structure Setup
```
ai-task-agent/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── tasks.py
│   │   │   │   ├── agents.py
│   │   │   │   └── health.py
│   │   │   └── websockets.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── agent/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── graph.py
│   │   │   │   ├── nodes.py
│   │   │   │   └── state.py
│   │   │   ├── llm/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── watsonx_client.py
│   │   │   │   └── embeddings.py
│   │   │   └── rag/
│   │   │       ├── __init__.py
│   │   │       ├── retriever.py
│   │   │       └── vector_store.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── task.py
│   │   │   └── agent_state.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── session.py
│   │   │   └── migrations/
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       └── validators.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_agent.py
│   │   └── test_rag.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TaskInput.tsx
│   │   │   ├── TaskMonitor.tsx
│   │   │   ├── ResultsDisplay.tsx
│   │   │   └── AgentStatus.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   └── useTaskManager.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   ├── types/
│   │   │   └── task.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── SETUP.md
└── README.md
```

#### 1.2 Technology Stack Details

**Backend Dependencies:**
- `fastapi>=0.104.0` - Web framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `sqlalchemy>=2.0.0` - ORM
- `psycopg2-binary>=2.9.9` - PostgreSQL adapter
- `pgvector>=0.2.3` - Vector similarity search
- `chromadb>=0.4.18` - Vector database
- `langgraph>=0.0.20` - Agent workflow framework
- `langchain>=0.1.0` - LLM framework
- `ibm-watsonx-ai>=0.2.0` - watsonx.ai SDK
- `pydantic>=2.5.0` - Data validation
- `python-dotenv>=1.0.0` - Environment management
- `websockets>=12.0` - WebSocket support
- `redis>=5.0.0` - Caching and session management
- `alembic>=1.13.0` - Database migrations

**Frontend Dependencies:**
- `react>=18.2.0`
- `typescript>=5.0.0`
- `vite>=5.0.0`
- `@tanstack/react-query>=5.0.0` - Data fetching
- `axios>=1.6.0` - HTTP client
- `socket.io-client>=4.6.0` - WebSocket client
- `tailwindcss>=3.4.0` - Styling
- `zustand>=4.4.0` - State management
- `react-markdown>=9.0.0` - Markdown rendering

### Phase 2: Database Setup

#### 2.1 PostgreSQL with pgvector

**Database Schema:**

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB
);

-- Agent states table
CREATE TABLE agent_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    state_type VARCHAR(50) NOT NULL,
    state_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vector embeddings table
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_agent_states_task_id ON agent_states(task_id);
CREATE INDEX idx_embeddings_task_id ON embeddings(task_id);

-- Vector similarity search index
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

#### 2.2 ChromaDB Configuration

ChromaDB will be used for:
- Document storage and retrieval
- Semantic search across task history
- Context retrieval for RAG

### Phase 3: Backend Implementation

#### 3.1 FastAPI Core Structure

**[`backend/app/main.py`](backend/app/main.py)**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import tasks, agents, health
from app.api.websockets import router as ws_router
from app.config import settings
from app.db.session import init_db

app = FastAPI(
    title="AI Task Completion Agent",
    version="1.0.0",
    description="Autonomous task planning, execution, and verification"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(ws_router, prefix="/ws", tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup resources
    pass
```

#### 3.2 watsonx.ai Integration

**[`backend/app/core/llm/watsonx_client.py`](backend/app/core/llm/watsonx_client.py)**
```python
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from app.config import settings

class WatsonxClient:
    def __init__(self):
        self.credentials = Credentials(
            url=settings.WATSONX_URL,
            api_key=settings.WATSONX_API_KEY,
        )
        self.project_id = settings.WATSONX_PROJECT_ID
        
    def get_model(self, model_id: str = "ibm/granite-13b-chat-v2"):
        return ModelInference(
            model_id=model_id,
            credentials=self.credentials,
            project_id=self.project_id,
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9,
            }
        )
    
    async def generate(self, prompt: str, model_id: str = None) -> str:
        model = self.get_model(model_id)
        response = model.generate_text(prompt=prompt)
        return response
    
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        # Use watsonx.ai embedding model
        model = self.get_model("ibm/slate-125m-english-rtrvr")
        embeddings = []
        for text in texts:
            embedding = model.generate_text_embedding(text)
            embeddings.append(embedding)
        return embeddings
```

#### 3.3 LangGraph Agent Workflow

**[`backend/app/core/agent/state.py`](backend/app/core/agent/state.py)**
```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task_description: str
    plan: dict
    execution_results: list[dict]
    verification_status: dict
    iteration_count: int
    max_iterations: int
    final_result: str
```

**[`backend/app/core/agent/graph.py`](backend/app/core/agent/graph.py)**
```python
from langgraph.graph import StateGraph, END
from app.core.agent.state import AgentState
from app.core.agent.nodes import (
    planning_node,
    execution_node,
    verification_node,
    should_continue
)

def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("plan", planning_node)
    workflow.add_node("execute", execution_node)
    workflow.add_node("verify", verification_node)
    
    # Add edges
    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "execute")
    workflow.add_edge("execute", "verify")
    
    # Conditional edge based on verification
    workflow.add_conditional_edges(
        "verify",
        should_continue,
        {
            "continue": "plan",
            "end": END
        }
    )
    
    return workflow.compile()
```

**[`backend/app/core/agent/nodes.py`](backend/app/core/agent/nodes.py)**
```python
from app.core.llm.watsonx_client import WatsonxClient
from app.core.rag.retriever import RAGRetriever
from langchain_core.messages import HumanMessage, AIMessage

watsonx_client = WatsonxClient()
rag_retriever = RAGRetriever()

async def planning_node(state: AgentState) -> AgentState:
    """Generate a plan for task completion"""
    task = state["task_description"]
    
    # Retrieve relevant context
    context = await rag_retriever.retrieve(task)
    
    # Generate plan using Granite LLM
    prompt = f"""
    Task: {task}
    
    Relevant Context:
    {context}
    
    Create a detailed step-by-step plan to complete this task.
    Format as JSON with steps, dependencies, and expected outcomes.
    """
    
    plan_response = await watsonx_client.generate(prompt)
    
    state["plan"] = parse_plan(plan_response)
    state["messages"].append(AIMessage(content=f"Plan created: {plan_response}"))
    
    return state

async def execution_node(state: AgentState) -> AgentState:
    """Execute the planned steps"""
    plan = state["plan"]
    results = []
    
    for step in plan["steps"]:
        # Execute each step
        prompt = f"""
        Execute this step: {step['description']}
        
        Context: {step.get('context', '')}
        Expected outcome: {step['expected_outcome']}
        
        Provide the execution result.
        """
        
        result = await watsonx_client.generate(prompt)
        results.append({
            "step": step["id"],
            "result": result,
            "status": "completed"
        })
    
    state["execution_results"] = results
    state["messages"].append(AIMessage(content=f"Executed {len(results)} steps"))
    
    return state

async def verification_node(state: AgentState) -> AgentState:
    """Verify task completion"""
    task = state["task_description"]
    results = state["execution_results"]
    
    prompt = f"""
    Task: {task}
    
    Execution Results:
    {results}
    
    Verify if the task has been completed successfully.
    Provide:
    1. Verification status (complete/incomplete)
    2. Quality assessment
    3. Any issues or improvements needed
    
    Format as JSON.
    """
    
    verification = await watsonx_client.generate(prompt)
    state["verification_status"] = parse_verification(verification)
    state["iteration_count"] += 1
    
    return state

def should_continue(state: AgentState) -> str:
    """Determine if agent should continue or end"""
    if state["verification_status"]["status"] == "complete":
        return "end"
    
    if state["iteration_count"] >= state["max_iterations"]:
        return "end"
    
    return "continue"

def parse_plan(plan_text: str) -> dict:
    # Parse LLM response into structured plan
    # Implementation depends on response format
    pass

def parse_verification(verification_text: str) -> dict:
    # Parse verification response
    pass
```

#### 3.4 RAG Implementation

**[`backend/app/core/rag/retriever.py`](backend/app/core/rag/retriever.py)**
```python
from app.core.rag.vector_store import VectorStore
from app.core.llm.watsonx_client import WatsonxClient

class RAGRetriever:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_client = WatsonxClient()
    
    async def retrieve(self, query: str, top_k: int = 5) -> str:
        # Generate query embedding
        query_embedding = await self.llm_client.generate_embeddings([query])
        
        # Search in both PostgreSQL and ChromaDB
        pg_results = await self.vector_store.search_pgvector(
            query_embedding[0], 
            top_k
        )
        chroma_results = await self.vector_store.search_chromadb(
            query, 
            top_k
        )
        
        # Combine and rank results
        combined_results = self._combine_results(pg_results, chroma_results)
        
        # Format context
        context = self._format_context(combined_results)
        
        return context
    
    def _combine_results(self, pg_results, chroma_results):
        # Merge and deduplicate results
        pass
    
    def _format_context(self, results):
        # Format retrieved documents into context string
        pass
```

**[`backend/app/core/rag/vector_store.py`](backend/app/core/rag/vector_store.py)**
```python
import chromadb
from sqlalchemy import select
from app.db.session import get_db
from app.models.task import Embedding

class VectorStore:
    def __init__(self):
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection(
            name="task_documents"
        )
    
    async def search_pgvector(self, embedding: list[float], top_k: int):
        async with get_db() as db:
            # Vector similarity search using pgvector
            query = select(Embedding).order_by(
                Embedding.embedding.cosine_distance(embedding)
            ).limit(top_k)
            
            results = await db.execute(query)
            return results.scalars().all()
    
    async def search_chromadb(self, query: str, top_k: int):
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        return results
    
    async def add_document(self, content: str, metadata: dict):
        # Add to ChromaDB
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[metadata["id"]]
        )
```

#### 3.5 Task Management API

**[`backend/app/api/routes/tasks.py`](backend/app/api/routes/tasks.py)**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.task import Task, TaskCreate, TaskResponse
from app.core.agent.graph import create_agent_graph

router = APIRouter()

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    # Create task in database
    db_task = Task(**task.dict())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    
    # Start agent workflow asynchronously
    agent_graph = create_agent_graph()
    # Trigger agent execution in background
    
    return db_task

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(Task).offset(skip).limit(limit)
    results = await db.execute(query)
    return results.scalars().all()
```

#### 3.6 WebSocket for Real-time Updates

**[`backend/app/api/websockets.py`](backend/app/api/websockets.py)**
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[task_id] = websocket
    
    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]
    
    async def send_update(self, task_id: str, message: dict):
        if task_id in self.active_connections:
            await self.active_connections[task_id].send_json(message)

manager = ConnectionManager()

@router.websocket("/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await manager.connect(task_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        manager.disconnect(task_id)
```

### Phase 4: Frontend Implementation

#### 4.1 React Application Structure

**[`frontend/src/App.tsx`](frontend/src/App.tsx)**
```typescript
import React from 'react';
import TaskInput from './components/TaskInput';
import TaskMonitor from './components/TaskMonitor';
import ResultsDisplay from './components/ResultsDisplay';
import { useTaskManager } from './hooks/useTaskManager';

function App() {
  const { currentTask, submitTask, taskStatus } = useTaskManager();

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 text-white p-6">
        <h1 className="text-3xl font-bold">AI Task Completion Agent</h1>
        <p className="text-blue-100">Autonomous Planning, Execution & Verification</p>
      </header>
      
      <main className="container mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <TaskInput onSubmit={submitTask} />
            {currentTask && <TaskMonitor taskId={currentTask.id} />}
          </div>
          
          <div>
            {currentTask && (
              <ResultsDisplay 
                taskId={currentTask.id} 
                status={taskStatus} 
              />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
```

#### 4.2 WebSocket Hook

**[`frontend/src/hooks/useWebSocket.ts`](frontend/src/hooks/useWebSocket.ts)**
```typescript
import { useEffect, useState, useCallback } from 'react';

interface WebSocketMessage {
  type: string;
  data: any;
}

export const useWebSocket = (taskId: string | null) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!taskId) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/tasks/${taskId}`);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages((prev) => [...prev, message]);
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [taskId]);

  const sendMessage = useCallback((message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  }, [socket, isConnected]);

  return { messages, isConnected, sendMessage };
};
```

#### 4.3 Task Input Component

**[`frontend/src/components/TaskInput.tsx`](frontend/src/components/TaskInput.tsx)**
```typescript
import React, { useState } from 'react';

interface TaskInputProps {
  onSubmit: (task: { title: string; description: string }) => void;
}

const TaskInput: React.FC<TaskInputProps> = ({ onSubmit }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ title, description });
    setTitle('');
    setDescription('');
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-semibold mb-4">Create New Task</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Task Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter task title"
            required
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Task Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={6}
            placeholder="Describe the task in detail..."
            required
          />
        </div>
        
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Start Task
        </button>
      </form>
    </div>
  );
};

export default TaskInput;
```

#### 4.4 Task Monitor Component

**[`frontend/src/components/TaskMonitor.tsx`](frontend/src/components/TaskMonitor.tsx)**
```typescript
import React from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface TaskMonitorProps {
  taskId: string;
}

const TaskMonitor: React.FC<TaskMonitorProps> = ({ taskId }) => {
  const { messages, isConnected } = useWebSocket(taskId);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">Task Progress</h2>
        <div className={`px-3 py-1 rounded-full text-sm ${
          isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </div>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {messages.map((msg, idx) => (
          <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
            <div className="text-sm text-gray-500">{msg.type}</div>
            <div className="text-gray-800">{JSON.stringify(msg.data, null, 2)}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TaskMonitor;
```

### Phase 5: Deployment Configuration

#### 5.1 Docker Compose

**[`docker/docker-compose.yml`](docker/docker-compose.yml)**
```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: taskagent
      POSTGRES_PASSWORD: taskagent_password
      POSTGRES_DB: taskagent_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://taskagent:taskagent_password@postgres:5432/taskagent_db
      REDIS_URL: redis://redis:6379
      WATSONX_API_KEY: ${WATSONX_API_KEY}
      WATSONX_PROJECT_ID: ${WATSONX_PROJECT_ID}
      WATSONX_URL: ${WATSONX_URL}
    depends_on:
      - postgres
      - redis
    volumes:
      - ../backend:/app

  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ../frontend:/app

volumes:
  postgres_data:
  redis_data:
```

#### 5.2 Backend Dockerfile

**[`docker/Dockerfile.backend`](docker/Dockerfile.backend)**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
```

#### 5.3 Frontend Dockerfile

**[`docker/Dockerfile.frontend`](docker/Dockerfile.frontend)**
```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### Phase 6: Configuration and Environment

#### 6.1 Backend Configuration

**[`backend/.env.example`](backend/.env.example)**
```env
# Database
DATABASE_URL=postgresql+asyncpg://taskagent:taskagent_password@localhost:5432/taskagent_db

# Redis
REDIS_URL=redis://localhost:6379

# watsonx.ai
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Application
SECRET_KEY=your_secret_key_here
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Agent Configuration
MAX_AGENT_ITERATIONS=5
AGENT_TIMEOUT_SECONDS=300
```

**[`backend/app/config.py`](backend/app/config.py)**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # watsonx.ai
    WATSONX_API_KEY: str
    WATSONX_PROJECT_ID: str
    WATSONX_URL: str
    
    # Application
    SECRET_KEY: str
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # Agent
    MAX_AGENT_ITERATIONS: int = 5
    AGENT_TIMEOUT_SECONDS: int = 300
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Phase 7: Testing Strategy

#### 7.1 Backend Tests

**[`backend/tests/test_agent.py`](backend/tests/test_agent.py)**
```python
import pytest
from app.core.agent.graph import create_agent_graph
from app.core.agent.state import AgentState

@pytest.mark.asyncio
async def test_agent_planning():
    graph = create_agent_graph()
    
    initial_state = AgentState(
        messages=[],
        task_description="Create a simple Python function to calculate factorial",
        plan={},
        execution_results=[],
        verification_status={},
        iteration_count=0,
        max_iterations=3,
        final_result=""
    )
    
    result = await graph.ainvoke(initial_state)
    
    assert result["plan"] is not None
    assert len(result["execution_results"]) > 0
    assert result["verification_status"]["status"] in ["complete", "incomplete"]

@pytest.mark.asyncio
async def test_rag_retrieval():
    from app.core.rag.retriever import RAGRetriever
    
    retriever = RAGRetriever()
    context = await retriever.retrieve("How to implement a REST API?")
    
    assert context is not None
    assert len(context) > 0
```

#### 7.2 Integration Tests

**[`backend/tests/test_api.py`](backend/tests/test_api.py)**
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/tasks/",
            json={
                "title": "Test Task",
                "description": "This is a test task"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"
        assert "id" in data

@pytest.mark.asyncio
async def test_get_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create task first
        create_response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Test", "description": "Test"}
        )
        task_id = create_response.json()["id"]
        
        # Get task
        response = await client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["id"] == task_id
```

### Phase 8: Documentation

#### 8.1 API Documentation

FastAPI automatically generates OpenAPI documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### 8.2 Setup Guide

**[`docs/SETUP.md`](docs/SETUP.md)**
```markdown
# Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+ with pgvector
- Docker and Docker Compose (optional)
- IBM watsonx.ai account with API credentials

## Local Development Setup

### 1. Clone Repository

git clone <repository-url>
cd ai-task-agent

### 2. Backend Setup

cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

### 3. Frontend Setup

cd frontend
npm install
npm run dev

### 4. Database Setup

# Install PostgreSQL with pgvector
# Create database
createdb taskagent_db

# Enable pgvector extension
psql taskagent_db -c "CREATE EXTENSION vector;"

## Docker Setup

docker-compose -f docker/docker-compose.yml up -d

## Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
```

## Implementation Timeline

### Week 1: Foundation
- Set up project structure
- Configure development environment
- Set up databases (PostgreSQL + pgvector, ChromaDB)
- Implement basic FastAPI structure

### Week 2: Core Backend
- Integrate watsonx.ai Granite LLM
- Implement RAG system
- Build LangGraph agent workflow
- Create planning, execution, and verification nodes

### Week 3: API and Data Layer
- Implement task management API
- Add WebSocket support
- Create database models and migrations
- Implement vector storage operations

### Week 4: Frontend Development
- Build React application structure
- Create UI components
- Implement WebSocket integration
- Add state management

### Week 5: Integration and Testing
- Integration testing
- End-to-end testing
- Performance optimization
- Bug fixes

### Week 6: Documentation and Deployment
- Write comprehensive documentation
- Create Docker configuration
- Set up local deployment
- Final testing and refinement

## Key Features Summary

1. **Autonomous Task Planning**: Agent analyzes tasks and creates detailed execution plans
2. **Intelligent Execution**: Step-by-step task execution with context awareness
3. **Self-Verification**: Automatic verification and quality assessment
4. **RAG-Enhanced Context**: Retrieval-augmented generation for better decision-making
5. **Real-time Monitoring**: WebSocket-based live updates
6. **Vector Search**: Semantic search across task history using pgvector and ChromaDB
7. **Persistent State**: Task history and agent states stored in PostgreSQL
8. **Iterative Refinement**: Agent can re-plan and re-execute based on verification results

## Architecture Highlights

- **Modular Design**: Clear separation of concerns
- **Async/Await**: Full async support for better performance
- **Type Safety**: Pydantic models and TypeScript for type safety
- **Scalable**: Ready for horizontal scaling with Redis and async processing
- **Observable**: Comprehensive logging and monitoring
- **Testable**: Unit and integration tests for all components

## Next Steps

After reviewing this plan, we can proceed with implementation by switching to Code mode to start building the components step by step.