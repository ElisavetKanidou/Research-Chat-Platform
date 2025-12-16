"""
Quick script to add deadline column to papers table
"""
import asyncio
from sqlalchemy import text
from app.database.session import async_session_maker


async def add_deadline_column():
    """Add deadline column to papers table"""
    async with async_session_maker() as session:
        try:
            # Add deadline column if it doesn't exist
            await session.execute(text(
                "ALTER TABLE papers ADD COLUMN IF NOT EXISTS deadline TIMESTAMP"
            ))
            await session.commit()
            print("✅ Successfully added deadline column to papers table!")
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(add_deadline_column())
