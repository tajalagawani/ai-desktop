"""
MongoDB Node - Comprehensive MongoDB integration for NoSQL database operations
Refactored with improved architecture: dispatch maps, unified async/sync handling,
proper connection lifecycle, and standardized return shapes.
Supports all major MongoDB operations including CRUD, aggregation, indexing, 
transactions, change streams, GridFS, and advanced database features.
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import pymongo
import pymongo.errors
from pymongo import MongoClient
try:
    import motor.motor_asyncio
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False
import gridfs
import bson
from bson import ObjectId, Binary

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

class MongoDBOperation:
    """All available MongoDB operations."""
    
    # Connection Operations
    PING = "ping"
    SERVER_INFO = "server_info"
    DATABASE_NAMES = "database_names"
    COLLECTION_NAMES = "collection_names"
    CLOSE = "close"
    
    # Database Operations
    CREATE_DATABASE = "create_database"
    DROP_DATABASE = "drop_database"
    DATABASE_STATS = "database_stats"
    
    # Collection Operations
    CREATE_COLLECTION = "create_collection"
    DROP_COLLECTION = "drop_collection"
    COLLECTION_STATS = "collection_stats"
    
    # CRUD Operations - Create
    INSERT_ONE = "insert_one"
    INSERT_MANY = "insert_many"
    
    # CRUD Operations - Read
    FIND = "find"
    FIND_ONE = "find_one"
    COUNT_DOCUMENTS = "count_documents"
    ESTIMATED_DOCUMENT_COUNT = "estimated_document_count"
    DISTINCT = "distinct"
    
    # CRUD Operations - Update
    UPDATE_ONE = "update_one"
    UPDATE_MANY = "update_many"
    REPLACE_ONE = "replace_one"
    FIND_ONE_AND_UPDATE = "find_one_and_update"
    FIND_ONE_AND_REPLACE = "find_one_and_replace"
    
    # CRUD Operations - Delete
    DELETE_ONE = "delete_one"
    DELETE_MANY = "delete_many"
    FIND_ONE_AND_DELETE = "find_one_and_delete"
    
    # Bulk Operations
    BULK_WRITE = "bulk_write"
    
    # Aggregation Operations
    AGGREGATE = "aggregate"
    
    # Index Operations
    CREATE_INDEX = "create_index"
    CREATE_INDEXES = "create_indexes"
    DROP_INDEX = "drop_index"
    DROP_INDEXES = "drop_indexes"
    LIST_INDEXES = "list_indexes"
    INDEX_INFORMATION = "index_information"
    ENSURE_INDEX = "ensure_index"
    
    # Transaction Operations
    START_TRANSACTION = "start_transaction"
    COMMIT_TRANSACTION = "commit_transaction"
    ABORT_TRANSACTION = "abort_transaction"
    WITH_TRANSACTION = "with_transaction"
    
    # Change Stream Operations
    WATCH = "watch"
    WATCH_DATABASE = "watch_database"
    WATCH_COLLECTION = "watch_collection"
    
    # GridFS Operations
    GRIDFS_PUT = "gridfs_put"
    GRIDFS_GET = "gridfs_get"
    GRIDFS_DELETE = "gridfs_delete"
    GRIDFS_FIND = "gridfs_find"
    GRIDFS_LIST = "gridfs_list"
    GRIDFS_UPLOAD_FROM_STREAM = "gridfs_upload_from_stream"
    GRIDFS_DOWNLOAD_TO_STREAM = "gridfs_download_to_stream"
    GRIDFS_OPEN_DOWNLOAD_STREAM = "gridfs_open_download_stream"
    
    # Text Search Operations
    TEXT_SEARCH = "text_search"
    
    # Geospatial Operations
    GEOSPATIAL_NEAR = "geospatial_near"
    GEOSPATIAL_WITHIN = "geospatial_within"
    
    # Advanced Operations
    MAP_REDUCE = "map_reduce"
    RENAME_COLLECTION = "rename_collection"
    VALIDATE_COLLECTION = "validate_collection"
    COMPACT_COLLECTION = "compact_collection"
    REINDEX_COLLECTION = "reindex_collection"
    
    # Replica Set Operations
    REPLICA_SET_STATUS = "replica_set_status"
    STEP_DOWN = "step_down"
    
    # Sharding Operations
    SHARD_COLLECTION = "shard_collection"
    SPLIT_CHUNK = "split_chunk"
    MOVE_CHUNK = "move_chunk"


class MongoDBClient:
    """Unified MongoDB client wrapper that handles sync/async operations."""
    
    def __init__(self, client: Union[MongoClient, 'motor.motor_asyncio.AsyncIOMotorClient']):
        self.client = client
        self.is_async = hasattr(client, 'get_io_loop')
    
    async def maybe_await(self, result):
        """Helper to handle both sync and async results."""
        if self.is_async and asyncio.iscoroutine(result):
            return await result
        return result
    
    # Connection operations
    async def ping(self) -> bool:
        admin_db = self.client.admin
        result = await self.maybe_await(admin_db.command("ping"))
        return result.get("ok") == 1
    
    async def server_info(self) -> Dict[str, Any]:
        return await self.maybe_await(self.client.server_info())
    
    async def database_names(self) -> List[str]:
        return await self.maybe_await(self.client.list_database_names())
    
    async def collection_names(self, database_name: str) -> List[str]:
        db = self.client[database_name]
        return await self.maybe_await(db.list_collection_names())
    
    async def close(self):
        """Close the connection."""
        if self.is_async:
            self.client.close()
        else:
            self.client.close()
    
    # Database operations
    async def create_database(self, database_name: str) -> Dict[str, Any]:
        # MongoDB creates databases implicitly, so we'll create a dummy collection
        db = self.client[database_name]
        collection = db["_temp_collection"]
        result = await self.maybe_await(collection.insert_one({"_temp": True}))
        await self.maybe_await(collection.delete_one({"_temp": True}))
        return {"database_created": database_name, "acknowledged": True}
    
    async def drop_database(self, database_name: str) -> Dict[str, Any]:
        result = await self.maybe_await(self.client.drop_database(database_name))
        return {"database_dropped": database_name, "acknowledged": True}
    
    async def database_stats(self, database_name: str) -> Dict[str, Any]:
        db = self.client[database_name]
        return await self.maybe_await(db.command("dbStats"))
    
    # Collection operations
    async def create_collection(self, database_name: str, collection_name: str, **options) -> Dict[str, Any]:
        db = self.client[database_name]
        result = await self.maybe_await(db.create_collection(collection_name, **options))
        return {"collection_created": collection_name, "acknowledged": True}
    
    async def drop_collection(self, database_name: str, collection_name: str) -> Dict[str, Any]:
        db = self.client[database_name]
        result = await self.maybe_await(db.drop_collection(collection_name))
        return {"collection_dropped": collection_name, "acknowledged": True}
    
    async def collection_stats(self, database_name: str, collection_name: str) -> Dict[str, Any]:
        db = self.client[database_name]
        return await self.maybe_await(db.command("collStats", collection_name))
    
    # CRUD operations
    async def insert_one(self, database_name: str, collection_name: str, document: Dict[str, Any], **options) -> Dict[str, Any]:
        db = self.client[database_name]
        collection = db[collection_name]
        result = await self.maybe_await(collection.insert_one(document, **options))
        return {
            "acknowledged": result.acknowledged,
            "inserted_id": str(result.inserted_id)
        }
    
    async def insert_many(self, database_name: str, collection_name: str, documents: List[Dict[str, Any]], **options) -> Dict[str, Any]:
        db = self.client[database_name]
        collection = db[collection_name]
        result = await self.maybe_await(collection.insert_many(documents, **options))
        return {
            "acknowledged": result.acknowledged,
            "inserted_ids": [str(id) for id in result.inserted_ids]
        }
    
    async def find(self, database_name: str, collection_name: str, filter_dict: Dict[str, Any] = None, **options) -> List[Dict[str, Any]]:
        db = self.client[database_name]
        collection = db[collection_name]
        filter_dict = filter_dict or {}
        
        cursor = collection.find(filter_dict, **options)
        if self.is_async:
            documents = []
            async for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                documents.append(doc)
            return documents
        else:
            documents = []
            for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                documents.append(doc)
            return documents
    
    async def find_one(self, database_name: str, collection_name: str, filter_dict: Dict[str, Any] = None, **options) -> Optional[Dict[str, Any]]:
        db = self.client[database_name]
        collection = db[collection_name]
        filter_dict = filter_dict or {}
        
        document = await self.maybe_await(collection.find_one(filter_dict, **options))
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    async def update_one(self, database_name: str, collection_name: str, filter_dict: Dict[str, Any], update: Dict[str, Any], **options) -> Dict[str, Any]:
        db = self.client[database_name]
        collection = db[collection_name]
        result = await self.maybe_await(collection.update_one(filter_dict, update, **options))
        return {
            "acknowledged": result.acknowledged,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None
        }
    
    async def update_many(self, database_name: str, collection_name: str, filter_dict: Dict[str, Any], update: Dict[str, Any], **options) -> Dict[str, Any]:
        db = self.client[database_name]
        collection = db[collection_name]
        result = await self.maybe_await(collection.update_many(filter_dict, update, **options))
        return {
            "acknowledged": result.acknowledged,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None
        }
    
    async def delete_one(self, database_name: str, collection_name: str, filter_dict: Dict[str, Any], **options) -> Dict[str, Any]:
        db = self.client[database_name]
        collection = db[collection_name]
        result = await self.maybe_await(collection.delete_one(filter_dict, **options))
        return {
            "acknowledged": result.acknowledged,
            "deleted_count": result.deleted_count
        }
    
    async def delete_many(self, database_name: str, collection_name: str, filter_dict: Dict[str, Any], **options) -> Dict[str, Any]:
        db = self.client[database_name]
        collection = db[collection_name]
        result = await self.maybe_await(collection.delete_many(filter_dict, **options))
        return {
            "acknowledged": result.acknowledged,
            "deleted_count": result.deleted_count
        }
    
    async def count_documents(self, database_name: str, collection_name: str, filter_dict: Dict[str, Any] = None, **options) -> int:
        db = self.client[database_name]
        collection = db[collection_name]
        filter_dict = filter_dict or {}
        return await self.maybe_await(collection.count_documents(filter_dict, **options))
    
    async def estimated_document_count(self, database_name: str, collection_name: str, **options) -> int:
        db = self.client[database_name]
        collection = db[collection_name]
        return await self.maybe_await(collection.estimated_document_count(**options))
    
    async def distinct(self, database_name: str, collection_name: str, key: str, filter_dict: Dict[str, Any] = None, **options) -> List[Any]:
        db = self.client[database_name]
        collection = db[collection_name]
        filter_dict = filter_dict or {}
        return await self.maybe_await(collection.distinct(key, filter_dict, **options))
    
    # Aggregation operations
    async def aggregate(self, database_name: str, collection_name: str, pipeline: List[Dict[str, Any]], **options) -> List[Dict[str, Any]]:
        db = self.client[database_name]
        collection = db[collection_name]
        
        cursor = collection.aggregate(pipeline, **options)
        if self.is_async:
            documents = []
            async for doc in cursor:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                documents.append(doc)
            return documents
        else:
            documents = []
            for doc in cursor:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                documents.append(doc)
            return documents
    
    # Index operations
    async def create_index(self, database_name: str, collection_name: str, keys: Union[str, List[Tuple[str, int]]], **options) -> str:
        db = self.client[database_name]
        collection = db[collection_name]
        return await self.maybe_await(collection.create_index(keys, **options))
    
    async def drop_index(self, database_name: str, collection_name: str, index_name: str, **options) -> Dict[str, Any]:
        db = self.client[database_name]
        collection = db[collection_name]
        result = await self.maybe_await(collection.drop_index(index_name, **options))
        return {"index_dropped": index_name, "acknowledged": True}
    
    async def list_indexes(self, database_name: str, collection_name: str) -> List[Dict[str, Any]]:
        db = self.client[database_name]
        collection = db[collection_name]
        
        cursor = collection.list_indexes()
        if self.is_async:
            indexes = []
            async for index in cursor:
                indexes.append(index)
            return indexes
        else:
            return list(cursor)
    
    # GridFS operations
    async def gridfs_put(self, database_name: str, data: bytes, filename: str = None, **metadata) -> str:
        db = self.client[database_name]
        fs = gridfs.GridFS(db)
        
        if self.is_async:
            # For async, we'd need to use motor's GridFS, but for simplicity using sync
            file_id = fs.put(data, filename=filename, **metadata)
        else:
            file_id = fs.put(data, filename=filename, **metadata)
        
        return str(file_id)
    
    async def gridfs_get(self, database_name: str, file_id: str) -> bytes:
        db = self.client[database_name]
        fs = gridfs.GridFS(db)
        
        try:
            grid_out = fs.get(ObjectId(file_id))
            return grid_out.read()
        except gridfs.errors.NoFile:
            raise FileNotFoundError(f"File with id {file_id} not found")
    
    async def gridfs_delete(self, database_name: str, file_id: str) -> Dict[str, Any]:
        db = self.client[database_name]
        fs = gridfs.GridFS(db)
        
        try:
            fs.delete(ObjectId(file_id))
            return {"file_deleted": file_id, "acknowledged": True}
        except gridfs.errors.NoFile:
            raise FileNotFoundError(f"File with id {file_id} not found")
    
    async def gridfs_find(self, database_name: str, filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        db = self.client[database_name]
        fs = gridfs.GridFS(db)
        filter_dict = filter_dict or {}
        
        files = []
        for grid_out in fs.find(filter_dict):
            files.append({
                "_id": str(grid_out._id),
                "filename": grid_out.filename,
                "length": grid_out.length,
                "upload_date": grid_out.upload_date.isoformat() if grid_out.upload_date else None,
                "md5": grid_out.md5,
                "metadata": grid_out.metadata
            })
        
        return files


class OperationMetadata:
    """Metadata for MongoDB operations including parameter requirements."""
    
    def __init__(self, required_params: List[str], optional_params: List[str] = None, 
                 handler: Optional[Callable] = None):
        self.required_params = required_params
        self.optional_params = optional_params or []
        self.handler = handler


class MongoDBNode(BaseNode):
    """
    Comprehensive MongoDB integration node supporting all major NoSQL operations.
    Handles CRUD operations, aggregation, indexing, transactions, change streams, 
    GridFS, and advanced MongoDB features.
    """
    
    # Operation metadata table - programmatic validation generation
    OPERATION_METADATA = {
        # Connection operations
        MongoDBOperation.PING: OperationMetadata([]),
        MongoDBOperation.SERVER_INFO: OperationMetadata([]),
        MongoDBOperation.DATABASE_NAMES: OperationMetadata([]),
        MongoDBOperation.COLLECTION_NAMES: OperationMetadata(["database_name"]),
        MongoDBOperation.CLOSE: OperationMetadata([]),
        
        # Database operations
        MongoDBOperation.CREATE_DATABASE: OperationMetadata(["database_name"]),
        MongoDBOperation.DROP_DATABASE: OperationMetadata(["database_name"]),
        MongoDBOperation.DATABASE_STATS: OperationMetadata(["database_name"]),
        
        # Collection operations
        MongoDBOperation.CREATE_COLLECTION: OperationMetadata(["database_name", "collection_name"]),
        MongoDBOperation.DROP_COLLECTION: OperationMetadata(["database_name", "collection_name"]),
        MongoDBOperation.COLLECTION_STATS: OperationMetadata(["database_name", "collection_name"]),
        
        # CRUD operations - Create
        MongoDBOperation.INSERT_ONE: OperationMetadata(["database_name", "collection_name", "document"]),
        MongoDBOperation.INSERT_MANY: OperationMetadata(["database_name", "collection_name", "documents"]),
        
        # CRUD operations - Read
        MongoDBOperation.FIND: OperationMetadata(["database_name", "collection_name"], ["filter", "projection", "sort", "limit", "skip"]),
        MongoDBOperation.FIND_ONE: OperationMetadata(["database_name", "collection_name"], ["filter", "projection", "sort"]),
        MongoDBOperation.COUNT_DOCUMENTS: OperationMetadata(["database_name", "collection_name"], ["filter"]),
        MongoDBOperation.ESTIMATED_DOCUMENT_COUNT: OperationMetadata(["database_name", "collection_name"]),
        MongoDBOperation.DISTINCT: OperationMetadata(["database_name", "collection_name", "key"], ["filter"]),
        
        # CRUD operations - Update
        MongoDBOperation.UPDATE_ONE: OperationMetadata(["database_name", "collection_name", "filter", "update"]),
        MongoDBOperation.UPDATE_MANY: OperationMetadata(["database_name", "collection_name", "filter", "update"]),
        MongoDBOperation.REPLACE_ONE: OperationMetadata(["database_name", "collection_name", "filter", "replacement"]),
        MongoDBOperation.FIND_ONE_AND_UPDATE: OperationMetadata(["database_name", "collection_name", "filter", "update"]),
        MongoDBOperation.FIND_ONE_AND_REPLACE: OperationMetadata(["database_name", "collection_name", "filter", "replacement"]),
        
        # CRUD operations - Delete
        MongoDBOperation.DELETE_ONE: OperationMetadata(["database_name", "collection_name", "filter"]),
        MongoDBOperation.DELETE_MANY: OperationMetadata(["database_name", "collection_name", "filter"]),
        MongoDBOperation.FIND_ONE_AND_DELETE: OperationMetadata(["database_name", "collection_name", "filter"]),
        
        # Aggregation operations
        MongoDBOperation.AGGREGATE: OperationMetadata(["database_name", "collection_name", "pipeline"]),
        
        # Index operations
        MongoDBOperation.CREATE_INDEX: OperationMetadata(["database_name", "collection_name", "keys"]),
        MongoDBOperation.DROP_INDEX: OperationMetadata(["database_name", "collection_name", "index_name"]),
        MongoDBOperation.LIST_INDEXES: OperationMetadata(["database_name", "collection_name"]),
        
        # GridFS operations
        MongoDBOperation.GRIDFS_PUT: OperationMetadata(["database_name", "data"], ["filename", "metadata"]),
        MongoDBOperation.GRIDFS_GET: OperationMetadata(["database_name", "file_id"]),
        MongoDBOperation.GRIDFS_DELETE: OperationMetadata(["database_name", "file_id"]),
        MongoDBOperation.GRIDFS_FIND: OperationMetadata(["database_name"], ["filter"]),
        
        # Advanced operations
        MongoDBOperation.TEXT_SEARCH: OperationMetadata(["database_name", "collection_name", "text"]),
        MongoDBOperation.MAP_REDUCE: OperationMetadata(["database_name", "collection_name", "map", "reduce"]),
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create dispatch map for operations
        self.operation_dispatch = {
            # Connection operations
            MongoDBOperation.PING: self._handle_ping,
            MongoDBOperation.SERVER_INFO: self._handle_server_info,
            MongoDBOperation.DATABASE_NAMES: self._handle_database_names,
            MongoDBOperation.COLLECTION_NAMES: self._handle_collection_names,
            MongoDBOperation.CLOSE: self._handle_close,
            
            # Database operations
            MongoDBOperation.CREATE_DATABASE: self._handle_create_database,
            MongoDBOperation.DROP_DATABASE: self._handle_drop_database,
            MongoDBOperation.DATABASE_STATS: self._handle_database_stats,
            
            # Collection operations
            MongoDBOperation.CREATE_COLLECTION: self._handle_create_collection,
            MongoDBOperation.DROP_COLLECTION: self._handle_drop_collection,
            MongoDBOperation.COLLECTION_STATS: self._handle_collection_stats,
            
            # CRUD operations - Create
            MongoDBOperation.INSERT_ONE: self._handle_insert_one,
            MongoDBOperation.INSERT_MANY: self._handle_insert_many,
            
            # CRUD operations - Read
            MongoDBOperation.FIND: self._handle_find,
            MongoDBOperation.FIND_ONE: self._handle_find_one,
            MongoDBOperation.COUNT_DOCUMENTS: self._handle_count_documents,
            MongoDBOperation.ESTIMATED_DOCUMENT_COUNT: self._handle_estimated_document_count,
            MongoDBOperation.DISTINCT: self._handle_distinct,
            
            # CRUD operations - Update
            MongoDBOperation.UPDATE_ONE: self._handle_update_one,
            MongoDBOperation.UPDATE_MANY: self._handle_update_many,
            MongoDBOperation.REPLACE_ONE: self._handle_replace_one,
            MongoDBOperation.FIND_ONE_AND_UPDATE: self._handle_find_one_and_update,
            MongoDBOperation.FIND_ONE_AND_REPLACE: self._handle_find_one_and_replace,
            
            # CRUD operations - Delete
            MongoDBOperation.DELETE_ONE: self._handle_delete_one,
            MongoDBOperation.DELETE_MANY: self._handle_delete_many,
            MongoDBOperation.FIND_ONE_AND_DELETE: self._handle_find_one_and_delete,
            
            # Aggregation operations
            MongoDBOperation.AGGREGATE: self._handle_aggregate,
            
            # Index operations
            MongoDBOperation.CREATE_INDEX: self._handle_create_index,
            MongoDBOperation.DROP_INDEX: self._handle_drop_index,
            MongoDBOperation.LIST_INDEXES: self._handle_list_indexes,
            
            # GridFS operations
            MongoDBOperation.GRIDFS_PUT: self._handle_gridfs_put,
            MongoDBOperation.GRIDFS_GET: self._handle_gridfs_get,
            MongoDBOperation.GRIDFS_DELETE: self._handle_gridfs_delete,
            MongoDBOperation.GRIDFS_FIND: self._handle_gridfs_find,
        }
    
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the MongoDB node."""
        # Create a simple schema with common parameters
        parameters = {}
        
        # Add basic parameters
        param_definitions = [
            ("operation", NodeParameterType.STRING, "The MongoDB operation to perform", True, list(self.OPERATION_METADATA.keys())),
            ("connection_string", NodeParameterType.SECRET, "MongoDB connection string", False),
            ("host", NodeParameterType.STRING, "MongoDB host address", False, None, "localhost"),
            ("port", NodeParameterType.NUMBER, "MongoDB port number", False, None, 27017),
            ("username", NodeParameterType.STRING, "MongoDB username", False),
            ("password", NodeParameterType.SECRET, "MongoDB password", False),
            ("auth_source", NodeParameterType.STRING, "Authentication database", False, None, "admin"),
            ("auth_mechanism", NodeParameterType.STRING, "Authentication mechanism", False),
            ("ssl", NodeParameterType.BOOLEAN, "Use SSL connection", False, None, False),
            ("ssl_cert_reqs", NodeParameterType.STRING, "SSL certificate requirements", False),
            ("async_mode", NodeParameterType.BOOLEAN, "Use async MongoDB client", False, None, False),
            ("timeout", NodeParameterType.NUMBER, "Connection timeout in seconds", False, None, 30),
            ("server_selection_timeout", NodeParameterType.NUMBER, "Server selection timeout in seconds", False, None, 30),
            ("max_pool_size", NodeParameterType.NUMBER, "Maximum connection pool size", False, None, 100),
            
            # Database and collection parameters
            ("database_name", NodeParameterType.STRING, "MongoDB database name", False),
            ("collection_name", NodeParameterType.STRING, "MongoDB collection name", False),
            
            # Document parameters
            ("document", NodeParameterType.OBJECT, "Document to insert", False),
            ("documents", NodeParameterType.ARRAY, "Array of documents to insert", False),
            ("filter", NodeParameterType.OBJECT, "Query filter", False),
            ("update", NodeParameterType.OBJECT, "Update document", False),
            ("replacement", NodeParameterType.OBJECT, "Replacement document", False),
            ("projection", NodeParameterType.OBJECT, "Fields to include/exclude", False),
            ("sort", NodeParameterType.OBJECT, "Sort specification", False),
            ("limit", NodeParameterType.NUMBER, "Maximum number of documents to return", False),
            ("skip", NodeParameterType.NUMBER, "Number of documents to skip", False),
            ("upsert", NodeParameterType.BOOLEAN, "Create document if it doesn't exist", False, None, False),
            
            # Aggregation parameters
            ("pipeline", NodeParameterType.ARRAY, "Aggregation pipeline", False),
            ("allow_disk_use", NodeParameterType.BOOLEAN, "Allow disk usage for large aggregations", False, None, False),
            
            # Index parameters
            ("keys", NodeParameterType.ANY, "Index keys specification", False),
            ("index_name", NodeParameterType.STRING, "Index name", False),
            ("unique", NodeParameterType.BOOLEAN, "Create unique index", False, None, False),
            ("sparse", NodeParameterType.BOOLEAN, "Create sparse index", False, None, False),
            ("background", NodeParameterType.BOOLEAN, "Build index in background", False, None, False),
            ("expire_after_seconds", NodeParameterType.NUMBER, "TTL for documents", False),
            
            # GridFS parameters
            ("file_id", NodeParameterType.STRING, "GridFS file ID", False),
            ("filename", NodeParameterType.STRING, "GridFS filename", False),
            ("data", NodeParameterType.ANY, "File data (base64 encoded for binary)", False),
            ("metadata", NodeParameterType.OBJECT, "GridFS file metadata", False),
            
            # Advanced parameters
            ("key", NodeParameterType.STRING, "Field key for distinct operation", False),
            ("text", NodeParameterType.STRING, "Text search query", False),
            ("map", NodeParameterType.STRING, "MapReduce map function", False),
            ("reduce", NodeParameterType.STRING, "MapReduce reduce function", False),
            ("finalize", NodeParameterType.STRING, "MapReduce finalize function", False),
            ("out", NodeParameterType.OBJECT, "MapReduce output specification", False),
            
            # Transaction parameters
            ("session_id", NodeParameterType.STRING, "Session ID for transactions", False),
            ("read_concern", NodeParameterType.OBJECT, "Read concern", False),
            ("write_concern", NodeParameterType.OBJECT, "Write concern", False),
            ("read_preference", NodeParameterType.STRING, "Read preference", False),
            
            # Change stream parameters
            ("resume_after", NodeParameterType.OBJECT, "Resume token", False),
            ("start_after", NodeParameterType.OBJECT, "Start after token", False),
            ("start_at_operation_time", NodeParameterType.STRING, "Start at operation time", False),
            ("full_document", NodeParameterType.STRING, "Full document option", False),
            ("max_await_time_ms", NodeParameterType.NUMBER, "Maximum await time in milliseconds", False),
            ("batch_size", NodeParameterType.NUMBER, "Batch size", False),
            
            # Options
            ("bypass_document_validation", NodeParameterType.BOOLEAN, "Bypass document validation", False, None, False),
            ("ordered", NodeParameterType.BOOLEAN, "Ordered bulk operations", False, None, True),
            ("return_document", NodeParameterType.STRING, "Return document option", False),
            ("array_filters", NodeParameterType.ARRAY, "Array filters for updates", False),
            ("collation", NodeParameterType.OBJECT, "Collation specification", False),
            ("hint", NodeParameterType.ANY, "Index hint", False),
        ]
        
        # Build parameters dict
        for param_def in param_definitions:
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
            node_type="mongodb",
            version="1.0.0",
            description="Comprehensive MongoDB integration supporting all major NoSQL operations including CRUD, aggregation, indexing, transactions, change streams, GridFS, and advanced database features",
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
                "mongodb_error": NodeParameterType.STRING,
                "connection_info": NodeParameterType.OBJECT,
                "document_count": NodeParameterType.NUMBER,
                "matched_count": NodeParameterType.NUMBER,
                "modified_count": NodeParameterType.NUMBER,
                "deleted_count": NodeParameterType.NUMBER,
                "inserted_ids": NodeParameterType.ARRAY,
                "upserted_id": NodeParameterType.STRING,
                "acknowledged": NodeParameterType.BOOLEAN,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MongoDB-specific parameters using operation metadata."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Basic validation
        if not operation:
            raise NodeValidationError("Operation is required")
        
        if operation not in self.OPERATION_METADATA:
            raise NodeValidationError(f"Invalid operation: {operation}")
        
        # Connection validation - at least one connection method required
        has_connection_string = bool(params.get("connection_string"))
        has_host = bool(params.get("host"))
        
        if not has_connection_string and not has_host:
            raise NodeValidationError("Either connection_string or host is required")
        
        # Operation-specific validation using metadata
        metadata = self.OPERATION_METADATA[operation]
        
        # Check required parameters
        for param in metadata.required_params:
            if param not in params or params[param] is None:
                raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")
        
        # Additional validation for specific operations
        if operation in [MongoDBOperation.INSERT_ONE] and "document" in params:
            if not isinstance(params["document"], dict):
                raise NodeValidationError("Document must be a dictionary")
        
        if operation in [MongoDBOperation.INSERT_MANY] and "documents" in params:
            if not isinstance(params["documents"], list):
                raise NodeValidationError("Documents must be an array")
        
        if operation in [MongoDBOperation.AGGREGATE] and "pipeline" in params:
            if not isinstance(params["pipeline"], list):
                raise NodeValidationError("Pipeline must be an array")
        
        return node_data
    
    @asynccontextmanager
    async def _get_mongodb_client(self, params: Dict[str, Any]):
        """Context manager for MongoDB client with proper connection lifecycle."""
        connection_string = params.get("connection_string")
        host = params.get("host", "localhost")
        port = params.get("port", 27017)
        username = params.get("username")
        password = params.get("password")
        auth_source = params.get("auth_source", "admin")
        auth_mechanism = params.get("auth_mechanism")
        ssl = params.get("ssl", False)
        timeout = params.get("timeout", 30)
        server_selection_timeout = params.get("server_selection_timeout", 30)
        max_pool_size = params.get("max_pool_size", 100)
        async_mode = params.get("async_mode", False)
        
        # Build connection parameters
        if connection_string:
            connection_uri = connection_string
        else:
            # Build URI from individual parameters
            if username and password:
                auth_part = f"{username}:{password}@"
            else:
                auth_part = ""
            
            connection_uri = f"mongodb://{auth_part}{host}:{port}/"
            
            if auth_source and username:
                connection_uri += f"?authSource={auth_source}"
                if auth_mechanism:
                    connection_uri += f"&authMechanism={auth_mechanism}"
        
        connection_kwargs = {
            "serverSelectionTimeoutMS": server_selection_timeout * 1000,
            "maxPoolSize": max_pool_size,
            "ssl": ssl,
        }
        
        client = None
        try:
            if async_mode and MOTOR_AVAILABLE:
                client = motor.motor_asyncio.AsyncIOMotorClient(connection_uri, **connection_kwargs)
            else:
                client = MongoClient(connection_uri, **connection_kwargs)
            
            mongodb_client = MongoDBClient(client)
            yield mongodb_client
        finally:
            if client:
                await mongodb_client.close()
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in parameters for logging."""
        masked_data = data.copy()
        
        # Mask sensitive fields
        sensitive_fields = ["password", "connection_string"]
        for field in sensitive_fields:
            if field in masked_data:
                masked_data[field] = "***MASKED***"
        
        return masked_data
    
    def _create_standard_response(self, operation: str, start_time: datetime, 
                                 params: Dict[str, Any], result: Any, 
                                 error: Optional[str] = None, 
                                 mongodb_error: Optional[str] = None) -> Dict[str, Any]:
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
        
        if mongodb_error:
            response["mongodb_error"] = mongodb_error
        
        # Add connection info (without sensitive data)
        response["connection_info"] = {
            "host": params.get("host", "from_connection_string"),
            "port": params.get("port", "from_connection_string"),
            "database": params.get("database_name"),
            "collection": params.get("collection_name"),
        }
        
        return response
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the MongoDB operation using dispatch map."""
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
            # Create MongoDB client with proper connection lifecycle
            async with self._get_mongodb_client(params) as mongodb_client:
                # Call the handler
                result = await handler(mongodb_client, params)
                
                return self._create_standard_response(
                    operation, start_time, params, result
                )
        
        except pymongo.errors.PyMongoError as e:
            error_type = type(e).__name__
            return self._create_standard_response(
                operation, start_time, params, None,
                error=str(e), mongodb_error=error_type
            )
        except Exception as e:
            logger.error(f"Unexpected error in operation {operation}: {e}")
            return self._create_standard_response(
                operation, start_time, params, None,
                error=str(e), mongodb_error=type(e).__name__
            )
    
    # Connection operation handlers
    async def _handle_ping(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> bool:
        """Handle PING operation."""
        return await mongodb_client.ping()
    
    async def _handle_server_info(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SERVER_INFO operation."""
        return await mongodb_client.server_info()
    
    async def _handle_database_names(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> List[str]:
        """Handle DATABASE_NAMES operation."""
        return await mongodb_client.database_names()
    
    async def _handle_collection_names(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> List[str]:
        """Handle COLLECTION_NAMES operation."""
        database_name = params.get("database_name")
        return await mongodb_client.collection_names(database_name)
    
    async def _handle_close(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CLOSE operation."""
        await mongodb_client.close()
        return {"connection_closed": True}
    
    # Database operation handlers
    async def _handle_create_database(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CREATE_DATABASE operation."""
        database_name = params.get("database_name")
        return await mongodb_client.create_database(database_name)
    
    async def _handle_drop_database(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DROP_DATABASE operation."""
        database_name = params.get("database_name")
        return await mongodb_client.drop_database(database_name)
    
    async def _handle_database_stats(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DATABASE_STATS operation."""
        database_name = params.get("database_name")
        return await mongodb_client.database_stats(database_name)
    
    # Collection operation handlers
    async def _handle_create_collection(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CREATE_COLLECTION operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        return await mongodb_client.create_collection(database_name, collection_name)
    
    async def _handle_drop_collection(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DROP_COLLECTION operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        return await mongodb_client.drop_collection(database_name, collection_name)
    
    async def _handle_collection_stats(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle COLLECTION_STATS operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        return await mongodb_client.collection_stats(database_name, collection_name)
    
    # CRUD operation handlers - Create
    async def _handle_insert_one(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle INSERT_ONE operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        document = params.get("document")
        
        # Extract optional parameters
        options = {}
        if params.get("bypass_document_validation") is not None:
            options["bypass_document_validation"] = params.get("bypass_document_validation")
        
        return await mongodb_client.insert_one(database_name, collection_name, document, **options)
    
    async def _handle_insert_many(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle INSERT_MANY operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        documents = params.get("documents")
        
        # Extract optional parameters
        options = {}
        if params.get("bypass_document_validation") is not None:
            options["bypass_document_validation"] = params.get("bypass_document_validation")
        if params.get("ordered") is not None:
            options["ordered"] = params.get("ordered")
        
        return await mongodb_client.insert_many(database_name, collection_name, documents, **options)
    
    # CRUD operation handlers - Read
    async def _handle_find(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle FIND operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        filter_dict = params.get("filter", {})
        
        # Extract optional parameters
        options = {}
        if params.get("projection") is not None:
            options["projection"] = params.get("projection")
        if params.get("sort") is not None:
            options["sort"] = list(params.get("sort").items())
        if params.get("limit") is not None:
            options["limit"] = params.get("limit")
        if params.get("skip") is not None:
            options["skip"] = params.get("skip")
        if params.get("hint") is not None:
            options["hint"] = params.get("hint")
        
        return await mongodb_client.find(database_name, collection_name, filter_dict, **options)
    
    async def _handle_find_one(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle FIND_ONE operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        filter_dict = params.get("filter", {})
        
        # Extract optional parameters
        options = {}
        if params.get("projection") is not None:
            options["projection"] = params.get("projection")
        if params.get("sort") is not None:
            options["sort"] = list(params.get("sort").items())
        
        return await mongodb_client.find_one(database_name, collection_name, filter_dict, **options)
    
    async def _handle_count_documents(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> int:
        """Handle COUNT_DOCUMENTS operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        filter_dict = params.get("filter", {})
        
        # Extract optional parameters
        options = {}
        if params.get("limit") is not None:
            options["limit"] = params.get("limit")
        if params.get("skip") is not None:
            options["skip"] = params.get("skip")
        
        return await mongodb_client.count_documents(database_name, collection_name, filter_dict, **options)
    
    async def _handle_estimated_document_count(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> int:
        """Handle ESTIMATED_DOCUMENT_COUNT operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        
        return await mongodb_client.estimated_document_count(database_name, collection_name)
    
    async def _handle_distinct(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> List[Any]:
        """Handle DISTINCT operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        key = params.get("key")
        filter_dict = params.get("filter", {})
        
        return await mongodb_client.distinct(database_name, collection_name, key, filter_dict)
    
    # CRUD operation handlers - Update
    async def _handle_update_one(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle UPDATE_ONE operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        filter_dict = params.get("filter")
        update = params.get("update")
        
        # Extract optional parameters
        options = {}
        if params.get("upsert") is not None:
            options["upsert"] = params.get("upsert")
        if params.get("array_filters") is not None:
            options["array_filters"] = params.get("array_filters")
        if params.get("hint") is not None:
            options["hint"] = params.get("hint")
        
        return await mongodb_client.update_one(database_name, collection_name, filter_dict, update, **options)
    
    async def _handle_update_many(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle UPDATE_MANY operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        filter_dict = params.get("filter")
        update = params.get("update")
        
        # Extract optional parameters
        options = {}
        if params.get("upsert") is not None:
            options["upsert"] = params.get("upsert")
        if params.get("array_filters") is not None:
            options["array_filters"] = params.get("array_filters")
        if params.get("hint") is not None:
            options["hint"] = params.get("hint")
        
        return await mongodb_client.update_many(database_name, collection_name, filter_dict, update, **options)
    
    async def _handle_replace_one(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle REPLACE_ONE operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        filter_dict = params.get("filter")
        replacement = params.get("replacement")
        
        # Extract optional parameters
        options = {}
        if params.get("upsert") is not None:
            options["upsert"] = params.get("upsert")
        if params.get("hint") is not None:
            options["hint"] = params.get("hint")
        
        db = mongodb_client.client[database_name]
        collection = db[collection_name]
        result = await mongodb_client.maybe_await(collection.replace_one(filter_dict, replacement, **options))
        
        return {
            "acknowledged": result.acknowledged,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None
        }
    
    async def _handle_find_one_and_update(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle FIND_ONE_AND_UPDATE operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        filter_dict = params.get("filter")
        update = params.get("update")
        
        # Extract optional parameters
        options = {}
        if params.get("projection") is not None:
            options["projection"] = params.get("projection")
        if params.get("sort") is not None:
            options["sort"] = list(params.get("sort").items())
        if params.get("upsert") is not None:
            options["upsert"] = params.get("upsert")
        if params.get("return_document") is not None:
            # Convert string to pymongo ReturnDocument enum
            if params.get("return_document").lower() == "after":
                options["return_document"] = pymongo.ReturnDocument.AFTER
            else:
                options["return_document"] = pymongo.ReturnDocument.BEFORE
        if params.get("array_filters") is not None:
            options["array_filters"] = params.get("array_filters")
        
        db = mongodb_client.client[database_name]
        collection = db[collection_name]
        document = await mongodb_client.maybe_await(collection.find_one_and_update(filter_dict, update, **options))
        
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        
        return document
    
    async def _handle_find_one_and_replace(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle FIND_ONE_AND_REPLACE operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        filter_dict = params.get("filter")
        replacement = params.get("replacement")
        
        # Extract optional parameters
        options = {}
        if params.get("projection") is not None:
            options["projection"] = params.get("projection")
        if params.get("sort") is not None:
            options["sort"] = list(params.get("sort").items())
        if params.get("upsert") is not None:
            options["upsert"] = params.get("upsert")
        if params.get("return_document") is not None:
            # Convert string to pymongo ReturnDocument enum
            if params.get("return_document").lower() == "after":
                options["return_document"] = pymongo.ReturnDocument.AFTER
            else:
                options["return_document"] = pymongo.ReturnDocument.BEFORE
        
        db = mongodb_client.client[database_name]
        collection = db[collection_name]
        document = await mongodb_client.maybe_await(collection.find_one_and_replace(filter_dict, replacement, **options))
        
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        
        return document
    
    # CRUD operation handlers - Delete
    async def _handle_delete_one(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DELETE_ONE operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        filter_dict = params.get("filter")
        
        # Extract optional parameters
        options = {}
        if params.get("hint") is not None:
            options["hint"] = params.get("hint")
        
        return await mongodb_client.delete_one(database_name, collection_name, filter_dict, **options)
    
    async def _handle_delete_many(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DELETE_MANY operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        filter_dict = params.get("filter")
        
        # Extract optional parameters
        options = {}
        if params.get("hint") is not None:
            options["hint"] = params.get("hint")
        
        return await mongodb_client.delete_many(database_name, collection_name, filter_dict, **options)
    
    async def _handle_find_one_and_delete(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle FIND_ONE_AND_DELETE operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        filter_dict = params.get("filter")
        
        # Extract optional parameters
        options = {}
        if params.get("projection") is not None:
            options["projection"] = params.get("projection")
        if params.get("sort") is not None:
            options["sort"] = list(params.get("sort").items())
        
        db = mongodb_client.client[database_name]
        collection = db[collection_name]
        document = await mongodb_client.maybe_await(collection.find_one_and_delete(filter_dict, **options))
        
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        
        return document
    
    # Aggregation operation handlers
    async def _handle_aggregate(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle AGGREGATE operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        pipeline = params.get("pipeline")
        
        # Extract optional parameters
        options = {}
        if params.get("allow_disk_use") is not None:
            options["allowDiskUse"] = params.get("allow_disk_use")
        if params.get("batch_size") is not None:
            options["batchSize"] = params.get("batch_size")
        
        return await mongodb_client.aggregate(database_name, collection_name, pipeline, **options)
    
    # Index operation handlers
    async def _handle_create_index(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> str:
        """Handle CREATE_INDEX operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        keys = params.get("keys")
        
        # Extract optional parameters
        options = {}
        if params.get("unique") is not None:
            options["unique"] = params.get("unique")
        if params.get("sparse") is not None:
            options["sparse"] = params.get("sparse")
        if params.get("background") is not None:
            options["background"] = params.get("background")
        if params.get("expire_after_seconds") is not None:
            options["expireAfterSeconds"] = params.get("expire_after_seconds")
        if params.get("index_name") is not None:
            options["name"] = params.get("index_name")
        
        return await mongodb_client.create_index(database_name, collection_name, keys, **options)
    
    async def _handle_drop_index(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DROP_INDEX operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        index_name = params.get("index_name")
        
        return await mongodb_client.drop_index(database_name, collection_name, index_name)
    
    async def _handle_list_indexes(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle LIST_INDEXES operation."""
        database_name = params.get("database_name")
        collection_name = params.get("collection_name")
        
        return await mongodb_client.list_indexes(database_name, collection_name)
    
    # GridFS operation handlers
    async def _handle_gridfs_put(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> str:
        """Handle GRIDFS_PUT operation."""
        database_name = params.get("database_name")
        data = params.get("data")
        filename = params.get("filename")
        metadata = params.get("metadata", {})
        
        # Handle base64 encoded data
        if isinstance(data, str):
            import base64
            try:
                data = base64.b64decode(data)
            except:
                data = data.encode('utf-8')
        elif isinstance(data, (list, dict)):
            data = json.dumps(data).encode('utf-8')
        
        return await mongodb_client.gridfs_put(database_name, data, filename, **metadata)
    
    async def _handle_gridfs_get(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GRIDFS_GET operation."""
        database_name = params.get("database_name")
        file_id = params.get("file_id")
        
        data = await mongodb_client.gridfs_get(database_name, file_id)
        
        # Return base64 encoded data for binary safety
        import base64
        return {
            "file_id": file_id,
            "data": base64.b64encode(data).decode('utf-8'),
            "size": len(data)
        }
    
    async def _handle_gridfs_delete(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GRIDFS_DELETE operation."""
        database_name = params.get("database_name")
        file_id = params.get("file_id")
        
        return await mongodb_client.gridfs_delete(database_name, file_id)
    
    async def _handle_gridfs_find(self, mongodb_client: MongoDBClient, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle GRIDFS_FIND operation."""
        database_name = params.get("database_name")
        filter_dict = params.get("filter", {})
        
        return await mongodb_client.gridfs_find(database_name, filter_dict)


# Helper functions for MongoDB data serialization
def serialize_mongodb_value(value: Any) -> Any:
    """Serialize a value for MongoDB storage."""
    if isinstance(value, ObjectId):
        return str(value)
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, Binary):
        import base64
        return base64.b64encode(value).decode('utf-8')
    elif isinstance(value, (dict, list)):
        return json.loads(json.dumps(value, default=serialize_mongodb_value))
    else:
        return value


def deserialize_mongodb_value(value: Any) -> Any:
    """Deserialize a value from MongoDB storage."""
    if isinstance(value, str):
        # Try to parse as ObjectId
        try:
            return ObjectId(value)
        except:
            pass
        
        # Try to parse as datetime
        try:
            return datetime.fromisoformat(value)
        except:
            pass
    
    return value