from fastapi import Depends

from src.app.repositories.user_repository import UserRepository, get_user_repository
from src.app.services.cache_service import CacheService, get_cache_service
from src.app.schemas.user import UserCreate
from src.app.models.user import User


CACHE_KEY_ALL_USERS = "users:all"
CACHE_TTL_SECONDS = 60

class UserService:
    def __init__(self, user_repository: UserRepository, cache_service: CacheService):
        self.user_repository = user_repository
        self.cache_service = cache_service

    async def create_user(self, data: UserCreate):
        # invalidar cache antes o después de commit

        user_model = User(**data.model_dump())
        user_model.role_id = 2
        user_model.is_active = True

        user = await self.user_repository.create(user_model)
        await self.cache_service.delete(CACHE_KEY_ALL_USERS)
        return user

    async def is_username_exists(self, username: str):
        """
        Check if a user exists by username.
        """
        return await self.user_repository.get_by_username(username) is not None

    async def is_email_exists(self, email: str):
        """
        Check if a user exists by email.
        """
        return await self.user_repository.get_by_email(email) is not None

    async def list_users(self):
        cached = await self.cache_service.get(CACHE_KEY_ALL_USERS)
        if cached:
            return cached

        users = await self.user_repository.list_all()
        serializable = [
            {"id": u.id, "username": u.username, "email": u.email}
            for u in users
        ]

        cache_users = {
            "users": serializable
        }

        await self.cache_service.set(
            CACHE_KEY_ALL_USERS,
            cache_users,
            ttl_seconds=CACHE_TTL_SECONDS
        )

        return cache_users


def get_user_service(user_repository: UserRepository = Depends(get_user_repository), cache_service: CacheService = Depends(get_cache_service)) -> UserService:
    """
    Dependency to get the user service instance.
    """
    return UserService(user_repository=user_repository, cache_service=cache_service)