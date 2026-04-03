"""
AEGISCORE — Authentication Schemas
Pydantic v2 models for login, token, and user profile responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Password cannot be empty")
        return v


class RefreshRequest(BaseModel):
    """Request body for POST /auth/refresh."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Response containing JWT access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AccessTokenResponse(BaseModel):
    """Response for token refresh — only new access token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfile(BaseModel):
    """Current user profile returned by GET /auth/me."""
    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
    """Request body for user registration."""
    email: EmailStr
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip()
