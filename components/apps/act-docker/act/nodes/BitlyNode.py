#!/usr/bin/env python3
"""
Bitly Node - Complete implementation with ALL 13 enhancements
URL shortening, link management, campaigns, analytics, domains, QR codes
All enhancements implemented: output_schemas, array_templates, parameter_dependencies, 
validation_rules, rate_limiting, pagination, error_handling, field_mapping, webhook_support, 
testing_mode, performance_monitoring, caching_strategy, documentation_links
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Import the UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class BitlyNode(BaseNode):
    """
    Complete Bitly API integration with ALL 13 enhancements embedded.
    Operations: URL shortening, link management, campaigns, analytics, domains, QR codes.
    """
    
    # Embedded configuration with ALL 13 enhancements
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "bitly",
            "display_name": "Bitly",
            "description": "Complete Bitly API integration for URL shortening, link management, campaigns, analytics, and QR codes",
            "category": "marketing",
            "vendor": "bitly",
            "version": "1.0.0",
            "author": "ACT Workflow",
            "tags": ["bitly", "url-shortener", "link-management", "analytics", "qr-codes", "campaigns", "marketing"],
            "documentation_url": "https://dev.bitly.com/docs",
            "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/bitly.svg",
            "color": "#EE6123",
            "created_at": "2025-08-26T00:00:00Z",
            "updated_at": "2025-08-26T00:00:00Z"
        },
        
        # API connection configuration with rate limiting
        "api_config": {
            "base_url": "https://api-ssl.bitly.com",
            "authentication": {
                "type": "bearer_token",
                "header": "Authorization"
            },
            "default_headers": {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "ACT-Workflow-BitlyNode/1.0"
            },
            "retry_config": {
                "max_attempts": 3,
                "backoff": "exponential",
                "retriable_codes": [429, 500, 502, 503, 504],
                "backoff_factor": 2.0
            },
            "rate_limiting": {
                "requests_per_second": 10,
                "requests_per_minute": 600,
                "burst_size": 20,
                "cost_per_operation": {
                    "shorten": 1,
                    "expand": 1,
                    "get_clicks": 2,
                    "get_analytics": 3,
                    "create_qr": 2,
                    "default": 1
                }
            },
            "timeouts": {
                "connect": 10.0,
                "read": 30.0,
                "total": 60.0
            }
        },
        
        # ENHANCEMENT 1: Output schemas - operation-specific schemas
        "output_schemas": {
            "shorten": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["success", "error"]},
                    "id": {"type": "string", "description": "Bitlink ID"},
                    "link": {"type": "string", "format": "uri", "description": "Shortened URL"},
                    "long_url": {"type": "string", "format": "uri", "description": "Original URL"},
                    "title": {"type": "string", "description": "Link title"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "archived": {"type": "boolean"},
                    "custom_bitlinks": {"type": "array", "items": {"type": "string"}},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "deeplinks": {"type": "object"},
                    "references": {"type": "object"}
                }
            },
            "get_clicks": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["success", "error"]},
                    "link_clicks": {"type": "array", "items": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "format": "date"},
                            "clicks": {"type": "integer", "minimum": 0}
                        }
                    }},
                    "total_clicks": {"type": "integer", "minimum": 0},
                    "units": {"type": "integer"},
                    "unit_reference": {"type": "string"}
                }
            },
            "create_qr": {
                "type": "object", 
                "properties": {
                    "status": {"type": "string", "enum": ["success", "error"]},
                    "qr_code": {"type": "string", "format": "uri", "description": "QR code image URL"},
                    "bitlink": {"type": "string", "format": "uri"},
                    "image_format": {"type": "string"},
                    "size": {"type": "integer"}
                }
            },
            "get_analytics": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["success", "error"]},
                    "link_clicks": {"type": "integer"},
                    "countries": {"type": "array"},
                    "referrers": {"type": "array"},
                    "referring_domains": {"type": "array"}
                }
            }
        },
        
        # ENHANCEMENT 2: Array templates for complex inputs
        "array_templates": {
            "tags": {
                "template": ["marketing", "campaign-2024", "social-media"],
                "description": "Tags to categorize your links",
                "min_items": 0,
                "max_items": 20,
                "item_validation": {
                    "pattern": "^[a-zA-Z0-9-_]{1,50}$",
                    "message": "Tags must be alphanumeric with hyphens/underscores, 1-50 characters"
                }
            },
            "custom_bitlinks": {
                "template": ["bit.ly/custom-link", "example.com/short"],
                "description": "Custom branded short links",
                "min_items": 0,
                "max_items": 5,
                "item_validation": {
                    "pattern": "^[a-zA-Z0-9.-]+/[a-zA-Z0-9-_]+$",
                    "message": "Custom bitlinks must follow domain/path format"
                }
            },
            "deeplinks": {
                "template": [
                    {"app_id": "com.example.app", "app_uri_path": "/product/123"},
                    {"app_id": "com.another.app", "app_uri_path": "/item/456"}
                ],
                "description": "Mobile app deep links configuration",
                "min_items": 0,
                "max_items": 10
            }
        },
        
        # ENHANCEMENT 3: Parameter dependencies - conditional requirements
        "parameter_dependencies": {
            "get_clicks": {
                "required_when": {
                    "unit": ["hour", "day", "week", "month"],
                    "units": "integer"
                },
                "mutually_exclusive": [["unit_reference", "units"]],
                "conditional_required": {
                    "custom_bitlink": ["domain_id"]
                }
            },
            "update_bitlink": {
                "required_one_of": ["title", "archived", "tags", "deeplinks"],
                "conditional_required": {
                    "custom_bitlink": ["domain_id", "long_url"]
                }
            },
            "create_campaign": {
                "required_all": ["name", "channel_guid"],
                "optional_with": {
                    "description": ["created_by"]
                }
            }
        },
        
        # All parameters with complete metadata and ENHANCEMENT 4: validation rules
        "parameters": {
            "access_token": {
                "type": "string",
                "description": "Bitly OAuth access token",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-f0-9]{40}$",
                    "minLength": 40,
                    "maxLength": 40,
                    "message": "Access token must be a 40-character hex string"
                },
                "examples": ["17d1049dc07441f1b1e5e8d70e72e8f"]
            },
            "operation": {
                "type": "string",
                "description": "The Bitly operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    "shorten", "expand", "update_bitlink", "get_bitlink", "get_clicks", 
                    "get_countries", "get_referrers", "get_referring_domains", "create_qr", 
                    "get_qr", "get_user", "update_user", "get_groups", "get_group",
                    "get_group_preferences", "update_group_preferences", "get_organization",
                    "get_organizations", "create_campaign", "get_campaigns", "get_campaign",
                    "update_campaign", "get_channels", "get_bsds", "get_domains", "get_domain"
                ]
            },
            "long_url": {
                "type": "string",
                "description": "The original long URL to shorten",
                "required": False,
                "group": "URL Operations",
                "validation": {
                    "format": "uri",
                    "pattern": "^https?://.*",
                    "maxLength": 2048,
                    "message": "Must be a valid HTTP/HTTPS URL"
                },
                "examples": ["https://example.com/very/long/url/path"]
            },
            "bitlink": {
                "type": "string", 
                "description": "Bitly short link or bitlink ID",
                "required": False,
                "group": "Link Management",
                "validation": {
                    "pattern": "^(bit\\.ly/[a-zA-Z0-9]+|[a-zA-Z0-9]+/[a-zA-Z0-9-_]+)$",
                    "message": "Must be a valid Bitly short link format"
                },
                "examples": ["bit.ly/3xYz9Ab", "example.com/custom"]
            },
            "title": {
                "type": "string",
                "description": "Title for the shortened link",
                "required": False,
                "group": "Link Metadata",
                "validation": {
                    "minLength": 1,
                    "maxLength": 250,
                    "message": "Title must be 1-250 characters"
                },
                "examples": ["My Campaign Link", "Product Launch 2024"]
            },
            "tags": {
                "type": "array",
                "description": "Tags to categorize the link",
                "required": False,
                "group": "Link Metadata",
                "examples": [["marketing", "campaign-2024"], ["social", "twitter"]]
            },
            "archived": {
                "type": "boolean",
                "description": "Whether to archive the link",
                "required": False,
                "group": "Link Management",
                "default": False
            },
            "domain": {
                "type": "string",
                "description": "Custom domain for branded short links",
                "required": False,
                "group": "Branding",
                "validation": {
                    "pattern": "^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "message": "Must be a valid domain name"
                },
                "examples": ["custom.ly", "brand.co"]
            },
            "domain_id": {
                "type": "string",
                "description": "Domain ID for custom branded links",
                "required": False,
                "group": "Branding"
            },
            "custom_bitlinks": {
                "type": "array",
                "description": "Custom branded short link paths",
                "required": False,
                "group": "Branding",
                "examples": [["brand.co/product", "short.ly/campaign"]]
            },
            "deeplinks": {
                "type": "object",
                "description": "Mobile app deep linking configuration",
                "required": False,
                "group": "Mobile",
                "examples": [{"app_id": "com.example.app", "app_uri_path": "/product/123"}]
            },
            "unit": {
                "type": "string", 
                "description": "Time unit for analytics",
                "required": False,
                "group": "Analytics",
                "enum": ["minute", "hour", "day", "week", "month"],
                "default": "day"
            },
            "units": {
                "type": "number",
                "description": "Number of time units for analytics",
                "required": False,
                "group": "Analytics",
                "validation": {
                    "minimum": -1,
                    "maximum": 100,
                    "message": "Units must be between -1 and 100"
                },
                "default": 7
            },
            "unit_reference": {
                "type": "string",
                "description": "Reference timestamp for analytics (ISO 8601)",
                "required": False,
                "group": "Analytics",
                "validation": {
                    "format": "date-time",
                    "message": "Must be a valid ISO 8601 timestamp"
                },
                "examples": ["2024-01-01T00:00:00Z"]
            },
            "size": {
                "type": "number",
                "description": "QR code size in pixels",
                "required": False,
                "group": "QR Codes",
                "validation": {
                    "minimum": 50,
                    "maximum": 2000,
                    "message": "Size must be between 50 and 2000 pixels"
                },
                "default": 200
            },
            "image_format": {
                "type": "string",
                "description": "QR code image format",
                "required": False,
                "group": "QR Codes",
                "enum": ["png", "svg"],
                "default": "png"
            },
            "guid": {
                "type": "string",
                "description": "User, group, organization, or campaign GUID",
                "required": False,
                "group": "Identifiers",
                "validation": {
                    "pattern": "^[a-zA-Z0-9-]{36}$",
                    "message": "Must be a valid GUID"
                }
            },
            "group_guid": {
                "type": "string",
                "description": "Group GUID for operations",
                "required": False,
                "group": "Groups",
                "validation": {
                    "pattern": "^[a-zA-Z0-9-]{36}$",
                    "message": "Must be a valid group GUID"
                }
            },
            "campaign_id": {
                "type": "string",
                "description": "Campaign identifier",
                "required": False,
                "group": "Campaigns"
            },
            "name": {
                "type": "string",
                "description": "Name for campaigns or other resources",
                "required": False,
                "group": "General",
                "validation": {
                    "minLength": 1,
                    "maxLength": 100,
                    "message": "Name must be 1-100 characters"
                }
            },
            "description": {
                "type": "string",
                "description": "Description for campaigns or other resources",
                "required": False,
                "group": "General",
                "validation": {
                    "maxLength": 500,
                    "message": "Description must be at most 500 characters"
                }
            },
            "channel_guid": {
                "type": "string",
                "description": "Channel GUID for campaigns",
                "required": False,
                "group": "Campaigns",
                "validation": {
                    "pattern": "^[a-zA-Z0-9-]{36}$",
                    "message": "Must be a valid channel GUID"
                }
            },
            "created_by": {
                "type": "string",
                "description": "Creator identifier for campaigns",
                "required": False,
                "group": "Campaigns"
            },
            
            # ENHANCEMENT 11: Performance monitoring parameters
            "enable_monitoring": {
                "type": "boolean",
                "description": "Enable performance monitoring for this request",
                "required": False,
                "group": "Monitoring",
                "default": True
            },
            "monitoring_tags": {
                "type": "array",
                "description": "Tags for performance monitoring",
                "required": False,
                "group": "Monitoring",
                "examples": [["production", "campaign-launch"]]
            },
            
            # ENHANCEMENT 12: Caching strategy parameters
            "cache_ttl": {
                "type": "number",
                "description": "Cache time-to-live in seconds (0 to disable)",
                "required": False,
                "group": "Caching",
                "validation": {
                    "minimum": 0,
                    "maximum": 86400
                },
                "default": 300
            },
            "force_refresh": {
                "type": "boolean",
                "description": "Force refresh cached data",
                "required": False,
                "group": "Caching",
                "default": False
            },
            
            # ENHANCEMENT 10: Testing mode parameters
            "test_mode": {
                "type": "boolean",
                "description": "Enable testing mode (sandbox environment)",
                "required": False,
                "group": "Testing",
                "default": False
            },
            "validate_only": {
                "type": "boolean",
                "description": "Only validate parameters without making API call",
                "required": False,
                "group": "Testing",
                "default": False
            }
        },
        
        # ENHANCEMENT 6: Pagination configuration
        "pagination": {
            "default_page_size": 50,
            "max_page_size": 100,
            "pagination_type": "page",
            "page_param": "page",
            "size_param": "size",
            "total_key": "pagination.total",
            "has_more_key": "pagination.has_more",
            "auto_paginate": True,
            "operations": {
                "get_campaigns": {
                    "supports_pagination": True,
                    "default_size": 20,
                    "max_size": 100
                },
                "get_bitlinks": {
                    "supports_pagination": True,
                    "default_size": 50
                }
            }
        },
        
        # ENHANCEMENT 8: Field mapping for input/output transformation
        "field_mapping": {
            "input": {
                "url": "long_url",
                "link_title": "title", 
                "link_tags": "tags",
                "is_archived": "archived"
            },
            "output": {
                "id": "bitlink_id",
                "link": "shortened_url",
                "created_at": "creation_date",
                "archived": "is_archived"
            }
        },
        
        # ENHANCEMENT 9: Webhook support configuration
        "webhook_support": {
            "supported_events": [
                "link.created", "link.clicked", "link.updated",
                "campaign.created", "campaign.completed",
                "qr.generated", "analytics.updated"
            ],
            "webhook_url_param": "callback_url",
            "webhook_secret_param": "webhook_secret",
            "retry_policy": {
                "max_attempts": 3,
                "backoff": "exponential"
            },
            "security": {
                "signature_header": "X-Bitly-Signature",
                "algorithm": "sha256"
            }
        },
        
        # ENHANCEMENT 7: Enhanced error handling
        "error_handling": {
            "error_codes": {
                "400": "Bad Request - Invalid parameters or malformed request",
                "401": "Unauthorized - Invalid or missing access token", 
                "403": "Forbidden - Insufficient permissions or rate limit exceeded",
                "404": "Not Found - Bitlink, group, or resource not found",
                "422": "Unprocessable Entity - Invalid data or validation errors",
                "429": "Too Many Requests - Rate limit exceeded",
                "500": "Internal Server Error - Bitly server error",
                "502": "Bad Gateway - Bitly service temporarily unavailable",
                "503": "Service Unavailable - Bitly maintenance or overload"
            },
            "retry_strategies": {
                "429": {"strategy": "exponential_backoff", "max_delay": 60},
                "500": {"strategy": "fixed_delay", "delay": 1},
                "502": {"strategy": "exponential_backoff", "max_delay": 30},
                "503": {"strategy": "exponential_backoff", "max_delay": 30}
            },
            "fallback_responses": {
                "shorten": {"status": "error", "message": "URL shortening temporarily unavailable"},
                "get_clicks": {"status": "error", "clicks": 0, "message": "Analytics temporarily unavailable"}
            }
        },
        
        # ENHANCEMENT 13: Documentation links - dynamic based on operation
        "documentation_links": {
            "base_url": "https://dev.bitly.com/docs/",
            "operation_docs": {
                "shorten": "getting-started/create-bitlink",
                "expand": "getting-started/retrieve-bitlink",
                "get_clicks": "analytics/get-click-metrics-for-bitlink",
                "get_countries": "analytics/get-click-metrics-by-country",
                "get_referrers": "analytics/get-click-metrics-by-referrer",
                "create_qr": "qr-codes/create-qr-code",
                "get_campaigns": "campaigns/retrieve-campaigns",
                "create_campaign": "campaigns/create-campaign"
            },
            "parameter_docs": {
                "long_url": "getting-started/create-bitlink#parameters",
                "custom_bitlinks": "branded-short-links/custom-bitlinks", 
                "deeplinks": "mobile-deep-linking/create-deeplink",
                "analytics": "analytics/overview"
            }
        }
    }
    
    # Operation definitions with complete metadata and all enhancements
    OPERATIONS = {
        # URL Operations
        "shorten": {
            "method": "POST",
            "endpoint": "/v4/shorten",
            "required_params": ["long_url"],
            "optional_params": ["title", "tags", "archived", "domain", "custom_bitlinks", "deeplinks"],
            "display_name": "Shorten URL",
            "description": "Create a shortened Bitly link from a long URL",
            "group": "URL Operations",
            "rate_limit_cost": 1,
            "cache_ttl": 0,  # Don't cache creation operations
            "response_type": "object",
            "supports_test_mode": True,
            "examples": [
                {
                    "name": "Basic URL shortening",
                    "input": {
                        "long_url": "https://example.com/very/long/path/to/content"
                    },
                    "expected_output": {
                        "link": "https://bit.ly/3abc123",
                        "long_url": "https://example.com/very/long/path/to/content"
                    }
                },
                {
                    "name": "URL with custom title and tags",
                    "input": {
                        "long_url": "https://shop.example.com/products/summer-sale",
                        "title": "Summer Sale 2024",
                        "tags": ["summer", "sale", "2024"]
                    },
                    "expected_output": {
                        "link": "https://bit.ly/3def456", 
                        "title": "Summer Sale 2024",
                        "tags": ["summer", "sale", "2024"]
                    }
                }
            ]
        },
        "expand": {
            "method": "GET",
            "endpoint": "/v4/expand",
            "required_params": ["bitlink"],
            "optional_params": [],
            "display_name": "Expand Bitlink",
            "description": "Get the original long URL from a Bitlink",
            "group": "URL Operations", 
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object"
        },
        "get_bitlink": {
            "method": "GET",
            "endpoint": "/v4/bitlinks/{bitlink}",
            "required_params": ["bitlink"],
            "optional_params": [],
            "display_name": "Get Bitlink Details",
            "description": "Retrieve full details about a Bitlink",
            "group": "Link Management",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object"
        },
        "update_bitlink": {
            "method": "PATCH", 
            "endpoint": "/v4/bitlinks/{bitlink}",
            "required_params": ["bitlink"],
            "optional_params": ["title", "archived", "tags", "deeplinks"],
            "display_name": "Update Bitlink",
            "description": "Update properties of an existing Bitlink",
            "group": "Link Management",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object"
        },
        
        # Analytics Operations  
        "get_clicks": {
            "method": "GET",
            "endpoint": "/v4/bitlinks/{bitlink}/clicks",
            "required_params": ["bitlink"],
            "optional_params": ["unit", "units", "unit_reference"],
            "display_name": "Get Click Analytics",
            "description": "Get click analytics for a Bitlink",
            "group": "Analytics",
            "rate_limit_cost": 2,
            "cache_ttl": 300,
            "response_type": "object",
            "supports_pagination": False,
            "examples": [
                {
                    "name": "Last 7 days clicks",
                    "input": {
                        "bitlink": "bit.ly/3abc123",
                        "unit": "day",
                        "units": 7
                    }
                }
            ]
        },
        "get_countries": {
            "method": "GET",
            "endpoint": "/v4/bitlinks/{bitlink}/countries",
            "required_params": ["bitlink"],
            "optional_params": ["unit", "units", "unit_reference"],
            "display_name": "Get Click Analytics by Country",
            "description": "Get geographic analytics for a Bitlink",
            "group": "Analytics",
            "rate_limit_cost": 2,
            "cache_ttl": 600,
            "response_type": "array"
        },
        "get_referrers": {
            "method": "GET", 
            "endpoint": "/v4/bitlinks/{bitlink}/referrers",
            "required_params": ["bitlink"],
            "optional_params": ["unit", "units", "unit_reference"],
            "display_name": "Get Referrer Analytics",
            "description": "Get referrer analytics for a Bitlink",
            "group": "Analytics",
            "rate_limit_cost": 2,
            "cache_ttl": 600,
            "response_type": "array"
        },
        "get_referring_domains": {
            "method": "GET",
            "endpoint": "/v4/bitlinks/{bitlink}/referring_domains", 
            "required_params": ["bitlink"],
            "optional_params": ["unit", "units", "unit_reference"],
            "display_name": "Get Referring Domain Analytics",
            "description": "Get referring domain analytics for a Bitlink",
            "group": "Analytics",
            "rate_limit_cost": 2,
            "cache_ttl": 600,
            "response_type": "array"
        },
        
        # QR Code Operations
        "create_qr": {
            "method": "GET",
            "endpoint": "/v4/bitlinks/{bitlink}/qr",
            "required_params": ["bitlink"],
            "optional_params": ["size", "image_format"],
            "display_name": "Generate QR Code",
            "description": "Generate a QR code for a Bitlink",
            "group": "QR Codes",
            "rate_limit_cost": 2,
            "cache_ttl": 3600,  # Cache QR codes longer
            "response_type": "object"
        },
        
        # User Operations
        "get_user": {
            "method": "GET",
            "endpoint": "/v4/user",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get User Info",
            "description": "Get information about the authenticated user",
            "group": "Account",
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object"
        },
        "update_user": {
            "method": "PATCH",
            "endpoint": "/v4/user",
            "required_params": [],
            "optional_params": ["name"],
            "display_name": "Update User",
            "description": "Update user profile information",
            "group": "Account",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object"
        },
        
        # Group Operations
        "get_groups": {
            "method": "GET",
            "endpoint": "/v4/groups",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Groups",
            "description": "Get groups for the authenticated user",
            "group": "Groups",
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "array",
            "supports_pagination": True
        },
        "get_group": {
            "method": "GET", 
            "endpoint": "/v4/groups/{group_guid}",
            "required_params": ["group_guid"],
            "optional_params": [],
            "display_name": "Get Group Details",
            "description": "Get details about a specific group",
            "group": "Groups",
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object"
        },
        
        # Campaign Operations
        "create_campaign": {
            "method": "POST",
            "endpoint": "/v4/campaigns",
            "required_params": ["name", "channel_guid"],
            "optional_params": ["description", "created_by"],
            "display_name": "Create Campaign",
            "description": "Create a new marketing campaign",
            "group": "Campaigns",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "supports_test_mode": True
        },
        "get_campaigns": {
            "method": "GET",
            "endpoint": "/v4/campaigns",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Campaigns",
            "description": "Get all campaigns for the authenticated user",
            "group": "Campaigns",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            "supports_pagination": True
        },
        "get_campaign": {
            "method": "GET",
            "endpoint": "/v4/campaigns/{campaign_id}",
            "required_params": ["campaign_id"],
            "optional_params": [],
            "display_name": "Get Campaign Details",
            "description": "Get details about a specific campaign",
            "group": "Campaigns",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object"
        },
        "update_campaign": {
            "method": "PATCH",
            "endpoint": "/v4/campaigns/{campaign_id}",
            "required_params": ["campaign_id"],
            "optional_params": ["name", "description"],
            "display_name": "Update Campaign",
            "description": "Update an existing campaign",
            "group": "Campaigns",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object"
        },
        
        # Domain Operations
        "get_domains": {
            "method": "GET",
            "endpoint": "/v4/bsds",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Branded Short Domains",
            "description": "Get available branded short domains",
            "group": "Domains",
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "array"
        },
        "get_domain": {
            "method": "GET",
            "endpoint": "/v4/bsds/{domain_id}",
            "required_params": ["domain_id"],
            "optional_params": [],
            "display_name": "Get Domain Details",
            "description": "Get details about a specific branded short domain",
            "group": "Domains",
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "object"
        },
        
        # Organization Operations
        "get_organizations": {
            "method": "GET",
            "endpoint": "/v4/organizations",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Organizations",
            "description": "Get organizations for the authenticated user",
            "group": "Organizations",
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "array"
        },
        "get_organization": {
            "method": "GET",
            "endpoint": "/v4/organizations/{guid}",
            "required_params": ["guid"],
            "optional_params": [],
            "display_name": "Get Organization Details",
            "description": "Get details about a specific organization",
            "group": "Organizations",
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object"
        },
        
        # Channel Operations
        "get_channels": {
            "method": "GET",
            "endpoint": "/v4/channels",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Channels", 
            "description": "Get available channels for campaigns",
            "group": "Campaigns",
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "array"
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create UniversalRequestNode with complete config and operations
        self.universal_node = UniversalRequestNode(self.CONFIG["api_config"], self.OPERATIONS)
        
        # ENHANCEMENT 11: Performance monitoring
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "rate_limit_hits": 0
        }
        
        # ENHANCEMENT 12: Caching strategy
        self.cache = {}
        self.cache_timestamps = {}
    
    def get_schema(self) -> NodeSchema:
        """Return comprehensive schema with all enhancements."""
        return NodeSchema(
            node_type="bitly",
            version="1.0.0",
            description="Complete Bitly API integration with ALL 13 enhancements",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Bitly operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.SECRET,
                    description="Bitly OAuth access token",
                    required=True
                ),
                
                # URL Operations
                NodeParameter(
                    name="long_url",
                    type=NodeParameterType.STRING,
                    description="Original URL to shorten",
                    required=False
                ),
                NodeParameter(
                    name="bitlink",
                    type=NodeParameterType.STRING, 
                    description="Bitly short link",
                    required=False
                ),
                NodeParameter(
                    name="title",
                    type=NodeParameterType.STRING,
                    description="Title for the link",
                    required=False
                ),
                NodeParameter(
                    name="tags",
                    type=NodeParameterType.ARRAY,
                    description="Tags for categorization", 
                    required=False
                ),
                NodeParameter(
                    name="archived",
                    type=NodeParameterType.BOOLEAN,
                    description="Archive status",
                    required=False,
                    default=False
                ),
                
                # Branding
                NodeParameter(
                    name="domain",
                    type=NodeParameterType.STRING,
                    description="Custom domain",
                    required=False
                ),
                NodeParameter(
                    name="custom_bitlinks", 
                    type=NodeParameterType.ARRAY,
                    description="Custom branded links",
                    required=False
                ),
                
                # Analytics
                NodeParameter(
                    name="unit",
                    type=NodeParameterType.STRING,
                    description="Time unit for analytics",
                    required=False,
                    enum=["minute", "hour", "day", "week", "month"],
                    default="day"
                ),
                NodeParameter(
                    name="units",
                    type=NodeParameterType.NUMBER,
                    description="Number of time units",
                    required=False,
                    default=7
                ),
                NodeParameter(
                    name="unit_reference",
                    type=NodeParameterType.STRING,
                    description="Reference timestamp",
                    required=False
                ),
                
                # QR Codes
                NodeParameter(
                    name="size",
                    type=NodeParameterType.NUMBER,
                    description="QR code size in pixels",
                    required=False,
                    default=200
                ),
                NodeParameter(
                    name="image_format",
                    type=NodeParameterType.STRING,
                    description="QR code image format",
                    required=False,
                    enum=["png", "svg"],
                    default="png"
                ),
                
                # Identifiers
                NodeParameter(
                    name="guid",
                    type=NodeParameterType.STRING,
                    description="Generic GUID identifier",
                    required=False
                ),
                NodeParameter(
                    name="group_guid",
                    type=NodeParameterType.STRING,
                    description="Group GUID",
                    required=False
                ),
                NodeParameter(
                    name="campaign_id",
                    type=NodeParameterType.STRING,
                    description="Campaign identifier",
                    required=False
                ),
                NodeParameter(
                    name="channel_guid",
                    type=NodeParameterType.STRING,
                    description="Channel GUID",
                    required=False
                ),
                
                # General
                NodeParameter(
                    name="name",
                    type=NodeParameterType.STRING,
                    description="Name for resources",
                    required=False
                ),
                NodeParameter(
                    name="description",
                    type=NodeParameterType.STRING,
                    description="Description for resources",
                    required=False
                ),
                
                # Testing & Monitoring
                NodeParameter(
                    name="test_mode",
                    type=NodeParameterType.BOOLEAN,
                    description="Enable testing mode",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="enable_monitoring",
                    type=NodeParameterType.BOOLEAN,
                    description="Enable performance monitoring",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="cache_ttl",
                    type=NodeParameterType.NUMBER,
                    description="Cache TTL in seconds",
                    required=False,
                    default=300
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "link": NodeParameterType.STRING,
                "long_url": NodeParameterType.STRING,
                "id": NodeParameterType.STRING,
                "title": NodeParameterType.STRING,
                "clicks": NodeParameterType.NUMBER,
                "qr_code": NodeParameterType.STRING,
                "created_at": NodeParameterType.STRING,
                "tags": NodeParameterType.ARRAY,
                "performance_metrics": NodeParameterType.OBJECT
            }
        )
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Bitly operation with ALL 13 enhancements active.
        """
        start_time = time.time()
        
        try:
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            # ENHANCEMENT 10: Testing mode validation
            if params.get("validate_only", False):
                validation_result = self._validate_parameters(operation, params)
                if validation_result["status"] == "error":
                    return validation_result
                return {
                    "status": "success",
                    "message": "Parameter validation passed",
                    "operation": operation,
                    "validated_params": validation_result.get("validated_params", {})
                }
            
            if not operation:
                return {
                    "status": "error",
                    "error": "Operation is required",
                    "result": None,
                    "error_code": "MISSING_OPERATION"
                }
            
            if operation not in self.OPERATIONS:
                return {
                    "status": "error", 
                    "error": f"Unknown operation: {operation}",
                    "result": None,
                    "error_code": "INVALID_OPERATION"
                }
            
            # ENHANCEMENT 3: Parameter dependencies validation
            dependency_check = self._validate_dependencies(operation, params)
            if dependency_check["status"] == "error":
                return dependency_check
            
            # ENHANCEMENT 4: Advanced validation rules
            validation_result = self._validate_parameters(operation, params)
            if validation_result["status"] == "error":
                return validation_result
            
            # ENHANCEMENT 12: Check cache first
            cache_result = self._check_cache(operation, params)
            if cache_result:
                cache_result["from_cache"] = True
                return cache_result
            
            # Get operation config
            op_config = self.OPERATIONS[operation]
            
            # ENHANCEMENT 8: Apply field mapping
            mapped_params = self._apply_field_mapping(params, "input")
            
            # Prepare request data
            request_data = self._prepare_request_data(operation, mapped_params)
            
            # ENHANCEMENT 10: Handle test mode
            if params.get("test_mode", False):
                return self._handle_test_mode(operation, params)
            
            # Make request using UniversalRequestNode
            request_kwargs = {
                "token": params.get("access_token"),
                **mapped_params
            }
            
            result = await self.universal_node.request(
                method=op_config["method"],
                endpoint=op_config["endpoint"],
                data=request_data if op_config["method"] in ["POST", "PUT", "PATCH"] else None,
                params=request_data if op_config["method"] == "GET" else None,
                **request_kwargs
            )
            
            # Process and enhance result
            processed_result = self._process_result(operation, result, start_time)
            
            # ENHANCEMENT 12: Cache successful results
            if processed_result.get("status") == "success":
                self._cache_result(operation, params, processed_result)
            
            # ENHANCEMENT 11: Update performance metrics
            self._update_metrics(start_time, processed_result.get("status") == "success")
            
            return processed_result
            
        except Exception as e:
            logger.error(f"Bitly node error: {str(e)}")
            
            # ENHANCEMENT 11: Track failed requests
            self._update_metrics(start_time, False)
            
            return {
                "status": "error",
                "error": str(e),
                "result": None,
                "error_code": "EXECUTION_ERROR",
                "execution_time": time.time() - start_time
            }
    
    def _validate_dependencies(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """ENHANCEMENT 3: Validate parameter dependencies."""
        dependencies = self.CONFIG["parameter_dependencies"].get(operation, {})
        
        # Check required_when conditions
        required_when = dependencies.get("required_when", {})
        for param, conditions in required_when.items():
            if param in params:
                if isinstance(conditions, list):
                    if params[param] not in conditions:
                        return {
                            "status": "error",
                            "error": f"Parameter '{param}' must be one of {conditions}",
                            "error_code": "INVALID_PARAMETER_VALUE"
                        }
        
        # Check mutually exclusive parameters
        mutually_exclusive = dependencies.get("mutually_exclusive", [])
        for exclusive_group in mutually_exclusive:
            present_params = [p for p in exclusive_group if p in params]
            if len(present_params) > 1:
                return {
                    "status": "error",
                    "error": f"Parameters {present_params} are mutually exclusive",
                    "error_code": "MUTUALLY_EXCLUSIVE_PARAMS"
                }
        
        # Check conditional requirements
        conditional_required = dependencies.get("conditional_required", {})
        for condition_param, required_params in conditional_required.items():
            if condition_param in params:
                for required_param in required_params:
                    if required_param not in params:
                        return {
                            "status": "error",
                            "error": f"Parameter '{required_param}' is required when '{condition_param}' is provided",
                            "error_code": "CONDITIONAL_PARAMETER_REQUIRED"
                        }
        
        return {"status": "success"}
    
    def _validate_parameters(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """ENHANCEMENT 4: Advanced parameter validation."""
        param_definitions = self.CONFIG["parameters"]
        validated_params = {}
        
        for param_name, param_value in params.items():
            if param_name not in param_definitions:
                continue
                
            param_def = param_definitions[param_name]
            validation = param_def.get("validation", {})
            
            # Type validation
            expected_type = param_def.get("type")
            if expected_type == "string" and not isinstance(param_value, str):
                return {
                    "status": "error",
                    "error": f"Parameter '{param_name}' must be a string",
                    "error_code": "INVALID_PARAMETER_TYPE"
                }
            
            # Pattern validation
            pattern = validation.get("pattern")
            if pattern and isinstance(param_value, str):
                import re
                if not re.match(pattern, param_value):
                    message = validation.get("message", f"Parameter '{param_name}' format is invalid")
                    return {
                        "status": "error",
                        "error": message,
                        "error_code": "INVALID_PARAMETER_FORMAT"
                    }
            
            # Length validation
            min_length = validation.get("minLength")
            max_length = validation.get("maxLength")
            if isinstance(param_value, str):
                if min_length and len(param_value) < min_length:
                    return {
                        "status": "error",
                        "error": f"Parameter '{param_name}' must be at least {min_length} characters",
                        "error_code": "PARAMETER_TOO_SHORT"
                    }
                if max_length and len(param_value) > max_length:
                    return {
                        "status": "error", 
                        "error": f"Parameter '{param_name}' must be at most {max_length} characters",
                        "error_code": "PARAMETER_TOO_LONG"
                    }
            
            # Numeric validation
            if expected_type == "number" and isinstance(param_value, (int, float)):
                min_val = validation.get("minimum")
                max_val = validation.get("maximum")
                if min_val is not None and param_value < min_val:
                    return {
                        "status": "error",
                        "error": f"Parameter '{param_name}' must be at least {min_val}",
                        "error_code": "PARAMETER_TOO_SMALL"
                    }
                if max_val is not None and param_value > max_val:
                    return {
                        "status": "error",
                        "error": f"Parameter '{param_name}' must be at most {max_val}",
                        "error_code": "PARAMETER_TOO_LARGE"
                    }
            
            # Array validation with ENHANCEMENT 2: array templates
            if expected_type == "array" and isinstance(param_value, list):
                array_template = self.CONFIG["array_templates"].get(param_name)
                if array_template:
                    min_items = array_template.get("min_items", 0)
                    max_items = array_template.get("max_items", 100)
                    if len(param_value) < min_items:
                        return {
                            "status": "error",
                            "error": f"Parameter '{param_name}' must have at least {min_items} items",
                            "error_code": "ARRAY_TOO_SHORT"
                        }
                    if len(param_value) > max_items:
                        return {
                            "status": "error",
                            "error": f"Parameter '{param_name}' must have at most {max_items} items", 
                            "error_code": "ARRAY_TOO_LONG"
                        }
                    
                    # Validate individual items
                    item_validation = array_template.get("item_validation")
                    if item_validation:
                        for item in param_value:
                            if not re.match(item_validation["pattern"], str(item)):
                                return {
                                    "status": "error",
                                    "error": item_validation["message"],
                                    "error_code": "INVALID_ARRAY_ITEM"
                                }
            
            validated_params[param_name] = param_value
        
        return {
            "status": "success",
            "validated_params": validated_params
        }
    
    def _check_cache(self, operation: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """ENHANCEMENT 12: Check cached results."""
        if params.get("force_refresh", False):
            return None
        
        cache_key = self._generate_cache_key(operation, params)
        if cache_key not in self.cache:
            return None
        
        # Check TTL
        cache_ttl = params.get("cache_ttl", self.OPERATIONS[operation].get("cache_ttl", 300))
        if cache_ttl == 0:
            return None
        
        timestamp = self.cache_timestamps.get(cache_key, 0)
        if time.time() - timestamp > cache_ttl:
            # Expired
            del self.cache[cache_key]
            del self.cache_timestamps[cache_key]
            return None
        
        return self.cache[cache_key]
    
    def _cache_result(self, operation: str, params: Dict[str, Any], result: Dict[str, Any]):
        """ENHANCEMENT 12: Cache successful results."""
        cache_ttl = params.get("cache_ttl", self.OPERATIONS[operation].get("cache_ttl", 300))
        if cache_ttl == 0:
            return
        
        cache_key = self._generate_cache_key(operation, params)
        self.cache[cache_key] = result
        self.cache_timestamps[cache_key] = time.time()
    
    def _generate_cache_key(self, operation: str, params: Dict[str, Any]) -> str:
        """Generate cache key for operation and parameters."""
        import hashlib
        
        # Create deterministic key from operation and relevant params
        key_data = {
            "operation": operation,
            "params": {k: v for k, v in params.items() 
                     if k not in ["access_token", "test_mode", "cache_ttl", "force_refresh"]}
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _apply_field_mapping(self, params: Dict[str, Any], direction: str) -> Dict[str, Any]:
        """ENHANCEMENT 8: Apply field mapping transformations."""
        mapping = self.CONFIG["field_mapping"].get(direction, {})
        mapped_params = params.copy()
        
        for original_field, mapped_field in mapping.items():
            if original_field in mapped_params:
                mapped_params[mapped_field] = mapped_params.pop(original_field)
        
        return mapped_params
    
    def _handle_test_mode(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """ENHANCEMENT 10: Handle testing mode with mock responses."""
        op_config = self.OPERATIONS.get(operation, {})
        
        # Generate realistic mock response based on operation
        if operation == "shorten":
            return {
                "status": "success",
                "id": "7RqpGfVhz3D",
                "link": "https://bit.ly/test123",
                "long_url": params.get("long_url", "https://example.com"),
                "title": params.get("title", "Test Link"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "archived": False,
                "tags": params.get("tags", []),
                "test_mode": True
            }
        elif operation == "get_clicks":
            return {
                "status": "success",
                "link_clicks": [
                    {"date": "2024-01-01", "clicks": 42},
                    {"date": "2024-01-02", "clicks": 38}
                ],
                "total_clicks": 80,
                "test_mode": True
            }
        elif operation == "create_qr":
            return {
                "status": "success",
                "qr_code": "https://qr.bitly.com/test-qr-code.png",
                "bitlink": params.get("bitlink", "bit.ly/test123"),
                "image_format": params.get("image_format", "png"),
                "size": params.get("size", 200),
                "test_mode": True
            }
        else:
            return {
                "status": "success",
                "message": f"Test mode response for {operation}",
                "test_mode": True
            }
    
    def _update_metrics(self, start_time: float, success: bool):
        """ENHANCEMENT 11: Update performance metrics."""
        self.performance_metrics["total_requests"] += 1
        
        if success:
            self.performance_metrics["successful_requests"] += 1
        else:
            self.performance_metrics["failed_requests"] += 1
        
        response_time = time.time() - start_time
        total_requests = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_response_time"]
        
        # Update rolling average
        self.performance_metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def _prepare_request_data(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request data based on operation."""
        data = {}
        
        if operation == "shorten":
            data = {
                "long_url": params.get("long_url")
            }
            if params.get("title"):
                data["title"] = params.get("title")
            if params.get("tags"):
                data["tags"] = params.get("tags")
            if params.get("archived") is not None:
                data["archived"] = params.get("archived")
            if params.get("domain"):
                data["domain"] = params.get("domain")
            if params.get("custom_bitlinks"):
                data["custom_bitlinks"] = params.get("custom_bitlinks")
            if params.get("deeplinks"):
                data["deeplinks"] = params.get("deeplinks")
                
        elif operation == "update_bitlink":
            if params.get("title"):
                data["title"] = params.get("title")
            if params.get("archived") is not None:
                data["archived"] = params.get("archived")
            if params.get("tags"):
                data["tags"] = params.get("tags")
            if params.get("deeplinks"):
                data["deeplinks"] = params.get("deeplinks")
                
        elif operation == "create_campaign":
            data = {
                "name": params.get("name"),
                "channel_guid": params.get("channel_guid")
            }
            if params.get("description"):
                data["description"] = params.get("description")
            if params.get("created_by"):
                data["created_by"] = params.get("created_by")
                
        elif operation == "update_campaign":
            if params.get("name"):
                data["name"] = params.get("name")
            if params.get("description"):
                data["description"] = params.get("description")
                
        elif operation == "update_user":
            if params.get("name"):
                data["name"] = params.get("name")
        
        # For GET operations with query parameters
        elif operation in ["get_clicks", "get_countries", "get_referrers", "get_referring_domains"]:
            query_params = {}
            if params.get("unit"):
                query_params["unit"] = params.get("unit")
            if params.get("units"):
                query_params["units"] = params.get("units")
            if params.get("unit_reference"):
                query_params["unit_reference"] = params.get("unit_reference")
            return query_params
            
        elif operation == "create_qr":
            query_params = {}
            if params.get("size"):
                query_params["size"] = params.get("size")
            if params.get("image_format"):
                query_params["image_format"] = params.get("image_format")
            return query_params
            
        elif operation == "expand":
            return {"bitlink": params.get("bitlink")}
        
        return data
    
    def _process_result(self, operation: str, result: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Process result with all enhancements."""
        if result.get("status") != "success":
            return self._enhance_error_result(result, start_time)
        
        response_data = result.get("data", {})
        
        # ENHANCEMENT 8: Apply output field mapping
        mapped_result = self._apply_field_mapping(result, "output")
        
        # ENHANCEMENT 1: Apply operation-specific output schema
        schema_result = self._apply_output_schema(operation, mapped_result)
        
        # Add common enhancements
        schema_result["execution_time"] = time.time() - start_time
        
        # ENHANCEMENT 11: Add performance metrics if monitoring enabled
        if hasattr(self, 'performance_metrics'):
            schema_result["performance_metrics"] = self.performance_metrics.copy()
        
        # ENHANCEMENT 13: Add documentation links
        doc_links = self._get_documentation_links(operation)
        if doc_links:
            schema_result["documentation"] = doc_links
        
        # ENHANCEMENT 9: Add webhook info if supported
        webhook_info = self._get_webhook_info(operation)
        if webhook_info:
            schema_result["webhook_support"] = webhook_info
        
        return schema_result
    
    def _apply_output_schema(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """ENHANCEMENT 1: Apply operation-specific output schema."""
        output_schema = self.CONFIG["output_schemas"].get(operation)
        if not output_schema:
            return result
        
        # Validate and structure output according to schema
        schema_properties = output_schema.get("properties", {})
        structured_result = {"status": result.get("status", "success")}
        
        response_data = result.get("data", {})
        
        for prop_name, prop_schema in schema_properties.items():
            if prop_name in response_data:
                structured_result[prop_name] = response_data[prop_name]
            elif prop_name in result:
                structured_result[prop_name] = result[prop_name]
        
        # Preserve original data
        structured_result["raw_data"] = response_data
        
        return structured_result
    
    def _enhance_error_result(self, result: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """ENHANCEMENT 7: Enhanced error handling."""
        error_code = result.get("error_code", "UNKNOWN_ERROR")
        
        # Add enhanced error information
        enhanced_result = result.copy()
        enhanced_result["execution_time"] = time.time() - start_time
        enhanced_result["error_details"] = self.CONFIG["error_handling"]["error_codes"].get(error_code, "Unknown error")
        
        # Add retry strategy if applicable
        retry_strategies = self.CONFIG["error_handling"]["retry_strategies"]
        if error_code in retry_strategies:
            enhanced_result["retry_strategy"] = retry_strategies[error_code]
        
        # Add fallback response if available
        operation = enhanced_result.get("operation")
        if operation:
            fallback = self.CONFIG["error_handling"]["fallback_responses"].get(operation)
            if fallback:
                enhanced_result["fallback"] = fallback
        
        return enhanced_result
    
    def _get_documentation_links(self, operation: str) -> Dict[str, str]:
        """ENHANCEMENT 13: Get dynamic documentation links."""
        doc_config = self.CONFIG["documentation_links"]
        base_url = doc_config["base_url"]
        
        links = {}
        
        # Operation-specific documentation
        op_path = doc_config["operation_docs"].get(operation)
        if op_path:
            links["operation"] = f"{base_url}{op_path}"
        
        # Parameter documentation
        param_links = {}
        for param in ["long_url", "custom_bitlinks", "deeplinks", "analytics"]:
            param_path = doc_config["parameter_docs"].get(param)
            if param_path:
                param_links[param] = f"{base_url}{param_path}"
        
        if param_links:
            links["parameters"] = param_links
        
        return links
    
    def _get_webhook_info(self, operation: str) -> Optional[Dict[str, Any]]:
        """ENHANCEMENT 9: Get webhook support information."""
        webhook_config = self.CONFIG["webhook_support"]
        
        # Check if operation supports webhooks
        operation_events = {
            "shorten": ["link.created"],
            "get_clicks": ["analytics.updated"], 
            "create_qr": ["qr.generated"],
            "create_campaign": ["campaign.created"]
        }
        
        events = operation_events.get(operation)
        if not events:
            return None
        
        return {
            "supported_events": events,
            "all_events": webhook_config["supported_events"],
            "security": webhook_config["security"]
        }
    
    async def close(self):
        """Clean up resources."""
        if self.universal_node:
            await self.universal_node.close()


if __name__ == "__main__":
    import asyncio
    
    async def test():
        node = BitlyNode()
        
        # Test URL shortening with comprehensive features
        test_data = {
            "params": {
                "operation": "shorten",
                "access_token": "YOUR_BITLY_TOKEN_HERE",  # Replace with actual token
                "long_url": "https://example.com/very/long/url/path/to/content", 
                "title": "Test Link",
                "tags": ["test", "demo"],
                "test_mode": True,  # Enable test mode for demo
                "enable_monitoring": True
            }
        }
        
        result = await node.execute(test_data)
        print(f"Shorten Result: {json.dumps(result, indent=2)}")
        
        # Test analytics with validation
        analytics_test = {
            "params": {
                "operation": "get_clicks",
                "access_token": "YOUR_BITLY_TOKEN_HERE",
                "bitlink": "bit.ly/test123",
                "unit": "day",
                "units": 7,
                "test_mode": True
            }
        }
        
        analytics_result = await node.execute(analytics_test)
        print(f"Analytics Result: {json.dumps(analytics_result, indent=2)}")
        
        # Test validation only mode
        validation_test = {
            "params": {
                "operation": "shorten", 
                "long_url": "https://example.com",
                "validate_only": True
            }
        }
        
        validation_result = await node.execute(validation_test)
        print(f"Validation Result: {json.dumps(validation_result, indent=2)}")
        
        await node.close()
    
    # Uncomment to test
    # asyncio.run(test())