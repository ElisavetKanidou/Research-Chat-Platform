"""
Pydantic schemas for chat and AI-related API requests and responses
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List




class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AttachmentType(str, Enum):
    EXCEL = "excel"
    PDF = "pdf"
    REFERENCES = "references"
    DATA = "data"
    IMAGE = "image"
    TEXT = "text"


class WritingStyle(str, Enum):
    ACADEMIC = "academic"
    CONCISE = "concise"
    DETAILED = "detailed"
    COLLABORATIVE = "collaborative"


class ContextDepth(str, Enum):
    MINIMAL = "minimal"
    MODERATE = "moderate"
    COMPREHENSIVE = "comprehensive"


# Chat Attachment Schemas
class ChatAttachmentBase(BaseModel):
    type: AttachmentType
    name: str = Field(..., min_length=1, max_length=255)
    size: Optional[str] = None
    url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ChatAttachmentCreate(ChatAttachmentBase):
    pass


class ChatAttachmentResponse(ChatAttachmentBase):
    id: str
    message_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Personalization Settings Schemas
class PersonalizationSettingsBase(BaseModel):
    lab_level: int = Field(default=3, ge=1, le=5)
    personal_level: int = Field(default=2, ge=1, le=5)
    global_level: int = Field(default=1, ge=1, le=5)
    writing_style: WritingStyle = WritingStyle.ACADEMIC
    context_depth: ContextDepth = ContextDepth.MODERATE
    research_focus: List[str] = []
    suggestions_enabled: bool = True


class PersonalizationSettingsUpdate(BaseModel):
    lab_level: Optional[int] = Field(None, ge=1, le=5)
    personal_level: Optional[int] = Field(None, ge=1, le=5)
    global_level: Optional[int] = Field(None, ge=1, le=5)
    writing_style: Optional[WritingStyle] = None
    context_depth: Optional[ContextDepth] = None
    research_focus: Optional[List[str]] = None
    suggestions_enabled: Optional[bool] = None


class PersonalizationSettingsResponse(PersonalizationSettingsBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Paper Context for Chat
class PaperContextBase(BaseModel):
    id: str
    title: str
    status: str
    progress: int = Field(ge=0, le=100)
    research_area: str
    abstract: str
    co_authors: List[str] = []
    current_word_count: int = Field(ge=0)
    target_word_count: int = Field(gt=0)


class UserPaperContextItem(BaseModel):
    id: str
    title: str
    research_area: str
    status: str


# Chat Message Schemas
class ChatMessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    role: MessageRole = MessageRole.USER


class ChatMessageCreate(ChatMessageBase):
    paper_context: Optional[PaperContextBase] = None
    user_papers_context: Optional[List[UserPaperContextItem]] = None
    personalization_settings: Optional[PersonalizationSettingsBase] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[ChatAttachmentCreate]] = []


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    paper_context: Optional[PaperContextBase] = None
    user_papers_context: Optional[List[UserPaperContextItem]] = None
    personalization_settings: Optional[PersonalizationSettingsBase] = None
    attachments: Optional[List[ChatAttachmentCreate]] = []

class ChatMessageResponse(BaseModel):
    messageId: str = Field(..., alias="message_id")
    responseContent: str = Field(..., alias="response_content")
    needsConfirmation: bool = Field(default=False, alias="needs_confirmation")
    attachments: List[Any] = []
    suggestions: List[str] = []
    createdAt: str = Field(..., alias="created_at")
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
        from_attributes = True
        fields = {
            'message_id': 'messageId',
            'response_content': 'responseContent',
            'needs_confirmation': 'needsConfirmation',
            'created_at': 'createdAt'
        }

# Update ChatMessageResponse to include section options
class ChatMessageResponseEnhanced(BaseModel):
    """Enhanced chat response with section addition options"""
    message_id: str
    response_content: str
    needs_confirmation: bool = False
    attachments: List[Any] = []
    suggestions: List[str] = []
    created_at: str
    metadata: Optional[Dict[str, Any]] = None

    # NEW: Available sections to add this content to
    available_sections: List[str] = [
        "abstract",
        "introduction",
        "literature_review",
        "methodology",
        "results",
        "discussion",
        "conclusion"
    ]

    # NEW: Indicates if this content is suitable for adding to sections
    can_add_to_section: bool = True

    class Config:
        fields = {
            'message_id': 'messageId',
            'response_content': 'responseContent',
            'needs_confirmation': 'needsConfirmation',
            'created_at': 'createdAt',
            'available_sections': 'availableSections',
            'can_add_to_section': 'canAddToSection'
        }

class ChatHistoryResponse(BaseModel):
    id: str
    content: str
    role: MessageRole
    created_at: datetime
    paper_context: Optional[str] = None
    needs_confirmation: bool = False
    confirmed: bool = False
    attachments: List[ChatAttachmentResponse] = []
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        fields = {
            'created_at': 'timestamp',
            'paper_context': 'paperContext',
            'needs_confirmation': 'needsConfirmation'
        }


# AI Service Response Schemas
class ResearchInsightsResponse(BaseModel):
    gaps: List[str] = []
    suggestions: List[str] = []
    related_papers: List[str] = []
    methodology_tips: List[str] = []

    class Config:
        fields = {
            'related_papers': 'relatedPapers',
            'methodology_tips': 'methodologyTips'
        }


class PaperOutlineSection(BaseModel):
    title: str
    description: str
    estimated_words: int = Field(gt=0)

    class Config:
        fields = {
            'estimated_words': 'estimatedWords'
        }


class TimelinePhase(BaseModel):
    phase: str
    duration: str
    description: str


class PaperOutlineResponse(BaseModel):
    sections: List[PaperOutlineSection]
    timeline: List[TimelinePhase]


class AIGenerateOutlineRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    research_area: str = Field(..., min_length=1, max_length=255)
    abstract: Optional[str] = None


class WritingAnalysisResponse(BaseModel):
    writing_patterns: Dict[str, Any] = {}
    suggestions: List[str] = []
    readability_score: Optional[float] = None
    word_frequency: Dict[str, int] = {}
    sentiment_analysis: Optional[Dict[str, float]] = None
    improvement_areas: List[str] = []

    class Config:
        fields = {
            'writing_patterns': 'writingPatterns',
            'readability_score': 'readabilityScore',
            'word_frequency': 'wordFrequency',
            'sentiment_analysis': 'sentimentAnalysis',
            'improvement_areas': 'improvementAreas'
        }


class SectionImprovementResponse(BaseModel):
    improvements: List[str] = []
    suggestions: List[str] = []
    clarity_score: Optional[float] = None
    coherence_feedback: Optional[str] = None

    class Config:
        fields = {
            'clarity_score': 'clarityScore',
            'coherence_feedback': 'coherenceFeedback'
        }


# Chat Session Schemas
class ChatSessionCreate(BaseModel):
    title: Optional[str] = None
    paper_id: Optional[str] = None


class ChatSessionResponse(BaseModel):
    id: str
    session_key: str
    title: Optional[str] = None
    message_count: int
    last_activity: datetime
    created_at: datetime
    paper_id: Optional[str] = None

    class Config:
        from_attributes = True
        fields = {
            'session_key': 'sessionKey',
            'message_count': 'messageCount',
            'last_activity': 'lastActivity',
            'created_at': 'createdAt',
            'paper_id': 'paperId'
        }


# AI Interaction Analytics
class AIInteractionCreate(BaseModel):
    interaction_type: str
    model_used: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    response_time_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    paper_id: Optional[str] = None


class AIInteractionResponse(BaseModel):
    id: str
    interaction_type: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_time_ms: Optional[int] = None
    model_used: Optional[str] = None
    success: bool
    created_at: datetime

    class Config:
        from_attributes = True
        fields = {
            'interaction_type': 'interactionType',
            'prompt_tokens': 'promptTokens',
            'completion_tokens': 'completionTokens',
            'total_tokens': 'totalTokens',
            'response_time_ms': 'responseTimeMs',
            'model_used': 'modelUsed',
            'created_at': 'createdAt'
        }


# Advanced Chat Features
class ChatSuggestionsResponse(BaseModel):
    suggestions: List[str] = []
    context_based: bool = False

    class Config:
        fields = {
            'context_based': 'contextBased'
        }


class ChatExportRequest(BaseModel):
    format: str = Field(..., pattern=r'^(json|txt|pdf)$')
    include_metadata: bool = False
    date_range: Optional[Dict[str, datetime]] = None

    class Config:
        fields = {
            'include_metadata': 'includeMetadata',
            'date_range': 'dateRange'
        }


class ChatStatsResponse(BaseModel):
    total_messages: int
    user_messages: int
    assistant_messages: int
    total_conversations: int
    avg_response_time: Optional[float] = None
    most_active_day: Optional[str] = None
    research_areas_discussed: List[str] = []

    class Config:
        fields = {
            'total_messages': 'totalMessages',
            'user_messages': 'userMessages',
            'assistant_messages': 'assistantMessages',
            'total_conversations': 'totalConversations',
            'avg_response_time': 'avgResponseTime',
            'most_active_day': 'mostActiveDay',
            'research_areas_discussed': 'researchAreasDiscussed'
        }


# Validation helpers
class ChatMessageValidator:
    @staticmethod
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()

    @staticmethod
    @validator('attachments')
    def validate_attachments(cls, v):
        if v and len(v) > 10:
            raise ValueError('Cannot attach more than 10 files per message')
        return v
class SectionType(str, Enum):
    """Available paper sections"""
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    LITERATURE_REVIEW = "literature_review"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"


class AddToSectionRequest(BaseModel):
    """Request to add chat content to a paper section"""
    message_id: str = Field(..., description="ID of the chat message containing the content")
    paper_id: str = Field(..., description="ID of the paper to add content to")
    section_type: SectionType = Field(..., description="Type of section to add to")
    content: str = Field(..., description="Content to add to the section")
    append: bool = Field(default=True, description="If True, append to existing content. If False, replace.")


class AddToSectionResponse(BaseModel):
    """Response after adding content to section"""
    success: bool
    message: str
    section_id: str
    updated_content: str
    word_count: int

    class Config:
        fields = {
            'section_id': 'sectionId',
            'updated_content': 'updatedContent',
            'word_count': 'wordCount'
        }


from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SectionType(str, Enum):
    """Enumeration of available paper section types"""
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    LITERATURE_REVIEW = "literature_review"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"


class AddToSectionRequest(BaseModel):
    """Request schema for adding content to a section"""
    message_id: str = Field(
        ...,
        description="ID of the chat message containing the content",
        min_length=1
    )
    paper_id: str = Field(
        ...,
        description="ID of the paper to add content to",
        min_length=1
    )
    section_type: SectionType = Field(
        ...,
        description="Type of section to add content to"
    )
    content: str = Field(
        ...,
        description="Content to add to the section",
        min_length=1,
        max_length=50000
    )
    append: bool = Field(
        default=True,
        description="If true, append to existing content; if false, replace"
    )

    class Config:
        schema_extra = {
            "example": {
                "message_id": "msg-12345",
                "paper_id": "10d46132-fb7b-456f-80ac-2e2aeb49b870",
                "section_type": "abstract",
                "content": "This research investigates...",
                "append": True
            }
        }


class AddToSectionResponse(BaseModel):
    """Response schema after adding content to a section"""
    sectionId: str = Field(..., description="ID of the section")
    sectionType: str = Field(..., description="Type of the section")
    title: str = Field(..., description="Title of the section")
    content: str = Field(..., description="Updated content of the section")
    wordCount: int = Field(..., description="Word count of the section")
    status: str = Field(..., description="Status of the section")
    updatedAt: Optional[str] = Field(None, description="Last update timestamp")

    class Config:
        schema_extra = {
            "example": {
                "sectionId": "section-uuid",
                "sectionType": "abstract",
                "title": "Abstract",
                "content": "This research investigates...",
                "wordCount": 150,
                "status": "in-progress",
                "updatedAt": "2025-11-16T14:30:00Z"
            }
        }


class GetSectionContentResponse(BaseModel):
    """Response schema for getting section content"""
    content: str = Field(..., description="Content of the section")
    sectionType: str = Field(..., description="Type of the section")
    wordCount: int = Field(..., description="Word count")
    status: str = Field(..., description="Section status")

    class Config:
        schema_extra = {
            "example": {
                "content": "This research investigates...",
                "sectionType": "abstract",
                "wordCount": 150,
                "status": "in-progress"
            }
        }


class SectionContent(BaseModel):
    """Individual section content"""
    sectionId: str
    sectionType: str
    title: str
    content: str
    wordCount: int
    status: str
    order: int


class GetAllSectionsResponse(BaseModel):
    """Response schema for getting all sections"""
    sections: List[SectionContent] = Field(
        ...,
        description="List of all sections with their content"
    )
    totalWordCount: int = Field(
        ...,
        description="Total word count across all sections"
    )
    paperProgress: int = Field(
        ...,
        description="Overall paper progress (0-100)"
    )

    class Config:
        schema_extra = {
            "example": {
                "sections": [
                    {
                        "sectionId": "uuid-1",
                        "sectionType": "abstract",
                        "title": "Abstract",
                        "content": "This research...",
                        "wordCount": 150,
                        "status": "completed",
                        "order": 0
                    },
                    {
                        "sectionId": "uuid-2",
                        "sectionType": "introduction",
                        "title": "Introduction",
                        "content": "Background...",
                        "wordCount": 500,
                        "status": "in-progress",
                        "order": 1
                    }
                ],
                "totalWordCount": 650,
                "paperProgress": 25
            }
        }


"""
Additional Chat Schemas - ADD TO END OF chat.py
backend/app/schemas/chat.py

These schemas should be APPENDED to the existing chat.py file
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SectionType(str, Enum):
    """Enumeration of available paper section types"""
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    LITERATURE_REVIEW = "literature_review"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"


class AddToSectionRequest(BaseModel):
    """Request schema for adding content to a section"""
    message_id: str = Field(
        ...,
        description="ID of the chat message containing the content",
        min_length=1
    )
    paper_id: str = Field(
        ...,
        description="ID of the paper to add content to",
        min_length=1
    )
    section_type: SectionType = Field(
        ...,
        description="Type of section to add content to"
    )
    content: str = Field(
        ...,
        description="Content to add to the section",
        min_length=1,
        max_length=50000
    )
    append: bool = Field(
        default=True,
        description="If true, append to existing content; if false, replace"
    )

    class Config:
        schema_extra = {
            "example": {
                "message_id": "msg-12345",
                "paper_id": "10d46132-fb7b-456f-80ac-2e2aeb49b870",
                "section_type": "abstract",
                "content": "This research investigates...",
                "append": True
            }
        }


class AddToSectionResponse(BaseModel):
    """Response schema after adding content to a section"""
    sectionId: str = Field(..., description="ID of the section")
    sectionType: str = Field(..., description="Type of the section")
    title: str = Field(..., description="Title of the section")
    content: str = Field(..., description="Updated content of the section")
    wordCount: int = Field(..., description="Word count of the section")
    status: str = Field(..., description="Status of the section")
    updatedAt: Optional[str] = Field(None, description="Last update timestamp")

    class Config:
        schema_extra = {
            "example": {
                "sectionId": "section-uuid",
                "sectionType": "abstract",
                "title": "Abstract",
                "content": "This research investigates...",
                "wordCount": 150,
                "status": "in-progress",
                "updatedAt": "2025-11-16T14:30:00Z"
            }
        }


class GetSectionContentResponse(BaseModel):
    """Response schema for getting section content"""
    content: str = Field(..., description="Content of the section")
    sectionType: str = Field(..., description="Type of the section")
    wordCount: int = Field(..., description="Word count")
    status: str = Field(..., description="Section status")

    class Config:
        schema_extra = {
            "example": {
                "content": "This research investigates...",
                "sectionType": "abstract",
                "wordCount": 150,
                "status": "in-progress"
            }
        }


class SectionContent(BaseModel):
    """Individual section content"""
    sectionId: str
    sectionType: str
    title: str
    content: str
    wordCount: int
    status: str
    order: int


class GetAllSectionsResponse(BaseModel):
    """Response schema for getting all sections"""
    sections: List[SectionContent] = Field(
        ...,
        description="List of all sections with their content"
    )
    totalWordCount: int = Field(
        ...,
        description="Total word count across all sections"
    )
    paperProgress: int = Field(
        ...,
        description="Overall paper progress (0-100)"
    )

    class Config:
        schema_extra = {
            "example": {
                "sections": [
                    {
                        "sectionId": "uuid-1",
                        "sectionType": "abstract",
                        "title": "Abstract",
                        "content": "This research...",
                        "wordCount": 150,
                        "status": "completed",
                        "order": 0
                    },
                    {
                        "sectionId": "uuid-2",
                        "sectionType": "introduction",
                        "title": "Introduction",
                        "content": "Background...",
                        "wordCount": 500,
                        "status": "in-progress",
                        "order": 1
                    }
                ],
                "totalWordCount": 650,
                "paperProgress": 25
            }
        }