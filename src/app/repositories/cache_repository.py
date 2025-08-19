# Import required modules
import json
from typing import Protocol, List

# Import Redis client and related dependencies
from src.app.core.cache import Redis, get_redis
from src.app.core.config import settings
from fastapi import Depends

# ---------------------------- Cache Repository Interface ----------------------------

class CacheRepository(Protocol):
    """
    Interface (Protocol) that defines the required methods for a cache repository.
    Any implementation of this interface must define these methods.
    """

    async def set_user_session_data(self, session_id: str, user_data: dict) -> None: ...
    async def get_user_session_data(self, session_id: str) -> dict | None: ...
    async def set(self, key: str, value: dict, ttl_seconds: int = 60) -> None: ...
    async def get(self, key: str) -> dict | None: ...
    async def delete(self, key: str) -> None: ...
    pass

# ---------------------------- Cache Repository Implementation ----------------------------

class CacheRepositoryImpl:
    """
    Concrete implementation of the CacheRepository interface using Redis.
    """

    def __init__(self, redis_client: Redis = Depends(get_redis)):
        # Assign the Redis client
        self.redis_client = redis_client
        # Set the default expiration time from configuration
        self.expiration_time = settings.CACHE_EXPIRATION_TIME

    # ---------------------------- Session Methods ----------------------------

    async def set_user_session_data(self, session_id: str, user_data: dict) -> None:
        """
        Store user session data in Redis using a unique session ID.
        """
        await self.redis_client.set(
            f"session:{session_id}",
            json.dumps(user_data),
            ex=self.expiration_time
        )

    async def get_user_session_data(self, session_id: str) -> dict | None:
        """
        Retrieve user session data from Redis by session ID.
        """
        user_data = await self.redis_client.get(f"session:{session_id}")

        if user_data:
            user_data = json.loads(user_data)

        return user_data if user_data else None

    # ---------------------------- Generic Cache Methods ----------------------------

    async def set(self, key: str, value: dict, ttl_seconds: int = 60) -> None:
        """
        Set a generic key-value pair in Redis with a time-to-live (TTL).
        """
        if not key or not value:
            raise ValueError("Key and value are required.")

        await self.redis_client.set(key, json.dumps(value), ex=ttl_seconds)

    async def get(self, key: str) -> dict | None:
        """
        Retrieve a value from Redis using the given key.
        """
        if not key:
            raise ValueError("Key is required.")

        value = await self.redis_client.get(key)

        if value:
            return json.loads(value)

        return None

    async def delete(self, key: str) -> None:
        """
        Delete a key and its value from Redis.
        """
        if not key:
            raise ValueError("Key is required.")

        await self.redis_client.delete(key)

# ---------------------------- Dependency Injection ----------------------------

def get_cache_repository(redis_client: Redis = Depends(get_redis)) -> CacheRepositoryImpl:
    """
    Dependency to get a CacheRepositoryImpl instance.
    This allows it to be injected automatically in route handlers or services.
    """
    return CacheRepositoryImpl(redis_client=redis_client)