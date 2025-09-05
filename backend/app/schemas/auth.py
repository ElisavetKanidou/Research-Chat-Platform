"""
Authentication schemas (app/schemas/auth.py)
"""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime


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


class LoginResponse(BaseModel):
    user: 'UserResponse'
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

    class Config:
        fields = {
            'access_token': 'accessToken',
            'refresh_token': 'refreshToken',
            'token_type': 'tokenType',
            'expires_in': 'expiresIn'
        }


class RefreshTokenRequest(BaseModel):
    refresh_token: str

    class Config:
        fields = {
            'refresh_token': 'refreshToken'
        }


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)

    class Config:
        fields = {
            'current_password': 'currentPassword',
            'new_password': 'newPassword'
        }


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

    class Config:
        fields = {
            'new_password': 'newPassword'
        }


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

    class Config:
        fields = {
            'access_token': 'accessToken',
            'refresh_token': 'refreshToken',
            'token_type': 'tokenType',
            'expires_in': 'expiresIn'
        }
