"""
OpenAI Service for GPT-3.5 and GPT-4 models
Provides integration with OpenAI API for research assistance
"""
import logging
import os
from typing import Optional, Dict, List, Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI GPT models"""

    def __init__(self):
        """Initialize OpenAI service with API key"""
        try:
            self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
            self.api_url = "https://api.openai.com/v1/chat/completions"

            if self.api_key and self.api_key.strip():
                self.enabled = True
                logger.info("✅ OpenAI service initialized successfully")
            else:
                self.enabled = False
                logger.warning("⚠️ OPENAI_API_KEY not found - OpenAI service disabled")
        except Exception as e:
            self.enabled = False
            logger.error(f"❌ Failed to initialize OpenAI service: {str(e)}")

    def build_research_prompt(
        self,
        message: str,
        files_content: List[Dict[str, Any]],
        personalization: Optional[Dict[str, int]],
        paper_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a comprehensive research-focused prompt for OpenAI

        Args:
            message: User's question/request
            files_content: List of uploaded files with content
            personalization: User's AI personalization settings
            paper_context: Current paper being worked on

        Returns:
            Formatted prompt string
        """
        # Build personalization instructions
        style_instructions = ""
        if personalization:
            lab_level = personalization.get('lab_level', 5)
            personal_level = personalization.get('personal_level', 5)
            global_level = personalization.get('global_level', 5)

            style_instructions = f"""
WRITING STYLE PREFERENCES:
- Lab Research Influence: {lab_level}/10 (use terminology and style from lab papers)
- Personal Writing Style: {personal_level}/10 (match user's personal academic writing)
- Global Academic Standards: {global_level}/10 (follow international conventions)
"""

        # Build paper context
        paper_info = ""
        if paper_context:
            paper_info = f"""
CURRENT PAPER CONTEXT:
- Title: {paper_context.get('title', 'Untitled')}
- Research Area: {paper_context.get('research_area', 'Not specified')}
- Status: {paper_context.get('status', 'in-progress')}
- Progress: {paper_context.get('progress', 0)}%
- Current Words: {paper_context.get('current_word_count', 0)}/{paper_context.get('target_word_count', 8000)}
"""

        # Build files summary
        files_info = ""
        if files_content:
            files_info = "\n\nUPLOADED FILES:\n"
            for file_data in files_content:
                files_info += f"\n**File: {file_data['filename']}** ({file_data['size']/1024:.1f} KB)\n"
                files_info += f"Content Preview:\n{file_data['content'][:3000]}\n"
                if len(file_data['content']) > 3000:
                    files_info += f"... (truncated, total: {len(file_data['content'])} characters)\n"

        # Complete prompt
        system_prompt = f"""You are an expert academic research assistant specialized in helping researchers write high-quality research papers.

{style_instructions}
{paper_info}

INSTRUCTIONS:
1. Provide clear, academic-style responses
2. Suggest relevant citations where applicable (use placeholder format: [Author, Year])
3. Identify connections to existing literature
4. Highlight research gaps and opportunities
5. Offer specific suggestions for paper sections (Abstract, Introduction, Methodology, etc.)
6. Use formal academic language appropriate for publication
7. If comparing files, analyze content similarities and differences
8. Suggest statistical/analytical methods when relevant

Format your response with:
- Clear section headings
- Bullet points for suggestions
- Academic tone and precision
- Actionable recommendations"""

        return system_prompt, message + files_info

    async def generate_response(
        self,
        message: str,
        files_content: List[Dict[str, Any]] = None,
        personalization: Optional[Dict[str, int]] = None,
        paper_context: Optional[Dict[str, Any]] = None,
        model: str = 'gpt-3.5-turbo'
    ) -> Dict[str, Any]:
        """
        Generate AI response using OpenAI

        Args:
            message: User's message
            files_content: Uploaded files data
            personalization: User preferences
            paper_context: Paper being worked on
            model: OpenAI model to use ('gpt-3.5-turbo' or 'gpt-4')

        Returns:
            Dict with response content and metadata
        """
        if not self.enabled:
            raise Exception("OpenAI service is not enabled. Please configure OPENAI_API_KEY.")

        try:
            # Build the prompts
            system_prompt, user_prompt = self.build_research_prompt(
                message=message,
                files_content=files_content or [],
                personalization=personalization,
                paper_context=paper_context
            )

            logger.info(f"🤖 Sending request to OpenAI {model} (prompt length: {len(user_prompt)} chars)")

            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            # Make API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

            # Extract response text
            response_text = data['choices'][0]['message']['content']

            logger.info(f"✅ Received response from OpenAI {model} ({len(response_text)} chars)")

            # Parse for citations (simple extraction)
            citations = self._extract_citations(response_text)

            return {
                'content': response_text,
                'model': model,
                'citations': citations,
                'metadata': {
                    'prompt_length': len(user_prompt),
                    'response_length': len(response_text),
                    'files_processed': len(files_content) if files_content else 0,
                    'usage': data.get('usage', {})
                }
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ OpenAI API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"OpenAI API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {str(e)}")
            raise Exception(f"Failed to generate response from OpenAI: {str(e)}")

    def _extract_citations(self, text: str) -> List[str]:
        """
        Extract citation suggestions from response text

        Args:
            text: Response text to parse

        Returns:
            List of found citations
        """
        import re

        # Match patterns like [Author, Year] or (Author, Year)
        citation_pattern = r'[\[\(]([A-Z][a-z]+(?:\set\sal\.)?),?\s*(\d{4})[\]\)]'
        matches = re.findall(citation_pattern, text)

        citations = [f"{author}, {year}" for author, year in matches]
        return list(set(citations))  # Remove duplicates


# Global instance
openai_service = OpenAIService()
