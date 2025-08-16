import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True )
    is_completed: Mapped[bool] = mapped_column(Integer, default=False, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # Default priority set to 1
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="not_started", nullable=False)  # Default status set to "not_started"
    subject: Mapped[str] = mapped_column(String(100), nullable=True)

    # Relationship with User
    owner: Mapped["User"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, is_completed={self.is_completed})>"