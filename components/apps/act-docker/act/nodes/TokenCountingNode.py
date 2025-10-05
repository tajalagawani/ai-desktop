import asyncio
import re
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from act_workflow.act.node_schema import NodeSchema, NodeParameter, NodeParameterType
from act_workflow.act.nodes.base_node import BaseNode

class TokenCountingOperation:
    """Token counting and estimation operations."""
    
    # Basic token counting
    COUNT_TOKENS = "count_tokens"
    ESTIMATE_TOKENS = "estimate_tokens"
    COUNT_TOKENS_BATCH = "count_tokens_batch"
    
    # Cost estimation
    ESTIMATE_COST = "estimate_cost"
    CALCULATE_BATCH_COST = "calculate_batch_cost"
    COMPARE_MODEL_COSTS = "compare_model_costs"
    
    # Token analysis
    ANALYZE_TOKEN_DISTRIBUTION = "analyze_token_distribution"
    GET_TOKEN_BREAKDOWN = "get_token_breakdown"
    VALIDATE_TOKEN_LIMITS = "validate_token_limits"
    
    # Optimization
    OPTIMIZE_FOR_TOKENS = "optimize_for_tokens"
    TRUNCATE_TO_LIMIT = "truncate_to_limit"
    SPLIT_BY_TOKEN_LIMIT = "split_by_token_limit"
    
    # Model-specific
    COUNT_BY_MODEL = "count_by_model"
    GET_MODEL_LIMITS = "get_model_limits"
    CHECK_CONTEXT_WINDOW = "check_context_window"

@dataclass
class TokenResult:
    """Result of token counting operation."""
    token_count: int
    character_count: int
    word_count: int
    estimated_cost: Optional[float] = None
    model_used: Optional[str] = None
    breakdown: Optional[Dict[str, int]] = None

@dataclass
class ModelInfo:
    """Model information for token counting."""
    name: str
    max_tokens: int
    input_cost_per_1k: float
    output_cost_per_1k: float
    context_window: int

class TokenCountingNode(BaseNode):
    def __init__(self):
        schema = NodeSchema(
            name="TokenCounting",
            version="1.0.0", 
            description="Advanced token counting, estimation, and cost analysis for LLM operations",
            auth_params=[
                NodeParameter(
                    name="openai_api_key",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="OpenAI API key for accurate token counting (optional)"
                )
            ],
            parameters=[
                NodeParameter(
                    name="operation",
                    param_type=NodeParameterType.SELECT,
                    required=True,
                    description="Token operation to perform",
                    options=[
                        {"label": "Count Tokens", "value": "count_tokens"},
                        {"label": "Estimate Tokens", "value": "estimate_tokens"},
                        {"label": "Count Tokens Batch", "value": "count_tokens_batch"},
                        {"label": "Estimate Cost", "value": "estimate_cost"},
                        {"label": "Calculate Batch Cost", "value": "calculate_batch_cost"},
                        {"label": "Compare Model Costs", "value": "compare_model_costs"},
                        {"label": "Analyze Token Distribution", "value": "analyze_token_distribution"},
                        {"label": "Get Token Breakdown", "value": "get_token_breakdown"},
                        {"label": "Validate Token Limits", "value": "validate_token_limits"},
                        {"label": "Optimize for Tokens", "value": "optimize_for_tokens"},
                        {"label": "Truncate to Limit", "value": "truncate_to_limit"},
                        {"label": "Split by Token Limit", "value": "split_by_token_limit"},
                        {"label": "Count by Model", "value": "count_by_model"},
                        {"label": "Get Model Limits", "value": "get_model_limits"},
                        {"label": "Check Context Window", "value": "check_context_window"}
                    ]
                ),
                NodeParameter(
                    name="text",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Text to analyze"
                ),
                NodeParameter(
                    name="texts",
                    param_type=NodeParameterType.JSON,
                    required=False,
                    description="Array of texts for batch operations"
                ),
                NodeParameter(
                    name="model",
                    param_type=NodeParameterType.SELECT,
                    required=False,
                    description="LLM model for token counting",
                    options=[
                        {"label": "GPT-4", "value": "gpt-4"},
                        {"label": "GPT-4 Turbo", "value": "gpt-4-turbo"},
                        {"label": "GPT-4o", "value": "gpt-4o"},
                        {"label": "GPT-3.5 Turbo", "value": "gpt-3.5-turbo"},
                        {"label": "Claude 3 Opus", "value": "claude-3-opus"},
                        {"label": "Claude 3 Sonnet", "value": "claude-3-sonnet"},
                        {"label": "Claude 3 Haiku", "value": "claude-3-haiku"},
                        {"label": "Gemini Pro", "value": "gemini-pro"},
                        {"label": "Llama 2 70B", "value": "llama-2-70b"},
                        {"label": "Mistral Large", "value": "mistral-large"}
                    ],
                    default_value="gpt-4"
                ),
                NodeParameter(
                    name="models",
                    param_type=NodeParameterType.JSON,
                    required=False,
                    description="Array of models for comparison"
                ),
                NodeParameter(
                    name="token_limit",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Token limit for validation/truncation",
                    default_value=4096
                ),
                NodeParameter(
                    name="include_cost",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Include cost estimation in results",
                    default_value=True
                ),
                NodeParameter(
                    name="count_method",
                    param_type=NodeParameterType.SELECT,
                    required=False,
                    description="Method for token counting",
                    options=[
                        {"label": "Accurate (API)", "value": "api"},
                        {"label": "Estimation", "value": "estimate"},
                        {"label": "Simple Word Count", "value": "words"},
                        {"label": "Character Count", "value": "chars"}
                    ],
                    default_value="estimate"
                ),
                NodeParameter(
                    name="split_strategy",
                    param_type=NodeParameterType.SELECT,
                    required=False,
                    description="Strategy for splitting text",
                    options=[
                        {"label": "Sentence Boundary", "value": "sentence"},
                        {"label": "Paragraph Boundary", "value": "paragraph"},
                        {"label": "Word Boundary", "value": "word"},
                        {"label": "Hard Split", "value": "hard"}
                    ],
                    default_value="sentence"
                ),
                NodeParameter(
                    name="optimization_level",
                    param_type=NodeParameterType.SELECT,
                    required=False,
                    description="Level of text optimization",
                    options=[
                        {"label": "None", "value": "none"},
                        {"label": "Basic", "value": "basic"},
                        {"label": "Aggressive", "value": "aggressive"},
                        {"label": "Maximum", "value": "maximum"}
                    ],
                    default_value="basic"
                ),
                NodeParameter(
                    name="preserve_meaning",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Preserve meaning during optimization",
                    default_value=True
                ),
                NodeParameter(
                    name="target_tokens",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Target token count for optimization"
                ),
                NodeParameter(
                    name="include_breakdown",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Include detailed token breakdown",
                    default_value=False
                )
            ],
            icon_path="https://cdn.jsdelivr.net/gh/microsoft/vscode-icons/icons/file_type_ai2.svg"
        )
        super().__init__(schema)
        
        # Model configurations
        self.models = {
            "gpt-4": ModelInfo("gpt-4", 8192, 0.03, 0.06, 8192),
            "gpt-4-turbo": ModelInfo("gpt-4-turbo", 128000, 0.01, 0.03, 128000),
            "gpt-4o": ModelInfo("gpt-4o", 128000, 0.005, 0.015, 128000),
            "gpt-3.5-turbo": ModelInfo("gpt-3.5-turbo", 16385, 0.0015, 0.002, 16385),
            "claude-3-opus": ModelInfo("claude-3-opus", 200000, 0.015, 0.075, 200000),
            "claude-3-sonnet": ModelInfo("claude-3-sonnet", 200000, 0.003, 0.015, 200000),
            "claude-3-haiku": ModelInfo("claude-3-haiku", 200000, 0.00025, 0.00125, 200000),
            "gemini-pro": ModelInfo("gemini-pro", 30720, 0.0005, 0.0015, 30720),
            "llama-2-70b": ModelInfo("llama-2-70b", 4096, 0.0007, 0.0009, 4096),
            "mistral-large": ModelInfo("mistral-large", 32000, 0.008, 0.024, 32000)
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        operation = params.get("operation")
        
        if operation == "count_tokens":
            return await self._count_tokens(params)
        elif operation == "estimate_tokens":
            return await self._estimate_tokens(params)
        elif operation == "count_tokens_batch":
            return await self._count_tokens_batch(params)
        elif operation == "estimate_cost":
            return await self._estimate_cost(params)
        elif operation == "calculate_batch_cost":
            return await self._calculate_batch_cost(params)
        elif operation == "compare_model_costs":
            return await self._compare_model_costs(params)
        elif operation == "analyze_token_distribution":
            return await self._analyze_token_distribution(params)
        elif operation == "get_token_breakdown":
            return await self._get_token_breakdown(params)
        elif operation == "validate_token_limits":
            return await self._validate_token_limits(params)
        elif operation == "optimize_for_tokens":
            return await self._optimize_for_tokens(params)
        elif operation == "truncate_to_limit":
            return await self._truncate_to_limit(params)
        elif operation == "split_by_token_limit":
            return await self._split_by_token_limit(params)
        elif operation == "count_by_model":
            return await self._count_by_model(params)
        elif operation == "get_model_limits":
            return await self._get_model_limits(params)
        elif operation == "check_context_window":
            return await self._check_context_window(params)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    async def _count_tokens(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Count tokens in text with high accuracy."""
        text = params.get("text", "")
        model = params.get("model", "gpt-4")
        count_method = params.get("count_method", "estimate")
        include_cost = params.get("include_cost", True)
        
        if not text:
            raise ValueError("Text is required for token counting")
        
        # Get token count based on method
        if count_method == "api" and params.get("openai_api_key"):
            token_count = await self._accurate_token_count(text, model, params.get("openai_api_key"))
        else:
            token_count = self._estimate_token_count(text, model)
        
        result = TokenResult(
            token_count=token_count,
            character_count=len(text),
            word_count=len(text.split()),
            model_used=model
        )
        
        if include_cost:
            model_info = self.models.get(model)
            if model_info:
                result.estimated_cost = (token_count / 1000) * model_info.input_cost_per_1k
        
        return {
            "token_count": result.token_count,
            "character_count": result.character_count,
            "word_count": result.word_count,
            "estimated_cost": result.estimated_cost,
            "model": result.model_used,
            "cost_currency": "USD"
        }

    async def _estimate_tokens(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fast token estimation using heuristics."""
        text = params.get("text", "")
        model = params.get("model", "gpt-4")
        
        if not text:
            raise ValueError("Text is required for token estimation")
        
        # Fast estimation methods
        char_count = len(text)
        word_count = len(text.split())
        
        # Estimate based on model type
        if "gpt" in model.lower():
            # GPT models: ~4 chars per token on average
            estimated_tokens = char_count // 4
        elif "claude" in model.lower():
            # Claude models: ~3.5 chars per token
            estimated_tokens = char_count // 3.5
        elif "gemini" in model.lower():
            # Gemini: ~3.8 chars per token
            estimated_tokens = char_count // 3.8
        else:
            # Default estimation
            estimated_tokens = char_count // 4
        
        return {
            "estimated_tokens": int(estimated_tokens),
            "character_count": char_count,
            "word_count": word_count,
            "estimation_method": "heuristic",
            "model": model,
            "confidence": "medium"
        }

    async def _count_tokens_batch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Count tokens for multiple texts."""
        texts = params.get("texts", [])
        model = params.get("model", "gpt-4")
        include_cost = params.get("include_cost", True)
        
        if not texts:
            raise ValueError("Texts array is required for batch counting")
        
        results = []
        total_tokens = 0
        total_cost = 0.0
        
        for i, text in enumerate(texts):
            token_count = self._estimate_token_count(text, model)
            char_count = len(text)
            word_count = len(text.split())
            
            result = {
                "index": i,
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "token_count": token_count,
                "character_count": char_count,
                "word_count": word_count
            }
            
            if include_cost:
                model_info = self.models.get(model)
                if model_info:
                    cost = (token_count / 1000) * model_info.input_cost_per_1k
                    result["estimated_cost"] = cost
                    total_cost += cost
            
            results.append(result)
            total_tokens += token_count
        
        return {
            "batch_results": results,
            "total_texts": len(texts),
            "total_tokens": total_tokens,
            "total_cost": total_cost if include_cost else None,
            "average_tokens_per_text": total_tokens / len(texts) if texts else 0,
            "model": model
        }

    async def _estimate_cost(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate costs for LLM operations."""
        text = params.get("text", "")
        model = params.get("model", "gpt-4")
        input_tokens = params.get("input_tokens")
        output_tokens = params.get("output_tokens", 0)
        
        if not text and not input_tokens:
            raise ValueError("Either text or input_tokens is required")
        
        model_info = self.models.get(model)
        if not model_info:
            raise ValueError(f"Model {model} not supported")
        
        # Calculate input tokens
        if input_tokens is None:
            input_tokens = self._estimate_token_count(text, model)
        
        # Calculate costs
        input_cost = (input_tokens / 1000) * model_info.input_cost_per_1k
        output_cost = (output_tokens / 1000) * model_info.output_cost_per_1k
        total_cost = input_cost + output_cost
        
        return {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "currency": "USD",
            "cost_per_1k_input": model_info.input_cost_per_1k,
            "cost_per_1k_output": model_info.output_cost_per_1k
        }

    async def _compare_model_costs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compare costs across different models."""
        text = params.get("text", "")
        models = params.get("models", ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"])
        output_tokens = params.get("output_tokens", 1000)
        
        if not text:
            raise ValueError("Text is required for cost comparison")
        
        comparisons = []
        
        for model in models:
            if model not in self.models:
                continue
                
            model_info = self.models[model]
            input_tokens = self._estimate_token_count(text, model)
            
            input_cost = (input_tokens / 1000) * model_info.input_cost_per_1k
            output_cost = (output_tokens / 1000) * model_info.output_cost_per_1k
            total_cost = input_cost + output_cost
            
            comparisons.append({
                "model": model,
                "input_tokens": input_tokens,
                "total_cost": total_cost,
                "cost_per_1k_tokens": (total_cost / (input_tokens + output_tokens)) * 1000,
                "context_window": model_info.context_window,
                "fits_in_context": input_tokens + output_tokens <= model_info.context_window
            })
        
        # Sort by total cost
        comparisons.sort(key=lambda x: x["total_cost"])
        
        cheapest = comparisons[0] if comparisons else None
        most_expensive = comparisons[-1] if comparisons else None
        
        return {
            "comparisons": comparisons,
            "cheapest_option": cheapest,
            "most_expensive_option": most_expensive,
            "cost_savings": most_expensive["total_cost"] - cheapest["total_cost"] if cheapest and most_expensive else 0,
            "output_tokens": output_tokens
        }

    async def _validate_token_limits(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate text against model token limits."""
        text = params.get("text", "")
        model = params.get("model", "gpt-4")
        token_limit = params.get("token_limit")
        
        if not text:
            raise ValueError("Text is required for validation")
        
        model_info = self.models.get(model)
        if not model_info:
            raise ValueError(f"Model {model} not supported")
        
        # Use provided limit or model's context window
        limit = token_limit or model_info.context_window
        
        token_count = self._estimate_token_count(text, model)
        
        return {
            "text_tokens": token_count,
            "token_limit": limit,
            "within_limit": token_count <= limit,
            "excess_tokens": max(0, token_count - limit),
            "utilization_percentage": (token_count / limit) * 100,
            "model": model,
            "context_window": model_info.context_window,
            "recommendation": self._get_limit_recommendation(token_count, limit)
        }

    async def _truncate_to_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Truncate text to fit within token limits."""
        text = params.get("text", "")
        model = params.get("model", "gpt-4")
        token_limit = params.get("token_limit")
        preserve_meaning = params.get("preserve_meaning", True)
        
        if not text:
            raise ValueError("Text is required for truncation")
        
        model_info = self.models.get(model)
        limit = token_limit or model_info.context_window
        
        current_tokens = self._estimate_token_count(text, model)
        
        if current_tokens <= limit:
            return {
                "original_text": text,
                "truncated_text": text,
                "truncation_needed": False,
                "original_tokens": current_tokens,
                "final_tokens": current_tokens,
                "tokens_removed": 0
            }
        
        # Truncate text
        if preserve_meaning:
            truncated = self._smart_truncate(text, limit, model)
        else:
            # Simple character-based truncation
            ratio = limit / current_tokens
            target_chars = int(len(text) * ratio * 0.9)  # 90% safety margin
            truncated = text[:target_chars]
        
        final_tokens = self._estimate_token_count(truncated, model)
        
        return {
            "original_text": text[:200] + "..." if len(text) > 200 else text,
            "truncated_text": truncated,
            "truncation_needed": True,
            "original_tokens": current_tokens,
            "final_tokens": final_tokens,
            "tokens_removed": current_tokens - final_tokens,
            "character_reduction": len(text) - len(truncated),
            "method": "smart" if preserve_meaning else "simple"
        }

    def _estimate_token_count(self, text: str, model: str) -> int:
        """Estimate token count using various heuristics."""
        if not text:
            return 0
        
        # Basic character-based estimation with model-specific adjustments
        char_count = len(text)
        
        # Model-specific token ratios (characters per token)
        ratios = {
            "gpt-4": 4.0,
            "gpt-4-turbo": 4.0,
            "gpt-4o": 4.0,
            "gpt-3.5-turbo": 4.0,
            "claude-3-opus": 3.5,
            "claude-3-sonnet": 3.5,
            "claude-3-haiku": 3.5,
            "gemini-pro": 3.8,
            "llama-2-70b": 4.2,
            "mistral-large": 3.9
        }
        
        ratio = ratios.get(model, 4.0)
        
        # Adjust for text characteristics
        word_count = len(text.split())
        avg_word_length = char_count / word_count if word_count > 0 else 0
        
        # Longer words typically use fewer tokens per character
        if avg_word_length > 6:
            ratio *= 1.1
        elif avg_word_length < 3:
            ratio *= 0.9
        
        # Account for punctuation and special characters
        special_chars = len(re.findall(r'[^\w\s]', text))
        if special_chars > char_count * 0.1:  # More than 10% special chars
            ratio *= 0.95
        
        estimated_tokens = char_count / ratio
        return max(1, int(estimated_tokens))

    def _smart_truncate(self, text: str, token_limit: int, model: str) -> str:
        """Intelligently truncate text while preserving meaning."""
        # Try to truncate at sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        
        truncated = ""
        for sentence in sentences:
            test_text = truncated + sentence + "."
            if self._estimate_token_count(test_text, model) > token_limit:
                break
            truncated = test_text
        
        # If no complete sentences fit, truncate at word boundaries
        if not truncated and token_limit > 10:
            words = text.split()
            truncated = ""
            for word in words:
                test_text = truncated + " " + word if truncated else word
                if self._estimate_token_count(test_text, model) > token_limit:
                    break
                truncated = test_text
        
        return truncated.strip()

    def _get_limit_recommendation(self, tokens: int, limit: int) -> str:
        """Get recommendation based on token usage."""
        utilization = tokens / limit
        
        if utilization <= 0.5:
            return "Excellent - Well within limits"
        elif utilization <= 0.7:
            return "Good - Comfortable usage"
        elif utilization <= 0.9:
            return "Caution - Approaching limit"
        elif utilization <= 1.0:
            return "Warning - Very close to limit"
        else:
            return "Error - Exceeds token limit"

    async def _accurate_token_count(self, text: str, model: str, api_key: str) -> int:
        """Get accurate token count using OpenAI API (placeholder)."""
        # This would use tiktoken or OpenAI API for accurate counting
        # For now, return estimation
        return self._estimate_token_count(text, model)

    async def _split_by_token_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Split text into chunks based on token limits."""
        text = params.get("text", "")
        model = params.get("model", "gpt-4")
        token_limit = params.get("token_limit", 4000)
        split_strategy = params.get("split_strategy", "sentence")
        
        if not text:
            raise ValueError("Text is required for splitting")
        
        chunks = []
        current_chunk = ""
        
        if split_strategy == "sentence":
            sentences = re.split(r'[.!?]+', text)
            for sentence in sentences:
                test_chunk = current_chunk + sentence + "."
                if self._estimate_token_count(test_chunk, model) > token_limit:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + "."
                else:
                    current_chunk = test_chunk
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Calculate stats
        chunk_stats = []
        for i, chunk in enumerate(chunks):
            token_count = self._estimate_token_count(chunk, model)
            chunk_stats.append({
                "chunk_index": i,
                "token_count": token_count,
                "character_count": len(chunk),
                "preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
            })
        
        return {
            "original_tokens": self._estimate_token_count(text, model),
            "chunks": chunks,
            "chunk_count": len(chunks),
            "chunk_stats": chunk_stats,
            "split_strategy": split_strategy,
            "token_limit": token_limit,
            "model": model
        }

    async def _get_model_limits(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get token limits and information for all models."""
        model = params.get("model")
        
        if model:
            if model not in self.models:
                raise ValueError(f"Model {model} not supported")
            
            model_info = self.models[model]
            return {
                "model": model,
                "max_tokens": model_info.max_tokens,
                "context_window": model_info.context_window,
                "input_cost_per_1k": model_info.input_cost_per_1k,
                "output_cost_per_1k": model_info.output_cost_per_1k
            }
        else:
            # Return all models
            return {
                "models": {
                    name: {
                        "max_tokens": info.max_tokens,
                        "context_window": info.context_window,
                        "input_cost_per_1k": info.input_cost_per_1k,
                        "output_cost_per_1k": info.output_cost_per_1k
                    }
                    for name, info in self.models.items()
                }
            }

    async def _check_context_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check if text fits within model's context window."""
        text = params.get("text", "")
        model = params.get("model", "gpt-4")
        
        if not text:
            raise ValueError("Text is required for context window check")
        
        model_info = self.models.get(model)
        if not model_info:
            raise ValueError(f"Model {model} not supported")
        
        token_count = self._estimate_token_count(text, model)
        context_window = model_info.context_window
        
        return {
            "model": model,
            "text_tokens": token_count,
            "context_window": context_window,
            "fits_in_context": token_count <= context_window,
            "remaining_tokens": context_window - token_count,
            "utilization_percentage": (token_count / context_window) * 100,
            "recommendation": self._get_context_recommendation(token_count, context_window)
        }

    def _get_context_recommendation(self, tokens: int, context_window: int) -> str:
        """Get recommendation for context window usage."""
        utilization = tokens / context_window
        
        if utilization <= 0.3:
            return "Plenty of room for additional context"
        elif utilization <= 0.6:
            return "Good utilization, room for responses"
        elif utilization <= 0.8:
            return "High utilization, limited response space"
        elif utilization <= 0.95:
            return "Very high utilization, consider truncation"
        else:
            return "Exceeds context window, truncation required"

    async def _analyze_token_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how tokens are distributed in the text."""
        text = params.get("text", "")
        model = params.get("model", "gpt-4")
        
        if not text:
            raise ValueError("Text is required for analysis")
        
        # Analyze different parts of the text
        paragraphs = text.split('\n\n')
        sentences = re.split(r'[.!?]+', text)
        words = text.split()
        
        # Calculate token distribution
        paragraph_tokens = [self._estimate_token_count(p, model) for p in paragraphs if p.strip()]
        sentence_tokens = [self._estimate_token_count(s, model) for s in sentences if s.strip()]
        
        total_tokens = self._estimate_token_count(text, model)
        
        return {
            "total_tokens": total_tokens,
            "paragraphs": {
                "count": len(paragraph_tokens),
                "average_tokens": sum(paragraph_tokens) / len(paragraph_tokens) if paragraph_tokens else 0,
                "min_tokens": min(paragraph_tokens) if paragraph_tokens else 0,
                "max_tokens": max(paragraph_tokens) if paragraph_tokens else 0
            },
            "sentences": {
                "count": len(sentence_tokens),
                "average_tokens": sum(sentence_tokens) / len(sentence_tokens) if sentence_tokens else 0,
                "min_tokens": min(sentence_tokens) if sentence_tokens else 0,
                "max_tokens": max(sentence_tokens) if sentence_tokens else 0
            },
            "words": {
                "count": len(words),
                "average_chars_per_word": len(text) / len(words) if words else 0,
                "estimated_tokens_per_word": total_tokens / len(words) if words else 0
            },
            "model": model
        }

    async def _get_token_breakdown(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed breakdown of token usage."""
        text = params.get("text", "")
        model = params.get("model", "gpt-4")
        
        if not text:
            raise ValueError("Text is required for breakdown")
        
        # Analyze different text components
        letters = len(re.findall(r'[a-zA-Z]', text))
        numbers = len(re.findall(r'\d', text))
        punctuation = len(re.findall(r'[^\w\s]', text))
        whitespace = len(re.findall(r'\s', text))
        
        total_tokens = self._estimate_token_count(text, model)
        total_chars = len(text)
        
        return {
            "total_tokens": total_tokens,
            "total_characters": total_chars,
            "character_breakdown": {
                "letters": letters,
                "numbers": numbers,
                "punctuation": punctuation,
                "whitespace": whitespace
            },
            "ratios": {
                "chars_per_token": total_chars / total_tokens if total_tokens > 0 else 0,
                "letters_per_token": letters / total_tokens if total_tokens > 0 else 0,
                "compression_ratio": total_tokens / total_chars if total_chars > 0 else 0
            },
            "text_characteristics": {
                "average_word_length": letters / len(text.split()) if text.split() else 0,
                "punctuation_density": punctuation / total_chars if total_chars > 0 else 0,
                "whitespace_ratio": whitespace / total_chars if total_chars > 0 else 0
            },
            "model": model
        }

    async def _optimize_for_tokens(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize text to reduce token count while preserving meaning."""
        text = params.get("text", "")
        model = params.get("model", "gpt-4")
        optimization_level = params.get("optimization_level", "basic")
        target_tokens = params.get("target_tokens")
        preserve_meaning = params.get("preserve_meaning", True)
        
        if not text:
            raise ValueError("Text is required for optimization")
        
        original_tokens = self._estimate_token_count(text, model)
        optimized_text = text
        
        # Apply optimizations based on level
        if optimization_level in ["basic", "aggressive", "maximum"]:
            # Remove extra whitespace
            optimized_text = re.sub(r'\s+', ' ', optimized_text).strip()
            
        if optimization_level in ["aggressive", "maximum"]:
            # Remove redundant words and phrases
            optimized_text = self._remove_redundancy(optimized_text)
            
        if optimization_level == "maximum":
            # More aggressive optimizations
            optimized_text = self._aggressive_optimize(optimized_text)
        
        # If target tokens specified, truncate if needed
        if target_tokens:
            current_tokens = self._estimate_token_count(optimized_text, model)
            if current_tokens > target_tokens:
                optimized_text = self._smart_truncate(optimized_text, target_tokens, model)
        
        final_tokens = self._estimate_token_count(optimized_text, model)
        
        return {
            "original_text": text[:200] + "..." if len(text) > 200 else text,
            "optimized_text": optimized_text,
            "original_tokens": original_tokens,
            "final_tokens": final_tokens,
            "tokens_saved": original_tokens - final_tokens,
            "reduction_percentage": ((original_tokens - final_tokens) / original_tokens * 100) if original_tokens > 0 else 0,
            "optimization_level": optimization_level,
            "target_tokens": target_tokens,
            "target_achieved": final_tokens <= target_tokens if target_tokens else True,
            "model": model
        }

    def _remove_redundancy(self, text: str) -> str:
        """Remove redundant words and phrases."""
        # Remove common redundant phrases
        redundant_patterns = [
            r'\b(very|really|quite|rather|extremely)\s+',
            r'\b(in order to)\b',
            r'\b(it is|there is|there are)\s+',
            r'\b(that is to say)\b',
            r'\b(as a matter of fact)\b',
            r'\b(the fact that)\b'
        ]
        
        for pattern in redundant_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def _aggressive_optimize(self, text: str) -> str:
        """Apply aggressive optimizations."""
        # Convert contractions
        contractions = {
            r'\bdo not\b': "don't",
            r'\bcannot\b': "can't",
            r'\bwill not\b': "won't",
            r'\bshould not\b': "shouldn't",
            r'\bwould not\b': "wouldn't",
            r'\bis not\b': "isn't",
            r'\bare not\b': "aren't",
            r'\bwas not\b': "wasn't",
            r'\bwere not\b': "weren't"
        }
        
        for pattern, replacement in contractions.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Remove filler words
        filler_words = [
            r'\b(actually|basically|literally|essentially|obviously|clearly)\b',
            r'\b(of course|needless to say|it goes without saying)\b'
        ]
        
        for pattern in filler_words:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    async def _calculate_batch_cost(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total cost for batch operations."""
        texts = params.get("texts", [])
        model = params.get("model", "gpt-4")
        output_tokens_per_text = params.get("output_tokens_per_text", 500)
        
        if not texts:
            raise ValueError("Texts array is required for batch cost calculation")
        
        model_info = self.models.get(model)
        if not model_info:
            raise ValueError(f"Model {model} not supported")
        
        batch_results = []
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0
        
        for i, text in enumerate(texts):
            input_tokens = self._estimate_token_count(text, model)
            output_tokens = output_tokens_per_text
            
            input_cost = (input_tokens / 1000) * model_info.input_cost_per_1k
            output_cost = (output_tokens / 1000) * model_info.output_cost_per_1k
            text_total_cost = input_cost + output_cost
            
            batch_results.append({
                "index": i,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost": text_total_cost,
                "text_preview": text[:50] + "..." if len(text) > 50 else text
            })
            
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_cost += text_total_cost
        
        return {
            "batch_results": batch_results,
            "summary": {
                "total_texts": len(texts),
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens,
                "total_cost": total_cost,
                "average_cost_per_text": total_cost / len(texts) if texts else 0,
                "currency": "USD"
            },
            "model": model,
            "output_tokens_per_text": output_tokens_per_text
        }