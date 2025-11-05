"""
Collaboration models (app/models/collaboration.py)
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Text, Enum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
from app.models.base import BaseModel


class CollaborationRole(str, enum.Enum):
    """Collaboration role enumeration"""
    VIEWER = "viewer"
    COMMENTER = "commenter"
    EDITOR = "editor"
    CO_AUTHOR = "co-author"
    OWNER = "owner"


class InvitationStatus(str, enum.Enum):
    """Invitation status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class CollaborationInvite(BaseModel):
    """Collaboration invitation"""
    __tablename__ = "collaboration_invites"

    # Invitation details
    email = Column(String(255), nullable=False)
    role = Column(Enum(CollaborationRole), default=CollaborationRole.VIEWER, nullable=False)
    message = Column(Text, nullable=True)
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False)

    # Expiry and tracking
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    token = Column(String(255), unique=True, nullable=False)

    # Relationships
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False)
    paper = relationship("Paper")

    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    invited_by = relationship("User", foreign_keys=[invited_by_id])

    invited_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    invited_user = relationship("User", foreign_keys=[invited_user_id])


class PaperVersion(BaseModel):
    """Paper version tracking"""
    __tablename__ = "paper_versions"

    # Version info
    version_number = Column(String(20), nullable=False)
    title = Column(String(500), nullable=False)
    abstract = Column(Text, nullable=True)
    content_snapshot = Column(JSON, nullable=False)  # Full paper content

    # Change tracking
    changes_summary = Column(Text, nullable=True)
    word_count_change = Column(Integer, default=0, nullable=False)
    sections_modified = Column(JSON, nullable=True, default=[])

    # Metadata
    is_major_version = Column(Boolean, default=False, nullable=False)
    tags = Column(JSON, nullable=True, default=[])

    # Relationships
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False)
    paper = relationship("Paper", back_populates="versions")

    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")


class PaperComment(BaseModel):
    """Paper comments and reviews"""
    __tablename__ = "paper_comments"

    # Comment content
    content = Column(Text, nullable=False)
    comment_type = Column(String(20), default="general", nullable=False)  # general, suggestion, question, approval

    # Location context
    section_id = Column(UUID(as_uuid=True), ForeignKey("paper_sections.id"), nullable=True)
    line_number = Column(Integer, nullable=True)
    selection_start = Column(Integer, nullable=True)
    selection_end = Column(Integer, nullable=True)

    # Status
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Threading
    parent_id = Column(UUID(as_uuid=True), ForeignKey("paper_comments.id"), nullable=True)
    thread_id = Column(UUID(as_uuid=True), nullable=True)  # Root comment ID

    # Relationships
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False)
    paper = relationship("Paper", back_populates="comments")

    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    author = relationship("User", foreign_keys=[author_id])

    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    section = relationship("PaperSection")

    # Self-referencing for replies
    parent = relationship("PaperComment", remote_side="PaperComment.id", back_populates="replies")
    replies = relationship("PaperComment", back_populates="parent")


class CollaborationSession(BaseModel):
    """Real-time collaboration session tracking"""
    __tablename__ = "collaboration_sessions"

    # Session details
    session_id = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Cursor and selection tracking
    cursor_position = Column(JSON, nullable=True)  # {section_id, position}
    current_selection = Column(JSON, nullable=True)  # {section_id, start, end}

    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Relationships
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False)
    paper = relationship("Paper")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User")