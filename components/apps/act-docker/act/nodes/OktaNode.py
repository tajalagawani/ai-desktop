"""
Okta Node - Comprehensive integration with Okta Management API
Provides access to all Okta API operations including user management, application management, groups, roles, system logs, and authentication.
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

class OktaOperation:
    """Operations available on Okta Management API."""
    
    # Authentication
    GET_ACCESS_TOKEN = "get_access_token"
    
    # User Management
    GET_USERS = "get_users"
    GET_USER = "get_user"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    ACTIVATE_USER = "activate_user"
    DEACTIVATE_USER = "deactivate_user"
    SUSPEND_USER = "suspend_user"
    UNSUSPEND_USER = "unsuspend_user"
    RESET_PASSWORD = "reset_password"
    EXPIRE_PASSWORD = "expire_password"
    UNLOCK_USER = "unlock_user"
    
    # User Factors (MFA)
    GET_USER_FACTORS = "get_user_factors"
    ENROLL_FACTOR = "enroll_factor"
    ACTIVATE_FACTOR = "activate_factor"
    VERIFY_FACTOR = "verify_factor"
    DELETE_FACTOR = "delete_factor"
    LIST_FACTORS = "list_factors"
    
    # Application Management
    GET_APPLICATIONS = "get_applications"
    GET_APPLICATION = "get_application"
    CREATE_APPLICATION = "create_application"
    UPDATE_APPLICATION = "update_application"
    DELETE_APPLICATION = "delete_application"
    ACTIVATE_APPLICATION = "activate_application"
    DEACTIVATE_APPLICATION = "deactivate_application"
    
    # Application Users
    GET_APPLICATION_USERS = "get_application_users"
    ASSIGN_USER_TO_APPLICATION = "assign_user_to_application"
    UNASSIGN_USER_FROM_APPLICATION = "unassign_user_from_application"
    
    # Application Groups
    GET_APPLICATION_GROUPS = "get_application_groups"
    ASSIGN_GROUP_TO_APPLICATION = "assign_group_to_application"
    UNASSIGN_GROUP_FROM_APPLICATION = "unassign_group_from_application"
    
    # Group Management
    GET_GROUPS = "get_groups"
    GET_GROUP = "get_group"
    CREATE_GROUP = "create_group"
    UPDATE_GROUP = "update_group"
    DELETE_GROUP = "delete_group"
    
    # Group Members
    GET_GROUP_MEMBERS = "get_group_members"
    ADD_USER_TO_GROUP = "add_user_to_group"
    REMOVE_USER_FROM_GROUP = "remove_user_from_group"
    
    # Roles Management
    GET_ROLES = "get_roles"
    GET_ROLE = "get_role"
    CREATE_ROLE = "create_role"
    UPDATE_ROLE = "update_role"
    DELETE_ROLE = "delete_role"
    ASSIGN_ROLE_TO_USER = "assign_role_to_user"
    UNASSIGN_ROLE_FROM_USER = "unassign_role_from_user"
    GET_USER_ROLES = "get_user_roles"
    
    # Authorization Servers
    GET_AUTHORIZATION_SERVERS = "get_authorization_servers"
    GET_AUTHORIZATION_SERVER = "get_authorization_server"
    CREATE_AUTHORIZATION_SERVER = "create_authorization_server"
    UPDATE_AUTHORIZATION_SERVER = "update_authorization_server"
    DELETE_AUTHORIZATION_SERVER = "delete_authorization_server"
    ACTIVATE_AUTHORIZATION_SERVER = "activate_authorization_server"
    DEACTIVATE_AUTHORIZATION_SERVER = "deactivate_authorization_server"
    
    # Scopes Management
    GET_SCOPES = "get_scopes"
    GET_SCOPE = "get_scope"
    CREATE_SCOPE = "create_scope"
    UPDATE_SCOPE = "update_scope"
    DELETE_SCOPE = "delete_scope"
    
    # Claims Management
    GET_CLAIMS = "get_claims"
    GET_CLAIM = "get_claim"
    CREATE_CLAIM = "create_claim"
    UPDATE_CLAIM = "update_claim"
    DELETE_CLAIM = "delete_claim"
    
    # Policies Management
    GET_POLICIES = "get_policies"
    GET_POLICY = "get_policy"
    CREATE_POLICY = "create_policy"
    UPDATE_POLICY = "update_policy"
    DELETE_POLICY = "delete_policy"
    ACTIVATE_POLICY = "activate_policy"
    DEACTIVATE_POLICY = "deactivate_policy"
    
    # Policy Rules
    GET_POLICY_RULES = "get_policy_rules"
    GET_POLICY_RULE = "get_policy_rule"
    CREATE_POLICY_RULE = "create_policy_rule"
    UPDATE_POLICY_RULE = "update_policy_rule"
    DELETE_POLICY_RULE = "delete_policy_rule"
    ACTIVATE_POLICY_RULE = "activate_policy_rule"
    DEACTIVATE_POLICY_RULE = "deactivate_policy_rule"
    
    # Zones Management
    GET_ZONES = "get_zones"
    GET_ZONE = "get_zone"
    CREATE_ZONE = "create_zone"
    UPDATE_ZONE = "update_zone"
    DELETE_ZONE = "delete_zone"
    ACTIVATE_ZONE = "activate_zone"
    DEACTIVATE_ZONE = "deactivate_zone"
    
    # System Logs
    GET_SYSTEM_LOGS = "get_system_logs"
    
    # Sessions Management
    GET_USER_SESSIONS = "get_user_sessions"
    DELETE_USER_SESSION = "delete_user_session"
    DELETE_USER_SESSIONS = "delete_user_sessions"
    
    # Identity Providers
    GET_IDENTITY_PROVIDERS = "get_identity_providers"
    GET_IDENTITY_PROVIDER = "get_identity_provider"
    CREATE_IDENTITY_PROVIDER = "create_identity_provider"
    UPDATE_IDENTITY_PROVIDER = "update_identity_provider"
    DELETE_IDENTITY_PROVIDER = "delete_identity_provider"
    ACTIVATE_IDENTITY_PROVIDER = "activate_identity_provider"
    DEACTIVATE_IDENTITY_PROVIDER = "deactivate_identity_provider"
    
    # Realms Management
    GET_REALMS = "get_realms"
    GET_REALM = "get_realm"
    CREATE_REALM = "create_realm"
    UPDATE_REALM = "update_realm"
    DELETE_REALM = "delete_realm"

class OktaNode(BaseNode):
    """
    Node for interacting with Okta Management API.
    Provides comprehensive functionality for identity and access management, user authentication, and organizational administration.
    """
    
    SANDBOX_BASE_URL = "https://dev-{org}.okta.com"
    LIVE_BASE_URL = "https://{org}.okta.com"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        self.access_token = None
        self.token_expires_at = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Okta node."""
        return NodeSchema(
            node_type="okta",
            version="1.0.0",
            description="Comprehensive integration with Okta Management API for identity and access management, user authentication, and organizational administration",
            parameters=[
                # Authentication
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Okta API",
                    required=True,
                    enum=[
                        # Authentication
                        OktaOperation.GET_ACCESS_TOKEN,
                        
                        # User Management
                        OktaOperation.GET_USERS,
                        OktaOperation.GET_USER,
                        OktaOperation.CREATE_USER,
                        OktaOperation.UPDATE_USER,
                        OktaOperation.DELETE_USER,
                        OktaOperation.ACTIVATE_USER,
                        OktaOperation.DEACTIVATE_USER,
                        OktaOperation.SUSPEND_USER,
                        OktaOperation.UNSUSPEND_USER,
                        OktaOperation.RESET_PASSWORD,
                        OktaOperation.EXPIRE_PASSWORD,
                        OktaOperation.UNLOCK_USER,
                        
                        # User Factors (MFA)
                        OktaOperation.GET_USER_FACTORS,
                        OktaOperation.ENROLL_FACTOR,
                        OktaOperation.ACTIVATE_FACTOR,
                        OktaOperation.VERIFY_FACTOR,
                        OktaOperation.DELETE_FACTOR,
                        OktaOperation.LIST_FACTORS,
                        
                        # Application Management
                        OktaOperation.GET_APPLICATIONS,
                        OktaOperation.GET_APPLICATION,
                        OktaOperation.CREATE_APPLICATION,
                        OktaOperation.UPDATE_APPLICATION,
                        OktaOperation.DELETE_APPLICATION,
                        OktaOperation.ACTIVATE_APPLICATION,
                        OktaOperation.DEACTIVATE_APPLICATION,
                        
                        # Application Users
                        OktaOperation.GET_APPLICATION_USERS,
                        OktaOperation.ASSIGN_USER_TO_APPLICATION,
                        OktaOperation.UNASSIGN_USER_FROM_APPLICATION,
                        
                        # Application Groups
                        OktaOperation.GET_APPLICATION_GROUPS,
                        OktaOperation.ASSIGN_GROUP_TO_APPLICATION,
                        OktaOperation.UNASSIGN_GROUP_FROM_APPLICATION,
                        
                        # Group Management
                        OktaOperation.GET_GROUPS,
                        OktaOperation.GET_GROUP,
                        OktaOperation.CREATE_GROUP,
                        OktaOperation.UPDATE_GROUP,
                        OktaOperation.DELETE_GROUP,
                        
                        # Group Members
                        OktaOperation.GET_GROUP_MEMBERS,
                        OktaOperation.ADD_USER_TO_GROUP,
                        OktaOperation.REMOVE_USER_FROM_GROUP,
                        
                        # Roles Management
                        OktaOperation.GET_ROLES,
                        OktaOperation.GET_ROLE,
                        OktaOperation.CREATE_ROLE,
                        OktaOperation.UPDATE_ROLE,
                        OktaOperation.DELETE_ROLE,
                        OktaOperation.ASSIGN_ROLE_TO_USER,
                        OktaOperation.UNASSIGN_ROLE_FROM_USER,
                        OktaOperation.GET_USER_ROLES,
                        
                        # Authorization Servers
                        OktaOperation.GET_AUTHORIZATION_SERVERS,
                        OktaOperation.GET_AUTHORIZATION_SERVER,
                        OktaOperation.CREATE_AUTHORIZATION_SERVER,
                        OktaOperation.UPDATE_AUTHORIZATION_SERVER,
                        OktaOperation.DELETE_AUTHORIZATION_SERVER,
                        OktaOperation.ACTIVATE_AUTHORIZATION_SERVER,
                        OktaOperation.DEACTIVATE_AUTHORIZATION_SERVER,
                        
                        # Scopes Management
                        OktaOperation.GET_SCOPES,
                        OktaOperation.GET_SCOPE,
                        OktaOperation.CREATE_SCOPE,
                        OktaOperation.UPDATE_SCOPE,
                        OktaOperation.DELETE_SCOPE,
                        
                        # Claims Management
                        OktaOperation.GET_CLAIMS,
                        OktaOperation.GET_CLAIM,
                        OktaOperation.CREATE_CLAIM,
                        OktaOperation.UPDATE_CLAIM,
                        OktaOperation.DELETE_CLAIM,
                        
                        # Policies Management
                        OktaOperation.GET_POLICIES,
                        OktaOperation.GET_POLICY,
                        OktaOperation.CREATE_POLICY,
                        OktaOperation.UPDATE_POLICY,
                        OktaOperation.DELETE_POLICY,
                        OktaOperation.ACTIVATE_POLICY,
                        OktaOperation.DEACTIVATE_POLICY,
                        
                        # Policy Rules
                        OktaOperation.GET_POLICY_RULES,
                        OktaOperation.GET_POLICY_RULE,
                        OktaOperation.CREATE_POLICY_RULE,
                        OktaOperation.UPDATE_POLICY_RULE,
                        OktaOperation.DELETE_POLICY_RULE,
                        OktaOperation.ACTIVATE_POLICY_RULE,
                        OktaOperation.DEACTIVATE_POLICY_RULE,
                        
                        # Zones Management
                        OktaOperation.GET_ZONES,
                        OktaOperation.GET_ZONE,
                        OktaOperation.CREATE_ZONE,
                        OktaOperation.UPDATE_ZONE,
                        OktaOperation.DELETE_ZONE,
                        OktaOperation.ACTIVATE_ZONE,
                        OktaOperation.DEACTIVATE_ZONE,
                        
                        # System Logs
                        OktaOperation.GET_SYSTEM_LOGS,
                        
                        # Sessions Management
                        OktaOperation.GET_USER_SESSIONS,
                        OktaOperation.DELETE_USER_SESSION,
                        OktaOperation.DELETE_USER_SESSIONS,
                        
                        # Identity Providers
                        OktaOperation.GET_IDENTITY_PROVIDERS,
                        OktaOperation.GET_IDENTITY_PROVIDER,
                        OktaOperation.CREATE_IDENTITY_PROVIDER,
                        OktaOperation.UPDATE_IDENTITY_PROVIDER,
                        OktaOperation.DELETE_IDENTITY_PROVIDER,
                        OktaOperation.ACTIVATE_IDENTITY_PROVIDER,
                        OktaOperation.DEACTIVATE_IDENTITY_PROVIDER,
                        
                        # Realms Management
                        OktaOperation.GET_REALMS,
                        OktaOperation.GET_REALM,
                        OktaOperation.CREATE_REALM,
                        OktaOperation.UPDATE_REALM,
                        OktaOperation.DELETE_REALM
                    ]
                ),
                NodeParameter(
                    name="org_url",
                    type=NodeParameterType.STRING,
                    description="Okta organization URL (e.g., https://dev-123456.okta.com)",
                    required=True
                ),
                NodeParameter(
                    name="api_token",
                    type=NodeParameterType.SECRET,
                    description="Okta API token for authentication",
                    required=False
                ),
                NodeParameter(
                    name="client_id",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 Client ID for authentication",
                    required=False
                ),
                NodeParameter(
                    name="client_secret",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 Client Secret for authentication",
                    required=False
                ),
                NodeParameter(
                    name="private_key",
                    type=NodeParameterType.SECRET,
                    description="Private key for JWT authentication",
                    required=False
                ),
                NodeParameter(
                    name="scopes",
                    type=NodeParameterType.ARRAY,
                    description="OAuth 2.0 scopes for token request",
                    required=False,
                    default=["okta.users.read", "okta.apps.read"]
                ),
                
                # Common parameters
                NodeParameter(
                    name="user_id",
                    type=NodeParameterType.STRING,
                    description="User ID for user operations",
                    required=False
                ),
                NodeParameter(
                    name="application_id",
                    type=NodeParameterType.STRING,
                    description="Application ID for application operations",
                    required=False
                ),
                NodeParameter(
                    name="group_id",
                    type=NodeParameterType.STRING,
                    description="Group ID for group operations",
                    required=False
                ),
                NodeParameter(
                    name="role_id",
                    type=NodeParameterType.STRING,
                    description="Role ID for role operations",
                    required=False
                ),
                NodeParameter(
                    name="factor_id",
                    type=NodeParameterType.STRING,
                    description="Factor ID for factor operations",
                    required=False
                ),
                NodeParameter(
                    name="authorization_server_id",
                    type=NodeParameterType.STRING,
                    description="Authorization server ID for authorization server operations",
                    required=False
                ),
                NodeParameter(
                    name="scope_id",
                    type=NodeParameterType.STRING,
                    description="Scope ID for scope operations",
                    required=False
                ),
                NodeParameter(
                    name="claim_id",
                    type=NodeParameterType.STRING,
                    description="Claim ID for claim operations",
                    required=False
                ),
                NodeParameter(
                    name="policy_id",
                    type=NodeParameterType.STRING,
                    description="Policy ID for policy operations",
                    required=False
                ),
                NodeParameter(
                    name="policy_rule_id",
                    type=NodeParameterType.STRING,
                    description="Policy rule ID for policy rule operations",
                    required=False
                ),
                NodeParameter(
                    name="zone_id",
                    type=NodeParameterType.STRING,
                    description="Zone ID for zone operations",
                    required=False
                ),
                NodeParameter(
                    name="session_id",
                    type=NodeParameterType.STRING,
                    description="Session ID for session operations",
                    required=False
                ),
                NodeParameter(
                    name="identity_provider_id",
                    type=NodeParameterType.STRING,
                    description="Identity provider ID for identity provider operations",
                    required=False
                ),
                NodeParameter(
                    name="realm_id",
                    type=NodeParameterType.STRING,
                    description="Realm ID for realm operations",
                    required=False
                ),
                
                # Request body parameters
                NodeParameter(
                    name="request_body",
                    type=NodeParameterType.OBJECT,
                    description="Request body for create/update operations",
                    required=False
                ),
                NodeParameter(
                    name="profile",
                    type=NodeParameterType.OBJECT,
                    description="User profile object",
                    required=False
                ),
                NodeParameter(
                    name="credentials",
                    type=NodeParameterType.OBJECT,
                    description="User credentials object",
                    required=False
                ),
                NodeParameter(
                    name="activate",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to activate user upon creation",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="provider",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to create user in specific provider",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="next_login",
                    type=NodeParameterType.STRING,
                    description="Set user password behavior on next login",
                    required=False,
                    enum=["changePassword", "setPassword"]
                ),
                
                # Search and filter parameters
                NodeParameter(
                    name="q",
                    type=NodeParameterType.STRING,
                    description="Search query using SCIM filter expressions",
                    required=False
                ),
                NodeParameter(
                    name="filter",
                    type=NodeParameterType.STRING,
                    description="SCIM filter expression",
                    required=False
                ),
                NodeParameter(
                    name="search",
                    type=NodeParameterType.STRING,
                    description="Search term for full-text search",
                    required=False
                ),
                NodeParameter(
                    name="sortBy",
                    type=NodeParameterType.STRING,
                    description="Property to sort by",
                    required=False
                ),
                NodeParameter(
                    name="sortOrder",
                    type=NodeParameterType.STRING,
                    description="Sort order",
                    required=False,
                    enum=["asc", "desc"],
                    default="asc"
                ),
                
                # Pagination parameters
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Number of items per page",
                    required=False,
                    default=20,
                    min_value=1,
                    max_value=200
                ),
                NodeParameter(
                    name="after",
                    type=NodeParameterType.STRING,
                    description="Cursor for pagination (after)",
                    required=False
                ),
                NodeParameter(
                    name="before",
                    type=NodeParameterType.STRING,
                    description="Cursor for pagination (before)",
                    required=False
                ),
                
                # System Log parameters
                NodeParameter(
                    name="since",
                    type=NodeParameterType.STRING,
                    description="Start date for log filtering (ISO 8601)",
                    required=False
                ),
                NodeParameter(
                    name="until",
                    type=NodeParameterType.STRING,
                    description="End date for log filtering (ISO 8601)",
                    required=False
                ),
                
                # Factor parameters
                NodeParameter(
                    name="factor_type",
                    type=NodeParameterType.STRING,
                    description="Type of factor",
                    required=False,
                    enum=["sms", "call", "token:software:totp", "token:hardware", "push", "email", "question", "web", "token"]
                ),
                NodeParameter(
                    name="provider",
                    type=NodeParameterType.STRING,
                    description="Factor provider",
                    required=False,
                    enum=["OKTA", "RSA", "SYMANTEC", "GOOGLE", "DUO", "YUBICO", "FIDO"]
                ),
                NodeParameter(
                    name="pass_code",
                    type=NodeParameterType.STRING,
                    description="Pass code for factor verification",
                    required=False
                ),
                
                # Additional parameters
                NodeParameter(
                    name="expand",
                    type=NodeParameterType.STRING,
                    description="Comma-separated list of objects to expand",
                    required=False
                ),
                NodeParameter(
                    name="send_email",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to send email notification",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="temp_password",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to generate temporary password",
                    required=False,
                    default=False
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "id": NodeParameterType.STRING,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT,
                "access_token": NodeParameterType.STRING,
                "token_type": NodeParameterType.STRING,
                "expires_in": NodeParameterType.NUMBER,
                "users": NodeParameterType.ARRAY,
                "user": NodeParameterType.OBJECT,
                "applications": NodeParameterType.ARRAY,
                "application": NodeParameterType.OBJECT,
                "groups": NodeParameterType.ARRAY,
                "group": NodeParameterType.OBJECT,
                "roles": NodeParameterType.ARRAY,
                "role": NodeParameterType.OBJECT,
                "factors": NodeParameterType.ARRAY,
                "factor": NodeParameterType.OBJECT,
                "authorization_servers": NodeParameterType.ARRAY,
                "authorization_server": NodeParameterType.OBJECT,
                "scopes": NodeParameterType.ARRAY,
                "scope": NodeParameterType.OBJECT,
                "claims": NodeParameterType.ARRAY,
                "claim": NodeParameterType.OBJECT,
                "policies": NodeParameterType.ARRAY,
                "policy": NodeParameterType.OBJECT,
                "policy_rules": NodeParameterType.ARRAY,
                "policy_rule": NodeParameterType.OBJECT,
                "zones": NodeParameterType.ARRAY,
                "zone": NodeParameterType.OBJECT,
                "logs": NodeParameterType.ARRAY,
                "log": NodeParameterType.OBJECT,
                "sessions": NodeParameterType.ARRAY,
                "session": NodeParameterType.OBJECT,
                "identity_providers": NodeParameterType.ARRAY,
                "identity_provider": NodeParameterType.OBJECT,
                "realms": NodeParameterType.ARRAY,
                "realm": NodeParameterType.OBJECT,
                "pagination": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["okta", "identity", "authentication", "authorization", "security", "api", "integration"],
            author="System",
            documentation_url="https://developer.okta.com/docs/reference/"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for organization URL
        if not params.get("org_url"):
            raise NodeValidationError("Okta organization URL is required")
            
        # Check for authentication credentials
        if not params.get("api_token") and not (params.get("client_id") and params.get("client_secret")):
            raise NodeValidationError("Either API token or OAuth 2.0 credentials (client_id and client_secret) are required")
            
        # Validate based on operation
        if operation in [OktaOperation.GET_USER, OktaOperation.UPDATE_USER, OktaOperation.DELETE_USER,
                        OktaOperation.ACTIVATE_USER, OktaOperation.DEACTIVATE_USER, OktaOperation.SUSPEND_USER,
                        OktaOperation.UNSUSPEND_USER, OktaOperation.RESET_PASSWORD, OktaOperation.EXPIRE_PASSWORD,
                        OktaOperation.UNLOCK_USER, OktaOperation.GET_USER_FACTORS, OktaOperation.GET_USER_ROLES,
                        OktaOperation.GET_USER_SESSIONS, OktaOperation.DELETE_USER_SESSIONS]:
            if not params.get("user_id"):
                raise NodeValidationError("User ID is required for user operations")
                
        elif operation in [OktaOperation.GET_APPLICATION, OktaOperation.UPDATE_APPLICATION, 
                          OktaOperation.DELETE_APPLICATION, OktaOperation.ACTIVATE_APPLICATION,
                          OktaOperation.DEACTIVATE_APPLICATION, OktaOperation.GET_APPLICATION_USERS,
                          OktaOperation.GET_APPLICATION_GROUPS]:
            if not params.get("application_id"):
                raise NodeValidationError("Application ID is required for application operations")
                
        elif operation in [OktaOperation.GET_GROUP, OktaOperation.UPDATE_GROUP, OktaOperation.DELETE_GROUP,
                          OktaOperation.GET_GROUP_MEMBERS]:
            if not params.get("group_id"):
                raise NodeValidationError("Group ID is required for group operations")
                
        elif operation in [OktaOperation.GET_ROLE, OktaOperation.UPDATE_ROLE, OktaOperation.DELETE_ROLE]:
            if not params.get("role_id"):
                raise NodeValidationError("Role ID is required for role operations")
                
        elif operation in [OktaOperation.ACTIVATE_FACTOR, OktaOperation.VERIFY_FACTOR, OktaOperation.DELETE_FACTOR]:
            if not params.get("user_id"):
                raise NodeValidationError("User ID is required for factor operations")
            if not params.get("factor_id"):
                raise NodeValidationError("Factor ID is required for factor operations")
                
        elif operation in [OktaOperation.GET_AUTHORIZATION_SERVER, OktaOperation.UPDATE_AUTHORIZATION_SERVER,
                          OktaOperation.DELETE_AUTHORIZATION_SERVER, OktaOperation.ACTIVATE_AUTHORIZATION_SERVER,
                          OktaOperation.DEACTIVATE_AUTHORIZATION_SERVER, OktaOperation.GET_SCOPES,
                          OktaOperation.GET_CLAIMS]:
            if not params.get("authorization_server_id"):
                raise NodeValidationError("Authorization server ID is required for authorization server operations")
                
        elif operation in [OktaOperation.GET_SCOPE, OktaOperation.UPDATE_SCOPE, OktaOperation.DELETE_SCOPE]:
            if not params.get("authorization_server_id"):
                raise NodeValidationError("Authorization server ID is required for scope operations")
            if not params.get("scope_id"):
                raise NodeValidationError("Scope ID is required for scope operations")
                
        elif operation in [OktaOperation.GET_CLAIM, OktaOperation.UPDATE_CLAIM, OktaOperation.DELETE_CLAIM]:
            if not params.get("authorization_server_id"):
                raise NodeValidationError("Authorization server ID is required for claim operations")
            if not params.get("claim_id"):
                raise NodeValidationError("Claim ID is required for claim operations")
                
        elif operation in [OktaOperation.GET_POLICY, OktaOperation.UPDATE_POLICY, OktaOperation.DELETE_POLICY,
                          OktaOperation.ACTIVATE_POLICY, OktaOperation.DEACTIVATE_POLICY,
                          OktaOperation.GET_POLICY_RULES]:
            if not params.get("policy_id"):
                raise NodeValidationError("Policy ID is required for policy operations")
                
        elif operation in [OktaOperation.GET_POLICY_RULE, OktaOperation.UPDATE_POLICY_RULE,
                          OktaOperation.DELETE_POLICY_RULE, OktaOperation.ACTIVATE_POLICY_RULE,
                          OktaOperation.DEACTIVATE_POLICY_RULE]:
            if not params.get("policy_id"):
                raise NodeValidationError("Policy ID is required for policy rule operations")
            if not params.get("policy_rule_id"):
                raise NodeValidationError("Policy rule ID is required for policy rule operations")
                
        elif operation in [OktaOperation.GET_ZONE, OktaOperation.UPDATE_ZONE, OktaOperation.DELETE_ZONE,
                          OktaOperation.ACTIVATE_ZONE, OktaOperation.DEACTIVATE_ZONE]:
            if not params.get("zone_id"):
                raise NodeValidationError("Zone ID is required for zone operations")
                
        elif operation == OktaOperation.DELETE_USER_SESSION:
            if not params.get("user_id"):
                raise NodeValidationError("User ID is required for session operations")
            if not params.get("session_id"):
                raise NodeValidationError("Session ID is required for session operations")
                
        elif operation in [OktaOperation.GET_IDENTITY_PROVIDER, OktaOperation.UPDATE_IDENTITY_PROVIDER,
                          OktaOperation.DELETE_IDENTITY_PROVIDER, OktaOperation.ACTIVATE_IDENTITY_PROVIDER,
                          OktaOperation.DEACTIVATE_IDENTITY_PROVIDER]:
            if not params.get("identity_provider_id"):
                raise NodeValidationError("Identity provider ID is required for identity provider operations")
                
        elif operation in [OktaOperation.GET_REALM, OktaOperation.UPDATE_REALM, OktaOperation.DELETE_REALM]:
            if not params.get("realm_id"):
                raise NodeValidationError("Realm ID is required for realm operations")
                
        elif operation == OktaOperation.CREATE_USER:
            if not params.get("profile") and not params.get("request_body"):
                raise NodeValidationError("Profile or request body is required for user creation")
                
        elif operation == OktaOperation.ENROLL_FACTOR:
            if not params.get("user_id"):
                raise NodeValidationError("User ID is required for factor enrollment")
            if not params.get("factor_type"):
                raise NodeValidationError("Factor type is required for factor enrollment")
                
        elif operation == OktaOperation.VERIFY_FACTOR:
            if not params.get("pass_code") and not params.get("request_body"):
                raise NodeValidationError("Pass code or request body is required for factor verification")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Okta node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Get access token if using OAuth 2.0
            if not validated_data.get("api_token") and validated_data.get("client_id"):
                token_result = await self._get_access_token(validated_data)
                if token_result["status"] != "success":
                    return token_result
                validated_data["access_token"] = token_result["access_token"]
            
            # Execute the appropriate operation
            if operation == OktaOperation.GET_ACCESS_TOKEN:
                return await self._operation_get_access_token(validated_data)
            elif operation == OktaOperation.GET_USERS:
                return await self._operation_get_users(validated_data)
            elif operation == OktaOperation.GET_USER:
                return await self._operation_get_user(validated_data)
            elif operation == OktaOperation.CREATE_USER:
                return await self._operation_create_user(validated_data)
            elif operation == OktaOperation.UPDATE_USER:
                return await self._operation_update_user(validated_data)
            elif operation == OktaOperation.DELETE_USER:
                return await self._operation_delete_user(validated_data)
            elif operation == OktaOperation.ACTIVATE_USER:
                return await self._operation_activate_user(validated_data)
            elif operation == OktaOperation.DEACTIVATE_USER:
                return await self._operation_deactivate_user(validated_data)
            elif operation == OktaOperation.SUSPEND_USER:
                return await self._operation_suspend_user(validated_data)
            elif operation == OktaOperation.UNSUSPEND_USER:
                return await self._operation_unsuspend_user(validated_data)
            elif operation == OktaOperation.RESET_PASSWORD:
                return await self._operation_reset_password(validated_data)
            elif operation == OktaOperation.EXPIRE_PASSWORD:
                return await self._operation_expire_password(validated_data)
            elif operation == OktaOperation.UNLOCK_USER:
                return await self._operation_unlock_user(validated_data)
            elif operation == OktaOperation.GET_USER_FACTORS:
                return await self._operation_get_user_factors(validated_data)
            elif operation == OktaOperation.ENROLL_FACTOR:
                return await self._operation_enroll_factor(validated_data)
            elif operation == OktaOperation.ACTIVATE_FACTOR:
                return await self._operation_activate_factor(validated_data)
            elif operation == OktaOperation.VERIFY_FACTOR:
                return await self._operation_verify_factor(validated_data)
            elif operation == OktaOperation.DELETE_FACTOR:
                return await self._operation_delete_factor(validated_data)
            elif operation == OktaOperation.LIST_FACTORS:
                return await self._operation_list_factors(validated_data)
            elif operation == OktaOperation.GET_APPLICATIONS:
                return await self._operation_get_applications(validated_data)
            elif operation == OktaOperation.GET_APPLICATION:
                return await self._operation_get_application(validated_data)
            elif operation == OktaOperation.CREATE_APPLICATION:
                return await self._operation_create_application(validated_data)
            elif operation == OktaOperation.UPDATE_APPLICATION:
                return await self._operation_update_application(validated_data)
            elif operation == OktaOperation.DELETE_APPLICATION:
                return await self._operation_delete_application(validated_data)
            elif operation == OktaOperation.ACTIVATE_APPLICATION:
                return await self._operation_activate_application(validated_data)
            elif operation == OktaOperation.DEACTIVATE_APPLICATION:
                return await self._operation_deactivate_application(validated_data)
            elif operation == OktaOperation.GET_GROUPS:
                return await self._operation_get_groups(validated_data)
            elif operation == OktaOperation.GET_GROUP:
                return await self._operation_get_group(validated_data)
            elif operation == OktaOperation.CREATE_GROUP:
                return await self._operation_create_group(validated_data)
            elif operation == OktaOperation.UPDATE_GROUP:
                return await self._operation_update_group(validated_data)
            elif operation == OktaOperation.DELETE_GROUP:
                return await self._operation_delete_group(validated_data)
            elif operation == OktaOperation.GET_GROUP_MEMBERS:
                return await self._operation_get_group_members(validated_data)
            elif operation == OktaOperation.ADD_USER_TO_GROUP:
                return await self._operation_add_user_to_group(validated_data)
            elif operation == OktaOperation.REMOVE_USER_FROM_GROUP:
                return await self._operation_remove_user_from_group(validated_data)
            elif operation == OktaOperation.GET_ROLES:
                return await self._operation_get_roles(validated_data)
            elif operation == OktaOperation.GET_AUTHORIZATION_SERVERS:
                return await self._operation_get_authorization_servers(validated_data)
            elif operation == OktaOperation.GET_AUTHORIZATION_SERVER:
                return await self._operation_get_authorization_server(validated_data)
            elif operation == OktaOperation.CREATE_AUTHORIZATION_SERVER:
                return await self._operation_create_authorization_server(validated_data)
            elif operation == OktaOperation.UPDATE_AUTHORIZATION_SERVER:
                return await self._operation_update_authorization_server(validated_data)
            elif operation == OktaOperation.DELETE_AUTHORIZATION_SERVER:
                return await self._operation_delete_authorization_server(validated_data)
            elif operation == OktaOperation.GET_SCOPES:
                return await self._operation_get_scopes(validated_data)
            elif operation == OktaOperation.GET_SCOPE:
                return await self._operation_get_scope(validated_data)
            elif operation == OktaOperation.CREATE_SCOPE:
                return await self._operation_create_scope(validated_data)
            elif operation == OktaOperation.UPDATE_SCOPE:
                return await self._operation_update_scope(validated_data)
            elif operation == OktaOperation.DELETE_SCOPE:
                return await self._operation_delete_scope(validated_data)
            elif operation == OktaOperation.GET_POLICIES:
                return await self._operation_get_policies(validated_data)
            elif operation == OktaOperation.GET_POLICY:
                return await self._operation_get_policy(validated_data)
            elif operation == OktaOperation.CREATE_POLICY:
                return await self._operation_create_policy(validated_data)
            elif operation == OktaOperation.UPDATE_POLICY:
                return await self._operation_update_policy(validated_data)
            elif operation == OktaOperation.DELETE_POLICY:
                return await self._operation_delete_policy(validated_data)
            elif operation == OktaOperation.GET_ZONES:
                return await self._operation_get_zones(validated_data)
            elif operation == OktaOperation.GET_ZONE:
                return await self._operation_get_zone(validated_data)
            elif operation == OktaOperation.CREATE_ZONE:
                return await self._operation_create_zone(validated_data)
            elif operation == OktaOperation.UPDATE_ZONE:
                return await self._operation_update_zone(validated_data)
            elif operation == OktaOperation.DELETE_ZONE:
                return await self._operation_delete_zone(validated_data)
            elif operation == OktaOperation.GET_SYSTEM_LOGS:
                return await self._operation_get_system_logs(validated_data)
            elif operation == OktaOperation.GET_USER_SESSIONS:
                return await self._operation_get_user_sessions(validated_data)
            elif operation == OktaOperation.DELETE_USER_SESSION:
                return await self._operation_delete_user_session(validated_data)
            elif operation == OktaOperation.DELETE_USER_SESSIONS:
                return await self._operation_delete_user_sessions(validated_data)
            elif operation == OktaOperation.GET_IDENTITY_PROVIDERS:
                return await self._operation_get_identity_providers(validated_data)
            elif operation == OktaOperation.GET_IDENTITY_PROVIDER:
                return await self._operation_get_identity_provider(validated_data)
            elif operation == OktaOperation.CREATE_IDENTITY_PROVIDER:
                return await self._operation_create_identity_provider(validated_data)
            elif operation == OktaOperation.UPDATE_IDENTITY_PROVIDER:
                return await self._operation_update_identity_provider(validated_data)
            elif operation == OktaOperation.DELETE_IDENTITY_PROVIDER:
                return await self._operation_delete_identity_provider(validated_data)
            elif operation == OktaOperation.GET_REALMS:
                return await self._operation_get_realms(validated_data)
            elif operation == OktaOperation.GET_REALM:
                return await self._operation_get_realm(validated_data)
            elif operation == OktaOperation.CREATE_REALM:
                return await self._operation_create_realm(validated_data)
            elif operation == OktaOperation.UPDATE_REALM:
                return await self._operation_update_realm(validated_data)
            elif operation == OktaOperation.DELETE_REALM:
                return await self._operation_delete_realm(validated_data)
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
            error_message = f"Error in Okta node: {str(e)}"
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
    
    async def _get_access_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get access token using OAuth 2.0 client credentials."""
        try:
            org_url = params.get("org_url").rstrip('/')
            client_id = params.get("client_id")
            client_secret = params.get("client_secret")
            scopes = params.get("scopes", ["okta.users.read", "okta.apps.read"])
            
            url = f"{org_url}/oauth2/v1/token"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            
            data = {
                "grant_type": "client_credentials",
                "scope": " ".join(scopes)
            }
            
            # Use basic authentication
            auth = aiohttp.BasicAuth(client_id, client_secret)
            
            async with self.session.post(url, headers=headers, data=data, auth=auth) as response:
                response_headers = dict(response.headers)
                response_data = await response.json()
                
                if response.status >= 400:
                    error_message = f"Okta API error {response.status}: {response_data}"
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
                    "access_token": response_data.get("access_token"),
                    "token_type": response_data.get("token_type"),
                    "expires_in": response_data.get("expires_in"),
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
        except Exception as e:
            error_message = f"Error getting access token: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "error": error_message,
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any], 
                          data: Optional[Dict[str, Any]] = None, query_params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the Okta API."""
        org_url = params.get("org_url").rstrip('/')
        api_token = params.get("api_token")
        access_token = params.get("access_token")
        
        url = f"{org_url}/api/v1/{endpoint}"
        if query_params:
            url += "?" + urlencode(query_params)
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Use API token or OAuth 2.0 access token
        if api_token:
            headers["Authorization"] = f"SSWS {api_token}"
        elif access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                response_headers = dict(response.headers)
                
                # Handle different response content types
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Okta API error {response.status}: {response_data}"
                    logger.error(error_message)
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                # Extract pagination info if present
                pagination = {}
                if "link" in response_headers:
                    pagination["link"] = response_headers["link"]
                
                return {
                    "status": "success",
                    "result": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers,
                    "pagination": pagination if pagination else None
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
    
    async def _operation_get_access_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get access token for Okta API."""
        return await self._get_access_token(params)
    
    # -------------------------
    # User Management Operations
    # -------------------------
    
    async def _operation_get_users(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of users."""
        query_params = {}
        
        if params.get("q"):
            query_params["q"] = params.get("q")
        if params.get("filter"):
            query_params["filter"] = params.get("filter")
        if params.get("search"):
            query_params["search"] = params.get("search")
        if params.get("limit"):
            query_params["limit"] = str(params.get("limit"))
        if params.get("after"):
            query_params["after"] = params.get("after")
        if params.get("sortBy"):
            query_params["sortBy"] = params.get("sortBy")
        if params.get("sortOrder"):
            query_params["sortOrder"] = params.get("sortOrder")
        
        result = await self._make_request("GET", "users", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["users"] = result["result"]
        
        return result
    
    async def _operation_get_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific user."""
        user_id = params.get("user_id")
        
        result = await self._make_request("GET", f"users/{user_id}", params)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_create_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        request_body = params.get("request_body", {})
        
        # If no request body provided, build from parameters
        if not request_body:
            request_body = {}
            
            if params.get("profile"):
                request_body["profile"] = params.get("profile")
            if params.get("credentials"):
                request_body["credentials"] = params.get("credentials")
        
        query_params = {}
        if params.get("activate") is not None:
            query_params["activate"] = str(params.get("activate")).lower()
        if params.get("provider") is not None:
            query_params["provider"] = str(params.get("provider")).lower()
        if params.get("next_login"):
            query_params["nextLogin"] = params.get("next_login")
        
        result = await self._make_request("POST", "users", params, request_body, query_params)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_update_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing user."""
        user_id = params.get("user_id")
        request_body = params.get("request_body", {})
        
        # If no request body provided, build from parameters
        if not request_body:
            request_body = {}
            
            if params.get("profile"):
                request_body["profile"] = params.get("profile")
            if params.get("credentials"):
                request_body["credentials"] = params.get("credentials")
        
        result = await self._make_request("POST", f"users/{user_id}", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_delete_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a user."""
        user_id = params.get("user_id")
        
        query_params = {}
        if params.get("send_email") is not None:
            query_params["sendEmail"] = str(params.get("send_email")).lower()
        
        result = await self._make_request("DELETE", f"users/{user_id}", params, query_params=query_params)
        
        if result["status"] == "success":
            result["id"] = user_id
        
        return result
    
    async def _operation_activate_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Activate a user."""
        user_id = params.get("user_id")
        
        query_params = {}
        if params.get("send_email") is not None:
            query_params["sendEmail"] = str(params.get("send_email")).lower()
        
        result = await self._make_request("POST", f"users/{user_id}/lifecycle/activate", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_deactivate_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deactivate a user."""
        user_id = params.get("user_id")
        
        query_params = {}
        if params.get("send_email") is not None:
            query_params["sendEmail"] = str(params.get("send_email")).lower()
        
        result = await self._make_request("POST", f"users/{user_id}/lifecycle/deactivate", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_suspend_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Suspend a user."""
        user_id = params.get("user_id")
        
        result = await self._make_request("POST", f"users/{user_id}/lifecycle/suspend", params)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_unsuspend_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unsuspend a user."""
        user_id = params.get("user_id")
        
        result = await self._make_request("POST", f"users/{user_id}/lifecycle/unsuspend", params)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_reset_password(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reset user password."""
        user_id = params.get("user_id")
        
        query_params = {}
        if params.get("send_email") is not None:
            query_params["sendEmail"] = str(params.get("send_email")).lower()
        
        result = await self._make_request("POST", f"users/{user_id}/lifecycle/reset_password", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_expire_password(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Expire user password."""
        user_id = params.get("user_id")
        
        query_params = {}
        if params.get("temp_password") is not None:
            query_params["tempPassword"] = str(params.get("temp_password")).lower()
        
        result = await self._make_request("POST", f"users/{user_id}/lifecycle/expire_password", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_unlock_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unlock a user."""
        user_id = params.get("user_id")
        
        result = await self._make_request("POST", f"users/{user_id}/lifecycle/unlock", params)
        
        if result["status"] == "success" and result["result"]:
            result["user"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    # -------------------------
    # User Factors Operations
    # -------------------------
    
    async def _operation_get_user_factors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get user factors."""
        user_id = params.get("user_id")
        
        result = await self._make_request("GET", f"users/{user_id}/factors", params)
        
        if result["status"] == "success" and result["result"]:
            result["factors"] = result["result"]
        
        return result
    
    async def _operation_enroll_factor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enroll a factor for a user."""
        user_id = params.get("user_id")
        request_body = params.get("request_body", {})
        
        # If no request body provided, build from parameters
        if not request_body:
            request_body = {}
            
            if params.get("factor_type"):
                request_body["factorType"] = params.get("factor_type")
            if params.get("provider"):
                request_body["provider"] = params.get("provider")
        
        query_params = {}
        if params.get("update_phone") is not None:
            query_params["updatePhone"] = str(params.get("update_phone")).lower()
        if params.get("template_id"):
            query_params["templateId"] = params.get("template_id")
        if params.get("token_lifetime_seconds"):
            query_params["tokenLifetimeSeconds"] = str(params.get("token_lifetime_seconds"))
        if params.get("activate") is not None:
            query_params["activate"] = str(params.get("activate")).lower()
        
        result = await self._make_request("POST", f"users/{user_id}/factors", params, request_body, query_params)
        
        if result["status"] == "success" and result["result"]:
            result["factor"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_activate_factor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Activate a factor."""
        user_id = params.get("user_id")
        factor_id = params.get("factor_id")
        request_body = params.get("request_body", {})
        
        # If no request body provided, build from parameters
        if not request_body:
            request_body = {}
            
            if params.get("pass_code"):
                request_body["passCode"] = params.get("pass_code")
        
        result = await self._make_request("POST", f"users/{user_id}/factors/{factor_id}/lifecycle/activate", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["factor"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_verify_factor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a factor."""
        user_id = params.get("user_id")
        factor_id = params.get("factor_id")
        request_body = params.get("request_body", {})
        
        # If no request body provided, build from parameters
        if not request_body:
            request_body = {}
            
            if params.get("pass_code"):
                request_body["passCode"] = params.get("pass_code")
        
        result = await self._make_request("POST", f"users/{user_id}/factors/{factor_id}/verify", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["factor"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_delete_factor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a factor."""
        user_id = params.get("user_id")
        factor_id = params.get("factor_id")
        
        result = await self._make_request("DELETE", f"users/{user_id}/factors/{factor_id}", params)
        
        if result["status"] == "success":
            result["id"] = factor_id
        
        return result
    
    async def _operation_list_factors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available factors."""
        result = await self._make_request("GET", "users/factors/catalog", params)
        
        if result["status"] == "success" and result["result"]:
            result["factors"] = result["result"]
        
        return result
    
    # -------------------------
    # Application Management Operations
    # -------------------------
    
    async def _operation_get_applications(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of applications."""
        query_params = {}
        
        if params.get("q"):
            query_params["q"] = params.get("q")
        if params.get("filter"):
            query_params["filter"] = params.get("filter")
        if params.get("limit"):
            query_params["limit"] = str(params.get("limit"))
        if params.get("after"):
            query_params["after"] = params.get("after")
        if params.get("expand"):
            query_params["expand"] = params.get("expand")
        
        result = await self._make_request("GET", "apps", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["applications"] = result["result"]
        
        return result
    
    async def _operation_get_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific application."""
        application_id = params.get("application_id")
        
        query_params = {}
        if params.get("expand"):
            query_params["expand"] = params.get("expand")
        
        result = await self._make_request("GET", f"apps/{application_id}", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["application"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_create_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new application."""
        request_body = params.get("request_body", {})
        
        query_params = {}
        if params.get("activate") is not None:
            query_params["activate"] = str(params.get("activate")).lower()
        
        result = await self._make_request("POST", "apps", params, request_body, query_params)
        
        if result["status"] == "success" and result["result"]:
            result["application"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_update_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing application."""
        application_id = params.get("application_id")
        request_body = params.get("request_body", {})
        
        result = await self._make_request("PUT", f"apps/{application_id}", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["application"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_delete_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an application."""
        application_id = params.get("application_id")
        
        result = await self._make_request("DELETE", f"apps/{application_id}", params)
        
        if result["status"] == "success":
            result["id"] = application_id
        
        return result
    
    async def _operation_activate_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Activate an application."""
        application_id = params.get("application_id")
        
        result = await self._make_request("POST", f"apps/{application_id}/lifecycle/activate", params)
        
        if result["status"] == "success" and result["result"]:
            result["application"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_deactivate_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deactivate an application."""
        application_id = params.get("application_id")
        
        result = await self._make_request("POST", f"apps/{application_id}/lifecycle/deactivate", params)
        
        if result["status"] == "success" and result["result"]:
            result["application"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    # -------------------------
    # Group Management Operations
    # -------------------------
    
    async def _operation_get_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of groups."""
        query_params = {}
        
        if params.get("q"):
            query_params["q"] = params.get("q")
        if params.get("filter"):
            query_params["filter"] = params.get("filter")
        if params.get("search"):
            query_params["search"] = params.get("search")
        if params.get("limit"):
            query_params["limit"] = str(params.get("limit"))
        if params.get("after"):
            query_params["after"] = params.get("after")
        if params.get("sortBy"):
            query_params["sortBy"] = params.get("sortBy")
        if params.get("sortOrder"):
            query_params["sortOrder"] = params.get("sortOrder")
        if params.get("expand"):
            query_params["expand"] = params.get("expand")
        
        result = await self._make_request("GET", "groups", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["groups"] = result["result"]
        
        return result
    
    async def _operation_get_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific group."""
        group_id = params.get("group_id")
        
        result = await self._make_request("GET", f"groups/{group_id}", params)
        
        if result["status"] == "success" and result["result"]:
            result["group"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_create_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new group."""
        request_body = params.get("request_body", {})
        
        result = await self._make_request("POST", "groups", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["group"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_update_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing group."""
        group_id = params.get("group_id")
        request_body = params.get("request_body", {})
        
        result = await self._make_request("PUT", f"groups/{group_id}", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["group"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_delete_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a group."""
        group_id = params.get("group_id")
        
        result = await self._make_request("DELETE", f"groups/{group_id}", params)
        
        if result["status"] == "success":
            result["id"] = group_id
        
        return result
    
    async def _operation_get_group_members(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get group members."""
        group_id = params.get("group_id")
        
        query_params = {}
        if params.get("limit"):
            query_params["limit"] = str(params.get("limit"))
        if params.get("after"):
            query_params["after"] = params.get("after")
        
        result = await self._make_request("GET", f"groups/{group_id}/users", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["users"] = result["result"]
        
        return result
    
    async def _operation_add_user_to_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add user to group."""
        group_id = params.get("group_id")
        user_id = params.get("user_id")
        
        result = await self._make_request("PUT", f"groups/{group_id}/users/{user_id}", params)
        
        if result["status"] == "success":
            result["id"] = user_id
        
        return result
    
    async def _operation_remove_user_from_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove user from group."""
        group_id = params.get("group_id")
        user_id = params.get("user_id")
        
        result = await self._make_request("DELETE", f"groups/{group_id}/users/{user_id}", params)
        
        if result["status"] == "success":
            result["id"] = user_id
        
        return result
    
    # -------------------------
    # Roles Management Operations
    # -------------------------
    
    async def _operation_get_roles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of roles."""
        query_params = {}
        
        if params.get("type"):
            query_params["type"] = params.get("type")
        
        result = await self._make_request("GET", "iam/roles", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["roles"] = result["result"]
        
        return result
    
    # -------------------------
    # Authorization Server Operations
    # -------------------------
    
    async def _operation_get_authorization_servers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of authorization servers."""
        query_params = {}
        
        if params.get("q"):
            query_params["q"] = params.get("q")
        if params.get("limit"):
            query_params["limit"] = str(params.get("limit"))
        if params.get("after"):
            query_params["after"] = params.get("after")
        
        result = await self._make_request("GET", "authorizationServers", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["authorization_servers"] = result["result"]
        
        return result
    
    async def _operation_get_authorization_server(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific authorization server."""
        authorization_server_id = params.get("authorization_server_id")
        
        result = await self._make_request("GET", f"authorizationServers/{authorization_server_id}", params)
        
        if result["status"] == "success" and result["result"]:
            result["authorization_server"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_create_authorization_server(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new authorization server."""
        request_body = params.get("request_body", {})
        
        result = await self._make_request("POST", "authorizationServers", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["authorization_server"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_update_authorization_server(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing authorization server."""
        authorization_server_id = params.get("authorization_server_id")
        request_body = params.get("request_body", {})
        
        result = await self._make_request("PUT", f"authorizationServers/{authorization_server_id}", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["authorization_server"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_delete_authorization_server(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an authorization server."""
        authorization_server_id = params.get("authorization_server_id")
        
        result = await self._make_request("DELETE", f"authorizationServers/{authorization_server_id}", params)
        
        if result["status"] == "success":
            result["id"] = authorization_server_id
        
        return result
    
    # -------------------------
    # Scopes Management Operations
    # -------------------------
    
    async def _operation_get_scopes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get scopes for an authorization server."""
        authorization_server_id = params.get("authorization_server_id")
        
        query_params = {}
        if params.get("q"):
            query_params["q"] = params.get("q")
        if params.get("filter"):
            query_params["filter"] = params.get("filter")
        if params.get("limit"):
            query_params["limit"] = str(params.get("limit"))
        if params.get("after"):
            query_params["after"] = params.get("after")
        
        result = await self._make_request("GET", f"authorizationServers/{authorization_server_id}/scopes", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["scopes"] = result["result"]
        
        return result
    
    async def _operation_get_scope(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific scope."""
        authorization_server_id = params.get("authorization_server_id")
        scope_id = params.get("scope_id")
        
        result = await self._make_request("GET", f"authorizationServers/{authorization_server_id}/scopes/{scope_id}", params)
        
        if result["status"] == "success" and result["result"]:
            result["scope"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_create_scope(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new scope."""
        authorization_server_id = params.get("authorization_server_id")
        request_body = params.get("request_body", {})
        
        result = await self._make_request("POST", f"authorizationServers/{authorization_server_id}/scopes", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["scope"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_update_scope(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing scope."""
        authorization_server_id = params.get("authorization_server_id")
        scope_id = params.get("scope_id")
        request_body = params.get("request_body", {})
        
        result = await self._make_request("PUT", f"authorizationServers/{authorization_server_id}/scopes/{scope_id}", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["scope"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_delete_scope(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a scope."""
        authorization_server_id = params.get("authorization_server_id")
        scope_id = params.get("scope_id")
        
        result = await self._make_request("DELETE", f"authorizationServers/{authorization_server_id}/scopes/{scope_id}", params)
        
        if result["status"] == "success":
            result["id"] = scope_id
        
        return result
    
    # -------------------------
    # Policies Management Operations
    # -------------------------
    
    async def _operation_get_policies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of policies."""
        query_params = {}
        
        if params.get("type"):
            query_params["type"] = params.get("type")
        if params.get("status"):
            query_params["status"] = params.get("status")
        if params.get("expand"):
            query_params["expand"] = params.get("expand")
        
        result = await self._make_request("GET", "policies", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["policies"] = result["result"]
        
        return result
    
    async def _operation_get_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific policy."""
        policy_id = params.get("policy_id")
        
        query_params = {}
        if params.get("expand"):
            query_params["expand"] = params.get("expand")
        
        result = await self._make_request("GET", f"policies/{policy_id}", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["policy"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_create_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new policy."""
        request_body = params.get("request_body", {})
        
        query_params = {}
        if params.get("activate") is not None:
            query_params["activate"] = str(params.get("activate")).lower()
        
        result = await self._make_request("POST", "policies", params, request_body, query_params)
        
        if result["status"] == "success" and result["result"]:
            result["policy"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_update_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing policy."""
        policy_id = params.get("policy_id")
        request_body = params.get("request_body", {})
        
        result = await self._make_request("PUT", f"policies/{policy_id}", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["policy"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_delete_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a policy."""
        policy_id = params.get("policy_id")
        
        result = await self._make_request("DELETE", f"policies/{policy_id}", params)
        
        if result["status"] == "success":
            result["id"] = policy_id
        
        return result
    
    # -------------------------
    # Zones Management Operations
    # -------------------------
    
    async def _operation_get_zones(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of zones."""
        query_params = {}
        
        if params.get("filter"):
            query_params["filter"] = params.get("filter")
        if params.get("after"):
            query_params["after"] = params.get("after")
        if params.get("limit"):
            query_params["limit"] = str(params.get("limit"))
        
        result = await self._make_request("GET", "zones", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["zones"] = result["result"]
        
        return result
    
    async def _operation_get_zone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific zone."""
        zone_id = params.get("zone_id")
        
        result = await self._make_request("GET", f"zones/{zone_id}", params)
        
        if result["status"] == "success" and result["result"]:
            result["zone"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_create_zone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new zone."""
        request_body = params.get("request_body", {})
        
        result = await self._make_request("POST", "zones", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["zone"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_update_zone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing zone."""
        zone_id = params.get("zone_id")
        request_body = params.get("request_body", {})
        
        result = await self._make_request("PUT", f"zones/{zone_id}", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["zone"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_delete_zone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a zone."""
        zone_id = params.get("zone_id")
        
        result = await self._make_request("DELETE", f"zones/{zone_id}", params)
        
        if result["status"] == "success":
            result["id"] = zone_id
        
        return result
    
    # -------------------------
    # System Log Operations
    # -------------------------
    
    async def _operation_get_system_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get system logs."""
        query_params = {}
        
        if params.get("filter"):
            query_params["filter"] = params.get("filter")
        if params.get("q"):
            query_params["q"] = params.get("q")
        if params.get("limit"):
            query_params["limit"] = str(params.get("limit"))
        if params.get("sortOrder"):
            query_params["sortOrder"] = params.get("sortOrder")
        if params.get("after"):
            query_params["after"] = params.get("after")
        if params.get("since"):
            query_params["since"] = params.get("since")
        if params.get("until"):
            query_params["until"] = params.get("until")
        
        result = await self._make_request("GET", "logs", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["logs"] = result["result"]
        
        return result
    
    # -------------------------
    # Sessions Management Operations
    # -------------------------
    
    async def _operation_get_user_sessions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get user sessions."""
        user_id = params.get("user_id")
        
        result = await self._make_request("GET", f"users/{user_id}/sessions", params)
        
        if result["status"] == "success" and result["result"]:
            result["sessions"] = result["result"]
        
        return result
    
    async def _operation_delete_user_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a specific user session."""
        user_id = params.get("user_id")
        session_id = params.get("session_id")
        
        result = await self._make_request("DELETE", f"users/{user_id}/sessions/{session_id}", params)
        
        if result["status"] == "success":
            result["id"] = session_id
        
        return result
    
    async def _operation_delete_user_sessions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete all user sessions."""
        user_id = params.get("user_id")
        
        query_params = {}
        if params.get("oauth_tokens_only") is not None:
            query_params["oauthTokens"] = str(params.get("oauth_tokens_only")).lower()
        
        result = await self._make_request("DELETE", f"users/{user_id}/sessions", params, query_params=query_params)
        
        if result["status"] == "success":
            result["id"] = user_id
        
        return result
    
    # -------------------------
    # Identity Provider Operations
    # -------------------------
    
    async def _operation_get_identity_providers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of identity providers."""
        query_params = {}
        
        if params.get("q"):
            query_params["q"] = params.get("q")
        if params.get("after"):
            query_params["after"] = params.get("after")
        if params.get("limit"):
            query_params["limit"] = str(params.get("limit"))
        if params.get("type"):
            query_params["type"] = params.get("type")
        
        result = await self._make_request("GET", "idps", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["identity_providers"] = result["result"]
        
        return result
    
    async def _operation_get_identity_provider(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific identity provider."""
        identity_provider_id = params.get("identity_provider_id")
        
        result = await self._make_request("GET", f"idps/{identity_provider_id}", params)
        
        if result["status"] == "success" and result["result"]:
            result["identity_provider"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_create_identity_provider(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new identity provider."""
        request_body = params.get("request_body", {})
        
        result = await self._make_request("POST", "idps", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["identity_provider"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_update_identity_provider(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing identity provider."""
        identity_provider_id = params.get("identity_provider_id")
        request_body = params.get("request_body", {})
        
        result = await self._make_request("PUT", f"idps/{identity_provider_id}", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["identity_provider"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_delete_identity_provider(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an identity provider."""
        identity_provider_id = params.get("identity_provider_id")
        
        result = await self._make_request("DELETE", f"idps/{identity_provider_id}", params)
        
        if result["status"] == "success":
            result["id"] = identity_provider_id
        
        return result
    
    # -------------------------
    # Realms Management Operations
    # -------------------------
    
    async def _operation_get_realms(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of realms."""
        query_params = {}
        
        if params.get("limit"):
            query_params["limit"] = str(params.get("limit"))
        if params.get("after"):
            query_params["after"] = params.get("after")
        
        result = await self._make_request("GET", "realms", params, query_params=query_params)
        
        if result["status"] == "success" and result["result"]:
            result["realms"] = result["result"]
        
        return result
    
    async def _operation_get_realm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific realm."""
        realm_id = params.get("realm_id")
        
        result = await self._make_request("GET", f"realms/{realm_id}", params)
        
        if result["status"] == "success" and result["result"]:
            result["realm"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_create_realm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new realm."""
        request_body = params.get("request_body", {})
        
        result = await self._make_request("POST", "realms", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["realm"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_update_realm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing realm."""
        realm_id = params.get("realm_id")
        request_body = params.get("request_body", {})
        
        result = await self._make_request("PUT", f"realms/{realm_id}", params, request_body)
        
        if result["status"] == "success" and result["result"]:
            result["realm"] = result["result"]
            result["id"] = result["result"].get("id")
        
        return result
    
    async def _operation_delete_realm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a realm."""
        realm_id = params.get("realm_id")
        
        result = await self._make_request("DELETE", f"realms/{realm_id}", params)
        
        if result["status"] == "success":
            result["id"] = realm_id
        
        return result


# Utility functions for common Okta operations
class OktaHelpers:
    """Helper functions for common Okta operations."""
    
    @staticmethod
    def create_user_profile(email: str, first_name: str, last_name: str, 
                           login: str = None, mobile_phone: str = None) -> Dict[str, Any]:
        """Create a user profile object."""
        profile = {
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "login": login or email
        }
        
        if mobile_phone:
            profile["mobilePhone"] = mobile_phone
            
        return profile
    
    @staticmethod
    def create_user_credentials(password: str = None, recovery_question: Dict[str, str] = None) -> Dict[str, Any]:
        """Create a user credentials object."""
        credentials = {}
        
        if password:
            credentials["password"] = {"value": password}
        
        if recovery_question:
            credentials["recovery_question"] = recovery_question
            
        return credentials
    
    @staticmethod
    def create_group_profile(name: str, description: str = None) -> Dict[str, Any]:
        """Create a group profile object."""
        profile = {"name": name}
        
        if description:
            profile["description"] = description
            
        return profile
    
    @staticmethod
    def create_application_settings(app_url: str = None, redirect_uris: List[str] = None) -> Dict[str, Any]:
        """Create application settings object."""
        settings = {}
        
        if app_url:
            settings["app"] = {"baseUrl": app_url}
        
        if redirect_uris:
            settings["oauthClient"] = {"redirect_uris": redirect_uris}
            
        return settings
    
    @staticmethod
    def create_factor_profile(phone_number: str = None, question: str = None, answer: str = None) -> Dict[str, Any]:
        """Create a factor profile object."""
        profile = {}
        
        if phone_number:
            profile["phoneNumber"] = phone_number
        
        if question and answer:
            profile["question"] = question
            profile["answer"] = answer
            
        return profile
    
    @staticmethod
    def create_authorization_server_settings(issuer: str, audience: str = None) -> Dict[str, Any]:
        """Create authorization server settings."""
        settings = {
            "issuer": issuer
        }
        
        if audience:
            settings["audience"] = audience
            
        return settings
    
    @staticmethod
    def create_scope_settings(name: str, description: str = None, consent: str = "IMPLICIT") -> Dict[str, Any]:
        """Create scope settings."""
        settings = {
            "name": name,
            "consent": consent
        }
        
        if description:
            settings["description"] = description
            
        return settings


# Main test function for Okta Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Okta Node Test Suite ===")
        
        # Get credentials from environment or user input
        org_url = os.environ.get("OKTA_ORG_URL")
        api_token = os.environ.get("OKTA_API_TOKEN")
        client_id = os.environ.get("OKTA_CLIENT_ID")
        client_secret = os.environ.get("OKTA_CLIENT_SECRET")
        
        if not org_url:
            print("Okta organization URL not found in environment variables")
            print("Please set OKTA_ORG_URL")
            print("Or provide it when prompted...")
            org_url = input("Enter Okta organization URL: ")
        
        if not api_token and not (client_id and client_secret):
            print("Okta credentials not found in environment variables")
            print("Please set OKTA_API_TOKEN or (OKTA_CLIENT_ID and OKTA_CLIENT_SECRET)")
            print("Or provide them when prompted...")
            
            choice = input("Use API token (1) or OAuth 2.0 (2)? ")
            if choice == "1":
                api_token = input("Enter Okta API token: ")
            else:
                client_id = input("Enter Okta Client ID: ")
                client_secret = input("Enter Okta Client Secret: ")
        
        if not org_url or (not api_token and not (client_id and client_secret)):
            print("Okta credentials are required for testing")
            return
        
        # Create an instance of the Okta Node
        node = OktaNode()
        
        # Test cases
        test_cases = [
            {
                "name": "Get Users",
                "params": {
                    "operation": OktaOperation.GET_USERS,
                    "org_url": org_url,
                    "api_token": api_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "limit": 5
                },
                "expected_status": "success"
            },
            {
                "name": "Get Applications",
                "params": {
                    "operation": OktaOperation.GET_APPLICATIONS,
                    "org_url": org_url,
                    "api_token": api_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "limit": 5
                },
                "expected_status": "success"
            },
            {
                "name": "Get Groups",
                "params": {
                    "operation": OktaOperation.GET_GROUPS,
                    "org_url": org_url,
                    "api_token": api_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "limit": 5
                },
                "expected_status": "success"
            }
        ]
        
        # Add OAuth 2.0 test if using OAuth
        if client_id and client_secret:
            test_cases.insert(0, {
                "name": "Get Access Token",
                "params": {
                    "operation": OktaOperation.GET_ACCESS_TOKEN,
                    "org_url": org_url,
                    "client_id": client_id,
                    "client_secret": client_secret
                },
                "expected_status": "success"
            })
        
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
                        print(f"Access token obtained (length: {len(result['access_token'])} chars)")
                    if result.get("users"):
                        print(f"Users retrieved: {len(result['users'])} users")
                    if result.get("applications"):
                        print(f"Applications retrieved: {len(result['applications'])} applications")
                    if result.get("groups"):
                        print(f"Groups retrieved: {len(result['groups'])} groups")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
                # Add a delay between tests to avoid rate limiting
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
    registry.register("okta", OktaNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register OktaNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")