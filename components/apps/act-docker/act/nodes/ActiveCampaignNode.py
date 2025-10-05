#!/usr/bin/env python3
"""
ActiveCampaign Node - Enhanced with ALL 66+ operations and 13 advanced features following OpenAI template
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

class ActiveCampaignNode(BaseNode):
    """
    Enhanced ActiveCampaign node with ALL 66+ operations and 13 advanced features.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "activecampaign",
            "display_name": "ActiveCampaign",
            "description": "Comprehensive ActiveCampaign API integration for email marketing automation, CRM, contacts, deals, campaigns, lists, accounts, e-commerce, and advanced automation workflows",
            "category": "marketing",
            "vendor": "activecampaign",
            "version": "3.0.0",
            "author": "ACT Workflow",
            "tags": ["email", "marketing", "automation", "crm", "contacts", "campaigns", "deals", "ecommerce", "accounts"],
            "documentation_url": "https://developers.activecampaign.com",
            "icon": "https://www.activecampaign.com/favicon.ico",
            "color": "#365DF0",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "{base_url}",  # Dynamic base URL from user input
            "authentication": {
                "type": "api_key",
                "header": "Api-Token"
            },
            "default_headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ACT-Workflow/3.0"
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
            "cost_per_1k_requests": 1.00,
            "cost_per_request": 0.001,
            "billing_unit": "requests",
            "free_tier_limit": 500
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
                "exclude_params": ["timestamp", "offset", "limit"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/contacts"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://developers.activecampaign.com/reference",
            "setup_guide": "https://developers.activecampaign.com/docs",
            "troubleshooting": "https://help.activecampaign.com/hc/en-us",
            "changelog": "https://developers.activecampaign.com/changelog"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "ActiveCampaign API key (Api-Token)",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-f0-9-]+$",
                    "message": "API key must contain only lowercase letters, numbers, and hyphens",
                    "minLength": 10,
                    "maxLength": 100
                }
            },
            "base_url": {
                "type": "string",
                "description": "ActiveCampaign API base URL (e.g., https://yoursubdomain.api-us1.com/api/3)",
                "required": True,
                "group": "Authentication",
                "examples": ["https://yoursubdomain.api-us1.com/api/3", "https://example.api-us1.com/api/3"],
                "validation": {
                    "pattern": "^https://[a-zA-Z0-9-]+\\.api-[a-z0-9]+\\.com/api/3$",
                    "message": "Base URL must be a valid ActiveCampaign API URL format"
                }
            },
            "operation": {
                "type": "string",
                "description": "The ActiveCampaign operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    # Contact operations (14)
                    "list_contacts", "get_contact", "create_contact", "update_contact", "delete_contact", 
                    "sync_contact", "get_contact_by_email", "create_contact_custom_field", 
                    "update_contact_custom_field", "list_contact_custom_fields", "get_contact_custom_field_value",
                    "list_contact_activities", "create_contact_note", "update_contact_note",
                    
                    # Deal operations (10) 
                    "list_deals", "get_deal", "create_deal", "update_deal", "delete_deal",
                    "list_deal_stages", "get_deal_stage", "create_deal_stage", "update_deal_stage", "delete_deal_stage",
                    
                    # Campaign operations (8)
                    "list_campaigns", "get_campaign", "create_campaign", "update_campaign", "delete_campaign",
                    "get_campaign_links", "list_campaign_activities", "send_campaign",
                    
                    # List operations (8)
                    "list_lists", "get_list", "create_list", "update_list", "delete_list",
                    "add_contact_to_list", "remove_contact_from_list", "get_list_status",
                    
                    # Automation operations (6)
                    "list_automations", "get_automation", "add_contact_to_automation", 
                    "remove_contact_from_automation", "list_automation_contacts", "get_automation_contact_status",
                    
                    # Tag operations (6)
                    "list_tags", "get_tag", "create_tag", "update_tag", "delete_tag", "add_tag_to_contact",
                    
                    # Account operations (6)
                    "list_accounts", "get_account", "create_account", "update_account", "delete_account",
                    "create_account_contact_association",
                    
                    # E-commerce operations (8)
                    "list_ecom_orders", "get_ecom_order", "create_ecom_order", "update_ecom_order", "delete_ecom_order",
                    "list_ecom_customers", "create_ecom_customer", "update_ecom_customer"
                ]
            },
            # Resource IDs for different operations
            "contact_id": {"type": "integer", "description": "Contact ID", "required": False, "group": "Resource"},
            "deal_id": {"type": "integer", "description": "Deal ID", "required": False, "group": "Resource"}, 
            "campaign_id": {"type": "integer", "description": "Campaign ID", "required": False, "group": "Resource"},
            "list_id": {"type": "integer", "description": "List ID", "required": False, "group": "Resource"},
            "automation_id": {"type": "integer", "description": "Automation ID", "required": False, "group": "Resource"},
            "tag_id": {"type": "integer", "description": "Tag ID", "required": False, "group": "Resource"},
            "account_id": {"type": "integer", "description": "Account ID", "required": False, "group": "Resource"},
            "order_id": {"type": "integer", "description": "Order ID", "required": False, "group": "Resource"},
            
            # Pagination parameters
            "offset": {"type": "integer", "description": "Offset for pagination", "required": False, "default": 0, "group": "Pagination"},
            "limit": {"type": "integer", "description": "Number of items to return (max 100)", "required": False, "default": 20, "group": "Pagination"},
            
            # Search and filtering
            "search": {"type": "string", "description": "Search query for filtering results", "required": False, "group": "Filtering"},
            "filters": {"type": "object", "description": "Additional filters", "required": False, "group": "Filtering"},
            "email": {"type": "string", "description": "Email address for contact operations", "required": False, "group": "Filtering"},
            
            # Data objects for create/update operations
            "contact_data": {"type": "object", "description": "Contact data for create/update operations", "required": False, "group": "Data"},
            "deal_data": {"type": "object", "description": "Deal data for create/update operations", "required": False, "group": "Data"},
            "campaign_data": {"type": "object", "description": "Campaign data for create operations", "required": False, "group": "Data"},
            "list_data": {"type": "object", "description": "List data for create/update operations", "required": False, "group": "Data"},
            "tag_data": {"type": "object", "description": "Tag data for create operations", "required": False, "group": "Data"},
            "account_data": {"type": "object", "description": "Account data for create/update operations", "required": False, "group": "Data"},
            "order_data": {"type": "object", "description": "Order data for create/update operations", "required": False, "group": "Data"},
            "custom_field_data": {"type": "object", "description": "Custom field data", "required": False, "group": "Data"}
        },
        
        # Enhanced output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful ActiveCampaign API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from ActiveCampaign API"},
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
                    "error_code": {"type": "string", "description": "ActiveCampaign error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration for all operations
        "auth": {
            # Contact operations
            "list_contacts": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_contact": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_contact": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "update_contact": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "delete_contact": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "sync_contact": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_contact_by_email": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_contact_custom_field": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "update_contact_custom_field": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "list_contact_custom_fields": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_contact_custom_field_value": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "list_contact_activities": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_contact_note": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "update_contact_note": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            
            # Deal operations
            "list_deals": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_deal": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_deal": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "update_deal": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "delete_deal": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "list_deal_stages": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_deal_stage": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_deal_stage": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "update_deal_stage": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "delete_deal_stage": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            
            # Campaign operations
            "list_campaigns": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_campaign": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_campaign": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "update_campaign": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "delete_campaign": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_campaign_links": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "list_campaign_activities": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "send_campaign": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            
            # List operations
            "list_lists": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_list": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_list": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "update_list": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "delete_list": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "add_contact_to_list": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "remove_contact_from_list": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_list_status": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            
            # Continue for all 66+ operations...
            "list_automations": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_automation": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "add_contact_to_automation": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "remove_contact_from_automation": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "list_automation_contacts": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_automation_contact_status": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            
            "list_tags": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_tag": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_tag": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "update_tag": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "delete_tag": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "add_tag_to_contact": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            
            "list_accounts": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_account": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_account": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "update_account": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "delete_account": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_account_contact_association": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            
            "list_ecom_orders": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "get_ecom_order": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_ecom_order": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "update_ecom_order": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "delete_ecom_order": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "list_ecom_customers": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "create_ecom_customer": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "update_ecom_customer": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []}
        },
        
        # Error codes specific to ActiveCampaign
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid API key or insufficient permissions",
            "403": "Forbidden - Access denied to resource",
            "404": "Not Found - Resource not found",
            "422": "Unprocessable Entity - Validation errors in request data",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - ActiveCampaign server error",
            "502": "Bad Gateway - ActiveCampaign server temporarily unavailable",
            "503": "Service Unavailable - ActiveCampaign server overloaded"
        }
    }
    
    # Enhanced operation definitions with ALL 66+ operations
    OPERATIONS = {
        # ========== CONTACT OPERATIONS (14) ==========
        "list_contacts": {
            "method": "GET",
            "endpoint": "/contacts",
            "required_params": [],
            "optional_params": ["offset", "limit", "search", "filters"],
            "display_name": "List Contacts",
            "description": "Retrieve a list of contacts from ActiveCampaign",
            "group": "Contacts",
            "tags": ["contacts", "list", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List first 10 contacts", "input": {"limit": 10}}]
        },
        "get_contact": {
            "method": "GET",
            "endpoint": "/contacts/{contact_id}",
            "required_params": ["contact_id"],
            "optional_params": [],
            "display_name": "Get Contact",
            "description": "Retrieve a specific contact by ID",
            "group": "Contacts",
            "tags": ["contacts", "get", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get contact by ID", "input": {"contact_id": 123}}]
        },
        "create_contact": {
            "method": "POST",
            "endpoint": "/contacts",
            "required_params": ["contact_data"],
            "optional_params": [],
            "body_parameters": ["contact_data"],
            "display_name": "Create Contact",
            "description": "Create a new contact in ActiveCampaign",
            "group": "Contacts",
            "tags": ["contacts", "create", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Create basic contact", "input": {"contact_data": {"email": "john@example.com", "firstName": "John", "lastName": "Doe"}}}],
            
            # Array templates for complex contact data
            "array_templates": {
                "fieldValues": [
                    {"template": {"field": "1", "value": "Company Name"}, "description": "Custom field assignment"},
                    {"template": {"field": "2", "value": "Position Title"}, "description": "Another custom field"}
                ],
                "tags": [
                    {"template": "VIP Customer", "description": "Tag for VIP customers"},
                    {"template": "Newsletter Subscriber", "description": "Newsletter subscription tag"}
                ],
                "listMemberships": [
                    {"template": {"list": 1, "status": "active"}, "description": "Active list membership"},
                    {"template": {"list": 2, "status": "active"}, "description": "Additional list membership"}
                ]
            }
        },
        "update_contact": {
            "method": "PUT",
            "endpoint": "/contacts/{contact_id}",
            "required_params": ["contact_id", "contact_data"],
            "optional_params": [],
            "body_parameters": ["contact_data"],
            "display_name": "Update Contact",
            "description": "Update an existing contact",
            "group": "Contacts",
            "tags": ["contacts", "update", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Update contact", "input": {"contact_id": 123, "contact_data": {"firstName": "Jane"}}}],
            
            # Array templates for contact updates
            "array_templates": {
                "fieldValues": [
                    {"template": {"field": "1", "value": "Updated Company Name"}, "description": "Update custom field value"},
                    {"template": {"field": "2", "value": "New Position"}, "description": "Update another custom field"}
                ],
                "tags": [
                    {"template": "Premium Customer", "description": "Upgrade customer status"},
                    {"template": "Active User", "description": "Activity tracking tag"}
                ]
            }
        },
        "delete_contact": {
            "method": "DELETE",
            "endpoint": "/contacts/{contact_id}",
            "required_params": ["contact_id"],
            "optional_params": [],
            "display_name": "Delete Contact",
            "description": "Delete a contact from ActiveCampaign",
            "group": "Contacts",
            "tags": ["contacts", "delete", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Delete contact", "input": {"contact_id": 123}}]
        },
        "sync_contact": {
            "method": "POST",
            "endpoint": "/contact/sync",
            "required_params": ["contact_data"],
            "optional_params": [],
            "body_parameters": ["contact_data"],
            "display_name": "Sync Contact",
            "description": "Sync a contact (create or update based on email)",
            "group": "Contacts",
            "tags": ["contacts", "sync", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Sync contact", "input": {"contact_data": {"email": "user@example.com", "firstName": "User"}}}],
            
            # Array templates for contact sync with arrays
            "array_templates": {
                "fieldValues": [
                    {"template": {"field": "1", "value": "Synced Company"}, "description": "Custom field for sync"},
                    {"template": {"field": "2", "value": "Import Source"}, "description": "Track sync source"}
                ],
                "tags": [
                    {"template": "Imported Contact", "description": "Tag for imported contacts"},
                    {"template": "Data Sync", "description": "Sync operation tag"}
                ]
            }
        },
        "get_contact_by_email": {
            "method": "GET",
            "endpoint": "/contacts",
            "required_params": ["email"],
            "optional_params": [],
            "display_name": "Get Contact by Email",
            "description": "Find a contact by email address",
            "group": "Contacts",
            "tags": ["contacts", "search", "email"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Find contact by email", "input": {"email": "user@example.com"}}]
        },
        "create_contact_custom_field": {
            "method": "POST",
            "endpoint": "/fields",
            "required_params": ["custom_field_data"],
            "optional_params": [],
            "body_parameters": ["custom_field_data"],
            "display_name": "Create Contact Custom Field",
            "description": "Create a custom field for contacts",
            "group": "Contacts",
            "tags": ["contacts", "custom-fields", "create"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Create custom field", "input": {"custom_field_data": {"type": "text", "title": "Company", "descript": "Company name"}}}]
        },
        "update_contact_custom_field": {
            "method": "PUT",
            "endpoint": "/fields/{field_id}",
            "required_params": ["field_id", "custom_field_data"],
            "optional_params": [],
            "body_parameters": ["custom_field_data"],
            "display_name": "Update Contact Custom Field",
            "description": "Update a contact custom field",
            "group": "Contacts",
            "tags": ["contacts", "custom-fields", "update"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Update custom field", "input": {"field_id": 1, "custom_field_data": {"title": "Company Name"}}}]
        },
        "list_contact_custom_fields": {
            "method": "GET",
            "endpoint": "/fields",
            "required_params": [],
            "optional_params": ["limit", "offset"],
            "display_name": "List Contact Custom Fields",
            "description": "List all custom fields for contacts",
            "group": "Contacts",
            "tags": ["contacts", "custom-fields", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List custom fields", "input": {}}]
        },
        "get_contact_custom_field_value": {
            "method": "GET",
            "endpoint": "/fieldValues",
            "required_params": ["contact_id"],
            "optional_params": ["field_id"],
            "display_name": "Get Contact Custom Field Value",
            "description": "Get custom field values for a contact",
            "group": "Contacts",
            "tags": ["contacts", "custom-fields", "values"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get field values", "input": {"contact_id": 123}}]
        },
        "list_contact_activities": {
            "method": "GET",
            "endpoint": "/activities",
            "required_params": [],
            "optional_params": ["contact_id", "limit", "offset"],
            "display_name": "List Contact Activities",
            "description": "List activities for contacts",
            "group": "Contacts",
            "tags": ["contacts", "activities", "tracking"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List activities", "input": {"contact_id": 123}}]
        },
        "create_contact_note": {
            "method": "POST",
            "endpoint": "/notes",
            "required_params": ["contact_id", "note_data"],
            "optional_params": [],
            "body_parameters": ["note_data"],
            "display_name": "Create Contact Note",
            "description": "Create a note for a contact",
            "group": "Contacts",
            "tags": ["contacts", "notes", "create"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Create note", "input": {"contact_id": 123, "note_data": {"note": "Important client meeting scheduled"}}}]
        },
        "update_contact_note": {
            "method": "PUT",
            "endpoint": "/notes/{note_id}",
            "required_params": ["note_id", "note_data"],
            "optional_params": [],
            "body_parameters": ["note_data"],
            "display_name": "Update Contact Note",
            "description": "Update a contact note",
            "group": "Contacts",
            "tags": ["contacts", "notes", "update"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Update note", "input": {"note_id": 456, "note_data": {"note": "Meeting completed successfully"}}}]
        },

        # ========== DEAL OPERATIONS (10) ==========
        "list_deals": {
            "method": "GET",
            "endpoint": "/deals",
            "required_params": [],
            "optional_params": ["offset", "limit", "search", "filters"],
            "display_name": "List Deals",
            "description": "Retrieve a list of deals from ActiveCampaign",
            "group": "Deals",
            "tags": ["deals", "list", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List all deals", "input": {"limit": 20}}]
        },
        "get_deal": {
            "method": "GET",
            "endpoint": "/deals/{deal_id}",
            "required_params": ["deal_id"],
            "optional_params": [],
            "display_name": "Get Deal",
            "description": "Retrieve a specific deal by ID",
            "group": "Deals",
            "tags": ["deals", "get", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get deal by ID", "input": {"deal_id": 123}}]
        },
        "create_deal": {
            "method": "POST",
            "endpoint": "/deals",
            "required_params": ["deal_data"],
            "optional_params": [],
            "body_parameters": ["deal_data"],
            "display_name": "Create Deal",
            "description": "Create a new deal in ActiveCampaign",
            "group": "Deals",
            "tags": ["deals", "create", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Create deal", "input": {"deal_data": {"title": "New Opportunity", "value": 5000, "currency": "USD"}}}],
            
            # Array templates for deal custom fields and tasks
            "array_templates": {
                "dealCustomFieldData": [
                    {"template": {"customFieldId": "1", "fieldValue": "Enterprise"}, "description": "Deal category custom field"},
                    {"template": {"customFieldId": "2", "fieldValue": "Q1 2025"}, "description": "Expected close quarter"}
                ],
                "dealTasks": [
                    {"template": {"title": "Initial Discovery Call", "note": "Schedule discovery call with prospect"}, "description": "First task template"},
                    {"template": {"title": "Proposal Preparation", "note": "Prepare proposal based on requirements"}, "description": "Follow-up task template"}
                ]
            }
        },
        "update_deal": {
            "method": "PUT",
            "endpoint": "/deals/{deal_id}",
            "required_params": ["deal_id", "deal_data"],
            "optional_params": [],
            "body_parameters": ["deal_data"],
            "display_name": "Update Deal",
            "description": "Update an existing deal",
            "group": "Deals",
            "tags": ["deals", "update", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Update deal", "input": {"deal_id": 123, "deal_data": {"value": 7500}}}]
        },
        "delete_deal": {
            "method": "DELETE",
            "endpoint": "/deals/{deal_id}",
            "required_params": ["deal_id"],
            "optional_params": [],
            "display_name": "Delete Deal",
            "description": "Delete a deal from ActiveCampaign",
            "group": "Deals",
            "tags": ["deals", "delete", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Delete deal", "input": {"deal_id": 123}}]
        },
        "list_deal_stages": {
            "method": "GET",
            "endpoint": "/dealStages",
            "required_params": [],
            "optional_params": ["limit", "offset"],
            "display_name": "List Deal Stages",
            "description": "List all deal stages",
            "group": "Deals",
            "tags": ["deals", "stages", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List deal stages", "input": {}}]
        },
        "get_deal_stage": {
            "method": "GET",
            "endpoint": "/dealStages/{stage_id}",
            "required_params": ["stage_id"],
            "optional_params": [],
            "display_name": "Get Deal Stage",
            "description": "Get a specific deal stage",
            "group": "Deals",
            "tags": ["deals", "stages", "get"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get stage", "input": {"stage_id": 1}}]
        },
        "create_deal_stage": {
            "method": "POST",
            "endpoint": "/dealStages",
            "required_params": ["stage_data"],
            "optional_params": [],
            "body_parameters": ["stage_data"],
            "display_name": "Create Deal Stage",
            "description": "Create a new deal stage",
            "group": "Deals",
            "tags": ["deals", "stages", "create"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Create stage", "input": {"stage_data": {"title": "Qualification", "group": "1"}}}]
        },
        "update_deal_stage": {
            "method": "PUT",
            "endpoint": "/dealStages/{stage_id}",
            "required_params": ["stage_id", "stage_data"],
            "optional_params": [],
            "body_parameters": ["stage_data"],
            "display_name": "Update Deal Stage",
            "description": "Update a deal stage",
            "group": "Deals",
            "tags": ["deals", "stages", "update"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Update stage", "input": {"stage_id": 1, "stage_data": {"title": "Initial Qualification"}}}]
        },
        "delete_deal_stage": {
            "method": "DELETE",
            "endpoint": "/dealStages/{stage_id}",
            "required_params": ["stage_id"],
            "optional_params": [],
            "display_name": "Delete Deal Stage",
            "description": "Delete a deal stage",
            "group": "Deals",
            "tags": ["deals", "stages", "delete"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Delete stage", "input": {"stage_id": 1}}]
        },

        # ========== CAMPAIGN OPERATIONS (8) ==========
        "list_campaigns": {
            "method": "GET",
            "endpoint": "/campaigns",
            "required_params": [],
            "optional_params": ["offset", "limit", "search", "filters"],
            "display_name": "List Campaigns",
            "description": "Retrieve a list of campaigns from ActiveCampaign",
            "group": "Campaigns",
            "tags": ["campaigns", "list", "email"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List campaigns", "input": {"limit": 20}}]
        },
        "get_campaign": {
            "method": "GET",
            "endpoint": "/campaigns/{campaign_id}",
            "required_params": ["campaign_id"],
            "optional_params": [],
            "display_name": "Get Campaign",
            "description": "Retrieve a specific campaign by ID",
            "group": "Campaigns",
            "tags": ["campaigns", "get", "email"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get campaign", "input": {"campaign_id": 123}}]
        },
        "create_campaign": {
            "method": "POST",
            "endpoint": "/campaigns",
            "required_params": ["campaign_data"],
            "optional_params": [],
            "body_parameters": ["campaign_data"],
            "display_name": "Create Campaign",
            "description": "Create a new email campaign",
            "group": "Campaigns",
            "tags": ["campaigns", "create", "email"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Create campaign", "input": {"campaign_data": {"type": "single", "name": "Newsletter", "subject": "Monthly Update"}}}],
            
            # Array templates for campaign lists and segments
            "array_templates": {
                "lists": [
                    {"template": {"listid": "1"}, "description": "Primary mailing list"},
                    {"template": {"listid": "2"}, "description": "Secondary target list"}
                ],
                "segments": [
                    {"template": {"segmentid": "1"}, "description": "VIP customers segment"},
                    {"template": {"segmentid": "2"}, "description": "Active subscribers segment"}
                ],
                "tags": [
                    {"template": "Newsletter Campaign", "description": "Campaign tracking tag"},
                    {"template": "Q1 2025", "description": "Quarterly campaign tag"}
                ]
            }
        },
        "update_campaign": {
            "method": "PUT",
            "endpoint": "/campaigns/{campaign_id}",
            "required_params": ["campaign_id", "campaign_data"],
            "optional_params": [],
            "body_parameters": ["campaign_data"],
            "display_name": "Update Campaign",
            "description": "Update an existing campaign",
            "group": "Campaigns",
            "tags": ["campaigns", "update", "email"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Update campaign", "input": {"campaign_id": 123, "campaign_data": {"subject": "Updated Subject"}}}]
        },
        "delete_campaign": {
            "method": "DELETE",
            "endpoint": "/campaigns/{campaign_id}",
            "required_params": ["campaign_id"],
            "optional_params": [],
            "display_name": "Delete Campaign",
            "description": "Delete a campaign",
            "group": "Campaigns",
            "tags": ["campaigns", "delete", "email"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Delete campaign", "input": {"campaign_id": 123}}]
        },
        "get_campaign_links": {
            "method": "GET",
            "endpoint": "/campaigns/{campaign_id}/links",
            "required_params": ["campaign_id"],
            "optional_params": [],
            "display_name": "Get Campaign Links",
            "description": "Get links tracked in a campaign",
            "group": "Campaigns",
            "tags": ["campaigns", "links", "tracking"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get campaign links", "input": {"campaign_id": 123}}]
        },
        "list_campaign_activities": {
            "method": "GET",
            "endpoint": "/campaigns/{campaign_id}/activities",
            "required_params": ["campaign_id"],
            "optional_params": ["limit", "offset"],
            "display_name": "List Campaign Activities",
            "description": "List activities for a campaign",
            "group": "Campaigns",
            "tags": ["campaigns", "activities", "tracking"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List campaign activities", "input": {"campaign_id": 123}}]
        },
        "send_campaign": {
            "method": "POST",
            "endpoint": "/campaigns/{campaign_id}/actions/send",
            "required_params": ["campaign_id"],
            "optional_params": [],
            "display_name": "Send Campaign",
            "description": "Send a campaign to its subscribers",
            "group": "Campaigns",
            "tags": ["campaigns", "send", "email"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Send campaign", "input": {"campaign_id": 123}}]
        },

        # ========== LIST OPERATIONS (8) ==========
        "list_lists": {
            "method": "GET",
            "endpoint": "/lists",
            "required_params": [],
            "optional_params": ["offset", "limit", "search", "filters"],
            "display_name": "List Lists",
            "description": "Retrieve all contact lists from ActiveCampaign",
            "group": "Lists",
            "tags": ["lists", "list", "email"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List all lists", "input": {"limit": 20}}]
        },
        "get_list": {
            "method": "GET",
            "endpoint": "/lists/{list_id}",
            "required_params": ["list_id"],
            "optional_params": [],
            "display_name": "Get List",
            "description": "Retrieve a specific list by ID",
            "group": "Lists",
            "tags": ["lists", "get", "email"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get list", "input": {"list_id": 123}}]
        },
        "create_list": {
            "method": "POST",
            "endpoint": "/lists",
            "required_params": ["list_data"],
            "optional_params": [],
            "body_parameters": ["list_data"],
            "display_name": "Create List",
            "description": "Create a new contact list",
            "group": "Lists",
            "tags": ["lists", "create", "email"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Create list", "input": {"list_data": {"name": "Newsletter Subscribers", "stringid": "newsletter"}}}]
        },
        "update_list": {
            "method": "PUT",
            "endpoint": "/lists/{list_id}",
            "required_params": ["list_id", "list_data"],
            "optional_params": [],
            "body_parameters": ["list_data"],
            "display_name": "Update List",
            "description": "Update an existing list",
            "group": "Lists",
            "tags": ["lists", "update", "email"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Update list", "input": {"list_id": 123, "list_data": {"name": "Updated Newsletter"}}}]
        },
        "delete_list": {
            "method": "DELETE",
            "endpoint": "/lists/{list_id}",
            "required_params": ["list_id"],
            "optional_params": [],
            "display_name": "Delete List",
            "description": "Delete a contact list",
            "group": "Lists",
            "tags": ["lists", "delete", "email"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Delete list", "input": {"list_id": 123}}]
        },
        "add_contact_to_list": {
            "method": "POST",
            "endpoint": "/contactLists",
            "required_params": ["contact_id", "list_id"],
            "optional_params": [],
            "body_parameters": ["contact_id", "list_id"],
            "display_name": "Add Contact to List",
            "description": "Add a contact to a list",
            "group": "Lists",
            "tags": ["lists", "contacts", "subscribe"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Add contact to list", "input": {"contact_id": 123, "list_id": 456}}],
            
            # Array templates for bulk list operations
            "array_templates": {
                "contactLists": [
                    {"template": {"contact": "123", "list": "456", "status": "1"}, "description": "Active list subscription"},
                    {"template": {"contact": "124", "list": "456", "status": "1"}, "description": "Another contact subscription"}
                ],
                "bulkListSubscriptions": [
                    {"template": {"contacts": ["123", "124", "125"], "list": "456", "status": "active"}, "description": "Bulk list subscription"},
                    {"template": {"contacts": ["126", "127"], "list": "457", "status": "active"}, "description": "Another bulk subscription"}
                ]
            }
        },
        "remove_contact_from_list": {
            "method": "DELETE",
            "endpoint": "/contactLists/{contact_list_id}",
            "required_params": ["contact_list_id"],
            "optional_params": [],
            "display_name": "Remove Contact from List",
            "description": "Remove a contact from a list",
            "group": "Lists",
            "tags": ["lists", "contacts", "unsubscribe"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Remove contact from list", "input": {"contact_list_id": 789}}]
        },
        "get_list_status": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/status",
            "required_params": ["list_id"],
            "optional_params": [],
            "display_name": "Get List Status",
            "description": "Get status information for a list",
            "group": "Lists",
            "tags": ["lists", "status", "info"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get list status", "input": {"list_id": 123}}]
        },

        # ========== AUTOMATION OPERATIONS (6) ==========
        "list_automations": {
            "method": "GET",
            "endpoint": "/automations",
            "required_params": [],
            "optional_params": ["offset", "limit", "search", "filters"],
            "display_name": "List Automations",
            "description": "Retrieve all automations from ActiveCampaign",
            "group": "Automations",
            "tags": ["automations", "list", "workflow"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List automations", "input": {"limit": 20}}]
        },
        "get_automation": {
            "method": "GET",
            "endpoint": "/automations/{automation_id}",
            "required_params": ["automation_id"],
            "optional_params": [],
            "display_name": "Get Automation",
            "description": "Retrieve a specific automation by ID",
            "group": "Automations",
            "tags": ["automations", "get", "workflow"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get automation", "input": {"automation_id": 123}}]
        },
        "add_contact_to_automation": {
            "method": "POST",
            "endpoint": "/contactAutomations",
            "required_params": ["contact_id", "automation_id"],
            "optional_params": [],
            "body_parameters": ["contact_id", "automation_id"],
            "display_name": "Add Contact to Automation",
            "description": "Add a contact to an automation workflow",
            "group": "Automations",
            "tags": ["automations", "contacts", "trigger"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Add contact to automation", "input": {"contact_id": 123, "automation_id": 456}}],
            
            # Array templates for bulk automation assignments
            "array_templates": {
                "contactAutomations": [
                    {"template": {"contact": "123", "automation": "456"}, "description": "Contact automation assignment"},
                    {"template": {"contact": "124", "automation": "456"}, "description": "Another contact assignment"}
                ],
                "automationTriggers": [
                    {"template": {"trigger": "tag_added", "value": "VIP"}, "description": "Tag-based trigger"},
                    {"template": {"trigger": "list_subscribed", "value": "1"}, "description": "List subscription trigger"}
                ]
            }
        },
        "remove_contact_from_automation": {
            "method": "DELETE",
            "endpoint": "/contactAutomations/{contact_automation_id}",
            "required_params": ["contact_automation_id"],
            "optional_params": [],
            "display_name": "Remove Contact from Automation",
            "description": "Remove a contact from an automation",
            "group": "Automations",
            "tags": ["automations", "contacts", "remove"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Remove contact from automation", "input": {"contact_automation_id": 789}}]
        },
        "list_automation_contacts": {
            "method": "GET",
            "endpoint": "/automations/{automation_id}/contacts",
            "required_params": ["automation_id"],
            "optional_params": ["limit", "offset"],
            "display_name": "List Automation Contacts",
            "description": "List contacts in an automation",
            "group": "Automations",
            "tags": ["automations", "contacts", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List automation contacts", "input": {"automation_id": 123}}]
        },
        "get_automation_contact_status": {
            "method": "GET",
            "endpoint": "/contactAutomations",
            "required_params": ["contact_id", "automation_id"],
            "optional_params": [],
            "display_name": "Get Automation Contact Status",
            "description": "Get status of a contact in an automation",
            "group": "Automations",
            "tags": ["automations", "contacts", "status"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get contact status", "input": {"contact_id": 123, "automation_id": 456}}]
        },

        # ========== TAG OPERATIONS (6) ==========
        "list_tags": {
            "method": "GET",
            "endpoint": "/tags",
            "required_params": [],
            "optional_params": ["offset", "limit", "search"],
            "display_name": "List Tags",
            "description": "Retrieve all tags from ActiveCampaign",
            "group": "Tags",
            "tags": ["tags", "list", "organization"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List tags", "input": {"limit": 50}}]
        },
        "get_tag": {
            "method": "GET",
            "endpoint": "/tags/{tag_id}",
            "required_params": ["tag_id"],
            "optional_params": [],
            "display_name": "Get Tag",
            "description": "Retrieve a specific tag by ID",
            "group": "Tags",
            "tags": ["tags", "get", "organization"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get tag", "input": {"tag_id": 123}}]
        },
        "create_tag": {
            "method": "POST",
            "endpoint": "/tags",
            "required_params": ["tag_data"],
            "optional_params": [],
            "body_parameters": ["tag_data"],
            "display_name": "Create Tag",
            "description": "Create a new tag",
            "group": "Tags",
            "tags": ["tags", "create", "organization"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Create tag", "input": {"tag_data": {"tag": "VIP Customer", "tagType": "contact"}}}]
        },
        "update_tag": {
            "method": "PUT",
            "endpoint": "/tags/{tag_id}",
            "required_params": ["tag_id", "tag_data"],
            "optional_params": [],
            "body_parameters": ["tag_data"],
            "display_name": "Update Tag",
            "description": "Update an existing tag",
            "group": "Tags",
            "tags": ["tags", "update", "organization"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Update tag", "input": {"tag_id": 123, "tag_data": {"tag": "Premium Customer"}}}]
        },
        "delete_tag": {
            "method": "DELETE",
            "endpoint": "/tags/{tag_id}",
            "required_params": ["tag_id"],
            "optional_params": [],
            "display_name": "Delete Tag",
            "description": "Delete a tag",
            "group": "Tags",
            "tags": ["tags", "delete", "organization"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Delete tag", "input": {"tag_id": 123}}]
        },
        "add_tag_to_contact": {
            "method": "POST",
            "endpoint": "/contactTags",
            "required_params": ["contact_id", "tag_id"],
            "optional_params": [],
            "body_parameters": ["contact_id", "tag_id"],
            "display_name": "Add Tag to Contact",
            "description": "Add a tag to a contact",
            "group": "Tags",
            "tags": ["tags", "contacts", "assign"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Add tag to contact", "input": {"contact_id": 123, "tag_id": 456}}],
            
            # Array templates for bulk tag assignments
            "array_templates": {
                "contactTags": [
                    {"template": {"contact": "123", "tag": "456"}, "description": "Contact tag assignment"},
                    {"template": {"contact": "123", "tag": "457"}, "description": "Additional tag for same contact"},
                    {"template": {"contact": "124", "tag": "456"}, "description": "Same tag for different contact"}
                ],
                "bulkTagAssignments": [
                    {"template": {"contacts": ["123", "124", "125"], "tag": "VIP"}, "description": "Bulk VIP tag assignment"},
                    {"template": {"contacts": ["126", "127"], "tag": "Newsletter"}, "description": "Bulk newsletter tag assignment"}
                ]
            }
        },

        # ========== ACCOUNT OPERATIONS (6) ==========
        "list_accounts": {
            "method": "GET",
            "endpoint": "/accounts",
            "required_params": [],
            "optional_params": ["offset", "limit", "search", "filters"],
            "display_name": "List Accounts",
            "description": "Retrieve all accounts from ActiveCampaign",
            "group": "Accounts",
            "tags": ["accounts", "list", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List accounts", "input": {"limit": 20}}]
        },
        "get_account": {
            "method": "GET",
            "endpoint": "/accounts/{account_id}",
            "required_params": ["account_id"],
            "optional_params": [],
            "display_name": "Get Account",
            "description": "Retrieve a specific account by ID",
            "group": "Accounts",
            "tags": ["accounts", "get", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get account", "input": {"account_id": 123}}]
        },
        "create_account": {
            "method": "POST",
            "endpoint": "/accounts",
            "required_params": ["account_data"],
            "optional_params": [],
            "body_parameters": ["account_data"],
            "display_name": "Create Account",
            "description": "Create a new account",
            "group": "Accounts",
            "tags": ["accounts", "create", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Create account", "input": {"account_data": {"name": "Acme Corporation", "accountUrl": "https://acme.com"}}}]
        },
        "update_account": {
            "method": "PUT",
            "endpoint": "/accounts/{account_id}",
            "required_params": ["account_id", "account_data"],
            "optional_params": [],
            "body_parameters": ["account_data"],
            "display_name": "Update Account",
            "description": "Update an existing account",
            "group": "Accounts",
            "tags": ["accounts", "update", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Update account", "input": {"account_id": 123, "account_data": {"name": "Acme Corp"}}}]
        },
        "delete_account": {
            "method": "DELETE",
            "endpoint": "/accounts/{account_id}",
            "required_params": ["account_id"],
            "optional_params": [],
            "display_name": "Delete Account",
            "description": "Delete an account",
            "group": "Accounts",
            "tags": ["accounts", "delete", "crm"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Delete account", "input": {"account_id": 123}}]
        },
        "create_account_contact_association": {
            "method": "POST",
            "endpoint": "/accountContacts",
            "required_params": ["account_id", "contact_id"],
            "optional_params": [],
            "body_parameters": ["account_id", "contact_id"],
            "display_name": "Create Account Contact Association",
            "description": "Associate a contact with an account",
            "group": "Accounts",
            "tags": ["accounts", "contacts", "associate"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Associate contact with account", "input": {"account_id": 123, "contact_id": 456}}]
        },

        # ========== E-COMMERCE OPERATIONS (8) ==========
        "list_ecom_orders": {
            "method": "GET",
            "endpoint": "/ecomOrders",
            "required_params": [],
            "optional_params": ["offset", "limit", "search", "filters"],
            "display_name": "List E-commerce Orders",
            "description": "Retrieve all e-commerce orders",
            "group": "E-commerce",
            "tags": ["ecommerce", "orders", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List orders", "input": {"limit": 20}}]
        },
        "get_ecom_order": {
            "method": "GET",
            "endpoint": "/ecomOrders/{order_id}",
            "required_params": ["order_id"],
            "optional_params": [],
            "display_name": "Get E-commerce Order",
            "description": "Retrieve a specific e-commerce order",
            "group": "E-commerce",
            "tags": ["ecommerce", "orders", "get"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Get order", "input": {"order_id": 123}}]
        },
        "create_ecom_order": {
            "method": "POST",
            "endpoint": "/ecomOrders",
            "required_params": ["order_data"],
            "optional_params": [],
            "body_parameters": ["order_data"],
            "display_name": "Create E-commerce Order",
            "description": "Create a new e-commerce order",
            "group": "E-commerce",
            "tags": ["ecommerce", "orders", "create"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Create order", "input": {"order_data": {"externalid": "ORDER001", "email": "customer@example.com", "totalPrice": 10000}}}],
            
            # Array templates for e-commerce order items and products
            "array_templates": {
                "orderProducts": [
                    {"template": {"name": "Product Name", "price": 2500, "quantity": 2, "externalid": "PROD001"}, "description": "Order line item"},
                    {"template": {"name": "Another Product", "price": 5000, "quantity": 1, "externalid": "PROD002"}, "description": "Additional product"}
                ],
                "orderDiscounts": [
                    {"template": {"name": "10% Off Coupon", "type": "percentage", "value": 10}, "description": "Percentage discount"},
                    {"template": {"name": "$5 Off", "type": "fixed", "value": 500}, "description": "Fixed amount discount"}
                ],
                "customFields": [
                    {"template": {"field": "gift_message", "value": "Happy Birthday!"}, "description": "Gift message custom field"},
                    {"template": {"field": "delivery_instructions", "value": "Leave at door"}, "description": "Delivery instructions"}
                ]
            }
        },
        "update_ecom_order": {
            "method": "PUT",
            "endpoint": "/ecomOrders/{order_id}",
            "required_params": ["order_id", "order_data"],
            "optional_params": [],
            "body_parameters": ["order_data"],
            "display_name": "Update E-commerce Order",
            "description": "Update an existing e-commerce order",
            "group": "E-commerce",
            "tags": ["ecommerce", "orders", "update"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Update order", "input": {"order_id": 123, "order_data": {"totalPrice": 12000}}}]
        },
        "delete_ecom_order": {
            "method": "DELETE",
            "endpoint": "/ecomOrders/{order_id}",
            "required_params": ["order_id"],
            "optional_params": [],
            "display_name": "Delete E-commerce Order",
            "description": "Delete an e-commerce order",
            "group": "E-commerce",
            "tags": ["ecommerce", "orders", "delete"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Delete order", "input": {"order_id": 123}}]
        },
        "list_ecom_customers": {
            "method": "GET",
            "endpoint": "/ecomCustomers",
            "required_params": [],
            "optional_params": ["offset", "limit", "search", "filters"],
            "display_name": "List E-commerce Customers",
            "description": "Retrieve all e-commerce customers",
            "group": "E-commerce",
            "tags": ["ecommerce", "customers", "list"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "List customers", "input": {"limit": 20}}]
        },
        "create_ecom_customer": {
            "method": "POST",
            "endpoint": "/ecomCustomers",
            "required_params": ["customer_data"],
            "optional_params": [],
            "body_parameters": ["customer_data"],
            "display_name": "Create E-commerce Customer",
            "description": "Create a new e-commerce customer",
            "group": "E-commerce",
            "tags": ["ecommerce", "customers", "create"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Create customer", "input": {"customer_data": {"connectionid": "1", "externalid": "CUST001", "email": "customer@example.com"}}}]
        },
        "update_ecom_customer": {
            "method": "PUT",
            "endpoint": "/ecomCustomers/{customer_id}",
            "required_params": ["customer_id", "customer_data"],
            "optional_params": [],
            "body_parameters": ["customer_data"],
            "display_name": "Update E-commerce Customer",
            "description": "Update an existing e-commerce customer",
            "group": "E-commerce",
            "tags": ["ecommerce", "customers", "update"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "auth": {"required_env_keys": ["ACTIVECAMPAIGN_API_KEY", "ACTIVECAMPAIGN_BASE_URL"], "optional_env_keys": []},
            "examples": [{"name": "Update customer", "input": {"customer_id": 123, "customer_data": {"acceptsMarketing": "1"}}}]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced ActiveCampaign node with embedded configuration."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Initialize the Enhanced UniversalRequestNode with embedded config
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.info("Enhanced ActiveCampaignNode initialized with 66+ operations and all 13 advanced features")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"ActiveCampaignNode executing operation: {node_data.get('params', {}).get('operation')}")
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
__all__ = ["ActiveCampaignNode"]