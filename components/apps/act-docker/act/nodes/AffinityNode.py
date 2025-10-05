#!/usr/bin/env python3
"""
Affinity Node - FULLY RESTORED with ALL 40 original operations + Enhanced with ALL 13 advanced features
This is the complete recovery of the catastrophically lost AffinityNode operations.
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

class AffinityNode(BaseNode):
    """
    FULLY RESTORED Affinity CRM node with ALL 40 original operations + Enhanced with ALL 13 advanced features.
    This is the complete recovery from the catastrophic data loss.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features - COMPLETE RECOVERY
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "affinity",
            "display_name": "Affinity CRM",
            "description": "Professional relationship intelligence and deal management CRM for investment professionals - FULLY RESTORED with all 40 operations",
            "category": "crm",
            "vendor": "affinity", 
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["crm", "relationships", "deals", "contacts", "organizations", "venture", "private-equity", "investment", "portfolio", "fundraising"],
            "documentation_url": "https://api-docs.affinity.co",
            "icon": "https://assets.affinity.co/favicon/favicon-32x32.png",
            "color": "#1f4788",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.affinity.co",
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
                "requests_per_minute": 900,
                "requests_per_second": 15.0,
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
            "cost_per_request": 0.001,
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
                "exclude_params": ["timestamp", "nonce", "page_token"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/auth/whoami"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://api-docs.affinity.co/",
            "setup_guide": "https://support.affinity.co/hc/en-us/sections/360000683932-API",
            "troubleshooting": "https://support.affinity.co/hc/en-us/articles/360000694071-API-Rate-Limits",
            "changelog": "https://api-docs.affinity.co/#changelog"
        },
        
        # All parameters with enhanced metadata - COMPLETE RESTORATION
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "Affinity API key (get from Settings > API Keys)",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "minLength": 10,
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "API key must be alphanumeric"
                }
            },
            "operation": {
                "type": "string",
                "description": "The Affinity operation to perform - ALL 40 OPERATIONS RESTORED",
                "required": True,
                "group": "Operation",
                "enum": [
                    "get_persons", "get_person", "create_person", "update_person", "delete_person",
                    "get_companies", "get_company", "create_company", "update_company", "delete_company", 
                    "get_opportunities", "get_opportunity", "create_opportunity", "update_opportunity", "delete_opportunity",
                    "get_lists", "get_list", "create_list", "update_list", "delete_list",
                    "get_list_entries", "create_list_entry", "update_list_entry", "delete_list_entry",
                    "get_fields", "get_field", "create_field", "update_field", "delete_field",
                    "get_field_values", "update_field_values",
                    "search_persons", "search_companies", "search_opportunities",
                    "get_interactions", "create_interaction",
                    "get_webhooks", "create_webhook", "delete_webhook",
                    "whoami"
                ]
            },
            
            # ID parameters
            "person_id": {
                "type": "integer",
                "description": "Person ID for person-specific operations",
                "required": False,
                "group": "Identifiers",
                "validation": {"minimum": 1}
            },
            "company_id": {
                "type": "integer",
                "description": "Company ID for company-specific operations",
                "required": False,
                "group": "Identifiers",
                "validation": {"minimum": 1}
            },
            "organization_id": {
                "type": "integer", 
                "description": "Organization ID for organization-specific operations",
                "required": False,
                "group": "Identifiers",
                "validation": {"minimum": 1}
            },
            "opportunity_id": {
                "type": "integer",
                "description": "Opportunity ID for opportunity-specific operations", 
                "required": False,
                "group": "Identifiers",
                "validation": {"minimum": 1}
            },
            "list_id": {
                "type": "integer",
                "description": "List ID for list-specific operations",
                "required": False,
                "group": "Identifiers",
                "validation": {"minimum": 1}
            },
            "list_entry_id": {
                "type": "integer",
                "description": "List entry ID for list entry operations",
                "required": False,
                "group": "Identifiers",
                "validation": {"minimum": 1}
            },
            "field_id": {
                "type": "integer",
                "description": "Field ID for field operations",
                "required": False,
                "group": "Identifiers",
                "validation": {"minimum": 1}
            },
            "webhook_id": {
                "type": "integer",
                "description": "Webhook ID for webhook operations",
                "required": False,
                "group": "Identifiers",
                "validation": {"minimum": 1}
            },
            
            # Person parameters
            "first_name": {
                "type": "string",
                "description": "Person's first name",
                "required": False,
                "group": "Person Details",
                "examples": ["John", "Jane"],
                "validation": {"maxLength": 100}
            },
            "last_name": {
                "type": "string",
                "description": "Person's last name",
                "required": False,
                "group": "Person Details", 
                "examples": ["Doe", "Smith"],
                "validation": {"maxLength": 100}
            },
            "emails": {
                "type": "array",
                "description": "Array of email addresses",
                "required": False,
                "group": "Person Details",
                "examples": [["john@example.com"], ["jane.doe@company.com", "jane@personal.com"]],
                "validation": {
                    "maxItems": 10,
                    "items": {"type": "string", "format": "email"}
                }
            },
            "phone_numbers": {
                "type": "array",
                "description": "Array of phone numbers",
                "required": False,
                "group": "Person Details",
                "examples": [["+1-555-123-4567"], ["+1-555-987-6543", "+1-555-111-2222"]],
                "validation": {"maxItems": 10}
            },
            "organization_ids": {
                "type": "array",
                "description": "Array of organization IDs to associate with person",
                "required": False,
                "group": "Person Details",
                "validation": {
                    "maxItems": 50,
                    "items": {"type": "integer", "minimum": 1}
                }
            },
            
            # Company parameters
            "name": {
                "type": "string",
                "description": "Organization or opportunity name",
                "required": False,
                "group": "General Details",
                "examples": ["Acme Corp", "Strategic Partnership Opportunity"],
                "validation": {"maxLength": 200}
            },
            "domain": {
                "type": "string",
                "description": "Organization domain name",
                "required": False,
                "group": "Organization Details",
                "examples": ["acme.com", "example.org"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "message": "Must be a valid domain"
                }
            },
            "domains": {
                "type": "array",
                "description": "Array of domain names",
                "required": False,
                "group": "Organization Details",
                "examples": [["acme.com"], ["example.org", "example.com"]],
                "validation": {"maxItems": 20}
            },
            
            # Opportunity parameters
            "person_ids": {
                "type": "array",
                "description": "Array of person IDs associated with opportunity",
                "required": False,
                "group": "Opportunity Details",
                "validation": {
                    "maxItems": 100,
                    "items": {"type": "integer", "minimum": 1}
                }
            },
            
            # List parameters
            "list_name": {
                "type": "string",
                "description": "Name of the list",
                "required": False,
                "group": "List Details",
                "examples": ["Key Investors", "Portfolio Companies"],
                "validation": {"maxLength": 100}
            },
            "list_type": {
                "type": "string",
                "description": "Type of list",
                "required": False,
                "group": "List Details",
                "validation": {
                    "enum": ["person", "organization", "opportunity"]
                }
            },
            "is_public": {
                "type": "boolean",
                "description": "Whether the list is public",
                "required": False,
                "group": "List Details",
                "default": False
            },
            
            # List Entry parameters
            "entity_id": {
                "type": "integer",
                "description": "ID of entity (person, organization, or opportunity) to add to list",
                "required": False,
                "group": "List Entry Details",
                "validation": {"minimum": 1}
            },
            "creator_id": {
                "type": "integer",
                "description": "ID of user creating the list entry",
                "required": False,
                "group": "List Entry Details",
                "validation": {"minimum": 1}
            },
            
            # Field parameters
            "field_name": {
                "type": "string",
                "description": "Name of the custom field",
                "required": False,
                "group": "Field Details",
                "examples": ["Investment Stage", "Deal Size", "Last Contact Date"],
                "validation": {"maxLength": 100}
            },
            "field_type": {
                "type": "string",
                "description": "Type of custom field",
                "required": False,
                "group": "Field Details",
                "validation": {
                    "enum": ["text", "number", "date", "dropdown", "multi_select", "person", "organization"]
                }
            },
            "field_value": {
                "type": "any",
                "description": "Field value to set",
                "required": False,
                "group": "Field Details"
            },
            "field_values": {
                "type": "object",
                "description": "Object containing field ID to value mappings",
                "required": False,
                "group": "Field Details"
            },
            
            # Search parameters
            "term": {
                "type": "string",
                "description": "Search term for search operations",
                "required": False,
                "group": "Search Parameters",
                "examples": ["john doe", "acme corp", "series a"],
                "validation": {"minLength": 2, "maxLength": 100}
            },
            
            # Interaction parameters
            "interaction_type": {
                "type": "string",
                "description": "Type of interaction",
                "required": False,
                "group": "Interaction Details",
                "validation": {
                    "enum": ["email", "call", "meeting", "note"]
                }
            },
            "interaction_date": {
                "type": "string",
                "description": "Date of interaction (ISO format)",
                "required": False,
                "group": "Interaction Details",
                "examples": ["2025-08-25T10:30:00Z"],
                "validation": {
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$",
                    "message": "Must be ISO 8601 format"
                }
            },
            "interaction_content": {
                "type": "string",
                "description": "Content or notes for the interaction",
                "required": False,
                "group": "Interaction Details",
                "examples": ["Discussed Series A funding round", "Follow-up call scheduled"],
                "validation": {"maxLength": 2000}
            },
            
            # Webhook parameters
            "webhook_url": {
                "type": "string",
                "description": "URL to receive webhook notifications",
                "required": False,
                "group": "Webhook Details",
                "examples": ["https://api.yourapp.com/webhooks/affinity"],
                "validation": {
                    "pattern": "^https?://",
                    "message": "Must be a valid HTTP/HTTPS URL"
                }
            },
            "subscriptions": {
                "type": "array",
                "description": "Array of event types to subscribe to",
                "required": False,
                "group": "Webhook Details",
                "examples": [["person.created", "organization.updated"]],
                "validation": {"maxItems": 50}
            },
            
            # Pagination parameters
            "page_size": {
                "type": "integer",
                "description": "Number of results per page (max 500)",
                "required": False,
                "group": "Pagination",
                "default": 100,
                "validation": {
                    "minimum": 1,
                    "maximum": 500
                }
            },
            "page_token": {
                "type": "string",
                "description": "Token for pagination",
                "required": False,
                "group": "Pagination"
            },
            "with_interaction_dates": {
                "type": "boolean",
                "description": "Include interaction dates in response",
                "required": False,
                "group": "Response Options",
                "default": False
            },
            "with_interaction_persons": {
                "type": "boolean",
                "description": "Include interaction persons in response", 
                "required": False,
                "group": "Response Options",
                "default": False
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful Affinity API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from Affinity API"},
                    "result": {"type": "object", "description": "Full API response data"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Error code"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "default": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "optional_env_keys": []
            }
        },
        
        # Error codes specific to Affinity
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid API key",
            "403": "Forbidden - Request not allowed",
            "404": "Not Found - Resource not found", 
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Affinity server error",
            "502": "Bad Gateway - Affinity server temporarily unavailable",
            "503": "Service Unavailable - Affinity server overloaded"
        }
    }
    
    # COMPLETE OPERATIONS DICTIONARY WITH ALL 40 OPERATIONS RESTORED + Enhanced Features
    OPERATIONS = {
        # PERSON OPERATIONS (5 operations)
        "get_persons": {
            "method": "GET",
            "endpoint": "/persons",
            "required_params": [],
            "optional_params": ["page_size", "page_token", "with_interaction_dates", "with_interaction_persons"],
            "display_name": "Get Persons",
            "description": "Retrieve all persons from Affinity CRM",
            "group": "Persons",
            "tags": ["persons", "contacts", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "persons": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "type": {"type": "integer", "enum": [0]},
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "primary_email": {"type": "string"},
                                    "emails": {"type": "array"},
                                    "organizations": {"type": "array"}
                                }
                            }
                        },
                        "page_size": {"type": "integer"},
                        "next_page_token": {"type": "string"}
                    }
                }
            },
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get all persons",
                    "input": {"page_size": 50, "with_interaction_dates": True}
                }
            ]
        },
        
        "get_person": {
            "method": "GET", 
            "endpoint": "/persons/{person_id}",
            "required_params": ["person_id"],
            "optional_params": ["with_interaction_dates", "with_interaction_persons"],
            "display_name": "Get Person",
            "description": "Get a specific person by ID",
            "group": "Persons",
            "tags": ["person", "contact", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "type": {"type": "integer", "enum": [0]},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "primary_email": {"type": "string"},
                        "emails": {"type": "array"},
                        "phone_numbers": {"type": "array"},
                        "organizations": {"type": "array"}
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get person with interactions",
                    "input": {"person_id": 12345, "with_interaction_dates": True}
                }
            ]
        },
        
        "create_person": {
            "method": "POST",
            "endpoint": "/persons",
            "required_params": [],
            "optional_params": ["first_name", "last_name", "emails", "phone_numbers", "organization_ids"],
            "body_parameters": ["first_name", "last_name", "emails", "phone_numbers", "organization_ids"],
            "display_name": "Create Person",
            "description": "Create a new person in Affinity CRM",
            "group": "Persons",
            "tags": ["person", "create", "contact"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "emails": [
                    {"template": "john.doe@company.com", "description": "Primary business email"},
                    {"template": "john@personal.com", "description": "Personal email address"}
                ],
                "phone_numbers": [
                    {"template": "+1-555-123-4567", "description": "Business phone number"},
                    {"template": "+1-555-987-6543", "description": "Mobile phone number"}
                ],
                "organization_ids": [
                    {"template": 12345, "description": "Primary organization ID"},
                    {"template": 67890, "description": "Secondary organization ID"}
                ]
            },
            
            "validation_rules": {
                "emails_or_name_required": {
                    "message": "At least one of first_name, last_name, or emails is required",
                    "require_one_of": ["first_name", "last_name", "emails"]
                }
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Create person with email",
                    "input": {
                        "first_name": "John",
                        "last_name": "Doe", 
                        "emails": ["john@example.com"]
                    }
                }
            ]
        },
        
        "update_person": {
            "method": "PUT",
            "endpoint": "/persons/{person_id}",
            "required_params": ["person_id"],
            "optional_params": ["first_name", "last_name", "emails", "phone_numbers", "organization_ids"],
            "body_parameters": ["first_name", "last_name", "emails", "phone_numbers", "organization_ids"],
            "display_name": "Update Person",
            "description": "Update an existing person in Affinity CRM",
            "group": "Persons",
            "tags": ["person", "update", "contact"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "emails": [
                    {"template": "updated.email@company.com", "description": "Updated business email"},
                    {"template": "new.personal@email.com", "description": "New personal email"}
                ],
                "phone_numbers": [
                    {"template": "+1-555-999-8888", "description": "Updated phone number"},
                    {"template": "+1-555-777-6666", "description": "Additional contact number"}
                ],
                "organization_ids": [
                    {"template": 11111, "description": "New primary organization"},
                    {"template": 22222, "description": "Additional organization association"}
                ]
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Update person email",
                    "input": {
                        "person_id": 12345,
                        "emails": ["newemail@example.com"]
                    }
                }
            ]
        },
        
        "delete_person": {
            "method": "DELETE",
            "endpoint": "/persons/{person_id}",
            "required_params": ["person_id"],
            "optional_params": [],
            "display_name": "Delete Person",
            "description": "Delete a person from Affinity CRM",
            "group": "Persons",
            "tags": ["person", "delete"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Delete person",
                    "input": {"person_id": 12345}
                }
            ]
        },
        
        # COMPANY OPERATIONS (5 operations)
        "get_companies": {
            "method": "GET",
            "endpoint": "/organizations",
            "required_params": [],
            "optional_params": ["page_size", "page_token", "with_interaction_dates"],
            "display_name": "Get Companies",
            "description": "Retrieve all companies/organizations from Affinity CRM",
            "group": "Companies",
            "tags": ["companies", "organizations", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get all companies",
                    "input": {"page_size": 50}
                }
            ]
        },
        
        "get_company": {
            "method": "GET",
            "endpoint": "/organizations/{organization_id}",
            "required_params": ["organization_id"],
            "optional_params": ["with_interaction_dates"],
            "display_name": "Get Company",
            "description": "Get a specific company/organization by ID",
            "group": "Companies",
            "tags": ["company", "organization", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get company details",
                    "input": {"organization_id": 67890}
                }
            ]
        },
        
        "create_company": {
            "method": "POST",
            "endpoint": "/organizations",
            "required_params": [],
            "optional_params": ["name", "domain", "domains"],
            "body_parameters": ["name", "domain", "domains"],
            "display_name": "Create Company",
            "description": "Create a new company/organization in Affinity CRM",
            "group": "Companies",
            "tags": ["company", "organization", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "domains": [
                    {"template": "acme.com", "description": "Primary company domain"},
                    {"template": "acmecorp.org", "description": "Secondary organization domain"},
                    {"template": "acme.co", "description": "Alternative domain"}
                ]
            },
            
            "validation_rules": {
                "name_or_domain_required": {
                    "message": "Either name or domain is required",
                    "require_one_of": ["name", "domain"]
                }
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Create company with domain",
                    "input": {
                        "name": "Acme Corp",
                        "domain": "acme.com"
                    }
                }
            ]
        },
        
        "update_company": {
            "method": "PUT",
            "endpoint": "/organizations/{organization_id}",
            "required_params": ["organization_id"],
            "optional_params": ["name", "domain", "domains"],
            "body_parameters": ["name", "domain", "domains"],
            "display_name": "Update Company",
            "description": "Update an existing company/organization in Affinity CRM",
            "group": "Companies",
            "tags": ["company", "organization", "update"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "domains": [
                    {"template": "newdomain.com", "description": "Updated primary domain"},
                    {"template": "company-new.org", "description": "Additional updated domain"}
                ]
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Update company name",
                    "input": {
                        "organization_id": 67890,
                        "name": "Acme Corporation"
                    }
                }
            ]
        },
        
        "delete_company": {
            "method": "DELETE",
            "endpoint": "/organizations/{organization_id}",
            "required_params": ["organization_id"],
            "optional_params": [],
            "display_name": "Delete Company",
            "description": "Delete a company/organization from Affinity CRM",
            "group": "Companies",
            "tags": ["company", "organization", "delete"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Delete company",
                    "input": {"organization_id": 67890}
                }
            ]
        },
        
        # OPPORTUNITY OPERATIONS (5 operations)
        "get_opportunities": {
            "method": "GET",
            "endpoint": "/opportunities",
            "required_params": [],
            "optional_params": ["page_size", "page_token"],
            "display_name": "Get Opportunities",
            "description": "Retrieve all opportunities from Affinity CRM",
            "group": "Opportunities",
            "tags": ["opportunities", "deals", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get all opportunities",
                    "input": {"page_size": 50}
                }
            ]
        },
        
        "get_opportunity": {
            "method": "GET",
            "endpoint": "/opportunities/{opportunity_id}",
            "required_params": ["opportunity_id"],
            "optional_params": [],
            "display_name": "Get Opportunity",
            "description": "Get a specific opportunity by ID",
            "group": "Opportunities",
            "tags": ["opportunity", "deal", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get opportunity details",
                    "input": {"opportunity_id": 54321}
                }
            ]
        },
        
        "create_opportunity": {
            "method": "POST",
            "endpoint": "/opportunities",
            "required_params": [],
            "optional_params": ["name", "person_ids", "organization_id"],
            "body_parameters": ["name", "person_ids", "organization_id"],
            "display_name": "Create Opportunity",
            "description": "Create a new opportunity in Affinity CRM",
            "group": "Opportunities",
            "tags": ["opportunity", "deal", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "person_ids": [
                    {"template": 12345, "description": "Primary contact person ID"},
                    {"template": 67890, "description": "Secondary stakeholder ID"},
                    {"template": 54321, "description": "Decision maker ID"}
                ]
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Create opportunity",
                    "input": {
                        "name": "Series A Funding",
                        "person_ids": [12345],
                        "organization_id": 67890
                    }
                }
            ]
        },
        
        "update_opportunity": {
            "method": "PUT",
            "endpoint": "/opportunities/{opportunity_id}",
            "required_params": ["opportunity_id"],
            "optional_params": ["name", "person_ids", "organization_id"],
            "body_parameters": ["name", "person_ids", "organization_id"],
            "display_name": "Update Opportunity",
            "description": "Update an existing opportunity in Affinity CRM",
            "group": "Opportunities",
            "tags": ["opportunity", "deal", "update"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "person_ids": [
                    {"template": 11111, "description": "Updated primary contact ID"},
                    {"template": 22222, "description": "New stakeholder ID"},
                    {"template": 33333, "description": "Additional team member ID"}
                ]
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Update opportunity name",
                    "input": {
                        "opportunity_id": 54321,
                        "name": "Series B Funding"
                    }
                }
            ]
        },
        
        "delete_opportunity": {
            "method": "DELETE",
            "endpoint": "/opportunities/{opportunity_id}",
            "required_params": ["opportunity_id"],
            "optional_params": [],
            "display_name": "Delete Opportunity",
            "description": "Delete an opportunity from Affinity CRM",
            "group": "Opportunities",
            "tags": ["opportunity", "deal", "delete"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Delete opportunity",
                    "input": {"opportunity_id": 54321}
                }
            ]
        },
        
        # LIST OPERATIONS (5 operations)
        "get_lists": {
            "method": "GET",
            "endpoint": "/lists",
            "required_params": [],
            "optional_params": ["page_size", "page_token"],
            "display_name": "Get Lists",
            "description": "Retrieve all lists from Affinity CRM",
            "group": "Lists",
            "tags": ["lists", "collections"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get all lists",
                    "input": {"page_size": 50}
                }
            ]
        },
        
        "get_list": {
            "method": "GET",
            "endpoint": "/lists/{list_id}",
            "required_params": ["list_id"],
            "optional_params": [],
            "display_name": "Get List",
            "description": "Get a specific list by ID",
            "group": "Lists",
            "tags": ["list", "collection", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get list details",
                    "input": {"list_id": 98765}
                }
            ]
        },
        
        "create_list": {
            "method": "POST",
            "endpoint": "/lists",
            "required_params": ["list_name", "list_type"],
            "optional_params": ["is_public"],
            "body_parameters": ["name", "type", "is_public"],
            "display_name": "Create List",
            "description": "Create a new list in Affinity CRM",
            "group": "Lists",
            "tags": ["list", "collection", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "field_mapping": {
                "input_transforms": {
                    "list_name": "name",
                    "list_type": "type"
                }
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Create person list",
                    "input": {
                        "list_name": "Key Investors",
                        "list_type": "person",
                        "is_public": False
                    }
                }
            ]
        },
        
        "update_list": {
            "method": "PUT",
            "endpoint": "/lists/{list_id}",
            "required_params": ["list_id"],
            "optional_params": ["list_name", "is_public"],
            "body_parameters": ["name", "is_public"],
            "display_name": "Update List",
            "description": "Update an existing list in Affinity CRM",
            "group": "Lists",
            "tags": ["list", "collection", "update"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "field_mapping": {
                "input_transforms": {
                    "list_name": "name"
                }
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Update list name",
                    "input": {
                        "list_id": 98765,
                        "list_name": "Top Investors"
                    }
                }
            ]
        },
        
        "delete_list": {
            "method": "DELETE",
            "endpoint": "/lists/{list_id}",
            "required_params": ["list_id"],
            "optional_params": [],
            "display_name": "Delete List",
            "description": "Delete a list from Affinity CRM",
            "group": "Lists",
            "tags": ["list", "collection", "delete"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Delete list",
                    "input": {"list_id": 98765}
                }
            ]
        },
        
        # LIST ENTRY OPERATIONS (4 operations)
        "get_list_entries": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/list-entries",
            "required_params": ["list_id"],
            "optional_params": ["page_size", "page_token"],
            "display_name": "Get List Entries",
            "description": "Get entries from a specific list",
            "group": "List Entries",
            "tags": ["list entries", "list items"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get list entries",
                    "input": {"list_id": 98765, "page_size": 50}
                }
            ]
        },
        
        "create_list_entry": {
            "method": "POST",
            "endpoint": "/lists/{list_id}/list-entries",
            "required_params": ["list_id", "entity_id"],
            "optional_params": ["creator_id"],
            "body_parameters": ["entity_id", "creator_id"],
            "display_name": "Create List Entry",
            "description": "Add an entity to a list",
            "group": "List Entries",
            "tags": ["list entry", "add to list"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Add person to list",
                    "input": {
                        "list_id": 98765,
                        "entity_id": 12345
                    }
                }
            ]
        },
        
        "update_list_entry": {
            "method": "PUT",
            "endpoint": "/list-entries/{list_entry_id}",
            "required_params": ["list_entry_id"],
            "optional_params": [],
            "body_parameters": [],
            "display_name": "Update List Entry",
            "description": "Update a list entry",
            "group": "List Entries",
            "tags": ["list entry", "update"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Update list entry",
                    "input": {"list_entry_id": 11111}
                }
            ]
        },
        
        "delete_list_entry": {
            "method": "DELETE",
            "endpoint": "/list-entries/{list_entry_id}",
            "required_params": ["list_entry_id"],
            "optional_params": [],
            "display_name": "Delete List Entry",
            "description": "Remove an entry from a list",
            "group": "List Entries",
            "tags": ["list entry", "remove from list"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Remove entry from list",
                    "input": {"list_entry_id": 11111}
                }
            ]
        },
        
        # FIELD OPERATIONS (5 operations)
        "get_fields": {
            "method": "GET",
            "endpoint": "/fields",
            "required_params": [],
            "optional_params": ["page_size", "page_token"],
            "display_name": "Get Fields",
            "description": "Retrieve all custom fields from Affinity CRM",
            "group": "Fields",
            "tags": ["fields", "custom fields"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get all fields",
                    "input": {"page_size": 50}
                }
            ]
        },
        
        "get_field": {
            "method": "GET",
            "endpoint": "/fields/{field_id}",
            "required_params": ["field_id"],
            "optional_params": [],
            "display_name": "Get Field",
            "description": "Get a specific custom field by ID",
            "group": "Fields",
            "tags": ["field", "custom field", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get field details",
                    "input": {"field_id": 33333}
                }
            ]
        },
        
        "create_field": {
            "method": "POST",
            "endpoint": "/fields",
            "required_params": ["field_name", "field_type"],
            "optional_params": [],
            "body_parameters": ["name", "value_type"],
            "display_name": "Create Field",
            "description": "Create a new custom field in Affinity CRM",
            "group": "Fields",
            "tags": ["field", "custom field", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "field_mapping": {
                "input_transforms": {
                    "field_name": "name",
                    "field_type": "value_type"
                }
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Create text field",
                    "input": {
                        "field_name": "Investment Stage",
                        "field_type": "text"
                    }
                }
            ]
        },
        
        "update_field": {
            "method": "PUT",
            "endpoint": "/fields/{field_id}",
            "required_params": ["field_id"],
            "optional_params": ["field_name"],
            "body_parameters": ["name"],
            "display_name": "Update Field",
            "description": "Update an existing custom field in Affinity CRM",
            "group": "Fields",
            "tags": ["field", "custom field", "update"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "field_mapping": {
                "input_transforms": {
                    "field_name": "name"
                }
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Update field name",
                    "input": {
                        "field_id": 33333,
                        "field_name": "Deal Stage"
                    }
                }
            ]
        },
        
        "delete_field": {
            "method": "DELETE",
            "endpoint": "/fields/{field_id}",
            "required_params": ["field_id"],
            "optional_params": [],
            "display_name": "Delete Field",
            "description": "Delete a custom field from Affinity CRM",
            "group": "Fields",
            "tags": ["field", "custom field", "delete"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Delete field",
                    "input": {"field_id": 33333}
                }
            ]
        },
        
        # FIELD VALUE OPERATIONS (2 operations)
        "get_field_values": {
            "method": "GET",
            "endpoint": "/field-values",
            "required_params": [],
            "optional_params": ["page_size", "page_token"],
            "display_name": "Get Field Values",
            "description": "Retrieve field values from Affinity CRM",
            "group": "Field Values",
            "tags": ["field values", "custom data"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get field values",
                    "input": {"page_size": 50}
                }
            ]
        },
        
        "update_field_values": {
            "method": "PUT",
            "endpoint": "/field-values",
            "required_params": ["field_values"],
            "optional_params": [],
            "body_parameters": ["field_values"],
            "display_name": "Update Field Values",
            "description": "Update field values in Affinity CRM",
            "group": "Field Values",
            "tags": ["field values", "custom data", "update"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "field_values": [
                    {"template": {"field_id": "value"}, "description": "Field ID to value mapping"},
                    {"template": {"12345": "Series A"}, "description": "Investment stage field example"},
                    {"template": {"67890": "2500000"}, "description": "Deal size field example"},
                    {"template": {"11111": "2025-08-25"}, "description": "Date field example"},
                    {"template": {"22222": ["Tech", "SaaS"]}, "description": "Multi-select field example"}
                ]
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Update field values",
                    "input": {
                        "field_values": {
                            "33333": "Series A",
                            "44444": "2500000"
                        }
                    }
                }
            ]
        },
        
        # SEARCH OPERATIONS (3 operations)
        "search_persons": {
            "method": "GET",
            "endpoint": "/persons/search",
            "required_params": ["term"],
            "optional_params": ["page_size", "page_token"],
            "display_name": "Search Persons",
            "description": "Search for persons in Affinity CRM",
            "group": "Search",
            "tags": ["search", "persons", "find"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Search for John Doe",
                    "input": {
                        "term": "john doe",
                        "page_size": 20
                    }
                }
            ]
        },
        
        "search_companies": {
            "method": "GET",
            "endpoint": "/organizations/search",
            "required_params": ["term"],
            "optional_params": ["page_size", "page_token"],
            "display_name": "Search Companies",
            "description": "Search for companies/organizations in Affinity CRM",
            "group": "Search",
            "tags": ["search", "companies", "organizations", "find"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Search for Acme",
                    "input": {
                        "term": "acme",
                        "page_size": 20
                    }
                }
            ]
        },
        
        "search_opportunities": {
            "method": "GET",
            "endpoint": "/opportunities/search",
            "required_params": ["term"],
            "optional_params": ["page_size", "page_token"],
            "display_name": "Search Opportunities",
            "description": "Search for opportunities in Affinity CRM",
            "group": "Search",
            "tags": ["search", "opportunities", "deals", "find"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Search for Series A",
                    "input": {
                        "term": "series a",
                        "page_size": 20
                    }
                }
            ]
        },
        
        # INTERACTION OPERATIONS (2 operations)
        "get_interactions": {
            "method": "GET",
            "endpoint": "/interactions",
            "required_params": [],
            "optional_params": ["page_size", "page_token"],
            "display_name": "Get Interactions",
            "description": "Retrieve interactions from Affinity CRM",
            "group": "Interactions",
            "tags": ["interactions", "communications"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get recent interactions",
                    "input": {"page_size": 50}
                }
            ]
        },
        
        "create_interaction": {
            "method": "POST",
            "endpoint": "/interactions",
            "required_params": [],
            "optional_params": ["interaction_type", "interaction_date", "interaction_content", "person_ids"],
            "body_parameters": ["type", "date", "content", "person_ids"],
            "display_name": "Create Interaction",
            "description": "Create a new interaction in Affinity CRM",
            "group": "Interactions",
            "tags": ["interaction", "communication", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "person_ids": [
                    {"template": 12345, "description": "Primary interaction participant"},
                    {"template": 67890, "description": "Meeting attendee ID"},
                    {"template": 54321, "description": "Additional stakeholder ID"}
                ]
            },
            
            "field_mapping": {
                "input_transforms": {
                    "interaction_type": "type",
                    "interaction_date": "date",
                    "interaction_content": "content"
                }
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Create meeting interaction",
                    "input": {
                        "interaction_type": "meeting",
                        "interaction_date": "2025-08-25T10:30:00Z",
                        "interaction_content": "Discussed Series A funding",
                        "person_ids": [12345]
                    }
                }
            ]
        },
        
        # WEBHOOK OPERATIONS (3 operations)
        "get_webhooks": {
            "method": "GET",
            "endpoint": "/webhooks",
            "required_params": [],
            "optional_params": ["page_size", "page_token"],
            "display_name": "Get Webhooks",
            "description": "Retrieve webhooks from Affinity CRM",
            "group": "Webhooks",
            "tags": ["webhooks", "notifications"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "pagination": {
                "type": "token",
                "page_size_param": "page_size",
                "page_token_param": "page_token",
                "response_token_field": "next_page_token",
                "max_page_size": 500
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get all webhooks",
                    "input": {"page_size": 50}
                }
            ]
        },
        
        "create_webhook": {
            "method": "POST",
            "endpoint": "/webhooks",
            "required_params": ["webhook_url", "subscriptions"],
            "optional_params": [],
            "body_parameters": ["url", "subscriptions"],
            "display_name": "Create Webhook",
            "description": "Create a new webhook in Affinity CRM",
            "group": "Webhooks",
            "tags": ["webhook", "notification", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "subscriptions": [
                    {"template": "person.created", "description": "Subscribe to person creation events"},
                    {"template": "person.updated", "description": "Subscribe to person update events"},
                    {"template": "person.deleted", "description": "Subscribe to person deletion events"},
                    {"template": "organization.created", "description": "Subscribe to organization creation events"},
                    {"template": "organization.updated", "description": "Subscribe to organization update events"},
                    {"template": "opportunity.created", "description": "Subscribe to opportunity creation events"},
                    {"template": "opportunity.updated", "description": "Subscribe to opportunity update events"},
                    {"template": "list_entry.created", "description": "Subscribe to list entry creation events"},
                    {"template": "field_value.updated", "description": "Subscribe to field value update events"}
                ]
            },
            
            "field_mapping": {
                "input_transforms": {
                    "webhook_url": "url"
                }
            },
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Create webhook for person events",
                    "input": {
                        "webhook_url": "https://api.yourapp.com/webhooks/affinity",
                        "subscriptions": ["person.created", "person.updated"]
                    }
                }
            ]
        },
        
        "delete_webhook": {
            "method": "DELETE",
            "endpoint": "/webhooks/{webhook_id}",
            "required_params": ["webhook_id"],
            "optional_params": [],
            "display_name": "Delete Webhook",
            "description": "Delete a webhook from Affinity CRM",
            "group": "Webhooks",
            "tags": ["webhook", "notification", "delete"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Delete webhook",
                    "input": {"webhook_id": 55555}
                }
            ]
        },
        
        # UTILITY OPERATIONS (1 operation)
        "whoami": {
            "method": "GET",
            "endpoint": "/auth/whoami",
            "required_params": [],
            "optional_params": [],
            "display_name": "Who Am I",
            "description": "Get current user information and validate API key",
            "group": "Authentication",
            "tags": ["auth", "user", "validate"],
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["AFFINITY_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "basic_auth"
            },
            
            "examples": [
                {
                    "name": "Get user info",
                    "input": {}
                }
            ]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the FULLY RESTORED Affinity node with embedded configuration."""
        # Initialize the Enhanced UniversalRequestNode with embedded config first
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        super().__init__(sandbox_timeout=sandbox_timeout)
        logger.debug("AffinityNode FULLY RESTORED with all 40 operations + enhanced features")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"AffinityNode executing operation: {node_data.get('params', {}).get('operation')}")
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

    @staticmethod
    def format_response(response_data: Any) -> Dict[str, Any]:
        """Format response data consistently."""
        if isinstance(response_data, dict):
            return response_data
        elif isinstance(response_data, list):
            return {"items": response_data, "count": len(response_data)}
        else:
            return {"result": response_data}

    def get_operation_count(self) -> int:
        """Get the total number of operations - for verification."""
        return len(self.OPERATIONS)

# Export the node class
__all__ = ["AffinityNode"]