"""
Configuration settings - FIXED with dotenv loading
backend/app/core/config.py
"""
# CRITICAL: Load .env file FIRST before anything else
from dotenv import load_dotenv
load_dotenv()  # This MUST be at the top!

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Optional, Union
import secrets
import os


class Settings(BaseSettings):
    """Application settings"""

    # Basic app settings
    DEBUG: bool = False
    PROJECT_NAME: str = "Research Platform API"
    VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 1
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/research_platform"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # CORS - Accept string or list
    ALLOWED_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173"]  # Default fallback

    # Groq AI (FREE!)
    GROQ_API_KEY: Optional[str] = None

    # OpenAI (Optional)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000

    # Google Gemini AI (FREE!)
    GEMINI_API_KEY: Optional[str] = None

    # GPT-OSS Local AI (120B Model)
    GPT_OSS_API_KEY: Optional[str] = None
    GPT_OSS_BASE_URL: str = "http://34.9.154.79:11481/api/chat/completions"
    GPT_OSS_MODEL: str = "gpt-oss:120b"

    # Email - Resend Service
    RESEND_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "onboarding@resend.dev"
    EMAIL_FROM_NAME: str = "Research Platform"
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Frontend URL (for OAuth redirects)
    FRONTEND_URL: str = "http://localhost:5173"

    # ==================== INTEGRATIONS ====================

    # Google Drive OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:5173/settings/integrations/google-drive/callback"

    # Dropbox OAuth
    DROPBOX_APP_KEY: Optional[str] = None
    DROPBOX_APP_SECRET: Optional[str] = None
    DROPBOX_REDIRECT_URI: str = "http://localhost:5173/settings/integrations/dropbox/callback"

    # Mendeley OAuth
    MENDELEY_CLIENT_ID: Optional[str] = None
    MENDELEY_CLIENT_SECRET: Optional[str] = None
    MENDELEY_REDIRECT_URI: str = "http://localhost:5173/settings/integrations/mendeley/callback"

    # File storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760
    ALLOWED_EXTENSIONS: List[str] = Field(default=[".pdf", ".docx", ".txt", ".md"])

    # AWS (optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # Features
    ENABLE_AI_FEATURES: bool = True
    AI_RESPONSE_TIMEOUT: int = 30
    MAX_CHAT_HISTORY: int = 50
    ENABLE_ANALYTICS: bool = True

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100

    # Background tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Create settings instance
settings = Settings()

# Print configuration on startup (only in DEBUG mode)
if settings.DEBUG:
    print("\n" + "="*60)
    print("✅ CONFIGURATION LOADED")
    print("="*60)
    print(f"📦 Project: {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print(f"💾 Database: {settings.DATABASE_URL[:40]}...")
    print(f"🤖 Groq API: {'✅ Configured' if settings.GROQ_API_KEY else '❌ Not Set'}")
    print(f"🔐 OpenAI API: {'✅ Configured' if settings.OPENAI_API_KEY else '⚠️  Optional'}")
    print(f"🧠 Gemini API: {'✅ Configured' if settings.GEMINI_API_KEY else '⚠️  Optional'}")
    print(f"🚀 GPT-OSS API: {'✅ Configured' if settings.GPT_OSS_API_KEY else '⚠️  Optional'}")
    print(f"📧 Resend Email: {'✅ Configured' if settings.RESEND_API_KEY else '⚠️  Optional'}")
    print(f"☁️  Google Drive: {'✅ Configured' if settings.GOOGLE_CLIENT_ID else '⚠️  Optional'}")
    print(f"📦 Dropbox: {'✅ Configured' if settings.DROPBOX_APP_KEY else '⚠️  Optional'}")
    print(f"📚 Mendeley: {'✅ Configured' if settings.MENDELEY_CLIENT_ID else '⚠️  Optional'}")
    print(f"🌐 CORS Origins: {len(settings.ALLOWED_ORIGINS)} configured")
    print(f"💬 Max Chat History: {settings.MAX_CHAT_HISTORY}")
    print(f"📊 AI Features: {'Enabled' if settings.ENABLE_AI_FEATURES else 'Disabled'}")
    print("="*60 + "\n")


# Helper functions
def get_database_url() -> str:
    """Get the database URL for SQLAlchemy"""
    return settings.DATABASE_URL


def get_async_database_url() -> str:
    """Get the async database URL for SQLAlchemy"""
    if "postgresql://" in settings.DATABASE_URL:
        return settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    return settings.DATABASE_URL


def get_redis_url() -> str:
    """Get Redis URL for connections"""
    return settings.REDIS_URL


def get_groq_config() -> dict:
    """Get Groq AI configuration"""
    return {
        "api_key": settings.GROQ_API_KEY,
        "timeout": settings.AI_RESPONSE_TIMEOUT
    }


def get_openai_config() -> dict:
    """Get OpenAI configuration"""
    return {
        "api_key": settings.OPENAI_API_KEY,
        "model": settings.OPENAI_MODEL,
        "max_tokens": settings.OPENAI_MAX_TOKENS,
        "timeout": settings.AI_RESPONSE_TIMEOUT
    }


def get_email_config() -> dict:
    """Get email configuration"""
    return {
        "smtp_host": settings.SMTP_HOST,
        "smtp_port": settings.SMTP_PORT,
        "smtp_user": settings.SMTP_USER,
        "smtp_password": settings.SMTP_PASSWORD,
        "from_email": settings.EMAIL_FROM,
        "from_name": settings.EMAIL_FROM_NAME
    }


def get_gpt_oss_config() -> dict:
    """Get GPT-OSS configuration"""
    return {
        "api_key": settings.GPT_OSS_API_KEY,
        "base_url": settings.GPT_OSS_BASE_URL,
        "model": settings.GPT_OSS_MODEL,
        "timeout": None  # No timeout
    }


# ==================== INTEGRATION HELPER FUNCTIONS ====================

def get_resend_config() -> dict:
    """Get Resend email service configuration"""
    return {
        "api_key": settings.RESEND_API_KEY,
        "from_email": settings.EMAIL_FROM,
        "from_name": settings.EMAIL_FROM_NAME
    }


def get_google_drive_config() -> dict:
    """Get Google Drive OAuth configuration"""
    return {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scopes": [
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive.readonly"
        ]
    }


def get_dropbox_config() -> dict:
    """Get Dropbox OAuth configuration"""
    return {
        "app_key": settings.DROPBOX_APP_KEY,
        "app_secret": settings.DROPBOX_APP_SECRET,
        "redirect_uri": settings.DROPBOX_REDIRECT_URI
    }


def get_mendeley_config() -> dict:
    """Get Mendeley OAuth configuration"""
    return {
        "client_id": settings.MENDELEY_CLIENT_ID,
        "client_secret": settings.MENDELEY_CLIENT_SECRET,
        "redirect_uri": settings.MENDELEY_REDIRECT_URI,
        "scopes": ["all"]
    }