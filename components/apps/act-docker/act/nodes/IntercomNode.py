"""
Intercom Node - Comprehensive integration with Intercom REST API

Provides access to all Intercom API operations including conversations, contacts, companies, articles, admins, and webhooks.
Supports complete customer messaging workflow integration with team collaboration, help desk management,
knowledge base administration, and customer relationship management features.

Key capabilities include: Conversation management and messaging, contact and customer data management, company organization,
help center article management, admin and team coordination, segment targeting, webhook integration,
event tracking, and comprehensive customer support workflow automation.

Built for production environments with Bearer token authentication, comprehensive error handling,
rate limiting compliance, and team collaboration features for customer messaging and support.
"""

import logging
from typing import Dict, Any, Optional

try:
    from universal_request_node import UniversalRequestNode
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError, NodeExecutionError
    )
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )
    except ImportError:
        from universal_request_node import UniversalRequestNode
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )

logger = logging.getLogger(__name__)

class IntercomNode(BaseNode):
    """Comprehensive Intercom REST API integration node."""
    
    # Embedded configuration for Intercom API
    CONFIG = {
        "base_url": "https://api.intercom.io",
        "authentication": {
            "type": "bearer_token",
            "header": "Authorization"
        },
        "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Intercom-Version": "2.11"
        },
        "timeout": 30,
        "retry_config": {
            "max_retries": 3,
            "retry_delay": 1.0,
            "exponential_backoff": True
        },
        "rate_limiting": {
            "max_requests_per_minute": 1000,
            "burst_limit": 100
        }
    }
    
    # Complete operations mapping for Intercom API (50+ operations)
    OPERATIONS = {
        # Authentication
        "get_access_token": {
            "method": "GET",
            "endpoint": "/me",
            "params": [],
            "required": []
        },
        
        # Conversations API
        "list_conversations": {
            "method": "GET",
            "endpoint": "/conversations",
            "params": ["starting_after", "per_page", "display_as", "order"],
            "required": []
        },
        "get_conversation": {
            "method": "GET",
            "endpoint": "/conversations/{conversation_id}",
            "params": ["conversation_id", "display_as"],
            "required": ["conversation_id"]
        },
        "create_conversation": {
            "method": "POST",
            "endpoint": "/conversations",
            "params": ["from", "body", "message_type", "subject", "template", "request_body"],
            "required": ["from", "body"]
        },
        "update_conversation": {
            "method": "PUT",
            "endpoint": "/conversations/{conversation_id}",
            "params": ["conversation_id", "request_body"],
            "required": ["conversation_id", "request_body"]
        },
        "reply_to_conversation": {
            "method": "POST",
            "endpoint": "/conversations/{conversation_id}/reply",
            "params": ["conversation_id", "message_type", "type", "body", "attachment_urls", "request_body"],
            "required": ["conversation_id", "message_type", "type", "body"]
        },
        "close_conversation": {
            "method": "POST",
            "endpoint": "/conversations/{conversation_id}/parts",
            "params": ["conversation_id"],
            "required": ["conversation_id"]
        },
        "open_conversation": {
            "method": "POST",
            "endpoint": "/conversations/{conversation_id}/parts",
            "params": ["conversation_id"],
            "required": ["conversation_id"]
        },
        "assign_conversation": {
            "method": "POST",
            "endpoint": "/conversations/{conversation_id}/parts",
            "params": ["conversation_id", "admin_id", "assignee_id", "request_body"],
            "required": ["conversation_id"]
        },
        "snooze_conversation": {
            "method": "POST",
            "endpoint": "/conversations/{conversation_id}/parts",
            "params": ["conversation_id", "snoozed_until", "request_body"],
            "required": ["conversation_id", "snoozed_until"]
        },
        "tag_conversation": {
            "method": "POST",
            "endpoint": "/conversations/{conversation_id}/tags",
            "params": ["conversation_id", "tag_id", "admin_id", "request_body"],
            "required": ["conversation_id", "tag_id"]
        },
        "untag_conversation": {
            "method": "DELETE",
            "endpoint": "/conversations/{conversation_id}/tags/{tag_id}",
            "params": ["conversation_id", "tag_id", "admin_id"],
            "required": ["conversation_id", "tag_id"]
        },
        
        # Contacts API
        "list_contacts": {
            "method": "GET",
            "endpoint": "/contacts",
            "params": ["per_page", "starting_after", "email", "phone", "user_id", "intercom_user_id"],
            "required": []
        },
        "get_contact": {
            "method": "GET",
            "endpoint": "/contacts/{contact_id}",
            "params": ["contact_id"],
            "required": ["contact_id"]
        },
        "create_contact": {
            "method": "POST",
            "endpoint": "/contacts",
            "params": ["external_id", "email", "phone", "name", "avatar", "signed_up_at", "last_seen_at", "owner_id", "unsubscribed_from_emails", "custom_attributes", "request_body"],
            "required": []
        },
        "update_contact": {
            "method": "PUT",
            "endpoint": "/contacts/{contact_id}",
            "params": ["contact_id", "request_body"],
            "required": ["contact_id", "request_body"]
        },
        "delete_contact": {
            "method": "DELETE",
            "endpoint": "/contacts/{contact_id}",
            "params": ["contact_id"],
            "required": ["contact_id"]
        },
        "merge_contacts": {
            "method": "POST",
            "endpoint": "/contacts/merge",
            "params": ["from", "into", "request_body"],
            "required": ["from", "into"]
        },
        "search_contacts": {
            "method": "POST",
            "endpoint": "/contacts/search",
            "params": ["query", "sort", "pagination", "request_body"],
            "required": ["query"]
        },
        "tag_contact": {
            "method": "POST",
            "endpoint": "/contacts/{contact_id}/tags",
            "params": ["contact_id", "tag_id", "request_body"],
            "required": ["contact_id", "tag_id"]
        },
        "untag_contact": {
            "method": "DELETE",
            "endpoint": "/contacts/{contact_id}/tags/{tag_id}",
            "params": ["contact_id", "tag_id"],
            "required": ["contact_id", "tag_id"]
        },
        
        # Companies API
        "list_companies": {
            "method": "GET",
            "endpoint": "/companies",
            "params": ["per_page", "page", "order", "sort"],
            "required": []
        },
        "get_company": {
            "method": "GET",
            "endpoint": "/companies/{company_id}",
            "params": ["company_id"],
            "required": ["company_id"]
        },
        "create_company": {
            "method": "POST",
            "endpoint": "/companies",
            "params": ["company_id", "name", "created_at", "plan", "monthly_spend", "user_count", "size", "website", "industry", "custom_attributes", "request_body"],
            "required": []
        },
        "update_company": {
            "method": "PUT",
            "endpoint": "/companies/{company_id}",
            "params": ["company_id", "request_body"],
            "required": ["company_id", "request_body"]
        },
        "delete_company": {
            "method": "DELETE",
            "endpoint": "/companies/{company_id}",
            "params": ["company_id"],
            "required": ["company_id"]
        },
        "scroll_companies": {
            "method": "GET",
            "endpoint": "/companies/scroll",
            "params": ["scroll_param"],
            "required": []
        },
        "list_company_contacts": {
            "method": "GET",
            "endpoint": "/companies/{company_id}/contacts",
            "params": ["company_id", "per_page", "page"],
            "required": ["company_id"]
        },
        
        # Articles API (Help Center)
        "list_articles": {
            "method": "GET",
            "endpoint": "/articles",
            "params": ["per_page", "page", "order"],
            "required": []
        },
        "get_article": {
            "method": "GET",
            "endpoint": "/articles/{article_id}",
            "params": ["article_id"],
            "required": ["article_id"]
        },
        "create_article": {
            "method": "POST",
            "endpoint": "/articles",
            "params": ["title", "description", "body", "author_id", "state", "parent_id", "parent_type", "translated_content", "request_body"],
            "required": ["title", "body", "author_id"]
        },
        "update_article": {
            "method": "PUT",
            "endpoint": "/articles/{article_id}",
            "params": ["article_id", "request_body"],
            "required": ["article_id", "request_body"]
        },
        "delete_article": {
            "method": "DELETE",
            "endpoint": "/articles/{article_id}",
            "params": ["article_id"],
            "required": ["article_id"]
        },
        "search_articles": {
            "method": "GET",
            "endpoint": "/articles/search",
            "params": ["phrase", "collection_ids"],
            "required": ["phrase"]
        },
        
        # Admins/Teammates API
        "list_admins": {
            "method": "GET",
            "endpoint": "/admins",
            "params": [],
            "required": []
        },
        "get_admin": {
            "method": "GET",
            "endpoint": "/admins/{admin_id}",
            "params": ["admin_id"],
            "required": ["admin_id"]
        },
        "set_admin_away": {
            "method": "PUT",
            "endpoint": "/admins/{admin_id}/away",
            "params": ["admin_id", "away_mode_enabled", "away_mode_reassign", "request_body"],
            "required": ["admin_id", "away_mode_enabled"]
        },
        
        # Teams API
        "list_teams": {
            "method": "GET",
            "endpoint": "/teams",
            "params": [],
            "required": []
        },
        "get_team": {
            "method": "GET",
            "endpoint": "/teams/{team_id}",
            "params": ["team_id"],
            "required": ["team_id"]
        },
        
        # Segments API
        "list_segments": {
            "method": "GET",
            "endpoint": "/segments",
            "params": ["include_count"],
            "required": []
        },
        "get_segment": {
            "method": "GET",
            "endpoint": "/segments/{segment_id}",
            "params": ["segment_id", "include_count"],
            "required": ["segment_id"]
        },
        
        # Tags API
        "list_tags": {
            "method": "GET",
            "endpoint": "/tags",
            "params": [],
            "required": []
        },
        "create_tag": {
            "method": "POST",
            "endpoint": "/tags",
            "params": ["tag_name", "request_body"],
            "required": ["tag_name"]
        },
        "delete_tag": {
            "method": "DELETE",
            "endpoint": "/tags/{tag_id}",
            "params": ["tag_id"],
            "required": ["tag_id"]
        },
        
        # Events API
        "create_event": {
            "method": "POST",
            "endpoint": "/events",
            "params": ["event_name", "user_id", "id", "email", "created_at", "metadata", "request_body"],
            "required": ["event_name"]
        },
        "list_events": {
            "method": "GET",
            "endpoint": "/events",
            "params": ["user_id", "email", "per_page", "summary"],
            "required": []
        },
        
        # Data Attributes API
        "list_data_attributes": {
            "method": "GET",
            "endpoint": "/data_attributes",
            "params": ["model", "include_archived"],
            "required": []
        },
        "create_data_attribute": {
            "method": "POST",
            "endpoint": "/data_attributes",
            "params": ["data_type", "model", "attribute_name", "description", "options", "request_body"],
            "required": ["data_type", "model", "attribute_name"]
        },
        "update_data_attribute": {
            "method": "PUT",
            "endpoint": "/data_attributes/{data_attribute_id}",
            "params": ["data_attribute_id", "request_body"],
            "required": ["data_attribute_id", "request_body"]
        },
        
        # Collections API (Help Center)
        "list_collections": {
            "method": "GET",
            "endpoint": "/help_center/collections",
            "params": ["per_page", "page"],
            "required": []
        },
        "get_collection": {
            "method": "GET",
            "endpoint": "/help_center/collections/{collection_id}",
            "params": ["collection_id"],
            "required": ["collection_id"]
        },
        "create_collection": {
            "method": "POST",
            "endpoint": "/help_center/collections",
            "params": ["collection_name", "description", "translated_content", "request_body"],
            "required": ["collection_name"]
        },
        "update_collection": {
            "method": "PUT",
            "endpoint": "/help_center/collections/{collection_id}",
            "params": ["collection_id", "request_body"],
            "required": ["collection_id", "request_body"]
        },
        "delete_collection": {
            "method": "DELETE",
            "endpoint": "/help_center/collections/{collection_id}",
            "params": ["collection_id"],
            "required": ["collection_id"]
        },
        
        # Webhooks API
        "list_webhooks": {
            "method": "GET",
            "endpoint": "/webhooks",
            "params": [],
            "required": []
        },
        "create_webhook": {
            "method": "POST",
            "endpoint": "/webhooks",
            "params": ["webhook_url", "topics", "request_body"],
            "required": ["webhook_url", "topics"]
        },
        "get_webhook": {
            "method": "GET",
            "endpoint": "/webhooks/{webhook_id}",
            "params": ["webhook_id"],
            "required": ["webhook_id"]
        },
        "update_webhook": {
            "method": "PUT",
            "endpoint": "/webhooks/{webhook_id}",
            "params": ["webhook_id", "request_body"],
            "required": ["webhook_id", "request_body"]
        },
        "delete_webhook": {
            "method": "DELETE",
            "endpoint": "/webhooks/{webhook_id}",
            "params": ["webhook_id"],
            "required": ["webhook_id"]
        },
        
        # Messages API
        "create_message": {
            "method": "POST",
            "endpoint": "/messages",
            "params": ["message_type", "subject", "body", "template", "from", "to", "request_body"],
            "required": ["message_type", "body", "from", "to"]
        },
        
        # Notes API
        "create_note": {
            "method": "POST",
            "endpoint": "/contacts/{contact_id}/notes",
            "params": ["contact_id", "body", "request_body"],
            "required": ["contact_id", "body"]
        },
        "list_notes": {
            "method": "GET",
            "endpoint": "/contacts/{contact_id}/notes",
            "params": ["contact_id"],
            "required": ["contact_id"]
        },
        "get_note": {
            "method": "GET",
            "endpoint": "/contacts/{contact_id}/notes/{note_id}",
            "params": ["contact_id", "note_id"],
            "required": ["contact_id", "note_id"]
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.universal_node = UniversalRequestNode()
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Intercom node."""
        return NodeSchema(
            name="IntercomNode",
            description="Comprehensive Intercom REST API integration for customer messaging and support",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Intercom operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                "access_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Intercom access token for authentication",
                    required=True
                ),
                # Common ID parameters
                "conversation_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Conversation ID for conversation operations",
                    required=False
                ),
                "contact_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Contact ID for contact operations",
                    required=False
                ),
                "company_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Company ID for company operations",
                    required=False
                ),
                "article_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Article ID for article operations",
                    required=False
                ),
                "admin_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Admin ID for admin operations",
                    required=False
                ),
                "team_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Team ID for team operations",
                    required=False
                ),
                "segment_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Segment ID for segment operations",
                    required=False
                ),
                "tag_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Tag ID for tag operations",
                    required=False
                ),
                "webhook_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Webhook ID for webhook operations",
                    required=False
                ),
                "collection_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Collection ID for collection operations",
                    required=False
                ),
                "note_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Note ID for note operations",
                    required=False
                ),
                "data_attribute_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Data attribute ID for data attribute operations",
                    required=False
                ),
                # Content parameters
                "body": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Message/content body",
                    required=False
                ),
                "subject": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Message subject",
                    required=False
                ),
                "title": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Title for articles or other content",
                    required=False
                ),
                "description": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Description for various operations",
                    required=False
                ),
                "name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Name for contacts, companies, etc.",
                    required=False
                ),
                "email": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Email address",
                    required=False
                ),
                "phone": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Phone number",
                    required=False
                ),
                # Message parameters
                "message_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Type of message (inapp, email, etc.)",
                    required=False
                ),
                "type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Type parameter for various operations",
                    required=False
                ),
                "from": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="From field for messages",
                    required=False
                ),
                "to": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="To field for messages",
                    required=False
                ),
                # Contact/Company parameters
                "external_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="External ID for contacts/companies",
                    required=False
                ),
                "user_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="User ID",
                    required=False
                ),
                "owner_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Owner ID for contacts",
                    required=False
                ),
                "custom_attributes": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Custom attributes object",
                    required=False
                ),
                # Article parameters
                "author_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Author ID for articles",
                    required=False
                ),
                "state": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="State for articles (published/draft)",
                    required=False
                ),
                # Tag parameters
                "tag_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Tag name for tag operations",
                    required=False
                ),
                # Event parameters
                "event_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Event name for event tracking",
                    required=False
                ),
                "metadata": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Event metadata",
                    required=False
                ),
                # Webhook parameters
                "webhook_url": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Webhook URL",
                    required=False
                ),
                "topics": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Webhook topics",
                    required=False
                ),
                # Search parameters
                "query": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Search query object",
                    required=False
                ),
                "phrase": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Search phrase",
                    required=False
                ),
                # Pagination parameters
                "per_page": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Number of items per page",
                    required=False
                ),
                "page": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Page number",
                    required=False
                ),
                "starting_after": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Cursor for pagination",
                    required=False
                ),
                # Other parameters
                "order": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Order for results (asc/desc)",
                    required=False
                ),
                "sort": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Sort field",
                    required=False
                ),
                "assignee_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Assignee ID for assignments",
                    required=False
                ),
                "snoozed_until": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Snooze until timestamp",
                    required=False
                ),
                # Data attribute parameters
                "data_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Data attribute type",
                    required=False
                ),
                "model": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Model for data attributes",
                    required=False
                ),
                "attribute_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Attribute name",
                    required=False
                ),
                # Collection parameters
                "collection_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Collection name",
                    required=False
                ),
                # Generic request body
                "request_body": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Request body for create/update operations",
                    required=False
                )
            },
            outputs={
                "status": NodeParameterType.STRING,
                "conversations": NodeParameterType.ARRAY,
                "conversation_info": NodeParameterType.OBJECT,
                "contacts": NodeParameterType.ARRAY,
                "contact_info": NodeParameterType.OBJECT,
                "companies": NodeParameterType.ARRAY,
                "company_info": NodeParameterType.OBJECT,
                "articles": NodeParameterType.ARRAY,
                "article_info": NodeParameterType.OBJECT,
                "admins": NodeParameterType.ARRAY,
                "admin_info": NodeParameterType.OBJECT,
                "teams": NodeParameterType.ARRAY,
                "team_info": NodeParameterType.OBJECT,
                "segments": NodeParameterType.ARRAY,
                "segment_info": NodeParameterType.OBJECT,
                "tags": NodeParameterType.ARRAY,
                "tag_info": NodeParameterType.OBJECT,
                "webhooks": NodeParameterType.ARRAY,
                "webhook_info": NodeParameterType.OBJECT,
                "events": NodeParameterType.ARRAY,
                "event_info": NodeParameterType.OBJECT,
                "data_attributes": NodeParameterType.ARRAY,
                "data_attribute_info": NodeParameterType.OBJECT,
                "collections": NodeParameterType.ARRAY,
                "collection_info": NodeParameterType.OBJECT,
                "notes": NodeParameterType.ARRAY,
                "note_info": NodeParameterType.OBJECT,
                "message_info": NodeParameterType.OBJECT,
                "search_results": NodeParameterType.OBJECT,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Intercom-specific parameters."""
        params = node_data.get("params", {})
        
        if not params.get("operation"):
            raise NodeValidationError("Operation is required")
        if not params.get("access_token"):
            raise NodeValidationError("Intercom access token is required")
        
        operation = params["operation"]
        if operation not in self.OPERATIONS:
            raise NodeValidationError(f"Unknown operation: {operation}")
        
        # Check required parameters for operation
        operation_config = self.OPERATIONS[operation]
        for required_param in operation_config.get("required", []):
            if not params.get(required_param):
                raise NodeValidationError(f"Parameter '{required_param}' is required for operation '{operation}'")
        
        return params
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Intercom operation using UniversalRequestNode."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Get operation configuration
            operation_config = self.OPERATIONS[operation]
            
            # Prepare configuration with authentication
            config = self.CONFIG.copy()
            
            # Prepare universal request node parameters
            universal_params = {
                "config": config,
                "method": operation_config["method"],
                "endpoint": operation_config["endpoint"],
                "token": params["access_token"]
            }
            
            # Handle path parameters
            endpoint = operation_config["endpoint"]
            path_params = {
                "conversation_id": params.get("conversation_id"),
                "contact_id": params.get("contact_id"),
                "company_id": params.get("company_id"),
                "article_id": params.get("article_id"),
                "admin_id": params.get("admin_id"),
                "team_id": params.get("team_id"),
                "segment_id": params.get("segment_id"),
                "tag_id": params.get("tag_id"),
                "webhook_id": params.get("webhook_id"),
                "collection_id": params.get("collection_id"),
                "note_id": params.get("note_id"),
                "data_attribute_id": params.get("data_attribute_id")
            }
            
            for param_name, param_value in path_params.items():
                if f"{{{param_name}}}" in endpoint and param_value:
                    endpoint = endpoint.replace(f"{{{param_name}}}", param_value)
            
            universal_params["endpoint"] = endpoint
            
            # Handle query parameters and body data
            if operation_config["method"] == "GET":
                query_params = {}
                for param in operation_config.get("params", []):
                    if param in params and params[param] is not None:
                        if param not in ["conversation_id", "contact_id", "company_id", "article_id", 
                                        "admin_id", "team_id", "segment_id", "tag_id", "webhook_id",
                                        "collection_id", "note_id", "data_attribute_id"]:
                            query_params[param] = params[param]
                
                if query_params:
                    universal_params["query_params"] = query_params
            else:
                # POST/PUT/DELETE operations - prepare body data
                body_data = {}
                
                if params.get("request_body"):
                    body_data = params["request_body"]
                else:
                    # Build body based on operation
                    if operation == "create_conversation":
                        body_data = {
                            "from": params.get("from"),
                            "body": params.get("body"),
                            "message_type": params.get("message_type"),
                            "subject": params.get("subject"),
                            "template": params.get("template")
                        }
                    elif operation == "reply_to_conversation":
                        body_data = {
                            "message_type": params.get("message_type"),
                            "type": params.get("type"),
                            "body": params.get("body"),
                            "attachment_urls": params.get("attachment_urls", [])
                        }
                    elif operation == "close_conversation":
                        body_data = {
                            "message_type": "close",
                            "type": "admin"
                        }
                    elif operation == "open_conversation":
                        body_data = {
                            "message_type": "open",
                            "type": "admin"
                        }
                    elif operation == "assign_conversation":
                        body_data = {
                            "message_type": "assignment",
                            "type": "admin",
                            "admin_id": params.get("admin_id"),
                            "assignee_id": params.get("assignee_id")
                        }
                    elif operation == "snooze_conversation":
                        body_data = {
                            "message_type": "snoozed",
                            "type": "admin",
                            "snoozed_until": params.get("snoozed_until")
                        }
                    elif operation == "tag_conversation":
                        body_data = {
                            "id": params.get("tag_id"),
                            "admin_id": params.get("admin_id")
                        }
                    elif operation == "create_contact":
                        body_data = {
                            "external_id": params.get("external_id"),
                            "email": params.get("email"),
                            "phone": params.get("phone"),
                            "name": params.get("name"),
                            "avatar": params.get("avatar"),
                            "signed_up_at": params.get("signed_up_at"),
                            "last_seen_at": params.get("last_seen_at"),
                            "owner_id": params.get("owner_id"),
                            "unsubscribed_from_emails": params.get("unsubscribed_from_emails"),
                            "custom_attributes": params.get("custom_attributes", {})
                        }
                    elif operation == "create_company":
                        body_data = {
                            "company_id": params.get("company_id"),
                            "name": params.get("name"),
                            "created_at": params.get("created_at"),
                            "plan": params.get("plan"),
                            "monthly_spend": params.get("monthly_spend"),
                            "user_count": params.get("user_count"),
                            "size": params.get("size"),
                            "website": params.get("website"),
                            "industry": params.get("industry"),
                            "custom_attributes": params.get("custom_attributes", {})
                        }
                    elif operation == "create_article":
                        body_data = {
                            "title": params.get("title"),
                            "description": params.get("description"),
                            "body": params.get("body"),
                            "author_id": params.get("author_id"),
                            "state": params.get("state"),
                            "parent_id": params.get("parent_id"),
                            "parent_type": params.get("parent_type"),
                            "translated_content": params.get("translated_content")
                        }
                    elif operation == "set_admin_away":
                        body_data = {
                            "away_mode_enabled": params.get("away_mode_enabled"),
                            "away_mode_reassign": params.get("away_mode_reassign")
                        }
                    elif operation == "create_tag":
                        body_data = {"name": params.get("tag_name")}
                    elif operation == "create_event":
                        body_data = {
                            "event_name": params.get("event_name"),
                            "user_id": params.get("user_id"),
                            "id": params.get("id"),
                            "email": params.get("email"),
                            "created_at": params.get("created_at"),
                            "metadata": params.get("metadata", {})
                        }
                    elif operation == "create_data_attribute":
                        body_data = {
                            "name": params.get("attribute_name"),
                            "model": params.get("model"),
                            "data_type": params.get("data_type"),
                            "description": params.get("description"),
                            "options": params.get("options")
                        }
                    elif operation == "create_collection":
                        body_data = {
                            "name": params.get("collection_name"),
                            "description": params.get("description"),
                            "translated_content": params.get("translated_content")
                        }
                    elif operation == "create_webhook":
                        body_data = {
                            "url": params.get("webhook_url"),
                            "topics": params.get("topics", [])
                        }
                    elif operation == "create_message":
                        body_data = {
                            "message_type": params.get("message_type"),
                            "subject": params.get("subject"),
                            "body": params.get("body"),
                            "template": params.get("template"),
                            "from": params.get("from"),
                            "to": params.get("to")
                        }
                    elif operation == "create_note":
                        body_data = {"body": params.get("body")}
                    elif operation == "merge_contacts":
                        body_data = {
                            "from": params.get("from"),
                            "into": params.get("into")
                        }
                    elif operation == "search_contacts":
                        body_data = {
                            "query": params.get("query"),
                            "sort": params.get("sort"),
                            "pagination": params.get("pagination")
                        }
                    elif operation == "tag_contact":
                        body_data = {"id": params.get("tag_id")}
                
                # Clean up None values
                body_data = {k: v for k, v in body_data.items() if v is not None}
                
                if body_data:
                    universal_params["body"] = body_data
            
            # Execute the request
            result = await self.universal_node.execute({
                "params": universal_params
            })
            
            if result.get("status") == "success":
                response_data = result.get("response", {})
                
                # Transform response based on operation type
                if operation.startswith("list_conversations") or operation == "list_conversations":
                    return {
                        "status": "success",
                        "conversations": response_data.get("conversations", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_conversation") or operation.startswith("create_conversation") or operation.startswith("update_conversation"):
                    return {
                        "status": "success",
                        "conversation_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_contacts") or operation == "list_contacts":
                    return {
                        "status": "success",
                        "contacts": response_data.get("data", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_contact") or operation.startswith("create_contact") or operation.startswith("update_contact"):
                    return {
                        "status": "success",
                        "contact_info": response_data,
                        "response_data": response_data
                    }
                elif operation == "search_contacts":
                    return {
                        "status": "success",
                        "search_results": response_data,
                        "contacts": response_data.get("data", []),
                        "response_data": response_data
                    }
                elif operation.startswith("list_companies") or operation == "list_companies":
                    return {
                        "status": "success",
                        "companies": response_data.get("data", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_company") or operation.startswith("create_company") or operation.startswith("update_company"):
                    return {
                        "status": "success",
                        "company_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_articles") or operation == "list_articles":
                    return {
                        "status": "success",
                        "articles": response_data.get("data", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_article") or operation.startswith("create_article") or operation.startswith("update_article"):
                    return {
                        "status": "success",
                        "article_info": response_data,
                        "response_data": response_data
                    }
                elif operation == "search_articles":
                    return {
                        "status": "success",
                        "search_results": response_data,
                        "articles": response_data.get("data", []),
                        "response_data": response_data
                    }
                elif operation.startswith("list_admins") or operation == "list_admins":
                    return {
                        "status": "success",
                        "admins": response_data.get("admins", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_admin") or operation.startswith("set_admin_away"):
                    return {
                        "status": "success",
                        "admin_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_teams") or operation == "list_teams":
                    return {
                        "status": "success",
                        "teams": response_data.get("teams", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_team"):
                    return {
                        "status": "success",
                        "team_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_segments") or operation == "list_segments":
                    return {
                        "status": "success",
                        "segments": response_data.get("data", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_segment"):
                    return {
                        "status": "success",
                        "segment_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_tags") or operation == "list_tags":
                    return {
                        "status": "success",
                        "tags": response_data.get("data", []),
                        "response_data": response_data
                    }
                elif operation.startswith("create_tag"):
                    return {
                        "status": "success",
                        "tag_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_events") or operation == "list_events":
                    return {
                        "status": "success",
                        "events": response_data.get("events", []),
                        "response_data": response_data
                    }
                elif operation.startswith("create_event"):
                    return {
                        "status": "success",
                        "event_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_data_attributes") or operation == "list_data_attributes":
                    return {
                        "status": "success",
                        "data_attributes": response_data.get("data", []),
                        "response_data": response_data
                    }
                elif operation.startswith("create_data_attribute") or operation.startswith("update_data_attribute"):
                    return {
                        "status": "success",
                        "data_attribute_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_collections") or operation == "list_collections":
                    return {
                        "status": "success",
                        "collections": response_data.get("data", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_collection") or operation.startswith("create_collection") or operation.startswith("update_collection"):
                    return {
                        "status": "success",
                        "collection_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_webhooks") or operation == "list_webhooks":
                    return {
                        "status": "success",
                        "webhooks": response_data.get("data", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_webhook") or operation.startswith("create_webhook") or operation.startswith("update_webhook"):
                    return {
                        "status": "success",
                        "webhook_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("create_message"):
                    return {
                        "status": "success",
                        "message_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("list_notes") or operation == "list_notes":
                    return {
                        "status": "success",
                        "notes": response_data.get("data", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_note") or operation.startswith("create_note"):
                    return {
                        "status": "success",
                        "note_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("delete_") or operation.startswith("untag_"):
                    return {
                        "status": "success",
                        "response_data": response_data
                    }
                else:
                    return {
                        "status": "success",
                        "response_data": response_data
                    }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Intercom operation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "INTERCOM_ERROR"
            }
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'universal_node'):
            await self.universal_node.close()