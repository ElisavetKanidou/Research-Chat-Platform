"""
AI Chat API endpoints for research assistance - PRODUCTION READY
backend/app/api/v1/endpoints/chat.py

This is a complete, production-ready implementation with:
- Proper authentication
- Error handling
- Logging
- Security
- Documentation
"""
# Also add these imports at the TOP of the file (if not already there):
from datetime import datetime
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.paper import Paper
from app.models.chat import ChatMessage
from app.schemas.chat import (
    ChatMessageRequest, ChatMessageResponse, ChatHistoryResponse,
    PersonalizationSettingsUpdate, AddToSectionRequest, AddToSectionResponse,
    GetSectionContentResponse, GetAllSectionsResponse
)
from app.services.ai_service import ai_service
from app.services.paper_service import paper_service
from app.services.section_content_service import section_content_service
from app.core.exceptions import (
    NotFoundException, ValidationException,
    AIServiceException, AuthorizationException
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== CHAT ENDPOINTS ====================

@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    message_request: ChatMessageRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to AI assistant and get a personalized response.

    This endpoint processes user messages through the AI service with:
    - Context from the current paper (if provided)
    - User's other papers for reference
    - Personalized AI settings
    - Conversation history

    Returns:
        ChatMessageResponse: AI-generated response with suggestions and metadata

    Raises:
        HTTPException: 401 if unauthorized, 403 if forbidden, 502 if AI service fails
    """

    logger.info(f"Chat message from user {current_user.id}: {message_request.content[:50]}...")

    try:
        # Validate and get paper context if provided
        paper = None
        if message_request.paper_context and message_request.paper_context.id:
            paper = await paper_service.get_paper_by_id(
                db, message_request.paper_context.id
            )

            if not paper:
                raise NotFoundException("Paper not found")

            if not paper.is_viewable_by(str(current_user.id)):
                raise AuthorizationException("You don't have permission to access this paper")

            logger.debug(f"Paper context: {paper.title}")

        # Process the chat message through AI service
        ai_response = await ai_service.process_chat_message(
            user=current_user,
            message=message_request.content,
            paper_context=paper,
            user_papers_context=message_request.user_papers_context,
            personalization_settings=message_request.personalization_settings,
            db=db
        )

        # Save conversation to database in background (non-blocking)
        background_tasks.add_task(
            save_chat_conversation,
            db,
            str(current_user.id),
            str(paper.id) if paper else None,
            message_request.content,
            ai_response.responseContent
        )

        logger.info(f"Successfully generated AI response for user {current_user.id}")

        return {
            "messageId": getattr(ai_response, 'messageId', f"msg-{current_user.id}-{int(time.time())}"),
            "responseContent": getattr(ai_response, 'responseContent', str(ai_response)),
            "createdAt": getattr(ai_response, 'createdAt', datetime.now().isoformat()),
            "needsConfirmation": getattr(ai_response, 'needsConfirmation', False),
            "attachments": getattr(ai_response, 'attachments', []),
            "suggestions": getattr(ai_response, 'suggestions', []),
            "metadata": getattr(ai_response, 'metadata', None)
        }

    except AuthorizationException as e:
        logger.warning(f"Authorization failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except NotFoundException as e:
        logger.warning(f"Resource not found for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AIServiceException as e:
        logger.error(f"AI service error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service temporarily unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in chat for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your message"
        )


@router.get("/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    paper_id: Optional[str] = None,
    limit: int = 50
):
    """
    Get chat history for the current user.

    Args:
        paper_id: Optional - filter by specific paper
        limit: Maximum number of messages (default: 50, max: 100)

    Returns:
        List of chat messages in chronological order
    """

    # Validate limit
    if limit > 100:
        limit = 100
    elif limit < 1:
        limit = 10

    logger.info(f"Fetching chat history for user {current_user.id}, limit={limit}")

    try:
        messages = await ai_service.get_chat_history(
            db=db,
            user_id=str(current_user.id),
            paper_id=paper_id,
            limit=limit
        )

        return [ChatHistoryResponse.from_orm(msg) for msg in messages]

    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )


@router.delete("/history/{message_id}")
async def delete_chat_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a specific chat message (user must own the message)"""

    logger.info(f"User {current_user.id} deleting message {message_id}")

    message = await ai_service.get_message_by_id(db, message_id)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat message not found"
        )

    if str(message.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own messages"
        )

    await ai_service.delete_message(db, message_id)

    return {"success": True, "message": "Chat message deleted successfully"}


@router.delete("/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    paper_id: Optional[str] = None
):
    """
    Clear chat history for the current user.

    Args:
        paper_id: Optional - clear only messages for specific paper
    """

    logger.info(f"User {current_user.id} clearing chat history (paper_id={paper_id})")

    await ai_service.clear_chat_history(
        db=db,
        user_id=str(current_user.id),
        paper_id=paper_id
    )

    return {
        "success": True,
        "message": "Chat history cleared successfully",
        "scope": "paper-specific" if paper_id else "all"
    }


# ==================== PERSONALIZATION ENDPOINTS ====================

@router.post("/personalization")
async def update_personalization_settings(
    settings: PersonalizationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update AI personalization settings for the current user.

    Settings control how the AI adapts to:
    - Lab research patterns
    - Personal writing style
    - Global literature trends
    """

    logger.info(f"User {current_user.id} updating personalization settings")

    try:
        # Get or create user preferences
        current_preferences = current_user.preferences or {}
        ai_personalization = current_preferences.get("ai_personalization", {})

        # Update settings (only non-None values)
        updates = {}
        if settings.lab_level is not None:
            updates["lab_level"] = settings.lab_level
        if settings.personal_level is not None:
            updates["personal_level"] = settings.personal_level
        if settings.global_level is not None:
            updates["global_level"] = settings.global_level
        if settings.writing_style is not None:
            updates["writing_style"] = settings.writing_style
        if settings.research_focus is not None:
            updates["research_focus"] = settings.research_focus
        if settings.context_depth is not None:
            updates["context_depth"] = settings.context_depth

        ai_personalization.update(updates)
        current_preferences["ai_personalization"] = ai_personalization

        # Save to database
        current_user.update_preferences(current_preferences)
        await db.commit()

        logger.info(f"Personalization settings updated for user {current_user.id}")

        return {
            "success": True,
            "message": "Personalization settings updated successfully",
            "settings": ai_personalization
        }

    except Exception as e:
        logger.error(f"Error updating personalization: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update personalization settings"
        )


@router.get("/suggestions")
async def get_ai_suggestions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    paper_id: Optional[str] = None
):
    """
    Get AI-generated suggestions for research or writing.

    Args:
        paper_id: Optional - get suggestions specific to a paper

    Returns:
        List of actionable suggestions
    """

    logger.info(f"Generating suggestions for user {current_user.id}")

    paper = None
    if paper_id:
        paper = await paper_service.get_paper_by_id(db, paper_id)

        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found"
            )

        if not paper.is_viewable_by(str(current_user.id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access this paper"
            )

    try:
        suggestions = await ai_service.generate_suggestions(
            user=current_user,
            paper=paper,
            db=db
        )

        return {
            "success": True,
            "suggestions": suggestions,
            "context": "paper-specific" if paper else "general"
        }

    except AIServiceException as e:
        logger.error(f"AI service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable"
        )


# ==================== SECTION MANAGEMENT ENDPOINTS ====================

@router.post("/add-to-section", response_model=AddToSectionResponse)
async def add_content_to_section(
    request: AddToSectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add AI-generated content from chat to a specific paper section.

    This allows users to:
    - Save chat responses directly to paper sections
    - Choose between append or replace mode
    - Automatically update word counts and progress

    Args:
        request: Contains message_id, paper_id, section_type, content, and append mode

    Returns:
        Section details after update including new word count

    Raises:
        HTTPException: 404 if not found, 403 if forbidden, 400 if validation fails
    """

    logger.info(
        f"User {current_user.id} adding content to section "
        f"{request.section_type} in paper {request.paper_id}"
    )

    try:
        result = await section_content_service.add_chat_content_to_section(
            db=db,
            user_id=str(current_user.id),
            paper_id=request.paper_id,
            section_type=request.section_type.value,
            content=request.content,
            message_id=request.message_id,
            append=request.append
        )

        logger.info(
            f"Successfully added {result['wordCount']} words to "
            f"{request.section_type} for paper {request.paper_id}"
        )

        return AddToSectionResponse(**result)

    except NotFoundException as e:
        logger.warning(f"Resource not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AuthorizationException as e:
        logger.warning(f"Authorization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValidationException as e:
        logger.warning(f"Validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding to section: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add content to section"
        )


@router.get("/section-content/{paper_id}/{section_type}", response_model=GetSectionContentResponse)
async def get_section_content(
    paper_id: str,
    section_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current content of a specific paper section.

    Returns the full content, word count, and status of the section.
    """

    logger.debug(f"Fetching {section_type} content for paper {paper_id}")

    try:
        content = await section_content_service.get_section_content(
            db=db,
            paper_id=paper_id,
            section_type=section_type,
            user_id=str(current_user.id)
        )

        if content is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found or you don't have access"
            )

        # Get paper to retrieve section details
        paper = await db.get(Paper, paper_id)
        section_obj = None

        for s in paper.sections:
            if s.title == section_content_service.SECTION_TITLES.get(section_type):
                section_obj = s
                break

        return GetSectionContentResponse(
            content=content,
            sectionType=section_type,
            wordCount=section_obj.word_count if section_obj else 0,
            status=section_obj.status.value if section_obj else "not-started"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching section content: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve section content"
        )


@router.get("/all-sections/{paper_id}", response_model=GetAllSectionsResponse)
async def get_all_sections(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get content of all sections for a paper.

    Returns a complete overview of the paper structure with:
    - All section contents
    - Individual word counts
    - Section statuses
    - Total paper metrics
    """

    logger.debug(f"Fetching all sections for paper {paper_id}")

    try:
        contents = await section_content_service.get_all_section_contents(
            db=db,
            paper_id=paper_id,
            user_id=str(current_user.id)
        )

        paper = await db.get(Paper, paper_id)

        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found"
            )

        return GetAllSectionsResponse(
            sections=contents,
            totalWordCount=paper.current_word_count,
            paperProgress=paper.progress
        )

    except AuthorizationException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching all sections: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sections"
        )


# ==================== UTILITY ENDPOINTS ====================

@router.get("/health")
async def chat_health_check():
    """Health check endpoint for the chat service"""
    return {
        "status": "healthy",
        "service": "chat",
        "version": "1.0.0",
        "features": [
            "ai_chat",
            "section_management",
            "personalization",
            "history"
        ]
    }


async def save_chat_conversation(
        db: AsyncSession,
        user_id: str,
        paper_id: Optional[str],
        user_message: str,
        ai_response: str
):
    """
    Background task to save chat conversation to database.

    This function saves both the user message and AI response to the database
    for conversation history. It runs in the background and won't affect the
    user experience if it fails.

    Args:
        db: Database session (reused from endpoint)
        user_id: User UUID as string
        paper_id: Optional paper UUID as string
        user_message: User's message content
        ai_response: AI's response content
    """
    try:
        from app.models.chat import ChatMessage
        from uuid import UUID

        logger.debug(f"Saving chat conversation for user {user_id}")

        # Convert string IDs to UUID
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        paper_uuid = UUID(paper_id) if paper_id and isinstance(paper_id, str) else None

        # Create user message
        user_msg = ChatMessage(
            user_id=user_uuid,
            paper_id=paper_uuid,
            role="user",
            content=user_message
        )
        db.add(user_msg)

        # Create AI response message
        ai_msg = ChatMessage(
            user_id=user_uuid,
            paper_id=paper_uuid,
            role="assistant",
            content=ai_response
        )
        db.add(ai_msg)

        # Commit to database
        await db.commit()

        logger.info(f"✅ Successfully saved conversation for user {user_id}")

    except Exception as e:
        logger.error(f"Failed to save chat conversation: {str(e)}", exc_info=True)
        try:
            await db.rollback()
        except:
            pass
        # Don't raise - this is a background task
        # Failures here shouldn't affect the user's chat experience