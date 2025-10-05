# Enhanced UniversalRequestNode Template Guide v2.0

**Complete Template with ALL Advanced Features**

This guide includes ALL 13 enhancements for production-ready nodes with:
- Operation-specific output schemas
- Array templates for complex inputs  
- Parameter dependencies & conditional fields
- Advanced validation patterns
- Rate limiting & pricing info
- Webhook support & pagination
- Field mapping & transforms
- Performance monitoring & caching

## 📋 Complete File Structure Checklist

### 1. File Header & Imports ✅
```python
#!/usr/bin/env python3
"""
[NodeName] Node - Pure config-driven implementation using UniversalRequestNode
Configuration is embedded directly in the node - no separate config.json needed
"""

import logging
from typing import Dict, Any, Optional

# Standard BaseNode imports with try/except pattern
try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        from  base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# UniversalRequestNode import with try/except pattern
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from .universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)
```

### 2. Class Declaration ✅
```python
class [VendorName]Node(BaseNode):
    """
    Pure config-driven [Vendor] node with embedded configuration.
    All operations are handled by UniversalRequestNode based on this config.
    """
```

### 3. CONFIG Dictionary - Complete Structure ✅

#### 3.1 Node Metadata (node_info) - REQUIRED
```python
CONFIG = {
    "node_info": {
        "name": "[lowercase_vendor_name]",                    # REQUIRED
        "display_name": "[Proper Vendor Name]",              # REQUIRED
        "description": "[Comprehensive description...]",      # REQUIRED
        "category": "[api|ai|finance|communication|etc]",    # REQUIRED
        "vendor": "[vendor_name]",                           # REQUIRED
        "version": "1.0.0",                                  # REQUIRED
        "author": "ACT Workflow",                            # REQUIRED
        "tags": ["tag1", "tag2", "tag3"],                   # REQUIRED - Array
        "documentation_url": "https://api.vendor.com/docs", # REQUIRED
        "icon": "https://cdn.vendor.com/icon.svg",          # OPTIONAL
        "color": "#hexcolor",                                # OPTIONAL
        "created_at": "2025-08-25T00:00:00Z",              # REQUIRED - ISO format
        "updated_at": "2025-08-25T00:00:00Z"               # REQUIRED - ISO format
    },
```

#### 3.2 API Configuration (api_config) - REQUIRED
```python
    "api_config": {
        "base_url": "https://api.vendor.com/v1",            # REQUIRED
        "authentication": {                                  # REQUIRED
            "type": "bearer_token|api_key|basic_auth|custom|oauth2|aws_signature", # REQUIRED
            "header": "Authorization|X-API-Key|etc",        # REQUIRED
            "key": None,                                     # OPTIONAL - for API key auth
            "secret": None,                                  # OPTIONAL - for basic/oauth auth
            "token": None,                                   # OPTIONAL - static token
            "refresh_url": None,                            # OPTIONAL - for token refresh
            "refresh_threshold": 0.8                        # OPTIONAL - when to refresh token
        },
        "default_headers": {                                # REQUIRED - Even if empty
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ACT-Workflow/1.0"
        },
        "retry_config": {                                   # REQUIRED
            "max_attempts": 3,                              # REQUIRED
            "backoff": "exponential|linear|fixed|custom",   # REQUIRED
            "base_delay": 1.0,                             # OPTIONAL - initial delay
            "max_delay": 60.0,                             # OPTIONAL - max delay
            "jitter": True,                                # OPTIONAL - add randomness
            "retriable_codes": [429, 500, 502, 503, 504], # REQUIRED
            "retriable_exceptions": [                       # OPTIONAL
                "aiohttp.ClientTimeout", 
                "aiohttp.ClientConnectorError"
            ]
        },
        "rate_limiting": {                                  # REQUIRED
            "requests_per_second": 10.0,                   # REQUIRED - adjust per vendor
            "burst_size": 20,                              # REQUIRED
            "adaptive": True,                              # OPTIONAL - adaptive rate limiting
            "queue_timeout": 30.0                          # OPTIONAL - queue timeout
        },
        "timeouts": {                                       # REQUIRED
            "connect": 10.0,                               # REQUIRED
            "read": 30.0,                                  # REQUIRED
            "total": 60.0                                  # REQUIRED
        },
        "circuit_breaker": {                               # OPTIONAL - for resilience
            "failure_threshold": 5,                        # OPTIONAL - failures before opening
            "recovery_timeout": 60.0,                      # OPTIONAL - time before retry
            "expected_failure_rate": 0.5                   # OPTIONAL - expected failure rate
        },
        "pagination": {                                    # OPTIONAL - if API supports pagination
            "type": "none|offset|cursor|link|token|page",  # OPTIONAL - pagination type
            "page_param": "page",                          # OPTIONAL - page parameter name
            "size_param": "limit",                         # OPTIONAL - size parameter name
            "offset_param": "offset",                      # OPTIONAL - offset parameter name
            "cursor_param": "cursor",                      # OPTIONAL - cursor parameter name
            "token_param": "next_token",                   # OPTIONAL - token parameter name
            "max_pages": 100,                              # OPTIONAL - max pages to fetch
            "default_size": 20                             # OPTIONAL - default page size
        },
        "environment": "production"                        # OPTIONAL - environment identifier
    },
```

#### 3.3 Parameters Definition (parameters) - REQUIRED
```python
    "parameters": {
        # ALWAYS include these base parameters
        "api_key": {                                        # Authentication parameter
            "type": "string",
            "description": "[Vendor] API key",
            "required": True,
            "sensitive": True,
            "group": "Authentication",
            "validation": {
                "pattern": "^[pattern]$",  # Vendor-specific pattern
                "minLength": 10
            }
        },
        "operation": {                                      # Operation selector
            "type": "string",
            "description": "The [vendor] operation to perform",
            "required": True,
            "group": "Operation",
            "enum": ["op1", "op2", "op3"]  # List all operations
        },
        
        # Add vendor-specific parameters with complete metadata
        "parameter_name": {
            "type": "string|number|array|object|boolean",
            "description": "Clear description of parameter",
            "required": true|false,
            "default": "default_value",  # If applicable
            "group": "GroupName",  # Logical grouping
            "examples": ["example1", "example2"],
            "validation": {  # If needed
                "enum": ["val1", "val2"],
                "minimum": 0,
                "maximum": 100,
                "pattern": "^regex$",
                "minLength": 1,
                "maxLength": 100
            }
        }
        # ... more parameters
    },
```

#### 3.4 Output Definitions (outputs) - REQUIRED
```python
    "outputs": {
        "success": {
            "type": "object",
            "description": "Successful [vendor] API response",
            "properties": {
                "status": {"type": "string", "enum": ["success"]},
                "data": {"type": "object", "description": "Response data"},
                "result": {"type": "object", "description": "Operation result"}
                # Add vendor-specific output properties
            }
        },
        "error": {
            "type": "object",
            "description": "Error response", 
            "properties": {
                "status": {"type": "string", "enum": ["error"]},
                "error": {"type": "string", "description": "Error message"},
                "error_code": {"type": "string", "description": "Error code"}
            }
        }
    },
```

#### 3.5 Legacy Auth Section (auth) - OPTIONAL BUT RECOMMENDED
```python
    "auth": {
        "operation_name": {
            "required_env_keys": ["VENDOR_API_KEY"],
            "optional_env_keys": ["VENDOR_ORG_ID"]
        }
        # ... for each operation
    },
```

#### 3.6 Error Codes (error_codes) - REQUIRED
```python
    "error_codes": {
        "400": "Bad Request - Invalid parameters",
        "401": "Unauthorized - Invalid API key", 
        "403": "Forbidden - Insufficient permissions",
        "404": "Not Found - Resource not found",
        "429": "Too Many Requests - Rate limit exceeded",
        "500": "Internal Server Error - Server error",
        "502": "Bad Gateway - Service temporarily unavailable",
        "503": "Service Unavailable - Service overloaded"
        # Add vendor-specific error codes
    }
}
```

### 4. OPERATIONS Dictionary - Complete Structure ✅

```python
OPERATIONS = {
    "operation_name": {
        "method": "GET|POST|PUT|PATCH|DELETE",              # REQUIRED
        "endpoint": "/api/endpoint/path",                   # REQUIRED
        "required_params": ["param1", "param2"],           # REQUIRED - Array (empty if none)
        "optional_params": ["param3", "param4"],           # REQUIRED - Array (empty if none)
        "display_name": "Human Readable Name",             # REQUIRED
        "description": "What this operation does",         # REQUIRED
        "group": "API Group Name",                         # REQUIRED
        "rate_limit_cost": 1,                             # REQUIRED - Integer
        "cache_ttl": 0,                                   # REQUIRED - Seconds (0 = no cache)
        "response_type": "object|array|string",           # REQUIRED
        "auth": {                                         # REQUIRED - Per-operation auth
            "required_env_keys": ["VENDOR_API_KEY"],      # REQUIRED
            "optional_env_keys": ["VENDOR_ORG_ID"],       # REQUIRED (empty if none)
            "required_params": ["api_key"],               # REQUIRED
            "auth_type": "bearer_token|api_key|basic",    # REQUIRED
            "auth_description": "Auth requirement desc"   # REQUIRED
        },
        "examples": [                                     # REQUIRED - Array
            {
                "name": "Example name",
                "input": {
                    "param1": "value1",
                    "param2": "value2"
                }
            }
        ]
    }
    # ... more operations
}
```

### 5. Constructor (__init__) ✅
```python
def __init__(self, sandbox_timeout: Optional[int] = None):
    super().__init__(sandbox_timeout=sandbox_timeout)
    
    # Create UniversalRequestNode with api_config section
    self.universal_node = UniversalRequestNode(self.CONFIG["api_config"])
```

### 6. Schema Method (get_schema) ✅
```python
def get_schema(self) -> NodeSchema:
    """Return basic schema."""
    return NodeSchema(
        node_type="[vendor_name]",
        version="1.0.0", 
        description="[Vendor] API integration with embedded configuration",
        parameters=[
            # Core parameters that ALL nodes need
            NodeParameter(
                name="operation",
                type=NodeParameterType.STRING,
                description="Operation to perform",
                required=True,
                enum=list(self.OPERATIONS.keys())
            ),
            NodeParameter(
                name="api_key", 
                type=NodeParameterType.SECRET,
                description="[Vendor] API key",
                required=True
            ),
            # Add other essential parameters
            # Don't duplicate ALL parameters - just the key ones
        ],
        outputs={
            "status": NodeParameterType.STRING,
            "result": NodeParameterType.ANY,
            "error": NodeParameterType.STRING,
            # Add vendor-specific outputs
        }
    )
```

### 7. Execute Method ✅
```python
async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute operation using UniversalRequestNode.
    """
    try:
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Validation
        if not operation:
            return {
                "status": "error",
                "error": "Operation is required",
                "result": None
            }
        
        if operation not in self.OPERATIONS:
            return {
                "status": "error", 
                "error": f"Unknown operation: {operation}",
                "result": None
            }
        
        # Get operation config
        op_config = self.OPERATIONS[operation]
        
        # Prepare request data
        request_data = self._prepare_request_data(operation, params)
        
        # Make request using UniversalRequestNode
        # Authentication parameter mapping based on auth type:
        request_kwargs = {}
        
        if self.CONFIG["api_config"]["authentication"]["type"] == "bearer_token":
            request_kwargs["token"] = params.get("api_key")
        elif self.CONFIG["api_config"]["authentication"]["type"] == "api_key":
            request_kwargs["api_key"] = params.get("api_key")
        elif self.CONFIG["api_config"]["authentication"]["type"] == "basic_auth":
            request_kwargs["username"] = params.get("username")
            request_kwargs["password"] = params.get("password")
        elif self.CONFIG["api_config"]["authentication"]["type"] == "oauth2":
            request_kwargs["token"] = params.get("access_token")
        
        # Add other parameters
        request_kwargs.update(params)
        
        result = await self.universal_node.request(
            method=op_config["method"],
            endpoint=op_config["endpoint"],
            data=request_data if op_config["method"] in ["POST", "PUT", "PATCH"] else None,
            params=request_data if op_config["method"] == "GET" else None,
            **request_kwargs
        )
        
        # Process result
        return self._process_result(operation, result)
        
    except Exception as e:
        logger.error(f"[Vendor] node error: {str(e)}")
        return {
            "status": "error", 
            "error": str(e),
            "result": None
        }
```

### 8. Helper Methods ✅

#### 8.1 Request Data Preparation
```python
def _prepare_request_data(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare request data based on operation."""
    data = {}
    
    if operation == "operation_name":
        # Build request data for this operation
        data = {
            "param1": params.get("param1"),
            "param2": params.get("param2", "default_value")
        }
        
        # Add optional parameters conditionally
        if params.get("optional_param"):
            data["optional_param"] = params.get("optional_param")
    
    elif operation == "another_operation":
        # Handle another operation
        data = {
            "different_param": params.get("different_param")
        }
    
    # Continue for all operations
    
    return data
```

#### 8.2 Result Processing
```python
def _process_result(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """Process result based on operation type."""
    if result.get("status") != "success":
        return result
    
    response_data = result.get("data", {})
    
    # Extract operation-specific data
    if operation == "operation_name":
        # Process this operation's response
        result.update({
            "specific_field": response_data.get("specific_field"),
            "processed_data": response_data.get("raw_data", [])
        })
    
    elif operation == "another_operation":
        # Process another operation's response
        result.update({
            "different_field": response_data.get("different_field")
        })
    
    # Continue for all operations
    
    return result
```

### 9. Cleanup Method ✅
```python
async def close(self):
    """Clean up resources."""
    if self.universal_node:
        await self.universal_node.close()
```

### 10. Optional Test Section ✅
```python
if __name__ == "__main__":
    import asyncio
    
    async def test():
        node = [VendorName]Node()
        
        # Test operation
        test_data = {
            "params": {
                "operation": "test_operation",
                "api_key": "test_key",
                # Add test parameters
            }
        }
        
        result = await node.execute(test_data)
        print(f"Result: {result}")
        
        await node.close()
    
    # Uncomment to test
    # asyncio.run(test())
```

## 🔧 UniversalRequestNode Features

### Supported Authentication Types
- `bearer_token` - Bearer token in Authorization header
- `api_key` - API key in header or query parameter  
- `basic_auth` - HTTP Basic authentication
- `oauth2` - OAuth2 access token
- `custom` - Custom authentication function
- `aws_signature` - AWS signature v4

### Supported HTTP Methods
- `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, and any other HTTP method

### Convenience Methods Available
```python
# Instead of universal_node.request("GET", "/endpoint")
result = await self.universal_node.get("/endpoint", params={...})
result = await self.universal_node.post("/endpoint", data={...})
result = await self.universal_node.put("/endpoint", data={...})
result = await self.universal_node.patch("/endpoint", data={...})
result = await self.universal_node.delete("/endpoint")

# Pagination support
all_pages = await self.universal_node.paginate("GET", "/endpoint", max_pages=10)
```

### Additional Features
- **Circuit Breaker** - Prevents cascading failures
- **Rate Limiting** - Adaptive throttling with burst support
- **Retry Logic** - Exponential backoff with jitter
- **Timeout Management** - Connect, read, and total timeouts
- **Request/Response Transformation** - Automatic content type handling
- **Pagination Support** - Automatic multi-page data fetching
- **Error Normalization** - Consistent error response format

## 🔍 Validation Checklist

Before considering a node conversion complete, verify:

### Structure ✅
- [ ] All imports with try/except patterns
- [ ] Class inherits from BaseNode
- [ ] CONFIG dictionary with all 6 sections
- [ ] OPERATIONS dictionary with complete metadata
- [ ] All required methods implemented

### CONFIG Completeness ✅
- [ ] node_info: All 9 required fields
- [ ] api_config: base_url, authentication, headers, retry, rate_limiting, timeouts
- [ ] parameters: api_key, operation, + vendor-specific params
- [ ] outputs: success and error schemas
- [ ] error_codes: HTTP status codes with descriptions

### OPERATIONS Completeness ✅
- [ ] Each operation has all 12 required fields
- [ ] Auth section in each operation with 5 required fields
- [ ] Examples array with at least one example
- [ ] All parameters referenced in required_params/optional_params exist in CONFIG.parameters

### Methods ✅
- [ ] __init__ creates UniversalRequestNode with CONFIG["api_config"]
- [ ] get_schema returns basic schema with core parameters
- [ ] execute handles all operations with proper error handling
- [ ] _prepare_request_data maps all operations
- [ ] _process_result handles all operations
- [ ] close method cleans up universal_node

### Authentication ✅
- [ ] Correct auth type in api_config.authentication
- [ ] Auth mapping in execute method (token vs api_key)
- [ ] Per-operation auth in OPERATIONS
- [ ] Sensitive parameters marked as sensitive: true

## 🎯 Final Validation

The node should:
1. **Compile without errors**
2. **Be discoverable by node_discovery_app.py** 
3. **Show complete operation metadata in API**
4. **Handle all operations without hardcoded logic**
5. **Follow exact same pattern as OpenaiNode.py**

---

**Remember: OpenaiNode.py is the PERFECT template. Any deviation should be justified and documented.**