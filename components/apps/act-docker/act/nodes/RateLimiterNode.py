#!/usr/bin/env python3

import asyncio
import logging
import time
from collections import defaultdict, deque
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import threading
from abc import ABC, abstractmethod

try:
    from .base_node import BaseNode
except ImportError:
    try:
        from base_node import BaseNode
    except ImportError:
        from act_workflow.nodes.base_node import BaseNode

class RateLimitOperation(Enum):
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW_COUNTER = "sliding_window_counter"
    ADAPTIVE_RATE_LIMIT = "adaptive_rate_limit"
    DISTRIBUTED_RATE_LIMIT = "distributed_rate_limit"
    HIERARCHICAL_RATE_LIMIT = "hierarchical_rate_limit"
    QUOTA_MANAGEMENT = "quota_management"
    RATE_LIMIT_CONFIG = "rate_limit_config"
    RATE_LIMIT_STATUS = "rate_limit_status"
    RATE_LIMIT_RESET = "rate_limit_reset"
    RATE_LIMIT_BURST = "rate_limit_burst"
    RATE_LIMIT_PRIORITY = "rate_limit_priority"
    RATE_LIMIT_ANALYZE = "rate_limit_analyze"

@dataclass
class RateLimitConfig:
    limit: int = 100
    window_size: int = 60
    burst_size: int = 10
    refill_rate: float = 1.0
    algorithm: str = "token_bucket"
    enable_burst: bool = True
    priority: int = 1
    quota_reset_interval: int = 3600
    
@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_time: float
    retry_after: float
    current_usage: int
    limit: int
    algorithm: str
    metadata: Dict[str, Any]

class RateLimiter(ABC):
    """Abstract base class for rate limiters"""
    
    @abstractmethod
    async def is_allowed(self, identifier: str, request_weight: int = 1) -> RateLimitResult:
        pass
    
    @abstractmethod
    async def reset(self, identifier: str) -> bool:
        pass
    
    @abstractmethod
    async def get_status(self, identifier: str) -> Dict[str, Any]:
        pass

class TokenBucketRateLimiter(RateLimiter):
    """Token bucket rate limiter implementation"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.buckets = defaultdict(lambda: {"tokens": config.limit, "last_refill": time.time()})
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    async def is_allowed(self, identifier: str, request_weight: int = 1) -> RateLimitResult:
        with self.lock:
            bucket = self.buckets[identifier]
            now = time.time()
            
            # Refill tokens
            time_passed = now - bucket["last_refill"]
            tokens_to_add = time_passed * self.config.refill_rate
            bucket["tokens"] = min(self.config.limit, bucket["tokens"] + tokens_to_add)
            bucket["last_refill"] = now
            
            # Check if request can be processed
            if bucket["tokens"] >= request_weight:
                bucket["tokens"] -= request_weight
                return RateLimitResult(
                    allowed=True,
                    remaining=int(bucket["tokens"]),
                    reset_time=now + (self.config.limit - bucket["tokens"]) / self.config.refill_rate,
                    retry_after=0,
                    current_usage=self.config.limit - int(bucket["tokens"]),
                    limit=self.config.limit,
                    algorithm="token_bucket",
                    metadata={"refill_rate": self.config.refill_rate}
                )
            else:
                retry_after = (request_weight - bucket["tokens"]) / self.config.refill_rate
                return RateLimitResult(
                    allowed=False,
                    remaining=int(bucket["tokens"]),
                    reset_time=now + retry_after,
                    retry_after=retry_after,
                    current_usage=self.config.limit - int(bucket["tokens"]),
                    limit=self.config.limit,
                    algorithm="token_bucket",
                    metadata={"refill_rate": self.config.refill_rate}
                )
    
    async def reset(self, identifier: str) -> bool:
        with self.lock:
            if identifier in self.buckets:
                self.buckets[identifier] = {"tokens": self.config.limit, "last_refill": time.time()}
                return True
            return False
    
    async def get_status(self, identifier: str) -> Dict[str, Any]:
        with self.lock:
            bucket = self.buckets[identifier]
            return {
                "tokens": bucket["tokens"],
                "last_refill": bucket["last_refill"],
                "capacity": self.config.limit,
                "refill_rate": self.config.refill_rate
            }

class LeakyBucketRateLimiter(RateLimiter):
    """Leaky bucket rate limiter implementation"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.buckets = defaultdict(lambda: {"level": 0, "last_leak": time.time()})
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    async def is_allowed(self, identifier: str, request_weight: int = 1) -> RateLimitResult:
        with self.lock:
            bucket = self.buckets[identifier]
            now = time.time()
            
            # Leak water from bucket
            time_passed = now - bucket["last_leak"]
            leak_amount = time_passed * self.config.refill_rate
            bucket["level"] = max(0, bucket["level"] - leak_amount)
            bucket["last_leak"] = now
            
            # Check if request can be processed
            if bucket["level"] + request_weight <= self.config.limit:
                bucket["level"] += request_weight
                return RateLimitResult(
                    allowed=True,
                    remaining=int(self.config.limit - bucket["level"]),
                    reset_time=now + bucket["level"] / self.config.refill_rate,
                    retry_after=0,
                    current_usage=int(bucket["level"]),
                    limit=self.config.limit,
                    algorithm="leaky_bucket",
                    metadata={"leak_rate": self.config.refill_rate}
                )
            else:
                retry_after = (bucket["level"] + request_weight - self.config.limit) / self.config.refill_rate
                return RateLimitResult(
                    allowed=False,
                    remaining=int(self.config.limit - bucket["level"]),
                    reset_time=now + retry_after,
                    retry_after=retry_after,
                    current_usage=int(bucket["level"]),
                    limit=self.config.limit,
                    algorithm="leaky_bucket",
                    metadata={"leak_rate": self.config.refill_rate}
                )
    
    async def reset(self, identifier: str) -> bool:
        with self.lock:
            if identifier in self.buckets:
                self.buckets[identifier] = {"level": 0, "last_leak": time.time()}
                return True
            return False
    
    async def get_status(self, identifier: str) -> Dict[str, Any]:
        with self.lock:
            bucket = self.buckets[identifier]
            return {
                "level": bucket["level"],
                "last_leak": bucket["last_leak"],
                "capacity": self.config.limit,
                "leak_rate": self.config.refill_rate
            }

class SlidingWindowRateLimiter(RateLimiter):
    """Sliding window rate limiter implementation"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.windows = defaultdict(lambda: deque())
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    async def is_allowed(self, identifier: str, request_weight: int = 1) -> RateLimitResult:
        with self.lock:
            window = self.windows[identifier]
            now = time.time()
            cutoff = now - self.config.window_size
            
            # Remove old entries
            while window and window[0] <= cutoff:
                window.popleft()
            
            # Check if request can be processed
            current_count = len(window)
            if current_count < self.config.limit:
                window.append(now)
                return RateLimitResult(
                    allowed=True,
                    remaining=self.config.limit - current_count - 1,
                    reset_time=now + self.config.window_size,
                    retry_after=0,
                    current_usage=current_count + 1,
                    limit=self.config.limit,
                    algorithm="sliding_window",
                    metadata={"window_size": self.config.window_size}
                )
            else:
                # Calculate retry after based on oldest entry
                retry_after = window[0] + self.config.window_size - now
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=window[0] + self.config.window_size,
                    retry_after=max(0, retry_after),
                    current_usage=current_count,
                    limit=self.config.limit,
                    algorithm="sliding_window",
                    metadata={"window_size": self.config.window_size}
                )
    
    async def reset(self, identifier: str) -> bool:
        with self.lock:
            if identifier in self.windows:
                self.windows[identifier].clear()
                return True
            return False
    
    async def get_status(self, identifier: str) -> Dict[str, Any]:
        with self.lock:
            window = self.windows[identifier]
            return {
                "current_count": len(window),
                "window_size": self.config.window_size,
                "limit": self.config.limit,
                "oldest_entry": window[0] if window else None
            }

class FixedWindowRateLimiter(RateLimiter):
    """Fixed window rate limiter implementation"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.windows = defaultdict(lambda: {"count": 0, "window_start": 0})
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    async def is_allowed(self, identifier: str, request_weight: int = 1) -> RateLimitResult:
        with self.lock:
            window = self.windows[identifier]
            now = time.time()
            current_window = int(now // self.config.window_size)
            
            # Reset window if it's a new window
            if window["window_start"] != current_window:
                window["count"] = 0
                window["window_start"] = current_window
            
            # Check if request can be processed
            if window["count"] + request_weight <= self.config.limit:
                window["count"] += request_weight
                window_end = (current_window + 1) * self.config.window_size
                return RateLimitResult(
                    allowed=True,
                    remaining=self.config.limit - window["count"],
                    reset_time=window_end,
                    retry_after=0,
                    current_usage=window["count"],
                    limit=self.config.limit,
                    algorithm="fixed_window",
                    metadata={"window_start": current_window * self.config.window_size}
                )
            else:
                window_end = (current_window + 1) * self.config.window_size
                retry_after = window_end - now
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=window_end,
                    retry_after=retry_after,
                    current_usage=window["count"],
                    limit=self.config.limit,
                    algorithm="fixed_window",
                    metadata={"window_start": current_window * self.config.window_size}
                )
    
    async def reset(self, identifier: str) -> bool:
        with self.lock:
            if identifier in self.windows:
                self.windows[identifier] = {"count": 0, "window_start": 0}
                return True
            return False
    
    async def get_status(self, identifier: str) -> Dict[str, Any]:
        with self.lock:
            window = self.windows[identifier]
            return {
                "count": window["count"],
                "window_start": window["window_start"],
                "window_size": self.config.window_size,
                "limit": self.config.limit
            }

class AdaptiveRateLimiter(RateLimiter):
    """Adaptive rate limiter that adjusts limits based on system load"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.base_limiter = TokenBucketRateLimiter(config)
        self.load_factor = 1.0
        self.last_adjustment = time.time()
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    async def is_allowed(self, identifier: str, request_weight: int = 1) -> RateLimitResult:
        # Adjust load factor based on system metrics
        await self._adjust_load_factor()
        
        # Create adapted config
        adapted_config = RateLimitConfig(
            limit=int(self.config.limit * self.load_factor),
            window_size=self.config.window_size,
            burst_size=self.config.burst_size,
            refill_rate=self.config.refill_rate * self.load_factor,
            algorithm="adaptive"
        )
        
        # Use adapted limiter
        adapted_limiter = TokenBucketRateLimiter(adapted_config)
        result = await adapted_limiter.is_allowed(identifier, request_weight)
        result.algorithm = "adaptive"
        result.metadata["load_factor"] = self.load_factor
        result.metadata["original_limit"] = self.config.limit
        
        return result
    
    async def _adjust_load_factor(self):
        """Adjust load factor based on system metrics"""
        now = time.time()
        if now - self.last_adjustment > 60:  # Adjust every minute
            # Simple load factor adjustment (in real implementation, use actual metrics)
            # For demo purposes, we'll use a simple fluctuation
            import random
            self.load_factor = max(0.1, min(2.0, self.load_factor + random.uniform(-0.1, 0.1)))
            self.last_adjustment = now
    
    async def reset(self, identifier: str) -> bool:
        return await self.base_limiter.reset(identifier)
    
    async def get_status(self, identifier: str) -> Dict[str, Any]:
        status = await self.base_limiter.get_status(identifier)
        status["load_factor"] = self.load_factor
        return status

class RateLimiterNode(BaseNode):
    def __init__(self, node_id: str = "rate_limiter"):
        super().__init__(node_id)
        self.logger = logging.getLogger(__name__)
        self.limiters = {}
        self.operation_map = {
            RateLimitOperation.TOKEN_BUCKET: self._token_bucket,
            RateLimitOperation.LEAKY_BUCKET: self._leaky_bucket,
            RateLimitOperation.SLIDING_WINDOW: self._sliding_window,
            RateLimitOperation.FIXED_WINDOW: self._fixed_window,
            RateLimitOperation.SLIDING_WINDOW_COUNTER: self._sliding_window_counter,
            RateLimitOperation.ADAPTIVE_RATE_LIMIT: self._adaptive_rate_limit,
            RateLimitOperation.DISTRIBUTED_RATE_LIMIT: self._distributed_rate_limit,
            RateLimitOperation.HIERARCHICAL_RATE_LIMIT: self._hierarchical_rate_limit,
            RateLimitOperation.QUOTA_MANAGEMENT: self._quota_management,
            RateLimitOperation.RATE_LIMIT_CONFIG: self._rate_limit_config,
            RateLimitOperation.RATE_LIMIT_STATUS: self._rate_limit_status,
            RateLimitOperation.RATE_LIMIT_RESET: self._rate_limit_reset,
            RateLimitOperation.RATE_LIMIT_BURST: self._rate_limit_burst,
            RateLimitOperation.RATE_LIMIT_PRIORITY: self._rate_limit_priority,
            RateLimitOperation.RATE_LIMIT_ANALYZE: self._rate_limit_analyze,
        }
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [op.value for op in RateLimitOperation],
                    "description": "The rate limiting operation to perform"
                },
                "identifier": {
                    "type": "string",
                    "description": "Unique identifier for the rate limit (e.g., user ID, IP address)"
                },
                "limit": {
                    "type": "integer",
                    "default": 100,
                    "description": "Maximum number of requests allowed"
                },
                "window_size": {
                    "type": "integer",
                    "default": 60,
                    "description": "Time window in seconds"
                },
                "burst_size": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum burst size allowed"
                },
                "refill_rate": {
                    "type": "number",
                    "default": 1.0,
                    "description": "Rate at which tokens are refilled (tokens per second)"
                },
                "algorithm": {
                    "type": "string",
                    "enum": ["token_bucket", "leaky_bucket", "sliding_window", "fixed_window", "adaptive"],
                    "default": "token_bucket",
                    "description": "Rate limiting algorithm to use"
                },
                "request_weight": {
                    "type": "integer",
                    "default": 1,
                    "description": "Weight of the current request"
                },
                "priority": {
                    "type": "integer",
                    "default": 1,
                    "description": "Priority level for hierarchical rate limiting"
                },
                "enable_burst": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable burst capacity"
                },
                "quota_reset_interval": {
                    "type": "integer",
                    "default": 3600,
                    "description": "Quota reset interval in seconds"
                }
            },
            "required": ["operation", "identifier"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            operation = RateLimitOperation(params["operation"])
            self.logger.info(f"Executing rate limit operation: {operation}")
            
            handler = self.operation_map.get(operation)
            if not handler:
                raise ValueError(f"Unknown rate limit operation: {operation}")
            
            result = await handler(params)
            
            self.logger.info(f"Rate limit operation {operation} completed successfully")
            return {
                "status": "success",
                "result": result,
                "operation": operation.value
            }
            
        except Exception as e:
            self.logger.error(f"Rate limit operation error: {str(e)}")
            return {
                "status": "error",
                "error": f"Rate limit operation error: {str(e)}",
                "operation": params.get("operation", "unknown")
            }
    
    def _get_or_create_limiter(self, identifier: str, config: RateLimitConfig) -> RateLimiter:
        """Get or create rate limiter for identifier"""
        limiter_key = f"{identifier}_{config.algorithm}"
        
        if limiter_key not in self.limiters:
            if config.algorithm == "token_bucket":
                self.limiters[limiter_key] = TokenBucketRateLimiter(config)
            elif config.algorithm == "leaky_bucket":
                self.limiters[limiter_key] = LeakyBucketRateLimiter(config)
            elif config.algorithm == "sliding_window":
                self.limiters[limiter_key] = SlidingWindowRateLimiter(config)
            elif config.algorithm == "fixed_window":
                self.limiters[limiter_key] = FixedWindowRateLimiter(config)
            elif config.algorithm == "adaptive":
                self.limiters[limiter_key] = AdaptiveRateLimiter(config)
            else:
                self.limiters[limiter_key] = TokenBucketRateLimiter(config)
        
        return self.limiters[limiter_key]
    
    def _create_config(self, params: Dict[str, Any]) -> RateLimitConfig:
        """Create rate limit configuration from parameters"""
        return RateLimitConfig(
            limit=params.get("limit", 100),
            window_size=params.get("window_size", 60),
            burst_size=params.get("burst_size", 10),
            refill_rate=params.get("refill_rate", 1.0),
            algorithm=params.get("algorithm", "token_bucket"),
            enable_burst=params.get("enable_burst", True),
            priority=params.get("priority", 1),
            quota_reset_interval=params.get("quota_reset_interval", 3600)
        )
    
    async def _token_bucket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Token bucket rate limiting"""
        identifier = params["identifier"]
        config = self._create_config(params)
        config.algorithm = "token_bucket"
        
        limiter = self._get_or_create_limiter(identifier, config)
        result = await limiter.is_allowed(identifier, params.get("request_weight", 1))
        
        return {
            "allowed": result.allowed,
            "remaining": result.remaining,
            "reset_time": result.reset_time,
            "retry_after": result.retry_after,
            "current_usage": result.current_usage,
            "limit": result.limit,
            "algorithm": result.algorithm,
            "metadata": result.metadata
        }
    
    async def _leaky_bucket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Leaky bucket rate limiting"""
        identifier = params["identifier"]
        config = self._create_config(params)
        config.algorithm = "leaky_bucket"
        
        limiter = self._get_or_create_limiter(identifier, config)
        result = await limiter.is_allowed(identifier, params.get("request_weight", 1))
        
        return {
            "allowed": result.allowed,
            "remaining": result.remaining,
            "reset_time": result.reset_time,
            "retry_after": result.retry_after,
            "current_usage": result.current_usage,
            "limit": result.limit,
            "algorithm": result.algorithm,
            "metadata": result.metadata
        }
    
    async def _sliding_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sliding window rate limiting"""
        identifier = params["identifier"]
        config = self._create_config(params)
        config.algorithm = "sliding_window"
        
        limiter = self._get_or_create_limiter(identifier, config)
        result = await limiter.is_allowed(identifier, params.get("request_weight", 1))
        
        return {
            "allowed": result.allowed,
            "remaining": result.remaining,
            "reset_time": result.reset_time,
            "retry_after": result.retry_after,
            "current_usage": result.current_usage,
            "limit": result.limit,
            "algorithm": result.algorithm,
            "metadata": result.metadata
        }
    
    async def _fixed_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fixed window rate limiting"""
        identifier = params["identifier"]
        config = self._create_config(params)
        config.algorithm = "fixed_window"
        
        limiter = self._get_or_create_limiter(identifier, config)
        result = await limiter.is_allowed(identifier, params.get("request_weight", 1))
        
        return {
            "allowed": result.allowed,
            "remaining": result.remaining,
            "reset_time": result.reset_time,
            "retry_after": result.retry_after,
            "current_usage": result.current_usage,
            "limit": result.limit,
            "algorithm": result.algorithm,
            "metadata": result.metadata
        }
    
    async def _sliding_window_counter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sliding window counter rate limiting"""
        # Use sliding window implementation
        return await self._sliding_window(params)
    
    async def _adaptive_rate_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptive rate limiting"""
        identifier = params["identifier"]
        config = self._create_config(params)
        config.algorithm = "adaptive"
        
        limiter = self._get_or_create_limiter(identifier, config)
        result = await limiter.is_allowed(identifier, params.get("request_weight", 1))
        
        return {
            "allowed": result.allowed,
            "remaining": result.remaining,
            "reset_time": result.reset_time,
            "retry_after": result.retry_after,
            "current_usage": result.current_usage,
            "limit": result.limit,
            "algorithm": result.algorithm,
            "metadata": result.metadata
        }
    
    async def _distributed_rate_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Distributed rate limiting (simplified implementation)"""
        # In a real implementation, this would use Redis or similar
        return await self._token_bucket(params)
    
    async def _hierarchical_rate_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Hierarchical rate limiting with priority levels"""
        identifier = params["identifier"]
        priority = params.get("priority", 1)
        
        # Adjust limits based on priority
        config = self._create_config(params)
        config.limit = int(config.limit * (1 + priority * 0.1))  # Higher priority gets more quota
        
        limiter = self._get_or_create_limiter(identifier, config)
        result = await limiter.is_allowed(identifier, params.get("request_weight", 1))
        
        return {
            "allowed": result.allowed,
            "remaining": result.remaining,
            "reset_time": result.reset_time,
            "retry_after": result.retry_after,
            "current_usage": result.current_usage,
            "limit": result.limit,
            "algorithm": result.algorithm,
            "priority": priority,
            "metadata": result.metadata
        }
    
    async def _quota_management(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Quota management operations"""
        identifier = params["identifier"]
        config = self._create_config(params)
        
        limiter = self._get_or_create_limiter(identifier, config)
        status = await limiter.get_status(identifier)
        
        return {
            "identifier": identifier,
            "quota_used": status.get("count", 0),
            "quota_limit": config.limit,
            "quota_remaining": config.limit - status.get("count", 0),
            "reset_interval": config.quota_reset_interval,
            "status": status
        }
    
    async def _rate_limit_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configure rate limit settings"""
        identifier = params["identifier"]
        config = self._create_config(params)
        
        return {
            "identifier": identifier,
            "configuration": {
                "limit": config.limit,
                "window_size": config.window_size,
                "burst_size": config.burst_size,
                "refill_rate": config.refill_rate,
                "algorithm": config.algorithm,
                "enable_burst": config.enable_burst,
                "priority": config.priority,
                "quota_reset_interval": config.quota_reset_interval
            }
        }
    
    async def _rate_limit_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get rate limit status"""
        identifier = params["identifier"]
        config = self._create_config(params)
        
        limiter = self._get_or_create_limiter(identifier, config)
        status = await limiter.get_status(identifier)
        
        return {
            "identifier": identifier,
            "status": status,
            "algorithm": config.algorithm,
            "timestamp": time.time()
        }
    
    async def _rate_limit_reset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reset rate limit for identifier"""
        identifier = params["identifier"]
        config = self._create_config(params)
        
        limiter = self._get_or_create_limiter(identifier, config)
        reset_success = await limiter.reset(identifier)
        
        return {
            "identifier": identifier,
            "reset_success": reset_success,
            "timestamp": time.time()
        }
    
    async def _rate_limit_burst(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle burst rate limiting"""
        identifier = params["identifier"]
        config = self._create_config(params)
        
        # Enable burst and increase limit temporarily
        config.enable_burst = True
        config.limit = config.limit + config.burst_size
        
        limiter = self._get_or_create_limiter(identifier, config)
        result = await limiter.is_allowed(identifier, params.get("request_weight", 1))
        
        return {
            "allowed": result.allowed,
            "remaining": result.remaining,
            "reset_time": result.reset_time,
            "retry_after": result.retry_after,
            "current_usage": result.current_usage,
            "limit": result.limit,
            "algorithm": result.algorithm,
            "burst_enabled": True,
            "metadata": result.metadata
        }
    
    async def _rate_limit_priority(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Priority-based rate limiting"""
        return await self._hierarchical_rate_limit(params)
    
    async def _rate_limit_analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze rate limit patterns and metrics"""
        identifier = params["identifier"]
        config = self._create_config(params)
        
        limiter = self._get_or_create_limiter(identifier, config)
        status = await limiter.get_status(identifier)
        
        # Calculate metrics
        usage_percentage = (status.get("count", 0) / config.limit) * 100 if config.limit > 0 else 0
        
        analysis = {
            "identifier": identifier,
            "usage_percentage": usage_percentage,
            "is_approaching_limit": usage_percentage > 80,
            "is_at_limit": usage_percentage >= 100,
            "recommended_action": "normal",
            "status": status,
            "configuration": {
                "limit": config.limit,
                "window_size": config.window_size,
                "algorithm": config.algorithm
            }
        }
        
        # Provide recommendations
        if usage_percentage > 90:
            analysis["recommended_action"] = "increase_limit"
        elif usage_percentage > 80:
            analysis["recommended_action"] = "monitor_closely"
        elif usage_percentage < 20:
            analysis["recommended_action"] = "consider_reducing_limit"
        
        return analysis