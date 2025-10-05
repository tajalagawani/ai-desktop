"""
CyberArk Node - Comprehensive integration with CyberArk Privileged Access Security API
Provides access to all CyberArk operations including account management, user management, safe operations, and session management.
"""

import logging
import json
import asyncio
import time
import os
import ssl
import base64
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

class CyberArkOperation:
    """Operations available on CyberArk Privileged Access Security API."""
    
    # Authentication Operations
    LOGON = "logon"
    LOGOFF = "logoff"
    EXTENDED_AUTHENTICATION = "extended_authentication"
    
    # Account Operations
    GET_ACCOUNTS = "get_accounts"
    GET_ACCOUNT_DETAILS = "get_account_details"
    ADD_ACCOUNT = "add_account"
    UPDATE_ACCOUNT = "update_account"
    DELETE_ACCOUNT = "delete_account"
    GET_ACCOUNT_PASSWORD = "get_account_password"
    SET_NEXT_PASSWORD = "set_next_password"
    VERIFY_CREDENTIALS = "verify_credentials"
    CHANGE_CREDENTIALS = "change_credentials"
    RECONCILE_CREDENTIALS = "reconcile_credentials"
    
    # Safe Operations
    GET_SAFES = "get_safes"
    GET_SAFE_DETAILS = "get_safe_details"
    ADD_SAFE = "add_safe"
    UPDATE_SAFE = "update_safe"
    DELETE_SAFE = "delete_safe"
    GET_SAFE_MEMBERS = "get_safe_members"
    ADD_SAFE_MEMBER = "add_safe_member"
    UPDATE_SAFE_MEMBER = "update_safe_member"
    DELETE_SAFE_MEMBER = "delete_safe_member"
    
    # User Operations
    GET_USERS = "get_users"
    GET_USER_DETAILS = "get_user_details"
    ADD_USER = "add_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    ACTIVATE_USER = "activate_user"
    ENABLE_USER = "enable_user"
    DISABLE_USER = "disable_user"
    UNLOCK_USER = "unlock_user"
    
    # Group Operations
    GET_GROUPS = "get_groups"
    ADD_GROUP = "add_group"
    GET_GROUP_MEMBERS = "get_group_members"
    ADD_GROUP_MEMBER = "add_group_member"
    DELETE_GROUP_MEMBER = "delete_group_member"
    
    # Session Management Operations
    GET_LIVE_SESSIONS = "get_live_sessions"
    SUSPEND_SESSION = "suspend_session"
    RESUME_SESSION = "resume_session"
    TERMINATE_SESSION = "terminate_session"
    GET_SESSION_RECORDINGS = "get_session_recordings"
    
    # Platform Operations
    GET_PLATFORMS = "get_platforms"
    GET_PLATFORM_DETAILS = "get_platform_details"
    DUPLICATE_PLATFORM = "duplicate_platform"
    IMPORT_PLATFORM = "import_platform"
    EXPORT_PLATFORM = "export_platform"
    DELETE_PLATFORM = "delete_platform"
    
    # Discovery Operations
    GET_DISCOVERED_ACCOUNTS = "get_discovered_accounts"
    ADD_DISCOVERED_ACCOUNT = "add_discovered_account"
    
    # Policy Operations
    GET_ACCOUNT_GROUPS = "get_account_groups"
    ADD_ACCOUNT_GROUP = "add_account_group"
    GET_SAFE_ACCOUNT_GROUPS = "get_safe_account_groups"
    
    # Monitoring and Reporting Operations
    GET_ACTIVITIES = "get_activities"
    GET_SERVER_DETAILS = "get_server_details"
    
    # Application Operations
    GET_APPLICATIONS = "get_applications"
    ADD_APPLICATION = "add_application"
    DELETE_APPLICATION = "delete_application"
    GET_APPLICATION_AUTHENTICATION_METHODS = "get_application_authentication_methods"
    ADD_APPLICATION_AUTHENTICATION_METHOD = "add_application_authentication_method"
    DELETE_APPLICATION_AUTHENTICATION_METHOD = "delete_application_authentication_method"
    
    # LDAP Operations
    GET_LDAP_DIRECTORIES = "get_ldap_directories"
    ADD_LDAP_DIRECTORY = "add_ldap_directory"
    
    # Bulk Operations
    BULK_UPLOAD_ACCOUNTS = "bulk_upload_accounts"
    BULK_UPLOAD_SAFES = "bulk_upload_safes"
    
    # SSH Key Operations
    GET_SSH_KEYS = "get_ssh_keys"
    ADD_SSH_KEY = "add_ssh_key"
    DELETE_SSH_KEY = "delete_ssh_key"

class CyberArkNode(BaseNode):
    """
    Node for interacting with CyberArk Privileged Access Security API.
    Provides comprehensive functionality for privileged account management, user management, and session control.
    """
    
    BASE_URL = "https://pvwa.company.com/PasswordVault/api"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the CyberArk node."""
        return NodeSchema(
            node_type="cyberark",
            version="1.0.0",
            description="Comprehensive integration with CyberArk Privileged Access Security API for account management, user management, and session control",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with CyberArk API",
                    required=True,
                    enum=[
                        CyberArkOperation.LOGON,
                        CyberArkOperation.LOGOFF,
                        CyberArkOperation.EXTENDED_AUTHENTICATION,
                        CyberArkOperation.GET_ACCOUNTS,
                        CyberArkOperation.GET_ACCOUNT_DETAILS,
                        CyberArkOperation.ADD_ACCOUNT,
                        CyberArkOperation.UPDATE_ACCOUNT,
                        CyberArkOperation.DELETE_ACCOUNT,
                        CyberArkOperation.GET_ACCOUNT_PASSWORD,
                        CyberArkOperation.SET_NEXT_PASSWORD,
                        CyberArkOperation.VERIFY_CREDENTIALS,
                        CyberArkOperation.CHANGE_CREDENTIALS,
                        CyberArkOperation.RECONCILE_CREDENTIALS,
                        CyberArkOperation.GET_SAFES,
                        CyberArkOperation.GET_SAFE_DETAILS,
                        CyberArkOperation.ADD_SAFE,
                        CyberArkOperation.UPDATE_SAFE,
                        CyberArkOperation.DELETE_SAFE,
                        CyberArkOperation.GET_SAFE_MEMBERS,
                        CyberArkOperation.ADD_SAFE_MEMBER,
                        CyberArkOperation.UPDATE_SAFE_MEMBER,
                        CyberArkOperation.DELETE_SAFE_MEMBER,
                        CyberArkOperation.GET_USERS,
                        CyberArkOperation.GET_USER_DETAILS,
                        CyberArkOperation.ADD_USER,
                        CyberArkOperation.UPDATE_USER,
                        CyberArkOperation.DELETE_USER,
                        CyberArkOperation.ACTIVATE_USER,
                        CyberArkOperation.ENABLE_USER,
                        CyberArkOperation.DISABLE_USER,
                        CyberArkOperation.UNLOCK_USER,
                        CyberArkOperation.GET_GROUPS,
                        CyberArkOperation.ADD_GROUP,
                        CyberArkOperation.GET_GROUP_MEMBERS,
                        CyberArkOperation.ADD_GROUP_MEMBER,
                        CyberArkOperation.DELETE_GROUP_MEMBER,
                        CyberArkOperation.GET_LIVE_SESSIONS,
                        CyberArkOperation.SUSPEND_SESSION,
                        CyberArkOperation.RESUME_SESSION,
                        CyberArkOperation.TERMINATE_SESSION,
                        CyberArkOperation.GET_SESSION_RECORDINGS,
                        CyberArkOperation.GET_PLATFORMS,
                        CyberArkOperation.GET_PLATFORM_DETAILS,
                        CyberArkOperation.DUPLICATE_PLATFORM,
                        CyberArkOperation.IMPORT_PLATFORM,
                        CyberArkOperation.EXPORT_PLATFORM,
                        CyberArkOperation.DELETE_PLATFORM,
                        CyberArkOperation.GET_DISCOVERED_ACCOUNTS,
                        CyberArkOperation.ADD_DISCOVERED_ACCOUNT,
                        CyberArkOperation.GET_ACCOUNT_GROUPS,
                        CyberArkOperation.ADD_ACCOUNT_GROUP,
                        CyberArkOperation.GET_SAFE_ACCOUNT_GROUPS,
                        CyberArkOperation.GET_ACTIVITIES,
                        CyberArkOperation.GET_SERVER_DETAILS,
                        CyberArkOperation.GET_APPLICATIONS,
                        CyberArkOperation.ADD_APPLICATION,
                        CyberArkOperation.DELETE_APPLICATION,
                        CyberArkOperation.GET_APPLICATION_AUTHENTICATION_METHODS,
                        CyberArkOperation.ADD_APPLICATION_AUTHENTICATION_METHOD,
                        CyberArkOperation.DELETE_APPLICATION_AUTHENTICATION_METHOD,
                        CyberArkOperation.GET_LDAP_DIRECTORIES,
                        CyberArkOperation.ADD_LDAP_DIRECTORY,
                        CyberArkOperation.BULK_UPLOAD_ACCOUNTS,
                        CyberArkOperation.BULK_UPLOAD_SAFES,
                        CyberArkOperation.GET_SSH_KEYS,
                        CyberArkOperation.ADD_SSH_KEY,
                        CyberArkOperation.DELETE_SSH_KEY
                    ]
                ),
                NodeParameter(
                    name="cyberark_url",
                    type=NodeParameterType.STRING,
                    description="CyberArk PVWA server URL",
                    required=True
                ),
                NodeParameter(
                    name="username",
                    type=NodeParameterType.STRING,
                    description="CyberArk username for authentication",
                    required=False
                ),
                NodeParameter(
                    name="password",
                    type=NodeParameterType.SECRET,
                    description="CyberArk password for authentication",
                    required=False
                ),
                NodeParameter(
                    name="session_token",
                    type=NodeParameterType.SECRET,
                    description="CyberArk session token for authenticated requests",
                    required=False
                ),
                NodeParameter(
                    name="account_id",
                    type=NodeParameterType.STRING,
                    description="Account ID for account-specific operations",
                    required=False
                ),
                NodeParameter(
                    name="safe_name",
                    type=NodeParameterType.STRING,
                    description="Safe name for safe operations",
                    required=False
                ),
                NodeParameter(
                    name="user_id",
                    type=NodeParameterType.STRING,
                    description="User ID for user operations",
                    required=False
                ),
                NodeParameter(
                    name="group_id",
                    type=NodeParameterType.STRING,
                    description="Group ID for group operations",
                    required=False
                ),
                NodeParameter(
                    name="platform_id",
                    type=NodeParameterType.STRING,
                    description="Platform ID for platform operations",
                    required=False
                ),
                NodeParameter(
                    name="session_id",
                    type=NodeParameterType.STRING,
                    description="Session ID for session management",
                    required=False
                ),
                NodeParameter(
                    name="application_id",
                    type=NodeParameterType.STRING,
                    description="Application ID for application operations",
                    required=False
                ),
                NodeParameter(
                    name="account_data",
                    type=NodeParameterType.OBJECT,
                    description="Account data for account creation/update",
                    required=False
                ),
                NodeParameter(
                    name="safe_data",
                    type=NodeParameterType.OBJECT,
                    description="Safe data for safe creation/update",
                    required=False
                ),
                NodeParameter(
                    name="user_data",
                    type=NodeParameterType.OBJECT,
                    description="User data for user creation/update",
                    required=False
                ),
                NodeParameter(
                    name="group_data",
                    type=NodeParameterType.OBJECT,
                    description="Group data for group creation/update",
                    required=False
                ),
                NodeParameter(
                    name="member_data",
                    type=NodeParameterType.OBJECT,
                    description="Member data for safe member operations",
                    required=False
                ),
                NodeParameter(
                    name="search_criteria",
                    type=NodeParameterType.STRING,
                    description="Search criteria for filtering results",
                    required=False
                ),
                NodeParameter(
                    name="search_in",
                    type=NodeParameterType.STRING,
                    description="Search scope (account name, address, etc.)",
                    required=False
                ),
                NodeParameter(
                    name="sort_by",
                    type=NodeParameterType.STRING,
                    description="Field to sort results by",
                    required=False
                ),
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of results to return",
                    required=False,
                    default=50
                ),
                NodeParameter(
                    name="offset",
                    type=NodeParameterType.NUMBER,
                    description="Number of results to skip",
                    required=False,
                    default=0
                ),
                NodeParameter(
                    name="filter",
                    type=NodeParameterType.STRING,
                    description="Filter expression for advanced filtering",
                    required=False
                ),
                NodeParameter(
                    name="new_password",
                    type=NodeParameterType.SECRET,
                    description="New password for password change operations",
                    required=False
                ),
                NodeParameter(
                    name="immediate_change",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to perform immediate password change",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="reason",
                    type=NodeParameterType.STRING,
                    description="Reason for the operation (for audit purposes)",
                    required=False
                ),
                NodeParameter(
                    name="ticket_id",
                    type=NodeParameterType.STRING,
                    description="Ticket ID for request tracking",
                    required=False
                ),
                NodeParameter(
                    name="machine_address",
                    type=NodeParameterType.STRING,
                    description="Machine address for connection",
                    required=False
                ),
                NodeParameter(
                    name="connection_component",
                    type=NodeParameterType.STRING,
                    description="Connection component ID",
                    required=False
                ),
                NodeParameter(
                    name="extra_fields",
                    type=NodeParameterType.OBJECT,
                    description="Additional fields for extended operations",
                    required=False
                ),
                NodeParameter(
                    name="from_date",
                    type=NodeParameterType.STRING,
                    description="Start date for activity/audit queries (YYYY-MM-DD)",
                    required=False
                ),
                NodeParameter(
                    name="to_date",
                    type=NodeParameterType.STRING,
                    description="End date for activity/audit queries (YYYY-MM-DD)",
                    required=False
                ),
                NodeParameter(
                    name="safe_member_name",
                    type=NodeParameterType.STRING,
                    description="Safe member username for member operations",
                    required=False
                ),
                NodeParameter(
                    name="permissions",
                    type=NodeParameterType.OBJECT,
                    description="Permission settings for safe members",
                    required=False
                ),
                NodeParameter(
                    name="platform_file",
                    type=NodeParameterType.STRING,
                    description="Platform file path for import/export operations",
                    required=False
                ),
                NodeParameter(
                    name="ssh_key_data",
                    type=NodeParameterType.OBJECT,
                    description="SSH key data for SSH key operations",
                    required=False
                ),
                NodeParameter(
                    name="bulk_data",
                    type=NodeParameterType.ARRAY,
                    description="Bulk data for batch operations",
                    required=False
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "session_token": NodeParameterType.STRING,
                "accounts": NodeParameterType.ARRAY,
                "account": NodeParameterType.OBJECT,
                "account_password": NodeParameterType.STRING,
                "safes": NodeParameterType.ARRAY,
                "safe": NodeParameterType.OBJECT,
                "safe_members": NodeParameterType.ARRAY,
                "users": NodeParameterType.ARRAY,
                "user": NodeParameterType.OBJECT,
                "groups": NodeParameterType.ARRAY,
                "group": NodeParameterType.OBJECT,
                "group_members": NodeParameterType.ARRAY,
                "sessions": NodeParameterType.ARRAY,
                "session": NodeParameterType.OBJECT,
                "recordings": NodeParameterType.ARRAY,
                "platforms": NodeParameterType.ARRAY,
                "platform": NodeParameterType.OBJECT,
                "discovered_accounts": NodeParameterType.ARRAY,
                "account_groups": NodeParameterType.ARRAY,
                "activities": NodeParameterType.ARRAY,
                "server_details": NodeParameterType.OBJECT,
                "applications": NodeParameterType.ARRAY,
                "application": NodeParameterType.OBJECT,
                "authentication_methods": NodeParameterType.ARRAY,
                "ldap_directories": NodeParameterType.ARRAY,
                "ssh_keys": NodeParameterType.ARRAY,
                "bulk_results": NodeParameterType.OBJECT,
                "count": NodeParameterType.NUMBER,
                "next_password": NodeParameterType.STRING,
                "password_changed": NodeParameterType.BOOLEAN,
                "verification_result": NodeParameterType.BOOLEAN,
                "reconciliation_result": NodeParameterType.BOOLEAN,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["cyberark", "privileged-access", "security", "pam", "vault", "credentials"],
            author="System",
            documentation_url="https://docs.cyberark.com"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for CyberArk URL
        if not params.get("cyberark_url"):
            raise NodeValidationError("CyberArk URL is required")
            
        # Authentication validation
        if operation == CyberArkOperation.LOGON:
            if not params.get("username") or not params.get("password"):
                raise NodeValidationError("Username and password are required for logon")
        elif operation != CyberArkOperation.LOGON:
            if not params.get("session_token"):
                raise NodeValidationError("Session token is required for authenticated operations")
                
        # Account operations validation
        if operation in [CyberArkOperation.GET_ACCOUNT_DETAILS, CyberArkOperation.UPDATE_ACCOUNT,
                        CyberArkOperation.DELETE_ACCOUNT, CyberArkOperation.GET_ACCOUNT_PASSWORD,
                        CyberArkOperation.SET_NEXT_PASSWORD, CyberArkOperation.VERIFY_CREDENTIALS,
                        CyberArkOperation.CHANGE_CREDENTIALS, CyberArkOperation.RECONCILE_CREDENTIALS]:
            if not params.get("account_id"):
                raise NodeValidationError("Account ID is required for account-specific operations")
                
        elif operation in [CyberArkOperation.ADD_ACCOUNT, CyberArkOperation.UPDATE_ACCOUNT]:
            if not params.get("account_data"):
                raise NodeValidationError("Account data is required for account creation/update")
                
        # Safe operations validation
        elif operation in [CyberArkOperation.GET_SAFE_DETAILS, CyberArkOperation.UPDATE_SAFE,
                          CyberArkOperation.DELETE_SAFE, CyberArkOperation.GET_SAFE_MEMBERS,
                          CyberArkOperation.ADD_SAFE_MEMBER, CyberArkOperation.UPDATE_SAFE_MEMBER,
                          CyberArkOperation.DELETE_SAFE_MEMBER, CyberArkOperation.GET_SAFE_ACCOUNT_GROUPS]:
            if not params.get("safe_name"):
                raise NodeValidationError("Safe name is required for safe operations")
                
        elif operation in [CyberArkOperation.ADD_SAFE, CyberArkOperation.UPDATE_SAFE]:
            if not params.get("safe_data"):
                raise NodeValidationError("Safe data is required for safe creation/update")
                
        elif operation in [CyberArkOperation.ADD_SAFE_MEMBER, CyberArkOperation.UPDATE_SAFE_MEMBER,
                          CyberArkOperation.DELETE_SAFE_MEMBER]:
            if not params.get("safe_member_name"):
                raise NodeValidationError("Safe member name is required for member operations")
                
        # User operations validation
        elif operation in [CyberArkOperation.GET_USER_DETAILS, CyberArkOperation.UPDATE_USER,
                          CyberArkOperation.DELETE_USER, CyberArkOperation.ACTIVATE_USER,
                          CyberArkOperation.ENABLE_USER, CyberArkOperation.DISABLE_USER,
                          CyberArkOperation.UNLOCK_USER]:
            if not params.get("user_id"):
                raise NodeValidationError("User ID is required for user-specific operations")
                
        elif operation in [CyberArkOperation.ADD_USER, CyberArkOperation.UPDATE_USER]:
            if not params.get("user_data"):
                raise NodeValidationError("User data is required for user creation/update")
                
        # Session operations validation
        elif operation in [CyberArkOperation.SUSPEND_SESSION, CyberArkOperation.RESUME_SESSION,
                          CyberArkOperation.TERMINATE_SESSION]:
            if not params.get("session_id"):
                raise NodeValidationError("Session ID is required for session management")
                
        # Platform operations validation
        elif operation in [CyberArkOperation.GET_PLATFORM_DETAILS, CyberArkOperation.DUPLICATE_PLATFORM,
                          CyberArkOperation.EXPORT_PLATFORM, CyberArkOperation.DELETE_PLATFORM]:
            if not params.get("platform_id"):
                raise NodeValidationError("Platform ID is required for platform operations")
                
        # Password change validation
        elif operation in [CyberArkOperation.SET_NEXT_PASSWORD, CyberArkOperation.CHANGE_CREDENTIALS]:
            if not params.get("new_password"):
                raise NodeValidationError("New password is required for password change operations")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the CyberArk node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Execute the appropriate operation
            if operation == CyberArkOperation.LOGON:
                return await self._operation_logon(validated_data)
            elif operation == CyberArkOperation.LOGOFF:
                return await self._operation_logoff(validated_data)
            elif operation == CyberArkOperation.EXTENDED_AUTHENTICATION:
                return await self._operation_extended_authentication(validated_data)
            elif operation == CyberArkOperation.GET_ACCOUNTS:
                return await self._operation_get_accounts(validated_data)
            elif operation == CyberArkOperation.GET_ACCOUNT_DETAILS:
                return await self._operation_get_account_details(validated_data)
            elif operation == CyberArkOperation.ADD_ACCOUNT:
                return await self._operation_add_account(validated_data)
            elif operation == CyberArkOperation.UPDATE_ACCOUNT:
                return await self._operation_update_account(validated_data)
            elif operation == CyberArkOperation.DELETE_ACCOUNT:
                return await self._operation_delete_account(validated_data)
            elif operation == CyberArkOperation.GET_ACCOUNT_PASSWORD:
                return await self._operation_get_account_password(validated_data)
            elif operation == CyberArkOperation.SET_NEXT_PASSWORD:
                return await self._operation_set_next_password(validated_data)
            elif operation == CyberArkOperation.VERIFY_CREDENTIALS:
                return await self._operation_verify_credentials(validated_data)
            elif operation == CyberArkOperation.CHANGE_CREDENTIALS:
                return await self._operation_change_credentials(validated_data)
            elif operation == CyberArkOperation.RECONCILE_CREDENTIALS:
                return await self._operation_reconcile_credentials(validated_data)
            elif operation == CyberArkOperation.GET_SAFES:
                return await self._operation_get_safes(validated_data)
            elif operation == CyberArkOperation.GET_SAFE_DETAILS:
                return await self._operation_get_safe_details(validated_data)
            elif operation == CyberArkOperation.ADD_SAFE:
                return await self._operation_add_safe(validated_data)
            elif operation == CyberArkOperation.UPDATE_SAFE:
                return await self._operation_update_safe(validated_data)
            elif operation == CyberArkOperation.DELETE_SAFE:
                return await self._operation_delete_safe(validated_data)
            elif operation == CyberArkOperation.GET_SAFE_MEMBERS:
                return await self._operation_get_safe_members(validated_data)
            elif operation == CyberArkOperation.ADD_SAFE_MEMBER:
                return await self._operation_add_safe_member(validated_data)
            elif operation == CyberArkOperation.UPDATE_SAFE_MEMBER:
                return await self._operation_update_safe_member(validated_data)
            elif operation == CyberArkOperation.DELETE_SAFE_MEMBER:
                return await self._operation_delete_safe_member(validated_data)
            elif operation == CyberArkOperation.GET_USERS:
                return await self._operation_get_users(validated_data)
            elif operation == CyberArkOperation.GET_USER_DETAILS:
                return await self._operation_get_user_details(validated_data)
            elif operation == CyberArkOperation.ADD_USER:
                return await self._operation_add_user(validated_data)
            elif operation == CyberArkOperation.UPDATE_USER:
                return await self._operation_update_user(validated_data)
            elif operation == CyberArkOperation.DELETE_USER:
                return await self._operation_delete_user(validated_data)
            elif operation == CyberArkOperation.ACTIVATE_USER:
                return await self._operation_activate_user(validated_data)
            elif operation == CyberArkOperation.ENABLE_USER:
                return await self._operation_enable_user(validated_data)
            elif operation == CyberArkOperation.DISABLE_USER:
                return await self._operation_disable_user(validated_data)
            elif operation == CyberArkOperation.UNLOCK_USER:
                return await self._operation_unlock_user(validated_data)
            elif operation == CyberArkOperation.GET_GROUPS:
                return await self._operation_get_groups(validated_data)
            elif operation == CyberArkOperation.ADD_GROUP:
                return await self._operation_add_group(validated_data)
            elif operation == CyberArkOperation.GET_GROUP_MEMBERS:
                return await self._operation_get_group_members(validated_data)
            elif operation == CyberArkOperation.ADD_GROUP_MEMBER:
                return await self._operation_add_group_member(validated_data)
            elif operation == CyberArkOperation.DELETE_GROUP_MEMBER:
                return await self._operation_delete_group_member(validated_data)
            elif operation == CyberArkOperation.GET_LIVE_SESSIONS:
                return await self._operation_get_live_sessions(validated_data)
            elif operation == CyberArkOperation.SUSPEND_SESSION:
                return await self._operation_suspend_session(validated_data)
            elif operation == CyberArkOperation.RESUME_SESSION:
                return await self._operation_resume_session(validated_data)
            elif operation == CyberArkOperation.TERMINATE_SESSION:
                return await self._operation_terminate_session(validated_data)
            elif operation == CyberArkOperation.GET_SESSION_RECORDINGS:
                return await self._operation_get_session_recordings(validated_data)
            elif operation == CyberArkOperation.GET_PLATFORMS:
                return await self._operation_get_platforms(validated_data)
            elif operation == CyberArkOperation.GET_PLATFORM_DETAILS:
                return await self._operation_get_platform_details(validated_data)
            elif operation == CyberArkOperation.DUPLICATE_PLATFORM:
                return await self._operation_duplicate_platform(validated_data)
            elif operation == CyberArkOperation.IMPORT_PLATFORM:
                return await self._operation_import_platform(validated_data)
            elif operation == CyberArkOperation.EXPORT_PLATFORM:
                return await self._operation_export_platform(validated_data)
            elif operation == CyberArkOperation.DELETE_PLATFORM:
                return await self._operation_delete_platform(validated_data)
            elif operation == CyberArkOperation.GET_DISCOVERED_ACCOUNTS:
                return await self._operation_get_discovered_accounts(validated_data)
            elif operation == CyberArkOperation.ADD_DISCOVERED_ACCOUNT:
                return await self._operation_add_discovered_account(validated_data)
            elif operation == CyberArkOperation.GET_ACCOUNT_GROUPS:
                return await self._operation_get_account_groups(validated_data)
            elif operation == CyberArkOperation.ADD_ACCOUNT_GROUP:
                return await self._operation_add_account_group(validated_data)
            elif operation == CyberArkOperation.GET_SAFE_ACCOUNT_GROUPS:
                return await self._operation_get_safe_account_groups(validated_data)
            elif operation == CyberArkOperation.GET_ACTIVITIES:
                return await self._operation_get_activities(validated_data)
            elif operation == CyberArkOperation.GET_SERVER_DETAILS:
                return await self._operation_get_server_details(validated_data)
            elif operation == CyberArkOperation.GET_APPLICATIONS:
                return await self._operation_get_applications(validated_data)
            elif operation == CyberArkOperation.ADD_APPLICATION:
                return await self._operation_add_application(validated_data)
            elif operation == CyberArkOperation.DELETE_APPLICATION:
                return await self._operation_delete_application(validated_data)
            elif operation == CyberArkOperation.GET_APPLICATION_AUTHENTICATION_METHODS:
                return await self._operation_get_application_authentication_methods(validated_data)
            elif operation == CyberArkOperation.ADD_APPLICATION_AUTHENTICATION_METHOD:
                return await self._operation_add_application_authentication_method(validated_data)
            elif operation == CyberArkOperation.DELETE_APPLICATION_AUTHENTICATION_METHOD:
                return await self._operation_delete_application_authentication_method(validated_data)
            elif operation == CyberArkOperation.GET_LDAP_DIRECTORIES:
                return await self._operation_get_ldap_directories(validated_data)
            elif operation == CyberArkOperation.ADD_LDAP_DIRECTORY:
                return await self._operation_add_ldap_directory(validated_data)
            elif operation == CyberArkOperation.BULK_UPLOAD_ACCOUNTS:
                return await self._operation_bulk_upload_accounts(validated_data)
            elif operation == CyberArkOperation.BULK_UPLOAD_SAFES:
                return await self._operation_bulk_upload_safes(validated_data)
            elif operation == CyberArkOperation.GET_SSH_KEYS:
                return await self._operation_get_ssh_keys(validated_data)
            elif operation == CyberArkOperation.ADD_SSH_KEY:
                return await self._operation_add_ssh_key(validated_data)
            elif operation == CyberArkOperation.DELETE_SSH_KEY:
                return await self._operation_delete_ssh_key(validated_data)
            else:
                error_message = f"Unknown operation: {operation}"
                logger.error(error_message)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_message,
                    "status_code": None,
                    "response_headers": None
                }
                
        except Exception as e:
            error_message = f"Error in CyberArk node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "status_code": None,
                "response_headers": None
            }
        finally:
            # Clean up session
            await self._cleanup_session()
    
    async def _init_session(self):
        """Initialize HTTP session."""
        if not self.session:
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(connector=connector)
    
    async def _cleanup_session(self):
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any], 
                          data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the CyberArk API."""
        cyberark_url = params.get("cyberark_url", self.BASE_URL)
        url = f"{cyberark_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add session token header if provided
        if params.get("session_token"):
            headers["Authorization"] = params.get("session_token")
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                response_headers = dict(response.headers)
                
                # Handle different response content types
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"CyberArk API error {response.status}: {response_data}"
                    logger.error(error_message)
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                return {
                    "status": "success",
                    "result": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
        except aiohttp.ClientError as e:
            error_message = f"HTTP error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "error": error_message,
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    # -------------------------
    # Authentication Operations
    # -------------------------
    
    async def _operation_logon(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate with CyberArk and get session token."""
        username = params.get("username", "")
        password = params.get("password", "")
        
        request_data = {
            "username": username,
            "password": password
        }
        
        result = await self._make_request("POST", "auth/CyberArk/Logon", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            # CyberArk returns the token directly as a string
            token = result["result"]
            if isinstance(token, str):
                result["session_token"] = token
            else:
                result["session_token"] = str(token)
        
        return result
    
    async def _operation_logoff(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Logoff from CyberArk."""
        return await self._make_request("POST", "auth/Logoff", params)
    
    async def _operation_extended_authentication(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform extended authentication."""
        extra_fields = params.get("extra_fields", {})
        return await self._make_request("POST", "auth/CyberArk/ExtendedAuth", params, extra_fields)
    
    # -------------------------
    # Account Operations
    # -------------------------
    
    async def _operation_get_accounts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get accounts list."""
        query_params = []
        
        # Build query parameters
        if params.get("search_criteria"):
            query_params.append(f"search={params.get('search_criteria')}")
        if params.get("search_in"):
            query_params.append(f"searchType={params.get('search_in')}")
        if params.get("sort_by"):
            query_params.append(f"sort={params.get('sort_by')}")
        if params.get("offset"):
            query_params.append(f"offset={params.get('offset')}")
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        if params.get("filter"):
            query_params.append(f"filter={params.get('filter')}")
        if params.get("safe_name"):
            query_params.append(f"safeName={params.get('safe_name')}")
        
        endpoint = "accounts"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["accounts"] = result["result"].get("value", [])
                result["count"] = result["result"].get("count", 0)
            else:
                result["accounts"] = result["result"]
                result["count"] = len(result["result"]) if isinstance(result["result"], list) else 0
        
        return result
    
    async def _operation_get_account_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific account details."""
        account_id = params.get("account_id", "")
        
        result = await self._make_request("GET", f"accounts/{account_id}", params)
        
        if result["status"] == "success" and result["result"]:
            result["account"] = result["result"]
        
        return result
    
    async def _operation_add_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new account."""
        account_data = params.get("account_data", {})
        
        result = await self._make_request("POST", "accounts", params, account_data)
        
        if result["status"] == "success" and result["result"]:
            result["account"] = result["result"]
        
        return result
    
    async def _operation_update_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing account."""
        account_id = params.get("account_id", "")
        account_data = params.get("account_data", {})
        
        result = await self._make_request("PATCH", f"accounts/{account_id}", params, account_data)
        
        if result["status"] == "success" and result["result"]:
            result["account"] = result["result"]
        
        return result
    
    async def _operation_delete_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an account."""
        account_id = params.get("account_id", "")
        
        return await self._make_request("DELETE", f"accounts/{account_id}", params)
    
    async def _operation_get_account_password(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get account password."""
        account_id = params.get("account_id", "")
        reason = params.get("reason", "")
        ticket_id = params.get("ticket_id", "")
        machine_address = params.get("machine_address", "")
        
        query_params = []
        if reason:
            query_params.append(f"reason={reason}")
        if ticket_id:
            query_params.append(f"ticketingSystemName=ServiceNow&ticketId={ticket_id}")
        if machine_address:
            query_params.append(f"machineAddress={machine_address}")
        
        endpoint = f"accounts/{account_id}/password/retrieve"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            # Handle both string and object responses
            if isinstance(result["result"], str):
                result["account_password"] = result["result"]
            else:
                result["account_password"] = result["result"].get("password", "")
        
        return result
    
    async def _operation_set_next_password(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set next password for an account."""
        account_id = params.get("account_id", "")
        new_password = params.get("new_password", "")
        immediate_change = params.get("immediate_change", False)
        
        request_data = {
            "NewCredentials": new_password,
            "ChangeEntireGroup": False,
            "ChangeImmediately": immediate_change
        }
        
        result = await self._make_request("POST", f"accounts/{account_id}/password/update", params, request_data)
        
        if result["status"] == "success":
            result["next_password"] = new_password
        
        return result
    
    async def _operation_verify_credentials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify account credentials."""
        account_id = params.get("account_id", "")
        
        result = await self._make_request("POST", f"accounts/{account_id}/verify", params)
        
        if result["status"] == "success":
            result["verification_result"] = True
        else:
            result["verification_result"] = False
        
        return result
    
    async def _operation_change_credentials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Change account credentials."""
        account_id = params.get("account_id", "")
        new_password = params.get("new_password", "")
        immediate_change = params.get("immediate_change", True)
        
        request_data = {}
        if new_password:
            request_data["NewCredentials"] = new_password
        if immediate_change is not None:
            request_data["ChangeImmediately"] = immediate_change
        
        result = await self._make_request("POST", f"accounts/{account_id}/change", params, request_data)
        
        if result["status"] == "success":
            result["password_changed"] = True
        else:
            result["password_changed"] = False
        
        return result
    
    async def _operation_reconcile_credentials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcile account credentials."""
        account_id = params.get("account_id", "")
        
        result = await self._make_request("POST", f"accounts/{account_id}/reconcile", params)
        
        if result["status"] == "success":
            result["reconciliation_result"] = True
        else:
            result["reconciliation_result"] = False
        
        return result
    
    # -------------------------
    # Safe Operations
    # -------------------------
    
    async def _operation_get_safes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get safes list."""
        query_params = []
        
        if params.get("search_criteria"):
            query_params.append(f"search={params.get('search_criteria')}")
        if params.get("offset"):
            query_params.append(f"offset={params.get('offset')}")
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        
        endpoint = "safes"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["safes"] = result["result"].get("value", [])
                result["count"] = result["result"].get("count", 0)
            else:
                result["safes"] = result["result"]
                result["count"] = len(result["result"]) if isinstance(result["result"], list) else 0
        
        return result
    
    async def _operation_get_safe_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific safe details."""
        safe_name = params.get("safe_name", "")
        
        result = await self._make_request("GET", f"safes/{safe_name}", params)
        
        if result["status"] == "success" and result["result"]:
            result["safe"] = result["result"]
        
        return result
    
    async def _operation_add_safe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new safe."""
        safe_data = params.get("safe_data", {})
        
        result = await self._make_request("POST", "safes", params, safe_data)
        
        if result["status"] == "success" and result["result"]:
            result["safe"] = result["result"]
        
        return result
    
    async def _operation_update_safe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing safe."""
        safe_name = params.get("safe_name", "")
        safe_data = params.get("safe_data", {})
        
        result = await self._make_request("PUT", f"safes/{safe_name}", params, safe_data)
        
        if result["status"] == "success" and result["result"]:
            result["safe"] = result["result"]
        
        return result
    
    async def _operation_delete_safe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a safe."""
        safe_name = params.get("safe_name", "")
        
        return await self._make_request("DELETE", f"safes/{safe_name}", params)
    
    async def _operation_get_safe_members(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get safe members."""
        safe_name = params.get("safe_name", "")
        
        result = await self._make_request("GET", f"safes/{safe_name}/members", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["safe_members"] = result["result"].get("value", [])
            else:
                result["safe_members"] = result["result"]
        
        return result
    
    async def _operation_add_safe_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a safe member."""
        safe_name = params.get("safe_name", "")
        member_data = params.get("member_data", {})
        
        result = await self._make_request("POST", f"safes/{safe_name}/members", params, member_data)
        
        if result["status"] == "success" and result["result"]:
            result["safe_member"] = result["result"]
        
        return result
    
    async def _operation_update_safe_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a safe member."""
        safe_name = params.get("safe_name", "")
        safe_member_name = params.get("safe_member_name", "")
        member_data = params.get("member_data", {})
        
        result = await self._make_request("PUT", f"safes/{safe_name}/members/{safe_member_name}", params, member_data)
        
        if result["status"] == "success" and result["result"]:
            result["safe_member"] = result["result"]
        
        return result
    
    async def _operation_delete_safe_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a safe member."""
        safe_name = params.get("safe_name", "")
        safe_member_name = params.get("safe_member_name", "")
        
        return await self._make_request("DELETE", f"safes/{safe_name}/members/{safe_member_name}", params)
    
    # -------------------------
    # User Operations
    # -------------------------
    
    async def _operation_get_users(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get users list."""
        query_params = []
        
        if params.get("search_criteria"):
            query_params.append(f"search={params.get('search_criteria')}")
        if params.get("offset"):
            query_params.append(f"offset={params.get('offset')}")
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        
        endpoint = "users"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["users"] = result["result"].get("value", [])
                result["count"] = result["result"].get("Total", 0)
            else:
                result["users"] = result["result"]
                result["count"] = len(result["result"]) if isinstance(result["result"], list) else 0
        
        return result
    
    async def _operation_get_user_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific user details."""
        user_id = params.get("user_id", "")
        
        result = await self._make_request("GET", f"users/{user_id}", params)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
        
        return result
    
    async def _operation_add_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new user."""
        user_data = params.get("user_data", {})
        
        result = await self._make_request("POST", "users", params, user_data)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
        
        return result
    
    async def _operation_update_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing user."""
        user_id = params.get("user_id", "")
        user_data = params.get("user_data", {})
        
        result = await self._make_request("PUT", f"users/{user_id}", params, user_data)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
        
        return result
    
    async def _operation_delete_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a user."""
        user_id = params.get("user_id", "")
        
        return await self._make_request("DELETE", f"users/{user_id}", params)
    
    async def _operation_activate_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Activate a user."""
        user_id = params.get("user_id", "")
        
        return await self._make_request("POST", f"users/{user_id}/activate", params)
    
    async def _operation_enable_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enable a user."""
        user_id = params.get("user_id", "")
        
        return await self._make_request("POST", f"users/{user_id}/enable", params)
    
    async def _operation_disable_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Disable a user."""
        user_id = params.get("user_id", "")
        
        return await self._make_request("POST", f"users/{user_id}/disable", params)
    
    async def _operation_unlock_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unlock a user."""
        user_id = params.get("user_id", "")
        
        return await self._make_request("POST", f"users/{user_id}/unlock", params)
    
    # -------------------------
    # Group Operations
    # -------------------------
    
    async def _operation_get_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get groups list."""
        query_params = []
        
        if params.get("search_criteria"):
            query_params.append(f"search={params.get('search_criteria')}")
        
        endpoint = "groups"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["groups"] = result["result"].get("value", [])
            else:
                result["groups"] = result["result"]
        
        return result
    
    async def _operation_add_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new group."""
        group_data = params.get("group_data", {})
        
        result = await self._make_request("POST", "groups", params, group_data)
        
        if result["status"] == "success" and result["result"]:
            result["group"] = result["result"]
        
        return result
    
    async def _operation_get_group_members(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get group members."""
        group_id = params.get("group_id", "")
        
        result = await self._make_request("GET", f"groups/{group_id}/members", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["group_members"] = result["result"].get("value", [])
            else:
                result["group_members"] = result["result"]
        
        return result
    
    async def _operation_add_group_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a group member."""
        group_id = params.get("group_id", "")
        member_data = params.get("member_data", {})
        
        return await self._make_request("POST", f"groups/{group_id}/members", params, member_data)
    
    async def _operation_delete_group_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a group member."""
        group_id = params.get("group_id", "")
        user_id = params.get("user_id", "")
        
        return await self._make_request("DELETE", f"groups/{group_id}/members/{user_id}", params)
    
    # -------------------------
    # Session Management Operations
    # -------------------------
    
    async def _operation_get_live_sessions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get live sessions."""
        result = await self._make_request("GET", "livesessions", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["sessions"] = result["result"].get("LiveSessions", [])
            else:
                result["sessions"] = result["result"]
        
        return result
    
    async def _operation_suspend_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Suspend a session."""
        session_id = params.get("session_id", "")
        
        return await self._make_request("POST", f"livesessions/{session_id}/suspend", params)
    
    async def _operation_resume_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resume a session."""
        session_id = params.get("session_id", "")
        
        return await self._make_request("POST", f"livesessions/{session_id}/resume", params)
    
    async def _operation_terminate_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Terminate a session."""
        session_id = params.get("session_id", "")
        
        return await self._make_request("POST", f"livesessions/{session_id}/terminate", params)
    
    async def _operation_get_session_recordings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get session recordings."""
        query_params = []
        
        if params.get("from_date"):
            query_params.append(f"fromTime={params.get('from_date')}")
        if params.get("to_date"):
            query_params.append(f"toTime={params.get('to_date')}")
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        if params.get("offset"):
            query_params.append(f"offset={params.get('offset')}")
        
        endpoint = "recordings"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["recordings"] = result["result"].get("Recordings", [])
            else:
                result["recordings"] = result["result"]
        
        return result
    
    # -------------------------
    # Platform Operations
    # -------------------------
    
    async def _operation_get_platforms(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get platforms list."""
        result = await self._make_request("GET", "platforms", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["platforms"] = result["result"].get("Platforms", [])
            else:
                result["platforms"] = result["result"]
        
        return result
    
    async def _operation_get_platform_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific platform details."""
        platform_id = params.get("platform_id", "")
        
        result = await self._make_request("GET", f"platforms/{platform_id}", params)
        
        if result["status"] == "success" and result["result"]:
            result["platform"] = result["result"]
        
        return result
    
    async def _operation_duplicate_platform(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Duplicate a platform."""
        platform_id = params.get("platform_id", "")
        platform_data = params.get("platform_data", {})
        
        return await self._make_request("POST", f"platforms/{platform_id}/duplicate", params, platform_data)
    
    async def _operation_import_platform(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Import a platform."""
        platform_file = params.get("platform_file", "")
        
        # Note: This would typically require multipart/form-data
        return await self._make_request("POST", "platforms/import", params, {"file": platform_file})
    
    async def _operation_export_platform(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export a platform."""
        platform_id = params.get("platform_id", "")
        
        return await self._make_request("POST", f"platforms/{platform_id}/export", params)
    
    async def _operation_delete_platform(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a platform."""
        platform_id = params.get("platform_id", "")
        
        return await self._make_request("DELETE", f"platforms/{platform_id}", params)
    
    # -------------------------
    # Discovery Operations
    # -------------------------
    
    async def _operation_get_discovered_accounts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get discovered accounts."""
        query_params = []
        
        if params.get("search_criteria"):
            query_params.append(f"search={params.get('search_criteria')}")
        if params.get("offset"):
            query_params.append(f"offset={params.get('offset')}")
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        
        endpoint = "discoveredaccounts"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["discovered_accounts"] = result["result"].get("value", [])
            else:
                result["discovered_accounts"] = result["result"]
        
        return result
    
    async def _operation_add_discovered_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a discovered account."""
        account_data = params.get("account_data", {})
        
        return await self._make_request("POST", "discoveredaccounts", params, account_data)
    
    # -------------------------
    # Policy Operations
    # -------------------------
    
    async def _operation_get_account_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get account groups."""
        result = await self._make_request("GET", "accountgroups", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["account_groups"] = result["result"].get("value", [])
            else:
                result["account_groups"] = result["result"]
        
        return result
    
    async def _operation_add_account_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add an account group."""
        group_data = params.get("group_data", {})
        
        return await self._make_request("POST", "accountgroups", params, group_data)
    
    async def _operation_get_safe_account_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get safe account groups."""
        safe_name = params.get("safe_name", "")
        
        result = await self._make_request("GET", f"safes/{safe_name}/accountgroups", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["account_groups"] = result["result"].get("value", [])
            else:
                result["account_groups"] = result["result"]
        
        return result
    
    # -------------------------
    # Monitoring and Reporting Operations
    # -------------------------
    
    async def _operation_get_activities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get activities/audit logs."""
        query_params = []
        
        if params.get("from_date"):
            query_params.append(f"fromTime={params.get('from_date')}")
        if params.get("to_date"):
            query_params.append(f"toTime={params.get('to_date')}")
        if params.get("search_criteria"):
            query_params.append(f"search={params.get('search_criteria')}")
        if params.get("offset"):
            query_params.append(f"offset={params.get('offset')}")
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        
        endpoint = "activities"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["activities"] = result["result"].get("Activities", [])
                result["count"] = result["result"].get("Count", 0)
            else:
                result["activities"] = result["result"]
        
        return result
    
    async def _operation_get_server_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get server details."""
        result = await self._make_request("GET", "server", params)
        
        if result["status"] == "success" and result["result"]:
            result["server_details"] = result["result"]
        
        return result
    
    # -------------------------
    # Application Operations
    # -------------------------
    
    async def _operation_get_applications(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get applications list."""
        result = await self._make_request("GET", "applications", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["applications"] = result["result"].get("application", [])
            else:
                result["applications"] = result["result"]
        
        return result
    
    async def _operation_add_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new application."""
        application_data = params.get("application_data", {})
        
        return await self._make_request("POST", "applications", params, application_data)
    
    async def _operation_delete_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an application."""
        application_id = params.get("application_id", "")
        
        return await self._make_request("DELETE", f"applications/{application_id}", params)
    
    async def _operation_get_application_authentication_methods(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get application authentication methods."""
        application_id = params.get("application_id", "")
        
        result = await self._make_request("GET", f"applications/{application_id}/authentications", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["authentication_methods"] = result["result"].get("authentication", [])
            else:
                result["authentication_methods"] = result["result"]
        
        return result
    
    async def _operation_add_application_authentication_method(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add application authentication method."""
        application_id = params.get("application_id", "")
        auth_data = params.get("auth_data", {})
        
        return await self._make_request("POST", f"applications/{application_id}/authentications", params, auth_data)
    
    async def _operation_delete_application_authentication_method(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete application authentication method."""
        application_id = params.get("application_id", "")
        auth_id = params.get("auth_id", "")
        
        return await self._make_request("DELETE", f"applications/{application_id}/authentications/{auth_id}", params)
    
    # -------------------------
    # LDAP Operations
    # -------------------------
    
    async def _operation_get_ldap_directories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get LDAP directories."""
        result = await self._make_request("GET", "configuration/ldap", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["ldap_directories"] = result["result"].get("value", [])
            else:
                result["ldap_directories"] = result["result"]
        
        return result
    
    async def _operation_add_ldap_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add LDAP directory."""
        ldap_data = params.get("ldap_data", {})
        
        return await self._make_request("POST", "configuration/ldap", params, ldap_data)
    
    # -------------------------
    # Bulk Operations
    # -------------------------
    
    async def _operation_bulk_upload_accounts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Bulk upload accounts."""
        bulk_data = params.get("bulk_data", [])
        
        result = await self._make_request("POST", "bulkupload/accounts", params, {"accounts": bulk_data})
        
        if result["status"] == "success" and result["result"]:
            result["bulk_results"] = result["result"]
        
        return result
    
    async def _operation_bulk_upload_safes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Bulk upload safes."""
        bulk_data = params.get("bulk_data", [])
        
        result = await self._make_request("POST", "bulkupload/safes", params, {"safes": bulk_data})
        
        if result["status"] == "success" and result["result"]:
            result["bulk_results"] = result["result"]
        
        return result
    
    # -------------------------
    # SSH Key Operations
    # -------------------------
    
    async def _operation_get_ssh_keys(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get SSH keys for a user."""
        user_id = params.get("user_id", "")
        
        result = await self._make_request("GET", f"users/{user_id}/sshkeys", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["ssh_keys"] = result["result"].get("value", [])
            else:
                result["ssh_keys"] = result["result"]
        
        return result
    
    async def _operation_add_ssh_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add SSH key for a user."""
        user_id = params.get("user_id", "")
        ssh_key_data = params.get("ssh_key_data", {})
        
        return await self._make_request("POST", f"users/{user_id}/sshkeys", params, ssh_key_data)
    
    async def _operation_delete_ssh_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete SSH key for a user."""
        user_id = params.get("user_id", "")
        key_id = params.get("key_id", "")
        
        return await self._make_request("DELETE", f"users/{user_id}/sshkeys/{key_id}", params)


# Utility functions for common CyberArk operations
class CyberArkHelpers:
    """Helper functions for common CyberArk operations."""
    
    @staticmethod
    def create_account_data(name: str, address: str, username: str, platform_id: str, safe_name: str, 
                           password: str = "", **kwargs) -> Dict[str, Any]:
        """Create account data structure."""
        account_data = {
            "name": name,
            "address": address,
            "userName": username,
            "platformId": platform_id,
            "safeName": safe_name
        }
        
        if password:
            account_data["secret"] = password
        
        # Add any additional properties
        account_data.update(kwargs)
        
        return account_data
    
    @staticmethod
    def create_safe_data(safe_name: str, description: str = "", managing_cpm: str = "", 
                        number_of_days_retention: int = 7, **kwargs) -> Dict[str, Any]:
        """Create safe data structure."""
        safe_data = {
            "safeName": safe_name,
            "description": description,
            "managingCPM": managing_cpm,
            "numberOfDaysRetention": number_of_days_retention
        }
        
        # Add any additional properties
        safe_data.update(kwargs)
        
        return safe_data
    
    @staticmethod
    def create_user_data(username: str, initial_password: str, email: str = "", 
                        first_name: str = "", last_name: str = "", **kwargs) -> Dict[str, Any]:
        """Create user data structure."""
        user_data = {
            "username": username,
            "initialPassword": initial_password,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "changePasswordOnTheNextLogon": True,
            "passwordNeverExpires": False,
            "distinguishedName": "",
            "description": "",
            "location": "",
            "street": "",
            "city": "",
            "state": "",
            "zip": "",
            "country": "",
            "title": "",
            "organization": "",
            "department": "",
            "profession": "",
            "workPhone": "",
            "homePhone": "",
            "cellularPhone": "",
            "fax": "",
            "pagerNumber": "",
            "homePage": "",
            "notes": "",
            "businessAddress": "",
            "internet": "",
            "enableUser": True,
            "expiryDate": "",
            "userTypeName": "EPVUser"
        }
        
        # Add any additional properties
        user_data.update(kwargs)
        
        return user_data
    
    @staticmethod
    def create_safe_member_data(member_name: str, search_in: str = "Vault", 
                               permissions: Dict[str, bool] = None) -> Dict[str, Any]:
        """Create safe member data structure."""
        if permissions is None:
            permissions = {
                "useAccounts": True,
                "retrieveAccounts": True,
                "listAccounts": True,
                "addAccounts": False,
                "updateAccountContent": False,
                "updateAccountProperties": False,
                "initiateCPMAccountManagementOperations": False,
                "specifyNextAccountContent": False,
                "renameAccounts": False,
                "deleteAccounts": False,
                "unlockAccounts": False,
                "manageSafe": False,
                "manageSafeMembers": False,
                "backupSafe": False,
                "viewAuditLog": True,
                "viewSafeMembers": True,
                "requestsAuthorizationLevel1": False,
                "requestsAuthorizationLevel2": False,
                "accessWithoutConfirmation": False,
                "createFolders": False,
                "deleteFolders": False,
                "moveAccountsAndFolders": False
            }
        
        member_data = {
            "memberName": member_name,
            "searchIn": search_in,
            "permissions": permissions
        }
        
        return member_data
    
    @staticmethod
    def format_date_filter(date_str: str) -> str:
        """Format date string for CyberArk API filters."""
        # Convert YYYY-MM-DD to MM/DD/YYYY format expected by CyberArk
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%m/%d/%Y")
        except ValueError:
            return date_str
    
    @staticmethod
    def build_search_filter(criteria: str, search_type: str = "contains") -> str:
        """Build search filter for CyberArk API."""
        if search_type == "contains":
            return f"*{criteria}*"
        elif search_type == "startswith":
            return f"{criteria}*"
        elif search_type == "endswith":
            return f"*{criteria}"
        else:
            return criteria
    
    @staticmethod
    def parse_account_id(account_data: Dict[str, Any]) -> str:
        """Extract account ID from account data."""
        return account_data.get("id", "") or account_data.get("accountId", "")
    
    @staticmethod
    def validate_safe_name(safe_name: str) -> bool:
        """Validate safe name according to CyberArk rules."""
        # Safe names must be 1-28 characters, alphanumeric plus underscore and hyphen
        import re
        pattern = r'^[a-zA-Z0-9_-]{1,28}$'
        return bool(re.match(pattern, safe_name))
    
    @staticmethod
    def encode_password(password: str) -> str:
        """Encode password for secure transmission."""
        # In a real implementation, this might involve encryption
        return base64.b64encode(password.encode()).decode()
    
    @staticmethod
    def decode_password(encoded_password: str) -> str:
        """Decode password from secure format."""
        # In a real implementation, this might involve decryption
        return base64.b64decode(encoded_password).decode()


# Main test function for CyberArk Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== CyberArk Node Test Suite ===")
        
        # Get CyberArk credentials from environment or user input
        cyberark_url = os.environ.get("CYBERARK_URL")
        username = os.environ.get("CYBERARK_USERNAME")
        password = os.environ.get("CYBERARK_PASSWORD")
        
        if not cyberark_url:
            print("CyberArk URL not found in environment variables")
            print("Please set CYBERARK_URL")
            cyberark_url = input("Enter CyberArk PVWA URL: ")
        
        if not username:
            print("CyberArk username not found in environment variables")
            username = input("Enter CyberArk username: ")
        
        if not password:
            print("CyberArk password not found in environment variables")
            password = input("Enter CyberArk password: ")
        
        if not cyberark_url or not username or not password:
            print("CyberArk credentials are required for testing")
            return
        
        # Create an instance of the CyberArk Node
        node = CyberArkNode()
        
        # Test cases
        test_cases = [
            {
                "name": "Logon to CyberArk",
                "params": {
                    "operation": CyberArkOperation.LOGON,
                    "cyberark_url": cyberark_url,
                    "username": username,
                    "password": password
                },
                "expected_status": "success"
            }
        ]
        
        session_token = None
        
        # Run test cases
        total_tests = len(test_cases)
        passed_tests = 0
        
        for test_case in test_cases:
            print(f"\nRunning test: {test_case['name']}")
            
            try:
                # Prepare node data
                node_data = {
                    "params": test_case["params"]
                }
                
                # Execute the node
                result = await node.execute(node_data)
                
                # Check if the result status matches expected status
                if result["status"] == test_case["expected_status"]:
                    print(f"✅ PASS: {test_case['name']} - Status: {result['status']}")
                    if result.get("session_token"):
                        session_token = result["session_token"]
                        print(f"Session token obtained: {session_token[:20]}...")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
                # Add a delay between tests
                await asyncio.sleep(1.0)
                
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # If we have a session token, test additional operations
        if session_token:
            additional_tests = [
                {
                    "name": "Get Safes",
                    "params": {
                        "operation": CyberArkOperation.GET_SAFES,
                        "cyberark_url": cyberark_url,
                        "session_token": session_token,
                        "limit": 10
                    },
                    "expected_status": "success"
                },
                {
                    "name": "Logoff from CyberArk",
                    "params": {
                        "operation": CyberArkOperation.LOGOFF,
                        "cyberark_url": cyberark_url,
                        "session_token": session_token
                    },
                    "expected_status": "success"
                }
            ]
            
            for test_case in additional_tests:
                print(f"\nRunning test: {test_case['name']}")
                total_tests += 1
                
                try:
                    # Prepare node data
                    node_data = {
                        "params": test_case["params"]
                    }
                    
                    # Execute the node
                    result = await node.execute(node_data)
                    
                    # Check if the result status matches expected status
                    if result["status"] == test_case["expected_status"]:
                        print(f"✅ PASS: {test_case['name']} - Status: {result['status']}")
                        if result.get("safes"):
                            print(f"Found {len(result.get('safes', []))} safes")
                        if result.get("count"):
                            print(f"Total count: {result.get('count')}")
                        passed_tests += 1
                    else:
                        print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                        print(f"Error: {result.get('error')}")
                        
                    # Add a delay between tests
                    await asyncio.sleep(1.0)
                    
                except Exception as e:
                    print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")
        
        print("\nAll tests completed!")

    # Run the async tests
    asyncio.run(run_tests())

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("cyberark", CyberArkNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register CyberArkNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")