from pydantic import BaseModel

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False
    priority: int = 1  # Default priority set to 1
    status: str = "not_started"  # Default status set to "not_started"
    due_date: str | None = None  # ISO format date string
    subject: str | None = None  # Optional subject field
    owner_id: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    id: int  # Include ID for updates
    class Config:
        from_attributes = True  # Pydantic v2 compatibility
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy models

class TaskOut(TaskBase):
    id: int
    created_at: str  # ISO format date string

    class Config:
        from_attributes = True  # Pydantic v2 compatibility
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy models