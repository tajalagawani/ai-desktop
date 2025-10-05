"""
Pinecone Node - Comprehensive integration with Pinecone vector database API
Provides access to all Pinecone operations including vector operations, index management, namespace operations, and statistical queries.
"""

import logging
import json
import asyncio
import time
import os
import ssl
import base64
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timezone
from urllib.parse import urlencode

# Import HTTP client for API calls
import aiohttp
import certifi

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from .base_node import (
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

class PineconeOperation:
    """Operations available on Pinecone Vector Database API."""
    
    # Index Operations
    CREATE_INDEX = "create_index"
    DELETE_INDEX = "delete_index"
    LIST_INDEXES = "list_indexes"
    DESCRIBE_INDEX = "describe_index"
    CONFIGURE_INDEX = "configure_index"
    
    # Vector Operations
    UPSERT_VECTORS = "upsert_vectors"
    DELETE_VECTORS = "delete_vectors"
    DELETE_ALL_VECTORS = "delete_all_vectors"
    FETCH_VECTORS = "fetch_vectors"
    UPDATE_VECTOR = "update_vector"
    
    # Query Operations
    QUERY_VECTORS = "query_vectors"
    SIMILARITY_SEARCH = "similarity_search"
    
    # Namespace Operations
    LIST_NAMESPACES = "list_namespaces"
    DELETE_NAMESPACE = "delete_namespace"
    
    # Index Statistics
    DESCRIBE_INDEX_STATS = "describe_index_stats"
    
    # Collection Operations
    CREATE_COLLECTION = "create_collection"
    DELETE_COLLECTION = "delete_collection"
    LIST_COLLECTIONS = "list_collections"
    DESCRIBE_COLLECTION = "describe_collection"

class PineconeNode(BaseNode):
    """
    Node for interacting with Pinecone vector database API.
    Provides comprehensive functionality for vector operations, index management, and similarity search capabilities.
    """
    
    BASE_URL = "https://controller.{environment}.pinecone.io"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Pinecone node."""
        return NodeSchema(
            node_type="pinecone",
            version="1.0.0",
            description="Comprehensive integration with Pinecone vector database API for vector operations, index management, and similarity search capabilities",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Pinecone API",
                    required=True,
                    enum=[
                        PineconeOperation.CREATE_INDEX,
                        PineconeOperation.DELETE_INDEX,
                        PineconeOperation.LIST_INDEXES,
                        PineconeOperation.DESCRIBE_INDEX,
                        PineconeOperation.CONFIGURE_INDEX,
                        PineconeOperation.UPSERT_VECTORS,
                        PineconeOperation.DELETE_VECTORS,
                        PineconeOperation.DELETE_ALL_VECTORS,
                        PineconeOperation.FETCH_VECTORS,
                        PineconeOperation.UPDATE_VECTOR,
                        PineconeOperation.QUERY_VECTORS,
                        PineconeOperation.SIMILARITY_SEARCH,
                        PineconeOperation.LIST_NAMESPACES,
                        PineconeOperation.DELETE_NAMESPACE,
                        PineconeOperation.DESCRIBE_INDEX_STATS,
                        PineconeOperation.CREATE_COLLECTION,
                        PineconeOperation.DELETE_COLLECTION,
                        PineconeOperation.LIST_COLLECTIONS,
                        PineconeOperation.DESCRIBE_COLLECTION
                    ]
                ),
                NodeParameter(
                    name="api_key",
                    type=NodeParameterType.SECRET,
                    description="Pinecone API key for authentication",
                    required=True
                ),
                NodeParameter(
                    name="environment",
                    type=NodeParameterType.STRING,
                    description="Pinecone environment (e.g., us-west1-gcp)",
                    required=True
                ),
                NodeParameter(
                    name="index_name",
                    type=NodeParameterType.STRING,
                    description="Name of the Pinecone index",
                    required=False
                ),
                NodeParameter(
                    name="dimension",
                    type=NodeParameterType.NUMBER,
                    description="Vector dimension for index creation",
                    required=False
                ),
                NodeParameter(
                    name="metric",
                    type=NodeParameterType.STRING,
                    description="Distance metric for similarity calculation",
                    required=False,
                    default="cosine",
                    enum=["cosine", "euclidean", "dotproduct"]
                ),
                NodeParameter(
                    name="vectors",
                    type=NodeParameterType.ARRAY,
                    description="Array of vectors for upsert operations",
                    required=False
                ),
                NodeParameter(
                    name="vector_ids",
                    type=NodeParameterType.ARRAY,
                    description="Array of vector IDs for fetch/delete operations",
                    required=False
                ),
                NodeParameter(
                    name="query_vector",
                    type=NodeParameterType.ARRAY,
                    description="Query vector for similarity search",
                    required=False
                ),
                NodeParameter(
                    name="top_k",
                    type=NodeParameterType.NUMBER,
                    description="Number of top similar vectors to return",
                    required=False,
                    default=10
                ),
                NodeParameter(
                    name="namespace",
                    type=NodeParameterType.STRING,
                    description="Namespace for vector operations",
                    required=False
                ),
                NodeParameter(
                    name="filter",
                    type=NodeParameterType.OBJECT,
                    description="Metadata filter for query operations",
                    required=False
                ),
                NodeParameter(
                    name="include_metadata",
                    type=NodeParameterType.BOOLEAN,
                    description="Include metadata in results",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="include_values",
                    type=NodeParameterType.BOOLEAN,
                    description="Include vector values in results",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="pod_type",
                    type=NodeParameterType.STRING,
                    description="Pod type for index creation",
                    required=False,
                    default="p1.x1"
                ),
                NodeParameter(
                    name="replicas",
                    type=NodeParameterType.NUMBER,
                    description="Number of replicas for index",
                    required=False,
                    default=1
                ),
                NodeParameter(
                    name="shards",
                    type=NodeParameterType.NUMBER,
                    description="Number of shards for index",
                    required=False,
                    default=1
                ),
                NodeParameter(
                    name="pods",
                    type=NodeParameterType.NUMBER,
                    description="Number of pods for index",
                    required=False,
                    default=1
                ),
                NodeParameter(
                    name="metadata_config",
                    type=NodeParameterType.OBJECT,
                    description="Metadata configuration for index",
                    required=False
                ),
                NodeParameter(
                    name="source_collection",
                    type=NodeParameterType.STRING,
                    description="Source collection for index creation",
                    required=False
                ),
                NodeParameter(
                    name="collection_name",
                    type=NodeParameterType.STRING,
                    description="Name of the collection",
                    required=False
                ),
                NodeParameter(
                    name="sparse_values",
                    type=NodeParameterType.OBJECT,
                    description="Sparse vector values for hybrid search",
                    required=False
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "indexes": NodeParameterType.ARRAY,
                "index_info": NodeParameterType.OBJECT,
                "vectors": NodeParameterType.ARRAY,
                "query_results": NodeParameterType.ARRAY,
                "matches": NodeParameterType.ARRAY,
                "namespaces": NodeParameterType.ARRAY,
                "stats": NodeParameterType.OBJECT,
                "upsert_count": NodeParameterType.NUMBER,
                "delete_count": NodeParameterType.NUMBER,
                "collections": NodeParameterType.ARRAY,
                "collection_info": NodeParameterType.OBJECT,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["pinecone", "vector", "database", "ai", "ml", "api", "integration"],
            author="System",
            documentation_url="https://docs.pinecone.io/reference"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for API key
        if not params.get("api_key"):
            raise NodeValidationError("Pinecone API key is required")
            
        # Check for environment
        if not params.get("environment"):
            raise NodeValidationError("Pinecone environment is required")
            
        # Validate operation-specific requirements
        if operation in [PineconeOperation.CREATE_INDEX]:
            if not params.get("index_name"):
                raise NodeValidationError("Index name is required for index creation")
            if not params.get("dimension"):
                raise NodeValidationError("Dimension is required for index creation")
                
        elif operation in [PineconeOperation.DELETE_INDEX, PineconeOperation.DESCRIBE_INDEX,
                          PineconeOperation.CONFIGURE_INDEX, PineconeOperation.DESCRIBE_INDEX_STATS]:
            if not params.get("index_name"):
                raise NodeValidationError("Index name is required for this operation")
                
        elif operation in [PineconeOperation.UPSERT_VECTORS]:
            if not params.get("index_name"):
                raise NodeValidationError("Index name is required for vector operations")
            if not params.get("vectors"):
                raise NodeValidationError("Vectors are required for upsert operation")
                
        elif operation in [PineconeOperation.DELETE_VECTORS, PineconeOperation.FETCH_VECTORS]:
            if not params.get("index_name"):
                raise NodeValidationError("Index name is required for vector operations")
            if not params.get("vector_ids"):
                raise NodeValidationError("Vector IDs are required for this operation")
                
        elif operation in [PineconeOperation.QUERY_VECTORS, PineconeOperation.SIMILARITY_SEARCH]:
            if not params.get("index_name"):
                raise NodeValidationError("Index name is required for query operations")
            if not params.get("query_vector"):
                raise NodeValidationError("Query vector is required for search operations")
                
        elif operation in [PineconeOperation.CREATE_COLLECTION]:
            if not params.get("collection_name"):
                raise NodeValidationError("Collection name is required for collection creation")
            if not params.get("source_collection"):
                raise NodeValidationError("Source collection is required for collection creation")
                
        elif operation in [PineconeOperation.DELETE_COLLECTION, PineconeOperation.DESCRIBE_COLLECTION]:
            if not params.get("collection_name"):
                raise NodeValidationError("Collection name is required for this operation")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Pinecone node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Execute the appropriate operation
            if operation == PineconeOperation.CREATE_INDEX:
                return await self._operation_create_index(validated_data)
            elif operation == PineconeOperation.DELETE_INDEX:
                return await self._operation_delete_index(validated_data)
            elif operation == PineconeOperation.LIST_INDEXES:
                return await self._operation_list_indexes(validated_data)
            elif operation == PineconeOperation.DESCRIBE_INDEX:
                return await self._operation_describe_index(validated_data)
            elif operation == PineconeOperation.CONFIGURE_INDEX:
                return await self._operation_configure_index(validated_data)
            elif operation == PineconeOperation.UPSERT_VECTORS:
                return await self._operation_upsert_vectors(validated_data)
            elif operation == PineconeOperation.DELETE_VECTORS:
                return await self._operation_delete_vectors(validated_data)
            elif operation == PineconeOperation.DELETE_ALL_VECTORS:
                return await self._operation_delete_all_vectors(validated_data)
            elif operation == PineconeOperation.FETCH_VECTORS:
                return await self._operation_fetch_vectors(validated_data)
            elif operation == PineconeOperation.UPDATE_VECTOR:
                return await self._operation_update_vector(validated_data)
            elif operation == PineconeOperation.QUERY_VECTORS:
                return await self._operation_query_vectors(validated_data)
            elif operation == PineconeOperation.SIMILARITY_SEARCH:
                return await self._operation_similarity_search(validated_data)
            elif operation == PineconeOperation.LIST_NAMESPACES:
                return await self._operation_list_namespaces(validated_data)
            elif operation == PineconeOperation.DELETE_NAMESPACE:
                return await self._operation_delete_namespace(validated_data)
            elif operation == PineconeOperation.DESCRIBE_INDEX_STATS:
                return await self._operation_describe_index_stats(validated_data)
            elif operation == PineconeOperation.CREATE_COLLECTION:
                return await self._operation_create_collection(validated_data)
            elif operation == PineconeOperation.DELETE_COLLECTION:
                return await self._operation_delete_collection(validated_data)
            elif operation == PineconeOperation.LIST_COLLECTIONS:
                return await self._operation_list_collections(validated_data)
            elif operation == PineconeOperation.DESCRIBE_COLLECTION:
                return await self._operation_describe_collection(validated_data)
            else:
                error_message = f"Unknown operation: {operation}"
                logger.error(error_message)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_message,
                    "status_code": None,
                    "response_headers": None
                }
                
        except Exception as e:
            error_message = f"Error in Pinecone node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "status_code": None,
                "response_headers": None
            }
        finally:
            # Clean up session
            await self._cleanup_session()
    
    async def _init_session(self):
        """Initialize HTTP session."""
        if not self.session:
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(connector=connector)
    
    async def _cleanup_session(self):
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any], 
                          data: Optional[Dict[str, Any]] = None, index_host: Optional[str] = None) -> Dict[str, Any]:
        """Make an HTTP request to the Pinecone API."""
        if index_host:
            # Use index-specific host for vector operations
            url = f"https://{index_host}/{endpoint}"
        else:
            # Use controller host for management operations
            environment = params.get("environment")
            base_url = self.BASE_URL.format(environment=environment)
            url = f"{base_url}/{endpoint}"
        
        headers = {
            "Api-Key": params.get("api_key"),
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                response_headers = dict(response.headers)
                
                # Handle different response content types
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Pinecone API error {response.status}: {response_data}"
                    logger.error(error_message)
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                return {
                    "status": "success",
                    "result": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
        except aiohttp.ClientError as e:
            error_message = f"HTTP error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "error": error_message,
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    # -------------------------
    # Index Operations
    # -------------------------
    
    async def _operation_create_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Pinecone index."""
        index_name = params.get("index_name")
        dimension = params.get("dimension")
        metric = params.get("metric", "cosine")
        pod_type = params.get("pod_type", "p1.x1")
        replicas = params.get("replicas", 1)
        shards = params.get("shards", 1)
        pods = params.get("pods", 1)
        metadata_config = params.get("metadata_config")
        source_collection = params.get("source_collection")
        
        request_data = {
            "name": index_name,
            "dimension": dimension,
            "metric": metric,
            "pod_type": pod_type,
            "replicas": replicas,
            "shards": shards,
            "pods": pods
        }
        
        if metadata_config:
            request_data["metadata_config"] = metadata_config
        if source_collection:
            request_data["source_collection"] = source_collection
        
        result = await self._make_request("POST", "databases", params, request_data)
        
        if result["status"] == "success":
            result["index_info"] = result["result"]
        
        return result
    
    async def _operation_delete_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Pinecone index."""
        index_name = params.get("index_name")
        
        result = await self._make_request("DELETE", f"databases/{index_name}", params)
        return result
    
    async def _operation_list_indexes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all Pinecone indexes."""
        result = await self._make_request("GET", "databases", params)
        
        if result["status"] == "success":
            result["indexes"] = result["result"]
        
        return result
    
    async def _operation_describe_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Describe a specific Pinecone index."""
        index_name = params.get("index_name")
        
        result = await self._make_request("GET", f"databases/{index_name}", params)
        
        if result["status"] == "success":
            result["index_info"] = result["result"]
        
        return result
    
    async def _operation_configure_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configure an existing Pinecone index."""
        index_name = params.get("index_name")
        replicas = params.get("replicas")
        pod_type = params.get("pod_type")
        
        request_data = {}
        if replicas is not None:
            request_data["replicas"] = replicas
        if pod_type:
            request_data["pod_type"] = pod_type
        
        result = await self._make_request("PATCH", f"databases/{index_name}", params, request_data)
        
        if result["status"] == "success":
            result["index_info"] = result["result"]
        
        return result
    
    # -------------------------
    # Vector Operations
    # -------------------------
    
    async def _get_index_host(self, params: Dict[str, Any]) -> str:
        """Get the index host URL for vector operations."""
        # First get index info to get the host
        index_info_result = await self._operation_describe_index(params)
        if index_info_result["status"] == "success":
            status = index_info_result["result"].get("status", {})
            return status.get("host", "")
        return ""
    
    async def _operation_upsert_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert vectors into a Pinecone index."""
        vectors = params.get("vectors", [])
        namespace = params.get("namespace", "")
        
        request_data = {
            "vectors": vectors
        }
        
        if namespace:
            request_data["namespace"] = namespace
        
        # Get index host
        index_host = await self._get_index_host(params)
        if not index_host:
            return {
                "status": "error",
                "error": "Could not get index host",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        result = await self._make_request("POST", "vectors/upsert", params, request_data, index_host)
        
        if result["status"] == "success":
            result["upsert_count"] = result["result"].get("upsertedCount", 0)
        
        return result
    
    async def _operation_delete_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete specific vectors from a Pinecone index."""
        vector_ids = params.get("vector_ids", [])
        namespace = params.get("namespace", "")
        
        request_data = {
            "ids": vector_ids
        }
        
        if namespace:
            request_data["namespace"] = namespace
        
        # Get index host
        index_host = await self._get_index_host(params)
        if not index_host:
            return {
                "status": "error",
                "error": "Could not get index host",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        result = await self._make_request("POST", "vectors/delete", params, request_data, index_host)
        return result
    
    async def _operation_delete_all_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete all vectors from a Pinecone index."""
        namespace = params.get("namespace", "")
        
        request_data = {
            "deleteAll": True
        }
        
        if namespace:
            request_data["namespace"] = namespace
        
        # Get index host
        index_host = await self._get_index_host(params)
        if not index_host:
            return {
                "status": "error",
                "error": "Could not get index host",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        result = await self._make_request("POST", "vectors/delete", params, request_data, index_host)
        return result
    
    async def _operation_fetch_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch specific vectors from a Pinecone index."""
        vector_ids = params.get("vector_ids", [])
        namespace = params.get("namespace", "")
        
        query_params = {
            "ids": vector_ids
        }
        
        if namespace:
            query_params["namespace"] = namespace
        
        # Convert to query string
        query_string = "&".join([f"ids={id}" for id in vector_ids])
        if namespace:
            query_string += f"&namespace={namespace}"
        
        # Get index host
        index_host = await self._get_index_host(params)
        if not index_host:
            return {
                "status": "error",
                "error": "Could not get index host",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        result = await self._make_request("GET", f"vectors/fetch?{query_string}", params, None, index_host)
        
        if result["status"] == "success":
            result["vectors"] = result["result"].get("vectors", {})
        
        return result
    
    async def _operation_update_vector(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a vector in a Pinecone index."""
        vector_id = params.get("vector_ids", [None])[0] if params.get("vector_ids") else None
        values = params.get("query_vector", [])
        sparse_values = params.get("sparse_values")
        metadata = params.get("metadata_config")
        namespace = params.get("namespace", "")
        
        if not vector_id:
            return {
                "status": "error",
                "error": "Vector ID is required for update operation",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        request_data = {
            "id": vector_id,
            "values": values
        }
        
        if sparse_values:
            request_data["sparseValues"] = sparse_values
        if metadata:
            request_data["setMetadata"] = metadata
        if namespace:
            request_data["namespace"] = namespace
        
        # Get index host
        index_host = await self._get_index_host(params)
        if not index_host:
            return {
                "status": "error",
                "error": "Could not get index host",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        result = await self._make_request("POST", "vectors/update", params, request_data, index_host)
        return result
    
    # -------------------------
    # Query Operations
    # -------------------------
    
    async def _operation_query_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query vectors in a Pinecone index."""
        return await self._operation_similarity_search(params)
    
    async def _operation_similarity_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform similarity search in a Pinecone index."""
        query_vector = params.get("query_vector", [])
        top_k = params.get("top_k", 10)
        namespace = params.get("namespace", "")
        filter_obj = params.get("filter")
        include_metadata = params.get("include_metadata", True)
        include_values = params.get("include_values", False)
        sparse_values = params.get("sparse_values")
        
        request_data = {
            "vector": query_vector,
            "topK": top_k,
            "includeMetadata": include_metadata,
            "includeValues": include_values
        }
        
        if namespace:
            request_data["namespace"] = namespace
        if filter_obj:
            request_data["filter"] = filter_obj
        if sparse_values:
            request_data["sparseVector"] = sparse_values
        
        # Get index host
        index_host = await self._get_index_host(params)
        if not index_host:
            return {
                "status": "error",
                "error": "Could not get index host",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        result = await self._make_request("POST", "query", params, request_data, index_host)
        
        if result["status"] == "success":
            result["query_results"] = result["result"]
            result["matches"] = result["result"].get("matches", [])
        
        return result
    
    # -------------------------
    # Namespace Operations
    # -------------------------
    
    async def _operation_list_namespaces(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List namespaces in a Pinecone index."""
        # Get index host
        index_host = await self._get_index_host(params)
        if not index_host:
            return {
                "status": "error",
                "error": "Could not get index host",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        result = await self._make_request("GET", "vectors/list", params, None, index_host)
        
        if result["status"] == "success":
            result["namespaces"] = result["result"].get("namespaces", [])
        
        return result
    
    async def _operation_delete_namespace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a namespace from a Pinecone index."""
        namespace = params.get("namespace")
        
        if not namespace:
            return {
                "status": "error",
                "error": "Namespace is required for delete operation",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        request_data = {
            "deleteAll": True,
            "namespace": namespace
        }
        
        # Get index host
        index_host = await self._get_index_host(params)
        if not index_host:
            return {
                "status": "error",
                "error": "Could not get index host",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        result = await self._make_request("POST", "vectors/delete", params, request_data, index_host)
        return result
    
    # -------------------------
    # Statistics Operations
    # -------------------------
    
    async def _operation_describe_index_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics for a Pinecone index."""
        filter_obj = params.get("filter")
        
        request_data = {}
        if filter_obj:
            request_data["filter"] = filter_obj
        
        # Get index host
        index_host = await self._get_index_host(params)
        if not index_host:
            return {
                "status": "error",
                "error": "Could not get index host",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        result = await self._make_request("POST", "describe_index_stats", params, request_data, index_host)
        
        if result["status"] == "success":
            result["stats"] = result["result"]
        
        return result
    
    # -------------------------
    # Collection Operations
    # -------------------------
    
    async def _operation_create_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Pinecone collection."""
        collection_name = params.get("collection_name")
        source_collection = params.get("source_collection")
        
        request_data = {
            "name": collection_name,
            "source": source_collection
        }
        
        result = await self._make_request("POST", "collections", params, request_data)
        
        if result["status"] == "success":
            result["collection_info"] = result["result"]
        
        return result
    
    async def _operation_delete_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Pinecone collection."""
        collection_name = params.get("collection_name")
        
        result = await self._make_request("DELETE", f"collections/{collection_name}", params)
        return result
    
    async def _operation_list_collections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all Pinecone collections."""
        result = await self._make_request("GET", "collections", params)
        
        if result["status"] == "success":
            result["collections"] = result["result"]
        
        return result
    
    async def _operation_describe_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Describe a specific Pinecone collection."""
        collection_name = params.get("collection_name")
        
        result = await self._make_request("GET", f"collections/{collection_name}", params)
        
        if result["status"] == "success":
            result["collection_info"] = result["result"]
        
        return result


# Utility functions for common Pinecone operations
class PineconeHelpers:
    """Helper functions for common Pinecone operations."""
    
    @staticmethod
    def create_vector(id: str, values: List[float], metadata: Optional[Dict[str, Any]] = None, 
                     sparse_values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a vector object for upsert operations."""
        vector = {
            "id": id,
            "values": values
        }
        if metadata:
            vector["metadata"] = metadata
        if sparse_values:
            vector["sparseValues"] = sparse_values
        return vector
    
    @staticmethod
    def create_sparse_vector(indices: List[int], values: List[float]) -> Dict[str, Any]:
        """Create a sparse vector object."""
        return {
            "indices": indices,
            "values": values
        }
    
    @staticmethod
    def create_metadata_filter(field: str, operator: str, value: Any) -> Dict[str, Any]:
        """Create a metadata filter for queries."""
        return {
            field: {operator: value}
        }
    
    @staticmethod
    def format_query_results(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format query results for easier processing."""
        formatted_results = []
        for match in matches:
            formatted_match = {
                "id": match.get("id"),
                "score": match.get("score"),
                "values": match.get("values", []),
                "metadata": match.get("metadata", {})
            }
            formatted_results.append(formatted_match)
        return formatted_results


# Main test function for Pinecone Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Pinecone Node Test Suite ===")
        
        # Get API key from environment or user input
        api_key = os.environ.get("PINECONE_API_KEY")
        environment = os.environ.get("PINECONE_ENVIRONMENT")
        
        if not api_key:
            print("Pinecone API key not found in environment variables")
            print("Please set PINECONE_API_KEY")
            print("Or provide it when prompted...")
            api_key = input("Enter Pinecone API key: ")
        
        if not environment:
            print("Pinecone environment not found in environment variables")
            print("Please set PINECONE_ENVIRONMENT")
            print("Or provide it when prompted...")
            environment = input("Enter Pinecone environment (e.g., us-west1-gcp): ")
        
        if not api_key or not environment:
            print("Pinecone API key and environment are required for testing")
            return
        
        # Create an instance of the Pinecone Node
        node = PineconeNode()
        
        # Test cases
        test_cases = [
            {
                "name": "List Indexes",
                "params": {
                    "operation": PineconeOperation.LIST_INDEXES,
                    "api_key": api_key,
                    "environment": environment
                },
                "expected_status": "success"
            },
            {
                "name": "List Collections",
                "params": {
                    "operation": PineconeOperation.LIST_COLLECTIONS,
                    "api_key": api_key,
                    "environment": environment
                },
                "expected_status": "success"
            }
        ]
        
        # Run test cases
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
                    print(f"✅ PASS: {test_case['name']} - Status: {result['status']}")
                    if result.get("indexes"):
                        print(f"Indexes found: {len(result['indexes'])}")
                    if result.get("collections"):
                        print(f"Collections found: {len(result['collections'])}")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
                # Add a delay between tests to avoid rate limiting
                await asyncio.sleep(1.0)
                
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")
        
        print("\nAll tests completed!")

    # Run the async tests
    asyncio.run(run_tests())

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("pinecone", PineconeNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register PineconeNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")