"""
Application configuration management using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://taskagent:taskagent_password@localhost:5432/taskagent_db",
        description="PostgreSQL database URL with asyncpg driver"
    )
    
    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    REDIS_PASSWORD: str = Field(default="", description="Redis password if required")
    
    # watsonx.ai Configuration
    WATSONX_API_KEY: str = Field(..., description="IBM watsonx.ai API key")
    WATSONX_PROJECT_ID: str = Field(..., description="IBM watsonx.ai project ID")
    WATSONX_URL: str = Field(
        default="https://us-south.ml.cloud.ibm.com",
        description="watsonx.ai API endpoint URL"
    )
    
    # Application Configuration
    SECRET_KEY: str = Field(
        default="change-this-to-a-secure-random-key-in-production",
        description="Secret key for JWT token generation"
    )
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIRECTORY: str = Field(
        default="./chroma_db",
        description="Directory for ChromaDB persistence"
    )
    CHROMA_HOST: str = Field(default="localhost", description="ChromaDB host")
    CHROMA_PORT: int = Field(default=8001, description="ChromaDB port")
    
    # Agent Configuration
    MAX_AGENT_ITERATIONS: int = Field(
        default=5,
        description="Maximum number of agent iterations before stopping"
    )
    AGENT_TIMEOUT_SECONDS: int = Field(
        default=300,
        description="Maximum time in seconds for agent execution"
    )
    DEFAULT_MODEL_ID: str = Field(
        default="ibm/granite-13b-chat-v2",
        description="Default Granite model ID"
    )
    EMBEDDING_MODEL_ID: str = Field(
        default="ibm/slate-125m-english-rtrvr",
        description="Model ID for generating embeddings"
    )
    
    # Vector Search Configuration
    VECTOR_DIMENSION: int = Field(
        default=1536,
        description="Dimension of vector embeddings"
    )
    SIMILARITY_THRESHOLD: float = Field(
        default=0.7,
        description="Minimum similarity score for vector search results"
    )
    MAX_SEARCH_RESULTS: int = Field(
        default=5,
        description="Maximum number of search results to return"
    )
    
    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1", description="API version 1 prefix")
    PROJECT_NAME: str = Field(
        default="AI Task Completion Agent",
        description="Project name for API documentation"
    )
    VERSION: str = Field(default="1.0.0", description="API version")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Maximum requests per minute per user"
    )
    RATE_LIMIT_PER_HOUR: int = Field(
        default=1000,
        description="Maximum requests per hour per user"
    )
    
    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def cors_origins(self) -> List[str]:
        """Get parsed CORS origins as a list."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic migrations."""
        return self.DATABASE_URL.replace("+asyncpg", "")


# Global settings instance
settings = Settings()

# Made with Bob
