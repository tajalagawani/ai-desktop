"""
EmbeddingSimilarityNode - Embedding similarity search for LLM workflows.
Handles text embeddings, similarity calculations, clustering, and semantic search operations.
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import asyncio
import hashlib
from collections import defaultdict
import math

from .base_node import BaseNode, NodeResult, NodeSchema, NodeParameter, NodeParameterType
from ..utils.validation import NodeValidationError

class EmbeddingSimilarityOperation:
    GENERATE_EMBEDDING = "generate_embedding"
    CALCULATE_SIMILARITY = "calculate_similarity"
    FIND_SIMILAR_TEXTS = "find_similar_texts"
    CLUSTER_EMBEDDINGS = "cluster_embeddings"
    SEMANTIC_SEARCH = "semantic_search"
    BATCH_SIMILARITY = "batch_similarity"
    EMBEDDING_ARITHMETIC = "embedding_arithmetic"
    DIMENSION_REDUCTION = "dimension_reduction"
    EMBEDDING_VISUALIZATION = "embedding_visualization"
    SIMILARITY_MATRIX = "similarity_matrix"
    FIND_OUTLIERS = "find_outliers"
    CENTROID_CALCULATION = "centroid_calculation"
    EMBEDDING_INTERPOLATION = "embedding_interpolation"
    NEAREST_NEIGHBORS = "nearest_neighbors"
    SIMILARITY_THRESHOLD = "similarity_threshold"
    EMBEDDING_STATISTICS = "embedding_statistics"
    COMPARE_EMBEDDINGS = "compare_embeddings"
    EMBEDDING_QUALITY_CHECK = "embedding_quality_check"
    SIMILARITY_RANKING = "similarity_ranking"
    EMBEDDING_CACHE = "embedding_cache"
    CROSS_MODAL_SIMILARITY = "cross_modal_similarity"
    EMBEDDING_FUSION = "embedding_fusion"
    SIMILARITY_AGGREGATION = "similarity_aggregation"
    EMBEDDING_NORMALIZATION = "embedding_normalization"

class EmbeddingSimilarityNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.name = "EmbeddingSimilarityNode"
        self.description = "Embedding similarity search for LLM workflows"
        self.version = "1.0.0"
        self.icon_path = "🔗"
        
        # Embedding storage and cache
        self.embedding_cache = {}
        self.embedding_metadata = {}
        self.similarity_cache = {}
        
        # Configuration
        self.default_similarity_metric = "cosine"
        self.cache_size_limit = 10000
        self.default_embedding_dimension = 384

    async def execute(self, operation: str, params: Dict[str, Any]) -> NodeResult:
        try:
            operation_map = {
                EmbeddingSimilarityOperation.GENERATE_EMBEDDING: self._generate_embedding,
                EmbeddingSimilarityOperation.CALCULATE_SIMILARITY: self._calculate_similarity,
                EmbeddingSimilarityOperation.FIND_SIMILAR_TEXTS: self._find_similar_texts,
                EmbeddingSimilarityOperation.CLUSTER_EMBEDDINGS: self._cluster_embeddings,
                EmbeddingSimilarityOperation.SEMANTIC_SEARCH: self._semantic_search,
                EmbeddingSimilarityOperation.BATCH_SIMILARITY: self._batch_similarity,
                EmbeddingSimilarityOperation.EMBEDDING_ARITHMETIC: self._embedding_arithmetic,
                EmbeddingSimilarityOperation.DIMENSION_REDUCTION: self._dimension_reduction,
                EmbeddingSimilarityOperation.EMBEDDING_VISUALIZATION: self._embedding_visualization,
                EmbeddingSimilarityOperation.SIMILARITY_MATRIX: self._similarity_matrix,
                EmbeddingSimilarityOperation.FIND_OUTLIERS: self._find_outliers,
                EmbeddingSimilarityOperation.CENTROID_CALCULATION: self._centroid_calculation,
                EmbeddingSimilarityOperation.EMBEDDING_INTERPOLATION: self._embedding_interpolation,
                EmbeddingSimilarityOperation.NEAREST_NEIGHBORS: self._nearest_neighbors,
                EmbeddingSimilarityOperation.SIMILARITY_THRESHOLD: self._similarity_threshold,
                EmbeddingSimilarityOperation.EMBEDDING_STATISTICS: self._embedding_statistics,
                EmbeddingSimilarityOperation.COMPARE_EMBEDDINGS: self._compare_embeddings,
                EmbeddingSimilarityOperation.EMBEDDING_QUALITY_CHECK: self._embedding_quality_check,
                EmbeddingSimilarityOperation.SIMILARITY_RANKING: self._similarity_ranking,
                EmbeddingSimilarityOperation.EMBEDDING_CACHE: self._embedding_cache,
                EmbeddingSimilarityOperation.CROSS_MODAL_SIMILARITY: self._cross_modal_similarity,
                EmbeddingSimilarityOperation.EMBEDDING_FUSION: self._embedding_fusion,
                EmbeddingSimilarityOperation.SIMILARITY_AGGREGATION: self._similarity_aggregation,
                EmbeddingSimilarityOperation.EMBEDDING_NORMALIZATION: self._embedding_normalization,
            }

            if operation not in operation_map:
                return self._create_error_result(f"Unknown operation: {operation}")

            self._validate_params(operation, params)
            result = await operation_map[operation](params)
            
            return self._create_success_result(result, f"Embedding similarity operation '{operation}' completed")
            
        except Exception as e:
            return self._create_error_result(f"Embedding similarity error: {str(e)}")

    async def _generate_embedding(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate embedding for text."""
        text = params["text"]
        model_type = params.get("model_type", "sentence_transformer")
        embedding_dimension = params.get("embedding_dimension", self.default_embedding_dimension)
        normalize = params.get("normalize", True)
        use_cache = params.get("use_cache", True)
        
        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(text, model_type)
            if cache_key in self.embedding_cache:
                cached_embedding = self.embedding_cache[cache_key]
                return {
                    "text": text,
                    "embedding": cached_embedding["embedding"],
                    "dimension": len(cached_embedding["embedding"]),
                    "model_type": model_type,
                    "from_cache": True,
                    "generated_at": cached_embedding["generated_at"]
                }
        
        # Generate new embedding
        if model_type == "sentence_transformer":
            embedding = self._generate_sentence_transformer_embedding(text, embedding_dimension)
        elif model_type == "openai":
            embedding = self._generate_openai_embedding(text, embedding_dimension)
        elif model_type == "tfidf":
            embedding = self._generate_tfidf_embedding(text, embedding_dimension)
        elif model_type == "word2vec":
            embedding = self._generate_word2vec_embedding(text, embedding_dimension)
        elif model_type == "random":
            embedding = self._generate_random_embedding(embedding_dimension)
        else:
            raise NodeValidationError(f"Unknown model type: {model_type}")
        
        # Normalize embedding if requested
        if normalize:
            embedding = self._normalize_embedding(embedding)
        
        # Cache embedding
        if use_cache:
            embedding_data = {
                "embedding": embedding,
                "generated_at": datetime.now().isoformat(),
                "model_type": model_type,
                "text_hash": hashlib.md5(text.encode()).hexdigest()
            }
            self.embedding_cache[cache_key] = embedding_data
            self._manage_cache_size()
        
        return {
            "text": text,
            "embedding": embedding,
            "dimension": len(embedding),
            "model_type": model_type,
            "normalized": normalize,
            "from_cache": False,
            "generated_at": datetime.now().isoformat()
        }

    async def _calculate_similarity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate similarity between two embeddings."""
        embedding1 = params["embedding1"]
        embedding2 = params["embedding2"]
        metric = params.get("metric", self.default_similarity_metric)
        
        # Validate embeddings
        if len(embedding1) != len(embedding2):
            raise NodeValidationError("Embeddings must have the same dimension")
        
        similarity = self._compute_similarity(embedding1, embedding2, metric)
        
        return {
            "similarity": similarity,
            "metric": metric,
            "embedding_dimension": len(embedding1),
            "calculated_at": datetime.now().isoformat()
        }

    async def _find_similar_texts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find texts similar to a query text."""
        query_text = params["query_text"]
        text_collection = params["text_collection"]
        top_k = params.get("top_k", 5)
        similarity_threshold = params.get("similarity_threshold", 0.0)
        model_type = params.get("model_type", "sentence_transformer")
        metric = params.get("metric", self.default_similarity_metric)
        
        # Generate query embedding
        query_embedding_result = await self._generate_embedding({
            "text": query_text,
            "model_type": model_type
        })
        query_embedding = query_embedding_result["embedding"]
        
        # Generate embeddings for text collection
        similarities = []
        
        for i, text in enumerate(text_collection):
            text_embedding_result = await self._generate_embedding({
                "text": text,
                "model_type": model_type
            })
            text_embedding = text_embedding_result["embedding"]
            
            similarity = self._compute_similarity(query_embedding, text_embedding, metric)
            
            if similarity >= similarity_threshold:
                similarities.append({
                    "text": text,
                    "similarity": similarity,
                    "index": i,
                    "embedding": text_embedding
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Return top k results
        top_results = similarities[:top_k]
        
        return {
            "query_text": query_text,
            "similar_texts": top_results,
            "total_candidates": len(text_collection),
            "filtered_candidates": len(similarities),
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "metric": metric
        }

    async def _cluster_embeddings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cluster embeddings using various clustering algorithms."""
        embeddings = params["embeddings"]
        texts = params.get("texts", [])
        algorithm = params.get("algorithm", "kmeans")
        num_clusters = params.get("num_clusters", 3)
        distance_threshold = params.get("distance_threshold", 0.5)
        
        if algorithm == "kmeans":
            clusters = self._kmeans_clustering(embeddings, num_clusters)
        elif algorithm == "hierarchical":
            clusters = self._hierarchical_clustering(embeddings, distance_threshold)
        elif algorithm == "dbscan":
            clusters = self._dbscan_clustering(embeddings, distance_threshold)
        else:
            raise NodeValidationError(f"Unknown clustering algorithm: {algorithm}")
        
        # Organize results
        cluster_results = []
        for cluster_id in set(clusters):
            cluster_members = []
            cluster_embeddings = []
            
            for i, cluster_assignment in enumerate(clusters):
                if cluster_assignment == cluster_id:
                    member_data = {"index": i, "embedding": embeddings[i]}
                    if i < len(texts):
                        member_data["text"] = texts[i]
                    cluster_members.append(member_data)
                    cluster_embeddings.append(embeddings[i])
            
            # Calculate cluster centroid
            if cluster_embeddings:
                centroid = self._calculate_centroid(cluster_embeddings)
                cluster_results.append({
                    "cluster_id": cluster_id,
                    "members": cluster_members,
                    "size": len(cluster_members),
                    "centroid": centroid,
                    "avg_intra_similarity": self._calculate_avg_intra_similarity(cluster_embeddings)
                })
        
        return {
            "clusters": cluster_results,
            "num_clusters": len(cluster_results),
            "algorithm": algorithm,
            "silhouette_score": self._calculate_silhouette_score(embeddings, clusters),
            "clustering_quality": self._assess_clustering_quality(cluster_results)
        }

    async def _semantic_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform semantic search across a document collection."""
        query = params["query"]
        documents = params["documents"]
        top_k = params.get("top_k", 10)
        search_mode = params.get("search_mode", "similarity")  # similarity, hybrid, rerank
        semantic_weight = params.get("semantic_weight", 0.7)
        model_type = params.get("model_type", "sentence_transformer")
        
        # Generate query embedding
        query_embedding_result = await self._generate_embedding({
            "text": query,
            "model_type": model_type
        })
        query_embedding = query_embedding_result["embedding"]
        
        # Process documents
        search_results = []
        
        for i, doc in enumerate(documents):
            doc_text = doc if isinstance(doc, str) else doc.get("text", "")
            doc_metadata = {} if isinstance(doc, str) else {k: v for k, v in doc.items() if k != "text"}
            
            # Generate document embedding
            doc_embedding_result = await self._generate_embedding({
                "text": doc_text,
                "model_type": model_type
            })
            doc_embedding = doc_embedding_result["embedding"]
            
            # Calculate semantic similarity
            semantic_score = self._compute_similarity(query_embedding, doc_embedding, "cosine")
            
            if search_mode == "similarity":
                final_score = semantic_score
            elif search_mode == "hybrid":
                # Combine with keyword matching score
                keyword_score = self._calculate_keyword_similarity(query, doc_text)
                final_score = semantic_weight * semantic_score + (1 - semantic_weight) * keyword_score
            elif search_mode == "rerank":
                # Initial semantic filtering, then reranking
                final_score = semantic_score
            else:
                final_score = semantic_score
            
            search_results.append({
                "document": doc,
                "text": doc_text,
                "metadata": doc_metadata,
                "index": i,
                "semantic_score": semantic_score,
                "final_score": final_score,
                "embedding": doc_embedding
            })
        
        # Sort by final score
        search_results.sort(key=lambda x: x["final_score"], reverse=True)
        
        # Apply reranking if specified
        if search_mode == "rerank" and len(search_results) > top_k:
            # Rerank top 2*top_k results using more sophisticated scoring
            rerank_candidates = search_results[:2*top_k]
            reranked = self._rerank_results(query, rerank_candidates)
            search_results = reranked + search_results[2*top_k:]
        
        return {
            "query": query,
            "results": search_results[:top_k],
            "total_documents": len(documents),
            "search_mode": search_mode,
            "top_k": top_k,
            "query_embedding_dimension": len(query_embedding)
        }

    async def _batch_similarity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate similarities for multiple embedding pairs efficiently."""
        embedding_pairs = params["embedding_pairs"]
        metric = params.get("metric", self.default_similarity_metric)
        parallel_processing = params.get("parallel_processing", True)
        
        similarities = []
        
        if parallel_processing:
            # Process in batches for efficiency
            batch_size = 100
            for i in range(0, len(embedding_pairs), batch_size):
                batch = embedding_pairs[i:i+batch_size]
                batch_results = await self._process_similarity_batch(batch, metric)
                similarities.extend(batch_results)
        else:
            # Sequential processing
            for pair in embedding_pairs:
                embedding1 = pair["embedding1"]
                embedding2 = pair["embedding2"]
                similarity = self._compute_similarity(embedding1, embedding2, metric)
                similarities.append({
                    "similarity": similarity,
                    "pair_index": len(similarities)
                })
        
        # Calculate statistics
        similarity_values = [s["similarity"] for s in similarities]
        statistics = {
            "mean": np.mean(similarity_values),
            "std": np.std(similarity_values),
            "min": np.min(similarity_values),
            "max": np.max(similarity_values),
            "median": np.median(similarity_values)
        }
        
        return {
            "similarities": similarities,
            "total_pairs": len(embedding_pairs),
            "metric": metric,
            "statistics": statistics,
            "processed_at": datetime.now().isoformat()
        }

    async def _embedding_arithmetic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform arithmetic operations on embeddings."""
        operation = params["operation"]  # add, subtract, multiply, average, weighted_average
        embeddings = params["embeddings"]
        weights = params.get("weights", [])
        normalize_result = params.get("normalize_result", True)
        
        if operation == "add":
            result_embedding = self._add_embeddings(embeddings)
        elif operation == "subtract":
            if len(embeddings) != 2:
                raise NodeValidationError("Subtract operation requires exactly 2 embeddings")
            result_embedding = self._subtract_embeddings(embeddings[0], embeddings[1])
        elif operation == "multiply":
            result_embedding = self._multiply_embeddings(embeddings)
        elif operation == "average":
            result_embedding = self._average_embeddings(embeddings)
        elif operation == "weighted_average":
            if not weights or len(weights) != len(embeddings):
                raise NodeValidationError("Weighted average requires weights for each embedding")
            result_embedding = self._weighted_average_embeddings(embeddings, weights)
        else:
            raise NodeValidationError(f"Unknown operation: {operation}")
        
        if normalize_result:
            result_embedding = self._normalize_embedding(result_embedding)
        
        return {
            "result_embedding": result_embedding,
            "operation": operation,
            "input_count": len(embeddings),
            "weights": weights if weights else None,
            "normalized": normalize_result,
            "dimension": len(result_embedding)
        }

    async def _dimension_reduction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce dimensionality of embeddings."""
        embeddings = params["embeddings"]
        target_dimension = params["target_dimension"]
        method = params.get("method", "pca")  # pca, random_projection, truncate
        preserve_variance = params.get("preserve_variance", 0.95)
        
        original_dimension = len(embeddings[0]) if embeddings else 0
        
        if target_dimension >= original_dimension:
            raise NodeValidationError("Target dimension must be smaller than original dimension")
        
        if method == "pca":
            reduced_embeddings = self._pca_reduction(embeddings, target_dimension, preserve_variance)
        elif method == "random_projection":
            reduced_embeddings = self._random_projection_reduction(embeddings, target_dimension)
        elif method == "truncate":
            reduced_embeddings = [emb[:target_dimension] for emb in embeddings]
        else:
            raise NodeValidationError(f"Unknown reduction method: {method}")
        
        # Calculate variance preservation
        variance_preserved = self._calculate_variance_preservation(embeddings, reduced_embeddings)
        
        return {
            "reduced_embeddings": reduced_embeddings,
            "original_dimension": original_dimension,
            "target_dimension": target_dimension,
            "method": method,
            "variance_preserved": variance_preserved,
            "compression_ratio": target_dimension / original_dimension
        }

    async def _embedding_visualization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization data for embeddings."""
        embeddings = params["embeddings"]
        labels = params.get("labels", [])
        method = params.get("method", "tsne")  # tsne, umap, pca
        dimensions = params.get("dimensions", 2)  # 2D or 3D
        perplexity = params.get("perplexity", 30)  # for t-SNE
        
        if method == "tsne":
            coordinates = self._tsne_visualization(embeddings, dimensions, perplexity)
        elif method == "umap":
            coordinates = self._umap_visualization(embeddings, dimensions)
        elif method == "pca":
            coordinates = self._pca_visualization(embeddings, dimensions)
        else:
            raise NodeValidationError(f"Unknown visualization method: {method}")
        
        # Prepare visualization data
        visualization_data = []
        for i, coord in enumerate(coordinates):
            point = {
                "id": i,
                "coordinates": coord,
                "embedding_index": i
            }
            if i < len(labels):
                point["label"] = labels[i]
            visualization_data.append(point)
        
        return {
            "visualization_data": visualization_data,
            "method": method,
            "dimensions": dimensions,
            "total_points": len(coordinates),
            "coordinate_bounds": self._calculate_coordinate_bounds(coordinates)
        }

    async def _similarity_matrix(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate similarity matrix for a collection of embeddings."""
        embeddings = params["embeddings"]
        metric = params.get("metric", self.default_similarity_metric)
        symmetric = params.get("symmetric", True)
        include_diagonal = params.get("include_diagonal", False)
        
        n = len(embeddings)
        similarity_matrix = []
        
        for i in range(n):
            row = []
            for j in range(n):
                if i == j and not include_diagonal:
                    similarity = 0.0
                elif symmetric and j < i:
                    # Use already calculated value
                    similarity = similarity_matrix[j][i]
                else:
                    similarity = self._compute_similarity(embeddings[i], embeddings[j], metric)
                row.append(similarity)
            similarity_matrix.append(row)
        
        # Calculate matrix statistics
        all_similarities = [sim for row in similarity_matrix for sim in row if sim != 0.0 or include_diagonal]
        statistics = {
            "mean": np.mean(all_similarities) if all_similarities else 0,
            "std": np.std(all_similarities) if all_similarities else 0,
            "min": np.min(all_similarities) if all_similarities else 0,
            "max": np.max(all_similarities) if all_similarities else 0
        }
        
        return {
            "similarity_matrix": similarity_matrix,
            "matrix_size": n,
            "metric": metric,
            "symmetric": symmetric,
            "statistics": statistics,
            "sparsity": self._calculate_matrix_sparsity(similarity_matrix)
        }

    async def _find_outliers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find outlier embeddings in a collection."""
        embeddings = params["embeddings"]
        texts = params.get("texts", [])
        method = params.get("method", "isolation_forest")  # isolation_forest, distance_based, statistical
        contamination = params.get("contamination", 0.1)
        distance_threshold = params.get("distance_threshold", 2.0)
        
        outlier_scores = []
        outlier_indices = []
        
        if method == "isolation_forest":
            scores, indices = self._isolation_forest_outliers(embeddings, contamination)
        elif method == "distance_based":
            scores, indices = self._distance_based_outliers(embeddings, distance_threshold)
        elif method == "statistical":
            scores, indices = self._statistical_outliers(embeddings, distance_threshold)
        else:
            raise NodeValidationError(f"Unknown outlier detection method: {method}")
        
        outlier_scores = scores
        outlier_indices = indices
        
        # Prepare outlier results
        outliers = []
        for i, idx in enumerate(outlier_indices):
            outlier_data = {
                "index": idx,
                "embedding": embeddings[idx],
                "outlier_score": outlier_scores[i]
            }
            if idx < len(texts):
                outlier_data["text"] = texts[idx]
            outliers.append(outlier_data)
        
        return {
            "outliers": outliers,
            "total_embeddings": len(embeddings),
            "outlier_count": len(outliers),
            "method": method,
            "outlier_ratio": len(outliers) / len(embeddings) if embeddings else 0
        }

    async def _centroid_calculation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate centroid of a group of embeddings."""
        embeddings = params["embeddings"]
        method = params.get("method", "mean")  # mean, median, weighted_mean
        weights = params.get("weights", [])
        
        if method == "mean":
            centroid = self._calculate_centroid(embeddings)
        elif method == "median":
            centroid = self._calculate_median_centroid(embeddings)
        elif method == "weighted_mean":
            if not weights or len(weights) != len(embeddings):
                raise NodeValidationError("Weighted mean requires weights for each embedding")
            centroid = self._calculate_weighted_centroid(embeddings, weights)
        else:
            raise NodeValidationError(f"Unknown centroid method: {method}")
        
        # Calculate distances from centroid
        distances = [self._euclidean_distance(emb, centroid) for emb in embeddings]
        
        return {
            "centroid": centroid,
            "method": method,
            "embedding_count": len(embeddings),
            "weights": weights if weights else None,
            "avg_distance_to_centroid": np.mean(distances),
            "max_distance_to_centroid": np.max(distances),
            "centroid_dimension": len(centroid)
        }

    async def _embedding_interpolation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Interpolate between embeddings."""
        start_embedding = params["start_embedding"]
        end_embedding = params["end_embedding"]
        steps = params.get("steps", 5)
        interpolation_method = params.get("interpolation_method", "linear")  # linear, spherical
        
        if len(start_embedding) != len(end_embedding):
            raise NodeValidationError("Embeddings must have the same dimension")
        
        if interpolation_method == "linear":
            interpolated = self._linear_interpolation(start_embedding, end_embedding, steps)
        elif interpolation_method == "spherical":
            interpolated = self._spherical_interpolation(start_embedding, end_embedding, steps)
        else:
            raise NodeValidationError(f"Unknown interpolation method: {interpolation_method}")
        
        # Calculate interpolation quality metrics
        interpolation_distances = []
        for i in range(1, len(interpolated)):
            dist = self._euclidean_distance(interpolated[i-1], interpolated[i])
            interpolation_distances.append(dist)
        
        return {
            "interpolated_embeddings": interpolated,
            "start_embedding": start_embedding,
            "end_embedding": end_embedding,
            "steps": steps,
            "method": interpolation_method,
            "step_distances": interpolation_distances,
            "smooth_interpolation": np.std(interpolation_distances) < 0.1
        }

    async def _nearest_neighbors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find k nearest neighbors for query embeddings."""
        query_embeddings = params["query_embeddings"]
        candidate_embeddings = params["candidate_embeddings"]
        k = params.get("k", 5)
        metric = params.get("metric", self.default_similarity_metric)
        exclude_self = params.get("exclude_self", True)
        
        # Ensure query_embeddings is a list
        if not isinstance(query_embeddings[0], list):
            query_embeddings = [query_embeddings]
        
        results = []
        
        for q_idx, query_emb in enumerate(query_embeddings):
            neighbors = []
            
            for c_idx, candidate_emb in enumerate(candidate_embeddings):
                # Skip self if requested and embeddings are the same
                if exclude_self and np.array_equal(query_emb, candidate_emb):
                    continue
                
                similarity = self._compute_similarity(query_emb, candidate_emb, metric)
                neighbors.append({
                    "index": c_idx,
                    "embedding": candidate_emb,
                    "similarity": similarity,
                    "distance": 1 - similarity if metric == "cosine" else abs(1 - similarity)
                })
            
            # Sort by similarity and take top k
            neighbors.sort(key=lambda x: x["similarity"], reverse=True)
            top_neighbors = neighbors[:k]
            
            results.append({
                "query_index": q_idx,
                "query_embedding": query_emb,
                "neighbors": top_neighbors,
                "neighbor_count": len(top_neighbors)
            })
        
        return {
            "nearest_neighbors": results,
            "k": k,
            "metric": metric,
            "total_queries": len(query_embeddings),
            "total_candidates": len(candidate_embeddings)
        }

    async def _similarity_threshold(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter embeddings based on similarity threshold."""
        query_embedding = params["query_embedding"]
        candidate_embeddings = params["candidate_embeddings"]
        threshold = params["threshold"]
        metric = params.get("metric", self.default_similarity_metric)
        above_threshold = params.get("above_threshold", True)
        
        filtered_results = []
        
        for i, candidate_emb in enumerate(candidate_embeddings):
            similarity = self._compute_similarity(query_embedding, candidate_emb, metric)
            
            passes_threshold = (similarity >= threshold) if above_threshold else (similarity < threshold)
            
            if passes_threshold:
                filtered_results.append({
                    "index": i,
                    "embedding": candidate_emb,
                    "similarity": similarity
                })
        
        return {
            "filtered_embeddings": filtered_results,
            "threshold": threshold,
            "above_threshold": above_threshold,
            "metric": metric,
            "total_candidates": len(candidate_embeddings),
            "filtered_count": len(filtered_results),
            "filter_ratio": len(filtered_results) / len(candidate_embeddings) if candidate_embeddings else 0
        }

    async def _embedding_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive statistics for embeddings."""
        embeddings = params["embeddings"]
        include_pairwise = params.get("include_pairwise", False)
        metric = params.get("metric", self.default_similarity_metric)
        
        if not embeddings:
            return {"error": "No embeddings provided"}
        
        # Basic statistics
        embedding_array = np.array(embeddings)
        stats = {
            "count": len(embeddings),
            "dimension": len(embeddings[0]),
            "mean": np.mean(embedding_array, axis=0).tolist(),
            "std": np.std(embedding_array, axis=0).tolist(),
            "min": np.min(embedding_array, axis=0).tolist(),
            "max": np.max(embedding_array, axis=0).tolist(),
            "norm_stats": {
                "mean_norm": np.mean([np.linalg.norm(emb) for emb in embeddings]),
                "std_norm": np.std([np.linalg.norm(emb) for emb in embeddings]),
                "min_norm": np.min([np.linalg.norm(emb) for emb in embeddings]),
                "max_norm": np.max([np.linalg.norm(emb) for emb in embeddings])
            }
        }
        
        # Centroid and spread
        centroid = self._calculate_centroid(embeddings)
        distances_to_centroid = [self._euclidean_distance(emb, centroid) for emb in embeddings]
        
        stats["centroid"] = centroid
        stats["spread"] = {
            "mean_distance_to_centroid": np.mean(distances_to_centroid),
            "std_distance_to_centroid": np.std(distances_to_centroid),
            "max_distance_to_centroid": np.max(distances_to_centroid)
        }
        
        # Pairwise statistics (optional, expensive for large sets)
        if include_pairwise and len(embeddings) <= 1000:  # Limit for performance
            pairwise_similarities = []
            for i in range(len(embeddings)):
                for j in range(i+1, len(embeddings)):
                    sim = self._compute_similarity(embeddings[i], embeddings[j], metric)
                    pairwise_similarities.append(sim)
            
            stats["pairwise"] = {
                "mean_similarity": np.mean(pairwise_similarities),
                "std_similarity": np.std(pairwise_similarities),
                "min_similarity": np.min(pairwise_similarities),
                "max_similarity": np.max(pairwise_similarities),
                "total_pairs": len(pairwise_similarities)
            }
        
        return {
            "statistics": stats,
            "analysis_timestamp": datetime.now().isoformat()
        }

    async def _compare_embeddings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two sets of embeddings comprehensively."""
        embeddings1 = params["embeddings1"]
        embeddings2 = params["embeddings2"]
        comparison_metrics = params.get("comparison_metrics", ["similarity", "distance", "alignment"])
        
        comparison_results = {}
        
        # Basic comparison
        comparison_results["basic"] = {
            "set1_count": len(embeddings1),
            "set2_count": len(embeddings2),
            "dimension_match": len(embeddings1[0]) == len(embeddings2[0]) if embeddings1 and embeddings2 else False
        }
        
        if "similarity" in comparison_metrics:
            # Average cross-set similarity
            cross_similarities = []
            for emb1 in embeddings1:
                for emb2 in embeddings2:
                    sim = self._compute_similarity(emb1, emb2, "cosine")
                    cross_similarities.append(sim)
            
            comparison_results["similarity"] = {
                "mean_cross_similarity": np.mean(cross_similarities) if cross_similarities else 0,
                "std_cross_similarity": np.std(cross_similarities) if cross_similarities else 0,
                "max_cross_similarity": np.max(cross_similarities) if cross_similarities else 0
            }
        
        if "distance" in comparison_metrics:
            # Centroid distance
            centroid1 = self._calculate_centroid(embeddings1)
            centroid2 = self._calculate_centroid(embeddings2)
            centroid_distance = self._euclidean_distance(centroid1, centroid2)
            
            comparison_results["distance"] = {
                "centroid_distance": centroid_distance,
                "centroid1": centroid1,
                "centroid2": centroid2
            }
        
        if "alignment" in comparison_metrics:
            # Distribution alignment (simplified)
            alignment_score = self._calculate_distribution_alignment(embeddings1, embeddings2)
            comparison_results["alignment"] = {
                "distribution_alignment": alignment_score
            }
        
        return {
            "comparison": comparison_results,
            "metrics_used": comparison_metrics
        }

    async def _embedding_quality_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check quality and validity of embeddings."""
        embeddings = params["embeddings"]
        quality_checks = params.get("quality_checks", ["dimension", "normalization", "diversity", "outliers"])
        
        quality_results = {}
        
        if "dimension" in quality_checks:
            # Check dimension consistency
            dimensions = [len(emb) for emb in embeddings]
            quality_results["dimension"] = {
                "consistent": len(set(dimensions)) == 1,
                "dimensions": list(set(dimensions)),
                "dimension_variance": np.var(dimensions)
            }
        
        if "normalization" in quality_checks:
            # Check if embeddings are normalized
            norms = [np.linalg.norm(emb) for emb in embeddings]
            quality_results["normalization"] = {
                "mean_norm": np.mean(norms),
                "std_norm": np.std(norms),
                "appears_normalized": abs(np.mean(norms) - 1.0) < 0.1 and np.std(norms) < 0.1
            }
        
        if "diversity" in quality_checks:
            # Check embedding diversity
            if len(embeddings) > 1:
                pairwise_similarities = []
                for i in range(min(100, len(embeddings))):  # Sample for performance
                    for j in range(i+1, min(100, len(embeddings))):
                        sim = self._compute_similarity(embeddings[i], embeddings[j], "cosine")
                        pairwise_similarities.append(sim)
                
                quality_results["diversity"] = {
                    "mean_pairwise_similarity": np.mean(pairwise_similarities),
                    "similarity_variance": np.var(pairwise_similarities),
                    "appears_diverse": np.mean(pairwise_similarities) < 0.8
                }
        
        if "outliers" in quality_checks:
            # Check for obvious outliers
            outlier_result = await self._find_outliers({
                "embeddings": embeddings,
                "method": "statistical",
                "contamination": 0.05
            })
            quality_results["outliers"] = {
                "outlier_count": outlier_result["outlier_count"],
                "outlier_ratio": outlier_result["outlier_ratio"]
            }
        
        # Overall quality score
        quality_score = self._calculate_overall_quality_score(quality_results)
        
        return {
            "quality_results": quality_results,
            "overall_quality_score": quality_score,
            "quality_grade": self._quality_score_to_grade(quality_score)
        }

    async def _similarity_ranking(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rank embeddings by similarity to multiple reference embeddings."""
        candidate_embeddings = params["candidate_embeddings"]
        reference_embeddings = params["reference_embeddings"]
        ranking_method = params.get("ranking_method", "average")  # average, max, min, weighted
        weights = params.get("weights", [])
        metric = params.get("metric", self.default_similarity_metric)
        
        rankings = []
        
        for i, candidate_emb in enumerate(candidate_embeddings):
            similarities_to_refs = []
            
            for ref_emb in reference_embeddings:
                sim = self._compute_similarity(candidate_emb, ref_emb, metric)
                similarities_to_refs.append(sim)
            
            # Calculate final ranking score
            if ranking_method == "average":
                ranking_score = np.mean(similarities_to_refs)
            elif ranking_method == "max":
                ranking_score = np.max(similarities_to_refs)
            elif ranking_method == "min":
                ranking_score = np.min(similarities_to_refs)
            elif ranking_method == "weighted":
                if not weights or len(weights) != len(reference_embeddings):
                    raise NodeValidationError("Weighted ranking requires weights for each reference embedding")
                ranking_score = np.average(similarities_to_refs, weights=weights)
            else:
                ranking_score = np.mean(similarities_to_refs)
            
            rankings.append({
                "candidate_index": i,
                "embedding": candidate_emb,
                "ranking_score": ranking_score,
                "similarities_to_references": similarities_to_refs
            })
        
        # Sort by ranking score
        rankings.sort(key=lambda x: x["ranking_score"], reverse=True)
        
        # Add ranking positions
        for i, ranking in enumerate(rankings):
            ranking["rank"] = i + 1
        
        return {
            "rankings": rankings,
            "total_candidates": len(candidate_embeddings),
            "reference_count": len(reference_embeddings),
            "ranking_method": ranking_method,
            "metric": metric
        }

    async def _embedding_cache(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Manage embedding cache operations."""
        operation = params["operation"]  # get, set, clear, stats, cleanup
        
        if operation == "get":
            cache_key = params["cache_key"]
            cached_data = self.embedding_cache.get(cache_key)
            return {
                "cache_key": cache_key,
                "found": cached_data is not None,
                "data": cached_data
            }
        
        elif operation == "set":
            cache_key = params["cache_key"]
            embedding_data = params["embedding_data"]
            self.embedding_cache[cache_key] = embedding_data
            return {
                "cache_key": cache_key,
                "stored": True,
                "cache_size": len(self.embedding_cache)
            }
        
        elif operation == "clear":
            cache_size_before = len(self.embedding_cache)
            self.embedding_cache.clear()
            return {
                "cleared": True,
                "entries_removed": cache_size_before
            }
        
        elif operation == "stats":
            return {
                "total_entries": len(self.embedding_cache),
                "cache_size_limit": self.cache_size_limit,
                "memory_usage_estimate": self._estimate_cache_memory_usage()
            }
        
        elif operation == "cleanup":
            cleaned_count = self._cleanup_cache()
            return {
                "cleanup_performed": True,
                "entries_removed": cleaned_count,
                "remaining_entries": len(self.embedding_cache)
            }
        
        else:
            raise NodeValidationError(f"Unknown cache operation: {operation}")

    async def _cross_modal_similarity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate similarity across different modalities."""
        embeddings1 = params["embeddings1"]
        embeddings2 = params["embeddings2"]
        modality1 = params["modality1"]  # text, image, audio, etc.
        modality2 = params["modality2"]
        alignment_method = params.get("alignment_method", "linear")  # linear, learned, canonical
        
        # This is a simplified cross-modal similarity
        # In practice, you'd need proper cross-modal alignment
        
        if alignment_method == "linear":
            aligned_similarities = self._linear_cross_modal_alignment(embeddings1, embeddings2)
        elif alignment_method == "canonical":
            aligned_similarities = self._canonical_correlation_alignment(embeddings1, embeddings2)
        else:
            # Direct similarity without alignment
            aligned_similarities = []
            for emb1 in embeddings1:
                similarities = []
                for emb2 in embeddings2:
                    sim = self._compute_similarity(emb1, emb2, "cosine")
                    similarities.append(sim)
                aligned_similarities.append(similarities)
        
        return {
            "cross_modal_similarities": aligned_similarities,
            "modality1": modality1,
            "modality2": modality2,
            "alignment_method": alignment_method,
            "embedding1_count": len(embeddings1),
            "embedding2_count": len(embeddings2)
        }

    async def _embedding_fusion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fuse multiple embeddings into a single representation."""
        embedding_sets = params["embedding_sets"]  # List of embedding lists
        fusion_method = params.get("fusion_method", "concatenation")  # concatenation, average, weighted_average, learned
        weights = params.get("weights", [])
        normalize_result = params.get("normalize_result", True)
        
        if fusion_method == "concatenation":
            fused_embeddings = self._concatenate_embeddings(embedding_sets)
        elif fusion_method == "average":
            fused_embeddings = self._average_embedding_sets(embedding_sets)
        elif fusion_method == "weighted_average":
            if not weights or len(weights) != len(embedding_sets):
                raise NodeValidationError("Weighted average requires weights for each embedding set")
            fused_embeddings = self._weighted_average_embedding_sets(embedding_sets, weights)
        else:
            raise NodeValidationError(f"Unknown fusion method: {fusion_method}")
        
        if normalize_result:
            fused_embeddings = [self._normalize_embedding(emb) for emb in fused_embeddings]
        
        return {
            "fused_embeddings": fused_embeddings,
            "fusion_method": fusion_method,
            "input_sets": len(embedding_sets),
            "output_dimension": len(fused_embeddings[0]) if fused_embeddings else 0,
            "normalized": normalize_result
        }

    async def _similarity_aggregation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate similarity scores using various methods."""
        similarity_scores = params["similarity_scores"]  # List of similarity values or matrices
        aggregation_method = params.get("aggregation_method", "mean")  # mean, max, min, weighted_mean, harmonic_mean
        weights = params.get("weights", [])
        
        if aggregation_method == "mean":
            aggregated = np.mean(similarity_scores, axis=0)
        elif aggregation_method == "max":
            aggregated = np.max(similarity_scores, axis=0)
        elif aggregation_method == "min":
            aggregated = np.min(similarity_scores, axis=0)
        elif aggregation_method == "weighted_mean":
            if not weights or len(weights) != len(similarity_scores):
                raise NodeValidationError("Weighted mean requires weights for each similarity score set")
            aggregated = np.average(similarity_scores, weights=weights, axis=0)
        elif aggregation_method == "harmonic_mean":
            aggregated = len(similarity_scores) / np.sum(1.0 / (np.array(similarity_scores) + 1e-8), axis=0)
        else:
            raise NodeValidationError(f"Unknown aggregation method: {aggregation_method}")
        
        return {
            "aggregated_similarities": aggregated.tolist() if hasattr(aggregated, 'tolist') else aggregated,
            "aggregation_method": aggregation_method,
            "input_count": len(similarity_scores),
            "weights": weights if weights else None
        }

    async def _embedding_normalization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize embeddings using various methods."""
        embeddings = params["embeddings"]
        normalization_method = params.get("normalization_method", "l2")  # l2, l1, unit, standardize
        
        normalized_embeddings = []
        
        for embedding in embeddings:
            if normalization_method == "l2":
                normalized = self._l2_normalize(embedding)
            elif normalization_method == "l1":
                normalized = self._l1_normalize(embedding)
            elif normalization_method == "unit":
                normalized = self._unit_normalize(embedding)
            elif normalization_method == "standardize":
                normalized = self._standardize_embedding(embedding, embeddings)
            else:
                raise NodeValidationError(f"Unknown normalization method: {normalization_method}")
            
            normalized_embeddings.append(normalized)
        
        # Calculate normalization statistics
        original_norms = [np.linalg.norm(emb) for emb in embeddings]
        normalized_norms = [np.linalg.norm(emb) for emb in normalized_embeddings]
        
        return {
            "normalized_embeddings": normalized_embeddings,
            "normalization_method": normalization_method,
            "original_norm_stats": {
                "mean": np.mean(original_norms),
                "std": np.std(original_norms),
                "min": np.min(original_norms),
                "max": np.max(original_norms)
            },
            "normalized_norm_stats": {
                "mean": np.mean(normalized_norms),
                "std": np.std(normalized_norms),
                "min": np.min(normalized_norms),
                "max": np.max(normalized_norms)
            }
        }

    # Helper methods (implementing core functionality)
    def _generate_cache_key(self, text, model_type):
        """Generate cache key for embedding."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{model_type}_{text_hash}"

    def _generate_sentence_transformer_embedding(self, text, dimension):
        """Generate sentence transformer embedding (simplified)."""
        # This is a placeholder - in practice you'd use sentence-transformers library
        # For now, return a random normalized embedding
        np.random.seed(hash(text) % 2**32)
        embedding = np.random.normal(0, 1, dimension)
        return self._normalize_embedding(embedding.tolist())

    def _generate_openai_embedding(self, text, dimension):
        """Generate OpenAI-style embedding (simplified)."""
        # Placeholder for OpenAI API call
        np.random.seed(hash(text) % 2**32)
        embedding = np.random.normal(0, 0.1, dimension)
        return self._normalize_embedding(embedding.tolist())

    def _generate_tfidf_embedding(self, text, dimension):
        """Generate TF-IDF based embedding."""
        # Simplified TF-IDF embedding
        words = text.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Convert to fixed dimension vector
        embedding = [0.0] * dimension
        for i, word in enumerate(words[:dimension]):
            embedding[i] = word_freq[word] / len(words)
        
        return embedding

    def _generate_word2vec_embedding(self, text, dimension):
        """Generate Word2Vec-style embedding."""
        # Simplified word2vec simulation
        words = text.lower().split()
        if not words:
            return [0.0] * dimension
        
        # Average of word embeddings (simplified)
        word_embeddings = []
        for word in words:
            np.random.seed(hash(word) % 2**32)
            word_emb = np.random.normal(0, 1, dimension)
            word_embeddings.append(word_emb)
        
        avg_embedding = np.mean(word_embeddings, axis=0)
        return self._normalize_embedding(avg_embedding.tolist())

    def _generate_random_embedding(self, dimension):
        """Generate random embedding for testing."""
        embedding = np.random.normal(0, 1, dimension)
        return self._normalize_embedding(embedding.tolist())

    def _normalize_embedding(self, embedding):
        """Normalize embedding to unit length."""
        embedding_array = np.array(embedding)
        norm = np.linalg.norm(embedding_array)
        if norm == 0:
            return embedding
        return (embedding_array / norm).tolist()

    def _l2_normalize(self, embedding):
        """L2 normalization."""
        return self._normalize_embedding(embedding)

    def _l1_normalize(self, embedding):
        """L1 normalization."""
        embedding_array = np.array(embedding)
        norm = np.sum(np.abs(embedding_array))
        if norm == 0:
            return embedding
        return (embedding_array / norm).tolist()

    def _unit_normalize(self, embedding):
        """Unit normalization (same as L2)."""
        return self._normalize_embedding(embedding)

    def _standardize_embedding(self, embedding, all_embeddings):
        """Standardize embedding using mean and std of all embeddings."""
        all_embeddings_array = np.array(all_embeddings)
        mean = np.mean(all_embeddings_array, axis=0)
        std = np.std(all_embeddings_array, axis=0)
        
        embedding_array = np.array(embedding)
        standardized = (embedding_array - mean) / (std + 1e-8)
        return standardized.tolist()

    def _compute_similarity(self, embedding1, embedding2, metric):
        """Compute similarity between two embeddings."""
        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)
        
        if metric == "cosine":
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
        
        elif metric == "euclidean":
            distance = np.linalg.norm(emb1 - emb2)
            return 1 / (1 + distance)  # Convert distance to similarity
        
        elif metric == "manhattan":
            distance = np.sum(np.abs(emb1 - emb2))
            return 1 / (1 + distance)
        
        elif metric == "dot_product":
            return np.dot(emb1, emb2)
        
        else:
            return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    def _euclidean_distance(self, embedding1, embedding2):
        """Calculate Euclidean distance."""
        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)
        return np.linalg.norm(emb1 - emb2)

    def _calculate_keyword_similarity(self, query, text):
        """Calculate keyword-based similarity."""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        intersection = query_words.intersection(text_words)
        union = query_words.union(text_words)
        
        return len(intersection) / len(union) if union else 0

    def _rerank_results(self, query, results):
        """Rerank results using more sophisticated scoring."""
        # Simplified reranking - could implement more complex methods
        for result in results:
            # Boost score based on text length similarity
            query_len = len(query.split())
            text_len = len(result["text"].split())
            length_similarity = 1 - abs(query_len - text_len) / max(query_len, text_len, 1)
            
            # Combine with original score
            result["final_score"] = 0.8 * result["semantic_score"] + 0.2 * length_similarity
        
        results.sort(key=lambda x: x["final_score"], reverse=True)
        return results

    async def _process_similarity_batch(self, batch, metric):
        """Process a batch of similarity calculations."""
        results = []
        for pair in batch:
            embedding1 = pair["embedding1"]
            embedding2 = pair["embedding2"]
            similarity = self._compute_similarity(embedding1, embedding2, metric)
            results.append({
                "similarity": similarity,
                "pair_index": len(results)
            })
        return results

    def _add_embeddings(self, embeddings):
        """Add multiple embeddings element-wise."""
        result = np.zeros(len(embeddings[0]))
        for embedding in embeddings:
            result += np.array(embedding)
        return result.tolist()

    def _subtract_embeddings(self, embedding1, embedding2):
        """Subtract embedding2 from embedding1."""
        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)
        return (emb1 - emb2).tolist()

    def _multiply_embeddings(self, embeddings):
        """Multiply embeddings element-wise."""
        result = np.ones(len(embeddings[0]))
        for embedding in embeddings:
            result *= np.array(embedding)
        return result.tolist()

    def _average_embeddings(self, embeddings):
        """Calculate average of embeddings."""
        if not embeddings:
            return []
        return np.mean(embeddings, axis=0).tolist()

    def _weighted_average_embeddings(self, embeddings, weights):
        """Calculate weighted average of embeddings."""
        weighted_sum = np.zeros(len(embeddings[0]))
        total_weight = sum(weights)
        
        for embedding, weight in zip(embeddings, weights):
            weighted_sum += weight * np.array(embedding)
        
        return (weighted_sum / total_weight).tolist()

    def _calculate_centroid(self, embeddings):
        """Calculate centroid of embeddings."""
        return self._average_embeddings(embeddings)

    def _calculate_median_centroid(self, embeddings):
        """Calculate median centroid."""
        return np.median(embeddings, axis=0).tolist()

    def _calculate_weighted_centroid(self, embeddings, weights):
        """Calculate weighted centroid."""
        return self._weighted_average_embeddings(embeddings, weights)

    def _linear_interpolation(self, start_embedding, end_embedding, steps):
        """Linear interpolation between embeddings."""
        start = np.array(start_embedding)
        end = np.array(end_embedding)
        
        interpolated = []
        for i in range(steps + 1):
            t = i / steps
            interpolated_emb = (1 - t) * start + t * end
            interpolated.append(interpolated_emb.tolist())
        
        return interpolated

    def _spherical_interpolation(self, start_embedding, end_embedding, steps):
        """Spherical interpolation between normalized embeddings."""
        start = np.array(self._normalize_embedding(start_embedding))
        end = np.array(self._normalize_embedding(end_embedding))
        
        # Calculate angle between vectors
        dot_product = np.clip(np.dot(start, end), -1.0, 1.0)
        omega = np.arccos(dot_product)
        
        if omega == 0:
            # Vectors are identical, return linear interpolation
            return self._linear_interpolation(start_embedding, end_embedding, steps)
        
        sin_omega = np.sin(omega)
        interpolated = []
        
        for i in range(steps + 1):
            t = i / steps
            a = np.sin((1 - t) * omega) / sin_omega
            b = np.sin(t * omega) / sin_omega
            interpolated_emb = a * start + b * end
            interpolated.append(interpolated_emb.tolist())
        
        return interpolated

    def _kmeans_clustering(self, embeddings, num_clusters):
        """Simple k-means clustering."""
        # Simplified k-means implementation
        embeddings_array = np.array(embeddings)
        n_samples = len(embeddings)
        
        # Random initialization
        np.random.seed(42)
        centroids = embeddings_array[np.random.choice(n_samples, num_clusters, replace=False)]
        
        for _ in range(100):  # Max iterations
            # Assign points to clusters
            distances = np.linalg.norm(embeddings_array[:, np.newaxis] - centroids, axis=2)
            clusters = np.argmin(distances, axis=1)
            
            # Update centroids
            new_centroids = np.array([embeddings_array[clusters == i].mean(axis=0) 
                                    for i in range(num_clusters)])
            
            if np.allclose(centroids, new_centroids):
                break
            centroids = new_centroids
        
        return clusters.tolist()

    def _hierarchical_clustering(self, embeddings, distance_threshold):
        """Simple hierarchical clustering."""
        # Simplified implementation
        n_samples = len(embeddings)
        clusters = list(range(n_samples))  # Each point starts as its own cluster
        
        # This is a very simplified version
        # In practice, you'd use scipy.cluster.hierarchy
        return clusters

    def _dbscan_clustering(self, embeddings, distance_threshold):
        """Simple DBSCAN clustering."""
        # Simplified implementation
        # In practice, you'd use sklearn.cluster.DBSCAN
        clusters = [0] * len(embeddings)  # All points in cluster 0 for simplicity
        return clusters

    def _calculate_avg_intra_similarity(self, cluster_embeddings):
        """Calculate average intra-cluster similarity."""
        if len(cluster_embeddings) < 2:
            return 1.0
        
        similarities = []
        for i in range(len(cluster_embeddings)):
            for j in range(i + 1, len(cluster_embeddings)):
                sim = self._compute_similarity(cluster_embeddings[i], cluster_embeddings[j], "cosine")
                similarities.append(sim)
        
        return np.mean(similarities) if similarities else 1.0

    def _calculate_silhouette_score(self, embeddings, clusters):
        """Calculate simplified silhouette score."""
        # This is a placeholder - proper implementation would be more complex
        return 0.5  # Dummy value

    def _assess_clustering_quality(self, cluster_results):
        """Assess clustering quality."""
        if not cluster_results:
            return {"quality": "poor", "score": 0.0}
        
        # Simple quality assessment based on cluster sizes and similarities
        avg_similarity = np.mean([cluster["avg_intra_similarity"] for cluster in cluster_results])
        size_variance = np.var([cluster["size"] for cluster in cluster_results])
        
        quality_score = avg_similarity * (1 / (1 + size_variance))
        
        if quality_score > 0.7:
            quality = "good"
        elif quality_score > 0.5:
            quality = "fair"
        else:
            quality = "poor"
        
        return {"quality": quality, "score": quality_score}

    def _pca_reduction(self, embeddings, target_dimension, preserve_variance):
        """PCA dimensionality reduction."""
        # Simplified PCA implementation
        embeddings_array = np.array(embeddings)
        
        # Center the data
        mean = np.mean(embeddings_array, axis=0)
        centered = embeddings_array - mean
        
        # SVD
        U, s, Vt = np.linalg.svd(centered, full_matrices=False)
        
        # Take top components
        reduced = U[:, :target_dimension] @ np.diag(s[:target_dimension])
        
        return reduced.tolist()

    def _random_projection_reduction(self, embeddings, target_dimension):
        """Random projection dimensionality reduction."""
        embeddings_array = np.array(embeddings)
        original_dimension = embeddings_array.shape[1]
        
        # Random projection matrix
        np.random.seed(42)
        projection_matrix = np.random.normal(0, 1, (original_dimension, target_dimension))
        projection_matrix = projection_matrix / np.sqrt(target_dimension)
        
        reduced = embeddings_array @ projection_matrix
        return reduced.tolist()

    def _calculate_variance_preservation(self, original_embeddings, reduced_embeddings):
        """Calculate how much variance is preserved after reduction."""
        # Simplified calculation
        original_var = np.var(original_embeddings)
        reduced_var = np.var(reduced_embeddings)
        return reduced_var / original_var if original_var > 0 else 0

    def _tsne_visualization(self, embeddings, dimensions, perplexity):
        """t-SNE visualization (simplified)."""
        # This is a placeholder - in practice you'd use sklearn.manifold.TSNE
        embeddings_array = np.array(embeddings)
        n_samples = len(embeddings_array)
        
        # Random initialization for demo
        np.random.seed(42)
        coordinates = np.random.normal(0, 1, (n_samples, dimensions))
        
        return coordinates.tolist()

    def _umap_visualization(self, embeddings, dimensions):
        """UMAP visualization (simplified)."""
        # Placeholder - in practice you'd use umap-learn
        return self._tsne_visualization(embeddings, dimensions, 30)

    def _pca_visualization(self, embeddings, dimensions):
        """PCA visualization."""
        return self._pca_reduction(embeddings, dimensions, 0.95)

    def _calculate_coordinate_bounds(self, coordinates):
        """Calculate bounds for visualization coordinates."""
        coords_array = np.array(coordinates)
        return {
            "min": coords_array.min(axis=0).tolist(),
            "max": coords_array.max(axis=0).tolist(),
            "range": (coords_array.max(axis=0) - coords_array.min(axis=0)).tolist()
        }

    def _calculate_matrix_sparsity(self, similarity_matrix):
        """Calculate sparsity of similarity matrix."""
        matrix_array = np.array(similarity_matrix)
        total_elements = matrix_array.size
        zero_elements = np.count_nonzero(matrix_array == 0)
        return zero_elements / total_elements

    def _isolation_forest_outliers(self, embeddings, contamination):
        """Isolation forest outlier detection (simplified)."""
        # Simplified implementation - in practice use sklearn.ensemble.IsolationForest
        n_samples = len(embeddings)
        n_outliers = max(1, int(contamination * n_samples))
        
        # Random outlier detection for demo
        np.random.seed(42)
        outlier_indices = np.random.choice(n_samples, n_outliers, replace=False)
        scores = np.random.random(n_outliers)
        
        return scores.tolist(), outlier_indices.tolist()

    def _distance_based_outliers(self, embeddings, distance_threshold):
        """Distance-based outlier detection."""
        centroid = self._calculate_centroid(embeddings)
        outliers = []
        scores = []
        
        for i, embedding in enumerate(embeddings):
            distance = self._euclidean_distance(embedding, centroid)
            if distance > distance_threshold:
                outliers.append(i)
                scores.append(distance)
        
        return scores, outliers

    def _statistical_outliers(self, embeddings, threshold):
        """Statistical outlier detection."""
        # Use z-score approach
        embeddings_array = np.array(embeddings)
        mean = np.mean(embeddings_array, axis=0)
        std = np.std(embeddings_array, axis=0)
        
        outliers = []
        scores = []
        
        for i, embedding in enumerate(embeddings):
            z_scores = np.abs((np.array(embedding) - mean) / (std + 1e-8))
            max_z_score = np.max(z_scores)
            
            if max_z_score > threshold:
                outliers.append(i)
                scores.append(max_z_score)
        
        return scores, outliers

    def _linear_cross_modal_alignment(self, embeddings1, embeddings2):
        """Linear cross-modal alignment."""
        # Simplified cross-modal similarity
        similarities = []
        for emb1 in embeddings1:
            row = []
            for emb2 in embeddings2:
                # Pad shorter embedding with zeros
                min_len = min(len(emb1), len(emb2))
                sim = self._compute_similarity(emb1[:min_len], emb2[:min_len], "cosine")
                row.append(sim)
            similarities.append(row)
        return similarities

    def _canonical_correlation_alignment(self, embeddings1, embeddings2):
        """Canonical correlation analysis alignment."""
        # Simplified CCA - in practice you'd use proper CCA implementation
        return self._linear_cross_modal_alignment(embeddings1, embeddings2)

    def _concatenate_embeddings(self, embedding_sets):
        """Concatenate multiple embedding sets."""
        if not embedding_sets:
            return []
        
        fused = []
        for i in range(len(embedding_sets[0])):
            concatenated = []
            for embedding_set in embedding_sets:
                if i < len(embedding_set):
                    concatenated.extend(embedding_set[i])
            fused.append(concatenated)
        
        return fused

    def _average_embedding_sets(self, embedding_sets):
        """Average multiple embedding sets."""
        if not embedding_sets:
            return []
        
        # Ensure all sets have same length
        min_len = min(len(es) for es in embedding_sets)
        fused = []
        
        for i in range(min_len):
            embeddings_at_i = [embedding_set[i] for embedding_set in embedding_sets]
            averaged = self._average_embeddings(embeddings_at_i)
            fused.append(averaged)
        
        return fused

    def _weighted_average_embedding_sets(self, embedding_sets, weights):
        """Weighted average of multiple embedding sets."""
        if not embedding_sets:
            return []
        
        min_len = min(len(es) for es in embedding_sets)
        fused = []
        
        for i in range(min_len):
            embeddings_at_i = [embedding_set[i] for embedding_set in embedding_sets]
            weighted_avg = self._weighted_average_embeddings(embeddings_at_i, weights)
            fused.append(weighted_avg)
        
        return fused

    def _calculate_distribution_alignment(self, embeddings1, embeddings2):
        """Calculate distribution alignment between two embedding sets."""
        # Simplified distribution comparison
        mean1 = np.mean(embeddings1, axis=0)
        mean2 = np.mean(embeddings2, axis=0)
        
        # Cosine similarity between means
        alignment = self._compute_similarity(mean1.tolist(), mean2.tolist(), "cosine")
        return alignment

    def _calculate_overall_quality_score(self, quality_results):
        """Calculate overall quality score from individual checks."""
        scores = []
        
        if "dimension" in quality_results:
            scores.append(1.0 if quality_results["dimension"]["consistent"] else 0.0)
        
        if "normalization" in quality_results:
            scores.append(1.0 if quality_results["normalization"]["appears_normalized"] else 0.5)
        
        if "diversity" in quality_results:
            scores.append(1.0 if quality_results["diversity"]["appears_diverse"] else 0.3)
        
        if "outliers" in quality_results:
            outlier_ratio = quality_results["outliers"]["outlier_ratio"]
            outlier_score = max(0, 1.0 - outlier_ratio * 2)  # Penalize high outlier ratios
            scores.append(outlier_score)
        
        return np.mean(scores) if scores else 0.5

    def _quality_score_to_grade(self, score):
        """Convert quality score to letter grade."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    def _manage_cache_size(self):
        """Manage cache size to stay within limits."""
        while len(self.embedding_cache) > self.cache_size_limit:
            # Remove oldest entries (simplified LRU)
            oldest_key = min(self.embedding_cache.keys(), 
                           key=lambda k: self.embedding_cache[k]["generated_at"])
            del self.embedding_cache[oldest_key]

    def _estimate_cache_memory_usage(self):
        """Estimate memory usage of cache."""
        total_size = 0
        for cache_entry in self.embedding_cache.values():
            embedding_size = len(cache_entry["embedding"]) * 8  # 8 bytes per float
            total_size += embedding_size
        return total_size

    def _cleanup_cache(self):
        """Cleanup old cache entries."""
        cutoff_time = datetime.now().timestamp() - 3600  # 1 hour ago
        keys_to_remove = []
        
        for key, cache_entry in self.embedding_cache.items():
            entry_time = datetime.fromisoformat(cache_entry["generated_at"]).timestamp()
            if entry_time < cutoff_time:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.embedding_cache[key]
        
        return len(keys_to_remove)

    def _validate_params(self, operation: str, params: Dict[str, Any]) -> None:
        """Validate operation parameters."""
        required_params = {
            EmbeddingSimilarityOperation.GENERATE_EMBEDDING: ["text"],
            EmbeddingSimilarityOperation.CALCULATE_SIMILARITY: ["embedding1", "embedding2"],
            EmbeddingSimilarityOperation.FIND_SIMILAR_TEXTS: ["query_text", "text_collection"],
            EmbeddingSimilarityOperation.CLUSTER_EMBEDDINGS: ["embeddings"],
            EmbeddingSimilarityOperation.SEMANTIC_SEARCH: ["query", "documents"],
            EmbeddingSimilarityOperation.BATCH_SIMILARITY: ["embedding_pairs"],
            EmbeddingSimilarityOperation.EMBEDDING_ARITHMETIC: ["operation", "embeddings"],
            EmbeddingSimilarityOperation.DIMENSION_REDUCTION: ["embeddings", "target_dimension"],
            EmbeddingSimilarityOperation.EMBEDDING_VISUALIZATION: ["embeddings"],
            EmbeddingSimilarityOperation.SIMILARITY_MATRIX: ["embeddings"],
            EmbeddingSimilarityOperation.FIND_OUTLIERS: ["embeddings"],
            EmbeddingSimilarityOperation.CENTROID_CALCULATION: ["embeddings"],
            EmbeddingSimilarityOperation.EMBEDDING_INTERPOLATION: ["start_embedding", "end_embedding"],
            EmbeddingSimilarityOperation.NEAREST_NEIGHBORS: ["query_embeddings", "candidate_embeddings"],
            EmbeddingSimilarityOperation.SIMILARITY_THRESHOLD: ["query_embedding", "candidate_embeddings", "threshold"],
            EmbeddingSimilarityOperation.EMBEDDING_STATISTICS: ["embeddings"],
            EmbeddingSimilarityOperation.COMPARE_EMBEDDINGS: ["embeddings1", "embeddings2"],
            EmbeddingSimilarityOperation.EMBEDDING_QUALITY_CHECK: ["embeddings"],
            EmbeddingSimilarityOperation.SIMILARITY_RANKING: ["candidate_embeddings", "reference_embeddings"],
            EmbeddingSimilarityOperation.EMBEDDING_CACHE: ["operation"],
            EmbeddingSimilarityOperation.CROSS_MODAL_SIMILARITY: ["embeddings1", "embeddings2", "modality1", "modality2"],
            EmbeddingSimilarityOperation.EMBEDDING_FUSION: ["embedding_sets"],
            EmbeddingSimilarityOperation.SIMILARITY_AGGREGATION: ["similarity_scores"],
            EmbeddingSimilarityOperation.EMBEDDING_NORMALIZATION: ["embeddings"],
        }

        if operation in required_params:
            for param in required_params[operation]:
                if param not in params:
                    raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            name="EmbeddingSimilarityNode",
            description="Embedding similarity search for LLM workflows",
            version="1.0.0",
            icon_path="🔗",
            auth_params=[],
            parameters=[
                NodeParameter(
                    name="text",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Text to generate embedding for"
                ),
                NodeParameter(
                    name="embedding1",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="First embedding for similarity calculation"
                ),
                NodeParameter(
                    name="embedding2",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Second embedding for similarity calculation"
                ),
                NodeParameter(
                    name="embeddings",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Array of embeddings for processing"
                ),
                NodeParameter(
                    name="model_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Type of embedding model: sentence_transformer, openai, tfidf, word2vec, random"
                ),
                NodeParameter(
                    name="metric",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Similarity metric: cosine, euclidean, manhattan, dot_product"
                ),
                NodeParameter(
                    name="query_text",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Query text for similarity search"
                ),
                NodeParameter(
                    name="text_collection",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Collection of texts to search against"
                ),
                NodeParameter(
                    name="top_k",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Number of top results to return"
                ),
                NodeParameter(
                    name="similarity_threshold",
                    param_type=NodeParameterType.FLOAT,
                    required=False,
                    description="Minimum similarity threshold"
                ),
                NodeParameter(
                    name="algorithm",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Clustering algorithm: kmeans, hierarchical, dbscan"
                ),
                NodeParameter(
                    name="num_clusters",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Number of clusters for clustering algorithms"
                ),
                NodeParameter(
                    name="query",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Search query for semantic search"
                ),
                NodeParameter(
                    name="documents",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Document collection for semantic search"
                ),
                NodeParameter(
                    name="operation",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Arithmetic operation: add, subtract, multiply, average, weighted_average"
                ),
                NodeParameter(
                    name="target_dimension",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Target dimension for dimensionality reduction"
                ),
                NodeParameter(
                    name="method",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Method for various operations (clustering, reduction, etc.)"
                ),
                NodeParameter(
                    name="weights",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Weights for weighted operations"
                ),
                NodeParameter(
                    name="normalize",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Whether to normalize embeddings"
                ),
                NodeParameter(
                    name="embedding_dimension",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Dimension of generated embeddings"
                ),
                NodeParameter(
                    name="use_cache",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Whether to use embedding cache"
                ),
                NodeParameter(
                    name="steps",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Number of interpolation steps"
                ),
                NodeParameter(
                    name="k",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Number of nearest neighbors"
                ),
                NodeParameter(
                    name="threshold",
                    param_type=NodeParameterType.FLOAT,
                    required=False,
                    description="Threshold value for filtering"
                )
            ]
        )