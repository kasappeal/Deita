"""
Workspace-related Pydantic schemas.
"""
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


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
    max_file_size: int | None = None
    max_storage: int | None = None

    class Config:
        from_attributes = True
