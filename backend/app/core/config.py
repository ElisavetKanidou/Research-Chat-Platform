"""
Configuration settings - Pydantic v2 with better parsing
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Optional, Union
import secrets


class Settings(BaseSettings):
    """Application settings"""

    # Basic app settings
    DEBUG: bool = False
    PROJECT_NAME: str = "Research Platform API"
    VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
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

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000

    # Email
    EMAIL_FROM: str = "noreply@research-platform.com"
    EMAIL_FROM_NAME: str = "Research Platform"
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

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