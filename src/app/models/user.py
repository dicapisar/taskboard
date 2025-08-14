from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.app.core.database import Base
from src.app.dtos.user_detail import UserDetail
from src.app.models.role import Role


class User(Base):
    __tablename__ = "users"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    role_id:  Mapped[int]    = mapped_column(Integer, ForeignKey("roles.id"), nullable=False, index=True)

    # Relationship with Role
    role: Mapped[Role] = relationship(back_populates="users")

    # Relationship with Task
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email}, is_active={self.is_active})>"

    def is_admin(self) -> bool:
        return self.role_id == 1

    def to_user_detail(self) -> UserDetail:
        return UserDetail(
            id=self.id,
            username=self.username,
            email=self.email,
            is_admin=self.is_admin(),
        )