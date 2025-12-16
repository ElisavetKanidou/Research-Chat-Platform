"""
Notifications API Endpoints
app/api/v1/endpoints/notifications.py
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, func, delete
from datetime import datetime
import logging

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.notification import Notification, NotificationType

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's notifications"""

    logger.info(f"📬 Fetching notifications for user {current_user.id}")

    try:
        query = select(Notification).where(
            Notification.user_id == current_user.id
        )

        if unread_only:
            query = query.where(Notification.is_read == False)

        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        notifications = result.scalars().all()

        # Get unread count
        unread_count = await db.execute(
            select(func.count(Notification.id)).where(
                and_(
                    Notification.user_id == current_user.id,
                    Notification.is_read == False
                )
            )
        )
        unread = unread_count.scalar() or 0

        return {
            "notifications": [notif.to_dict() for notif in notifications],
            "unread_count": unread,
            "total": len(notifications)
        }

    except Exception as e:
        logger.error(f"❌ Error fetching notifications: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications"""

    try:
        result = await db.execute(
            select(func.count(Notification.id)).where(
                and_(
                    Notification.user_id == current_user.id,
                    Notification.is_read == False
                )
            )
        )
        count = result.scalar() or 0

        return {"unread_count": count}

    except Exception as e:
        logger.error(f"❌ Error fetching unread count: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a notification as read"""

    try:
        from uuid import UUID

        notification = await db.get(Notification, UUID(notification_id))

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        if str(notification.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        notification.mark_as_read()
        await db.commit()

        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error marking notification as read: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read"""

    try:
        await db.execute(
            update(Notification)
            .where(
                and_(
                    Notification.user_id == current_user.id,
                    Notification.is_read == False
                )
            )
            .values(is_read=True, updated_at=datetime.utcnow())
        )

        await db.commit()

        return {"success": True, "message": "All notifications marked as read"}

    except Exception as e:
        logger.error(f"❌ Error marking all as read: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification"""

    try:
        from uuid import UUID

        notification = await db.get(Notification, UUID(notification_id))

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        if str(notification.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        await db.delete(notification)
        await db.commit()

        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting notification: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear-all")
async def clear_all_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear all notifications for user"""

    try:
        await db.execute(
            delete(Notification).where(
                Notification.user_id == current_user.id
            )
        )

        await db.commit()

        return {"success": True, "message": "All notifications cleared"}

    except Exception as e:
        logger.error(f"❌ Error clearing notifications: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ✅ HELPER FUNCTION - Create notification
async def create_notification(
    db: AsyncSession,
    user_id: str,
    type: NotificationType,
    title: str,
    message: str,
    link: Optional[str] = None
):
    """Helper function to create a notification and send it via WebSocket and email"""

    from uuid import UUID
    from app.services.websocket_service import connection_manager
    from app.services.email_service import email_service

    notification = Notification(
        user_id=UUID(user_id),
        type=type,
        title=title,
        message=message,
        link=link,
        is_read=False
    )

    db.add(notification)
    await db.commit()
    await db.refresh(notification)

    logger.info(f"✅ Created notification for user {user_id}: {title}")

    # ✅ SEND VIA WEBSOCKET
    try:
        await connection_manager.send_notification(
            user_id=user_id,
            notification_type=type.value,
            title=title,
            message=message,
            data={
                "id": str(notification.id),
                "link": link,
                "created_at": notification.created_at.isoformat()
            }
        )
        logger.info(f"📡 Sent notification via WebSocket to user {user_id}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to send WebSocket notification: {e}")
        # Don't fail if WebSocket send fails - notification is still in DB

    # ✅ SEND VIA EMAIL (if user has email notifications enabled)
    try:
        # Fetch user to check email preferences
        user_query = select(User).where(User.id == UUID(user_id))
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user and user.should_send_email_notification(type.value):
            # Map notification types to email types
            notification_type_map = {
                "deadline": "deadline",
                "collaboration": "collaboration",
                "comment": "collaboration",
                "mention": "collaboration",
                "paper_shared": "collaboration"
            }
            email_type = notification_type_map.get(type.value, "general")

            # Send email notification
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9fafb; }}
                    .notification {{ background-color: white; padding: 15px; border-left: 4px solid #3b82f6; margin: 15px 0; }}
                    .button {{ display: inline-block; padding: 12px 24px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{title}</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user.name},</p>
                        <div class="notification">
                            {message}
                        </div>
                        {f'<a href="{link}" class="button">View Details</a>' if link else ''}
                    </div>
                    <div class="footer">
                        <p>You received this email because you have email notifications enabled.</p>
                        <p>Research Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """

            await email_service.send_email(
                to_email=user.email,
                subject=title,
                html_content=html_content,
                text_content=message
            )
            logger.info(f"📧 Sent email notification to {user.email}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to send email notification: {e}")
        # Don't fail if email send fails - notification is still in DB

    return notification