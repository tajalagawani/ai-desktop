"""
Neon Node - Performs Neon serverless PostgreSQL database operations
with comprehensive options and error handling.
"""

import logging
import json
import time
import asyncio
import os
from typing import Dict, Any, List, Optional

import psycopg2
import psycopg2.extras
import psycopg2.pool
from psycopg2 import sql
from psycopg2.extensions import (
    ISOLATION_LEVEL_AUTOCOMMIT,
    ISOLATION_LEVEL_READ_COMMITTED,
    ISOLATION_LEVEL_SERIALIZABLE
)

# Assuming base_node.py is in the same directory or accessible via PYTHONPATH
try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    except ImportError:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )

# Configure logging
logger = logging.getLogger(__name__)

class NeonOperationType:
    """Neon operation types (string constants)."""
    EXECUTE_QUERY = "execute_query"; EXECUTE_TRANSACTION = "execute_transaction"
    CREATE_TABLE = "create_table"; INSERT_DATA = "insert_data"; SELECT_DATA = "select_data"
    UPDATE_DATA = "update_data"; DELETE_DATA = "delete_data"; UPSERT_DATA = "upsert_data"
    BULK_INSERT = "bulk_insert"; CREATE_INDEX = "create_index"; DROP_INDEX = "drop_index"
    CREATE_SCHEMA = "create_schema"; DROP_SCHEMA = "drop_schema"; ANALYZE_TABLE = "analyze_table"
    VACUUM_TABLE = "vacuum_table"; GET_TABLE_INFO = "get_table_info"
    GET_DATABASE_INFO = "get_database_info"; GET_SCHEMA_INFO = "get_schema_info"
    BACKUP_TABLE = "backup_table"; RESTORE_TABLE = "restore_table"

class NeonNode(BaseNode):
    node_type = "neon"
    """Node for interacting with Neon Serverless PostgreSQL Database."""

    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self.connection: Optional[psycopg2.extensions.connection] = None
        self._connection_args: Optional[Dict[str, Any]] = None

    def get_schema(self) -> NodeSchema:
        op_enum_vals = [v for k,v in vars(NeonOperationType).items() if not k.startswith('_') and isinstance(v,str)]
        logger.debug(f"NeonNode schema: operation enum values: {op_enum_vals}")
        return NodeSchema(
            node_type="neon", version="1.2.2", description="Neon PostgreSQL operations.",
            parameters=[
                NodeParameter(name="connection_string",type=NodeParameterType.STRING,description="DB connection string",required=False),
                NodeParameter(name="host",type=NodeParameterType.STRING,description="DB host",required=False),
                NodeParameter(name="database",type=NodeParameterType.STRING,description="DB name",required=False),
                NodeParameter(name="user",type=NodeParameterType.STRING,description="DB user",required=False),
                NodeParameter(name="password",type=NodeParameterType.SECRET,description="DB password",required=False),
                NodeParameter(name="port",type=NodeParameterType.NUMBER,description="DB port",required=False,default=5432),
                NodeParameter(name="sslmode",type=NodeParameterType.STRING,description="SSL mode",required=False,default="require",enum=["disable","allow","prefer","require","verify-ca","verify-full"]),
                NodeParameter(name="use_pooling",type=NodeParameterType.BOOLEAN,description="Use connection pooling",required=False,default=True),
                NodeParameter(name="pool_size",type=NodeParameterType.NUMBER,description="Min pool size",required=False,default=1),
                NodeParameter(name="max_pool_size",type=NodeParameterType.NUMBER,description="Max pool size",required=False,default=5),
                NodeParameter(name="connection_timeout",type=NodeParameterType.NUMBER,description="Connection timeout (s)",required=False,default=30),
                NodeParameter(name="operation",type=NodeParameterType.STRING,description="DB operation",required=True,enum=op_enum_vals),
                NodeParameter(name="query",type=NodeParameterType.STRING,description="SQL query",required=False),
                NodeParameter(name="parameters",type=NodeParameterType.ARRAY,description="Positional query params",required=False,default=[]),
                NodeParameter(name="named_parameters",type=NodeParameterType.OBJECT,description="Named query params",required=False,default={}),
                NodeParameter(name="queries",type=NodeParameterType.ARRAY,description="Queries for transaction",required=False,default=[]),
                NodeParameter(name="table_name",type=NodeParameterType.STRING,description="Table name",required=False),
                NodeParameter(name="schema_name",type=NodeParameterType.STRING,description="Schema name",required=False,default="public"),
                NodeParameter(name="columns",type=NodeParameterType.OBJECT,description="Cols for CREATE_TABLE (name:type_str)",required=False,default={}),
                NodeParameter(name="data",type=NodeParameterType.OBJECT,description="Data for INSERT/UPDATE (col:val)",required=False,default={}),
                NodeParameter(name="bulk_data",type=NodeParameterType.ARRAY,description="Data for BULK_INSERT",required=False,default=[]),
                NodeParameter(name="where_clause",type=NodeParameterType.STRING,description="WHERE clause ('id=%s')",required=False),
                NodeParameter(name="where_parameters",type=NodeParameterType.ARRAY,description="Params for WHERE",required=False,default=[]),
                NodeParameter(name="conflict_columns",type=NodeParameterType.ARRAY,description="Cols for ON CONFLICT (UPSERT)",required=False,default=[]),
                NodeParameter(name="index_name",type=NodeParameterType.STRING,description="Index name",required=False),
                NodeParameter(name="index_columns",type=NodeParameterType.ARRAY,description="Cols for CREATE_INDEX",required=False,default=[]),
                NodeParameter(name="unique_index",type=NodeParameterType.BOOLEAN,description="Create unique index",required=False,default=False),
                NodeParameter(name="cascade",type=NodeParameterType.BOOLEAN,description="Use CASCADE (DROP_SCHEMA)",required=False,default=False),
                NodeParameter(name="full_vacuum",type=NodeParameterType.BOOLEAN,description="Perform FULL vacuum",required=False,default=False),
                NodeParameter(name="backup_table_name",type=NodeParameterType.STRING,description="Backup table name/restore source",required=False),
                NodeParameter(name="truncate_first",type=NodeParameterType.BOOLEAN,description="Truncate before RESTORE_TABLE",required=False,default=True),
                NodeParameter(name="fetch_size",type=NodeParameterType.NUMBER,description="Rows to fetch (-1 all)",required=False,default=-1),
                NodeParameter(name="return_dict",type=NodeParameterType.BOOLEAN,description="Return results as dicts",required=False,default=True),
                NodeParameter(name="limit",type=NodeParameterType.NUMBER,description="LIMIT for SELECT_DATA",required=False),
                NodeParameter(name="offset",type=NodeParameterType.NUMBER,description="OFFSET for SELECT_DATA",required=False),
                NodeParameter(name="order_by",type=NodeParameterType.STRING,description="ORDER BY for SELECT_DATA",required=False),
                NodeParameter(name="isolation_level",type=NodeParameterType.STRING,description="Transaction isolation level",required=False,default="read_committed",enum=["autocommit","read_committed","serializable"]),
                NodeParameter(name="rollback_on_error",type=NodeParameterType.BOOLEAN,description="Rollback Tx on error",required=False,default=True),
            ],
            outputs={"status":NodeParameterType.STRING,"data":NodeParameterType.ANY,"error":NodeParameterType.STRING,"rows_affected":NodeParameterType.NUMBER,"execution_time":NodeParameterType.NUMBER,"row_count":NodeParameterType.NUMBER,"columns":NodeParameterType.ARRAY,"query_stats":NodeParameterType.OBJECT},
            tags=["database","postgresql","neon","sql"]
        )

    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        raw_params = node_data.get("params", {})
        operation = raw_params.get("operation")
        logger.debug(f"NeonNode validate_custom: operation={operation}")
        if not operation: raise NodeValidationError("Operation parameter is missing.")
        if not raw_params.get("connection_string") and not (raw_params.get("host") and raw_params.get("database") and raw_params.get("user") and raw_params.get("password")):
            raise NodeValidationError("Connection details (string or host/db/user/pass) required.")
        
        if operation == NeonOperationType.EXECUTE_QUERY and not raw_params.get("query"): raise NodeValidationError("'query' required for 'execute_query'.")
        if operation == NeonOperationType.EXECUTE_TRANSACTION and not raw_params.get("queries"): raise NodeValidationError("'queries' list required for 'execute_transaction'.")
        
        table_required_ops = [
            NeonOperationType.CREATE_TABLE, NeonOperationType.INSERT_DATA, NeonOperationType.SELECT_DATA,
            NeonOperationType.UPDATE_DATA, NeonOperationType.DELETE_DATA, NeonOperationType.UPSERT_DATA,
            NeonOperationType.BULK_INSERT, NeonOperationType.ANALYZE_TABLE, NeonOperationType.VACUUM_TABLE,
            NeonOperationType.GET_TABLE_INFO, NeonOperationType.BACKUP_TABLE, NeonOperationType.RESTORE_TABLE,
            NeonOperationType.CREATE_INDEX
        ]
        if operation in table_required_ops and not raw_params.get("table_name"):
            raise NodeValidationError(f"'table_name' is required for operation '{operation}'.")

        if operation == NeonOperationType.CREATE_TABLE and not raw_params.get("columns"): raise NodeValidationError("'columns' required for 'create_table'.")
        if operation == NeonOperationType.UPSERT_DATA and not raw_params.get("conflict_columns"): raise NodeValidationError("'conflict_columns' list required for 'upsert_data'.")
        if operation == NeonOperationType.BULK_INSERT and (not raw_params.get("bulk_data") or not isinstance(raw_params.get("bulk_data"), list) or not raw_params.get("bulk_data")):
            raise NodeValidationError("'bulk_data' (non-empty list of dicts) required for 'bulk_insert'.")
        if operation == NeonOperationType.CREATE_INDEX:
            if not raw_params.get("index_name"): raise NodeValidationError("'index_name' required for 'create_index'.")
            if not raw_params.get("index_columns") or not isinstance(raw_params.get("index_columns"), list) or not raw_params.get("index_columns"):
                 raise NodeValidationError("'index_columns' (non-empty list) required for 'create_index'.")
        if operation == NeonOperationType.DROP_INDEX and not raw_params.get("index_name"): raise NodeValidationError("'index_name' required for 'drop_index'.")
        if operation == NeonOperationType.RESTORE_TABLE and not raw_params.get("backup_table_name"): raise NodeValidationError("'backup_table_name' required for 'restore_table'.")
        return raw_params
    
    def validate_schema(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override parent validation to ensure parameters are passed through correctly."""
        logger.debug(f"NeonNode validate_schema override: input keys {list(node_data.keys())}")
        params = node_data.get("params", {})
        logger.debug(f"NeonNode validate_schema override: params {params}")
        
        # Perform basic validation
        operation = params.get("operation")
        if not operation:
            raise NodeValidationError("Operation parameter is required")
        
        # Validate operation is in allowed values
        allowed_ops = [v for k,v in vars(NeonOperationType).items() if not k.startswith('_') and isinstance(v,str)]
        if operation not in allowed_ops:
            raise NodeValidationError(f"Operation '{operation}' not in allowed values: {allowed_ops}")
            
        # Validate required parameters for operation
        if operation == NeonOperationType.EXECUTE_QUERY and not params.get("query"):
            raise NodeValidationError("'query' required for 'execute_query'")
            
        # Return the full params dictionary
        logger.debug(f"NeonNode validate_schema override: returning {params}")
        return params
    
    def log_safe_data(self, data):
        """Safely log data by truncating or masking sensitive information."""
        if isinstance(data, dict):
            return {k: "***" if "password" in k.lower() or "secret" in k.lower() or "token" in k.lower() else v for k, v in data.items()}
        elif isinstance(data, list) and len(data) > 10:
            return data[:10] + ["... truncated"]
        return data

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.debug(f"NeonNode DEBUG: Input node_data keys: {list(node_data.keys())}")
            logger.debug(f"NeonNode DEBUG: Input params: {node_data.get('params', {})}")
            params = self.validate_schema(node_data) # Returns validated parameters dict
            logger.debug(f"NeonNode DEBUG: After validate_schema, params: {params}")
            operation = params.get("operation")
            logger.debug(f"NeonNode DEBUG: operation value: {operation}")
            if operation is None: raise ValueError("Operation parameter is unexpectedly None after validation.")

            # Determine current connection arguments based on input params and schema defaults
            current_call_conn_args_temp = { k: params.get(k) for k in ["connection_string","host","database","user","password","port","sslmode","use_pooling","pool_size","max_pool_size","connection_timeout"] if params.get(k) is not None }
            schema_params_dict = {p.name: p for p in self.get_schema().parameters}
            final_effective_conn_args = {}
            for arg_name in ["connection_string","host","database","user","password","port","sslmode","use_pooling","pool_size","max_pool_size","connection_timeout"]:
                if arg_name in current_call_conn_args_temp:
                    final_effective_conn_args[arg_name] = current_call_conn_args_temp[arg_name]
                elif arg_name in schema_params_dict and schema_params_dict[arg_name].default is not None:
                    final_effective_conn_args[arg_name] = schema_params_dict[arg_name].default


            needs_init = False
            if not self._connection_args: 
                needs_init = True
            elif self._connection_args != final_effective_conn_args: # Compare with fully resolved effective args
                logger.info("Connection parameters changed, re-initializing connection.")
                needs_init = True
            elif self.connection and self.connection.closed: 
                logger.warning("Single connection found closed, re-initializing.")
                needs_init = True
            elif self.connection_pool and self.connection_pool.closed: 
                logger.warning("Connection pool found closed, re-initializing.")
                needs_init = True
            
            if needs_init:
                # _initialize_connection will use 'params' to set self._connection_args correctly
                await asyncio.to_thread(self._initialize_connection, params)


            op_map = {
                NeonOperationType.EXECUTE_QUERY: self.operation_execute_query, NeonOperationType.EXECUTE_TRANSACTION: self.operation_execute_transaction,
                NeonOperationType.CREATE_TABLE: self.operation_create_table, NeonOperationType.INSERT_DATA: self.operation_insert_data, 
                NeonOperationType.SELECT_DATA: self.operation_select_data, NeonOperationType.UPDATE_DATA: self.operation_update_data, 
                NeonOperationType.DELETE_DATA: self.operation_delete_data, NeonOperationType.UPSERT_DATA: self.operation_upsert_data,
                NeonOperationType.BULK_INSERT: self.operation_bulk_insert, NeonOperationType.CREATE_INDEX: self.operation_create_index, 
                NeonOperationType.DROP_INDEX: self.operation_drop_index, NeonOperationType.CREATE_SCHEMA: self.operation_create_schema, 
                NeonOperationType.DROP_SCHEMA: self.operation_drop_schema, NeonOperationType.ANALYZE_TABLE: self.operation_analyze_table,
                NeonOperationType.VACUUM_TABLE: self.operation_vacuum_table, NeonOperationType.GET_TABLE_INFO: self.operation_get_table_info,
                NeonOperationType.GET_DATABASE_INFO: self.operation_get_database_info, NeonOperationType.GET_SCHEMA_INFO: self.operation_get_schema_info,
                NeonOperationType.BACKUP_TABLE: self.operation_backup_table, NeonOperationType.RESTORE_TABLE: self.operation_restore_table,
            }
            if operation_func := op_map.get(operation):
                return await operation_func(params) # Pass validated params
            else:
                raise ValueError(f"Unsupported database operation: {operation}")
        except NodeValidationError as ve:
            logger.warning(f"NeonNode Validation: {ve}")
            return {"status": "error", "error": f"Validation Error: {str(ve)}", "rows_affected":0, "execution_time":0, "row_count":0, "columns":[], "query_stats":None}
        except psycopg2.pool.PoolError as pool_err:
            logger.error(f"Connection Pool Error: {pool_err}", exc_info=True)
            return {"status": "error", "error": f"Connection Pool Error: {str(pool_err)}", "rows_affected":0, "execution_time":0, "row_count":0, "columns":[], "query_stats":None}
        except psycopg2.Error as db_err:
            err_diag = db_err.diag.message_primary if hasattr(db_err, 'diag') and db_err.diag else str(db_err)
            logger.error(f"DB Error (Code: {getattr(db_err, 'pgcode', 'N/A')}): {err_diag}", exc_info=False)
            return {"status": "error", "error": f"Database Error: {err_diag}", "rows_affected":0, "execution_time":0, "row_count":0, "columns":[], "query_stats":None}
        except ValueError as val_err:
            logger.error(f"NeonNode Value Error: {val_err}", exc_info=True)
            return {"status": "error", "error": f"Execution Error: {str(val_err)}", "rows_affected":0, "execution_time":0, "row_count":0, "columns":[], "query_stats":None}
        except Exception as e:
            logger.error(f"Unhandled NeonNode Error: {e}", exc_info=True)
            return {"status": "error", "error": f"Unexpected Error: {str(e)}", "rows_affected":0, "execution_time":0, "row_count":0, "columns":[], "query_stats":None}

    def _store_connection_args(self, params: Dict[str, Any]):
        """Stores relevant connection parameters from validated params, applying schema defaults."""
        self._connection_args = {}
        schema_params_dict = {p.name: p for p in self.get_schema().parameters}
        
        conn_arg_names = ["connection_string","host","database","user","password","port","sslmode","use_pooling","pool_size","max_pool_size","connection_timeout"]
        
        for arg_name in conn_arg_names:
            if params.get(arg_name) is not None:
                self._connection_args[arg_name] = params.get(arg_name)
            elif arg_name in schema_params_dict and schema_params_dict[arg_name].default is not None:
                 self._connection_args[arg_name] = schema_params_dict[arg_name].default
        
        # Ensure correct types for numeric args, especially from defaults
        for num_field in ["port", "pool_size", "max_pool_size", "connection_timeout"]:
            if num_field in self._connection_args and self._connection_args[num_field] is not None:
                try: self._connection_args[num_field] = int(self._connection_args[num_field])
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {num_field} '{self._connection_args[num_field]}' to int. Using schema default or None.")
                    # Fallback to schema default if conversion fails
                    self._connection_args[num_field] = schema_params_dict[num_field].default if num_field in schema_params_dict else None


    def _initialize_connection(self, params: Dict[str, Any]): # Sync
        self._store_connection_args(params) 

        if self.connection_pool: self.connection_pool.closeall()
        if self.connection and not self.connection.closed: self.connection.close()
        self.connection_pool, self.connection = None, None

        args = self._connection_args
        if not args: raise ValueError("Cannot initialize connection without stored arguments (logic error).")
        
        conn_str = args.get("connection_string")
        if not conn_str:
            # Ensure all necessary parts are available in args for building connection string
            # These should have been defaulted by _store_connection_args if not in params
            required_for_build = {"user", "password", "host", "database", "port", "sslmode"}
            if not all(args.get(k) is not None for k in required_for_build):
                missing_keys = [k for k in required_for_build if args.get(k) is None]
                raise ValueError(f"Incomplete connection details for string build. Missing/None: {missing_keys}. Current args: {args}")
            conn_str = "postgresql://{user}:{password}@{host}:{port}/{database}?sslmode={sslmode}".format(**args)
        
        try:
            timeout = args["connection_timeout"] # Should be int and exist from _store_connection_args
            if args.get("use_pooling"): 
                self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                    args["pool_size"], args["max_pool_size"], conn_str, connect_timeout=timeout)
                with self.connection_pool.getconn(): pass
                logger.info(f"Neon pool initialized (min:{args['pool_size']}-max:{args['max_pool_size']}).")
            else:
                self.connection = psycopg2.connect(conn_str, connect_timeout=timeout)
                with self.connection.cursor() as c: c.execute("SELECT 1")
                logger.info("Neon single connection initialized.")
        except Exception as e:
            self._connection_args = None 
            raise ValueError(f"DB Conn Init Failed: {e}")

    def _ensure_connection(self): # Sync
        if not self.connection_pool and not self.connection:
            if not self._connection_args: raise ValueError("No connection args to init.")
            self._initialize_connection(self._connection_args) # Use stored args (which are a full param dict)
        elif self.connection and self.connection.closed:
            logger.warning("Single conn closed, re-init.")
            if not self._connection_args: raise ValueError("No connection args to re-init.")
            self._initialize_connection(self._connection_args)
        elif self.connection_pool and self.connection_pool.closed:
            logger.warning("Connection pool found closed, re-initializing.")
            if not self._connection_args: raise ValueError("No connection args to re-init pool.")
            self._initialize_connection(self._connection_args)
    
    def _get_connection(self): # Sync
        self._ensure_connection()
        if self.connection_pool: return self.connection_pool.getconn()
        if self.connection: 
            if self.connection.closed: raise ValueError("DB conn closed unexpectedly.")
            return self.connection
        raise ValueError("DB conn not available.")

    def _return_connection(self, conn): # Sync
        if self.connection_pool and conn and not conn.closed:
            self.connection_pool.putconn(conn)

    def _get_isolation_level(self, level_str: Optional[str]): # Sync
        if not level_str: return ISOLATION_LEVEL_READ_COMMITTED
        lvls = {"autocommit":ISOLATION_LEVEL_AUTOCOMMIT,"read_committed":ISOLATION_LEVEL_READ_COMMITTED,"serializable":ISOLATION_LEVEL_SERIALIZABLE}
        return lvls.get(str(level_str).lower(), ISOLATION_LEVEL_READ_COMMITTED)

    async def _async_get_connection(self): return await asyncio.to_thread(self._get_connection)
    async def _async_return_connection(self, conn): await asyncio.to_thread(self._return_connection, conn)

    async def _execute_query(self, query: str, parameters: Optional[List]=None, named_parameters: Optional[Dict]=None, fetch_size: int = -1, return_dict: bool = True) -> Dict[str, Any]:
        start_time, conn, cursor = time.time(), None, None
        try:
            conn = await self._async_get_connection()
            def db_ops(curr_conn):
                nonlocal cursor
                curr_cursor = curr_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor if return_dict else None)
                cursor = curr_cursor
                if named_parameters: curr_cursor.execute(query, named_parameters)
                elif parameters: curr_cursor.execute(query, parameters)
                else: curr_cursor.execute(query)
                _d, _c, _ra = [], [], curr_cursor.rowcount if curr_cursor.rowcount is not None else 0
                if curr_cursor.description:
                    res = curr_cursor.fetchall() if fetch_size == -1 else curr_cursor.fetchmany(int(fetch_size))
                    _d = [dict(r) for r in res] if return_dict and res else ([list(r) for r in res] if res else [])
                    _c = [d[0] for d in curr_cursor.description]
                if curr_conn.isolation_level != ISOLATION_LEVEL_AUTOCOMMIT: curr_conn.commit()
                return _d, _c, _ra
            data, cols, rows_aff = await asyncio.to_thread(db_ops, conn)
            exec_time = time.time() - start_time
            return {"data":data,"rows_affected":rows_aff,"execution_time":exec_time,"row_count":len(data),"columns":cols,
                    "query_stats":{"query":query,"parameters":self.log_safe_data(parameters or named_parameters),"execution_time_ms":exec_time*1000}}
        except psycopg2.Error as db_err:
            if conn and not conn.closed and conn.isolation_level!=ISOLATION_LEVEL_AUTOCOMMIT: await asyncio.to_thread(conn.rollback)
            raise 
        except Exception as e:
            if conn and not conn.closed and conn.isolation_level!=ISOLATION_LEVEL_AUTOCOMMIT: await asyncio.to_thread(conn.rollback)
            raise ValueError(f"Query exec error: {e}") 
        finally:
            if cursor: await asyncio.to_thread(cursor.close)
            if conn: await self._async_return_connection(conn)

    async def operation_execute_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug(f"NEON_NODE operation_execute_query: Received params dict: {json.dumps(params, default=str)}")
        received_sql_parameters = params.get("parameters")
        logger.debug(f"NEON_NODE operation_execute_query: Value for params.get('parameters'): {received_sql_parameters} (type: {type(received_sql_parameters)})")
        
        result = await self._execute_query(
            params["query"],
            received_sql_parameters, # Use the logged variable
            params.get("named_parameters"),
            int(params.get("fetch_size", -1)),
            params.get("return_dict", True)
        )
        return {"status": "success", **result, "error": None}

    async def operation_execute_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        queries_input = params.get("queries", [])
        if not isinstance(queries_input, list): raise NodeValidationError("'queries' must be a list.")
        start_time, conn, cursor, orig_iso = time.time(), None, None, None
        try:
            conn = await self._async_get_connection()
            def db_tx_ops(curr_conn):
                nonlocal cursor, orig_iso
                orig_iso = curr_conn.isolation_level
                curr_conn.set_isolation_level(self._get_isolation_level(params.get("isolation_level")))
                curr_cursor = curr_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cursor = curr_cursor
                _res_list, _total_ra = [], 0
                for idx, item in enumerate(queries_input):
                    q, qp, qnp = (item.get("query") if isinstance(item,dict) else item), (item.get("parameters",[]) if isinstance(item,dict) else []), (item.get("named_parameters",{}) if isinstance(item,dict) else {})
                    if not q: raise ValueError(f"Empty query in Tx item {idx}.")
                    if qnp: curr_cursor.execute(q, qnp)
                    elif qp: curr_cursor.execute(q, qp)
                    else: curr_cursor.execute(q)
                    ra = curr_cursor.rowcount if curr_cursor.rowcount is not None else 0
                    _total_ra += ra
                    _d, _c = ([dict(r) for r in curr_cursor.fetchall()] if curr_cursor.description else []), ([d[0] for d in curr_cursor.description] if curr_cursor.description else [])
                    _res_list.append({"query":q,"data":_d,"rows_affected":ra,"columns":_c})
                if curr_conn.isolation_level != ISOLATION_LEVEL_AUTOCOMMIT: curr_conn.commit()
                return _res_list, _total_ra
            
            res_list, total_ra = await asyncio.to_thread(db_tx_ops, conn)
            exec_time = time.time() - start_time
            return {"status":"success","data":res_list,"error":None,"rows_affected":total_ra,"execution_time":exec_time,
                    "row_count":sum(len(r["data"]) for r in res_list),"columns":[r["columns"] for r in res_list],
                    "query_stats":{"queries_executed":len(queries_input),"total_execution_time_ms":exec_time*1000,"isolation_level":params.get("isolation_level")}}
        except Exception as e:
            if conn and not conn.closed and params.get("rollback_on_error",True) and conn.isolation_level!=ISOLATION_LEVEL_AUTOCOMMIT:
                await asyncio.to_thread(conn.rollback)
            raise 
        finally:
            if cursor: await asyncio.to_thread(cursor.close)
            if conn:
                if orig_iso is not None and not conn.closed: await asyncio.to_thread(conn.set_isolation_level, orig_iso)
                await self._async_return_connection(conn)

    async def _get_composed_query_string(self, query_sql: sql.Composed) -> str:
        conn_temp = await self._async_get_connection()
        try: return await asyncio.to_thread(query_sql.as_string, conn_temp)
        finally: await self._async_return_connection(conn_temp)

    async def _simple_ddl_query_exec(self, query_sql: sql.Composed, op_params: Dict[str, Any]) -> Dict[str, Any]:
        query_str = await self._get_composed_query_string(query_sql)
        # For DDL, pass through all original params so execute_query can log them if needed,
        # but set query and return_dict specifically.
        exec_params = {**op_params, "query": query_str, "return_dict": False, "parameters": None, "named_parameters": None}
        return await self.operation_execute_query(exec_params)

    async def operation_create_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cols_def = params.get("columns", {})
        if not cols_def: raise ValueError("Columns definition missing.")
        col_items = [sql.SQL("{} {}").format(sql.Identifier(n), sql.SQL(t)) for n,t in cols_def.items()]
        q_sql = sql.SQL("CREATE TABLE {s}.{t} ({c})").format(s=sql.Identifier(params["schema_name"]),t=sql.Identifier(params["table_name"]),c=sql.SQL(", ").join(col_items))
        return await self._simple_ddl_query_exec(q_sql, params)

    async def operation_insert_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        data_map = params.get("data",{})
        if not data_map: raise ValueError("Data map missing.")
        cols = list(data_map.keys())
        q_sql = sql.SQL("INSERT INTO {s}.{t} ({c}) VALUES ({p}) RETURNING *").format(
            s=sql.Identifier(params["schema_name"]),t=sql.Identifier(params["table_name"]),
            c=sql.SQL(", ").join(map(sql.Identifier,cols)),p=sql.SQL(", ").join(sql.Placeholder(k) for k in cols))
        q_str = await self._get_composed_query_string(q_sql)
        return await self.operation_execute_query({**params, "query":q_str, "named_parameters": data_map})


    async def operation_select_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        parts = [sql.SQL("SELECT * FROM {s}.{t}").format(s=sql.Identifier(params["schema_name"]),t=sql.Identifier(params["table_name"]))]
        curr_q_params = list(params.get("where_parameters",[]))
        if wc:=params.get("where_clause"):parts.append(sql.SQL("WHERE ")+sql.SQL(wc))
        if ob:=params.get("order_by"):parts.append(sql.SQL("ORDER BY ")+sql.SQL(ob))
        if (lim:=params.get("limit")) is not None:parts.append(sql.SQL("LIMIT %s"));curr_q_params.append(int(lim))
        if (off:=params.get("offset")) is not None:parts.append(sql.SQL("OFFSET %s"));curr_q_params.append(int(off))
        q_str = await self._get_composed_query_string(sql.SQL(" ").join(parts))
        # Pass all relevant params, including those used by _execute_query like fetch_size, return_dict
        exec_params = {
            **params, # Includes connection details, return_dict, fetch_size etc.
            "query":q_str,
            "parameters":curr_q_params,
        }
        return await self.operation_execute_query(exec_params)

    async def operation_update_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        data_map=params.get("data",{})
        if not data_map: raise ValueError("Data map missing.")
        if not params.get("where_clause"): raise ValueError("WHERE clause required.")
        set_cls=[sql.SQL("{} = %s").format(sql.Identifier(k)) for k in data_map.keys()]
        final_q_params=list(data_map.values())+params.get("where_parameters",[])
        q_sql=sql.SQL("UPDATE {s}.{t} SET {sc} WHERE {wc} RETURNING *").format(s=sql.Identifier(params["schema_name"]),t=sql.Identifier(params["table_name"]),sc=sql.SQL(", ").join(set_cls),wc=sql.SQL(params["where_clause"]))
        q_str=await self._get_composed_query_string(q_sql)
        return await self.operation_execute_query({**params, "query":q_str,"parameters":final_q_params})

    async def operation_delete_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not params.get("where_clause"): raise ValueError("WHERE clause required.")
        q_sql=sql.SQL("DELETE FROM {s}.{t} WHERE {wc} RETURNING *").format(s=sql.Identifier(params["schema_name"]),t=sql.Identifier(params["table_name"]),wc=sql.SQL(params["where_clause"]))
        q_str=await self._get_composed_query_string(q_sql)
        return await self.operation_execute_query({**params, "query":q_str,"parameters":params.get("where_parameters",[])})

    async def operation_upsert_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        data_map,conf_cols=params.get("data",{}),params.get("conflict_columns",[])
        if not data_map or not conf_cols: raise ValueError("Data and conflict_columns required.")
        ins_cols=list(data_map.keys())
        upd_set=sql.SQL(", ").join([sql.SQL("{c} = EXCLUDED.{c}").format(c=sql.Identifier(c)) for c in ins_cols])
        q_sql=sql.SQL("INSERT INTO {s}.{t} ({c_sql}) VALUES ({p_sql}) ON CONFLICT ({cf_sql}) DO UPDATE SET {us_sql} RETURNING *").format(
            s=sql.Identifier(params["schema_name"]),t=sql.Identifier(params["table_name"]),
            c_sql=sql.SQL(", ").join(map(sql.Identifier,ins_cols)),p_sql=sql.SQL(", ").join(sql.Placeholder()*len(ins_cols)),
            cf_sql=sql.SQL(", ").join(map(sql.Identifier,conf_cols)),us_sql=upd_set)
        q_str=await self._get_composed_query_string(q_sql)
        return await self.operation_execute_query({**params, "query":q_str,"parameters":list(data_map.values())})

    async def operation_bulk_insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        bulk_data = params.get("bulk_data", [])
        if not bulk_data or not isinstance(bulk_data, list) or not all(isinstance(d, dict) for d in bulk_data):
            raise NodeValidationError("bulk_data must be a non-empty list of dictionaries.")
        cols = list(bulk_data[0].keys())
        start_time, conn = time.time(), None
        try:
            conn = await self._async_get_connection()
            def db_bulk_ops_sync(current_conn):
                with current_conn.cursor() as current_cursor:
                    cols_sql = sql.SQL(", ").join(map(sql.Identifier, cols))
                    placeholders_sql = sql.SQL(", ").join([sql.Placeholder()] * len(cols))
                    query_template_sql = sql.SQL("INSERT INTO {s}.{t} ({c_sql}) VALUES ({p_sql})").format(
                        s=sql.Identifier(params["schema_name"]), t=sql.Identifier(params["table_name"]),
                        c_sql=cols_sql, p_sql=placeholders_sql)
                    query_str_template = query_template_sql.as_string(current_conn)
                    values_list = [[row.get(col) for col in cols] for row in bulk_data]
                    psycopg2.extras.execute_batch(current_cursor, query_str_template, values_list, page_size=100)
                    if current_conn.isolation_level != ISOLATION_LEVEL_AUTOCOMMIT: current_conn.commit()
            await asyncio.to_thread(db_bulk_ops_sync, conn)
            exec_time = time.time() - start_time; inserted_count = len(bulk_data)
            return {"status": "success", "data": {"inserted_rows_count": inserted_count}, "rows_affected": inserted_count, "execution_time": exec_time, "columns": cols, "query_stats": {"bulk_insert_size": inserted_count}, "error": None}
        except Exception as e:
            if conn and not conn.closed and conn.isolation_level != ISOLATION_LEVEL_AUTOCOMMIT: await asyncio.to_thread(conn.rollback)
            raise ValueError(f"Bulk insert operation failed: {e}")
        finally:
            if conn: await self._async_return_connection(conn)

    async def operation_create_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        idx_cols_sql = sql.SQL(", ").join(map(sql.Identifier, params["index_columns"]))
        unique_sql = sql.SQL("UNIQUE") if params.get("unique_index") else sql.SQL("")
        q_sql = sql.SQL("CREATE {uniq} INDEX {idx_name} ON {s}.{t} ({cols})").format(
            uniq=unique_sql, idx_name=sql.Identifier(params["index_name"]),
            s=sql.Identifier(params["schema_name"]), t=sql.Identifier(params["table_name"]),
            cols=idx_cols_sql)
        return await self._simple_ddl_query_exec(q_sql, params)

    async def operation_drop_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        q_sql=sql.SQL("DROP INDEX IF EXISTS {s}.{idx_name}").format(s=sql.Identifier(params["schema_name"]),idx_name=sql.Identifier(params["index_name"]))
        return await self._simple_ddl_query_exec(q_sql, params)

    async def operation_create_schema(self, params: Dict[str, Any]) -> Dict[str, Any]:
        q_sql=sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(params["schema_name"]))
        return await self._simple_ddl_query_exec(q_sql, params)

    async def operation_drop_schema(self, params: Dict[str, Any]) -> Dict[str, Any]:
        casc=sql.SQL("CASCADE") if params.get("cascade") else sql.SQL("")
        q_sql=sql.SQL("DROP SCHEMA IF EXISTS {s_name} {cas}").format(s_name=sql.Identifier(params["schema_name"]),cas=casc)
        return await self._simple_ddl_query_exec(q_sql, params)

    async def operation_analyze_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        q_sql=sql.SQL("ANALYZE {s}.{t}").format(s=sql.Identifier(params["schema_name"]),t=sql.Identifier(params["table_name"]))
        return await self._simple_ddl_query_exec(q_sql, params)

    async def operation_vacuum_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vac_type=sql.SQL("VACUUM FULL") if params.get("full_vacuum") else sql.SQL("VACUUM")
        q_sql=sql.SQL("{vac} {s}.{t}").format(vac=vac_type,s=sql.Identifier(params["schema_name"]),t=sql.Identifier(params["table_name"]))
        return await self._simple_ddl_query_exec(q_sql, params)

    async def _run_info_queries_transaction(self, queries_info_list: List[Dict], params_context: Dict) -> Dict[str, Any]:
        transaction_queries_for_op = [{"query": item["query"], "parameters": item.get("parameters", [])} for item in queries_info_list]
        transaction_payload = {**params_context, "queries": transaction_queries_for_op, "isolation_level": "read_committed"}
        transaction_result = await self.operation_execute_transaction(transaction_payload)
        if transaction_result.get("status") == "success":
            structured_data = {}
            for i, spec_item in enumerate(queries_info_list):
                query_name = spec_item.get("name", f"query_{i}")
                if i < len(transaction_result.get("data", [])):
                    structured_data[query_name] = transaction_result["data"][i].get("data", [])
                else: structured_data[query_name] = [] 
            transaction_result["data"] = structured_data
        return transaction_result

    async def operation_get_table_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        sch, tbl = params["schema_name"], params["table_name"]
        q_list = [
            {"name":"columns","query":"SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_schema=%s AND table_name=%s ORDER BY ordinal_position","parameters":[sch,tbl]},
            {"name":"indexes","query":"SELECT indexname, indexdef FROM pg_indexes WHERE schemaname=%s AND tablename=%s","parameters":[sch,tbl]},
            {"name":"constraints","query":"SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_schema=%s AND table_name=%s","parameters":[sch,tbl]},
            {"name":"stats","query":"SELECT n_live_tup,n_dead_tup,last_analyze,last_vacuum FROM pg_stat_user_tables WHERE schemaname=%s AND relname=%s","parameters":[sch,tbl]}
        ]
        return await self._run_info_queries_transaction(q_list, params)

    async def operation_get_database_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        q_list = [
            {"name":"version","query":"SELECT version()"},
            {"name":"current_db_details","query":"SELECT current_database() as db, current_user as user, inet_server_addr() as addr, inet_server_port() as port"},
            {"name":"db_size","query":"SELECT pg_size_pretty(pg_database_size(current_database())) as size"},
            {"name":"active_conns","query":"SELECT count(*) as count FROM pg_stat_activity WHERE state='active' AND datname=current_database()"},
            {"name":"schemas","query":"SELECT schema_name FROM information_schema.schemata WHERE schema_owner<>'postgres' AND schema_name NOT IN ('information_schema','pg_catalog','pg_toast') AND NOT schema_name LIKE 'pg_temp_%' ORDER BY schema_name"}
        ]
        return await self._run_info_queries_transaction(q_list, params)

    async def operation_get_schema_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        sch = params["schema_name"]
        q_list = [
            {"name":"tables_views","query":"SELECT table_name,table_type FROM information_schema.tables WHERE table_schema=%s ORDER BY table_type,table_name","parameters":[sch]},
            {"name":"routines","query":"SELECT routine_name,routine_type,data_type as return_type FROM information_schema.routines WHERE specific_schema=%s ORDER BY routine_type,routine_name","parameters":[sch]}
        ]
        return await self._run_info_queries_transaction(q_list, params)

    async def operation_backup_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        bak_name = params.get("backup_table_name", f"{params['table_name']}_bak_{int(time.time())}")
        q_sql = sql.SQL("CREATE TABLE {bs}.{bt} AS SELECT * FROM {ss}.{st}").format(
            bs=sql.Identifier(params["schema_name"]),bt=sql.Identifier(bak_name),
            ss=sql.Identifier(params["schema_name"]),st=sql.Identifier(params["table_name"]))
        return await self._simple_ddl_query_exec(q_sql, params)

    async def operation_restore_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ts,tt,ss,st = params["schema_name"],params["table_name"],params["schema_name"],params["backup_table_name"]
        tx_items_def = []
        if params.get("truncate_first",True): tx_items_def.append({"q_obj":sql.SQL("TRUNCATE TABLE {s}.{t}").format(s=sql.Identifier(ts),t=sql.Identifier(tt))})
        tx_items_def.append({"q_obj":sql.SQL("INSERT INTO {ts}.{tt} SELECT * FROM {ss}.{st}").format(ts=sql.Identifier(ts),tt=sql.Identifier(tt),ss=sql.Identifier(ss),st=sql.Identifier(st))})
        final_tx_items = []
        conn_tmp = await self._async_get_connection()
        try:
            for item_def in tx_items_def:
                final_tx_items.append({"query": await asyncio.to_thread(item_def["q_obj"].as_string, conn_tmp)})
        finally: await self._async_return_connection(conn_tmp)
        return await self.operation_execute_transaction({**params, "queries":final_tx_items, "isolation_level":"read_committed"})

    async def close(self):
        logger.debug(f"Closing resources for NeonNode instance {id(self)}...")
        if self.connection_pool: await asyncio.to_thread(self.connection_pool.closeall); self.connection_pool=None; logger.info("Neon pool closed.")
        if self.connection and not self.connection.closed: await asyncio.to_thread(self.connection.close); self.connection=None; logger.info("Neon single conn closed.")
        logger.debug("NeonNode resources closed.")

# === Register Node with Registry (happens during module import) ===
logger.debug("🔍 About to register node type 'neon'")
try:
    from base_node import NodeRegistry
    NodeRegistry.register("neon", NeonNode)
    logger.debug("✅ REGISTERED NeonNode as 'neon' at module level")
except Exception as e:
    logger.error(f"❌ ERROR registering NeonNode at module level: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Starting NeonNode test suite in __main__...")

    from base_node import NodeRegistry as GlobalNodeRegistry 
    GlobalNodeRegistry.register("neon", NeonNode) 
    logger.info(f"NeonNode registered. Current registry: {GlobalNodeRegistry.list_node_types()}")

    async def run_tests():
        print("=== NeonNode Test Suite ===")
        node = NeonNode() 

        CONNECTION_STRING = os.getenv("NEON_CONNECTION_STRING", "YOUR_NEON_CONNECTION_STRING_HERE") 
        if CONNECTION_STRING == "YOUR_NEON_CONNECTION_STRING_HERE": # Check actual placeholder
            logger.error("NEON_CONNECTION_STRING env var not set or is placeholder. Update it to run tests.")
            print("\nERROR: NEON_CONNECTION_STRING not set or is placeholder.")
            return

        neon_params_base = {
            "connection_string": CONNECTION_STRING, "use_pooling": True, "pool_size": 1,
            "max_pool_size": 2, "connection_timeout": 15,
        }
        try:
            await asyncio.to_thread(node._initialize_connection, neon_params_base)
            logger.info("Test suite node connection initialized using base params.")
        except Exception as e:
            logger.error(f"Initial connection setup for tests failed: {e}", exc_info=True)
            print(f"\nERROR: DB Connection for tests failed: {e}") # Print for visibility
            return

        TEST_SCHEMA = f"neon_test_s_{int(time.time())}" 
        TEST_TABLE = "users_main"
        TEST_TABLE_BACKUP = f"{TEST_TABLE}_bak"
        TEST_INDEX = f"idx_{TEST_TABLE}_age" # Note: Index name was idx_{TEST_TABLE}_age_name before, changed for consistency
        TEST_RESTORE_TARGET_TABLE = f"{TEST_TABLE}_restore"

        if not node._connection_args: 
             await asyncio.to_thread(node._initialize_connection, neon_params_base)

        drop_backup_table_query_str = await node._get_composed_query_string(sql.SQL("DROP TABLE IF EXISTS {schema}.{table} CASCADE;").format(schema=sql.Identifier(TEST_SCHEMA), table=sql.Identifier(TEST_TABLE_BACKUP)))
        drop_main_table_query_str = await node._get_composed_query_string(sql.SQL("DROP TABLE IF EXISTS {schema}.{table} CASCADE;").format(schema=sql.Identifier(TEST_SCHEMA), table=sql.Identifier(TEST_TABLE)))
        drop_restore_target_table_query_str = await node._get_composed_query_string(sql.SQL("DROP TABLE IF EXISTS {schema}.{table} CASCADE;").format(schema=sql.Identifier(TEST_SCHEMA), table=sql.Identifier(TEST_RESTORE_TARGET_TABLE)))
        create_restore_target_ddl = await node._get_composed_query_string(sql.SQL("CREATE TABLE {schema}.{table} (id SERIAL PRIMARY KEY, name VARCHAR(100), email VARCHAR(255), age INTEGER);").format(schema=sql.Identifier(TEST_SCHEMA), table=sql.Identifier(TEST_RESTORE_TARGET_TABLE)))

        test_cases = [
            {"name": "00. Initial Cleanup: Drop Test Schema", "node_input_params": {**neon_params_base, "operation": NeonOperationType.DROP_SCHEMA, "schema_name": TEST_SCHEMA, "cascade": True }, "expected_status": "success", "idempotent_cleanup": True },
            {"name": "01. Execute Simple Query (SELECT NOW())", "node_input_params": {**neon_params_base, "operation": NeonOperationType.EXECUTE_QUERY, "query": "SELECT NOW() as current_time, VERSION() as version"}, "expected_status": "success", "validation": lambda r: len(r.get("data",[])) > 0 and "current_time" in r.get("data",[{}])[0]},
            {"name": "02. Get Database Info", "node_input_params": {**neon_params_base, "operation": NeonOperationType.GET_DATABASE_INFO}, "expected_status": "success", "validation": lambda r: "version" in r.get("data",{}) and "schemas" in r.get("data",{})},
            {"name": "03. Create Test Schema", "node_input_params": {**neon_params_base, "operation": NeonOperationType.CREATE_SCHEMA, "schema_name": TEST_SCHEMA}, "expected_status": "success"},
            {"name": "04. Create Test Table", "node_input_params": {**neon_params_base, "operation": NeonOperationType.CREATE_TABLE, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE, "columns": {"id": "SERIAL PRIMARY KEY", "name": "VARCHAR(100) NOT NULL", "email": "VARCHAR(255) UNIQUE", "age": "INTEGER"}}, "expected_status": "success"},
            {"name": "05. Insert Single Record", "node_input_params": {**neon_params_base, "operation": NeonOperationType.INSERT_DATA, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE, "data": {"name": "John Doe", "email": "john.doe@example.com", "age": 30}}, "expected_status": "success", "validation": lambda r: len(r.get("data",[])) == 1 and r.get("data",[{}])[0].get("name") == "John Doe"},
            {"name": "06. Bulk Insert Records", "node_input_params": {**neon_params_base, "operation": NeonOperationType.BULK_INSERT, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE, "bulk_data": [{"name": "Jane Smith", "email": "jane.smith@example.com", "age": 25}, {"name": "Bob Johnson", "email": "bob.johnson@example.com", "age": 35}]}, "expected_status": "success", "validation": lambda r: r.get("rows_affected") == 2},
            {"name": "07. Select Data with Conditions", "node_input_params": {**neon_params_base, "operation": NeonOperationType.SELECT_DATA, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE, "where_clause": "age > %s", "where_parameters": [27], "order_by": "age DESC", "limit": 1}, "expected_status": "success", "validation": lambda r: len(r.get("data",[])) == 1 and r.get("data",[{}])[0].get("age", 0) > 27},
            {"name": "08. Update Data", "node_input_params": {**neon_params_base, "operation": NeonOperationType.UPDATE_DATA, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE, "data": {"age": 31}, "where_clause": "email = %s", "where_parameters": ["john.doe@example.com"]}, "expected_status": "success", "validation": lambda r: len(r.get("data",[])) == 1 and r.get("data",[{}])[0].get("age") == 31},
            {"name": "09. Upsert Data (Update Existing)", "node_input_params": {**neon_params_base, "operation": NeonOperationType.UPSERT_DATA, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE, "data": {"name": "John Doe Updated", "email": "john.doe@example.com", "age": 32}, "conflict_columns": ["email"]}, "expected_status": "success", "validation": lambda r: len(r.get("data",[])) > 0 and r.get("data",[{}])[0].get("age") == 32},
            {"name": "10. Upsert Data (Insert New)", "node_input_params": {**neon_params_base, "operation": NeonOperationType.UPSERT_DATA, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE, "data": {"name": "Kevin Add", "email": "kevin.add@example.com", "age": 40}, "conflict_columns": ["email"]}, "expected_status": "success", "validation": lambda r: len(r.get("data",[])) > 0 and r.get("data",[{}])[0].get("email") == "kevin.add@example.com"},
            {"name": "11. Create Index", "node_input_params": {**neon_params_base, "operation": NeonOperationType.CREATE_INDEX, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE, "index_name": TEST_INDEX, "index_columns": ["age", "name"]}, "expected_status": "success"}, # index_columns was ["age", "name"]
            {"name": "12. Get Table Info (After Index)", "node_input_params": {**neon_params_base, "operation": NeonOperationType.GET_TABLE_INFO, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE}, "expected_status": "success", "validation": lambda r: len(r.get("data",{}).get("columns",[])) > 0 and any(idx.get("indexname") == TEST_INDEX for idx in r.get("data",{}).get("indexes",[]))},
            {"name": "13. Execute Transaction (Insert & Update)", "node_input_params": {**neon_params_base, "operation": NeonOperationType.EXECUTE_TRANSACTION, "queries": [{"query": f"INSERT INTO {TEST_SCHEMA}.{TEST_TABLE} (name, email, age) VALUES (%s, %s, %s) RETURNING id", "parameters": ["Trans Man", "trans.man@example.com", 50]}, {"query": f"UPDATE {TEST_SCHEMA}.{TEST_TABLE} SET age = age + 1 WHERE email = %s", "parameters": ["trans.man@example.com"]}]}, "expected_status": "success", "validation": lambda r: len(r.get("data",[])) == 2 and r.get("data",[{},{}])[0].get("rows_affected") == 1 and r.get("data",[{},{}])[1].get("rows_affected") == 1},
            {"name": "14. Backup Table", "node_input_params": {**neon_params_base, "operation": NeonOperationType.BACKUP_TABLE, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE, "backup_table_name": TEST_TABLE_BACKUP}, "expected_status": "success"},
            {"name": "15. Verify Backup Table Exists", "node_input_params": {**neon_params_base, "operation": NeonOperationType.GET_SCHEMA_INFO, "schema_name": TEST_SCHEMA}, "expected_status": "success", "validation": lambda r: any(t.get("table_name") == TEST_TABLE_BACKUP for t in r.get("data",{}).get("tables_views",[]))},
            {"name": "16. Analyze Table", "node_input_params": {**neon_params_base, "operation": NeonOperationType.ANALYZE_TABLE, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE}, "expected_status": "success"},
            {"name": "17. Get Schema Info", "node_input_params": {**neon_params_base, "operation": NeonOperationType.GET_SCHEMA_INFO, "schema_name": TEST_SCHEMA}, "expected_status": "success", "validation": lambda r: len(r.get("data",{}).get("tables_views",[])) > 0},
            {"name": "18. Delete Specific Data", "node_input_params": {**neon_params_base, "operation": NeonOperationType.DELETE_DATA, "schema_name": TEST_SCHEMA, "table_name": TEST_TABLE, "where_clause": "email = %s", "where_parameters": ["bob.johnson@example.com"]}, "expected_status": "success", "validation": lambda r: r.get("rows_affected") == 1},
            {"name": "19. Setup Restore Target Table", "node_input_params": {**neon_params_base, "operation": NeonOperationType.EXECUTE_QUERY, "query": create_restore_target_ddl}, "expected_status": "success"},
            {"name": "20. Restore Table from Backup", "node_input_params": {**neon_params_base, "operation": NeonOperationType.RESTORE_TABLE, "schema_name": TEST_SCHEMA, "table_name": TEST_RESTORE_TARGET_TABLE, "backup_table_name": TEST_TABLE_BACKUP, "truncate_first": False}, "expected_status": "success"},
            
            {"name": "90. Drop Index", "node_input_params": {**neon_params_base, "operation": NeonOperationType.DROP_INDEX, "schema_name": TEST_SCHEMA, "index_name": TEST_INDEX}, "expected_status": "success", "cleanup": True},
            {"name": "91. Drop Test Table (Backup)", "node_input_params": {**neon_params_base, "operation": NeonOperationType.EXECUTE_QUERY, "query": drop_backup_table_query_str}, "expected_status": "success", "cleanup": True},
            {"name": "92. Drop Test Table (Restore Target)", "node_input_params": {**neon_params_base, "operation": NeonOperationType.EXECUTE_QUERY, "query": drop_restore_target_table_query_str}, "expected_status": "success", "cleanup": True},
            {"name": "93. Drop Test Table (Main)", "node_input_params": {**neon_params_base, "operation": NeonOperationType.EXECUTE_QUERY, "query": drop_main_table_query_str}, "expected_status": "success", "cleanup": True},
            {"name": "94. Drop Test Schema (Final Cleanup)", "node_input_params": {**neon_params_base, "operation": NeonOperationType.DROP_SCHEMA, "schema_name": TEST_SCHEMA, "cascade": True}, "expected_status": "success", "cleanup": True, "idempotent_cleanup": True}
        ]
        
        total_tests, passed_tests = len(test_cases), 0
        failed_tests_details = []

        for i, test_case in enumerate(test_cases):
            print(f"\nRunning test [{i+1}/{total_tests}]: {test_case['name']}")
            is_cleanup, is_idempotent_cleanup = test_case.get("cleanup", False), test_case.get("idempotent_cleanup", False)
            try:
                node_data_to_execute = {"params": test_case["node_input_params"]}
                result = await node.execute(node_data_to_execute) 

                if result.get("status") == test_case["expected_status"]:
                    val_passed = True
                    if "validation" in test_case:
                        try: val_passed = test_case["validation"](result)
                        except Exception as val_e: val_passed = False; print(f"    ⚠️ Validation error: {val_e}")
                    if val_passed: print(f"    ✅ PASS - Status: {result.get('status')}"); passed_tests += 1
                    else: print(f"    ❌ FAIL - Validation failed."); failed_tests_details.append({"name": test_case['name'], "reason": "Validation Failed", "result": result})
                else:
                    err_detail = result.get('error', 'N/A')
                    print(f"    ❌ FAIL - Expected status '{test_case['expected_status']}', got '{result.get('status')}'. Error: {err_detail}")
                    failed_tests_details.append({"name": test_case['name'], "reason": f"Status Mismatch", "error": err_detail, "result_status": result.get('status')})
            except Exception as e:
                if is_cleanup and is_idempotent_cleanup and isinstance(e, (NodeValidationError, psycopg2.Error)):
                    print(f"    ℹ️ INFO (Idempotent Cleanup) - '{test_case['name']}' encountered expected DDL issue: {e}"); passed_tests +=1
                else: 
                    print(f"    ❌ FAIL - Exception: {e}"); 
                    logger.error(f"Test '{test_case['name']}' exception:", exc_info=True); 
                    failed_tests_details.append({"name": test_case['name'], "reason": "Exception", "exception": str(e)})
        
        print(f"\n=== Test Summary ===\nTotal: {total_tests}, Passed: {passed_tests}, Failed: {total_tests - passed_tests}")
        if total_tests > 0: print(f"Success rate: {(passed_tests / total_tests) * 100:.1f}%")
        if failed_tests_details:
            print("\n--- Failed Test Details ---")
            for detail in failed_tests_details:
                print(f"  Test: {detail['name']}, Reason: {detail.get('reason','N/A')}, Error: {detail.get('error','N/A')}, Exception: {detail.get('exception','N/A')}")

        print("\n=== Performance Test: Concurrent Simple Queries ===")
        perf_node = NeonNode() 
        perf_test_conn_params = { **neon_params_base, "pool_size": 5, "max_pool_size": 15 }
        try:
            await asyncio.to_thread(perf_node._initialize_connection, perf_test_conn_params)
            tasks = [perf_node.execute({"params": {**perf_test_conn_params, "operation": NeonOperationType.EXECUTE_QUERY, "query": f"SELECT {i} as test_id, pg_sleep(0.001)"}}) for i in range(20)]
            start_t = time.monotonic()
            perf_res = await asyncio.gather(*tasks, return_exceptions=True)
            successful_perf_ops = sum(1 for r in perf_res if isinstance(r, dict) and r.get('status') == 'success')
            print(f"Completed {len(tasks)} concurrent queries in {time.monotonic() - start_t:.4f}s. Successful: {successful_perf_ops}/{len(tasks)}")
        except Exception as e:
            print(f"Performance test setup/execution failed: {e}")
        finally:
            await perf_node.close()

        print("\n=== Error Handling Test: Invalid Query ===")
        err_res = await node.execute({"params": {**neon_params_base, "operation": NeonOperationType.EXECUTE_QUERY, "query": "SELECT * FROM non_existent_table_for_error_test"}})
        print(f"Error Handling Test: Status='{err_res.get('status')}', Error Present={bool(err_res.get('error'))}")
        if err_res.get('status') == 'error' and err_res.get('error'): print("    ✅ PASS - Correctly handled invalid query.")
        else: print("    ❌ FAIL - Did not correctly handle invalid query.")

        await node.close() 
        logger.info("NeonNode test suite completed.")

    asyncio.run(run_tests())