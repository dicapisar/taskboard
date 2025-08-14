from typing import Protocol, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_db
from src.app.models.user import User


class UserRepository(Protocol):
    async def create(self, user: User) -> User: ...
    async def list_all(self) -> Sequence[User]: ...
    async def get_by_username(self, username: str) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def get_user_by_id(self, user_id: int) -> User | None: ...
    async def update_user(self, user: User) -> User: ...
    async def delete_user(self, user_id: int) -> User | None: ...
    pass

class UserRepositoryImpl:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def list_all(self) -> Sequence[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def update_user(self, user: User) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> User:
        user = await self.get_user_by_id(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
        return user

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepositoryImpl:
    """
    Dependency to get the user repository instance.
    """
    return UserRepositoryImpl(db=db)