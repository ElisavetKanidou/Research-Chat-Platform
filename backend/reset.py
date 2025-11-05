"""
Reset database - Drop and recreate public schema
"""
import asyncio
from sqlalchemy import text
from app.database.connection import engine


async def reset_database():
    """Reset the database schema"""
    try:
        async with engine.begin() as conn:
            print("🗑️  Dropping public schema...")
            await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))

            print("✅ Creating public schema...")
            await conn.execute(text("CREATE SCHEMA public"))

            print("🔐 Granting permissions...")
            await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))

            print("✨ Database reset complete!")
            print("\nNext steps:")
            print("1. alembic revision --autogenerate -m 'Initial migration'")
            print("2. alembic upgrade head")
            print("3. python scripts/create_admin.py")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("⚠️  DATABASE RESET WARNING")
    print("=" * 60)
    print("This will DELETE ALL TABLES and DATA in the database!")
    print("Database: research_platform")
    print("=" * 60)

    response = input("\nType 'yes' to continue or anything else to cancel: ")

    if response.lower() == 'yes':
        print("\n🔄 Starting database reset...\n")
        asyncio.run(reset_database())
    else:
        print("\n❌ Operation cancelled. Database unchanged.")