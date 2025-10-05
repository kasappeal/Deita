"""
Authentication-related Pydantic schemas.
"""
from pydantic import BaseModel, EmailStr


class MagicLinkRequest(BaseModel):
    """Schema for requesting a magic link."""
    email: EmailStr


class MagicLinkResponse(BaseModel):
    """Schema for magic link request response."""
    message: str


class VerifyTokenRequest(BaseModel):
    """Schema for verifying a magic link token."""
    token: str


class AuthResponse(BaseModel):
    """Schema for authentication response with JWT."""
    jwt: str
    user: dict


class UserInfo(BaseModel):
    """Schema for user info response."""
    id: str
    email: EmailStr
    name: str
