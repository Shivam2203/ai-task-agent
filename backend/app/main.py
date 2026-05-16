"""
FastAPI application entry point.

This module initializes the FastAPI application with all routes, middleware,
and event handlers for the AI Task Completion Agent.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.logger import setup_logging, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting AI Task Completion Agent...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Initialize database connection
    try:
        from app.db.session import init_db
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Initialize ChromaDB
    try:
        from app.core.rag.vector_store import vector_store
        await vector_store.initialize()
        logger.info("ChromaDB initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")
        raise
    
    # Initialize Redis connection
    try:
        from app.db.redis import redis_client
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Task Completion Agent...")
    
    # Close database connections
    try:
        from app.db.session import close_db
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
    
    # Close Redis connection
    try:
        from app.db.redis import redis_client
        await redis_client.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis: {e}")
    
    logger.info("Application shutdown complete")


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous AI agent for task planning, execution, and verification",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Setup logging
setup_logging(settings.LOG_LEVEL)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify service status.
    
    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        dict: API information
    """
    return {
        "message": "AI Task Completion Agent API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


# Import and include routers
# Note: These will be implemented in subsequent steps
try:
    from app.api.routes import health, tasks, agents
    from app.api.websockets import router as ws_router
    
    app.include_router(
        health.router,
        prefix=settings.API_V1_PREFIX,
        tags=["health"]
    )
    app.include_router(
        tasks.router,
        prefix=f"{settings.API_V1_PREFIX}/tasks",
        tags=["tasks"]
    )
    app.include_router(
        agents.router,
        prefix=f"{settings.API_V1_PREFIX}/agents",
        tags=["agents"]
    )
    app.include_router(
        ws_router,
        prefix="/ws",
        tags=["websocket"]
    )
    logger.info("All API routes registered successfully")
except ImportError as e:
    logger.warning(f"Some routes not yet implemented: {e}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

# Made with Bob
