"""
OneDrive Node - Unified implementation using UniversalRequestNode
Provides comprehensive integration with Microsoft Graph OneDrive API for files, folders, drives, sharing, and content management.
"""

import logging
from typing import Dict, Any, List, Optional
from urllib.parse import quote
import base64

try:
    from universal_request_node import UniversalRequestNode
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    except ImportError:
        from universal_request_node import UniversalRequestNode
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )

# Configure logging
logger = logging.getLogger(__name__)

class OneDriveNode(BaseNode):
    """
    Unified OneDrive Node using UniversalRequestNode for Microsoft Graph OneDrive API integration.
    Provides comprehensive functionality for files, folders, drives, sharing, and content management.
    """
    
    # Configuration for Microsoft Graph OneDrive API
    CONFIG = {
        "base_url": "https://graph.microsoft.com/v1.0",
        "auth_url": "https://login.microsoftonline.com",
        "authentication": {
            "type": "oauth2_client_credentials",
            "token_url": "/{tenant_id}/oauth2/v2.0/token",
            "token_params": {
                "grant_type": "client_credentials",
                "scope": "https://graph.microsoft.com/.default"
            }
        },
        "default_headers": {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        "retry_config": {
            "max_retries": 3,
            "backoff_factor": 1.0,
            "retry_on_status": [429, 500, 502, 503, 504]
        },
        "rate_limiting": {
            "requests_per_second": 10,
            "requests_per_minute": 600
        },
        "timeouts": {
            "connect": 30,
            "read": 300,
            "total": 600
        }
    }
    
    # Operations mapping for Microsoft Graph OneDrive API
    OPERATIONS = {
        # Authentication
        "get_access_token": {
            "method": "POST",
            "endpoint": "oauth2/v2.0/token",
            "required_params": ["client_id", "client_secret", "tenant_id"]
        },
        
        # Drive Operations
        "get_drive": {
            "method": "GET", 
            "endpoint": "drives/{drive_id}",
            "required_params": [],
            "path_params": ["drive_id"]
        },
        "get_user_drive": {
            "method": "GET",
            "endpoint": "users/{user_id}/drive",
            "required_params": [],
            "path_params": ["user_id"]
        },
        "list_drives": {
            "method": "GET",
            "endpoint": "users/{user_id}/drives", 
            "required_params": [],
            "path_params": ["user_id"]
        },
        "get_my_drive": {
            "method": "GET",
            "endpoint": "me/drive",
            "required_params": []
        },
        
        # DriveItem Operations - Core
        "get_item": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}",
            "required_params": ["item_id"],
            "path_params": ["drive_id", "item_id"]
        },
        "get_item_by_path": {
            "method": "GET", 
            "endpoint": "drives/{drive_id}/root:/{item_path}:",
            "required_params": ["item_path"],
            "path_params": ["drive_id", "item_path"]
        },
        "get_my_item": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}",
            "required_params": ["item_id"],
            "path_params": ["item_id"]
        },
        "get_my_item_by_path": {
            "method": "GET",
            "endpoint": "me/drive/root:/{item_path}:",
            "required_params": ["item_path"], 
            "path_params": ["item_path"]
        },
        "create_folder": {
            "method": "POST",
            "endpoint": "drives/{drive_id}/items/{parent_id}/children",
            "required_params": ["folder_name"],
            "path_params": ["drive_id", "parent_id"]
        },
        "create_my_folder": {
            "method": "POST",
            "endpoint": "me/drive/items/{parent_id}/children",
            "required_params": ["folder_name"],
            "path_params": ["parent_id"]
        },
        "update_item": {
            "method": "PATCH",
            "endpoint": "drives/{drive_id}/items/{item_id}",
            "required_params": ["item_id", "request_body"],
            "path_params": ["drive_id", "item_id"]
        },
        "update_my_item": {
            "method": "PATCH",
            "endpoint": "me/drive/items/{item_id}",
            "required_params": ["item_id", "request_body"],
            "path_params": ["item_id"]
        },
        "delete_item": {
            "method": "DELETE",
            "endpoint": "drives/{drive_id}/items/{item_id}",
            "required_params": ["item_id"],
            "path_params": ["drive_id", "item_id"]
        },
        "delete_my_item": {
            "method": "DELETE",
            "endpoint": "me/drive/items/{item_id}",
            "required_params": ["item_id"],
            "path_params": ["item_id"]
        },
        "permanently_delete_item": {
            "method": "POST",
            "endpoint": "drives/{drive_id}/items/{item_id}/permanentDelete",
            "required_params": ["item_id"],
            "path_params": ["drive_id", "item_id"]
        },
        "permanently_delete_my_item": {
            "method": "POST",
            "endpoint": "me/drive/items/{item_id}/permanentDelete",
            "required_params": ["item_id"],
            "path_params": ["item_id"]
        },
        
        # DriveItem Operations - Content
        "upload_content": {
            "method": "PUT",
            "endpoint": "drives/{drive_id}/root:/{item_path}:/content",
            "required_params": ["item_path", "content"],
            "path_params": ["drive_id", "item_path"]
        },
        "upload_my_content": {
            "method": "PUT", 
            "endpoint": "me/drive/root:/{item_path}:/content",
            "required_params": ["item_path", "content"],
            "path_params": ["item_path"]
        },
        "download_content": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}/content",
            "required_params": ["item_id"],
            "path_params": ["drive_id", "item_id"]
        },
        "download_my_content": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}/content",
            "required_params": ["item_id"],
            "path_params": ["item_id"]
        },
        "create_upload_session": {
            "method": "POST",
            "endpoint": "drives/{drive_id}/root:/{item_path}:/createUploadSession",
            "required_params": ["item_path"],
            "path_params": ["drive_id", "item_path"]
        },
        "create_my_upload_session": {
            "method": "POST",
            "endpoint": "me/drive/root:/{item_path}:/createUploadSession",
            "required_params": ["item_path"],
            "path_params": ["item_path"]
        },
        
        # DriveItem Operations - Advanced
        "copy_item": {
            "method": "POST",
            "endpoint": "drives/{drive_id}/items/{item_id}/copy",
            "required_params": ["item_id", "parent_reference"],
            "path_params": ["drive_id", "item_id"]
        },
        "copy_my_item": {
            "method": "POST",
            "endpoint": "me/drive/items/{item_id}/copy",
            "required_params": ["item_id", "parent_reference"],
            "path_params": ["item_id"]
        },
        "move_item": {
            "method": "PATCH",
            "endpoint": "drives/{drive_id}/items/{item_id}",
            "required_params": ["item_id", "parent_reference"],
            "path_params": ["drive_id", "item_id"]
        },
        "move_my_item": {
            "method": "PATCH",
            "endpoint": "me/drive/items/{item_id}",
            "required_params": ["item_id", "parent_reference"],
            "path_params": ["item_id"]
        },
        "restore_item": {
            "method": "POST",
            "endpoint": "drives/{drive_id}/items/{item_id}/restore",
            "required_params": ["item_id"],
            "path_params": ["drive_id", "item_id"]
        },
        "restore_my_item": {
            "method": "POST",
            "endpoint": "me/drive/items/{item_id}/restore",
            "required_params": ["item_id"],
            "path_params": ["item_id"]
        },
        
        # Children Operations
        "list_children": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}/children",
            "required_params": ["item_id"],
            "path_params": ["drive_id", "item_id"]
        },
        "list_my_children": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}/children",
            "required_params": ["item_id"],
            "path_params": ["item_id"]
        },
        "list_root_children": {
            "method": "GET",
            "endpoint": "me/drive/root/children",
            "required_params": []
        },
        "add_child": {
            "method": "POST",
            "endpoint": "drives/{drive_id}/items/{item_id}/children",
            "required_params": ["item_id", "request_body"],
            "path_params": ["drive_id", "item_id"]
        },
        "add_my_child": {
            "method": "POST",
            "endpoint": "me/drive/items/{item_id}/children",
            "required_params": ["item_id", "request_body"],
            "path_params": ["item_id"]
        },
        
        # Versions Operations
        "list_versions": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}/versions",
            "required_params": ["item_id"],
            "path_params": ["drive_id", "item_id"]
        },
        "list_my_versions": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}/versions",
            "required_params": ["item_id"],
            "path_params": ["item_id"]
        },
        "get_version": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}/versions/{version_id}",
            "required_params": ["item_id", "version_id"],
            "path_params": ["drive_id", "item_id", "version_id"]
        },
        "get_my_version": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}/versions/{version_id}",
            "required_params": ["item_id", "version_id"],
            "path_params": ["item_id", "version_id"]
        },
        "restore_version": {
            "method": "POST",
            "endpoint": "drives/{drive_id}/items/{item_id}/versions/{version_id}/restoreVersion",
            "required_params": ["item_id", "version_id"],
            "path_params": ["drive_id", "item_id", "version_id"]
        },
        "restore_my_version": {
            "method": "POST",
            "endpoint": "me/drive/items/{item_id}/versions/{version_id}/restoreVersion",
            "required_params": ["item_id", "version_id"],
            "path_params": ["item_id", "version_id"]
        },
        
        # Permissions Operations
        "list_permissions": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}/permissions",
            "required_params": ["item_id"],
            "path_params": ["drive_id", "item_id"]
        },
        "list_my_permissions": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}/permissions",
            "required_params": ["item_id"],
            "path_params": ["item_id"]
        },
        "get_permission": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}/permissions/{permission_id}",
            "required_params": ["item_id", "permission_id"],
            "path_params": ["drive_id", "item_id", "permission_id"]
        },
        "get_my_permission": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}/permissions/{permission_id}",
            "required_params": ["item_id", "permission_id"],
            "path_params": ["item_id", "permission_id"]
        },
        "create_permission": {
            "method": "POST",
            "endpoint": "drives/{drive_id}/items/{item_id}/permissions",
            "required_params": ["item_id", "request_body"],
            "path_params": ["drive_id", "item_id"]
        },
        "create_my_permission": {
            "method": "POST",
            "endpoint": "me/drive/items/{item_id}/permissions",
            "required_params": ["item_id", "request_body"],
            "path_params": ["item_id"]
        },
        "update_permission": {
            "method": "PATCH",
            "endpoint": "drives/{drive_id}/items/{item_id}/permissions/{permission_id}",
            "required_params": ["item_id", "permission_id", "request_body"],
            "path_params": ["drive_id", "item_id", "permission_id"]
        },
        "update_my_permission": {
            "method": "PATCH",
            "endpoint": "me/drive/items/{item_id}/permissions/{permission_id}",
            "required_params": ["item_id", "permission_id", "request_body"],
            "path_params": ["item_id", "permission_id"]
        },
        "delete_permission": {
            "method": "DELETE",
            "endpoint": "drives/{drive_id}/items/{item_id}/permissions/{permission_id}",
            "required_params": ["item_id", "permission_id"],
            "path_params": ["drive_id", "item_id", "permission_id"]
        },
        "delete_my_permission": {
            "method": "DELETE",
            "endpoint": "me/drive/items/{item_id}/permissions/{permission_id}",
            "required_params": ["item_id", "permission_id"],
            "path_params": ["item_id", "permission_id"]
        },
        
        # Sharing Operations
        "create_sharing_link": {
            "method": "POST",
            "endpoint": "drives/{drive_id}/items/{item_id}/createLink",
            "required_params": ["item_id", "sharing_type"],
            "path_params": ["drive_id", "item_id"]
        },
        "create_my_sharing_link": {
            "method": "POST",
            "endpoint": "me/drive/items/{item_id}/createLink",
            "required_params": ["item_id", "sharing_type"],
            "path_params": ["item_id"]
        },
        "send_sharing_invitation": {
            "method": "POST",
            "endpoint": "drives/{drive_id}/items/{item_id}/invite",
            "required_params": ["item_id", "recipients"],
            "path_params": ["drive_id", "item_id"]
        },
        "send_my_sharing_invitation": {
            "method": "POST",
            "endpoint": "me/drive/items/{item_id}/invite",
            "required_params": ["item_id", "recipients"],
            "path_params": ["item_id"]
        },
        
        # Search Operations
        "search_items": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/search(q='{search_query}')",
            "required_params": ["search_query"],
            "path_params": ["drive_id", "search_query"]
        },
        "search_my_items": {
            "method": "GET",
            "endpoint": "me/drive/search(q='{search_query}')",
            "required_params": ["search_query"],
            "path_params": ["search_query"]
        },
        
        # Thumbnails Operations
        "list_thumbnails": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}/thumbnails",
            "required_params": ["item_id"],
            "path_params": ["drive_id", "item_id"]
        },
        "list_my_thumbnails": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}/thumbnails",
            "required_params": ["item_id"],
            "path_params": ["item_id"]
        },
        "get_thumbnail": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}/thumbnails/{thumbnail_set_id}/{thumbnail_size}",
            "required_params": ["item_id", "thumbnail_set_id"],
            "path_params": ["drive_id", "item_id", "thumbnail_set_id", "thumbnail_size"]
        },
        "get_my_thumbnail": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}/thumbnails/{thumbnail_set_id}/{thumbnail_size}",
            "required_params": ["item_id", "thumbnail_set_id"],
            "path_params": ["item_id", "thumbnail_set_id", "thumbnail_size"]
        },
        
        # Special Folders Operations
        "get_special_folder": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/special/{special_folder}",
            "required_params": ["special_folder"],
            "path_params": ["drive_id", "special_folder"]
        },
        "get_my_special_folder": {
            "method": "GET",
            "endpoint": "me/drive/special/{special_folder}",
            "required_params": ["special_folder"],
            "path_params": ["special_folder"]
        },
        
        # Delta Operations
        "get_delta": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/root/delta",
            "required_params": [],
            "path_params": ["drive_id"]
        },
        "get_my_delta": {
            "method": "GET",
            "endpoint": "me/drive/root/delta",
            "required_params": []
        },
        
        # Workbook Operations (Excel)
        "get_workbook": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}/workbook",
            "required_params": ["item_id"],
            "path_params": ["drive_id", "item_id"]
        },
        "get_my_workbook": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}/workbook",
            "required_params": ["item_id"],
            "path_params": ["item_id"]
        },
        
        # Activities Operations
        "list_activities": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}/activities",
            "required_params": ["item_id"],
            "path_params": ["drive_id", "item_id"]
        },
        "list_my_activities": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}/activities",
            "required_params": ["item_id"],
            "path_params": ["item_id"]
        },
        "get_activity": {
            "method": "GET",
            "endpoint": "drives/{drive_id}/items/{item_id}/activities/{activity_id}",
            "required_params": ["item_id", "activity_id"],
            "path_params": ["drive_id", "item_id", "activity_id"]
        },
        "get_my_activity": {
            "method": "GET",
            "endpoint": "me/drive/items/{item_id}/activities/{activity_id}",
            "required_params": ["item_id", "activity_id"],
            "path_params": ["item_id", "activity_id"]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.universal_node = UniversalRequestNode(self.CONFIG, self.OPERATIONS, sandbox_timeout)
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the OneDrive node."""
        return NodeSchema(
            node_type="onedrive",
            version="2.0.0",
            description="Comprehensive Microsoft Graph OneDrive API integration with 60+ operations using UniversalRequestNode for files, folders, drives, sharing, and content management",
            parameters=[
                # Core configuration
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="OneDrive operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="client_id",
                    type=NodeParameterType.SECRET,
                    description="Microsoft Azure Application Client ID",
                    required=True
                ),
                NodeParameter(
                    name="client_secret", 
                    type=NodeParameterType.SECRET,
                    description="Microsoft Azure Application Client Secret",
                    required=True
                ),
                NodeParameter(
                    name="tenant_id",
                    type=NodeParameterType.STRING,
                    description="Microsoft Azure Tenant ID",
                    required=True
                ),
                NodeParameter(
                    name="scope",
                    type=NodeParameterType.STRING,
                    description="OAuth scope for access",
                    required=False,
                    default="https://graph.microsoft.com/.default"
                ),
                
                # ID parameters
                NodeParameter(
                    name="drive_id",
                    type=NodeParameterType.STRING,
                    description="Drive ID for drive-specific operations",
                    required=False
                ),
                NodeParameter(
                    name="user_id",
                    type=NodeParameterType.STRING,
                    description="User ID (defaults to 'me' for current user)",
                    required=False,
                    default="me"
                ),
                NodeParameter(
                    name="item_id",
                    type=NodeParameterType.STRING,
                    description="Item ID for item operations",
                    required=False
                ),
                NodeParameter(
                    name="parent_id",
                    type=NodeParameterType.STRING,
                    description="Parent item ID (defaults to 'root')",
                    required=False,
                    default="root"
                ),
                NodeParameter(
                    name="item_path",
                    type=NodeParameterType.STRING,
                    description="Item path for path-based operations",
                    required=False
                ),
                NodeParameter(
                    name="permission_id",
                    type=NodeParameterType.STRING,
                    description="Permission ID for permission operations",
                    required=False
                ),
                NodeParameter(
                    name="version_id",
                    type=NodeParameterType.STRING,
                    description="Version ID for version operations", 
                    required=False
                ),
                NodeParameter(
                    name="thumbnail_set_id",
                    type=NodeParameterType.STRING,
                    description="Thumbnail set ID for thumbnail operations",
                    required=False
                ),
                NodeParameter(
                    name="activity_id",
                    type=NodeParameterType.STRING,
                    description="Activity ID for activity operations",
                    required=False
                ),
                
                # Content parameters
                NodeParameter(
                    name="content",
                    type=NodeParameterType.STRING,
                    description="File content for upload operations",
                    required=False
                ),
                NodeParameter(
                    name="content_type",
                    type=NodeParameterType.STRING,
                    description="Content type for upload operations",
                    required=False,
                    default="application/octet-stream"
                ),
                NodeParameter(
                    name="folder_name",
                    type=NodeParameterType.STRING,
                    description="Name for folder creation",
                    required=False
                ),
                NodeParameter(
                    name="file_name",
                    type=NodeParameterType.STRING,
                    description="File name for file operations",
                    required=False
                ),
                
                # Request body
                NodeParameter(
                    name="request_body",
                    type=NodeParameterType.OBJECT,
                    description="Request body for create/update operations",
                    required=False
                ),
                
                # Search parameters
                NodeParameter(
                    name="search_query",
                    type=NodeParameterType.STRING,
                    description="Search query for search operations",
                    required=False
                ),
                
                # Sharing parameters
                NodeParameter(
                    name="sharing_type",
                    type=NodeParameterType.STRING,
                    description="Type of sharing link",
                    required=False,
                    enum=["view", "edit", "embed"],
                    default="view"
                ),
                NodeParameter(
                    name="sharing_scope",
                    type=NodeParameterType.STRING,
                    description="Scope of sharing link",
                    required=False,
                    enum=["anonymous", "organization", "users"],
                    default="anonymous"
                ),
                NodeParameter(
                    name="recipients",
                    type=NodeParameterType.ARRAY,
                    description="Recipients for sharing invitation (email addresses)",
                    required=False
                ),
                NodeParameter(
                    name="message",
                    type=NodeParameterType.STRING,
                    description="Message for sharing invitation",
                    required=False
                ),
                
                # Special folder parameters
                NodeParameter(
                    name="special_folder",
                    type=NodeParameterType.STRING,
                    description="Special folder name",
                    required=False,
                    enum=["documents", "photos", "cameraRoll", "appRoot", "music"]
                ),
                
                # Move/Copy parameters
                NodeParameter(
                    name="parent_reference",
                    type=NodeParameterType.OBJECT,
                    description="Parent reference for move/copy operations",
                    required=False
                ),
                NodeParameter(
                    name="new_name",
                    type=NodeParameterType.STRING,
                    description="New name for move/copy operations",
                    required=False
                ),
                
                # Upload parameters
                NodeParameter(
                    name="conflict_behavior",
                    type=NodeParameterType.STRING,
                    description="Conflict behavior for upload/create operations",
                    required=False,
                    enum=["rename", "replace", "fail"],
                    default="rename"
                ),
                
                # Thumbnail parameters
                NodeParameter(
                    name="thumbnail_size",
                    type=NodeParameterType.STRING,
                    description="Thumbnail size",
                    required=False,
                    enum=["small", "medium", "large"],
                    default="medium"
                ),
                
                # Query parameters
                NodeParameter(
                    name="select",
                    type=NodeParameterType.STRING,
                    description="Select specific properties ($select)",
                    required=False
                ),
                NodeParameter(
                    name="filter", 
                    type=NodeParameterType.STRING,
                    description="Filter criteria ($filter)",
                    required=False
                ),
                NodeParameter(
                    name="order_by",
                    type=NodeParameterType.STRING,
                    description="Order by criteria ($orderby)",
                    required=False
                ),
                NodeParameter(
                    name="top",
                    type=NodeParameterType.NUMBER,
                    description="Number of items to return ($top)",
                    required=False,
                    default=100,
                    min_value=1,
                    max_value=1000
                ),
                NodeParameter(
                    name="skip",
                    type=NodeParameterType.NUMBER,
                    description="Number of items to skip ($skip)",
                    required=False,
                    default=0,
                    min_value=0
                ),
                
                # Delta parameters
                NodeParameter(
                    name="delta_token",
                    type=NodeParameterType.STRING,
                    description="Delta token for incremental changes",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT,
                "id": NodeParameterType.STRING,
                "access_token": NodeParameterType.STRING,
                "download_url": NodeParameterType.STRING,
                "upload_url": NodeParameterType.STRING,
                "sharing_url": NodeParameterType.STRING
            },
            tags=["onedrive", "microsoft", "graph", "files", "storage", "cloud", "api", "unified"],
            author="System",
            documentation_url="https://learn.microsoft.com/en-us/graph/api/resources/onedrive"
        )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the OneDrive operation using UniversalRequestNode."""
        try:
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            if not operation:
                raise NodeValidationError("Operation is required")
            
            if operation not in self.OPERATIONS:
                raise NodeValidationError(f"Unknown operation: {operation}")
            
            # Get operation config
            op_config = self.OPERATIONS[operation]
            
            # Build the universal request node data
            universal_data = await self._build_universal_request(params, op_config)
            
            # Execute using universal request node
            result = await self.universal_node.execute(universal_data)
            
            # Process the result for OneDrive-specific outputs
            return await self._process_result(result, params, operation)
            
        except Exception as e:
            logger.error(f"Error in OneDrive operation: {str(e)}")
            return {
                "status": "error",
                "result": None,
                "error": str(e),
                "status_code": None,
                "response_headers": None,
                "id": None,
                "access_token": None,
                "download_url": None,
                "upload_url": None,
                "sharing_url": None
            }

    async def _build_universal_request(self, params: Dict[str, Any], op_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build request data for UniversalRequestNode."""
        # Start with base config
        config = self.CONFIG.copy()
        
        # Handle OAuth2 authentication
        client_id = params.get("client_id")
        client_secret = params.get("client_secret")
        tenant_id = params.get("tenant_id")
        scope = params.get("scope", "https://graph.microsoft.com/.default")
        
        if client_id and client_secret and tenant_id:
            config["authentication"]["token_url"] = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
            config["authentication"]["credentials"] = {
                "client_id": client_id,
                "client_secret": client_secret
            }
            config["authentication"]["token_params"]["scope"] = scope
        
        # Build endpoint with path parameters
        endpoint = op_config["endpoint"]
        path_params = op_config.get("path_params", [])
        
        for param in path_params:
            value = params.get(param)
            if value is not None:
                if param == "item_path":
                    # URL encode path segments
                    value = quote(str(value), safe='/')
                placeholder = "{" + param + "}"
                endpoint = endpoint.replace(placeholder, str(value))
        
        # Build query parameters
        query_params = {}
        query_mappings = {
            "select": "$select",
            "filter": "$filter", 
            "order_by": "$orderby",
            "top": "$top",
            "skip": "$skip"
        }
        
        for param, query_param in query_mappings.items():
            if params.get(param) is not None:
                query_params[query_param] = params[param]
        
        # Add delta token if present
        if params.get("delta_token"):
            query_params["token"] = params["delta_token"]
        
        # Add conflict behavior for upload operations
        if "upload" in endpoint and params.get("conflict_behavior"):
            query_params["@microsoft.graph.conflictBehavior"] = params["conflict_behavior"]
        
        # Build request body based on operation
        request_body = await self._build_request_body(params, op_config, endpoint)
        
        # Handle content uploads
        if params.get("content") and "content" in endpoint:
            config["default_headers"]["Content-Type"] = params.get("content_type", "application/octet-stream")
            request_body = params["content"]
        
        return {
            "params": {
                "config": config,
                "method": op_config["method"],
                "endpoint": endpoint,
                "query_params": query_params if query_params else None,
                "request_body": request_body,
                "timeout": config["timeouts"]["total"]
            }
        }

    async def _build_request_body(self, params: Dict[str, Any], op_config: Dict[str, Any], endpoint: str) -> Optional[Dict[str, Any]]:
        """Build request body for specific operations."""
        operation = params.get("operation", "")
        
        # Use explicit request_body if provided
        if params.get("request_body"):
            return params["request_body"]
        
        # Handle folder creation
        if "create_folder" in operation or "create" in operation and params.get("folder_name"):
            return {
                "name": params["folder_name"],
                "folder": {},
                "@microsoft.graph.conflictBehavior": params.get("conflict_behavior", "rename")
            }
        
        # Handle sharing link creation
        if "create_sharing_link" in operation or "createLink" in endpoint:
            return {
                "type": params.get("sharing_type", "view"),
                "scope": params.get("sharing_scope", "anonymous")
            }
        
        # Handle sharing invitations
        if "send_sharing_invitation" in operation or "invite" in endpoint:
            recipients = params.get("recipients", [])
            recipient_list = []
            for recipient in recipients:
                if isinstance(recipient, str):
                    recipient_list.append({"email": recipient})
                elif isinstance(recipient, dict):
                    recipient_list.append(recipient)
            
            return {
                "recipients": recipient_list,
                "message": params.get("message", ""),
                "requireSignIn": True,
                "sendInvitation": True,
                "roles": ["read"]
            }
        
        # Handle copy operations
        if "copy" in operation and params.get("parent_reference"):
            body = {"parentReference": params["parent_reference"]}
            if params.get("new_name"):
                body["name"] = params["new_name"]
            return body
        
        # Handle move operations  
        if "move" in operation and params.get("parent_reference"):
            body = {"parentReference": params["parent_reference"]}
            if params.get("new_name"):
                body["name"] = params["new_name"]
            return body
        
        # Handle restore operations
        if "restore" in operation and not "version" in operation:
            return {"parentReference": params.get("parent_reference", {})}
        
        # Handle upload session creation
        if "createUploadSession" in endpoint:
            return {
                "item": {
                    "@microsoft.graph.conflictBehavior": params.get("conflict_behavior", "rename")
                }
            }
        
        return None

    async def _process_result(self, result: Dict[str, Any], params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Process result from UniversalRequestNode for OneDrive-specific outputs."""
        if result.get("status") != "success":
            return result
        
        response_data = result.get("result", {})
        
        # Extract OneDrive-specific fields
        item_id = None
        download_url = None
        upload_url = None
        sharing_url = None
        access_token = None
        
        if isinstance(response_data, dict):
            item_id = response_data.get("id")
            download_url = response_data.get("@microsoft.graph.downloadUrl")
            upload_url = response_data.get("uploadUrl")
            
            # Extract sharing URL from different response formats
            if response_data.get("link"):
                sharing_url = response_data["link"].get("webUrl")
            elif response_data.get("webUrl"):
                sharing_url = response_data["webUrl"]
        
        # Extract access token for auth operations
        if operation == "get_access_token" and isinstance(response_data, dict):
            access_token = response_data.get("access_token")
        
        return {
            "status": result.get("status"),
            "result": response_data,
            "error": result.get("error"),
            "status_code": result.get("status_code"),
            "response_headers": result.get("response_headers"),
            "id": item_id,
            "access_token": access_token,
            "download_url": download_url,
            "upload_url": upload_url,
            "sharing_url": sharing_url
        }


# Helper class for creating common request objects
class OneDriveHelpers:
    """Helper functions for creating OneDrive API request objects."""
    
    @staticmethod
    def create_parent_reference(drive_id: str, item_id: str) -> Dict[str, str]:
        """Create parent reference for move/copy operations."""
        return {
            "driveId": drive_id,
            "id": item_id
        }
    
    @staticmethod
    def create_folder_request(name: str, conflict_behavior: str = "rename") -> Dict[str, Any]:
        """Create folder creation request."""
        return {
            "name": name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": conflict_behavior
        }
    
    @staticmethod
    def create_sharing_invitation(recipients: List[str], message: str = "", roles: List[str] = None) -> Dict[str, Any]:
        """Create sharing invitation request."""
        if roles is None:
            roles = ["read"]
        
        return {
            "recipients": [{"email": email} for email in recipients],
            "message": message,
            "requireSignIn": True,
            "sendInvitation": True,
            "roles": roles
        }
    
    @staticmethod
    def create_permission_request(recipients: List[str], roles: List[str] = None) -> Dict[str, Any]:
        """Create permission request."""
        if roles is None:
            roles = ["read"]
            
        return {
            "recipients": [{"email": email} for email in recipients],
            "roles": roles,
            "sendInvitation": True
        }


# Register with NodeRegistry if available
if __name__ == "__main__":
    import asyncio
    import os
    
    async def test_onedrive_node():
        """Test the OneDrive node with sample operations."""
        node = OneDriveNode()
        
        # Test schema
        schema = node.get_schema()
        print(f"OneDrive Node Schema: {schema.node_type} v{schema.version}")
        print(f"Available operations: {len(node.OPERATIONS)}")
        print(f"Sample operations: {list(node.OPERATIONS.keys())[:5]}...")
        
        # You would need actual credentials to test operations:
        # client_id = os.getenv("AZURE_CLIENT_ID")
        # client_secret = os.getenv("AZURE_CLIENT_SECRET") 
        # tenant_id = os.getenv("AZURE_TENANT_ID")
        
        print("OneDrive Node unified implementation ready!")
    
    asyncio.run(test_onedrive_node())

try:
    from node_registry import NodeRegistry
    registry = NodeRegistry()
    registry.register("onedrive", OneDriveNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register OneDriveNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")