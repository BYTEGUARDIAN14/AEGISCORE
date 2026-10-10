"""
AEGISCORE — Async Database Configuration
SQLAlchemy 2.x async engine with asyncpg driver.
"""

import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings


db_url = settings.DATABASE_URL
if db_url.startswith("sqlite"):
    db_url = db_url.replace("\\", "/")
    prefix = "sqlite+aiosqlite:///"
    if db_url.startswith(prefix):
        raw_path = db_url[len(prefix):]
        # If relative path, resolve to backend dir where aegiscore.db lives
        if not os.path.isabs(raw_path) and not (len(raw_path) > 1 and raw_path[1] == ":"):
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            candidate1 = os.path.join(backend_dir, os.path.basename(raw_path)).replace("\\", "/")
            candidate2 = os.path.join(os.path.dirname(backend_dir), raw_path).replace("\\", "/")
            if os.path.exists(candidate1):
                db_url = f"{prefix}{candidate1}"
            elif os.path.exists(candidate2):
                db_url = f"{prefix}{candidate2}"
            else:
                db_url = f"{prefix}{candidate1}"

is_sqlite = db_url.startswith("sqlite")
engine_kwargs = {"echo": settings.DEBUG}
if not is_sqlite:
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
    })

engine = create_async_engine(
    db_url,
    **engine_kwargs,
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
