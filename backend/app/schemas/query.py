"""
Query schema definitions.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Schema for SQL query request."""
    query: str


class QueryResult(BaseModel):
    """Schema for SQL query result."""
    columns: list[str]
    rows: list[list]
    time: float
    has_more: bool = False


class SaveQueryRequest(BaseModel):
    """Schema for saving a query."""
    name: str
    query: str


class SavedQuery(BaseModel):
    """Schema for a saved query response."""
    id: UUID
    name: str
    query: str
    created_at: datetime

    class Config:
        from_attributes = True
