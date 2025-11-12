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
    PaperComment,
    CollaborationSession,
    CollaborationRole,
    InvitationStatus
)

# Analytics models
from app.models.analytics import (
    UserAnalytics,
    PaperAnalytics,
    ActivityLog
)

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
    "PaperComment",
    "CollaborationSession",
    "CollaborationRole",
    "InvitationStatus",

    # Analytics
    "UserAnalytics",
    "PaperAnalytics",
    "ActivityLog",
]