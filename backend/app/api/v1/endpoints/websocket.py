"""
WebSocket endpoints for real-time communication
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from app.services.websocket_service import connection_manager
from app.api.v1.endpoints.auth import get_current_user_ws
from app.database.session import get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = None
):
    """
    WebSocket endpoint for real-time notifications

    Usage:
    ws://localhost:8000/api/v1/ws?token=YOUR_JWT_TOKEN
    """

    # Authenticate user from query parameter
    user = None
    try:
        # Get token from query params
        if not token:
            logger.warning("⚠️ WebSocket connection attempt without token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Verify JWT token and get user
        async for db in get_db():
            user = await get_current_user_ws(token, db)
            break

        if not user:
            logger.warning("⚠️ WebSocket authentication failed - invalid user")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user_id = str(user.id)
        logger.info(f"🔌 WebSocket connection request from user: {user.email} (ID: {user_id})")

    except Exception as e:
        logger.error(f"❌ Authentication failed: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Accept connection
    await connection_manager.connect(websocket, user_id)

    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "message": "WebSocket connection established",
        "user_id": user_id
    })

    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Handle different message types
            message_type = data.get("type")

            if message_type == "ping":
                # Respond to ping with pong
                await websocket.send_json({"type": "pong"})

            elif message_type == "subscribe":
                # Subscribe to specific channels (paper updates, collaborations, etc.)
                channel = data.get("channel")
                logger.info(f"📡 User {user_id} subscribed to channel: {channel}")
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": channel
                })

            else:
                logger.warning(f"⚠️ Unknown message type: {message_type}")

    except WebSocketDisconnect:
        logger.info(f"🔌 User {user_id} disconnected normally")
        connection_manager.disconnect(websocket, user_id)

    except Exception as e:
        logger.error(f"❌ WebSocket error for user {user_id}: {str(e)}")
        connection_manager.disconnect(websocket, user_id)


@router.get("/ws/status")
async def websocket_status(current_user: User = Depends(get_current_user)):
    """Get WebSocket service status"""
    return {
        "status": "active",
        "total_connections": connection_manager.get_total_connections(),
        "user_connections": connection_manager.get_user_connection_count(str(current_user.id))
    }
