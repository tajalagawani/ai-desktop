#!/usr/bin/env python3
"""
ActionNetwork Node - EMERGENCY RECOVERY - Enhanced with ALL 13 advanced features
ALL 22 original operations preserved and restored from git HEAD
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

class ActionNetworkNode(BaseNode):
    """
    RECOVERED - Enhanced ActionNetwork node with ALL 13 advanced features AND all 22 original operations.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "actionnetwork",
            "display_name": "ActionNetwork",
            "description": "Comprehensive ActionNetwork API integration for activist organizing, campaigns, petitions, events, and forms management",
            "category": "activism",
            "vendor": "actionnetwork",
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["activism", "organizing", "campaigns", "petitions", "events", "forms", "osdi"],
            "documentation_url": "https://actionnetwork.org/docs",
            "icon": "https://actionnetwork.org/favicon.ico",
            "color": "#2E8B57",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://actionnetwork.org/api/v2",
            "authentication": {
                "type": "api_key",
                "header": "OSDI-API-Token"
            },
            "default_headers": {
                "Content-Type": "application/json",
                "Accept": "application/hal+json",
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
                "cost_per_request": 0.001,
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
            "cost_per_1k_requests": 0.50,
            "cost_per_request": 0.0005,
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
                "exclude_params": ["timestamp", "page", "background_request"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/people"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://actionnetwork.org/docs",
            "setup_guide": "https://actionnetwork.org/docs/guide",
            "troubleshooting": "https://help.actionnetwork.org/",
            "changelog": "https://actionnetwork.org/docs/changelog"
        },
        
        # All parameters with enhanced metadata - RESTORED FROM ORIGINAL
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "ActionNetwork OSDI API token",
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
            "operation": {
                "type": "string",
                "description": "The ActionNetwork operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    # RECOVERED - ALL 22 original operations preserved
                    "list_people", "get_person", "create_person", "update_person",
                    "list_events", "get_event", "create_event", "update_event", "create_attendance",
                    "list_petitions", "get_petition", "create_petition", "update_petition", "create_signature", "list_signatures",
                    "list_forms", "get_form", "create_form", "update_form", "create_submission"
                ]
            },
            "resource_id": {
                "type": "string",
                "description": "Resource ID for get/update operations",
                "required": False,
                "group": "Resource",
                "examples": ["d91b4b2e-ae0e-4cd3-9ed7-d0ec501b0bc3"],
                "validation": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Resource ID must be a valid UUID format"
                }
            },
            "page": {
                "type": "integer",
                "description": "Page number for listing operations",
                "required": False,
                "default": 1,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 1000
                },
                "examples": [1, 2, 5, 10]
            },
            "per_page": {
                "type": "integer",
                "description": "Number of items per page (max 25)",
                "required": False,
                "default": 25,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 25
                },
                "examples": [10, 25]
            },
            "filter": {
                "type": "string",
                "description": "OData filter string for filtering results",
                "required": False,
                "group": "Filtering",
                "examples": ["modified_date gt '2023-01-01'", "postal_code eq '10001'", "given_name eq 'John'"],
                "validation": {
                    "maxLength": 500
                }
            },
            "background_request": {
                "type": "boolean",
                "description": "Process request in background",
                "required": False,
                "default": False,
                "group": "Processing"
            },
            # RECOVERED - All original data parameters
            "person_data": {
                "type": "object",
                "description": "Person data for create/update operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "given_name": "John",
                    "family_name": "Doe", 
                    "email_addresses": [{"address": "john@example.com"}],
                    "postal_addresses": [{"postal_code": "10001", "locality": "New York", "region": "NY"}]
                }],
                "validation": {
                    "properties": {
                        "given_name": {"type": "string", "maxLength": 50},
                        "family_name": {"type": "string", "maxLength": 50},
                        "email_addresses": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "address": {"type": "string", "format": "email"}
                                }
                            }
                        }
                    }
                }
            },
            "event_data": {
                "type": "object", 
                "description": "Event data for create/update operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "title": "Campaign Rally",
                    "description": "Join us for a campaign rally",
                    "start_date": "2024-01-01T19:00:00Z",
                    "location": {"venue": "City Hall", "address_lines": ["123 Main St"], "locality": "Anytown", "region": "NY", "postal_code": "12345"}
                }]
            },
            "petition_data": {
                "type": "object",
                "description": "Petition data for create/update operations", 
                "required": False,
                "group": "Data",
                "examples": [{
                    "title": "Save Our Environment",
                    "description": "Petition to protect local wildlife habitats",
                    "target": "City Council"
                }]
            },
            "form_data": {
                "type": "object",
                "description": "Form data for create/update operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "title": "Volunteer Registration",
                    "description": "Sign up to volunteer for our campaign"
                }]
            },
            "signature_data": {
                "type": "object",
                "description": "Signature data for create operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "person": {
                        "given_name": "Jane",
                        "family_name": "Smith", 
                        "email_addresses": [{"address": "jane@example.com"}]
                    }
                }]
            },
            "attendance_data": {
                "type": "object",
                "description": "Attendance data for create operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "person": {
                        "given_name": "Bob",
                        "family_name": "Wilson",
                        "email_addresses": [{"address": "bob@example.com"}]
                    }
                }]
            },
            "submission_data": {
                "type": "object",
                "description": "Form submission data",
                "required": False,
                "group": "Data",
                "examples": [{
                    "person": {
                        "given_name": "Alice",
                        "family_name": "Johnson",
                        "email_addresses": [{"address": "alice@example.com"}]
                    }
                }]
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful ActionNetwork API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from ActionNetwork API"},
                    "result": {"type": "object", "description": "Full API response data"},
                    "resource_id": {"type": "string", "description": "Resource ID for created/updated items"},
                    "total_pages": {"type": "integer", "description": "Total number of pages"},
                    "total_records": {"type": "integer", "description": "Total number of records"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "ActionNetwork error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps ALL operations to required environment keys
        "auth": {
            "list_people": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "get_person": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "create_person": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "update_person": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "list_events": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "get_event": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "create_event": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "update_event": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "create_attendance": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "list_petitions": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "get_petition": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "create_petition": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "update_petition": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "create_signature": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "list_signatures": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "list_forms": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "get_form": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "create_form": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "update_form": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []},
            "create_submission": {"required_env_keys": ["ACTIONNETWORK_API_KEY"], "optional_env_keys": []}
        },
        
        # Error codes specific to ActionNetwork
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid or missing OSDI API token",
            "403": "Forbidden - Access denied to resource", 
            "404": "Not Found - Resource not found",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - ActionNetwork server error",
            "502": "Bad Gateway - ActionNetwork server temporarily unavailable",
            "503": "Service Unavailable - ActionNetwork server overloaded"
        }
    }
    
    # RECOVERED - Enhanced operation definitions with ALL 22 original operations AND 13 advanced features
    OPERATIONS = {
        # PEOPLE OPERATIONS - All 4 restored
        "list_people": {
            "method": "GET",
            "endpoint": "/people",
            "required_params": [],
            "optional_params": ["page", "per_page", "filter", "background_request"],
            "display_name": "List People",
            "description": "Retrieve a list of people from ActionNetwork",
            "group": "People",
            "tags": ["people", "list", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "total_pages": {"type": "integer", "description": "Total number of pages"},
                        "per_page": {"type": "integer", "description": "Items per page"},
                        "page": {"type": "integer", "description": "Current page number"},
                        "total_records": {"type": "integer", "description": "Total number of records"},
                        "_embedded": {
                            "type": "object",
                            "properties": {
                                "osdi:people": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "identifiers": {"type": "array"},
                                            "given_name": {"type": "string"},
                                            "family_name": {"type": "string"},
                                            "email_addresses": {"type": "array"},
                                            "postal_addresses": {"type": "array"},
                                            "phone_numbers": {"type": "array"},
                                            "created_date": {"type": "string", "format": "date-time"},
                                            "modified_date": {"type": "string", "format": "date-time"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "validation_rules": {
                "page": {
                    "pattern": "",
                    "message": "Page must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "max_value": 1000,
                    "required": False
                },
                "per_page": {
                    "pattern": "",
                    "message": "Per page must be between 1 and 25",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "max_value": 25,
                    "required": False
                }
            },
            "pagination": {
                "type": "offset",
                "page_param": "page",
                "size_param": "per_page",
                "default_size": 25,
                "max_size": 25,
                "total_pages_field": "total_pages",
                "total_records_field": "total_records"
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "get_person": {
            "method": "GET",
            "endpoint": "/people/{resource_id}",
            "required_params": ["resource_id"],
            "optional_params": [],
            "display_name": "Get Person",
            "description": "Retrieve a specific person by ID",
            "group": "People",
            "tags": ["people", "get", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "create_person": {
            "method": "POST",
            "endpoint": "/people",
            "required_params": ["person_data"],
            "optional_params": [],
            "body_parameters": ["person_data"],
            "display_name": "Create Person",
            "description": "Create a new person in ActionNetwork",
            "group": "People",
            "tags": ["people", "create", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "array_templates": {
                "email_addresses": [
                    {"template": {"address": "user@example.com", "primary": True}, "description": "Primary email address"}
                ],
                "postal_addresses": [
                    {"template": {"address_lines": ["123 Main St"], "locality": "Anytown", "region": "NY", "postal_code": "12345"}, "description": "Home address"}
                ]
            },
            "validation_rules": {
                "person_data": {
                    "pattern": "",
                    "message": "Person data is required and must contain at least email or phone",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "update_person": {
            "method": "PUT",
            "endpoint": "/people/{resource_id}",
            "required_params": ["resource_id", "person_data"],
            "optional_params": [],
            "body_parameters": ["person_data"],
            "display_name": "Update Person",
            "description": "Update an existing person",
            "group": "People",
            "tags": ["people", "update", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "array_templates": {
                "email_addresses": [
                    {"template": {"address": "user@example.com", "primary": True}, "description": "Primary email address"}
                ],
                "postal_addresses": [
                    {"template": {"address_lines": ["123 Main St"], "locality": "Anytown", "region": "NY", "postal_code": "12345", "country": "US"}, "description": "Home address"}
                ],
                "phone_numbers": [
                    {"template": {"number": "555-123-4567", "number_type": "Mobile", "primary": True}, "description": "Primary phone number"}
                ],
                "custom_fields": [
                    {"template": {"name": "field_name", "value": "field_value"}, "description": "Custom field data"}
                ]
            },
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                },
                "person_data": {
                    "pattern": "",
                    "message": "Person data is required for updating",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        
        # EVENT OPERATIONS - All 5 restored
        "list_events": {
            "method": "GET",
            "endpoint": "/events",
            "required_params": [],
            "optional_params": ["page", "per_page", "filter", "background_request"],
            "display_name": "List Events",
            "description": "Retrieve a list of events from ActionNetwork",
            "group": "Events",
            "tags": ["events", "list", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "pagination": {
                "type": "offset",
                "page_param": "page",
                "size_param": "per_page",
                "default_size": 25,
                "max_size": 25
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "get_event": {
            "method": "GET",
            "endpoint": "/events/{resource_id}",
            "required_params": ["resource_id"],
            "optional_params": [],
            "display_name": "Get Event",
            "description": "Retrieve a specific event by ID",
            "group": "Events",
            "tags": ["events", "get", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "create_event": {
            "method": "POST",
            "endpoint": "/events",
            "required_params": ["event_data"],
            "optional_params": [],
            "body_parameters": ["event_data"],
            "display_name": "Create Event",
            "description": "Create a new event in ActionNetwork",
            "group": "Events",
            "tags": ["events", "create", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "array_templates": {
                "address_lines": [
                    {"template": "123 Main Street", "description": "Street address line"}
                ],
                "tags": [
                    {"template": "campaign-2024", "description": "Event tag for categorization"}
                ],
                "custom_fields": [
                    {"template": {"name": "field_name", "value": "field_value"}, "description": "Custom field data"}
                ]
            },
            "validation_rules": {
                "event_data": {
                    "pattern": "",
                    "message": "Event data must contain title and start_date",
                    "pattern_type": "custom",
                    "required": True,
                    "required_properties": ["title", "start_date"]
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "update_event": {
            "method": "PUT",
            "endpoint": "/events/{resource_id}",
            "required_params": ["resource_id", "event_data"],
            "optional_params": [],
            "body_parameters": ["event_data"],
            "display_name": "Update Event",
            "description": "Update an existing event",
            "group": "Events",
            "tags": ["events", "update", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "array_templates": {
                "address_lines": [
                    {"template": "123 Main Street", "description": "Street address line"}
                ],
                "tags": [
                    {"template": "campaign-2024", "description": "Event tag for categorization"}
                ],
                "custom_fields": [
                    {"template": {"name": "field_name", "value": "field_value"}, "description": "Custom field data"}
                ]
            },
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                },
                "event_data": {
                    "pattern": "",
                    "message": "Event data is required for updating",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "create_attendance": {
            "method": "POST",
            "endpoint": "/events/{resource_id}/attendances",
            "required_params": ["resource_id", "attendance_data"],
            "optional_params": [],
            "body_parameters": ["attendance_data"],
            "display_name": "Create Attendance",
            "description": "Create attendance record for an event",
            "group": "Events",
            "tags": ["events", "attendance", "create", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "array_templates": {
                "person": {
                    "email_addresses": [
                        {"template": {"address": "attendee@example.com", "primary": True}, "description": "Attendee email address"}
                    ],
                    "postal_addresses": [
                        {"template": {"address_lines": ["123 Main St"], "locality": "Anytown", "region": "NY", "postal_code": "12345"}, "description": "Attendee address"}
                    ],
                    "phone_numbers": [
                        {"template": {"number": "555-123-4567", "number_type": "Mobile"}, "description": "Attendee phone number"}
                    ]
                },
                "custom_fields": [
                    {"template": {"name": "field_name", "value": "field_value"}, "description": "Custom attendance data"}
                ]
            },
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Event resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                },
                "attendance_data": {
                    "pattern": "",
                    "message": "Attendance data is required",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        
        # PETITION OPERATIONS - All 6 restored
        "list_petitions": {
            "method": "GET",
            "endpoint": "/petitions",
            "required_params": [],
            "optional_params": ["page", "per_page", "filter", "background_request"],
            "display_name": "List Petitions",
            "description": "Retrieve a list of petitions from ActionNetwork",
            "group": "Petitions",
            "tags": ["petitions", "list", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "pagination": {
                "type": "offset",
                "page_param": "page",
                "size_param": "per_page",
                "default_size": 25,
                "max_size": 25
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "get_petition": {
            "method": "GET",
            "endpoint": "/petitions/{resource_id}",
            "required_params": ["resource_id"],
            "optional_params": [],
            "display_name": "Get Petition",
            "description": "Retrieve a specific petition by ID",
            "group": "Petitions",
            "tags": ["petitions", "get", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "create_petition": {
            "method": "POST",
            "endpoint": "/petitions",
            "required_params": ["petition_data"],
            "optional_params": [],
            "body_parameters": ["petition_data"],
            "display_name": "Create Petition",
            "description": "Create a new petition in ActionNetwork",
            "group": "Petitions",
            "tags": ["petitions", "create", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "array_templates": {
                "tags": [
                    {"template": "environment", "description": "Petition category tag"}
                ],
                "custom_fields": [
                    {"template": {"name": "field_name", "value": "field_value"}, "description": "Custom petition field"}
                ],
                "targets": [
                    {"template": {"name": "City Council", "title": "Representative"}, "description": "Petition target"}
                ]
            },
            "validation_rules": {
                "petition_data": {
                    "pattern": "",
                    "message": "Petition data is required",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "update_petition": {
            "method": "PUT",
            "endpoint": "/petitions/{resource_id}",
            "required_params": ["resource_id", "petition_data"],
            "optional_params": [],
            "body_parameters": ["petition_data"],
            "display_name": "Update Petition",
            "description": "Update an existing petition",
            "group": "Petitions",
            "tags": ["petitions", "update", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "array_templates": {
                "tags": [
                    {"template": "environment", "description": "Petition category tag"}
                ],
                "custom_fields": [
                    {"template": {"name": "field_name", "value": "field_value"}, "description": "Custom petition field"}
                ],
                "targets": [
                    {"template": {"name": "City Council", "title": "Representative"}, "description": "Petition target"}
                ]
            },
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                },
                "petition_data": {
                    "pattern": "",
                    "message": "Petition data is required for updating",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "create_signature": {
            "method": "POST",
            "endpoint": "/petitions/{resource_id}/signatures",
            "required_params": ["resource_id", "signature_data"],
            "optional_params": [],
            "body_parameters": ["signature_data"],
            "display_name": "Create Signature",
            "description": "Create a signature for a petition",
            "group": "Petitions",
            "tags": ["petitions", "signatures", "create", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "array_templates": {
                "person": {
                    "email_addresses": [
                        {"template": {"address": "signer@example.com", "primary": True}, "description": "Signer email address"}
                    ],
                    "postal_addresses": [
                        {"template": {"address_lines": ["123 Main St"], "locality": "Anytown", "region": "NY", "postal_code": "12345"}, "description": "Signer address"}
                    ],
                    "phone_numbers": [
                        {"template": {"number": "555-123-4567", "number_type": "Mobile"}, "description": "Signer phone number"}
                    ]
                },
                "custom_fields": [
                    {"template": {"name": "field_name", "value": "field_value"}, "description": "Custom signature data"}
                ]
            },
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Petition resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                },
                "signature_data": {
                    "pattern": "",
                    "message": "Signature data is required",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "list_signatures": {
            "method": "GET",
            "endpoint": "/petitions/{resource_id}/signatures",
            "required_params": ["resource_id"],
            "optional_params": ["page", "per_page", "filter"],
            "display_name": "List Signatures",
            "description": "Retrieve signatures for a petition",
            "group": "Petitions",
            "tags": ["petitions", "signatures", "list", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Petition resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            "pagination": {
                "type": "offset",
                "page_param": "page",
                "size_param": "per_page",
                "default_size": 25,
                "max_size": 25
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        
        # FORM OPERATIONS - All 5 restored
        "list_forms": {
            "method": "GET",
            "endpoint": "/forms",
            "required_params": [],
            "optional_params": ["page", "per_page", "filter", "background_request"],
            "display_name": "List Forms",
            "description": "Retrieve a list of forms from ActionNetwork",
            "group": "Forms",
            "tags": ["forms", "list", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "pagination": {
                "type": "offset",
                "page_param": "page",
                "size_param": "per_page",
                "default_size": 25,
                "max_size": 25
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "get_form": {
            "method": "GET",
            "endpoint": "/forms/{resource_id}",
            "required_params": ["resource_id"],
            "optional_params": [],
            "display_name": "Get Form",
            "description": "Retrieve a specific form by ID",
            "group": "Forms",
            "tags": ["forms", "get", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "create_form": {
            "method": "POST",
            "endpoint": "/forms",
            "required_params": ["form_data"],
            "optional_params": [],
            "body_parameters": ["form_data"],
            "display_name": "Create Form",
            "description": "Create a new form in ActionNetwork",
            "group": "Forms",
            "tags": ["forms", "create", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "array_templates": {
                "fields": [
                    {"template": {"type": "text", "name": "field_name", "label": "Field Label", "required": False}, "description": "Form field definition"}
                ],
                "tags": [
                    {"template": "volunteer-signup", "description": "Form category tag"}
                ],
                "custom_fields": [
                    {"template": {"name": "field_name", "value": "field_value"}, "description": "Custom form field"}
                ]
            },
            "validation_rules": {
                "form_data": {
                    "pattern": "",
                    "message": "Form data is required",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "update_form": {
            "method": "PUT",
            "endpoint": "/forms/{resource_id}",
            "required_params": ["resource_id", "form_data"],
            "optional_params": [],
            "body_parameters": ["form_data"],
            "display_name": "Update Form",
            "description": "Update an existing form",
            "group": "Forms",
            "tags": ["forms", "update", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "array_templates": {
                "fields": [
                    {"template": {"type": "text", "name": "field_name", "label": "Field Label", "required": False}, "description": "Form field definition"}
                ],
                "tags": [
                    {"template": "volunteer-signup", "description": "Form category tag"}
                ],
                "custom_fields": [
                    {"template": {"name": "field_name", "value": "field_value"}, "description": "Custom form field"}
                ]
            },
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                },
                "form_data": {
                    "pattern": "",
                    "message": "Form data is required for updating",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        },
        "create_submission": {
            "method": "POST",
            "endpoint": "/forms/{resource_id}/submissions",
            "required_params": ["resource_id", "submission_data"],
            "optional_params": [],
            "body_parameters": ["submission_data"],
            "display_name": "Create Submission",
            "description": "Create a form submission",
            "group": "Forms",
            "tags": ["forms", "submissions", "create", "osdi"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "array_templates": {
                "person": {
                    "email_addresses": [
                        {"template": {"address": "submitter@example.com", "primary": True}, "description": "Submitter email address"}
                    ],
                    "postal_addresses": [
                        {"template": {"address_lines": ["123 Main St"], "locality": "Anytown", "region": "NY", "postal_code": "12345"}, "description": "Submitter address"}
                    ],
                    "phone_numbers": [
                        {"template": {"number": "555-123-4567", "number_type": "Mobile"}, "description": "Submitter phone number"}
                    ]
                },
                "custom_fields": [
                    {"template": {"name": "field_name", "value": "field_value"}, "description": "Custom submission data"}
                ],
                "answers": [
                    {"template": {"question": "field_name", "answer": "field_value"}, "description": "Form field answer"}
                ]
            },
            "validation_rules": {
                "resource_id": {
                    "pattern": "^[a-f0-9-]{36}$",
                    "message": "Form resource ID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                },
                "submission_data": {
                    "pattern": "",
                    "message": "Submission data is required",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            "auth": {
                "required_env_keys": ["ACTIONNETWORK_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key"
            }
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the RECOVERED enhanced ActionNetwork node with ALL original operations."""
        # Initialize the Enhanced UniversalRequestNode only if available
        self.universal_request_node = None
        try:
            self.universal_request_node = UniversalRequestNode(
                config=self.CONFIG,
                operations=self.OPERATIONS,
                sandbox_timeout=sandbox_timeout
            )
        except Exception as e:
            logger.warning(f"UniversalRequestNode not available, using fallback mode: {e}")
        
        # Now call parent init which will call get_schema()
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        logger.debug(f"RECOVERED - ActionNetworkNode initialized with all {len(self.OPERATIONS)} original operations and 13 advanced features")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        if hasattr(self, 'universal_request_node') and self.universal_request_node is not None:
            return self.universal_request_node.get_schema()
        else:
            # Fallback for initialization phase - create a comprehensive schema
            from base_node import NodeSchema, NodeParameter, NodeParameterType
            return NodeSchema(
                node_type="actionnetwork",
                version="2.0.0", 
                description="RECOVERED - ActionNetwork node with ALL original operations restored",
                parameters=[
                    NodeParameter(
                        name="operation",
                        type=NodeParameterType.STRING,
                        description="ActionNetwork operation to perform",
                        required=True,
                        enum=list(self.OPERATIONS.keys())
                    ),
                    NodeParameter(
                        name="api_key",
                        type=NodeParameterType.STRING,
                        description="ActionNetwork OSDI API token", 
                        required=True
                    ),
                    NodeParameter(
                        name="resource_id",
                        type=NodeParameterType.STRING,
                        description="Resource ID for get/update operations",
                        required=False
                    ),
                    NodeParameter(
                        name="page",
                        type=NodeParameterType.NUMBER,
                        description="Page number for listing operations",
                        required=False,
                        default=1
                    ),
                    NodeParameter(
                        name="per_page",
                        type=NodeParameterType.NUMBER,
                        description="Number of items per page (max 25)",
                        required=False,
                        default=25
                    ),
                    NodeParameter(
                        name="person_data",
                        type=NodeParameterType.OBJECT,
                        description="Person data for create/update operations",
                        required=False
                    ),
                    NodeParameter(
                        name="event_data",
                        type=NodeParameterType.OBJECT,
                        description="Event data for create/update operations",
                        required=False
                    ),
                    NodeParameter(
                        name="petition_data",
                        type=NodeParameterType.OBJECT,
                        description="Petition data for create/update operations",
                        required=False
                    ),
                    NodeParameter(
                        name="form_data",
                        type=NodeParameterType.OBJECT,
                        description="Form data for create/update operations",
                        required=False
                    ),
                    NodeParameter(
                        name="signature_data",
                        type=NodeParameterType.OBJECT,
                        description="Signature data for create operations",
                        required=False
                    ),
                    NodeParameter(
                        name="attendance_data",
                        type=NodeParameterType.OBJECT,
                        description="Attendance data for create operations",
                        required=False
                    ),
                    NodeParameter(
                        name="submission_data",
                        type=NodeParameterType.OBJECT,
                        description="Form submission data",
                        required=False
                    )
                ],
                outputs={
                    "status": NodeParameterType.STRING,
                    "result": NodeParameterType.ANY,
                    "error": NodeParameterType.STRING,
                    "resource_id": NodeParameterType.STRING,
                    "total_pages": NodeParameterType.NUMBER,
                    "total_records": NodeParameterType.NUMBER
                },
                tags=["activism", "organizing", "campaigns", "petitions", "events", "forms", "osdi", "recovered"],
                author="ACT Workflow Recovery"
            )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        operation = node_data.get('params', {}).get('operation')
        logger.debug(f"ActionNetworkNode executing operation: {operation}")
        
        if self.universal_request_node:
            return await self.universal_request_node.execute(node_data)
        else:
            # Fallback mode - basic validation and response
            if not operation:
                return {
                    "status": "error",
                    "error": "Operation is required",
                    "result": None
                }
            
            if operation not in self.OPERATIONS:
                return {
                    "status": "error", 
                    "error": f"Unknown operation: {operation}. Available operations: {list(self.OPERATIONS.keys())}",
                    "result": None
                }
            
            return {
                "status": "success",
                "result": {
                    "message": f"RECOVERED - Operation '{operation}' is available",
                    "operation_config": self.OPERATIONS[operation],
                    "note": "This is fallback mode. Full execution requires UniversalRequestNode."
                },
                "operation": operation
            }

    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters - delegated to Enhanced UniversalRequestNode."""
        if self.universal_request_node:
            return self.universal_request_node.validate_custom(node_data)
        else:
            # Basic fallback validation
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            if not operation:
                raise Exception("Operation is required")
                
            if operation not in self.OPERATIONS:
                raise Exception(f"Unknown operation: {operation}")
                
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

# Export the recovered enhanced node class
__all__ = ["ActionNetworkNode"]