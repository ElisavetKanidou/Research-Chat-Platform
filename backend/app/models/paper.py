"""
Paper database model - COMPLETE CLEAN VERSION
backend/app/models/paper.py
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum

from app.models.base import BaseModel


class PaperStatus(str, enum.Enum):
    """Paper status enumeration"""
    DRAFT = "draft"
    IN_PROGRESS = "in-progress"
    IN_REVIEW = "in-review"
    REVISION = "revision"
    COMPLETED = "completed"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class SectionStatus(str, enum.Enum):
    """Section status enumeration"""
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs-review"


class Paper(BaseModel):
    """Paper model for research paper management"""
    __tablename__ = "papers"

    # Basic paper information
    title = Column(String(500), nullable=False)
    abstract = Column(Text, nullable=True, default="")

    # Status and progress
    status = Column(Enum(PaperStatus), default=PaperStatus.DRAFT, nullable=False)
    progress = Column(Integer, default=0, nullable=False)  # 0-100 percentage

    # Word count tracking
    target_word_count = Column(Integer, default=8000, nullable=False)
    current_word_count = Column(Integer, default=0, nullable=False)

    # Research information
    research_area = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True, default=[])  # Array of tag strings

    # Collaboration
    co_authors = Column(JSON, nullable=True, default=[])  # Array of co-author names
    is_public = Column(Boolean, default=False, nullable=False)

    # ✅ AI Personalization Settings (per-paper, no global dependency)
    ai_settings = Column(JSON, nullable=True, default=None)
    """
    Structure (simplified - no global settings reference):
    {
        "lab_level": 7,
        "personal_level": 8,
        "global_level": 5,
        "writing_style": "academic",
        "context_depth": "moderate",
        "research_focus": ["quantum computing", "optimization"],
        "suggestions_enabled": true
    }
    """

    # Publication information
    doi = Column(String(255), nullable=True)
    journal = Column(String(255), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    citation_count = Column(Integer, default=0, nullable=False)

    # Deadline tracking
    deadline = Column(DateTime, nullable=True)

    # Owner relationship
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="papers")

    # Relationships
    sections = relationship(
        "PaperSection",
        back_populates="paper",
        cascade="all, delete-orphan",
        order_by="PaperSection.order"
    )
    collaborators = relationship(
        "PaperCollaborator",
        back_populates="paper",
        foreign_keys="PaperCollaborator.paper_id",
        cascade="all, delete-orphan"
    )
    chat_messages = relationship(
        "ChatMessage",
        back_populates="paper",
        cascade="all, delete-orphan"
    )
    versions = relationship(
        "PaperVersion",
        back_populates="paper",
        cascade="all, delete-orphan"
    )
    comments = relationship(
        "app.models.comment.PaperComment",
        back_populates="paper",
        cascade="all, delete-orphan"
    )
    analytics = relationship(
        "PaperAnalytics",
        back_populates="paper",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Paper(id={self.id}, title='{self.title}', status='{self.status}')>"

    # ==================== PROGRESS & WORD COUNT ====================

    def calculate_progress(self) -> int:
        """Calculate paper progress based on section completion"""
        if not self.sections:
            return 0

        completed_sections = sum(
            1 for section in self.sections
            if section.status == SectionStatus.COMPLETED
        )
        total_sections = len(self.sections)

        if total_sections == 0:
            return 0

        progress = int((completed_sections / total_sections) * 100)
        self.progress = progress
        return progress

    def calculate_word_count(self) -> int:
        """Calculate total word count from all sections"""
        total_words = sum(section.word_count for section in self.sections)
        self.current_word_count = total_words
        return total_words

    def get_completion_percentage(self) -> float:
        """Get word count completion percentage"""
        if self.target_word_count == 0:
            return 0.0
        return min(100.0, (self.current_word_count / self.target_word_count) * 100)

    # ==================== AI SETTINGS ====================

    def get_ai_settings(self) -> dict:
        """
        Get AI settings for this paper

        Returns:
            Dictionary of AI settings for this paper
        """
        if not self.ai_settings:
            # Return default settings
            default_settings = {
                "lab_level": 7,
                "personal_level": 8,
                "global_level": 5,
                "writing_style": "academic",
                "context_depth": "moderate",
                "research_focus": [],
                "suggestions_enabled": True
            }
            print(f"📋 [Paper.get_ai_settings] Returning defaults")
            return default_settings

        # Ensure research_focus is always an array
        if "research_focus" not in self.ai_settings:
            self.ai_settings["research_focus"] = []

        print(f"📋 [Paper.get_ai_settings] Returning: {self.ai_settings}")
        return self.ai_settings

    def update_ai_settings(self, settings: dict) -> None:
        """
        Update paper's AI settings

        Args:
            settings: Dictionary of AI settings to update
        """
        print(f"🔧 [Paper.update_ai_settings] BEFORE: {self.ai_settings}")
        print(f"📥 [Paper.update_ai_settings] Incoming: {settings}")

        # Initialize if needed
        if not self.ai_settings:
            self.ai_settings = {}

        # Deep merge settings - handle each field explicitly
        for key, value in settings.items():
            if value is not None:  # Only update non-None values
                self.ai_settings[key] = value
                print(f"  ✅ Set {key} = {value} (type: {type(value)})")

        # ✅ CRITICAL: Tell SQLAlchemy the JSON column changed!
        flag_modified(self, "ai_settings")
        print(f"🚩 [Paper.update_ai_settings] Called flag_modified")

        # Update timestamp
        self.updated_at = datetime.utcnow()

        print(f"🔧 [Paper.update_ai_settings] AFTER: {self.ai_settings}")

    # ==================== COLLABORATION ====================

    def add_collaborator(self, user_id: str, role: str = "editor") -> None:
        """Add a collaborator to the paper"""
        # This will be implemented when we create the PaperCollaborator model
        pass

    def remove_collaborator(self, user_id: str) -> bool:
        """Remove a collaborator from the paper"""
        # This will be implemented when we create the PaperCollaborator model
        return False

    def is_editable_by(self, user_id: str) -> bool:
        """Check if user can edit this paper"""
        if str(self.owner_id) == str(user_id):
            return True

        # Check if user is a collaborator with edit permissions
        for collab in self.collaborators:
            if str(collab.user_id) == str(user_id) and collab.role in ["editor", "co-author"]:
                return True

        return False

    def is_viewable_by(self, user_id: str) -> bool:
        """Check if user can view this paper"""
        if self.is_public:
            return True

        if str(self.owner_id) == str(user_id):
            return True

        # Check if user is a collaborator
        for collab in self.collaborators:
            if str(collab.user_id) == str(user_id):
                return True

        return False

    # ==================== UTILITY METHODS ====================

    def update_from_dict(self, data: dict) -> None:
        """Update paper from dictionary with automatic progress calculation"""
        super().update_from_dict(data)

        # Recalculate progress and word count if sections were updated
        if "sections" in data or any(
            section.updated_at > self.updated_at for section in self.sections
        ):
            self.calculate_progress()
            self.calculate_word_count()

    def to_dict_with_sections(self) -> dict:
        """Convert to dictionary including sections"""
        paper_dict = self.to_dict()
        paper_dict["sections"] = [section.to_dict() for section in self.sections]
        paper_dict["collaborators"] = [collab.to_dict() for collab in self.collaborators]
        return paper_dict


class PaperSection(BaseModel):
    """Paper section model"""
    __tablename__ = "paper_sections"

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True, default="")
    status = Column(Enum(SectionStatus), default=SectionStatus.NOT_STARTED, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    word_count = Column(Integer, default=0, nullable=False)

    # Parent paper relationship
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False)
    paper = relationship("Paper", back_populates="sections")

    # Comments relationship
    comments = relationship(
        "app.models.comment.PaperComment",
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="app.models.comment.PaperComment.created_at"
    )

    def __repr__(self) -> str:
        return f"<PaperSection(id={self.id}, title='{self.title}', status='{self.status}')>"

    def update_word_count(self) -> int:
        """Update word count based on content"""
        if self.content:
            # Simple word count (can be improved with better text processing)
            words = len(self.content.split())
            self.word_count = words
        else:
            self.word_count = 0

        return self.word_count

    def set_content(self, content: str) -> None:
        """Set section content and update word count"""
        self.content = content
        self.update_word_count()
        self.updated_at = datetime.utcnow()

        # Auto-update status based on content
        if content.strip():
            if self.status == SectionStatus.NOT_STARTED:
                self.status = SectionStatus.IN_PROGRESS
        else:
            self.status = SectionStatus.NOT_STARTED


class PaperCollaborator(BaseModel):
    """Paper collaborator relationship model"""
    __tablename__ = "paper_collaborators"

    # Collaboration role
    role = Column(String(50), default="viewer", nullable=False)  # viewer, editor, co-author
    status = Column(String(50), default="pending", nullable=False)  # pending, accepted, declined

    # Permissions
    can_edit = Column(Boolean, default=False, nullable=False)
    can_comment = Column(Boolean, default=True, nullable=False)
    can_invite_others = Column(Boolean, default=False, nullable=False)

    # Relationships
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False)
    paper = relationship("Paper", back_populates="collaborators")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="collaborations", foreign_keys=[user_id])

    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    invited_by = relationship("User", foreign_keys=[invited_by_id])
    invited_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    accepted_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<PaperCollaborator(paper_id={self.paper_id}, user_id={self.user_id}, role='{self.role}')>"

    def accept_invitation(self) -> None:
        """Accept collaboration invitation"""
        self.status = "accepted"
        self.accepted_at = datetime.utcnow()

        # Set permissions based on role
        if self.role in ["editor", "co-author"]:
            self.can_edit = True
            self.can_invite_others = self.role == "co-author"

    def decline_invitation(self) -> None:
        """Decline collaboration invitation"""
        self.status = "declined"