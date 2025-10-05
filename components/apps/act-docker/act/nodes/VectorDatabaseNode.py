"""
VectorDatabaseNode - Vector database operations for LLM workflows.
Handles vector storage, indexing, similarity search, and database management with support for
multiple vector database backends including Pinecone, Weaviate, Qdrant, Chroma, and FAISS.
"""

import json
import numpy as np
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import asyncio
import hashlib
from collections import defaultdict
import pickle
import base64

from .base_node import BaseNode, NodeResult, NodeSchema, NodeParameter, NodeParameterType
from ..utils.validation import NodeValidationError

class VectorDatabaseOperation:
    CREATE_INDEX = "create_index"
    DELETE_INDEX = "delete_index"
    LIST_INDEXES = "list_indexes"
    INSERT_VECTORS = "insert_vectors"
    UPDATE_VECTORS = "update_vectors"
    DELETE_VECTORS = "delete_vectors"
    SEARCH_VECTORS = "search_vectors"
    HYBRID_SEARCH = "hybrid_search"
    BATCH_OPERATIONS = "batch_operations"
    GET_VECTOR = "get_vector"
    LIST_VECTORS = "list_vectors"
    COUNT_VECTORS = "count_vectors"
    CREATE_COLLECTION = "create_collection"
    DELETE_COLLECTION = "delete_collection"
    LIST_COLLECTIONS = "list_collections"
    BACKUP_INDEX = "backup_index"
    RESTORE_INDEX = "restore_index"
    OPTIMIZE_INDEX = "optimize_index"
    GET_STATISTICS = "get_statistics"
    FILTER_VECTORS = "filter_vectors"
    AGGREGATE_VECTORS = "aggregate_vectors"
    BULK_IMPORT = "bulk_import"
    BULK_EXPORT = "bulk_export"
    REINDEX_VECTORS = "reindex_vectors"
    CONFIGURE_INDEX = "configure_index"
    MONITOR_PERFORMANCE = "monitor_performance"
    MANAGE_SHARDS = "manage_shards"
    SETUP_REPLICATION = "setup_replication"
    VECTOR_ANALYTICS = "vector_analytics"

class VectorDatabaseNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.name = "VectorDatabaseNode"
        self.description = "Vector database operations for LLM workflows"
        self.version = "1.0.0"
        self.icon_path = "🗃️"
        
        # Database configurations and connections
        self.database_configs = {}
        self.active_connections = {}
        self.indexes = {}
        self.collections = {}
        
        # In-memory storage for demonstration (FAISS-like)
        self.vector_store = {}
        self.metadata_store = {}
        self.index_configs = {}
        
        # Performance monitoring
        self.operation_stats = defaultdict(list)
        self.performance_metrics = {}

    async def execute(self, operation: str, params: Dict[str, Any]) -> NodeResult:
        try:
            operation_map = {
                VectorDatabaseOperation.CREATE_INDEX: self._create_index,
                VectorDatabaseOperation.DELETE_INDEX: self._delete_index,
                VectorDatabaseOperation.LIST_INDEXES: self._list_indexes,
                VectorDatabaseOperation.INSERT_VECTORS: self._insert_vectors,
                VectorDatabaseOperation.UPDATE_VECTORS: self._update_vectors,
                VectorDatabaseOperation.DELETE_VECTORS: self._delete_vectors,
                VectorDatabaseOperation.SEARCH_VECTORS: self._search_vectors,
                VectorDatabaseOperation.HYBRID_SEARCH: self._hybrid_search,
                VectorDatabaseOperation.BATCH_OPERATIONS: self._batch_operations,
                VectorDatabaseOperation.GET_VECTOR: self._get_vector,
                VectorDatabaseOperation.LIST_VECTORS: self._list_vectors,
                VectorDatabaseOperation.COUNT_VECTORS: self._count_vectors,
                VectorDatabaseOperation.CREATE_COLLECTION: self._create_collection,
                VectorDatabaseOperation.DELETE_COLLECTION: self._delete_collection,
                VectorDatabaseOperation.LIST_COLLECTIONS: self._list_collections,
                VectorDatabaseOperation.BACKUP_INDEX: self._backup_index,
                VectorDatabaseOperation.RESTORE_INDEX: self._restore_index,
                VectorDatabaseOperation.OPTIMIZE_INDEX: self._optimize_index,
                VectorDatabaseOperation.GET_STATISTICS: self._get_statistics,
                VectorDatabaseOperation.FILTER_VECTORS: self._filter_vectors,
                VectorDatabaseOperation.AGGREGATE_VECTORS: self._aggregate_vectors,
                VectorDatabaseOperation.BULK_IMPORT: self._bulk_import,
                VectorDatabaseOperation.BULK_EXPORT: self._bulk_export,
                VectorDatabaseOperation.REINDEX_VECTORS: self._reindex_vectors,
                VectorDatabaseOperation.CONFIGURE_INDEX: self._configure_index,
                VectorDatabaseOperation.MONITOR_PERFORMANCE: self._monitor_performance,
                VectorDatabaseOperation.MANAGE_SHARDS: self._manage_shards,
                VectorDatabaseOperation.SETUP_REPLICATION: self._setup_replication,
                VectorDatabaseOperation.VECTOR_ANALYTICS: self._vector_analytics,
            }

            if operation not in operation_map:
                return self._create_error_result(f"Unknown operation: {operation}")

            self._validate_params(operation, params)
            
            # Record operation start time for performance monitoring
            start_time = datetime.now()
            
            result = await operation_map[operation](params)
            
            # Record operation performance
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            self.operation_stats[operation].append({
                "timestamp": start_time.isoformat(),
                "execution_time": execution_time,
                "success": True
            })
            
            return self._create_success_result(result, f"Vector database operation '{operation}' completed")
            
        except Exception as e:
            # Record failed operation
            if operation in self.operation_stats:
                self.operation_stats[operation].append({
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": 0,
                    "success": False,
                    "error": str(e)
                })
            
            return self._create_error_result(f"Vector database error: {str(e)}")

    async def _create_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new vector index."""
        index_name = params["index_name"]
        dimension = params["dimension"]
        metric = params.get("metric", "cosine")  # cosine, euclidean, dot_product
        index_type = params.get("index_type", "hnsw")  # hnsw, ivf, flat
        database_type = params.get("database_type", "memory")  # memory, pinecone, weaviate, qdrant, chroma
        
        # Advanced configuration
        config = params.get("config", {})
        m = config.get("m", 16)  # HNSW parameter
        ef_construction = config.get("ef_construction", 200)  # HNSW parameter
        nlist = config.get("nlist", 100)  # IVF parameter
        
        if index_name in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' already exists")
        
        # Create index configuration
        index_config = {
            "name": index_name,
            "dimension": dimension,
            "metric": metric,
            "index_type": index_type,
            "database_type": database_type,
            "created_at": datetime.now().isoformat(),
            "config": {
                "m": m,
                "ef_construction": ef_construction,
                "nlist": nlist,
                **config
            },
            "vector_count": 0,
            "status": "active"
        }
        
        # Initialize storage based on database type
        if database_type == "memory":
            self.vector_store[index_name] = {}
            self.metadata_store[index_name] = {}
        elif database_type == "pinecone":
            await self._initialize_pinecone_index(index_name, index_config)
        elif database_type == "weaviate":
            await self._initialize_weaviate_index(index_name, index_config)
        elif database_type == "qdrant":
            await self._initialize_qdrant_index(index_name, index_config)
        elif database_type == "chroma":
            await self._initialize_chroma_index(index_name, index_config)
        
        self.indexes[index_name] = index_config
        self.index_configs[index_name] = index_config
        
        return {
            "index_name": index_name,
            "index_config": index_config,
            "database_type": database_type,
            "status": "created"
        }

    async def _delete_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a vector index."""
        index_name = params["index_name"]
        force = params.get("force", False)
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        index_config = self.indexes[index_name]
        vector_count = index_config.get("vector_count", 0)
        
        if vector_count > 0 and not force:
            raise NodeValidationError(f"Index '{index_name}' contains {vector_count} vectors. Use force=True to delete.")
        
        # Delete from appropriate backend
        database_type = index_config["database_type"]
        
        if database_type == "memory":
            if index_name in self.vector_store:
                del self.vector_store[index_name]
            if index_name in self.metadata_store:
                del self.metadata_store[index_name]
        elif database_type == "pinecone":
            await self._delete_pinecone_index(index_name)
        elif database_type == "weaviate":
            await self._delete_weaviate_index(index_name)
        elif database_type == "qdrant":
            await self._delete_qdrant_index(index_name)
        elif database_type == "chroma":
            await self._delete_chroma_index(index_name)
        
        # Remove from local tracking
        del self.indexes[index_name]
        if index_name in self.index_configs:
            del self.index_configs[index_name]
        
        return {
            "index_name": index_name,
            "deleted_vector_count": vector_count,
            "status": "deleted"
        }

    async def _list_indexes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all vector indexes."""
        database_type_filter = params.get("database_type")
        include_stats = params.get("include_stats", False)
        
        indexes_list = []
        
        for index_name, index_config in self.indexes.items():
            if database_type_filter and index_config["database_type"] != database_type_filter:
                continue
            
            index_info = {
                "name": index_name,
                "dimension": index_config["dimension"],
                "metric": index_config["metric"],
                "index_type": index_config["index_type"],
                "database_type": index_config["database_type"],
                "created_at": index_config["created_at"],
                "vector_count": index_config.get("vector_count", 0),
                "status": index_config.get("status", "unknown")
            }
            
            if include_stats:
                stats = await self._get_index_statistics(index_name)
                index_info["statistics"] = stats
            
            indexes_list.append(index_info)
        
        return {
            "indexes": indexes_list,
            "total_count": len(indexes_list),
            "database_types": list(set(idx["database_type"] for idx in indexes_list))
        }

    async def _insert_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Insert vectors into an index."""
        index_name = params["index_name"]
        vectors = params["vectors"]  # List of {"id": str, "vector": List[float], "metadata": dict}
        batch_size = params.get("batch_size", 100)
        upsert = params.get("upsert", False)  # Update if exists
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        index_config = self.indexes[index_name]
        expected_dimension = index_config["dimension"]
        
        # Validate vectors
        for vector_data in vectors:
            if "id" not in vector_data or "vector" not in vector_data:
                raise NodeValidationError("Each vector must have 'id' and 'vector' fields")
            
            if len(vector_data["vector"]) != expected_dimension:
                raise NodeValidationError(f"Vector dimension {len(vector_data['vector'])} doesn't match index dimension {expected_dimension}")
        
        # Insert in batches
        inserted_count = 0
        updated_count = 0
        failed_count = 0
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            
            try:
                batch_result = await self._insert_vector_batch(index_name, batch, upsert)
                inserted_count += batch_result["inserted"]
                updated_count += batch_result["updated"]
                failed_count += batch_result["failed"]
            except Exception as e:
                failed_count += len(batch)
                continue
        
        # Update index statistics
        self.indexes[index_name]["vector_count"] = await self._get_vector_count(index_name)
        
        return {
            "index_name": index_name,
            "total_vectors": len(vectors),
            "inserted_count": inserted_count,
            "updated_count": updated_count,
            "failed_count": failed_count,
            "final_vector_count": self.indexes[index_name]["vector_count"]
        }

    async def _update_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing vectors in an index."""
        index_name = params["index_name"]
        updates = params["updates"]  # List of {"id": str, "vector": List[float], "metadata": dict}
        partial_update = params.get("partial_update", False)  # Update only provided fields
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        updated_count = 0
        not_found_count = 0
        failed_count = 0
        
        for update_data in updates:
            vector_id = update_data["id"]
            
            try:
                exists = await self._vector_exists(index_name, vector_id)
                
                if exists:
                    await self._update_single_vector(index_name, update_data, partial_update)
                    updated_count += 1
                else:
                    not_found_count += 1
            except Exception as e:
                failed_count += 1
                continue
        
        return {
            "index_name": index_name,
            "total_updates": len(updates),
            "updated_count": updated_count,
            "not_found_count": not_found_count,
            "failed_count": failed_count
        }

    async def _delete_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete vectors from an index."""
        index_name = params["index_name"]
        vector_ids = params.get("vector_ids", [])
        filter_criteria = params.get("filter_criteria")  # Alternative: delete by filter
        confirm_delete_all = params.get("confirm_delete_all", False)
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        deleted_count = 0
        not_found_count = 0
        
        if vector_ids:
            # Delete specific vectors
            for vector_id in vector_ids:
                try:
                    exists = await self._vector_exists(index_name, vector_id)
                    
                    if exists:
                        await self._delete_single_vector(index_name, vector_id)
                        deleted_count += 1
                    else:
                        not_found_count += 1
                except Exception:
                    not_found_count += 1
        
        elif filter_criteria:
            # Delete by filter
            deleted_count = await self._delete_vectors_by_filter(index_name, filter_criteria)
        
        elif confirm_delete_all:
            # Delete all vectors
            deleted_count = await self._delete_all_vectors(index_name)
        
        else:
            raise NodeValidationError("Must provide vector_ids, filter_criteria, or confirm_delete_all=True")
        
        # Update index statistics
        self.indexes[index_name]["vector_count"] = await self._get_vector_count(index_name)
        
        return {
            "index_name": index_name,
            "deleted_count": deleted_count,
            "not_found_count": not_found_count,
            "remaining_vectors": self.indexes[index_name]["vector_count"]
        }

    async def _search_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for similar vectors in an index."""
        index_name = params["index_name"]
        query_vector = params["query_vector"]
        top_k = params.get("top_k", 10)
        include_metadata = params.get("include_metadata", True)
        include_vectors = params.get("include_vectors", False)
        filter_criteria = params.get("filter_criteria")
        score_threshold = params.get("score_threshold", 0.0)
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        index_config = self.indexes[index_name]
        
        if len(query_vector) != index_config["dimension"]:
            raise NodeValidationError(f"Query vector dimension {len(query_vector)} doesn't match index dimension {index_config['dimension']}")
        
        # Perform search based on database type
        database_type = index_config["database_type"]
        
        if database_type == "memory":
            search_results = await self._search_memory_index(index_name, query_vector, top_k, filter_criteria, score_threshold)
        elif database_type == "pinecone":
            search_results = await self._search_pinecone_index(index_name, query_vector, top_k, filter_criteria, score_threshold)
        elif database_type == "weaviate":
            search_results = await self._search_weaviate_index(index_name, query_vector, top_k, filter_criteria, score_threshold)
        elif database_type == "qdrant":
            search_results = await self._search_qdrant_index(index_name, query_vector, top_k, filter_criteria, score_threshold)
        elif database_type == "chroma":
            search_results = await self._search_chroma_index(index_name, query_vector, top_k, filter_criteria, score_threshold)
        else:
            raise NodeValidationError(f"Unsupported database type: {database_type}")
        
        # Format results
        formatted_results = []
        for result in search_results:
            formatted_result = {
                "id": result["id"],
                "score": result["score"],
                "metadata": result.get("metadata", {}) if include_metadata else None
            }
            
            if include_vectors:
                formatted_result["vector"] = result.get("vector", [])
            
            formatted_results.append(formatted_result)
        
        return {
            "index_name": index_name,
            "query_dimension": len(query_vector),
            "results": formatted_results,
            "total_results": len(formatted_results),
            "top_k": top_k,
            "score_threshold": score_threshold,
            "search_time_ms": 0  # Would track actual search time
        }

    async def _hybrid_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform hybrid search combining vector and keyword search."""
        index_name = params["index_name"]
        query_vector = params.get("query_vector")
        query_text = params.get("query_text")
        top_k = params.get("top_k", 10)
        vector_weight = params.get("vector_weight", 0.7)
        text_weight = params.get("text_weight", 0.3)
        include_metadata = params.get("include_metadata", True)
        
        if not query_vector and not query_text:
            raise NodeValidationError("Must provide either query_vector or query_text")
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        hybrid_results = []
        
        # Vector search results
        vector_results = []
        if query_vector:
            vector_search = await self._search_vectors({
                "index_name": index_name,
                "query_vector": query_vector,
                "top_k": top_k * 2,  # Get more candidates for reranking
                "include_metadata": include_metadata
            })
            vector_results = vector_search["results"]
        
        # Text search results
        text_results = []
        if query_text:
            text_results = await self._keyword_search(index_name, query_text, top_k * 2)
        
        # Combine and rerank results
        if vector_results and text_results:
            # Hybrid scoring
            combined_scores = {}
            
            # Add vector scores
            for result in vector_results:
                vector_id = result["id"]
                combined_scores[vector_id] = {
                    "vector_score": result["score"] * vector_weight,
                    "text_score": 0,
                    "metadata": result.get("metadata", {}),
                    "id": vector_id
                }
            
            # Add text scores
            for result in text_results:
                vector_id = result["id"]
                if vector_id in combined_scores:
                    combined_scores[vector_id]["text_score"] = result["score"] * text_weight
                else:
                    combined_scores[vector_id] = {
                        "vector_score": 0,
                        "text_score": result["score"] * text_weight,
                        "metadata": result.get("metadata", {}),
                        "id": vector_id
                    }
            
            # Calculate final scores and sort
            for vector_id, scores in combined_scores.items():
                final_score = scores["vector_score"] + scores["text_score"]
                hybrid_results.append({
                    "id": vector_id,
                    "score": final_score,
                    "vector_score": scores["vector_score"],
                    "text_score": scores["text_score"],
                    "metadata": scores["metadata"] if include_metadata else None
                })
            
            hybrid_results.sort(key=lambda x: x["score"], reverse=True)
            hybrid_results = hybrid_results[:top_k]
        
        elif vector_results:
            hybrid_results = vector_results[:top_k]
        elif text_results:
            hybrid_results = text_results[:top_k]
        
        return {
            "index_name": index_name,
            "hybrid_results": hybrid_results,
            "total_results": len(hybrid_results),
            "vector_weight": vector_weight,
            "text_weight": text_weight,
            "search_type": "hybrid"
        }

    async def _batch_operations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple operations in a batch."""
        operations = params["operations"]  # List of operation definitions
        parallel_execution = params.get("parallel_execution", False)
        fail_fast = params.get("fail_fast", False)
        
        batch_results = []
        
        if parallel_execution:
            # Execute operations in parallel
            tasks = []
            for operation in operations:
                task = self._execute_single_operation(operation)
                tasks.append(task)
            
            if fail_fast:
                batch_results = await asyncio.gather(*tasks)
            else:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        else:
            # Sequential execution
            for operation in operations:
                try:
                    result = await self._execute_single_operation(operation)
                    batch_results.append(result)
                except Exception as e:
                    error_result = {"error": str(e), "operation": operation}
                    batch_results.append(error_result)
                    
                    if fail_fast:
                        break
        
        # Calculate batch statistics
        successful_operations = sum(1 for r in batch_results if "error" not in r)
        failed_operations = len(batch_results) - successful_operations
        
        return {
            "batch_results": batch_results,
            "total_operations": len(operations),
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "execution_mode": "parallel" if parallel_execution else "sequential"
        }

    async def _get_vector(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific vector by ID."""
        index_name = params["index_name"]
        vector_id = params["vector_id"]
        include_vector = params.get("include_vector", True)
        include_metadata = params.get("include_metadata", True)
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        vector_data = await self._get_vector_by_id(index_name, vector_id)
        
        if not vector_data:
            raise NodeValidationError(f"Vector '{vector_id}' not found in index '{index_name}'")
        
        result = {"id": vector_id}
        
        if include_vector:
            result["vector"] = vector_data.get("vector", [])
        
        if include_metadata:
            result["metadata"] = vector_data.get("metadata", {})
        
        # Add additional information
        result["dimension"] = len(vector_data.get("vector", []))
        result["created_at"] = vector_data.get("created_at")
        result["updated_at"] = vector_data.get("updated_at")
        
        return {
            "vector_data": result,
            "index_name": index_name
        }

    async def _list_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List vectors in an index with pagination."""
        index_name = params["index_name"]
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        include_vectors = params.get("include_vectors", False)
        include_metadata = params.get("include_metadata", True)
        filter_criteria = params.get("filter_criteria")
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        vectors = await self._list_vectors_from_index(index_name, limit, offset, filter_criteria)
        
        # Format results
        formatted_vectors = []
        for vector_data in vectors:
            formatted_vector = {
                "id": vector_data["id"],
                "created_at": vector_data.get("created_at"),
                "updated_at": vector_data.get("updated_at")
            }
            
            if include_vectors:
                formatted_vector["vector"] = vector_data.get("vector", [])
                formatted_vector["dimension"] = len(vector_data.get("vector", []))
            
            if include_metadata:
                formatted_vector["metadata"] = vector_data.get("metadata", {})
            
            formatted_vectors.append(formatted_vector)
        
        total_count = await self._get_vector_count(index_name)
        
        return {
            "vectors": formatted_vectors,
            "total_count": total_count,
            "returned_count": len(formatted_vectors),
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(formatted_vectors) < total_count
        }

    async def _count_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Count vectors in an index."""
        index_name = params["index_name"]
        filter_criteria = params.get("filter_criteria")
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        if filter_criteria:
            count = await self._count_vectors_with_filter(index_name, filter_criteria)
        else:
            count = await self._get_vector_count(index_name)
        
        return {
            "index_name": index_name,
            "vector_count": count,
            "filter_applied": filter_criteria is not None
        }

    async def _create_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a collection (namespace) for organizing indexes."""
        collection_name = params["collection_name"]
        description = params.get("description", "")
        config = params.get("config", {})
        
        if collection_name in self.collections:
            raise NodeValidationError(f"Collection '{collection_name}' already exists")
        
        collection_config = {
            "name": collection_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "config": config,
            "indexes": [],
            "status": "active"
        }
        
        self.collections[collection_name] = collection_config
        
        return {
            "collection_name": collection_name,
            "collection_config": collection_config,
            "status": "created"
        }

    async def _delete_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a collection and optionally its indexes."""
        collection_name = params["collection_name"]
        delete_indexes = params.get("delete_indexes", False)
        force = params.get("force", False)
        
        if collection_name not in self.collections:
            raise NodeValidationError(f"Collection '{collection_name}' not found")
        
        collection = self.collections[collection_name]
        indexes_in_collection = collection.get("indexes", [])
        
        if indexes_in_collection and not force and not delete_indexes:
            raise NodeValidationError(f"Collection contains {len(indexes_in_collection)} indexes. Use delete_indexes=True or force=True")
        
        deleted_indexes = []
        
        if delete_indexes:
            for index_name in indexes_in_collection:
                try:
                    await self._delete_index({"index_name": index_name, "force": True})
                    deleted_indexes.append(index_name)
                except Exception:
                    continue
        
        del self.collections[collection_name]
        
        return {
            "collection_name": collection_name,
            "deleted_indexes": deleted_indexes,
            "status": "deleted"
        }

    async def _list_collections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all collections."""
        include_indexes = params.get("include_indexes", False)
        
        collections_list = []
        
        for collection_name, collection_config in self.collections.items():
            collection_info = {
                "name": collection_name,
                "description": collection_config.get("description", ""),
                "created_at": collection_config["created_at"],
                "status": collection_config.get("status", "active"),
                "index_count": len(collection_config.get("indexes", []))
            }
            
            if include_indexes:
                collection_info["indexes"] = collection_config.get("indexes", [])
            
            collections_list.append(collection_info)
        
        return {
            "collections": collections_list,
            "total_count": len(collections_list)
        }

    async def _backup_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a backup of an index."""
        index_name = params["index_name"]
        backup_name = params.get("backup_name") or f"{index_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        include_vectors = params.get("include_vectors", True)
        compression = params.get("compression", True)
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        # Create backup data
        backup_data = {
            "index_config": self.indexes[index_name].copy(),
            "backup_name": backup_name,
            "created_at": datetime.now().isoformat(),
            "vector_count": 0,
            "vectors": []
        }
        
        if include_vectors:
            vectors = await self._export_all_vectors(index_name)
            backup_data["vectors"] = vectors
            backup_data["vector_count"] = len(vectors)
        
        # Compress if requested
        if compression:
            backup_data = self._compress_backup_data(backup_data)
        
        # Store backup (in practice, this would go to external storage)
        backup_path = f"backups/{backup_name}.pkl"
        
        return {
            "backup_name": backup_name,
            "backup_path": backup_path,
            "index_name": index_name,
            "vector_count": backup_data["vector_count"],
            "backup_size_mb": self._estimate_backup_size(backup_data),
            "compressed": compression
        }

    async def _restore_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Restore an index from backup."""
        backup_name = params["backup_name"]
        target_index_name = params.get("target_index_name")
        overwrite_existing = params.get("overwrite_existing", False)
        
        # Load backup data (in practice, from external storage)
        backup_data = await self._load_backup_data(backup_name)
        
        if not backup_data:
            raise NodeValidationError(f"Backup '{backup_name}' not found")
        
        # Determine target index name
        if not target_index_name:
            target_index_name = backup_data["index_config"]["name"]
        
        # Check if target index exists
        if target_index_name in self.indexes and not overwrite_existing:
            raise NodeValidationError(f"Index '{target_index_name}' already exists. Use overwrite_existing=True")
        
        # Restore index configuration
        index_config = backup_data["index_config"].copy()
        index_config["name"] = target_index_name
        index_config["restored_at"] = datetime.now().isoformat()
        index_config["restored_from"] = backup_name
        
        # Create index
        await self._create_index({
            "index_name": target_index_name,
            "dimension": index_config["dimension"],
            "metric": index_config["metric"],
            "index_type": index_config["index_type"],
            "database_type": index_config["database_type"],
            "config": index_config["config"]
        })
        
        # Restore vectors
        restored_count = 0
        if backup_data.get("vectors"):
            insert_result = await self._insert_vectors({
                "index_name": target_index_name,
                "vectors": backup_data["vectors"],
                "upsert": True
            })
            restored_count = insert_result["inserted_count"] + insert_result["updated_count"]
        
        return {
            "backup_name": backup_name,
            "target_index_name": target_index_name,
            "restored_vector_count": restored_count,
            "index_config": index_config,
            "status": "restored"
        }

    async def _optimize_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize index performance."""
        index_name = params["index_name"]
        optimization_type = params.get("optimization_type", "full")  # full, compact, rebalance
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        index_config = self.indexes[index_name]
        optimization_start = datetime.now()
        
        optimization_results = {
            "index_name": index_name,
            "optimization_type": optimization_type,
            "started_at": optimization_start.isoformat()
        }
        
        if optimization_type in ["full", "compact"]:
            # Compact index (remove deleted vectors, optimize storage)
            compact_result = await self._compact_index(index_name)
            optimization_results["compact_result"] = compact_result
        
        if optimization_type in ["full", "rebalance"]:
            # Rebalance index (redistribute data for optimal search performance)
            rebalance_result = await self._rebalance_index(index_name)
            optimization_results["rebalance_result"] = rebalance_result
        
        if optimization_type == "full":
            # Full optimization includes index rebuilding for maximum performance
            rebuild_result = await self._rebuild_index(index_name)
            optimization_results["rebuild_result"] = rebuild_result
        
        optimization_end = datetime.now()
        optimization_time = (optimization_end - optimization_start).total_seconds()
        
        optimization_results.update({
            "completed_at": optimization_end.isoformat(),
            "optimization_time_seconds": optimization_time,
            "status": "completed"
        })
        
        return optimization_results

    async def _get_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive statistics for indexes and operations."""
        index_name = params.get("index_name")
        include_performance = params.get("include_performance", True)
        include_storage = params.get("include_storage", True)
        
        if index_name:
            # Statistics for specific index
            if index_name not in self.indexes:
                raise NodeValidationError(f"Index '{index_name}' not found")
            
            stats = await self._get_index_statistics(index_name)
            
            if include_performance:
                stats["performance"] = await self._get_index_performance_stats(index_name)
            
            if include_storage:
                stats["storage"] = await self._get_index_storage_stats(index_name)
            
            return {
                "index_name": index_name,
                "statistics": stats
            }
        
        else:
            # Global statistics
            global_stats = {
                "total_indexes": len(self.indexes),
                "total_collections": len(self.collections),
                "indexes_by_type": {},
                "indexes_by_database": {},
                "total_vectors": 0
            }
            
            # Aggregate statistics
            for index_name, index_config in self.indexes.items():
                index_type = index_config["index_type"]
                database_type = index_config["database_type"]
                vector_count = index_config.get("vector_count", 0)
                
                global_stats["indexes_by_type"][index_type] = global_stats["indexes_by_type"].get(index_type, 0) + 1
                global_stats["indexes_by_database"][database_type] = global_stats["indexes_by_database"].get(database_type, 0) + 1
                global_stats["total_vectors"] += vector_count
            
            if include_performance:
                global_stats["performance"] = await self._get_global_performance_stats()
            
            return {
                "global_statistics": global_stats
            }

    async def _filter_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter vectors based on metadata criteria."""
        index_name = params["index_name"]
        filter_criteria = params["filter_criteria"]
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        include_vectors = params.get("include_vectors", False)
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        filtered_vectors = await self._apply_metadata_filter(index_name, filter_criteria, limit, offset)
        
        # Format results
        results = []
        for vector_data in filtered_vectors:
            result = {
                "id": vector_data["id"],
                "metadata": vector_data.get("metadata", {})
            }
            
            if include_vectors:
                result["vector"] = vector_data.get("vector", [])
                result["dimension"] = len(vector_data.get("vector", []))
            
            results.append(result)
        
        total_matches = await self._count_vectors_with_filter(index_name, filter_criteria)
        
        return {
            "index_name": index_name,
            "filter_criteria": filter_criteria,
            "results": results,
            "total_matches": total_matches,
            "returned_count": len(results),
            "limit": limit,
            "offset": offset
        }

    async def _aggregate_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform aggregation operations on vectors."""
        index_name = params["index_name"]
        aggregation_type = params["aggregation_type"]  # centroid, stats, clustering
        filter_criteria = params.get("filter_criteria")
        group_by = params.get("group_by")  # Metadata field to group by
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        vectors = await self._get_vectors_for_aggregation(index_name, filter_criteria)
        
        if aggregation_type == "centroid":
            result = await self._calculate_vector_centroid(vectors)
        elif aggregation_type == "stats":
            result = await self._calculate_vector_statistics(vectors)
        elif aggregation_type == "clustering":
            result = await self._perform_vector_clustering(vectors, params.get("num_clusters", 5))
        else:
            raise NodeValidationError(f"Unknown aggregation type: {aggregation_type}")
        
        if group_by:
            result = await self._group_aggregation_by_metadata(vectors, group_by, aggregation_type)
        
        return {
            "index_name": index_name,
            "aggregation_type": aggregation_type,
            "filter_criteria": filter_criteria,
            "group_by": group_by,
            "vector_count": len(vectors),
            "result": result
        }

    async def _bulk_import(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Import vectors from external source in bulk."""
        index_name = params["index_name"]
        source_type = params["source_type"]  # file, url, database
        source_path = params["source_path"]
        batch_size = params.get("batch_size", 1000)
        format_type = params.get("format_type", "json")  # json, csv, parquet
        mapping_config = params.get("mapping_config", {})
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        import_stats = {
            "source_type": source_type,
            "source_path": source_path,
            "format_type": format_type,
            "started_at": datetime.now().isoformat(),
            "processed_count": 0,
            "inserted_count": 0,
            "failed_count": 0,
            "batches_processed": 0
        }
        
        # Load data based on source type
        if source_type == "file":
            data_stream = await self._load_from_file(source_path, format_type)
        elif source_type == "url":
            data_stream = await self._load_from_url(source_path, format_type)
        elif source_type == "database":
            data_stream = await self._load_from_database(source_path, mapping_config)
        else:
            raise NodeValidationError(f"Unknown source type: {source_type}")
        
        # Process in batches
        batch = []
        for data_item in data_stream:
            # Map data to vector format
            vector_data = self._map_data_to_vector(data_item, mapping_config)
            batch.append(vector_data)
            
            if len(batch) >= batch_size:
                # Process batch
                batch_result = await self._process_import_batch(index_name, batch)
                import_stats["processed_count"] += len(batch)
                import_stats["inserted_count"] += batch_result["inserted"]
                import_stats["failed_count"] += batch_result["failed"]
                import_stats["batches_processed"] += 1
                
                batch = []
        
        # Process remaining batch
        if batch:
            batch_result = await self._process_import_batch(index_name, batch)
            import_stats["processed_count"] += len(batch)
            import_stats["inserted_count"] += batch_result["inserted"]
            import_stats["failed_count"] += batch_result["failed"]
            import_stats["batches_processed"] += 1
        
        import_stats["completed_at"] = datetime.now().isoformat()
        
        return {
            "index_name": index_name,
            "import_statistics": import_stats
        }

    async def _bulk_export(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export vectors to external destination in bulk."""
        index_name = params["index_name"]
        destination_type = params["destination_type"]  # file, url, database
        destination_path = params["destination_path"]
        format_type = params.get("format_type", "json")
        include_vectors = params.get("include_vectors", True)
        include_metadata = params.get("include_metadata", True)
        filter_criteria = params.get("filter_criteria")
        batch_size = params.get("batch_size", 1000)
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        export_stats = {
            "destination_type": destination_type,
            "destination_path": destination_path,
            "format_type": format_type,
            "started_at": datetime.now().isoformat(),
            "exported_count": 0,
            "batches_processed": 0
        }
        
        # Get vectors to export
        vectors = await self._get_vectors_for_export(index_name, filter_criteria, include_vectors, include_metadata)
        
        # Export in batches
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            
            if destination_type == "file":
                await self._export_to_file(batch, destination_path, format_type, i == 0)
            elif destination_type == "url":
                await self._export_to_url(batch, destination_path, format_type)
            elif destination_type == "database":
                await self._export_to_database(batch, destination_path)
            
            export_stats["exported_count"] += len(batch)
            export_stats["batches_processed"] += 1
        
        export_stats["completed_at"] = datetime.now().isoformat()
        
        return {
            "index_name": index_name,
            "export_statistics": export_stats
        }

    async def _reindex_vectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reindex vectors with new configuration."""
        index_name = params["index_name"]
        new_config = params["new_config"]
        preserve_data = params.get("preserve_data", True)
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        old_config = self.indexes[index_name].copy()
        
        # Backup vectors if preserving data
        vectors_backup = []
        if preserve_data:
            vectors_backup = await self._export_all_vectors(index_name)
        
        # Update index configuration
        self.indexes[index_name].update(new_config)
        self.indexes[index_name]["reindexed_at"] = datetime.now().isoformat()
        
        # Rebuild index with new configuration
        await self._rebuild_index_with_config(index_name, new_config)
        
        # Restore vectors if preserved
        restored_count = 0
        if preserve_data and vectors_backup:
            insert_result = await self._insert_vectors({
                "index_name": index_name,
                "vectors": vectors_backup,
                "upsert": True
            })
            restored_count = insert_result["inserted_count"] + insert_result["updated_count"]
        
        return {
            "index_name": index_name,
            "old_config": old_config,
            "new_config": new_config,
            "vectors_preserved": preserve_data,
            "restored_vector_count": restored_count,
            "status": "reindexed"
        }

    async def _configure_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configure index settings and parameters."""
        index_name = params["index_name"]
        configuration = params["configuration"]
        apply_immediately = params.get("apply_immediately", True)
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        old_config = self.indexes[index_name]["config"].copy()
        
        # Update configuration
        self.indexes[index_name]["config"].update(configuration)
        self.indexes[index_name]["configured_at"] = datetime.now().isoformat()
        
        # Apply configuration changes
        applied_changes = []
        if apply_immediately:
            for key, value in configuration.items():
                try:
                    await self._apply_config_change(index_name, key, value)
                    applied_changes.append(key)
                except Exception as e:
                    # Revert change if application failed
                    if key in old_config:
                        self.indexes[index_name]["config"][key] = old_config[key]
                    continue
        
        return {
            "index_name": index_name,
            "old_config": old_config,
            "new_config": self.indexes[index_name]["config"],
            "applied_changes": applied_changes,
            "status": "configured"
        }

    async def _monitor_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and analyze index performance."""
        index_name = params.get("index_name")
        time_range = params.get("time_range", "1h")  # 1h, 24h, 7d, 30d
        metrics = params.get("metrics", ["latency", "throughput", "errors"])
        
        performance_data = {}
        
        if index_name:
            # Performance for specific index
            if index_name not in self.indexes:
                raise NodeValidationError(f"Index '{index_name}' not found")
            
            performance_data[index_name] = await self._get_index_performance_metrics(index_name, time_range, metrics)
        else:
            # Performance for all indexes
            for idx_name in self.indexes.keys():
                performance_data[idx_name] = await self._get_index_performance_metrics(idx_name, time_range, metrics)
        
        # Calculate aggregated metrics
        aggregated_metrics = self._calculate_aggregated_performance(performance_data, metrics)
        
        return {
            "time_range": time_range,
            "metrics": metrics,
            "performance_data": performance_data,
            "aggregated_metrics": aggregated_metrics,
            "monitored_at": datetime.now().isoformat()
        }

    async def _manage_shards(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Manage index sharding configuration."""
        index_name = params["index_name"]
        operation = params["operation"]  # create, delete, rebalance, list
        shard_config = params.get("shard_config", {})
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        if operation == "create":
            result = await self._create_shard(index_name, shard_config)
        elif operation == "delete":
            shard_id = params["shard_id"]
            result = await self._delete_shard(index_name, shard_id)
        elif operation == "rebalance":
            result = await self._rebalance_shards(index_name)
        elif operation == "list":
            result = await self._list_shards(index_name)
        else:
            raise NodeValidationError(f"Unknown shard operation: {operation}")
        
        return {
            "index_name": index_name,
            "operation": operation,
            "result": result
        }

    async def _setup_replication(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Setup replication for high availability."""
        index_name = params["index_name"]
        replication_config = params["replication_config"]
        replica_count = replication_config.get("replica_count", 1)
        consistency_level = replication_config.get("consistency_level", "eventual")
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        # Setup replication (simplified implementation)
        replication_info = {
            "index_name": index_name,
            "replica_count": replica_count,
            "consistency_level": consistency_level,
            "setup_at": datetime.now().isoformat(),
            "replicas": []
        }
        
        for i in range(replica_count):
            replica_id = f"{index_name}_replica_{i+1}"
            replica_info = await self._create_replica(index_name, replica_id, replication_config)
            replication_info["replicas"].append(replica_info)
        
        # Update index configuration
        self.indexes[index_name]["replication"] = replication_info
        
        return {
            "replication_setup": replication_info,
            "status": "configured"
        }

    async def _vector_analytics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform analytics on vector data."""
        index_name = params["index_name"]
        analysis_type = params["analysis_type"]  # distribution, clustering, outliers, similarity_graph
        sample_size = params.get("sample_size", 1000)
        
        if index_name not in self.indexes:
            raise NodeValidationError(f"Index '{index_name}' not found")
        
        # Get sample vectors for analysis
        vectors = await self._get_vector_sample(index_name, sample_size)
        
        analytics_result = {}
        
        if analysis_type in ["distribution", "all"]:
            analytics_result["distribution"] = await self._analyze_vector_distribution(vectors)
        
        if analysis_type in ["clustering", "all"]:
            analytics_result["clustering"] = await self._analyze_vector_clusters(vectors)
        
        if analysis_type in ["outliers", "all"]:
            analytics_result["outliers"] = await self._analyze_vector_outliers(vectors)
        
        if analysis_type in ["similarity_graph", "all"]:
            analytics_result["similarity_graph"] = await self._analyze_similarity_graph(vectors)
        
        return {
            "index_name": index_name,
            "analysis_type": analysis_type,
            "sample_size": len(vectors),
            "analytics": analytics_result,
            "analyzed_at": datetime.now().isoformat()
        }

    # Helper methods for database operations
    async def _initialize_pinecone_index(self, index_name: str, config: Dict[str, Any]):
        """Initialize Pinecone index (placeholder)."""
        # In practice, this would use the Pinecone API
        pass

    async def _initialize_weaviate_index(self, index_name: str, config: Dict[str, Any]):
        """Initialize Weaviate index (placeholder)."""
        # In practice, this would use the Weaviate API
        pass

    async def _initialize_qdrant_index(self, index_name: str, config: Dict[str, Any]):
        """Initialize Qdrant index (placeholder)."""
        # In practice, this would use the Qdrant API
        pass

    async def _initialize_chroma_index(self, index_name: str, config: Dict[str, Any]):
        """Initialize Chroma index (placeholder)."""
        # In practice, this would use the Chroma API
        pass

    async def _search_memory_index(self, index_name: str, query_vector: List[float], top_k: int, filter_criteria: Dict, score_threshold: float):
        """Search in-memory index."""
        if index_name not in self.vector_store:
            return []
        
        vectors = self.vector_store[index_name]
        results = []
        
        for vector_id, vector_data in vectors.items():
            # Apply filter if provided
            if filter_criteria and not self._matches_filter(vector_data.get("metadata", {}), filter_criteria):
                continue
            
            # Calculate similarity
            similarity = self._cosine_similarity(query_vector, vector_data["vector"])
            
            if similarity >= score_threshold:
                results.append({
                    "id": vector_id,
                    "score": similarity,
                    "vector": vector_data["vector"],
                    "metadata": vector_data.get("metadata", {})
                })
        
        # Sort by score and return top k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    async def _insert_vector_batch(self, index_name: str, batch: List[Dict], upsert: bool):
        """Insert a batch of vectors."""
        if index_name not in self.vector_store:
            self.vector_store[index_name] = {}
            self.metadata_store[index_name] = {}
        
        inserted = 0
        updated = 0
        failed = 0
        
        for vector_data in batch:
            try:
                vector_id = vector_data["id"]
                
                # Check if vector exists
                exists = vector_id in self.vector_store[index_name]
                
                if exists and not upsert:
                    failed += 1
                    continue
                
                # Store vector
                self.vector_store[index_name][vector_id] = {
                    "vector": vector_data["vector"],
                    "metadata": vector_data.get("metadata", {}),
                    "created_at": datetime.now().isoformat() if not exists else self.vector_store[index_name][vector_id].get("created_at"),
                    "updated_at": datetime.now().isoformat()
                }
                
                if exists:
                    updated += 1
                else:
                    inserted += 1
                    
            except Exception:
                failed += 1
        
        return {"inserted": inserted, "updated": updated, "failed": failed}

    async def _get_vector_count(self, index_name: str) -> int:
        """Get total vector count for index."""
        if index_name in self.vector_store:
            return len(self.vector_store[index_name])
        return 0

    async def _vector_exists(self, index_name: str, vector_id: str) -> bool:
        """Check if vector exists."""
        return (index_name in self.vector_store and 
                vector_id in self.vector_store[index_name])

    async def _get_vector_by_id(self, index_name: str, vector_id: str) -> Optional[Dict]:
        """Get vector by ID."""
        if (index_name in self.vector_store and 
            vector_id in self.vector_store[index_name]):
            return self.vector_store[index_name][vector_id]
        return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

    def _matches_filter(self, metadata: Dict, filter_criteria: Dict) -> bool:
        """Check if metadata matches filter criteria."""
        for key, value in filter_criteria.items():
            if key not in metadata:
                return False
            
            if isinstance(value, dict):
                # Support operators like {"$gte": 10}, {"$in": [1,2,3]}
                if "$gte" in value and metadata[key] < value["$gte"]:
                    return False
                if "$lte" in value and metadata[key] > value["$lte"]:
                    return False
                if "$in" in value and metadata[key] not in value["$in"]:
                    return False
                if "$eq" in value and metadata[key] != value["$eq"]:
                    return False
            else:
                # Direct equality check
                if metadata[key] != value:
                    return False
        
        return True

    async def _execute_single_operation(self, operation_def: Dict) -> Dict:
        """Execute a single operation definition."""
        operation_type = operation_def["operation"]
        params = operation_def.get("params", {})
        
        # This would recursively call the appropriate operation method
        # For simplicity, returning a placeholder
        return {"operation": operation_type, "status": "completed", "params": params}

    async def _keyword_search(self, index_name: str, query_text: str, top_k: int) -> List[Dict]:
        """Perform keyword search on metadata."""
        if index_name not in self.vector_store:
            return []
        
        query_words = set(query_text.lower().split())
        results = []
        
        for vector_id, vector_data in self.vector_store[index_name].items():
            metadata = vector_data.get("metadata", {})
            
            # Simple keyword matching on metadata text fields
            text_content = " ".join(str(v) for v in metadata.values() if isinstance(v, str))
            text_words = set(text_content.lower().split())
            
            # Calculate keyword overlap score
            overlap = len(query_words.intersection(text_words))
            if overlap > 0:
                score = overlap / len(query_words)
                results.append({
                    "id": vector_id,
                    "score": score,
                    "metadata": metadata
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    async def _get_index_statistics(self, index_name: str) -> Dict:
        """Get statistics for a specific index."""
        if index_name not in self.indexes:
            return {}
        
        index_config = self.indexes[index_name]
        vector_count = await self._get_vector_count(index_name)
        
        return {
            "vector_count": vector_count,
            "dimension": index_config["dimension"],
            "index_type": index_config["index_type"],
            "database_type": index_config["database_type"],
            "created_at": index_config["created_at"],
            "last_updated": index_config.get("updated_at"),
            "status": index_config.get("status", "active")
        }

    def _compress_backup_data(self, backup_data: Dict) -> Dict:
        """Compress backup data."""
        # In practice, would use compression algorithms
        return backup_data

    def _estimate_backup_size(self, backup_data: Dict) -> float:
        """Estimate backup size in MB."""
        # Rough estimation
        vector_count = backup_data.get("vector_count", 0)
        dimension = backup_data.get("index_config", {}).get("dimension", 0)
        
        # Estimate: vectors + metadata + overhead
        estimated_mb = (vector_count * dimension * 4) / (1024 * 1024)  # 4 bytes per float
        return round(estimated_mb, 2)

    async def _load_backup_data(self, backup_name: str) -> Optional[Dict]:
        """Load backup data (placeholder)."""
        # In practice, would load from external storage
        return None

    def _validate_params(self, operation: str, params: Dict[str, Any]) -> None:
        """Validate operation parameters."""
        required_params = {
            VectorDatabaseOperation.CREATE_INDEX: ["index_name", "dimension"],
            VectorDatabaseOperation.DELETE_INDEX: ["index_name"],
            VectorDatabaseOperation.LIST_INDEXES: [],
            VectorDatabaseOperation.INSERT_VECTORS: ["index_name", "vectors"],
            VectorDatabaseOperation.UPDATE_VECTORS: ["index_name", "updates"],
            VectorDatabaseOperation.DELETE_VECTORS: ["index_name"],
            VectorDatabaseOperation.SEARCH_VECTORS: ["index_name", "query_vector"],
            VectorDatabaseOperation.HYBRID_SEARCH: ["index_name"],
            VectorDatabaseOperation.BATCH_OPERATIONS: ["operations"],
            VectorDatabaseOperation.GET_VECTOR: ["index_name", "vector_id"],
            VectorDatabaseOperation.LIST_VECTORS: ["index_name"],
            VectorDatabaseOperation.COUNT_VECTORS: ["index_name"],
            VectorDatabaseOperation.CREATE_COLLECTION: ["collection_name"],
            VectorDatabaseOperation.DELETE_COLLECTION: ["collection_name"],
            VectorDatabaseOperation.LIST_COLLECTIONS: [],
            VectorDatabaseOperation.BACKUP_INDEX: ["index_name"],
            VectorDatabaseOperation.RESTORE_INDEX: ["backup_name"],
            VectorDatabaseOperation.OPTIMIZE_INDEX: ["index_name"],
            VectorDatabaseOperation.GET_STATISTICS: [],
            VectorDatabaseOperation.FILTER_VECTORS: ["index_name", "filter_criteria"],
            VectorDatabaseOperation.AGGREGATE_VECTORS: ["index_name", "aggregation_type"],
            VectorDatabaseOperation.BULK_IMPORT: ["index_name", "source_type", "source_path"],
            VectorDatabaseOperation.BULK_EXPORT: ["index_name", "destination_type", "destination_path"],
            VectorDatabaseOperation.REINDEX_VECTORS: ["index_name", "new_config"],
            VectorDatabaseOperation.CONFIGURE_INDEX: ["index_name", "configuration"],
            VectorDatabaseOperation.MONITOR_PERFORMANCE: [],
            VectorDatabaseOperation.MANAGE_SHARDS: ["index_name", "operation"],
            VectorDatabaseOperation.SETUP_REPLICATION: ["index_name", "replication_config"],
            VectorDatabaseOperation.VECTOR_ANALYTICS: ["index_name", "analysis_type"],
        }

        if operation in required_params:
            for param in required_params[operation]:
                if param not in params:
                    raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            name="VectorDatabaseNode",
            description="Vector database operations for LLM workflows",
            version="1.0.0",
            icon_path="🗃️",
            auth_params=[
                NodeParameter(
                    name="api_key",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="API key for vector database service"
                ),
                NodeParameter(
                    name="endpoint",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Database endpoint URL"
                )
            ],
            parameters=[
                NodeParameter(
                    name="index_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Name of the vector index"
                ),
                NodeParameter(
                    name="dimension",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Vector dimension for the index"
                ),
                NodeParameter(
                    name="metric",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Distance metric: cosine, euclidean, dot_product"
                ),
                NodeParameter(
                    name="index_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Index type: hnsw, ivf, flat"
                ),
                NodeParameter(
                    name="database_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Database backend: memory, pinecone, weaviate, qdrant, chroma"
                ),
                NodeParameter(
                    name="vectors",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Array of vector objects with id, vector, and metadata"
                ),
                NodeParameter(
                    name="query_vector",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Query vector for similarity search"
                ),
                NodeParameter(
                    name="top_k",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Number of top results to return"
                ),
                NodeParameter(
                    name="filter_criteria",
                    param_type=NodeParameterType.OBJECT,
                    required=False,
                    description="Metadata filter criteria"
                ),
                NodeParameter(
                    name="include_metadata",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Include metadata in results"
                ),
                NodeParameter(
                    name="include_vectors",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Include vector data in results"
                ),
                NodeParameter(
                    name="batch_size",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Batch size for bulk operations"
                ),
                NodeParameter(
                    name="upsert",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Update vectors if they already exist"
                ),
                NodeParameter(
                    name="collection_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Name of the collection (namespace)"
                ),
                NodeParameter(
                    name="backup_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Name for backup or restore operation"
                ),
                NodeParameter(
                    name="optimization_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Type of optimization: full, compact, rebalance"
                ),
                NodeParameter(
                    name="source_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Import source type: file, url, database"
                ),
                NodeParameter(
                    name="source_path",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Source path for import operations"
                ),
                NodeParameter(
                    name="destination_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Export destination type: file, url, database"
                ),
                NodeParameter(
                    name="destination_path",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Destination path for export operations"
                )
            ]
        )