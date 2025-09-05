"""
AI Integration Utils (app/utils/ai_integration.py)
"""
import openai
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


class AIIntegrationHelper:
    """Helper utilities for AI service integration"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.enabled = bool(self.api_key)

    def validate_prompt(self, prompt: str) -> bool:
        """Validate AI prompt for safety and length"""
        if not prompt or len(prompt.strip()) == 0:
            return False

        if len(prompt) > 4000:  # Token limit consideration
            return False

        # Basic content filtering
        forbidden_patterns = [
            "hack", "exploit", "bypass", "jailbreak",
            "ignore previous", "forget instructions"
        ]

        prompt_lower = prompt.lower()
        if any(pattern in prompt_lower for pattern in forbidden_patterns):
            return False

        return True

    def format_paper_context(self, paper_data: Dict[str, Any]) -> str:
        """Format paper data for AI context"""
        context = f"Paper: {paper_data.get('title', 'Untitled')}\n"
        context += f"Research Area: {paper_data.get('research_area', 'General')}\n"
        context += f"Status: {paper_data.get('status', 'draft')}\n"
        context += f"Progress: {paper_data.get('progress', 0)}%\n"

        if paper_data.get('abstract'):
            context += f"Abstract: {paper_data['abstract'][:500]}...\n"

        return context

    def extract_citations(self, text: str) -> List[str]:
        """Extract potential citations from text"""
        import re

        # Simple citation pattern matching
        patterns = [
            r'\(([A-Z][a-z]+(?:\s+et\s+al\.?)?,?\s+\d{4})\)',  # (Author, 2023)
            r'\[(\d+)\]',  # [1]
            r'doi:\s*(10\.\d+/[^\s]+)',  # DOI
        ]

        citations = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            citations.extend(matches)

        return list(set(citations))  # Remove duplicates

    def calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate basic readability metrics"""
        if not text:
            return {"readability_score": 0, "complexity": 0}

        words = text.split()
        sentences = text.count('.') + text.count('!') + text.count('?')

        if sentences == 0:
            return {"readability_score": 0, "complexity": 0}

        avg_words_per_sentence = len(words) / sentences
        long_words = sum(1 for word in words if len(word) > 6)
        complexity = long_words / len(words) if words else 0

        # Simplified readability score
        readability = max(0, min(100, 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * complexity)))

        return {
            "readability_score": round(readability, 2),
            "complexity": round(complexity * 100, 2),
            "avg_words_per_sentence": round(avg_words_per_sentence, 2)
        }

