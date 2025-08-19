import pytest
from src.app.services.user_service import UserService
from src.app.dtos.user_detail import UserDetail
from src.app.schemas.user import UserCreate, UserUpdate, UserPasswordUpdate


@pytest.fixture
def mock_repo():
    class MockRepo:
        def __init__(self):
            self.users = []

        async def is_username_exists(self, username):
            return username == "existing_user"

        async def is_email_exists(self, email):
            return email == "existing@example.com"

        async def create_user(self, payload):
            return type("User", (), {
                "id": 1,
                "username": payload.username,
                "email": payload.email,
                "is_admin": lambda self: False
            })()

        async def update_user_details(self, user_id, payload):
            return

        async def update_user_password(self, user_id, old_password, new_password):
            return

        async def delete_user(self, user_id):
            return

        async def list_users(self):
            return [{"id": 1, "username": "test", "email": "test@example.com"}]

    return MockRepo()


@pytest.fixture
def mock_cache():
    class MockCache:
        async def set_user_session_data(self, session_id, user_detail): pass
        async def delete(self, key): pass
    return MockCache()


@pytest.mark.asyncio
async def test_is_username_exists(mock_repo):
    service = UserService(user_repository=mock_repo)
    assert await service.is_username_exists("existing_user") is True
    assert await service.is_username_exists("new_user") is False


@pytest.mark.asyncio
async def test_is_email_exists(mock_repo):
    service = UserService(user_repository=mock_repo)
    assert await service.is_email_exists("existing@example.com") is True
    assert await service.is_email_exists("new@example.com") is False


@pytest.mark.asyncio
async def test_create_user(mock_repo):
    service = UserService(user_repository=mock_repo)
    payload = UserCreate(username="new", email="new@example.com", password="pass")
    user = await service.create_user(payload)
    assert user.username == "new"


@pytest.mark.asyncio
async def test_update_user_details(mock_repo, mock_cache):
    service = UserService(user_repository=mock_repo, cache_service=mock_cache)
    payload = UserUpdate(username="updated", email="updated@example.com")
    await service.update_user_details(payload, user_id=1)
    # No assertions, just ensuring no exceptions


@pytest.mark.asyncio
async def test_update_user_password(mock_repo):
    service = UserService(user_repository=mock_repo)
    payload = UserPasswordUpdate(old_password="old", new_password="new")
    await service.update_user_password(1, payload.old_password, payload.new_password)


@pytest.mark.asyncio
async def test_delete_user(mock_repo, mock_cache):
    service = UserService(user_repository=mock_repo, cache_service=mock_cache)
    await service.delete_user(user_id=1)


@pytest.mark.asyncio
async def test_list_users(mock_repo):
    service = UserService(user_repository=mock_repo)
    result = await service.list_users()
    assert isinstance(result, dict)
    assert "users" in result
    assert result["users"][0]["username"] == "test"
