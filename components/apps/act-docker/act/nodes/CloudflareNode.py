#!/usr/bin/env python3
"""
Cloudflare Node - Enhanced with ALL 13 advanced features
Comprehensive Cloudflare API v4 integration with 85+ operations
Configuration is embedded directly in the node - no separate config.json needed
"""

import logging
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Import the Enhanced UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from .universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class CloudflareNode(BaseNode):
    """
    Enhanced Cloudflare node with ALL 13 advanced features and 85 operations.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "cloudflare",
            "display_name": "Cloudflare",
            "description": "Comprehensive Cloudflare API v4 integration for zones, DNS, workers, security, SSL/TLS, analytics and more - 85+ operations",
            "category": "infrastructure",
            "vendor": "cloudflare",
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["cloudflare", "cdn", "dns", "security", "workers", "ssl", "api", "integration", "zones", "analytics"],
            "documentation_url": "https://developers.cloudflare.com/api/",
            "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/cloudflare.svg",
            "color": "#F38020",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.cloudflare.com/client/v4",
            "authentication": {
                "type": "bearer_token",
                "header": "Authorization"
            },
            "default_headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ACT-Workflow/2.0"
            },
            "retry_config": {
                "max_attempts": 3,
                "backoff": "exponential_jitter",
                "base_delay": 2.0,
                "max_delay": 30.0,
                "jitter": True,
                "retriable_codes": [429, 500, 502, 503, 504],
                "retriable_exceptions": ["aiohttp.ClientTimeout", "aiohttp.ClientConnectorError"],
                "timeout_ms": 45000
            },
            "rate_limiting": {
                "requests_per_minute": 1200,
                "requests_per_second": 20.0,
                "burst_size": 5,
                "cost_per_request": 0.0001,
                "quota_type": "requests"
            },
            "timeouts": {
                "connect": 10.0,
                "read": 45.0,
                "total": 60.0
            }
        },
        
        # Enhanced pricing information
        "pricing": {
            "cost_per_request": 0.0001,
            "billing_unit": "requests",
            "free_tier_limit": 100000
        },
        
        # Performance monitoring
        "monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "zone_operations", "dns_modifications"],
            "alerts": {
                "error_rate_threshold": 0.02,
                "response_time_threshold": 3000
            }
        },
        
        # Intelligent caching
        "caching": {
            "enabled": True,
            "cache_key_template": "{operation}:{zone_id}:{hash}",
            "ttl_seconds": 300,
            "cache_conditions": {
                "only_for": ["GET"],
                "exclude_params": ["timestamp", "nonce"],
                "cache_by_zone": True
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_api_token",
            "validation_endpoint": "/user/tokens/verify"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://developers.cloudflare.com/api/",
            "setup_guide": "https://developers.cloudflare.com/fundamentals/api/get-started/",
            "troubleshooting": "https://developers.cloudflare.com/support/troubleshooting/",
            "changelog": "https://developers.cloudflare.com/api/changelog/"
        },
        
        # Enhanced parameters with validation and dependencies
        "parameters": {
            "api_token": {
                "type": "string",
                "description": "Cloudflare API Token (recommended authentication method)",
                "required": False,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "minLength": 40,
                    "message": "API token must be at least 40 characters"
                }
            },
            "email": {
                "type": "string",
                "description": "Cloudflare account email (for legacy API key authentication)",
                "required": False,
                "group": "Authentication",
                "validation": {
                    "pattern": "email",
                    "message": "Must be a valid email address"
                }
            },
            "api_key": {
                "type": "string",
                "description": "Cloudflare Global API Key (legacy authentication)",
                "required": False,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "minLength": 37,
                    "maxLength": 37,
                    "message": "API key must be exactly 37 characters"
                }
            },
            "operation": {
                "type": "string",
                "description": "The Cloudflare operation to perform",
                "required": True,
                "group": "Operation"
            },
            "zone_id": {
                "type": "string",
                "description": "Zone ID for zone-specific operations",
                "required": False,
                "group": "Zone",
                "validation": {
                    "minLength": 32,
                    "maxLength": 32,
                    "message": "Zone ID must be 32 characters"
                }
            },
            "account_id": {
                "type": "string",
                "description": "Account ID for account-specific operations",
                "required": False,
                "group": "Account",
                "validation": {
                    "minLength": 32,
                    "maxLength": 32,
                    "message": "Account ID must be 32 characters"
                }
            },
            "dns_record_id": {
                "type": "string",
                "description": "DNS record ID for DNS record operations",
                "required": False,
                "group": "DNS"
            },
            "dns_type": {
                "type": "string",
                "description": "DNS record type",
                "required": False,
                "group": "DNS",
                "validation": {
                    "enum": ["A", "AAAA", "CNAME", "MX", "TXT", "SRV", "NS", "PTR", "CAA", "HTTPS", "SVCB"]
                }
            },
            "dns_name": {
                "type": "string",
                "description": "DNS record name",
                "required": False,
                "group": "DNS",
                "validation": {
                    "maxLength": 255,
                    "message": "DNS name cannot exceed 255 characters"
                }
            },
            "dns_content": {
                "type": "string",
                "description": "DNS record content",
                "required": False,
                "group": "DNS"
            },
            "dns_ttl": {
                "type": "number",
                "description": "DNS record TTL (1 for automatic)",
                "required": False,
                "default": 1,
                "group": "DNS",
                "validation": {
                    "min_value": 1,
                    "max_value": 86400
                }
            },
            "dns_priority": {
                "type": "number",
                "description": "DNS record priority (for MX/SRV records)",
                "required": False,
                "group": "DNS",
                "validation": {
                    "min_value": 0,
                    "max_value": 65535
                }
            },
            "proxied": {
                "type": "boolean",
                "description": "Whether DNS record is proxied through Cloudflare",
                "required": False,
                "default": False,
                "group": "DNS"
            },
            "zone_name": {
                "type": "string",
                "description": "Zone name for zone operations",
                "required": False,
                "group": "Zone",
                "validation": {
                    "pattern": "url",
                    "message": "Must be a valid domain name"
                }
            },
            "worker_name": {
                "type": "string",
                "description": "Worker name for worker operations",
                "required": False,
                "group": "Workers",
                "validation": {
                    "maxLength": 63,
                    "pattern": "^[a-zA-Z0-9][a-zA-Z0-9_-]*$",
                    "message": "Worker name must be alphanumeric with hyphens/underscores"
                }
            },
            "request_body": {
                "type": "object",
                "description": "Request body for create/update operations",
                "required": False,
                "group": "Request"
            },
            "page": {
                "type": "number",
                "description": "Page number for pagination",
                "required": False,
                "default": 1,
                "group": "Pagination",
                "validation": {
                    "min_value": 1
                }
            },
            "per_page": {
                "type": "number",
                "description": "Number of items per page",
                "required": False,
                "default": 20,
                "group": "Pagination",
                "validation": {
                    "min_value": 5,
                    "max_value": 100
                }
            }
        },
        
        # Enhanced outputs with detailed schemas
        "outputs": {
            "status": {"type": "string", "description": "Operation status"},
            "success": {"type": "boolean", "description": "Whether operation succeeded"},
            "result": {"type": "any", "description": "Operation result data"},
            "errors": {"type": "array", "description": "Error messages if any"},
            "messages": {"type": "array", "description": "Success messages"},
            "result_info": {"type": "object", "description": "Pagination and metadata"},
            "id": {"type": "string", "description": "Resource ID if applicable"},
            "status_code": {"type": "number", "description": "HTTP status code"},
            "timestamp": {"type": "string", "description": "Response timestamp"}
        },
        
        # Authentication configuration
        "auth": {
            "bearer_token": {
                "parameter": "api_token",
                "header": "Authorization",
                "prefix": "Bearer"
            },
            "legacy": {
                "email_parameter": "email",
                "key_parameter": "api_key",
                "email_header": "X-Auth-Email",
                "key_header": "X-Auth-Key"
            }
        },
        
        # Error code mappings
        "error_codes": {
            "400": "Bad Request - Invalid parameters",
            "401": "Unauthorized - Invalid credentials",
            "403": "Forbidden - Insufficient permissions",
            "404": "Not Found - Resource does not exist",
            "409": "Conflict - Resource already exists",
            "429": "Rate Limited - Too many requests",
            "500": "Internal Server Error",
            "502": "Bad Gateway",
            "503": "Service Unavailable"
        }
    }
    
    # Complete operations configuration with all 85 operations
    OPERATIONS = {
        # ===== AUTHENTICATION =====
        "verify_token": {
            "method": "GET",
            "endpoint": "/user/tokens/verify",
            "description": "Verify API token validity",
            "group": "Authentication",
            "required_params": [],
            "optional_params": [],
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "status": {"type": "string"},
                        "expires_on": {"type": "string"}
                    }
                },
                "error": {"type": "object"},
                "status_codes": {200: "Token valid", 401: "Token invalid"}
            },
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Verify API token",
                    "params": {"operation": "verify_token"}
                }
            ]
        },
        
        # ===== ZONE OPERATIONS =====
        "list_zones": {
            "method": "GET",
            "endpoint": "/zones",
            "description": "List all zones in the account",
            "group": "Zones",
            "required_params": [],
            "optional_params": ["page", "per_page", "name", "status", "account_name", "order", "direction", "match"],
            "pagination": {
                "type": "page",
                "cursor_param": "page",
                "size_param": "per_page",
                "max_size": 50,
                "response_fields": {
                    "next_cursor": "result_info.page",
                    "has_more": "result_info.total_pages",
                    "total_count": "result_info.count"
                }
            },
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "result": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "status": {"type": "string"},
                                    "type": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "List first 10 zones",
                    "params": {"operation": "list_zones", "per_page": 10}
                }
            ]
        },
        
        "get_zone": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}",
            "description": "Get zone details by ID",
            "group": "Zones",
            "required_params": ["zone_id"],
            "optional_params": [],
            "parameter_dependencies": [
                {
                    "when_field": "operation",
                    "when_value": "get_zone",
                    "then_require": ["zone_id"]
                }
            ],
            "validation_rules": {
                "zone_id": {
                    "pattern": "^[a-f0-9]{32}$",
                    "message": "Zone ID must be a 32-character hexadecimal string",
                    "required": True
                }
            },
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "result": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "status": {"type": "string"},
                                "type": {"type": "string"},
                                "name_servers": {"type": "array"}
                            }
                        }
                    }
                }
            },
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "examples": [
                {
                    "name": "Get zone details",
                    "params": {
                        "operation": "get_zone",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "create_zone": {
            "method": "POST",
            "endpoint": "/zones",
            "description": "Create a new zone",
            "group": "Zones",
            "required_params": ["zone_name"],
            "optional_params": ["account_id", "zone_type", "request_body"],
            "body_parameters": ["zone_name", "account_id", "zone_type"],
            "parameter_dependencies": [
                {
                    "when_field": "operation",
                    "when_value": "create_zone",
                    "then_require": ["zone_name"]
                }
            ],
            "validation_rules": {
                "zone_name": {
                    "pattern": "^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$",
                    "message": "Zone name must be a valid domain name",
                    "required": True
                }
            },
            "field_mapping": {
                "input_transforms": {
                    "zone_name": "lowercase",
                    "zone_type": "default_full"
                }
            },
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Create new zone",
                    "params": {
                        "operation": "create_zone",
                        "zone_name": "example.com",
                        "zone_type": "full"
                    }
                }
            ]
        },
        
        "update_zone": {
            "method": "PATCH",
            "endpoint": "/zones/{zone_id}",
            "description": "Update zone settings",
            "group": "Zones",
            "required_params": ["zone_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 3,
            "examples": [
                {
                    "name": "Update zone plan",
                    "params": {
                        "operation": "update_zone",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "request_body": {"plan": {"id": "free"}}
                    }
                }
            ]
        },
        
        "delete_zone": {
            "method": "DELETE",
            "endpoint": "/zones/{zone_id}",
            "description": "Delete a zone",
            "group": "Zones",
            "required_params": ["zone_id"],
            "optional_params": [],
            "rate_limit_cost": 10,
            "examples": [
                {
                    "name": "Delete zone",
                    "params": {
                        "operation": "delete_zone",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        # ===== DNS RECORDS =====
        "list_dns_records": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/dns_records",
            "description": "List DNS records for a zone",
            "group": "DNS Records",
            "required_params": ["zone_id"],
            "optional_params": ["page", "per_page", "dns_type", "dns_name", "order", "direction", "match"],
            "pagination": {
                "type": "page",
                "cursor_param": "page",
                "size_param": "per_page",
                "max_size": 100
            },
            "array_templates": {
                "dns_records": {
                    "template": [
                        {
                            "type": "A",
                            "name": "@",
                            "content": "192.0.2.1",
                            "ttl": 1,
                            "proxied": False
                        }
                    ],
                    "description": "Array of DNS record objects",
                    "min_items": 1,
                    "max_items": 100
                }
            },
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "examples": [
                {
                    "name": "List A records",
                    "params": {
                        "operation": "list_dns_records",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "dns_type": "A"
                    }
                }
            ]
        },
        
        "get_dns_record": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/dns_records/{dns_record_id}",
            "description": "Get DNS record details",
            "group": "DNS Records",
            "required_params": ["zone_id", "dns_record_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get DNS record",
                    "params": {
                        "operation": "get_dns_record",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "dns_record_id": "372e67954025e0ba6aaa6d586b9e0b59"
                    }
                }
            ]
        },
        
        "create_dns_record": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/dns_records",
            "description": "Create a new DNS record",
            "group": "DNS Records",
            "required_params": ["zone_id", "dns_type", "dns_name", "dns_content"],
            "optional_params": ["dns_ttl", "dns_priority", "proxied", "request_body"],
            "body_parameters": ["dns_type", "dns_name", "dns_content", "dns_ttl", "dns_priority", "proxied"],
            "parameter_dependencies": [
                {
                    "when_field": "dns_type",
                    "when_value": "MX",
                    "then_require": ["dns_priority"]
                },
                {
                    "when_field": "dns_type",
                    "when_value": "SRV",
                    "then_require": ["dns_priority"]
                }
            ],
            "validation_rules": {
                "dns_type": {
                    "pattern": "^(A|AAAA|CNAME|MX|TXT|SRV|NS|PTR|CAA|HTTPS|SVCB)$",
                    "message": "Invalid DNS record type",
                    "required": True
                },
                "dns_name": {
                    "max_length": 255,
                    "message": "DNS name cannot exceed 255 characters",
                    "required": True
                },
                "dns_content": {
                    "min_length": 1,
                    "message": "DNS content is required",
                    "required": True
                }
            },
            "rate_limit_cost": 3,
            "examples": [
                {
                    "name": "Create A record",
                    "params": {
                        "operation": "create_dns_record",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "dns_type": "A",
                        "dns_name": "www",
                        "dns_content": "192.0.2.1",
                        "proxied": True
                    }
                }
            ]
        },
        
        "update_dns_record": {
            "method": "PUT",
            "endpoint": "/zones/{zone_id}/dns_records/{dns_record_id}",
            "description": "Update an existing DNS record",
            "group": "DNS Records",
            "required_params": ["zone_id", "dns_record_id"],
            "optional_params": ["dns_type", "dns_name", "dns_content", "dns_ttl", "dns_priority", "proxied", "request_body"],
            "body_parameters": ["dns_type", "dns_name", "dns_content", "dns_ttl", "dns_priority", "proxied"],
            "rate_limit_cost": 3,
            "examples": [
                {
                    "name": "Update A record",
                    "params": {
                        "operation": "update_dns_record",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "dns_record_id": "372e67954025e0ba6aaa6d586b9e0b59",
                        "dns_content": "203.0.113.1"
                    }
                }
            ]
        },
        
        "delete_dns_record": {
            "method": "DELETE",
            "endpoint": "/zones/{zone_id}/dns_records/{dns_record_id}",
            "description": "Delete a DNS record",
            "group": "DNS Records",
            "required_params": ["zone_id", "dns_record_id"],
            "optional_params": [],
            "rate_limit_cost": 3,
            "examples": [
                {
                    "name": "Delete DNS record",
                    "params": {
                        "operation": "delete_dns_record",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "dns_record_id": "372e67954025e0ba6aaa6d586b9e0b59"
                    }
                }
            ]
        },
        
        # ===== WORKERS =====
        "list_workers": {
            "method": "GET",
            "endpoint": "/accounts/{account_id}/workers/scripts",
            "description": "List Workers scripts",
            "group": "Workers",
            "required_params": ["account_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 180,
            "examples": [
                {
                    "name": "List workers",
                    "params": {
                        "operation": "list_workers",
                        "account_id": "01a7362d577a6c3019a474fd6f485823"
                    }
                }
            ]
        },
        
        "get_worker": {
            "method": "GET",
            "endpoint": "/accounts/{account_id}/workers/scripts/{worker_name}",
            "description": "Get Worker script details",
            "group": "Workers",
            "required_params": ["account_id", "worker_name"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get worker script",
                    "params": {
                        "operation": "get_worker",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "worker_name": "my-worker"
                    }
                }
            ]
        },
        
        "create_worker": {
            "method": "PUT",
            "endpoint": "/accounts/{account_id}/workers/scripts/{worker_name}",
            "description": "Create or update a Worker script",
            "group": "Workers",
            "required_params": ["account_id", "worker_name"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Create worker",
                    "params": {
                        "operation": "create_worker",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "worker_name": "my-worker",
                        "request_body": {"script": "export default { async fetch(request) { return new Response('Hello World!'); } }"}
                    }
                }
            ]
        },
        
        "delete_worker": {
            "method": "DELETE",
            "endpoint": "/accounts/{account_id}/workers/scripts/{worker_name}",
            "description": "Delete a Worker script",
            "group": "Workers",
            "required_params": ["account_id", "worker_name"],
            "optional_params": [],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Delete worker",
                    "params": {
                        "operation": "delete_worker",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "worker_name": "my-worker"
                    }
                }
            ]
        },
        
        # ===== SSL/TLS =====
        "list_ssl_certificates": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/ssl/certificate_packs",
            "description": "List SSL certificate packs",
            "group": "SSL/TLS",
            "required_params": ["zone_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "examples": [
                {
                    "name": "List SSL certificates",
                    "params": {
                        "operation": "list_ssl_certificates",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "get_ssl_certificate": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/ssl/certificate_packs/{certificate_id}",
            "description": "Get SSL certificate pack details",
            "group": "SSL/TLS",
            "required_params": ["zone_id", "certificate_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "examples": [
                {
                    "name": "Get SSL certificate",
                    "params": {
                        "operation": "get_ssl_certificate",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "certificate_id": "3822ff90-ea29-44df-9e55-21300bb9419b"
                    }
                }
            ]
        },
        
        # ===== ANALYTICS =====
        "get_analytics": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/analytics/dashboard",
            "description": "Get zone analytics data",
            "group": "Analytics",
            "required_params": ["zone_id"],
            "optional_params": ["since", "until", "continuous"],
            "validation_rules": {
                "since": {
                    "pattern": "iso_date",
                    "message": "Since must be in ISO 8601 format"
                },
                "until": {
                    "pattern": "iso_date",
                    "message": "Until must be in ISO 8601 format"
                }
            },
            "rate_limit_cost": 2,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get zone analytics",
                    "params": {
                        "operation": "get_analytics",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "since": "2023-01-01T00:00:00Z",
                        "until": "2023-01-02T00:00:00Z"
                    }
                }
            ]
        },
        
        # ===== FIREWALL =====
        "list_firewall_rules": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/firewall/rules",
            "description": "List firewall rules",
            "group": "Firewall",
            "required_params": ["zone_id"],
            "optional_params": ["page", "per_page"],
            "pagination": {
                "type": "page",
                "cursor_param": "page",
                "size_param": "per_page",
                "max_size": 100
            },
            "rate_limit_cost": 1,
            "cache_ttl": 180,
            "examples": [
                {
                    "name": "List firewall rules",
                    "params": {
                        "operation": "list_firewall_rules",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "create_firewall_rule": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/firewall/rules",
            "description": "Create a firewall rule",
            "group": "Firewall",
            "required_params": ["zone_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "array_templates": {
                "firewall_rules": {
                    "template": [
                        {
                            "filter": {
                                "expression": "(http.request.uri.path contains \"admin\")"
                            },
                            "action": "block",
                            "description": "Block admin access"
                        }
                    ],
                    "description": "Array of firewall rule objects",
                    "min_items": 1,
                    "max_items": 25
                }
            },
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Create firewall rule",
                    "params": {
                        "operation": "create_firewall_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "request_body": [
                            {
                                "filter": {"expression": "(ip.geoip.country eq \"CN\")"},
                                "action": "block",
                                "description": "Block China traffic"
                            }
                        ]
                    }
                }
            ]
        },
        
        # ===== CACHE OPERATIONS =====
        "purge_cache": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/purge_cache",
            "description": "Purge cache (everything or specific files/tags)",
            "group": "Cache",
            "required_params": ["zone_id"],
            "optional_params": ["purge_everything", "files", "tags", "prefixes"],
            "body_parameters": ["purge_everything", "files", "tags", "prefixes"],
            "parameter_dependencies": [
                {
                    "when_field": "purge_everything",
                    "when_value": True,
                    "mutually_exclusive": ["files", "tags", "prefixes"]
                },
                {
                    "when_field": "operation",
                    "when_value": "purge_cache",
                    "require_one_of": ["purge_everything", "files", "tags", "prefixes"]
                }
            ],
            "array_templates": {
                "files": {
                    "template": ["https://example.com/css/app.css"],
                    "description": "Array of URLs to purge from cache",
                    "min_items": 1,
                    "max_items": 30
                },
                "tags": {
                    "template": ["static", "api"],
                    "description": "Array of cache tags to purge",
                    "min_items": 1,
                    "max_items": 30
                }
            },
            "rate_limit_cost": 10,
            "webhook_support": {
                "supported_events": ["cache.purge.complete"],
                "callback_param": "webhook_url"
            },
            "examples": [
                {
                    "name": "Purge everything",
                    "params": {
                        "operation": "purge_cache",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "purge_everything": True
                    }
                },
                {
                    "name": "Purge specific files",
                    "params": {
                        "operation": "purge_cache",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "files": ["https://example.com/css/app.css", "https://example.com/js/app.js"]
                    }
                }
            ]
        },
        
        # ===== PAGE RULES =====
        "list_page_rules": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/pagerules",
            "description": "List page rules",
            "group": "Page Rules",
            "required_params": ["zone_id"],
            "optional_params": ["status", "order", "direction", "match"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "List page rules",
                    "params": {
                        "operation": "list_page_rules",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "create_page_rule": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/pagerules",
            "description": "Create a page rule",
            "group": "Page Rules", 
            "required_params": ["zone_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Create caching page rule",
                    "params": {
                        "operation": "create_page_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "request_body": {
                            "targets": [{"target": "url", "constraint": {"operator": "matches", "value": "*.example.com/images/*"}}],
                            "actions": [{"id": "cache_level", "value": "cache_everything"}],
                            "priority": 1,
                            "status": "active"
                        }
                    }
                }
            ]
        },
        
        # ===== RATE LIMITING =====
        "list_rate_limits": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/rate_limits",
            "description": "List rate limiting rules",
            "group": "Rate Limiting",
            "required_params": ["zone_id"],
            "optional_params": ["page", "per_page"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "List rate limits",
                    "params": {
                        "operation": "list_rate_limits",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "create_rate_limit": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/rate_limits",
            "description": "Create a rate limiting rule",
            "group": "Rate Limiting",
            "required_params": ["zone_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Create rate limit rule",
                    "params": {
                        "operation": "create_rate_limit",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "request_body": {
                            "threshold": 1000,
                            "period": 60,
                            "action": {"mode": "challenge"},
                            "match": {"request": {"url": "*.example.com/api/*"}}
                        }
                    }
                }
            ]
        },
        
        # ===== LOAD BALANCING =====
        "list_load_balancers": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/load_balancers",
            "description": "List load balancers",
            "group": "Load Balancing",
            "required_params": ["zone_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "List load balancers",
                    "params": {
                        "operation": "list_load_balancers",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "create_load_balancer": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/load_balancers",
            "description": "Create a load balancer",
            "group": "Load Balancing",
            "required_params": ["zone_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 10,
            "examples": [
                {
                    "name": "Create load balancer",
                    "params": {
                        "operation": "create_load_balancer",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "request_body": {
                            "name": "api.example.com",
                            "fallback_pool": "17b5962d775c646f3f9725cbc7a53df4",
                            "default_pools": ["17b5962d775c646f3f9725cbc7a53df4"],
                            "description": "Load balancer for API endpoints",
                            "ttl": 30
                        }
                    }
                }
            ]
        },
        
        # ===== ACCOUNT MANAGEMENT =====
        "list_accounts": {
            "method": "GET",
            "endpoint": "/accounts",
            "description": "List accounts",
            "group": "Account",
            "required_params": [],
            "optional_params": ["page", "per_page", "direction"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "examples": [
                {
                    "name": "List accounts",
                    "params": {"operation": "list_accounts"}
                }
            ]
        },
        
        "get_account": {
            "method": "GET",
            "endpoint": "/accounts/{account_id}",
            "description": "Get account details",
            "group": "Account",
            "required_params": ["account_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "examples": [
                {
                    "name": "Get account details",
                    "params": {
                        "operation": "get_account",
                        "account_id": "01a7362d577a6c3019a474fd6f485823"
                    }
                }
            ]
        },
        
        # ===== USER MANAGEMENT =====
        "get_user": {
            "method": "GET",
            "endpoint": "/user",
            "description": "Get user details",
            "group": "User",
            "required_params": [],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "examples": [
                {
                    "name": "Get user details",
                    "params": {"operation": "get_user"}
                }
            ]
        },
        
        "update_user": {
            "method": "PATCH",
            "endpoint": "/user",
            "description": "Update user details",
            "group": "User",
            "required_params": [],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 3,
            "examples": [
                {
                    "name": "Update user profile",
                    "params": {
                        "operation": "update_user",
                        "request_body": {"first_name": "John", "last_name": "Doe"}
                    }
                }
            ]
        },
        
        # ===== DNS RECORD ADDITIONAL OPERATIONS =====
        "export_dns_records": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/dns_records/export",
            "description": "Export DNS records in BIND format",
            "group": "DNS Records",
            "required_params": ["zone_id"],
            "optional_params": [],
            "rate_limit_cost": 2,
            "cache_ttl": 180,
            "examples": [
                {
                    "name": "Export DNS records",
                    "params": {
                        "operation": "export_dns_records",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "import_dns_records": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/dns_records/import",
            "description": "Import DNS records from BIND file",
            "group": "DNS Records",
            "required_params": ["zone_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 10,
            "examples": [
                {
                    "name": "Import DNS records",
                    "params": {
                        "operation": "import_dns_records",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "request_body": {"file": "@/path/to/zone.bind"}
                    }
                }
            ]
        },
        
        # ===== ZONE SETTINGS =====
        "get_zone_settings": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/settings",
            "description": "Get all zone settings",
            "group": "Zone Settings",
            "required_params": ["zone_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get zone settings",
                    "params": {
                        "operation": "get_zone_settings",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "update_zone_settings": {
            "method": "PATCH",
            "endpoint": "/zones/{zone_id}/settings",
            "description": "Update zone settings",
            "group": "Zone Settings",
            "required_params": ["zone_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 3,
            "examples": [
                {
                    "name": "Update security level",
                    "params": {
                        "operation": "update_zone_settings",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "request_body": {"items": [{"id": "security_level", "value": "high"}]}
                    }
                }
            ]
        },
        
        "get_ssl_setting": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/settings/ssl",
            "description": "Get SSL setting for zone",
            "group": "Zone Settings",
            "required_params": ["zone_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get SSL setting",
                    "params": {
                        "operation": "get_ssl_setting",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "update_ssl_setting": {
            "method": "PATCH",
            "endpoint": "/zones/{zone_id}/settings/ssl",
            "description": "Update SSL setting for zone",
            "group": "Zone Settings",
            "required_params": ["zone_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 3,
            "examples": [
                {
                    "name": "Enable full SSL",
                    "params": {
                        "operation": "update_ssl_setting",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "request_body": {"value": "full"}
                    }
                }
            ]
        },
        
        # ===== WAF OPERATIONS =====
        "list_waf_rules": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/firewall/waf/packages/{package_id}/rules",
            "description": "List WAF rules for a package",
            "group": "WAF",
            "required_params": ["zone_id"],
            "optional_params": ["package_id", "page", "per_page"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "List WAF rules",
                    "params": {
                        "operation": "list_waf_rules",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "package_id": "a25a9a24e2d41c8ecaaf6b2b44b54e46"
                    }
                }
            ]
        },
        
        "get_waf_rule": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/firewall/waf/packages/{package_id}/rules/{rule_id}",
            "description": "Get WAF rule details",
            "group": "WAF",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": ["package_id"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get WAF rule",
                    "params": {
                        "operation": "get_waf_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "package_id": "a25a9a24e2d41c8ecaaf6b2b44b54e46",
                        "rule_id": "100000"
                    }
                }
            ]
        },
        
        "update_waf_rule": {
            "method": "PATCH",
            "endpoint": "/zones/{zone_id}/firewall/waf/packages/{package_id}/rules/{rule_id}",
            "description": "Update WAF rule",
            "group": "WAF",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": ["package_id", "request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 3,
            "examples": [
                {
                    "name": "Update WAF rule mode",
                    "params": {
                        "operation": "update_waf_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "package_id": "a25a9a24e2d41c8ecaaf6b2b44b54e46",
                        "rule_id": "100000",
                        "request_body": {"mode": "block"}
                    }
                }
            ]
        },
        
        # ===== ADDITIONAL FIREWALL OPERATIONS =====
        "get_firewall_rule": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/firewall/rules/{rule_id}",
            "description": "Get firewall rule details",
            "group": "Firewall",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get firewall rule",
                    "params": {
                        "operation": "get_firewall_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "372e67954025e0ba6aaa6d586b9e0b59"
                    }
                }
            ]
        },
        
        "update_firewall_rule": {
            "method": "PUT",
            "endpoint": "/zones/{zone_id}/firewall/rules/{rule_id}",
            "description": "Update firewall rule",
            "group": "Firewall",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Update firewall rule",
                    "params": {
                        "operation": "update_firewall_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "372e67954025e0ba6aaa6d586b9e0b59",
                        "request_body": {"action": "allow", "paused": False}
                    }
                }
            ]
        },
        
        "delete_firewall_rule": {
            "method": "DELETE",
            "endpoint": "/zones/{zone_id}/firewall/rules/{rule_id}",
            "description": "Delete firewall rule",
            "group": "Firewall",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": [],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Delete firewall rule",
                    "params": {
                        "operation": "delete_firewall_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "372e67954025e0ba6aaa6d586b9e0b59"
                    }
                }
            ]
        },
        
        # ===== ACCESS RULES =====
        "list_access_rules": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/firewall/access_rules/rules",
            "description": "List access rules",
            "group": "Access Rules",
            "required_params": ["zone_id"],
            "optional_params": ["page", "per_page", "mode", "match"],
            "rate_limit_cost": 1,
            "cache_ttl": 180,
            "examples": [
                {
                    "name": "List access rules",
                    "params": {
                        "operation": "list_access_rules",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "get_access_rule": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/firewall/access_rules/rules/{rule_id}",
            "description": "Get access rule details",
            "group": "Access Rules",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get access rule",
                    "params": {
                        "operation": "get_access_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "92f17202ed8bd63d69a66b86a49a8f6b"
                    }
                }
            ]
        },
        
        "create_access_rule": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/firewall/access_rules/rules",
            "description": "Create access rule",
            "group": "Access Rules",
            "required_params": ["zone_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Block IP address",
                    "params": {
                        "operation": "create_access_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "request_body": {
                            "mode": "block",
                            "configuration": {"target": "ip", "value": "198.51.100.4"},
                            "notes": "Block malicious IP"
                        }
                    }
                }
            ]
        },
        
        "update_access_rule": {
            "method": "PATCH",
            "endpoint": "/zones/{zone_id}/firewall/access_rules/rules/{rule_id}",
            "description": "Update access rule",
            "group": "Access Rules",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 3,
            "examples": [
                {
                    "name": "Update access rule mode",
                    "params": {
                        "operation": "update_access_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "92f17202ed8bd63d69a66b86a49a8f6b",
                        "request_body": {"mode": "challenge"}
                    }
                }
            ]
        },
        
        "delete_access_rule": {
            "method": "DELETE",
            "endpoint": "/zones/{zone_id}/firewall/access_rules/rules/{rule_id}",
            "description": "Delete access rule",
            "group": "Access Rules",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": [],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Delete access rule",
                    "params": {
                        "operation": "delete_access_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "92f17202ed8bd63d69a66b86a49a8f6b"
                    }
                }
            ]
        },
        
        # ===== ADDITIONAL PAGE RULE OPERATIONS =====
        "get_page_rule": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/pagerules/{rule_id}",
            "description": "Get page rule details",
            "group": "Page Rules",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get page rule",
                    "params": {
                        "operation": "get_page_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "9a7806061c88ada191ed06f989cc3dac"
                    }
                }
            ]
        },
        
        "update_page_rule": {
            "method": "PUT",
            "endpoint": "/zones/{zone_id}/pagerules/{rule_id}",
            "description": "Update page rule",
            "group": "Page Rules",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Update page rule priority",
                    "params": {
                        "operation": "update_page_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "9a7806061c88ada191ed06f989cc3dac",
                        "request_body": {"priority": 2}
                    }
                }
            ]
        },
        
        "delete_page_rule": {
            "method": "DELETE",
            "endpoint": "/zones/{zone_id}/pagerules/{rule_id}",
            "description": "Delete page rule",
            "group": "Page Rules",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": [],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Delete page rule",
                    "params": {
                        "operation": "delete_page_rule",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "9a7806061c88ada191ed06f989cc3dac"
                    }
                }
            ]
        },
        
        # ===== ADDITIONAL RATE LIMITING OPERATIONS =====
        "get_rate_limit": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/rate_limits/{rule_id}",
            "description": "Get rate limit rule details",
            "group": "Rate Limiting",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get rate limit rule",
                    "params": {
                        "operation": "get_rate_limit",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "372e67954025e0ba6aaa6d586b9e0b59"
                    }
                }
            ]
        },
        
        "update_rate_limit": {
            "method": "PUT",
            "endpoint": "/zones/{zone_id}/rate_limits/{rule_id}",
            "description": "Update rate limit rule",
            "group": "Rate Limiting",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Update rate limit threshold",
                    "params": {
                        "operation": "update_rate_limit",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "372e67954025e0ba6aaa6d586b9e0b59",
                        "request_body": {"threshold": 500}
                    }
                }
            ]
        },
        
        "delete_rate_limit": {
            "method": "DELETE",
            "endpoint": "/zones/{zone_id}/rate_limits/{rule_id}",
            "description": "Delete rate limit rule",
            "group": "Rate Limiting",
            "required_params": ["zone_id", "rule_id"],
            "optional_params": [],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Delete rate limit rule",
                    "params": {
                        "operation": "delete_rate_limit",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "rule_id": "372e67954025e0ba6aaa6d586b9e0b59"
                    }
                }
            ]
        },
        
        # ===== ADDITIONAL LOAD BALANCER OPERATIONS =====
        "get_load_balancer": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/load_balancers/{lb_id}",
            "description": "Get load balancer details",
            "group": "Load Balancing",
            "required_params": ["zone_id", "lb_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get load balancer",
                    "params": {
                        "operation": "get_load_balancer",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "lb_id": "f1aba936b94213e5b8dca0c0dbf1f9cc"
                    }
                }
            ]
        },
        
        "update_load_balancer": {
            "method": "PUT",
            "endpoint": "/zones/{zone_id}/load_balancers/{lb_id}",
            "description": "Update load balancer",
            "group": "Load Balancing",
            "required_params": ["zone_id", "lb_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 10,
            "examples": [
                {
                    "name": "Update load balancer TTL",
                    "params": {
                        "operation": "update_load_balancer",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "lb_id": "f1aba936b94213e5b8dca0c0dbf1f9cc",
                        "request_body": {"ttl": 60}
                    }
                }
            ]
        },
        
        "delete_load_balancer": {
            "method": "DELETE",
            "endpoint": "/zones/{zone_id}/load_balancers/{lb_id}",
            "description": "Delete load balancer",
            "group": "Load Balancing",
            "required_params": ["zone_id", "lb_id"],
            "optional_params": [],
            "rate_limit_cost": 10,
            "examples": [
                {
                    "name": "Delete load balancer",
                    "params": {
                        "operation": "delete_load_balancer",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "lb_id": "f1aba936b94213e5b8dca0c0dbf1f9cc"
                    }
                }
            ]
        },
        
        # ===== POOLS OPERATIONS =====
        "list_pools": {
            "method": "GET",
            "endpoint": "/accounts/{account_id}/load_balancers/pools",
            "description": "List load balancer pools",
            "group": "Pools",
            "required_params": ["account_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "List pools",
                    "params": {
                        "operation": "list_pools",
                        "account_id": "01a7362d577a6c3019a474fd6f485823"
                    }
                }
            ]
        },
        
        "get_pool": {
            "method": "GET",
            "endpoint": "/accounts/{account_id}/load_balancers/pools/{pool_id}",
            "description": "Get pool details",
            "group": "Pools",
            "required_params": ["account_id", "pool_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get pool",
                    "params": {
                        "operation": "get_pool",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "pool_id": "17b5962d775c646f3f9725cbc7a53df4"
                    }
                }
            ]
        },
        
        "create_pool": {
            "method": "POST",
            "endpoint": "/accounts/{account_id}/load_balancers/pools",
            "description": "Create load balancer pool",
            "group": "Pools",
            "required_params": ["account_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Create pool",
                    "params": {
                        "operation": "create_pool",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "request_body": {
                            "name": "primary-dc-pool",
                            "origins": [{"name": "app-server-1", "address": "0.0.0.0", "enabled": True}],
                            "monitor": "f1aba936b94213e5b8dca0c0dbf1f9cc",
                            "enabled": True
                        }
                    }
                }
            ]
        },
        
        "update_pool": {
            "method": "PUT",
            "endpoint": "/accounts/{account_id}/load_balancers/pools/{pool_id}",
            "description": "Update load balancer pool",
            "group": "Pools",
            "required_params": ["account_id", "pool_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Update pool",
                    "params": {
                        "operation": "update_pool",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "pool_id": "17b5962d775c646f3f9725cbc7a53df4",
                        "request_body": {"enabled": False}
                    }
                }
            ]
        },
        
        "delete_pool": {
            "method": "DELETE",
            "endpoint": "/accounts/{account_id}/load_balancers/pools/{pool_id}",
            "description": "Delete load balancer pool",
            "group": "Pools",
            "required_params": ["account_id", "pool_id"],
            "optional_params": [],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Delete pool",
                    "params": {
                        "operation": "delete_pool",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "pool_id": "17b5962d775c646f3f9725cbc7a53df4"
                    }
                }
            ]
        },
        
        # ===== MONITORS OPERATIONS =====
        "list_monitors": {
            "method": "GET",
            "endpoint": "/accounts/{account_id}/load_balancers/monitors",
            "description": "List health check monitors",
            "group": "Monitors",
            "required_params": ["account_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "List monitors",
                    "params": {
                        "operation": "list_monitors",
                        "account_id": "01a7362d577a6c3019a474fd6f485823"
                    }
                }
            ]
        },
        
        "get_monitor": {
            "method": "GET",
            "endpoint": "/accounts/{account_id}/load_balancers/monitors/{monitor_id}",
            "description": "Get monitor details",
            "group": "Monitors",
            "required_params": ["account_id", "monitor_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get monitor",
                    "params": {
                        "operation": "get_monitor",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "monitor_id": "f1aba936b94213e5b8dca0c0dbf1f9cc"
                    }
                }
            ]
        },
        
        "create_monitor": {
            "method": "POST",
            "endpoint": "/accounts/{account_id}/load_balancers/monitors",
            "description": "Create health check monitor",
            "group": "Monitors",
            "required_params": ["account_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Create HTTP monitor",
                    "params": {
                        "operation": "create_monitor",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "request_body": {
                            "type": "http",
                            "expected_codes": "200",
                            "method": "GET",
                            "path": "/health",
                            "timeout": 5,
                            "retries": 2,
                            "interval": 60
                        }
                    }
                }
            ]
        },
        
        "update_monitor": {
            "method": "PUT",
            "endpoint": "/accounts/{account_id}/load_balancers/monitors/{monitor_id}",
            "description": "Update health check monitor",
            "group": "Monitors",
            "required_params": ["account_id", "monitor_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Update monitor timeout",
                    "params": {
                        "operation": "update_monitor",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "monitor_id": "f1aba936b94213e5b8dca0c0dbf1f9cc",
                        "request_body": {"timeout": 10}
                    }
                }
            ]
        },
        
        "delete_monitor": {
            "method": "DELETE",
            "endpoint": "/accounts/{account_id}/load_balancers/monitors/{monitor_id}",
            "description": "Delete health check monitor",
            "group": "Monitors",
            "required_params": ["account_id", "monitor_id"],
            "optional_params": [],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Delete monitor",
                    "params": {
                        "operation": "delete_monitor",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "monitor_id": "f1aba936b94213e5b8dca0c0dbf1f9cc"
                    }
                }
            ]
        },
        
        # ===== WORKER ROUTES =====
        "list_worker_routes": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/workers/routes",
            "description": "List Worker routes",
            "group": "Worker Routes",
            "required_params": ["zone_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 180,
            "examples": [
                {
                    "name": "List worker routes",
                    "params": {
                        "operation": "list_worker_routes",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "get_worker_route": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/workers/routes/{route_id}",
            "description": "Get Worker route details",
            "group": "Worker Routes",
            "required_params": ["zone_id", "route_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get worker route",
                    "params": {
                        "operation": "get_worker_route",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "route_id": "e7a57d8746e74ae49c25994dadb421b1"
                    }
                }
            ]
        },
        
        "create_worker_route": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/workers/routes",
            "description": "Create Worker route",
            "group": "Worker Routes",
            "required_params": ["zone_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Create worker route",
                    "params": {
                        "operation": "create_worker_route",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "request_body": {
                            "pattern": "example.com/api/*",
                            "script": "my-worker"
                        }
                    }
                }
            ]
        },
        
        "update_worker_route": {
            "method": "PUT",
            "endpoint": "/zones/{zone_id}/workers/routes/{route_id}",
            "description": "Update Worker route",
            "group": "Worker Routes",
            "required_params": ["zone_id", "route_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Update worker route",
                    "params": {
                        "operation": "update_worker_route",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "route_id": "e7a57d8746e74ae49c25994dadb421b1",
                        "request_body": {"pattern": "example.com/new-api/*"}
                    }
                }
            ]
        },
        
        "delete_worker_route": {
            "method": "DELETE",
            "endpoint": "/zones/{zone_id}/workers/routes/{route_id}",
            "description": "Delete Worker route",
            "group": "Worker Routes",
            "required_params": ["zone_id", "route_id"],
            "optional_params": [],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Delete worker route",
                    "params": {
                        "operation": "delete_worker_route",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "route_id": "e7a57d8746e74ae49c25994dadb421b1"
                    }
                }
            ]
        },
        
        # ===== ADDITIONAL SSL OPERATIONS =====
        "create_ssl_certificate": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/ssl/certificate_packs",
            "description": "Create SSL certificate pack",
            "group": "SSL/TLS",
            "required_params": ["zone_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 10,
            "examples": [
                {
                    "name": "Order SSL certificate",
                    "params": {
                        "operation": "create_ssl_certificate",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "request_body": {
                            "type": "advanced",
                            "hosts": ["example.com", "*.example.com"]
                        }
                    }
                }
            ]
        },
        
        "delete_ssl_certificate": {
            "method": "DELETE",
            "endpoint": "/zones/{zone_id}/ssl/certificate_packs/{certificate_id}",
            "description": "Delete SSL certificate pack",
            "group": "SSL/TLS",
            "required_params": ["zone_id", "certificate_id"],
            "optional_params": [],
            "rate_limit_cost": 10,
            "examples": [
                {
                    "name": "Delete SSL certificate",
                    "params": {
                        "operation": "delete_ssl_certificate",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "certificate_id": "3822ff90-ea29-44df-9e55-21300bb9419b"
                    }
                }
            ]
        },
        
        # ===== ADDITIONAL ANALYTICS OPERATIONS =====
        "get_colos_analytics": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/analytics/colos",
            "description": "Get analytics by data center",
            "group": "Analytics",
            "required_params": ["zone_id"],
            "optional_params": ["since", "until"],
            "rate_limit_cost": 2,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "Get data center analytics",
                    "params": {
                        "operation": "get_colos_analytics",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        "get_dashboard_analytics": {
            "method": "GET",
            "endpoint": "/zones/{zone_id}/analytics/dashboard",
            "description": "Get dashboard analytics with detailed metrics",
            "group": "Analytics",
            "required_params": ["zone_id"],
            "optional_params": ["since", "until", "continuous"],
            "rate_limit_cost": 2,
            "cache_ttl": 180,
            "examples": [
                {
                    "name": "Get dashboard analytics",
                    "params": {
                        "operation": "get_dashboard_analytics",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "since": "2023-01-01T00:00:00Z",
                        "until": "2023-01-02T00:00:00Z"
                    }
                }
            ]
        },
        
        # ===== ADDITIONAL CACHE OPERATIONS =====
        "purge_cache_by_url": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/purge_cache",
            "description": "Purge cache by specific URLs",
            "group": "Cache",
            "required_params": ["zone_id", "files"],
            "optional_params": [],
            "body_parameters": ["files"],
            "array_templates": {
                "files": {
                    "template": ["https://example.com/css/app.css"],
                    "description": "Array of URLs to purge from cache",
                    "min_items": 1,
                    "max_items": 30
                }
            },
            "rate_limit_cost": 10,
            "examples": [
                {
                    "name": "Purge specific URLs",
                    "params": {
                        "operation": "purge_cache_by_url",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "files": ["https://example.com/css/app.css"]
                    }
                }
            ]
        },
        
        "purge_cache_by_tag": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/purge_cache",
            "description": "Purge cache by tags",
            "group": "Cache",
            "required_params": ["zone_id", "tags"],
            "optional_params": [],
            "body_parameters": ["tags"],
            "array_templates": {
                "tags": {
                    "template": ["static", "api"],
                    "description": "Array of cache tags to purge",
                    "min_items": 1,
                    "max_items": 30
                }
            },
            "rate_limit_cost": 10,
            "examples": [
                {
                    "name": "Purge by tags",
                    "params": {
                        "operation": "purge_cache_by_tag",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "tags": ["static", "css"]
                    }
                }
            ]
        },
        
        "purge_cache_by_prefix": {
            "method": "POST",
            "endpoint": "/zones/{zone_id}/purge_cache",
            "description": "Purge cache by URL prefixes",
            "group": "Cache",
            "required_params": ["zone_id", "prefixes"],
            "optional_params": [],
            "body_parameters": ["prefixes"],
            "array_templates": {
                "prefixes": {
                    "template": ["example.com/images/"],
                    "description": "Array of URL prefixes to purge from cache",
                    "min_items": 1,
                    "max_items": 30
                }
            },
            "rate_limit_cost": 10,
            "examples": [
                {
                    "name": "Purge by prefixes",
                    "params": {
                        "operation": "purge_cache_by_prefix",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
                        "prefixes": ["example.com/images/"]
                    }
                }
            ]
        },
        
        # ===== ADDITIONAL ACCOUNT OPERATIONS =====
        "update_account": {
            "method": "PATCH",
            "endpoint": "/accounts/{account_id}",
            "description": "Update account settings",
            "group": "Account",
            "required_params": ["account_id"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Update account name",
                    "params": {
                        "operation": "update_account",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "request_body": {"name": "My Company Account"}
                    }
                }
            ]
        },
        
        # ===== ZONE ACTIVATION =====
        "activate_zone": {
            "method": "PUT",
            "endpoint": "/zones/{zone_id}/activation_check",
            "description": "Re-run activation check for zone",
            "group": "Zones",
            "required_params": ["zone_id"],
            "optional_params": [],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Reactivate zone",
                    "params": {
                        "operation": "activate_zone",
                        "zone_id": "023e105f4ecef8ad9ca31a8372d0c353"
                    }
                }
            ]
        },
        
        # ===== ADDITIONAL WORKERS OPERATIONS =====
        "update_worker": {
            "method": "PUT",
            "endpoint": "/accounts/{account_id}/workers/scripts/{worker_name}",
            "description": "Update an existing Worker script",
            "group": "Workers",
            "required_params": ["account_id", "worker_name"],
            "optional_params": ["request_body"],
            "body_parameters": ["request_body"],
            "rate_limit_cost": 5,
            "examples": [
                {
                    "name": "Update worker script",
                    "params": {
                        "operation": "update_worker",
                        "account_id": "01a7362d577a6c3019a474fd6f485823",
                        "worker_name": "my-worker",
                        "request_body": {"script": "export default { async fetch(request) { return new Response('Updated Hello World!'); } }"}
                    }
                }
            ]
        },
        
        # ===== ADDITIONAL MODELS OPERATIONS =====
        "list_models": {
            "method": "GET",
            "endpoint": "/accounts/{account_id}/ai/models",
            "description": "List available AI models",
            "group": "AI Models",
            "required_params": ["account_id"],
            "optional_params": [],
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "examples": [
                {
                    "name": "List AI models",
                    "params": {
                        "operation": "list_models",
                        "account_id": "01a7362d577a6c3019a474fd6f485823"
                    }
                }
            ]
        },
        
        # ===== IMAGES OPERATIONS =====
        "list_images": {
            "method": "GET",
            "endpoint": "/accounts/{account_id}/images/v1",
            "description": "List Cloudflare Images",
            "group": "Images",
            "required_params": ["account_id"],
            "optional_params": ["page", "per_page"],
            "pagination": {
                "type": "page",
                "cursor_param": "page",
                "size_param": "per_page",
                "max_size": 100
            },
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "examples": [
                {
                    "name": "List images",
                    "params": {
                        "operation": "list_images",
                        "account_id": "01a7362d577a6c3019a474fd6f485823"
                    }
                }
            ]
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize CloudflareNode with enhanced UniversalRequestNode."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create UniversalRequestNode instance with our configuration
        self.request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.debug("Enhanced CloudflareNode initialized with 85+ operations and 13 advanced features")
    
    def get_schema(self) -> NodeSchema:
        """Get schema from the UniversalRequestNode."""
        return self.request_node.get_schema()
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced validation using UniversalRequestNode."""
        return self.request_node.validate_custom(node_data)
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute using enhanced UniversalRequestNode."""
        return await self.request_node.execute(node_data)
    
    def get_operation_info(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific operation."""
        return self.request_node.get_operation_config(operation)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.request_node.get_metrics()
    
    def get_supported_operations(self) -> Dict[str, str]:
        """Get list of supported operations with descriptions."""
        return {
            op_name: op_config["description"] 
            for op_name, op_config in self.OPERATIONS.items()
        }

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    registry = NodeRegistry()
    registry.register("cloudflare", CloudflareNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register Enhanced CloudflareNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")

# Export for direct usage
__all__ = ["CloudflareNode"]