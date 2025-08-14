from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.app.core.database import Base

class Role(Base):
    __tablename__ = "roles"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    #Relationship with User
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"<Rol(id={self.id}, name={self.name})>"