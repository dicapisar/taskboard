import pytest
from httpx import AsyncClient
from fastapi import status
from src.app.main import app
from pydantic import EmailStr


@pytest.mark.anyio
async def test_upload_profile_image(monkeypatch, tmp_path):
    from io import BytesIO

    # Crear archivo simulado PNG válido
    image_bytes = BytesIO(b"fake_image_data")
    image_bytes.name = "image.png"

    # Monkeypatch para evitar escritura en disco real
    monkeypatch.setattr("src.app.api.v1.user_settings.UPLOAD_PROFILE_IMAGE_DIR", str(tmp_path))

    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.cookies.set("session_id", "abc123")
        response = await ac.post(
            "/api/v1/user_settings/profile_image",
            files={"file": ("image.png", image_bytes, "image/png")}
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Profile image uploaded successfully"


@pytest.mark.anyio
async def test_update_user_details_success(monkeypatch):
    class MockUserService:
        async def is_username_exists(self, username):
            return False
        async def is_email_exists(self, email):
            return False
        async def update_user_details(self, user_detail, user_id):
            return
    class MockCacheService:
        async def set_user_session_data(self, session_id, user_data):
            return

    from src.app.services.user_service import get_user_service
    from src.app.services.cache_service import get_cache_service
    app.dependency_overrides[get_user_service] = lambda: MockUserService()
    app.dependency_overrides[get_cache_service] = lambda: MockCacheService()

    payload = {
        "username": "new_user",
        "email": "new@example.com"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.cookies.set("session_id", "abc123")
        response = await ac.post("/api/v1/user_settings/user_details", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "User details updated successfully"


@pytest.mark.anyio
async def test_update_password(monkeypatch):
    class MockUserService:
        async def update_user_password(self, user_id, old_password, new_password):
            return

    from src.app.services.user_service import get_user_service
    app.dependency_overrides[get_user_service] = lambda: MockUserService()

    payload = {
        "old_password": "oldpass",
        "new_password": "newpass"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.cookies.set("session_id", "abc123")
        response = await ac.post("/api/v1/user_settings/password", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Password updated successfully"


@pytest.mark.anyio
async def test_delete_user(monkeypatch):
    class MockUserService:
        cache_service = type("CacheService", (), {"delete": lambda self, key: None})()
        async def delete_user(self, user_id):
            return

    from src.app.services.user_service import get_user_service
    app.dependency_overrides[get_user_service] = lambda: MockUserService()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.cookies.set("session_id", "abc123")
        response = await ac.delete("/api/v1/user_settings")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "User deleted successfully"
