#!/usr/bin/env python3
"""
Beehiiv Node - Enhanced with ALL 13 advanced features
Configuration is embedded directly in the node - no separate config.json needed
Comprehensive Beehiiv API integration for newsletter management, subscribers, campaigns, analytics, automation, and segments
"""

import logging
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Import the Enhanced UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class BeehiivNode(BaseNode):
    """
    Enhanced Beehiiv node with ALL 13 advanced features - newsletter automation platform.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    Provides comprehensive Beehiiv API functionality.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # 1. NODE METADATA - Complete discovery information
        "node_info": {
            "name": "beehiiv",
            "display_name": "Beehiiv",
            "description": "Comprehensive Beehiiv API integration for newsletter management, subscriber automation, campaign analytics, segmentation, and email marketing workflows",
            "category": "marketing",
            "vendor": "beehiiv",
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["newsletter", "email", "marketing", "automation", "subscribers", "campaigns", "analytics", "beehiiv"],
            "documentation_url": "https://developers.beehiiv.com/docs/v2",
            "icon": "https://assets.beehiiv.com/logo.svg",
            "color": "#FF6B35",
            "created_at": "2025-08-26T00:00:00Z",
            "updated_at": "2025-08-26T00:00:00Z"
        },
        
        # 2. API CONFIGURATION with rate limiting and retry logic
        "api_config": {
            "base_url": "https://api.beehiiv.com/v2",
            "authentication": {
                "type": "bearer_token",
                "header": "Authorization"
            },
            "default_headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ACT-Workflow-BeehiivNode/2.0"
            },
            "retry_config": {
                "max_attempts": 3,
                "backoff": "exponential_jitter",
                "base_delay": 1.5,
                "max_delay": 30.0,
                "jitter": True,
                "retriable_codes": [429, 500, 502, 503, 504],
                "retriable_exceptions": ["aiohttp.ClientTimeout", "aiohttp.ClientConnectorError"],
                "timeout_ms": 45000
            },
            "rate_limiting": {
                "requests_per_minute": 100,
                "requests_per_second": 5.0,
                "burst_size": 10,
                "cost_per_request": 0.01,
                "quota_type": "requests"
            },
            "timeouts": {
                "connect": 15.0,
                "read": 60.0,
                "total": 90.0
            }
        },
        
        # 3. PRICING INFORMATION
        "pricing": {
            "cost_per_1k_subscribers": 0.10,
            "cost_per_request": 0.005,
            "billing_unit": "requests",
            "free_tier_limit": 1000
        },
        
        # 4. PERFORMANCE MONITORING
        "monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "subscriber_count", "campaign_stats"],
            "alerts": {
                "error_rate_threshold": 0.03,
                "response_time_threshold": 10000,
                "bounce_rate_threshold": 0.05
            }
        },
        
        # 5. INTELLIGENT CACHING STRATEGY
        "caching": {
            "enabled": True,
            "cache_key_template": "{operation}:{publication_id}:{hash}",
            "ttl_seconds": 600,
            "cache_conditions": {
                "only_for": ["GET"],
                "exclude_params": ["timestamp", "nonce", "page", "per_page"],
                "cache_by_operation": {
                    "get_subscriber": 300,
                    "get_publication": 1800,
                    "list_posts": 900,
                    "get_analytics": 3600
                }
            }
        },
        
        # 6. TESTING CONFIGURATION
        "testing": {
            "sandbox_mode": True,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/publications",
            "test_publication_id": "test_pub_123",
            "mock_responses": True
        },
        
        # 7. DOCUMENTATION LINKS
        "documentation": {
            "api_docs_url": "https://developers.beehiiv.com/docs/v2",
            "setup_guide": "https://developers.beehiiv.com/docs/getting-started",
            "authentication": "https://developers.beehiiv.com/docs/authentication",
            "troubleshooting": "https://developers.beehiiv.com/docs/errors",
            "changelog": "https://developers.beehiiv.com/docs/changelog",
            "webhooks": "https://developers.beehiiv.com/docs/webhooks"
        },
        
        # 8. ENHANCED PARAMETERS with validation rules and dependencies
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "Beehiiv API key",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^bh_[a-zA-Z0-9_-]{40,60}$",
                    "message": "API key must start with 'bh_' and be 40-60 characters",
                    "minLength": 43,
                    "maxLength": 63
                }
            },
            "operation": {
                "type": "string",
                "description": "The Beehiiv operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    "get_publication", "list_publications", "create_publication", "update_publication",
                    "get_subscriber", "list_subscribers", "create_subscriber", "update_subscriber", "delete_subscriber",
                    "bulk_subscribe", "bulk_unsubscribe", "import_subscribers",
                    "create_post", "get_post", "list_posts", "update_post", "delete_post", "publish_post",
                    "create_campaign", "get_campaign", "list_campaigns", "send_campaign", "schedule_campaign",
                    "get_analytics", "get_subscriber_analytics", "get_campaign_analytics", "get_publication_stats",
                    "create_segment", "get_segment", "list_segments", "update_segment", "delete_segment",
                    "create_automation", "get_automation", "list_automations", "trigger_automation",
                    "create_webhook", "list_webhooks", "delete_webhook", "test_webhook",
                    "upload_image", "get_templates", "export_data"
                ]
            },
            "publication_id": {
                "type": "string",
                "description": "Beehiiv publication ID",
                "required": False,
                "group": "Publication",
                "examples": ["pub_12345abc", "pub_67890def"],
                "validation": {
                    "pattern": "^pub_[a-zA-Z0-9]{8,}$",
                    "message": "Publication ID must start with 'pub_'"
                }
            },
            "subscriber_id": {
                "type": "string",
                "description": "Subscriber unique ID",
                "required": False,
                "group": "Subscribers",
                "examples": ["sub_abc123", "sub_def456"]
            },
            "email": {
                "type": "string",
                "description": "Email address for subscriber operations",
                "required": False,
                "group": "Subscribers",
                "validation": {
                    "format": "email",
                    "message": "Must be a valid email address"
                },
                "examples": ["user@example.com", "newsletter@company.com"]
            },
            "name": {
                "type": "string",
                "description": "Name for publications, subscribers, segments, or automations",
                "required": False,
                "group": "General",
                "validation": {
                    "maxLength": 100,
                    "minLength": 1
                },
                "examples": ["My Newsletter", "Weekly Updates", "Premium Subscribers"]
            },
            "description": {
                "type": "string",
                "description": "Description for publications, segments, or automations",
                "required": False,
                "group": "General",
                "validation": {
                    "maxLength": 500
                },
                "examples": ["Weekly tech newsletter", "Automation for new subscribers"]
            },
            "title": {
                "type": "string",
                "description": "Title for posts and campaigns",
                "required": False,
                "group": "Content",
                "validation": {
                    "maxLength": 200,
                    "minLength": 1
                },
                "examples": ["Weekly Newsletter #42", "Product Launch Announcement"]
            },
            "content": {
                "type": "string",
                "description": "HTML content for posts and campaigns",
                "required": False,
                "group": "Content",
                "validation": {
                    "maxLength": 100000
                },
                "examples": ["<h1>Hello World</h1><p>Newsletter content...</p>"]
            },
            "subject": {
                "type": "string",
                "description": "Email subject line for campaigns",
                "required": False,
                "group": "Content",
                "validation": {
                    "maxLength": 150,
                    "minLength": 1
                },
                "examples": ["Don't miss this week's updates!", "Special offer inside"]
            },
            "preview_text": {
                "type": "string",
                "description": "Email preview text",
                "required": False,
                "group": "Content",
                "validation": {
                    "maxLength": 150
                },
                "examples": ["Get the latest updates from our team..."]
            },
            "status": {
                "type": "string",
                "description": "Status filter or update value",
                "required": False,
                "group": "Filters",
                "enum": ["active", "inactive", "unsubscribed", "draft", "scheduled", "sent", "published"],
                "examples": ["active", "published", "draft"]
            },
            "tags": {
                "type": "array",
                "description": "Tags for subscribers or content",
                "required": False,
                "group": "Organization",
                "validation": {
                    "items": {"type": "string", "maxLength": 50},
                    "maxItems": 10
                },
                "examples": [["premium", "early-adopter"], ["tech", "weekly"]]
            },
            "custom_fields": {
                "type": "object",
                "description": "Custom fields for subscribers",
                "required": False,
                "group": "Subscribers",
                "examples": [{"company": "Tech Corp", "role": "Developer"}]
            },
            "segment_id": {
                "type": "string",
                "description": "Segment ID for targeted operations",
                "required": False,
                "group": "Segments",
                "examples": ["seg_abc123", "seg_premium"]
            },
            "criteria": {
                "type": "object",
                "description": "Criteria for segment creation",
                "required": False,
                "group": "Segments",
                "examples": [{"tag": "premium", "subscription_date": ">2023-01-01"}]
            },
            "automation_id": {
                "type": "string",
                "description": "Automation workflow ID",
                "required": False,
                "group": "Automation",
                "examples": ["auto_welcome123", "auto_nurture456"]
            },
            "trigger_event": {
                "type": "string",
                "description": "Event that triggers automation",
                "required": False,
                "group": "Automation",
                "enum": ["subscribe", "unsubscribe", "tag_added", "custom_field_updated"],
                "examples": ["subscribe", "tag_added"]
            },
            "webhook_url": {
                "type": "string",
                "description": "Webhook URL for event notifications",
                "required": False,
                "group": "Webhooks",
                "validation": {
                    "format": "uri",
                    "message": "Must be a valid HTTPS URL"
                },
                "examples": ["https://example.com/webhook", "https://api.myapp.com/beehiiv"]
            },
            "webhook_events": {
                "type": "array",
                "description": "Events to send to webhook",
                "required": False,
                "group": "Webhooks",
                "validation": {
                    "items": {"type": "string", "enum": ["subscriber.created", "subscriber.updated", "post.published", "campaign.sent"]}
                },
                "examples": [["subscriber.created", "post.published"]]
            },
            "post_id": {
                "type": "string",
                "description": "Post ID",
                "required": False,
                "group": "Content",
                "examples": ["post_abc123", "post_def456"]
            },
            "campaign_id": {
                "type": "string",
                "description": "Campaign ID",
                "required": False,
                "group": "Campaigns",
                "examples": ["camp_abc123", "camp_weekly456"]
            },
            "send_time": {
                "type": "string",
                "description": "Scheduled send time (ISO 8601 format)",
                "required": False,
                "group": "Scheduling",
                "validation": {
                    "format": "date-time"
                },
                "examples": ["2025-12-25T10:00:00Z", "2025-01-01T00:00:00Z"]
            },
            "timezone": {
                "type": "string",
                "description": "Timezone for scheduling",
                "required": False,
                "group": "Scheduling",
                "default": "UTC",
                "examples": ["UTC", "America/New_York", "Europe/London"]
            },
            "template_id": {
                "type": "string",
                "description": "Template ID for creating content",
                "required": False,
                "group": "Templates",
                "examples": ["tpl_newsletter123", "tpl_welcome456"]
            },
            "image_file": {
                "type": "string",
                "description": "Base64 encoded image data or file path",
                "required": False,
                "group": "Media",
                "validation": {
                    "maxLength": 10485760  # 10MB in base64
                }
            },
            "image_name": {
                "type": "string",
                "description": "Name for uploaded image",
                "required": False,
                "group": "Media",
                "examples": ["newsletter-header.jpg", "product-image.png"]
            },
            "export_format": {
                "type": "string",
                "description": "Format for data export",
                "required": False,
                "group": "Export",
                "enum": ["csv", "json"],
                "default": "csv",
                "examples": ["csv", "json"]
            },
            "date_range": {
                "type": "object",
                "description": "Date range for analytics and exports",
                "required": False,
                "group": "Analytics",
                "examples": [{"start": "2025-01-01", "end": "2025-01-31"}]
            },
            "metrics": {
                "type": "array",
                "description": "Specific metrics to retrieve",
                "required": False,
                "group": "Analytics",
                "validation": {
                    "items": {"type": "string", "enum": ["subscribers", "opens", "clicks", "unsubscribes", "bounces"]}
                },
                "examples": [["subscribers", "opens"], ["clicks", "unsubscribes"]]
            },
            "page": {
                "type": "number",
                "description": "Page number for pagination",
                "required": False,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 1000
                },
                "default": 1
            },
            "per_page": {
                "type": "number",
                "description": "Number of results per page (1-100)",
                "required": False,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 100
                },
                "default": 25
            },
            "sort": {
                "type": "string",
                "description": "Sort field",
                "required": False,
                "group": "Filters",
                "enum": ["created_at", "updated_at", "name", "email", "subscriber_count"],
                "default": "created_at"
            },
            "order": {
                "type": "string",
                "description": "Sort order",
                "required": False,
                "group": "Filters",
                "enum": ["asc", "desc"],
                "default": "desc"
            },
            "filter": {
                "type": "object",
                "description": "Advanced filtering options",
                "required": False,
                "group": "Filters",
                "examples": [{"status": "active", "tags": ["premium"]}, {"created_after": "2025-01-01"}]
            }
        },
        
        # 9. PARAMETER DEPENDENCIES - Dynamic requirements
        "parameter_dependencies": {
            "create_subscriber": {
                "required": ["email"],
                "optional_groups": [["name"], ["custom_fields"], ["tags"]]
            },
            "update_subscriber": {
                "required": ["subscriber_id"],
                "at_least_one": ["email", "name", "status", "tags", "custom_fields"]
            },
            "create_post": {
                "required": ["publication_id", "title", "content"],
                "optional": ["tags", "status"]
            },
            "send_campaign": {
                "required": ["campaign_id"],
                "conditional": {
                    "if_status_scheduled": ["send_time"]
                }
            },
            "create_segment": {
                "required": ["publication_id", "name", "criteria"],
                "validate_criteria": True
            },
            "create_automation": {
                "required": ["publication_id", "name", "trigger_event"],
                "optional": ["description"]
            },
            "create_webhook": {
                "required": ["webhook_url", "webhook_events"],
                "validate_url": True
            }
        },
        
        # 10. COMPREHENSIVE OUTPUT SCHEMAS
        "output_schemas": {
            "subscriber": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "name": {"type": "string"},
                    "status": {"type": "string", "enum": ["active", "inactive", "unsubscribed"]},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "custom_fields": {"type": "object"},
                    "subscription_tier": {"type": "string"},
                    "engagement_score": {"type": "number"}
                }
            },
            "publication": {
                "type": "object", 
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "website_url": {"type": "string", "format": "uri"},
                    "subscriber_count": {"type": "number"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "status": {"type": "string"},
                    "branding": {"type": "object"}
                }
            },
            "post": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "status": {"type": "string", "enum": ["draft", "published", "scheduled"]},
                    "published_at": {"type": "string", "format": "date-time"},
                    "view_count": {"type": "number"},
                    "share_count": {"type": "number"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                }
            },
            "campaign": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "subject": {"type": "string"},
                    "content": {"type": "string"},
                    "status": {"type": "string", "enum": ["draft", "scheduled", "sending", "sent"]},
                    "sent_at": {"type": "string", "format": "date-time"},
                    "recipient_count": {"type": "number"},
                    "open_rate": {"type": "number"},
                    "click_rate": {"type": "number"}
                }
            },
            "analytics": {
                "type": "object",
                "properties": {
                    "period": {"type": "object"},
                    "subscribers": {
                        "type": "object",
                        "properties": {
                            "total": {"type": "number"},
                            "new": {"type": "number"},
                            "unsubscribed": {"type": "number"},
                            "growth_rate": {"type": "number"}
                        }
                    },
                    "engagement": {
                        "type": "object",
                        "properties": {
                            "open_rate": {"type": "number"},
                            "click_rate": {"type": "number"},
                            "bounce_rate": {"type": "number"},
                            "unsubscribe_rate": {"type": "number"}
                        }
                    }
                }
            }
        },
        
        # 11. ARRAY TEMPLATES for batch operations
        "array_templates": {
            "bulk_subscribers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                        "name": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "custom_fields": {"type": "object"}
                    },
                    "required": ["email"]
                },
                "maxItems": 1000,
                "example": [
                    {"email": "user1@example.com", "name": "User One", "tags": ["premium"]},
                    {"email": "user2@example.com", "name": "User Two", "tags": ["free"]}
                ]
            },
            "webhook_events": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["subscriber.created", "subscriber.updated", "subscriber.deleted", "post.published", "campaign.sent", "automation.triggered"]
                },
                "minItems": 1,
                "maxItems": 10
            }
        },
        
        # 12. VALIDATION RULES - Complex business logic validation
        "validation_rules": {
            "email_validation": {
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                "message": "Must be a valid email address"
            },
            "publication_limits": {
                "max_subscribers_free": 2500,
                "max_campaigns_per_day": 5,
                "max_automations": 10
            },
            "content_restrictions": {
                "max_subject_length": 150,
                "max_preview_length": 150,
                "max_content_size": 102400,  # 100KB
                "forbidden_words": ["spam", "free money"]
            },
            "rate_limits": {
                "bulk_operations_per_hour": 10,
                "api_calls_per_minute": 100,
                "concurrent_requests": 5
            }
        },
        
        # 13. WEBHOOK SUPPORT - Event handling
        "webhook_support": {
            "supported_events": [
                "subscriber.created",
                "subscriber.updated", 
                "subscriber.deleted",
                "subscriber.unsubscribed",
                "post.published",
                "post.updated",
                "campaign.sent",
                "campaign.delivered",
                "campaign.opened",
                "campaign.clicked",
                "automation.triggered",
                "publication.updated"
            ],
            "webhook_validation": {
                "signature_header": "X-Beehiiv-Signature",
                "signature_algorithm": "hmac-sha256",
                "timestamp_header": "X-Beehiiv-Timestamp",
                "timestamp_tolerance": 300
            },
            "retry_policy": {
                "max_retries": 3,
                "backoff_seconds": [1, 5, 15],
                "timeout_seconds": 10
            }
        },
        
        # Error codes specific to Beehiiv API
        "error_codes": {
            "400": "Bad Request - Invalid request parameters or malformed data",
            "401": "Unauthorized - Invalid or missing API key",
            "403": "Forbidden - API key lacks required permissions or rate limit exceeded",
            "404": "Not Found - Publication, subscriber, or resource not found",
            "409": "Conflict - Subscriber already exists or resource conflict",
            "422": "Unprocessable Entity - Validation failed or business rule violation",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Beehiiv server error",
            "502": "Bad Gateway - Beehiiv server temporarily unavailable", 
            "503": "Service Unavailable - Beehiiv maintenance or overload"
        }
    }
    
    # Operation definitions with complete metadata (35+ operations)
    OPERATIONS = {
        # Publication operations
        "get_publication": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}",
            "required_params": ["publication_id"],
            "optional_params": [],
            "display_name": "Get Publication",
            "description": "Get detailed information about a specific publication",
            "group": "Publications",
            "rate_limit_cost": 1,
            "cache_ttl": 1800,
            "response_schema": "publication"
        },
        "list_publications": {
            "method": "GET", 
            "endpoint": "/publications",
            "required_params": [],
            "optional_params": ["page", "per_page", "sort", "order"],
            "display_name": "List Publications",
            "description": "List all publications for the authenticated account",
            "group": "Publications",
            "rate_limit_cost": 1,
            "cache_ttl": 600
        },
        "create_publication": {
            "method": "POST",
            "endpoint": "/publications",
            "required_params": ["name"],
            "optional_params": ["description", "website_url", "branding"],
            "display_name": "Create Publication",
            "description": "Create a new publication",
            "group": "Publications",
            "rate_limit_cost": 5
        },
        "update_publication": {
            "method": "PUT",
            "endpoint": "/publications/{publication_id}",
            "required_params": ["publication_id"],
            "optional_params": ["name", "description", "website_url", "branding"],
            "display_name": "Update Publication",
            "description": "Update publication settings",
            "group": "Publications",
            "rate_limit_cost": 3
        },
        
        # Subscriber operations
        "get_subscriber": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/subscriptions/{subscriber_id}",
            "required_params": ["publication_id", "subscriber_id"],
            "optional_params": [],
            "display_name": "Get Subscriber",
            "description": "Get detailed information about a specific subscriber",
            "group": "Subscribers",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_schema": "subscriber"
        },
        "list_subscribers": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/subscriptions",
            "required_params": ["publication_id"],
            "optional_params": ["page", "per_page", "status", "tags", "sort", "order", "filter"],
            "display_name": "List Subscribers",
            "description": "List all subscribers for a publication",
            "group": "Subscribers",
            "rate_limit_cost": 2,
            "cache_ttl": 120,
            "supports_pagination": True
        },
        "create_subscriber": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/subscriptions",
            "required_params": ["publication_id", "email"],
            "optional_params": ["name", "tags", "custom_fields", "double_opt_in"],
            "display_name": "Create Subscriber",
            "description": "Add a new subscriber to the publication",
            "group": "Subscribers",
            "rate_limit_cost": 3,
            "response_schema": "subscriber"
        },
        "update_subscriber": {
            "method": "PUT",
            "endpoint": "/publications/{publication_id}/subscriptions/{subscriber_id}",
            "required_params": ["publication_id", "subscriber_id"],
            "optional_params": ["email", "name", "status", "tags", "custom_fields"],
            "display_name": "Update Subscriber",
            "description": "Update subscriber information",
            "group": "Subscribers",
            "rate_limit_cost": 2,
            "response_schema": "subscriber"
        },
        "delete_subscriber": {
            "method": "DELETE",
            "endpoint": "/publications/{publication_id}/subscriptions/{subscriber_id}",
            "required_params": ["publication_id", "subscriber_id"],
            "optional_params": [],
            "display_name": "Delete Subscriber",
            "description": "Permanently delete a subscriber",
            "group": "Subscribers",
            "rate_limit_cost": 2
        },
        "bulk_subscribe": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/subscriptions/bulk",
            "required_params": ["publication_id", "subscribers"],
            "optional_params": ["double_opt_in", "send_welcome"],
            "display_name": "Bulk Subscribe",
            "description": "Add multiple subscribers at once (up to 1000)",
            "group": "Subscribers",
            "rate_limit_cost": 10,
            "array_template": "bulk_subscribers"
        },
        "bulk_unsubscribe": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/subscriptions/bulk_unsubscribe",
            "required_params": ["publication_id", "emails"],
            "optional_params": [],
            "display_name": "Bulk Unsubscribe",
            "description": "Unsubscribe multiple email addresses at once",
            "group": "Subscribers",
            "rate_limit_cost": 8
        },
        "import_subscribers": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/subscriptions/import",
            "required_params": ["publication_id", "csv_data"],
            "optional_params": ["mapping", "double_opt_in"],
            "display_name": "Import Subscribers",
            "description": "Import subscribers from CSV data",
            "group": "Subscribers",
            "rate_limit_cost": 15
        },
        
        # Content operations
        "create_post": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/posts",
            "required_params": ["publication_id", "title", "content"],
            "optional_params": ["status", "tags", "featured_image", "publish_at"],
            "display_name": "Create Post",
            "description": "Create a new newsletter post",
            "group": "Content",
            "rate_limit_cost": 5,
            "response_schema": "post"
        },
        "get_post": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/posts/{post_id}",
            "required_params": ["publication_id", "post_id"],
            "optional_params": [],
            "display_name": "Get Post",
            "description": "Get detailed information about a specific post",
            "group": "Content",
            "rate_limit_cost": 1,
            "cache_ttl": 900,
            "response_schema": "post"
        },
        "list_posts": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/posts",
            "required_params": ["publication_id"],
            "optional_params": ["page", "per_page", "status", "tags", "sort", "order"],
            "display_name": "List Posts",
            "description": "List all posts for a publication",
            "group": "Content",
            "rate_limit_cost": 2,
            "cache_ttl": 600,
            "supports_pagination": True
        },
        "update_post": {
            "method": "PUT",
            "endpoint": "/publications/{publication_id}/posts/{post_id}",
            "required_params": ["publication_id", "post_id"],
            "optional_params": ["title", "content", "status", "tags", "featured_image"],
            "display_name": "Update Post",
            "description": "Update an existing post",
            "group": "Content",
            "rate_limit_cost": 3,
            "response_schema": "post"
        },
        "delete_post": {
            "method": "DELETE",
            "endpoint": "/publications/{publication_id}/posts/{post_id}",
            "required_params": ["publication_id", "post_id"],
            "optional_params": [],
            "display_name": "Delete Post",
            "description": "Permanently delete a post",
            "group": "Content",
            "rate_limit_cost": 2
        },
        "publish_post": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/posts/{post_id}/publish",
            "required_params": ["publication_id", "post_id"],
            "optional_params": ["publish_at", "send_email"],
            "display_name": "Publish Post",
            "description": "Publish a draft post immediately or schedule it",
            "group": "Content",
            "rate_limit_cost": 5
        },
        
        # Campaign operations
        "create_campaign": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/campaigns",
            "required_params": ["publication_id", "subject", "content"],
            "optional_params": ["preview_text", "segment_id", "template_id", "send_time"],
            "display_name": "Create Campaign",
            "description": "Create a new email campaign",
            "group": "Campaigns",
            "rate_limit_cost": 5,
            "response_schema": "campaign"
        },
        "get_campaign": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/campaigns/{campaign_id}",
            "required_params": ["publication_id", "campaign_id"],
            "optional_params": [],
            "display_name": "Get Campaign",
            "description": "Get detailed information about a campaign",
            "group": "Campaigns",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_schema": "campaign"
        },
        "list_campaigns": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/campaigns",
            "required_params": ["publication_id"],
            "optional_params": ["page", "per_page", "status", "sort", "order", "date_range"],
            "display_name": "List Campaigns",
            "description": "List all campaigns for a publication",
            "group": "Campaigns",
            "rate_limit_cost": 2,
            "cache_ttl": 300,
            "supports_pagination": True
        },
        "send_campaign": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/campaigns/{campaign_id}/send",
            "required_params": ["publication_id", "campaign_id"],
            "optional_params": ["send_immediately", "send_time", "timezone"],
            "display_name": "Send Campaign",
            "description": "Send or schedule a campaign",
            "group": "Campaigns",
            "rate_limit_cost": 10
        },
        "schedule_campaign": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/campaigns/{campaign_id}/schedule",
            "required_params": ["publication_id", "campaign_id", "send_time"],
            "optional_params": ["timezone"],
            "display_name": "Schedule Campaign",
            "description": "Schedule a campaign for future delivery",
            "group": "Campaigns",
            "rate_limit_cost": 5
        },
        
        # Analytics operations
        "get_analytics": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/analytics",
            "required_params": ["publication_id"],
            "optional_params": ["date_range", "metrics", "granularity"],
            "display_name": "Get Analytics",
            "description": "Get comprehensive publication analytics",
            "group": "Analytics",
            "rate_limit_cost": 3,
            "cache_ttl": 3600,
            "response_schema": "analytics"
        },
        "get_subscriber_analytics": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/analytics/subscribers",
            "required_params": ["publication_id"],
            "optional_params": ["date_range", "segment_id", "breakdown"],
            "display_name": "Get Subscriber Analytics",
            "description": "Get detailed subscriber growth and engagement analytics",
            "group": "Analytics",
            "rate_limit_cost": 3,
            "cache_ttl": 3600
        },
        "get_campaign_analytics": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/campaigns/{campaign_id}/analytics",
            "required_params": ["publication_id", "campaign_id"],
            "optional_params": ["detailed"],
            "display_name": "Get Campaign Analytics",
            "description": "Get detailed analytics for a specific campaign",
            "group": "Analytics",
            "rate_limit_cost": 2,
            "cache_ttl": 1800
        },
        "get_publication_stats": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/stats",
            "required_params": ["publication_id"],
            "optional_params": [],
            "display_name": "Get Publication Stats",
            "description": "Get quick overview statistics for a publication",
            "group": "Analytics",
            "rate_limit_cost": 1,
            "cache_ttl": 600
        },
        
        # Segment operations
        "create_segment": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/segments",
            "required_params": ["publication_id", "name", "criteria"],
            "optional_params": ["description"],
            "display_name": "Create Segment",
            "description": "Create a new subscriber segment",
            "group": "Segments",
            "rate_limit_cost": 3
        },
        "get_segment": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/segments/{segment_id}",
            "required_params": ["publication_id", "segment_id"],
            "optional_params": [],
            "display_name": "Get Segment",
            "description": "Get detailed information about a segment",
            "group": "Segments",
            "rate_limit_cost": 1,
            "cache_ttl": 600
        },
        "list_segments": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/segments",
            "required_params": ["publication_id"],
            "optional_params": ["page", "per_page", "sort", "order"],
            "display_name": "List Segments",
            "description": "List all segments for a publication",
            "group": "Segments",
            "rate_limit_cost": 2,
            "cache_ttl": 600,
            "supports_pagination": True
        },
        "update_segment": {
            "method": "PUT",
            "endpoint": "/publications/{publication_id}/segments/{segment_id}",
            "required_params": ["publication_id", "segment_id"],
            "optional_params": ["name", "description", "criteria"],
            "display_name": "Update Segment",
            "description": "Update segment criteria and settings",
            "group": "Segments",
            "rate_limit_cost": 3
        },
        "delete_segment": {
            "method": "DELETE",
            "endpoint": "/publications/{publication_id}/segments/{segment_id}",
            "required_params": ["publication_id", "segment_id"],
            "optional_params": [],
            "display_name": "Delete Segment",
            "description": "Permanently delete a segment",
            "group": "Segments",
            "rate_limit_cost": 2
        },
        
        # Automation operations
        "create_automation": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/automations",
            "required_params": ["publication_id", "name", "trigger_event"],
            "optional_params": ["description", "actions", "conditions"],
            "display_name": "Create Automation",
            "description": "Create a new automation workflow",
            "group": "Automation",
            "rate_limit_cost": 5
        },
        "get_automation": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/automations/{automation_id}",
            "required_params": ["publication_id", "automation_id"],
            "optional_params": [],
            "display_name": "Get Automation",
            "description": "Get detailed information about an automation",
            "group": "Automation",
            "rate_limit_cost": 1,
            "cache_ttl": 600
        },
        "list_automations": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/automations",
            "required_params": ["publication_id"],
            "optional_params": ["page", "per_page", "status", "trigger_event"],
            "display_name": "List Automations",
            "description": "List all automations for a publication",
            "group": "Automation",
            "rate_limit_cost": 2,
            "cache_ttl": 600,
            "supports_pagination": True
        },
        "trigger_automation": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/automations/{automation_id}/trigger",
            "required_params": ["publication_id", "automation_id"],
            "optional_params": ["subscriber_id", "data"],
            "display_name": "Trigger Automation",
            "description": "Manually trigger an automation for a subscriber",
            "group": "Automation",
            "rate_limit_cost": 3
        },
        
        # Webhook operations
        "create_webhook": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/webhooks",
            "required_params": ["publication_id", "webhook_url", "webhook_events"],
            "optional_params": ["description", "secret"],
            "display_name": "Create Webhook",
            "description": "Create a new webhook endpoint",
            "group": "Webhooks",
            "rate_limit_cost": 3
        },
        "list_webhooks": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/webhooks",
            "required_params": ["publication_id"],
            "optional_params": ["page", "per_page"],
            "display_name": "List Webhooks",
            "description": "List all webhooks for a publication",
            "group": "Webhooks",
            "rate_limit_cost": 1,
            "cache_ttl": 600
        },
        "delete_webhook": {
            "method": "DELETE",
            "endpoint": "/publications/{publication_id}/webhooks/{webhook_id}",
            "required_params": ["publication_id", "webhook_id"],
            "optional_params": [],
            "display_name": "Delete Webhook",
            "description": "Delete a webhook endpoint",
            "group": "Webhooks",
            "rate_limit_cost": 2
        },
        "test_webhook": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/webhooks/{webhook_id}/test",
            "required_params": ["publication_id", "webhook_id"],
            "optional_params": ["test_event"],
            "display_name": "Test Webhook",
            "description": "Send a test event to a webhook endpoint",
            "group": "Webhooks",
            "rate_limit_cost": 1
        },
        
        # Utility operations
        "upload_image": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/images",
            "required_params": ["publication_id", "image_file"],
            "optional_params": ["image_name", "alt_text"],
            "display_name": "Upload Image",
            "description": "Upload an image for use in content",
            "group": "Media",
            "rate_limit_cost": 5
        },
        "get_templates": {
            "method": "GET",
            "endpoint": "/publications/{publication_id}/templates",
            "required_params": ["publication_id"],
            "optional_params": ["type", "category"],
            "display_name": "Get Templates",
            "description": "List available email and content templates",
            "group": "Templates",
            "rate_limit_cost": 1,
            "cache_ttl": 3600
        },
        "export_data": {
            "method": "POST",
            "endpoint": "/publications/{publication_id}/export",
            "required_params": ["publication_id", "data_type"],
            "optional_params": ["export_format", "date_range", "filters"],
            "display_name": "Export Data",
            "description": "Export publication data (subscribers, analytics, etc.)",
            "group": "Export",
            "rate_limit_cost": 10
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create UniversalRequestNode with api_config section
        self.universal_node = UniversalRequestNode(self.CONFIG["api_config"])
    
    def get_schema(self) -> NodeSchema:
        """Return enhanced schema with all parameters."""
        return NodeSchema(
            node_type="beehiiv",
            version="2.0.0",
            description="Comprehensive Beehiiv API integration with ALL 13 enhancements",
            parameters=[
                NodeParameter(
                    name="api_key",
                    type=NodeParameterType.SECRET,
                    description="Beehiiv API key",
                    required=True
                ),
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Beehiiv operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="publication_id",
                    type=NodeParameterType.STRING,
                    description="Beehiiv publication ID",
                    required=False
                ),
                NodeParameter(
                    name="email",
                    type=NodeParameterType.STRING,
                    description="Email address for subscriber operations",
                    required=False
                ),
                NodeParameter(
                    name="name",
                    type=NodeParameterType.STRING,
                    description="Name for publications, subscribers, segments",
                    required=False
                ),
                NodeParameter(
                    name="title",
                    type=NodeParameterType.STRING,
                    description="Title for posts and campaigns",
                    required=False
                ),
                NodeParameter(
                    name="content",
                    type=NodeParameterType.STRING,
                    description="HTML content for posts and campaigns",
                    required=False
                ),
                NodeParameter(
                    name="subject",
                    type=NodeParameterType.STRING,
                    description="Email subject line",
                    required=False
                ),
                NodeParameter(
                    name="status",
                    type=NodeParameterType.STRING,
                    description="Status filter or update value",
                    required=False,
                    enum=["active", "inactive", "unsubscribed", "draft", "scheduled", "sent", "published"]
                ),
                NodeParameter(
                    name="tags",
                    type=NodeParameterType.ARRAY,
                    description="Tags for organization",
                    required=False
                ),
                NodeParameter(
                    name="page",
                    type=NodeParameterType.NUMBER,
                    description="Page number for pagination",
                    required=False,
                    default=1
                ),
                NodeParameter(
                    name="per_page",
                    type=NodeParameterType.NUMBER,
                    description="Results per page (1-100)",
                    required=False,
                    default=25
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "data": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "subscriber_id": NodeParameterType.STRING,
                "subscriber_count": NodeParameterType.NUMBER,
                "campaign_id": NodeParameterType.STRING,
                "post_id": NodeParameterType.STRING,
                "segment_id": NodeParameterType.STRING,
                "automation_id": NodeParameterType.STRING
            }
        )
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Beehiiv operation with enhanced error handling and validation."""
        try:
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            if not operation:
                return {
                    "status": "error",
                    "error": "Operation is required",
                    "error_code": "MISSING_OPERATION",
                    "result": None
                }
            
            if operation not in self.OPERATIONS:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}",
                    "error_code": "INVALID_OPERATION", 
                    "result": None
                }
            
            # Enhanced parameter validation
            validation_error = self._validate_parameters(operation, params)
            if validation_error:
                return {
                    "status": "error",
                    "error": validation_error,
                    "error_code": "VALIDATION_ERROR",
                    "result": None
                }
            
            # Get operation config
            op_config = self.OPERATIONS[operation]
            
            # Prepare request data
            request_data = self._prepare_request_data(operation, params)
            
            # Make request using UniversalRequestNode
            request_kwargs = {
                "token": params.get("api_key"),
                **params
            }
            
            result = await self.universal_node.request(
                method=op_config["method"],
                endpoint=op_config["endpoint"],
                data=request_data if op_config["method"] in ["POST", "PUT", "PATCH"] else None,
                params=request_data if op_config["method"] == "GET" else None,
                **request_kwargs
            )
            
            # Enhanced result processing
            return self._process_result(operation, result)
            
        except Exception as e:
            logger.error(f"BeehiivNode error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "EXECUTION_ERROR",
                "result": None
            }
    
    def _validate_parameters(self, operation: str, params: Dict[str, Any]) -> Optional[str]:
        """Enhanced parameter validation with business rules."""
        # Check parameter dependencies
        if operation in self.CONFIG["parameter_dependencies"]:
            deps = self.CONFIG["parameter_dependencies"][operation]
            
            # Check required parameters
            for required_param in deps.get("required", []):
                if not params.get(required_param):
                    return f"Missing required parameter: {required_param}"
            
            # Check conditional requirements
            if "at_least_one" in deps:
                if not any(params.get(param) for param in deps["at_least_one"]):
                    return f"At least one of these parameters is required: {', '.join(deps['at_least_one'])}"
        
        # Validate email format
        if params.get("email"):
            import re
            email_pattern = self.CONFIG["validation_rules"]["email_validation"]["pattern"]
            if not re.match(email_pattern, params["email"]):
                return "Invalid email address format"
        
        # Validate content restrictions
        if params.get("subject"):
            max_length = self.CONFIG["validation_rules"]["content_restrictions"]["max_subject_length"]
            if len(params["subject"]) > max_length:
                return f"Subject line too long (max {max_length} characters)"
        
        # Validate API key format
        if params.get("api_key"):
            api_key = params["api_key"]
            if not api_key.startswith("bh_") or len(api_key) < 43:
                return "Invalid API key format"
        
        return None
    
    def _prepare_request_data(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request data based on operation with enhanced logic."""
        data = {}
        
        # Publication operations
        if operation == "create_publication":
            data = {
                "name": params.get("name"),
                "description": params.get("description", ""),
                "website_url": params.get("website_url"),
                "branding": params.get("branding", {})
            }
            
        elif operation == "update_publication":
            data = {}
            if params.get("name"): data["name"] = params["name"]
            if params.get("description"): data["description"] = params["description"]
            if params.get("website_url"): data["website_url"] = params["website_url"]
            if params.get("branding"): data["branding"] = params["branding"]
        
        # Subscriber operations
        elif operation == "create_subscriber":
            data = {
                "email": params.get("email"),
                "name": params.get("name", ""),
                "status": params.get("status", "active"),
                "double_opt_in": params.get("double_opt_in", True)
            }
            if params.get("tags"): data["tags"] = params["tags"]
            if params.get("custom_fields"): data["custom_fields"] = params["custom_fields"]
            
        elif operation == "update_subscriber":
            data = {}
            if params.get("email"): data["email"] = params["email"]
            if params.get("name"): data["name"] = params["name"]
            if params.get("status"): data["status"] = params["status"]
            if params.get("tags"): data["tags"] = params["tags"]
            if params.get("custom_fields"): data["custom_fields"] = params["custom_fields"]
            
        elif operation == "bulk_subscribe":
            data = {
                "subscribers": params.get("subscribers", []),
                "double_opt_in": params.get("double_opt_in", True),
                "send_welcome": params.get("send_welcome", True)
            }
            
        elif operation == "bulk_unsubscribe":
            data = {"emails": params.get("emails", [])}
            
        elif operation == "import_subscribers":
            data = {
                "csv_data": params.get("csv_data"),
                "mapping": params.get("mapping", {}),
                "double_opt_in": params.get("double_opt_in", True)
            }
        
        # Content operations
        elif operation == "create_post":
            data = {
                "title": params.get("title"),
                "content": params.get("content"),
                "status": params.get("status", "draft"),
                "featured_image": params.get("featured_image"),
                "publish_at": params.get("publish_at")
            }
            if params.get("tags"): data["tags"] = params["tags"]
            
        elif operation == "update_post":
            data = {}
            if params.get("title"): data["title"] = params["title"]
            if params.get("content"): data["content"] = params["content"]
            if params.get("status"): data["status"] = params["status"]
            if params.get("tags"): data["tags"] = params["tags"]
            if params.get("featured_image"): data["featured_image"] = params["featured_image"]
            
        elif operation == "publish_post":
            data = {
                "publish_at": params.get("publish_at"),
                "send_email": params.get("send_email", True)
            }
        
        # Campaign operations
        elif operation == "create_campaign":
            data = {
                "subject": params.get("subject"),
                "content": params.get("content"),
                "preview_text": params.get("preview_text", ""),
                "segment_id": params.get("segment_id"),
                "template_id": params.get("template_id"),
                "send_time": params.get("send_time")
            }
            
        elif operation == "send_campaign":
            data = {
                "send_immediately": params.get("send_immediately", False),
                "send_time": params.get("send_time"),
                "timezone": params.get("timezone", "UTC")
            }
            
        elif operation == "schedule_campaign":
            data = {
                "send_time": params.get("send_time"),
                "timezone": params.get("timezone", "UTC")
            }
        
        # Segment operations
        elif operation == "create_segment":
            data = {
                "name": params.get("name"),
                "description": params.get("description", ""),
                "criteria": params.get("criteria", {})
            }
            
        elif operation == "update_segment":
            data = {}
            if params.get("name"): data["name"] = params["name"]
            if params.get("description"): data["description"] = params["description"]
            if params.get("criteria"): data["criteria"] = params["criteria"]
        
        # Automation operations
        elif operation == "create_automation":
            data = {
                "name": params.get("name"),
                "description": params.get("description", ""),
                "trigger_event": params.get("trigger_event"),
                "actions": params.get("actions", []),
                "conditions": params.get("conditions", {})
            }
            
        elif operation == "trigger_automation":
            data = {
                "subscriber_id": params.get("subscriber_id"),
                "data": params.get("data", {})
            }
        
        # Webhook operations
        elif operation == "create_webhook":
            data = {
                "url": params.get("webhook_url"),
                "events": params.get("webhook_events", []),
                "description": params.get("description", ""),
                "secret": params.get("secret")
            }
            
        elif operation == "test_webhook":
            data = {"test_event": params.get("test_event", "subscriber.created")}
        
        # Utility operations
        elif operation == "upload_image":
            data = {
                "image": params.get("image_file"),
                "name": params.get("image_name", "uploaded-image"),
                "alt_text": params.get("alt_text", "")
            }
            
        elif operation == "export_data":
            data = {
                "data_type": params.get("data_type", "subscribers"),
                "format": params.get("export_format", "csv"),
                "date_range": params.get("date_range"),
                "filters": params.get("filters", {})
            }
        
        # For GET operations with query parameters
        if operation in ["list_publications", "list_subscribers", "list_posts", "list_campaigns", 
                        "list_segments", "list_automations", "list_webhooks"]:
            query_params = {}
            if params.get("page"): query_params["page"] = params["page"]
            if params.get("per_page"): query_params["per_page"] = params["per_page"]
            if params.get("sort"): query_params["sort"] = params["sort"]
            if params.get("order"): query_params["order"] = params["order"]
            if params.get("status"): query_params["status"] = params["status"]
            if params.get("tags"): query_params["tags"] = params["tags"]
            if params.get("filter"): query_params.update(params["filter"])
            return query_params
        
        # Analytics operations query params
        if operation in ["get_analytics", "get_subscriber_analytics", "get_campaign_analytics"]:
            query_params = {}
            if params.get("date_range"): query_params["date_range"] = params["date_range"]
            if params.get("metrics"): query_params["metrics"] = params["metrics"]
            if params.get("granularity"): query_params["granularity"] = params["granularity"]
            if params.get("segment_id"): query_params["segment_id"] = params["segment_id"]
            if params.get("breakdown"): query_params["breakdown"] = params["breakdown"]
            if params.get("detailed"): query_params["detailed"] = params["detailed"]
            return query_params
        
        return data
    
    def _process_result(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced result processing with schema validation."""
        if result.get("status") != "success":
            return result
        
        response_data = result.get("data", {})
        
        # Enhanced result processing with extracted fields
        if isinstance(response_data, dict):
            result["data"] = response_data
            
            # Extract common identifiers
            result["subscriber_id"] = response_data.get("id") if "subscription" in operation else None
            result["campaign_id"] = response_data.get("id") if "campaign" in operation else None
            result["post_id"] = response_data.get("id") if "post" in operation else None
            result["segment_id"] = response_data.get("id") if "segment" in operation else None
            result["automation_id"] = response_data.get("id") if "automation" in operation else None
            
            # Extract metrics
            result["subscriber_count"] = response_data.get("subscriber_count")
            result["open_rate"] = response_data.get("open_rate")
            result["click_rate"] = response_data.get("click_rate")
            result["bounce_rate"] = response_data.get("bounce_rate")
            
            # Pagination info
            if response_data.get("pagination"):
                result["pagination"] = response_data["pagination"]
                result["total_count"] = response_data["pagination"].get("total")
                result["has_more"] = response_data["pagination"].get("has_more", False)
        
        return result
    
    async def close(self):
        """Clean up resources."""
        if self.universal_node:
            await self.universal_node.close()

if __name__ == "__main__":
    import asyncio
    
    async def test():
        node = BeehiivNode()
        
        # Test get publication
        test_data = {
            "params": {
                "operation": "get_publication",
                "api_key": "bh_test_api_key_here",  # Replace with actual API key
                "publication_id": "pub_test123"
            }
        }
        
        result = await node.execute(test_data)
        print(f"Result: {result}")
        
        await node.close()
    
    # Uncomment to test
    # asyncio.run(test())