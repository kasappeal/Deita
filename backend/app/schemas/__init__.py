"""
Pydantic schemas for API request/response models.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    full_name: str | None = None


class User(UserBase):
    """User schema for responses."""

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workspace schemas
class WorkspaceCreate(BaseModel):
    """Schema for creating a workspace."""

    name: str
    visibility: Literal["public", "private"] | None = None


class WorkspaceUpdate(BaseModel):
    """Schema for updating a workspace."""

    name: str | None = None
    visibility: Literal["public", "private"] | None = None


class Workspace(BaseModel):
    """Workspace schema for responses."""

    id: uuid.UUID
    name: str
    visibility: Literal["public", "private"]
    created_at: datetime
    last_accessed_at: datetime

    class Config:
        from_attributes = True


class HealthCheck(BaseModel):
    """Health check response schema."""

    status: str
    message: str
    version: str
    timestamp: datetime


class HelloWorld(BaseModel):
    """Hello world response schema."""

    message: str
    version: str
    environment: str
