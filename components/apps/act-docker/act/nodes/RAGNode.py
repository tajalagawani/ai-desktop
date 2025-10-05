"""
RAGNode - Retrieval Augmented Generation workflows for LLM applications.
Implements comprehensive RAG pipelines with document processing, vector retrieval,
context management, and response generation with state-of-the-art practices.
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import asyncio
import hashlib
from collections import defaultdict
import re

from .base_node import BaseNode, NodeResult, NodeSchema, NodeParameter, NodeParameterType
from ..utils.validation import NodeValidationError

class RAGOperation:
    INGEST_DOCUMENTS = "ingest_documents"
    PROCESS_DOCUMENTS = "process_documents"
    CREATE_CHUNKS = "create_chunks"
    GENERATE_EMBEDDINGS = "generate_embeddings"
    INDEX_DOCUMENTS = "index_documents"
    RETRIEVE_CONTEXT = "retrieve_context"
    RERANK_RESULTS = "rerank_results"
    GENERATE_RESPONSE = "generate_response"
    FULL_RAG_PIPELINE = "full_rag_pipeline"
    UPDATE_KNOWLEDGE_BASE = "update_knowledge_base"
    DELETE_DOCUMENTS = "delete_documents"
    SEARCH_DOCUMENTS = "search_documents"
    EXTRACT_ENTITIES = "extract_entities"
    SUMMARIZE_DOCUMENTS = "summarize_documents"
    FACT_CHECK = "fact_check"
    CITATION_TRACKING = "citation_tracking"
    CONTEXT_COMPRESSION = "context_compression"
    MULTI_HOP_REASONING = "multi_hop_reasoning"
    ADAPTIVE_RETRIEVAL = "adaptive_retrieval"
    QUERY_EXPANSION = "query_expansion"
    QUERY_DECOMPOSITION = "query_decomposition"
    ANSWER_VALIDATION = "answer_validation"
    KNOWLEDGE_GRAPH_RAG = "knowledge_graph_rag"
    CONVERSATIONAL_RAG = "conversational_rag"
    MULTI_MODAL_RAG = "multi_modal_rag"
    RAG_EVALUATION = "rag_evaluation"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"

class RAGNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.name = "RAGNode"
        self.description = "Retrieval Augmented Generation workflows for LLM applications"
        self.version = "1.0.0"
        self.icon_path = "🔍📚"
        
        # RAG components storage
        self.knowledge_bases = {}
        self.document_store = {}
        self.chunk_store = {}
        self.embedding_store = {}
        self.retrieval_cache = {}
        
        # Configuration
        self.default_chunk_size = 512
        self.default_chunk_overlap = 50
        self.default_retrieval_k = 5
        self.max_context_length = 4000

    async def execute(self, operation: str, params: Dict[str, Any]) -> NodeResult:
        try:
            operation_map = {
                RAGOperation.INGEST_DOCUMENTS: self._ingest_documents,
                RAGOperation.PROCESS_DOCUMENTS: self._process_documents,
                RAGOperation.CREATE_CHUNKS: self._create_chunks,
                RAGOperation.GENERATE_EMBEDDINGS: self._generate_embeddings,
                RAGOperation.INDEX_DOCUMENTS: self._index_documents,
                RAGOperation.RETRIEVE_CONTEXT: self._retrieve_context,
                RAGOperation.RERANK_RESULTS: self._rerank_results,
                RAGOperation.GENERATE_RESPONSE: self._generate_response,
                RAGOperation.FULL_RAG_PIPELINE: self._full_rag_pipeline,
                RAGOperation.UPDATE_KNOWLEDGE_BASE: self._update_knowledge_base,
                RAGOperation.DELETE_DOCUMENTS: self._delete_documents,
                RAGOperation.SEARCH_DOCUMENTS: self._search_documents,
                RAGOperation.EXTRACT_ENTITIES: self._extract_entities,
                RAGOperation.SUMMARIZE_DOCUMENTS: self._summarize_documents,
                RAGOperation.FACT_CHECK: self._fact_check,
                RAGOperation.CITATION_TRACKING: self._citation_tracking,
                RAGOperation.CONTEXT_COMPRESSION: self._context_compression,
                RAGOperation.MULTI_HOP_REASONING: self._multi_hop_reasoning,
                RAGOperation.ADAPTIVE_RETRIEVAL: self._adaptive_retrieval,
                RAGOperation.QUERY_EXPANSION: self._query_expansion,
                RAGOperation.QUERY_DECOMPOSITION: self._query_decomposition,
                RAGOperation.ANSWER_VALIDATION: self._answer_validation,
                RAGOperation.KNOWLEDGE_GRAPH_RAG: self._knowledge_graph_rag,
                RAGOperation.CONVERSATIONAL_RAG: self._conversational_rag,
                RAGOperation.MULTI_MODAL_RAG: self._multi_modal_rag,
                RAGOperation.RAG_EVALUATION: self._rag_evaluation,
                RAGOperation.PERFORMANCE_OPTIMIZATION: self._performance_optimization,
            }

            if operation not in operation_map:
                return self._create_error_result(f"Unknown operation: {operation}")

            self._validate_params(operation, params)
            result = await operation_map[operation](params)
            
            return self._create_success_result(result, f"RAG operation '{operation}' completed")
            
        except Exception as e:
            return self._create_error_result(f"RAG error: {str(e)}")

    async def _ingest_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest documents into the knowledge base."""
        kb_name = params["kb_name"]
        documents = params["documents"]
        document_type = params.get("document_type", "text")
        source_metadata = params.get("source_metadata", {})
        auto_process = params.get("auto_process", True)
        
        if kb_name not in self.knowledge_bases:
            self.knowledge_bases[kb_name] = {
                "name": kb_name,
                "created_at": datetime.now().isoformat(),
                "document_count": 0,
                "chunk_count": 0,
                "last_updated": datetime.now().isoformat()
            }
        
        if kb_name not in self.document_store:
            self.document_store[kb_name] = {}
        
        ingestion_results = []
        
        for doc in documents:
            doc_id = doc.get("id") or self._generate_document_id()
            
            document_record = {
                "id": doc_id,
                "content": doc["content"],
                "type": document_type,
                "metadata": {**source_metadata, **doc.get("metadata", {})},
                "ingested_at": datetime.now().isoformat(),
                "processed": False,
                "chunk_ids": [],
                "embedding_ids": []
            }
            
            self.document_store[kb_name][doc_id] = document_record
            
            ingestion_result = {
                "document_id": doc_id,
                "status": "ingested",
                "content_length": len(doc["content"]),
                "metadata_keys": list(document_record["metadata"].keys())
            }
            
            # Auto-process if requested
            if auto_process:
                try:
                    process_result = await self._process_single_document(kb_name, doc_id)
                    ingestion_result.update(process_result)
                    ingestion_result["status"] = "processed"
                except Exception as e:
                    ingestion_result["processing_error"] = str(e)
            
            ingestion_results.append(ingestion_result)
        
        # Update knowledge base stats
        self.knowledge_bases[kb_name]["document_count"] = len(self.document_store[kb_name])
        self.knowledge_bases[kb_name]["last_updated"] = datetime.now().isoformat()
        
        return {
            "kb_name": kb_name,
            "ingested_documents": len(documents),
            "ingestion_results": ingestion_results,
            "total_documents": self.knowledge_bases[kb_name]["document_count"]
        }

    async def _process_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process documents with cleaning, chunking, and embedding generation."""
        kb_name = params["kb_name"]
        document_ids = params.get("document_ids", [])
        processing_config = params.get("processing_config", {})
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        # Get documents to process
        if document_ids:
            docs_to_process = document_ids
        else:
            # Process all unprocessed documents
            docs_to_process = [
                doc_id for doc_id, doc in self.document_store[kb_name].items()
                if not doc.get("processed", False)
            ]
        
        processing_results = []
        
        for doc_id in docs_to_process:
            try:
                result = await self._process_single_document(kb_name, doc_id, processing_config)
                processing_results.append({
                    "document_id": doc_id,
                    "status": "success",
                    **result
                })
            except Exception as e:
                processing_results.append({
                    "document_id": doc_id,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "kb_name": kb_name,
            "processed_documents": len(processing_results),
            "processing_results": processing_results
        }

    async def _create_chunks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create text chunks from documents."""
        kb_name = params["kb_name"]
        document_id = params["document_id"]
        chunk_size = params.get("chunk_size", self.default_chunk_size)
        chunk_overlap = params.get("chunk_overlap", self.default_chunk_overlap)
        chunking_strategy = params.get("chunking_strategy", "sliding_window")
        preserve_structure = params.get("preserve_structure", True)
        
        if kb_name not in self.document_store or document_id not in self.document_store[kb_name]:
            raise NodeValidationError(f"Document '{document_id}' not found in knowledge base '{kb_name}'")
        
        document = self.document_store[kb_name][document_id]
        content = document["content"]
        
        # Create chunks based on strategy
        if chunking_strategy == "sliding_window":
            chunks = self._sliding_window_chunking(content, chunk_size, chunk_overlap)
        elif chunking_strategy == "sentence_aware":
            chunks = self._sentence_aware_chunking(content, chunk_size, chunk_overlap)
        elif chunking_strategy == "semantic":
            chunks = self._semantic_chunking(content, chunk_size)
        elif chunking_strategy == "paragraph":
            chunks = self._paragraph_chunking(content, chunk_size)
        else:
            chunks = self._sliding_window_chunking(content, chunk_size, chunk_overlap)
        
        # Store chunks
        if kb_name not in self.chunk_store:
            self.chunk_store[kb_name] = {}
        
        chunk_ids = []
        chunk_records = []
        
        for i, chunk_content in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{i}"
            
            chunk_record = {
                "id": chunk_id,
                "document_id": document_id,
                "content": chunk_content,
                "chunk_index": i,
                "character_start": self._find_chunk_start_position(content, chunk_content, i),
                "character_end": None,  # Will be calculated
                "metadata": {
                    **document["metadata"],
                    "chunk_strategy": chunking_strategy,
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap
                },
                "created_at": datetime.now().isoformat()
            }
            
            # Calculate character end position
            chunk_record["character_end"] = chunk_record["character_start"] + len(chunk_content)
            
            self.chunk_store[kb_name][chunk_id] = chunk_record
            chunk_ids.append(chunk_id)
            chunk_records.append(chunk_record)
        
        # Update document record
        self.document_store[kb_name][document_id]["chunk_ids"] = chunk_ids
        
        return {
            "document_id": document_id,
            "chunks_created": len(chunks),
            "chunk_ids": chunk_ids,
            "chunking_strategy": chunking_strategy,
            "average_chunk_length": np.mean([len(chunk) for chunk in chunks]),
            "chunk_records": chunk_records
        }

    async def _generate_embeddings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate embeddings for chunks."""
        kb_name = params["kb_name"]
        chunk_ids = params.get("chunk_ids", [])
        embedding_model = params.get("embedding_model", "sentence-transformer")
        batch_size = params.get("batch_size", 32)
        
        if kb_name not in self.chunk_store:
            raise NodeValidationError(f"No chunks found for knowledge base '{kb_name}'")
        
        # Get chunks to process
        if chunk_ids:
            chunks_to_process = chunk_ids
        else:
            chunks_to_process = list(self.chunk_store[kb_name].keys())
        
        if kb_name not in self.embedding_store:
            self.embedding_store[kb_name] = {}
        
        embedding_results = []
        
        # Process in batches
        for i in range(0, len(chunks_to_process), batch_size):
            batch_chunk_ids = chunks_to_process[i:i + batch_size]
            batch_chunks = [self.chunk_store[kb_name][cid]["content"] for cid in batch_chunk_ids]
            
            # Generate embeddings (simplified - would use actual embedding model)
            batch_embeddings = await self._generate_chunk_embeddings(batch_chunks, embedding_model)
            
            for chunk_id, embedding in zip(batch_chunk_ids, batch_embeddings):
                embedding_record = {
                    "chunk_id": chunk_id,
                    "embedding": embedding,
                    "model": embedding_model,
                    "dimension": len(embedding),
                    "generated_at": datetime.now().isoformat()
                }
                
                self.embedding_store[kb_name][chunk_id] = embedding_record
                
                embedding_results.append({
                    "chunk_id": chunk_id,
                    "embedding_dimension": len(embedding),
                    "status": "success"
                })
        
        return {
            "kb_name": kb_name,
            "processed_chunks": len(chunks_to_process),
            "embedding_model": embedding_model,
            "embedding_results": embedding_results
        }

    async def _index_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Index documents for efficient retrieval."""
        kb_name = params["kb_name"]
        index_type = params.get("index_type", "dense")  # dense, sparse, hybrid
        index_config = params.get("index_config", {})
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        indexing_results = {
            "kb_name": kb_name,
            "index_type": index_type,
            "started_at": datetime.now().isoformat()
        }
        
        if index_type in ["dense", "hybrid"]:
            # Build dense vector index
            dense_index = await self._build_dense_index(kb_name, index_config)
            indexing_results["dense_index"] = dense_index
        
        if index_type in ["sparse", "hybrid"]:
            # Build sparse keyword index
            sparse_index = await self._build_sparse_index(kb_name, index_config)
            indexing_results["sparse_index"] = sparse_index
        
        # Update knowledge base with index info
        self.knowledge_bases[kb_name]["indexes"] = {
            "type": index_type,
            "config": index_config,
            "created_at": datetime.now().isoformat()
        }
        
        indexing_results["completed_at"] = datetime.now().isoformat()
        
        return indexing_results

    async def _retrieve_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant context for a query."""
        kb_name = params["kb_name"]
        query = params["query"]
        retrieval_method = params.get("retrieval_method", "hybrid")  # dense, sparse, hybrid
        top_k = params.get("top_k", self.default_retrieval_k)
        score_threshold = params.get("score_threshold", 0.0)
        rerank = params.get("rerank", True)
        include_metadata = params.get("include_metadata", True)
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        retrieval_results = []
        
        if retrieval_method in ["dense", "hybrid"]:
            # Dense vector retrieval
            dense_results = await self._dense_retrieval(kb_name, query, top_k, score_threshold)
            retrieval_results.extend(dense_results)
        
        if retrieval_method in ["sparse", "hybrid"]:
            # Sparse keyword retrieval
            sparse_results = await self._sparse_retrieval(kb_name, query, top_k, score_threshold)
            retrieval_results.extend(sparse_results)
        
        # Remove duplicates and merge scores for hybrid
        if retrieval_method == "hybrid":
            retrieval_results = self._merge_retrieval_results(retrieval_results)
        
        # Sort by score
        retrieval_results.sort(key=lambda x: x["score"], reverse=True)
        retrieval_results = retrieval_results[:top_k]
        
        # Rerank if requested
        if rerank and len(retrieval_results) > 1:
            rerank_result = await self._rerank_results({
                "query": query,
                "results": retrieval_results,
                "rerank_method": "cross_encoder"
            })
            retrieval_results = rerank_result["reranked_results"]
        
        # Format results
        formatted_results = []
        for result in retrieval_results:
            chunk_id = result["chunk_id"]
            chunk = self.chunk_store[kb_name][chunk_id]
            
            formatted_result = {
                "chunk_id": chunk_id,
                "document_id": chunk["document_id"],
                "content": chunk["content"],
                "score": result["score"],
                "retrieval_method": result.get("method", retrieval_method)
            }
            
            if include_metadata:
                formatted_result["metadata"] = chunk["metadata"]
                formatted_result["chunk_index"] = chunk["chunk_index"]
            
            formatted_results.append(formatted_result)
        
        return {
            "kb_name": kb_name,
            "query": query,
            "retrieval_method": retrieval_method,
            "retrieved_chunks": len(formatted_results),
            "results": formatted_results,
            "total_score": sum(r["score"] for r in formatted_results)
        }

    async def _rerank_results(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rerank retrieval results for improved relevance."""
        query = params["query"]
        results = params["results"]
        rerank_method = params.get("rerank_method", "cross_encoder")
        top_k = params.get("top_k", len(results))
        
        if rerank_method == "cross_encoder":
            reranked_results = await self._cross_encoder_rerank(query, results)
        elif rerank_method == "diversity":
            reranked_results = await self._diversity_rerank(query, results)
        elif rerank_method == "temporal":
            reranked_results = await self._temporal_rerank(query, results)
        elif rerank_method == "relevance_feedback":
            reranked_results = await self._relevance_feedback_rerank(query, results, params.get("feedback", {}))
        else:
            reranked_results = results
        
        return {
            "query": query,
            "rerank_method": rerank_method,
            "original_results": len(results),
            "reranked_results": reranked_results[:top_k],
            "reranking_score_change": self._calculate_score_change(results, reranked_results)
        }

    async def _generate_response(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using retrieved context."""
        query = params["query"]
        context_chunks = params["context_chunks"]
        model_config = params.get("model_config", {})
        response_style = params.get("response_style", "informative")
        include_citations = params.get("include_citations", True)
        max_context_length = params.get("max_context_length", self.max_context_length)
        
        # Prepare context
        context_preparation = await self._prepare_context_for_generation(
            context_chunks, max_context_length, include_citations
        )
        
        context_text = context_preparation["context_text"]
        citation_mapping = context_preparation["citations"]
        
        # Generate prompt
        prompt = self._build_generation_prompt(query, context_text, response_style)
        
        # Generate response (simplified - would use actual LLM)
        response = await self._generate_llm_response(prompt, model_config)
        
        # Post-process response
        if include_citations:
            response = self._add_citations_to_response(response, citation_mapping)
        
        # Validate response
        validation_result = await self._validate_generated_response(response, context_chunks, query)
        
        return {
            "query": query,
            "response": response,
            "context_used": len(context_chunks),
            "context_length": len(context_text),
            "citations": citation_mapping if include_citations else None,
            "validation": validation_result,
            "generation_metadata": {
                "response_style": response_style,
                "model_config": model_config,
                "prompt_tokens": len(prompt.split()),
                "response_tokens": len(response.split())
            }
        }

    async def _full_rag_pipeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete RAG pipeline from query to response."""
        kb_name = params["kb_name"]
        query = params["query"]
        pipeline_config = params.get("pipeline_config", {})
        
        # Pipeline configuration with defaults
        retrieval_config = pipeline_config.get("retrieval", {})
        rerank_config = pipeline_config.get("rerank", {})
        generation_config = pipeline_config.get("generation", {})
        
        pipeline_results = {
            "kb_name": kb_name,
            "query": query,
            "pipeline_started_at": datetime.now().isoformat(),
            "steps": {}
        }
        
        try:
            # Step 1: Query preprocessing
            preprocessed_query = await self._preprocess_query(query, pipeline_config.get("preprocessing", {}))
            pipeline_results["steps"]["preprocessing"] = {
                "original_query": query,
                "preprocessed_query": preprocessed_query,
                "status": "completed"
            }
            
            # Step 2: Context retrieval
            retrieval_result = await self._retrieve_context({
                "kb_name": kb_name,
                "query": preprocessed_query,
                **retrieval_config
            })
            pipeline_results["steps"]["retrieval"] = {
                "retrieved_chunks": retrieval_result["retrieved_chunks"],
                "total_score": retrieval_result["total_score"],
                "status": "completed"
            }
            
            # Step 3: Reranking (if enabled)
            if rerank_config.get("enabled", True):
                rerank_result = await self._rerank_results({
                    "query": preprocessed_query,
                    "results": retrieval_result["results"],
                    **rerank_config
                })
                context_chunks = rerank_result["reranked_results"]
                pipeline_results["steps"]["reranking"] = {
                    "rerank_method": rerank_result["rerank_method"],
                    "score_change": rerank_result["reranking_score_change"],
                    "status": "completed"
                }
            else:
                context_chunks = retrieval_result["results"]
                pipeline_results["steps"]["reranking"] = {"status": "skipped"}
            
            # Step 4: Response generation
            generation_result = await self._generate_response({
                "query": query,  # Use original query for generation
                "context_chunks": context_chunks,
                **generation_config
            })
            pipeline_results["steps"]["generation"] = {
                "response_length": len(generation_result["response"]),
                "context_used": generation_result["context_used"],
                "validation": generation_result["validation"],
                "status": "completed"
            }
            
            # Pipeline summary
            pipeline_results.update({
                "final_response": generation_result["response"],
                "citations": generation_result.get("citations"),
                "context_chunks": context_chunks,
                "pipeline_completed_at": datetime.now().isoformat(),
                "total_pipeline_time": (datetime.now() - datetime.fromisoformat(pipeline_results["pipeline_started_at"])).total_seconds(),
                "status": "success"
            })
            
        except Exception as e:
            pipeline_results.update({
                "status": "error",
                "error": str(e),
                "pipeline_failed_at": datetime.now().isoformat()
            })
        
        return pipeline_results

    async def _update_knowledge_base(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update knowledge base with new or modified documents."""
        kb_name = params["kb_name"]
        updates = params["updates"]  # List of update operations
        incremental = params.get("incremental", True)
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        update_results = []
        
        for update in updates:
            update_type = update["type"]  # add, modify, delete
            
            try:
                if update_type == "add":
                    result = await self._add_document_to_kb(kb_name, update["document"])
                elif update_type == "modify":
                    result = await self._modify_document_in_kb(kb_name, update["document_id"], update["changes"])
                elif update_type == "delete":
                    result = await self._delete_document_from_kb(kb_name, update["document_id"])
                else:
                    result = {"status": "error", "error": f"Unknown update type: {update_type}"}
                
                update_results.append({
                    "update_type": update_type,
                    "result": result
                })
                
            except Exception as e:
                update_results.append({
                    "update_type": update_type,
                    "result": {"status": "error", "error": str(e)}
                })
        
        # Rebuild indexes if needed
        if incremental:
            await self._incremental_index_update(kb_name, updates)
        else:
            await self._full_index_rebuild(kb_name)
        
        # Update knowledge base metadata
        self.knowledge_bases[kb_name]["last_updated"] = datetime.now().isoformat()
        self.knowledge_bases[kb_name]["document_count"] = len(self.document_store.get(kb_name, {}))
        
        return {
            "kb_name": kb_name,
            "updates_processed": len(updates),
            "update_results": update_results,
            "incremental_update": incremental,
            "updated_at": datetime.now().isoformat()
        }

    async def _delete_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete documents from knowledge base."""
        kb_name = params["kb_name"]
        document_ids = params["document_ids"]
        cleanup_chunks = params.get("cleanup_chunks", True)
        cleanup_embeddings = params.get("cleanup_embeddings", True)
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        deletion_results = []
        
        for doc_id in document_ids:
            try:
                # Delete document
                if doc_id in self.document_store[kb_name]:
                    document = self.document_store[kb_name][doc_id]
                    
                    # Cleanup related chunks
                    if cleanup_chunks and kb_name in self.chunk_store:
                        for chunk_id in document.get("chunk_ids", []):
                            if chunk_id in self.chunk_store[kb_name]:
                                del self.chunk_store[kb_name][chunk_id]
                    
                    # Cleanup embeddings
                    if cleanup_embeddings and kb_name in self.embedding_store:
                        for chunk_id in document.get("chunk_ids", []):
                            if chunk_id in self.embedding_store[kb_name]:
                                del self.embedding_store[kb_name][chunk_id]
                    
                    del self.document_store[kb_name][doc_id]
                    
                    deletion_results.append({
                        "document_id": doc_id,
                        "status": "deleted",
                        "chunks_removed": len(document.get("chunk_ids", [])),
                        "embeddings_removed": len(document.get("chunk_ids", []))
                    })
                else:
                    deletion_results.append({
                        "document_id": doc_id,
                        "status": "not_found"
                    })
                    
            except Exception as e:
                deletion_results.append({
                    "document_id": doc_id,
                    "status": "error",
                    "error": str(e)
                })
        
        # Update knowledge base stats
        self.knowledge_bases[kb_name]["document_count"] = len(self.document_store[kb_name])
        self.knowledge_bases[kb_name]["last_updated"] = datetime.now().isoformat()
        
        return {
            "kb_name": kb_name,
            "deletion_results": deletion_results,
            "remaining_documents": self.knowledge_bases[kb_name]["document_count"]
        }

    async def _search_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search documents in knowledge base."""
        kb_name = params["kb_name"]
        search_query = params["search_query"]
        search_type = params.get("search_type", "semantic")  # semantic, keyword, hybrid
        filters = params.get("filters", {})
        limit = params.get("limit", 10)
        include_content = params.get("include_content", True)
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        search_results = []
        
        if search_type in ["semantic", "hybrid"]:
            # Semantic search
            semantic_results = await self._semantic_document_search(kb_name, search_query, filters, limit)
            search_results.extend(semantic_results)
        
        if search_type in ["keyword", "hybrid"]:
            # Keyword search
            keyword_results = await self._keyword_document_search(kb_name, search_query, filters, limit)
            search_results.extend(keyword_results)
        
        # Merge and deduplicate results
        if search_type == "hybrid":
            search_results = self._merge_search_results(search_results)
        
        # Sort by relevance score
        search_results.sort(key=lambda x: x["score"], reverse=True)
        search_results = search_results[:limit]
        
        # Format results
        formatted_results = []
        for result in search_results:
            doc_id = result["document_id"]
            document = self.document_store[kb_name][doc_id]
            
            formatted_result = {
                "document_id": doc_id,
                "score": result["score"],
                "metadata": document["metadata"],
                "type": document["type"],
                "ingested_at": document["ingested_at"]
            }
            
            if include_content:
                formatted_result["content"] = document["content"]
                formatted_result["content_preview"] = document["content"][:200] + "..." if len(document["content"]) > 200 else document["content"]
            
            formatted_results.append(formatted_result)
        
        return {
            "kb_name": kb_name,
            "search_query": search_query,
            "search_type": search_type,
            "results": formatted_results,
            "total_results": len(formatted_results)
        }

    async def _extract_entities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract named entities from documents."""
        kb_name = params["kb_name"]
        document_ids = params.get("document_ids", [])
        entity_types = params.get("entity_types", ["PERSON", "ORG", "LOC", "MISC"])
        extraction_method = params.get("extraction_method", "rule_based")
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        # Get documents to process
        if document_ids:
            docs_to_process = document_ids
        else:
            docs_to_process = list(self.document_store[kb_name].keys())
        
        entity_extraction_results = []
        
        for doc_id in docs_to_process:
            if doc_id not in self.document_store[kb_name]:
                continue
            
            document = self.document_store[kb_name][doc_id]
            content = document["content"]
            
            # Extract entities based on method
            if extraction_method == "rule_based":
                entities = self._rule_based_entity_extraction(content, entity_types)
            elif extraction_method == "ml_based":
                entities = await self._ml_based_entity_extraction(content, entity_types)
            else:
                entities = self._rule_based_entity_extraction(content, entity_types)
            
            entity_extraction_results.append({
                "document_id": doc_id,
                "entities": entities,
                "entity_count": len(entities),
                "extraction_method": extraction_method
            })
        
        # Aggregate entity statistics
        all_entities = []
        for result in entity_extraction_results:
            all_entities.extend(result["entities"])
        
        entity_stats = self._calculate_entity_statistics(all_entities)
        
        return {
            "kb_name": kb_name,
            "processed_documents": len(entity_extraction_results),
            "extraction_results": entity_extraction_results,
            "entity_statistics": entity_stats,
            "total_entities": len(all_entities)
        }

    async def _summarize_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summaries for documents."""
        kb_name = params["kb_name"]
        document_ids = params.get("document_ids", [])
        summary_type = params.get("summary_type", "extractive")  # extractive, abstractive
        summary_length = params.get("summary_length", "medium")  # short, medium, long
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        # Get documents to summarize
        if document_ids:
            docs_to_summarize = document_ids
        else:
            docs_to_summarize = list(self.document_store[kb_name].keys())
        
        summarization_results = []
        
        for doc_id in docs_to_summarize:
            if doc_id not in self.document_store[kb_name]:
                continue
            
            document = self.document_store[kb_name][doc_id]
            content = document["content"]
            
            # Generate summary
            if summary_type == "extractive":
                summary = self._extractive_summarization(content, summary_length)
            elif summary_type == "abstractive":
                summary = await self._abstractive_summarization(content, summary_length)
            else:
                summary = self._extractive_summarization(content, summary_length)
            
            summarization_results.append({
                "document_id": doc_id,
                "summary": summary,
                "summary_type": summary_type,
                "summary_length": summary_length,
                "compression_ratio": len(summary) / len(content),
                "original_length": len(content),
                "summary_word_count": len(summary.split())
            })
        
        return {
            "kb_name": kb_name,
            "summarized_documents": len(summarization_results),
            "summarization_results": summarization_results,
            "summary_type": summary_type
        }

    async def _fact_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fact-check statements against knowledge base."""
        kb_name = params["kb_name"]
        statements = params["statements"]
        confidence_threshold = params.get("confidence_threshold", 0.7)
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        fact_check_results = []
        
        for statement in statements:
            # Retrieve relevant context for fact-checking
            retrieval_result = await self._retrieve_context({
                "kb_name": kb_name,
                "query": statement,
                "top_k": 5,
                "retrieval_method": "hybrid"
            })
            
            # Analyze statement against context
            fact_check_result = await self._analyze_fact_claim(statement, retrieval_result["results"])
            
            fact_check_results.append({
                "statement": statement,
                "verification_status": fact_check_result["status"],  # supported, contradicted, insufficient_evidence
                "confidence": fact_check_result["confidence"],
                "supporting_evidence": fact_check_result["supporting_evidence"],
                "contradicting_evidence": fact_check_result["contradicting_evidence"],
                "explanation": fact_check_result["explanation"]
            })
        
        return {
            "kb_name": kb_name,
            "fact_check_results": fact_check_results,
            "statements_checked": len(statements),
            "confidence_threshold": confidence_threshold
        }

    async def _citation_tracking(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Track citations and sources in generated responses."""
        response_text = params["response_text"]
        context_chunks = params["context_chunks"]
        citation_style = params.get("citation_style", "academic")  # academic, numbered, inline
        
        # Extract citation information from context chunks
        citations = []
        for i, chunk in enumerate(context_chunks):
            citation = {
                "id": i + 1,
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "source": chunk.get("metadata", {}).get("source", "Unknown"),
                "title": chunk.get("metadata", {}).get("title", "Untitled"),
                "author": chunk.get("metadata", {}).get("author", "Unknown"),
                "date": chunk.get("metadata", {}).get("date", "Unknown"),
                "page": chunk.get("metadata", {}).get("page"),
                "url": chunk.get("metadata", {}).get("url")
            }
            citations.append(citation)
        
        # Format citations according to style
        if citation_style == "academic":
            formatted_citations = self._format_academic_citations(citations)
        elif citation_style == "numbered":
            formatted_citations = self._format_numbered_citations(citations)
        elif citation_style == "inline":
            formatted_citations = self._format_inline_citations(citations)
        else:
            formatted_citations = citations
        
        # Add citation markers to response text
        response_with_citations = self._add_citation_markers(response_text, context_chunks, citation_style)
        
        return {
            "original_response": response_text,
            "response_with_citations": response_with_citations,
            "citations": formatted_citations,
            "citation_style": citation_style,
            "total_citations": len(citations)
        }

    async def _context_compression(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compress context to fit within model limits while preserving relevance."""
        context_chunks = params["context_chunks"]
        query = params["query"]
        max_tokens = params.get("max_tokens", 3000)
        compression_method = params.get("compression_method", "selective")  # selective, summarize, truncate
        
        # Estimate current token count
        current_tokens = sum(len(chunk["content"].split()) for chunk in context_chunks)
        
        if current_tokens <= max_tokens:
            return {
                "compressed_context": context_chunks,
                "compression_applied": False,
                "original_tokens": current_tokens,
                "final_tokens": current_tokens,
                "compression_ratio": 1.0
            }
        
        # Apply compression
        if compression_method == "selective":
            compressed_chunks = self._selective_chunk_compression(context_chunks, query, max_tokens)
        elif compression_method == "summarize":
            compressed_chunks = await self._summarize_context_chunks(context_chunks, max_tokens)
        elif compression_method == "truncate":
            compressed_chunks = self._truncate_context_chunks(context_chunks, max_tokens)
        else:
            compressed_chunks = context_chunks
        
        final_tokens = sum(len(chunk["content"].split()) for chunk in compressed_chunks)
        
        return {
            "compressed_context": compressed_chunks,
            "compression_applied": True,
            "compression_method": compression_method,
            "original_tokens": current_tokens,
            "final_tokens": final_tokens,
            "compression_ratio": final_tokens / current_tokens,
            "chunks_removed": len(context_chunks) - len(compressed_chunks)
        }

    async def _multi_hop_reasoning(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform multi-hop reasoning across knowledge base."""
        kb_name = params["kb_name"]
        query = params["query"]
        max_hops = params.get("max_hops", 3)
        reasoning_strategy = params.get("reasoning_strategy", "iterative")  # iterative, graph_based
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        reasoning_path = []
        current_query = query
        
        for hop in range(max_hops):
            # Retrieve relevant context for current query
            retrieval_result = await self._retrieve_context({
                "kb_name": kb_name,
                "query": current_query,
                "top_k": 5,
                "retrieval_method": "hybrid"
            })
            
            hop_result = {
                "hop_number": hop + 1,
                "query": current_query,
                "retrieved_chunks": retrieval_result["retrieved_chunks"],
                "context": retrieval_result["results"]
            }
            
            # Analyze context and generate follow-up questions
            if reasoning_strategy == "iterative":
                analysis = await self._analyze_context_for_gaps(current_query, retrieval_result["results"])
                
                if analysis["has_sufficient_info"]:
                    hop_result["conclusion"] = "Sufficient information found"
                    reasoning_path.append(hop_result)
                    break
                else:
                    # Generate follow-up query
                    current_query = analysis["follow_up_query"]
                    hop_result["follow_up_query"] = current_query
            
            reasoning_path.append(hop_result)
        
        # Synthesize final answer from all hops
        final_answer = await self._synthesize_multi_hop_answer(query, reasoning_path)
        
        return {
            "kb_name": kb_name,
            "original_query": query,
            "reasoning_path": reasoning_path,
            "total_hops": len(reasoning_path),
            "reasoning_strategy": reasoning_strategy,
            "final_answer": final_answer,
            "reasoning_complete": True
        }

    async def _adaptive_retrieval(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptively adjust retrieval strategy based on query characteristics."""
        kb_name = params["kb_name"]
        query = params["query"]
        adaptation_criteria = params.get("adaptation_criteria", ["query_type", "complexity", "specificity"])
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        # Analyze query characteristics
        query_analysis = self._analyze_query_characteristics(query)
        
        # Determine optimal retrieval strategy
        retrieval_strategy = self._determine_retrieval_strategy(query_analysis, adaptation_criteria)
        
        # Execute adaptive retrieval
        retrieval_result = await self._retrieve_context({
            "kb_name": kb_name,
            "query": query,
            **retrieval_strategy["config"]
        })
        
        return {
            "kb_name": kb_name,
            "query": query,
            "query_analysis": query_analysis,
            "selected_strategy": retrieval_strategy,
            "retrieval_result": retrieval_result,
            "adaptation_applied": True
        }

    async def _query_expansion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Expand query to improve retrieval coverage."""
        query = params["query"]
        expansion_method = params.get("expansion_method", "semantic")  # semantic, synonyms, related_terms
        max_expansions = params.get("max_expansions", 5)
        
        expanded_terms = []
        
        if expansion_method == "semantic":
            expanded_terms = await self._semantic_query_expansion(query, max_expansions)
        elif expansion_method == "synonyms":
            expanded_terms = self._synonym_query_expansion(query, max_expansions)
        elif expansion_method == "related_terms":
            expanded_terms = await self._related_terms_expansion(query, max_expansions)
        
        # Create expanded query
        expanded_query = self._construct_expanded_query(query, expanded_terms)
        
        return {
            "original_query": query,
            "expanded_terms": expanded_terms,
            "expanded_query": expanded_query,
            "expansion_method": expansion_method,
            "expansion_count": len(expanded_terms)
        }

    async def _query_decomposition(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Decompose complex queries into simpler sub-queries."""
        query = params["query"]
        decomposition_method = params.get("decomposition_method", "semantic")  # semantic, syntactic, logical
        max_subqueries = params.get("max_subqueries", 5)
        
        # Analyze query complexity
        complexity_analysis = self._analyze_query_complexity(query)
        
        if not complexity_analysis["is_complex"]:
            return {
                "original_query": query,
                "subqueries": [{"query": query, "type": "original"}],
                "decomposition_applied": False,
                "complexity_analysis": complexity_analysis
            }
        
        # Decompose query
        if decomposition_method == "semantic":
            subqueries = await self._semantic_query_decomposition(query, max_subqueries)
        elif decomposition_method == "syntactic":
            subqueries = self._syntactic_query_decomposition(query, max_subqueries)
        elif decomposition_method == "logical":
            subqueries = self._logical_query_decomposition(query, max_subqueries)
        else:
            subqueries = [{"query": query, "type": "original"}]
        
        return {
            "original_query": query,
            "subqueries": subqueries,
            "decomposition_method": decomposition_method,
            "decomposition_applied": True,
            "complexity_analysis": complexity_analysis,
            "subquery_count": len(subqueries)
        }

    async def _answer_validation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated answers for accuracy and consistency."""
        answer = params["answer"]
        context_chunks = params["context_chunks"]
        query = params["query"]
        validation_criteria = params.get("validation_criteria", ["factual_consistency", "relevance", "completeness"])
        
        validation_results = {}
        
        if "factual_consistency" in validation_criteria:
            factual_score = await self._validate_factual_consistency(answer, context_chunks)
            validation_results["factual_consistency"] = factual_score
        
        if "relevance" in validation_criteria:
            relevance_score = await self._validate_answer_relevance(answer, query)
            validation_results["relevance"] = relevance_score
        
        if "completeness" in validation_criteria:
            completeness_score = await self._validate_answer_completeness(answer, query, context_chunks)
            validation_results["completeness"] = completeness_score
        
        if "coherence" in validation_criteria:
            coherence_score = await self._validate_answer_coherence(answer)
            validation_results["coherence"] = coherence_score
        
        # Calculate overall validation score
        overall_score = np.mean(list(validation_results.values()))
        
        # Determine validation status
        if overall_score >= 0.8:
            validation_status = "high_quality"
        elif overall_score >= 0.6:
            validation_status = "acceptable"
        else:
            validation_status = "needs_improvement"
        
        return {
            "answer": answer,
            "validation_results": validation_results,
            "overall_score": overall_score,
            "validation_status": validation_status,
            "validation_criteria": validation_criteria,
            "recommendations": self._generate_validation_recommendations(validation_results)
        }

    async def _knowledge_graph_rag(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """RAG with knowledge graph integration."""
        kb_name = params["kb_name"]
        query = params["query"]
        kg_integration = params.get("kg_integration", "entity_linking")  # entity_linking, relation_extraction, graph_traversal
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        # Build or retrieve knowledge graph
        knowledge_graph = await self._build_knowledge_graph(kb_name)
        
        # Process query with knowledge graph
        if kg_integration == "entity_linking":
            kg_result = await self._entity_linking_rag(query, knowledge_graph, kb_name)
        elif kg_integration == "relation_extraction":
            kg_result = await self._relation_extraction_rag(query, knowledge_graph, kb_name)
        elif kg_integration == "graph_traversal":
            kg_result = await self._graph_traversal_rag(query, knowledge_graph, kb_name)
        else:
            kg_result = await self._entity_linking_rag(query, knowledge_graph, kb_name)
        
        return {
            "kb_name": kb_name,
            "query": query,
            "kg_integration": kg_integration,
            "knowledge_graph_stats": {
                "entities": len(knowledge_graph.get("entities", {})),
                "relations": len(knowledge_graph.get("relations", {}))
            },
            "kg_enhanced_result": kg_result
        }

    async def _conversational_rag(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """RAG for conversational context with memory."""
        kb_name = params["kb_name"]
        current_query = params["current_query"]
        conversation_history = params.get("conversation_history", [])
        context_window = params.get("context_window", 5)
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        # Analyze conversation context
        conversation_context = self._analyze_conversation_context(conversation_history, context_window)
        
        # Enhance query with conversational context
        enhanced_query = self._enhance_query_with_conversation(current_query, conversation_context)
        
        # Perform context-aware retrieval
        retrieval_result = await self._retrieve_context({
            "kb_name": kb_name,
            "query": enhanced_query,
            "top_k": 7,  # Slightly more for conversational context
            "retrieval_method": "hybrid"
        })
        
        # Generate conversational response
        response_result = await self._generate_conversational_response(
            current_query, enhanced_query, retrieval_result["results"], conversation_context
        )
        
        return {
            "kb_name": kb_name,
            "current_query": current_query,
            "enhanced_query": enhanced_query,
            "conversation_context": conversation_context,
            "retrieval_result": retrieval_result,
            "conversational_response": response_result
        }

    async def _multi_modal_rag(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """RAG with multi-modal content support."""
        kb_name = params["kb_name"]
        query = params["query"]
        modalities = params.get("modalities", ["text", "image"])
        fusion_strategy = params.get("fusion_strategy", "late_fusion")  # early_fusion, late_fusion
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        multimodal_results = {}
        
        # Process each modality
        for modality in modalities:
            if modality == "text":
                modality_result = await self._retrieve_context({
                    "kb_name": kb_name,
                    "query": query,
                    "top_k": 5
                })
            elif modality == "image":
                modality_result = await self._retrieve_image_context(kb_name, query)
            elif modality == "audio":
                modality_result = await self._retrieve_audio_context(kb_name, query)
            else:
                continue
            
            multimodal_results[modality] = modality_result
        
        # Fuse multimodal results
        if fusion_strategy == "early_fusion":
            fused_result = self._early_fusion_multimodal(multimodal_results)
        elif fusion_strategy == "late_fusion":
            fused_result = self._late_fusion_multimodal(multimodal_results)
        else:
            fused_result = multimodal_results
        
        return {
            "kb_name": kb_name,
            "query": query,
            "modalities": modalities,
            "fusion_strategy": fusion_strategy,
            "multimodal_results": multimodal_results,
            "fused_result": fused_result
        }

    async def _rag_evaluation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate RAG system performance."""
        kb_name = params["kb_name"]
        evaluation_dataset = params["evaluation_dataset"]  # List of {query, expected_answer, ground_truth_docs}
        metrics = params.get("metrics", ["accuracy", "relevance", "faithfulness", "context_precision", "context_recall"])
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        evaluation_results = []
        
        for eval_item in evaluation_dataset:
            query = eval_item["query"]
            expected_answer = eval_item.get("expected_answer")
            ground_truth_docs = eval_item.get("ground_truth_docs", [])
            
            # Run RAG pipeline
            rag_result = await self._full_rag_pipeline({
                "kb_name": kb_name,
                "query": query
            })
            
            # Calculate metrics
            item_metrics = {}
            
            if "accuracy" in metrics and expected_answer:
                item_metrics["accuracy"] = self._calculate_accuracy_score(rag_result["final_response"], expected_answer)
            
            if "relevance" in metrics:
                item_metrics["relevance"] = self._calculate_relevance_score(rag_result["final_response"], query)
            
            if "faithfulness" in metrics:
                item_metrics["faithfulness"] = self._calculate_faithfulness_score(
                    rag_result["final_response"], rag_result["context_chunks"]
                )
            
            if "context_precision" in metrics and ground_truth_docs:
                item_metrics["context_precision"] = self._calculate_context_precision(
                    rag_result["context_chunks"], ground_truth_docs
                )
            
            if "context_recall" in metrics and ground_truth_docs:
                item_metrics["context_recall"] = self._calculate_context_recall(
                    rag_result["context_chunks"], ground_truth_docs
                )
            
            evaluation_results.append({
                "query": query,
                "generated_answer": rag_result["final_response"],
                "expected_answer": expected_answer,
                "metrics": item_metrics,
                "retrieval_results": len(rag_result["context_chunks"])
            })
        
        # Aggregate metrics
        aggregated_metrics = {}
        for metric in metrics:
            metric_values = [result["metrics"].get(metric, 0) for result in evaluation_results]
            aggregated_metrics[metric] = {
                "mean": np.mean(metric_values),
                "std": np.std(metric_values),
                "min": np.min(metric_values),
                "max": np.max(metric_values)
            }
        
        return {
            "kb_name": kb_name,
            "evaluation_results": evaluation_results,
            "aggregated_metrics": aggregated_metrics,
            "total_queries": len(evaluation_dataset),
            "metrics_evaluated": metrics
        }

    async def _performance_optimization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize RAG system performance."""
        kb_name = params["kb_name"]
        optimization_targets = params.get("optimization_targets", ["latency", "accuracy", "cost"])
        optimization_method = params.get("optimization_method", "automated")  # automated, manual, hybrid
        
        if kb_name not in self.knowledge_bases:
            raise NodeValidationError(f"Knowledge base '{kb_name}' not found")
        
        optimization_results = {
            "kb_name": kb_name,
            "optimization_targets": optimization_targets,
            "optimization_method": optimization_method,
            "optimizations_applied": []
        }
        
        # Analyze current performance
        current_performance = await self._analyze_rag_performance(kb_name)
        
        # Apply optimizations based on targets
        if "latency" in optimization_targets:
            latency_optimization = await self._optimize_latency(kb_name, current_performance)
            optimization_results["optimizations_applied"].append(latency_optimization)
        
        if "accuracy" in optimization_targets:
            accuracy_optimization = await self._optimize_accuracy(kb_name, current_performance)
            optimization_results["optimizations_applied"].append(accuracy_optimization)
        
        if "cost" in optimization_targets:
            cost_optimization = await self._optimize_cost(kb_name, current_performance)
            optimization_results["optimizations_applied"].append(cost_optimization)
        
        # Measure post-optimization performance
        post_optimization_performance = await self._analyze_rag_performance(kb_name)
        
        optimization_results.update({
            "pre_optimization_performance": current_performance,
            "post_optimization_performance": post_optimization_performance,
            "improvement_metrics": self._calculate_improvement_metrics(
                current_performance, post_optimization_performance
            )
        })
        
        return optimization_results

    # Helper methods
    def _generate_document_id(self) -> str:
        """Generate unique document ID."""
        return f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now()) % 10000}"

    async def _process_single_document(self, kb_name: str, doc_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a single document through the RAG pipeline."""
        config = config or {}
        
        # Create chunks
        chunk_result = await self._create_chunks({
            "kb_name": kb_name,
            "document_id": doc_id,
            **config
        })
        
        # Generate embeddings
        embedding_result = await self._generate_embeddings({
            "kb_name": kb_name,
            "chunk_ids": chunk_result["chunk_ids"]
        })
        
        # Mark document as processed
        self.document_store[kb_name][doc_id]["processed"] = True
        self.document_store[kb_name][doc_id]["processing_completed_at"] = datetime.now().isoformat()
        
        return {
            "chunks_created": chunk_result["chunks_created"],
            "embeddings_generated": len(embedding_result["embedding_results"])
        }

    def _sliding_window_chunking(self, content: str, chunk_size: int, overlap: int) -> List[str]:
        """Create overlapping chunks using sliding window."""
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            if chunk_words:
                chunks.append(" ".join(chunk_words))
            
            if i + chunk_size >= len(words):
                break
        
        return chunks

    def _sentence_aware_chunking(self, content: str, chunk_size: int, overlap: int) -> List[str]:
        """Create chunks respecting sentence boundaries."""
        sentences = re.split(r'[.!?]+', content)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > chunk_size and current_chunk:
                # Finalize current chunk
                chunks.append(" ".join(current_chunk))
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def _semantic_chunking(self, content: str, chunk_size: int) -> List[str]:
        """Create semantically coherent chunks."""
        # Simplified semantic chunking - would use embeddings in practice
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            para_length = len(paragraph.split())
            
            if current_length + para_length > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [paragraph]
                current_length = para_length
            else:
                current_chunk.append(paragraph)
                current_length += para_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def _paragraph_chunking(self, content: str, chunk_size: int) -> List[str]:
        """Create chunks based on paragraph boundaries."""
        paragraphs = content.split('\n\n')
        chunks = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If paragraph is too long, split it
            if len(paragraph.split()) > chunk_size:
                sub_chunks = self._sliding_window_chunking(paragraph, chunk_size, 0)
                chunks.extend(sub_chunks)
            else:
                chunks.append(paragraph)
        
        return chunks

    def _find_chunk_start_position(self, content: str, chunk_content: str, chunk_index: int) -> int:
        """Find the starting character position of a chunk in the original content."""
        # Simplified implementation
        start_pos = content.find(chunk_content[:100])  # Use first 100 chars for matching
        return max(0, start_pos) if start_pos != -1 else chunk_index * 500  # Fallback

    async def _generate_chunk_embeddings(self, chunks: List[str], model: str) -> List[List[float]]:
        """Generate embeddings for chunks (simplified)."""
        embeddings = []
        
        for chunk in chunks:
            # Simplified embedding generation - would use actual model
            words = chunk.lower().split()
            
            # Create a simple hash-based embedding
            embedding = []
            for i in range(384):  # Standard embedding size
                hash_val = hash(f"{chunk}_{i}") % 1000000
                embedding.append((hash_val / 1000000) * 2 - 1)  # Normalize to [-1, 1]
            
            # Normalize embedding
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = [x / norm for x in embedding]
            
            embeddings.append(embedding)
        
        return embeddings

    async def _build_dense_index(self, kb_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build dense vector index."""
        if kb_name not in self.embedding_store:
            return {"status": "no_embeddings", "indexed_count": 0}
        
        embeddings = self.embedding_store[kb_name]
        
        # Simplified index building - would use FAISS or similar
        index_info = {
            "type": "dense",
            "embedding_count": len(embeddings),
            "dimension": len(next(iter(embeddings.values()))["embedding"]) if embeddings else 0,
            "index_size_mb": len(embeddings) * 384 * 4 / (1024 * 1024),  # Rough estimate
            "created_at": datetime.now().isoformat()
        }
        
        return index_info

    async def _build_sparse_index(self, kb_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build sparse keyword index."""
        if kb_name not in self.chunk_store:
            return {"status": "no_chunks", "indexed_count": 0}
        
        chunks = self.chunk_store[kb_name]
        
        # Build inverted index
        inverted_index = {}
        for chunk_id, chunk_data in chunks.items():
            words = chunk_data["content"].lower().split()
            for word in set(words):  # Unique words only
                if word not in inverted_index:
                    inverted_index[word] = []
                inverted_index[word].append(chunk_id)
        
        index_info = {
            "type": "sparse",
            "vocabulary_size": len(inverted_index),
            "chunk_count": len(chunks),
            "avg_postings_per_term": np.mean([len(postings) for postings in inverted_index.values()]),
            "created_at": datetime.now().isoformat()
        }
        
        return index_info

    async def _dense_retrieval(self, kb_name: str, query: str, top_k: int, score_threshold: float) -> List[Dict]:
        """Perform dense vector retrieval."""
        if kb_name not in self.embedding_store:
            return []
        
        # Generate query embedding
        query_embedding = (await self._generate_chunk_embeddings([query], "sentence-transformer"))[0]
        
        # Calculate similarities
        results = []
        for chunk_id, embedding_data in self.embedding_store[kb_name].items():
            chunk_embedding = embedding_data["embedding"]
            
            # Cosine similarity
            similarity = np.dot(query_embedding, chunk_embedding)
            
            if similarity >= score_threshold:
                results.append({
                    "chunk_id": chunk_id,
                    "score": similarity,
                    "method": "dense"
                })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

    async def _sparse_retrieval(self, kb_name: str, query: str, top_k: int, score_threshold: float) -> List[Dict]:
        """Perform sparse keyword retrieval."""
        if kb_name not in self.chunk_store:
            return []
        
        query_words = set(query.lower().split())
        chunk_scores = {}
        
        # Score chunks based on keyword overlap
        for chunk_id, chunk_data in self.chunk_store[kb_name].items():
            chunk_words = set(chunk_data["content"].lower().split())
            
            # Simple TF-IDF-like scoring
            overlap = len(query_words.intersection(chunk_words))
            total_words = len(chunk_words)
            
            if overlap > 0:
                score = overlap / len(query_words)  # Query coverage
                score *= min(1.0, overlap / total_words)  # Document relevance
                
                if score >= score_threshold:
                    chunk_scores[chunk_id] = score
        
        # Convert to result format
        results = [
            {"chunk_id": chunk_id, "score": score, "method": "sparse"}
            for chunk_id, score in chunk_scores.items()
        ]
        
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

    def _merge_retrieval_results(self, results: List[Dict]) -> List[Dict]:
        """Merge dense and sparse retrieval results."""
        merged = {}
        
        for result in results:
            chunk_id = result["chunk_id"]
            
            if chunk_id in merged:
                # Combine scores (weighted average)
                existing_score = merged[chunk_id]["score"]
                new_score = result["score"]
                
                if result["method"] == "dense":
                    combined_score = 0.7 * new_score + 0.3 * existing_score
                else:  # sparse
                    combined_score = 0.7 * existing_score + 0.3 * new_score
                
                merged[chunk_id]["score"] = combined_score
                merged[chunk_id]["method"] = "hybrid"
            else:
                merged[chunk_id] = result
        
        return list(merged.values())

    async def _cross_encoder_rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rerank using cross-encoder approach (simplified)."""
        reranked_results = []
        
        for result in results:
            chunk_id = result["chunk_id"]
            
            # Simplified cross-encoder scoring
            # In practice, would use a trained cross-encoder model
            query_chunk_pair = f"{query} [SEP] {result.get('content', '')}"
            
            # Simple heuristic scoring
            query_words = set(query.lower().split())
            content_words = set(result.get('content', '').lower().split())
            
            # Boost score based on exact matches and semantic similarity
            exact_matches = len(query_words.intersection(content_words))
            total_query_words = len(query_words)
            
            rerank_boost = (exact_matches / total_query_words) * 0.2 if total_query_words > 0 else 0
            new_score = result["score"] + rerank_boost
            
            reranked_results.append({
                **result,
                "score": min(1.0, new_score),  # Cap at 1.0
                "rerank_boost": rerank_boost
            })
        
        return sorted(reranked_results, key=lambda x: x["score"], reverse=True)

    async def _diversity_rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rerank to promote diversity in results."""
        if len(results) <= 1:
            return results
        
        reranked = [results[0]]  # Start with highest scored
        remaining = results[1:]
        
        while remaining and len(reranked) < len(results):
            max_diversity_score = -1
            best_candidate = None
            
            for candidate in remaining:
                # Calculate diversity score (average distance from selected results)
                diversity_score = 0
                for selected in reranked:
                    # Simple content-based diversity
                    candidate_words = set(candidate.get('content', '').lower().split())
                    selected_words = set(selected.get('content', '').lower().split())
                    
                    jaccard_distance = 1 - (len(candidate_words.intersection(selected_words)) / 
                                          len(candidate_words.union(selected_words)))
                    diversity_score += jaccard_distance
                
                diversity_score /= len(reranked)
                
                # Combine with original relevance score
                combined_score = 0.7 * candidate["score"] + 0.3 * diversity_score
                
                if combined_score > max_diversity_score:
                    max_diversity_score = combined_score
                    best_candidate = candidate
            
            if best_candidate:
                reranked.append(best_candidate)
                remaining.remove(best_candidate)
        
        return reranked

    async def _temporal_rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rerank based on temporal relevance."""
        current_time = datetime.now()
        
        for result in results:
            # Extract temporal information from metadata
            chunk_metadata = result.get('metadata', {})
            doc_date = chunk_metadata.get('date')
            
            if doc_date:
                try:
                    doc_datetime = datetime.fromisoformat(doc_date)
                    days_old = (current_time - doc_datetime).days
                    
                    # Apply temporal decay (fresher content gets boost)
                    temporal_boost = max(0, 1 - (days_old / 365))  # Decay over a year
                    result["score"] = result["score"] * (1 + 0.1 * temporal_boost)
                except:
                    pass  # Skip temporal adjustment if date parsing fails
        
        return sorted(results, key=lambda x: x["score"], reverse=True)

    async def _relevance_feedback_rerank(self, query: str, results: List[Dict], feedback: Dict) -> List[Dict]:
        """Rerank based on relevance feedback."""
        relevant_docs = feedback.get('relevant_docs', [])
        irrelevant_docs = feedback.get('irrelevant_docs', [])
        
        for result in results:
            chunk_id = result["chunk_id"]
            
            if chunk_id in relevant_docs:
                result["score"] *= 1.2  # Boost relevant documents
            elif chunk_id in irrelevant_docs:
                result["score"] *= 0.8  # Penalize irrelevant documents
        
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def _calculate_score_change(self, original_results: List[Dict], reranked_results: List[Dict]) -> Dict:
        """Calculate the change in scores after reranking."""
        if not original_results or not reranked_results:
            return {"average_change": 0, "max_change": 0, "rank_changes": 0}
        
        # Create mappings for comparison
        original_ranks = {result["chunk_id"]: i for i, result in enumerate(original_results)}
        reranked_ranks = {result["chunk_id"]: i for i, result in enumerate(reranked_results)}
        
        rank_changes = 0
        score_changes = []
        
        for i, result in enumerate(reranked_results):
            chunk_id = result["chunk_id"]
            
            # Count rank changes
            if chunk_id in original_ranks and original_ranks[chunk_id] != i:
                rank_changes += 1
            
            # Track score changes
            original_result = next((r for r in original_results if r["chunk_id"] == chunk_id), None)
            if original_result:
                score_change = result["score"] - original_result["score"]
                score_changes.append(score_change)
        
        return {
            "average_score_change": np.mean(score_changes) if score_changes else 0,
            "max_score_change": np.max(np.abs(score_changes)) if score_changes else 0,
            "rank_changes": rank_changes
        }

    async def _prepare_context_for_generation(self, context_chunks: List[Dict], max_length: int, include_citations: bool) -> Dict:
        """Prepare context text for generation."""
        context_parts = []
        citations = {}
        current_length = 0
        
        for i, chunk in enumerate(context_chunks):
            chunk_content = chunk["content"]
            chunk_length = len(chunk_content.split())
            
            if current_length + chunk_length > max_length:
                break
            
            if include_citations:
                citation_marker = f"[{i+1}]"
                chunk_with_citation = f"{chunk_content} {citation_marker}"
                context_parts.append(chunk_with_citation)
                
                citations[i+1] = {
                    "chunk_id": chunk["chunk_id"],
                    "document_id": chunk["document_id"],
                    "source": chunk.get("metadata", {}).get("source", "Unknown")
                }
            else:
                context_parts.append(chunk_content)
            
            current_length += chunk_length
        
        context_text = "\n\n".join(context_parts)
        
        return {
            "context_text": context_text,
            "citations": citations,
            "chunks_used": len(context_parts),
            "total_tokens": current_length
        }

    def _build_generation_prompt(self, query: str, context: str, style: str) -> str:
        """Build prompt for response generation."""
        style_instructions = {
            "informative": "Provide a comprehensive and informative answer based on the given context.",
            "concise": "Provide a brief and direct answer based on the given context.",
            "detailed": "Provide a detailed explanation with examples and elaboration.",
            "conversational": "Respond in a conversational and friendly tone."
        }
        
        instruction = style_instructions.get(style, style_instructions["informative"])
        
        prompt = f"""Context: {context}

Question: {query}

{instruction} Use only the information provided in the context above.

Answer:"""
        
        return prompt

    async def _generate_llm_response(self, prompt: str, model_config: Dict) -> str:
        """Generate LLM response (simplified)."""
        # Simplified response generation - would use actual LLM API
        
        # Extract key information from prompt
        lines = prompt.split('\n')
        context_start = next((i for i, line in enumerate(lines) if line.startswith("Context:")), 0)
        question_start = next((i for i, line in enumerate(lines) if line.startswith("Question:")), 0)
        
        if context_start < question_start:
            context = '\n'.join(lines[context_start+1:question_start]).strip()
            question = lines[question_start].replace("Question:", "").strip()
        else:
            context = "No context provided"
            question = "No question provided"
        
        # Generate a simple response based on context
        if "define" in question.lower() or "what is" in question.lower():
            response = f"Based on the provided context, {question.lower().replace('what is', '').replace('define', '').strip()} refers to the information mentioned in the source material. "
        else:
            response = "Based on the provided context, "
        
        # Add some context information
        context_words = context.split()[:50]  # First 50 words
        response += " ".join(context_words)
        
        if len(context_words) == 50:
            response += "..."
        
        return response

    def _add_citations_to_response(self, response: str, citations: Dict) -> str:
        """Add citation markers to response."""
        # Simple citation addition - would be more sophisticated in practice
        for citation_num, citation_info in citations.items():
            marker = f"[{citation_num}]"
            if marker not in response:
                # Add citation at end of relevant sentences
                sentences = response.split('.')
                if len(sentences) > citation_num:
                    sentences[citation_num-1] += f" {marker}"
                    response = '.'.join(sentences)
        
        return response

    async def _validate_generated_response(self, response: str, context_chunks: List[Dict], query: str) -> Dict:
        """Validate the generated response."""
        validation = {
            "has_content": len(response.strip()) > 0,
            "answers_question": query.lower() in response.lower() or any(word in response.lower() for word in query.lower().split()),
            "uses_context": any(chunk["content"][:50].lower() in response.lower() for chunk in context_chunks[:3]),
            "appropriate_length": 50 <= len(response.split()) <= 500,
            "coherent": not any(repeat in response for repeat in ["the the", "and and", "is is"])
        }
        
        validation["overall_score"] = sum(validation.values()) / len(validation)
        
        return validation

    def _validate_params(self, operation: str, params: Dict[str, Any]) -> None:
        """Validate operation parameters."""
        required_params = {
            RAGOperation.INGEST_DOCUMENTS: ["kb_name", "documents"],
            RAGOperation.PROCESS_DOCUMENTS: ["kb_name"],
            RAGOperation.CREATE_CHUNKS: ["kb_name", "document_id"],
            RAGOperation.GENERATE_EMBEDDINGS: ["kb_name"],
            RAGOperation.INDEX_DOCUMENTS: ["kb_name"],
            RAGOperation.RETRIEVE_CONTEXT: ["kb_name", "query"],
            RAGOperation.RERANK_RESULTS: ["query", "results"],
            RAGOperation.GENERATE_RESPONSE: ["query", "context_chunks"],
            RAGOperation.FULL_RAG_PIPELINE: ["kb_name", "query"],
            RAGOperation.UPDATE_KNOWLEDGE_BASE: ["kb_name", "updates"],
            RAGOperation.DELETE_DOCUMENTS: ["kb_name", "document_ids"],
            RAGOperation.SEARCH_DOCUMENTS: ["kb_name", "search_query"],
            RAGOperation.EXTRACT_ENTITIES: ["kb_name"],
            RAGOperation.SUMMARIZE_DOCUMENTS: ["kb_name"],
            RAGOperation.FACT_CHECK: ["kb_name", "statements"],
            RAGOperation.CITATION_TRACKING: ["response_text", "context_chunks"],
            RAGOperation.CONTEXT_COMPRESSION: ["context_chunks", "query"],
            RAGOperation.MULTI_HOP_REASONING: ["kb_name", "query"],
            RAGOperation.ADAPTIVE_RETRIEVAL: ["kb_name", "query"],
            RAGOperation.QUERY_EXPANSION: ["query"],
            RAGOperation.QUERY_DECOMPOSITION: ["query"],
            RAGOperation.ANSWER_VALIDATION: ["answer", "context_chunks", "query"],
            RAGOperation.KNOWLEDGE_GRAPH_RAG: ["kb_name", "query"],
            RAGOperation.CONVERSATIONAL_RAG: ["kb_name", "current_query"],
            RAGOperation.MULTI_MODAL_RAG: ["kb_name", "query"],
            RAGOperation.RAG_EVALUATION: ["kb_name", "evaluation_dataset"],
            RAGOperation.PERFORMANCE_OPTIMIZATION: ["kb_name"],
        }

        if operation in required_params:
            for param in required_params[operation]:
                if param not in params:
                    raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            name="RAGNode",
            description="Retrieval Augmented Generation workflows for LLM applications",
            version="1.0.0",
            icon_path="🔍📚",
            auth_params=[
                NodeParameter(
                    name="openai_api_key",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="OpenAI API key for embeddings and generation"
                ),
                NodeParameter(
                    name="embedding_service_key",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="API key for embedding service"
                )
            ],
            parameters=[
                NodeParameter(
                    name="kb_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Name of the knowledge base"
                ),
                NodeParameter(
                    name="documents",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Array of documents to ingest"
                ),
                NodeParameter(
                    name="query",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Query for retrieval or generation"
                ),
                NodeParameter(
                    name="document_id",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="ID of specific document to process"
                ),
                NodeParameter(
                    name="chunk_size",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Size of text chunks for processing"
                ),
                NodeParameter(
                    name="chunk_overlap",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Overlap between consecutive chunks"
                ),
                NodeParameter(
                    name="chunking_strategy",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Strategy for text chunking: sliding_window, sentence_aware, semantic, paragraph"
                ),
                NodeParameter(
                    name="embedding_model",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Model for generating embeddings"
                ),
                NodeParameter(
                    name="retrieval_method",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Method for retrieval: dense, sparse, hybrid"
                ),
                NodeParameter(
                    name="top_k",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Number of top results to retrieve"
                ),
                NodeParameter(
                    name="rerank",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Whether to rerank retrieval results"
                ),
                NodeParameter(
                    name="response_style",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Style for response generation: informative, concise, detailed, conversational"
                ),
                NodeParameter(
                    name="include_citations",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Whether to include citations in response"
                ),
                NodeParameter(
                    name="max_context_length",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Maximum context length for generation"
                ),
                NodeParameter(
                    name="pipeline_config",
                    param_type=NodeParameterType.OBJECT,
                    required=False,
                    description="Configuration for RAG pipeline"
                ),
                NodeParameter(
                    name="context_chunks",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Context chunks for response generation"
                ),
                NodeParameter(
                    name="search_query",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Query for document search"
                ),
                NodeParameter(
                    name="search_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Type of search: semantic, keyword, hybrid"
                )
            ]
        )