"""
User management API endpoints (app/api/v1/endpoints/users.py)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserResponse, UserUpdate, UserPublicResponse, UserStatsResponse,
    UserPreferencesUpdate, APIKeyCreate, APIKeyResponse
)
from app.services.auth_service import auth_service
from app.services.paper_service import paper_service
from app.core.exceptions import NotFoundException, ValidationException

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
        current_user: User = Depends(get_current_user)
):
    """Get current user's full profile"""
    return UserResponse.from_orm(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
        user_updates: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    try:
        # Update user fields
        update_data = user_updates.dict(exclude_unset=True, exclude={'preferences'})

        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)

        # Update preferences if provided
        if user_updates.preferences:
            current_user.update_preferences(user_updates.preferences.dict())

        await db.commit()
        await db.refresh(current_user)

        return UserResponse.from_orm(current_user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_statistics(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get user's research statistics"""
    stats = await paper_service.get_paper_statistics(db, current_user.id)

    return UserStatsResponse(
        total_papers=stats["total_papers"],
        published_papers=stats["published_papers"],
        total_words=stats["total_words"],
        collaborators=0,  # Would calculate from collaborations
        research_areas=list(stats["research_areas"].keys()),
        avg_completion_time=None,  # Would calculate from paper creation/completion dates
        productivity_score=stats["average_progress"],
        last_updated=current_user.updated_at
    )


@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user_public_profile(
        user_id: str,
        db: AsyncSession = Depends(get_db)
):
    """Get public user profile"""
    user = await auth_service.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User")

    return UserPublicResponse.from_orm(user)


@router.patch("/me/preferences")
async def update_user_preferences(
        preferences: UserPreferencesUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    try:
        current_user.update_preferences(preferences.dict(exclude_unset=True))
        await db.commit()
        return {"message": "Preferences updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.post("/me/api-keys", response_model=APIKeyResponse)
async def create_api_key(
        api_key_data: APIKeyCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Create new API key for user"""
    # This would be implemented with proper API key generation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="API key management not yet implemented"
    )


@router.get("/me/api-keys", response_model=List[APIKeyResponse])
async def get_user_api_keys(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get user's API keys"""
    # This would return user's API keys (without the actual key values)
    return []


@router.delete("/me/api-keys/{key_id}")
async def delete_api_key(
        key_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Delete an API key"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="API key management not yet implemented"
    )


