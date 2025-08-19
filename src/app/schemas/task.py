# Import date class for due dates and creation dates
from datetime import date

# Import Enum to define fixed status values
from enum import Enum

# Import Pydantic for data validation and serialization
from pydantic import BaseModel

# ---------------------------- ENUM: TaskStatusEnum ----------------------------

class TaskStatusEnum(str, Enum):
    """
    Enum class to represent the allowed values for task status.
    """

    NOT_STARTED = "not_started"     # Task has not been started yet
    IN_PROGRESS = "in_progress"     # Task is currently being worked on
    COMPLETED = "completed"         # Task has been finished
    BLOCKED = "blocked"             # Task cannot move forward due to an issue

# ---------------------------- BASE SCHEMA: TaskBase ----------------------------

class TaskBase(BaseModel):
    """
    Base schema that contains common fields shared by other task models.
    """

    title: str                               # Title of the task (required)
    description: str | None = None           # Optional task description
    completed: bool = False                  # Status flag, default is not completed
    priority: int = 1                        # Task priority level; default is 1 (low)
    status: TaskStatusEnum = "not_started"   # Task status using defined enum; default is "not_started"
    due_date: date | None = None             # Optional due date for the task
    subject: str | None = None               # Optional subject related to the task

# ---------------------------- CREATE SCHEMA: TaskCreate ----------------------------

class TaskCreate(TaskBase):
    """
    Schema used for creating a new task.
    Inherits all fields from TaskBase.
    """
    pass

# ---------------------------- UPDATE SCHEMA: TaskUpdate ----------------------------

class TaskUpdate(TaskBase):
    """
    Schema used for updating an existing task.
    Includes the task ID.
    """

    id: int  # ID of the task to be updated

    class Config:
        from_attributes = True  # Enables model creation from ORM-like objects (Pydantic v2)
        orm_mode = True         # Compatibility with SQLAlchemy ORM models (for backward compatibility)

# ---------------------------- STATUS CHANGE SCHEMA: TaskChangeStatus ----------------------------

class TaskChangeStatus(BaseModel):
    """
    Schema used to change the status of a task.
    """

    status: TaskStatusEnum  # New status to apply to the task

    class Config:
        from_attributes = True  # Enables model creation from ORM-like objects (Pydantic v2)
        orm_mode = True         # Compatibility with SQLAlchemy ORM models

# ---------------------------- RESPONSE SCHEMA: TaskOut ----------------------------

class TaskOut(TaskBase):
    """
    Schema used when returning task data from the system.
    Includes extra read-only fields such as ID and timestamps.
    """

    id: int                      # Unique identifier of the task
    created_at: date            # Date when the task was created
    owner_id: int               # ID of the user who created or owns the task

    class Config:
        from_attributes = True  # Enables model creation from ORM-like objects (Pydantic v2)
        orm_mode = True         # Compatibility with SQLAlchemy ORM models