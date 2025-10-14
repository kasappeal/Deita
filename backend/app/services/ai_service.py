import json
from collections.abc import Iterator
from os import environ
from uuid import UUID

from litellm import completion
from sqlalchemy.orm import Session

from app.schemas.chat_message import ChatMemoryContext, ChatMessageCreate
from app.schemas.file import File
from app.services.chat_service import ChatService


class AIService:

    def __init__(self, api_key: str, model: str, chat_service: ChatService | None = None, db: Session | None = None):
        self.api_key = api_key
        if not model.startswith('openrouter/'):
            model = f'openrouter/{model}'
        self.model = model
        self.db = db

        # If chat_service is provided, use it. Otherwise, create one from db if available
        if chat_service is not None:
            self.chat_service = chat_service
        elif db is not None:
            self.chat_service = ChatService(db)
        else:
            self.chat_service = None

    def _setup_environment(self):
        environ["OPENROUTER_API_KEY"] = self.api_key

    def stream_answer(self, prompt: str) -> Iterator[str]:
        response = []
        for chunk in response:
            if 'choices' in chunk and len(chunk['choices']) > 0:
                delta = chunk['choices'][0]['delta']
                if 'content' in delta:
                    yield delta['content']  # type: ignore

    def build_system_prompt(self, content: str) -> dict:
        return {"role": "system", "content": content}

    def build_user_prompt(self, content: str) -> dict:
        return {"role": "user", "content": content}

    @staticmethod
    def generate_db_description(files: list[File]) -> str:
        descriptions = ['Database is composed of the following tables:', '']
        for file in files:
            columns = file.csv_metadata.get("headers") if file.csv_metadata else []
            columns_description = f' and columns: {", ".join(columns)}' if columns else ''
            descriptions.append(
                f'- Table "{file.table_name}" with {file.row_count} rows{columns_description}.'
            )
        return "\n".join(descriptions)

    def store_chat_message(
        self,
        workspace_id: UUID,
        role: str,
        content: str,
        user_id: int | None = None,
        message_metadata: dict | None = None,
        is_sql_query: bool = False
    ) -> None:
        """Store a chat message in the database."""
        if not self.chat_service:
            return

        message_create = ChatMessageCreate(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
            content=content,
            message_metadata=message_metadata,
            is_sql_query=is_sql_query
        )
        self.chat_service.create_message(message_create)

    def get_chat_memory(
        self,
        workspace_id: UUID,
        user_id: int | None = None
    ) -> ChatMemoryContext | None:
        """Get chat memory context for a workspace."""
        if not self.chat_service:
            return None

        return self.chat_service.build_memory_context(workspace_id, user_id)

    def build_memory_context_string(
        self,
        memory_context: ChatMemoryContext | None
    ) -> str:
        """Build a string representation of chat memory for AI prompts."""
        if not memory_context:
            return ""

        # Check if context is empty
        if (not memory_context.recent_messages and
            not memory_context.sql_query_history and
            not memory_context.user_context):
            return ""

        context_parts = []

        # Add user context if available
        if memory_context.user_context:
            context_parts.append("<user_context>")
            context_parts.append(memory_context.user_context)
            context_parts.append("</user_context>")

        # Add recent conversation history
        if memory_context.recent_messages:
            context_parts.append("<conversation_history>")
            for msg in memory_context.recent_messages:
                context_parts.append(f"{msg.role}: {msg.content}")
            context_parts.append("</conversation_history>")

        # Add SQL query history
        if memory_context.sql_query_history:
            context_parts.append("<previous_sql_queries>")
            for query in memory_context.sql_query_history:
                context_parts.append(f"- {query}")
            context_parts.append("</previous_sql_queries>")

        return "\n\n".join(context_parts)

    def build_natural_language_based_sql_prompt(
        self,
        user_input: str,
        files: list[File],
        workspace_id: UUID | None = None,
        user_id: int | None = None
    ) -> str:
        db_description = self.generate_db_description(files)
        print(db_description)

        # Get chat memory context if workspace_id is provided
        memory_context_str = ""
        if workspace_id and self.chat_service:
            memory_context = self.chat_service.build_memory_context(workspace_id, user_id)
            memory_context_str = self.build_memory_context_string(memory_context)

        prompt = f"""
            You must strictly follow the instructions below. Deviations will result in a penalty to your confidence score.

            MANDATORY RULES:
            - Always explain if you cannot fully follow the instructions.
            - Always reduce the confidence score if instructions cannot be fully applied.
            - Provide a confidence score between 0 and 100.
            - Provide a detailed explanation in the "answer" field. Talk directly to the user. Use a simple, clear and funny language.
            - Use same language as the user for the answer. This is very important to offer a great user experience.
            - Respond ONLY in strict JSON format, without extra text.
            - Give a good format to the SQL query for better readability.

            Your output JSON MUST contain all fields, even if empty (e.g., "tables_used": []).

            ---

            Now analyze the user query based on the provided inputs:

            <database_description>
            {db_description}
            </database_description>

            <memory_context>
            {memory_context_str}
            </memory_context>

            <user_input>
            {user_input}
            </user_input>

            ---

            Your task:

            - Analyze and understand the user input, considering the database schema and memory context.
            - Analyze the query's translatability into SQL according to the instructions.
            - Apply the instructions explicitly.
            - If you CANNOT apply instructions in the SQL, explain why under "instructions_comments", "explanation" and reduce your confidence.
            - Penalize confidence appropriately if any part of the instructions is unmet.
            - When there several tables that can be used to answer the question, you can combine them in a single SQL query.
            - NEVER assume general/company-wide interpretations for personal pronouns when NO user context is available.

            Provide your output ONLY in the following JSON structure:

            {{
                "is_sql_translatable": true or false,
                "answer": ("Detailed explanation why the query can or cannot be "
                               "translated, mentioning instructions explicitly and "
                               "referencing conversation history if relevant"),
                "sql_query": ("High-level SQL query for DuckDB engine (you must to applying instructions "
                             "and use previous answers if the question is a continuation)"),
                "tables_used": ["list", "of", "tables", "used", "in", "the", "query",
                               "with", "the", "relationships", "between", "them"],
                "confidence": integer between 0 and 100
            }}

            Evaluation Guidelines:

            1. Verify if all requested information exists in the schema.
            2. Check if the query's intent is clear enough for SQL translation.
            3. Identify any ambiguities in the query or instructions.
            4. List missing information explicitly if applicable.
            5. When critical information is missing make the is_sql_translatable false and add it to missing_information.
            6. Confirm if necessary joins are possible.
            7. If similar query have been failed before, learn the error and try to avoid it.
            8. Consider if complex calculations are feasible in SQL.
            9. Identify multiple interpretations if they exist.
            10. If the question is a follow-up, resolve references using the
               conversation history and previous answers.
            11. Use memory context to provide more personalized and informed SQL generation.
            12. Learn from successful query patterns in memory context and avoid failed approaches.
            13. For personal queries, FIRST check memory context for user identification. If user identity is found in memory context (user name, previous personal queries, etc.), the query IS translatable.
            14. CRITICAL PERSONALIZATION CHECK: If missing user identification/personalization is a significant or primary component of the query (e.g., "show my orders", "my account balance", "my recent purchases", "how many employees I have", "products I own") AND no user identification is available in memory context or schema, set "is_sql_translatable" to false. However, if memory context contains user identification (like user name or previous successful personal queries), then personal queries ARE translatable even if they are the primary component of the query.

            Again: OUTPUT ONLY VALID JSON. No explanations outside the JSON block. """  # pylint: disable=line-too-long
        return prompt

    def generate_natural_language_based_sql(
        self,
        prompt: str,
        files: list[File],
        workspace_id: UUID | None = None,
        user_id: int | None = None,
        store_messages: bool = True
    ) -> dict:
        self._setup_environment()

        # Store user message if chat service is available and storage is enabled
        if store_messages and workspace_id and self.chat_service:
            self.store_chat_message(
                workspace_id=workspace_id,
                role="user",
                content=prompt,
                user_id=user_id,
                is_sql_query=False
            )

        prompt_with_memory = self.build_natural_language_based_sql_prompt(
            prompt, files, workspace_id, user_id
        )
        response = completion(model=self.model, messages=[self.build_system_prompt(prompt_with_memory)])

        if len(response['choices']) > 0:  # type: ignore
            choice = response['choices'][0]  # type: ignore
            try:
                content = choice['message']['content']
                result = json.loads(content)  # type: ignore

                # Store assistant response if chat service is available and storage is enabled
                if store_messages and workspace_id and self.chat_service:
                    metadata = {
                        "sql_query": result.get("sql_query", ""),
                        "confidence": result.get("confidence", 0),
                        "is_sql_translatable": result.get("is_sql_translatable", False),
                        "tables_used": result.get("tables_used", [])
                    }
                    self.store_chat_message(
                        workspace_id=workspace_id,
                        role="assistant",
                        content=result.get("answer", ""),
                        user_id=user_id,
                        message_metadata=metadata,
                        is_sql_query=result.get("is_sql_translatable", False)
                    )

                return result
            except json.JSONDecodeError:
                # logger.critical("Failed to parse JSON from LLM response: %s", choice['message']['content'])
                pass

        return {}
