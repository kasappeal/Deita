"""
Chat message model for storing conversation history in workspaces.
"""
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class ChatMessage(Base):
    """Chat message model for storing conversation history in workspaces."""

    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    role = Column(String, nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    message_metadata = Column(
        JSONB,
        nullable=True
    )  # JSONB for additional data like SQL queries, confidence scores, etc.
    is_sql_query = Column(Boolean, default=False)  # Flag to identify SQL-related messages
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    workspace = relationship("Workspace", back_populates="chat_messages")
    user = relationship("User", back_populates="chat_messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, workspace_id={self.workspace_id}, role='{self.role}')>"
