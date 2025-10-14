"""
Tests for chat service functionality.
"""
import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.models import ChatMessage, User
from app.schemas.chat_message import (
    ChatMemoryContext,
    ChatMessageCreate,
    ChatMessageResponse,
)
from app.services.chat_service import ChatService


class TestChatService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.db = MagicMock()
        self.chat_service = ChatService(self.db)

        # Mock objects
        self.workspace_id = uuid.uuid4()
        self.user_id = 1
        self.message_id = uuid.uuid4()

        # Sample chat message
        self.sample_message = ChatMessage(
            id=self.message_id,
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            role="user",
            content="Show me the top 10 customers",
            message_metadata=None,
            is_sql_query=False,
            created_at=datetime.now(UTC)
        )

    def test_create_message(self):
        """Test creating a new chat message."""
        # Setup
        message_create = ChatMessageCreate(
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            role="user",
            content="Show me the top 10 customers",
            message_metadata=None,
            is_sql_query=False
        )

        self.db.add = MagicMock()
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()

        def refresh_side_effect(obj):
            # Simulate the database setting the ID and timestamp
            obj.id = self.message_id
            obj.created_at = datetime.now(UTC)

        self.db.refresh.side_effect = refresh_side_effect

        # Execute
        result = self.chat_service.create_message(message_create)

        # Verify
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()

        assert isinstance(result, ChatMessageResponse)
        assert result.role == "user"
        assert result.content == "Show me the top 10 customers"

    def test_get_workspace_messages(self):
        """Test retrieving workspace messages with pagination."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_order = MagicMock()
        mock_limit = MagicMock()
        mock_offset = MagicMock()

        self.db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        mock_order.limit.return_value = mock_limit
        mock_limit.offset.return_value = mock_offset
        mock_offset.all.return_value = [self.sample_message]

        # Execute
        result = self.chat_service.get_workspace_messages(self.workspace_id, limit=10, offset=0)

        # Verify
        self.db.query.assert_called_once_with(ChatMessage)
        mock_query.filter.assert_called_once()
        mock_filter.order_by.assert_called_once()
        mock_order.limit.assert_called_once_with(10)
        mock_limit.offset.assert_called_once_with(0)

        assert len(result) == 1
        assert isinstance(result[0], ChatMessageResponse)

    def test_get_recent_messages(self):
        """Test retrieving recent messages in chronological order."""
        # Setup
        messages = [self.sample_message]

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_order = MagicMock()
        mock_limit = MagicMock()

        self.db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        mock_order.limit.return_value = mock_limit
        mock_limit.all.return_value = messages

        # Execute
        result = self.chat_service.get_recent_messages(self.workspace_id, limit=5)

        # Verify
        mock_order.limit.assert_called_once_with(5)
        assert len(result) == 1

    def test_get_sql_query_history(self):
        """Test retrieving SQL query history from chat messages."""
        # Setup
        sql_metadata = {
            "sql_query": "SELECT * FROM customers ORDER BY total DESC LIMIT 10",
            "confidence": 95,
            "is_sql_translatable": True
        }

        sql_message = ChatMessage(
            id=uuid.uuid4(),
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            role="assistant",
            content="Here are the top 10 customers",
            message_metadata=sql_metadata,  # Pass dict, not JSON string
            is_sql_query=True,
            created_at=datetime.now(UTC)
        )

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_order = MagicMock()
        mock_limit = MagicMock()

        self.db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        mock_order.limit.return_value = mock_limit
        mock_limit.all.return_value = [sql_message]

        # Execute
        result = self.chat_service.get_sql_query_history(self.workspace_id, limit=3)

        # Verify
        assert len(result) == 1
        assert result[0] == "SELECT * FROM customers ORDER BY total DESC LIMIT 10"

    def test_get_sql_query_history_invalid_json(self):
        """Test SQL query history with metadata without sql_query key."""
        # Setup
        sql_message = ChatMessage(
            id=uuid.uuid4(),
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            role="assistant",
            content="Response",
            message_metadata={"other_key": "value"},  # Dict without sql_query key
            is_sql_query=True,
            created_at=datetime.now(UTC)
        )

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_order = MagicMock()
        mock_limit = MagicMock()

        self.db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        mock_order.limit.return_value = mock_limit
        mock_limit.all.return_value = [sql_message]

        # Execute
        result = self.chat_service.get_sql_query_history(self.workspace_id, limit=3)

        # Verify - should return empty list since metadata doesn't have sql_query key
        assert len(result) == 0

    def test_build_memory_context_with_user(self):
        """Test building memory context with user information."""
        # Setup
        mock_user = User(id=self.user_id, email="test@example.com", full_name="Test User")

        # Mock recent messages query
        mock_messages_query = MagicMock()
        mock_messages_filter = MagicMock()
        mock_messages_order = MagicMock()
        mock_messages_limit = MagicMock()

        # Mock SQL query history
        mock_sql_query = MagicMock()
        mock_sql_filter = MagicMock()
        mock_sql_order = MagicMock()
        mock_sql_limit = MagicMock()

        # Mock user query
        mock_user_query = MagicMock()
        mock_user_filter = MagicMock()

        def query_side_effect(model):
            if model == ChatMessage:
                return mock_messages_query
            elif model == User:
                return mock_user_query
            return MagicMock()

        self.db.query.side_effect = query_side_effect

        # Setup message query chain
        mock_messages_query.filter.return_value = mock_messages_filter
        mock_messages_filter.order_by.return_value = mock_messages_order
        mock_messages_order.limit.return_value = mock_messages_limit
        mock_messages_limit.all.return_value = [self.sample_message]

        # Setup SQL query chain
        mock_sql_query.filter.return_value = mock_sql_filter
        mock_sql_filter.order_by.return_value = mock_sql_order
        mock_sql_order.limit.return_value = mock_sql_limit
        mock_sql_limit.all.return_value = []

        # Setup user query
        mock_user_query.filter.return_value = mock_user_filter
        mock_user_filter.first.return_value = mock_user

        # Execute
        result = self.chat_service.build_memory_context(self.workspace_id, self.user_id)

        # Verify
        assert isinstance(result, ChatMemoryContext)
        assert len(result.recent_messages) == 1
        assert result.user_context == "User: Test User"
        assert len(result.sql_query_history) == 0

    def test_build_memory_context_without_user(self):
        """Test building memory context without user information."""
        # Setup mocks similar to previous test but without user
        mock_messages_query = MagicMock()
        mock_messages_filter = MagicMock()
        mock_messages_order = MagicMock()
        mock_messages_limit = MagicMock()

        mock_sql_query = MagicMock()
        mock_sql_filter = MagicMock()
        mock_sql_order = MagicMock()
        mock_sql_limit = MagicMock()

        def query_side_effect(model):
            if model == ChatMessage:
                return mock_messages_query
            return MagicMock()

        self.db.query.side_effect = query_side_effect

        mock_messages_query.filter.return_value = mock_messages_filter
        mock_messages_filter.order_by.return_value = mock_messages_order
        mock_messages_order.limit.return_value = mock_messages_limit
        mock_messages_limit.all.return_value = []

        mock_sql_query.filter.return_value = mock_sql_filter
        mock_sql_filter.order_by.return_value = mock_sql_order
        mock_sql_order.limit.return_value = mock_sql_limit
        mock_sql_limit.all.return_value = []

        # Execute
        result = self.chat_service.build_memory_context(self.workspace_id)

        # Verify
        assert isinstance(result, ChatMemoryContext)
        assert len(result.recent_messages) == 0
        assert result.user_context is None
        assert len(result.sql_query_history) == 0

    def test_clear_workspace_messages(self):
        """Test clearing all messages for a workspace."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.delete.return_value = 5  # 5 messages deleted

        # Execute
        result = self.chat_service.clear_workspace_messages(self.workspace_id)

        # Verify
        self.db.query.assert_called_with(ChatMessage)
        mock_query.filter.assert_called_once()
        mock_filter.delete.assert_called_once()
        self.db.commit.assert_called_once()
        assert result == 5

    def test_get_message_count(self):
        """Test getting message count for a workspace."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.scalar.return_value = 10

        # Execute
        result = self.chat_service.get_message_count(self.workspace_id)

        # Verify
        mock_filter.scalar.assert_called_once()
        assert result == 10

    def test_get_message_count_none_result(self):
        """Test getting message count when result is None."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.scalar.return_value = None

        # Execute
        result = self.chat_service.get_message_count(self.workspace_id)

        # Verify
        assert result == 0
