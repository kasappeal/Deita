"""
Pydantic schemas for API request/response models.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


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

    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


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


# Import workspace schemas
from .workspace import (
    CreateWorkspaceRequest,
    CreateOrphanWorkspaceRequest,
    UpdateWorkspaceRequest,
    ClaimWorkspaceRequest,
    WorkspaceVisibilityRequest,
    ShareWorkspaceRequest,
    WorkspaceFilters,
    WorkspaceResponse,
    WorkspaceListResponse,
    WorkspaceDetailsResponse,
    ValidateWorkspaceNameRequest,
    ValidateWorkspaceNameResponse,
    ShareLinkResponse,
    WorkspaceUsageResponse,
    WorkspaceUsageSchema,
    WorkspaceAuditLogSchema,
)

__all__ = [
    "UserBase", "UserCreate", "UserUpdate", "User",
    "HealthCheck", "HelloWorld",
    "CreateWorkspaceRequest", "CreateOrphanWorkspaceRequest", 
    "UpdateWorkspaceRequest", "ClaimWorkspaceRequest",
    "WorkspaceVisibilityRequest", "ShareWorkspaceRequest",
    "WorkspaceFilters", "WorkspaceResponse", "WorkspaceListResponse",
    "WorkspaceDetailsResponse", "ValidateWorkspaceNameRequest",
    "ValidateWorkspaceNameResponse", "ShareLinkResponse",
    "WorkspaceUsageResponse", "WorkspaceUsageSchema", "WorkspaceAuditLogSchema"
]
