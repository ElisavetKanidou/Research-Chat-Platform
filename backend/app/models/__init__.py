"""
Database models initialization - FIXED VERSION
Remove duplicate PersonalizationSettings import
"""
from app.models.base import BaseModel

# User model (base for relationships)
from app.models.user import User

# ✅ Import PersonalizationSettings ONCE from its dedicated file
from app.models.personalization_settings import PersonalizationSettings

# Paper models
from app.models.paper import (
    Paper,
    PaperSection,
    PaperCollaborator,
    PaperStatus,
    SectionStatus
)

# Chat models (PersonalizationSettings is imported above, not here)
from app.models.chat import (
    ChatMessage,
    ChatAttachment,
    MessageRole,
    AttachmentType,
    ChatSession,
    AIInteraction
)

# Collaboration models
from app.models.collaboration import (
    CollaborationInvite,
    PaperVersion,
    CollaborationSession,
    CollaborationRole,
    InvitationStatus
)

# Comment models
from app.models.comment import PaperComment

# Analytics models
from app.models.analytics import (
    UserAnalytics,
    PaperAnalytics,
    ActivityLog
)

# Notification models
from app.models.notification import Notification, NotificationType

# OAuth token models
from app.models.oauth_token import OAuthToken

# Reference papers for AI personalization
from app.models.reference_paper import ReferencePaper, PaperType

__all__ = [
    # Base
    "BaseModel",

    # User
    "User",

    # Personalization
    "PersonalizationSettings",  # ✅ Only imported ONCE

    # Paper
    "Paper",
    "PaperSection",
    "PaperCollaborator",
    "PaperStatus",
    "SectionStatus",

    # Chat
    "ChatMessage",
    "ChatAttachment",
    "MessageRole",
    "AttachmentType",
    "ChatSession",
    "AIInteraction",

    # Collaboration
    "CollaborationInvite",
    "PaperVersion",
    "CollaborationSession",
    "CollaborationRole",
    "InvitationStatus",

    # Comments
    "PaperComment",

    # Analytics
    "UserAnalytics",
    "PaperAnalytics",
    "ActivityLog",

    # Notifications
    "Notification",
    "NotificationType",

    # OAuth
    "OAuthToken",

    # Reference Papers
    "ReferencePaper",
    "PaperType",
]