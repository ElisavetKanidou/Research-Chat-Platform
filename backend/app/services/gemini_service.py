"""
Google Gemini AI Service for Research Chat
Provides FREE AI model integration with academic research focus
"""
import logging
from typing import Optional, Dict, List, Any
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini AI models"""

    def __init__(self):
        """Initialize Gemini service with API key"""
        try:
            # Configure Gemini API
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.enabled = True
                logger.info("✅ Gemini service initialized successfully with gemini-2.5-flash")
            else:
                self.enabled = False
                logger.warning("⚠️ GEMINI_API_KEY not found - Gemini service disabled")
        except Exception as e:
            self.enabled = False
            logger.error(f"❌ Failed to initialize Gemini service: {str(e)}")

    def build_research_prompt(
        self,
        message: str,
        files_content: List[Dict[str, Any]],
        personalization: Optional[Dict[str, int]],
        paper_context: Optional[Dict[str, Any]] = None,
        reference_papers: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Build a comprehensive research-focused prompt for Gemini

        Args:
            message: User's question/request
            files_content: List of uploaded files with content
            personalization: User's AI personalization settings
            paper_context: Current paper being worked on
            reference_papers: Lab/personal/literature papers for style analysis

        Returns:
            Formatted prompt string
        """
        # Build personalization instructions with reference papers
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

        # Add reference papers analysis
        reference_papers_info = ""
        if reference_papers:
            lab_papers = [p for p in reference_papers if p.get('paper_type') == 'lab']
            personal_papers = [p for p in reference_papers if p.get('paper_type') == 'personal']
            literature_papers = [p for p in reference_papers if p.get('paper_type') == 'literature']

            if lab_papers or personal_papers or literature_papers:
                reference_papers_info = "\n\nREFERENCE PAPERS ANALYSIS:\n"

                if lab_papers:
                    reference_papers_info += f"\n📚 LAB PAPERS ({len(lab_papers)} papers):\n"
                    for paper in lab_papers[:3]:  # Top 3
                        reference_papers_info += f"  • {paper.get('title', 'Untitled')}\n"
                        if paper.get('writing_style_features'):
                            features = paper['writing_style_features']
                            reference_papers_info += f"    Style: Avg {features.get('avg_sentence_length', 0):.1f} words/sentence, "
                            reference_papers_info += f"{features.get('passive_voice_ratio', 0):.0%} passive voice\n"
                            if features.get('common_phrases'):
                                reference_papers_info += f"    Common phrases: {', '.join(features['common_phrases'][:3])}\n"

                if personal_papers:
                    reference_papers_info += f"\n✍️ PERSONAL PAPERS ({len(personal_papers)} papers):\n"
                    for paper in personal_papers[:3]:
                        reference_papers_info += f"  • {paper.get('title', 'Untitled')}\n"
                        if paper.get('writing_style_features'):
                            features = paper['writing_style_features']
                            reference_papers_info += f"    Your style: {features.get('avg_sentence_length', 0):.1f} words/sentence, "
                            reference_papers_info += f"complexity {features.get('vocabulary_complexity', 0):.2f}\n"
                            if features.get('technical_terms'):
                                reference_papers_info += f"    Your terms: {', '.join(features['technical_terms'][:3])}\n"

                if literature_papers:
                    reference_papers_info += f"\n🌐 LITERATURE PAPERS ({len(literature_papers)} papers):\n"
                    for paper in literature_papers[:3]:
                        reference_papers_info += f"  • {paper.get('title', 'Untitled')}\n"

                reference_papers_info += "\n💡 INSTRUCTION: Adapt your responses based on these reference papers' writing styles according to the personalization levels above.\n"

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
        prompt = f"""You are an expert academic research assistant specialized in helping researchers write high-quality research papers.

{style_instructions}
{reference_papers_info}
{paper_info}
{files_info}

USER'S REQUEST:
{message}

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
- Actionable recommendations

Provide your expert analysis:"""

        return prompt

    async def generate_response(
        self,
        message: str,
        files_content: List[Dict[str, Any]] = None,
        personalization: Optional[Dict[str, int]] = None,
        paper_context: Optional[Dict[str, Any]] = None,
        reference_papers: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response using Gemini

        Args:
            message: User's message
            files_content: Uploaded files data
            personalization: User preferences
            paper_context: Paper being worked on
            reference_papers: Lab/personal/literature papers for style analysis

        Returns:
            Dict with response content and metadata
        """
        if not self.enabled:
            raise Exception("Gemini service is not enabled. Please configure GEMINI_API_KEY.")

        try:
            # Build the prompt
            prompt = self.build_research_prompt(
                message=message,
                files_content=files_content or [],
                personalization=personalization,
                paper_context=paper_context,
                reference_papers=reference_papers
            )

            logger.info(f"🤖 Sending request to Gemini (prompt length: {len(prompt)} chars)")

            # Generate response
            response = self.model.generate_content(prompt)

            # Extract response text
            response_text = response.text

            logger.info(f"✅ Received response from Gemini ({len(response_text)} chars)")

            # Parse for citations (simple extraction)
            citations = self._extract_citations(response_text)

            return {
                'content': response_text,
                'model': 'gemini-2.5-pro',
                'citations': citations,
                'metadata': {
                    'prompt_length': len(prompt),
                    'response_length': len(response_text),
                    'files_processed': len(files_content) if files_content else 0
                }
            }

        except Exception as e:
            logger.error(f"❌ Gemini API error: {str(e)}")
            raise Exception(f"Failed to generate response from Gemini: {str(e)}")

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
gemini_service = GeminiService()
