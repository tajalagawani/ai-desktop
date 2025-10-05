"""
Zoom Node - Unified implementation using UniversalRequestNode
Comprehensive Zoom Video Communications API integration for meeting management, webinars, recordings, and user administration.
"""

import logging
import json
import base64
import hashlib
import hmac
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

try:
    from universal_request_node import UniversalRequestNode
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    except ImportError:
        from universal_request_node import UniversalRequestNode
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )

# Configure logging
logger = logging.getLogger(__name__)

class ZoomNode(BaseNode):
    """
    Unified Zoom Node using UniversalRequestNode for Zoom Video Communications API integration.
    Supports comprehensive meeting management, webinars, recordings, and user administration.
    """
    
    # Configuration for Zoom API v2
    CONFIG = {
        "base_url": "https://api.zoom.us/v2",
        "authentication": {
            "type": "oauth2_bearer",
            "header": "Authorization",
            "prefix": "Bearer"
        },
        "default_headers": {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        "retry_config": {
            "max_retries": 3,
            "backoff_factor": 1.0,
            "retry_on_status": [429, 500, 502, 503, 504]
        },
        "rate_limiting": {
            "requests_per_second": 10,
            "requests_per_minute": 600
        },
        "timeouts": {
            "connect": 30,
            "read": 300,
            "total": 600
        }
    }
    
    # Operations mapping for Zoom API v2
    OPERATIONS = {
        # Meeting Operations
        "create_meeting": {
            "method": "POST",
            "endpoint": "users/{user_id}/meetings",
            "required_params": ["user_id", "topic"],
            "path_params": ["user_id"]
        },
        "get_meeting": {
            "method": "GET",
            "endpoint": "meetings/{meeting_id}",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "update_meeting": {
            "method": "PATCH",
            "endpoint": "meetings/{meeting_id}",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "delete_meeting": {
            "method": "DELETE",
            "endpoint": "meetings/{meeting_id}",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "list_meetings": {
            "method": "GET",
            "endpoint": "users/{user_id}/meetings",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        "get_meeting_invitation": {
            "method": "GET",
            "endpoint": "meetings/{meeting_id}/invitation",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "update_meeting_status": {
            "method": "PATCH",
            "endpoint": "meetings/{meeting_id}/status",
            "required_params": ["meeting_id", "action"],
            "path_params": ["meeting_id"]
        },
        "get_meeting_poll": {
            "method": "GET",
            "endpoint": "meetings/{meeting_id}/polls/{poll_id}",
            "required_params": ["meeting_id", "poll_id"],
            "path_params": ["meeting_id", "poll_id"]
        },
        "create_meeting_poll": {
            "method": "POST",
            "endpoint": "meetings/{meeting_id}/polls",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "update_meeting_poll": {
            "method": "PUT",
            "endpoint": "meetings/{meeting_id}/polls/{poll_id}",
            "required_params": ["meeting_id", "poll_id"],
            "path_params": ["meeting_id", "poll_id"]
        },
        "delete_meeting_poll": {
            "method": "DELETE",
            "endpoint": "meetings/{meeting_id}/polls/{poll_id}",
            "required_params": ["meeting_id", "poll_id"],
            "path_params": ["meeting_id", "poll_id"]
        },
        "list_meeting_polls": {
            "method": "GET",
            "endpoint": "meetings/{meeting_id}/polls",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        
        # Meeting Registration Operations
        "add_meeting_registrant": {
            "method": "POST",
            "endpoint": "meetings/{meeting_id}/registrants",
            "required_params": ["meeting_id", "email", "first_name", "last_name"],
            "path_params": ["meeting_id"]
        },
        "list_meeting_registrants": {
            "method": "GET",
            "endpoint": "meetings/{meeting_id}/registrants",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "update_registrant_status": {
            "method": "PUT",
            "endpoint": "meetings/{meeting_id}/registrants/status",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "get_meeting_registrant": {
            "method": "GET",
            "endpoint": "meetings/{meeting_id}/registrants/{registrant_id}",
            "required_params": ["meeting_id", "registrant_id"],
            "path_params": ["meeting_id", "registrant_id"]
        },
        
        # Participant Operations
        "list_meeting_participants": {
            "method": "GET",
            "endpoint": "past_meetings/{meeting_uuid}/participants",
            "required_params": ["meeting_uuid"],
            "path_params": ["meeting_uuid"]
        },
        "get_meeting_participant": {
            "method": "GET",
            "endpoint": "past_meetings/{meeting_uuid}/participants/{participant_uuid}",
            "required_params": ["meeting_uuid", "participant_uuid"],
            "path_params": ["meeting_uuid", "participant_uuid"]
        },
        "get_live_participants": {
            "method": "GET",
            "endpoint": "meetings/{meeting_id}/participants",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "update_participant_status": {
            "method": "PATCH",
            "endpoint": "meetings/{meeting_id}/participants/{participant_id}/status",
            "required_params": ["meeting_id", "participant_id", "action"],
            "path_params": ["meeting_id", "participant_id"]
        },
        
        # Recording Operations
        "list_recordings": {
            "method": "GET",
            "endpoint": "users/{user_id}/recordings",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        "get_meeting_recordings": {
            "method": "GET",
            "endpoint": "meetings/{meeting_id}/recordings",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "delete_meeting_recording": {
            "method": "DELETE",
            "endpoint": "meetings/{meeting_id}/recordings",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "delete_recording_file": {
            "method": "DELETE",
            "endpoint": "meetings/{meeting_id}/recordings/{recording_id}",
            "required_params": ["meeting_id", "recording_id"],
            "path_params": ["meeting_id", "recording_id"]
        },
        "recover_meeting_recordings": {
            "method": "PUT",
            "endpoint": "meetings/{meeting_id}/recordings/status",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "get_recording_settings": {
            "method": "GET",
            "endpoint": "meetings/{meeting_id}/recordings/settings",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "update_recording_settings": {
            "method": "PATCH",
            "endpoint": "meetings/{meeting_id}/recordings/settings",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        
        # Webinar Operations
        "create_webinar": {
            "method": "POST",
            "endpoint": "users/{user_id}/webinars",
            "required_params": ["user_id", "topic"],
            "path_params": ["user_id"]
        },
        "get_webinar": {
            "method": "GET",
            "endpoint": "webinars/{webinar_id}",
            "required_params": ["webinar_id"],
            "path_params": ["webinar_id"]
        },
        "update_webinar": {
            "method": "PATCH",
            "endpoint": "webinars/{webinar_id}",
            "required_params": ["webinar_id"],
            "path_params": ["webinar_id"]
        },
        "delete_webinar": {
            "method": "DELETE",
            "endpoint": "webinars/{webinar_id}",
            "required_params": ["webinar_id"],
            "path_params": ["webinar_id"]
        },
        "list_webinars": {
            "method": "GET",
            "endpoint": "users/{user_id}/webinars",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        "update_webinar_status": {
            "method": "PATCH",
            "endpoint": "webinars/{webinar_id}/status",
            "required_params": ["webinar_id", "action"],
            "path_params": ["webinar_id"]
        },
        "get_webinar_panelists": {
            "method": "GET",
            "endpoint": "webinars/{webinar_id}/panelists",
            "required_params": ["webinar_id"],
            "path_params": ["webinar_id"]
        },
        "add_webinar_panelists": {
            "method": "POST",
            "endpoint": "webinars/{webinar_id}/panelists",
            "required_params": ["webinar_id", "panelists"],
            "path_params": ["webinar_id"]
        },
        "remove_webinar_panelist": {
            "method": "DELETE",
            "endpoint": "webinars/{webinar_id}/panelists/{panelist_id}",
            "required_params": ["webinar_id", "panelist_id"],
            "path_params": ["webinar_id", "panelist_id"]
        },
        "remove_all_webinar_panelists": {
            "method": "DELETE",
            "endpoint": "webinars/{webinar_id}/panelists",
            "required_params": ["webinar_id"],
            "path_params": ["webinar_id"]
        },
        
        # Webinar Registration Operations
        "add_webinar_registrant": {
            "method": "POST",
            "endpoint": "webinars/{webinar_id}/registrants",
            "required_params": ["webinar_id", "email", "first_name", "last_name"],
            "path_params": ["webinar_id"]
        },
        "list_webinar_registrants": {
            "method": "GET",
            "endpoint": "webinars/{webinar_id}/registrants",
            "required_params": ["webinar_id"],
            "path_params": ["webinar_id"]
        },
        "update_webinar_registrant_status": {
            "method": "PUT",
            "endpoint": "webinars/{webinar_id}/registrants/status",
            "required_params": ["webinar_id"],
            "path_params": ["webinar_id"]
        },
        "get_webinar_registrant": {
            "method": "GET",
            "endpoint": "webinars/{webinar_id}/registrants/{registrant_id}",
            "required_params": ["webinar_id", "registrant_id"],
            "path_params": ["webinar_id", "registrant_id"]
        },
        
        # User Management Operations
        "create_user": {
            "method": "POST",
            "endpoint": "users",
            "required_params": ["email", "type", "first_name", "last_name"]
        },
        "get_user": {
            "method": "GET",
            "endpoint": "users/{user_id}",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        "update_user": {
            "method": "PATCH",
            "endpoint": "users/{user_id}",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        "delete_user": {
            "method": "DELETE",
            "endpoint": "users/{user_id}",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        "list_users": {
            "method": "GET",
            "endpoint": "users",
            "required_params": []
        },
        "check_user_email": {
            "method": "GET",
            "endpoint": "users/{email}",
            "required_params": ["email"],
            "path_params": ["email"]
        },
        "get_user_token": {
            "method": "GET",
            "endpoint": "users/{user_id}/token",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        "revoke_user_sso_token": {
            "method": "DELETE",
            "endpoint": "users/{user_id}/token",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        "get_user_permissions": {
            "method": "GET",
            "endpoint": "users/{user_id}/permissions",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        "update_user_permissions": {
            "method": "PATCH",
            "endpoint": "users/{user_id}/permissions",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        "get_user_settings": {
            "method": "GET",
            "endpoint": "users/{user_id}/settings",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        "update_user_settings": {
            "method": "PATCH",
            "endpoint": "users/{user_id}/settings",
            "required_params": ["user_id"],
            "path_params": ["user_id"]
        },
        
        # Account Operations
        "get_account_info": {
            "method": "GET",
            "endpoint": "accounts/{account_id}",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        },
        "update_account_info": {
            "method": "PATCH",
            "endpoint": "accounts/{account_id}",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        },
        "get_account_settings": {
            "method": "GET",
            "endpoint": "accounts/{account_id}/settings",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        },
        "update_account_settings": {
            "method": "PATCH",
            "endpoint": "accounts/{account_id}/settings",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        },
        "get_billing_info": {
            "method": "GET",
            "endpoint": "accounts/{account_id}/billing",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        },
        "update_billing_info": {
            "method": "PATCH",
            "endpoint": "accounts/{account_id}/billing",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        },
        "get_plan_information": {
            "method": "GET",
            "endpoint": "accounts/{account_id}/plans",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        },
        "update_plan_information": {
            "method": "PATCH",
            "endpoint": "accounts/{account_id}/plans",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        },
        
        # Phone and SMS Operations
        "list_phone_numbers": {
            "method": "GET",
            "endpoint": "phone/numbers",
            "required_params": []
        },
        "get_phone_number": {
            "method": "GET",
            "endpoint": "phone/numbers/{number_id}",
            "required_params": ["number_id"],
            "path_params": ["number_id"]
        },
        "assign_phone_number": {
            "method": "PATCH",
            "endpoint": "phone/numbers/{number_id}",
            "required_params": ["number_id"],
            "path_params": ["number_id"]
        },
        "unassign_phone_number": {
            "method": "DELETE",
            "endpoint": "phone/numbers/{number_id}",
            "required_params": ["number_id"],
            "path_params": ["number_id"]
        },
        "send_sms": {
            "method": "POST",
            "endpoint": "sms",
            "required_params": ["to", "message"]
        },
        "get_sms": {
            "method": "GET",
            "endpoint": "sms/{sms_id}",
            "required_params": ["sms_id"],
            "path_params": ["sms_id"]
        },
        "list_sms": {
            "method": "GET",
            "endpoint": "sms",
            "required_params": []
        },
        
        # Dashboard and Analytics Operations
        "get_dashboard_meetings": {
            "method": "GET",
            "endpoint": "metrics/meetings",
            "required_params": ["from", "to"]
        },
        "get_meeting_details": {
            "method": "GET",
            "endpoint": "metrics/meetings/{meeting_id}",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "get_meeting_participant_qos": {
            "method": "GET",
            "endpoint": "metrics/meetings/{meeting_id}/participants/{participant_id}/qos",
            "required_params": ["meeting_id", "participant_id"],
            "path_params": ["meeting_id", "participant_id"]
        },
        "list_meeting_participants_qos": {
            "method": "GET",
            "endpoint": "metrics/meetings/{meeting_id}/participants/qos",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "get_meeting_participant_sharing_recording_details": {
            "method": "GET",
            "endpoint": "metrics/meetings/{meeting_id}/participants/sharing",
            "required_params": ["meeting_id"],
            "path_params": ["meeting_id"]
        },
        "list_webinar_participants_qos": {
            "method": "GET",
            "endpoint": "metrics/webinars/{webinar_id}/participants/qos",
            "required_params": ["webinar_id"],
            "path_params": ["webinar_id"]
        },
        "get_webinar_details": {
            "method": "GET",
            "endpoint": "metrics/webinars/{webinar_id}",
            "required_params": ["webinar_id"],
            "path_params": ["webinar_id"]
        },
        "get_webinar_participant_qos": {
            "method": "GET",
            "endpoint": "metrics/webinars/{webinar_id}/participants/{participant_id}/qos",
            "required_params": ["webinar_id", "participant_id"],
            "path_params": ["webinar_id", "participant_id"]
        },
        "get_webinar_participant_sharing_recording_details": {
            "method": "GET",
            "endpoint": "metrics/webinars/{webinar_id}/participants/sharing",
            "required_params": ["webinar_id"],
            "path_params": ["webinar_id"]
        },
        "get_dashboard_webinars": {
            "method": "GET",
            "endpoint": "metrics/webinars",
            "required_params": ["from", "to"]
        },
        
        # Cloud Recording Management Operations
        "get_account_cloud_recording": {
            "method": "GET",
            "endpoint": "accounts/{account_id}/recordings",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.universal_node = UniversalRequestNode(self.CONFIG, self.OPERATIONS, sandbox_timeout)
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Zoom node."""
        return NodeSchema(
            node_type="zoom",
            version="2.0.0", 
            description="Comprehensive Zoom Video Communications API integration with 80+ operations using UniversalRequestNode for meetings, webinars, recordings, and user management",
            parameters=[
                # Core configuration
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Zoom operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 access token for Zoom API",
                    required=True
                ),
                
                # ID parameters
                NodeParameter(
                    name="user_id",
                    type=NodeParameterType.STRING,
                    description="User ID or email address for user operations",
                    required=False
                ),
                NodeParameter(
                    name="meeting_id",
                    type=NodeParameterType.STRING,
                    description="Meeting ID for meeting operations",
                    required=False
                ),
                NodeParameter(
                    name="meeting_uuid",
                    type=NodeParameterType.STRING,
                    description="Meeting UUID for meeting operations",
                    required=False
                ),
                NodeParameter(
                    name="webinar_id",
                    type=NodeParameterType.STRING,
                    description="Webinar ID for webinar operations",
                    required=False
                ),
                NodeParameter(
                    name="participant_id",
                    type=NodeParameterType.STRING,
                    description="Participant ID for participant operations",
                    required=False
                ),
                NodeParameter(
                    name="participant_uuid",
                    type=NodeParameterType.STRING,
                    description="Participant UUID for participant operations",
                    required=False
                ),
                NodeParameter(
                    name="registrant_id",
                    type=NodeParameterType.STRING,
                    description="Registrant ID for registration operations",
                    required=False
                ),
                NodeParameter(
                    name="panelist_id",
                    type=NodeParameterType.STRING,
                    description="Panelist ID for webinar panelist operations",
                    required=False
                ),
                NodeParameter(
                    name="poll_id",
                    type=NodeParameterType.STRING,
                    description="Poll ID for poll operations",
                    required=False
                ),
                NodeParameter(
                    name="recording_id",
                    type=NodeParameterType.STRING,
                    description="Recording ID for recording operations",
                    required=False
                ),
                NodeParameter(
                    name="account_id",
                    type=NodeParameterType.STRING,
                    description="Account ID for account operations",
                    required=False
                ),
                NodeParameter(
                    name="number_id",
                    type=NodeParameterType.STRING,
                    description="Phone number ID for phone operations",
                    required=False
                ),
                NodeParameter(
                    name="sms_id",
                    type=NodeParameterType.STRING,
                    description="SMS ID for SMS operations",
                    required=False
                ),
                
                # Meeting parameters
                NodeParameter(
                    name="topic",
                    type=NodeParameterType.STRING,
                    description="Meeting or webinar topic",
                    required=False
                ),
                NodeParameter(
                    name="agenda",
                    type=NodeParameterType.STRING,
                    description="Meeting or webinar agenda",
                    required=False
                ),
                NodeParameter(
                    name="start_time",
                    type=NodeParameterType.STRING,
                    description="Start time in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ)",
                    required=False
                ),
                NodeParameter(
                    name="duration",
                    type=NodeParameterType.NUMBER,
                    description="Meeting duration in minutes",
                    required=False,
                    default=60
                ),
                NodeParameter(
                    name="timezone",
                    type=NodeParameterType.STRING,
                    description="Timezone for the meeting",
                    required=False,
                    default="UTC"
                ),
                NodeParameter(
                    name="password",
                    type=NodeParameterType.STRING,
                    description="Meeting or webinar password",
                    required=False
                ),
                NodeParameter(
                    name="type",
                    type=NodeParameterType.NUMBER,
                    description="Meeting type (1=instant, 2=scheduled, 3=recurring no fixed time, 8=recurring fixed time)",
                    required=False,
                    enum=[1, 2, 3, 8],
                    default=2
                ),
                
                # User parameters
                NodeParameter(
                    name="email",
                    type=NodeParameterType.STRING,
                    description="User email address",
                    required=False
                ),
                NodeParameter(
                    name="first_name",
                    type=NodeParameterType.STRING,
                    description="User first name",
                    required=False
                ),
                NodeParameter(
                    name="last_name",
                    type=NodeParameterType.STRING,
                    description="User last name",
                    required=False
                ),
                
                # Action parameters
                NodeParameter(
                    name="action",
                    type=NodeParameterType.STRING,
                    description="Action to perform (end, recover, etc.)",
                    required=False
                ),
                
                # Request body
                NodeParameter(
                    name="request_body",
                    type=NodeParameterType.OBJECT,
                    description="Request body for create/update operations",
                    required=False
                ),
                
                # Phone/SMS parameters
                NodeParameter(
                    name="to",
                    type=NodeParameterType.STRING,
                    description="Destination phone number for SMS",
                    required=False
                ),
                NodeParameter(
                    name="message",
                    type=NodeParameterType.STRING,
                    description="SMS message content",
                    required=False
                ),
                
                # Date range parameters
                NodeParameter(
                    name="from",
                    type=NodeParameterType.STRING,
                    description="Start date for date range queries (YYYY-MM-DD)",
                    required=False
                ),
                NodeParameter(
                    name="to_date",
                    type=NodeParameterType.STRING,
                    description="End date for date range queries (YYYY-MM-DD)",
                    required=False
                ),
                
                # Query parameters
                NodeParameter(
                    name="page_size",
                    type=NodeParameterType.NUMBER,
                    description="Number of records per page",
                    required=False,
                    default=30,
                    min_value=1,
                    max_value=300
                ),
                NodeParameter(
                    name="page_number",
                    type=NodeParameterType.NUMBER,
                    description="Page number",
                    required=False,
                    default=1,
                    min_value=1
                ),
                NodeParameter(
                    name="next_page_token",
                    type=NodeParameterType.STRING,
                    description="Next page token for pagination",
                    required=False
                ),
                
                # Arrays for bulk operations
                NodeParameter(
                    name="panelists",
                    type=NodeParameterType.ARRAY,
                    description="Array of panelists for webinar operations",
                    required=False
                ),
                NodeParameter(
                    name="registrants",
                    type=NodeParameterType.ARRAY,
                    description="Array of registrants for status updates",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT,
                "meeting_id": NodeParameterType.STRING,
                "webinar_id": NodeParameterType.STRING,
                "join_url": NodeParameterType.STRING,
                "start_url": NodeParameterType.STRING,
                "participant_count": NodeParameterType.NUMBER,
                "registration_url": NodeParameterType.STRING
            },
            tags=["zoom", "video", "conferencing", "meetings", "webinars", "api", "unified"],
            author="System",
            documentation_url="https://marketplace.zoom.us/docs/api-reference/zoom-api"
        )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Zoom operation using UniversalRequestNode."""
        try:
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            if not operation:
                raise NodeValidationError("Operation is required")
                
            if operation not in self.OPERATIONS:
                raise NodeValidationError(f"Unknown operation: {operation}")
            
            # Get operation config
            op_config = self.OPERATIONS[operation]
            
            # Build the universal request node data
            universal_data = await self._build_universal_request(params, op_config)
            
            # Execute using universal request node
            result = await self.universal_node.execute(universal_data)
            
            # Process the result for Zoom-specific outputs
            return await self._process_result(result, params, operation)
            
        except Exception as e:
            logger.error(f"Error in Zoom operation: {str(e)}")
            return {
                "status": "error",
                "result": None,
                "error": str(e),
                "status_code": None,
                "response_headers": None,
                "meeting_id": None,
                "webinar_id": None,
                "join_url": None,
                "start_url": None,
                "participant_count": None,
                "registration_url": None
            }

    async def _build_universal_request(self, params: Dict[str, Any], op_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build request data for UniversalRequestNode."""
        # Start with base config
        config = self.CONFIG.copy()
        
        # Set up OAuth2 bearer token authentication
        access_token = params.get("access_token")
        if access_token:
            config["authentication"]["token"] = access_token
        
        # Build endpoint with path parameters
        endpoint = op_config["endpoint"]
        path_params = op_config.get("path_params", [])
        
        for param in path_params:
            value = params.get(param)
            if value is not None:
                placeholder = "{" + param + "}"
                endpoint = endpoint.replace(placeholder, str(value))
        
        # Build query parameters
        query_params = {}
        query_mappings = {
            "page_size": "page_size",
            "page_number": "page_number", 
            "next_page_token": "next_page_token",
            "from": "from",
            "to_date": "to",
            "occurrence_id": "occurrence_id",
            "show_previous_occurrences": "show_previous_occurrences",
            "type": "type"
        }
        
        for param, query_param in query_mappings.items():
            if params.get(param) is not None:
                query_params[query_param] = params[param]
        
        # Build request body based on operation
        request_body = await self._build_request_body(params, op_config, endpoint)
        
        return {
            "params": {
                "config": config,
                "method": op_config["method"],
                "endpoint": endpoint,
                "query_params": query_params if query_params else None,
                "request_body": request_body,
                "timeout": config["timeouts"]["total"]
            }
        }

    async def _build_request_body(self, params: Dict[str, Any], op_config: Dict[str, Any], endpoint: str) -> Optional[Dict[str, Any]]:
        """Build request body for specific operations."""
        operation = params.get("operation", "")
        
        # Use explicit request_body if provided
        if params.get("request_body"):
            return params["request_body"]
        
        # Handle meeting creation
        if "create_meeting" in operation:
            body = {
                "topic": params.get("topic"),
                "type": params.get("type", 2),
                "agenda": params.get("agenda", ""),
                "duration": params.get("duration", 60),
                "timezone": params.get("timezone", "UTC"),
                "password": params.get("password", ""),
                "settings": {
                    "host_video": True,
                    "participant_video": True,
                    "cn_meeting": False,
                    "in_meeting": False,
                    "join_before_host": True,
                    "mute_upon_entry": True,
                    "watermark": False,
                    "use_pmi": False,
                    "approval_type": 2,
                    "registration_type": 1,
                    "audio": "both",
                    "auto_recording": "none"
                }
            }
            
            if params.get("start_time"):
                body["start_time"] = params["start_time"]
            
            return body
        
        # Handle webinar creation
        if "create_webinar" in operation:
            body = {
                "topic": params.get("topic"),
                "type": params.get("type", 5),
                "agenda": params.get("agenda", ""),
                "duration": params.get("duration", 60),
                "timezone": params.get("timezone", "UTC"),
                "password": params.get("password", ""),
                "settings": {
                    "host_video": True,
                    "panelists_video": True,
                    "practice_session": False,
                    "hd_video": True,
                    "approval_type": 0,
                    "registration_type": 1,
                    "audio": "both",
                    "auto_recording": "none",
                    "show_share_button": True,
                    "allow_multiple_devices": True
                }
            }
            
            if params.get("start_time"):
                body["start_time"] = params["start_time"]
            
            return body
        
        # Handle user creation
        if "create_user" in operation:
            return {
                "action": "create",
                "user_info": {
                    "email": params.get("email"),
                    "type": params.get("type", 1),
                    "first_name": params.get("first_name"),
                    "last_name": params.get("last_name"),
                    "password": params.get("password", "")
                }
            }
        
        # Handle registrant addition
        if "add_meeting_registrant" in operation or "add_webinar_registrant" in operation:
            return {
                "email": params.get("email"),
                "first_name": params.get("first_name"),
                "last_name": params.get("last_name")
            }
        
        # Handle panelist addition
        if "add_webinar_panelists" in operation:
            return {
                "panelists": params.get("panelists", [])
            }
        
        # Handle status updates
        if "update_participant_status" in operation:
            return {
                "action": params.get("action")
            }
        
        # Handle status updates for registrants
        if "update_registrant_status" in operation or "update_webinar_registrant_status" in operation:
            return {
                "action": params.get("action", "approve"),
                "registrants": params.get("registrants", [])
            }
        
        # Handle meeting status updates
        if "update_meeting_status" in operation or "update_webinar_status" in operation:
            return {
                "action": params.get("action")
            }
        
        # Handle SMS sending
        if "send_sms" in operation:
            return {
                "to": params.get("to"),
                "message": params.get("message")
            }
        
        # Handle poll creation
        if "create_meeting_poll" in operation:
            return params.get("poll_data", {})
        
        # Handle recording recovery
        if "recover_meeting_recordings" in operation:
            return {
                "action": "recover"
            }
        
        return None

    async def _process_result(self, result: Dict[str, Any], params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Process result from UniversalRequestNode for Zoom-specific outputs."""
        if result.get("status") != "success":
            return result
        
        response_data = result.get("result", {})
        
        # Extract Zoom-specific fields
        meeting_id = None
        webinar_id = None
        join_url = None
        start_url = None
        participant_count = None
        registration_url = None
        
        if isinstance(response_data, dict):
            meeting_id = response_data.get("id") or response_data.get("meeting_id")
            webinar_id = response_data.get("id") if "webinar" in operation else None
            join_url = response_data.get("join_url")
            start_url = response_data.get("start_url")
            registration_url = response_data.get("registration_url")
            
            # Extract participant count from various response formats
            if response_data.get("participants"):
                participant_count = len(response_data["participants"])
            elif response_data.get("page_count"):
                participant_count = response_data.get("total_records")
        
        return {
            "status": result.get("status"),
            "result": response_data,
            "error": result.get("error"),
            "status_code": result.get("status_code"),
            "response_headers": result.get("response_headers"),
            "meeting_id": meeting_id,
            "webinar_id": webinar_id,
            "join_url": join_url,
            "start_url": start_url,
            "participant_count": participant_count,
            "registration_url": registration_url
        }


# Helper class for creating Zoom API request objects
class ZoomHelpers:
    """Helper functions for creating Zoom API request objects."""
    
    @staticmethod
    def create_meeting_settings(
        host_video: bool = True,
        participant_video: bool = True,
        join_before_host: bool = True,
        mute_upon_entry: bool = True,
        audio: str = "both",
        auto_recording: str = "none",
        approval_type: int = 2
    ) -> Dict[str, Any]:
        """Create meeting settings object."""
        return {
            "host_video": host_video,
            "participant_video": participant_video,
            "cn_meeting": False,
            "in_meeting": False,
            "join_before_host": join_before_host,
            "mute_upon_entry": mute_upon_entry,
            "watermark": False,
            "use_pmi": False,
            "approval_type": approval_type,
            "registration_type": 1,
            "audio": audio,
            "auto_recording": auto_recording
        }
    
    @staticmethod
    def create_webinar_settings(
        host_video: bool = True,
        panelists_video: bool = True,
        practice_session: bool = False,
        hd_video: bool = True,
        approval_type: int = 0,
        audio: str = "both",
        auto_recording: str = "none"
    ) -> Dict[str, Any]:
        """Create webinar settings object."""
        return {
            "host_video": host_video,
            "panelists_video": panelists_video,
            "practice_session": practice_session,
            "hd_video": hd_video,
            "approval_type": approval_type,
            "registration_type": 1,
            "audio": audio,
            "auto_recording": auto_recording,
            "show_share_button": True,
            "allow_multiple_devices": True
        }
    
    @staticmethod
    def create_user_info(
        email: str,
        first_name: str,
        last_name: str,
        user_type: int = 1,
        password: str = ""
    ) -> Dict[str, Any]:
        """Create user info object."""
        return {
            "email": email,
            "type": user_type,
            "first_name": first_name,
            "last_name": last_name,
            "password": password
        }
    
    @staticmethod
    def create_panelist(email: str, name: str) -> Dict[str, str]:
        """Create panelist object."""
        return {
            "email": email,
            "name": name
        }


# Register with NodeRegistry if available
if __name__ == "__main__":
    import asyncio
    
    async def test_zoom_node():
        """Test the Zoom node with sample operations."""
        node = ZoomNode()
        
        # Test schema
        schema = node.get_schema()
        print(f"Zoom Node Schema: {schema.node_type} v{schema.version}")
        print(f"Available operations: {len(node.OPERATIONS)}")
        print(f"Sample operations: {list(node.OPERATIONS.keys())[:10]}...")
        
        print("Zoom Node unified implementation ready!")
    
    asyncio.run(test_zoom_node())

try:
    from node_registry import NodeRegistry
    registry = NodeRegistry()
    registry.register("zoom", ZoomNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register ZoomNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")