#!/usr/bin/env python3
"""
AcuityScheduling Node - Enhanced with ALL 13 advanced features following OpenAI template
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

class AcuitySchedulingNode(BaseNode):
    """
    Enhanced AcuityScheduling node with ALL 13 advanced features - following perfect OpenAI template.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "acuityscheduling",
            "display_name": "AcuityScheduling",
            "description": "Comprehensive AcuityScheduling API integration for appointment scheduling, client management, availability tracking, and booking workflows",
            "category": "scheduling",
            "vendor": "acuityscheduling",
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["scheduling", "appointments", "booking", "calendar", "clients", "availability"],
            "documentation_url": "https://developers.acuityscheduling.com/docs",
            "icon": "https://acuityscheduling.com/favicon.ico",
            "color": "#00A4DB",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://acuityscheduling.com/api/v1",
            "authentication": {
                "type": "basic_auth",
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
            "cost_per_1k_requests": 2.00,
            "cost_per_request": 0.002,
            "billing_unit": "requests",
            "free_tier_limit": 250
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
                "exclude_params": ["timestamp", "minDate", "maxDate"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_user_id",
            "validation_endpoint": "/appointments"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://developers.acuityscheduling.com/reference",
            "setup_guide": "https://developers.acuityscheduling.com/docs",
            "troubleshooting": "https://help.acuityscheduling.com/hc/en-us",
            "changelog": "https://developers.acuityscheduling.com/changelog"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "user_id": {
                "type": "string",
                "description": "AcuityScheduling User ID (for basic auth)",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[0-9]+$",
                    "message": "User ID must be numeric",
                    "minLength": 1,
                    "maxLength": 20
                }
            },
            "api_key": {
                "type": "string",
                "description": "AcuityScheduling API Key (for basic auth)",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-zA-Z0-9]+$",
                    "message": "API key must be alphanumeric",
                    "minLength": 10,
                    "maxLength": 100
                }
            },
            "operation": {
                "type": "string",
                "description": "The AcuityScheduling operation to perform",
                "required": True,
                "group": "Operation",
                "enum": ["list_appointments", "get_appointment", "create_appointment", "update_appointment", "delete_appointment", "cancel_appointment", "list_clients", "get_client", "create_client", "update_client", "get_availability", "get_times", "list_calendars", "get_calendar", "list_appointment_types", "get_appointment_type", "list_blocks", "create_block", "delete_block", "list_certificates", "list_forms", "list_products", "list_orders"]
            },
            "appointment_id": {
                "type": "integer",
                "description": "Appointment ID for specific appointment operations",
                "required": False,
                "group": "Resource",
                "examples": [123, 456, 789],
                "validation": {
                    "minimum": 1
                }
            },
            "client_id": {
                "type": "integer", 
                "description": "Client ID for specific client operations",
                "required": False,
                "group": "Resource",
                "examples": [1, 25, 100],
                "validation": {
                    "minimum": 1
                }
            },
            "appointment_type_id": {
                "type": "integer",
                "description": "Appointment type ID for scheduling operations",
                "required": False,
                "group": "Resource",
                "examples": [1, 5, 15],
                "validation": {
                    "minimum": 1
                }
            },
            "appointmentTypeID": {
                "type": "integer",
                "description": "Appointment type ID (AcuityScheduling parameter name)",
                "required": False,
                "group": "Resource",
                "examples": [1, 5, 15],
                "validation": {
                    "minimum": 1
                }
            },
            "calendar_id": {
                "type": "integer",
                "description": "Calendar ID for availability and scheduling",
                "required": False,
                "group": "Resource",
                "examples": [1, 2, 10],
                "validation": {
                    "minimum": 1
                }
            },
            "block_id": {
                "type": "integer",
                "description": "Block ID for time block operations",
                "required": False,
                "group": "Resource",
                "examples": [1, 50, 200],
                "validation": {
                    "minimum": 1
                }
            },
            "minDate": {
                "type": "string",
                "description": "Minimum date filter (YYYY-MM-DD format)",
                "required": False,
                "group": "Filtering",
                "examples": ["2024-01-01", "2024-06-15"],
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "message": "Date must be in YYYY-MM-DD format"
                }
            },
            "maxDate": {
                "type": "string",
                "description": "Maximum date filter (YYYY-MM-DD format)",
                "required": False,
                "group": "Filtering",
                "examples": ["2024-12-31", "2024-06-30"],
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "message": "Date must be in YYYY-MM-DD format"
                }
            },
            "calendarID": {
                "type": "integer",
                "description": "Calendar ID filter for appointments and availability",
                "required": False,
                "group": "Filtering",
                "examples": [1, 2, 5],
                "validation": {
                    "minimum": 1
                }
            },
            "appointmentTypeID": {
                "type": "integer",
                "description": "Appointment type ID filter",
                "required": False,
                "group": "Filtering",
                "examples": [1, 3, 8],
                "validation": {
                    "minimum": 1
                }
            },
            "appointment_data": {
                "type": "object",
                "description": "Appointment data for create/update operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "appointmentTypeID": 1,
                    "datetime": "2024-01-15T14:00:00",
                    "firstName": "John",
                    "lastName": "Doe", 
                    "email": "john@example.com",
                    "phone": "555-123-4567",
                    "notes": "First appointment",
                    "fields": [{"id": 1, "value": "Consultation"}]
                }],
                "validation": {
                    "properties": {
                        "appointmentTypeID": {"type": "integer", "minimum": 1},
                        "datetime": {"type": "string", "format": "date-time"},
                        "firstName": {"type": "string", "maxLength": 50},
                        "lastName": {"type": "string", "maxLength": 50},
                        "email": {"type": "string", "format": "email"},
                        "phone": {"type": "string", "maxLength": 20}
                    }
                }
            },
            "client_data": {
                "type": "object",
                "description": "Client data for create/update operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "firstName": "Jane",
                    "lastName": "Smith",
                    "email": "jane@example.com",
                    "phone": "555-987-6543"
                }],
                "validation": {
                    "properties": {
                        "firstName": {"type": "string", "maxLength": 50},
                        "lastName": {"type": "string", "maxLength": 50},
                        "email": {"type": "string", "format": "email"},
                        "phone": {"type": "string", "maxLength": 20}
                    }
                }
            },
            "block_data": {
                "type": "object",
                "description": "Time block data for create operations",
                "required": False,
                "group": "Data",
                "examples": [{
                    "start": "2024-01-15T09:00:00",
                    "end": "2024-01-15T17:00:00",
                    "calendarID": 1,
                    "notes": "Blocked for training"
                }]
            },
            "date": {
                "type": "string",
                "description": "Date for availability checks (YYYY-MM-DD format)",
                "required": False,
                "group": "Scheduling",
                "examples": ["2024-01-15", "2024-03-20"],
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "message": "Date must be in YYYY-MM-DD format"
                }
            },
            "month": {
                "type": "string",
                "description": "Month for availability checks (YYYY-MM format)",
                "required": False,
                "group": "Scheduling",
                "examples": ["2024-01", "2024-06"],
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}$",
                    "message": "Month must be in YYYY-MM format"
                }
            },
            "cancel_note": {
                "type": "string",
                "description": "Note for appointment cancellation",
                "required": False,
                "group": "Data",
                "examples": ["Client requested cancellation", "Emergency cancellation"],
                "validation": {
                    "maxLength": 500,
                    "message": "Cancellation note cannot exceed 500 characters"
                }
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "required": False,
                "group": "Pagination",
                "examples": [10, 25, 50],
                "validation": {
                    "minimum": 1,
                    "maximum": 100,
                    "message": "Limit must be between 1 and 100"
                }
            },
            "offset": {
                "type": "integer",
                "description": "Number of results to skip for pagination",
                "required": False,
                "group": "Pagination",
                "examples": [0, 10, 50],
                "validation": {
                    "minimum": 0,
                    "message": "Offset must be 0 or greater"
                }
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful AcuityScheduling API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from AcuityScheduling API"},
                    "result": {"type": "object", "description": "Full API response data"},
                    "resource_id": {"type": "integer", "description": "Resource ID for created/updated items"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "AcuityScheduling error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "list_appointments": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "get_appointment": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "create_appointment": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "update_appointment": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "cancel_appointment": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "list_clients": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "get_client": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "create_client": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "update_client": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "list_appointment_types": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "get_appointment_type": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "get_availability": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "get_times": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "list_calendars": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "get_calendar": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "list_blocks": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "create_block": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "delete_block": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "delete_appointment": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "list_certificates": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "list_forms": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "list_products": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            },
            "list_orders": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": []
            }
        },
        
        # Error codes specific to AcuityScheduling
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid credentials or authentication failure",
            "403": "Forbidden - Access denied to resource",
            "404": "Not Found - Resource not found",
            "422": "Unprocessable Entity - Validation errors in request data",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - AcuityScheduling server error",
            "502": "Bad Gateway - AcuityScheduling server temporarily unavailable",
            "503": "Service Unavailable - AcuityScheduling server overloaded"
        }
    }
    
    # Enhanced operation definitions with ALL 13 features
    OPERATIONS = {
        "list_appointments": {
            "method": "GET",
            "endpoint": "/appointments",
            "required_params": [],
            "optional_params": ["minDate", "maxDate", "calendarID", "appointmentTypeID"],
            "display_name": "List Appointments",
            "description": "Retrieve a list of appointments from AcuityScheduling",
            "group": "Appointments",
            "tags": ["appointments", "list", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            # 2. Array templates for filtering by multiple IDs and statuses
            "array_templates": {
                "calendarIDs": [
                    {"template": 1, "description": "Primary calendar ID"},
                    {"template": 2, "description": "Secondary calendar ID"},
                    {"template": 3, "description": "Additional calendar ID"}
                ],
                "appointmentTypeIDs": [
                    {"template": 1, "description": "Consultation appointment type"},
                    {"template": 2, "description": "Treatment appointment type"},
                    {"template": 3, "description": "Follow-up appointment type"}
                ],
                "statuses": [
                    {"template": "scheduled", "description": "Scheduled appointments"},
                    {"template": "confirmed", "description": "Confirmed appointments"},
                    {"template": "cancelled", "description": "Cancelled appointments"}
                ]
            },
            
            # 1. Operation-specific output schema
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Appointment ID"},
                            "firstName": {"type": "string"},
                            "lastName": {"type": "string"},
                            "phone": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "date": {"type": "string", "format": "date"},
                            "time": {"type": "string", "format": "time"},
                            "endTime": {"type": "string", "format": "time"},
                            "datetime": {"type": "string", "format": "date-time"},
                            "endDateTime": {"type": "string", "format": "date-time"},
                            "price": {"type": "string"},
                            "priceSold": {"type": "string"},
                            "paid": {"type": "string"},
                            "amountPaid": {"type": "string"},
                            "type": {"type": "string"},
                            "appointmentTypeID": {"type": "integer"},
                            "classID": {"type": "integer"},
                            "addonIDs": {"type": "array"},
                            "category": {"type": "string"},
                            "duration": {"type": "string"},
                            "calendar": {"type": "string"},
                            "calendarID": {"type": "integer"},
                            "certificate": {"type": "string"},
                            "confirmationPage": {"type": "string"},
                            "location": {"type": "string"},
                            "notes": {"type": "string"},
                            "timezone": {"type": "string"},
                            "calendarTimezone": {"type": "string"},
                            "canceled": {"type": "boolean"},
                            "canClientCancel": {"type": "boolean"},
                            "canClientReschedule": {"type": "boolean"}
                        }
                    }
                },
                "error": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"},
                                "error_code": {"type": "string"}
                            }
                        }
                    }
                },
                "status_codes": {
                    200: "Success",
                    400: "Bad Request - Invalid parameters",
                    401: "Invalid authentication",
                    429: "Rate limit exceeded",
                    500: "Server error"
                }
            },
            
            # 4. Advanced validation rules
            "validation_rules": {
                "minDate": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "message": "minDate must be in YYYY-MM-DD format",
                    "pattern_type": "regex",
                    "required": False
                },
                "maxDate": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "message": "maxDate must be in YYYY-MM-DD format",
                    "pattern_type": "regex",
                    "required": False
                },
                "calendarID": {
                    "pattern": "",
                    "message": "Calendar ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": False
                }
            },
            
            # 8. Field mapping & transformation
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {
                    "datetime": "format_timestamp",
                    "endDateTime": "format_timestamp"
                },
                "field_aliases": {
                    "first_name": "firstName",
                    "last_name": "lastName",
                    "appointment_type_id": "appointmentTypeID",
                    "calendar_id": "calendarID"
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "List all appointments",
                    "description": "Get all appointments without date filtering",
                    "input": {}
                },
                {
                    "name": "List appointments for date range",
                    "description": "Get appointments within a specific date range",
                    "input": {
                        "minDate": "2024-01-01",
                        "maxDate": "2024-01-31"
                    }
                },
                {
                    "name": "List appointments for specific calendar",
                    "description": "Get appointments for a specific calendar",
                    "input": {
                        "calendarID": 1,
                        "minDate": "2024-01-01"
                    }
                }
            ]
        },
        "get_appointment": {
            "method": "GET",
            "endpoint": "/appointments/{appointment_id}",
            "required_params": ["appointment_id"],
            "optional_params": [],
            "display_name": "Get Appointment",
            "description": "Retrieve a specific appointment by ID",
            "group": "Appointments",
            "tags": ["appointments", "get", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Appointment ID"},
                        "firstName": {"type": "string"},
                        "lastName": {"type": "string"},
                        "phone": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "datetime": {"type": "string", "format": "date-time"},
                        "endDateTime": {"type": "string", "format": "date-time"},
                        "price": {"type": "string"},
                        "type": {"type": "string"},
                        "appointmentTypeID": {"type": "integer"},
                        "calendar": {"type": "string"},
                        "calendarID": {"type": "integer"},
                        "location": {"type": "string"},
                        "notes": {"type": "string"},
                        "canceled": {"type": "boolean"}
                    }
                }
            },
            
            "validation_rules": {
                "appointment_id": {
                    "pattern": "",
                    "message": "Appointment ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Get appointment by ID",
                    "description": "Retrieve a specific appointment using its ID",
                    "input": {
                        "appointment_id": 123
                    }
                }
            ]
        },
        "create_appointment": {
            "method": "POST",
            "endpoint": "/appointments",
            "required_params": ["appointment_data"],
            "optional_params": [],
            "body_parameters": ["appointment_data"],
            "display_name": "Create Appointment",
            "description": "Create a new appointment in AcuityScheduling",
            "group": "Appointments",
            "tags": ["appointments", "create", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Created appointment ID"},
                        "firstName": {"type": "string"},
                        "lastName": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "phone": {"type": "string"},
                        "datetime": {"type": "string", "format": "date-time"},
                        "endDateTime": {"type": "string", "format": "date-time"},
                        "appointmentTypeID": {"type": "integer"},
                        "calendarID": {"type": "integer"},
                        "price": {"type": "string"},
                        "confirmationPage": {"type": "string"},
                        "location": {"type": "string"}
                    }
                }
            },
            
            # 2. Array templates for complex inputs
            "array_templates": {
                "fields": [
                    {"template": {"id": 1, "value": "Consultation"}, "description": "Custom field value"},
                    {"template": {"id": 2, "value": "First time client"}, "description": "Another custom field"}
                ]
            },
            
            # 3. Parameter dependencies & conditional fields
            "parameter_dependencies": [
                {
                    "when_field": "appointment_data.appointmentTypeID",
                    "when_value": "exists",
                    "then_require": ["appointment_data.datetime", "appointment_data.firstName", "appointment_data.email"],
                    "then_optional": ["appointment_data.lastName", "appointment_data.phone"],
                    "require_one_of": ["appointment_data.email"],
                    "mutually_exclusive": []
                }
            ],
            
            "validation_rules": {
                "appointment_data": {
                    "pattern": "",
                    "message": "Appointment data must contain appointmentTypeID, datetime, firstName, and email",
                    "pattern_type": "custom",
                    "required": True,
                    "required_properties": ["appointmentTypeID", "datetime", "firstName", "email"]
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Create basic appointment",
                    "description": "Create a new appointment with basic information",
                    "input": {
                        "appointment_data": {
                            "appointmentTypeID": 1,
                            "datetime": "2024-01-15T14:00:00",
                            "firstName": "John",
                            "lastName": "Doe",
                            "email": "john@example.com",
                            "phone": "555-123-4567"
                        }
                    }
                },
                {
                    "name": "Create appointment with custom fields",
                    "description": "Create an appointment with additional custom field data",
                    "input": {
                        "appointment_data": {
                            "appointmentTypeID": 1,
                            "datetime": "2024-01-15T14:00:00",
                            "firstName": "Jane",
                            "lastName": "Smith",
                            "email": "jane@example.com",
                            "phone": "555-987-6543",
                            "notes": "First appointment",
                            "fields": [
                                {"id": 1, "value": "Consultation"},
                                {"id": 2, "value": "New client"}
                            ]
                        }
                    }
                }
            ]
        },
        "update_appointment": {
            "method": "PUT",
            "endpoint": "/appointments/{appointment_id}",
            "required_params": ["appointment_id", "appointment_data"],
            "optional_params": [],
            "body_parameters": ["appointment_data"],
            "display_name": "Update Appointment",
            "description": "Update an existing appointment in AcuityScheduling",
            "group": "Appointments",
            "tags": ["appointments", "update", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            # 2. Array templates for updating custom fields and add-ons
            "array_templates": {
                "fields": [
                    {"template": {"id": 1, "value": "Updated consultation"}, "description": "Custom field value update"},
                    {"template": {"id": 2, "value": "Returning client"}, "description": "Another custom field update"}
                ],
                "addonIDs": [
                    {"template": 1, "description": "Add-on service ID"},
                    {"template": 2, "description": "Additional service ID"},
                    {"template": 3, "description": "Premium service add-on ID"}
                ]
            },
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Updated appointment ID"},
                        "firstName": {"type": "string"},
                        "lastName": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "datetime": {"type": "string", "format": "date-time"},
                        "appointmentTypeID": {"type": "integer"},
                        "calendarID": {"type": "integer"},
                        "notes": {"type": "string"}
                    }
                }
            },
            
            "validation_rules": {
                "appointment_id": {
                    "pattern": "",
                    "message": "Appointment ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Update appointment",
                    "description": "Update an existing appointment",
                    "input": {
                        "appointment_id": 123,
                        "appointment_data": {
                            "notes": "Updated notes",
                            "firstName": "John",
                            "lastName": "Smith"
                        }
                    }
                }
            ]
        },
        "delete_appointment": {
            "method": "DELETE",
            "endpoint": "/appointments/{appointment_id}",
            "required_params": ["appointment_id"],
            "optional_params": [],
            "display_name": "Delete Appointment",
            "description": "Delete an appointment from AcuityScheduling",
            "group": "Appointments",
            "tags": ["appointments", "delete", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Success message"}
                    }
                }
            },
            
            "validation_rules": {
                "appointment_id": {
                    "pattern": "",
                    "message": "Appointment ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Delete appointment",
                    "description": "Delete an appointment by ID",
                    "input": {
                        "appointment_id": 123
                    }
                }
            ]
        },
        "cancel_appointment": {
            "method": "PUT",
            "endpoint": "/appointments/{appointment_id}/cancel",
            "required_params": ["appointment_id"],
            "optional_params": ["cancel_note"],
            "body_parameters": ["cancel_note"],
            "display_name": "Cancel Appointment",
            "description": "Cancel an appointment in AcuityScheduling",
            "group": "Appointments",
            "tags": ["appointments", "cancel", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Cancelled appointment ID"},
                        "canceled": {"type": "boolean", "description": "Cancellation status"},
                        "cancelNote": {"type": "string", "description": "Cancellation note"}
                    }
                }
            },
            
            "validation_rules": {
                "appointment_id": {
                    "pattern": "",
                    "message": "Appointment ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Cancel appointment",
                    "description": "Cancel an appointment with optional note",
                    "input": {
                        "appointment_id": 123,
                        "cancel_note": "Client requested cancellation"
                    }
                }
            ]
        },
        "list_clients": {
            "method": "GET",
            "endpoint": "/clients",
            "required_params": [],
            "optional_params": ["limit", "offset"],
            "display_name": "List Clients",
            "description": "Retrieve a list of clients from AcuityScheduling",
            "group": "Clients",
            "tags": ["clients", "list", "management"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Client ID"},
                            "firstName": {"type": "string"},
                            "lastName": {"type": "string"},
                            "phone": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "notes": {"type": "string"}
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "List all clients",
                    "description": "Get all clients",
                    "input": {}
                }
            ]
        },
        "get_client": {
            "method": "GET",
            "endpoint": "/clients/{client_id}",
            "required_params": ["client_id"],
            "optional_params": [],
            "display_name": "Get Client",
            "description": "Retrieve a specific client by ID",
            "group": "Clients",
            "tags": ["clients", "get", "management"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Client ID"},
                        "firstName": {"type": "string"},
                        "lastName": {"type": "string"},
                        "phone": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "notes": {"type": "string"}
                    }
                }
            },
            
            "validation_rules": {
                "client_id": {
                    "pattern": "",
                    "message": "Client ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Get client by ID",
                    "description": "Retrieve a specific client",
                    "input": {
                        "client_id": 456
                    }
                }
            ]
        },
        "create_client": {
            "method": "POST",
            "endpoint": "/clients",
            "required_params": ["client_data"],
            "optional_params": [],
            "body_parameters": ["client_data"],
            "display_name": "Create Client",
            "description": "Create a new client in AcuityScheduling",
            "group": "Clients",
            "tags": ["clients", "create", "management"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Created client ID"},
                        "firstName": {"type": "string"},
                        "lastName": {"type": "string"},
                        "phone": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "notes": {"type": "string"}
                    }
                }
            },
            
            "validation_rules": {
                "client_data": {
                    "pattern": "",
                    "message": "Client data must contain firstName and email",
                    "pattern_type": "custom",
                    "required": True,
                    "required_properties": ["firstName", "email"]
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Create new client",
                    "description": "Create a new client record",
                    "input": {
                        "client_data": {
                            "firstName": "Jane",
                            "lastName": "Smith",
                            "email": "jane@example.com",
                            "phone": "555-987-6543"
                        }
                    }
                }
            ]
        },
        "update_client": {
            "method": "PUT",
            "endpoint": "/clients/{client_id}",
            "required_params": ["client_id", "client_data"],
            "optional_params": [],
            "body_parameters": ["client_data"],
            "display_name": "Update Client",
            "description": "Update an existing client in AcuityScheduling",
            "group": "Clients",
            "tags": ["clients", "update", "management"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Updated client ID"},
                        "firstName": {"type": "string"},
                        "lastName": {"type": "string"},
                        "phone": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "notes": {"type": "string"}
                    }
                }
            },
            
            "validation_rules": {
                "client_id": {
                    "pattern": "",
                    "message": "Client ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Update client",
                    "description": "Update client information",
                    "input": {
                        "client_id": 456,
                        "client_data": {
                            "firstName": "Jane",
                            "lastName": "Doe",
                            "phone": "555-123-9999"
                        }
                    }
                }
            ]
        },
        "get_availability": {
            "method": "GET",
            "endpoint": "/availability/dates",
            "required_params": ["appointmentTypeID"],
            "optional_params": ["month", "calendarID"],
            "display_name": "Get Availability",
            "description": "Get availability dates for an appointment type",
            "group": "Availability",
            "tags": ["availability", "dates", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "array",
            
            # 2. Array templates for checking availability across multiple appointment types and calendars
            "array_templates": {
                "appointmentTypeIDs": [
                    {"template": 1, "description": "Primary appointment type for availability"},
                    {"template": 2, "description": "Secondary appointment type for availability"},
                    {"template": 3, "description": "Alternative appointment type"}
                ],
                "calendarIDs": [
                    {"template": 1, "description": "Primary calendar for availability"},
                    {"template": 2, "description": "Secondary calendar for availability"}
                ],
                "months": [
                    {"template": "2024-01", "description": "January 2024"},
                    {"template": "2024-02", "description": "February 2024"},
                    {"template": "2024-03", "description": "March 2024"}
                ]
            },
            
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "format": "date", "description": "Available date"},
                            "hasAvailability": {"type": "boolean", "description": "Whether date has availability"}
                        }
                    }
                }
            },
            
            "validation_rules": {
                "appointmentTypeID": {
                    "pattern": "",
                    "message": "Appointment Type ID is required and must be positive",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Get availability for appointment type",
                    "description": "Get available dates for a specific appointment type",
                    "input": {
                        "appointmentTypeID": 1
                    }
                }
            ]
        },
        "get_times": {
            "method": "GET",
            "endpoint": "/availability/times",
            "required_params": ["appointmentTypeID"],
            "optional_params": ["date", "month", "calendarID"],
            "display_name": "Get Times",
            "description": "Retrieve available appointment time slots",
            "group": "Availability",
            "tags": ["availability", "times", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "array",
            
            # 2. Array templates for multiple appointment types and calendar availability
            "array_templates": {
                "appointmentTypeIDs": [
                    {"template": 1, "description": "Primary appointment type for availability"},
                    {"template": 2, "description": "Alternative appointment type"},
                    {"template": 3, "description": "Backup appointment type"}
                ],
                "calendarIDs": [
                    {"template": 1, "description": "Primary calendar for availability check"},
                    {"template": 2, "description": "Secondary calendar for availability check"}
                ],
                "preferred_times": [
                    {"template": "09:00", "description": "Morning preferred time"},
                    {"template": "14:00", "description": "Afternoon preferred time"},
                    {"template": "17:00", "description": "Evening preferred time"}
                ]
            },
            
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "time": {"type": "string", "format": "date-time", "description": "Available time slot"},
                            "slotsAvailable": {"type": "integer", "description": "Number of slots available"}
                        }
                    }
                }
            },
            
            "validation_rules": {
                "appointmentTypeID": {
                    "pattern": "",
                    "message": "Appointment Type ID is required and must be positive",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                },
                "date": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "message": "Date must be in YYYY-MM-DD format",
                    "pattern_type": "regex",
                    "required": False
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Get availability for appointment type",
                    "description": "Get all available times for a specific appointment type",
                    "input": {
                        "appointmentTypeID": 1
                    }
                },
                {
                    "name": "Get availability for specific date",
                    "description": "Get available times for a specific date and appointment type",
                    "input": {
                        "appointmentTypeID": 1,
                        "date": "2024-01-15"
                    }
                }
            ]
        }
        ,
        "list_calendars": {
            "method": "GET",
            "endpoint": "/calendars",
            "required_params": [],
            "optional_params": [],
            "display_name": "List Calendars",
            "description": "Retrieve a list of calendars from AcuityScheduling",
            "group": "Calendars",
            "tags": ["calendars", "list", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            # 2. Array templates for calendar filtering and management
            "array_templates": {
                "calendar_ids": [
                    {"template": 1, "description": "Primary practitioner calendar"},
                    {"template": 2, "description": "Secondary practitioner calendar"},
                    {"template": 3, "description": "Resource/room calendar"}
                ],
                "timezones": [
                    {"template": "America/New_York", "description": "Eastern Time"},
                    {"template": "America/Chicago", "description": "Central Time"},
                    {"template": "America/Los_Angeles", "description": "Pacific Time"},
                    {"template": "Europe/London", "description": "GMT/UTC"}
                ],
                "locations": [
                    {"template": "Main Office", "description": "Primary location"},
                    {"template": "Branch Office", "description": "Secondary location"},
                    {"template": "Remote/Virtual", "description": "Virtual appointments"}
                ]
            },
            
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Calendar ID"},
                            "name": {"type": "string", "description": "Calendar name"},
                            "description": {"type": "string", "description": "Calendar description"},
                            "location": {"type": "string", "description": "Calendar location"},
                            "timezone": {"type": "string", "description": "Calendar timezone"}
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "List all calendars",
                    "description": "Get all available calendars",
                    "input": {}
                }
            ]
        },
        "get_calendar": {
            "method": "GET",
            "endpoint": "/calendars/{calendar_id}",
            "required_params": ["calendar_id"],
            "optional_params": [],
            "display_name": "Get Calendar",
            "description": "Retrieve a specific calendar by ID",
            "group": "Calendars",
            "tags": ["calendars", "get", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Calendar ID"},
                        "name": {"type": "string", "description": "Calendar name"},
                        "description": {"type": "string", "description": "Calendar description"},
                        "location": {"type": "string", "description": "Calendar location"},
                        "timezone": {"type": "string", "description": "Calendar timezone"}
                    }
                }
            },
            
            "validation_rules": {
                "calendar_id": {
                    "pattern": "",
                    "message": "Calendar ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Get calendar by ID",
                    "description": "Retrieve a specific calendar",
                    "input": {
                        "calendar_id": 1
                    }
                }
            ]
        },
        "list_appointment_types": {
            "method": "GET",
            "endpoint": "/appointment-types",
            "required_params": [],
            "optional_params": [],
            "display_name": "List Appointment Types",
            "description": "Retrieve a list of appointment types from AcuityScheduling",
            "group": "Appointment Types",
            "tags": ["appointment-types", "list", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            # 2. Array templates for appointment type filtering and configuration
            "array_templates": {
                "appointment_type_ids": [
                    {"template": 1, "description": "Consultation appointment type"},
                    {"template": 2, "description": "Follow-up appointment type"},
                    {"template": 3, "description": "Emergency appointment type"}
                ],
                "categories": [
                    {"template": "consultation", "description": "Initial consultation appointments"},
                    {"template": "treatment", "description": "Treatment session appointments"},
                    {"template": "follow-up", "description": "Follow-up appointments"}
                ],
                "durations": [
                    {"template": 30, "description": "30-minute appointment"},
                    {"template": 60, "description": "1-hour appointment"},
                    {"template": 90, "description": "90-minute appointment"},
                    {"template": 120, "description": "2-hour appointment"}
                ]
            },
            
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Appointment type ID"},
                            "name": {"type": "string", "description": "Appointment type name"},
                            "description": {"type": "string", "description": "Appointment type description"},
                            "duration": {"type": "integer", "description": "Appointment duration in minutes"},
                            "price": {"type": "string", "description": "Appointment price"},
                            "category": {"type": "string", "description": "Appointment category"},
                            "active": {"type": "boolean", "description": "Whether appointment type is active"}
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "List all appointment types",
                    "description": "Get all available appointment types",
                    "input": {}
                }
            ]
        },
        "get_appointment_type": {
            "method": "GET",
            "endpoint": "/appointment-types/{appointment_type_id}",
            "required_params": ["appointment_type_id"],
            "optional_params": [],
            "display_name": "Get Appointment Type",
            "description": "Retrieve a specific appointment type by ID",
            "group": "Appointment Types",
            "tags": ["appointment-types", "get", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Appointment type ID"},
                        "name": {"type": "string", "description": "Appointment type name"},
                        "description": {"type": "string", "description": "Appointment type description"},
                        "duration": {"type": "integer", "description": "Appointment duration in minutes"},
                        "price": {"type": "string", "description": "Appointment price"},
                        "category": {"type": "string", "description": "Appointment category"},
                        "active": {"type": "boolean", "description": "Whether appointment type is active"}
                    }
                }
            },
            
            "validation_rules": {
                "appointment_type_id": {
                    "pattern": "",
                    "message": "Appointment Type ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Get appointment type by ID",
                    "description": "Retrieve a specific appointment type",
                    "input": {
                        "appointment_type_id": 1
                    }
                }
            ]
        },
        "list_blocks": {
            "method": "GET",
            "endpoint": "/blocks",
            "required_params": [],
            "optional_params": ["minDate", "maxDate", "calendarID"],
            "display_name": "List Blocks",
            "description": "Retrieve a list of time blocks from AcuityScheduling",
            "group": "Blocks",
            "tags": ["blocks", "list", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            # 2. Array templates for multiple calendar IDs filtering
            "array_templates": {
                "calendarIDs": [
                    {"template": 1, "description": "Primary calendar ID"},
                    {"template": 2, "description": "Secondary calendar ID"},
                    {"template": 3, "description": "Additional calendar ID"}
                ]
            },
            
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Block ID"},
                            "start": {"type": "string", "format": "date-time", "description": "Block start time"},
                            "end": {"type": "string", "format": "date-time", "description": "Block end time"},
                            "calendarID": {"type": "integer", "description": "Associated calendar ID"},
                            "notes": {"type": "string", "description": "Block notes"}
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "List all blocks",
                    "description": "Get all time blocks",
                    "input": {}
                }
            ]
        },
        "create_block": {
            "method": "POST",
            "endpoint": "/blocks",
            "required_params": ["block_data"],
            "optional_params": [],
            "body_parameters": ["block_data"],
            "display_name": "Create Block",
            "description": "Create a new time block in AcuityScheduling",
            "group": "Blocks",
            "tags": ["blocks", "create", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            # 2. Array templates for recurring blocks or multiple calendar blocks
            "array_templates": {
                "recurring_dates": [
                    {"template": "2024-01-15", "description": "First date for recurring block"},
                    {"template": "2024-01-22", "description": "Second date for recurring block"},
                    {"template": "2024-01-29", "description": "Third date for recurring block"}
                ],
                "calendar_ids": [
                    {"template": 1, "description": "Primary calendar for block"},
                    {"template": 2, "description": "Secondary calendar for block"}
                ]
            },
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Created block ID"},
                        "start": {"type": "string", "format": "date-time", "description": "Block start time"},
                        "end": {"type": "string", "format": "date-time", "description": "Block end time"},
                        "calendarID": {"type": "integer", "description": "Associated calendar ID"},
                        "notes": {"type": "string", "description": "Block notes"}
                    }
                }
            },
            
            "validation_rules": {
                "block_data": {
                    "pattern": "",
                    "message": "Block data must contain start, end, and calendarID",
                    "pattern_type": "custom",
                    "required": True,
                    "required_properties": ["start", "end", "calendarID"]
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Create time block",
                    "description": "Create a new time block",
                    "input": {
                        "block_data": {
                            "start": "2024-01-15T09:00:00",
                            "end": "2024-01-15T17:00:00",
                            "calendarID": 1,
                            "notes": "Blocked for training"
                        }
                    }
                }
            ]
        },
        "delete_block": {
            "method": "DELETE",
            "endpoint": "/blocks/{block_id}",
            "required_params": ["block_id"],
            "optional_params": [],
            "display_name": "Delete Block",
            "description": "Delete a time block from AcuityScheduling",
            "group": "Blocks",
            "tags": ["blocks", "delete", "scheduling"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Success message"}
                    }
                }
            },
            
            "validation_rules": {
                "block_id": {
                    "pattern": "",
                    "message": "Block ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "Delete block",
                    "description": "Delete a time block by ID",
                    "input": {
                        "block_id": 123
                    }
                }
            ]
        },
        "list_certificates": {
            "method": "GET",
            "endpoint": "/certificates",
            "required_params": [],
            "optional_params": [],
            "display_name": "List Certificates",
            "description": "Retrieve a list of certificates from AcuityScheduling",
            "group": "Certificates",
            "tags": ["certificates", "list", "products"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            # 2. Array templates for certificate filtering and bulk operations
            "array_templates": {
                "certificate_ids": [
                    {"template": 1, "description": "Basic certificate ID"},
                    {"template": 2, "description": "Premium certificate ID"},
                    {"template": 3, "description": "Advanced certificate ID"}
                ],
                "categories": [
                    {"template": "massage", "description": "Massage therapy certificates"},
                    {"template": "yoga", "description": "Yoga instructor certificates"},
                    {"template": "fitness", "description": "Fitness training certificates"}
                ]
            },
            
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Certificate ID"},
                            "name": {"type": "string", "description": "Certificate name"},
                            "description": {"type": "string", "description": "Certificate description"},
                            "price": {"type": "string", "description": "Certificate price"},
                            "active": {"type": "boolean", "description": "Whether certificate is active"}
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "List all certificates",
                    "description": "Get all available certificates",
                    "input": {}
                }
            ]
        },
        "list_forms": {
            "method": "GET",
            "endpoint": "/forms",
            "required_params": [],
            "optional_params": [],
            "display_name": "List Forms",
            "description": "Retrieve a list of forms from AcuityScheduling",
            "group": "Forms",
            "tags": ["forms", "list", "intake"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            # 2. Array templates for form fields and form management
            "array_templates": {
                "form_ids": [
                    {"template": 1, "description": "Intake form ID"},
                    {"template": 2, "description": "Medical history form ID"},
                    {"template": 3, "description": "Consent form ID"}
                ],
                "field_types": [
                    {"template": "text", "description": "Text input field"},
                    {"template": "select", "description": "Dropdown selection field"},
                    {"template": "checkbox", "description": "Checkbox field"},
                    {"template": "textarea", "description": "Multi-line text area"}
                ],
                "form_fields": [
                    {"template": {"id": 1, "label": "First Name", "type": "text", "required": True}, "description": "Basic text field"},
                    {"template": {"id": 2, "label": "Medical Conditions", "type": "textarea", "required": False}, "description": "Multi-line input field"},
                    {"template": {"id": 3, "label": "Preferred Time", "type": "select", "options": ["Morning", "Afternoon", "Evening"], "required": True}, "description": "Dropdown selection field"}
                ]
            },
            
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Form ID"},
                            "name": {"type": "string", "description": "Form name"},
                            "description": {"type": "string", "description": "Form description"},
                            "active": {"type": "boolean", "description": "Whether form is active"}
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "List all forms",
                    "description": "Get all available forms",
                    "input": {}
                }
            ]
        },
        "list_products": {
            "method": "GET",
            "endpoint": "/products",
            "required_params": [],
            "optional_params": [],
            "display_name": "List Products",
            "description": "Retrieve a list of products from AcuityScheduling",
            "group": "Products",
            "tags": ["products", "list", "e-commerce"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            # 2. Array templates for product management and e-commerce operations
            "array_templates": {
                "product_ids": [
                    {"template": 1, "description": "Basic service product ID"},
                    {"template": 2, "description": "Premium service product ID"},
                    {"template": 3, "description": "Package deal product ID"}
                ],
                "categories": [
                    {"template": "services", "description": "Service products"},
                    {"template": "packages", "description": "Package deals"},
                    {"template": "add-ons", "description": "Add-on services"}
                ],
                "price_ranges": [
                    {"template": {"min": 0, "max": 50}, "description": "Budget price range"},
                    {"template": {"min": 50, "max": 150}, "description": "Standard price range"},
                    {"template": {"min": 150, "max": 500}, "description": "Premium price range"}
                ]
            },
            
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Product ID"},
                            "name": {"type": "string", "description": "Product name"},
                            "description": {"type": "string", "description": "Product description"},
                            "price": {"type": "string", "description": "Product price"},
                            "active": {"type": "boolean", "description": "Whether product is active"}
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "List all products",
                    "description": "Get all available products",
                    "input": {}
                }
            ]
        },
        "list_orders": {
            "method": "GET",
            "endpoint": "/orders",
            "required_params": [],
            "optional_params": ["minDate", "maxDate"],
            "display_name": "List Orders",
            "description": "Retrieve a list of orders from AcuityScheduling",
            "group": "Orders",
            "tags": ["orders", "list", "e-commerce"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            # 2. Array templates for order filtering and management
            "array_templates": {
                "order_ids": [
                    {"template": 1001, "description": "Sample order ID"},
                    {"template": 1002, "description": "Another order ID"},
                    {"template": 1003, "description": "Additional order ID"}
                ],
                "order_statuses": [
                    {"template": "pending", "description": "Pending payment orders"},
                    {"template": "paid", "description": "Completed payment orders"},
                    {"template": "refunded", "description": "Refunded orders"},
                    {"template": "cancelled", "description": "Cancelled orders"}
                ],
                "payment_methods": [
                    {"template": "credit_card", "description": "Credit card payments"},
                    {"template": "paypal", "description": "PayPal payments"},
                    {"template": "cash", "description": "Cash payments"},
                    {"template": "check", "description": "Check payments"}
                ]
            },
            
            "output_schema": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Order ID"},
                            "appointmentID": {"type": "integer", "description": "Associated appointment ID"},
                            "total": {"type": "string", "description": "Order total"},
                            "date": {"type": "string", "format": "date-time", "description": "Order date"},
                            "status": {"type": "string", "description": "Order status"}
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["ACUITYSCHEDULING_USER_ID", "ACUITYSCHEDULING_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["user_id", "api_key"],
                "auth_type": "basic_auth",
                "auth_description": "Requires AcuityScheduling User ID and API Key for basic authentication"
            },
            "examples": [
                {
                    "name": "List all orders",
                    "description": "Get all orders",
                    "input": {}
                }
            ]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced AcuityScheduling node with embedded configuration."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Initialize the Enhanced UniversalRequestNode with embedded config
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.info("Enhanced AcuitySchedulingNode initialized with all 13 advanced features")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"AcuitySchedulingNode executing operation: {node_data.get('params', {}).get('operation')}")
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
__all__ = ["AcuitySchedulingNode"]