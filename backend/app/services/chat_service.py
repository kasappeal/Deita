"""
Chat service for managing chat message persistence and retrieval.
"""
from uuid import UUID

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models import ChatMessage
from app.schemas.chat_message import ChatMessageCreate, ChatMessageResponse


class ChatService:
    """Service for managing chat message operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_message(self, message_create: ChatMessageCreate) -> ChatMessageResponse:
        """Create a new chat message in the database."""
        db_message = ChatMessage(
            workspace_id=message_create.workspace_id,
            user_id=message_create.user_id,
            role=message_create.role,
            content=message_create.content,
            message_metadata=message_create.message_metadata,
            is_sql_query=message_create.is_sql_query,
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return ChatMessageResponse.model_validate(db_message)

    def get_workspace_messages(
        self,
        workspace_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> list[ChatMessageResponse]:
        """Get chat messages for a workspace with pagination."""
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.workspace_id == workspace_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        responses = [ChatMessageResponse.model_validate(msg) for msg in messages]
        responses.reverse()  # Return in chronological order (oldest first)
        return responses

    def get_recent_messages(
        self,
        workspace_id: UUID,
        limit: int = 10
    ) -> list[ChatMessageResponse]:
        """Get recent chat messages for a workspace (most recent first)."""
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.workspace_id == workspace_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
            .all()
        )
        # Return in chronological order (oldest first) for better context building
        return [ChatMessageResponse.model_validate(msg) for msg in reversed(messages)]

    def get_sql_query_history(
        self,
        workspace_id: UUID,
        limit: int = 5
    ) -> list[str]:
        """Get recent SQL queries from chat history."""
        sql_messages = (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.workspace_id == workspace_id,
                ChatMessage.is_sql_query.is_(True),
                ChatMessage.role == "assistant"
            )
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
            .all()
        )

        sql_queries = []
        for msg in sql_messages:
            if msg.message_metadata is not None and "sql_query" in msg.message_metadata:
                sql_queries.append(msg.message_metadata["sql_query"])

        return list(reversed(sql_queries))  # Return in chronological order

    def clear_workspace_messages(self, workspace_id: UUID) -> int:
        """Clear all chat messages for a workspace. Returns count of deleted messages."""
        deleted_count = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.workspace_id == workspace_id)
            .delete()
        )
        self.db.commit()
        return deleted_count

    def get_message_count(self, workspace_id: UUID) -> int:
        """Get total count of messages in a workspace."""
        return (
            self.db.query(func.count(ChatMessage.id))
            .filter(ChatMessage.workspace_id == workspace_id)
            .scalar()
        ) or 0
