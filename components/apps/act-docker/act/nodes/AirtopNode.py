#!/usr/bin/env python3
"""
Airtop Node - COMPLETE RECOVERY with ALL 35 original operations + Enhanced Structure + Array Templates
Configuration is embedded directly in the node - no separate config.json needed
RECOVERED FROM CATASTROPHIC DATA LOSS - ALL ORIGINAL OPERATIONS RESTORED
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

class AirtopNode(BaseNode):
    """
    EMERGENCY RECOVERY: Enhanced Airtop node with ALL 35 original operations restored + Enhanced structure.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    INCLUDES PROPER ARRAY TEMPLATES for complex operations!
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "airtop",
            "display_name": "Airtop",
            "description": "Comprehensive Airtop API integration for cloud browser automation, AI-powered web interactions, session management, content extraction, and complete browser control",
            "category": "automation",
            "vendor": "airtop",
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["browser", "automation", "web-scraping", "ai", "sessions", "cloud", "forms", "content-extraction"],
            "documentation_url": "https://docs.airtop.ai",
            "icon": "https://airtop.ai/favicon.ico",
            "color": "#00A4E4",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.airtop.ai/v1",
            "authentication": {
                "type": "api_key",
                "header": "X-API-Key"
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
                "max_delay": 120.0,
                "jitter": True,
                "retriable_codes": [429, 500, 502, 503, 504],
                "retriable_exceptions": ["aiohttp.ClientTimeout", "aiohttp.ClientConnectorError"],
                "timeout_ms": 60000
            },
            "rate_limiting": {
                "requests_per_minute": 60,
                "requests_per_second": 1.0,
                "burst_size": 5,
                "cost_per_request": 0.05,
                "quota_type": "requests"
            },
            "timeouts": {
                "connect": 15.0,
                "read": 60.0,
                "total": 120.0
            }
        },
        
        # Enhanced pricing information
        "pricing": {
            "cost_per_1k_requests": 50.00,
            "cost_per_request": 0.05,
            "billing_unit": "requests",
            "free_tier_limit": 50
        },
        
        # Performance monitoring
        "monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "request_count", "session_count"],
            "alerts": {
                "error_rate_threshold": 0.10,
                "response_time_threshold": 10000
            }
        },
        
        # Intelligent caching
        "caching": {
            "enabled": True,
            "cache_key_template": "{operation}:{hash}",
            "ttl_seconds": 60,
            "cache_conditions": {
                "only_for": ["GET"],
                "exclude_params": ["timestamp", "session_id", "window_id"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": True,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/sessions"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://docs.airtop.ai/api-reference",
            "setup_guide": "https://docs.airtop.ai/quickstart",
            "troubleshooting": "https://docs.airtop.ai/troubleshooting",
            "changelog": "https://docs.airtop.ai/changelog"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "Airtop API key",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^ak_[a-zA-Z0-9]{32,}$",
                    "message": "API key must start with 'ak_' followed by alphanumeric characters",
                    "minLength": 35,
                    "maxLength": 100
                }
            },
            "operation": {
                "type": "string",
                "description": "The Airtop operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    "list_sessions", "create_session", "get_session", "terminate_session", "save_profile",
                    "list_windows", "create_window", "get_window", "load_url", "close_window",
                    "click", "type", "hover", "scroll", "screenshot", "file_input",
                    "fill_form", "async_fill_form", "async_create_form_filler",
                    "page_query", "paginated_extraction", "monitor_conditions",
                    "async_create_automation", "async_execute_automation", "list_automations",
                    "get_automation", "update_automation", "delete_automation",
                    "delete_profile", "list_files", "create_file", "get_file", "delete_file", "push_file",
                    "get_request_status"
                ]
            },
            "session_id": {
                "type": "string",
                "description": "Browser session ID for session-specific operations",
                "required": False,
                "group": "Resource",
                "examples": ["ses_1234567890abcdef"],
                "validation": {
                    "pattern": "^ses_[a-f0-9]{16}$",
                    "message": "Session ID must start with 'ses_' followed by 16 hex characters"
                }
            },
            "window_id": {
                "type": "string",
                "description": "Window ID for window-specific operations",
                "required": False,
                "group": "Resource",
                "examples": ["win_1234567890abcdef"],
                "validation": {
                    "pattern": "^win_[a-f0-9]{16}$",
                    "message": "Window ID must start with 'win_' followed by 16 hex characters"
                }
            },
            "automation_id": {
                "type": "string",
                "description": "Automation ID for automation operations",
                "required": False,
                "group": "Resource",
                "examples": ["auto_1234567890abcdef"]
            },
            "profile_id": {
                "type": "string",
                "description": "Profile ID for profile operations",
                "required": False,
                "group": "Resource",
                "examples": ["prof_1234567890abcdef"]
            },
            "file_id": {
                "type": "string",
                "description": "File ID for file operations",
                "required": False,
                "group": "Resource",
                "examples": ["file_1234567890abcdef"]
            },
            "request_id": {
                "type": "string",
                "description": "Request ID for request status operations",
                "required": False,
                "group": "Resource",
                "examples": ["req_1234567890abcdef"]
            },
            "url": {
                "type": "string",
                "description": "URL to navigate to",
                "required": False,
                "group": "Navigation",
                "examples": ["https://example.com"],
                "validation": {
                    "pattern": "^https?://[a-zA-Z0-9.-]+(/.*)?$",
                    "message": "URL must be a valid HTTP or HTTPS URL"
                }
            },
            "selector": {
                "type": "string",
                "description": "CSS selector for element selection",
                "required": False,
                "group": "Interaction",
                "examples": ["#submit-button", ".login-form input"],
                "validation": {
                    "maxLength": 500
                }
            },
            "text": {
                "type": "string",
                "description": "Text to type into elements",
                "required": False,
                "group": "Interaction",
                "examples": ["Hello World", "user@example.com"],
                "validation": {
                    "maxLength": 1000
                }
            },
            "query": {
                "type": "string",
                "description": "Natural language query for page content",
                "required": False,
                "group": "Content",
                "examples": ["Find all product names", "Extract contact information"]
            },
            "conditions": {
                "type": "array",
                "description": "Array of conditions to monitor",
                "required": False,
                "group": "Monitoring"
            },
            "automation_steps": {
                "type": "array",
                "description": "Array of automation steps",
                "required": False,
                "group": "Automation"
            },
            "form_data": {
                "type": "object",
                "description": "Form data as key-value pairs",
                "required": False,
                "group": "Forms"
            },
            "configuration": {
                "type": "object",
                "description": "Browser session configuration",
                "required": False,
                "group": "Configuration"
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful Airtop API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from Airtop API"},
                    "result": {"type": "object", "description": "Full API response data"},
                    "resource_id": {"type": "string", "description": "Resource ID for created items"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Airtop error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "list_sessions": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "create_session": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "get_session": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "terminate_session": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "save_profile": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "list_windows": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "create_window": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "get_window": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "load_url": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "close_window": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "click": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "type": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "hover": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "scroll": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "screenshot": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "file_input": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "fill_form": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "async_fill_form": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "async_create_form_filler": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "page_query": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "paginated_extraction": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "monitor_conditions": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "async_create_automation": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "async_execute_automation": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "list_automations": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "get_automation": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "update_automation": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "delete_automation": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "delete_profile": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "list_files": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "create_file": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "get_file": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "delete_file": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "push_file": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []},
            "get_request_status": {"required_env_keys": ["AIRTOP_API_KEY"], "optional_env_keys": []}
        },
        
        # Error codes specific to Airtop
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid or missing API key",
            "403": "Forbidden - Access denied or insufficient permissions",
            "404": "Not Found - Session or resource not found",
            "408": "Timeout - Request timeout or browser operation timeout",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Airtop server error",
            "502": "Bad Gateway - Airtop server temporarily unavailable",
            "503": "Service Unavailable - Airtop server overloaded"
        }
    }
    
    # Enhanced operation definitions with ALL 35 ORIGINAL OPERATIONS + 13 advanced features
    OPERATIONS = {
        # SESSION OPERATIONS (5 operations)
        "list_sessions": {
            "method": "GET",
            "endpoint": "/sessions",
            "required_params": [],
            "optional_params": [],
            "display_name": "List Sessions",
            "description": "Retrieve a list of active browser sessions",
            "group": "Sessions",
            "tags": ["sessions", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"},
                            "status": {"type": "string", "enum": ["active", "terminated"]},
                            "created_at": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "List all sessions", "input": {}}]
        },
        "create_session": {
            "method": "POST",
            "endpoint": "/sessions",
            "required_params": [],
            "optional_params": ["configuration"],
            "body_parameters": ["configuration"],
            "display_name": "Create Session",
            "description": "Create a new browser session for web automation",
            "group": "Sessions",
            "tags": ["sessions", "create", "browser"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "status": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "array_templates": {
                "configuration.capabilities": [
                    {"template": {"name": "webDriver", "version": "latest"}, "description": "WebDriver capability"},
                    {"template": {"name": "chromeOptions", "args": ["--no-sandbox", "--disable-dev-shm-usage"]}, "description": "Chrome options"}
                ]
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {"name": "Create basic session", "input": {}},
                {"name": "Create session with config", "input": {"configuration": {"viewport": {"width": 1920, "height": 1080}}}}
            ]
        },
        "get_session": {
            "method": "GET",
            "endpoint": "/sessions/{session_id}",
            "required_params": ["session_id"],
            "optional_params": [],
            "display_name": "Get Session",
            "description": "Retrieve details of a specific session",
            "group": "Sessions",
            "tags": ["sessions", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 30,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "status": {"type": "string"},
                        "windows": {"type": "array"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {
                    "pattern": "^ses_[a-f0-9]{16}$",
                    "message": "Session ID must be valid",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Get session details", "input": {"session_id": "ses_1234567890abcdef"}}]
        },
        "terminate_session": {
            "method": "DELETE",
            "endpoint": "/sessions/{session_id}",
            "required_params": ["session_id"],
            "optional_params": [],
            "display_name": "Terminate Session",
            "description": "Terminate a browser session",
            "group": "Sessions",
            "tags": ["sessions", "terminate"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["terminated"]}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Terminate session", "input": {"session_id": "ses_1234567890abcdef"}}]
        },
        "save_profile": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/profile/save",
            "required_params": ["session_id"],
            "optional_params": ["profile_id"],
            "body_parameters": ["profile_id"],
            "display_name": "Save Profile",
            "description": "Save browser profile from session",
            "group": "Profiles",
            "tags": ["profiles", "save"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "profile_id": {"type": "string"},
                        "saved_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Save session profile", "input": {"session_id": "ses_1234567890abcdef"}}]
        },

        # WINDOW OPERATIONS (5 operations)
        "list_windows": {
            "method": "GET",
            "endpoint": "/sessions/{session_id}/windows",
            "required_params": ["session_id"],
            "optional_params": [],
            "display_name": "List Windows",
            "description": "List all windows in a session",
            "group": "Windows",
            "tags": ["windows", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 30,
            "response_type": "array",
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "window_id": {"type": "string"},
                            "title": {"type": "string"},
                            "url": {"type": "string"}
                        }
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "List session windows", "input": {"session_id": "ses_1234567890abcdef"}}]
        },
        "create_window": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows",
            "required_params": ["session_id"],
            "optional_params": ["url"],
            "body_parameters": ["url"],
            "display_name": "Create Window",
            "description": "Create a new window in a session",
            "group": "Windows",
            "tags": ["windows", "create"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "window_id": {"type": "string"},
                        "url": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "url": {"pattern": "^https?://", "required": False}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {"name": "Create blank window", "input": {"session_id": "ses_1234567890abcdef"}},
                {"name": "Create window with URL", "input": {"session_id": "ses_1234567890abcdef", "url": "https://example.com"}}
            ]
        },
        "get_window": {
            "method": "GET",
            "endpoint": "/sessions/{session_id}/windows/{window_id}",
            "required_params": ["session_id", "window_id"],
            "optional_params": [],
            "display_name": "Get Window",
            "description": "Get details of a specific window",
            "group": "Windows",
            "tags": ["windows", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 30,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "window_id": {"type": "string"},
                        "title": {"type": "string"},
                        "url": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Get window details", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef"}}]
        },
        "load_url": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/navigate",
            "required_params": ["session_id", "window_id", "url"],
            "optional_params": [],
            "body_parameters": ["url"],
            "display_name": "Load URL",
            "description": "Navigate a window to a specific URL",
            "group": "Navigation",
            "tags": ["navigation", "url"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "title": {"type": "string"},
                        "load_time": {"type": "number"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True},
                "url": {"pattern": "^https?://", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Navigate to URL", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef", "url": "https://example.com"}}]
        },
        "close_window": {
            "method": "DELETE",
            "endpoint": "/sessions/{session_id}/windows/{window_id}",
            "required_params": ["session_id", "window_id"],
            "optional_params": [],
            "display_name": "Close Window",
            "description": "Close a specific window",
            "group": "Windows",
            "tags": ["windows", "close"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "window_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["closed"]}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Close window", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef"}}]
        },

        # BROWSER INTERACTION OPERATIONS (6 operations)
        "click": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/click",
            "required_params": ["session_id", "window_id", "selector"],
            "optional_params": [],
            "body_parameters": ["selector"],
            "display_name": "Click Element",
            "description": "Click on an element using CSS selector",
            "group": "Interaction",
            "tags": ["interaction", "click"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "element_found": {"type": "boolean"},
                        "selector": {"type": "string"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True},
                "selector": {"required": True, "max_length": 500}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Click button", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef", "selector": "#submit-button"}}]
        },
        "type": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/type",
            "required_params": ["session_id", "window_id", "selector", "text"],
            "optional_params": [],
            "body_parameters": ["selector", "text"],
            "display_name": "Type Text",
            "description": "Type text into an element",
            "group": "Interaction",
            "tags": ["interaction", "input", "type"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "text_entered": {"type": "string"},
                        "element_found": {"type": "boolean"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True},
                "selector": {"required": True, "max_length": 500},
                "text": {"required": True, "max_length": 1000}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Type in input field", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef", "selector": "#email", "text": "user@example.com"}}]
        },
        "hover": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/hover",
            "required_params": ["session_id", "window_id", "selector"],
            "optional_params": [],
            "body_parameters": ["selector"],
            "display_name": "Hover Element",
            "description": "Hover over an element using CSS selector",
            "group": "Interaction",
            "tags": ["interaction", "hover"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "element_found": {"type": "boolean"},
                        "selector": {"type": "string"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True},
                "selector": {"required": True, "max_length": 500}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Hover over menu", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef", "selector": ".dropdown-menu"}}]
        },
        "scroll": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/scroll",
            "required_params": ["session_id", "window_id"],
            "optional_params": ["selector", "direction", "amount"],
            "body_parameters": ["selector", "direction", "amount"],
            "display_name": "Scroll Page",
            "description": "Scroll the page or a specific element",
            "group": "Interaction",
            "tags": ["interaction", "scroll"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "scroll_position": {"type": "object"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {"name": "Scroll down page", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef", "direction": "down", "amount": 500}},
                {"name": "Scroll element", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef", "selector": ".scrollable-div", "direction": "down"}}
            ]
        },
        "screenshot": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/screenshot",
            "required_params": ["session_id", "window_id"],
            "optional_params": ["selector", "full_page"],
            "body_parameters": ["selector", "full_page"],
            "display_name": "Take Screenshot",
            "description": "Take a screenshot of the page or element",
            "group": "Capture",
            "tags": ["screenshot", "capture"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "image_data": {"type": "string", "description": "Base64 encoded image"},
                        "format": {"type": "string", "enum": ["png", "jpeg"]},
                        "width": {"type": "integer"},
                        "height": {"type": "integer"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {"name": "Full page screenshot", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef", "full_page": True}},
                {"name": "Element screenshot", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef", "selector": ".main-content"}}
            ]
        },
        "file_input": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/file-input",
            "required_params": ["session_id", "window_id", "selector", "file_path"],
            "optional_params": [],
            "body_parameters": ["selector", "file_path"],
            "display_name": "File Input",
            "description": "Upload a file to a file input element",
            "group": "Interaction",
            "tags": ["interaction", "file", "upload"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "file_uploaded": {"type": "string"},
                        "element_found": {"type": "boolean"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True},
                "selector": {"required": True, "max_length": 500},
                "file_path": {"required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Upload file", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef", "selector": "input[type='file']", "file_path": "/path/to/file.pdf"}}]
        },

        # FORM OPERATIONS (3 operations)
        "fill_form": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/fill-form",
            "required_params": ["session_id", "window_id", "form_data"],
            "optional_params": ["selector"],
            "body_parameters": ["form_data", "selector"],
            "display_name": "Fill Form",
            "description": "Fill out a form with data",
            "group": "Forms",
            "tags": ["forms", "fill", "automation"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "fields_filled": {"type": "integer"},
                        "form_selector": {"type": "string"}
                    }
                }
            },
            "array_templates": {
                "form_data": [
                    {"template": {"field": "email", "value": "user@example.com", "type": "input"}, "description": "Email input field"},
                    {"template": {"field": "password", "value": "password123", "type": "password"}, "description": "Password input field"},
                    {"template": {"field": "name", "value": "John Doe", "type": "input"}, "description": "Name input field"},
                    {"template": {"field": "phone", "value": "+1234567890", "type": "tel"}, "description": "Phone input field"},
                    {"template": {"field": "country", "value": "US", "type": "select", "selector": "#country-select"}, "description": "Country dropdown"},
                    {"template": {"field": "terms", "value": True, "type": "checkbox", "selector": "#terms-checkbox"}, "description": "Terms checkbox"},
                    {"template": {"field": "newsletter", "value": False, "type": "checkbox"}, "description": "Newsletter subscription"}
                ]
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True},
                "form_data": {"required": True, "type": "object"}
            },
            "parameter_dependencies": [
                {
                    "when_field": "form_data",
                    "when_value": "exists",
                    "then_require": [],
                    "then_optional": ["selector"],
                    "require_one_of": [],
                    "mutually_exclusive": []
                }
            ],
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {
                    "name": "Fill contact form",
                    "input": {
                        "session_id": "ses_1234567890abcdef",
                        "window_id": "win_1234567890abcdef",
                        "form_data": {
                            "name": "John Doe",
                            "email": "john@example.com",
                            "message": "Hello, this is a test message"
                        }
                    }
                }
            ]
        },
        "async_fill_form": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/async-fill-form",
            "required_params": ["session_id", "window_id", "form_data"],
            "optional_params": ["selector"],
            "body_parameters": ["form_data", "selector"],
            "display_name": "Async Fill Form",
            "description": "Asynchronously fill out a form with data",
            "group": "Forms",
            "tags": ["forms", "fill", "async", "automation"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "request_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["pending", "in_progress"]},
                        "estimated_time": {"type": "number"}
                    }
                }
            },
            "array_templates": {
                "form_data": [
                    {"template": {"field": "username", "value": "user123", "type": "input", "wait_after": 1000}, "description": "Username with delay"},
                    {"template": {"field": "bio", "value": "Long biography text...", "type": "textarea", "typing_speed": "slow"}, "description": "Textarea with typing speed"},
                    {"template": {"field": "category", "value": "Technology", "type": "select", "wait_for_options": True}, "description": "Dynamic select dropdown"}
                ]
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True},
                "form_data": {"required": True, "type": "object"}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {
                    "name": "Async form filling",
                    "input": {
                        "session_id": "ses_1234567890abcdef",
                        "window_id": "win_1234567890abcdef",
                        "form_data": {
                            "firstName": "John",
                            "lastName": "Doe",
                            "email": "john.doe@example.com"
                        }
                    }
                }
            ]
        },
        "async_create_form_filler": {
            "method": "POST",
            "endpoint": "/form-fillers",
            "required_params": ["form_description"],
            "optional_params": ["session_id", "window_id"],
            "body_parameters": ["form_description", "session_id", "window_id"],
            "display_name": "Create Form Filler",
            "description": "Create an AI-powered form filler from description",
            "group": "AI Forms",
            "tags": ["forms", "ai", "automation", "smart-fill"],
            "rate_limit_cost": 5,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "filler_id": {"type": "string"},
                        "status": {"type": "string"},
                        "description": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "validation_rules": {
                "form_description": {"required": True, "min_length": 10, "max_length": 2000}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {
                    "name": "Create registration form filler",
                    "input": {
                        "form_description": "Fill out a user registration form with name, email, phone, and address fields"
                    }
                }
            ]
        },

        # PAGE QUERY AND EXTRACTION OPERATIONS (3 operations)
        "page_query": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/query",
            "required_params": ["session_id", "window_id", "query"],
            "optional_params": [],
            "body_parameters": ["query"],
            "display_name": "Page Query",
            "description": "Query page content using natural language",
            "group": "AI Query",
            "tags": ["ai", "query", "content", "extraction"],
            "rate_limit_cost": 3,
            "cache_ttl": 60,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "results": {"type": "array"},
                        "confidence": {"type": "number"},
                        "elements_found": {"type": "integer"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True},
                "query": {"required": True, "min_length": 5, "max_length": 500}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {"name": "Find products", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef", "query": "Find all product names and prices"}},
                {"name": "Extract contacts", "input": {"session_id": "ses_1234567890abcdef", "window_id": "win_1234567890abcdef", "query": "Extract contact information from this page"}}
            ]
        },
        "paginated_extraction": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/extract-paginated",
            "required_params": ["session_id", "window_id", "query"],
            "optional_params": ["max_pages", "next_button_selector"],
            "body_parameters": ["query", "max_pages", "next_button_selector"],
            "display_name": "Paginated Extraction",
            "description": "Extract data across multiple pages",
            "group": "AI Extraction",
            "tags": ["ai", "extraction", "pagination", "scraping"],
            "rate_limit_cost": 5,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "total_items": {"type": "integer"},
                        "pages_processed": {"type": "integer"},
                        "data": {"type": "array"},
                        "status": {"type": "string"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True},
                "query": {"required": True, "min_length": 5},
                "max_pages": {"required": False, "min_value": 1, "max_value": 100}
            },
            "parameter_dependencies": [
                {
                    "when_field": "max_pages",
                    "when_value": ">1",
                    "then_require": [],
                    "then_optional": ["next_button_selector"],
                    "require_one_of": [],
                    "mutually_exclusive": []
                }
            ],
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {
                    "name": "Extract product listings",
                    "input": {
                        "session_id": "ses_1234567890abcdef",
                        "window_id": "win_1234567890abcdef",
                        "query": "Extract product name, price, and rating from all listings",
                        "max_pages": 5,
                        "next_button_selector": ".next-page"
                    }
                }
            ]
        },
        "monitor_conditions": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/windows/{window_id}/monitor",
            "required_params": ["session_id", "window_id", "conditions"],
            "optional_params": ["timeout", "interval"],
            "body_parameters": ["conditions", "timeout", "interval"],
            "display_name": "Monitor Conditions",
            "description": "Monitor page for specific conditions",
            "group": "Monitoring",
            "tags": ["monitoring", "conditions", "waiting"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "conditions_met": {"type": "array"},
                        "timeout_reached": {"type": "boolean"},
                        "monitoring_time": {"type": "number"},
                        "status": {"type": "string"}
                    }
                }
            },
            "array_templates": {
                "conditions": [
                    {"template": {"type": "element_visible", "selector": "#loading-spinner", "negate": True}, "description": "Wait for loading to complete"},
                    {"template": {"type": "element_contains_text", "selector": ".status", "text": "Complete"}, "description": "Wait for specific text"},
                    {"template": {"type": "url_changes", "pattern": "/success"}, "description": "Wait for URL change"},
                    {"template": {"type": "element_clickable", "selector": "#submit-btn"}, "description": "Wait for element to be clickable"},
                    {"template": {"type": "page_loaded", "wait_for": "networkidle"}, "description": "Wait for network idle"},
                    {"template": {"type": "custom_script", "script": "return document.readyState === 'complete'"}, "description": "Custom JavaScript condition"}
                ]
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "window_id": {"pattern": "^win_[a-f0-9]{16}$", "required": True},
                "conditions": {"required": True, "type": "array", "min_items": 1},
                "timeout": {"required": False, "min_value": 1000, "max_value": 300000}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {
                    "name": "Wait for form submission",
                    "input": {
                        "session_id": "ses_1234567890abcdef",
                        "window_id": "win_1234567890abcdef",
                        "conditions": [
                            {"type": "element_visible", "selector": ".success-message"},
                            {"type": "url_contains", "text": "success"}
                        ],
                        "timeout": 30000
                    }
                }
            ]
        },

        # AUTOMATION OPERATIONS (6 operations)
        "async_create_automation": {
            "method": "POST",
            "endpoint": "/automations",
            "required_params": ["automation_description"],
            "optional_params": ["name", "session_id"],
            "body_parameters": ["automation_description", "name", "session_id"],
            "display_name": "Create Automation",
            "description": "Create an AI-powered automation from description",
            "group": "AI Automation",
            "tags": ["automation", "ai", "workflow"],
            "rate_limit_cost": 10,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "automation_id": {"type": "string"},
                        "name": {"type": "string"},
                        "status": {"type": "string"},
                        "description": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "validation_rules": {
                "automation_description": {"required": True, "min_length": 20, "max_length": 2000},
                "name": {"required": False, "max_length": 100}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {
                    "name": "Create login automation",
                    "input": {
                        "name": "Login Flow",
                        "automation_description": "Navigate to login page, enter credentials, and verify successful login"
                    }
                }
            ]
        },
        "async_execute_automation": {
            "method": "POST",
            "endpoint": "/automations/{automation_id}/execute",
            "required_params": ["automation_id"],
            "optional_params": ["session_id", "parameters"],
            "body_parameters": ["session_id", "parameters"],
            "display_name": "Execute Automation",
            "description": "Execute a previously created automation",
            "group": "AI Automation",
            "tags": ["automation", "execute", "workflow"],
            "rate_limit_cost": 8,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "execution_id": {"type": "string"},
                        "automation_id": {"type": "string"},
                        "status": {"type": "string"},
                        "started_at": {"type": "string", "format": "date-time"},
                        "estimated_duration": {"type": "number"}
                    }
                }
            },
            "array_templates": {
                "parameters": [
                    {"template": {"name": "username", "value": "user@example.com", "type": "string"}, "description": "Username parameter"},
                    {"template": {"name": "password", "value": "password123", "type": "string", "sensitive": True}, "description": "Password parameter"},
                    {"template": {"name": "wait_time", "value": 5000, "type": "number"}, "description": "Wait time in milliseconds"},
                    {"template": {"name": "retry_count", "value": 3, "type": "integer"}, "description": "Number of retries"}
                ]
            },
            "validation_rules": {
                "automation_id": {"pattern": "^auto_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {
                    "name": "Execute automation with parameters",
                    "input": {
                        "automation_id": "auto_1234567890abcdef",
                        "parameters": {
                            "username": "test@example.com",
                            "password": "testpass123"
                        }
                    }
                }
            ]
        },
        "list_automations": {
            "method": "GET",
            "endpoint": "/automations",
            "required_params": [],
            "optional_params": ["limit", "offset", "status"],
            "display_name": "List Automations",
            "description": "List all created automations",
            "group": "Automation",
            "tags": ["automation", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "automations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "automation_id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "status": {"type": "string"},
                                    "created_at": {"type": "string", "format": "date-time"}
                                }
                            }
                        },
                        "total_count": {"type": "integer"}
                    }
                }
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "List all automations", "input": {}}]
        },
        "get_automation": {
            "method": "GET",
            "endpoint": "/automations/{automation_id}",
            "required_params": ["automation_id"],
            "optional_params": [],
            "display_name": "Get Automation",
            "description": "Get details of a specific automation",
            "group": "Automation",
            "tags": ["automation", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "automation_id": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "status": {"type": "string"},
                        "steps": {"type": "array"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "validation_rules": {
                "automation_id": {"pattern": "^auto_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Get automation details", "input": {"automation_id": "auto_1234567890abcdef"}}]
        },
        "update_automation": {
            "method": "PUT",
            "endpoint": "/automations/{automation_id}",
            "required_params": ["automation_id"],
            "optional_params": ["name", "description", "steps"],
            "body_parameters": ["name", "description", "steps"],
            "display_name": "Update Automation",
            "description": "Update an existing automation",
            "group": "Automation",
            "tags": ["automation", "update"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "automation_id": {"type": "string"},
                        "updated_at": {"type": "string", "format": "date-time"},
                        "status": {"type": "string"}
                    }
                }
            },
            "array_templates": {
                "steps": [
                    {"template": {"action": "navigate", "url": "https://example.com", "wait_for": "load"}, "description": "Navigation step"},
                    {"template": {"action": "click", "selector": "#login-btn", "wait_after": 2000}, "description": "Click step with wait"},
                    {"template": {"action": "type", "selector": "#username", "text": "${username}", "clear_first": True}, "description": "Input step with parameter"},
                    {"template": {"action": "wait", "condition": "element_visible", "selector": ".success-message", "timeout": 10000}, "description": "Wait condition step"},
                    {"template": {"action": "extract", "query": "Get the page title", "store_as": "page_title"}, "description": "Data extraction step"}
                ]
            },
            "validation_rules": {
                "automation_id": {"pattern": "^auto_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {
                    "name": "Update automation name",
                    "input": {
                        "automation_id": "auto_1234567890abcdef",
                        "name": "Updated Login Flow",
                        "description": "Enhanced login automation with error handling"
                    }
                }
            ]
        },
        "delete_automation": {
            "method": "DELETE",
            "endpoint": "/automations/{automation_id}",
            "required_params": ["automation_id"],
            "optional_params": [],
            "display_name": "Delete Automation",
            "description": "Delete an automation",
            "group": "Automation",
            "tags": ["automation", "delete"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "automation_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["deleted"]},
                        "deleted_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "validation_rules": {
                "automation_id": {"pattern": "^auto_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Delete automation", "input": {"automation_id": "auto_1234567890abcdef"}}]
        },

        # PROFILE OPERATIONS (1 operation)
        "delete_profile": {
            "method": "DELETE",
            "endpoint": "/profiles/{profile_id}",
            "required_params": ["profile_id"],
            "optional_params": [],
            "display_name": "Delete Profile",
            "description": "Delete a saved browser profile",
            "group": "Profiles",
            "tags": ["profiles", "delete"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "profile_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["deleted"]},
                        "deleted_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "validation_rules": {
                "profile_id": {"pattern": "^prof_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Delete profile", "input": {"profile_id": "prof_1234567890abcdef"}}]
        },

        # FILE OPERATIONS (5 operations)
        "list_files": {
            "method": "GET",
            "endpoint": "/files",
            "required_params": [],
            "optional_params": ["limit", "offset", "type"],
            "display_name": "List Files",
            "description": "List uploaded files",
            "group": "Files",
            "tags": ["files", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "files": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "file_id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "size": {"type": "integer"},
                                    "type": {"type": "string"},
                                    "created_at": {"type": "string", "format": "date-time"}
                                }
                            }
                        },
                        "total_count": {"type": "integer"}
                    }
                }
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "List all files", "input": {}}]
        },
        "create_file": {
            "method": "POST",
            "endpoint": "/files",
            "required_params": ["file_data", "file_name"],
            "optional_params": ["file_type"],
            "body_parameters": ["file_data", "file_name", "file_type"],
            "display_name": "Create File",
            "description": "Upload and create a new file",
            "group": "Files",
            "tags": ["files", "upload", "create"],
            "rate_limit_cost": 5,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string"},
                        "name": {"type": "string"},
                        "size": {"type": "integer"},
                        "type": {"type": "string"},
                        "url": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "validation_rules": {
                "file_name": {"required": True, "max_length": 255},
                "file_data": {"required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {
                    "name": "Upload PDF file",
                    "input": {
                        "file_name": "document.pdf",
                        "file_type": "application/pdf",
                        "file_data": "base64_encoded_pdf_data_here"
                    }
                }
            ]
        },
        "get_file": {
            "method": "GET",
            "endpoint": "/files/{file_id}",
            "required_params": ["file_id"],
            "optional_params": [],
            "display_name": "Get File",
            "description": "Retrieve file details and content",
            "group": "Files",
            "tags": ["files", "download", "get"],
            "rate_limit_cost": 2,
            "cache_ttl": 300,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string"},
                        "name": {"type": "string"},
                        "size": {"type": "integer"},
                        "type": {"type": "string"},
                        "data": {"type": "string", "description": "Base64 encoded file data"},
                        "url": {"type": "string"}
                    }
                }
            },
            "validation_rules": {
                "file_id": {"pattern": "^file_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Get file details", "input": {"file_id": "file_1234567890abcdef"}}]
        },
        "delete_file": {
            "method": "DELETE",
            "endpoint": "/files/{file_id}",
            "required_params": ["file_id"],
            "optional_params": [],
            "display_name": "Delete File",
            "description": "Delete an uploaded file",
            "group": "Files",
            "tags": ["files", "delete"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["deleted"]},
                        "deleted_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "validation_rules": {
                "file_id": {"pattern": "^file_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Delete file", "input": {"file_id": "file_1234567890abcdef"}}]
        },
        "push_file": {
            "method": "POST",
            "endpoint": "/sessions/{session_id}/files/{file_id}/push",
            "required_params": ["session_id", "file_id"],
            "optional_params": ["target_path"],
            "body_parameters": ["target_path"],
            "display_name": "Push File to Session",
            "description": "Push a file to a browser session for use",
            "group": "Files",
            "tags": ["files", "push", "session"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string"},
                        "session_id": {"type": "string"},
                        "target_path": {"type": "string"},
                        "status": {"type": "string", "enum": ["pushed"]},
                        "pushed_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "validation_rules": {
                "session_id": {"pattern": "^ses_[a-f0-9]{16}$", "required": True},
                "file_id": {"pattern": "^file_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [
                {
                    "name": "Push file to session",
                    "input": {
                        "session_id": "ses_1234567890abcdef",
                        "file_id": "file_1234567890abcdef",
                        "target_path": "/downloads/document.pdf"
                    }
                }
            ]
        },

        # REQUEST OPERATIONS (1 operation)
        "get_request_status": {
            "method": "GET",
            "endpoint": "/requests/{request_id}",
            "required_params": ["request_id"],
            "optional_params": [],
            "display_name": "Get Request Status",
            "description": "Get the status of an asynchronous request",
            "group": "Requests",
            "tags": ["requests", "status", "async"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "request_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "failed"]},
                        "progress": {"type": "number", "minimum": 0, "maximum": 100},
                        "result": {"type": "object"},
                        "error": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "completed_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "validation_rules": {
                "request_id": {"pattern": "^req_[a-f0-9]{16}$", "required": True}
            },
            "auth": {
                "required_env_keys": ["AIRTOP_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            },
            "examples": [{"name": "Get request status", "input": {"request_id": "req_1234567890abcdef"}}]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the RECOVERED enhanced Airtop node with embedded configuration."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Initialize the Enhanced UniversalRequestNode with embedded config
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.info("EMERGENCY RECOVERY: Enhanced AirtopNode initialized with ALL 35 original operations restored + Enhanced features")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"AirtopNode executing operation: {node_data.get('params', {}).get('operation')}")
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
__all__ = ["AirtopNode"]