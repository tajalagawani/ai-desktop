"""
PostgreSQL Node - Comprehensive PostgreSQL integration for SQL database operations
Refactored with improved architecture: dispatch maps, unified async/sync handling,
proper connection lifecycle, and standardized return shapes.
Supports all major PostgreSQL operations including queries, transactions, prepared statements,
connection pooling, and advanced database features. Uses both psycopg3 and asyncpg for
optimal performance and compatibility.
"""

import logging
import asyncio
import json
import re
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime, timezone
from contextlib import asynccontextmanager

try:
    import psycopg
    from psycopg import sql
    from psycopg.rows import dict_row, tuple_row
    PSYCOPG3_AVAILABLE = True
except ImportError:
    PSYCOPG3_AVAILABLE = False

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError, NodeExecutionError
    )
except ImportError:
    try:
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )
    except ImportError:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )

# Configure logging with proper masking
logger = logging.getLogger(__name__)

class PostgreSQLOperation:
    """All available PostgreSQL operations."""
    
    # Basic Query Operations
    EXECUTE_QUERY = "execute_query"
    FETCH_ONE = "fetch_one"
    FETCH_ALL = "fetch_all"
    FETCH_MANY = "fetch_many"
    EXECUTE_MANY = "execute_many"
    
    # Transaction Operations
    BEGIN_TRANSACTION = "begin_transaction"
    COMMIT_TRANSACTION = "commit_transaction"
    ROLLBACK_TRANSACTION = "rollback_transaction"
    SAVEPOINT = "savepoint"
    ROLLBACK_TO_SAVEPOINT = "rollback_to_savepoint"
    RELEASE_SAVEPOINT = "release_savepoint"
    
    # Prepared Statement Operations
    PREPARE_STATEMENT = "prepare_statement"
    EXECUTE_PREPARED = "execute_prepared"
    DEALLOCATE_PREPARED = "deallocate_prepared"
    
    # Table Operations
    CREATE_TABLE = "create_table"
    DROP_TABLE = "drop_table"
    ALTER_TABLE = "alter_table"
    TRUNCATE_TABLE = "truncate_table"
    
    # Index Operations
    CREATE_INDEX = "create_index"
    DROP_INDEX = "drop_index"
    REINDEX = "reindex"
    
    # Data Operations
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    SELECT = "select"
    UPSERT = "upsert"
    
    # Bulk Operations
    BULK_INSERT = "bulk_insert"
    COPY_FROM = "copy_from"
    COPY_TO = "copy_to"
    
    # Database Operations
    CREATE_DATABASE = "create_database"
    DROP_DATABASE = "drop_database"
    LIST_DATABASES = "list_databases"
    
    # Schema Operations
    CREATE_SCHEMA = "create_schema"
    DROP_SCHEMA = "drop_schema"
    LIST_SCHEMAS = "list_schemas"
    
    # User/Role Operations
    CREATE_USER = "create_user"
    DROP_USER = "drop_user"
    ALTER_USER = "alter_user"
    GRANT_PRIVILEGES = "grant_privileges"
    REVOKE_PRIVILEGES = "revoke_privileges"
    
    # Information Schema Queries
    LIST_TABLES = "list_tables"
    LIST_COLUMNS = "list_columns"
    LIST_INDEXES = "list_indexes"
    TABLE_INFO = "table_info"
    COLUMN_INFO = "column_info"
    
    # Connection Operations
    TEST_CONNECTION = "test_connection"
    GET_SERVER_VERSION = "get_server_version"
    GET_DATABASE_SIZE = "get_database_size"
    
    # Advanced Operations
    EXPLAIN_QUERY = "explain_query"
    ANALYZE_QUERY = "analyze_query"
    VACUUM = "vacuum"
    VACUUM_ANALYZE = "vacuum_analyze"
    
    # Cursor Operations
    DECLARE_CURSOR = "declare_cursor"
    FETCH_CURSOR = "fetch_cursor"
    CLOSE_CURSOR = "close_cursor"
    
    # Function/Procedure Operations
    CREATE_FUNCTION = "create_function"
    DROP_FUNCTION = "drop_function"
    CALL_FUNCTION = "call_function"
    CALL_PROCEDURE = "call_procedure"
    
    # Trigger Operations
    CREATE_TRIGGER = "create_trigger"
    DROP_TRIGGER = "drop_trigger"
    
    # Sequence Operations
    CREATE_SEQUENCE = "create_sequence"
    DROP_SEQUENCE = "drop_sequence"
    NEXTVAL = "nextval"
    CURRVAL = "currval"
    SETVAL = "setval"


class PostgreSQLClientWrapper:
    """Unified PostgreSQL client wrapper that handles both psycopg3 and asyncpg."""
    
    def __init__(self, connection, client_type="psycopg3"):
        self.connection = connection
        self.client_type = client_type
        self.is_async = client_type == "asyncpg"
    
    async def maybe_await(self, result):
        """Helper to handle both sync and async results."""
        if self.is_async and asyncio.iscoroutine(result):
            return await result
        return result
    
    # Connection operations
    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            if self.client_type == "asyncpg":
                await self.connection.fetchval("SELECT 1")
            else:
                cursor = self.connection.cursor()
                await self.maybe_await(cursor.execute("SELECT 1"))
                await self.maybe_await(cursor.close())
            return True
        except Exception:
            return False
    
    async def get_server_version(self) -> str:
        """Get PostgreSQL server version."""
        if self.client_type == "asyncpg":
            return await self.connection.fetchval("SELECT version()")
        else:
            cursor = self.connection.cursor()
            await self.maybe_await(cursor.execute("SELECT version()"))
            result = await self.maybe_await(cursor.fetchone())
            await self.maybe_await(cursor.close())
            return result[0] if result else None
    
    # Query operations
    async def execute_query(self, query: str, params: Tuple = None) -> Any:
        """Execute a query."""
        if self.client_type == "asyncpg":
            if params:
                return await self.connection.execute(query, *params)
            else:
                return await self.connection.execute(query)
        else:
            cursor = self.connection.cursor()
            try:
                await self.maybe_await(cursor.execute(query, params))
                return cursor.rowcount
            finally:
                await self.maybe_await(cursor.close())
    
    async def fetch_one(self, query: str, params: Tuple = None) -> Dict[str, Any]:
        """Fetch one row from query."""
        if self.client_type == "asyncpg":
            if params:
                result = await self.connection.fetchrow(query, *params)
            else:
                result = await self.connection.fetchrow(query)
            return dict(result) if result else None
        else:
            cursor = self.connection.cursor(row_factory=dict_row)
            try:
                await self.maybe_await(cursor.execute(query, params))
                result = await self.maybe_await(cursor.fetchone())
                return result
            finally:
                await self.maybe_await(cursor.close())
    
    async def fetch_all(self, query: str, params: Tuple = None) -> List[Dict[str, Any]]:
        """Fetch all rows from query."""
        if self.client_type == "asyncpg":
            if params:
                results = await self.connection.fetch(query, *params)
            else:
                results = await self.connection.fetch(query)
            return [dict(row) for row in results]
        else:
            cursor = self.connection.cursor(row_factory=dict_row)
            try:
                await self.maybe_await(cursor.execute(query, params))
                results = await self.maybe_await(cursor.fetchall())
                return results
            finally:
                await self.maybe_await(cursor.close())
    
    async def fetch_many(self, query: str, size: int, params: Tuple = None) -> List[Dict[str, Any]]:
        """Fetch many rows from query."""
        if self.client_type == "asyncpg":
            # asyncpg doesn't have fetchmany, so we'll use fetch with limit
            if params:
                results = await self.connection.fetch(f"{query} LIMIT $1", *params, size)
            else:
                results = await self.connection.fetch(f"{query} LIMIT $1", size)
            return [dict(row) for row in results]
        else:
            cursor = self.connection.cursor(row_factory=dict_row)
            try:
                await self.maybe_await(cursor.execute(query, params))
                results = await self.maybe_await(cursor.fetchmany(size))
                return results
            finally:
                await self.maybe_await(cursor.close())
    
    async def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Execute query with multiple parameter sets."""
        if self.client_type == "asyncpg":
            return await self.connection.executemany(query, params_list)
        else:
            cursor = self.connection.cursor()
            try:
                await self.maybe_await(cursor.executemany(query, params_list))
                return cursor.rowcount
            finally:
                await self.maybe_await(cursor.close())
    
    # Transaction operations
    async def begin_transaction(self) -> Any:
        """Begin transaction."""
        if self.client_type == "asyncpg":
            return await self.connection.transaction()
        else:
            # psycopg3 uses context managers for transactions
            return self.connection.transaction()
    
    async def commit_transaction(self) -> None:
        """Commit transaction."""
        if self.client_type == "asyncpg":
            # Transactions are handled via context managers in asyncpg
            pass
        else:
            await self.maybe_await(self.connection.commit())
    
    async def rollback_transaction(self) -> None:
        """Rollback transaction."""
        if self.client_type == "asyncpg":
            # Transactions are handled via context managers in asyncpg
            pass
        else:
            await self.maybe_await(self.connection.rollback())
    
    # Prepared statement operations
    async def prepare_statement(self, name: str, query: str) -> Any:
        """Prepare a statement."""
        if self.client_type == "asyncpg":
            return await self.connection.prepare(query)
        else:
            cursor = self.connection.cursor()
            prepare_query = f"PREPARE {name} AS {query}"
            await self.maybe_await(cursor.execute(prepare_query))
            await self.maybe_await(cursor.close())
            return name
    
    async def execute_prepared(self, statement, params: Tuple = None) -> Any:
        """Execute prepared statement."""
        if self.client_type == "asyncpg":
            if params:
                return await statement(*params)
            else:
                return await statement()
        else:
            cursor = self.connection.cursor()
            try:
                if params:
                    await self.maybe_await(cursor.execute(f"EXECUTE {statement} ({','.join(['%s'] * len(params))})", params))
                else:
                    await self.maybe_await(cursor.execute(f"EXECUTE {statement}"))
                return cursor.rowcount
            finally:
                await self.maybe_await(cursor.close())
    
    # Bulk operations
    async def bulk_insert(self, table: str, columns: List[str], data: List[Tuple]) -> int:
        """Bulk insert data."""
        if self.client_type == "asyncpg":
            query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(['$' + str(i+1) for i in range(len(columns))])})"
            return await self.connection.executemany(query, data)
        else:
            cursor = self.connection.cursor()
            try:
                query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(['%s'] * len(columns))})"
                await self.maybe_await(cursor.executemany(query, data))
                return cursor.rowcount
            finally:
                await self.maybe_await(cursor.close())
    
    async def copy_from(self, table: str, columns: List[str], data: str) -> int:
        """Copy data from string."""
        if self.client_type == "asyncpg":
            return await self.connection.copy_from_table(table, source=data, columns=columns)
        else:
            cursor = self.connection.cursor()
            try:
                import io
                copy_query = f"COPY {table} ({','.join(columns)}) FROM STDIN"
                with cursor.copy(copy_query) as copy:
                    copy.write(data)
                return cursor.rowcount
            finally:
                await self.maybe_await(cursor.close())
    
    # Information queries
    async def list_tables(self, schema: str = "public") -> List[str]:
        """List tables in schema."""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = $1 AND table_type = 'BASE TABLE'
        """ if self.client_type == "asyncpg" else """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
        """
        
        if self.client_type == "asyncpg":
            results = await self.connection.fetch(query, schema)
            return [row['table_name'] for row in results]
        else:
            cursor = self.connection.cursor()
            try:
                await self.maybe_await(cursor.execute(query, (schema,)))
                results = await self.maybe_await(cursor.fetchall())
                return [row[0] for row in results]
            finally:
                await self.maybe_await(cursor.close())
    
    async def list_columns(self, table: str, schema: str = "public") -> List[Dict[str, Any]]:
        """List columns in table."""
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = $1 AND table_name = $2
        ORDER BY ordinal_position
        """ if self.client_type == "asyncpg" else """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """
        
        if self.client_type == "asyncpg":
            results = await self.connection.fetch(query, schema, table)
            return [dict(row) for row in results]
        else:
            cursor = self.connection.cursor(row_factory=dict_row)
            try:
                await self.maybe_await(cursor.execute(query, (schema, table)))
                return await self.maybe_await(cursor.fetchall())
            finally:
                await self.maybe_await(cursor.close())
    
    async def get_database_size(self, database: str) -> int:
        """Get database size in bytes."""
        query = "SELECT pg_database_size($1)" if self.client_type == "asyncpg" else "SELECT pg_database_size(%s)"
        
        if self.client_type == "asyncpg":
            return await self.connection.fetchval(query, database)
        else:
            cursor = self.connection.cursor()
            try:
                await self.maybe_await(cursor.execute(query, (database,)))
                result = await self.maybe_await(cursor.fetchone())
                return result[0] if result else 0
            finally:
                await self.maybe_await(cursor.close())
    
    async def explain_query(self, query: str, params: Tuple = None, analyze: bool = False) -> List[str]:
        """Explain query execution plan."""
        explain_query = f"EXPLAIN {'ANALYZE ' if analyze else ''}{query}"
        
        if self.client_type == "asyncpg":
            if params:
                results = await self.connection.fetch(explain_query, *params)
            else:
                results = await self.connection.fetch(explain_query)
            return [row[0] for row in results]
        else:
            cursor = self.connection.cursor()
            try:
                await self.maybe_await(cursor.execute(explain_query, params))
                results = await self.maybe_await(cursor.fetchall())
                return [row[0] for row in results]
            finally:
                await self.maybe_await(cursor.close())
    
    async def close(self):
        """Close connection."""
        if self.client_type == "asyncpg":
            await self.connection.close()
        else:
            await self.maybe_await(self.connection.close())


class OperationMetadata:
    """Metadata for operation validation and parameter requirements."""
    
    def __init__(self, required_params: List[str], optional_params: List[str] = None, 
                 handler: Optional[Callable] = None):
        self.required_params = required_params
        self.optional_params = optional_params or []
        self.handler = handler


class PostgreSQLNode(BaseNode):
    """
    Comprehensive PostgreSQL integration node supporting all major SQL database operations.
    Handles queries, transactions, prepared statements, bulk operations, and advanced 
    PostgreSQL features. Uses both psycopg3 and asyncpg for optimal performance.
    """
    
    # Operation metadata table - programmatic validation generation
    OPERATION_METADATA = {
        # Basic query operations
        PostgreSQLOperation.EXECUTE_QUERY: OperationMetadata(["query"]),
        PostgreSQLOperation.FETCH_ONE: OperationMetadata(["query"]),
        PostgreSQLOperation.FETCH_ALL: OperationMetadata(["query"]),
        PostgreSQLOperation.FETCH_MANY: OperationMetadata(["query", "size"]),
        PostgreSQLOperation.EXECUTE_MANY: OperationMetadata(["query", "params_list"]),
        
        # Transaction operations
        PostgreSQLOperation.BEGIN_TRANSACTION: OperationMetadata([]),
        PostgreSQLOperation.COMMIT_TRANSACTION: OperationMetadata([]),
        PostgreSQLOperation.ROLLBACK_TRANSACTION: OperationMetadata([]),
        PostgreSQLOperation.SAVEPOINT: OperationMetadata(["savepoint_name"]),
        PostgreSQLOperation.ROLLBACK_TO_SAVEPOINT: OperationMetadata(["savepoint_name"]),
        PostgreSQLOperation.RELEASE_SAVEPOINT: OperationMetadata(["savepoint_name"]),
        
        # Prepared statement operations
        PostgreSQLOperation.PREPARE_STATEMENT: OperationMetadata(["statement_name", "query"]),
        PostgreSQLOperation.EXECUTE_PREPARED: OperationMetadata(["statement_name"]),
        PostgreSQLOperation.DEALLOCATE_PREPARED: OperationMetadata(["statement_name"]),
        
        # Table operations
        PostgreSQLOperation.CREATE_TABLE: OperationMetadata(["table_name", "columns"]),
        PostgreSQLOperation.DROP_TABLE: OperationMetadata(["table_name"]),
        PostgreSQLOperation.ALTER_TABLE: OperationMetadata(["table_name", "alteration"]),
        PostgreSQLOperation.TRUNCATE_TABLE: OperationMetadata(["table_name"]),
        
        # Index operations
        PostgreSQLOperation.CREATE_INDEX: OperationMetadata(["index_name", "table_name", "columns"]),
        PostgreSQLOperation.DROP_INDEX: OperationMetadata(["index_name"]),
        PostgreSQLOperation.REINDEX: OperationMetadata(["target"]),
        
        # Data operations
        PostgreSQLOperation.INSERT: OperationMetadata(["table_name", "data"]),
        PostgreSQLOperation.UPDATE: OperationMetadata(["table_name", "data", "where_clause"]),
        PostgreSQLOperation.DELETE: OperationMetadata(["table_name", "where_clause"]),
        PostgreSQLOperation.SELECT: OperationMetadata(["table_name"]),
        PostgreSQLOperation.UPSERT: OperationMetadata(["table_name", "data", "conflict_columns"]),
        
        # Bulk operations
        PostgreSQLOperation.BULK_INSERT: OperationMetadata(["table_name", "columns", "data"]),
        PostgreSQLOperation.COPY_FROM: OperationMetadata(["table_name", "columns", "data"]),
        PostgreSQLOperation.COPY_TO: OperationMetadata(["table_name", "columns"]),
        
        # Database operations
        PostgreSQLOperation.CREATE_DATABASE: OperationMetadata(["database_name"]),
        PostgreSQLOperation.DROP_DATABASE: OperationMetadata(["database_name"]),
        PostgreSQLOperation.LIST_DATABASES: OperationMetadata([]),
        
        # Schema operations
        PostgreSQLOperation.CREATE_SCHEMA: OperationMetadata(["schema_name"]),
        PostgreSQLOperation.DROP_SCHEMA: OperationMetadata(["schema_name"]),
        PostgreSQLOperation.LIST_SCHEMAS: OperationMetadata([]),
        
        # User operations
        PostgreSQLOperation.CREATE_USER: OperationMetadata(["username"]),
        PostgreSQLOperation.DROP_USER: OperationMetadata(["username"]),
        PostgreSQLOperation.ALTER_USER: OperationMetadata(["username", "alterations"]),
        PostgreSQLOperation.GRANT_PRIVILEGES: OperationMetadata(["privileges", "target", "username"]),
        PostgreSQLOperation.REVOKE_PRIVILEGES: OperationMetadata(["privileges", "target", "username"]),
        
        # Information operations
        PostgreSQLOperation.LIST_TABLES: OperationMetadata([]),
        PostgreSQLOperation.LIST_COLUMNS: OperationMetadata(["table_name"]),
        PostgreSQLOperation.LIST_INDEXES: OperationMetadata(["table_name"]),
        PostgreSQLOperation.TABLE_INFO: OperationMetadata(["table_name"]),
        PostgreSQLOperation.COLUMN_INFO: OperationMetadata(["table_name", "column_name"]),
        
        # Connection operations
        PostgreSQLOperation.TEST_CONNECTION: OperationMetadata([]),
        PostgreSQLOperation.GET_SERVER_VERSION: OperationMetadata([]),
        PostgreSQLOperation.GET_DATABASE_SIZE: OperationMetadata(["database_name"]),
        
        # Advanced operations
        PostgreSQLOperation.EXPLAIN_QUERY: OperationMetadata(["query"]),
        PostgreSQLOperation.ANALYZE_QUERY: OperationMetadata(["query"]),
        PostgreSQLOperation.VACUUM: OperationMetadata([]),
        PostgreSQLOperation.VACUUM_ANALYZE: OperationMetadata([]),
        
        # Function operations
        PostgreSQLOperation.CREATE_FUNCTION: OperationMetadata(["function_name", "function_body"]),
        PostgreSQLOperation.DROP_FUNCTION: OperationMetadata(["function_name"]),
        PostgreSQLOperation.CALL_FUNCTION: OperationMetadata(["function_name"]),
        PostgreSQLOperation.CALL_PROCEDURE: OperationMetadata(["procedure_name"]),
        
        # Sequence operations
        PostgreSQLOperation.CREATE_SEQUENCE: OperationMetadata(["sequence_name"]),
        PostgreSQLOperation.DROP_SEQUENCE: OperationMetadata(["sequence_name"]),
        PostgreSQLOperation.NEXTVAL: OperationMetadata(["sequence_name"]),
        PostgreSQLOperation.CURRVAL: OperationMetadata(["sequence_name"]),
        PostgreSQLOperation.SETVAL: OperationMetadata(["sequence_name", "value"]),
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create dispatch map for operations
        self.operation_dispatch = {
            # Basic query operations
            PostgreSQLOperation.EXECUTE_QUERY: self._handle_execute_query,
            PostgreSQLOperation.FETCH_ONE: self._handle_fetch_one,
            PostgreSQLOperation.FETCH_ALL: self._handle_fetch_all,
            PostgreSQLOperation.FETCH_MANY: self._handle_fetch_many,
            PostgreSQLOperation.EXECUTE_MANY: self._handle_execute_many,
            
            # Transaction operations
            PostgreSQLOperation.BEGIN_TRANSACTION: self._handle_begin_transaction,
            PostgreSQLOperation.COMMIT_TRANSACTION: self._handle_commit_transaction,
            PostgreSQLOperation.ROLLBACK_TRANSACTION: self._handle_rollback_transaction,
            PostgreSQLOperation.SAVEPOINT: self._handle_savepoint,
            PostgreSQLOperation.ROLLBACK_TO_SAVEPOINT: self._handle_rollback_to_savepoint,
            PostgreSQLOperation.RELEASE_SAVEPOINT: self._handle_release_savepoint,
            
            # Prepared statement operations
            PostgreSQLOperation.PREPARE_STATEMENT: self._handle_prepare_statement,
            PostgreSQLOperation.EXECUTE_PREPARED: self._handle_execute_prepared,
            PostgreSQLOperation.DEALLOCATE_PREPARED: self._handle_deallocate_prepared,
            
            # Table operations
            PostgreSQLOperation.CREATE_TABLE: self._handle_create_table,
            PostgreSQLOperation.DROP_TABLE: self._handle_drop_table,
            PostgreSQLOperation.ALTER_TABLE: self._handle_alter_table,
            PostgreSQLOperation.TRUNCATE_TABLE: self._handle_truncate_table,
            
            # Index operations
            PostgreSQLOperation.CREATE_INDEX: self._handle_create_index,
            PostgreSQLOperation.DROP_INDEX: self._handle_drop_index,
            PostgreSQLOperation.REINDEX: self._handle_reindex,
            
            # Data operations
            PostgreSQLOperation.INSERT: self._handle_insert,
            PostgreSQLOperation.UPDATE: self._handle_update,
            PostgreSQLOperation.DELETE: self._handle_delete,
            PostgreSQLOperation.SELECT: self._handle_select,
            PostgreSQLOperation.UPSERT: self._handle_upsert,
            
            # Bulk operations
            PostgreSQLOperation.BULK_INSERT: self._handle_bulk_insert,
            PostgreSQLOperation.COPY_FROM: self._handle_copy_from,
            PostgreSQLOperation.COPY_TO: self._handle_copy_to,
            
            # Database operations
            PostgreSQLOperation.CREATE_DATABASE: self._handle_create_database,
            PostgreSQLOperation.DROP_DATABASE: self._handle_drop_database,
            PostgreSQLOperation.LIST_DATABASES: self._handle_list_databases,
            
            # Schema operations
            PostgreSQLOperation.CREATE_SCHEMA: self._handle_create_schema,
            PostgreSQLOperation.DROP_SCHEMA: self._handle_drop_schema,
            PostgreSQLOperation.LIST_SCHEMAS: self._handle_list_schemas,
            
            # User operations
            PostgreSQLOperation.CREATE_USER: self._handle_create_user,
            PostgreSQLOperation.DROP_USER: self._handle_drop_user,
            PostgreSQLOperation.ALTER_USER: self._handle_alter_user,
            PostgreSQLOperation.GRANT_PRIVILEGES: self._handle_grant_privileges,
            PostgreSQLOperation.REVOKE_PRIVILEGES: self._handle_revoke_privileges,
            
            # Information operations
            PostgreSQLOperation.LIST_TABLES: self._handle_list_tables,
            PostgreSQLOperation.LIST_COLUMNS: self._handle_list_columns,
            PostgreSQLOperation.LIST_INDEXES: self._handle_list_indexes,
            PostgreSQLOperation.TABLE_INFO: self._handle_table_info,
            PostgreSQLOperation.COLUMN_INFO: self._handle_column_info,
            
            # Connection operations
            PostgreSQLOperation.TEST_CONNECTION: self._handle_test_connection,
            PostgreSQLOperation.GET_SERVER_VERSION: self._handle_get_server_version,
            PostgreSQLOperation.GET_DATABASE_SIZE: self._handle_get_database_size,
            
            # Advanced operations
            PostgreSQLOperation.EXPLAIN_QUERY: self._handle_explain_query,
            PostgreSQLOperation.ANALYZE_QUERY: self._handle_analyze_query,
            PostgreSQLOperation.VACUUM: self._handle_vacuum,
            PostgreSQLOperation.VACUUM_ANALYZE: self._handle_vacuum_analyze,
            
            # Function operations
            PostgreSQLOperation.CREATE_FUNCTION: self._handle_create_function,
            PostgreSQLOperation.DROP_FUNCTION: self._handle_drop_function,
            PostgreSQLOperation.CALL_FUNCTION: self._handle_call_function,
            PostgreSQLOperation.CALL_PROCEDURE: self._handle_call_procedure,
            
            # Sequence operations
            PostgreSQLOperation.CREATE_SEQUENCE: self._handle_create_sequence,
            PostgreSQLOperation.DROP_SEQUENCE: self._handle_drop_sequence,
            PostgreSQLOperation.NEXTVAL: self._handle_nextval,
            PostgreSQLOperation.CURRVAL: self._handle_currval,
            PostgreSQLOperation.SETVAL: self._handle_setval,
        }
    
    def get_schema(self) -> NodeSchema:
        """Generate schema with all parameters from operation metadata."""
        # Common parameters for all operations
        base_params = [
            ("operation", NodeParameterType.STRING, "PostgreSQL operation to perform", True, list(self.OPERATION_METADATA.keys())),
            ("host", NodeParameterType.STRING, "PostgreSQL host", False, None, "localhost"),
            ("port", NodeParameterType.NUMBER, "PostgreSQL port", False, None, 5432),
            ("database", NodeParameterType.STRING, "Database name", True),
            ("username", NodeParameterType.STRING, "Username", True),
            ("password", NodeParameterType.STRING, "Password", True),
            ("ssl_mode", NodeParameterType.STRING, "SSL mode", False, ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"], "prefer"),
            ("client_type", NodeParameterType.STRING, "Client library to use", False, ["psycopg3", "asyncpg"], "psycopg3"),
            ("connection_timeout", NodeParameterType.NUMBER, "Connection timeout in seconds", False, None, 30),
            ("command_timeout", NodeParameterType.NUMBER, "Command timeout in seconds", False, None, 60),
        ]
        
        # Operation-specific parameters
        operation_params = [
            # Query parameters
            ("query", NodeParameterType.STRING, "SQL query to execute", False),
            ("params", NodeParameterType.ARRAY, "Query parameters", False),
            ("size", NodeParameterType.NUMBER, "Number of rows to fetch", False),
            ("params_list", NodeParameterType.ARRAY, "List of parameter tuples for execute_many", False),
            
            # Table parameters
            ("table_name", NodeParameterType.STRING, "Table name", False),
            ("schema_name", NodeParameterType.STRING, "Schema name", False),
            ("columns", NodeParameterType.ARRAY, "Column definitions or names", False),
            ("data", NodeParameterType.OBJECT, "Data for insert/update operations", False),
            ("where_clause", NodeParameterType.STRING, "WHERE clause for update/delete", False),
            ("conflict_columns", NodeParameterType.ARRAY, "Columns for conflict resolution in upsert", False),
            
            # Index parameters
            ("index_name", NodeParameterType.STRING, "Index name", False),
            ("unique", NodeParameterType.BOOLEAN, "Create unique index", False),
            ("concurrent", NodeParameterType.BOOLEAN, "Create index concurrently", False),
            
            # Database/Schema parameters
            ("database_name", NodeParameterType.STRING, "Database name for operations", False),
            ("owner", NodeParameterType.STRING, "Owner for database/schema", False),
            ("template", NodeParameterType.STRING, "Template database", False),
            ("encoding", NodeParameterType.STRING, "Database encoding", False),
            
            # User parameters
            ("password_user", NodeParameterType.STRING, "Password for user creation", False),
            ("privileges", NodeParameterType.ARRAY, "Privileges to grant/revoke", False),
            ("target", NodeParameterType.STRING, "Target object for privileges", False),
            ("alterations", NodeParameterType.OBJECT, "User alterations", False),
            
            # Transaction parameters
            ("savepoint_name", NodeParameterType.STRING, "Savepoint name", False),
            ("isolation_level", NodeParameterType.STRING, "Transaction isolation level", False, ["READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"]),
            
            # Prepared statement parameters
            ("statement_name", NodeParameterType.STRING, "Prepared statement name", False),
            
            # Advanced parameters
            ("analyze", NodeParameterType.BOOLEAN, "Include ANALYZE in EXPLAIN", False),
            ("vacuum_full", NodeParameterType.BOOLEAN, "Perform VACUUM FULL", False),
            ("vacuum_freeze", NodeParameterType.BOOLEAN, "Perform VACUUM FREEZE", False),
            
            # Function/Procedure parameters
            ("function_name", NodeParameterType.STRING, "Function name", False),
            ("procedure_name", NodeParameterType.STRING, "Procedure name", False),
            ("function_body", NodeParameterType.STRING, "Function body/definition", False),
            ("return_type", NodeParameterType.STRING, "Function return type", False),
            ("language", NodeParameterType.STRING, "Function language", False, ["SQL", "PLPGSQL", "PYTHON", "C"]),
            
            # Sequence parameters
            ("sequence_name", NodeParameterType.STRING, "Sequence name", False),
            ("value", NodeParameterType.NUMBER, "Value for sequence operations", False),
            ("increment", NodeParameterType.NUMBER, "Sequence increment", False),
            ("min_value", NodeParameterType.NUMBER, "Sequence minimum value", False),
            ("max_value", NodeParameterType.NUMBER, "Sequence maximum value", False),
            ("start_value", NodeParameterType.NUMBER, "Sequence start value", False),
            
            # Cursor parameters
            ("cursor_name", NodeParameterType.STRING, "Cursor name", False),
            ("fetch_count", NodeParameterType.NUMBER, "Number of rows to fetch from cursor", False),
            
            # Copy parameters
            ("format", NodeParameterType.STRING, "Copy format", False, ["TEXT", "CSV", "BINARY"]),
            ("delimiter", NodeParameterType.STRING, "Copy delimiter", False),
            ("header", NodeParameterType.BOOLEAN, "Include header in copy", False),
            
            # Trigger parameters
            ("trigger_name", NodeParameterType.STRING, "Trigger name", False),
            ("trigger_function", NodeParameterType.STRING, "Trigger function", False),
            ("trigger_events", NodeParameterType.ARRAY, "Trigger events", False),
            ("trigger_timing", NodeParameterType.STRING, "Trigger timing", False, ["BEFORE", "AFTER", "INSTEAD OF"]),
            
            # Filter parameters
            ("pattern", NodeParameterType.STRING, "Pattern for filtering results", False),
            ("limit", NodeParameterType.NUMBER, "Limit number of results", False),
            ("offset", NodeParameterType.NUMBER, "Offset for pagination", False),
        ]
        
        # Build parameters dict
        parameters = {}
        for param_def in base_params + operation_params:
            name = param_def[0]
            param_type = param_def[1]
            description = param_def[2]
            required = param_def[3]
            enum = param_def[4] if len(param_def) > 4 else None
            default = param_def[5] if len(param_def) > 5 else None
            
            param_kwargs = {
                "name": name,
                "type": param_type,
                "description": description,
                "required": required
            }
            
            if enum:
                param_kwargs["enum"] = enum
            if default is not None:
                param_kwargs["default"] = default
            
            parameters[name] = NodeParameter(**param_kwargs)
        
        return NodeSchema(
            node_type="postgresql",
            version="1.0.0",
            description="Comprehensive PostgreSQL integration supporting all major SQL database operations including queries, transactions, prepared statements, bulk operations, and advanced PostgreSQL features",
            parameters=list(parameters.values()),
            outputs={
                "status": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "start_time": NodeParameterType.STRING,
                "execution_time": NodeParameterType.NUMBER,
                "inputs": NodeParameterType.OBJECT,
                "raw_result": NodeParameterType.ANY,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "postgresql_error": NodeParameterType.STRING,
                "connection_info": NodeParameterType.OBJECT,
                "rows_affected": NodeParameterType.NUMBER,
                "row_count": NodeParameterType.NUMBER,
                "columns": NodeParameterType.ARRAY,
                "execution_plan": NodeParameterType.ARRAY,
                "server_version": NodeParameterType.STRING,
                "database_size": NodeParameterType.NUMBER,
                "transaction_id": NodeParameterType.STRING,
                "prepared_statement": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PostgreSQL-specific parameters using operation metadata."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Basic validation
        if not operation:
            raise NodeValidationError("Operation is required")
        
        if operation not in self.OPERATION_METADATA:
            raise NodeValidationError(f"Invalid operation: {operation}")
        
        # Connection validation
        required_conn_params = ["database", "username", "password"]
        for param in required_conn_params:
            if not params.get(param):
                raise NodeValidationError(f"{param} is required")
        
        # Operation-specific validation using metadata
        metadata = self.OPERATION_METADATA[operation]
        
        # Check required parameters
        for param in metadata.required_params:
            if param not in params or params[param] is None:
                raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")
        
        # Additional validation for specific operations
        if operation in [PostgreSQLOperation.EXECUTE_QUERY, PostgreSQLOperation.FETCH_ONE, PostgreSQLOperation.FETCH_ALL]:
            query = params.get("query", "")
            if not query.strip():
                raise NodeValidationError("Query cannot be empty")
            
            # Basic SQL injection protection
            dangerous_patterns = [
                r";\s*drop\s+",
                r";\s*delete\s+from\s+",
                r";\s*truncate\s+",
                r"--.*",
                r"/\*.*\*/"
            ]
            for pattern in dangerous_patterns:
                if re.search(pattern, query.lower()):
                    logger.warning(f"Potentially dangerous SQL pattern detected: {pattern}")
        
        if operation == PostgreSQLOperation.EXECUTE_MANY:
            params_list = params.get("params_list")
            if not isinstance(params_list, list):
                raise NodeValidationError("params_list must be a list of parameter tuples")
        
        if operation in [PostgreSQLOperation.INSERT, PostgreSQLOperation.UPDATE, PostgreSQLOperation.UPSERT]:
            data = params.get("data")
            if not isinstance(data, (dict, list)):
                raise NodeValidationError("data must be a dictionary or list")
        
        if operation == PostgreSQLOperation.BULK_INSERT:
            columns = params.get("columns")
            data = params.get("data")
            if not isinstance(columns, list):
                raise NodeValidationError("columns must be a list")
            if not isinstance(data, list):
                raise NodeValidationError("data must be a list of tuples")
        
        return node_data
    
    @asynccontextmanager
    async def _get_postgresql_client(self, params: Dict[str, Any]):
        """Context manager for PostgreSQL client with proper connection lifecycle."""
        host = params.get("host", "localhost")
        port = params.get("port", 5432)
        database = params.get("database")
        username = params.get("username")
        password = params.get("password")
        ssl_mode = params.get("ssl_mode", "prefer")
        client_type = params.get("client_type", "psycopg3")
        connection_timeout = params.get("connection_timeout", 30)
        
        connection = None
        try:
            if client_type == "asyncpg" and ASYNCPG_AVAILABLE:
                # Use asyncpg for high performance
                connection = await asyncpg.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=username,
                    password=password,
                    ssl=ssl_mode,
                    timeout=connection_timeout
                )
                client = PostgreSQLClientWrapper(connection, "asyncpg")
            elif PSYCOPG3_AVAILABLE:
                # Use psycopg3 as default
                conn_params = {
                    "host": host,
                    "port": port,
                    "dbname": database,
                    "user": username,
                    "password": password,
                    "sslmode": ssl_mode,
                    "connect_timeout": connection_timeout
                }
                
                # Create async connection for psycopg3
                connection = await psycopg.AsyncConnection.connect(**conn_params)
                client = PostgreSQLClientWrapper(connection, "psycopg3")
            else:
                raise NodeExecutionError("No PostgreSQL client library available. Install psycopg3 or asyncpg.")
            
            yield client
        finally:
            if connection:
                await client.close()
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in parameters for logging."""
        masked_data = data.copy()
        
        # Mask sensitive fields
        sensitive_fields = ["password", "password_user"]
        for field in sensitive_fields:
            if field in masked_data:
                masked_data[field] = "***MASKED***"
        
        return masked_data
    
    def _create_standard_response(self, operation: str, start_time: datetime, 
                                 params: Dict[str, Any], result: Any, 
                                 error: Optional[str] = None, 
                                 postgresql_error: Optional[str] = None) -> Dict[str, Any]:
        """Create standardized response shape."""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        response = {
            "status": "success" if error is None else "error",
            "operation": operation,
            "start_time": start_time.isoformat(),
            "execution_time": execution_time,
            "inputs": self._mask_sensitive_data(params),
            "raw_result": result,
            "result": result,
        }
        
        if error:
            response["error"] = error
        
        if postgresql_error:
            response["postgresql_error"] = postgresql_error
        
        # Add connection info (without sensitive data)
        response["connection_info"] = {
            "host": params.get("host", "localhost"),
            "port": params.get("port", 5432),
            "database": params.get("database"),
            "username": params.get("username"),
            "client_type": params.get("client_type", "psycopg3"),
        }
        
        return response
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the PostgreSQL operation using dispatch map."""
        start_time = datetime.now()
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Get handler from dispatch map
        handler = self.operation_dispatch.get(operation)
        if not handler:
            return self._create_standard_response(
                operation, start_time, params, None,
                error=f"Unknown operation: {operation}"
            )
        
        try:
            # Create PostgreSQL client with proper connection lifecycle
            async with self._get_postgresql_client(params) as pg_client:
                # Call the handler
                result = await handler(pg_client, params)
                
                return self._create_standard_response(
                    operation, start_time, params, result
                )
        
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Unexpected error in operation {operation}: {e}")
            return self._create_standard_response(
                operation, start_time, params, None,
                error=str(e), postgresql_error=error_type
            )
    
    # Basic query operation handlers
    async def _handle_execute_query(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle EXECUTE_QUERY operation."""
        query = params["query"]
        query_params = tuple(params.get("params", []))
        return await pg_client.execute_query(query, query_params if query_params else None)
    
    async def _handle_fetch_one(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FETCH_ONE operation."""
        query = params["query"]
        query_params = tuple(params.get("params", []))
        return await pg_client.fetch_one(query, query_params if query_params else None)
    
    async def _handle_fetch_all(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle FETCH_ALL operation."""
        query = params["query"]
        query_params = tuple(params.get("params", []))
        return await pg_client.fetch_all(query, query_params if query_params else None)
    
    async def _handle_fetch_many(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle FETCH_MANY operation."""
        query = params["query"]
        size = params["size"]
        query_params = tuple(params.get("params", []))
        return await pg_client.fetch_many(query, size, query_params if query_params else None)
    
    async def _handle_execute_many(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> int:
        """Handle EXECUTE_MANY operation."""
        query = params["query"]
        params_list = params["params_list"]
        return await pg_client.execute_many(query, params_list)
    
    # Transaction operation handlers
    async def _handle_begin_transaction(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle BEGIN_TRANSACTION operation."""
        transaction = await pg_client.begin_transaction()
        return "Transaction started"
    
    async def _handle_commit_transaction(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle COMMIT_TRANSACTION operation."""
        await pg_client.commit_transaction()
        return "Transaction committed"
    
    async def _handle_rollback_transaction(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle ROLLBACK_TRANSACTION operation."""
        await pg_client.rollback_transaction()
        return "Transaction rolled back"
    
    async def _handle_savepoint(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle SAVEPOINT operation."""
        savepoint_name = params["savepoint_name"]
        query = f"SAVEPOINT {savepoint_name}"
        await pg_client.execute_query(query)
        return f"Savepoint {savepoint_name} created"
    
    async def _handle_rollback_to_savepoint(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle ROLLBACK_TO_SAVEPOINT operation."""
        savepoint_name = params["savepoint_name"]
        query = f"ROLLBACK TO SAVEPOINT {savepoint_name}"
        await pg_client.execute_query(query)
        return f"Rolled back to savepoint {savepoint_name}"
    
    async def _handle_release_savepoint(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle RELEASE_SAVEPOINT operation."""
        savepoint_name = params["savepoint_name"]
        query = f"RELEASE SAVEPOINT {savepoint_name}"
        await pg_client.execute_query(query)
        return f"Savepoint {savepoint_name} released"
    
    # Prepared statement handlers
    async def _handle_prepare_statement(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle PREPARE_STATEMENT operation."""
        statement_name = params["statement_name"]
        query = params["query"]
        return await pg_client.prepare_statement(statement_name, query)
    
    async def _handle_execute_prepared(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle EXECUTE_PREPARED operation."""
        statement_name = params["statement_name"]
        query_params = tuple(params.get("params", []))
        return await pg_client.execute_prepared(statement_name, query_params if query_params else None)
    
    async def _handle_deallocate_prepared(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle DEALLOCATE_PREPARED operation."""
        statement_name = params["statement_name"]
        query = f"DEALLOCATE {statement_name}"
        await pg_client.execute_query(query)
        return f"Prepared statement {statement_name} deallocated"
    
    # Table operation handlers
    async def _handle_create_table(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle CREATE_TABLE operation."""
        table_name = params["table_name"]
        columns = params["columns"]
        
        if isinstance(columns, list):
            columns_def = ", ".join(columns)
        else:
            columns_def = columns
        
        query = f"CREATE TABLE {table_name} ({columns_def})"
        await pg_client.execute_query(query)
        return f"Table {table_name} created"
    
    async def _handle_drop_table(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle DROP_TABLE operation."""
        table_name = params["table_name"]
        cascade = params.get("cascade", False)
        
        query = f"DROP TABLE {table_name}"
        if cascade:
            query += " CASCADE"
        
        await pg_client.execute_query(query)
        return f"Table {table_name} dropped"
    
    async def _handle_alter_table(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle ALTER_TABLE operation."""
        table_name = params["table_name"]
        alteration = params["alteration"]
        
        query = f"ALTER TABLE {table_name} {alteration}"
        await pg_client.execute_query(query)
        return f"Table {table_name} altered"
    
    async def _handle_truncate_table(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle TRUNCATE_TABLE operation."""
        table_name = params["table_name"]
        restart_identity = params.get("restart_identity", False)
        cascade = params.get("cascade", False)
        
        query = f"TRUNCATE TABLE {table_name}"
        if restart_identity:
            query += " RESTART IDENTITY"
        if cascade:
            query += " CASCADE"
        
        await pg_client.execute_query(query)
        return f"Table {table_name} truncated"
    
    # Index operation handlers
    async def _handle_create_index(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle CREATE_INDEX operation."""
        index_name = params["index_name"]
        table_name = params["table_name"]
        columns = params["columns"]
        unique = params.get("unique", False)
        concurrent = params.get("concurrent", False)
        
        if isinstance(columns, list):
            columns_str = ", ".join(columns)
        else:
            columns_str = columns
        
        query = "CREATE"
        if unique:
            query += " UNIQUE"
        query += " INDEX"
        if concurrent:
            query += " CONCURRENTLY"
        query += f" {index_name} ON {table_name} ({columns_str})"
        
        await pg_client.execute_query(query)
        return f"Index {index_name} created"
    
    async def _handle_drop_index(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle DROP_INDEX operation."""
        index_name = params["index_name"]
        concurrent = params.get("concurrent", False)
        cascade = params.get("cascade", False)
        
        query = f"DROP INDEX"
        if concurrent:
            query += " CONCURRENTLY"
        query += f" {index_name}"
        if cascade:
            query += " CASCADE"
        
        await pg_client.execute_query(query)
        return f"Index {index_name} dropped"
    
    async def _handle_reindex(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle REINDEX operation."""
        target = params["target"]
        concurrent = params.get("concurrent", False)
        
        query = f"REINDEX"
        if concurrent:
            query += " CONCURRENTLY"
        query += f" {target}"
        
        await pg_client.execute_query(query)
        return f"Reindex completed for {target}"
    
    # Data operation handlers
    async def _handle_insert(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle INSERT operation."""
        table_name = params["table_name"]
        data = params["data"]
        
        if isinstance(data, dict):
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ", ".join([f"${i+1}" if pg_client.client_type == "asyncpg" else "%s" for i in range(len(values))])
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            await pg_client.execute_query(query, tuple(values))
        else:
            # Assume data is already formatted for bulk insert
            query = f"INSERT INTO {table_name} VALUES {data}"
            await pg_client.execute_query(query)
        
        return f"Data inserted into {table_name}"
    
    async def _handle_update(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle UPDATE operation."""
        table_name = params["table_name"]
        data = params["data"]
        where_clause = params["where_clause"]
        
        if isinstance(data, dict):
            set_clauses = []
            values = []
            for i, (key, value) in enumerate(data.items()):
                if pg_client.client_type == "asyncpg":
                    set_clauses.append(f"{key} = ${i+1}")
                else:
                    set_clauses.append(f"{key} = %s")
                values.append(value)
            
            query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {where_clause}"
            await pg_client.execute_query(query, tuple(values))
        else:
            query = f"UPDATE {table_name} SET {data} WHERE {where_clause}"
            await pg_client.execute_query(query)
        
        return f"Data updated in {table_name}"
    
    async def _handle_delete(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle DELETE operation."""
        table_name = params["table_name"]
        where_clause = params["where_clause"]
        
        query = f"DELETE FROM {table_name} WHERE {where_clause}"
        await pg_client.execute_query(query)
        return f"Data deleted from {table_name}"
    
    async def _handle_select(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle SELECT operation."""
        table_name = params["table_name"]
        columns = params.get("columns", "*")
        where_clause = params.get("where_clause", "")
        order_by = params.get("order_by", "")
        limit = params.get("limit")
        offset = params.get("offset")
        
        if isinstance(columns, list):
            columns_str = ", ".join(columns)
        else:
            columns_str = columns
        
        query = f"SELECT {columns_str} FROM {table_name}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"
        
        return await pg_client.fetch_all(query)
    
    async def _handle_upsert(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle UPSERT operation."""
        table_name = params["table_name"]
        data = params["data"]
        conflict_columns = params["conflict_columns"]
        
        if isinstance(data, dict):
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ", ".join([f"${i+1}" if pg_client.client_type == "asyncpg" else "%s" for i in range(len(values))])
            
            # Create update clause for conflict resolution
            update_clauses = []
            for col in columns:
                if col not in conflict_columns:
                    update_clauses.append(f"{col} = EXCLUDED.{col}")
            
            query = f"""
            INSERT INTO {table_name} ({', '.join(columns)}) 
            VALUES ({placeholders})
            ON CONFLICT ({', '.join(conflict_columns)})
            DO UPDATE SET {', '.join(update_clauses)}
            """
            
            await pg_client.execute_query(query, tuple(values))
        
        return f"Upsert completed for {table_name}"
    
    # Bulk operation handlers
    async def _handle_bulk_insert(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> int:
        """Handle BULK_INSERT operation."""
        table_name = params["table_name"]
        columns = params["columns"]
        data = params["data"]
        
        return await pg_client.bulk_insert(table_name, columns, data)
    
    async def _handle_copy_from(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> int:
        """Handle COPY_FROM operation."""
        table_name = params["table_name"]
        columns = params["columns"]
        data = params["data"]
        
        return await pg_client.copy_from(table_name, columns, data)
    
    async def _handle_copy_to(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle COPY_TO operation."""
        table_name = params["table_name"]
        columns = params["columns"]
        format_type = params.get("format", "TEXT")
        delimiter = params.get("delimiter", "\t")
        header = params.get("header", False)
        
        copy_options = []
        if format_type != "TEXT":
            copy_options.append(f"FORMAT {format_type}")
        if delimiter != "\t":
            copy_options.append(f"DELIMITER '{delimiter}'")
        if header:
            copy_options.append("HEADER")
        
        options_str = f" WITH ({', '.join(copy_options)})" if copy_options else ""
        
        if isinstance(columns, list):
            columns_str = f"({', '.join(columns)})"
        else:
            columns_str = f"({columns})"
        
        query = f"COPY {table_name} {columns_str} TO STDOUT{options_str}"
        
        # For demonstration, we'll return the query
        # In practice, this would stream data out
        return f"Copy query prepared: {query}"
    
    # Database operation handlers
    async def _handle_create_database(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle CREATE_DATABASE operation."""
        database_name = params["database_name"]
        owner = params.get("owner")
        template = params.get("template")
        encoding = params.get("encoding")
        
        query = f"CREATE DATABASE {database_name}"
        
        options = []
        if owner:
            options.append(f"OWNER {owner}")
        if template:
            options.append(f"TEMPLATE {template}")
        if encoding:
            options.append(f"ENCODING '{encoding}'")
        
        if options:
            query += f" WITH {' '.join(options)}"
        
        await pg_client.execute_query(query)
        return f"Database {database_name} created"
    
    async def _handle_drop_database(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle DROP_DATABASE operation."""
        database_name = params["database_name"]
        
        query = f"DROP DATABASE {database_name}"
        await pg_client.execute_query(query)
        return f"Database {database_name} dropped"
    
    async def _handle_list_databases(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle LIST_DATABASES operation."""
        query = """
        SELECT datname as database_name, datowner, pg_encoding_to_char(encoding) as encoding
        FROM pg_database 
        WHERE datistemplate = false
        ORDER BY datname
        """
        return await pg_client.fetch_all(query)
    
    # Schema operation handlers
    async def _handle_create_schema(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle CREATE_SCHEMA operation."""
        schema_name = params["schema_name"]
        owner = params.get("owner")
        
        query = f"CREATE SCHEMA {schema_name}"
        if owner:
            query += f" AUTHORIZATION {owner}"
        
        await pg_client.execute_query(query)
        return f"Schema {schema_name} created"
    
    async def _handle_drop_schema(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle DROP_SCHEMA operation."""
        schema_name = params["schema_name"]
        cascade = params.get("cascade", False)
        
        query = f"DROP SCHEMA {schema_name}"
        if cascade:
            query += " CASCADE"
        
        await pg_client.execute_query(query)
        return f"Schema {schema_name} dropped"
    
    async def _handle_list_schemas(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> List[str]:
        """Handle LIST_SCHEMAS operation."""
        query = """
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
        ORDER BY schema_name
        """
        results = await pg_client.fetch_all(query)
        return [row['schema_name'] for row in results]
    
    # User operation handlers
    async def _handle_create_user(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle CREATE_USER operation."""
        username = params["username"]
        password_user = params.get("password_user")
        
        query = f"CREATE USER {username}"
        if password_user:
            query += f" WITH PASSWORD '{password_user}'"
        
        await pg_client.execute_query(query)
        return f"User {username} created"
    
    async def _handle_drop_user(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle DROP_USER operation."""
        username = params["username"]
        
        query = f"DROP USER {username}"
        await pg_client.execute_query(query)
        return f"User {username} dropped"
    
    async def _handle_alter_user(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle ALTER_USER operation."""
        username = params["username"]
        alterations = params["alterations"]
        
        if isinstance(alterations, dict):
            alter_parts = []
            for key, value in alterations.items():
                if key == "password":
                    alter_parts.append(f"PASSWORD '{value}'")
                else:
                    alter_parts.append(f"{key.upper()} {value}")
            alteration_str = " ".join(alter_parts)
        else:
            alteration_str = alterations
        
        query = f"ALTER USER {username} {alteration_str}"
        await pg_client.execute_query(query)
        return f"User {username} altered"
    
    async def _handle_grant_privileges(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle GRANT_PRIVILEGES operation."""
        privileges = params["privileges"]
        target = params["target"]
        username = params["username"]
        
        if isinstance(privileges, list):
            privileges_str = ", ".join(privileges)
        else:
            privileges_str = privileges
        
        query = f"GRANT {privileges_str} ON {target} TO {username}"
        await pg_client.execute_query(query)
        return f"Privileges granted to {username}"
    
    async def _handle_revoke_privileges(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle REVOKE_PRIVILEGES operation."""
        privileges = params["privileges"]
        target = params["target"]
        username = params["username"]
        
        if isinstance(privileges, list):
            privileges_str = ", ".join(privileges)
        else:
            privileges_str = privileges
        
        query = f"REVOKE {privileges_str} ON {target} FROM {username}"
        await pg_client.execute_query(query)
        return f"Privileges revoked from {username}"
    
    # Information operation handlers
    async def _handle_list_tables(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> List[str]:
        """Handle LIST_TABLES operation."""
        schema_name = params.get("schema_name", "public")
        return await pg_client.list_tables(schema_name)
    
    async def _handle_list_columns(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle LIST_COLUMNS operation."""
        table_name = params["table_name"]
        schema_name = params.get("schema_name", "public")
        return await pg_client.list_columns(table_name, schema_name)
    
    async def _handle_list_indexes(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle LIST_INDEXES operation."""
        table_name = params["table_name"]
        schema_name = params.get("schema_name", "public")
        
        query = """
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE schemaname = $1 AND tablename = $2
        """ if pg_client.client_type == "asyncpg" else """
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE schemaname = %s AND tablename = %s
        """
        
        return await pg_client.fetch_all(query, (schema_name, table_name))
    
    async def _handle_table_info(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TABLE_INFO operation."""
        table_name = params["table_name"]
        schema_name = params.get("schema_name", "public")
        
        # Get table information
        query = """
        SELECT table_name, table_type, table_schema
        FROM information_schema.tables 
        WHERE table_schema = $1 AND table_name = $2
        """ if pg_client.client_type == "asyncpg" else """
        SELECT table_name, table_type, table_schema
        FROM information_schema.tables 
        WHERE table_schema = %s AND table_name = %s
        """
        
        table_info = await pg_client.fetch_one(query, (schema_name, table_name))
        
        if table_info:
            # Get column information
            columns = await pg_client.list_columns(table_name, schema_name)
            table_info["columns"] = columns
        
        return table_info
    
    async def _handle_column_info(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle COLUMN_INFO operation."""
        table_name = params["table_name"]
        column_name = params["column_name"]
        schema_name = params.get("schema_name", "public")
        
        query = """
        SELECT column_name, data_type, is_nullable, column_default, 
               character_maximum_length, numeric_precision, numeric_scale
        FROM information_schema.columns 
        WHERE table_schema = $1 AND table_name = $2 AND column_name = $3
        """ if pg_client.client_type == "asyncpg" else """
        SELECT column_name, data_type, is_nullable, column_default, 
               character_maximum_length, numeric_precision, numeric_scale
        FROM information_schema.columns 
        WHERE table_schema = %s AND table_name = %s AND column_name = %s
        """
        
        return await pg_client.fetch_one(query, (schema_name, table_name, column_name))
    
    # Connection operation handlers
    async def _handle_test_connection(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle TEST_CONNECTION operation."""
        return await pg_client.test_connection()
    
    async def _handle_get_server_version(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle GET_SERVER_VERSION operation."""
        return await pg_client.get_server_version()
    
    async def _handle_get_database_size(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> int:
        """Handle GET_DATABASE_SIZE operation."""
        database_name = params["database_name"]
        return await pg_client.get_database_size(database_name)
    
    # Advanced operation handlers
    async def _handle_explain_query(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> List[str]:
        """Handle EXPLAIN_QUERY operation."""
        query = params["query"]
        query_params = tuple(params.get("params", []))
        analyze = params.get("analyze", False)
        
        return await pg_client.explain_query(query, query_params if query_params else None, analyze)
    
    async def _handle_analyze_query(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> List[str]:
        """Handle ANALYZE_QUERY operation."""
        query = params["query"]
        query_params = tuple(params.get("params", []))
        
        return await pg_client.explain_query(query, query_params if query_params else None, analyze=True)
    
    async def _handle_vacuum(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle VACUUM operation."""
        table_name = params.get("table_name")
        vacuum_full = params.get("vacuum_full", False)
        vacuum_freeze = params.get("vacuum_freeze", False)
        
        query = "VACUUM"
        if vacuum_full:
            query += " FULL"
        if vacuum_freeze:
            query += " FREEZE"
        if table_name:
            query += f" {table_name}"
        
        await pg_client.execute_query(query)
        return f"Vacuum completed"
    
    async def _handle_vacuum_analyze(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle VACUUM_ANALYZE operation."""
        table_name = params.get("table_name")
        
        query = "VACUUM ANALYZE"
        if table_name:
            query += f" {table_name}"
        
        await pg_client.execute_query(query)
        return f"Vacuum analyze completed"
    
    # Function operation handlers
    async def _handle_create_function(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle CREATE_FUNCTION operation."""
        function_name = params["function_name"]
        function_body = params["function_body"]
        return_type = params.get("return_type", "void")
        language = params.get("language", "SQL")
        
        query = f"""
        CREATE OR REPLACE FUNCTION {function_name}()
        RETURNS {return_type}
        LANGUAGE {language}
        AS $$
        {function_body}
        $$;
        """
        
        await pg_client.execute_query(query)
        return f"Function {function_name} created"
    
    async def _handle_drop_function(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle DROP_FUNCTION operation."""
        function_name = params["function_name"]
        
        query = f"DROP FUNCTION {function_name}"
        await pg_client.execute_query(query)
        return f"Function {function_name} dropped"
    
    async def _handle_call_function(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle CALL_FUNCTION operation."""
        function_name = params["function_name"]
        function_params = params.get("params", [])
        
        if function_params:
            params_str = ", ".join([str(p) for p in function_params])
            query = f"SELECT {function_name}({params_str})"
        else:
            query = f"SELECT {function_name}()"
        
        return await pg_client.fetch_one(query)
    
    async def _handle_call_procedure(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle CALL_PROCEDURE operation."""
        procedure_name = params["procedure_name"]
        procedure_params = params.get("params", [])
        
        if procedure_params:
            params_str = ", ".join([str(p) for p in procedure_params])
            query = f"CALL {procedure_name}({params_str})"
        else:
            query = f"CALL {procedure_name}()"
        
        await pg_client.execute_query(query)
        return f"Procedure {procedure_name} called"
    
    # Sequence operation handlers
    async def _handle_create_sequence(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle CREATE_SEQUENCE operation."""
        sequence_name = params["sequence_name"]
        increment = params.get("increment", 1)
        min_value = params.get("min_value")
        max_value = params.get("max_value")
        start_value = params.get("start_value", 1)
        
        query = f"CREATE SEQUENCE {sequence_name}"
        
        options = []
        options.append(f"INCREMENT BY {increment}")
        options.append(f"START WITH {start_value}")
        if min_value is not None:
            options.append(f"MINVALUE {min_value}")
        if max_value is not None:
            options.append(f"MAXVALUE {max_value}")
        
        if options:
            query += f" {' '.join(options)}"
        
        await pg_client.execute_query(query)
        return f"Sequence {sequence_name} created"
    
    async def _handle_drop_sequence(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> str:
        """Handle DROP_SEQUENCE operation."""
        sequence_name = params["sequence_name"]
        
        query = f"DROP SEQUENCE {sequence_name}"
        await pg_client.execute_query(query)
        return f"Sequence {sequence_name} dropped"
    
    async def _handle_nextval(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> int:
        """Handle NEXTVAL operation."""
        sequence_name = params["sequence_name"]
        
        query = f"SELECT nextval('{sequence_name}')"
        result = await pg_client.fetch_one(query)
        return result['nextval'] if result else None
    
    async def _handle_currval(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> int:
        """Handle CURRVAL operation."""
        sequence_name = params["sequence_name"]
        
        query = f"SELECT currval('{sequence_name}')"
        result = await pg_client.fetch_one(query)
        return result['currval'] if result else None
    
    async def _handle_setval(self, pg_client: PostgreSQLClientWrapper, params: Dict[str, Any]) -> int:
        """Handle SETVAL operation."""
        sequence_name = params["sequence_name"]
        value = params["value"]
        
        query = f"SELECT setval('{sequence_name}', {value})"
        result = await pg_client.fetch_one(query)
        return result['setval'] if result else None