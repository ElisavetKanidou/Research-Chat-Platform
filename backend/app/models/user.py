"""
User database model - COMPLETE VERSION WITH PERSONALIZATION
app/models/user.py
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import json

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

    # User preferences stored as JSON with proper default
    preferences = Column(JSON, nullable=True, default=lambda: {
        "theme": "light",
        "language": "en",
        "timezone": "UTC",
        "dateFormat": "MM/dd/yyyy",
        "defaultWordCount": 8000,
        "autoSave": True,
        "notifications": {
            "emailNotifications": True,
            "deadlineReminders": True,
            "collaborationUpdates": True,
            "aiSuggestions": True,
            "weeklyReports": False,
            "pushNotifications": True,
            "reminderFrequency": "weekly"
        },
        "privacy": {
            "profileVisibility": "private",
            "shareAnalytics": False,
            "dataSyncEnabled": True,
            "allowResearchSharing": False,
            "trackingOptOut": False
        }
    })

    # Research interests (array of strings)
    research_interests = Column(JSON, nullable=True, default=list)

    # Subscription information
    subscription_plan = Column(String(50), default="free", nullable=False)
    subscription_status = Column(String(50), default="active", nullable=False)
    subscription_start_date = Column(DateTime, default=datetime.utcnow)
    subscription_end_date = Column(DateTime, nullable=True)

    # Relationships
    papers = relationship(
        "Paper",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    chat_messages = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    collaborations = relationship(
        "PaperCollaborator",
        back_populates="user",
        foreign_keys="PaperCollaborator.user_id"
    )

    # CRITICAL: Personalization settings relationship
    personalization_settings = relationship(
        "PersonalizationSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    analytics = relationship(
        "UserAnalytics",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(Notification.created_at)"
    )

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
            # Free users have paper limits (e.g., 5 papers)
            return len(self.papers) < 5

        return True

    def get_research_focus(self) -> list:
        """Get user's research focus from personalization settings or preferences"""
        # First try personalization_settings table
        if self.personalization_settings and self.personalization_settings.research_focus:
            return self.personalization_settings.research_focus

        # Fallback to preferences JSON (legacy)
        if self.preferences and "aiPersonalization" in self.preferences:
            return self.preferences["aiPersonalization"].get("researchFocus", [])

        # Final fallback to research_interests
        return self.research_interests or []

    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login_at = datetime.utcnow()

    def verify_email(self) -> None:
        """Mark email as verified"""
        self.is_verified = True
        self.email_verified_at = datetime.utcnow()

    def update_preferences(self, preferences: dict) -> None:
        """Update user preferences with deep merge

        Args:
            preferences: Dictionary of preferences to merge

        Note:
            This creates a NEW dict to trigger SQLAlchemy change detection
        """
        if self.preferences is None:
            self.preferences = {}

        # Deep merge preferences
        def merge_dict(target: dict, source: dict) -> dict:
            """Recursively merge source into target"""
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value
            return target

        # CRITICAL: Create a NEW dict to trigger SQLAlchemy change detection
        updated_prefs = merge_dict(self.preferences.copy() if self.preferences else {}, preferences)
        self.preferences = updated_prefs
        self.updated_at = datetime.utcnow()

    def get_ai_personalization(self) -> dict:
        """Get AI personalization settings from personalization_settings table"""
        if self.personalization_settings:
            return {
                "labLevel": self.personalization_settings.lab_level,
                "personalLevel": self.personalization_settings.personal_level,
                "globalLevel": self.personalization_settings.global_level,
                "writingStyle": self.personalization_settings.writing_style,
                "contextDepth": self.personalization_settings.context_depth,
                "researchFocus": self.personalization_settings.research_focus or [],
                "suggestionsEnabled": self.personalization_settings.suggestions_enabled
            }

        # Fallback to preferences JSON if no personalization_settings
        if self.preferences and "aiPersonalization" in self.preferences:
            return self.preferences["aiPersonalization"]

        # Default values
        return {
            "labLevel": 7,
            "personalLevel": 8,
            "globalLevel": 5,
            "writingStyle": "academic",
            "contextDepth": "moderate",
            "researchFocus": [],
            "suggestionsEnabled": True
        }

    def to_dict(self) -> dict:
        """Convert to dictionary with full information"""
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "affiliation": self.affiliation,
            "orcid_id": self.orcid_id,
            "website": self.website,
            "location": self.location,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_superuser": self.is_superuser,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "email_verified_at": self.email_verified_at.isoformat() if self.email_verified_at else None,
            "preferences": self.preferences,
            "research_interests": self.research_interests,
            "subscription_plan": self.subscription_plan,
            "subscription_status": self.subscription_status,
            "subscription_start_date": self.subscription_start_date.isoformat() if self.subscription_start_date else None,
            "subscription_end_date": self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "ai_personalization": self.get_ai_personalization()
        }

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

    def deactivate(self) -> None:
        """Deactivate user account (soft delete)"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate user account"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def upgrade_subscription(self, plan: str) -> None:
        """Upgrade user subscription

        Args:
            plan: One of 'free', 'pro', 'academic', 'enterprise'
        """
        valid_plans = ["free", "pro", "academic", "enterprise"]
        if plan not in valid_plans:
            raise ValueError(f"Invalid plan. Must be one of: {valid_plans}")

        self.subscription_plan = plan
        self.subscription_status = "active"
        self.updated_at = datetime.utcnow()

    def cancel_subscription(self) -> None:
        """Cancel user subscription"""
        self.subscription_status = "cancelled"
        self.subscription_end_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @property
    def is_subscription_active(self) -> bool:
        """Check if subscription is currently active"""
        if self.subscription_status != "active":
            return False

        if self.subscription_end_date and self.subscription_end_date < datetime.utcnow():
            return False

        return True

    @property
    def paper_count(self) -> int:
        """Get count of user's papers"""
        return len(self.papers) if self.papers else 0

    @property
    def has_verified_email(self) -> bool:
        """Check if user has verified their email"""
        return self.is_verified and self.email_verified_at is not None

    def get_notification_preferences(self) -> dict:
        """Get notification preferences from preferences JSON"""
        if self.preferences and "notifications" in self.preferences:
            return self.preferences["notifications"]

        # Default notification preferences
        return {
            "emailNotifications": True,
            "deadlineReminders": True,
            "collaborationUpdates": True,
            "aiSuggestions": False,
            "weeklyReports": True,
            "pushNotifications": True,
            "reminderFrequency": "weekly"
        }

    def get_privacy_settings(self) -> dict:
        """Get privacy settings from preferences JSON"""
        if self.preferences and "privacy" in self.preferences:
            return self.preferences["privacy"]

        # Default privacy settings
        return {
            "profileVisibility": "private",
            "shareAnalytics": False,
            "dataSyncEnabled": True,
            "allowResearchSharing": False,
            "trackingOptOut": False
        }

    def should_send_email_notification(self, notification_type: str) -> bool:
        """Check if user should receive email notification for given type

        Args:
            notification_type: Type of notification (e.g., 'deadline', 'collaboration')

        Returns:
            True if notification should be sent, False otherwise
        """
        if not self.is_active or not self.has_verified_email:
            return False

        prefs = self.get_notification_preferences()

        if not prefs.get("emailNotifications", True):
            return False

        # Check specific notification type
        type_map = {
            "deadline": "deadlineReminders",
            "collaboration": "collaborationUpdates",
            "ai_suggestion": "aiSuggestions",
            "weekly_report": "weeklyReports"
        }

        pref_key = type_map.get(notification_type)
        if pref_key:
            return prefs.get(pref_key, False)

        return True

    def is_profile_visible_to(self, viewer_affiliation: str = None) -> bool:
        """Check if profile is visible to viewer

        Args:
            viewer_affiliation: Affiliation of the viewer (optional)

        Returns:
            True if profile should be visible, False otherwise
        """
        privacy = self.get_privacy_settings()
        visibility = privacy.get("profileVisibility", "private")

        if visibility == "public":
            return True

        if visibility == "institution":
            # Check if viewer has same affiliation
            if viewer_affiliation and self.affiliation:
                return viewer_affiliation.lower() == self.affiliation.lower()
            return False

        # Private - only visible to self
        return False