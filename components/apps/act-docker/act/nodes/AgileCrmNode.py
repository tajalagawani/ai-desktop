#!/usr/bin/env python3
"""
AgileCRM Node - Enhanced with ALL 13 advanced features
Comprehensive CRM and sales automation integration supporting all major AgileCRM operations.
Configuration is embedded directly in the node - no separate config.json needed.
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

class AgileCrmNode(BaseNode):
    """
    Enhanced AgileCRM node with ALL 13 advanced features - comprehensive CRM integration.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "agilecrm",
            "display_name": "AgileCRM",
            "description": "Comprehensive AgileCRM integration supporting all major API operations including contacts, companies, deals, tasks, notes, events, campaigns, documents, tickets, users, and tags management",
            "category": "crm",
            "vendor": "agilecrm", 
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["crm", "sales", "marketing", "contacts", "deals", "tasks", "campaigns", "automation"],
            "documentation_url": "https://github.com/agilecrm/rest-api",
            "icon": "https://s3.amazonaws.com/agilecrm/panel/uploaded-logo/1535471705_logo.png",
            "color": "#ff6600",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://{domain}.agilecrm.com/dev/api",
            "authentication": {
                "type": "basic_auth",
                "username_field": "email",
                "password_field": "api_key"
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
                "max_delay": 30.0,
                "jitter": True,
                "retriable_codes": [429, 500, 502, 503, 504],
                "retriable_exceptions": ["aiohttp.ClientTimeout", "aiohttp.ClientConnectorError"],
                "timeout_ms": 30000
            },
            "rate_limiting": {
                "requests_per_minute": 300,
                "requests_per_second": 5.0,
                "burst_size": 10,
                "cost_per_request": 1,
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
            "free_tier_limit": 10000
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
            "cache_key_template": "{operation}:{domain}:{hash}",
            "ttl_seconds": 300,
            "cache_conditions": {
                "only_for": ["GET"],
                "exclude_params": ["timestamp", "cursor"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/users"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://github.com/agilecrm/rest-api",
            "setup_guide": "https://github.com/agilecrm/rest-api#authentication",
            "troubleshooting": "https://github.com/agilecrm/rest-api#common-errors",
            "changelog": "https://github.com/agilecrm/rest-api/releases"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "domain": {
                "type": "string",
                "description": "AgileCRM domain (subdomain before .agilecrm.com)",
                "required": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-zA-Z0-9-_]+$",
                    "message": "Domain must contain only letters, numbers, hyphens, and underscores",
                    "minLength": 3,
                    "maxLength": 50
                }
            },
            "email": {
                "type": "string",
                "description": "AgileCRM login email address",
                "required": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "message": "Must be a valid email address"
                }
            },
            "api_key": {
                "type": "string",
                "description": "AgileCRM API key (from Admin Settings > API & Analytics)",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "minLength": 10,
                    "maxLength": 100
                }
            },
            "operation": {
                "type": "string",
                "description": "The AgileCRM operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    "get_contacts", "get_contact", "create_contact", "update_contact", "delete_contact", "search_contacts",
                    "get_companies", "get_company", "create_company", "update_company", "delete_company",
                    "get_deals", "get_deal", "create_deal", "update_deal", "delete_deal",
                    "get_tasks", "get_task", "create_task", "update_task", "delete_task",
                    "get_notes", "get_note", "create_note", "update_note", "delete_note",
                    "get_events", "get_event", "create_event", "update_event", "delete_event",
                    "get_campaigns", "get_campaign", "create_campaign", "update_campaign", "delete_campaign",
                    "get_tracks", "create_track", "update_track", "delete_track",
                    "get_documents", "upload_document", "delete_document",
                    "get_tickets", "get_ticket", "create_ticket", "update_ticket", "delete_ticket",
                    "get_users", "get_user", "get_tags", "create_tag", "delete_tag"
                ]
            },
            # ID parameters
            "contact_id": {
                "type": "integer",
                "description": "Contact ID for contact-specific operations",
                "required": False,
                "group": "Identifiers"
            },
            "company_id": {
                "type": "integer",
                "description": "Company ID for company-specific operations",
                "required": False,
                "group": "Identifiers"
            },
            "deal_id": {
                "type": "integer",
                "description": "Deal ID for deal-specific operations",
                "required": False,
                "group": "Identifiers"
            },
            "task_id": {
                "type": "integer",
                "description": "Task ID for task-specific operations",
                "required": False,
                "group": "Identifiers"
            },
            "note_id": {
                "type": "integer",
                "description": "Note ID for note-specific operations",
                "required": False,
                "group": "Identifiers"
            },
            "event_id": {
                "type": "integer",
                "description": "Event ID for event-specific operations",
                "required": False,
                "group": "Identifiers"
            },
            "campaign_id": {
                "type": "integer",
                "description": "Campaign ID for campaign-specific operations",
                "required": False,
                "group": "Identifiers"
            },
            "track_id": {
                "type": "integer",
                "description": "Track ID for track operations",
                "required": False,
                "group": "Identifiers"
            },
            "document_id": {
                "type": "integer",
                "description": "Document ID for document operations",
                "required": False,
                "group": "Identifiers"
            },
            "ticket_id": {
                "type": "integer",
                "description": "Ticket ID for help desk operations",
                "required": False,
                "group": "Identifiers"
            },
            "user_id": {
                "type": "integer",
                "description": "User ID for user operations",
                "required": False,
                "group": "Identifiers"
            },
            "tag_id": {
                "type": "integer",
                "description": "Tag ID for tag operations",
                "required": False,
                "group": "Identifiers"
            },
            # Contact parameters
            "first_name": {
                "type": "string",
                "description": "Contact's first name",
                "required": False,
                "group": "Contact Data",
                "validation": {
                    "maxLength": 100
                }
            },
            "last_name": {
                "type": "string",
                "description": "Contact's last name",
                "required": False,
                "group": "Contact Data",
                "validation": {
                    "maxLength": 100
                }
            },
            "email_address": {
                "type": "string",
                "description": "Contact's email address",
                "required": False,
                "group": "Contact Data",
                "validation": {
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "message": "Must be a valid email address"
                }
            },
            "phone": {
                "type": "string",
                "description": "Contact's phone number",
                "required": False,
                "group": "Contact Data",
                "validation": {
                    "pattern": "^\\+?[\\d\\s\\-\\(\\)]{10,}$",
                    "message": "Must be a valid phone number"
                }
            },
            "company": {
                "type": "string",
                "description": "Contact's company name",
                "required": False,
                "group": "Contact Data",
                "validation": {
                    "maxLength": 200
                }
            },
            "title": {
                "type": "string",
                "description": "Contact's job title",
                "required": False,
                "group": "Contact Data",
                "validation": {
                    "maxLength": 100
                }
            },
            "website": {
                "type": "string",
                "description": "Contact's website URL",
                "required": False,
                "group": "Contact Data",
                "validation": {
                    "pattern": "^https?://.*$",
                    "message": "Must be a valid URL starting with http:// or https://"
                }
            },
            "address": {
                "type": "string",
                "description": "Contact's address",
                "required": False,
                "group": "Contact Data",
                "validation": {
                    "maxLength": 500
                }
            },
            "lead_score": {
                "type": "integer",
                "description": "Contact's lead score",
                "required": False,
                "group": "Contact Data",
                "validation": {
                    "minimum": 0,
                    "maximum": 100
                }
            },
            "tags": {
                "type": "array",
                "description": "Array of tags to assign",
                "required": False,
                "group": "Contact Data",
                "validation": {
                    "maxItems": 20,
                    "items": {"type": "string", "maxLength": 50}
                }
            },
            "properties": {
                "type": "object",
                "description": "Custom properties object",
                "required": False,
                "group": "Contact Data"
            },
            # Company parameters
            "company_name": {
                "type": "string",
                "description": "Company name",
                "required": False,
                "group": "Company Data",
                "validation": {
                    "maxLength": 200
                }
            },
            "company_url": {
                "type": "string",
                "description": "Company website URL",
                "required": False,
                "group": "Company Data",
                "validation": {
                    "pattern": "^https?://.*$",
                    "message": "Must be a valid URL starting with http:// or https://"
                }
            },
            "company_phone": {
                "type": "string",
                "description": "Company phone number",
                "required": False,
                "group": "Company Data",
                "validation": {
                    "pattern": "^\\+?[\\d\\s\\-\\(\\)]{10,}$",
                    "message": "Must be a valid phone number"
                }
            },
            "company_address": {
                "type": "string",
                "description": "Company address",
                "required": False,
                "group": "Company Data",
                "validation": {
                    "maxLength": 500
                }
            },
            # Deal parameters
            "deal_name": {
                "type": "string",
                "description": "Deal name",
                "required": False,
                "group": "Deal Data",
                "validation": {
                    "maxLength": 200
                }
            },
            "deal_value": {
                "type": "number",
                "description": "Deal value/amount",
                "required": False,
                "group": "Deal Data",
                "validation": {
                    "minimum": 0
                }
            },
            "probability": {
                "type": "number",
                "description": "Deal probability (0-100)",
                "required": False,
                "group": "Deal Data",
                "validation": {
                    "minimum": 0,
                    "maximum": 100
                }
            },
            "close_date": {
                "type": "string",
                "description": "Deal close date (ISO format)",
                "required": False,
                "group": "Deal Data",
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.*$",
                    "message": "Must be in ISO 8601 format (YYYY-MM-DDTHH:mm:ss)"
                }
            },
            "milestone": {
                "type": "string",
                "description": "Deal milestone/stage",
                "required": False,
                "group": "Deal Data",
                "validation": {
                    "maxLength": 100
                }
            },
            # Task parameters
            "task_subject": {
                "type": "string",
                "description": "Task subject/title",
                "required": False,
                "group": "Task Data",
                "validation": {
                    "maxLength": 200
                }
            },
            "task_type": {
                "type": "string",
                "description": "Task type",
                "required": False,
                "group": "Task Data",
                "validation": {
                    "enum": ["CALL", "EMAIL", "FOLLOW_UP", "MEETING", "MILESTONE", "TWEET", "OTHER"]
                }
            },
            "task_priority": {
                "type": "string",
                "description": "Task priority level",
                "required": False,
                "group": "Task Data",
                "validation": {
                    "enum": ["HIGH", "NORMAL", "LOW"]
                }
            },
            "task_status": {
                "type": "string",
                "description": "Task status",
                "required": False,
                "group": "Task Data",
                "validation": {
                    "enum": ["YET_TO_START", "IN_PROGRESS", "COMPLETED"]
                }
            },
            "due_date": {
                "type": "string",
                "description": "Task due date (ISO format)",
                "required": False,
                "group": "Task Data",
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.*$",
                    "message": "Must be in ISO 8601 format (YYYY-MM-DDTHH:mm:ss)"
                }
            },
            "task_description": {
                "type": "string",
                "description": "Task description",
                "required": False,
                "group": "Task Data",
                "validation": {
                    "maxLength": 1000
                }
            },
            # Additional parameters for other operations
            "note_subject": {
                "type": "string",
                "description": "Note subject/title",
                "required": False,
                "group": "Note Data",
                "validation": {
                    "maxLength": 200
                }
            },
            "note_description": {
                "type": "string",
                "description": "Note content/description",
                "required": False,
                "group": "Note Data",
                "validation": {
                    "maxLength": 5000
                }
            },
            "event_title": {
                "type": "string",
                "description": "Event title",
                "required": False,
                "group": "Event Data",
                "validation": {
                    "maxLength": 200
                }
            },
            "event_start_time": {
                "type": "string",
                "description": "Event start time (ISO format)",
                "required": False,
                "group": "Event Data",
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.*$",
                    "message": "Must be in ISO 8601 format (YYYY-MM-DDTHH:mm:ss)"
                }
            },
            "event_end_time": {
                "type": "string",
                "description": "Event end time (ISO format)",
                "required": False,
                "group": "Event Data",
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.*$",
                    "message": "Must be in ISO 8601 format (YYYY-MM-DDTHH:mm:ss)"
                }
            },
            "event_location": {
                "type": "string",
                "description": "Event location",
                "required": False,
                "group": "Event Data",
                "validation": {
                    "maxLength": 500
                }
            },
            "event_description": {
                "type": "string",
                "description": "Event description",
                "required": False,
                "group": "Event Data",
                "validation": {
                    "maxLength": 1000
                }
            },
            # Campaign parameters
            "campaign_name": {
                "type": "string",
                "description": "Campaign name",
                "required": False,
                "group": "Campaign Data",
                "validation": {
                    "maxLength": 200
                }
            },
            "campaign_type": {
                "type": "string",
                "description": "Campaign type",
                "required": False,
                "group": "Campaign Data",
                "validation": {
                    "enum": ["EMAIL", "SMS", "PUSH", "WEBHOOK"]
                }
            },
            "campaign_subject": {
                "type": "string",
                "description": "Campaign subject line",
                "required": False,
                "group": "Campaign Data",
                "validation": {
                    "maxLength": 200
                }
            },
            "campaign_content": {
                "type": "string",
                "description": "Campaign content/body",
                "required": False,
                "group": "Campaign Data",
                "validation": {
                    "maxLength": 10000
                }
            },
            # Search and filtering parameters
            "search_query": {
                "type": "string",
                "description": "Search query string",
                "required": False,
                "group": "Search",
                "validation": {
                    "maxLength": 500
                }
            },
            "page_size": {
                "type": "integer",
                "description": "Number of results per page",
                "required": False,
                "default": 20,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "cursor": {
                "type": "string",
                "description": "Pagination cursor for next page",
                "required": False,
                "group": "Pagination"
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful AgileCRM API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from AgileCRM API"},
                    "result": {"type": "object", "description": "Full API response data"},
                    "count": {"type": "integer", "description": "Number of items returned"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "AgileCRM error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "get_contacts": {
                "required_env_keys": ["AGILECRM_DOMAIN", "AGILECRM_EMAIL", "AGILECRM_API_KEY"],
                "optional_env_keys": []
            },
            "create_contact": {
                "required_env_keys": ["AGILECRM_DOMAIN", "AGILECRM_EMAIL", "AGILECRM_API_KEY"],
                "optional_env_keys": []
            }
        },
        
        # Error codes specific to AgileCRM
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid credentials or API key",
            "403": "Forbidden - Request not allowed",
            "404": "Not Found - Resource not found",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - AgileCRM server error",
            "502": "Bad Gateway - AgileCRM server temporarily unavailable",
            "503": "Service Unavailable - AgileCRM server overloaded"
        }
    }
    
    # Enhanced operation definitions with ALL 13 features - All 53 operations
    OPERATIONS = {
        # CONTACT OPERATIONS (6 operations)
        "get_contacts": {
            "method": "GET",
            "endpoint": "/contacts",
            "required_params": [],
            "optional_params": ["page_size", "cursor"],
            "query_parameters": ["page_size", "cursor"],
            "display_name": "Get Contacts",
            "description": "Retrieve list of contacts from AgileCRM",
            "group": "Contacts",
            "tags": ["contacts", "list", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            # 1. Operation-specific output schema
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "contacts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "type": {"type": "string"},
                                    "properties": {"type": "array"},
                                    "tags": {"type": "array"},
                                    "created_time": {"type": "integer"},
                                    "updated_time": {"type": "integer"}
                                }
                            }
                        },
                        "count": {"type": "integer"}
                    }
                }
            },
            
            # 6. Pagination support
            "pagination": {
                "type": "cursor",
                "cursor_param": "cursor",
                "size_param": "page_size",
                "default_size": 20,
                "max_size": 100
            },
            
            # 5. Rate limiting configuration
            "rate_limiting": {
                "requests_per_minute": 60,
                "cost_per_request": 1
            },
            
            # 7. Error handling
            "error_handling": {
                "retry_codes": [429, 500, 502, 503],
                "max_retries": 3,
                "backoff": "exponential"
            },
            
            # 8. Field mapping
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {
                    "created_time": "format_timestamp",
                    "updated_time": "format_timestamp"
                }
            },
            
            # 12. Caching strategy
            "caching_strategy": {
                "enabled": True,
                "ttl": 300,
                "cache_key": "contacts:{domain}:{page_size}:{cursor}"
            },
            
            "examples": [
                {
                    "name": "List all contacts",
                    "description": "Get all contacts with default pagination",
                    "input": {
                        "page_size": 20
                    }
                }
            ]
        },
        
        "get_contact": {
            "method": "GET",
            "endpoint": "/contacts/{contact_id}",
            "required_params": ["contact_id"],
            "optional_params": [],
            "path_parameters": ["contact_id"],
            "display_name": "Get Contact",
            "description": "Retrieve a specific contact by ID",
            "group": "Contacts",
            "tags": ["contact", "detail", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "contact": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "type": {"type": "string"},
                                "properties": {"type": "array"},
                                "tags": {"type": "array"}
                            }
                        }
                    }
                }
            },
            
            # 4. Validation rules
            "validation_rules": {
                "contact_id": {
                    "pattern": "",
                    "message": "Contact ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Get specific contact",
                    "description": "Retrieve contact details by ID",
                    "input": {
                        "contact_id": 123456
                    }
                }
            ]
        },
        
        "create_contact": {
            "method": "POST",
            "endpoint": "/contacts",
            "required_params": [],
            "optional_params": ["first_name", "last_name", "email_address", "phone", "company", "title", "website", "address", "lead_score", "tags", "properties"],
            "body_parameters": ["first_name", "last_name", "email_address", "phone", "company", "title", "website", "address", "lead_score", "tags", "properties"],
            "display_name": "Create Contact",
            "description": "Create a new contact in AgileCRM",
            "group": "Contacts",
            "tags": ["contact", "create", "crm"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "contact": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "properties": {"type": "array"}
                            }
                        }
                    }
                }
            },
            
            # 3. Parameter dependencies
            "parameter_dependencies": [
                {
                    "require_one_of": ["first_name", "last_name", "email_address"],
                    "message": "At least one of first_name, last_name, or email_address is required"
                }
            ],
            
            "validation_rules": {
                "email_address": {
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "message": "Must be a valid email address",
                    "pattern_type": "regex",
                    "required": False
                },
                "lead_score": {
                    "pattern": "",
                    "message": "Lead score must be between 0 and 100",
                    "pattern_type": "custom",
                    "min_value": 0,
                    "max_value": 100,
                    "required": False
                }
            },
            
            # 8. Field mapping for contact creation
            "field_mapping": {
                "input_transforms": {
                    "email_address": "validate_email",
                    "phone": "validate_phone"
                },
                "output_transforms": {},
                "body_structure": "contact_properties"
            },
            
            "examples": [
                {
                    "name": "Create basic contact",
                    "description": "Create a contact with basic information",
                    "input": {
                        "first_name": "John",
                        "last_name": "Doe",
                        "email_address": "john.doe@example.com",
                        "phone": "+1-555-123-4567",
                        "company": "Example Corp"
                    }
                }
            ]
        },
        
        "update_contact": {
            "method": "PUT",
            "endpoint": "/contacts/edit-properties",
            "required_params": ["contact_id"],
            "optional_params": ["first_name", "last_name", "email_address", "phone", "company", "title", "website", "address", "lead_score"],
            "body_parameters": ["contact_id", "first_name", "last_name", "email_address", "phone", "company", "title", "website", "address", "lead_score"],
            "display_name": "Update Contact",
            "description": "Update an existing contact's information",
            "group": "Contacts",
            "tags": ["contact", "update", "crm"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "contact": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "contact_id": {
                    "pattern": "",
                    "message": "Contact ID is required for updates",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Update contact email",
                    "description": "Update a contact's email address",
                    "input": {
                        "contact_id": 123456,
                        "email_address": "newemail@example.com"
                    }
                }
            ]
        },
        
        "delete_contact": {
            "method": "DELETE",
            "endpoint": "/contacts/{contact_id}",
            "required_params": ["contact_id"],
            "optional_params": [],
            "path_parameters": ["contact_id"],
            "display_name": "Delete Contact",
            "description": "Delete a contact from AgileCRM",
            "group": "Contacts",
            "tags": ["contact", "delete", "crm"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "contact_id": {
                    "pattern": "",
                    "message": "Contact ID is required for deletion",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Delete contact",
                    "description": "Delete a specific contact by ID",
                    "input": {
                        "contact_id": 123456
                    }
                }
            ]
        },
        
        "search_contacts": {
            "method": "GET",
            "endpoint": "/search",
            "required_params": ["search_query"],
            "optional_params": ["page_size"],
            "query_parameters": ["search_query", "page_size", "type"],
            "display_name": "Search Contacts",
            "description": "Search contacts by query string",
            "group": "Contacts",
            "tags": ["contact", "search", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "contacts": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "search_query": {
                    "pattern": "",
                    "message": "Search query is required and must be at least 2 characters",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 500,
                    "required": True
                }
            },
            
            # Override query parameters to include type=PERSON
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "query_defaults": {
                    "type": "PERSON"
                }
            },
            
            "examples": [
                {
                    "name": "Search by email",
                    "description": "Search contacts by email address",
                    "input": {
                        "search_query": "john@example.com"
                    }
                }
            ]
        },
        
        # COMPANY OPERATIONS (5 operations)
        "get_companies": {
            "method": "GET",
            "endpoint": "/contacts/companies/list",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Companies",
            "description": "Retrieve list of companies from AgileCRM",
            "group": "Companies",
            "tags": ["companies", "list", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "companies": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            "examples": [
                {
                    "name": "List all companies",
                    "description": "Get all companies from AgileCRM",
                    "input": {}
                }
            ]
        },
        
        "get_company": {
            "method": "GET",
            "endpoint": "/contacts/{company_id}",
            "required_params": ["company_id"],
            "optional_params": [],
            "path_parameters": ["company_id"],
            "display_name": "Get Company",
            "description": "Retrieve a specific company by ID",
            "group": "Companies",
            "tags": ["company", "detail", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "company": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "company_id": {
                    "pattern": "",
                    "message": "Company ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Get specific company",
                    "description": "Retrieve company details by ID",
                    "input": {
                        "company_id": 123456
                    }
                }
            ]
        },
        
        "create_company": {
            "method": "POST",
            "endpoint": "/contacts",
            "required_params": ["company_name"],
            "optional_params": ["company_url", "company_phone", "company_address"],
            "body_parameters": ["company_name", "company_url", "company_phone", "company_address"],
            "display_name": "Create Company",
            "description": "Create a new company in AgileCRM",
            "group": "Companies",
            "tags": ["company", "create", "crm"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "company": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "company_name": {
                    "pattern": "",
                    "message": "Company name is required and must be at least 2 characters",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 200,
                    "required": True
                }
            },
            
            # Company-specific field mapping
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "body_structure": "company_properties",
                "type_override": "COMPANY"
            },
            
            "examples": [
                {
                    "name": "Create basic company",
                    "description": "Create a company with basic information",
                    "input": {
                        "company_name": "Acme Corporation",
                        "company_url": "https://acme.com",
                        "company_phone": "+1-555-123-4567"
                    }
                }
            ]
        },
        
        "update_company": {
            "method": "PUT",
            "endpoint": "/contacts/edit-properties",
            "required_params": ["company_id"],
            "optional_params": ["company_name", "company_url", "company_phone", "company_address"],
            "body_parameters": ["company_id", "company_name", "company_url", "company_phone", "company_address"],
            "display_name": "Update Company",
            "description": "Update an existing company's information",
            "group": "Companies",
            "tags": ["company", "update", "crm"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "company": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "company_id": {
                    "pattern": "",
                    "message": "Company ID is required for updates",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "body_structure": "company_properties",
                "type_override": "COMPANY"
            },
            
            "examples": [
                {
                    "name": "Update company website",
                    "description": "Update a company's website URL",
                    "input": {
                        "company_id": 123456,
                        "company_url": "https://newwebsite.com"
                    }
                }
            ]
        },
        
        "delete_company": {
            "method": "DELETE",
            "endpoint": "/contacts/{company_id}",
            "required_params": ["company_id"],
            "optional_params": [],
            "path_parameters": ["company_id"],
            "display_name": "Delete Company",
            "description": "Delete a company from AgileCRM",
            "group": "Companies",
            "tags": ["company", "delete", "crm"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "company_id": {
                    "pattern": "",
                    "message": "Company ID is required for deletion",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Delete company",
                    "description": "Delete a specific company by ID",
                    "input": {
                        "company_id": 123456
                    }
                }
            ]
        },
        
        # DEAL OPERATIONS (5 operations)
        "get_deals": {
            "method": "GET",
            "endpoint": "/opportunity",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Deals",
            "description": "Retrieve list of deals from AgileCRM",
            "group": "Deals",
            "tags": ["deals", "opportunities", "sales"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "deals": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            "examples": [
                {
                    "name": "List all deals",
                    "description": "Get all deals from AgileCRM",
                    "input": {}
                }
            ]
        },
        
        "get_deal": {
            "method": "GET",
            "endpoint": "/opportunity/{deal_id}",
            "required_params": ["deal_id"],
            "optional_params": [],
            "path_parameters": ["deal_id"],
            "display_name": "Get Deal",
            "description": "Retrieve a specific deal by ID",
            "group": "Deals",
            "tags": ["deal", "opportunity", "sales"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "deal": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "deal_id": {
                    "pattern": "",
                    "message": "Deal ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Get specific deal",
                    "description": "Retrieve deal details by ID",
                    "input": {
                        "deal_id": 123456
                    }
                }
            ]
        },
        
        "create_deal": {
            "method": "POST",
            "endpoint": "/opportunity",
            "required_params": ["deal_name"],
            "optional_params": ["deal_value", "probability", "close_date", "milestone", "contact_id"],
            "body_parameters": ["deal_name", "deal_value", "probability", "close_date", "milestone", "contact_id"],
            "display_name": "Create Deal",
            "description": "Create a new deal in AgileCRM",
            "group": "Deals",
            "tags": ["deal", "opportunity", "create", "sales"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "deal": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "deal_name": {
                    "pattern": "",
                    "message": "Deal name is required and must be at least 2 characters",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 200,
                    "required": True
                },
                "probability": {
                    "pattern": "",
                    "message": "Probability must be between 0 and 100",
                    "pattern_type": "custom",
                    "min_value": 0,
                    "max_value": 100,
                    "required": False
                },
                "deal_value": {
                    "pattern": "",
                    "message": "Deal value must be a positive number",
                    "pattern_type": "custom",
                    "min_value": 0,
                    "required": False
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "close_date": "parse_iso_date"
                },
                "output_transforms": {},
                "field_aliases": {
                    "deal_name": "name",
                    "deal_value": "expected_value",
                    "contact_id": "contact_ids"
                }
            },
            
            "examples": [
                {
                    "name": "Create basic deal",
                    "description": "Create a deal with basic information",
                    "input": {
                        "deal_name": "New Business Opportunity",
                        "deal_value": 50000,
                        "probability": 75,
                        "close_date": "2025-12-31T23:59:59Z"
                    }
                }
            ]
        },
        
        "update_deal": {
            "method": "PUT",
            "endpoint": "/opportunity/partial-update",
            "required_params": ["deal_id"],
            "optional_params": ["deal_name", "deal_value", "probability", "close_date", "milestone"],
            "body_parameters": ["deal_id", "deal_name", "deal_value", "probability", "close_date", "milestone"],
            "display_name": "Update Deal",
            "description": "Update an existing deal's information",
            "group": "Deals",
            "tags": ["deal", "opportunity", "update", "sales"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "deal": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "deal_id": {
                    "pattern": "",
                    "message": "Deal ID is required for updates",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "close_date": "parse_iso_date"
                },
                "output_transforms": {},
                "field_aliases": {
                    "deal_name": "name",
                    "deal_value": "expected_value"
                }
            },
            
            "examples": [
                {
                    "name": "Update deal value",
                    "description": "Update a deal's value and probability",
                    "input": {
                        "deal_id": 123456,
                        "deal_value": 75000,
                        "probability": 85
                    }
                }
            ]
        },
        
        "delete_deal": {
            "method": "DELETE",
            "endpoint": "/opportunity/{deal_id}",
            "required_params": ["deal_id"],
            "optional_params": [],
            "path_parameters": ["deal_id"],
            "display_name": "Delete Deal",
            "description": "Delete a deal from AgileCRM",
            "group": "Deals",
            "tags": ["deal", "opportunity", "delete", "sales"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "deal_id": {
                    "pattern": "",
                    "message": "Deal ID is required for deletion",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Delete deal",
                    "description": "Delete a specific deal by ID",
                    "input": {
                        "deal_id": 123456
                    }
                }
            ]
        },
        
        # TASK OPERATIONS (5 operations)
        "get_tasks": {
            "method": "GET",
            "endpoint": "/tasks",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Tasks",
            "description": "Retrieve list of tasks from AgileCRM",
            "group": "Tasks",
            "tags": ["tasks", "activities", "productivity"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "tasks": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            "examples": [
                {
                    "name": "List all tasks",
                    "description": "Get all tasks from AgileCRM",
                    "input": {}
                }
            ]
        },
        
        "get_task": {
            "method": "GET",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id"],
            "optional_params": [],
            "path_parameters": ["task_id"],
            "display_name": "Get Task",
            "description": "Retrieve a specific task by ID",
            "group": "Tasks",
            "tags": ["task", "activity", "productivity"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "task": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "task_id": {
                    "pattern": "",
                    "message": "Task ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Get specific task",
                    "description": "Retrieve task details by ID",
                    "input": {
                        "task_id": 123456
                    }
                }
            ]
        },
        
        "create_task": {
            "method": "POST",
            "endpoint": "/tasks",
            "required_params": ["task_subject"],
            "optional_params": ["task_type", "task_priority", "task_status", "due_date", "task_description", "contact_id"],
            "body_parameters": ["task_subject", "task_type", "task_priority", "task_status", "due_date", "task_description", "contact_id"],
            "display_name": "Create Task",
            "description": "Create a new task in AgileCRM",
            "group": "Tasks",
            "tags": ["task", "activity", "create", "productivity"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "task": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "task_subject": {
                    "pattern": "",
                    "message": "Task subject is required and must be at least 2 characters",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 200,
                    "required": True
                },
                "task_type": {
                    "pattern": "",
                    "message": "Task type must be one of the allowed values",
                    "pattern_type": "custom",
                    "enum": ["CALL", "EMAIL", "FOLLOW_UP", "MEETING", "MILESTONE", "TWEET", "OTHER"],
                    "required": False
                },
                "task_priority": {
                    "pattern": "",
                    "message": "Task priority must be HIGH, NORMAL, or LOW",
                    "pattern_type": "custom",
                    "enum": ["HIGH", "NORMAL", "LOW"],
                    "required": False
                },
                "task_status": {
                    "pattern": "",
                    "message": "Task status must be a valid status",
                    "pattern_type": "custom",
                    "enum": ["YET_TO_START", "IN_PROGRESS", "COMPLETED"],
                    "required": False
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "due_date": "parse_iso_date_to_timestamp"
                },
                "output_transforms": {},
                "field_aliases": {
                    "task_subject": "subject",
                    "task_type": "type",
                    "task_priority": "priority_type",
                    "task_status": "status",
                    "task_description": "taskDescription",
                    "contact_id": "contacts"
                }
            },
            
            "examples": [
                {
                    "name": "Create follow-up task",
                    "description": "Create a follow-up task for a contact",
                    "input": {
                        "task_subject": "Follow up with client",
                        "task_type": "FOLLOW_UP",
                        "task_priority": "HIGH",
                        "due_date": "2025-09-01T10:00:00Z",
                        "task_description": "Follow up on proposal discussion",
                        "contact_id": 123456
                    }
                }
            ]
        },
        
        "update_task": {
            "method": "PUT",
            "endpoint": "/tasks/partial-update",
            "required_params": ["task_id"],
            "optional_params": ["task_subject", "task_type", "task_priority", "task_status", "due_date", "task_description"],
            "body_parameters": ["task_id", "task_subject", "task_type", "task_priority", "task_status", "due_date", "task_description"],
            "display_name": "Update Task",
            "description": "Update an existing task's information",
            "group": "Tasks",
            "tags": ["task", "activity", "update", "productivity"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "task": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "task_id": {
                    "pattern": "",
                    "message": "Task ID is required for updates",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "due_date": "parse_iso_date_to_timestamp"
                },
                "output_transforms": {},
                "field_aliases": {
                    "task_subject": "subject",
                    "task_type": "type",
                    "task_priority": "priority_type",
                    "task_status": "status",
                    "task_description": "taskDescription"
                }
            },
            
            "examples": [
                {
                    "name": "Mark task completed",
                    "description": "Update a task's status to completed",
                    "input": {
                        "task_id": 123456,
                        "task_status": "COMPLETED"
                    }
                }
            ]
        },
        
        "delete_task": {
            "method": "DELETE",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id"],
            "optional_params": [],
            "path_parameters": ["task_id"],
            "display_name": "Delete Task",
            "description": "Delete a task from AgileCRM",
            "group": "Tasks",
            "tags": ["task", "activity", "delete", "productivity"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "task_id": {
                    "pattern": "",
                    "message": "Task ID is required for deletion",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Delete task",
                    "description": "Delete a specific task by ID",
                    "input": {
                        "task_id": 123456
                    }
                }
            ]
        },
        
        # NOTE OPERATIONS (5 operations)
        "get_notes": {
            "method": "GET",
            "endpoint": "/notes",
            "required_params": [],
            "optional_params": ["contact_id"],
            "query_parameters": ["contact_id"],
            "display_name": "Get Notes",
            "description": "Retrieve list of notes from AgileCRM",
            "group": "Notes",
            "tags": ["notes", "comments", "content"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "notes": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            # Conditional endpoint based on contact_id
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "conditional_endpoint": {
                    "when_param": "contact_id",
                    "endpoint_template": "/contacts/{contact_id}/notes"
                }
            },
            
            "examples": [
                {
                    "name": "List all notes",
                    "description": "Get all notes from AgileCRM",
                    "input": {}
                },
                {
                    "name": "List contact notes",
                    "description": "Get notes for a specific contact",
                    "input": {
                        "contact_id": 123456
                    }
                }
            ]
        },
        
        "get_note": {
            "method": "GET",
            "endpoint": "/notes/{note_id}",
            "required_params": ["note_id"],
            "optional_params": [],
            "path_parameters": ["note_id"],
            "display_name": "Get Note",
            "description": "Retrieve a specific note by ID",
            "group": "Notes",
            "tags": ["note", "comment", "content"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "note": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "note_id": {
                    "pattern": "",
                    "message": "Note ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Get specific note",
                    "description": "Retrieve note details by ID",
                    "input": {
                        "note_id": 123456
                    }
                }
            ]
        },
        
        "create_note": {
            "method": "POST",
            "endpoint": "/notes",
            "required_params": [],
            "optional_params": ["note_subject", "note_description", "contact_id"],
            "body_parameters": ["note_subject", "note_description", "contact_id"],
            "display_name": "Create Note",
            "description": "Create a new note in AgileCRM",
            "group": "Notes",
            "tags": ["note", "comment", "create", "content"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "note": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "parameter_dependencies": [
                {
                    "require_one_of": ["note_subject", "note_description"],
                    "message": "Either note subject or description is required"
                }
            ],
            
            "validation_rules": {
                "note_subject": {
                    "pattern": "",
                    "message": "Note subject must be at least 2 characters if provided",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 200,
                    "required": False
                },
                "note_description": {
                    "pattern": "",
                    "message": "Note description must be at least 2 characters if provided",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 5000,
                    "required": False
                }
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "field_aliases": {
                    "note_subject": "subject",
                    "note_description": "description",
                    "contact_id": "contact_ids"
                }
            },
            
            "examples": [
                {
                    "name": "Create contact note",
                    "description": "Create a note for a specific contact",
                    "input": {
                        "note_subject": "Initial consultation",
                        "note_description": "Discussed project requirements and timeline",
                        "contact_id": 123456
                    }
                }
            ]
        },
        
        "update_note": {
            "method": "PUT",
            "endpoint": "/notes/partial-update",
            "required_params": ["note_id"],
            "optional_params": ["note_subject", "note_description"],
            "body_parameters": ["note_id", "note_subject", "note_description"],
            "display_name": "Update Note",
            "description": "Update an existing note's information",
            "group": "Notes",
            "tags": ["note", "comment", "update", "content"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "note": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "note_id": {
                    "pattern": "",
                    "message": "Note ID is required for updates",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "field_aliases": {
                    "note_subject": "subject",
                    "note_description": "description"
                }
            },
            
            "examples": [
                {
                    "name": "Update note content",
                    "description": "Update a note's subject and description",
                    "input": {
                        "note_id": 123456,
                        "note_subject": "Updated consultation notes",
                        "note_description": "Added follow-up items and next steps"
                    }
                }
            ]
        },
        
        "delete_note": {
            "method": "DELETE",
            "endpoint": "/notes/{note_id}",
            "required_params": ["note_id"],
            "optional_params": [],
            "path_parameters": ["note_id"],
            "display_name": "Delete Note",
            "description": "Delete a note from AgileCRM",
            "group": "Notes",
            "tags": ["note", "comment", "delete", "content"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "note_id": {
                    "pattern": "",
                    "message": "Note ID is required for deletion",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Delete note",
                    "description": "Delete a specific note by ID",
                    "input": {
                        "note_id": 123456
                    }
                }
            ]
        },
        
        # EVENT OPERATIONS (5 operations)
        "get_events": {
            "method": "GET",
            "endpoint": "/events",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Events",
            "description": "Retrieve list of events from AgileCRM",
            "group": "Events",
            "tags": ["events", "calendar", "activities"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "events": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            "examples": [
                {
                    "name": "List all events",
                    "description": "Get all events from AgileCRM",
                    "input": {}
                }
            ]
        },
        
        "get_event": {
            "method": "GET",
            "endpoint": "/events/{event_id}",
            "required_params": ["event_id"],
            "optional_params": [],
            "path_parameters": ["event_id"],
            "display_name": "Get Event",
            "description": "Retrieve a specific event by ID",
            "group": "Events",
            "tags": ["event", "calendar", "activity"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "event": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "event_id": {
                    "pattern": "",
                    "message": "Event ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Get specific event",
                    "description": "Retrieve event details by ID",
                    "input": {
                        "event_id": 123456
                    }
                }
            ]
        },
        
        "create_event": {
            "method": "POST",
            "endpoint": "/events",
            "required_params": ["event_title"],
            "optional_params": ["event_start_time", "event_end_time", "event_location", "event_description", "contact_id"],
            "body_parameters": ["event_title", "event_start_time", "event_end_time", "event_location", "event_description", "contact_id"],
            "display_name": "Create Event",
            "description": "Create a new event in AgileCRM",
            "group": "Events",
            "tags": ["event", "calendar", "create", "activity"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "event": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "event_title": {
                    "pattern": "",
                    "message": "Event title is required and must be at least 2 characters",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 200,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "event_start_time": "parse_iso_date_to_timestamp",
                    "event_end_time": "parse_iso_date_to_timestamp"
                },
                "output_transforms": {},
                "field_aliases": {
                    "event_title": "title",
                    "event_start_time": "start_time",
                    "event_end_time": "end_time",
                    "event_location": "location",
                    "event_description": "description",
                    "contact_id": "contacts"
                }
            },
            
            "examples": [
                {
                    "name": "Create client meeting",
                    "description": "Create a meeting event with a client",
                    "input": {
                        "event_title": "Client Meeting - Project Discussion",
                        "event_start_time": "2025-09-01T14:00:00Z",
                        "event_end_time": "2025-09-01T15:00:00Z",
                        "event_location": "Conference Room A",
                        "event_description": "Discuss project timeline and deliverables",
                        "contact_id": 123456
                    }
                }
            ]
        },
        
        "update_event": {
            "method": "PUT",
            "endpoint": "/events/partial-update",
            "required_params": ["event_id"],
            "optional_params": ["event_title", "event_start_time", "event_end_time", "event_location", "event_description"],
            "body_parameters": ["event_id", "event_title", "event_start_time", "event_end_time", "event_location", "event_description"],
            "display_name": "Update Event",
            "description": "Update an existing event's information",
            "group": "Events",
            "tags": ["event", "calendar", "update", "activity"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "event": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "event_id": {
                    "pattern": "",
                    "message": "Event ID is required for updates",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "event_start_time": "parse_iso_date_to_timestamp",
                    "event_end_time": "parse_iso_date_to_timestamp"
                },
                "output_transforms": {},
                "field_aliases": {
                    "event_title": "title",
                    "event_start_time": "start_time",
                    "event_end_time": "end_time",
                    "event_location": "location",
                    "event_description": "description"
                }
            },
            
            "examples": [
                {
                    "name": "Update event time",
                    "description": "Update an event's start and end times",
                    "input": {
                        "event_id": 123456,
                        "event_start_time": "2025-09-01T15:00:00Z",
                        "event_end_time": "2025-09-01T16:00:00Z"
                    }
                }
            ]
        },
        
        "delete_event": {
            "method": "DELETE",
            "endpoint": "/events/{event_id}",
            "required_params": ["event_id"],
            "optional_params": [],
            "path_parameters": ["event_id"],
            "display_name": "Delete Event",
            "description": "Delete an event from AgileCRM",
            "group": "Events",
            "tags": ["event", "calendar", "delete", "activity"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "event_id": {
                    "pattern": "",
                    "message": "Event ID is required for deletion",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Delete event",
                    "description": "Delete a specific event by ID",
                    "input": {
                        "event_id": 123456
                    }
                }
            ]
        },
        
        # CAMPAIGN OPERATIONS (5 operations)
        "get_campaigns": {
            "method": "GET",
            "endpoint": "/campaigns",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Campaigns",
            "description": "Retrieve list of campaigns from AgileCRM",
            "group": "Campaigns",
            "tags": ["campaigns", "marketing", "automation"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "campaigns": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            "examples": [
                {
                    "name": "List all campaigns",
                    "description": "Get all campaigns from AgileCRM",
                    "input": {}
                }
            ]
        },
        
        "get_campaign": {
            "method": "GET",
            "endpoint": "/campaigns/{campaign_id}",
            "required_params": ["campaign_id"],
            "optional_params": [],
            "path_parameters": ["campaign_id"],
            "display_name": "Get Campaign",
            "description": "Retrieve a specific campaign by ID",
            "group": "Campaigns",
            "tags": ["campaign", "marketing", "automation"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "campaign": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "campaign_id": {
                    "pattern": "",
                    "message": "Campaign ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Get specific campaign",
                    "description": "Retrieve campaign details by ID",
                    "input": {
                        "campaign_id": 123456
                    }
                }
            ]
        },
        
        "create_campaign": {
            "method": "POST",
            "endpoint": "/campaigns",
            "required_params": ["campaign_name"],
            "optional_params": ["campaign_type", "campaign_subject", "campaign_content"],
            "body_parameters": ["campaign_name", "campaign_type", "campaign_subject", "campaign_content"],
            "display_name": "Create Campaign",
            "description": "Create a new campaign in AgileCRM",
            "group": "Campaigns",
            "tags": ["campaign", "marketing", "create", "automation"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "campaign": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "campaign_name": {
                    "pattern": "",
                    "message": "Campaign name is required and must be at least 2 characters",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 200,
                    "required": True
                },
                "campaign_type": {
                    "pattern": "",
                    "message": "Campaign type must be one of the allowed values",
                    "pattern_type": "custom",
                    "enum": ["EMAIL", "SMS", "PUSH", "WEBHOOK"],
                    "required": False
                }
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "field_aliases": {
                    "campaign_name": "name",
                    "campaign_type": "type",
                    "campaign_subject": "subject",
                    "campaign_content": "content"
                }
            },
            
            "examples": [
                {
                    "name": "Create email campaign",
                    "description": "Create a new email marketing campaign",
                    "input": {
                        "campaign_name": "Summer Sale 2025",
                        "campaign_type": "EMAIL",
                        "campaign_subject": "Don't Miss Our Summer Sale!",
                        "campaign_content": "Save up to 50% on selected items during our summer sale."
                    }
                }
            ]
        },
        
        "update_campaign": {
            "method": "PUT",
            "endpoint": "/campaigns/partial-update",
            "required_params": ["campaign_id"],
            "optional_params": ["campaign_name", "campaign_type", "campaign_subject", "campaign_content"],
            "body_parameters": ["campaign_id", "campaign_name", "campaign_type", "campaign_subject", "campaign_content"],
            "display_name": "Update Campaign",
            "description": "Update an existing campaign's information",
            "group": "Campaigns",
            "tags": ["campaign", "marketing", "update", "automation"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "campaign": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "campaign_id": {
                    "pattern": "",
                    "message": "Campaign ID is required for updates",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "field_aliases": {
                    "campaign_name": "name",
                    "campaign_type": "type",
                    "campaign_subject": "subject",
                    "campaign_content": "content"
                }
            },
            
            "examples": [
                {
                    "name": "Update campaign content",
                    "description": "Update a campaign's subject and content",
                    "input": {
                        "campaign_id": 123456,
                        "campaign_subject": "Extended Summer Sale!",
                        "campaign_content": "Due to popular demand, we've extended our summer sale by one week!"
                    }
                }
            ]
        },
        
        "delete_campaign": {
            "method": "DELETE",
            "endpoint": "/campaigns/{campaign_id}",
            "required_params": ["campaign_id"],
            "optional_params": [],
            "path_parameters": ["campaign_id"],
            "display_name": "Delete Campaign",
            "description": "Delete a campaign from AgileCRM",
            "group": "Campaigns",
            "tags": ["campaign", "marketing", "delete", "automation"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "campaign_id": {
                    "pattern": "",
                    "message": "Campaign ID is required for deletion",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Delete campaign",
                    "description": "Delete a specific campaign by ID",
                    "input": {
                        "campaign_id": 123456
                    }
                }
            ]
        },
        
        # TRACK OPERATIONS (4 operations)
        "get_tracks": {
            "method": "GET",
            "endpoint": "/tracks",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Tracks",
            "description": "Retrieve list of tracks from AgileCRM",
            "group": "Tracks",
            "tags": ["tracks", "automation", "workflows"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "tracks": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            "examples": [
                {
                    "name": "List all tracks",
                    "description": "Get all automation tracks from AgileCRM",
                    "input": {}
                }
            ]
        },
        
        "create_track": {
            "method": "POST",
            "endpoint": "/tracks",
            "required_params": ["track_name"],
            "optional_params": ["track_description"],
            "body_parameters": ["track_name", "track_description"],
            "display_name": "Create Track",
            "description": "Create a new automation track in AgileCRM",
            "group": "Tracks",
            "tags": ["track", "automation", "create", "workflow"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "track": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "track_name": {
                    "pattern": "",
                    "message": "Track name is required and must be at least 2 characters",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 200,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "field_aliases": {
                    "track_name": "name",
                    "track_description": "description"
                }
            },
            
            "examples": [
                {
                    "name": "Create lead nurturing track",
                    "description": "Create an automation track for lead nurturing",
                    "input": {
                        "track_name": "Lead Nurturing Sequence",
                        "track_description": "Automated sequence to nurture new leads"
                    }
                }
            ]
        },
        
        "update_track": {
            "method": "PUT",
            "endpoint": "/tracks/{track_id}",
            "required_params": ["track_id"],
            "optional_params": ["track_name", "track_description"],
            "path_parameters": ["track_id"],
            "body_parameters": ["track_name", "track_description"],
            "display_name": "Update Track",
            "description": "Update an existing track's information",
            "group": "Tracks",
            "tags": ["track", "automation", "update", "workflow"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "track": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "track_id": {
                    "pattern": "",
                    "message": "Track ID is required for updates",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "field_aliases": {
                    "track_name": "name",
                    "track_description": "description"
                }
            },
            
            "examples": [
                {
                    "name": "Update track description",
                    "description": "Update a track's name and description",
                    "input": {
                        "track_id": 123456,
                        "track_name": "Updated Lead Nurturing",
                        "track_description": "Enhanced lead nurturing with new steps"
                    }
                }
            ]
        },
        
        "delete_track": {
            "method": "DELETE",
            "endpoint": "/tracks/{track_id}",
            "required_params": ["track_id"],
            "optional_params": [],
            "path_parameters": ["track_id"],
            "display_name": "Delete Track",
            "description": "Delete a track from AgileCRM",
            "group": "Tracks",
            "tags": ["track", "automation", "delete", "workflow"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "track_id": {
                    "pattern": "",
                    "message": "Track ID is required for deletion",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Delete track",
                    "description": "Delete a specific track by ID",
                    "input": {
                        "track_id": 123456
                    }
                }
            ]
        },
        
        # DOCUMENT OPERATIONS (3 operations)
        "get_documents": {
            "method": "GET",
            "endpoint": "/documents",
            "required_params": [],
            "optional_params": ["contact_id"],
            "query_parameters": ["contact_id"],
            "display_name": "Get Documents",
            "description": "Retrieve list of documents from AgileCRM",
            "group": "Documents",
            "tags": ["documents", "files", "attachments"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "documents": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            # Conditional endpoint for contact-specific documents
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "conditional_endpoint": {
                    "when_param": "contact_id",
                    "endpoint_template": "/contacts/{contact_id}/documents"
                }
            },
            
            "examples": [
                {
                    "name": "List all documents",
                    "description": "Get all documents from AgileCRM",
                    "input": {}
                },
                {
                    "name": "List contact documents",
                    "description": "Get documents for a specific contact",
                    "input": {
                        "contact_id": 123456
                    }
                }
            ]
        },
        
        "upload_document": {
            "method": "POST",
            "endpoint": "/documents",
            "required_params": ["document_name"],
            "optional_params": ["document_url", "document_content", "contact_id"],
            "body_parameters": ["document_name", "document_url", "document_content", "contact_id"],
            "display_name": "Upload Document",
            "description": "Upload a new document to AgileCRM",
            "group": "Documents",
            "tags": ["document", "file", "upload", "attachment"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "document": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "document_name": {
                    "pattern": "",
                    "message": "Document name is required and must be at least 2 characters",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 200,
                    "required": True
                }
            },
            
            "parameter_dependencies": [
                {
                    "require_one_of": ["document_url", "document_content"],
                    "message": "Either document_url or document_content is required"
                }
            ],
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "field_aliases": {
                    "document_name": "name",
                    "document_url": "url",
                    "document_content": "content",
                    "contact_id": "contact_id"
                }
            },
            
            "examples": [
                {
                    "name": "Upload document from URL",
                    "description": "Upload a document by providing its URL",
                    "input": {
                        "document_name": "Project Proposal.pdf",
                        "document_url": "https://example.com/proposal.pdf",
                        "contact_id": 123456
                    }
                }
            ]
        },
        
        "delete_document": {
            "method": "DELETE",
            "endpoint": "/documents/{document_id}",
            "required_params": ["document_id"],
            "optional_params": [],
            "path_parameters": ["document_id"],
            "display_name": "Delete Document",
            "description": "Delete a document from AgileCRM",
            "group": "Documents",
            "tags": ["document", "file", "delete", "attachment"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "document_id": {
                    "pattern": "",
                    "message": "Document ID is required for deletion",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Delete document",
                    "description": "Delete a specific document by ID",
                    "input": {
                        "document_id": 123456
                    }
                }
            ]
        },
        
        # TICKET OPERATIONS (5 operations)
        "get_tickets": {
            "method": "GET",
            "endpoint": "/tickets",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Tickets",
            "description": "Retrieve list of support tickets from AgileCRM",
            "group": "Help Desk",
            "tags": ["tickets", "support", "helpdesk"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "tickets": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            "examples": [
                {
                    "name": "List all tickets",
                    "description": "Get all support tickets from AgileCRM",
                    "input": {}
                }
            ]
        },
        
        "get_ticket": {
            "method": "GET",
            "endpoint": "/tickets/{ticket_id}",
            "required_params": ["ticket_id"],
            "optional_params": [],
            "path_parameters": ["ticket_id"],
            "display_name": "Get Ticket",
            "description": "Retrieve a specific support ticket by ID",
            "group": "Help Desk",
            "tags": ["ticket", "support", "helpdesk"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "ticket": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "ticket_id": {
                    "pattern": "",
                    "message": "Ticket ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Get specific ticket",
                    "description": "Retrieve ticket details by ID",
                    "input": {
                        "ticket_id": 123456
                    }
                }
            ]
        },
        
        "create_ticket": {
            "method": "POST",
            "endpoint": "/tickets",
            "required_params": ["ticket_subject"],
            "optional_params": ["ticket_description", "ticket_priority", "ticket_status", "ticket_type", "contact_id"],
            "body_parameters": ["ticket_subject", "ticket_description", "ticket_priority", "ticket_status", "ticket_type", "contact_id"],
            "display_name": "Create Ticket",
            "description": "Create a new support ticket in AgileCRM",
            "group": "Help Desk",
            "tags": ["ticket", "support", "create", "helpdesk"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "ticket": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "ticket_subject": {
                    "pattern": "",
                    "message": "Ticket subject is required and must be at least 2 characters",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 200,
                    "required": True
                },
                "ticket_priority": {
                    "pattern": "",
                    "message": "Ticket priority must be HIGH, NORMAL, or LOW",
                    "pattern_type": "custom",
                    "enum": ["HIGH", "NORMAL", "LOW"],
                    "required": False
                },
                "ticket_status": {
                    "pattern": "",
                    "message": "Ticket status must be a valid status",
                    "pattern_type": "custom",
                    "enum": ["OPEN", "PENDING", "RESOLVED", "CLOSED"],
                    "required": False
                }
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "field_aliases": {
                    "ticket_subject": "subject",
                    "ticket_description": "description",
                    "ticket_priority": "priority",
                    "ticket_status": "status",
                    "ticket_type": "type",
                    "contact_id": "requester_id"
                }
            },
            
            "examples": [
                {
                    "name": "Create support ticket",
                    "description": "Create a new support ticket for a customer issue",
                    "input": {
                        "ticket_subject": "Login Issue - Cannot Access Account",
                        "ticket_description": "Customer reporting they cannot login to their account after password reset",
                        "ticket_priority": "HIGH",
                        "ticket_status": "OPEN",
                        "ticket_type": "Technical",
                        "contact_id": 123456
                    }
                }
            ]
        },
        
        "update_ticket": {
            "method": "PUT",
            "endpoint": "/tickets/{ticket_id}",
            "required_params": ["ticket_id"],
            "optional_params": ["ticket_subject", "ticket_description", "ticket_priority", "ticket_status", "ticket_type"],
            "path_parameters": ["ticket_id"],
            "body_parameters": ["ticket_subject", "ticket_description", "ticket_priority", "ticket_status", "ticket_type"],
            "display_name": "Update Ticket",
            "description": "Update an existing support ticket's information",
            "group": "Help Desk",
            "tags": ["ticket", "support", "update", "helpdesk"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "ticket": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "ticket_id": {
                    "pattern": "",
                    "message": "Ticket ID is required for updates",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "field_aliases": {
                    "ticket_subject": "subject",
                    "ticket_description": "description",
                    "ticket_priority": "priority",
                    "ticket_status": "status",
                    "ticket_type": "type"
                }
            },
            
            "examples": [
                {
                    "name": "Update ticket status",
                    "description": "Update a ticket's status to resolved",
                    "input": {
                        "ticket_id": 123456,
                        "ticket_status": "RESOLVED"
                    }
                }
            ]
        },
        
        "delete_ticket": {
            "method": "DELETE",
            "endpoint": "/tickets/{ticket_id}",
            "required_params": ["ticket_id"],
            "optional_params": [],
            "path_parameters": ["ticket_id"],
            "display_name": "Delete Ticket",
            "description": "Delete a support ticket from AgileCRM",
            "group": "Help Desk",
            "tags": ["ticket", "support", "delete", "helpdesk"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "ticket_id": {
                    "pattern": "",
                    "message": "Ticket ID is required for deletion",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Delete ticket",
                    "description": "Delete a specific ticket by ID",
                    "input": {
                        "ticket_id": 123456
                    }
                }
            ]
        },
        
        # USER OPERATIONS (2 operations)
        "get_users": {
            "method": "GET",
            "endpoint": "/users",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Users",
            "description": "Retrieve list of users from AgileCRM",
            "group": "Users",
            "tags": ["users", "team", "management"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "users": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            "examples": [
                {
                    "name": "List all users",
                    "description": "Get all users from AgileCRM",
                    "input": {}
                }
            ]
        },
        
        "get_user": {
            "method": "GET",
            "endpoint": "/users/{user_id}",
            "required_params": ["user_id"],
            "optional_params": [],
            "path_parameters": ["user_id"],
            "display_name": "Get User",
            "description": "Retrieve a specific user by ID",
            "group": "Users",
            "tags": ["user", "team", "management"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "user": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "user_id": {
                    "pattern": "",
                    "message": "User ID must be a positive integer",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Get specific user",
                    "description": "Retrieve user details by ID",
                    "input": {
                        "user_id": 123456
                    }
                }
            ]
        },
        
        # TAG OPERATIONS (3 operations)
        "get_tags": {
            "method": "GET",
            "endpoint": "/tags",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Tags",
            "description": "Retrieve list of tags from AgileCRM",
            "group": "Tags",
            "tags": ["tags", "labels", "organization"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "tags": {"type": "array"},
                        "count": {"type": "integer"}
                    }
                }
            },
            
            "examples": [
                {
                    "name": "List all tags",
                    "description": "Get all tags from AgileCRM",
                    "input": {}
                }
            ]
        },
        
        "create_tag": {
            "method": "POST",
            "endpoint": "/tags",
            "required_params": ["tag_name"],
            "optional_params": ["tag_color"],
            "body_parameters": ["tag_name", "tag_color"],
            "display_name": "Create Tag",
            "description": "Create a new tag in AgileCRM",
            "group": "Tags",
            "tags": ["tag", "label", "create", "organization"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "tag": {"type": "object"},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "tag_name": {
                    "pattern": "",
                    "message": "Tag name is required and must be at least 2 characters",
                    "pattern_type": "custom",
                    "min_length": 2,
                    "max_length": 50,
                    "required": True
                },
                "tag_color": {
                    "pattern": "^#[0-9A-Fa-f]{6}$",
                    "message": "Tag color must be a valid hex color code (e.g., #FF0000)",
                    "pattern_type": "regex",
                    "required": False
                }
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {},
                "field_aliases": {
                    "tag_name": "tag",
                    "tag_color": "color"
                }
            },
            
            "examples": [
                {
                    "name": "Create colored tag",
                    "description": "Create a new tag with a specific color",
                    "input": {
                        "tag_name": "High Value Customer",
                        "tag_color": "#FF6600"
                    }
                }
            ]
        },
        
        "delete_tag": {
            "method": "DELETE",
            "endpoint": "/tags/{tag_id}",
            "required_params": ["tag_id"],
            "optional_params": [],
            "path_parameters": ["tag_id"],
            "display_name": "Delete Tag",
            "description": "Delete a tag from AgileCRM",
            "group": "Tags",
            "tags": ["tag", "label", "delete", "organization"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["success"]},
                        "id": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "tag_id": {
                    "pattern": "",
                    "message": "Tag ID is required for deletion",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Delete tag",
                    "description": "Delete a specific tag by ID",
                    "input": {
                        "tag_id": 123456
                    }
                }
            ]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced AgileCRM node with embedded configuration."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Initialize the Enhanced UniversalRequestNode with embedded config
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.info("Enhanced AgileCrmNode initialized with all 13 advanced features and 53 operations")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"AgileCrmNode executing operation: {node_data.get('params', {}).get('operation')}")
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
__all__ = ["AgileCrmNode"]