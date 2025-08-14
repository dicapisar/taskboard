from fastapi import Depends

from src.app.repositories.user_repository import UserRepository, get_user_repository
from src.app.services.cache_service import CacheService, get_cache_service
from src.app.schemas.user import UserCreate, UserUpdate
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

    async def update_user_details(self, user_detail: UserUpdate, user_id: int):

        user = await self.user_repository.get_user_by_id(user_id)

        user.email = user_detail.email.__str__()
        user.username = user_detail.username

        updated_user = await self.user_repository.update_user(user)

        # Invalidate cache after updating user details
        await self.cache_service.delete(CACHE_KEY_ALL_USERS)

        return updated_user

    async def update_user_password(self, user_id: int, old_password: str, new_password: str):
        """
        Update the user's password.
        This method should include logic to verify the old password and set the new password.
        """
        user = await self.user_repository.get_user_by_id(user_id)
        if not user or not user.password != old_password:
            raise ValueError("Old password is incorrect or user not found")

        user.password = new_password
        updated_user = await self.user_repository.update_user(user)

        # Invalidate cache after updating password
        await self.cache_service.delete(CACHE_KEY_ALL_USERS)

        return

    async def delete_user(self, user_id: int):
        """
        Delete a user by ID.
        This method should include logic to delete the user from the database.
        """
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        await self.user_repository.delete_user(user_id)

        # Invalidate cache after deleting user
        await self.cache_service.delete(CACHE_KEY_ALL_USERS)

        return None


def get_user_service(user_repository: UserRepository = Depends(get_user_repository), cache_service: CacheService = Depends(get_cache_service)) -> UserService:
    """
    Dependency to get the user service instance.
    """
    return UserService(user_repository=user_repository, cache_service=cache_service)