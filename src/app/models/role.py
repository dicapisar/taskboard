# Import required types from SQLAlchemy
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import the base class for ORM models
from src.app.core.database import Base

# ---------------------------- Role ORM Model ----------------------------

class Role(Base):
    """
    This class represents a 'Role' in the database.
    Each role can be assigned to multiple users.
    """

    # Name of the table in the database
    __tablename__ = "roles"

    # ---------------------------- Table Columns ----------------------------

    # Unique identifier for the role (Primary Key)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Name of the role (e.g., 'admin', 'user')
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # Optional description of the role
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    # ---------------------------- Relationships ----------------------------

    # One-to-many relationship: A role can be assigned to many users
    users: Mapped[list["User"]] = relationship(back_populates="role")

    # ---------------------------- Representation ----------------------------

    def __repr__(self):
        """
        Return a string representation of the Role instance.
        Useful for debugging or logging.
        """
        return f"<Rol(id={self.id}, name={self.name})>"