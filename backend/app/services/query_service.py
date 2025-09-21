"""
Query service for validating and executing SQL queries.
"""

import time

import duckdb
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
from app.models.file import File
from app.schemas.query import QueryResult
from app.services.exceptions import BadQuery, DisallowedQuery


class QueryService:
    """Service for handling SQL queries with validation and execution."""

    DISALLOWED_EXPRESSIONS = {
        Insert, Update, Delete, Merge, Create, Drop, Alter, TruncateTable, Clone, Analyze,
        Commit, Rollback, Transaction, Grant, Revoke, Export, Cache, Uncache, Kill, Pragma,
        Describe, Show, Use, Set, Lock, Comment, Cluster, Detach, Attach, Replace
    }

    def __init__(self, settings: Settings):
        self.settings = settings

    def _add_limit(self, expr: Expression, page: int = 1, size: int | None = None) -> Expression:
        """Add a LIMIT 50 to the query if not already present."""
        return expr.limit(size).offset((page - 1) * size) # type: ignore

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

    def _validate_query_and_map_tables(self, expression: Expression, files: list[File] = None) -> Expression:
        if files is None:
            files = []
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
                item.replace(to_table(self._get_read_csv_calls_for_file(matching_file)))
                # TODO: add alias to the table
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

    def _execute_ducbkdb(self, sql: str) -> dict:
        con = self._get_connection()
        result = con.sql(sql)
        res = {
            'columns': result.columns,
            'rows': result.fetchall()
        }
        con.close()
        return res

    def execute_query(self, query: str, files: list[File], page: int | None = None, size: int | None = None, count: bool = False) -> QueryResult:
        if files is None:
            files = []
        try:
            if count:
                query = f"SELECT COUNT(*) AS count FROM ({query}) arctic_monkeys"
            expression = parse_one(query)
            expression = self._validate_query_and_map_tables(expression, files)
            if size is None:
                size = self.settings.duckdb_page_size
            if page:
                expression = self._add_limit(expression, page, size)
            sql = expression.sql(dialect="duckdb")
            print(sql)
            start_time = time.perf_counter()
            result = self._execute_ducbkdb(sql)
            elapsed_time = time.perf_counter() - start_time
            return QueryResult(
                time=elapsed_time,
                columns=result['columns'],
                rows=result['rows']
            )
        except (ParseError, TokenError) as e:
            # TODO: optimize exception handling to avoid showing raw error messages
            raise BadQuery("Invalid SQL query: {str(e)}") from e
