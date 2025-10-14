"""
Tests for AI service chat memory functionality.
"""
import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.chat_message import ChatMemoryContext, ChatMessageResponse
from app.schemas.file import File
from app.services.ai_service import AIService


class TestAIServiceChatMemory:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.db = MagicMock()
        self.ai_service = AIService(
            api_key="test-key",
            model="test-model",
            db=self.db
        )
        # Mock the chat service
        self.ai_service.chat_service = MagicMock()
        self.workspace_id = uuid.uuid4()
        self.user_id = 1

    def test_ai_service_initialization_with_db(self):
        """Test AI service initialization with database session."""
        assert self.ai_service.db == self.db
        assert self.ai_service.chat_service is not None

    def test_ai_service_initialization_without_db(self):
        """Test AI service initialization without database session."""
        ai_service = AIService(api_key="test-key", model="test-model")
        assert ai_service.db is None
        assert ai_service.chat_service is None

    def test_store_chat_message_with_chat_service(self):
        """Test storing a chat message when chat service is available."""
        # Mock the chat service create_message method
        self.ai_service.chat_service.create_message = MagicMock()

        self.ai_service.store_chat_message(
            workspace_id=self.workspace_id,
            role="user",
            content="Show me the top customers",
            user_id=self.user_id,
            is_sql_query=False
        )

        # Verify the chat service was called
        self.ai_service.chat_service.create_message.assert_called_once()
        call_args = self.ai_service.chat_service.create_message.call_args[0][0]
        assert call_args.workspace_id == self.workspace_id
        assert call_args.role == "user"
        assert call_args.content == "Show me the top customers"

    def test_store_chat_message_without_chat_service(self):
        """Test storing a chat message when chat service is not available."""
        ai_service = AIService(api_key="test-key", model="test-model")  # No DB

        # Should not raise an error, just return without doing anything
        ai_service.store_chat_message(
            workspace_id=self.workspace_id,
            role="user",
            content="Show me the top customers"
        )

    def test_get_chat_memory_with_chat_service(self):
        """Test getting chat memory when chat service is available."""
        # Setup mock memory context
        mock_memory = ChatMemoryContext(
            recent_messages=[],
            sql_query_history=[],
            user_context="User: Test User"
        )

        self.ai_service.chat_service.build_memory_context = MagicMock(return_value=mock_memory)

        result = self.ai_service.get_chat_memory(self.workspace_id, self.user_id)

        assert result == mock_memory
        self.ai_service.chat_service.build_memory_context.assert_called_once_with(
            self.workspace_id, self.user_id
        )

    def test_get_chat_memory_without_chat_service(self):
        """Test getting chat memory when chat service is not available."""
        ai_service = AIService(api_key="test-key", model="test-model")  # No DB

        result = ai_service.get_chat_memory(self.workspace_id, self.user_id)

        assert result is None

    def test_build_memory_context_string_with_context(self):
        """Test building memory context string with full context."""
        # Setup mock memory context with messages
        mock_message = ChatMessageResponse(
            id=uuid.uuid4(),
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            role="user",
            content="Show me the customers",
            message_metadata=None,
            is_sql_query=False,
            created_at="2023-10-13T10:00:00Z"  # type: ignore
        )

        memory_context = ChatMemoryContext(
            recent_messages=[mock_message],
            sql_query_history=["SELECT * FROM customers LIMIT 10"],
            user_context="User: Test User"
        )

        result = self.ai_service.build_memory_context_string(memory_context)

        # Verify all sections are included
        assert "<user_context>" in result
        assert "User: Test User" in result
        assert "<conversation_history>" in result
        assert "user: Show me the customers" in result
        assert "<previous_sql_queries>" in result
        assert "- SELECT * FROM customers LIMIT 10" in result

    def test_build_memory_context_string_empty(self):
        """Test building memory context string with empty context."""
        memory_context = ChatMemoryContext(
            recent_messages=[],
            sql_query_history=[],
            user_context=None
        )

        result = self.ai_service.build_memory_context_string(memory_context)

        assert result == ""

    def test_build_memory_context_string_none(self):
        """Test building memory context string with None context."""
        result = self.ai_service.build_memory_context_string(None)

        assert result == ""

    @patch('app.services.ai_service.completion')
    def test_generate_natural_language_based_sql_with_memory(self, mock_completion):
        """Test SQL generation with chat memory integration."""
        # Setup mock LLM response
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "is_sql_translatable": True,
                        "answer": "Here are the top customers based on our data",
                        "sql_query": "SELECT * FROM customers ORDER BY total DESC LIMIT 10",
                        "tables_used": ["customers"],
                        "confidence": 95
                    })
                }
            }]
        }
        mock_completion.return_value = mock_response

        # Setup mock chat service
        mock_memory = ChatMemoryContext(
            recent_messages=[],
            sql_query_history=["SELECT * FROM sales"],
            user_context="User: Test User"
        )
        self.ai_service.chat_service.build_memory_context = MagicMock(return_value=mock_memory)
        self.ai_service.chat_service.create_message = MagicMock()

        # Setup files
        files = [File(
            id=uuid.uuid4(),
            filename="customers.csv",
            size=1024,
            table_name="customers",
            row_count=100,
            csv_metadata={"headers": ["id", "name", "total"]},
            uploaded_at="2023-10-13T10:00:00Z"  # type: ignore
        )]

        # Execute
        result = self.ai_service.generate_natural_language_based_sql(
            prompt="Show me the top customers",
            files=files,
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            store_messages=True
        )

        # Verify
        assert result["is_sql_translatable"] is True
        assert result["confidence"] == 95

        # Verify chat messages were stored (user message + assistant response)
        assert self.ai_service.chat_service.create_message.call_count == 2

    @patch('app.services.ai_service.completion')
    def test_generate_natural_language_based_sql_without_storage(self, mock_completion):
        """Test SQL generation without storing chat messages."""
        # Setup mock LLM response
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "is_sql_translatable": True,
                        "answer": "Query result",
                        "sql_query": "SELECT * FROM customers",
                        "tables_used": ["customers"],
                        "confidence": 90
                    })
                }
            }]
        }
        mock_completion.return_value = mock_response

        # Setup mock chat service
        mock_memory = ChatMemoryContext(
            recent_messages=[],
            sql_query_history=[],
            user_context=None
        )
        self.ai_service.chat_service.build_memory_context = MagicMock(return_value=mock_memory)
        self.ai_service.chat_service.create_message = MagicMock()

        # Setup files
        files = [File(
            id=uuid.uuid4(),
            filename="customers.csv",
            size=1024,
            table_name="customers",
            row_count=100,
            csv_metadata={"headers": ["id", "name"]},
            uploaded_at="2023-10-13T10:00:00Z"  # type: ignore
        )]

        # Execute with storage disabled
        result = self.ai_service.generate_natural_language_based_sql(
            prompt="Show me customers",
            files=files,
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            store_messages=False
        )

        # Verify result but no messages stored
        assert result["is_sql_translatable"] is True
        self.ai_service.chat_service.create_message.assert_not_called()

    @patch('app.services.ai_service.completion')
    def test_generate_natural_language_based_sql_json_decode_error(self, mock_completion):
        """Test handling of JSON decode error from LLM response."""
        # Setup mock LLM response with invalid JSON
        mock_response = {
            "choices": [{
                "message": {
                    "content": "invalid json response"
                }
            }]
        }
        mock_completion.return_value = mock_response

        files = [File(
            id=uuid.uuid4(),
            filename="test.csv",
            size=512,
            table_name="test",
            row_count=10,
            csv_metadata={},
            uploaded_at="2023-10-13T10:00:00Z"  # type: ignore
        )]

        # Execute
        result = self.ai_service.generate_natural_language_based_sql(
            prompt="test query",
            files=files
        )

        # Should return empty dict on JSON decode error
        assert result == {}

    def test_build_natural_language_based_sql_prompt_with_memory(self):
        """Test prompt building includes memory context."""
        # Setup mock memory
        mock_memory = ChatMemoryContext(
            recent_messages=[],
            sql_query_history=["SELECT * FROM customers"],
            user_context="User: Test User"
        )
        # Mock the build_memory_context method on chat_service
        self.ai_service.chat_service.build_memory_context = MagicMock(return_value=mock_memory)

        files = [File(
            id=uuid.uuid4(),
            filename="test.csv",
            size=512,
            table_name="test",
            row_count=10,
            csv_metadata={"headers": ["id", "name"]},
            uploaded_at="2023-10-13T10:00:00Z"  # type: ignore
        )]

        # Execute
        prompt = self.ai_service.build_natural_language_based_sql_prompt(
            user_input="Show me data",
            files=files,
            workspace_id=self.workspace_id,
            user_id=self.user_id
        )

        # Verify memory context is included
        assert "<user_context>" in prompt
        assert "User: Test User" in prompt
        assert "previous_sql_queries" in prompt

    def test_build_natural_language_based_sql_prompt_without_workspace(self):
        """Test prompt building without workspace_id (no memory)."""
        files = [File(
            id=uuid.uuid4(),
            filename="test.csv",
            size=512,
            table_name="test",
            row_count=10,
            csv_metadata={"headers": ["id"]},
            uploaded_at="2023-10-13T10:00:00Z"  # type: ignore
        )]

        # Execute without workspace_id
        prompt = self.ai_service.build_natural_language_based_sql_prompt(
            user_input="Show me data",
            files=files
        )

        # Verify no memory context is included
        assert "<user_context>" not in prompt
        assert "<conversation_history>" not in prompt
        assert "<database_description>" in prompt  # But database description should still be there
