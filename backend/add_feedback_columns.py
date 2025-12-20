"""
Add user_feedback and feedback_timestamp columns to chat_messages table
"""
import asyncio
import sys
from sqlalchemy import text
from app.database.connection import engine


async def add_feedback_columns():
    """Add feedback columns to chat_messages table"""
    print("🔧 Adding feedback columns to chat_messages table...")

    async with engine.connect() as conn:
        try:
            # Check if columns exist
            check_query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'chat_messages'
                AND column_name IN ('user_feedback', 'feedback_timestamp');
            """)
            result = await conn.execute(check_query)
            existing_columns = [row[0] for row in result.fetchall()]

            print(f"📊 Existing feedback columns: {existing_columns}")

            # Add user_feedback column if not exists
            if 'user_feedback' not in existing_columns:
                print("➕ Adding user_feedback column...")
                await conn.execute(text("""
                    ALTER TABLE chat_messages
                    ADD COLUMN user_feedback BOOLEAN DEFAULT NULL;
                """))
                print("✅ user_feedback column added!")
            else:
                print("⏭️  user_feedback column already exists")

            # Add feedback_timestamp column if not exists
            if 'feedback_timestamp' not in existing_columns:
                print("➕ Adding feedback_timestamp column...")
                await conn.execute(text("""
                    ALTER TABLE chat_messages
                    ADD COLUMN feedback_timestamp TIMESTAMP DEFAULT NULL;
                """))
                print("✅ feedback_timestamp column added!")
            else:
                print("⏭️  feedback_timestamp column already exists")

            # Commit the changes
            await conn.commit()

            print("🎉 Migration completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            await conn.rollback()
            return False


async def main():
    """Main function"""
    try:
        success = await add_feedback_columns()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
