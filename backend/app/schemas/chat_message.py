"""Pydantic schemas for chat message operations."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class ChatMessageBase(BaseModel):
    """Base schema for chat messages."""
    content: str
    role: str  # 'user' or 'assistant'
    message_metadata: dict | None = None
    is_sql_query: bool = False


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating new chat messages."""
    workspace_id: uuid.UUID
    user_id: int | None = None


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message responses."""
    workspace_id: uuid.UUID
    user_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMemoryContext(BaseModel):
    """Schema for chat memory context used in AI prompts."""
    recent_messages: list[ChatMessageResponse]
    user_context: str | None = None
    sql_query_history: list[str] = []
