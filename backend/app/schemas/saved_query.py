"""
SavedQuery schema definitions.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SaveQueryCreate(BaseModel):
    """Schema for creating a saved query."""
    name: str = Field(..., min_length=1, max_length=255)
    query: str = Field(..., min_length=1)


class SavedQuery(BaseModel):
    """Schema for saved query response."""
    id: uuid.UUID
    name: str
    query: str
    created_at: datetime

    class Config:
        from_attributes = True
