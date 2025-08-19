import pytest
from httpx import AsyncClient
from fastapi import status
from src.app.main import app


@pytest.mark.anyio
async def test_logout_success(monkeypatch):
    class MockCacheService:
        async def delete(self, key):
            assert key == "session:abc123"

    class MockRequest:
        cookies = {"session_id": "abc123"}
        state = type("State", (), {"session": {"id": 1}})()

    from src.app.services.cache_service import get_cache_service
    app.dependency_overrides[get_cache_service] = lambda: MockCacheService()

    # Simula una sesión válida en cookies
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/logout",
            cookies={"session_id": "abc123"}
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True
    assert response.json()["message"] == "Login successful"


@pytest.mark.anyio
async def test_logout_unauthenticated(monkeypatch):
    class MockCacheService:
        async def delete(self, key):
            pass

    from src.app.services.cache_service import get_cache_service
    app.dependency_overrides[get_cache_service] = lambda: MockCacheService()

    # No hay sesión ni cookies válidas
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/logout")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "User not authenticated"
