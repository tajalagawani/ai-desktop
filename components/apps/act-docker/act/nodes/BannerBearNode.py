#!/usr/bin/env python3
"""
BannerBear Node - Enhanced with ALL 13 advanced features for automated media generation
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

class BannerBearNode(BaseNode):
    """
    Enhanced BannerBear node with ALL 13 advanced features for automated media generation.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "bannerbear",
            "display_name": "BannerBear",
            "description": "Comprehensive BannerBear API integration for automated image and video generation, template management, and bulk media creation",
            "category": "media",
            "vendor": "bannerbear", 
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["media", "image", "video", "template", "generation", "automation", "design", "banner", "bulk"],
            "documentation_url": "https://developers.bannerbear.com/",
            "icon": "https://www.bannerbear.com/favicon.ico",
            "color": "#FF6B35",
            "created_at": "2025-08-26T00:00:00Z",
            "updated_at": "2025-08-26T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.bannerbear.com/v2",
            "authentication": {
                "type": "bearer_token",
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
                "base_delay": 2.0,
                "max_delay": 120.0,
                "jitter": True,
                "retriable_codes": [429, 500, 502, 503, 504],
                "retriable_exceptions": ["aiohttp.ClientTimeout", "aiohttp.ClientConnectorError"],
                "timeout_ms": 60000
            }
        },
        
        # 5. Rate limiting configuration
        "rate_limiting": {
            "requests_per_minute": 300,
            "requests_per_second": 5.0,
            "burst_size": 10,
            "cost_per_request": 0.01,
            "quota_type": "requests",
            "concurrent_requests": 5
        },
        
        # Enhanced pricing information
        "pricing": {
            "cost_per_image": 0.05,
            "cost_per_video": 0.25,
            "cost_per_request": 0.01,
            "billing_unit": "credits",
            "free_tier_limit": 50
        },
        
        # 11. Performance monitoring
        "monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "media_generated", "template_usage"],
            "alerts": {
                "error_rate_threshold": 0.08,
                "response_time_threshold": 10000,
                "queue_depth_threshold": 50
            },
            "performance_tracking": {
                "generation_time": True,
                "file_size_metrics": True,
                "quality_scores": True
            }
        },
        
        # 12. Intelligent caching strategy
        "caching": {
            "enabled": True,
            "cache_key_template": "{operation}:{template_uid}:{hash}",
            "ttl_seconds": 1800,
            "cache_conditions": {
                "only_for": ["get_template", "list_templates", "list_projects"],
                "exclude_params": ["timestamp", "webhook_url", "synchronous"]
            },
            "cache_strategy": {
                "template_cache_ttl": 3600,
                "media_cache_ttl": 300,
                "project_cache_ttl": 7200
            }
        },
        
        # 10. Testing configuration
        "testing": {
            "sandbox_mode": True,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/account",
            "test_template_id": "test_template_123",
            "mock_generation": True
        },
        
        # 13. Documentation links
        "documentation": {
            "api_docs_url": "https://developers.bannerbear.com/",
            "setup_guide": "https://www.bannerbear.com/help/articles/123-how-do-i-create-an-image-via-api/",
            "troubleshooting": "https://www.bannerbear.com/help/",
            "changelog": "https://developers.bannerbear.com/changelog",
            "template_editor_guide": "https://www.bannerbear.com/help/template-editor",
            "webhook_guide": "https://developers.bannerbear.com/webhooks"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "BannerBear API key (Project API Key or Master API Key)",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^bb_[a-zA-Z0-9_]+$",
                    "message": "API key must start with 'bb_'",
                    "minLength": 40,
                    "maxLength": 80
                }
            },
            "operation": {
                "type": "string",
                "description": "The BannerBear operation to perform",
                "required": True,
                "group": "Operation",
                "enum": ["create_image", "create_video", "create_collection", "get_image", "get_video", "list_templates", "get_template", "create_template_duplicate", "list_projects", "get_account"]
            },
            "template_uid": {
                "type": "string",
                "description": "Unique identifier of the template to use",
                "required": False,
                "group": "Template",
                "examples": ["A89Znq5X4lBXbdRPej", "B12Abc3D4eFgHiJkLm"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Template UID must be alphanumeric with hyphens/underscores",
                    "minLength": 10,
                    "maxLength": 50
                }
            },
            "modifications": {
                "type": "array",
                "description": "Array of template modifications (text, images, colors)",
                "required": False,
                "group": "Content",
                "examples": [[{"name": "title", "text": "Hello World"}, {"name": "image", "image_url": "https://example.com/image.jpg"}]],
                "validation": {
                    "minItems": 0,
                    "maxItems": 50,
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "text": {"type": "string"},
                            "image_url": {"type": "string", "format": "uri"},
                            "color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"}
                        }
                    }
                }
            },
            "webhook_url": {
                "type": "string",
                "description": "URL to receive webhook notifications when generation completes",
                "required": False,
                "group": "Webhooks",
                "examples": ["https://your-app.com/webhook/bannerbear"],
                "validation": {
                    "format": "uri",
                    "pattern": "^https?://.*$",
                    "message": "Webhook URL must be a valid HTTP/HTTPS URL"
                }
            },
            "synchronous": {
                "type": "boolean",
                "description": "Wait for generation to complete before returning response",
                "required": False,
                "default": False,
                "group": "Generation",
                "examples": [True, False]
            },
            "transparent": {
                "type": "boolean", 
                "description": "Generate image with transparent background",
                "required": False,
                "default": False,
                "group": "Image",
                "examples": [True, False]
            },
            "jpg": {
                "type": "boolean",
                "description": "Generate image in JPG format instead of PNG",
                "required": False,
                "default": False,
                "group": "Image",
                "examples": [True, False]
            },
            "width": {
                "type": "integer",
                "description": "Custom width for generated media",
                "required": False,
                "group": "Dimensions",
                "validation": {
                    "minimum": 100,
                    "maximum": 4000
                },
                "examples": [800, 1200, 1920]
            },
            "height": {
                "type": "integer",
                "description": "Custom height for generated media",
                "required": False,
                "group": "Dimensions",
                "validation": {
                    "minimum": 100,
                    "maximum": 4000
                },
                "examples": [600, 800, 1080]
            },
            "frames": {
                "type": "array",
                "description": "Array of frames for video generation",
                "required": False,
                "group": "Video",
                "examples": [[{"duration": 3000, "template_uid": "A89Znq5X4l", "modifications": []}]],
                "validation": {
                    "minItems": 1,
                    "maxItems": 100,
                    "items": {
                        "type": "object",
                        "properties": {
                            "duration": {"type": "integer", "minimum": 500, "maximum": 10000},
                            "template_uid": {"type": "string"},
                            "modifications": {"type": "array"}
                        }
                    }
                }
            },
            "input_media_url": {
                "type": "string",
                "description": "URL of input media file for processing",
                "required": False,
                "group": "Media",
                "validation": {
                    "format": "uri",
                    "pattern": "^https?://.*\\.(jpg|jpeg|png|gif|mp4|mov|avi)$",
                    "message": "Must be a valid media file URL"
                }
            },
            "metadata": {
                "type": "object",
                "description": "Custom metadata to attach to generated media",
                "required": False,
                "group": "Metadata",
                "examples": [{"campaign": "summer2024", "client": "acme_corp"}]
            },
            "template_tags": {
                "type": "array",
                "description": "Tags to filter templates",
                "required": False,
                "group": "Template",
                "examples": [["social", "instagram"], ["banner", "web"]],
                "validation": {
                    "items": {"type": "string"}
                }
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful BannerBear API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from BannerBear API"},
                    "usage": {"type": "object", "description": "Credit usage information"},
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
                    "error_code": {"type": "string", "description": "BannerBear error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "create_image": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"]
            },
            "create_video": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"]
            },
            "create_collection": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"]
            },
            "get_image": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"]
            },
            "get_video": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"]
            },
            "list_templates": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"]
            },
            "get_template": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"]
            },
            "create_template_duplicate": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"]
            },
            "list_projects": {
                "required_env_keys": ["BANNERBEAR_MASTER_API_KEY"],
                "optional_env_keys": []
            },
            "get_account": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"]
            }
        },
        
        # 7. Error handling - Error codes specific to BannerBear
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid API key or insufficient permissions",
            "402": "Payment Required - Insufficient credits",
            "403": "Forbidden - Request not allowed or rate limit exceeded",
            "404": "Not Found - Template, project, or resource not found",
            "422": "Unprocessable Entity - Invalid template modifications or data",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - BannerBear server error",
            "502": "Bad Gateway - BannerBear server temporarily unavailable",
            "503": "Service Unavailable - BannerBear server overloaded or maintenance"
        }
    }
    
    # Enhanced operation definitions with ALL 13 features
    OPERATIONS = {
        "create_image": {
            "method": "POST",
            "endpoint": "/images",
            "required_params": ["template_uid"],
            "optional_params": ["modifications", "webhook_url", "synchronous", "transparent", "jpg", "width", "height", "metadata"],
            "body_parameters": ["template_uid", "modifications", "webhook_url", "synchronous", "transparent", "jpg", "width", "height", "metadata"],
            "display_name": "Create Image",
            "description": "Generate a custom image using a BannerBear template with dynamic content modifications",
            "group": "Image Generation",
            "tags": ["image", "generation", "template", "media", "design"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            # 1. Operation-specific output schema
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "uid": {"type": "string", "description": "Unique image identifier"},
                        "template_uid": {"type": "string", "description": "Template used for generation"},
                        "status": {"type": "string", "enum": ["pending", "completed", "failed"]},
                        "image_url": {"type": "string", "format": "uri", "description": "URL of generated image"},
                        "image_url_png": {"type": "string", "format": "uri", "description": "PNG version URL"},
                        "image_url_jpg": {"type": "string", "format": "uri", "description": "JPG version URL"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "width": {"type": "integer", "description": "Image width in pixels"},
                        "height": {"type": "integer", "description": "Image height in pixels"},
                        "file_size": {"type": "integer", "description": "File size in bytes"},
                        "webhook_url": {"type": "string", "format": "uri"},
                        "metadata": {"type": "object", "description": "Custom metadata"}
                    }
                },
                "error": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Error message"},
                        "errors": {"type": "array", "items": {"type": "string"}},
                        "code": {"type": "integer", "description": "HTTP error code"}
                    }
                },
                "status_codes": {
                    200: "Image created successfully",
                    400: "Invalid request parameters",
                    401: "Invalid API key",
                    402: "Insufficient credits",
                    404: "Template not found",
                    422: "Invalid modifications",
                    429: "Rate limit exceeded"
                }
            },
            
            # 2. Array templates for complex inputs
            "array_templates": {
                "modifications": [
                    {"template": {"name": "title", "text": "Your Title Here"}, "description": "Text layer modification"},
                    {"template": {"name": "subtitle", "text": "Your subtitle text"}, "description": "Secondary text layer"},
                    {"template": {"name": "logo", "image_url": "https://example.com/logo.png"}, "description": "Image layer replacement"},
                    {"template": {"name": "background", "color": "#FF5733"}, "description": "Color layer modification"},
                    {"template": {"name": "avatar", "image_url": "https://example.com/avatar.jpg", "resize_strategy": "cover"}, "description": "Avatar image with resize strategy"}
                ]
            },
            
            # 3. Parameter dependencies & conditional fields
            "parameter_dependencies": [
                {
                    "when_field": "synchronous",
                    "when_value": True,
                    "then_require": [],
                    "then_optional": ["webhook_url"],
                    "require_one_of": [],
                    "mutually_exclusive": ["webhook_url"]
                },
                {
                    "when_field": "jpg",
                    "when_value": True,
                    "then_require": [],
                    "then_optional": [],
                    "require_one_of": [],
                    "mutually_exclusive": ["transparent"]
                }
            ],
            
            # 4. Advanced validation rules
            "validation_rules": {
                "template_uid": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Template UID must be alphanumeric with hyphens/underscores only",
                    "pattern_type": "regex",
                    "min_length": 10,
                    "max_length": 50,
                    "required": True
                },
                "modifications": {
                    "pattern": "",
                    "message": "Each modification must have a 'name' field",
                    "pattern_type": "custom",
                    "min_items": 0,
                    "max_items": 50,
                    "required": False
                },
                "webhook_url": {
                    "pattern": "^https?://.*$",
                    "message": "Webhook URL must be a valid HTTP/HTTPS URL",
                    "pattern_type": "regex",
                    "required": False
                }
            },
            
            # 5. Rate limiting (inherited from CONFIG)
            "rate_limiting": {
                "requests_per_minute": 30,
                "cost_multiplier": 2.0,
                "burst_allowance": 5
            },
            
            # 6. Pagination (not applicable for single image creation)
            "pagination": None,
            
            # 7. Error handling
            "error_handling": {
                "retry_on_codes": [429, 500, 502, 503],
                "max_retries": 3,
                "backoff_strategy": "exponential",
                "timeout_handling": "graceful",
                "custom_error_messages": {
                    402: "Insufficient credits to generate image. Please add credits to your account.",
                    404: "Template not found. Please check the template_uid.",
                    422: "Invalid template modifications. Please check your modification parameters."
                }
            },
            
            # 8. Field mapping & transformation
            "field_mapping": {
                "input_transforms": {
                    "template_uid": "validate_template_uid",
                    "modifications": "validate_modifications_array"
                },
                "output_transforms": {
                    "created_at": "format_timestamp",
                    "file_size": "format_file_size"
                },
                "field_aliases": {
                    "template_id": "template_uid",
                    "mods": "modifications"
                }
            },
            
            # 9. Webhook support
            "webhook_support": {
                "enabled": True,
                "events": ["image.completed", "image.failed"],
                "required_fields": ["webhook_url"],
                "payload_format": "json",
                "authentication": "none",
                "retry_policy": {
                    "max_attempts": 5,
                    "backoff": "exponential"
                }
            },
            
            "auth": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires BannerBear API key for image generation"
            },
            "examples": [
                {
                    "name": "Simple text image",
                    "description": "Generate image with text modification",
                    "input": {
                        "template_uid": "A89Znq5X4lBXbdRPej",
                        "modifications": [
                            {"name": "title", "text": "Hello World!"}
                        ]
                    }
                },
                {
                    "name": "Complex image with multiple layers",
                    "description": "Generate image with text, image, and color modifications",
                    "input": {
                        "template_uid": "B12Abc3D4eFgHiJkLm",
                        "modifications": [
                            {"name": "title", "text": "Summer Sale"},
                            {"name": "subtitle", "text": "50% Off Everything"},
                            {"name": "logo", "image_url": "https://example.com/logo.png"},
                            {"name": "background", "color": "#FF6B35"}
                        ],
                        "synchronous": True,
                        "transparent": False
                    }
                },
                {
                    "name": "Webhook-enabled generation",
                    "description": "Generate image with webhook notification",
                    "input": {
                        "template_uid": "C34DeF5G6hIjKlMnOp",
                        "modifications": [
                            {"name": "product_name", "text": "New Product Launch"}
                        ],
                        "webhook_url": "https://your-app.com/webhook/bannerbear",
                        "metadata": {"campaign": "product_launch", "version": "v1"}
                    }
                }
            ]
        },
        "create_video": {
            "method": "POST",
            "endpoint": "/videos",
            "required_params": ["frames"],
            "optional_params": ["webhook_url", "synchronous", "width", "height", "metadata"],
            "body_parameters": ["frames", "webhook_url", "synchronous", "width", "height", "metadata"],
            "display_name": "Create Video",
            "description": "Generate a custom video using multiple template frames with dynamic content",
            "group": "Video Generation",
            "tags": ["video", "generation", "template", "media", "animation"],
            "rate_limit_cost": 5,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "uid": {"type": "string", "description": "Unique video identifier"},
                        "status": {"type": "string", "enum": ["pending", "completed", "failed"]},
                        "video_url": {"type": "string", "format": "uri", "description": "URL of generated video"},
                        "thumbnail_url": {"type": "string", "format": "uri", "description": "Video thumbnail URL"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "duration": {"type": "number", "description": "Video duration in seconds"},
                        "width": {"type": "integer", "description": "Video width in pixels"},
                        "height": {"type": "integer", "description": "Video height in pixels"},
                        "file_size": {"type": "integer", "description": "File size in bytes"},
                        "frame_count": {"type": "integer", "description": "Number of frames"},
                        "webhook_url": {"type": "string", "format": "uri"},
                        "metadata": {"type": "object", "description": "Custom metadata"}
                    }
                }
            },
            
            "array_templates": {
                "frames": [
                    {
                        "template": {
                            "duration": 3000,
                            "template_uid": "A89Znq5X4l",
                            "modifications": [
                                {"name": "title", "text": "Frame 1 Title"}
                            ]
                        },
                        "description": "Video frame with 3-second duration"
                    },
                    {
                        "template": {
                            "duration": 2000,
                            "template_uid": "B12Abc3D4e",
                            "modifications": [
                                {"name": "title", "text": "Frame 2 Title"},
                                {"name": "image", "image_url": "https://example.com/frame2.jpg"}
                            ]
                        },
                        "description": "Second frame with image and text"
                    }
                ]
            },
            
            "validation_rules": {
                "frames": {
                    "pattern": "",
                    "message": "At least one frame is required for video generation",
                    "pattern_type": "custom",
                    "min_items": 1,
                    "max_items": 100,
                    "required": True
                }
            },
            
            "rate_limiting": {
                "requests_per_minute": 10,
                "cost_multiplier": 5.0,
                "burst_allowance": 2
            },
            
            "error_handling": {
                "retry_on_codes": [429, 500, 502, 503],
                "max_retries": 2,
                "backoff_strategy": "linear",
                "timeout_handling": "extended",
                "custom_error_messages": {
                    402: "Insufficient credits for video generation. Video costs more credits than images.",
                    422: "Invalid video frames. Check duration and template_uid for each frame."
                }
            },
            
            "webhook_support": {
                "enabled": True,
                "events": ["video.completed", "video.failed", "video.processing"],
                "required_fields": ["webhook_url"],
                "payload_format": "json",
                "authentication": "none"
            },
            
            "auth": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires BannerBear API key for video generation"
            },
            "examples": [
                {
                    "name": "Simple 2-frame video",
                    "description": "Create a video with two frames",
                    "input": {
                        "frames": [
                            {
                                "duration": 3000,
                                "template_uid": "A89Znq5X4l",
                                "modifications": [{"name": "title", "text": "Welcome"}]
                            },
                            {
                                "duration": 2000,
                                "template_uid": "B12Abc3D4e",
                                "modifications": [{"name": "title", "text": "Thank You"}]
                            }
                        ],
                        "synchronous": False
                    }
                }
            ]
        },
        "create_collection": {
            "method": "POST",
            "endpoint": "/collections",
            "required_params": ["templates"],
            "optional_params": ["synchronous", "webhook_url", "metadata"],
            "body_parameters": ["templates", "synchronous", "webhook_url", "metadata"],
            "display_name": "Create Collection",
            "description": "Generate multiple images at once using different templates and modifications",
            "group": "Bulk Generation",
            "tags": ["collection", "bulk", "batch", "multiple", "templates"],
            "rate_limit_cost": 3,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "uid": {"type": "string", "description": "Collection identifier"},
                        "status": {"type": "string", "enum": ["pending", "completed", "failed"]},
                        "images": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "uid": {"type": "string"},
                                    "template_uid": {"type": "string"},
                                    "image_url": {"type": "string", "format": "uri"},
                                    "status": {"type": "string"}
                                }
                            }
                        },
                        "created_at": {"type": "string", "format": "date-time"},
                        "total_images": {"type": "integer"},
                        "completed_images": {"type": "integer"}
                    }
                }
            },
            
            "array_templates": {
                "templates": [
                    {
                        "template": {
                            "template_uid": "A89Znq5X4l",
                            "modifications": [
                                {"name": "title", "text": "Product 1"}
                            ]
                        },
                        "description": "Template configuration for collection item"
                    }
                ]
            },
            
            "validation_rules": {
                "templates": {
                    "pattern": "",
                    "message": "At least one template is required for collection",
                    "pattern_type": "custom",
                    "min_items": 1,
                    "max_items": 50,
                    "required": True
                }
            },
            
            "rate_limiting": {
                "requests_per_minute": 20,
                "cost_multiplier": 3.0,
                "burst_allowance": 3
            },
            
            "pagination": {
                "supported": True,
                "default_limit": 20,
                "max_limit": 100,
                "offset_param": "offset",
                "limit_param": "limit"
            },
            
            "webhook_support": {
                "enabled": True,
                "events": ["collection.completed", "collection.failed"],
                "required_fields": ["webhook_url"],
                "payload_format": "json"
            },
            
            "auth": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires BannerBear API key for bulk generation"
            },
            "examples": [
                {
                    "name": "Product collection",
                    "description": "Generate multiple product images",
                    "input": {
                        "templates": [
                            {
                                "template_uid": "A89Znq5X4l",
                                "modifications": [{"name": "product_name", "text": "Product A"}]
                            },
                            {
                                "template_uid": "A89Znq5X4l",
                                "modifications": [{"name": "product_name", "text": "Product B"}]
                            }
                        ]
                    }
                }
            ]
        },
        "get_image": {
            "method": "GET",
            "endpoint": "/images/{uid}",
            "required_params": ["uid"],
            "optional_params": [],
            "url_parameters": ["uid"],
            "display_name": "Get Image",
            "description": "Retrieve details and status of a generated image",
            "group": "Image Management",
            "tags": ["image", "status", "retrieve", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "uid": {"type": "string"},
                        "template_uid": {"type": "string"},
                        "status": {"type": "string", "enum": ["pending", "completed", "failed"]},
                        "image_url": {"type": "string", "format": "uri"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "width": {"type": "integer"},
                        "height": {"type": "integer"},
                        "modifications": {"type": "array"}
                    }
                }
            },
            
            "validation_rules": {
                "uid": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Image UID must be alphanumeric",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires BannerBear API key to retrieve image details"
            },
            "examples": [
                {
                    "name": "Get image status",
                    "description": "Check the status of a generated image",
                    "input": {
                        "uid": "XyZ123AbC456DeF789"
                    }
                }
            ]
        },
        "get_video": {
            "method": "GET",
            "endpoint": "/videos/{uid}",
            "required_params": ["uid"],
            "optional_params": [],
            "url_parameters": ["uid"],
            "display_name": "Get Video",
            "description": "Retrieve details and status of a generated video",
            "group": "Video Management", 
            "tags": ["video", "status", "retrieve", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "uid": {"type": "string"},
                        "status": {"type": "string", "enum": ["pending", "completed", "failed"]},
                        "video_url": {"type": "string", "format": "uri"},
                        "thumbnail_url": {"type": "string", "format": "uri"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "duration": {"type": "number"},
                        "frame_count": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "uid": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Video UID must be alphanumeric",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires BannerBear API key to retrieve video details"
            },
            "examples": [
                {
                    "name": "Get video status",
                    "description": "Check the status of a generated video",
                    "input": {
                        "uid": "VdO789XyZ123AbC456"
                    }
                }
            ]
        },
        "list_templates": {
            "method": "GET",
            "endpoint": "/templates",
            "required_params": [],
            "optional_params": ["template_tags", "page", "limit"],
            "query_parameters": ["template_tags", "page", "limit"],
            "display_name": "List Templates",
            "description": "Retrieve list of available templates in the project",
            "group": "Template Management",
            "tags": ["templates", "list", "browse", "catalog"],
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
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
                                    "uid": {"type": "string"},
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "tags": {"type": "array", "items": {"type": "string"}},
                                    "width": {"type": "integer"},
                                    "height": {"type": "integer"},
                                    "available_modifications": {"type": "array"},
                                    "preview_url": {"type": "string", "format": "uri"}
                                }
                            }
                        },
                        "pagination": {
                            "type": "object",
                            "properties": {
                                "current_page": {"type": "integer"},
                                "per_page": {"type": "integer"},
                                "total_pages": {"type": "integer"},
                                "total_count": {"type": "integer"}
                            }
                        }
                    }
                }
            },
            
            "pagination": {
                "supported": True,
                "default_limit": 25,
                "max_limit": 100,
                "page_param": "page",
                "limit_param": "limit"
            },
            
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {
                    "templates": "format_template_list"
                },
                "field_aliases": {}
            },
            
            "auth": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires BannerBear API key to list templates"
            },
            "examples": [
                {
                    "name": "List all templates",
                    "description": "Get all available templates",
                    "input": {}
                },
                {
                    "name": "Filter templates by tags",
                    "description": "Get templates with specific tags",
                    "input": {
                        "template_tags": ["social", "instagram"]
                    }
                }
            ]
        },
        "get_template": {
            "method": "GET",
            "endpoint": "/templates/{uid}",
            "required_params": ["uid"],
            "optional_params": [],
            "url_parameters": ["uid"],
            "display_name": "Get Template",
            "description": "Retrieve detailed information about a specific template",
            "group": "Template Management",
            "tags": ["template", "details", "inspect", "modifications"],
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "uid": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "width": {"type": "integer"},
                        "height": {"type": "integer"},
                        "available_modifications": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string", "enum": ["text", "image", "color"]},
                                    "required": {"type": "boolean"}
                                }
                            }
                        },
                        "preview_url": {"type": "string", "format": "uri"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            
            "validation_rules": {
                "uid": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Template UID must be alphanumeric",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires BannerBear API key to get template details"
            },
            "examples": [
                {
                    "name": "Get template details",
                    "description": "Retrieve full details of a template",
                    "input": {
                        "uid": "A89Znq5X4lBXbdRPej"
                    }
                }
            ]
        },
        "create_template_duplicate": {
            "method": "POST",
            "endpoint": "/templates/{uid}/duplicate",
            "required_params": ["uid"],
            "optional_params": ["name", "metadata"],
            "url_parameters": ["uid"],
            "body_parameters": ["name", "metadata"],
            "display_name": "Duplicate Template",
            "description": "Create a duplicate of an existing template",
            "group": "Template Management",
            "tags": ["template", "duplicate", "copy", "create"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "uid": {"type": "string", "description": "New template UID"},
                        "original_uid": {"type": "string", "description": "Original template UID"},
                        "name": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            
            "validation_rules": {
                "uid": {
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "message": "Template UID must be alphanumeric",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "auth": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires BannerBear API key to duplicate templates"
            },
            "examples": [
                {
                    "name": "Duplicate template",
                    "description": "Create a copy of an existing template",
                    "input": {
                        "uid": "A89Znq5X4lBXbdRPej",
                        "name": "My Template Copy"
                    }
                }
            ]
        },
        "list_projects": {
            "method": "GET",
            "endpoint": "/projects",
            "required_params": [],
            "optional_params": ["page", "limit"],
            "query_parameters": ["page", "limit"],
            "display_name": "List Projects",
            "description": "Retrieve list of all projects (requires Master API Key)",
            "group": "Account Management",
            "tags": ["projects", "account", "management", "organization"],
            "rate_limit_cost": 1,
            "cache_ttl": 7200,
            "response_type": "array",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "projects": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "uid": {"type": "string"},
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "created_at": {"type": "string", "format": "date-time"},
                                    "template_count": {"type": "integer"},
                                    "api_key": {"type": "string", "description": "Project API key"}
                                }
                            }
                        }
                    }
                }
            },
            
            "pagination": {
                "supported": True,
                "default_limit": 25,
                "max_limit": 100,
                "page_param": "page",
                "limit_param": "limit"
            },
            
            "auth": {
                "required_env_keys": ["BANNERBEAR_MASTER_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires BannerBear Master API key to list projects"
            },
            "examples": [
                {
                    "name": "List all projects",
                    "description": "Get all projects in account",
                    "input": {}
                }
            ]
        },
        "get_account": {
            "method": "GET",
            "endpoint": "/account",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Account",
            "description": "Retrieve account information including credit balance and usage",
            "group": "Account Management",
            "tags": ["account", "credits", "usage", "billing", "info"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "uid": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "plan": {"type": "string"},
                        "credits_remaining": {"type": "integer"},
                        "credits_used": {"type": "integer"},
                        "api_requests_made": {"type": "integer"},
                        "projects_count": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["BANNERBEAR_API_KEY"],
                "optional_env_keys": ["BANNERBEAR_PROJECT_ID"],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires BannerBear API key to get account information"
            },
            "examples": [
                {
                    "name": "Get account info",
                    "description": "Retrieve account details and credit balance",
                    "input": {}
                }
            ]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced BannerBear node with embedded configuration."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Initialize the Enhanced UniversalRequestNode with embedded config
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.info("Enhanced BannerBearNode initialized with all 13 advanced features")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"BannerBearNode executing operation: {node_data.get('params', {}).get('operation')}")
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
__all__ = ["BannerBearNode"]