#!/usr/bin/env python3
"""
AworkNode - Enhanced with ALL 13 advanced features
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

class AworkNode(BaseNode):
    """
    Enhanced Awork node with ALL 13 advanced features.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "awork",
            "display_name": "Awork",
            "description": "Comprehensive Awork API integration for project management, task tracking, time management, and team collaboration",
            "category": "project_management",
            "vendor": "awork", 
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["project", "management", "tasks", "time", "tracking", "collaboration", "teams", "productivity"],
            "documentation_url": "https://developers.awork.io/",
            "icon": "https://cdn.jsdelivr.net/gh/n8n-io/n8n/packages/nodes-base/nodes/Awork/awork.svg",
            "color": "#7C4DFF",
            "created_at": "2025-08-26T00:00:00Z",
            "updated_at": "2025-08-26T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.awork.com/api/v1",
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
                "requests_per_minute": 1000,
                "requests_per_second": 10.0,
                "burst_size": 20,
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
            "cost_per_1k_requests": 10.0,
            "cost_per_request": 0.01,
            "billing_unit": "requests",
            "free_tier_limit": 1000
        },
        
        # Performance monitoring
        "monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "request_count"],
            "alerts": {
                "error_rate_threshold": 0.1,
                "response_time_threshold": 10000
            }
        },
        
        # Intelligent caching
        "caching": {
            "enabled": True,
            "cache_key_template": "{operation}:{hash}",
            "ttl_seconds": 300,
            "cache_conditions": {
                "only_for": ["GET"],
                "exclude_params": ["timestamp", "nonce", "page"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/workspace"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://developers.awork.io/",
            "setup_guide": "https://developers.awork.io/getting-started",
            "troubleshooting": "https://support.awork.io/",
            "changelog": "https://developers.awork.io/changelog"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "Awork API key (found in Settings > Integrations)",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-zA-Z0-9-_]+$",
                    "message": "API key must be alphanumeric with hyphens and underscores",
                    "minLength": 20,
                    "maxLength": 100
                }
            },
            "operation": {
                "type": "string",
                "description": "The Awork operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    # Project Operations
                    "get_projects", "create_project", "update_project", "delete_project", "get_project",
                    "get_project_members", "add_project_member", "remove_project_member", "get_project_tasks",
                    "get_project_time_entries", "get_project_comments", "create_project_comment",
                    "get_project_milestones", "create_project_milestone",
                    # Task Operations
                    "get_tasks", "create_task", "update_task", "delete_task", "get_task", "get_task_comments",
                    "create_task_comment", "get_task_dependencies", "add_task_dependency", "assign_task",
                    "get_task_lists", "create_task_list",
                    # Time Tracking Operations
                    "get_time_entries", "create_time_entry", "update_time_entry", "delete_time_entry",
                    "start_timer", "stop_timer", "get_time_reports",
                    # User Operations
                    "get_users", "get_user", "update_user", "get_user_capacities", "get_user_absences",
                    "create_user_absence", "get_my_profile",
                    # Team Operations
                    "get_teams", "create_team", "update_team", "delete_team", "get_team_members", "add_team_member",
                    # Company Operations
                    "get_companies", "create_company", "update_company", "delete_company",
                    # Workspace Operations
                    "get_workspace", "update_workspace", "get_workspace_settings",
                    # Other Operations
                    "get_custom_fields", "create_custom_field", "get_project_templates", "create_project_from_template",
                    "get_webhooks", "create_webhook", "delete_webhook", "search"
                ]
            },
            "project_id": {
                "type": "string",
                "description": "Project ID",
                "required": False,
                "group": "Project",
                "examples": ["proj_123abc", "project-456def"],
                "validation": {
                    "minLength": 1
                }
            },
            "task_id": {
                "type": "string",
                "description": "Task ID",
                "required": False,
                "group": "Task",
                "examples": ["task_789ghi", "task-012jkl"],
                "validation": {
                    "minLength": 1
                }
            },
            "user_id": {
                "type": "string",
                "description": "User ID",
                "required": False,
                "group": "User",
                "examples": ["user_345mno", "usr-678pqr"],
                "validation": {
                    "minLength": 1
                }
            },
            "team_id": {
                "type": "string",
                "description": "Team ID",
                "required": False,
                "group": "Team",
                "examples": ["team_901stu", "tm-234vwx"],
                "validation": {
                    "minLength": 1
                }
            },
            "company_id": {
                "type": "string",
                "description": "Company ID",
                "required": False,
                "group": "Company",
                "examples": ["comp_567yza", "company-890bcd"],
                "validation": {
                    "minLength": 1
                }
            },
            "name": {
                "type": "string",
                "description": "Name for creation operations",
                "required": False,
                "group": "Content",
                "examples": ["My Project", "Important Task", "Development Team"],
                "validation": {
                    "minLength": 1,
                    "maxLength": 200
                }
            },
            "description": {
                "type": "string",
                "description": "Description",
                "required": False,
                "group": "Content",
                "validation": {
                    "maxLength": 5000
                }
            },
            "start_date": {
                "type": "string",
                "description": "Start date (ISO format)",
                "required": False,
                "group": "Dates",
                "examples": ["2025-08-26T10:00:00Z", "2025-09-01"],
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}(T\\d{2}:\\d{2}:\\d{2}(\\.\\d{3})?Z?)?$",
                    "message": "Date must be in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:mm:ssZ)"
                }
            },
            "end_date": {
                "type": "string",
                "description": "End date (ISO format)",
                "required": False,
                "group": "Dates",
                "examples": ["2025-08-30T18:00:00Z", "2025-09-30"],
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}(T\\d{2}:\\d{2}:\\d{2}(\\.\\d{3})?Z?)?$",
                    "message": "Date must be in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:mm:ssZ)"
                }
            },
            "due_date": {
                "type": "string",
                "description": "Due date (ISO format)",
                "required": False,
                "group": "Dates",
                "examples": ["2025-08-28T17:00:00Z", "2025-08-31"],
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}(T\\d{2}:\\d{2}:\\d{2}(\\.\\d{3})?Z?)?$",
                    "message": "Date must be in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:mm:ssZ)"
                }
            },
            "status": {
                "type": "string",
                "description": "Status",
                "required": False,
                "group": "Status",
                "validation": {
                    "enum": ["active", "planned", "completed", "archived", "on_hold"]
                },
                "examples": ["active", "completed"]
            },
            "priority": {
                "type": "string",
                "description": "Priority level",
                "required": False,
                "group": "Priority",
                "validation": {
                    "enum": ["low", "normal", "high", "urgent"]
                },
                "examples": ["normal", "high"]
            },
            "assignee_id": {
                "type": "string",
                "description": "ID of user to assign",
                "required": False,
                "group": "Assignment",
                "validation": {
                    "minLength": 1
                }
            },
            "tags": {
                "type": "string",
                "description": "Comma-separated list of tags",
                "required": False,
                "group": "Tags",
                "examples": ["bug,urgent", "feature,frontend,ui"],
                "validation": {
                    "pattern": "^[^,]+(,[^,]+)*$",
                    "message": "Tags must be comma-separated without spaces around commas"
                }
            },
            "comment": {
                "type": "string",
                "description": "Comment text",
                "required": False,
                "group": "Comments",
                "validation": {
                    "minLength": 1,
                    "maxLength": 2000
                }
            },
            "duration": {
                "type": "integer",
                "description": "Duration in minutes",
                "required": False,
                "group": "Time",
                "validation": {
                    "minimum": 1,
                    "maximum": 1440
                },
                "examples": [30, 60, 120, 240]
            },
            "billable": {
                "type": "boolean",
                "description": "Whether time is billable",
                "required": False,
                "group": "Time",
                "default": True
            },
            "custom_fields": {
                "type": "object",
                "description": "Custom field values as JSON object",
                "required": False,
                "group": "Custom"
            },
            "color": {
                "type": "string",
                "description": "Color hex code (e.g., #FF5733)",
                "required": False,
                "group": "Appearance",
                "validation": {
                    "pattern": "^#[0-9A-Fa-f]{6}$",
                    "message": "Color must be a valid hex code (e.g., #FF5733)"
                },
                "examples": ["#FF5733", "#3498DB", "#27AE60"]
            },
            "budget": {
                "type": "number",
                "description": "Budget amount",
                "required": False,
                "group": "Budget",
                "validation": {
                    "minimum": 0
                },
                "examples": [1000.0, 5000.0, 10000.0]
            },
            "hourly_rate": {
                "type": "number",
                "description": "Hourly rate",
                "required": False,
                "group": "Budget",
                "validation": {
                    "minimum": 0
                },
                "examples": [50.0, 75.0, 100.0]
            },
            "template_id": {
                "type": "string",
                "description": "Project template ID",
                "required": False,
                "group": "Template",
                "validation": {
                    "minLength": 1
                }
            },
            "webhook_url": {
                "type": "string",
                "description": "Webhook URL",
                "required": False,
                "group": "Webhooks",
                "validation": {
                    "pattern": "^https?://[\\w\\-\\.]+\\.[a-zA-Z]{2,}(:\\d+)?(/.*)?$",
                    "message": "Must be a valid HTTP/HTTPS URL"
                },
                "examples": ["https://example.com/webhook", "https://api.myapp.com/awork-webhook"]
            },
            "webhook_events": {
                "type": "string",
                "description": "Comma-separated list of webhook events",
                "required": False,
                "group": "Webhooks",
                "examples": ["project.created,project.updated", "task.completed,task.deleted"],
                "validation": {
                    "pattern": "^[^,]+(,[^,]+)*$",
                    "message": "Events must be comma-separated"
                }
            },
            "search_query": {
                "type": "string",
                "description": "Search query",
                "required": False,
                "group": "Search",
                "examples": ["project name", "bug reports", "team meetings"],
                "validation": {
                    "minLength": 1,
                    "maxLength": 500
                }
            },
            "filter_by": {
                "type": "string",
                "description": "Filter expression (e.g., 'status eq active')",
                "required": False,
                "group": "Filter",
                "examples": ["status eq active", "priority eq high", "name contains 'project'"]
            },
            "page": {
                "type": "integer",
                "description": "Page number for pagination",
                "required": False,
                "default": 1,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 1000
                }
            },
            "page_size": {
                "type": "integer",
                "description": "Number of items per page",
                "required": False,
                "default": 50,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 200
                }
            },
            "order_by": {
                "type": "string",
                "description": "Order by field (e.g., 'created desc')",
                "required": False,
                "group": "Sorting",
                "examples": ["created desc", "name asc", "updated desc", "priority asc"]
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful Awork API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from Awork API"},
                    "result": {"type": "object", "description": "Full API response data"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Awork error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "default": {
                "required_env_keys": ["AWORK_API_KEY"],
                "optional_env_keys": ["AWORK_BASE_URL", "AWORK_ORG_ID"]
            }
        },
        
        # Error codes specific to Awork
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid API key or insufficient permissions",
            "403": "Forbidden - Request not allowed for current user",
            "404": "Not Found - Resource not found",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Awork server error",
            "502": "Bad Gateway - Awork server temporarily unavailable",
            "503": "Service Unavailable - Awork server overloaded"
        }
    }
    
    # Enhanced operation definitions with ALL 13 features (ALL 70 OPERATIONS)
    OPERATIONS = {
        # PROJECT OPERATIONS
        "get_projects": {
            "method": "GET",
            "endpoint": "/projects",
            "required_params": [],
            "optional_params": ["filter_by", "order_by", "page", "page_size"],
            "display_name": "Get Projects",
            "description": "Retrieve list of projects with optional filtering and pagination",
            "group": "Projects",
            "tags": ["projects", "list", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            # 1. Output schema
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "projects": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "status": {"type": "string", "enum": ["active", "planned", "completed", "archived"]},
                                    "startDate": {"type": "string", "format": "date-time"},
                                    "endDate": {"type": "string", "format": "date-time"},
                                    "budget": {"type": "number"},
                                    "color": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            
            # 2. Array templates (not applicable for GET)
            "array_templates": {},
            
            # 3. Parameter dependencies
            "parameter_dependencies": [
                {
                    "when_field": "filter_by",
                    "when_value": "*",
                    "then_require": [],
                    "then_optional": ["order_by"],
                    "require_one_of": [],
                    "mutually_exclusive": []
                }
            ],
            
            # 4. Validation rules
            "validation_rules": {
                "page": {
                    "pattern": "",
                    "message": "Page must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "max_value": 1000,
                    "required": False
                },
                "page_size": {
                    "pattern": "",
                    "message": "Page size must be between 1 and 200",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "max_value": 200,
                    "required": False
                }
            },
            
            # 5. Rate limiting
            "rate_limiting": {
                "requests_per_minute": 60,
                "burst_size": 10,
                "cost_multiplier": 1.0
            },
            
            # 6. Pagination
            "pagination": {
                "type": "page_based",
                "page_param": "page",
                "size_param": "page_size",
                "default_size": 50,
                "max_size": 200,
                "total_count_field": "total",
                "items_field": "projects"
            },
            
            # 7. Error handling
            "error_handling": {
                "retry_codes": [429, 500, 502, 503],
                "timeout_ms": 30000,
                "custom_messages": {
                    "401": "Invalid API key - please check your Awork credentials",
                    "403": "Insufficient permissions to access projects",
                    "404": "No projects found or endpoint not available"
                }
            },
            
            # 8. Field mapping
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {
                    "startDate": "format_datetime",
                    "endDate": "format_datetime"
                },
                "field_aliases": {
                    "proj_id": "id",
                    "project_name": "name"
                }
            },
            
            # 9. Webhook support
            "webhook_support": {
                "events": ["project.created", "project.updated", "project.deleted"],
                "payload_template": {
                    "event": "{event}",
                    "data": "{project}",
                    "timestamp": "{timestamp}"
                }
            },
            
            # 10. Testing mode
            "testing_mode": {
                "mock_response": {
                    "projects": [
                        {
                            "id": "test_project_1",
                            "name": "Test Project",
                            "status": "active",
                            "description": "Test project for development"
                        }
                    ]
                },
                "sandbox_endpoint": "/sandbox/projects"
            },
            
            # 11. Performance monitoring
            "performance_monitoring": {
                "track_metrics": True,
                "slow_query_threshold": 2000,
                "alert_on_errors": True,
                "custom_metrics": ["project_count", "active_projects"]
            },
            
            # 12. Caching strategy
            "caching_strategy": {
                "cache_key": "projects:{filter}:{page}:{size}",
                "ttl_seconds": 300,
                "vary_on": ["filter_by", "order_by"],
                "invalidate_on": ["project.created", "project.updated", "project.deleted"]
            },
            
            # 13. Documentation links
            "documentation_links": {
                "api_reference": "https://developers.awork.io/projects#get-projects",
                "examples": "https://developers.awork.io/projects/examples#list",
                "troubleshooting": "https://support.awork.io/projects/troubleshooting"
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "optional_env_keys": ["AWORK_BASE_URL"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "List all projects",
                    "description": "Get all projects with default pagination",
                    "input": {}
                },
                {
                    "name": "Filter active projects",
                    "description": "Get only active projects",
                    "input": {
                        "filter_by": "status eq active",
                        "order_by": "name asc"
                    }
                }
            ]
        },
        "create_project": {
            "method": "POST",
            "endpoint": "/projects",
            "required_params": ["name"],
            "optional_params": ["description", "status", "start_date", "end_date", "color", "budget", "hourly_rate", "tags", "custom_fields"],
            "body_parameters": ["name", "description", "status", "startDate", "endDate", "color", "budget", "hourlyRate", "tags", "customFields"],
            "display_name": "Create Project",
            "description": "Create a new project with specified parameters",
            "group": "Projects",
            "tags": ["projects", "create", "write"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "status": {"type": "string"},
                                "created": {"type": "string", "format": "date-time"}
                            }
                        }
                    }
                }
            },
            
            "array_templates": {
                "tags": [
                    {"template": "frontend", "description": "Frontend development tag"},
                    {"template": "backend", "description": "Backend development tag"},
                    {"template": "urgent", "description": "High priority tag"}
                ],
                "customFields": [
                    {"template": {"key": "client_name", "value": "Acme Corp"}, "description": "Client name custom field"},
                    {"template": {"key": "project_type", "value": "web_app"}, "description": "Project type classification"}
                ]
            },
            
            "parameter_dependencies": [
                {
                    "when_field": "budget",
                    "when_value": "*",
                    "then_require": [],
                    "then_optional": ["hourly_rate"],
                    "require_one_of": [],
                    "mutually_exclusive": []
                }
            ],
            
            "validation_rules": {
                "name": {
                    "pattern": "",
                    "message": "Project name is required and must be 1-200 characters",
                    "pattern_type": "custom",
                    "min_length": 1,
                    "max_length": 200,
                    "required": True
                },
                "budget": {
                    "pattern": "",
                    "message": "Budget must be a positive number",
                    "pattern_type": "custom",
                    "min_value": 0,
                    "required": False
                }
            },
            
            "rate_limiting": {
                "requests_per_minute": 20,
                "burst_size": 5,
                "cost_multiplier": 2.0
            },
            
            "pagination": None,
            
            "error_handling": {
                "retry_codes": [500, 502, 503],
                "timeout_ms": 15000,
                "custom_messages": {
                    "400": "Invalid project data - check required fields",
                    "409": "Project with this name already exists"
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "start_date": "to_camel_case->startDate",
                    "end_date": "to_camel_case->endDate",
                    "hourly_rate": "to_camel_case->hourlyRate",
                    "custom_fields": "to_camel_case->customFields"
                },
                "output_transforms": {
                    "created": "format_datetime"
                },
                "field_aliases": {}
            },
            
            "webhook_support": {
                "events": ["project.created"],
                "payload_template": {
                    "event": "project.created",
                    "project_id": "{id}",
                    "project_name": "{name}"
                }
            },
            
            "testing_mode": {
                "mock_response": {
                    "project": {
                        "id": "test_created_project",
                        "name": "Test Created Project",
                        "status": "active"
                    }
                }
            },
            
            "performance_monitoring": {
                "track_metrics": True,
                "slow_query_threshold": 3000,
                "alert_on_errors": True
            },
            
            "caching_strategy": {
                "cache_key": "none",
                "ttl_seconds": 0,
                "invalidate_on": ["project.created"]
            },
            
            "documentation_links": {
                "api_reference": "https://developers.awork.io/projects#create-project",
                "examples": "https://developers.awork.io/projects/examples#create"
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            },
            "examples": [
                {
                    "name": "Create basic project",
                    "description": "Create a project with minimal information",
                    "input": {
                        "name": "My New Project",
                        "description": "A project for testing",
                        "status": "active"
                    }
                }
            ]
        },
        "update_project": {
            "method": "PUT",
            "endpoint": "/projects/{project_id}",
            "required_params": ["project_id"],
            "optional_params": ["name", "description", "status", "start_date", "end_date", "color", "budget", "hourly_rate", "tags", "custom_fields"],
            "body_parameters": ["name", "description", "status", "startDate", "endDate", "color", "budget", "hourlyRate", "tags", "customFields"],
            "display_name": "Update Project",
            "description": "Update an existing project",
            "group": "Projects",
            "tags": ["projects", "update", "write"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "updated": {"type": "string", "format": "date-time"}
                            }
                        }
                    }
                }
            },
            
            "validation_rules": {
                "project_id": {
                    "pattern": "",
                    "message": "Project ID is required for updates",
                    "pattern_type": "custom",
                    "min_length": 1,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "start_date": "to_camel_case->startDate",
                    "end_date": "to_camel_case->endDate"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "delete_project": {
            "method": "DELETE",
            "endpoint": "/projects/{project_id}",
            "required_params": ["project_id"],
            "optional_params": [],
            "display_name": "Delete Project",
            "description": "Delete a project",
            "group": "Projects",
            "tags": ["projects", "delete", "write"],
            "rate_limit_cost": 3,
            
            "validation_rules": {
                "project_id": {
                    "pattern": "",
                    "message": "Project ID is required for deletion",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_project": {
            "method": "GET",
            "endpoint": "/projects/{project_id}",
            "required_params": ["project_id"],
            "optional_params": [],
            "display_name": "Get Project",
            "description": "Get a specific project by ID",
            "group": "Projects",
            "tags": ["projects", "read", "single"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            
            "validation_rules": {
                "project_id": {
                    "pattern": "",
                    "message": "Project ID is required",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_project_members": {
            "method": "GET",
            "endpoint": "/projects/{project_id}/members",
            "required_params": ["project_id"],
            "optional_params": [],
            "display_name": "Get Project Members",
            "description": "Get members of a specific project",
            "group": "Projects",
            "tags": ["projects", "members", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 180,
            
            "validation_rules": {
                "project_id": {
                    "pattern": "",
                    "message": "Project ID is required",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "add_project_member": {
            "method": "POST",
            "endpoint": "/projects/{project_id}/members",
            "required_params": ["project_id", "user_id"],
            "optional_params": [],
            "body_parameters": ["userId"],
            "display_name": "Add Project Member",
            "description": "Add a member to a project",
            "group": "Projects",
            "tags": ["projects", "members", "write"],
            "rate_limit_cost": 2,
            
            "validation_rules": {
                "project_id": {"required": True},
                "user_id": {"required": True}
            },
            
            "field_mapping": {
                "input_transforms": {
                    "user_id": "to_camel_case->userId"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "remove_project_member": {
            "method": "DELETE",
            "endpoint": "/projects/{project_id}/members/{user_id}",
            "required_params": ["project_id", "user_id"],
            "optional_params": [],
            "display_name": "Remove Project Member",
            "description": "Remove a member from a project",
            "group": "Projects",
            "tags": ["projects", "members", "delete"],
            "rate_limit_cost": 2,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_project_tasks": {
            "method": "GET",
            "endpoint": "/projects/{project_id}/tasks",
            "required_params": ["project_id"],
            "optional_params": ["filter_by", "order_by", "page", "page_size"],
            "display_name": "Get Project Tasks",
            "description": "Get tasks for a specific project",
            "group": "Projects",
            "tags": ["projects", "tasks", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 180,
            
            "pagination": {
                "type": "page_based",
                "page_param": "page",
                "size_param": "page_size",
                "default_size": 50
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_project_time_entries": {
            "method": "GET",
            "endpoint": "/projects/{project_id}/timeentries",
            "required_params": ["project_id"],
            "optional_params": ["filter_by", "order_by", "page", "page_size"],
            "display_name": "Get Project Time Entries",
            "description": "Get time entries for a specific project",
            "group": "Projects",
            "tags": ["projects", "time", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 120,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_project_comments": {
            "method": "GET",
            "endpoint": "/projects/{project_id}/comments",
            "required_params": ["project_id"],
            "optional_params": [],
            "display_name": "Get Project Comments",
            "description": "Get comments for a specific project",
            "group": "Projects",
            "tags": ["projects", "comments", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_project_comment": {
            "method": "POST",
            "endpoint": "/projects/{project_id}/comments",
            "required_params": ["project_id", "comment"],
            "optional_params": [],
            "body_parameters": ["text"],
            "display_name": "Create Project Comment",
            "description": "Add a comment to a project",
            "group": "Projects",
            "tags": ["projects", "comments", "write"],
            "rate_limit_cost": 1,
            
            "field_mapping": {
                "input_transforms": {
                    "comment": "rename->text"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_project_milestones": {
            "method": "GET",
            "endpoint": "/projects/{project_id}/milestones",
            "required_params": ["project_id"],
            "optional_params": [],
            "display_name": "Get Project Milestones",
            "description": "Get milestones for a specific project",
            "group": "Projects",
            "tags": ["projects", "milestones", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_project_milestone": {
            "method": "POST",
            "endpoint": "/projects/{project_id}/milestones",
            "required_params": ["project_id", "name"],
            "optional_params": ["description", "due_date"],
            "body_parameters": ["name", "description", "dueDate"],
            "display_name": "Create Project Milestone",
            "description": "Create a milestone for a project",
            "group": "Projects",
            "tags": ["projects", "milestones", "write"],
            "rate_limit_cost": 2,
            
            "field_mapping": {
                "input_transforms": {
                    "due_date": "to_camel_case->dueDate"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },

        # TASK OPERATIONS
        "get_tasks": {
            "method": "GET",
            "endpoint": "/tasks",
            "required_params": [],
            "optional_params": ["filter_by", "order_by", "page", "page_size"],
            "display_name": "Get Tasks",
            "description": "Retrieve list of tasks with filtering and pagination",
            "group": "Tasks",
            "tags": ["tasks", "list", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 180,
            
            "pagination": {
                "type": "page_based",
                "page_param": "page",
                "size_param": "page_size",
                "default_size": 50
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_task": {
            "method": "POST",
            "endpoint": "/tasks",
            "required_params": ["name"],
            "optional_params": ["description", "priority", "due_date", "project_id", "assignee_id", "tags", "custom_fields"],
            "body_parameters": ["name", "description", "priority", "dueDate", "projectId", "assigneeId", "tags", "customFields"],
            "display_name": "Create Task",
            "description": "Create a new task",
            "group": "Tasks",
            "tags": ["tasks", "create", "write"],
            "rate_limit_cost": 2,
            
            "field_mapping": {
                "input_transforms": {
                    "due_date": "to_camel_case->dueDate",
                    "project_id": "to_camel_case->projectId",
                    "assignee_id": "to_camel_case->assigneeId",
                    "custom_fields": "to_camel_case->customFields"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "update_task": {
            "method": "PUT",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id"],
            "optional_params": ["name", "description", "priority", "due_date", "assignee_id", "status", "tags", "custom_fields"],
            "body_parameters": ["name", "description", "priority", "dueDate", "assigneeId", "status", "tags", "customFields"],
            "display_name": "Update Task",
            "description": "Update an existing task",
            "group": "Tasks",
            "tags": ["tasks", "update", "write"],
            "rate_limit_cost": 2,
            
            "field_mapping": {
                "input_transforms": {
                    "due_date": "to_camel_case->dueDate",
                    "assignee_id": "to_camel_case->assigneeId",
                    "custom_fields": "to_camel_case->customFields"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "delete_task": {
            "method": "DELETE",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id"],
            "optional_params": [],
            "display_name": "Delete Task",
            "description": "Delete a task",
            "group": "Tasks",
            "tags": ["tasks", "delete", "write"],
            "rate_limit_cost": 2,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_task": {
            "method": "GET",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id"],
            "optional_params": [],
            "display_name": "Get Task",
            "description": "Get a specific task by ID",
            "group": "Tasks",
            "tags": ["tasks", "read", "single"],
            "rate_limit_cost": 1,
            "cache_ttl": 180,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_task_comments": {
            "method": "GET",
            "endpoint": "/tasks/{task_id}/comments",
            "required_params": ["task_id"],
            "optional_params": [],
            "display_name": "Get Task Comments",
            "description": "Get comments for a specific task",
            "group": "Tasks",
            "tags": ["tasks", "comments", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_task_comment": {
            "method": "POST",
            "endpoint": "/tasks/{task_id}/comments",
            "required_params": ["task_id", "comment"],
            "optional_params": [],
            "body_parameters": ["text"],
            "display_name": "Create Task Comment",
            "description": "Add a comment to a task",
            "group": "Tasks",
            "tags": ["tasks", "comments", "write"],
            "rate_limit_cost": 1,
            
            "field_mapping": {
                "input_transforms": {
                    "comment": "rename->text"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_task_dependencies": {
            "method": "GET",
            "endpoint": "/tasks/{task_id}/dependencies",
            "required_params": ["task_id"],
            "optional_params": [],
            "display_name": "Get Task Dependencies",
            "description": "Get dependencies for a specific task",
            "group": "Tasks",
            "tags": ["tasks", "dependencies", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "add_task_dependency": {
            "method": "POST",
            "endpoint": "/tasks/{task_id}/dependencies",
            "required_params": ["task_id", "dependency_id"],
            "optional_params": [],
            "body_parameters": ["dependencyTaskId"],
            "display_name": "Add Task Dependency",
            "description": "Add a dependency to a task",
            "group": "Tasks",
            "tags": ["tasks", "dependencies", "write"],
            "rate_limit_cost": 2,
            
            "field_mapping": {
                "input_transforms": {
                    "dependency_id": "to_camel_case->dependencyTaskId"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "assign_task": {
            "method": "PATCH",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id", "assignee_id"],
            "optional_params": [],
            "body_parameters": ["assigneeId"],
            "display_name": "Assign Task",
            "description": "Assign a task to a user",
            "group": "Tasks",
            "tags": ["tasks", "assignment", "write"],
            "rate_limit_cost": 1,
            
            "field_mapping": {
                "input_transforms": {
                    "assignee_id": "to_camel_case->assigneeId"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_task_lists": {
            "method": "GET",
            "endpoint": "/projects/{project_id}/tasklists",
            "required_params": ["project_id"],
            "optional_params": [],
            "display_name": "Get Task Lists",
            "description": "Get task lists for a project",
            "group": "Tasks",
            "tags": ["tasks", "lists", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_task_list": {
            "method": "POST",
            "endpoint": "/projects/{project_id}/tasklists",
            "required_params": ["project_id", "name"],
            "optional_params": [],
            "body_parameters": ["name"],
            "display_name": "Create Task List",
            "description": "Create a task list for a project",
            "group": "Tasks",
            "tags": ["tasks", "lists", "write"],
            "rate_limit_cost": 2,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },

        # TIME TRACKING OPERATIONS
        "get_time_entries": {
            "method": "GET",
            "endpoint": "/timeentries",
            "required_params": [],
            "optional_params": ["filter_by", "order_by", "page", "page_size"],
            "display_name": "Get Time Entries",
            "description": "Retrieve list of time entries",
            "group": "Time Tracking",
            "tags": ["time", "entries", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 120,
            
            "pagination": {
                "type": "page_based",
                "page_param": "page",
                "size_param": "page_size",
                "default_size": 50
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_time_entry": {
            "method": "POST",
            "endpoint": "/timeentries",
            "required_params": ["duration"],
            "optional_params": ["description", "start_date", "task_id", "project_id", "user_id", "billable"],
            "body_parameters": ["duration", "description", "startTime", "taskId", "projectId", "userId", "isBillable"],
            "display_name": "Create Time Entry",
            "description": "Create a new time entry",
            "group": "Time Tracking",
            "tags": ["time", "entries", "write"],
            "rate_limit_cost": 2,
            
            "field_mapping": {
                "input_transforms": {
                    "start_date": "to_camel_case->startTime",
                    "task_id": "to_camel_case->taskId",
                    "project_id": "to_camel_case->projectId",
                    "user_id": "to_camel_case->userId",
                    "billable": "to_camel_case->isBillable"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "update_time_entry": {
            "method": "PUT",
            "endpoint": "/timeentries/{time_entry_id}",
            "required_params": ["time_entry_id"],
            "optional_params": ["duration", "description", "billable"],
            "body_parameters": ["duration", "description", "isBillable"],
            "display_name": "Update Time Entry",
            "description": "Update an existing time entry",
            "group": "Time Tracking",
            "tags": ["time", "entries", "write"],
            "rate_limit_cost": 2,
            
            "field_mapping": {
                "input_transforms": {
                    "billable": "to_camel_case->isBillable"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "delete_time_entry": {
            "method": "DELETE",
            "endpoint": "/timeentries/{time_entry_id}",
            "required_params": ["time_entry_id"],
            "optional_params": [],
            "display_name": "Delete Time Entry",
            "description": "Delete a time entry",
            "group": "Time Tracking",
            "tags": ["time", "entries", "delete"],
            "rate_limit_cost": 2,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "start_timer": {
            "method": "POST",
            "endpoint": "/timetracking/start",
            "required_params": [],
            "optional_params": ["description", "task_id", "project_id"],
            "body_parameters": ["description", "taskId", "projectId"],
            "display_name": "Start Timer",
            "description": "Start a time tracking timer",
            "group": "Time Tracking",
            "tags": ["time", "timer", "start"],
            "rate_limit_cost": 1,
            
            "field_mapping": {
                "input_transforms": {
                    "task_id": "to_camel_case->taskId",
                    "project_id": "to_camel_case->projectId"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "stop_timer": {
            "method": "POST",
            "endpoint": "/timetracking/stop",
            "required_params": [],
            "optional_params": [],
            "display_name": "Stop Timer",
            "description": "Stop the currently running timer",
            "group": "Time Tracking",
            "tags": ["time", "timer", "stop"],
            "rate_limit_cost": 1,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_time_reports": {
            "method": "GET",
            "endpoint": "/timereports",
            "required_params": [],
            "optional_params": ["start_date", "end_date"],
            "display_name": "Get Time Reports",
            "description": "Get time tracking reports",
            "group": "Time Tracking",
            "tags": ["time", "reports", "read"],
            "rate_limit_cost": 2,
            "cache_ttl": 600,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },

        # USER OPERATIONS
        "get_users": {
            "method": "GET",
            "endpoint": "/users",
            "required_params": [],
            "optional_params": ["filter_by", "order_by", "page", "page_size"],
            "display_name": "Get Users",
            "description": "Retrieve list of users",
            "group": "Users",
            "tags": ["users", "list", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            
            "pagination": {
                "type": "page_based",
                "page_param": "page",
                "size_param": "page_size",
                "default_size": 50
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_user": {
            "method": "GET",
            "endpoint": "/users/{user_id}",
            "required_params": ["user_id"],
            "optional_params": [],
            "display_name": "Get User",
            "description": "Get a specific user by ID",
            "group": "Users",
            "tags": ["users", "read", "single"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "update_user": {
            "method": "PUT",
            "endpoint": "/users/{user_id}",
            "required_params": ["user_id"],
            "optional_params": ["name", "email", "title", "department"],
            "body_parameters": ["name", "email", "title", "department"],
            "display_name": "Update User",
            "description": "Update user information",
            "group": "Users",
            "tags": ["users", "update", "write"],
            "rate_limit_cost": 2,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_user_capacities": {
            "method": "GET",
            "endpoint": "/users/{user_id}/capacities",
            "required_params": ["user_id"],
            "optional_params": [],
            "display_name": "Get User Capacities",
            "description": "Get capacity information for a user",
            "group": "Users",
            "tags": ["users", "capacity", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_user_absences": {
            "method": "GET",
            "endpoint": "/users/{user_id}/absences",
            "required_params": ["user_id"],
            "optional_params": [],
            "display_name": "Get User Absences",
            "description": "Get absence information for a user",
            "group": "Users",
            "tags": ["users", "absences", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_user_absence": {
            "method": "POST",
            "endpoint": "/users/{user_id}/absences",
            "required_params": ["user_id", "start_date", "end_date"],
            "optional_params": ["description"],
            "body_parameters": ["startDate", "endDate", "reason"],
            "display_name": "Create User Absence",
            "description": "Create an absence record for a user",
            "group": "Users",
            "tags": ["users", "absences", "write"],
            "rate_limit_cost": 2,
            
            "field_mapping": {
                "input_transforms": {
                    "start_date": "to_camel_case->startDate",
                    "end_date": "to_camel_case->endDate",
                    "description": "rename->reason"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_my_profile": {
            "method": "GET",
            "endpoint": "/me",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get My Profile",
            "description": "Get current user profile information",
            "group": "Users",
            "tags": ["users", "profile", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },

        # TEAM OPERATIONS
        "get_teams": {
            "method": "GET",
            "endpoint": "/teams",
            "required_params": [],
            "optional_params": ["filter_by", "order_by", "page", "page_size"],
            "display_name": "Get Teams",
            "description": "Retrieve list of teams",
            "group": "Teams",
            "tags": ["teams", "list", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            
            "pagination": {
                "type": "page_based",
                "page_param": "page",
                "size_param": "page_size",
                "default_size": 50
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_team": {
            "method": "POST",
            "endpoint": "/teams",
            "required_params": ["name"],
            "optional_params": ["description"],
            "body_parameters": ["name", "description"],
            "display_name": "Create Team",
            "description": "Create a new team",
            "group": "Teams",
            "tags": ["teams", "create", "write"],
            "rate_limit_cost": 2,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "update_team": {
            "method": "PUT",
            "endpoint": "/teams/{team_id}",
            "required_params": ["team_id"],
            "optional_params": ["name", "description"],
            "body_parameters": ["name", "description"],
            "display_name": "Update Team",
            "description": "Update an existing team",
            "group": "Teams",
            "tags": ["teams", "update", "write"],
            "rate_limit_cost": 2,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "delete_team": {
            "method": "DELETE",
            "endpoint": "/teams/{team_id}",
            "required_params": ["team_id"],
            "optional_params": [],
            "display_name": "Delete Team",
            "description": "Delete a team",
            "group": "Teams",
            "tags": ["teams", "delete", "write"],
            "rate_limit_cost": 3,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_team_members": {
            "method": "GET",
            "endpoint": "/teams/{team_id}/members",
            "required_params": ["team_id"],
            "optional_params": [],
            "display_name": "Get Team Members",
            "description": "Get members of a specific team",
            "group": "Teams",
            "tags": ["teams", "members", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 180,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "add_team_member": {
            "method": "POST",
            "endpoint": "/teams/{team_id}/members",
            "required_params": ["team_id", "user_id"],
            "optional_params": [],
            "body_parameters": ["userId"],
            "display_name": "Add Team Member",
            "description": "Add a member to a team",
            "group": "Teams",
            "tags": ["teams", "members", "write"],
            "rate_limit_cost": 2,
            
            "field_mapping": {
                "input_transforms": {
                    "user_id": "to_camel_case->userId"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },

        # COMPANY OPERATIONS
        "get_companies": {
            "method": "GET",
            "endpoint": "/companies",
            "required_params": [],
            "optional_params": ["filter_by", "order_by", "page", "page_size"],
            "display_name": "Get Companies",
            "description": "Retrieve list of companies",
            "group": "Companies",
            "tags": ["companies", "list", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            
            "pagination": {
                "type": "page_based",
                "page_param": "page",
                "size_param": "page_size",
                "default_size": 50
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_company": {
            "method": "POST",
            "endpoint": "/companies",
            "required_params": ["name"],
            "optional_params": ["description", "tags"],
            "body_parameters": ["name", "description", "tags"],
            "display_name": "Create Company",
            "description": "Create a new company",
            "group": "Companies",
            "tags": ["companies", "create", "write"],
            "rate_limit_cost": 3,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "update_company": {
            "method": "PUT",
            "endpoint": "/companies/{company_id}",
            "required_params": ["company_id"],
            "optional_params": ["name", "description", "tags"],
            "body_parameters": ["name", "description", "tags"],
            "display_name": "Update Company",
            "description": "Update an existing company",
            "group": "Companies",
            "tags": ["companies", "update", "write"],
            "rate_limit_cost": 3,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "delete_company": {
            "method": "DELETE",
            "endpoint": "/companies/{company_id}",
            "required_params": ["company_id"],
            "optional_params": [],
            "display_name": "Delete Company",
            "description": "Delete a company",
            "group": "Companies",
            "tags": ["companies", "delete", "write"],
            "rate_limit_cost": 5,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },

        # WORKSPACE OPERATIONS
        "get_workspace": {
            "method": "GET",
            "endpoint": "/workspace",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Workspace",
            "description": "Get current workspace information",
            "group": "Workspace",
            "tags": ["workspace", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "update_workspace": {
            "method": "PUT",
            "endpoint": "/workspace",
            "required_params": [],
            "optional_params": ["name", "description"],
            "body_parameters": ["name", "description"],
            "display_name": "Update Workspace",
            "description": "Update workspace information",
            "group": "Workspace",
            "tags": ["workspace", "update", "write"],
            "rate_limit_cost": 3,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_workspace_settings": {
            "method": "GET",
            "endpoint": "/workspace/settings",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Workspace Settings",
            "description": "Get workspace settings",
            "group": "Workspace",
            "tags": ["workspace", "settings", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 1200,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },

        # OTHER OPERATIONS
        "get_custom_fields": {
            "method": "GET",
            "endpoint": "/customfields",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Custom Fields",
            "description": "Get list of custom fields",
            "group": "Configuration",
            "tags": ["custom", "fields", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 1200,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_custom_field": {
            "method": "POST",
            "endpoint": "/customfields",
            "required_params": ["name"],
            "optional_params": ["field_type"],
            "body_parameters": ["name", "type"],
            "display_name": "Create Custom Field",
            "description": "Create a new custom field",
            "group": "Configuration",
            "tags": ["custom", "fields", "write"],
            "rate_limit_cost": 3,
            
            "field_mapping": {
                "input_transforms": {
                    "field_type": "rename->type"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_project_templates": {
            "method": "GET",
            "endpoint": "/projecttemplates",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Project Templates",
            "description": "Get list of project templates",
            "group": "Templates",
            "tags": ["templates", "projects", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 1200,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_project_from_template": {
            "method": "POST",
            "endpoint": "/projects/fromtemplate",
            "required_params": ["template_id", "name"],
            "optional_params": [],
            "body_parameters": ["name", "templateId"],
            "display_name": "Create Project from Template",
            "description": "Create a new project from a template",
            "group": "Templates",
            "tags": ["templates", "projects", "create"],
            "rate_limit_cost": 5,
            
            "field_mapping": {
                "input_transforms": {
                    "template_id": "to_camel_case->templateId"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "get_webhooks": {
            "method": "GET",
            "endpoint": "/webhooks",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Webhooks",
            "description": "Get list of configured webhooks",
            "group": "Webhooks",
            "tags": ["webhooks", "read"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "create_webhook": {
            "method": "POST",
            "endpoint": "/webhooks",
            "required_params": ["webhook_url", "webhook_events"],
            "optional_params": [],
            "body_parameters": ["url", "events"],
            "display_name": "Create Webhook",
            "description": "Create a new webhook",
            "group": "Webhooks",
            "tags": ["webhooks", "create", "write"],
            "rate_limit_cost": 3,
            
            "field_mapping": {
                "input_transforms": {
                    "webhook_url": "rename->url",
                    "webhook_events": "split_comma->events"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "delete_webhook": {
            "method": "DELETE",
            "endpoint": "/webhooks/{webhook_id}",
            "required_params": ["webhook_id"],
            "optional_params": [],
            "display_name": "Delete Webhook",
            "description": "Delete a webhook",
            "group": "Webhooks",
            "tags": ["webhooks", "delete", "write"],
            "rate_limit_cost": 2,
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        },
        "search": {
            "method": "GET",
            "endpoint": "/search",
            "required_params": ["search_query"],
            "optional_params": [],
            "display_name": "Search",
            "description": "Search across Awork resources",
            "group": "Search",
            "tags": ["search", "find", "read"],
            "rate_limit_cost": 2,
            "cache_ttl": 60,
            
            "field_mapping": {
                "input_transforms": {
                    "search_query": "rename->q"
                }
            },
            
            "auth": {
                "required_env_keys": ["AWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token"
            }
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced Awork node with embedded configuration."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Initialize the Enhanced UniversalRequestNode with embedded config
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.info("Enhanced AworkNode initialized with all 13 advanced features and 70 operations")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"AworkNode executing operation: {node_data.get('params', {}).get('operation')}")
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
__all__ = ["AworkNode"]