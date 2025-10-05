"""
Twilio Node - Comprehensive Twilio integration for SMS/voice communications
Refactored with improved architecture: dispatch maps, unified async/sync handling,
proper connection lifecycle, and standardized return shapes.
Supports all major Twilio operations including SMS, voice calls, phone numbers,
recordings, conferences, video, and advanced communication features.
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime, timezone
from contextlib import asynccontextmanager

try:
    from twilio.rest import Client as TwilioClient
    from twilio.base.exceptions import TwilioException
    from twilio.twiml.voice_response import VoiceResponse
    from twilio.twiml.messaging_response import MessagingResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    TwilioClient = None  # Fallback for type hints
    TwilioException = Exception
    VoiceResponse = None
    MessagingResponse = None

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

# Configure logging with proper masking
logger = logging.getLogger(__name__)

class TwilioOperation:
    """All available Twilio operations."""
    
    # SMS/Messaging Operations
    SEND_SMS = "send_sms"
    SEND_MMS = "send_mms"
    LIST_MESSAGES = "list_messages"
    GET_MESSAGE = "get_message"
    DELETE_MESSAGE = "delete_message"
    UPDATE_MESSAGE = "update_message"
    
    # Voice Call Operations
    MAKE_CALL = "make_call"
    LIST_CALLS = "list_calls"
    GET_CALL = "get_call"
    UPDATE_CALL = "update_call"
    DELETE_CALL = "delete_call"
    
    # Recording Operations
    LIST_RECORDINGS = "list_recordings"
    GET_RECORDING = "get_recording"
    DELETE_RECORDING = "delete_recording"
    
    # Conference Operations
    LIST_CONFERENCES = "list_conferences"
    GET_CONFERENCE = "get_conference"
    UPDATE_CONFERENCE = "update_conference"
    LIST_CONFERENCE_PARTICIPANTS = "list_conference_participants"
    GET_CONFERENCE_PARTICIPANT = "get_conference_participant"
    UPDATE_CONFERENCE_PARTICIPANT = "update_conference_participant"
    DELETE_CONFERENCE_PARTICIPANT = "delete_conference_participant"
    
    # Phone Number Operations
    LIST_PHONE_NUMBERS = "list_phone_numbers"
    GET_PHONE_NUMBER = "get_phone_number"
    UPDATE_PHONE_NUMBER = "update_phone_number"
    DELETE_PHONE_NUMBER = "delete_phone_number"
    SEARCH_AVAILABLE_PHONE_NUMBERS = "search_available_phone_numbers"
    PURCHASE_PHONE_NUMBER = "purchase_phone_number"
    
    # Account Operations
    GET_ACCOUNT = "get_account"
    UPDATE_ACCOUNT = "update_account"
    LIST_SUBACCOUNTS = "list_subaccounts"
    CREATE_SUBACCOUNT = "create_subaccount"
    GET_BALANCE = "get_balance"
    LIST_USAGE = "list_usage"
    
    # Lookup Operations
    LOOKUP_PHONE_NUMBER = "lookup_phone_number"
    CARRIER_LOOKUP = "carrier_lookup"
    
    # Verification (Verify API)
    START_VERIFICATION = "start_verification"
    CHECK_VERIFICATION = "check_verification"
    
    # TwiML Generation
    GENERATE_VOICE_TWIML = "generate_voice_twiml"
    GENERATE_MESSAGING_TWIML = "generate_messaging_twiml"
    
    # Queue Operations
    LIST_QUEUES = "list_queues"
    GET_QUEUE = "get_queue"
    CREATE_QUEUE = "create_queue"
    UPDATE_QUEUE = "update_queue"
    DELETE_QUEUE = "delete_queue"
    
    # Application Operations
    LIST_APPLICATIONS = "list_applications"
    GET_APPLICATION = "get_application"
    CREATE_APPLICATION = "create_application"
    UPDATE_APPLICATION = "update_application"
    DELETE_APPLICATION = "delete_application"
    
    # SIP Operations
    LIST_SIP_DOMAINS = "list_sip_domains"
    GET_SIP_DOMAIN = "get_sip_domain"
    CREATE_SIP_DOMAIN = "create_sip_domain"
    UPDATE_SIP_DOMAIN = "update_sip_domain"
    DELETE_SIP_DOMAIN = "delete_sip_domain"
    
    # Webhook Operations
    VALIDATE_WEBHOOK = "validate_webhook"
    
    # Video Operations (if Twilio Video is used)
    CREATE_VIDEO_ROOM = "create_video_room"
    GET_VIDEO_ROOM = "get_video_room"
    LIST_VIDEO_ROOMS = "list_video_rooms"
    UPDATE_VIDEO_ROOM = "update_video_room"


class TwilioClientWrapper:
    """Unified Twilio client wrapper that handles sync/async operations."""
    
    def __init__(self, client: TwilioClient):
        self.client = client
        self.is_async = False  # Twilio Python SDK is synchronous
    
    async def maybe_await(self, result):
        """Helper to handle both sync and async results."""
        if self.is_async and asyncio.iscoroutine(result):
            return await result
        return result
    
    # SMS/Messaging operations
    async def send_message(self, to: str, from_: str, body: str = None, 
                          media_url: List[str] = None, **kwargs) -> Any:
        """Send SMS/MMS message."""
        message_kwargs = {"to": to, "from_": from_}
        if body:
            message_kwargs["body"] = body
        if media_url:
            message_kwargs["media_url"] = media_url
        message_kwargs.update(kwargs)
        
        return await self.maybe_await(self.client.messages.create(**message_kwargs))
    
    async def list_messages(self, **kwargs) -> List[Any]:
        """List messages."""
        return await self.maybe_await(list(self.client.messages.list(**kwargs)))
    
    async def get_message(self, message_sid: str) -> Any:
        """Get specific message."""
        return await self.maybe_await(self.client.messages(message_sid).fetch())
    
    async def delete_message(self, message_sid: str) -> bool:
        """Delete message."""
        await self.maybe_await(self.client.messages(message_sid).delete())
        return True
    
    async def update_message(self, message_sid: str, **kwargs) -> Any:
        """Update message."""
        return await self.maybe_await(self.client.messages(message_sid).update(**kwargs))
    
    # Voice call operations
    async def make_call(self, to: str, from_: str, url: str = None, 
                       twiml: str = None, **kwargs) -> Any:
        """Make a voice call."""
        call_kwargs = {"to": to, "from_": from_}
        if url:
            call_kwargs["url"] = url
        if twiml:
            call_kwargs["twiml"] = twiml
        call_kwargs.update(kwargs)
        
        return await self.maybe_await(self.client.calls.create(**call_kwargs))
    
    async def list_calls(self, **kwargs) -> List[Any]:
        """List calls."""
        return await self.maybe_await(list(self.client.calls.list(**kwargs)))
    
    async def get_call(self, call_sid: str) -> Any:
        """Get specific call."""
        return await self.maybe_await(self.client.calls(call_sid).fetch())
    
    async def update_call(self, call_sid: str, **kwargs) -> Any:
        """Update call."""
        return await self.maybe_await(self.client.calls(call_sid).update(**kwargs))
    
    async def delete_call(self, call_sid: str) -> bool:
        """Delete call record."""
        await self.maybe_await(self.client.calls(call_sid).delete())
        return True
    
    # Recording operations
    async def list_recordings(self, **kwargs) -> List[Any]:
        """List recordings."""
        return await self.maybe_await(list(self.client.recordings.list(**kwargs)))
    
    async def get_recording(self, recording_sid: str) -> Any:
        """Get specific recording."""
        return await self.maybe_await(self.client.recordings(recording_sid).fetch())
    
    async def delete_recording(self, recording_sid: str) -> bool:
        """Delete recording."""
        await self.maybe_await(self.client.recordings(recording_sid).delete())
        return True
    
    # Conference operations
    async def list_conferences(self, **kwargs) -> List[Any]:
        """List conferences."""
        return await self.maybe_await(list(self.client.conferences.list(**kwargs)))
    
    async def get_conference(self, conference_sid: str) -> Any:
        """Get specific conference."""
        return await self.maybe_await(self.client.conferences(conference_sid).fetch())
    
    async def update_conference(self, conference_sid: str, **kwargs) -> Any:
        """Update conference."""
        return await self.maybe_await(self.client.conferences(conference_sid).update(**kwargs))
    
    # Phone number operations
    async def list_phone_numbers(self, **kwargs) -> List[Any]:
        """List incoming phone numbers."""
        return await self.maybe_await(list(self.client.incoming_phone_numbers.list(**kwargs)))
    
    async def get_phone_number(self, phone_number_sid: str) -> Any:
        """Get specific phone number."""
        return await self.maybe_await(self.client.incoming_phone_numbers(phone_number_sid).fetch())
    
    async def update_phone_number(self, phone_number_sid: str, **kwargs) -> Any:
        """Update phone number."""
        return await self.maybe_await(self.client.incoming_phone_numbers(phone_number_sid).update(**kwargs))
    
    async def delete_phone_number(self, phone_number_sid: str) -> bool:
        """Delete phone number."""
        await self.maybe_await(self.client.incoming_phone_numbers(phone_number_sid).delete())
        return True
    
    async def search_available_phone_numbers(self, country_code: str, **kwargs) -> List[Any]:
        """Search available phone numbers."""
        return await self.maybe_await(
            list(self.client.available_phone_numbers(country_code).local.list(**kwargs))
        )
    
    async def purchase_phone_number(self, phone_number: str, **kwargs) -> Any:
        """Purchase phone number."""
        return await self.maybe_await(
            self.client.incoming_phone_numbers.create(phone_number=phone_number, **kwargs)
        )
    
    # Account operations
    async def get_account(self) -> Any:
        """Get account information."""
        return await self.maybe_await(self.client.api.accounts(self.client.account_sid).fetch())
    
    async def update_account(self, **kwargs) -> Any:
        """Update account."""
        return await self.maybe_await(self.client.api.accounts(self.client.account_sid).update(**kwargs))
    
    async def list_subaccounts(self, **kwargs) -> List[Any]:
        """List subaccounts."""
        return await self.maybe_await(list(self.client.api.accounts.list(**kwargs)))
    
    async def create_subaccount(self, **kwargs) -> Any:
        """Create subaccount."""
        return await self.maybe_await(self.client.api.accounts.create(**kwargs))
    
    async def get_balance(self) -> Any:
        """Get account balance."""
        return await self.maybe_await(self.client.balance.fetch())
    
    # Lookup operations
    async def lookup_phone_number(self, phone_number: str, **kwargs) -> Any:
        """Lookup phone number information."""
        return await self.maybe_await(self.client.lookups.phone_numbers(phone_number).fetch(**kwargs))
    
    # Verification operations
    async def start_verification(self, to: str, channel: str = "sms", **kwargs) -> Any:
        """Start verification process."""
        return await self.maybe_await(
            self.client.verify.services(kwargs.get("verify_service_sid")).verifications.create(
                to=to, channel=channel
            )
        )
    
    async def check_verification(self, to: str, code: str, **kwargs) -> Any:
        """Check verification code."""
        return await self.maybe_await(
            self.client.verify.services(kwargs.get("verify_service_sid")).verification_checks.create(
                to=to, code=code
            )
        )


class OperationMetadata:
    """Metadata for operation validation and parameter requirements."""
    
    def __init__(self, required_params: List[str], optional_params: List[str] = None, 
                 handler: Optional[Callable] = None):
        self.required_params = required_params
        self.optional_params = optional_params or []
        self.handler = handler


class TwilioNode(BaseNode):
    """
    Comprehensive Twilio integration node supporting all major communication operations.
    Handles SMS, voice calls, phone numbers, recordings, conferences, verification,
    and advanced Twilio features.
    """
    
    # Operation metadata table - programmatic validation generation
    OPERATION_METADATA = {
        # SMS/Messaging operations
        TwilioOperation.SEND_SMS: OperationMetadata(["to", "from_", "body"]),
        TwilioOperation.SEND_MMS: OperationMetadata(["to", "from_"], ["body", "media_url"]),
        TwilioOperation.LIST_MESSAGES: OperationMetadata([]),
        TwilioOperation.GET_MESSAGE: OperationMetadata(["message_sid"]),
        TwilioOperation.DELETE_MESSAGE: OperationMetadata(["message_sid"]),
        TwilioOperation.UPDATE_MESSAGE: OperationMetadata(["message_sid"]),
        
        # Voice call operations
        TwilioOperation.MAKE_CALL: OperationMetadata(["to", "from_"], ["url", "twiml"]),
        TwilioOperation.LIST_CALLS: OperationMetadata([]),
        TwilioOperation.GET_CALL: OperationMetadata(["call_sid"]),
        TwilioOperation.UPDATE_CALL: OperationMetadata(["call_sid"]),
        TwilioOperation.DELETE_CALL: OperationMetadata(["call_sid"]),
        
        # Recording operations
        TwilioOperation.LIST_RECORDINGS: OperationMetadata([]),
        TwilioOperation.GET_RECORDING: OperationMetadata(["recording_sid"]),
        TwilioOperation.DELETE_RECORDING: OperationMetadata(["recording_sid"]),
        
        # Conference operations
        TwilioOperation.LIST_CONFERENCES: OperationMetadata([]),
        TwilioOperation.GET_CONFERENCE: OperationMetadata(["conference_sid"]),
        TwilioOperation.UPDATE_CONFERENCE: OperationMetadata(["conference_sid"]),
        
        # Phone number operations
        TwilioOperation.LIST_PHONE_NUMBERS: OperationMetadata([]),
        TwilioOperation.GET_PHONE_NUMBER: OperationMetadata(["phone_number_sid"]),
        TwilioOperation.UPDATE_PHONE_NUMBER: OperationMetadata(["phone_number_sid"]),
        TwilioOperation.DELETE_PHONE_NUMBER: OperationMetadata(["phone_number_sid"]),
        TwilioOperation.SEARCH_AVAILABLE_PHONE_NUMBERS: OperationMetadata(["country_code"]),
        TwilioOperation.PURCHASE_PHONE_NUMBER: OperationMetadata(["phone_number"]),
        
        # Account operations
        TwilioOperation.GET_ACCOUNT: OperationMetadata([]),
        TwilioOperation.UPDATE_ACCOUNT: OperationMetadata([]),
        TwilioOperation.LIST_SUBACCOUNTS: OperationMetadata([]),
        TwilioOperation.CREATE_SUBACCOUNT: OperationMetadata([]),
        TwilioOperation.GET_BALANCE: OperationMetadata([]),
        
        # Lookup operations
        TwilioOperation.LOOKUP_PHONE_NUMBER: OperationMetadata(["phone_number"]),
        
        # Verification operations
        TwilioOperation.START_VERIFICATION: OperationMetadata(["to", "verify_service_sid"]),
        TwilioOperation.CHECK_VERIFICATION: OperationMetadata(["to", "code", "verify_service_sid"]),
        
        # TwiML generation
        TwilioOperation.GENERATE_VOICE_TWIML: OperationMetadata(["actions"]),
        TwilioOperation.GENERATE_MESSAGING_TWIML: OperationMetadata(["actions"]),
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create dispatch map for operations
        self.operation_dispatch = {
            # SMS/Messaging operations
            TwilioOperation.SEND_SMS: self._handle_send_sms,
            TwilioOperation.SEND_MMS: self._handle_send_mms,
            TwilioOperation.LIST_MESSAGES: self._handle_list_messages,
            TwilioOperation.GET_MESSAGE: self._handle_get_message,
            TwilioOperation.DELETE_MESSAGE: self._handle_delete_message,
            TwilioOperation.UPDATE_MESSAGE: self._handle_update_message,
            
            # Voice call operations
            TwilioOperation.MAKE_CALL: self._handle_make_call,
            TwilioOperation.LIST_CALLS: self._handle_list_calls,
            TwilioOperation.GET_CALL: self._handle_get_call,
            TwilioOperation.UPDATE_CALL: self._handle_update_call,
            TwilioOperation.DELETE_CALL: self._handle_delete_call,
            
            # Recording operations
            TwilioOperation.LIST_RECORDINGS: self._handle_list_recordings,
            TwilioOperation.GET_RECORDING: self._handle_get_recording,
            TwilioOperation.DELETE_RECORDING: self._handle_delete_recording,
            
            # Conference operations
            TwilioOperation.LIST_CONFERENCES: self._handle_list_conferences,
            TwilioOperation.GET_CONFERENCE: self._handle_get_conference,
            TwilioOperation.UPDATE_CONFERENCE: self._handle_update_conference,
            
            # Phone number operations
            TwilioOperation.LIST_PHONE_NUMBERS: self._handle_list_phone_numbers,
            TwilioOperation.GET_PHONE_NUMBER: self._handle_get_phone_number,
            TwilioOperation.UPDATE_PHONE_NUMBER: self._handle_update_phone_number,
            TwilioOperation.DELETE_PHONE_NUMBER: self._handle_delete_phone_number,
            TwilioOperation.SEARCH_AVAILABLE_PHONE_NUMBERS: self._handle_search_available_phone_numbers,
            TwilioOperation.PURCHASE_PHONE_NUMBER: self._handle_purchase_phone_number,
            
            # Account operations
            TwilioOperation.GET_ACCOUNT: self._handle_get_account,
            TwilioOperation.UPDATE_ACCOUNT: self._handle_update_account,
            TwilioOperation.LIST_SUBACCOUNTS: self._handle_list_subaccounts,
            TwilioOperation.CREATE_SUBACCOUNT: self._handle_create_subaccount,
            TwilioOperation.GET_BALANCE: self._handle_get_balance,
            
            # Lookup operations
            TwilioOperation.LOOKUP_PHONE_NUMBER: self._handle_lookup_phone_number,
            
            # Verification operations
            TwilioOperation.START_VERIFICATION: self._handle_start_verification,
            TwilioOperation.CHECK_VERIFICATION: self._handle_check_verification,
            
            # TwiML generation
            TwilioOperation.GENERATE_VOICE_TWIML: self._handle_generate_voice_twiml,
            TwilioOperation.GENERATE_MESSAGING_TWIML: self._handle_generate_messaging_twiml,
        }
    
    def get_schema(self) -> NodeSchema:
        """Generate schema with all parameters from operation metadata."""
        # Common parameters for all operations
        base_params = [
            ("operation", NodeParameterType.STRING, "Twilio operation to perform", True, list(self.OPERATION_METADATA.keys())),
            ("account_sid", NodeParameterType.STRING, "Twilio Account SID", True),
            ("auth_token", NodeParameterType.STRING, "Twilio Auth Token", True),
            ("region", NodeParameterType.STRING, "Twilio region", False),
            ("edge", NodeParameterType.STRING, "Twilio edge location", False),
        ]
        
        # Operation-specific parameters
        operation_params = [
            # SMS/MMS parameters
            ("to", NodeParameterType.STRING, "Recipient phone number in E.164 format", False),
            ("from_", NodeParameterType.STRING, "Sender phone number (your Twilio number)", False),
            ("body", NodeParameterType.STRING, "Message body text", False),
            ("media_url", NodeParameterType.ARRAY, "Media URLs for MMS (array of strings)", False),
            ("message_sid", NodeParameterType.STRING, "Message SID for specific message operations", False),
            
            # Voice call parameters
            ("url", NodeParameterType.STRING, "TwiML URL for call instructions", False),
            ("twiml", NodeParameterType.STRING, "TwiML content for call instructions", False),
            ("call_sid", NodeParameterType.STRING, "Call SID for specific call operations", False),
            ("timeout", NodeParameterType.NUMBER, "Call timeout in seconds", False),
            ("record", NodeParameterType.BOOLEAN, "Record the call", False),
            ("recording_status_callback", NodeParameterType.STRING, "Recording status callback URL", False),
            
            # Recording parameters
            ("recording_sid", NodeParameterType.STRING, "Recording SID for specific recording operations", False),
            
            # Conference parameters
            ("conference_sid", NodeParameterType.STRING, "Conference SID for specific conference operations", False),
            ("participant_sid", NodeParameterType.STRING, "Participant SID for conference participant operations", False),
            ("status", NodeParameterType.STRING, "Conference or participant status", False),
            
            # Phone number parameters
            ("phone_number_sid", NodeParameterType.STRING, "Phone number SID for specific phone number operations", False),
            ("phone_number", NodeParameterType.STRING, "Phone number in E.164 format", False),
            ("country_code", NodeParameterType.STRING, "Two-letter country code (e.g., US, GB)", False),
            ("area_code", NodeParameterType.STRING, "Area code for phone number search", False),
            ("friendly_name", NodeParameterType.STRING, "Friendly name for phone number", False),
            
            # Account parameters
            ("subaccount_sid", NodeParameterType.STRING, "Subaccount SID", False),
            
            # Verification parameters
            ("verify_service_sid", NodeParameterType.STRING, "Verify Service SID", False),
            ("channel", NodeParameterType.STRING, "Verification channel (sms, call, email)", False, ["sms", "call", "email"]),
            ("code", NodeParameterType.STRING, "Verification code to check", False),
            
            # TwiML generation parameters
            ("actions", NodeParameterType.ARRAY, "Array of TwiML actions to generate", False),
            
            # Filter parameters
            ("limit", NodeParameterType.NUMBER, "Maximum number of results to return", False),
            ("page_size", NodeParameterType.NUMBER, "Page size for pagination", False),
            ("date_created_after", NodeParameterType.STRING, "Filter by creation date (ISO format)", False),
            ("date_created_before", NodeParameterType.STRING, "Filter by creation date (ISO format)", False),
            
            # Lookup parameters
            ("type", NodeParameterType.ARRAY, "Lookup information types", False),
            ("country_code_lookup", NodeParameterType.STRING, "Country code for lookup", False),
        ]
        
        # Build parameters dict
        parameters = {}
        for param_def in base_params + operation_params:
            name = param_def[0]
            param_type = param_def[1]
            description = param_def[2]
            required = param_def[3]
            enum = param_def[4] if len(param_def) > 4 else None
            default = param_def[5] if len(param_def) > 5 else None
            
            param_kwargs = {
                "name": name,
                "type": param_type,
                "description": description,
                "required": required
            }
            
            if enum:
                param_kwargs["enum"] = enum
            if default is not None:
                param_kwargs["default"] = default
            
            parameters[name] = NodeParameter(**param_kwargs)
        
        return NodeSchema(
            node_type="twilio",
            version="1.0.0",
            description="Comprehensive Twilio integration supporting all major communication operations including SMS, voice calls, phone numbers, recordings, conferences, verification, and advanced Twilio features",
            parameters=list(parameters.values()),
            outputs={
                "status": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "start_time": NodeParameterType.STRING,
                "execution_time": NodeParameterType.NUMBER,
                "inputs": NodeParameterType.OBJECT,
                "raw_result": NodeParameterType.ANY,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "twilio_error": NodeParameterType.STRING,
                "connection_info": NodeParameterType.OBJECT,
                "message_sid": NodeParameterType.STRING,
                "call_sid": NodeParameterType.STRING,
                "recording_sid": NodeParameterType.STRING,
                "conference_sid": NodeParameterType.STRING,
                "phone_number_sid": NodeParameterType.STRING,
                "account_sid": NodeParameterType.STRING,
                "balance": NodeParameterType.STRING,
                "status_result": NodeParameterType.STRING,
                "verification_status": NodeParameterType.STRING,
                "twiml": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Twilio-specific parameters using operation metadata."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Basic validation
        if not operation:
            raise NodeValidationError("Operation is required")
        
        if operation not in self.OPERATION_METADATA:
            raise NodeValidationError(f"Invalid operation: {operation}")
        
        # Authentication validation
        account_sid = params.get("account_sid")
        auth_token = params.get("auth_token")
        
        if not account_sid:
            raise NodeValidationError("account_sid is required")
        if not auth_token:
            raise NodeValidationError("auth_token is required")
        
        # Operation-specific validation using metadata
        metadata = self.OPERATION_METADATA[operation]
        
        # Check required parameters
        for param in metadata.required_params:
            if param not in params or params[param] is None:
                raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")
        
        # Additional validation for specific operations
        if operation in [TwilioOperation.SEND_SMS, TwilioOperation.SEND_MMS, TwilioOperation.MAKE_CALL]:
            to = params.get("to")
            from_ = params.get("from_")
            if to and not to.startswith("+"):
                raise NodeValidationError("'to' number must be in E.164 format (start with +)")
            if from_ and not from_.startswith("+"):
                raise NodeValidationError("'from_' number must be in E.164 format (start with +)")
        
        if operation == TwilioOperation.SEND_MMS and "media_url" in params:
            if not isinstance(params["media_url"], list):
                raise NodeValidationError("media_url must be an array")
        
        if operation in [TwilioOperation.GENERATE_VOICE_TWIML, TwilioOperation.GENERATE_MESSAGING_TWIML]:
            if "actions" in params and not isinstance(params["actions"], list):
                raise NodeValidationError("actions must be an array")
        
        return node_data
    
    @asynccontextmanager
    async def _get_twilio_client(self, params: Dict[str, Any]):
        """Context manager for Twilio client with proper connection lifecycle."""
        account_sid = params.get("account_sid")
        auth_token = params.get("auth_token")
        region = params.get("region")
        edge = params.get("edge")
        
        client = None
        try:
            client = TwilioClient(account_sid, auth_token, region=region, edge=edge)
            twilio_client = TwilioClientWrapper(client)
            yield twilio_client
        finally:
            # Twilio client doesn't need explicit closing
            pass
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in parameters for logging."""
        masked_data = data.copy()
        
        # Mask sensitive fields
        sensitive_fields = ["auth_token", "api_key", "api_secret"]
        for field in sensitive_fields:
            if field in masked_data:
                masked_data[field] = "***MASKED***"
        
        return masked_data
    
    def _create_standard_response(self, operation: str, start_time: datetime, 
                                 params: Dict[str, Any], result: Any, 
                                 error: Optional[str] = None, 
                                 twilio_error: Optional[str] = None) -> Dict[str, Any]:
        """Create standardized response shape."""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        response = {
            "status": "success" if error is None else "error",
            "operation": operation,
            "start_time": start_time.isoformat(),
            "execution_time": execution_time,
            "inputs": self._mask_sensitive_data(params),
            "raw_result": result,
            "result": result,
        }
        
        if error:
            response["error"] = error
        
        if twilio_error:
            response["twilio_error"] = twilio_error
        
        # Add connection info (without sensitive data)
        response["connection_info"] = {
            "account_sid": params.get("account_sid"),
            "region": params.get("region"),
            "edge": params.get("edge"),
        }
        
        return response
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Twilio operation using dispatch map."""
        start_time = datetime.now()
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Get handler from dispatch map
        handler = self.operation_dispatch.get(operation)
        if not handler:
            return self._create_standard_response(
                operation, start_time, params, None,
                error=f"Unknown operation: {operation}"
            )
        
        try:
            # Create Twilio client with proper connection lifecycle
            async with self._get_twilio_client(params) as twilio_client:
                # Call the handler
                result = await handler(twilio_client, params)
                
                return self._create_standard_response(
                    operation, start_time, params, result
                )
        
        except TwilioException as e:
            error_type = type(e).__name__
            return self._create_standard_response(
                operation, start_time, params, None,
                error=str(e), twilio_error=error_type
            )
        except Exception as e:
            logger.error(f"Unexpected error in operation {operation}: {e}")
            return self._create_standard_response(
                operation, start_time, params, None,
                error=str(e), twilio_error=type(e).__name__
            )
    
    # SMS/Messaging operation handlers
    async def _handle_send_sms(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle SEND_SMS operation."""
        return await twilio_client.send_message(
            to=params["to"],
            from_=params["from_"],
            body=params["body"]
        )
    
    async def _handle_send_mms(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle SEND_MMS operation."""
        return await twilio_client.send_message(
            to=params["to"],
            from_=params["from_"],
            body=params.get("body"),
            media_url=params.get("media_url", [])
        )
    
    async def _handle_list_messages(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> List[Any]:
        """Handle LIST_MESSAGES operation."""
        filter_params = {}
        if params.get("limit"):
            filter_params["limit"] = params["limit"]
        if params.get("date_created_after"):
            filter_params["date_created_after"] = params["date_created_after"]
        if params.get("date_created_before"):
            filter_params["date_created_before"] = params["date_created_before"]
        
        return await twilio_client.list_messages(**filter_params)
    
    async def _handle_get_message(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle GET_MESSAGE operation."""
        return await twilio_client.get_message(params["message_sid"])
    
    async def _handle_delete_message(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DELETE_MESSAGE operation."""
        return await twilio_client.delete_message(params["message_sid"])
    
    async def _handle_update_message(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle UPDATE_MESSAGE operation."""
        update_params = {k: v for k, v in params.items() if k not in ["operation", "message_sid", "account_sid", "auth_token"]}
        return await twilio_client.update_message(params["message_sid"], **update_params)
    
    # Voice call operation handlers
    async def _handle_make_call(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle MAKE_CALL operation."""
        call_params = {}
        if params.get("url"):
            call_params["url"] = params["url"]
        if params.get("twiml"):
            call_params["twiml"] = params["twiml"]
        if params.get("timeout"):
            call_params["timeout"] = params["timeout"]
        if params.get("record"):
            call_params["record"] = params["record"]
        if params.get("recording_status_callback"):
            call_params["recording_status_callback"] = params["recording_status_callback"]
        
        return await twilio_client.make_call(
            to=params["to"],
            from_=params["from_"],
            **call_params
        )
    
    async def _handle_list_calls(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> List[Any]:
        """Handle LIST_CALLS operation."""
        filter_params = {}
        if params.get("limit"):
            filter_params["limit"] = params["limit"]
        if params.get("status"):
            filter_params["status"] = params["status"]
        if params.get("date_created_after"):
            filter_params["start_time_after"] = params["date_created_after"]
        if params.get("date_created_before"):
            filter_params["start_time_before"] = params["date_created_before"]
        
        return await twilio_client.list_calls(**filter_params)
    
    async def _handle_get_call(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle GET_CALL operation."""
        return await twilio_client.get_call(params["call_sid"])
    
    async def _handle_update_call(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle UPDATE_CALL operation."""
        update_params = {k: v for k, v in params.items() if k not in ["operation", "call_sid", "account_sid", "auth_token"]}
        return await twilio_client.update_call(params["call_sid"], **update_params)
    
    async def _handle_delete_call(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DELETE_CALL operation."""
        return await twilio_client.delete_call(params["call_sid"])
    
    # Recording operation handlers
    async def _handle_list_recordings(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> List[Any]:
        """Handle LIST_RECORDINGS operation."""
        filter_params = {}
        if params.get("limit"):
            filter_params["limit"] = params["limit"]
        if params.get("call_sid"):
            filter_params["call_sid"] = params["call_sid"]
        if params.get("date_created_after"):
            filter_params["date_created_after"] = params["date_created_after"]
        if params.get("date_created_before"):
            filter_params["date_created_before"] = params["date_created_before"]
        
        return await twilio_client.list_recordings(**filter_params)
    
    async def _handle_get_recording(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle GET_RECORDING operation."""
        return await twilio_client.get_recording(params["recording_sid"])
    
    async def _handle_delete_recording(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DELETE_RECORDING operation."""
        return await twilio_client.delete_recording(params["recording_sid"])
    
    # Conference operation handlers
    async def _handle_list_conferences(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> List[Any]:
        """Handle LIST_CONFERENCES operation."""
        filter_params = {}
        if params.get("limit"):
            filter_params["limit"] = params["limit"]
        if params.get("status"):
            filter_params["status"] = params["status"]
        if params.get("date_created_after"):
            filter_params["date_created_after"] = params["date_created_after"]
        if params.get("date_created_before"):
            filter_params["date_created_before"] = params["date_created_before"]
        
        return await twilio_client.list_conferences(**filter_params)
    
    async def _handle_get_conference(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle GET_CONFERENCE operation."""
        return await twilio_client.get_conference(params["conference_sid"])
    
    async def _handle_update_conference(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle UPDATE_CONFERENCE operation."""
        update_params = {k: v for k, v in params.items() if k not in ["operation", "conference_sid", "account_sid", "auth_token"]}
        return await twilio_client.update_conference(params["conference_sid"], **update_params)
    
    # Phone number operation handlers
    async def _handle_list_phone_numbers(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> List[Any]:
        """Handle LIST_PHONE_NUMBERS operation."""
        filter_params = {}
        if params.get("limit"):
            filter_params["limit"] = params["limit"]
        if params.get("friendly_name"):
            filter_params["friendly_name"] = params["friendly_name"]
        
        return await twilio_client.list_phone_numbers(**filter_params)
    
    async def _handle_get_phone_number(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle GET_PHONE_NUMBER operation."""
        return await twilio_client.get_phone_number(params["phone_number_sid"])
    
    async def _handle_update_phone_number(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle UPDATE_PHONE_NUMBER operation."""
        update_params = {k: v for k, v in params.items() if k not in ["operation", "phone_number_sid", "account_sid", "auth_token"]}
        return await twilio_client.update_phone_number(params["phone_number_sid"], **update_params)
    
    async def _handle_delete_phone_number(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DELETE_PHONE_NUMBER operation."""
        return await twilio_client.delete_phone_number(params["phone_number_sid"])
    
    async def _handle_search_available_phone_numbers(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> List[Any]:
        """Handle SEARCH_AVAILABLE_PHONE_NUMBERS operation."""
        search_params = {}
        if params.get("area_code"):
            search_params["area_code"] = params["area_code"]
        if params.get("limit"):
            search_params["limit"] = params["limit"]
        
        return await twilio_client.search_available_phone_numbers(params["country_code"], **search_params)
    
    async def _handle_purchase_phone_number(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle PURCHASE_PHONE_NUMBER operation."""
        purchase_params = {}
        if params.get("friendly_name"):
            purchase_params["friendly_name"] = params["friendly_name"]
        
        return await twilio_client.purchase_phone_number(params["phone_number"], **purchase_params)
    
    # Account operation handlers
    async def _handle_get_account(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle GET_ACCOUNT operation."""
        return await twilio_client.get_account()
    
    async def _handle_update_account(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle UPDATE_ACCOUNT operation."""
        update_params = {k: v for k, v in params.items() if k not in ["operation", "account_sid", "auth_token"]}
        return await twilio_client.update_account(**update_params)
    
    async def _handle_list_subaccounts(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> List[Any]:
        """Handle LIST_SUBACCOUNTS operation."""
        filter_params = {}
        if params.get("limit"):
            filter_params["limit"] = params["limit"]
        
        return await twilio_client.list_subaccounts(**filter_params)
    
    async def _handle_create_subaccount(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle CREATE_SUBACCOUNT operation."""
        create_params = {k: v for k, v in params.items() if k not in ["operation", "account_sid", "auth_token"]}
        return await twilio_client.create_subaccount(**create_params)
    
    async def _handle_get_balance(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle GET_BALANCE operation."""
        return await twilio_client.get_balance()
    
    # Lookup operation handlers
    async def _handle_lookup_phone_number(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle LOOKUP_PHONE_NUMBER operation."""
        lookup_params = {}
        if params.get("type"):
            lookup_params["type"] = params["type"]
        if params.get("country_code_lookup"):
            lookup_params["country_code"] = params["country_code_lookup"]
        
        return await twilio_client.lookup_phone_number(params["phone_number"], **lookup_params)
    
    # Verification operation handlers
    async def _handle_start_verification(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle START_VERIFICATION operation."""
        return await twilio_client.start_verification(
            to=params["to"],
            channel=params.get("channel", "sms"),
            verify_service_sid=params["verify_service_sid"]
        )
    
    async def _handle_check_verification(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> Any:
        """Handle CHECK_VERIFICATION operation."""
        return await twilio_client.check_verification(
            to=params["to"],
            code=params["code"],
            verify_service_sid=params["verify_service_sid"]
        )
    
    # TwiML generation handlers
    async def _handle_generate_voice_twiml(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> str:
        """Handle GENERATE_VOICE_TWIML operation."""
        response = VoiceResponse()
        
        for action in params["actions"]:
            action_type = action.get("type")
            if action_type == "say":
                response.say(action.get("text", ""))
            elif action_type == "play":
                response.play(action.get("url", ""))
            elif action_type == "gather":
                gather = response.gather(
                    num_digits=action.get("num_digits", 1),
                    timeout=action.get("timeout", 5),
                    action=action.get("action", "")
                )
                if action.get("say"):
                    gather.say(action["say"])
            elif action_type == "dial":
                response.dial(action.get("number", ""))
            elif action_type == "hangup":
                response.hangup()
        
        return str(response)
    
    async def _handle_generate_messaging_twiml(self, twilio_client: TwilioClientWrapper, params: Dict[str, Any]) -> str:
        """Handle GENERATE_MESSAGING_TWIML operation."""
        response = MessagingResponse()
        
        for action in params["actions"]:
            action_type = action.get("type")
            if action_type == "message":
                msg = response.message(action.get("body", ""))
                if action.get("media"):
                    msg.media(action["media"])
            elif action_type == "redirect":
                response.redirect(action.get("url", ""))
        
        return str(response)