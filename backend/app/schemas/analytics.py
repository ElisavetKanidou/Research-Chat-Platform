"""
Missing Analytics Types for Backend (app/types/analytics.py)
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel

# Match frontend analytics types exactly

class UserAnalytics(BaseModel):
    userId: str
    totalPapers: int
    publishedPapers: int
    draftPapers: int
    inProgressPapers: int
    totalWords: int
    avgProgress: float
    totalCollaborators: int
    researchAreas: int
    avgCompletionTime: float
    productivityScore: float
    lastUpdated: datetime


class SectionProgress(BaseModel):
    sectionId: str
    title: str
    wordCount: int
    status: str
    timeSpent: float
    lastModified: datetime
    revisions: int


class TimeDistribution(BaseModel):
    date: str
    wordsWritten: int
    timeSpent: float
    sessionsCount: int


class PaperAnalytics(BaseModel):
    paperId: str
    wordCount: int
    readingTime: int
    estimatedCompletionTime: float
    collaboratorCount: int
    sectionProgress: List[SectionProgress]
    timeDistribution: List[TimeDistribution]
    citationCount: int
    revisionCount: int
    createdAt: datetime
    lastModified: datetime


class ProductivityDataPoint(BaseModel):
    date: str
    wordsWritten: int
    timeSpent: float
    papersWorkedOn: int
    sessionsCount: int
    focusScore: int


class ProductivityMetrics(BaseModel):
    daily: List[ProductivityDataPoint]
    weekly: List[ProductivityDataPoint]
    monthly: List[ProductivityDataPoint]


class ContributionType(BaseModel):
    type: str
    count: int
    percentage: float


class CollaborationAnalytics(BaseModel):
    collaboratorId: str
    name: str
    email: str
    sharedPapers: int
    totalContributions: int
    avgResponseTime: float
    collaborationStarted: datetime
    lastActivity: datetime
    contributionTypes: List[ContributionType]


class ResearchTrend(BaseModel):
    area: str
    paperCount: int
    wordCount: int
    averageProgress: float
    timeSpent: float
    collaborators: List[str]
    publications: int
    citations: int


class PreferredTime(BaseModel):
    hour: int
    dayOfWeek: int
    productivity: float


class SessionLength(BaseModel):
    average: float
    optimal: float
    distribution: List[int]


class WritingVelocity(BaseModel):
    wordsPerHour: int
    wordsPerSession: int
    consistency: int


class WritingPattern(BaseModel):
    preferredTime: PreferredTime
    sessionLength: SessionLength
    writingVelocity: WritingVelocity


class Insight(BaseModel):
    id: str
    type: str
    title: str
    description: str
    severity: str
    actionable: bool
    suggestions: List[str]
    dataPoints: List[Any] = []
    generatedAt: datetime


class ComparisonMetric(BaseModel):
    label: str
    userValue: Union[int, float]
    benchmarkValue: Union[int, float]
    percentile: int
    trend: str


class AnalyticsFilter(BaseModel):
    timeframe: str = "month"
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    paperIds: Optional[List[str]] = None
    metrics: List[str] = ["all"]


class AnalyticsTimeframe(str):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

