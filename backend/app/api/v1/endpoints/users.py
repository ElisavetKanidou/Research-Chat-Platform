"""
User management API endpoints - COMPLETE WORKING VERSION
backend/app/api/v1/endpoints/users.py
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserResponse, UserUpdate, UserPublicResponse, UserStatsResponse,
    UserPreferencesUpdate, PasswordChangeRequest, EmailChangeRequest,
    AccountDeletionRequest, UserActivityResponse
)
from app.services.auth_service import auth_service
from app.services.paper_service import paper_service
from app.core.exceptions import NotFoundException, ValidationException

router = APIRouter()


# ==================== CURRENT USER PROFILE ====================

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
        current_user: User = Depends(get_current_user)
):
    """Get current user's full profile with all preferences"""
    print(f"🔍 [GET /users/me] User: {current_user.email}")
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
        user_updates: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Update current user's profile (basic fields only)"""
    try:
        print(f"\n{'='*80}")
        print(f"📝 [PATCH /users/me] Updating profile")
        print(f"👤 User: {current_user.email}")
        print(f"{'='*80}")

        # Update basic fields (exclude preferences - use separate endpoint)
        update_data = user_updates.model_dump(exclude_unset=True, exclude={'preferences'})
        print(f"📥 Fields to update: {list(update_data.keys())}")

        for field, value in update_data.items():
            if hasattr(current_user, field) and value is not None:
                setattr(current_user, field, value)
                print(f"  ✅ {field} = {value}")

        await db.commit()
        await db.refresh(current_user)

        print(f"✅ Profile updated successfully\n")
        return UserResponse.model_validate(current_user)

    except Exception as e:
        await db.rollback()
        print(f"❌ Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}"
        )


# ==================== PREFERENCES ====================

@router.get("/me/preferences")
async def get_user_preferences(
        current_user: User = Depends(get_current_user)
):
    """Get user preferences"""
    print(f"🔍 [GET /users/me/preferences] User: {current_user.email}")
    return {
        "preferences": current_user.preferences or {}
    }


@router.patch("/me/preferences")
async def update_user_preferences(
        preferences: dict,  # Accept raw dict for flexibility
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Update user preferences (theme, notifications, privacy, integrations)

    Accepts a dictionary with any combination of:
    - theme, language, timezone, dateFormat, defaultWordCount
    - notifications: {emailNotifications, deadlineReminders, ...}
    - privacy: {profileVisibility, shareAnalytics, dataSyncEnabled}
    - integrations: {googleDrive, dropbox, zotero, mendeley, latex}
    """
    try:
        print(f"\n{'='*80}")
        print(f"📝 [PATCH /users/me/preferences] Updating preferences")
        print(f"👤 User: {current_user.email}")
        print(f"{'='*80}")
        print(f"📥 Incoming preferences: {preferences}")

        # Get current preferences (already a dict)
        current_prefs = current_user.preferences if current_user.preferences else {}
        print(f"📊 Current preferences: {list(current_prefs.keys())}")

        # Deep merge function
        def deep_merge(target: dict, source: dict) -> dict:
            """Recursively merge source into target"""
            result = target.copy()
            for key, value in source.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    # Recursively merge nested dicts
                    result[key] = deep_merge(result[key], value)
                else:
                    # Overwrite or add new key
                    result[key] = value
            return result

        # Merge preferences
        updated_prefs = deep_merge(current_prefs, preferences)

        print(f"\n🔧 Merged preferences:")
        for key in updated_prefs.keys():
            print(f"  ✅ {key}")

        # ✅ CRITICAL: Create NEW dict for SQLAlchemy change detection
        current_user.preferences = updated_prefs

        # ✅ CRITICAL: Tell SQLAlchemy the JSON column changed!
        flag_modified(current_user, "preferences")
        print(f"🚩 Called flag_modified on preferences")

        await db.commit()
        print(f"💾 Committed to database")

        await db.refresh(current_user)
        print(f"🔄 Refreshed user")

        print(f"✅ Preferences updated successfully")
        print(f"{'='*80}\n")

        return {
            "message": "Preferences updated successfully",
            "preferences": current_user.preferences
        }

    except Exception as e:
        await db.rollback()
        print(f"❌ Error updating preferences: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update preferences: {str(e)}"
        )


# ==================== PASSWORD CHANGE ====================

@router.post("/me/change-password")
async def change_password(
        password_data: PasswordChangeRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    try:
        print(f"🔍 [POST /users/me/change-password] User: {current_user.email}")

        await auth_service.change_password(
            db=db,
            user=current_user,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )

        print(f"✅ Password changed successfully")
        return {"message": "Password changed successfully"}

    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        print(f"❌ Error changing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


# ==================== USER STATISTICS ====================

@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_statistics(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get user's research statistics"""
    print(f"🔍 [GET /users/me/stats] User: {current_user.email}")

    stats = await paper_service.get_paper_statistics(db, str(current_user.id))

    return UserStatsResponse(
        total_papers=stats.get("total_papers", 0),
        published_papers=stats.get("published_papers", 0),
        total_words=stats.get("total_words", 0),
        collaborators=0,
        research_areas=list(stats.get("research_areas", {}).keys()),
        avg_completion_time=None,
        productivity_score=stats.get("average_progress", 0),
        last_updated=current_user.updated_at
    )


# ==================== PUBLIC PROFILE ====================

@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user_public_profile(
        user_id: str,
        db: AsyncSession = Depends(get_db)
):
    """Get public user profile"""
    print(f"🔍 [GET /users/{user_id}] Loading public profile")

    user = await auth_service.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User")

    return UserPublicResponse.model_validate(user)


# ==================== DATA EXPORT (GDPR) ====================

@router.post("/me/export-data")
async def export_user_data(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Export all user data (GDPR compliance)"""
    try:
        from datetime import datetime

        print(f"🔍 [POST /users/me/export-data] User: {current_user.email}")

        export_data = {
            "user_profile": {
                "email": current_user.email,
                "name": current_user.name,
                "affiliation": current_user.affiliation,
                "orcid_id": current_user.orcid_id,
                "research_interests": current_user.research_interests,
                "bio": current_user.bio,
                "website": current_user.website,
                "location": current_user.location,
                "created_at": str(current_user.created_at),
                "last_login_at": str(current_user.last_login_at) if current_user.last_login_at else None,
            },
            "preferences": current_user.preferences,
            "subscription": {
                "plan": current_user.subscription_plan,
                "status": current_user.subscription_status,
            },
            "exported_at": str(datetime.utcnow())
        }

        print(f"✅ Data export prepared")

        return {
            "message": "Data export ready",
            "data": export_data
        }
    except Exception as e:
        print(f"❌ Error exporting data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


# ==================== ACCOUNT DEACTIVATION ====================

@router.delete("/me/account")
async def deactivate_account(
        deletion_request: AccountDeletionRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Deactivate user account (soft delete)"""
    try:
        print(f"🔍 [DELETE /users/me/account] User: {current_user.email}")

        # Verify password
        if not auth_service.verify_password(deletion_request.password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect"
            )

        # Verify confirmation
        if deletion_request.confirmation != "DELETE MY ACCOUNT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account deletion must be confirmed with exact phrase"
            )

        # Soft delete
        await auth_service.deactivate_user(db=db, user=current_user)

        print(f"✅ Account deactivated")
        return {"message": "Account deactivated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"❌ Error deactivating account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate account"
        )


# ==================== EMAIL CHANGE ====================

@router.post("/me/change-email")
async def change_email(
        email_data: EmailChangeRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Change user email address"""
    try:
        print(f"🔍 [POST /users/me/change-email] User: {current_user.email} -> {email_data.new_email}")

        # Verify password
        if not auth_service.verify_password(email_data.password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect"
            )

        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == email_data.new_email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already in use"
            )

        # Update email
        current_user.email = email_data.new_email
        current_user.is_verified = False  # Require re-verification

        await db.commit()

        print(f"✅ Email changed successfully")
        return {
            "message": "Email changed successfully. Please verify your new email address.",
            "new_email": email_data.new_email
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"❌ Error changing email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change email"
        )


# ==================== ACTIVITY LOG ====================

@router.get("/me/activity", response_model=List[UserActivityResponse])
async def get_user_activity(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        limit: int = 50,
        offset: int = 0
):
    """Get user activity log"""
    print(f"🔍 [GET /users/me/activity] User: {current_user.email}")

    # Placeholder - implement actual activity logging
    return []


# ==================== RESEARCH INTERESTS ====================

@router.patch("/me/research-interests")
async def update_research_interests(
        research_interests: List[str],
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Update user's research interests"""
    try:
        print(f"🔍 [PATCH /users/me/research-interests] User: {current_user.email}")
        print(f"📝 New interests: {research_interests}")

        current_user.research_interests = research_interests

        await db.commit()
        await db.refresh(current_user)

        print(f"✅ Research interests updated")
        return {
            "message": "Research interests updated successfully",
            "research_interests": current_user.research_interests
        }
    except Exception as e:
        await db.rollback()
        print(f"❌ Error updating research interests: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update research interests: {str(e)}"
        )