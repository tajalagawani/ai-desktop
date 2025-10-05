"""
Neo4j Node - Performs Neo4j graph database operations with comprehensive options and error handling.
"""

import logging
import json
import time
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
import neo4j
from neo4j import GraphDatabase

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

class Neo4jOperationType:
    """Neo4j operation types."""
    RUN_QUERY = "run_query"
    RUN_TRANSACTION = "run_transaction"
    CREATE_NODE = "create_node"
    MATCH_NODE = "match_node"
    UPDATE_NODE = "update_node"
    DELETE_NODE = "delete_node"
    CREATE_RELATIONSHIP = "create_relationship"
    MATCH_RELATIONSHIP = "match_relationship"
    UPDATE_RELATIONSHIP = "update_relationship"
    DELETE_RELATIONSHIP = "delete_relationship"
    GET_DATABASE_INFO = "get_database_info"

class Neo4jNode(BaseNode):
    """
    Node for interacting with Neo4j Graph Database.
    Provides functionality for common Neo4j operations with comprehensive error handling.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.driver = None
    
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Neo4j node."""
        return NodeSchema(
            node_type="neo4j",
            version="1.0.0",
            description="Interacts with Neo4j Graph Database using neo4j-driver",
            parameters=[
                # Connection parameters
                NodeParameter(
                    name="uri",
                    type=NodeParameterType.STRING,
                    description="Neo4j connection URI (e.g., bolt://localhost:7687)",
                    required=True
                ),
                NodeParameter(
                    name="username",
                    type=NodeParameterType.STRING,
                    description="Neo4j username",
                    required=True
                ),
                NodeParameter(
                    name="password",
                    type=NodeParameterType.STRING,
                    description="Neo4j password",
                    required=True
                ),
                NodeParameter(
                    name="database",
                    type=NodeParameterType.STRING,
                    description="Neo4j database name (for Neo4j 4.0+)",
                    required=False,
                    default="neo4j"
                ),
                NodeParameter(
                    name="connection_timeout",
                    type=NodeParameterType.NUMBER,
                    description="Connection timeout in seconds",
                    required=False,
                    default=30
                ),
                NodeParameter(
                    name="max_transaction_retry_time",
                    type=NodeParameterType.NUMBER,
                    description="Maximum transaction retry time in seconds",
                    required=False,
                    default=30
                ),
                
                # Operation parameters
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Neo4j operation to perform",
                    required=True,
                    enum=[
                        Neo4jOperationType.RUN_QUERY,
                        Neo4jOperationType.RUN_TRANSACTION,
                        Neo4jOperationType.CREATE_NODE,
                        Neo4jOperationType.MATCH_NODE,
                        Neo4jOperationType.UPDATE_NODE,
                        Neo4jOperationType.DELETE_NODE,
                        Neo4jOperationType.CREATE_RELATIONSHIP,
                        Neo4jOperationType.MATCH_RELATIONSHIP,
                        Neo4jOperationType.UPDATE_RELATIONSHIP,
                        Neo4jOperationType.DELETE_RELATIONSHIP,
                        Neo4jOperationType.GET_DATABASE_INFO
                    ]
                ),
                
                # Query parameters
                NodeParameter(
                    name="query",
                    type=NodeParameterType.STRING,
                    description="Cypher query to execute",
                    required=False
                ),
                NodeParameter(
                    name="parameters",
                    type=NodeParameterType.OBJECT,
                    description="Parameters for Cypher query",
                    required=False,
                    default={}
                ),
                NodeParameter(
                    name="queries",
                    type=NodeParameterType.ARRAY,
                    description="List of Cypher queries to execute in a transaction",
                    required=False
                ),
                
                # Node operation parameters
                NodeParameter(
                    name="labels",
                    type=NodeParameterType.ARRAY,
                    description="Labels for node operations",
                    required=False
                ),
                NodeParameter(
                    name="properties",
                    type=NodeParameterType.OBJECT,
                    description="Properties for node/relationship operations",
                    required=False
                ),
                NodeParameter(
                    name="match_properties",
                    type=NodeParameterType.OBJECT,
                    description="Properties to match nodes/relationships",
                    required=False
                ),
                NodeParameter(
                    name="update_properties",
                    type=NodeParameterType.OBJECT,
                    description="Properties to update for nodes/relationships",
                    required=False
                ),
                
                # Relationship operation parameters
                NodeParameter(
                    name="relationship_type",
                    type=NodeParameterType.STRING,
                    description="Type of relationship for relationship operations",
                    required=False
                ),
                NodeParameter(
                    name="from_node_labels",
                    type=NodeParameterType.ARRAY,
                    description="Labels for the source node in relationship operations",
                    required=False
                ),
                NodeParameter(
                    name="from_node_properties",
                    type=NodeParameterType.OBJECT,
                    description="Properties to identify the source node in relationship operations",
                    required=False
                ),
                NodeParameter(
                    name="to_node_labels",
                    type=NodeParameterType.ARRAY,
                    description="Labels for the target node in relationship operations",
                    required=False
                ),
                NodeParameter(
                    name="to_node_properties",
                    type=NodeParameterType.OBJECT,
                    description="Properties to identify the target node in relationship operations",
                    required=False
                ),
                
                # Result parameters
                NodeParameter(
                    name="return_nodes",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to return matched/created nodes",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Limit the number of results",
                    required=False
                ),
                NodeParameter(
                    name="skip",
                    type=NodeParameterType.NUMBER,
                    description="Skip the first N results",
                    required=False
                ),
                NodeParameter(
                    name="order_by",
                    type=NodeParameterType.STRING,
                    description="Property to order results by",
                    required=False
                ),
                NodeParameter(
                    name="order_direction",
                    type=NodeParameterType.STRING,
                    description="Direction to order results",
                    required=False,
                    default="ASC",
                    enum=["ASC", "DESC"]
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "data": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "stats": NodeParameterType.OBJECT,
                "execution_time": NodeParameterType.NUMBER,
                "count": NodeParameterType.NUMBER,
                "summary": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["database", "graph", "neo4j", "cypher"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation for Neo4j parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Validate connection parameters
        uri = params.get("uri")
        if not uri:
            raise NodeValidationError("URI is required")
        
        username = params.get("username")
        if not username:
            raise NodeValidationError("Username is required")
        
        password = params.get("password")
        if not password:
            raise NodeValidationError("Password is required")
        
        # Validate operation-specific parameters
        if operation == Neo4jOperationType.RUN_QUERY:
            if not params.get("query"):
                raise NodeValidationError("Query is required for RUN_QUERY operation")
                
        elif operation == Neo4jOperationType.RUN_TRANSACTION:
            if not params.get("queries") or not isinstance(params.get("queries"), list) or len(params.get("queries")) == 0:
                raise NodeValidationError("Queries array is required for RUN_TRANSACTION operation")
        
        elif operation == Neo4jOperationType.CREATE_NODE:
            if not params.get("labels") or not isinstance(params.get("labels"), list) or len(params.get("labels")) == 0:
                raise NodeValidationError("Labels are required for CREATE_NODE operation")
            if not params.get("properties") or not isinstance(params.get("properties"), dict):
                raise NodeValidationError("Properties are required for CREATE_NODE operation")
        
        elif operation == Neo4jOperationType.MATCH_NODE:
            if not params.get("labels") or not isinstance(params.get("labels"), list) or len(params.get("labels")) == 0:
                raise NodeValidationError("Labels are required for MATCH_NODE operation")
        
        elif operation == Neo4jOperationType.UPDATE_NODE:
            if not params.get("labels") or not isinstance(params.get("labels"), list) or len(params.get("labels")) == 0:
                raise NodeValidationError("Labels are required for UPDATE_NODE operation")
            if not params.get("match_properties") or not isinstance(params.get("match_properties"), dict):
                raise NodeValidationError("Match properties are required for UPDATE_NODE operation")
            if not params.get("update_properties") or not isinstance(params.get("update_properties"), dict):
                raise NodeValidationError("Update properties are required for UPDATE_NODE operation")
        
        elif operation == Neo4jOperationType.DELETE_NODE:
            if not params.get("labels") or not isinstance(params.get("labels"), list) or len(params.get("labels")) == 0:
                raise NodeValidationError("Labels are required for DELETE_NODE operation")
            if not params.get("match_properties") or not isinstance(params.get("match_properties"), dict):
                raise NodeValidationError("Match properties are required for DELETE_NODE operation")
        
        elif operation == Neo4jOperationType.CREATE_RELATIONSHIP:
            if not params.get("relationship_type"):
                raise NodeValidationError("Relationship type is required for CREATE_RELATIONSHIP operation")
            if not params.get("from_node_labels") or not isinstance(params.get("from_node_labels"), list) or len(params.get("from_node_labels")) == 0:
                raise NodeValidationError("From node labels are required for CREATE_RELATIONSHIP operation")
            if not params.get("to_node_labels") or not isinstance(params.get("to_node_labels"), list) or len(params.get("to_node_labels")) == 0:
                raise NodeValidationError("To node labels are required for CREATE_RELATIONSHIP operation")
            if not params.get("from_node_properties") or not isinstance(params.get("from_node_properties"), dict):
                raise NodeValidationError("From node properties are required for CREATE_RELATIONSHIP operation")
            if not params.get("to_node_properties") or not isinstance(params.get("to_node_properties"), dict):
                raise NodeValidationError("To node properties are required for CREATE_RELATIONSHIP operation")
        
        elif operation == Neo4jOperationType.MATCH_RELATIONSHIP:
            if not params.get("relationship_type"):
                raise NodeValidationError("Relationship type is required for MATCH_RELATIONSHIP operation")
        
        elif operation == Neo4jOperationType.UPDATE_RELATIONSHIP:
            if not params.get("relationship_type"):
                raise NodeValidationError("Relationship type is required for UPDATE_RELATIONSHIP operation")
            if not params.get("match_properties") or not isinstance(params.get("match_properties"), dict):
                raise NodeValidationError("Match properties are required for UPDATE_RELATIONSHIP operation")
            if not params.get("update_properties") or not isinstance(params.get("update_properties"), dict):
                raise NodeValidationError("Update properties are required for UPDATE_RELATIONSHIP operation")
        
        elif operation == Neo4jOperationType.DELETE_RELATIONSHIP:
            if not params.get("relationship_type"):
                raise NodeValidationError("Relationship type is required for DELETE_RELATIONSHIP operation")
            if not params.get("match_properties") or not isinstance(params.get("match_properties"), dict):
                raise NodeValidationError("Match properties are required for DELETE_RELATIONSHIP operation")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Neo4j node operation."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            params = validated_data.get("params", {})
            
            # Initialize Neo4j driver if not already initialized
            if not self.driver:
                self._initialize_driver(params)
            
            # Get operation type
            operation = params.get("operation")
            
            # Execute the appropriate operation based on the operation type
            if operation == Neo4jOperationType.RUN_QUERY:
                return await self.operation_run_query(params)
            elif operation == Neo4jOperationType.RUN_TRANSACTION:
                return await self.operation_run_transaction(params)
            elif operation == Neo4jOperationType.CREATE_NODE:
                return await self.operation_create_node(params)
            elif operation == Neo4jOperationType.MATCH_NODE:
                return await self.operation_match_node(params)
            elif operation == Neo4jOperationType.UPDATE_NODE:
                return await self.operation_update_node(params)
            elif operation == Neo4jOperationType.DELETE_NODE:
                return await self.operation_delete_node(params)
            elif operation == Neo4jOperationType.CREATE_RELATIONSHIP:
                return await self.operation_create_relationship(params)
            elif operation == Neo4jOperationType.MATCH_RELATIONSHIP:
                return await self.operation_match_relationship(params)
            elif operation == Neo4jOperationType.UPDATE_RELATIONSHIP:
                return await self.operation_update_relationship(params)
            elif operation == Neo4jOperationType.DELETE_RELATIONSHIP:
                return await self.operation_delete_relationship(params)
            elif operation == Neo4jOperationType.GET_DATABASE_INFO:
                return await self.operation_get_database_info(params)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
        except Exception as e:
            error_message = f"Error in Neo4j node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "data": None,
                "error": error_message,
                "stats": None,
                "execution_time": 0,
                "count": 0,
                "summary": None
            }
    
    def _initialize_driver(self, params: Dict[str, Any]) -> None:
        """
        Initialize Neo4j driver.
        
        Args:
            params: Parameters including Neo4j connection details
        """
        uri = params.get("uri")
        username = params.get("username")
        password = params.get("password")
        connection_timeout = params.get("connection_timeout", 30)
        max_transaction_retry_time = params.get("max_transaction_retry_time", 30)
        
        try:
            self.driver = GraphDatabase.driver(
                uri,
                auth=(username, password),
                connection_timeout=connection_timeout,
                max_transaction_retry_time=max_transaction_retry_time
            )
            # Verify connection by running a simple query
            with self.driver.session() as session:
                session.run("RETURN 1")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {str(e)}")
            raise ValueError(f"Failed to connect to Neo4j: {str(e)}")
    
    def _record_to_dict(self, record):
        """
        Convert a Neo4j record to a dictionary.
        
        Args:
            record: Neo4j record
            
        Returns:
            Dictionary representation of the record
        """
        return {key: self._neo4j_value_to_python(record[key]) for key in record.keys()}
    
    def _neo4j_value_to_python(self, value):
        """
        Convert Neo4j values to Python types.
        
        Args:
            value: Neo4j value
            
        Returns:
            Python representation of the value
        """
        if hasattr(value, "labels") and callable(getattr(value, "labels")):
            # It's a node
            return {
                "_id": value.id,
                "_labels": list(value.labels),
                **{k: self._neo4j_value_to_python(v) for k, v in dict(value).items()}
            }
        elif hasattr(value, "type") and callable(getattr(value, "type")):
            # It's a relationship
            return {
                "_id": value.id,
                "_type": value.type,
                "_start_node_id": value.start_node.id,
                "_end_node_id": value.end_node.id,
                **{k: self._neo4j_value_to_python(v) for k, v in dict(value).items()}
            }
        elif hasattr(value, "nodes") and callable(getattr(value, "nodes")):
            # It's a path
            return {
                "nodes": [self._neo4j_value_to_python(node) for node in value.nodes],
                "relationships": [self._neo4j_value_to_python(rel) for rel in value.relationships],
                "segments": [
                    {
                        "start": self._neo4j_value_to_python(segment.start),
                        "relationship": self._neo4j_value_to_python(segment.relationship),
                        "end": self._neo4j_value_to_python(segment.end)
                    }
                    for segment in value
                ]
            }
        elif isinstance(value, list):
            return [self._neo4j_value_to_python(v) for v in value]
        elif isinstance(value, dict):
            return {k: self._neo4j_value_to_python(v) for k, v in value.items()}
        else:
            # Basic types (int, str, float, bool, etc.)
            return value
    
    def _get_summary_dict(self, summary):
        """
        Convert Neo4j summary to a dictionary.
        
        Args:
            summary: Neo4j result summary
            
        Returns:
            Dictionary representation of the summary
        """
        result = {}
        
        if hasattr(summary, "counters") and summary.counters:
            counters = summary.counters
            result["counters"] = {
                "nodes_created": counters.nodes_created,
                "nodes_deleted": counters.nodes_deleted,
                "relationships_created": counters.relationships_created,
                "relationships_deleted": counters.relationships_deleted,
                "properties_set": counters.properties_set,
                "labels_added": counters.labels_added,
                "labels_removed": counters.labels_removed,
                "indexes_added": counters.indexes_added,
                "indexes_removed": counters.indexes_removed,
                "constraints_added": counters.constraints_added,
                "constraints_removed": counters.constraints_removed
            }
        
        if hasattr(summary, "query"):
            result["query"] = {
                "text": summary.query,
                "parameters": summary.parameters
            }
        
        if hasattr(summary, "result_available_after"):
            result["result_available_after"] = summary.result_available_after
        
        if hasattr(summary, "result_consumed_after"):
            result["result_consumed_after"] = summary.result_consumed_after
        
        if hasattr(summary, "plan") and summary.plan:
            result["plan"] = {
                "operator_type": summary.plan.operator_type,
                "identifiers": summary.plan.identifiers,
                "arguments": summary.plan.arguments,
                "children": [
                    {
                        "operator_type": child.operator_type,
                        "identifiers": child.identifiers,
                        "arguments": child.arguments
                    }
                    for child in summary.plan.children
                ] if summary.plan.children else []
            }
        
        return result
    
    async def _run_query(self, database, query, parameters=None, return_summary=True):
        """
        Run a Cypher query.
        
        Args:
            database: Neo4j database name
            query: Cypher query
            parameters: Query parameters
            return_summary: Whether to return the summary
            
        Returns:
            Query results, summary, and execution time
        """
        if parameters is None:
            parameters = {}
        
        start_time = time.time()
        
        try:
            with self.driver.session(database=database) as session:
                result = session.run(query, parameters)
                records = list(result)
                summary = result.consume() if return_summary else None
                
                execution_time = time.time() - start_time
                
                data = [self._record_to_dict(record) for record in records]
                
                return {
                    "data": data,
                    "summary": self._get_summary_dict(summary) if summary else None,
                    "execution_time": execution_time,
                    "count": len(data)
                }
        except Exception as e:
            raise ValueError(f"Query execution failed: {str(e)}")
    
    async def operation_run_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a Cypher query.
        
        Args:
            params: Parameters for running the query
            
        Returns:
            Operation result with query results
        """
        database = params.get("database", "neo4j")
        query = params.get("query")
        parameters = params.get("parameters", {})
        
        try:
            result = await self._run_query(database, query, parameters)
            
            return {
                "status": "success",
                "data": result["data"],
                "error": None,
                "stats": result["summary"].get("counters") if result["summary"] else None,
                "execution_time": result["execution_time"],
                "count": result["count"],
                "summary": result["summary"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "stats": None,
                "execution_time": 0,
                "count": 0,
                "summary": None
            }
    
    async def operation_run_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run multiple queries in a transaction.
        
        Args:
            params: Parameters for running the transaction
            
        Returns:
            Operation result with transaction results
        """
        database = params.get("database", "neo4j")
        queries = params.get("queries", [])
        
        start_time = time.time()
        
        try:
            results = []
            stats = {
                "nodes_created": 0,
                "nodes_deleted": 0,
                "relationships_created": 0,
                "relationships_deleted": 0,
                "properties_set": 0,
                "labels_added": 0,
                "labels_removed": 0,
                "indexes_added": 0,
                "indexes_removed": 0,
                "constraints_added": 0,
                "constraints_removed": 0
            }
            
            with self.driver.session(database=database) as session:
                # Define transaction function
                def run_queries(tx):
                    query_results = []
                    for query_item in queries:
                        query = query_item.get("query")
                        parameters = query_item.get("parameters", {})
                        
                        result = tx.run(query, parameters)
                        records = list(result)
                        summary = result.consume()
                        
                        data = [self._record_to_dict(record) for record in records]
                        summary_dict = self._get_summary_dict(summary)
                        
                        query_results.append({
                            "data": data,
                            "summary": summary_dict,
                            "count": len(data)
                        })
                    
                    return query_results
                
                # Run transaction
                results = session.write_transaction(run_queries)
            
            # Combine stats from all query results
            for result in results:
                if result["summary"] and "counters" in result["summary"]:
                    counters = result["summary"]["counters"]
                    for key in stats:
                        stats[key] += counters.get(key, 0)
            
            execution_time = time.time() - start_time
            
            return {
                "status": "success",
                "data": [result["data"] for result in results],
                "error": None,
                "stats": stats,
                "execution_time": execution_time,
                "count": sum(result["count"] for result in results),
                "summary": [result["summary"] for result in results]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "stats": None,
                "execution_time": time.time() - start_time,
                "count": 0,
                "summary": None
            }
    
    async def operation_create_node(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a node.
        
        Args:
            params: Parameters for creating the node
            
        Returns:
            Operation result with the created node
        """
        database = params.get("database", "neo4j")
        labels = params.get("labels", [])
        properties = params.get("properties", {})
        return_nodes = params.get("return_nodes", True)
        
        # Construct the Cypher query
        label_str = ":".join(labels)
        query = f"CREATE (n:{label_str} $properties) "
        
        if return_nodes:
            query += "RETURN n"
        else:
            query += "RETURN count(n) AS count"
        
        try:
            result = await self._run_query(database, query, {"properties": properties})
            
            return {
                "status": "success",
                "data": result["data"],
                "error": None,
                "stats": result["summary"].get("counters") if result["summary"] else None,
                "execution_time": result["execution_time"],
                "count": result["count"],
                "summary": result["summary"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "stats": None,
                "execution_time": 0,
                "count": 0,
                "summary": None
            }
    
    async def operation_match_node(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match nodes.
        
        Args:
            params: Parameters for matching nodes
            
        Returns:
            Operation result with matched nodes
        """
        database = params.get("database", "neo4j")
        labels = params.get("labels", [])
        match_properties = params.get("match_properties", {})
        limit = params.get("limit")
        skip = params.get("skip")
        order_by = params.get("order_by")
        order_direction = params.get("order_direction", "ASC")
        
        # Construct the Cypher query
        label_str = ":".join(labels)
        query = f"MATCH (n:{label_str}"
        
        # Add property conditions if provided
        if match_properties:
            property_conditions = []
            for key, value in match_properties.items():
                property_conditions.append(f"n.{key} = ${key}")
            
            if property_conditions:
                query += " {"
                query += ", ".join(f"{key}: ${key}" for key in match_properties.keys())
                query += "}"
        
        query += ") "
        
        # Add ORDER BY clause if specified
        if order_by:
            query += f"ORDER BY n.{order_by} {order_direction} "
        
        # Add SKIP clause if specified
        if skip:
            query += f"SKIP {skip} "
        
        # Add LIMIT clause if specified
        if limit:
            query += f"LIMIT {limit} "
        
        query += "RETURN n"
        
        try:
            result = await self._run_query(database, query, match_properties)
            
            return {
                "status": "success",
                "data": result["data"],
                "error": None,
                "stats": result["summary"].get("counters") if result["summary"] else None,
                "execution_time": result["execution_time"],
                "count": result["count"],
                "summary": result["summary"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "stats": None,
                "execution_time": 0,
                "count": 0,
                "summary": None
            }
    
    async def operation_update_node(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update nodes.
        
        Args:
            params: Parameters for updating nodes
            
        Returns:
            Operation result with updated nodes
        """
        database = params.get("database", "neo4j")
        labels = params.get("labels", [])
        match_properties = params.get("match_properties", {})
        update_properties = params.get("update_properties", {})
        return_nodes = params.get("return_nodes", True)
        
        # Construct the Cypher query
        label_str = ":".join(labels)
        query = f"MATCH (n:{label_str}"
        
        # Add property conditions if provided
        if match_properties:
            property_conditions = []
            for key, value in match_properties.items():
                property_conditions.append(f"n.{key} = ${key}")
            
            if property_conditions:
                query += " {"
                query += ", ".join(f"{key}: ${key}" for key in match_properties.keys())
                query += "}"
        
        query += ") "
        
        # Add SET clause for updates
        if update_properties:
            query += "SET "
            update_clauses = []
            for key in update_properties.keys():
                update_clauses.append(f"n.{key} = $update_{key}")
            query += ", ".join(update_clauses)
        
        if return_nodes:
            query += " RETURN n"
        else:
            query += " RETURN count(n) AS count"
        
        # Prepare parameters
        parameters = dict(match_properties)
        for key, value in update_properties.items():
            parameters[f"update_{key}"] = value
        
        try:
            result = await self._run_query(database, query, parameters)
            
            return {
                "status": "success",
                "data": result["data"],
                "error": None,
                "stats": result["summary"].get("counters") if result["summary"] else None,
                "execution_time": result["execution_time"],
                "count": result["count"],
                "summary": result["summary"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "stats": None,
                "execution_time": 0,
                "count": 0,
                "summary": None
            }
    
    async def operation_delete_node(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete nodes.
        
        Args:
            params: Parameters for deleting nodes
            
        Returns:
            Operation result with deletion statistics
        """
        database = params.get("database", "neo4j")
        labels = params.get("labels", [])
        match_properties = params.get("match_properties", {})
        detach_delete = params.get("detach_delete", True)
        
        # Construct the Cypher query
        label_str = ":".join(labels)
        query = f"MATCH (n:{label_str}"
        
        # Add property conditions if provided
        if match_properties:
            property_conditions = []
            for key, value in match_properties.items():
                property_conditions.append(f"n.{key} = ${key}")
            
            if property_conditions:
                query += " {"
                query += ", ".join(f"{key}: ${key}" for key in match_properties.keys())
                query += "}"
        
        query += ") "
        
        # Add DELETE or DETACH DELETE clause
        if detach_delete:
            query += "DETACH DELETE n "
        else:
            query += "DELETE n "
        
        query += "RETURN count(n) AS count"
        
        try:
            result = await self._run_query(database, query, match_properties)
            
            return {
                "status": "success",
                "data": result["data"],
                "error": None,
                "stats": result["summary"].get("counters") if result["summary"] else None,
                "execution_time": result["execution_time"],
                "count": result["count"],
                "summary": result["summary"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "stats": None,
                "execution_time": 0,
                "count": 0,
                "summary": None
            }
    
    async def operation_create_relationship(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a relationship between nodes.
        
        Args:
            params: Parameters for creating the relationship
            
        Returns:
            Operation result with the created relationship
        """
        database = params.get("database", "neo4j")
        relationship_type = params.get("relationship_type")
        from_node_labels = params.get("from_node_labels", [])
        from_node_properties = params.get("from_node_properties", {})
        to_node_labels = params.get("to_node_labels", [])
        to_node_properties = params.get("to_node_properties", {})
        properties = params.get("properties", {})
        return_nodes = params.get("return_nodes", True)
        
        # Construct the Cypher query
        from_label_str = ":".join(from_node_labels)
        to_label_str = ":".join(to_node_labels)
        
        query = f"MATCH (a:{from_label_str}), (b:{to_label_str}) "
        
        # Add WHERE clauses for node matching
        where_clauses = []
        
        for key, value in from_node_properties.items():
            where_clauses.append(f"a.{key} = $from_{key}")
        
        for key, value in to_node_properties.items():
            where_clauses.append(f"b.{key} = $to_{key}")
        
        if where_clauses:
            query += "WHERE " + " AND ".join(where_clauses) + " "
        
        # Create the relationship
        query += f"CREATE (a)-[r:{relationship_type} $rel_properties]->(b) "
        
        if return_nodes:
            query += "RETURN a, r, b"
        else:
            query += "RETURN count(r) AS count"
        
        # Prepare parameters
        parameters = {}
        for key, value in from_node_properties.items():
            parameters[f"from_{key}"] = value
        
        for key, value in to_node_properties.items():
            parameters[f"to_{key}"] = value
        
        parameters["rel_properties"] = properties
        
        try:
            result = await self._run_query(database, query, parameters)
            
            return {
                "status": "success",
                "data": result["data"],
                "error": None,
                "stats": result["summary"].get("counters") if result["summary"] else None,
                "execution_time": result["execution_time"],
                "count": result["count"],
                "summary": result["summary"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "stats": None,
                "execution_time": 0,
                "count": 0,
                "summary": None
            }
    
    async def operation_match_relationship(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match relationships.
        
        Args:
            params: Parameters for matching relationships
            
        Returns:
            Operation result with matched relationships
        """
        database = params.get("database", "neo4j")
        relationship_type = params.get("relationship_type")
        from_node_labels = params.get("from_node_labels", [])
        from_node_properties = params.get("from_node_properties", {})
        to_node_labels = params.get("to_node_labels", [])
        to_node_properties = params.get("to_node_properties", {})
        match_properties = params.get("match_properties", {})
        limit = params.get("limit")
        skip = params.get("skip")
        order_by = params.get("order_by")
        order_direction = params.get("order_direction", "ASC")
        
        # Construct the Cypher query
        from_label_str = ":".join(from_node_labels) if from_node_labels else ""
        to_label_str = ":".join(to_node_labels) if to_node_labels else ""
        
        query = "MATCH "
        
        # Add node and relationship pattern
        if from_label_str:
            query += f"(a:{from_label_str})"
        else:
            query += "(a)"
        
        query += f"-[r:{relationship_type}]->"
        
        if to_label_str:
            query += f"(b:{to_label_str})"
        else:
            query += "(b)"
        
        # Add WHERE clauses for node and relationship matching
        where_clauses = []
        
        for key, value in from_node_properties.items():
            where_clauses.append(f"a.{key} = $from_{key}")
        
        for key, value in to_node_properties.items():
            where_clauses.append(f"b.{key} = $to_{key}")
        
        for key, value in match_properties.items():
            where_clauses.append(f"r.{key} = $rel_{key}")
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Add ORDER BY clause if specified
        if order_by:
            if order_by.startswith("a."):
                query += f" ORDER BY {order_by} {order_direction}"
            elif order_by.startswith("b."):
                query += f" ORDER BY {order_by} {order_direction}"
            elif order_by.startswith("r."):
                query += f" ORDER BY {order_by} {order_direction}"
            else:
                query += f" ORDER BY r.{order_by} {order_direction}"
        
        # Add SKIP clause if specified
        if skip:
            query += f" SKIP {skip}"
        
        # Add LIMIT clause if specified
        if limit:
            query += f" LIMIT {limit}"
        
        query += " RETURN a, r, b"
        
        # Prepare parameters
        parameters = {}
        for key, value in from_node_properties.items():
            parameters[f"from_{key}"] = value
        
        for key, value in to_node_properties.items():
            parameters[f"to_{key}"] = value
        
        for key, value in match_properties.items():
            parameters[f"rel_{key}"] = value
        
        try:
            result = await self._run_query(database, query, parameters)
            
            return {
                "status": "success",
                "data": result["data"],
                "error": None,
                "stats": result["summary"].get("counters") if result["summary"] else None,
                "execution_time": result["execution_time"],
                "count": result["count"],
                "summary": result["summary"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "stats": None,
                "execution_time": 0,
                "count": 0,
                "summary": None
            }
    
    async def operation_update_relationship(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update relationships.
        
        Args:
            params: Parameters for updating relationships
            
        Returns:
            Operation result with updated relationships
        """
        database = params.get("database", "neo4j")
        relationship_type = params.get("relationship_type")
        from_node_labels = params.get("from_node_labels", [])
        from_node_properties = params.get("from_node_properties", {})
        to_node_labels = params.get("to_node_labels", [])
        to_node_properties = params.get("to_node_properties", {})
        match_properties = params.get("match_properties", {})
        update_properties = params.get("update_properties", {})
        return_nodes = params.get("return_nodes", True)
        
        # Construct the Cypher query
        from_label_str = ":".join(from_node_labels) if from_node_labels else ""
        to_label_str = ":".join(to_node_labels) if to_node_labels else ""
        
        query = "MATCH "
        
        # Add node and relationship pattern
        if from_label_str:
            query += f"(a:{from_label_str})"
        else:
            query += "(a)"
        
        query += f"-[r:{relationship_type}]->"
        
        if to_label_str:
            query += f"(b:{to_label_str})"
        else:
            query += "(b)"
        
        # Add WHERE clauses for node and relationship matching
        where_clauses = []
        
        for key, value in from_node_properties.items():
            where_clauses.append(f"a.{key} = $from_{key}")
        
        for key, value in to_node_properties.items():
            where_clauses.append(f"b.{key} = $to_{key}")
        
        for key, value in match_properties.items():
            where_clauses.append(f"r.{key} = $rel_{key}")
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Add SET clause for updates
        if update_properties:
            query += " SET "
            update_clauses = []
            for key in update_properties.keys():
                update_clauses.append(f"r.{key} = $update_{key}")
            query += ", ".join(update_clauses)
        
        if return_nodes:
            query += " RETURN a, r, b"
        else:
            query += " RETURN count(r) AS count"
        
        # Prepare parameters
        parameters = {}
        for key, value in from_node_properties.items():
            parameters[f"from_{key}"] = value
        
        for key, value in to_node_properties.items():
            parameters[f"to_{key}"] = value
        
        for key, value in match_properties.items():
            parameters[f"rel_{key}"] = value
        
        for key, value in update_properties.items():
            parameters[f"update_{key}"] = value
        
        try:
            result = await self._run_query(database, query, parameters)
            
            return {
                "status": "success",
                "data": result["data"],
                "error": None,
                "stats": result["summary"].get("counters") if result["summary"] else None,
                "execution_time": result["execution_time"],
                "count": result["count"],
                "summary": result["summary"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "stats": None,
                "execution_time": 0,
                "count": 0,
                "summary": None
            }
    
    async def operation_delete_relationship(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete relationships.
        
        Args:
            params: Parameters for deleting relationships
            
        Returns:
            Operation result with deletion statistics
        """
        database = params.get("database", "neo4j")
        relationship_type = params.get("relationship_type")
        from_node_labels = params.get("from_node_labels", [])
        from_node_properties = params.get("from_node_properties", {})
        to_node_labels = params.get("to_node_labels", [])
        to_node_properties = params.get("to_node_properties", {})
        match_properties = params.get("match_properties", {})
        
        # Construct the Cypher query
        from_label_str = ":".join(from_node_labels) if from_node_labels else ""
        to_label_str = ":".join(to_node_labels) if to_node_labels else ""
        
        query = "MATCH "
        
        # Add node and relationship pattern
        if from_label_str:
            query += f"(a:{from_label_str})"
        else:
            query += "(a)"
        
        query += f"-[r:{relationship_type}]->"
        
        if to_label_str:
            query += f"(b:{to_label_str})"
        else:
            query += "(b)"
        
        # Add WHERE clauses for node and relationship matching
        where_clauses = []
        
        for key, value in from_node_properties.items():
            where_clauses.append(f"a.{key} = $from_{key}")
        
        for key, value in to_node_properties.items():
            where_clauses.append(f"b.{key} = $to_{key}")
        
        for key, value in match_properties.items():
            where_clauses.append(f"r.{key} = $rel_{key}")
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " DELETE r RETURN count(r) AS count"
        
        # Prepare parameters
        parameters = {}
        for key, value in from_node_properties.items():
            parameters[f"from_{key}"] = value
        
        for key, value in to_node_properties.items():
            parameters[f"to_{key}"] = value
        
        for key, value in match_properties.items():
            parameters[f"rel_{key}"] = value
        
        try:
            result = await self._run_query(database, query, parameters)
            
            return {
                "status": "success",
                "data": result["data"],
                "error": None,
                "stats": result["summary"].get("counters") if result["summary"] else None,
                "execution_time": result["execution_time"],
                "count": result["count"],
                "summary": result["summary"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "stats": None,
                "execution_time": 0,
                "count": 0,
                "summary": None
            }
    
    async def operation_get_database_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about the Neo4j database.
        
        Args:
            params: Parameters for getting database info
            
        Returns:
            Operation result with database information
        """
        database = params.get("database", "neo4j")
        
        try:
            # Query for database size
            size_query = "CALL dbms.database.size($database) YIELD total, data RETURN total, data"
            size_result = await self._run_query(database, size_query, {"database": database})
            
            # Query for database info
            info_query = "CALL dbms.database.info($database) YIELD status, address, role, requestedStatus, currentStatus, error, default RETURN status, address, role, requestedStatus, currentStatus, error, default"
            info_result = await self._run_query(database, info_query, {"database": database})
            
            # Query for node and relationship counts
            count_query = "MATCH (n) RETURN count(n) as nodeCount UNION ALL MATCH ()-[r]->() RETURN count(r) as relCount"
            count_result = await self._run_query(database, count_query)
            
            # Query for schema info
            schema_query = "CALL db.schema.visualization()"
            schema_result = await self._run_query(database, schema_query)
            
            # Query for constraints and indexes
            constraints_query = "SHOW CONSTRAINTS"
            constraints_result = await self._run_query(database, constraints_query)
            
            indexes_query = "SHOW INDEXES"
            indexes_result = await self._run_query(database, indexes_query)
            
            return {
                "status": "success",
                "data": {
                    "size": size_result["data"][0] if size_result["data"] else None,
                    "info": info_result["data"][0] if info_result["data"] else None,
                    "counts": {
                        "nodes": count_result["data"][0]["nodeCount"] if count_result["data"] and len(count_result["data"]) > 0 else 0,
                        "relationships": count_result["data"][1]["relCount"] if count_result["data"] and len(count_result["data"]) > 1 else 0
                    },
                    "schema": schema_result["data"][0] if schema_result["data"] else None,
                    "constraints": constraints_result["data"],
                    "indexes": indexes_result["data"]
                },
                "error": None,
                "stats": None,
                "execution_time": sum([
                    size_result["execution_time"],
                    info_result["execution_time"],
                    count_result["execution_time"],
                    schema_result["execution_time"],
                    constraints_result["execution_time"],
                    indexes_result["execution_time"]
                ]),
                "count": None,
                "summary": None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "stats": None,
                "execution_time": 0,
                "count": 0,
                "summary": None
            }
    
    async def close(self):
        """Close resources used by this node."""
        if self.driver:
            self.driver.close()
            self.driver = None

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("neo4j", Neo4jNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register Neo4jNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")

# Main test suite for Neo4jNode
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Neo4jNode Test Suite ===")
        
        # Create an instance of the Neo4jNode
        node = Neo4jNode()
        
        # Neo4j connection parameters - update with your Neo4j instance details
        neo4j_params = {
            "uri": "bolt://localhost:7687",  # Update with your Neo4j URI
            "username": "neo4j",             # Update with your Neo4j username
            "password": "password",          # Update with your Neo4j password
            "database": "neo4j"
        }
        
        # Test cases
        test_cases = [
            {
                "name": "Run Simple Query",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.RUN_QUERY,
                    "query": "RETURN 1 AS test"
                },
                "expected_status": "success",
                "validation": lambda result: result["data"][0]["test"] == 1
            },
            {
                "name": "Run Transaction",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.RUN_TRANSACTION,
                    "queries": [
                        {
                            "query": "RETURN 1 AS test1"
                        },
                        {
                            "query": "RETURN 2 AS test2"
                        }
                    ]
                },
                "expected_status": "success",
                "validation": lambda result: len(result["data"]) == 2
            },
            {
                "name": "Create Node",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.CREATE_NODE,
                    "labels": ["TestNode"],
                    "properties": {
                        "name": "Test Node",
                        "created": int(time.time())
                    }
                },
                "expected_status": "success",
                "validation": lambda result: result["data"][0]["n"]["_labels"] == ["TestNode"]
            },
            {
                "name": "Match Node",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.MATCH_NODE,
                    "labels": ["TestNode"],
                    "match_properties": {
                        "name": "Test Node"
                    }
                },
                "expected_status": "success",
                "validation": lambda result: len(result["data"]) > 0
            },
            {
                "name": "Update Node",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.UPDATE_NODE,
                    "labels": ["TestNode"],
                    "match_properties": {
                        "name": "Test Node"
                    },
                    "update_properties": {
                        "updated": int(time.time()),
                        "description": "Updated test node"
                    }
                },
                "expected_status": "success",
                "validation": lambda result: "description" in result["data"][0]["n"]
            },
            {
                "name": "Create Relationship",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.CREATE_NODE,
                    "labels": ["TestNode"],
                    "properties": {
                        "name": "Related Node",
                        "created": int(time.time())
                    }
                },
                "expected_status": "success"
            },
            {
                "name": "Create Relationship Between Nodes",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.CREATE_RELATIONSHIP,
                    "relationship_type": "RELATED_TO",
                    "from_node_labels": ["TestNode"],
                    "from_node_properties": {
                        "name": "Test Node"
                    },
                    "to_node_labels": ["TestNode"],
                    "to_node_properties": {
                        "name": "Related Node"
                    },
                    "properties": {
                        "since": int(time.time())
                    }
                },
                "expected_status": "success",
                "validation": lambda result: result["data"][0]["r"]["_type"] == "RELATED_TO"
            },
            {
                "name": "Match Relationship",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.MATCH_RELATIONSHIP,
                    "relationship_type": "RELATED_TO",
                    "from_node_labels": ["TestNode"],
                    "to_node_labels": ["TestNode"]
                },
                "expected_status": "success",
                "validation": lambda result: len(result["data"]) > 0
            },
            {
                "name": "Update Relationship",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.UPDATE_RELATIONSHIP,
                    "relationship_type": "RELATED_TO",
                    "from_node_labels": ["TestNode"],
                    "to_node_labels": ["TestNode"],
                    "update_properties": {
                        "updated": int(time.time()),
                        "description": "Updated relationship"
                    }
                },
                "expected_status": "success",
                "validation": lambda result: "description" in result["data"][0]["r"]
            },
            {
                "name": "Delete Relationship",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.DELETE_RELATIONSHIP,
                    "relationship_type": "RELATED_TO",
                    "from_node_labels": ["TestNode"],
                    "to_node_labels": ["TestNode"]
                },
                "expected_status": "success",
                "validation": lambda result: result["data"][0]["count"] > 0
            },
            {
                "name": "Delete Nodes",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.DELETE_NODE,
                    "labels": ["TestNode"],
                    "detach_delete": True
                },
                "expected_status": "success",
                "validation": lambda result: result["data"][0]["count"] >= 2
            },
            {
                "name": "Get Database Info",
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.GET_DATABASE_INFO
                },
                "expected_status": "success"
            }
        ]
        
        # Run all test cases
        total_tests = len(test_cases)
        passed_tests = 0
        
        for test_case in test_cases:
            print(f"\nRunning test: {test_case['name']}")
            
            try:
                # Prepare node data
                node_data = {
                    "params": test_case["params"]
                }
                
                # Execute the node
                result = await node.execute(node_data)
                
                # Check if the result status matches expected status
                if result["status"] == test_case["expected_status"]:
                    # Run additional validation if provided
                    if "validation" in test_case:
                        validation_func = test_case["validation"]
                        if validation_func(result):
                            print(f"✅ PASS: {test_case['name']} - Status: {result['status']} - Validation passed")
                            passed_tests += 1
                        else:
                            print(f"❌ FAIL: {test_case['name']} - Validation failed")
                            print(f"Response: {result}")
                    else:
                        print(f"✅ PASS: {test_case['name']} - Status: {result['status']}")
                        passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")
        
        # Additional manual tests for specific scenarios
        print("\n=== Manual Test: Complex Cypher Query ===")
        
        # Test a more complex Cypher query
        complex_query_result = await node.execute({
            "params": {
                **neo4j_params,
                "operation": Neo4jOperationType.RUN_QUERY,
                "query": """
                CREATE (n:ComplexTest {name: $name, created: timestamp()})
                WITH n
                CREATE (m:ComplexTest {name: $related_name, created: timestamp()})
                CREATE (n)-[r:COMPLEX_REL {since: timestamp()}]->(m)
                RETURN n, r, m
                """,
                "parameters": {
                    "name": "Complex Test Node",
                    "related_name": "Complex Related Node"
                }
            }
        })
        
        print(f"Complex Query Result: Status={complex_query_result['status']}")
        
        # Clean up after complex query test
        await node.execute({
            "params": {
                **neo4j_params,
                "operation": Neo4jOperationType.RUN_QUERY,
                "query": "MATCH (n:ComplexTest) DETACH DELETE n",
                "parameters": {}
            }
        })
        
        print("\n=== Performance Test: Multiple Concurrent Queries ===")
        
        # Perform multiple concurrent queries to test performance
        async def run_concurrent_queries():
            tasks = []
            start_time = time.time()
            
            for i in range(5):
                task = node.execute({
                    "params": {
                        **neo4j_params,
                        "operation": Neo4jOperationType.RUN_QUERY,
                        "query": f"CREATE (n:PerfTest{{id:{i}, created:timestamp()}}) RETURN n",
                        "parameters": {}
                    }
                })
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Clean up performance test nodes
            await node.execute({
                "params": {
                    **neo4j_params,
                    "operation": Neo4jOperationType.RUN_QUERY,
                    "query": "MATCH (n:PerfTest) DELETE n",
                    "parameters": {}
                }
            })
            
            successful = sum(1 for r in results if r["status"] == "success")
            print(f"Completed {len(tasks)} concurrent queries in {end_time - start_time:.4f} seconds")
            print(f"Successful queries: {successful}/{len(tasks)}")
        
        await run_concurrent_queries()
        
        print("\n=== Error Handling Test ===")
        
        # Test with invalid query
        error_result = await node.execute({
            "params": {
                **neo4j_params,
                "operation": Neo4jOperationType.RUN_QUERY,
                "query": "THIS IS NOT A VALID CYPHER QUERY",
                "parameters": {}
            }
        })
        
        print(f"Error Handling Test: Status={error_result['status']}, Error={error_result['error']}")
        
        # Close the node
        await node.close()
        print("\nAll tests completed!")
    
    # Run the async tests if this file is executed directly
    asyncio.run(run_tests())