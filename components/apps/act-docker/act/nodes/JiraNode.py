"""
Jira Node - Comprehensive integration with Jira Cloud REST API

Provides access to all Jira API operations including issues, projects, users, workflows, and project management.
Supports complete Jira workflow integration with issue tracking, project management, user administration,
and enterprise collaboration features.

Key capabilities include: Issue creation, tracking and management, project administration and configuration,
user and group management, workflow automation, time tracking and reporting, custom fields and permissions,
dashboard and filter management, webhook integration, and comprehensive search with JQL.

Built for production environments with multiple authentication methods (Basic Auth, OAuth 2.0, Personal Access Tokens),
comprehensive error handling, rate limiting compliance, and enterprise features for development teams.
"""

import logging
from typing import Dict, Any, Optional
import base64

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

class JiraNode(BaseNode):
    """Comprehensive Jira Cloud REST API integration node."""
    
    # Embedded configuration for Jira API
    CONFIG = {
        "base_url": "",  # Dynamic based on jira_domain
        "authentication": {
            "type": "basic_auth",  # Will be overridden based on auth_type
            "header": "Authorization"
        },
        "headers": {
            "Accept": "application/json",
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
    
    # Complete operations mapping for Jira API (80+ operations)
    OPERATIONS = {
        # Issue Operations
        "create_issue": {
            "method": "POST",
            "endpoint": "/issue",
            "params": ["issue_data"],
            "required": ["issue_data"]
        },
        "get_issue": {
            "method": "GET",
            "endpoint": "/issue/{issue_id_or_key}",
            "params": ["issue_id_or_key", "expand", "fields"],
            "required": ["issue_id_or_key"]
        },
        "update_issue": {
            "method": "PUT",
            "endpoint": "/issue/{issue_id_or_key}",
            "params": ["issue_id_or_key", "issue_data"],
            "required": ["issue_id_or_key", "issue_data"]
        },
        "delete_issue": {
            "method": "DELETE",
            "endpoint": "/issue/{issue_id_or_key}",
            "params": ["issue_id_or_key"],
            "required": ["issue_id_or_key"]
        },
        "search_issues": {
            "method": "POST",
            "endpoint": "/search",
            "params": ["jql", "search_filters", "start_at", "max_results", "expand", "fields"],
            "required": []
        },
        "get_issue_transitions": {
            "method": "GET",
            "endpoint": "/issue/{issue_id_or_key}/transitions",
            "params": ["issue_id_or_key"],
            "required": ["issue_id_or_key"]
        },
        "transition_issue": {
            "method": "POST",
            "endpoint": "/issue/{issue_id_or_key}/transitions",
            "params": ["issue_id_or_key", "transition_data"],
            "required": ["issue_id_or_key", "transition_data"]
        },
        "assign_issue": {
            "method": "PUT",
            "endpoint": "/issue/{issue_id_or_key}/assignee",
            "params": ["issue_id_or_key", "user_account_id"],
            "required": ["issue_id_or_key", "user_account_id"]
        },
        "get_issue_changelog": {
            "method": "GET",
            "endpoint": "/issue/{issue_id_or_key}/changelog",
            "params": ["issue_id_or_key", "start_at", "max_results"],
            "required": ["issue_id_or_key"]
        },
        "get_issue_watchers": {
            "method": "GET",
            "endpoint": "/issue/{issue_id_or_key}/watchers",
            "params": ["issue_id_or_key"],
            "required": ["issue_id_or_key"]
        },
        "add_watcher": {
            "method": "POST",
            "endpoint": "/issue/{issue_id_or_key}/watchers",
            "params": ["issue_id_or_key", "user_account_id"],
            "required": ["issue_id_or_key", "user_account_id"]
        },
        "remove_watcher": {
            "method": "DELETE",
            "endpoint": "/issue/{issue_id_or_key}/watchers",
            "params": ["issue_id_or_key", "user_account_id"],
            "required": ["issue_id_or_key", "user_account_id"]
        },
        "get_issue_votes": {
            "method": "GET",
            "endpoint": "/issue/{issue_id_or_key}/votes",
            "params": ["issue_id_or_key"],
            "required": ["issue_id_or_key"]
        },
        "vote_for_issue": {
            "method": "POST",
            "endpoint": "/issue/{issue_id_or_key}/votes",
            "params": ["issue_id_or_key"],
            "required": ["issue_id_or_key"]
        },
        "remove_vote": {
            "method": "DELETE",
            "endpoint": "/issue/{issue_id_or_key}/votes",
            "params": ["issue_id_or_key"],
            "required": ["issue_id_or_key"]
        },
        
        # Issue Comments
        "get_issue_comments": {
            "method": "GET",
            "endpoint": "/issue/{issue_id_or_key}/comment",
            "params": ["issue_id_or_key", "start_at", "max_results", "expand"],
            "required": ["issue_id_or_key"]
        },
        "add_comment": {
            "method": "POST",
            "endpoint": "/issue/{issue_id_or_key}/comment",
            "params": ["issue_id_or_key", "comment_data"],
            "required": ["issue_id_or_key", "comment_data"]
        },
        "update_comment": {
            "method": "PUT",
            "endpoint": "/issue/{issue_id_or_key}/comment/{comment_id}",
            "params": ["issue_id_or_key", "comment_id", "comment_data"],
            "required": ["issue_id_or_key", "comment_id", "comment_data"]
        },
        "delete_comment": {
            "method": "DELETE",
            "endpoint": "/issue/{issue_id_or_key}/comment/{comment_id}",
            "params": ["issue_id_or_key", "comment_id"],
            "required": ["issue_id_or_key", "comment_id"]
        },
        
        # Issue Attachments
        "get_issue_attachments": {
            "method": "GET",
            "endpoint": "/issue/{issue_id_or_key}/attachments",
            "params": ["issue_id_or_key"],
            "required": ["issue_id_or_key"]
        },
        "get_attachment": {
            "method": "GET",
            "endpoint": "/attachment/{attachment_id}",
            "params": ["attachment_id"],
            "required": ["attachment_id"]
        },
        "delete_attachment": {
            "method": "DELETE",
            "endpoint": "/attachment/{attachment_id}",
            "params": ["attachment_id"],
            "required": ["attachment_id"]
        },
        
        # Issue Links
        "create_issue_link": {
            "method": "POST",
            "endpoint": "/issueLink",
            "params": ["link_data"],
            "required": ["link_data"]
        },
        "get_issue_link": {
            "method": "GET",
            "endpoint": "/issueLink/{link_id}",
            "params": ["link_id"],
            "required": ["link_id"]
        },
        "delete_issue_link": {
            "method": "DELETE",
            "endpoint": "/issueLink/{link_id}",
            "params": ["link_id"],
            "required": ["link_id"]
        },
        
        # Projects
        "get_all_projects": {
            "method": "GET",
            "endpoint": "/project",
            "params": ["expand"],
            "required": []
        },
        "get_project": {
            "method": "GET",
            "endpoint": "/project/{project_id_or_key}",
            "params": ["project_id_or_key", "expand"],
            "required": ["project_id_or_key"]
        },
        "create_project": {
            "method": "POST",
            "endpoint": "/project",
            "params": ["project_data"],
            "required": ["project_data"]
        },
        "update_project": {
            "method": "PUT",
            "endpoint": "/project/{project_id_or_key}",
            "params": ["project_id_or_key", "project_data"],
            "required": ["project_id_or_key", "project_data"]
        },
        "delete_project": {
            "method": "DELETE",
            "endpoint": "/project/{project_id_or_key}",
            "params": ["project_id_or_key"],
            "required": ["project_id_or_key"]
        },
        "get_project_roles": {
            "method": "GET",
            "endpoint": "/project/{project_id_or_key}/role",
            "params": ["project_id_or_key"],
            "required": ["project_id_or_key"]
        },
        "get_project_role_details": {
            "method": "GET",
            "endpoint": "/project/{project_id_or_key}/role/{role_id}",
            "params": ["project_id_or_key", "role_id"],
            "required": ["project_id_or_key", "role_id"]
        },
        "get_project_statuses": {
            "method": "GET",
            "endpoint": "/project/{project_id_or_key}/statuses",
            "params": ["project_id_or_key"],
            "required": ["project_id_or_key"]
        },
        
        # Project Components
        "get_project_components": {
            "method": "GET",
            "endpoint": "/project/{project_id_or_key}/components",
            "params": ["project_id_or_key"],
            "required": ["project_id_or_key"]
        },
        "create_component": {
            "method": "POST",
            "endpoint": "/component",
            "params": ["component_data"],
            "required": ["component_data"]
        },
        "get_component": {
            "method": "GET",
            "endpoint": "/component/{component_id}",
            "params": ["component_id"],
            "required": ["component_id"]
        },
        "update_component": {
            "method": "PUT",
            "endpoint": "/component/{component_id}",
            "params": ["component_id", "component_data"],
            "required": ["component_id", "component_data"]
        },
        "delete_component": {
            "method": "DELETE",
            "endpoint": "/component/{component_id}",
            "params": ["component_id"],
            "required": ["component_id"]
        },
        
        # Project Versions
        "get_project_versions": {
            "method": "GET",
            "endpoint": "/project/{project_id_or_key}/versions",
            "params": ["project_id_or_key"],
            "required": ["project_id_or_key"]
        },
        "create_version": {
            "method": "POST",
            "endpoint": "/version",
            "params": ["version_data"],
            "required": ["version_data"]
        },
        "get_version": {
            "method": "GET",
            "endpoint": "/version/{version_id}",
            "params": ["version_id"],
            "required": ["version_id"]
        },
        "update_version": {
            "method": "PUT",
            "endpoint": "/version/{version_id}",
            "params": ["version_id", "version_data"],
            "required": ["version_id", "version_data"]
        },
        "delete_version": {
            "method": "DELETE",
            "endpoint": "/version/{version_id}",
            "params": ["version_id"],
            "required": ["version_id"]
        },
        
        # Users
        "get_current_user": {
            "method": "GET",
            "endpoint": "/myself",
            "params": ["expand"],
            "required": []
        },
        "get_user": {
            "method": "GET",
            "endpoint": "/user",
            "params": ["user_account_id", "expand"],
            "required": ["user_account_id"]
        },
        "find_users": {
            "method": "GET",
            "endpoint": "/user/search",
            "params": ["query", "start_at", "max_results", "include_inactive"],
            "required": ["query"]
        },
        "find_assignable_users": {
            "method": "GET",
            "endpoint": "/user/assignable/search",
            "params": ["query", "project_id_or_key", "issue_id_or_key", "start_at", "max_results"],
            "required": ["query"]
        },
        
        # Groups
        "get_group": {
            "method": "GET",
            "endpoint": "/group",
            "params": ["group_name", "expand"],
            "required": ["group_name"]
        },
        "create_group": {
            "method": "POST",
            "endpoint": "/group",
            "params": ["group_name"],
            "required": ["group_name"]
        },
        "find_groups": {
            "method": "GET",
            "endpoint": "/groups/picker",
            "params": ["query", "max_results"],
            "required": []
        },
        
        # Workflows
        "get_all_workflows": {
            "method": "GET",
            "endpoint": "/workflow",
            "params": [],
            "required": []
        },
        "get_workflow": {
            "method": "GET",
            "endpoint": "/workflow/{workflow_id}",
            "params": ["workflow_id"],
            "required": ["workflow_id"]
        },
        
        # Issue Types
        "get_all_issue_types": {
            "method": "GET",
            "endpoint": "/issuetype",
            "params": [],
            "required": []
        },
        "get_issue_type": {
            "method": "GET",
            "endpoint": "/issuetype/{issue_type_id}",
            "params": ["issue_type_id"],
            "required": ["issue_type_id"]
        },
        "create_issue_type": {
            "method": "POST",
            "endpoint": "/issuetype",
            "params": ["issue_type_data"],
            "required": ["issue_type_data"]
        },
        "update_issue_type": {
            "method": "PUT",
            "endpoint": "/issuetype/{issue_type_id}",
            "params": ["issue_type_id", "issue_type_data"],
            "required": ["issue_type_id", "issue_type_data"]
        },
        "delete_issue_type": {
            "method": "DELETE",
            "endpoint": "/issuetype/{issue_type_id}",
            "params": ["issue_type_id"],
            "required": ["issue_type_id"]
        },
        
        # Priorities
        "get_priorities": {
            "method": "GET",
            "endpoint": "/priority",
            "params": [],
            "required": []
        },
        "get_priority": {
            "method": "GET",
            "endpoint": "/priority/{priority_id}",
            "params": ["priority_id"],
            "required": ["priority_id"]
        },
        
        # Resolutions
        "get_resolutions": {
            "method": "GET",
            "endpoint": "/resolution",
            "params": [],
            "required": []
        },
        "get_resolution": {
            "method": "GET",
            "endpoint": "/resolution/{resolution_id}",
            "params": ["resolution_id"],
            "required": ["resolution_id"]
        },
        
        # Status
        "get_all_statuses": {
            "method": "GET",
            "endpoint": "/status",
            "params": [],
            "required": []
        },
        "get_status": {
            "method": "GET",
            "endpoint": "/status/{status_id}",
            "params": ["status_id"],
            "required": ["status_id"]
        },
        
        # Custom Fields
        "get_fields": {
            "method": "GET",
            "endpoint": "/field",
            "params": [],
            "required": []
        },
        "create_custom_field": {
            "method": "POST",
            "endpoint": "/field",
            "params": ["field_data"],
            "required": ["field_data"]
        },
        "update_custom_field": {
            "method": "PUT",
            "endpoint": "/field/{field_id}",
            "params": ["field_id", "field_data"],
            "required": ["field_id", "field_data"]
        },
        "get_custom_field_options": {
            "method": "GET",
            "endpoint": "/customFieldOption/{field_id}",
            "params": ["field_id"],
            "required": ["field_id"]
        },
        
        # Permissions
        "get_my_permissions": {
            "method": "GET",
            "endpoint": "/mypermissions",
            "params": ["project_id_or_key", "issue_id_or_key"],
            "required": []
        },
        "get_all_permissions": {
            "method": "GET",
            "endpoint": "/permissions",
            "params": [],
            "required": []
        },
        
        # Dashboards
        "get_all_dashboards": {
            "method": "GET",
            "endpoint": "/dashboard",
            "params": ["start_at", "max_results"],
            "required": []
        },
        "get_dashboard": {
            "method": "GET",
            "endpoint": "/dashboard/{dashboard_id}",
            "params": ["dashboard_id"],
            "required": ["dashboard_id"]
        },
        
        # Filters
        "get_favourite_filters": {
            "method": "GET",
            "endpoint": "/filter/favourite",
            "params": ["expand"],
            "required": []
        },
        "get_filter": {
            "method": "GET",
            "endpoint": "/filter/{filter_id}",
            "params": ["filter_id", "expand"],
            "required": ["filter_id"]
        },
        "create_filter": {
            "method": "POST",
            "endpoint": "/filter",
            "params": ["filter_data"],
            "required": ["filter_data"]
        },
        "update_filter": {
            "method": "PUT",
            "endpoint": "/filter/{filter_id}",
            "params": ["filter_id", "filter_data"],
            "required": ["filter_id", "filter_data"]
        },
        "delete_filter": {
            "method": "DELETE",
            "endpoint": "/filter/{filter_id}",
            "params": ["filter_id"],
            "required": ["filter_id"]
        },
        
        # Time Tracking / Worklogs
        "get_issue_worklogs": {
            "method": "GET",
            "endpoint": "/issue/{issue_id_or_key}/worklog",
            "params": ["issue_id_or_key", "start_at", "max_results"],
            "required": ["issue_id_or_key"]
        },
        "add_worklog": {
            "method": "POST",
            "endpoint": "/issue/{issue_id_or_key}/worklog",
            "params": ["issue_id_or_key", "worklog_data"],
            "required": ["issue_id_or_key", "worklog_data"]
        },
        "update_worklog": {
            "method": "PUT",
            "endpoint": "/issue/{issue_id_or_key}/worklog/{worklog_id}",
            "params": ["issue_id_or_key", "worklog_id", "worklog_data"],
            "required": ["issue_id_or_key", "worklog_id", "worklog_data"]
        },
        "delete_worklog": {
            "method": "DELETE",
            "endpoint": "/issue/{issue_id_or_key}/worklog/{worklog_id}",
            "params": ["issue_id_or_key", "worklog_id"],
            "required": ["issue_id_or_key", "worklog_id"]
        },
        
        # Labels
        "get_labels": {
            "method": "GET",
            "endpoint": "/label",
            "params": ["start_at", "max_results"],
            "required": []
        },
        
        # Server Info
        "get_server_info": {
            "method": "GET",
            "endpoint": "/serverInfo",
            "params": [],
            "required": []
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.universal_node = UniversalRequestNode()
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Jira node."""
        return NodeSchema(
            name="JiraNode",
            description="Comprehensive Jira Cloud REST API integration for issue tracking and project management",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Jira operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                "auth_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Authentication method",
                    required=True,
                    enum=["basic_auth", "oauth2", "personal_access_token"]
                ),
                "jira_domain": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Jira domain (e.g., your-domain.atlassian.net)",
                    required=True
                ),
                "username": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Jira username/email (for basic auth)",
                    required=False
                ),
                "password": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Jira password/API token (for basic auth)",
                    required=False
                ),
                "access_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 access token",
                    required=False
                ),
                "personal_access_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Personal Access Token",
                    required=False
                ),
                # Issue parameters
                "issue_id_or_key": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Issue ID or key",
                    required=False
                ),
                "issue_data": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Issue data for creation/update",
                    required=False
                ),
                # Project parameters
                "project_id_or_key": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Project ID or key",
                    required=False
                ),
                "project_data": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Project data for creation/update",
                    required=False
                ),
                # Comment parameters
                "comment_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Comment ID",
                    required=False
                ),
                "comment_data": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Comment data for creation/update",
                    required=False
                ),
                # Component parameters
                "component_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Component ID",
                    required=False
                ),
                "component_data": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Component data for creation/update",
                    required=False
                ),
                # Version parameters
                "version_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Version ID",
                    required=False
                ),
                "version_data": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Version data for creation/update",
                    required=False
                ),
                # User parameters
                "user_account_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="User account ID",
                    required=False
                ),
                # Group parameters
                "group_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Group name",
                    required=False
                ),
                # Workflow parameters
                "workflow_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Workflow ID",
                    required=False
                ),
                # Issue type parameters
                "issue_type_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Issue type ID",
                    required=False
                ),
                "issue_type_data": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Issue type data for creation/update",
                    required=False
                ),
                # Priority parameters
                "priority_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Priority ID",
                    required=False
                ),
                # Resolution parameters
                "resolution_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Resolution ID",
                    required=False
                ),
                # Status parameters
                "status_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Status ID",
                    required=False
                ),
                # Field parameters
                "field_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Custom field ID",
                    required=False
                ),
                "field_data": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Field data for creation/update",
                    required=False
                ),
                # Attachment parameters
                "attachment_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Attachment ID",
                    required=False
                ),
                # Link parameters
                "link_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Issue link ID",
                    required=False
                ),
                "link_data": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Issue link data",
                    required=False
                ),
                # Worklog parameters
                "worklog_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Worklog ID",
                    required=False
                ),
                "worklog_data": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Worklog data for creation/update",
                    required=False
                ),
                # Filter parameters
                "filter_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Filter ID",
                    required=False
                ),
                "filter_data": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Filter data for creation/update",
                    required=False
                ),
                # Dashboard parameters
                "dashboard_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Dashboard ID",
                    required=False
                ),
                # Role parameters
                "role_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Project role ID",
                    required=False
                ),
                # Transition parameters
                "transition_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Transition ID",
                    required=False
                ),
                "transition_data": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Transition data",
                    required=False
                ),
                # Search parameters
                "search_filters": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Filters for JQL search",
                    required=False
                ),
                "jql": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="JQL query string",
                    required=False
                ),
                "query": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Search query string",
                    required=False
                ),
                # Common parameters
                "expand": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Expand parameter for additional details",
                    required=False
                ),
                "fields": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Comma-separated list of fields to return",
                    required=False
                ),
                "max_results": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of results to return",
                    required=False
                ),
                "start_at": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Starting index for pagination",
                    required=False
                ),
                "include_inactive": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include inactive users/groups",
                    required=False
                ),
                "timeout": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Request timeout in seconds",
                    required=False
                ),
                "additional_headers": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Additional HTTP headers",
                    required=False
                )
            },
            outputs={
                "status": NodeParameterType.STRING,
                "issues": NodeParameterType.ARRAY,
                "issue_info": NodeParameterType.OBJECT,
                "projects": NodeParameterType.ARRAY,
                "project_info": NodeParameterType.OBJECT,
                "users": NodeParameterType.ARRAY,
                "user_info": NodeParameterType.OBJECT,
                "comments": NodeParameterType.ARRAY,
                "comment_info": NodeParameterType.OBJECT,
                "components": NodeParameterType.ARRAY,
                "component_info": NodeParameterType.OBJECT,
                "versions": NodeParameterType.ARRAY,
                "version_info": NodeParameterType.OBJECT,
                "worklogs": NodeParameterType.ARRAY,
                "worklog_info": NodeParameterType.OBJECT,
                "filters": NodeParameterType.ARRAY,
                "filter_info": NodeParameterType.OBJECT,
                "dashboards": NodeParameterType.ARRAY,
                "dashboard_info": NodeParameterType.OBJECT,
                "transitions": NodeParameterType.ARRAY,
                "attachments": NodeParameterType.ARRAY,
                "server_info": NodeParameterType.OBJECT,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Jira-specific parameters."""
        params = node_data.get("params", {})
        
        if not params.get("operation"):
            raise NodeValidationError("Operation is required")
        if not params.get("jira_domain"):
            raise NodeValidationError("Jira domain is required")
        
        auth_type = params.get("auth_type", "basic_auth")
        
        # Validate authentication parameters
        if auth_type == "basic_auth":
            if not params.get("username") or not params.get("password"):
                raise NodeValidationError("Username and password are required for basic authentication")
        elif auth_type == "oauth2":
            if not params.get("access_token"):
                raise NodeValidationError("Access token is required for OAuth2 authentication")
        elif auth_type == "personal_access_token":
            if not params.get("personal_access_token"):
                raise NodeValidationError("Personal access token is required")
        
        operation = params["operation"]
        if operation not in self.OPERATIONS:
            raise NodeValidationError(f"Unknown operation: {operation}")
        
        # Check required parameters for operation
        operation_config = self.OPERATIONS[operation]
        for required_param in operation_config.get("required", []):
            if not params.get(required_param):
                raise NodeValidationError(f"Parameter '{required_param}' is required for operation '{operation}'")
        
        return params
    
    def _format_basic_auth(self, username: str, password: str) -> str:
        """Format basic authentication header."""
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    def _build_jql_query(self, filters: Dict[str, Any]) -> str:
        """Build JQL query from filters."""
        conditions = []
        
        if 'project' in filters:
            if isinstance(filters['project'], list):
                projects = "', '".join(filters['project'])
                conditions.append(f"project in ('{projects}')")
            else:
                conditions.append(f"project = '{filters['project']}'")
        
        if 'assignee' in filters:
            conditions.append(f"assignee = '{filters['assignee']}'")
        
        if 'reporter' in filters:
            conditions.append(f"reporter = '{filters['reporter']}'")
        
        if 'status' in filters:
            if isinstance(filters['status'], list):
                statuses = "', '".join(filters['status'])
                conditions.append(f"status in ('{statuses}')")
            else:
                conditions.append(f"status = '{filters['status']}'")
        
        if 'priority' in filters:
            conditions.append(f"priority = '{filters['priority']}'")
        
        if 'issuetype' in filters:
            conditions.append(f"issuetype = '{filters['issuetype']}'")
        
        if 'text' in filters:
            conditions.append(f"text ~ \"{filters['text']}\"")
        
        return " AND ".join(conditions) if conditions else ""
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Jira operation using UniversalRequestNode."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            auth_type = params.get("auth_type", "basic_auth")
            jira_domain = params["jira_domain"]
            
            # Get operation configuration
            operation_config = self.OPERATIONS[operation]
            
            # Prepare dynamic configuration
            config = self.CONFIG.copy()
            if not jira_domain.startswith("http"):
                config["base_url"] = f"https://{jira_domain}/rest/api/3"
            else:
                config["base_url"] = f"{jira_domain}/rest/api/3"
            
            # Set authentication method
            auth_token = None
            if auth_type == "basic_auth":
                config["authentication"] = {
                    "type": "basic_auth",
                    "header": "Authorization"
                }
                auth_token = self._format_basic_auth(params["username"], params["password"])
            elif auth_type == "oauth2":
                config["authentication"] = {
                    "type": "bearer_token",
                    "header": "Authorization"
                }
                auth_token = params["access_token"]
            elif auth_type == "personal_access_token":
                config["authentication"] = {
                    "type": "bearer_token",
                    "header": "Authorization"
                }
                auth_token = params["personal_access_token"]
            
            # Prepare universal request node parameters
            universal_params = {
                "config": config,
                "method": operation_config["method"],
                "endpoint": operation_config["endpoint"],
                "token": auth_token
            }
            
            # Handle path parameters
            endpoint = operation_config["endpoint"]
            for param_name in ["issue_id_or_key", "project_id_or_key", "comment_id", "component_id", "version_id", 
                              "user_account_id", "workflow_id", "issue_type_id", "priority_id", "resolution_id", 
                              "status_id", "field_id", "attachment_id", "link_id", "worklog_id", "filter_id", 
                              "dashboard_id", "role_id"]:
                if f"{{{param_name}}}" in endpoint and params.get(param_name):
                    endpoint = endpoint.replace(f"{{{param_name}}}", params[param_name])
            universal_params["endpoint"] = endpoint
            
            # Handle query parameters and body data
            if operation_config["method"] == "GET":
                query_params = {}
                for param in operation_config.get("params", []):
                    if param in params and params[param] is not None:
                        if param in ["max_results", "start_at"]:
                            query_params[param] = str(params[param])
                        elif param == "include_inactive":
                            query_params["includeInactive"] = str(params[param]).lower()
                        elif param == "user_account_id" and operation in ["get_user", "remove_watcher"]:
                            query_params["accountId"] = params[param]
                        elif param == "group_name":
                            query_params["groupname"] = params[param]
                        elif param not in ["issue_id_or_key", "project_id_or_key", "comment_id", "component_id", 
                                          "version_id", "workflow_id", "issue_type_id", "priority_id", 
                                          "resolution_id", "status_id", "field_id", "attachment_id", 
                                          "link_id", "worklog_id", "filter_id", "dashboard_id", "role_id"]:
                            query_params[param] = params[param]
                if query_params:
                    universal_params["query_params"] = query_params
            else:
                # POST/PUT/DELETE operations - prepare body data
                body_data = {}
                
                if operation == "search_issues":
                    # Special handling for search
                    jql_query = params.get("jql")
                    if not jql_query and params.get("search_filters"):
                        jql_query = self._build_jql_query(params["search_filters"])
                    
                    body_data = {
                        "jql": jql_query or "",
                        "startAt": params.get("start_at", 0),
                        "maxResults": params.get("max_results", 50)
                    }
                    
                    if params.get("expand"):
                        body_data["expand"] = params["expand"]
                    if params.get("fields"):
                        body_data["fields"] = params["fields"].split(",")
                        
                elif operation in ["create_issue", "update_issue"]:
                    # Format issue data
                    issue_data = params.get("issue_data", {})
                    if "fields" in issue_data:
                        body_data = issue_data
                    else:
                        body_data = {"fields": issue_data}
                        
                elif operation == "assign_issue":
                    body_data = {"accountId": params.get("user_account_id")}
                    
                elif operation in ["add_watcher", "remove_watcher"]:
                    if operation == "add_watcher":
                        body_data = params.get("user_account_id")
                    else:
                        # remove_watcher uses query param, handled above
                        pass
                        
                elif operation in ["add_comment", "update_comment"]:
                    body_data = params.get("comment_data", {})
                    
                elif operation in ["create_project", "update_project"]:
                    body_data = params.get("project_data", {})
                    
                elif operation in ["create_component", "update_component"]:
                    body_data = params.get("component_data", {})
                    
                elif operation in ["create_version", "update_version"]:
                    body_data = params.get("version_data", {})
                    
                elif operation in ["create_issue_type", "update_issue_type"]:
                    body_data = params.get("issue_type_data", {})
                    
                elif operation in ["create_custom_field", "update_custom_field"]:
                    body_data = params.get("field_data", {})
                    
                elif operation == "create_issue_link":
                    body_data = params.get("link_data", {})
                    
                elif operation in ["add_worklog", "update_worklog"]:
                    body_data = params.get("worklog_data", {})
                    
                elif operation in ["create_filter", "update_filter"]:
                    body_data = params.get("filter_data", {})
                    
                elif operation == "transition_issue":
                    body_data = params.get("transition_data", {})
                    
                elif operation == "create_group":
                    body_data = {"name": params.get("group_name")}
                
                if body_data:
                    universal_params["body"] = body_data
            
            # Execute the request
            result = await self.universal_node.execute({
                "params": universal_params
            })
            
            if result.get("status") == "success":
                response_data = result.get("response", {})
                
                # Transform response based on operation type
                if operation == "search_issues":
                    return {
                        "status": "success",
                        "issues": response_data.get("issues", []),
                        "total": response_data.get("total", 0),
                        "start_at": response_data.get("startAt", 0),
                        "max_results": response_data.get("maxResults", 0),
                        "response_data": response_data
                    }
                elif operation.startswith("create_issue") or operation.startswith("get_issue") or operation.startswith("update_issue"):
                    return {
                        "status": "success",
                        "issue_info": response_data,
                        "response_data": response_data
                    }
                elif operation == "get_all_projects" or operation.startswith("get_project_"):
                    return {
                        "status": "success",
                        "projects": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_project") or operation.startswith("get_project") or operation.startswith("update_project"):
                    return {
                        "status": "success",
                        "project_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("find_users") or operation == "get_current_user":
                    return {
                        "status": "success",
                        "users": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("get_user"):
                    return {
                        "status": "success",
                        "user_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_issue_comments") or operation == "get_issue_comments":
                    return {
                        "status": "success",
                        "comments": response_data.get("comments", []) if isinstance(response_data, dict) else response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("add_comment") or operation.startswith("update_comment"):
                    return {
                        "status": "success",
                        "comment_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_project_components") or operation == "get_project_components":
                    return {
                        "status": "success",
                        "components": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_component") or operation.startswith("get_component") or operation.startswith("update_component"):
                    return {
                        "status": "success",
                        "component_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_project_versions") or operation == "get_project_versions":
                    return {
                        "status": "success",
                        "versions": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_version") or operation.startswith("get_version") or operation.startswith("update_version"):
                    return {
                        "status": "success",
                        "version_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_issue_worklogs") or operation == "get_issue_worklogs":
                    return {
                        "status": "success",
                        "worklogs": response_data.get("worklogs", []) if isinstance(response_data, dict) else response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("add_worklog") or operation.startswith("update_worklog"):
                    return {
                        "status": "success",
                        "worklog_info": response_data,
                        "response_data": response_data
                    }
                elif operation == "get_favourite_filters" or operation.startswith("get_filter"):
                    return {
                        "status": "success",
                        "filters": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_filter") or operation.startswith("update_filter"):
                    return {
                        "status": "success",
                        "filter_info": response_data,
                        "response_data": response_data
                    }
                elif operation == "get_all_dashboards" or operation.startswith("get_dashboard"):
                    return {
                        "status": "success",
                        "dashboards": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation == "get_issue_transitions":
                    return {
                        "status": "success",
                        "transitions": response_data.get("transitions", []),
                        "response_data": response_data
                    }
                elif operation == "get_issue_attachments" or operation.startswith("get_attachment"):
                    return {
                        "status": "success",
                        "attachments": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation == "get_server_info":
                    return {
                        "status": "success",
                        "server_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("delete_"):
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
            logger.error(f"Jira operation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "JIRA_ERROR"
            }
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'universal_node'):
            await self.universal_node.close()