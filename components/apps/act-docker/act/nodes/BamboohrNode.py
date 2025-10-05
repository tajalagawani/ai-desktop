#!/usr/bin/env python3
"""
BambooHR Node - Enhanced with ALL 13 advanced features
Configuration is embedded directly in the node - no separate config.json needed
Comprehensive HR management integration for BambooHR API
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

class BamboohrNode(BaseNode):
    """
    Enhanced BambooHR node with ALL 13 advanced features - comprehensive HR management.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "bamboohr",
            "display_name": "BambooHR",
            "description": "Comprehensive BambooHR API integration for HR management, employee data, time tracking, payroll, benefits, and performance management",
            "category": "hr",
            "vendor": "bamboohr", 
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["hr", "human-resources", "payroll", "employees", "benefits", "time-tracking", "performance", "bamboo"],
            "documentation_url": "https://documentation.bamboohr.com/docs",
            "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/bamboo.svg",
            "color": "#7CB342",
            "created_at": "2025-08-26T00:00:00Z",
            "updated_at": "2025-08-26T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.bamboohr.com/api/gateway.php/{subdomain}/v1",
            "authentication": {
                "type": "basic_auth",
                "username": "api_key",
                "password": ""
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
                "timeout_ms": 45000
            },
            # 5. Rate limiting configuration
            "rate_limiting": {
                "requests_per_minute": 1000,
                "requests_per_second": 15.0,
                "burst_size": 5,
                "cost_per_request": 0.01,
                "quota_type": "requests",
                "rate_limit_headers": {
                    "limit": "X-RateLimit-Limit",
                    "remaining": "X-RateLimit-Remaining",
                    "reset": "X-RateLimit-Reset"
                }
            },
            "timeouts": {
                "connect": 15.0,
                "read": 45.0,
                "total": 90.0
            }
        },
        
        # Enhanced pricing information
        "pricing": {
            "cost_per_1k_requests": 10.0,
            "cost_per_request": 0.01,
            "billing_unit": "requests",
            "free_tier_limit": 10000
        },
        
        # 11. Performance monitoring
        "performance_monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "request_count", "data_volume"],
            "alerts": {
                "error_rate_threshold": 0.03,
                "response_time_threshold": 8000,
                "quota_usage_threshold": 0.85
            },
            "sampling_rate": 0.1,
            "retention_days": 30
        },
        
        # 12. Intelligent caching strategy
        "caching_strategy": {
            "enabled": True,
            "cache_key_template": "{operation}:{subdomain}:{hash}",
            "ttl_seconds": 600,
            "cache_conditions": {
                "only_for": ["GET"],
                "exclude_params": ["timestamp", "nonce", "updated_since"],
                "cache_by_operation": {
                    "get_employee": 1800,
                    "list_employees": 300,
                    "get_company_files": 3600,
                    "list_time_off_requests": 180
                }
            },
            "invalidation_patterns": [
                "employee_*",
                "timeoff_*",
                "payroll_*"
            ]
        },
        
        # 10. Testing configuration
        "testing_mode": {
            "sandbox_mode": True,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/meta/users",
            "test_subdomain": "test-company",
            "mock_responses": True,
            "test_data_reset": True
        },
        
        # 13. Documentation links
        "documentation_links": {
            "api_docs_url": "https://documentation.bamboohr.com/docs",
            "setup_guide": "https://documentation.bamboohr.com/docs/getting-started",
            "troubleshooting": "https://help.bamboohr.com/hc/en-us/categories/360002712231-API",
            "changelog": "https://documentation.bamboohr.com/docs/changelog",
            "authentication_guide": "https://documentation.bamboohr.com/docs/authentication",
            "rate_limits": "https://documentation.bamboohr.com/docs/rate-limiting",
            "webhook_guide": "https://documentation.bamboohr.com/docs/webhooks"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "BambooHR API key for authentication",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-f0-9]{40}$",
                    "message": "API key must be 40-character hexadecimal string",
                    "minLength": 40,
                    "maxLength": 40
                }
            },
            "subdomain": {
                "type": "string",
                "description": "BambooHR company subdomain",
                "required": True,
                "group": "Authentication",
                "examples": ["acme-corp", "my-company", "test-org"],
                "validation": {
                    "pattern": "^[a-z0-9-]+$",
                    "message": "Subdomain must contain only lowercase letters, numbers, and hyphens",
                    "minLength": 2,
                    "maxLength": 50
                }
            },
            "operation": {
                "type": "string",
                "description": "The BambooHR operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    "get_employee", "list_employees", "create_employee", "update_employee",
                    "get_time_off_request", "list_time_off_requests", "create_time_off_request", 
                    "approve_time_off_request", "get_employee_files", "upload_employee_file",
                    "get_company_files", "list_custom_fields", "get_payroll_deductions",
                    "get_benefits_enrollments", "list_training_records", "create_performance_review",
                    "get_goals", "list_compensation_changes", "get_employee_photo", "update_employee_photo"
                ]
            },
            "employee_id": {
                "type": "integer",
                "description": "Employee ID for employee-specific operations",
                "required": False,
                "group": "Employee",
                "validation": {
                    "minimum": 1,
                    "maximum": 999999
                },
                "examples": [123, 456, 789]
            },
            "fields": {
                "type": "array",
                "description": "List of fields to retrieve for employee data",
                "required": False,
                "group": "Data",
                "examples": [["firstName", "lastName", "workEmail"], ["department", "jobTitle", "hireDate"]],
                "validation": {
                    "minItems": 1,
                    "maxItems": 50,
                    "items": {
                        "type": "string",
                        "enum": [
                            "firstName", "lastName", "middleName", "workEmail", "personalEmail",
                            "department", "jobTitle", "hireDate", "terminationDate", "workPhone",
                            "mobilePhone", "address1", "address2", "city", "state", "zipcode",
                            "country", "dateOfBirth", "ssn", "sin", "employeeNumber", "status",
                            "supervisor", "payRate", "payType", "paySchedule", "location"
                        ]
                    }
                }
            },
            "employee_data": {
                "type": "object",
                "description": "Employee data for create/update operations",
                "required": False,
                "group": "Employee Data",
                "examples": [
                    {
                        "firstName": "John",
                        "lastName": "Doe", 
                        "workEmail": "john.doe@company.com",
                        "department": "Engineering",
                        "jobTitle": "Software Engineer"
                    }
                ]
            },
            "time_off_request_data": {
                "type": "object",
                "description": "Time off request data",
                "required": False,
                "group": "Time Off",
                "examples": [
                    {
                        "employeeId": 123,
                        "start": "2025-09-01",
                        "end": "2025-09-05",
                        "timeOffTypeId": 1,
                        "amount": 5.0,
                        "notes": "Family vacation"
                    }
                ]
            },
            "start_date": {
                "type": "string",
                "description": "Start date for date range queries (YYYY-MM-DD format)",
                "required": False,
                "group": "Date Range",
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "message": "Date must be in YYYY-MM-DD format"
                },
                "examples": ["2025-01-01", "2025-06-01", "2025-12-31"]
            },
            "end_date": {
                "type": "string",
                "description": "End date for date range queries (YYYY-MM-DD format)",
                "required": False,
                "group": "Date Range",
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "message": "Date must be in YYYY-MM-DD format"
                },
                "examples": ["2025-01-31", "2025-06-30", "2025-12-31"]
            },
            "status": {
                "type": "string",
                "description": "Filter by employee status",
                "required": False,
                "group": "Filters",
                "validation": {
                    "enum": ["Active", "Inactive", "Terminated"]
                }
            },
            "department": {
                "type": "string",
                "description": "Filter by department",
                "required": False,
                "group": "Filters",
                "examples": ["Engineering", "Sales", "Marketing", "HR", "Finance"]
            },
            "file": {
                "type": "string",
                "description": "File data (base64 encoded) for file upload operations",
                "required": False,
                "group": "Files"
            },
            "file_name": {
                "type": "string",
                "description": "Name of the file being uploaded",
                "required": False,
                "group": "Files",
                "validation": {
                    "maxLength": 255
                }
            },
            "file_category": {
                "type": "string",
                "description": "Category for file uploads",
                "required": False,
                "group": "Files",
                "validation": {
                    "enum": ["general", "emergency", "personal", "benefits", "immigration"]
                }
            },
            "time_off_type_id": {
                "type": "integer",
                "description": "ID of the time off type",
                "required": False,
                "group": "Time Off",
                "validation": {
                    "minimum": 1
                }
            },
            "approval_status": {
                "type": "string",
                "description": "Approval status for time off requests",
                "required": False,
                "group": "Time Off",
                "validation": {
                    "enum": ["approved", "denied", "superseded", "requested", "canceled"]
                }
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of records to return",
                "required": False,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 1000
                },
                "default": 100
            },
            "offset": {
                "type": "integer",
                "description": "Number of records to skip",
                "required": False,
                "group": "Pagination",
                "validation": {
                    "minimum": 0
                },
                "default": 0
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful BambooHR API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from BambooHR API"},
                    "pagination": {"type": "object", "description": "Pagination information if applicable"},
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
                    "error_code": {"type": "string", "description": "BambooHR error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "get_employee": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": []
            },
            "list_employees": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": []
            },
            "create_employee": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": []
            },
            "update_employee": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": []
            },
            "get_time_off_request": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": []
            },
            "list_time_off_requests": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": []
            },
            "create_time_off_request": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": []
            }
        },
        
        # 7. Error handling - comprehensive error codes
        "error_handling": {
            "error_codes": {
                "400": "Bad Request - Invalid parameters or malformed request",
                "401": "Unauthorized - Invalid API key or subdomain",
                "403": "Forbidden - Access denied to requested resource",
                "404": "Not Found - Employee, resource, or endpoint not found",
                "405": "Method Not Allowed - HTTP method not supported for endpoint",
                "409": "Conflict - Resource conflict (duplicate employee, etc.)",
                "422": "Unprocessable Entity - Validation errors in request data",
                "429": "Too Many Requests - Rate limit exceeded",
                "500": "Internal Server Error - BambooHR server error",
                "502": "Bad Gateway - BambooHR server temporarily unavailable",
                "503": "Service Unavailable - BambooHR maintenance or overload"
            },
            "retry_strategies": {
                "429": {"strategy": "exponential_backoff", "max_attempts": 5, "base_delay": 60},
                "500": {"strategy": "linear_backoff", "max_attempts": 3, "base_delay": 5},
                "502": {"strategy": "exponential_backoff", "max_attempts": 3, "base_delay": 2},
                "503": {"strategy": "exponential_backoff", "max_attempts": 3, "base_delay": 10}
            },
            "circuit_breaker": {
                "failure_threshold": 5,
                "recovery_timeout": 300,
                "expected_recovery_time": 60
            }
        },
        
        # 9. Webhook support
        "webhook_support": {
            "supported": True,
            "webhook_events": [
                "employee.created", "employee.updated", "employee.terminated",
                "timeoff.requested", "timeoff.approved", "timeoff.denied",
                "benefit.enrolled", "benefit.terminated",
                "performance.review.created", "goal.updated"
            ],
            "webhook_config": {
                "url": "webhook_url",
                "secret": "webhook_secret",
                "events": "webhook_events"
            },
            "verification": {
                "signature_header": "X-BambooHR-Signature",
                "algorithm": "sha256"
            }
        },
        
        # 6. Pagination support
        "pagination": {
            "supported": True,
            "default_limit": 100,
            "max_limit": 1000,
            "pagination_style": "offset_limit",
            "parameters": {
                "limit": "limit",
                "offset": "offset"
            },
            "response_format": {
                "total_count": "total",
                "current_page": "page",
                "items": "employees"
            }
        }
    }
    
    # Enhanced operation definitions with ALL 13 features
    OPERATIONS = {
        "get_employee": {
            "method": "GET",
            "endpoint": "/employees/{employee_id}",
            "required_params": ["employee_id"],
            "optional_params": ["fields"],
            "url_parameters": ["employee_id"],
            "query_parameters": ["fields"],
            "display_name": "Get Employee",
            "description": "Retrieve detailed information about a specific employee",
            "group": "Employees",
            "tags": ["employee", "profile", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 1800,
            "response_type": "object",
            
            # 1. Output schemas - detailed response schemas
            "output_schemas": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Employee ID"},
                        "firstName": {"type": "string", "description": "Employee first name"},
                        "lastName": {"type": "string", "description": "Employee last name"},
                        "workEmail": {"type": "string", "format": "email", "description": "Work email address"},
                        "department": {"type": "string", "description": "Department name"},
                        "jobTitle": {"type": "string", "description": "Job title"},
                        "hireDate": {"type": "string", "format": "date", "description": "Hire date"},
                        "status": {"type": "string", "enum": ["Active", "Inactive", "Terminated"]},
                        "supervisor": {"type": "string", "description": "Supervisor name"},
                        "location": {"type": "string", "description": "Work location"},
                        "payRate": {"type": "number", "description": "Pay rate"},
                        "payType": {"type": "string", "enum": ["hourly", "salary"]},
                        "employeeNumber": {"type": "string", "description": "Employee number"}
                    }
                },
                "error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "description": "Error message"},
                        "code": {"type": "integer", "description": "HTTP error code"}
                    }
                },
                "status_codes": {
                    200: "Employee found and returned successfully",
                    404: "Employee not found",
                    401: "Invalid authentication",
                    403: "Access denied to employee record"
                }
            },
            
            # 2. Array templates for complex inputs
            "array_templates": {
                "fields": [
                    {"template": "firstName", "description": "Employee first name"},
                    {"template": "lastName", "description": "Employee last name"},
                    {"template": "workEmail", "description": "Work email address"},
                    {"template": "department", "description": "Department name"},
                    {"template": "jobTitle", "description": "Job title"},
                    {"template": "hireDate", "description": "Employee hire date"},
                    {"template": "supervisor", "description": "Supervisor information"},
                    {"template": "payRate", "description": "Employee pay rate"},
                    {"template": "status", "description": "Employment status"},
                    {"template": "location", "description": "Work location"}
                ]
            },
            
            # 3. Parameter dependencies & conditional fields
            "parameter_dependencies": [
                {
                    "when_field": "fields",
                    "when_value": ["payRate", "payType"],
                    "then_require": [],
                    "then_optional": [],
                    "require_one_of": [],
                    "mutually_exclusive": [],
                    "note": "Pay information requires elevated permissions"
                }
            ],
            
            # 4. Validation rules - advanced validation with regex patterns
            "validation_rules": {
                "employee_id": {
                    "pattern": "^[1-9]\\d*$",
                    "message": "Employee ID must be a positive integer",
                    "pattern_type": "regex",
                    "min_value": 1,
                    "max_value": 999999,
                    "required": True
                },
                "fields": {
                    "pattern": "",
                    "message": "Fields must be valid BambooHR field names",
                    "pattern_type": "custom",
                    "allowed_values": [
                        "firstName", "lastName", "middleName", "workEmail", "personalEmail",
                        "department", "jobTitle", "hireDate", "terminationDate", "workPhone",
                        "mobilePhone", "address1", "address2", "city", "state", "zipcode",
                        "country", "dateOfBirth", "ssn", "sin", "employeeNumber", "status",
                        "supervisor", "payRate", "payType", "paySchedule", "location"
                    ],
                    "required": False
                }
            },
            
            # 6. Pagination handling info (not applicable for single employee)
            "pagination": None,
            
            # 8. Field mapping & transformations
            "field_mapping": {
                "input_transforms": {
                    "employee_id": "validate_employee_id",
                    "fields": "validate_field_names"
                },
                "output_transforms": {
                    "hireDate": "format_date",
                    "terminationDate": "format_date",
                    "payRate": "format_currency"
                },
                "field_aliases": {
                    "emp_id": "employee_id",
                    "id": "employee_id"
                }
            },
            
            "auth": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": [],
                "required_params": ["api_key", "subdomain"],
                "auth_type": "basic_auth",
                "auth_description": "Requires BambooHR API key and company subdomain"
            },
            "examples": [
                {
                    "name": "Get basic employee info",
                    "description": "Retrieve basic employee information",
                    "input": {
                        "employee_id": 123,
                        "fields": ["firstName", "lastName", "workEmail", "department"]
                    }
                },
                {
                    "name": "Get comprehensive employee profile",
                    "description": "Get detailed employee profile with all available fields",
                    "input": {
                        "employee_id": 456,
                        "fields": [
                            "firstName", "lastName", "workEmail", "department", "jobTitle",
                            "hireDate", "supervisor", "location", "status"
                        ]
                    }
                }
            ]
        },
        
        "list_employees": {
            "method": "GET",
            "endpoint": "/employees/directory",
            "required_params": [],
            "optional_params": ["fields", "status", "department", "limit", "offset"],
            "query_parameters": ["fields", "status", "department", "limit", "offset"],
            "display_name": "List Employees",
            "description": "Retrieve a list of all employees with optional filtering",
            "group": "Employees",
            "tags": ["employees", "directory", "list"],
            "rate_limit_cost": 2,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schemas": {
                "success": {
                    "type": "object",
                    "properties": {
                        "employees": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "firstName": {"type": "string"},
                                    "lastName": {"type": "string"},
                                    "workEmail": {"type": "string", "format": "email"},
                                    "department": {"type": "string"},
                                    "jobTitle": {"type": "string"},
                                    "status": {"type": "string"}
                                }
                            }
                        },
                        "pagination": {
                            "type": "object",
                            "properties": {
                                "total": {"type": "integer"},
                                "limit": {"type": "integer"},
                                "offset": {"type": "integer"}
                            }
                        }
                    }
                }
            },
            
            "array_templates": {
                "fields": [
                    {"template": "firstName", "description": "Employee first name"},
                    {"template": "lastName", "description": "Employee last name"},
                    {"template": "workEmail", "description": "Work email address"},
                    {"template": "department", "description": "Department name"},
                    {"template": "jobTitle", "description": "Job title"},
                    {"template": "status", "description": "Employment status"}
                ]
            },
            
            "validation_rules": {
                "limit": {
                    "pattern": "^[1-9]\\d*$",
                    "message": "Limit must be between 1 and 1000",
                    "pattern_type": "regex",
                    "min_value": 1,
                    "max_value": 1000,
                    "required": False
                },
                "offset": {
                    "pattern": "^\\d+$",
                    "message": "Offset must be a non-negative integer",
                    "pattern_type": "regex",
                    "min_value": 0,
                    "required": False
                }
            },
            
            # 6. Pagination handling info
            "pagination": {
                "supported": True,
                "default_limit": 100,
                "max_limit": 1000,
                "style": "offset_limit"
            },
            
            "field_mapping": {
                "input_transforms": {
                    "fields": "validate_field_names"
                },
                "output_transforms": {
                    "employees": "format_employee_list"
                },
                "field_aliases": {}
            },
            
            "auth": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": [],
                "required_params": ["api_key", "subdomain"],
                "auth_type": "basic_auth",
                "auth_description": "Requires BambooHR API key and company subdomain"
            },
            "examples": [
                {
                    "name": "List all active employees",
                    "description": "Get directory of all active employees",
                    "input": {
                        "status": "Active",
                        "fields": ["firstName", "lastName", "workEmail", "department", "jobTitle"]
                    }
                },
                {
                    "name": "List engineering department",
                    "description": "Get employees from engineering department",
                    "input": {
                        "department": "Engineering",
                        "fields": ["firstName", "lastName", "workEmail", "jobTitle"],
                        "limit": 50
                    }
                }
            ]
        },
        
        "create_employee": {
            "method": "POST",
            "endpoint": "/employees",
            "required_params": ["employee_data"],
            "optional_params": [],
            "body_parameters": ["employee_data"],
            "display_name": "Create Employee",
            "description": "Create a new employee record in BambooHR",
            "group": "Employees",
            "tags": ["employee", "create", "onboarding"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schemas": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "New employee ID"},
                        "location": {"type": "string", "description": "URL of created employee resource"},
                        "created": {"type": "string", "format": "date-time"}
                    }
                }
            },
            
            "array_templates": {
                "employee_data": [
                    {
                        "template": {
                            "firstName": "John",
                            "lastName": "Doe",
                            "workEmail": "john.doe@company.com",
                            "department": "Engineering",
                            "jobTitle": "Software Engineer",
                            "hireDate": "2025-09-01",
                            "supervisor": "Jane Smith",
                            "location": "Remote"
                        },
                        "description": "Complete employee profile template"
                    },
                    {
                        "template": {
                            "firstName": "Jane",
                            "lastName": "Smith",
                            "workEmail": "jane.smith@company.com",
                            "department": "Marketing",
                            "jobTitle": "Marketing Manager"
                        },
                        "description": "Basic employee information template"
                    }
                ]
            },
            
            "parameter_dependencies": [
                {
                    "when_field": "employee_data.payType",
                    "when_value": "salary",
                    "then_require": ["employee_data.payRate"],
                    "then_optional": ["employee_data.paySchedule"],
                    "require_one_of": [],
                    "mutually_exclusive": []
                }
            ],
            
            "validation_rules": {
                "employee_data": {
                    "pattern": "",
                    "message": "Employee data must contain required fields",
                    "pattern_type": "object",
                    "required_fields": ["firstName", "lastName"],
                    "optional_fields": [
                        "middleName", "workEmail", "personalEmail", "department", "jobTitle",
                        "hireDate", "supervisor", "location", "payRate", "payType", "workPhone",
                        "mobilePhone", "address1", "city", "state", "zipcode", "country"
                    ],
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "employee_data": "validate_employee_data",
                    "employee_data.workEmail": "validate_email",
                    "employee_data.hireDate": "validate_date"
                },
                "output_transforms": {},
                "field_aliases": {}
            },
            
            "auth": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": [],
                "required_params": ["api_key", "subdomain"],
                "auth_type": "basic_auth",
                "auth_description": "Requires BambooHR API key with employee creation permissions"
            },
            "examples": [
                {
                    "name": "Create new software engineer",
                    "description": "Onboard a new software engineer",
                    "input": {
                        "employee_data": {
                            "firstName": "Alice",
                            "lastName": "Johnson",
                            "workEmail": "alice.johnson@company.com",
                            "department": "Engineering",
                            "jobTitle": "Senior Software Engineer",
                            "hireDate": "2025-09-15",
                            "supervisor": "Bob Wilson",
                            "location": "San Francisco"
                        }
                    }
                }
            ]
        },
        
        "update_employee": {
            "method": "POST",
            "endpoint": "/employees/{employee_id}",
            "required_params": ["employee_id", "employee_data"],
            "optional_params": [],
            "url_parameters": ["employee_id"],
            "body_parameters": ["employee_data"],
            "display_name": "Update Employee",
            "description": "Update an existing employee's information",
            "group": "Employees",
            "tags": ["employee", "update", "modify"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schemas": {
                "success": {
                    "type": "object",
                    "properties": {
                        "updated": {"type": "boolean"},
                        "employee_id": {"type": "integer"},
                        "modified_fields": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            
            "array_templates": {
                "employee_data": [
                    {
                        "template": {
                            "department": "Marketing",
                            "jobTitle": "Senior Marketing Specialist",
                            "supervisor": "Marketing Director"
                        },
                        "description": "Department transfer template"
                    },
                    {
                        "template": {
                            "workEmail": "new.email@company.com",
                            "workPhone": "+1-555-0123"
                        },
                        "description": "Contact information update template"
                    }
                ]
            },
            
            "validation_rules": {
                "employee_id": {
                    "pattern": "^[1-9]\\d*$",
                    "message": "Employee ID must be a positive integer",
                    "pattern_type": "regex",
                    "min_value": 1,
                    "max_value": 999999,
                    "required": True
                },
                "employee_data": {
                    "pattern": "",
                    "message": "Employee data must contain at least one field to update",
                    "pattern_type": "object",
                    "min_fields": 1,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "employee_id": "validate_employee_id",
                    "employee_data": "validate_employee_data"
                },
                "output_transforms": {},
                "field_aliases": {}
            },
            
            "auth": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": [],
                "required_params": ["api_key", "subdomain"],
                "auth_type": "basic_auth",
                "auth_description": "Requires BambooHR API key with employee update permissions"
            },
            "examples": [
                {
                    "name": "Update job title",
                    "description": "Promote employee with new job title",
                    "input": {
                        "employee_id": 123,
                        "employee_data": {
                            "jobTitle": "Senior Software Engineer",
                            "payRate": 95000
                        }
                    }
                }
            ]
        },
        
        "list_time_off_requests": {
            "method": "GET",
            "endpoint": "/time_off/requests",
            "required_params": [],
            "optional_params": ["employee_id", "start_date", "end_date", "approval_status", "time_off_type_id", "limit", "offset"],
            "query_parameters": ["employee_id", "start", "end", "status", "type", "limit", "offset"],
            "display_name": "List Time Off Requests",
            "description": "Retrieve time off requests with filtering options",
            "group": "Time Off",
            "tags": ["timeoff", "vacation", "pto", "requests"],
            "rate_limit_cost": 2,
            "cache_ttl": 180,
            "response_type": "array",
            
            "output_schemas": {
                "success": {
                    "type": "object",
                    "properties": {
                        "requests": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "employeeId": {"type": "integer"},
                                    "name": {"type": "string"},
                                    "start": {"type": "string", "format": "date"},
                                    "end": {"type": "string", "format": "date"},
                                    "created": {"type": "string", "format": "date-time"},
                                    "type": {"type": "object"},
                                    "amount": {"type": "number"},
                                    "status": {"type": "object"},
                                    "notes": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            
            "array_templates": {
                "approval_status": [
                    {"template": "approved", "description": "Approved time off requests"},
                    {"template": "denied", "description": "Denied time off requests"},
                    {"template": "requested", "description": "Pending approval requests"},
                    {"template": "canceled", "description": "Canceled requests"}
                ]
            },
            
            "validation_rules": {
                "start_date": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "message": "Start date must be in YYYY-MM-DD format",
                    "pattern_type": "regex",
                    "required": False
                },
                "end_date": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "message": "End date must be in YYYY-MM-DD format",
                    "pattern_type": "regex",
                    "required": False
                }
            },
            
            "pagination": {
                "supported": True,
                "default_limit": 50,
                "max_limit": 500,
                "style": "offset_limit"
            },
            
            "field_mapping": {
                "input_transforms": {
                    "start_date": "validate_date",
                    "end_date": "validate_date"
                },
                "output_transforms": {
                    "start": "format_date",
                    "end": "format_date",
                    "created": "format_datetime"
                },
                "field_aliases": {
                    "from": "start_date",
                    "to": "end_date"
                }
            },
            
            "auth": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": [],
                "required_params": ["api_key", "subdomain"],
                "auth_type": "basic_auth",
                "auth_description": "Requires BambooHR API key with time off access"
            },
            "examples": [
                {
                    "name": "Get pending requests",
                    "description": "List all pending time off requests",
                    "input": {
                        "approval_status": "requested",
                        "limit": 100
                    }
                },
                {
                    "name": "Employee's time off history",
                    "description": "Get time off requests for specific employee",
                    "input": {
                        "employee_id": 123,
                        "start_date": "2025-01-01",
                        "end_date": "2025-12-31"
                    }
                }
            ]
        },
        
        "create_time_off_request": {
            "method": "PUT",
            "endpoint": "/employees/{employee_id}/time_off/request",
            "required_params": ["employee_id", "time_off_request_data"],
            "optional_params": [],
            "url_parameters": ["employee_id"],
            "body_parameters": ["time_off_request_data"],
            "display_name": "Create Time Off Request",
            "description": "Submit a new time off request for an employee",
            "group": "Time Off",
            "tags": ["timeoff", "request", "vacation", "pto"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schemas": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Time off request ID"},
                        "created": {"type": "string", "format": "date-time"},
                        "status": {"type": "string", "enum": ["requested"]}
                    }
                }
            },
            
            "array_templates": {
                "time_off_request_data": [
                    {
                        "template": {
                            "start": "2025-09-01",
                            "end": "2025-09-05",
                            "timeOffTypeId": 1,
                            "amount": 5.0,
                            "notes": "Family vacation"
                        },
                        "description": "Standard vacation request template"
                    },
                    {
                        "template": {
                            "start": "2025-10-15",
                            "end": "2025-10-15",
                            "timeOffTypeId": 2,
                            "amount": 1.0,
                            "notes": "Medical appointment"
                        },
                        "description": "Single day time off template"
                    }
                ]
            },
            
            "parameter_dependencies": [
                {
                    "when_field": "time_off_request_data.start",
                    "when_value": "*",
                    "then_require": ["time_off_request_data.end", "time_off_request_data.timeOffTypeId"],
                    "then_optional": ["time_off_request_data.notes"],
                    "require_one_of": [],
                    "mutually_exclusive": []
                }
            ],
            
            "validation_rules": {
                "employee_id": {
                    "pattern": "^[1-9]\\d*$",
                    "message": "Employee ID must be a positive integer",
                    "pattern_type": "regex",
                    "required": True
                },
                "time_off_request_data": {
                    "pattern": "",
                    "message": "Time off request data must contain required fields",
                    "pattern_type": "object",
                    "required_fields": ["start", "end", "timeOffTypeId", "amount"],
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "employee_id": "validate_employee_id",
                    "time_off_request_data.start": "validate_date",
                    "time_off_request_data.end": "validate_date"
                },
                "output_transforms": {},
                "field_aliases": {}
            },
            
            "auth": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": [],
                "required_params": ["api_key", "subdomain"],
                "auth_type": "basic_auth",
                "auth_description": "Requires BambooHR API key with time off request permissions"
            },
            "examples": [
                {
                    "name": "Submit vacation request",
                    "description": "Request week-long vacation",
                    "input": {
                        "employee_id": 123,
                        "time_off_request_data": {
                            "start": "2025-09-01",
                            "end": "2025-09-05",
                            "timeOffTypeId": 1,
                            "amount": 5.0,
                            "notes": "Annual family vacation to Hawaii"
                        }
                    }
                }
            ]
        },
        
        "get_company_files": {
            "method": "GET",
            "endpoint": "/files/view/",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Company Files",
            "description": "Retrieve list of company files and documents",
            "group": "Files",
            "tags": ["files", "documents", "company"],
            "rate_limit_cost": 2,
            "cache_ttl": 3600,
            "response_type": "array",
            
            "output_schemas": {
                "success": {
                    "type": "object",
                    "properties": {
                        "categories": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "string"},
                                    "files": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                                "originalFileName": {"type": "string"},
                                                "size": {"type": "integer"},
                                                "dateCreated": {"type": "string", "format": "date-time"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": [],
                "required_params": ["api_key", "subdomain"],
                "auth_type": "basic_auth",
                "auth_description": "Requires BambooHR API key with file access permissions"
            },
            "examples": [
                {
                    "name": "List company files",
                    "description": "Get all company files and documents",
                    "input": {}
                }
            ]
        },
        
        "list_custom_fields": {
            "method": "GET",
            "endpoint": "/meta/fields",
            "required_params": [],
            "optional_params": [],
            "display_name": "List Custom Fields",
            "description": "Retrieve all available custom fields and their definitions",
            "group": "Meta",
            "tags": ["fields", "meta", "custom", "configuration"],
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "array",
            
            "output_schemas": {
                "success": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "alias": {"type": "string"}
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"],
                "optional_env_keys": [],
                "required_params": ["api_key", "subdomain"],
                "auth_type": "basic_auth",
                "auth_description": "Requires BambooHR API key"
            },
            "examples": [
                {
                    "name": "Get field definitions",
                    "description": "Retrieve all custom field definitions",
                    "input": {}
                }
            ]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced BambooHR node with embedded configuration."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Initialize the Enhanced UniversalRequestNode with embedded config
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.info("Enhanced BamboohrNode initialized with all 13 advanced features")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"BamboohrNode executing operation: {node_data.get('params', {}).get('operation')}")
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
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance monitoring metrics."""
        return self.universal_request_node.get_metrics()
    
    def get_caching_info(self) -> Dict[str, Any]:
        """Get current caching strategy information."""
        return self.CONFIG.get("caching_strategy", {})
    
    def get_webhook_config(self) -> Dict[str, Any]:
        """Get webhook support configuration."""
        return self.CONFIG.get("webhook_support", {})
    
    def get_error_handling_info(self) -> Dict[str, Any]:
        """Get comprehensive error handling information."""
        return self.CONFIG.get("error_handling", {})

    @staticmethod
    def format_response(response_data: Any) -> Dict[str, Any]:
        """Format response data consistently for HR operations."""
        if isinstance(response_data, dict):
            return response_data
        elif isinstance(response_data, list):
            return {"items": response_data, "count": len(response_data)}
        else:
            return {"result": response_data}

# Export the enhanced node class
__all__ = ["BamboohrNode"]