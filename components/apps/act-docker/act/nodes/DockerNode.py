"""
Docker Node - Comprehensive integration with Docker Engine API
Provides access to all Docker operations including container management, image operations, network configuration, volume management, and system administration.
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

class DockerOperation:
    """Operations available on Docker Engine API."""
    
    # Container Operations
    LIST_CONTAINERS = "list_containers"
    CREATE_CONTAINER = "create_container"
    START_CONTAINER = "start_container"
    STOP_CONTAINER = "stop_container"
    RESTART_CONTAINER = "restart_container"
    PAUSE_CONTAINER = "pause_container"
    UNPAUSE_CONTAINER = "unpause_container"
    KILL_CONTAINER = "kill_container"
    REMOVE_CONTAINER = "remove_container"
    INSPECT_CONTAINER = "inspect_container"
    GET_CONTAINER_LOGS = "get_container_logs"
    GET_CONTAINER_STATS = "get_container_stats"
    EXEC_CONTAINER = "exec_container"
    
    # Image Operations
    LIST_IMAGES = "list_images"
    PULL_IMAGE = "pull_image"
    BUILD_IMAGE = "build_image"
    PUSH_IMAGE = "push_image"
    REMOVE_IMAGE = "remove_image"
    TAG_IMAGE = "tag_image"
    INSPECT_IMAGE = "inspect_image"
    SEARCH_IMAGES = "search_images"
    PRUNE_IMAGES = "prune_images"
    EXPORT_IMAGE = "export_image"
    IMPORT_IMAGE = "import_image"
    
    # Network Operations
    LIST_NETWORKS = "list_networks"
    CREATE_NETWORK = "create_network"
    REMOVE_NETWORK = "remove_network"
    INSPECT_NETWORK = "inspect_network"
    CONNECT_CONTAINER = "connect_container"
    DISCONNECT_CONTAINER = "disconnect_container"
    PRUNE_NETWORKS = "prune_networks"
    
    # Volume Operations
    LIST_VOLUMES = "list_volumes"
    CREATE_VOLUME = "create_volume"
    REMOVE_VOLUME = "remove_volume"
    INSPECT_VOLUME = "inspect_volume"
    PRUNE_VOLUMES = "prune_volumes"
    
    # System Operations
    GET_SYSTEM_INFO = "get_system_info"
    GET_VERSION = "get_version"
    PING_DAEMON = "ping_daemon"
    GET_EVENTS = "get_events"
    SYSTEM_DF = "system_df"
    SYSTEM_PRUNE = "system_prune"

class DockerNode(BaseNode):
    """
    Node for interacting with Docker Engine API.
    Provides comprehensive functionality for container management, image operations, network configuration, and system administration.
    """
    
    BASE_URL = "http://localhost"
    UNIX_SOCKET = "/var/run/docker.sock"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        self.connector = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Docker node."""
        return NodeSchema(
            node_type="docker",
            version="1.0.0",
            description="Comprehensive integration with Docker Engine API for container management, image operations, network configuration, and system administration",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Docker API",
                    required=True,
                    enum=[
                        DockerOperation.LIST_CONTAINERS,
                        DockerOperation.CREATE_CONTAINER,
                        DockerOperation.START_CONTAINER,
                        DockerOperation.STOP_CONTAINER,
                        DockerOperation.RESTART_CONTAINER,
                        DockerOperation.PAUSE_CONTAINER,
                        DockerOperation.UNPAUSE_CONTAINER,
                        DockerOperation.KILL_CONTAINER,
                        DockerOperation.REMOVE_CONTAINER,
                        DockerOperation.INSPECT_CONTAINER,
                        DockerOperation.GET_CONTAINER_LOGS,
                        DockerOperation.GET_CONTAINER_STATS,
                        DockerOperation.EXEC_CONTAINER,
                        DockerOperation.LIST_IMAGES,
                        DockerOperation.PULL_IMAGE,
                        DockerOperation.BUILD_IMAGE,
                        DockerOperation.PUSH_IMAGE,
                        DockerOperation.REMOVE_IMAGE,
                        DockerOperation.TAG_IMAGE,
                        DockerOperation.INSPECT_IMAGE,
                        DockerOperation.SEARCH_IMAGES,
                        DockerOperation.PRUNE_IMAGES,
                        DockerOperation.EXPORT_IMAGE,
                        DockerOperation.IMPORT_IMAGE,
                        DockerOperation.LIST_NETWORKS,
                        DockerOperation.CREATE_NETWORK,
                        DockerOperation.REMOVE_NETWORK,
                        DockerOperation.INSPECT_NETWORK,
                        DockerOperation.CONNECT_CONTAINER,
                        DockerOperation.DISCONNECT_CONTAINER,
                        DockerOperation.PRUNE_NETWORKS,
                        DockerOperation.LIST_VOLUMES,
                        DockerOperation.CREATE_VOLUME,
                        DockerOperation.REMOVE_VOLUME,
                        DockerOperation.INSPECT_VOLUME,
                        DockerOperation.PRUNE_VOLUMES,
                        DockerOperation.GET_SYSTEM_INFO,
                        DockerOperation.GET_VERSION,
                        DockerOperation.PING_DAEMON,
                        DockerOperation.GET_EVENTS,
                        DockerOperation.SYSTEM_DF,
                        DockerOperation.SYSTEM_PRUNE
                    ]
                ),
                NodeParameter(
                    name="docker_host",
                    type=NodeParameterType.STRING,
                    description="Docker daemon host (unix socket or TCP address)",
                    required=False,
                    default="unix:///var/run/docker.sock"
                ),
                NodeParameter(
                    name="api_version",
                    type=NodeParameterType.STRING,
                    description="Docker API version to use",
                    required=False,
                    default="1.41"
                ),
                NodeParameter(
                    name="container_id",
                    type=NodeParameterType.STRING,
                    description="Container ID or name for operations",
                    required=False
                ),
                NodeParameter(
                    name="image_name",
                    type=NodeParameterType.STRING,
                    description="Docker image name with optional tag",
                    required=False
                ),
                NodeParameter(
                    name="container_name",
                    type=NodeParameterType.STRING,
                    description="Name for new container",
                    required=False
                ),
                NodeParameter(
                    name="command",
                    type=NodeParameterType.ARRAY,
                    description="Command to run in container",
                    required=False
                ),
                NodeParameter(
                    name="environment",
                    type=NodeParameterType.ARRAY,
                    description="Environment variables for container",
                    required=False
                ),
                NodeParameter(
                    name="ports",
                    type=NodeParameterType.OBJECT,
                    description="Port mappings for container",
                    required=False
                ),
                NodeParameter(
                    name="volumes",
                    type=NodeParameterType.ARRAY,
                    description="Volume mounts for container",
                    required=False
                ),
                NodeParameter(
                    name="working_dir",
                    type=NodeParameterType.STRING,
                    description="Working directory for container",
                    required=False
                ),
                NodeParameter(
                    name="network_name",
                    type=NodeParameterType.STRING,
                    description="Network name for operations",
                    required=False
                ),
                NodeParameter(
                    name="volume_name",
                    type=NodeParameterType.STRING,
                    description="Volume name for operations",
                    required=False
                ),
                NodeParameter(
                    name="dockerfile",
                    type=NodeParameterType.STRING,
                    description="Dockerfile content or path for build operations",
                    required=False
                ),
                NodeParameter(
                    name="build_context",
                    type=NodeParameterType.STRING,
                    description="Build context (base64 encoded tar or path)",
                    required=False
                ),
                NodeParameter(
                    name="tag",
                    type=NodeParameterType.STRING,
                    description="Tag for image operations",
                    required=False
                ),
                NodeParameter(
                    name="registry_url",
                    type=NodeParameterType.STRING,
                    description="Container registry URL",
                    required=False
                ),
                NodeParameter(
                    name="username",
                    type=NodeParameterType.STRING,
                    description="Registry username for authentication",
                    required=False
                ),
                NodeParameter(
                    name="password",
                    type=NodeParameterType.SECRET,
                    description="Registry password for authentication",
                    required=False
                ),
                NodeParameter(
                    name="all_containers",
                    type=NodeParameterType.BOOLEAN,
                    description="Include stopped containers in listing",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="follow_logs",
                    type=NodeParameterType.BOOLEAN,
                    description="Follow container logs stream",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="tail_logs",
                    type=NodeParameterType.NUMBER,
                    description="Number of log lines to tail",
                    required=False,
                    default=100
                ),
                NodeParameter(
                    name="since_timestamp",
                    type=NodeParameterType.STRING,
                    description="Show logs since timestamp (ISO format)",
                    required=False
                ),
                NodeParameter(
                    name="force",
                    type=NodeParameterType.BOOLEAN,
                    description="Force operation (remove, prune, etc.)",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="remove_volumes",
                    type=NodeParameterType.BOOLEAN,
                    description="Remove associated volumes when removing container",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="build_args",
                    type=NodeParameterType.OBJECT,
                    description="Build arguments for image build",
                    required=False
                ),
                NodeParameter(
                    name="labels",
                    type=NodeParameterType.OBJECT,
                    description="Labels for container or image",
                    required=False
                ),
                NodeParameter(
                    name="restart_policy",
                    type=NodeParameterType.STRING,
                    description="Container restart policy",
                    required=False,
                    enum=["no", "always", "unless-stopped", "on-failure"]
                ),
                NodeParameter(
                    name="memory_limit",
                    type=NodeParameterType.STRING,
                    description="Memory limit for container (e.g., '512m', '1g')",
                    required=False
                ),
                NodeParameter(
                    name="cpu_limit",
                    type=NodeParameterType.NUMBER,
                    description="CPU limit for container (number of CPUs)",
                    required=False
                ),
                NodeParameter(
                    name="privileged",
                    type=NodeParameterType.BOOLEAN,
                    description="Run container in privileged mode",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="detach",
                    type=NodeParameterType.BOOLEAN,
                    description="Run container in detached mode",
                    required=False,
                    default=True
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "containers": NodeParameterType.ARRAY,
                "container_info": NodeParameterType.OBJECT,
                "container_id": NodeParameterType.STRING,
                "container_logs": NodeParameterType.STRING,
                "container_stats": NodeParameterType.OBJECT,
                "images": NodeParameterType.ARRAY,
                "image_info": NodeParameterType.OBJECT,
                "image_id": NodeParameterType.STRING,
                "networks": NodeParameterType.ARRAY,
                "network_info": NodeParameterType.OBJECT,
                "network_id": NodeParameterType.STRING,
                "volumes": NodeParameterType.ARRAY,
                "volume_info": NodeParameterType.OBJECT,
                "volume_name": NodeParameterType.STRING,
                "system_info": NodeParameterType.OBJECT,
                "version_info": NodeParameterType.OBJECT,
                "events": NodeParameterType.ARRAY,
                "build_logs": NodeParameterType.ARRAY,
                "exec_output": NodeParameterType.STRING,
                "search_results": NodeParameterType.ARRAY,
                "prune_results": NodeParameterType.OBJECT,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["docker", "container", "orchestration", "deployment", "api", "integration"],
            author="System",
            documentation_url="https://docs.docker.com/engine/api/"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Validate operation-specific requirements
        if operation in [DockerOperation.CREATE_CONTAINER]:
            if not params.get("image_name"):
                raise NodeValidationError("Image name is required for container creation")
                
        elif operation in [DockerOperation.START_CONTAINER, DockerOperation.STOP_CONTAINER,
                          DockerOperation.RESTART_CONTAINER, DockerOperation.PAUSE_CONTAINER,
                          DockerOperation.UNPAUSE_CONTAINER, DockerOperation.KILL_CONTAINER,
                          DockerOperation.REMOVE_CONTAINER, DockerOperation.INSPECT_CONTAINER,
                          DockerOperation.GET_CONTAINER_LOGS, DockerOperation.GET_CONTAINER_STATS,
                          DockerOperation.EXEC_CONTAINER]:
            if not params.get("container_id"):
                raise NodeValidationError("Container ID is required for this operation")
                
        elif operation in [DockerOperation.PULL_IMAGE, DockerOperation.PUSH_IMAGE,
                          DockerOperation.REMOVE_IMAGE, DockerOperation.TAG_IMAGE,
                          DockerOperation.INSPECT_IMAGE]:
            if not params.get("image_name"):
                raise NodeValidationError("Image name is required for this operation")
                
        elif operation in [DockerOperation.BUILD_IMAGE]:
            if not params.get("dockerfile") and not params.get("build_context"):
                raise NodeValidationError("Dockerfile or build context is required for image build")
                
        elif operation in [DockerOperation.CREATE_NETWORK, DockerOperation.REMOVE_NETWORK,
                          DockerOperation.INSPECT_NETWORK]:
            if not params.get("network_name"):
                raise NodeValidationError("Network name is required for this operation")
                
        elif operation in [DockerOperation.CONNECT_CONTAINER, DockerOperation.DISCONNECT_CONTAINER]:
            if not params.get("container_id") or not params.get("network_name"):
                raise NodeValidationError("Container ID and network name are required for this operation")
                
        elif operation in [DockerOperation.CREATE_VOLUME, DockerOperation.REMOVE_VOLUME,
                          DockerOperation.INSPECT_VOLUME]:
            if not params.get("volume_name"):
                raise NodeValidationError("Volume name is required for this operation")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Docker node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session(validated_data)
            
            # Execute the appropriate operation
            if operation == DockerOperation.LIST_CONTAINERS:
                return await self._operation_list_containers(validated_data)
            elif operation == DockerOperation.CREATE_CONTAINER:
                return await self._operation_create_container(validated_data)
            elif operation == DockerOperation.START_CONTAINER:
                return await self._operation_start_container(validated_data)
            elif operation == DockerOperation.STOP_CONTAINER:
                return await self._operation_stop_container(validated_data)
            elif operation == DockerOperation.RESTART_CONTAINER:
                return await self._operation_restart_container(validated_data)
            elif operation == DockerOperation.PAUSE_CONTAINER:
                return await self._operation_pause_container(validated_data)
            elif operation == DockerOperation.UNPAUSE_CONTAINER:
                return await self._operation_unpause_container(validated_data)
            elif operation == DockerOperation.KILL_CONTAINER:
                return await self._operation_kill_container(validated_data)
            elif operation == DockerOperation.REMOVE_CONTAINER:
                return await self._operation_remove_container(validated_data)
            elif operation == DockerOperation.INSPECT_CONTAINER:
                return await self._operation_inspect_container(validated_data)
            elif operation == DockerOperation.GET_CONTAINER_LOGS:
                return await self._operation_get_container_logs(validated_data)
            elif operation == DockerOperation.GET_CONTAINER_STATS:
                return await self._operation_get_container_stats(validated_data)
            elif operation == DockerOperation.EXEC_CONTAINER:
                return await self._operation_exec_container(validated_data)
            elif operation == DockerOperation.LIST_IMAGES:
                return await self._operation_list_images(validated_data)
            elif operation == DockerOperation.PULL_IMAGE:
                return await self._operation_pull_image(validated_data)
            elif operation == DockerOperation.BUILD_IMAGE:
                return await self._operation_build_image(validated_data)
            elif operation == DockerOperation.PUSH_IMAGE:
                return await self._operation_push_image(validated_data)
            elif operation == DockerOperation.REMOVE_IMAGE:
                return await self._operation_remove_image(validated_data)
            elif operation == DockerOperation.TAG_IMAGE:
                return await self._operation_tag_image(validated_data)
            elif operation == DockerOperation.INSPECT_IMAGE:
                return await self._operation_inspect_image(validated_data)
            elif operation == DockerOperation.SEARCH_IMAGES:
                return await self._operation_search_images(validated_data)
            elif operation == DockerOperation.PRUNE_IMAGES:
                return await self._operation_prune_images(validated_data)
            elif operation == DockerOperation.LIST_NETWORKS:
                return await self._operation_list_networks(validated_data)
            elif operation == DockerOperation.CREATE_NETWORK:
                return await self._operation_create_network(validated_data)
            elif operation == DockerOperation.REMOVE_NETWORK:
                return await self._operation_remove_network(validated_data)
            elif operation == DockerOperation.INSPECT_NETWORK:
                return await self._operation_inspect_network(validated_data)
            elif operation == DockerOperation.CONNECT_CONTAINER:
                return await self._operation_connect_container(validated_data)
            elif operation == DockerOperation.DISCONNECT_CONTAINER:
                return await self._operation_disconnect_container(validated_data)
            elif operation == DockerOperation.PRUNE_NETWORKS:
                return await self._operation_prune_networks(validated_data)
            elif operation == DockerOperation.LIST_VOLUMES:
                return await self._operation_list_volumes(validated_data)
            elif operation == DockerOperation.CREATE_VOLUME:
                return await self._operation_create_volume(validated_data)
            elif operation == DockerOperation.REMOVE_VOLUME:
                return await self._operation_remove_volume(validated_data)
            elif operation == DockerOperation.INSPECT_VOLUME:
                return await self._operation_inspect_volume(validated_data)
            elif operation == DockerOperation.PRUNE_VOLUMES:
                return await self._operation_prune_volumes(validated_data)
            elif operation == DockerOperation.GET_SYSTEM_INFO:
                return await self._operation_get_system_info(validated_data)
            elif operation == DockerOperation.GET_VERSION:
                return await self._operation_get_version(validated_data)
            elif operation == DockerOperation.PING_DAEMON:
                return await self._operation_ping_daemon(validated_data)
            elif operation == DockerOperation.GET_EVENTS:
                return await self._operation_get_events(validated_data)
            elif operation == DockerOperation.SYSTEM_DF:
                return await self._operation_system_df(validated_data)
            elif operation == DockerOperation.SYSTEM_PRUNE:
                return await self._operation_system_prune(validated_data)
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
            error_message = f"Error in Docker node: {str(e)}"
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
    
    async def _init_session(self, params: Dict[str, Any]):
        """Initialize HTTP session with Docker daemon."""
        if not self.session:
            docker_host = params.get("docker_host", "unix:///var/run/docker.sock")
            
            if docker_host.startswith("unix://"):
                # Unix socket connection
                socket_path = docker_host[7:]  # Remove 'unix://' prefix
                self.connector = aiohttp.UnixConnector(path=socket_path)
                self.session = aiohttp.ClientSession(connector=self.connector)
            else:
                # TCP connection
                ssl_context = ssl.create_default_context()
                ssl_context.load_verify_locations(certifi.where())
                self.connector = aiohttp.TCPConnector(ssl=ssl_context)
                self.session = aiohttp.ClientSession(connector=self.connector)
    
    async def _cleanup_session(self):
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
        if self.connector:
            await self.connector.close()
            self.connector = None
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any], 
                          data: Optional[Dict[str, Any]] = None, 
                          query_params: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the Docker API."""
        api_version = params.get("api_version", "1.41")
        docker_host = params.get("docker_host", "unix:///var/run/docker.sock")
        
        if docker_host.startswith("unix://"):
            url = f"http://localhost/v{api_version}/{endpoint}"
        else:
            url = f"{docker_host}/v{api_version}/{endpoint}"
        
        request_headers = {
            "Content-Type": "application/json"
        }
        if headers:
            request_headers.update(headers)
        
        try:
            async with self.session.request(
                method, url, 
                headers=request_headers, 
                json=data,
                params=query_params
            ) as response:
                response_headers = dict(response.headers)
                
                # Handle different response content types
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Docker API error {response.status}: {response_data}"
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
    # Container Operations
    # -------------------------
    
    async def _operation_list_containers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Docker containers."""
        all_containers = params.get("all_containers", False)
        
        query_params = {
            "all": str(all_containers).lower()
        }
        
        result = await self._make_request("GET", "containers/json", params, query_params=query_params)
        
        if result["status"] == "success":
            result["containers"] = result["result"]
        
        return result
    
    async def _operation_create_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Docker container."""
        image_name = params.get("image_name")
        container_name = params.get("container_name")
        command = params.get("command", [])
        environment = params.get("environment", [])
        ports = params.get("ports", {})
        volumes = params.get("volumes", [])
        working_dir = params.get("working_dir")
        labels = params.get("labels", {})
        restart_policy = params.get("restart_policy", "no")
        memory_limit = params.get("memory_limit")
        cpu_limit = params.get("cpu_limit")
        privileged = params.get("privileged", False)
        detach = params.get("detach", True)
        
        container_config = {
            "Image": image_name,
            "Env": environment,
            "Labels": labels,
            "AttachStdin": not detach,
            "AttachStdout": not detach,
            "AttachStderr": not detach,
            "Tty": not detach
        }
        
        if command:
            container_config["Cmd"] = command
        if working_dir:
            container_config["WorkingDir"] = working_dir
        
        host_config = {
            "RestartPolicy": {"Name": restart_policy},
            "Privileged": privileged
        }
        
        if ports:
            container_config["ExposedPorts"] = {port: {} for port in ports.keys()}
            host_config["PortBindings"] = ports
            
        if volumes:
            binds = []
            for volume in volumes:
                if isinstance(volume, str):
                    binds.append(volume)
                elif isinstance(volume, dict):
                    source = volume.get("source")
                    target = volume.get("target")
                    mode = volume.get("mode", "rw")
                    if source and target:
                        binds.append(f"{source}:{target}:{mode}")
            if binds:
                host_config["Binds"] = binds
                
        if memory_limit:
            host_config["Memory"] = DockerHelpers.parse_memory_limit(memory_limit)
        if cpu_limit:
            host_config["NanoCpus"] = int(cpu_limit * 1e9)
        
        request_data = {
            **container_config,
            "HostConfig": host_config
        }
        
        query_params = {}
        if container_name:
            query_params["name"] = container_name
        
        result = await self._make_request("POST", "containers/create", params, 
                                        data=request_data, query_params=query_params)
        
        if result["status"] == "success":
            result["container_id"] = result["result"].get("Id")
        
        return result
    
    async def _operation_start_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start a Docker container."""
        container_id = params.get("container_id")
        
        result = await self._make_request("POST", f"containers/{container_id}/start", params)
        return result
    
    async def _operation_stop_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop a Docker container."""
        container_id = params.get("container_id")
        timeout = params.get("timeout", 10)
        
        query_params = {"t": timeout}
        
        result = await self._make_request("POST", f"containers/{container_id}/stop", params, 
                                        query_params=query_params)
        return result
    
    async def _operation_restart_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Restart a Docker container."""
        container_id = params.get("container_id")
        timeout = params.get("timeout", 10)
        
        query_params = {"t": timeout}
        
        result = await self._make_request("POST", f"containers/{container_id}/restart", params, 
                                        query_params=query_params)
        return result
    
    async def _operation_pause_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Pause a Docker container."""
        container_id = params.get("container_id")
        
        result = await self._make_request("POST", f"containers/{container_id}/pause", params)
        return result
    
    async def _operation_unpause_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unpause a Docker container."""
        container_id = params.get("container_id")
        
        result = await self._make_request("POST", f"containers/{container_id}/unpause", params)
        return result
    
    async def _operation_kill_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Kill a Docker container."""
        container_id = params.get("container_id")
        signal = params.get("signal", "SIGKILL")
        
        query_params = {"signal": signal}
        
        result = await self._make_request("POST", f"containers/{container_id}/kill", params, 
                                        query_params=query_params)
        return result
    
    async def _operation_remove_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a Docker container."""
        container_id = params.get("container_id")
        force = params.get("force", False)
        remove_volumes = params.get("remove_volumes", False)
        
        query_params = {
            "force": str(force).lower(),
            "v": str(remove_volumes).lower()
        }
        
        result = await self._make_request("DELETE", f"containers/{container_id}", params, 
                                        query_params=query_params)
        return result
    
    async def _operation_inspect_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect a Docker container."""
        container_id = params.get("container_id")
        
        result = await self._make_request("GET", f"containers/{container_id}/json", params)
        
        if result["status"] == "success":
            result["container_info"] = result["result"]
        
        return result
    
    async def _operation_get_container_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get logs from a Docker container."""
        container_id = params.get("container_id")
        follow = params.get("follow_logs", False)
        tail = params.get("tail_logs", 100)
        since = params.get("since_timestamp")
        
        query_params = {
            "stdout": "true",
            "stderr": "true",
            "follow": str(follow).lower(),
            "tail": str(tail)
        }
        
        if since:
            query_params["since"] = since
        
        result = await self._make_request("GET", f"containers/{container_id}/logs", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["container_logs"] = result["result"]
        
        return result
    
    async def _operation_get_container_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics from a Docker container."""
        container_id = params.get("container_id")
        stream = params.get("stream", False)
        
        query_params = {
            "stream": str(stream).lower()
        }
        
        result = await self._make_request("GET", f"containers/{container_id}/stats", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["container_stats"] = result["result"]
        
        return result
    
    async def _operation_exec_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command in a Docker container."""
        container_id = params.get("container_id")
        command = params.get("command", [])
        
        if isinstance(command, str):
            command = ["/bin/sh", "-c", command]
        
        # Create exec instance
        exec_config = {
            "Cmd": command,
            "AttachStdin": False,
            "AttachStdout": True,
            "AttachStderr": True,
            "Tty": False
        }
        
        exec_result = await self._make_request("POST", f"containers/{container_id}/exec", params, 
                                             data=exec_config)
        
        if exec_result["status"] != "success":
            return exec_result
        
        exec_id = exec_result["result"].get("Id")
        
        # Start exec
        start_config = {
            "Detach": False,
            "Tty": False
        }
        
        result = await self._make_request("POST", f"exec/{exec_id}/start", params, 
                                        data=start_config)
        
        if result["status"] == "success":
            result["exec_output"] = result["result"]
        
        return result
    
    # -------------------------
    # Image Operations
    # -------------------------
    
    async def _operation_list_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Docker images."""
        all_images = params.get("all_containers", False)  # Reuse parameter
        
        query_params = {
            "all": str(all_images).lower()
        }
        
        result = await self._make_request("GET", "images/json", params, query_params=query_params)
        
        if result["status"] == "success":
            result["images"] = result["result"]
        
        return result
    
    async def _operation_pull_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Pull a Docker image."""
        image_name = params.get("image_name")
        tag = params.get("tag", "latest")
        
        if ":" not in image_name:
            image_name = f"{image_name}:{tag}"
        
        query_params = {"fromImage": image_name}
        
        # Add registry authentication if provided
        auth_header = {}
        username = params.get("username")
        password = params.get("password")
        if username and password:
            auth_config = {
                "username": username,
                "password": password
            }
            auth_header["X-Registry-Auth"] = base64.b64encode(
                json.dumps(auth_config).encode()
            ).decode()
        
        result = await self._make_request("POST", "images/create", params, 
                                        query_params=query_params, headers=auth_header)
        return result
    
    async def _operation_build_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Build a Docker image."""
        dockerfile = params.get("dockerfile")
        build_context = params.get("build_context")
        tag = params.get("tag")
        build_args = params.get("build_args", {})
        labels = params.get("labels", {})
        
        query_params = {}
        if tag:
            query_params["t"] = tag
        
        # Handle build context
        if build_context:
            if build_context.startswith("/"):
                # Local path - would need to tar it up
                return {
                    "status": "error",
                    "error": "Local path build context not supported in this implementation",
                    "result": None,
                    "status_code": None,
                    "response_headers": None
                }
            else:
                # Assume base64 encoded tar
                try:
                    context_data = base64.b64decode(build_context)
                except Exception as e:
                    return {
                        "status": "error",
                        "error": f"Invalid build context: {str(e)}",
                        "result": None,
                        "status_code": None,
                        "response_headers": None
                    }
        else:
            # Create minimal context with Dockerfile
            import tarfile
            import io
            
            tar_buffer = io.BytesIO()
            with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
                dockerfile_info = tarfile.TarInfo(name='Dockerfile')
                dockerfile_content = dockerfile.encode('utf-8')
                dockerfile_info.size = len(dockerfile_content)
                tar.addfile(dockerfile_info, io.BytesIO(dockerfile_content))
            
            context_data = tar_buffer.getvalue()
        
        headers = {
            "Content-Type": "application/x-tar"
        }
        
        # This would need special handling for streaming tar data
        # For now, return a placeholder
        return {
            "status": "error",
            "error": "Image build not fully implemented in this version",
            "result": None,
            "status_code": None,
            "response_headers": None
        }
    
    async def _operation_push_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Push a Docker image to registry."""
        image_name = params.get("image_name")
        tag = params.get("tag", "latest")
        
        if ":" not in image_name:
            image_name = f"{image_name}:{tag}"
        
        # Add registry authentication if provided
        auth_header = {}
        username = params.get("username")
        password = params.get("password")
        if username and password:
            auth_config = {
                "username": username,
                "password": password
            }
            auth_header["X-Registry-Auth"] = base64.b64encode(
                json.dumps(auth_config).encode()
            ).decode()
        
        result = await self._make_request("POST", f"images/{image_name}/push", params, 
                                        headers=auth_header)
        return result
    
    async def _operation_remove_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a Docker image."""
        image_name = params.get("image_name")
        force = params.get("force", False)
        no_prune = params.get("no_prune", False)
        
        query_params = {
            "force": str(force).lower(),
            "noprune": str(no_prune).lower()
        }
        
        result = await self._make_request("DELETE", f"images/{image_name}", params, 
                                        query_params=query_params)
        return result
    
    async def _operation_tag_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tag a Docker image."""
        image_name = params.get("image_name")
        tag = params.get("tag")
        repo = params.get("repository", image_name)
        
        query_params = {
            "repo": repo,
            "tag": tag
        }
        
        result = await self._make_request("POST", f"images/{image_name}/tag", params, 
                                        query_params=query_params)
        return result
    
    async def _operation_inspect_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect a Docker image."""
        image_name = params.get("image_name")
        
        result = await self._make_request("GET", f"images/{image_name}/json", params)
        
        if result["status"] == "success":
            result["image_info"] = result["result"]
        
        return result
    
    async def _operation_search_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for Docker images."""
        term = params.get("search_term", params.get("image_name", ""))
        limit = params.get("limit", 25)
        
        query_params = {
            "term": term,
            "limit": limit
        }
        
        result = await self._make_request("GET", "images/search", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["search_results"] = result["result"]
        
        return result
    
    async def _operation_prune_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prune unused Docker images."""
        filters = params.get("filters", {})
        
        query_params = {}
        if filters:
            query_params["filters"] = json.dumps(filters)
        
        result = await self._make_request("POST", "images/prune", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["prune_results"] = result["result"]
        
        return result
    
    # -------------------------
    # Network Operations
    # -------------------------
    
    async def _operation_list_networks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Docker networks."""
        result = await self._make_request("GET", "networks", params)
        
        if result["status"] == "success":
            result["networks"] = result["result"]
        
        return result
    
    async def _operation_create_network(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Docker network."""
        network_name = params.get("network_name")
        driver = params.get("driver", "bridge")
        labels = params.get("labels", {})
        
        request_data = {
            "Name": network_name,
            "Driver": driver,
            "Labels": labels
        }
        
        result = await self._make_request("POST", "networks/create", params, data=request_data)
        
        if result["status"] == "success":
            result["network_id"] = result["result"].get("Id")
        
        return result
    
    async def _operation_remove_network(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a Docker network."""
        network_name = params.get("network_name")
        
        result = await self._make_request("DELETE", f"networks/{network_name}", params)
        return result
    
    async def _operation_inspect_network(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect a Docker network."""
        network_name = params.get("network_name")
        
        result = await self._make_request("GET", f"networks/{network_name}", params)
        
        if result["status"] == "success":
            result["network_info"] = result["result"]
        
        return result
    
    async def _operation_connect_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Connect a container to a network."""
        network_name = params.get("network_name")
        container_id = params.get("container_id")
        
        request_data = {
            "Container": container_id
        }
        
        result = await self._make_request("POST", f"networks/{network_name}/connect", params, 
                                        data=request_data)
        return result
    
    async def _operation_disconnect_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Disconnect a container from a network."""
        network_name = params.get("network_name")
        container_id = params.get("container_id")
        force = params.get("force", False)
        
        request_data = {
            "Container": container_id,
            "Force": force
        }
        
        result = await self._make_request("POST", f"networks/{network_name}/disconnect", params, 
                                        data=request_data)
        return result
    
    async def _operation_prune_networks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prune unused Docker networks."""
        filters = params.get("filters", {})
        
        query_params = {}
        if filters:
            query_params["filters"] = json.dumps(filters)
        
        result = await self._make_request("POST", "networks/prune", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["prune_results"] = result["result"]
        
        return result
    
    # -------------------------
    # Volume Operations
    # -------------------------
    
    async def _operation_list_volumes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Docker volumes."""
        result = await self._make_request("GET", "volumes", params)
        
        if result["status"] == "success":
            result["volumes"] = result["result"].get("Volumes", [])
        
        return result
    
    async def _operation_create_volume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Docker volume."""
        volume_name = params.get("volume_name")
        driver = params.get("driver", "local")
        labels = params.get("labels", {})
        
        request_data = {
            "Name": volume_name,
            "Driver": driver,
            "Labels": labels
        }
        
        result = await self._make_request("POST", "volumes/create", params, data=request_data)
        
        if result["status"] == "success":
            result["volume_name"] = result["result"].get("Name")
        
        return result
    
    async def _operation_remove_volume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a Docker volume."""
        volume_name = params.get("volume_name")
        force = params.get("force", False)
        
        query_params = {
            "force": str(force).lower()
        }
        
        result = await self._make_request("DELETE", f"volumes/{volume_name}", params, 
                                        query_params=query_params)
        return result
    
    async def _operation_inspect_volume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect a Docker volume."""
        volume_name = params.get("volume_name")
        
        result = await self._make_request("GET", f"volumes/{volume_name}", params)
        
        if result["status"] == "success":
            result["volume_info"] = result["result"]
        
        return result
    
    async def _operation_prune_volumes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prune unused Docker volumes."""
        filters = params.get("filters", {})
        
        query_params = {}
        if filters:
            query_params["filters"] = json.dumps(filters)
        
        result = await self._make_request("POST", "volumes/prune", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["prune_results"] = result["result"]
        
        return result
    
    # -------------------------
    # System Operations
    # -------------------------
    
    async def _operation_get_system_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Docker system information."""
        result = await self._make_request("GET", "info", params)
        
        if result["status"] == "success":
            result["system_info"] = result["result"]
        
        return result
    
    async def _operation_get_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Docker version information."""
        result = await self._make_request("GET", "version", params)
        
        if result["status"] == "success":
            result["version_info"] = result["result"]
        
        return result
    
    async def _operation_ping_daemon(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ping Docker daemon."""
        result = await self._make_request("GET", "_ping", params)
        
        if result["status"] == "success":
            result["ping_result"] = "OK"
        
        return result
    
    async def _operation_get_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Docker system events."""
        since = params.get("since_timestamp")
        until = params.get("until_timestamp")
        filters = params.get("filters", {})
        
        query_params = {}
        if since:
            query_params["since"] = since
        if until:
            query_params["until"] = until
        if filters:
            query_params["filters"] = json.dumps(filters)
        
        result = await self._make_request("GET", "events", params, query_params=query_params)
        
        if result["status"] == "success":
            result["events"] = result["result"]
        
        return result
    
    async def _operation_system_df(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Docker system disk usage."""
        result = await self._make_request("GET", "system/df", params)
        
        if result["status"] == "success":
            result["disk_usage"] = result["result"]
        
        return result
    
    async def _operation_system_prune(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prune Docker system (containers, images, networks, volumes)."""
        filters = params.get("filters", {})
        
        query_params = {}
        if filters:
            query_params["filters"] = json.dumps(filters)
        
        result = await self._make_request("POST", "system/prune", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["prune_results"] = result["result"]
        
        return result


# Utility functions for common Docker operations
class DockerHelpers:
    """Helper functions for common Docker operations."""
    
    @staticmethod
    def parse_memory_limit(memory_str: str) -> int:
        """Parse memory limit string to bytes."""
        memory_str = memory_str.lower()
        if memory_str.endswith('k'):
            return int(memory_str[:-1]) * 1024
        elif memory_str.endswith('m'):
            return int(memory_str[:-1]) * 1024 * 1024
        elif memory_str.endswith('g'):
            return int(memory_str[:-1]) * 1024 * 1024 * 1024
        else:
            return int(memory_str)
    
    @staticmethod
    def create_port_binding(container_port: int, host_port: int, protocol: str = "tcp") -> Dict[str, Any]:
        """Create a port binding configuration."""
        return {
            f"{container_port}/{protocol}": [{"HostPort": str(host_port)}]
        }
    
    @staticmethod
    def create_volume_mount(source: str, target: str, mode: str = "rw") -> str:
        """Create a volume mount string."""
        return f"{source}:{target}:{mode}"
    
    @staticmethod
    def create_environment_vars(env_dict: Dict[str, str]) -> List[str]:
        """Convert environment dictionary to Docker format."""
        return [f"{key}={value}" for key, value in env_dict.items()]
    
    @staticmethod
    def format_container_status(container: Dict[str, Any]) -> str:
        """Format container status for display."""
        state = container.get("State", "unknown")
        status = container.get("Status", "")
        return f"{state} ({status})" if status else state


# Main test function for Docker Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Docker Node Test Suite ===")
        
        # Create an instance of the Docker Node
        node = DockerNode()
        
        # Test cases (these require Docker daemon to be running)
        test_cases = [
            {
                "name": "Ping Docker Daemon",
                "params": {
                    "operation": DockerOperation.PING_DAEMON
                },
                "expected_status": "success"
            },
            {
                "name": "Get Docker Version",
                "params": {
                    "operation": DockerOperation.GET_VERSION
                },
                "expected_status": "success"
            },
            {
                "name": "List Docker Containers",
                "params": {
                    "operation": DockerOperation.LIST_CONTAINERS,
                    "all_containers": True
                },
                "expected_status": "success"
            },
            {
                "name": "List Docker Images",
                "params": {
                    "operation": DockerOperation.LIST_IMAGES
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
                    if result.get("version_info"):
                        version = result["version_info"].get("Version", "Unknown")
                        print(f"Docker Version: {version}")
                    if result.get("containers"):
                        print(f"Containers found: {len(result['containers'])}")
                    if result.get("images"):
                        print(f"Images found: {len(result['images'])}")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
                # Add a delay between tests
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")
        
        if passed_tests < total_tests:
            print("\nNote: Some tests may fail if Docker daemon is not running or accessible")
        
        print("\nAll tests completed!")

    # Run the async tests
    asyncio.run(run_tests())

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("docker", DockerNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register DockerNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")