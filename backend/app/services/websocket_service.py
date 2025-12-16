"""
WebSocket service for real-time notifications and presence tracking
"""
import logging
import json
from typing import Dict, Set, List
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""

    def __init__(self):
        # Store active connections: {user_id: Set[WebSocket]}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        logger.info("✅ ConnectionManager initialized")

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        logger.info(f"🔗 User {user_id} connected via WebSocket. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Remove user entry if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

            logger.info(f"❌ User {user_id} disconnected. Remaining connections: {len(self.active_connections.get(user_id, set()))}")

    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to a specific user's all connections"""
        if user_id not in self.active_connections:
            logger.warning(f"⚠️ User {user_id} has no active connections")
            return

        disconnected = set()

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
                logger.debug(f"📤 Sent message to user {user_id}")
            except Exception as e:
                logger.error(f"❌ Failed to send message to user {user_id}: {str(e)}")
                disconnected.add(connection)

        # Clean up disconnected websockets
        for connection in disconnected:
            self.disconnect(connection, user_id)

    async def broadcast_to_users(self, message: dict, user_ids: list):
        """Broadcast message to multiple users"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)

    async def send_notification(self, user_id: str, notification_type: str, title: str, message: str, data: dict = None):
        """Send a formatted notification to a user"""
        notification = {
            "type": "notification",
            "notification_type": notification_type,  # success, error, warning, info
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }

        await self.send_personal_message(notification, user_id)

    async def send_paper_update(self, user_id: str, paper_id: str, update_type: str, data: dict = None):
        """Send paper update notification"""
        message = {
            "type": "paper_update",
            "paper_id": paper_id,
            "update_type": update_type,  # created, updated, deleted, section_changed
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }

        await self.send_personal_message(message, user_id)

    async def send_collaboration_update(self, user_ids: list, paper_id: str, author_name: str, action: str):
        """Send collaboration update to all collaborators"""
        message = {
            "type": "collaboration",
            "paper_id": paper_id,
            "author_name": author_name,
            "action": action,  # joined, left, edited, commented
            "timestamp": datetime.now().isoformat()
        }

        await self.broadcast_to_users(message, user_ids)

    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of active connections for a user"""
        return len(self.active_connections.get(user_id, set()))

    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())

    def is_user_connected(self, user_id: str) -> bool:
        """Check if user has any active WebSocket connections"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0

    async def broadcast_presence_update(self, user_id: str, status: str, user_ids: List[str]):
        """
        Broadcast user presence update to specific users (e.g., collaborators)

        Args:
            user_id: User whose presence changed
            status: 'online', 'away', or 'offline'
            user_ids: List of user IDs to notify
        """
        message = {
            "type": "presence",
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }

        await self.broadcast_to_users(message, user_ids)
        logger.debug(f"📡 Broadcasted presence update for user {user_id}: {status}")


# Global instance
connection_manager = ConnectionManager()
