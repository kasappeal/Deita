"""
Query schema definitions.
"""
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
