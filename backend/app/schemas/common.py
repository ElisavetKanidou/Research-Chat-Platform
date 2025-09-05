

"""
Common schemas (app/schemas/common.py)
"""
from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class ResponseBase(BaseModel):
    """Base response schema"""
    success: bool = True
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(ResponseBase):
    """Error response schema"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(ResponseBase, Generic[T]):
    """Success response with data"""
    data: T


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    size: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response"""
    items: List[T]
    meta: PaginationMeta


class SortParams(BaseModel):
    """Sorting parameters"""
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", regex="^(asc|desc)$")


class FilterParams(BaseModel):
    """Base filter parameters"""
    search: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class IDResponse(BaseModel):
    """Simple ID response"""
    id: str


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str


class StatusResponse(BaseModel):
    """Status response"""
    status: str
    details: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dependencies: Optional[Dict[str, str]] = None


class BulkOperationResponse(BaseModel):
    """Bulk operation response"""
    total: int
    successful: int
    failed: int
    errors: Optional[List[str]] = None


class UploadResponse(BaseModel):
    """File upload response"""
    filename: str
    size: int
    content_type: str
    url: str
    upload_id: str


class ExportResponse(BaseModel):
    """Export operation response"""
    download_url: str
    filename: str
    size: int
    expires_at: datetime
    format: str
