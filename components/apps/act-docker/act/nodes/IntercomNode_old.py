"""
Intercom Node - Comprehensive integration with Intercom REST API
Provides access to all Intercom API operations including conversations, contacts, companies, articles, admins, and webhooks.
"""

import logging
import json
import asyncio
import time
import os
import ssl
import base64
import hashlib
import hmac
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

class IntercomOperation:
    """Operations available on Intercom REST API."""
    
    # Authentication
    GET_ACCESS_TOKEN = "get_access_token"
    
    # Conversations API
    LIST_CONVERSATIONS = "list_conversations"
    GET_CONVERSATION = "get_conversation"
    CREATE_CONVERSATION = "create_conversation"
    UPDATE_CONVERSATION = "update_conversation"
    REPLY_TO_CONVERSATION = "reply_to_conversation"
    CLOSE_CONVERSATION = "close_conversation"
    OPEN_CONVERSATION = "open_conversation"
    ASSIGN_CONVERSATION = "assign_conversation"
    SNOOZE_CONVERSATION = "snooze_conversation"
    TAG_CONVERSATION = "tag_conversation"
    UNTAG_CONVERSATION = "untag_conversation"
    
    # Contacts API
    LIST_CONTACTS = "list_contacts"
    GET_CONTACT = "get_contact"
    CREATE_CONTACT = "create_contact"
    UPDATE_CONTACT = "update_contact"
    DELETE_CONTACT = "delete_contact"
    MERGE_CONTACTS = "merge_contacts"
    SEARCH_CONTACTS = "search_contacts"
    TAG_CONTACT = "tag_contact"
    UNTAG_CONTACT = "untag_contact"
    
    # Companies API
    LIST_COMPANIES = "list_companies"
    GET_COMPANY = "get_company"
    CREATE_COMPANY = "create_company"
    UPDATE_COMPANY = "update_company"
    DELETE_COMPANY = "delete_company"
    SCROLL_COMPANIES = "scroll_companies"
    LIST_COMPANY_CONTACTS = "list_company_contacts"
    
    # Articles API (Help Center)
    LIST_ARTICLES = "list_articles"
    GET_ARTICLE = "get_article"
    CREATE_ARTICLE = "create_article"
    UPDATE_ARTICLE = "update_article"
    DELETE_ARTICLE = "delete_article"
    SEARCH_ARTICLES = "search_articles"
    
    # Admins/Teammates API
    LIST_ADMINS = "list_admins"
    GET_ADMIN = "get_admin"
    SET_ADMIN_AWAY = "set_admin_away"
    
    # Teams API
    LIST_TEAMS = "list_teams"
    GET_TEAM = "get_team"
    
    # Segments API
    LIST_SEGMENTS = "list_segments"
    GET_SEGMENT = "get_segment"
    
    # Tags API
    LIST_TAGS = "list_tags"
    GET_TAG = "get_tag"
    CREATE_TAG = "create_tag"
    DELETE_TAG = "delete_tag"
    TAG_COMPANIES = "tag_companies"
    UNTAG_COMPANIES = "untag_companies"
    
    # Notes API
    LIST_NOTES = "list_notes"
    GET_NOTE = "get_note"
    CREATE_NOTE = "create_note"
    
    # Events API
    CREATE_EVENT = "create_event"
    LIST_EVENTS = "list_events"
    
    # Data Attributes API
    LIST_DATA_ATTRIBUTES = "list_data_attributes"
    CREATE_DATA_ATTRIBUTE = "create_data_attribute"
    UPDATE_DATA_ATTRIBUTE = "update_data_attribute"
    
    # Subscription Types API
    LIST_SUBSCRIPTION_TYPES = "list_subscription_types"
    
    # Webhooks API
    CREATE_WEBHOOK = "create_webhook"
    GET_WEBHOOK = "get_webhook"
    UPDATE_WEBHOOK = "update_webhook"
    DELETE_WEBHOOK = "delete_webhook"
    LIST_WEBHOOKS = "list_webhooks"
    
    # Visitors API
    GET_VISITOR = "get_visitor"
    UPDATE_VISITOR = "update_visitor"
    CONVERT_VISITOR = "convert_visitor"
    
    # Counts API
    GET_COUNTS = "get_counts"
    
    # Activity Logs API
    LIST_ACTIVITY_LOGS = "list_activity_logs"
    
    # Custom Objects API
    LIST_CUSTOM_OBJECTS = "list_custom_objects"
    GET_CUSTOM_OBJECT = "get_custom_object"
    CREATE_CUSTOM_OBJECT = "create_custom_object"
    UPDATE_CUSTOM_OBJECT = "update_custom_object"
    DELETE_CUSTOM_OBJECT = "delete_custom_object"

class IntercomAuthType:
    """Authentication types for Intercom API."""
    ACCESS_TOKEN = "access_token"
    OAUTH = "oauth"

class IntercomHelper:
    """Helper class for Intercom API operations."""
    
    @staticmethod
    def format_contact_data(contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format contact data for API requests."""
        formatted = {}
        
        # Standard fields
        if 'email' in contact_data:
            formatted['email'] = contact_data['email']
        if 'phone' in contact_data:
            formatted['phone'] = contact_data['phone']
        if 'name' in contact_data:
            formatted['name'] = contact_data['name']
        if 'user_id' in contact_data:
            formatted['user_id'] = contact_data['user_id']
        if 'signed_up_at' in contact_data:
            formatted['signed_up_at'] = contact_data['signed_up_at']
        if 'last_seen_at' in contact_data:
            formatted['last_seen_at'] = contact_data['last_seen_at']
        
        # Custom attributes
        if 'custom_attributes' in contact_data:
            formatted['custom_attributes'] = contact_data['custom_attributes']
            
        return formatted
    
    @staticmethod
    def format_company_data(company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format company data for API requests."""
        formatted = {}
        
        # Standard fields
        if 'company_id' in company_data:
            formatted['company_id'] = company_data['company_id']
        if 'name' in company_data:
            formatted['name'] = company_data['name']
        if 'plan' in company_data:
            formatted['plan'] = company_data['plan']
        if 'size' in company_data:
            formatted['size'] = company_data['size']
        if 'website' in company_data:
            formatted['website'] = company_data['website']
        if 'industry' in company_data:
            formatted['industry'] = company_data['industry']
        if 'monthly_spend' in company_data:
            formatted['monthly_spend'] = company_data['monthly_spend']
        
        # Custom attributes
        if 'custom_attributes' in company_data:
            formatted['custom_attributes'] = company_data['custom_attributes']
            
        return formatted
    
    @staticmethod
    def format_conversation_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format conversation message data."""
        formatted = {
            'message_type': message_data.get('message_type', 'comment'),
            'type': message_data.get('type', 'user'),
            'body': message_data.get('body', '')
        }
        
        if 'intercom_user_id' in message_data:
            formatted['intercom_user_id'] = message_data['intercom_user_id']
        if 'user_id' in message_data:
            formatted['user_id'] = message_data['user_id']
        if 'email' in message_data:
            formatted['email'] = message_data['email']
        if 'admin_id' in message_data:
            formatted['admin_id'] = message_data['admin_id']
            
        return formatted
    
    @staticmethod
    def build_search_query(filters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build search query for contacts/companies."""
        return {
            'query': {
                'operator': 'AND',
                'value': filters
            }
        }
    
    @staticmethod
    def validate_webhook_signature(payload: str, signature: str, secret: str) -> bool:
        """Validate Intercom webhook signature."""
        try:
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha1
            ).hexdigest()
            return hmac.compare_digest(f"sha1={expected_signature}", signature)
        except Exception:
            return False

class IntercomNode(BaseNode):
    """
    Intercom Node for comprehensive API integration.
    
    Provides access to all Intercom API operations including conversations,
    contacts, companies, articles, admins, teams, segments, and webhooks.
    """

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.intercom.io"
        self.session = None
        self.rate_limit_remaining = 1000
        self.rate_limit_reset = 0

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            name="intercom",
            description="Comprehensive Intercom API integration for customer messaging and support",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="The Intercom operation to perform",
                    required=True,
                    options=[
                        # Authentication
                        IntercomOperation.GET_ACCESS_TOKEN,
                        
                        # Conversations
                        IntercomOperation.LIST_CONVERSATIONS,
                        IntercomOperation.GET_CONVERSATION,
                        IntercomOperation.CREATE_CONVERSATION,
                        IntercomOperation.UPDATE_CONVERSATION,
                        IntercomOperation.REPLY_TO_CONVERSATION,
                        IntercomOperation.CLOSE_CONVERSATION,
                        IntercomOperation.OPEN_CONVERSATION,
                        IntercomOperation.ASSIGN_CONVERSATION,
                        IntercomOperation.SNOOZE_CONVERSATION,
                        IntercomOperation.TAG_CONVERSATION,
                        IntercomOperation.UNTAG_CONVERSATION,
                        
                        # Contacts
                        IntercomOperation.LIST_CONTACTS,
                        IntercomOperation.GET_CONTACT,
                        IntercomOperation.CREATE_CONTACT,
                        IntercomOperation.UPDATE_CONTACT,
                        IntercomOperation.DELETE_CONTACT,
                        IntercomOperation.MERGE_CONTACTS,
                        IntercomOperation.SEARCH_CONTACTS,
                        IntercomOperation.TAG_CONTACT,
                        IntercomOperation.UNTAG_CONTACT,
                        
                        # Companies
                        IntercomOperation.LIST_COMPANIES,
                        IntercomOperation.GET_COMPANY,
                        IntercomOperation.CREATE_COMPANY,
                        IntercomOperation.UPDATE_COMPANY,
                        IntercomOperation.DELETE_COMPANY,
                        IntercomOperation.SCROLL_COMPANIES,
                        IntercomOperation.LIST_COMPANY_CONTACTS,
                        
                        # Articles
                        IntercomOperation.LIST_ARTICLES,
                        IntercomOperation.GET_ARTICLE,
                        IntercomOperation.CREATE_ARTICLE,
                        IntercomOperation.UPDATE_ARTICLE,
                        IntercomOperation.DELETE_ARTICLE,
                        IntercomOperation.SEARCH_ARTICLES,
                        
                        # Admins
                        IntercomOperation.LIST_ADMINS,
                        IntercomOperation.GET_ADMIN,
                        IntercomOperation.SET_ADMIN_AWAY,
                        
                        # Teams
                        IntercomOperation.LIST_TEAMS,
                        IntercomOperation.GET_TEAM,
                        
                        # Segments
                        IntercomOperation.LIST_SEGMENTS,
                        IntercomOperation.GET_SEGMENT,
                        
                        # Tags
                        IntercomOperation.LIST_TAGS,
                        IntercomOperation.GET_TAG,
                        IntercomOperation.CREATE_TAG,
                        IntercomOperation.DELETE_TAG,
                        IntercomOperation.TAG_COMPANIES,
                        IntercomOperation.UNTAG_COMPANIES,
                        
                        # Notes
                        IntercomOperation.LIST_NOTES,
                        IntercomOperation.GET_NOTE,
                        IntercomOperation.CREATE_NOTE,
                        
                        # Events
                        IntercomOperation.CREATE_EVENT,
                        IntercomOperation.LIST_EVENTS,
                        
                        # Data Attributes
                        IntercomOperation.LIST_DATA_ATTRIBUTES,
                        IntercomOperation.CREATE_DATA_ATTRIBUTE,
                        IntercomOperation.UPDATE_DATA_ATTRIBUTE,
                        
                        # Subscription Types
                        IntercomOperation.LIST_SUBSCRIPTION_TYPES,
                        
                        # Webhooks
                        IntercomOperation.CREATE_WEBHOOK,
                        IntercomOperation.GET_WEBHOOK,
                        IntercomOperation.UPDATE_WEBHOOK,
                        IntercomOperation.DELETE_WEBHOOK,
                        IntercomOperation.LIST_WEBHOOKS,
                        
                        # Visitors
                        IntercomOperation.GET_VISITOR,
                        IntercomOperation.UPDATE_VISITOR,
                        IntercomOperation.CONVERT_VISITOR,
                        
                        # Counts
                        IntercomOperation.GET_COUNTS,
                        
                        # Activity Logs
                        IntercomOperation.LIST_ACTIVITY_LOGS,
                        
                        # Custom Objects
                        IntercomOperation.LIST_CUSTOM_OBJECTS,
                        IntercomOperation.GET_CUSTOM_OBJECT,
                        IntercomOperation.CREATE_CUSTOM_OBJECT,
                        IntercomOperation.UPDATE_CUSTOM_OBJECT,
                        IntercomOperation.DELETE_CUSTOM_OBJECT
                    ]
                ),
                NodeParameter(
                    name="auth_type",
                    type=NodeParameterType.STRING,
                    description="Authentication method",
                    required=True,
                    default=IntercomAuthType.ACCESS_TOKEN,
                    options=[IntercomAuthType.ACCESS_TOKEN, IntercomAuthType.OAUTH]
                ),
                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.STRING,
                    description="Intercom Access Token",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="client_id",
                    type=NodeParameterType.STRING,
                    description="OAuth Client ID",
                    required=False
                ),
                NodeParameter(
                    name="client_secret",
                    type=NodeParameterType.STRING,
                    description="OAuth Client Secret",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="region",
                    type=NodeParameterType.STRING,
                    description="Intercom region (us, eu, au)",
                    required=False,
                    default="us",
                    options=["us", "eu", "au"]
                ),
                NodeParameter(
                    name="conversation_id",
                    type=NodeParameterType.STRING,
                    description="Conversation ID",
                    required=False
                ),
                NodeParameter(
                    name="contact_id",
                    type=NodeParameterType.STRING,
                    description="Contact ID",
                    required=False
                ),
                NodeParameter(
                    name="company_id",
                    type=NodeParameterType.STRING,
                    description="Company ID",
                    required=False
                ),
                NodeParameter(
                    name="article_id",
                    type=NodeParameterType.STRING,
                    description="Article ID",
                    required=False
                ),
                NodeParameter(
                    name="admin_id",
                    type=NodeParameterType.STRING,
                    description="Admin ID",
                    required=False
                ),
                NodeParameter(
                    name="team_id",
                    type=NodeParameterType.STRING,
                    description="Team ID",
                    required=False
                ),
                NodeParameter(
                    name="segment_id",
                    type=NodeParameterType.STRING,
                    description="Segment ID",
                    required=False
                ),
                NodeParameter(
                    name="tag_id",
                    type=NodeParameterType.STRING,
                    description="Tag ID",
                    required=False
                ),
                NodeParameter(
                    name="note_id",
                    type=NodeParameterType.STRING,
                    description="Note ID",
                    required=False
                ),
                NodeParameter(
                    name="webhook_id",
                    type=NodeParameterType.STRING,
                    description="Webhook ID",
                    required=False
                ),
                NodeParameter(
                    name="visitor_id",
                    type=NodeParameterType.STRING,
                    description="Visitor ID",
                    required=False
                ),
                NodeParameter(
                    name="custom_object_id",
                    type=NodeParameterType.STRING,
                    description="Custom Object ID",
                    required=False
                ),
                NodeParameter(
                    name="email",
                    type=NodeParameterType.STRING,
                    description="Contact email address",
                    required=False
                ),
                NodeParameter(
                    name="user_id",
                    type=NodeParameterType.STRING,
                    description="External user ID",
                    required=False
                ),
                NodeParameter(
                    name="phone",
                    type=NodeParameterType.STRING,
                    description="Phone number",
                    required=False
                ),
                NodeParameter(
                    name="name",
                    type=NodeParameterType.STRING,
                    description="Name (contact, company, etc.)",
                    required=False
                ),
                NodeParameter(
                    name="message_body",
                    type=NodeParameterType.STRING,
                    description="Message content",
                    required=False
                ),
                NodeParameter(
                    name="subject",
                    type=NodeParameterType.STRING,
                    description="Subject line",
                    required=False
                ),
                NodeParameter(
                    name="message_type",
                    type=NodeParameterType.STRING,
                    description="Message type",
                    required=False,
                    default="comment",
                    options=["comment", "note"]
                ),
                NodeParameter(
                    name="assignee_id",
                    type=NodeParameterType.STRING,
                    description="Admin ID to assign to",
                    required=False
                ),
                NodeParameter(
                    name="state",
                    type=NodeParameterType.STRING,
                    description="Conversation state",
                    required=False,
                    options=["open", "closed", "snoozed"]
                ),
                NodeParameter(
                    name="snooze_until",
                    type=NodeParameterType.INTEGER,
                    description="Unix timestamp to snooze until",
                    required=False
                ),
                NodeParameter(
                    name="tag_name",
                    type=NodeParameterType.STRING,
                    description="Tag name",
                    required=False
                ),
                NodeParameter(
                    name="search_query",
                    type=NodeParameterType.OBJECT,
                    description="Search query for contacts/companies",
                    required=False
                ),
                NodeParameter(
                    name="filters",
                    type=NodeParameterType.OBJECT,
                    description="Filters for listing operations",
                    required=False
                ),
                NodeParameter(
                    name="custom_attributes",
                    type=NodeParameterType.OBJECT,
                    description="Custom attributes object",
                    required=False
                ),
                NodeParameter(
                    name="contact_data",
                    type=NodeParameterType.OBJECT,
                    description="Contact data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="company_data",
                    type=NodeParameterType.OBJECT,
                    description="Company data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="article_data",
                    type=NodeParameterType.OBJECT,
                    description="Article data for creation/update",
                    required=False
                ),
                NodeParameter(
                    name="webhook_data",
                    type=NodeParameterType.OBJECT,
                    description="Webhook configuration data",
                    required=False
                ),
                NodeParameter(
                    name="event_data",
                    type=NodeParameterType.OBJECT,
                    description="Event data for tracking",
                    required=False
                ),
                NodeParameter(
                    name="note_data",
                    type=NodeParameterType.OBJECT,
                    description="Note data for creation",
                    required=False
                ),
                NodeParameter(
                    name="data_attribute_data",
                    type=NodeParameterType.OBJECT,
                    description="Data attribute configuration",
                    required=False
                ),
                NodeParameter(
                    name="custom_object_data",
                    type=NodeParameterType.OBJECT,
                    description="Custom object data",
                    required=False
                ),
                NodeParameter(
                    name="pagination",
                    type=NodeParameterType.OBJECT,
                    description="Pagination parameters (per_page, starting_after)",
                    required=False
                ),
                NodeParameter(
                    name="scroll_param",
                    type=NodeParameterType.STRING,
                    description="Scroll parameter for large datasets",
                    required=False
                ),
                NodeParameter(
                    name="sort",
                    type=NodeParameterType.STRING,
                    description="Sort order",
                    required=False,
                    options=["created_at", "updated_at", "last_seen_at"]
                ),
                NodeParameter(
                    name="order",
                    type=NodeParameterType.STRING,
                    description="Sort direction",
                    required=False,
                    default="desc",
                    options=["asc", "desc"]
                ),
                NodeParameter(
                    name="include_counts",
                    type=NodeParameterType.BOOLEAN,
                    description="Include conversation counts",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="webhook_secret",
                    type=NodeParameterType.STRING,
                    description="Webhook secret for signature validation",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="webhook_signature",
                    type=NodeParameterType.STRING,
                    description="Webhook signature to validate",
                    required=False
                ),
                NodeParameter(
                    name="webhook_payload",
                    type=NodeParameterType.STRING,
                    description="Webhook payload to validate",
                    required=False
                ),
                NodeParameter(
                    name="timeout",
                    type=NodeParameterType.INTEGER,
                    description="Request timeout in seconds",
                    required=False,
                    default=30
                ),
                NodeParameter(
                    name="retry_attempts",
                    type=NodeParameterType.INTEGER,
                    description="Number of retry attempts for failed requests",
                    required=False,
                    default=3
                ),
                NodeParameter(
                    name="additional_headers",
                    type=NodeParameterType.OBJECT,
                    description="Additional HTTP headers",
                    required=False
                )
            ],
            outputs=[
                "success",
                "error",
                "response_data",
                "status_code",
                "conversation_id",
                "contact_id",
                "company_id",
                "admin_id",
                "rate_limit_remaining",
                "rate_limit_reset"
            ],
            metadata={
                "category": "customer_support",
                "vendor": "intercom",
                "api_version": "2.13",
                "documentation": "https://developers.intercom.com/docs",
                "rate_limits": {
                    "requests_per_minute": 1000,
                    "burst_limit": 1000
                }
            }
        )

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with SSL context."""
        if self.session is None or self.session.closed:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        return self.session

    def _get_base_url(self, region: str = "us") -> str:
        """Get base URL for specified region."""
        if region == "eu":
            return "https://api.eu.intercom.io"
        elif region == "au":
            return "https://api.au.intercom.io"
        else:
            return "https://api.intercom.io"

    def _get_headers(self, access_token: str, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Intercom-Version": "2.13"
        }
        
        if additional_headers:
            headers.update(additional_headers)
            
        return headers

    async def _handle_rate_limiting(self, response: aiohttp.ClientResponse):
        """Handle rate limiting based on response headers."""
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        
        if 'X-RateLimit-Reset' in response.headers:
            self.rate_limit_reset = int(response.headers['X-RateLimit-Reset'])
        
        if response.status == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            await asyncio.sleep(retry_after)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        access_token: str,
        region: str = "us",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        retry_attempts: int = 3
    ) -> Tuple[Dict[str, Any], int]:
        """Make HTTP request to Intercom API with retries and error handling."""
        
        session = await self._get_session()
        base_url = self._get_base_url(region)
        url = f"{base_url}{endpoint}"
        headers = self._get_headers(access_token, additional_headers)
        
        for attempt in range(retry_attempts + 1):
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if data else None,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    
                    await self._handle_rate_limiting(response)
                    
                    if response.status == 429 and attempt < retry_attempts:
                        continue
                    
                    response_text = await response.text()
                    
                    try:
                        if response_text:
                            response_data = json.loads(response_text)
                        else:
                            response_data = {}
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    
                    return response_data, response.status
                    
            except asyncio.TimeoutError:
                if attempt < retry_attempts:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise NodeValidationError(f"Request timeout after {timeout} seconds")
            except Exception as e:
                if attempt < retry_attempts:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise NodeValidationError(f"Request failed: {str(e)}")
        
        raise NodeValidationError("All retry attempts failed")

    # Authentication Methods
    async def _get_access_token(self, client_id: str, client_secret: str, region: str = "us") -> Dict[str, Any]:
        """Get OAuth access token."""
        data = {
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/auth/eagle/token",
            access_token="",
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Conversation Methods
    async def _list_conversations(self, access_token: str, region: str = "us", filters: Optional[Dict[str, Any]] = None, pagination: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List conversations."""
        params = {}
        
        if filters:
            params.update(filters)
        
        if pagination:
            params.update(pagination)
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/conversations",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_conversation(self, conversation_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get a specific conversation."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/conversations/{conversation_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_conversation(self, contact_data: Dict[str, Any], message_body: str, access_token: str, region: str = "us", subject: Optional[str] = None) -> Dict[str, Any]:
        """Create a new conversation."""
        data = {
            "from": contact_data,
            "body": message_body
        }
        
        if subject:
            data["subject"] = subject
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/conversations",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _reply_to_conversation(self, conversation_id: str, message_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Reply to a conversation."""
        formatted_message = IntercomHelper.format_conversation_message(message_data)
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/conversations/{conversation_id}/reply",
            access_token=access_token,
            region=region,
            data=formatted_message
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_conversation(self, conversation_id: str, update_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Update conversation properties."""
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/conversations/{conversation_id}",
            access_token=access_token,
            region=region,
            data=update_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _assign_conversation(self, conversation_id: str, assignee_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Assign conversation to an admin."""
        data = {
            "message_type": "assignment",
            "type": "admin",
            "admin_id": assignee_id,
            "assignee_id": assignee_id
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/conversations/{conversation_id}/reply",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _close_conversation(self, conversation_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Close a conversation."""
        data = {
            "message_type": "close",
            "type": "admin"
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/conversations/{conversation_id}/reply",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _open_conversation(self, conversation_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Open a conversation."""
        data = {
            "message_type": "open",
            "type": "admin"
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/conversations/{conversation_id}/reply",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _snooze_conversation(self, conversation_id: str, snooze_until: int, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Snooze a conversation."""
        data = {
            "message_type": "snooze",
            "type": "admin",
            "snoozed_until": snooze_until
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/conversations/{conversation_id}/reply",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _tag_conversation(self, conversation_id: str, tag_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Add tag to conversation."""
        data = {
            "id": tag_id
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/conversations/{conversation_id}/tags",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _untag_conversation(self, conversation_id: str, tag_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Remove tag from conversation."""
        data = {
            "id": tag_id
        }
        
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/conversations/{conversation_id}/tags",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Contact Methods
    async def _list_contacts(self, access_token: str, region: str = "us", filters: Optional[Dict[str, Any]] = None, pagination: Optional[Dict[str, Any]] = None, sort: Optional[str] = None, order: Optional[str] = None) -> Dict[str, Any]:
        """List contacts."""
        params = {}
        
        if filters:
            params.update(filters)
        
        if pagination:
            params.update(pagination)
        
        if sort:
            params["sort"] = sort
        
        if order:
            params["order"] = order
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/contacts",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_contact(self, contact_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get a specific contact."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/contacts/{contact_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_contact(self, contact_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Create a new contact."""
        formatted_data = IntercomHelper.format_contact_data(contact_data)
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/contacts",
            access_token=access_token,
            region=region,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_contact(self, contact_id: str, contact_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Update an existing contact."""
        formatted_data = IntercomHelper.format_contact_data(contact_data)
        
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/contacts/{contact_id}",
            access_token=access_token,
            region=region,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_contact(self, contact_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Delete a contact."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/contacts/{contact_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _search_contacts(self, search_query: Dict[str, Any], access_token: str, region: str = "us", pagination: Optional[Dict[str, Any]] = None, sort: Optional[str] = None, order: Optional[str] = None) -> Dict[str, Any]:
        """Search contacts."""
        data = search_query.copy()
        
        if pagination:
            data.update(pagination)
        
        if sort:
            data["sort"] = {"field": sort, "order": order or "desc"}
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/contacts/search",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _merge_contacts(self, from_contact_id: str, into_contact_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Merge two contacts."""
        data = {
            "from": from_contact_id,
            "into": into_contact_id
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/contacts/merge",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _tag_contact(self, contact_id: str, tag_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Add tag to contact."""
        data = {
            "id": tag_id
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/contacts/{contact_id}/tags",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _untag_contact(self, contact_id: str, tag_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Remove tag from contact."""
        data = {
            "id": tag_id
        }
        
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/contacts/{contact_id}/tags",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Company Methods
    async def _list_companies(self, access_token: str, region: str = "us", filters: Optional[Dict[str, Any]] = None, pagination: Optional[Dict[str, Any]] = None, sort: Optional[str] = None, order: Optional[str] = None) -> Dict[str, Any]:
        """List companies."""
        params = {}
        
        if filters:
            params.update(filters)
        
        if pagination:
            params.update(pagination)
        
        if sort:
            params["sort"] = sort
        
        if order:
            params["order"] = order
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/companies",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_company(self, company_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get a specific company."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/companies/{company_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_company(self, company_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Create a new company."""
        formatted_data = IntercomHelper.format_company_data(company_data)
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/companies",
            access_token=access_token,
            region=region,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_company(self, company_id: str, company_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Update an existing company."""
        formatted_data = IntercomHelper.format_company_data(company_data)
        
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/companies/{company_id}",
            access_token=access_token,
            region=region,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_company(self, company_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Delete a company."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/companies/{company_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _scroll_companies(self, access_token: str, region: str = "us", scroll_param: Optional[str] = None) -> Dict[str, Any]:
        """Scroll through companies for large datasets."""
        params = {}
        
        if scroll_param:
            params["scroll_param"] = scroll_param
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/companies/scroll",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _list_company_contacts(self, company_id: str, access_token: str, region: str = "us", pagination: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List contacts for a company."""
        params = {}
        
        if pagination:
            params.update(pagination)
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/companies/{company_id}/contacts",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    # Article Methods
    async def _list_articles(self, access_token: str, region: str = "us", filters: Optional[Dict[str, Any]] = None, pagination: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List articles."""
        params = {}
        
        if filters:
            params.update(filters)
        
        if pagination:
            params.update(pagination)
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/articles",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_article(self, article_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get a specific article."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/articles/{article_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_article(self, article_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Create a new article."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/articles",
            access_token=access_token,
            region=region,
            data=article_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_article(self, article_id: str, article_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Update an existing article."""
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/articles/{article_id}",
            access_token=access_token,
            region=region,
            data=article_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_article(self, article_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Delete an article."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/articles/{article_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _search_articles(self, search_query: str, access_token: str, region: str = "us", pagination: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search articles."""
        params = {
            "query": search_query
        }
        
        if pagination:
            params.update(pagination)
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/articles/search",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    # Admin Methods
    async def _list_admins(self, access_token: str, region: str = "us") -> Dict[str, Any]:
        """List admins."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/admins",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_admin(self, admin_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get a specific admin."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/admins/{admin_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _set_admin_away(self, admin_id: str, away_mode_enabled: bool, reassign_conversations_to: Optional[str], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Set admin away status."""
        data = {
            "away_mode_enabled": away_mode_enabled
        }
        
        if reassign_conversations_to:
            data["away_mode_reassign"] = reassign_conversations_to
        
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/admins/{admin_id}/away",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Team Methods
    async def _list_teams(self, access_token: str, region: str = "us") -> Dict[str, Any]:
        """List teams."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/teams",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_team(self, team_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get a specific team."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/teams/{team_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    # Segment Methods
    async def _list_segments(self, access_token: str, region: str = "us", include_counts: bool = False) -> Dict[str, Any]:
        """List segments."""
        params = {}
        
        if include_counts:
            params["include_count"] = "true"
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/segments",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_segment(self, segment_id: str, access_token: str, region: str = "us", include_counts: bool = False) -> Dict[str, Any]:
        """Get a specific segment."""
        params = {}
        
        if include_counts:
            params["include_count"] = "true"
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/segments/{segment_id}",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    # Tag Methods
    async def _list_tags(self, access_token: str, region: str = "us") -> Dict[str, Any]:
        """List tags."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/tags",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_tag(self, tag_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get a specific tag."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/tags/{tag_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_tag(self, tag_name: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Create a new tag."""
        data = {
            "name": tag_name
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/tags",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_tag(self, tag_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Delete a tag."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/tags/{tag_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _tag_companies(self, tag_id: str, company_ids: List[str], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Tag multiple companies."""
        data = {
            "name": "bulk_tag",
            "companies": [{"id": company_id} for company_id in company_ids]
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/tags/{tag_id}",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _untag_companies(self, tag_id: str, company_ids: List[str], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Untag multiple companies."""
        data = {
            "name": "bulk_untag",
            "companies": [{"id": company_id} for company_id in company_ids]
        }
        
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/tags/{tag_id}",
            access_token=access_token,
            region=region,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Note Methods
    async def _list_notes(self, access_token: str, region: str = "us", contact_id: Optional[str] = None, pagination: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List notes."""
        params = {}
        
        if contact_id:
            params["contact_id"] = contact_id
        
        if pagination:
            params.update(pagination)
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/notes",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_note(self, note_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get a specific note."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/notes/{note_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_note(self, note_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Create a new note."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/notes",
            access_token=access_token,
            region=region,
            data=note_data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Event Methods
    async def _create_event(self, event_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Create an event."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/events",
            access_token=access_token,
            region=region,
            data=event_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _list_events(self, access_token: str, region: str = "us", filters: Optional[Dict[str, Any]] = None, pagination: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List events."""
        params = {}
        
        if filters:
            params.update(filters)
        
        if pagination:
            params.update(pagination)
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/events",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    # Data Attribute Methods
    async def _list_data_attributes(self, access_token: str, region: str = "us", model: Optional[str] = None, include_archived: bool = False) -> Dict[str, Any]:
        """List data attributes."""
        params = {}
        
        if model:
            params["model"] = model
        
        if include_archived:
            params["include_archived"] = "true"
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/data_attributes",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_data_attribute(self, data_attribute_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Create a new data attribute."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/data_attributes",
            access_token=access_token,
            region=region,
            data=data_attribute_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_data_attribute(self, data_attribute_id: str, data_attribute_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Update a data attribute."""
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/data_attributes/{data_attribute_id}",
            access_token=access_token,
            region=region,
            data=data_attribute_data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Subscription Types Methods
    async def _list_subscription_types(self, access_token: str, region: str = "us") -> Dict[str, Any]:
        """List subscription types."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/subscription_types",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    # Webhook Methods
    async def _create_webhook(self, webhook_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Create a webhook."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/me/webhooks",
            access_token=access_token,
            region=region,
            data=webhook_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_webhook(self, webhook_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get a specific webhook."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/me/webhooks/{webhook_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_webhook(self, webhook_id: str, webhook_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Update a webhook."""
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/me/webhooks/{webhook_id}",
            access_token=access_token,
            region=region,
            data=webhook_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_webhook(self, webhook_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Delete a webhook."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/me/webhooks/{webhook_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _list_webhooks(self, access_token: str, region: str = "us") -> Dict[str, Any]:
        """List webhooks."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/me/webhooks",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    # Visitor Methods
    async def _get_visitor(self, visitor_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get a visitor."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/visitors/{visitor_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_visitor(self, visitor_id: str, visitor_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Update a visitor."""
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/visitors/{visitor_id}",
            access_token=access_token,
            region=region,
            data=visitor_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _convert_visitor(self, visitor_id: str, contact_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Convert visitor to contact."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint=f"/visitors/{visitor_id}/convert",
            access_token=access_token,
            region=region,
            data=contact_data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Counts Methods
    async def _get_counts(self, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get conversation counts."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/counts",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    # Activity Logs Methods
    async def _list_activity_logs(self, access_token: str, region: str = "us", filters: Optional[Dict[str, Any]] = None, pagination: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List activity logs."""
        params = {}
        
        if filters:
            params.update(filters)
        
        if pagination:
            params.update(pagination)
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/activity_logs",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    # Custom Object Methods
    async def _list_custom_objects(self, access_token: str, region: str = "us", filters: Optional[Dict[str, Any]] = None, pagination: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List custom objects."""
        params = {}
        
        if filters:
            params.update(filters)
        
        if pagination:
            params.update(pagination)
        
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint="/data/custom_objects",
            access_token=access_token,
            region=region,
            params=params
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_custom_object(self, custom_object_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Get a custom object."""
        response_data, status_code = await self._make_request(
            method="GET",
            endpoint=f"/data/custom_objects/{custom_object_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _create_custom_object(self, custom_object_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Create a custom object."""
        response_data, status_code = await self._make_request(
            method="POST",
            endpoint="/data/custom_objects",
            access_token=access_token,
            region=region,
            data=custom_object_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _update_custom_object(self, custom_object_id: str, custom_object_data: Dict[str, Any], access_token: str, region: str = "us") -> Dict[str, Any]:
        """Update a custom object."""
        response_data, status_code = await self._make_request(
            method="PUT",
            endpoint=f"/data/custom_objects/{custom_object_id}",
            access_token=access_token,
            region=region,
            data=custom_object_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _delete_custom_object(self, custom_object_id: str, access_token: str, region: str = "us") -> Dict[str, Any]:
        """Delete a custom object."""
        response_data, status_code = await self._make_request(
            method="DELETE",
            endpoint=f"/data/custom_objects/{custom_object_id}",
            access_token=access_token,
            region=region
        )
        
        return {"response": response_data, "status_code": status_code}

    # Webhook Validation Methods
    async def _validate_webhook(self, webhook_payload: str, webhook_signature: str, webhook_secret: str) -> Dict[str, Any]:
        """Validate webhook signature."""
        is_valid = IntercomHelper.validate_webhook_signature(
            webhook_payload, webhook_signature, webhook_secret
        )
        
        return {
            "response": {"valid": is_valid},
            "status_code": 200 if is_valid else 401
        }

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Intercom operation."""
        try:
            # Validate required parameters
            operation = parameters.get("operation")
            if not operation:
                raise NodeValidationError("Operation is required")

            auth_type = parameters.get("auth_type", IntercomAuthType.ACCESS_TOKEN)
            region = parameters.get("region", "us")
            timeout = parameters.get("timeout", 30)
            retry_attempts = parameters.get("retry_attempts", 3)
            
            # Get authentication credentials
            access_token = parameters.get("access_token")
            client_id = parameters.get("client_id")
            client_secret = parameters.get("client_secret")
            
            # Validate authentication
            if auth_type == IntercomAuthType.ACCESS_TOKEN:
                if not access_token:
                    raise NodeValidationError("Access token is required for token authentication")
            elif auth_type == IntercomAuthType.OAUTH:
                if not client_id or not client_secret:
                    raise NodeValidationError("Client ID and secret are required for OAuth authentication")

            # Execute the operation
            result = None
            
            if operation == IntercomOperation.GET_ACCESS_TOKEN:
                result = await self._get_access_token(client_id, client_secret, region)
            
            # Conversation operations
            elif operation == IntercomOperation.LIST_CONVERSATIONS:
                filters = parameters.get("filters")
                pagination = parameters.get("pagination")
                result = await self._list_conversations(access_token, region, filters, pagination)
            
            elif operation == IntercomOperation.GET_CONVERSATION:
                conversation_id = parameters.get("conversation_id")
                if not conversation_id:
                    raise NodeValidationError("Conversation ID is required")
                result = await self._get_conversation(conversation_id, access_token, region)
            
            elif operation == IntercomOperation.CREATE_CONVERSATION:
                contact_data = parameters.get("contact_data")
                message_body = parameters.get("message_body")
                subject = parameters.get("subject")
                if not contact_data or not message_body:
                    raise NodeValidationError("Contact data and message body are required")
                result = await self._create_conversation(contact_data, message_body, access_token, region, subject)
            
            elif operation == IntercomOperation.REPLY_TO_CONVERSATION:
                conversation_id = parameters.get("conversation_id")
                message_data = {
                    "body": parameters.get("message_body"),
                    "message_type": parameters.get("message_type", "comment"),
                    "type": "admin",
                    "admin_id": parameters.get("admin_id")
                }
                if not conversation_id or not message_data.get("body"):
                    raise NodeValidationError("Conversation ID and message body are required")
                result = await self._reply_to_conversation(conversation_id, message_data, access_token, region)
            
            elif operation == IntercomOperation.UPDATE_CONVERSATION:
                conversation_id = parameters.get("conversation_id")
                update_data = {}
                if parameters.get("state"):
                    update_data["state"] = parameters["state"]
                if parameters.get("assignee_id"):
                    update_data["assignee_id"] = parameters["assignee_id"]
                if not conversation_id:
                    raise NodeValidationError("Conversation ID is required")
                result = await self._update_conversation(conversation_id, update_data, access_token, region)
            
            elif operation == IntercomOperation.ASSIGN_CONVERSATION:
                conversation_id = parameters.get("conversation_id")
                assignee_id = parameters.get("assignee_id")
                if not conversation_id or not assignee_id:
                    raise NodeValidationError("Conversation ID and assignee ID are required")
                result = await self._assign_conversation(conversation_id, assignee_id, access_token, region)
            
            elif operation == IntercomOperation.CLOSE_CONVERSATION:
                conversation_id = parameters.get("conversation_id")
                if not conversation_id:
                    raise NodeValidationError("Conversation ID is required")
                result = await self._close_conversation(conversation_id, access_token, region)
            
            elif operation == IntercomOperation.OPEN_CONVERSATION:
                conversation_id = parameters.get("conversation_id")
                if not conversation_id:
                    raise NodeValidationError("Conversation ID is required")
                result = await self._open_conversation(conversation_id, access_token, region)
            
            elif operation == IntercomOperation.SNOOZE_CONVERSATION:
                conversation_id = parameters.get("conversation_id")
                snooze_until = parameters.get("snooze_until")
                if not conversation_id or not snooze_until:
                    raise NodeValidationError("Conversation ID and snooze until timestamp are required")
                result = await self._snooze_conversation(conversation_id, snooze_until, access_token, region)
            
            elif operation == IntercomOperation.TAG_CONVERSATION:
                conversation_id = parameters.get("conversation_id")
                tag_id = parameters.get("tag_id")
                if not conversation_id or not tag_id:
                    raise NodeValidationError("Conversation ID and tag ID are required")
                result = await self._tag_conversation(conversation_id, tag_id, access_token, region)
            
            elif operation == IntercomOperation.UNTAG_CONVERSATION:
                conversation_id = parameters.get("conversation_id")
                tag_id = parameters.get("tag_id")
                if not conversation_id or not tag_id:
                    raise NodeValidationError("Conversation ID and tag ID are required")
                result = await self._untag_conversation(conversation_id, tag_id, access_token, region)
            
            # Contact operations
            elif operation == IntercomOperation.LIST_CONTACTS:
                filters = parameters.get("filters")
                pagination = parameters.get("pagination")
                sort = parameters.get("sort")
                order = parameters.get("order")
                result = await self._list_contacts(access_token, region, filters, pagination, sort, order)
            
            elif operation == IntercomOperation.GET_CONTACT:
                contact_id = parameters.get("contact_id")
                if not contact_id:
                    raise NodeValidationError("Contact ID is required")
                result = await self._get_contact(contact_id, access_token, region)
            
            elif operation == IntercomOperation.CREATE_CONTACT:
                contact_data = parameters.get("contact_data")
                if not contact_data:
                    # Build contact data from individual parameters
                    contact_data = {}
                    if parameters.get("email"):
                        contact_data["email"] = parameters["email"]
                    if parameters.get("phone"):
                        contact_data["phone"] = parameters["phone"]
                    if parameters.get("name"):
                        contact_data["name"] = parameters["name"]
                    if parameters.get("user_id"):
                        contact_data["user_id"] = parameters["user_id"]
                    if parameters.get("custom_attributes"):
                        contact_data["custom_attributes"] = parameters["custom_attributes"]
                
                if not contact_data:
                    raise NodeValidationError("Contact data is required")
                result = await self._create_contact(contact_data, access_token, region)
            
            elif operation == IntercomOperation.UPDATE_CONTACT:
                contact_id = parameters.get("contact_id")
                contact_data = parameters.get("contact_data")
                if not contact_id or not contact_data:
                    raise NodeValidationError("Contact ID and contact data are required")
                result = await self._update_contact(contact_id, contact_data, access_token, region)
            
            elif operation == IntercomOperation.DELETE_CONTACT:
                contact_id = parameters.get("contact_id")
                if not contact_id:
                    raise NodeValidationError("Contact ID is required")
                result = await self._delete_contact(contact_id, access_token, region)
            
            elif operation == IntercomOperation.SEARCH_CONTACTS:
                search_query = parameters.get("search_query")
                pagination = parameters.get("pagination")
                sort = parameters.get("sort")
                order = parameters.get("order")
                if not search_query:
                    raise NodeValidationError("Search query is required")
                result = await self._search_contacts(search_query, access_token, region, pagination, sort, order)
            
            elif operation == IntercomOperation.MERGE_CONTACTS:
                # Expecting contact_data to contain from and into IDs
                contact_data = parameters.get("contact_data")
                if not contact_data or "from" not in contact_data or "into" not in contact_data:
                    raise NodeValidationError("Contact data with 'from' and 'into' contact IDs is required")
                result = await self._merge_contacts(contact_data["from"], contact_data["into"], access_token, region)
            
            elif operation == IntercomOperation.TAG_CONTACT:
                contact_id = parameters.get("contact_id")
                tag_id = parameters.get("tag_id")
                if not contact_id or not tag_id:
                    raise NodeValidationError("Contact ID and tag ID are required")
                result = await self._tag_contact(contact_id, tag_id, access_token, region)
            
            elif operation == IntercomOperation.UNTAG_CONTACT:
                contact_id = parameters.get("contact_id")
                tag_id = parameters.get("tag_id")
                if not contact_id or not tag_id:
                    raise NodeValidationError("Contact ID and tag ID are required")
                result = await self._untag_contact(contact_id, tag_id, access_token, region)
            
            # Company operations
            elif operation == IntercomOperation.LIST_COMPANIES:
                filters = parameters.get("filters")
                pagination = parameters.get("pagination")
                sort = parameters.get("sort")
                order = parameters.get("order")
                result = await self._list_companies(access_token, region, filters, pagination, sort, order)
            
            elif operation == IntercomOperation.GET_COMPANY:
                company_id = parameters.get("company_id")
                if not company_id:
                    raise NodeValidationError("Company ID is required")
                result = await self._get_company(company_id, access_token, region)
            
            elif operation == IntercomOperation.CREATE_COMPANY:
                company_data = parameters.get("company_data")
                if not company_data:
                    raise NodeValidationError("Company data is required")
                result = await self._create_company(company_data, access_token, region)
            
            elif operation == IntercomOperation.UPDATE_COMPANY:
                company_id = parameters.get("company_id")
                company_data = parameters.get("company_data")
                if not company_id or not company_data:
                    raise NodeValidationError("Company ID and company data are required")
                result = await self._update_company(company_id, company_data, access_token, region)
            
            elif operation == IntercomOperation.DELETE_COMPANY:
                company_id = parameters.get("company_id")
                if not company_id:
                    raise NodeValidationError("Company ID is required")
                result = await self._delete_company(company_id, access_token, region)
            
            elif operation == IntercomOperation.SCROLL_COMPANIES:
                scroll_param = parameters.get("scroll_param")
                result = await self._scroll_companies(access_token, region, scroll_param)
            
            elif operation == IntercomOperation.LIST_COMPANY_CONTACTS:
                company_id = parameters.get("company_id")
                pagination = parameters.get("pagination")
                if not company_id:
                    raise NodeValidationError("Company ID is required")
                result = await self._list_company_contacts(company_id, access_token, region, pagination)
            
            # Article operations
            elif operation == IntercomOperation.LIST_ARTICLES:
                filters = parameters.get("filters")
                pagination = parameters.get("pagination")
                result = await self._list_articles(access_token, region, filters, pagination)
            
            elif operation == IntercomOperation.GET_ARTICLE:
                article_id = parameters.get("article_id")
                if not article_id:
                    raise NodeValidationError("Article ID is required")
                result = await self._get_article(article_id, access_token, region)
            
            elif operation == IntercomOperation.CREATE_ARTICLE:
                article_data = parameters.get("article_data")
                if not article_data:
                    raise NodeValidationError("Article data is required")
                result = await self._create_article(article_data, access_token, region)
            
            elif operation == IntercomOperation.UPDATE_ARTICLE:
                article_id = parameters.get("article_id")
                article_data = parameters.get("article_data")
                if not article_id or not article_data:
                    raise NodeValidationError("Article ID and article data are required")
                result = await self._update_article(article_id, article_data, access_token, region)
            
            elif operation == IntercomOperation.DELETE_ARTICLE:
                article_id = parameters.get("article_id")
                if not article_id:
                    raise NodeValidationError("Article ID is required")
                result = await self._delete_article(article_id, access_token, region)
            
            elif operation == IntercomOperation.SEARCH_ARTICLES:
                search_query = parameters.get("search_query")
                pagination = parameters.get("pagination")
                if not search_query:
                    raise NodeValidationError("Search query is required")
                result = await self._search_articles(search_query, access_token, region, pagination)
            
            # Admin operations
            elif operation == IntercomOperation.LIST_ADMINS:
                result = await self._list_admins(access_token, region)
            
            elif operation == IntercomOperation.GET_ADMIN:
                admin_id = parameters.get("admin_id")
                if not admin_id:
                    raise NodeValidationError("Admin ID is required")
                result = await self._get_admin(admin_id, access_token, region)
            
            elif operation == IntercomOperation.SET_ADMIN_AWAY:
                admin_id = parameters.get("admin_id")
                away_mode_enabled = parameters.get("away_mode_enabled", True)
                reassign_conversations_to = parameters.get("reassign_conversations_to")
                if not admin_id:
                    raise NodeValidationError("Admin ID is required")
                result = await self._set_admin_away(admin_id, away_mode_enabled, reassign_conversations_to, access_token, region)
            
            # Team operations
            elif operation == IntercomOperation.LIST_TEAMS:
                result = await self._list_teams(access_token, region)
            
            elif operation == IntercomOperation.GET_TEAM:
                team_id = parameters.get("team_id")
                if not team_id:
                    raise NodeValidationError("Team ID is required")
                result = await self._get_team(team_id, access_token, region)
            
            # Segment operations
            elif operation == IntercomOperation.LIST_SEGMENTS:
                include_counts = parameters.get("include_counts", False)
                result = await self._list_segments(access_token, region, include_counts)
            
            elif operation == IntercomOperation.GET_SEGMENT:
                segment_id = parameters.get("segment_id")
                include_counts = parameters.get("include_counts", False)
                if not segment_id:
                    raise NodeValidationError("Segment ID is required")
                result = await self._get_segment(segment_id, access_token, region, include_counts)
            
            # Tag operations
            elif operation == IntercomOperation.LIST_TAGS:
                result = await self._list_tags(access_token, region)
            
            elif operation == IntercomOperation.GET_TAG:
                tag_id = parameters.get("tag_id")
                if not tag_id:
                    raise NodeValidationError("Tag ID is required")
                result = await self._get_tag(tag_id, access_token, region)
            
            elif operation == IntercomOperation.CREATE_TAG:
                tag_name = parameters.get("tag_name")
                if not tag_name:
                    raise NodeValidationError("Tag name is required")
                result = await self._create_tag(tag_name, access_token, region)
            
            elif operation == IntercomOperation.DELETE_TAG:
                tag_id = parameters.get("tag_id")
                if not tag_id:
                    raise NodeValidationError("Tag ID is required")
                result = await self._delete_tag(tag_id, access_token, region)
            
            elif operation == IntercomOperation.TAG_COMPANIES:
                tag_id = parameters.get("tag_id")
                company_ids = parameters.get("company_ids", [])
                if not tag_id or not company_ids:
                    raise NodeValidationError("Tag ID and company IDs are required")
                result = await self._tag_companies(tag_id, company_ids, access_token, region)
            
            elif operation == IntercomOperation.UNTAG_COMPANIES:
                tag_id = parameters.get("tag_id")
                company_ids = parameters.get("company_ids", [])
                if not tag_id or not company_ids:
                    raise NodeValidationError("Tag ID and company IDs are required")
                result = await self._untag_companies(tag_id, company_ids, access_token, region)
            
            # Note operations
            elif operation == IntercomOperation.LIST_NOTES:
                contact_id = parameters.get("contact_id")
                pagination = parameters.get("pagination")
                result = await self._list_notes(access_token, region, contact_id, pagination)
            
            elif operation == IntercomOperation.GET_NOTE:
                note_id = parameters.get("note_id")
                if not note_id:
                    raise NodeValidationError("Note ID is required")
                result = await self._get_note(note_id, access_token, region)
            
            elif operation == IntercomOperation.CREATE_NOTE:
                note_data = parameters.get("note_data")
                if not note_data:
                    raise NodeValidationError("Note data is required")
                result = await self._create_note(note_data, access_token, region)
            
            # Event operations
            elif operation == IntercomOperation.CREATE_EVENT:
                event_data = parameters.get("event_data")
                if not event_data:
                    raise NodeValidationError("Event data is required")
                result = await self._create_event(event_data, access_token, region)
            
            elif operation == IntercomOperation.LIST_EVENTS:
                filters = parameters.get("filters")
                pagination = parameters.get("pagination")
                result = await self._list_events(access_token, region, filters, pagination)
            
            # Data attribute operations
            elif operation == IntercomOperation.LIST_DATA_ATTRIBUTES:
                model = parameters.get("model")
                include_archived = parameters.get("include_archived", False)
                result = await self._list_data_attributes(access_token, region, model, include_archived)
            
            elif operation == IntercomOperation.CREATE_DATA_ATTRIBUTE:
                data_attribute_data = parameters.get("data_attribute_data")
                if not data_attribute_data:
                    raise NodeValidationError("Data attribute data is required")
                result = await self._create_data_attribute(data_attribute_data, access_token, region)
            
            elif operation == IntercomOperation.UPDATE_DATA_ATTRIBUTE:
                data_attribute_id = parameters.get("data_attribute_id")
                data_attribute_data = parameters.get("data_attribute_data")
                if not data_attribute_id or not data_attribute_data:
                    raise NodeValidationError("Data attribute ID and data are required")
                result = await self._update_data_attribute(data_attribute_id, data_attribute_data, access_token, region)
            
            # Subscription type operations
            elif operation == IntercomOperation.LIST_SUBSCRIPTION_TYPES:
                result = await self._list_subscription_types(access_token, region)
            
            # Webhook operations
            elif operation == IntercomOperation.CREATE_WEBHOOK:
                webhook_data = parameters.get("webhook_data")
                if not webhook_data:
                    raise NodeValidationError("Webhook data is required")
                result = await self._create_webhook(webhook_data, access_token, region)
            
            elif operation == IntercomOperation.GET_WEBHOOK:
                webhook_id = parameters.get("webhook_id")
                if not webhook_id:
                    raise NodeValidationError("Webhook ID is required")
                result = await self._get_webhook(webhook_id, access_token, region)
            
            elif operation == IntercomOperation.UPDATE_WEBHOOK:
                webhook_id = parameters.get("webhook_id")
                webhook_data = parameters.get("webhook_data")
                if not webhook_id or not webhook_data:
                    raise NodeValidationError("Webhook ID and webhook data are required")
                result = await self._update_webhook(webhook_id, webhook_data, access_token, region)
            
            elif operation == IntercomOperation.DELETE_WEBHOOK:
                webhook_id = parameters.get("webhook_id")
                if not webhook_id:
                    raise NodeValidationError("Webhook ID is required")
                result = await self._delete_webhook(webhook_id, access_token, region)
            
            elif operation == IntercomOperation.LIST_WEBHOOKS:
                result = await self._list_webhooks(access_token, region)
            
            # Visitor operations
            elif operation == IntercomOperation.GET_VISITOR:
                visitor_id = parameters.get("visitor_id")
                if not visitor_id:
                    raise NodeValidationError("Visitor ID is required")
                result = await self._get_visitor(visitor_id, access_token, region)
            
            elif operation == IntercomOperation.UPDATE_VISITOR:
                visitor_id = parameters.get("visitor_id")
                visitor_data = parameters.get("visitor_data")
                if not visitor_id or not visitor_data:
                    raise NodeValidationError("Visitor ID and visitor data are required")
                result = await self._update_visitor(visitor_id, visitor_data, access_token, region)
            
            elif operation == IntercomOperation.CONVERT_VISITOR:
                visitor_id = parameters.get("visitor_id")
                contact_data = parameters.get("contact_data")
                if not visitor_id or not contact_data:
                    raise NodeValidationError("Visitor ID and contact data are required")
                result = await self._convert_visitor(visitor_id, contact_data, access_token, region)
            
            # Counts operations
            elif operation == IntercomOperation.GET_COUNTS:
                result = await self._get_counts(access_token, region)
            
            # Activity logs operations
            elif operation == IntercomOperation.LIST_ACTIVITY_LOGS:
                filters = parameters.get("filters")
                pagination = parameters.get("pagination")
                result = await self._list_activity_logs(access_token, region, filters, pagination)
            
            # Custom object operations
            elif operation == IntercomOperation.LIST_CUSTOM_OBJECTS:
                filters = parameters.get("filters")
                pagination = parameters.get("pagination")
                result = await self._list_custom_objects(access_token, region, filters, pagination)
            
            elif operation == IntercomOperation.GET_CUSTOM_OBJECT:
                custom_object_id = parameters.get("custom_object_id")
                if not custom_object_id:
                    raise NodeValidationError("Custom object ID is required")
                result = await self._get_custom_object(custom_object_id, access_token, region)
            
            elif operation == IntercomOperation.CREATE_CUSTOM_OBJECT:
                custom_object_data = parameters.get("custom_object_data")
                if not custom_object_data:
                    raise NodeValidationError("Custom object data is required")
                result = await self._create_custom_object(custom_object_data, access_token, region)
            
            elif operation == IntercomOperation.UPDATE_CUSTOM_OBJECT:
                custom_object_id = parameters.get("custom_object_id")
                custom_object_data = parameters.get("custom_object_data")
                if not custom_object_id or not custom_object_data:
                    raise NodeValidationError("Custom object ID and data are required")
                result = await self._update_custom_object(custom_object_id, custom_object_data, access_token, region)
            
            elif operation == IntercomOperation.DELETE_CUSTOM_OBJECT:
                custom_object_id = parameters.get("custom_object_id")
                if not custom_object_id:
                    raise NodeValidationError("Custom object ID is required")
                result = await self._delete_custom_object(custom_object_id, access_token, region)
            
            # Webhook validation
            elif operation == "validate_webhook":
                webhook_payload = parameters.get("webhook_payload")
                webhook_signature = parameters.get("webhook_signature")
                webhook_secret = parameters.get("webhook_secret")
                if not all([webhook_payload, webhook_signature, webhook_secret]):
                    raise NodeValidationError("Webhook payload, signature, and secret are required")
                result = await self._validate_webhook(webhook_payload, webhook_signature, webhook_secret)
            
            else:
                raise NodeValidationError(f"Unsupported operation: {operation}")

            if not result:
                raise NodeValidationError("Operation failed to return a result")

            # Extract response data and status
            response_data = result.get("response", {})
            status_code = result.get("status_code", 200)
            
            # Determine success based on status code
            success = 200 <= status_code < 300
            
            # Extract specific IDs from response for convenience
            conversation_id = None
            contact_id = None
            company_id = None
            admin_id = None
            
            if isinstance(response_data, dict):
                conversation_id = response_data.get("id") if "conversation" in str(response_data.get("type", "")).lower() else None
                contact_id = response_data.get("id") if response_data.get("type") == "contact" else None
                company_id = response_data.get("id") if response_data.get("type") == "company" else None
                admin_id = response_data.get("id") if response_data.get("type") == "admin" else None

            return {
                "success": success,
                "error": None if success else response_data.get("errors", [{"message": f"HTTP {status_code}"}]),
                "response_data": response_data,
                "status_code": status_code,
                "conversation_id": conversation_id,
                "contact_id": contact_id,
                "company_id": company_id,
                "admin_id": admin_id,
                "rate_limit_remaining": self.rate_limit_remaining,
                "rate_limit_reset": self.rate_limit_reset
            }

        except NodeValidationError as e:
            logger.error(f"Validation error in IntercomNode: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response_data": None,
                "status_code": 400,
                "conversation_id": None,
                "contact_id": None,
                "company_id": None,
                "admin_id": None,
                "rate_limit_remaining": self.rate_limit_remaining,
                "rate_limit_reset": self.rate_limit_reset
            }
        except Exception as e:
            logger.error(f"Unexpected error in IntercomNode: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "response_data": None,
                "status_code": 500,
                "conversation_id": None,
                "contact_id": None,
                "company_id": None,
                "admin_id": None,
                "rate_limit_remaining": self.rate_limit_remaining,
                "rate_limit_reset": self.rate_limit_reset
            }

    async def cleanup(self):
        """Cleanup resources."""
        if self.session and not self.session.closed:
            await self.session.close()

# Register the node
if __name__ == "__main__":
    node = IntercomNode()
    print(f"IntercomNode registered with {len(node.get_schema().parameters)} parameters")