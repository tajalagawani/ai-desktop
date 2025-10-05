"""
OneLogin Node - Comprehensive integration with OneLogin Identity and Access Management API
Provides access to all OneLogin operations including user management, authentication, role management, and application management.
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

class OneLoginOperation:
    """Operations available on OneLogin Identity and Access Management API."""
    
    # Authentication Operations
    GENERATE_ACCESS_TOKEN = "generate_access_token"
    REVOKE_ACCESS_TOKEN = "revoke_access_token"
    CREATE_SESSION_LOGIN_TOKEN = "create_session_login_token"
    CREATE_SESSION = "create_session"
    VERIFY_FACTOR = "verify_factor"
    
    # User Management Operations
    GET_USERS = "get_users"
    GET_USER = "get_user"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    SET_PASSWORD_CLEAR_TEXT = "set_password_clear_text"
    SET_PASSWORD_SALT = "set_password_salt"
    SET_CUSTOM_ATTRIBUTES = "set_custom_attributes"
    LOCK_USER = "lock_user"
    UNLOCK_USER = "unlock_user"
    LOG_USER_OUT = "log_user_out"
    
    # Role Management Operations
    GET_ROLES = "get_roles"
    GET_ROLE = "get_role"
    CREATE_ROLE = "create_role"
    UPDATE_ROLE = "update_role"
    DELETE_ROLE = "delete_role"
    GET_ROLE_USERS = "get_role_users"
    ASSIGN_ROLE_TO_USER = "assign_role_to_user"
    REMOVE_ROLE_FROM_USER = "remove_role_from_user"
    GET_USER_ROLES = "get_user_roles"
    
    # Group Management Operations
    GET_GROUPS = "get_groups"
    GET_GROUP = "get_group"
    CREATE_GROUP = "create_group"
    UPDATE_GROUP = "update_group"
    DELETE_GROUP = "delete_group"
    
    # Application Management Operations
    GET_APPS = "get_apps"
    GET_APP = "get_app"
    CREATE_APP = "create_app"
    UPDATE_APP = "update_app"
    DELETE_APP = "delete_app"
    GET_APP_USERS = "get_app_users"
    ASSIGN_APP_TO_USER = "assign_app_to_user"
    REMOVE_APP_FROM_USER = "remove_app_from_user"
    
    # Multi-Factor Authentication Operations
    GET_FACTORS = "get_factors"
    ENROLL_FACTOR = "enroll_factor"
    ACTIVATE_FACTOR = "activate_factor"
    REMOVE_FACTOR = "remove_factor"
    GET_ENROLLED_FACTORS = "get_enrolled_factors"
    TRIGGER_MFA = "trigger_mfa"
    
    # SAML Operations
    GENERATE_SAML_ASSERTION = "generate_saml_assertion"
    GET_SAML_ASSERTION = "get_saml_assertion"
    VERIFY_SAML_FACTOR = "verify_saml_factor"
    
    # Event Management Operations
    GET_EVENTS = "get_events"
    CREATE_EVENT = "create_event"
    GET_EVENT_TYPES = "get_event_types"
    
    # Session Management Operations
    GET_SESSIONS = "get_sessions"
    DESTROY_SESSION = "destroy_session"
    GET_SESSION_LOGIN_TOKEN = "get_session_login_token"
    
    # Privilege Management Operations
    GET_PRIVILEGES = "get_privileges"
    ASSIGN_PRIVILEGE = "assign_privilege"
    REMOVE_PRIVILEGE = "remove_privilege"
    GET_ASSIGNED_PRIVILEGES = "get_assigned_privileges"
    
    # Configuration Operations
    GET_CONNECTORS = "get_connectors"
    GET_MAPPINGS = "get_mappings"
    CREATE_MAPPING = "create_mapping"
    UPDATE_MAPPING = "update_mapping"
    DELETE_MAPPING = "delete_mapping"
    
    # Invitation Operations
    INVITE_USER = "invite_user"
    SEND_INVITE_LINK = "send_invite_link"
    GENERATE_INVITE_LINK = "generate_invite_link"
    
    # Brand Management Operations
    GET_BRANDS = "get_brands"
    GET_BRAND = "get_brand"
    UPDATE_BRAND = "update_brand"
    
    # Smart Hook Operations
    GET_SMART_HOOKS = "get_smart_hooks"
    CREATE_SMART_HOOK = "create_smart_hook"
    UPDATE_SMART_HOOK = "update_smart_hook"
    DELETE_SMART_HOOK = "delete_smart_hook"
    
    # Risk Management Operations
    GET_RISK_RULES = "get_risk_rules"
    CREATE_RISK_RULE = "create_risk_rule"
    UPDATE_RISK_RULE = "update_risk_rule"
    DELETE_RISK_RULE = "delete_risk_rule"

class OneLoginNode(BaseNode):
    """
    Node for interacting with OneLogin Identity and Access Management API.
    Provides comprehensive functionality for user management, authentication, role management, and application management.
    """
    
    BASE_URL = "https://api.us.onelogin.com"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the OneLogin node."""
        return NodeSchema(
            node_type="onelogin",
            version="1.0.0",
            description="Comprehensive integration with OneLogin Identity and Access Management API for user management, authentication, and application management",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with OneLogin API",
                    required=True,
                    enum=[
                        OneLoginOperation.GENERATE_ACCESS_TOKEN,
                        OneLoginOperation.REVOKE_ACCESS_TOKEN,
                        OneLoginOperation.CREATE_SESSION_LOGIN_TOKEN,
                        OneLoginOperation.CREATE_SESSION,
                        OneLoginOperation.VERIFY_FACTOR,
                        OneLoginOperation.GET_USERS,
                        OneLoginOperation.GET_USER,
                        OneLoginOperation.CREATE_USER,
                        OneLoginOperation.UPDATE_USER,
                        OneLoginOperation.DELETE_USER,
                        OneLoginOperation.SET_PASSWORD_CLEAR_TEXT,
                        OneLoginOperation.SET_PASSWORD_SALT,
                        OneLoginOperation.SET_CUSTOM_ATTRIBUTES,
                        OneLoginOperation.LOCK_USER,
                        OneLoginOperation.UNLOCK_USER,
                        OneLoginOperation.LOG_USER_OUT,
                        OneLoginOperation.GET_ROLES,
                        OneLoginOperation.GET_ROLE,
                        OneLoginOperation.CREATE_ROLE,
                        OneLoginOperation.UPDATE_ROLE,
                        OneLoginOperation.DELETE_ROLE,
                        OneLoginOperation.GET_ROLE_USERS,
                        OneLoginOperation.ASSIGN_ROLE_TO_USER,
                        OneLoginOperation.REMOVE_ROLE_FROM_USER,
                        OneLoginOperation.GET_USER_ROLES,
                        OneLoginOperation.GET_GROUPS,
                        OneLoginOperation.GET_GROUP,
                        OneLoginOperation.CREATE_GROUP,
                        OneLoginOperation.UPDATE_GROUP,
                        OneLoginOperation.DELETE_GROUP,
                        OneLoginOperation.GET_APPS,
                        OneLoginOperation.GET_APP,
                        OneLoginOperation.CREATE_APP,
                        OneLoginOperation.UPDATE_APP,
                        OneLoginOperation.DELETE_APP,
                        OneLoginOperation.GET_APP_USERS,
                        OneLoginOperation.ASSIGN_APP_TO_USER,
                        OneLoginOperation.REMOVE_APP_FROM_USER,
                        OneLoginOperation.GET_FACTORS,
                        OneLoginOperation.ENROLL_FACTOR,
                        OneLoginOperation.ACTIVATE_FACTOR,
                        OneLoginOperation.REMOVE_FACTOR,
                        OneLoginOperation.GET_ENROLLED_FACTORS,
                        OneLoginOperation.TRIGGER_MFA,
                        OneLoginOperation.GENERATE_SAML_ASSERTION,
                        OneLoginOperation.GET_SAML_ASSERTION,
                        OneLoginOperation.VERIFY_SAML_FACTOR,
                        OneLoginOperation.GET_EVENTS,
                        OneLoginOperation.CREATE_EVENT,
                        OneLoginOperation.GET_EVENT_TYPES,
                        OneLoginOperation.GET_SESSIONS,
                        OneLoginOperation.DESTROY_SESSION,
                        OneLoginOperation.GET_SESSION_LOGIN_TOKEN,
                        OneLoginOperation.GET_PRIVILEGES,
                        OneLoginOperation.ASSIGN_PRIVILEGE,
                        OneLoginOperation.REMOVE_PRIVILEGE,
                        OneLoginOperation.GET_ASSIGNED_PRIVILEGES,
                        OneLoginOperation.GET_CONNECTORS,
                        OneLoginOperation.GET_MAPPINGS,
                        OneLoginOperation.CREATE_MAPPING,
                        OneLoginOperation.UPDATE_MAPPING,
                        OneLoginOperation.DELETE_MAPPING,
                        OneLoginOperation.INVITE_USER,
                        OneLoginOperation.SEND_INVITE_LINK,
                        OneLoginOperation.GENERATE_INVITE_LINK,
                        OneLoginOperation.GET_BRANDS,
                        OneLoginOperation.GET_BRAND,
                        OneLoginOperation.UPDATE_BRAND,
                        OneLoginOperation.GET_SMART_HOOKS,
                        OneLoginOperation.CREATE_SMART_HOOK,
                        OneLoginOperation.UPDATE_SMART_HOOK,
                        OneLoginOperation.DELETE_SMART_HOOK,
                        OneLoginOperation.GET_RISK_RULES,
                        OneLoginOperation.CREATE_RISK_RULE,
                        OneLoginOperation.UPDATE_RISK_RULE,
                        OneLoginOperation.DELETE_RISK_RULE
                    ]
                ),
                NodeParameter(
                    name="onelogin_url",
                    type=NodeParameterType.STRING,
                    description="OneLogin API base URL (default: https://api.us.onelogin.com)",
                    required=False,
                    default="https://api.us.onelogin.com"
                ),
                NodeParameter(
                    name="client_id",
                    type=NodeParameterType.STRING,
                    description="OneLogin API client ID",
                    required=False
                ),
                NodeParameter(
                    name="client_secret",
                    type=NodeParameterType.SECRET,
                    description="OneLogin API client secret",
                    required=False
                ),
                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.SECRET,
                    description="OneLogin API access token for authenticated requests",
                    required=False
                ),
                NodeParameter(
                    name="subdomain",
                    type=NodeParameterType.STRING,
                    description="OneLogin subdomain for your organization",
                    required=False
                ),
                NodeParameter(
                    name="user_id",
                    type=NodeParameterType.STRING,
                    description="User ID for user-specific operations",
                    required=False
                ),
                NodeParameter(
                    name="role_id",
                    type=NodeParameterType.STRING,
                    description="Role ID for role-specific operations",
                    required=False
                ),
                NodeParameter(
                    name="group_id",
                    type=NodeParameterType.STRING,
                    description="Group ID for group-specific operations",
                    required=False
                ),
                NodeParameter(
                    name="app_id",
                    type=NodeParameterType.STRING,
                    description="Application ID for app-specific operations",
                    required=False
                ),
                NodeParameter(
                    name="session_id",
                    type=NodeParameterType.STRING,
                    description="Session ID for session management",
                    required=False
                ),
                NodeParameter(
                    name="device_id",
                    type=NodeParameterType.STRING,
                    description="Device ID for MFA operations",
                    required=False
                ),
                NodeParameter(
                    name="factor_id",
                    type=NodeParameterType.STRING,
                    description="Factor ID for MFA operations",
                    required=False
                ),
                NodeParameter(
                    name="privilege_id",
                    type=NodeParameterType.STRING,
                    description="Privilege ID for privilege operations",
                    required=False
                ),
                NodeParameter(
                    name="mapping_id",
                    type=NodeParameterType.STRING,
                    description="Mapping ID for mapping operations",
                    required=False
                ),
                NodeParameter(
                    name="brand_id",
                    type=NodeParameterType.STRING,
                    description="Brand ID for brand operations",
                    required=False
                ),
                NodeParameter(
                    name="hook_id",
                    type=NodeParameterType.STRING,
                    description="Smart Hook ID for hook operations",
                    required=False
                ),
                NodeParameter(
                    name="rule_id",
                    type=NodeParameterType.STRING,
                    description="Risk Rule ID for risk rule operations",
                    required=False
                ),
                NodeParameter(
                    name="user_data",
                    type=NodeParameterType.OBJECT,
                    description="User data for user creation/update",
                    required=False
                ),
                NodeParameter(
                    name="role_data",
                    type=NodeParameterType.OBJECT,
                    description="Role data for role creation/update",
                    required=False
                ),
                NodeParameter(
                    name="group_data",
                    type=NodeParameterType.OBJECT,
                    description="Group data for group creation/update",
                    required=False
                ),
                NodeParameter(
                    name="app_data",
                    type=NodeParameterType.OBJECT,
                    description="Application data for app creation/update",
                    required=False
                ),
                NodeParameter(
                    name="factor_data",
                    type=NodeParameterType.OBJECT,
                    description="Factor data for MFA enrollment",
                    required=False
                ),
                NodeParameter(
                    name="event_data",
                    type=NodeParameterType.OBJECT,
                    description="Event data for event creation",
                    required=False
                ),
                NodeParameter(
                    name="mapping_data",
                    type=NodeParameterType.OBJECT,
                    description="Mapping data for mapping creation/update",
                    required=False
                ),
                NodeParameter(
                    name="brand_data",
                    type=NodeParameterType.OBJECT,
                    description="Brand data for brand updates",
                    required=False
                ),
                NodeParameter(
                    name="hook_data",
                    type=NodeParameterType.OBJECT,
                    description="Smart Hook data for hook creation/update",
                    required=False
                ),
                NodeParameter(
                    name="rule_data",
                    type=NodeParameterType.OBJECT,
                    description="Risk Rule data for rule creation/update",
                    required=False
                ),
                NodeParameter(
                    name="username",
                    type=NodeParameterType.STRING,
                    description="Username for authentication operations",
                    required=False
                ),
                NodeParameter(
                    name="password",
                    type=NodeParameterType.SECRET,
                    description="Password for authentication operations",
                    required=False
                ),
                NodeParameter(
                    name="email",
                    type=NodeParameterType.STRING,
                    description="Email address for user operations",
                    required=False
                ),
                NodeParameter(
                    name="otp_token",
                    type=NodeParameterType.STRING,
                    description="OTP token for MFA verification",
                    required=False
                ),
                NodeParameter(
                    name="state_token",
                    type=NodeParameterType.STRING,
                    description="State token for authentication flow",
                    required=False
                ),
                NodeParameter(
                    name="search",
                    type=NodeParameterType.STRING,
                    description="Search criteria for filtering results",
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
                    name="after_cursor",
                    type=NodeParameterType.STRING,
                    description="Cursor for pagination",
                    required=False
                ),
                NodeParameter(
                    name="before_cursor",
                    type=NodeParameterType.STRING,
                    description="Cursor for reverse pagination",
                    required=False
                ),
                NodeParameter(
                    name="since",
                    type=NodeParameterType.STRING,
                    description="Start date for event queries (ISO 8601 format)",
                    required=False
                ),
                NodeParameter(
                    name="until",
                    type=NodeParameterType.STRING,
                    description="End date for event queries (ISO 8601 format)",
                    required=False
                ),
                NodeParameter(
                    name="event_type_id",
                    type=NodeParameterType.STRING,
                    description="Event type ID for filtering events",
                    required=False
                ),
                NodeParameter(
                    name="resolution",
                    type=NodeParameterType.STRING,
                    description="Resolution for event data aggregation",
                    required=False
                ),
                NodeParameter(
                    name="grant_type",
                    type=NodeParameterType.STRING,
                    description="OAuth2 grant type",
                    required=False,
                    default="client_credentials"
                ),
                NodeParameter(
                    name="scope",
                    type=NodeParameterType.STRING,
                    description="OAuth2 scope for access token",
                    required=False
                ),
                NodeParameter(
                    name="fields",
                    type=NodeParameterType.STRING,
                    description="Comma-separated list of fields to return",
                    required=False
                ),
                NodeParameter(
                    name="include",
                    type=NodeParameterType.STRING,
                    description="Related resources to include in response",
                    required=False
                ),
                NodeParameter(
                    name="directory_id",
                    type=NodeParameterType.STRING,
                    description="Directory ID for user operations",
                    required=False
                ),
                NodeParameter(
                    name="ip_address",
                    type=NodeParameterType.STRING,
                    description="IP address for login operations",
                    required=False
                ),
                NodeParameter(
                    name="browser_id",
                    type=NodeParameterType.STRING,
                    description="Browser ID for session management",
                    required=False
                ),
                NodeParameter(
                    name="custom_attributes",
                    type=NodeParameterType.OBJECT,
                    description="Custom attributes for user/app operations",
                    required=False
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "access_token": NodeParameterType.STRING,
                "token_type": NodeParameterType.STRING,
                "expires_in": NodeParameterType.NUMBER,
                "session_token": NodeParameterType.STRING,
                "state_token": NodeParameterType.STRING,
                "users": NodeParameterType.ARRAY,
                "user": NodeParameterType.OBJECT,
                "roles": NodeParameterType.ARRAY,
                "role": NodeParameterType.OBJECT,
                "groups": NodeParameterType.ARRAY,
                "group": NodeParameterType.OBJECT,
                "apps": NodeParameterType.ARRAY,
                "app": NodeParameterType.OBJECT,
                "factors": NodeParameterType.ARRAY,
                "factor": NodeParameterType.OBJECT,
                "enrolled_factors": NodeParameterType.ARRAY,
                "saml_response": NodeParameterType.STRING,
                "assertion": NodeParameterType.STRING,
                "events": NodeParameterType.ARRAY,
                "event": NodeParameterType.OBJECT,
                "event_types": NodeParameterType.ARRAY,
                "sessions": NodeParameterType.ARRAY,
                "session": NodeParameterType.OBJECT,
                "privileges": NodeParameterType.ARRAY,
                "privilege": NodeParameterType.OBJECT,
                "connectors": NodeParameterType.ARRAY,
                "mappings": NodeParameterType.ARRAY,
                "mapping": NodeParameterType.OBJECT,
                "brands": NodeParameterType.ARRAY,
                "brand": NodeParameterType.OBJECT,
                "smart_hooks": NodeParameterType.ARRAY,
                "smart_hook": NodeParameterType.OBJECT,
                "risk_rules": NodeParameterType.ARRAY,
                "risk_rule": NodeParameterType.OBJECT,
                "invite_link": NodeParameterType.STRING,
                "custom_attributes": NodeParameterType.OBJECT,
                "password_changed": NodeParameterType.BOOLEAN,
                "user_locked": NodeParameterType.BOOLEAN,
                "user_unlocked": NodeParameterType.BOOLEAN,
                "factor_enrolled": NodeParameterType.BOOLEAN,
                "factor_activated": NodeParameterType.BOOLEAN,
                "mfa_triggered": NodeParameterType.BOOLEAN,
                "verification_result": NodeParameterType.BOOLEAN,
                "pagination": NodeParameterType.OBJECT,
                "count": NodeParameterType.NUMBER,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["onelogin", "identity", "access-management", "authentication", "sso", "mfa"],
            author="System",
            documentation_url="https://developers.onelogin.com"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Token generation validation
        if operation == OneLoginOperation.GENERATE_ACCESS_TOKEN:
            if not params.get("client_id") or not params.get("client_secret"):
                raise NodeValidationError("Client ID and client secret are required for token generation")
                
        # Most operations require access token except token generation
        elif operation != OneLoginOperation.GENERATE_ACCESS_TOKEN:
            if not params.get("access_token"):
                raise NodeValidationError("Access token is required for authenticated operations")
                
        # User operations validation
        if operation in [OneLoginOperation.GET_USER, OneLoginOperation.UPDATE_USER, OneLoginOperation.DELETE_USER,
                        OneLoginOperation.SET_PASSWORD_CLEAR_TEXT, OneLoginOperation.SET_PASSWORD_SALT,
                        OneLoginOperation.SET_CUSTOM_ATTRIBUTES, OneLoginOperation.LOCK_USER,
                        OneLoginOperation.UNLOCK_USER, OneLoginOperation.LOG_USER_OUT,
                        OneLoginOperation.ASSIGN_ROLE_TO_USER, OneLoginOperation.REMOVE_ROLE_FROM_USER,
                        OneLoginOperation.GET_USER_ROLES, OneLoginOperation.GET_ENROLLED_FACTORS]:
            if not params.get("user_id"):
                raise NodeValidationError("User ID is required for user-specific operations")
                
        elif operation in [OneLoginOperation.CREATE_USER, OneLoginOperation.UPDATE_USER]:
            if not params.get("user_data"):
                raise NodeValidationError("User data is required for user creation/update")
                
        # Role operations validation
        elif operation in [OneLoginOperation.GET_ROLE, OneLoginOperation.UPDATE_ROLE, OneLoginOperation.DELETE_ROLE,
                          OneLoginOperation.GET_ROLE_USERS]:
            if not params.get("role_id"):
                raise NodeValidationError("Role ID is required for role-specific operations")
                
        elif operation in [OneLoginOperation.CREATE_ROLE, OneLoginOperation.UPDATE_ROLE]:
            if not params.get("role_data"):
                raise NodeValidationError("Role data is required for role creation/update")
                
        # Group operations validation
        elif operation in [OneLoginOperation.GET_GROUP, OneLoginOperation.UPDATE_GROUP, OneLoginOperation.DELETE_GROUP]:
            if not params.get("group_id"):
                raise NodeValidationError("Group ID is required for group-specific operations")
                
        elif operation in [OneLoginOperation.CREATE_GROUP, OneLoginOperation.UPDATE_GROUP]:
            if not params.get("group_data"):
                raise NodeValidationError("Group data is required for group creation/update")
                
        # App operations validation
        elif operation in [OneLoginOperation.GET_APP, OneLoginOperation.UPDATE_APP, OneLoginOperation.DELETE_APP,
                          OneLoginOperation.GET_APP_USERS]:
            if not params.get("app_id"):
                raise NodeValidationError("App ID is required for app-specific operations")
                
        elif operation in [OneLoginOperation.CREATE_APP, OneLoginOperation.UPDATE_APP]:
            if not params.get("app_data"):
                raise NodeValidationError("App data is required for app creation/update")
                
        # MFA operations validation
        elif operation in [OneLoginOperation.ACTIVATE_FACTOR, OneLoginOperation.REMOVE_FACTOR]:
            if not params.get("device_id"):
                raise NodeValidationError("Device ID is required for factor operations")
                
        elif operation == OneLoginOperation.ENROLL_FACTOR:
            if not params.get("factor_data"):
                raise NodeValidationError("Factor data is required for factor enrollment")
                
        elif operation == OneLoginOperation.VERIFY_FACTOR:
            if not params.get("otp_token"):
                raise NodeValidationError("OTP token is required for factor verification")
                
        # Authentication operations validation
        elif operation == OneLoginOperation.CREATE_SESSION_LOGIN_TOKEN:
            if not params.get("username") or not params.get("password"):
                raise NodeValidationError("Username and password are required for session login token creation")
                
        elif operation == OneLoginOperation.CREATE_SESSION:
            if not params.get("session_token"):
                raise NodeValidationError("Session token is required for session creation")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the OneLogin node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Execute the appropriate operation
            if operation == OneLoginOperation.GENERATE_ACCESS_TOKEN:
                return await self._operation_generate_access_token(validated_data)
            elif operation == OneLoginOperation.REVOKE_ACCESS_TOKEN:
                return await self._operation_revoke_access_token(validated_data)
            elif operation == OneLoginOperation.CREATE_SESSION_LOGIN_TOKEN:
                return await self._operation_create_session_login_token(validated_data)
            elif operation == OneLoginOperation.CREATE_SESSION:
                return await self._operation_create_session(validated_data)
            elif operation == OneLoginOperation.VERIFY_FACTOR:
                return await self._operation_verify_factor(validated_data)
            elif operation == OneLoginOperation.GET_USERS:
                return await self._operation_get_users(validated_data)
            elif operation == OneLoginOperation.GET_USER:
                return await self._operation_get_user(validated_data)
            elif operation == OneLoginOperation.CREATE_USER:
                return await self._operation_create_user(validated_data)
            elif operation == OneLoginOperation.UPDATE_USER:
                return await self._operation_update_user(validated_data)
            elif operation == OneLoginOperation.DELETE_USER:
                return await self._operation_delete_user(validated_data)
            elif operation == OneLoginOperation.SET_PASSWORD_CLEAR_TEXT:
                return await self._operation_set_password_clear_text(validated_data)
            elif operation == OneLoginOperation.SET_PASSWORD_SALT:
                return await self._operation_set_password_salt(validated_data)
            elif operation == OneLoginOperation.SET_CUSTOM_ATTRIBUTES:
                return await self._operation_set_custom_attributes(validated_data)
            elif operation == OneLoginOperation.LOCK_USER:
                return await self._operation_lock_user(validated_data)
            elif operation == OneLoginOperation.UNLOCK_USER:
                return await self._operation_unlock_user(validated_data)
            elif operation == OneLoginOperation.LOG_USER_OUT:
                return await self._operation_log_user_out(validated_data)
            elif operation == OneLoginOperation.GET_ROLES:
                return await self._operation_get_roles(validated_data)
            elif operation == OneLoginOperation.GET_ROLE:
                return await self._operation_get_role(validated_data)
            elif operation == OneLoginOperation.CREATE_ROLE:
                return await self._operation_create_role(validated_data)
            elif operation == OneLoginOperation.UPDATE_ROLE:
                return await self._operation_update_role(validated_data)
            elif operation == OneLoginOperation.DELETE_ROLE:
                return await self._operation_delete_role(validated_data)
            elif operation == OneLoginOperation.GET_ROLE_USERS:
                return await self._operation_get_role_users(validated_data)
            elif operation == OneLoginOperation.ASSIGN_ROLE_TO_USER:
                return await self._operation_assign_role_to_user(validated_data)
            elif operation == OneLoginOperation.REMOVE_ROLE_FROM_USER:
                return await self._operation_remove_role_from_user(validated_data)
            elif operation == OneLoginOperation.GET_USER_ROLES:
                return await self._operation_get_user_roles(validated_data)
            elif operation == OneLoginOperation.GET_GROUPS:
                return await self._operation_get_groups(validated_data)
            elif operation == OneLoginOperation.GET_GROUP:
                return await self._operation_get_group(validated_data)
            elif operation == OneLoginOperation.CREATE_GROUP:
                return await self._operation_create_group(validated_data)
            elif operation == OneLoginOperation.UPDATE_GROUP:
                return await self._operation_update_group(validated_data)
            elif operation == OneLoginOperation.DELETE_GROUP:
                return await self._operation_delete_group(validated_data)
            elif operation == OneLoginOperation.GET_APPS:
                return await self._operation_get_apps(validated_data)
            elif operation == OneLoginOperation.GET_APP:
                return await self._operation_get_app(validated_data)
            elif operation == OneLoginOperation.CREATE_APP:
                return await self._operation_create_app(validated_data)
            elif operation == OneLoginOperation.UPDATE_APP:
                return await self._operation_update_app(validated_data)
            elif operation == OneLoginOperation.DELETE_APP:
                return await self._operation_delete_app(validated_data)
            elif operation == OneLoginOperation.GET_APP_USERS:
                return await self._operation_get_app_users(validated_data)
            elif operation == OneLoginOperation.ASSIGN_APP_TO_USER:
                return await self._operation_assign_app_to_user(validated_data)
            elif operation == OneLoginOperation.REMOVE_APP_FROM_USER:
                return await self._operation_remove_app_from_user(validated_data)
            elif operation == OneLoginOperation.GET_FACTORS:
                return await self._operation_get_factors(validated_data)
            elif operation == OneLoginOperation.ENROLL_FACTOR:
                return await self._operation_enroll_factor(validated_data)
            elif operation == OneLoginOperation.ACTIVATE_FACTOR:
                return await self._operation_activate_factor(validated_data)
            elif operation == OneLoginOperation.REMOVE_FACTOR:
                return await self._operation_remove_factor(validated_data)
            elif operation == OneLoginOperation.GET_ENROLLED_FACTORS:
                return await self._operation_get_enrolled_factors(validated_data)
            elif operation == OneLoginOperation.TRIGGER_MFA:
                return await self._operation_trigger_mfa(validated_data)
            elif operation == OneLoginOperation.GENERATE_SAML_ASSERTION:
                return await self._operation_generate_saml_assertion(validated_data)
            elif operation == OneLoginOperation.GET_SAML_ASSERTION:
                return await self._operation_get_saml_assertion(validated_data)
            elif operation == OneLoginOperation.VERIFY_SAML_FACTOR:
                return await self._operation_verify_saml_factor(validated_data)
            elif operation == OneLoginOperation.GET_EVENTS:
                return await self._operation_get_events(validated_data)
            elif operation == OneLoginOperation.CREATE_EVENT:
                return await self._operation_create_event(validated_data)
            elif operation == OneLoginOperation.GET_EVENT_TYPES:
                return await self._operation_get_event_types(validated_data)
            elif operation == OneLoginOperation.GET_SESSIONS:
                return await self._operation_get_sessions(validated_data)
            elif operation == OneLoginOperation.DESTROY_SESSION:
                return await self._operation_destroy_session(validated_data)
            elif operation == OneLoginOperation.GET_SESSION_LOGIN_TOKEN:
                return await self._operation_get_session_login_token(validated_data)
            elif operation == OneLoginOperation.GET_PRIVILEGES:
                return await self._operation_get_privileges(validated_data)
            elif operation == OneLoginOperation.ASSIGN_PRIVILEGE:
                return await self._operation_assign_privilege(validated_data)
            elif operation == OneLoginOperation.REMOVE_PRIVILEGE:
                return await self._operation_remove_privilege(validated_data)
            elif operation == OneLoginOperation.GET_ASSIGNED_PRIVILEGES:
                return await self._operation_get_assigned_privileges(validated_data)
            elif operation == OneLoginOperation.GET_CONNECTORS:
                return await self._operation_get_connectors(validated_data)
            elif operation == OneLoginOperation.GET_MAPPINGS:
                return await self._operation_get_mappings(validated_data)
            elif operation == OneLoginOperation.CREATE_MAPPING:
                return await self._operation_create_mapping(validated_data)
            elif operation == OneLoginOperation.UPDATE_MAPPING:
                return await self._operation_update_mapping(validated_data)
            elif operation == OneLoginOperation.DELETE_MAPPING:
                return await self._operation_delete_mapping(validated_data)
            elif operation == OneLoginOperation.INVITE_USER:
                return await self._operation_invite_user(validated_data)
            elif operation == OneLoginOperation.SEND_INVITE_LINK:
                return await self._operation_send_invite_link(validated_data)
            elif operation == OneLoginOperation.GENERATE_INVITE_LINK:
                return await self._operation_generate_invite_link(validated_data)
            elif operation == OneLoginOperation.GET_BRANDS:
                return await self._operation_get_brands(validated_data)
            elif operation == OneLoginOperation.GET_BRAND:
                return await self._operation_get_brand(validated_data)
            elif operation == OneLoginOperation.UPDATE_BRAND:
                return await self._operation_update_brand(validated_data)
            elif operation == OneLoginOperation.GET_SMART_HOOKS:
                return await self._operation_get_smart_hooks(validated_data)
            elif operation == OneLoginOperation.CREATE_SMART_HOOK:
                return await self._operation_create_smart_hook(validated_data)
            elif operation == OneLoginOperation.UPDATE_SMART_HOOK:
                return await self._operation_update_smart_hook(validated_data)
            elif operation == OneLoginOperation.DELETE_SMART_HOOK:
                return await self._operation_delete_smart_hook(validated_data)
            elif operation == OneLoginOperation.GET_RISK_RULES:
                return await self._operation_get_risk_rules(validated_data)
            elif operation == OneLoginOperation.CREATE_RISK_RULE:
                return await self._operation_create_risk_rule(validated_data)
            elif operation == OneLoginOperation.UPDATE_RISK_RULE:
                return await self._operation_update_risk_rule(validated_data)
            elif operation == OneLoginOperation.DELETE_RISK_RULE:
                return await self._operation_delete_risk_rule(validated_data)
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
            error_message = f"Error in OneLogin node: {str(e)}"
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
                          data: Optional[Dict[str, Any]] = None, api_version: str = "2") -> Dict[str, Any]:
        """Make an HTTP request to the OneLogin API."""
        onelogin_url = params.get("onelogin_url", self.BASE_URL)
        url = f"{onelogin_url}/api/{api_version}/{endpoint.lstrip('/')}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add access token header if provided
        if params.get("access_token"):
            headers["Authorization"] = f"bearer:{params.get('access_token')}"
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                response_headers = dict(response.headers)
                
                # Handle different response content types
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"OneLogin API error {response.status}: {response_data}"
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
    
    async def _operation_generate_access_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate OAuth2 access token."""
        client_id = params.get("client_id", "")
        client_secret = params.get("client_secret", "")
        grant_type = params.get("grant_type", "client_credentials")
        scope = params.get("scope", "")
        
        request_data = {
            "grant_type": grant_type
        }
        
        if scope:
            request_data["scope"] = scope
        
        # Use basic auth for client credentials
        auth_string = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        # Override headers for this specific call
        headers = {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json"
        }
        
        onelogin_url = params.get("onelogin_url", self.BASE_URL)
        url = f"{onelogin_url}/auth/oauth2/v2/token"
        
        try:
            async with self.session.post(url, headers=headers, json=request_data) as response:
                response_headers = dict(response.headers)
                
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"OneLogin API error {response.status}: {response_data}"
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                result = {
                    "status": "success",
                    "result": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
                # Extract token information
                if isinstance(response_data, dict):
                    result["access_token"] = response_data.get("access_token", "")
                    result["token_type"] = response_data.get("token_type", "")
                    result["expires_in"] = response_data.get("expires_in", 0)
                
                return result
                
        except aiohttp.ClientError as e:
            error_message = f"HTTP error: {str(e)}"
            return {
                "status": "error",
                "error": error_message,
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    async def _operation_revoke_access_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Revoke OAuth2 access token."""
        access_token = params.get("access_token", "")
        
        request_data = {
            "access_token": access_token
        }
        
        return await self._make_request("POST", "auth/oauth2/revoke", params, request_data)
    
    async def _operation_create_session_login_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create session login token."""
        username = params.get("username", "")
        password = params.get("password", "")
        subdomain = params.get("subdomain", "")
        ip_address = params.get("ip_address", "")
        
        request_data = {
            "username_or_email": username,
            "password": password,
            "subdomain": subdomain
        }
        
        if ip_address:
            request_data["ip_address"] = ip_address
        
        result = await self._make_request("POST", "login/auth", params, request_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["session_token"] = result["result"].get("session_token", "")
                result["state_token"] = result["result"].get("state_token", "")
                result["user"] = result["result"].get("user", {})
        
        return result
    
    async def _operation_create_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create session."""
        session_token = params.get("session_token", "")
        
        request_data = {
            "session_token": session_token
        }
        
        result = await self._make_request("POST", "sessions", params, request_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["session"] = result["result"]
        
        return result
    
    async def _operation_verify_factor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify MFA factor."""
        device_id = params.get("device_id", "")
        state_token = params.get("state_token", "")
        otp_token = params.get("otp_token", "")
        
        request_data = {
            "device_id": device_id,
            "state_token": state_token,
            "otp_token": otp_token
        }
        
        result = await self._make_request("POST", "login/verify_factor", params, request_data, api_version="1")
        
        if result["status"] == "success":
            result["verification_result"] = True
        else:
            result["verification_result"] = False
        
        return result
    
    # -------------------------
    # User Management Operations
    # -------------------------
    
    async def _operation_get_users(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get users list."""
        query_params = []
        
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        if params.get("after_cursor"):
            query_params.append(f"after_cursor={params.get('after_cursor')}")
        if params.get("before_cursor"):
            query_params.append(f"before_cursor={params.get('before_cursor')}")
        if params.get("search"):
            query_params.append(f"search={params.get('search')}")
        if params.get("fields"):
            query_params.append(f"fields={params.get('fields')}")
        
        endpoint = "users"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["users"] = result["result"].get("data", [])
                result["pagination"] = result["result"].get("pagination", {})
            else:
                result["users"] = result["result"]
        
        return result
    
    async def _operation_get_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific user."""
        user_id = params.get("user_id", "")
        
        result = await self._make_request("GET", f"users/{user_id}", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["user"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["user"] = result["result"]
        
        return result
    
    async def _operation_create_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        user_data = params.get("user_data", {})
        
        result = await self._make_request("POST", "users", params, user_data)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["user"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["user"] = result["result"]
        
        return result
    
    async def _operation_update_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing user."""
        user_id = params.get("user_id", "")
        user_data = params.get("user_data", {})
        
        result = await self._make_request("PUT", f"users/{user_id}", params, user_data)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["user"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["user"] = result["result"]
        
        return result
    
    async def _operation_delete_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a user."""
        user_id = params.get("user_id", "")
        
        return await self._make_request("DELETE", f"users/{user_id}", params)
    
    async def _operation_set_password_clear_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set user password using clear text."""
        user_id = params.get("user_id", "")
        password = params.get("password", "")
        
        request_data = {
            "password": password,
            "password_confirmation": password
        }
        
        result = await self._make_request("PUT", f"users/{user_id}/set_password_clear_text", params, request_data, api_version="1")
        
        if result["status"] == "success":
            result["password_changed"] = True
        else:
            result["password_changed"] = False
        
        return result
    
    async def _operation_set_password_salt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set user password using salt."""
        user_id = params.get("user_id", "")
        password = params.get("password", "")
        
        request_data = {
            "password": password,
            "password_confirmation": password,
            "password_algorithm": "SHA-1"
        }
        
        result = await self._make_request("PUT", f"users/{user_id}/set_password_using_salt", params, request_data, api_version="1")
        
        if result["status"] == "success":
            result["password_changed"] = True
        else:
            result["password_changed"] = False
        
        return result
    
    async def _operation_set_custom_attributes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set custom attributes for a user."""
        user_id = params.get("user_id", "")
        custom_attributes = params.get("custom_attributes", {})
        
        request_data = {
            "custom_attributes": custom_attributes
        }
        
        result = await self._make_request("PUT", f"users/{user_id}/set_custom_attributes", params, request_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            result["custom_attributes"] = result["result"].get("custom_attributes", {})
        
        return result
    
    async def _operation_lock_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lock a user account."""
        user_id = params.get("user_id", "")
        
        result = await self._make_request("PUT", f"users/{user_id}/lock_user", params, api_version="1")
        
        if result["status"] == "success":
            result["user_locked"] = True
        else:
            result["user_locked"] = False
        
        return result
    
    async def _operation_unlock_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unlock a user account."""
        user_id = params.get("user_id", "")
        
        result = await self._make_request("PUT", f"users/{user_id}/unlock_user", params, api_version="1")
        
        if result["status"] == "success":
            result["user_unlocked"] = True
        else:
            result["user_unlocked"] = False
        
        return result
    
    async def _operation_log_user_out(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Log user out of all sessions."""
        user_id = params.get("user_id", "")
        
        return await self._make_request("PUT", f"users/{user_id}/logout", params, api_version="1")
    
    # -------------------------
    # Role Management Operations
    # -------------------------
    
    async def _operation_get_roles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get roles list."""
        query_params = []
        
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        if params.get("after_cursor"):
            query_params.append(f"after_cursor={params.get('after_cursor')}")
        if params.get("before_cursor"):
            query_params.append(f"before_cursor={params.get('before_cursor')}")
        
        endpoint = "roles"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["roles"] = result["result"].get("data", [])
                result["pagination"] = result["result"].get("pagination", {})
            else:
                result["roles"] = result["result"]
        
        return result
    
    async def _operation_get_role(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific role."""
        role_id = params.get("role_id", "")
        
        result = await self._make_request("GET", f"roles/{role_id}", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["role"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["role"] = result["result"]
        
        return result
    
    async def _operation_create_role(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new role."""
        role_data = params.get("role_data", {})
        
        result = await self._make_request("POST", "roles", params, role_data)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["role"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["role"] = result["result"]
        
        return result
    
    async def _operation_update_role(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing role."""
        role_id = params.get("role_id", "")
        role_data = params.get("role_data", {})
        
        result = await self._make_request("PUT", f"roles/{role_id}", params, role_data)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["role"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["role"] = result["result"]
        
        return result
    
    async def _operation_delete_role(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a role."""
        role_id = params.get("role_id", "")
        
        return await self._make_request("DELETE", f"roles/{role_id}", params)
    
    async def _operation_get_role_users(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get users assigned to a role."""
        role_id = params.get("role_id", "")
        
        query_params = []
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        if params.get("after_cursor"):
            query_params.append(f"after_cursor={params.get('after_cursor')}")
        
        endpoint = f"roles/{role_id}/users"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["users"] = result["result"].get("data", [])
                result["pagination"] = result["result"].get("pagination", {})
            else:
                result["users"] = result["result"]
        
        return result
    
    async def _operation_assign_role_to_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assign role to user."""
        user_id = params.get("user_id", "")
        role_id = params.get("role_id", "")
        
        request_data = {
            "role_id_array": [role_id]
        }
        
        return await self._make_request("PUT", f"users/{user_id}/add_roles", params, request_data, api_version="1")
    
    async def _operation_remove_role_from_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove role from user."""
        user_id = params.get("user_id", "")
        role_id = params.get("role_id", "")
        
        request_data = {
            "role_id_array": [role_id]
        }
        
        return await self._make_request("PUT", f"users/{user_id}/remove_roles", params, request_data, api_version="1")
    
    async def _operation_get_user_roles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get roles assigned to a user."""
        user_id = params.get("user_id", "")
        
        result = await self._make_request("GET", f"users/{user_id}/roles", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["roles"] = result["result"].get("data", [])
            else:
                result["roles"] = result["result"]
        
        return result
    
    # -------------------------
    # Group Management Operations
    # -------------------------
    
    async def _operation_get_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get groups list."""
        query_params = []
        
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        if params.get("search"):
            query_params.append(f"search={params.get('search')}")
        
        endpoint = "groups"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["groups"] = result["result"].get("data", [])
            else:
                result["groups"] = result["result"]
        
        return result
    
    async def _operation_get_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific group."""
        group_id = params.get("group_id", "")
        
        result = await self._make_request("GET", f"groups/{group_id}", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["group"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["group"] = result["result"]
        
        return result
    
    async def _operation_create_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new group."""
        group_data = params.get("group_data", {})
        
        result = await self._make_request("POST", "groups", params, group_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["group"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["group"] = result["result"]
        
        return result
    
    async def _operation_update_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing group."""
        group_id = params.get("group_id", "")
        group_data = params.get("group_data", {})
        
        result = await self._make_request("PUT", f"groups/{group_id}", params, group_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["group"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["group"] = result["result"]
        
        return result
    
    async def _operation_delete_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a group."""
        group_id = params.get("group_id", "")
        
        return await self._make_request("DELETE", f"groups/{group_id}", params, api_version="1")
    
    # -------------------------
    # Application Management Operations
    # -------------------------
    
    async def _operation_get_apps(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get applications list."""
        query_params = []
        
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        if params.get("after_cursor"):
            query_params.append(f"after_cursor={params.get('after_cursor')}")
        if params.get("before_cursor"):
            query_params.append(f"before_cursor={params.get('before_cursor')}")
        
        endpoint = "apps"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["apps"] = result["result"].get("data", [])
                result["pagination"] = result["result"].get("pagination", {})
            else:
                result["apps"] = result["result"]
        
        return result
    
    async def _operation_get_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific application."""
        app_id = params.get("app_id", "")
        
        result = await self._make_request("GET", f"apps/{app_id}", params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["app"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["app"] = result["result"]
        
        return result
    
    async def _operation_create_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new application."""
        app_data = params.get("app_data", {})
        
        result = await self._make_request("POST", "apps", params, app_data)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["app"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["app"] = result["result"]
        
        return result
    
    async def _operation_update_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing application."""
        app_id = params.get("app_id", "")
        app_data = params.get("app_data", {})
        
        result = await self._make_request("PUT", f"apps/{app_id}", params, app_data)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["app"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["app"] = result["result"]
        
        return result
    
    async def _operation_delete_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an application."""
        app_id = params.get("app_id", "")
        
        return await self._make_request("DELETE", f"apps/{app_id}", params)
    
    async def _operation_get_app_users(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get users assigned to an application."""
        app_id = params.get("app_id", "")
        
        query_params = []
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        if params.get("after_cursor"):
            query_params.append(f"after_cursor={params.get('after_cursor')}")
        
        endpoint = f"apps/{app_id}/users"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["users"] = result["result"].get("data", [])
                result["pagination"] = result["result"].get("pagination", {})
            else:
                result["users"] = result["result"]
        
        return result
    
    async def _operation_assign_app_to_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assign application to user."""
        app_id = params.get("app_id", "")
        user_id = params.get("user_id", "")
        
        request_data = {
            "user_ids": [user_id]
        }
        
        return await self._make_request("POST", f"apps/{app_id}/users", params, request_data)
    
    async def _operation_remove_app_from_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove application from user."""
        app_id = params.get("app_id", "")
        user_id = params.get("user_id", "")
        
        return await self._make_request("DELETE", f"apps/{app_id}/users/{user_id}", params)
    
    # -------------------------
    # Multi-Factor Authentication Operations
    # -------------------------
    
    async def _operation_get_factors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get available MFA factors."""
        result = await self._make_request("GET", "auth_factors", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["factors"] = result["result"].get("data", [])
            else:
                result["factors"] = result["result"]
        
        return result
    
    async def _operation_enroll_factor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enroll MFA factor for user."""
        user_id = params.get("user_id", "")
        factor_data = params.get("factor_data", {})
        
        result = await self._make_request("POST", f"users/{user_id}/otp_devices", params, factor_data, api_version="1")
        
        if result["status"] == "success":
            result["factor_enrolled"] = True
        else:
            result["factor_enrolled"] = False
        
        return result
    
    async def _operation_activate_factor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Activate MFA factor for user."""
        user_id = params.get("user_id", "")
        device_id = params.get("device_id", "")
        
        result = await self._make_request("POST", f"users/{user_id}/otp_devices/{device_id}/activate", params, api_version="1")
        
        if result["status"] == "success":
            result["factor_activated"] = True
        else:
            result["factor_activated"] = False
        
        return result
    
    async def _operation_remove_factor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove MFA factor for user."""
        user_id = params.get("user_id", "")
        device_id = params.get("device_id", "")
        
        return await self._make_request("DELETE", f"users/{user_id}/otp_devices/{device_id}", params, api_version="1")
    
    async def _operation_get_enrolled_factors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get enrolled MFA factors for user."""
        user_id = params.get("user_id", "")
        
        result = await self._make_request("GET", f"users/{user_id}/otp_devices", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["enrolled_factors"] = result["result"].get("data", [])
            else:
                result["enrolled_factors"] = result["result"]
        
        return result
    
    async def _operation_trigger_mfa(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger MFA for user."""
        user_id = params.get("user_id", "")
        device_id = params.get("device_id", "")
        
        result = await self._make_request("POST", f"users/{user_id}/otp_devices/{device_id}/trigger", params, api_version="1")
        
        if result["status"] == "success":
            result["mfa_triggered"] = True
        else:
            result["mfa_triggered"] = False
        
        return result
    
    # -------------------------
    # SAML Operations
    # -------------------------
    
    async def _operation_generate_saml_assertion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SAML assertion."""
        username = params.get("username", "")
        password = params.get("password", "")
        app_id = params.get("app_id", "")
        subdomain = params.get("subdomain", "")
        
        request_data = {
            "username_or_email": username,
            "password": password,
            "app_id": app_id,
            "subdomain": subdomain
        }
        
        result = await self._make_request("POST", "saml_assertion", params, request_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["saml_response"] = result["result"].get("saml_response", "")
                result["assertion"] = result["result"].get("assertion", "")
        
        return result
    
    async def _operation_get_saml_assertion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get SAML assertion."""
        username = params.get("username", "")
        password = params.get("password", "")
        app_id = params.get("app_id", "")
        subdomain = params.get("subdomain", "")
        
        request_data = {
            "username_or_email": username,
            "password": password,
            "app_id": app_id,
            "subdomain": subdomain
        }
        
        result = await self._make_request("POST", "saml_assertion", params, request_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["saml_response"] = result["result"].get("saml_response", "")
                result["assertion"] = result["result"].get("assertion", "")
        
        return result
    
    async def _operation_verify_saml_factor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify SAML factor."""
        app_id = params.get("app_id", "")
        device_id = params.get("device_id", "")
        state_token = params.get("state_token", "")
        otp_token = params.get("otp_token", "")
        
        request_data = {
            "app_id": app_id,
            "device_id": device_id,
            "state_token": state_token,
            "otp_token": otp_token
        }
        
        result = await self._make_request("POST", "saml_assertion/verify_factor", params, request_data, api_version="1")
        
        if result["status"] == "success":
            result["verification_result"] = True
        else:
            result["verification_result"] = False
        
        return result
    
    # -------------------------
    # Event Management Operations
    # -------------------------
    
    async def _operation_get_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get events list."""
        query_params = []
        
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        if params.get("since"):
            query_params.append(f"since={params.get('since')}")
        if params.get("until"):
            query_params.append(f"until={params.get('until')}")
        if params.get("event_type_id"):
            query_params.append(f"event_type_id={params.get('event_type_id')}")
        if params.get("after_cursor"):
            query_params.append(f"after_cursor={params.get('after_cursor')}")
        
        endpoint = "events"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["events"] = result["result"].get("data", [])
                result["pagination"] = result["result"].get("pagination", {})
            else:
                result["events"] = result["result"]
        
        return result
    
    async def _operation_create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom event."""
        event_data = params.get("event_data", {})
        
        result = await self._make_request("POST", "events", params, event_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["event"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["event"] = result["result"]
        
        return result
    
    async def _operation_get_event_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get event types."""
        result = await self._make_request("GET", "events/types", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["event_types"] = result["result"].get("data", [])
            else:
                result["event_types"] = result["result"]
        
        return result
    
    # -------------------------
    # Session Management Operations
    # -------------------------
    
    async def _operation_get_sessions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get active sessions."""
        query_params = []
        
        if params.get("limit"):
            query_params.append(f"limit={params.get('limit')}")
        if params.get("after_cursor"):
            query_params.append(f"after_cursor={params.get('after_cursor')}")
        
        endpoint = "sessions"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        result = await self._make_request("GET", endpoint, params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["sessions"] = result["result"].get("data", [])
                result["pagination"] = result["result"].get("pagination", {})
            else:
                result["sessions"] = result["result"]
        
        return result
    
    async def _operation_destroy_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Destroy a session."""
        session_id = params.get("session_id", "")
        
        return await self._make_request("DELETE", f"sessions/{session_id}", params, api_version="1")
    
    async def _operation_get_session_login_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get session login token."""
        username = params.get("username", "")
        password = params.get("password", "")
        
        request_data = {
            "username_or_email": username,
            "password": password
        }
        
        result = await self._make_request("POST", "login/auth", params, request_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["session_token"] = result["result"].get("session_token", "")
                result["state_token"] = result["result"].get("state_token", "")
        
        return result
    
    # -------------------------
    # Privilege Management Operations
    # -------------------------
    
    async def _operation_get_privileges(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get privileges list."""
        result = await self._make_request("GET", "privileges", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["privileges"] = result["result"].get("data", [])
            else:
                result["privileges"] = result["result"]
        
        return result
    
    async def _operation_assign_privilege(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assign privilege to role."""
        privilege_id = params.get("privilege_id", "")
        role_id = params.get("role_id", "")
        
        request_data = {
            "privilege": {
                "Statement": [{
                    "Effect": "Allow",
                    "Action": ["*"],
                    "Scope": ["*"]
                }]
            }
        }
        
        return await self._make_request("POST", f"privileges/{privilege_id}/roles/{role_id}", params, request_data, api_version="1")
    
    async def _operation_remove_privilege(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove privilege from role."""
        privilege_id = params.get("privilege_id", "")
        role_id = params.get("role_id", "")
        
        return await self._make_request("DELETE", f"privileges/{privilege_id}/roles/{role_id}", params, api_version="1")
    
    async def _operation_get_assigned_privileges(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get assigned privileges."""
        result = await self._make_request("GET", "privileges/roles", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["privileges"] = result["result"].get("data", [])
            else:
                result["privileges"] = result["result"]
        
        return result
    
    # -------------------------
    # Configuration Operations
    # -------------------------
    
    async def _operation_get_connectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get connectors list."""
        result = await self._make_request("GET", "connectors", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["connectors"] = result["result"].get("data", [])
            else:
                result["connectors"] = result["result"]
        
        return result
    
    async def _operation_get_mappings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get mappings list."""
        result = await self._make_request("GET", "mappings", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["mappings"] = result["result"].get("data", [])
            else:
                result["mappings"] = result["result"]
        
        return result
    
    async def _operation_create_mapping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new mapping."""
        mapping_data = params.get("mapping_data", {})
        
        result = await self._make_request("POST", "mappings", params, mapping_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["mapping"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["mapping"] = result["result"]
        
        return result
    
    async def _operation_update_mapping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing mapping."""
        mapping_id = params.get("mapping_id", "")
        mapping_data = params.get("mapping_data", {})
        
        result = await self._make_request("PUT", f"mappings/{mapping_id}", params, mapping_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["mapping"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["mapping"] = result["result"]
        
        return result
    
    async def _operation_delete_mapping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a mapping."""
        mapping_id = params.get("mapping_id", "")
        
        return await self._make_request("DELETE", f"mappings/{mapping_id}", params, api_version="1")
    
    # -------------------------
    # Invitation Operations
    # -------------------------
    
    async def _operation_invite_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Invite a user."""
        email = params.get("email", "")
        
        request_data = {
            "email": email
        }
        
        return await self._make_request("POST", "invitations", params, request_data, api_version="1")
    
    async def _operation_send_invite_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send invite link to user."""
        email = params.get("email", "")
        
        request_data = {
            "email": email
        }
        
        return await self._make_request("POST", "invitations/send", params, request_data, api_version="1")
    
    async def _operation_generate_invite_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate invite link for user."""
        email = params.get("email", "")
        
        request_data = {
            "email": email
        }
        
        result = await self._make_request("POST", "invitations/get_link", params, request_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["invite_link"] = result["result"].get("link", "")
        
        return result
    
    # -------------------------
    # Brand Management Operations
    # -------------------------
    
    async def _operation_get_brands(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get brands list."""
        result = await self._make_request("GET", "branding", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["brands"] = result["result"].get("data", [])
            else:
                result["brands"] = result["result"]
        
        return result
    
    async def _operation_get_brand(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific brand."""
        brand_id = params.get("brand_id", "")
        
        result = await self._make_request("GET", f"branding/{brand_id}", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["brand"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["brand"] = result["result"]
        
        return result
    
    async def _operation_update_brand(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update brand."""
        brand_id = params.get("brand_id", "")
        brand_data = params.get("brand_data", {})
        
        result = await self._make_request("PUT", f"branding/{brand_id}", params, brand_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["brand"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["brand"] = result["result"]
        
        return result
    
    # -------------------------
    # Smart Hook Operations
    # -------------------------
    
    async def _operation_get_smart_hooks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get smart hooks list."""
        result = await self._make_request("GET", "hooks", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["smart_hooks"] = result["result"].get("data", [])
            else:
                result["smart_hooks"] = result["result"]
        
        return result
    
    async def _operation_create_smart_hook(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create smart hook."""
        hook_data = params.get("hook_data", {})
        
        result = await self._make_request("POST", "hooks", params, hook_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["smart_hook"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["smart_hook"] = result["result"]
        
        return result
    
    async def _operation_update_smart_hook(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update smart hook."""
        hook_id = params.get("hook_id", "")
        hook_data = params.get("hook_data", {})
        
        result = await self._make_request("PUT", f"hooks/{hook_id}", params, hook_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["smart_hook"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["smart_hook"] = result["result"]
        
        return result
    
    async def _operation_delete_smart_hook(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete smart hook."""
        hook_id = params.get("hook_id", "")
        
        return await self._make_request("DELETE", f"hooks/{hook_id}", params, api_version="1")
    
    # -------------------------
    # Risk Management Operations
    # -------------------------
    
    async def _operation_get_risk_rules(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get risk rules list."""
        result = await self._make_request("GET", "risk/rules", params, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["risk_rules"] = result["result"].get("data", [])
            else:
                result["risk_rules"] = result["result"]
        
        return result
    
    async def _operation_create_risk_rule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create risk rule."""
        rule_data = params.get("rule_data", {})
        
        result = await self._make_request("POST", "risk/rules", params, rule_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["risk_rule"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["risk_rule"] = result["result"]
        
        return result
    
    async def _operation_update_risk_rule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update risk rule."""
        rule_id = params.get("rule_id", "")
        rule_data = params.get("rule_data", {})
        
        result = await self._make_request("PUT", f"risk/rules/{rule_id}", params, rule_data, api_version="1")
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], dict):
                result["risk_rule"] = result["result"].get("data", [{}])[0] if result["result"].get("data") else result["result"]
            else:
                result["risk_rule"] = result["result"]
        
        return result
    
    async def _operation_delete_risk_rule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete risk rule."""
        rule_id = params.get("rule_id", "")
        
        return await self._make_request("DELETE", f"risk/rules/{rule_id}", params, api_version="1")


# Utility functions for common OneLogin operations
class OneLoginHelpers:
    """Helper functions for common OneLogin operations."""
    
    @staticmethod
    def create_user_data(email: str, firstname: str, lastname: str, username: str = "", 
                        **kwargs) -> Dict[str, Any]:
        """Create user data structure."""
        user_data = {
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
            "username": username or email
        }
        
        # Add optional fields
        optional_fields = [
            "phone", "title", "department", "company", "comment", "group_id",
            "role_ids", "password", "password_confirmation", "invalid_login_attempts",
            "locked_until", "activated_at", "last_login", "invitation_sent_at",
            "directory_id", "distinguished_name", "external_id", "salt", "userprincipalname",
            "manager_ad_id", "manager_user_id", "samaccountname", "member_of", "state"
        ]
        
        for field in optional_fields:
            if field in kwargs:
                user_data[field] = kwargs[field]
        
        return user_data
    
    @staticmethod
    def create_role_data(name: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create role data structure."""
        role_data = {
            "name": name,
            "description": description
        }
        
        # Add optional fields
        if "apps" in kwargs:
            role_data["apps"] = kwargs["apps"]
        if "users" in kwargs:
            role_data["users"] = kwargs["users"]
        
        return role_data
    
    @staticmethod
    def create_group_data(name: str, reference: str = "", **kwargs) -> Dict[str, Any]:
        """Create group data structure."""
        group_data = {
            "name": name,
            "reference": reference
        }
        
        # Add optional fields
        for field in ["description", "notes"]:
            if field in kwargs:
                group_data[field] = kwargs[field]
        
        return group_data
    
    @staticmethod
    def create_app_data(name: str, connector_id: int, description: str = "", 
                       **kwargs) -> Dict[str, Any]:
        """Create application data structure."""
        app_data = {
            "name": name,
            "connector_id": connector_id,
            "description": description
        }
        
        # Add optional fields
        optional_fields = [
            "visible", "allow_assumed_signin", "provisioning", "parameters",
            "brand_id", "notes", "policy_id", "sso", "configuration"
        ]
        
        for field in optional_fields:
            if field in kwargs:
                app_data[field] = kwargs[field]
        
        return app_data
    
    @staticmethod
    def create_factor_data(type_display_name: str, **kwargs) -> Dict[str, Any]:
        """Create factor data structure for MFA enrollment."""
        factor_data = {
            "type_display_name": type_display_name
        }
        
        # Add optional fields based on factor type
        if "phone_number" in kwargs:
            factor_data["phone_number"] = kwargs["phone_number"]
        if "display_name" in kwargs:
            factor_data["display_name"] = kwargs["display_name"]
        
        return factor_data
    
    @staticmethod
    def create_event_data(event_type_id: int, account_id: int, user_id: int = None, 
                         **kwargs) -> Dict[str, Any]:
        """Create event data structure."""
        event_data = {
            "event_type_id": event_type_id,
            "account_id": account_id
        }
        
        if user_id:
            event_data["user_id"] = user_id
        
        # Add optional fields
        optional_fields = [
            "app_id", "group_id", "role_id", "otp_device_id", "policy_id",
            "actor_system", "actor_user_id", "actor_user_name", "assuming_acting_user_id",
            "directory_sync_run_id", "directory_id", "resolution", "client_id",
            "resource", "operation_name", "error_description"
        ]
        
        for field in optional_fields:
            if field in kwargs:
                event_data[field] = kwargs[field]
        
        return event_data
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Format datetime for OneLogin API."""
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    @staticmethod
    def parse_datetime(dt_string: str) -> datetime:
        """Parse datetime from OneLogin API response."""
        try:
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except ValueError:
            # Try alternative formats
            for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"]:
                try:
                    return datetime.strptime(dt_string, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Unable to parse datetime string: {dt_string}")
    
    @staticmethod
    def build_search_query(field: str, value: str, operator: str = "eq") -> str:
        """Build search query for OneLogin API."""
        operators_map = {
            "eq": "=",
            "ne": "!=",
            "gt": ">",
            "ge": ">=",
            "lt": "<",
            "le": "<=",
            "contains": "~",
            "startswith": "^",
            "endswith": "$"
        }
        
        op = operators_map.get(operator, "=")
        return f"{field}{op}{value}"
    
    @staticmethod
    def extract_pagination_info(result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract pagination information from API response."""
        pagination = {}
        
        if "pagination" in result:
            pag_data = result["pagination"]
            pagination = {
                "before_cursor": pag_data.get("before_cursor"),
                "after_cursor": pag_data.get("after_cursor"),
                "previous_link": pag_data.get("previous_link"),
                "next_link": pag_data.get("next_link")
            }
        
        return pagination
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """Generate a random password."""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password


# Main test function for OneLogin Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== OneLogin Node Test Suite ===")
        
        # Get OneLogin credentials from environment or user input
        client_id = os.environ.get("ONELOGIN_CLIENT_ID")
        client_secret = os.environ.get("ONELOGIN_CLIENT_SECRET")
        onelogin_url = os.environ.get("ONELOGIN_URL", "https://api.us.onelogin.com")
        
        if not client_id:
            print("OneLogin client ID not found in environment variables")
            print("Please set ONELOGIN_CLIENT_ID")
            client_id = input("Enter OneLogin client ID: ")
        
        if not client_secret:
            print("OneLogin client secret not found in environment variables")
            print("Please set ONELOGIN_CLIENT_SECRET")
            client_secret = input("Enter OneLogin client secret: ")
        
        if not client_id or not client_secret:
            print("OneLogin credentials are required for testing")
            return
        
        # Create an instance of the OneLogin Node
        node = OneLoginNode()
        
        # Test cases
        test_cases = [
            {
                "name": "Generate Access Token",
                "params": {
                    "operation": OneLoginOperation.GENERATE_ACCESS_TOKEN,
                    "onelogin_url": onelogin_url,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials"
                },
                "expected_status": "success"
            }
        ]
        
        access_token = None
        
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
                    if result.get("access_token"):
                        access_token = result["access_token"]
                        print(f"Access token obtained: {access_token[:20]}...")
                        print(f"Token type: {result.get('token_type', 'N/A')}")
                        print(f"Expires in: {result.get('expires_in', 'N/A')} seconds")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
                # Add a delay between tests
                await asyncio.sleep(1.0)
                
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # If we have an access token, test additional operations
        if access_token:
            additional_tests = [
                {
                    "name": "Get Users",
                    "params": {
                        "operation": OneLoginOperation.GET_USERS,
                        "onelogin_url": onelogin_url,
                        "access_token": access_token,
                        "limit": 10
                    },
                    "expected_status": "success"
                },
                {
                    "name": "Get Roles",
                    "params": {
                        "operation": OneLoginOperation.GET_ROLES,
                        "onelogin_url": onelogin_url,
                        "access_token": access_token,
                        "limit": 10
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
                        if result.get("users"):
                            print(f"Found {len(result.get('users', []))} users")
                        if result.get("roles"):
                            print(f"Found {len(result.get('roles', []))} roles")
                        if result.get("pagination"):
                            print(f"Pagination info: {result.get('pagination')}")
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
    registry.register("onelogin", OneLoginNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register OneLoginNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")