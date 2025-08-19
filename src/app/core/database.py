# Import type hints for asynchronous generators
from typing import Any, AsyncGenerator

# Import SQLAlchemy components for async database operations
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase

# Import application configuration for database URL and environment
from src.app.core.config import settings

# ---------------------------- Base Class for ORM Models ----------------------------

class Base(DeclarativeBase):
    """
    This is the base class for all ORM models in the project.
    All database models should inherit from this class.
    """
    pass

# ---------------------------- Database Engine Initialization ----------------------------

# Create an asynchronous database engine using the URL from settings
# The echo option prints SQL queries to the console in development mode
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "dev",
    future=True,  # Use SQLAlchemy 2.0-style behavior
)

# ---------------------------- Async Session Factory ----------------------------

# Create a session factory that will generate AsyncSession instances
SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,            # Prevent automatic flushing to the database
    expire_on_commit=False,     # Keep data in session after commit
    class_=AsyncSession         # Use async-compatible sessions
)

# ---------------------------- Dependency for DB Session ----------------------------

async def get_db() -> AsyncGenerator[AsyncSession | Any, Any]:
    """
    Dependency to provide a database session.
    This session is used inside route handlers or services.
    It ensures the session is opened and closed properly.
    """
    async with SessionLocal() as session:
        yield session