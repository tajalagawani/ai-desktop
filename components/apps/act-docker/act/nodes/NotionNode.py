#!/usr/bin/env python3
"""
Notion Node - Pure config-driven implementation using UniversalRequestNode
Configuration is embedded directly in the node - no separate config.json needed
Comprehensive Notion API integration with all 17 operations preserved
"""

import logging
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Import the UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class NotionNode(BaseNode):
    """
    Pure config-driven Notion node with embedded configuration.
    All operations are handled by UniversalRequestNode based on this config.
    Provides comprehensive Notion API functionality - all 17 operations preserved.
    """
    
    # Embedded configuration for Notion API
    CONFIG = {
        "base_url": "https://api.notion.com/v1",
        "authentication": {
            "type": "bearer_token",
            "header": "Authorization"
        },
        "default_headers": {
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        },
        "retry_config": {
            "max_attempts": 3,
            "backoff": "exponential",
            "retriable_codes": [429, 500, 502, 503, 504]
        },
        "rate_limiting": {
            "requests_per_second": 3,  # Notion has strict rate limits
            "burst_size": 1
        },
        "timeouts": {
            "connect": 10.0,
            "read": 30.0,
            "total": 60.0
        }
    }
    
    # Operation definitions - all 17 operations from original NotionNode
    OPERATIONS = {
        # Database operations (4)
        "create_database": {
            "method": "POST",
            "endpoint": "/databases",
            "required_params": ["title", "parent", "properties"]
        },
        "retrieve_database": {
            "method": "GET",
            "endpoint": "/databases/{database_id}",
            "required_params": ["database_id"]
        },
        "update_database": {
            "method": "PATCH",
            "endpoint": "/databases/{database_id}",
            "required_params": ["database_id"]
        },
        "query_database": {
            "method": "POST",
            "endpoint": "/databases/{database_id}/query",
            "required_params": ["database_id"]
        },
        
        # Page operations (4)
        "create_page": {
            "method": "POST",
            "endpoint": "/pages",
            "required_params": ["parent", "properties"]
        },
        "retrieve_page": {
            "method": "GET",
            "endpoint": "/pages/{page_id}",
            "required_params": ["page_id"]
        },
        "update_page": {
            "method": "PATCH",
            "endpoint": "/pages/{page_id}",
            "required_params": ["page_id"]
        },
        "archive_page": {
            "method": "PATCH",
            "endpoint": "/pages/{page_id}",
            "required_params": ["page_id"]
        },
        
        # Block operations (5)
        "retrieve_block": {
            "method": "GET",
            "endpoint": "/blocks/{block_id}",
            "required_params": ["block_id"]
        },
        "retrieve_block_children": {
            "method": "GET",
            "endpoint": "/blocks/{block_id}/children",
            "required_params": ["block_id"]
        },
        "append_block_children": {
            "method": "PATCH",
            "endpoint": "/blocks/{block_id}/children",
            "required_params": ["block_id", "children"]
        },
        "update_block": {
            "method": "PATCH",
            "endpoint": "/blocks/{block_id}",
            "required_params": ["block_id"]
        },
        "delete_block": {
            "method": "DELETE",
            "endpoint": "/blocks/{block_id}",
            "required_params": ["block_id"]
        },
        
        # Search operations (1)
        "search": {
            "method": "POST",
            "endpoint": "/search",
            "required_params": []
        },
        
        # User operations (2)
        "list_users": {
            "method": "GET",
            "endpoint": "/users",
            "required_params": []
        },
        "retrieve_user": {
            "method": "GET",
            "endpoint": "/users/{user_id}",
            "required_params": ["user_id"]
        },
        
        # Comment operations (2)
        "create_comment": {
            "method": "POST",
            "endpoint": "/comments",
            "required_params": ["rich_text", "parent"]
        },
        "retrieve_comments": {
            "method": "GET",
            "endpoint": "/comments",
            "required_params": []
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create UniversalRequestNode with embedded config
        self.universal_node = UniversalRequestNode(self.CONFIG)
    
    def get_schema(self) -> NodeSchema:
        """Return basic schema."""
        return NodeSchema(
            node_type="notion",
            version="1.0.0", 
            description="Notion API integration with embedded configuration - all 17 operations preserved",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="token", 
                    type=NodeParameterType.SECRET,
                    description="Notion API integration token",
                    required=True
                ),
                
                # ID parameters
                NodeParameter(
                    name="database_id",
                    type=NodeParameterType.STRING,
                    description="Database ID (required for database operations)",
                    required=False
                ),
                NodeParameter(
                    name="page_id",
                    type=NodeParameterType.STRING,
                    description="Page ID (required for page operations)",
                    required=False
                ),
                NodeParameter(
                    name="block_id",
                    type=NodeParameterType.STRING,
                    description="Block ID (required for block operations)",
                    required=False
                ),
                NodeParameter(
                    name="user_id",
                    type=NodeParameterType.STRING,
                    description="User ID (required for user operations)",
                    required=False
                ),
                
                # Content parameters
                NodeParameter(
                    name="title",
                    type=NodeParameterType.STRING,
                    description="Title for database or page",
                    required=False
                ),
                NodeParameter(
                    name="description",
                    type=NodeParameterType.STRING,
                    description="Description for database or page",
                    required=False
                ),
                NodeParameter(
                    name="properties",
                    type=NodeParameterType.OBJECT,
                    description="Properties schema for database or page properties",
                    required=False
                ),
                NodeParameter(
                    name="parent",
                    type=NodeParameterType.OBJECT,
                    description="Parent object for pages and databases",
                    required=False
                ),
                NodeParameter(
                    name="icon",
                    type=NodeParameterType.OBJECT,
                    description="Icon object for database or page",
                    required=False
                ),
                NodeParameter(
                    name="cover",
                    type=NodeParameterType.OBJECT,
                    description="Cover object for database or page",
                    required=False
                ),
                
                # Query parameters
                NodeParameter(
                    name="filter",
                    type=NodeParameterType.OBJECT,
                    description="Filter object for database queries and search",
                    required=False
                ),
                NodeParameter(
                    name="sorts",
                    type=NodeParameterType.ARRAY,
                    description="Sort array for database queries",
                    required=False
                ),
                NodeParameter(
                    name="start_cursor",
                    type=NodeParameterType.STRING,
                    description="Start cursor for pagination",
                    required=False
                ),
                NodeParameter(
                    name="page_size",
                    type=NodeParameterType.NUMBER,
                    description="Page size for pagination (max 100)",
                    required=False,
                    default=10
                ),
                
                # Search parameters
                NodeParameter(
                    name="query",
                    type=NodeParameterType.STRING,
                    description="Search query string",
                    required=False
                ),
                NodeParameter(
                    name="sort",
                    type=NodeParameterType.OBJECT,
                    description="Sort object for search results",
                    required=False
                ),
                
                # Block parameters
                NodeParameter(
                    name="children",
                    type=NodeParameterType.ARRAY,
                    description="Array of block objects to append",
                    required=False
                ),
                NodeParameter(
                    name="block_type",
                    type=NodeParameterType.STRING,
                    description="Type of block to create",
                    required=False,
                    enum=[
                        "paragraph", "heading_1", "heading_2", "heading_3",
                        "bulleted_list_item", "numbered_list_item", "to_do",
                        "toggle", "code", "quote", "callout", "divider",
                        "bookmark", "image", "video", "file", "pdf", "audio",
                        "embed", "equation", "table", "column", "child_page",
                        "child_database", "synced_block", "table_of_contents",
                        "breadcrumb", "link_preview", "mention"
                    ]
                ),
                NodeParameter(
                    name="block_content",
                    type=NodeParameterType.OBJECT,
                    description="Content object for block creation/update",
                    required=False
                ),
                
                # Comment parameters
                NodeParameter(
                    name="rich_text",
                    type=NodeParameterType.ARRAY,
                    description="Rich text array for comments",
                    required=False
                ),
                NodeParameter(
                    name="discussion_id",
                    type=NodeParameterType.STRING,
                    description="Discussion ID for retrieving comments",
                    required=False
                ),
                
                # Archive parameter
                NodeParameter(
                    name="archived",
                    type=NodeParameterType.BOOLEAN,
                    description="Archive status for pages/databases",
                    required=False,
                    default=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "object": NodeParameterType.OBJECT,
                "results": NodeParameterType.ARRAY,
                "has_more": NodeParameterType.BOOLEAN,
                "next_cursor": NodeParameterType.STRING
            }
        )
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute operation using UniversalRequestNode.
        """
        try:
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            if not operation:
                return {
                    "status": "error",
                    "error": "Operation is required",
                    "result": None
                }
            
            if operation not in self.OPERATIONS:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}",
                    "result": None
                }
            
            # Get operation config
            op_config = self.OPERATIONS[operation]
            
            # Prepare request data based on operation
            request_data = self._prepare_request_data(operation, params)
            
            # Make request using UniversalRequestNode
            # Pass token for bearer authentication
            request_kwargs = {
                "token": params.get("token"),  # Notion uses Bearer token
                **params  # Pass all original parameters for path substitution
            }
            
            result = await self.universal_node.request(
                method=op_config["method"],
                endpoint=op_config["endpoint"],
                data=request_data if op_config["method"] in ["POST", "PUT", "PATCH"] else None,
                params=request_data if op_config["method"] == "GET" and request_data else None,
                **request_kwargs
            )
            
            # Process result
            return self._process_result(operation, result)
            
        except Exception as e:
            logger.error(f"Notion node error: {str(e)}")
            return {
                "status": "error", 
                "error": str(e),
                "result": None
            }
    
    def _prepare_request_data(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request data based on operation."""
        data = {}
        
        # Database operations
        if operation == "create_database":
            data = {
                "parent": params.get("parent"),
                "title": [{"type": "text", "text": {"content": params.get("title", "")}}],
                "properties": params.get("properties", {})
            }
            
            # Add optional parameters
            if params.get("description"):
                data["description"] = [{"type": "text", "text": {"content": params.get("description", "")}}]
            if params.get("icon"):
                data["icon"] = params.get("icon")
            if params.get("cover"):
                data["cover"] = params.get("cover")
                
        elif operation == "update_database":
            data = {}
            if params.get("title"):
                data["title"] = [{"type": "text", "text": {"content": params.get("title")}}]
            if params.get("description"):
                data["description"] = [{"type": "text", "text": {"content": params.get("description")}}]
            if params.get("properties"):
                data["properties"] = params.get("properties")
            if params.get("icon"):
                data["icon"] = params.get("icon")
            if params.get("cover"):
                data["cover"] = params.get("cover")
                
        elif operation == "query_database":
            data = {}
            if params.get("filter"):
                data["filter"] = params.get("filter")
            if params.get("sorts"):
                data["sorts"] = params.get("sorts")
            if params.get("start_cursor"):
                data["start_cursor"] = params.get("start_cursor")
            if params.get("page_size"):
                data["page_size"] = min(params.get("page_size", 10), 100)
                
        # Page operations
        elif operation == "create_page":
            data = {
                "parent": params.get("parent"),
                "properties": params.get("properties", {})
            }
            
            # Add optional parameters
            if params.get("icon"):
                data["icon"] = params.get("icon")
            if params.get("cover"):
                data["cover"] = params.get("cover")
            if params.get("children"):
                data["children"] = params.get("children")
                
        elif operation == "update_page":
            data = {}
            if params.get("properties"):
                data["properties"] = params.get("properties")
            if params.get("icon"):
                data["icon"] = params.get("icon")
            if params.get("cover"):
                data["cover"] = params.get("cover")
            if params.get("archived") is not None:
                data["archived"] = params.get("archived")
                
        elif operation == "archive_page":
            data = {"archived": True}
            
        # Block operations
        elif operation == "append_block_children":
            data = {
                "children": params.get("children", [])
            }
            
        elif operation == "update_block":
            data = {}
            block_type = params.get("block_type")
            block_content = params.get("block_content")
            if block_type and block_content:
                data[block_type] = block_content
            elif params.get("archived") is not None:
                data["archived"] = params.get("archived")
                
        # Search operations
        elif operation == "search":
            data = {}
            if params.get("query"):
                data["query"] = params.get("query")
            if params.get("filter"):
                data["filter"] = params.get("filter")
            if params.get("sort"):
                data["sort"] = params.get("sort")
            if params.get("start_cursor"):
                data["start_cursor"] = params.get("start_cursor")
            if params.get("page_size"):
                data["page_size"] = min(params.get("page_size", 10), 100)
                
        # Comment operations
        elif operation == "create_comment":
            data = {
                "parent": params.get("parent"),
                "rich_text": params.get("rich_text", [])
            }
            
        # For operations with query parameters instead of body
        elif operation in ["retrieve_comments"]:
            query_params = {}
            if params.get("block_id"):
                query_params["block_id"] = params.get("block_id")
            if params.get("page_id"):
                query_params["page_id"] = params.get("page_id")
            if params.get("start_cursor"):
                query_params["start_cursor"] = params.get("start_cursor")
            if params.get("page_size"):
                query_params["page_size"] = min(params.get("page_size", 10), 100)
            return query_params
            
        elif operation in ["list_users"]:
            query_params = {}
            if params.get("start_cursor"):
                query_params["start_cursor"] = params.get("start_cursor")
            if params.get("page_size"):
                query_params["page_size"] = min(params.get("page_size", 10), 100)
            return query_params
        
        return data
    
    def _process_result(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process result based on operation type."""
        if result.get("status") != "success":
            return result
        
        response_data = result.get("data", {})
        
        # Ensure Notion-style response format
        notion_result = {
            "status": "success",
            "result": response_data,
            "error": None,
            "object": response_data,
            "results": response_data.get("results", []),
            "has_more": response_data.get("has_more", False),
            "next_cursor": response_data.get("next_cursor")
        }
        
        # For list operations, extract results array
        if isinstance(response_data, dict) and "results" in response_data:
            notion_result["results"] = response_data["results"]
            notion_result["has_more"] = response_data.get("has_more", False)
            notion_result["next_cursor"] = response_data.get("next_cursor")
        elif isinstance(response_data, list):
            notion_result["results"] = response_data
            
        return notion_result
    
    async def close(self):
        """Clean up resources."""
        if self.universal_node:
            await self.universal_node.close()


if __name__ == "__main__":
    import asyncio
    
    async def test():
        node = NotionNode()
        
        # Test list users (simplest operation)
        test_data = {
            "params": {
                "operation": "list_users",
                "token": "YOUR_NOTION_TOKEN_HERE",  # Replace with actual token
            }
        }
        
        result = await node.execute(test_data)
        print(f"Result: {result}")
        
        await node.close()
    
    # Uncomment to test
    asyncio.run(test())