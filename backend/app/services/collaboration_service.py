"""
Collaboration Service (app/services/collaboration_service.py)
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import secrets

from app.models.user import User
from app.models.paper import Paper
from app.models.collaboration import (
    CollaborationInvite, PaperComment, PaperVersion, CollaborationSession,
    CollaborationRole, InvitationStatus
)
from app.schemas.paper import CollaboratorInvite
from app.core.exceptions import NotFoundException, ValidationException, AuthorizationException
from app.utils.email import email_service


class CollaborationService:
    """Service for collaboration management"""

    async def invite_collaborator(
            self,
            db: AsyncSession,
            paper_id: str,
            inviter_id: str,
            invite_data: CollaboratorInvite
    ) -> CollaborationInvite:
        """Send collaboration invitation"""

        # Verify paper exists and user has permission
        paper = await db.get(Paper, paper_id)
        if not paper:
            raise NotFoundException("Paper")

        if str(paper.owner_id) != inviter_id:
            raise AuthorizationException("Only paper owner can invite collaborators")

        # Check if invitation already exists
        existing = await db.execute(
            select(CollaborationInvite).where(
                and_(
                    CollaborationInvite.paper_id == paper_id,
                    CollaborationInvite.email == invite_data.email,
                    CollaborationInvite.status == InvitationStatus.PENDING
                )
            )
        )

        if existing.scalar_one_or_none():
            raise ValidationException("Invitation already pending for this email")

        # Create invitation
        invitation = CollaborationInvite(
            paper_id=paper_id,
            email=invite_data.email,
            role=invite_data.role,
            message=invite_data.message,
            invited_by_id=inviter_id,
            expires_at=datetime.utcnow() + timedelta(days=7),
            token=secrets.token_urlsafe(32)
        )

        db.add(invitation)
        await db.commit()

        # Send invitation email
        await self._send_invitation_email(invitation, paper)

        return invitation

    async def accept_invitation(
            self,
            db: AsyncSession,
            token: str,
            user_id: str
    ) -> CollaborationInvite:
        """Accept collaboration invitation"""

        invitation = await db.execute(
            select(CollaborationInvite).where(CollaborationInvite.token == token)
        )
        invitation = invitation.scalar_one_or_none()

        if not invitation:
            raise NotFoundException("Invitation")

        if invitation.status != InvitationStatus.PENDING:
            raise ValidationException("Invitation is not pending")

        if invitation.expires_at < datetime.utcnow():
            invitation.status = InvitationStatus.EXPIRED
            await db.commit()
            raise ValidationException("Invitation has expired")

        # Accept invitation
        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = datetime.utcnow()
        invitation.invited_user_id = user_id

        # Add to paper collaborators
        from app.models.paper import PaperCollaborator

        collaborator = PaperCollaborator(
            paper_id=invitation.paper_id,
            user_id=user_id,
            role=invitation.role.value,
            status="accepted",
            invited_by_id=invitation.invited_by_id
        )
        collaborator.accept_invitation()

        db.add(collaborator)
        await db.commit()

        return invitation

    async def add_comment(
            self,
            db: AsyncSession,
            paper_id: str,
            user_id: str,
            content: str,
            section_id: Optional[str] = None,
            parent_id: Optional[str] = None,
            comment_type: str = "general"
    ) -> PaperComment:
        """Add comment to paper"""

        # Verify access
        paper = await db.get(Paper, paper_id)
        if not paper or not paper.is_viewable_by(user_id):
            raise AuthorizationException("Cannot comment on this paper")

        comment = PaperComment(
            paper_id=paper_id,
            author_id=user_id,
            content=content,
            section_id=section_id,
            parent_id=parent_id,
            comment_type=comment_type,
            thread_id=parent_id if parent_id else None  # Will be set to own ID if root comment
        )

        db.add(comment)
        await db.flush()

        # Set thread_id for root comments
        if not parent_id:
            comment.thread_id = comment.id

        await db.commit()
        return comment

    async def resolve_comment(
            self,
            db: AsyncSession,
            comment_id: str,
            user_id: str
    ) -> PaperComment:
        """Resolve a comment"""

        comment = await db.get(PaperComment, comment_id)
        if not comment:
            raise NotFoundException("Comment")

        # Verify permission (author or paper owner)
        paper = await db.get(Paper, comment.paper_id)
        if not (str(comment.author_id) == user_id or str(paper.owner_id) == user_id):
            raise AuthorizationException("Cannot resolve this comment")

        comment.is_resolved = True
        comment.resolved_at = datetime.utcnow()
        comment.resolved_by_id = user_id

        await db.commit()
        return comment

    async def create_version(
            self,
            db: AsyncSession,
            paper_id: str,
            user_id: str,
            changes_summary: str,
            is_major: bool = False
    ) -> PaperVersion:
        """Create paper version"""

        paper = await db.get(Paper, paper_id)
        if not paper or not paper.is_editable_by(user_id):
            raise AuthorizationException("Cannot create version for this paper")

        # Get current version number
        last_version = await db.execute(
            select(PaperVersion)
            .where(PaperVersion.paper_id == paper_id)
            .order_by(PaperVersion.created_at.desc())
            .limit(1)
        )
        last_version = last_version.scalar_one_or_none()

        # Calculate new version number
        if last_version:
            major, minor = map(int, last_version.version_number.split('.'))
            if is_major:
                version_number = f"{major + 1}.0"
            else:
                version_number = f"{major}.{minor + 1}"
        else:
            version_number = "1.0"

        # Create content snapshot
        content_snapshot = {
            "title": paper.title,
            "abstract": paper.abstract,
            "sections": [
                {
                    "id": str(section.id),
                    "title": section.title,
                    "content": section.content,
                    "status": section.status.value,
                    "order": section.order
                }
                for section in paper.sections
            ],
            "metadata": {
                "status": paper.status.value,
                "progress": paper.progress,
                "word_count": paper.current_word_count,
                "research_area": paper.research_area,
                "tags": paper.tags,
                "co_authors": paper.co_authors
            }
        }

        version = PaperVersion(
            paper_id=paper_id,
            version_number=version_number,
            title=paper.title,
            abstract=paper.abstract,
            content_snapshot=content_snapshot,
            changes_summary=changes_summary,
            is_major_version=is_major,
            created_by_id=user_id
        )

        db.add(version)
        await db.commit()
        return version

    async def _send_invitation_email(
            self,
            invitation: CollaborationInvite,
            paper: Paper
    ):
        """Send invitation email"""

        accept_url = f"https://yourapp.com/collaborate/accept?token={invitation.token}"

        subject = f"Collaboration Invitation: {paper.title}"
        body = f"""
        You've been invited to collaborate on the research paper "{paper.title}".

        Role: {invitation.role.value.title()}

        {invitation.message or ""}

        To accept this invitation, click here: {accept_url}

        This invitation expires on {invitation.expires_at.strftime('%Y-%m-%d')}.
        """

        await email_service.send_email([invitation.email], subject, body)


# Create service instance
collaboration_service = CollaborationService()

