"""
Pydantic schemas for workspace API request/response models.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class WorkspaceUsageSchema(BaseModel):
    """Schema for workspace usage information."""
    
    file_count: int = 0
    storage_used_bytes: int = 0
    query_count: int = 0
    last_accessed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WorkspaceAuditLogSchema(BaseModel):
    """Schema for workspace audit log entries."""
    
    id: UUID
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WorkspaceBase(BaseModel):
    """Base workspace schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Workspace name")
    description: Optional[str] = Field(None, max_length=500, description="Workspace description")
    is_public: bool = Field(True, description="Whether workspace is publicly visible")


class CreateWorkspaceRequest(WorkspaceBase):
    """Schema for creating a new workspace."""
    
    template_id: Optional[UUID] = Field(None, description="Optional template to initialize workspace from")


class CreateOrphanWorkspaceRequest(BaseModel):
    """Schema for creating an orphan workspace (anonymous users)."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Workspace name")
    description: Optional[str] = Field(None, max_length=500, description="Workspace description")


class UpdateWorkspaceRequest(BaseModel):
    """Schema for updating workspace metadata."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Workspace name")
    description: Optional[str] = Field(None, max_length=500, description="Workspace description")


class ClaimWorkspaceRequest(BaseModel):
    """Schema for claiming an orphan workspace."""
    
    session_id: str = Field(..., description="Session ID that created the orphan workspace")


class WorkspaceVisibilityRequest(BaseModel):
    """Schema for changing workspace visibility."""
    
    is_public: bool = Field(..., description="Whether workspace should be publicly visible")


class ShareWorkspaceRequest(BaseModel):
    """Schema for generating workspace sharing links."""
    
    expires_in_hours: Optional[int] = Field(None, ge=1, le=8760, description="Link expiration in hours (max 1 year)")
    allow_edit: bool = Field(False, description="Whether shared link allows editing")


class WorkspaceFilters(BaseModel):
    """Schema for workspace listing filters."""
    
    search: Optional[str] = Field(None, description="Search in workspace name and description")
    is_public: Optional[bool] = Field(None, description="Filter by visibility")
    is_orphan: Optional[bool] = Field(None, description="Filter by orphan status")
    owner_id: Optional[UUID] = Field(None, description="Filter by owner")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")


class WorkspaceResponse(WorkspaceBase):
    """Schema for workspace responses."""
    
    id: UUID
    owner_id: Optional[UUID] = None
    is_orphan: bool = False
    storage_quota_bytes: int
    settings: dict = {}
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    usage: Optional[WorkspaceUsageSchema] = None
    
    model_config = ConfigDict(from_attributes=True)


class WorkspaceListResponse(BaseModel):
    """Schema for workspace list responses with pagination."""
    
    workspaces: List[WorkspaceResponse]
    total: int
    page: int
    size: int
    has_more: bool


class WorkspaceDetailsResponse(WorkspaceResponse):
    """Schema for detailed workspace responses including audit logs."""
    
    recent_audit_logs: Optional[List[WorkspaceAuditLogSchema]] = None


class ValidateWorkspaceNameRequest(BaseModel):
    """Schema for validating workspace name availability."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Workspace name to validate")


class ValidateWorkspaceNameResponse(BaseModel):
    """Schema for workspace name validation response."""
    
    available: bool
    message: str


class ShareLinkResponse(BaseModel):
    """Schema for workspace sharing link response."""
    
    share_url: str
    expires_at: Optional[datetime] = None
    allow_edit: bool = False


class WorkspaceUsageResponse(BaseModel):
    """Schema for workspace usage statistics."""
    
    workspace_id: UUID
    file_count: int
    storage_used_bytes: int
    storage_quota_bytes: int
    storage_used_percentage: float
    query_count: int
    last_accessed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)