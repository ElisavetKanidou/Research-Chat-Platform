"""
Chat message database models - FIXED VERSION
Remove duplicate PersonalizationSettings class
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum

from app.models.base import BaseModel
# ✅ Import PersonalizationSettings from its own file
from app.models.personalization_settings import PersonalizationSettings


class MessageRole(str, enum.Enum):
    """Chat message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AttachmentType(str, enum.Enum):
    """Chat attachment type enumeration"""
    EXCEL = "excel"
    PDF = "pdf"
    REFERENCES = "references"
    DATA = "data"
    IMAGE = "image"
    TEXT = "text"


class ChatMessage(BaseModel):
    """Chat message model"""
    __tablename__ = "chat_messages"

    # Message content
    content = Column(Text, nullable=False)
    role = Column(Enum(MessageRole), nullable=False)

    # Context information
    paper_context = Column(String(255), nullable=True)  # Paper title for context
    needs_confirmation = Column(Boolean, default=False, nullable=False)
    confirmed = Column(Boolean, default=False, nullable=False)

    # User feedback
    user_feedback = Column(Boolean, nullable=True)  # True=helpful, False=not helpful, None=no feedback
    feedback_timestamp = Column(DateTime, nullable=True)

    # Metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    message_metadata = Column(JSON, nullable=True, default={})  # sources, confidence, reasoning steps

    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="chat_messages")

    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=True)
    paper = relationship("Paper", back_populates="chat_messages")

    # Attachments relationship
    attachments = relationship("ChatAttachment", back_populates="message", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, role='{self.role}', user_id={self.user_id})>"

    def to_dict_with_attachments(self) -> dict:
        """Convert to dictionary including attachments"""
        message_dict = self.to_dict()
        message_dict["attachments"] = [att.to_dict() for att in self.attachments]
        return message_dict


class ChatAttachment(BaseModel):
    """Chat attachment model"""
    __tablename__ = "chat_attachments"

    # Attachment information
    type = Column(Enum(AttachmentType), nullable=False)
    name = Column(String(255), nullable=False)
    size = Column(String(50), nullable=True)  # Human readable size (e.g., "2.5MB")
    url = Column(String(500), nullable=True)

    # Attachment data (stored as JSON for flexibility)
    data = Column(JSON, nullable=True)

    # Relationship to message
    message_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id"), nullable=False)
    message = relationship("ChatMessage", back_populates="attachments")

    def __repr__(self) -> str:
        return f"<ChatAttachment(id={self.id}, type='{self.type}', name='{self.name}')>"


# ✅ PersonalizationSettings is now imported from app.models.personalization_settings
# No duplicate definition needed here


class ChatSession(BaseModel):
    """Chat session tracking"""
    __tablename__ = "chat_sessions"

    # Session information
    session_key = Column(String(255), unique=True, nullable=False)  # user_id or user_id-paper_id
    title = Column(String(255), nullable=True)

    # Context
    paper_context = Column(JSON, nullable=True)  # Serialized paper context
    user_papers_context = Column(JSON, nullable=True)  # User's other papers for context

    # Session metadata
    message_count = Column(String(10), default="0", nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User")

    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=True)
    paper = relationship("Paper")

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, session_key='{self.session_key}')>"

    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        self.message_count = str(int(self.message_count) + 1)


class AIInteraction(BaseModel):
    """Track AI service interactions for analytics"""
    __tablename__ = "ai_interactions"

    # Interaction details
    interaction_type = Column(String(50), nullable=False)  # chat, suggestions, analysis, outline
    prompt_tokens = Column(String(10), default="0", nullable=False)
    completion_tokens = Column(String(10), default="0", nullable=False)
    total_tokens = Column(String(10), default="0", nullable=False)

    # Performance metrics
    response_time_ms = Column(String(10), nullable=True)
    model_used = Column(String(50), nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)

    # Context
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=True)

    # Relationships
    user = relationship("User")
    paper = relationship("Paper")

    def __repr__(self) -> str:
        return f"<AIInteraction(id={self.id}, type='{self.interaction_type}', user_id={self.user_id})>"

    @classmethod
    def create_interaction(
            cls,
            interaction_type: str,
            user_id: str,
            paper_id: str = None,
            model_used: str = None,
            prompt_tokens: int = 0,
            completion_tokens: int = 0,
            response_time_ms: int = None,
            success: bool = True,
            error_message: str = None
    ):
        """Factory method to create interaction record"""
        return cls(
            interaction_type=interaction_type,
            user_id=user_id,
            paper_id=paper_id,
            model_used=model_used,
            prompt_tokens=str(prompt_tokens),
            completion_tokens=str(completion_tokens),
            total_tokens=str(prompt_tokens + completion_tokens),
            response_time_ms=str(response_time_ms) if response_time_ms else None,
            success=success,
            error_message=error_message
        )