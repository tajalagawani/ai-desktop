"""
Vercel Node - Comprehensive integration with Vercel API
Provides access to all Vercel API operations including projects, deployments, domains, functions, and team management.
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

class VercelOperation:
    """Operations available on Vercel API."""
    
    # Authentication & Account
    GET_USER = "get_user"
    UPDATE_USER = "update_user"
    
    # Projects Management
    CREATE_PROJECT = "create_project"
    GET_PROJECT = "get_project"
    UPDATE_PROJECT = "update_project"
    DELETE_PROJECT = "delete_project"
    LIST_PROJECTS = "list_projects"
    PAUSE_PROJECT = "pause_project"
    UNPAUSE_PROJECT = "unpause_project"
    
    # Project Domains
    ADD_PROJECT_DOMAIN = "add_project_domain"
    REMOVE_PROJECT_DOMAIN = "remove_project_domain"
    LIST_PROJECT_DOMAINS = "list_project_domains"
    VERIFY_PROJECT_DOMAIN = "verify_project_domain"
    
    # Deployments Management
    CREATE_DEPLOYMENT = "create_deployment"
    GET_DEPLOYMENT = "get_deployment"
    DELETE_DEPLOYMENT = "delete_deployment"
    LIST_DEPLOYMENTS = "list_deployments"
    CANCEL_DEPLOYMENT = "cancel_deployment"
    PROMOTE_DEPLOYMENT = "promote_deployment"
    
    # Deployment Files
    LIST_DEPLOYMENT_FILES = "list_deployment_files"
    GET_DEPLOYMENT_FILE = "get_deployment_file"
    GET_DEPLOYMENT_EVENTS = "get_deployment_events"
    
    # Domains Management
    CREATE_DOMAIN = "create_domain"
    GET_DOMAIN = "get_domain"
    DELETE_DOMAIN = "delete_domain"
    LIST_DOMAINS = "list_domains"
    TRANSFER_DOMAIN = "transfer_domain"
    
    # DNS Records
    CREATE_DNS_RECORD = "create_dns_record"
    GET_DNS_RECORD = "get_dns_record"
    UPDATE_DNS_RECORD = "update_dns_record"
    DELETE_DNS_RECORD = "delete_dns_record"
    LIST_DNS_RECORDS = "list_dns_records"
    
    # Environment Variables
    CREATE_ENV_VAR = "create_env_var"
    GET_ENV_VAR = "get_env_var"
    UPDATE_ENV_VAR = "update_env_var"
    DELETE_ENV_VAR = "delete_env_var"
    LIST_ENV_VARS = "list_env_vars"
    BULK_CREATE_ENV_VARS = "bulk_create_env_vars"
    
    # Functions & Edge Functions
    LIST_FUNCTIONS = "list_functions"
    GET_FUNCTION = "get_function"
    DELETE_FUNCTION = "delete_function"
    GET_FUNCTION_LOGS = "get_function_logs"
    
    # Teams Management
    CREATE_TEAM = "create_team"
    GET_TEAM = "get_team"
    UPDATE_TEAM = "update_team"
    DELETE_TEAM = "delete_team"
    LIST_TEAMS = "list_teams"
    
    # Team Members
    ADD_TEAM_MEMBER = "add_team_member"
    GET_TEAM_MEMBER = "get_team_member"
    UPDATE_TEAM_MEMBER = "update_team_member"
    REMOVE_TEAM_MEMBER = "remove_team_member"
    LIST_TEAM_MEMBERS = "list_team_members"
    
    # Access Groups
    CREATE_ACCESS_GROUP = "create_access_group"
    GET_ACCESS_GROUP = "get_access_group"
    UPDATE_ACCESS_GROUP = "update_access_group"
    DELETE_ACCESS_GROUP = "delete_access_group"
    LIST_ACCESS_GROUPS = "list_access_groups"
    
    # Certificates
    GET_CERTIFICATE = "get_certificate"
    ISSUE_CERTIFICATE = "issue_certificate"
    DELETE_CERTIFICATE = "delete_certificate"
    LIST_CERTIFICATES = "list_certificates"
    
    # Webhooks
    CREATE_WEBHOOK = "create_webhook"
    GET_WEBHOOK = "get_webhook"
    UPDATE_WEBHOOK = "update_webhook"
    DELETE_WEBHOOK = "delete_webhook"
    LIST_WEBHOOKS = "list_webhooks"
    
    # Edge Config
    CREATE_EDGE_CONFIG = "create_edge_config"
    GET_EDGE_CONFIG = "get_edge_config"
    UPDATE_EDGE_CONFIG = "update_edge_config"
    DELETE_EDGE_CONFIG = "delete_edge_config"
    LIST_EDGE_CONFIGS = "list_edge_configs"
    GET_EDGE_CONFIG_ITEMS = "get_edge_config_items"
    UPSERT_EDGE_CONFIG_ITEMS = "upsert_edge_config_items"
    
    # Artifacts
    UPLOAD_ARTIFACT = "upload_artifact"
    GET_ARTIFACT = "get_artifact"
    DELETE_ARTIFACT = "delete_artifact"
    LIST_ARTIFACTS = "list_artifacts"
    
    # Checks (Deployment Validation)
    CREATE_CHECK = "create_check"
    GET_CHECK = "get_check"
    UPDATE_CHECK = "update_check"
    LIST_CHECKS = "list_checks"
    
    # Aliases
    CREATE_ALIAS = "create_alias"
    GET_ALIAS = "get_alias"
    DELETE_ALIAS = "delete_alias"
    LIST_ALIASES = "list_aliases"
    
    # Secrets
    CREATE_SECRET = "create_secret"
    GET_SECRET = "get_secret"
    RENAME_SECRET = "rename_secret"
    DELETE_SECRET = "delete_secret"
    LIST_SECRETS = "list_secrets"
    
    # Usage & Analytics
    GET_USAGE = "get_usage"
    GET_ANALYTICS = "get_analytics"

class VercelAuthType:
    """Authentication types for Vercel API."""
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"

class VercelEnvironment:
    """Vercel deployment environments."""
    PRODUCTION = "production"
    PREVIEW = "preview"
    DEVELOPMENT = "development"

class VercelFramework:
    """Supported frameworks on Vercel."""
    NEXTJS = "nextjs"
    REACT = "create-react-app"
    VUE = "vue"
    NUXT = "nuxtjs"
    GATSBY = "gatsby"
    ANGULAR = "angular"
    SVELTE = "svelte"
    STATIC = "static"
    OTHER = "other"

class VercelHelper:
    """Helper class for Vercel API operations."""
    
    @staticmethod
    def build_query_params(
        limit: Optional[int] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        team_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build query parameters for Vercel API requests."""
        params = {}
        
        if limit is not None:
            params['limit'] = min(limit, 100)  # Max 100 per Vercel limits
        if since:
            params['since'] = since
        if until:
            params['until'] = until
        if team_id:
            params['teamId'] = team_id
        
        # Add any additional parameters
        params.update(kwargs)
        
        return {k: v for k, v in params.items() if v is not None}
    
    @staticmethod
    def format_deployment_target(targets: List[str]) -> List[str]:
        """Format deployment targets for environment variables."""
        valid_targets = [VercelEnvironment.PRODUCTION, VercelEnvironment.PREVIEW, VercelEnvironment.DEVELOPMENT]
        return [target for target in targets if target in valid_targets]
    
    @staticmethod
    def validate_domain_name(domain: str) -> bool:
        """Validate domain name format."""
        import re
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    @staticmethod
    def build_env_var_payload(
        key: str,
        value: str,
        target: List[str],
        type: str = "encrypted",
        git_branch: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build environment variable payload."""
        payload = {
            "key": key,
            "value": value,
            "target": VercelHelper.format_deployment_target(target),
            "type": type
        }
        
        if git_branch:
            payload["gitBranch"] = git_branch
        if comment:
            payload["comment"] = comment
        
        return payload
    
    @staticmethod
    def build_deployment_payload(
        name: str,
        files: Optional[List[Dict[str, Any]]] = None,
        env: Optional[Dict[str, str]] = None,
        build: Optional[Dict[str, Any]] = None,
        regions: Optional[List[str]] = None,
        functions: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build deployment payload."""
        payload = {"name": name}
        
        if files:
            payload["files"] = files
        if env:
            payload["env"] = env
        if build:
            payload["build"] = build
        if regions:
            payload["regions"] = regions
        if functions:
            payload["functions"] = functions
        
        # Add additional deployment options
        payload.update(kwargs)
        
        return payload
    
    @staticmethod
    def validate_env_var_key(key: str) -> bool:
        """Validate environment variable key format."""
        import re
        # Must start with letter or underscore, contain only alphanumeric and underscores
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, key)) and len(key) <= 256
    
    @staticmethod
    def validate_env_var_value(value: str) -> bool:
        """Validate environment variable value length."""
        return len(value) <= 65536  # 64KB limit

class VercelNode(BaseNode):
    """
    Vercel Node - Comprehensive Vercel API integration
    
    This node provides access to all Vercel API operations including:
    - Project creation and management
    - Deployment automation and monitoring
    - Custom domain and DNS management
    - Environment variable configuration
    - Team collaboration and access control
    - Serverless and Edge function management
    - SSL certificate management
    - Webhook and integration setup
    - Analytics and usage monitoring
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://api.vercel.com"
        self.session = None
        
        # Rate limiting
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        self.request_times = []
        
    @property
    def schema(self) -> NodeSchema:
        return NodeSchema(
            name="vercel",
            display_name="Vercel",
            description="Comprehensive Vercel API integration for deployment automation, project management, and team collaboration",
            version="1.0.0",
            parameters=[
                # Authentication parameters
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Vercel API operation to perform",
                    required=True,
                    options=[
                        # Account
                        VercelOperation.GET_USER,
                        VercelOperation.UPDATE_USER,
                        
                        # Projects
                        VercelOperation.CREATE_PROJECT,
                        VercelOperation.GET_PROJECT,
                        VercelOperation.UPDATE_PROJECT,
                        VercelOperation.DELETE_PROJECT,
                        VercelOperation.LIST_PROJECTS,
                        VercelOperation.PAUSE_PROJECT,
                        VercelOperation.UNPAUSE_PROJECT,
                        
                        # Project Domains
                        VercelOperation.ADD_PROJECT_DOMAIN,
                        VercelOperation.REMOVE_PROJECT_DOMAIN,
                        VercelOperation.LIST_PROJECT_DOMAINS,
                        VercelOperation.VERIFY_PROJECT_DOMAIN,
                        
                        # Deployments
                        VercelOperation.CREATE_DEPLOYMENT,
                        VercelOperation.GET_DEPLOYMENT,
                        VercelOperation.DELETE_DEPLOYMENT,
                        VercelOperation.LIST_DEPLOYMENTS,
                        VercelOperation.CANCEL_DEPLOYMENT,
                        VercelOperation.PROMOTE_DEPLOYMENT,
                        
                        # Deployment Files
                        VercelOperation.LIST_DEPLOYMENT_FILES,
                        VercelOperation.GET_DEPLOYMENT_FILE,
                        VercelOperation.GET_DEPLOYMENT_EVENTS,
                        
                        # Domains
                        VercelOperation.CREATE_DOMAIN,
                        VercelOperation.GET_DOMAIN,
                        VercelOperation.DELETE_DOMAIN,
                        VercelOperation.LIST_DOMAINS,
                        VercelOperation.TRANSFER_DOMAIN,
                        
                        # DNS Records
                        VercelOperation.CREATE_DNS_RECORD,
                        VercelOperation.GET_DNS_RECORD,
                        VercelOperation.UPDATE_DNS_RECORD,
                        VercelOperation.DELETE_DNS_RECORD,
                        VercelOperation.LIST_DNS_RECORDS,
                        
                        # Environment Variables
                        VercelOperation.CREATE_ENV_VAR,
                        VercelOperation.GET_ENV_VAR,
                        VercelOperation.UPDATE_ENV_VAR,
                        VercelOperation.DELETE_ENV_VAR,
                        VercelOperation.LIST_ENV_VARS,
                        VercelOperation.BULK_CREATE_ENV_VARS,
                        
                        # Functions
                        VercelOperation.LIST_FUNCTIONS,
                        VercelOperation.GET_FUNCTION,
                        VercelOperation.DELETE_FUNCTION,
                        VercelOperation.GET_FUNCTION_LOGS,
                        
                        # Teams
                        VercelOperation.CREATE_TEAM,
                        VercelOperation.GET_TEAM,
                        VercelOperation.UPDATE_TEAM,
                        VercelOperation.DELETE_TEAM,
                        VercelOperation.LIST_TEAMS,
                        
                        # Team Members
                        VercelOperation.ADD_TEAM_MEMBER,
                        VercelOperation.GET_TEAM_MEMBER,
                        VercelOperation.UPDATE_TEAM_MEMBER,
                        VercelOperation.REMOVE_TEAM_MEMBER,
                        VercelOperation.LIST_TEAM_MEMBERS,
                        
                        # Access Groups
                        VercelOperation.CREATE_ACCESS_GROUP,
                        VercelOperation.GET_ACCESS_GROUP,
                        VercelOperation.UPDATE_ACCESS_GROUP,
                        VercelOperation.DELETE_ACCESS_GROUP,
                        VercelOperation.LIST_ACCESS_GROUPS,
                        
                        # Certificates
                        VercelOperation.GET_CERTIFICATE,
                        VercelOperation.ISSUE_CERTIFICATE,
                        VercelOperation.DELETE_CERTIFICATE,
                        VercelOperation.LIST_CERTIFICATES,
                        
                        # Webhooks
                        VercelOperation.CREATE_WEBHOOK,
                        VercelOperation.GET_WEBHOOK,
                        VercelOperation.UPDATE_WEBHOOK,
                        VercelOperation.DELETE_WEBHOOK,
                        VercelOperation.LIST_WEBHOOKS,
                        
                        # Edge Config
                        VercelOperation.CREATE_EDGE_CONFIG,
                        VercelOperation.GET_EDGE_CONFIG,
                        VercelOperation.UPDATE_EDGE_CONFIG,
                        VercelOperation.DELETE_EDGE_CONFIG,
                        VercelOperation.LIST_EDGE_CONFIGS,
                        VercelOperation.GET_EDGE_CONFIG_ITEMS,
                        VercelOperation.UPSERT_EDGE_CONFIG_ITEMS,
                        
                        # Artifacts
                        VercelOperation.UPLOAD_ARTIFACT,
                        VercelOperation.GET_ARTIFACT,
                        VercelOperation.DELETE_ARTIFACT,
                        VercelOperation.LIST_ARTIFACTS,
                        
                        # Checks
                        VercelOperation.CREATE_CHECK,
                        VercelOperation.GET_CHECK,
                        VercelOperation.UPDATE_CHECK,
                        VercelOperation.LIST_CHECKS,
                        
                        # Aliases
                        VercelOperation.CREATE_ALIAS,
                        VercelOperation.GET_ALIAS,
                        VercelOperation.DELETE_ALIAS,
                        VercelOperation.LIST_ALIASES,
                        
                        # Secrets
                        VercelOperation.CREATE_SECRET,
                        VercelOperation.GET_SECRET,
                        VercelOperation.RENAME_SECRET,
                        VercelOperation.DELETE_SECRET,
                        VercelOperation.LIST_SECRETS,
                        
                        # Analytics
                        VercelOperation.GET_USAGE,
                        VercelOperation.GET_ANALYTICS
                    ]
                ),
                NodeParameter(
                    name="auth_type",
                    type=NodeParameterType.STRING,
                    description="Authentication type",
                    required=False,
                    default=VercelAuthType.BEARER_TOKEN,
                    options=[
                        VercelAuthType.BEARER_TOKEN,
                        VercelAuthType.OAUTH2
                    ]
                ),
                
                # Authentication
                NodeParameter(
                    name="api_token",
                    type=NodeParameterType.STRING,
                    description="Vercel API access token",
                    required=True,
                    sensitive=True
                ),
                NodeParameter(
                    name="team_id",
                    type=NodeParameterType.STRING,
                    description="Team ID (for team resources)",
                    required=False
                ),
                
                # Resource identifiers
                NodeParameter(
                    name="project_id",
                    type=NodeParameterType.STRING,
                    description="Project ID or name",
                    required=False
                ),
                NodeParameter(
                    name="deployment_id",
                    type=NodeParameterType.STRING,
                    description="Deployment ID",
                    required=False
                ),
                NodeParameter(
                    name="domain_name",
                    type=NodeParameterType.STRING,
                    description="Domain name",
                    required=False
                ),
                NodeParameter(
                    name="record_id",
                    type=NodeParameterType.STRING,
                    description="DNS record ID",
                    required=False
                ),
                NodeParameter(
                    name="env_var_id",
                    type=NodeParameterType.STRING,
                    description="Environment variable ID",
                    required=False
                ),
                NodeParameter(
                    name="function_id",
                    type=NodeParameterType.STRING,
                    description="Function ID",
                    required=False
                ),
                NodeParameter(
                    name="member_uid",
                    type=NodeParameterType.STRING,
                    description="Team member UID",
                    required=False
                ),
                NodeParameter(
                    name="webhook_id",
                    type=NodeParameterType.STRING,
                    description="Webhook ID",
                    required=False
                ),
                NodeParameter(
                    name="edge_config_id",
                    type=NodeParameterType.STRING,
                    description="Edge config ID",
                    required=False
                ),
                NodeParameter(
                    name="secret_name",
                    type=NodeParameterType.STRING,
                    description="Secret name",
                    required=False
                ),
                
                # Resource data
                NodeParameter(
                    name="resource_data",
                    type=NodeParameterType.OBJECT,
                    description="Resource data for create/update operations",
                    required=False
                ),
                
                # Project-specific parameters
                NodeParameter(
                    name="project_name",
                    type=NodeParameterType.STRING,
                    description="Project name",
                    required=False
                ),
                NodeParameter(
                    name="framework",
                    type=NodeParameterType.STRING,
                    description="Project framework",
                    required=False,
                    options=[
                        VercelFramework.NEXTJS,
                        VercelFramework.REACT,
                        VercelFramework.VUE,
                        VercelFramework.NUXT,
                        VercelFramework.GATSBY,
                        VercelFramework.ANGULAR,
                        VercelFramework.SVELTE,
                        VercelFramework.STATIC,
                        VercelFramework.OTHER
                    ]
                ),
                NodeParameter(
                    name="git_repository",
                    type=NodeParameterType.OBJECT,
                    description="Git repository configuration",
                    required=False
                ),
                
                # Deployment parameters
                NodeParameter(
                    name="deployment_files",
                    type=NodeParameterType.ARRAY,
                    description="Files for deployment",
                    required=False
                ),
                NodeParameter(
                    name="build_env",
                    type=NodeParameterType.OBJECT,
                    description="Build environment variables",
                    required=False
                ),
                NodeParameter(
                    name="regions",
                    type=NodeParameterType.ARRAY,
                    description="Deployment regions",
                    required=False
                ),
                
                # Environment variable parameters
                NodeParameter(
                    name="env_key",
                    type=NodeParameterType.STRING,
                    description="Environment variable key",
                    required=False
                ),
                NodeParameter(
                    name="env_value",
                    type=NodeParameterType.STRING,
                    description="Environment variable value",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="env_target",
                    type=NodeParameterType.ARRAY,
                    description="Environment variable targets",
                    required=False,
                    default=[VercelEnvironment.PRODUCTION]
                ),
                NodeParameter(
                    name="env_vars",
                    type=NodeParameterType.ARRAY,
                    description="Bulk environment variables",
                    required=False
                ),
                
                # DNS parameters
                NodeParameter(
                    name="record_type",
                    type=NodeParameterType.STRING,
                    description="DNS record type",
                    required=False,
                    options=["A", "AAAA", "CNAME", "MX", "TXT", "SRV"]
                ),
                NodeParameter(
                    name="record_name",
                    type=NodeParameterType.STRING,
                    description="DNS record name",
                    required=False
                ),
                NodeParameter(
                    name="record_value",
                    type=NodeParameterType.STRING,
                    description="DNS record value",
                    required=False
                ),
                NodeParameter(
                    name="record_ttl",
                    type=NodeParameterType.INTEGER,
                    description="DNS record TTL",
                    required=False,
                    default=60
                ),
                
                # Query parameters
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.INTEGER,
                    description="Number of results to return",
                    required=False,
                    default=20
                ),
                NodeParameter(
                    name="since",
                    type=NodeParameterType.STRING,
                    description="Return results since timestamp",
                    required=False
                ),
                NodeParameter(
                    name="until",
                    type=NodeParameterType.STRING,
                    description="Return results until timestamp",
                    required=False
                ),
                
                # Filters
                NodeParameter(
                    name="state",
                    type=NodeParameterType.STRING,
                    description="Deployment state filter",
                    required=False,
                    options=["BUILDING", "ERROR", "INITIALIZING", "QUEUED", "READY", "CANCELED"]
                ),
                NodeParameter(
                    name="target",
                    type=NodeParameterType.STRING,
                    description="Deployment target filter",
                    required=False,
                    options=[VercelEnvironment.PRODUCTION, VercelEnvironment.PREVIEW, VercelEnvironment.DEVELOPMENT]
                )
            ],
            outputs=[
                NodeParameter(
                    name="success",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether the operation was successful"
                ),
                NodeParameter(
                    name="data",
                    type=NodeParameterType.OBJECT,
                    description="Response data from Vercel API"
                ),
                NodeParameter(
                    name="resource_id",
                    type=NodeParameterType.STRING,
                    description="ID of created/updated resource"
                ),
                NodeParameter(
                    name="deployment_url",
                    type=NodeParameterType.STRING,
                    description="Deployment URL (for deployment operations)"
                ),
                NodeParameter(
                    name="total_results",
                    type=NodeParameterType.INTEGER,
                    description="Total number of results"
                ),
                NodeParameter(
                    name="pagination",
                    type=NodeParameterType.OBJECT,
                    description="Pagination information"
                ),
                NodeParameter(
                    name="error_message",
                    type=NodeParameterType.STRING,
                    description="Error message if operation failed"
                ),
                NodeParameter(
                    name="error_code",
                    type=NodeParameterType.STRING,
                    description="Error code if operation failed"
                ),
                NodeParameter(
                    name="rate_limit_remaining",
                    type=NodeParameterType.INTEGER,
                    description="Remaining API quota"
                ),
                NodeParameter(
                    name="rate_limit_reset",
                    type=NodeParameterType.STRING,
                    description="Rate limit reset timestamp"
                ),
                NodeParameter(
                    name="response_headers",
                    type=NodeParameterType.OBJECT,
                    description="HTTP response headers"
                )
            ],
            metadata={
                "category": "deployment",
                "tags": ["vercel", "deployment", "hosting", "serverless", "edge", "domains"],
                "cost_per_execution": 0.001,
                "rate_limit": "Per-endpoint rate limiting with headers"
            }
        )
    
    async def _ensure_session(self):
        """Ensure aiohttp session is available."""
        if self.session is None:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": "VercelNode/1.0"}
            )
    
    async def _cleanup_session(self):
        """Clean up aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _check_rate_limit(self, response_headers: Dict[str, str]):
        """Check and update rate limit status from response headers."""
        self.rate_limit_remaining = response_headers.get('x-ratelimit-remaining')
        self.rate_limit_reset = response_headers.get('x-ratelimit-reset')
        
        if self.rate_limit_remaining:
            self.rate_limit_remaining = int(self.rate_limit_remaining)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Dict[str, str],
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Make HTTP request to Vercel API."""
        await self._ensure_session()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            kwargs = {"headers": headers}
            if data:
                kwargs["json"] = data
            if params:
                kwargs["params"] = params
            
            async with self.session.request(method, url, **kwargs) as response:
                response_headers = dict(response.headers)
                self._check_rate_limit(response_headers)
                
                if response.status >= 400:
                    error_data = await response.json()
                    return {
                        "error": True,
                        "error_code": error_data.get("error", {}).get("code", str(response.status)),
                        "error_message": error_data.get("error", {}).get("message", "Unknown error"),
                        "error_details": error_data
                    }, response_headers
                
                response_data = await response.json()
                return response_data, response_headers
                
        except asyncio.TimeoutError:
            return {
                "error": True,
                "error_code": "TIMEOUT",
                "error_message": "Request timeout"
            }, {}
        except Exception as e:
            return {
                "error": True,
                "error_code": "REQUEST_ERROR",
                "error_message": str(e)
            }, {}
    
    def _build_headers(self, api_token: str) -> Dict[str, str]:
        """Build headers for Vercel API requests."""
        return {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute Vercel API operation."""
        try:
            operation = kwargs.get("operation")
            if not operation:
                raise NodeValidationError("Operation parameter is required")
            
            # Extract authentication parameters
            api_token = kwargs.get("api_token")
            if not api_token:
                raise NodeValidationError("API token is required")
            
            team_id = kwargs.get("team_id")
            
            # Build headers
            headers = self._build_headers(api_token)
            
            # Build query parameters
            query_params = VercelHelper.build_query_params(
                limit=kwargs.get("limit"),
                since=kwargs.get("since"),
                until=kwargs.get("until"),
                team_id=team_id
            )
            
            # Execute specific operation
            if operation == VercelOperation.GET_USER:
                return await self._handle_get_user(headers, query_params)
            elif operation == VercelOperation.UPDATE_USER:
                return await self._handle_update_user(headers, kwargs, query_params)
            
            # Project operations
            elif operation == VercelOperation.CREATE_PROJECT:
                return await self._handle_create_project(headers, kwargs, query_params)
            elif operation == VercelOperation.GET_PROJECT:
                return await self._handle_get_project(headers, kwargs, query_params)
            elif operation == VercelOperation.UPDATE_PROJECT:
                return await self._handle_update_project(headers, kwargs, query_params)
            elif operation == VercelOperation.DELETE_PROJECT:
                return await self._handle_delete_project(headers, kwargs, query_params)
            elif operation == VercelOperation.LIST_PROJECTS:
                return await self._handle_list_projects(headers, query_params)
            elif operation in [VercelOperation.PAUSE_PROJECT, VercelOperation.UNPAUSE_PROJECT]:
                return await self._handle_project_status_change(headers, kwargs, query_params, operation)
            
            # Deployment operations
            elif operation == VercelOperation.CREATE_DEPLOYMENT:
                return await self._handle_create_deployment(headers, kwargs, query_params)
            elif operation == VercelOperation.GET_DEPLOYMENT:
                return await self._handle_get_deployment(headers, kwargs, query_params)
            elif operation == VercelOperation.DELETE_DEPLOYMENT:
                return await self._handle_delete_deployment(headers, kwargs, query_params)
            elif operation == VercelOperation.LIST_DEPLOYMENTS:
                return await self._handle_list_deployments(headers, kwargs, query_params)
            elif operation == VercelOperation.CANCEL_DEPLOYMENT:
                return await self._handle_cancel_deployment(headers, kwargs, query_params)
            
            # Environment variable operations
            elif operation == VercelOperation.CREATE_ENV_VAR:
                return await self._handle_create_env_var(headers, kwargs, query_params)
            elif operation == VercelOperation.GET_ENV_VAR:
                return await self._handle_get_env_var(headers, kwargs, query_params)
            elif operation == VercelOperation.UPDATE_ENV_VAR:
                return await self._handle_update_env_var(headers, kwargs, query_params)
            elif operation == VercelOperation.DELETE_ENV_VAR:
                return await self._handle_delete_env_var(headers, kwargs, query_params)
            elif operation == VercelOperation.LIST_ENV_VARS:
                return await self._handle_list_env_vars(headers, kwargs, query_params)
            elif operation == VercelOperation.BULK_CREATE_ENV_VARS:
                return await self._handle_bulk_create_env_vars(headers, kwargs, query_params)
            
            # Domain operations
            elif operation == VercelOperation.CREATE_DOMAIN:
                return await self._handle_create_domain(headers, kwargs, query_params)
            elif operation == VercelOperation.GET_DOMAIN:
                return await self._handle_get_domain(headers, kwargs, query_params)
            elif operation == VercelOperation.DELETE_DOMAIN:
                return await self._handle_delete_domain(headers, kwargs, query_params)
            elif operation == VercelOperation.LIST_DOMAINS:
                return await self._handle_list_domains(headers, query_params)
            
            # DNS operations
            elif operation == VercelOperation.CREATE_DNS_RECORD:
                return await self._handle_create_dns_record(headers, kwargs, query_params)
            elif operation == VercelOperation.LIST_DNS_RECORDS:
                return await self._handle_list_dns_records(headers, kwargs, query_params)
            
            # Team operations
            elif operation == VercelOperation.LIST_TEAMS:
                return await self._handle_list_teams(headers, query_params)
            elif operation == VercelOperation.GET_TEAM:
                return await self._handle_get_team(headers, kwargs, query_params)
            
            else:
                raise NodeValidationError(f"Unsupported operation: {operation}")
                
        except Exception as e:
            logger.error(f"Vercel API operation failed: {str(e)}")
            return {
                "success": False,
                "error_message": str(e),
                "error_code": "EXECUTION_ERROR"
            }
        finally:
            await self._cleanup_session()
    
    # User operations
    async def _handle_get_user(self, headers: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get user operation."""
        endpoint = "v2/user"
        response_data, response_headers = await self._make_request("GET", endpoint, headers, params=params)
        
        if response_data.get("error"):
            return {
                "success": False,
                "error_message": response_data["error_message"],
                "error_code": response_data["error_code"],
                "response_headers": response_headers
            }
        
        return {
            "success": True,
            "data": response_data,
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset,
            "response_headers": response_headers
        }
    
    async def _handle_update_user(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update user operation."""
        resource_data = kwargs.get("resource_data")
        if not resource_data:
            return {
                "success": False,
                "error_message": "resource_data is required for update_user",
                "error_code": "MISSING_PARAMETER"
            }
        
        endpoint = "v2/user"
        response_data, response_headers = await self._make_request("PATCH", endpoint, headers, resource_data, params)
        
        if response_data.get("error"):
            return {
                "success": False,
                "error_message": response_data["error_message"],
                "error_code": response_data["error_code"],
                "response_headers": response_headers
            }
        
        return {
            "success": True,
            "data": response_data,
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset,
            "response_headers": response_headers
        }
    
    # Project operations
    async def _handle_create_project(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create project operation."""
        resource_data = kwargs.get("resource_data")
        if not resource_data and not kwargs.get("project_name"):
            return {
                "success": False,
                "error_message": "resource_data or project_name is required for create_project",
                "error_code": "MISSING_PARAMETER"
            }
        
        if not resource_data:
            resource_data = {
                "name": kwargs.get("project_name"),
                "framework": kwargs.get("framework"),
                "gitRepository": kwargs.get("git_repository")
            }
            # Remove None values
            resource_data = {k: v for k, v in resource_data.items() if v is not None}
        
        endpoint = "v9/projects"
        response_data, response_headers = await self._make_request("POST", endpoint, headers, resource_data, params)
        
        if response_data.get("error"):
            return {
                "success": False,
                "error_message": response_data["error_message"],
                "error_code": response_data["error_code"],
                "response_headers": response_headers
            }
        
        return {
            "success": True,
            "data": response_data,
            "resource_id": response_data.get("id"),
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset,
            "response_headers": response_headers
        }
    
    async def _handle_get_project(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get project operation."""
        project_id = kwargs.get("project_id")
        if not project_id:
            return {
                "success": False,
                "error_message": "project_id is required for get_project",
                "error_code": "MISSING_PARAMETER"
            }
        
        endpoint = f"v9/projects/{project_id}"
        response_data, response_headers = await self._make_request("GET", endpoint, headers, params=params)
        
        if response_data.get("error"):
            return {
                "success": False,
                "error_message": response_data["error_message"],
                "error_code": response_data["error_code"],
                "response_headers": response_headers
            }
        
        return {
            "success": True,
            "data": response_data,
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset,
            "response_headers": response_headers
        }
    
    async def _handle_list_projects(self, headers: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list projects operation."""
        endpoint = "v9/projects"
        response_data, response_headers = await self._make_request("GET", endpoint, headers, params=params)
        
        if response_data.get("error"):
            return {
                "success": False,
                "error_message": response_data["error_message"],
                "error_code": response_data["error_code"],
                "response_headers": response_headers
            }
        
        projects = response_data.get("projects", [])
        pagination = response_data.get("pagination", {})
        
        return {
            "success": True,
            "data": response_data,
            "total_results": len(projects),
            "pagination": pagination,
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset,
            "response_headers": response_headers
        }
    
    # Environment variable operations
    async def _handle_create_env_var(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create environment variable operation."""
        project_id = kwargs.get("project_id")
        if not project_id:
            return {
                "success": False,
                "error_message": "project_id is required for create_env_var",
                "error_code": "MISSING_PARAMETER"
            }
        
        env_key = kwargs.get("env_key")
        env_value = kwargs.get("env_value")
        env_target = kwargs.get("env_target", [VercelEnvironment.PRODUCTION])
        
        if not env_key or not env_value:
            return {
                "success": False,
                "error_message": "env_key and env_value are required for create_env_var",
                "error_code": "MISSING_PARAMETER"
            }
        
        # Validate environment variable
        if not VercelHelper.validate_env_var_key(env_key):
            return {
                "success": False,
                "error_message": "Invalid environment variable key format",
                "error_code": "INVALID_KEY"
            }
        
        if not VercelHelper.validate_env_var_value(env_value):
            return {
                "success": False,
                "error_message": "Environment variable value exceeds maximum length",
                "error_code": "INVALID_VALUE"
            }
        
        resource_data = VercelHelper.build_env_var_payload(
            key=env_key,
            value=env_value,
            target=env_target
        )
        
        endpoint = f"v10/projects/{project_id}/env"
        response_data, response_headers = await self._make_request("POST", endpoint, headers, resource_data, params)
        
        if response_data.get("error"):
            return {
                "success": False,
                "error_message": response_data["error_message"],
                "error_code": response_data["error_code"],
                "response_headers": response_headers
            }
        
        return {
            "success": True,
            "data": response_data,
            "resource_id": response_data.get("id"),
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset,
            "response_headers": response_headers
        }
    
    async def _handle_list_env_vars(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list environment variables operation."""
        project_id = kwargs.get("project_id")
        if not project_id:
            return {
                "success": False,
                "error_message": "project_id is required for list_env_vars",
                "error_code": "MISSING_PARAMETER"
            }
        
        endpoint = f"v9/projects/{project_id}/env"
        response_data, response_headers = await self._make_request("GET", endpoint, headers, params=params)
        
        if response_data.get("error"):
            return {
                "success": False,
                "error_message": response_data["error_message"],
                "error_code": response_data["error_code"],
                "response_headers": response_headers
            }
        
        env_vars = response_data.get("envs", [])
        
        return {
            "success": True,
            "data": response_data,
            "total_results": len(env_vars),
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset,
            "response_headers": response_headers
        }
    
    # Deployment operations
    async def _handle_create_deployment(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create deployment operation."""
        resource_data = kwargs.get("resource_data")
        project_name = kwargs.get("project_name")
        
        if not resource_data and not project_name:
            return {
                "success": False,
                "error_message": "resource_data or project_name is required for create_deployment",
                "error_code": "MISSING_PARAMETER"
            }
        
        if not resource_data:
            resource_data = VercelHelper.build_deployment_payload(
                name=project_name,
                files=kwargs.get("deployment_files"),
                env=kwargs.get("build_env"),
                regions=kwargs.get("regions")
            )
        
        endpoint = "v13/deployments"
        response_data, response_headers = await self._make_request("POST", endpoint, headers, resource_data, params)
        
        if response_data.get("error"):
            return {
                "success": False,
                "error_message": response_data["error_message"],
                "error_code": response_data["error_code"],
                "response_headers": response_headers
            }
        
        return {
            "success": True,
            "data": response_data,
            "resource_id": response_data.get("id"),
            "deployment_url": response_data.get("url"),
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset,
            "response_headers": response_headers
        }
    
    async def _handle_list_deployments(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list deployments operation."""
        # Add deployment-specific filters to params
        if kwargs.get("state"):
            params["state"] = kwargs["state"]
        if kwargs.get("target"):
            params["target"] = kwargs["target"]
        
        endpoint = "v6/deployments"
        response_data, response_headers = await self._make_request("GET", endpoint, headers, params=params)
        
        if response_data.get("error"):
            return {
                "success": False,
                "error_message": response_data["error_message"],
                "error_code": response_data["error_code"],
                "response_headers": response_headers
            }
        
        deployments = response_data.get("deployments", [])
        pagination = response_data.get("pagination", {})
        
        return {
            "success": True,
            "data": response_data,
            "total_results": len(deployments),
            "pagination": pagination,
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset,
            "response_headers": response_headers
        }
    
    # Additional placeholder handlers for remaining operations
    async def _handle_update_project(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_delete_project(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_project_status_change(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_get_deployment(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_delete_deployment(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_cancel_deployment(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_get_env_var(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_update_env_var(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_delete_env_var(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_bulk_create_env_vars(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_create_domain(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_get_domain(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_delete_domain(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_list_domains(self, headers: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_create_dns_record(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_list_dns_records(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_list_teams(self, headers: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}
    
    async def _handle_get_team(self, headers: Dict[str, str], kwargs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error_message": "Operation not implemented yet", "error_code": "NOT_IMPLEMENTED"}

if __name__ == "__main__":
    import asyncio
    
    async def test_vercel_node():
        """Test Vercel node functionality."""
        node = VercelNode()
        
        # Test schema
        schema = node.schema
        print(f"Node: {schema.name}")
        print(f"Parameters: {len(schema.parameters)}")
        print(f"Outputs: {len(schema.outputs)}")
        
        # Test operation (would need real API token)
        # result = await node.execute(
        #     operation=VercelOperation.GET_USER,
        #     api_token="your_api_token"
        # )
        # print(f"Result: {result}")
        
        print("Vercel node test completed")
    
    asyncio.run(test_vercel_node())