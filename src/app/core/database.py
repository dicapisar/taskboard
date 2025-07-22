from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.app.core.config import settings

class Base(DeclarativeBase):
    pass

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "dev",
    future=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session