#!/usr/bin/env python3
"""
ApiTemplate.io Node - Enhanced with ALL 13 advanced features and complete operation recovery
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

class ApiTemplateIoNode(BaseNode):
    """
    Enhanced ApiTemplate.io node with ALL 13 advanced features and complete operation recovery.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "apitemplate",
            "display_name": "ApiTemplate.io",
            "description": "Comprehensive ApiTemplate.io API integration for image and PDF generation, template management, batch processing, and automation workflows",
            "category": "content",
            "vendor": "apitemplate.io", 
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["template", "image", "pdf", "generation", "automation", "batch", "design"],
            "documentation_url": "https://apitemplate.io/docs/",
            "icon": "https://apitemplate.io/favicon.ico",
            "color": "#2563eb",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://rest.apitemplate.io",
            "authentication": {
                "type": "api_key_header",
                "header": "X-API-KEY"
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
                "timeout_ms": 60000
            },
            "rate_limiting": {
                "requests_per_minute": 300,
                "requests_per_second": 5.0,
                "burst_size": 10,
                "cost_per_request": 0.01,
                "quota_type": "requests"
            },
            "timeouts": {
                "connect": 10.0,
                "read": 60.0,
                "total": 90.0
            }
        },
        
        # Enhanced pricing information
        "pricing": {
            "cost_per_request": 0.05,
            "cost_per_image": 0.10,
            "cost_per_pdf": 0.15,
            "billing_unit": "generation",
            "free_tier_limit": 50
        },
        
        # Performance monitoring
        "monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "generation_count"],
            "alerts": {
                "error_rate_threshold": 0.05,
                "response_time_threshold": 30000
            }
        },
        
        # Intelligent caching
        "caching": {
            "enabled": True,
            "cache_key_template": "{operation}:{template_id}:{hash}",
            "ttl_seconds": 1800,
            "cache_conditions": {
                "only_for": ["GET"],
                "exclude_params": ["timestamp", "nonce", "callback_url"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/v2/templates"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://apitemplate.io/docs/api-reference/",
            "setup_guide": "https://apitemplate.io/docs/getting-started/",
            "troubleshooting": "https://apitemplate.io/docs/troubleshooting/",
            "changelog": "https://apitemplate.io/docs/changelog/"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "ApiTemplate.io API key",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "API key must contain only alphanumeric characters, underscores, and dashes",
                    "minLength": 20,
                    "maxLength": 100
                }
            },
            "operation": {
                "type": "string",
                "description": "The ApiTemplate.io operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    "get_templates", "get_template", "create_template", "update_template", "delete_template", "duplicate_template",
                    "generate_image", "generate_image_async", "generate_image_url", "generate_images_batch",
                    "generate_pdf", "generate_pdf_async", "generate_pdf_url", "generate_pdfs_batch",
                    "get_job_status", "get_job_result", "list_jobs", "cancel_job",
                    "get_account_info", "get_usage_stats", "get_credits",
                    "upload_image", "upload_file", "get_uploads", "delete_upload"
                ]
            },
            "template_id": {
                "type": "string",
                "description": "Template ID for template-specific operations",
                "required": False,
                "group": "Template",
                "examples": ["template_123abc", "tmpl_xyz789"],
                "validation": {
                    "minLength": 5,
                    "maxLength": 50
                }
            },
            "job_id": {
                "type": "string",
                "description": "Job ID for job-specific operations",
                "required": False,
                "group": "Job"
            },
            "upload_id": {
                "type": "string",
                "description": "Upload ID for upload operations",
                "required": False,
                "group": "Upload"
            },
            "template_name": {
                "type": "string",
                "description": "Template name for creation and updates",
                "required": False,
                "group": "Template",
                "examples": ["Business Card Template", "Social Media Post"],
                "validation": {
                    "maxLength": 100
                }
            },
            "template_type": {
                "type": "string",
                "description": "Template type",
                "required": False,
                "default": "image",
                "group": "Template",
                "validation": {
                    "enum": ["image", "pdf", "html", "svg"]
                }
            },
            "template_data": {
                "type": "object",
                "description": "Template configuration data including elements and properties",
                "required": False,
                "group": "Template"
            },
            "template_tags": {
                "type": "array",
                "description": "Template tags for organization and categorization",
                "required": False,
                "group": "Template"
            },
            "data": {
                "type": "object",
                "description": "Data to merge with template for generation",
                "required": False,
                "group": "Generation",
                "examples": [{"title": "Hello World", "name": "John Doe"}]
            },
            "properties": {
                "type": "object",
                "description": "Additional properties for generation (width, height, quality, etc.)",
                "required": False,
                "group": "Generation"
            },
            "format": {
                "type": "string",
                "description": "Output format for generated content",
                "required": False,
                "default": "png",
                "group": "Output",
                "validation": {
                    "enum": ["png", "jpg", "jpeg", "pdf", "svg", "webp"]
                }
            },
            "quality": {
                "type": "integer",
                "description": "Output quality (1-100 for images)",
                "required": False,
                "default": 90,
                "group": "Quality",
                "validation": {
                    "minimum": 1,
                    "maximum": 100
                },
                "examples": [70, 85, 90, 95]
            },
            "width": {
                "type": "integer",
                "description": "Output width in pixels",
                "required": False,
                "group": "Dimensions",
                "validation": {
                    "minimum": 1,
                    "maximum": 8000
                },
                "examples": [800, 1200, 1920, 3000]
            },
            "height": {
                "type": "integer",
                "description": "Output height in pixels",
                "required": False,
                "group": "Dimensions",
                "validation": {
                    "minimum": 1,
                    "maximum": 8000
                },
                "examples": [600, 800, 1080, 2000]
            },
            "scale": {
                "type": "number",
                "description": "Output scale factor for high-resolution outputs",
                "required": False,
                "default": 1.0,
                "group": "Quality",
                "validation": {
                    "minimum": 0.1,
                    "maximum": 5.0
                }
            },
            "batch_data": {
                "type": "array",
                "description": "Array of data objects for batch generation",
                "required": False,
                "group": "Batch"
            },
            "callback_url": {
                "type": "string",
                "description": "Callback URL for async operations",
                "required": False,
                "group": "Async",
                "validation": {
                    "format": "uri"
                }
            },
            "webhook_secret": {
                "type": "string",
                "description": "Webhook secret for callback verification",
                "required": False,
                "sensitive": True,
                "group": "Async"
            },
            "file_content": {
                "type": "string",
                "description": "Base64 encoded file content for upload",
                "required": False,
                "group": "Upload"
            },
            "file_name": {
                "type": "string",
                "description": "File name for upload operations",
                "required": False,
                "group": "Upload",
                "examples": ["logo.png", "banner.jpg", "document.pdf"]
            },
            "file_type": {
                "type": "string",
                "description": "File MIME type",
                "required": False,
                "group": "Upload",
                "examples": ["image/png", "image/jpeg", "application/pdf"]
            },
            "file_url": {
                "type": "string",
                "description": "URL of file to upload",
                "required": False,
                "group": "Upload",
                "validation": {
                    "format": "uri"
                }
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful ApiTemplate.io API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from ApiTemplate.io API"},
                    "result": {"type": "object", "description": "Generated content or operation result"},
                    "url": {"type": "string", "description": "Download URL for generated content"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "ApiTemplate.io error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "default": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "optional_env_keys": ["APITEMPLATE_TEAM_ID"]
            }
        },
        
        # Error codes specific to ApiTemplate.io
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid API key",
            "402": "Payment Required - Insufficient credits or quota exceeded", 
            "403": "Forbidden - Request not allowed",
            "404": "Not Found - Template or resource not found",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - ApiTemplate.io server error",
            "502": "Bad Gateway - ApiTemplate.io server temporarily unavailable",
            "503": "Service Unavailable - ApiTemplate.io server overloaded"
        }
    }
    
    # Enhanced operation definitions with ALL 25 operations and array_templates
    OPERATIONS = {
        "get_templates": {
            "method": "GET",
            "endpoint": "/v2/templates",
            "required_params": [],
            "optional_params": ["limit", "offset"],
            "query_parameters": ["limit", "offset"],
            "display_name": "Get Templates",
            "description": "Retrieve list of all templates in your account",
            "group": "Templates",
            "tags": ["templates", "list", "management"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "templates": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "created": {"type": "string"},
                                    "modified": {"type": "string"},
                                    "tags": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        },
                        "count": {"type": "integer"}
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header",
                "auth_description": "Requires ApiTemplate.io API key for authentication"
            },
            "examples": [
                {
                    "name": "List all templates",
                    "description": "Get all templates with pagination",
                    "input": {"limit": 50, "offset": 0}
                }
            ]
        },
        
        "get_template": {
            "method": "GET",
            "endpoint": "/v2/templates/{template_id}",
            "required_params": ["template_id"],
            "optional_params": [],
            "path_parameters": ["template_id"],
            "display_name": "Get Template",
            "description": "Retrieve specific template details and configuration",
            "group": "Templates",
            "tags": ["template", "details", "configuration"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "elements": {"type": "array"},
                        "properties": {"type": "object"},
                        "created": {"type": "string"},
                        "modified": {"type": "string"}
                    }
                }
            },
            
            "validation_rules": {
                "template_id": {
                    "pattern": "",
                    "message": "Template ID is required",
                    "pattern_type": "custom",
                    "min_length": 5,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Get template details",
                    "description": "Retrieve template configuration",
                    "input": {"template_id": "template_123abc"}
                }
            ]
        },
        
        "create_template": {
            "method": "POST",
            "endpoint": "/v2/templates",
            "required_params": ["template_name", "template_type"],
            "optional_params": ["template_data", "template_tags"],
            "body_parameters": ["template_name", "template_type", "template_data", "template_tags"],
            "display_name": "Create Template",
            "description": "Create a new template with specified configuration",
            "group": "Templates",
            "tags": ["template", "create", "design"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "created": {"type": "string"},
                        "url": {"type": "string"}
                    }
                }
            },
            
            "array_templates": {
                "template_tags": [
                    {"template": "business", "description": "Business-related templates"},
                    {"template": "social", "description": "Social media templates"},
                    {"template": "marketing", "description": "Marketing materials"},
                    {"template": "design", "description": "General design templates"}
                ]
            },
            
            "validation_rules": {
                "template_name": {
                    "pattern": "",
                    "message": "Template name is required and must be 1-100 characters",
                    "pattern_type": "custom",
                    "min_length": 1,
                    "max_length": 100,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Create image template",
                    "description": "Create a new image template",
                    "input": {
                        "template_name": "Business Card Template",
                        "template_type": "image",
                        "template_tags": ["business", "card", "professional"]
                    }
                }
            ]
        },
        
        "update_template": {
            "method": "PUT",
            "endpoint": "/v2/templates/{template_id}",
            "required_params": ["template_id"],
            "optional_params": ["template_name", "template_data", "template_tags"],
            "path_parameters": ["template_id"],
            "body_parameters": ["template_name", "template_data", "template_tags"],
            "display_name": "Update Template",
            "description": "Update existing template configuration",
            "group": "Templates",
            "tags": ["template", "update", "modify"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "template_tags": [
                    {"template": "updated", "description": "Recently updated templates"},
                    {"template": "modified", "description": "Modified templates"},
                    {"template": "version-2", "description": "Version 2 templates"}
                ]
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Update template name",
                    "description": "Change template name and tags",
                    "input": {
                        "template_id": "template_123abc",
                        "template_name": "Updated Business Card",
                        "template_tags": ["business", "updated"]
                    }
                }
            ]
        },
        
        "delete_template": {
            "method": "DELETE",
            "endpoint": "/v2/templates/{template_id}",
            "required_params": ["template_id"],
            "optional_params": [],
            "path_parameters": ["template_id"],
            "display_name": "Delete Template",
            "description": "Permanently delete a template",
            "group": "Templates",
            "tags": ["template", "delete", "remove"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Delete template",
                    "description": "Remove template permanently",
                    "input": {"template_id": "template_123abc"}
                }
            ]
        },
        
        "duplicate_template": {
            "method": "POST",
            "endpoint": "/v2/templates/{template_id}/duplicate",
            "required_params": ["template_id"],
            "optional_params": ["template_name"],
            "path_parameters": ["template_id"],
            "body_parameters": ["template_name"],
            "display_name": "Duplicate Template",
            "description": "Create a copy of an existing template",
            "group": "Templates",
            "tags": ["template", "duplicate", "copy"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Duplicate template",
                    "description": "Create copy with new name",
                    "input": {
                        "template_id": "template_123abc",
                        "template_name": "Copy of Business Card"
                    }
                }
            ]
        },
        
        "generate_image": {
            "method": "POST",
            "endpoint": "/v2/create-image",
            "required_params": ["template_id"],
            "optional_params": ["data", "properties", "format", "quality", "width", "height", "scale"],
            "body_parameters": ["template_id", "data", "properties", "format", "quality", "width", "height", "scale"],
            "display_name": "Generate Image",
            "description": "Generate an image from a template with custom data",
            "group": "Generation",
            "tags": ["image", "generate", "template", "merge"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "download_url": {"type": "string", "format": "uri"},
                        "download_url_png": {"type": "string", "format": "uri"},
                        "download_url_pdf": {"type": "string", "format": "uri"},
                        "transaction_id": {"type": "string"},
                        "status": {"type": "string"},
                        "properties": {"type": "object"}
                    }
                }
            },
            
            "array_templates": {
                "data": [
                    {"template": {"title": "Sample Title", "subtitle": "Sample Subtitle"}, "description": "Basic text data"},
                    {"template": {"name": "John Doe", "position": "CEO", "company": "ACME Inc"}, "description": "Business card data"},
                    {"template": {"product_name": "Product X", "price": "$99", "description": "Amazing product"}, "description": "Product information"}
                ]
            },
            
            "validation_rules": {
                "template_id": {
                    "pattern": "",
                    "message": "Template ID is required for image generation",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Generate business card",
                    "description": "Create personalized business card image",
                    "input": {
                        "template_id": "template_123abc",
                        "data": {"name": "John Doe", "title": "CEO", "email": "john@example.com"},
                        "format": "png",
                        "quality": 95
                    }
                }
            ]
        },
        
        "generate_image_async": {
            "method": "POST",
            "endpoint": "/v2/create-image-async",
            "required_params": ["template_id"],
            "optional_params": ["data", "properties", "callback_url", "webhook_secret"],
            "body_parameters": ["template_id", "data", "properties", "callback_url", "webhook_secret"],
            "display_name": "Generate Image (Async)",
            "description": "Generate an image asynchronously with callback notification",
            "group": "Generation",
            "tags": ["image", "async", "callback", "webhook"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "transaction_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["processing"]},
                        "callback_url": {"type": "string"}
                    }
                }
            },
            
            "array_templates": {
                "data": [
                    {"template": {"title": "Async Title", "content": "Processing..."}, "description": "Async processing data"},
                    {"template": {"batch_id": "batch_001", "items": 50}, "description": "Batch processing info"}
                ]
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Async image generation",
                    "description": "Generate image with webhook callback",
                    "input": {
                        "template_id": "template_123abc",
                        "data": {"name": "Jane Smith"},
                        "callback_url": "https://example.com/webhook"
                    }
                }
            ]
        },
        
        "generate_image_url": {
            "method": "POST", 
            "endpoint": "/v2/create-image-url",
            "required_params": ["template_id"],
            "optional_params": ["data", "properties", "expiration_time"],
            "body_parameters": ["template_id", "data", "properties", "expiration_time"],
            "display_name": "Generate Image URL",
            "description": "Generate an image and return temporary download URL",
            "group": "Generation",
            "tags": ["image", "url", "temporary", "download"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "data": [
                    {"template": {"logo_url": "https://example.com/logo.png", "text": "Sample"}, "description": "URL-based data"},
                    {"template": {"images": ["url1", "url2", "url3"], "layout": "grid"}, "description": "Multiple image URLs"}
                ]
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Generate with URL response",
                    "description": "Get temporary download URL for generated image",
                    "input": {
                        "template_id": "template_123abc",
                        "data": {"title": "Sample Image"},
                        "expiration_time": 3600
                    }
                }
            ]
        },
        
        "generate_images_batch": {
            "method": "POST",
            "endpoint": "/v2/create-images-batch",
            "required_params": ["template_id", "batch_data"],
            "optional_params": ["properties", "callback_url"],
            "body_parameters": ["template_id", "batch_data", "properties", "callback_url"],
            "display_name": "Generate Images (Batch)",
            "description": "Generate multiple images from template with array of data objects",
            "group": "Generation",
            "tags": ["batch", "images", "bulk", "multiple"],
            "rate_limit_cost": 5,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["processing", "queued"]},
                        "total_items": {"type": "integer"},
                        "estimated_completion": {"type": "string"}
                    }
                }
            },
            
            "array_templates": {
                "batch_data": [
                    {"template": {"name": "John Doe", "title": "CEO"}, "description": "First batch item"},
                    {"template": {"name": "Jane Smith", "title": "CTO"}, "description": "Second batch item"},
                    {"template": {"name": "Bob Johnson", "title": "CFO"}, "description": "Third batch item"}
                ]
            },
            
            "validation_rules": {
                "batch_data": {
                    "pattern": "",
                    "message": "Batch data must be an array with at least one item",
                    "pattern_type": "custom",
                    "min_items": 1,
                    "max_items": 100,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Batch business cards",
                    "description": "Generate multiple business cards in one request",
                    "input": {
                        "template_id": "template_123abc",
                        "batch_data": [
                            {"name": "John Doe", "email": "john@example.com"},
                            {"name": "Jane Smith", "email": "jane@example.com"}
                        ]
                    }
                }
            ]
        },
        
        "generate_pdf": {
            "method": "POST",
            "endpoint": "/v2/create-pdf",
            "required_params": ["template_id"],
            "optional_params": ["data", "properties", "page_size", "orientation"],
            "body_parameters": ["template_id", "data", "properties", "page_size", "orientation"],
            "display_name": "Generate PDF",
            "description": "Generate a PDF document from template with custom data",
            "group": "Generation",
            "tags": ["pdf", "document", "generate", "template"],
            "rate_limit_cost": 4,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "data": [
                    {"template": {"invoice_number": "INV-001", "items": [{"name": "Item 1", "price": 100}]}, "description": "Invoice data with items array"},
                    {"template": {"report_title": "Monthly Report", "sections": [{"title": "Section 1", "content": "Data"}]}, "description": "Report with sections"},
                    {"template": {"certificate_name": "John Doe", "achievements": ["Award 1", "Award 2"]}, "description": "Certificate with achievements list"}
                ]
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Generate invoice PDF",
                    "description": "Create PDF invoice with line items",
                    "input": {
                        "template_id": "template_pdf_123",
                        "data": {
                            "invoice_number": "INV-001",
                            "client_name": "ACME Corp",
                            "items": [
                                {"description": "Service A", "amount": "$500"},
                                {"description": "Service B", "amount": "$300"}
                            ]
                        },
                        "page_size": "A4"
                    }
                }
            ]
        },
        
        "generate_pdf_async": {
            "method": "POST",
            "endpoint": "/v2/create-pdf-async",
            "required_params": ["template_id"],
            "optional_params": ["data", "properties", "callback_url", "webhook_secret"],
            "body_parameters": ["template_id", "data", "properties", "callback_url", "webhook_secret"],
            "display_name": "Generate PDF (Async)",
            "description": "Generate a PDF asynchronously with callback notification",
            "group": "Generation",
            "tags": ["pdf", "async", "callback", "webhook"],
            "rate_limit_cost": 4,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "data": [
                    {"template": {"report_data": [{"month": "Jan", "sales": 1000}, {"month": "Feb", "sales": 1200}]}, "description": "Monthly sales report data"},
                    {"template": {"pages": [{"title": "Page 1", "content": "..."}, {"title": "Page 2", "content": "..."}]}, "description": "Multi-page document data"}
                ]
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Async PDF generation",
                    "description": "Generate large PDF with webhook notification",
                    "input": {
                        "template_id": "template_pdf_123",
                        "data": {"report_name": "Annual Report"},
                        "callback_url": "https://example.com/pdf-webhook"
                    }
                }
            ]
        },
        
        "generate_pdf_url": {
            "method": "POST",
            "endpoint": "/v2/create-pdf-url",
            "required_params": ["template_id"],
            "optional_params": ["data", "properties", "expiration_time"],
            "body_parameters": ["template_id", "data", "properties", "expiration_time"],
            "display_name": "Generate PDF URL", 
            "description": "Generate a PDF and return temporary download URL",
            "group": "Generation",
            "tags": ["pdf", "url", "temporary", "download"],
            "rate_limit_cost": 4,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "data": [
                    {"template": {"document_sections": [{"header": "Section 1"}, {"header": "Section 2"}]}, "description": "Structured document sections"},
                    {"template": {"table_data": [{"col1": "A", "col2": "B"}, {"col1": "C", "col2": "D"}]}, "description": "Tabular data for PDF"}
                ]
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "PDF with temporary URL",
                    "description": "Generate PDF and get download URL",
                    "input": {
                        "template_id": "template_pdf_123",
                        "data": {"document_title": "Sample Document"},
                        "expiration_time": 7200
                    }
                }
            ]
        },
        
        "generate_pdfs_batch": {
            "method": "POST",
            "endpoint": "/v2/create-pdfs-batch", 
            "required_params": ["template_id", "batch_data"],
            "optional_params": ["properties", "callback_url"],
            "body_parameters": ["template_id", "batch_data", "properties", "callback_url"],
            "display_name": "Generate PDFs (Batch)",
            "description": "Generate multiple PDFs from template with array of data objects",
            "group": "Generation",
            "tags": ["batch", "pdf", "bulk", "multiple"],
            "rate_limit_cost": 6,
            "cache_ttl": 0,
            "response_type": "object",
            
            "array_templates": {
                "batch_data": [
                    {"template": {"customer_name": "Customer A", "order_items": [{"item": "Product 1", "qty": 2}]}, "description": "First customer order"},
                    {"template": {"customer_name": "Customer B", "order_items": [{"item": "Product 2", "qty": 1}]}, "description": "Second customer order"},
                    {"template": {"customer_name": "Customer C", "order_items": [{"item": "Product 3", "qty": 3}]}, "description": "Third customer order"}
                ]
            },
            
            "validation_rules": {
                "batch_data": {
                    "pattern": "",
                    "message": "Batch data must be an array with at least one PDF data object",
                    "pattern_type": "custom",
                    "min_items": 1,
                    "max_items": 50,
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Batch invoices",
                    "description": "Generate multiple invoice PDFs",
                    "input": {
                        "template_id": "template_invoice",
                        "batch_data": [
                            {"invoice_number": "INV-001", "amount": "$500"},
                            {"invoice_number": "INV-002", "amount": "$750"}
                        ]
                    }
                }
            ]
        },
        
        "get_job_status": {
            "method": "GET",
            "endpoint": "/v2/jobs/{job_id}",
            "required_params": ["job_id"],
            "optional_params": [],
            "path_parameters": ["job_id"],
            "display_name": "Get Job Status",
            "description": "Check the status of an asynchronous job",
            "group": "Jobs",
            "tags": ["job", "status", "async", "monitoring"],
            "rate_limit_cost": 1,
            "cache_ttl": 30,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["processing", "completed", "failed", "queued"]},
                        "progress": {"type": "number", "minimum": 0, "maximum": 100},
                        "total_items": {"type": "integer"},
                        "completed_items": {"type": "integer"},
                        "failed_items": {"type": "integer"},
                        "estimated_completion": {"type": "string"},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"}
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Check job status",
                    "description": "Monitor async generation job progress",
                    "input": {"job_id": "job_abc123"}
                }
            ]
        },
        
        "get_job_result": {
            "method": "GET",
            "endpoint": "/v2/jobs/{job_id}/result",
            "required_params": ["job_id"],
            "optional_params": [],
            "path_parameters": ["job_id"],
            "display_name": "Get Job Result",
            "description": "Retrieve the results of a completed job",
            "group": "Jobs",
            "tags": ["job", "result", "download", "completed"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object", 
                    "properties": {
                        "job_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["completed"]},
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "download_url": {"type": "string"},
                                    "transaction_id": {"type": "string"},
                                    "status": {"type": "string"}
                                }
                            }
                        },
                        "total_generated": {"type": "integer"},
                        "completion_time": {"type": "string"}
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Download job results",
                    "description": "Get all generated files from completed job",
                    "input": {"job_id": "job_abc123"}
                }
            ]
        },
        
        "list_jobs": {
            "method": "GET",
            "endpoint": "/v2/jobs",
            "required_params": [],
            "optional_params": ["limit", "offset", "status"],
            "query_parameters": ["limit", "offset", "status"],
            "display_name": "List Jobs",
            "description": "Retrieve list of all jobs with optional filtering",
            "group": "Jobs",
            "tags": ["jobs", "list", "history"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "jobs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "job_id": {"type": "string"},
                                    "status": {"type": "string"},
                                    "created_at": {"type": "string"},
                                    "template_id": {"type": "string"},
                                    "total_items": {"type": "integer"}
                                }
                            }
                        },
                        "total": {"type": "integer"}
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "List recent jobs",
                    "description": "Get latest 10 jobs with status filter",
                    "input": {"limit": 10, "status": "completed"}
                }
            ]
        },
        
        "cancel_job": {
            "method": "DELETE",
            "endpoint": "/v2/jobs/{job_id}",
            "required_params": ["job_id"],
            "optional_params": [],
            "path_parameters": ["job_id"],
            "display_name": "Cancel Job",
            "description": "Cancel a running or queued job",
            "group": "Jobs",
            "tags": ["job", "cancel", "stop"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Cancel running job",
                    "description": "Stop a job that's currently processing",
                    "input": {"job_id": "job_abc123"}
                }
            ]
        },
        
        "get_account_info": {
            "method": "GET",
            "endpoint": "/v2/account",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Account Info",
            "description": "Retrieve account information and settings",
            "group": "Account",
            "tags": ["account", "info", "profile"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "account_id": {"type": "string"},
                        "email": {"type": "string"},
                        "plan": {"type": "string"},
                        "credits_remaining": {"type": "integer"},
                        "monthly_limit": {"type": "integer"},
                        "usage_current_month": {"type": "integer"}
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Get account details",
                    "description": "Retrieve current account status",
                    "input": {}
                }
            ]
        },
        
        "get_usage_stats": {
            "method": "GET",
            "endpoint": "/v2/account/usage",
            "required_params": [],
            "optional_params": ["month", "year"],
            "query_parameters": ["month", "year"],
            "display_name": "Get Usage Stats",
            "description": "Retrieve detailed usage statistics",
            "group": "Account",
            "tags": ["usage", "statistics", "analytics"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "current_month": {
                            "type": "object",
                            "properties": {
                                "images_generated": {"type": "integer"},
                                "pdfs_generated": {"type": "integer"},
                                "total_requests": {"type": "integer"},
                                "credits_used": {"type": "integer"}
                            }
                        },
                        "daily_breakdown": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "date": {"type": "string"},
                                    "requests": {"type": "integer"},
                                    "credits": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Current month usage",
                    "description": "Get usage stats for current month",
                    "input": {}
                }
            ]
        },
        
        "get_credits": {
            "method": "GET",
            "endpoint": "/v2/account/credits",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Credits",
            "description": "Retrieve current credit balance and history",
            "group": "Account",
            "tags": ["credits", "balance", "billing"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "current_balance": {"type": "integer"},
                        "total_purchased": {"type": "integer"},
                        "total_used": {"type": "integer"},
                        "last_purchase": {"type": "string"},
                        "next_refill": {"type": "string"}
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Check credit balance",
                    "description": "Get current available credits",
                    "input": {}
                }
            ]
        },
        
        "upload_image": {
            "method": "POST",
            "endpoint": "/v2/uploads/image",
            "required_params": ["file_name"],
            "optional_params": ["file_content", "file_url", "file_type"],
            "body_parameters": ["file_name", "file_content", "file_url", "file_type"],
            "display_name": "Upload Image",
            "description": "Upload an image file for use in templates",
            "group": "Upload",
            "tags": ["upload", "image", "asset", "file"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "upload_id": {"type": "string"},
                        "file_name": {"type": "string"},
                        "file_url": {"type": "string"},
                        "file_size": {"type": "integer"},
                        "mime_type": {"type": "string"},
                        "uploaded_at": {"type": "string"}
                    }
                }
            },
            
            "parameter_dependencies": [
                {
                    "when_field": "file_content",
                    "when_value": "",
                    "then_require": ["file_url"],
                    "then_optional": [],
                    "require_one_of": ["file_content", "file_url"],
                    "mutually_exclusive": ["file_content", "file_url"]
                }
            ],
            
            "validation_rules": {
                "file_name": {
                    "pattern": "\\.(jpg|jpeg|png|gif|webp)$",
                    "message": "File name must have a valid image extension",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Upload image from URL",
                    "description": "Upload image from external URL",
                    "input": {
                        "file_name": "logo.png",
                        "file_url": "https://example.com/logo.png",
                        "file_type": "image/png"
                    }
                }
            ]
        },
        
        "upload_file": {
            "method": "POST",
            "endpoint": "/v2/uploads/file",
            "required_params": ["file_name"],
            "optional_params": ["file_content", "file_url", "file_type"],
            "body_parameters": ["file_name", "file_content", "file_url", "file_type"],
            "display_name": "Upload File",
            "description": "Upload any file type for use in templates",
            "group": "Upload",
            "tags": ["upload", "file", "asset", "document"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "parameter_dependencies": [
                {
                    "when_field": "file_content",
                    "when_value": "",
                    "then_require": ["file_url"],
                    "then_optional": [],
                    "require_one_of": ["file_content", "file_url"],
                    "mutually_exclusive": ["file_content", "file_url"]
                }
            ],
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Upload PDF file",
                    "description": "Upload PDF document from base64 content",
                    "input": {
                        "file_name": "document.pdf",
                        "file_content": "base64_encoded_content_here",
                        "file_type": "application/pdf"
                    }
                }
            ]
        },
        
        "get_uploads": {
            "method": "GET",
            "endpoint": "/v2/uploads",
            "required_params": [],
            "optional_params": ["limit", "offset", "type"],
            "query_parameters": ["limit", "offset", "type"],
            "display_name": "Get Uploads",
            "description": "Retrieve list of uploaded files",
            "group": "Upload",
            "tags": ["uploads", "list", "files", "assets"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "uploads": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "upload_id": {"type": "string"},
                                    "file_name": {"type": "string"},
                                    "file_url": {"type": "string"},
                                    "file_size": {"type": "integer"},
                                    "mime_type": {"type": "string"},
                                    "uploaded_at": {"type": "string"}
                                }
                            }
                        },
                        "total": {"type": "integer"}
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "List uploaded images",
                    "description": "Get all uploaded image files",
                    "input": {"type": "image", "limit": 20}
                }
            ]
        },
        
        "delete_upload": {
            "method": "DELETE",
            "endpoint": "/v2/uploads/{upload_id}",
            "required_params": ["upload_id"],
            "optional_params": [],
            "path_parameters": ["upload_id"],
            "display_name": "Delete Upload",
            "description": "Delete an uploaded file permanently",
            "group": "Upload",
            "tags": ["upload", "delete", "remove", "cleanup"],
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            
            "validation_rules": {
                "upload_id": {
                    "pattern": "",
                    "message": "Upload ID is required for deletion",
                    "pattern_type": "custom",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["APITEMPLATE_API_KEY"],
                "required_params": ["api_key"],
                "auth_type": "api_key_header"
            },
            "examples": [
                {
                    "name": "Delete uploaded file",
                    "description": "Remove file from upload storage",
                    "input": {"upload_id": "upload_abc123"}
                }
            ]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced ApiTemplate.io node with embedded configuration."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Initialize the Enhanced UniversalRequestNode with embedded config
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.info("Enhanced ApiTemplateIoNode initialized with all 25 operations and advanced features")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"ApiTemplateIoNode executing operation: {node_data.get('params', {}).get('operation')}")
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
__all__ = ["ApiTemplateIoNode"]