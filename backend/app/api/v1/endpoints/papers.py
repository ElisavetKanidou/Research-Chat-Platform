"""
Paper management CRUD API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

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
from app.services.paper_export_service import paper_export_service
from app.schemas.paper import PaperAISettingsUpdate, PaperAISettingsResponse

router = APIRouter()


@router.post("/", response_model=PaperResponse)
async def create_paper(
        paper_data: PaperCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Create a new research paper"""

    # ✅ FIX: Count papers without lazy loading
    from sqlalchemy import func

    result = await db.execute(
        select(func.count(Paper.id))
        .where(Paper.owner_id == current_user.id)
    )
    paper_count = result.scalar() or 0

    # Check subscription limit (5 papers for free tier)
    if paper_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have reached the free tier limit of 5 papers. Upgrade your plan to create more papers."
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
    """
    Get user's papers with optional filtering and pagination
    Returns papers where user is EITHER owner OR collaborator
    """

    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"📄 Fetching papers for user {current_user.id}")

    # Import selectinload for loading collaborators
    from sqlalchemy.orm import selectinload

    # ✅ STEP 1: Get papers where user is OWNER
    owned_query = select(Paper).where(Paper.owner_id == current_user.id).options(
        selectinload(Paper.collaborators)
    )

    # Apply filters to owned papers
    if status_filter:
        try:
            status_enum = PaperStatus(status_filter)
            owned_query = owned_query.where(Paper.status == status_enum)
        except ValueError:
            raise ValidationException(f"Invalid status: {status_filter}")

    if research_area:
        owned_query = owned_query.where(Paper.research_area.ilike(f"%{research_area}%"))

    if search:
        search_filter = or_(
            Paper.title.ilike(f"%{search}%"),
            Paper.abstract.ilike(f"%{search}%")
        )
        owned_query = owned_query.where(search_filter)

    owned_query = owned_query.order_by(Paper.updated_at.desc())

    owned_result = await db.execute(owned_query)
    owned_papers = owned_result.scalars().all()

    logger.info(f"👑 User owns {len(owned_papers)} papers")

    # ✅ STEP 2: Get papers where user is COLLABORATOR
    from app.models.paper import PaperCollaborator

    collab_query = select(PaperCollaborator).where(
        and_(
            PaperCollaborator.user_id == current_user.id,
            PaperCollaborator.status == "accepted"
        )
    )

    collab_result = await db.execute(collab_query)
    collaborations = collab_result.scalars().all()

    logger.info(f"🤝 User is collaborator on {len(collaborations)} papers")

    # Get the actual papers from collaborations
    collab_paper_ids = [c.paper_id for c in collaborations]

    collab_papers = []
    if collab_paper_ids:
        collab_papers_query = select(Paper).where(
            Paper.id.in_(collab_paper_ids)
        ).options(
            selectinload(Paper.collaborators)
        )

        # Apply same filters to collaborative papers
        if status_filter:
            collab_papers_query = collab_papers_query.where(Paper.status == status_enum)
        if research_area:
            collab_papers_query = collab_papers_query.where(Paper.research_area.ilike(f"%{research_area}%"))
        if search:
            collab_papers_query = collab_papers_query.where(search_filter)

        collab_papers_query = collab_papers_query.order_by(Paper.updated_at.desc())

        collab_papers_result = await db.execute(collab_papers_query)
        collab_papers = collab_papers_result.scalars().all()

        logger.info(f"📋 Fetched {len(collab_papers)} collaborative papers")

    # ✅ STEP 3: Combine both lists
    all_papers = list(owned_papers) + list(collab_papers)

    # Remove duplicates (if user is both owner and collaborator)
    seen_ids = set()
    unique_papers = []
    for paper in all_papers:
        if paper.id not in seen_ids:
            seen_ids.add(paper.id)
            unique_papers.append(paper)

    # Sort by updated_at
    unique_papers.sort(key=lambda p: p.updated_at, reverse=True)

    # Apply pagination
    paginated_papers = unique_papers[skip:skip + limit]

    logger.info(f"✅ Returning {len(paginated_papers)} papers (total: {len(unique_papers)})")

    # Convert to PaperListResponse with collaborator count
    response_papers = []
    for paper in paginated_papers:
        # Count accepted collaborators
        collab_count = len([c for c in (paper.collaborators or []) if c.status == "accepted"])

        logger.info(f"📊 Paper '{paper.title[:30]}': {len(paper.collaborators or [])} total collabs, {collab_count} accepted")

        paper_dict = {
            "id": str(paper.id),
            "title": paper.title,
            "status": paper.status,
            "progress": paper.progress,
            "created_at": paper.created_at,
            "updated_at": paper.updated_at,
            "current_word_count": paper.current_word_count,
            "target_word_count": paper.target_word_count,
            "research_area": paper.research_area,
            "tags": paper.tags or [],
            "is_public": paper.is_public,
            "deadline": paper.deadline,
            "collaborator_count": collab_count
        }
        response_papers.append(PaperListResponse.model_validate(paper_dict))

    return response_papers

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

    # Build response with collaborator count
    paper_dict = {
        "id": str(paper.id),
        "title": paper.title,
        "status": paper.status,
        "progress": paper.progress,
        "created_at": paper.created_at,
        "updated_at": paper.updated_at,
        "current_word_count": paper.current_word_count,
        "target_word_count": paper.target_word_count,
        "research_area": paper.research_area,
        "tags": paper.tags or [],
        "is_public": paper.is_public,
        "deadline": paper.deadline,
        "collaborator_count": len([c for c in (paper.collaborators or []) if c.status == "accepted"]),
        "abstract": paper.abstract,
        "sections": paper.sections,
        "owner_id": str(paper.owner_id),
        "doi": paper.doi,
        "journal": paper.journal,
        "publication_date": paper.publication_date,
        "citation_count": paper.citation_count or 0
    }

    return PaperResponse.model_validate(paper_dict)


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

    # Check if user is a viewer
    user_role = None
    if str(paper.owner_id) == str(current_user.id):
        user_role = "owner"
    else:
        for collab in paper.collaborators:
            if str(collab.user_id) == str(current_user.id):
                user_role = collab.role
                break

    if user_role == "viewer":
        raise AuthorizationException(
            "Viewers cannot edit paper content. Please contact the paper owner to upgrade your role to Editor or Co-author."
        )

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


"""
Paper AI Settings Endpoints - ADD TO app/api/v1/endpoints/papers.py
Add these at the end of the file
"""


# Add these imports at the top:
# from app.schemas.paper import PaperAISettingsUpdate, PaperAISettingsResponse

"""
Simplified Paper AI Settings Endpoints - NO GLOBAL SETTINGS
Add to app/api/v1/endpoints/papers.py
"""


# ==================== SIMPLIFIED PAPER AI SETTINGS ====================

@router.get("/{paper_id}/ai-settings")
async def get_paper_ai_settings(
        paper_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get AI settings for a specific paper"""
    paper = await paper_service.get_paper_by_id(db, paper_id)
    if not paper:
        raise NotFoundException("Paper")

    if not paper.is_viewable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to view this paper")

    # Get paper's AI settings (returns snake_case from DB)
    settings = paper.get_ai_settings()

    # ✅ Convert snake_case to camelCase for frontend
    camel_case_settings = {
        "labLevel": settings.get("lab_level", 7),
        "personalLevel": settings.get("personal_level", 8),
        "globalLevel": settings.get("global_level", 5),
        "writingStyle": settings.get("writing_style", "academic"),
        "contextDepth": settings.get("context_depth", "moderate"),
        "researchFocus": settings.get("research_focus", []),
        "suggestionsEnabled": settings.get("suggestions_enabled", True)
    }

    print(f"📤 [GET /{paper_id}/ai-settings] Returning settings:", camel_case_settings)

    return {
        "paperId": str(paper.id),
        "settings": camel_case_settings
    }


@router.patch("/{paper_id}/ai-settings")
async def update_paper_ai_settings(
        paper_id: str,
        settings_update: dict,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Update AI settings for a specific paper"""
    paper = await paper_service.get_paper_by_id(db, paper_id)
    if not paper:
        raise NotFoundException("Paper")

    if not paper.is_editable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to edit this paper")

    print(f"🤖 [PATCH /{paper_id}/ai-settings] Received settings:", settings_update)

    # ✅ Convert camelCase from frontend to snake_case for DB
    snake_case_settings = {
        "lab_level": settings_update.get("labLevel"),
        "personal_level": settings_update.get("personalLevel"),
        "global_level": settings_update.get("globalLevel"),
        "writing_style": settings_update.get("writingStyle"),
        "context_depth": settings_update.get("contextDepth"),
        "research_focus": settings_update.get("researchFocus"),  # ✅ Array should pass through
        "suggestions_enabled": settings_update.get("suggestionsEnabled")
    }

    # Remove None values
    snake_case_settings = {k: v for k, v in snake_case_settings.items() if v is not None}

    print(f"📝 Converting to snake_case:", snake_case_settings)
    print(f"🔍 research_focus type: {type(snake_case_settings.get('research_focus'))}")
    print(f"🔍 research_focus value: {snake_case_settings.get('research_focus')}")

    # Update paper's AI settings
    paper.update_ai_settings(snake_case_settings)

    await db.commit()
    await db.refresh(paper)

    print(f"💾 After save - paper.ai_settings:", paper.ai_settings)

    # Get updated settings and convert back to camelCase
    updated_settings = paper.get_ai_settings()
    camel_case_settings = {
        "labLevel": updated_settings.get("lab_level", 7),
        "personalLevel": updated_settings.get("personal_level", 8),
        "globalLevel": updated_settings.get("global_level", 5),
        "writingStyle": updated_settings.get("writing_style", "academic"),
        "contextDepth": updated_settings.get("context_depth", "moderate"),
        "researchFocus": updated_settings.get("research_focus", []),  # ✅ Return array
        "suggestionsEnabled": updated_settings.get("suggestions_enabled", True)
    }

    print(f"✅ Paper AI settings updated successfully")
    print(f"📤 Returning to frontend:", camel_case_settings)

    return {
        "paperId": str(paper.id),
        "settings": camel_case_settings
    }


@router.get("/{paper_id}/export")
async def export_paper(
        paper_id: str,
        format: str = Query("pdf", description="Export format: pdf, word, or latex"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Export paper in specified format (PDF, Word, or LaTeX)

    Args:
        paper_id: Paper ID
        format: Export format (pdf, word, latex)

    Returns:
        File download response with appropriate content type
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"📤 Export request for paper {paper_id} in format: {format}")

    # Validate format
    valid_formats = ["pdf", "word", "latex"]
    if format.lower() not in valid_formats:
        raise ValidationException(
            f"Invalid export format: {format}. Must be one of: {', '.join(valid_formats)}"
        )

    # Get paper with sections, collaborators, and owner eagerly loaded
    from app.models.paper import PaperCollaborator
    query = (
        select(Paper)
        .options(
            selectinload(Paper.sections),
            selectinload(Paper.collaborators).selectinload(PaperCollaborator.user),
            selectinload(Paper.owner)
        )
        .where(Paper.id == paper_id)
    )
    result = await db.execute(query)
    paper = result.scalar_one_or_none()

    if not paper:
        raise NotFoundException("Paper")

    # Check permissions
    if not paper.is_viewable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to view this paper")

    # Generate export based on format
    try:
        if format.lower() == "pdf":
            content = paper_export_service.export_to_pdf(paper)
            media_type = "application/pdf"
            extension = "pdf"
        elif format.lower() == "word":
            content = paper_export_service.export_to_word(paper)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            extension = "docx"
        else:  # latex
            content = paper_export_service.export_to_latex(paper)
            media_type = "application/x-latex"
            extension = "tex"

        # Create safe filename
        safe_title = "".join(c for c in paper.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        filename = f"{safe_title}.{extension}"

        logger.info(f"✅ Export completed: {filename}")

        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        logger.error(f"❌ Export failed for paper {paper_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export paper: {str(e)}"
        )