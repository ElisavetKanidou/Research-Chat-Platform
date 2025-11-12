"""
User schemas - COMPLETE VERSION WITH FIXED PREFERENCES HANDLING
app/schemas/user.py
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from datetime import datetime
from enum import Enum
from uuid import UUID
import json

# ==================== ENUMS ====================

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


# ==================== NOTIFICATION PREFERENCES ====================

class NotificationPreferences(BaseModel):
    """Notification preferences - accepts both camelCase and snake_case"""
    email_notifications: Optional[bool] = Field(default=None, alias="emailNotifications")
    deadline_reminders: Optional[bool] = Field(default=None, alias="deadlineReminders")
    collaboration_updates: Optional[bool] = Field(default=None, alias="collaborationUpdates")
    ai_suggestions: Optional[bool] = Field(default=None, alias="aiSuggestions")
    weekly_reports: Optional[bool] = Field(default=None, alias="weeklyReports")
    push_notifications: Optional[bool] = Field(default=None, alias="pushNotifications")
    reminder_frequency: Optional[str] = Field(default=None, alias="reminderFrequency")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "emailNotifications": True,
                "deadlineReminders": True,
                "collaborationUpdates": True
            }
        }
    }


# ==================== PRIVACY SETTINGS ====================

class PrivacySettings(BaseModel):
    """Privacy settings - accepts both camelCase and snake_case"""
    profile_visibility: Optional[str] = Field(default=None, alias="profileVisibility")
    share_analytics: Optional[bool] = Field(default=None, alias="shareAnalytics")
    data_sync_enabled: Optional[bool] = Field(default=None, alias="dataSyncEnabled")
    allow_research_sharing: Optional[bool] = Field(default=None, alias="allowResearchSharing")
    tracking_opt_out: Optional[bool] = Field(default=None, alias="trackingOptOut")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "profileVisibility": "private",
                "shareAnalytics": False
            }
        }
    }


# ==================== AI PERSONALIZATION ====================

class AIPersonalizationSettings(BaseModel):
    """AI Personalization settings - accepts both camelCase and snake_case"""
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
                "labLevel": 8,
                "personalLevel": 9,
                "globalLevel": 6,
                "writingStyle": "academic"
            }
        }
    }


# ==================== USER PREFERENCES UPDATE ====================

class UserPreferencesUpdate(BaseModel):
    """
    Schema for updating user preferences

    CRITICAL: This accepts BOTH camelCase (from frontend) and snake_case (Python)
    All fields are optional to support partial updates
    """
    # Basic preferences
    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = Field(default=None, alias="dateFormat")
    default_word_count: Optional[int] = Field(default=None, alias="defaultWordCount", gt=0)
    auto_save: Optional[bool] = Field(default=None, alias="autoSave")

    # Nested preferences (can be dict or Pydantic model)
    notifications: Optional[NotificationPreferences] = None
    privacy: Optional[PrivacySettings] = None
    ai_personalization: Optional[AIPersonalizationSettings] = Field(default=None, alias="aiPersonalization")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "theme": "dark",
                "language": "en",
                "dateFormat": "MM/DD/YYYY",
                "defaultWordCount": 8000,
                "notifications": {
                    "emailNotifications": True,
                    "deadlineReminders": True
                },
                "aiPersonalization": {
                    "labLevel": 8,
                    "personalLevel": 9,
                    "globalLevel": 6
                }
            }
        }
    }


# ==================== PERSONAL INFO ====================

class PersonalInfoUpdate(BaseModel):
    """Schema for updating personal information"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    affiliation: Optional[str] = Field(None, max_length=255)
    research_interests: Optional[List[str]] = Field(default=None, alias="researchInterests")
    orcid_id: Optional[str] = Field(None, max_length=50, alias="orcidId")
    bio: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=255)

    model_config = {"populate_by_name": True}


# ==================== USER UPDATE ====================

class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=500, alias="avatarUrl")
    bio: Optional[str] = Field(None, max_length=1000)
    affiliation: Optional[str] = Field(None, max_length=255)
    orcid_id: Optional[str] = Field(None, max_length=50, alias="orcidId")
    website: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=255)
    research_interests: Optional[List[str]] = Field(default=None, alias="researchInterests")
    preferences: Optional[UserPreferencesUpdate] = None

    model_config = {"populate_by_name": True}


# ==================== USER CREATE ====================

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
    affiliation: Optional[str] = Field(None, max_length=255)
    research_interests: Optional[List[str]] = Field(default=None, alias="researchInterests")

    model_config = {"populate_by_name": True}


# ==================== USER RESPONSE ====================

class UserResponse(BaseModel):
    """Complete user profile response"""
    id: str
    email: EmailStr
    name: str
    avatar_url: Optional[str] = Field(default=None, alias="avatarUrl")
    bio: Optional[str] = None
    affiliation: Optional[str] = None
    orcid_id: Optional[str] = Field(default=None, alias="orcidId")
    website: Optional[str] = None
    location: Optional[str] = None
    research_interests: List[str] = Field(default_factory=list, alias="researchInterests")

    is_active: bool = Field(alias="isActive")
    is_verified: bool = Field(alias="isVerified")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    last_login_at: Optional[datetime] = Field(default=None, alias="lastLoginAt")

    # Subscription info
    subscription_plan: str = Field(alias="subscriptionPlan")
    subscription_status: str = Field(alias="subscriptionStatus")

    # Preferences as dict (will be returned as camelCase JSON)
    preferences: Optional[Dict[str, Any]] = None

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string"""
        if isinstance(v, UUID):
            return str(v)
        return v

    @field_validator('preferences', mode='before')
    @classmethod
    def parse_preferences(cls, v):
        """Parse preferences JSON from database"""
        if v is None:
            return {
                "theme": "light",
                "language": "en",
                "timezone": "UTC",
                "dateFormat": "MM/dd/yyyy",
                "defaultWordCount": 8000,
                "autoSave": True,
                "notifications": {
                    "emailNotifications": True,
                    "deadlineReminders": True,
                    "collaborationUpdates": True,
                    "aiSuggestions": False,
                    "weeklyReports": True,
                    "pushNotifications": True,
                    "reminderFrequency": "weekly"
                },
                "privacy": {
                    "profileVisibility": "private",
                    "shareAnalytics": False,
                    "dataSyncEnabled": True,
                    "allowResearchSharing": False,
                    "trackingOptOut": False
                },
                "aiPersonalization": {
                    "labLevel": 7,
                    "personalLevel": 8,
                    "globalLevel": 5,
                    "writingStyle": "academic",
                    "researchFocus": [],
                    "suggestionsEnabled": True,
                    "contextDepth": "moderate"
                }
            }
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return {}
        return {}

    @field_validator('research_interests', mode='before')
    @classmethod
    def parse_research_interests(cls, v):
        """Parse research_interests JSON from database"""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        return []

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


# ==================== PUBLIC PROFILE ====================

class UserPublicResponse(BaseModel):
    """Public user profile (limited information)"""
    id: str
    name: str
    avatar_url: Optional[str] = Field(default=None, alias="avatarUrl")
    bio: Optional[str] = None
    affiliation: Optional[str] = None
    location: Optional[str] = None
    research_interests: List[str] = Field(default_factory=list, alias="researchInterests")
    created_at: datetime = Field(alias="createdAt")

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string"""
        if isinstance(v, UUID):
            return str(v)
        return v

    @field_validator('research_interests', mode='before')
    @classmethod
    def parse_research_interests(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        return []

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


# ==================== USER STATISTICS ====================

class UserStatsResponse(BaseModel):
    """User statistics and analytics"""
    total_papers: int = Field(alias="totalPapers")
    published_papers: int = Field(alias="publishedPapers")
    total_words: int = Field(alias="totalWords")
    collaborators: int
    research_areas: List[str] = Field(alias="researchAreas")
    avg_completion_time: Optional[float] = Field(default=None, alias="avgCompletionTime")
    productivity_score: Optional[float] = Field(default=None, alias="productivityScore")
    last_updated: datetime = Field(alias="lastUpdated")

    model_config = {"populate_by_name": True}


# ==================== USER ACTIVITY ====================

class UserActivityResponse(BaseModel):
    """User activity log entry"""
    id: str
    action: str
    resource: str
    resource_id: str = Field(alias="resourceId")
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


# ==================== API KEYS ====================

class APIKeyCreate(BaseModel):
    """API key creation request"""
    name: str = Field(..., min_length=1, max_length=255)
    permissions: List[str] = []
    expires_at: Optional[datetime] = Field(default=None, alias="expiresAt")

    model_config = {"populate_by_name": True}


class APIKeyResponse(BaseModel):
    """API key response"""
    id: str
    name: str
    key: str  # Only shown once during creation
    permissions: List[str]
    created_at: datetime = Field(alias="createdAt")
    last_used: Optional[datetime] = Field(default=None, alias="lastUsed")
    is_active: bool = Field(alias="isActive")
    expires_at: Optional[datetime] = Field(default=None, alias="expiresAt")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


# ==================== INTEGRATIONS ====================

class UserIntegrationResponse(BaseModel):
    """Third-party service integration"""
    id: str
    service: str
    is_connected: bool = Field(alias="isConnected")
    last_sync: Optional[datetime] = Field(default=None, alias="lastSync")
    created_at: datetime = Field(alias="createdAt")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


# ==================== TWO-FACTOR AUTH ====================

class TwoFactorSetupResponse(BaseModel):
    """2FA setup response"""
    qr_code: str = Field(alias="qrCode")
    secret: str
    backup_codes: List[str] = Field(default_factory=list, alias="backupCodes")

    model_config = {"populate_by_name": True}


class TwoFactorVerifyRequest(BaseModel):
    """2FA verification request"""
    code: str = Field(..., min_length=6, max_length=6)


# ==================== PASSWORD CHANGE ====================

class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str = Field(..., min_length=8, alias="currentPassword")
    new_password: str = Field(..., min_length=8, max_length=100, alias="newPassword")

    model_config = {"populate_by_name": True}


# ==================== EMAIL CHANGE ====================

class EmailChangeRequest(BaseModel):
    """Email change request"""
    new_email: EmailStr = Field(alias="newEmail")
    password: str

    model_config = {"populate_by_name": True}


# ==================== ACCOUNT DELETION ====================

class AccountDeletionRequest(BaseModel):
    """Account deletion request"""
    password: str
    confirmation: str = Field(..., pattern="^DELETE MY ACCOUNT$")
    reason: Optional[str] = None