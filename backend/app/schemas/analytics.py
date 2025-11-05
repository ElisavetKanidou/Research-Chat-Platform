"""
Analytics Schemas (app/schemas/analytics.py)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class AnalyticsOverview(BaseModel):
    """Analytics overview schema matching service output"""
    user_id: str
    timeframe: str
    total_papers: int = 0
    published_papers: int = 0
    draft_papers: int = 0
    in_progress_papers: int = 0
    total_words: int = 0
    avg_progress: float = 0.0
    total_collaborators: int = 0
    research_areas: int = 0
    avg_completion_time: float = 0.0
    productivity_score: int = 0
    last_updated: str

    # Additional nested data that service might return
    collaboration: Optional[Dict[str, Any]] = Field(default_factory=lambda: {"total_collaborators": 0})

    class Config:
        from_attributes = True


class TrendDataPoint(BaseModel):
    """Single data point for trend analysis"""
    date: str
    value: float
    label: Optional[str] = None


class TrendAnalysis(BaseModel):
    """Trend analysis schema"""
    period: str  # "day", "week", "month", "quarter", "year"
    metric: str
    data_points: List[TrendDataPoint] = []
    total_change: float = 0.0
    percentage_change: float = 0.0
    trend_direction: str = "stable"  # "up", "down", "stable"

    class Config:
        from_attributes = True


class SectionProgress(BaseModel):
    """Individual section progress"""
    section_id: str
    title: str
    word_count: int
    status: str
    progress: float
    last_modified: str


class PaperAnalytics(BaseModel):
    """Detailed paper analytics"""
    paper_id: str
    word_count: int
    reading_time: int
    estimated_completion_time: float
    collaborator_count: int
    section_progress: List[SectionProgress]
    revision_count: int
    created_at: str
    last_modified: str

    class Config:
        from_attributes = True


class ProductivityDataPoint(BaseModel):
    """Daily productivity metrics"""
    date: str
    words_written: int
    papers_worked_on: int
    sessions_count: int
    focus_score: int
    time_spent: Optional[float] = 0.0


class ProductivityMetrics(BaseModel):
    """Productivity metrics over time"""
    daily: List[ProductivityDataPoint]
    start_date: str
    end_date: str

    class Config:
        from_attributes = True


class CollaborationAnalytics(BaseModel):
    """Collaboration analytics for a collaborator"""
    collaborator_name: str
    shared_papers: int
    total_words: int
    research_areas: List[str]
    collaboration_strength: int

    class Config:
        from_attributes = True


class ResearchTrend(BaseModel):
    """Research trend by area"""
    area: str
    paper_count: int
    word_count: int
    average_progress: float
    collaborators: List[str]
    publications: int

    class Config:
        from_attributes = True


class WritingPattern(BaseModel):
    """Writing patterns and habits"""
    average_words_per_paper: float
    average_sections_per_paper: float
    most_productive_status: str
    consistency_score: float
    total_writing_days: int

    class Config:
        from_attributes = True


class Insight(BaseModel):
    """AI-generated insight"""
    type: str
    title: str
    description: str
    severity: str
    actionable: bool
    suggestions: Optional[List[str]] = None

    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    """Complete analytics response"""
    overview: AnalyticsOverview
    trends: Optional[List[TrendAnalysis]] = None
    insights: Optional[List[Insight]] = None

    class Config:
        from_attributes = True