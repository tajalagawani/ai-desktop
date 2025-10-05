"""
ClickUp Node - Comprehensive integration with ClickUp REST API
Provides access to all ClickUp API operations including tasks, spaces, lists, folders, teams, goals, and time tracking.
"""

import logging
import json
import asyncio
import time
import os
import ssl
import base64
import hashlib
import hmac
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timezone
from urllib.parse import urlencode

# Import HTTP client for API calls
import aiohttp
import certifi

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    except ImportError:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )

# Configure logging
logger = logging.getLogger(__name__)

class ClickUpOperation:
    """Operations available on ClickUp REST API."""
    
    # Authentication
    GET_ACCESS_TOKEN = "get_access_token"
    
    # Teams (Workspaces) API
    GET_TEAMS = "get_teams"
    
    # Spaces API
    GET_SPACES = "get_spaces"
    GET_SPACE = "get_space"
    CREATE_SPACE = "create_space"
    UPDATE_SPACE = "update_space"
    DELETE_SPACE = "delete_space"
    
    # Folders API
    GET_FOLDERS = "get_folders"
    GET_FOLDER = "get_folder"
    CREATE_FOLDER = "create_folder"
    UPDATE_FOLDER = "update_folder"
    DELETE_FOLDER = "delete_folder"
    
    # Lists API
    GET_LISTS = "get_lists"
    GET_LIST = "get_list"
    CREATE_LIST = "create_list"
    UPDATE_LIST = "update_list"
    DELETE_LIST = "delete_list"
    GET_FOLDERLESS_LISTS = "get_folderless_lists"
    CREATE_FOLDERLESS_LIST = "create_folderless_list"
    
    # Tasks API
    GET_TASKS = "get_tasks"
    GET_TASK = "get_task"
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    GET_FILTERED_TEAM_TASKS = "get_filtered_team_tasks"
    
    # Task Comments API
    GET_TASK_COMMENTS = "get_task_comments"
    CREATE_TASK_COMMENT = "create_task_comment"
    UPDATE_COMMENT = "update_comment"
    DELETE_COMMENT = "delete_comment"
    
    # Task Dependencies API
    ADD_DEPENDENCY = "add_dependency"
    DELETE_DEPENDENCY = "delete_dependency"
    ADD_TASK_LINK = "add_task_link"
    DELETE_TASK_LINK = "delete_task_link"
    
    # Task Attachments API
    CREATE_TASK_ATTACHMENT = "create_task_attachment"
    
    # Custom Fields API
    GET_ACCESSIBLE_CUSTOM_FIELDS = "get_accessible_custom_fields"
    SET_CUSTOM_FIELD_VALUE = "set_custom_field_value"
    REMOVE_CUSTOM_FIELD_VALUE = "remove_custom_field_value"
    
    # Members API
    GET_TASK_MEMBERS = "get_task_members"
    GET_LIST_MEMBERS = "get_list_members"
    
    # Tags API
    GET_SPACE_TAGS = "get_space_tags"
    CREATE_SPACE_TAG = "create_space_tag"
    EDIT_TAG = "edit_tag"
    DELETE_TAG = "delete_tag"
    ADD_TAG_TO_TASK = "add_tag_to_task"
    REMOVE_TAG_FROM_TASK = "remove_tag_from_task"
    
    # Goals API
    CREATE_GOAL = "create_goal"
    UPDATE_GOAL = "update_goal"
    DELETE_GOAL = "delete_goal"
    GET_GOAL = "get_goal"
    GET_GOALS = "get_goals"
    
    # Key Results API
    CREATE_KEY_RESULT = "create_key_result"
    EDIT_KEY_RESULT = "edit_key_result"
    DELETE_KEY_RESULT = "delete_key_result"
    
    # Time Tracking API
    GET_TIME_ENTRIES_WITHIN_DATE_RANGE = "get_time_entries_within_date_range"
    GET_SINGLE_TIME_ENTRY = "get_single_time_entry"
    START_TIME_ENTRY = "start_time_entry"
    STOP_TIME_ENTRY = "stop_time_entry"
    DELETE_TIME_ENTRY = "delete_time_entry"
    UPDATE_TIME_ENTRY = "update_time_entry"
    CREATE_TIME_ENTRY = "create_time_entry"
    GET_RUNNING_TIME_ENTRY = "get_running_time_entry"
    
    # Views API
    GET_TEAM_VIEWS = "get_team_views"
    GET_SPACE_VIEWS = "get_space_views"
    GET_FOLDER_VIEWS = "get_folder_views"
    GET_LIST_VIEWS = "get_list_views"
    GET_VIEW = "get_view"
    CREATE_TEAM_VIEW = "create_team_view"
    CREATE_SPACE_VIEW = "create_space_view"
    CREATE_FOLDER_VIEW = "create_folder_view"
    CREATE_LIST_VIEW = "create_list_view"
    UPDATE_VIEW = "update_view"
    DELETE_VIEW = "delete_view"
    
    # Shared Hierarchy API
    GET_SHARED_HIERARCHY = "get_shared_hierarchy"
    
    # Webhooks API
    CREATE_WEBHOOK = "create_webhook"
    UPDATE_WEBHOOK = "update_webhook"
    DELETE_WEBHOOK = "delete_webhook"
    GET_WEBHOOKS = "get_webhooks"
    
    # Users API
    GET_AUTHORIZED_USER = "get_authorized_user"
    UPDATE_USER = "update_user"
    GET_USER = "get_user"
    
    # Checklists API
    CREATE_CHECKLIST = "create_checklist"
    EDIT_CHECKLIST = "edit_checklist"
    DELETE_CHECKLIST = "delete_checklist"
    CREATE_CHECKLIST_ITEM = "create_checklist_item"
    EDIT_CHECKLIST_ITEM = "edit_checklist_item"
    DELETE_CHECKLIST_ITEM = "delete_checklist_item"

class ClickUpAuthType:
    """Authentication types for ClickUp API."""
    API_TOKEN = "api_token"
    OAUTH = "oauth"

class ClickUpHelper:
    """Helper class for ClickUp API operations."""
    
    @staticmethod
    def format_task_data(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format task data for API requests."""
        formatted = {}
        
        # Basic fields
        if 'name' in task_data:
            formatted['name'] = task_data['name']
        if 'description' in task_data:
            formatted['description'] = task_data['description']
        if 'status' in task_data:
            formatted['status'] = task_data['status']
        if 'priority' in task_data:
            formatted['priority'] = task_data['priority']
        if 'due_date' in task_data:
            formatted['due_date'] = task_data['due_date']
        if 'due_date_time' in task_data:
            formatted['due_date_time'] = task_data['due_date_time']
        if 'start_date' in task_data:
            formatted['start_date'] = task_data['start_date']
        if 'start_date_time' in task_data:
            formatted['start_date_time'] = task_data['start_date_time']
        if 'time_estimate' in task_data:
            formatted['time_estimate'] = task_data['time_estimate']
        if 'assignees' in task_data:
            formatted['assignees'] = task_data['assignees']
        if 'tags' in task_data:
            formatted['tags'] = task_data['tags']
        if 'parent' in task_data:
            formatted['parent'] = task_data['parent']
        if 'links_to' in task_data:
            formatted['links_to'] = task_data['links_to']
        if 'check_required_custom_fields' in task_data:
            formatted['check_required_custom_fields'] = task_data['check_required_custom_fields']
        if 'custom_fields' in task_data:
            formatted['custom_fields'] = task_data['custom_fields']
            
        return formatted
    
    @staticmethod
    def format_space_data(space_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format space data for API requests."""
        formatted = {}
        
        if 'name' in space_data:
            formatted['name'] = space_data['name']
        if 'multiple_assignees' in space_data:
            formatted['multiple_assignees'] = space_data['multiple_assignees']
        if 'features' in space_data:
            formatted['features'] = space_data['features']
            
        return formatted
    
    @staticmethod
    def format_list_data(list_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format list data for API requests."""
        formatted = {}
        
        if 'name' in list_data:
            formatted['name'] = list_data['name']
        if 'content' in list_data:
            formatted['content'] = list_data['content']
        if 'due_date' in list_data:
            formatted['due_date'] = list_data['due_date']
        if 'due_date_time' in list_data:
            formatted['due_date_time'] = list_data['due_date_time']
        if 'priority' in list_data:
            formatted['priority'] = list_data['priority']
        if 'assignee' in list_data:
            formatted['assignee'] = list_data['assignee']
        if 'status' in list_data:
            formatted['status'] = list_data['status']
            
        return formatted
    
    @staticmethod
    def format_goal_data(goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format goal data for API requests."""
        formatted = {}
        
        if 'name' in goal_data:
            formatted['name'] = goal_data['name']
        if 'description' in goal_data:
            formatted['description'] = goal_data['description']
        if 'due_date' in goal_data:
            formatted['due_date'] = goal_data['due_date']
        if 'color' in goal_data:
            formatted['color'] = goal_data['color']
        if 'multiple_owners' in goal_data:
            formatted['multiple_owners'] = goal_data['multiple_owners']
        if 'owners' in goal_data:
            formatted['owners'] = goal_data['owners']
            
        return formatted
    
    @staticmethod
    def format_time_entry_data(time_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format time entry data for API requests."""
        formatted = {}
        
        if 'description' in time_data:
            formatted['description'] = time_data['description']
        if 'start' in time_data:
            formatted['start'] = time_data['start']
        if 'end' in time_data:
            formatted['end'] = time_data['end']
        if 'billable' in time_data:
            formatted['billable'] = time_data['billable']
        if 'duration' in time_data:
            formatted['duration'] = time_data['duration']
        if 'assignee' in time_data:
            formatted['assignee'] = time_data['assignee']
        if 'tags' in time_data:
            formatted['tags'] = time_data['tags']
            
        return formatted
    
    @staticmethod
    def build_task_filters(filters: Dict[str, Any]) -> Dict[str, str]:
        """Build query parameters for task filtering."""
        params = {}
        
        if 'archived' in filters:
            params['archived'] = str(filters['archived']).lower()
        if 'page' in filters:
            params['page'] = str(filters['page'])
        if 'order_by' in filters:
            params['order_by'] = filters['order_by']
        if 'reverse' in filters:
            params['reverse'] = str(filters['reverse']).lower()
        if 'subtasks' in filters:
            params['subtasks'] = str(filters['subtasks']).lower()
        if 'statuses' in filters:
            if isinstance(filters['statuses'], list):
                params['statuses[]'] = filters['statuses']
            else:
                params['statuses[]'] = [filters['statuses']]
        if 'include_closed' in filters:
            params['include_closed'] = str(filters['include_closed']).lower()
        if 'assignees' in filters:
            if isinstance(filters['assignees'], list):
                params['assignees[]'] = filters['assignees']
            else:
                params['assignees[]'] = [filters['assignees']]
        if 'tags' in filters:
            if isinstance(filters['tags'], list):
                params['tags[]'] = filters['tags']
            else:
                params['tags[]'] = [filters['tags']]
        if 'due_date_gt' in filters:
            params['due_date_gt'] = str(filters['due_date_gt'])
        if 'due_date_lt' in filters:
            params['due_date_lt'] = str(filters['due_date_lt'])
        if 'date_created_gt' in filters:
            params['date_created_gt'] = str(filters['date_created_gt'])
        if 'date_created_lt' in filters:
            params['date_created_lt'] = str(filters['date_created_lt'])
        if 'date_updated_gt' in filters:
            params['date_updated_gt'] = str(filters['date_updated_gt'])
        if 'date_updated_lt' in filters:
            params['date_updated_lt'] = str(filters['date_updated_lt'])
        if 'custom_fields' in filters:
            for field_id, value in filters['custom_fields'].items():
                params[f'custom_fields[{field_id}]'] = str(value)
                
        return params

class ClickUpNode(BaseNode):
    """
    ClickUp Node for comprehensive API integration.
    
    Provides access to all ClickUp API operations including tasks, spaces,
    lists, folders, teams, goals, time tracking, and project management.
    """

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.clickup.com/api/v2"
        self.session = None
        self.rate_limit_remaining = 100
        self.rate_limit_reset = 0

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            name="clickup",
            description="Comprehensive ClickUp API integration for project management and task tracking",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="The ClickUp operation to perform",
                    required=True,
                    options=[
                        # Authentication
                        ClickUpOperation.GET_ACCESS_TOKEN,
                        
                        # Teams
                        ClickUpOperation.GET_TEAMS,
                        
                        # Spaces
                        ClickUpOperation.GET_SPACES,
                        ClickUpOperation.GET_SPACE,
                        ClickUpOperation.CREATE_SPACE,
                        ClickUpOperation.UPDATE_SPACE,
                        ClickUpOperation.DELETE_SPACE,
                        
                        # Folders
                        ClickUpOperation.GET_FOLDERS,
                        ClickUpOperation.GET_FOLDER,
                        ClickUpOperation.CREATE_FOLDER,
                        ClickUpOperation.UPDATE_FOLDER,
                        ClickUpOperation.DELETE_FOLDER,
                        
                        # Lists
                        ClickUpOperation.GET_LISTS,
                        ClickUpOperation.GET_LIST,
                        ClickUpOperation.CREATE_LIST,
                        ClickUpOperation.UPDATE_LIST,
                        ClickUpOperation.DELETE_LIST,
                        ClickUpOperation.GET_FOLDERLESS_LISTS,
                        ClickUpOperation.CREATE_FOLDERLESS_LIST,
                        
                        # Tasks
                        ClickUpOperation.GET_TASKS,
                        ClickUpOperation.GET_TASK,
                        ClickUpOperation.CREATE_TASK,
                        ClickUpOperation.UPDATE_TASK,
                        ClickUpOperation.DELETE_TASK,
                        ClickUpOperation.GET_FILTERED_TEAM_TASKS,
                        
                        # Task Comments
                        ClickUpOperation.GET_TASK_COMMENTS,
                        ClickUpOperation.CREATE_TASK_COMMENT,
                        ClickUpOperation.UPDATE_COMMENT,
                        ClickUpOperation.DELETE_COMMENT,
                        
                        # Task Dependencies
                        ClickUpOperation.ADD_DEPENDENCY,
                        ClickUpOperation.DELETE_DEPENDENCY,
                        ClickUpOperation.ADD_TASK_LINK,
                        ClickUpOperation.DELETE_TASK_LINK,
                        
                        # Task Attachments
                        ClickUpOperation.CREATE_TASK_ATTACHMENT,
                        
                        # Custom Fields
                        ClickUpOperation.GET_ACCESSIBLE_CUSTOM_FIELDS,
                        ClickUpOperation.SET_CUSTOM_FIELD_VALUE,
                        ClickUpOperation.REMOVE_CUSTOM_FIELD_VALUE,
                        
                        # Members
                        ClickUpOperation.GET_TASK_MEMBERS,
                        ClickUpOperation.GET_LIST_MEMBERS,
                        
                        # Tags
                        ClickUpOperation.GET_SPACE_TAGS,
                        ClickUpOperation.CREATE_SPACE_TAG,
                        ClickUpOperation.EDIT_TAG,
                        ClickUpOperation.DELETE_TAG,
                        ClickUpOperation.ADD_TAG_TO_TASK,
                        ClickUpOperation.REMOVE_TAG_FROM_TASK,
                        
                        # Goals
                        ClickUpOperation.CREATE_GOAL,
                        ClickUpOperation.UPDATE_GOAL,
                        ClickUpOperation.DELETE_GOAL,
                        ClickUpOperation.GET_GOAL,
                        ClickUpOperation.GET_GOALS,
                        
                        # Key Results
                        ClickUpOperation.CREATE_KEY_RESULT,
                        ClickUpOperation.EDIT_KEY_RESULT,
                        ClickUpOperation.DELETE_KEY_RESULT,
                        
                        # Time Tracking
                        ClickUpOperation.GET_TIME_ENTRIES_WITHIN_DATE_RANGE,
                        ClickUpOperation.GET_SINGLE_TIME_ENTRY,
                        ClickUpOperation.START_TIME_ENTRY,
                        ClickUpOperation.STOP_TIME_ENTRY,
                        ClickUpOperation.DELETE_TIME_ENTRY,
                        ClickUpOperation.UPDATE_TIME_ENTRY,
                        ClickUpOperation.CREATE_TIME_ENTRY,
                        ClickUpOperation.GET_RUNNING_TIME_ENTRY,
                        
                        # Views
                        ClickUpOperation.GET_TEAM_VIEWS,
                        ClickUpOperation.GET_SPACE_VIEWS,
                        ClickUpOperation.GET_FOLDER_VIEWS,
                        ClickUpOperation.GET_LIST_VIEWS,
                        ClickUpOperation.GET_VIEW,
                        ClickUpOperation.CREATE_TEAM_VIEW,
                        ClickUpOperation.CREATE_SPACE_VIEW,
                        ClickUpOperation.CREATE_FOLDER_VIEW,
                        ClickUpOperation.CREATE_LIST_VIEW,
                        ClickUpOperation.UPDATE_VIEW,
                        ClickUpOperation.DELETE_VIEW,
                        
                        # Shared Hierarchy
                        ClickUpOperation.GET_SHARED_HIERARCHY,
                        
                        # Webhooks
                        ClickUpOperation.CREATE_WEBHOOK,
                        ClickUpOperation.UPDATE_WEBHOOK,
                        ClickUpOperation.DELETE_WEBHOOK,
                        ClickUpOperation.GET_WEBHOOKS,
                        
                        # Users
                        ClickUpOperation.GET_AUTHORIZED_USER,
                        ClickUpOperation.UPDATE_USER,
                        ClickUpOperation.GET_USER,
                        
                        # Checklists
                        ClickUpOperation.CREATE_CHECKLIST,
                        ClickUpOperation.EDIT_CHECKLIST,
                        ClickUpOperation.DELETE_CHECKLIST,
                        ClickUpOperation.CREATE_CHECKLIST_ITEM,
                        ClickUpOperation.EDIT_CHECKLIST_ITEM,
                        ClickUpOperation.DELETE_CHECKLIST_ITEM
                    ]
                ),
                NodeParameter(
                    name="auth_type",
                    type=NodeParameterType.STRING,
                    description="Authentication method",
                    required=True,
                    default=ClickUpAuthType.API_TOKEN,
                    options=[ClickUpAuthType.API_TOKEN, ClickUpAuthType.OAUTH]
                ),
                NodeParameter(
                    name="api_token",
                    type=NodeParameterType.STRING,
                    description="ClickUp API Token",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="client_id",
                    type=NodeParameterType.STRING,
                    description="OAuth Client ID",
                    required=False
                ),
                NodeParameter(
                    name="client_secret",
                    type=NodeParameterType.STRING,
                    description="OAuth Client Secret",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="team_id",
                    type=NodeParameterType.STRING,
                    description="Team (Workspace) ID",
                    required=False
                ),
                NodeParameter(
                    name="space_id",
                    type=NodeParameterType.STRING,
                    description="Space ID",
                    required=False
                ),
                NodeParameter(
                    name="folder_id",
                    type=NodeParameterType.STRING,
                    description="Folder ID",
                    required=False
                ),
                NodeParameter(
                    name="list_id",
                    type=NodeParameterType.STRING,
                    description="List ID",
                    required=False
                ),
                NodeParameter(
                    name="task_id",
                    type=NodeParameterType.STRING,
                    description="Task ID",
                    required=False
                ),
                NodeParameter(
                    name="comment_id",
                    type=NodeParameterType.STRING,
                    description="Comment ID",
                    required=False
                ),
                NodeParameter(
                    name="goal_id",
                    type=NodeParameterType.STRING,
                    description="Goal ID",
                    required=False
                ),
                NodeParameter(
                    name="key_result_id",
                    type=NodeParameterType.STRING,
                    description="Key Result ID",
                    required=False
                ),
                NodeParameter(
                    name="view_id",
                    type=NodeParameterType.STRING,
                    description="View ID",
                    required=False
                ),
                NodeParameter(
                    name="webhook_id",
                    type=NodeParameterType.STRING,
                    description="Webhook ID",
                    required=False
                ),
                NodeParameter(
                    name="user_id",
                    type=NodeParameterType.STRING,
                    description="User ID",
                    required=False
                ),
                NodeParameter(
                    name="checklist_id",
                    type=NodeParameterType.STRING,
                    description="Checklist ID",
                    required=False
                ),
                NodeParameter(
                    name="checklist_item_id",
                    type=NodeParameterType.STRING,
                    description="Checklist Item ID",
                    required=False
                ),
                NodeParameter(
                    name="tag_name",
                    type=NodeParameterType.STRING,
                    description="Tag name",
                    required=False
                ),
                NodeParameter(
                    name="custom_field_id",
                    type=NodeParameterType.STRING,
                    description="Custom Field ID",
                    required=False
                ),
                NodeParameter(
                    name="timer_id",
                    type=NodeParameterType.STRING,
                    description="Timer ID",
                    required=False
                ),
                NodeParameter(
                    name="depends_on",
                    type=NodeParameterType.STRING,
                    description="Task ID that this task depends on",
                    required=False
                ),
                NodeParameter(
                    name="dependency_of",
                    type=NodeParameterType.STRING,
                    description="Task ID that depends on this task",
                    required=False
                ),
                NodeParameter(
                    name="link_id",
                    type=NodeParameterType.STRING,
                    description="Link ID for task relationships",
                    required=False
                ),
                NodeParameter(
                    name="task_data",
                    type=NodeParameterType.OBJECT,
                    description="Task data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="space_data",
                    type=NodeParameterType.OBJECT,
                    description="Space data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="folder_data",
                    type=NodeParameterType.OBJECT,
                    description="Folder data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="list_data",
                    type=NodeParameterType.OBJECT,
                    description="List data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="goal_data",
                    type=NodeParameterType.OBJECT,
                    description="Goal data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="key_result_data",
                    type=NodeParameterType.OBJECT,
                    description="Key result data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="time_entry_data",
                    type=NodeParameterType.OBJECT,
                    description="Time entry data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="view_data",
                    type=NodeParameterType.OBJECT,
                    description="View data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="webhook_data",
                    type=NodeParameterType.OBJECT,
                    description="Webhook data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="user_data",
                    type=NodeParameterType.OBJECT,
                    description="User data for updates",
                    required=False
                ),
                NodeParameter(
                    name="checklist_data",
                    type=NodeParameterType.OBJECT,
                    description="Checklist data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="comment_data",
                    type=NodeParameterType.OBJECT,
                    description="Comment data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="custom_field_data",
                    type=NodeParameterType.OBJECT,
                    description="Custom field data for updates",
                    required=False
                ),
                NodeParameter(
                    name="tag_data",
                    type=NodeParameterType.OBJECT,
                    description="Tag data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="filters",
                    type=NodeParameterType.OBJECT,
                    description="Filters for listing operations",
                    required=False
                ),
                NodeParameter(
                    name="include_subtasks",
                    type=NodeParameterType.BOOLEAN,
                    description="Include subtasks in results",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="include_closed",
                    type=NodeParameterType.BOOLEAN,
                    description="Include closed items",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="archived",
                    type=NodeParameterType.BOOLEAN,
                    description="Include archived items",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="page",
                    type=NodeParameterType.INTEGER,
                    description="Page number for pagination",
                    required=False,
                    default=0
                ),
                NodeParameter(
                    name="order_by",
                    type=NodeParameterType.STRING,
                    description="Field to order results by",
                    required=False,
                    options=["id", "created", "updated", "due_date"]
                ),
                NodeParameter(
                    name="reverse",
                    type=NodeParameterType.BOOLEAN,
                    description="Reverse the order",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="start_date",
                    type=NodeParameterType.INTEGER,
                    description="Start date (Unix timestamp in milliseconds)",
                    required=False
                ),
                NodeParameter(
                    name="end_date",
                    type=NodeParameterType.INTEGER,
                    description="End date (Unix timestamp in milliseconds)",
                    required=False
                ),
                NodeParameter(
                    name="assignee_id",
                    type=NodeParameterType.INTEGER,
                    description="Assignee user ID for time tracking",
                    required=False
                ),
                NodeParameter(
                    name="include_location_names",
                    type=NodeParameterType.BOOLEAN,
                    description="Include location names in time entries",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="timeout",
                    type=NodeParameterType.INTEGER,
                    description="Request timeout in seconds",
                    required=False,
                    default=30
                ),
                NodeParameter(
                    name="retry_attempts",
                    type=NodeParameterType.INTEGER,
                    description="Number of retry attempts for failed requests",
                    required=False,
                    default=3
                ),
                NodeParameter(
                    name="additional_headers",
                    type=NodeParameterType.OBJECT,
                    description="Additional HTTP headers",
                    required=False
                )
            ],
            outputs=[
                "success",
                "error",
                "response_data",
                "status_code",
                "team_id",
                "space_id",
                "folder_id",
                "list_id",
                "task_id",
                "goal_id",
                "rate_limit_remaining",
                "rate_limit_reset"
            ],
            metadata={
                "category": "project_management",
                "vendor": "clickup",
                "api_version": "2.0",
                "documentation": "https://developer.clickup.com/docs",
                "rate_limits": {
                    "requests_per_hour": 100,
                    "varies_by_plan": True
                }
            }
        )

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with SSL context."""
        if self.session is None or self.session.closed:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        return self.session

    def _get_headers(self, api_token: str, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
        
        if additional_headers:
            headers.update(additional_headers)
            
        return headers

    async def _handle_rate_limiting(self, response: aiohttp.ClientResponse):
        """Handle rate limiting based on response headers."""
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        
        if 'X-RateLimit-Reset' in response.headers:
            self.rate_limit_reset = int(response.headers['X-RateLimit-Reset'])
        
        if response.status == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            await asyncio.sleep(retry_after)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        api_token: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        retry_attempts: int = 3
    ) -> Tuple[Dict[str, Any], int]:
        """Make HTTP request to ClickUp API with retries and error handling."""
        
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(api_token, additional_headers)
        
        for attempt in range(retry_attempts + 1):
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if data else None,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    
                    await self._handle_rate_limiting(response)
                    
                    if response.status == 429 and attempt < retry_attempts:
                        continue
                    
                    response_text = await response.text()
                    
                    try:
                        if response_text:
                            response_data = json.loads(response_text)
                        else:
                            response_data = {}
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    
                    return response_data, response.status
                    
            except asyncio.TimeoutError:
                if attempt < retry_attempts:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise NodeValidationError(f"Request timeout after {timeout} seconds")
            except Exception as e:
                if attempt < retry_attempts:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise NodeValidationError(f"Request failed: {str(e)}")
        
        raise NodeValidationError("All retry attempts failed")

    # Authentication Methods
    async def _get_access_token(self, client_id: str, client_secret: str, code: str) -> Dict[str, Any]:
        """Get OAuth access token."""
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/oauth/token",
            api_token="",
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Team Methods
    async def _get_teams(self, api_token: str) -> Dict[str, Any]:
        """Get authorized teams."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/team",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    # Space Methods
    async def _get_spaces(self, team_id: str, api_token: str, archived: bool = False) -> Dict[str, Any]:
        """Get spaces in a team."""
        params = {"archived": str(archived).lower()}
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/team/{team_id}/space",
            api_token=api_token,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_space(self, space_id: str, api_token: str) -> Dict[str, Any]:
        """Get a space."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/space/{space_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_space(self, team_id: str, space_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Create a space."""
        formatted_data = ClickUpHelper.format_space_data(space_data)
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/team/{team_id}/space",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_space(self, space_id: str, space_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Update a space."""
        formatted_data = ClickUpHelper.format_space_data(space_data)
        
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/space/{space_id}",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_space(self, space_id: str, api_token: str) -> Dict[str, Any]:
        """Delete a space."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/space/{space_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    # Folder Methods
    async def _get_folders(self, space_id: str, api_token: str, archived: bool = False) -> Dict[str, Any]:
        """Get folders in a space."""
        params = {"archived": str(archived).lower()}
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/space/{space_id}/folder",
            api_token=api_token,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_folder(self, folder_id: str, api_token: str) -> Dict[str, Any]:
        """Get a folder."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/folder/{folder_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_folder(self, space_id: str, folder_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Create a folder."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/space/{space_id}/folder",
            api_token=api_token,
            data=folder_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_folder(self, folder_id: str, folder_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Update a folder."""
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/folder/{folder_id}",
            api_token=api_token,
            data=folder_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_folder(self, folder_id: str, api_token: str) -> Dict[str, Any]:
        """Delete a folder."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/folder/{folder_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    # List Methods
    async def _get_lists(self, folder_id: str, api_token: str, archived: bool = False) -> Dict[str, Any]:
        """Get lists in a folder."""
        params = {"archived": str(archived).lower()}
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/folder/{folder_id}/list",
            api_token=api_token,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_folderless_lists(self, space_id: str, api_token: str, archived: bool = False) -> Dict[str, Any]:
        """Get folderless lists in a space."""
        params = {"archived": str(archived).lower()}
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/space/{space_id}/list",
            api_token=api_token,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_list(self, list_id: str, api_token: str) -> Dict[str, Any]:
        """Get a list."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/list/{list_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_list(self, folder_id: str, list_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Create a list in a folder."""
        formatted_data = ClickUpHelper.format_list_data(list_data)
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/folder/{folder_id}/list",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_folderless_list(self, space_id: str, list_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Create a folderless list in a space."""
        formatted_data = ClickUpHelper.format_list_data(list_data)
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/space/{space_id}/list",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_list(self, list_id: str, list_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Update a list."""
        formatted_data = ClickUpHelper.format_list_data(list_data)
        
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/list/{list_id}",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_list(self, list_id: str, api_token: str) -> Dict[str, Any]:
        """Delete a list."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/list/{list_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    # Task Methods
    async def _get_tasks(self, list_id: str, api_token: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get tasks in a list."""
        params = {}
        
        if filters:
            params.update(ClickUpHelper.build_task_filters(filters))
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/list/{list_id}/task",
            api_token=api_token,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_task(self, task_id: str, api_token: str, include_subtasks: bool = False) -> Dict[str, Any]:
        """Get a task."""
        params = {"include_subtasks": str(include_subtasks).lower()}
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/task/{task_id}",
            api_token=api_token,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_task(self, list_id: str, task_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Create a task."""
        formatted_data = ClickUpHelper.format_task_data(task_data)
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/list/{list_id}/task",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_task(self, task_id: str, task_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Update a task."""
        formatted_data = ClickUpHelper.format_task_data(task_data)
        
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/task/{task_id}",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_task(self, task_id: str, api_token: str) -> Dict[str, Any]:
        """Delete a task."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/task/{task_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_filtered_team_tasks(self, team_id: str, api_token: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get filtered team tasks."""
        params = {}
        
        if filters:
            params.update(ClickUpHelper.build_task_filters(filters))
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/team/{team_id}/task",
            api_token=api_token,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    # Task Comments Methods
    async def _get_task_comments(self, task_id: str, api_token: str) -> Dict[str, Any]:
        """Get task comments."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/task/{task_id}/comment",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_task_comment(self, task_id: str, comment_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Create a task comment."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/task/{task_id}/comment",
            api_token=api_token,
            data=comment_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_comment(self, comment_id: str, comment_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Update a comment."""
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/comment/{comment_id}",
            api_token=api_token,
            data=comment_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_comment(self, comment_id: str, api_token: str) -> Dict[str, Any]:
        """Delete a comment."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/comment/{comment_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    # Task Dependencies Methods
    async def _add_dependency(self, task_id: str, depends_on: str, api_token: str) -> Dict[str, Any]:
        """Add task dependency."""
        data = {"depends_on": depends_on}
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/task/{task_id}/dependency",
            api_token=api_token,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_dependency(self, task_id: str, depends_on: str, api_token: str) -> Dict[str, Any]:
        """Delete task dependency."""
        params = {"depends_on": depends_on}
        
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/task/{task_id}/dependency",
            api_token=api_token,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _add_task_link(self, task_id: str, links_to: str, api_token: str) -> Dict[str, Any]:
        """Add task link."""
        data = {"links_to": links_to}
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/task/{task_id}/link",
            api_token=api_token,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_task_link(self, task_id: str, link_id: str, api_token: str) -> Dict[str, Any]:
        """Delete task link."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/task/{task_id}/link/{link_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    # Custom Fields Methods
    async def _get_accessible_custom_fields(self, list_id: str, api_token: str) -> Dict[str, Any]:
        """Get accessible custom fields for a list."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/list/{list_id}/field",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _set_custom_field_value(self, task_id: str, field_id: str, custom_field_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Set custom field value."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/task/{task_id}/field/{field_id}",
            api_token=api_token,
            data=custom_field_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _remove_custom_field_value(self, task_id: str, field_id: str, api_token: str) -> Dict[str, Any]:
        """Remove custom field value."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/task/{task_id}/field/{field_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    # Tags Methods
    async def _get_space_tags(self, space_id: str, api_token: str) -> Dict[str, Any]:
        """Get space tags."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/space/{space_id}/tag",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_space_tag(self, space_id: str, tag_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Create space tag."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/space/{space_id}/tag",
            api_token=api_token,
            data=tag_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _edit_tag(self, space_id: str, tag_name: str, tag_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Edit tag."""
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/space/{space_id}/tag/{tag_name}",
            api_token=api_token,
            data=tag_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_tag(self, space_id: str, tag_name: str, api_token: str) -> Dict[str, Any]:
        """Delete tag."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/space/{space_id}/tag/{tag_name}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _add_tag_to_task(self, task_id: str, tag_name: str, api_token: str) -> Dict[str, Any]:
        """Add tag to task."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/task/{task_id}/tag/{tag_name}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _remove_tag_from_task(self, task_id: str, tag_name: str, api_token: str) -> Dict[str, Any]:
        """Remove tag from task."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/task/{task_id}/tag/{tag_name}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    # Goals Methods
    async def _create_goal(self, team_id: str, goal_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Create a goal."""
        formatted_data = ClickUpHelper.format_goal_data(goal_data)
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/team/{team_id}/goal",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_goal(self, goal_id: str, api_token: str) -> Dict[str, Any]:
        """Get a goal."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/goal/{goal_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_goal(self, goal_id: str, goal_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Update a goal."""
        formatted_data = ClickUpHelper.format_goal_data(goal_data)
        
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/goal/{goal_id}",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_goal(self, goal_id: str, api_token: str) -> Dict[str, Any]:
        """Delete a goal."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/goal/{goal_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_goals(self, team_id: str, api_token: str, include_completed: bool = False) -> Dict[str, Any]:
        """Get goals."""
        params = {"include_completed": str(include_completed).lower()}
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/team/{team_id}/goal",
            api_token=api_token,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    # Time Tracking Methods
    async def _get_time_entries_within_date_range(self, team_id: str, start_date: int, end_date: int, api_token: str, assignee_id: Optional[int] = None, include_location_names: bool = False) -> Dict[str, Any]:
        """Get time entries within date range."""
        params = {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "include_location_names": str(include_location_names).lower()
        }
        
        if assignee_id:
            params["assignee"] = str(assignee_id)
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/team/{team_id}/time_entries",
            api_token=api_token,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _start_time_entry(self, team_id: str, time_entry_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Start time entry."""
        formatted_data = ClickUpHelper.format_time_entry_data(time_entry_data)
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/team/{team_id}/time_entries/start",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _stop_time_entry(self, team_id: str, api_token: str) -> Dict[str, Any]:
        """Stop time entry."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/team/{team_id}/time_entries/stop",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_time_entry(self, team_id: str, time_entry_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Create time entry."""
        formatted_data = ClickUpHelper.format_time_entry_data(time_entry_data)
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/team/{team_id}/time_entries",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_single_time_entry(self, team_id: str, timer_id: str, api_token: str) -> Dict[str, Any]:
        """Get single time entry."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/team/{team_id}/time_entries/{timer_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_time_entry(self, team_id: str, timer_id: str, time_entry_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Update time entry."""
        formatted_data = ClickUpHelper.format_time_entry_data(time_entry_data)
        
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/team/{team_id}/time_entries/{timer_id}",
            api_token=api_token,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_time_entry(self, team_id: str, timer_id: str, api_token: str) -> Dict[str, Any]:
        """Delete time entry."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/team/{team_id}/time_entries/{timer_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_running_time_entry(self, team_id: str, api_token: str, assignee_id: Optional[int] = None) -> Dict[str, Any]:
        """Get running time entry."""
        params = {}
        
        if assignee_id:
            params["assignee"] = str(assignee_id)
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/team/{team_id}/time_entries/current",
            api_token=api_token,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    # Webhook Methods
    async def _create_webhook(self, team_id: str, webhook_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Create webhook."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/team/{team_id}/webhook",
            api_token=api_token,
            data=webhook_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_webhooks(self, team_id: str, api_token: str) -> Dict[str, Any]:
        """Get webhooks."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/team/{team_id}/webhook",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_webhook(self, webhook_id: str, webhook_data: Dict[str, Any], api_token: str) -> Dict[str, Any]:
        """Update webhook."""
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/webhook/{webhook_id}",
            api_token=api_token,
            data=webhook_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_webhook(self, webhook_id: str, api_token: str) -> Dict[str, Any]:
        """Delete webhook."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/webhook/{webhook_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    # User Methods
    async def _get_authorized_user(self, api_token: str) -> Dict[str, Any]:
        """Get authorized user."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/user",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_user(self, user_id: str, api_token: str) -> Dict[str, Any]:
        """Get user."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/user/{user_id}",
            api_token=api_token
        )
        
        return {"response": response_data, "status_code": status_code}

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the ClickUp operation."""
        try:
            # Validate required parameters
            operation = parameters.get("operation")
            if not operation:
                raise NodeValidationError("Operation is required")

            auth_type = parameters.get("auth_type", ClickUpAuthType.API_TOKEN)
            timeout = parameters.get("timeout", 30)
            retry_attempts = parameters.get("retry_attempts", 3)
            
            # Get authentication credentials
            api_token = parameters.get("api_token")
            client_id = parameters.get("client_id")
            client_secret = parameters.get("client_secret")
            
            # Validate authentication
            if auth_type == ClickUpAuthType.API_TOKEN:
                if not api_token:
                    raise NodeValidationError("API token is required for token authentication")
            elif auth_type == ClickUpAuthType.OAUTH:
                if not client_id or not client_secret:
                    raise NodeValidationError("Client ID and secret are required for OAuth authentication")

            # Execute the operation
            result = None
            
            if operation == ClickUpOperation.GET_ACCESS_TOKEN:
                code = parameters.get("code")
                if not code:
                    raise NodeValidationError("Authorization code is required")
                result = await self._get_access_token(client_id, client_secret, code)
            
            elif operation == ClickUpOperation.GET_TEAMS:
                result = await self._get_teams(api_token)
            
            # Space operations
            elif operation == ClickUpOperation.GET_SPACES:
                team_id = parameters.get("team_id")
                archived = parameters.get("archived", False)
                if not team_id:
                    raise NodeValidationError("Team ID is required")
                result = await self._get_spaces(team_id, api_token, archived)
            
            elif operation == ClickUpOperation.GET_SPACE:
                space_id = parameters.get("space_id")
                if not space_id:
                    raise NodeValidationError("Space ID is required")
                result = await self._get_space(space_id, api_token)
            
            elif operation == ClickUpOperation.CREATE_SPACE:
                team_id = parameters.get("team_id")
                space_data = parameters.get("space_data")
                if not team_id or not space_data:
                    raise NodeValidationError("Team ID and space data are required")
                result = await self._create_space(team_id, space_data, api_token)
            
            elif operation == ClickUpOperation.UPDATE_SPACE:
                space_id = parameters.get("space_id")
                space_data = parameters.get("space_data")
                if not space_id or not space_data:
                    raise NodeValidationError("Space ID and space data are required")
                result = await self._update_space(space_id, space_data, api_token)
            
            elif operation == ClickUpOperation.DELETE_SPACE:
                space_id = parameters.get("space_id")
                if not space_id:
                    raise NodeValidationError("Space ID is required")
                result = await self._delete_space(space_id, api_token)
            
            # Task operations
            elif operation == ClickUpOperation.GET_TASKS:
                list_id = parameters.get("list_id")
                filters = parameters.get("filters")
                if not list_id:
                    raise NodeValidationError("List ID is required")
                result = await self._get_tasks(list_id, api_token, filters)
            
            elif operation == ClickUpOperation.GET_TASK:
                task_id = parameters.get("task_id")
                include_subtasks = parameters.get("include_subtasks", False)
                if not task_id:
                    raise NodeValidationError("Task ID is required")
                result = await self._get_task(task_id, api_token, include_subtasks)
            
            elif operation == ClickUpOperation.CREATE_TASK:
                list_id = parameters.get("list_id")
                task_data = parameters.get("task_data")
                if not list_id or not task_data:
                    raise NodeValidationError("List ID and task data are required")
                result = await self._create_task(list_id, task_data, api_token)
            
            elif operation == ClickUpOperation.UPDATE_TASK:
                task_id = parameters.get("task_id")
                task_data = parameters.get("task_data")
                if not task_id or not task_data:
                    raise NodeValidationError("Task ID and task data are required")
                result = await self._update_task(task_id, task_data, api_token)
            
            elif operation == ClickUpOperation.DELETE_TASK:
                task_id = parameters.get("task_id")
                if not task_id:
                    raise NodeValidationError("Task ID is required")
                result = await self._delete_task(task_id, api_token)
            
            # Goal operations
            elif operation == ClickUpOperation.CREATE_GOAL:
                team_id = parameters.get("team_id")
                goal_data = parameters.get("goal_data")
                if not team_id or not goal_data:
                    raise NodeValidationError("Team ID and goal data are required")
                result = await self._create_goal(team_id, goal_data, api_token)
            
            elif operation == ClickUpOperation.GET_GOAL:
                goal_id = parameters.get("goal_id")
                if not goal_id:
                    raise NodeValidationError("Goal ID is required")
                result = await self._get_goal(goal_id, api_token)
            
            # Time tracking operations
            elif operation == ClickUpOperation.GET_TIME_ENTRIES_WITHIN_DATE_RANGE:
                team_id = parameters.get("team_id")
                start_date = parameters.get("start_date")
                end_date = parameters.get("end_date")
                assignee_id = parameters.get("assignee_id")
                include_location_names = parameters.get("include_location_names", False)
                if not team_id or not start_date or not end_date:
                    raise NodeValidationError("Team ID, start date, and end date are required")
                result = await self._get_time_entries_within_date_range(team_id, start_date, end_date, api_token, assignee_id, include_location_names)
            
            elif operation == ClickUpOperation.START_TIME_ENTRY:
                team_id = parameters.get("team_id")
                time_entry_data = parameters.get("time_entry_data")
                if not team_id or not time_entry_data:
                    raise NodeValidationError("Team ID and time entry data are required")
                result = await self._start_time_entry(team_id, time_entry_data, api_token)
            
            elif operation == ClickUpOperation.STOP_TIME_ENTRY:
                team_id = parameters.get("team_id")
                if not team_id:
                    raise NodeValidationError("Team ID is required")
                result = await self._stop_time_entry(team_id, api_token)
            
            # Webhook operations
            elif operation == ClickUpOperation.CREATE_WEBHOOK:
                team_id = parameters.get("team_id")
                webhook_data = parameters.get("webhook_data")
                if not team_id or not webhook_data:
                    raise NodeValidationError("Team ID and webhook data are required")
                result = await self._create_webhook(team_id, webhook_data, api_token)
            
            elif operation == ClickUpOperation.GET_WEBHOOKS:
                team_id = parameters.get("team_id")
                if not team_id:
                    raise NodeValidationError("Team ID is required")
                result = await self._get_webhooks(team_id, api_token)
            
            # User operations
            elif operation == ClickUpOperation.GET_AUTHORIZED_USER:
                result = await self._get_authorized_user(api_token)
            
            else:
                raise NodeValidationError(f"Unsupported operation: {operation}")

            if not result:
                raise NodeValidationError("Operation failed to return a result")

            # Extract response data and status
            response_data = result.get("response", {})
            status_code = result.get("status_code", 200)
            
            # Determine success based on status code
            success = 200 <= status_code < 300
            
            # Extract specific IDs from response for convenience
            team_id = None
            space_id = None
            folder_id = None
            list_id = None
            task_id = None
            goal_id = None
            
            if isinstance(response_data, dict):
                team_id = response_data.get("team", {}).get("id") if "team" in response_data else response_data.get("id") if "name" in response_data else None
                space_id = response_data.get("space", {}).get("id") if "space" in response_data else response_data.get("id") if "statuses" in response_data else None
                folder_id = response_data.get("folder", {}).get("id") if "folder" in response_data else response_data.get("id") if "lists" in response_data else None
                list_id = response_data.get("list", {}).get("id") if "list" in response_data else response_data.get("id") if "tasks" in response_data else None
                task_id = response_data.get("id") if "status" in response_data and "assignees" in response_data else None
                goal_id = response_data.get("id") if "key_results" in response_data else None

            return {
                "success": success,
                "error": None if success else response_data.get("err", f"HTTP {status_code}"),
                "response_data": response_data,
                "status_code": status_code,
                "team_id": team_id,
                "space_id": space_id,
                "folder_id": folder_id,
                "list_id": list_id,
                "task_id": task_id,
                "goal_id": goal_id,
                "rate_limit_remaining": self.rate_limit_remaining,
                "rate_limit_reset": self.rate_limit_reset
            }

        except NodeValidationError as e:
            logger.error(f"Validation error in ClickUpNode: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response_data": None,
                "status_code": 400,
                "team_id": None,
                "space_id": None,
                "folder_id": None,
                "list_id": None,
                "task_id": None,
                "goal_id": None,
                "rate_limit_remaining": self.rate_limit_remaining,
                "rate_limit_reset": self.rate_limit_reset
            }
        except Exception as e:
            logger.error(f"Unexpected error in ClickUpNode: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "response_data": None,
                "status_code": 500,
                "team_id": None,
                "space_id": None,
                "folder_id": None,
                "list_id": None,
                "task_id": None,
                "goal_id": None,
                "rate_limit_remaining": self.rate_limit_remaining,
                "rate_limit_reset": self.rate_limit_reset
            }

    async def cleanup(self):
        """Cleanup resources."""
        if self.session and not self.session.closed:
            await self.session.close()

# Register the node
if __name__ == "__main__":
    node = ClickUpNode()
    print(f"ClickUpNode registered with {len(node.get_schema().parameters)} parameters")