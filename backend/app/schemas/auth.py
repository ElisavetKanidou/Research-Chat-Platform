"""
Authentication schemas (app/schemas/auth.py) - FIXED VERSION
"""
from typing import Optional, TYPE_CHECKING, Any
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime

# Use TYPE_CHECKING to avoid circular import at runtime
if TYPE_CHECKING:
    from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=2, max_length=255)
    affiliation: Optional[str] = Field(None, max_length=255)
    research_interests: Optional[list[str]] = []

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    class Config:
        populate_by_name = True


class LoginResponse(BaseModel):
    user: Any  # Will be UserResponse, but use Any to avoid circular import
    access_token: str = Field(..., serialization_alias='accessToken')
    refresh_token: str = Field(..., serialization_alias='refreshToken')
    token_type: str = Field(default="bearer", serialization_alias='tokenType')
    expires_in: int = Field(..., serialization_alias='expiresIn')

    class Config:
        populate_by_name = True


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., alias='refreshToken')

    class Config:
        populate_by_name = True


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8, alias='currentPassword')
    new_password: str = Field(..., min_length=8, alias='newPassword')

    class Config:
        populate_by_name = True


class ResetPasswordRequest(BaseModel):
    email: EmailStr

    class Config:
        populate_by_name = True


class ResetPasswordConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, alias='newPassword')

    class Config:
        populate_by_name = True


class TokenResponse(BaseModel):
    access_token: str = Field(..., serialization_alias='accessToken')
    refresh_token: str = Field(..., serialization_alias='refreshToken')
    token_type: str = Field(default="bearer", serialization_alias='tokenType')
    expires_in: int = Field(..., serialization_alias='expiresIn')

    class Config:
        populate_by_name = True