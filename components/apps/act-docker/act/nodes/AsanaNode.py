#!/usr/bin/env python3
"""
Asana Node - Pure config-driven implementation using UniversalRequestNode
Configuration is embedded directly in the node - no separate config.json needed
Following exact OpenAI node pattern
"""

import logging
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        from  base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Import the UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from .universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class AsanaNode(BaseNode):
    """
    Pure config-driven Asana node with embedded configuration.
    All operations are handled by UniversalRequestNode based on this config.
    """
    
    node_type = "asana"  # Add this for node discovery
    
    # Embedded configuration for Asana API
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "asana",
            "display_name": "Asana",
            "description": "Comprehensive Asana API integration for project management, task tracking, and team collaboration",
            "category": "productivity",
            "vendor": "asana",
            "version": "1.0.0",
            "author": "ACT Workflow",
            "tags": ["project-management", "tasks", "collaboration", "productivity", "teams"],
            "documentation_url": "https://developers.asana.com/docs",
            "icon": "https://asana.com/favicon.ico",
            "color": "#273347",
            "created_at": "2025-08-27T00:00:00Z",
            "updated_at": "2025-08-27T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://app.asana.com/api/1.0",
            "authentication": {
                "type": "bearer_token",
                "header": "Authorization"
            },
            "default_headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "retry_config": {
                "max_attempts": 3,
                "backoff": "exponential",
                "retriable_codes": [429, 500, 502, 503, 504]
            },
            "rate_limiting": {
                "requests_per_second": 10,
                "burst_size": 5
            },
            "timeouts": {
                "connect": 10.0,
                "read": 30.0,
                "total": 60.0
            }
        },
        
        # All parameters with complete metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "Asana personal access token",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "minLength": 10
                }
            },
            "operation": {
                "type": "string",
                "description": "The Asana operation to perform",
                "required": True,
                "group": "Operation",
                "enum": ["list_workspaces", "get_workspace", "list_projects", "get_project", "create_task", "get_task", "update_task", "delete_task", "list_tasks"]
            },
            "workspace_id": {
                "type": "string",
                "description": "Workspace ID",
                "required": False,
                "group": "Workspace"
            },
            "project_id": {
                "type": "string",
                "description": "Project ID",
                "required": False,
                "group": "Project"
            },
            "task_id": {
                "type": "string",
                "description": "Task ID",
                "required": False,
                "group": "Task"
            },
            "name": {
                "type": "string",
                "description": "Name of the resource (task, project, etc.)",
                "required": False,
                "group": "General"
            },
            "notes": {
                "type": "string",
                "description": "Description or notes for the resource",
                "required": False,
                "group": "General"
            },
            "assignee": {
                "type": "string",
                "description": "User ID to assign task to",
                "required": False,
                "group": "Task"
            },
            "due_on": {
                "type": "string",
                "description": "Due date (YYYY-MM-DD)",
                "required": False,
                "group": "Task"
            },
            "completed": {
                "type": "boolean",
                "description": "Whether task is completed",
                "required": False,
                "default": False,
                "group": "Task"
            },
            "limit": {
                "type": "number",
                "description": "Maximum number of results to return",
                "required": False,
                "default": 100,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 100
                }
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful Asana API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data"},
                    "result": {"type": "object", "description": "Full API response data"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Error code"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "list_workspaces": {
                "required_env_keys": ["ASANA_ACCESS_TOKEN"]
            },
            "get_workspace": {
                "required_env_keys": ["ASANA_ACCESS_TOKEN"]
            },
            "list_projects": {
                "required_env_keys": ["ASANA_ACCESS_TOKEN"]
            },
            "get_project": {
                "required_env_keys": ["ASANA_ACCESS_TOKEN"]
            },
            "create_task": {
                "required_env_keys": ["ASANA_ACCESS_TOKEN"]
            },
            "get_task": {
                "required_env_keys": ["ASANA_ACCESS_TOKEN"]
            },
            "update_task": {
                "required_env_keys": ["ASANA_ACCESS_TOKEN"]
            },
            "delete_task": {
                "required_env_keys": ["ASANA_ACCESS_TOKEN"]
            },
            "list_tasks": {
                "required_env_keys": ["ASANA_ACCESS_TOKEN"]
            }
        },
        
        # Error codes specific to Asana
        "error_codes": {
            "400": "Bad Request - Invalid parameters",
            "401": "Unauthorized - Invalid access token",
            "403": "Forbidden - Access denied",
            "404": "Not Found - Resource not found",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error",
            "503": "Service Unavailable"
        }
    }
    
    # Operation definitions with complete metadata
    OPERATIONS = {
        "list_workspaces": {
            "method": "GET",
            "endpoint": "/workspaces",
            "required_params": [],
            "optional_params": ["limit"],
            "body_parameters": [],
            "display_name": "List Workspaces",
            "description": "Get all workspaces accessible to the authenticated user",
            "group": "Workspaces",
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "array",
            "examples": [
                {
                    "name": "List all workspaces",
                    "input": {}
                }
            ]
        },
        "get_workspace": {
            "method": "GET",
            "endpoint": "/workspaces/{workspace_id}",
            "required_params": ["workspace_id"],
            "optional_params": [],
            "body_parameters": [],
            "display_name": "Get Workspace",
            "description": "Get details of a specific workspace",
            "group": "Workspaces",
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "object"
        },
        "list_projects": {
            "method": "GET",
            "endpoint": "/projects",
            "required_params": [],
            "optional_params": ["workspace_id", "limit"],
            "body_parameters": [],
            "display_name": "List Projects",
            "description": "Get all projects in a workspace",
            "group": "Projects",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array"
        },
        "get_project": {
            "method": "GET",
            "endpoint": "/projects/{project_id}",
            "required_params": ["project_id"],
            "optional_params": [],
            "body_parameters": [],
            "display_name": "Get Project",
            "description": "Get details of a specific project",
            "group": "Projects",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object"
        },
        "create_task": {
            "method": "POST",
            "endpoint": "/tasks",
            "required_params": ["name"],
            "optional_params": ["workspace_id", "project_id", "notes", "assignee", "due_on", "completed"],
            "body_parameters": ["name", "workspace", "projects", "notes", "assignee", "due_on", "completed"],
            "display_name": "Create Task",
            "description": "Create a new task",
            "group": "Tasks",
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object"
        },
        "get_task": {
            "method": "GET",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id"],
            "optional_params": [],
            "body_parameters": [],
            "display_name": "Get Task",
            "description": "Get details of a specific task",
            "group": "Tasks",
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "object"
        },
        "update_task": {
            "method": "PUT",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id"],
            "optional_params": ["name", "notes", "assignee", "due_on", "completed"],
            "body_parameters": ["name", "notes", "assignee", "due_on", "completed"],
            "display_name": "Update Task",
            "description": "Update an existing task",
            "group": "Tasks",
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object"
        },
        "delete_task": {
            "method": "DELETE",
            "endpoint": "/tasks/{task_id}",
            "required_params": ["task_id"],
            "optional_params": [],
            "body_parameters": [],
            "display_name": "Delete Task",
            "description": "Delete a task",
            "group": "Tasks",
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object"
        },
        "list_tasks": {
            "method": "GET",
            "endpoint": "/tasks",
            "required_params": [],
            "optional_params": ["project_id", "assignee", "completed", "limit"],
            "body_parameters": [],
            "display_name": "List Tasks",
            "description": "List tasks based on filters",
            "group": "Tasks",
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array"
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create UniversalRequestNode with full config and operations
        # UniversalRequestNode expects the full config dict, not just api_config
        self.universal_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
    
    def get_schema(self) -> NodeSchema:
        """Return basic schema."""
        return NodeSchema(
            node_type="asana",
            version="1.0.0",
            description="Asana API integration with embedded configuration",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="api_key",
                    type=NodeParameterType.SECRET,
                    description="Asana personal access token",
                    required=True
                ),
                # Dynamic parameters based on operation
                NodeParameter(
                    name="workspace_id",
                    type=NodeParameterType.STRING,
                    description="Workspace ID",
                    required=False
                ),
                NodeParameter(
                    name="project_id",
                    type=NodeParameterType.STRING,
                    description="Project ID",
                    required=False
                ),
                NodeParameter(
                    name="task_id",
                    type=NodeParameterType.STRING,
                    description="Task ID",
                    required=False
                ),
                NodeParameter(
                    name="name",
                    type=NodeParameterType.STRING,
                    description="Resource name",
                    required=False
                ),
                NodeParameter(
                    name="notes",
                    type=NodeParameterType.STRING,
                    description="Resource notes/description",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "data": NodeParameterType.OBJECT
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
            
            # Prepare request data based on operation
            request_data = self._prepare_request_data(operation, params)
            
            # Prepare parameters for UniversalRequestNode
            # The UniversalRequestNode expects all parameters in the params dict
            universal_params = {
                "operation": operation,
                "api_key": params.get("api_key"),
                **request_data  # Merge in the prepared request data
            }
            
            # Create node_data for UniversalRequestNode
            universal_node_data = {
                "params": universal_params
            }
            
            # Execute via UniversalRequestNode
            result = await self.universal_node.execute(universal_node_data)
            
            # Process and enhance the result
            return self._process_result(operation, result)
            
        except Exception as e:
            logger.error(f"Asana node error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "result": None
            }
    
    def _prepare_request_data(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request data based on operation."""
        data = {}
        
        # Path parameters
        if params.get("workspace_id"):
            data["workspace_id"] = params["workspace_id"]
        if params.get("project_id"):
            data["project_id"] = params["project_id"]
        if params.get("task_id"):
            data["task_id"] = params["task_id"]
        
        # Body parameters for POST/PUT requests
        if operation == "create_task":
            task_data = {
                "name": params.get("name")
            }
            if params.get("notes"):
                task_data["notes"] = params["notes"]
            if params.get("assignee"):
                task_data["assignee"] = params["assignee"]
            if params.get("due_on"):
                task_data["due_on"] = params["due_on"]
            if params.get("completed") is not None:
                task_data["completed"] = params["completed"]
            if params.get("workspace_id"):
                task_data["workspace"] = params["workspace_id"]
            if params.get("project_id"):
                task_data["projects"] = [params["project_id"]]
            
            data.update({"data": task_data})
            
        elif operation == "update_task":
            task_data = {}
            if params.get("name"):
                task_data["name"] = params["name"]
            if params.get("notes"):
                task_data["notes"] = params["notes"]
            if params.get("assignee"):
                task_data["assignee"] = params["assignee"]
            if params.get("due_on"):
                task_data["due_on"] = params["due_on"]
            if params.get("completed") is not None:
                task_data["completed"] = params["completed"]
            
            if task_data:
                data.update({"data": task_data})
        
        # Query parameters for GET requests
        elif operation in ["list_projects", "list_tasks"]:
            if params.get("workspace_id"):
                data["workspace"] = params["workspace_id"]
            if params.get("project_id"):
                data["project"] = params["project_id"]
            if params.get("assignee"):
                data["assignee"] = params["assignee"]
            if params.get("completed") is not None:
                data["completed"] = params["completed"]
            if params.get("limit"):
                data["limit"] = params["limit"]
        
        return data
    
    def _process_result(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process result based on operation type."""
        if result.get("status") != "success":
            return result
        
        # Asana API returns data wrapped in a "data" field
        # UniversalRequestNode already handles this, but we can add operation-specific processing
        
        return result
    
    async def close(self):
        """Clean up resources."""
        # UniversalRequestNode doesn't have a close method
        # It uses session per request, so no cleanup needed
        pass

# That's it! Everything is embedded in the node:
# 1. CONFIG defines the API connection settings
# 2. OPERATIONS defines the available operations
# 3. UniversalRequestNode handles all HTTP complexity
# 4. Node just maps operations to HTTP requests

if __name__ == "__main__":
    import asyncio
    
    async def test():
        node = AsanaNode()
        
        # Test listing workspaces
        test_data = {
            "params": {
                "operation": "list_workspaces",
                "api_key": "YOUR_ASANA_TOKEN_HERE"  # Replace with actual token
            }
        }
        
        result = await node.execute(test_data)
        print(f"Result: {result}")
        
        await node.close()
    
    # Uncomment to test
    # asyncio.run(test())