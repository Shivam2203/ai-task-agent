"""
Health check endpoints for monitoring service status.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.redis import redis_client
from app.core.rag.vector_store import vector_store
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "AI Task Completion Agent",
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check including all dependencies.
    
    Returns:
        Detailed health status of all components
    """
    health_status = {
        "status": "healthy",
        "components": {}
    }
    
    # Check database
    try:
        await db.execute("SELECT 1")
        health_status["components"]["database"] = {
            "status": "healthy",
            "type": "PostgreSQL"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check Redis
    try:
        redis_healthy = await redis_client.ping()
        health_status["components"]["redis"] = {
            "status": "healthy" if redis_healthy else "unhealthy",
            "type": "Redis"
        }
        if not redis_healthy:
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check ChromaDB
    try:
        stats = await vector_store.get_collection_stats()
        health_status["components"]["vector_store"] = {
            "status": "healthy",
            "type": "ChromaDB",
            "documents": stats.get("document_count", 0)
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["vector_store"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    return health_status

# Made with Bob
