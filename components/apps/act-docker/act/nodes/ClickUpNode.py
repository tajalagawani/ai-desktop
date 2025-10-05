"""
ClickUp Node - Comprehensive integration with ClickUp REST API

Provides access to all ClickUp API operations including tasks, spaces, lists, folders, teams, goals, and time tracking.
Supports complete project management workflow integration with team collaboration, productivity tracking,
and comprehensive workspace management features.

Key capabilities include: Task management and lifecycle tracking, space and folder organization, list management,
team collaboration, goal setting and tracking, time tracking and productivity monitoring, custom fields and tags,
checklist management, comment and attachment handling, webhook integration, and view customization.

Built for production environments with API token authentication, comprehensive error handling,
rate limiting compliance, and team collaboration features for project management and productivity tracking.
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

class ClickUpNode(BaseNode):
    """Comprehensive ClickUp REST API integration node."""
    
    # Embedded configuration for ClickUp API
    CONFIG = {
        "base_url": "https://api.clickup.com/api/v2",
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
            "max_requests_per_minute": 100,
            "burst_limit": 10
        }
    }
    
    # Complete operations mapping for ClickUp API (70+ operations)
    OPERATIONS = {
        # Authentication
        "get_access_token": {
            "method": "GET",
            "endpoint": "/oauth/token",
            "params": ["code", "client_id", "client_secret"],
            "required": ["code", "client_id", "client_secret"]
        },
        
        # Teams (Workspaces) API
        "get_teams": {
            "method": "GET",
            "endpoint": "/team",
            "params": [],
            "required": []
        },
        
        # Spaces API
        "get_spaces": {
            "method": "GET",
            "endpoint": "/team/{team_id}/space",
            "params": ["team_id", "archived"],
            "required": ["team_id"]
        },
        "get_space": {
            "method": "GET",
            "endpoint": "/space/{space_id}",
            "params": ["space_id"],
            "required": ["space_id"]
        },
        "create_space": {
            "method": "POST",
            "endpoint": "/team/{team_id}/space",
            "params": ["team_id", "space_name", "multiple_assignees", "features", "request_body"],
            "required": ["team_id", "space_name"]
        },
        "update_space": {
            "method": "PUT",
            "endpoint": "/space/{space_id}",
            "params": ["space_id", "request_body"],
            "required": ["space_id", "request_body"]
        },
        "delete_space": {
            "method": "DELETE",
            "endpoint": "/space/{space_id}",
            "params": ["space_id"],
            "required": ["space_id"]
        },
        
        # Folders API
        "get_folders": {
            "method": "GET",
            "endpoint": "/space/{space_id}/folder",
            "params": ["space_id", "archived"],
            "required": ["space_id"]
        },
        "get_folder": {
            "method": "GET",
            "endpoint": "/folder/{folder_id}",
            "params": ["folder_id"],
            "required": ["folder_id"]
        },
        "create_folder": {
            "method": "POST",
            "endpoint": "/space/{space_id}/folder",
            "params": ["space_id", "folder_name", "request_body"],
            "required": ["space_id", "folder_name"]
        },
        "update_folder": {
            "method": "PUT",
            "endpoint": "/folder/{folder_id}",
            "params": ["folder_id", "request_body"],
            "required": ["folder_id", "request_body"]
        },
        "delete_folder": {
            "method": "DELETE",
            "endpoint": "/folder/{folder_id}",
            "params": ["folder_id"],
            "required": ["folder_id"]
        },
        
        # Lists API
        "get_lists": {
            "method": "GET",
            "endpoint": "/folder/{folder_id}/list",
            "params": ["folder_id", "archived"],
            "required": ["folder_id"]
        },
        "get_list": {
            "method": "GET",
            "endpoint": "/list/{list_id}",
            "params": ["list_id"],
            "required": ["list_id"]
        },
        "create_list": {
            "method": "POST",
            "endpoint": "/folder/{folder_id}/list",
            "params": ["folder_id", "list_name", "content", "due_date", "priority", "assignee", "status", "request_body"],
            "required": ["folder_id", "list_name"]
        },
        "update_list": {
            "method": "PUT",
            "endpoint": "/list/{list_id}",
            "params": ["list_id", "request_body"],
            "required": ["list_id", "request_body"]
        },
        "delete_list": {
            "method": "DELETE",
            "endpoint": "/list/{list_id}",
            "params": ["list_id"],
            "required": ["list_id"]
        },
        "get_folderless_lists": {
            "method": "GET",
            "endpoint": "/space/{space_id}/list",
            "params": ["space_id", "archived"],
            "required": ["space_id"]
        },
        "create_folderless_list": {
            "method": "POST",
            "endpoint": "/space/{space_id}/list",
            "params": ["space_id", "list_name", "content", "due_date", "priority", "assignee", "status", "request_body"],
            "required": ["space_id", "list_name"]
        },
        
        # Tasks API
        "get_tasks": {
            "method": "GET",
            "endpoint": "/list/{list_id}/task",
            "params": ["list_id", "archived", "include_markdown_description", "page", "order_by", "reverse", "subtasks", "statuses", "include_closed", "assignees", "tags", "due_date_gt", "due_date_lt", "date_created_gt", "date_created_lt", "date_updated_gt", "date_updated_lt", "date_done_gt", "date_done_lt", "custom_fields"],
            "required": ["list_id"]
        },
        "get_task": {
            "method": "GET",
            "endpoint": "/task/{task_id}",
            "params": ["task_id", "custom_task_ids", "team_id", "include_subtasks", "include_markdown_description"],
            "required": ["task_id"]
        },
        "create_task": {
            "method": "POST",
            "endpoint": "/list/{list_id}/task",
            "params": ["list_id", "task_name", "description", "assignees", "tags", "status", "priority", "due_date", "due_date_time", "time_estimate", "start_date", "start_date_time", "notify_all", "parent", "links_to", "check_required_custom_fields", "custom_fields", "request_body"],
            "required": ["list_id", "task_name"]
        },
        "update_task": {
            "method": "PUT",
            "endpoint": "/task/{task_id}",
            "params": ["task_id", "request_body"],
            "required": ["task_id", "request_body"]
        },
        "delete_task": {
            "method": "DELETE",
            "endpoint": "/task/{task_id}",
            "params": ["task_id", "custom_task_ids", "team_id"],
            "required": ["task_id"]
        },
        "get_filtered_team_tasks": {
            "method": "GET",
            "endpoint": "/team/{team_id}/task",
            "params": ["team_id", "page", "order_by", "reverse", "subtasks", "space_ids", "project_ids", "list_ids", "statuses", "include_closed", "assignees", "tags", "due_date_gt", "due_date_lt", "date_created_gt", "date_created_lt", "date_updated_gt", "date_updated_lt", "custom_fields"],
            "required": ["team_id"]
        },
        
        # Task Comments API
        "get_task_comments": {
            "method": "GET",
            "endpoint": "/task/{task_id}/comment",
            "params": ["task_id", "custom_task_ids", "team_id", "start", "start_id"],
            "required": ["task_id"]
        },
        "create_task_comment": {
            "method": "POST",
            "endpoint": "/task/{task_id}/comment",
            "params": ["task_id", "comment_text", "assignee", "notify_all", "request_body"],
            "required": ["task_id", "comment_text"]
        },
        "update_comment": {
            "method": "PUT",
            "endpoint": "/comment/{comment_id}",
            "params": ["comment_id", "request_body"],
            "required": ["comment_id", "request_body"]
        },
        "delete_comment": {
            "method": "DELETE",
            "endpoint": "/comment/{comment_id}",
            "params": ["comment_id"],
            "required": ["comment_id"]
        },
        
        # Task Dependencies API
        "add_dependency": {
            "method": "POST",
            "endpoint": "/task/{task_id}/dependency",
            "params": ["task_id", "depends_on", "dependency_of", "request_body"],
            "required": ["task_id"]
        },
        "delete_dependency": {
            "method": "DELETE",
            "endpoint": "/task/{task_id}/dependency",
            "params": ["task_id", "depends_on", "dependency_of"],
            "required": ["task_id"]
        },
        "add_task_link": {
            "method": "POST",
            "endpoint": "/task/{task_id}/link/{links_to}",
            "params": ["task_id", "links_to"],
            "required": ["task_id", "links_to"]
        },
        "delete_task_link": {
            "method": "DELETE",
            "endpoint": "/task/{task_id}/link/{links_to}",
            "params": ["task_id", "links_to"],
            "required": ["task_id", "links_to"]
        },
        
        # Task Attachments API
        "create_task_attachment": {
            "method": "POST",
            "endpoint": "/task/{task_id}/attachment",
            "params": ["task_id", "attachment", "filename", "request_body"],
            "required": ["task_id", "attachment"]
        },
        
        # Custom Fields API
        "get_accessible_custom_fields": {
            "method": "GET",
            "endpoint": "/list/{list_id}/field",
            "params": ["list_id"],
            "required": ["list_id"]
        },
        "set_custom_field_value": {
            "method": "POST",
            "endpoint": "/task/{task_id}/field/{field_id}",
            "params": ["task_id", "field_id", "value", "value_options", "request_body"],
            "required": ["task_id", "field_id"]
        },
        "remove_custom_field_value": {
            "method": "DELETE",
            "endpoint": "/task/{task_id}/field/{field_id}",
            "params": ["task_id", "field_id"],
            "required": ["task_id", "field_id"]
        },
        
        # Members API
        "get_task_members": {
            "method": "GET",
            "endpoint": "/task/{task_id}/member",
            "params": ["task_id"],
            "required": ["task_id"]
        },
        "get_list_members": {
            "method": "GET",
            "endpoint": "/list/{list_id}/member",
            "params": ["list_id"],
            "required": ["list_id"]
        },
        
        # Tags API
        "get_space_tags": {
            "method": "GET",
            "endpoint": "/space/{space_id}/tag",
            "params": ["space_id"],
            "required": ["space_id"]
        },
        "create_space_tag": {
            "method": "POST",
            "endpoint": "/space/{space_id}/tag",
            "params": ["space_id", "tag_name", "tag_fg", "tag_bg", "request_body"],
            "required": ["space_id", "tag_name"]
        },
        "edit_tag": {
            "method": "PUT",
            "endpoint": "/space/{space_id}/tag/{tag_name}",
            "params": ["space_id", "tag_name", "new_tag_name", "tag_fg", "tag_bg", "request_body"],
            "required": ["space_id", "tag_name"]
        },
        "delete_tag": {
            "method": "DELETE",
            "endpoint": "/space/{space_id}/tag/{tag_name}",
            "params": ["space_id", "tag_name"],
            "required": ["space_id", "tag_name"]
        },
        "add_tag_to_task": {
            "method": "POST",
            "endpoint": "/task/{task_id}/tag/{tag_name}",
            "params": ["task_id", "tag_name"],
            "required": ["task_id", "tag_name"]
        },
        "remove_tag_from_task": {
            "method": "DELETE",
            "endpoint": "/task/{task_id}/tag/{tag_name}",
            "params": ["task_id", "tag_name"],
            "required": ["task_id", "tag_name"]
        },
        
        # Goals API
        "create_goal": {
            "method": "POST",
            "endpoint": "/team/{team_id}/goal",
            "params": ["team_id", "goal_name", "due_date", "description", "multiple_owners", "owners", "color", "request_body"],
            "required": ["team_id", "goal_name"]
        },
        "update_goal": {
            "method": "PUT",
            "endpoint": "/goal/{goal_id}",
            "params": ["goal_id", "request_body"],
            "required": ["goal_id", "request_body"]
        },
        "delete_goal": {
            "method": "DELETE",
            "endpoint": "/goal/{goal_id}",
            "params": ["goal_id"],
            "required": ["goal_id"]
        },
        "get_goal": {
            "method": "GET",
            "endpoint": "/goal/{goal_id}",
            "params": ["goal_id"],
            "required": ["goal_id"]
        },
        "get_goals": {
            "method": "GET",
            "endpoint": "/team/{team_id}/goal",
            "params": ["team_id", "include_completed"],
            "required": ["team_id"]
        },
        
        # Key Results API
        "create_key_result": {
            "method": "POST",
            "endpoint": "/goal/{goal_id}/key_result",
            "params": ["goal_id", "kr_name", "owners", "type", "steps_start", "steps_end", "unit", "task_ids", "list_ids", "request_body"],
            "required": ["goal_id", "kr_name"]
        },
        "edit_key_result": {
            "method": "PUT",
            "endpoint": "/key_result/{key_result_id}",
            "params": ["key_result_id", "request_body"],
            "required": ["key_result_id", "request_body"]
        },
        "delete_key_result": {
            "method": "DELETE",
            "endpoint": "/key_result/{key_result_id}",
            "params": ["key_result_id"],
            "required": ["key_result_id"]
        },
        
        # Time Tracking API
        "get_time_entries_within_date_range": {
            "method": "GET",
            "endpoint": "/team/{team_id}/time_entries",
            "params": ["team_id", "start_date", "end_date", "assignee", "include_task_tags", "include_location_names", "space_id", "folder_id", "list_id", "task_id"],
            "required": ["team_id"]
        },
        "get_single_time_entry": {
            "method": "GET",
            "endpoint": "/team/{team_id}/time_entries/{timer_id}",
            "params": ["team_id", "timer_id"],
            "required": ["team_id", "timer_id"]
        },
        "start_time_entry": {
            "method": "POST",
            "endpoint": "/team/{team_id}/time_entries/start",
            "params": ["team_id", "tid", "description", "tags", "billable", "request_body"],
            "required": ["team_id"]
        },
        "stop_time_entry": {
            "method": "POST",
            "endpoint": "/team/{team_id}/time_entries/stop",
            "params": ["team_id"],
            "required": ["team_id"]
        },
        "delete_time_entry": {
            "method": "DELETE",
            "endpoint": "/team/{team_id}/time_entries/{timer_id}",
            "params": ["team_id", "timer_id"],
            "required": ["team_id", "timer_id"]
        },
        "update_time_entry": {
            "method": "PUT",
            "endpoint": "/team/{team_id}/time_entries/{timer_id}",
            "params": ["team_id", "timer_id", "request_body"],
            "required": ["team_id", "timer_id", "request_body"]
        },
        "create_time_entry": {
            "method": "POST",
            "endpoint": "/team/{team_id}/time_entries",
            "params": ["team_id", "start", "end", "time", "description", "tags", "tid", "billable", "request_body"],
            "required": ["team_id"]
        },
        "get_running_time_entry": {
            "method": "GET",
            "endpoint": "/team/{team_id}/time_entries/current",
            "params": ["team_id"],
            "required": ["team_id"]
        },
        
        # Views API
        "get_team_views": {
            "method": "GET",
            "endpoint": "/team/{team_id}/view",
            "params": ["team_id"],
            "required": ["team_id"]
        },
        "get_space_views": {
            "method": "GET",
            "endpoint": "/space/{space_id}/view",
            "params": ["space_id"],
            "required": ["space_id"]
        },
        "get_folder_views": {
            "method": "GET",
            "endpoint": "/folder/{folder_id}/view",
            "params": ["folder_id"],
            "required": ["folder_id"]
        },
        "get_list_views": {
            "method": "GET",
            "endpoint": "/list/{list_id}/view",
            "params": ["list_id"],
            "required": ["list_id"]
        },
        "get_view": {
            "method": "GET",
            "endpoint": "/view/{view_id}",
            "params": ["view_id"],
            "required": ["view_id"]
        },
        "create_team_view": {
            "method": "POST",
            "endpoint": "/team/{team_id}/view",
            "params": ["team_id", "view_name", "type", "request_body"],
            "required": ["team_id", "view_name", "type"]
        },
        "create_space_view": {
            "method": "POST",
            "endpoint": "/space/{space_id}/view",
            "params": ["space_id", "view_name", "type", "request_body"],
            "required": ["space_id", "view_name", "type"]
        },
        "create_folder_view": {
            "method": "POST",
            "endpoint": "/folder/{folder_id}/view",
            "params": ["folder_id", "view_name", "type", "request_body"],
            "required": ["folder_id", "view_name", "type"]
        },
        "create_list_view": {
            "method": "POST",
            "endpoint": "/list/{list_id}/view",
            "params": ["list_id", "view_name", "type", "request_body"],
            "required": ["list_id", "view_name", "type"]
        },
        "update_view": {
            "method": "PUT",
            "endpoint": "/view/{view_id}",
            "params": ["view_id", "request_body"],
            "required": ["view_id", "request_body"]
        },
        "delete_view": {
            "method": "DELETE",
            "endpoint": "/view/{view_id}",
            "params": ["view_id"],
            "required": ["view_id"]
        },
        
        # Shared Hierarchy API
        "get_shared_hierarchy": {
            "method": "GET",
            "endpoint": "/team/{team_id}/shared",
            "params": ["team_id"],
            "required": ["team_id"]
        },
        
        # Webhooks API
        "create_webhook": {
            "method": "POST",
            "endpoint": "/team/{team_id}/webhook",
            "params": ["team_id", "endpoint", "events", "space_id", "folder_id", "list_id", "task_id", "request_body"],
            "required": ["team_id", "endpoint", "events"]
        },
        "update_webhook": {
            "method": "PUT",
            "endpoint": "/webhook/{webhook_id}",
            "params": ["webhook_id", "request_body"],
            "required": ["webhook_id", "request_body"]
        },
        "delete_webhook": {
            "method": "DELETE",
            "endpoint": "/webhook/{webhook_id}",
            "params": ["webhook_id"],
            "required": ["webhook_id"]
        },
        "get_webhooks": {
            "method": "GET",
            "endpoint": "/team/{team_id}/webhook",
            "params": ["team_id"],
            "required": ["team_id"]
        },
        
        # Users API
        "get_authorized_user": {
            "method": "GET",
            "endpoint": "/user",
            "params": [],
            "required": []
        },
        "update_user": {
            "method": "PUT",
            "endpoint": "/user",
            "params": ["username", "email", "color", "request_body"],
            "required": []
        },
        "get_user": {
            "method": "GET",
            "endpoint": "/user/{user_id}",
            "params": ["user_id"],
            "required": ["user_id"]
        },
        
        # Checklists API
        "create_checklist": {
            "method": "POST",
            "endpoint": "/task/{task_id}/checklist",
            "params": ["task_id", "checklist_name", "position", "request_body"],
            "required": ["task_id", "checklist_name"]
        },
        "edit_checklist": {
            "method": "PUT",
            "endpoint": "/checklist/{checklist_id}",
            "params": ["checklist_id", "request_body"],
            "required": ["checklist_id", "request_body"]
        },
        "delete_checklist": {
            "method": "DELETE",
            "endpoint": "/checklist/{checklist_id}",
            "params": ["checklist_id"],
            "required": ["checklist_id"]
        },
        "create_checklist_item": {
            "method": "POST",
            "endpoint": "/checklist/{checklist_id}/checklist_item",
            "params": ["checklist_id", "item_name", "assignee", "request_body"],
            "required": ["checklist_id", "item_name"]
        },
        "edit_checklist_item": {
            "method": "PUT",
            "endpoint": "/checklist/{checklist_id}/checklist_item/{checklist_item_id}",
            "params": ["checklist_id", "checklist_item_id", "request_body"],
            "required": ["checklist_id", "checklist_item_id", "request_body"]
        },
        "delete_checklist_item": {
            "method": "DELETE",
            "endpoint": "/checklist/{checklist_id}/checklist_item/{checklist_item_id}",
            "params": ["checklist_id", "checklist_item_id"],
            "required": ["checklist_id", "checklist_item_id"]
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.universal_node = UniversalRequestNode()
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the ClickUp node."""
        return NodeSchema(
            name="ClickUpNode",
            description="Comprehensive ClickUp REST API integration for project management and task tracking",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The ClickUp operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                "api_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="ClickUp API token for authentication",
                    required=True
                ),
                # Common ID parameters
                "team_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Team ID for team operations",
                    required=False
                ),
                "space_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Space ID for space operations",
                    required=False
                ),
                "folder_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Folder ID for folder operations",
                    required=False
                ),
                "list_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="List ID for list operations",
                    required=False
                ),
                "task_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Task ID for task operations",
                    required=False
                ),
                "comment_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Comment ID for comment operations",
                    required=False
                ),
                "goal_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Goal ID for goal operations",
                    required=False
                ),
                "key_result_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Key Result ID for key result operations",
                    required=False
                ),
                "view_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="View ID for view operations",
                    required=False
                ),
                "webhook_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Webhook ID for webhook operations",
                    required=False
                ),
                "user_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="User ID for user operations",
                    required=False
                ),
                "checklist_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Checklist ID for checklist operations",
                    required=False
                ),
                "checklist_item_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Checklist item ID for checklist item operations",
                    required=False
                ),
                "field_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Field ID for custom field operations",
                    required=False
                ),
                "timer_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Timer ID for time tracking operations",
                    required=False
                ),
                # Content parameters
                "space_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Space name for space creation",
                    required=False
                ),
                "folder_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Folder name for folder creation",
                    required=False
                ),
                "list_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="List name for list creation",
                    required=False
                ),
                "task_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Task name for task creation",
                    required=False
                ),
                "description": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Description for various operations",
                    required=False
                ),
                "comment_text": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Comment text for comment creation",
                    required=False
                ),
                "goal_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Goal name for goal creation",
                    required=False
                ),
                "kr_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Key result name for key result creation",
                    required=False
                ),
                "view_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="View name for view creation",
                    required=False
                ),
                "checklist_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Checklist name for checklist creation",
                    required=False
                ),
                "item_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Item name for checklist item creation",
                    required=False
                ),
                "tag_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Tag name for tag operations",
                    required=False
                ),
                # Task specific parameters
                "status": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Task status",
                    required=False
                ),
                "priority": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Task priority (1-4)",
                    required=False
                ),
                "assignees": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Task assignees (user IDs)",
                    required=False
                ),
                "tags": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Task tags",
                    required=False
                ),
                "due_date": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Due date (Unix timestamp)",
                    required=False
                ),
                "due_date_time": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include time in due date",
                    required=False
                ),
                "start_date": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Start date (Unix timestamp)",
                    required=False
                ),
                "start_date_time": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include time in start date",
                    required=False
                ),
                "time_estimate": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Time estimate in milliseconds",
                    required=False
                ),
                # Common parameters
                "archived": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include archived items",
                    required=False
                ),
                "page": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Page number for pagination",
                    required=False
                ),
                "order_by": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Order by field",
                    required=False
                ),
                "reverse": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Reverse order",
                    required=False
                ),
                "subtasks": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include subtasks",
                    required=False
                ),
                "include_closed": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include closed items",
                    required=False
                ),
                # Generic request body
                "request_body": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Request body for create/update operations",
                    required=False
                )
            },
            outputs={
                "status": NodeParameterType.STRING,
                "teams": NodeParameterType.ARRAY,
                "spaces": NodeParameterType.ARRAY,
                "space_info": NodeParameterType.OBJECT,
                "folders": NodeParameterType.ARRAY,
                "folder_info": NodeParameterType.OBJECT,
                "lists": NodeParameterType.ARRAY,
                "list_info": NodeParameterType.OBJECT,
                "tasks": NodeParameterType.ARRAY,
                "task_info": NodeParameterType.OBJECT,
                "comments": NodeParameterType.ARRAY,
                "comment_info": NodeParameterType.OBJECT,
                "goals": NodeParameterType.ARRAY,
                "goal_info": NodeParameterType.OBJECT,
                "key_results": NodeParameterType.ARRAY,
                "key_result_info": NodeParameterType.OBJECT,
                "time_entries": NodeParameterType.ARRAY,
                "time_entry_info": NodeParameterType.OBJECT,
                "views": NodeParameterType.ARRAY,
                "view_info": NodeParameterType.OBJECT,
                "webhooks": NodeParameterType.ARRAY,
                "webhook_info": NodeParameterType.OBJECT,
                "user_info": NodeParameterType.OBJECT,
                "checklists": NodeParameterType.ARRAY,
                "checklist_info": NodeParameterType.OBJECT,
                "custom_fields": NodeParameterType.ARRAY,
                "members": NodeParameterType.ARRAY,
                "shared_hierarchy": NodeParameterType.OBJECT,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ClickUp-specific parameters."""
        params = node_data.get("params", {})
        
        if not params.get("operation"):
            raise NodeValidationError("Operation is required")
        if not params.get("api_token"):
            raise NodeValidationError("ClickUp API token is required")
        
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
        """Execute the ClickUp operation using UniversalRequestNode."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Get operation configuration
            operation_config = self.OPERATIONS[operation]
            
            # Prepare configuration with authentication
            config = self.CONFIG.copy()
            
            # Prepare universal request node parameters
            universal_params = {
                "config": config,
                "method": operation_config["method"],
                "endpoint": operation_config["endpoint"],
                "token": params["api_token"]
            }
            
            # Handle path parameters
            endpoint = operation_config["endpoint"]
            path_params = {
                "team_id": params.get("team_id"),
                "space_id": params.get("space_id"),
                "folder_id": params.get("folder_id"),
                "list_id": params.get("list_id"),
                "task_id": params.get("task_id"),
                "comment_id": params.get("comment_id"),
                "goal_id": params.get("goal_id"),
                "key_result_id": params.get("key_result_id"),
                "view_id": params.get("view_id"),
                "webhook_id": params.get("webhook_id"),
                "user_id": params.get("user_id"),
                "checklist_id": params.get("checklist_id"),
                "checklist_item_id": params.get("checklist_item_id"),
                "field_id": params.get("field_id"),
                "timer_id": params.get("timer_id"),
                "tag_name": params.get("tag_name"),
                "links_to": params.get("links_to")
            }
            
            for param_name, param_value in path_params.items():
                if f"{{{param_name}}}" in endpoint and param_value:
                    endpoint = endpoint.replace(f"{{{param_name}}}", param_value)
            
            universal_params["endpoint"] = endpoint
            
            # Handle query parameters and body data
            if operation_config["method"] == "GET":
                query_params = {}
                for param in operation_config.get("params", []):
                    if param in params and params[param] is not None:
                        if param not in ["team_id", "space_id", "folder_id", "list_id", "task_id", 
                                        "comment_id", "goal_id", "key_result_id", "view_id", 
                                        "webhook_id", "user_id", "checklist_id", "checklist_item_id",
                                        "field_id", "timer_id", "tag_name", "links_to"]:
                            query_params[param] = params[param]
                
                if query_params:
                    universal_params["query_params"] = query_params
            else:
                # POST/PUT/DELETE operations - prepare body data
                body_data = {}
                
                if params.get("request_body"):
                    body_data = params["request_body"]
                else:
                    # Build body based on operation
                    if operation == "create_space":
                        body_data = {
                            "name": params.get("space_name"),
                            "multiple_assignees": params.get("multiple_assignees"),
                            "features": params.get("features", {})
                        }
                    elif operation == "create_folder":
                        body_data = {"name": params.get("folder_name")}
                    elif operation == "create_list" or operation == "create_folderless_list":
                        body_data = {
                            "name": params.get("list_name"),
                            "content": params.get("content"),
                            "due_date": params.get("due_date"),
                            "priority": params.get("priority"),
                            "assignee": params.get("assignee"),
                            "status": params.get("status")
                        }
                    elif operation == "create_task":
                        body_data = {
                            "name": params.get("task_name"),
                            "description": params.get("description"),
                            "assignees": params.get("assignees", []),
                            "tags": params.get("tags", []),
                            "status": params.get("status"),
                            "priority": params.get("priority"),
                            "due_date": params.get("due_date"),
                            "due_date_time": params.get("due_date_time"),
                            "time_estimate": params.get("time_estimate"),
                            "start_date": params.get("start_date"),
                            "start_date_time": params.get("start_date_time"),
                            "notify_all": params.get("notify_all"),
                            "parent": params.get("parent"),
                            "links_to": params.get("links_to"),
                            "check_required_custom_fields": params.get("check_required_custom_fields"),
                            "custom_fields": params.get("custom_fields", [])
                        }
                    elif operation == "create_task_comment":
                        body_data = {
                            "comment_text": params.get("comment_text"),
                            "assignee": params.get("assignee"),
                            "notify_all": params.get("notify_all")
                        }
                    elif operation == "create_goal":
                        body_data = {
                            "name": params.get("goal_name"),
                            "due_date": params.get("due_date"),
                            "description": params.get("description"),
                            "multiple_owners": params.get("multiple_owners"),
                            "owners": params.get("owners", []),
                            "color": params.get("color")
                        }
                    elif operation == "create_key_result":
                        body_data = {
                            "name": params.get("kr_name"),
                            "owners": params.get("owners", []),
                            "type": params.get("type"),
                            "steps_start": params.get("steps_start"),
                            "steps_end": params.get("steps_end"),
                            "unit": params.get("unit"),
                            "task_ids": params.get("task_ids", []),
                            "list_ids": params.get("list_ids", [])
                        }
                    elif operation == "create_space_tag":
                        body_data = {
                            "name": params.get("tag_name"),
                            "tag_fg": params.get("tag_fg"),
                            "tag_bg": params.get("tag_bg")
                        }
                    elif operation.startswith("create_") and "view" in operation:
                        body_data = {
                            "name": params.get("view_name"),
                            "type": params.get("type")
                        }
                    elif operation == "create_webhook":
                        body_data = {
                            "endpoint": params.get("endpoint"),
                            "events": params.get("events", []),
                            "space_id": params.get("space_id"),
                            "folder_id": params.get("folder_id"),
                            "list_id": params.get("list_id"),
                            "task_id": params.get("task_id")
                        }
                    elif operation == "create_checklist":
                        body_data = {
                            "name": params.get("checklist_name"),
                            "position": params.get("position")
                        }
                    elif operation == "create_checklist_item":
                        body_data = {
                            "name": params.get("item_name"),
                            "assignee": params.get("assignee")
                        }
                    elif operation == "set_custom_field_value":
                        body_data = {
                            "value": params.get("value"),
                            "value_options": params.get("value_options")
                        }
                    elif operation == "add_dependency":
                        body_data = {
                            "depends_on": params.get("depends_on"),
                            "dependency_of": params.get("dependency_of")
                        }
                    elif operation == "start_time_entry":
                        body_data = {
                            "tid": params.get("tid"),
                            "description": params.get("description"),
                            "tags": params.get("tags", []),
                            "billable": params.get("billable")
                        }
                    elif operation == "create_time_entry":
                        body_data = {
                            "start": params.get("start"),
                            "end": params.get("end"),
                            "time": params.get("time"),
                            "description": params.get("description"),
                            "tags": params.get("tags", []),
                            "tid": params.get("tid"),
                            "billable": params.get("billable")
                        }
                
                # Clean up None values
                body_data = {k: v for k, v in body_data.items() if v is not None}
                
                if body_data:
                    universal_params["body"] = body_data
            
            # Execute the request
            result = await self.universal_node.execute({
                "params": universal_params
            })
            
            if result.get("status") == "success":
                response_data = result.get("response", {})
                
                # Transform response based on operation type
                if operation == "get_teams":
                    return {
                        "status": "success",
                        "teams": response_data.get("teams", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_space") and operation != "get_space_tags" and operation != "get_space_views":
                    if operation == "get_spaces":
                        return {
                            "status": "success",
                            "spaces": response_data.get("spaces", []),
                            "response_data": response_data
                        }
                    else:
                        return {
                            "status": "success",
                            "space_info": response_data,
                            "response_data": response_data
                        }
                elif operation.startswith("create_space") or operation.startswith("update_space"):
                    return {
                        "status": "success",
                        "space_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_folder"):
                    if operation == "get_folders":
                        return {
                            "status": "success",
                            "folders": response_data.get("folders", []),
                            "response_data": response_data
                        }
                    else:
                        return {
                            "status": "success",
                            "folder_info": response_data,
                            "response_data": response_data
                        }
                elif operation.startswith("create_folder") or operation.startswith("update_folder"):
                    return {
                        "status": "success",
                        "folder_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_list") or operation.startswith("get_folderless_list"):
                    if operation in ["get_lists", "get_folderless_lists"]:
                        return {
                            "status": "success",
                            "lists": response_data.get("lists", []),
                            "response_data": response_data
                        }
                    else:
                        return {
                            "status": "success",
                            "list_info": response_data,
                            "response_data": response_data
                        }
                elif operation.startswith("create_list") or operation.startswith("update_list") or operation.startswith("create_folderless_list"):
                    return {
                        "status": "success",
                        "list_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_task"):
                    if operation == "get_tasks" or operation == "get_filtered_team_tasks":
                        return {
                            "status": "success",
                            "tasks": response_data.get("tasks", []),
                            "response_data": response_data
                        }
                    else:
                        return {
                            "status": "success",
                            "task_info": response_data,
                            "response_data": response_data
                        }
                elif operation.startswith("create_task") or operation.startswith("update_task"):
                    return {
                        "status": "success",
                        "task_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_") and "comment" in operation:
                    if operation == "get_task_comments":
                        return {
                            "status": "success",
                            "comments": response_data.get("comments", []),
                            "response_data": response_data
                        }
                    else:
                        return {
                            "status": "success",
                            "comment_info": response_data,
                            "response_data": response_data
                        }
                elif operation.startswith("create_task_comment") or operation.startswith("update_comment"):
                    return {
                        "status": "success",
                        "comment_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_goal"):
                    if operation == "get_goals":
                        return {
                            "status": "success",
                            "goals": response_data.get("goals", []),
                            "response_data": response_data
                        }
                    else:
                        return {
                            "status": "success",
                            "goal_info": response_data,
                            "response_data": response_data
                        }
                elif operation.startswith("create_goal") or operation.startswith("update_goal"):
                    return {
                        "status": "success",
                        "goal_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("create_key_result") or operation.startswith("edit_key_result"):
                    return {
                        "status": "success",
                        "key_result_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_time_entries") or operation.startswith("get_single_time_entry") or operation.startswith("get_running_time_entry"):
                    if operation == "get_time_entries_within_date_range":
                        return {
                            "status": "success",
                            "time_entries": response_data.get("data", []),
                            "response_data": response_data
                        }
                    else:
                        return {
                            "status": "success",
                            "time_entry_info": response_data,
                            "response_data": response_data
                        }
                elif operation.startswith("start_time_entry") or operation.startswith("create_time_entry") or operation.startswith("update_time_entry"):
                    return {
                        "status": "success",
                        "time_entry_info": response_data,
                        "response_data": response_data
                    }
                elif operation.endswith("_views") or operation.startswith("get_view"):
                    if operation.endswith("_views"):
                        return {
                            "status": "success",
                            "views": response_data.get("views", []),
                            "response_data": response_data
                        }
                    else:
                        return {
                            "status": "success",
                            "view_info": response_data,
                            "response_data": response_data
                        }
                elif operation.startswith("create_") and "view" in operation or operation.startswith("update_view"):
                    return {
                        "status": "success",
                        "view_info": response_data,
                        "response_data": response_data
                    }
                elif operation == "get_webhooks":
                    return {
                        "status": "success",
                        "webhooks": response_data.get("webhooks", []),
                        "response_data": response_data
                    }
                elif operation.startswith("create_webhook") or operation.startswith("update_webhook"):
                    return {
                        "status": "success",
                        "webhook_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_user") or operation.startswith("get_authorized_user") or operation.startswith("update_user"):
                    return {
                        "status": "success",
                        "user_info": response_data.get("user", response_data),
                        "response_data": response_data
                    }
                elif operation.startswith("create_checklist") or operation.startswith("edit_checklist"):
                    return {
                        "status": "success",
                        "checklist_info": response_data,
                        "response_data": response_data
                    }
                elif operation == "get_accessible_custom_fields":
                    return {
                        "status": "success",
                        "custom_fields": response_data.get("fields", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_") and "member" in operation:
                    return {
                        "status": "success",
                        "members": response_data.get("members", []),
                        "response_data": response_data
                    }
                elif operation == "get_shared_hierarchy":
                    return {
                        "status": "success",
                        "shared_hierarchy": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("delete_") or operation.startswith("remove_"):
                    return {
                        "status": "success",
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
            logger.error(f"ClickUp operation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "CLICKUP_ERROR"
            }
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'universal_node'):
            await self.universal_node.close()