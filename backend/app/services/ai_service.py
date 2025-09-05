"""
AI service for chat, analysis, and research assistance
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from datetime import datetime, timedelta
import time
import json
import asyncio

from app.models.user import User
from app.models.paper import Paper, PaperSection
from app.models.chat import ChatMessage, ChatAttachment, PersonalizationSettings, AIInteraction
from app.schemas.chat import (
    ChatMessageResponse, PersonalizationSettingsBase,
    ResearchInsightsResponse, PaperOutlineResponse, WritingAnalysisResponse,
    SectionImprovementResponse, ChatMessageRequest
)
from app.external.openai_client import openai_client
from app.core.exceptions import AIServiceException, ValidationException
from app.core.config import settings


class AIService:
    """Service for AI-powered research assistance"""

    def __init__(self):
        self.default_model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.timeout = settings.AI_RESPONSE_TIMEOUT

    async def process_chat_message(
            self,
            user: User,
            message: str,
            paper_context: Optional[Paper] = None,
            user_papers_context: Optional[List[Dict[str, Any]]] = None,
            personalization_settings: Optional[PersonalizationSettingsBase] = None,
            db: AsyncSession = None
    ) -> ChatMessageResponse:
        """Process a chat message and generate AI response"""

        start_time = time.time()

        try:
            # Get or create personalization settings
            if not personalization_settings:
                personalization_settings = await self._get_user_personalization(db, user.id)

            # Build conversation context
            context = await self._build_conversation_context(
                user=user,
                paper_context=paper_context,
                user_papers_context=user_papers_context,
                personalization_settings=personalization_settings,
                db=db
            )

            # Get recent conversation history
            conversation_history = await self._get_recent_conversation_history(
                db=db,
                user_id=user.id,
                paper_id=paper_context.id if paper_context else None,
                limit=10
            )

            # Build messages for OpenAI
            messages = self._build_chat_messages(
                context=context,
                conversation_history=conversation_history,
                current_message=message,
                personalization_settings=personalization_settings
            )

            # Call OpenAI API
            ai_response = await openai_client.chat_completion(
                messages=messages,
                model=self.default_model,
                max_tokens=self.max_tokens,
                temperature=0.7
            )

            response_time = int((time.time() - start_time) * 1000)

            # Create response
            chat_response = ChatMessageResponse(
                message_id=f"ai_{int(time.time())}",
                response_content=ai_response['choices'][0]['message']['content'],
                needs_confirmation=self._needs_confirmation(ai_response['choices'][0]['message']['content']),
                attachments=[],
                suggestions=await self._generate_follow_up_suggestions(
                    message, ai_response['choices'][0]['message']['content'], paper_context
                ),
                created_at=datetime.utcnow(),
                metadata={
                    'model_used': ai_response.get('model'),
                    'prompt_tokens': ai_response.get('usage', {}).get('prompt_tokens', 0),
                    'completion_tokens': ai_response.get('usage', {}).get('completion_tokens', 0),
                    'response_time_ms': response_time
                }
            )

            # Log interaction for analytics
            if db:
                await self._log_ai_interaction(
                    db=db,
                    interaction_type="chat",
                    user_id=user.id,
                    paper_id=paper_context.id if paper_context else None,
                    model_used=ai_response.get('model'),
                    prompt_tokens=ai_response.get('usage', {}).get('prompt_tokens', 0),
                    completion_tokens=ai_response.get('usage', {}).get('completion_tokens', 0),
                    response_time_ms=response_time,
                    success=True
                )

            return chat_response

        except Exception as e:
            # Log failed interaction
            if db:
                await self._log_ai_interaction(
                    db=db,
                    interaction_type="chat",
                    user_id=user.id,
                    paper_id=paper_context.id if paper_context else None,
                    response_time_ms=int((time.time() - start_time) * 1000),
                    success=False,
                    error_message=str(e)
                )

            raise AIServiceException(f"Failed to process chat message: {str(e)}")

    async def generate_suggestions(
            self,
            user: User,
            paper: Optional[Paper] = None,
            db: AsyncSession = None
    ) -> List[str]:
        """Generate research suggestions based on user context"""

        try:
            if paper:
                prompt = f"""
                Based on this research paper context:
                Title: {paper.title}
                Research Area: {paper.research_area}
                Abstract: {paper.abstract}
                Progress: {paper.progress}%
                Status: {paper.status}

                Generate 5 specific, actionable research suggestions to help advance this work.
                Focus on methodology, literature gaps, and next steps.
                """
            else:
                user_research_areas = user.research_interests or []
                prompt = f"""
                For a researcher with interests in: {', '.join(user_research_areas)}

                Generate 5 current research suggestions including:
                - Emerging trends in these fields
                - Collaboration opportunities
                - Novel research questions
                - Methodological innovations
                """

            response = await openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.default_model,
                max_tokens=500,
                temperature=0.8
            )

            suggestions_text = response['choices'][0]['message']['content']
            # Parse suggestions (assume they're in a numbered or bulleted list)
            suggestions = self._parse_suggestions_from_text(suggestions_text)

            return suggestions[:5]  # Limit to 5 suggestions

        except Exception as e:
            # Return fallback suggestions
            return self._get_fallback_suggestions(paper)

    async def analyze_writing_patterns(
            self,
            user: User,
            paper: Optional[Paper] = None,
            db: AsyncSession = None
    ) -> WritingAnalysisResponse:
        """Analyze user's writing patterns and provide insights"""

        try:
            if paper:
                # Analyze specific paper
                content = paper.abstract
                for section in paper.sections:
                    content += f"\n\n{section.content}"
            else:
                # Analyze across all user papers
                user_papers = await db.execute(
                    select(Paper).where(Paper.owner_id == user.id).limit(5)
                )
                papers = user_papers.scalars().all()
                content = ""
                for p in papers:
                    content += f"{p.abstract}\n"
                    for section in p.sections:
                        content += f"{section.content}\n"

            if not content.strip():
                return WritingAnalysisResponse(
                    suggestions=["Add more content to enable writing analysis"]
                )

            # Use AI to analyze writing patterns
            prompt = f"""
            Analyze this academic writing and provide insights on:
            1. Writing patterns and style
            2. Strengths and areas for improvement
            3. Readability and clarity
            4. Academic tone and vocabulary
            5. Structure and organization

            Text to analyze:
            {content[:2000]}  # Limit to avoid token limits

            Provide specific, actionable feedback.
            """

            response = await openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.default_model,
                max_tokens=800,
                temperature=0.3
            )

            analysis_text = response['choices'][0]['message']['content']

            # Parse analysis (this would be more sophisticated in production)
            return WritingAnalysisResponse(
                writing_patterns={"analysis": analysis_text},
                suggestions=self._extract_suggestions_from_analysis(analysis_text),
                readability_score=self._calculate_readability_score(content),
                word_frequency=self._get_word_frequency(content),
                improvement_areas=self._extract_improvement_areas(analysis_text)
            )

        except Exception as e:
            raise AIServiceException(f"Failed to analyze writing patterns: {str(e)}")

    async def generate_paper_outline(
            self,
            paper: Paper,
            user: User,
            db: AsyncSession = None
    ) -> PaperOutlineResponse:
        """Generate AI-powered paper outline"""

        try:
            prompt = f"""
            Create a detailed outline for this research paper:

            Title: {paper.title}
            Research Area: {paper.research_area}
            Abstract: {paper.abstract}
            Target Word Count: {paper.target_word_count}

            Generate:
            1. Section structure with titles and descriptions
            2. Estimated word counts for each section
            3. Research timeline with phases

            Format as JSON with sections and timeline arrays.
            """

            response = await openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.default_model,
                max_tokens=1000,
                temperature=0.5
            )

            try:
                outline_data = json.loads(response['choices'][0]['message']['content'])
                return PaperOutlineResponse(**outline_data)
            except json.JSONDecodeError:
                # Fallback to parsing text response
                return self._parse_outline_from_text(response['choices'][0]['message']['content'])

        except Exception as e:
            raise AIServiceException(f"Failed to generate outline: {str(e)}")

    async def improve_section_content(
            self,
            section: PaperSection,
            paper: Paper,
            user: User,
            db: AsyncSession = None
    ) -> SectionImprovementResponse:
        """Get AI suggestions to improve a specific paper section"""

        try:
            prompt = f"""
            Review and suggest improvements for this paper section:

            Paper Title: {paper.title}
            Research Area: {paper.research_area}
            Section Title: {section.title}
            Current Content: {section.content}

            Provide:
            1. Specific improvement suggestions
            2. Clarity and coherence feedback
            3. Content gaps to address
            4. Structure recommendations

            Focus on academic writing quality and research rigor.
            """

            response = await openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.default_model,
                max_tokens=600,
                temperature=0.4
            )

            improvement_text = response['choices'][0]['message']['content']

            return SectionImprovementResponse(
                improvements=self._extract_improvements_from_text(improvement_text),
                suggestions=self._extract_suggestions_from_text(improvement_text),
                clarity_score=self._calculate_clarity_score(section.content),
                coherence_feedback=self._extract_coherence_feedback(improvement_text)
            )

        except Exception as e:
            raise AIServiceException(f"Failed to analyze section: {str(e)}")

    async def get_chat_history(
            self,
            db: AsyncSession,
            user_id: str,
            paper_id: Optional[str] = None,
            limit: int = 50
    ) -> List[ChatMessage]:
        """Get chat history for user/paper"""

        query = select(ChatMessage).where(ChatMessage.user_id == user_id)

        if paper_id:
            query = query.where(ChatMessage.paper_id == paper_id)

        query = query.order_by(desc(ChatMessage.created_at)).limit(limit)

        result = await db.execute(query)
        messages = result.scalars().all()

        return list(reversed(messages))  # Return in chronological order

    async def get_message_by_id(self, db: AsyncSession, message_id: str) -> Optional[ChatMessage]:
        """Get specific chat message by ID"""

        result = await db.execute(
            select(ChatMessage).where(ChatMessage.id == message_id)
        )
        return result.scalar_one_or_none()

    async def delete_message(self, db: AsyncSession, message_id: str) -> bool:
        """Delete a chat message"""

        message = await self.get_message_by_id(db, message_id)
        if not message:
            return False

        await db.delete(message)
        await db.commit()
        return True

    async def clear_chat_history(
            self,
            db: AsyncSession,
            user_id: str,
            paper_id: Optional[str] = None
    ) -> bool:
        """Clear chat history for user/paper"""

        query = select(ChatMessage).where(ChatMessage.user_id == user_id)

        if paper_id:
            query = query.where(ChatMessage.paper_id == paper_id)

        result = await db.execute(query)
        messages = result.scalars().all()

        for message in messages:
            await db.delete(message)

        await db.commit()
        return True

    # Private helper methods
    async def _get_user_personalization(
            self,
            db: AsyncSession,
            user_id: str
    ) -> PersonalizationSettingsBase:
        """Get user's personalization settings"""

        result = await db.execute(
            select(PersonalizationSettings).where(PersonalizationSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()

        if settings:
            return PersonalizationSettingsBase(**settings.to_settings_dict())
        else:
            # Return default settings
            return PersonalizationSettingsBase()

    async def _build_conversation_context(
            self,
            user: User,
            paper_context: Optional[Paper],
            user_papers_context: Optional[List[Dict[str, Any]]],
            personalization_settings: PersonalizationSettingsBase,
            db: AsyncSession
    ) -> str:
        """Build context string for AI conversation"""

        context_parts = []

        # User context
        context_parts.append(f"User: {user.name}")
        context_parts.append(f"Research Interests: {', '.join(user.research_interests or [])}")
        context_parts.append(f"Writing Style Preference: {personalization_settings.writing_style}")

        # Paper context
        if paper_context:
            context_parts.append(f"\nCurrent Paper Context:")
            context_parts.append(f"Title: {paper_context.title}")
            context_parts.append(f"Research Area: {paper_context.research_area}")
            context_parts.append(f"Status: {paper_context.status}")
            context_parts.append(f"Progress: {paper_context.progress}%")
            context_parts.append(f"Abstract: {paper_context.abstract}")

        # User's other papers context
        if user_papers_context:
            context_parts.append(f"\nUser's Other Research:")
            for paper_info in user_papers_context[:3]:  # Limit to 3 for context size
                context_parts.append(f"- {paper_info.get('title')} ({paper_info.get('research_area')})")

        return "\n".join(context_parts)

    async def _get_recent_conversation_history(
            self,
            db: AsyncSession,
            user_id: str,
            paper_id: Optional[str],
            limit: int = 10
    ) -> List[ChatMessage]:
        """Get recent conversation history"""

        query = select(ChatMessage).where(ChatMessage.user_id == user_id)

        if paper_id:
            query = query.where(ChatMessage.paper_id == paper_id)

        query = query.order_by(desc(ChatMessage.created_at)).limit(limit)

        result = await db.execute(query)
        messages = result.scalars().all()

        return list(reversed(messages))

    def _build_chat_messages(
            self,
            context: str,
            conversation_history: List[ChatMessage],
            current_message: str,
            personalization_settings: PersonalizationSettingsBase
    ) -> List[Dict[str, str]]:
        """Build messages array for OpenAI API"""

        messages = []

        # System message with context
        system_content = f"""You are an AI research assistant helping academic researchers. 

Context:
{context}

Guidelines:
- Provide helpful, accurate research assistance
- Match the user's preferred writing style: {personalization_settings.writing_style}
- Be concise but thorough
- Suggest specific, actionable next steps
- Cite relevant research when possible
- Ask clarifying questions when needed
"""

        messages.append({"role": "system", "content": system_content})

        # Add recent conversation history
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })

        # Add current message
        messages.append({"role": "user", "content": current_message})

        return messages

    def _needs_confirmation(self, response_content: str) -> bool:
        """Determine if AI response needs user confirmation"""

        confirmation_keywords = [
            "delete", "remove", "overwrite", "replace all",
            "publish", "submit", "send email", "share publicly"
        ]

        return any(keyword in response_content.lower() for keyword in confirmation_keywords)

    async def _generate_follow_up_suggestions(
            self,
            user_message: str,
            ai_response: str,
            paper_context: Optional[Paper]
    ) -> List[str]:
        """Generate follow-up question suggestions"""

        suggestions = [
            "Can you elaborate on that?",
            "What are the next steps?",
            "Any potential challenges to consider?"
        ]

        if paper_context:
            suggestions.extend([
                f"How does this apply to my {paper_context.research_area} research?",
                "Can you help me implement this suggestion?",
                "What resources would I need for this?"
            ])

        return suggestions[:3]

    async def _log_ai_interaction(
            self,
            db: AsyncSession,
            interaction_type: str,
            user_id: str,
            paper_id: Optional[str] = None,
            model_used: Optional[str] = None,
            prompt_tokens: int = 0,
            completion_tokens: int = 0,
            response_time_ms: Optional[int] = None,
            success: bool = True,
            error_message: Optional[str] = None
    ):
        """Log AI interaction for analytics"""

        try:
            interaction = AIInteraction.create_interaction(
                interaction_type=interaction_type,
                user_id=user_id,
                paper_id=paper_id,
                model_used=model_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                response_time_ms=response_time_ms,
                success=success,
                error_message=error_message
            )

            db.add(interaction)
            await db.commit()
        except Exception as e:
            # Don't fail the main operation if logging fails
            print(f"Failed to log AI interaction: {e}")

    def _get_fallback_suggestions(self, paper: Optional[Paper] = None) -> List[str]:
        """Get fallback suggestions when AI is unavailable"""

        if paper:
            return [
                f"Review recent publications in {paper.research_area}",
                "Consider expanding your methodology section",
                "Validate your current results with additional data",
                "Explore potential collaboration opportunities",
                "Document your research process more thoroughly"
            ]
        else:
            return [
                "Explore emerging trends in your field",
                "Consider interdisciplinary research opportunities",
                "Review and update your literature knowledge",
                "Network with researchers in related areas",
                "Plan your next research project"
            ]

    def _parse_suggestions_from_text(self, text: str) -> List[str]:
        """Parse suggestions from AI text response"""

        lines = text.strip().split('\n')
        suggestions = []

        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                # Remove bullet points and numbers
                clean_line = line.lstrip('-•0123456789. ').strip()
                if clean_line:
                    suggestions.append(clean_line)

        return suggestions

    def _extract_suggestions_from_analysis(self, analysis_text: str) -> List[str]:
        """Extract actionable suggestions from writing analysis"""

        # Simple extraction - in production, this would be more sophisticated
        suggestions = []
        lines = analysis_text.split('\n')

        for line in lines:
            if 'suggest' in line.lower() or 'recommend' in line.lower():
                suggestions.append(line.strip())

        return suggestions[:5]

    def _calculate_readability_score(self, content: str) -> Optional[float]:
        """Calculate basic readability score"""

        if not content:
            return None

        # Simple readability calculation (Flesch Reading Ease approximation)
        words = len(content.split())
        sentences = content.count('.') + content.count('!') + content.count('?')

        if sentences == 0:
            return None

        avg_sentence_length = words / sentences
        # Simplified score (would use more sophisticated calculation in production)
        score = max(0, min(100, 206.835 - (1.015 * avg_sentence_length)))

        return round(score, 2)

    def _get_word_frequency(self, content: str) -> Dict[str, int]:
        """Get word frequency analysis"""

        words = content.lower().split()
        frequency = {}

        # Filter out common words and get top words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is',
                        'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                        'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}

        for word in words:
            if word not in common_words and len(word) > 3:
                frequency[word] = frequency.get(word, 0) + 1

        # Return top 10 words
        sorted_words = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_words[:10])

    def _extract_improvement_areas(self, analysis_text: str) -> List[str]:
        """Extract improvement areas from analysis text"""

        improvement_keywords = ['improve', 'enhance', 'strengthen', 'clarify', 'expand', 'revise']
        areas = []

        lines = analysis_text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in improvement_keywords):
                areas.append(line.strip())

        return areas[:5]

    def _parse_outline_from_text(self, outline_text: str) -> PaperOutlineResponse:
        """Parse outline from text when JSON parsing fails"""

        # Fallback outline structure
        sections = [
            {"title": "Introduction", "description": "Background and objectives", "estimatedWords": 1000},
            {"title": "Literature Review", "description": "Critical analysis of existing research",
             "estimatedWords": 1500},
            {"title": "Methodology", "description": "Research design and methods", "estimatedWords": 1200},
            {"title": "Results", "description": "Presentation of findings", "estimatedWords": 1500},
            {"title": "Discussion", "description": "Interpretation and implications", "estimatedWords": 1300},
            {"title": "Conclusion", "description": "Summary and future directions", "estimatedWords": 500}
        ]

        timeline = [
            {"phase": "Planning", "duration": "2 weeks", "description": "Literature review and methodology design"},
            {"phase": "Data Collection", "duration": "4 weeks", "description": "Gather and validate research data"},
            {"phase": "Analysis", "duration": "3 weeks", "description": "Process data and generate results"},
            {"phase": "Writing", "duration": "4 weeks", "description": "Draft and revise manuscript"},
            {"phase": "Review", "duration": "2 weeks", "description": "Final review and submission preparation"}
        ]

        return PaperOutlineResponse(sections=sections, timeline=timeline)

    def _extract_improvements_from_text(self, improvement_text: str) -> List[str]:
        """Extract specific improvements from text"""

        improvements = []
        lines = improvement_text.split('\n')

        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or 'improve' in line.lower()):
                clean_line = line.lstrip('-•0123456789. ').strip()
                if clean_line and len(clean_line) > 10:
                    improvements.append(clean_line)

        return improvements[:5]

    def _extract_suggestions_from_text(self, text: str) -> List[str]:
        """Extract suggestions from text"""

        suggestions = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if 'suggest' in line.lower() or 'recommend' in line.lower() or 'consider' in line.lower():
                clean_line = line.lstrip('-•0123456789. ').strip()
                if clean_line and len(clean_line) > 10:
                    suggestions.append(clean_line)

        return suggestions[:5]

    def _calculate_clarity_score(self, content: str) -> Optional[float]:
        """Calculate a basic clarity score for content"""

        if not content or len(content.strip()) < 50:
            return None

        # Simple clarity metrics
        words = content.split()
        sentences = content.count('.') + content.count('!') + content.count('?')

        if sentences == 0:
            return None

        avg_sentence_length = len(words) / sentences
        long_words = sum(1 for word in words if len(word) > 6)
        long_word_ratio = long_words / len(words) if words else 0

        # Simple scoring algorithm (higher is better)
        # Penalize very long sentences and too many long words
        clarity_score = 100

        if avg_sentence_length > 25:
            clarity_score -= (avg_sentence_length - 25) * 2

        if long_word_ratio > 0.3:
            clarity_score -= (long_word_ratio - 0.3) * 100

        return max(0, min(100, round(clarity_score, 2)))

    def _extract_coherence_feedback(self, improvement_text: str) -> Optional[str]:
        """Extract coherence feedback from improvement text"""

        lines = improvement_text.split('\n')

        for line in lines:
            if any(word in line.lower() for word in ['coherence', 'flow', 'structure', 'organization', 'logical']):
                return line.strip()

        return None


# Create global service instance
ai_service = AIService()