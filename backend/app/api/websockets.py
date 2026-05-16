"""
WebSocket endpoints for real-time agent streaming.

Provides real-time updates during agent execution.
"""
import json
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from uuid import UUID

from app.core.agent.graph import agent_executor
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, task_id: str, websocket: WebSocket):
        """
        Accept and store a WebSocket connection.
        
        Args:
            task_id: Task identifier
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections[task_id] = websocket
        logger.info(f"WebSocket connected for task: {task_id}")
    
    def disconnect(self, task_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            task_id: Task identifier
        """
        if task_id in self.active_connections:
            del self.active_connections[task_id]
            logger.info(f"WebSocket disconnected for task: {task_id}")
    
    async def send_message(self, task_id: str, message: dict):
        """
        Send a message to a specific connection.
        
        Args:
            task_id: Task identifier
            message: Message to send
        """
        if task_id in self.active_connections:
            try:
                await self.active_connections[task_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {task_id}: {e}")
                self.disconnect(task_id)
    
    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connections.
        
        Args:
            message: Message to broadcast
        """
        for task_id, connection in list(self.active_connections.items()):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {task_id}: {e}")
                self.disconnect(task_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/agent-stream/{task_id}")
async def agent_stream(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for streaming agent execution.
    
    Args:
        websocket: WebSocket connection
        task_id: Task identifier
    """
    await manager.connect(task_id, websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "task_id": task_id,
            "message": "Connected to agent stream"
        })
        
        # Wait for start command
        data = await websocket.receive_text()
        command = json.loads(data)
        
        if command.get("action") == "start":
            task_description = command.get("task_description", "")
            
            # Send starting message
            await websocket.send_json({
                "type": "status",
                "task_id": task_id,
                "status": "starting",
                "message": "Agent execution starting..."
            })
            
            # Stream agent execution
            async for update in agent_executor.execute_task_stream(
                task_id=task_id,
                task_description=task_description
            ):
                await websocket.send_json({
                    "type": "update",
                    "task_id": task_id,
                    "data": update
                })
            
            # Send completion message
            await websocket.send_json({
                "type": "complete",
                "task_id": task_id,
                "message": "Agent execution complete"
            })
        
        # Keep connection alive for additional messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "task_id": task_id
                })
            elif message.get("action") == "close":
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "task_id": task_id,
                "error": str(e)
            })
        except:
            pass
    finally:
        manager.disconnect(task_id)


@router.websocket("/tasks/{task_id}")
async def task_updates(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for task status updates.
    
    Args:
        websocket: WebSocket connection
        task_id: Task identifier
    """
    await manager.connect(task_id, websocket)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "task_id": task_id
        })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Echo back for now (can be extended for bidirectional communication)
            await websocket.send_json({
                "type": "echo",
                "task_id": task_id,
                "data": message
            })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(task_id)

# Made with Bob
