"""
Collaboration API Endpoints - COMPLETE VERSION
backend/app/api/v1/endpoints/collaborations.py
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, timedelta
from uuid import UUID
import secrets
import logging

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.paper import Paper, PaperCollaborator
from app.models.collaboration import CollaborationInvite, InvitationStatus, CollaborationRole

router = APIRouter()
logger = logging.getLogger(__name__)

# ==================== SCHEMAS ====================
from pydantic import BaseModel, EmailStr


class InviteRequest(BaseModel):
    email: EmailStr
    role: str  # 'viewer', 'editor', 'co-author'
    message: str = ""


class BulkInviteRequest(BaseModel):
    invites: List[InviteRequest]
    paper_id: Optional[str] = None
    paper_title: Optional[str] = None


class CollaboratorInfo(BaseModel):
    id: str
    name: str
    email: str
    role: str
    status: str
    joinedAt: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.post("/invite")
async def send_invitations(
        request: BulkInviteRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Send collaboration invitations
    - If paper_id provided: Invite to specific paper
    - If no paper_id: General platform invitation
    """

    logger.info(f"📧 User {current_user.id} sending {len(request.invites)} invitations")

    if request.paper_id:
        # Verify paper exists and user owns it
        paper = await db.get(Paper, UUID(request.paper_id))
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        if str(paper.owner_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Only paper owner can invite collaborators")

        logger.info(f"📄 Inviting to paper: {paper.title}")

    sent_invites = []
    errors = []

    for invite in request.invites:
        try:
            # Check if user exists in system
            existing_user = await db.execute(
                select(User).where(User.email == invite.email)
            )
            existing_user = existing_user.scalar_one_or_none()

            # Check if invitation already exists
            query = select(CollaborationInvite).where(
                CollaborationInvite.email == invite.email,
                CollaborationInvite.status == InvitationStatus.PENDING
            )

            if request.paper_id:
                query = query.where(CollaborationInvite.paper_id == UUID(request.paper_id))

            existing_invite = await db.execute(query)

            if existing_invite.scalar_one_or_none():
                errors.append(f"{invite.email}: Already has pending invitation")
                continue

            # If paper-specific, check if already a collaborator
            if request.paper_id:
                existing_collab = await db.execute(
                    select(PaperCollaborator).where(
                        and_(
                            PaperCollaborator.paper_id == UUID(request.paper_id),
                            PaperCollaborator.user_id == existing_user.id if existing_user else None,
                            PaperCollaborator.status == "accepted"
                        )
                    )
                )

                if existing_collab.scalar_one_or_none():
                    errors.append(f"{invite.email}: Already a collaborator on this paper")
                    continue

            # ✅ AUTO-ACCEPT: If user exists, create collaboration directly
            if existing_user and request.paper_id:
                # Create PaperCollaborator directly (auto-accept)
                collaboration = PaperCollaborator(
                    paper_id=UUID(request.paper_id),
                    user_id=existing_user.id,
                    invited_by_id=current_user.id,
                    role=invite.role,
                    status="accepted",
                    can_edit=invite.role in ['co-author', 'editor'],
                    can_comment=True,
                    can_invite_others=invite.role == 'co-author',
                    created_at=datetime.utcnow()
                )
                db.add(collaboration)

                # Send collaborator_added notification
                from app.api.v1.endpoints.notifications import create_notification
                from app.models.notification import NotificationType

                await create_notification(
                    db=db,
                    user_id=str(existing_user.id),
                    type=NotificationType.COLLABORATOR_ADDED,
                    title="Added as Collaborator",
                    message=f"{current_user.name} added you as {invite.role} on '{paper.title}'",
                    link=f"/papers/{request.paper_id}"
                )

                logger.info(f"✅ Auto-accepted: Added {invite.email} as {invite.role}")
            else:
                # User doesn't exist - create invitation for later
                invitation = CollaborationInvite(
                    email=invite.email,
                    role=CollaborationRole(invite.role),
                    message=invite.message,
                    status=InvitationStatus.PENDING,
                    paper_id=UUID(request.paper_id) if request.paper_id else None,
                    invited_by_id=current_user.id,
                    invited_user_id=None,
                    expires_at=datetime.utcnow() + timedelta(days=7),
                    token=secrets.token_urlsafe(32)
                )
                db.add(invitation)

                logger.info(f"✅ Created invitation for {invite.email} (user not in system)")

            sent_invites.append({
                "email": invite.email,
                "role": invite.role,
                "existing_user": existing_user is not None,
                "auto_accepted": existing_user is not None and request.paper_id is not None
            })

            # TODO: Send email notification
            # await send_invitation_email(invitation, request.paper_title)

        except Exception as e:
            logger.error(f"❌ Failed to invite {invite.email}: {e}")
            errors.append(f"{invite.email}: {str(e)}")

    await db.commit()

    return {
        "success": True,
        "sent": len(sent_invites),
        "invites": sent_invites,
        "errors": errors
    }


@router.get("/search-friends")
async def search_friends(
        query: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Search for existing users to add as collaborators"""

    logger.info(f"🔍 Searching friends for user {current_user.id} with query: {query}")

    try:
        # ✅ SIMPLE SEARCH - All users except self
        all_users = await db.execute(
            select(User).where(
                and_(
                    User.id != current_user.id,  # Exclude self
                    or_(
                        User.name.ilike(f"%{query}%"),
                        User.email.ilike(f"%{query}%")
                    )
                )
            ).limit(10)
        )
        all_users = all_users.scalars().all()

        # Get user's papers to check past collaborators
        user_papers = await db.execute(
            select(Paper).where(Paper.owner_id == current_user.id)
        )
        user_papers = user_papers.scalars().all()
        paper_ids = [paper.id for paper in user_papers] if user_papers else []

        # Get past collaborator IDs
        past_collab_ids = set()
        if paper_ids:
            past_collabs = await db.execute(
                select(PaperCollaborator.user_id).where(
                    and_(
                        PaperCollaborator.paper_id.in_(paper_ids),
                        PaperCollaborator.status == "accepted"
                    )
                ).distinct()
            )
            past_collab_ids = {str(uid) for uid in past_collabs.scalars().all()}

        # Build response
        friends = [
            {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "is_past_collaborator": str(user.id) in past_collab_ids
            }
            for user in all_users
        ]

        logger.info(f"✅ Found {len(friends)} matching users")

        return {"friends": friends}

    except Exception as e:
        logger.error(f"❌ Error searching friends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/add-friend-to-paper")
async def add_friend_to_paper(
        paper_id: str = Body(...),
        user_id: str = Body(...),
        role: str = Body(default="co-author"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Add an existing friend/user directly to a paper (no invitation needed)
    """

    logger.info(f"➕ Adding user {user_id} to paper {paper_id} as {role}")

    try:
        # Verify paper exists and user owns it
        paper = await db.get(Paper, UUID(paper_id))
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        if str(paper.owner_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Only paper owner can add collaborators")

        # Verify friend exists
        friend = await db.get(User, UUID(user_id))
        if not friend:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if already a collaborator
        existing = await db.execute(
            select(PaperCollaborator).where(
                and_(
                    PaperCollaborator.paper_id == UUID(paper_id),
                    PaperCollaborator.user_id == UUID(user_id)
                )
            )
        )

        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User is already a collaborator on this paper")

        # ✅ FIX: Create collaboration with ALL required fields
        collaboration = PaperCollaborator(
            paper_id=UUID(paper_id),
            user_id=UUID(user_id),
            invited_by_id=current_user.id,  # ✅ ADDED
            role=role,
            status="accepted",
            can_edit=role in ['co-author', 'editor'],  # ✅ ADDED
            can_comment=True,  # ✅ ADDED
            can_invite_others=role == 'co-author',  # ✅ ADDED
            created_at=datetime.utcnow()
        )

        db.add(collaboration)

        await db.commit()
        await db.refresh(collaboration)

        # ✅ CREATE NOTIFICATION
        from app.api.v1.endpoints.notifications import create_notification
        from app.models.notification import NotificationType

        await create_notification(
            db=db,
            user_id=str(friend.id),
            type=NotificationType.COLLABORATOR_ADDED,
            title="Added as Co-author",
            message=f"{current_user.name} added you as a {role} on '{paper.title}'",
            link=f"/papers/{paper_id}"
        )

        logger.info(f"✅ Added {friend.name} to paper {paper.title}")

        return {
            "success": True,
            "collaborator": {
                "id": str(collaboration.id),
                "user_id": str(friend.id),
                "name": friend.name,
                "email": friend.email,
                "role": role,
                "status": "active",
                "joinedAt": collaboration.created_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error adding friend to paper: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/all")
async def get_all_collaborators(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Get all collaborators across all papers
    Returns BOTH:
    1. Users you added as collaborators (papers you own)
    2. Users who added YOU as collaborator (papers where you're a collaborator)
    """

    logger.info(f"📊 Fetching all collaborators for user {current_user.id}")

    try:
        # ✅ PART 1: Get papers where USER IS OWNER
        user_papers = await db.execute(
            select(Paper).where(Paper.owner_id == current_user.id)
        )
        user_papers = user_papers.scalars().all()
        paper_ids = [paper.id for paper in user_papers]

        collaborators_dict = {}

        # Get collaborators from papers you own
        if paper_ids:
            query = select(PaperCollaborator, User).join(
                User, PaperCollaborator.user_id == User.id
            ).where(
                and_(
                    PaperCollaborator.paper_id.in_(paper_ids),
                    PaperCollaborator.status == "accepted"
                )
            )

            result = await db.execute(query)
            collab_data = result.all()

            for collab, user in collab_data:
                user_id = str(user.id)

                if user_id not in collaborators_dict:
                    collaborators_dict[user_id] = {
                        "id": str(collab.id),
                        "user_id": user_id,
                        "name": user.name,
                        "email": user.email,
                        "role": collab.role,
                        "status": "active",
                        "joinedAt": collab.created_at.isoformat() if collab.created_at else None,
                        "avatar": None,
                        "paper_count": 1,
                        "relationship": "you_added_them"
                    }
                else:
                    collaborators_dict[user_id]["paper_count"] += 1

        # ✅ PART 2: Get papers where USER IS COLLABORATOR (reverse lookup)
        collab_papers_query = select(PaperCollaborator, Paper, User).join(
            Paper, PaperCollaborator.paper_id == Paper.id
        ).join(
            User, Paper.owner_id == User.id
        ).where(
            and_(
                PaperCollaborator.user_id == current_user.id,
                PaperCollaborator.status == "accepted"
            )
        )

        collab_papers_result = await db.execute(collab_papers_query)
        collab_papers_data = collab_papers_result.all()

        for collab, paper, owner in collab_papers_data:
            owner_id = str(owner.id)

            if owner_id not in collaborators_dict:
                collaborators_dict[owner_id] = {
                    "id": f"owner-{owner_id}",
                    "user_id": owner_id,
                    "name": owner.name,
                    "email": owner.email,
                    "role": "owner",
                    "status": "active",
                    "joinedAt": collab.created_at.isoformat() if collab.created_at else None,
                    "avatar": None,
                    "paper_count": 1,
                    "relationship": "they_added_you"
                }
            else:
                collaborators_dict[owner_id]["paper_count"] += 1

        collaborators = list(collaborators_dict.values())

        logger.info(f"✅ Found {len(collaborators)} unique collaborators")

        return {"collaborators": collaborators}

    except Exception as e:
        logger.error(f"❌ Error fetching collaborators: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/paper/{paper_id}")
async def get_paper_collaborators(
        paper_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get collaborators for specific paper"""

    logger.info(f"📊 Fetching collaborators for paper {paper_id}")

    try:
        # Verify paper exists and user has access
        paper = await db.get(Paper, UUID(paper_id))
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        # Get paper collaborators with user info
        query = select(PaperCollaborator, User).join(
            User, PaperCollaborator.user_id == User.id
        ).where(
            and_(
                PaperCollaborator.paper_id == UUID(paper_id),
                PaperCollaborator.status == "accepted"
            )
        )

        result = await db.execute(query)
        collab_data = result.all()

        collaborators = []

        for collab, user in collab_data:
            collaborators.append({
                "id": str(collab.id),
                "name": user.name,
                "email": user.email,
                "role": collab.role,
                "status": "active",
                "joinedAt": collab.created_at.isoformat() if collab.created_at else None,
                "avatar": None
            })

        # Add paper owner
        owner = await db.get(User, paper.owner_id)
        if owner:
            collaborators.insert(0, {
                "id": f"owner-{paper.owner_id}",
                "name": owner.name,
                "email": owner.email,
                "role": "owner",
                "status": "active",
                "joinedAt": paper.created_at.isoformat() if paper.created_at else None,
                "avatar": None
            })

        # Get pending invitations
        pending_invites = await db.execute(
            select(CollaborationInvite).where(
                and_(
                    CollaborationInvite.paper_id == UUID(paper_id),
                    CollaborationInvite.status == InvitationStatus.PENDING
                )
            )
        )
        pending_invites = pending_invites.scalars().all()

        for invite in pending_invites:
            collaborators.append({
                "id": str(invite.id),
                "name": invite.email.split('@')[0],  # Use email username as name
                "email": invite.email,
                "role": invite.role.value,
                "status": "pending",
                "joinedAt": None,
                "avatar": None
            })

        logger.info(f"✅ Found {len(collaborators)} collaborators for paper {paper_id}")

        return {"collaborators": collaborators}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching paper collaborators: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{collaboration_id}")
async def remove_collaborator(
        collaboration_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Remove a collaborator from a paper"""

    logger.info(f"🗑️  Removing collaborator {collaboration_id}")

    try:
        # Get collaboration
        collab = await db.get(PaperCollaborator, UUID(collaboration_id))
        if not collab:
            raise HTTPException(status_code=404, detail="Collaborator not found")

        # Verify paper ownership
        paper = await db.get(Paper, collab.paper_id)
        if not paper or str(paper.owner_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Only paper owner can remove collaborators")

        # Delete collaboration
        await db.delete(collab)
        await db.commit()

        logger.info(f"✅ Removed collaborator {collaboration_id}")

        return {"success": True, "message": "Collaborator removed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error removing collaborator: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{collaboration_id}/role")
async def change_collaborator_role(
        collaboration_id: str,
        role: str = Body(..., embed=True),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Change collaborator role"""

    logger.info(f"🔄 Changing role for collaborator {collaboration_id} to {role}")

    try:
        # Get collaboration
        collab = await db.get(PaperCollaborator, UUID(collaboration_id))
        if not collab:
            raise HTTPException(status_code=404, detail="Collaborator not found")

        # Verify paper ownership
        paper = await db.get(Paper, collab.paper_id)
        if not paper or str(paper.owner_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Only paper owner can change roles")

        # Validate role
        valid_roles = ['viewer', 'editor', 'co-author']
        if role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")

        # Update role and permissions
        collab.role = role
        collab.can_edit = role in ['co-author', 'editor']
        collab.can_comment = True
        collab.can_invite_others = role == 'co-author'

        await db.commit()
        await db.refresh(collab)

        logger.info(f"✅ Changed role for collaborator {collaboration_id} to {role}")

        return {
            "success": True,
            "new_role": role,
            "collaboration_id": str(collab.id)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error changing role: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_collaboration_stats(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get collaboration statistics for Analytics page"""

    try:
        # Get user's papers
        user_papers = await db.execute(
            select(Paper).where(Paper.owner_id == current_user.id)
        )
        user_papers = user_papers.scalars().all()
        paper_ids = [paper.id for paper in user_papers]

        if not paper_ids:
            return {
                "total_collaborators": 0,
                "active_collaborations": 0,
                "collaborative_papers": 0,
                "pending_invites": 0
            }

        # Count total collaborators
        total_collabs = await db.execute(
            select(func.count(func.distinct(PaperCollaborator.user_id))).where(
                and_(
                    PaperCollaborator.paper_id.in_(paper_ids),
                    PaperCollaborator.status == "accepted"
                )
            )
        )
        total_collaborators = total_collabs.scalar() or 0

        # Count collaborative papers (papers with at least one collaborator)
        collab_papers = await db.execute(
            select(func.count(func.distinct(PaperCollaborator.paper_id))).where(
                and_(
                    PaperCollaborator.paper_id.in_(paper_ids),
                    PaperCollaborator.status == "accepted"
                )
            )
        )
        collaborative_papers = collab_papers.scalar() or 0

        # Count pending invites
        pending = await db.execute(
            select(func.count(CollaborationInvite.id)).where(
                and_(
                    CollaborationInvite.paper_id.in_(paper_ids),
                    CollaborationInvite.status == InvitationStatus.PENDING
                )
            )
        )
        pending_invites = pending.scalar() or 0

        return {
            "total_collaborators": total_collaborators,
            "active_collaborations": total_collaborators,  # Same for now
            "collaborative_papers": collaborative_papers,
            "pending_invites": pending_invites
        }

    except Exception as e:
        logger.error(f"❌ Error fetching collaboration stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))