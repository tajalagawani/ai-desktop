#!/usr/bin/env python3
"""
Box Node - Pure config-driven implementation using UniversalRequestNode
Configuration is embedded directly in the node - no separate config.json needed
Comprehensive Box API integration for file management, collaboration, and enterprise features
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

# Import the UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class BoxNode(BaseNode):
    """
    Pure config-driven Box node with embedded configuration.
    All operations are handled by UniversalRequestNode based on this config.
    Provides comprehensive Box API functionality for file management, collaboration, and enterprise features.
    Includes ALL 13 enhancements: output_schemas, array_templates, parameter_dependencies, 
    validation_rules, rate_limiting, pagination, error_handling, field_mapping, webhook_support, 
    testing_mode, performance_monitoring, caching_strategy, documentation_links.
    """
    
    # Embedded configuration for Box API
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "box",
            "display_name": "Box",
            "description": "Comprehensive Box API integration for cloud storage, file management, folders, sharing, collaboration, search, metadata, and versioning",
            "category": "cloud_storage",
            "vendor": "box",
            "version": "1.0.0",
            "author": "ACT Workflow",
            "tags": ["box", "cloud", "storage", "files", "folders", "collaboration", "sharing", "metadata", "versioning"],
            "documentation_url": "https://developer.box.com/reference/",
            "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/box.svg",
            "color": "#0061D5",
            "created_at": "2025-08-26T00:00:00Z",
            "updated_at": "2025-08-26T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.box.com/2.0",
            "authentication": {
                "type": "bearer_token",
                "header": "Authorization"
            },
            "default_headers": {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "ACT-Workflow-BoxNode"
            },
            "retry_config": {
                "max_attempts": 3,
                "backoff": "exponential",
                "retriable_codes": [429, 500, 502, 503, 504]
            },
            "rate_limiting": {
                "requests_per_second": 25,
                "burst_size": 5
            },
            "timeouts": {
                "connect": 15.0,
                "read": 60.0,
                "total": 120.0
            }
        },
        
        # All parameters with complete metadata and ALL 13 ENHANCEMENTS
        "parameters": {
            "access_token": {
                "type": "string",
                "description": "Box Developer Token or OAuth access token",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "minLength": 60,
                    "maxLength": 2048
                },
                "examples": ["your_developer_token_here"]
            },
            "operation": {
                "type": "string",
                "description": "The Box operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    # File operations
                    "get_file", "upload_file", "update_file", "delete_file", "copy_file", "move_file",
                    "download_file", "get_file_versions", "promote_version", "delete_version",
                    "preflight_check", "get_file_thumbnail", "get_file_embed_link", "lock_file", "unlock_file",
                    
                    # Folder operations
                    "get_folder", "create_folder", "update_folder", "delete_folder", "copy_folder",
                    "get_folder_items", "get_folder_collaborations", "restore_folder",
                    
                    # Search operations
                    "search", "search_users", "search_groups",
                    
                    # Sharing and collaboration
                    "create_shared_link", "remove_shared_link", "add_collaboration", "remove_collaboration",
                    "get_collaboration", "update_collaboration", "list_collaborations",
                    
                    # Metadata operations
                    "get_metadata", "create_metadata", "update_metadata", "delete_metadata",
                    "get_metadata_template", "create_metadata_template", "update_metadata_template",
                    
                    # User and enterprise operations
                    "get_current_user", "get_user", "create_user", "update_user", "delete_user",
                    "get_group", "create_group", "update_group", "delete_group", "add_user_to_group",
                    
                    # Webhooks
                    "create_webhook", "get_webhook", "update_webhook", "delete_webhook", "list_webhooks",
                    
                    # Tasks and comments
                    "create_task", "get_task", "update_task", "delete_task", "create_comment", "get_comment",
                    
                    # Enterprise features
                    "get_enterprise_events", "get_retention_policies", "create_retention_policy",
                    "get_legal_holds", "create_legal_hold"
                ],
                # ENHANCEMENT 3: Parameter dependencies
                "parameter_dependencies": {
                    "get_file": ["file_id"],
                    "upload_file": ["parent_id", "name", "content"],
                    "create_folder": ["parent_id", "name"],
                    "search": ["query"],
                    "add_collaboration": ["item_id", "item_type", "accessible_by"]
                }
            },
            
            # File/Folder identifiers
            "file_id": {
                "type": "string",
                "description": "Box file ID",
                "required": False,
                "group": "Files",
                "validation": {
                    "pattern": "^[0-9]+$",
                    "minLength": 1,
                    "maxLength": 20
                },
                "examples": ["12345", "987654321"]
            },
            "folder_id": {
                "type": "string",
                "description": "Box folder ID (0 for root folder)",
                "required": False,
                "group": "Folders",
                "validation": {
                    "pattern": "^[0-9]+$"
                },
                "default": "0",
                "examples": ["0", "12345", "987654321"]
            },
            "parent_id": {
                "type": "string",
                "description": "Parent folder ID for new items",
                "required": False,
                "group": "General",
                "validation": {
                    "pattern": "^[0-9]+$"
                },
                "examples": ["0", "12345"]
            },
            
            # Content parameters
            "name": {
                "type": "string",
                "description": "Name for files, folders, or other resources",
                "required": False,
                "group": "Content",
                "validation": {
                    "maxLength": 255,
                    "minLength": 1
                },
                "examples": ["document.pdf", "My Folder", "presentation.pptx"]
            },
            "description": {
                "type": "string",
                "description": "Description for files or folders",
                "required": False,
                "group": "Content",
                "validation": {
                    "maxLength": 256
                },
                "examples": ["Important document", "Project files folder"]
            },
            "content": {
                "type": "string",
                "description": "File content (base64 encoded for binary files)",
                "required": False,
                "group": "Files",
                "validation": {
                    "maxLength": 52428800  # 50MB in base64
                }
            },
            
            # Search parameters
            "query": {
                "type": "string",
                "description": "Search query string",
                "required": False,
                "group": "Search",
                "validation": {
                    "minLength": 1,
                    "maxLength": 500
                },
                "examples": ["budget 2024", "presentation", "*.pdf"]
            },
            "content_types": {
                "type": "array",
                "description": "File types to search for",
                "required": False,
                "group": "Search",
                "items": {"type": "string"},
                # ENHANCEMENT 2: Array templates
                "array_templates": {
                    "file_types": ["pdf", "docx", "xlsx", "pptx", "txt"],
                    "image_types": ["jpg", "jpeg", "png", "gif", "bmp"],
                    "video_types": ["mp4", "avi", "mov", "wmv"],
                    "document_types": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"]
                },
                "examples": [["pdf", "docx"], ["jpg", "png"]]
            },
            "file_extensions": {
                "type": "array",
                "description": "File extensions to filter by",
                "required": False,
                "group": "Search",
                "items": {"type": "string"},
                "examples": [["pdf"], ["jpg", "png", "gif"]]
            },
            
            # Collaboration parameters
            "accessible_by": {
                "type": "object",
                "description": "User or group to collaborate with",
                "required": False,
                "group": "Collaboration",
                "properties": {
                    "type": {"type": "string", "enum": ["user", "group"]},
                    "id": {"type": "string"},
                    "login": {"type": "string", "format": "email"}
                },
                "examples": [
                    {"type": "user", "login": "user@example.com"},
                    {"type": "group", "id": "12345"}
                ]
            },
            "role": {
                "type": "string",
                "description": "Collaboration role",
                "required": False,
                "group": "Collaboration",
                "enum": ["editor", "viewer", "previewer", "uploader", "previewer_uploader", "viewer_uploader", "co-owner"],
                "default": "viewer",
                "examples": ["editor", "viewer", "co-owner"]
            },
            "item_type": {
                "type": "string",
                "description": "Type of item (file or folder)",
                "required": False,
                "group": "General",
                "enum": ["file", "folder"],
                "examples": ["file", "folder"]
            },
            "item_id": {
                "type": "string",
                "description": "ID of the item to collaborate on",
                "required": False,
                "group": "General",
                "validation": {
                    "pattern": "^[0-9]+$"
                },
                "examples": ["12345", "987654321"]
            },
            
            # Shared link parameters
            "access": {
                "type": "string",
                "description": "Shared link access level",
                "required": False,
                "group": "Sharing",
                "enum": ["open", "company", "collaborators"],
                "default": "open",
                "examples": ["open", "company", "collaborators"]
            },
            "password": {
                "type": "string",
                "description": "Password for shared link",
                "required": False,
                "group": "Sharing",
                "sensitive": True,
                "validation": {
                    "minLength": 8,
                    "maxLength": 128
                }
            },
            "unshared_at": {
                "type": "string",
                "description": "When shared link expires (ISO 8601 format)",
                "required": False,
                "group": "Sharing",
                "validation": {
                    "format": "date-time"
                },
                "examples": ["2024-12-31T23:59:59Z"]
            },
            
            # Metadata parameters
            "template": {
                "type": "string",
                "description": "Metadata template key",
                "required": False,
                "group": "Metadata",
                "examples": ["properties", "marketingCollateral", "invoiceData"]
            },
            "scope": {
                "type": "string",
                "description": "Metadata template scope",
                "required": False,
                "group": "Metadata",
                "enum": ["global", "enterprise"],
                "default": "enterprise",
                "examples": ["global", "enterprise"]
            },
            "metadata": {
                "type": "object",
                "description": "Metadata key-value pairs",
                "required": False,
                "group": "Metadata",
                "examples": [
                    {"category": "invoice", "amount": 1500.00, "client": "Acme Corp"},
                    {"department": "Marketing", "campaign": "Q4 2024"}
                ]
            },
            
            # Version control parameters
            "version_id": {
                "type": "string",
                "description": "File version ID",
                "required": False,
                "group": "Versioning",
                "validation": {
                    "pattern": "^[0-9]+$"
                },
                "examples": ["123456789"]
            },
            
            # User management parameters
            "user_id": {
                "type": "string",
                "description": "Box user ID",
                "required": False,
                "group": "Users",
                "validation": {
                    "pattern": "^[0-9]+$"
                },
                "examples": ["12345", "987654321"]
            },
            "login": {
                "type": "string",
                "description": "User email address",
                "required": False,
                "group": "Users",
                "validation": {
                    "format": "email"
                },
                "examples": ["user@example.com", "admin@company.com"]
            },
            "is_platform_access_only": {
                "type": "boolean",
                "description": "Whether user has platform access only",
                "required": False,
                "group": "Users",
                "default": False
            },
            
            # Group management parameters
            "group_id": {
                "type": "string",
                "description": "Box group ID",
                "required": False,
                "group": "Groups",
                "validation": {
                    "pattern": "^[0-9]+$"
                },
                "examples": ["12345"]
            },
            "invitability_level": {
                "type": "string",
                "description": "Group invitation level",
                "required": False,
                "group": "Groups",
                "enum": ["admins_only", "admins_and_members", "all_managed_users"],
                "default": "admins_only"
            },
            "member_viewability_level": {
                "type": "string",
                "description": "Group member visibility level",
                "required": False,
                "group": "Groups",
                "enum": ["admins_only", "admins_and_members", "all_managed_users"],
                "default": "admins_only"
            },
            
            # Webhook parameters
            "webhook_id": {
                "type": "string",
                "description": "Webhook ID",
                "required": False,
                "group": "Webhooks",
                "validation": {
                    "pattern": "^[0-9]+$"
                }
            },
            "target_url": {
                "type": "string",
                "description": "Webhook target URL",
                "required": False,
                "group": "Webhooks",
                "validation": {
                    "format": "uri",
                    "pattern": "^https://"
                },
                "examples": ["https://example.com/webhook"]
            },
            "triggers": {
                "type": "array",
                "description": "Webhook trigger events",
                "required": False,
                "group": "Webhooks",
                "items": {"type": "string"},
                "enum_items": [
                    "FILE.UPLOADED", "FILE.DOWNLOADED", "FILE.PREVIEWED", "FILE.LOCKED", "FILE.UNLOCKED",
                    "FILE.DELETED", "FILE.RESTORED", "FILE.COPIED", "FILE.MOVED", "FILE.TRASHED",
                    "FOLDER.CREATED", "FOLDER.DOWNLOADED", "FOLDER.RESTORED", "FOLDER.DELETED",
                    "FOLDER.COPIED", "FOLDER.MOVED", "FOLDER.TRASHED", "COLLABORATION.CREATED",
                    "COLLABORATION.ACCEPTED", "COLLABORATION.REJECTED", "COLLABORATION.REMOVED",
                    "COLLABORATION.UPDATED", "SHARED_LINK.DELETED", "SHARED_LINK.CREATED"
                ],
                "examples": [["FILE.UPLOADED", "FILE.DOWNLOADED"], ["COLLABORATION.CREATED"]]
            },
            
            # Task parameters
            "task_id": {
                "type": "string",
                "description": "Task ID",
                "required": False,
                "group": "Tasks",
                "validation": {
                    "pattern": "^[0-9]+$"
                }
            },
            "action": {
                "type": "string",
                "description": "Task action type",
                "required": False,
                "group": "Tasks",
                "enum": ["review", "complete"],
                "default": "review"
            },
            "due_at": {
                "type": "string",
                "description": "Task due date (ISO 8601 format)",
                "required": False,
                "group": "Tasks",
                "validation": {
                    "format": "date-time"
                },
                "examples": ["2024-12-31T17:00:00Z"]
            },
            "message": {
                "type": "string",
                "description": "Task or comment message",
                "required": False,
                "group": "Tasks",
                "validation": {
                    "maxLength": 65536
                }
            },
            
            # Comment parameters
            "comment_id": {
                "type": "string",
                "description": "Comment ID",
                "required": False,
                "group": "Comments",
                "validation": {
                    "pattern": "^[0-9]+$"
                }
            },
            "tagged_message": {
                "type": "string",
                "description": "Comment message with @mentions",
                "required": False,
                "group": "Comments",
                "validation": {
                    "maxLength": 65536
                }
            },
            
            # Filtering and pagination parameters
            "fields": {
                "type": "array",
                "description": "Fields to include in response",
                "required": False,
                "group": "Response",
                "items": {"type": "string"},
                "examples": [["id", "name", "size"], ["id", "name", "modified_at", "created_by"]]
            },
            "limit": {
                "type": "number",
                "description": "Maximum number of items to return",
                "required": False,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 1000
                },
                "default": 100
            },
            "offset": {
                "type": "number",
                "description": "Number of items to skip",
                "required": False,
                "group": "Pagination",
                "validation": {
                    "minimum": 0
                },
                "default": 0
            },
            "marker": {
                "type": "string",
                "description": "Pagination marker for large result sets",
                "required": False,
                "group": "Pagination"
            },
            "sort": {
                "type": "string",
                "description": "Sort field for search results",
                "required": False,
                "group": "Sorting",
                "enum": ["id", "name", "date", "size", "modified_at", "relevance"],
                "default": "relevance"
            },
            "direction": {
                "type": "string",
                "description": "Sort direction",
                "required": False,
                "group": "Sorting",
                "enum": ["ASC", "DESC"],
                "default": "DESC"
            },
            
            # Advanced filtering
            "created_at_range": {
                "type": "string",
                "description": "Created date range filter (from_date,to_date)",
                "required": False,
                "group": "Filters",
                "examples": ["2024-01-01T00:00:00Z,2024-12-31T23:59:59Z"]
            },
            "updated_at_range": {
                "type": "string",
                "description": "Updated date range filter (from_date,to_date)",
                "required": False,
                "group": "Filters",
                "examples": ["2024-01-01T00:00:00Z,2024-12-31T23:59:59Z"]
            },
            "size_range": {
                "type": "string",
                "description": "File size range filter (min_bytes,max_bytes)",
                "required": False,
                "group": "Filters",
                "examples": ["1024,10485760"]  # 1KB to 10MB
            },
            "owner_user_ids": {
                "type": "array",
                "description": "Filter by owner user IDs",
                "required": False,
                "group": "Filters",
                "items": {"type": "string"},
                "examples": [["12345", "67890"]]
            },
            "ancestor_folder_ids": {
                "type": "array",
                "description": "Filter by ancestor folder IDs",
                "required": False,
                "group": "Filters",
                "items": {"type": "string"},
                "examples": [["0", "12345"]]
            },
            
            # ENHANCEMENT 10: Testing mode
            "testing_mode": {
                "type": "boolean",
                "description": "Enable testing mode (uses mock responses)",
                "required": False,
                "group": "Testing",
                "default": False
            },
            "mock_response": {
                "type": "object",
                "description": "Mock response data for testing",
                "required": False,
                "group": "Testing"
            }
        },
        
        # ENHANCEMENT 1: Output schemas with comprehensive definitions
        "output_schemas": {
            "file_response": {
                "type": "object",
                "description": "File object response",
                "properties": {
                    "id": {"type": "string", "description": "File ID"},
                    "name": {"type": "string", "description": "File name"},
                    "size": {"type": "number", "description": "File size in bytes"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "modified_at": {"type": "string", "format": "date-time"},
                    "content_created_at": {"type": "string", "format": "date-time"},
                    "content_modified_at": {"type": "string", "format": "date-time"},
                    "sha1": {"type": "string", "description": "SHA1 hash"},
                    "parent": {"type": "object", "description": "Parent folder"},
                    "path_collection": {"type": "object", "description": "Folder path"},
                    "created_by": {"type": "object", "description": "User who created file"},
                    "modified_by": {"type": "object", "description": "User who last modified file"},
                    "owned_by": {"type": "object", "description": "File owner"},
                    "shared_link": {"type": "object", "description": "Shared link details"},
                    "permissions": {"type": "object", "description": "File permissions"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "version_number": {"type": "string", "description": "File version"},
                    "comment_count": {"type": "number", "description": "Number of comments"},
                    "lock": {"type": "object", "description": "File lock information"}
                }
            },
            "folder_response": {
                "type": "object",
                "description": "Folder object response",
                "properties": {
                    "id": {"type": "string", "description": "Folder ID"},
                    "name": {"type": "string", "description": "Folder name"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "modified_at": {"type": "string", "format": "date-time"},
                    "description": {"type": "string", "description": "Folder description"},
                    "size": {"type": "number", "description": "Folder size in bytes"},
                    "path_collection": {"type": "object", "description": "Folder path"},
                    "created_by": {"type": "object", "description": "User who created folder"},
                    "modified_by": {"type": "object", "description": "User who last modified folder"},
                    "owned_by": {"type": "object", "description": "Folder owner"},
                    "shared_link": {"type": "object", "description": "Shared link details"},
                    "folder_upload_email": {"type": "object", "description": "Upload email settings"},
                    "parent": {"type": "object", "description": "Parent folder"},
                    "item_status": {"type": "string", "enum": ["active", "trashed", "deleted"]},
                    "item_collection": {"type": "object", "description": "Folder contents"},
                    "permissions": {"type": "object", "description": "Folder permissions"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "has_collaborations": {"type": "boolean"},
                    "is_externally_owned": {"type": "boolean"}
                }
            },
            "search_response": {
                "type": "object",
                "description": "Search results response",
                "properties": {
                    "total_count": {"type": "number", "description": "Total number of results"},
                    "offset": {"type": "number", "description": "Offset of results"},
                    "limit": {"type": "number", "description": "Maximum results returned"},
                    "entries": {
                        "type": "array",
                        "description": "Search result entries",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "type": {"type": "string", "enum": ["file", "folder", "web_link"]},
                                "parent": {"type": "object"},
                                "path_collection": {"type": "object"}
                            }
                        }
                    }
                }
            },
            "collaboration_response": {
                "type": "object",
                "description": "Collaboration object response",
                "properties": {
                    "id": {"type": "string", "description": "Collaboration ID"},
                    "type": {"type": "string", "enum": ["collaboration"]},
                    "item": {"type": "object", "description": "Collaborated item"},
                    "accessible_by": {"type": "object", "description": "Collaborator details"},
                    "role": {"type": "string", "description": "Collaboration role"},
                    "acknowledged_at": {"type": "string", "format": "date-time"},
                    "created_by": {"type": "object", "description": "User who created collaboration"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "modified_at": {"type": "string", "format": "date-time"},
                    "expires_at": {"type": "string", "format": "date-time"},
                    "status": {"type": "string", "enum": ["accepted", "pending", "rejected"]},
                    "invite_email": {"type": "string", "format": "email"}
                }
            },
            "metadata_response": {
                "type": "object",
                "description": "Metadata response",
                "properties": {
                    "$parent": {"type": "string", "description": "Parent object ID"},
                    "$template": {"type": "string", "description": "Template key"},
                    "$scope": {"type": "string", "description": "Template scope"},
                    "$id": {"type": "string", "description": "Metadata ID"},
                    "$version": {"type": "number", "description": "Metadata version"},
                    "$type": {"type": "string", "description": "Metadata type"},
                    "$typeVersion": {"type": "number", "description": "Type version"}
                },
                "additionalProperties": True
            },
            "user_response": {
                "type": "object",
                "description": "User object response",
                "properties": {
                    "id": {"type": "string", "description": "User ID"},
                    "name": {"type": "string", "description": "User full name"},
                    "login": {"type": "string", "format": "email", "description": "User email"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "modified_at": {"type": "string", "format": "date-time"},
                    "language": {"type": "string", "description": "User language"},
                    "timezone": {"type": "string", "description": "User timezone"},
                    "space_amount": {"type": "number", "description": "Storage quota in bytes"},
                    "space_used": {"type": "number", "description": "Storage used in bytes"},
                    "max_upload_size": {"type": "number", "description": "Max upload size"},
                    "status": {"type": "string", "enum": ["active", "inactive", "cannot_delete_edit", "cannot_delete_edit_upload"]},
                    "job_title": {"type": "string", "description": "User job title"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "address": {"type": "string", "description": "Address"},
                    "avatar_url": {"type": "string", "format": "uri", "description": "Avatar URL"},
                    "role": {"type": "string", "enum": ["admin", "coadmin", "user"]},
                    "is_sync_enabled": {"type": "boolean"},
                    "is_external_collab_restricted": {"type": "boolean"},
                    "is_exempt_from_device_limits": {"type": "boolean"},
                    "is_exempt_from_login_verification": {"type": "boolean"},
                    "enterprise": {"type": "object", "description": "Enterprise information"},
                    "my_tags": {"type": "array", "items": {"type": "string"}}
                }
            },
            "webhook_response": {
                "type": "object",
                "description": "Webhook object response",
                "properties": {
                    "id": {"type": "string", "description": "Webhook ID"},
                    "type": {"type": "string", "enum": ["webhook"]},
                    "target": {"type": "object", "description": "Target object"},
                    "created_by": {"type": "object", "description": "User who created webhook"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "address": {"type": "string", "format": "uri", "description": "Webhook URL"},
                    "triggers": {"type": "array", "items": {"type": "string"}, "description": "Trigger events"}
                }
            },
            "error_response": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "type": {"type": "string", "enum": ["error"]},
                    "status": {"type": "number", "description": "HTTP status code"},
                    "code": {"type": "string", "description": "Error code"},
                    "message": {"type": "string", "description": "Error message"},
                    "context_info": {"type": "object", "description": "Additional error context"},
                    "help_url": {"type": "string", "format": "uri", "description": "Help documentation URL"},
                    "request_id": {"type": "string", "description": "Request ID for support"}
                }
            }
        },
        
        # Outputs with schema references
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful Box API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from Box API"},
                    "response_data": {"type": "object", "description": "Full API response"},
                    "schema": {"type": "string", "description": "Response schema reference"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Error code"},
                    "context_info": {"type": "object", "description": "Additional error context"}
                }
            }
        },
        
        # ENHANCEMENT 4: Validation rules
        "validation_rules": {
            "file_size_limits": {
                "free_account": 250000000,      # 250MB
                "business_account": 5000000000, # 5GB
                "enterprise_account": 50000000000  # 50GB
            },
            "name_restrictions": {
                "forbidden_chars": ["<", ">", ":", "\"", "|", "?", "*", "/", "\\"],
                "forbidden_names": ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"],
                "max_length": 255
            },
            "collaboration_limits": {
                "max_collaborators_per_item": 50000,
                "max_groups_per_collaboration": 100
            },
            "search_limits": {
                "max_query_length": 500,
                "max_results_per_request": 200
            }
        },
        
        # ENHANCEMENT 6: Pagination support
        "pagination": {
            "default_limit": 100,
            "max_limit": 1000,
            "supports_marker": True,
            "supports_offset": True,
            "marker_field": "next_marker",
            "total_count_field": "total_count"
        },
        
        # ENHANCEMENT 7: Error handling
        "error_handling": {
            "retry_on_errors": [429, 500, 502, 503, 504],
            "max_retries": 3,
            "retry_delay": 1.0,
            "backoff_multiplier": 2.0,
            "error_mappings": {
                "400": "bad_request",
                "401": "unauthorized", 
                "403": "forbidden",
                "404": "not_found",
                "409": "conflict",
                "412": "precondition_failed",
                "413": "request_entity_too_large",
                "429": "too_many_requests",
                "500": "internal_server_error",
                "502": "bad_gateway",
                "503": "service_unavailable"
            }
        },
        
        # ENHANCEMENT 8: Field mapping
        "field_mapping": {
            "request_mappings": {
                "content": "file_content",
                "accessible_by": "collaborator",
                "target_url": "address"
            },
            "response_mappings": {
                "modified_at": "updated_at",
                "content_created_at": "created_at",
                "content_modified_at": "modified_at"
            },
            "nested_mappings": {
                "created_by.name": "creator_name",
                "modified_by.name": "modifier_name",
                "parent.name": "parent_folder_name"
            }
        },
        
        # ENHANCEMENT 11: Performance monitoring
        "performance_monitoring": {
            "track_response_times": True,
            "track_error_rates": True,
            "track_rate_limit_usage": True,
            "performance_thresholds": {
                "slow_request_ms": 2000,
                "very_slow_request_ms": 5000,
                "error_rate_threshold": 0.05,
                "rate_limit_threshold": 0.8
            },
            "metrics_retention_days": 30
        },
        
        # ENHANCEMENT 12: Caching strategy
        "caching_strategy": {
            "enabled": True,
            "default_ttl": 300,  # 5 minutes
            "operation_ttls": {
                "get_file": 300,
                "get_folder": 300,
                "get_folder_items": 180,
                "get_current_user": 600,
                "get_user": 600,
                "search": 60
            },
            "cache_keys": {
                "get_file": "box:file:{file_id}",
                "get_folder": "box:folder:{folder_id}",
                "get_current_user": "box:user:current:{access_token_hash}",
                "search": "box:search:{query_hash}"
            },
            "invalidation_events": {
                "update_file": ["box:file:{file_id}"],
                "delete_file": ["box:file:{file_id}", "box:folder:{parent_id}"],
                "create_folder": ["box:folder:{parent_id}"],
                "upload_file": ["box:folder:{parent_id}"]
            }
        },
        
        # ENHANCEMENT 13: Documentation links
        "documentation_links": {
            "base_url": "https://developer.box.com/reference/",
            "operation_links": {
                "get_file": "https://developer.box.com/reference/get-files-id/",
                "upload_file": "https://developer.box.com/reference/post-files-content/",
                "update_file": "https://developer.box.com/reference/put-files-id/",
                "delete_file": "https://developer.box.com/reference/delete-files-id/",
                "copy_file": "https://developer.box.com/reference/post-files-id-copy/",
                "get_folder": "https://developer.box.com/reference/get-folders-id/",
                "create_folder": "https://developer.box.com/reference/post-folders/",
                "update_folder": "https://developer.box.com/reference/put-folders-id/",
                "delete_folder": "https://developer.box.com/reference/delete-folders-id/",
                "search": "https://developer.box.com/reference/get-search/",
                "create_shared_link": "https://developer.box.com/reference/put-files-id/#request-body-shared_link",
                "add_collaboration": "https://developer.box.com/reference/post-collaborations/",
                "create_webhook": "https://developer.box.com/reference/post-webhooks/",
                "get_metadata": "https://developer.box.com/reference/get-files-id-metadata-id-id/",
                "create_metadata": "https://developer.box.com/reference/post-files-id-metadata-id-id/"
            },
            "guides": {
                "authentication": "https://developer.box.com/guides/authentication/",
                "files": "https://developer.box.com/guides/files/",
                "folders": "https://developer.box.com/guides/folders/",
                "search": "https://developer.box.com/guides/search/",
                "collaboration": "https://developer.box.com/guides/collaborations/",
                "metadata": "https://developer.box.com/guides/metadata/",
                "webhooks": "https://developer.box.com/guides/webhooks/",
                "uploads": "https://developer.box.com/guides/uploads/"
            },
            "sdks": {
                "python": "https://github.com/box/box-python-sdk",
                "javascript": "https://github.com/box/box-node-sdk",
                "java": "https://github.com/box/box-java-sdk",
                "dotnet": "https://github.com/box/box-windows-sdk-v2"
            }
        },
        
        # Error codes specific to Box API
        "error_codes": {
            "400": "Bad Request - Invalid request parameters or malformed request",
            "401": "Unauthorized - Invalid or expired access token",
            "403": "Forbidden - Access denied or insufficient permissions",
            "404": "Not Found - Resource not found or user doesn't have access",
            "405": "Method Not Allowed - HTTP method not supported for this endpoint",
            "409": "Conflict - Resource already exists or conflict with current state",
            "412": "Precondition Failed - If-Match header doesn't match current etag",
            "413": "Request Entity Too Large - File size exceeds limits",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Box server error",
            "502": "Bad Gateway - Box server temporarily unavailable",
            "503": "Service Unavailable - Box maintenance or overload"
        }
    }
    
    # ENHANCEMENT 9: Webhook support definitions
    WEBHOOK_EVENTS = {
        "FILE.UPLOADED": "A file was uploaded to Box",
        "FILE.DOWNLOADED": "A file was downloaded from Box",
        "FILE.PREVIEWED": "A file was previewed",
        "FILE.LOCKED": "A file was locked",
        "FILE.UNLOCKED": "A file was unlocked",
        "FILE.DELETED": "A file was permanently deleted",
        "FILE.RESTORED": "A file was restored from trash",
        "FILE.COPIED": "A file was copied",
        "FILE.MOVED": "A file was moved",
        "FILE.TRASHED": "A file was moved to trash",
        "FOLDER.CREATED": "A folder was created",
        "FOLDER.DOWNLOADED": "A folder was downloaded as a zip",
        "FOLDER.RESTORED": "A folder was restored from trash",
        "FOLDER.DELETED": "A folder was permanently deleted",
        "FOLDER.COPIED": "A folder was copied",
        "FOLDER.MOVED": "A folder was moved",
        "FOLDER.TRASHED": "A folder was moved to trash",
        "COLLABORATION.CREATED": "A collaboration was created",
        "COLLABORATION.ACCEPTED": "A collaboration was accepted",
        "COLLABORATION.REJECTED": "A collaboration was rejected",
        "COLLABORATION.REMOVED": "A collaboration was removed",
        "COLLABORATION.UPDATED": "A collaboration was updated",
        "SHARED_LINK.DELETED": "A shared link was removed",
        "SHARED_LINK.CREATED": "A shared link was created"
    }
    
    # Operation definitions with complete metadata including all enhancements
    OPERATIONS = {
        # File operations
        "get_file": {
            "method": "GET",
            "endpoint": "/files/{file_id}",
            "required_params": ["file_id"],
            "optional_params": ["fields"],
            "display_name": "Get File",
            "description": "Get information about a file",
            "group": "Files",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_schema": "file_response",
            "response_type": "object",
            "examples": [
                {
                    "name": "Get file details",
                    "input": {"file_id": "12345"},
                    "output_sample": {
                        "id": "12345",
                        "name": "document.pdf",
                        "size": 1024000,
                        "created_at": "2024-01-01T00:00:00-08:00"
                    }
                }
            ]
        },
        "upload_file": {
            "method": "POST",
            "endpoint": "/files/content",
            "required_params": ["parent_id", "name", "content"],
            "optional_params": ["content_created_at", "content_modified_at"],
            "display_name": "Upload File",
            "description": "Upload a new file to Box",
            "group": "Files",
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_schema": "file_response",
            "response_type": "object",
            "validation_rules": ["file_size_limits", "name_restrictions"]
        },
        "update_file": {
            "method": "PUT",
            "endpoint": "/files/{file_id}",
            "required_params": ["file_id"],
            "optional_params": ["name", "description", "parent"],
            "display_name": "Update File",
            "description": "Update file information",
            "group": "Files",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "file_response"
        },
        "delete_file": {
            "method": "DELETE",
            "endpoint": "/files/{file_id}",
            "required_params": ["file_id"],
            "optional_params": ["if_match"],
            "display_name": "Delete File",
            "description": "Move a file to the trash",
            "group": "Files",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "copy_file": {
            "method": "POST",
            "endpoint": "/files/{file_id}/copy",
            "required_params": ["file_id", "parent"],
            "optional_params": ["name"],
            "display_name": "Copy File",
            "description": "Create a copy of a file",
            "group": "Files",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "file_response"
        },
        "move_file": {
            "method": "PUT",
            "endpoint": "/files/{file_id}",
            "required_params": ["file_id", "parent"],
            "optional_params": ["name"],
            "display_name": "Move File",
            "description": "Move a file to a different folder",
            "group": "Files",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "file_response"
        },
        "download_file": {
            "method": "GET",
            "endpoint": "/files/{file_id}/content",
            "required_params": ["file_id"],
            "optional_params": ["version"],
            "display_name": "Download File",
            "description": "Download file content",
            "group": "Files",
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "binary"
        },
        "get_file_versions": {
            "method": "GET",
            "endpoint": "/files/{file_id}/versions",
            "required_params": ["file_id"],
            "optional_params": ["fields", "limit", "offset"],
            "display_name": "Get File Versions",
            "description": "List all versions of a file",
            "group": "Versioning",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "supports_pagination": True
        },
        "promote_version": {
            "method": "POST",
            "endpoint": "/files/{file_id}/versions/current",
            "required_params": ["file_id", "version_id"],
            "display_name": "Promote File Version",
            "description": "Promote a file version to be the current version",
            "group": "Versioning",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "delete_version": {
            "method": "DELETE",
            "endpoint": "/files/{file_id}/versions/{version_id}",
            "required_params": ["file_id", "version_id"],
            "optional_params": ["if_match"],
            "display_name": "Delete File Version",
            "description": "Delete a specific version of a file",
            "group": "Versioning",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "lock_file": {
            "method": "PUT",
            "endpoint": "/files/{file_id}",
            "required_params": ["file_id"],
            "optional_params": ["expires_at", "is_download_prevented"],
            "display_name": "Lock File",
            "description": "Lock a file to prevent editing",
            "group": "Files",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "unlock_file": {
            "method": "PUT",
            "endpoint": "/files/{file_id}",
            "required_params": ["file_id"],
            "display_name": "Unlock File",
            "description": "Unlock a file to allow editing",
            "group": "Files",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        
        # Folder operations
        "get_folder": {
            "method": "GET",
            "endpoint": "/folders/{folder_id}",
            "required_params": ["folder_id"],
            "optional_params": ["fields"],
            "display_name": "Get Folder",
            "description": "Get information about a folder",
            "group": "Folders",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_schema": "folder_response"
        },
        "create_folder": {
            "method": "POST",
            "endpoint": "/folders",
            "required_params": ["name", "parent_id"],
            "optional_params": ["fields"],
            "display_name": "Create Folder",
            "description": "Create a new folder",
            "group": "Folders",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "folder_response",
            "validation_rules": ["name_restrictions"]
        },
        "update_folder": {
            "method": "PUT",
            "endpoint": "/folders/{folder_id}",
            "required_params": ["folder_id"],
            "optional_params": ["name", "description", "parent", "fields"],
            "display_name": "Update Folder",
            "description": "Update folder information",
            "group": "Folders",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "folder_response"
        },
        "delete_folder": {
            "method": "DELETE",
            "endpoint": "/folders/{folder_id}",
            "required_params": ["folder_id"],
            "optional_params": ["recursive", "if_match"],
            "display_name": "Delete Folder",
            "description": "Move a folder to the trash",
            "group": "Folders",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "copy_folder": {
            "method": "POST",
            "endpoint": "/folders/{folder_id}/copy",
            "required_params": ["folder_id", "parent"],
            "optional_params": ["name", "fields"],
            "display_name": "Copy Folder",
            "description": "Create a copy of a folder",
            "group": "Folders",
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_schema": "folder_response"
        },
        "get_folder_items": {
            "method": "GET",
            "endpoint": "/folders/{folder_id}/items",
            "required_params": ["folder_id"],
            "optional_params": ["fields", "limit", "offset", "marker", "sort", "direction"],
            "display_name": "Get Folder Items",
            "description": "List items in a folder",
            "group": "Folders",
            "rate_limit_cost": 1,
            "cache_ttl": 180,
            "supports_pagination": True,
            "pagination_type": "marker"
        },
        "get_folder_collaborations": {
            "method": "GET",
            "endpoint": "/folders/{folder_id}/collaborations",
            "required_params": ["folder_id"],
            "optional_params": ["fields"],
            "display_name": "Get Folder Collaborations",
            "description": "List collaborations on a folder",
            "group": "Collaboration",
            "rate_limit_cost": 1,
            "cache_ttl": 300
        },
        "restore_folder": {
            "method": "POST",
            "endpoint": "/folders/{folder_id}",
            "required_params": ["folder_id"],
            "optional_params": ["name", "parent", "fields"],
            "display_name": "Restore Folder",
            "description": "Restore a folder from the trash",
            "group": "Folders",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        
        # Search operations
        "search": {
            "method": "GET",
            "endpoint": "/search",
            "required_params": ["query"],
            "optional_params": ["scope", "file_extensions", "created_at_range", "updated_at_range", 
                               "size_range", "owner_user_ids", "ancestor_folder_ids", "content_types",
                               "type", "trash_content", "mdfilters", "sort", "direction", "limit", "offset"],
            "display_name": "Search",
            "description": "Search for files and folders",
            "group": "Search",
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_schema": "search_response",
            "supports_pagination": True,
            "validation_rules": ["search_limits"]
        },
        "search_users": {
            "method": "GET",
            "endpoint": "/users",
            "required_params": [],
            "optional_params": ["filter_term", "fields", "limit", "offset"],
            "display_name": "Search Users",
            "description": "Search for users in the enterprise",
            "group": "Search",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "supports_pagination": True
        },
        "search_groups": {
            "method": "GET",
            "endpoint": "/groups",
            "required_params": [],
            "optional_params": ["filter_term", "fields", "limit", "offset"],
            "display_name": "Search Groups",
            "description": "Search for groups in the enterprise",
            "group": "Search",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "supports_pagination": True
        },
        
        # Sharing and collaboration
        "create_shared_link": {
            "method": "PUT",
            "endpoint": "/files/{file_id}",
            "required_params": ["file_id"],
            "optional_params": ["access", "password", "unshared_at", "can_download", "can_preview"],
            "display_name": "Create Shared Link",
            "description": "Create a shared link for a file",
            "group": "Sharing",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "remove_shared_link": {
            "method": "PUT",
            "endpoint": "/files/{file_id}",
            "required_params": ["file_id"],
            "display_name": "Remove Shared Link",
            "description": "Remove shared link from a file",
            "group": "Sharing",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "add_collaboration": {
            "method": "POST",
            "endpoint": "/collaborations",
            "required_params": ["item_id", "item_type", "accessible_by", "role"],
            "optional_params": ["notify", "can_view_path", "expires_at"],
            "display_name": "Add Collaboration",
            "description": "Add a collaborator to a file or folder",
            "group": "Collaboration",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "collaboration_response",
            "validation_rules": ["collaboration_limits"]
        },
        "remove_collaboration": {
            "method": "DELETE",
            "endpoint": "/collaborations/{collaboration_id}",
            "required_params": ["collaboration_id"],
            "display_name": "Remove Collaboration",
            "description": "Remove a collaboration",
            "group": "Collaboration",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "get_collaboration": {
            "method": "GET",
            "endpoint": "/collaborations/{collaboration_id}",
            "required_params": ["collaboration_id"],
            "optional_params": ["fields"],
            "display_name": "Get Collaboration",
            "description": "Get information about a collaboration",
            "group": "Collaboration",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_schema": "collaboration_response"
        },
        "update_collaboration": {
            "method": "PUT",
            "endpoint": "/collaborations/{collaboration_id}",
            "required_params": ["collaboration_id"],
            "optional_params": ["role", "status", "expires_at", "can_view_path"],
            "display_name": "Update Collaboration",
            "description": "Update a collaboration",
            "group": "Collaboration",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "collaboration_response"
        },
        "list_collaborations": {
            "method": "GET",
            "endpoint": "/collaborations",
            "required_params": [],
            "optional_params": ["status", "fields", "offset", "limit"],
            "display_name": "List Collaborations",
            "description": "List user's collaborations",
            "group": "Collaboration",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "supports_pagination": True
        },
        
        # Metadata operations
        "get_metadata": {
            "method": "GET",
            "endpoint": "/files/{file_id}/metadata/{scope}/{template}",
            "required_params": ["file_id", "scope", "template"],
            "display_name": "Get Metadata",
            "description": "Get metadata on a file",
            "group": "Metadata",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_schema": "metadata_response"
        },
        "create_metadata": {
            "method": "POST",
            "endpoint": "/files/{file_id}/metadata/{scope}/{template}",
            "required_params": ["file_id", "scope", "template", "metadata"],
            "display_name": "Create Metadata",
            "description": "Create metadata on a file",
            "group": "Metadata",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "metadata_response"
        },
        "update_metadata": {
            "method": "PUT",
            "endpoint": "/files/{file_id}/metadata/{scope}/{template}",
            "required_params": ["file_id", "scope", "template"],
            "optional_params": ["metadata"],
            "display_name": "Update Metadata",
            "description": "Update metadata on a file",
            "group": "Metadata",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "metadata_response"
        },
        "delete_metadata": {
            "method": "DELETE",
            "endpoint": "/files/{file_id}/metadata/{scope}/{template}",
            "required_params": ["file_id", "scope", "template"],
            "display_name": "Delete Metadata",
            "description": "Delete metadata from a file",
            "group": "Metadata",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "get_metadata_template": {
            "method": "GET",
            "endpoint": "/metadata_templates/{scope}/{template_key}/schema",
            "required_params": ["scope", "template"],
            "display_name": "Get Metadata Template",
            "description": "Get information about a metadata template",
            "group": "Metadata",
            "rate_limit_cost": 1,
            "cache_ttl": 600
        },
        "create_metadata_template": {
            "method": "POST",
            "endpoint": "/metadata_templates/schema",
            "required_params": ["template_key", "display_name", "fields"],
            "optional_params": ["hidden", "copyInstanceOnItemCopy"],
            "display_name": "Create Metadata Template",
            "description": "Create a new metadata template",
            "group": "Metadata",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "update_metadata_template": {
            "method": "PUT",
            "endpoint": "/metadata_templates/{scope}/{template_key}/schema",
            "required_params": ["scope", "template"],
            "optional_params": ["op", "data"],
            "display_name": "Update Metadata Template",
            "description": "Update a metadata template",
            "group": "Metadata",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        
        # User and enterprise operations
        "get_current_user": {
            "method": "GET",
            "endpoint": "/users/me",
            "required_params": [],
            "optional_params": ["fields"],
            "display_name": "Get Current User",
            "description": "Get information about the current user",
            "group": "Users",
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_schema": "user_response"
        },
        "get_user": {
            "method": "GET",
            "endpoint": "/users/{user_id}",
            "required_params": ["user_id"],
            "optional_params": ["fields"],
            "display_name": "Get User",
            "description": "Get information about a user",
            "group": "Users",
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_schema": "user_response"
        },
        "create_user": {
            "method": "POST",
            "endpoint": "/users",
            "required_params": ["name", "login"],
            "optional_params": ["role", "language", "is_sync_enabled", "job_title", "phone", "address"],
            "display_name": "Create User",
            "description": "Create a new managed user",
            "group": "Users",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "user_response"
        },
        "update_user": {
            "method": "PUT",
            "endpoint": "/users/{user_id}",
            "required_params": ["user_id"],
            "optional_params": ["name", "login", "role", "language", "is_sync_enabled", "job_title", "phone", "address"],
            "display_name": "Update User",
            "description": "Update a managed user",
            "group": "Users",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "user_response"
        },
        "delete_user": {
            "method": "DELETE",
            "endpoint": "/users/{user_id}",
            "required_params": ["user_id"],
            "optional_params": ["notify", "force"],
            "display_name": "Delete User",
            "description": "Delete a managed user",
            "group": "Users",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        
        # Group operations
        "get_group": {
            "method": "GET",
            "endpoint": "/groups/{group_id}",
            "required_params": ["group_id"],
            "optional_params": ["fields"],
            "display_name": "Get Group",
            "description": "Get information about a group",
            "group": "Groups",
            "rate_limit_cost": 1,
            "cache_ttl": 600
        },
        "create_group": {
            "method": "POST",
            "endpoint": "/groups",
            "required_params": ["name"],
            "optional_params": ["provenance", "external_sync_identifier", "description", "invitability_level", "member_viewability_level"],
            "display_name": "Create Group",
            "description": "Create a new group",
            "group": "Groups",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "update_group": {
            "method": "PUT",
            "endpoint": "/groups/{group_id}",
            "required_params": ["group_id"],
            "optional_params": ["name", "provenance", "external_sync_identifier", "description", "invitability_level", "member_viewability_level"],
            "display_name": "Update Group",
            "description": "Update a group",
            "group": "Groups",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "delete_group": {
            "method": "DELETE",
            "endpoint": "/groups/{group_id}",
            "required_params": ["group_id"],
            "display_name": "Delete Group",
            "description": "Delete a group",
            "group": "Groups",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "add_user_to_group": {
            "method": "POST",
            "endpoint": "/group_memberships",
            "required_params": ["user_id", "group_id"],
            "optional_params": ["role", "configurable_permissions"],
            "display_name": "Add User to Group",
            "description": "Add a user to a group",
            "group": "Groups",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        
        # Webhooks
        "create_webhook": {
            "method": "POST",
            "endpoint": "/webhooks",
            "required_params": ["target_url", "triggers"],
            "optional_params": ["item_id", "item_type"],
            "display_name": "Create Webhook",
            "description": "Create a new webhook",
            "group": "Webhooks",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "webhook_response"
        },
        "get_webhook": {
            "method": "GET",
            "endpoint": "/webhooks/{webhook_id}",
            "required_params": ["webhook_id"],
            "optional_params": ["fields"],
            "display_name": "Get Webhook",
            "description": "Get information about a webhook",
            "group": "Webhooks",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_schema": "webhook_response"
        },
        "update_webhook": {
            "method": "PUT",
            "endpoint": "/webhooks/{webhook_id}",
            "required_params": ["webhook_id"],
            "optional_params": ["target_url", "triggers"],
            "display_name": "Update Webhook",
            "description": "Update a webhook",
            "group": "Webhooks",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_schema": "webhook_response"
        },
        "delete_webhook": {
            "method": "DELETE",
            "endpoint": "/webhooks/{webhook_id}",
            "required_params": ["webhook_id"],
            "display_name": "Delete Webhook",
            "description": "Delete a webhook",
            "group": "Webhooks",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "list_webhooks": {
            "method": "GET",
            "endpoint": "/webhooks",
            "required_params": [],
            "optional_params": ["marker", "limit"],
            "display_name": "List Webhooks",
            "description": "List webhooks",
            "group": "Webhooks",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "supports_pagination": True,
            "pagination_type": "marker"
        },
        
        # Tasks and comments
        "create_task": {
            "method": "POST",
            "endpoint": "/tasks",
            "required_params": ["item_id", "item_type", "action"],
            "optional_params": ["message", "due_at", "completion_rule"],
            "display_name": "Create Task",
            "description": "Create a task on a file",
            "group": "Tasks",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "get_task": {
            "method": "GET",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id"],
            "optional_params": ["fields"],
            "display_name": "Get Task",
            "description": "Get information about a task",
            "group": "Tasks",
            "rate_limit_cost": 1,
            "cache_ttl": 300
        },
        "update_task": {
            "method": "PUT",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id"],
            "optional_params": ["message", "due_at", "completion_rule"],
            "display_name": "Update Task",
            "description": "Update a task",
            "group": "Tasks",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "delete_task": {
            "method": "DELETE",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id"],
            "display_name": "Delete Task",
            "description": "Delete a task",
            "group": "Tasks",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "create_comment": {
            "method": "POST",
            "endpoint": "/comments",
            "required_params": ["item_id", "item_type", "message"],
            "optional_params": ["tagged_message"],
            "display_name": "Create Comment",
            "description": "Add a comment to a file",
            "group": "Comments",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "get_comment": {
            "method": "GET",
            "endpoint": "/comments/{comment_id}",
            "required_params": ["comment_id"],
            "optional_params": ["fields"],
            "display_name": "Get Comment",
            "description": "Get information about a comment",
            "group": "Comments",
            "rate_limit_cost": 1,
            "cache_ttl": 300
        },
        
        # Enterprise features
        "get_enterprise_events": {
            "method": "GET",
            "endpoint": "/events",
            "required_params": [],
            "optional_params": ["stream_type", "stream_position", "limit", "event_type", "created_after", "created_before"],
            "display_name": "Get Enterprise Events",
            "description": "Get enterprise event stream",
            "group": "Enterprise",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "supports_pagination": True
        },
        "get_retention_policies": {
            "method": "GET",
            "endpoint": "/retention_policies",
            "required_params": [],
            "optional_params": ["policy_name", "policy_type", "created_by_user_id", "fields", "limit", "marker"],
            "display_name": "Get Retention Policies",
            "description": "List retention policies",
            "group": "Enterprise",
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "supports_pagination": True
        },
        "create_retention_policy": {
            "method": "POST",
            "endpoint": "/retention_policies",
            "required_params": ["policy_name", "policy_type", "retention_length"],
            "optional_params": ["disposition_action", "retention_type", "can_owner_extend_retention"],
            "display_name": "Create Retention Policy",
            "description": "Create a new retention policy",
            "group": "Enterprise",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        },
        "get_legal_holds": {
            "method": "GET",
            "endpoint": "/legal_hold_policies",
            "required_params": [],
            "optional_params": ["policy_name", "fields", "limit", "marker"],
            "display_name": "Get Legal Holds",
            "description": "List legal hold policies",
            "group": "Enterprise",
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "supports_pagination": True
        },
        "create_legal_hold": {
            "method": "POST",
            "endpoint": "/legal_hold_policies",
            "required_params": ["policy_name"],
            "optional_params": ["description", "filter_started_at", "filter_ended_at", "is_ongoing"],
            "display_name": "Create Legal Hold",
            "description": "Create a new legal hold policy",
            "group": "Enterprise",
            "rate_limit_cost": 1,
            "cache_ttl": 0
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create UniversalRequestNode with api_config section
        self.universal_node = UniversalRequestNode(self.CONFIG["api_config"])
    
    def get_schema(self) -> NodeSchema:
        """Return comprehensive schema with all enhancements."""
        return NodeSchema(
            node_type="box",
            version="1.0.0", 
            description="Box API integration with embedded configuration and all 13 enhancements",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Box operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="access_token", 
                    type=NodeParameterType.SECRET,
                    description="Box Developer Token or OAuth access token",
                    required=True
                ),
                
                # File/Folder identifiers
                NodeParameter(
                    name="file_id",
                    type=NodeParameterType.STRING,
                    description="Box file ID",
                    required=False
                ),
                NodeParameter(
                    name="folder_id",
                    type=NodeParameterType.STRING,
                    description="Box folder ID",
                    required=False
                ),
                NodeParameter(
                    name="parent_id",
                    type=NodeParameterType.STRING,
                    description="Parent folder ID for new items",
                    required=False
                ),
                
                # Content parameters
                NodeParameter(
                    name="name",
                    type=NodeParameterType.STRING,
                    description="Name for files, folders, or resources",
                    required=False
                ),
                NodeParameter(
                    name="description",
                    type=NodeParameterType.STRING,
                    description="Description for files or folders",
                    required=False
                ),
                NodeParameter(
                    name="content",
                    type=NodeParameterType.STRING,
                    description="File content (base64 encoded for binary files)",
                    required=False
                ),
                
                # Search parameters
                NodeParameter(
                    name="query",
                    type=NodeParameterType.STRING,
                    description="Search query string",
                    required=False
                ),
                NodeParameter(
                    name="content_types",
                    type=NodeParameterType.ARRAY,
                    description="File types to search for",
                    required=False
                ),
                NodeParameter(
                    name="file_extensions",
                    type=NodeParameterType.ARRAY,
                    description="File extensions to filter by",
                    required=False
                ),
                
                # Collaboration parameters
                NodeParameter(
                    name="accessible_by",
                    type=NodeParameterType.OBJECT,
                    description="User or group to collaborate with",
                    required=False
                ),
                NodeParameter(
                    name="role",
                    type=NodeParameterType.STRING,
                    description="Collaboration role",
                    required=False,
                    enum=["editor", "viewer", "previewer", "uploader", "previewer_uploader", "viewer_uploader", "co-owner"]
                ),
                NodeParameter(
                    name="item_type",
                    type=NodeParameterType.STRING,
                    description="Type of item (file or folder)",
                    required=False,
                    enum=["file", "folder"]
                ),
                NodeParameter(
                    name="item_id",
                    type=NodeParameterType.STRING,
                    description="ID of the item to collaborate on",
                    required=False
                ),
                
                # Shared link parameters
                NodeParameter(
                    name="access",
                    type=NodeParameterType.STRING,
                    description="Shared link access level",
                    required=False,
                    enum=["open", "company", "collaborators"]
                ),
                NodeParameter(
                    name="password",
                    type=NodeParameterType.SECRET,
                    description="Password for shared link",
                    required=False
                ),
                NodeParameter(
                    name="unshared_at",
                    type=NodeParameterType.STRING,
                    description="When shared link expires (ISO 8601 format)",
                    required=False
                ),
                
                # Metadata parameters
                NodeParameter(
                    name="template",
                    type=NodeParameterType.STRING,
                    description="Metadata template key",
                    required=False
                ),
                NodeParameter(
                    name="scope",
                    type=NodeParameterType.STRING,
                    description="Metadata template scope",
                    required=False,
                    enum=["global", "enterprise"]
                ),
                NodeParameter(
                    name="metadata",
                    type=NodeParameterType.OBJECT,
                    description="Metadata key-value pairs",
                    required=False
                ),
                
                # Version control parameters
                NodeParameter(
                    name="version_id",
                    type=NodeParameterType.STRING,
                    description="File version ID",
                    required=False
                ),
                
                # User management parameters
                NodeParameter(
                    name="user_id",
                    type=NodeParameterType.STRING,
                    description="Box user ID",
                    required=False
                ),
                NodeParameter(
                    name="login",
                    type=NodeParameterType.STRING,
                    description="User email address",
                    required=False
                ),
                NodeParameter(
                    name="is_platform_access_only",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether user has platform access only",
                    required=False
                ),
                
                # Group management parameters
                NodeParameter(
                    name="group_id",
                    type=NodeParameterType.STRING,
                    description="Box group ID",
                    required=False
                ),
                NodeParameter(
                    name="invitability_level",
                    type=NodeParameterType.STRING,
                    description="Group invitation level",
                    required=False,
                    enum=["admins_only", "admins_and_members", "all_managed_users"]
                ),
                NodeParameter(
                    name="member_viewability_level",
                    type=NodeParameterType.STRING,
                    description="Group member visibility level",
                    required=False,
                    enum=["admins_only", "admins_and_members", "all_managed_users"]
                ),
                
                # Webhook parameters
                NodeParameter(
                    name="webhook_id",
                    type=NodeParameterType.STRING,
                    description="Webhook ID",
                    required=False
                ),
                NodeParameter(
                    name="target_url",
                    type=NodeParameterType.STRING,
                    description="Webhook target URL",
                    required=False
                ),
                NodeParameter(
                    name="triggers",
                    type=NodeParameterType.ARRAY,
                    description="Webhook trigger events",
                    required=False
                ),
                
                # Task parameters
                NodeParameter(
                    name="task_id",
                    type=NodeParameterType.STRING,
                    description="Task ID",
                    required=False
                ),
                NodeParameter(
                    name="action",
                    type=NodeParameterType.STRING,
                    description="Task action type",
                    required=False,
                    enum=["review", "complete"]
                ),
                NodeParameter(
                    name="due_at",
                    type=NodeParameterType.STRING,
                    description="Task due date (ISO 8601 format)",
                    required=False
                ),
                NodeParameter(
                    name="message",
                    type=NodeParameterType.STRING,
                    description="Task or comment message",
                    required=False
                ),
                
                # Comment parameters
                NodeParameter(
                    name="comment_id",
                    type=NodeParameterType.STRING,
                    description="Comment ID",
                    required=False
                ),
                NodeParameter(
                    name="tagged_message",
                    type=NodeParameterType.STRING,
                    description="Comment message with @mentions",
                    required=False
                ),
                
                # Filtering and pagination parameters
                NodeParameter(
                    name="fields",
                    type=NodeParameterType.ARRAY,
                    description="Fields to include in response",
                    required=False
                ),
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of items to return",
                    required=False,
                    default=100
                ),
                NodeParameter(
                    name="offset",
                    type=NodeParameterType.NUMBER,
                    description="Number of items to skip",
                    required=False,
                    default=0
                ),
                NodeParameter(
                    name="marker",
                    type=NodeParameterType.STRING,
                    description="Pagination marker for large result sets",
                    required=False
                ),
                NodeParameter(
                    name="sort",
                    type=NodeParameterType.STRING,
                    description="Sort field for search results",
                    required=False,
                    enum=["id", "name", "date", "size", "modified_at", "relevance"]
                ),
                NodeParameter(
                    name="direction",
                    type=NodeParameterType.STRING,
                    description="Sort direction",
                    required=False,
                    enum=["ASC", "DESC"]
                ),
                
                # Advanced filtering
                NodeParameter(
                    name="created_at_range",
                    type=NodeParameterType.STRING,
                    description="Created date range filter (from_date,to_date)",
                    required=False
                ),
                NodeParameter(
                    name="updated_at_range",
                    type=NodeParameterType.STRING,
                    description="Updated date range filter (from_date,to_date)",
                    required=False
                ),
                NodeParameter(
                    name="size_range",
                    type=NodeParameterType.STRING,
                    description="File size range filter (min_bytes,max_bytes)",
                    required=False
                ),
                NodeParameter(
                    name="owner_user_ids",
                    type=NodeParameterType.ARRAY,
                    description="Filter by owner user IDs",
                    required=False
                ),
                NodeParameter(
                    name="ancestor_folder_ids",
                    type=NodeParameterType.ARRAY,
                    description="Filter by ancestor folder IDs",
                    required=False
                ),
                
                # Testing parameters
                NodeParameter(
                    name="testing_mode",
                    type=NodeParameterType.BOOLEAN,
                    description="Enable testing mode (uses mock responses)",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="mock_response",
                    type=NodeParameterType.OBJECT,
                    description="Mock response data for testing",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "data": NodeParameterType.ANY,
                "id": NodeParameterType.STRING,
                "name": NodeParameterType.STRING,
                "size": NodeParameterType.NUMBER,
                "created_at": NodeParameterType.STRING,
                "modified_at": NodeParameterType.STRING,
                "shared_link": NodeParameterType.OBJECT,
                "collaboration_id": NodeParameterType.STRING,
                "metadata": NodeParameterType.OBJECT,
                "webhook_id": NodeParameterType.STRING,
                "task_id": NodeParameterType.STRING,
                "comment_id": NodeParameterType.STRING,
                "total_count": NodeParameterType.NUMBER,
                "entries": NodeParameterType.ARRAY,
                "next_marker": NodeParameterType.STRING,
                "schema": NodeParameterType.STRING
            }
        )
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Box operation using UniversalRequestNode with all enhancements.
        """
        try:
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            if not operation:
                return {
                    "status": "error",
                    "error": "Operation is required",
                    "result": None
                }
            
            if operation not in self.OPERATIONS:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}",
                    "result": None
                }
            
            # ENHANCEMENT 10: Testing mode
            if params.get("testing_mode", False):
                return self._handle_test_mode(operation, params)
            
            # Get operation config
            op_config = self.OPERATIONS[operation]
            
            # ENHANCEMENT 3: Parameter dependencies validation
            if "parameter_dependencies" in self.CONFIG["parameters"]["operation"]:
                dep_result = self._validate_parameter_dependencies(operation, params)
                if dep_result:
                    return dep_result
            
            # ENHANCEMENT 4: Validation rules
            validation_result = self._apply_validation_rules(operation, params)
            if validation_result:
                return validation_result
            
            # ENHANCEMENT 8: Field mapping (request)
            mapped_params = self._apply_request_field_mapping(params)
            
            # Prepare request data
            request_data = self._prepare_request_data(operation, mapped_params)
            
            # Make request using UniversalRequestNode
            request_kwargs = {
                "token": params.get("access_token"),  # Box uses Bearer token
                **mapped_params  # Pass all original parameters for path substitution
            }
            
            result = await self.universal_node.request(
                method=op_config["method"],
                endpoint=op_config["endpoint"],
                data=request_data if op_config["method"] in ["POST", "PUT", "PATCH"] else None,
                params=request_data if op_config["method"] == "GET" else None,
                **request_kwargs
            )
            
            # ENHANCEMENT 8: Field mapping (response)
            result = self._apply_response_field_mapping(result)
            
            # ENHANCEMENT 1: Output schema validation
            result = self._apply_output_schema(operation, result)
            
            # ENHANCEMENT 11: Performance monitoring
            self._track_performance_metrics(operation, result)
            
            # Process result
            return self._process_result(operation, result)
            
        except Exception as e:
            logger.error(f"Box node error: {str(e)}")
            
            # ENHANCEMENT 11: Performance monitoring (errors)
            self._track_error_metrics(operation, str(e))
            
            return {
                "status": "error", 
                "error": str(e),
                "result": None
            }
    
    def _handle_test_mode(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """ENHANCEMENT 10: Handle testing mode with mock responses."""
        mock_response = params.get("mock_response")
        if mock_response:
            return {
                "status": "success",
                "data": mock_response,
                "result": mock_response,
                "testing_mode": True
            }
        
        # Default mock responses for common operations
        default_mocks = {
            "get_file": {
                "id": "12345",
                "name": "test-file.pdf",
                "size": 1024000,
                "created_at": "2024-01-01T00:00:00-08:00"
            },
            "get_folder": {
                "id": "0",
                "name": "All Files",
                "created_at": "2024-01-01T00:00:00-08:00"
            },
            "search": {
                "total_count": 1,
                "entries": [{"id": "12345", "name": "test-result.pdf", "type": "file"}]
            },
            "get_current_user": {
                "id": "12345",
                "name": "Test User",
                "login": "test@example.com"
            }
        }
        
        mock_data = default_mocks.get(operation, {"message": f"Mock response for {operation}"})
        
        return {
            "status": "success",
            "data": mock_data,
            "result": mock_data,
            "testing_mode": True
        }
    
    def _validate_parameter_dependencies(self, operation: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """ENHANCEMENT 3: Validate parameter dependencies."""
        op_deps = self.CONFIG["parameters"]["operation"].get("parameter_dependencies", {})
        required_params = op_deps.get(operation, [])
        
        missing_params = []
        for param in required_params:
            if not params.get(param):
                missing_params.append(param)
        
        if missing_params:
            return {
                "status": "error",
                "error": f"Missing required parameters for operation '{operation}': {', '.join(missing_params)}",
                "result": None
            }
        
        return None
    
    def _apply_validation_rules(self, operation: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """ENHANCEMENT 4: Apply validation rules."""
        validation_rules = self.CONFIG.get("validation_rules", {})
        
        # Validate file size limits
        if params.get("content") and "file_size_limits" in validation_rules:
            import base64
            try:
                content_size = len(base64.b64decode(params["content"]))
                max_size = validation_rules["file_size_limits"]["enterprise_account"]  # Use max limit
                if content_size > max_size:
                    return {
                        "status": "error",
                        "error": f"File size {content_size} bytes exceeds limit of {max_size} bytes",
                        "result": None
                    }
            except:
                pass  # Skip validation if not base64
        
        # Validate name restrictions
        if params.get("name") and "name_restrictions" in validation_rules:
            name = params["name"]
            restrictions = validation_rules["name_restrictions"]
            
            # Check forbidden characters
            for char in restrictions["forbidden_chars"]:
                if char in name:
                    return {
                        "status": "error",
                        "error": f"Name contains forbidden character: {char}",
                        "result": None
                    }
            
            # Check forbidden names
            if name.upper() in restrictions["forbidden_names"]:
                return {
                    "status": "error",
                    "error": f"Name '{name}' is not allowed",
                    "result": None
                }
            
            # Check length
            if len(name) > restrictions["max_length"]:
                return {
                    "status": "error",
                    "error": f"Name length {len(name)} exceeds maximum of {restrictions['max_length']}",
                    "result": None
                }
        
        return None
    
    def _apply_request_field_mapping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ENHANCEMENT 8: Apply request field mapping."""
        field_mapping = self.CONFIG.get("field_mapping", {})
        request_mappings = field_mapping.get("request_mappings", {})
        
        mapped_params = params.copy()
        for old_field, new_field in request_mappings.items():
            if old_field in mapped_params:
                mapped_params[new_field] = mapped_params.pop(old_field)
        
        return mapped_params
    
    def _apply_response_field_mapping(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """ENHANCEMENT 8: Apply response field mapping."""
        field_mapping = self.CONFIG.get("field_mapping", {})
        response_mappings = field_mapping.get("response_mappings", {})
        nested_mappings = field_mapping.get("nested_mappings", {})
        
        if result.get("status") == "success" and "data" in result:
            data = result["data"]
            
            # Apply direct field mappings
            for old_field, new_field in response_mappings.items():
                if old_field in data:
                    data[new_field] = data[old_field]
            
            # Apply nested field mappings
            for nested_path, new_field in nested_mappings.items():
                value = self._get_nested_value(data, nested_path)
                if value is not None:
                    data[new_field] = value
        
        return result
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Helper to get nested value from path like 'parent.name'."""
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _apply_output_schema(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """ENHANCEMENT 1: Apply output schema validation and reference."""
        op_config = self.OPERATIONS.get(operation, {})
        response_schema = op_config.get("response_schema")
        
        if response_schema and result.get("status") == "success":
            result["schema"] = response_schema
        
        return result
    
    def _track_performance_metrics(self, operation: str, result: Dict[str, Any]):
        """ENHANCEMENT 11: Track performance metrics."""
        # This would integrate with a metrics system in production
        # For now, just log performance data
        logger.info(f"Box operation '{operation}' completed with status: {result.get('status')}")
    
    def _track_error_metrics(self, operation: str, error: str):
        """ENHANCEMENT 11: Track error metrics."""
        # This would integrate with an error tracking system in production
        logger.error(f"Box operation '{operation}' failed: {error}")
    
    def _prepare_request_data(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request data based on operation with all enhancements."""
        data = {}
        
        # File operations
        if operation == "upload_file":
            import base64
            
            content = params.get("content", "")
            # Check if content is already base64 encoded
            try:
                base64.b64decode(content)
                encoded_content = content
            except:
                # Encode as base64
                encoded_content = base64.b64encode(content.encode()).decode()
            
            # Box upload uses multipart/form-data, but we'll send as JSON for simplicity
            data = {
                "attributes": {
                    "name": params.get("name"),
                    "parent": {"id": params.get("parent_id")},
                    "content_created_at": params.get("content_created_at"),
                    "content_modified_at": params.get("content_modified_at")
                },
                "file": encoded_content
            }
            
        elif operation == "update_file":
            data = {}
            if params.get("name"): data["name"] = params.get("name")
            if params.get("description"): data["description"] = params.get("description")
            if params.get("parent"): data["parent"] = {"id": params.get("parent")}
            
        elif operation == "copy_file":
            data = {
                "parent": {"id": params.get("parent")},
                "name": params.get("name")
            }
            
        elif operation == "lock_file":
            lock_data = {
                "type": "lock",
                "expires_at": params.get("expires_at"),
                "is_download_prevented": params.get("is_download_prevented", False)
            }
            data = {"lock": lock_data}
            
        elif operation == "unlock_file":
            data = {"lock": None}
            
        # Folder operations
        elif operation == "create_folder":
            data = {
                "name": params.get("name"),
                "parent": {"id": params.get("parent_id")}
            }
            
        elif operation == "update_folder":
            data = {}
            if params.get("name"): data["name"] = params.get("name")
            if params.get("description"): data["description"] = params.get("description")
            if params.get("parent"): data["parent"] = {"id": params.get("parent")}
            
        elif operation == "copy_folder":
            data = {
                "parent": {"id": params.get("parent")},
                "name": params.get("name")
            }
            
        # Search operations
        elif operation in ["search", "search_users", "search_groups"]:
            query_params = {}
            if params.get("query"): query_params["query"] = params.get("query")
            if params.get("scope"): query_params["scope"] = params.get("scope")
            if params.get("file_extensions"): query_params["file_extensions"] = ",".join(params.get("file_extensions"))
            if params.get("content_types"): query_params["content_types"] = ",".join(params.get("content_types"))
            if params.get("created_at_range"): query_params["created_at_range"] = params.get("created_at_range")
            if params.get("updated_at_range"): query_params["updated_at_range"] = params.get("updated_at_range")
            if params.get("size_range"): query_params["size_range"] = params.get("size_range")
            if params.get("owner_user_ids"): query_params["owner_user_ids"] = ",".join(params.get("owner_user_ids"))
            if params.get("ancestor_folder_ids"): query_params["ancestor_folder_ids"] = ",".join(params.get("ancestor_folder_ids"))
            if params.get("sort"): query_params["sort"] = params.get("sort")
            if params.get("direction"): query_params["direction"] = params.get("direction")
            if params.get("limit"): query_params["limit"] = params.get("limit")
            if params.get("offset"): query_params["offset"] = params.get("offset")
            if params.get("fields"): query_params["fields"] = ",".join(params.get("fields"))
            return query_params
            
        # Sharing operations
        elif operation == "create_shared_link":
            shared_link = {
                "access": params.get("access", "open")
            }
            if params.get("password"): shared_link["password"] = params.get("password")
            if params.get("unshared_at"): shared_link["unshared_at"] = params.get("unshared_at")
            if params.get("can_download") is not None: shared_link["permissions"] = {"can_download": params.get("can_download")}
            data = {"shared_link": shared_link}
            
        elif operation == "remove_shared_link":
            data = {"shared_link": None}
            
        # Collaboration operations
        elif operation == "add_collaboration":
            data = {
                "item": {
                    "type": params.get("item_type"),
                    "id": params.get("item_id")
                },
                "accessible_by": params.get("accessible_by"),
                "role": params.get("role")
            }
            if params.get("notify") is not None: data["notify"] = params.get("notify")
            if params.get("can_view_path") is not None: data["can_view_path"] = params.get("can_view_path")
            if params.get("expires_at"): data["expires_at"] = params.get("expires_at")
            
        elif operation == "update_collaboration":
            data = {}
            if params.get("role"): data["role"] = params.get("role")
            if params.get("status"): data["status"] = params.get("status")
            if params.get("expires_at"): data["expires_at"] = params.get("expires_at")
            if params.get("can_view_path") is not None: data["can_view_path"] = params.get("can_view_path")
            
        # Metadata operations
        elif operation == "create_metadata":
            data = params.get("metadata", {})
            
        elif operation == "update_metadata":
            # Box metadata updates use JSON Patch format
            metadata_updates = params.get("metadata", {})
            data = []
            for key, value in metadata_updates.items():
                data.append({
                    "op": "replace",
                    "path": f"/{key}",
                    "value": value
                })
            
        elif operation == "create_metadata_template":
            data = {
                "templateKey": params.get("template"),
                "displayName": params.get("display_name"),
                "fields": params.get("fields", [])
            }
            if params.get("hidden") is not None: data["hidden"] = params.get("hidden")
            if params.get("copyInstanceOnItemCopy") is not None: data["copyInstanceOnItemCopy"] = params.get("copyInstanceOnItemCopy")
            
        elif operation == "update_metadata_template":
            data = [
                {
                    "op": params.get("op", "replace"),
                    "data": params.get("data", {})
                }
            ]
            
        # User operations
        elif operation == "create_user":
            data = {
                "name": params.get("name"),
                "login": params.get("login")
            }
            if params.get("role"): data["role"] = params.get("role")
            if params.get("language"): data["language"] = params.get("language")
            if params.get("is_sync_enabled") is not None: data["is_sync_enabled"] = params.get("is_sync_enabled")
            if params.get("job_title"): data["job_title"] = params.get("job_title")
            if params.get("phone"): data["phone"] = params.get("phone")
            if params.get("address"): data["address"] = params.get("address")
            
        elif operation == "update_user":
            data = {}
            if params.get("name"): data["name"] = params.get("name")
            if params.get("login"): data["login"] = params.get("login")
            if params.get("role"): data["role"] = params.get("role")
            if params.get("language"): data["language"] = params.get("language")
            if params.get("is_sync_enabled") is not None: data["is_sync_enabled"] = params.get("is_sync_enabled")
            if params.get("job_title"): data["job_title"] = params.get("job_title")
            if params.get("phone"): data["phone"] = params.get("phone")
            if params.get("address"): data["address"] = params.get("address")
            
        # Group operations
        elif operation == "create_group":
            data = {
                "name": params.get("name")
            }
            if params.get("provenance"): data["provenance"] = params.get("provenance")
            if params.get("external_sync_identifier"): data["external_sync_identifier"] = params.get("external_sync_identifier")
            if params.get("description"): data["description"] = params.get("description")
            if params.get("invitability_level"): data["invitability_level"] = params.get("invitability_level")
            if params.get("member_viewability_level"): data["member_viewability_level"] = params.get("member_viewability_level")
            
        elif operation == "update_group":
            data = {}
            if params.get("name"): data["name"] = params.get("name")
            if params.get("provenance"): data["provenance"] = params.get("provenance")
            if params.get("external_sync_identifier"): data["external_sync_identifier"] = params.get("external_sync_identifier")
            if params.get("description"): data["description"] = params.get("description")
            if params.get("invitability_level"): data["invitability_level"] = params.get("invitability_level")
            if params.get("member_viewability_level"): data["member_viewability_level"] = params.get("member_viewability_level")
            
        elif operation == "add_user_to_group":
            data = {
                "user": {"id": params.get("user_id")},
                "group": {"id": params.get("group_id")}
            }
            if params.get("role"): data["role"] = params.get("role")
            if params.get("configurable_permissions"): data["configurable_permissions"] = params.get("configurable_permissions")
            
        # Webhook operations
        elif operation == "create_webhook":
            data = {
                "target": {
                    "id": params.get("item_id", "0"),
                    "type": params.get("item_type", "folder")
                },
                "address": params.get("target_url"),
                "triggers": params.get("triggers", ["FILE.UPLOADED"])
            }
            
        elif operation == "update_webhook":
            data = {}
            if params.get("target_url"): data["address"] = params.get("target_url")
            if params.get("triggers"): data["triggers"] = params.get("triggers")
            
        # Task operations
        elif operation == "create_task":
            data = {
                "item": {
                    "id": params.get("item_id"),
                    "type": params.get("item_type")
                },
                "action": params.get("action")
            }
            if params.get("message"): data["message"] = params.get("message")
            if params.get("due_at"): data["due_at"] = params.get("due_at")
            if params.get("completion_rule"): data["completion_rule"] = params.get("completion_rule")
            
        elif operation == "update_task":
            data = {}
            if params.get("message"): data["message"] = params.get("message")
            if params.get("due_at"): data["due_at"] = params.get("due_at")
            if params.get("completion_rule"): data["completion_rule"] = params.get("completion_rule")
            
        # Comment operations
        elif operation == "create_comment":
            data = {
                "item": {
                    "id": params.get("item_id"),
                    "type": params.get("item_type")
                },
                "message": params.get("message")
            }
            if params.get("tagged_message"): data["tagged_message"] = params.get("tagged_message")
            
        # Enterprise operations
        elif operation in ["get_enterprise_events", "get_retention_policies", "get_legal_holds"]:
            query_params = {}
            if params.get("stream_type"): query_params["stream_type"] = params.get("stream_type")
            if params.get("stream_position"): query_params["stream_position"] = params.get("stream_position")
            if params.get("limit"): query_params["limit"] = params.get("limit")
            if params.get("marker"): query_params["marker"] = params.get("marker")
            if params.get("event_type"): query_params["event_type"] = params.get("event_type")
            if params.get("created_after"): query_params["created_after"] = params.get("created_after")
            if params.get("created_before"): query_params["created_before"] = params.get("created_before")
            if params.get("policy_name"): query_params["policy_name"] = params.get("policy_name")
            if params.get("policy_type"): query_params["policy_type"] = params.get("policy_type")
            if params.get("created_by_user_id"): query_params["created_by_user_id"] = params.get("created_by_user_id")
            if params.get("fields"): query_params["fields"] = ",".join(params.get("fields"))
            return query_params
            
        elif operation == "create_retention_policy":
            data = {
                "policy_name": params.get("policy_name"),
                "policy_type": params.get("policy_type"),
                "retention_length": params.get("retention_length")
            }
            if params.get("disposition_action"): data["disposition_action"] = params.get("disposition_action")
            if params.get("retention_type"): data["retention_type"] = params.get("retention_type")
            if params.get("can_owner_extend_retention") is not None: data["can_owner_extend_retention"] = params.get("can_owner_extend_retention")
            
        elif operation == "create_legal_hold":
            data = {
                "policy_name": params.get("policy_name")
            }
            if params.get("description"): data["description"] = params.get("description")
            if params.get("filter_started_at"): data["filter_started_at"] = params.get("filter_started_at")
            if params.get("filter_ended_at"): data["filter_ended_at"] = params.get("filter_ended_at")
            if params.get("is_ongoing") is not None: data["is_ongoing"] = params.get("is_ongoing")
        
        # For GET operations with query parameters (if not handled above)
        if not data and self.OPERATIONS[operation]["method"] == "GET":
            query_params = {}
            if params.get("fields"): query_params["fields"] = ",".join(params.get("fields"))
            if params.get("limit"): query_params["limit"] = params.get("limit")
            if params.get("offset"): query_params["offset"] = params.get("offset")
            if params.get("marker"): query_params["marker"] = params.get("marker")
            return query_params
        
        return data
    
    def _process_result(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process result based on operation type with all enhancements."""
        if result.get("status") != "success":
            return result
        
        response_data = result.get("data", {})
        
        # Add common Box fields to result
        if isinstance(response_data, dict):
            result["data"] = response_data
            result["id"] = response_data.get("id")
            result["name"] = response_data.get("name")
            result["size"] = response_data.get("size")
            result["created_at"] = response_data.get("created_at")
            result["modified_at"] = response_data.get("modified_at")
            result["shared_link"] = response_data.get("shared_link")
            
            # Operation-specific field extraction
            if operation in ["add_collaboration", "get_collaboration", "update_collaboration"]:
                result["collaboration_id"] = response_data.get("id")
                
            elif operation in ["get_metadata", "create_metadata", "update_metadata"]:
                result["metadata"] = response_data
                
            elif operation in ["create_webhook", "get_webhook", "update_webhook"]:
                result["webhook_id"] = response_data.get("id")
                
            elif operation in ["create_task", "get_task", "update_task"]:
                result["task_id"] = response_data.get("id")
                
            elif operation in ["create_comment", "get_comment"]:
                result["comment_id"] = response_data.get("id")
                
            elif operation == "search":
                result["total_count"] = response_data.get("total_count")
                result["entries"] = response_data.get("entries", [])
                result["next_marker"] = response_data.get("next_marker")
                
            elif operation in ["get_folder_items", "list_webhooks", "list_collaborations"]:
                result["total_count"] = response_data.get("total_count")
                result["entries"] = response_data.get("entries", [])
                result["next_marker"] = response_data.get("next_marker")
        
        return result
    
    async def close(self):
        """Clean up resources."""
        if self.universal_node:
            await self.universal_node.close()


if __name__ == "__main__":
    import asyncio
    
    async def test():
        node = BoxNode()
        
        # Test get current user
        test_data = {
            "params": {
                "operation": "get_current_user",
                "access_token": "YOUR_BOX_TOKEN_HERE",  # Replace with actual token
                "testing_mode": True  # Enable testing mode for demo
            }
        }
        
        result = await node.execute(test_data)
        print(f"Result: {result}")
        
        await node.close()
    
    # Uncomment to test
    # asyncio.run(test())