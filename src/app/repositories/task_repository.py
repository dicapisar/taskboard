# Import necessary modules
import datetime
from typing import Protocol, List, Any, Coroutine

# Import SQLAlchemy components
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import task-related models and schemas
from src.app.models.task import Task
from src.app.schemas.task import TaskCreate, TaskOut, TaskUpdate

# Import FastAPI dependency tools
from fastapi import Depends
from src.app.core.database import get_db

# ---------------------------- Utility Function ----------------------------

def task_to_task_out(task: Task) -> TaskOut:
    """
    Convert a Task model instance into a TaskOut schema instance.
    This function is used to return clean task data to the client.
    """
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.is_completed,
        priority=task.priority,
        status=task.status,
        due_date=task.due_date.date(),
        subject=task.subject,
        created_at=task.created_at.date(),
        owner_id=task.owner_id
    )

# ---------------------------- Task Repository Protocol ----------------------------

class TaskRepository(Protocol):
    """
    Interface (protocol) that defines the required methods for managing tasks.
    Any repository implementing this interface must define these methods.
    """

    async def get_all_tasks_by_user_id(self, user_id) -> List[TaskOut]: ...
    async def get_task_by_id_and_user_id(self, task_id, user_id) -> TaskOut | None: ...
    async def create_task(self, task_data: TaskCreate, user_id: int) -> TaskOut: ...
    async def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskOut: ...
    async def delete_task_(self, task_id: int) -> bool: ...

# ---------------------------- Task Repository Implementation ----------------------------

class TaskRepositoryImpl:
    """
    Concrete implementation of the TaskRepository interface.
    This class handles all task-related database operations.
    """

    def __init__(self, db: AsyncSession):
        # Assign the database session
        self.db = db

    async def get_all_tasks_by_user_id(self, user_id) -> List[TaskOut]:
        """
        Retrieve all tasks that belong to a specific user.
        """
        query = select(Task).where(Task.owner_id == user_id)
        result = await self.db.execute(query)

        if result is None or result.scalars() is None:
            return []

        task_list = []

        for task in result.scalars():
            task_list.append(task_to_task_out(task))

        return task_list

    async def get_task_by_id_and_user_id(self, task_id, user_id) -> TaskOut | None:
        """
        Retrieve a single task by its ID and the owner's user ID.
        """
        query = select(Task).where(Task.id == task_id, Task.owner_id == user_id)
        result = await self.db.execute(query)
        task = result.scalars().first()

        if task is None:
            return None

        return task_to_task_out(task)

    async def create_task(self, task_data: TaskCreate, user_id: int) -> TaskOut:
        """
        Create a new task and assign it to a specific user.
        """
        task = Task(
            title=task_data.title,
            description=task_data.description,
            owner_id=user_id,
            is_completed=task_data.completed,
            priority=task_data.priority,
            status=task_data.status,
            due_date=task_data.due_date,
            created_at=datetime.date.today(),
            subject=task_data.subject
        )

        # Add the new task to the session and commit
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        return TaskOut.model_validate(task)

    async def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskOut | None:
        """
        Update the fields of an existing task.
        """
        query = select(Task).where(Task.id == task_id)
        result = await self.db.execute(query)
        task = result.scalars().first()

        if task is None:
            return None

        # Apply updates
        task.title = task_data.title
        task.description = task_data.description
        task.is_completed = task_data.completed
        task.priority = task_data.priority
        task.status = task_data.status
        task.due_date = task_data.due_date
        task.subject = task_data.subject

        # Commit changes to the database
        await self.db.commit()
        await self.db.refresh(task)

        # Ensure that created_at is in date format
        task.created_at = task.created_at.date()

        return TaskOut.model_validate(task)

    async def delete_task_(self, task_id: int) -> bool:
        """
        Delete a task by its ID.
        Returns True if successful, False if task not found.
        """
        query = select(Task).where(Task.id == task_id)
        result = await self.db.execute(query)
        task = result.scalars().first()

        if task is None:
            return False

        await self.db.delete(task)
        await self.db.commit()

        return True

# ---------------------------- Dependency Provider ----------------------------

def get_task_repository(db: AsyncSession = Depends(get_db)) -> TaskRepository:
    """
    Dependency function that returns an instance of TaskRepositoryImpl.
    This allows it to be injected into services or endpoints.
    """
    return TaskRepositoryImpl(db=db)