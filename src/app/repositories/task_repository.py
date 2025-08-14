import datetime
from typing import Protocol, List, Any, Coroutine

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.models.task import Task
from src.app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from fastapi import Depends
from src.app.core.database import get_db


def task_to_task_out(task: Task) -> TaskOut:
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


class TaskRepository(Protocol):
    async def get_all_tasks_by_user_id(self, user_id) -> List[TaskOut]: ...
    async def get_task_by_id_and_user_id(self, task_id, user_id) -> TaskOut | None: ...
    async def create_task(self, task_data: TaskCreate, user_id: int) -> TaskOut: ...
    async def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskOut: ...
    async def delete_task_(self, task_id: int) -> bool: ...


class TaskRepositoryImpl:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_tasks_by_user_id(self, user_id) -> List[TaskOut]:
        query = select(Task).where(Task.owner_id == user_id)
        result = await self.db.execute(query)

        if result is None or result.scalars() is None:
            return []

        task_list = []

        for task in result.scalars():
            task_list.append(task_to_task_out(task))

        return task_list

    async def get_task_by_id_and_user_id(self, task_id, user_id) -> TaskOut | None:
        query = select(Task).where(Task.id == task_id, Task.owner_id == user_id)
        result = await self.db.execute(query)
        task = result.scalars().first()
        if task is None:
            return None
        return task_to_task_out(task)

    async def create_task(self, task_data: TaskCreate, user_id: int) -> TaskOut:
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
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return TaskOut.model_validate(task)

    async def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskOut | None:
        query = select(Task).where(Task.id == task_id)
        result = await self.db.execute(query)
        task = result.scalars().first()

        if task is None:
            return None

        # Update task fields
        task.title = task_data.title
        task.description = task_data.description
        task.is_completed = task_data.completed
        task.priority = task_data.priority
        task.status = task_data.status
        task.due_date = task_data.due_date
        task.subject = task_data.subject

        await self.db.commit()
        await self.db.refresh(task)
        task.created_at = task.created_at.date()  # Ensure created_at is in date format
        return TaskOut.model_validate(task)

    async def delete_task_(self, task_id: int) -> bool:
        query = select(Task).where(Task.id == task_id)
        result = self.db.execute(query)
        task = result.scalars().first()

        if task is None:
            return False

        self.db.delete(task)
        self.db.commit()
        return True

def get_task_repository(db: AsyncSession = Depends(get_db)) -> TaskRepository:
    """
    Dependency to get the task repository instance.
    """

    return TaskRepositoryImpl(db=db)