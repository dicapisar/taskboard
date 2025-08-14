import json
from typing import Protocol, List

from src.app.core.cache import Redis, get_redis
from src.app.core.config import settings
from fastapi import Depends


class CacheRepository(Protocol):
    async def set_user_session_data(self, session_id: str, user_data: dict) -> None: ...
    async def get_user_session_data(self, session_id: str) -> dict | None: ...
    async def set(self, key: str, value: dict, ttl_seconds: int = 60) -> None: ...
    async def get(self, key: str) -> dict | None: ...
    async def delete(self, key: str) -> None: ...
    pass

class CacheRepositoryImpl:
    def __init__(self, redis_client: Redis = Depends(get_redis)):
        self.redis_client = redis_client
        self.expiration_time = settings.CACHE_EXPIRATION_TIME


    async def set_user_session_data(self, session_id: str, user_data: dict ) -> None:
        """
        Store user data in Redis cache.
        """
        await self.redis_client.set(f"session:{session_id}", json.dumps(user_data), ex=self.expiration_time)

    async def get_user_session_data(self, session_id: str) -> dict | None:
        """
        Retrieve user data from Redis cache.
        """
        user_data = await self.redis_client.get(f"session:{session_id}")

        if user_data:
            user_data = json.loads(user_data)

        return user_data if user_data else None


    async def set(self, key: str, value: dict, ttl_seconds: int = 60) -> None:
        """
        Set a key-value pair in the cache with an optional TTL.
        """
        if not key or not value:
            raise ValueError("Key and value are required.")

        await self.redis_client.set(key, json.dumps(value), ex=ttl_seconds)

    async def get(self, key: str) -> dict | None:
        """
        Get a value from the cache by key.
        """
        if not key:
            raise ValueError("Key is required.")

        value = await self.redis_client.get(key)

        if value:
            return json.loads(value)

        return None

    async def delete(self, key: str) -> None:
        """
        Delete a key from the cache.
        """
        if not key:
            raise ValueError("Key is required.")

        await self.redis_client.delete(key)

def get_cache_repository(redis_client: Redis = Depends(get_redis)) -> CacheRepositoryImpl:
    """
    Dependency to get the cache repository instance.
    """
    return CacheRepositoryImpl(redis_client=redis_client)