from src.app.dtos.user_detail import UserDetail
from src.app.repositories.cache_repository import CacheRepository, get_cache_repository

from fastapi import Depends


class CacheService:
    def __init__(self, cache_repository: CacheRepository):
        self.cache_repository = cache_repository


    async def set_user_session_data(self, session_id: str, user_data: UserDetail) -> None:
        """
        Store user data in Redis cache.
        """
        if not session_id or not user_data:
            raise ValueError("Session ID and user data are required.")

        await self.cache_repository.set_user_session_data(session_id, user_data.__dict__)

    async def get_user_session_data(self, session_id: str) -> UserDetail | None:
        """
        Retrieve user data from Redis cache.
        """
        if not session_id:
            raise ValueError("Session ID is required.")

        user_data = await self.cache_repository.get_user_session_data(session_id)

        if user_data:
            return UserDetail(**user_data)

        return None

    async def set(self, key: str, value: dict, ttl_seconds: int = 60) -> None:
        """
        Set a key-value pair in the cache with an optional TTL.
        """
        if not key or not value:
            raise ValueError("Key and value are required.")

        await self.cache_repository.set(key, value, ttl_seconds)

    async def get(self, key: str) -> dict | None:
        """
        Get a value from the cache by key.
        """
        if not key:
            raise ValueError("Key is required.")

        return await self.cache_repository.get(key)

    async def delete(self, key: str) -> None:
        """
        Delete a key from the cache.
        """
        if not key:
            raise ValueError("Key is required.")

        await self.cache_repository.delete(key)


def get_cache_service(cache_repository: CacheRepository = Depends(get_cache_repository)) -> CacheService:
    """
    Dependency to get the cache service instance.
    """
    return CacheService(cache_repository=cache_repository)