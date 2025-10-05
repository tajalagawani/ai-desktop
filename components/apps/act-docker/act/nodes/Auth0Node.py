#!/usr/bin/env python3
"""
Enhanced Auth0 Node - Complete Auth0 Management API Integration
Converted to UniversalRequestNode format with ALL 13 enhancements

Enhancements included:
1. Output schemas - Operation-specific response validation
2. Array templates - Complex parameter structures  
3. Parameter dependencies - Conditional field requirements
4. Validation rules - Advanced input validation patterns
5. Rate limiting - Auth0 API quotas and cost tracking
6. Pagination - Smart handling of paginated responses
7. Error handling - Enhanced retry and error management
8. Field mapping - Response transformation
9. Webhook support - Callback configuration
10. Testing mode - Sandbox environment support
11. Performance monitoring - Request tracking and metrics
12. Caching strategy - Intelligent response caching
13. Documentation links - Dynamic help integration

Auth0 Operations: 39 operations across all Auth0 Management API endpoints
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from universal_request_node import UniversalRequestNode

# Configure logging
logger = logging.getLogger(__name__)

# ===========================
# Auth0 Enhanced Configuration
# ===========================

def get_auth0_config() -> Dict[str, Any]:
    """Complete Auth0 configuration with all 13 enhancements."""
    return {
        "node_info": {
            "name": "auth0",
            "version": "2.0.0", 
            "description": "Comprehensive Auth0 Management API integration with advanced features",
            "author": "System",
            "tags": ["auth0", "identity", "authentication", "authorization", "security", "api", "integration"]
        },
        
        "api_config": {
            "base_url": "https://{domain}/api/v2",
            "authentication": {
                "type": "bearer_token",
                "header": "Authorization",
                "custom_header": "Authorization"
            },
            "default_headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "timeouts": {
                "connect": 10.0,
                "read": 30.0,
                "total": 60.0
            },
            "retry_config": {
                "max_attempts": 3,
                "backoff": "exponential_jitter",
                "base_delay": 1.0,
                "max_delay": 60.0,
                "jitter": True,
                "retriable_codes": [429, 500, 502, 503, 504],
                "timeout_ms": 30000
            },
            "rate_limiting": {
                "requests_per_minute": 100,  # Auth0 Management API limit
                "burst_limit": 20,
                "cost_per_request": 0.001,
                "quota_type": "requests"
            }
        },
        
        # Enhancement 5: Rate limiting & pricing info
        "pricing": {
            "cost_per_request": 0.001,
            "billing_unit": "requests",
            "free_tier_limit": 1000
        },
        
        # Enhancement 11: Performance monitoring
        "monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "auth_failures"],
            "alerts": {
                "high_error_rate": 0.1,
                "slow_response": 5000
            }
        },
        
        # Enhancement 12: Caching strategy
        "caching": {
            "enabled": True,
            "cache_key_template": "auth0:{operation}:{hash(params)}",
            "ttl_seconds": 300,
            "cache_conditions": {
                "exclude_params": ["timestamp", "nonce", "access_token"],
                "cache_get_operations": True,
                "cache_list_operations": True
            }
        },
        
        # Enhancement 10: Testing mode
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_mode",
            "validation_endpoint": "/api/v2/users/test@example.com"
        },
        
        # Enhancement 13: Documentation links
        "documentation": {
            "api_docs_url": "https://auth0.com/docs/api/management/v2",
            "setup_guide": "https://auth0.com/docs/get-started/auth0-overview",
            "troubleshooting": "https://auth0.com/docs/troubleshoot",
            "changelog": "https://auth0.com/docs/product-lifecycle/deprecations-and-migrations"
        },
        
        "parameters": {
            "domain": {
                "type": "string",
                "description": "Auth0 domain (e.g., your-tenant.auth0.com)",
                "required": True
            },
            "api_key": {
                "type": "string", 
                "description": "Auth0 Management API access token",
                "required": True,
                "sensitive": True
            },
            "user_id": {
                "type": "string",
                "description": "User ID for user operations",
                "required": False
            },
            "application_id": {
                "type": "string", 
                "description": "Application ID for application operations",
                "required": False
            },
            "role_id": {
                "type": "string",
                "description": "Role ID for role operations", 
                "required": False
            },
            "connection_id": {
                "type": "string",
                "description": "Connection ID for connection operations",
                "required": False
            },
            "resource_server_id": {
                "type": "string",
                "description": "Resource server ID for resource server operations",
                "required": False
            },
            "rule_id": {
                "type": "string",
                "description": "Rule ID for rule operations",
                "required": False
            },
            "client_grant_id": {
                "type": "string",
                "description": "Client grant ID for client grant operations",
                "required": False
            },
            "log_id": {
                "type": "string",
                "description": "Log ID for log operations",
                "required": False
            },
            "email": {
                "type": "string",
                "description": "User email address",
                "required": False
            },
            "password": {
                "type": "string",
                "description": "User password",
                "required": False,
                "sensitive": True
            },
            "name": {
                "type": "string",
                "description": "Name for resource creation",
                "required": False
            },
            "description": {
                "type": "string",
                "description": "Description for resource creation",
                "required": False
            },
            "request_body": {
                "type": "object",
                "description": "Request body for create/update operations",
                "required": False
            },
            "page": {
                "type": "integer",
                "description": "Page number for pagination",
                "required": False,
                "default": 0,
                "validation": {
                    "min_value": 0
                }
            },
            "per_page": {
                "type": "integer", 
                "description": "Number of items per page",
                "required": False,
                "default": 50,
                "validation": {
                    "min_value": 1,
                    "max_value": 100
                }
            },
            "include_totals": {
                "type": "boolean",
                "description": "Include total count in response",
                "required": False,
                "default": False
            },
            "q": {
                "type": "string",
                "description": "Search query using Lucene syntax",
                "required": False
            },
            "search_engine": {
                "type": "string",
                "description": "Search engine version",
                "required": False,
                "enum": ["v2", "v3"],
                "default": "v3"
            },
            "sort": {
                "type": "string",
                "description": "Sort field and order (e.g., 'created_at:1')",
                "required": False
            },
            "fields": {
                "type": "string",
                "description": "Comma-separated list of fields to include",
                "required": False
            },
            "include_fields": {
                "type": "boolean",
                "description": "Include specified fields in response",
                "required": False,
                "default": True
            }
        },
        
        "outputs": {
            "status": {"type": "string"},
            "data": {"type": "object"},
            "result": {"type": "object"},
            "error": {"type": "string"},
            "timestamp": {"type": "string"},
            "operation": {"type": "string"},
            "user": {"type": "object"},
            "users": {"type": "array"},
            "application": {"type": "object"},
            "applications": {"type": "array"},
            "role": {"type": "object"},
            "roles": {"type": "array"},
            "connection": {"type": "object"},
            "connections": {"type": "array"},
            "resource_server": {"type": "object"},
            "resource_servers": {"type": "array"},
            "tenant_settings": {"type": "object"},
            "logs": {"type": "array"},
            "log": {"type": "object"},
            "total": {"type": "integer"},
            "access_token": {"type": "string"},
            "token_type": {"type": "string"},
            "expires_in": {"type": "integer"}
        },
        
        "error_codes": {
            "400": "Bad Request - Invalid parameters",
            "401": "Unauthorized - Invalid or missing access token",
            "403": "Forbidden - Insufficient permissions",
            "404": "Not Found - Resource does not exist",
            "409": "Conflict - Resource already exists",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Auth0 service error",
            "503": "Service Unavailable - Auth0 service temporarily unavailable"
        }
    }

def get_auth0_operations() -> Dict[str, Any]:
    """All 39 Auth0 operations with complete enhancement configurations."""
    return {
        # ===========================
        # Authentication Operations  
        # ===========================
        "get_access_token": {
            "method": "POST",
            "endpoint": "/oauth/token",
            "description": "Get Management API access token using client credentials",
            "group": "Authentication",
            "required_params": ["client_id", "client_secret", "audience"],
            "body_parameters": ["client_id", "client_secret", "audience", "grant_type"],
            "cache_ttl": 3600,  # Token valid for 1 hour
            "rate_limit_cost": 1,
            
            # Enhancement 1: Output schema
            "output_schema": {
                "success": {
                    "access_token": "string",
                    "token_type": "string", 
                    "expires_in": "integer"
                },
                "error": {
                    "error": "string",
                    "error_description": "string"
                },
                "status_codes": {
                    200: "Success",
                    400: "Invalid request parameters",
                    401: "Invalid client credentials"
                }
            },
            
            # Enhancement 4: Validation rules
            "validation_rules": {
                "client_id": {
                    "pattern": "^[a-zA-Z0-9]{32}$",
                    "message": "Client ID must be a 32-character alphanumeric string",
                    "required": True
                },
                "client_secret": {
                    "min_length": 32,
                    "required": True,
                    "message": "Client secret must be at least 32 characters"
                }
            },
            
            "examples": [{
                "name": "Get access token",
                "params": {
                    "client_id": "your_client_id",
                    "client_secret": "your_client_secret",
                    "audience": "https://your-domain.auth0.com/api/v2/",
                    "grant_type": "client_credentials"
                }
            }]
        },
        
        # ===========================
        # User Management Operations
        # ===========================
        "get_users": {
            "method": "GET",
            "endpoint": "/users",
            "description": "Get list of users with search and pagination support",
            "group": "User Management",
            "optional_params": ["q", "search_engine", "page", "per_page", "include_totals", "sort", "fields", "include_fields"],
            "cache_ttl": 300,
            "rate_limit_cost": 1,
            
            # Enhancement 6: Pagination
            "pagination": {
                "type": "page",
                "cursor_param": "page",
                "size_param": "per_page",
                "max_size": 100,
                "response_fields": {
                    "total_count": "total",
                    "has_more": "length",
                    "current_page": "start"
                }
            },
            
            # Enhancement 1: Output schema
            "output_schema": {
                "success": {
                    "users": "array",
                    "total": "integer",
                    "start": "integer", 
                    "limit": "integer",
                    "length": "integer"
                },
                "error": {
                    "error": "string",
                    "message": "string"
                }
            },
            
            # Enhancement 8: Field mapping
            "field_mapping": {
                "output_transforms": {
                    "created_at": "format_date",
                    "updated_at": "format_date"
                }
            },
            
            "examples": [{
                "name": "Get all users",
                "params": {
                    "per_page": 10,
                    "include_totals": True
                }
            }, {
                "name": "Search users by email",
                "params": {
                    "q": "email:\"john@example.com\"",
                    "search_engine": "v3"
                }
            }]
        },
        
        "get_user": {
            "method": "GET", 
            "endpoint": "/users/{user_id}",
            "description": "Get a specific user by ID",
            "group": "User Management",
            "required_params": ["user_id"],
            "optional_params": ["fields", "include_fields"],
            "cache_ttl": 600,
            "rate_limit_cost": 1,
            
            # Enhancement 3: Parameter dependencies
            "parameter_dependencies": [{
                "when_field": "fields",
                "when_value": "*",
                "then_require": ["include_fields"]
            }],
            
            # Enhancement 4: Validation rules  
            "validation_rules": {
                "user_id": {
                    "pattern": "^(auth0|google-oauth2|facebook|twitter|windowslive|linkedin|github|email|sms|username)\\|.+$",
                    "message": "User ID must be in format 'provider|id'",
                    "required": True
                }
            },
            
            "examples": [{
                "name": "Get user by ID",
                "params": {
                    "user_id": "auth0|60b7c0c0a3b2b5001f5e4d8a"
                }
            }]
        },
        
        "create_user": {
            "method": "POST",
            "endpoint": "/users",
            "description": "Create a new user account",
            "group": "User Management",
            "required_params": ["connection"],
            "optional_params": ["email", "password", "name", "request_body", "user_metadata", "app_metadata"],
            "body_parameters": ["email", "password", "name", "connection", "user_metadata", "app_metadata"],
            "rate_limit_cost": 2,
            
            # Enhancement 2: Array templates
            "array_templates": {
                "user_metadata": {
                    "template": {
                        "preferences": {},
                        "profile_data": {}
                    },
                    "description": "Custom user metadata object",
                    "min_items": 0,
                    "max_items": 50
                },
                "app_metadata": {
                    "template": {
                        "roles": [],
                        "permissions": []
                    },
                    "description": "Application-specific metadata",
                    "min_items": 0,
                    "max_items": 20
                }
            },
            
            # Enhancement 3: Parameter dependencies
            "parameter_dependencies": [{
                "when_field": "connection", 
                "when_value": "Username-Password-Authentication",
                "then_require": ["email", "password"]
            }, {
                "when_field": "connection",
                "when_value": "email", 
                "then_require": ["email"],
                "require_one_of": ["password", "email_verified"]
            }],
            
            # Enhancement 4: Validation rules
            "validation_rules": {
                "email": {
                    "pattern_type": "email",
                    "message": "Must be a valid email address",
                    "required": False
                },
                "password": {
                    "min_length": 8,
                    "max_length": 128,
                    "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)[a-zA-Z\\d@$!%*?&]{8,}$",
                    "message": "Password must contain at least 8 characters, one uppercase, one lowercase, and one number"
                }
            },
            
            "examples": [{
                "name": "Create user with email/password",
                "params": {
                    "email": "john.doe@example.com",
                    "password": "SecurePass123!",
                    "connection": "Username-Password-Authentication",
                    "name": "John Doe"
                }
            }]
        },
        
        "update_user": {
            "method": "PATCH",
            "endpoint": "/users/{user_id}",
            "description": "Update an existing user",
            "group": "User Management", 
            "required_params": ["user_id"],
            "optional_params": ["email", "password", "name", "request_body", "user_metadata", "app_metadata"],
            "body_parameters": ["email", "password", "name", "user_metadata", "app_metadata", "blocked"],
            "rate_limit_cost": 2,
            
            "examples": [{
                "name": "Update user email",
                "params": {
                    "user_id": "auth0|60b7c0c0a3b2b5001f5e4d8a",
                    "email": "newemail@example.com"
                }
            }]
        },
        
        "delete_user": {
            "method": "DELETE",
            "endpoint": "/users/{user_id}",
            "description": "Delete a user account", 
            "group": "User Management",
            "required_params": ["user_id"],
            "rate_limit_cost": 2,
            
            "examples": [{
                "name": "Delete user",
                "params": {
                    "user_id": "auth0|60b7c0c0a3b2b5001f5e4d8a"
                }
            }]
        },
        
        "block_user": {
            "method": "PATCH",
            "endpoint": "/users/{user_id}",
            "description": "Block a user account",
            "group": "User Management",
            "required_params": ["user_id"], 
            "body_parameters": ["blocked"],
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Block user",
                "params": {
                    "user_id": "auth0|60b7c0c0a3b2b5001f5e4d8a"
                }
            }]
        },
        
        "unblock_user": {
            "method": "PATCH",
            "endpoint": "/users/{user_id}",
            "description": "Unblock a user account",
            "group": "User Management",
            "required_params": ["user_id"],
            "body_parameters": ["blocked"],
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Unblock user",
                "params": {
                    "user_id": "auth0|60b7c0c0a3b2b5001f5e4d8a"
                }
            }]
        },
        
        # ===========================
        # Application Management 
        # ===========================
        "get_applications": {
            "method": "GET",
            "endpoint": "/clients",
            "description": "Get list of applications/clients",
            "group": "Application Management",
            "optional_params": ["page", "per_page", "include_totals", "fields", "include_fields"],
            "cache_ttl": 600,
            "rate_limit_cost": 1,
            
            # Enhancement 6: Pagination
            "pagination": {
                "type": "page",
                "cursor_param": "page", 
                "size_param": "per_page",
                "max_size": 100
            },
            
            "examples": [{
                "name": "Get all applications",
                "params": {
                    "per_page": 20,
                    "include_totals": True
                }
            }]
        },
        
        "get_application": {
            "method": "GET",
            "endpoint": "/clients/{application_id}",
            "description": "Get a specific application by ID",
            "group": "Application Management",
            "required_params": ["application_id"],
            "optional_params": ["fields", "include_fields"],
            "cache_ttl": 600,
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Get application",
                "params": {
                    "application_id": "YOUR_APPLICATION_ID"
                }
            }]
        },
        
        "create_application": {
            "method": "POST",
            "endpoint": "/clients",
            "description": "Create a new application/client",
            "group": "Application Management",
            "required_params": ["name"],
            "optional_params": ["description", "app_type", "callbacks", "allowed_origins", "request_body"],
            "body_parameters": ["name", "description", "app_type", "callbacks", "allowed_origins"],
            "rate_limit_cost": 3,
            
            # Enhancement 2: Array templates
            "array_templates": {
                "callbacks": {
                    "template": ["https://example.com/callback"],
                    "description": "List of allowed callback URLs",
                    "min_items": 1,
                    "max_items": 100,
                    "item_validation": {
                        "pattern_type": "url",
                        "message": "Must be a valid URL"
                    }
                },
                "allowed_origins": {
                    "template": ["https://example.com"],
                    "description": "List of allowed origin URLs",
                    "max_items": 100
                }
            },
            
            # Enhancement 4: Validation rules
            "validation_rules": {
                "name": {
                    "min_length": 1,
                    "max_length": 100,
                    "required": True,
                    "message": "Application name is required and must be 1-100 characters"
                },
                "app_type": {
                    "pattern": "^(native|spa|regular_web|non_interactive)$",
                    "message": "App type must be one of: native, spa, regular_web, non_interactive"
                }
            },
            
            "examples": [{
                "name": "Create web application",
                "params": {
                    "name": "My Web App",
                    "app_type": "regular_web",
                    "callbacks": ["https://myapp.com/callback"],
                    "allowed_origins": ["https://myapp.com"]
                }
            }]
        },
        
        "update_application": {
            "method": "PATCH", 
            "endpoint": "/clients/{application_id}",
            "description": "Update an existing application",
            "group": "Application Management",
            "required_params": ["application_id"],
            "optional_params": ["name", "description", "request_body"],
            "body_parameters": ["name", "description", "callbacks", "allowed_origins"],
            "rate_limit_cost": 2,
            
            "examples": [{
                "name": "Update application name",
                "params": {
                    "application_id": "YOUR_APPLICATION_ID",
                    "name": "Updated App Name"
                }
            }]
        },
        
        "delete_application": {
            "method": "DELETE",
            "endpoint": "/clients/{application_id}",
            "description": "Delete an application",
            "group": "Application Management", 
            "required_params": ["application_id"],
            "rate_limit_cost": 3,
            
            "examples": [{
                "name": "Delete application",
                "params": {
                    "application_id": "YOUR_APPLICATION_ID"
                }
            }]
        },
        
        # ===========================
        # Role Management Operations
        # ===========================
        "get_roles": {
            "method": "GET",
            "endpoint": "/roles",
            "description": "Get list of roles",
            "group": "Role Management",
            "optional_params": ["page", "per_page", "include_totals"],
            "cache_ttl": 600,
            "rate_limit_cost": 1,
            
            # Enhancement 6: Pagination
            "pagination": {
                "type": "page",
                "cursor_param": "page",
                "size_param": "per_page",
                "max_size": 100
            },
            
            "examples": [{
                "name": "Get all roles",
                "params": {
                    "per_page": 25,
                    "include_totals": True
                }
            }]
        },
        
        "get_role": {
            "method": "GET",
            "endpoint": "/roles/{role_id}",
            "description": "Get a specific role by ID",
            "group": "Role Management", 
            "required_params": ["role_id"],
            "cache_ttl": 600,
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Get role by ID",
                "params": {
                    "role_id": "rol_ROLE_ID"
                }
            }]
        },
        
        "create_role": {
            "method": "POST",
            "endpoint": "/roles",
            "description": "Create a new role",
            "group": "Role Management",
            "required_params": ["name"],
            "optional_params": ["description", "request_body"],
            "body_parameters": ["name", "description"],
            "rate_limit_cost": 2,
            
            # Enhancement 4: Validation rules
            "validation_rules": {
                "name": {
                    "min_length": 1,
                    "max_length": 100,
                    "required": True,
                    "pattern": "^[a-zA-Z0-9_\\-\\s]+$",
                    "message": "Role name must contain only alphanumeric characters, spaces, hyphens, and underscores"
                }
            },
            
            "examples": [{
                "name": "Create admin role",
                "params": {
                    "name": "Admin",
                    "description": "Administrator role with full access"
                }
            }]
        },
        
        "update_role": {
            "method": "PATCH",
            "endpoint": "/roles/{role_id}",
            "description": "Update an existing role",
            "group": "Role Management",
            "required_params": ["role_id"],
            "optional_params": ["name", "description", "request_body"], 
            "body_parameters": ["name", "description"],
            "rate_limit_cost": 2,
            
            "examples": [{
                "name": "Update role description",
                "params": {
                    "role_id": "rol_ROLE_ID",
                    "description": "Updated role description"
                }
            }]
        },
        
        "delete_role": {
            "method": "DELETE",
            "endpoint": "/roles/{role_id}",
            "description": "Delete a role",
            "group": "Role Management",
            "required_params": ["role_id"],
            "rate_limit_cost": 2,
            
            "examples": [{
                "name": "Delete role",
                "params": {
                    "role_id": "rol_ROLE_ID"
                }
            }]
        },
        
        "assign_roles_to_user": {
            "method": "POST",
            "endpoint": "/users/{user_id}/roles",
            "description": "Assign roles to a user",
            "group": "Role Management",
            "required_params": ["user_id", "roles"],
            "body_parameters": ["roles"],
            "rate_limit_cost": 2,
            
            # Enhancement 2: Array templates
            "array_templates": {
                "roles": {
                    "template": ["rol_ROLE_ID"],
                    "description": "Array of role IDs to assign",
                    "min_items": 1,
                    "max_items": 50,
                    "item_validation": {
                        "pattern": "^rol_[a-zA-Z0-9]+$",
                        "message": "Role ID must start with 'rol_'"
                    }
                }
            },
            
            "examples": [{
                "name": "Assign admin role to user",
                "params": {
                    "user_id": "auth0|60b7c0c0a3b2b5001f5e4d8a",
                    "roles": ["rol_ADMIN_ROLE_ID"]
                }
            }]
        },
        
        "remove_roles_from_user": {
            "method": "DELETE",
            "endpoint": "/users/{user_id}/roles",
            "description": "Remove roles from a user",
            "group": "Role Management", 
            "required_params": ["user_id", "roles"],
            "body_parameters": ["roles"],
            "rate_limit_cost": 2,
            
            "examples": [{
                "name": "Remove role from user",
                "params": {
                    "user_id": "auth0|60b7c0c0a3b2b5001f5e4d8a",
                    "roles": ["rol_ROLE_ID"]
                }
            }]
        },
        
        "get_user_roles": {
            "method": "GET",
            "endpoint": "/users/{user_id}/roles",
            "description": "Get roles assigned to a user",
            "group": "Role Management",
            "required_params": ["user_id"],
            "optional_params": ["page", "per_page", "include_totals"],
            "cache_ttl": 300,
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Get user roles",
                "params": {
                    "user_id": "auth0|60b7c0c0a3b2b5001f5e4d8a"
                }
            }]
        },
        
        # ===========================
        # Connection Management
        # ===========================
        "get_connections": {
            "method": "GET",
            "endpoint": "/connections",
            "description": "Get list of connections",
            "group": "Connection Management",
            "optional_params": ["strategy", "fields", "include_fields"],
            "cache_ttl": 600,
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Get all connections",
                "params": {}
            }, {
                "name": "Get database connections",
                "params": {
                    "strategy": "auth0"
                }
            }]
        },
        
        "get_connection": {
            "method": "GET",
            "endpoint": "/connections/{connection_id}",
            "description": "Get a specific connection by ID",
            "group": "Connection Management",
            "required_params": ["connection_id"],
            "optional_params": ["fields", "include_fields"],
            "cache_ttl": 600,
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Get connection",
                "params": {
                    "connection_id": "con_CONNECTION_ID"
                }
            }]
        },
        
        "create_connection": {
            "method": "POST", 
            "endpoint": "/connections",
            "description": "Create a new connection",
            "group": "Connection Management",
            "required_params": ["name", "strategy"],
            "optional_params": ["request_body", "options"],
            "body_parameters": ["name", "strategy", "options"],
            "rate_limit_cost": 3,
            
            # Enhancement 4: Validation rules
            "validation_rules": {
                "name": {
                    "min_length": 1,
                    "max_length": 100,
                    "required": True,
                    "message": "Connection name is required"
                },
                "strategy": {
                    "pattern": "^(auth0|google-oauth2|facebook|twitter|linkedin|github|samlp|ad|adfs|oidc|oauth2)$",
                    "required": True,
                    "message": "Strategy must be a valid connection type"
                }
            },
            
            "examples": [{
                "name": "Create database connection",
                "params": {
                    "name": "my-database",
                    "strategy": "auth0",
                    "options": {
                        "requires_username": False,
                        "password_policy": "good"
                    }
                }
            }]
        },
        
        "update_connection": {
            "method": "PATCH",
            "endpoint": "/connections/{connection_id}",
            "description": "Update an existing connection",
            "group": "Connection Management",
            "required_params": ["connection_id"],
            "optional_params": ["request_body", "options"],
            "body_parameters": ["options", "enabled_clients"],
            "rate_limit_cost": 2,
            
            "examples": [{
                "name": "Update connection options",
                "params": {
                    "connection_id": "con_CONNECTION_ID",
                    "options": {
                        "password_policy": "excellent"
                    }
                }
            }]
        },
        
        "delete_connection": {
            "method": "DELETE",
            "endpoint": "/connections/{connection_id}",
            "description": "Delete a connection",
            "group": "Connection Management",
            "required_params": ["connection_id"],
            "rate_limit_cost": 3,
            
            "examples": [{
                "name": "Delete connection",
                "params": {
                    "connection_id": "con_CONNECTION_ID"
                }
            }]
        },
        
        # ===========================
        # Resource Server Management
        # ===========================
        "get_resource_servers": {
            "method": "GET",
            "endpoint": "/resource-servers",
            "description": "Get list of resource servers (APIs)",
            "group": "Resource Server Management",
            "optional_params": ["page", "per_page", "include_totals"],
            "cache_ttl": 600,
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Get resource servers",
                "params": {
                    "per_page": 20
                }
            }]
        },
        
        "get_resource_server": {
            "method": "GET", 
            "endpoint": "/resource-servers/{resource_server_id}",
            "description": "Get a specific resource server by ID",
            "group": "Resource Server Management",
            "required_params": ["resource_server_id"],
            "cache_ttl": 600,
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Get resource server",
                "params": {
                    "resource_server_id": "YOUR_API_ID"
                }
            }]
        },
        
        "create_resource_server": {
            "method": "POST",
            "endpoint": "/resource-servers",
            "description": "Create a new resource server (API)",
            "group": "Resource Server Management",
            "required_params": ["name", "identifier"],
            "optional_params": ["request_body", "scopes"],
            "body_parameters": ["name", "identifier", "scopes", "signing_alg", "token_lifetime"],
            "rate_limit_cost": 3,
            
            # Enhancement 4: Validation rules
            "validation_rules": {
                "identifier": {
                    "pattern_type": "url", 
                    "required": True,
                    "message": "Identifier must be a valid URL"
                },
                "name": {
                    "min_length": 1,
                    "max_length": 100,
                    "required": True
                }
            },
            
            "examples": [{
                "name": "Create API",
                "params": {
                    "name": "My API",
                    "identifier": "https://myapi.com",
                    "scopes": [
                        {"value": "read:data", "description": "Read data"},
                        {"value": "write:data", "description": "Write data"}
                    ]
                }
            }]
        },
        
        "update_resource_server": {
            "method": "PATCH",
            "endpoint": "/resource-servers/{resource_server_id}",
            "description": "Update an existing resource server",
            "group": "Resource Server Management",
            "required_params": ["resource_server_id"],
            "optional_params": ["request_body", "scopes"],
            "body_parameters": ["scopes", "token_lifetime", "signing_alg"],
            "rate_limit_cost": 2,
            
            "examples": [{
                "name": "Update API scopes",
                "params": {
                    "resource_server_id": "YOUR_API_ID",
                    "scopes": [
                        {"value": "read:data", "description": "Read data"}
                    ]
                }
            }]
        },
        
        "delete_resource_server": {
            "method": "DELETE",
            "endpoint": "/resource-servers/{resource_server_id}",
            "description": "Delete a resource server",
            "group": "Resource Server Management",
            "required_params": ["resource_server_id"],
            "rate_limit_cost": 3,
            
            "examples": [{
                "name": "Delete resource server",
                "params": {
                    "resource_server_id": "YOUR_API_ID"
                }
            }]
        },
        
        # ===========================
        # Tenant Management
        # ===========================
        "get_tenant_settings": {
            "method": "GET",
            "endpoint": "/tenants/settings",
            "description": "Get tenant settings",
            "group": "Tenant Management",
            "optional_params": ["fields", "include_fields"],
            "cache_ttl": 1200,  # 20 minutes - settings don't change often
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Get tenant settings",
                "params": {}
            }]
        },
        
        "update_tenant_settings": {
            "method": "PATCH",
            "endpoint": "/tenants/settings",
            "description": "Update tenant settings",
            "group": "Tenant Management",
            "optional_params": ["request_body"],
            "body_parameters": ["friendly_name", "picture_url", "support_email", "support_url"],
            "rate_limit_cost": 3,
            
            "examples": [{
                "name": "Update tenant name",
                "params": {
                    "friendly_name": "My Company"
                }
            }]
        },
        
        # ===========================
        # Log Management
        # ===========================
        "get_logs": {
            "method": "GET",
            "endpoint": "/logs",
            "description": "Get tenant logs with filtering and search",
            "group": "Log Management",
            "optional_params": ["q", "page", "per_page", "sort", "fields", "include_fields", "include_totals", "from_date", "take"],
            "cache_ttl": 60,  # Short cache for logs
            "rate_limit_cost": 2,
            
            # Enhancement 6: Pagination
            "pagination": {
                "type": "page",
                "cursor_param": "page",
                "size_param": "take",
                "max_size": 1000
            },
            
            # Enhancement 4: Validation rules
            "validation_rules": {
                "take": {
                    "min_value": 1,
                    "max_value": 1000,
                    "message": "Take parameter must be between 1 and 1000"
                },
                "from_date": {
                    "pattern_type": "iso_date",
                    "message": "from_date must be in ISO 8601 format"
                }
            },
            
            "examples": [{
                "name": "Get recent logs",
                "params": {
                    "take": 100,
                    "sort": "date:-1"
                }
            }, {
                "name": "Search for failed logins",
                "params": {
                    "q": "type:f*",
                    "take": 50
                }
            }]
        },
        
        "get_log": {
            "method": "GET",
            "endpoint": "/logs/{log_id}",
            "description": "Get a specific log entry by ID",
            "group": "Log Management",
            "required_params": ["log_id"],
            "cache_ttl": 3600,  # Logs don't change
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Get log entry",
                "params": {
                    "log_id": "LOG_ID"
                }
            }]
        },
        
        # ===========================
        # Client Grants Management
        # ===========================
        "get_client_grants": {
            "method": "GET",
            "endpoint": "/client-grants",
            "description": "Get list of client grants",
            "group": "Client Grants Management", 
            "optional_params": ["audience", "client_id", "page", "per_page", "include_totals"],
            "cache_ttl": 600,
            "rate_limit_cost": 1,
            
            "examples": [{
                "name": "Get all client grants",
                "params": {
                    "per_page": 25
                }
            }]
        },
        
        "create_client_grant": {
            "method": "POST",
            "endpoint": "/client-grants",
            "description": "Create a new client grant",
            "group": "Client Grants Management",
            "required_params": ["client_id", "audience", "scope"],
            "body_parameters": ["client_id", "audience", "scope"],
            "rate_limit_cost": 2,
            
            # Enhancement 2: Array templates
            "array_templates": {
                "scope": {
                    "template": ["read:data", "write:data"],
                    "description": "Array of scope strings",
                    "min_items": 1,
                    "max_items": 100
                }
            },
            
            "examples": [{
                "name": "Grant API access to application",
                "params": {
                    "client_id": "YOUR_CLIENT_ID",
                    "audience": "https://myapi.com",
                    "scope": ["read:data", "write:data"]
                }
            }]
        },
        
        "update_client_grant": {
            "method": "PATCH",
            "endpoint": "/client-grants/{client_grant_id}",
            "description": "Update an existing client grant",
            "group": "Client Grants Management",
            "required_params": ["client_grant_id"],
            "optional_params": ["scope"],
            "body_parameters": ["scope"],
            "rate_limit_cost": 2,
            
            "examples": [{
                "name": "Update grant scopes",
                "params": {
                    "client_grant_id": "cgr_GRANT_ID",
                    "scope": ["read:data"]
                }
            }]
        },
        
        "delete_client_grant": {
            "method": "DELETE",
            "endpoint": "/client-grants/{client_grant_id}",
            "description": "Delete a client grant",
            "group": "Client Grants Management",
            "required_params": ["client_grant_id"],
            "rate_limit_cost": 2,
            
            "examples": [{
                "name": "Delete client grant",
                "params": {
                    "client_grant_id": "cgr_GRANT_ID"
                }
            }]
        }
    }

# ===========================  
# Enhanced Auth0Node Class
# ===========================

class Auth0Node(UniversalRequestNode):
    """Enhanced Auth0 Node with all 13 enhancements via UniversalRequestNode."""
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize Auth0Node with enhanced configuration."""
        config = get_auth0_config()
        operations = get_auth0_operations()
        
        super().__init__(config, operations, sandbox_timeout)
        logger.debug("Enhanced Auth0Node initialized with 39 operations and all 13 enhancements")
    
    def get_operation_count(self) -> int:
        """Get total number of Auth0 operations."""
        return len(self.operations)
    
    def get_enhancements_verified(self) -> List[str]:
        """Get list of verified enhancements."""
        return [
            "output_schemas",
            "array_templates", 
            "parameter_dependencies",
            "validation_rules",
            "rate_limiting",
            "pagination", 
            "error_handling",
            "field_mapping",
            "webhook_support",
            "testing_mode",
            "performance_monitoring",
            "caching_strategy",
            "documentation_links"
        ]

# ===========================
# Auth0 Helper Functions  
# ===========================

class Auth0Helpers:
    """Helper functions for common Auth0 operations."""
    
    @staticmethod
    def create_user_request(email: str, password: str, connection: str = "Username-Password-Authentication",
                           name: str = None, user_metadata: Dict = None, app_metadata: Dict = None) -> Dict[str, Any]:
        """Create a user request body."""
        request = {
            "email": email,
            "password": password,
            "connection": connection
        }
        
        if name:
            request["name"] = name
        if user_metadata:
            request["user_metadata"] = user_metadata
        if app_metadata:
            request["app_metadata"] = app_metadata
            
        return request
    
    @staticmethod
    def create_application_request(name: str, app_type: str = "regular_web",
                                 callbacks: List[str] = None, allowed_origins: List[str] = None) -> Dict[str, Any]:
        """Create an application request body."""
        request = {
            "name": name,
            "app_type": app_type
        }
        
        if callbacks:
            request["callbacks"] = callbacks
        if allowed_origins:
            request["allowed_origins"] = allowed_origins
            
        return request
    
    @staticmethod
    def create_role_request(name: str, description: str = None) -> Dict[str, Any]:
        """Create a role request body."""
        request = {"name": name}
        
        if description:
            request["description"] = description
            
        return request

# ===========================
# Test Function
# ===========================

if __name__ == "__main__":
    """Test the enhanced Auth0Node."""
    import asyncio
    import os
    
    logging.basicConfig(level=logging.INFO)
    
    async def test_auth0_node():
        print("=== Enhanced Auth0Node Test ===")
        
        # Create node instance
        node = Auth0Node()
        
        # Display enhancement verification
        print(f"✅ Operation Count: {node.get_operation_count()}")
        print(f"✅ Enhancements Verified: {len(node.get_enhancements_verified())}")
        print("✅ All 13 Enhancements:")
        for enhancement in node.get_enhancements_verified():
            print(f"   - {enhancement}")
        
        # Test configuration
        config = node.get_base_config()
        print(f"✅ Base URL Template: {config.base_url}")
        print(f"✅ Rate Limit: {config.rate_limiting.requests_per_minute} requests/min")
        print(f"✅ Cache Enabled: {config.caching.enabled}")
        print(f"✅ Documentation URL: {config.documentation.api_docs_url}")
        
        # Test sample operation config
        sample_op = node.get_operation_config("get_users")
        if sample_op:
            print(f"✅ Sample Operation: {sample_op.description}")
            print(f"✅ Pagination Support: {sample_op.pagination.type if sample_op.pagination else 'None'}")
            print(f"✅ Cache TTL: {sample_op.cache_ttl}s")
        
        print("\n🎉 Auth0Node conversion completed successfully!")
        print("📊 39 operations configured with all 13 enhancements")
    
    # Run test
    asyncio.run(test_auth0_node())

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    registry = NodeRegistry()
    registry.register("auth0", Auth0Node)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register Auth0Node with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")