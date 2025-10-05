"""
Jenkins Node - Comprehensive integration with Jenkins CI/CD automation platform
Provides access to all Jenkins REST API operations including job management, build automation, pipeline execution, and system administration.
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

class JenkinsOperation:
    """Operations available on Jenkins REST API."""
    
    # Job Operations
    CREATE_JOB = "create_job"
    UPDATE_JOB = "update_job"
    DELETE_JOB = "delete_job"
    GET_JOB_INFO = "get_job_info"
    LIST_JOBS = "list_jobs"
    COPY_JOB = "copy_job"
    ENABLE_JOB = "enable_job"
    DISABLE_JOB = "disable_job"
    RENAME_JOB = "rename_job"
    
    # Build Operations
    BUILD_JOB = "build_job"
    BUILD_JOB_WITH_PARAMS = "build_job_with_params"
    STOP_BUILD = "stop_build"
    GET_BUILD_INFO = "get_build_info"
    DELETE_BUILD = "delete_build"
    GET_BUILD_LOG = "get_build_log"
    GET_BUILD_CONSOLE = "get_build_console"
    GET_LAST_BUILD = "get_last_build"
    GET_LAST_SUCCESSFUL_BUILD = "get_last_successful_build"
    GET_LAST_FAILED_BUILD = "get_last_failed_build"
    GET_BUILD_STATUS = "get_build_status"
    GET_BUILD_ARTIFACTS = "get_build_artifacts"
    LIST_BUILDS = "list_builds"
    
    # Queue Operations
    GET_QUEUE_INFO = "get_queue_info"
    CANCEL_QUEUE_ITEM = "cancel_queue_item"
    GET_QUEUE_ITEM = "get_queue_item"
    
    # Node/Computer Operations
    LIST_NODES = "list_nodes"
    GET_NODE_INFO = "get_node_info"
    CREATE_NODE = "create_node"
    DELETE_NODE = "delete_node"
    ENABLE_NODE = "enable_node"
    DISABLE_NODE = "disable_node"
    TAKE_NODE_OFFLINE = "take_node_offline"
    BRING_NODE_ONLINE = "bring_node_online"
    GET_NODE_LOG = "get_node_log"
    
    # Plugin Operations
    LIST_PLUGINS = "list_plugins"
    INSTALL_PLUGIN = "install_plugin"
    UNINSTALL_PLUGIN = "uninstall_plugin"
    UPDATE_PLUGIN = "update_plugin"
    GET_PLUGIN_INFO = "get_plugin_info"
    
    # View Operations
    LIST_VIEWS = "list_views"
    CREATE_VIEW = "create_view"
    DELETE_VIEW = "delete_view"
    UPDATE_VIEW = "update_view"
    GET_VIEW_INFO = "get_view_info"
    ADD_JOB_TO_VIEW = "add_job_to_view"
    REMOVE_JOB_FROM_VIEW = "remove_job_from_view"
    
    # System Operations
    GET_VERSION = "get_version"
    GET_SYSTEM_INFO = "get_system_info"
    RESTART_JENKINS = "restart_jenkins"
    SAFE_RESTART = "safe_restart"
    SHUTDOWN = "shutdown"
    SAFE_SHUTDOWN = "safe_shutdown"
    QUIET_DOWN = "quiet_down"
    CANCEL_QUIET_DOWN = "cancel_quiet_down"
    
    # User Operations
    CREATE_USER = "create_user"
    DELETE_USER = "delete_user"
    LIST_USERS = "list_users"
    GET_USER_INFO = "get_user_info"
    UPDATE_USER = "update_user"
    
    # Credential Operations
    LIST_CREDENTIALS = "list_credentials"
    CREATE_CREDENTIAL = "create_credential"
    DELETE_CREDENTIAL = "delete_credential"
    UPDATE_CREDENTIAL = "update_credential"
    GET_CREDENTIAL = "get_credential"
    
    # Pipeline Operations
    RUN_PIPELINE = "run_pipeline"
    GET_PIPELINE_RUN = "get_pipeline_run"
    STOP_PIPELINE_RUN = "stop_pipeline_run"
    GET_PIPELINE_LOG = "get_pipeline_log"
    LIST_PIPELINE_RUNS = "list_pipeline_runs"
    
    # Folder Operations
    CREATE_FOLDER = "create_folder"
    DELETE_FOLDER = "delete_folder"
    LIST_FOLDER_JOBS = "list_folder_jobs"
    
    # Security Operations
    GET_CRUMB = "get_crumb"
    VALIDATE_TOKEN = "validate_token"
    
    # Statistics Operations
    GET_BUILD_STATISTICS = "get_build_statistics"
    GET_JOB_STATISTICS = "get_job_statistics"
    GET_LOAD_STATISTICS = "get_load_statistics"

class JenkinsNode(BaseNode):
    """
    Node for interacting with Jenkins CI/CD automation platform.
    Provides comprehensive functionality for build automation, pipeline management, and system administration.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        self.crumb_issuer = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Jenkins node."""
        return NodeSchema(
            node_type="jenkins",
            version="1.0.0",
            description="Comprehensive integration with Jenkins CI/CD automation platform for build automation, pipeline management, and system administration",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Jenkins API",
                    required=True,
                    enum=[
                        JenkinsOperation.CREATE_JOB,
                        JenkinsOperation.UPDATE_JOB,
                        JenkinsOperation.DELETE_JOB,
                        JenkinsOperation.GET_JOB_INFO,
                        JenkinsOperation.LIST_JOBS,
                        JenkinsOperation.COPY_JOB,
                        JenkinsOperation.ENABLE_JOB,
                        JenkinsOperation.DISABLE_JOB,
                        JenkinsOperation.RENAME_JOB,
                        JenkinsOperation.BUILD_JOB,
                        JenkinsOperation.BUILD_JOB_WITH_PARAMS,
                        JenkinsOperation.STOP_BUILD,
                        JenkinsOperation.GET_BUILD_INFO,
                        JenkinsOperation.DELETE_BUILD,
                        JenkinsOperation.GET_BUILD_LOG,
                        JenkinsOperation.GET_BUILD_CONSOLE,
                        JenkinsOperation.GET_LAST_BUILD,
                        JenkinsOperation.GET_LAST_SUCCESSFUL_BUILD,
                        JenkinsOperation.GET_LAST_FAILED_BUILD,
                        JenkinsOperation.GET_BUILD_STATUS,
                        JenkinsOperation.GET_BUILD_ARTIFACTS,
                        JenkinsOperation.LIST_BUILDS,
                        JenkinsOperation.GET_QUEUE_INFO,
                        JenkinsOperation.CANCEL_QUEUE_ITEM,
                        JenkinsOperation.GET_QUEUE_ITEM,
                        JenkinsOperation.LIST_NODES,
                        JenkinsOperation.GET_NODE_INFO,
                        JenkinsOperation.CREATE_NODE,
                        JenkinsOperation.DELETE_NODE,
                        JenkinsOperation.ENABLE_NODE,
                        JenkinsOperation.DISABLE_NODE,
                        JenkinsOperation.TAKE_NODE_OFFLINE,
                        JenkinsOperation.BRING_NODE_ONLINE,
                        JenkinsOperation.GET_NODE_LOG,
                        JenkinsOperation.LIST_PLUGINS,
                        JenkinsOperation.INSTALL_PLUGIN,
                        JenkinsOperation.UNINSTALL_PLUGIN,
                        JenkinsOperation.UPDATE_PLUGIN,
                        JenkinsOperation.GET_PLUGIN_INFO,
                        JenkinsOperation.LIST_VIEWS,
                        JenkinsOperation.CREATE_VIEW,
                        JenkinsOperation.DELETE_VIEW,
                        JenkinsOperation.UPDATE_VIEW,
                        JenkinsOperation.GET_VIEW_INFO,
                        JenkinsOperation.ADD_JOB_TO_VIEW,
                        JenkinsOperation.REMOVE_JOB_FROM_VIEW,
                        JenkinsOperation.GET_VERSION,
                        JenkinsOperation.GET_SYSTEM_INFO,
                        JenkinsOperation.RESTART_JENKINS,
                        JenkinsOperation.SAFE_RESTART,
                        JenkinsOperation.SHUTDOWN,
                        JenkinsOperation.SAFE_SHUTDOWN,
                        JenkinsOperation.QUIET_DOWN,
                        JenkinsOperation.CANCEL_QUIET_DOWN,
                        JenkinsOperation.CREATE_USER,
                        JenkinsOperation.DELETE_USER,
                        JenkinsOperation.LIST_USERS,
                        JenkinsOperation.GET_USER_INFO,
                        JenkinsOperation.UPDATE_USER,
                        JenkinsOperation.LIST_CREDENTIALS,
                        JenkinsOperation.CREATE_CREDENTIAL,
                        JenkinsOperation.DELETE_CREDENTIAL,
                        JenkinsOperation.UPDATE_CREDENTIAL,
                        JenkinsOperation.GET_CREDENTIAL,
                        JenkinsOperation.RUN_PIPELINE,
                        JenkinsOperation.GET_PIPELINE_RUN,
                        JenkinsOperation.STOP_PIPELINE_RUN,
                        JenkinsOperation.GET_PIPELINE_LOG,
                        JenkinsOperation.LIST_PIPELINE_RUNS,
                        JenkinsOperation.CREATE_FOLDER,
                        JenkinsOperation.DELETE_FOLDER,
                        JenkinsOperation.LIST_FOLDER_JOBS,
                        JenkinsOperation.GET_CRUMB,
                        JenkinsOperation.VALIDATE_TOKEN,
                        JenkinsOperation.GET_BUILD_STATISTICS,
                        JenkinsOperation.GET_JOB_STATISTICS,
                        JenkinsOperation.GET_LOAD_STATISTICS
                    ]
                ),
                NodeParameter(
                    name="jenkins_url",
                    type=NodeParameterType.STRING,
                    description="Jenkins server URL (e.g., https://jenkins.example.com)",
                    required=True
                ),
                NodeParameter(
                    name="username",
                    type=NodeParameterType.STRING,
                    description="Jenkins username for authentication",
                    required=False
                ),
                NodeParameter(
                    name="api_token",
                    type=NodeParameterType.SECRET,
                    description="Jenkins API token for authentication",
                    required=False
                ),
                NodeParameter(
                    name="job_name",
                    type=NodeParameterType.STRING,
                    description="Name of the Jenkins job",
                    required=False
                ),
                NodeParameter(
                    name="build_number",
                    type=NodeParameterType.NUMBER,
                    description="Build number for build operations",
                    required=False
                ),
                NodeParameter(
                    name="job_config",
                    type=NodeParameterType.STRING,
                    description="XML configuration for job creation/update",
                    required=False
                ),
                NodeParameter(
                    name="build_parameters",
                    type=NodeParameterType.OBJECT,
                    description="Parameters for parameterized builds",
                    required=False
                ),
                NodeParameter(
                    name="node_name",
                    type=NodeParameterType.STRING,
                    description="Name of the Jenkins node/computer",
                    required=False
                ),
                NodeParameter(
                    name="view_name",
                    type=NodeParameterType.STRING,
                    description="Name of the Jenkins view",
                    required=False
                ),
                NodeParameter(
                    name="plugin_name",
                    type=NodeParameterType.STRING,
                    description="Name of the Jenkins plugin",
                    required=False
                ),
                NodeParameter(
                    name="plugin_version",
                    type=NodeParameterType.STRING,
                    description="Version of the plugin to install",
                    required=False
                ),
                NodeParameter(
                    name="user_name",
                    type=NodeParameterType.STRING,
                    description="Username for user operations",
                    required=False
                ),
                NodeParameter(
                    name="folder_name",
                    type=NodeParameterType.STRING,
                    description="Name of the Jenkins folder",
                    required=False
                ),
                NodeParameter(
                    name="credential_id",
                    type=NodeParameterType.STRING,
                    description="ID of the credential",
                    required=False
                ),
                NodeParameter(
                    name="queue_id",
                    type=NodeParameterType.NUMBER,
                    description="Queue item ID",
                    required=False
                ),
                NodeParameter(
                    name="wait_for_completion",
                    type=NodeParameterType.BOOLEAN,
                    description="Wait for build completion before returning",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="timeout",
                    type=NodeParameterType.NUMBER,
                    description="Timeout in seconds for operations",
                    required=False,
                    default=300
                ),
                NodeParameter(
                    name="use_crumb",
                    type=NodeParameterType.BOOLEAN,
                    description="Use CSRF protection crumb",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="recursive",
                    type=NodeParameterType.BOOLEAN,
                    description="Recursive operation for folder/view operations",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="depth",
                    type=NodeParameterType.NUMBER,
                    description="API depth parameter for fetching data",
                    required=False,
                    default=1
                ),
                NodeParameter(
                    name="filter",
                    type=NodeParameterType.STRING,
                    description="Filter criteria for list operations",
                    required=False
                ),
                NodeParameter(
                    name="config_data",
                    type=NodeParameterType.OBJECT,
                    description="Configuration data for various operations",
                    required=False
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "job_info": NodeParameterType.OBJECT,
                "jobs": NodeParameterType.ARRAY,
                "build_info": NodeParameterType.OBJECT,
                "builds": NodeParameterType.ARRAY,
                "build_log": NodeParameterType.STRING,
                "build_number": NodeParameterType.NUMBER,
                "build_status": NodeParameterType.STRING,
                "queue_info": NodeParameterType.ARRAY,
                "queue_item": NodeParameterType.OBJECT,
                "nodes": NodeParameterType.ARRAY,
                "node_info": NodeParameterType.OBJECT,
                "plugins": NodeParameterType.ARRAY,
                "plugin_info": NodeParameterType.OBJECT,
                "views": NodeParameterType.ARRAY,
                "view_info": NodeParameterType.OBJECT,
                "users": NodeParameterType.ARRAY,
                "user_info": NodeParameterType.OBJECT,
                "credentials": NodeParameterType.ARRAY,
                "credential_info": NodeParameterType.OBJECT,
                "version": NodeParameterType.STRING,
                "system_info": NodeParameterType.OBJECT,
                "statistics": NodeParameterType.OBJECT,
                "crumb": NodeParameterType.OBJECT,
                "artifacts": NodeParameterType.ARRAY,
                "pipeline_runs": NodeParameterType.ARRAY,
                "pipeline_run": NodeParameterType.OBJECT,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["jenkins", "ci", "cd", "pipeline", "build", "automation", "devops", "api", "integration"],
            author="System",
            documentation_url="https://www.jenkins.io/doc/book/using/remote-access-api/"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for Jenkins URL
        if not params.get("jenkins_url"):
            raise NodeValidationError("Jenkins URL is required")
        
        # Validate authentication
        if not (params.get("username") and params.get("api_token")):
            logger.warning("No authentication provided - some operations may fail")
        
        # Operation-specific validation
        job_operations = [
            JenkinsOperation.CREATE_JOB, JenkinsOperation.UPDATE_JOB, JenkinsOperation.DELETE_JOB,
            JenkinsOperation.GET_JOB_INFO, JenkinsOperation.COPY_JOB, JenkinsOperation.ENABLE_JOB,
            JenkinsOperation.DISABLE_JOB, JenkinsOperation.RENAME_JOB, JenkinsOperation.BUILD_JOB,
            JenkinsOperation.BUILD_JOB_WITH_PARAMS
        ]
        
        build_operations = [
            JenkinsOperation.GET_BUILD_INFO, JenkinsOperation.DELETE_BUILD, JenkinsOperation.GET_BUILD_LOG,
            JenkinsOperation.GET_BUILD_CONSOLE, JenkinsOperation.STOP_BUILD, JenkinsOperation.GET_BUILD_ARTIFACTS
        ]
        
        if operation in job_operations and not params.get("job_name"):
            raise NodeValidationError(f"Job name is required for operation: {operation}")
            
        if operation in build_operations and not params.get("build_number"):
            if operation != JenkinsOperation.GET_BUILD_INFO:  # Can use "lastBuild"
                raise NodeValidationError(f"Build number is required for operation: {operation}")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Jenkins node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Get CSRF crumb if needed
            if validated_data.get("use_crumb", True):
                await self._get_crumb(validated_data)
            
            # Execute the appropriate operation
            if operation == JenkinsOperation.CREATE_JOB:
                return await self._operation_create_job(validated_data)
            elif operation == JenkinsOperation.UPDATE_JOB:
                return await self._operation_update_job(validated_data)
            elif operation == JenkinsOperation.DELETE_JOB:
                return await self._operation_delete_job(validated_data)
            elif operation == JenkinsOperation.GET_JOB_INFO:
                return await self._operation_get_job_info(validated_data)
            elif operation == JenkinsOperation.LIST_JOBS:
                return await self._operation_list_jobs(validated_data)
            elif operation == JenkinsOperation.COPY_JOB:
                return await self._operation_copy_job(validated_data)
            elif operation == JenkinsOperation.ENABLE_JOB:
                return await self._operation_enable_job(validated_data)
            elif operation == JenkinsOperation.DISABLE_JOB:
                return await self._operation_disable_job(validated_data)
            elif operation == JenkinsOperation.BUILD_JOB:
                return await self._operation_build_job(validated_data)
            elif operation == JenkinsOperation.BUILD_JOB_WITH_PARAMS:
                return await self._operation_build_job_with_params(validated_data)
            elif operation == JenkinsOperation.STOP_BUILD:
                return await self._operation_stop_build(validated_data)
            elif operation == JenkinsOperation.GET_BUILD_INFO:
                return await self._operation_get_build_info(validated_data)
            elif operation == JenkinsOperation.DELETE_BUILD:
                return await self._operation_delete_build(validated_data)
            elif operation == JenkinsOperation.GET_BUILD_LOG:
                return await self._operation_get_build_log(validated_data)
            elif operation == JenkinsOperation.GET_BUILD_STATUS:
                return await self._operation_get_build_status(validated_data)
            elif operation == JenkinsOperation.LIST_BUILDS:
                return await self._operation_list_builds(validated_data)
            elif operation == JenkinsOperation.GET_QUEUE_INFO:
                return await self._operation_get_queue_info(validated_data)
            elif operation == JenkinsOperation.CANCEL_QUEUE_ITEM:
                return await self._operation_cancel_queue_item(validated_data)
            elif operation == JenkinsOperation.LIST_NODES:
                return await self._operation_list_nodes(validated_data)
            elif operation == JenkinsOperation.GET_NODE_INFO:
                return await self._operation_get_node_info(validated_data)
            elif operation == JenkinsOperation.CREATE_NODE:
                return await self._operation_create_node(validated_data)
            elif operation == JenkinsOperation.DELETE_NODE:
                return await self._operation_delete_node(validated_data)
            elif operation == JenkinsOperation.LIST_PLUGINS:
                return await self._operation_list_plugins(validated_data)
            elif operation == JenkinsOperation.INSTALL_PLUGIN:
                return await self._operation_install_plugin(validated_data)
            elif operation == JenkinsOperation.LIST_VIEWS:
                return await self._operation_list_views(validated_data)
            elif operation == JenkinsOperation.CREATE_VIEW:
                return await self._operation_create_view(validated_data)
            elif operation == JenkinsOperation.DELETE_VIEW:
                return await self._operation_delete_view(validated_data)
            elif operation == JenkinsOperation.GET_VERSION:
                return await self._operation_get_version(validated_data)
            elif operation == JenkinsOperation.GET_SYSTEM_INFO:
                return await self._operation_get_system_info(validated_data)
            elif operation == JenkinsOperation.RESTART_JENKINS:
                return await self._operation_restart_jenkins(validated_data)
            elif operation == JenkinsOperation.SAFE_RESTART:
                return await self._operation_safe_restart(validated_data)
            elif operation == JenkinsOperation.LIST_USERS:
                return await self._operation_list_users(validated_data)
            elif operation == JenkinsOperation.CREATE_USER:
                return await self._operation_create_user(validated_data)
            elif operation == JenkinsOperation.DELETE_USER:
                return await self._operation_delete_user(validated_data)
            elif operation == JenkinsOperation.LIST_CREDENTIALS:
                return await self._operation_list_credentials(validated_data)
            elif operation == JenkinsOperation.CREATE_CREDENTIAL:
                return await self._operation_create_credential(validated_data)
            elif operation == JenkinsOperation.CREATE_FOLDER:
                return await self._operation_create_folder(validated_data)
            elif operation == JenkinsOperation.DELETE_FOLDER:
                return await self._operation_delete_folder(validated_data)
            elif operation == JenkinsOperation.GET_CRUMB:
                return await self._operation_get_crumb_standalone(validated_data)
            elif operation == JenkinsOperation.GET_BUILD_STATISTICS:
                return await self._operation_get_build_statistics(validated_data)
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
            error_message = f"Error in Jenkins node: {str(e)}"
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
    
    async def _get_crumb(self, params: Dict[str, Any]):
        """Get CSRF crumb for protection."""
        try:
            url = f"{params.get('jenkins_url').rstrip('/')}/crumbIssuer/api/json"
            auth = None
            
            if params.get("username") and params.get("api_token"):
                auth = aiohttp.BasicAuth(params.get("username"), params.get("api_token"))
            
            async with self.session.get(url, auth=auth) as response:
                if response.status == 200:
                    crumb_data = await response.json()
                    self.crumb_issuer = {
                        crumb_data.get("crumbRequestField"): crumb_data.get("crumb")
                    }
                else:
                    logger.warning(f"Could not get CSRF crumb: {response.status}")
        except Exception as e:
            logger.warning(f"Failed to get CSRF crumb: {str(e)}")
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any], 
                          data: Optional[Union[Dict[str, Any], str]] = None,
                          content_type: str = "application/json") -> Dict[str, Any]:
        """Make an HTTP request to the Jenkins API."""
        jenkins_url = params.get("jenkins_url").rstrip("/")
        url = f"{jenkins_url}/{endpoint}"
        
        headers = {}
        if content_type:
            headers["Content-Type"] = content_type
        
        # Add CSRF crumb if available
        if self.crumb_issuer:
            headers.update(self.crumb_issuer)
        
        # Setup authentication
        auth = None
        if params.get("username") and params.get("api_token"):
            auth = aiohttp.BasicAuth(params.get("username"), params.get("api_token"))
        
        try:
            request_kwargs = {"headers": headers, "auth": auth}
            
            if method.upper() in ["POST", "PUT", "PATCH"]:
                if content_type == "application/json" and isinstance(data, dict):
                    request_kwargs["json"] = data
                elif content_type == "application/xml" and isinstance(data, str):
                    request_kwargs["data"] = data
                elif content_type == "application/x-www-form-urlencoded":
                    request_kwargs["data"] = data
                else:
                    request_kwargs["data"] = data
            
            async with self.session.request(method, url, **request_kwargs) as response:
                response_headers = dict(response.headers)
                
                # Handle different response content types
                if response.content_type == 'application/json':
                    response_data = await response.json()
                elif response.content_type == 'text/plain' or 'text' in response.content_type:
                    response_data = await response.text()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Jenkins API error {response.status}: {response_data}"
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
    # Job Operations
    # -------------------------
    
    async def _operation_create_job(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jenkins job."""
        job_name = params.get("job_name")
        job_config = params.get("job_config")
        
        if not job_config:
            # Create a basic freestyle job config if none provided
            job_config = """<?xml version='1.1' encoding='UTF-8'?>
<project>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders/>
  <publishers/>
  <buildWrappers/>
</project>"""
        
        endpoint = f"createItem?name={quote(job_name)}"
        result = await self._make_request("POST", endpoint, params, job_config, "application/xml")
        
        if result["status"] == "success":
            result["job_info"] = {"name": job_name, "created": True}
        
        return result
    
    async def _operation_update_job(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing Jenkins job configuration."""
        job_name = params.get("job_name")
        job_config = params.get("job_config")
        
        endpoint = f"job/{quote(job_name)}/config.xml"
        result = await self._make_request("POST", endpoint, params, job_config, "application/xml")
        
        if result["status"] == "success":
            result["job_info"] = {"name": job_name, "updated": True}
        
        return result
    
    async def _operation_delete_job(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Jenkins job."""
        job_name = params.get("job_name")
        
        endpoint = f"job/{quote(job_name)}/doDelete"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["job_info"] = {"name": job_name, "deleted": True}
        
        return result
    
    async def _operation_get_job_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a Jenkins job."""
        job_name = params.get("job_name")
        depth = params.get("depth", 1)
        
        endpoint = f"job/{quote(job_name)}/api/json?depth={depth}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["job_info"] = result["result"]
        
        return result
    
    async def _operation_list_jobs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all Jenkins jobs."""
        depth = params.get("depth", 1)
        
        endpoint = f"api/json?depth={depth}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            jobs = result["result"].get("jobs", [])
            result["jobs"] = jobs
        
        return result
    
    async def _operation_copy_job(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Copy a Jenkins job."""
        job_name = params.get("job_name")
        new_job_name = params.get("config_data", {}).get("new_name", f"{job_name}_copy")
        
        endpoint = f"createItem?name={quote(new_job_name)}&mode=copy&from={quote(job_name)}"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["job_info"] = {"original": job_name, "copy": new_job_name, "copied": True}
        
        return result
    
    async def _operation_enable_job(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enable a Jenkins job."""
        job_name = params.get("job_name")
        
        endpoint = f"job/{quote(job_name)}/enable"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["job_info"] = {"name": job_name, "enabled": True}
        
        return result
    
    async def _operation_disable_job(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Disable a Jenkins job."""
        job_name = params.get("job_name")
        
        endpoint = f"job/{quote(job_name)}/disable"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["job_info"] = {"name": job_name, "disabled": True}
        
        return result
    
    # -------------------------
    # Build Operations
    # -------------------------
    
    async def _operation_build_job(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a build for a Jenkins job."""
        job_name = params.get("job_name")
        
        endpoint = f"job/{quote(job_name)}/build"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            # If waiting for completion, get the build number and wait
            if params.get("wait_for_completion"):
                await asyncio.sleep(2)  # Wait for build to start
                queue_result = await self._operation_get_queue_info(params)
                if queue_result["status"] == "success":
                    # Find the build number from queue or last build
                    last_build_result = await self._operation_get_build_info({
                        **params, 
                        "build_number": "lastBuild"
                    })
                    if last_build_result["status"] == "success":
                        build_number = last_build_result["build_info"].get("number")
                        result["build_number"] = build_number
                        result["build_info"] = last_build_result["build_info"]
        
        return result
    
    async def _operation_build_job_with_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a parameterized build for a Jenkins job."""
        job_name = params.get("job_name")
        build_params = params.get("build_parameters", {})
        
        # Convert parameters to form data
        form_data = aiohttp.FormData()
        for key, value in build_params.items():
            form_data.add_field(key, str(value))
        
        endpoint = f"job/{quote(job_name)}/buildWithParameters"
        result = await self._make_request("POST", endpoint, params, form_data, "application/x-www-form-urlencoded")
        
        if result["status"] == "success":
            result["build_parameters"] = build_params
        
        return result
    
    async def _operation_stop_build(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop a running build."""
        job_name = params.get("job_name")
        build_number = params.get("build_number")
        
        endpoint = f"job/{quote(job_name)}/{build_number}/stop"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["build_info"] = {"job": job_name, "build_number": build_number, "stopped": True}
        
        return result
    
    async def _operation_get_build_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a specific build."""
        job_name = params.get("job_name")
        build_number = params.get("build_number", "lastBuild")
        depth = params.get("depth", 1)
        
        endpoint = f"job/{quote(job_name)}/{build_number}/api/json?depth={depth}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["build_info"] = result["result"]
            if result["result"]:
                result["build_number"] = result["result"].get("number")
                result["build_status"] = result["result"].get("result", "UNKNOWN")
        
        return result
    
    async def _operation_delete_build(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a specific build."""
        job_name = params.get("job_name")
        build_number = params.get("build_number")
        
        endpoint = f"job/{quote(job_name)}/{build_number}/doDelete"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["build_info"] = {"job": job_name, "build_number": build_number, "deleted": True}
        
        return result
    
    async def _operation_get_build_log(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the console log for a build."""
        job_name = params.get("job_name")
        build_number = params.get("build_number", "lastBuild")
        
        endpoint = f"job/{quote(job_name)}/{build_number}/consoleText"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["build_log"] = result["result"]
        
        return result
    
    async def _operation_get_build_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the status of a build."""
        build_info_result = await self._operation_get_build_info(params)
        
        if build_info_result["status"] == "success":
            build_status = build_info_result["build_info"].get("result", "UNKNOWN")
            build_info_result["build_status"] = build_status
        
        return build_info_result
    
    async def _operation_list_builds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List builds for a job."""
        job_name = params.get("job_name")
        depth = params.get("depth", 1)
        
        endpoint = f"job/{quote(job_name)}/api/json?depth={depth}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            builds = result["result"].get("builds", [])
            result["builds"] = builds
        
        return result
    
    # -------------------------
    # Queue Operations
    # -------------------------
    
    async def _operation_get_queue_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about the build queue."""
        endpoint = "queue/api/json"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            queue_items = result["result"].get("items", [])
            result["queue_info"] = queue_items
        
        return result
    
    async def _operation_cancel_queue_item(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a queued build item."""
        queue_id = params.get("queue_id")
        
        endpoint = f"queue/cancelItem?id={queue_id}"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["queue_item"] = {"id": queue_id, "cancelled": True}
        
        return result
    
    # -------------------------
    # Node Operations
    # -------------------------
    
    async def _operation_list_nodes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all Jenkins nodes."""
        endpoint = "computer/api/json"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            computers = result["result"].get("computer", [])
            result["nodes"] = computers
        
        return result
    
    async def _operation_get_node_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a specific node."""
        node_name = params.get("node_name", "master")
        
        endpoint = f"computer/{quote(node_name)}/api/json"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["node_info"] = result["result"]
        
        return result
    
    async def _operation_create_node(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jenkins node."""
        node_name = params.get("node_name")
        config_data = params.get("config_data", {})
        
        # Basic node configuration
        node_config = {
            "name": node_name,
            "nodeDescription": config_data.get("description", ""),
            "numExecutors": config_data.get("executors", 1),
            "remoteFS": config_data.get("remote_fs", "/tmp"),
            "labelString": config_data.get("labels", ""),
            "mode": config_data.get("mode", "NORMAL"),
            "retentionStrategy": {"stapler-class": "hudson.slaves.RetentionStrategy$Always"},
            "nodeProperties": {"stapler-class-bag": "true"},
            "launcher": {"stapler-class": "hudson.slaves.JNLPLauncher"}
        }
        
        form_data = aiohttp.FormData()
        for key, value in node_config.items():
            if isinstance(value, dict):
                form_data.add_field(key, json.dumps(value))
            else:
                form_data.add_field(key, str(value))
        
        endpoint = "computer/doCreateItem"
        result = await self._make_request("POST", endpoint, params, form_data, "application/x-www-form-urlencoded")
        
        if result["status"] == "success":
            result["node_info"] = {"name": node_name, "created": True}
        
        return result
    
    async def _operation_delete_node(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Jenkins node."""
        node_name = params.get("node_name")
        
        endpoint = f"computer/{quote(node_name)}/doDelete"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["node_info"] = {"name": node_name, "deleted": True}
        
        return result
    
    # -------------------------
    # Plugin Operations
    # -------------------------
    
    async def _operation_list_plugins(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List installed Jenkins plugins."""
        depth = params.get("depth", 1)
        
        endpoint = f"pluginManager/api/json?depth={depth}"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            plugins = result["result"].get("plugins", [])
            result["plugins"] = plugins
        
        return result
    
    async def _operation_install_plugin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Install a Jenkins plugin."""
        plugin_name = params.get("plugin_name")
        plugin_version = params.get("plugin_version")
        
        form_data = aiohttp.FormData()
        if plugin_version:
            form_data.add_field("plugin.name", f"{plugin_name}@{plugin_version}")
        else:
            form_data.add_field("plugin.name", plugin_name)
        
        endpoint = "pluginManager/installNecessaryPlugins"
        result = await self._make_request("POST", endpoint, params, form_data, "application/x-www-form-urlencoded")
        
        if result["status"] == "success":
            result["plugin_info"] = {"name": plugin_name, "version": plugin_version, "installing": True}
        
        return result
    
    # -------------------------
    # View Operations
    # -------------------------
    
    async def _operation_list_views(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all Jenkins views."""
        endpoint = "api/json"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            views = result["result"].get("views", [])
            result["views"] = views
        
        return result
    
    async def _operation_create_view(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jenkins view."""
        view_name = params.get("view_name")
        config_data = params.get("config_data", {})
        
        # Basic list view configuration
        view_config = f"""<?xml version='1.1' encoding='UTF-8'?>
<hudson.model.ListView>
  <description>{config_data.get('description', '')}</description>
  <jobNames>
    <comparator class="hudson.util.CaseInsensitiveComparator"/>
  </jobNames>
  <jobFilters/>
  <columns>
    <hudson.views.StatusColumn/>
    <hudson.views.WeatherColumn/>
    <hudson.views.JobColumn/>
    <hudson.views.LastSuccessColumn/>
    <hudson.views.LastFailureColumn/>
    <hudson.views.LastDurationColumn/>
    <hudson.views.BuildButtonColumn/>
  </columns>
  <includeRegex>{config_data.get('include_regex', '.*')}</includeRegex>
  <recurse>{str(config_data.get('recursive', False)).lower()}</recurse>
</hudson.model.ListView>"""
        
        endpoint = f"createView?name={quote(view_name)}"
        result = await self._make_request("POST", endpoint, params, view_config, "application/xml")
        
        if result["status"] == "success":
            result["view_info"] = {"name": view_name, "created": True}
        
        return result
    
    async def _operation_delete_view(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Jenkins view."""
        view_name = params.get("view_name")
        
        endpoint = f"view/{quote(view_name)}/doDelete"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["view_info"] = {"name": view_name, "deleted": True}
        
        return result
    
    # -------------------------
    # System Operations
    # -------------------------
    
    async def _operation_get_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Jenkins version information."""
        endpoint = "api/json"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            result["version"] = result["result"].get("version", "unknown")
        
        return result
    
    async def _operation_get_system_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Jenkins system information."""
        endpoint = "systemInfo"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["system_info"] = result["result"]
        
        return result
    
    async def _operation_restart_jenkins(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Restart Jenkins server."""
        endpoint = "restart"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["system_info"] = {"action": "restart", "initiated": True}
        
        return result
    
    async def _operation_safe_restart(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Safely restart Jenkins server."""
        endpoint = "safeRestart"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["system_info"] = {"action": "safe_restart", "initiated": True}
        
        return result
    
    # -------------------------
    # User Operations
    # -------------------------
    
    async def _operation_list_users(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Jenkins users."""
        endpoint = "asynchPeople/api/json"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            users = result["result"].get("users", [])
            result["users"] = users
        
        return result
    
    async def _operation_create_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jenkins user."""
        user_data = params.get("config_data", {})
        
        form_data = aiohttp.FormData()
        form_data.add_field("username", user_data.get("username", ""))
        form_data.add_field("password1", user_data.get("password", ""))
        form_data.add_field("password2", user_data.get("password", ""))
        form_data.add_field("fullname", user_data.get("fullname", ""))
        form_data.add_field("email", user_data.get("email", ""))
        
        endpoint = "securityRealm/createAccountByAdmin"
        result = await self._make_request("POST", endpoint, params, form_data, "application/x-www-form-urlencoded")
        
        if result["status"] == "success":
            result["user_info"] = {"username": user_data.get("username"), "created": True}
        
        return result
    
    async def _operation_delete_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Jenkins user."""
        user_name = params.get("user_name")
        
        endpoint = f"user/{quote(user_name)}/doDelete"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["user_info"] = {"username": user_name, "deleted": True}
        
        return result
    
    # -------------------------
    # Credential Operations
    # -------------------------
    
    async def _operation_list_credentials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Jenkins credentials."""
        endpoint = "credentials/store/system/domain/_/api/json"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            credentials = result["result"].get("credentials", [])
            result["credentials"] = credentials
        
        return result
    
    async def _operation_create_credential(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jenkins credential."""
        credential_data = params.get("config_data", {})
        
        # Basic username/password credential JSON
        credential_config = {
            "": "0",
            "credentials": {
                "scope": credential_data.get("scope", "GLOBAL"),
                "id": credential_data.get("id", ""),
                "username": credential_data.get("username", ""),
                "password": credential_data.get("password", ""),
                "description": credential_data.get("description", ""),
                "$class": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl"
            }
        }
        
        endpoint = "credentials/store/system/domain/_/createCredentials"
        result = await self._make_request("POST", endpoint, params, credential_config)
        
        if result["status"] == "success":
            result["credential_info"] = {"id": credential_data.get("id"), "created": True}
        
        return result
    
    # -------------------------
    # Folder Operations
    # -------------------------
    
    async def _operation_create_folder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jenkins folder."""
        folder_name = params.get("folder_name")
        
        endpoint = f"createItem?name={quote(folder_name)}&mode=com.cloudbees.hudson.plugins.folder.Folder"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["folder_info"] = {"name": folder_name, "created": True}
        
        return result
    
    async def _operation_delete_folder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Jenkins folder."""
        folder_name = params.get("folder_name")
        
        endpoint = f"job/{quote(folder_name)}/doDelete"
        result = await self._make_request("POST", endpoint, params)
        
        if result["status"] == "success":
            result["folder_info"] = {"name": folder_name, "deleted": True}
        
        return result
    
    # -------------------------
    # Security Operations
    # -------------------------
    
    async def _operation_get_crumb_standalone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get CSRF crumb information."""
        endpoint = "crumbIssuer/api/json"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["crumb"] = result["result"]
        
        return result
    
    # -------------------------
    # Statistics Operations
    # -------------------------
    
    async def _operation_get_build_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get build statistics."""
        endpoint = "overallLoad/api/json"
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success":
            result["statistics"] = result["result"]
        
        return result


# Utility functions for common Jenkins operations
class JenkinsHelpers:
    """Helper functions for common Jenkins operations."""
    
    @staticmethod
    def create_freestyle_job_config(description: str = "", commands: List[str] = None) -> str:
        """Create a basic freestyle job configuration."""
        commands = commands or []
        build_steps = ""
        
        for command in commands:
            build_steps += f"""
    <hudson.tasks.Shell>
      <command>{command}</command>
    </hudson.tasks.Shell>"""
        
        return f"""<?xml version='1.1' encoding='UTF-8'?>
<project>
  <description>{description}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>{build_steps}
  </builders>
  <publishers/>
  <buildWrappers/>
</project>"""
    
    @staticmethod
    def create_pipeline_job_config(script: str, description: str = "") -> str:
        """Create a pipeline job configuration."""
        return f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@2.40">
  <description>{description}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.87">
    <script>{script}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""
    
    @staticmethod
    def create_node_config(name: str, description: str = "", executors: int = 1, 
                          remote_fs: str = "/tmp", labels: str = "") -> Dict[str, Any]:
        """Create a node configuration."""
        return {
            "name": name,
            "nodeDescription": description,
            "numExecutors": executors,
            "remoteFS": remote_fs,
            "labelString": labels,
            "mode": "NORMAL",
            "retentionStrategy": {"stapler-class": "hudson.slaves.RetentionStrategy$Always"},
            "nodeProperties": {"stapler-class-bag": "true"},
            "launcher": {"stapler-class": "hudson.slaves.JNLPLauncher"}
        }
    
    @staticmethod
    def create_view_config(name: str, description: str = "", include_regex: str = ".*", 
                          recursive: bool = False) -> str:
        """Create a view configuration."""
        return f"""<?xml version='1.1' encoding='UTF-8'?>
<hudson.model.ListView>
  <description>{description}</description>
  <jobNames>
    <comparator class="hudson.util.CaseInsensitiveComparator"/>
  </jobNames>
  <jobFilters/>
  <columns>
    <hudson.views.StatusColumn/>
    <hudson.views.WeatherColumn/>
    <hudson.views.JobColumn/>
    <hudson.views.LastSuccessColumn/>
    <hudson.views.LastFailureColumn/>
    <hudson.views.LastDurationColumn/>
    <hudson.views.BuildButtonColumn/>
  </columns>
  <includeRegex>{include_regex}</includeRegex>
  <recurse>{str(recursive).lower()}</recurse>
</hudson.model.ListView>"""
    
    @staticmethod
    def parse_build_status(status: str) -> Dict[str, Any]:
        """Parse build status into structured information."""
        status_map = {
            "SUCCESS": {"state": "completed", "result": "success"},
            "FAILURE": {"state": "completed", "result": "failure"},
            "UNSTABLE": {"state": "completed", "result": "unstable"},
            "ABORTED": {"state": "completed", "result": "aborted"},
            "NOT_BUILT": {"state": "not_built", "result": "not_built"},
            None: {"state": "running", "result": "running"}
        }
        
        return status_map.get(status, {"state": "unknown", "result": "unknown"})


# Main test function for Jenkins Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Jenkins Node Test Suite ===")
        
        # Get Jenkins configuration from environment or user input
        jenkins_url = os.environ.get("JENKINS_URL")
        jenkins_username = os.environ.get("JENKINS_USERNAME")
        jenkins_token = os.environ.get("JENKINS_API_TOKEN")
        
        if not jenkins_url:
            print("Jenkins configuration not found in environment variables")
            print("Please set JENKINS_URL, JENKINS_USERNAME, JENKINS_API_TOKEN")
            print("Or provide them when prompted...")
            jenkins_url = input("Enter Jenkins URL: ")
            jenkins_username = input("Enter Jenkins username: ")
            jenkins_token = input("Enter Jenkins API token: ")
        
        if not all([jenkins_url, jenkins_username, jenkins_token]):
            print("Jenkins configuration is required for testing")
            return
        
        # Create an instance of the Jenkins Node
        node = JenkinsNode()
        
        # Test cases
        test_cases = [
            {
                "name": "Get Version",
                "params": {
                    "operation": JenkinsOperation.GET_VERSION,
                    "jenkins_url": jenkins_url,
                    "username": jenkins_username,
                    "api_token": jenkins_token
                },
                "expected_status": "success"
            },
            {
                "name": "List Jobs",
                "params": {
                    "operation": JenkinsOperation.LIST_JOBS,
                    "jenkins_url": jenkins_url,
                    "username": jenkins_username,
                    "api_token": jenkins_token
                },
                "expected_status": "success"
            },
            {
                "name": "Get Queue Info",
                "params": {
                    "operation": JenkinsOperation.GET_QUEUE_INFO,
                    "jenkins_url": jenkins_url,
                    "username": jenkins_username,
                    "api_token": jenkins_token
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
                    if result.get("version"):
                        print(f"Jenkins Version: {result['version']}")
                    if result.get("jobs"):
                        print(f"Found {len(result['jobs'])} jobs")
                    if result.get("queue_info"):
                        print(f"Queue items: {len(result['queue_info'])}")
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
    registry.register("jenkins", JenkinsNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register JenkinsNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")