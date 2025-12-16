"""
COMPLETE FIXED VERSION - app/schemas/paper.py για Pydantic v2
Αντικαταστήστε ΟΛΟΚΛΗΡΟ το αρχείο app/schemas/paper.py με αυτό
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from enum import Enum
from uuid import UUID

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
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    status: Optional[SectionStatusEnum] = None
    order: Optional[int] = Field(None, ge=0)

class PaperSectionResponse(PaperSectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    word_count: int
    updated_at: datetime  # Changed from last_modified

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


# Paper Base Schemas
class PaperBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    abstract: Optional[str] = ""
    research_area: Optional[str] = Field(None, max_length=255)
    target_word_count: int = Field(default=8000, gt=0, le=100000)
    tags: Optional[List[str]] = []
    co_authors: Optional[str] = []
    is_public: bool = False

    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v

    @field_validator('co_authors', mode='before')
    @classmethod
    def validate_co_authors(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [author.strip() for author in v.split(',') if author.strip()]
        return v


class PaperCreate(PaperBase):
    status: PaperStatusEnum = PaperStatusEnum.DRAFT
    sections: Optional[List[PaperSectionCreate]] = None

    @field_validator('sections', mode='before')
    @classmethod
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
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True  # ← Αυτό επιτρέπει και τα δύο formats
    )

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    abstract: Optional[str] = None
    status: Optional[PaperStatusEnum] = None
    research_area: Optional[str] = Field(None, max_length=255, alias='researchArea')  # ← ALIAS
    target_word_count: Optional[int] = Field(None, gt=0, le=100000, alias='targetWordCount')
    tags: Optional[List[str]] = None
    co_authors: Optional[List[str]] = Field(None, alias='coAuthors')
    is_public: Optional[bool] = Field(None, alias='isPublic')
    progress: Optional[int] = Field(None, ge=0, le=100)
    current_word_count: Optional[int] = Field(None, ge=0, alias='currentWordCount')

    # Publication fields
    doi: Optional[str] = None
    journal: Optional[str] = None
    publication_date: Optional[datetime] = Field(None, alias='publicationDate')
    citation_count: Optional[int] = Field(None, ge=0, alias='citationCount')

    # Deadline field
    deadline: Optional[datetime] = None

    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v

    @field_validator('co_authors', mode='before')
    @classmethod
    def validate_co_authors(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return [author.strip() for author in v.split(',') if author.strip()]
        return v


class PaperListResponse(BaseModel):
    """Lightweight response for paper lists"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: PaperStatusEnum
    progress: int
    created_at: datetime
    updated_at: datetime  # Changed from last_modified
    current_word_count: int
    target_word_count: int
    research_area: Optional[str] = None  # Make optional
    co_authors: List[str]
    tags: List[str]
    is_public: bool
    deadline: Optional[datetime] = None  # Deadline field

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


class PaperResponse(PaperListResponse):
    """Full paper response with sections"""
    model_config = ConfigDict(from_attributes=True)

    abstract: str
    sections: List[PaperSectionResponse] = []
    owner_id: str

    # Publication fields (optional)
    doi: Optional[str] = None
    journal: Optional[str] = None
    publication_date: Optional[datetime] = None
    citation_count: Optional[int] = 0

    @field_validator('id', 'owner_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


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
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    role: CollaboratorRole = CollaboratorRole.VIEWER
    message: Optional[str] = None


class CollaboratorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    paper_id: str
    role: CollaboratorRole
    status: str
    invited_at: datetime
    accepted_at: Optional[datetime] = None
    user_name: str
    user_email: str

    @field_validator('id', 'user_id', 'paper_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


# Version control schemas
class PaperVersionCreate(BaseModel):
    changes: str = Field(..., min_length=1, max_length=1000)


class PaperVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    paper_id: str
    version: str
    title: str
    abstract: str
    created_at: datetime
    created_by: str
    changes: str

    @field_validator('id', 'paper_id', 'created_by', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


# Comment schemas
class PaperCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    section_id: Optional[str] = None
    parent_id: Optional[str] = None


class PaperCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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

    @field_validator('id', 'paper_id', 'section_id', 'author_id', 'parent_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if v is None:
            return None
        if isinstance(v, UUID):
            return str(v)
        return v


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
    include_sections: List[str] = []
    include_comments: bool = False
    include_references: bool = True


"""
Paper AI Settings Schemas - ADD TO app/schemas/paper.py
Add these at the end of the file
"""


# ==================== PAPER AI SETTINGS ====================

class PaperAISettings(BaseModel):
    """AI Personalization settings for a specific paper"""
    use_global_settings: bool = Field(default=True, alias="useGlobalSettings")
    lab_level: Optional[int] = Field(default=None, alias="labLevel", ge=1, le=10)
    personal_level: Optional[int] = Field(default=None, alias="personalLevel", ge=1, le=10)
    global_level: Optional[int] = Field(default=None, alias="globalLevel", ge=1, le=10)
    writing_style: Optional[str] = Field(default=None, alias="writingStyle")
    context_depth: Optional[str] = Field(default=None, alias="contextDepth")
    research_focus: Optional[List[str]] = Field(default=None, alias="researchFocus")
    suggestions_enabled: Optional[bool] = Field(default=None, alias="suggestionsEnabled")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "useGlobalSettings": False,
                "labLevel": 8,
                "personalLevel": 9,
                "globalLevel": 6,
                "writingStyle": "detailed",
                "contextDepth": "comprehensive",
                "researchFocus": ["quantum computing", "optimization"],
                "suggestionsEnabled": True
            }
        }
    }


class PaperAISettingsUpdate(BaseModel):
    """Update AI settings for a paper"""
    use_global_settings: Optional[bool] = Field(default=None, alias="useGlobalSettings")
    lab_level: Optional[int] = Field(default=None, alias="labLevel", ge=1, le=10)
    personal_level: Optional[int] = Field(default=None, alias="personalLevel", ge=1, le=10)
    global_level: Optional[int] = Field(default=None, alias="globalLevel", ge=1, le=10)
    writing_style: Optional[str] = Field(default=None, alias="writingStyle")
    context_depth: Optional[str] = Field(default=None, alias="contextDepth")
    research_focus: Optional[List[str]] = Field(default=None, alias="researchFocus")
    suggestions_enabled: Optional[bool] = Field(default=None, alias="suggestionsEnabled")

    model_config = {"populate_by_name": True}


class PaperAISettingsResponse(BaseModel):
    """Response with paper's AI settings (merged with global if needed)"""
    paper_id: str = Field(alias="paperId")
    is_using_global: bool = Field(alias="isUsingGlobal")
    settings: Dict[str, Any]
    global_settings: Optional[Dict[str, Any]] = Field(default=None, alias="globalSettings")

    model_config = {"populate_by_name": True}