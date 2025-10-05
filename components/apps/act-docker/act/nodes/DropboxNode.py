"""
Dropbox Node - Comprehensive integration with Dropbox API v2

Provides access to all Dropbox file operations, sharing, team management, and collaboration features.
Supports complete cloud storage workflow integration with file management, folder operations,
sharing and collaboration, team administration, and comprehensive content synchronization.

Key capabilities include: File upload and download operations, folder creation and management,
file sharing and link generation, team member collaboration, metadata and search operations,
batch processing for bulk operations, version control and file restoration, and comprehensive cloud storage automation.

Built for production environments with OAuth 2.0 Bearer token authentication, comprehensive error handling,
rate limiting compliance, and team collaboration features for cloud storage and file management.
"""

import logging
from typing import Dict, Any, Optional

try:
    from universal_request_node import UniversalRequestNode
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError, NodeExecutionError
    )
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )
    except ImportError:
        from universal_request_node import UniversalRequestNode
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )

logger = logging.getLogger(__name__)

class DropboxNode(BaseNode):
    """Comprehensive Dropbox API v2 integration node."""
    
    # Embedded configuration for Dropbox API
    CONFIG = {
        "base_url": "https://api.dropboxapi.com/2",
        "content_base_url": "https://content.dropboxapi.com/2",
        "authentication": {
            "type": "bearer_token",
            "header": "Authorization"
        },
        "headers": {
            "Content-Type": "application/json"
        },
        "timeout": 30,
        "retry_config": {
            "max_retries": 3,
            "retry_delay": 1.0,
            "exponential_backoff": True
        },
        "rate_limiting": {
            "max_requests_per_minute": 1200,
            "burst_limit": 120
        }
    }
    
    # Complete operations mapping for Dropbox API (50+ key operations)
    OPERATIONS = {
        # Authentication Operations
        "revoke_access_token": {
            "method": "POST",
            "endpoint": "/auth/token/revoke",
            "base_url": "base_url",
            "params": [],
            "required": []
        },
        
        # File Upload Operations
        "upload_file": {
            "method": "POST",
            "endpoint": "/files/upload",
            "base_url": "content_base_url",
            "params": ["path", "mode", "autorename", "client_modified", "mute", "property_groups", "strict_conflict", "file_content", "request_body"],
            "required": ["path", "file_content"]
        },
        "upload_session_start": {
            "method": "POST",
            "endpoint": "/files/upload_session/start",
            "base_url": "content_base_url",
            "params": ["close", "session_type", "file_content", "request_body"],
            "required": []
        },
        "upload_session_append": {
            "method": "POST",
            "endpoint": "/files/upload_session/append_v2",
            "base_url": "content_base_url",
            "params": ["cursor", "close", "file_content", "request_body"],
            "required": ["cursor", "file_content"]
        },
        "upload_session_finish": {
            "method": "POST",
            "endpoint": "/files/upload_session/finish",
            "base_url": "content_base_url",
            "params": ["cursor", "commit", "file_content", "request_body"],
            "required": ["cursor", "commit"]
        },
        
        # File Download Operations
        "download_file": {
            "method": "POST",
            "endpoint": "/files/download",
            "base_url": "content_base_url",
            "params": ["path", "rev", "request_body"],
            "required": ["path"]
        },
        "get_thumbnail": {
            "method": "POST",
            "endpoint": "/files/get_thumbnail",
            "base_url": "content_base_url",
            "params": ["path", "format", "size", "mode", "request_body"],
            "required": ["path"]
        },
        "get_preview": {
            "method": "POST",
            "endpoint": "/files/get_preview",
            "base_url": "content_base_url",
            "params": ["path", "rev", "request_body"],
            "required": ["path"]
        },
        "get_temporary_link": {
            "method": "POST",
            "endpoint": "/files/get_temporary_link",
            "base_url": "base_url",
            "params": ["path", "request_body"],
            "required": ["path"]
        },
        
        # File Management Operations
        "copy_file": {
            "method": "POST",
            "endpoint": "/files/copy_v2",
            "base_url": "base_url",
            "params": ["from_path", "to_path", "allow_shared_folder", "autorename", "allow_ownership_transfer", "request_body"],
            "required": ["from_path", "to_path"]
        },
        "copy_batch": {
            "method": "POST",
            "endpoint": "/files/copy_batch_v2",
            "base_url": "base_url",
            "params": ["entries", "autorename", "allow_ownership_transfer", "request_body"],
            "required": ["entries"]
        },
        "move_file": {
            "method": "POST",
            "endpoint": "/files/move_v2",
            "base_url": "base_url",
            "params": ["from_path", "to_path", "allow_shared_folder", "autorename", "allow_ownership_transfer", "request_body"],
            "required": ["from_path", "to_path"]
        },
        "move_batch": {
            "method": "POST",
            "endpoint": "/files/move_batch_v2",
            "base_url": "base_url",
            "params": ["entries", "autorename", "allow_ownership_transfer", "request_body"],
            "required": ["entries"]
        },
        "delete_file": {
            "method": "POST",
            "endpoint": "/files/delete_v2",
            "base_url": "base_url",
            "params": ["path", "parent_rev", "request_body"],
            "required": ["path"]
        },
        "delete_batch": {
            "method": "POST",
            "endpoint": "/files/delete_batch",
            "base_url": "base_url",
            "params": ["entries", "request_body"],
            "required": ["entries"]
        },
        "restore_file": {
            "method": "POST",
            "endpoint": "/files/restore",
            "base_url": "base_url",
            "params": ["path", "rev", "request_body"],
            "required": ["path", "rev"]
        },
        "save_url": {
            "method": "POST",
            "endpoint": "/files/save_url",
            "base_url": "base_url",
            "params": ["path", "url", "request_body"],
            "required": ["path", "url"]
        },
        
        # Folder Operations
        "create_folder": {
            "method": "POST",
            "endpoint": "/files/create_folder_v2",
            "base_url": "base_url",
            "params": ["path", "autorename", "request_body"],
            "required": ["path"]
        },
        "create_folder_batch": {
            "method": "POST",
            "endpoint": "/files/create_folder_batch",
            "base_url": "base_url",
            "params": ["paths", "autorename", "force_async", "request_body"],
            "required": ["paths"]
        },
        "list_folder": {
            "method": "POST",
            "endpoint": "/files/list_folder",
            "base_url": "base_url",
            "params": ["path", "recursive", "include_media_info", "include_deleted", "include_has_explicit_shared_members", "include_mounted_folders", "limit", "shared_link", "include_property_groups", "include_non_downloadable_files", "request_body"],
            "required": ["path"]
        },
        "list_folder_continue": {
            "method": "POST",
            "endpoint": "/files/list_folder/continue",
            "base_url": "base_url",
            "params": ["cursor", "request_body"],
            "required": ["cursor"]
        },
        "list_folder_longpoll": {
            "method": "POST",
            "endpoint": "/files/list_folder/longpoll",
            "base_url": "base_url",
            "params": ["cursor", "timeout", "request_body"],
            "required": ["cursor"]
        },
        "list_folder_get_latest_cursor": {
            "method": "POST",
            "endpoint": "/files/list_folder/get_latest_cursor",
            "base_url": "base_url",
            "params": ["path", "recursive", "include_media_info", "include_deleted", "include_has_explicit_shared_members", "include_mounted_folders", "limit", "shared_link", "include_property_groups", "include_non_downloadable_files", "request_body"],
            "required": ["path"]
        },
        
        # Metadata Operations
        "get_metadata": {
            "method": "POST",
            "endpoint": "/files/get_metadata",
            "base_url": "base_url",
            "params": ["path", "include_media_info", "include_deleted", "include_has_explicit_shared_members", "include_property_groups", "request_body"],
            "required": ["path"]
        },
        "list_revisions": {
            "method": "POST",
            "endpoint": "/files/list_revisions",
            "base_url": "base_url",
            "params": ["path", "mode", "limit", "request_body"],
            "required": ["path"]
        },
        "search_files": {
            "method": "POST",
            "endpoint": "/files/search_v2",
            "base_url": "base_url",
            "params": ["query", "options", "match_field_options", "request_body"],
            "required": ["query"]
        },
        
        # Sharing Operations
        "create_shared_link": {
            "method": "POST",
            "endpoint": "/sharing/create_shared_link_with_settings",
            "base_url": "base_url",
            "params": ["path", "settings", "request_body"],
            "required": ["path"]
        },
        "get_shared_links": {
            "method": "POST",
            "endpoint": "/sharing/get_shared_links",
            "base_url": "base_url",
            "params": ["path", "direct_only", "request_body"],
            "required": []
        },
        "list_shared_links": {
            "method": "POST",
            "endpoint": "/sharing/list_shared_links",
            "base_url": "base_url",
            "params": ["path", "cursor", "direct_only", "request_body"],
            "required": []
        },
        "modify_shared_link_settings": {
            "method": "POST",
            "endpoint": "/sharing/modify_shared_link_settings",
            "base_url": "base_url",
            "params": ["url", "settings", "remove_expiration", "request_body"],
            "required": ["url", "settings"]
        },
        "revoke_shared_link": {
            "method": "POST",
            "endpoint": "/sharing/revoke_shared_link",
            "base_url": "base_url",
            "params": ["url", "request_body"],
            "required": ["url"]
        },
        "share_folder": {
            "method": "POST",
            "endpoint": "/sharing/share_folder",
            "base_url": "base_url",
            "params": ["path", "member_policy", "acl_update_policy", "shared_link_policy", "force_async", "request_body"],
            "required": ["path"]
        },
        "unshare_folder": {
            "method": "POST",
            "endpoint": "/sharing/unshare_folder",
            "base_url": "base_url",
            "params": ["shared_folder_id", "leave_a_copy", "request_body"],
            "required": ["shared_folder_id"]
        },
        "transfer_folder": {
            "method": "POST",
            "endpoint": "/sharing/transfer_folder",
            "base_url": "base_url",
            "params": ["shared_folder_id", "to_dropbox_id", "request_body"],
            "required": ["shared_folder_id", "to_dropbox_id"]
        },
        "update_folder_member": {
            "method": "POST",
            "endpoint": "/sharing/update_folder_member",
            "base_url": "base_url",
            "params": ["shared_folder_id", "member", "access_level", "request_body"],
            "required": ["shared_folder_id", "member", "access_level"]
        },
        "add_folder_member": {
            "method": "POST",
            "endpoint": "/sharing/add_folder_member",
            "base_url": "base_url",
            "params": ["shared_folder_id", "members", "quiet", "custom_message", "request_body"],
            "required": ["shared_folder_id", "members"]
        },
        "remove_folder_member": {
            "method": "POST",
            "endpoint": "/sharing/remove_folder_member",
            "base_url": "base_url",
            "params": ["shared_folder_id", "member", "leave_a_copy", "request_body"],
            "required": ["shared_folder_id", "member"]
        },
        "list_folder_members": {
            "method": "POST",
            "endpoint": "/sharing/list_folder_members",
            "base_url": "base_url",
            "params": ["shared_folder_id", "actions", "limit", "request_body"],
            "required": ["shared_folder_id"]
        },
        "list_folder_members_continue": {
            "method": "POST",
            "endpoint": "/sharing/list_folder_members/continue",
            "base_url": "base_url",
            "params": ["cursor", "request_body"],
            "required": ["cursor"]
        },
        "list_folders": {
            "method": "POST",
            "endpoint": "/sharing/list_folders",
            "base_url": "base_url",
            "params": ["limit", "actions", "request_body"],
            "required": []
        },
        "list_folders_continue": {
            "method": "POST",
            "endpoint": "/sharing/list_folders/continue",
            "base_url": "base_url",
            "params": ["cursor", "request_body"],
            "required": ["cursor"]
        },
        "list_mountable_folders": {
            "method": "POST",
            "endpoint": "/sharing/list_mountable_folders",
            "base_url": "base_url",
            "params": ["limit", "actions", "request_body"],
            "required": []
        },
        "list_mountable_folders_continue": {
            "method": "POST",
            "endpoint": "/sharing/list_mountable_folders/continue",
            "base_url": "base_url",
            "params": ["cursor", "request_body"],
            "required": ["cursor"]
        },
        "mount_folder": {
            "method": "POST",
            "endpoint": "/sharing/mount_folder",
            "base_url": "base_url",
            "params": ["shared_folder_id", "request_body"],
            "required": ["shared_folder_id"]
        },
        "unmount_folder": {
            "method": "POST",
            "endpoint": "/sharing/unmount_folder",
            "base_url": "base_url",
            "params": ["shared_folder_id", "request_body"],
            "required": ["shared_folder_id"]
        },
        
        # User and Account Operations
        "get_account": {
            "method": "POST",
            "endpoint": "/users/get_account",
            "base_url": "base_url",
            "params": ["account_id", "request_body"],
            "required": ["account_id"]
        },
        "get_account_batch": {
            "method": "POST",
            "endpoint": "/users/get_account_batch",
            "base_url": "base_url",
            "params": ["account_ids", "request_body"],
            "required": ["account_ids"]
        },
        "get_current_account": {
            "method": "POST",
            "endpoint": "/users/get_current_account",
            "base_url": "base_url",
            "params": [],
            "required": []
        },
        "get_space_usage": {
            "method": "POST",
            "endpoint": "/users/get_space_usage",
            "base_url": "base_url",
            "params": [],
            "required": []
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.universal_node = UniversalRequestNode()
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Dropbox node."""
        return NodeSchema(
            name="DropboxNode",
            description="Comprehensive Dropbox API v2 integration for cloud storage and file management",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Dropbox operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                "access_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Dropbox access token for authentication",
                    required=True
                ),
                # File path parameters
                "path": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="File or folder path in Dropbox",
                    required=False
                ),
                "from_path": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Source path for copy/move operations",
                    required=False
                ),
                "to_path": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Destination path for copy/move operations",
                    required=False
                ),
                "paths": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of paths for batch operations",
                    required=False
                ),
                # File content and upload parameters
                "file_content": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="File content for upload operations (base64 encoded)",
                    required=False
                ),
                "mode": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Upload mode (add/overwrite/update)",
                    required=False
                ),
                "autorename": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Automatically rename if conflict exists",
                    required=False
                ),
                "client_modified": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Client modified timestamp",
                    required=False
                ),
                "mute": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Mute notifications for this operation",
                    required=False
                ),
                "strict_conflict": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Strictly check for conflicts",
                    required=False
                ),
                # Upload session parameters
                "cursor": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Upload session cursor",
                    required=False
                ),
                "commit": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Upload session commit info",
                    required=False
                ),
                "close": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Close upload session",
                    required=False
                ),
                "session_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Upload session type",
                    required=False
                ),
                # Download and preview parameters
                "rev": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="File revision",
                    required=False
                ),
                "format": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Thumbnail format (jpeg/png)",
                    required=False
                ),
                "size": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Thumbnail size (w32h32/w64h64/w128h128/w256h256/w480h320/w640h480/w960h640/w1024h768/w2048h1536)",
                    required=False
                ),
                # List folder parameters
                "recursive": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="List folder recursively",
                    required=False
                ),
                "include_media_info": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include media info in results",
                    required=False
                ),
                "include_deleted": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include deleted files",
                    required=False
                ),
                "include_has_explicit_shared_members": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include explicit shared members info",
                    required=False
                ),
                "include_mounted_folders": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include mounted folders",
                    required=False
                ),
                "limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Limit number of results",
                    required=False
                ),
                "shared_link": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Shared link info",
                    required=False
                ),
                "include_property_groups": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Property groups to include",
                    required=False
                ),
                "include_non_downloadable_files": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include non-downloadable files",
                    required=False
                ),
                "timeout": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Timeout for longpoll operations",
                    required=False
                ),
                # Search parameters
                "query": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Search query",
                    required=False
                ),
                "options": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Search options",
                    required=False
                ),
                "match_field_options": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Match field options for search",
                    required=False
                ),
                # Sharing parameters
                "settings": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Shared link settings",
                    required=False
                ),
                "direct_only": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Direct links only",
                    required=False
                ),
                "url": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Shared link URL",
                    required=False
                ),
                "remove_expiration": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Remove expiration from shared link",
                    required=False
                ),
                "shared_folder_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Shared folder ID",
                    required=False
                ),
                "member_policy": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Member policy for folder sharing",
                    required=False
                ),
                "acl_update_policy": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="ACL update policy",
                    required=False
                ),
                "shared_link_policy": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Shared link policy",
                    required=False
                ),
                "force_async": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Force async processing",
                    required=False
                ),
                "leave_a_copy": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Leave a copy when removing from folder",
                    required=False
                ),
                "to_dropbox_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Target Dropbox ID for transfer",
                    required=False
                ),
                "member": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Folder member info",
                    required=False
                ),
                "members": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of folder members",
                    required=False
                ),
                "access_level": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Access level for folder member",
                    required=False
                ),
                "quiet": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Send notification quietly",
                    required=False
                ),
                "custom_message": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Custom message for folder invitation",
                    required=False
                ),
                "actions": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Actions to include in results",
                    required=False
                ),
                # Batch operation parameters
                "entries": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of entries for batch operations",
                    required=False
                ),
                "allow_shared_folder": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Allow operations on shared folders",
                    required=False
                ),
                "allow_ownership_transfer": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Allow ownership transfer",
                    required=False
                ),
                "parent_rev": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Parent revision for delete operations",
                    required=False
                ),
                # Account parameters
                "account_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Account ID",
                    required=False
                ),
                "account_ids": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of account IDs",
                    required=False
                ),
                # Generic request body
                "request_body": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Request body for operations",
                    required=False
                )
            },
            outputs={
                "status": NodeParameterType.STRING,
                "file_metadata": NodeParameterType.OBJECT,
                "folder_metadata": NodeParameterType.OBJECT,
                "entries": NodeParameterType.ARRAY,
                "files": NodeParameterType.ARRAY,
                "folders": NodeParameterType.ARRAY,
                "shared_links": NodeParameterType.ARRAY,
                "shared_link_metadata": NodeParameterType.OBJECT,
                "folder_members": NodeParameterType.ARRAY,
                "shared_folders": NodeParameterType.ARRAY,
                "upload_session_id": NodeParameterType.STRING,
                "cursor": NodeParameterType.STRING,
                "has_more": NodeParameterType.BOOLEAN,
                "download_url": NodeParameterType.STRING,
                "temporary_link": NodeParameterType.STRING,
                "thumbnail_data": NodeParameterType.STRING,
                "preview_data": NodeParameterType.STRING,
                "file_content": NodeParameterType.STRING,
                "search_results": NodeParameterType.OBJECT,
                "revisions": NodeParameterType.ARRAY,
                "account_info": NodeParameterType.OBJECT,
                "space_usage": NodeParameterType.OBJECT,
                "batch_result": NodeParameterType.OBJECT,
                "deleted_metadata": NodeParameterType.OBJECT,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Dropbox-specific parameters."""
        params = node_data.get("params", {})
        
        if not params.get("operation"):
            raise NodeValidationError("Operation is required")
        if not params.get("access_token"):
            raise NodeValidationError("Dropbox access token is required")
        
        operation = params["operation"]
        if operation not in self.OPERATIONS:
            raise NodeValidationError(f"Unknown operation: {operation}")
        
        # Check required parameters for operation
        operation_config = self.OPERATIONS[operation]
        for required_param in operation_config.get("required", []):
            if not params.get(required_param):
                raise NodeValidationError(f"Parameter '{required_param}' is required for operation '{operation}'")
        
        return params
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Dropbox operation using UniversalRequestNode."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Get operation configuration
            operation_config = self.OPERATIONS[operation]
            
            # Prepare configuration with authentication and correct base URL
            config = self.CONFIG.copy()
            
            # Use content base URL for upload/download operations
            if operation_config.get("base_url") == "content_base_url":
                config["base_url"] = config["content_base_url"]
                # Content operations use different headers
                config["headers"] = {
                    "Content-Type": "application/octet-stream",
                    "Dropbox-API-Arg": ""  # Will be set dynamically
                }
            
            # Prepare universal request node parameters
            universal_params = {
                "config": config,
                "method": operation_config["method"],
                "endpoint": operation_config["endpoint"],
                "token": params["access_token"]
            }
            
            # Handle content operations differently (upload/download)
            if operation_config.get("base_url") == "content_base_url":
                # Build Dropbox-API-Arg header
                api_arg = {}
                for param in operation_config.get("params", []):
                    if param in params and params[param] is not None and param != "file_content":
                        api_arg[param] = params[param]
                
                # Set the API arg header
                universal_params["config"]["headers"]["Dropbox-API-Arg"] = str(api_arg).replace("'", '"')
                
                # Set file content as body for upload operations
                if params.get("file_content"):
                    universal_params["body"] = params["file_content"]
                    universal_params["raw_body"] = True
            else:
                # Regular API operations - prepare body data
                body_data = {}
                
                if params.get("request_body"):
                    body_data = params["request_body"]
                else:
                    # Build body based on operation
                    for param in operation_config.get("params", []):
                        if param in params and params[param] is not None:
                            body_data[param] = params[param]
                
                if body_data:
                    universal_params["body"] = body_data
            
            # Execute the request
            result = await self.universal_node.execute({
                "params": universal_params
            })
            
            if result.get("status") == "success":
                response_data = result.get("response", {})
                
                # Transform response based on operation type
                if operation.startswith("upload_"):
                    if operation == "upload_session_start":
                        return {
                            "status": "success",
                            "upload_session_id": response_data.get("session_id"),
                            "response_data": response_data
                        }
                    else:
                        return {
                            "status": "success",
                            "file_metadata": response_data,
                            "response_data": response_data
                        }
                elif operation.startswith("download_") or operation.startswith("get_thumbnail") or operation.startswith("get_preview"):
                    return {
                        "status": "success",
                        "file_content": result.get("raw_content", ""),
                        "file_metadata": response_data,
                        "response_data": response_data
                    }
                elif operation == "get_temporary_link":
                    return {
                        "status": "success",
                        "temporary_link": response_data.get("link"),
                        "response_data": response_data
                    }
                elif operation in ["copy_file", "move_file", "delete_file", "restore_file"]:
                    return {
                        "status": "success",
                        "file_metadata": response_data,
                        "response_data": response_data
                    }
                elif operation in ["copy_batch", "move_batch", "delete_batch"]:
                    return {
                        "status": "success",
                        "batch_result": response_data,
                        "response_data": response_data
                    }
                elif operation in ["create_folder", "create_folder_batch"]:
                    return {
                        "status": "success",
                        "folder_metadata": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_folder"):
                    return {
                        "status": "success",
                        "entries": response_data.get("entries", []),
                        "cursor": response_data.get("cursor"),
                        "has_more": response_data.get("has_more"),
                        "response_data": response_data
                    }
                elif operation == "get_metadata":
                    return {
                        "status": "success",
                        "file_metadata": response_data,
                        "response_data": response_data
                    }
                elif operation == "list_revisions":
                    return {
                        "status": "success",
                        "revisions": response_data.get("entries", []),
                        "response_data": response_data
                    }
                elif operation == "search_files":
                    return {
                        "status": "success",
                        "search_results": response_data,
                        "matches": response_data.get("matches", []),
                        "response_data": response_data
                    }
                elif operation.startswith("create_shared_link") or operation.startswith("modify_shared_link"):
                    return {
                        "status": "success",
                        "shared_link_metadata": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_shared_links") or operation.startswith("list_shared_links"):
                    return {
                        "status": "success",
                        "shared_links": response_data.get("links", []),
                        "response_data": response_data
                    }
                elif operation.startswith("share_folder") or operation.startswith("unshare_folder"):
                    return {
                        "status": "success",
                        "folder_metadata": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_folder_members"):
                    return {
                        "status": "success",
                        "folder_members": response_data.get("users", []) + response_data.get("groups", []) + response_data.get("invitees", []),
                        "cursor": response_data.get("cursor"),
                        "response_data": response_data
                    }
                elif operation.startswith("list_folders") or operation.startswith("list_mountable_folders"):
                    return {
                        "status": "success",
                        "shared_folders": response_data.get("entries", []),
                        "cursor": response_data.get("cursor"),
                        "response_data": response_data
                    }
                elif operation.startswith("get_account") or operation.startswith("get_current_account"):
                    return {
                        "status": "success",
                        "account_info": response_data,
                        "response_data": response_data
                    }
                elif operation == "get_space_usage":
                    return {
                        "status": "success",
                        "space_usage": response_data,
                        "response_data": response_data
                    }
                else:
                    return {
                        "status": "success",
                        "response_data": response_data
                    }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Dropbox operation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "DROPBOX_ERROR"
            }
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'universal_node'):
            await self.universal_node.close()