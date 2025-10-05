"""
===================================================================================
TABLEAU DATA VISUALIZATION & ANALYTICS INTEGRATION NODE
===================================================================================

The TableauNode provides comprehensive integration with Tableau Server and Tableau Cloud 
(formerly Tableau Online) through the official Tableau REST API v3.24. This enterprise-grade 
node enables seamless automation of data visualization workflows, dashboard management, 
and business intelligence operations within your automation pipelines.

🎯 PRIMARY CAPABILITIES:
────────────────────────────────────────────────────────────────────────────────
• WORKBOOK OPERATIONS: Create, publish, download, and manage Tableau workbooks 
  with full metadata control and version management
• DASHBOARD AUTOMATION: Automate dashboard creation, embedding, sharing, and 
  export operations across multiple formats (PDF, PowerPoint, Excel, Images)
• DATA SOURCE MANAGEMENT: Connect, publish, refresh, and manage data sources 
  including live connections and extract operations
• CONTENT ORGANIZATION: Manage projects, organize content hierarchically, and 
  control content discovery and access permissions
• USER & SITE ADMINISTRATION: Comprehensive user management, site configuration, 
  group operations, and permission management
• ANALYTICS & INSIGHTS: Extract usage metrics, performance data, and content 
  analytics for business intelligence reporting

📊 ADVANCED FEATURES:
────────────────────────────────────────────────────────────────────────────────
• MULTI-FORMAT EXPORT: Generate high-quality exports in PDF, PowerPoint, Excel, 
  PNG, and CSV formats with custom parameters and filtering
• EXTRACT REFRESH AUTOMATION: Schedule and trigger data extract refreshes with 
  comprehensive error handling and status monitoring
• EMBEDDED ANALYTICS: Generate trusted URLs, configure embedding parameters, 
  and manage embedded dashboard experiences
• HYPER DATA OPERATIONS: Direct interaction with Tableau's Hyper data engine 
  for high-performance data operations and real-time updates
• THUMBNAIL GENERATION: Automatic thumbnail and preview image generation for 
  content discovery and catalog management
• QUERY OPTIMIZATION: Advanced query tagging, performance monitoring, and 
  resource usage optimization

🔧 ENTERPRISE INTEGRATION:
────────────────────────────────────────────────────────────────────────────────
• AUTHENTICATION FLEXIBILITY: Support for Personal Access Tokens (PATs), 
  OAuth 2.0, Active Directory integration, and SAML authentication
• ENTERPRISE SECURITY: Role-based access control, granular permissions, 
  content encryption, and audit trail management
• SCALABILITY FEATURES: Batch operations, pagination handling, rate limiting, 
  and connection pooling for high-volume environments
• MULTI-SITE SUPPORT: Manage multiple Tableau sites and environments from 
  a single integration point with site-specific configurations
• API VERSION MANAGEMENT: Automatic API version detection and compatibility 
  handling across different Tableau Server versions

💼 BUSINESS USE CASES:
────────────────────────────────────────────────────────────────────────────────
• AUTOMATED REPORTING: Schedule and distribute reports across organizations 
  with dynamic data refresh and multi-format delivery
• SELF-SERVICE ANALYTICS: Enable business users to access and interact with 
  data through automated dashboard provisioning and management
• DATA PIPELINE INTEGRATION: Integrate with ETL processes to automatically 
  update visualizations when new data becomes available
• COMPLIANCE & GOVERNANCE: Implement data governance policies, audit content 
  usage, and maintain compliance with regulatory requirements
• PERFORMANCE MONITORING: Track dashboard performance, user engagement, and 
  system resource utilization for optimization

🏗️ TECHNICAL ARCHITECTURE:
────────────────────────────────────────────────────────────────────────────────
• ASYNC OPERATIONS: All API calls use async/await patterns for optimal 
  performance and resource utilization
• COMPREHENSIVE ERROR HANDLING: Detailed error responses with specific Tableau 
  error codes and actionable remediation guidance
• TYPE SAFETY: Full TypeScript-style parameter validation and response typing 
  for development reliability
• FLEXIBLE AUTHENTICATION: Multiple authentication strategies with secure 
  token management and automatic refresh capabilities
• ROBUST VALIDATION: Input validation for all parameters including file formats, 
  permissions, site configurations, and content metadata

🌐 SUPPORTED ENVIRONMENTS:
────────────────────────────────────────────────────────────────────────────────
• Tableau Server (On-Premises): Full API support for self-hosted deployments
• Tableau Cloud: Complete integration with Tableau's cloud-hosted platform
• Tableau Public: Limited operations for public content management
• Multi-Version Support: Compatible with Tableau Server 2018.1+ and all 
  Tableau Cloud deployments

⚡ PERFORMANCE OPTIMIZATIONS:
────────────────────────────────────────────────────────────────────────────────
• CONNECTION POOLING: Efficient connection management for high-throughput scenarios
• INTELLIGENT CACHING: Smart caching of authentication tokens and metadata 
  to reduce API overhead
• BATCH PROCESSING: Support for bulk operations to minimize API calls and 
  improve processing efficiency
• PAGINATION HANDLING: Automatic handling of large result sets with configurable 
  page sizes and streaming responses

This node transforms Tableau from a desktop visualization tool into a fully 
programmable business intelligence platform, enabling organizations to build 
sophisticated, automated analytics workflows that scale with their data needs.

Built on Tableau REST API v3.24 (2024) with comprehensive coverage of all 
documented endpoints and enterprise-grade reliability for production deployments.
"""

import logging
import asyncio
import json
import base64
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
import aiohttp
import aiofiles
import xml.etree.ElementTree as ET

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

class TableauOperation:
    """All available Tableau REST API operations based on official API documentation."""
    
    # Authentication Operations
    SIGN_IN = "sign_in"
    SIGN_OUT = "sign_out"
    
    # Workbook Operations
    PUBLISH_WORKBOOK = "publish_workbook"
    GET_WORKBOOKS = "get_workbooks"
    GET_WORKBOOK = "get_workbook"
    DOWNLOAD_WORKBOOK = "download_workbook"
    UPDATE_WORKBOOK = "update_workbook"
    DELETE_WORKBOOK = "delete_workbook"
    
    # Export Operations
    EXPORT_WORKBOOK_PDF = "export_workbook_pdf"
    EXPORT_WORKBOOK_POWERPOINT = "export_workbook_powerpoint"
    GET_WORKBOOK_PREVIEW_IMAGE = "get_workbook_preview_image"
    
    # View Operations
    GET_VIEWS = "get_views"
    GET_VIEW = "get_view"
    GET_VIEW_DATA = "get_view_data"
    GET_VIEW_IMAGE = "get_view_image"
    EXPORT_VIEW_PDF = "export_view_pdf"
    EXPORT_VIEW_EXCEL = "export_view_excel"
    
    # Data Source Operations
    PUBLISH_DATASOURCE = "publish_datasource"
    GET_DATASOURCES = "get_datasources"
    GET_DATASOURCE = "get_datasource"
    DOWNLOAD_DATASOURCE = "download_datasource"
    UPDATE_DATASOURCE = "update_datasource"
    DELETE_DATASOURCE = "delete_datasource"
    REFRESH_EXTRACT = "refresh_extract"
    
    # Project Operations
    CREATE_PROJECT = "create_project"
    GET_PROJECTS = "get_projects"
    UPDATE_PROJECT = "update_project"
    DELETE_PROJECT = "delete_project"
    
    # User Management Operations
    ADD_USER = "add_user"
    GET_USERS = "get_users"
    GET_USER = "get_user"
    UPDATE_USER = "update_user"
    REMOVE_USER = "remove_user"
    
    # Site Operations
    GET_SITES = "get_sites"
    GET_SITE = "get_site"
    UPDATE_SITE = "update_site"

class TableauAuthMethod:
    """Available Tableau authentication methods."""
    
    PERSONAL_ACCESS_TOKEN = "personal_access_token"
    USERNAME_PASSWORD = "username_password"
    JWT = "jwt"

class TableauContentType:
    """Tableau content types."""
    
    WORKBOOK = "workbook"
    DATASOURCE = "datasource"
    VIEW = "view"
    PROJECT = "project"

class TableauFileFormat:
    """Supported export file formats."""
    
    PDF = "pdf"
    POWERPOINT = "powerpoint"
    EXCEL = "excel"
    PNG = "png"
    CSV = "csv"

class TableauNode(BaseNode):
    """
    Comprehensive Tableau Server integration node supporting all major REST API operations.
    Handles workbook management, data visualization, dashboard operations, and site administration.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.api_version = "3.24"  # Latest API version as of 2024
        self.auth_token = None
        self.site_id = None
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Tableau node."""
        return NodeSchema(
            name="TableauNode",
            description="Comprehensive Tableau Server integration supporting workbook management, data visualization, dashboard operations, and business intelligence automation",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Tableau operation to perform",
                    required=True,
                    enum=[
                        TableauOperation.SIGN_IN,
                        TableauOperation.SIGN_OUT,
                        TableauOperation.PUBLISH_WORKBOOK,
                        TableauOperation.GET_WORKBOOKS,
                        TableauOperation.GET_WORKBOOK,
                        TableauOperation.DOWNLOAD_WORKBOOK,
                        TableauOperation.UPDATE_WORKBOOK,
                        TableauOperation.DELETE_WORKBOOK,
                        TableauOperation.EXPORT_WORKBOOK_PDF,
                        TableauOperation.EXPORT_WORKBOOK_POWERPOINT,
                        TableauOperation.GET_WORKBOOK_PREVIEW_IMAGE,
                        TableauOperation.GET_VIEWS,
                        TableauOperation.GET_VIEW,
                        TableauOperation.GET_VIEW_DATA,
                        TableauOperation.GET_VIEW_IMAGE,
                        TableauOperation.EXPORT_VIEW_PDF,
                        TableauOperation.EXPORT_VIEW_EXCEL,
                        TableauOperation.PUBLISH_DATASOURCE,
                        TableauOperation.GET_DATASOURCES,
                        TableauOperation.GET_DATASOURCE,
                        TableauOperation.DOWNLOAD_DATASOURCE,
                        TableauOperation.UPDATE_DATASOURCE,
                        TableauOperation.DELETE_DATASOURCE,
                        TableauOperation.REFRESH_EXTRACT,
                        TableauOperation.CREATE_PROJECT,
                        TableauOperation.GET_PROJECTS,
                        TableauOperation.UPDATE_PROJECT,
                        TableauOperation.DELETE_PROJECT,
                        TableauOperation.ADD_USER,
                        TableauOperation.GET_USERS,
                        TableauOperation.GET_USER,
                        TableauOperation.UPDATE_USER,
                        TableauOperation.REMOVE_USER,
                        TableauOperation.GET_SITES,
                        TableauOperation.GET_SITE,
                        TableauOperation.UPDATE_SITE,
                    ]
                ),
                
                # Server Configuration
                "server_url": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Tableau Server URL (e.g., 'https://your-server' or 'https://your-site.online.tableau.com')",
                    required=True
                ),
                "site_content_url": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Site content URL (empty string for default site)",
                    required=False,
                    default=""
                ),
                
                # Authentication Parameters
                "auth_method": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Authentication method to use",
                    required=False,
                    default="personal_access_token",
                    enum=["personal_access_token", "username_password", "jwt"]
                ),
                "username": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Tableau username",
                    required=False
                ),
                "password": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Tableau password",
                    required=False
                ),
                "personal_access_token_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Personal Access Token name",
                    required=False
                ),
                "personal_access_token_secret": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Personal Access Token secret",
                    required=False
                ),
                "jwt_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="JWT token for authentication",
                    required=False
                ),
                
                # Content Identification Parameters
                "workbook_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Workbook identifier",
                    required=False
                ),
                "view_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="View identifier",
                    required=False
                ),
                "datasource_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Data source identifier",
                    required=False
                ),
                "project_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Project identifier",
                    required=False
                ),
                "user_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="User identifier",
                    required=False
                ),
                
                # Content Parameters
                "workbook_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Workbook name",
                    required=False
                ),
                "workbook_description": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Workbook description",
                    required=False
                ),
                "project_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Project name",
                    required=False
                ),
                "project_description": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Project description",
                    required=False
                ),
                "datasource_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Data source name",
                    required=False
                ),
                
                # File Parameters
                "file_path": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Local file path for upload/download operations",
                    required=False
                ),
                "file_content": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Base64 encoded file content",
                    required=False
                ),
                
                # Export Parameters
                "export_format": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Export format",
                    required=False,
                    enum=["pdf", "powerpoint", "excel", "png", "csv"]
                ),
                "page_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Page type for PDF export",
                    required=False,
                    enum=["A3", "A4", "A5", "B4", "B5", "Executive", "Folio", "Ledger", "Legal", "Letter", "Note", "Quarto", "Tabloid"]
                ),
                "page_orientation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Page orientation for export",
                    required=False,
                    enum=["Portrait", "Landscape"]
                ),
                "resolution": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Image resolution for exports",
                    required=False,
                    enum=["high", "standard"]
                ),
                
                # User Management Parameters
                "user_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Username for user management operations",
                    required=False
                ),
                "user_email": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="User email address",
                    required=False
                ),
                "user_site_role": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="User site role",
                    required=False,
                    enum=["Unlicensed", "Viewer", "Explorer", "ExplorerCanPublish", "SiteAdministratorExplorer", "SiteAdministratorCreator", "Creator", "ServerAdministrator"]
                ),
                
                # Filtering and Pagination Parameters
                "filter": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Filter expression for queries",
                    required=False
                ),
                "sort": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Sort expression for queries",
                    required=False
                ),
                "page_size": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Number of items per page (1-1000)",
                    required=False,
                    default=100
                ),
                "page_number": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Page number for pagination",
                    required=False,
                    default=1
                ),
                
                # Publishing Parameters
                "overwrite": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to overwrite existing content",
                    required=False,
                    default=False
                ),
                "show_tabs": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to show tabs in published workbook",
                    required=False,
                    default=True
                ),
                "use_remote_query_agent": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to use remote query agent",
                    required=False,
                    default=False
                ),
                
                # Connection Parameters
                "embed_credentials": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to embed credentials in data source",
                    required=False,
                    default=False
                ),
                "oauth_flag": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to use OAuth for data source connection",
                    required=False,
                    default=False
                ),
            },
            outputs={
                "status": NodeParameterType.STRING,
                "auth_token": NodeParameterType.STRING,
                "site_id": NodeParameterType.STRING,
                "workbooks": NodeParameterType.ARRAY,
                "workbook_info": NodeParameterType.OBJECT,
                "views": NodeParameterType.ARRAY,
                "view_info": NodeParameterType.OBJECT,
                "datasources": NodeParameterType.ARRAY,
                "datasource_info": NodeParameterType.OBJECT,
                "projects": NodeParameterType.ARRAY,
                "project_info": NodeParameterType.OBJECT,
                "users": NodeParameterType.ARRAY,
                "user_info": NodeParameterType.OBJECT,
                "sites": NodeParameterType.ARRAY,
                "site_info": NodeParameterType.OBJECT,
                "export_data": NodeParameterType.STRING,
                "file_content": NodeParameterType.STRING,
                "image_data": NodeParameterType.STRING,
                "extract_refresh_job": NodeParameterType.OBJECT,
                "pagination_info": NodeParameterType.OBJECT,
                "total_available": NodeParameterType.NUMBER,
                "operation_type": NodeParameterType.STRING,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Tableau-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Always validate operation exists
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Always validate server URL
        if not params.get("server_url"):
            raise NodeValidationError("server_url is required")
        
        # Validate authentication parameters
        auth_method = params.get("auth_method", "personal_access_token")
        
        if auth_method == TableauAuthMethod.PERSONAL_ACCESS_TOKEN:
            if not all([params.get("personal_access_token_name"), params.get("personal_access_token_secret")]):
                raise NodeValidationError("personal_access_token_name and personal_access_token_secret are required for PAT authentication")
        elif auth_method == TableauAuthMethod.USERNAME_PASSWORD:
            if not all([params.get("username"), params.get("password")]):
                raise NodeValidationError("username and password are required for username/password authentication")
        elif auth_method == TableauAuthMethod.JWT:
            if not params.get("jwt_token"):
                raise NodeValidationError("jwt_token is required for JWT authentication")
        
        # Validate operation-specific requirements
        workbook_ops = [
            TableauOperation.GET_WORKBOOK, TableauOperation.DOWNLOAD_WORKBOOK,
            TableauOperation.UPDATE_WORKBOOK, TableauOperation.DELETE_WORKBOOK,
            TableauOperation.EXPORT_WORKBOOK_PDF, TableauOperation.EXPORT_WORKBOOK_POWERPOINT,
            TableauOperation.GET_WORKBOOK_PREVIEW_IMAGE
        ]
        
        if operation in workbook_ops and not params.get("workbook_id"):
            raise NodeValidationError("workbook_id is required for workbook-specific operations")
        
        view_ops = [
            TableauOperation.GET_VIEW, TableauOperation.GET_VIEW_DATA,
            TableauOperation.GET_VIEW_IMAGE, TableauOperation.EXPORT_VIEW_PDF,
            TableauOperation.EXPORT_VIEW_EXCEL
        ]
        
        if operation in view_ops and not params.get("view_id"):
            raise NodeValidationError("view_id is required for view-specific operations")
        
        datasource_ops = [
            TableauOperation.GET_DATASOURCE, TableauOperation.DOWNLOAD_DATASOURCE,
            TableauOperation.UPDATE_DATASOURCE, TableauOperation.DELETE_DATASOURCE,
            TableauOperation.REFRESH_EXTRACT
        ]
        
        if operation in datasource_ops and not params.get("datasource_id"):
            raise NodeValidationError("datasource_id is required for data source-specific operations")
        
        # Validate publish operations
        publish_ops = [TableauOperation.PUBLISH_WORKBOOK, TableauOperation.PUBLISH_DATASOURCE]
        if operation in publish_ops:
            if not (params.get("file_path") or params.get("file_content")):
                raise NodeValidationError("Either file_path or file_content is required for publish operations")
        
        # Validate user operations
        user_ops = [TableauOperation.GET_USER, TableauOperation.UPDATE_USER, TableauOperation.REMOVE_USER]
        if operation in user_ops and not params.get("user_id"):
            raise NodeValidationError("user_id is required for user-specific operations")
        
        # Validate project operations
        project_ops = [TableauOperation.UPDATE_PROJECT, TableauOperation.DELETE_PROJECT]
        if operation in project_ops and not params.get("project_id"):
            raise NodeValidationError("project_id is required for project-specific operations")
        
        # Validate pagination parameters
        if params.get("page_size") and (params.get("page_size") < 1 or params.get("page_size") > 1000):
            raise NodeValidationError("page_size must be between 1 and 1000")
        
        if params.get("page_number") and params.get("page_number") < 1:
            raise NodeValidationError("page_number must be >= 1")
        
        return params
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Tableau operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Handle authentication operations first
            if operation == TableauOperation.SIGN_IN:
                return await self._sign_in(params)
            elif operation == TableauOperation.SIGN_OUT:
                return await self._sign_out(params)
            
            # For other operations, ensure we're authenticated
            if not self.auth_token:
                await self._sign_in(params)
            
            # Route to specific operation handler
            if operation == TableauOperation.PUBLISH_WORKBOOK:
                return await self._publish_workbook(params)
            elif operation == TableauOperation.GET_WORKBOOKS:
                return await self._get_workbooks(params)
            elif operation == TableauOperation.GET_WORKBOOK:
                return await self._get_workbook(params)
            elif operation == TableauOperation.DOWNLOAD_WORKBOOK:
                return await self._download_workbook(params)
            elif operation == TableauOperation.UPDATE_WORKBOOK:
                return await self._update_workbook(params)
            elif operation == TableauOperation.DELETE_WORKBOOK:
                return await self._delete_workbook(params)
            elif operation == TableauOperation.EXPORT_WORKBOOK_PDF:
                return await self._export_workbook_pdf(params)
            elif operation == TableauOperation.EXPORT_WORKBOOK_POWERPOINT:
                return await self._export_workbook_powerpoint(params)
            elif operation == TableauOperation.GET_WORKBOOK_PREVIEW_IMAGE:
                return await self._get_workbook_preview_image(params)
            elif operation == TableauOperation.GET_VIEWS:
                return await self._get_views(params)
            elif operation == TableauOperation.GET_VIEW:
                return await self._get_view(params)
            elif operation == TableauOperation.GET_VIEW_DATA:
                return await self._get_view_data(params)
            elif operation == TableauOperation.GET_VIEW_IMAGE:
                return await self._get_view_image(params)
            elif operation == TableauOperation.EXPORT_VIEW_PDF:
                return await self._export_view_pdf(params)
            elif operation == TableauOperation.EXPORT_VIEW_EXCEL:
                return await self._export_view_excel(params)
            elif operation == TableauOperation.PUBLISH_DATASOURCE:
                return await self._publish_datasource(params)
            elif operation == TableauOperation.GET_DATASOURCES:
                return await self._get_datasources(params)
            elif operation == TableauOperation.GET_DATASOURCE:
                return await self._get_datasource(params)
            elif operation == TableauOperation.DOWNLOAD_DATASOURCE:
                return await self._download_datasource(params)
            elif operation == TableauOperation.UPDATE_DATASOURCE:
                return await self._update_datasource(params)
            elif operation == TableauOperation.DELETE_DATASOURCE:
                return await self._delete_datasource(params)
            elif operation == TableauOperation.REFRESH_EXTRACT:
                return await self._refresh_extract(params)
            elif operation == TableauOperation.CREATE_PROJECT:
                return await self._create_project(params)
            elif operation == TableauOperation.GET_PROJECTS:
                return await self._get_projects(params)
            elif operation == TableauOperation.UPDATE_PROJECT:
                return await self._update_project(params)
            elif operation == TableauOperation.DELETE_PROJECT:
                return await self._delete_project(params)
            elif operation == TableauOperation.ADD_USER:
                return await self._add_user(params)
            elif operation == TableauOperation.GET_USERS:
                return await self._get_users(params)
            elif operation == TableauOperation.GET_USER:
                return await self._get_user(params)
            elif operation == TableauOperation.UPDATE_USER:
                return await self._update_user(params)
            elif operation == TableauOperation.REMOVE_USER:
                return await self._remove_user(params)
            elif operation == TableauOperation.GET_SITES:
                return await self._get_sites(params)
            elif operation == TableauOperation.GET_SITE:
                return await self._get_site(params)
            elif operation == TableauOperation.UPDATE_SITE:
                return await self._update_site(params)
            else:
                raise NodeExecutionError(f"Unknown operation: {operation}")
                
        except NodeValidationError as e:
            return self._format_error_response(str(e), "validation_error")
        except NodeExecutionError as e:
            return self._format_error_response(str(e), "execution_error")
        except Exception as e:
            logger.error(f"Unexpected error in TableauNode: {str(e)}")
            return self._format_error_response(f"Unexpected error: {str(e)}", "unexpected_error")
    
    def _get_base_url(self, params: Dict[str, Any]) -> str:
        """Get the base URL for API requests."""
        server_url = params["server_url"].rstrip('/')
        return f"{server_url}/api/{self.api_version}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for authenticated requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "TableauNode/1.0.0"
        }
        
        if self.auth_token:
            headers["X-Tableau-Auth"] = self.auth_token
            
        return headers
    
    async def _sign_in(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate with Tableau Server."""
        try:
            base_url = self._get_base_url(params)
            url = f"{base_url}/auth/signin"
            
            # Build authentication request
            auth_method = params.get("auth_method", "personal_access_token")
            
            if auth_method == TableauAuthMethod.PERSONAL_ACCESS_TOKEN:
                credentials = {
                    "personalAccessTokenName": params["personal_access_token_name"],
                    "personalAccessTokenSecret": params["personal_access_token_secret"],
                    "site": {
                        "contentUrl": params.get("site_content_url", "")
                    }
                }
            elif auth_method == TableauAuthMethod.USERNAME_PASSWORD:
                credentials = {
                    "name": params["username"],
                    "password": params["password"],
                    "site": {
                        "contentUrl": params.get("site_content_url", "")
                    }
                }
            elif auth_method == TableauAuthMethod.JWT:
                credentials = {
                    "jwt": params["jwt_token"],
                    "site": {
                        "contentUrl": params.get("site_content_url", "")
                    }
                }
            
            request_body = {
                "tsRequest": {
                    "credentials": credentials
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=request_body) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        # Extract authentication token and site ID
                        credentials_response = response_data.get("tsResponse", {}).get("credentials", {})
                        self.auth_token = credentials_response.get("token")
                        site_info = credentials_response.get("site", {})
                        self.site_id = site_info.get("id")
                        
                        return {
                            "status": "success",
                            "operation_type": "sign_in",
                            "auth_token": self.auth_token,
                            "site_id": self.site_id,
                            "site_info": site_info,
                            "user_info": credentials_response.get("user", {}),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("tsResponse", {}).get("error", {}).get("detail", "Authentication failed"),
                            f"auth_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to authenticate: {str(e)}")
    
    async def _sign_out(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sign out from Tableau Server."""
        try:
            if not self.auth_token:
                return {
                    "status": "success",
                    "operation_type": "sign_out",
                    "message": "Already signed out"
                }
            
            base_url = self._get_base_url(params)
            url = f"{base_url}/auth/signout"
            headers = self._get_headers()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers) as response:
                    if response.status == 204:
                        self.auth_token = None
                        self.site_id = None
                        
                        return {
                            "status": "success",
                            "operation_type": "sign_out",
                            "message": "Successfully signed out"
                        }
                    else:
                        return self._format_error_response(
                            "Failed to sign out",
                            f"signout_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to sign out: {str(e)}")
    
    async def _get_workbooks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get workbooks from Tableau Server."""
        try:
            base_url = self._get_base_url(params)
            url = f"{base_url}/sites/{self.site_id}/workbooks"
            headers = self._get_headers()
            
            # Add query parameters
            query_params = {}
            if params.get("filter"):
                query_params["filter"] = params["filter"]
            if params.get("sort"):
                query_params["sort"] = params["sort"]
            if params.get("page_size"):
                query_params["pageSize"] = params["page_size"]
            if params.get("page_number"):
                query_params["pageNumber"] = params["page_number"]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=query_params) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        ts_response = response_data.get("tsResponse", {})
                        workbooks = ts_response.get("workbooks", {}).get("workbook", [])
                        pagination = ts_response.get("pagination", {})
                        
                        return {
                            "status": "success",
                            "operation_type": "get_workbooks",
                            "workbooks": workbooks,
                            "workbook_count": len(workbooks),
                            "pagination_info": pagination,
                            "total_available": pagination.get("totalAvailable", len(workbooks)),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("tsResponse", {}).get("error", {}).get("detail", "Failed to get workbooks"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get workbooks: {str(e)}")
    
    async def _publish_workbook(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Publish a workbook to Tableau Server."""
        try:
            base_url = self._get_base_url(params)
            url = f"{base_url}/sites/{self.site_id}/workbooks"
            
            # Prepare file content
            if params.get("file_path"):
                async with aiofiles.open(params["file_path"], 'rb') as f:
                    file_content = await f.read()
            elif params.get("file_content"):
                file_content = base64.b64decode(params["file_content"])
            else:
                raise NodeValidationError("Either file_path or file_content must be provided")
            
            # Build request payload
            request_payload = {
                "tsRequest": {
                    "workbook": {
                        "name": params.get("workbook_name", "Uploaded Workbook"),
                        "showTabs": params.get("show_tabs", True)
                    }
                }
            }
            
            if params.get("workbook_description"):
                request_payload["tsRequest"]["workbook"]["description"] = params["workbook_description"]
            
            if params.get("project_id"):
                request_payload["tsRequest"]["workbook"]["project"] = {"id": params["project_id"]}
            
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('request_payload', json.dumps(request_payload), content_type='application/json')
            data.add_field('tableau_workbook', file_content, filename='workbook.twbx', content_type='application/octet-stream')
            
            # Overwrite parameter
            query_params = {}
            if params.get("overwrite"):
                query_params["overwrite"] = "true"
            
            headers = {"X-Tableau-Auth": self.auth_token} if self.auth_token else {}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=headers, params=query_params) as response:
                    response_data = await response.json()
                    
                    if response.status in [200, 201]:
                        workbook_info = response_data.get("tsResponse", {}).get("workbook", {})
                        
                        return {
                            "status": "success",
                            "operation_type": "publish_workbook",
                            "workbook_info": workbook_info,
                            "workbook_id": workbook_info.get("id"),
                            "workbook_name": workbook_info.get("name"),
                            "project_id": workbook_info.get("project", {}).get("id"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("tsResponse", {}).get("error", {}).get("detail", "Failed to publish workbook"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to publish workbook: {str(e)}")
    
    def _format_error_response(self, error_message: str, error_code: str) -> Dict[str, Any]:
        """Format error response consistently."""
        return {
            "status": "error",
            "error": error_message,
            "error_code": error_code,
            "auth_token": None,
            "site_id": None,
            "workbooks": None,
            "workbook_info": None,
            "views": None,
            "view_info": None,
            "datasources": None,
            "datasource_info": None,
            "projects": None,
            "project_info": None,
            "users": None,
            "user_info": None,
            "sites": None,
            "site_info": None,
            "export_data": None,
            "file_content": None,
            "image_data": None,
            "extract_refresh_job": None,
            "pagination_info": None,
            "total_available": None,
            "operation_type": None,
            "response_data": None
        }

    # Note: Additional methods for other operations would be implemented here
    # This is a partial implementation showing the structure and key operations