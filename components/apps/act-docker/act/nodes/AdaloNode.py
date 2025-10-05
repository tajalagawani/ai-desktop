#!/usr/bin/env python3
"""
Adalo Node - Enhanced with ALL 13 advanced features following OpenAI template
EMERGENCY RECOVERY: ALL original 17 operations restored and enhanced
Configuration is embedded directly in the node - no separate config.json needed
"""

import logging
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema
    except ImportError:
        from  base_node import BaseNode, NodeSchema

# Import the Enhanced UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from .universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class AdaloNode(BaseNode):
    """
    Enhanced Adalo node with ALL 13 advanced features - following perfect OpenAI template.
    EMERGENCY RECOVERY: ALL original 17 operations restored and enhanced.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "adalo",
            "display_name": "Adalo",
            "description": "Comprehensive Adalo API integration for no-code app platform with ALL 17 operations: collections, records CRUD, users, notifications, and file management",
            "category": "no-code",
            "vendor": "adalo",
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["no-code", "app-platform", "collections", "records", "users", "notifications", "files", "mobile-app"],
            "documentation_url": "https://help.adalo.com/integrations/the-adalo-api",
            "icon": "https://www.adalo.com/favicon.ico",
            "color": "#6C5CE7",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.adalo.com/v0/apps/{app_id}",
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
                "base_delay": 1.0,
                "max_delay": 60.0,
                "jitter": True,
                "retriable_codes": [429, 500, 502, 503, 504],
                "retriable_exceptions": ["aiohttp.ClientTimeout", "aiohttp.ClientConnectorError"],
                "timeout_ms": 30000
            },
            "rate_limiting": {
                "requests_per_minute": 100,
                "requests_per_second": 2.0,
                "burst_size": 5,
                "cost_per_request": 0.01,
                "quota_type": "requests"
            },
            "timeouts": {
                "connect": 10.0,
                "read": 30.0,
                "total": 60.0
            }
        },
        
        # Enhanced pricing information
        "pricing": {
            "cost_per_1k_requests": 10.00,
            "cost_per_request": 0.01,
            "billing_unit": "requests",
            "free_tier_limit": 100
        },
        
        # Performance monitoring
        "monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "request_count"],
            "alerts": {
                "error_rate_threshold": 0.05,
                "response_time_threshold": 5000
            }
        },
        
        # Intelligent caching
        "caching": {
            "enabled": True,
            "cache_key_template": "{operation}:{hash}",
            "ttl_seconds": 300,
            "cache_conditions": {
                "only_for": ["GET"],
                "exclude_params": ["timestamp", "offset", "limit"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_api_token",
            "validation_endpoint": "/collections"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://help.adalo.com/integrations/the-adalo-api",
            "setup_guide": "https://help.adalo.com/integrations/the-adalo-api/getting-started",
            "troubleshooting": "https://community.adalo.com/c/help/18",
            "changelog": "https://help.adalo.com/integrations/the-adalo-api/changelog"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "Adalo App API Key (Bearer token)",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-zA-Z0-9-_]+$",
                    "message": "API key must contain only alphanumeric characters, hyphens, and underscores",
                    "minLength": 10,
                    "maxLength": 100
                }
            },
            "app_id": {
                "type": "string",
                "description": "Adalo App ID",
                "required": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "App ID must be a valid UUID format"
                },
                "examples": ["12345678-1234-1234-1234-123456789012"]
            },
            "operation": {
                "type": "string",
                "description": "The Adalo operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    "list_collections", "get_collection", 
                    "list_records", "get_record", "create_record", "update_record", "delete_record",
                    "send_push_notification", "send_bulk_notifications", 
                    "get_current_user", "list_users", "get_user", "create_user", "update_user", "delete_user",
                    "upload_file", "delete_file"
                ]
            },
            "collection_id": {
                "type": "string",
                "description": "Collection ID for record operations",
                "required": False,
                "group": "Resource",
                "examples": ["users", "posts", "products"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Collection ID must contain only alphanumeric characters, hyphens, and underscores"
                }
            },
            "collection_name": {
                "type": "string",
                "description": "Collection name (alternative to collection_id)",
                "required": False,
                "group": "Resource",
                "examples": ["users", "posts", "products"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Collection name must contain only alphanumeric characters, hyphens, and underscores"
                }
            },
            "record_id": {
                "type": "string",
                "description": "Record ID for specific record operations",
                "required": False,
                "group": "Resource",
                "examples": ["1", "123", "abc123"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Record ID must contain only alphanumeric characters, hyphens, and underscores"
                }
            },
            "user_id": {
                "type": "string",
                "description": "User ID for user operations",
                "required": False,
                "group": "Resource",
                "examples": ["1", "123", "user456"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "User ID must contain only alphanumeric characters, hyphens, and underscores"
                }
            },
            "file_id": {
                "type": "string",
                "description": "File ID for file operations",
                "required": False,
                "group": "Resource",
                "examples": ["file123", "img456"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "File ID must contain only alphanumeric characters, hyphens, and underscores"
                }
            },
            "limit": {
                "type": "integer",
                "description": "Number of items to return (max 100)",
                "required": False,
                "default": 20,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 100
                },
                "examples": [20, 50, 100]
            },
            "offset": {
                "type": "integer",
                "description": "Number of records to skip",
                "required": False,
                "default": 0,
                "group": "Pagination",
                "validation": {
                    "minimum": 0
                },
                "examples": [0, 20, 100]
            },
            "sort_field": {
                "type": "string",
                "description": "Field to sort by",
                "required": False,
                "group": "Sorting",
                "examples": ["created_at", "name", "id", "updated_at"]
            },
            "sort_order": {
                "type": "string",
                "description": "Sort order",
                "required": False,
                "default": "asc",
                "group": "Sorting",
                "validation": {
                    "enum": ["asc", "desc"]
                }
            },
            "filters": {
                "type": "object",
                "description": "Filters for querying records",
                "required": False,
                "group": "Filtering",
                "examples": [
                    {"name": {"$eq": "John Doe"}},
                    {"age": {"$gte": 18}},
                    {"status": {"$in": ["active", "pending"]}}
                ]
            },
            "search_query": {
                "type": "string",
                "description": "Search query for records",
                "required": False,
                "group": "Filtering",
                "examples": ["John", "active users", "recent posts"],
                "validation": {
                    "maxLength": 255
                }
            },
            "record_data": {
                "type": "object",
                "description": "Record data for create/update operations",
                "required": False,
                "group": "Data",
                "examples": [
                    {"name": "John Doe", "email": "john@example.com", "age": 30},
                    {"title": "New Post", "content": "This is the post content", "published": True}
                ]
            },
            "user_data": {
                "type": "object",
                "description": "User data for create/update user operations",
                "required": False,
                "group": "Data",
                "examples": [
                    {"email": "user@example.com", "password": "secure123", "name": "Jane Doe"}
                ]
            },
            "notification_title": {
                "type": "string",
                "description": "Push notification title",
                "required": False,
                "group": "Notifications",
                "examples": ["New Message", "Update Available", "Welcome!"],
                "validation": {
                    "maxLength": 100
                }
            },
            "notification_body": {
                "type": "string",
                "description": "Push notification body/message",
                "required": False,
                "group": "Notifications",
                "examples": ["You have a new message", "App update is available", "Welcome to our app!"],
                "validation": {
                    "maxLength": 500
                }
            },
            "notification_data": {
                "type": "object",
                "description": "Additional notification data/payload",
                "required": False,
                "group": "Notifications",
                "examples": [
                    {"type": "message", "id": "123"},
                    {"feature": "new_dashboard", "version": "2.0"}
                ]
            },
            "target_users": {
                "type": "array",
                "description": "Array of user IDs to send notifications to",
                "required": False,
                "group": "Notifications",
                "examples": [["user123", "user456"], ["all_users"]]
            },
            "send_to_all": {
                "type": "boolean",
                "description": "Send notification to all app users",
                "required": False,
                "default": False,
                "group": "Notifications"
            },
            "file_data": {
                "type": "string",
                "description": "Base64 encoded file data or file URL",
                "required": False,
                "group": "Files",
                "examples": ["data:image/jpeg;base64,/9j/4AAQSkZ...", "https://example.com/file.jpg"]
            },
            "file_name": {
                "type": "string",
                "description": "File name for upload",
                "required": False,
                "group": "Files",
                "examples": ["profile.jpg", "document.pdf", "avatar.png"]
            },
            "file_type": {
                "type": "string",
                "description": "File MIME type",
                "required": False,
                "group": "Files",
                "examples": ["image/jpeg", "image/png", "application/pdf", "text/plain"]
            },
            "include_relationships": {
                "type": "boolean",
                "description": "Include related records in response",
                "required": False,
                "default": False,
                "group": "Advanced"
            },
            "fields": {
                "type": "array",
                "description": "Specific fields to return in response",
                "required": False,
                "group": "Advanced",
                "examples": [["id", "name", "email"], ["title", "content", "created_at"]]
            },
            "timeout": {
                "type": "number",
                "description": "Request timeout in seconds",
                "required": False,
                "default": 30,
                "group": "Advanced",
                "validation": {
                    "minimum": 5,
                    "maximum": 300
                }
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful Adalo API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from Adalo API"},
                    "result": {"type": "object", "description": "Full API response data"},
                    "resource_id": {"type": "string", "description": "Resource ID for created/updated items"},
                    "count": {"type": "number", "description": "Number of items returned"},
                    "has_more": {"type": "boolean", "description": "Whether there are more results"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Adalo error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "list_collections": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "get_collection": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "list_records": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "get_record": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "create_record": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "update_record": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "delete_record": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "send_push_notification": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "send_bulk_notifications": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "get_current_user": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "list_users": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "get_user": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "create_user": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "update_user": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "delete_user": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "upload_file": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            },
            "delete_file": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": []
            }
        },
        
        # Error codes specific to Adalo
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid or missing API key",
            "403": "Forbidden - Access denied to resource",
            "404": "Not Found - Resource not found",
            "422": "Unprocessable Entity - Validation errors in request data",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Adalo server error",
            "502": "Bad Gateway - Adalo server temporarily unavailable",
            "503": "Service Unavailable - Adalo server overloaded"
        }
    }
    
    # Enhanced operation definitions with ALL 17 OPERATIONS restored and enhanced
    OPERATIONS = {
        # COLLECTIONS OPERATIONS (2 operations)
        "list_collections": {
            "method": "GET",
            "endpoint": "/collections",
            "required_params": [],
            "optional_params": [],
            "display_name": "List Collections",
            "description": "Retrieve a list of collections from the Adalo app",
            "group": "Collections",
            "tags": ["collections", "list", "schema"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Collection ID"},
                            "name": {"type": "string", "description": "Collection display name"},
                            "slug": {"type": "string", "description": "Collection API slug"},
                            "fields": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "name": {"type": "string"},
                                        "type": {"type": "string"},
                                        "required": {"type": "boolean"}
                                    }
                                }
                            },
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {
                    "created_at": "format_timestamp",
                    "updated_at": "format_timestamp"
                },
                "field_aliases": {}
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "List all collections",
                    "description": "Get all collections in the Adalo app",
                    "input": {}
                }
            ]
        },
        "get_collection": {
            "method": "GET",
            "endpoint": "/collections/{collection_id}",
            "required_params": ["collection_id"],
            "optional_params": [],
            "display_name": "Get Collection",
            "description": "Get details of a specific collection",
            "group": "Collections",
            "tags": ["collections", "get", "schema"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Collection ID"},
                        "name": {"type": "string", "description": "Collection display name"},
                        "slug": {"type": "string", "description": "Collection API slug"},
                        "fields": {"type": "array"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            
            "validation_rules": {
                "collection_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Collection ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Get collection details",
                    "description": "Get details of a specific collection",
                    "input": {
                        "collection_id": "users"
                    }
                }
            ]
        },
        
        # RECORDS OPERATIONS (5 operations)
        "list_records": {
            "method": "GET",
            "endpoint": "/collections/{collection_id}/records",
            "required_params": ["collection_id"],
            "optional_params": ["limit", "offset", "sort_field", "sort_order", "filters", "search_query", "fields", "include_relationships"],
            "display_name": "List Records",
            "description": "Retrieve records from a specific collection with pagination and filtering",
            "group": "Records",
            "tags": ["records", "list", "data"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "records": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string", "description": "Record ID"},
                                    "created_at": {"type": "string", "format": "date-time"},
                                    "updated_at": {"type": "string", "format": "date-time"}
                                },
                                "additionalProperties": True
                            }
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "total_count": {"type": "integer"},
                                "offset": {"type": "integer"},
                                "limit": {"type": "integer"}
                            }
                        }
                    }
                }
            },
            
            "validation_rules": {
                "collection_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Collection ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "limit": {
                    "pattern": "",
                    "message": "Limit must be between 1 and 100",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "max_value": 100,
                    "required": False
                }
            },
            
            "pagination": {
                "type": "offset",
                "offset_param": "offset",
                "size_param": "limit",
                "default_size": 20,
                "max_size": 100,
                "total_field": "meta.total_count",
                "count_field": "meta.total_count"
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "List all records",
                    "description": "Get all records from a collection",
                    "input": {
                        "collection_id": "users"
                    }
                },
                {
                    "name": "List records with pagination",
                    "description": "Get records with pagination and sorting",
                    "input": {
                        "collection_id": "posts",
                        "offset": 0,
                        "limit": 20,
                        "sort_field": "created_at",
                        "sort_order": "desc"
                    }
                }
            ]
        },
        "get_record": {
            "method": "GET",
            "endpoint": "/collections/{collection_id}/records/{record_id}",
            "required_params": ["collection_id", "record_id"],
            "optional_params": ["include_relationships", "fields"],
            "display_name": "Get Record",
            "description": "Retrieve a specific record by ID",
            "group": "Records",
            "tags": ["records", "get", "data"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Record ID"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    },
                    "additionalProperties": True
                }
            },
            
            "validation_rules": {
                "collection_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Collection ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "record_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Record ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Get specific record",
                    "description": "Retrieve a record by its ID",
                    "input": {
                        "collection_id": "users",
                        "record_id": "123"
                    }
                }
            ]
        },
        "create_record": {
            "method": "POST",
            "endpoint": "/collections/{collection_id}/records",
            "required_params": ["collection_id", "record_data"],
            "optional_params": [],
            "body_parameters": ["record_data"],
            "display_name": "Create Record",
            "description": "Create a new record in a collection",
            "group": "Records",
            "tags": ["records", "create", "data"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Created record ID"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    },
                    "additionalProperties": True
                }
            },
            
            "array_templates": {
                "tags": [
                    {"template": "important", "description": "Tag for important records"},
                    {"template": "featured", "description": "Tag for featured records"},
                    {"template": "urgent", "description": "Tag for urgent records"}
                ],
                "categories": [
                    {"template": "general", "description": "General category"},
                    {"template": "business", "description": "Business category"},
                    {"template": "personal", "description": "Personal category"}
                ],
                "attachments": [
                    {"template": {"file_id": "file123", "name": "document.pdf", "type": "application/pdf"}, "description": "File attachment object"},
                    {"template": {"file_id": "img456", "name": "image.jpg", "type": "image/jpeg"}, "description": "Image attachment object"}
                ],
                "permissions": [
                    {"template": "read", "description": "Read permission"},
                    {"template": "write", "description": "Write permission"},
                    {"template": "admin", "description": "Admin permission"}
                ]
            },
            
            "validation_rules": {
                "collection_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Collection ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "record_data": {
                    "pattern": "",
                    "message": "Record data is required for creating records",
                    "pattern_type": "custom",
                    "required": True,
                    "min_properties": 1
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Create user record",
                    "description": "Create a new user record with basic information",
                    "input": {
                        "collection_id": "users",
                        "record_data": {
                            "name": "John Doe",
                            "email": "john@example.com",
                            "age": 30,
                            "status": "active"
                        }
                    }
                }
            ]
        },
        "update_record": {
            "method": "PUT",
            "endpoint": "/collections/{collection_id}/records/{record_id}",
            "required_params": ["collection_id", "record_id", "record_data"],
            "optional_params": [],
            "body_parameters": ["record_data"],
            "display_name": "Update Record",
            "description": "Update an existing record",
            "group": "Records",
            "tags": ["records", "update", "data"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Updated record ID"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    },
                    "additionalProperties": True
                }
            },
            
            "array_templates": {
                "tags": [
                    {"template": "updated", "description": "Tag for updated records"},
                    {"template": "reviewed", "description": "Tag for reviewed records"},
                    {"template": "published", "description": "Tag for published records"}
                ],
                "categories": [
                    {"template": "draft", "description": "Draft category for updates"},
                    {"template": "final", "description": "Final category for updates"}
                ],
                "modifications": [
                    {"template": {"field": "name", "old_value": "John Doe", "new_value": "John Smith"}, "description": "Field modification tracking"},
                    {"template": {"field": "status", "old_value": "pending", "new_value": "active"}, "description": "Status change tracking"}
                ]
            },
            
            "validation_rules": {
                "collection_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Collection ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "record_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Record ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "record_data": {
                    "pattern": "",
                    "message": "Record data is required for updating records",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Update user record",
                    "description": "Update an existing user record",
                    "input": {
                        "collection_id": "users",
                        "record_id": "123",
                        "record_data": {
                            "name": "John Smith",
                            "age": 31
                        }
                    }
                }
            ]
        },
        "delete_record": {
            "method": "DELETE",
            "endpoint": "/collections/{collection_id}/records/{record_id}",
            "required_params": ["collection_id", "record_id"],
            "optional_params": [],
            "display_name": "Delete Record",
            "description": "Delete a specific record",
            "group": "Records",
            "tags": ["records", "delete", "data"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Deleted record ID"},
                        "status": {"type": "string", "enum": ["deleted"]},
                        "message": {"type": "string", "description": "Success message"}
                    }
                }
            },
            
            "validation_rules": {
                "collection_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Collection ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "record_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Record ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Delete record",
                    "description": "Delete a specific record by ID",
                    "input": {
                        "collection_id": "posts",
                        "record_id": "456"
                    }
                }
            ]
        },
        
        # NOTIFICATIONS OPERATIONS (2 operations)
        "send_push_notification": {
            "method": "POST",
            "endpoint": "/notifications/push",
            "required_params": ["notification_title", "notification_body"],
            "optional_params": ["notification_data", "target_users", "send_to_all"],
            "body_parameters": ["notification_title", "notification_body", "notification_data", "target_users", "send_to_all"],
            "display_name": "Send Push Notification",
            "description": "Send push notifications to app users",
            "group": "Notifications",
            "tags": ["notifications", "push", "messaging"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Notification ID"},
                        "status": {"type": "string", "enum": ["sent", "queued"]},
                        "recipients": {"type": "integer", "description": "Number of recipients"},
                        "sent_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            
            "array_templates": {
                "target_users": [
                    {"template": "user123", "description": "User ID for targeting"},
                    {"template": "user456", "description": "Another user ID"}
                ]
            },
            
            "validation_rules": {
                "notification_title": {
                    "pattern": "",
                    "message": "Notification title is required",
                    "pattern_type": "custom",
                    "required": True,
                    "max_length": 100
                },
                "notification_body": {
                    "pattern": "",
                    "message": "Notification body is required",
                    "pattern_type": "custom",
                    "required": True,
                    "max_length": 500
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Send notification to all users",
                    "description": "Send a push notification to all app users",
                    "input": {
                        "notification_title": "New Feature Available",
                        "notification_body": "Check out our latest feature in the app!",
                        "send_to_all": True,
                        "notification_data": {"feature": "new_dashboard"}
                    }
                }
            ]
        },
        "send_bulk_notifications": {
            "method": "POST",
            "endpoint": "/notifications/bulk",
            "required_params": ["notification_title", "notification_body", "target_users"],
            "optional_params": ["notification_data"],
            "body_parameters": ["notification_title", "notification_body", "target_users", "notification_data"],
            "display_name": "Send Bulk Notifications",
            "description": "Send bulk push notifications to multiple users",
            "group": "Notifications",
            "tags": ["notifications", "push", "bulk", "messaging"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Bulk notification ID"},
                        "status": {"type": "string", "enum": ["sent", "queued"]},
                        "recipients": {"type": "integer", "description": "Number of recipients"},
                        "sent_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            
            "array_templates": {
                "target_users": [
                    {"template": "user123", "description": "User ID for bulk targeting"},
                    {"template": "user456", "description": "Another user ID for bulk targeting"},
                    {"template": "user789", "description": "Third user ID example"}
                ],
                "notification_segments": [
                    {"template": "active_users", "description": "Segment for active users"},
                    {"template": "premium_users", "description": "Segment for premium users"},
                    {"template": "new_users", "description": "Segment for new users"}
                ],
                "custom_data_keys": [
                    {"template": "campaign_id", "description": "Campaign tracking ID"},
                    {"template": "event_type", "description": "Type of event triggering notification"},
                    {"template": "priority_level", "description": "Priority level of notification"}
                ]
            },
            
            "validation_rules": {
                "notification_title": {
                    "pattern": "",
                    "message": "Notification title is required",
                    "pattern_type": "custom",
                    "required": True
                },
                "notification_body": {
                    "pattern": "",
                    "message": "Notification body is required",
                    "pattern_type": "custom",
                    "required": True
                },
                "target_users": {
                    "pattern": "",
                    "message": "Target users array is required",
                    "pattern_type": "custom",
                    "required": True,
                    "min_items": 1
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Send notification to specific users",
                    "description": "Send a targeted push notification",
                    "input": {
                        "notification_title": "Personal Message",
                        "notification_body": "You have a new message waiting",
                        "target_users": ["user123", "user456"],
                        "notification_data": {"type": "message", "id": "msg789"}
                    }
                }
            ]
        },
        
        # USER OPERATIONS (6 operations)
        "get_current_user": {
            "method": "GET",
            "endpoint": "/users/me",
            "required_params": [],
            "optional_params": ["fields", "include_relationships"],
            "display_name": "Get Current User",
            "description": "Get current authenticated user information",
            "group": "Users",
            "tags": ["users", "current", "profile"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "User ID"},
                        "email": {"type": "string", "format": "email"},
                        "name": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    },
                    "additionalProperties": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Get current user",
                    "description": "Get authenticated user information",
                    "input": {}
                }
            ]
        },
        "list_users": {
            "method": "GET",
            "endpoint": "/users",
            "required_params": [],
            "optional_params": ["limit", "offset", "sort_field", "sort_order", "filters", "search_query"],
            "display_name": "List Users",
            "description": "Retrieve a list of users in the app",
            "group": "Users",
            "tags": ["users", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "users": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "email": {"type": "string", "format": "email"},
                                    "name": {"type": "string"},
                                    "created_at": {"type": "string", "format": "date-time"},
                                    "updated_at": {"type": "string", "format": "date-time"}
                                }
                            }
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "total_count": {"type": "integer"},
                                "offset": {"type": "integer"},
                                "limit": {"type": "integer"}
                            }
                        }
                    }
                }
            },
            
            "pagination": {
                "type": "offset",
                "offset_param": "offset",
                "size_param": "limit",
                "default_size": 20,
                "max_size": 100,
                "total_field": "meta.total_count",
                "count_field": "meta.total_count"
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "List all users",
                    "description": "Get all users in the app",
                    "input": {}
                }
            ]
        },
        "get_user": {
            "method": "GET",
            "endpoint": "/users/{user_id}",
            "required_params": ["user_id"],
            "optional_params": ["fields", "include_relationships"],
            "display_name": "Get User",
            "description": "Retrieve a specific user by ID",
            "group": "Users",
            "tags": ["users", "get"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "User ID"},
                        "email": {"type": "string", "format": "email"},
                        "name": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    },
                    "additionalProperties": True
                }
            },
            
            "validation_rules": {
                "user_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "User ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Get specific user",
                    "description": "Get user by ID",
                    "input": {
                        "user_id": "123"
                    }
                }
            ]
        },
        "create_user": {
            "method": "POST",
            "endpoint": "/users",
            "required_params": ["user_data"],
            "optional_params": [],
            "body_parameters": ["user_data"],
            "display_name": "Create User",
            "description": "Create a new user in the app",
            "group": "Users",
            "tags": ["users", "create"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Created user ID"},
                        "email": {"type": "string", "format": "email"},
                        "name": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    },
                    "additionalProperties": True
                }
            },
            
            "array_templates": {
                "roles": [
                    {"template": "user", "description": "Standard user role"},
                    {"template": "admin", "description": "Administrator role"},
                    {"template": "moderator", "description": "Moderator role"}
                ],
                "permissions": [
                    {"template": "read_posts", "description": "Permission to read posts"},
                    {"template": "create_posts", "description": "Permission to create posts"},
                    {"template": "edit_profile", "description": "Permission to edit profile"}
                ],
                "preferences": [
                    {"template": {"key": "notifications", "value": True}, "description": "User preference for notifications"},
                    {"template": {"key": "theme", "value": "dark"}, "description": "User preference for theme"},
                    {"template": {"key": "language", "value": "en"}, "description": "User preference for language"}
                ],
                "tags": [
                    {"template": "new_user", "description": "Tag for new users"},
                    {"template": "verified", "description": "Tag for verified users"},
                    {"template": "premium", "description": "Tag for premium users"}
                ]
            },
            
            "validation_rules": {
                "user_data": {
                    "pattern": "",
                    "message": "User data is required for creating users",
                    "pattern_type": "custom",
                    "required": True,
                    "required_properties": ["email"]
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Create new user",
                    "description": "Create a user with email and password",
                    "input": {
                        "user_data": {
                            "email": "user@example.com",
                            "password": "secure123",
                            "name": "Jane Doe"
                        }
                    }
                }
            ]
        },
        "update_user": {
            "method": "PUT",
            "endpoint": "/users/{user_id}",
            "required_params": ["user_id", "user_data"],
            "optional_params": [],
            "body_parameters": ["user_data"],
            "display_name": "Update User",
            "description": "Update an existing user",
            "group": "Users",
            "tags": ["users", "update"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Updated user ID"},
                        "email": {"type": "string", "format": "email"},
                        "name": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    },
                    "additionalProperties": True
                }
            },
            
            "array_templates": {
                "roles": [
                    {"template": "editor", "description": "Editor role for updates"},
                    {"template": "viewer", "description": "Viewer role for updates"},
                    {"template": "contributor", "description": "Contributor role for updates"}
                ],
                "updated_fields": [
                    {"template": "email", "description": "Email field update"},
                    {"template": "name", "description": "Name field update"},
                    {"template": "profile_picture", "description": "Profile picture field update"}
                ],
                "activity_log": [
                    {"template": {"action": "login", "timestamp": "2025-08-25T10:00:00Z"}, "description": "User activity log entry"},
                    {"template": {"action": "profile_update", "timestamp": "2025-08-25T10:05:00Z"}, "description": "Profile update activity"}
                ],
                "preferences": [
                    {"template": {"key": "email_notifications", "value": False}, "description": "Updated email notification preference"},
                    {"template": {"key": "privacy_level", "value": "private"}, "description": "Updated privacy level preference"}
                ]
            },
            
            "validation_rules": {
                "user_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "User ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "user_data": {
                    "pattern": "",
                    "message": "User data is required for updating users",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Update user",
                    "description": "Update user information",
                    "input": {
                        "user_id": "123",
                        "user_data": {
                            "name": "Jane Smith",
                            "email": "jane.smith@example.com"
                        }
                    }
                }
            ]
        },
        "delete_user": {
            "method": "DELETE",
            "endpoint": "/users/{user_id}",
            "required_params": ["user_id"],
            "optional_params": [],
            "display_name": "Delete User",
            "description": "Delete a specific user",
            "group": "Users",
            "tags": ["users", "delete"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Deleted user ID"},
                        "status": {"type": "string", "enum": ["deleted"]},
                        "message": {"type": "string", "description": "Success message"}
                    }
                }
            },
            
            "validation_rules": {
                "user_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "User ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Delete user",
                    "description": "Delete a specific user by ID",
                    "input": {
                        "user_id": "123"
                    }
                }
            ]
        },
        
        # FILE OPERATIONS (2 operations)
        "upload_file": {
            "method": "POST",
            "endpoint": "/files",
            "required_params": ["file_data", "file_name"],
            "optional_params": ["file_type"],
            "body_parameters": ["file_data", "file_name", "file_type"],
            "display_name": "Upload File",
            "description": "Upload a file to Adalo storage",
            "group": "Files",
            "tags": ["files", "upload", "storage"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "File ID"},
                        "url": {"type": "string", "format": "uri", "description": "File URL"},
                        "name": {"type": "string", "description": "File name"},
                        "size": {"type": "integer", "description": "File size in bytes"},
                        "type": {"type": "string", "description": "File MIME type"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            
            "array_templates": {
                "file_tags": [
                    {"template": "document", "description": "Tag for document files"},
                    {"template": "image", "description": "Tag for image files"},
                    {"template": "temporary", "description": "Tag for temporary files"}
                ],
                "metadata_fields": [
                    {"template": {"key": "author", "value": "John Doe"}, "description": "File metadata for author"},
                    {"template": {"key": "category", "value": "business"}, "description": "File metadata for category"},
                    {"template": {"key": "version", "value": "1.0"}, "description": "File metadata for version"}
                ],
                "allowed_extensions": [
                    {"template": ".pdf", "description": "PDF file extension"},
                    {"template": ".jpg", "description": "JPEG image extension"},
                    {"template": ".png", "description": "PNG image extension"},
                    {"template": ".docx", "description": "Word document extension"}
                ],
                "access_permissions": [
                    {"template": {"user_id": "user123", "permission": "read"}, "description": "File access permission"},
                    {"template": {"user_id": "user456", "permission": "write"}, "description": "File write permission"}
                ]
            },
            
            "validation_rules": {
                "file_data": {
                    "pattern": "",
                    "message": "File data is required for file upload",
                    "pattern_type": "custom",
                    "required": True
                },
                "file_name": {
                    "pattern": "",
                    "message": "File name is required for file upload",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Upload image file",
                    "description": "Upload an image file",
                    "input": {
                        "file_data": "data:image/jpeg;base64,/9j/4AAQSkZ...",
                        "file_name": "profile.jpg",
                        "file_type": "image/jpeg"
                    }
                }
            ]
        },
        "delete_file": {
            "method": "DELETE",
            "endpoint": "/files/{file_id}",
            "required_params": ["file_id"],
            "optional_params": [],
            "display_name": "Delete File",
            "description": "Delete a file from Adalo storage",
            "group": "Files",
            "tags": ["files", "delete", "storage"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Deleted file ID"},
                        "status": {"type": "string", "enum": ["deleted"]},
                        "message": {"type": "string", "description": "Success message"}
                    }
                }
            },
            
            "validation_rules": {
                "file_id": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "File ID is required and must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ADALO_API_KEY", "ADALO_APP_ID"],
                "optional_env_keys": [],
                "required_params": ["api_key", "app_id"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Adalo API key and App ID"
            },
            "examples": [
                {
                    "name": "Delete file",
                    "description": "Delete a specific file by ID",
                    "input": {
                        "file_id": "file123"
                    }
                }
            ]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced Adalo node with embedded configuration."""
        # Initialize the Enhanced UniversalRequestNode with embedded config first
        try:
            self.universal_request_node = UniversalRequestNode(
                config=self.CONFIG,
                operations=self.OPERATIONS,
                sandbox_timeout=sandbox_timeout
            )
        except Exception as e:
            logger.warning(f"UniversalRequestNode not available, falling back to base implementation: {e}")
            self.universal_request_node = None
        
        # Now call super init, which will call get_schema()
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        logger.debug(f"Enhanced AdaloNode initialized with ALL 17 operations and all 13 advanced features")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        if self.universal_request_node:
            return self.universal_request_node.get_schema()
        else:
            # Fallback: create a basic schema from our configuration
            from base_node import NodeParameter, NodeParameterType
            parameters = []
            for param_name, param_config in self.CONFIG.get("parameters", {}).items():
                param_type = getattr(NodeParameterType, param_config.get("type", "string").upper(), NodeParameterType.STRING)
                param = NodeParameter(
                    name=param_name,
                    type=param_type,
                    description=param_config.get("description", ""),
                    required=param_config.get("required", False)
                )
                parameters.append(param)
            
            return NodeSchema(
                node_type=self.CONFIG["node_info"]["name"],
                version=self.CONFIG["node_info"]["version"],
                description=self.CONFIG["node_info"]["description"],
                parameters=parameters,
                outputs={"result": NodeParameterType.OBJECT, "status": NodeParameterType.STRING},
                tags=self.CONFIG["node_info"]["tags"],
                author=self.CONFIG["node_info"]["author"]
            )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"AdaloNode executing operation: {node_data.get('params', {}).get('operation')}")
        if self.universal_request_node:
            return await self.universal_request_node.execute(node_data)
        else:
            # Fallback: Basic error response 
            return {
                "status": "error",
                "error": "AdaloNode enhanced functionality requires UniversalRequestNode but it's not available",
                "timestamp": "2025-08-25T00:00:00Z"
            }

    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters - delegated to Enhanced UniversalRequestNode."""
        if self.universal_request_node:
            return self.universal_request_node.validate_custom(node_data)
        else:
            # Basic validation fallback
            return {}

    def get_operation_config(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific operation."""
        return self.OPERATIONS.get(operation)

    def get_base_config(self) -> Dict[str, Any]:
        """Get the base configuration for this node."""
        return self.CONFIG
    
    def get_array_template(self, operation: str, parameter: str) -> Optional[Dict[str, Any]]:
        """Get array template for a parameter in an operation."""
        op_config = self.OPERATIONS.get(operation)
        if not op_config or "array_templates" not in op_config:
            return None
        return op_config["array_templates"].get(parameter)
    
    def get_validation_rules(self, operation: str) -> Dict[str, Any]:
        """Get validation rules for an operation."""
        op_config = self.OPERATIONS.get(operation)
        if not op_config or "validation_rules" not in op_config:
            return {}
        return op_config["validation_rules"]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if self.universal_request_node:
            return self.universal_request_node.get_metrics()
        else:
            return {"status": "UniversalRequestNode not available"}

    @staticmethod
    def format_response(response_data: Any) -> Dict[str, Any]:
        """Format response data consistently."""
        if isinstance(response_data, dict):
            return response_data
        elif isinstance(response_data, list):
            return {"items": response_data, "count": len(response_data)}
        else:
            return {"result": response_data}

# Export the enhanced node class
__all__ = ["AdaloNode"]