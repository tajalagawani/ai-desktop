#!/usr/bin/env python3
"""
Universal Request Node - Production-Ready HTTP Client
Version 2.1 - Complete implementation with all critical fixes

Features:
- Thread-safe operation with proper async lifecycle
- Robust error handling and retry logic
- Efficient resource management
- Comprehensive validation and security
- Smart caching and rate limiting
- Performance monitoring and metrics
- Query parameter support
- Multiple content type handling
- Circuit breaker pattern
- Request deduplication
- Streaming support
- Compression handling
- Proxy support
"""

import asyncio
import aiohttp
import json
import time
import random
import logging
import base64
import hashlib
import re
import os
import gzip
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlencode, urlparse
from collections import OrderedDict, deque

# Configure logging
logger = logging.getLogger(__name__)

# ===========================
# Configuration Classes  
# ===========================

class AuthType(str, Enum):
    """Supported authentication types."""
    BEARER_TOKEN = "bearer_token"
    API_KEY = "api_key" 
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"
    OAUTH2 = "oauth2"
    AWS_SIGNATURE = "aws_signature"

class BackoffStrategy(str, Enum):
    """Retry backoff strategies."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"
    EXPONENTIAL_JITTER = "exponential_jitter"

class PaginationType(str, Enum):
    """Pagination patterns."""
    OFFSET = "offset"
    CURSOR = "cursor" 
    LINK = "link"
    TOKEN = "token"
    PAGE = "page"
    NONE = "none"

class ValidationPattern(str, Enum):
    """Common validation patterns."""
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    UUID = "uuid"
    ISO_DATE = "iso_date"
    REGEX = "regex"
    CUSTOM = "custom"

class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class ValidationRule:
    """Input validation rule."""
    pattern: str
    message: str
    pattern_type: ValidationPattern = ValidationPattern.CUSTOM
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    required: bool = False

@dataclass
class ArrayTemplate:
    """Template for array parameters."""
    template: Any
    description: str
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    item_validation: Optional[ValidationRule] = None

@dataclass
class OutputSchema:
    """Operation-specific output schema."""
    success_schema: Dict[str, Any]
    error_schema: Dict[str, Any]
    status_codes: Dict[int, str] = field(default_factory=dict)

@dataclass
class ParameterDependency:
    """Parameter dependency rules."""
    when_field: str
    when_value: Any
    then_require: List[str] = field(default_factory=list)
    then_optional: List[str] = field(default_factory=list)
    require_one_of: List[str] = field(default_factory=list)
    mutually_exclusive: List[str] = field(default_factory=list)

@dataclass  
class RateLimitInfo:
    """Rate limiting information."""
    requests_per_minute: int
    requests_per_second: Optional[float] = None
    burst_limit: int = 30
    cost_per_request: Optional[float] = None
    quota_type: str = "requests"

@dataclass
class PricingInfo:
    """API pricing information."""
    cost_per_1k_tokens: Optional[float] = None
    cost_per_request: Optional[float] = None
    billing_unit: str = "requests"
    free_tier_limit: Optional[int] = None

@dataclass
class WebhookConfig:
    """Webhook configuration."""
    callback_param: Optional[str] = None
    supported_events: List[str] = field(default_factory=list)
    retry_policy: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PaginationConfig:
    """Pagination configuration."""
    type: PaginationType = PaginationType.NONE
    page_param: str = "page"
    cursor_param: str = "cursor"
    size_param: str = "page_size"
    default_size: int = 25
    max_size: int = 100
    total_pages_field: Optional[str] = None
    total_records_field: Optional[str] = None
    next_cursor_field: Optional[str] = None
    has_more_field: Optional[str] = None

@dataclass
class FieldMapping:
    """Field transformation configuration."""
    input_transforms: Dict[str, str] = field(default_factory=dict)
    output_transforms: Dict[str, str] = field(default_factory=dict)
    field_aliases: Dict[str, str] = field(default_factory=dict)

@dataclass
class RetryConfig:
    """Retry configuration."""
    max_attempts: int = 3
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL_JITTER
    base_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True
    retriable_codes: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])
    retriable_exceptions: List[str] = field(default_factory=lambda: [
        "ClientTimeout", "ClientConnectorError", "ServerTimeoutError", "ClientOSError"
    ])
    timeout_ms: int = 30000

@dataclass
class MonitoringConfig:
    """Performance monitoring configuration."""
    track_response_time: bool = True
    log_errors: bool = True
    metrics: List[str] = field(default_factory=lambda: ["success_rate", "avg_response_time", "error_count"])
    alerts: Dict[str, Union[int, float]] = field(default_factory=dict)
    max_metrics_history: int = 1000

@dataclass
class CachingConfig:
    """Caching strategy configuration."""
    enabled: bool = False
    cache_key_template: str = "{operation}:{hash}"
    ttl_seconds: int = 300
    max_cache_size: int = 1000
    cache_conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    enabled: bool = False
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: int = 60
    half_open_max_calls: int = 3

@dataclass
class ProxyConfig:
    """Proxy configuration."""
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    no_proxy: Optional[List[str]] = None

@dataclass
class CompressionConfig:
    """Compression configuration."""
    enabled: bool = True
    accept_encoding: List[str] = field(default_factory=lambda: ["gzip", "deflate"])
    auto_decompress: bool = True

@dataclass
class TestingConfig:
    """Testing and validation configuration."""
    sandbox_mode: bool = False
    test_credentials_param: Optional[str] = None
    validation_endpoint: Optional[str] = None

@dataclass
class DocumentationConfig:
    """Documentation links."""
    api_docs_url: Optional[str] = None
    setup_guide: Optional[str] = None
    troubleshooting: Optional[str] = None
    changelog: Optional[str] = None

# ===========================
# Operation Configuration
# ===========================

@dataclass
class OperationConfig:
    """Complete operation configuration."""
    method: str
    endpoint: str
    description: str
    
    # Parameters
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)
    body_parameters: List[str] = field(default_factory=list)
    path_parameters: Set[str] = field(default_factory=set)
    
    # Advanced features
    output_schema: Optional[OutputSchema] = None
    array_templates: Dict[str, ArrayTemplate] = field(default_factory=dict)
    validation_rules: Dict[str, ValidationRule] = field(default_factory=dict)
    parameter_dependencies: List[ParameterDependency] = field(default_factory=list)
    
    # API details
    rate_limit_cost: int = 1
    cache_ttl: int = 0
    webhook_support: Optional[WebhookConfig] = None
    pagination: Optional[PaginationConfig] = None
    field_mapping: Optional[FieldMapping] = None
    
    # Auth and examples
    auth: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    display_name: Optional[str] = None
    group: str = "General"
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False
    response_type: str = "object"
    streaming_supported: bool = False

# ===========================
# Main Configuration
# ===========================

@dataclass
class UniversalRequestConfig:
    """Universal request configuration."""
    # Core API config
    base_url: str
    authentication: Dict[str, Any]
    default_headers: Dict[str, str] = field(default_factory=dict)
    
    # Configurations
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    rate_limiting: RateLimitInfo = field(default_factory=lambda: RateLimitInfo(requests_per_minute=300))
    pricing: Optional[PricingInfo] = None
    timeouts: Dict[str, float] = field(default_factory=lambda: {"connect": 10.0, "read": 30.0, "total": 60.0})
    
    # Advanced features
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    caching: CachingConfig = field(default_factory=CachingConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    compression: CompressionConfig = field(default_factory=CompressionConfig)
    testing: TestingConfig = field(default_factory=TestingConfig)
    documentation: DocumentationConfig = field(default_factory=DocumentationConfig)
    
    # Node metadata
    node_info: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    auth: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    error_codes: Dict[str, str] = field(default_factory=dict)

# ===========================
# Centralized Import Helper
# ===========================

def import_base_node():
    """Centralized import for base_node module."""
    try:
        from .base_node import NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        try:
            from base_node import NodeSchema, NodeParameter, NodeParameterType
        except ImportError:
            logger.warning("base_node module not found, using minimal implementations")
            from enum import Enum
            
            class NodeParameterType(str, Enum):
                STRING = "string"
                NUMBER = "number"
                BOOLEAN = "boolean"
                ARRAY = "array"
                OBJECT = "object"
                ANY = "any"
            
            class NodeParameter:
                def __init__(self, name, type, description="", required=False, default=None, enum=None, validation=None):
                    self.name = name
                    self.type = type
                    self.description = description
                    self.required = required
                    self.default = default
                    self.enum = enum
                    self.validation = validation
            
            class NodeSchema:
                def __init__(self, node_type, version, description, parameters, outputs):
                    self.node_type = node_type
                    self.version = version
                    self.description = description
                    self.parameters = parameters
                    self.outputs = outputs
    
    return NodeSchema, NodeParameter, NodeParameterType

# ===========================
# Validation Engine
# ===========================

class ValidationEngine:
    """Advanced parameter validation with patterns and dependencies."""
    
    PATTERNS = {
        ValidationPattern.EMAIL: r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        ValidationPattern.PHONE: r'^\+?[1-9]\d{1,14}$',
        ValidationPattern.URL: r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$',
        ValidationPattern.UUID: r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        ValidationPattern.ISO_DATE: r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z?$'
    }
    
    @classmethod
    def validate_parameter(cls, value: Any, rule: ValidationRule) -> Tuple[bool, str]:
        """Validate a single parameter value."""
        if rule.required and (value is None or value == ""):
            return False, "This field is required"
        
        if value is None or value == "":
            return True, ""
        
        # Type validation for strings
        if isinstance(value, str):
            if rule.min_length and len(value) < rule.min_length:
                return False, f"Minimum length is {rule.min_length}"
            if rule.max_length and len(value) > rule.max_length:
                return False, f"Maximum length is {rule.max_length}"
        
        # Type validation for numbers
        if isinstance(value, (int, float)):
            if rule.min_value is not None and value < rule.min_value:
                return False, f"Minimum value is {rule.min_value}"
            if rule.max_value is not None and value > rule.max_value:
                return False, f"Maximum value is {rule.max_value}"
        
        # Pattern validation
        if isinstance(value, str) and rule.pattern:
            if rule.pattern_type == ValidationPattern.REGEX:
                if not rule.pattern:
                    return False, "Regex pattern cannot be empty"
                pattern = rule.pattern
            else:
                pattern = cls.PATTERNS.get(rule.pattern_type, rule.pattern)
            
            if pattern:
                try:
                    if not re.match(pattern, value, re.IGNORECASE if rule.pattern_type != ValidationPattern.REGEX else 0):
                        return False, rule.message or "Invalid format"
                except re.error as e:
                    logger.error(f"Invalid regex pattern: {e}")
                    return False, "Invalid regex pattern"
        
        return True, ""
    
    @classmethod
    def validate_dependencies(cls, params: Dict[str, Any], dependencies: List[ParameterDependency]) -> List[str]:
        """Validate parameter dependencies."""
        errors = []
        
        for dep in dependencies:
            when_value = params.get(dep.when_field)
            
            if when_value == dep.when_value:
                # Check required fields
                for field in dep.then_require:
                    if field not in params or params[field] is None:
                        errors.append(f"Field '{field}' is required when '{dep.when_field}' is '{dep.when_value}'")
                
                # Check require_one_of
                if dep.require_one_of:
                    if not any(field in params and params[field] is not None for field in dep.require_one_of):
                        errors.append(f"At least one of {dep.require_one_of} is required")
                
                # Check mutually exclusive
                exclusive_present = [field for field in dep.mutually_exclusive if field in params and params[field] is not None]
                if len(exclusive_present) > 1:
                    errors.append(f"Fields {exclusive_present} are mutually exclusive")
        
        return errors

# ===========================
# Authentication Manager
# ===========================

class AuthenticationManager:
    """Authentication with all supported types."""
    
    def __init__(self, auth_config: Dict[str, Any], service_name: str = ""):
        self.config = auth_config
        self.auth_type = auth_config.get("type", "bearer_token")
        self.header = auth_config.get("header", "Authorization")
        self.service_name = service_name.upper().replace("-", "_").replace(" ", "_")
    
    async def get_auth_headers(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Get authentication headers based on configuration."""
        headers = {}
        
        # Get API key with service-specific fallback
        api_key = params.get("api_key")
        if not api_key and self.service_name:
            api_key = os.getenv(f"{self.service_name}_API_KEY")
        if not api_key:
            api_key = os.getenv("API_KEY")
        
        if not api_key:
            logger.warning("No API key found in params or environment")
            return headers
        
        if self.auth_type == "bearer_token":
            headers[self.header] = f"Bearer {api_key}"
        
        elif self.auth_type == "api_key":
            headers[self.header] = api_key
        
        elif self.auth_type == "basic_auth":
            username = params.get("username", "")
            auth_string = base64.b64encode(f"{username}:{api_key}".encode()).decode()
            headers[self.header] = f"Basic {auth_string}"
        
        elif self.auth_type == "custom":
            custom_header = self.config.get("custom_header")
            custom_prefix = self.config.get("custom_prefix", "")
            if custom_header:
                headers[custom_header] = f"{custom_prefix}{api_key}".strip()
        
        return headers

# ===========================
# Rate Limiter
# ===========================

class RateLimiter:
    """Thread-safe rate limiter with token bucket algorithm."""
    
    def __init__(self, rate_config: RateLimitInfo):
        self.config = rate_config
        self.burst_tokens = float(rate_config.burst_limit)
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
        self.tokens_per_second = rate_config.requests_per_minute / 60.0
    
    async def acquire(self, cost: int = 1) -> bool:
        """Acquire permission to make a request."""
        wait_time = 0.0
        
        async with self._lock:
            now = time.time()
            
            # Refill tokens based on time passed
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.tokens_per_second
            self.burst_tokens = min(self.config.burst_limit, self.burst_tokens + tokens_to_add)
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.burst_tokens >= cost:
                self.burst_tokens -= cost
                return True
            
            # Calculate wait time
            tokens_needed = cost - self.burst_tokens
            wait_time = tokens_needed / self.tokens_per_second
        
        # Sleep outside the lock
        if wait_time > 0:
            await asyncio.sleep(wait_time)
            async with self._lock:
                self.burst_tokens = max(0, self.burst_tokens - cost)
        
        return True

# ===========================
# Retry Manager
# ===========================

class RetryManager:
    """Retry logic with multiple backoff strategies."""
    
    def __init__(self, retry_config: RetryConfig):
        self.config = retry_config
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        if self.config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (2 ** (attempt - 1))
        elif self.config.backoff_strategy == BackoffStrategy.EXPONENTIAL_JITTER:
            delay = self.config.base_delay * (2 ** (attempt - 1))
            delay = delay * (0.5 + random.random() * 0.5)  # Add jitter
        elif self.config.backoff_strategy == BackoffStrategy.LINEAR:
            delay = self.config.base_delay * attempt
        else:  # FIXED
            delay = self.config.base_delay
        
        return min(delay, self.config.max_delay)
    
    def should_retry(self, attempt: int, status_code: Optional[int] = None, exception: Optional[Exception] = None) -> bool:
        """Determine if request should be retried."""
        if attempt >= self.config.max_attempts:
            return False
        
        if status_code and status_code in self.config.retriable_codes:
            return True
        
        if exception:
            exception_type = type(exception).__name__
            return any(exc_type in exception_type for exc_type in self.config.retriable_exceptions)
        
        return False

# ===========================
# Circuit Breaker
# ===========================

class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.half_open_calls = 0
        self._lock = asyncio.Lock()
    
    async def call_allowed(self) -> bool:
        """Check if a call is allowed through the circuit."""
        if not self.config.enabled:
            return True
        
        async with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            
            elif self.state == CircuitState.OPEN:
                # Check if timeout has elapsed
                if time.time() - self.last_failure_time >= self.config.timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    logger.debug("Circuit breaker transitioning to HALF_OPEN")
                    return True
                return False
            
            else:  # HALF_OPEN
                if self.half_open_calls < self.config.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False
    
    async def record_success(self):
        """Record a successful call."""
        if not self.config.enabled:
            return
        
        async with self._lock:
            self.failure_count = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.success_count = 0
                    logger.debug("Circuit breaker transitioning to CLOSED")
    
    async def record_failure(self):
        """Record a failed call."""
        if not self.config.enabled:
            return
        
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.success_count = 0
                logger.warning("Circuit breaker transitioning to OPEN (from HALF_OPEN)")
            
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.warning("Circuit breaker transitioning to OPEN")
    
    async def get_state(self) -> CircuitState:
        """Get current circuit state."""
        async with self._lock:
            return self.state

# ===========================
# Request Deduplicator
# ===========================

class RequestDeduplicator:
    """Prevents duplicate in-flight requests."""
    
    def __init__(self):
        self.in_flight: Dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()
    
    def _get_request_key(self, method: str, url: str, body: Optional[Dict[str, Any]]) -> str:
        """Generate unique key for request."""
        key_parts = [method, url]
        if body:
            key_parts.append(json.dumps(body, sort_keys=True))
        key_str = "|".join(key_parts)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    async def get_or_create(self, method: str, url: str, body: Optional[Dict[str, Any]]) -> Tuple[bool, Optional[asyncio.Future]]:
        """Get existing future or create new one. Returns (is_duplicate, future)."""
        request_key = self._get_request_key(method, url, body)
        
        async with self._lock:
            if request_key in self.in_flight:
                logger.debug(f"Duplicate request detected: {method} {url}")
                return True, self.in_flight[request_key]
            
            future = asyncio.Future()
            self.in_flight[request_key] = future
            return False, future
    
    async def complete(self, method: str, url: str, body: Optional[Dict[str, Any]], result: Any):
        """Mark request as complete and set result."""
        request_key = self._get_request_key(method, url, body)
        
        async with self._lock:
            if request_key in self.in_flight:
                future = self.in_flight[request_key]
                if not future.done():
                    future.set_result(result)
                del self.in_flight[request_key]
    
    async def complete_with_exception(self, method: str, url: str, body: Optional[Dict[str, Any]], exception: Exception):
        """Mark request as failed."""
        request_key = self._get_request_key(method, url, body)
        
        async with self._lock:
            if request_key in self.in_flight:
                future = self.in_flight[request_key]
                if not future.done():
                    future.set_exception(exception)
                del self.in_flight[request_key]

# ===========================
# Response Processor
# ===========================

class ResponseProcessor:
    """Process and transform API responses."""
    
    @staticmethod
    async def process_response(response: aiohttp.ClientResponse, output_schema: Optional[OutputSchema] = None, 
                               field_mapping: Optional[FieldMapping] = None, compression_config: Optional[CompressionConfig] = None) -> Dict[str, Any]:
        """Process response with content type detection and field mapping."""
        # Detect content type
        content_type = response.headers.get('Content-Type', '').lower()
        content_encoding = response.headers.get('Content-Encoding', '').lower()
        
        # Handle compression
        raw_content = await response.read()
        if compression_config and compression_config.auto_decompress:
            if content_encoding == 'gzip':
                try:
                    raw_content = gzip.decompress(raw_content)
                except Exception as e:
                    logger.warning(f"Failed to decompress gzip content: {e}")
        
        # Parse response based on content type
        if 'application/json' in content_type or 'application/hal+json' in content_type:
            try:
                response_data = json.loads(raw_content.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                text = raw_content.decode('utf-8', errors='replace')
                response_data = {"raw_response": text, "parse_error": str(e)}
        elif 'text/' in content_type:
            response_data = raw_content.decode('utf-8', errors='replace')
        elif 'application/octet-stream' in content_type or 'application/pdf' in content_type:
            response_data = {
                "content_type": content_type,
                "size_bytes": len(raw_content),
                "binary_data": base64.b64encode(raw_content).decode()
            }
        else:
            # Default to text
            try:
                response_data = raw_content.decode('utf-8', errors='replace')
            except:
                response_data = {"raw_bytes": base64.b64encode(raw_content).decode()}
        
        # Apply field mapping if configured
        if field_mapping:
            response_data = ResponseProcessor._apply_field_mapping(response_data, field_mapping)
        
        return {
            "status": "success",
            "data": response_data,
            "result": response_data,  # For backward compatibility
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": response.status
        }
    
    @staticmethod
    async def process_streaming_response(response: aiohttp.ClientResponse, chunk_size: int = 8192) -> Dict[str, Any]:
        """Process streaming response."""
        chunks = []
        total_size = 0
        
        async for chunk in response.content.iter_chunked(chunk_size):
            chunks.append(chunk)
            total_size += len(chunk)
        
        full_content = b''.join(chunks)
        
        return {
            "status": "success",
            "data": {
                "content": base64.b64encode(full_content).decode(),
                "size_bytes": total_size,
                "chunks_received": len(chunks)
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": response.status
        }
    
    @staticmethod
    def _apply_field_mapping(data: Any, mapping: FieldMapping) -> Any:
        """Apply field transformations and aliases."""
        if not isinstance(data, dict):
            return data
        
        transformed = {}
        
        for key, value in data.items():
            # Apply alias
            field_name = mapping.field_aliases.get(key, key)
            
            # Apply output transform
            if key in mapping.output_transforms:
                value = ResponseProcessor._apply_transform(value, mapping.output_transforms[key])
            
            # Recurse for nested dicts
            if isinstance(value, dict):
                value = ResponseProcessor._apply_field_mapping(value, mapping)
            elif isinstance(value, list):
                value = [ResponseProcessor._apply_field_mapping(item, mapping) if isinstance(item, dict) else item 
                        for item in value]
            
            transformed[field_name] = value
        
        return transformed
    
    @staticmethod
    def _apply_transform(value: Any, transform_name: str) -> Any:
        """Apply specific transform to a value."""
        if value is None:
            return value
            
        if transform_name == "format_date" and isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            except:
                return value
        elif transform_name == "lowercase_trim" and isinstance(value, str):
            return value.lower().strip()
        elif transform_name == "uppercase_trim" and isinstance(value, str):
            return value.upper().strip()
        elif transform_name == "format_international" and isinstance(value, str):
            # Basic phone number formatting
            digits = re.sub(r'\D', '', value)
            if len(digits) >= 10:
                return f"+{digits}"
            return value
        elif transform_name == "to_int":
            try:
                return int(float(value))
            except:
                return value
        elif transform_name == "to_float":
            try:
                return float(value)
            except:
                return value
        
        return value

# ===========================
# Monitoring System
# ===========================

class MonitoringSystem:
    """Thread-safe performance monitoring and metrics collection."""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.metrics = {
            "total_requests": 0,
            "success_count": 0,
            "error_count": 0,
            "response_times": deque(maxlen=config.max_metrics_history),
            "error_rates": deque(maxlen=config.max_metrics_history),
            "status_codes": {}
        }
        self.start_time = time.time()
        self._lock = asyncio.Lock()
    
    async def record_request(self, duration: float, success: bool, status_code: Optional[int] = None):
        """Record request metrics in a thread-safe manner."""
        if not self.config.track_response_time:
            return
        
        async with self._lock:
            self.metrics["total_requests"] += 1
            self.metrics["response_times"].append(duration)
            
            if success:
                self.metrics["success_count"] += 1
            else:
                self.metrics["error_count"] += 1
                if self.config.log_errors:
                    logger.error(f"Request failed with status: {status_code}, duration: {duration:.2f}ms")
            
            # Track status codes
            if status_code:
                self.metrics["status_codes"][status_code] = self.metrics["status_codes"].get(status_code, 0) + 1
            
            # Calculate current error rate
            total = self.metrics["total_requests"]
            error_rate = self.metrics["error_count"] / total if total > 0 else 0
            self.metrics["error_rates"].append(error_rate)
            
            # Check alerts
            self._check_alerts(duration, error_rate)
    
    def _check_alerts(self, response_time: float, error_rate: float):
        """Check if any alert thresholds are exceeded."""
        if "error_rate_threshold" in self.config.alerts:
            if error_rate > self.config.alerts["error_rate_threshold"]:
                logger.warning(f"Error rate threshold exceeded: {error_rate:.2%}")
        
        if "response_time_threshold" in self.config.alerts:
            if response_time > self.config.alerts["response_time_threshold"]:
                logger.warning(f"Response time threshold exceeded: {response_time:.2f}ms")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics in a thread-safe manner."""
        async with self._lock:
            total = self.metrics["total_requests"]
            if total == 0:
                return {"status": "no_data", "total_requests": 0}
            
            response_times = list(self.metrics["response_times"])
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            success_rate = self.metrics["success_count"] / total
            
            return {
                "total_requests": total,
                "success_count": self.metrics["success_count"],
                "error_count": self.metrics["error_count"],
                "success_rate": success_rate,
                "error_rate": 1 - success_rate,
                "avg_response_time_ms": avg_response_time,
                "min_response_time_ms": min(response_times) if response_times else 0,
                "max_response_time_ms": max(response_times) if response_times else 0,
                "uptime_seconds": time.time() - self.start_time,
                "status_codes": dict(self.metrics["status_codes"])
            }
    
    async def cleanup(self):
        """Cleanup metrics on shutdown."""
        async with self._lock:
            self.metrics["response_times"].clear()
            self.metrics["error_rates"].clear()
            self.metrics["status_codes"].clear()

# ===========================
# Caching System  
# ===========================

class CachingSystem:
    """LRU cache with intelligent invalidation."""
    
    def __init__(self, config: CachingConfig):
        self.config = config
        self.cache = OrderedDict()
        self.cache_times = {}
        self._lock = asyncio.Lock()
        
        # Normalize cache key template
        self.cache_key_template = config.cache_key_template.replace("{hash(params)}", "{hash}")
    
    async def get_cache_key(self, operation: str, params: Dict[str, Any]) -> str:
        """Generate cache key from operation and parameters."""
        # Exclude certain params from cache key
        exclude_params = self.config.cache_conditions.get("exclude_params", ["timestamp", "nonce", "background_request"])
        cache_params = {k: v for k, v in params.items() if k not in exclude_params}
        
        # Create stable hash using SHA-256 for better collision resistance
        param_str = json.dumps(cache_params, sort_keys=True)
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()
        
        return self.cache_key_template.format(operation=operation, hash=param_hash)
    
    async def get(self, cache_key: str) -> Optional[Any]:
        """Get cached response if valid."""
        if not self.config.enabled:
            return None
        
        async with self._lock:
            if cache_key not in self.cache:
                return None
            
            cache_time = self.cache_times.get(cache_key, 0)
            if time.time() - cache_time > self.config.ttl_seconds:
                # Cache expired
                del self.cache[cache_key]
                del self.cache_times[cache_key]
                return None
            
            # Move to end (LRU)
            self.cache.move_to_end(cache_key)
            return self.cache[cache_key]
    
    async def set(self, cache_key: str, value: Any):
        """Cache response with LRU eviction."""
        if not self.config.enabled:
            return
        
        async with self._lock:
            # Add/update cache entry
            self.cache[cache_key] = value
            self.cache_times[cache_key] = time.time()
            self.cache.move_to_end(cache_key)
            
            # LRU eviction
            while len(self.cache) > self.config.max_cache_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.cache_times[oldest_key]
    
    async def cleanup(self):
        """Cleanup cache on shutdown."""
        async with self._lock:
            self.cache.clear()
            self.cache_times.clear()

# ===========================
# Universal Request Node
# ===========================

class UniversalRequestNode:
    """Production-ready Universal Request Node with proper async lifecycle."""
    
    def __init__(self, config: Dict[str, Any], operations: Dict[str, Any], sandbox_timeout: Optional[int] = None):
        """Initialize with configuration."""
        self.raw_config = config
        self.raw_operations = operations
        self.sandbox_timeout = sandbox_timeout
        
        # Parse configuration
        self.config = self._parse_config(config)
        self.operations = self._parse_operations(operations)
        
        # Initialize components
        service_name = self.config.node_info.get("name", "")
        self.auth_manager = AuthenticationManager(self.config.authentication, service_name)
        self.rate_limiter = RateLimiter(self.config.rate_limiting)
        self.retry_manager = RetryManager(self.config.retry_config)
        self.monitoring = MonitoringSystem(self.config.monitoring)
        self.caching = CachingSystem(self.config.caching)
        self.circuit_breaker = CircuitBreaker(self.config.circuit_breaker)
        self.deduplicator = RequestDeduplicator()
        self.validator = ValidationEngine()
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock()
        
        logger.debug(f"UniversalRequestNode initialized for {service_name}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()
        await self.monitoring.cleanup()
        await self.caching.cleanup()
    
    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        async with self._session_lock:
            if self.session is None:
                timeout = aiohttp.ClientTimeout(
                    connect=self.config.timeouts["connect"],
                    sock_read=self.config.timeouts["read"],
                    total=self.config.timeouts["total"]
                )
                
                # Configure connector with proxy support
                connector_kwargs = {}
                if self.config.proxy.http_proxy or self.config.proxy.https_proxy:
                    connector_kwargs['trust_env'] = True
                
                connector = aiohttp.TCPConnector(**connector_kwargs)
                
                self.session = aiohttp.ClientSession(
                    timeout=timeout,
                    connector=connector
                )
    
    async def _close_session(self):
        """Close aiohttp session."""
        async with self._session_lock:
            if self.session:
                await self.session.close()
                self.session = None
    
    def _parse_config(self, config: Dict[str, Any]) -> UniversalRequestConfig:
        """Parse configuration dictionary into structured config."""
        api_config = config.get("api_config", {})
        
        return UniversalRequestConfig(
            base_url=api_config.get("base_url", ""),
            authentication=api_config.get("authentication", {}),
            default_headers=api_config.get("default_headers", {}),
            retry_config=self._parse_retry_config(api_config.get("retry_config", {})),
            rate_limiting=self._parse_rate_limiting(api_config.get("rate_limiting", {})),
            pricing=self._parse_pricing(config.get("pricing")),
            timeouts=api_config.get("timeouts", {"connect": 10.0, "read": 30.0, "total": 60.0}),
            monitoring=self._parse_monitoring(config.get("monitoring", {})),
            caching=self._parse_caching(config.get("caching", {})),
            circuit_breaker=self._parse_circuit_breaker(config.get("circuit_breaker", {})),
            proxy=self._parse_proxy(config.get("proxy", {})),
            compression=self._parse_compression(config.get("compression", {})),
            testing=self._parse_testing(config.get("testing", {})),
            documentation=self._parse_documentation(config.get("documentation", {})),
            node_info=config.get("node_info", {}),
            parameters=config.get("parameters", {}),
            outputs=config.get("outputs", {}),
            auth=config.get("auth", {}),
            error_codes=config.get("error_codes", {})
        )
    
    def _parse_operations(self, operations: Dict[str, Any]) -> Dict[str, OperationConfig]:
        """Parse operations into structured configs."""
        parsed_ops = {}
        
        for op_name, op_data in operations.items():
            # Extract path parameters from endpoint
            endpoint = op_data.get("endpoint", "/")
            path_params = set(re.findall(r'\{(\w+)\}', endpoint))
            
            parsed_ops[op_name] = OperationConfig(
                method=op_data.get("method", "GET"),
                endpoint=endpoint,
                description=op_data.get("description", ""),
                required_params=op_data.get("required_params", []),
                optional_params=op_data.get("optional_params", []),
                body_parameters=op_data.get("body_parameters", []),
                path_parameters=path_params,
                output_schema=self._parse_output_schema(op_data.get("output_schema")),
                array_templates=self._parse_array_templates(op_data.get("array_templates", {})),
                validation_rules=self._parse_validation_rules(op_data.get("validation_rules", {})),
                parameter_dependencies=self._parse_dependencies(op_data.get("parameter_dependencies", [])),
                rate_limit_cost=op_data.get("rate_limit_cost", 1),
                cache_ttl=op_data.get("cache_ttl", 0),
                webhook_support=self._parse_webhook_config(op_data.get("webhook_support")),
                pagination=self._parse_pagination_config(op_data.get("pagination")),
                field_mapping=self._parse_field_mapping(op_data.get("field_mapping")),
                auth=op_data.get("auth", {}),
                examples=op_data.get("examples", []),
                display_name=op_data.get("display_name", op_name.replace("_", " ").title()),
                group=op_data.get("group", "General"),
                tags=op_data.get("tags", []),
                deprecated=op_data.get("deprecated", False),
                response_type=op_data.get("response_type", "object"),
                streaming_supported=op_data.get("streaming_supported", False)
            )
        
        return parsed_ops
    
    def _parse_retry_config(self, retry_data: Dict[str, Any]) -> RetryConfig:
        """Parse retry configuration."""
        backoff = retry_data.get("backoff", "exponential_jitter")
        try:
            backoff_strategy = BackoffStrategy(backoff)
        except ValueError:
            logger.warning(f"Invalid backoff strategy '{backoff}', using exponential_jitter")
            backoff_strategy = BackoffStrategy.EXPONENTIAL_JITTER
        
        return RetryConfig(
            max_attempts=retry_data.get("max_attempts", 3),
            backoff_strategy=backoff_strategy,
            base_delay=retry_data.get("base_delay", 1.0),
            max_delay=retry_data.get("max_delay", 60.0),
            jitter=retry_data.get("jitter", True),
            retriable_codes=retry_data.get("retriable_codes", [429, 500, 502, 503, 504]),
            retriable_exceptions=retry_data.get("retriable_exceptions", ["ClientTimeout", "ClientConnectorError"]),
            timeout_ms=retry_data.get("timeout_ms", 30000)
        )
    
    def _parse_rate_limiting(self, rate_data: Dict[str, Any]) -> RateLimitInfo:
        """Parse rate limiting configuration."""
        return RateLimitInfo(
            requests_per_minute=rate_data.get("requests_per_minute", 300),
            requests_per_second=rate_data.get("requests_per_second"),
            burst_limit=rate_data.get("burst_size", rate_data.get("burst_limit", 30)),
            cost_per_request=rate_data.get("cost_per_request"),
            quota_type=rate_data.get("quota_type", "requests")
        )
    
    def _parse_pricing(self, pricing_data: Optional[Dict[str, Any]]) -> Optional[PricingInfo]:
        """Parse pricing information."""
        if not pricing_data:
            return None
        
        return PricingInfo(
            cost_per_1k_tokens=pricing_data.get("cost_per_1k_tokens"),
            cost_per_request=pricing_data.get("cost_per_request"),
            billing_unit=pricing_data.get("billing_unit", "requests"),
            free_tier_limit=pricing_data.get("free_tier_limit")
        )
    
    def _parse_monitoring(self, monitoring_data: Dict[str, Any]) -> MonitoringConfig:
        """Parse monitoring configuration."""
        return MonitoringConfig(
            track_response_time=monitoring_data.get("track_response_time", True),
            log_errors=monitoring_data.get("log_errors", True),
            metrics=monitoring_data.get("metrics", ["success_rate", "avg_response_time", "error_count"]),
            alerts=monitoring_data.get("alerts", {}),
            max_metrics_history=monitoring_data.get("max_metrics_history", 1000)
        )
    
    def _parse_caching(self, caching_data: Dict[str, Any]) -> CachingConfig:
        """Parse caching configuration."""
        return CachingConfig(
            enabled=caching_data.get("enabled", False),
            cache_key_template=caching_data.get("cache_key_template", "{operation}:{hash}"),
            ttl_seconds=caching_data.get("ttl_seconds", 300),
            max_cache_size=caching_data.get("max_cache_size", 1000),
            cache_conditions=caching_data.get("cache_conditions", {})
        )
    
    def _parse_circuit_breaker(self, cb_data: Dict[str, Any]) -> CircuitBreakerConfig:
        """Parse circuit breaker configuration."""
        return CircuitBreakerConfig(
            enabled=cb_data.get("enabled", False),
            failure_threshold=cb_data.get("failure_threshold", 5),
            success_threshold=cb_data.get("success_threshold", 2),
            timeout_seconds=cb_data.get("timeout_seconds", 60),
            half_open_max_calls=cb_data.get("half_open_max_calls", 3)
        )
    
    def _parse_proxy(self, proxy_data: Dict[str, Any]) -> ProxyConfig:
        """Parse proxy configuration."""
        return ProxyConfig(
            http_proxy=proxy_data.get("http_proxy"),
            https_proxy=proxy_data.get("https_proxy"),
            no_proxy=proxy_data.get("no_proxy")
        )
    
    def _parse_compression(self, compression_data: Dict[str, Any]) -> CompressionConfig:
        """Parse compression configuration."""
        return CompressionConfig(
            enabled=compression_data.get("enabled", True),
            accept_encoding=compression_data.get("accept_encoding", ["gzip", "deflate"]),
            auto_decompress=compression_data.get("auto_decompress", True)
        )
    
    def _parse_testing(self, testing_data: Dict[str, Any]) -> TestingConfig:
        """Parse testing configuration."""
        return TestingConfig(
            sandbox_mode=testing_data.get("sandbox_mode", False),
            test_credentials_param=testing_data.get("test_credentials_param"),
            validation_endpoint=testing_data.get("validation_endpoint")
        )
    
    def _parse_documentation(self, doc_data: Dict[str, Any]) -> DocumentationConfig:
        """Parse documentation configuration."""
        return DocumentationConfig(
            api_docs_url=doc_data.get("api_docs_url"),
            setup_guide=doc_data.get("setup_guide"),
            troubleshooting=doc_data.get("troubleshooting"),
            changelog=doc_data.get("changelog")
        )
    
    def _parse_output_schema(self, schema_data: Optional[Dict[str, Any]]) -> Optional[OutputSchema]:
        """Parse output schema configuration."""
        if not schema_data:
            return None
        
        return OutputSchema(
            success_schema=schema_data.get("success", {}),
            error_schema=schema_data.get("error", {}),
            status_codes=schema_data.get("status_codes", {})
        )
    
    def _parse_array_templates(self, templates_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse array templates - handle both list and dict formats."""
        templates = {}
        
        for key, template_data in templates_data.items():
            if isinstance(template_data, list):
                # Legacy format: list of template objects
                templates[key] = template_data
            elif isinstance(template_data, dict):
                # New format: dict with template, description, etc.
                if "template" in template_data:
                    templates[key] = ArrayTemplate(
                        template=template_data.get("template", []),
                        description=template_data.get("description", ""),
                        min_items=template_data.get("min_items"),
                        max_items=template_data.get("max_items"),
                        item_validation=self._parse_validation_rule(template_data.get("item_validation"))
                    )
                else:
                    # Nested templates (e.g., person.email_addresses)
                    templates[key] = template_data
        
        return templates
    
    def _parse_validation_rules(self, rules_data: Dict[str, Any]) -> Dict[str, ValidationRule]:
        """Parse validation rules."""
        rules = {}
        for key, rule_data in rules_data.items():
            parsed_rule = self._parse_validation_rule(rule_data)
            if parsed_rule:
                rules[key] = parsed_rule
        return rules
    
    def _parse_validation_rule(self, rule_data: Optional[Dict[str, Any]]) -> Optional[ValidationRule]:
        """Parse a single validation rule."""
        if not rule_data:
            return None
        
        pattern_type_str = rule_data.get("pattern_type", "custom")
        try:
            pattern_type = ValidationPattern(pattern_type_str)
        except ValueError:
            logger.warning(f"Invalid pattern type '{pattern_type_str}', using custom")
            pattern_type = ValidationPattern.CUSTOM
        
        return ValidationRule(
            pattern=rule_data.get("pattern", ""),
            message=rule_data.get("message", "Invalid format"),
            pattern_type=pattern_type,
            min_length=rule_data.get("min_length") or rule_data.get("minLength"),
            max_length=rule_data.get("max_length") or rule_data.get("maxLength"),
            min_value=rule_data.get("min_value") or rule_data.get("minimum"),
            max_value=rule_data.get("max_value") or rule_data.get("maximum"),
            required=rule_data.get("required", False)
        )
    
    def _parse_dependencies(self, deps_data: List[Dict[str, Any]]) -> List[ParameterDependency]:
        """Parse parameter dependencies."""
        dependencies = []
        for dep_data in deps_data:
            dependencies.append(ParameterDependency(
                when_field=dep_data.get("when_field", ""),
                when_value=dep_data.get("when_value"),
                then_require=dep_data.get("then_require", []),
                then_optional=dep_data.get("then_optional", []),
                require_one_of=dep_data.get("require_one_of", []),
                mutually_exclusive=dep_data.get("mutually_exclusive", [])
            ))
        return dependencies
    
    def _parse_webhook_config(self, webhook_data: Optional[Dict[str, Any]]) -> Optional[WebhookConfig]:
        """Parse webhook configuration."""
        if not webhook_data:
            return None
        
        return WebhookConfig(
            callback_param=webhook_data.get("callback_param"),
            supported_events=webhook_data.get("supported_events", []),
            retry_policy=webhook_data.get("retry_policy", {})
        )
    
    def _parse_pagination_config(self, pagination_data: Optional[Dict[str, Any]]) -> Optional[PaginationConfig]:
        """Parse pagination configuration."""
        if not pagination_data:
            return None
        
        pagination_type_str = pagination_data.get("type", "none")
        try:
            pagination_type = PaginationType(pagination_type_str)
        except ValueError:
            logger.warning(f"Invalid pagination type '{pagination_type_str}', using none")
            pagination_type = PaginationType.NONE
        
        return PaginationConfig(
            type=pagination_type,
            page_param=pagination_data.get("page_param", "page"),
            cursor_param=pagination_data.get("cursor_param", "cursor"),
            size_param=pagination_data.get("size_param", "per_page"),
            default_size=pagination_data.get("default_size", 25),
            max_size=pagination_data.get("max_size", 100),
            total_pages_field=pagination_data.get("total_pages_field"),
            total_records_field=pagination_data.get("total_records_field"),
            next_cursor_field=pagination_data.get("next_cursor_field"),
            has_more_field=pagination_data.get("has_more_field")
        )
    
    def _parse_field_mapping(self, mapping_data: Optional[Dict[str, Any]]) -> Optional[FieldMapping]:
        """Parse field mapping configuration."""
        if not mapping_data:
            return None
        
        return FieldMapping(
            input_transforms=mapping_data.get("input_transforms", {}),
            output_transforms=mapping_data.get("output_transforms", {}),
            field_aliases=mapping_data.get("field_aliases", {})
        )
    
    def get_schema(self):
        """Get node schema for UI integration."""
        NodeSchema, NodeParameter, NodeParameterType = import_base_node()
        
        # Build parameters from config
        parameters = []
        
        # Add operation parameter
        op_param = NodeParameter(
            name="operation",
            type=NodeParameterType.STRING,
            description="The operation to perform",
            required=True,
            enum=list(self.operations.keys())
        )
        parameters.append(op_param)
        
        # Add parameters from config
        for param_name, param_config in self.config.parameters.items():
            if param_name == "operation":
                continue
            
            param_type = self._get_parameter_type(param_config.get("type", "string"))
            
            param = NodeParameter(
                name=param_name,
                type=param_type,
                description=param_config.get("description", ""),
                required=param_config.get("required", False),
                default=param_config.get("default"),
                enum=param_config.get("enum"),
                validation=param_config.get("validation", {})
            )
            parameters.append(param)
        
        return NodeSchema(
            node_type=self.config.node_info.get("name", "universal"),
            version=self.config.node_info.get("version", "2.1.0"),
            description=self.config.node_info.get("description", "Universal API integration"),
            parameters=parameters,
            outputs={
                "status": NodeParameterType.STRING,
                "data": NodeParameterType.ANY,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "timestamp": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "resource_id": NodeParameterType.STRING,
                "total_pages": NodeParameterType.NUMBER,
                "total_records": NodeParameterType.NUMBER
            }
        )
    
    def _get_parameter_type(self, type_str: str):
        """Convert string type to NodeParameterType."""
        NodeSchema, NodeParameter, NodeParameterType = import_base_node()
        
        type_mapping = {
            "string": NodeParameterType.STRING,
            "integer": NodeParameterType.NUMBER,
            "number": NodeParameterType.NUMBER,
            "boolean": NodeParameterType.BOOLEAN,
            "array": NodeParameterType.ARRAY,
            "object": NodeParameterType.OBJECT
        }
        
        return type_mapping.get(type_str, NodeParameterType.STRING)
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parameter validation with all new features."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise ValueError("Operation is required")
        
        if operation not in self.operations:
            available = ", ".join(sorted(self.operations.keys()))
            raise ValueError(f"Unknown operation: {operation}. Available: {available}")
        
        op_config = self.operations[operation]
        errors = []
        
        # Validate required parameters
        for param in op_config.required_params:
            if param not in params or params[param] is None or params[param] == "":
                errors.append(f"Parameter '{param}' is required for operation '{operation}'")
        
        # Validate with rules
        for param_name, value in params.items():
            if param_name in op_config.validation_rules:
                rule = op_config.validation_rules[param_name]
                is_valid, error_msg = self.validator.validate_parameter(value, rule)
                if not is_valid:
                    errors.append(f"Parameter '{param_name}': {error_msg}")
        
        # Validate dependencies
        dep_errors = self.validator.validate_dependencies(params, op_config.parameter_dependencies)
        errors.extend(dep_errors)
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return params
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with timeout and proper error handling."""
        try:
            # Apply overall timeout
            return await asyncio.wait_for(
                self._execute_internal(node_data),
                timeout=self.config.timeouts["total"]
            )
        except asyncio.TimeoutError:
            logger.error(f"Request timeout after {self.config.timeouts['total']}s")
            return {
                "status": "error",
                "error": f"Request timeout after {self.config.timeouts['total']} seconds",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _execute_internal(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal execution with all advanced features."""
        start_time = time.time()
        
        try:
            # Validate parameters
            params = self.validate_custom(node_data)
            operation = params["operation"]
            op_config = self.operations[operation]
            
            # Check circuit breaker
            if not await self.circuit_breaker.call_allowed():
                circuit_state = await self.circuit_breaker .get_state()
                return {
                    "status": "error",
                    "error": f"Circuit breaker is {circuit_state.value}. Service temporarily unavailable.",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "circuit_state": circuit_state.value
                }
            
            # Check cache first (only for GET requests with caching enabled)
            if op_config.method == "GET" and op_config.cache_ttl > 0:
                cache_key = await self.caching.get_cache_key(operation, params)
                cached_response = await self.caching.get(cache_key)
                if cached_response:
                    logger.debug(f"Cache hit for {operation}")
                    return cached_response
            
            # Ensure session exists
            await self._ensure_session()
            
            # Rate limiting
            await self.rate_limiter.acquire(op_config.rate_limit_cost)
            
            # Build request
            url = self._build_url(op_config.endpoint, params, op_config)
            headers = await self._build_headers(params, op_config)
            body = self._build_body(params, op_config)
            
            logger.debug(f"Executing {op_config.method} {url}")
            
            # Check for duplicate requests
            is_duplicate, future = await self.deduplicator.get_or_create(op_config.method, url, body)
            
            if is_duplicate and future:
                # Wait for the in-flight request to complete
                try:
                    response_data = await future
                    logger.debug(f"Using deduplicated response for {op_config.method} {url}")
                    return response_data
                except Exception as e:
                    logger.warning(f"Deduplicated request failed: {e}")
                    # Fall through to make new request
            
            try:
                # Execute request with retry logic
                response_data = await self._execute_with_retry(
                    op_config.method, url, headers, body, params, op_config
                )
                
                # Complete deduplication
                await self.deduplicator.complete(op_config.method, url, body, response_data)
                
                # Record circuit breaker success
                await self.circuit_breaker.record_success()
                
                # Cache response if applicable
                if op_config.cache_ttl > 0:
                    cache_key = await self.caching.get_cache_key(operation, params)
                    await self.caching.set(cache_key, response_data)
                
                # Record metrics
                duration = (time.time() - start_time) * 1000
                await self.monitoring.record_request(duration, True, response_data.get("status_code"))
                
                return response_data
            
            except Exception as e:
                # Complete deduplication with exception
                await self.deduplicator.complete_with_exception(op_config.method, url, body, e)
                raise
            
        except ValueError as e:
            # Validation errors
            duration = (time.time() - start_time) * 1000
            await self.monitoring.record_request(duration, False)
            
            logger.error(f"Validation error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_type": "validation_error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            # All other errors
            duration = (time.time() - start_time) * 1000
            await self.monitoring.record_request(duration, False)
            await self.circuit_breaker.record_failure()
            
            logger.error(f"Request execution failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _build_url(self, endpoint: str, params: Dict[str, Any], op_config: OperationConfig) -> str:
        """Build request URL with path and query parameters."""
        url = self.config.base_url.rstrip('/') + endpoint
        
        # Replace path parameters
        for param_name in op_config.path_parameters:
            if param_name in params:
                placeholder = f"{{{param_name}}}"
                url = url.replace(placeholder, str(params[param_name]))
        
        # Build query parameters
        query_params = {}
        for key, value in params.items():
            # Skip operation, path params, and body params
            if key == "operation":
                continue
            if key in op_config.path_parameters:
                continue
            if key in op_config.body_parameters:
                continue
            
            # Include query params
            if value is not None and value != "":
                query_params[key] = value
        
        # Add query string
        if query_params:
            url += '?' + urlencode(query_params)
        
        return url
    
    async def _build_headers(self, params: Dict[str, Any], op_config: OperationConfig) -> Dict[str, str]:
        """Build request headers including authentication."""
        headers = self.config.default_headers.copy()
        
        # Add authentication headers
        auth_headers = await self.auth_manager.get_auth_headers(params)
        headers.update(auth_headers)
        
        # Add compression headers
        if self.config.compression.enabled:
            headers['Accept-Encoding'] = ', '.join(self.config.compression.accept_encoding)
        
        return headers
    
    def _build_body(self, params: Dict[str, Any], op_config: OperationConfig) -> Optional[Dict[str, Any]]:
        """Build request body from parameters with input transforms."""
        if op_config.method in ["GET", "DELETE", "HEAD"] or not op_config.body_parameters:
            return None
        
        body = {}
        for param in op_config.body_parameters:
            if param in params and params[param] is not None:
                value = params[param]
                
                # Apply input transforms if configured
                if op_config.field_mapping and param in op_config.field_mapping.input_transforms:
                    transform = op_config.field_mapping.input_transforms[param]
                    value = ResponseProcessor._apply_transform(value, transform)
                
                body[param] = value
        
        return body if body else None
    
    async def _execute_with_retry(self, method: str, url: str, headers: Dict[str, str], 
                                  body: Optional[Dict[str, Any]], params: Dict[str, Any],
                                  op_config: OperationConfig) -> Any:
        """Execute request with retry logic and proper error handling."""
        last_exception = None
        last_status = None
        last_error_text = None
        
        for attempt in range(1, self.retry_manager.config.max_attempts + 1):
            try:
                if not self.session:
                    raise RuntimeError("Session not initialized")
                
                # Configure proxy for this request
                proxy = None
                if url.startswith('https://') and self.config.proxy.https_proxy:
                    proxy = self.config.proxy.https_proxy
                elif url.startswith('http://') and self.config.proxy.http_proxy:
                    proxy = self.config.proxy.http_proxy
                
                # Make request
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body,
                    proxy=proxy
                ) as response:
                    last_status = response.status
                    
                    # Success
                    if response.status < 400:
                        # Check if streaming is requested
                        if op_config.streaming_supported and params.get("stream", False):
                            return await ResponseProcessor.process_streaming_response(response)
                        else:
                            return await ResponseProcessor.process_response(
                                response, op_config.output_schema, op_config.field_mapping, 
                                self.config.compression
                            )
                    
                    # Client/Server error
                    error_text = await response.text()
                    last_error_text = error_text
                    
                    # Log full error before potential truncation
                    logger.error(f"Request failed with status {response.status}: {error_text}")
                    
                    # Check if should retry
                    if not self.retry_manager.should_retry(attempt, response.status):
                        # Extract pagination info if present
                        extra_info = {}
                        try:
                            error_json = json.loads(error_text)
                            if op_config.pagination:
                                if op_config.pagination.total_pages_field:
                                    extra_info["total_pages"] = error_json.get(op_config.pagination.total_pages_field)
                                if op_config.pagination.total_records_field:
                                    extra_info["total_records"] = error_json.get(op_config.pagination.total_records_field)
                        except:
                            pass
                        
                        error_msg = self.config.error_codes.get(str(response.status), error_text)
                        return {
                            "status": "error",
                            "error": error_msg,
                            "error_details": error_text[:500],  # Truncate for response
                            "status_code": response.status,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            **extra_info
                        }
                    
                    # Wait before retry
                    if attempt < self.retry_manager.config.max_attempts:
                        delay = self.retry_manager.calculate_delay(attempt)
                        logger.debug(f"Retrying request in {delay:.2f}s (attempt {attempt})")
                        await asyncio.sleep(delay)
            
            except aiohttp.ClientError as e:
                last_exception = e
                logger.error(f"Client error on attempt {attempt}: {type(e).__name__}: {str(e)}")
                
                # Check if should retry
                if not self.retry_manager.should_retry(attempt, exception=e):
                    raise
                
                # Wait before retry
                if attempt < self.retry_manager.config.max_attempts:
                    delay = self.retry_manager.calculate_delay(attempt)
                    logger.debug(f"Retrying after error: {type(e).__name__} in {delay:.2f}s (attempt {attempt})")
                    await asyncio.sleep(delay)
            
            except Exception as e:
                # Non-retriable errors
                logger.error(f"Non-retriable error: {type(e).__name__}: {str(e)}")
                raise
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        
        return {
            "status": "error",
            "error": f"Request failed after {self.retry_manager.config.max_attempts} attempts",
            "error_details": last_error_text[:500] if last_error_text else None,
            "status_code": last_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_operation_config(self, operation: str) -> Optional[OperationConfig]:
        """Get configuration for a specific operation."""
        return self.operations.get(operation)
    
    def get_base_config(self) -> UniversalRequestConfig:
        """Get the base configuration."""
        return self.config
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        metrics = await self.monitoring.get_metrics()
        circuit_state = await self.circuit_breaker.get_state()
        metrics["circuit_breaker_state"] = circuit_state.value
        return metrics
    
    def get_array_template(self, operation: str, parameter: str) -> Optional[Any]:
        """Get array template for a parameter in an operation."""
        op_config = self.operations.get(operation)
        if not op_config:
            return None
        
        return op_config.array_templates.get(parameter)
    
    def get_validation_rules(self, operation: str) -> Dict[str, ValidationRule]:
        """Get validation rules for an operation."""
        op_config = self.operations.get(operation)
        if not op_config:
            return {}
        
        return op_config.validation_rules
    
    def list_operations(self) -> List[str]:
        """Get list of all available operations."""
        return list(self.operations.keys())
    
    def get_operation_details(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an operation."""
        op_config = self.operations.get(operation)
        if not op_config:
            return None
        
        return {
            "name": operation,
            "display_name": op_config.display_name,
            "method": op_config.method,
            "endpoint": op_config.endpoint,
            "description": op_config.description,
            "required_params": op_config.required_params,
            "optional_params": op_config.optional_params,
            "body_parameters": op_config.body_parameters,
            "path_parameters": list(op_config.path_parameters),
            "group": op_config.group,
            "tags": op_config.tags,
            "deprecated": op_config.deprecated,
            "streaming_supported": op_config.streaming_supported,
            "rate_limit_cost": op_config.rate_limit_cost,
            "cache_ttl": op_config.cache_ttl,
            "examples": op_config.examples
        }

# Export the node
__all__ = [
    "UniversalRequestNode", 
    "UniversalRequestConfig", 
    "OperationConfig",
    "AuthType",
    "BackoffStrategy",
    "PaginationType",
    "ValidationPattern",
    "CircuitState"
]