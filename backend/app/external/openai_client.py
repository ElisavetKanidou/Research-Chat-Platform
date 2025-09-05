"""
OpenAI API client for AI services
"""
from typing import List, Dict, Any, Optional
import openai
import asyncio
from openai import AsyncOpenAI
import logging

from app.core.config import settings
from app.core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI API client wrapper"""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured. AI features will use mock responses.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        self.default_model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.timeout = settings.AI_RESPONSE_TIMEOUT

    async def chat_completion(
            self,
            messages: List[Dict[str, str]],
            model: Optional[str] = None,
            max_tokens: Optional[int] = None,
            temperature: float = 0.7,
            **kwargs
    ) -> Dict[str, Any]:
        """Create a chat completion"""

        if not self.client:
            return self._mock_chat_completion(messages, model or self.default_model)

        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=model or self.default_model,
                    messages=messages,
                    max_tokens=max_tokens or self.max_tokens,
                    temperature=temperature,
                    **kwargs
                ),
                timeout=self.timeout
            )

            return {
                "choices": [
                    {
                        "message": {
                            "role": response.choices[0].message.role,
                            "content": response.choices[0].message.content
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "model": response.model
            }

        except asyncio.TimeoutError:
            raise AIServiceException("OpenAI API request timed out")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise AIServiceException(f"OpenAI API error: {str(e)}")

    async def generate_embeddings(
            self,
            text: str,
            model: str = "text-embedding-ada-002"
    ) -> List[float]:
        """Generate embeddings for text"""

        if not self.client:
            # Return mock embedding vector
            return [0.1] * 1536  # Ada-002 embedding size

        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"OpenAI embeddings error: {e}")
            raise AIServiceException(f"Failed to generate embeddings: {str(e)}")

    async def moderate_content(self, content: str) -> Dict[str, Any]:
        """Moderate content using OpenAI moderation API"""

        if not self.client:
            return {"flagged": False, "categories": {}}

        try:
            response = await self.client.moderations.create(input=content)

            return {
                "flagged": response.results[0].flagged,
                "categories": dict(response.results[0].categories),
                "category_scores": dict(response.results[0].category_scores)
            }

        except Exception as e:
            logger.error(f"OpenAI moderation error: {e}")
            # Return safe result on error
            return {"flagged": False, "categories": {}}

    def _mock_chat_completion(self, messages: List[Dict[str, str]], model: str) -> Dict[str, Any]:
        """Mock chat completion for development/testing"""

        user_message = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                user_message = message.get("content", "")
                break

        # Generate contextual mock responses
        mock_responses = self._get_mock_responses(user_message)

        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": mock_responses
                    }
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message.split()) * 4 // 3,  # Rough token estimate
                "completion_tokens": len(mock_responses.split()) * 4 // 3,
                "total_tokens": (len(user_message) + len(mock_responses)) * 4 // 3
            },
            "model": model
        }

    def _get_mock_responses(self, user_message: str) -> str:
        """Generate contextual mock responses based on user message"""

        message_lower = user_message.lower()

        # Research-related responses
        if any(word in message_lower for word in ["research", "study", "methodology", "literature"]):
            return """Based on your research focus, I'd suggest starting with a comprehensive literature review to identify current gaps in the field. Consider using systematic review methodologies to ensure you capture all relevant work.

For your methodology, think about:
1. Mixed methods approach for robust data collection
2. Clear inclusion/exclusion criteria
3. Appropriate sample size calculations
4. Ethical considerations and IRB approval

Would you like me to help you develop any of these areas further?"""

        # Writing assistance responses
        elif any(word in message_lower for word in ["write", "writing", "abstract", "section", "paper"]):
            return """For academic writing, I recommend focusing on clarity and logical flow. Here are some suggestions:

**Structure**: Ensure each paragraph has a clear topic sentence and supporting evidence.

**Clarity**: Use active voice where possible and avoid unnecessary jargon.

**Flow**: Use transitional phrases to connect ideas between sentences and paragraphs.

**Evidence**: Support your claims with appropriate citations and data.

Would you like me to review a specific section or help with outlining your paper?"""

        # General research assistance
        elif any(word in message_lower for word in ["help", "suggest", "advice", "guidance"]):
            return """I'm here to help with your research! I can assist with:

• Literature review strategies and gap analysis
• Research methodology design and validation
• Academic writing and structure improvement
• Data analysis approaches and interpretation
• Citation management and reference formatting
• Research project planning and timeline development

What specific aspect of your research would you like to focus on today?"""

        # Analysis and insights
        elif any(word in message_lower for word in ["analyze", "analysis", "insights", "patterns"]):
            return """For effective analysis, consider these approaches:

**Quantitative Data**: Use appropriate statistical tests, check assumptions, and consider effect sizes alongside p-values.

**Qualitative Data**: Employ systematic coding methods, look for themes and patterns, and consider multiple perspectives.

**Mixed Methods**: Integrate findings thoughtfully, using each method to complement and validate the other.

**Interpretation**: Connect findings back to your research questions and existing literature. Consider alternative explanations and limitations.

Would you like me to help you develop a specific analysis plan?"""

        # Default response
        else:
            return """I understand you're working on your research. As your AI research assistant, I can help you with various aspects of academic work including literature reviews, methodology design, writing assistance, and analysis planning.

To provide more targeted help, could you tell me more about:
- What stage of research you're currently in
- The specific challenges you're facing
- What type of assistance would be most valuable right now

How can I best support your research goals today?"""


# Create global client instance
openai_client = OpenAIClient()