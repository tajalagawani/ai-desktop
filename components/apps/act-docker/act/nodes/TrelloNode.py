"""
Trello Node - Comprehensive integration with Trello REST API

Provides access to all Trello API operations including boards, cards, lists, members, and organization management.
Supports complete Trello workflow integration with Kanban-style project management, team collaboration,
and productivity tracking features.

Key capabilities include: Board management and organization, list creation and organization, card lifecycle management,
team member collaboration, label organization and categorization, checklist and task tracking, attachment management,
comment and activity tracking, webhook integration, and comprehensive search functionality.

Built for production environments with API key and token authentication, comprehensive error handling,
rate limiting compliance, and team collaboration features for project management.
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

class TrelloNode(BaseNode):
    """Comprehensive Trello REST API integration node."""
    
    # Embedded configuration for Trello API
    CONFIG = {
        "base_url": "https://api.trello.com/1",
        "authentication": {
            "type": "query_params",
            "params": {
                "key": "{api_key}",
                "token": "{token}"
            }
        },
        "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        "timeout": 30,
        "retry_config": {
            "max_retries": 3,
            "retry_delay": 1.0,
            "exponential_backoff": True
        },
        "rate_limiting": {
            "max_requests_per_minute": 300,
            "burst_limit": 30
        }
    }
    
    # Complete operations mapping for Trello API (60+ operations)
    OPERATIONS = {
        # Authentication
        "get_token": {
            "method": "GET",
            "endpoint": "/tokens/{token}",
            "params": ["token"],
            "required": ["token"]
        },
        
        # Board Operations
        "get_boards": {
            "method": "GET",
            "endpoint": "/members/{member_id}/boards",
            "params": ["member_id", "fields", "filter"],
            "required": []
        },
        "get_board": {
            "method": "GET",
            "endpoint": "/boards/{board_id}",
            "params": ["board_id", "fields"],
            "required": ["board_id"]
        },
        "create_board": {
            "method": "POST",
            "endpoint": "/boards",
            "params": ["board_name", "board_description", "board_closed", "request_body"],
            "required": ["board_name"]
        },
        "update_board": {
            "method": "PUT",
            "endpoint": "/boards/{board_id}",
            "params": ["board_id", "request_body"],
            "required": ["board_id", "request_body"]
        },
        "delete_board": {
            "method": "DELETE",
            "endpoint": "/boards/{board_id}",
            "params": ["board_id"],
            "required": ["board_id"]
        },
        
        # List Operations
        "get_board_lists": {
            "method": "GET",
            "endpoint": "/boards/{board_id}/lists",
            "params": ["board_id", "fields"],
            "required": ["board_id"]
        },
        "get_list": {
            "method": "GET",
            "endpoint": "/lists/{list_id}",
            "params": ["list_id", "fields"],
            "required": ["list_id"]
        },
        "create_list": {
            "method": "POST",
            "endpoint": "/lists",
            "params": ["list_name", "board_id", "list_position", "request_body"],
            "required": ["list_name", "board_id"]
        },
        "update_list": {
            "method": "PUT",
            "endpoint": "/lists/{list_id}",
            "params": ["list_id", "request_body"],
            "required": ["list_id", "request_body"]
        },
        "archive_list": {
            "method": "PUT",
            "endpoint": "/lists/{list_id}",
            "params": ["list_id"],
            "required": ["list_id"]
        },
        "move_list": {
            "method": "PUT",
            "endpoint": "/lists/{list_id}",
            "params": ["list_id", "request_body"],
            "required": ["list_id", "request_body"]
        },
        
        # Card Operations
        "get_board_cards": {
            "method": "GET",
            "endpoint": "/boards/{board_id}/cards",
            "params": ["board_id", "fields"],
            "required": ["board_id"]
        },
        "get_list_cards": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/cards",
            "params": ["list_id", "fields"],
            "required": ["list_id"]
        },
        "get_card": {
            "method": "GET",
            "endpoint": "/cards/{card_id}",
            "params": ["card_id", "fields"],
            "required": ["card_id"]
        },
        "create_card": {
            "method": "POST",
            "endpoint": "/cards",
            "params": ["card_name", "card_description", "list_id", "card_position", "due_date", "due_complete", "request_body"],
            "required": ["card_name", "list_id"]
        },
        "update_card": {
            "method": "PUT",
            "endpoint": "/cards/{card_id}",
            "params": ["card_id", "request_body"],
            "required": ["card_id", "request_body"]
        },
        "delete_card": {
            "method": "DELETE",
            "endpoint": "/cards/{card_id}",
            "params": ["card_id"],
            "required": ["card_id"]
        },
        "archive_card": {
            "method": "PUT",
            "endpoint": "/cards/{card_id}",
            "params": ["card_id"],
            "required": ["card_id"]
        },
        "move_card": {
            "method": "PUT",
            "endpoint": "/cards/{card_id}",
            "params": ["card_id", "list_id", "request_body"],
            "required": ["card_id"]
        },
        "copy_card": {
            "method": "POST",
            "endpoint": "/cards/{card_id}/actions/copyCard",
            "params": ["card_id", "request_body"],
            "required": ["card_id", "request_body"]
        },
        
        # Card Actions/Comments
        "add_card_comment": {
            "method": "POST",
            "endpoint": "/cards/{card_id}/actions/comments",
            "params": ["card_id", "comment_text", "request_body"],
            "required": ["card_id", "comment_text"]
        },
        "get_card_comments": {
            "method": "GET",
            "endpoint": "/cards/{card_id}/actions",
            "params": ["card_id"],
            "required": ["card_id"]
        },
        "update_card_comment": {
            "method": "PUT",
            "endpoint": "/actions/{comment_id}",
            "params": ["comment_id", "request_body"],
            "required": ["comment_id", "request_body"]
        },
        "delete_card_comment": {
            "method": "DELETE",
            "endpoint": "/actions/{comment_id}",
            "params": ["comment_id"],
            "required": ["comment_id"]
        },
        
        # Card Attachments
        "get_card_attachments": {
            "method": "GET",
            "endpoint": "/cards/{card_id}/attachments",
            "params": ["card_id"],
            "required": ["card_id"]
        },
        "add_card_attachment": {
            "method": "POST",
            "endpoint": "/cards/{card_id}/attachments",
            "params": ["card_id", "attachment_url", "attachment_name", "request_body"],
            "required": ["card_id"]
        },
        "delete_card_attachment": {
            "method": "DELETE",
            "endpoint": "/cards/{card_id}/attachments/{attachment_id}",
            "params": ["card_id", "attachment_id"],
            "required": ["card_id", "attachment_id"]
        },
        
        # Card Members
        "get_card_members": {
            "method": "GET",
            "endpoint": "/cards/{card_id}/members",
            "params": ["card_id"],
            "required": ["card_id"]
        },
        "add_card_member": {
            "method": "POST",
            "endpoint": "/cards/{card_id}/idMembers",
            "params": ["card_id", "member_id"],
            "required": ["card_id", "member_id"]
        },
        "remove_card_member": {
            "method": "DELETE",
            "endpoint": "/cards/{card_id}/idMembers/{member_id}",
            "params": ["card_id", "member_id"],
            "required": ["card_id", "member_id"]
        },
        
        # Card Labels
        "get_card_labels": {
            "method": "GET",
            "endpoint": "/cards/{card_id}/labels",
            "params": ["card_id"],
            "required": ["card_id"]
        },
        "add_card_label": {
            "method": "POST",
            "endpoint": "/cards/{card_id}/idLabels",
            "params": ["card_id", "label_id"],
            "required": ["card_id", "label_id"]
        },
        "remove_card_label": {
            "method": "DELETE",
            "endpoint": "/cards/{card_id}/idLabels/{label_id}",
            "params": ["card_id", "label_id"],
            "required": ["card_id", "label_id"]
        },
        
        # Card Checklists
        "get_card_checklists": {
            "method": "GET",
            "endpoint": "/cards/{card_id}/checklists",
            "params": ["card_id"],
            "required": ["card_id"]
        },
        "create_card_checklist": {
            "method": "POST",
            "endpoint": "/cards/{card_id}/checklists",
            "params": ["card_id", "checklist_name", "request_body"],
            "required": ["card_id", "checklist_name"]
        },
        "delete_card_checklist": {
            "method": "DELETE",
            "endpoint": "/cards/{card_id}/checklists/{checklist_id}",
            "params": ["card_id", "checklist_id"],
            "required": ["card_id", "checklist_id"]
        },
        
        # Checklist Items
        "get_checklist_items": {
            "method": "GET",
            "endpoint": "/checklists/{checklist_id}/checkItems",
            "params": ["checklist_id"],
            "required": ["checklist_id"]
        },
        "create_checklist_item": {
            "method": "POST",
            "endpoint": "/checklists/{checklist_id}/checkItems",
            "params": ["checklist_id", "checklist_item_name", "checklist_item_checked", "request_body"],
            "required": ["checklist_id", "checklist_item_name"]
        },
        "update_checklist_item": {
            "method": "PUT",
            "endpoint": "/cards/{card_id}/checkItem/{checklist_item_id}",
            "params": ["card_id", "checklist_item_id", "request_body"],
            "required": ["card_id", "checklist_item_id", "request_body"]
        },
        "delete_checklist_item": {
            "method": "DELETE",
            "endpoint": "/checklists/{checklist_id}/checkItems/{checklist_item_id}",
            "params": ["checklist_id", "checklist_item_id"],
            "required": ["checklist_id", "checklist_item_id"]
        },
        
        # Member Operations
        "get_member": {
            "method": "GET",
            "endpoint": "/members/{member_id}",
            "params": ["member_id", "fields"],
            "required": []
        },
        "get_member_boards": {
            "method": "GET",
            "endpoint": "/members/{member_id}/boards",
            "params": ["member_id", "fields", "filter"],
            "required": []
        },
        "get_member_cards": {
            "method": "GET",
            "endpoint": "/members/{member_id}/cards",
            "params": ["member_id", "fields", "filter"],
            "required": []
        },
        "update_member": {
            "method": "PUT",
            "endpoint": "/members/{member_id}",
            "params": ["member_id", "request_body"],
            "required": ["member_id", "request_body"]
        },
        
        # Organization Operations
        "get_organizations": {
            "method": "GET",
            "endpoint": "/members/me/organizations",
            "params": ["fields"],
            "required": []
        },
        "get_organization": {
            "method": "GET",
            "endpoint": "/organizations/{organization_id}",
            "params": ["organization_id", "fields"],
            "required": ["organization_id"]
        },
        "create_organization": {
            "method": "POST",
            "endpoint": "/organizations",
            "params": ["request_body"],
            "required": ["request_body"]
        },
        "update_organization": {
            "method": "PUT",
            "endpoint": "/organizations/{organization_id}",
            "params": ["organization_id", "request_body"],
            "required": ["organization_id", "request_body"]
        },
        "delete_organization": {
            "method": "DELETE",
            "endpoint": "/organizations/{organization_id}",
            "params": ["organization_id"],
            "required": ["organization_id"]
        },
        
        # Label Operations
        "get_board_labels": {
            "method": "GET",
            "endpoint": "/boards/{board_id}/labels",
            "params": ["board_id", "fields"],
            "required": ["board_id"]
        },
        "get_label": {
            "method": "GET",
            "endpoint": "/labels/{label_id}",
            "params": ["label_id", "fields"],
            "required": ["label_id"]
        },
        "create_label": {
            "method": "POST",
            "endpoint": "/labels",
            "params": ["label_name", "label_color", "board_id", "request_body"],
            "required": ["label_name", "board_id"]
        },
        "update_label": {
            "method": "PUT",
            "endpoint": "/labels/{label_id}",
            "params": ["label_id", "request_body"],
            "required": ["label_id", "request_body"]
        },
        "delete_label": {
            "method": "DELETE",
            "endpoint": "/labels/{label_id}",
            "params": ["label_id"],
            "required": ["label_id"]
        },
        
        # Webhook Operations
        "get_webhooks": {
            "method": "GET",
            "endpoint": "/tokens/{token}/webhooks",
            "params": ["token"],
            "required": ["token"]
        },
        "get_webhook": {
            "method": "GET",
            "endpoint": "/webhooks/{webhook_id}",
            "params": ["webhook_id"],
            "required": ["webhook_id"]
        },
        "create_webhook": {
            "method": "POST",
            "endpoint": "/webhooks",
            "params": ["webhook_callback_url", "webhook_description", "request_body"],
            "required": ["webhook_callback_url"]
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
        
        # Search Operations
        "search_boards": {
            "method": "GET",
            "endpoint": "/search",
            "params": ["search_query", "search_boards_limit"],
            "required": ["search_query"]
        },
        "search_cards": {
            "method": "GET",
            "endpoint": "/search",
            "params": ["search_query", "search_cards_limit"],
            "required": ["search_query"]
        },
        "search_members": {
            "method": "GET",
            "endpoint": "/search",
            "params": ["search_query"],
            "required": ["search_query"]
        },
        "search_organizations": {
            "method": "GET",
            "endpoint": "/search",
            "params": ["search_query"],
            "required": ["search_query"]
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.universal_node = UniversalRequestNode()
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Trello node."""
        return NodeSchema(
            name="TrelloNode",
            description="Comprehensive Trello REST API integration for boards, cards, lists, members, and organization management",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Trello operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                "api_key": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Trello API Key for authentication",
                    required=True
                ),
                "token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Trello Token for authentication",
                    required=True
                ),
                # Common parameters
                "board_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Board ID for board operations",
                    required=False
                ),
                "list_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="List ID for list operations",
                    required=False
                ),
                "card_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Card ID for card operations",
                    required=False
                ),
                "member_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Member ID for member operations (defaults to 'me')",
                    required=False
                ),
                "organization_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Organization ID for organization operations",
                    required=False
                ),
                "label_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Label ID for label operations",
                    required=False
                ),
                "checklist_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Checklist ID for checklist operations",
                    required=False
                ),
                "checklist_item_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Checklist item ID for checklist item operations",
                    required=False
                ),
                "comment_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Comment ID for comment operations",
                    required=False
                ),
                "attachment_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Attachment ID for attachment operations",
                    required=False
                ),
                "webhook_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Webhook ID for webhook operations",
                    required=False
                ),
                # Board parameters
                "board_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Board name for board creation",
                    required=False
                ),
                "board_description": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Board description",
                    required=False
                ),
                "board_closed": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether board is closed",
                    required=False
                ),
                # List parameters
                "list_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="List name for list creation",
                    required=False
                ),
                "list_position": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="List position (top/bottom)",
                    required=False
                ),
                # Card parameters
                "card_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Card name for card creation",
                    required=False
                ),
                "card_description": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Card description",
                    required=False
                ),
                "card_position": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Card position (top/bottom)",
                    required=False
                ),
                "due_date": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Card due date (ISO 8601)",
                    required=False
                ),
                "due_complete": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether card due date is complete",
                    required=False
                ),
                # Comment parameters
                "comment_text": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Comment text",
                    required=False
                ),
                # Attachment parameters
                "attachment_url": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Attachment URL",
                    required=False
                ),
                "attachment_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Attachment name",
                    required=False
                ),
                # Label parameters
                "label_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Label name",
                    required=False
                ),
                "label_color": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Label color",
                    required=False
                ),
                # Checklist parameters
                "checklist_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Checklist name",
                    required=False
                ),
                "checklist_item_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Checklist item name",
                    required=False
                ),
                "checklist_item_checked": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether checklist item is checked",
                    required=False
                ),
                # Webhook parameters
                "webhook_callback_url": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Webhook callback URL",
                    required=False
                ),
                "webhook_description": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Webhook description",
                    required=False
                ),
                # Search parameters
                "search_query": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Search query",
                    required=False
                ),
                "search_cards_limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Limit for card search results",
                    required=False
                ),
                "search_boards_limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Limit for board search results",
                    required=False
                ),
                # Common parameters
                "fields": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Fields to include in response",
                    required=False
                ),
                "filter": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Filter for results",
                    required=False
                ),
                "limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Limit number of results",
                    required=False
                ),
                "request_body": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Request body for create/update operations",
                    required=False
                )
            },
            outputs={
                "status": NodeParameterType.STRING,
                "boards": NodeParameterType.ARRAY,
                "board_info": NodeParameterType.OBJECT,
                "lists": NodeParameterType.ARRAY,
                "list_info": NodeParameterType.OBJECT,
                "cards": NodeParameterType.ARRAY,
                "card_info": NodeParameterType.OBJECT,
                "members": NodeParameterType.ARRAY,
                "member_info": NodeParameterType.OBJECT,
                "organizations": NodeParameterType.ARRAY,
                "organization_info": NodeParameterType.OBJECT,
                "labels": NodeParameterType.ARRAY,
                "label_info": NodeParameterType.OBJECT,
                "checklists": NodeParameterType.ARRAY,
                "checklist_info": NodeParameterType.OBJECT,
                "checklist_items": NodeParameterType.ARRAY,
                "checklist_item_info": NodeParameterType.OBJECT,
                "comments": NodeParameterType.ARRAY,
                "comment_info": NodeParameterType.OBJECT,
                "attachments": NodeParameterType.ARRAY,
                "attachment_info": NodeParameterType.OBJECT,
                "webhooks": NodeParameterType.ARRAY,
                "webhook_info": NodeParameterType.OBJECT,
                "search_results": NodeParameterType.OBJECT,
                "token_info": NodeParameterType.OBJECT,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Trello-specific parameters."""
        params = node_data.get("params", {})
        
        if not params.get("operation"):
            raise NodeValidationError("Operation is required")
        if not params.get("api_key"):
            raise NodeValidationError("Trello API Key is required")
        if not params.get("token"):
            raise NodeValidationError("Trello Token is required")
        
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
        """Execute the Trello operation using UniversalRequestNode."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Get operation configuration
            operation_config = self.OPERATIONS[operation]
            
            # Prepare configuration with authentication
            config = self.CONFIG.copy()
            config["authentication"]["params"]["key"] = params["api_key"]
            config["authentication"]["params"]["token"] = params["token"]
            
            # Prepare universal request node parameters
            universal_params = {
                "config": config,
                "method": operation_config["method"],
                "endpoint": operation_config["endpoint"],
                "token": None  # Not needed since we use query params
            }
            
            # Handle path parameters
            endpoint = operation_config["endpoint"]
            path_params = {
                "board_id": params.get("board_id"),
                "list_id": params.get("list_id"),
                "card_id": params.get("card_id"),
                "member_id": params.get("member_id", "me"),
                "organization_id": params.get("organization_id"),
                "label_id": params.get("label_id"),
                "checklist_id": params.get("checklist_id"),
                "checklist_item_id": params.get("checklist_item_id"),
                "comment_id": params.get("comment_id"),
                "attachment_id": params.get("attachment_id"),
                "webhook_id": params.get("webhook_id"),
                "token": params.get("token")
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
                        if param == "fields":
                            query_params["fields"] = params[param]
                        elif param == "filter":
                            if operation.startswith("search_"):
                                # Special handling for search operations
                                if operation == "search_boards":
                                    query_params["modelTypes"] = "boards"
                                    query_params["boards_limit"] = params.get("search_boards_limit", 10)
                                elif operation == "search_cards":
                                    query_params["modelTypes"] = "cards"
                                    query_params["cards_limit"] = params.get("search_cards_limit", 10)
                                elif operation == "search_members":
                                    query_params["modelTypes"] = "members"
                                elif operation == "search_organizations":
                                    query_params["modelTypes"] = "organizations"
                            else:
                                query_params["filter"] = params[param]
                        elif param == "search_query":
                            query_params["query"] = params[param]
                        elif param == "limit":
                            query_params["limit"] = str(params[param])
                        elif param not in ["board_id", "list_id", "card_id", "member_id", "organization_id", 
                                          "label_id", "checklist_id", "checklist_item_id", "comment_id", 
                                          "attachment_id", "webhook_id", "token"]:
                            query_params[param] = params[param]
                
                # Special handling for comments
                if operation == "get_card_comments":
                    query_params["filter"] = "commentCard"
                
                if query_params:
                    universal_params["query_params"] = query_params
            else:
                # POST/PUT/DELETE operations - prepare body data
                body_data = {}
                
                if params.get("request_body"):
                    body_data = params["request_body"]
                else:
                    # Build body based on operation
                    if operation == "create_board":
                        body_data = {
                            "name": params.get("board_name"),
                            "desc": params.get("board_description", ""),
                            "closed": params.get("board_closed", False)
                        }
                    elif operation == "create_list":
                        body_data = {
                            "name": params.get("list_name"),
                            "idBoard": params.get("board_id"),
                            "pos": params.get("list_position", "bottom")
                        }
                    elif operation == "create_card":
                        body_data = {
                            "name": params.get("card_name"),
                            "desc": params.get("card_description", ""),
                            "idList": params.get("list_id"),
                            "pos": params.get("card_position", "bottom")
                        }
                        if params.get("due_date"):
                            body_data["due"] = params["due_date"]
                        if params.get("due_complete") is not None:
                            body_data["dueComplete"] = params["due_complete"]
                    elif operation == "archive_list":
                        body_data = {"closed": True}
                    elif operation == "archive_card":
                        body_data = {"closed": True}
                    elif operation == "move_card" and params.get("list_id"):
                        body_data = {"idList": params["list_id"]}
                    elif operation == "add_card_comment":
                        body_data = {"text": params.get("comment_text")}
                    elif operation == "add_card_attachment":
                        body_data = {
                            "url": params.get("attachment_url"),
                            "name": params.get("attachment_name", "")
                        }
                    elif operation == "add_card_member":
                        body_data = {"value": params.get("member_id")}
                    elif operation == "add_card_label":
                        body_data = {"value": params.get("label_id")}
                    elif operation == "create_card_checklist":
                        body_data = {"name": params.get("checklist_name")}
                    elif operation == "create_checklist_item":
                        body_data = {
                            "name": params.get("checklist_item_name"),
                            "checked": params.get("checklist_item_checked", False)
                        }
                    elif operation == "create_label":
                        body_data = {
                            "name": params.get("label_name"),
                            "color": params.get("label_color"),
                            "idBoard": params.get("board_id")
                        }
                    elif operation == "create_webhook":
                        body_data = {
                            "callbackURL": params.get("webhook_callback_url"),
                            "description": params.get("webhook_description", "")
                        }
                        # Add model ID if provided
                        if params.get("board_id"):
                            body_data["idModel"] = params["board_id"]
                
                if body_data:
                    universal_params["body"] = body_data
            
            # Execute the request
            result = await self.universal_node.execute({
                "params": universal_params
            })
            
            if result.get("status") == "success":
                response_data = result.get("response", {})
                
                # Transform response based on operation type
                if operation == "get_token":
                    return {
                        "status": "success",
                        "token_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_boards") or operation == "get_member_boards":
                    return {
                        "status": "success",
                        "boards": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_board") or operation.startswith("get_board") or operation.startswith("update_board"):
                    return {
                        "status": "success",
                        "board_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_board_lists") or operation == "get_board_lists":
                    return {
                        "status": "success",
                        "lists": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_list") or operation.startswith("get_list") or operation.startswith("update_list"):
                    return {
                        "status": "success",
                        "list_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_board_cards") or operation.startswith("get_list_cards") or operation == "get_member_cards":
                    return {
                        "status": "success",
                        "cards": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_card") or operation.startswith("get_card") or operation.startswith("update_card"):
                    return {
                        "status": "success",
                        "card_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_card_comments") or operation == "get_card_comments":
                    return {
                        "status": "success",
                        "comments": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("add_card_comment") or operation.startswith("update_card_comment"):
                    return {
                        "status": "success",
                        "comment_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_card_attachments") or operation == "get_card_attachments":
                    return {
                        "status": "success",
                        "attachments": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("add_card_attachment"):
                    return {
                        "status": "success",
                        "attachment_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_card_members") or operation == "get_card_members":
                    return {
                        "status": "success",
                        "members": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("get_member") or operation == "get_member":
                    return {
                        "status": "success",
                        "member_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_card_labels") or operation == "get_card_labels" or operation == "get_board_labels":
                    return {
                        "status": "success",
                        "labels": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_label") or operation.startswith("get_label") or operation.startswith("update_label"):
                    return {
                        "status": "success",
                        "label_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_card_checklists") or operation == "get_card_checklists":
                    return {
                        "status": "success",
                        "checklists": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_card_checklist"):
                    return {
                        "status": "success",
                        "checklist_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_checklist_items") or operation == "get_checklist_items":
                    return {
                        "status": "success",
                        "checklist_items": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_checklist_item") or operation.startswith("update_checklist_item"):
                    return {
                        "status": "success",
                        "checklist_item_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_organizations") or operation == "get_organizations":
                    return {
                        "status": "success",
                        "organizations": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_organization") or operation.startswith("get_organization") or operation.startswith("update_organization"):
                    return {
                        "status": "success",
                        "organization_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_webhooks") or operation == "get_webhooks":
                    return {
                        "status": "success",
                        "webhooks": response_data if isinstance(response_data, list) else [response_data],
                        "response_data": response_data
                    }
                elif operation.startswith("create_webhook") or operation.startswith("get_webhook") or operation.startswith("update_webhook"):
                    return {
                        "status": "success",
                        "webhook_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("search_"):
                    return {
                        "status": "success",
                        "search_results": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("delete_") or operation.startswith("archive_"):
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
            logger.error(f"Trello operation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "TRELLO_ERROR"
            }
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'universal_node'):
            await self.universal_node.close()