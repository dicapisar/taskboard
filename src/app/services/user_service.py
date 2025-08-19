# Import libraries for password hashing and dependency injection
import bcrypt
from fastapi import Depends

# Import repository and service dependencies
from src.app.repositories.user_repository import UserRepository, get_user_repository
from src.app.services.cache_service import CacheService, get_cache_service
from src.app.schemas.user import UserCreate, UserUpdate
from src.app.models.user import User

# Constants for cache key and time-to-live (TTL)
CACHE_KEY_ALL_USERS = "users:all"
CACHE_TTL_SECONDS = 60


class UserService:
    """
    UserService handles business logic for managing user accounts,
    including creating, retrieving, updating, and deleting users.
    It also manages caching behavior.
    """

    def __init__(self, user_repository: UserRepository, cache_service: CacheService):
        """
        Initialize the service with a user repository and cache service.
        """
        self.user_repository = user_repository
        self.cache_service = cache_service

    async def create_user(self, data: UserCreate):
        """
        Create a new user with default role and hashed password.
        It also invalidates the cached list of users after creation.

        :param data: UserCreate schema with new user details.
        :return: The created user instance.
        """
        # Create a User instance from the input data
        user_model = User(**data.model_dump())
        user_model.role_id = 2  # Assign default role
        user_model.is_active = True  # Activate user account

        # Hash the password securely
        hashed_pw = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode()
        user_model.password = hashed_pw

        # Save the user to the database
        user = await self.user_repository.create(user_model)

        # Invalidate cached user list
        await self.cache_service.delete(CACHE_KEY_ALL_USERS)

        return user

    async def is_username_exists(self, username: str):
        """
        Check if a user with the given username exists.

        :param username: Username to check.
        :return: True if the username exists, False otherwise.
        """
        return await self.user_repository.get_by_username(username) is not None

    async def is_email_exists(self, email: str):
        """
        Check if a user with the given email exists.

        :param email: Email to check.
        :return: True if the email exists, False otherwise.
        """
        return await self.user_repository.get_by_email(email) is not None

    async def list_users(self):
        """
        Retrieve a list of all users.
        If cached, return from cache; otherwise fetch from database,
        cache the result, and return it.

        :return: A dictionary with a list of users.
        """
        cached = await self.cache_service.get(CACHE_KEY_ALL_USERS)
        if cached:
            return cached

        # Fetch from DB if not cached
        users = await self.user_repository.list_all()
        serializable = [
            {"id": u.id, "username": u.username, "email": u.email}
            for u in users
        ]

        cache_users = {"users": serializable}

        # Store in cache
        await self.cache_service.set(
            CACHE_KEY_ALL_USERS,
            cache_users,
            ttl_seconds=CACHE_TTL_SECONDS
        )

        return cache_users

    async def update_user_details(self, user_detail: UserUpdate, user_id: int):
        """
        Update username and email for a specific user.

        :param user_detail: Updated user details.
        :param user_id: ID of the user to update.
        :return: The updated user instance.
        """
        user = await self.user_repository.get_user_by_id(user_id)

        user.email = user_detail.email.__str__()
        user.username = user_detail.username

        updated_user = await self.user_repository.update_user(user)

        # Invalidate cached user list after update
        await self.cache_service.delete(CACHE_KEY_ALL_USERS)

        return updated_user

    async def update_user_password(self, user_id: int, old_password: str, new_password: str):
        """
        Update the user's password if the old password matches.

        :param user_id: ID of the user whose password is being changed.
        :param old_password: Current password to verify.
        :param new_password: New password to set.
        """
        user = await self.user_repository.get_user_by_id(user_id)

        # Check if user exists and old password matches
        if not user or not user.password != old_password:
            raise ValueError("Old password is incorrect or user not found")

        # Hash new password and save
        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode()
        user.password = hashed_pw
        await self.user_repository.update_user(user)

        # Invalidate cache
        await self.cache_service.delete(CACHE_KEY_ALL_USERS)

        return

    async def delete_user(self, user_id: int):
        """
        Delete a user from the system.

        :param user_id: ID of the user to delete.
        :return: None if successful, or raises an error if user is not found.
        """
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        await self.user_repository.delete_user(user_id)

        # Invalidate cache
        await self.cache_service.delete(CACHE_KEY_ALL_USERS)

        return None


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    cache_service: CacheService = Depends(get_cache_service)
) -> UserService:
    """
    Dependency injector for UserService.

    :return: Instance of UserService with required dependencies.
    """
    return UserService(user_repository=user_repository, cache_service=cache_service)