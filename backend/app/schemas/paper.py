"""
Pydantic schemas for paper-related API requests and responses
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class PaperStatusEnum(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in-progress"
    IN_REVIEW = "in-review"
    REVISION = "revision"
    COMPLETED = "completed"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class SectionStatusEnum(str, Enum):
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs-review"


# Paper Section Schemas
class PaperSectionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = ""
    status: SectionStatusEnum = SectionStatusEnum.NOT_STARTED
    order: int = Field(default=0, ge=0)


class PaperSectionCreate(PaperSectionBase):
    pass


class PaperSectionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    status: Optional[SectionStatusEnum] = None
    order: Optional[int] = Field(None, ge=0)


class PaperSectionResponse(PaperSectionBase):
    id: str
    word_count: int
    last_modified: datetime

    class Config:
        from_attributes = True
        # Map database field names to frontend field names
        fields = {
            'last_modified': 'lastModified',
            'word_count': 'wordCount'
        }


# Paper Base Schemas
class PaperBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    abstract: Optional[str] = ""
    research_area: Optional[str] = Field(None, max_length=255)
    target_word_count: int = Field(default=8000, gt=0, le=100000)
    tags: Optional[List[str]] = []
    co_authors: Optional[List[str]] = []
    is_public: bool = False

    @validator('tags', pre=True)
    def validate_tags(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v

    @validator('co_authors', pre=True)
    def validate_co_authors(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [author.strip() for author in v.split(',') if author.strip()]
        return v


class PaperCreate(PaperBase):
    status: PaperStatusEnum = PaperStatusEnum.DRAFT
    sections: Optional[List[PaperSectionCreate]] = None

    @validator('sections', pre=True, always=True)
    def create_default_sections(cls, v):
        if v is None or len(v) == 0:
            return [
                PaperSectionCreate(title="Introduction", order=1),
                PaperSectionCreate(title="Literature Review", order=2),
                PaperSectionCreate(title="Methodology", order=3),
                PaperSectionCreate(title="Results", order=4),
                PaperSectionCreate(title="Discussion", order=5),
                PaperSectionCreate(title="Conclusion", order=6),
            ]
        return v


class PaperUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    abstract: Optional[str] = None
    status: Optional[PaperStatusEnum] = None
    research_area: Optional[str] = Field(None, max_length=255)
    target_word_count: Optional[int] = Field(None, gt=0, le=100000)
    tags: Optional[List[str]] = None
    co_authors: Optional[List[str]] = None
    is_public: Optional[bool] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    current_word_count: Optional[int] = Field(None, ge=0)

    # Publication fields
    doi: Optional[str] = None
    journal: Optional[str] = None
    publication_date: Optional[datetime] = None
    citation_count: Optional[int] = Field(None, ge=0)

    @validator('tags', pre=True)
    def validate_tags(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v

    @validator('co_authors', pre=True)
    def validate_co_authors(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return [author.strip() for author in v.split(',') if author.strip()]
        return v


class PaperListResponse(BaseModel):
    """Lightweight response for paper lists"""
    id: str
    title: str
    status: PaperStatusEnum
    progress: int
    created_at: datetime
    last_modified: datetime
    current_word_count: int
    target_word_count: int
    research_area: str
    co_authors: List[str]
    tags: List[str]
    is_public: bool

    class Config:
        from_attributes = True
        # Map database field names to frontend field names
        fields = {
            'created_at': 'createdAt',
            'last_modified': 'lastModified',
            'current_word_count': 'currentWordCount',
            'target_word_count': 'targetWordCount',
            'research_area': 'researchArea',
            'co_authors': 'coAuthors',
            'is_public': 'isPublic'
        }


class PaperResponse(PaperListResponse):
    """Full paper response with sections"""
    abstract: str
    sections: List[PaperSectionResponse]

    # Publication fields (optional)
    doi: Optional[str] = None
    journal: Optional[str] = None
    publication_date: Optional[datetime] = None
    citation_count: Optional[int] = 0

    class Config:
        from_attributes = True
        fields = {
            'created_at': 'createdAt',
            'last_modified': 'lastModified',
            'current_word_count': 'currentWordCount',
            'target_word_count': 'targetWordCount',
            'research_area': 'researchArea',
            'co_authors': 'coAuthors',
            'is_public': 'isPublic',
            'publication_date': 'publicationDate',
            'citation_count': 'citationCount'
        }


class PaperStatsResponse(BaseModel):
    """Paper statistics response"""
    total_papers: int
    status_breakdown: Dict[str, int]
    total_words: int
    average_progress: float
    published_papers: int
    active_papers: int


class PaperDuplicateRequest(BaseModel):
    new_title: Optional[str] = None


class PaperSectionBulkUpdate(BaseModel):
    """For updating multiple sections at once"""
    sections: List[Dict[str, Any]]


# Collaboration schemas
class CollaboratorRole(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    CO_AUTHOR = "co-author"


class CollaboratorInvite(BaseModel):
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    role: CollaboratorRole = CollaboratorRole.VIEWER
    message: Optional[str] = None


class CollaboratorResponse(BaseModel):
    id: str
    user_id: str
    paper_id: str
    role: CollaboratorRole
    status: str
    invited_at: datetime
    accepted_at: Optional[datetime] = None

    # User info
    user_name: str
    user_email: str

    class Config:
        from_attributes = True


# Version control schemas
class PaperVersionCreate(BaseModel):
    changes: str = Field(..., min_length=1, max_length=1000)


class PaperVersionResponse(BaseModel):
    id: str
    paper_id: str
    version: str
    title: str
    abstract: str
    created_at: datetime
    created_by: str
    changes: str

    class Config:
        from_attributes = True


# Comment schemas
class PaperCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    section_id: Optional[str] = None
    parent_id: Optional[str] = None


class PaperCommentResponse(BaseModel):
    id: str
    paper_id: str
    section_id: Optional[str] = None
    content: str
    author_id: str
    author_name: str
    created_at: datetime
    resolved: bool
    parent_id: Optional[str] = None
    replies: Optional[List['PaperCommentResponse']] = []

    class Config:
        from_attributes = True


# Update forward reference
PaperCommentResponse.model_rebuild()


# Export filter schemas
class ExportFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    LATEX = "latex"
    MARKDOWN = "markdown"


class PaperExportRequest(BaseModel):
    format: ExportFormat
    include_sections: List[str] = []  # Section IDs to include, empty means all
    include_comments: bool = False
    include_references: bool = True