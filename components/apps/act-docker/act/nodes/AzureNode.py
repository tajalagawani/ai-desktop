"""
Azure Node - Comprehensive integration with Microsoft Azure REST APIs
Provides access to all major Azure services including compute, storage, databases, and management operations.
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

class AzureOperation:
    """Operations available on Microsoft Azure REST APIs."""
    
    # Authentication Operations
    GET_ACCESS_TOKEN = "get_access_token"
    
    # Virtual Machines Operations
    LIST_VMS = "list_vms"
    GET_VM = "get_vm"
    CREATE_VM = "create_vm"
    UPDATE_VM = "update_vm"
    DELETE_VM = "delete_vm"
    START_VM = "start_vm"
    STOP_VM = "stop_vm"
    RESTART_VM = "restart_vm"
    DEALLOCATE_VM = "deallocate_vm"
    RESIZE_VM = "resize_vm"
    CAPTURE_VM = "capture_vm"
    
    # Storage Account Operations
    LIST_STORAGE_ACCOUNTS = "list_storage_accounts"
    GET_STORAGE_ACCOUNT = "get_storage_account"
    CREATE_STORAGE_ACCOUNT = "create_storage_account"
    UPDATE_STORAGE_ACCOUNT = "update_storage_account"
    DELETE_STORAGE_ACCOUNT = "delete_storage_account"
    LIST_STORAGE_KEYS = "list_storage_keys"
    REGENERATE_STORAGE_KEY = "regenerate_storage_key"
    
    # Blob Storage Operations
    LIST_BLOB_CONTAINERS = "list_blob_containers"
    CREATE_BLOB_CONTAINER = "create_blob_container"
    DELETE_BLOB_CONTAINER = "delete_blob_container"
    LIST_BLOBS = "list_blobs"
    GET_BLOB = "get_blob"
    PUT_BLOB = "put_blob"
    DELETE_BLOB = "delete_blob"
    COPY_BLOB = "copy_blob"
    GET_BLOB_PROPERTIES = "get_blob_properties"
    SET_BLOB_METADATA = "set_blob_metadata"
    
    # Queue Storage Operations
    LIST_QUEUES = "list_queues"
    CREATE_QUEUE = "create_queue"
    DELETE_QUEUE = "delete_queue"
    PUT_MESSAGE = "put_message"
    GET_MESSAGES = "get_messages"
    DELETE_MESSAGE = "delete_message"
    PEEK_MESSAGES = "peek_messages"
    
    # Table Storage Operations
    LIST_TABLES = "list_tables"
    CREATE_TABLE = "create_table"
    DELETE_TABLE = "delete_table"
    INSERT_ENTITY = "insert_entity"
    UPDATE_ENTITY = "update_entity"
    DELETE_ENTITY = "delete_entity"
    QUERY_ENTITIES = "query_entities"
    
    # File Storage Operations
    LIST_FILE_SHARES = "list_file_shares"
    CREATE_FILE_SHARE = "create_file_share"
    DELETE_FILE_SHARE = "delete_file_share"
    LIST_FILES = "list_files"
    GET_FILE = "get_file"
    PUT_FILE = "put_file"
    DELETE_FILE = "delete_file"
    
    # Resource Group Operations
    LIST_RESOURCE_GROUPS = "list_resource_groups"
    GET_RESOURCE_GROUP = "get_resource_group"
    CREATE_RESOURCE_GROUP = "create_resource_group"
    UPDATE_RESOURCE_GROUP = "update_resource_group"
    DELETE_RESOURCE_GROUP = "delete_resource_group"
    
    # Resource Management Operations
    LIST_RESOURCES = "list_resources"
    GET_RESOURCE = "get_resource"
    CREATE_RESOURCE = "create_resource"
    UPDATE_RESOURCE = "update_resource"
    DELETE_RESOURCE = "delete_resource"
    
    # ARM Template Operations
    DEPLOY_TEMPLATE = "deploy_template"
    VALIDATE_TEMPLATE = "validate_template"
    LIST_DEPLOYMENTS = "list_deployments"
    GET_DEPLOYMENT = "get_deployment"
    DELETE_DEPLOYMENT = "delete_deployment"
    
    # Subscription Operations
    LIST_SUBSCRIPTIONS = "list_subscriptions"
    GET_SUBSCRIPTION = "get_subscription"
    
    # Microsoft Graph - User Operations
    GET_USERS = "get_users"
    GET_USER = "get_user"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Microsoft Graph - Group Operations
    GET_GROUPS = "get_groups"
    GET_GROUP = "get_group"
    CREATE_GROUP = "create_group"
    UPDATE_GROUP = "update_group"
    DELETE_GROUP = "delete_group"
    ADD_GROUP_MEMBER = "add_group_member"
    REMOVE_GROUP_MEMBER = "remove_group_member"
    
    # Microsoft Graph - Application Operations
    GET_APPLICATIONS = "get_applications"
    GET_APPLICATION = "get_application"
    CREATE_APPLICATION = "create_application"
    UPDATE_APPLICATION = "update_application"
    DELETE_APPLICATION = "delete_application"
    
    # Key Vault Operations
    LIST_KEY_VAULTS = "list_key_vaults"
    GET_KEY_VAULT = "get_key_vault"
    CREATE_KEY_VAULT = "create_key_vault"
    DELETE_KEY_VAULT = "delete_key_vault"
    LIST_SECRETS = "list_secrets"
    GET_SECRET = "get_secret"
    SET_SECRET = "set_secret"
    DELETE_SECRET = "delete_secret"
    LIST_KEYS = "list_keys"
    GET_KEY = "get_key"
    CREATE_KEY = "create_key"
    DELETE_KEY = "delete_key"
    
    # SQL Database Operations
    LIST_SQL_SERVERS = "list_sql_servers"
    GET_SQL_SERVER = "get_sql_server"
    CREATE_SQL_SERVER = "create_sql_server"
    DELETE_SQL_SERVER = "delete_sql_server"
    LIST_SQL_DATABASES = "list_sql_databases"
    GET_SQL_DATABASE = "get_sql_database"
    CREATE_SQL_DATABASE = "create_sql_database"
    DELETE_SQL_DATABASE = "delete_sql_database"
    
    # App Service Operations
    LIST_WEB_APPS = "list_web_apps"
    GET_WEB_APP = "get_web_app"
    CREATE_WEB_APP = "create_web_app"
    DELETE_WEB_APP = "delete_web_app"
    START_WEB_APP = "start_web_app"
    STOP_WEB_APP = "stop_web_app"
    RESTART_WEB_APP = "restart_web_app"
    
    # Network Operations
    LIST_VIRTUAL_NETWORKS = "list_virtual_networks"
    GET_VIRTUAL_NETWORK = "get_virtual_network"
    CREATE_VIRTUAL_NETWORK = "create_virtual_network"
    DELETE_VIRTUAL_NETWORK = "delete_virtual_network"
    LIST_NETWORK_SECURITY_GROUPS = "list_network_security_groups"
    GET_NETWORK_SECURITY_GROUP = "get_network_security_group"
    CREATE_NETWORK_SECURITY_GROUP = "create_network_security_group"
    DELETE_NETWORK_SECURITY_GROUP = "delete_network_security_group"

class AzureNode(BaseNode):
    """
    Node for interacting with Microsoft Azure REST APIs.
    Provides comprehensive functionality for Azure compute, storage, management, and Microsoft Graph operations.
    """
    
    MANAGEMENT_BASE_URL = "https://management.azure.com"
    GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
    LOGIN_BASE_URL = "https://login.microsoftonline.com"
    STORAGE_BASE_URL = "https://{account}.blob.core.windows.net"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Azure node."""
        return NodeSchema(
            node_type="azure",
            version="1.0.0",
            description="Comprehensive integration with Microsoft Azure REST APIs for compute, storage, management, and Microsoft Graph operations",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Azure API",
                    required=True,
                    enum=[
                        AzureOperation.GET_ACCESS_TOKEN,
                        AzureOperation.LIST_VMS,
                        AzureOperation.GET_VM,
                        AzureOperation.CREATE_VM,
                        AzureOperation.UPDATE_VM,
                        AzureOperation.DELETE_VM,
                        AzureOperation.START_VM,
                        AzureOperation.STOP_VM,
                        AzureOperation.RESTART_VM,
                        AzureOperation.DEALLOCATE_VM,
                        AzureOperation.RESIZE_VM,
                        AzureOperation.CAPTURE_VM,
                        AzureOperation.LIST_STORAGE_ACCOUNTS,
                        AzureOperation.GET_STORAGE_ACCOUNT,
                        AzureOperation.CREATE_STORAGE_ACCOUNT,
                        AzureOperation.UPDATE_STORAGE_ACCOUNT,
                        AzureOperation.DELETE_STORAGE_ACCOUNT,
                        AzureOperation.LIST_STORAGE_KEYS,
                        AzureOperation.REGENERATE_STORAGE_KEY,
                        AzureOperation.LIST_BLOB_CONTAINERS,
                        AzureOperation.CREATE_BLOB_CONTAINER,
                        AzureOperation.DELETE_BLOB_CONTAINER,
                        AzureOperation.LIST_BLOBS,
                        AzureOperation.GET_BLOB,
                        AzureOperation.PUT_BLOB,
                        AzureOperation.DELETE_BLOB,
                        AzureOperation.COPY_BLOB,
                        AzureOperation.GET_BLOB_PROPERTIES,
                        AzureOperation.SET_BLOB_METADATA,
                        AzureOperation.LIST_QUEUES,
                        AzureOperation.CREATE_QUEUE,
                        AzureOperation.DELETE_QUEUE,
                        AzureOperation.PUT_MESSAGE,
                        AzureOperation.GET_MESSAGES,
                        AzureOperation.DELETE_MESSAGE,
                        AzureOperation.PEEK_MESSAGES,
                        AzureOperation.LIST_TABLES,
                        AzureOperation.CREATE_TABLE,
                        AzureOperation.DELETE_TABLE,
                        AzureOperation.INSERT_ENTITY,
                        AzureOperation.UPDATE_ENTITY,
                        AzureOperation.DELETE_ENTITY,
                        AzureOperation.QUERY_ENTITIES,
                        AzureOperation.LIST_FILE_SHARES,
                        AzureOperation.CREATE_FILE_SHARE,
                        AzureOperation.DELETE_FILE_SHARE,
                        AzureOperation.LIST_FILES,
                        AzureOperation.GET_FILE,
                        AzureOperation.PUT_FILE,
                        AzureOperation.DELETE_FILE,
                        AzureOperation.LIST_RESOURCE_GROUPS,
                        AzureOperation.GET_RESOURCE_GROUP,
                        AzureOperation.CREATE_RESOURCE_GROUP,
                        AzureOperation.UPDATE_RESOURCE_GROUP,
                        AzureOperation.DELETE_RESOURCE_GROUP,
                        AzureOperation.LIST_RESOURCES,
                        AzureOperation.GET_RESOURCE,
                        AzureOperation.CREATE_RESOURCE,
                        AzureOperation.UPDATE_RESOURCE,
                        AzureOperation.DELETE_RESOURCE,
                        AzureOperation.DEPLOY_TEMPLATE,
                        AzureOperation.VALIDATE_TEMPLATE,
                        AzureOperation.LIST_DEPLOYMENTS,
                        AzureOperation.GET_DEPLOYMENT,
                        AzureOperation.DELETE_DEPLOYMENT,
                        AzureOperation.LIST_SUBSCRIPTIONS,
                        AzureOperation.GET_SUBSCRIPTION,
                        AzureOperation.GET_USERS,
                        AzureOperation.GET_USER,
                        AzureOperation.CREATE_USER,
                        AzureOperation.UPDATE_USER,
                        AzureOperation.DELETE_USER,
                        AzureOperation.GET_GROUPS,
                        AzureOperation.GET_GROUP,
                        AzureOperation.CREATE_GROUP,
                        AzureOperation.UPDATE_GROUP,
                        AzureOperation.DELETE_GROUP,
                        AzureOperation.ADD_GROUP_MEMBER,
                        AzureOperation.REMOVE_GROUP_MEMBER,
                        AzureOperation.GET_APPLICATIONS,
                        AzureOperation.GET_APPLICATION,
                        AzureOperation.CREATE_APPLICATION,
                        AzureOperation.UPDATE_APPLICATION,
                        AzureOperation.DELETE_APPLICATION,
                        AzureOperation.LIST_KEY_VAULTS,
                        AzureOperation.GET_KEY_VAULT,
                        AzureOperation.CREATE_KEY_VAULT,
                        AzureOperation.DELETE_KEY_VAULT,
                        AzureOperation.LIST_SECRETS,
                        AzureOperation.GET_SECRET,
                        AzureOperation.SET_SECRET,
                        AzureOperation.DELETE_SECRET,
                        AzureOperation.LIST_KEYS,
                        AzureOperation.GET_KEY,
                        AzureOperation.CREATE_KEY,
                        AzureOperation.DELETE_KEY,
                        AzureOperation.LIST_SQL_SERVERS,
                        AzureOperation.GET_SQL_SERVER,
                        AzureOperation.CREATE_SQL_SERVER,
                        AzureOperation.DELETE_SQL_SERVER,
                        AzureOperation.LIST_SQL_DATABASES,
                        AzureOperation.GET_SQL_DATABASE,
                        AzureOperation.CREATE_SQL_DATABASE,
                        AzureOperation.DELETE_SQL_DATABASE,
                        AzureOperation.LIST_WEB_APPS,
                        AzureOperation.GET_WEB_APP,
                        AzureOperation.CREATE_WEB_APP,
                        AzureOperation.DELETE_WEB_APP,
                        AzureOperation.START_WEB_APP,
                        AzureOperation.STOP_WEB_APP,
                        AzureOperation.RESTART_WEB_APP,
                        AzureOperation.LIST_VIRTUAL_NETWORKS,
                        AzureOperation.GET_VIRTUAL_NETWORK,
                        AzureOperation.CREATE_VIRTUAL_NETWORK,
                        AzureOperation.DELETE_VIRTUAL_NETWORK,
                        AzureOperation.LIST_NETWORK_SECURITY_GROUPS,
                        AzureOperation.GET_NETWORK_SECURITY_GROUP,
                        AzureOperation.CREATE_NETWORK_SECURITY_GROUP,
                        AzureOperation.DELETE_NETWORK_SECURITY_GROUP
                    ]
                ),
                NodeParameter(
                    name="tenant_id",
                    type=NodeParameterType.SECRET,
                    description="Azure Active Directory tenant ID",
                    required=False
                ),
                NodeParameter(
                    name="client_id",
                    type=NodeParameterType.SECRET,
                    description="Azure application client ID",
                    required=False
                ),
                NodeParameter(
                    name="client_secret",
                    type=NodeParameterType.SECRET,
                    description="Azure application client secret",
                    required=False
                ),
                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.SECRET,
                    description="Azure access token for authentication",
                    required=False
                ),
                NodeParameter(
                    name="subscription_id",
                    type=NodeParameterType.STRING,
                    description="Azure subscription ID",
                    required=False
                ),
                NodeParameter(
                    name="resource_group_name",
                    type=NodeParameterType.STRING,
                    description="Azure resource group name",
                    required=False
                ),
                NodeParameter(
                    name="resource_name",
                    type=NodeParameterType.STRING,
                    description="Name of the Azure resource",
                    required=False
                ),
                NodeParameter(
                    name="location",
                    type=NodeParameterType.STRING,
                    description="Azure region/location",
                    required=False
                ),
                NodeParameter(
                    name="storage_account_name",
                    type=NodeParameterType.STRING,
                    description="Azure storage account name",
                    required=False
                ),
                NodeParameter(
                    name="container_name",
                    type=NodeParameterType.STRING,
                    description="Blob container name",
                    required=False
                ),
                NodeParameter(
                    name="blob_name",
                    type=NodeParameterType.STRING,
                    description="Blob name",
                    required=False
                ),
                NodeParameter(
                    name="file_content",
                    type=NodeParameterType.STRING,
                    description="Content for file upload operations",
                    required=False
                ),
                NodeParameter(
                    name="vm_name",
                    type=NodeParameterType.STRING,
                    description="Virtual machine name",
                    required=False
                ),
                NodeParameter(
                    name="vm_size",
                    type=NodeParameterType.STRING,
                    description="Virtual machine size",
                    required=False
                ),
                NodeParameter(
                    name="user_id",
                    type=NodeParameterType.STRING,
                    description="User ID for Microsoft Graph operations",
                    required=False
                ),
                NodeParameter(
                    name="group_id",
                    type=NodeParameterType.STRING,
                    description="Group ID for Microsoft Graph operations",
                    required=False
                ),
                NodeParameter(
                    name="application_id",
                    type=NodeParameterType.STRING,
                    description="Application ID for Microsoft Graph operations",
                    required=False
                ),
                NodeParameter(
                    name="key_vault_name",
                    type=NodeParameterType.STRING,
                    description="Key Vault name",
                    required=False
                ),
                NodeParameter(
                    name="secret_name",
                    type=NodeParameterType.STRING,
                    description="Secret name for Key Vault operations",
                    required=False
                ),
                NodeParameter(
                    name="key_name",
                    type=NodeParameterType.STRING,
                    description="Key name for Key Vault operations",
                    required=False
                ),
                NodeParameter(
                    name="template_content",
                    type=NodeParameterType.OBJECT,
                    description="ARM template content for deployment",
                    required=False
                ),
                NodeParameter(
                    name="parameters",
                    type=NodeParameterType.OBJECT,
                    description="Additional parameters for Azure operations",
                    required=False
                ),
                NodeParameter(
                    name="properties",
                    type=NodeParameterType.OBJECT,
                    description="Resource properties for create/update operations",
                    required=False
                ),
                NodeParameter(
                    name="tags",
                    type=NodeParameterType.OBJECT,
                    description="Resource tags",
                    required=False
                ),
                NodeParameter(
                    name="scope",
                    type=NodeParameterType.STRING,
                    description="Scope for Microsoft Graph operations",
                    required=False,
                    default="https://graph.microsoft.com/.default"
                ),
                NodeParameter(
                    name="api_version",
                    type=NodeParameterType.STRING,
                    description="Azure API version",
                    required=False,
                    default="2023-09-01"
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
                "resources": NodeParameterType.ARRAY,
                "resource": NodeParameterType.OBJECT,
                "vms": NodeParameterType.ARRAY,
                "vm": NodeParameterType.OBJECT,
                "storage_accounts": NodeParameterType.ARRAY,
                "storage_account": NodeParameterType.OBJECT,
                "containers": NodeParameterType.ARRAY,
                "blobs": NodeParameterType.ARRAY,
                "blob_data": NodeParameterType.STRING,
                "users": NodeParameterType.ARRAY,
                "user": NodeParameterType.OBJECT,
                "groups": NodeParameterType.ARRAY,
                "group": NodeParameterType.OBJECT,
                "applications": NodeParameterType.ARRAY,
                "application": NodeParameterType.OBJECT,
                "secrets": NodeParameterType.ARRAY,
                "secret": NodeParameterType.STRING,
                "keys": NodeParameterType.ARRAY,
                "key": NodeParameterType.OBJECT,
                "deployments": NodeParameterType.ARRAY,
                "deployment": NodeParameterType.OBJECT,
                "subscriptions": NodeParameterType.ARRAY,
                "subscription": NodeParameterType.OBJECT,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["azure", "microsoft", "cloud", "api", "integration", "management"],
            author="System",
            documentation_url="https://docs.microsoft.com/en-us/rest/api/azure/"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for authentication
        has_access_token = params.get("access_token")
        has_service_principal = all([
            params.get("tenant_id"),
            params.get("client_id"),
            params.get("client_secret")
        ])
        
        if not has_access_token and not has_service_principal and operation != AzureOperation.GET_ACCESS_TOKEN:
            raise NodeValidationError("Either access_token or service principal credentials (tenant_id, client_id, client_secret) are required")
            
        # Validate based on operation
        if operation in [AzureOperation.LIST_VMS, AzureOperation.CREATE_VM, AzureOperation.GET_VM, 
                        AzureOperation.UPDATE_VM, AzureOperation.DELETE_VM, AzureOperation.START_VM,
                        AzureOperation.STOP_VM, AzureOperation.RESTART_VM, AzureOperation.DEALLOCATE_VM]:
            if not params.get("subscription_id"):
                raise NodeValidationError("Subscription ID is required for VM operations")
            if not params.get("resource_group_name"):
                raise NodeValidationError("Resource group name is required for VM operations")
                
        elif operation in [AzureOperation.LIST_STORAGE_ACCOUNTS, AzureOperation.GET_STORAGE_ACCOUNT,
                          AzureOperation.CREATE_STORAGE_ACCOUNT, AzureOperation.UPDATE_STORAGE_ACCOUNT,
                          AzureOperation.DELETE_STORAGE_ACCOUNT]:
            if not params.get("subscription_id"):
                raise NodeValidationError("Subscription ID is required for storage operations")
                
        elif operation in [AzureOperation.LIST_BLOB_CONTAINERS, AzureOperation.CREATE_BLOB_CONTAINER,
                          AzureOperation.DELETE_BLOB_CONTAINER, AzureOperation.LIST_BLOBS]:
            if not params.get("storage_account_name"):
                raise NodeValidationError("Storage account name is required for blob operations")
                
        elif operation in [AzureOperation.GET_BLOB, AzureOperation.PUT_BLOB, AzureOperation.DELETE_BLOB]:
            if not params.get("storage_account_name"):
                raise NodeValidationError("Storage account name is required for blob operations")
            if not params.get("container_name"):
                raise NodeValidationError("Container name is required for blob operations")
            if not params.get("blob_name"):
                raise NodeValidationError("Blob name is required for blob operations")
                
        elif operation in [AzureOperation.GET_USER, AzureOperation.UPDATE_USER, AzureOperation.DELETE_USER]:
            if not params.get("user_id"):
                raise NodeValidationError("User ID is required for user operations")
                
        elif operation in [AzureOperation.GET_GROUP, AzureOperation.UPDATE_GROUP, AzureOperation.DELETE_GROUP,
                          AzureOperation.ADD_GROUP_MEMBER, AzureOperation.REMOVE_GROUP_MEMBER]:
            if not params.get("group_id"):
                raise NodeValidationError("Group ID is required for group operations")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Azure node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Execute the appropriate operation
            if operation == AzureOperation.GET_ACCESS_TOKEN:
                return await self._operation_get_access_token(validated_data)
                
            # Virtual Machine Operations
            elif operation == AzureOperation.LIST_VMS:
                return await self._operation_list_vms(validated_data)
            elif operation == AzureOperation.GET_VM:
                return await self._operation_get_vm(validated_data)
            elif operation == AzureOperation.CREATE_VM:
                return await self._operation_create_vm(validated_data)
            elif operation == AzureOperation.START_VM:
                return await self._operation_start_vm(validated_data)
            elif operation == AzureOperation.STOP_VM:
                return await self._operation_stop_vm(validated_data)
            elif operation == AzureOperation.RESTART_VM:
                return await self._operation_restart_vm(validated_data)
                
            # Storage Operations
            elif operation == AzureOperation.LIST_STORAGE_ACCOUNTS:
                return await self._operation_list_storage_accounts(validated_data)
            elif operation == AzureOperation.GET_STORAGE_ACCOUNT:
                return await self._operation_get_storage_account(validated_data)
            elif operation == AzureOperation.CREATE_STORAGE_ACCOUNT:
                return await self._operation_create_storage_account(validated_data)
                
            # Blob Operations
            elif operation == AzureOperation.LIST_BLOB_CONTAINERS:
                return await self._operation_list_blob_containers(validated_data)
            elif operation == AzureOperation.CREATE_BLOB_CONTAINER:
                return await self._operation_create_blob_container(validated_data)
            elif operation == AzureOperation.LIST_BLOBS:
                return await self._operation_list_blobs(validated_data)
            elif operation == AzureOperation.GET_BLOB:
                return await self._operation_get_blob(validated_data)
            elif operation == AzureOperation.PUT_BLOB:
                return await self._operation_put_blob(validated_data)
                
            # Resource Group Operations
            elif operation == AzureOperation.LIST_RESOURCE_GROUPS:
                return await self._operation_list_resource_groups(validated_data)
            elif operation == AzureOperation.GET_RESOURCE_GROUP:
                return await self._operation_get_resource_group(validated_data)
            elif operation == AzureOperation.CREATE_RESOURCE_GROUP:
                return await self._operation_create_resource_group(validated_data)
                
            # Microsoft Graph Operations
            elif operation == AzureOperation.GET_USERS:
                return await self._operation_get_users(validated_data)
            elif operation == AzureOperation.GET_USER:
                return await self._operation_get_user(validated_data)
            elif operation == AzureOperation.CREATE_USER:
                return await self._operation_create_user(validated_data)
            elif operation == AzureOperation.GET_GROUPS:
                return await self._operation_get_groups(validated_data)
            elif operation == AzureOperation.GET_GROUP:
                return await self._operation_get_group(validated_data)
            elif operation == AzureOperation.CREATE_GROUP:
                return await self._operation_create_group(validated_data)
                
            # Add more operations as needed
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
            error_message = f"Error in Azure node: {str(e)}"
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
    
    async def _make_request(self, method: str, url: str, params: Dict[str, Any], 
                          data: Optional[Union[Dict[str, Any], str]] = None,
                          headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the Azure API."""
        
        request_headers = headers or {}
        
        # Add authorization header if access token is available
        if params.get("access_token"):
            request_headers["Authorization"] = f"Bearer {params.get('access_token')}"
        
        if not request_headers.get("Content-Type") and data:
            request_headers["Content-Type"] = "application/json"
        
        try:
            kwargs = {"headers": request_headers}
            if data:
                if isinstance(data, dict):
                    kwargs["json"] = data
                else:
                    kwargs["data"] = data
            
            async with self.session.request(method, url, **kwargs) as response:
                response_headers = dict(response.headers)
                
                # Handle different response content types
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Azure API error {response.status}: {response_data}"
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
    
    async def _operation_get_access_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get access token using client credentials flow."""
        tenant_id = params.get("tenant_id")
        client_id = params.get("client_id")
        client_secret = params.get("client_secret")
        scope = params.get("scope", "https://management.azure.com/.default")
        
        if not all([tenant_id, client_id, client_secret]):
            return {
                "status": "error",
                "error": "tenant_id, client_id, and client_secret are required for authentication",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        url = f"{self.LOGIN_BASE_URL}/{tenant_id}/oauth2/v2.0/token"
        
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        result = await self._make_request("POST", url, params, urlencode(data), headers)
        
        if result["status"] == "success" and result["result"]:
            token_data = result["result"]
            result["access_token"] = token_data.get("access_token")
            result["token_type"] = token_data.get("token_type")
            result["expires_in"] = token_data.get("expires_in")
        
        return result
    
    # -------------------------
    # Virtual Machine Operations
    # -------------------------
    
    async def _operation_list_vms(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List virtual machines in a subscription."""
        subscription_id = params.get("subscription_id")
        resource_group = params.get("resource_group_name")
        api_version = params.get("api_version", "2023-09-01")
        
        if resource_group:
            url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines"
        else:
            url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/providers/Microsoft.Compute/virtualMachines"
        
        url += f"?api-version={api_version}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            result["vms"] = result["result"].get("value", [])
        
        return result
    
    async def _operation_get_vm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific virtual machine."""
        subscription_id = params.get("subscription_id")
        resource_group = params.get("resource_group_name")
        vm_name = params.get("vm_name")
        api_version = params.get("api_version", "2023-09-01")
        
        url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}"
        url += f"?api-version={api_version}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success":
            result["vm"] = result["result"]
        
        return result
    
    async def _operation_create_vm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new virtual machine."""
        subscription_id = params.get("subscription_id")
        resource_group = params.get("resource_group_name")
        vm_name = params.get("vm_name")
        location = params.get("location", "East US")
        vm_size = params.get("vm_size", "Standard_B1s")
        api_version = params.get("api_version", "2023-09-01")
        
        # Basic VM configuration
        vm_config = params.get("properties", {
            "hardwareProfile": {
                "vmSize": vm_size
            },
            "storageProfile": {
                "imageReference": {
                    "publisher": "Canonical",
                    "offer": "0001-com-ubuntu-server-jammy",
                    "sku": "22_04-lts-gen2",
                    "version": "latest"
                }
            },
            "osProfile": {
                "computerName": vm_name,
                "adminUsername": "azureuser"
            },
            "networkProfile": {
                "networkInterfaces": []
            }
        })
        
        data = {
            "location": location,
            "properties": vm_config
        }
        
        if params.get("tags"):
            data["tags"] = params.get("tags")
        
        url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}"
        url += f"?api-version={api_version}"
        
        result = await self._make_request("PUT", url, params, data)
        
        if result["status"] == "success":
            result["vm"] = result["result"]
        
        return result
    
    async def _operation_start_vm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start a virtual machine."""
        subscription_id = params.get("subscription_id")
        resource_group = params.get("resource_group_name")
        vm_name = params.get("vm_name")
        api_version = params.get("api_version", "2023-09-01")
        
        url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}/start"
        url += f"?api-version={api_version}"
        
        return await self._make_request("POST", url, params)
    
    async def _operation_stop_vm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop a virtual machine."""
        subscription_id = params.get("subscription_id")
        resource_group = params.get("resource_group_name")
        vm_name = params.get("vm_name")
        api_version = params.get("api_version", "2023-09-01")
        
        url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}/powerOff"
        url += f"?api-version={api_version}"
        
        return await self._make_request("POST", url, params)
    
    async def _operation_restart_vm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Restart a virtual machine."""
        subscription_id = params.get("subscription_id")
        resource_group = params.get("resource_group_name")
        vm_name = params.get("vm_name")
        api_version = params.get("api_version", "2023-09-01")
        
        url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}/restart"
        url += f"?api-version={api_version}"
        
        return await self._make_request("POST", url, params)
    
    # -------------------------
    # Storage Account Operations
    # -------------------------
    
    async def _operation_list_storage_accounts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List storage accounts in a subscription."""
        subscription_id = params.get("subscription_id")
        api_version = params.get("api_version", "2023-01-01")
        
        url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/providers/Microsoft.Storage/storageAccounts"
        url += f"?api-version={api_version}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            result["storage_accounts"] = result["result"].get("value", [])
        
        return result
    
    async def _operation_get_storage_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific storage account."""
        subscription_id = params.get("subscription_id")
        resource_group = params.get("resource_group_name")
        storage_account_name = params.get("storage_account_name")
        api_version = params.get("api_version", "2023-01-01")
        
        url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}"
        url += f"?api-version={api_version}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success":
            result["storage_account"] = result["result"]
        
        return result
    
    async def _operation_create_storage_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new storage account."""
        subscription_id = params.get("subscription_id")
        resource_group = params.get("resource_group_name")
        storage_account_name = params.get("storage_account_name")
        location = params.get("location", "East US")
        api_version = params.get("api_version", "2023-01-01")
        
        storage_config = params.get("properties", {
            "sku": {
                "name": "Standard_LRS"
            },
            "kind": "StorageV2",
            "accessTier": "Hot"
        })
        
        data = {
            "location": location,
            "sku": storage_config.get("sku", {"name": "Standard_LRS"}),
            "kind": storage_config.get("kind", "StorageV2"),
            "properties": {
                "accessTier": storage_config.get("accessTier", "Hot")
            }
        }
        
        if params.get("tags"):
            data["tags"] = params.get("tags")
        
        url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}"
        url += f"?api-version={api_version}"
        
        result = await self._make_request("PUT", url, params, data)
        
        if result["status"] == "success":
            result["storage_account"] = result["result"]
        
        return result
    
    # -------------------------
    # Blob Storage Operations
    # -------------------------
    
    async def _operation_list_blob_containers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List blob containers in a storage account."""
        storage_account_name = params.get("storage_account_name")
        
        url = f"https://{storage_account_name}.blob.core.windows.net/?comp=list"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            # Parse XML response (simplified)
            result["containers"] = []
        
        return result
    
    async def _operation_create_blob_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new blob container."""
        storage_account_name = params.get("storage_account_name")
        container_name = params.get("container_name")
        
        url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}?restype=container"
        
        return await self._make_request("PUT", url, params)
    
    async def _operation_list_blobs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List blobs in a container."""
        storage_account_name = params.get("storage_account_name")
        container_name = params.get("container_name")
        
        url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}?restype=container&comp=list"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            # Parse XML response (simplified)
            result["blobs"] = []
        
        return result
    
    async def _operation_get_blob(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get blob content."""
        storage_account_name = params.get("storage_account_name")
        container_name = params.get("container_name")
        blob_name = params.get("blob_name")
        
        url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{blob_name}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success":
            result["blob_data"] = result["result"]
        
        return result
    
    async def _operation_put_blob(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Upload blob content."""
        storage_account_name = params.get("storage_account_name")
        container_name = params.get("container_name")
        blob_name = params.get("blob_name")
        file_content = params.get("file_content", "")
        
        url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{blob_name}"
        
        headers = {"x-ms-blob-type": "BlockBlob"}
        
        return await self._make_request("PUT", url, params, file_content, headers)
    
    # -------------------------
    # Resource Group Operations
    # -------------------------
    
    async def _operation_list_resource_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List resource groups in a subscription."""
        subscription_id = params.get("subscription_id")
        api_version = params.get("api_version", "2023-09-01")
        
        url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/resourcegroups"
        url += f"?api-version={api_version}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            result["resources"] = result["result"].get("value", [])
        
        return result
    
    async def _operation_get_resource_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific resource group."""
        subscription_id = params.get("subscription_id")
        resource_group = params.get("resource_group_name")
        api_version = params.get("api_version", "2023-09-01")
        
        url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/resourcegroups/{resource_group}"
        url += f"?api-version={api_version}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success":
            result["resource"] = result["result"]
        
        return result
    
    async def _operation_create_resource_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource group."""
        subscription_id = params.get("subscription_id")
        resource_group = params.get("resource_group_name")
        location = params.get("location", "East US")
        api_version = params.get("api_version", "2023-09-01")
        
        data = {
            "location": location
        }
        
        if params.get("tags"):
            data["tags"] = params.get("tags")
        
        url = f"{self.MANAGEMENT_BASE_URL}/subscriptions/{subscription_id}/resourcegroups/{resource_group}"
        url += f"?api-version={api_version}"
        
        result = await self._make_request("PUT", url, params, data)
        
        if result["status"] == "success":
            result["resource"] = result["result"]
        
        return result
    
    # -------------------------
    # Microsoft Graph Operations
    # -------------------------
    
    async def _operation_get_users(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all users from Azure AD."""
        url = f"{self.GRAPH_BASE_URL}/users"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            result["users"] = result["result"].get("value", [])
        
        return result
    
    async def _operation_get_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific user from Azure AD."""
        user_id = params.get("user_id")
        
        url = f"{self.GRAPH_BASE_URL}/users/{user_id}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success":
            result["user"] = result["result"]
        
        return result
    
    async def _operation_create_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user in Azure AD."""
        user_data = params.get("properties", {})
        
        url = f"{self.GRAPH_BASE_URL}/users"
        
        result = await self._make_request("POST", url, params, user_data)
        
        if result["status"] == "success":
            result["user"] = result["result"]
        
        return result
    
    async def _operation_get_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all groups from Azure AD."""
        url = f"{self.GRAPH_BASE_URL}/groups"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            result["groups"] = result["result"].get("value", [])
        
        return result
    
    async def _operation_get_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific group from Azure AD."""
        group_id = params.get("group_id")
        
        url = f"{self.GRAPH_BASE_URL}/groups/{group_id}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success":
            result["group"] = result["result"]
        
        return result
    
    async def _operation_create_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new group in Azure AD."""
        group_data = params.get("properties", {})
        
        url = f"{self.GRAPH_BASE_URL}/groups"
        
        result = await self._make_request("POST", url, params, group_data)
        
        if result["status"] == "success":
            result["group"] = result["result"]
        
        return result


# Utility functions for common Azure operations
class AzureHelpers:
    """Helper functions for common Azure operations."""
    
    @staticmethod
    def create_vm_configuration(vm_size: str = "Standard_B1s", 
                              publisher: str = "Canonical",
                              offer: str = "0001-com-ubuntu-server-jammy",
                              sku: str = "22_04-lts-gen2",
                              admin_username: str = "azureuser") -> Dict[str, Any]:
        """Create a basic VM configuration."""
        return {
            "hardwareProfile": {
                "vmSize": vm_size
            },
            "storageProfile": {
                "imageReference": {
                    "publisher": publisher,
                    "offer": offer,
                    "sku": sku,
                    "version": "latest"
                }
            },
            "osProfile": {
                "adminUsername": admin_username
            },
            "networkProfile": {
                "networkInterfaces": []
            }
        }
    
    @staticmethod
    def create_storage_account_configuration(sku_name: str = "Standard_LRS",
                                           kind: str = "StorageV2",
                                           access_tier: str = "Hot") -> Dict[str, Any]:
        """Create a storage account configuration."""
        return {
            "sku": {
                "name": sku_name
            },
            "kind": kind,
            "accessTier": access_tier
        }
    
    @staticmethod
    def create_user_object(display_name: str, user_principal_name: str,
                          mail_nickname: str, password: str) -> Dict[str, Any]:
        """Create a user object for Azure AD."""
        return {
            "accountEnabled": True,
            "displayName": display_name,
            "mailNickname": mail_nickname,
            "userPrincipalName": user_principal_name,
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": password
            }
        }
    
    @staticmethod
    def create_group_object(display_name: str, mail_nickname: str,
                           description: str = "", group_types: List[str] = None) -> Dict[str, Any]:
        """Create a group object for Azure AD."""
        return {
            "displayName": display_name,
            "mailNickname": mail_nickname,
            "description": description,
            "groupTypes": group_types or [],
            "mailEnabled": False,
            "securityEnabled": True
        }


# Main test function for Azure Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Azure Node Test Suite ===")
        
        # Get Azure credentials from environment or user input
        tenant_id = os.environ.get("AZURE_TENANT_ID")
        client_id = os.environ.get("AZURE_CLIENT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")
        subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
        
        if not all([tenant_id, client_id, client_secret]):
            print("Azure credentials not found in environment variables")
            print("Please set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET")
            print("Or provide them when prompted...")
            tenant_id = tenant_id or input("Enter Azure Tenant ID: ")
            client_id = client_id or input("Enter Azure Client ID: ")
            client_secret = client_secret or input("Enter Azure Client Secret: ")
            subscription_id = subscription_id or input("Enter Azure Subscription ID: ")
        
        if not all([tenant_id, client_id, client_secret, subscription_id]):
            print("Azure credentials are required for testing")
            return
        
        # Create an instance of the Azure Node
        node = AzureNode()
        
        # Test cases
        test_cases = [
            {
                "name": "Get Access Token",
                "params": {
                    "operation": AzureOperation.GET_ACCESS_TOKEN,
                    "tenant_id": tenant_id,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": "https://management.azure.com/.default"
                },
                "expected_status": "success"
            }
        ]
        
        # Run test cases
        total_tests = len(test_cases)
        passed_tests = 0
        access_token = None
        
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
                        print(f"Access token acquired (expires in {result.get('expires_in')} seconds)")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
                # Add a delay between tests to avoid rate limiting
                await asyncio.sleep(2.0)
                
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # Additional tests with access token
        if access_token:
            additional_tests = [
                {
                    "name": "List Resource Groups",
                    "params": {
                        "operation": AzureOperation.LIST_RESOURCE_GROUPS,
                        "access_token": access_token,
                        "subscription_id": subscription_id
                    },
                    "expected_status": "success"
                }
            ]
            
            for test_case in additional_tests:
                print(f"\nRunning test: {test_case['name']}")
                
                try:
                    node_data = {"params": test_case["params"]}
                    result = await node.execute(node_data)
                    
                    if result["status"] == test_case["expected_status"]:
                        print(f"✅ PASS: {test_case['name']} - Status: {result['status']}")
                        if result.get("resources"):
                            print(f"Found {len(result['resources'])} resource groups")
                        passed_tests += 1
                        total_tests += 1
                    else:
                        print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                        print(f"Error: {result.get('error')}")
                        total_tests += 1
                        
                    await asyncio.sleep(2.0)
                    
                except Exception as e:
                    print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
                    total_tests += 1
        
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
    registry.register("azure", AzureNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register AzureNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")