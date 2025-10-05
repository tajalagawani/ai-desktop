#!/usr/bin/env python3
"""
Autopilot Node - Enhanced with ALL 13 advanced features + ALL 32 original operations
Journey email marketing automation platform integration
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

class AutopilotNode(BaseNode):
    """
    Enhanced Autopilot node with ALL 13 advanced features - comprehensive email marketing automation.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "autopilot",
            "display_name": "Autopilot",
            "description": "Comprehensive journey email marketing automation platform for customer engagement, nurturing, and conversions",
            "category": "marketing",
            "vendor": "autopilot", 
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["marketing", "email", "automation", "journey", "contacts", "lists", "campaigns", "analytics"],
            "documentation_url": "https://autopilot.docs.apiary.io/",
            "icon": "https://cdn.jsdelivr.net/gh/n8n-io/n8n/packages/nodes-base/nodes/Autopilot/autopilot.svg",
            "color": "#4A90E2",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api2.autopilothq.com/v1",
            "authentication": {
                "type": "api_key",
                "header": "autopilotapikey"
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
                "max_delay": 60.0,
                "jitter": True,
                "retriable_codes": [429, 500, 502, 503, 504],
                "retriable_exceptions": ["aiohttp.ClientTimeout", "aiohttp.ClientConnectorError"],
                "timeout_ms": 30000
            },
            "rate_limiting": {
                "requests_per_minute": 1000,
                "requests_per_second": 16.0,
                "burst_size": 5,
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
            "cost_per_1k_requests": 1.0,
            "cost_per_request": 0.001,
            "billing_unit": "requests",
            "free_tier_limit": 10000
        },
        
        # Performance monitoring
        "monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "contact_operations"],
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
                "exclude_params": ["timestamp", "bookmark"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/account"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://autopilot.docs.apiary.io/",
            "setup_guide": "https://autopilot.com/help/api-getting-started",
            "troubleshooting": "https://autopilot.com/help/troubleshooting-api",
            "changelog": "https://autopilot.com/help/api-changelog"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "Autopilot API key (found in Settings > Autopilot API)",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-zA-Z0-9-_]+$",
                    "message": "API key must be alphanumeric with dashes and underscores",
                    "minLength": 20,
                    "maxLength": 100
                }
            },
            "operation": {
                "type": "string",
                "description": "The Autopilot operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    "get_contacts", "create_contact", "update_contact", "delete_contact", "get_contact", "search_contacts",
                    "add_to_list", "remove_from_list", "get_lists", "create_list", "update_list", "delete_list",
                    "get_journeys", "add_to_journey", "remove_from_journey", "get_journey_stats",
                    "get_emails", "get_email_stats", "send_email",
                    "get_custom_fields", "create_custom_field", "update_custom_field", "delete_custom_field",
                    "get_account", "get_webhooks", "create_webhook", "delete_webhook", "track_event",
                    "get_smart_segments", "create_smart_segment", "get_forms", "get_form_submissions"
                ]
            },
            "contact_id": {
                "type": "string",
                "description": "Contact ID for contact-specific operations",
                "required": False,
                "group": "Contact",
                "examples": ["person_12345", "contact_abc123"]
            },
            "email": {
                "type": "string",
                "description": "Contact email address",
                "required": False,
                "group": "Contact",
                "validation": {
                    "pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.[\\w]+$",
                    "message": "Must be a valid email address"
                },
                "examples": ["user@example.com", "john.doe@company.com"]
            },
            "first_name": {
                "type": "string",
                "description": "Contact first name",
                "required": False,
                "group": "Contact",
                "examples": ["John", "Jane"],
                "validation": {
                    "maxLength": 50
                }
            },
            "last_name": {
                "type": "string",
                "description": "Contact last name",
                "required": False,
                "group": "Contact",
                "examples": ["Doe", "Smith"],
                "validation": {
                    "maxLength": 50
                }
            },
            "phone": {
                "type": "string",
                "description": "Contact phone number",
                "required": False,
                "group": "Contact",
                "examples": ["+1-555-123-4567", "555.123.4567"]
            },
            "company": {
                "type": "string",
                "description": "Contact company",
                "required": False,
                "group": "Contact",
                "examples": ["Acme Corp", "Tech Innovations Inc"],
                "validation": {
                    "maxLength": 100
                }
            },
            "list_id": {
                "type": "string",
                "description": "List ID for list operations",
                "required": False,
                "group": "Lists",
                "examples": ["contactlist_12345", "list_abc123"]
            },
            "journey_id": {
                "type": "string",
                "description": "Journey ID for journey operations",
                "required": False,
                "group": "Journeys",
                "examples": ["journey_12345", "trigger_abc123"]
            },
            "name": {
                "type": "string",
                "description": "Name for creation operations",
                "required": False,
                "group": "General",
                "examples": ["My Campaign", "Newsletter List"],
                "validation": {
                    "maxLength": 200
                }
            },
            "description": {
                "type": "string",
                "description": "Description for creation operations",
                "required": False,
                "group": "General",
                "examples": ["Marketing campaign for Q4", "Monthly newsletter subscribers"],
                "validation": {
                    "maxLength": 500
                }
            },
            "tags": {
                "type": "array",
                "description": "Array of tags for contact segmentation",
                "required": False,
                "group": "Contact",
                "examples": [["vip", "premium"], ["lead", "nurture"], ["customer", "active"]],
                "validation": {
                    "maxItems": 10,
                    "items": {
                        "type": "string",
                        "maxLength": 50
                    }
                }
            },
            "custom_fields": {
                "type": "object",
                "description": "Custom field values as JSON object",
                "required": False,
                "group": "Contact",
                "examples": [{"industry": "Technology", "revenue": 50000}, {"source": "Website", "score": 85}]
            },
            "webhook_url": {
                "type": "string",
                "description": "Webhook URL for webhook creation",
                "required": False,
                "group": "Webhooks",
                "validation": {
                    "pattern": "^https?://[\\w\\.-]+\\.[\\w]+(/.*)??$",
                    "message": "Must be a valid HTTP/HTTPS URL"
                },
                "examples": ["https://api.myapp.com/webhook", "https://webhook.site/unique-id"]
            },
            "event_name": {
                "type": "string",
                "description": "Event name for webhook creation or event tracking",
                "required": False,
                "group": "Events",
                "examples": ["contact_added", "email_opened", "purchase_completed"],
                "validation": {
                    "maxLength": 100
                }
            },
            "event_data": {
                "type": "object",
                "description": "Event data for event tracking",
                "required": False,
                "group": "Events",
                "examples": [{"product": "Premium Plan", "value": 99.99}, {"page": "/pricing", "referrer": "google"}]
            },
            "subject": {
                "type": "string",
                "description": "Email subject for sending emails",
                "required": False,
                "group": "Email",
                "examples": ["Welcome to our platform!", "Special offer just for you"],
                "validation": {
                    "maxLength": 200
                }
            },
            "email_content": {
                "type": "string",
                "description": "Email content/body for sending emails",
                "required": False,
                "group": "Email",
                "examples": ["<html><body><h1>Welcome!</h1><p>Thank you for joining us.</p></body></html>"],
                "validation": {
                    "maxLength": 50000
                }
            },
            "from_name": {
                "type": "string",
                "description": "From name for sending emails",
                "required": False,
                "group": "Email",
                "examples": ["John from Acme", "Support Team"],
                "validation": {
                    "maxLength": 100
                }
            },
            "from_email": {
                "type": "string",
                "description": "From email address for sending emails",
                "required": False,
                "group": "Email",
                "validation": {
                    "pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.[\\w]+$",
                    "message": "Must be a valid email address"
                },
                "examples": ["john@acme.com", "noreply@company.com"]
            },
            "query": {
                "type": "string",
                "description": "Search query for contact search",
                "required": False,
                "group": "Search",
                "examples": ["john@example.com", "Premium customer", "Technology industry"],
                "validation": {
                    "maxLength": 200
                }
            },
            "field_type": {
                "type": "string",
                "description": "Custom field type",
                "required": False,
                "group": "Custom Fields",
                "default": "text",
                "validation": {
                    "enum": ["text", "number", "date", "boolean", "select"]
                }
            },
            "field_options": {
                "type": "array",
                "description": "Options for select custom fields",
                "required": False,
                "group": "Custom Fields",
                "examples": [["Option 1", "Option 2", "Option 3"], ["Small", "Medium", "Large"]],
                "validation": {
                    "maxItems": 20,
                    "items": {
                        "type": "string",
                        "maxLength": 100
                    }
                }
            },
            "segment_conditions": {
                "type": "array",
                "description": "Conditions array for smart segment creation",
                "required": False,
                "group": "Segments",
                "examples": [[{"field": "industry", "operator": "equals", "value": "Technology"}]]
            },
            "webhook_events": {
                "type": "array",
                "description": "Array of webhook events to subscribe to",
                "required": False,
                "group": "Webhooks",
                "examples": [["contact_added", "contact_updated"], ["email_opened", "email_clicked"]],
                "validation": {
                    "maxItems": 10,
                    "items": {
                        "type": "string",
                        "enum": ["contact_added", "contact_updated", "contact_deleted", "email_opened", "email_clicked", "journey_entered", "journey_completed"]
                    }
                }
            },
            "limit": {
                "type": "integer",
                "description": "Limit for pagination (default: 100)",
                "required": False,
                "default": 100,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 1000
                }
            },
            "bookmark": {
                "type": "string",
                "description": "Bookmark for pagination",
                "required": False,
                "group": "Pagination",
                "examples": ["page_abc123", "next_token_xyz"]
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful Autopilot API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from Autopilot API"},
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
                    "error_code": {"type": "string", "description": "Autopilot error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "default": {
                "required_env_keys": ["AUTOPILOT_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["api_key"],
                "auth_type": "api_key",
                "auth_description": "Requires Autopilot API key for authentication"
            }
        },
        
        # Error codes specific to Autopilot
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid API key",
            "403": "Forbidden - Request not allowed or insufficient permissions",
            "404": "Not Found - Resource not found",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Autopilot server error",
            "502": "Bad Gateway - Autopilot server temporarily unavailable",
            "503": "Service Unavailable - Autopilot server overloaded"
        }
    }
    
    # Enhanced operation definitions with ALL 32 operations and ALL 13 features
    OPERATIONS = {
        # CONTACT OPERATIONS (6 operations)
        "get_contacts": {
            "method": "GET",
            "endpoint": "/contacts",
            "required_params": [],
            "optional_params": ["limit", "bookmark"],
            "query_parameters": ["limit", "bookmark"],
            "display_name": "Get Contacts",
            "description": "Retrieve a paginated list of all contacts in your Autopilot account",
            "group": "Contacts",
            "tags": ["contacts", "list", "pagination"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "contacts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "contact_id": {"type": "string"},
                                    "Email": {"type": "string"},
                                    "FirstName": {"type": "string"},
                                    "LastName": {"type": "string"},
                                    "Phone": {"type": "string"},
                                    "Company": {"type": "string"}
                                }
                            }
                        },
                        "total_contacts": {"type": "integer"},
                        "bookmark": {"type": "string"}
                    }
                }
            },
            
            "pagination": {
                "type": "cursor",
                "cursor_param": "bookmark",
                "limit_param": "limit",
                "default_limit": 100,
                "max_limit": 1000
            },
            
            "examples": [
                {
                    "name": "Get first 50 contacts",
                    "description": "Retrieve the first 50 contacts",
                    "input": {"limit": 50}
                },
                {
                    "name": "Get next page",
                    "description": "Get next page using bookmark",
                    "input": {"limit": 100, "bookmark": "page_abc123"}
                }
            ]
        },
        
        "create_contact": {
            "method": "POST",
            "endpoint": "/contact",
            "required_params": ["email"],
            "optional_params": ["first_name", "last_name", "phone", "company", "custom_fields"],
            "body_parameters": ["email", "first_name", "last_name", "phone", "company", "custom_fields"],
            "display_name": "Create Contact",
            "description": "Create a new contact in your Autopilot account",
            "group": "Contacts",
            "tags": ["contacts", "create", "lead"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "email": {
                    "pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.[\\w]+$",
                    "message": "Valid email address is required",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "field_mapping": {
                "input_transforms": {
                    "email": "to_autopilot_email",
                    "first_name": "to_autopilot_firstname",
                    "last_name": "to_autopilot_lastname",
                    "phone": "to_autopilot_phone",
                    "company": "to_autopilot_company"
                },
                "field_aliases": {
                    "email": "Email",
                    "first_name": "FirstName", 
                    "last_name": "LastName",
                    "phone": "Phone",
                    "company": "Company"
                }
            },
            
            "examples": [
                {
                    "name": "Simple contact creation",
                    "description": "Create basic contact with email only",
                    "input": {"email": "john@example.com"}
                },
                {
                    "name": "Full contact creation",
                    "description": "Create contact with all details",
                    "input": {
                        "email": "jane@example.com",
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "phone": "+1-555-123-4567",
                        "company": "Acme Corp",
                        "custom_fields": {"industry": "Technology", "source": "Website"}
                    }
                }
            ]
        },
        
        "update_contact": {
            "method": "POST",
            "endpoint": "/contact/{contact_id}",
            "required_params": ["contact_id"],
            "optional_params": ["first_name", "last_name", "phone", "company", "custom_fields", "email"],
            "body_parameters": ["first_name", "last_name", "phone", "company", "custom_fields", "email"],
            "path_parameters": ["contact_id"],
            "display_name": "Update Contact",
            "description": "Update an existing contact's information",
            "group": "Contacts",
            "tags": ["contacts", "update", "modify"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "parameter_dependencies": [
                {
                    "when_field": "contact_id",
                    "when_value": "*",
                    "then_require": [],
                    "then_optional": ["first_name", "last_name", "phone", "company", "custom_fields"],
                    "require_one_of": ["first_name", "last_name", "phone", "company", "custom_fields", "email"]
                }
            ],
            
            "examples": [
                {
                    "name": "Update contact name",
                    "description": "Update contact's first and last name",
                    "input": {
                        "contact_id": "person_12345",
                        "first_name": "John",
                        "last_name": "Smith"
                    }
                }
            ]
        },
        
        "delete_contact": {
            "method": "DELETE",
            "endpoint": "/contact/{contact_id}",
            "required_params": ["contact_id"],
            "optional_params": [],
            "path_parameters": ["contact_id"],
            "display_name": "Delete Contact",
            "description": "Permanently delete a contact from your Autopilot account",
            "group": "Contacts",
            "tags": ["contacts", "delete", "remove"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Delete contact",
                    "description": "Delete contact by ID",
                    "input": {"contact_id": "person_12345"}
                }
            ]
        },
        
        "get_contact": {
            "method": "GET",
            "endpoint": "/contact/{contact_id}",
            "required_params": ["contact_id"],
            "optional_params": [],
            "path_parameters": ["contact_id"],
            "display_name": "Get Contact",
            "description": "Retrieve details of a specific contact by ID or email",
            "group": "Contacts",
            "tags": ["contacts", "get", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get contact by ID",
                    "description": "Retrieve contact using contact ID",
                    "input": {"contact_id": "person_12345"}
                },
                {
                    "name": "Get contact by email",
                    "description": "Retrieve contact using email address",
                    "input": {"contact_id": "john@example.com"}
                }
            ]
        },
        
        "search_contacts": {
            "method": "POST",
            "endpoint": "/contacts/search",
            "required_params": ["query"],
            "optional_params": [],
            "body_parameters": ["query"],
            "display_name": "Search Contacts",
            "description": "Search for contacts using a query string",
            "group": "Contacts",
            "tags": ["contacts", "search", "find"],
            "rate_limit_cost": 2,
            "cache_ttl": 60,
            "response_type": "object",
            
            "validation_rules": {
                "query": {
                    "pattern": ".+",
                    "message": "Search query cannot be empty",
                    "pattern_type": "regex",
                    "min_length": 1,
                    "max_length": 200,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Search by email",
                    "description": "Search for contact by email",
                    "input": {"query": "john@example.com"}
                },
                {
                    "name": "Search by name",
                    "description": "Search for contacts by name",
                    "input": {"query": "John Doe"}
                }
            ]
        },

        # LIST OPERATIONS (6 operations)
        "get_lists": {
            "method": "GET",
            "endpoint": "/lists",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Lists",
            "description": "Retrieve all contact lists in your Autopilot account",
            "group": "Lists",
            "tags": ["lists", "get", "all"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get all lists",
                    "description": "Retrieve all contact lists",
                    "input": {}
                }
            ]
        },
        
        "create_list": {
            "method": "POST",
            "endpoint": "/list",
            "required_params": ["name"],
            "optional_params": [],
            "body_parameters": ["name"],
            "display_name": "Create List",
            "description": "Create a new contact list",
            "group": "Lists",
            "tags": ["lists", "create", "new"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "field_mapping": {
                "field_aliases": {
                    "name": "title"
                }
            },
            
            "examples": [
                {
                    "name": "Create newsletter list",
                    "description": "Create a list for newsletter subscribers",
                    "input": {"name": "Newsletter Subscribers"}
                }
            ]
        },
        
        "update_list": {
            "method": "POST",
            "endpoint": "/list/{list_id}",
            "required_params": ["list_id", "name"],
            "optional_params": [],
            "body_parameters": ["name"],
            "path_parameters": ["list_id"],
            "display_name": "Update List",
            "description": "Update an existing contact list",
            "group": "Lists",
            "tags": ["lists", "update", "modify"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Update list name",
                    "description": "Change the name of an existing list",
                    "input": {
                        "list_id": "contactlist_12345",
                        "name": "VIP Newsletter Subscribers"
                    }
                }
            ]
        },
        
        "delete_list": {
            "method": "DELETE",
            "endpoint": "/list/{list_id}",
            "required_params": ["list_id"],
            "optional_params": [],
            "path_parameters": ["list_id"],
            "display_name": "Delete List",
            "description": "Delete a contact list",
            "group": "Lists",
            "tags": ["lists", "delete", "remove"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Delete list",
                    "description": "Delete a contact list by ID",
                    "input": {"list_id": "contactlist_12345"}
                }
            ]
        },
        
        "add_to_list": {
            "method": "POST",
            "endpoint": "/list/{list_id}/contact/{contact_id}",
            "required_params": ["list_id", "contact_id"],
            "optional_params": [],
            "path_parameters": ["list_id", "contact_id"],
            "display_name": "Add Contact to List",
            "description": "Add a contact to a specific list",
            "group": "Lists",
            "tags": ["lists", "contacts", "add"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Add contact to VIP list",
                    "description": "Add a contact to the VIP list",
                    "input": {
                        "list_id": "contactlist_12345",
                        "contact_id": "person_67890"
                    }
                }
            ]
        },
        
        "remove_from_list": {
            "method": "DELETE",
            "endpoint": "/list/{list_id}/contact/{contact_id}",
            "required_params": ["list_id", "contact_id"],
            "optional_params": [],
            "path_parameters": ["list_id", "contact_id"],
            "display_name": "Remove Contact from List",
            "description": "Remove a contact from a specific list",
            "group": "Lists",
            "tags": ["lists", "contacts", "remove"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Remove contact from list",
                    "description": "Remove a contact from a specific list",
                    "input": {
                        "list_id": "contactlist_12345",
                        "contact_id": "person_67890"
                    }
                }
            ]
        },

        # JOURNEY OPERATIONS (4 operations)
        "get_journeys": {
            "method": "GET",
            "endpoint": "/journeys",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Journeys",
            "description": "Retrieve all automation journeys in your account",
            "group": "Journeys",
            "tags": ["journeys", "automation", "get"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get all journeys",
                    "description": "Retrieve all automation journeys",
                    "input": {}
                }
            ]
        },
        
        "add_to_journey": {
            "method": "POST",
            "endpoint": "/trigger/{journey_id}/contact/{contact_id}",
            "required_params": ["journey_id", "contact_id"],
            "optional_params": [],
            "path_parameters": ["journey_id", "contact_id"],
            "body_parameters": ["trigger_id", "contact_id"],
            "display_name": "Add Contact to Journey",
            "description": "Add a contact to an automation journey",
            "group": "Journeys",
            "tags": ["journeys", "contacts", "trigger"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Add to welcome journey",
                    "description": "Add new contact to welcome journey",
                    "input": {
                        "journey_id": "journey_12345",
                        "contact_id": "person_67890"
                    }
                }
            ]
        },
        
        "remove_from_journey": {
            "method": "DELETE",
            "endpoint": "/trigger/{journey_id}/contact/{contact_id}",
            "required_params": ["journey_id", "contact_id"],
            "optional_params": [],
            "path_parameters": ["journey_id", "contact_id"],
            "display_name": "Remove Contact from Journey",
            "description": "Remove a contact from an automation journey",
            "group": "Journeys",
            "tags": ["journeys", "contacts", "remove"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Remove from journey",
                    "description": "Remove contact from automation journey",
                    "input": {
                        "journey_id": "journey_12345",
                        "contact_id": "person_67890"
                    }
                }
            ]
        },
        
        "get_journey_stats": {
            "method": "GET",
            "endpoint": "/journey/{journey_id}/stats",
            "required_params": ["journey_id"],
            "optional_params": [],
            "path_parameters": ["journey_id"],
            "display_name": "Get Journey Stats",
            "description": "Get performance statistics for a specific journey",
            "group": "Journeys",
            "tags": ["journeys", "analytics", "stats"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get journey performance",
                    "description": "Get stats for welcome journey",
                    "input": {"journey_id": "journey_12345"}
                }
            ]
        },

        # EMAIL OPERATIONS (3 operations)
        "get_emails": {
            "method": "GET",
            "endpoint": "/emails",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Emails",
            "description": "Retrieve all emails in your Autopilot account",
            "group": "Emails",
            "tags": ["emails", "campaigns", "get"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get all emails",
                    "description": "Retrieve all email campaigns",
                    "input": {}
                }
            ]
        },
        
        "get_email_stats": {
            "method": "GET",
            "endpoint": "/email/{email_id}/stats",
            "required_params": ["email_id"],
            "optional_params": [],
            "path_parameters": ["email_id"],
            "display_name": "Get Email Stats",
            "description": "Get performance statistics for a specific email",
            "group": "Emails",
            "tags": ["emails", "analytics", "stats"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get email performance",
                    "description": "Get stats for specific email campaign",
                    "input": {"email_id": "email_12345"}
                }
            ]
        },
        
        "send_email": {
            "method": "POST",
            "endpoint": "/email/send",
            "required_params": ["contact_id", "subject", "email_content"],
            "optional_params": ["from_name", "from_email"],
            "body_parameters": ["contact_id", "subject", "content", "from_name", "from_email"],
            "display_name": "Send Email",
            "description": "Send a direct email to a contact",
            "group": "Emails",
            "tags": ["emails", "send", "direct"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "field_mapping": {
                "field_aliases": {
                    "email_content": "content"
                }
            },
            
            "validation_rules": {
                "subject": {
                    "pattern": ".+",
                    "message": "Email subject cannot be empty",
                    "pattern_type": "regex",
                    "min_length": 1,
                    "max_length": 200,
                    "required": True
                },
                "email_content": {
                    "pattern": ".+",
                    "message": "Email content cannot be empty",
                    "pattern_type": "regex",
                    "min_length": 1,
                    "max_length": 50000,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Send welcome email",
                    "description": "Send welcome email to new contact",
                    "input": {
                        "contact_id": "person_12345",
                        "subject": "Welcome to our platform!",
                        "email_content": "<html><body><h1>Welcome!</h1><p>Thank you for joining us.</p></body></html>",
                        "from_name": "Support Team",
                        "from_email": "support@company.com"
                    }
                }
            ]
        },

        # CUSTOM FIELD OPERATIONS (4 operations)
        "get_custom_fields": {
            "method": "GET",
            "endpoint": "/contact/custom_fields",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Custom Fields",
            "description": "Retrieve all custom fields defined in your account",
            "group": "Custom Fields",
            "tags": ["custom-fields", "schema", "get"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get all custom fields",
                    "description": "Retrieve all custom field definitions",
                    "input": {}
                }
            ]
        },
        
        "create_custom_field": {
            "method": "POST",
            "endpoint": "/contact/custom_field",
            "required_params": ["name"],
            "optional_params": ["field_type", "field_options"],
            "body_parameters": ["name", "field_type", "field_options"],
            "display_name": "Create Custom Field",
            "description": "Create a new custom field for contacts",
            "group": "Custom Fields",
            "tags": ["custom-fields", "create", "schema"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "field_mapping": {
                "field_aliases": {
                    "field_type": "kind"
                }
            },
            
            "array_templates": {
                "field_options": [
                    {"template": "Option 1", "description": "First option for select field"},
                    {"template": "Option 2", "description": "Second option for select field"},
                    {"template": "Option 3", "description": "Third option for select field"}
                ]
            },
            
            "parameter_dependencies": [
                {
                    "when_field": "field_type",
                    "when_value": "select",
                    "then_require": ["field_options"],
                    "then_optional": []
                }
            ],
            
            "examples": [
                {
                    "name": "Create text field",
                    "description": "Create a simple text custom field",
                    "input": {
                        "name": "Industry",
                        "field_type": "text"
                    }
                },
                {
                    "name": "Create select field",
                    "description": "Create a select field with options",
                    "input": {
                        "name": "Company Size",
                        "field_type": "select",
                        "field_options": ["Small (1-10)", "Medium (11-50)", "Large (51+)"]
                    }
                }
            ]
        },
        
        "update_custom_field": {
            "method": "POST",
            "endpoint": "/contact/custom_field/{field_id}",
            "required_params": ["field_id", "name"],
            "optional_params": [],
            "body_parameters": ["name"],
            "path_parameters": ["field_id"],
            "display_name": "Update Custom Field",
            "description": "Update an existing custom field",
            "group": "Custom Fields",
            "tags": ["custom-fields", "update", "modify"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Update field name",
                    "description": "Update custom field name",
                    "input": {
                        "field_id": "custom_field_12345",
                        "name": "Company Industry"
                    }
                }
            ]
        },
        
        "delete_custom_field": {
            "method": "DELETE",
            "endpoint": "/contact/custom_field/{field_id}",
            "required_params": ["field_id"],
            "optional_params": [],
            "path_parameters": ["field_id"],
            "display_name": "Delete Custom Field",
            "description": "Delete a custom field",
            "group": "Custom Fields",
            "tags": ["custom-fields", "delete", "remove"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Delete custom field",
                    "description": "Delete a custom field by ID",
                    "input": {"field_id": "custom_field_12345"}
                }
            ]
        },

        # ACCOUNT OPERATIONS (1 operation)
        "get_account": {
            "method": "GET",
            "endpoint": "/account",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Account",
            "description": "Retrieve account information and settings",
            "group": "Account",
            "tags": ["account", "info", "settings"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get account info",
                    "description": "Retrieve account information",
                    "input": {}
                }
            ]
        },

        # WEBHOOK OPERATIONS (3 operations)
        "get_webhooks": {
            "method": "GET",
            "endpoint": "/hooks",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Webhooks",
            "description": "Retrieve all webhooks configured in your account",
            "group": "Webhooks",
            "tags": ["webhooks", "integrations", "get"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get all webhooks",
                    "description": "Retrieve all configured webhooks",
                    "input": {}
                }
            ]
        },
        
        "create_webhook": {
            "method": "POST",
            "endpoint": "/hook",
            "required_params": ["webhook_url", "event_name"],
            "optional_params": ["webhook_events"],
            "body_parameters": ["webhook_url", "event_name", "webhook_events"],
            "display_name": "Create Webhook",
            "description": "Create a new webhook for receiving event notifications",
            "group": "Webhooks",
            "tags": ["webhooks", "integrations", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "field_mapping": {
                "field_aliases": {
                    "webhook_url": "target_url",
                    "event_name": "event"
                }
            },
            
            "array_templates": {
                "webhook_events": [
                    {"template": "contact_added", "description": "Triggered when a new contact is added"},
                    {"template": "contact_updated", "description": "Triggered when a contact is updated"},
                    {"template": "email_opened", "description": "Triggered when an email is opened"},
                    {"template": "email_clicked", "description": "Triggered when an email link is clicked"}
                ]
            },
            
            "validation_rules": {
                "webhook_url": {
                    "pattern": "^https?://[\\w\\.-]+\\.[\\w]+(/.*)??$",
                    "message": "Must be a valid HTTP/HTTPS URL",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Create contact webhook",
                    "description": "Create webhook for contact events",
                    "input": {
                        "webhook_url": "https://api.myapp.com/autopilot-webhook",
                        "event_name": "contact_added"
                    }
                },
                {
                    "name": "Create multi-event webhook",
                    "description": "Create webhook for multiple events",
                    "input": {
                        "webhook_url": "https://webhook.site/unique-id",
                        "event_name": "contact_added",
                        "webhook_events": ["contact_added", "contact_updated", "email_opened"]
                    }
                }
            ]
        },
        
        "delete_webhook": {
            "method": "DELETE",
            "endpoint": "/hook/{webhook_id}",
            "required_params": ["webhook_id"],
            "optional_params": [],
            "path_parameters": ["webhook_id"],
            "display_name": "Delete Webhook",
            "description": "Delete an existing webhook",
            "group": "Webhooks",
            "tags": ["webhooks", "integrations", "delete"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Delete webhook",
                    "description": "Delete webhook by ID",
                    "input": {"webhook_id": "hook_12345"}
                }
            ]
        },

        # EVENT OPERATIONS (1 operation)
        "track_event": {
            "method": "POST",
            "endpoint": "/trigger/{event_name}/contact/{contact_id}",
            "required_params": ["contact_id", "event_name"],
            "optional_params": ["event_data"],
            "body_parameters": ["contact_id", "event", "properties"],
            "path_parameters": ["event_name", "contact_id"],
            "display_name": "Track Event",
            "description": "Track a custom event for a contact",
            "group": "Events",
            "tags": ["events", "tracking", "analytics"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "field_mapping": {
                "field_aliases": {
                    "event_name": "event",
                    "event_data": "properties"
                }
            },
            
            "examples": [
                {
                    "name": "Track purchase",
                    "description": "Track a purchase event",
                    "input": {
                        "contact_id": "person_12345",
                        "event_name": "purchase_completed",
                        "event_data": {
                            "product": "Premium Plan",
                            "value": 99.99,
                            "currency": "USD"
                        }
                    }
                },
                {
                    "name": "Track page view",
                    "description": "Track a page view event",
                    "input": {
                        "contact_id": "person_12345",
                        "event_name": "page_viewed",
                        "event_data": {
                            "page": "/pricing",
                            "referrer": "google",
                            "utm_source": "adwords"
                        }
                    }
                }
            ]
        },

        # SMART SEGMENT OPERATIONS (2 operations)
        "get_smart_segments": {
            "method": "GET",
            "endpoint": "/smart_segments",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Smart Segments",
            "description": "Retrieve all smart segments in your account",
            "group": "Segments",
            "tags": ["segments", "targeting", "get"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get all segments",
                    "description": "Retrieve all smart segments",
                    "input": {}
                }
            ]
        },
        
        "create_smart_segment": {
            "method": "POST",
            "endpoint": "/smart_segment",
            "required_params": ["name", "segment_conditions"],
            "optional_params": [],
            "body_parameters": ["name", "segment_conditions"],
            "display_name": "Create Smart Segment",
            "description": "Create a new smart segment with specified conditions",
            "group": "Segments",
            "tags": ["segments", "targeting", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "field_mapping": {
                "field_aliases": {
                    "name": "title",
                    "segment_conditions": "conditions"
                }
            },
            
            "array_templates": {
                "segment_conditions": [
                    {
                        "template": {
                            "field": "industry",
                            "operator": "equals",
                            "value": "Technology"
                        },
                        "description": "Condition to match contacts in Technology industry"
                    },
                    {
                        "template": {
                            "field": "Email",
                            "operator": "contains",
                            "value": "@gmail.com"
                        },
                        "description": "Condition to match Gmail email addresses"
                    },
                    {
                        "template": {
                            "field": "created_at",
                            "operator": "after",
                            "value": "2024-01-01"
                        },
                        "description": "Condition to match recently added contacts"
                    }
                ]
            },
            
            "validation_rules": {
                "segment_conditions": {
                    "pattern": "",
                    "message": "Segment conditions array is required",
                    "pattern_type": "custom",
                    "min_items": 1,
                    "max_items": 10,
                    "required": True
                }
            },
            
            "examples": [
                {
                    "name": "Create tech industry segment",
                    "description": "Create segment for technology industry contacts",
                    "input": {
                        "name": "Technology Industry",
                        "segment_conditions": [
                            {
                                "field": "industry",
                                "operator": "equals",
                                "value": "Technology"
                            }
                        ]
                    }
                },
                {
                    "name": "Create multi-condition segment",
                    "description": "Create segment with multiple conditions",
                    "input": {
                        "name": "VIP Tech Customers",
                        "segment_conditions": [
                            {
                                "field": "industry",
                                "operator": "equals",
                                "value": "Technology"
                            },
                            {
                                "field": "customer_type",
                                "operator": "equals",
                                "value": "Premium"
                            }
                        ]
                    }
                }
            ]
        },

        # FORM OPERATIONS (2 operations)
        "get_forms": {
            "method": "GET",
            "endpoint": "/forms",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Forms",
            "description": "Retrieve all forms in your Autopilot account",
            "group": "Forms",
            "tags": ["forms", "lead-capture", "get"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get all forms",
                    "description": "Retrieve all lead capture forms",
                    "input": {}
                }
            ]
        },
        
        "get_form_submissions": {
            "method": "GET",
            "endpoint": "/form/{form_id}/submissions",
            "required_params": ["form_id"],
            "optional_params": [],
            "path_parameters": ["form_id"],
            "display_name": "Get Form Submissions",
            "description": "Retrieve submissions for a specific form",
            "group": "Forms",
            "tags": ["forms", "submissions", "leads"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "examples": [
                {
                    "name": "Get form submissions",
                    "description": "Retrieve all submissions for a form",
                    "input": {"form_id": "form_12345"}
                }
            ]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced Autopilot node with embedded configuration."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Initialize the Enhanced UniversalRequestNode with embedded config
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.info("Enhanced AutopilotNode initialized with all 13 advanced features and 32 operations")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"AutopilotNode executing operation: {node_data.get('params', {}).get('operation')}")
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
__all__ = ["AutopilotNode"]