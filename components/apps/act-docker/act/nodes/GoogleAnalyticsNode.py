"""
Google Analytics Node - Comprehensive integration with Google Analytics Data API v1 (GA4)
Provides access to all Google Analytics 4 API operations including reports, audiences, events, conversions, and real-time data.
"""

import logging
import json
import asyncio
import time
import os
import ssl
import base64
import hashlib
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

class GoogleAnalyticsOperation:
    """Operations available on Google Analytics Data API v1."""
    
    # Authentication
    GET_ACCESS_TOKEN = "get_access_token"
    
    # Reporting Operations
    RUN_REPORT = "run_report"
    RUN_PIVOT_REPORT = "run_pivot_report"
    BATCH_RUN_REPORTS = "batch_run_reports"
    BATCH_RUN_PIVOT_REPORTS = "batch_run_pivot_reports"
    
    # Real-time Operations
    RUN_REALTIME_REPORT = "run_realtime_report"
    
    # Funnel Operations
    RUN_FUNNEL_REPORT = "run_funnel_report"
    
    # Cohort Operations
    RUN_COHORT_REPORT = "run_cohort_report"
    
    # Metadata Operations
    GET_METADATA = "get_metadata"
    
    # Audience Operations
    LIST_AUDIENCES = "list_audiences"
    GET_AUDIENCE = "get_audience"
    CREATE_AUDIENCE = "create_audience"
    UPDATE_AUDIENCE = "update_audience"
    DELETE_AUDIENCE = "delete_audience"
    
    # Custom Dimensions Operations
    LIST_CUSTOM_DIMENSIONS = "list_custom_dimensions"
    GET_CUSTOM_DIMENSION = "get_custom_dimension"
    CREATE_CUSTOM_DIMENSION = "create_custom_dimension"
    UPDATE_CUSTOM_DIMENSION = "update_custom_dimension"
    DELETE_CUSTOM_DIMENSION = "delete_custom_dimension"
    ARCHIVE_CUSTOM_DIMENSION = "archive_custom_dimension"
    
    # Custom Metrics Operations
    LIST_CUSTOM_METRICS = "list_custom_metrics"
    GET_CUSTOM_METRIC = "get_custom_metric"
    CREATE_CUSTOM_METRIC = "create_custom_metric"
    UPDATE_CUSTOM_METRIC = "update_custom_metric"
    DELETE_CUSTOM_METRIC = "delete_custom_metric"
    ARCHIVE_CUSTOM_METRIC = "archive_custom_metric"
    
    # Conversion Events Operations
    LIST_CONVERSION_EVENTS = "list_conversion_events"
    GET_CONVERSION_EVENT = "get_conversion_event"
    CREATE_CONVERSION_EVENT = "create_conversion_event"
    UPDATE_CONVERSION_EVENT = "update_conversion_event"
    DELETE_CONVERSION_EVENT = "delete_conversion_event"
    
    # Data Streams Operations
    LIST_DATA_STREAMS = "list_data_streams"
    GET_DATA_STREAM = "get_data_stream"
    CREATE_DATA_STREAM = "create_data_stream"
    UPDATE_DATA_STREAM = "update_data_stream"
    DELETE_DATA_STREAM = "delete_data_stream"
    
    # Google Ads Links Operations
    LIST_GOOGLE_ADS_LINKS = "list_google_ads_links"
    GET_GOOGLE_ADS_LINK = "get_google_ads_link"
    CREATE_GOOGLE_ADS_LINK = "create_google_ads_link"
    UPDATE_GOOGLE_ADS_LINK = "update_google_ads_link"
    DELETE_GOOGLE_ADS_LINK = "delete_google_ads_link"
    
    # Attribution Settings Operations
    GET_ATTRIBUTION_SETTINGS = "get_attribution_settings"
    UPDATE_ATTRIBUTION_SETTINGS = "update_attribution_settings"
    
    # Data Retention Settings Operations
    GET_DATA_RETENTION_SETTINGS = "get_data_retention_settings"
    UPDATE_DATA_RETENTION_SETTINGS = "update_data_retention_settings"
    
    # Enhanced Measurement Settings Operations
    GET_ENHANCED_MEASUREMENT_SETTINGS = "get_enhanced_measurement_settings"
    UPDATE_ENHANCED_MEASUREMENT_SETTINGS = "update_enhanced_measurement_settings"
    
    # Firebase Links Operations
    LIST_FIREBASE_LINKS = "list_firebase_links"
    GET_FIREBASE_LINK = "get_firebase_link"
    CREATE_FIREBASE_LINK = "create_firebase_link"
    UPDATE_FIREBASE_LINK = "update_firebase_link"
    DELETE_FIREBASE_LINK = "delete_firebase_link"

class GoogleAnalyticsNode(BaseNode):
    """
    Node for interacting with Google Analytics Data API v1 (GA4).
    Provides comprehensive functionality for reports, audiences, events, conversions, and real-time data.
    """
    
    DATA_API_BASE_URL = "https://analyticsdata.googleapis.com/v1beta"
    ADMIN_API_BASE_URL = "https://analyticsadmin.googleapis.com/v1beta"
    AUTH_URL = "https://oauth2.googleapis.com/token"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        self.access_token = None
        self.token_expires_at = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Google Analytics node."""
        return NodeSchema(
            node_type="google_analytics",
            version="1.0.0",
            description="Comprehensive integration with Google Analytics Data API v1 (GA4) for reports, audiences, events, conversions, and real-time data",
            parameters=[
                # Authentication
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Google Analytics API",
                    required=True,
                    enum=[
                        # Authentication
                        GoogleAnalyticsOperation.GET_ACCESS_TOKEN,
                        
                        # Reporting
                        GoogleAnalyticsOperation.RUN_REPORT,
                        GoogleAnalyticsOperation.RUN_PIVOT_REPORT,
                        GoogleAnalyticsOperation.BATCH_RUN_REPORTS,
                        GoogleAnalyticsOperation.BATCH_RUN_PIVOT_REPORTS,
                        
                        # Real-time
                        GoogleAnalyticsOperation.RUN_REALTIME_REPORT,
                        
                        # Funnel
                        GoogleAnalyticsOperation.RUN_FUNNEL_REPORT,
                        
                        # Cohort
                        GoogleAnalyticsOperation.RUN_COHORT_REPORT,
                        
                        # Metadata
                        GoogleAnalyticsOperation.GET_METADATA,
                        
                        # Audiences
                        GoogleAnalyticsOperation.LIST_AUDIENCES,
                        GoogleAnalyticsOperation.GET_AUDIENCE,
                        GoogleAnalyticsOperation.CREATE_AUDIENCE,
                        GoogleAnalyticsOperation.UPDATE_AUDIENCE,
                        GoogleAnalyticsOperation.DELETE_AUDIENCE,
                        
                        # Custom Dimensions
                        GoogleAnalyticsOperation.LIST_CUSTOM_DIMENSIONS,
                        GoogleAnalyticsOperation.GET_CUSTOM_DIMENSION,
                        GoogleAnalyticsOperation.CREATE_CUSTOM_DIMENSION,
                        GoogleAnalyticsOperation.UPDATE_CUSTOM_DIMENSION,
                        GoogleAnalyticsOperation.DELETE_CUSTOM_DIMENSION,
                        GoogleAnalyticsOperation.ARCHIVE_CUSTOM_DIMENSION,
                        
                        # Custom Metrics
                        GoogleAnalyticsOperation.LIST_CUSTOM_METRICS,
                        GoogleAnalyticsOperation.GET_CUSTOM_METRIC,
                        GoogleAnalyticsOperation.CREATE_CUSTOM_METRIC,
                        GoogleAnalyticsOperation.UPDATE_CUSTOM_METRIC,
                        GoogleAnalyticsOperation.DELETE_CUSTOM_METRIC,
                        GoogleAnalyticsOperation.ARCHIVE_CUSTOM_METRIC,
                        
                        # Conversion Events
                        GoogleAnalyticsOperation.LIST_CONVERSION_EVENTS,
                        GoogleAnalyticsOperation.GET_CONVERSION_EVENT,
                        GoogleAnalyticsOperation.CREATE_CONVERSION_EVENT,
                        GoogleAnalyticsOperation.UPDATE_CONVERSION_EVENT,
                        GoogleAnalyticsOperation.DELETE_CONVERSION_EVENT,
                        
                        # Data Streams
                        GoogleAnalyticsOperation.LIST_DATA_STREAMS,
                        GoogleAnalyticsOperation.GET_DATA_STREAM,
                        GoogleAnalyticsOperation.CREATE_DATA_STREAM,
                        GoogleAnalyticsOperation.UPDATE_DATA_STREAM,
                        GoogleAnalyticsOperation.DELETE_DATA_STREAM,
                        
                        # Google Ads Links
                        GoogleAnalyticsOperation.LIST_GOOGLE_ADS_LINKS,
                        GoogleAnalyticsOperation.GET_GOOGLE_ADS_LINK,
                        GoogleAnalyticsOperation.CREATE_GOOGLE_ADS_LINK,
                        GoogleAnalyticsOperation.UPDATE_GOOGLE_ADS_LINK,
                        GoogleAnalyticsOperation.DELETE_GOOGLE_ADS_LINK,
                        
                        # Attribution Settings
                        GoogleAnalyticsOperation.GET_ATTRIBUTION_SETTINGS,
                        GoogleAnalyticsOperation.UPDATE_ATTRIBUTION_SETTINGS,
                        
                        # Data Retention Settings
                        GoogleAnalyticsOperation.GET_DATA_RETENTION_SETTINGS,
                        GoogleAnalyticsOperation.UPDATE_DATA_RETENTION_SETTINGS,
                        
                        # Enhanced Measurement Settings
                        GoogleAnalyticsOperation.GET_ENHANCED_MEASUREMENT_SETTINGS,
                        GoogleAnalyticsOperation.UPDATE_ENHANCED_MEASUREMENT_SETTINGS,
                        
                        # Firebase Links
                        GoogleAnalyticsOperation.LIST_FIREBASE_LINKS,
                        GoogleAnalyticsOperation.GET_FIREBASE_LINK,
                        GoogleAnalyticsOperation.CREATE_FIREBASE_LINK,
                        GoogleAnalyticsOperation.UPDATE_FIREBASE_LINK,
                        GoogleAnalyticsOperation.DELETE_FIREBASE_LINK
                    ]
                ),
                NodeParameter(
                    name="service_account_key",
                    type=NodeParameterType.SECRET,
                    description="Google Service Account Key JSON for authentication",
                    required=False
                ),
                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 Access Token for authentication",
                    required=False
                ),
                NodeParameter(
                    name="refresh_token",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 Refresh Token for token renewal",
                    required=False
                ),
                NodeParameter(
                    name="client_id",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 Client ID",
                    required=False
                ),
                NodeParameter(
                    name="client_secret",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 Client Secret",
                    required=False
                ),
                
                # Common parameters
                NodeParameter(
                    name="property_id",
                    type=NodeParameterType.STRING,
                    description="Google Analytics 4 Property ID",
                    required=True
                ),
                NodeParameter(
                    name="data_stream_id",
                    type=NodeParameterType.STRING,
                    description="Data stream ID for stream operations",
                    required=False
                ),
                NodeParameter(
                    name="audience_id",
                    type=NodeParameterType.STRING,
                    description="Audience ID for audience operations",
                    required=False
                ),
                NodeParameter(
                    name="custom_dimension_id",
                    type=NodeParameterType.STRING,
                    description="Custom dimension ID for custom dimension operations",
                    required=False
                ),
                NodeParameter(
                    name="custom_metric_id",
                    type=NodeParameterType.STRING,
                    description="Custom metric ID for custom metric operations",
                    required=False
                ),
                NodeParameter(
                    name="conversion_event_id",
                    type=NodeParameterType.STRING,
                    description="Conversion event ID for conversion event operations",
                    required=False
                ),
                NodeParameter(
                    name="google_ads_link_id",
                    type=NodeParameterType.STRING,
                    description="Google Ads link ID for Google Ads link operations",
                    required=False
                ),
                NodeParameter(
                    name="firebase_link_id",
                    type=NodeParameterType.STRING,
                    description="Firebase link ID for Firebase link operations",
                    required=False
                ),
                
                # Report parameters
                NodeParameter(
                    name="date_ranges",
                    type=NodeParameterType.ARRAY,
                    description="Date ranges for reports",
                    required=False
                ),
                NodeParameter(
                    name="dimensions",
                    type=NodeParameterType.ARRAY,
                    description="Dimensions for reports",
                    required=False
                ),
                NodeParameter(
                    name="metrics",
                    type=NodeParameterType.ARRAY,
                    description="Metrics for reports",
                    required=False
                ),
                NodeParameter(
                    name="dimension_filter",
                    type=NodeParameterType.OBJECT,
                    description="Dimension filter for reports",
                    required=False
                ),
                NodeParameter(
                    name="metric_filter",
                    type=NodeParameterType.OBJECT,
                    description="Metric filter for reports",
                    required=False
                ),
                NodeParameter(
                    name="order_bys",
                    type=NodeParameterType.ARRAY,
                    description="Order by clauses for reports",
                    required=False
                ),
                NodeParameter(
                    name="currency_code",
                    type=NodeParameterType.STRING,
                    description="Currency code for reports",
                    required=False,
                    default="USD"
                ),
                NodeParameter(
                    name="cohort_spec",
                    type=NodeParameterType.OBJECT,
                    description="Cohort specification for cohort reports",
                    required=False
                ),
                
                # Real-time parameters
                NodeParameter(
                    name="minute_ranges",
                    type=NodeParameterType.ARRAY,
                    description="Minute ranges for real-time reports",
                    required=False
                ),
                
                # Funnel parameters
                NodeParameter(
                    name="funnel",
                    type=NodeParameterType.OBJECT,
                    description="Funnel definition for funnel reports",
                    required=False
                ),
                
                # Request body parameters
                NodeParameter(
                    name="request_body",
                    type=NodeParameterType.OBJECT,
                    description="Request body for create/update operations",
                    required=False
                ),
                
                # Pagination parameters
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Number of rows to return",
                    required=False,
                    default=10000,
                    min_value=1,
                    max_value=100000
                ),
                NodeParameter(
                    name="offset",
                    type=NodeParameterType.NUMBER,
                    description="Number of rows to skip",
                    required=False,
                    default=0,
                    min_value=0
                ),
                NodeParameter(
                    name="page_size",
                    type=NodeParameterType.NUMBER,
                    description="Page size for paginated requests",
                    required=False,
                    default=50,
                    min_value=1,
                    max_value=200
                ),
                NodeParameter(
                    name="page_token",
                    type=NodeParameterType.STRING,
                    description="Page token for paginated requests",
                    required=False
                ),
                
                # Options
                NodeParameter(
                    name="keep_empty_rows",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to keep empty rows in reports",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="return_property_quota",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to return property quota information",
                    required=False,
                    default=False
                ),
                
                # Additional filters
                NodeParameter(
                    name="show_all_dimensions",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to show all dimensions in metadata",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="show_all_metrics",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to show all metrics in metadata",
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
                "rows": NodeParameterType.ARRAY,
                "row_count": NodeParameterType.NUMBER,
                "metadata": NodeParameterType.OBJECT,
                "property_quota": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["google", "analytics", "ga4", "reports", "data", "api", "integration"],
            author="System",
            documentation_url="https://developers.google.com/analytics/devguides/reporting/data/v1"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Check for authentication
        has_service_account = params.get("service_account_key")
        has_oauth = params.get("access_token") or (params.get("refresh_token") and params.get("client_id") and params.get("client_secret"))
        
        if not has_service_account and not has_oauth:
            raise NodeValidationError("Either service account key or OAuth credentials (access_token or refresh_token + client_id + client_secret) are required")
        
        # Check for property ID (required for most operations)
        if operation != GoogleAnalyticsOperation.GET_ACCESS_TOKEN:
            if not params.get("property_id"):
                raise NodeValidationError("Property ID is required for Google Analytics operations")
        
        # Validate based on operation
        report_operations = [
            GoogleAnalyticsOperation.RUN_REPORT, GoogleAnalyticsOperation.RUN_PIVOT_REPORT,
            GoogleAnalyticsOperation.BATCH_RUN_REPORTS, GoogleAnalyticsOperation.BATCH_RUN_PIVOT_REPORTS,
            GoogleAnalyticsOperation.RUN_REALTIME_REPORT, GoogleAnalyticsOperation.RUN_FUNNEL_REPORT,
            GoogleAnalyticsOperation.RUN_COHORT_REPORT
        ]
        
        if operation in report_operations:
            if not params.get("metrics") and not params.get("request_body"):
                raise NodeValidationError("Metrics are required for report operations")
        
        # Specific operation validations
        audience_operations = [
            GoogleAnalyticsOperation.GET_AUDIENCE, GoogleAnalyticsOperation.UPDATE_AUDIENCE,
            GoogleAnalyticsOperation.DELETE_AUDIENCE
        ]
        if operation in audience_operations:
            if not params.get("audience_id"):
                raise NodeValidationError("Audience ID is required for audience operations")
        
        custom_dimension_operations = [
            GoogleAnalyticsOperation.GET_CUSTOM_DIMENSION, GoogleAnalyticsOperation.UPDATE_CUSTOM_DIMENSION,
            GoogleAnalyticsOperation.DELETE_CUSTOM_DIMENSION, GoogleAnalyticsOperation.ARCHIVE_CUSTOM_DIMENSION
        ]
        if operation in custom_dimension_operations:
            if not params.get("custom_dimension_id"):
                raise NodeValidationError("Custom dimension ID is required for custom dimension operations")
        
        custom_metric_operations = [
            GoogleAnalyticsOperation.GET_CUSTOM_METRIC, GoogleAnalyticsOperation.UPDATE_CUSTOM_METRIC,
            GoogleAnalyticsOperation.DELETE_CUSTOM_METRIC, GoogleAnalyticsOperation.ARCHIVE_CUSTOM_METRIC
        ]
        if operation in custom_metric_operations:
            if not params.get("custom_metric_id"):
                raise NodeValidationError("Custom metric ID is required for custom metric operations")
        
        conversion_event_operations = [
            GoogleAnalyticsOperation.GET_CONVERSION_EVENT, GoogleAnalyticsOperation.UPDATE_CONVERSION_EVENT,
            GoogleAnalyticsOperation.DELETE_CONVERSION_EVENT
        ]
        if operation in conversion_event_operations:
            if not params.get("conversion_event_id"):
                raise NodeValidationError("Conversion event ID is required for conversion event operations")
        
        data_stream_operations = [
            GoogleAnalyticsOperation.GET_DATA_STREAM, GoogleAnalyticsOperation.UPDATE_DATA_STREAM,
            GoogleAnalyticsOperation.DELETE_DATA_STREAM
        ]
        if operation in data_stream_operations:
            if not params.get("data_stream_id"):
                raise NodeValidationError("Data stream ID is required for data stream operations")
        
        google_ads_link_operations = [
            GoogleAnalyticsOperation.GET_GOOGLE_ADS_LINK, GoogleAnalyticsOperation.UPDATE_GOOGLE_ADS_LINK,
            GoogleAnalyticsOperation.DELETE_GOOGLE_ADS_LINK
        ]
        if operation in google_ads_link_operations:
            if not params.get("google_ads_link_id"):
                raise NodeValidationError("Google Ads link ID is required for Google Ads link operations")
        
        firebase_link_operations = [
            GoogleAnalyticsOperation.GET_FIREBASE_LINK, GoogleAnalyticsOperation.UPDATE_FIREBASE_LINK,
            GoogleAnalyticsOperation.DELETE_FIREBASE_LINK
        ]
        if operation in firebase_link_operations:
            if not params.get("firebase_link_id"):
                raise NodeValidationError("Firebase link ID is required for Firebase link operations")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Google Analytics node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Get access token if needed
            if operation != GoogleAnalyticsOperation.GET_ACCESS_TOKEN:
                await self._ensure_access_token(validated_data)
            
            # Execute the appropriate operation
            if operation == GoogleAnalyticsOperation.GET_ACCESS_TOKEN:
                return await self._operation_get_access_token(validated_data)
            elif operation == GoogleAnalyticsOperation.RUN_REPORT:
                return await self._operation_run_report(validated_data)
            elif operation == GoogleAnalyticsOperation.RUN_PIVOT_REPORT:
                return await self._operation_run_pivot_report(validated_data)
            elif operation == GoogleAnalyticsOperation.BATCH_RUN_REPORTS:
                return await self._operation_batch_run_reports(validated_data)
            elif operation == GoogleAnalyticsOperation.BATCH_RUN_PIVOT_REPORTS:
                return await self._operation_batch_run_pivot_reports(validated_data)
            elif operation == GoogleAnalyticsOperation.RUN_REALTIME_REPORT:
                return await self._operation_run_realtime_report(validated_data)
            elif operation == GoogleAnalyticsOperation.RUN_FUNNEL_REPORT:
                return await self._operation_run_funnel_report(validated_data)
            elif operation == GoogleAnalyticsOperation.RUN_COHORT_REPORT:
                return await self._operation_run_cohort_report(validated_data)
            elif operation == GoogleAnalyticsOperation.GET_METADATA:
                return await self._operation_get_metadata(validated_data)
            elif operation == GoogleAnalyticsOperation.LIST_AUDIENCES:
                return await self._operation_list_audiences(validated_data)
            elif operation == GoogleAnalyticsOperation.GET_AUDIENCE:
                return await self._operation_get_audience(validated_data)
            elif operation == GoogleAnalyticsOperation.CREATE_AUDIENCE:
                return await self._operation_create_audience(validated_data)
            elif operation == GoogleAnalyticsOperation.UPDATE_AUDIENCE:
                return await self._operation_update_audience(validated_data)
            elif operation == GoogleAnalyticsOperation.DELETE_AUDIENCE:
                return await self._operation_delete_audience(validated_data)
            elif operation == GoogleAnalyticsOperation.LIST_CUSTOM_DIMENSIONS:
                return await self._operation_list_custom_dimensions(validated_data)
            elif operation == GoogleAnalyticsOperation.GET_CUSTOM_DIMENSION:
                return await self._operation_get_custom_dimension(validated_data)
            elif operation == GoogleAnalyticsOperation.CREATE_CUSTOM_DIMENSION:
                return await self._operation_create_custom_dimension(validated_data)
            elif operation == GoogleAnalyticsOperation.UPDATE_CUSTOM_DIMENSION:
                return await self._operation_update_custom_dimension(validated_data)
            elif operation == GoogleAnalyticsOperation.DELETE_CUSTOM_DIMENSION:
                return await self._operation_delete_custom_dimension(validated_data)
            elif operation == GoogleAnalyticsOperation.ARCHIVE_CUSTOM_DIMENSION:
                return await self._operation_archive_custom_dimension(validated_data)
            elif operation == GoogleAnalyticsOperation.LIST_CUSTOM_METRICS:
                return await self._operation_list_custom_metrics(validated_data)
            elif operation == GoogleAnalyticsOperation.GET_CUSTOM_METRIC:
                return await self._operation_get_custom_metric(validated_data)
            elif operation == GoogleAnalyticsOperation.CREATE_CUSTOM_METRIC:
                return await self._operation_create_custom_metric(validated_data)
            elif operation == GoogleAnalyticsOperation.UPDATE_CUSTOM_METRIC:
                return await self._operation_update_custom_metric(validated_data)
            elif operation == GoogleAnalyticsOperation.DELETE_CUSTOM_METRIC:
                return await self._operation_delete_custom_metric(validated_data)
            elif operation == GoogleAnalyticsOperation.ARCHIVE_CUSTOM_METRIC:
                return await self._operation_archive_custom_metric(validated_data)
            elif operation == GoogleAnalyticsOperation.LIST_CONVERSION_EVENTS:
                return await self._operation_list_conversion_events(validated_data)
            elif operation == GoogleAnalyticsOperation.GET_CONVERSION_EVENT:
                return await self._operation_get_conversion_event(validated_data)
            elif operation == GoogleAnalyticsOperation.CREATE_CONVERSION_EVENT:
                return await self._operation_create_conversion_event(validated_data)
            elif operation == GoogleAnalyticsOperation.UPDATE_CONVERSION_EVENT:
                return await self._operation_update_conversion_event(validated_data)
            elif operation == GoogleAnalyticsOperation.DELETE_CONVERSION_EVENT:
                return await self._operation_delete_conversion_event(validated_data)
            elif operation == GoogleAnalyticsOperation.LIST_DATA_STREAMS:
                return await self._operation_list_data_streams(validated_data)
            elif operation == GoogleAnalyticsOperation.GET_DATA_STREAM:
                return await self._operation_get_data_stream(validated_data)
            elif operation == GoogleAnalyticsOperation.CREATE_DATA_STREAM:
                return await self._operation_create_data_stream(validated_data)
            elif operation == GoogleAnalyticsOperation.UPDATE_DATA_STREAM:
                return await self._operation_update_data_stream(validated_data)
            elif operation == GoogleAnalyticsOperation.DELETE_DATA_STREAM:
                return await self._operation_delete_data_stream(validated_data)
            elif operation == GoogleAnalyticsOperation.LIST_GOOGLE_ADS_LINKS:
                return await self._operation_list_google_ads_links(validated_data)
            elif operation == GoogleAnalyticsOperation.GET_GOOGLE_ADS_LINK:
                return await self._operation_get_google_ads_link(validated_data)
            elif operation == GoogleAnalyticsOperation.CREATE_GOOGLE_ADS_LINK:
                return await self._operation_create_google_ads_link(validated_data)
            elif operation == GoogleAnalyticsOperation.UPDATE_GOOGLE_ADS_LINK:
                return await self._operation_update_google_ads_link(validated_data)
            elif operation == GoogleAnalyticsOperation.DELETE_GOOGLE_ADS_LINK:
                return await self._operation_delete_google_ads_link(validated_data)
            elif operation == GoogleAnalyticsOperation.GET_ATTRIBUTION_SETTINGS:
                return await self._operation_get_attribution_settings(validated_data)
            elif operation == GoogleAnalyticsOperation.UPDATE_ATTRIBUTION_SETTINGS:
                return await self._operation_update_attribution_settings(validated_data)
            elif operation == GoogleAnalyticsOperation.GET_DATA_RETENTION_SETTINGS:
                return await self._operation_get_data_retention_settings(validated_data)
            elif operation == GoogleAnalyticsOperation.UPDATE_DATA_RETENTION_SETTINGS:
                return await self._operation_update_data_retention_settings(validated_data)
            elif operation == GoogleAnalyticsOperation.GET_ENHANCED_MEASUREMENT_SETTINGS:
                return await self._operation_get_enhanced_measurement_settings(validated_data)
            elif operation == GoogleAnalyticsOperation.UPDATE_ENHANCED_MEASUREMENT_SETTINGS:
                return await self._operation_update_enhanced_measurement_settings(validated_data)
            elif operation == GoogleAnalyticsOperation.LIST_FIREBASE_LINKS:
                return await self._operation_list_firebase_links(validated_data)
            elif operation == GoogleAnalyticsOperation.GET_FIREBASE_LINK:
                return await self._operation_get_firebase_link(validated_data)
            elif operation == GoogleAnalyticsOperation.CREATE_FIREBASE_LINK:
                return await self._operation_create_firebase_link(validated_data)
            elif operation == GoogleAnalyticsOperation.UPDATE_FIREBASE_LINK:
                return await self._operation_update_firebase_link(validated_data)
            elif operation == GoogleAnalyticsOperation.DELETE_FIREBASE_LINK:
                return await self._operation_delete_firebase_link(validated_data)
            else:
                error_message = f"Unknown operation: {operation}"
                logger.error(error_message)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_message,
                    "id": None,
                    "status_code": None,
                    "response_headers": None,
                    "access_token": None,
                    "token_type": None,
                    "expires_in": None,
                    "rows": None,
                    "row_count": None,
                    "metadata": None,
                    "property_quota": None
                }
                
        except Exception as e:
            error_message = f"Error in Google Analytics node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "id": None,
                "status_code": None,
                "response_headers": None,
                "access_token": None,
                "token_type": None,
                "expires_in": None,
                "rows": None,
                "row_count": None,
                "metadata": None,
                "property_quota": None
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
    
    def _get_data_api_base_url(self) -> str:
        """Get the base URL for Google Analytics Data API."""
        return self.DATA_API_BASE_URL
    
    def _get_admin_api_base_url(self) -> str:
        """Get the base URL for Google Analytics Admin API."""
        return self.ADMIN_API_BASE_URL
    
    async def _ensure_access_token(self, params: Dict[str, Any]):
        """Ensure we have a valid access token."""
        if not self.access_token or (self.token_expires_at and time.time() >= self.token_expires_at):
            await self._get_access_token(params)
    
    async def _get_access_token(self, params: Dict[str, Any]):
        """Get access token using service account or OAuth."""
        service_account_key = params.get("service_account_key")
        refresh_token = params.get("refresh_token")
        client_id = params.get("client_id")
        client_secret = params.get("client_secret")
        access_token = params.get("access_token")
        
        if access_token:
            self.access_token = access_token
            self.token_expires_at = time.time() + 3600  # Assume 1 hour expiry
            logger.info("Using provided access token")
            return
        
        if service_account_key:
            await self._get_service_account_token(service_account_key)
        elif refresh_token and client_id and client_secret:
            await self._refresh_oauth_token(refresh_token, client_id, client_secret)
        else:
            raise Exception("No valid authentication method found")
    
    async def _get_service_account_token(self, service_account_key: str):
        """Get access token using service account."""
        try:
            import jwt
            
            # Parse service account key
            if isinstance(service_account_key, str):
                service_account = json.loads(service_account_key)
            else:
                service_account = service_account_key
            
            # Create JWT assertion
            now = int(time.time())
            payload = {
                "iss": service_account["client_email"],
                "scope": "https://www.googleapis.com/auth/analytics.readonly https://www.googleapis.com/auth/analytics.edit",
                "aud": "https://oauth2.googleapis.com/token",
                "exp": now + 3600,
                "iat": now
            }
            
            # Sign JWT
            assertion = jwt.encode(payload, service_account["private_key"], algorithm="RS256")
            
            # Exchange JWT for access token
            data = {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": assertion
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with self.session.post(self.AUTH_URL, headers=headers, data=data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.access_token = response_data.get("access_token")
                    expires_in = response_data.get("expires_in", 3600)
                    self.token_expires_at = time.time() + expires_in - 60
                    logger.info("Service account access token obtained successfully")
                else:
                    error_message = f"Failed to get service account token: {response_data.get('error_description', 'Unknown error')}"
                    logger.error(error_message)
                    raise Exception(error_message)
                    
        except ImportError:
            raise Exception("PyJWT library is required for service account authentication")
        except Exception as e:
            error_message = f"Error getting service account token: {str(e)}"
            logger.error(error_message)
            raise Exception(error_message)
    
    async def _refresh_oauth_token(self, refresh_token: str, client_id: str, client_secret: str):
        """Refresh OAuth access token."""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            async with self.session.post(self.AUTH_URL, headers=headers, data=data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.access_token = response_data.get("access_token")
                    expires_in = response_data.get("expires_in", 3600)
                    self.token_expires_at = time.time() + expires_in - 60
                    logger.info("OAuth access token refreshed successfully")
                else:
                    error_message = f"Failed to refresh OAuth token: {response_data.get('error_description', 'Unknown error')}"
                    logger.error(error_message)
                    raise Exception(error_message)
                    
        except Exception as e:
            error_message = f"Error refreshing OAuth token: {str(e)}"
            logger.error(error_message)
            raise Exception(error_message)
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any], 
                          data: Optional[Dict[str, Any]] = None, use_admin_api: bool = False) -> Dict[str, Any]:
        """Make an HTTP request to the Google Analytics API."""
        base_url = self._get_admin_api_base_url() if use_admin_api else self._get_data_api_base_url()
        url = f"{base_url}/{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                response_headers = dict(response.headers)
                
                # Handle different response content types
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Google Analytics API error {response.status}: {response_data}"
                    logger.error(error_message)
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "id": None,
                        "status_code": response.status,
                        "response_headers": response_headers,
                        "access_token": self.access_token,
                        "token_type": "Bearer",
                        "expires_in": None,
                        "rows": None,
                        "row_count": None,
                        "metadata": None,
                        "property_quota": None
                    }
                
                # Extract data from response
                rows = None
                row_count = None
                metadata = None
                property_quota = None
                response_id = None
                
                if isinstance(response_data, dict):
                    response_id = response_data.get("name") or response_data.get("id")
                    rows = response_data.get("rows", [])
                    row_count = response_data.get("rowCount", len(rows) if rows else 0)
                    metadata = response_data.get("metadata")
                    property_quota = response_data.get("propertyQuota")
                
                return {
                    "status": "success",
                    "result": response_data,
                    "error": None,
                    "id": response_id,
                    "status_code": response.status,
                    "response_headers": response_headers,
                    "access_token": self.access_token,
                    "token_type": "Bearer",
                    "expires_in": None,
                    "rows": rows,
                    "row_count": row_count,
                    "metadata": metadata,
                    "property_quota": property_quota
                }
                
        except aiohttp.ClientError as e:
            error_message = f"HTTP error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "error": error_message,
                "result": None,
                "id": None,
                "status_code": None,
                "response_headers": None,
                "access_token": self.access_token,
                "token_type": "Bearer",
                "expires_in": None,
                "rows": None,
                "row_count": None,
                "metadata": None,
                "property_quota": None
            }
    
    # -------------------------
    # Authentication Operations
    # -------------------------
    
    async def _operation_get_access_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get access token."""
        try:
            await self._get_access_token(params)
            return {
                "status": "success",
                "result": {
                    "access_token": self.access_token,
                    "token_type": "Bearer",
                    "expires_at": self.token_expires_at
                },
                "error": None,
                "id": None,
                "status_code": 200,
                "response_headers": None,
                "access_token": self.access_token,
                "token_type": "Bearer",
                "expires_in": int(self.token_expires_at - time.time()) if self.token_expires_at else None,
                "rows": None,
                "row_count": None,
                "metadata": None,
                "property_quota": None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "result": None,
                "id": None,
                "status_code": None,
                "response_headers": None,
                "access_token": None,
                "token_type": None,
                "expires_in": None,
                "rows": None,
                "row_count": None,
                "metadata": None,
                "property_quota": None
            }
    
    # -------------------------
    # Reporting Operations
    # -------------------------
    
    async def _operation_run_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a report."""
        property_id = params.get("property_id")
        
        request_data = params.get("request_body", {})
        if not request_data:
            request_data = {
                "dateRanges": params.get("date_ranges", [{"startDate": "30daysAgo", "endDate": "today"}]),
                "dimensions": params.get("dimensions", []),
                "metrics": params.get("metrics", []),
                "limit": params.get("limit", 10000),
                "offset": params.get("offset", 0),
                "keepEmptyRows": params.get("keep_empty_rows", False),
                "returnPropertyQuota": params.get("return_property_quota", False)
            }
            
            if params.get("dimension_filter"):
                request_data["dimensionFilter"] = params.get("dimension_filter")
            if params.get("metric_filter"):
                request_data["metricFilter"] = params.get("metric_filter")
            if params.get("order_bys"):
                request_data["orderBys"] = params.get("order_bys")
            if params.get("currency_code"):
                request_data["currencyCode"] = params.get("currency_code")
        
        return await self._make_request("POST", f"properties/{property_id}:runReport", params, request_data)
    
    async def _operation_run_pivot_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a pivot report."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}:runPivotReport", params, request_data)
    
    async def _operation_batch_run_reports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Batch run reports."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}:batchRunReports", params, request_data)
    
    async def _operation_batch_run_pivot_reports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Batch run pivot reports."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}:batchRunPivotReports", params, request_data)
    
    async def _operation_run_realtime_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a real-time report."""
        property_id = params.get("property_id")
        
        request_data = params.get("request_body", {})
        if not request_data:
            request_data = {
                "dimensions": params.get("dimensions", []),
                "metrics": params.get("metrics", []),
                "limit": params.get("limit", 10000)
            }
            
            if params.get("minute_ranges"):
                request_data["minuteRanges"] = params.get("minute_ranges")
            if params.get("dimension_filter"):
                request_data["dimensionFilter"] = params.get("dimension_filter")
            if params.get("metric_filter"):
                request_data["metricFilter"] = params.get("metric_filter")
            if params.get("order_bys"):
                request_data["orderBys"] = params.get("order_bys")
        
        return await self._make_request("POST", f"properties/{property_id}:runRealtimeReport", params, request_data)
    
    async def _operation_run_funnel_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a funnel report."""
        property_id = params.get("property_id")
        
        request_data = params.get("request_body", {})
        if not request_data:
            request_data = {
                "dateRanges": params.get("date_ranges", [{"startDate": "30daysAgo", "endDate": "today"}]),
                "funnel": params.get("funnel", {}),
                "dimensions": params.get("dimensions", [])
            }
        
        return await self._make_request("POST", f"properties/{property_id}:runFunnelReport", params, request_data)
    
    async def _operation_run_cohort_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a cohort report."""
        property_id = params.get("property_id")
        
        request_data = params.get("request_body", {})
        if not request_data:
            request_data = {
                "dateRanges": params.get("date_ranges", [{"startDate": "30daysAgo", "endDate": "today"}]),
                "cohortSpec": params.get("cohort_spec", {}),
                "dimensions": params.get("dimensions", []),
                "metrics": params.get("metrics", [])
            }
        
        return await self._make_request("POST", f"properties/{property_id}:runCohortReport", params, request_data)
    
    async def _operation_get_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata."""
        property_id = params.get("property_id")
        
        query_params = []
        if params.get("show_all_dimensions"):
            query_params.append("showAllDimensions=true")
        if params.get("show_all_metrics"):
            query_params.append("showAllMetrics=true")
        
        endpoint = f"properties/{property_id}/metadata"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        return await self._make_request("GET", endpoint, params)
    
    # -------------------------
    # Audience Operations
    # -------------------------
    
    async def _operation_list_audiences(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List audiences."""
        property_id = params.get("property_id")
        
        query_params = []
        if params.get("page_size"):
            query_params.append(f"pageSize={params.get('page_size')}")
        if params.get("page_token"):
            query_params.append(f"pageToken={params.get('page_token')}")
        
        endpoint = f"properties/{property_id}/audiences"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        return await self._make_request("GET", endpoint, params, use_admin_api=True)
    
    async def _operation_get_audience(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get audience details."""
        property_id = params.get("property_id")
        audience_id = params.get("audience_id")
        return await self._make_request("GET", f"properties/{property_id}/audiences/{audience_id}", params, use_admin_api=True)
    
    async def _operation_create_audience(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an audience."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}/audiences", params, request_data, use_admin_api=True)
    
    async def _operation_update_audience(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an audience."""
        property_id = params.get("property_id")
        audience_id = params.get("audience_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PATCH", f"properties/{property_id}/audiences/{audience_id}", params, request_data, use_admin_api=True)
    
    async def _operation_delete_audience(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an audience."""
        property_id = params.get("property_id")
        audience_id = params.get("audience_id")
        return await self._make_request("DELETE", f"properties/{property_id}/audiences/{audience_id}", params, use_admin_api=True)
    
    # -------------------------
    # Custom Dimensions Operations
    # -------------------------
    
    async def _operation_list_custom_dimensions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List custom dimensions."""
        property_id = params.get("property_id")
        
        query_params = []
        if params.get("page_size"):
            query_params.append(f"pageSize={params.get('page_size')}")
        if params.get("page_token"):
            query_params.append(f"pageToken={params.get('page_token')}")
        
        endpoint = f"properties/{property_id}/customDimensions"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        return await self._make_request("GET", endpoint, params, use_admin_api=True)
    
    async def _operation_get_custom_dimension(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get custom dimension details."""
        property_id = params.get("property_id")
        custom_dimension_id = params.get("custom_dimension_id")
        return await self._make_request("GET", f"properties/{property_id}/customDimensions/{custom_dimension_id}", params, use_admin_api=True)
    
    async def _operation_create_custom_dimension(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom dimension."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}/customDimensions", params, request_data, use_admin_api=True)
    
    async def _operation_update_custom_dimension(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a custom dimension."""
        property_id = params.get("property_id")
        custom_dimension_id = params.get("custom_dimension_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PATCH", f"properties/{property_id}/customDimensions/{custom_dimension_id}", params, request_data, use_admin_api=True)
    
    async def _operation_delete_custom_dimension(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a custom dimension."""
        property_id = params.get("property_id")
        custom_dimension_id = params.get("custom_dimension_id")
        return await self._make_request("DELETE", f"properties/{property_id}/customDimensions/{custom_dimension_id}", params, use_admin_api=True)
    
    async def _operation_archive_custom_dimension(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Archive a custom dimension."""
        property_id = params.get("property_id")
        custom_dimension_id = params.get("custom_dimension_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}/customDimensions/{custom_dimension_id}:archive", params, request_data, use_admin_api=True)
    
    # -------------------------
    # Custom Metrics Operations
    # -------------------------
    
    async def _operation_list_custom_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List custom metrics."""
        property_id = params.get("property_id")
        
        query_params = []
        if params.get("page_size"):
            query_params.append(f"pageSize={params.get('page_size')}")
        if params.get("page_token"):
            query_params.append(f"pageToken={params.get('page_token')}")
        
        endpoint = f"properties/{property_id}/customMetrics"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        return await self._make_request("GET", endpoint, params, use_admin_api=True)
    
    async def _operation_get_custom_metric(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get custom metric details."""
        property_id = params.get("property_id")
        custom_metric_id = params.get("custom_metric_id")
        return await self._make_request("GET", f"properties/{property_id}/customMetrics/{custom_metric_id}", params, use_admin_api=True)
    
    async def _operation_create_custom_metric(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom metric."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}/customMetrics", params, request_data, use_admin_api=True)
    
    async def _operation_update_custom_metric(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a custom metric."""
        property_id = params.get("property_id")
        custom_metric_id = params.get("custom_metric_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PATCH", f"properties/{property_id}/customMetrics/{custom_metric_id}", params, request_data, use_admin_api=True)
    
    async def _operation_delete_custom_metric(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a custom metric."""
        property_id = params.get("property_id")
        custom_metric_id = params.get("custom_metric_id")
        return await self._make_request("DELETE", f"properties/{property_id}/customMetrics/{custom_metric_id}", params, use_admin_api=True)
    
    async def _operation_archive_custom_metric(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Archive a custom metric."""
        property_id = params.get("property_id")
        custom_metric_id = params.get("custom_metric_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}/customMetrics/{custom_metric_id}:archive", params, request_data, use_admin_api=True)
    
    # -------------------------
    # Conversion Events Operations
    # -------------------------
    
    async def _operation_list_conversion_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List conversion events."""
        property_id = params.get("property_id")
        
        query_params = []
        if params.get("page_size"):
            query_params.append(f"pageSize={params.get('page_size')}")
        if params.get("page_token"):
            query_params.append(f"pageToken={params.get('page_token')}")
        
        endpoint = f"properties/{property_id}/conversionEvents"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        return await self._make_request("GET", endpoint, params, use_admin_api=True)
    
    async def _operation_get_conversion_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get conversion event details."""
        property_id = params.get("property_id")
        conversion_event_id = params.get("conversion_event_id")
        return await self._make_request("GET", f"properties/{property_id}/conversionEvents/{conversion_event_id}", params, use_admin_api=True)
    
    async def _operation_create_conversion_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a conversion event."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}/conversionEvents", params, request_data, use_admin_api=True)
    
    async def _operation_update_conversion_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a conversion event."""
        property_id = params.get("property_id")
        conversion_event_id = params.get("conversion_event_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PATCH", f"properties/{property_id}/conversionEvents/{conversion_event_id}", params, request_data, use_admin_api=True)
    
    async def _operation_delete_conversion_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a conversion event."""
        property_id = params.get("property_id")
        conversion_event_id = params.get("conversion_event_id")
        return await self._make_request("DELETE", f"properties/{property_id}/conversionEvents/{conversion_event_id}", params, use_admin_api=True)
    
    # -------------------------
    # Data Streams Operations
    # -------------------------
    
    async def _operation_list_data_streams(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List data streams."""
        property_id = params.get("property_id")
        
        query_params = []
        if params.get("page_size"):
            query_params.append(f"pageSize={params.get('page_size')}")
        if params.get("page_token"):
            query_params.append(f"pageToken={params.get('page_token')}")
        
        endpoint = f"properties/{property_id}/dataStreams"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        return await self._make_request("GET", endpoint, params, use_admin_api=True)
    
    async def _operation_get_data_stream(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get data stream details."""
        property_id = params.get("property_id")
        data_stream_id = params.get("data_stream_id")
        return await self._make_request("GET", f"properties/{property_id}/dataStreams/{data_stream_id}", params, use_admin_api=True)
    
    async def _operation_create_data_stream(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a data stream."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}/dataStreams", params, request_data, use_admin_api=True)
    
    async def _operation_update_data_stream(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a data stream."""
        property_id = params.get("property_id")
        data_stream_id = params.get("data_stream_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PATCH", f"properties/{property_id}/dataStreams/{data_stream_id}", params, request_data, use_admin_api=True)
    
    async def _operation_delete_data_stream(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a data stream."""
        property_id = params.get("property_id")
        data_stream_id = params.get("data_stream_id")
        return await self._make_request("DELETE", f"properties/{property_id}/dataStreams/{data_stream_id}", params, use_admin_api=True)
    
    # -------------------------
    # Google Ads Links Operations
    # -------------------------
    
    async def _operation_list_google_ads_links(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Google Ads links."""
        property_id = params.get("property_id")
        
        query_params = []
        if params.get("page_size"):
            query_params.append(f"pageSize={params.get('page_size')}")
        if params.get("page_token"):
            query_params.append(f"pageToken={params.get('page_token')}")
        
        endpoint = f"properties/{property_id}/googleAdsLinks"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        return await self._make_request("GET", endpoint, params, use_admin_api=True)
    
    async def _operation_get_google_ads_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Google Ads link details."""
        property_id = params.get("property_id")
        google_ads_link_id = params.get("google_ads_link_id")
        return await self._make_request("GET", f"properties/{property_id}/googleAdsLinks/{google_ads_link_id}", params, use_admin_api=True)
    
    async def _operation_create_google_ads_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Google Ads link."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}/googleAdsLinks", params, request_data, use_admin_api=True)
    
    async def _operation_update_google_ads_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Google Ads link."""
        property_id = params.get("property_id")
        google_ads_link_id = params.get("google_ads_link_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PATCH", f"properties/{property_id}/googleAdsLinks/{google_ads_link_id}", params, request_data, use_admin_api=True)
    
    async def _operation_delete_google_ads_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Google Ads link."""
        property_id = params.get("property_id")
        google_ads_link_id = params.get("google_ads_link_id")
        return await self._make_request("DELETE", f"properties/{property_id}/googleAdsLinks/{google_ads_link_id}", params, use_admin_api=True)
    
    # -------------------------
    # Attribution Settings Operations
    # -------------------------
    
    async def _operation_get_attribution_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get attribution settings."""
        property_id = params.get("property_id")
        return await self._make_request("GET", f"properties/{property_id}/attributionSettings", params, use_admin_api=True)
    
    async def _operation_update_attribution_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update attribution settings."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PATCH", f"properties/{property_id}/attributionSettings", params, request_data, use_admin_api=True)
    
    # -------------------------
    # Data Retention Settings Operations
    # -------------------------
    
    async def _operation_get_data_retention_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get data retention settings."""
        property_id = params.get("property_id")
        return await self._make_request("GET", f"properties/{property_id}/dataRetentionSettings", params, use_admin_api=True)
    
    async def _operation_update_data_retention_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update data retention settings."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PATCH", f"properties/{property_id}/dataRetentionSettings", params, request_data, use_admin_api=True)
    
    # -------------------------
    # Enhanced Measurement Settings Operations
    # -------------------------
    
    async def _operation_get_enhanced_measurement_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get enhanced measurement settings."""
        property_id = params.get("property_id")
        data_stream_id = params.get("data_stream_id")
        return await self._make_request("GET", f"properties/{property_id}/dataStreams/{data_stream_id}/enhancedMeasurementSettings", params, use_admin_api=True)
    
    async def _operation_update_enhanced_measurement_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update enhanced measurement settings."""
        property_id = params.get("property_id")
        data_stream_id = params.get("data_stream_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PATCH", f"properties/{property_id}/dataStreams/{data_stream_id}/enhancedMeasurementSettings", params, request_data, use_admin_api=True)
    
    # -------------------------
    # Firebase Links Operations
    # -------------------------
    
    async def _operation_list_firebase_links(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Firebase links."""
        property_id = params.get("property_id")
        
        query_params = []
        if params.get("page_size"):
            query_params.append(f"pageSize={params.get('page_size')}")
        if params.get("page_token"):
            query_params.append(f"pageToken={params.get('page_token')}")
        
        endpoint = f"properties/{property_id}/firebaseLinks"
        if query_params:
            endpoint += "?" + "&".join(query_params)
        
        return await self._make_request("GET", endpoint, params, use_admin_api=True)
    
    async def _operation_get_firebase_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Firebase link details."""
        property_id = params.get("property_id")
        firebase_link_id = params.get("firebase_link_id")
        return await self._make_request("GET", f"properties/{property_id}/firebaseLinks/{firebase_link_id}", params, use_admin_api=True)
    
    async def _operation_create_firebase_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Firebase link."""
        property_id = params.get("property_id")
        request_data = params.get("request_body", {})
        return await self._make_request("POST", f"properties/{property_id}/firebaseLinks", params, request_data, use_admin_api=True)
    
    async def _operation_update_firebase_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Firebase link."""
        property_id = params.get("property_id")
        firebase_link_id = params.get("firebase_link_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PATCH", f"properties/{property_id}/firebaseLinks/{firebase_link_id}", params, request_data, use_admin_api=True)
    
    async def _operation_delete_firebase_link(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Firebase link."""
        property_id = params.get("property_id")
        firebase_link_id = params.get("firebase_link_id")
        return await self._make_request("DELETE", f"properties/{property_id}/firebaseLinks/{firebase_link_id}", params, use_admin_api=True)


# Utility functions for common Google Analytics operations
class GoogleAnalyticsHelpers:
    """Helper functions for common Google Analytics operations."""
    
    @staticmethod
    def create_date_range(start_date: str, end_date: str, name: str = None) -> Dict[str, Any]:
        """Create date range object for reports."""
        date_range = {
            "startDate": start_date,
            "endDate": end_date
        }
        if name:
            date_range["name"] = name
        return date_range
    
    @staticmethod
    def create_dimension(name: str, dimension_expression: str = None) -> Dict[str, Any]:
        """Create dimension object for reports."""
        dimension = {"name": name}
        if dimension_expression:
            dimension["dimensionExpression"] = {"lowerCase": {"dimension": {"name": dimension_expression}}}
        return dimension
    
    @staticmethod
    def create_metric(name: str, expression: str = None) -> Dict[str, Any]:
        """Create metric object for reports."""
        metric = {"name": name}
        if expression:
            metric["expression"] = expression
        return metric
    
    @staticmethod
    def create_order_by(field_name: str, desc: bool = False, order_type: str = "VALUE") -> Dict[str, Any]:
        """Create order by object for reports."""
        return {
            "desc": desc,
            order_type.lower(): {"fieldName": field_name}
        }
    
    @staticmethod
    def create_dimension_filter(dimension_name: str, values: List[str], 
                              match_type: str = "EXACT", case_sensitive: bool = False) -> Dict[str, Any]:
        """Create dimension filter for reports."""
        return {
            "filter": {
                "fieldName": dimension_name,
                "stringFilter": {
                    "matchType": match_type,
                    "value": values[0] if len(values) == 1 else None,
                    "caseSensitive": case_sensitive
                },
                "inListFilter": {
                    "values": values,
                    "caseSensitive": case_sensitive
                } if len(values) > 1 else None
            }
        }
    
    @staticmethod
    def create_metric_filter(metric_name: str, value: float, operation: str = "EQUAL") -> Dict[str, Any]:
        """Create metric filter for reports."""
        return {
            "filter": {
                "fieldName": metric_name,
                "numericFilter": {
                    "operation": operation,
                    "value": {"doubleValue": value}
                }
            }
        }
    
    @staticmethod
    def create_cohort_spec(cohorts: List[Dict[str, Any]], cohort_reporting_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create cohort specification for cohort reports."""
        return {
            "cohorts": cohorts,
            "cohortReportingSettings": cohort_reporting_settings
        }
    
    @staticmethod
    def create_funnel_step(name: str, filter_expression: str, 
                          is_directly_followed_by: bool = False) -> Dict[str, Any]:
        """Create funnel step for funnel reports."""
        return {
            "name": name,
            "filterExpression": {
                "filter": {
                    "fieldName": "eventName",
                    "stringFilter": {
                        "value": filter_expression
                    }
                }
            },
            "isDirectlyFollowedBy": is_directly_followed_by
        }


# Main test function for Google Analytics Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Google Analytics Node Test Suite ===")
        
        # Get API credentials from environment or user input
        service_account_key = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY")
        property_id = os.environ.get("GA4_PROPERTY_ID")
        
        if not service_account_key:
            print("Google Service Account Key not found in environment variable GOOGLE_SERVICE_ACCOUNT_KEY")
            print("Please provide service account credentials...")
            
            service_account_path = input("Enter path to service account JSON file (or press Enter to skip): ")
            if service_account_path and os.path.exists(service_account_path):
                with open(service_account_path, 'r') as f:
                    service_account_key = f.read()
        
        if not property_id:
            property_id = input("Enter GA4 Property ID: ")
        
        if not service_account_key or not property_id:
            print("Service account key and property ID are required for testing")
            return
        
        # Create an instance of the Google Analytics Node
        node = GoogleAnalyticsNode()
        
        # Test cases
        test_cases = [
            {
                "name": "Get Access Token",
                "params": {
                    "operation": GoogleAnalyticsOperation.GET_ACCESS_TOKEN,
                    "service_account_key": service_account_key
                },
                "expected_status": "success"
            },
            {
                "name": "Get Metadata",
                "params": {
                    "operation": GoogleAnalyticsOperation.GET_METADATA,
                    "service_account_key": service_account_key,
                    "property_id": property_id
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
                    if result.get("access_token"):
                        print(f"Access token obtained: {result['access_token'][:20]}...")
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
    registry.register("google_analytics", GoogleAnalyticsNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register GoogleAnalyticsNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")