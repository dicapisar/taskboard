import pytest
from httpx import AsyncClient
from fastapi import status
from fastapi.responses import Response
from src.app.main import app


@pytest.mark.anyio
async def test_login_success(monkeypatch):
    class MockLoginService:
        async def authenticate_user(self, email, password):
            return type("User", (), {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "is_admin": lambda self: False,
                "to_user_detail": lambda self: {
                    "id": 1,
                    "username": "testuser",
                    "email": "test@example.com",
                    "is_admin": False
                }
            })()

    class MockCacheService:
        async def set_user_session_data(self, session_id, user_data):
            return

    app.dependency_overrides = {}
    from src.app.services.login_service import get_login_service
    from src.app.services.cache_service import get_cache_service

    app.dependency_overrides[get_login_service] = lambda: MockLoginService()
    app.dependency_overrides[get_cache_service] = lambda: MockCacheService()

    payload = {
        "email": "test@example.com",
        "password": "password123"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/login", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True
    assert "session_id" in response.json()["data"]


@pytest.mark.anyio
async def test_login_invalid_credentials(monkeypatch):
    class MockLoginService:
        async def authenticate_user(self, email, password):
            return None

    class MockCacheService:
        async def set_user_session_data(self, session_id, user_data):
            pass

    from src.app.services.login_service import get_login_service
    from src.app.services.cache_service import get_cache_service

    app.dependency_overrides[get_login_service] = lambda: MockLoginService()
    app.dependency_overrides[get_cache_service] = lambda: MockCacheService()

    payload = {
        "email": "wrong@example.com",
        "password": "wrongpass"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/login", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"
