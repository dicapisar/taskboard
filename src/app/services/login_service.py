from src.app.models.user import User
from src.app.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

class LoginService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.repo.get_by_email(email)
        if user and user.password == password:
            return user
        return None
