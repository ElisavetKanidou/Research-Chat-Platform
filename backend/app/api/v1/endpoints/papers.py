"""
Paper management CRUD API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.paper import Paper, PaperSection, PaperStatus
from app.schemas.paper import (
    PaperCreate, PaperUpdate, PaperResponse, PaperListResponse,
    PaperSectionCreate, PaperSectionUpdate, PaperSectionResponse
)
from app.core.exceptions import NotFoundException, AuthorizationException, ValidationException
from app.services.paper_service import paper_service

router = APIRouter()


@router.post("/", response_model=PaperResponse)
async def create_paper(
        paper_data: PaperCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Create a new research paper"""

    # Check if user can create papers (subscription limits)
    if not current_user.can_create_papers():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Paper creation limit reached for your subscription plan"
        )

    paper = await paper_service.create_paper(
        db=db,
        user_id=current_user.id,
        paper_data=paper_data
    )

    return PaperResponse.model_validate(paper)


@router.get("/", response_model=List[PaperListResponse])
async def get_papers(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        status_filter: Optional[str] = Query(None, description="Filter by paper status"),
        research_area: Optional[str] = Query(None, description="Filter by research area"),
        search: Optional[str] = Query(None, description="Search in title and abstract"),
        skip: int = Query(0, ge=0, description="Number of papers to skip"),
        limit: int = Query(50, ge=1, le=100, description="Number of papers to return")
):
    """Get user's papers with optional filtering and pagination"""

    query = select(Paper).where(Paper.owner_id == current_user.id)

    # Apply filters
    if status_filter:
        try:
            status_enum = PaperStatus(status_filter)
            query = query.where(Paper.status == status_enum)
        except ValueError:
            raise ValidationException(f"Invalid status: {status_filter}")

    if research_area:
        query = query.where(Paper.research_area.ilike(f"%{research_area}%"))

    if search:
        search_filter = or_(
            Paper.title.ilike(f"%{search}%"),
            Paper.abstract.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # Add pagination
    query = query.offset(skip).limit(limit).order_by(Paper.updated_at.desc())

    result = await db.execute(query)
    papers = result.scalars().all()

    return [PaperListResponse.model_validate(paper) for paper in papers]


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
        paper_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get a specific paper by ID"""

    paper = await paper_service.get_paper_by_id(db, paper_id)
    if not paper:
        raise NotFoundException("Paper")

    # Check if user can view this paper
    if not paper.is_viewable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to view this paper")

    return PaperResponse.model_validate(paper)


@router.patch("/{paper_id}", response_model=PaperResponse)
async def update_paper(
        paper_id: str,
        paper_updates: PaperUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Update a paper"""

    paper = await paper_service.get_paper_by_id(db, paper_id)
    if not paper:
        raise NotFoundException("Paper")

    # Check if user can edit this paper
    if not paper.is_editable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to edit this paper")

    updated_paper = await paper_service.update_paper(
        db=db,
        paper_id=paper_id,
        updates=paper_updates
    )

    return PaperResponse.model_validate(updated_paper)


@router.delete("/{paper_id}")
async def delete_paper(
        paper_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Delete a paper"""

    paper = await paper_service.get_paper_by_id(db, paper_id)
    if not paper:
        raise NotFoundException("Paper")

    # Only owner can delete papers
    if str(paper.owner_id) != str(current_user.id):
        raise AuthorizationException("You can only delete your own papers")

    await paper_service.delete_paper(db=db, paper_id=paper_id)

    return {"message": "Paper deleted successfully"}


@router.post("/{paper_id}/sections", response_model=PaperSectionResponse)
async def create_paper_section(
        paper_id: str,
        section_data: PaperSectionCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Add a new section to a paper"""

    paper = await paper_service.get_paper_by_id(db, paper_id)
    if not paper:
        raise NotFoundException("Paper")

    if not paper.is_editable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to edit this paper")

    section = await paper_service.create_section(
        db=db,
        paper_id=paper_id,
        section_data=section_data
    )

    return PaperSectionResponse.model_validate(section)


@router.patch("/{paper_id}/sections/{section_id}", response_model=PaperSectionResponse)
async def update_paper_section(
        paper_id: str,
        section_id: str,
        section_updates: PaperSectionUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Update a paper section"""

    paper = await paper_service.get_paper_by_id(db, paper_id)
    if not paper:
        raise NotFoundException("Paper")

    if not paper.is_editable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to edit this paper")

    section = await paper_service.update_section(
        db=db,
        section_id=section_id,
        updates=section_updates
    )

    return PaperSectionResponse.model_validate(section)


@router.delete("/{paper_id}/sections/{section_id}")
async def delete_paper_section(
        paper_id: str,
        section_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Delete a paper section"""

    paper = await paper_service.get_paper_by_id(db, paper_id)
    if not paper:
        raise NotFoundException("Paper")

    if not paper.is_editable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to edit this paper")

    await paper_service.delete_section(db=db, section_id=section_id)

    return {"message": "Section deleted successfully"}


@router.post("/{paper_id}/duplicate", response_model=PaperResponse)
async def duplicate_paper(
        paper_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Create a duplicate of an existing paper"""

    original_paper = await paper_service.get_paper_by_id(db, paper_id)
    if not original_paper:
        raise NotFoundException("Paper")

    if not original_paper.is_viewable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to view this paper")

    # Check if user can create papers
    if not current_user.can_create_papers():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Paper creation limit reached for your subscription plan"
        )

    duplicated_paper = await paper_service.duplicate_paper(
        db=db,
        original_paper_id=paper_id,
        new_owner_id=current_user.id
    )

    return PaperResponse.model_validate(duplicated_paper)


@router.get("/stats/summary")
async def get_papers_summary(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get summary statistics for user's papers"""

    # Count papers by status
    status_query = select(
        Paper.status,
        func.count(Paper.id).label('count')
    ).where(
        Paper.owner_id == current_user.id
    ).group_by(Paper.status)

    status_result = await db.execute(status_query)
    status_counts = {row.status: row.count for row in status_result}

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

    return {
        "total_papers": sum(status_counts.values()),
        "status_breakdown": status_counts,
        "total_words": int(total_words),
        "average_progress": round(float(avg_progress), 2),
        "published_papers": status_counts.get(PaperStatus.PUBLISHED, 0),
        "active_papers": status_counts.get(PaperStatus.IN_PROGRESS, 0) +
                         status_counts.get(PaperStatus.DRAFT, 0)
    }