# Import datetime module for handling dates and times
import datetime

# Import necessary types from SQLAlchemy
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import the base class for all ORM models
from src.app.core.database import Base

# ---------------------------- Task ORM Model ----------------------------

class Task(Base):
    """
    This class represents a task in the database.
    Each task is assigned to one user and includes details such as title, status, priority, and deadlines.
    """

    __tablename__ = "tasks"  # Name of the table in the database

    # ---------------------------- Table Columns ----------------------------

    # Primary key: Unique ID for each task
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Title of the task (required)
    title: Mapped[str] = mapped_column(String(100), nullable=False)

    # Optional description of the task
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    # Foreign key linking the task to the owner (user)
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),  # Delete tasks if the user is deleted
        nullable=False,
        index=True
    )

    # Indicates if the task is completed (0 = False, 1 = True)
    is_completed: Mapped[bool] = mapped_column(Integer, default=False, nullable=False)

    # Priority level of the task (default: 1)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Due date of the task (must be set)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Timestamp when the task was created (defaults to current time)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    # Status of the task (default: "not_started")
    status: Mapped[str] = mapped_column(String(50), default="not_started", nullable=False)

    # Optional subject or category of the task
    subject: Mapped[str] = mapped_column(String(100), nullable=True)

    # ---------------------------- Relationships ----------------------------

    # Relationship to the User model (a task belongs to one user)
    owner: Mapped["User"] = relationship(back_populates="tasks")

    # ---------------------------- Representation ----------------------------

    def __repr__(self) -> str:
        """
        Return a string representation of the task.
        Useful for logging and debugging.
        """
        return f"<Task(id={self.id}, title={self.title}, is_completed={self.is_completed})>"