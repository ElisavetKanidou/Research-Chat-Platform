"""
Custom exception classes for the Research Platform API
"""
from datetime import datetime
from typing import Optional, Any, Dict


class ResearchPlatformException(Exception):
    """Base exception class for Research Platform"""

    def __init__(
            self,
            message: str,
            status_code: int = 500,
            error_code: str = "INTERNAL_ERROR",
            details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)


class AuthenticationException(ResearchPlatformException):
    """Authentication related exceptions"""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationException(ResearchPlatformException):
    """Authorization related exceptions"""

    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class ValidationException(ResearchPlatformException):
    """Validation related exceptions"""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if not details:
            details = {}
        if field:
            details["field"] = field

        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundException(ResearchPlatformException):
    """Resource not found exceptions"""

    def __init__(self, resource: str = "Resource", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            details=details
        )


class ConflictException(ResearchPlatformException):
    """Resource conflict exceptions"""

    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="RESOURCE_CONFLICT",
            details=details
        )


class RateLimitException(ResearchPlatformException):
    """Rate limiting exceptions"""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


class ExternalServiceException(ResearchPlatformException):
    """External service integration exceptions"""

    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        if not details:
            details = {}
        details["service"] = service

        super().__init__(
            message=f"{service} service error: {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details
        )


class AIServiceException(ExternalServiceException):
    """AI service specific exceptions"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(service="AI", message=message, details=details)


class DatabaseException(ResearchPlatformException):
    """Database operation exceptions"""

    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details
        )


class FileUploadException(ResearchPlatformException):
    """File upload related exceptions"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_UPLOAD_ERROR",
            details=details
        )


class CollaborationException(ResearchPlatformException):
    """Collaboration related exceptions"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="COLLABORATION_ERROR",
            details=details
        )