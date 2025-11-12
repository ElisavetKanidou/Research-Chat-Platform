"""
AI Chat API endpoints for research assistance - FIXED IMPORTS
backend/app/api/v1/endpoints/chat.py
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.paper import Paper
from app.models.chat import ChatMessage
from app.schemas.chat import (
    ChatMessageRequest, ChatMessageResponse, ChatHistoryResponse,
    PersonalizationSettingsUpdate
)
from app.services.ai_service import ai_service
from app.services.paper_service import paper_service
# ✅ ADD THIS IMPORT - IT WAS MISSING!
from app.core.exceptions import NotFoundException, ValidationException, AIServiceException, AuthorizationException

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
        message_request: ChatMessageRequest,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Send a message to AI assistant and get response"""

    try:
        # Get paper context if paper_id provided
        paper = None
        if message_request.paper_context and message_request.paper_context.id:
            paper = await paper_service.get_paper_by_id(
                db, message_request.paper_context.id
            )
            if not paper or not paper.is_viewable_by(str(current_user.id)):
                raise AuthorizationException("Cannot access specified paper")

        # Process the chat message through AI service
        ai_response = await ai_service.process_chat_message(
            user=current_user,
            message=message_request.content,
            paper_context=paper,
            user_papers_context=message_request.user_papers_context,
            personalization_settings=message_request.personalization_settings,
            db=db
        )

        # Save the conversation to database in background
        background_tasks.add_task(
            save_chat_conversation,
            db, current_user.id, paper.id if paper else None,
            message_request.content, ai_response.response_content
        )

        return ai_response

    except AIServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message"
        )


@router.get("/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        paper_id: Optional[str] = None,
        limit: int = 50
):
    """Get chat history for user, optionally filtered by paper"""

    messages = await ai_service.get_chat_history(
        db=db,
        user_id=current_user.id,
        paper_id=paper_id,
        limit=limit
    )

    return [ChatHistoryResponse.from_orm(msg) for msg in messages]


@router.delete("/history/{message_id}")
async def delete_chat_message(
        message_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Delete a specific chat message"""

    message = await ai_service.get_message_by_id(db, message_id)
    if not message:
        raise NotFoundException("Chat message")

    if str(message.user_id) != str(current_user.id):
        raise AuthorizationException("You can only delete your own messages")

    await ai_service.delete_message(db, message_id)
    return {"message": "Chat message deleted successfully"}


@router.delete("/history")
async def clear_chat_history(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        paper_id: Optional[str] = None
):
    """Clear chat history for user, optionally for specific paper"""

    await ai_service.clear_chat_history(
        db=db,
        user_id=current_user.id,
        paper_id=paper_id
    )

    return {"message": "Chat history cleared successfully"}


@router.post("/personalization")
async def update_personalization_settings(
        settings: PersonalizationSettingsUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Update AI personalization settings for user"""

    # Update user preferences with new AI personalization settings
    current_preferences = current_user.preferences or {}
    ai_personalization = current_preferences.get("ai_personalization", {})

    # Update with new settings
    if settings.lab_level is not None:
        ai_personalization["lab_level"] = settings.lab_level
    if settings.personal_level is not None:
        ai_personalization["personal_level"] = settings.personal_level
    if settings.global_level is not None:
        ai_personalization["global_level"] = settings.global_level
    if settings.writing_style is not None:
        ai_personalization["writing_style"] = settings.writing_style
    if settings.research_focus is not None:
        ai_personalization["research_focus"] = settings.research_focus
    if settings.context_depth is not None:
        ai_personalization["context_depth"] = settings.context_depth

    current_preferences["ai_personalization"] = ai_personalization
    current_user.update_preferences(current_preferences)

    await db.commit()

    return {"message": "Personalization settings updated successfully"}


@router.get("/suggestions")
async def get_ai_suggestions(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        paper_id: Optional[str] = None
):
    """Get AI-generated suggestions for research or writing"""

    paper = None
    if paper_id:
        paper = await paper_service.get_paper_by_id(db, paper_id)
        if not paper or not paper.is_viewable_by(str(current_user.id)):
            raise AuthorizationException("Cannot access specified paper")

    try:
        suggestions = await ai_service.generate_suggestions(
            user=current_user,
            paper=paper,
            db=db
        )

        return {"suggestions": suggestions}

    except AIServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {e.message}"
        )


@router.post("/analyze-writing")
async def analyze_writing_patterns(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        paper_id: Optional[str] = None
):
    """Analyze user's writing patterns and provide insights"""

    paper = None
    if paper_id:
        paper = await paper_service.get_paper_by_id(db, paper_id)
        if not paper or not paper.is_viewable_by(str(current_user.id)):
            raise AuthorizationException("Cannot access specified paper")

    try:
        analysis = await ai_service.analyze_writing_patterns(
            user=current_user,
            paper=paper,
            db=db
        )

        return analysis

    except AIServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {e.message}"
        )


@router.post("/generate-outline")
async def generate_paper_outline(
        paper_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Generate an AI-powered outline for a paper"""

    paper = await paper_service.get_paper_by_id(db, paper_id)
    if not paper:
        raise NotFoundException("Paper")

    if not paper.is_editable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to edit this paper")

    try:
        outline = await ai_service.generate_paper_outline(
            paper=paper,
            user=current_user,
            db=db
        )

        return {"outline": outline}

    except AIServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {e.message}"
        )


@router.post("/improve-section")
async def improve_section_content(
        paper_id: str,
        section_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get AI suggestions to improve a specific paper section"""

    paper = await paper_service.get_paper_by_id(db, paper_id)
    if not paper:
        raise NotFoundException("Paper")

    if not paper.is_viewable_by(str(current_user.id)):
        raise AuthorizationException("You don't have permission to view this paper")

    # Find the specific section
    section = None
    for s in paper.sections:
        if str(s.id) == section_id:
            section = s
            break

    if not section:
        raise NotFoundException("Paper section")

    try:
        improvements = await ai_service.improve_section_content(
            section=section,
            paper=paper,
            user=current_user,
            db=db
        )

        return {"improvements": improvements}

    except AIServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {e.message}"
        )


async def save_chat_conversation(
        db: AsyncSession,
        user_id: str,
        paper_id: Optional[str],
        user_message: str,
        ai_response: str
):
    """Background task to save chat conversation to database"""
    try:
        # Save user message
        user_msg = ChatMessage(
            user_id=user_id,
            paper_id=paper_id,
            role="user",
            content=user_message
        )
        db.add(user_msg)

        # Save AI response
        ai_msg = ChatMessage(
            user_id=user_id,
            paper_id=paper_id,
            role="assistant",
            content=ai_response
        )
        db.add(ai_msg)

        await db.commit()

    except Exception as e:
        await db.rollback()
        # Log error but don't fail the request
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to save chat conversation: {e}")