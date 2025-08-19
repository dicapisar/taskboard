# Import the bcrypt library for password hashing
import bcrypt

# Import FastAPI dependency injection utility
from fastapi import Depends

# Import the User model and repository dependencies
from src.app.models.user import User
from src.app.repositories.user_repository import UserRepository, get_user_repository

# ---------------------------- CLASS: LoginService ----------------------------

class LoginService:
    """
    This service handles the logic related to user login and authentication.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the login service with a user repository to access user data.
        """
        self.repo = user_repository

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """
        Check if the user exists and if the provided password is correct.

        Parameters:
        - email: the user's email address
        - password: the plain text password entered by the user

        Returns:
        - The User object if authentication is successful, otherwise None
        """
        # Search for the user in the database using their email
        user = await self.repo.get_by_email(email)

        # If user does not exist or has an invalid password format, return None
        if not user or not isinstance(user.password, str):
            return None

        # Check if the provided password matches the hashed password
        password_matches = bcrypt.checkpw(password.encode(), user.password.encode())

        # Return user object only if passwords match
        if password_matches:
            return user

        return None

# ------------------------ DEPENDENCY INJECTION ------------------------

def get_login_service(user_repository: UserRepository = Depends(get_user_repository)) -> LoginService:
    """
    Dependency function to provide an instance of LoginService.

    Returns:
    - A LoginService object with the required user repository injected.
    """
    return LoginService(user_repository=user_repository)