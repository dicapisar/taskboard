# Import type hints
from typing import Protocol, Sequence

# Import FastAPI and SQLAlchemy dependencies
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import database session and User model
from src.app.core.database import get_db
from src.app.models.user import User

# ---------------------------- User Repository Protocol ----------------------------

class UserRepository(Protocol):
    """
    Protocol (interface) for user-related database operations.
    This defines the contract that any repository must implement.
    """

    async def create(self, user: User) -> User: ...
    async def list_all(self) -> Sequence[User]: ...
    async def get_by_username(self, username: str) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def get_user_by_id(self, user_id: int) -> User | None: ...
    async def update_user(self, user: User) -> User: ...
    async def delete_user(self, user_id: int) -> User | None: ...
    pass

# ---------------------------- User Repository Implementation ----------------------------

class UserRepositoryImpl:
    """
    Implementation of the UserRepository using SQLAlchemy and AsyncSession.
    Provides full CRUD operations for the User model.
    """

    def __init__(self, db: AsyncSession):
        # Store the database session
        self.db = db

    async def create(self, user: User) -> User:
        """
        Add a new user to the database.
        """
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def list_all(self) -> Sequence[User]:
        """
        Return a list of all users from the database.
        """
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_by_username(self, username: str) -> User | None:
        """
        Find a user by username.
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        """
        Find a user by email address.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def update_user(self, user: User) -> User:
        """
        Commit any changes made to the user object.
        """
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> User:
        """
        Delete a user by ID if they exist.
        """
        user = await self.get_user_by_id(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
        return user

# ---------------------------- Dependency Injection ----------------------------

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepositoryImpl:
    """
    Dependency function that returns a UserRepository instance.
    Allows automatic injection in services and routes.
    """
    return UserRepositoryImpl(db=db)