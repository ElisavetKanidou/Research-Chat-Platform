"""
CORRECTED Analytics Endpoints - Removed duplicate /productivity endpoint
app/api/v1/endpoints/analytics.py
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.paper import Paper, PaperStatus, PaperCollaborator
from app.services.analytics_service import analytics_service

router = APIRouter()

# ============================================
# MAIN ANALYTICS ENDPOINTS
# ============================================

@router.get("/overview")
async def get_analytics_overview(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get overview analytics for the user"""

    # Total papers by status
    status_query = select(
        Paper.status,
        func.count(Paper.id).label('count')
    ).where(
        Paper.owner_id == current_user.id
    ).group_by(Paper.status)

    status_result = await db.execute(status_query)
    status_counts = {}
    for row in status_result:
        # Convert enum to string
        status_str = row.status.value if hasattr(row.status, 'value') else str(row.status)
        status_counts[status_str] = row.count

    # Total word count
    word_count_query = select(
        func.sum(Paper.current_word_count).label('total_words')
    ).where(Paper.owner_id == current_user.id)

    word_result = await db.execute(word_count_query)
    total_words = word_result.scalar() or 0

    # Average progress
    progress_query = select(
        func.avg(Paper.progress).label('avg_progress')
    ).where(
        and_(
            Paper.owner_id == current_user.id,
            Paper.status != PaperStatus.ARCHIVED
        )
    )

    progress_result = await db.execute(progress_query)
    avg_progress = progress_result.scalar() or 0

    # Papers created this month
    now = datetime.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    this_month_query = select(
        func.count(Paper.id)
    ).where(
        and_(
            Paper.owner_id == current_user.id,
            Paper.created_at >= first_day_of_month
        )
    )

    this_month_result = await db.execute(this_month_query)
    papers_this_month = this_month_result.scalar() or 0

    # ============================================
    # FIX: Calculate active_papers correctly
    # Check all possible status variations
    # ============================================
    active_papers = 0
    for status_key in status_counts.keys():
        status_lower = status_key.lower()
        # Match any variation: 'in-progress', 'IN_PROGRESS', 'draft', 'DRAFT', etc.
        if any(x in status_lower for x in ['progress', 'draft', 'in_progress', 'in-progress']):
            active_papers += status_counts[status_key]

    # Debug: Print status_counts to see actual values
    print(f"DEBUG - Status counts: {status_counts}")
    print(f"DEBUG - Active papers: {active_papers}")

    return {
        "total_papers": sum(status_counts.values()),
        "status_breakdown": status_counts,
        "total_words": int(total_words),
        "average_progress": round(float(avg_progress), 2),
        "active_papers": active_papers,  # ← Fixed calculation
        "published_papers": status_counts.get('PUBLISHED', 0) or status_counts.get('published', 0),
        "papers_this_month": papers_this_month
    }

@router.get("/productivity")
async def get_productivity_analytics(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        months: int = Query(6, ge=1, le=24)
):
    """Get monthly productivity data"""

    now = datetime.now()

    # Monthly paper counts and word counts
    monthly_query = select(
        extract('year', Paper.created_at).label('year'),
        extract('month', Paper.created_at).label('month'),
        func.count(Paper.id).label('paper_count'),
        func.sum(Paper.current_word_count).label('word_count')
    ).where(
        Paper.owner_id == current_user.id
    ).group_by(
        extract('year', Paper.created_at),
        extract('month', Paper.created_at)
    ).order_by(
        extract('year', Paper.created_at),
        extract('month', Paper.created_at)
    )

    result = await db.execute(monthly_query)
    monthly_data = []

    for row in result:
        try:
            month_name = datetime(int(row.year), int(row.month), 1).strftime('%b')
            monthly_data.append({
                "month": month_name,
                "year": int(row.year),
                "papers": row.paper_count,
                "words": int(row.word_count or 0)
            })
        except Exception as e:
            print(f"Error processing row: {e}")
            continue

    # ============================================
    # FIX 1: Calculate writing velocity from UPDATED papers
    # (papers worked on in last 30 days, not created)
    # ============================================
    recent_work_query = select(
        func.sum(Paper.current_word_count)
    ).where(
        and_(
            Paper.owner_id == current_user.id,
            Paper.updated_at >= now - timedelta(days=30)  # ← Changed from created_at
        )
    )

    words_result = await db.execute(recent_work_query)
    words_last_month = words_result.scalar() or 0
    words_per_week = int(words_last_month / 4) if words_last_month else 0

    # ============================================
    # FIX 2: Calculate completion time correctly
    # ============================================
    completed_papers_query = select(
        Paper.created_at,
        Paper.updated_at
    ).where(
        and_(
            Paper.owner_id == current_user.id,
            Paper.status == PaperStatus.PUBLISHED
        )
    )

    completed_result = await db.execute(completed_papers_query)
    completion_times = []

    for row in completed_result:
        if row.created_at and row.updated_at:
            delta = row.updated_at - row.created_at
            months_taken = delta.days / 30
            if months_taken > 0:  # Only count valid times
                completion_times.append(months_taken)

    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

    return {
        "monthly_data": monthly_data,
        "writing_velocity": {
            "words_per_week": words_per_week,
            "change_from_last_month": 0
        },
        "completion_time": {
            "average_months": round(avg_completion_time, 1),
            "fastest_months": round(min(completion_times), 1) if completion_times else 0
        }
    }


@router.get("/collaboration")
async def get_collaboration_analytics(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get collaboration analytics based on real paper collaborations"""

    # Get all papers with their collaborators (from paper_collaborators table)
    # Load collaborators and their user info
    papers_query = select(Paper).where(Paper.owner_id == current_user.id).options(
        selectinload(Paper.collaborators).selectinload(PaperCollaborator.user)
    )
    result = await db.execute(papers_query)
    papers = result.scalars().all()

    # Collect all collaborators with their user info
    collaborator_papers = {}  # {user_id: {"name": str, "email": str, "papers": int}}
    collaborative_paper_count = 0

    for paper in papers:
        if paper.collaborators:
            collaborative_paper_count += 1
            for collab in paper.collaborators:
                user_id = str(collab.user_id)
                if user_id not in collaborator_papers:
                    # Get user info from the collaboration
                    collaborator_papers[user_id] = {
                        "name": collab.user.name if collab.user else "Unknown",
                        "email": collab.user.email if collab.user else "",
                        "papers": 0
                    }
                collaborator_papers[user_id]["papers"] += 1

    # Sort by number of papers and get top 10
    top_collaborators = sorted(
        [
            {"name": data["name"], "papers": data["papers"]}
            for data in collaborator_papers.values()
        ],
        key=lambda x: x["papers"],
        reverse=True
    )[:10]

    solo_papers = len(papers) - collaborative_paper_count

    return {
        "total_collaborators": len(collaborator_papers),
        "collaborative_papers": collaborative_paper_count,
        "solo_papers": solo_papers,
        "top_collaborators": top_collaborators
    }


@router.get("/research-impact")
async def get_research_impact(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get research impact analytics with H-Index calculation"""

    # Get all published papers with their citation counts
    papers_query = select(
        Paper.citation_count
    ).where(
        and_(
            Paper.owner_id == current_user.id,
            Paper.status == PaperStatus.PUBLISHED,
            Paper.citation_count.isnot(None)
        )
    ).order_by(Paper.citation_count.desc())

    papers_result = await db.execute(papers_query)
    citation_counts = [row.citation_count for row in papers_result if row.citation_count > 0]

    # Calculate total citations
    total_citations = sum(citation_counts)

    # Calculate H-Index
    h_index = 0
    for i, citations in enumerate(citation_counts, start=1):
        if citations >= i:
            h_index = i
        else:
            break

    # Published papers count
    published_query = select(
        func.count(Paper.id)
    ).where(
        and_(
            Paper.owner_id == current_user.id,
            Paper.status == PaperStatus.PUBLISHED
        )
    )

    published_result = await db.execute(published_query)
    published_count = published_result.scalar() or 0

    # Published papers by research area
    area_query = select(
        Paper.research_area,
        func.count(Paper.id).label('count')
    ).where(
        and_(
            Paper.owner_id == current_user.id,
            Paper.status == PaperStatus.PUBLISHED,
            Paper.research_area.isnot(None)
        )
    ).group_by(Paper.research_area)

    area_result = await db.execute(area_query)
    research_areas = [
        {"area": row.research_area, "papers": row.count}
        for row in area_result
    ]

    return {
        "total_citations": int(total_citations),
        "published_papers": published_count,
        "research_areas": research_areas,
        "h_index": h_index,  # ← CALCULATED!
        "average_citations": round(total_citations / published_count, 1) if published_count > 0 else 0
    }

# ============================================
# LEGACY ENDPOINTS (Keep for compatibility)
# ============================================

@router.get("/trends")
async def get_research_trends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get research trends"""
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
        }
    ]
    return trends


@router.get("/insights")
async def get_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI insights"""
    insights = [
        {
            "id": "1",
            "type": "productivity",
            "title": "Peak Writing Hours",
            "description": "You are most productive between 9-11 AM.",
            "severity": "info",
            "actionable": True,
            "suggestions": ["Schedule important writing tasks during peak hours"]
        }
    ]
    return insights


@router.post("/export")
async def export_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    format: str = "json"
):
    """Export analytics data"""
    return {
        "exportId": f"export_{int(datetime.utcnow().timestamp())}",
        "status": "completed",
        "downloadUrl": "/exports/analytics.json",
        "createdAt": datetime.utcnow().isoformat()
    }