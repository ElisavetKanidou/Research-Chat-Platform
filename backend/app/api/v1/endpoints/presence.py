"""
Presence API endpoints for user online status
"""
from fastapi import APIRouter, Depends, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from app.database.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.presence_service import presence_service

router = APIRouter()


@router.post("/heartbeat")
async def heartbeat(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's last_active timestamp (called periodically by frontend)
    Updates both cache and database
    """
    presence_service.mark_active(str(current_user.id))

    # Also update database immediately
    await presence_service.batch_update_database(db)

    return {
        "status": "ok",
        "user_id": str(current_user.id)
    }


@router.get("/status/{user_id}")
async def get_user_status(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get presence status for a specific user"""
    status_data = presence_service.get_user_status(user_id)

    return {
        "user_id": user_id,
        "status": status_data['status'],
        "last_seen": status_data['last_seen'].isoformat() if status_data['last_seen'] else None
    }


@router.post("/bulk-status")
async def get_bulk_status(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get presence status for multiple users at once
    Used by CollaboratorsList, Dashboard, etc.

    Accepts: ["user_id_1", "user_id_2", ...] as JSON array in request body
    """
    # Parse the raw JSON array from request body
    user_ids = await request.json()

    # Handle empty array
    if not user_ids:
        return {}

    statuses = await presence_service.get_online_users(db, user_ids)

    result = {}
    for user_id, status_data in statuses.items():
        result[user_id] = {
            "status": status_data['status'],
            "last_seen": status_data['last_seen'].isoformat() if status_data['last_seen'] else None
        }

    return result


@router.get("/online")
async def get_online_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all currently online users"""
    online_users = await presence_service.get_online_users(db)

    return {
        "count": len(online_users),
        "users": {
            user_id: {
                "status": data['status'],
                "last_seen": data['last_seen'].isoformat() if data['last_seen'] else None
            }
            for user_id, data in online_users.items()
        }
    }


@router.get("/stats")
async def get_presence_stats(
    current_user: User = Depends(get_current_user)
):
    """Get presence statistics (admin/monitoring)"""
    return {
        "online_count": presence_service.get_online_count(),
        "total_active_users": len(presence_service.active_users)
    }
