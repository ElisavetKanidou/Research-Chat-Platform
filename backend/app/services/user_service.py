"""
User service - COMPLETE WITH PREFERENCES SAVING
backend/app/services/user_service.py
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
from app.models.user import User
from app.schemas.user import UserUpdate, UserPreferencesUpdate
from datetime import datetime


class UserService:
    """Service for user-related operations"""

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def update_user(
            self,
            db: AsyncSession,
            user_id: str,
            updates: UserUpdate
    ) -> User:
        """Update user profile"""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        # Update basic fields
        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != 'preferences':  # Handle preferences separately
                setattr(user, field, value)

        user.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(user)

        return user

    async def update_preferences(
            self,
            db: AsyncSession,
            user_id: str,
            preferences: Dict[str, Any]
    ) -> User:
        """
        Update user preferences including notifications, privacy, integrations

        Args:
            db: Database session
            user_id: User ID
            preferences: Dictionary with ALL preferences
                {
                    "theme": "light",
                    "language": "English",
                    "timezone": "UTC-5 (EST)",
                    "dateFormat": "MM/DD/YYYY",
                    "defaultWordCount": 8000,
                    "notifications": {
                        "emailNotifications": true,
                        "deadlineReminders": true,
                        "collaborationUpdates": true,
                        "aiSuggestions": false,
                        "weeklyReports": true
                    },
                    "privacy": {
                        "profileVisibility": "institution",
                        "shareAnalytics": true,
                        "dataSyncEnabled": true
                    },
                    "integrations": {
                        "googleDrive": false,
                        "dropbox": false,
                        "zotero": false,
                        "mendeley": false,
                        "latex": false
                    }
                }
        """
        print(f"\n{'=' * 80}")
        print(f"💾 [UserService.update_preferences] Updating preferences for user {user_id}")
        print(f"{'=' * 80}")
        print(f"📥 Incoming preferences: {preferences}")

        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        # Initialize preferences if None
        if user.preferences is None:
            user.preferences = {}
            print("📋 Initialized empty preferences")

        # Deep merge all preferences
        print(f"\n🔧 BEFORE update:")
        print(f"   Current preferences: {user.preferences}")

        # Update each field
        for key, value in preferences.items():
            if value is not None:
                user.preferences[key] = value
                print(f"   ✅ Set {key} = {value}")

        # ✅ CRITICAL: Tell SQLAlchemy the JSON column changed!
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "preferences")
        print(f"🚩 Called flag_modified on preferences")

        user.updated_at = datetime.utcnow()

        print(f"\n🔧 AFTER update:")
        print(f"   New preferences: {user.preferences}")

        await db.commit()
        print("💾 Committed to database")

        await db.refresh(user)
        print(f"🔄 Refreshed user")
        print(f"   Final preferences: {user.preferences}")
        print(f"{'=' * 80}\n")

        return user

    async def create_user(
            self,
            db: AsyncSession,
            email: str,
            name: str,
            hashed_password: str
    ) -> User:
        """Create a new user"""
        user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            preferences={}  # Initialize with empty dict
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user


user_service = UserService()