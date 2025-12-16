"""
PDF Analysis Service for Reference Papers
Extracts text and analyzes writing style from academic papers
"""
import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFAnalyzer:
    """Service for analyzing PDF papers and extracting writing style features"""

    def __init__(self):
        """Initialize PDF analyzer"""
        self.initialized = False
        try:
            # Try to import PyPDF2
            import PyPDF2
            self.pdf_lib = PyPDF2
            self.initialized = True
            logger.info("✅ PDF Analyzer initialized with PyPDF2")
        except ImportError:
            logger.warning("⚠️ PyPDF2 not installed - PDF extraction disabled")

    def extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        """
        Extract text content from PDF file

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text or None if extraction failed
        """
        if not self.initialized:
            logger.error("❌ PDF library not available")
            return None

        try:
            text_content = []

            with open(file_path, 'rb') as file:
                pdf_reader = self.pdf_lib.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                logger.info(f"📄 Extracting text from {num_pages} pages...")

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_content.append(text)

            full_text = "\n".join(text_content)
            logger.info(f"✅ Extracted {len(full_text)} characters from PDF")

            return full_text

        except Exception as e:
            logger.error(f"❌ Failed to extract PDF text: {str(e)}")
            return None

    def analyze_writing_style(self, text: str) -> Dict[str, Any]:
        """
        Analyze writing style from extracted text

        Args:
            text: Extracted text content

        Returns:
            Dictionary of writing style features
        """
        if not text:
            return {}

        try:
            # Clean text
            text = self._clean_text(text)

            # Calculate various style metrics
            features = {
                "avg_sentence_length": self._calculate_avg_sentence_length(text),
                "vocabulary_complexity": self._calculate_vocabulary_complexity(text),
                "passive_voice_ratio": self._estimate_passive_voice_ratio(text),
                "common_phrases": self._extract_common_phrases(text),
                "technical_terms": self._extract_technical_terms(text),
                "citation_density": self._estimate_citation_density(text),
                "section_structure": self._extract_section_structure(text),
                "word_count": len(text.split()),
                "unique_words": len(set(text.lower().split())),
            }

            logger.info(f"✅ Analyzed writing style: {features['word_count']} words, "
                       f"{features['avg_sentence_length']:.1f} avg sentence length")

            return features

        except Exception as e:
            logger.error(f"❌ Failed to analyze writing style: {str(e)}")
            return {}

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'\n\d+\n', '\n', text)
        return text.strip()

    def _calculate_avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length in words"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        total_words = sum(len(s.split()) for s in sentences)
        return total_words / len(sentences)

    def _calculate_vocabulary_complexity(self, text: str) -> float:
        """
        Calculate vocabulary complexity (unique words / total words)
        Range: 0.0 to 1.0 (higher = more diverse vocabulary)
        """
        words = text.lower().split()
        if not words:
            return 0.0

        unique_words = set(words)
        return len(unique_words) / len(words)

    def _estimate_passive_voice_ratio(self, text: str) -> float:
        """
        Estimate passive voice usage ratio
        Looks for common passive voice patterns
        """
        # Common passive voice indicators
        passive_patterns = [
            r'\b(is|are|was|were|been|be)\s+\w+ed\b',
            r'\b(is|are|was|were|been|be)\s+being\s+\w+ed\b',
        ]

        passive_count = 0
        for pattern in passive_patterns:
            passive_count += len(re.findall(pattern, text, re.IGNORECASE))

        sentences = len(re.split(r'[.!?]+', text))
        if sentences == 0:
            return 0.0

        return min(passive_count / sentences, 1.0)

    def _extract_common_phrases(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract common phrases (bigrams and trigrams)

        Returns:
            List of common phrases
        """
        # Convert to lowercase
        text_lower = text.lower()

        # Extract bigrams (2-word phrases)
        words = text_lower.split()
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]

        # Count frequency
        phrase_counts = {}
        for phrase in bigrams:
            # Filter out phrases with too many common words
            if self._is_meaningful_phrase(phrase):
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

        # Sort by frequency and return top N
        sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
        return [phrase for phrase, count in sorted_phrases[:top_n]]

    def _is_meaningful_phrase(self, phrase: str) -> bool:
        """Check if phrase is meaningful (not just common words)"""
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        words = phrase.split()
        return not all(word in common_words for word in words)

    def _extract_technical_terms(self, text: str, top_n: int = 15) -> List[str]:
        """
        Extract likely technical terms (capitalized multi-word phrases or complex words)

        Returns:
            List of technical terms
        """
        # Find capitalized phrases (likely technical terms)
        capitalized_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)

        # Find complex words (long words with specific suffixes)
        complex_words = re.findall(r'\b\w{10,}(?:tion|ment|ness|ity|ology|graphy)\b', text, re.IGNORECASE)

        # Combine and count
        all_terms = capitalized_phrases + complex_words
        term_counts = {}
        for term in all_terms:
            term_lower = term.lower()
            term_counts[term_lower] = term_counts.get(term_lower, 0) + 1

        # Sort by frequency
        sorted_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)
        return [term for term, count in sorted_terms[:top_n]]

    def _estimate_citation_density(self, text: str) -> float:
        """
        Estimate citation density (citations per 1000 words)

        Looks for patterns like (Author, Year) or [1]
        """
        # Pattern for (Author, Year) citations
        author_year_pattern = r'\([A-Z][a-z]+(?:\set\sal\.)?,?\s*\d{4}\)'
        # Pattern for [1] style citations
        numbered_pattern = r'\[\d+\]'

        author_year_citations = len(re.findall(author_year_pattern, text))
        numbered_citations = len(re.findall(numbered_pattern, text))

        total_citations = author_year_citations + numbered_citations
        word_count = len(text.split())

        if word_count == 0:
            return 0.0

        # Return citations per 1000 words
        return (total_citations / word_count) * 1000

    def _extract_section_structure(self, text: str) -> List[str]:
        """
        Extract section headings from paper

        Returns:
            List of section names
        """
        # Common academic paper section patterns
        section_patterns = [
            r'\n\s*([A-Z][A-Z\s]{2,})\n',  # ALL CAPS sections
            r'\n\s*(\d+\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\n',  # Numbered sections
            r'\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\n(?=\s*[A-Z])',  # Title Case sections
        ]

        sections = []
        for pattern in section_patterns:
            matches = re.findall(pattern, text)
            sections.extend(matches)

        # Clean and deduplicate
        sections = [s.strip() for s in sections]
        sections = list(dict.fromkeys(sections))  # Remove duplicates while preserving order

        # Filter out very long sections (likely not headings)
        sections = [s for s in sections if len(s.split()) <= 6]

        return sections[:15]  # Return max 15 sections


# Global instance
pdf_analyzer = PDFAnalyzer()
