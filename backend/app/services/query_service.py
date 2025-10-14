"""
Query service for validating and executing SQL queries.
"""

import signal
import time

import duckdb
from sqlalchemy.orm import Session
from sqlglot import ParseError, TokenError, parse_one, to_table
from sqlglot.expressions import (
    Alter,
    Analyze,
    Attach,
    Cache,
    Clone,
    Cluster,
    Comment,
    Commit,
    Create,
    Delete,
    Describe,
    Detach,
    Drop,
    Export,
    Expression,
    Grant,
    Insert,
    Kill,
    Lock,
    Merge,
    Pragma,
    Replace,
    Revoke,
    Rollback,
    Set,
    Show,
    Table,
    Transaction,
    TruncateTable,
    Uncache,
    Update,
    Use,
)
from sqlglot.optimizer.scope import build_scope

from app.core.config import Settings
from app.models import User, Workspace
from app.models.file import File
from app.models.query import Query
from app.schemas.query import QueryResult, SavedQuery
from app.services.exceptions import (
    BadQuery,
    DisallowedQuery,
    QueryNotFound,
    QueryTimeout,
    WorkspaceForbidden,
)


class QueryService:
    """Service for handling SQL queries with validation and execution."""

    DISALLOWED_EXPRESSIONS = {
        Insert, Update, Delete, Merge, Create, Drop, Alter, TruncateTable, Clone, Analyze,
        Commit, Rollback, Transaction, Grant, Revoke, Export, Cache, Uncache, Kill, Pragma,
        Describe, Show, Use, Set, Lock, Comment, Cluster, Detach, Attach, Replace
    }

    def __init__(self, settings: Settings, db: Session | None = None):
        self.settings = settings
        self.db = db

    def _add_limit(self, expr: Expression, page: int = 1, size: int | None = None) -> Expression:
        """Add a LIMIT 50 to the query if not already present."""
        return expr.limit(size + 1).offset((page - 1) * size) # type: ignore

    def _get_all_expression_items(self, expression: Expression) -> list[Expression]:
        # https://github.com/tobymao/sqlglot/blob/main/posts/ast_primer.md#scope
        root = build_scope(expression)
        if root is None:
            raise BadQuery("Unable to build scope for the query.")
        return [
            source
            for scope in root.traverse()
            for _, (_, source) in scope.selected_sources.items()
        ]

    def _get_read_csv_calls_for_file(self, file: File) -> str:
        call = f"read_csv('s3://{self.settings.s3_bucket_name}/{file.storage_path}'"
        if file.csv_metadata.get('delimiter'):
            call += f", delim='{file.csv_metadata['delimiter']}'"
        if file.csv_metadata.get('quotechar'):
            call += f", quote='{file.csv_metadata['quotechar']}'"
        call += ")"
        return call

    def _validate_query_and_map_tables(self, expression: Expression, files: list[File]) -> Expression:
        tables_map = {
            file.table_name: file for file in files # type: ignore
        }
        for item in self._get_all_expression_items(expression):
            if type(item) in self.DISALLOWED_EXPRESSIONS:
                raise DisallowedQuery(f"Disallowed expression: {type(item).__name__}")
            if isinstance(item, Table):
                table_name = item.name
                if table_name not in tables_map:
                    raise BadQuery(f"Table '{table_name}' does not exist in the workspace.")
                matching_file = tables_map[table_name] # type: ignore
                renamed_table = to_table(self._get_read_csv_calls_for_file(matching_file))
                renamed_table.set("alias", item.alias or table_name) # preserve alias if exists
                item.replace(renamed_table)
        return expression

    def _setup_s3(self, con: duckdb.DuckDBPyConnection):
        endpoint = self.settings.s3_endpoint.replace('https://', '').replace('http://', '')
        sql = f"""INSTALL cache_httpfs from community;
        LOAD cache_httpfs;
        CREATE SECRET s3 (
            TYPE s3,
            KEY_ID '{self.settings.s3_access_key}',
            SECRET '{self.settings.s3_secret_key}',
            ENDPOINT '{endpoint}'
        )"""
        con.sql(sql)

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        con = duckdb.connect()
        self._setup_s3(con)
        return con

    def _execute_ducbkdb(self, sql: str, timeout: int | None = None) -> dict:
        if timeout is not None:
            def timeout_handler(signum, frame):
                raise QueryTimeout("Query timeout")  # noqa: F821
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        try:
            con = self._get_connection()
            result = con.sql(sql)
            res = {
                'columns': result.columns,
                'rows': result.fetchall()
            }
            con.close()
            return res
        except Exception as e:
            raise e
        finally:
            if timeout is not None:
                signal.alarm(0)

    def validate_query(self, query: str, files: list[File]) -> None:
        """
        Validate SQL query without executing it.

        Raises:
            BadQuery: If the query is invalid or references non-existent tables
            DisallowedQuery: If the query contains disallowed expressions
        """
        if files is None:
            files = []
        try:
            expression = parse_one(query)
            self._validate_query_and_map_tables(expression, files)
        except (ParseError, TokenError) as e:
            raise BadQuery(f"Invalid SQL query: {str(e)}") from e

    def list_queries(
        self,
        workspace: Workspace,
        current_user: User | None,
    ) -> list[SavedQuery]:
        """
        List all saved queries in a workspace.

        Permission rules:
        - If workspace is public and has no owner (orphan), any user can retrieve queries
        - If workspace is private, only the owner can retrieve queries

        Args:
            workspace: The workspace to list queries from
            current_user: Current authenticated user (can be None)

        Returns:
            list[SavedQuery]: List of saved queries in the workspace

        Raises:
            WorkspaceForbidden: If user is not authorized to view queries
        """
        # Check permissions based on workspace visibility and ownership
        if workspace.is_public and workspace.is_orphaned:
            # Public orphan workspace: anyone can retrieve queries
            pass
        elif workspace.is_private:
            # Private workspace: only owner can retrieve queries
            if not current_user or workspace.owner_id != current_user.id:
                raise WorkspaceForbidden("Not authorized to view queries in this workspace")
        else:
            # Public workspace with owner: anyone can retrieve queries (it's public)
            pass

        # Get all queries for the workspace
        queries = self.db.query(Query).filter(Query.workspace_id == workspace.id).all()

        # Convert to SavedQuery schema
        return [
            SavedQuery(
                id=query.id,
                name=query.name,
                query=query.sql_text,
                created_at=query.created_at,
            )
            for query in queries
        ]

    def save_query(
        self,
        workspace: Workspace,
        name: str,
        query_text: str,
        files: list[File],
        current_user: User | None,
    ) -> SavedQuery:
        """
        Save a SQL query in a workspace.

        Permission rules:
        - If workspace is public and has no owner (orphan), any user can save queries
        - If workspace is private, only the owner can save queries
        - If workspace is public with owner, only the owner can save queries

        Args:
            workspace: The workspace to save the query in
            name: Name of the query
            query_text: SQL query text
            files: List of files in the workspace for validation
            current_user: Current authenticated user (can be None)

        Returns:
            SavedQuery: The saved query with id, name, query, and created_at

        Raises:
            WorkspaceForbidden: If user is not authorized to save queries
            BadQuery: If the query is invalid
            DisallowedQuery: If the query contains disallowed expressions
        """
        # Check permissions based on workspace visibility and ownership
        if workspace.is_public and workspace.is_orphaned:
            # Public orphan workspace: anyone can save queries
            pass
        elif workspace.is_private:
            # Private workspace: only owner can save queries
            if not current_user or workspace.owner_id != current_user.id: # type: ignore
                raise WorkspaceForbidden("Not authorized to save queries in this workspace")
        else:
            # Public workspace with owner: only owner can save queries
            if not current_user or workspace.owner_id != current_user.id: # type: ignore
                raise WorkspaceForbidden("Not authorized to save queries in this workspace")

        # Validate the query
        self.validate_query(query_text, files)

        # Create and save the query
        query = Query(
            workspace_id=workspace.id,
            name=name,
            sql_text=query_text,
        )
        self.db.add(query)
        self.db.commit()
        self.db.refresh(query)

        # Return the saved query
        return SavedQuery(
            id=query.id,
            name=query.name,
            query=query.sql_text,
            created_at=query.created_at,
        )

    def delete_query(
        self,
        workspace: Workspace,
        query_id,
        current_user: User | None,
    ) -> None:
        """
        Delete a SQL query from a workspace.

        Permission rules:
        - If workspace is public and has no owner (orphan), any user can delete queries
        - If workspace is private, only the owner can delete queries

        Args:
            workspace: The workspace containing the query
            query_id: UUID of the query to delete
            current_user: Current authenticated user (can be None)

        Raises:
            QueryNotFound: If query doesn't exist or doesn't belong to workspace
            WorkspaceForbidden: If user is not authorized to delete queries
        """
        # Get the query and verify it belongs to the workspace
        query = self.db.query(Query).filter(
            Query.id == query_id,
            Query.workspace_id == workspace.id
        ).first()

        if not query:
            raise QueryNotFound(f"Query not found: {query_id}")

        # Check permissions based on workspace visibility and ownership
        if workspace.is_public and workspace.is_orphaned:
            # Public orphan workspace: anyone can delete queries
            pass
        elif workspace.is_private:
            # Private workspace: only owner can delete queries
            if not current_user or workspace.owner_id != current_user.id:
                raise WorkspaceForbidden("Not authorized to delete queries in this workspace")
        else:
            # Public workspace with owner: only owner can delete queries
            if not current_user or workspace.owner_id != current_user.id:
                raise WorkspaceForbidden("Not authorized to delete queries in this workspace")

        # Delete the query from database
        self.db.delete(query)
        self.db.commit()

    def execute_query(self, query: str, files: list[File], page: int | None = None, size: int | None = None, count: bool = False, timeout: int | None = None) -> QueryResult:
        if files is None:
            files = []
        try:
            if size is None:
                size = self.settings.duckdb_page_size
            if count:
                query = query.strip().rstrip(';')
                query = f"SELECT COUNT(*) AS count FROM ({query}) q"
            expression = parse_one(query)
            expression = self._validate_query_and_map_tables(expression, files)
            is_limited = not count and page is not None
            if is_limited:
                expression = self._add_limit(expression, page, size)  # type: ignore
            sql = expression.sql(dialect="duckdb")
            start_time = time.perf_counter()
            result = self._execute_ducbkdb(sql, timeout=timeout)
            elapsed_time = time.perf_counter() - start_time
            return QueryResult(
                time=elapsed_time,
                columns=result['columns'],
                rows=result['rows'] if not is_limited else result['rows'][:size],
                has_more=len(result['rows']) > size
            )
        except (ParseError, TokenError, duckdb.Error) as e:
            # TODO: optimize exception handling to avoid showing raw error messages
            raise BadQuery(str(e)) from e
