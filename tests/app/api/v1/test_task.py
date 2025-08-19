import pytest
from httpx import AsyncClient
from fastapi import status
from src.app.main import app
from datetime import date


@pytest.fixture
def mock_session():
    return {"id": 1}


@pytest.mark.anyio
async def test_get_tasks_success(monkeypatch, mock_session):
    class MockTaskService:
        async def get_tasks(self, user_id):
            return [
                type("Task", (), {"model_dump": lambda self: {"id": 1}})()
            ]

    from src.app.services.task_service import get_task_service
    app.dependency_overrides[get_task_service] = lambda: MockTaskService()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.cookies.set("session_id", "abc123")
        response = await ac.get("/api/v1/tasks", cookies={"session_id": "abc123"})

    assert response.status_code == status.HTTP_200_OK
    assert "tasks" in response.json()["data"]


@pytest.mark.anyio
async def test_create_task_success(monkeypatch, mock_session):
    class MockTaskService:
        async def create_task(self, task_data, user_id):
            return type("Task", (), {
                "model_dump": lambda self: {"title": "New Task"}
            })()

    from src.app.services.task_service import get_task_service
    app.dependency_overrides[get_task_service] = lambda: MockTaskService()

    payload = {
        "title": "New Task",
        "description": "Test description",
        "completed": False,
        "priority": 1,
        "status": "not_started",
        "due_date": str(date.today()),
        "subject": "Test"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.cookies.set("session_id", "abc123")
        response = await ac.post("/api/v1/tasks", json=payload, cookies={"session_id": "abc123"})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["title"] == "New Task"


@pytest.mark.anyio
async def test_update_task_status_success(monkeypatch):
    class MockTaskService:
        async def update_task_status(self, task_id, status, user_id):
            return type("Task", (), {
                "model_dump": lambda self: {"status": status}
            })()

    from src.app.services.task_service import get_task_service
    app.dependency_overrides[get_task_service] = lambda: MockTaskService()

    payload = {"status": "in_progress"}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.cookies.set("session_id", "abc123")
        response = await ac.patch("/api/v1/tasks/1", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["status"] == "in_progress"


@pytest.mark.anyio
async def test_get_task_by_id_success(monkeypatch):
    class MockTaskService:
        async def get_task_by_id(self, task_id, user_id):
            return type("Task", (), {
                "model_dump": lambda self: {"id": task_id}
            })()

    from src.app.services.task_service import get_task_service
    app.dependency_overrides[get_task_service] = lambda: MockTaskService()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.cookies.set("session_id", "abc123")
        response = await ac.get("/api/v1/tasks/99")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["id"] == 99


@pytest.mark.anyio
async def test_update_task_success(monkeypatch):
    class MockTaskService:
        async def update_task(self, task_data, user_id):
            return type("Task", (), {
                "model_dump": lambda self: {"title": task_data.title}
            })()

    from src.app.services.task_service import get_task_service
    app.dependency_overrides[get_task_service] = lambda: MockTaskService()

    payload = {
        "id": 10,
        "title": "Updated Task",
        "description": "desc",
        "completed": False,
        "priority": 2,
        "status": "completed",
        "due_date": str(date.today()),
        "subject": "math"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.cookies.set("session_id", "abc123")
        response = await ac.post("/api/v1/tasks/10", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["title"] == "Updated Task"


@pytest.mark.anyio
async def test_delete_task_success(monkeypatch):
    class MockTaskService:
        async def delete_task(self, task_id, user_id):
            return True

    from src.app.services.task_service import get_task_service
    app.dependency_overrides[get_task_service] = lambda: MockTaskService()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.cookies.set("session_id", "abc123")
        response = await ac.delete("/api/v1/tasks/5")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Task deleted successfully"
