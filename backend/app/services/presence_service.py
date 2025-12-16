"""
Presence tracking service for real-time online status
Efficient implementation with caching to avoid performance impact
"""
import logging
from typing import Dict, Set, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.user import User

logger = logging.getLogger(__name__)


class PresenceService:
    """
    Manages user presence tracking with efficient caching

    Features:
    - Tracks online/away/offline status
    - Batches database updates (every 30 seconds)
    - Caches presence data to minimize DB queries
    - Emits presence updates via WebSocket
    """

    def __init__(self):
        # Track active users: {user_id: last_activity_timestamp}
        self.active_users: Dict[str, datetime] = {}

        # Cache user presence data: {user_id: {'status': 'online', 'last_seen': datetime}}
        self.presence_cache: Dict[str, dict] = {}

        # Track users needing DB update
        self.pending_updates: Set[str] = set()

        # Last batch update timestamp
        self.last_batch_update = datetime.utcnow()

        logger.info("✅ PresenceService initialized")

    def mark_active(self, user_id: str) -> None:
        """
        Mark user as active (called on WebSocket activity)

        This is called frequently but doesn't hit the database immediately
        Updates are batched for performance
        """
        now = datetime.utcnow()
        self.active_users[user_id] = now
        self.pending_updates.add(user_id)

        # Update cache
        self.presence_cache[user_id] = {
            'status': 'online',
            'last_seen': now
        }

    def mark_inactive(self, user_id: str) -> None:
        """Remove user from active tracking (on disconnect)"""
        self.active_users.pop(user_id, None)

        # Update cache to away/offline based on last seen
        if user_id in self.presence_cache:
            self.presence_cache[user_id]['status'] = 'offline'

    async def batch_update_database(self, db: AsyncSession) -> None:
        """
        Batch update user last_active in database
        Called periodically (every 30-60 seconds) to minimize DB load
        """
        if not self.pending_updates:
            return

        try:
            # Get users to update
            user_ids_to_update = list(self.pending_updates)
            self.pending_updates.clear()

            # Batch update in database
            for user_id in user_ids_to_update:
                if user_id in self.active_users:
                    await db.execute(
                        update(User)
                        .where(User.id == user_id)
                        .values(last_active_at=self.active_users[user_id])
                    )

            await db.commit()
            self.last_batch_update = datetime.utcnow()

            logger.debug(f"✅ Batch updated {len(user_ids_to_update)} user presence records")

        except Exception as e:
            logger.error(f"❌ Failed to batch update presence: {e}")
            await db.rollback()

    def get_user_status(self, user_id: str) -> dict:
        """
        Get user status from cache (fast, no DB query)

        Returns:
            {'status': 'online'|'away'|'offline', 'last_seen': datetime}
        """
        if user_id in self.presence_cache:
            cached = self.presence_cache[user_id]

            # Determine which timestamp to use for status calculation
            if user_id in self.active_users:
                # User is actively sending heartbeats - use real-time timestamp
                last_active = self.active_users[user_id]
            else:
                # User not currently active - use cached last_seen from DB
                last_active = cached.get('last_seen')

            # Update status based on last_active timestamp
            if last_active:
                delta = (datetime.utcnow() - last_active).total_seconds()
                if delta < 300:  # 5 minutes - online
                    cached['status'] = 'online'
                elif delta < 1800:  # 30 minutes - away
                    cached['status'] = 'away'
                else:  # > 30 minutes - offline
                    cached['status'] = 'offline'
            else:
                # No timestamp available, mark as offline
                cached['status'] = 'offline'

            return cached

        # Not in cache, return offline
        return {
            'status': 'offline',
            'last_seen': None
        }

    async def get_online_users(self, db: AsyncSession, user_ids: List[str] = None) -> Dict[str, dict]:
        """
        Get presence status for multiple users

        Args:
            user_ids: List of user IDs to check (if None, returns all online users)

        Returns:
            {user_id: {'status': 'online'|'away'|'offline', 'last_seen': datetime}}
        """
        result = {}

        # If specific users requested, check cache first
        if user_ids:
            for user_id in user_ids:
                result[user_id] = self.get_user_status(user_id)
            return result

        # Otherwise return all online/away users
        now = datetime.utcnow()
        for user_id, last_active in self.active_users.items():
            delta = (now - last_active).total_seconds()

            if delta < 300:  # 5 minutes
                status = 'online'
            elif delta < 1800:  # 30 minutes
                status = 'away'
            else:
                continue  # Skip offline users

            result[user_id] = {
                'status': status,
                'last_seen': last_active
            }

        return result

    async def load_recent_activity(self, db: AsyncSession, minutes: int = 30) -> None:
        """
        Load recent user activity from database on startup
        This populates the cache with users who were recently active

        NOTE: Only populates presence_cache, NOT active_users
        active_users should only contain users who are currently sending heartbeats
        """
        try:
            threshold = datetime.utcnow() - timedelta(minutes=minutes)

            result = await db.execute(
                select(User.id, User.last_active_at)
                .where(User.last_active_at >= threshold)
            )

            users = result.all()
            now = datetime.utcnow()

            for user_id, last_active_at in users:
                if last_active_at:
                    # Calculate status based on last_active_at
                    delta = (now - last_active_at).total_seconds()

                    if delta < 300:  # 5 minutes - consider online
                        status = 'online'
                    elif delta < 1800:  # 30 minutes - consider away
                        status = 'away'
                    else:
                        status = 'offline'

                    # ONLY populate cache, NOT active_users
                    # active_users is populated only when user actually sends heartbeat
                    self.presence_cache[str(user_id)] = {
                        'status': status,
                        'last_seen': last_active_at
                    }

            logger.info(f"✅ Loaded {len(users)} recently active users into presence cache")

        except Exception as e:
            logger.error(f"❌ Failed to load recent activity: {e}")

    def get_online_count(self) -> int:
        """Get count of currently online users (fast)"""
        now = datetime.utcnow()
        return sum(
            1 for last_active in self.active_users.values()
            if (now - last_active).total_seconds() < 300
        )


# Global instance
presence_service = PresenceService()
