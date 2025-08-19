import pytest
from datetime import date
from src.app.services.task_service import TaskService
from src.app.schemas.task import TaskCreate, TaskUpdate, TaskStatusEnum
from src.app.schemas.task import TaskOut


@pytest.fixture
def mock_repo():
    class MockRepo:
        def __init__(self):
            self.db = {}

        async def get_all_tasks_by_user_id(self, user_id):
            return [TaskOut(
                id=1, title="Task", description="desc", completed=False,
                priority=1, status="not_started", due_date=date.today(),
                subject="Math", created_at=date.today(), owner_id=user_id
            )]

        async def get_task_by_id_and_user_id(self, task_id, user_id):
            if task_id == 1 and user_id == 1:
                return TaskOut(
                    id=task_id, title="Task", description="desc", completed=False,
                    priority=1, status="not_started", due_date=date.today(),
                    subject="Math", created_at=date.today(), owner_id=user_id
                )
            return None

        async def create_task(self, task_data, user_id):
            return TaskOut(
                id=1, title=task_data.title, description=task_data.description,
                completed=task_data.completed, priority=task_data.priority,
                status=task_data.status, due_date=task_data.due_date,
                subject=task_data.subject, created_at=date.today(), owner_id=user_id
            )

        async def update_task(self, task_id, task_data):
            return TaskOut(**task_data.model_dump(), created_at=date.today(), owner_id=1)

        async def delete_task_(self, task_id):
            return True

    return MockRepo()


@pytest.mark.asyncio
async def test_get_tasks(mock_repo):
    service = TaskService(task_repository=mock_repo)
    tasks = await service.get_tasks(1)
    assert len(tasks) == 1
    assert tasks[0].title == "Task"


@pytest.mark.asyncio
async def test_get_task_by_id(mock_repo):
    service = TaskService(task_repository=mock_repo)
    task = await service.get_task_by_id(1, 1)
    assert task.id == 1


@pytest.mark.asyncio
async def test_create_task(mock_repo):
    service = TaskService(task_repository=mock_repo)
    task_data = TaskCreate(
        title="New", description="desc", completed=False,
        priority=1, status="not_started", due_date=date.today(), subject="math"
    )
    task = await service.create_task(task_data, 1)
    assert task.title == "New"


@pytest.mark.asyncio
async def test_update_task(mock_repo):
    service = TaskService(task_repository=mock_repo)
    task_data = TaskUpdate(
        id=1, title="Updated", description="d", completed=True,
        priority=2, status="completed", due_date=date.today(), subject="sci"
    )
    task = await service.update_task(task_data, 1)
    assert task.title == "Updated"
    assert task.status == "completed"


@pytest.mark.asyncio
async def test_update_task_status(mock_repo):
    service = TaskService(task_repository=mock_repo)
    task = await service.update_task_status(1, TaskStatusEnum.IN_PROGRESS, 1)
    assert task.status == TaskStatusEnum.IN_PROGRESS


@pytest.mark.asyncio
async def test_delete_task(mock_repo):
    service = TaskService(task_repository=mock_repo)
    deleted = await service.delete_task(1, 1)
    assert deleted is True


@pytest.mark.asyncio
async def test_get_tasks_invalid_input(mock_repo):
    service = TaskService(task_repository=mock_repo)
    with pytest.raises(TypeError):
        await service.get_tasks("not-an-int")


@pytest.mark.asyncio
async def test_update_task_missing_id(mock_repo):
    service = TaskService(task_repository=mock_repo)
    task_data = TaskUpdate(
        id=None, title="fail", description="fail", completed=True,
        priority=1, status="not_started", due_date=date.today(), subject="math"
    )
    with pytest.raises(ValueError):
        await service.update_task(task_data, 1)
