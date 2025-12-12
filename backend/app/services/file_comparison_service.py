"""
File Comparison Service
Provides utilities for comparing and analyzing uploaded files
"""
import logging
import hashlib
import difflib
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class FileComparisonService:
    """Service for comparing file contents"""

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for comparison by removing formatting differences

        Args:
            text: Raw text content

        Returns:
            Normalized text
        """
        # Convert to lowercase
        normalized = text.lower()

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        # Remove common punctuation that doesn't affect meaning
        for char in [',', '.', ';', ':', '!', '?', '"', "'", '(', ')', '[', ']', '{', '}']:
            normalized = normalized.replace(char, '')

        return normalized.strip()

    @staticmethod
    def compute_hash(text: str) -> str:
        """
        Compute MD5 hash of normalized text

        Args:
            text: Text to hash

        Returns:
            MD5 hash string
        """
        normalized = FileComparisonService.normalize_text(text)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    @staticmethod
    def compare_files(file1: Dict[str, Any], file2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two files and return similarity metrics

        Args:
            file1: First file dict with 'filename' and 'content'
            file2: Second file dict with 'filename' and 'content'

        Returns:
            Dict with comparison results
        """
        content1 = file1.get('content', '')
        content2 = file2.get('content', '')

        # Normalize texts
        norm1 = FileComparisonService.normalize_text(content1)
        norm2 = FileComparisonService.normalize_text(content2)

        # Compute hashes
        hash1 = hashlib.md5(norm1.encode('utf-8')).hexdigest()
        hash2 = hashlib.md5(norm2.encode('utf-8')).hexdigest()

        # Calculate similarity ratio
        similarity = difflib.SequenceMatcher(None, norm1, norm2).ratio()

        # Determine if identical
        are_identical = hash1 == hash2 or similarity > 0.95

        # Find differences if not identical
        differences = []
        if not are_identical and similarity < 1.0:
            # Sample some differences
            differ = difflib.Differ()
            diff = list(differ.compare(norm1.split()[:100], norm2.split()[:100]))
            differences = [line for line in diff if line.startswith('- ') or line.startswith('+ ')][:10]

        result = {
            'file1_name': file1.get('filename', 'Unknown'),
            'file2_name': file2.get('filename', 'Unknown'),
            'similarity_percentage': round(similarity * 100, 2),
            'are_identical': are_identical,
            'hash1': hash1,
            'hash2': hash2,
            'hashes_match': hash1 == hash2,
            'content1_length': len(content1),
            'content2_length': len(content2),
            'normalized1_length': len(norm1),
            'normalized2_length': len(norm2),
            'sample_differences': differences[:5] if differences else []
        }

        logger.info(
            f"📊 File comparison: {file1.get('filename')} vs {file2.get('filename')} "
            f"- Similarity: {result['similarity_percentage']}%"
        )

        return result

    @staticmethod
    def compare_multiple_files(files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compare all pairs of files in a list

        Args:
            files: List of file dicts

        Returns:
            List of comparison results for all pairs
        """
        if len(files) < 2:
            return []

        comparisons = []

        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                comparison = FileComparisonService.compare_files(files[i], files[j])
                comparisons.append(comparison)

        return comparisons

    @staticmethod
    def generate_comparison_summary(comparisons: List[Dict[str, Any]]) -> str:
        """
        Generate human-readable summary of file comparisons

        Args:
            comparisons: List of comparison results

        Returns:
            Formatted summary string
        """
        if not comparisons:
            return "No file comparisons available."

        summary = "📊 **File Comparison Summary**\n\n"

        for idx, comp in enumerate(comparisons, 1):
            summary += f"{idx}. **{comp['file1_name']}** vs **{comp['file2_name']}**\n"
            summary += f"   - Similarity: {comp['similarity_percentage']}%\n"

            if comp['are_identical']:
                summary += f"   - ✅ **Files are identical** (after normalization)\n"
            elif comp['similarity_percentage'] > 80:
                summary += f"   - ⚠️ Files are very similar but have minor differences\n"
            elif comp['similarity_percentage'] > 50:
                summary += f"   - 📝 Files share significant content but differ substantially\n"
            else:
                summary += f"   - ❌ Files have different content\n"

            summary += f"   - File sizes: {comp['content1_length']} chars vs {comp['content2_length']} chars\n"

            if comp['sample_differences']:
                summary += f"   - Sample differences: {len(comp['sample_differences'])} found\n"

            summary += "\n"

        return summary


# Global instance
file_comparison_service = FileComparisonService()
