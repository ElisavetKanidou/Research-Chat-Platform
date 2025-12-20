"""
Pydantic schemas for Reference Papers API
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ReferencePaperBase(BaseModel):
    """Base schema for reference paper"""
    title: str = Field(..., min_length=1, max_length=500)
    authors: Optional[str] = Field(None, max_length=500)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    journal: Optional[str] = Field(None, max_length=300)
    doi: Optional[str] = Field(None, max_length=200)
    paper_type: str = Field(..., description="Type: 'lab', 'personal', or 'literature'")
    research_area: Optional[str] = Field(None, max_length=200)
    keywords: Optional[List[str]] = None
    abstract: Optional[str] = None


class ReferencePaperCreate(ReferencePaperBase):
    """Schema for creating a reference paper"""
    pass


class ReferencePaperUpdate(BaseModel):
    """Schema for updating a reference paper"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    authors: Optional[str] = Field(None, max_length=500)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    journal: Optional[str] = Field(None, max_length=300)
    doi: Optional[str] = Field(None, max_length=200)
    research_area: Optional[str] = Field(None, max_length=200)
    keywords: Optional[List[str]] = None
    abstract: Optional[str] = None


class ReferencePaperResponse(ReferencePaperBase):
    """Schema for reference paper response"""
    id: UUID
    user_id: UUID
    file_url: str
    file_size: Optional[int]
    original_filename: str
    is_analyzed: bool
    analysis_date: Optional[str]
    writing_style_features: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None
    times_used: int
    created_at: datetime
    updated_at: datetime

    @model_validator(mode='before')
    @classmethod
    def extract_paper_metadata(cls, data: Any) -> Any:
        """Extract paper_metadata from SQLAlchemy model and expose as metadata"""
        if hasattr(data, 'paper_metadata'):
            # It's a SQLAlchemy model object
            if not hasattr(data, '__dict__'):
                return data
            data_dict = {}
            for key in ['id', 'user_id', 'title', 'authors', 'year', 'journal', 'doi',
                       'paper_type', 'research_area', 'keywords', 'file_url', 'file_size',
                       'original_filename', 'is_analyzed', 'analysis_date',
                       'writing_style_features', 'times_used', 'created_at', 'updated_at']:
                if hasattr(data, key):
                    data_dict[key] = getattr(data, key)
            # Map paper_metadata to metadata
            data_dict['metadata'] = getattr(data, 'paper_metadata', None) or {}
            return data_dict
        return data

    class Config:
        from_attributes = True


class ReferencePaperListResponse(BaseModel):
    """Schema for list of reference papers"""
    papers: List[ReferencePaperResponse]
    total: int
    lab_papers_count: int
    personal_papers_count: int
    literature_papers_count: int


class ReferencePaperUploadResponse(BaseModel):
    """Schema for file upload response"""
    id: UUID
    title: str
    paper_type: str
    file_url: str
    original_filename: str
    is_analyzed: bool
    message: str


class WritingStyleAnalysis(BaseModel):
    """Schema for writing style analysis result"""
    paper_id: UUID
    avg_sentence_length: float
    vocabulary_complexity: float
    passive_voice_ratio: float
    common_phrases: List[str]
    technical_terms: List[str]
    citation_density: float
    section_structure: List[str]
    analyzed_at: datetime
