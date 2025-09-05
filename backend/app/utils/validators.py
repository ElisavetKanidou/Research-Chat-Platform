
"""
Validators Utils (app/utils/validators.py)
"""
import re
from typing import Any, List, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation exception"""
    pass


class Validators:
    """Collection of validation utilities"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_orcid(orcid: str) -> bool:
        """Validate ORCID ID format"""
        pattern = r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$'
        return bool(re.match(pattern, orcid))

    @staticmethod
    def validate_doi(doi: str) -> bool:
        """Validate DOI format"""
        pattern = r'^10\.\d+/.+$'
        return bool(re.match(pattern, doi))

    @staticmethod
    def validate_paper_title(title: str) -> bool:
        """Validate paper title"""
        if not title or len(title.strip()) < 5:
            return False
        if len(title) > 500:
            return False
        return True

    @staticmethod
    def validate_research_area(area: str) -> bool:
        """Validate research area"""
        if not area or len(area.strip()) < 2:
            return False
        if len(area) > 255:
            return False
        return True

    @staticmethod
    def validate_word_count(count: int) -> bool:
        """Validate word count"""
        return 0 <= count <= 1000000

    @staticmethod
    def validate_progress(progress: int) -> bool:
        """Validate progress percentage"""
        return 0 <= progress <= 100

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255 - len(ext)] + ext
        return filename

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))

    @staticmethod
    def validate_json(data: Any) -> bool:
        """Validate if data can be JSON serialized"""
        try:
            import json
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False


# Create global instances
ai_helper = AIIntegrationHelper()
pdf_generator = PDFGenerator()
email_helper = EmailHelper()
file_handler = FileHandler()
validators = Validators()