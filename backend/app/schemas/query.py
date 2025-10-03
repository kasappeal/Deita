"""
Query schema definitions.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


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
    workspace_id: UUID
    name: str
    query: str
    ai_generated: bool
    created_at: datetime

    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to map sql_text to query."""
        if hasattr(obj, 'sql_text'):
            # Create a dict from the object with sql_text mapped to query
            data = {
                'id': obj.id,
                'workspace_id': obj.workspace_id,
                'name': obj.name,
                'query': obj.sql_text,
                'ai_generated': obj.ai_generated,
                'created_at': obj.created_at
            }
            return super().model_validate(data, **kwargs)
        return super().model_validate(obj, **kwargs)

    class Config:
        from_attributes = True



