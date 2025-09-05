"""
Database session management and dependency injection
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import AsyncGenerator
import logging

from app.database.connection import engine

logger = logging.getLogger(__name__)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides database session.
    Automatically handles session creation, cleanup, and rollback on errors.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


class DatabaseManager:
    """Database management utilities"""

    @staticmethod
    async def create_tables():
        """Create all database tables"""
        from app.models.base import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")

    @staticmethod
    async def drop_tables():
        """Drop all database tables (use with caution!)"""
        from app.models.base import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped")

    @staticmethod
    async def reset_database():
        """Reset database (drop and recreate tables)"""
        await DatabaseManager.drop_tables()
        await DatabaseManager.create_tables()
        logger.info("Database reset completed")


# Context manager for manual session handling
class DatabaseSession:
    """Context manager for manual database session handling"""

    def __init__(self):
        self.session: AsyncSession = None

    async def __aenter__(self) -> AsyncSession:
        self.session = async_session_maker()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
            logger.error(f"Database transaction rolled back due to error: {exc_val}")
        else:
            await self.session.commit()

        await self.session.close()


# Utility functions
async def execute_in_transaction(func, *args, **kwargs):
    """Execute function in a database transaction"""
    async with DatabaseSession() as session:
        kwargs['db'] = session
        return await func(*args, **kwargs)