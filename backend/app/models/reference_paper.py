"""
Reference Paper Model - For Lab and Personal Papers used for AI Personalization
Stores uploaded papers that influence AI writing style and suggestions
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
import enum

from app.models.base import BaseModel


class PaperType(str, enum.Enum):
    """Type of reference paper"""
    LAB = "lab"  # Papers from user's research lab/group
    PERSONAL = "personal"  # User's own published papers
    LITERATURE = "literature"  # Important papers from the field


class ReferencePaper(BaseModel):
    """
    Reference papers used for AI personalization.

    These papers are analyzed to understand:
    - Lab research patterns and terminology (LAB papers)
    - User's personal writing style (PERSONAL papers)
    - Field-wide trends and standards (LITERATURE papers)
    """
    __tablename__ = "reference_papers"

    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="reference_papers")

    # Paper information
    title = Column(String(500), nullable=False)
    authors = Column(String(500), nullable=True)  # Comma-separated authors
    year = Column(Integer, nullable=True)
    journal = Column(String(300), nullable=True)
    doi = Column(String(200), nullable=True)

    # Paper type and categorization
    paper_type = Column(Enum(PaperType), nullable=False, default=PaperType.PERSONAL)
    research_area = Column(String(200), nullable=True)
    keywords = Column(JSON, nullable=True)  # Array of keywords

    # File storage
    file_url = Column(String(500), nullable=False)  # Path to uploaded PDF
    file_size = Column(Integer, nullable=True)  # File size in bytes
    original_filename = Column(String(300), nullable=False)

    # Extracted content
    content_text = Column(Text, nullable=True)  # Extracted text from PDF
    abstract = Column(Text, nullable=True)  # Paper abstract

    # Analysis status
    is_analyzed = Column(Boolean, default=False, nullable=False)
    analysis_date = Column(String(50), nullable=True)

    # Writing style analysis (stored as JSON)
    writing_style_features = Column(JSON, nullable=True, default=dict)
    # Example features:
    # {
    #   "avg_sentence_length": 23.5,
    #   "vocabulary_complexity": 0.78,
    #   "passive_voice_ratio": 0.45,
    #   "common_phrases": ["in this study", "our results show"],
    #   "technical_terms": ["neural network", "regression analysis"],
    #   "citation_density": 0.15,
    #   "section_structure": ["introduction", "methodology", "results"]
    # }

    # Paper metadata (renamed from 'metadata' to avoid SQLAlchemy reserved keyword)
    paper_metadata = Column(JSON, nullable=True, default=dict)
    # Additional info like:
    # - Number of pages
    # - Language
    # - Conference/journal details
    # - Impact factor

    # Usage tracking
    times_used = Column(Integer, default=0, nullable=False)  # How many times used in AI responses

    def __repr__(self) -> str:
        return f"<ReferencePaper(id={self.id}, title='{self.title[:50]}', type='{self.paper_type}')>"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "journal": self.journal,
            "doi": self.doi,
            "paper_type": self.paper_type.value if self.paper_type else None,
            "research_area": self.research_area,
            "keywords": self.keywords,
            "file_url": self.file_url,
            "file_size": self.file_size,
            "original_filename": self.original_filename,
            "abstract": self.abstract,
            "is_analyzed": self.is_analyzed,
            "analysis_date": self.analysis_date,
            "writing_style_features": self.writing_style_features,
            "metadata": self.paper_metadata,
            "times_used": self.times_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def mark_as_analyzed(self, features: dict) -> None:
        """Mark paper as analyzed with extracted features"""
        from datetime import datetime
        self.is_analyzed = True
        self.analysis_date = datetime.utcnow().isoformat()
        self.writing_style_features = features
        self.updated_at = datetime.utcnow()

    def increment_usage(self) -> None:
        """Increment usage counter"""
        from datetime import datetime
        self.times_used += 1
        self.updated_at = datetime.utcnow()
