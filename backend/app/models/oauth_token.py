"""
OAuth Token model for storing third-party integration tokens
backend/app/models/oauth_token.py
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.models.base import BaseModel


class OAuthToken(BaseModel):
    """Model for storing OAuth tokens for third-party integrations"""
    __tablename__ = "oauth_tokens"

    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Integration service (google_drive, dropbox, mendeley, etc.)
    service = Column(String(50), nullable=False, index=True)

    # OAuth tokens
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="Bearer")

    # Token expiration
    expires_at = Column(DateTime, nullable=True)

    # Additional metadata (e.g., scope, user info from provider)
    token_metadata = Column(Text, nullable=True)

    # Relationship to user
    user = relationship("User", backref="oauth_tokens")

    def __repr__(self) -> str:
        return f"<OAuthToken(user_id={self.user_id}, service='{self.service}')>"

    def is_expired(self) -> bool:
        """Check if the token is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "service": self.service,
            "token_type": self.token_type,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_expired": self.is_expired(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
