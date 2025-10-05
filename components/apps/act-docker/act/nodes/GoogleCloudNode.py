"""
Google Cloud Platform Node - Comprehensive integration with Google Cloud Platform REST APIs
Provides access to all major GCP services including compute, storage, databases, AI/ML, and management operations.
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

class GoogleCloudOperation:
    """Operations available on Google Cloud Platform REST APIs."""
    
    # Authentication Operations
    GET_ACCESS_TOKEN = "get_access_token"
    
    # Compute Engine Operations
    LIST_INSTANCES = "list_instances"
    GET_INSTANCE = "get_instance"
    CREATE_INSTANCE = "create_instance"
    UPDATE_INSTANCE = "update_instance"
    DELETE_INSTANCE = "delete_instance"
    START_INSTANCE = "start_instance"
    STOP_INSTANCE = "stop_instance"
    RESTART_INSTANCE = "restart_instance"
    RESET_INSTANCE = "reset_instance"
    
    # Cloud Storage Operations
    LIST_BUCKETS = "list_buckets"
    GET_BUCKET = "get_bucket"
    CREATE_BUCKET = "create_bucket"
    UPDATE_BUCKET = "update_bucket"
    DELETE_BUCKET = "delete_bucket"
    LIST_OBJECTS = "list_objects"
    GET_OBJECT = "get_object"
    UPLOAD_OBJECT = "upload_object"
    DELETE_OBJECT = "delete_object"
    COPY_OBJECT = "copy_object"
    
    # BigQuery Operations
    LIST_DATASETS = "list_datasets"
    GET_DATASET = "get_dataset"
    CREATE_DATASET = "create_dataset"
    UPDATE_DATASET = "update_dataset"
    DELETE_DATASET = "delete_dataset"
    LIST_TABLES = "list_tables"
    GET_TABLE = "get_table"
    CREATE_TABLE = "create_table"
    UPDATE_TABLE = "update_table"
    DELETE_TABLE = "delete_table"
    QUERY_TABLE = "query_table"
    INSERT_ROWS = "insert_rows"
    
    # Cloud SQL Operations
    LIST_SQL_INSTANCES = "list_sql_instances"
    GET_SQL_INSTANCE = "get_sql_instance"
    CREATE_SQL_INSTANCE = "create_sql_instance"
    UPDATE_SQL_INSTANCE = "update_sql_instance"
    DELETE_SQL_INSTANCE = "delete_sql_instance"
    START_SQL_INSTANCE = "start_sql_instance"
    STOP_SQL_INSTANCE = "stop_sql_instance"
    RESTART_SQL_INSTANCE = "restart_sql_instance"
    LIST_SQL_DATABASES = "list_sql_databases"
    CREATE_SQL_DATABASE = "create_sql_database"
    DELETE_SQL_DATABASE = "delete_sql_database"
    
    # Cloud Functions Operations
    LIST_FUNCTIONS = "list_functions"
    GET_FUNCTION = "get_function"
    CREATE_FUNCTION = "create_function"
    UPDATE_FUNCTION = "update_function"
    DELETE_FUNCTION = "delete_function"
    CALL_FUNCTION = "call_function"
    
    # Kubernetes Engine (GKE) Operations
    LIST_CLUSTERS = "list_clusters"
    GET_CLUSTER = "get_cluster"
    CREATE_CLUSTER = "create_cluster"
    UPDATE_CLUSTER = "update_cluster"
    DELETE_CLUSTER = "delete_cluster"
    LIST_NODE_POOLS = "list_node_pools"
    CREATE_NODE_POOL = "create_node_pool"
    DELETE_NODE_POOL = "delete_node_pool"
    
    # App Engine Operations
    LIST_APPS = "list_apps"
    GET_APP = "get_app"
    CREATE_APP = "create_app"
    UPDATE_APP = "update_app"
    LIST_SERVICES = "list_services"
    GET_SERVICE = "get_service"
    CREATE_SERVICE = "create_service"
    DELETE_SERVICE = "delete_service"
    LIST_VERSIONS = "list_versions"
    CREATE_VERSION = "create_version"
    DELETE_VERSION = "delete_version"
    
    # Cloud Build Operations
    LIST_BUILDS = "list_builds"
    GET_BUILD = "get_build"
    CREATE_BUILD = "create_build"
    CANCEL_BUILD = "cancel_build"
    LIST_BUILD_TRIGGERS = "list_build_triggers"
    CREATE_BUILD_TRIGGER = "create_build_trigger"
    DELETE_BUILD_TRIGGER = "delete_build_trigger"
    
    # IAM Operations
    LIST_SERVICE_ACCOUNTS = "list_service_accounts"
    GET_SERVICE_ACCOUNT = "get_service_account"
    CREATE_SERVICE_ACCOUNT = "create_service_account"
    UPDATE_SERVICE_ACCOUNT = "update_service_account"
    DELETE_SERVICE_ACCOUNT = "delete_service_account"
    GET_IAM_POLICY = "get_iam_policy"
    SET_IAM_POLICY = "set_iam_policy"
    TEST_IAM_PERMISSIONS = "test_iam_permissions"
    
    # Cloud Monitoring Operations
    LIST_METRICS = "list_metrics"
    GET_METRIC = "get_metric"
    CREATE_METRIC = "create_metric"
    DELETE_METRIC = "delete_metric"
    LIST_ALERTS = "list_alerts"
    CREATE_ALERT = "create_alert"
    DELETE_ALERT = "delete_alert"
    
    # Cloud Logging Operations
    LIST_LOGS = "list_logs"
    LIST_LOG_ENTRIES = "list_log_entries"
    WRITE_LOG_ENTRIES = "write_log_entries"
    DELETE_LOG = "delete_log"
    
    # Pub/Sub Operations
    LIST_TOPICS = "list_topics"
    GET_TOPIC = "get_topic"
    CREATE_TOPIC = "create_topic"
    DELETE_TOPIC = "delete_topic"
    PUBLISH_MESSAGE = "publish_message"
    LIST_SUBSCRIPTIONS = "list_subscriptions"
    CREATE_SUBSCRIPTION = "create_subscription"
    DELETE_SUBSCRIPTION = "delete_subscription"
    PULL_MESSAGES = "pull_messages"
    
    # Cloud Firestore Operations
    LIST_DOCUMENTS = "list_documents"
    GET_DOCUMENT = "get_document"
    CREATE_DOCUMENT = "create_document"
    UPDATE_DOCUMENT = "update_document"
    DELETE_DOCUMENT = "delete_document"
    QUERY_DOCUMENTS = "query_documents"
    
    # Project Management Operations
    LIST_PROJECTS = "list_projects"
    GET_PROJECT = "get_project"
    CREATE_PROJECT = "create_project"
    UPDATE_PROJECT = "update_project"
    DELETE_PROJECT = "delete_project"

class GoogleCloudNode(BaseNode):
    """
    Node for interacting with Google Cloud Platform REST APIs.
    Provides comprehensive functionality for compute, storage, databases, AI/ML, and management operations.
    """
    
    COMPUTE_BASE_URL = "https://compute.googleapis.com/compute/v1"
    STORAGE_BASE_URL = "https://storage.googleapis.com/storage/v1"
    BIGQUERY_BASE_URL = "https://bigquery.googleapis.com/bigquery/v2"
    SQLADMIN_BASE_URL = "https://sqladmin.googleapis.com/v1"
    FUNCTIONS_BASE_URL = "https://cloudfunctions.googleapis.com/v1"
    CONTAINER_BASE_URL = "https://container.googleapis.com/v1"
    APPENGINE_BASE_URL = "https://appengine.googleapis.com/v1"
    CLOUDBUILD_BASE_URL = "https://cloudbuild.googleapis.com/v1"
    IAM_BASE_URL = "https://iam.googleapis.com/v1"
    MONITORING_BASE_URL = "https://monitoring.googleapis.com/v1"
    LOGGING_BASE_URL = "https://logging.googleapis.com/v2"
    PUBSUB_BASE_URL = "https://pubsub.googleapis.com/v1"
    FIRESTORE_BASE_URL = "https://firestore.googleapis.com/v1"
    RESOURCE_MANAGER_BASE_URL = "https://cloudresourcemanager.googleapis.com/v1"
    OAUTH_BASE_URL = "https://oauth2.googleapis.com/token"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Google Cloud node."""
        return NodeSchema(
            node_type="googlecloud",
            version="1.0.0",
            description="Comprehensive integration with Google Cloud Platform REST APIs for compute, storage, databases, AI/ML, and management operations",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Google Cloud API",
                    required=True,
                    enum=[
                        GoogleCloudOperation.GET_ACCESS_TOKEN,
                        GoogleCloudOperation.LIST_INSTANCES,
                        GoogleCloudOperation.GET_INSTANCE,
                        GoogleCloudOperation.CREATE_INSTANCE,
                        GoogleCloudOperation.UPDATE_INSTANCE,
                        GoogleCloudOperation.DELETE_INSTANCE,
                        GoogleCloudOperation.START_INSTANCE,
                        GoogleCloudOperation.STOP_INSTANCE,
                        GoogleCloudOperation.RESTART_INSTANCE,
                        GoogleCloudOperation.RESET_INSTANCE,
                        GoogleCloudOperation.LIST_BUCKETS,
                        GoogleCloudOperation.GET_BUCKET,
                        GoogleCloudOperation.CREATE_BUCKET,
                        GoogleCloudOperation.UPDATE_BUCKET,
                        GoogleCloudOperation.DELETE_BUCKET,
                        GoogleCloudOperation.LIST_OBJECTS,
                        GoogleCloudOperation.GET_OBJECT,
                        GoogleCloudOperation.UPLOAD_OBJECT,
                        GoogleCloudOperation.DELETE_OBJECT,
                        GoogleCloudOperation.COPY_OBJECT,
                        GoogleCloudOperation.LIST_DATASETS,
                        GoogleCloudOperation.GET_DATASET,
                        GoogleCloudOperation.CREATE_DATASET,
                        GoogleCloudOperation.UPDATE_DATASET,
                        GoogleCloudOperation.DELETE_DATASET,
                        GoogleCloudOperation.LIST_TABLES,
                        GoogleCloudOperation.GET_TABLE,
                        GoogleCloudOperation.CREATE_TABLE,
                        GoogleCloudOperation.UPDATE_TABLE,
                        GoogleCloudOperation.DELETE_TABLE,
                        GoogleCloudOperation.QUERY_TABLE,
                        GoogleCloudOperation.INSERT_ROWS,
                        GoogleCloudOperation.LIST_SQL_INSTANCES,
                        GoogleCloudOperation.GET_SQL_INSTANCE,
                        GoogleCloudOperation.CREATE_SQL_INSTANCE,
                        GoogleCloudOperation.UPDATE_SQL_INSTANCE,
                        GoogleCloudOperation.DELETE_SQL_INSTANCE,
                        GoogleCloudOperation.START_SQL_INSTANCE,
                        GoogleCloudOperation.STOP_SQL_INSTANCE,
                        GoogleCloudOperation.RESTART_SQL_INSTANCE,
                        GoogleCloudOperation.LIST_SQL_DATABASES,
                        GoogleCloudOperation.CREATE_SQL_DATABASE,
                        GoogleCloudOperation.DELETE_SQL_DATABASE,
                        GoogleCloudOperation.LIST_FUNCTIONS,
                        GoogleCloudOperation.GET_FUNCTION,
                        GoogleCloudOperation.CREATE_FUNCTION,
                        GoogleCloudOperation.UPDATE_FUNCTION,
                        GoogleCloudOperation.DELETE_FUNCTION,
                        GoogleCloudOperation.CALL_FUNCTION,
                        GoogleCloudOperation.LIST_CLUSTERS,
                        GoogleCloudOperation.GET_CLUSTER,
                        GoogleCloudOperation.CREATE_CLUSTER,
                        GoogleCloudOperation.UPDATE_CLUSTER,
                        GoogleCloudOperation.DELETE_CLUSTER,
                        GoogleCloudOperation.LIST_NODE_POOLS,
                        GoogleCloudOperation.CREATE_NODE_POOL,
                        GoogleCloudOperation.DELETE_NODE_POOL,
                        GoogleCloudOperation.LIST_APPS,
                        GoogleCloudOperation.GET_APP,
                        GoogleCloudOperation.CREATE_APP,
                        GoogleCloudOperation.UPDATE_APP,
                        GoogleCloudOperation.LIST_SERVICES,
                        GoogleCloudOperation.GET_SERVICE,
                        GoogleCloudOperation.CREATE_SERVICE,
                        GoogleCloudOperation.DELETE_SERVICE,
                        GoogleCloudOperation.LIST_VERSIONS,
                        GoogleCloudOperation.CREATE_VERSION,
                        GoogleCloudOperation.DELETE_VERSION,
                        GoogleCloudOperation.LIST_BUILDS,
                        GoogleCloudOperation.GET_BUILD,
                        GoogleCloudOperation.CREATE_BUILD,
                        GoogleCloudOperation.CANCEL_BUILD,
                        GoogleCloudOperation.LIST_BUILD_TRIGGERS,
                        GoogleCloudOperation.CREATE_BUILD_TRIGGER,
                        GoogleCloudOperation.DELETE_BUILD_TRIGGER,
                        GoogleCloudOperation.LIST_SERVICE_ACCOUNTS,
                        GoogleCloudOperation.GET_SERVICE_ACCOUNT,
                        GoogleCloudOperation.CREATE_SERVICE_ACCOUNT,
                        GoogleCloudOperation.UPDATE_SERVICE_ACCOUNT,
                        GoogleCloudOperation.DELETE_SERVICE_ACCOUNT,
                        GoogleCloudOperation.GET_IAM_POLICY,
                        GoogleCloudOperation.SET_IAM_POLICY,
                        GoogleCloudOperation.TEST_IAM_PERMISSIONS,
                        GoogleCloudOperation.LIST_METRICS,
                        GoogleCloudOperation.GET_METRIC,
                        GoogleCloudOperation.CREATE_METRIC,
                        GoogleCloudOperation.DELETE_METRIC,
                        GoogleCloudOperation.LIST_ALERTS,
                        GoogleCloudOperation.CREATE_ALERT,
                        GoogleCloudOperation.DELETE_ALERT,
                        GoogleCloudOperation.LIST_LOGS,
                        GoogleCloudOperation.LIST_LOG_ENTRIES,
                        GoogleCloudOperation.WRITE_LOG_ENTRIES,
                        GoogleCloudOperation.DELETE_LOG,
                        GoogleCloudOperation.LIST_TOPICS,
                        GoogleCloudOperation.GET_TOPIC,
                        GoogleCloudOperation.CREATE_TOPIC,
                        GoogleCloudOperation.DELETE_TOPIC,
                        GoogleCloudOperation.PUBLISH_MESSAGE,
                        GoogleCloudOperation.LIST_SUBSCRIPTIONS,
                        GoogleCloudOperation.CREATE_SUBSCRIPTION,
                        GoogleCloudOperation.DELETE_SUBSCRIPTION,
                        GoogleCloudOperation.PULL_MESSAGES,
                        GoogleCloudOperation.LIST_DOCUMENTS,
                        GoogleCloudOperation.GET_DOCUMENT,
                        GoogleCloudOperation.CREATE_DOCUMENT,
                        GoogleCloudOperation.UPDATE_DOCUMENT,
                        GoogleCloudOperation.DELETE_DOCUMENT,
                        GoogleCloudOperation.QUERY_DOCUMENTS,
                        GoogleCloudOperation.LIST_PROJECTS,
                        GoogleCloudOperation.GET_PROJECT,
                        GoogleCloudOperation.CREATE_PROJECT,
                        GoogleCloudOperation.UPDATE_PROJECT,
                        GoogleCloudOperation.DELETE_PROJECT
                    ]
                ),
                NodeParameter(
                    name="service_account_key",
                    type=NodeParameterType.SECRET,
                    description="Google Cloud service account key JSON",
                    required=False
                ),
                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.SECRET,
                    description="Google Cloud access token for authentication",
                    required=False
                ),
                NodeParameter(
                    name="project_id",
                    type=NodeParameterType.STRING,
                    description="Google Cloud project ID",
                    required=False
                ),
                NodeParameter(
                    name="zone",
                    type=NodeParameterType.STRING,
                    description="Google Cloud zone (e.g., us-central1-a)",
                    required=False
                ),
                NodeParameter(
                    name="region",
                    type=NodeParameterType.STRING,
                    description="Google Cloud region (e.g., us-central1)",
                    required=False
                ),
                NodeParameter(
                    name="instance_name",
                    type=NodeParameterType.STRING,
                    description="Compute Engine instance name",
                    required=False
                ),
                NodeParameter(
                    name="machine_type",
                    type=NodeParameterType.STRING,
                    description="Compute Engine machine type",
                    required=False,
                    default="e2-micro"
                ),
                NodeParameter(
                    name="bucket_name",
                    type=NodeParameterType.STRING,
                    description="Cloud Storage bucket name",
                    required=False
                ),
                NodeParameter(
                    name="object_name",
                    type=NodeParameterType.STRING,
                    description="Cloud Storage object name",
                    required=False
                ),
                NodeParameter(
                    name="file_content",
                    type=NodeParameterType.STRING,
                    description="Content for file upload operations",
                    required=False
                ),
                NodeParameter(
                    name="dataset_id",
                    type=NodeParameterType.STRING,
                    description="BigQuery dataset ID",
                    required=False
                ),
                NodeParameter(
                    name="table_id",
                    type=NodeParameterType.STRING,
                    description="BigQuery table ID",
                    required=False
                ),
                NodeParameter(
                    name="query",
                    type=NodeParameterType.STRING,
                    description="SQL query for BigQuery operations",
                    required=False
                ),
                NodeParameter(
                    name="sql_instance_id",
                    type=NodeParameterType.STRING,
                    description="Cloud SQL instance ID",
                    required=False
                ),
                NodeParameter(
                    name="database_name",
                    type=NodeParameterType.STRING,
                    description="Database name for Cloud SQL operations",
                    required=False
                ),
                NodeParameter(
                    name="function_name",
                    type=NodeParameterType.STRING,
                    description="Cloud Functions function name",
                    required=False
                ),
                NodeParameter(
                    name="cluster_name",
                    type=NodeParameterType.STRING,
                    description="GKE cluster name",
                    required=False
                ),
                NodeParameter(
                    name="service_name",
                    type=NodeParameterType.STRING,
                    description="App Engine service name",
                    required=False
                ),
                NodeParameter(
                    name="version_id",
                    type=NodeParameterType.STRING,
                    description="App Engine version ID",
                    required=False
                ),
                NodeParameter(
                    name="build_id",
                    type=NodeParameterType.STRING,
                    description="Cloud Build build ID",
                    required=False
                ),
                NodeParameter(
                    name="service_account_email",
                    type=NodeParameterType.STRING,
                    description="Service account email address",
                    required=False
                ),
                NodeParameter(
                    name="topic_name",
                    type=NodeParameterType.STRING,
                    description="Pub/Sub topic name",
                    required=False
                ),
                NodeParameter(
                    name="subscription_name",
                    type=NodeParameterType.STRING,
                    description="Pub/Sub subscription name",
                    required=False
                ),
                NodeParameter(
                    name="collection_id",
                    type=NodeParameterType.STRING,
                    description="Firestore collection ID",
                    required=False
                ),
                NodeParameter(
                    name="document_id",
                    type=NodeParameterType.STRING,
                    description="Firestore document ID",
                    required=False
                ),
                NodeParameter(
                    name="data",
                    type=NodeParameterType.OBJECT,
                    description="Data payload for create/update operations",
                    required=False
                ),
                NodeParameter(
                    name="metadata",
                    type=NodeParameterType.OBJECT,
                    description="Metadata for resource operations",
                    required=False
                ),
                NodeParameter(
                    name="labels",
                    type=NodeParameterType.OBJECT,
                    description="Labels for resource tagging",
                    required=False
                ),
                NodeParameter(
                    name="scopes",
                    type=NodeParameterType.ARRAY,
                    description="OAuth 2.0 scopes for authentication",
                    required=False,
                    default=["https://www.googleapis.com/auth/cloud-platform"]
                ),
                NodeParameter(
                    name="options",
                    type=NodeParameterType.OBJECT,
                    description="Additional options for API operations",
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
                "instances": NodeParameterType.ARRAY,
                "instance": NodeParameterType.OBJECT,
                "buckets": NodeParameterType.ARRAY,
                "bucket": NodeParameterType.OBJECT,
                "objects": NodeParameterType.ARRAY,
                "object_data": NodeParameterType.ANY,
                "datasets": NodeParameterType.ARRAY,
                "dataset": NodeParameterType.OBJECT,
                "tables": NodeParameterType.ARRAY,
                "table": NodeParameterType.OBJECT,
                "query_results": NodeParameterType.OBJECT,
                "sql_instances": NodeParameterType.ARRAY,
                "sql_instance": NodeParameterType.OBJECT,
                "databases": NodeParameterType.ARRAY,
                "functions": NodeParameterType.ARRAY,
                "function": NodeParameterType.OBJECT,
                "clusters": NodeParameterType.ARRAY,
                "cluster": NodeParameterType.OBJECT,
                "apps": NodeParameterType.ARRAY,
                "app": NodeParameterType.OBJECT,
                "services": NodeParameterType.ARRAY,
                "service": NodeParameterType.OBJECT,
                "builds": NodeParameterType.ARRAY,
                "build": NodeParameterType.OBJECT,
                "service_accounts": NodeParameterType.ARRAY,
                "service_account": NodeParameterType.OBJECT,
                "topics": NodeParameterType.ARRAY,
                "topic": NodeParameterType.OBJECT,
                "subscriptions": NodeParameterType.ARRAY,
                "subscription": NodeParameterType.OBJECT,
                "messages": NodeParameterType.ARRAY,
                "documents": NodeParameterType.ARRAY,
                "document": NodeParameterType.OBJECT,
                "projects": NodeParameterType.ARRAY,
                "project": NodeParameterType.OBJECT,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["googlecloud", "gcp", "google", "cloud", "api", "integration", "compute", "storage"],
            author="System",
            documentation_url="https://cloud.google.com/apis/docs/overview"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for authentication
        has_access_token = params.get("access_token")
        has_service_account_key = params.get("service_account_key")
        
        if not has_access_token and not has_service_account_key and operation != GoogleCloudOperation.GET_ACCESS_TOKEN:
            raise NodeValidationError("Either access_token or service_account_key is required for authentication")
            
        # Validate based on operation
        if operation in [GoogleCloudOperation.LIST_INSTANCES, GoogleCloudOperation.GET_INSTANCE,
                        GoogleCloudOperation.CREATE_INSTANCE, GoogleCloudOperation.DELETE_INSTANCE,
                        GoogleCloudOperation.START_INSTANCE, GoogleCloudOperation.STOP_INSTANCE]:
            if not params.get("project_id"):
                raise NodeValidationError("Project ID is required for Compute Engine operations")
            if not params.get("zone"):
                raise NodeValidationError("Zone is required for Compute Engine operations")
                
        elif operation in [GoogleCloudOperation.LIST_BUCKETS, GoogleCloudOperation.GET_BUCKET,
                          GoogleCloudOperation.CREATE_BUCKET, GoogleCloudOperation.DELETE_BUCKET]:
            if not params.get("project_id"):
                raise NodeValidationError("Project ID is required for Cloud Storage operations")
                
        elif operation in [GoogleCloudOperation.LIST_OBJECTS, GoogleCloudOperation.GET_OBJECT,
                          GoogleCloudOperation.UPLOAD_OBJECT, GoogleCloudOperation.DELETE_OBJECT]:
            if not params.get("bucket_name"):
                raise NodeValidationError("Bucket name is required for object operations")
                
        elif operation in [GoogleCloudOperation.LIST_DATASETS, GoogleCloudOperation.GET_DATASET,
                          GoogleCloudOperation.CREATE_DATASET, GoogleCloudOperation.DELETE_DATASET]:
            if not params.get("project_id"):
                raise NodeValidationError("Project ID is required for BigQuery operations")
                
        elif operation in [GoogleCloudOperation.LIST_TABLES, GoogleCloudOperation.GET_TABLE,
                          GoogleCloudOperation.CREATE_TABLE, GoogleCloudOperation.DELETE_TABLE,
                          GoogleCloudOperation.QUERY_TABLE]:
            if not params.get("project_id"):
                raise NodeValidationError("Project ID is required for BigQuery operations")
            if not params.get("dataset_id"):
                raise NodeValidationError("Dataset ID is required for table operations")
                
        elif operation in [GoogleCloudOperation.LIST_SQL_INSTANCES, GoogleCloudOperation.GET_SQL_INSTANCE,
                          GoogleCloudOperation.CREATE_SQL_INSTANCE, GoogleCloudOperation.DELETE_SQL_INSTANCE]:
            if not params.get("project_id"):
                raise NodeValidationError("Project ID is required for Cloud SQL operations")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Google Cloud node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Execute the appropriate operation
            if operation == GoogleCloudOperation.GET_ACCESS_TOKEN:
                return await self._operation_get_access_token(validated_data)
                
            # Compute Engine Operations
            elif operation == GoogleCloudOperation.LIST_INSTANCES:
                return await self._operation_list_instances(validated_data)
            elif operation == GoogleCloudOperation.GET_INSTANCE:
                return await self._operation_get_instance(validated_data)
            elif operation == GoogleCloudOperation.CREATE_INSTANCE:
                return await self._operation_create_instance(validated_data)
            elif operation == GoogleCloudOperation.START_INSTANCE:
                return await self._operation_start_instance(validated_data)
            elif operation == GoogleCloudOperation.STOP_INSTANCE:
                return await self._operation_stop_instance(validated_data)
                
            # Cloud Storage Operations
            elif operation == GoogleCloudOperation.LIST_BUCKETS:
                return await self._operation_list_buckets(validated_data)
            elif operation == GoogleCloudOperation.GET_BUCKET:
                return await self._operation_get_bucket(validated_data)
            elif operation == GoogleCloudOperation.CREATE_BUCKET:
                return await self._operation_create_bucket(validated_data)
            elif operation == GoogleCloudOperation.LIST_OBJECTS:
                return await self._operation_list_objects(validated_data)
            elif operation == GoogleCloudOperation.GET_OBJECT:
                return await self._operation_get_object(validated_data)
            elif operation == GoogleCloudOperation.UPLOAD_OBJECT:
                return await self._operation_upload_object(validated_data)
                
            # BigQuery Operations
            elif operation == GoogleCloudOperation.LIST_DATASETS:
                return await self._operation_list_datasets(validated_data)
            elif operation == GoogleCloudOperation.GET_DATASET:
                return await self._operation_get_dataset(validated_data)
            elif operation == GoogleCloudOperation.CREATE_DATASET:
                return await self._operation_create_dataset(validated_data)
            elif operation == GoogleCloudOperation.LIST_TABLES:
                return await self._operation_list_tables(validated_data)
            elif operation == GoogleCloudOperation.QUERY_TABLE:
                return await self._operation_query_table(validated_data)
                
            # Cloud SQL Operations
            elif operation == GoogleCloudOperation.LIST_SQL_INSTANCES:
                return await self._operation_list_sql_instances(validated_data)
            elif operation == GoogleCloudOperation.GET_SQL_INSTANCE:
                return await self._operation_get_sql_instance(validated_data)
                
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
            error_message = f"Error in Google Cloud node: {str(e)}"
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
        """Make an HTTP request to the Google Cloud API."""
        
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
                    error_message = f"Google Cloud API error {response.status}: {response_data}"
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
        """Get access token using service account key."""
        service_account_key = params.get("service_account_key")
        scopes = params.get("scopes", ["https://www.googleapis.com/auth/cloud-platform"])
        
        if not service_account_key:
            return {
                "status": "error",
                "error": "Service account key is required for authentication",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
        
        try:
            # Parse service account key
            if isinstance(service_account_key, str):
                key_data = json.loads(service_account_key)
            else:
                key_data = service_account_key
            
            # Create JWT assertion for service account authentication
            import jwt
            from datetime import datetime, timedelta
            
            now = datetime.utcnow()
            payload = {
                "iss": key_data["client_email"],
                "scope": " ".join(scopes),
                "aud": "https://oauth2.googleapis.com/token",
                "iat": now,
                "exp": now + timedelta(hours=1)
            }
            
            # Sign JWT with private key
            assertion = jwt.encode(payload, key_data["private_key"], algorithm="RS256")
            
            # Request access token
            data = {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": assertion
            }
            
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            result = await self._make_request("POST", self.OAUTH_BASE_URL, params, urlencode(data), headers)
            
            if result["status"] == "success" and result["result"]:
                token_data = result["result"]
                result["access_token"] = token_data.get("access_token")
                result["token_type"] = token_data.get("token_type")
                result["expires_in"] = token_data.get("expires_in")
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error generating access token: {str(e)}",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    # -------------------------
    # Compute Engine Operations
    # -------------------------
    
    async def _operation_list_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Compute Engine instances."""
        project_id = params.get("project_id")
        zone = params.get("zone")
        
        url = f"{self.COMPUTE_BASE_URL}/projects/{project_id}/zones/{zone}/instances"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            result["instances"] = result["result"].get("items", [])
        
        return result
    
    async def _operation_get_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific Compute Engine instance."""
        project_id = params.get("project_id")
        zone = params.get("zone")
        instance_name = params.get("instance_name")
        
        url = f"{self.COMPUTE_BASE_URL}/projects/{project_id}/zones/{zone}/instances/{instance_name}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success":
            result["instance"] = result["result"]
        
        return result
    
    async def _operation_create_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Compute Engine instance."""
        project_id = params.get("project_id")
        zone = params.get("zone")
        instance_name = params.get("instance_name")
        machine_type = params.get("machine_type", "e2-micro")
        
        # Basic instance configuration
        instance_config = params.get("data", {
            "name": instance_name,
            "machineType": f"zones/{zone}/machineTypes/{machine_type}",
            "disks": [
                {
                    "boot": True,
                    "autoDelete": True,
                    "initializeParams": {
                        "sourceImage": "projects/debian-cloud/global/images/family/debian-11"
                    }
                }
            ],
            "networkInterfaces": [
                {
                    "network": "global/networks/default",
                    "accessConfigs": [
                        {
                            "type": "ONE_TO_ONE_NAT",
                            "name": "External NAT"
                        }
                    ]
                }
            ]
        })
        
        if params.get("labels"):
            instance_config["labels"] = params.get("labels")
        
        url = f"{self.COMPUTE_BASE_URL}/projects/{project_id}/zones/{zone}/instances"
        
        result = await self._make_request("POST", url, params, instance_config)
        
        if result["status"] == "success":
            result["instance"] = result["result"]
        
        return result
    
    async def _operation_start_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start a Compute Engine instance."""
        project_id = params.get("project_id")
        zone = params.get("zone")
        instance_name = params.get("instance_name")
        
        url = f"{self.COMPUTE_BASE_URL}/projects/{project_id}/zones/{zone}/instances/{instance_name}/start"
        
        return await self._make_request("POST", url, params)
    
    async def _operation_stop_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop a Compute Engine instance."""
        project_id = params.get("project_id")
        zone = params.get("zone")
        instance_name = params.get("instance_name")
        
        url = f"{self.COMPUTE_BASE_URL}/projects/{project_id}/zones/{zone}/instances/{instance_name}/stop"
        
        return await self._make_request("POST", url, params)
    
    # -------------------------
    # Cloud Storage Operations
    # -------------------------
    
    async def _operation_list_buckets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Cloud Storage buckets."""
        project_id = params.get("project_id")
        
        url = f"{self.STORAGE_BASE_URL}/b?project={project_id}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            result["buckets"] = result["result"].get("items", [])
        
        return result
    
    async def _operation_get_bucket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific Cloud Storage bucket."""
        bucket_name = params.get("bucket_name")
        
        url = f"{self.STORAGE_BASE_URL}/b/{bucket_name}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success":
            result["bucket"] = result["result"]
        
        return result
    
    async def _operation_create_bucket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Cloud Storage bucket."""
        project_id = params.get("project_id")
        bucket_name = params.get("bucket_name")
        
        bucket_config = params.get("data", {
            "name": bucket_name,
            "location": "US"
        })
        
        if params.get("labels"):
            bucket_config["labels"] = params.get("labels")
        
        url = f"{self.STORAGE_BASE_URL}/b?project={project_id}"
        
        result = await self._make_request("POST", url, params, bucket_config)
        
        if result["status"] == "success":
            result["bucket"] = result["result"]
        
        return result
    
    async def _operation_list_objects(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List objects in a Cloud Storage bucket."""
        bucket_name = params.get("bucket_name")
        
        url = f"{self.STORAGE_BASE_URL}/b/{bucket_name}/o"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            result["objects"] = result["result"].get("items", [])
        
        return result
    
    async def _operation_get_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get an object from Cloud Storage."""
        bucket_name = params.get("bucket_name")
        object_name = params.get("object_name")
        
        url = f"{self.STORAGE_BASE_URL}/b/{bucket_name}/o/{object_name}?alt=media"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success":
            result["object_data"] = result["result"]
        
        return result
    
    async def _operation_upload_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Upload an object to Cloud Storage."""
        bucket_name = params.get("bucket_name")
        object_name = params.get("object_name")
        file_content = params.get("file_content", "")
        
        # Upload media
        upload_url = f"https://storage.googleapis.com/upload/storage/v1/b/{bucket_name}/o?uploadType=media&name={object_name}"
        
        headers = {"Content-Type": "application/octet-stream"}
        
        return await self._make_request("POST", upload_url, params, file_content, headers)
    
    # -------------------------
    # BigQuery Operations
    # -------------------------
    
    async def _operation_list_datasets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List BigQuery datasets."""
        project_id = params.get("project_id")
        
        url = f"{self.BIGQUERY_BASE_URL}/projects/{project_id}/datasets"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            result["datasets"] = result["result"].get("datasets", [])
        
        return result
    
    async def _operation_get_dataset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific BigQuery dataset."""
        project_id = params.get("project_id")
        dataset_id = params.get("dataset_id")
        
        url = f"{self.BIGQUERY_BASE_URL}/projects/{project_id}/datasets/{dataset_id}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success":
            result["dataset"] = result["result"]
        
        return result
    
    async def _operation_create_dataset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new BigQuery dataset."""
        project_id = params.get("project_id")
        dataset_id = params.get("dataset_id")
        
        dataset_config = params.get("data", {
            "datasetReference": {
                "datasetId": dataset_id,
                "projectId": project_id
            },
            "location": "US"
        })
        
        url = f"{self.BIGQUERY_BASE_URL}/projects/{project_id}/datasets"
        
        result = await self._make_request("POST", url, params, dataset_config)
        
        if result["status"] == "success":
            result["dataset"] = result["result"]
        
        return result
    
    async def _operation_list_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List tables in a BigQuery dataset."""
        project_id = params.get("project_id")
        dataset_id = params.get("dataset_id")
        
        url = f"{self.BIGQUERY_BASE_URL}/projects/{project_id}/datasets/{dataset_id}/tables"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            result["tables"] = result["result"].get("tables", [])
        
        return result
    
    async def _operation_query_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a query in BigQuery."""
        project_id = params.get("project_id")
        query = params.get("query")
        
        query_config = {
            "query": query,
            "useLegacySql": False
        }
        
        if params.get("options"):
            query_config.update(params.get("options"))
        
        url = f"{self.BIGQUERY_BASE_URL}/projects/{project_id}/queries"
        
        result = await self._make_request("POST", url, params, query_config)
        
        if result["status"] == "success":
            result["query_results"] = result["result"]
        
        return result
    
    # -------------------------
    # Cloud SQL Operations
    # -------------------------
    
    async def _operation_list_sql_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Cloud SQL instances."""
        project_id = params.get("project_id")
        
        url = f"{self.SQLADMIN_BASE_URL}/projects/{project_id}/instances"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success" and result["result"]:
            result["sql_instances"] = result["result"].get("items", [])
        
        return result
    
    async def _operation_get_sql_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific Cloud SQL instance."""
        project_id = params.get("project_id")
        sql_instance_id = params.get("sql_instance_id")
        
        url = f"{self.SQLADMIN_BASE_URL}/projects/{project_id}/instances/{sql_instance_id}"
        
        result = await self._make_request("GET", url, params)
        
        if result["status"] == "success":
            result["sql_instance"] = result["result"]
        
        return result


# Utility functions for common Google Cloud operations
class GoogleCloudHelpers:
    """Helper functions for common Google Cloud operations."""
    
    @staticmethod
    def create_instance_configuration(instance_name: str, machine_type: str = "e2-micro",
                                    zone: str = "us-central1-a",
                                    image_family: str = "debian-11",
                                    image_project: str = "debian-cloud") -> Dict[str, Any]:
        """Create a Compute Engine instance configuration."""
        return {
            "name": instance_name,
            "machineType": f"zones/{zone}/machineTypes/{machine_type}",
            "disks": [
                {
                    "boot": True,
                    "autoDelete": True,
                    "initializeParams": {
                        "sourceImage": f"projects/{image_project}/global/images/family/{image_family}"
                    }
                }
            ],
            "networkInterfaces": [
                {
                    "network": "global/networks/default",
                    "accessConfigs": [
                        {
                            "type": "ONE_TO_ONE_NAT",
                            "name": "External NAT"
                        }
                    ]
                }
            ]
        }
    
    @staticmethod
    def create_bucket_configuration(bucket_name: str, location: str = "US",
                                  storage_class: str = "STANDARD") -> Dict[str, Any]:
        """Create a Cloud Storage bucket configuration."""
        return {
            "name": bucket_name,
            "location": location,
            "storageClass": storage_class
        }
    
    @staticmethod
    def create_dataset_configuration(dataset_id: str, project_id: str,
                                   location: str = "US",
                                   description: str = "") -> Dict[str, Any]:
        """Create a BigQuery dataset configuration."""
        return {
            "datasetReference": {
                "datasetId": dataset_id,
                "projectId": project_id
            },
            "location": location,
            "description": description
        }
    
    @staticmethod
    def create_sql_instance_configuration(instance_id: str, database_version: str = "MYSQL_8_0",
                                        tier: str = "db-f1-micro",
                                        region: str = "us-central1") -> Dict[str, Any]:
        """Create a Cloud SQL instance configuration."""
        return {
            "name": instance_id,
            "databaseVersion": database_version,
            "settings": {
                "tier": tier,
                "availabilityType": "ZONAL",
                "backupConfiguration": {
                    "enabled": True
                },
                "ipConfiguration": {
                    "ipv4Enabled": True,
                    "authorizedNetworks": []
                }
            },
            "region": region
        }


# Main test function for Google Cloud Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Google Cloud Platform Node Test Suite ===")
        
        # Get Google Cloud credentials from environment or user input
        service_account_key = os.environ.get("GOOGLE_CLOUD_SERVICE_ACCOUNT_KEY")
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
        
        if not service_account_key:
            print("Google Cloud service account key not found in environment variables")
            print("Please set GOOGLE_CLOUD_SERVICE_ACCOUNT_KEY")
            print("Or provide it when prompted...")
            service_account_key_file = input("Enter path to service account key file (or press enter to skip): ")
            if service_account_key_file:
                try:
                    with open(service_account_key_file, 'r') as f:
                        service_account_key = f.read()
                except Exception as e:
                    print(f"Error reading service account key file: {e}")
        
        if not project_id:
            project_id = input("Enter Google Cloud Project ID: ")
        
        if not all([service_account_key, project_id]):
            print("Google Cloud credentials are required for testing")
            return
        
        # Create an instance of the Google Cloud Node
        node = GoogleCloudNode()
        
        # Test cases
        test_cases = [
            {
                "name": "Get Access Token",
                "params": {
                    "operation": GoogleCloudOperation.GET_ACCESS_TOKEN,
                    "service_account_key": service_account_key
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
                    "name": "List Cloud Storage Buckets",
                    "params": {
                        "operation": GoogleCloudOperation.LIST_BUCKETS,
                        "access_token": access_token,
                        "project_id": project_id
                    },
                    "expected_status": "success"
                },
                {
                    "name": "List BigQuery Datasets",
                    "params": {
                        "operation": GoogleCloudOperation.LIST_DATASETS,
                        "access_token": access_token,
                        "project_id": project_id
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
                        if result.get("buckets"):
                            print(f"Found {len(result['buckets'])} storage buckets")
                        if result.get("datasets"):
                            print(f"Found {len(result['datasets'])} BigQuery datasets")
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
    registry.register("googlecloud", GoogleCloudNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register GoogleCloudNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")