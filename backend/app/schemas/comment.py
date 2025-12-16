"""
Comment schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class CommentAuthor(BaseModel):
    """Comment author information"""
    id: str
    name: str
    email: str


class CommentCreate(BaseModel):
    """Schema for creating a new comment"""
    content: str = Field(..., min_length=1, max_length=5000)
    section_id: str
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    selected_text: Optional[str] = None
    parent_comment_id: Optional[str] = None


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    is_resolved: Optional[bool] = None


class CommentResponse(BaseModel):
    """Schema for comment response"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    content: str
    paper_id: str
    section_id: str
    author_id: str
    author: Optional[CommentAuthor] = None
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    selected_text: Optional[str] = None
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[dict] = None
    parent_comment_id: Optional[str] = None
    replies_count: int = 0
    created_at: datetime
    updated_at: datetime


class CommentListResponse(BaseModel):
    """Schema for list of comments"""
    comments: List[CommentResponse]
    total: int
    section_id: Optional[str] = None
