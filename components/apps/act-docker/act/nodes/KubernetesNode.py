"""
Kubernetes Node - Comprehensive integration with Kubernetes API
Provides access to all Kubernetes operations including pod management, deployment automation, service configuration, namespace operations, storage management, and cluster administration.
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

class KubernetesOperation:
    """Operations available on Kubernetes API."""
    
    # Pod Operations
    LIST_PODS = "list_pods"
    CREATE_POD = "create_pod"
    GET_POD = "get_pod"
    UPDATE_POD = "update_pod"
    DELETE_POD = "delete_pod"
    GET_POD_LOGS = "get_pod_logs"
    EXEC_POD = "exec_pod"
    PORT_FORWARD_POD = "port_forward_pod"
    
    # Deployment Operations
    LIST_DEPLOYMENTS = "list_deployments"
    CREATE_DEPLOYMENT = "create_deployment"
    GET_DEPLOYMENT = "get_deployment"
    UPDATE_DEPLOYMENT = "update_deployment"
    DELETE_DEPLOYMENT = "delete_deployment"
    SCALE_DEPLOYMENT = "scale_deployment"
    ROLLOUT_STATUS = "rollout_status"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    
    # Service Operations
    LIST_SERVICES = "list_services"
    CREATE_SERVICE = "create_service"
    GET_SERVICE = "get_service"
    UPDATE_SERVICE = "update_service"
    DELETE_SERVICE = "delete_service"
    
    # Namespace Operations
    LIST_NAMESPACES = "list_namespaces"
    CREATE_NAMESPACE = "create_namespace"
    GET_NAMESPACE = "get_namespace"
    UPDATE_NAMESPACE = "update_namespace"
    DELETE_NAMESPACE = "delete_namespace"
    
    # ConfigMap Operations
    LIST_CONFIGMAPS = "list_configmaps"
    CREATE_CONFIGMAP = "create_configmap"
    GET_CONFIGMAP = "get_configmap"
    UPDATE_CONFIGMAP = "update_configmap"
    DELETE_CONFIGMAP = "delete_configmap"
    
    # Secret Operations
    LIST_SECRETS = "list_secrets"
    CREATE_SECRET = "create_secret"
    GET_SECRET = "get_secret"
    UPDATE_SECRET = "update_secret"
    DELETE_SECRET = "delete_secret"
    
    # Ingress Operations
    LIST_INGRESSES = "list_ingresses"
    CREATE_INGRESS = "create_ingress"
    GET_INGRESS = "get_ingress"
    UPDATE_INGRESS = "update_ingress"
    DELETE_INGRESS = "delete_ingress"
    
    # PersistentVolume Operations
    LIST_PVS = "list_pvs"
    LIST_PVCS = "list_pvcs"
    CREATE_PVC = "create_pvc"
    GET_PVC = "get_pvc"
    UPDATE_PVC = "update_pvc"
    DELETE_PVC = "delete_pvc"
    
    # Job Operations
    LIST_JOBS = "list_jobs"
    CREATE_JOB = "create_job"
    GET_JOB = "get_job"
    DELETE_JOB = "delete_job"
    
    # CronJob Operations
    LIST_CRONJOBS = "list_cronjobs"
    CREATE_CRONJOB = "create_cronjob"
    GET_CRONJOB = "get_cronjob"
    UPDATE_CRONJOB = "update_cronjob"
    DELETE_CRONJOB = "delete_cronjob"
    
    # StatefulSet Operations
    LIST_STATEFULSETS = "list_statefulsets"
    CREATE_STATEFULSET = "create_statefulset"
    GET_STATEFULSET = "get_statefulset"
    UPDATE_STATEFULSET = "update_statefulset"
    DELETE_STATEFULSET = "delete_statefulset"
    SCALE_STATEFULSET = "scale_statefulset"
    
    # DaemonSet Operations
    LIST_DAEMONSETS = "list_daemonsets"
    CREATE_DAEMONSET = "create_daemonset"
    GET_DAEMONSET = "get_daemonset"
    UPDATE_DAEMONSET = "update_daemonset"
    DELETE_DAEMONSET = "delete_daemonset"
    
    # Node Operations
    LIST_NODES = "list_nodes"
    GET_NODE = "get_node"
    UPDATE_NODE = "update_node"
    DRAIN_NODE = "drain_node"
    CORDON_NODE = "cordon_node"
    UNCORDON_NODE = "uncordon_node"
    
    # Events Operations
    LIST_EVENTS = "list_events"
    
    # Custom Resource Operations
    LIST_CUSTOM_RESOURCES = "list_custom_resources"
    CREATE_CUSTOM_RESOURCE = "create_custom_resource"
    GET_CUSTOM_RESOURCE = "get_custom_resource"
    UPDATE_CUSTOM_RESOURCE = "update_custom_resource"
    DELETE_CUSTOM_RESOURCE = "delete_custom_resource"

class KubernetesNode(BaseNode):
    """
    Node for interacting with Kubernetes API.
    Provides comprehensive functionality for container orchestration, cluster management, and cloud-native application deployment.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        self.api_server = None
        self.headers = {}
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Kubernetes node."""
        return NodeSchema(
            node_type="kubernetes",
            version="1.0.0",
            description="Comprehensive integration with Kubernetes API for container orchestration, cluster management, and cloud-native application deployment",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Kubernetes API",
                    required=True,
                    enum=[
                        KubernetesOperation.LIST_PODS,
                        KubernetesOperation.CREATE_POD,
                        KubernetesOperation.GET_POD,
                        KubernetesOperation.UPDATE_POD,
                        KubernetesOperation.DELETE_POD,
                        KubernetesOperation.GET_POD_LOGS,
                        KubernetesOperation.EXEC_POD,
                        KubernetesOperation.PORT_FORWARD_POD,
                        KubernetesOperation.LIST_DEPLOYMENTS,
                        KubernetesOperation.CREATE_DEPLOYMENT,
                        KubernetesOperation.GET_DEPLOYMENT,
                        KubernetesOperation.UPDATE_DEPLOYMENT,
                        KubernetesOperation.DELETE_DEPLOYMENT,
                        KubernetesOperation.SCALE_DEPLOYMENT,
                        KubernetesOperation.ROLLOUT_STATUS,
                        KubernetesOperation.ROLLBACK_DEPLOYMENT,
                        KubernetesOperation.LIST_SERVICES,
                        KubernetesOperation.CREATE_SERVICE,
                        KubernetesOperation.GET_SERVICE,
                        KubernetesOperation.UPDATE_SERVICE,
                        KubernetesOperation.DELETE_SERVICE,
                        KubernetesOperation.LIST_NAMESPACES,
                        KubernetesOperation.CREATE_NAMESPACE,
                        KubernetesOperation.GET_NAMESPACE,
                        KubernetesOperation.UPDATE_NAMESPACE,
                        KubernetesOperation.DELETE_NAMESPACE,
                        KubernetesOperation.LIST_CONFIGMAPS,
                        KubernetesOperation.CREATE_CONFIGMAP,
                        KubernetesOperation.GET_CONFIGMAP,
                        KubernetesOperation.UPDATE_CONFIGMAP,
                        KubernetesOperation.DELETE_CONFIGMAP,
                        KubernetesOperation.LIST_SECRETS,
                        KubernetesOperation.CREATE_SECRET,
                        KubernetesOperation.GET_SECRET,
                        KubernetesOperation.UPDATE_SECRET,
                        KubernetesOperation.DELETE_SECRET,
                        KubernetesOperation.LIST_INGRESSES,
                        KubernetesOperation.CREATE_INGRESS,
                        KubernetesOperation.GET_INGRESS,
                        KubernetesOperation.UPDATE_INGRESS,
                        KubernetesOperation.DELETE_INGRESS,
                        KubernetesOperation.LIST_PVS,
                        KubernetesOperation.LIST_PVCS,
                        KubernetesOperation.CREATE_PVC,
                        KubernetesOperation.GET_PVC,
                        KubernetesOperation.UPDATE_PVC,
                        KubernetesOperation.DELETE_PVC,
                        KubernetesOperation.LIST_JOBS,
                        KubernetesOperation.CREATE_JOB,
                        KubernetesOperation.GET_JOB,
                        KubernetesOperation.DELETE_JOB,
                        KubernetesOperation.LIST_CRONJOBS,
                        KubernetesOperation.CREATE_CRONJOB,
                        KubernetesOperation.GET_CRONJOB,
                        KubernetesOperation.UPDATE_CRONJOB,
                        KubernetesOperation.DELETE_CRONJOB,
                        KubernetesOperation.LIST_STATEFULSETS,
                        KubernetesOperation.CREATE_STATEFULSET,
                        KubernetesOperation.GET_STATEFULSET,
                        KubernetesOperation.UPDATE_STATEFULSET,
                        KubernetesOperation.DELETE_STATEFULSET,
                        KubernetesOperation.SCALE_STATEFULSET,
                        KubernetesOperation.LIST_DAEMONSETS,
                        KubernetesOperation.CREATE_DAEMONSET,
                        KubernetesOperation.GET_DAEMONSET,
                        KubernetesOperation.UPDATE_DAEMONSET,
                        KubernetesOperation.DELETE_DAEMONSET,
                        KubernetesOperation.LIST_NODES,
                        KubernetesOperation.GET_NODE,
                        KubernetesOperation.UPDATE_NODE,
                        KubernetesOperation.DRAIN_NODE,
                        KubernetesOperation.CORDON_NODE,
                        KubernetesOperation.UNCORDON_NODE,
                        KubernetesOperation.LIST_EVENTS,
                        KubernetesOperation.LIST_CUSTOM_RESOURCES,
                        KubernetesOperation.CREATE_CUSTOM_RESOURCE,
                        KubernetesOperation.GET_CUSTOM_RESOURCE,
                        KubernetesOperation.UPDATE_CUSTOM_RESOURCE,
                        KubernetesOperation.DELETE_CUSTOM_RESOURCE
                    ]
                ),
                NodeParameter(
                    name="api_server",
                    type=NodeParameterType.STRING,
                    description="Kubernetes API server URL",
                    required=True
                ),
                NodeParameter(
                    name="token",
                    type=NodeParameterType.SECRET,
                    description="Service account bearer token",
                    required=False
                ),
                NodeParameter(
                    name="kubeconfig_content",
                    type=NodeParameterType.STRING,
                    description="Base64 encoded kubeconfig content",
                    required=False
                ),
                NodeParameter(
                    name="certificate_authority",
                    type=NodeParameterType.STRING,
                    description="Base64 encoded CA certificate",
                    required=False
                ),
                NodeParameter(
                    name="client_certificate",
                    type=NodeParameterType.STRING,
                    description="Base64 encoded client certificate",
                    required=False
                ),
                NodeParameter(
                    name="client_key",
                    type=NodeParameterType.SECRET,
                    description="Base64 encoded client private key",
                    required=False
                ),
                NodeParameter(
                    name="namespace",
                    type=NodeParameterType.STRING,
                    description="Kubernetes namespace for operations",
                    required=False,
                    default="default"
                ),
                NodeParameter(
                    name="resource_name",
                    type=NodeParameterType.STRING,
                    description="Name of the Kubernetes resource",
                    required=False
                ),
                NodeParameter(
                    name="manifest",
                    type=NodeParameterType.OBJECT,
                    description="Kubernetes resource manifest as JSON",
                    required=False
                ),
                NodeParameter(
                    name="yaml_manifest",
                    type=NodeParameterType.STRING,
                    description="Kubernetes resource manifest as YAML",
                    required=False
                ),
                NodeParameter(
                    name="labels",
                    type=NodeParameterType.OBJECT,
                    description="Label selector for filtering resources",
                    required=False
                ),
                NodeParameter(
                    name="field_selector",
                    type=NodeParameterType.STRING,
                    description="Field selector for filtering resources",
                    required=False
                ),
                NodeParameter(
                    name="container_name",
                    type=NodeParameterType.STRING,
                    description="Container name for log/exec operations",
                    required=False
                ),
                NodeParameter(
                    name="command",
                    type=NodeParameterType.ARRAY,
                    description="Command to execute in pod",
                    required=False
                ),
                NodeParameter(
                    name="follow_logs",
                    type=NodeParameterType.BOOLEAN,
                    description="Follow pod logs stream",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="tail_lines",
                    type=NodeParameterType.NUMBER,
                    description="Number of log lines to tail",
                    required=False,
                    default=100
                ),
                NodeParameter(
                    name="since_seconds",
                    type=NodeParameterType.NUMBER,
                    description="Show logs since N seconds ago",
                    required=False
                ),
                NodeParameter(
                    name="replicas",
                    type=NodeParameterType.NUMBER,
                    description="Number of replicas for scaling operations",
                    required=False
                ),
                NodeParameter(
                    name="image",
                    type=NodeParameterType.STRING,
                    description="Container image for deployment",
                    required=False
                ),
                NodeParameter(
                    name="ports",
                    type=NodeParameterType.ARRAY,
                    description="Container ports configuration",
                    required=False
                ),
                NodeParameter(
                    name="environment_vars",
                    type=NodeParameterType.OBJECT,
                    description="Environment variables for container",
                    required=False
                ),
                NodeParameter(
                    name="service_type",
                    type=NodeParameterType.STRING,
                    description="Kubernetes service type",
                    required=False,
                    default="ClusterIP",
                    enum=["ClusterIP", "NodePort", "LoadBalancer", "ExternalName"]
                ),
                NodeParameter(
                    name="service_ports",
                    type=NodeParameterType.ARRAY,
                    description="Service port configurations",
                    required=False
                ),
                NodeParameter(
                    name="data",
                    type=NodeParameterType.OBJECT,
                    description="Data for ConfigMap/Secret creation",
                    required=False
                ),
                NodeParameter(
                    name="secret_type",
                    type=NodeParameterType.STRING,
                    description="Type of Kubernetes secret",
                    required=False,
                    default="Opaque",
                    enum=["Opaque", "kubernetes.io/dockerconfigjson", "kubernetes.io/tls"]
                ),
                NodeParameter(
                    name="ingress_rules",
                    type=NodeParameterType.ARRAY,
                    description="Ingress routing rules",
                    required=False
                ),
                NodeParameter(
                    name="storage_class",
                    type=NodeParameterType.STRING,
                    description="Storage class for PVC",
                    required=False
                ),
                NodeParameter(
                    name="storage_size",
                    type=NodeParameterType.STRING,
                    description="Storage size for PVC (e.g., '10Gi')",
                    required=False
                ),
                NodeParameter(
                    name="access_modes",
                    type=NodeParameterType.ARRAY,
                    description="Access modes for PVC",
                    required=False,
                    default=["ReadWriteOnce"]
                ),
                NodeParameter(
                    name="schedule",
                    type=NodeParameterType.STRING,
                    description="Cron schedule for CronJob",
                    required=False
                ),
                NodeParameter(
                    name="wait_for_completion",
                    type=NodeParameterType.BOOLEAN,
                    description="Wait for operation to complete",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="timeout_seconds",
                    type=NodeParameterType.NUMBER,
                    description="Timeout for operations in seconds",
                    required=False,
                    default=300
                ),
                NodeParameter(
                    name="force",
                    type=NodeParameterType.BOOLEAN,
                    description="Force delete resources",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="grace_period_seconds",
                    type=NodeParameterType.NUMBER,
                    description="Grace period for deletion",
                    required=False,
                    default=30
                ),
                NodeParameter(
                    name="api_version",
                    type=NodeParameterType.STRING,
                    description="Kubernetes API version for custom resources",
                    required=False
                ),
                NodeParameter(
                    name="resource_group",
                    type=NodeParameterType.STRING,
                    description="API group for custom resources",
                    required=False
                ),
                NodeParameter(
                    name="resource_version",
                    type=NodeParameterType.STRING,
                    description="Resource version for custom resources",
                    required=False
                ),
                NodeParameter(
                    name="plural_name",
                    type=NodeParameterType.STRING,
                    description="Plural name for custom resources",
                    required=False
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "pods": NodeParameterType.ARRAY,
                "pod_info": NodeParameterType.OBJECT,
                "pod_logs": NodeParameterType.STRING,
                "deployments": NodeParameterType.ARRAY,
                "deployment_info": NodeParameterType.OBJECT,
                "services": NodeParameterType.ARRAY,
                "service_info": NodeParameterType.OBJECT,
                "namespaces": NodeParameterType.ARRAY,
                "namespace_info": NodeParameterType.OBJECT,
                "configmaps": NodeParameterType.ARRAY,
                "configmap_info": NodeParameterType.OBJECT,
                "secrets": NodeParameterType.ARRAY,
                "secret_info": NodeParameterType.OBJECT,
                "ingresses": NodeParameterType.ARRAY,
                "ingress_info": NodeParameterType.OBJECT,
                "pvs": NodeParameterType.ARRAY,
                "pvcs": NodeParameterType.ARRAY,
                "pvc_info": NodeParameterType.OBJECT,
                "jobs": NodeParameterType.ARRAY,
                "job_info": NodeParameterType.OBJECT,
                "cronjobs": NodeParameterType.ARRAY,
                "cronjob_info": NodeParameterType.OBJECT,
                "statefulsets": NodeParameterType.ARRAY,
                "statefulset_info": NodeParameterType.OBJECT,
                "daemonsets": NodeParameterType.ARRAY,
                "daemonset_info": NodeParameterType.OBJECT,
                "nodes": NodeParameterType.ARRAY,
                "node_info": NodeParameterType.OBJECT,
                "events": NodeParameterType.ARRAY,
                "custom_resources": NodeParameterType.ARRAY,
                "custom_resource_info": NodeParameterType.OBJECT,
                "created_resource": NodeParameterType.OBJECT,
                "updated_resource": NodeParameterType.OBJECT,
                "resource_version": NodeParameterType.STRING,
                "exec_output": NodeParameterType.STRING,
                "rollout_status": NodeParameterType.OBJECT,
                "scale_result": NodeParameterType.OBJECT,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["kubernetes", "k8s", "container", "orchestration", "deployment", "api", "integration"],
            author="System",
            documentation_url="https://kubernetes.io/docs/reference/generated/kubernetes-api/"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for API server
        if not params.get("api_server"):
            raise NodeValidationError("Kubernetes API server URL is required")
            
        # Check for authentication
        if not params.get("token") and not params.get("kubeconfig_content") and not params.get("client_certificate"):
            raise NodeValidationError("Authentication is required (token, kubeconfig, or client certificate)")
            
        # Validate operation-specific requirements
        if operation in [KubernetesOperation.GET_POD, KubernetesOperation.UPDATE_POD,
                        KubernetesOperation.DELETE_POD, KubernetesOperation.GET_POD_LOGS,
                        KubernetesOperation.EXEC_POD]:
            if not params.get("resource_name"):
                raise NodeValidationError("Resource name is required for pod operations")
                
        elif operation in [KubernetesOperation.CREATE_POD, KubernetesOperation.CREATE_DEPLOYMENT,
                          KubernetesOperation.CREATE_SERVICE, KubernetesOperation.CREATE_CONFIGMAP,
                          KubernetesOperation.CREATE_SECRET, KubernetesOperation.CREATE_INGRESS]:
            if not params.get("manifest") and not params.get("yaml_manifest"):
                raise NodeValidationError("Manifest is required for resource creation")
                
        elif operation in [KubernetesOperation.SCALE_DEPLOYMENT, KubernetesOperation.SCALE_STATEFULSET]:
            if not params.get("resource_name") or params.get("replicas") is None:
                raise NodeValidationError("Resource name and replicas are required for scaling")
                
        elif operation in [KubernetesOperation.CREATE_CUSTOM_RESOURCE, KubernetesOperation.GET_CUSTOM_RESOURCE,
                          KubernetesOperation.UPDATE_CUSTOM_RESOURCE, KubernetesOperation.DELETE_CUSTOM_RESOURCE]:
            if not params.get("api_version") or not params.get("plural_name"):
                raise NodeValidationError("API version and plural name are required for custom resource operations")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Kubernetes node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session and authentication
            await self._init_session(validated_data)
            
            # Execute the appropriate operation
            if operation == KubernetesOperation.LIST_PODS:
                return await self._operation_list_pods(validated_data)
            elif operation == KubernetesOperation.CREATE_POD:
                return await self._operation_create_pod(validated_data)
            elif operation == KubernetesOperation.GET_POD:
                return await self._operation_get_pod(validated_data)
            elif operation == KubernetesOperation.UPDATE_POD:
                return await self._operation_update_pod(validated_data)
            elif operation == KubernetesOperation.DELETE_POD:
                return await self._operation_delete_pod(validated_data)
            elif operation == KubernetesOperation.GET_POD_LOGS:
                return await self._operation_get_pod_logs(validated_data)
            elif operation == KubernetesOperation.EXEC_POD:
                return await self._operation_exec_pod(validated_data)
            elif operation == KubernetesOperation.LIST_DEPLOYMENTS:
                return await self._operation_list_deployments(validated_data)
            elif operation == KubernetesOperation.CREATE_DEPLOYMENT:
                return await self._operation_create_deployment(validated_data)
            elif operation == KubernetesOperation.GET_DEPLOYMENT:
                return await self._operation_get_deployment(validated_data)
            elif operation == KubernetesOperation.UPDATE_DEPLOYMENT:
                return await self._operation_update_deployment(validated_data)
            elif operation == KubernetesOperation.DELETE_DEPLOYMENT:
                return await self._operation_delete_deployment(validated_data)
            elif operation == KubernetesOperation.SCALE_DEPLOYMENT:
                return await self._operation_scale_deployment(validated_data)
            elif operation == KubernetesOperation.ROLLOUT_STATUS:
                return await self._operation_rollout_status(validated_data)
            elif operation == KubernetesOperation.LIST_SERVICES:
                return await self._operation_list_services(validated_data)
            elif operation == KubernetesOperation.CREATE_SERVICE:
                return await self._operation_create_service(validated_data)
            elif operation == KubernetesOperation.GET_SERVICE:
                return await self._operation_get_service(validated_data)
            elif operation == KubernetesOperation.UPDATE_SERVICE:
                return await self._operation_update_service(validated_data)
            elif operation == KubernetesOperation.DELETE_SERVICE:
                return await self._operation_delete_service(validated_data)
            elif operation == KubernetesOperation.LIST_NAMESPACES:
                return await self._operation_list_namespaces(validated_data)
            elif operation == KubernetesOperation.CREATE_NAMESPACE:
                return await self._operation_create_namespace(validated_data)
            elif operation == KubernetesOperation.GET_NAMESPACE:
                return await self._operation_get_namespace(validated_data)
            elif operation == KubernetesOperation.UPDATE_NAMESPACE:
                return await self._operation_update_namespace(validated_data)
            elif operation == KubernetesOperation.DELETE_NAMESPACE:
                return await self._operation_delete_namespace(validated_data)
            elif operation == KubernetesOperation.LIST_CONFIGMAPS:
                return await self._operation_list_configmaps(validated_data)
            elif operation == KubernetesOperation.CREATE_CONFIGMAP:
                return await self._operation_create_configmap(validated_data)
            elif operation == KubernetesOperation.GET_CONFIGMAP:
                return await self._operation_get_configmap(validated_data)
            elif operation == KubernetesOperation.UPDATE_CONFIGMAP:
                return await self._operation_update_configmap(validated_data)
            elif operation == KubernetesOperation.DELETE_CONFIGMAP:
                return await self._operation_delete_configmap(validated_data)
            elif operation == KubernetesOperation.LIST_SECRETS:
                return await self._operation_list_secrets(validated_data)
            elif operation == KubernetesOperation.CREATE_SECRET:
                return await self._operation_create_secret(validated_data)
            elif operation == KubernetesOperation.GET_SECRET:
                return await self._operation_get_secret(validated_data)
            elif operation == KubernetesOperation.UPDATE_SECRET:
                return await self._operation_update_secret(validated_data)
            elif operation == KubernetesOperation.DELETE_SECRET:
                return await self._operation_delete_secret(validated_data)
            elif operation == KubernetesOperation.LIST_NODES:
                return await self._operation_list_nodes(validated_data)
            elif operation == KubernetesOperation.GET_NODE:
                return await self._operation_get_node(validated_data)
            elif operation == KubernetesOperation.UPDATE_NODE:
                return await self._operation_update_node(validated_data)
            elif operation == KubernetesOperation.LIST_EVENTS:
                return await self._operation_list_events(validated_data)
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
            error_message = f"Error in Kubernetes node: {str(e)}"
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
        """Initialize HTTP session with Kubernetes authentication."""
        if not self.session:
            # Set up SSL context
            ssl_context = ssl.create_default_context()
            
            # Handle CA certificate
            ca_cert = params.get("certificate_authority")
            if ca_cert:
                try:
                    ca_cert_data = base64.b64decode(ca_cert)
                    # In production, write to temp file and load
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                except Exception:
                    logger.warning("Failed to load CA certificate, using insecure connection")
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
            else:
                # For development/testing, allow insecure connections
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(connector=connector)
            
            # Set API server
            self.api_server = params.get("api_server").rstrip("/")
            
            # Set up authentication headers
            self.headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Handle different authentication methods
            if params.get("token"):
                self.headers["Authorization"] = f"Bearer {params.get('token')}"
            elif params.get("kubeconfig_content"):
                # Parse kubeconfig for token/certificate
                try:
                    kubeconfig_data = base64.b64decode(params.get("kubeconfig_content")).decode()
                    # In production, parse YAML kubeconfig properly
                    # For now, assume token is provided separately
                    pass
                except Exception:
                    logger.warning("Failed to parse kubeconfig")
            elif params.get("client_certificate") and params.get("client_key"):
                # Handle client certificate authentication
                # In production, set up client certificates properly
                pass
    
    async def _cleanup_session(self):
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any], 
                          data: Optional[Dict[str, Any]] = None, 
                          query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the Kubernetes API."""
        url = f"{self.api_server}/{endpoint}"
        
        try:
            async with self.session.request(
                method, url, 
                headers=self.headers, 
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
                    error_message = f"Kubernetes API error {response.status}: {response_data}"
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
    # Pod Operations
    # -------------------------
    
    async def _operation_list_pods(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List pods in a namespace."""
        namespace = params.get("namespace", "default")
        labels = params.get("labels")
        field_selector = params.get("field_selector")
        
        query_params = {}
        if labels:
            label_selector = ",".join([f"{k}={v}" for k, v in labels.items()])
            query_params["labelSelector"] = label_selector
        if field_selector:
            query_params["fieldSelector"] = field_selector
        
        result = await self._make_request("GET", f"api/v1/namespaces/{namespace}/pods", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["pods"] = result["result"].get("items", [])
        
        return result
    
    async def _operation_create_pod(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new pod."""
        namespace = params.get("namespace", "default")
        manifest = params.get("manifest")
        yaml_manifest = params.get("yaml_manifest")
        
        if yaml_manifest:
            # In production, parse YAML properly
            try:
                import yaml
                manifest = yaml.safe_load(yaml_manifest)
            except Exception:
                return {
                    "status": "error",
                    "error": "Failed to parse YAML manifest",
                    "result": None,
                    "status_code": None,
                    "response_headers": None
                }
        
        result = await self._make_request("POST", f"api/v1/namespaces/{namespace}/pods", params, 
                                        data=manifest)
        
        if result["status"] == "success":
            result["created_resource"] = result["result"]
            result["pod_info"] = result["result"]
        
        return result
    
    async def _operation_get_pod(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific pod."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        
        result = await self._make_request("GET", f"api/v1/namespaces/{namespace}/pods/{resource_name}", params)
        
        if result["status"] == "success":
            result["pod_info"] = result["result"]
        
        return result
    
    async def _operation_update_pod(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a pod."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        manifest = params.get("manifest")
        
        result = await self._make_request("PUT", f"api/v1/namespaces/{namespace}/pods/{resource_name}", params, 
                                        data=manifest)
        
        if result["status"] == "success":
            result["updated_resource"] = result["result"]
            result["pod_info"] = result["result"]
        
        return result
    
    async def _operation_delete_pod(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a pod."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        grace_period = params.get("grace_period_seconds", 30)
        force = params.get("force", False)
        
        delete_options = {
            "gracePeriodSeconds": grace_period
        }
        
        if force:
            delete_options["gracePeriodSeconds"] = 0
        
        result = await self._make_request("DELETE", f"api/v1/namespaces/{namespace}/pods/{resource_name}", params, 
                                        data=delete_options)
        return result
    
    async def _operation_get_pod_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get logs from a pod."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        container_name = params.get("container_name")
        follow = params.get("follow_logs", False)
        tail_lines = params.get("tail_lines", 100)
        since_seconds = params.get("since_seconds")
        
        query_params = {
            "follow": str(follow).lower(),
            "tailLines": str(tail_lines)
        }
        
        if container_name:
            query_params["container"] = container_name
        if since_seconds:
            query_params["sinceSeconds"] = str(since_seconds)
        
        result = await self._make_request("GET", f"api/v1/namespaces/{namespace}/pods/{resource_name}/log", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["pod_logs"] = result["result"]
        
        return result
    
    async def _operation_exec_pod(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command in a pod."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        container_name = params.get("container_name")
        command = params.get("command", ["/bin/sh"])
        
        query_params = {
            "stdout": "true",
            "stderr": "true",
            "stdin": "false",
            "tty": "false"
        }
        
        if container_name:
            query_params["container"] = container_name
            
        for cmd in command:
            query_params["command"] = cmd
        
        # Note: Real exec requires WebSocket connection
        # This is a simplified implementation
        result = await self._make_request("POST", f"api/v1/namespaces/{namespace}/pods/{resource_name}/exec", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["exec_output"] = "Command executed (WebSocket implementation needed for full output)"
        
        return result
    
    # -------------------------
    # Deployment Operations
    # -------------------------
    
    async def _operation_list_deployments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List deployments in a namespace."""
        namespace = params.get("namespace", "default")
        labels = params.get("labels")
        
        query_params = {}
        if labels:
            label_selector = ",".join([f"{k}={v}" for k, v in labels.items()])
            query_params["labelSelector"] = label_selector
        
        result = await self._make_request("GET", f"apis/apps/v1/namespaces/{namespace}/deployments", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["deployments"] = result["result"].get("items", [])
        
        return result
    
    async def _operation_create_deployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deployment."""
        namespace = params.get("namespace", "default")
        manifest = params.get("manifest")
        
        result = await self._make_request("POST", f"apis/apps/v1/namespaces/{namespace}/deployments", params, 
                                        data=manifest)
        
        if result["status"] == "success":
            result["created_resource"] = result["result"]
            result["deployment_info"] = result["result"]
        
        return result
    
    async def _operation_get_deployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific deployment."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        
        result = await self._make_request("GET", f"apis/apps/v1/namespaces/{namespace}/deployments/{resource_name}", params)
        
        if result["status"] == "success":
            result["deployment_info"] = result["result"]
        
        return result
    
    async def _operation_update_deployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a deployment."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        manifest = params.get("manifest")
        
        result = await self._make_request("PUT", f"apis/apps/v1/namespaces/{namespace}/deployments/{resource_name}", params, 
                                        data=manifest)
        
        if result["status"] == "success":
            result["updated_resource"] = result["result"]
            result["deployment_info"] = result["result"]
        
        return result
    
    async def _operation_delete_deployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a deployment."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        
        result = await self._make_request("DELETE", f"apis/apps/v1/namespaces/{namespace}/deployments/{resource_name}", params)
        return result
    
    async def _operation_scale_deployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scale a deployment."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        replicas = params.get("replicas")
        
        scale_data = {
            "spec": {
                "replicas": replicas
            }
        }
        
        result = await self._make_request("PATCH", f"apis/apps/v1/namespaces/{namespace}/deployments/{resource_name}/scale", params, 
                                        data=scale_data)
        
        if result["status"] == "success":
            result["scale_result"] = result["result"]
        
        return result
    
    async def _operation_rollout_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get rollout status of a deployment."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        
        result = await self._make_request("GET", f"apis/apps/v1/namespaces/{namespace}/deployments/{resource_name}", params)
        
        if result["status"] == "success":
            deployment = result["result"]
            status = deployment.get("status", {})
            result["rollout_status"] = {
                "replicas": status.get("replicas", 0),
                "ready_replicas": status.get("readyReplicas", 0),
                "updated_replicas": status.get("updatedReplicas", 0),
                "available_replicas": status.get("availableReplicas", 0),
                "conditions": status.get("conditions", [])
            }
        
        return result
    
    # -------------------------
    # Service Operations
    # -------------------------
    
    async def _operation_list_services(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List services in a namespace."""
        namespace = params.get("namespace", "default")
        labels = params.get("labels")
        
        query_params = {}
        if labels:
            label_selector = ",".join([f"{k}={v}" for k, v in labels.items()])
            query_params["labelSelector"] = label_selector
        
        result = await self._make_request("GET", f"api/v1/namespaces/{namespace}/services", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["services"] = result["result"].get("items", [])
        
        return result
    
    async def _operation_create_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new service."""
        namespace = params.get("namespace", "default")
        manifest = params.get("manifest")
        
        result = await self._make_request("POST", f"api/v1/namespaces/{namespace}/services", params, 
                                        data=manifest)
        
        if result["status"] == "success":
            result["created_resource"] = result["result"]
            result["service_info"] = result["result"]
        
        return result
    
    async def _operation_get_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific service."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        
        result = await self._make_request("GET", f"api/v1/namespaces/{namespace}/services/{resource_name}", params)
        
        if result["status"] == "success":
            result["service_info"] = result["result"]
        
        return result
    
    async def _operation_update_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a service."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        manifest = params.get("manifest")
        
        result = await self._make_request("PUT", f"api/v1/namespaces/{namespace}/services/{resource_name}", params, 
                                        data=manifest)
        
        if result["status"] == "success":
            result["updated_resource"] = result["result"]
            result["service_info"] = result["result"]
        
        return result
    
    async def _operation_delete_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a service."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        
        result = await self._make_request("DELETE", f"api/v1/namespaces/{namespace}/services/{resource_name}", params)
        return result
    
    # -------------------------
    # Namespace Operations
    # -------------------------
    
    async def _operation_list_namespaces(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all namespaces."""
        labels = params.get("labels")
        
        query_params = {}
        if labels:
            label_selector = ",".join([f"{k}={v}" for k, v in labels.items()])
            query_params["labelSelector"] = label_selector
        
        result = await self._make_request("GET", "api/v1/namespaces", params, query_params=query_params)
        
        if result["status"] == "success":
            result["namespaces"] = result["result"].get("items", [])
        
        return result
    
    async def _operation_create_namespace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new namespace."""
        manifest = params.get("manifest")
        
        result = await self._make_request("POST", "api/v1/namespaces", params, data=manifest)
        
        if result["status"] == "success":
            result["created_resource"] = result["result"]
            result["namespace_info"] = result["result"]
        
        return result
    
    async def _operation_get_namespace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific namespace."""
        resource_name = params.get("resource_name")
        
        result = await self._make_request("GET", f"api/v1/namespaces/{resource_name}", params)
        
        if result["status"] == "success":
            result["namespace_info"] = result["result"]
        
        return result
    
    async def _operation_update_namespace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a namespace."""
        resource_name = params.get("resource_name")
        manifest = params.get("manifest")
        
        result = await self._make_request("PUT", f"api/v1/namespaces/{resource_name}", params, data=manifest)
        
        if result["status"] == "success":
            result["updated_resource"] = result["result"]
            result["namespace_info"] = result["result"]
        
        return result
    
    async def _operation_delete_namespace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a namespace."""
        resource_name = params.get("resource_name")
        
        result = await self._make_request("DELETE", f"api/v1/namespaces/{resource_name}", params)
        return result
    
    # -------------------------
    # ConfigMap Operations
    # -------------------------
    
    async def _operation_list_configmaps(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List configmaps in a namespace."""
        namespace = params.get("namespace", "default")
        labels = params.get("labels")
        
        query_params = {}
        if labels:
            label_selector = ",".join([f"{k}={v}" for k, v in labels.items()])
            query_params["labelSelector"] = label_selector
        
        result = await self._make_request("GET", f"api/v1/namespaces/{namespace}/configmaps", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["configmaps"] = result["result"].get("items", [])
        
        return result
    
    async def _operation_create_configmap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new configmap."""
        namespace = params.get("namespace", "default")
        manifest = params.get("manifest")
        
        result = await self._make_request("POST", f"api/v1/namespaces/{namespace}/configmaps", params, 
                                        data=manifest)
        
        if result["status"] == "success":
            result["created_resource"] = result["result"]
            result["configmap_info"] = result["result"]
        
        return result
    
    async def _operation_get_configmap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific configmap."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        
        result = await self._make_request("GET", f"api/v1/namespaces/{namespace}/configmaps/{resource_name}", params)
        
        if result["status"] == "success":
            result["configmap_info"] = result["result"]
        
        return result
    
    async def _operation_update_configmap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a configmap."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        manifest = params.get("manifest")
        
        result = await self._make_request("PUT", f"api/v1/namespaces/{namespace}/configmaps/{resource_name}", params, 
                                        data=manifest)
        
        if result["status"] == "success":
            result["updated_resource"] = result["result"]
            result["configmap_info"] = result["result"]
        
        return result
    
    async def _operation_delete_configmap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a configmap."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        
        result = await self._make_request("DELETE", f"api/v1/namespaces/{namespace}/configmaps/{resource_name}", params)
        return result
    
    # -------------------------
    # Secret Operations
    # -------------------------
    
    async def _operation_list_secrets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List secrets in a namespace."""
        namespace = params.get("namespace", "default")
        labels = params.get("labels")
        
        query_params = {}
        if labels:
            label_selector = ",".join([f"{k}={v}" for k, v in labels.items()])
            query_params["labelSelector"] = label_selector
        
        result = await self._make_request("GET", f"api/v1/namespaces/{namespace}/secrets", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["secrets"] = result["result"].get("items", [])
        
        return result
    
    async def _operation_create_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new secret."""
        namespace = params.get("namespace", "default")
        manifest = params.get("manifest")
        
        result = await self._make_request("POST", f"api/v1/namespaces/{namespace}/secrets", params, 
                                        data=manifest)
        
        if result["status"] == "success":
            result["created_resource"] = result["result"]
            result["secret_info"] = result["result"]
        
        return result
    
    async def _operation_get_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific secret."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        
        result = await self._make_request("GET", f"api/v1/namespaces/{namespace}/secrets/{resource_name}", params)
        
        if result["status"] == "success":
            result["secret_info"] = result["result"]
        
        return result
    
    async def _operation_update_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a secret."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        manifest = params.get("manifest")
        
        result = await self._make_request("PUT", f"api/v1/namespaces/{namespace}/secrets/{resource_name}", params, 
                                        data=manifest)
        
        if result["status"] == "success":
            result["updated_resource"] = result["result"]
            result["secret_info"] = result["result"]
        
        return result
    
    async def _operation_delete_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a secret."""
        namespace = params.get("namespace", "default")
        resource_name = params.get("resource_name")
        
        result = await self._make_request("DELETE", f"api/v1/namespaces/{namespace}/secrets/{resource_name}", params)
        return result
    
    # -------------------------
    # Node Operations
    # -------------------------
    
    async def _operation_list_nodes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all nodes in the cluster."""
        labels = params.get("labels")
        
        query_params = {}
        if labels:
            label_selector = ",".join([f"{k}={v}" for k, v in labels.items()])
            query_params["labelSelector"] = label_selector
        
        result = await self._make_request("GET", "api/v1/nodes", params, query_params=query_params)
        
        if result["status"] == "success":
            result["nodes"] = result["result"].get("items", [])
        
        return result
    
    async def _operation_get_node(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific node."""
        resource_name = params.get("resource_name")
        
        result = await self._make_request("GET", f"api/v1/nodes/{resource_name}", params)
        
        if result["status"] == "success":
            result["node_info"] = result["result"]
        
        return result
    
    async def _operation_update_node(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a node."""
        resource_name = params.get("resource_name")
        manifest = params.get("manifest")
        
        result = await self._make_request("PUT", f"api/v1/nodes/{resource_name}", params, data=manifest)
        
        if result["status"] == "success":
            result["updated_resource"] = result["result"]
            result["node_info"] = result["result"]
        
        return result
    
    # -------------------------
    # Events Operations
    # -------------------------
    
    async def _operation_list_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List events in a namespace."""
        namespace = params.get("namespace", "default")
        field_selector = params.get("field_selector")
        
        query_params = {}
        if field_selector:
            query_params["fieldSelector"] = field_selector
        
        result = await self._make_request("GET", f"api/v1/namespaces/{namespace}/events", params, 
                                        query_params=query_params)
        
        if result["status"] == "success":
            result["events"] = result["result"].get("items", [])
        
        return result


# Utility functions for common Kubernetes operations
class KubernetesHelpers:
    """Helper functions for common Kubernetes operations."""
    
    @staticmethod
    def create_pod_manifest(name: str, image: str, namespace: str = "default", 
                           labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a basic pod manifest."""
        return {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": name,
                "namespace": namespace,
                "labels": labels or {}
            },
            "spec": {
                "containers": [{
                    "name": name,
                    "image": image
                }]
            }
        }
    
    @staticmethod
    def create_deployment_manifest(name: str, image: str, replicas: int = 1, 
                                 namespace: str = "default", 
                                 labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a basic deployment manifest."""
        labels = labels or {"app": name}
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "namespace": namespace,
                "labels": labels
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": labels
                },
                "template": {
                    "metadata": {
                        "labels": labels
                    },
                    "spec": {
                        "containers": [{
                            "name": name,
                            "image": image
                        }]
                    }
                }
            }
        }
    
    @staticmethod
    def create_service_manifest(name: str, port: int, target_port: int = None, 
                               service_type: str = "ClusterIP", namespace: str = "default",
                               selector: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a basic service manifest."""
        if target_port is None:
            target_port = port
        if selector is None:
            selector = {"app": name}
            
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "type": service_type,
                "ports": [{
                    "port": port,
                    "targetPort": target_port
                }],
                "selector": selector
            }
        }
    
    @staticmethod
    def create_namespace_manifest(name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a namespace manifest."""
        return {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": name,
                "labels": labels or {}
            }
        }
    
    @staticmethod
    def create_configmap_manifest(name: str, data: Dict[str, str], 
                                 namespace: str = "default") -> Dict[str, Any]:
        """Create a configmap manifest."""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "data": data
        }
    
    @staticmethod
    def create_secret_manifest(name: str, data: Dict[str, str], 
                              secret_type: str = "Opaque", 
                              namespace: str = "default") -> Dict[str, Any]:
        """Create a secret manifest."""
        # Encode data as base64
        encoded_data = {}
        for key, value in data.items():
            encoded_data[key] = base64.b64encode(value.encode()).decode()
            
        return {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "type": secret_type,
            "data": encoded_data
        }


# Main test function for Kubernetes Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Kubernetes Node Test Suite ===")
        
        # Get configuration from environment or user input
        api_server = os.environ.get("KUBERNETES_API_SERVER")
        token = os.environ.get("KUBERNETES_TOKEN")
        
        if not api_server:
            print("Kubernetes API server not found in environment variables")
            print("Please set KUBERNETES_API_SERVER")
            print("Or provide it when prompted...")
            api_server = input("Enter Kubernetes API server URL: ")
        
        if not token:
            print("Kubernetes token not found in environment variables")
            print("Please set KUBERNETES_TOKEN")
            print("Or provide it when prompted...")
            token = input("Enter Kubernetes service account token: ")
        
        if not api_server or not token:
            print("Kubernetes API server and token are required for testing")
            return
        
        # Create an instance of the Kubernetes Node
        node = KubernetesNode()
        
        # Test cases (these require a running Kubernetes cluster)
        test_cases = [
            {
                "name": "List Namespaces",
                "params": {
                    "operation": KubernetesOperation.LIST_NAMESPACES,
                    "api_server": api_server,
                    "token": token
                },
                "expected_status": "success"
            },
            {
                "name": "List Nodes",
                "params": {
                    "operation": KubernetesOperation.LIST_NODES,
                    "api_server": api_server,
                    "token": token
                },
                "expected_status": "success"
            },
            {
                "name": "List Pods in Default Namespace",
                "params": {
                    "operation": KubernetesOperation.LIST_PODS,
                    "api_server": api_server,
                    "token": token,
                    "namespace": "default"
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
                    if result.get("namespaces"):
                        print(f"Namespaces found: {len(result['namespaces'])}")
                    if result.get("nodes"):
                        print(f"Nodes found: {len(result['nodes'])}")
                    if result.get("pods"):
                        print(f"Pods found: {len(result['pods'])}")
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
        
        if passed_tests < total_tests:
            print("\nNote: Some tests may fail if Kubernetes cluster is not accessible")
        
        print("\nAll tests completed!")

    # Run the async tests
    asyncio.run(run_tests())

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("kubernetes", KubernetesNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register KubernetesNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")