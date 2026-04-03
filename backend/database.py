"""
AEGISCORE — Async Database Configuration
SQLAlchemy 2.x async engine with asyncpg driver.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


async def get_db():
    """
    FastAPI dependency that yields an async database session.
    Automatically closes session on exit.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Create all database tables.
    Called on application startup if tables don't exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
