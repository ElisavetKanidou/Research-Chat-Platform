"""
Notification Model
app/models/notification.py
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import BaseModel


class NotificationType(str, enum.Enum):
    COLLABORATION_INVITE = "collaboration_invite"
    PAPER_SHARED = "paper_shared"
    COMMENT_ADDED = "comment_added"
    PAPER_UPDATED = "paper_updated"
    COLLABORATOR_ADDED = "collaborator_added"


class Notification(BaseModel):
    """Notification model for user notifications"""
    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)  # Optional link to relevant page
    is_read = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "link": self.link,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }