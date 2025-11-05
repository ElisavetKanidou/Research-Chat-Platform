"""
User schemas (app/schemas/user.py)
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator, field_validator  # ← Πρόσθεσε field_validator
from datetime import datetime
from enum import Enum
from uuid import UUID

class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class SubscriptionPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    ACADEMIC = "academic"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"


class ProfileVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INSTITUTION = "institution"


class ReminderFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# Personal Info Schemas
class PersonalInfoBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    affiliation: Optional[str] = Field(None, max_length=255)
    research_interests: List[str] = []
    orcid_id: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=255)

    class Config:
        fields = {
            'research_interests': 'researchInterests',
            'orcid_id': 'orcidId'
        }


class PersonalInfoUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    affiliation: Optional[str] = Field(None, max_length=255)
    research_interests: Optional[List[str]] = None
    orcid_id: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=255)

    class Config:
        fields = {
            'research_interests': 'researchInterests',
            'orcid_id': 'orcidId'
        }


# Notification Preferences
class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    deadline_reminders: bool = True
    collaboration_updates: bool = True
    ai_suggestions: bool = True
    weekly_reports: bool = False
    push_notifications: bool = True
    reminder_frequency: ReminderFrequency = ReminderFrequency.WEEKLY

    class Config:
        fields = {
            'email_notifications': 'emailNotifications',
            'deadline_reminders': 'deadlineReminders',
            'collaboration_updates': 'collaborationUpdates',
            'ai_suggestions': 'aiSuggestions',
            'weekly_reports': 'weeklyReports',
            'push_notifications': 'pushNotifications',
            'reminder_frequency': 'reminderFrequency'
        }


# Privacy Settings
class PrivacySettings(BaseModel):
    profile_visibility: ProfileVisibility = ProfileVisibility.PRIVATE
    share_analytics: bool = False
    data_sync_enabled: bool = True
    allow_research_sharing: bool = False
    tracking_opt_out: bool = False

    class Config:
        fields = {
            'profile_visibility': 'profileVisibility',
            'share_analytics': 'shareAnalytics',
            'data_sync_enabled': 'dataSyncEnabled',
            'allow_research_sharing': 'allowResearchSharing',
            'tracking_opt_out': 'trackingOptOut'
        }


# AI Personalization Settings
class AIPersonalizationSettings(BaseModel):
    lab_level: int = Field(default=3, ge=1, le=5)
    personal_level: int = Field(default=2, ge=1, le=5)
    global_level: int = Field(default=1, ge=1, le=5)
    writing_style: str = "academic"
    research_focus: List[str] = []
    suggestions_enabled: bool = True
    context_depth: str = "moderate"

    class Config:
        fields = {
            'lab_level': 'labLevel',
            'personal_level': 'personalLevel',
            'global_level': 'globalLevel',
            'writing_style': 'writingStyle',
            'research_focus': 'researchFocus',
            'suggestions_enabled': 'suggestionsEnabled',
            'context_depth': 'contextDepth'
        }


# User Preferences
class UserPreferences(BaseModel):
    theme: Theme = Theme.LIGHT
    language: str = "en"
    timezone: str = "UTC"
    date_format: str = "MM/dd/yyyy"
    default_word_count: int = Field(default=8000, gt=0)
    auto_save: bool = True
    notifications: NotificationPreferences = NotificationPreferences()
    privacy: PrivacySettings = PrivacySettings()
    ai_personalization: AIPersonalizationSettings = AIPersonalizationSettings()

    class Config:
        fields = {
            'date_format': 'dateFormat',
            'default_word_count': 'defaultWordCount',
            'auto_save': 'autoSave',
            'ai_personalization': 'aiPersonalization'
        }


class UserPreferencesUpdate(BaseModel):
    theme: Optional[Theme] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    default_word_count: Optional[int] = Field(None, gt=0)
    auto_save: Optional[bool] = None
    notifications: Optional[NotificationPreferences] = None
    privacy: Optional[PrivacySettings] = None
    ai_personalization: Optional[AIPersonalizationSettings] = None

    class Config:
        fields = {
            'date_format': 'dateFormat',
            'default_word_count': 'defaultWordCount',
            'auto_save': 'autoSave',
            'ai_personalization': 'aiPersonalization'
        }


# Subscription Feature
class SubscriptionFeature(BaseModel):
    name: str
    enabled: bool
    limit: Optional[int] = None
    used: Optional[int] = None


# User Subscription
class UserSubscription(BaseModel):
    plan: SubscriptionPlan = SubscriptionPlan.FREE
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    start_date: datetime
    end_date: Optional[datetime] = None
    features: List[SubscriptionFeature] = []

    class Config:
        fields = {
            'start_date': 'startDate',
            'end_date': 'endDate'
        }


# User Base Schema
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    affiliation: Optional[str] = Field(None, max_length=255)
    research_interests: List[str] = []

    class Config:
        fields = {
            'research_interests': 'researchInterests'
        }


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=1000)
    affiliation: Optional[str] = Field(None, max_length=255)
    orcid_id: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=255)
    research_interests: Optional[List[str]] = None
    preferences: Optional[UserPreferencesUpdate] = None

    class Config:
        fields = {
            'avatar_url': 'avatarUrl',
            'orcid_id': 'orcidId',
            'research_interests': 'researchInterests'
        }


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    affiliation: Optional[str] = None
    orcid_id: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    research_interests: List[str] = []

    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    # Subscription info
    subscription_plan: SubscriptionPlan
    subscription_status: SubscriptionStatus

    # For frontend compatibility, we include these nested objects
    personal_info: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    subscription: Optional[Dict[str, Any]] = None

    # ← ΠΡΟΣΘΕΣΕ ΑΥΤΟ ΕΔΩ (πριν το Config)
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string"""
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True
        fields = {
            'avatar_url': 'avatarUrl',
            'orcid_id': 'orcidId',
            'research_interests': 'researchInterests',
            'is_active': 'isActive',
            'is_verified': 'isVerified',
            'created_at': 'createdAt',
            'last_login_at': 'lastLoginAt',
            'subscription_plan': 'subscriptionPlan',
            'subscription_status': 'subscriptionStatus',
            'personal_info': 'personalInfo'
        }

    @validator('personal_info', pre=True, always=True)
    def build_personal_info(cls, v, values):
        """Build personal_info object for frontend compatibility"""
        return {
            'name': values.get('name'),
            'email': values.get('email'),
            'affiliation': values.get('affiliation'),
            'researchInterests': values.get('research_interests', []),
            'orcidId': values.get('orcid_id'),
            'bio': values.get('bio'),
            'website': values.get('website'),
            'location': values.get('location'),
        }

    @validator('subscription', pre=True, always=True)
    def build_subscription(cls, v, values):
        """Build subscription object for frontend compatibility"""
        return {
            'plan': values.get('subscription_plan'),
            'status': values.get('subscription_status'),
            'startDate': values.get('created_at'),  # Simplified
            'features': [],
        }


class UserPublicResponse(BaseModel):
    """Public user profile (limited information)"""
    id: str
    name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    affiliation: Optional[str] = None
    location: Optional[str] = None
    research_interests: List[str] = []
    created_at: datetime

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string"""
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True
        fields = {
            'avatar_url': 'avatarUrl',
            'research_interests': 'researchInterests',
            'created_at': 'createdAt'
        }


class UserStatsResponse(BaseModel):
    """User statistics and analytics"""
    total_papers: int
    published_papers: int
    total_words: int
    collaborators: int
    research_areas: List[str]
    avg_completion_time: Optional[float] = None
    productivity_score: Optional[float] = None
    last_updated: datetime

    class Config:
        fields = {
            'total_papers': 'totalPapers',
            'published_papers': 'publishedPapers',
            'total_words': 'totalWords',
            'research_areas': 'researchAreas',
            'avg_completion_time': 'avgCompletionTime',
            'productivity_score': 'productivityScore',
            'last_updated': 'lastUpdated'
        }


class UserActivityResponse(BaseModel):
    """User activity log entry"""
    id: str
    action: str
    resource: str
    resource_id: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True
        fields = {
            'resource_id': 'resourceId'
        }


class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    permissions: List[str] = []
    expires_at: Optional[datetime] = None

    class Config:
        fields = {
            'expires_at': 'expiresAt'
        }


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str  # Only shown once during creation
    permissions: List[str]
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        fields = {
            'created_at': 'createdAt',
            'last_used': 'lastUsed',
            'is_active': 'isActive',
            'expires_at': 'expiresAt'
        }


class UserIntegrationResponse(BaseModel):
    """Third-party service integration"""
    id: str
    service: str
    is_connected: bool
    last_sync: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
        fields = {
            'is_connected': 'isConnected',
            'last_sync': 'lastSync',
            'created_at': 'createdAt'
        }


class TwoFactorSetupResponse(BaseModel):
    qr_code: str
    secret: str

    class Config:
        fields = {
            'qr_code': 'qrCode'
        }


class TwoFactorVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


# Update forward references
from app.schemas.auth import LoginResponse

LoginResponse.model_rebuild()