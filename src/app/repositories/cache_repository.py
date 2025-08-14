import json
from typing import Protocol, List

from src.app.core.cache import Redis, get_redis
from src.app.core.config import settings
from fastapi import Depends


class CacheRepository(Protocol):
    async def set_user_session_data(self, session_id: str, user_data: dict) -> None: ...
    async def get_user_session_data(self, session_id: str) -> dict | None: ...
    pass

class CacheRepositoryImpl:
    def __init__(self, redis_client: Redis = Depends(get_redis)):
        self.redis_client = redis_client
        self.expiration_time = settings.CACHE_EXPIRATION_TIME


    async def set_user_session_data(self, session_id: str, user_data: dict ) -> None:
        """
        Store user data in Redis cache.
        """
        await self.redis_client.set(f"user:{session_id}", json.dumps(user_data), ex=self.expiration_time)

    async def get_user_session_data(self, session_id: str) -> dict | None:
        """
        Retrieve user data from Redis cache.
        """
        user_data = await self.redis_client.get(f"user:{session_id}")

        if user_data:
            user_data = json.loads(user_data)

        return user_data if user_data else None

def get_cache_repository(redis_client: Redis = Depends(get_redis)) -> CacheRepositoryImpl:
    """
    Dependency to get the cache repository instance.
    """
    return CacheRepositoryImpl(redis_client=redis_client)