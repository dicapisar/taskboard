import pytest
from datetime import date
from src.app.repositories.task_repository import TaskRepository
from src.app.models.task import Task
from src.app.schemas.task import TaskCreate, TaskUpdate


@pytest.fixture
def fake_db():
    class FakeSession:
        def __init__(self):
            self.tasks = [
                Task(id=1, title="Task 1", description="desc", completed=False, priority=1,
                     status="not_started", due_date=date.today(), subject="math", owner_id=1)
            ]

        def query(self, model):
            class Query:
                def __init__(self, data):
                    self.data = data

                def filter(self, *args):
                    return self

                def all(self):
                    return self.data

                def first(self):
                    return self.data[0] if self.data else None

            return Query(self.tasks)

        def add(self, obj):
            obj.id = 2
            self.tasks.append(obj)

        def commit(self): pass
        def refresh(self, obj): pass
        def delete(self, obj): self.tasks.remove(obj)

    return FakeSession()


@pytest.mark.asyncio
async def test_get_all_tasks_by_user_id(fake_db):
    repo = TaskRepository(db=fake_db)
    tasks = await repo.get_all_tasks_by_user_id(user_id=1)
    assert len(tasks) == 1
    assert tasks[0].title == "Task 1"


@pytest.mark.asyncio
async def test_get_task_by_id_and_user_id(fake_db):
    repo = TaskRepository(db=fake_db)
    task = await repo.get_task_by_id_and_user_id(1, 1)
    assert task.id == 1


@pytest.mark.asyncio
async def test_create_task(fake_db):
    repo = TaskRepository(db=fake_db)
    task_data = TaskCreate(
        title="New Task", description="desc", completed=False, priority=2,
        status="in_progress", due_date=date.today(), subject="science"
    )
    task = await repo.create_task(task_data, user_id=1)
    assert task.title == "New Task"


@pytest.mark.asyncio
async def test_update_task(fake_db):
    repo = TaskRepository(db=fake_db)
    task_data = TaskUpdate(
        id=1, title="Updated", description="updated", completed=True,
        priority=3, status="completed", due_date=date.today(), subject="english"
    )
    task = await repo.update_task(1, task_data)
    assert task.title == "Updated"
    assert task.completed is True


@pytest.mark.asyncio
async def test_delete_task(fake_db):
    repo = TaskRepository(db=fake_db)
    result = await repo.delete_task_(1)
    assert result is True
