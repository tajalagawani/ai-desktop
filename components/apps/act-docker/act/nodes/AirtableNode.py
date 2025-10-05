#!/usr/bin/env python3
"""
Airtable Node - Enhanced with ALL 13 advanced features following OpenAI template
Configuration is embedded directly in the node - no separate config.json needed
COMPLETE RECOVERY: ALL 42 ORIGINAL OPERATIONS RESTORED WITH ARRAY TEMPLATES
"""

import logging
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        from  base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Import the Enhanced UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from .universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class AirtableNode(BaseNode):
    """
    Enhanced Airtable node with ALL 13 advanced features - following perfect OpenAI template.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    COMPLETE RECOVERY: ALL 42 ORIGINAL OPERATIONS RESTORED WITH PROPER ARRAY TEMPLATES
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "airtable",
            "display_name": "Airtable",
            "description": "Comprehensive Airtable API integration for database management, record operations, field management, and collaboration workflows",
            "category": "database",
            "vendor": "airtable",
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["database", "spreadsheet", "records", "collaboration", "no-code"],
            "documentation_url": "https://airtable.com/developers/web/api/introduction",
            "icon": "https://airtable.com/favicon.ico",
            "color": "#FFAA01",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.airtable.com/v0",
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
                "requests_per_minute": 300,
                "requests_per_second": 5.0,
                "burst_size": 10,
                "cost_per_request": 0.002,
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
            "cost_per_1k_requests": 2.00,
            "cost_per_request": 0.002,
            "billing_unit": "requests",
            "free_tier_limit": 1000
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
                "exclude_params": ["timestamp", "offset", "pageSize"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_access_token",
            "validation_endpoint": "/meta/bases"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://airtable.com/developers/web/api/introduction",
            "setup_guide": "https://airtable.com/developers/web/guides/personal-access-tokens",
            "troubleshooting": "https://support.airtable.com/docs/airtable-api",
            "changelog": "https://airtable.com/developers/web/api/changelog"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "access_token": {
                "type": "string",
                "description": "Airtable Personal Access Token or OAuth token",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^pat[a-zA-Z0-9]{14}\\.[a-f0-9]{64}$|^[a-zA-Z0-9_-]+$",
                    "message": "Access token must be a valid Airtable Personal Access Token or OAuth token",
                    "minLength": 10,
                    "maxLength": 200
                }
            },
            "base_id": {
                "type": "string",
                "description": "Airtable Base ID (starts with 'app')",
                "required": True,
                "group": "Resource",
                "examples": ["appABC123DEF456", "appXYZ789GHI012"],
                "validation": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must start with 'app' followed by 14 alphanumeric characters"
                }
            },
            "operation": {
                "type": "string",
                "description": "The Airtable operation to perform",
                "required": True,
                "group": "Operation",
                "enum": ["get_bases", "get_base", "create_base", "update_base", "delete_base", "get_tables", "get_table", "create_table", "update_table", "delete_table", "get_records", "get_record", "create_record", "create_records", "update_record", "update_records", "delete_record", "delete_records", "get_fields", "get_field", "create_field", "update_field", "delete_field", "get_views", "get_view", "create_view", "update_view", "delete_view", "get_comments", "create_comment", "update_comment", "delete_comment", "get_webhooks", "create_webhook", "update_webhook", "delete_webhook", "get_collaborators", "invite_collaborator", "update_collaborator", "remove_collaborator", "get_sync_status", "trigger_sync"]
            },
            "table_id": {
                "type": "string",
                "description": "Table ID or name for table-specific operations",
                "required": False,
                "group": "Resource",
                "examples": ["tblABC123DEF456", "Users", "Products"],
                "validation": {
                    "pattern": "^(tbl[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "Table ID must start with 'tbl' or be a valid table name"
                }
            },
            "record_id": {
                "type": "string",
                "description": "Record ID for specific record operations",
                "required": False,
                "group": "Resource",
                "examples": ["recABC123DEF456", "recXYZ789GHI012"],
                "validation": {
                    "pattern": "^rec[a-zA-Z0-9]{14}$",
                    "message": "Record ID must start with 'rec' followed by 14 alphanumeric characters"
                }
            },
            "field_id": {
                "type": "string",
                "description": "Field ID for field-specific operations",
                "required": False,
                "group": "Resource",
                "examples": ["fldABC123DEF456", "Name", "Email"],
                "validation": {
                    "pattern": "^(fld[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "Field ID must start with 'fld' or be a valid field name"
                }
            },
            "view_id": {
                "type": "string",
                "description": "View ID for view-specific operations",
                "required": False,
                "group": "Resource",
                "examples": ["viwABC123DEF456", "Grid View", "Calendar"],
                "validation": {
                    "pattern": "^(viw[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "View ID must start with 'viw' or be a valid view name"
                }
            },
            "comment_id": {
                "type": "string",
                "description": "Comment ID for comment operations",
                "required": False,
                "group": "Resource",
                "examples": ["comABC123DEF456"],
                "validation": {
                    "pattern": "^com[a-zA-Z0-9]{14}$",
                    "message": "Comment ID must start with 'com' followed by 14 alphanumeric characters"
                }
            },
            "webhook_id": {
                "type": "string",
                "description": "Webhook ID for webhook operations",
                "required": False,
                "group": "Resource",
                "examples": ["achABC123DEF456"],
                "validation": {
                    "pattern": "^ach[a-zA-Z0-9]{14}$",
                    "message": "Webhook ID must start with 'ach' followed by 14 alphanumeric characters"
                }
            },
            "collaborator_id": {
                "type": "string",
                "description": "Collaborator ID or email for collaboration operations",
                "required": False,
                "group": "Resource",
                "examples": ["usrABC123DEF456", "user@example.com"],
                "validation": {
                    "pattern": "^(usr[a-zA-Z0-9]{14}|[^@]+@[^@]+\\.[^@]+)$",
                    "message": "Collaborator ID must be valid user ID or email address"
                }
            },
            "fields": {
                "type": "array",
                "description": "Array of field names to retrieve (for list/get operations)",
                "required": False,
                "group": "Filtering",
                "examples": [["Name", "Email", "Status"], ["Title", "Description", "Created"]],
                "validation": {
                    "items": {"type": "string", "maxLength": 255},
                    "maxItems": 100
                }
            },
            "filter_by_formula": {
                "type": "string",
                "description": "Airtable formula for filtering records",
                "required": False,
                "group": "Filtering",
                "examples": [
                    "{Status} = 'Active'",
                    "AND({Age} > 18, {Country} = 'US')",
                    "FIND('gmail', {Email}) > 0"
                ],
                "validation": {
                    "maxLength": 1000
                }
            },
            "sort": {
                "type": "array",
                "description": "Array of sort objects for ordering results",
                "required": False,
                "group": "Sorting",
                "examples": [
                    [{"field": "Name", "direction": "asc"}],
                    [{"field": "Created", "direction": "desc"}, {"field": "Name", "direction": "asc"}]
                ]
            },
            "view": {
                "type": "string",
                "description": "View ID or name to use for the query",
                "required": False,
                "group": "Filtering",
                "examples": ["viwABC123DEF456", "Grid view", "Active Users"],
                "validation": {
                    "pattern": "^(viw[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "View must be a valid view ID or name"
                }
            },
            "max_records": {
                "type": "integer",
                "description": "Maximum number of records to return (max 100)",
                "required": False,
                "default": 100,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 100
                },
                "examples": [10, 50, 100]
            },
            "page_size": {
                "type": "integer", 
                "description": "Number of records per page for pagination (max 100)",
                "required": False,
                "default": 100,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 100
                },
                "examples": [20, 50, 100]
            },
            "offset": {
                "type": "string",
                "description": "Pagination offset token from previous response",
                "required": False,
                "group": "Pagination",
                "examples": ["recABC123DEF456"]
            },
            "records": {
                "type": "array",
                "description": "Array of record objects for create/update operations",
                "required": False,
                "group": "Data",
                "examples": [[
                    {"fields": {"Name": "John Doe", "Email": "john@example.com", "Age": 30}},
                    {"fields": {"Name": "Jane Smith", "Email": "jane@example.com", "Age": 25}}
                ]],
                "validation": {
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "pattern": "^rec[a-zA-Z0-9]{14}$"},
                            "fields": {"type": "object"}
                        }
                    },
                    "maxItems": 10
                }
            },
            "table_data": {
                "type": "object",
                "description": "Table configuration data for create/update table operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "name": "New Table",
                    "description": "A new table for storing data",
                    "fields": [
                        {"name": "Name", "type": "singleLineText"},
                        {"name": "Email", "type": "email"},
                        {"name": "Age", "type": "number", "options": {"precision": 0}}
                    ]
                }]
            },
            "field_data": {
                "type": "object",
                "description": "Field configuration data for create/update field operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "name": "Phone Number",
                    "type": "phoneNumber",
                    "description": "Customer phone number"
                }]
            },
            "view_data": {
                "type": "object",
                "description": "View configuration data for create/update view operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "name": "Active Users",
                    "type": "grid",
                    "filter": {"filterByFormula": "{Status} = 'Active'"}
                }]
            },
            "comment_data": {
                "type": "object",
                "description": "Comment data for create/update operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "text": "This record needs review",
                    "mentions": {"users": ["usrABC123DEF456"]}
                }]
            },
            "webhook_data": {
                "type": "object",
                "description": "Webhook configuration data for create/update operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "notificationUrl": "https://example.com/webhook",
                    "specification": {
                        "options": {
                            "filters": {
                                "dataTypes": ["tableData"]
                            }
                        }
                    }
                }]
            },
            "collaborator_data": {
                "type": "object",
                "description": "Collaborator data for invite/update operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "email": "user@example.com",
                    "permissionLevel": "editor"
                }]
            },
            "return_fields_by_field_id": {
                "type": "boolean",
                "description": "Return field values using field IDs instead of names",
                "required": False,
                "default": False,
                "group": "Options"
            },
            "typecast": {
                "type": "boolean",
                "description": "Automatically typecast field values",
                "required": False,
                "default": False,
                "group": "Options"
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful Airtable API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from Airtable API"},
                    "result": {"type": "object", "description": "Full API response data"},
                    "resource_id": {"type": "string", "description": "Resource ID for created/updated items"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Airtable error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            # Base operations
            "get_bases": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "get_base": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "create_base": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "update_base": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "delete_base": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            
            # Table operations
            "get_tables": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "get_table": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "create_table": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "update_table": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "delete_table": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            
            # Record operations
            "get_records": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "get_record": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "create_record": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "create_records": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "update_record": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "update_records": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "delete_record": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "delete_records": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            
            # Field operations
            "get_fields": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "get_field": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "create_field": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "update_field": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "delete_field": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            
            # View operations
            "get_views": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "get_view": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "create_view": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "update_view": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "delete_view": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            
            # Comment operations
            "get_comments": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "create_comment": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "update_comment": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "delete_comment": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            
            # Webhook operations
            "get_webhooks": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "create_webhook": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "update_webhook": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "delete_webhook": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            
            # Collaboration operations
            "get_collaborators": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "invite_collaborator": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "update_collaborator": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "remove_collaborator": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            
            # Sync operations
            "get_sync_status": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            },
            "trigger_sync": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"]
            }
        },
        
        # Error codes specific to Airtable
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid or missing access token",
            "403": "Forbidden - Access denied to resource or insufficient permissions",
            "404": "Not Found - Base, table, record, or field not found",
            "413": "Request Entity Too Large - Request payload too large",
            "422": "Unprocessable Entity - Validation errors in request data",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Airtable server error",
            "502": "Bad Gateway - Airtable server temporarily unavailable",
            "503": "Service Unavailable - Airtable server overloaded"
        }
    }
    
    # Enhanced operation definitions with ALL 13 features - ALL 42 ORIGINAL OPERATIONS RESTORED WITH ARRAY TEMPLATES
    OPERATIONS = {
        # BASE OPERATIONS (5)
        "get_bases": {
            "method": "GET",
            "endpoint": "/meta/bases",
            "required_params": [],
            "optional_params": [],
            "display_name": "List Bases",
            "description": "Retrieve all bases accessible to the authenticated user",
            "group": "Bases",
            "tags": ["bases", "list", "meta"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object", 
                    "properties": {
                        "bases": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string", "description": "Base ID"},
                                    "name": {"type": "string", "description": "Base name"},
                                    "permissionLevel": {"type": "string", "enum": ["none", "read", "comment", "edit", "create"]}
                                }
                            }
                        }
                    }
                }
            },
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": [],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "List all accessible bases",
                    "description": "Get all bases the user has access to",
                    "input": {}
                }
            ]
        },
        "get_base": {
            "method": "GET",
            "endpoint": "/meta/bases/{base_id}",
            "required_params": ["base_id"],
            "optional_params": [],
            "display_name": "Get Base Schema",
            "description": "Retrieve base schema information including tables and fields",
            "group": "Bases",
            "tags": ["bases", "schema", "meta"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "tables": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "primaryFieldId": {"type": "string"},
                                    "fields": {"type": "array"},
                                    "views": {"type": "array"}
                                }
                            }
                        }
                    }
                }
            },
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must start with 'app' followed by 14 characters",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Get base schema",
                    "description": "Retrieve complete schema for a base",
                    "input": {"base_id": "appABC123DEF456"}
                }
            ]
        },
        "create_base": {
            "method": "POST",
            "endpoint": "/meta/bases",
            "required_params": ["base_data"],
            "optional_params": [],
            "body_parameters": ["base_data"],
            "display_name": "Create Base",
            "description": "Create a new Airtable base",
            "group": "Bases",
            "tags": ["bases", "create"],
            "rate_limit_cost": 5,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Created base ID"},
                        "name": {"type": "string"},
                        "workspaceId": {"type": "string"}
                    }
                }
            },
            "array_templates": {
                "base_data": [
                    {
                        "template": {
                            "name": "My New Base", 
                            "tables": [
                                {
                                    "name": "Main Table", 
                                    "fields": [
                                        {"name": "Name", "type": "singleLineText"},
                                        {"name": "Status", "type": "singleSelect", "options": {"choices": [{"name": "Active"}, {"name": "Inactive"}]}}
                                    ]
                                }
                            ]
                        },
                        "description": "Basic base with one table and essential fields"
                    }
                ]
            },
            "validation_rules": {
                "base_data": {
                    "pattern": "",
                    "message": "Base data is required with name and optional tables",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": [],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Create simple base",
                    "description": "Create a base with one table",
                    "input": {
                        "base_data": {
                            "name": "Project Management",
                            "tables": [
                                {
                                    "name": "Tasks",
                                    "fields": [
                                        {"name": "Task Name", "type": "singleLineText"},
                                        {"name": "Status", "type": "singleSelect", "options": {"choices": [{"name": "To Do"}, {"name": "In Progress"}, {"name": "Done"}]}},
                                        {"name": "Due Date", "type": "date"}
                                    ]
                                }
                            ]
                        }
                    }
                }
            ]
        },
        "update_base": {
            "method": "PATCH",
            "endpoint": "/meta/bases/{base_id}",
            "required_params": ["base_id", "base_data"],
            "optional_params": [],
            "body_parameters": ["base_data"],
            "display_name": "Update Base",
            "description": "Update base properties",
            "group": "Bases",
            "tags": ["bases", "update"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid Airtable base identifier",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Update base name",
                    "description": "Change the name of a base",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "base_data": {"name": "Updated Project Management"}
                    }
                }
            ]
        },
        "delete_base": {
            "method": "DELETE", 
            "endpoint": "/meta/bases/{base_id}",
            "required_params": ["base_id"],
            "optional_params": [],
            "display_name": "Delete Base",
            "description": "Permanently delete a base",
            "group": "Bases",
            "tags": ["bases", "delete"],
            "rate_limit_cost": 5,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid Airtable base identifier",
                    "pattern_type": "regex", 
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Delete base",
                    "description": "Permanently delete a base",
                    "input": {"base_id": "appABC123DEF456"}
                }
            ]
        },

        # TABLE OPERATIONS (5)
        "get_tables": {
            "method": "GET",
            "endpoint": "/meta/bases/{base_id}/tables",
            "required_params": ["base_id"],
            "optional_params": [],
            "display_name": "List Tables",
            "description": "Get all tables in a base",
            "group": "Tables",
            "tags": ["tables", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "tables": {
                            "type": "array",
                            "items": {
                                "type": "object", 
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "primaryFieldId": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "List all tables",
                    "description": "Get all tables in a base",
                    "input": {"base_id": "appABC123DEF456"}
                }
            ]
        },
        "get_table": {
            "method": "GET",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}",
            "required_params": ["base_id", "table_id"],
            "optional_params": [],
            "display_name": "Get Table Schema",
            "description": "Get detailed table schema including fields and views",
            "group": "Tables",
            "tags": ["tables", "schema"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "table_id": {
                    "pattern": "^(tbl[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "Table ID must be valid table identifier or name",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Get table schema",
                    "description": "Retrieve detailed schema for a table",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012"
                    }
                }
            ]
        },
        "create_table": {
            "method": "POST",
            "endpoint": "/meta/bases/{base_id}/tables",
            "required_params": ["base_id", "table_data"],
            "optional_params": [],
            "body_parameters": ["table_data"],
            "display_name": "Create Table",
            "description": "Create a new table in a base",
            "group": "Tables",
            "tags": ["tables", "create"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "table_data": [
                    {
                        "template": {
                            "name": "New Table",
                            "fields": [
                                {"name": "Name", "type": "singleLineText"},
                                {"name": "Status", "type": "singleSelect", "options": {"choices": [{"name": "Active"}, {"name": "Inactive"}]}},
                                {"name": "Email", "type": "email"},
                                {"name": "Phone", "type": "phoneNumber"},
                                {"name": "Created", "type": "dateTime"}
                            ]
                        },
                        "description": "Basic table with essential field types"
                    }
                ]
            },
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "table_data": {
                    "pattern": "",
                    "message": "Table data is required with name and fields",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Create contacts table",
                    "description": "Create a table for managing contacts",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_data": {
                            "name": "Contacts",
                            "fields": [
                                {"name": "Name", "type": "singleLineText"},
                                {"name": "Email", "type": "email"},
                                {"name": "Phone", "type": "phoneNumber"},
                                {"name": "Company", "type": "singleLineText"}
                            ]
                        }
                    }
                }
            ]
        },
        "update_table": {
            "method": "PATCH",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}",
            "required_params": ["base_id", "table_id", "table_data"],
            "optional_params": [],
            "body_parameters": ["table_data"],
            "display_name": "Update Table",
            "description": "Update table properties like name and description",
            "group": "Tables",
            "tags": ["tables", "update"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "table_id": {
                    "pattern": "^(tbl[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "Table ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Update table name",
                    "description": "Change table name and description",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "table_data": {
                            "name": "Updated Table Name",
                            "description": "Updated table description"
                        }
                    }
                }
            ]
        },
        "delete_table": {
            "method": "DELETE",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}",
            "required_params": ["base_id", "table_id"],
            "optional_params": [],
            "display_name": "Delete Table",
            "description": "Permanently delete a table and all its data",
            "group": "Tables",
            "tags": ["tables", "delete"],
            "rate_limit_cost": 5,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "table_id": {
                    "pattern": "^(tbl[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "Table ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Delete table",
                    "description": "Permanently delete a table",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012"
                    }
                }
            ]
        },

        # RECORD OPERATIONS (8) 
        "get_records": {
            "method": "GET",
            "endpoint": "/{base_id}/{table_id}",
            "required_params": ["base_id", "table_id"],
            "optional_params": ["fields", "filter_by_formula", "sort", "view", "max_records", "page_size", "offset", "return_fields_by_field_id"],
            "display_name": "List Records",
            "description": "Retrieve records from a table in an Airtable base",
            "group": "Records",
            "tags": ["records", "list", "query"],
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
                                    "createdTime": {"type": "string", "format": "date-time"},
                                    "fields": {
                                        "type": "object",
                                        "description": "Record field values",
                                        "additionalProperties": True
                                    }
                                }
                            }
                        },
                        "offset": {"type": "string", "description": "Pagination offset for next page"}
                    }
                }
            },
            
            "array_templates": {
                "fields": [
                    {"template": "Name", "description": "Field name to retrieve"},
                    {"template": "Email", "description": "Another field name"},
                    {"template": "Status", "description": "Status field"}
                ],
                "sort": [
                    {"template": {"field": "Name", "direction": "asc"}, "description": "Sort ascending by Name"},
                    {"template": {"field": "Created", "direction": "desc"}, "description": "Sort descending by Created date"},
                    {"template": {"field": "Priority", "direction": "asc"}, "description": "Sort by priority"}
                ]
            },
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must start with 'app' followed by 14 characters",
                    "pattern_type": "regex",
                    "required": True
                },
                "table_id": {
                    "pattern": "^(tbl[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "Table ID must be valid table identifier or name",
                    "pattern_type": "regex",
                    "required": True
                },
                "max_records": {
                    "pattern": "",
                    "message": "Max records must be between 1 and 100",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "max_value": 100,
                    "required": False
                }
            },
            
            "pagination": {
                "type": "cursor",
                "cursor_param": "offset",
                "size_param": "pageSize",
                "default_size": 100,
                "max_size": 100,
                "has_more_field": "offset",
                "next_cursor_field": "offset"
            },
            
            "field_mapping": {
                "input_transforms": {
                    "sort": "validate_sort_array"
                },
                "output_transforms": {
                    "createdTime": "format_timestamp"
                },
                "field_aliases": {
                    "page_size": "pageSize",
                    "max_records": "maxRecords",
                    "filter_formula": "filterByFormula"
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Airtable Personal Access Token or OAuth token"
            },
            "examples": [
                {
                    "name": "List all records",
                    "description": "Get all records from a table",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012"
                    }
                },
                {
                    "name": "List records with filters",
                    "description": "Get filtered records with specific fields",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "Users",
                        "fields": ["Name", "Email", "Status"],
                        "filter_by_formula": "{Status} = 'Active'",
                        "sort": [{"field": "Name", "direction": "asc"}],
                        "max_records": 50
                    }
                }
            ]
        },
        "get_record": {
            "method": "GET",
            "endpoint": "/{base_id}/{table_id}/{record_id}",
            "required_params": ["base_id", "table_id", "record_id"],
            "optional_params": ["return_fields_by_field_id"],
            "display_name": "Get Record",
            "description": "Retrieve a specific record by ID",
            "group": "Records",
            "tags": ["records", "get", "single"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Record ID"},
                        "createdTime": {"type": "string", "format": "date-time"},
                        "fields": {
                            "type": "object",
                            "description": "Record field values",
                            "additionalProperties": True
                        }
                    }
                }
            },
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid Airtable base identifier",
                    "pattern_type": "regex",
                    "required": True
                },
                "record_id": {
                    "pattern": "^rec[a-zA-Z0-9]{14}$",
                    "message": "Record ID must start with 'rec' followed by 14 characters",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Airtable Personal Access Token or OAuth token"
            },
            "examples": [
                {
                    "name": "Get specific record",
                    "description": "Retrieve a record by its ID",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "Users",
                        "record_id": "recABC123DEF456"
                    }
                }
            ]
        },
        "create_record": {
            "method": "POST",
            "endpoint": "/{base_id}/{table_id}",
            "required_params": ["base_id", "table_id", "records"],
            "optional_params": ["typecast", "return_fields_by_field_id"],
            "body_parameters": ["records"],
            "display_name": "Create Record",
            "description": "Create a single record in a table",
            "group": "Records",
            "tags": ["records", "create", "single"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "records": [
                    {
                        "template": {"fields": {"Name": "John Doe", "Email": "john@example.com", "Age": 30}},
                        "description": "Basic user record with name, email and age"
                    }
                ]
            },
            
            "validation_rules": {
                "records": {
                    "pattern": "",
                    "message": "Records array is required with at least one record",
                    "pattern_type": "custom",
                    "required": True,
                    "min_items": 1,
                    "max_items": 1
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Create single record",
                    "description": "Create one new record",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "Users",
                        "records": [
                            {"fields": {"Name": "Alice Johnson", "Email": "alice@example.com", "Status": "Active"}}
                        ]
                    }
                }
            ]
        },
        "create_records": {
            "method": "POST",
            "endpoint": "/{base_id}/{table_id}",
            "required_params": ["base_id", "table_id", "records"],
            "optional_params": ["typecast", "return_fields_by_field_id"],
            "body_parameters": ["records"],
            "display_name": "Create Records",
            "description": "Create one or more records in a table",
            "group": "Records",
            "tags": ["records", "create", "bulk"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
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
                                    "id": {"type": "string", "description": "Created record ID"},
                                    "createdTime": {"type": "string", "format": "date-time"},
                                    "fields": {
                                        "type": "object",
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            "array_templates": {
                "records": [
                    {
                        "template": {"fields": {"Name": "John Doe", "Email": "john@example.com", "Age": 30}},
                        "description": "Record with basic user fields"
                    },
                    {
                        "template": {"fields": {"Name": "Jane Smith", "Email": "jane@example.com", "Age": 25}},
                        "description": "Another user record"
                    },
                    {
                        "template": {"fields": {"Title": "Project Alpha", "Status": "In Progress", "Priority": "High"}},
                        "description": "Project record with status and priority"
                    }
                ]
            },
            
            "parameter_dependencies": [
                {
                    "when_field": "records",
                    "when_value": "exists",
                    "then_require": [],
                    "then_optional": ["typecast"],
                    "require_one_of": ["records"],
                    "mutually_exclusive": []
                }
            ],
            
            "validation_rules": {
                "records": {
                    "pattern": "",
                    "message": "Records array is required and must contain valid record objects",
                    "pattern_type": "custom",
                    "required": True,
                    "min_items": 1,
                    "max_items": 10
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Airtable Personal Access Token or OAuth token"
            },
            "examples": [
                {
                    "name": "Create multiple records",
                    "description": "Create multiple records in a single request",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "Products",
                        "records": [
                            {"fields": {"Name": "Product A", "Price": 29.99, "Category": "Electronics"}},
                            {"fields": {"Name": "Product B", "Price": 49.99, "Category": "Books"}},
                            {"fields": {"Name": "Product C", "Price": 19.99, "Category": "Home"}}
                        ],
                        "typecast": True
                    }
                }
            ]
        },
        "update_record": {
            "method": "PATCH",
            "endpoint": "/{base_id}/{table_id}/{record_id}",
            "required_params": ["base_id", "table_id", "record_id", "records"],
            "optional_params": ["typecast", "return_fields_by_field_id"],
            "body_parameters": ["records"],
            "display_name": "Update Record",
            "description": "Update a specific record by ID",
            "group": "Records",
            "tags": ["records", "update", "single"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "records": [
                    {
                        "template": {"fields": {"Name": "Updated Name", "Status": "Updated Status"}},
                        "description": "Updated field values for a record"
                    }
                ]
            },
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "record_id": {
                    "pattern": "^rec[a-zA-Z0-9]{14}$",
                    "message": "Record ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Update record",
                    "description": "Update fields in a specific record",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "Users",
                        "record_id": "recABC123DEF456",
                        "records": [
                            {"fields": {"Status": "Inactive", "LastUpdated": "2023-12-01"}}
                        ]
                    }
                }
            ]
        },
        "update_records": {
            "method": "PATCH",
            "endpoint": "/{base_id}/{table_id}",
            "required_params": ["base_id", "table_id", "records"],
            "optional_params": ["typecast", "return_fields_by_field_id"],
            "body_parameters": ["records"],
            "display_name": "Update Records",
            "description": "Update multiple records in a table",
            "group": "Records",
            "tags": ["records", "update", "bulk"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "records": [
                    {
                        "template": {"id": "recABC123DEF456", "fields": {"Status": "Updated"}},
                        "description": "Record with ID and updated fields"
                    },
                    {
                        "template": {"id": "recXYZ789GHI012", "fields": {"Status": "Updated", "Priority": "High"}},
                        "description": "Another record with multiple field updates"
                    }
                ]
            },
            
            "validation_rules": {
                "records": {
                    "pattern": "",
                    "message": "Records array is required with record IDs and field updates",
                    "pattern_type": "custom",
                    "required": True,
                    "min_items": 1,
                    "max_items": 10
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Update multiple records",
                    "description": "Update several records at once",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "Tasks",
                        "records": [
                            {"id": "recABC123DEF456", "fields": {"Status": "Completed", "CompletedDate": "2023-12-01"}},
                            {"id": "recXYZ789GHI012", "fields": {"Status": "In Progress", "Priority": "High"}}
                        ]
                    }
                }
            ]
        },
        "delete_record": {
            "method": "DELETE",
            "endpoint": "/{base_id}/{table_id}/{record_id}",
            "required_params": ["base_id", "table_id", "record_id"],
            "optional_params": [],
            "display_name": "Delete Record",
            "description": "Delete a specific record by ID",
            "group": "Records",
            "tags": ["records", "delete", "single"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "record_id": {
                    "pattern": "^rec[a-zA-Z0-9]{14}$",
                    "message": "Record ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Delete record",
                    "description": "Delete a specific record",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "Users",
                        "record_id": "recABC123DEF456"
                    }
                }
            ]
        },
        "delete_records": {
            "method": "DELETE",
            "endpoint": "/{base_id}/{table_id}",
            "required_params": ["base_id", "table_id", "records"],
            "optional_params": [],
            "query_parameters": ["records"],
            "display_name": "Delete Records",
            "description": "Delete multiple records by ID",
            "group": "Records",
            "tags": ["records", "delete", "bulk"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "records": [
                    {"template": "recABC123DEF456", "description": "Record ID to delete"},
                    {"template": "recXYZ789GHI012", "description": "Another record ID to delete"}
                ]
            },
            
            "validation_rules": {
                "records": {
                    "pattern": "",
                    "message": "Records array is required with record IDs to delete",
                    "pattern_type": "custom",
                    "required": True,
                    "min_items": 1,
                    "max_items": 10
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Delete multiple records",
                    "description": "Delete several records at once",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "Tasks",
                        "records": ["recABC123DEF456", "recXYZ789GHI012", "recLMN456OPQ789"]
                    }
                }
            ]
        },

        # FIELD OPERATIONS (5)
        "get_fields": {
            "method": "GET",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}/fields",
            "required_params": ["base_id", "table_id"],
            "optional_params": [],
            "display_name": "List Fields",
            "description": "Get all fields in a table",
            "group": "Fields",
            "tags": ["fields", "list", "schema"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "fields": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "description": {"type": "string"},
                                    "options": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "table_id": {
                    "pattern": "^(tbl[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "Table ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "List table fields",
                    "description": "Get all fields in a table",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012"
                    }
                }
            ]
        },
        "get_field": {
            "method": "GET",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}/fields/{field_id}",
            "required_params": ["base_id", "table_id", "field_id"],
            "optional_params": [],
            "display_name": "Get Field",
            "description": "Get detailed information about a specific field",
            "group": "Fields",
            "tags": ["fields", "get", "single"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "field_id": {
                    "pattern": "^(fld[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "Field ID must be valid field identifier or name",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Get field details",
                    "description": "Retrieve detailed information about a field",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "field_id": "fldABC123DEF456"
                    }
                }
            ]
        },
        "create_field": {
            "method": "POST",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}/fields",
            "required_params": ["base_id", "table_id", "field_data"],
            "optional_params": [],
            "body_parameters": ["field_data"],
            "display_name": "Create Field",
            "description": "Create a new field in a table",
            "group": "Fields",
            "tags": ["fields", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "field_data": [
                    {
                        "template": {"name": "Email", "type": "email", "description": "User email address"},
                        "description": "Email field with validation"
                    },
                    {
                        "template": {"name": "Status", "type": "singleSelect", "options": {"choices": [{"name": "Active"}, {"name": "Inactive"}, {"name": "Pending"}]}},
                        "description": "Single select field with predefined choices"
                    },
                    {
                        "template": {"name": "Tags", "type": "multipleSelects", "options": {"choices": [{"name": "Important"}, {"name": "Urgent"}, {"name": "Review"}]}},
                        "description": "Multiple select field for tags"
                    },
                    {
                        "template": {"name": "Due Date", "type": "date", "options": {"dateFormat": {"name": "us"}}},
                        "description": "Date field with US format"
                    },
                    {
                        "template": {"name": "Price", "type": "currency", "options": {"precision": 2, "symbol": "$"}},
                        "description": "Currency field for pricing"
                    }
                ]
            },
            
            "validation_rules": {
                "field_data": {
                    "pattern": "",
                    "message": "Field data is required with name and type",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Create email field",
                    "description": "Create a field for email addresses",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "field_data": {
                            "name": "Email Address",
                            "type": "email",
                            "description": "Primary email address for contact"
                        }
                    }
                }
            ]
        },
        "update_field": {
            "method": "PATCH",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}/fields/{field_id}",
            "required_params": ["base_id", "table_id", "field_id", "field_data"],
            "optional_params": [],
            "body_parameters": ["field_data"],
            "display_name": "Update Field",
            "description": "Update field properties",
            "group": "Fields",
            "tags": ["fields", "update"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "field_id": {
                    "pattern": "^(fld[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "Field ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Update field name",
                    "description": "Change field name and description",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "field_id": "fldABC123DEF456",
                        "field_data": {
                            "name": "Updated Field Name",
                            "description": "Updated field description"
                        }
                    }
                }
            ]
        },
        "delete_field": {
            "method": "DELETE",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}/fields/{field_id}",
            "required_params": ["base_id", "table_id", "field_id"],
            "optional_params": [],
            "display_name": "Delete Field",
            "description": "Permanently delete a field and all its data",
            "group": "Fields",
            "tags": ["fields", "delete"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "field_id": {
                    "pattern": "^(fld[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "Field ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Delete field",
                    "description": "Permanently delete a field",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "field_id": "fldABC123DEF456"
                    }
                }
            ]
        },

        # VIEW OPERATIONS (5)
        "get_views": {
            "method": "GET",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}/views",
            "required_params": ["base_id", "table_id"],
            "optional_params": [],
            "display_name": "List Views",
            "description": "Get all views in a table",
            "group": "Views",
            "tags": ["views", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "views": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "type": {"type": "string", "enum": ["grid", "form", "calendar", "gallery", "kanban", "timeline"]}
                                }
                            }
                        }
                    }
                }
            },
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "table_id": {
                    "pattern": "^(tbl[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "Table ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "List table views",
                    "description": "Get all views in a table",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012"
                    }
                }
            ]
        },
        "get_view": {
            "method": "GET",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}/views/{view_id}",
            "required_params": ["base_id", "table_id", "view_id"],
            "optional_params": [],
            "display_name": "Get View",
            "description": "Get detailed information about a specific view",
            "group": "Views",
            "tags": ["views", "get", "single"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "view_id": {
                    "pattern": "^(viw[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "View ID must be valid view identifier or name",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Get view details",
                    "description": "Retrieve detailed information about a view",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "view_id": "viwABC123DEF456"
                    }
                }
            ]
        },
        "create_view": {
            "method": "POST",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}/views",
            "required_params": ["base_id", "table_id", "view_data"],
            "optional_params": [],
            "body_parameters": ["view_data"],
            "display_name": "Create View",
            "description": "Create a new view in a table",
            "group": "Views",
            "tags": ["views", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "view_data": [
                    {
                        "template": {
                            "name": "Active Users",
                            "type": "grid",
                            "filter": {"filterByFormula": "{Status} = 'Active'"}
                        },
                        "description": "Grid view showing only active users"
                    },
                    {
                        "template": {
                            "name": "Priority Tasks",
                            "type": "kanban",
                            "groupingFieldId": "fldStatus123",
                            "filter": {"filterByFormula": "{Priority} = 'High'"}
                        },
                        "description": "Kanban view for high-priority tasks"
                    },
                    {
                        "template": {
                            "name": "Project Calendar",
                            "type": "calendar",
                            "dateFieldId": "fldDueDate123"
                        },
                        "description": "Calendar view showing project due dates"
                    }
                ]
            },
            
            "validation_rules": {
                "view_data": {
                    "pattern": "",
                    "message": "View data is required with name and type",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Create grid view",
                    "description": "Create a filtered grid view",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "view_data": {
                            "name": "Active Contacts",
                            "type": "grid",
                            "filter": {
                                "filterByFormula": "{Status} = 'Active'"
                            }
                        }
                    }
                }
            ]
        },
        "update_view": {
            "method": "PATCH",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}/views/{view_id}",
            "required_params": ["base_id", "table_id", "view_id", "view_data"],
            "optional_params": [],
            "body_parameters": ["view_data"],
            "display_name": "Update View",
            "description": "Update view properties",
            "group": "Views",
            "tags": ["views", "update"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "view_id": {
                    "pattern": "^(viw[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "View ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Update view name",
                    "description": "Change view name and filter",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "view_id": "viwABC123DEF456",
                        "view_data": {
                            "name": "Updated View Name",
                            "filter": {
                                "filterByFormula": "{Status} = 'Updated'"
                            }
                        }
                    }
                }
            ]
        },
        "delete_view": {
            "method": "DELETE",
            "endpoint": "/meta/bases/{base_id}/tables/{table_id}/views/{view_id}",
            "required_params": ["base_id", "table_id", "view_id"],
            "optional_params": [],
            "display_name": "Delete View",
            "description": "Permanently delete a view",
            "group": "Views",
            "tags": ["views", "delete"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "view_id": {
                    "pattern": "^(viw[a-zA-Z0-9]{14}|[a-zA-Z0-9\\s_-]+)$",
                    "message": "View ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Delete view",
                    "description": "Permanently delete a view",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "view_id": "viwABC123DEF456"
                    }
                }
            ]
        },

        # COMMENT OPERATIONS (4)
        "get_comments": {
            "method": "GET",
            "endpoint": "/{base_id}/{table_id}/{record_id}/comments",
            "required_params": ["base_id", "table_id", "record_id"],
            "optional_params": ["page_size", "offset"],
            "display_name": "List Comments",
            "description": "Get all comments on a record",
            "group": "Comments",
            "tags": ["comments", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "comments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "text": {"type": "string"},
                                    "createdTime": {"type": "string", "format": "date-time"},
                                    "author": {"type": "object"}
                                }
                            }
                        },
                        "offset": {"type": "string"}
                    }
                }
            },
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "record_id": {
                    "pattern": "^rec[a-zA-Z0-9]{14}$",
                    "message": "Record ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "List record comments",
                    "description": "Get all comments on a record",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "record_id": "recABC123DEF456"
                    }
                }
            ]
        },
        "create_comment": {
            "method": "POST",
            "endpoint": "/{base_id}/{table_id}/{record_id}/comments",
            "required_params": ["base_id", "table_id", "record_id", "comment_data"],
            "optional_params": [],
            "body_parameters": ["comment_data"],
            "display_name": "Create Comment",
            "description": "Create a new comment on a record",
            "group": "Comments",
            "tags": ["comments", "create"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "comment_data": [
                    {
                        "template": {
                            "text": "This record needs review",
                            "mentions": {"users": ["usrABC123DEF456"]}
                        },
                        "description": "Basic comment with user mention"
                    },
                    {
                        "template": {
                            "text": "Updated the status - please check the new information",
                            "mentions": {"users": ["usrABC123DEF456", "usrXYZ789GHI012"]}
                        },
                        "description": "Comment with multiple user mentions"
                    }
                ]
            },
            
            "validation_rules": {
                "comment_data": {
                    "pattern": "",
                    "message": "Comment data is required with text",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Create comment",
                    "description": "Add a comment to a record",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "record_id": "recABC123DEF456",
                        "comment_data": {
                            "text": "This record needs follow-up action"
                        }
                    }
                }
            ]
        },
        "update_comment": {
            "method": "PATCH",
            "endpoint": "/{base_id}/{table_id}/{record_id}/comments/{comment_id}",
            "required_params": ["base_id", "table_id", "record_id", "comment_id", "comment_data"],
            "optional_params": [],
            "body_parameters": ["comment_data"],
            "display_name": "Update Comment",
            "description": "Update an existing comment",
            "group": "Comments",
            "tags": ["comments", "update"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "comment_id": {
                    "pattern": "^com[a-zA-Z0-9]{14}$",
                    "message": "Comment ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Update comment",
                    "description": "Edit an existing comment",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "record_id": "recABC123DEF456",
                        "comment_id": "comABC123DEF456",
                        "comment_data": {
                            "text": "Updated comment text"
                        }
                    }
                }
            ]
        },
        "delete_comment": {
            "method": "DELETE",
            "endpoint": "/{base_id}/{table_id}/{record_id}/comments/{comment_id}",
            "required_params": ["base_id", "table_id", "record_id", "comment_id"],
            "optional_params": [],
            "display_name": "Delete Comment",
            "description": "Delete a comment",
            "group": "Comments",
            "tags": ["comments", "delete"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "comment_id": {
                    "pattern": "^com[a-zA-Z0-9]{14}$",
                    "message": "Comment ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Delete comment",
                    "description": "Remove a comment from a record",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "table_id": "tblXYZ789GHI012",
                        "record_id": "recABC123DEF456",
                        "comment_id": "comABC123DEF456"
                    }
                }
            ]
        },

        # WEBHOOK OPERATIONS (4)
        "get_webhooks": {
            "method": "GET",
            "endpoint": "/bases/{base_id}/webhooks",
            "required_params": ["base_id"],
            "optional_params": [],
            "display_name": "List Webhooks",
            "description": "Get all webhooks for a base",
            "group": "Webhooks",
            "tags": ["webhooks", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "webhooks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "macSecretBase64": {"type": "string"},
                                    "notificationUrl": {"type": "string", "format": "uri"},
                                    "isHookEnabled": {"type": "boolean"},
                                    "cursorForNextPayload": {"type": "number"}
                                }
                            }
                        }
                    }
                }
            },
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "List base webhooks",
                    "description": "Get all webhooks configured for a base",
                    "input": {
                        "base_id": "appABC123DEF456"
                    }
                }
            ]
        },
        "create_webhook": {
            "method": "POST",
            "endpoint": "/bases/{base_id}/webhooks",
            "required_params": ["base_id", "webhook_data"],
            "optional_params": [],
            "body_parameters": ["webhook_data"],
            "display_name": "Create Webhook",
            "description": "Create a new webhook for a base",
            "group": "Webhooks",
            "tags": ["webhooks", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "webhook_data": [
                    {
                        "template": {
                            "notificationUrl": "https://example.com/webhook",
                            "specification": {
                                "options": {
                                    "filters": {
                                        "dataTypes": ["tableData"]
                                    }
                                }
                            }
                        },
                        "description": "Basic webhook for table data changes"
                    },
                    {
                        "template": {
                            "notificationUrl": "https://example.com/record-webhook",
                            "specification": {
                                "options": {
                                    "filters": {
                                        "dataTypes": ["tableData"],
                                        "recordChangeScope": "tblXYZ789GHI012"
                                    }
                                }
                            }
                        },
                        "description": "Webhook for specific table record changes"
                    }
                ]
            },
            
            "validation_rules": {
                "webhook_data": {
                    "pattern": "",
                    "message": "Webhook data is required with notificationUrl and specification",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Create webhook",
                    "description": "Create a webhook to monitor table changes",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "webhook_data": {
                            "notificationUrl": "https://myapp.example.com/airtable-webhook",
                            "specification": {
                                "options": {
                                    "filters": {
                                        "dataTypes": ["tableData"]
                                    }
                                }
                            }
                        }
                    }
                }
            ]
        },
        "update_webhook": {
            "method": "PATCH",
            "endpoint": "/bases/{base_id}/webhooks/{webhook_id}",
            "required_params": ["base_id", "webhook_id", "webhook_data"],
            "optional_params": [],
            "body_parameters": ["webhook_data"],
            "display_name": "Update Webhook",
            "description": "Update webhook configuration",
            "group": "Webhooks",
            "tags": ["webhooks", "update"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "webhook_id": {
                    "pattern": "^ach[a-zA-Z0-9]{14}$",
                    "message": "Webhook ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Update webhook",
                    "description": "Update webhook configuration",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "webhook_id": "achABC123DEF456",
                        "webhook_data": {
                            "isHookEnabled": False
                        }
                    }
                }
            ]
        },
        "delete_webhook": {
            "method": "DELETE",
            "endpoint": "/bases/{base_id}/webhooks/{webhook_id}",
            "required_params": ["base_id", "webhook_id"],
            "optional_params": [],
            "display_name": "Delete Webhook",
            "description": "Delete a webhook",
            "group": "Webhooks",
            "tags": ["webhooks", "delete"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "webhook_id": {
                    "pattern": "^ach[a-zA-Z0-9]{14}$",
                    "message": "Webhook ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Delete webhook",
                    "description": "Remove a webhook from a base",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "webhook_id": "achABC123DEF456"
                    }
                }
            ]
        },

        # COLLABORATION OPERATIONS (4)
        "get_collaborators": {
            "method": "GET",
            "endpoint": "/bases/{base_id}/collaborators",
            "required_params": ["base_id"],
            "optional_params": [],
            "display_name": "List Collaborators",
            "description": "Get all collaborators for a base",
            "group": "Collaboration",
            "tags": ["collaborators", "list", "permissions"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "collaborators": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "email": {"type": "string", "format": "email"},
                                    "name": {"type": "string"},
                                    "permissionLevel": {"type": "string", "enum": ["none", "read", "comment", "edit", "create"]}
                                }
                            }
                        }
                    }
                }
            },
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "List base collaborators",
                    "description": "Get all users who have access to a base",
                    "input": {
                        "base_id": "appABC123DEF456"
                    }
                }
            ]
        },
        "invite_collaborator": {
            "method": "POST",
            "endpoint": "/bases/{base_id}/collaborators",
            "required_params": ["base_id", "collaborator_data"],
            "optional_params": [],
            "body_parameters": ["collaborator_data"],
            "display_name": "Invite Collaborator",
            "description": "Invite a new collaborator to a base",
            "group": "Collaboration",
            "tags": ["collaborators", "invite"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "collaborator_data": [
                    {
                        "template": {
                            "email": "user@example.com",
                            "permissionLevel": "editor"
                        },
                        "description": "Invite user with editor permissions"
                    },
                    {
                        "template": {
                            "email": "viewer@example.com",
                            "permissionLevel": "read"
                        },
                        "description": "Invite user with read-only permissions"
                    },
                    {
                        "template": {
                            "email": "commenter@example.com",
                            "permissionLevel": "comment"
                        },
                        "description": "Invite user with comment permissions"
                    }
                ]
            },
            
            "validation_rules": {
                "collaborator_data": {
                    "pattern": "",
                    "message": "Collaborator data is required with email and permissionLevel",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Invite collaborator",
                    "description": "Invite a user to collaborate on a base",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "collaborator_data": {
                            "email": "colleague@example.com",
                            "permissionLevel": "editor"
                        }
                    }
                }
            ]
        },
        "update_collaborator": {
            "method": "PATCH",
            "endpoint": "/bases/{base_id}/collaborators/{collaborator_id}",
            "required_params": ["base_id", "collaborator_id", "collaborator_data"],
            "optional_params": [],
            "body_parameters": ["collaborator_data"],
            "display_name": "Update Collaborator",
            "description": "Update collaborator permissions",
            "group": "Collaboration",
            "tags": ["collaborators", "update", "permissions"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "collaborator_id": {
                    "pattern": "^(usr[a-zA-Z0-9]{14}|[^@]+@[^@]+\\.[^@]+)$",
                    "message": "Collaborator ID must be valid user ID or email",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Update collaborator permissions",
                    "description": "Change a collaborator's permission level",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "collaborator_id": "usrABC123DEF456",
                        "collaborator_data": {
                            "permissionLevel": "read"
                        }
                    }
                }
            ]
        },
        "remove_collaborator": {
            "method": "DELETE",
            "endpoint": "/bases/{base_id}/collaborators/{collaborator_id}",
            "required_params": ["base_id", "collaborator_id"],
            "optional_params": [],
            "display_name": "Remove Collaborator",
            "description": "Remove a collaborator from a base",
            "group": "Collaboration",
            "tags": ["collaborators", "remove"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                },
                "collaborator_id": {
                    "pattern": "^(usr[a-zA-Z0-9]{14}|[^@]+@[^@]+\\.[^@]+)$",
                    "message": "Collaborator ID must be valid user ID or email",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Remove collaborator",
                    "description": "Remove a user's access to a base",
                    "input": {
                        "base_id": "appABC123DEF456",
                        "collaborator_id": "usrABC123DEF456"
                    }
                }
            ]
        },

        # SYNC OPERATIONS (2)
        "get_sync_status": {
            "method": "GET",
            "endpoint": "/bases/{base_id}/sync",
            "required_params": ["base_id"],
            "optional_params": [],
            "display_name": "Get Sync Status",
            "description": "Get synchronization status for a base",
            "group": "Sync",
            "tags": ["sync", "status"],
            "rate_limit_cost": 1,
            "cache_ttl": 30,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "state": {"type": "string", "enum": ["initializing", "synced", "syncing", "failed"]},
                        "lastSyncTime": {"type": "string", "format": "date-time"},
                        "nextSyncTime": {"type": "string", "format": "date-time"}
                    }
                }
            },
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Get sync status",
                    "description": "Check the synchronization status of a base",
                    "input": {
                        "base_id": "appABC123DEF456"
                    }
                }
            ]
        },
        "trigger_sync": {
            "method": "POST",
            "endpoint": "/bases/{base_id}/sync",
            "required_params": ["base_id"],
            "optional_params": [],
            "display_name": "Trigger Sync",
            "description": "Manually trigger synchronization for a base",
            "group": "Sync",
            "tags": ["sync", "trigger"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "base_id": {
                    "pattern": "^app[a-zA-Z0-9]{14}$",
                    "message": "Base ID must be valid",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AIRTABLE_ACCESS_TOKEN"],
                "optional_env_keys": ["AIRTABLE_BASE_ID"],
                "required_params": ["access_token"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Trigger sync",
                    "description": "Manually start synchronization for a base",
                    "input": {
                        "base_id": "appABC123DEF456"
                    }
                }
            ]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced Airtable node with embedded configuration."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Initialize the Enhanced UniversalRequestNode with embedded config
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.info("Enhanced AirtableNode initialized with ALL 42 original operations and array templates")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"AirtableNode executing operation: {node_data.get('params', {}).get('operation')}")
        return await self.universal_request_node.execute(node_data)

    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.validate_custom(node_data)

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
        return self.universal_request_node.get_metrics()

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
__all__ = ["AirtableNode"]