"""
Global dependencies (app/dependencies.py)
"""
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.session import get_db

security = HTTPBearer()


async def get_current_active_user(
        db: AsyncSession = get_db(),
        token: str = security
) -> "User":
    """Global dependency to get current active user"""
    from app.api.v1.endpoints.auth import get_current_user
    return await get_current_user(token, db)


"""
API v1 specific dependencies (app/api/v1/dependencies.py)  
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.session import get_db
from app.services.auth_service import auth_service
from app.models.user import User
from app.core.exceptions import AuthenticationException

security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from token"""
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token, "access")
        user_id = payload.get("sub")

        if user_id is None:
            raise AuthenticationException("Invalid token payload")

        user = await auth_service.get_user_by_id(db, user_id)
        if user is None or not user.is_active:
            raise AuthenticationException("User not found or inactive")

        return user

    except AuthenticationException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
        current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def require_subscription(required_plan: str = "pro"):
    """Dependency factory to require specific subscription"""

    async def _check_subscription(
            current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.is_premium_user() and required_plan != "free":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription plan '{required_plan}' required"
            )
        return current_user

    return _check_subscription


"""
Utility functions (app/utils/apiHelpers.py to match frontend)
"""
from typing import Dict, Any, Optional
import httpx
import json
from fastapi import HTTPException


class APIResponse:
    """API response wrapper to match frontend expectations"""

    def __init__(self, data: Any, status_code: int = 200, message: str = "Success"):
        self.data = data
        self.status_code = status_code
        self.message = message
        self.success = status_code < 400

    def dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "status_code": self.status_code
        }


def create_response(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200
) -> Dict[str, Any]:
    """Create standardized API response"""
    return {
        "success": status_code < 400,
        "data": data,
        "message": message,
        "status_code": status_code
    }


def handle_api_error(error: Exception) -> HTTPException:
    """Convert various errors to HTTP exceptions"""
    if isinstance(error, HTTPException):
        return error

    return HTTPException(
        status_code=500,
        detail=str(error)
    )


"""
Email utilities (app/utils/email.py)
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for notifications"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME

    async def send_email(
            self,
            to_emails: List[str],
            subject: str,
            body: str,
            html_body: Optional[str] = None
    ) -> bool:
        """Send email to recipients"""

        if not self.smtp_host:
            logger.warning("SMTP not configured, email not sent")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ', '.join(to_emails)

            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)

            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)

                server.send_message(msg)

            logger.info(f"Email sent to {len(to_emails)} recipients")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to Research Platform!"
        body = f"""
        Hi {user_name},

        Welcome to Research Platform! We're excited to help you with your research journey.

        Get started by:
        1. Creating your first research paper
        2. Exploring AI-powered research assistance
        3. Setting up your research preferences

        If you have any questions, don't hesitate to reach out.

        Best regards,
        The Research Platform Team
        """

        return await self.send_email([user_email], subject, body)

    async def send_password_reset_email(
            self,
            user_email: str,
            reset_token: str
    ) -> bool:
        """Send password reset email"""
        subject = "Reset Your Password"
        reset_url = f"https://yourapp.com/reset-password?token={reset_token}"

        body = f"""
        You requested a password reset for your Research Platform account.

        Click the link below to reset your password:
        {reset_url}

        This link will expire in 1 hour.

        If you didn't request this, please ignore this email.
        """

        return await self.send_email([user_email], subject, body)


# Create service instance
email_service = EmailService()

"""
File handling utilities (app/utils/file_handler.py)
"""
import os
import uuid
from typing import Optional, List
from fastapi import UploadFile, HTTPException
import magic

from app.core.config import settings


class FileHandler:
    """File upload and management utilities"""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.max_size = settings.MAX_UPLOAD_SIZE
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS

        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_upload_file(
            self,
            file: UploadFile,
            user_id: str,
            subfolder: Optional[str] = None
    ) -> str:
        """Save uploaded file and return file path"""

        # Validate file
        await self._validate_file(file)

        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Create user directory
        user_dir = os.path.join(self.upload_dir, user_id)
        if subfolder:
            user_dir = os.path.join(user_dir, subfolder)

        os.makedirs(user_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(user_dir, unique_filename)

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return file_path

    async def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""

        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset position

        if file_size > self.max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {self.max_size} bytes"
            )

        # Check file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
            )

        # Check MIME type (requires python-magic)
        try:
            content = await file.read(1024)  # Read first 1KB
            file.file.seek(0)  # Reset position

            mime_type = magic.from_buffer(content, mime=True)

            # Basic MIME type validation
            allowed_mimes = {
                '.pdf': 'application/pdf',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.txt': 'text/plain',
                '.md': 'text/plain'
            }

            expected_mime = allowed_mimes.get(file_extension)
            if expected_mime and expected_mime not in mime_type:
                raise HTTPException(
                    status_code=400,
                    detail="File content doesn't match extension"
                )

        except ImportError:
            # python-magic not installed, skip MIME validation
            pass

    def delete_file(self, file_path: str) -> bool:
        """Delete file from filesystem"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    def get_file_size(self, file_path: str) -> Optional[int]:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path) if os.path.exists(file_path) else None
        except Exception:
            return None


# Create service instance
file_handler = FileHandler()

"""
Status and validation helpers (app/utils/statusHelpers.py & validators.py)
"""
from typing import Dict, Any, List
from datetime import datetime
from app.models.paper import PaperStatus, SectionStatus


def calculate_paper_progress(sections: List[Dict[str, Any]]) -> int:
    """Calculate paper progress based on section statuses"""
    if not sections:
        return 0

    completed_sections = sum(
        1 for section in sections
        if section.get('status') == SectionStatus.COMPLETED.value
    )

    return int((completed_sections / len(sections)) * 100)


def get_status_color(status: str) -> str:
    """Get color class for status"""
    status_colors = {
        'draft': 'gray',
        'in-progress': 'blue',
        'in-review': 'yellow',
        'revision': 'orange',
        'completed': 'green',
        'published': 'purple',
        'archived': 'gray'
    }
    return status_colors.get(status, 'gray')


def format_date_for_frontend(date: datetime) -> str:
    """Format datetime for frontend consumption"""
    return date.isoformat() if date else None


def validate_research_area(area: str) -> bool:
    """Validate research area format"""
    return len(area.strip()) >= 2 and len(area) <= 255


def validate_paper_title(title: str) -> bool:
    """Validate paper title"""
    return 5 <= len(title.strip()) <= 500


class DataValidator:
    """Data validation utilities"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_orcid(orcid: str) -> bool:
        """Validate ORCID ID format"""
        import re
        pattern = r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$'
        return bool(re.match(pattern, orcid))

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        import re
        # Remove or replace unsafe characters
        sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
        return sanitized[:255]  # Limit length