
"""
Collaboration Endpoints (app/api/v1/endpoints/collaboration.py)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.paper import CollaboratorInvite, CollaboratorResponse
from app.schemas.collaboration import (
    CommentCreate, CommentResponse, VersionCreate, VersionResponse,
    InvitationResponse
)
from app.services.collaboration_service import collaboration_service
from app.core.exceptions import NotFoundException, AuthorizationException

router = APIRouter()


@router.post("/papers/{paper_id}/invite", response_model=InvitationResponse)
async def invite_collaborator(
        paper_id: str,
        invite_data: CollaboratorInvite,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Invite collaborator to paper"""

    try:
        invitation = await collaboration_service.invite_collaborator(
            db=db,
            paper_id=paper_id,
            inviter_id=current_user.id,
            invite_data=invite_data
        )

        return InvitationResponse.from_orm(invitation)

    except (NotFoundException, AuthorizationException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/invitations/{token}/accept")
async def accept_invitation(
        token: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Accept collaboration invitation"""

    try:
        invitation = await collaboration_service.accept_invitation(
            db=db,
            token=token,
            user_id=current_user.id
        )

        return {"message": "Invitation accepted successfully", "paper_id": str(invitation.paper_id)}

    except (NotFoundException, ValidationException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/papers/{paper_id}/comments", response_model=CommentResponse)
async def add_comment(
        paper_id: str,
        comment_data: CommentCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Add comment to paper"""

    try:
        comment = await collaboration_service.add_comment(
            db=db,
            paper_id=paper_id,
            user_id=current_user.id,
            content=comment_data.content,
            section_id=comment_data.section_id,
            parent_id=comment_data.parent_id,
            comment_type=comment_data.comment_type
        )

        return CommentResponse.from_orm(comment)

    except AuthorizationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/papers/{paper_id}/comments", response_model=List[CommentResponse])
async def get_paper_comments(
        paper_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        section_id: Optional[str] = Query(None),
        resolved: Optional[bool] = Query(None)
):
    """Get paper comments"""

    from sqlalchemy import select, and_
    from app.models.collaboration import PaperComment
    from app.models.paper import Paper

    # Verify access
    paper = await db.get(Paper, paper_id)
    if not paper or not paper.is_viewable_by(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Build query
    query = select(PaperComment).where(PaperComment.paper_id == paper_id)

    if section_id:
        query = query.where(PaperComment.section_id == section_id)

    if resolved is not None:
        query = query.where(PaperComment.is_resolved == resolved)

    query = query.order_by(PaperComment.created_at.desc())

    result = await db.execute(query)
    comments = result.scalars().all()

    return [CommentResponse.from_orm(comment) for comment in comments]


@router.patch("/comments/{comment_id}/resolve")
async def resolve_comment(
        comment_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Resolve a comment"""

    try:
        comment = await collaboration_service.resolve_comment(
            db=db,
            comment_id=comment_id,
            user_id=current_user.id
        )

        return {"message": "Comment resolved", "resolved_at": comment.resolved_at.isoformat()}

    except (NotFoundException, AuthorizationException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/papers/{paper_id}/versions", response_model=VersionResponse)
async def create_paper_version(
        paper_id: str,
        version_data: VersionCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Create paper version"""

    try:
        version = await collaboration_service.create_version(
            db=db,
            paper_id=paper_id,
            user_id=current_user.id,
            changes_summary=version_data.changes_summary,
            is_major=version_data.is_major_version
        )

        return VersionResponse.from_orm(version)

    except (NotFoundException, AuthorizationException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/papers/{paper_id}/versions", response_model=List[VersionResponse])
async def get_paper_versions(
        paper_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        limit: int = Query(10, le=50)
):
    """Get paper versions"""

    from sqlalchemy import select
    from app.models.collaboration import PaperVersion
    from app.models.paper import Paper

    # Verify access
    paper = await db.get(Paper, paper_id)
    if not paper or not paper.is_viewable_by(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    query = select(PaperVersion).where(
        PaperVersion.paper_id == paper_id
    ).order_by(PaperVersion.created_at.desc()).limit(limit)

    result = await db.execute(query)
    versions = result.scalars().all()

    return [VersionResponse.from_orm(version) for version in versions]

