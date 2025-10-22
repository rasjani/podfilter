"""Database configuration and models."""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from litestar.di import Provide


class Base(DeclarativeBase):
    """Base class for all database models."""


# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./podfilter.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncSession:
    """Get database session."""
    async with async_session_maker() as session:
        yield session
