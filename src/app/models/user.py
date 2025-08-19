# Import required SQLAlchemy modules and types
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import base class for ORM models and data transfer object for user detail
from src.app.core.database import Base
from src.app.dtos.user_detail import UserDetail
from src.app.models.role import Role

# ---------------------------- User ORM Model ----------------------------

class User(Base):
    """
    This class represents a user in the database.
    It includes attributes such as username, email, password, and role.
    """

    __tablename__ = "users"  # Name of the table in the database

    # ---------------------------- Table Columns ----------------------------

    # Unique identifier for the user (Primary Key)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Unique username chosen by the user
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # Unique email address of the user
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)

    # Encrypted password for authentication
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Indicates whether the user account is active
    is_active: Mapped[bool] = mapped_column(default=True)

    # Foreign key to the role assigned to the user
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False, index=True)

    # ---------------------------- Relationships ----------------------------

    # A user is linked to a role (Many users can have the same role)
    role: Mapped[Role] = relationship(back_populates="users")

    # A user can have multiple tasks
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="owner",
        cascade="all, delete-orphan",     # Delete tasks if user is deleted
        passive_deletes=True              # Enable database-level cascade deletes
    )

    # ---------------------------- Methods ----------------------------

    def __repr__(self) -> str:
        """
        Return a readable string that describes the user.
        Useful for logging or debugging.
        """
        return f"<User(id={self.id}, username={self.username}, email={self.email}, is_active={self.is_active})>"

    def is_admin(self) -> bool:
        """
        Check if the user has administrative privileges.
        For simplicity, this example assumes role_id == 1 is the admin role.
        """
        return self.role_id == 1

    def to_user_detail(self) -> UserDetail:
        """
        Convert the user instance to a UserDetail data object (DTO).
        This is useful for caching or passing lightweight user data.
        """
        return UserDetail(
            id=self.id,
            username=self.username,
            email=self.email,
            is_admin=self.is_admin(),
        )