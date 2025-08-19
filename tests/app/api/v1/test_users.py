import pytest
from httpx import AsyncClient
from fastapi import status
from src.app.main import app


@pytest.mark.anyio
async def test_create_user_success(monkeypatch):
    class MockUser:
        id = 1
        username = "new_user"
        email = "new@example.com"
        def is_admin(self): return False

    class MockUserService:
        async def is_username_exists(self, username): return False
        async def is_email_exists(self, email): return False
        async def create_user(self, payload): return MockUser()

    from src.app.services.user_service import get_user_service
    app.dependency_overrides[get_user_service] = lambda: MockUserService()

    payload = {
        "username": "new_user",
        "email": "new@example.com",
        "password": "secret123"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/users", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["username"] == "new_user"


@pytest.mark.anyio
async def test_create_user_conflict_username(monkeypatch):
    class MockUserService:
        async def is_username_exists(self, username): return True
        async def is_email_exists(self, email): return False

    from src.app.services.user_service import get_user_service
    app.dependency_overrides[get_user_service] = lambda: MockUserService()

    payload = {
        "username": "existing_user",
        "email": "user@example.com",
        "password": "secret"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/users", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Username already exists"


@pytest.mark.anyio
async def test_create_user_conflict_email(monkeypatch):
    class MockUserService:
        async def is_username_exists(self, username): return False
        async def is_email_exists(self, email): return True

    from src.app.services.user_service import get_user_service
    app.dependency_overrides[get_user_service] = lambda: MockUserService()

    payload = {
        "username": "user",
        "email": "existing@example.com",
        "password": "secret"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/users", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.anyio
async def test_list_users_success(monkeypatch):
    class MockUserService:
        async def list_users(self):
            return {"users": [{"id": 1, "username": "user1", "email": "u1@example.com"}]}

    from src.app.services.user_service import get_user_service
    app.dependency_overrides[get_user_service] = lambda: MockUserService()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/users")

    assert response.status_code == status.HTTP_200_OK
    assert "users" in response.json()["data"]
