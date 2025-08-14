from src.app.dtos.user_detail import UserDetail
from src.app.repositories.cache_repository import CacheRepository

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


def get_cache_service(cache_repository: CacheRepository = Depends(CacheRepository)) -> CacheService:
    """
    Dependency to get the cache service instance.
    """
    return CacheService(cache_repository=cache_repository)