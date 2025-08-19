import pytest
import bcrypt
from src.app.services.login_service import LoginService


@pytest.fixture
def mock_user():
    class User:
        id = 1
        email = "user@example.com"
        username = "user1"
        password = bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode()
        def is_admin(self): return False
    return User()


@pytest.fixture
def mock_repo(mock_user):
    class MockRepo:
        async def get_by_email(self, email):
            if email == mock_user.email:
                return mock_user
            return None
    return MockRepo()


@pytest.mark.asyncio
async def test_authenticate_user_success(mock_repo):
    service = LoginService(user_repository=mock_repo)
    user = await service.authenticate_user("user@example.com", "password123")

    assert user is not None
    assert user.username == "user1"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(mock_repo):
    service = LoginService(user_repository=mock_repo)
    user = await service.authenticate_user("user@example.com", "wrongpassword")
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_nonexistent_user():
    class EmptyRepo:
        async def get_by_email(self, email):
            return None

    service = LoginService(user_repository=EmptyRepo())
    user = await service.authenticate_user("no@user.com", "pass")
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password_field():
    class InvalidUser:
        password = None

    class BadRepo:
        async def get_by_email(self, email):
            return InvalidUser()

    service = LoginService(user_repository=BadRepo())
    user = await service.authenticate_user("user@example.com", "pass")
    assert user is None
