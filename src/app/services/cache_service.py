# Importing the user detail data structure and the cache repository interface
from src.app.dtos.user_detail import UserDetail
from src.app.repositories.cache_repository import CacheRepository, get_cache_repository

# Importing dependency injection utility from FastAPI
from fastapi import Depends


# ---------------------------- CLASS: CacheService ----------------------------

class CacheService:
    """
    This service class provides methods to manage caching logic using Redis.
    It acts as a middle layer between the FastAPI routes and the cache repository.
    """

    def __init__(self, cache_repository: CacheRepository):
        """
        Initialize the CacheService with a repository implementation.
        """
        self.cache_repository = cache_repository

    async def set_user_session_data(self, session_id: str, user_data: UserDetail) -> None:
        """
        Store user session data in the Redis cache.

        Parameters:
        - session_id: unique session identifier as a string.
        - user_data: instance of UserDetail containing user information.
        """
        if not session_id or not user_data:
            raise ValueError("Session ID and user data are required.")

        # Convert user data to dictionary format before storing
        await self.cache_repository.set_user_session_data(session_id, user_data.__dict__)

    async def get_user_session_data(self, session_id: str) -> UserDetail | None:
        """
        Retrieve user session data from the Redis cache.

        Parameters:
        - session_id: unique session identifier.

        Returns:
        - UserDetail object if found; otherwise, None.
        """
        if not session_id:
            raise ValueError("Session ID is required.")

        user_data = await self.cache_repository.get_user_session_data(session_id)

        if user_data:
            # Deserialize the dictionary back to a UserDetail object
            return UserDetail(**user_data)

        return None

    async def set(self, key: str, value: dict, ttl_seconds: int = 60) -> None:
        """
        Store a key-value pair in the cache with an optional time-to-live (TTL).

        Parameters:
        - key: the cache key
        - value: the data to store (in dictionary format)
        - ttl_seconds: how long the data should be stored (in seconds)
        """
        if not key or not value:
            raise ValueError("Key and value are required.")

        await self.cache_repository.set(key, value, ttl_seconds)

    async def get(self, key: str) -> dict | None:
        """
        Retrieve a value from the cache using the provided key.

        Parameters:
        - key: the cache key

        Returns:
        - The stored value as a dictionary, or None if not found.
        """
        if not key:
            raise ValueError("Key is required.")

        return await self.cache_repository.get(key)

    async def delete(self, key: str) -> None:
        """
        Delete a specific key from the cache.

        Parameters:
        - key: the cache key to be deleted
        """
        if not key:
            raise ValueError("Key is required.")

        await self.cache_repository.delete(key)


# ---------------------------- DEPENDENCY INJECTION ----------------------------

def get_cache_service(cache_repository: CacheRepository = Depends(get_cache_repository)) -> CacheService:
    """
    Dependency function to provide an instance of CacheService via FastAPI's DI system.

    Returns:
    - An initialized CacheService object with a bound CacheRepository.
    """
    return CacheService(cache_repository=cache_repository)