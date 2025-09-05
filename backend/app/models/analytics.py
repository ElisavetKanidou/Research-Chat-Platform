"""
Analytics models (app/models/analytics.py)
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.models.base import BaseModel


class UserAnalytics(BaseModel):
    """User analytics and metrics"""
    __tablename__ = "user_analytics"

    # Metrics
    total_papers = Column(Integer, default=0, nullable=False)
    published_papers = Column(Integer, default=0, nullable=False)
    total_words = Column(Integer, default=0, nullable=False)
    avg_completion_time = Column(Float, nullable=True)  # days
    productivity_score = Column(Float, default=0.0, nullable=False)

    # Activity metrics
    login_count = Column(Integer, default=0, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    active_days = Column(Integer, default=0, nullable=False)

    # Research insights
    research_areas = Column(JSON, nullable=True, default=[])
    collaboration_count = Column(Integer, default=0, nullable=False)
    citation_count = Column(Integer, default=0, nullable=False)

    # Time tracking
    daily_writing_minutes = Column(JSON, nullable=True, default={})  # {date: minutes}
    weekly_goals_met = Column(Integer, default=0, nullable=False)

    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="analytics")


class PaperAnalytics(BaseModel):
    """Paper-specific analytics"""
    __tablename__ = "paper_analytics"

    # Writing metrics
    words_per_session = Column(JSON, nullable=True, default=[])  # List of session word counts
    time_spent_minutes = Column(Integer, default=0, nullable=False)
    revision_count = Column(Integer, default=0, nullable=False)

    # Progress tracking
    daily_progress = Column(JSON, nullable=True, default={})  # {date: progress_percentage}
    section_completion_times = Column(JSON, nullable=True, default={})  # {section_id: completion_date}

    # Collaboration metrics
    collaborator_contributions = Column(JSON, nullable=True, default={})  # {user_id: word_count}
    comment_count = Column(Integer, default=0, nullable=False)
    review_cycles = Column(Integer, default=0, nullable=False)

    # Quality metrics
    readability_score = Column(Float, nullable=True)
    complexity_score = Column(Float, nullable=True)
    citation_density = Column(Float, nullable=True)

    # Paper relationship
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), unique=True, nullable=False)
    paper = relationship("Paper", back_populates="analytics")


class ActivityLog(BaseModel):
    """User activity logging"""
    __tablename__ = "activity_logs"

    # Activity details
    action = Column(String(100), nullable=False)
    resource = Column(String(50), nullable=False)  # paper, user, chat, etc.
    resource_id = Column(String(100), nullable=True)

    # Context
    details = Column(JSON, nullable=True, default={})
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Timestamps
    duration_ms = Column(Integer, nullable=True)
    session_id = Column(String(100), nullable=True)

    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User")

