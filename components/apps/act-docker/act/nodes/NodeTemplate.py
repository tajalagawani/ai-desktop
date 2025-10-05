"""
{SERVICE_NAME} Node - Template for creating new API integration nodes.
"""

import logging
import json
import asyncio
import time
import os
from typing import Dict, Any, List, Optional, Union, Tuple

# Import required libraries (will be replaced per node)
# import service_specific_sdk

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    except ImportError:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )

logger = logging.getLogger(__name__)

class {SERVICE_NAME}Operation:
    """Operations available on {SERVICE_NAME} API."""
    # Add operations based on research
    LIST = "list"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    GET = "get"

class {SERVICE_NAME}Node(BaseNode):
    """
    Node for interacting with {SERVICE_NAME} API.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.client = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the {SERVICE_NAME} node."""
        return NodeSchema(
            node_type="{service_name_lower}",
            version="1.0.0",
            description="Interacts with {SERVICE_NAME} API for {service_description}",
            parameters=[
                # Basic parameters
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with {SERVICE_NAME} API",
                    required=True,
                    enum=[
                        {SERVICE_NAME}Operation.LIST,
                        {SERVICE_NAME}Operation.CREATE,
                        {SERVICE_NAME}Operation.UPDATE,
                        {SERVICE_NAME}Operation.DELETE,
                        {SERVICE_NAME}Operation.GET
                    ]
                ),
                
                # Authentication parameters (customize based on research)
                NodeParameter(
                    name="api_key",
                    type=NodeParameterType.STRING,
                    description="{SERVICE_NAME} API key",
                    required=True
                ),
                
                # Common parameters (customize based on API)
                NodeParameter(
                    name="resource_id",
                    type=NodeParameterType.STRING,
                    description="Resource ID for operations that require it",
                    required=False
                ),
                
                NodeParameter(
                    name="data",
                    type=NodeParameterType.OBJECT,
                    description="Data for create/update operations",
                    required=False
                ),
                
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Max number of items to return",
                    required=False,
                    default=100
                ),
                
                NodeParameter(
                    name="filters",
                    type=NodeParameterType.OBJECT,
                    description="Filters for list operations",
                    required=False
                ),
            ],
            
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "resource_id": NodeParameterType.STRING
            },
            
            tags=["{service_name_lower}", "api", "integration"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for API credentials
        if not params.get("api_key"):
            raise NodeValidationError("{SERVICE_NAME} API key is required")
            
        # Validate based on operation
        if operation in [{SERVICE_NAME}Operation.UPDATE, {SERVICE_NAME}Operation.DELETE, {SERVICE_NAME}Operation.GET]:
            if not params.get("resource_id"):
                raise NodeValidationError("Resource ID is required for this operation")
                
        if operation in [{SERVICE_NAME}Operation.CREATE, {SERVICE_NAME}Operation.UPDATE]:
            if not params.get("data"):
                raise NodeValidationError("Data is required for create/update operations")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the {SERVICE_NAME} node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize client
            await self._initialize_client(validated_data)
            
            # Execute the appropriate operation
            if operation == {SERVICE_NAME}Operation.LIST:
                return await self._operation_list(validated_data)
            elif operation == {SERVICE_NAME}Operation.CREATE:
                return await self._operation_create(validated_data)
            elif operation == {SERVICE_NAME}Operation.UPDATE:
                return await self._operation_update(validated_data)
            elif operation == {SERVICE_NAME}Operation.DELETE:
                return await self._operation_delete(validated_data)
            elif operation == {SERVICE_NAME}Operation.GET:
                return await self._operation_get(validated_data)
            else:
                error_message = f"Unknown operation: {operation}"
                logger.error(error_message)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_message,
                    "resource_id": None
                }
                
        except Exception as e:
            error_message = f"Error in {SERVICE_NAME} node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "resource_id": None
            }
    
    async def _initialize_client(self, params: Dict[str, Any]):
        """Initialize the API client."""
        api_key = params.get("api_key")
        # Initialize client based on service SDK
        # self.client = ServiceClient(api_key=api_key)
        pass
    
    # Operation Methods (customize based on API capabilities)
    
    async def _operation_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List resources."""
        try:
            limit = params.get("limit", 100)
            filters = params.get("filters", {})
            
            # Implement API call
            # result = await self.client.list(limit=limit, **filters)
            result = {"message": "List operation not implemented"}
            
            return {
                "status": "success",
                "result": result,
                "error": None,
                "resource_id": None
            }
            
        except Exception as e:
            error_message = f"{SERVICE_NAME} API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "resource_id": None
            }
    
    async def _operation_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource."""
        try:
            data = params.get("data", {})
            
            # Implement API call
            # result = await self.client.create(data)
            result = {"message": "Create operation not implemented", "data": data}
            
            return {
                "status": "success",
                "result": result,
                "error": None,
                "resource_id": result.get("id")
            }
            
        except Exception as e:
            error_message = f"{SERVICE_NAME} API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "resource_id": None
            }
    
    async def _operation_update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing resource."""
        try:
            resource_id = params.get("resource_id")
            data = params.get("data", {})
            
            # Implement API call
            # result = await self.client.update(resource_id, data)
            result = {"message": "Update operation not implemented", "id": resource_id, "data": data}
            
            return {
                "status": "success",
                "result": result,
                "error": None,
                "resource_id": resource_id
            }
            
        except Exception as e:
            error_message = f"{SERVICE_NAME} API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "resource_id": params.get("resource_id")
            }
    
    async def _operation_delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a resource."""
        try:
            resource_id = params.get("resource_id")
            
            # Implement API call
            # result = await self.client.delete(resource_id)
            result = {"message": "Delete operation not implemented", "id": resource_id}
            
            return {
                "status": "success",
                "result": result,
                "error": None,
                "resource_id": resource_id
            }
            
        except Exception as e:
            error_message = f"{SERVICE_NAME} API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "resource_id": params.get("resource_id")
            }
    
    async def _operation_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific resource."""
        try:
            resource_id = params.get("resource_id")
            
            # Implement API call
            # result = await self.client.get(resource_id)
            result = {"message": "Get operation not implemented", "id": resource_id}
            
            return {
                "status": "success",
                "result": result,
                "error": None,
                "resource_id": resource_id
            }
            
        except Exception as e:
            error_message = f"{SERVICE_NAME} API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "resource_id": params.get("resource_id")
            }

# Test function template
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def run_tests():
        print("=== {SERVICE_NAME} Node Test Suite ===")
        
        # Get API credentials
        api_key = os.environ.get("{SERVICE_NAME_UPPER}_API_KEY")
        if not api_key:
            api_key = input("Enter {SERVICE_NAME} API key: ")
            if not api_key:
                print("API key is required for testing")
                return
        
        node = {SERVICE_NAME}Node()
        
        # Basic test cases
        test_cases = [
            {
                "name": "List Resources",
                "params": {
                    "operation": {SERVICE_NAME}Operation.LIST,
                    "api_key": api_key,
                    "limit": 10
                },
                "expected_status": "success"
            }
        ]
        
        for test_case in test_cases:
            print(f"\\nRunning test: {test_case['name']}")
            
            try:
                node_data = {"params": test_case["params"]}
                result = await node.execute(node_data)
                
                if result["status"] == test_case["expected_status"]:
                    print(f"✅ PASS: {test_case['name']}")
                    if result["result"]:
                        print(f"Response: {str(result['result'])[:150]}...")
                else:
                    print(f"❌ FAIL: {test_case['name']}")
                    print(f"Error: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        print("\\nTests completed!")

    asyncio.run(run_tests())

# Registry registration
try:
    from node_registry import NodeRegistry
    registry = NodeRegistry()
    registry.register("{service_name_lower}", {SERVICE_NAME}Node)
    logger.info("Successfully registered {SERVICE_NAME}Node with registry")
except ImportError:
    logger.warning("Could not register {SERVICE_NAME}Node with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")