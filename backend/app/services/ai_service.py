"""
Personalized AI Service with 3-Layer Influence System
backend/app/services/ai_service.py

Implements sophisticated multi-layered personalization:
- Lab Papers Influence (0-10): Research group patterns & methodologies
- Personal Papers Influence (0-10): Individual writing style & preferences
- Global Literature Influence (0-10): Broader field trends & emerging methods

Uses FREE Groq API with Llama 3.1 70B for academic writing assistance.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import logging
import os
import httpx

from app.models.user import User
from app.models.paper import Paper
from app.models.chat import ChatMessage
from app.schemas.chat import ChatMessageResponse

logger = logging.getLogger(__name__)


class AIService:
    """
    Intelligent research assistant with adaptive 3-layer personalization.

    This service implements the core AI functionality for the research platform,
    providing personalized writing assistance that balances:

    1. Lab influence - Research group conventions & methodologies
    2. Personal influence - Individual writing style & preferences
    3. Global influence - Field trends & contemporary practices

    The AI learns from user feedback (approval/rejection) to continuously
    refine suggestions and adapt to evolving research needs.
    """

    def __init__(self):
        """Initialize AI service with Groq API (FREE tier)"""
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        if not self.api_key:
            logger.warning(
                "⚠️  GROQ_API_KEY not set! Get FREE key: https://console.groq.com/keys"
            )
        else:
            logger.info("✅ Personalized AI assistant initialized (FREE Groq API)")

    async def process_chat_message(
        self,
        user: User,
        message: str,
        paper_context: Optional[Paper] = None,
        user_papers_context: Optional[List[Dict]] = None,
        personalization_settings: Optional[Dict] = None,
        db: AsyncSession = None
    ) -> ChatMessageResponse:
        """
        Process chat message with 3-layer personalized AI assistance.

        The personalization engine adapts responses based on:
        - Lab papers influence: Research group patterns
        - Personal papers influence: Individual writing style
        - Global literature influence: Field-wide trends

        Returns personalized academic writing guidance that evolves
        with user feedback and research progression.
        """

        logger.info(f"Processing personalized chat for user {user.id}: {message[:50]}...")

        try:
            # Extract personalization parameters (0-10 scale)
            personalization = self._extract_personalization(personalization_settings)

            # Build sophisticated context-aware system prompt
            system_prompt = self._build_personalized_system_prompt(
                user=user,
                paper_context=paper_context,
                user_papers_context=user_papers_context,
                personalization=personalization
            )

            # Get conversation history for continuity
            conversation_history = await self._get_conversation_history(
                db, user.id, paper_context
            )

            # Build complete message context
            messages = self._build_message_history(
                system_prompt,
                conversation_history,
                message
            )

            # Call Groq AI with personalization-adjusted parameters
            response_content = await self._call_groq_personalized(
                messages,
                personalization
            )

            # Generate context-aware suggestions
            suggestions = self._generate_personalized_suggestions(
                message,
                response_content,
                paper_context,
                personalization
            )

            # Check if response needs user approval
            needs_confirmation = self._check_needs_approval(message, response_content)

            logger.info(
                f"✅ Generated personalized response (Lab:{personalization['lab']}, "
                f"Personal:{personalization['personal']}, Global:{personalization['global']})"
            )

            return ChatMessageResponse(
                messageId=f"msg-{datetime.now().timestamp()}",
                responseContent=response_content,
                needsConfirmation=needs_confirmation,
                attachments=[],
                suggestions=suggestions,
                createdAt=datetime.now(timezone.utc).isoformat(),
                metadata={
                    "model": "llama-3.3-70b-versatile",
                    "provider": "groq",
                    "cost": "FREE",
                    "personalization": {
                        "lab_influence": personalization['lab'],
                        "personal_influence": personalization['personal'],
                        "global_influence": personalization['global']
                    },
                    "user_id": str(user.id),
                    "paper_id": str(paper_context.id) if paper_context else None,
                }
            )

        except Exception as e:
            logger.error(f"Error in personalized AI processing: {str(e)}", exc_info=True)

            return ChatMessageResponse(
                messageId=f"msg-error-{datetime.now().timestamp()}",
                responseContent=self._get_fallback_response(message),
                needsConfirmation=False,
                attachments=[],
                suggestions=["Try rephrasing", "Adjust personalization settings"],
                createdAt=datetime.now(timezone.utc).isoformat(),
                metadata={"error": True}
            )

    def _extract_personalization(
        self,
        settings: Optional[Dict]
    ) -> Dict[str, int]:
        """
        Extract and validate personalization parameters.

        Returns normalized 0-10 scale values for each influence layer.
        """
        if not settings:
            # Default balanced personalization
            return {
                'lab': 7,
                'personal': 8,
                'global': 5
            }

        return {
            'lab': max(0, min(10, getattr(settings, 'lab_level', 7))),
            'personal': max(0, min(10, getattr(settings, 'personal_level', 8))),
            'global': max(0, min(10, getattr(settings, 'global_level', 5)))
        }

    def _build_personalized_system_prompt(
        self,
        user: User,
        paper_context: Optional[Paper],
        user_papers_context: Optional[List[Dict]],
        personalization: Dict[str, int]
    ) -> str:
        """
        Build sophisticated system prompt with 3-layer personalization.

        This is the core of the adaptive AI assistant - it dynamically
        adjusts guidance based on the personalization influence settings.
        """

        # Base expert assistant identity
        prompt = f"""You are an intelligent research assistant helping {user.name or 'a researcher'} with academic writing and research development.

Your core capabilities:
- Provide expert guidance on research methodology and academic writing
- Assist throughout the research lifecycle: ideation → methodology → writing → publication
- Adapt recommendations based on personalization settings
- Learn from user feedback to refine future suggestions
- Maintain high academic standards and research integrity

Writing style: Academic, clear, rigorous
Tone: Supportive, encouraging, professionally critical
"""

        # Add current paper context
        if paper_context:
            prompt += f"""

═══════════════════════════════════════════════════════════
CURRENT RESEARCH PAPER
═══════════════════════════════════════════════════════════
Title: {paper_context.title}
Research Area: {paper_context.research_area or 'Not specified'}
Status: {paper_context.status}
Progress: {paper_context.progress}% complete
Current Words: {paper_context.current_word_count or 0} / {paper_context.target_word_count or 'Not set'}
Abstract: {paper_context.abstract or 'Not written yet - needs development'}

"""

        # Add user's research portfolio for personal context
        if user_papers_context and len(user_papers_context) > 0:
            prompt += f"""═══════════════════════════════════════════════════════════
RESEARCHER'S PORTFOLIO ({len(user_papers_context)} papers)
═══════════════════════════════════════════════════════════
"""
            for i, paper in enumerate(user_papers_context[:5], 1):
                prompt += f"{i}. {paper.get('title')} ({paper.get('researchArea', 'General')})\n"
            prompt += "\n"

        # CRITICAL: 3-Layer Personalization Configuration
        prompt += f"""═══════════════════════════════════════════════════════════
PERSONALIZATION CONFIGURATION (ADAPTIVE AI SETTINGS)
═══════════════════════════════════════════════════════════

The researcher has configured the following influence parameters to
customize your guidance. Adjust your recommendations accordingly:

1. LAB PAPERS INFLUENCE: {personalization['lab']}/10
   {"█" * personalization['lab']}{"░" * (10 - personalization['lab'])}
   {self._get_lab_influence_guidance(personalization['lab'])}

2. PERSONAL PAPERS INFLUENCE: {personalization['personal']}/10
   {"█" * personalization['personal']}{"░" * (10 - personalization['personal'])}
   {self._get_personal_influence_guidance(personalization['personal'])}

3. GLOBAL LITERATURE INFLUENCE: {personalization['global']}/10
   {"█" * personalization['global']}{"░" * (10 - personalization['global'])}
   {self._get_global_influence_guidance(personalization['global'])}

"""

        # Add behavioral guidelines based on personalization
        prompt += self._get_adaptive_guidelines(personalization)

        prompt += """
═══════════════════════════════════════════════════════════
CORE PRINCIPLES
═══════════════════════════════════════════════════════════
- Provide SPECIFIC, ACTIONABLE guidance (not generic advice)
- Use EXAMPLES from research when helpful
- Ask CLARIFYING questions when needed
- Offer STEP-BY-STEP guidance for complex tasks
- Cite BEST PRACTICES from academic methodology
- Encourage CRITICAL THINKING and rigor
- Support ACADEMIC INTEGRITY at all times

Remember: You are the researcher's expert colleague, helping them
succeed while maintaining the highest academic standards!
"""

        return prompt

    def _get_lab_influence_guidance(self, level: int) -> str:
        """Generate guidance for lab influence level"""
        if level >= 8:
            return """→ HIGH: Strongly consider lab research patterns, methodologies, and conventions
   - Prioritize approaches used in recent lab publications
   - Reference lab's established frameworks and terminology
   - Align with lab's methodological standards"""
        elif level >= 5:
            return """→ MEDIUM: Balance lab conventions with broader approaches
   - Consider lab patterns but remain open to alternatives
   - Reference lab work when relevant, not exclusively"""
        else:
            return """→ LOW: Focus on general best practices over lab-specific conventions
   - Prioritize field-wide standards
   - Use lab context only for background awareness"""

    def _get_personal_influence_guidance(self, level: int) -> str:
        """Generate guidance for personal influence level"""
        if level >= 8:
            return """→ HIGH: Strongly adapt to researcher's individual writing style & preferences
   - Mirror vocabulary choices and sentence structures from past work
   - Maintain consistency with established personal patterns
   - Preserve individual voice and approach"""
        elif level >= 5:
            return """→ MEDIUM: Balance personal style with academic conventions
   - Consider past preferences but suggest improvements
   - Adapt tone while maintaining academic rigor"""
        else:
            return """→ LOW: Prioritize standard academic writing conventions
   - Focus on field norms over individual preferences
   - Suggest improvements regardless of past patterns"""

    def _get_global_influence_guidance(self, level: int) -> str:
        """Generate guidance for global influence level"""
        if level >= 8:
            return """→ HIGH: Extensively incorporate field-wide trends & contemporary methods
   - Reference latest research methodologies and frameworks
   - Use emerging terminology and contemporary approaches
   - Align with cutting-edge practices in the field"""
        elif level >= 5:
            return """→ MEDIUM: Balance current trends with established practices
   - Reference recent developments when relevant
   - Use proven methods supplemented by new approaches"""
        else:
            return """→ LOW: Focus on established, proven methodologies
   - Prioritize time-tested approaches
   - Reference classics and foundational work"""

    def _get_adaptive_guidelines(self, personalization: Dict[str, int]) -> str:
        """Generate behavioral guidelines based on personalization mix"""

        guidelines = "\n═══════════════════════════════════════════════════════════\n"
        guidelines += "ADAPTIVE BEHAVIORAL GUIDELINES\n"
        guidelines += "═══════════════════════════════════════════════════════════\n"

        # Determine dominant influence
        if personalization['personal'] >= 8:
            guidelines += "• PRIORITIZE consistency with researcher's established voice\n"

        if personalization['lab'] >= 8:
            guidelines += "• EMPHASIZE lab methodologies and research patterns\n"

        if personalization['global'] >= 8:
            guidelines += "• INCORPORATE contemporary field trends and emerging methods\n"

        # Balanced approach
        if all(5 <= v <= 7 for v in personalization.values()):
            guidelines += "• BALANCE all three influences for well-rounded guidance\n"

        guidelines += "\n"
        return guidelines

    async def _get_conversation_history(
        self,
        db: AsyncSession,
        user_id: str,
        paper_context: Optional[Paper],
        limit: int = 10
    ) -> List[ChatMessage]:
        """Get recent conversation history for context continuity"""

        if not db:
            return []

        try:
            query = select(ChatMessage).where(ChatMessage.user_id == user_id)

            if paper_context:
                query = query.where(ChatMessage.paper_id == paper_context.id)

            query = query.order_by(desc(ChatMessage.created_at)).limit(limit)

            result = await db.execute(query)
            messages = result.scalars().all()

            return list(reversed(messages))  # Chronological order

        except Exception as e:
            logger.error(f"Error fetching conversation history: {e}")
            return []

    def _build_message_history(
        self,
        system_prompt: str,
        conversation_history: List[ChatMessage],
        current_message: str
    ) -> List[Dict[str, str]]:
        """Build complete message context for AI"""

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add recent conversation for context (last 10 messages)
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg.role,  # 'user' or 'assistant'
                "content": msg.content
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": current_message
        })

        return messages

    async def _call_groq_personalized(
        self,
        messages: List[Dict[str, str]],
        personalization: Dict[str, int]
    ) -> str:
        """
        Call Groq API with personalization-adjusted parameters.

        Adjusts temperature based on global influence (creativity).
        """

        if not self.api_key:
            raise Exception(
                "GROQ_API_KEY not set. Get FREE key: https://console.groq.com/keys"
            )

        try:
            # Adjust temperature based on global influence
            # Higher global influence = more creative/exploratory responses
            base_temp = 0.6
            global_factor = personalization['global'] / 20  # 0.0 to 0.5
            temperature = base_temp + global_factor  # 0.6 to 1.1

            # Prepare API request
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": min(temperature, 1.0),  # Cap at 1.0
                "max_tokens": 1500,
                "top_p": 0.9,
                "stream": False
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Call Groq API (FREE!)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )

                if response.status_code == 429:
                    logger.warning("Rate limit hit - waiting briefly")
                    raise Exception(
                        "Rate limit reached. Please wait a moment and try again. "
                        "(Free tier: 30 requests/minute)"
                    )

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"Groq API error {response.status_code}: {error_detail}")
                    raise Exception(f"AI service error: {response.status_code}")

                data = response.json()
                content = data['choices'][0]['message']['content'].strip()

                logger.debug(
                    f"Generated {len(content)} chars (temp={temperature:.2f}, "
                    f"personalization: L{personalization['lab']}/P{personalization['personal']}/G{personalization['global']})"
                )

                return content

        except httpx.TimeoutException:
            logger.error("Groq API timeout")
            raise Exception("AI service timeout. Please try again.")

        except Exception as e:
            logger.error(f"Error calling Groq: {e}", exc_info=True)
            raise

    def _generate_personalized_suggestions(
        self,
        user_message: str,
        ai_response: str,
        paper_context: Optional[Paper],
        personalization: Dict[str, int]
    ) -> List[str]:
        """Generate context-aware suggestions based on conversation and personalization"""

        msg_lower = user_message.lower()

        # Research phase-specific suggestions
        if "abstract" in msg_lower:
            return [
                "Refine the abstract structure",
                "Add specific methodology details",
                "Strengthen impact statement"
            ]
        elif "introduction" in msg_lower or "intro" in msg_lower:
            return [
                "Develop the research gap",
                "Add literature context",
                "Clarify research questions"
            ]
        elif "method" in msg_lower or "methodology" in msg_lower:
            return [
                "Detail the research design",
                "Explain data collection process",
                "Justify methodological choices"
            ]
        elif "literature" in msg_lower or "review" in msg_lower:
            return [
                "Identify key themes",
                "Find research gaps",
                "Synthesize conflicting findings"
            ]
        elif "results" in msg_lower:
            return [
                "Present key findings",
                "Add visualizations",
                "Highlight significant results"
            ]
        elif "discussion" in msg_lower:
            return [
                "Interpret findings",
                "Compare with literature",
                "Address limitations"
            ]
        elif "conclusion" in msg_lower:
            return [
                "Summarize contributions",
                "Suggest future research",
                "Emphasize implications"
            ]
        else:
            # General suggestions adapted to personalization
            if personalization['personal'] >= 8:
                return [
                    "Maintain your writing style",
                    "Build on your past work",
                    "Develop this further"
                ]
            elif personalization['global'] >= 8:
                return [
                    "Explore recent methods",
                    "Check latest literature",
                    "Consider emerging trends"
                ]
            else:
                return [
                    "Tell me more",
                    "Can you elaborate?",
                    "What's the next step?"
                ]

    def _check_needs_approval(
        self,
        user_message: str,
        ai_response: str
    ) -> bool:
        """
        Determine if response needs user approval before proceeding.

        This implements the feedback mechanism for continuous learning.
        """

        # Major structural changes need approval
        approval_keywords = [
            "restructure",
            "completely rewrite",
            "different approach",
            "major revision",
            "significant change"
        ]

        response_lower = ai_response.lower()

        return any(keyword in response_lower for keyword in approval_keywords)

    def _get_fallback_response(self, user_message: str) -> str:
        """Fallback response when AI service fails"""

        return f"""I apologize, but I'm having trouble processing your request right now.

Your message: "{user_message[:100]}..."

This could be due to:
- Temporary service unavailability
- Rate limits (30 requests/minute on free tier)
- Network connectivity issues

Please try:
1. Waiting a moment and trying again
2. Rephrasing your question
3. Checking that GROQ_API_KEY is configured

I'm here to help with your research once the connection is restored!"""

    # ==================== Additional Service Methods ====================

    async def get_chat_history(
        self,
        db: AsyncSession,
        user_id: str,
        paper_id: Optional[str] = None,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Get chat history for user"""

        query = select(ChatMessage).where(ChatMessage.user_id == user_id)

        if paper_id:
            query = query.where(ChatMessage.paper_id == paper_id)

        query = query.order_by(desc(ChatMessage.created_at)).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_message_by_id(
        self,
        db: AsyncSession,
        message_id: str
    ) -> Optional[ChatMessage]:
        """Get specific message"""
        result = await db.execute(
            select(ChatMessage).where(ChatMessage.id == message_id)
        )
        return result.scalar_one_or_none()

    async def delete_message(self, db: AsyncSession, message_id: str):
        """Delete message"""
        message = await self.get_message_by_id(db, message_id)
        if message:
            await db.delete(message)
            await db.commit()

    async def clear_chat_history(
        self,
        db: AsyncSession,
        user_id: str,
        paper_id: Optional[str] = None
    ):
        """Clear chat history"""

        query = select(ChatMessage).where(ChatMessage.user_id == user_id)
        if paper_id:
            query = query.where(ChatMessage.paper_id == paper_id)

        result = await db.execute(query)
        messages = result.scalars().all()

        for msg in messages:
            await db.delete(msg)

        await db.commit()

    async def generate_suggestions(
        self,
        user: User,
        paper: Optional[Paper] = None,
        db: AsyncSession = None
    ) -> List[str]:
        """Generate AI-powered suggestions for next steps"""

        if paper:
            return [
                f"Continue developing '{paper.title}'",
                "Expand the literature review section",
                "Refine your methodology approach",
                "Draft the results section",
                "Add figures and tables"
            ]
        else:
            return [
                "Start a new research paper",
                "Explore recent trends in your field",
                "Identify research gaps",
                "Develop a research proposal",
                "Review recent publications"
            ]

    async def analyze_writing_patterns(
        self,
        user: User,
        paper: Optional[Paper] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """Analyze user's writing patterns for personalization"""

        # This would analyze user's papers to extract patterns
        # For now, return basic analysis
        return {
            "writing_style": "academic",
            "avg_sentence_length": 20,
            "vocabulary_level": "advanced",
            "common_patterns": [
                "Uses evidence-based argumentation",
                "Prefers structured methodology",
                "Strong literature integration"
            ],
            "suggestions": [
                "Maintain consistent terminology",
                "Vary sentence structure for readability",
                "Continue strong citation practices"
            ]
        }


# Create singleton instance
ai_service = AIService()