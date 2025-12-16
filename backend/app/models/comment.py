"""
Paper Comment Model - For collaborative commenting on paper sections
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.models.base import BaseModel


class PaperComment(BaseModel):
    """
    Comments on paper sections for collaborative writing
    """
    __tablename__ = "paper_comments"
    __table_args__ = {'extend_existing': True}

    # Comment content
    content = Column(Text, nullable=False)

    # Optional: specific text selection within section
    # For highlighting specific parts of the text
    selection_start = Column(Integer, nullable=True)  # Character position
    selection_end = Column(Integer, nullable=True)    # Character position
    selected_text = Column(Text, nullable=True)       # The selected text

    # Comment metadata
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False)
    paper = relationship("app.models.paper.Paper", back_populates="comments")

    section_id = Column(UUID(as_uuid=True), ForeignKey("paper_sections.id"), nullable=False)
    section = relationship("app.models.paper.PaperSection", back_populates="comments")

    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    author = relationship("app.models.user.User", foreign_keys=[author_id])

    resolved_by = relationship("app.models.user.User", foreign_keys=[resolved_by_id])

    # Reply thread (optional - for nested comments)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey("paper_comments.id"), nullable=True)
    parent_comment = relationship(
        "PaperComment",
        remote_side="[PaperComment.id]",
        backref=backref("replies", cascade="all, delete-orphan"),
        foreign_keys="[PaperComment.parent_comment_id]"
    )

    def __repr__(self) -> str:
        return f"<PaperComment(id={self.id}, author={self.author_id}, paper={self.paper_id})>"

    def to_dict(self) -> dict:
        """Convert comment to dictionary with author info"""
        base_dict = super().to_dict()
        base_dict.update({
            "author": {
                "id": str(self.author.id),
                "name": self.author.name,
                "email": self.author.email
            } if self.author else None,
            "resolved_by": {
                "id": str(self.resolved_by.id),
                "name": self.resolved_by.name
            } if self.resolved_by else None,
            "replies_count": 0  # Simplified - avoid lazy loading in async context
        })
        return base_dict

    def resolve(self, user_id: str) -> None:
        """Mark comment as resolved"""
        self.is_resolved = True
        self.resolved_at = datetime.utcnow()
        self.resolved_by_id = user_id

    def unresolve(self) -> None:
        """Mark comment as unresolved"""
        self.is_resolved = False
        self.resolved_at = None
        self.resolved_by_id = None
