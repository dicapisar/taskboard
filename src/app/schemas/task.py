from datetime import date
from enum import Enum

from pydantic import BaseModel

class TaskStatusEnum(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False
    priority: int = 1  # Default priority set to 1
    status: TaskStatusEnum = "not_started"   # Default status set to "not_started"
    due_date: date | None = None  # Optional due date field
    subject: str | None = None  # Optional subject field

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    id: int  # Include ID for updates
    class Config:
        from_attributes = True  # Pydantic v2 compatibility
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy models

class TaskChangeStatus(BaseModel):
    status: TaskStatusEnum  # Status to change the task

    class Config:
        from_attributes = True  # Pydantic v2 compatibility
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy models


class TaskOut(TaskBase):
    id: int
    created_at: date  # ISO format date string for created_at
    owner_id: int  # ID of the user who owns the task

    class Config:
        from_attributes = True  # Pydantic v2 compatibility
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy models