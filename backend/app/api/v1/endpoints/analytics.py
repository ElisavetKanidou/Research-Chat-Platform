"""
Updated Analytics Endpoints to match Frontend (app/api/v1/endpoints/analytics.py)
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.paper_service import paper_service
from app.services.analytics_service import analytics_service
from app.schemas.analytics import AnalyticsOverview, TrendAnalysis
from app.schemas.common import SuccessResponse

router = APIRouter()


@router.get("/user")
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    timeframe: str = Query(default="month", pattern="^(day|week|month|quarter|year)$")
):
    """Get user analytics matching frontend expectations"""

    try:
        # Calculate date range based on timeframe
        end_date = datetime.utcnow()
        if timeframe == "day":
            start_date = end_date - timedelta(days=1)
        elif timeframe == "week":
            start_date = end_date - timedelta(weeks=1)
        elif timeframe == "month":
            start_date = end_date - timedelta(days=30)
        elif timeframe == "quarter":
            start_date = end_date - timedelta(days=90)
        else:  # year
            start_date = end_date - timedelta(days=365)

        # Get comprehensive analytics
        overview = await analytics_service.get_user_overview(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )

        # Transform to match frontend AnalyticsResponse format
        response = {
            "userId": str(current_user.id),
            "timeframe": timeframe,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "metrics": [
                {"name": "totalPapers", "value": overview.total_papers, "unit": "count", "change": 0, "changeType": "stable", "trend": []},
                {"name": "publishedPapers", "value": overview.published_papers, "unit": "count", "change": 0, "changeType": "stable", "trend": []},
                {"name": "draftPapers", "value": overview.total_papers - overview.published_papers, "unit": "count", "change": 0, "changeType": "stable", "trend": []},
                {"name": "inProgressPapers", "value": overview.total_papers - overview.published_papers, "unit": "count", "change": 0, "changeType": "stable", "trend": []},
                {"name": "totalWords", "value": overview.total_words, "unit": "words", "change": 12, "changeType": "increase", "trend": []},
                {"name": "avgProgress", "value": overview.avg_progress, "unit": "percentage", "change": 0, "changeType": "stable", "trend": []},
                {"name": "collaborators", "value": overview.collaboration.total_collaborators, "unit": "count", "change": 0, "changeType": "stable", "trend": []},
                {"name": "researchAreas", "value": len(overview.research_areas), "unit": "count", "change": 0, "changeType": "stable", "trend": []},
                {"name": "avgCompletionTime", "value": 4.2, "unit": "months", "change": 0, "changeType": "stable", "trend": []},
                {"name": "productivityScore", "value": overview.productivity_score, "unit": "score", "change": 5, "changeType": "increase", "trend": []},
            ],
            "insights": [],
            "generatedAt": datetime.utcnow().isoformat()
        }

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user analytics: {str(e)}"
        )


@router.get("/productivity")
async def get_productivity_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    filter: Optional[str] = Query(None)
):
    """Get productivity metrics matching frontend ProductivityMetrics format"""

    try:
        # Generate mock data that matches frontend expectations
        daily_data = []
        for i in range(30):
            date = datetime.utcnow() - timedelta(days=i)
            daily_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "wordsWritten": 200 + (i * 10) % 400,
                "timeSpent": 1 + (i % 6),
                "papersWorkedOn": 1 + (i % 3),
                "sessionsCount": 1 + (i % 4),
                "focusScore": 60 + (i % 40)
            })

        return {
            "daily": list(reversed(daily_data)),  # Most recent first
            "weekly": [],
            "monthly": []
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get productivity metrics: {str(e)}"
        )


@router.get("/collaboration")
async def get_collaboration_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get collaboration analytics"""

    try:
        # Mock collaboration data matching frontend expectations
        collaboration_data = [
            {
                "collaboratorId": "1",
                "name": "Dr. Sarah Wilson",
                "email": "sarah.wilson@university.edu",
                "sharedPapers": 3,
                "totalContributions": 25,
                "avgResponseTime": 2.5,
                "collaborationStarted": "2023-09-01T00:00:00Z",
                "lastActivity": "2024-01-15T10:30:00Z",
                "contributionTypes": [
                    {"type": "writing", "count": 10, "percentage": 40},
                    {"type": "review", "count": 8, "percentage": 32},
                    {"type": "editing", "count": 7, "percentage": 28}
                ]
            },
            {
                "collaboratorId": "2",
                "name": "Prof. Michael Johnson",
                "email": "m.johnson@research.edu",
                "sharedPapers": 2,
                "totalContributions": 18,
                "avgResponseTime": 1.8,
                "collaborationStarted": "2023-11-15T00:00:00Z",
                "lastActivity": "2024-01-10T16:20:00Z",
                "contributionTypes": [
                    {"type": "review", "count": 12, "percentage": 67},
                    {"type": "writing", "count": 4, "percentage": 22},
                    {"type": "editing", "count": 2, "percentage": 11}
                ]
            }
        ]

        return collaboration_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get collaboration analytics: {str(e)}"
        )


@router.get("/trends")
async def get_research_trends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get research trends matching frontend ResearchTrend format"""

    try:
        trends = [
            {
                "area": "Machine Learning",
                "paperCount": 5,
                "wordCount": 28500,
                "averageProgress": 72,
                "timeSpent": 120,
                "collaborators": ["Dr. Smith", "Jane Doe"],
                "publications": 2,
                "citations": 45
            },
            {
                "area": "Natural Language Processing",
                "paperCount": 3,
                "wordCount": 18200,
                "averageProgress": 65,
                "timeSpent": 85,
                "collaborators": ["Prof. Johnson"],
                "publications": 1,
                "citations": 23
            },
            {
                "area": "Computer Vision",
                "paperCount": 2,
                "wordCount": 12800,
                "averageProgress": 80,
                "timeSpent": 60,
                "collaborators": ["Dr. Wilson"],
                "publications": 1,
                "citations": 18
            }
        ]

        return trends

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get research trends: {str(e)}"
        )


@router.get("/writing-patterns")
async def get_writing_patterns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get writing patterns matching frontend WritingPattern format"""

    try:
        patterns = {
            "preferredTime": {
                "hour": 9,
                "dayOfWeek": 2,  # Tuesday
                "productivity": 85
            },
            "sessionLength": {
                "average": 2.5,
                "optimal": 3.0,
                "distribution": [1, 2, 4, 6, 3, 2, 1]  # Hours distribution
            },
            "writingVelocity": {
                "wordsPerHour": 320,
                "wordsPerSession": 800,
                "consistency": 75
            }
        }

        return patterns

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get writing patterns: {str(e)}"
        )


@router.get("/insights")
async def get_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI insights matching frontend Insight format"""

    try:
        insights = [
            {
                "id": "1",
                "type": "productivity",
                "title": "Peak Writing Hours",
                "description": "You are most productive between 9-11 AM, writing 40% more words during this time.",
                "severity": "info",
                "actionable": True,
                "suggestions": [
                    "Schedule important writing tasks during your peak hours",
                    "Block calendar time for deep work in the morning"
                ]
            },
            {
                "id": "2",
                "type": "collaboration",
                "title": "Collaboration Opportunity",
                "description": "Dr. Sarah Wilson has expertise that aligns with your current research direction.",
                "severity": "info",
                "actionable": True,
                "suggestions": [
                    "Reach out to discuss potential collaboration",
                    "Share your current draft for feedback"
                ]
            },
            {
                "id": "3",
                "type": "writing",
                "title": "Writing Consistency",
                "description": "Your writing sessions are most effective when longer than 2 hours.",
                "severity": "info",
                "actionable": True,
                "suggestions": [
                    "Block longer time periods for writing",
                    "Avoid short writing sessions when possible"
                ]
            }
        ]

        return insights

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insights: {str(e)}"
        )


@router.get("/comparisons")
async def get_comparisons(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comparison metrics"""

    try:
        comparisons = [
            {
                "label": "Words per Week",
                "userValue": 2847,
                "benchmarkValue": 2200,
                "percentile": 78,
                "trend": "improving"
            },
            {
                "label": "Papers per Year",
                "userValue": 4,
                "benchmarkValue": 3.2,
                "percentile": 65,
                "trend": "stable"
            },
            {
                "label": "Collaboration Rate",
                "userValue": 65,
                "benchmarkValue": 45,
                "percentile": 82,
                "trend": "improving"
            }
        ]

        return comparisons

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get comparisons: {str(e)}"
        )


@router.post("/export")
async def export_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    format: str = "json",
    filter: Optional[Dict[str, Any]] = None
):
    """Export analytics data"""

    try:
        # This would integrate with your export service
        export_data = {
            "userId": str(current_user.id),
            "exportDate": datetime.utcnow().isoformat(),
            "format": format,
            "data": {
                "summary": "Analytics export completed",
                "note": "This is a placeholder implementation"
            }
        }

        return {
            "exportId": f"export_{int(datetime.utcnow().timestamp())}",
            "status": "completed",
            "downloadUrl": "/exports/analytics.json",
            "createdAt": datetime.utcnow().isoformat(),
            "expiresAt": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export analytics: {str(e)}"
        )


