"""
GPT-OSS Service for local 120B model integration
backend/app/services/gpt_oss_service.py
"""
import httpx
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class GPTOSSService:
    """Service for GPT-OSS local AI model integration"""

    def __init__(self):
        self.api_key = settings.GPT_OSS_API_KEY
        self.base_url = settings.GPT_OSS_BASE_URL
        self.model = settings.GPT_OSS_MODEL
        self.enabled = bool(self.api_key and self.base_url)

        if self.enabled:
            logger.info(f"🚀 GPT-OSS Service initialized: {self.base_url}")
            logger.info(f"📊 Model: {self.model}")
        else:
            logger.warning("⚠️ GPT-OSS Service disabled - missing API key or base URL")

    async def generate_response(
        self,
        message: str,
        files_content: List[Dict[str, Any]] = None,
        personalization: Optional[Dict[str, int]] = None,
        paper_context: Optional[Dict[str, Any]] = None,
        reference_papers: Optional[List[Dict]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response using GPT-OSS local model

        Args:
            message: User message
            files_content: List of uploaded files
            personalization: User personalization settings
            paper_context: Current paper context
            reference_papers: User's reference papers for style analysis
            model: Optional model override

        Returns:
            Dict with response content and metadata
        """
        if not self.enabled:
            raise Exception("GPT-OSS service is not enabled. Please configure GPT_OSS_API_KEY in .env")

        try:
            # Build system prompt based on personalization
            system_prompt = self._build_system_prompt(
                personalization,
                paper_context,
                reference_papers
            )

            # Build messages array
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]

            # Add file context if provided
            if files_content:
                file_context = "\n\n--- Uploaded Files ---\n"
                for file_info in files_content:
                    file_context += f"\n**File: {file_info.get('filename', 'unknown')}**\n"
                    file_context += f"{file_info.get('content', '')[:5000]}\n"
                messages[1]["content"] = message + file_context

            # Prepare request
            request_data = {
                "model": model or self.model,
                "messages": messages
            }

            logger.info(f"🚀 Sending request to GPT-OSS: {self.base_url}")
            logger.debug(f"Request data: {request_data}")

            # Make HTTP request
            headers = {
                "Content-Type": "application/json"
            }

            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            async with httpx.AsyncClient(timeout=None) as client:  # No timeout
                response = await client.post(
                    self.base_url,
                    json=request_data,
                    headers=headers
                )

                response.raise_for_status()
                result = response.json()

            logger.info("✅ GPT-OSS response received")

            # Extract response from OpenAI-compatible format
            if "choices" in result and len(result["choices"]) > 0:
                response_content = result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Unexpected response format from GPT-OSS: {result}")

            return {
                "response": response_content,
                "model": result.get("model", self.model),
                "created": result.get("created"),
                "id": result.get("id"),
                "finish_reason": result["choices"][0].get("finish_reason", "stop")
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ GPT-OSS HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"GPT-OSS API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"❌ GPT-OSS request error: {str(e)}")
            raise Exception(f"Failed to connect to GPT-OSS server: {str(e)}")
        except Exception as e:
            logger.error(f"❌ GPT-OSS unexpected error: {str(e)}")
            raise

    def _build_system_prompt(
        self,
        personalization: Optional[Dict[str, int]],
        paper_context: Optional[Dict[str, Any]],
        reference_papers: Optional[List[Dict]] = None
    ) -> str:
        """Build system prompt with personalization"""

        prompt = "You are an expert research assistant helping with academic paper writing.\n\n"

        # Add personalization levels
        if personalization:
            lab_level = personalization.get('lab_level', 7)
            personal_level = personalization.get('personal_level', 8)
            global_level = personalization.get('global_level', 5)

            prompt += f"**Personalization Settings:**\n"
            prompt += f"- Lab Knowledge Level: {lab_level}/10\n"
            prompt += f"- Personal Knowledge Level: {personal_level}/10\n"
            prompt += f"- Global Knowledge Level: {global_level}/10\n\n"

        # Add paper context
        if paper_context:
            prompt += f"**Current Paper Context:**\n"
            prompt += f"- Title: {paper_context.get('title', 'N/A')}\n"
            prompt += f"- Research Area: {paper_context.get('research_area', 'N/A')}\n"
            prompt += f"- Status: {paper_context.get('status', 'N/A')}\n"
            prompt += f"- Progress: {paper_context.get('progress', 0)}%\n"
            prompt += f"- Word Count: {paper_context.get('current_word_count', 0)} / {paper_context.get('target_word_count', 0)}\n\n"

        # Add reference papers style analysis
        if reference_papers and len(reference_papers) > 0:
            prompt += f"**User's Reference Papers ({len(reference_papers)} papers):**\n"
            for paper in reference_papers[:3]:  # Top 3
                prompt += f"- {paper.get('title', 'Unknown')} ({paper.get('paper_type', 'personal')})\n"
            prompt += "\nPlease maintain consistency with the user's established writing style.\n\n"

        prompt += "Provide clear, academic, and well-researched responses."

        return prompt


# Create global instance
gpt_oss_service = GPTOSSService()
