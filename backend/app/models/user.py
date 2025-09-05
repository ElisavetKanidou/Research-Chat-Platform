"""
User database model
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.models.base import BaseModel


class User(BaseModel):
    """User model for authentication and profile management"""
    __tablename__ = "users"

    # Basic user information
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Profile information
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    affiliation = Column(String(255), nullable=True)
    orcid_id = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Timestamps
    last_login_at = Column(DateTime, nullable=True)
    email_verified_at = Column(DateTime, nullable=True)

    # User preferences stored as JSON
    preferences = Column(JSON, nullable=True, default={
        "theme": "light",
        "language": "en",
        "timezone": "UTC",
        "date_format": "MM/dd/yyyy",
        "default_word_count": 8000,
        "auto_save": True,
        "notifications": {
            "email_notifications": True,
            "deadline_reminders": True,
            "collaboration_updates": True,
            "ai_suggestions": True,
            "weekly_reports": False,
            "push_notifications": True,
            "reminder_frequency": "weekly"
        },
        "privacy": {
            "profile_visibility": "private",
            "share_analytics": False,
            "data_sync_enabled": True,
            "allow_research_sharing": False,
            "tracking_opt_out": False
        },
        "ai_personalization": {
            "lab_level": 3,
            "personal_level": 2,
            "global_level": 1,
            "writing_style": "academic",
            "research_focus": [],
            "suggestions_enabled": True,
            "context_depth": "moderate"
        }
    })

    # Research interests (array of strings)
    research_interests = Column(JSON, nullable=True, default=[])

    # Subscription information
    subscription_plan = Column(String(50), default="free", nullable=False)
    subscription_status = Column(String(50), default="active", nullable=False)
    subscription_start_date = Column(DateTime, default=datetime.utcnow)
    subscription_end_date = Column(DateTime, nullable=True)

    # Relationships
    papers = relationship("Paper", back_populates="owner", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    collaborations = relationship("PaperCollaborator", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"

    def get_full_name(self) -> str:
        """Get user's full name"""
        return self.name

    def is_premium_user(self) -> bool:
        """Check if user has premium subscription"""
        return self.subscription_plan in ["pro", "academic", "enterprise"]

    def can_create_papers(self) -> bool:
        """Check if user can create papers based on subscription"""
        if not self.is_active:
            return False

        if self.subscription_plan == "free":
            # Free users have paper limits
            return len(self.papers) < 5

        return True

    def get_research_focus(self) -> list:
        """Get user's research focus from preferences"""
        if self.preferences and "ai_personalization" in self.preferences:
            return self.preferences["ai_personalization"].get("research_focus", [])
        return self.research_interests or []

    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login_at = datetime.utcnow()

    def verify_email(self) -> None:
        """Mark email as verified"""
        self.is_verified = True
        self.email_verified_at = datetime.utcnow()

    def update_preferences(self, preferences: dict) -> None:
        """Update user preferences"""
        if self.preferences is None:
            self.preferences = {}

        # Deep merge preferences
        def merge_dict(target: dict, source: dict) -> dict:
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value
            return target

        self.preferences = merge_dict(self.preferences.copy(), preferences)
        self.updated_at = datetime.utcnow()

    def to_public_dict(self) -> dict:
        """Convert to dictionary with public information only"""
        return {
            "id": str(self.id),
            "name": self.name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "affiliation": self.affiliation,
            "location": self.location,
            "research_interests": self.research_interests,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }