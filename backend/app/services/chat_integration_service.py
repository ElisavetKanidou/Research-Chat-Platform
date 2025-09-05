
"""
Complete Chat Service Integration (app/services/chat_integration_service.py)
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.paper import Paper
from app.services.ai_service import ai_service
from app.external.openai_client import openai_client


class ChatIntegrationService:
    """Service to integrate with frontend chat expectations"""

    async def process_frontend_chat_request(
        self,
        db: AsyncSession,
        user: User,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process chat request in format expected by frontend"""

        # Extract frontend request data
        content = request_data.get("content")
        paper_context = request_data.get("paperContext")
        user_papers_context = request_data.get("userPapersContext", [])
        personalization_settings = request_data.get("personalizationSettings", {})

        # Convert to backend format
        paper = None
        if paper_context and paper_context.get("id"):
            paper = await db.get(Paper, paper_context["id"])

        # Process through AI service
        ai_response = await ai_service.process_chat_message(
            user=user,
            message=content,
            paper_context=paper,
            user_papers_context=user_papers_context,
            personalization_settings=personalization_settings,
            db=db
        )

        # Convert to frontend format
        return {
            "messageId": ai_response.message_id,
            "responseContent": ai_response.response_content,
            "needsConfirmation": ai_response.needs_confirmation,
            "attachments": [
                {
                    "type": att.type,
                    "name": att.name,
                    "size": att.size,
                    "url": att.url
                }
                for att in ai_response.attachments
            ],
            "suggestions": ai_response.suggestions,
            "createdAt": ai_response.created_at.isoformat(),
            "metadata": ai_response.metadata or {}
        }


# Global service instance
chat_integration_service = ChatIntegrationService()

