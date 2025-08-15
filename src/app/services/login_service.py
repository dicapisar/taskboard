import bcrypt
from fastapi import Depends

from src.app.models.user import User
from src.app.repositories.user_repository import UserRepository, get_user_repository

class LoginService:
    def __init__(self, user_repository: UserRepository):
        self.repo = user_repository

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.repo.get_by_email(email)
        if not user or not isinstance(user.password, str):
            return None

        password_matches = bcrypt.checkpw(password.encode(), user.password.encode())

        if password_matches:
            return user

        return None

def get_login_service(user_repository: UserRepository = Depends(get_user_repository)) -> LoginService:
    """
    Dependency to get the login service instance.
    """
    return LoginService(user_repository=user_repository)