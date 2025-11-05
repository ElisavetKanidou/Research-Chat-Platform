"""
Database models initialization
"""
from app.models.base import BaseModel

# User model (base for relationships)
from app.models.user import User

# Paper models
from app.models.paper import (
    Paper,
    PaperSection,
    PaperCollaborator,
    PaperStatus,
    SectionStatus
)

# Chat models
from app.models.chat import (
    ChatMessage,
    ChatAttachment,
    MessageRole,
    AttachmentType,
    PersonalizationSettings,
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
    "PersonalizationSettings",
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