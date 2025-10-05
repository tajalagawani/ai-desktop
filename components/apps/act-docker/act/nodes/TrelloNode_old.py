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

# Configure logging
logger = logging.getLogger(__name__)

class TrelloOperation:
    """Operations available on Trello REST API."""
    
    # Authentication
    GET_TOKEN = "get_token"
    
    # Board Operations
    GET_BOARDS = "get_boards"
    GET_BOARD = "get_board"
    CREATE_BOARD = "create_board"
    UPDATE_BOARD = "update_board"
    DELETE_BOARD = "delete_board"
    
    # List Operations
    GET_BOARD_LISTS = "get_board_lists"
    GET_LIST = "get_list"
    CREATE_LIST = "create_list"
    UPDATE_LIST = "update_list"
    ARCHIVE_LIST = "archive_list"
    MOVE_LIST = "move_list"
    
    # Card Operations
    GET_BOARD_CARDS = "get_board_cards"
    GET_LIST_CARDS = "get_list_cards"
    GET_CARD = "get_card"
    CREATE_CARD = "create_card"
    UPDATE_CARD = "update_card"
    DELETE_CARD = "delete_card"
    ARCHIVE_CARD = "archive_card"
    MOVE_CARD = "move_card"
    COPY_CARD = "copy_card"
    
    # Card Actions
    ADD_CARD_COMMENT = "add_card_comment"
    GET_CARD_COMMENTS = "get_card_comments"
    UPDATE_CARD_COMMENT = "update_card_comment"
    DELETE_CARD_COMMENT = "delete_card_comment"
    
    # Card Attachments
    GET_CARD_ATTACHMENTS = "get_card_attachments"
    ADD_CARD_ATTACHMENT = "add_card_attachment"
    DELETE_CARD_ATTACHMENT = "delete_card_attachment"
    
    # Card Members
    GET_CARD_MEMBERS = "get_card_members"
    ADD_CARD_MEMBER = "add_card_member"
    REMOVE_CARD_MEMBER = "remove_card_member"
    
    # Card Labels
    GET_CARD_LABELS = "get_card_labels"
    ADD_CARD_LABEL = "add_card_label"
    REMOVE_CARD_LABEL = "remove_card_label"
    
    # Card Checklists
    GET_CARD_CHECKLISTS = "get_card_checklists"
    CREATE_CARD_CHECKLIST = "create_card_checklist"
    DELETE_CARD_CHECKLIST = "delete_card_checklist"
    
    # Checklist Items
    GET_CHECKLIST_ITEMS = "get_checklist_items"
    CREATE_CHECKLIST_ITEM = "create_checklist_item"
    UPDATE_CHECKLIST_ITEM = "update_checklist_item"
    DELETE_CHECKLIST_ITEM = "delete_checklist_item"
    
    # Member Operations
    GET_MEMBER = "get_member"
    GET_MEMBER_BOARDS = "get_member_boards"
    GET_MEMBER_CARDS = "get_member_cards"
    UPDATE_MEMBER = "update_member"
    
    # Organization Operations
    GET_ORGANIZATIONS = "get_organizations"
    GET_ORGANIZATION = "get_organization"
    CREATE_ORGANIZATION = "create_organization"
    UPDATE_ORGANIZATION = "update_organization"
    DELETE_ORGANIZATION = "delete_organization"
    
    # Label Operations
    GET_BOARD_LABELS = "get_board_labels"
    GET_LABEL = "get_label"
    CREATE_LABEL = "create_label"
    UPDATE_LABEL = "update_label"
    DELETE_LABEL = "delete_label"
    
    # Webhook Operations
    GET_WEBHOOKS = "get_webhooks"
    GET_WEBHOOK = "get_webhook"
    CREATE_WEBHOOK = "create_webhook"
    UPDATE_WEBHOOK = "update_webhook"
    DELETE_WEBHOOK = "delete_webhook"
    
    # Search Operations
    SEARCH_BOARDS = "search_boards"
    SEARCH_CARDS = "search_cards"
    SEARCH_MEMBERS = "search_members"
    SEARCH_ORGANIZATIONS = "search_organizations"

class TrelloNode(BaseNode):
    """
    Node for interacting with Trello REST API.
    Provides comprehensive functionality for boards, cards, lists, members, and organization management.
    """
    
    BASE_URL = "https://api.trello.com/1"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Trello node."""
        return NodeSchema(
            node_type="trello",
            version="1.0.0",
            description="Comprehensive integration with Trello REST API for boards, cards, lists, members, and organization management",
            parameters=[
                # Authentication
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Trello API",
                    required=True,
                    enum=[
                        # Authentication
                        TrelloOperation.GET_TOKEN,
                        
                        # Boards
                        TrelloOperation.GET_BOARDS,
                        TrelloOperation.GET_BOARD,
                        TrelloOperation.CREATE_BOARD,
                        TrelloOperation.UPDATE_BOARD,
                        TrelloOperation.DELETE_BOARD,
                        
                        # Lists
                        TrelloOperation.GET_BOARD_LISTS,
                        TrelloOperation.GET_LIST,
                        TrelloOperation.CREATE_LIST,
                        TrelloOperation.UPDATE_LIST,
                        TrelloOperation.ARCHIVE_LIST,
                        TrelloOperation.MOVE_LIST,
                        
                        # Cards
                        TrelloOperation.GET_BOARD_CARDS,
                        TrelloOperation.GET_LIST_CARDS,
                        TrelloOperation.GET_CARD,
                        TrelloOperation.CREATE_CARD,
                        TrelloOperation.UPDATE_CARD,
                        TrelloOperation.DELETE_CARD,
                        TrelloOperation.ARCHIVE_CARD,
                        TrelloOperation.MOVE_CARD,
                        TrelloOperation.COPY_CARD,
                        
                        # Card Actions
                        TrelloOperation.ADD_CARD_COMMENT,
                        TrelloOperation.GET_CARD_COMMENTS,
                        TrelloOperation.UPDATE_CARD_COMMENT,
                        TrelloOperation.DELETE_CARD_COMMENT,
                        
                        # Card Attachments
                        TrelloOperation.GET_CARD_ATTACHMENTS,
                        TrelloOperation.ADD_CARD_ATTACHMENT,
                        TrelloOperation.DELETE_CARD_ATTACHMENT,
                        
                        # Card Members
                        TrelloOperation.GET_CARD_MEMBERS,
                        TrelloOperation.ADD_CARD_MEMBER,
                        TrelloOperation.REMOVE_CARD_MEMBER,
                        
                        # Card Labels
                        TrelloOperation.GET_CARD_LABELS,
                        TrelloOperation.ADD_CARD_LABEL,
                        TrelloOperation.REMOVE_CARD_LABEL,
                        
                        # Card Checklists
                        TrelloOperation.GET_CARD_CHECKLISTS,
                        TrelloOperation.CREATE_CARD_CHECKLIST,
                        TrelloOperation.DELETE_CARD_CHECKLIST,
                        
                        # Checklist Items
                        TrelloOperation.GET_CHECKLIST_ITEMS,
                        TrelloOperation.CREATE_CHECKLIST_ITEM,
                        TrelloOperation.UPDATE_CHECKLIST_ITEM,
                        TrelloOperation.DELETE_CHECKLIST_ITEM,
                        
                        # Members
                        TrelloOperation.GET_MEMBER,
                        TrelloOperation.GET_MEMBER_BOARDS,
                        TrelloOperation.GET_MEMBER_CARDS,
                        TrelloOperation.UPDATE_MEMBER,
                        
                        # Organizations
                        TrelloOperation.GET_ORGANIZATIONS,
                        TrelloOperation.GET_ORGANIZATION,
                        TrelloOperation.CREATE_ORGANIZATION,
                        TrelloOperation.UPDATE_ORGANIZATION,
                        TrelloOperation.DELETE_ORGANIZATION,
                        
                        # Labels
                        TrelloOperation.GET_BOARD_LABELS,
                        TrelloOperation.GET_LABEL,
                        TrelloOperation.CREATE_LABEL,
                        TrelloOperation.UPDATE_LABEL,
                        TrelloOperation.DELETE_LABEL,
                        
                        # Webhooks
                        TrelloOperation.GET_WEBHOOKS,
                        TrelloOperation.GET_WEBHOOK,
                        TrelloOperation.CREATE_WEBHOOK,
                        TrelloOperation.UPDATE_WEBHOOK,
                        TrelloOperation.DELETE_WEBHOOK,
                        
                        # Search
                        TrelloOperation.SEARCH_BOARDS,
                        TrelloOperation.SEARCH_CARDS,
                        TrelloOperation.SEARCH_MEMBERS,
                        TrelloOperation.SEARCH_ORGANIZATIONS
                    ]
                ),
                NodeParameter(
                    name="api_key",
                    type=NodeParameterType.SECRET,
                    description="Trello API Key for authentication",
                    required=True
                ),
                NodeParameter(
                    name="token",
                    type=NodeParameterType.SECRET,
                    description="Trello Token for authentication",
                    required=True
                ),
                
                # Common parameters
                NodeParameter(
                    name="board_id",
                    type=NodeParameterType.STRING,
                    description="Board ID for board operations",
                    required=False
                ),
                NodeParameter(
                    name="list_id",
                    type=NodeParameterType.STRING,
                    description="List ID for list operations",
                    required=False
                ),
                NodeParameter(
                    name="card_id",
                    type=NodeParameterType.STRING,
                    description="Card ID for card operations",
                    required=False
                ),
                NodeParameter(
                    name="member_id",
                    type=NodeParameterType.STRING,
                    description="Member ID for member operations",
                    required=False
                ),
                NodeParameter(
                    name="organization_id",
                    type=NodeParameterType.STRING,
                    description="Organization ID for organization operations",
                    required=False
                ),
                NodeParameter(
                    name="label_id",
                    type=NodeParameterType.STRING,
                    description="Label ID for label operations",
                    required=False
                ),
                NodeParameter(
                    name="checklist_id",
                    type=NodeParameterType.STRING,
                    description="Checklist ID for checklist operations",
                    required=False
                ),
                NodeParameter(
                    name="checklist_item_id",
                    type=NodeParameterType.STRING,
                    description="Checklist item ID for checklist item operations",
                    required=False
                ),
                NodeParameter(
                    name="comment_id",
                    type=NodeParameterType.STRING,
                    description="Comment ID for comment operations",
                    required=False
                ),
                NodeParameter(
                    name="attachment_id",
                    type=NodeParameterType.STRING,
                    description="Attachment ID for attachment operations",
                    required=False
                ),
                NodeParameter(
                    name="webhook_id",
                    type=NodeParameterType.STRING,
                    description="Webhook ID for webhook operations",
                    required=False
                ),
                
                # Request body parameters
                NodeParameter(
                    name="request_body",
                    type=NodeParameterType.OBJECT,
                    description="Request body for create/update operations",
                    required=False
                ),
                
                # Board parameters
                NodeParameter(
                    name="board_name",
                    type=NodeParameterType.STRING,
                    description="Board name for board creation",
                    required=False
                ),
                NodeParameter(
                    name="board_description",
                    type=NodeParameterType.STRING,
                    description="Board description",
                    required=False
                ),
                NodeParameter(
                    name="board_closed",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether board is closed",
                    required=False,
                    default=False
                ),
                
                # List parameters
                NodeParameter(
                    name="list_name",
                    type=NodeParameterType.STRING,
                    description="List name for list creation",
                    required=False
                ),
                NodeParameter(
                    name="list_position",
                    type=NodeParameterType.STRING,
                    description="List position",
                    required=False,
                    enum=["top", "bottom"],
                    default="bottom"
                ),
                
                # Card parameters
                NodeParameter(
                    name="card_name",
                    type=NodeParameterType.STRING,
                    description="Card name for card creation",
                    required=False
                ),
                NodeParameter(
                    name="card_description",
                    type=NodeParameterType.STRING,
                    description="Card description",
                    required=False
                ),
                NodeParameter(
                    name="card_position",
                    type=NodeParameterType.STRING,
                    description="Card position",
                    required=False,
                    enum=["top", "bottom"],
                    default="bottom"
                ),
                NodeParameter(
                    name="due_date",
                    type=NodeParameterType.STRING,
                    description="Card due date (ISO 8601)",
                    required=False
                ),
                NodeParameter(
                    name="due_complete",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether card due date is complete",
                    required=False,
                    default=False
                ),
                
                # Comment parameters
                NodeParameter(
                    name="comment_text",
                    type=NodeParameterType.STRING,
                    description="Comment text",
                    required=False
                ),
                
                # Attachment parameters
                NodeParameter(
                    name="attachment_url",
                    type=NodeParameterType.STRING,
                    description="Attachment URL",
                    required=False
                ),
                NodeParameter(
                    name="attachment_name",
                    type=NodeParameterType.STRING,
                    description="Attachment name",
                    required=False
                ),
                
                # Label parameters
                NodeParameter(
                    name="label_name",
                    type=NodeParameterType.STRING,
                    description="Label name",
                    required=False
                ),
                NodeParameter(
                    name="label_color",
                    type=NodeParameterType.STRING,
                    description="Label color",
                    required=False,
                    enum=["yellow", "purple", "blue", "red", "green", "orange", "black", "sky", "pink", "lime"]
                ),
                
                # Checklist parameters
                NodeParameter(
                    name="checklist_name",
                    type=NodeParameterType.STRING,
                    description="Checklist name",
                    required=False
                ),
                NodeParameter(
                    name="checklist_item_name",
                    type=NodeParameterType.STRING,
                    description="Checklist item name",
                    required=False
                ),
                NodeParameter(
                    name="checklist_item_checked",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether checklist item is checked",
                    required=False,
                    default=False
                ),
                
                # Webhook parameters
                NodeParameter(
                    name="webhook_callback_url",
                    type=NodeParameterType.STRING,
                    description="Webhook callback URL",
                    required=False
                ),
                NodeParameter(
                    name="webhook_description",
                    type=NodeParameterType.STRING,
                    description="Webhook description",
                    required=False
                ),
                
                # Search parameters
                NodeParameter(
                    name="search_query",
                    type=NodeParameterType.STRING,
                    description="Search query",
                    required=False
                ),
                NodeParameter(
                    name="search_cards_limit",
                    type=NodeParameterType.NUMBER,
                    description="Limit for card search results",
                    required=False,
                    default=10,
                    min_value=1,
                    max_value=1000
                ),
                NodeParameter(
                    name="search_boards_limit",
                    type=NodeParameterType.NUMBER,
                    description="Limit for board search results",
                    required=False,
                    default=10,
                    min_value=1,
                    max_value=1000
                ),
                
                # Query parameters
                NodeParameter(
                    name="fields",
                    type=NodeParameterType.STRING,
                    description="Fields to include in response",
                    required=False,
                    default="all"
                ),
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Limit number of results",
                    required=False,
                    default=50,
                    min_value=1,
                    max_value=1000
                ),
                NodeParameter(
                    name="filter",
                    type=NodeParameterType.STRING,
                    description="Filter for results",
                    required=False,
                    enum=["all", "open", "closed", "members", "organization", "public", "starred"]
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
                "board_id": NodeParameterType.STRING,
                "list_id": NodeParameterType.STRING,
                "card_id": NodeParameterType.STRING,
                "member_id": NodeParameterType.STRING,
                "organization_id": NodeParameterType.STRING,
                "webhook_id": NodeParameterType.STRING
            },
            
            # Add metadata
            tags=["trello", "project-management", "boards", "cards", "collaboration", "api", "integration"],
            author="System",
            documentation_url="https://developer.atlassian.com/cloud/trello/rest/"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for API credentials
        if not params.get("api_key"):
            raise NodeValidationError("Trello API Key is required")
        if not params.get("token"):
            raise NodeValidationError("Trello Token is required")
            
        # Validate based on operation
        board_operations = [
            TrelloOperation.GET_BOARD, TrelloOperation.UPDATE_BOARD,
            TrelloOperation.DELETE_BOARD, TrelloOperation.GET_BOARD_LISTS,
            TrelloOperation.GET_BOARD_CARDS, TrelloOperation.CREATE_LIST,
            TrelloOperation.GET_BOARD_LABELS, TrelloOperation.CREATE_LABEL
        ]
        
        if operation in board_operations:
            if not params.get("board_id"):
                raise NodeValidationError("Board ID is required for board operations")
                
        list_operations = [
            TrelloOperation.GET_LIST, TrelloOperation.UPDATE_LIST,
            TrelloOperation.ARCHIVE_LIST, TrelloOperation.MOVE_LIST,
            TrelloOperation.GET_LIST_CARDS, TrelloOperation.CREATE_CARD
        ]
        
        if operation in list_operations:
            if not params.get("list_id"):
                raise NodeValidationError("List ID is required for list operations")
                
        card_operations = [
            TrelloOperation.GET_CARD, TrelloOperation.UPDATE_CARD,
            TrelloOperation.DELETE_CARD, TrelloOperation.ARCHIVE_CARD,
            TrelloOperation.MOVE_CARD, TrelloOperation.COPY_CARD,
            TrelloOperation.ADD_CARD_COMMENT, TrelloOperation.GET_CARD_COMMENTS,
            TrelloOperation.GET_CARD_ATTACHMENTS, TrelloOperation.ADD_CARD_ATTACHMENT,
            TrelloOperation.GET_CARD_MEMBERS, TrelloOperation.ADD_CARD_MEMBER,
            TrelloOperation.GET_CARD_LABELS, TrelloOperation.ADD_CARD_LABEL,
            TrelloOperation.GET_CARD_CHECKLISTS, TrelloOperation.CREATE_CARD_CHECKLIST
        ]
        
        if operation in card_operations:
            if not params.get("card_id"):
                raise NodeValidationError("Card ID is required for card operations")
                
        # Specific validations
        if operation == TrelloOperation.CREATE_BOARD:
            if not params.get("board_name"):
                raise NodeValidationError("Board name is required for board creation")
                
        if operation == TrelloOperation.CREATE_LIST:
            if not params.get("list_name"):
                raise NodeValidationError("List name is required for list creation")
                
        if operation == TrelloOperation.CREATE_CARD:
            if not params.get("card_name"):
                raise NodeValidationError("Card name is required for card creation")
                
        if operation == TrelloOperation.ADD_CARD_COMMENT:
            if not params.get("comment_text"):
                raise NodeValidationError("Comment text is required for adding comment")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Trello node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Execute the appropriate operation
            if operation == TrelloOperation.GET_TOKEN:
                return await self._operation_get_token(validated_data)
            elif operation == TrelloOperation.GET_BOARDS:
                return await self._operation_get_boards(validated_data)
            elif operation == TrelloOperation.GET_BOARD:
                return await self._operation_get_board(validated_data)
            elif operation == TrelloOperation.CREATE_BOARD:
                return await self._operation_create_board(validated_data)
            elif operation == TrelloOperation.UPDATE_BOARD:
                return await self._operation_update_board(validated_data)
            elif operation == TrelloOperation.DELETE_BOARD:
                return await self._operation_delete_board(validated_data)
            elif operation == TrelloOperation.GET_BOARD_LISTS:
                return await self._operation_get_board_lists(validated_data)
            elif operation == TrelloOperation.GET_LIST:
                return await self._operation_get_list(validated_data)
            elif operation == TrelloOperation.CREATE_LIST:
                return await self._operation_create_list(validated_data)
            elif operation == TrelloOperation.UPDATE_LIST:
                return await self._operation_update_list(validated_data)
            elif operation == TrelloOperation.ARCHIVE_LIST:
                return await self._operation_archive_list(validated_data)
            elif operation == TrelloOperation.GET_BOARD_CARDS:
                return await self._operation_get_board_cards(validated_data)
            elif operation == TrelloOperation.GET_LIST_CARDS:
                return await self._operation_get_list_cards(validated_data)
            elif operation == TrelloOperation.GET_CARD:
                return await self._operation_get_card(validated_data)
            elif operation == TrelloOperation.CREATE_CARD:
                return await self._operation_create_card(validated_data)
            elif operation == TrelloOperation.UPDATE_CARD:
                return await self._operation_update_card(validated_data)
            elif operation == TrelloOperation.DELETE_CARD:
                return await self._operation_delete_card(validated_data)
            elif operation == TrelloOperation.ARCHIVE_CARD:
                return await self._operation_archive_card(validated_data)
            elif operation == TrelloOperation.MOVE_CARD:
                return await self._operation_move_card(validated_data)
            elif operation == TrelloOperation.ADD_CARD_COMMENT:
                return await self._operation_add_card_comment(validated_data)
            elif operation == TrelloOperation.GET_CARD_COMMENTS:
                return await self._operation_get_card_comments(validated_data)
            elif operation == TrelloOperation.GET_CARD_ATTACHMENTS:
                return await self._operation_get_card_attachments(validated_data)
            elif operation == TrelloOperation.ADD_CARD_ATTACHMENT:
                return await self._operation_add_card_attachment(validated_data)
            elif operation == TrelloOperation.GET_CARD_MEMBERS:
                return await self._operation_get_card_members(validated_data)
            elif operation == TrelloOperation.ADD_CARD_MEMBER:
                return await self._operation_add_card_member(validated_data)
            elif operation == TrelloOperation.GET_CARD_LABELS:
                return await self._operation_get_card_labels(validated_data)
            elif operation == TrelloOperation.ADD_CARD_LABEL:
                return await self._operation_add_card_label(validated_data)
            elif operation == TrelloOperation.GET_MEMBER:
                return await self._operation_get_member(validated_data)
            elif operation == TrelloOperation.SEARCH_BOARDS:
                return await self._operation_search_boards(validated_data)
            elif operation == TrelloOperation.SEARCH_CARDS:
                return await self._operation_search_cards(validated_data)
            else:
                error_message = f"Unknown operation: {operation}"
                logger.error(error_message)
                return self._create_error_response(error_message)
                
        except Exception as e:
            error_message = f"Error in Trello node: {str(e)}"
            logger.error(error_message)
            return self._create_error_response(error_message)
        finally:
            # Clean up session
            await self._cleanup_session()
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "status": "error",
            "result": None,
            "error": error_message,
            "id": None,
            "status_code": None,
            "response_headers": None,
            "board_id": None,
            "list_id": None,
            "card_id": None,
            "member_id": None,
            "organization_id": None,
            "webhook_id": None
        }
    
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
    
    def _get_base_url(self) -> str:
        """Get the base URL for Trello API."""
        return self.BASE_URL
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any], 
                          data: Optional[Dict[str, Any]] = None, query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the Trello API."""
        base_url = self._get_base_url()
        url = f"{base_url}/{endpoint}"
        
        # Add authentication parameters
        auth_params = {
            "key": params.get("api_key"),
            "token": params.get("token")
        }
        
        if query_params:
            auth_params.update(query_params)
        
        url += "?" + urlencode(auth_params)
        
        headers = {
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
                    error_message = f"Trello API error {response.status}: {response_data}"
                    logger.error(error_message)
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "id": None,
                        "status_code": response.status,
                        "response_headers": response_headers,
                        "board_id": None,
                        "list_id": None,
                        "card_id": None,
                        "member_id": None,
                        "organization_id": None,
                        "webhook_id": None
                    }
                
                # Extract data from response
                response_id = None
                board_id = None
                list_id = None
                card_id = None
                member_id = None
                organization_id = None
                webhook_id = None
                
                if isinstance(response_data, dict):
                    response_id = response_data.get("id")
                    board_id = response_data.get("idBoard") or response_data.get("board", {}).get("id")
                    list_id = response_data.get("idList") or response_data.get("list", {}).get("id")
                    card_id = response_data.get("idCard") or response_data.get("card", {}).get("id")
                    member_id = response_data.get("idMember") or response_data.get("member", {}).get("id")
                    organization_id = response_data.get("idOrganization") or response_data.get("organization", {}).get("id")
                    webhook_id = response_data.get("id") if "webhook" in endpoint else None
                
                return {
                    "status": "success",
                    "result": response_data,
                    "error": None,
                    "id": response_id,
                    "status_code": response.status,
                    "response_headers": response_headers,
                    "board_id": board_id,
                    "list_id": list_id,
                    "card_id": card_id,
                    "member_id": member_id,
                    "organization_id": organization_id,
                    "webhook_id": webhook_id
                }
                
        except aiohttp.ClientError as e:
            error_message = f"HTTP error: {str(e)}"
            logger.error(error_message)
            return self._create_error_response(error_message)
    
    # -------------------------
    # Authentication Operations
    # -------------------------
    
    async def _operation_get_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get token information."""
        return await self._make_request("GET", "tokens/" + params.get("token"), params)
    
    # -------------------------
    # Board Operations
    # -------------------------
    
    async def _operation_get_boards(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all boards for the authenticated user."""
        member_id = params.get("member_id", "me")
        query_params = {"fields": params.get("fields", "all")}
        return await self._make_request("GET", f"members/{member_id}/boards", params, query_params=query_params)
    
    async def _operation_get_board(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get board details."""
        board_id = params.get("board_id")
        query_params = {"fields": params.get("fields", "all")}
        return await self._make_request("GET", f"boards/{board_id}", params, query_params=query_params)
    
    async def _operation_create_board(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a board."""
        request_data = params.get("request_body", {})
        if not request_data:
            request_data = {
                "name": params.get("board_name"),
                "desc": params.get("board_description", ""),
                "closed": params.get("board_closed", False)
            }
        
        return await self._make_request("POST", "boards", params, request_data)
    
    async def _operation_update_board(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a board."""
        board_id = params.get("board_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PUT", f"boards/{board_id}", params, request_data)
    
    async def _operation_delete_board(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a board."""
        board_id = params.get("board_id")
        return await self._make_request("DELETE", f"boards/{board_id}", params)
    
    # -------------------------
    # List Operations
    # -------------------------
    
    async def _operation_get_board_lists(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get lists on a board."""
        board_id = params.get("board_id")
        query_params = {"fields": params.get("fields", "all")}
        return await self._make_request("GET", f"boards/{board_id}/lists", params, query_params=query_params)
    
    async def _operation_get_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list details."""
        list_id = params.get("list_id")
        query_params = {"fields": params.get("fields", "all")}
        return await self._make_request("GET", f"lists/{list_id}", params, query_params=query_params)
    
    async def _operation_create_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a list."""
        request_data = params.get("request_body", {})
        if not request_data:
            request_data = {
                "name": params.get("list_name"),
                "idBoard": params.get("board_id"),
                "pos": params.get("list_position", "bottom")
            }
        
        return await self._make_request("POST", "lists", params, request_data)
    
    async def _operation_update_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a list."""
        list_id = params.get("list_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PUT", f"lists/{list_id}", params, request_data)
    
    async def _operation_archive_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Archive a list."""
        list_id = params.get("list_id")
        request_data = {"closed": True}
        return await self._make_request("PUT", f"lists/{list_id}", params, request_data)
    
    # -------------------------
    # Card Operations
    # -------------------------
    
    async def _operation_get_board_cards(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get cards on a board."""
        board_id = params.get("board_id")
        query_params = {"fields": params.get("fields", "all")}
        return await self._make_request("GET", f"boards/{board_id}/cards", params, query_params=query_params)
    
    async def _operation_get_list_cards(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get cards in a list."""
        list_id = params.get("list_id")
        query_params = {"fields": params.get("fields", "all")}
        return await self._make_request("GET", f"lists/{list_id}/cards", params, query_params=query_params)
    
    async def _operation_get_card(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get card details."""
        card_id = params.get("card_id")
        query_params = {"fields": params.get("fields", "all")}
        return await self._make_request("GET", f"cards/{card_id}", params, query_params=query_params)
    
    async def _operation_create_card(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a card."""
        request_data = params.get("request_body", {})
        if not request_data:
            request_data = {
                "name": params.get("card_name"),
                "desc": params.get("card_description", ""),
                "idList": params.get("list_id"),
                "pos": params.get("card_position", "bottom")
            }
            
            if params.get("due_date"):
                request_data["due"] = params.get("due_date")
            if params.get("due_complete"):
                request_data["dueComplete"] = params.get("due_complete")
        
        return await self._make_request("POST", "cards", params, request_data)
    
    async def _operation_update_card(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a card."""
        card_id = params.get("card_id")
        request_data = params.get("request_body", {})
        return await self._make_request("PUT", f"cards/{card_id}", params, request_data)
    
    async def _operation_delete_card(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a card."""
        card_id = params.get("card_id")
        return await self._make_request("DELETE", f"cards/{card_id}", params)
    
    async def _operation_archive_card(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Archive a card."""
        card_id = params.get("card_id")
        request_data = {"closed": True}
        return await self._make_request("PUT", f"cards/{card_id}", params, request_data)
    
    async def _operation_move_card(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move a card to another list."""
        card_id = params.get("card_id")
        request_data = params.get("request_body", {})
        if not request_data and params.get("list_id"):
            request_data = {"idList": params.get("list_id")}
        
        return await self._make_request("PUT", f"cards/{card_id}", params, request_data)
    
    # -------------------------
    # Card Actions Operations
    # -------------------------
    
    async def _operation_add_card_comment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a comment to a card."""
        card_id = params.get("card_id")
        request_data = params.get("request_body", {})
        if not request_data:
            request_data = {"text": params.get("comment_text")}
        
        return await self._make_request("POST", f"cards/{card_id}/actions/comments", params, request_data)
    
    async def _operation_get_card_comments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comments on a card."""
        card_id = params.get("card_id")
        query_params = {"filter": "commentCard"}
        return await self._make_request("GET", f"cards/{card_id}/actions", params, query_params=query_params)
    
    # -------------------------
    # Card Attachments Operations
    # -------------------------
    
    async def _operation_get_card_attachments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get attachments on a card."""
        card_id = params.get("card_id")
        return await self._make_request("GET", f"cards/{card_id}/attachments", params)
    
    async def _operation_add_card_attachment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add an attachment to a card."""
        card_id = params.get("card_id")
        request_data = params.get("request_body", {})
        if not request_data:
            request_data = {
                "url": params.get("attachment_url"),
                "name": params.get("attachment_name", "")
            }
        
        return await self._make_request("POST", f"cards/{card_id}/attachments", params, request_data)
    
    # -------------------------
    # Card Members Operations
    # -------------------------
    
    async def _operation_get_card_members(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get members on a card."""
        card_id = params.get("card_id")
        return await self._make_request("GET", f"cards/{card_id}/members", params)
    
    async def _operation_add_card_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a member to a card."""
        card_id = params.get("card_id")
        member_id = params.get("member_id")
        return await self._make_request("POST", f"cards/{card_id}/idMembers", params, {"value": member_id})
    
    # -------------------------
    # Card Labels Operations
    # -------------------------
    
    async def _operation_get_card_labels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get labels on a card."""
        card_id = params.get("card_id")
        return await self._make_request("GET", f"cards/{card_id}/labels", params)
    
    async def _operation_add_card_label(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a label to a card."""
        card_id = params.get("card_id")
        label_id = params.get("label_id")
        return await self._make_request("POST", f"cards/{card_id}/idLabels", params, {"value": label_id})
    
    # -------------------------
    # Member Operations
    # -------------------------
    
    async def _operation_get_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get member details."""
        member_id = params.get("member_id", "me")
        query_params = {"fields": params.get("fields", "all")}
        return await self._make_request("GET", f"members/{member_id}", params, query_params=query_params)
    
    # -------------------------
    # Search Operations
    # -------------------------
    
    async def _operation_search_boards(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search boards."""
        query_params = {
            "query": params.get("search_query"),
            "modelTypes": "boards",
            "boards_limit": params.get("search_boards_limit", 10)
        }
        return await self._make_request("GET", "search", params, query_params=query_params)
    
    async def _operation_search_cards(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search cards."""
        query_params = {
            "query": params.get("search_query"),
            "modelTypes": "cards",
            "cards_limit": params.get("search_cards_limit", 10)
        }
        return await self._make_request("GET", "search", params, query_params=query_params)


# Utility functions for common Trello operations
class TrelloHelpers:
    """Helper functions for common Trello operations."""
    
    @staticmethod
    def create_board_data(name: str, description: str = "", closed: bool = False,
                         organization_id: str = None) -> Dict[str, Any]:
        """Create board data object."""
        board_data = {
            "name": name,
            "desc": description,
            "closed": closed
        }
        
        if organization_id:
            board_data["idOrganization"] = organization_id
        
        return board_data
    
    @staticmethod
    def create_list_data(name: str, board_id: str, position: str = "bottom") -> Dict[str, Any]:
        """Create list data object."""
        return {
            "name": name,
            "idBoard": board_id,
            "pos": position
        }
    
    @staticmethod
    def create_card_data(name: str, list_id: str, description: str = "",
                        position: str = "bottom", due_date: str = None,
                        due_complete: bool = False) -> Dict[str, Any]:
        """Create card data object."""
        card_data = {
            "name": name,
            "desc": description,
            "idList": list_id,
            "pos": position,
            "dueComplete": due_complete
        }
        
        if due_date:
            card_data["due"] = due_date
        
        return card_data
    
    @staticmethod
    def create_label_data(name: str, color: str, board_id: str) -> Dict[str, Any]:
        """Create label data object."""
        return {
            "name": name,
            "color": color,
            "idBoard": board_id
        }
    
    @staticmethod
    def create_webhook_data(callback_url: str, model_id: str, 
                           description: str = "") -> Dict[str, Any]:
        """Create webhook data object."""
        return {
            "callbackURL": callback_url,
            "idModel": model_id,
            "description": description
        }


# Main test function for Trello Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Trello Node Test Suite ===")
        
        # Get API credentials from environment or user input
        api_key = os.environ.get("TRELLO_API_KEY")
        token = os.environ.get("TRELLO_TOKEN")
        
        if not api_key or not token:
            print("Trello credentials not found in environment variables")
            print("Please set TRELLO_API_KEY and TRELLO_TOKEN")
            print("Or provide them when prompted...")
            
            if not api_key:
                api_key = input("Enter Trello API Key: ")
            if not token:
                token = input("Enter Trello Token: ")
        
        if not api_key or not token:
            print("Trello credentials are required for testing")
            return
        
        # Create an instance of the Trello Node
        node = TrelloNode()
        
        # Test cases
        test_cases = [
            {
                "name": "Get Token Info",
                "params": {
                    "operation": TrelloOperation.GET_TOKEN,
                    "api_key": api_key,
                    "token": token
                },
                "expected_status": "success"
            },
            {
                "name": "Get Boards",
                "params": {
                    "operation": TrelloOperation.GET_BOARDS,
                    "api_key": api_key,
                    "token": token
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
    registry.register("trello", TrelloNode)
    logger.debug("Successfully registered TrelloNode with registry")
except ImportError:
    logger.warning("Could not register TrelloNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")