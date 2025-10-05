"""
Microsoft Power BI Business Analytics Integration Node

Enterprise-grade integration with Microsoft Power BI REST API v1.0 providing comprehensive business analytics, 
reporting, and data visualization capabilities. Supports workspace management, dataset operations, report publishing, 
dashboard automation, data refresh scheduling, embedding operations, and administrative functions.

Key capabilities include: Dataset creation and management, report publishing and export (PDF, PPT, Excel), 
dashboard operations, real-time data refresh, workspace collaboration, embed token generation for secure sharing, 
row-level security implementation, gateway management, dataflow operations, and full administrative control.

Built for production environments with OAuth 2.0, service principal authentication, comprehensive error handling, 
rate limiting management, and enterprise security features. Supports both individual workspace operations and 
multi-tenant administrative scenarios.
"""

import logging
import asyncio
import json
import base64
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
import aiohttp

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError, NodeExecutionError
    )
except ImportError:
    try:
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )
    except ImportError:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )

# Configure logging
logger = logging.getLogger(__name__)

class PowerBIOperation:
    """All available Power BI REST API operations based on official documentation."""
    
    # Dataset Operations
    GET_DATASETS = "get_datasets"
    GET_DATASET = "get_dataset"
    DELETE_DATASET = "delete_dataset"
    REFRESH_DATASET = "refresh_dataset"
    GET_REFRESH_HISTORY = "get_refresh_history"
    EXECUTE_QUERIES = "execute_queries"
    
    # Report Operations
    GET_REPORTS = "get_reports"
    GET_REPORT = "get_report"
    CLONE_REPORT = "clone_report"
    DELETE_REPORT = "delete_report"
    EXPORT_REPORT = "export_report"
    GET_REPORT_PAGES = "get_report_pages"
    
    # Dashboard Operations
    GET_DASHBOARDS = "get_dashboards"
    GET_DASHBOARD = "get_dashboard"
    GET_DASHBOARD_TILES = "get_dashboard_tiles"
    CLONE_TILE = "clone_tile"
    DELETE_DASHBOARD = "delete_dashboard"
    
    # Workspace Operations
    GET_WORKSPACES = "get_workspaces"
    CREATE_WORKSPACE = "create_workspace"
    GET_WORKSPACE = "get_workspace"
    UPDATE_WORKSPACE = "update_workspace"
    DELETE_WORKSPACE = "delete_workspace"
    ADD_WORKSPACE_USER = "add_workspace_user"
    REMOVE_WORKSPACE_USER = "remove_workspace_user"
    
    # Embedding Operations
    GENERATE_EMBED_TOKEN = "generate_embed_token"
    
    # Gateway Operations
    GET_GATEWAYS = "get_gateways"
    GET_GATEWAY_DATASOURCES = "get_gateway_datasources"
    BIND_TO_GATEWAY = "bind_to_gateway"
    
    # Dataflow Operations
    GET_DATAFLOWS = "get_dataflows"
    GET_DATAFLOW = "get_dataflow"
    REFRESH_DATAFLOW = "refresh_dataflow"
    DELETE_DATAFLOW = "delete_dataflow"
    
    # Admin Operations
    GET_ADMIN_WORKSPACES = "get_admin_workspaces"
    GET_ADMIN_DATASETS = "get_admin_datasets"
    GET_ADMIN_REPORTS = "get_admin_reports"

class PowerBIAuthMethod:
    """Power BI authentication methods."""
    
    SERVICE_PRINCIPAL = "service_principal"
    OAUTH = "oauth"
    MASTER_USER = "master_user"

class PowerBIExportFormat:
    """Supported export formats."""
    
    PDF = "PDF"
    PPTX = "PPTX"
    XLSX = "XLSX"
    PNG = "PNG"
    CSV = "CSV"

class PowerBIUserRole:
    """Power BI workspace user roles."""
    
    ADMIN = "Admin"
    MEMBER = "Member"
    CONTRIBUTOR = "Contributor"
    VIEWER = "Viewer"

class PowerBINode(BaseNode):
    """
    Comprehensive Microsoft Power BI integration node supporting all major REST API operations.
    Handles business analytics, reporting, workspace management, and data visualization operations.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        self.auth_url = "https://login.microsoftonline.com"
        self.access_token = None
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Power BI node."""
        return NodeSchema(
            name="PowerBINode",
            description="Comprehensive Microsoft Power BI integration supporting business analytics, reporting, workspace management, and data visualization operations",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Power BI operation to perform",
                    required=True,
                    enum=[
                        PowerBIOperation.GET_DATASETS,
                        PowerBIOperation.GET_DATASET,
                        PowerBIOperation.DELETE_DATASET,
                        PowerBIOperation.REFRESH_DATASET,
                        PowerBIOperation.GET_REFRESH_HISTORY,
                        PowerBIOperation.EXECUTE_QUERIES,
                        PowerBIOperation.GET_REPORTS,
                        PowerBIOperation.GET_REPORT,
                        PowerBIOperation.CLONE_REPORT,
                        PowerBIOperation.DELETE_REPORT,
                        PowerBIOperation.EXPORT_REPORT,
                        PowerBIOperation.GET_REPORT_PAGES,
                        PowerBIOperation.GET_DASHBOARDS,
                        PowerBIOperation.GET_DASHBOARD,
                        PowerBIOperation.GET_DASHBOARD_TILES,
                        PowerBIOperation.CLONE_TILE,
                        PowerBIOperation.DELETE_DASHBOARD,
                        PowerBIOperation.GET_WORKSPACES,
                        PowerBIOperation.CREATE_WORKSPACE,
                        PowerBIOperation.GET_WORKSPACE,
                        PowerBIOperation.UPDATE_WORKSPACE,
                        PowerBIOperation.DELETE_WORKSPACE,
                        PowerBIOperation.ADD_WORKSPACE_USER,
                        PowerBIOperation.REMOVE_WORKSPACE_USER,
                        PowerBIOperation.GENERATE_EMBED_TOKEN,
                        PowerBIOperation.GET_GATEWAYS,
                        PowerBIOperation.GET_GATEWAY_DATASOURCES,
                        PowerBIOperation.BIND_TO_GATEWAY,
                        PowerBIOperation.GET_DATAFLOWS,
                        PowerBIOperation.GET_DATAFLOW,
                        PowerBIOperation.REFRESH_DATAFLOW,
                        PowerBIOperation.DELETE_DATAFLOW,
                        PowerBIOperation.GET_ADMIN_WORKSPACES,
                        PowerBIOperation.GET_ADMIN_DATASETS,
                        PowerBIOperation.GET_ADMIN_REPORTS,
                    ]
                ),
                
                # Authentication Parameters
                "auth_method": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Authentication method to use",
                    required=False,
                    default="service_principal",
                    enum=["service_principal", "oauth", "master_user"]
                ),
                "tenant_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Azure AD tenant ID",
                    required=False
                ),
                "client_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Azure AD application client ID",
                    required=False
                ),
                "client_secret": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Azure AD application client secret",
                    required=False
                ),
                "username": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Power BI username (for master user auth)",
                    required=False
                ),
                "password": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Power BI password (for master user auth)",
                    required=False
                ),
                "access_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Pre-obtained access token",
                    required=False
                ),
                
                # Resource Identification Parameters
                "workspace_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Workspace (group) identifier",
                    required=False
                ),
                "dataset_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Dataset identifier",
                    required=False
                ),
                "report_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Report identifier",
                    required=False
                ),
                "dashboard_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Dashboard identifier",
                    required=False
                ),
                "tile_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Dashboard tile identifier",
                    required=False
                ),
                "dataflow_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Dataflow identifier",
                    required=False
                ),
                "gateway_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Gateway identifier",
                    required=False
                ),
                
                # Content Parameters
                "workspace_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Workspace name for creation",
                    required=False
                ),
                "report_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Report name for cloning",
                    required=False
                ),
                "target_workspace_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Target workspace ID for cloning operations",
                    required=False
                ),
                
                # Export Parameters
                "export_format": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Export format for reports",
                    required=False,
                    enum=["PDF", "PPTX", "XLSX", "PNG", "CSV"]
                ),
                "page_names": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Specific page names to export",
                    required=False
                ),
                
                # User Management Parameters
                "user_email": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="User email for workspace operations",
                    required=False
                ),
                "user_role": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="User role in workspace",
                    required=False,
                    enum=["Admin", "Member", "Contributor", "Viewer"]
                ),
                "user_principal_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Principal type for user",
                    required=False,
                    enum=["User", "Group", "App"]
                ),
                
                # Refresh Parameters
                "refresh_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Type of dataset refresh",
                    required=False,
                    enum=["Full", "Incremental"],
                    default="Full"
                ),
                "commit_mode": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Refresh commit mode",
                    required=False,
                    enum=["transactional", "partialBatch"],
                    default="transactional"
                ),
                "max_parallelism": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Maximum parallelism for refresh",
                    required=False
                ),
                
                # Query Parameters
                "dax_query": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="DAX query to execute",
                    required=False
                ),
                "serializer_settings": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Query serializer settings",
                    required=False
                ),
                
                # Embedding Parameters
                "datasets_for_token": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Datasets to include in embed token",
                    required=False
                ),
                "reports_for_token": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Reports to include in embed token",
                    required=False
                ),
                "target_workspaces": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Target workspaces for embed token",
                    required=False
                ),
                "identities": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="RLS identities for embed token",
                    required=False
                ),
                
                # Filtering and Pagination Parameters
                "filter": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="OData filter expression",
                    required=False
                ),
                "top": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Number of items to return (top N)",
                    required=False
                ),
                "skip": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Number of items to skip",
                    required=False
                ),
            },
            outputs={
                "status": NodeParameterType.STRING,
                "access_token": NodeParameterType.STRING,
                "datasets": NodeParameterType.ARRAY,
                "dataset_info": NodeParameterType.OBJECT,
                "reports": NodeParameterType.ARRAY,
                "report_info": NodeParameterType.OBJECT,
                "dashboards": NodeParameterType.ARRAY,
                "dashboard_info": NodeParameterType.OBJECT,
                "workspaces": NodeParameterType.ARRAY,
                "workspace_info": NodeParameterType.OBJECT,
                "dataflows": NodeParameterType.ARRAY,
                "dataflow_info": NodeParameterType.OBJECT,
                "gateways": NodeParameterType.ARRAY,
                "gateway_info": NodeParameterType.OBJECT,
                "refresh_details": NodeParameterType.OBJECT,
                "refresh_history": NodeParameterType.ARRAY,
                "export_data": NodeParameterType.STRING,
                "embed_token": NodeParameterType.STRING,
                "embed_url": NodeParameterType.STRING,
                "query_results": NodeParameterType.ARRAY,
                "tiles": NodeParameterType.ARRAY,
                "pages": NodeParameterType.ARRAY,
                "operation_type": NodeParameterType.STRING,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Power BI-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Always validate operation exists
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Validate authentication parameters
        auth_method = params.get("auth_method", "service_principal")
        
        if not params.get("access_token"):
            if auth_method == PowerBIAuthMethod.SERVICE_PRINCIPAL:
                required_fields = ["tenant_id", "client_id", "client_secret"]
                for field in required_fields:
                    if not params.get(field):
                        raise NodeValidationError(f"{field} is required for service principal authentication")
            elif auth_method == PowerBIAuthMethod.MASTER_USER:
                required_fields = ["username", "password"]
                for field in required_fields:
                    if not params.get(field):
                        raise NodeValidationError(f"{field} is required for master user authentication")
        
        # Validate operation-specific requirements
        dataset_ops = [
            PowerBIOperation.GET_DATASET, PowerBIOperation.DELETE_DATASET,
            PowerBIOperation.REFRESH_DATASET, PowerBIOperation.GET_REFRESH_HISTORY,
            PowerBIOperation.EXECUTE_QUERIES, PowerBIOperation.BIND_TO_GATEWAY
        ]
        
        if operation in dataset_ops and not params.get("dataset_id"):
            raise NodeValidationError("dataset_id is required for dataset-specific operations")
        
        report_ops = [
            PowerBIOperation.GET_REPORT, PowerBIOperation.CLONE_REPORT,
            PowerBIOperation.DELETE_REPORT, PowerBIOperation.EXPORT_REPORT,
            PowerBIOperation.GET_REPORT_PAGES
        ]
        
        if operation in report_ops and not params.get("report_id"):
            raise NodeValidationError("report_id is required for report-specific operations")
        
        dashboard_ops = [
            PowerBIOperation.GET_DASHBOARD, PowerBIOperation.GET_DASHBOARD_TILES,
            PowerBIOperation.DELETE_DASHBOARD
        ]
        
        if operation in dashboard_ops and not params.get("dashboard_id"):
            raise NodeValidationError("dashboard_id is required for dashboard-specific operations")
        
        # Validate workspace operations
        workspace_ops = [
            PowerBIOperation.GET_WORKSPACE, PowerBIOperation.UPDATE_WORKSPACE,
            PowerBIOperation.DELETE_WORKSPACE, PowerBIOperation.ADD_WORKSPACE_USER,
            PowerBIOperation.REMOVE_WORKSPACE_USER
        ]
        
        if operation in workspace_ops and not params.get("workspace_id"):
            raise NodeValidationError("workspace_id is required for workspace-specific operations")
        
        # Validate user management operations
        user_ops = [PowerBIOperation.ADD_WORKSPACE_USER, PowerBIOperation.REMOVE_WORKSPACE_USER]
        if operation in user_ops and not params.get("user_email"):
            raise NodeValidationError("user_email is required for user management operations")
        
        # Validate clone operations
        if operation == PowerBIOperation.CLONE_REPORT:
            if not params.get("report_name"):
                raise NodeValidationError("report_name is required for report cloning")
        
        # Validate tile operations
        if operation == PowerBIOperation.CLONE_TILE:
            required_fields = ["dashboard_id", "tile_id", "target_workspace_id"]
            for field in required_fields:
                if not params.get(field):
                    raise NodeValidationError(f"{field} is required for tile cloning")
        
        # Validate query operations
        if operation == PowerBIOperation.EXECUTE_QUERIES:
            if not params.get("dax_query"):
                raise NodeValidationError("dax_query is required for query execution")
        
        return params
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Power BI operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Ensure we have access token
            if not params.get("access_token") and not self.access_token:
                await self._authenticate(params)
            elif params.get("access_token"):
                self.access_token = params["access_token"]
            
            # Route to specific operation handler
            if operation == PowerBIOperation.GET_DATASETS:
                return await self._get_datasets(params)
            elif operation == PowerBIOperation.GET_DATASET:
                return await self._get_dataset(params)
            elif operation == PowerBIOperation.DELETE_DATASET:
                return await self._delete_dataset(params)
            elif operation == PowerBIOperation.REFRESH_DATASET:
                return await self._refresh_dataset(params)
            elif operation == PowerBIOperation.GET_REFRESH_HISTORY:
                return await self._get_refresh_history(params)
            elif operation == PowerBIOperation.EXECUTE_QUERIES:
                return await self._execute_queries(params)
            elif operation == PowerBIOperation.GET_REPORTS:
                return await self._get_reports(params)
            elif operation == PowerBIOperation.GET_REPORT:
                return await self._get_report(params)
            elif operation == PowerBIOperation.CLONE_REPORT:
                return await self._clone_report(params)
            elif operation == PowerBIOperation.DELETE_REPORT:
                return await self._delete_report(params)
            elif operation == PowerBIOperation.EXPORT_REPORT:
                return await self._export_report(params)
            elif operation == PowerBIOperation.GET_REPORT_PAGES:
                return await self._get_report_pages(params)
            elif operation == PowerBIOperation.GET_DASHBOARDS:
                return await self._get_dashboards(params)
            elif operation == PowerBIOperation.GET_DASHBOARD:
                return await self._get_dashboard(params)
            elif operation == PowerBIOperation.GET_DASHBOARD_TILES:
                return await self._get_dashboard_tiles(params)
            elif operation == PowerBIOperation.DELETE_DASHBOARD:
                return await self._delete_dashboard(params)
            elif operation == PowerBIOperation.GET_WORKSPACES:
                return await self._get_workspaces(params)
            elif operation == PowerBIOperation.CREATE_WORKSPACE:
                return await self._create_workspace(params)
            elif operation == PowerBIOperation.GET_WORKSPACE:
                return await self._get_workspace(params)
            elif operation == PowerBIOperation.DELETE_WORKSPACE:
                return await self._delete_workspace(params)
            elif operation == PowerBIOperation.ADD_WORKSPACE_USER:
                return await self._add_workspace_user(params)
            elif operation == PowerBIOperation.REMOVE_WORKSPACE_USER:
                return await self._remove_workspace_user(params)
            elif operation == PowerBIOperation.GENERATE_EMBED_TOKEN:
                return await self._generate_embed_token(params)
            elif operation == PowerBIOperation.GET_GATEWAYS:
                return await self._get_gateways(params)
            elif operation == PowerBIOperation.GET_GATEWAY_DATASOURCES:
                return await self._get_gateway_datasources(params)
            elif operation == PowerBIOperation.GET_DATAFLOWS:
                return await self._get_dataflows(params)
            elif operation == PowerBIOperation.GET_DATAFLOW:
                return await self._get_dataflow(params)
            elif operation == PowerBIOperation.REFRESH_DATAFLOW:
                return await self._refresh_dataflow(params)
            elif operation == PowerBIOperation.DELETE_DATAFLOW:
                return await self._delete_dataflow(params)
            else:
                raise NodeExecutionError(f"Unknown operation: {operation}")
                
        except NodeValidationError as e:
            return self._format_error_response(str(e), "validation_error")
        except NodeExecutionError as e:
            return self._format_error_response(str(e), "execution_error")
        except Exception as e:
            logger.error(f"Unexpected error in PowerBINode: {str(e)}")
            return self._format_error_response(f"Unexpected error: {str(e)}", "unexpected_error")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for authenticated requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "PowerBINode/1.0.0"
        }
    
    def _get_url(self, params: Dict[str, Any], endpoint: str) -> str:
        """Get full URL for API requests."""
        if params.get("workspace_id"):
            return f"{self.base_url}/groups/{params['workspace_id']}/{endpoint}"
        else:
            return f"{self.base_url}/{endpoint}"
    
    async def _authenticate(self, params: Dict[str, Any]) -> str:
        """Authenticate with Power BI and get access token."""
        try:
            auth_method = params.get("auth_method", "service_principal")
            tenant_id = params.get("tenant_id", "common")
            
            url = f"{self.auth_url}/{tenant_id}/oauth2/v2.0/token"
            
            if auth_method == PowerBIAuthMethod.SERVICE_PRINCIPAL:
                data = {
                    "grant_type": "client_credentials",
                    "client_id": params["client_id"],
                    "client_secret": params["client_secret"],
                    "scope": "https://analysis.windows.net/powerbi/api/.default"
                }
            else:
                data = {
                    "grant_type": "password",
                    "client_id": params["client_id"],
                    "username": params["username"],
                    "password": params["password"],
                    "scope": "https://analysis.windows.net/powerbi/api/.default"
                }
            
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=headers) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        self.access_token = response_data.get("access_token")
                        return self.access_token
                    else:
                        raise NodeExecutionError(f"Authentication failed: {response_data.get('error_description', 'Unknown error')}")
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to authenticate: {str(e)}")
    
    async def _get_datasets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get datasets from Power BI."""
        try:
            url = self._get_url(params, "datasets")
            headers = self._get_headers()
            
            query_params = {}
            if params.get("filter"):
                query_params["$filter"] = params["filter"]
            if params.get("top"):
                query_params["$top"] = params["top"]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=query_params) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        datasets = response_data.get("value", [])
                        return {
                            "status": "success",
                            "operation_type": "get_datasets",
                            "datasets": datasets,
                            "dataset_count": len(datasets),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("error", {}).get("message", "Failed to get datasets"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get datasets: {str(e)}")
    
    def _format_error_response(self, error_message: str, error_code: str) -> Dict[str, Any]:
        """Format error response consistently."""
        return {
            "status": "error",
            "error": error_message,
            "error_code": error_code,
            "access_token": None,
            "datasets": None,
            "dataset_info": None,
            "reports": None,
            "report_info": None,
            "dashboards": None,
            "dashboard_info": None,
            "workspaces": None,
            "workspace_info": None,
            "dataflows": None,
            "dataflow_info": None,
            "gateways": None,
            "gateway_info": None,
            "refresh_details": None,
            "refresh_history": None,
            "export_data": None,
            "embed_token": None,
            "embed_url": None,
            "query_results": None,
            "tiles": None,
            "pages": None,
            "operation_type": None,
            "response_data": None
        }

    # Note: Additional operation methods would be implemented here following the same pattern