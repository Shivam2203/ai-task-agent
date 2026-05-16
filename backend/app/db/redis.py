"""
Redis client configuration for caching and session management.

Provides async Redis client with connection pooling.
"""
from typing import Optional, Any
import json

from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Async Redis client wrapper with utility methods."""
    
    def __init__(self):
        """Initialize Redis client with connection pool."""
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[Redis] = None
    
    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            self._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,
                max_connections=10,
            )
            self._client = Redis(connection_pool=self._pool)
            await self._client.ping()
            logger.info("Redis connection established")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Redis connection closed")
    
    async def ping(self) -> bool:
        """
        Check if Redis is available.
        
        Returns:
            bool: True if Redis is available
        """
        try:
            if not self._client:
                await self.connect()
            return await self._client.ping()
        except RedisError:
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis.
        
        Args:
            key: Redis key
            
        Returns:
            Value or None if not found
        """
        try:
            if not self._client:
                await self.connect()
            return await self._client.get(key)
        except RedisError as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """
        Set value in Redis.
        
        Args:
            key: Redis key
            value: Value to store
            expire: Expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            if not self._client:
                await self.connect()
            await self._client.set(key, value, ex=expire)
            return True
        except RedisError as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from Redis.
        
        Args:
            key: Redis key
            
        Returns:
            bool: True if successful
        """
        try:
            if not self._client:
                await self.connect()
            await self._client.delete(key)
            return True
        except RedisError as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[Any]:
        """
        Get JSON value from Redis.
        
        Args:
            key: Redis key
            
        Returns:
            Parsed JSON value or None
        """
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON for key {key}: {e}")
        return None
    
    async def set_json(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        Set JSON value in Redis.
        
        Args:
            key: Redis key
            value: Value to store (will be JSON serialized)
            expire: Expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value, expire)
        except (TypeError, json.JSONEncodeError) as e:
            logger.error(f"Failed to serialize JSON for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.
        
        Args:
            key: Redis key
            
        Returns:
            bool: True if key exists
        """
        try:
            if not self._client:
                await self.connect()
            return await self._client.exists(key) > 0
        except RedisError as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time for a key.
        
        Args:
            key: Redis key
            seconds: Expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            if not self._client:
                await self.connect()
            return await self._client.expire(key, seconds)
        except RedisError as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()

# Made with Bob
