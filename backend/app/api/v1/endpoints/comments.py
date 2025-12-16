"""
Comment API endpoints for collaborative paper writing
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.paper import Paper, PaperSection
from app.models.comment import PaperComment
from app.models.notification import NotificationType
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse, CommentListResponse
from app.core.exceptions import NotFoundException, AuthorizationException, ValidationException
from app.services.websocket_service import connection_manager
from app.services.email_service import email_service
from app.api.v1.endpoints.notifications import create_notification

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{paper_id}/comments", response_model=CommentResponse)
async def create_comment(
        paper_id: str,
        comment_data: CommentCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Create a new comment on a paper section

    Sends real-time notifications to all collaborators
    """
    logger.info(f"📝 Creating comment on paper {paper_id} by user {current_user.id}")

    # Get paper with collaborators
    query = (
        select(Paper)
        .options(selectinload(Paper.collaborators))
        .where(Paper.id == paper_id)
    )
    result = await db.execute(query)
    paper = result.scalar_one_or_none()

    if not paper:
        raise NotFoundException("Paper")

    # Check if user can comment (must be owner or collaborator with comment permission)
    if not paper.is_viewable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to comment on this paper")

    # Verify section exists and belongs to this paper
    section_query = select(PaperSection).where(
        and_(
            PaperSection.id == comment_data.section_id,
            PaperSection.paper_id == paper_id
        )
    )
    section_result = await db.execute(section_query)
    section = section_result.scalar_one_or_none()

    if not section:
        raise NotFoundException("Section")

    # Create comment
    comment = PaperComment(
        content=comment_data.content,
        paper_id=paper_id,
        section_id=comment_data.section_id,
        author_id=current_user.id,
        selection_start=comment_data.selection_start,
        selection_end=comment_data.selection_end,
        selected_text=comment_data.selected_text,
        parent_comment_id=comment_data.parent_comment_id
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment, ["author"])

    logger.info(f"✅ Comment created: {comment.id}")

    # Send real-time notifications to all collaborators (except the author)
    collaborator_ids = [str(paper.owner_id)]
    for collab in paper.collaborators:
        if collab.status == "accepted":
            collaborator_ids.append(str(collab.user_id))

    # Remove the comment author from notification list
    notification_recipients = [uid for uid in collaborator_ids if uid != str(current_user.id)]

    for user_id in notification_recipients:
        # Persist notification to database first (so it doesn't disappear)
        db_notification = await create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.COMMENT_ADDED,
            title="New Comment",
            message=f"{current_user.name} commented on '{section.title}': {comment.content[:100]}{'...' if len(comment.content) > 100 else ''}",
            link=f"/papers/{paper_id}"
        )

        # Send WebSocket notification (real-time) with database notification ID
        await connection_manager.send_notification(
            user_id=user_id,
            notification_type="comment",
            title="New Comment",
            message=f"{current_user.name} commented on '{section.title}': {comment.content[:100]}...",
            data={
                "paper_id": str(paper_id),
                "section_id": str(comment_data.section_id),
                "comment_id": str(comment.id),
                "author_name": current_user.name,
                "section_title": section.title,
                "notification_id": str(db_notification.id)  # Include DB notification ID
            }
        )

        # Send email notification if user has email notifications enabled
        try:
            # Get user to check notification preferences
            from uuid import UUID
            user_result = await db.execute(select(User).where(User.id == UUID(user_id)))
            recipient_user = user_result.scalar_one_or_none()

            if recipient_user and recipient_user.should_send_email_notification('collaboration'):
                await email_service.send_comment_notification(
                    to_email=recipient_user.email,
                    to_name=recipient_user.name,
                    author_name=current_user.name,
                    paper_title=paper.title,
                    comment_content=comment.content,
                    paper_url=f"http://localhost:3000/papers/{paper_id}"
                )
                logger.info(f"📧 Email notification sent to {recipient_user.email}")
        except Exception as e:
            logger.error(f"❌ Failed to send email notification: {str(e)}")

    logger.info(f"📤 Sent and persisted notifications to {len(notification_recipients)} collaborators")

    return CommentResponse.model_validate(comment.to_dict())


@router.get("/{paper_id}/comments", response_model=CommentListResponse)
async def get_paper_comments(
        paper_id: str,
        section_id: str = None,
        include_resolved: bool = True,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Get all comments for a paper or specific section
    """
    # Verify paper exists and user has access (eagerly load collaborators to avoid lazy loading)
    paper_query = (
        select(Paper)
        .options(selectinload(Paper.collaborators))
        .where(Paper.id == paper_id)
    )
    paper_result = await db.execute(paper_query)
    paper = paper_result.scalar_one_or_none()

    if not paper:
        raise NotFoundException("Paper")

    if not paper.is_viewable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to view this paper")

    # Build query for comments
    query = (
        select(PaperComment)
        .options(selectinload(PaperComment.author))
        .options(selectinload(PaperComment.resolved_by))
        .options(selectinload(PaperComment.replies))
        .where(PaperComment.paper_id == paper_id)
    )

    # Filter by section if specified
    if section_id:
        query = query.where(PaperComment.section_id == section_id)

    # Filter resolved comments
    if not include_resolved:
        query = query.where(PaperComment.is_resolved == False)

    # Only get top-level comments (not replies)
    query = query.where(PaperComment.parent_comment_id == None)

    # Order by creation date
    query = query.order_by(PaperComment.created_at.desc())

    result = await db.execute(query)
    comments = result.scalars().all()

    return CommentListResponse(
        comments=[CommentResponse.model_validate(c.to_dict()) for c in comments],
        total=len(comments),
        section_id=section_id
    )


@router.patch("/{paper_id}/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
        paper_id: str,
        comment_id: str,
        comment_update: CommentUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Update a comment (edit content or resolve/unresolve)
    """
    # Get comment
    query = (
        select(PaperComment)
        .options(selectinload(PaperComment.author))
        .where(
            and_(
                PaperComment.id == comment_id,
                PaperComment.paper_id == paper_id
            )
        )
    )
    result = await db.execute(query)
    comment = result.scalar_one_or_none()

    if not comment:
        raise NotFoundException("Comment")

    # Only author can edit content, but any collaborator can resolve
    if comment_update.content is not None:
        if str(comment.author_id) != str(current_user.id):
            raise AuthorizationException("You can only edit your own comments")
        comment.content = comment_update.content

    if comment_update.is_resolved is not None:
        if comment_update.is_resolved:
            comment.resolve(str(current_user.id))
        else:
            comment.unresolve()

    await db.commit()
    await db.refresh(comment, ["author", "resolved_by"])

    # Send WebSocket notification to all collaborators when comment is resolved/unresolved
    if comment_update.is_resolved is not None:
        # Get paper with collaborators
        paper_query = (
            select(Paper)
            .options(selectinload(Paper.collaborators))
            .where(Paper.id == paper_id)
        )
        paper_result = await db.execute(paper_query)
        paper = paper_result.scalar_one_or_none()

        # Get section for notification message
        section_query = select(PaperSection).where(PaperSection.id == comment.section_id)
        section_result = await db.execute(section_query)
        section = section_result.scalar_one_or_none()

        if paper and section:
            # Build list of collaborators
            collaborator_ids = [str(paper.owner_id)]
            for collab in paper.collaborators:
                if collab.status == "accepted":
                    collaborator_ids.append(str(collab.user_id))

            # Remove the person who resolved it from notification list
            notification_recipients = [uid for uid in collaborator_ids if uid != str(current_user.id)]

            action = "resolved" if comment_update.is_resolved else "reopened"
            for user_id in notification_recipients:
                # Persist notification to database first (so it doesn't disappear)
                # TODO: Change to COMMENT_UPDATED after running database migration
                db_notification = await create_notification(
                    db=db,
                    user_id=user_id,
                    type=NotificationType.COMMENT_ADDED,  # Temporary: using COMMENT_ADDED until DB migration
                    title=f"Comment {action}",
                    message=f"{current_user.name} {action} a comment on '{section.title}'",
                    link=f"/papers/{paper_id}"
                )

                # Send WebSocket notification (real-time) with database notification ID
                await connection_manager.send_notification(
                    user_id=user_id,
                    notification_type="comment_updated",
                    title=f"Comment {action}",
                    message=f"{current_user.name} {action} a comment on '{section.title}'",
                    data={
                        "paper_id": str(paper_id),
                        "section_id": str(comment.section_id),
                        "comment_id": str(comment_id),
                        "author_name": current_user.name,
                        "section_title": section.title,
                        "action": action,
                        "is_resolved": comment_update.is_resolved,
                        "notification_id": str(db_notification.id)  # Include DB notification ID
                    }
                )

            logger.info(f"📤 Sent and persisted {action} notifications to {len(notification_recipients)} collaborators")

    return CommentResponse.model_validate(comment.to_dict())


@router.delete("/{paper_id}/comments/{comment_id}")
async def delete_comment(
        paper_id: str,
        comment_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Delete a comment (only by author or paper owner)
    """
    # Get comment
    query = select(PaperComment).where(
        and_(
            PaperComment.id == comment_id,
            PaperComment.paper_id == paper_id
        )
    )
    result = await db.execute(query)
    comment = result.scalar_one_or_none()

    if not comment:
        raise NotFoundException("Comment")

    # Get paper to check ownership
    paper_query = select(Paper).where(Paper.id == paper_id)
    paper_result = await db.execute(paper_query)
    paper = paper_result.scalar_one_or_none()

    # Only comment author or paper owner can delete
    if str(comment.author_id) != str(current_user.id) and str(paper.owner_id) != str(current_user.id):
        raise AuthorizationException("You can only delete your own comments or comments on your papers")

    await db.delete(comment)
    await db.commit()

    return {"message": "Comment deleted successfully"}


@router.get("/{paper_id}/sections/{section_id}/comments", response_model=CommentListResponse)
async def get_section_comments(
        paper_id: str,
        section_id: str,
        include_resolved: bool = True,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Get all comments for a specific section
    """
    return await get_paper_comments(
        paper_id=paper_id,
        section_id=section_id,
        include_resolved=include_resolved,
        current_user=current_user,
        db=db
    )
