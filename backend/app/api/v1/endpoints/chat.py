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
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
import json
import os
import tempfile
from pathlib import Path
from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.paper import Paper
from app.models.chat import ChatMessage
from app.models.reference_paper import ReferencePaper
from app.schemas.chat import (
    ChatMessageRequest, ChatMessageResponse, ChatHistoryResponse,
    PersonalizationSettingsUpdate, AddToSectionRequest, AddToSectionResponse,
    GetSectionContentResponse, GetAllSectionsResponse,
    MessageFeedbackRequest, MessageFeedbackResponse
)
from app.services.ai_service import ai_service
from app.services.paper_service import paper_service
from app.services.section_content_service import section_content_service
from app.services.gemini_service import gemini_service
from app.services.openai_service import openai_service
from app.services.gpt_oss_service import gpt_oss_service
from app.services.file_comparison_service import file_comparison_service
from app.core.exceptions import (
    NotFoundException, ValidationException,
    AIServiceException, AuthorizationException
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== HELPER FUNCTIONS ====================

async def get_user_reference_papers(db: AsyncSession, user_id: UUID) -> List[Dict]:
    """
    Fetch user's reference papers for AI personalization

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of reference papers with their writing style features
    """
    try:
        query = select(ReferencePaper).where(
            ReferencePaper.user_id == user_id,
            ReferencePaper.is_analyzed == True  # Only analyzed papers
        ).order_by(ReferencePaper.created_at.desc()).limit(10)  # Top 10 most recent

        result = await db.execute(query)
        papers = result.scalars().all()

        # Convert to dict format
        papers_list = []
        for paper in papers:
            papers_list.append({
                'id': str(paper.id),
                'title': paper.title,
                'paper_type': paper.paper_type.value if paper.paper_type else 'personal',
                'writing_style_features': paper.writing_style_features or {},
                'authors': paper.authors,
                'year': paper.year
            })

        logger.info(f"📚 Fetched {len(papers_list)} reference papers for user {user_id}")
        return papers_list

    except Exception as e:
        logger.error(f"❌ Failed to fetch reference papers: {str(e)}")
        return []


def get_user_personalization_settings(user: User) -> Optional[Dict[str, int]]:
    """
    Get user's personalization settings from database

    Args:
        user: User object

    Returns:
        Dictionary with lab_level, personal_level, global_level or None
    """
    try:
        if user.preferences and isinstance(user.preferences, dict):
            ai_personalization = user.preferences.get('ai_personalization', {})
            if ai_personalization:
                settings = {
                    'lab_level': ai_personalization.get('lab_level', 5),
                    'personal_level': ai_personalization.get('personal_level', 5),
                    'global_level': ai_personalization.get('global_level', 5)
                }
                logger.info(f"📊 Using personalization settings from database: {settings}")
                return settings
    except Exception as e:
        logger.warning(f"⚠️ Failed to get personalization settings: {str(e)}")

    return None


def get_personalization_settings(message_request, current_user: User) -> Optional[Dict]:
    """
    Get personalization settings - prefer request (paper-specific) over database (global)

    Args:
        message_request: Request object with optional personalization_settings
        current_user: User object

    Returns:
        Dictionary with lab_level, personal_level, global_level, writing_style, context_depth, research_focus or None
    """
    if hasattr(message_request, 'personalization_settings') and message_request.personalization_settings:
        # Use paper-specific settings from request
        ps = message_request.personalization_settings
        settings = {
            'lab_level': ps.lab_level,
            'personal_level': ps.personal_level,
            'global_level': ps.global_level,
            'writing_style': getattr(ps, 'writing_style', 'academic'),
            'context_depth': getattr(ps, 'context_depth', 'moderate'),
            'research_focus': getattr(ps, 'research_focus', [])
        }
        logger.info(f"📊 Using personalization from request (paper-specific): {settings}")
        return settings
    else:
        # Fallback to global settings from database
        settings = get_user_personalization_settings(current_user)
        logger.info(f"📊 Using personalization from database (global): {settings}")
        return settings


# ==================== FILE PROCESSING UTILITIES ====================

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text content from uploaded files (PDF or TXT).

    Args:
        file: Uploaded file object

    Returns:
        Extracted text content

    Raises:
        HTTPException: If file processing fails
    """
    try:
        file_extension = file.filename.split('.')[-1].lower() if file.filename else ''

        if file_extension == 'txt':
            # Read text file directly
            content = await file.read()
            return content.decode('utf-8', errors='ignore')

        elif file_extension == 'pdf':
            # For PDF files, we'll need PyPDF2 or similar library
            # For now, let's create a temp file and extract text
            try:
                import PyPDF2
                content = await file.read()

                # Create temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(content)
                    tmp_file_path = tmp_file.name

                # Extract text from PDF
                text = ""
                try:
                    with open(tmp_file_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                finally:
                    # Clean up temp file
                    os.unlink(tmp_file_path)

                return text

            except ImportError:
                logger.warning("PyPDF2 not installed, returning placeholder for PDF")
                return f"[PDF content from {file.filename} - PDF processing library not available]"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_extension}"
            )

    except Exception as e:
        logger.error(f"Error extracting text from file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {file.filename}"
        )


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

    logger.info(f"Chat message from user {current_user.id}: {message_request.content[:50]}... (model: {message_request.model})")

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

        # Route to appropriate AI service based on selected model
        ai_response = None

        if message_request.model == 'gemini':
            # User selected Gemini
            if gemini_service.enabled:
                logger.info("🤖 Using Gemini AI (user selected)")
                try:
                    # Prepare paper context for Gemini
                    paper_ctx = None
                    if paper:
                        paper_ctx = {
                            'title': paper.title,
                            'research_area': paper.research_area or '',
                            'status': paper.status.value if hasattr(paper.status, 'value') else str(paper.status),
                            'progress': paper.progress,
                            'current_word_count': paper.current_word_count,
                            'target_word_count': paper.target_word_count,
                        }

                    # Fetch user's reference papers for style analysis
                    reference_papers = await get_user_reference_papers(db, current_user.id)

                    # Get personalization settings - prefer request over database
                    personalization = None
                    if message_request.personalization_settings:
                        # Use paper-specific settings from request
                        personalization = {
                            'lab_level': message_request.personalization_settings.lab_level,
                            'personal_level': message_request.personalization_settings.personal_level,
                            'global_level': message_request.personalization_settings.global_level
                        }
                        logger.info(f"📊 Using personalization settings from request (paper-specific): {personalization}")
                    else:
                        # Fallback to global settings from database
                        personalization = get_user_personalization_settings(current_user)
                        logger.info(f"📊 Using personalization settings from database (global): {personalization}")

                    # Generate response with Gemini
                    gemini_response = await gemini_service.generate_response(
                        message=message_request.content,
                        files_content=[],
                        personalization=personalization,
                        paper_context=paper_ctx,
                        reference_papers=reference_papers
                    )

                    # Create response wrapper
                    class GeminiResponseWrapper:
                        def __init__(self, gemini_data):
                            self.messageId = f"gemini-{current_user.id}-{int(time.time())}"
                            self.responseContent = gemini_data['content']
                            self.createdAt = datetime.now().isoformat()
                            self.needsConfirmation = False
                            self.attachments = []
                            self.suggestions = gemini_data.get('citations', [])
                            self.metadata = gemini_data.get('metadata', {})

                    ai_response = GeminiResponseWrapper(gemini_response)

                except Exception as e:
                    logger.warning(f"⚠️ Gemini failed, falling back to Groq: {str(e)}")
                    ai_response = None
            else:
                logger.warning("⚠️ Gemini selected but not enabled, falling back to Groq")

        # Route to appropriate service based on model selection
        if ai_response is None:
            if message_request.model == 'groq':
                # User explicitly selected Groq
                logger.info("🤖 Using Groq/Llama (user selected)")
                # Get personalization settings - prefer request over database
                personalization_dict = None
                if message_request.personalization_settings:
                    personalization_dict = {
                        'lab_level': message_request.personalization_settings.lab_level,
                        'personal_level': message_request.personalization_settings.personal_level,
                        'global_level': message_request.personalization_settings.global_level
                    }
                    logger.info(f"📊 Using personalization from request: {personalization_dict}")
                else:
                    personalization_dict = get_user_personalization_settings(current_user)
                    logger.info(f"📊 Using personalization from database: {personalization_dict}")
                ai_response = await ai_service.process_chat_message(
                    user=current_user,
                    message=message_request.content,
                    paper_context=paper,
                    user_papers_context=message_request.user_papers_context,
                    personalization_settings=personalization_dict,
                    db=db
                )
            elif message_request.model in ['gpt-3.5', 'gpt-4']:
                # User selected OpenAI models
                openai_model = 'gpt-3.5-turbo' if message_request.model == 'gpt-3.5' else 'gpt-4'

                if openai_service.enabled:
                    logger.info(f"🤖 Using OpenAI {openai_model} (user selected)")
                    try:
                        # Prepare paper context for OpenAI
                        paper_ctx = None
                        if paper:
                            paper_ctx = {
                                'title': paper.title,
                                'research_area': paper.research_area or '',
                                'status': paper.status.value if hasattr(paper.status, 'value') else str(paper.status),
                                'progress': paper.progress,
                                'current_word_count': paper.current_word_count,
                                'target_word_count': paper.target_word_count,
                            }

                        # Get personalization settings - prefer request over database
                        personalization = None
                        if message_request.personalization_settings:
                            personalization = {
                                'lab_level': message_request.personalization_settings.lab_level,
                                'personal_level': message_request.personalization_settings.personal_level,
                                'global_level': message_request.personalization_settings.global_level
                            }
                            logger.info(f"📊 Using personalization from request: {personalization}")
                        else:
                            personalization = get_user_personalization_settings(current_user)
                            logger.info(f"📊 Using personalization from database: {personalization}")

                        # Generate response with OpenAI
                        openai_response = await openai_service.generate_response(
                            message=message_request.content,
                            files_content=[],
                            personalization=personalization,
                            paper_context=paper_ctx,
                            model=openai_model
                        )

                        # Create response wrapper
                        class OpenAIResponseWrapper:
                            def __init__(self, openai_data):
                                self.messageId = f"openai-{current_user.id}-{int(time.time())}"
                                self.responseContent = openai_data['content']
                                self.createdAt = datetime.now().isoformat()
                                self.needsConfirmation = False
                                self.attachments = []
                                self.suggestions = openai_data.get('citations', [])
                                self.metadata = openai_data.get('metadata', {})

                        ai_response = OpenAIResponseWrapper(openai_response)

                    except Exception as e:
                        logger.warning(f"⚠️ OpenAI failed, falling back to Groq: {str(e)}")
                        personalization_dict = get_personalization_settings(message_request, current_user)
                        ai_response = await ai_service.process_chat_message(
                            user=current_user,
                            message=message_request.content,
                            paper_context=paper,
                            user_papers_context=message_request.user_papers_context,
                            personalization_settings=personalization_dict,
                            db=db
                        )
                else:
                    logger.warning("⚠️ OpenAI selected but not enabled, falling back to Groq")
                    personalization_dict = get_personalization_settings(message_request, current_user)
                    ai_response = await ai_service.process_chat_message(
                        user=current_user,
                        message=message_request.content,
                        paper_context=paper,
                        user_papers_context=message_request.user_papers_context,
                        personalization_settings=personalization_dict,
                        db=db
                    )
            elif message_request.model == 'gpt-oss-120b':
                # User selected GPT-OSS 120B Local Model
                if gpt_oss_service.enabled:
                    logger.info("🚀 Using GPT-OSS 120B (user selected)")
                    try:
                        # Prepare paper context for GPT-OSS
                        paper_ctx = None
                        if paper:
                            paper_ctx = {
                                'title': paper.title,
                                'research_area': paper.research_area or '',
                                'status': paper.status.value if hasattr(paper.status, 'value') else str(paper.status),
                                'progress': paper.progress,
                                'current_word_count': paper.current_word_count,
                                'target_word_count': paper.target_word_count,
                            }

                        # Get personalization settings - prefer request over database
                        personalization = None
                        if message_request.personalization_settings:
                            personalization = {
                                'lab_level': message_request.personalization_settings.lab_level,
                                'personal_level': message_request.personalization_settings.personal_level,
                                'global_level': message_request.personalization_settings.global_level
                            }
                            logger.info(f"📊 Using personalization from request: {personalization}")
                        else:
                            personalization = get_user_personalization_settings(current_user)
                            logger.info(f"📊 Using personalization from database: {personalization}")

                        # Fetch user's reference papers for style analysis
                        reference_papers = await get_user_reference_papers(db, current_user.id)

                        # Generate response with GPT-OSS
                        gpt_oss_response = await gpt_oss_service.generate_response(
                            message=message_request.content,
                            files_content=[],
                            personalization=personalization,
                            paper_context=paper_ctx,
                            reference_papers=reference_papers
                        )

                        # Create response wrapper
                        class GPTOSSResponseWrapper:
                            def __init__(self, gpt_oss_data):
                                self.messageId = gpt_oss_data.get('id', f"msg-gpt-oss-{int(time.time())}")
                                self.responseContent = gpt_oss_data.get('response', '')
                                self.createdAt = datetime.fromtimestamp(gpt_oss_data.get('created', time.time())).isoformat()
                                self.needsConfirmation = False
                                self.attachments = []
                                self.suggestions = []
                                self.metadata = {
                                    'model': gpt_oss_data.get('model', 'gpt-oss:120b'),
                                    'finish_reason': gpt_oss_data.get('finish_reason', 'stop')
                                }

                        ai_response = GPTOSSResponseWrapper(gpt_oss_response)

                    except Exception as e:
                        logger.error(f"❌ GPT-OSS error: {str(e)}")
                        raise AIServiceException(f"GPT-OSS service error: {str(e)}")
                else:
                    logger.warning("⚠️ GPT-OSS selected but not enabled, falling back to Groq")
                    personalization_dict = get_personalization_settings(message_request, current_user)
                    ai_response = await ai_service.process_chat_message(
                        user=current_user,
                        message=message_request.content,
                        paper_context=paper,
                        user_papers_context=message_request.user_papers_context,
                        personalization_settings=personalization_dict,
                        db=db
                    )
            else:
                # Default fallback to Groq
                logger.info(f"🤖 Using Groq/Llama (fallback for model: {message_request.model})")
                personalization_dict = get_personalization_settings(message_request, current_user)
                ai_response = await ai_service.process_chat_message(
                    user=current_user,
                    message=message_request.content,
                    paper_context=paper,
                    user_papers_context=message_request.user_papers_context,
                    personalization_settings=personalization_dict,
                    db=db
                )

        # Save conversation to database and get message ID
        assistant_message_id = await save_chat_conversation(
            db,
            str(current_user.id),
            str(paper.id) if paper else None,
            message_request.content,
            ai_response.responseContent
        )

        logger.info(f"Successfully generated AI response for user {current_user.id}")

        return {
            "messageId": assistant_message_id or getattr(ai_response, 'messageId', f"msg-{current_user.id}-{int(time.time())}"),
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

@router.post("/upload", response_model=ChatMessageResponse)
async def send_chat_message_with_files(
    content: str = Form(""),
    files: List[UploadFile] = File(...),
    paper_context: Optional[str] = Form(None),
    personalization_settings: Optional[str] = Form(None),
    model: str = Form('gemini'),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message with file attachments to AI assistant.

    This endpoint handles file uploads (PDF, TXT) along with chat messages.
    Files are processed and their content is extracted to provide context to the AI.

    Supported file types:
    - PDF (.pdf) - Text is extracted from PDF documents
    - Text (.txt) - Plain text files

    Returns:
        ChatMessageResponse: AI-generated response considering file contents

    Raises:
        HTTPException: 400 for invalid files, 401 if unauthorized, 502 if AI service fails
    """

    logger.info(f"Chat message with {len(files)} file(s) from user {current_user.id}")

    try:
        # Validate file count
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot upload more than 10 files at once"
            )

        # Extract text from all uploaded files
        file_contents = []
        for file in files:
            if not file.filename:
                continue

            # Validate file size (10MB max)
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Reset to beginning

            if file_size > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} exceeds 10MB limit"
                )

            # Validate file type
            file_extension = file.filename.split('.')[-1].lower()
            if file_extension not in ['pdf', 'txt']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type .{file_extension} is not supported. Only PDF and TXT files are allowed."
                )

            # Extract text from file
            extracted_text = await extract_text_from_file(file)
            file_contents.append({
                'filename': file.filename,
                'content': extracted_text,
                'size': file_size
            })

        # Parse paper context if provided
        paper = None
        if paper_context:
            try:
                paper_context_dict = json.loads(paper_context)
                if paper_context_dict and paper_context_dict.get('id'):
                    paper = await paper_service.get_paper_by_id(
                        db, paper_context_dict['id']
                    )

                    if not paper:
                        raise NotFoundException("Paper not found")

                    if not paper.is_viewable_by(str(current_user.id)):
                        raise AuthorizationException("You don't have permission to access this paper")
            except json.JSONDecodeError:
                logger.warning("Invalid paper_context JSON")

        # Get personalization settings - prefer request over database
        personalization = None
        if personalization_settings:
            try:
                pers_dict = json.loads(personalization_settings)
                personalization = {
                    'lab_level': pers_dict.get('lab_level', 5),
                    'personal_level': pers_dict.get('personal_level', 5),
                    'global_level': pers_dict.get('global_level', 5)
                }
                logger.info(f"📊 Using personalization from request (paper-specific): {personalization}")
            except json.JSONDecodeError:
                logger.warning("Invalid personalization_settings JSON, using database settings")
                personalization = get_user_personalization_settings(current_user)
        else:
            # Fallback to global settings from database
            personalization = get_user_personalization_settings(current_user)
            logger.info(f"📊 Using personalization from database (global): {personalization}")

        # Compare files if multiple uploaded
        comparison_summary = ""
        if len(file_contents) >= 2:
            logger.info(f"📊 Comparing {len(file_contents)} files")
            comparisons = file_comparison_service.compare_multiple_files(file_contents)
            comparison_summary = file_comparison_service.generate_comparison_summary(comparisons)

        # Route to appropriate AI service based on selected model
        logger.info(f"📤 Processing with model: {model}")

        ai_response = None

        # Try using Gemini if user selected it
        if model == 'gemini':
            if gemini_service.enabled:
                try:
                    logger.info("🤖 Using Gemini AI for response generation (user selected)")

                    # Prepare paper context for Gemini
                    paper_ctx = None
                    if paper:
                        paper_ctx = {
                            'title': paper.title,
                            'research_area': paper.research_area or '',
                            'status': paper.status.value if hasattr(paper.status, 'value') else str(paper.status),
                            'progress': paper.progress,
                            'current_word_count': paper.current_word_count,
                            'target_word_count': paper.target_word_count,
                        }

                    # Add comparison summary to user message
                    user_message_with_comparison = content if content else "I've uploaded files for analysis."
                    if comparison_summary:
                        user_message_with_comparison += f"\n\n{comparison_summary}"

                    # Fetch user's reference papers for style analysis
                    reference_papers = await get_user_reference_papers(db, current_user.id)

                    # Generate response with Gemini
                    gemini_response = await gemini_service.generate_response(
                        message=user_message_with_comparison,
                        files_content=file_contents,
                        personalization=personalization,
                        paper_context=paper_ctx,
                        reference_papers=reference_papers
                    )

                    # Create response object
                    class GeminiResponseWrapper:
                        def __init__(self, gemini_data):
                            self.messageId = f"gemini-{current_user.id}-{int(time.time())}"
                            self.responseContent = gemini_data['content']
                            self.createdAt = datetime.now().isoformat()
                            self.needsConfirmation = False
                            self.attachments = []
                            self.suggestions = gemini_data.get('citations', [])
                            self.metadata = gemini_data.get('metadata', {})
                            self.metadata['model'] = 'gemini-1.5-flash'
                            if comparison_summary:
                                self.metadata['file_comparison'] = comparison_summary

                    ai_response = GeminiResponseWrapper(gemini_response)

                except Exception as e:
                    logger.warning(f"⚠️ Gemini failed, falling back to Groq: {str(e)}")
                    ai_response = None

            else:
                logger.warning("⚠️ Gemini selected but not enabled, falling back to Groq")

        # Route to appropriate service based on model selection
        if ai_response is None:
            if model == 'groq':
                # User explicitly selected Groq
                logger.info("🤖 Using Groq/Llama for file upload (user selected)")

                enhanced_content = content if content else "I've uploaded some files for you to analyze."
                enhanced_content += "\n\n--- Uploaded Files ---\n"

                for file_info in file_contents:
                    enhanced_content += f"\n**File: {file_info['filename']}** ({file_info['size'] / 1024:.1f} KB)\n"
                    enhanced_content += f"Content:\n{file_info['content'][:5000]}\n"
                    if len(file_info['content']) > 5000:
                        enhanced_content += f"... (truncated, total length: {len(file_info['content'])} characters)\n"

                if comparison_summary:
                    enhanced_content += f"\n\n{comparison_summary}"

                ai_response = await ai_service.process_chat_message(
                    user=current_user,
                    message=enhanced_content,
                    paper_context=paper,
                    user_papers_context=None,
                    personalization_settings=personalization,
                    db=db
                )

            elif model in ['gpt-3.5', 'gpt-4']:
                # User selected OpenAI models
                openai_model = 'gpt-3.5-turbo' if model == 'gpt-3.5' else 'gpt-4'

                if openai_service.enabled:
                    logger.info(f"🤖 Using OpenAI {openai_model} for file upload (user selected)")
                    try:
                        # Prepare paper context for OpenAI
                        paper_ctx = None
                        if paper:
                            paper_ctx = {
                                'title': paper.title,
                                'research_area': paper.research_area or '',
                                'status': paper.status.value if hasattr(paper.status, 'value') else str(paper.status),
                                'progress': paper.progress,
                                'current_word_count': paper.current_word_count,
                                'target_word_count': paper.target_word_count,
                            }

                        # Add comparison summary to user message
                        user_message_with_comparison = content if content else "I've uploaded files for analysis."
                        if comparison_summary:
                            user_message_with_comparison += f"\n\n{comparison_summary}"

                        # Generate response with OpenAI
                        openai_response = await openai_service.generate_response(
                            message=user_message_with_comparison,
                            files_content=file_contents,
                            personalization=personalization,
                            paper_context=paper_ctx,
                            model=openai_model
                        )

                        # Create response object
                        class OpenAIResponseWrapper:
                            def __init__(self, openai_data):
                                self.messageId = f"openai-{current_user.id}-{int(time.time())}"
                                self.responseContent = openai_data['content']
                                self.createdAt = datetime.now().isoformat()
                                self.needsConfirmation = False
                                self.attachments = []
                                self.suggestions = openai_data.get('citations', [])
                                self.metadata = openai_data.get('metadata', {})
                                if comparison_summary:
                                    self.metadata['file_comparison'] = comparison_summary

                        ai_response = OpenAIResponseWrapper(openai_response)

                    except Exception as e:
                        logger.warning(f"⚠️ OpenAI failed, falling back to Groq: {str(e)}")
                        # Fallback to Groq
                        enhanced_content = content if content else "I've uploaded some files for you to analyze."
                        enhanced_content += "\n\n--- Uploaded Files ---\n"

                        for file_info in file_contents:
                            enhanced_content += f"\n**File: {file_info['filename']}** ({file_info['size'] / 1024:.1f} KB)\n"
                            enhanced_content += f"Content:\n{file_info['content'][:5000]}\n"
                            if len(file_info['content']) > 5000:
                                enhanced_content += f"... (truncated, total length: {len(file_info['content'])} characters)\n"

                        if comparison_summary:
                            enhanced_content += f"\n\n{comparison_summary}"

                        ai_response = await ai_service.process_chat_message(
                            user=current_user,
                            message=enhanced_content,
                            paper_context=paper,
                            user_papers_context=None,
                            personalization_settings=personalization,
                            db=db
                        )
                else:
                    logger.warning("⚠️ OpenAI selected but not enabled, falling back to Groq")
                    # Fallback to Groq
                    enhanced_content = content if content else "I've uploaded some files for you to analyze."
                    enhanced_content += "\n\n--- Uploaded Files ---\n"

                    for file_info in file_contents:
                        enhanced_content += f"\n**File: {file_info['filename']}** ({file_info['size'] / 1024:.1f} KB)\n"
                        enhanced_content += f"Content:\n{file_info['content'][:5000]}\n"
                        if len(file_info['content']) > 5000:
                            enhanced_content += f"... (truncated, total length: {len(file_info['content'])} characters)\n"

                    if comparison_summary:
                        enhanced_content += f"\n\n{comparison_summary}"

                    ai_response = await ai_service.process_chat_message(
                        user=current_user,
                        message=enhanced_content,
                        paper_context=paper,
                        user_papers_context=None,
                        personalization_settings=personalization,
                        db=db
                    )
            elif model == 'gpt-oss-120b':
                # User selected GPT-OSS 120B Local Model
                if gpt_oss_service.enabled:
                    logger.info("🚀 Using GPT-OSS 120B for file upload (user selected)")
                    try:
                        # Prepare paper context for GPT-OSS
                        paper_ctx = None
                        if paper:
                            paper_ctx = {
                                'title': paper.title,
                                'research_area': paper.research_area or '',
                                'status': paper.status.value if hasattr(paper.status, 'value') else str(paper.status),
                                'progress': paper.progress,
                                'current_word_count': paper.current_word_count,
                                'target_word_count': paper.target_word_count,
                            }

                        # Get personalization - prefer from form data over DB
                        personalization_dict = None
                        if personalization_settings_json:
                            personalization_dict = personalization_settings_json
                            logger.info(f"📊 Using personalization from request: {personalization_dict}")
                        else:
                            personalization_dict = get_user_personalization_settings(current_user)
                            logger.info(f"📊 Using personalization from database: {personalization_dict}")

                        # Fetch user's reference papers for style analysis
                        reference_papers = await get_user_reference_papers(db, current_user.id)

                        # Prepare message with file context
                        user_message_with_comparison = content if content else "I've uploaded files for analysis."
                        if comparison_summary:
                            user_message_with_comparison += f"\n\n{comparison_summary}"

                        # Generate response with GPT-OSS
                        gpt_oss_response = await gpt_oss_service.generate_response(
                            message=user_message_with_comparison,
                            files_content=file_contents,
                            personalization=personalization_dict,
                            paper_context=paper_ctx,
                            reference_papers=reference_papers
                        )

                        # Create response object
                        class GPTOSSResponseWrapper:
                            def __init__(self, gpt_oss_data):
                                self.messageId = gpt_oss_data.get('id', f"msg-gpt-oss-{int(time.time())}")
                                self.responseContent = gpt_oss_data.get('response', '')
                                self.createdAt = datetime.fromtimestamp(gpt_oss_data.get('created', time.time())).isoformat()
                                self.needsConfirmation = False
                                self.attachments = []
                                self.suggestions = []
                                self.metadata = {
                                    'model': gpt_oss_data.get('model', 'gpt-oss:120b'),
                                    'finish_reason': gpt_oss_data.get('finish_reason', 'stop'),
                                    'files_analyzed': len(file_contents)
                                }
                                if comparison_summary:
                                    self.metadata['file_comparison'] = comparison_summary

                        ai_response = GPTOSSResponseWrapper(gpt_oss_response)

                    except Exception as e:
                        logger.error(f"❌ GPT-OSS file upload error: {str(e)}")
                        raise AIServiceException(f"GPT-OSS service error: {str(e)}")
                else:
                    logger.warning("⚠️ GPT-OSS selected but not enabled, falling back to Groq")
                    enhanced_content = content if content else "I've uploaded some files for you to analyze."
                    enhanced_content += "\n\n--- Uploaded Files ---\n"

                    for file_info in file_contents:
                        enhanced_content += f"\n**File: {file_info['filename']}** ({file_info['size'] / 1024:.1f} KB)\n"
                        enhanced_content += f"Content:\n{file_info['content'][:5000]}\n"
                        if len(file_info['content']) > 5000:
                            enhanced_content += f"... (truncated, total length: {len(file_info['content'])} characters)\n"

                    if comparison_summary:
                        enhanced_content += f"\n\n{comparison_summary}"

                    ai_response = await ai_service.process_chat_message(
                        user=current_user,
                        message=enhanced_content,
                        paper_context=paper,
                        user_papers_context=None,
                        personalization_settings=personalization,
                        db=db
                    )
            else:
                # Default fallback to Groq
                logger.info(f"🤖 Using Groq/Llama (fallback for model: {model})")

                enhanced_content = content if content else "I've uploaded some files for you to analyze."
                enhanced_content += "\n\n--- Uploaded Files ---\n"

                for file_info in file_contents:
                    enhanced_content += f"\n**File: {file_info['filename']}** ({file_info['size'] / 1024:.1f} KB)\n"
                    enhanced_content += f"Content:\n{file_info['content'][:5000]}\n"
                    if len(file_info['content']) > 5000:
                        enhanced_content += f"... (truncated, total length: {len(file_info['content'])} characters)\n"

                if comparison_summary:
                    enhanced_content += f"\n\n{comparison_summary}"

                ai_response = await ai_service.process_chat_message(
                    user=current_user,
                    message=enhanced_content,
                    paper_context=paper,
                    user_papers_context=None,
                    personalization_settings=personalization,
                    db=db
                )

        # Save conversation to database and get message ID
        assistant_message_id = await save_chat_conversation(
            db,
            str(current_user.id),
            str(paper.id) if paper else None,
            f"{content}\n[{len(files)} file(s) uploaded]",
            ai_response.responseContent
        )

        logger.info(f"Successfully processed message with files for user {current_user.id}")

        return {
            "messageId": assistant_message_id or getattr(ai_response, 'messageId', f"msg-{current_user.id}-{int(time.time())}"),
            "responseContent": getattr(ai_response, 'responseContent', str(ai_response)),
            "createdAt": getattr(ai_response, 'createdAt', datetime.now().isoformat()),
            "needsConfirmation": getattr(ai_response, 'needsConfirmation', False),
            "attachments": getattr(ai_response, 'attachments', []),
            "suggestions": getattr(ai_response, 'suggestions', []),
            "metadata": getattr(ai_response, 'metadata', {
                'uploaded_files': [f['filename'] for f in file_contents]
            })
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in file upload for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your files"
        )


@router.get("/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    paper_id: Optional[str] = None,
    limit: int = 50
):
    """Get chat history for the current user."""

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

        # ✅ FIX: Manually convert to response format (avoid Pydantic validation issues)
        return [
            {
                "id": str(msg.id),  # ✅ Convert UUID to string
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
                "paper_id": str(msg.paper_id) if msg.paper_id else None,
                "attachments": [],  # ✅ Skip attachments to avoid lazy load
                "metadata": {}  # ✅ Return empty dict
            }
            for msg in messages
        ]

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
        # ✅ FIX: Eager load paper WITH sections to avoid lazy load error
        from uuid import UUID

        result = await db.execute(
            select(Paper)
            .options(selectinload(Paper.sections))  # ✅ Eager load sections!
            .where(Paper.id == UUID(request.paper_id))
        )
        paper = result.scalar_one_or_none()

        if not paper:
            raise NotFoundException(f"Paper {request.paper_id} not found")

        # Check permissions
        if not paper.is_viewable_by(str(current_user.id)):
            raise AuthorizationException("You don't have permission to edit this paper")

        # Now call service with loaded paper
        result = await section_content_service.add_chat_content_to_section(
            db=db,
            user_id=str(current_user.id),
            #paper=paper,  # Pass loaded paper object
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

        # Refresh to get the generated UUID
        await db.refresh(ai_msg)

        logger.info(f"✅ Successfully saved conversation for user {user_id}, assistant message ID: {ai_msg.id}")

        return str(ai_msg.id)  # Return the assistant message UUID

    except Exception as e:
        logger.error(f"Failed to save chat conversation: {str(e)}", exc_info=True)
        try:
            await db.rollback()
        except:
            pass
        # Don't raise - this is a background task
        # Failures here shouldn't affect the user's chat experience


@router.post("/feedback", response_model=MessageFeedbackResponse)
async def submit_message_feedback(
    feedback_request: MessageFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit user feedback on an AI message.

    Records whether a message was helpful or not helpful, which can be used to:
    - Improve future AI responses
    - Track message quality
    - Provide analytics on AI performance
    """
    try:
        from app.models.chat import ChatMessage
        from uuid import UUID
        from datetime import datetime

        logger.info(f"📝 Recording feedback for message {feedback_request.message_id}: {'helpful' if feedback_request.helpful else 'not helpful'}")

        # Get the message
        message_uuid = UUID(feedback_request.message_id)
        result = await db.execute(
            select(ChatMessage).filter(ChatMessage.id == message_uuid)
        )
        message = result.scalar_one_or_none()

        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )

        # Verify the message belongs to the current user
        if message.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to provide feedback on this message"
            )

        # Update feedback
        message.user_feedback = feedback_request.helpful
        message.feedback_timestamp = datetime.utcnow()

        await db.commit()
        await db.refresh(message)

        logger.info(f"✅ Feedback recorded successfully for message {feedback_request.message_id}")

        return MessageFeedbackResponse(
            success=True,
            message="Feedback recorded successfully",
            message_id=str(message.id),
            feedback=message.user_feedback,
            feedback_timestamp=message.feedback_timestamp.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to record feedback: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record feedback: {str(e)}"
        )