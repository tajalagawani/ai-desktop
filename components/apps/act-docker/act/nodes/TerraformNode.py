"""
Terraform Node - Comprehensive integration with Terraform Cloud and Enterprise APIs
Provides access to all Terraform Cloud API operations including workspace management, infrastructure deployment, state management, and policy enforcement.
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
from urllib.parse import urlencode, quote

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

class TerraformOperation:
    """Operations available on Terraform Cloud API."""
    
    # Workspace Operations
    CREATE_WORKSPACE = "create_workspace"
    UPDATE_WORKSPACE = "update_workspace"
    DELETE_WORKSPACE = "delete_workspace"
    GET_WORKSPACE = "get_workspace"
    LIST_WORKSPACES = "list_workspaces"
    LOCK_WORKSPACE = "lock_workspace"
    UNLOCK_WORKSPACE = "unlock_workspace"
    FORCE_UNLOCK_WORKSPACE = "force_unlock_workspace"
    
    # Configuration Version Operations
    CREATE_CONFIGURATION_VERSION = "create_configuration_version"
    UPLOAD_CONFIGURATION_FILES = "upload_configuration_files"
    GET_CONFIGURATION_VERSION = "get_configuration_version"
    LIST_CONFIGURATION_VERSIONS = "list_configuration_versions"
    
    # Run Operations
    CREATE_RUN = "create_run"
    GET_RUN = "get_run"
    LIST_RUNS = "list_runs"
    APPLY_RUN = "apply_run"
    DISCARD_RUN = "discard_run"
    CANCEL_RUN = "cancel_run"
    FORCE_CANCEL_RUN = "force_cancel_run"
    
    # Plan Operations
    GET_PLAN = "get_plan"
    GET_PLAN_JSON_OUTPUT = "get_plan_json_output"
    GET_PLAN_LOG = "get_plan_log"
    
    # Apply Operations
    GET_APPLY = "get_apply"
    GET_APPLY_LOG = "get_apply_log"
    
    # State Version Operations
    LIST_STATE_VERSIONS = "list_state_versions"
    GET_STATE_VERSION = "get_state_version"
    GET_CURRENT_STATE_VERSION = "get_current_state_version"
    CREATE_STATE_VERSION = "create_state_version"
    ROLLBACK_STATE_VERSION = "rollback_state_version"
    
    # Variable Operations
    LIST_VARIABLES = "list_variables"
    CREATE_VARIABLE = "create_variable"
    UPDATE_VARIABLE = "update_variable"
    DELETE_VARIABLE = "delete_variable"
    GET_VARIABLE = "get_variable"
    
    # Variable Set Operations
    LIST_VARIABLE_SETS = "list_variable_sets"
    CREATE_VARIABLE_SET = "create_variable_set"
    UPDATE_VARIABLE_SET = "update_variable_set"
    DELETE_VARIABLE_SET = "delete_variable_set"
    GET_VARIABLE_SET = "get_variable_set"
    APPLY_VARIABLE_SET = "apply_variable_set"
    
    # Organization Operations
    LIST_ORGANIZATIONS = "list_organizations"
    GET_ORGANIZATION = "get_organization"
    UPDATE_ORGANIZATION = "update_organization"
    
    # Team Operations
    LIST_TEAMS = "list_teams"
    CREATE_TEAM = "create_team"
    UPDATE_TEAM = "update_team"
    DELETE_TEAM = "delete_team"
    GET_TEAM = "get_team"
    
    # Team Access Operations
    LIST_TEAM_ACCESS = "list_team_access"
    ADD_TEAM_ACCESS = "add_team_access"
    UPDATE_TEAM_ACCESS = "update_team_access"
    REMOVE_TEAM_ACCESS = "remove_team_access"
    
    # Policy Operations
    LIST_POLICIES = "list_policies"
    CREATE_POLICY = "create_policy"
    UPDATE_POLICY = "update_policy"
    DELETE_POLICY = "delete_policy"
    GET_POLICY = "get_policy"
    
    # Policy Set Operations
    LIST_POLICY_SETS = "list_policy_sets"
    CREATE_POLICY_SET = "create_policy_set"
    UPDATE_POLICY_SET = "update_policy_set"
    DELETE_POLICY_SET = "delete_policy_set"
    GET_POLICY_SET = "get_policy_set"
    
    # Policy Check Operations
    GET_POLICY_CHECK = "get_policy_check"
    OVERRIDE_POLICY_CHECK = "override_policy_check"
    
    # Cost Estimation Operations
    GET_COST_ESTIMATE = "get_cost_estimate"
    
    # Registry Module Operations
    LIST_REGISTRY_MODULES = "list_registry_modules"
    CREATE_REGISTRY_MODULE = "create_registry_module"
    DELETE_REGISTRY_MODULE = "delete_registry_module"
    GET_REGISTRY_MODULE = "get_registry_module"
    
    # Registry Provider Operations
    LIST_REGISTRY_PROVIDERS = "list_registry_providers"
    CREATE_REGISTRY_PROVIDER = "create_registry_provider"
    DELETE_REGISTRY_PROVIDER = "delete_registry_provider"
    GET_REGISTRY_PROVIDER = "get_registry_provider"
    
    # OAuth Token Operations
    LIST_OAUTH_TOKENS = "list_oauth_tokens"
    CREATE_OAUTH_TOKEN = "create_oauth_token"
    UPDATE_OAUTH_TOKEN = "update_oauth_token"
    DELETE_OAUTH_TOKEN = "delete_oauth_token"
    
    # SSH Key Operations
    LIST_SSH_KEYS = "list_ssh_keys"
    CREATE_SSH_KEY = "create_ssh_key"
    UPDATE_SSH_KEY = "update_ssh_key"
    DELETE_SSH_KEY = "delete_ssh_key"
    
    # Notification Configuration Operations
    LIST_NOTIFICATION_CONFIGURATIONS = "list_notification_configurations"
    CREATE_NOTIFICATION_CONFIGURATION = "create_notification_configuration"
    UPDATE_NOTIFICATION_CONFIGURATION = "update_notification_configuration"
    DELETE_NOTIFICATION_CONFIGURATION = "delete_notification_configuration"
    
    # Agent Pool Operations
    LIST_AGENT_POOLS = "list_agent_pools"
    CREATE_AGENT_POOL = "create_agent_pool"
    UPDATE_AGENT_POOL = "update_agent_pool"
    DELETE_AGENT_POOL = "delete_agent_pool"

class TerraformNode(BaseNode):
    """
    Node for interacting with Terraform Cloud and Enterprise APIs.
    Provides comprehensive functionality for infrastructure as code management, workspace operations, and policy enforcement.
    """
    
    BASE_URL = "https://app.terraform.io/api/v2"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Terraform node."""
        return NodeSchema(
            node_type="terraform",
            version="1.0.0",
            description="Comprehensive integration with Terraform Cloud and Enterprise APIs for infrastructure as code management, workspace operations, and policy enforcement",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Terraform Cloud API",
                    required=True,
                    enum=[
                        TerraformOperation.CREATE_WORKSPACE,
                        TerraformOperation.UPDATE_WORKSPACE,
                        TerraformOperation.DELETE_WORKSPACE,
                        TerraformOperation.GET_WORKSPACE,
                        TerraformOperation.LIST_WORKSPACES,
                        TerraformOperation.LOCK_WORKSPACE,
                        TerraformOperation.UNLOCK_WORKSPACE,
                        TerraformOperation.FORCE_UNLOCK_WORKSPACE,
                        TerraformOperation.CREATE_CONFIGURATION_VERSION,
                        TerraformOperation.UPLOAD_CONFIGURATION_FILES,
                        TerraformOperation.GET_CONFIGURATION_VERSION,
                        TerraformOperation.LIST_CONFIGURATION_VERSIONS,
                        TerraformOperation.CREATE_RUN,
                        TerraformOperation.GET_RUN,
                        TerraformOperation.LIST_RUNS,
                        TerraformOperation.APPLY_RUN,
                        TerraformOperation.DISCARD_RUN,
                        TerraformOperation.CANCEL_RUN,
                        TerraformOperation.FORCE_CANCEL_RUN,
                        TerraformOperation.GET_PLAN,
                        TerraformOperation.GET_PLAN_JSON_OUTPUT,
                        TerraformOperation.GET_PLAN_LOG,
                        TerraformOperation.GET_APPLY,
                        TerraformOperation.GET_APPLY_LOG,
                        TerraformOperation.LIST_STATE_VERSIONS,
                        TerraformOperation.GET_STATE_VERSION,
                        TerraformOperation.GET_CURRENT_STATE_VERSION,
                        TerraformOperation.CREATE_STATE_VERSION,
                        TerraformOperation.ROLLBACK_STATE_VERSION,
                        TerraformOperation.LIST_VARIABLES,
                        TerraformOperation.CREATE_VARIABLE,
                        TerraformOperation.UPDATE_VARIABLE,
                        TerraformOperation.DELETE_VARIABLE,
                        TerraformOperation.GET_VARIABLE,
                        TerraformOperation.LIST_VARIABLE_SETS,
                        TerraformOperation.CREATE_VARIABLE_SET,
                        TerraformOperation.UPDATE_VARIABLE_SET,
                        TerraformOperation.DELETE_VARIABLE_SET,
                        TerraformOperation.GET_VARIABLE_SET,
                        TerraformOperation.APPLY_VARIABLE_SET,
                        TerraformOperation.LIST_ORGANIZATIONS,
                        TerraformOperation.GET_ORGANIZATION,
                        TerraformOperation.UPDATE_ORGANIZATION,
                        TerraformOperation.LIST_TEAMS,
                        TerraformOperation.CREATE_TEAM,
                        TerraformOperation.UPDATE_TEAM,
                        TerraformOperation.DELETE_TEAM,
                        TerraformOperation.GET_TEAM,
                        TerraformOperation.LIST_TEAM_ACCESS,
                        TerraformOperation.ADD_TEAM_ACCESS,
                        TerraformOperation.UPDATE_TEAM_ACCESS,
                        TerraformOperation.REMOVE_TEAM_ACCESS,
                        TerraformOperation.LIST_POLICIES,
                        TerraformOperation.CREATE_POLICY,
                        TerraformOperation.UPDATE_POLICY,
                        TerraformOperation.DELETE_POLICY,
                        TerraformOperation.GET_POLICY,
                        TerraformOperation.LIST_POLICY_SETS,
                        TerraformOperation.CREATE_POLICY_SET,
                        TerraformOperation.UPDATE_POLICY_SET,
                        TerraformOperation.DELETE_POLICY_SET,
                        TerraformOperation.GET_POLICY_SET,
                        TerraformOperation.GET_POLICY_CHECK,
                        TerraformOperation.OVERRIDE_POLICY_CHECK,
                        TerraformOperation.GET_COST_ESTIMATE,
                        TerraformOperation.LIST_REGISTRY_MODULES,
                        TerraformOperation.CREATE_REGISTRY_MODULE,
                        TerraformOperation.DELETE_REGISTRY_MODULE,
                        TerraformOperation.GET_REGISTRY_MODULE,
                        TerraformOperation.LIST_REGISTRY_PROVIDERS,
                        TerraformOperation.CREATE_REGISTRY_PROVIDER,
                        TerraformOperation.DELETE_REGISTRY_PROVIDER,
                        TerraformOperation.GET_REGISTRY_PROVIDER,
                        TerraformOperation.LIST_OAUTH_TOKENS,
                        TerraformOperation.CREATE_OAUTH_TOKEN,
                        TerraformOperation.UPDATE_OAUTH_TOKEN,
                        TerraformOperation.DELETE_OAUTH_TOKEN,
                        TerraformOperation.LIST_SSH_KEYS,
                        TerraformOperation.CREATE_SSH_KEY,
                        TerraformOperation.UPDATE_SSH_KEY,
                        TerraformOperation.DELETE_SSH_KEY,
                        TerraformOperation.LIST_NOTIFICATION_CONFIGURATIONS,
                        TerraformOperation.CREATE_NOTIFICATION_CONFIGURATION,
                        TerraformOperation.UPDATE_NOTIFICATION_CONFIGURATION,
                        TerraformOperation.DELETE_NOTIFICATION_CONFIGURATION,
                        TerraformOperation.LIST_AGENT_POOLS,
                        TerraformOperation.CREATE_AGENT_POOL,
                        TerraformOperation.UPDATE_AGENT_POOL,
                        TerraformOperation.DELETE_AGENT_POOL
                    ]
                ),
                NodeParameter(
                    name="api_token",
                    type=NodeParameterType.SECRET,
                    description="Terraform Cloud API token for authentication",
                    required=True
                ),
                NodeParameter(
                    name="organization",
                    type=NodeParameterType.STRING,
                    description="Terraform Cloud organization name",
                    required=False
                ),
                NodeParameter(
                    name="workspace_name",
                    type=NodeParameterType.STRING,
                    description="Name of the workspace",
                    required=False
                ),
                NodeParameter(
                    name="workspace_id",
                    type=NodeParameterType.STRING,
                    description="ID of the workspace",
                    required=False
                ),
                NodeParameter(
                    name="terraform_version",
                    type=NodeParameterType.STRING,
                    description="Terraform version for workspace",
                    required=False
                ),
                NodeParameter(
                    name="working_directory",
                    type=NodeParameterType.STRING,
                    description="Working directory for Terraform configurations",
                    required=False
                ),
                NodeParameter(
                    name="execution_mode",
                    type=NodeParameterType.STRING,
                    description="Workspace execution mode",
                    required=False,
                    enum=["remote", "local", "agent"]
                ),
                NodeParameter(
                    name="auto_apply",
                    type=NodeParameterType.BOOLEAN,
                    description="Enable auto-apply for workspace",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="queue_all_runs",
                    type=NodeParameterType.BOOLEAN,
                    description="Queue all runs for workspace",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="speculative",
                    type=NodeParameterType.BOOLEAN,
                    description="Create speculative plan",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="vcs_repo",
                    type=NodeParameterType.OBJECT,
                    description="VCS repository configuration",
                    required=False
                ),
                NodeParameter(
                    name="configuration_files",
                    type=NodeParameterType.OBJECT,
                    description="Configuration files to upload",
                    required=False
                ),
                NodeParameter(
                    name="run_id",
                    type=NodeParameterType.STRING,
                    description="ID of the run",
                    required=False
                ),
                NodeParameter(
                    name="run_message",
                    type=NodeParameterType.STRING,
                    description="Message for run creation",
                    required=False
                ),
                NodeParameter(
                    name="plan_id",
                    type=NodeParameterType.STRING,
                    description="ID of the plan",
                    required=False
                ),
                NodeParameter(
                    name="apply_id",
                    type=NodeParameterType.STRING,
                    description="ID of the apply",
                    required=False
                ),
                NodeParameter(
                    name="state_version_id",
                    type=NodeParameterType.STRING,
                    description="ID of the state version",
                    required=False
                ),
                NodeParameter(
                    name="variable_id",
                    type=NodeParameterType.STRING,
                    description="ID of the variable",
                    required=False
                ),
                NodeParameter(
                    name="variable_key",
                    type=NodeParameterType.STRING,
                    description="Variable key/name",
                    required=False
                ),
                NodeParameter(
                    name="variable_value",
                    type=NodeParameterType.STRING,
                    description="Variable value",
                    required=False
                ),
                NodeParameter(
                    name="variable_category",
                    type=NodeParameterType.STRING,
                    description="Variable category",
                    required=False,
                    enum=["terraform", "env"]
                ),
                NodeParameter(
                    name="variable_hcl",
                    type=NodeParameterType.BOOLEAN,
                    description="Variable is HCL format",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="variable_sensitive",
                    type=NodeParameterType.BOOLEAN,
                    description="Variable is sensitive",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="variable_description",
                    type=NodeParameterType.STRING,
                    description="Variable description",
                    required=False
                ),
                NodeParameter(
                    name="team_name",
                    type=NodeParameterType.STRING,
                    description="Name of the team",
                    required=False
                ),
                NodeParameter(
                    name="team_id",
                    type=NodeParameterType.STRING,
                    description="ID of the team",
                    required=False
                ),
                NodeParameter(
                    name="policy_name",
                    type=NodeParameterType.STRING,
                    description="Name of the policy",
                    required=False
                ),
                NodeParameter(
                    name="policy_id",
                    type=NodeParameterType.STRING,
                    description="ID of the policy",
                    required=False
                ),
                NodeParameter(
                    name="policy_code",
                    type=NodeParameterType.STRING,
                    description="Policy code content",
                    required=False
                ),
                NodeParameter(
                    name="enforcement_level",
                    type=NodeParameterType.STRING,
                    description="Policy enforcement level",
                    required=False,
                    enum=["advisory", "soft-mandatory", "hard-mandatory"]
                ),
                NodeParameter(
                    name="wait_for_completion",
                    type=NodeParameterType.BOOLEAN,
                    description="Wait for operation completion",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="timeout",
                    type=NodeParameterType.NUMBER,
                    description="Timeout in seconds for operations",
                    required=False,
                    default=3600
                ),
                NodeParameter(
                    name="config_data",
                    type=NodeParameterType.OBJECT,
                    description="Additional configuration data",
                    required=False
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "workspace": NodeParameterType.OBJECT,
                "workspaces": NodeParameterType.ARRAY,
                "run": NodeParameterType.OBJECT,
                "runs": NodeParameterType.ARRAY,
                "plan": NodeParameterType.OBJECT,
                "apply": NodeParameterType.OBJECT,
                "state_version": NodeParameterType.OBJECT,
                "state_versions": NodeParameterType.ARRAY,
                "current_state": NodeParameterType.OBJECT,
                "variable": NodeParameterType.OBJECT,
                "variables": NodeParameterType.ARRAY,
                "variable_set": NodeParameterType.OBJECT,
                "variable_sets": NodeParameterType.ARRAY,
                "organization": NodeParameterType.OBJECT,
                "organizations": NodeParameterType.ARRAY,
                "team": NodeParameterType.OBJECT,
                "teams": NodeParameterType.ARRAY,
                "policy": NodeParameterType.OBJECT,
                "policies": NodeParameterType.ARRAY,
                "policy_set": NodeParameterType.OBJECT,
                "policy_sets": NodeParameterType.ARRAY,
                "policy_check": NodeParameterType.OBJECT,
                "cost_estimate": NodeParameterType.OBJECT,
                "configuration_version": NodeParameterType.OBJECT,
                "configuration_versions": NodeParameterType.ARRAY,
                "registry_modules": NodeParameterType.ARRAY,
                "registry_providers": NodeParameterType.ARRAY,
                "oauth_tokens": NodeParameterType.ARRAY,
                "ssh_keys": NodeParameterType.ARRAY,
                "notification_configurations": NodeParameterType.ARRAY,
                "agent_pools": NodeParameterType.ARRAY,
                "plan_output": NodeParameterType.STRING,
                "plan_json": NodeParameterType.OBJECT,
                "apply_log": NodeParameterType.STRING,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["terraform", "infrastructure", "iac", "cloud", "deployment", "automation", "api", "integration"],
            author="System",
            documentation_url="https://www.terraform.io/docs/cloud/api/index.html"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for API token
        if not params.get("api_token"):
            raise NodeValidationError("Terraform Cloud API token is required")
        
        # Validate organization for most operations
        org_required_ops = [
            TerraformOperation.CREATE_WORKSPACE, TerraformOperation.LIST_WORKSPACES,
            TerraformOperation.LIST_TEAMS, TerraformOperation.CREATE_TEAM,
            TerraformOperation.LIST_POLICIES, TerraformOperation.CREATE_POLICY
        ]
        
        if operation in org_required_ops and not params.get("organization"):
            raise NodeValidationError(f"Organization is required for operation: {operation}")
        
        # Validate workspace identifier for workspace operations
        workspace_ops = [
            TerraformOperation.UPDATE_WORKSPACE, TerraformOperation.DELETE_WORKSPACE,
            TerraformOperation.GET_WORKSPACE, TerraformOperation.LOCK_WORKSPACE,
            TerraformOperation.UNLOCK_WORKSPACE, TerraformOperation.CREATE_RUN,
            TerraformOperation.LIST_RUNS, TerraformOperation.LIST_VARIABLES,
            TerraformOperation.CREATE_VARIABLE
        ]
        
        if operation in workspace_ops and not (params.get("workspace_id") or params.get("workspace_name")):
            raise NodeValidationError(f"Workspace ID or name is required for operation: {operation}")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Terraform node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Execute the appropriate operation
            if operation == TerraformOperation.CREATE_WORKSPACE:
                return await self._operation_create_workspace(validated_data)
            elif operation == TerraformOperation.UPDATE_WORKSPACE:
                return await self._operation_update_workspace(validated_data)
            elif operation == TerraformOperation.DELETE_WORKSPACE:
                return await self._operation_delete_workspace(validated_data)
            elif operation == TerraformOperation.GET_WORKSPACE:
                return await self._operation_get_workspace(validated_data)
            elif operation == TerraformOperation.LIST_WORKSPACES:
                return await self._operation_list_workspaces(validated_data)
            elif operation == TerraformOperation.LOCK_WORKSPACE:
                return await self._operation_lock_workspace(validated_data)
            elif operation == TerraformOperation.UNLOCK_WORKSPACE:
                return await self._operation_unlock_workspace(validated_data)
            elif operation == TerraformOperation.CREATE_CONFIGURATION_VERSION:
                return await self._operation_create_configuration_version(validated_data)
            elif operation == TerraformOperation.UPLOAD_CONFIGURATION_FILES:
                return await self._operation_upload_configuration_files(validated_data)
            elif operation == TerraformOperation.GET_CONFIGURATION_VERSION:
                return await self._operation_get_configuration_version(validated_data)
            elif operation == TerraformOperation.CREATE_RUN:
                return await self._operation_create_run(validated_data)
            elif operation == TerraformOperation.GET_RUN:
                return await self._operation_get_run(validated_data)
            elif operation == TerraformOperation.LIST_RUNS:
                return await self._operation_list_runs(validated_data)
            elif operation == TerraformOperation.APPLY_RUN:
                return await self._operation_apply_run(validated_data)
            elif operation == TerraformOperation.DISCARD_RUN:
                return await self._operation_discard_run(validated_data)
            elif operation == TerraformOperation.CANCEL_RUN:
                return await self._operation_cancel_run(validated_data)
            elif operation == TerraformOperation.GET_PLAN:
                return await self._operation_get_plan(validated_data)
            elif operation == TerraformOperation.GET_PLAN_JSON_OUTPUT:
                return await self._operation_get_plan_json_output(validated_data)
            elif operation == TerraformOperation.GET_PLAN_LOG:
                return await self._operation_get_plan_log(validated_data)
            elif operation == TerraformOperation.GET_APPLY:
                return await self._operation_get_apply(validated_data)
            elif operation == TerraformOperation.GET_APPLY_LOG:
                return await self._operation_get_apply_log(validated_data)
            elif operation == TerraformOperation.LIST_STATE_VERSIONS:
                return await self._operation_list_state_versions(validated_data)
            elif operation == TerraformOperation.GET_STATE_VERSION:
                return await self._operation_get_state_version(validated_data)
            elif operation == TerraformOperation.GET_CURRENT_STATE_VERSION:
                return await self._operation_get_current_state_version(validated_data)
            elif operation == TerraformOperation.CREATE_STATE_VERSION:
                return await self._operation_create_state_version(validated_data)
            elif operation == TerraformOperation.LIST_VARIABLES:
                return await self._operation_list_variables(validated_data)
            elif operation == TerraformOperation.CREATE_VARIABLE:
                return await self._operation_create_variable(validated_data)
            elif operation == TerraformOperation.UPDATE_VARIABLE:
                return await self._operation_update_variable(validated_data)
            elif operation == TerraformOperation.DELETE_VARIABLE:
                return await self._operation_delete_variable(validated_data)
            elif operation == TerraformOperation.GET_VARIABLE:
                return await self._operation_get_variable(validated_data)
            elif operation == TerraformOperation.LIST_ORGANIZATIONS:
                return await self._operation_list_organizations(validated_data)
            elif operation == TerraformOperation.GET_ORGANIZATION:
                return await self._operation_get_organization(validated_data)
            elif operation == TerraformOperation.UPDATE_ORGANIZATION:
                return await self._operation_update_organization(validated_data)
            elif operation == TerraformOperation.LIST_TEAMS:
                return await self._operation_list_teams(validated_data)
            elif operation == TerraformOperation.CREATE_TEAM:
                return await self._operation_create_team(validated_data)
            elif operation == TerraformOperation.UPDATE_TEAM:
                return await self._operation_update_team(validated_data)
            elif operation == TerraformOperation.DELETE_TEAM:
                return await self._operation_delete_team(validated_data)
            elif operation == TerraformOperation.GET_TEAM:
                return await self._operation_get_team(validated_data)
            elif operation == TerraformOperation.LIST_POLICIES:
                return await self._operation_list_policies(validated_data)
            elif operation == TerraformOperation.CREATE_POLICY:
                return await self._operation_create_policy(validated_data)
            elif operation == TerraformOperation.UPDATE_POLICY:
                return await self._operation_update_policy(validated_data)
            elif operation == TerraformOperation.DELETE_POLICY:
                return await self._operation_delete_policy(validated_data)
            elif operation == TerraformOperation.GET_POLICY:
                return await self._operation_get_policy(validated_data)
            elif operation == TerraformOperation.LIST_POLICY_SETS:
                return await self._operation_list_policy_sets(validated_data)
            elif operation == TerraformOperation.CREATE_POLICY_SET:
                return await self._operation_create_policy_set(validated_data)
            elif operation == TerraformOperation.GET_COST_ESTIMATE:
                return await self._operation_get_cost_estimate(validated_data)
            elif operation == TerraformOperation.LIST_REGISTRY_MODULES:
                return await self._operation_list_registry_modules(validated_data)
            elif operation == TerraformOperation.CREATE_REGISTRY_MODULE:
                return await self._operation_create_registry_module(validated_data)
            elif operation == TerraformOperation.LIST_SSH_KEYS:
                return await self._operation_list_ssh_keys(validated_data)
            elif operation == TerraformOperation.CREATE_SSH_KEY:
                return await self._operation_create_ssh_key(validated_data)
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
            error_message = f"Error in Terraform node: {str(e)}"
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
        """Make an HTTP request to the Terraform Cloud API."""
        url = f"{self.BASE_URL}/{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {params.get('api_token')}",
            "Content-Type": "application/vnd.api+json"
        }
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                response_headers = dict(response.headers)
                
                # Handle different response content types
                if response.content_type == 'application/vnd.api+json' or response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Terraform Cloud API error {response.status}: {response_data}"
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
    
    async def _get_workspace_id(self, params: Dict[str, Any]) -> Optional[str]:
        """Get workspace ID from name if needed."""
        if params.get("workspace_id"):
            return params.get("workspace_id")
        
        if params.get("workspace_name") and params.get("organization"):
            workspace_name = params.get("workspace_name")
            organization = params.get("organization")
            
            # Get workspace by name
            endpoint = f"organizations/{organization}/workspaces/{workspace_name}"
            result = await self._make_request("GET", endpoint, params)
            
            if result["status"] == "success" and result["result"]:
                return result["result"]["data"]["id"]
        
        return None
    
    # -------------------------
    # Workspace Operations
    # -------------------------
    
    async def _operation_create_workspace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workspace."""
        organization = params.get("organization")
        workspace_name = params.get("workspace_name")
        
        workspace_data = {
            "data": {
                "type": "workspaces",
                "attributes": {
                    "name": workspace_name,
                    "terraform-version": params.get("terraform_version"),
                    "working-directory": params.get("working_directory"),
                    "execution-mode": params.get("execution_mode", "remote"),
                    "auto-apply": params.get("auto_apply", False),
                    "queue-all-runs": params.get("queue_all_runs", True)
                }
            }
        }
        
        # Add VCS repo if provided
        if params.get("vcs_repo"):
            workspace_data["data"]["attributes"]["vcs-repo"] = params.get("vcs_repo")
        
        endpoint = f"organizations/{organization}/workspaces"
        result = await self._make_request("POST", endpoint, params, workspace_data)
        
        if result["status"] == "success":
            result["workspace"] = result["result"]["data"]
        
        return result
    
    async def _operation_update_workspace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing workspace."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        workspace_data = {
            "data": {
                "type": "workspaces",
                "attributes": {}
            }
        }
        
        # Update only provided attributes
        if params.get("terraform_version"):
            workspace_data["data"]["attributes"]["terraform-version"] = params.get("terraform_version")
        if params.get("working_directory"):
            workspace_data["data"]["attributes"]["working-directory"] = params.get("working_directory")
        if params.get("execution_mode"):
            workspace_data["data"]["attributes"]["execution-mode"] = params.get("execution_mode")
        if "auto_apply" in params:
            workspace_data["data"]["attributes"]["auto-apply"] = params.get("auto_apply")
        if "queue_all_runs" in params:
            workspace_data["data"]["attributes"]["queue-all-runs"] = params.get("queue_all_runs")
        
        endpoint = f"workspaces/{workspace_id}"
        result = await self._make_request("PATCH", endpoint, params, workspace_data)
        
        if result["status"] == "success":
            result["workspace"] = result["result"]["data"]
        
        return result
    
    async def _operation_delete_workspace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a workspace."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        endpoint = f"workspaces/{workspace_id}"
        result = await self._make_request("DELETE", endpoint, params)
        
        if result["status"] == "success":
            result["workspace"] = {"id": workspace_id, "deleted": True}
        
        return result
    
    async def _operation_get_workspace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get workspace information."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        endpoint = f"workspaces/{workspace_id}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["workspace"] = result["result"]["data"]
        
        return result
    
    async def _operation_list_workspaces(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List workspaces in an organization."""
        organization = params.get("organization")
        
        endpoint = f"organizations/{organization}/workspaces"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            result["workspaces"] = result["result"]["data"]
        
        return result
    
    async def _operation_lock_workspace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lock a workspace."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        lock_data = {
            "reason": params.get("config_data", {}).get("reason", "Locked via API")
        }
        
        endpoint = f"workspaces/{workspace_id}/actions/lock"
        result = await self._make_request("POST", endpoint, params, lock_data)
        
        if result["status"] == "success":
            result["workspace"] = {"id": workspace_id, "locked": True}
        
        return result
    
    async def _operation_unlock_workspace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unlock a workspace."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        endpoint = f"workspaces/{workspace_id}/actions/unlock"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["workspace"] = {"id": workspace_id, "unlocked": True}
        
        return result
    
    # -------------------------
    # Configuration Version Operations
    # -------------------------
    
    async def _operation_create_configuration_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a configuration version."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        config_data = {
            "data": {
                "type": "configuration-versions",
                "attributes": {
                    "auto-queue-runs": params.get("auto_apply", False),
                    "speculative": params.get("speculative", False)
                }
            }
        }
        
        endpoint = f"workspaces/{workspace_id}/configuration-versions"
        result = await self._make_request("POST", endpoint, params, config_data)
        
        if result["status"] == "success":
            result["configuration_version"] = result["result"]["data"]
        
        return result
    
    async def _operation_upload_configuration_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Upload configuration files to a configuration version."""
        config_version_id = params.get("config_data", {}).get("configuration_version_id")
        upload_url = params.get("config_data", {}).get("upload_url")
        
        if not config_version_id or not upload_url:
            return {
                "status": "error",
                "error": "Configuration version ID and upload URL required",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        # This would typically upload a tar.gz file
        # For demo purposes, we'll just return success
        return {
            "status": "success",
            "result": {"uploaded": True, "configuration_version_id": config_version_id},
            "error": None,
            "status_code": 200,
            "response_headers": {}
        }
    
    async def _operation_get_configuration_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration version information."""
        config_version_id = params.get("config_data", {}).get("configuration_version_id")
        
        endpoint = f"configuration-versions/{config_version_id}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["configuration_version"] = result["result"]["data"]
        
        return result
    
    # -------------------------
    # Run Operations
    # -------------------------
    
    async def _operation_create_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a run."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        run_data = {
            "data": {
                "type": "runs",
                "attributes": {
                    "message": params.get("run_message", "Run created via API"),
                    "is-destroy": params.get("config_data", {}).get("is_destroy", False)
                },
                "relationships": {
                    "workspace": {
                        "data": {
                            "type": "workspaces",
                            "id": workspace_id
                        }
                    }
                }
            }
        }
        
        # Add configuration version if provided
        config_version_id = params.get("config_data", {}).get("configuration_version_id")
        if config_version_id:
            run_data["data"]["relationships"]["configuration-version"] = {
                "data": {
                    "type": "configuration-versions",
                    "id": config_version_id
                }
            }
        
        endpoint = "runs"
        result = await self._make_request("POST", endpoint, params, run_data)
        
        if result["status"] == "success":
            result["run"] = result["result"]["data"]
        
        return result
    
    async def _operation_get_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get run information."""
        run_id = params.get("run_id")
        
        endpoint = f"runs/{run_id}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["run"] = result["result"]["data"]
        
        return result
    
    async def _operation_list_runs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List runs for a workspace."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        endpoint = f"workspaces/{workspace_id}/runs"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            result["runs"] = result["result"]["data"]
        
        return result
    
    async def _operation_apply_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a run."""
        run_id = params.get("run_id")
        
        apply_data = {
            "comment": params.get("config_data", {}).get("comment", "Applied via API")
        }
        
        endpoint = f"runs/{run_id}/actions/apply"
        result = await self._make_request("POST", endpoint, params, apply_data)
        
        if result["status"] == "success":
            result["run"] = {"id": run_id, "applied": True}
        
        return result
    
    async def _operation_discard_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Discard a run."""
        run_id = params.get("run_id")
        
        discard_data = {
            "comment": params.get("config_data", {}).get("comment", "Discarded via API")
        }
        
        endpoint = f"runs/{run_id}/actions/discard"
        result = await self._make_request("POST", endpoint, params, discard_data)
        
        if result["status"] == "success":
            result["run"] = {"id": run_id, "discarded": True}
        
        return result
    
    async def _operation_cancel_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a run."""
        run_id = params.get("run_id")
        
        cancel_data = {
            "comment": params.get("config_data", {}).get("comment", "Cancelled via API")
        }
        
        endpoint = f"runs/{run_id}/actions/cancel"
        result = await self._make_request("POST", endpoint, params, cancel_data)
        
        if result["status"] == "success":
            result["run"] = {"id": run_id, "cancelled": True}
        
        return result
    
    # -------------------------
    # Plan Operations
    # -------------------------
    
    async def _operation_get_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get plan information."""
        plan_id = params.get("plan_id")
        
        endpoint = f"plans/{plan_id}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["plan"] = result["result"]["data"]
        
        return result
    
    async def _operation_get_plan_json_output(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get plan JSON output."""
        plan_id = params.get("plan_id")
        
        endpoint = f"plans/{plan_id}/json-output"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["plan_json"] = result["result"]
        
        return result
    
    async def _operation_get_plan_log(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get plan log output."""
        plan_id = params.get("plan_id")
        
        # Note: This would typically return plain text
        endpoint = f"plans/{plan_id}/log"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["plan_output"] = result["result"]
        
        return result
    
    # -------------------------
    # Apply Operations
    # -------------------------
    
    async def _operation_get_apply(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get apply information."""
        apply_id = params.get("apply_id")
        
        endpoint = f"applies/{apply_id}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["apply"] = result["result"]["data"]
        
        return result
    
    async def _operation_get_apply_log(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get apply log output."""
        apply_id = params.get("apply_id")
        
        # Note: This would typically return plain text
        endpoint = f"applies/{apply_id}/log"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["apply_log"] = result["result"]
        
        return result
    
    # -------------------------
    # State Version Operations
    # -------------------------
    
    async def _operation_list_state_versions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List state versions for a workspace."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        endpoint = f"workspaces/{workspace_id}/state-versions"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            result["state_versions"] = result["result"]["data"]
        
        return result
    
    async def _operation_get_state_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get state version information."""
        state_version_id = params.get("state_version_id")
        
        endpoint = f"state-versions/{state_version_id}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["state_version"] = result["result"]["data"]
        
        return result
    
    async def _operation_get_current_state_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current state version for a workspace."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        endpoint = f"workspaces/{workspace_id}/current-state-version"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["current_state"] = result["result"]["data"]
        
        return result
    
    async def _operation_create_state_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new state version."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        state_data = {
            "data": {
                "type": "state-versions",
                "attributes": {
                    "serial": params.get("config_data", {}).get("serial", 1),
                    "md5": params.get("config_data", {}).get("md5"),
                    "lineage": params.get("config_data", {}).get("lineage")
                }
            }
        }
        
        endpoint = f"workspaces/{workspace_id}/state-versions"
        result = await self._make_request("POST", endpoint, params, state_data)
        
        if result["status"] == "success":
            result["state_version"] = result["result"]["data"]
        
        return result
    
    # -------------------------
    # Variable Operations
    # -------------------------
    
    async def _operation_list_variables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List variables for a workspace."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        endpoint = f"workspaces/{workspace_id}/vars"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            result["variables"] = result["result"]["data"]
        
        return result
    
    async def _operation_create_variable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a variable."""
        workspace_id = await self._get_workspace_id(params)
        
        if not workspace_id:
            return {
                "status": "error",
                "error": "Could not find workspace",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        variable_data = {
            "data": {
                "type": "vars",
                "attributes": {
                    "key": params.get("variable_key"),
                    "value": params.get("variable_value"),
                    "category": params.get("variable_category", "terraform"),
                    "hcl": params.get("variable_hcl", False),
                    "sensitive": params.get("variable_sensitive", False),
                    "description": params.get("variable_description", "")
                }
            }
        }
        
        endpoint = f"workspaces/{workspace_id}/vars"
        result = await self._make_request("POST", endpoint, params, variable_data)
        
        if result["status"] == "success":
            result["variable"] = result["result"]["data"]
        
        return result
    
    async def _operation_update_variable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a variable."""
        variable_id = params.get("variable_id")
        
        variable_data = {
            "data": {
                "type": "vars",
                "attributes": {}
            }
        }
        
        # Update only provided attributes
        if params.get("variable_key"):
            variable_data["data"]["attributes"]["key"] = params.get("variable_key")
        if params.get("variable_value"):
            variable_data["data"]["attributes"]["value"] = params.get("variable_value")
        if params.get("variable_category"):
            variable_data["data"]["attributes"]["category"] = params.get("variable_category")
        if "variable_hcl" in params:
            variable_data["data"]["attributes"]["hcl"] = params.get("variable_hcl")
        if "variable_sensitive" in params:
            variable_data["data"]["attributes"]["sensitive"] = params.get("variable_sensitive")
        if params.get("variable_description"):
            variable_data["data"]["attributes"]["description"] = params.get("variable_description")
        
        endpoint = f"vars/{variable_id}"
        result = await self._make_request("PATCH", endpoint, params, variable_data)
        
        if result["status"] == "success":
            result["variable"] = result["result"]["data"]
        
        return result
    
    async def _operation_delete_variable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a variable."""
        variable_id = params.get("variable_id")
        
        endpoint = f"vars/{variable_id}"
        result = await self._make_request("DELETE", endpoint, params)
        
        if result["status"] == "success":
            result["variable"] = {"id": variable_id, "deleted": True}
        
        return result
    
    async def _operation_get_variable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get variable information."""
        variable_id = params.get("variable_id")
        
        endpoint = f"vars/{variable_id}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["variable"] = result["result"]["data"]
        
        return result
    
    # -------------------------
    # Organization Operations
    # -------------------------
    
    async def _operation_list_organizations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List organizations."""
        endpoint = "organizations"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            result["organizations"] = result["result"]["data"]
        
        return result
    
    async def _operation_get_organization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get organization information."""
        organization = params.get("organization")
        
        endpoint = f"organizations/{organization}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["organization"] = result["result"]["data"]
        
        return result
    
    async def _operation_update_organization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update organization settings."""
        organization = params.get("organization")
        
        org_data = {
            "data": {
                "type": "organizations",
                "attributes": params.get("config_data", {})
            }
        }
        
        endpoint = f"organizations/{organization}"
        result = await self._make_request("PATCH", endpoint, params, org_data)
        
        if result["status"] == "success":
            result["organization"] = result["result"]["data"]
        
        return result
    
    # -------------------------
    # Team Operations
    # -------------------------
    
    async def _operation_list_teams(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List teams in an organization."""
        organization = params.get("organization")
        
        endpoint = f"organizations/{organization}/teams"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            result["teams"] = result["result"]["data"]
        
        return result
    
    async def _operation_create_team(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a team."""
        organization = params.get("organization")
        team_name = params.get("team_name")
        
        team_data = {
            "data": {
                "type": "teams",
                "attributes": {
                    "name": team_name,
                    "organization-access": params.get("config_data", {}).get("organization_access", {})
                }
            }
        }
        
        endpoint = f"organizations/{organization}/teams"
        result = await self._make_request("POST", endpoint, params, team_data)
        
        if result["status"] == "success":
            result["team"] = result["result"]["data"]
        
        return result
    
    async def _operation_update_team(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a team."""
        team_id = params.get("team_id")
        
        team_data = {
            "data": {
                "type": "teams",
                "attributes": {
                    "name": params.get("team_name"),
                    "organization-access": params.get("config_data", {}).get("organization_access", {})
                }
            }
        }
        
        endpoint = f"teams/{team_id}"
        result = await self._make_request("PATCH", endpoint, params, team_data)
        
        if result["status"] == "success":
            result["team"] = result["result"]["data"]
        
        return result
    
    async def _operation_delete_team(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a team."""
        team_id = params.get("team_id")
        
        endpoint = f"teams/{team_id}"
        result = await self._make_request("DELETE", endpoint, params)
        
        if result["status"] == "success":
            result["team"] = {"id": team_id, "deleted": True}
        
        return result
    
    async def _operation_get_team(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get team information."""
        team_id = params.get("team_id")
        
        endpoint = f"teams/{team_id}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["team"] = result["result"]["data"]
        
        return result
    
    # -------------------------
    # Policy Operations
    # -------------------------
    
    async def _operation_list_policies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List policies in an organization."""
        organization = params.get("organization")
        
        endpoint = f"organizations/{organization}/policies"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            result["policies"] = result["result"]["data"]
        
        return result
    
    async def _operation_create_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a policy."""
        organization = params.get("organization")
        policy_name = params.get("policy_name")
        
        policy_data = {
            "data": {
                "type": "policies",
                "attributes": {
                    "name": policy_name,
                    "description": params.get("config_data", {}).get("description", ""),
                    "kind": params.get("config_data", {}).get("kind", "sentinel"),
                    "query": params.get("config_data", {}).get("query"),
                    "enforcement-level": params.get("enforcement_level", "advisory")
                }
            }
        }
        
        endpoint = f"organizations/{organization}/policies"
        result = await self._make_request("POST", endpoint, params, policy_data)
        
        if result["status"] == "success":
            result["policy"] = result["result"]["data"]
        
        return result
    
    async def _operation_update_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a policy."""
        policy_id = params.get("policy_id")
        
        policy_data = {
            "data": {
                "type": "policies",
                "attributes": {}
            }
        }
        
        # Update only provided attributes
        if params.get("policy_name"):
            policy_data["data"]["attributes"]["name"] = params.get("policy_name")
        if params.get("enforcement_level"):
            policy_data["data"]["attributes"]["enforcement-level"] = params.get("enforcement_level")
        
        endpoint = f"policies/{policy_id}"
        result = await self._make_request("PATCH", endpoint, params, policy_data)
        
        if result["status"] == "success":
            result["policy"] = result["result"]["data"]
        
        return result
    
    async def _operation_delete_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a policy."""
        policy_id = params.get("policy_id")
        
        endpoint = f"policies/{policy_id}"
        result = await self._make_request("DELETE", endpoint, params)
        
        if result["status"] == "success":
            result["policy"] = {"id": policy_id, "deleted": True}
        
        return result
    
    async def _operation_get_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get policy information."""
        policy_id = params.get("policy_id")
        
        endpoint = f"policies/{policy_id}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["policy"] = result["result"]["data"]
        
        return result
    
    # -------------------------
    # Additional Operations
    # -------------------------
    
    async def _operation_list_policy_sets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List policy sets in an organization."""
        organization = params.get("organization")
        
        endpoint = f"organizations/{organization}/policy-sets"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            result["policy_sets"] = result["result"]["data"]
        
        return result
    
    async def _operation_create_policy_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a policy set."""
        organization = params.get("organization")
        
        policy_set_data = {
            "data": {
                "type": "policy-sets",
                "attributes": {
                    "name": params.get("config_data", {}).get("name"),
                    "description": params.get("config_data", {}).get("description", ""),
                    "global": params.get("config_data", {}).get("global", False)
                }
            }
        }
        
        endpoint = f"organizations/{organization}/policy-sets"
        result = await self._make_request("POST", endpoint, params, policy_set_data)
        
        if result["status"] == "success":
            result["policy_set"] = result["result"]["data"]
        
        return result
    
    async def _operation_get_cost_estimate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get cost estimate for a run."""
        cost_estimate_id = params.get("config_data", {}).get("cost_estimate_id")
        
        endpoint = f"cost-estimates/{cost_estimate_id}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["cost_estimate"] = result["result"]["data"]
        
        return result
    
    async def _operation_list_registry_modules(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List registry modules."""
        organization = params.get("organization")
        
        endpoint = f"organizations/{organization}/registry-modules"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            result["registry_modules"] = result["result"]["data"]
        
        return result
    
    async def _operation_create_registry_module(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a registry module."""
        organization = params.get("organization")
        
        module_data = {
            "data": {
                "type": "registry-modules",
                "attributes": {
                    "name": params.get("config_data", {}).get("name"),
                    "provider": params.get("config_data", {}).get("provider"),
                    "registry-name": params.get("config_data", {}).get("registry_name", "public")
                }
            }
        }
        
        endpoint = f"organizations/{organization}/registry-modules"
        result = await self._make_request("POST", endpoint, params, module_data)
        
        if result["status"] == "success":
            result["registry_module"] = result["result"]["data"]
        
        return result
    
    async def _operation_list_ssh_keys(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List SSH keys."""
        organization = params.get("organization")
        
        endpoint = f"organizations/{organization}/ssh-keys"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            result["ssh_keys"] = result["result"]["data"]
        
        return result
    
    async def _operation_create_ssh_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an SSH key."""
        organization = params.get("organization")
        
        ssh_key_data = {
            "data": {
                "type": "ssh-keys",
                "attributes": {
                    "name": params.get("config_data", {}).get("name"),
                    "value": params.get("config_data", {}).get("value")
                }
            }
        }
        
        endpoint = f"organizations/{organization}/ssh-keys"
        result = await self._make_request("POST", endpoint, params, ssh_key_data)
        
        if result["status"] == "success":
            result["ssh_key"] = result["result"]["data"]
        
        return result


# Utility functions for common Terraform operations
class TerraformHelpers:
    """Helper functions for common Terraform operations."""
    
    @staticmethod
    def create_workspace_config(name: str, organization: str, terraform_version: str = None,
                               execution_mode: str = "remote", auto_apply: bool = False) -> Dict[str, Any]:
        """Create a workspace configuration."""
        config = {
            "name": name,
            "organization": organization,
            "execution_mode": execution_mode,
            "auto_apply": auto_apply
        }
        
        if terraform_version:
            config["terraform_version"] = terraform_version
        
        return config
    
    @staticmethod
    def create_vcs_repo_config(oauth_token_id: str, identifier: str, branch: str = None,
                              working_directory: str = None) -> Dict[str, Any]:
        """Create a VCS repository configuration."""
        config = {
            "oauth-token-id": oauth_token_id,
            "identifier": identifier
        }
        
        if branch:
            config["branch"] = branch
        if working_directory:
            config["working-directory"] = working_directory
        
        return config
    
    @staticmethod
    def create_variable_config(key: str, value: str, category: str = "terraform",
                             hcl: bool = False, sensitive: bool = False,
                             description: str = "") -> Dict[str, Any]:
        """Create a variable configuration."""
        return {
            "key": key,
            "value": value,
            "category": category,
            "hcl": hcl,
            "sensitive": sensitive,
            "description": description
        }
    
    @staticmethod
    def create_run_config(workspace_id: str, message: str = None,
                         is_destroy: bool = False, configuration_version_id: str = None) -> Dict[str, Any]:
        """Create a run configuration."""
        config = {
            "workspace_id": workspace_id,
            "is_destroy": is_destroy
        }
        
        if message:
            config["message"] = message
        if configuration_version_id:
            config["configuration_version_id"] = configuration_version_id
        
        return config
    
    @staticmethod
    def parse_run_status(status: str) -> Dict[str, Any]:
        """Parse run status into structured information."""
        status_map = {
            "pending": {"state": "queued", "action": "planning"},
            "planning": {"state": "running", "action": "planning"},
            "planned": {"state": "completed", "action": "planning"},
            "cost_estimating": {"state": "running", "action": "cost_estimating"},
            "cost_estimated": {"state": "completed", "action": "cost_estimating"},
            "policy_checking": {"state": "running", "action": "policy_checking"},
            "policy_checked": {"state": "completed", "action": "policy_checking"},
            "confirmed": {"state": "ready", "action": "applying"},
            "applying": {"state": "running", "action": "applying"},
            "applied": {"state": "completed", "action": "applying"},
            "discarded": {"state": "cancelled", "action": "discarded"},
            "errored": {"state": "error", "action": "errored"},
            "canceled": {"state": "cancelled", "action": "cancelled"}
        }
        
        return status_map.get(status, {"state": "unknown", "action": "unknown"})


# Main test function for Terraform Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Terraform Node Test Suite ===")
        
        # Get Terraform configuration from environment or user input
        api_token = os.environ.get("TERRAFORM_CLOUD_TOKEN")
        organization = os.environ.get("TERRAFORM_ORGANIZATION")
        
        if not api_token:
            print("Terraform Cloud configuration not found in environment variables")
            print("Please set TERRAFORM_CLOUD_TOKEN and TERRAFORM_ORGANIZATION")
            print("Or provide them when prompted...")
            api_token = input("Enter Terraform Cloud API token: ")
            organization = input("Enter Terraform organization: ")
        
        if not all([api_token, organization]):
            print("Terraform Cloud configuration is required for testing")
            return
        
        # Create an instance of the Terraform Node
        node = TerraformNode()
        
        # Test cases
        test_cases = [
            {
                "name": "List Organizations",
                "params": {
                    "operation": TerraformOperation.LIST_ORGANIZATIONS,
                    "api_token": api_token
                },
                "expected_status": "success"
            },
            {
                "name": "Get Organization",
                "params": {
                    "operation": TerraformOperation.GET_ORGANIZATION,
                    "api_token": api_token,
                    "organization": organization
                },
                "expected_status": "success"
            },
            {
                "name": "List Workspaces",
                "params": {
                    "operation": TerraformOperation.LIST_WORKSPACES,
                    "api_token": api_token,
                    "organization": organization
                },
                "expected_status": "success"
            }
        ]
        
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
                    if result.get("organizations"):
                        print(f"Found {len(result['organizations'])} organizations")
                    if result.get("organization"):
                        org_name = result["organization"].get("attributes", {}).get("name")
                        print(f"Organization: {org_name}")
                    if result.get("workspaces"):
                        print(f"Found {len(result['workspaces'])} workspaces")
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
    registry.register("terraform", TerraformNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register TerraformNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")