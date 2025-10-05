import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class GenericNode:
    """
    Generic node implementation that can be used as a fallback for various node types.
    """
    
    def __init__(self, node_type: str = None, sandbox_timeout: Optional[int] = None):
        self.node_type = node_type or "generic"
        self.sandbox_timeout = sandbox_timeout
        self.resources = {}
        self.execution_manager = None
    
    def set_execution_manager(self, execution_manager):
        """Set the execution manager for this node."""
        self.execution_manager = execution_manager
        logger.debug(f"Set execution manager for {self.node_type}Node")
    
    def set_resources(self, resources: Dict[str, Any]):
        """Set resources for this node."""
        self.resources = resources
        logger.debug(f"Set resources for {self.node_type}Node")
    
    async def execute_async(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronously execute the generic node operation.
        
        Args:
            node_data: Node data including operation and input
            
        Returns:
            Execution result
        """
        try:
            # Extract operation and input data
            operation = node_data.get('operation', '').lower()
            input_data = node_data.get('input', {})
            params = node_data.get('params', {})
            
            logger.info(f"Executing {self.node_type}Node for operation: {operation}")
            
            # Dispatch based on operation type
            if operation == 'get':
                result = await self.handle_get(input_data, params)
            elif operation == 'post':
                result = await self.handle_post(input_data, params)
            elif operation == 'put':
                result = await self.handle_put(input_data, params)
            elif operation == 'delete':
                result = await self.handle_delete(input_data, params)
            else:
                result = {
                    "status": "error",
                    "message": f"Unsupported operation: {operation}",
                    "output": None
                }
            
            return {
                **result,
                "node_type": self.node_type
            }
            
        except Exception as e:
            error_message = f"Error in {self.node_type}Node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "message": error_message,
                "output": None,
                "node_type": self.node_type
            }
    
    def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronously execute the generic node operation.
        
        Args:
            node_data: Node data including operation and input
            
        Returns:
            Execution result
        """
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.execute_async(node_data))
        finally:
            loop.close()
    
    async def handle_get(self, input_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle GET operation.
        
        Args:
            input_data: Input data
            params: Operation parameters
            
        Returns:
            Operation result
        """
        return {
            "status": "success",
            "message": f"GET operation handled by {self.node_type}Node",
            "output": input_data
        }
    
    async def handle_post(self, input_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle POST operation.
        
        Args:
            input_data: Input data
            params: Operation parameters
            
        Returns:
            Operation result
        """
        return {
            "status": "success",
            "message": f"POST operation handled by {self.node_type}Node",
            "output": input_data
        }
    
    async def handle_put(self, input_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle PUT operation.
        
        Args:
            input_data: Input data
            params: Operation parameters
            
        Returns:
            Operation result
        """
        return {
            "status": "success",
            "message": f"PUT operation handled by {self.node_type}Node",
            "output": input_data
        }
    
    async def handle_delete(self, input_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle DELETE operation.
        
        Args:
            input_data: Input data
            params: Operation parameters
            
        Returns:
            Operation result
        """
        return {
            "status": "success",
            "message": f"DELETE operation handled by {self.node_type}Node",
            "output": input_data
        }
    
    def validate_schema(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the node data against the schema.
        
        Args:
            node_data: Node data to validate
            
        Returns:
            Validated node data
        """
        # In a real implementation, this would validate against a schema
        params = node_data.get("params", {})
        
        # Perform custom validation
        custom_validation = self.validate_custom(node_data)
        
        # Return validated data
        return params
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Custom validation logic to be overridden by subclasses.
        
        Args:
            node_data: Node data to validate
            
        Returns:
            Any validation results or metadata
        """
        return {}
    
    def resolve_placeholders(self, text: str, context: Dict[str, Any]) -> str:
        """
        Resolve placeholders in text using context data.
        
        Args:
            text: Text with placeholders
            context: Context data for resolution
            
        Returns:
            Text with resolved placeholders
        """
        if not isinstance(text, str):
            return text
            
        # Simple placeholder resolution
        if "{{" in text and "}}" in text:
            try:
                # Find all placeholders
                import re
                placeholders = re.findall(r'{{(.*?)}}', text)
                
                # Replace each placeholder
                result = text
                for placeholder in placeholders:
                    path = placeholder.strip().split('.')
                    value = context
                    
                    try:
                        for key in path:
                            if isinstance(value, dict) and key in value:
                                value = value[key]
                            else:
                                # Placeholder path not found
                                value = f"{{{{{placeholder}}}}}"
                                break
                        
                        # Replace the placeholder with the value
                        if value is not None and not isinstance(value, (dict, list)):
                            result = result.replace(f"{{{{{placeholder}}}}}", str(value))
                    except Exception as e:
                        logger.error(f"Error resolving placeholder '{placeholder}': {str(e)}")
                
                return result
            except Exception as e:
                logger.error(f"Error resolving placeholders: {str(e)}")
                
        return text