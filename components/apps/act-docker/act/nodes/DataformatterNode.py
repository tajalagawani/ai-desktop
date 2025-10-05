"""
DataformatterNode - Performs data formatting operations to prepare data for other nodes.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional, Union, Callable
import copy
import re

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

# Configure logging
logger = logging.getLogger(__name__)

class FormatterOperationType:
    """Formatter operation types."""
    ENSURE_ARRAY = "ensure_array"
    ENSURE_OBJECT = "ensure_object"
    STRINGIFY = "stringify"
    PARSE_JSON = "parse_json"
    EXTRACT_VALUES = "extract_values"
    CLEAN_TEXT = "clean_text"
    TRANSFORM = "transform"
    FORMAT_MESSAGES = "format_messages"
    CONVERT_TO_TEMPLATE = "convert_to_template"

class DataformatterNode(BaseNode):
    """
    Node for formatting data to be compatible with other nodes.
    Provides functionality to ensure proper data structures, formats, and transformations.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
    
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the data formatter node."""
        return NodeSchema(
            node_type="Dataformatter",
            version="1.0.0",
            description="Formats data to be compatible with other nodes",
            parameters=[
                # Basic parameters
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Type of formatting operation to perform",
                    required=True,
                    enum=[
                        FormatterOperationType.ENSURE_ARRAY,
                        FormatterOperationType.ENSURE_OBJECT,
                        FormatterOperationType.STRINGIFY,
                        FormatterOperationType.PARSE_JSON,
                        FormatterOperationType.EXTRACT_VALUES,
                        FormatterOperationType.CLEAN_TEXT,
                        FormatterOperationType.TRANSFORM,
                        FormatterOperationType.FORMAT_MESSAGES,
                        FormatterOperationType.CONVERT_TO_TEMPLATE
                    ]
                ),
                NodeParameter(
                    name="input",
                    type=NodeParameterType.ANY,
                    description="Input data to format",
                    required=True
                ),
                
                # Array formatting parameters
                NodeParameter(
                    name="wrap_if_not_array",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to wrap the input in an array if it's not already an array",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="flatten_arrays",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to flatten nested arrays",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="ensure_object_keys",
                    type=NodeParameterType.ARRAY,
                    description="Ensure that objects in the array have these keys",
                    required=False
                ),
                
                # Object formatting parameters
                NodeParameter(
                    name="default_values",
                    type=NodeParameterType.OBJECT,
                    description="Default values for keys when ensuring object structure",
                    required=False,
                    default={}
                ),
                NodeParameter(
                    name="remove_keys",
                    type=NodeParameterType.ARRAY,
                    description="Keys to remove from objects",
                    required=False
                ),
                
                # String formatting parameters
                NodeParameter(
                    name="escape_quotes",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to escape quotes in strings",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="pretty_print",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to pretty-print JSON strings",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="indent",
                    type=NodeParameterType.NUMBER,
                    description="Indentation level for pretty-printing",
                    required=False,
                    default=2
                ),
                
                # Extraction parameters
                NodeParameter(
                    name="extract_path",
                    type=NodeParameterType.STRING,
                    description="Path to extract values from (dot notation)",
                    required=False
                ),
                NodeParameter(
                    name="extract_regex",
                    type=NodeParameterType.STRING,
                    description="Regular expression to extract values with",
                    required=False
                ),
                
                # Text cleaning parameters
                NodeParameter(
                    name="remove_html",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to remove HTML tags",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="remove_extra_whitespace",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to remove extra whitespace",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="max_length",
                    type=NodeParameterType.NUMBER,
                    description="Maximum length of text",
                    required=False
                ),
                
                # Transformation parameters
                NodeParameter(
                    name="transform_script",
                    type=NodeParameterType.STRING,
                    description="JavaScript function to transform the data",
                    required=False
                ),
                
                # Message formatting parameters (for LLM APIs)
                NodeParameter(
                    name="message_role",
                    type=NodeParameterType.STRING,
                    description="Role for message formatting",
                    required=False,
                    default="user",
                    enum=["system", "user", "assistant", "function"]
                ),
                NodeParameter(
                    name="system_message",
                    type=NodeParameterType.STRING,
                    description="System message to add to the beginning of the messages array",
                    required=False
                ),
                NodeParameter(
                    name="content_key",
                    type=NodeParameterType.STRING,
                    description="Key to use for the content field in messages",
                    required=False,
                    default="content"
                ),
                
                # Template conversion parameters
                NodeParameter(
                    name="template_format",
                    type=NodeParameterType.STRING,
                    description="Format for template conversion",
                    required=False,
                    default="handlebars",
                    enum=["handlebars", "jinja", "custom"]
                ),
                NodeParameter(
                    name="template_custom_prefix",
                    type=NodeParameterType.STRING,
                    description="Custom prefix for template variables",
                    required=False,
                    default="{{"
                ),
                NodeParameter(
                    name="template_custom_suffix",
                    type=NodeParameterType.STRING,
                    description="Custom suffix for template variables",
                    required=False,
                    default="}}"
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "data": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "format_type": NodeParameterType.STRING,
                "original_type": NodeParameterType.STRING
            },
            
            # Add metadata
            tags=["utility", "formatting", "transformation", "preprocessing"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation for data formatter parameters."""
        params = node_data.get("params", {})
        
        # Operation can be in params or directly in node_data (for tests)
        operation = params.get("operation")
        if not operation and "operation" in node_data:
            operation = node_data.get("operation")
            
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Input can be in params or directly in node_data (for tests)
        input_present = "input" in params or "input" in node_data
        if not input_present:
            raise NodeValidationError("Input is required")
        
        # Validate operation-specific parameters
        if operation == FormatterOperationType.EXTRACT_VALUES:
            extract_path = params.get("extract_path")
            if not extract_path and "extract_path" in node_data:
                extract_path = node_data.get("extract_path")
                
            extract_regex = params.get("extract_regex")
            if not extract_regex and "extract_regex" in node_data:
                extract_regex = node_data.get("extract_regex")
                
            if not extract_path and not extract_regex:
                raise NodeValidationError("Either extract_path or extract_regex is required for EXTRACT_VALUES operation")
        
        elif operation == FormatterOperationType.TRANSFORM:
            transform_script = params.get("transform_script")
            if not transform_script and "transform_script" in node_data:
                transform_script = node_data.get("transform_script")
                
            if not transform_script:
                raise NodeValidationError("Transform script is required for TRANSFORM operation")
        
        elif operation == FormatterOperationType.CONVERT_TO_TEMPLATE:
            template_format = params.get("template_format", "handlebars")
            if "template_format" in node_data:
                template_format = node_data.get("template_format")
                
            if template_format == "custom":
                template_custom_prefix = params.get("template_custom_prefix")
                if not template_custom_prefix and "template_custom_prefix" in node_data:
                    template_custom_prefix = node_data.get("template_custom_prefix")
                    
                template_custom_suffix = params.get("template_custom_suffix")
                if not template_custom_suffix and "template_custom_suffix" in node_data:
                    template_custom_suffix = node_data.get("template_custom_suffix")
                    
                if not template_custom_prefix or not template_custom_suffix:
                    raise NodeValidationError("Custom prefix and suffix are required for custom template format")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the data formatter node."""
        try:
            # Get parameters from node_data or params
            params = node_data.get("params", {})
            
            # Get operation from params or directly from node_data (for tests)
            operation = params.get("operation")
            if not operation and "operation" in node_data:
                operation = node_data.get("operation")
                
            if not operation:
                raise ValueError("Operation is required")
            
            # Get input from params or directly from node_data (for tests)
            input_data = params.get("input")
            if input_data is None and "input" in node_data:
                input_data = node_data.get("input")
            
            # Create a combined params dictionary for operation functions
            combined_params = {}
            # First add node_data (lower priority)
            for key, value in node_data.items():
                if key not in ["params", "operation", "input"]:
                    combined_params[key] = value
            # Then add params (higher priority)
            for key, value in params.items():
                if key not in ["operation", "input"]:
                    combined_params[key] = value
            
            # Determine original type
            original_type = self._get_data_type(input_data)
            
            # Execute the appropriate operation
            if operation == FormatterOperationType.ENSURE_ARRAY:
                result = self._ensure_array(input_data, combined_params)
                format_type = "array"
                
            elif operation == FormatterOperationType.ENSURE_OBJECT:
                result = self._ensure_object(input_data, combined_params)
                format_type = "object"
                
            elif operation == FormatterOperationType.STRINGIFY:
                result = self._stringify(input_data, combined_params)
                format_type = "string"
                
            elif operation == FormatterOperationType.PARSE_JSON:
                result = self._parse_json(input_data, combined_params)
                format_type = self._get_data_type(result)
                
            elif operation == FormatterOperationType.EXTRACT_VALUES:
                result = self._extract_values(input_data, combined_params)
                format_type = self._get_data_type(result)
                
            elif operation == FormatterOperationType.CLEAN_TEXT:
                result = self._clean_text(input_data, combined_params)
                format_type = "string"
                
            elif operation == FormatterOperationType.TRANSFORM:
                result = self._transform(input_data, combined_params)
                format_type = self._get_data_type(result)
                
            elif operation == FormatterOperationType.FORMAT_MESSAGES:
                result = self._format_messages(input_data, combined_params)
                format_type = "array"
                
            elif operation == FormatterOperationType.CONVERT_TO_TEMPLATE:
                result = self._convert_to_template(input_data, combined_params)
                format_type = "string"
                
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            return {
                "status": "success",
                "data": result,
                "error": None,
                "format_type": format_type,
                "original_type": original_type
            }
            
        except Exception as e:
            error_message = f"Error in dataformatter node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "data": None,
                "error": error_message,
                "format_type": None,
                "original_type": self._get_data_type(params.get("input") if "input" in params else node_data.get("input"))
            }
    
    def _get_data_type(self, data: Any) -> str:
        """
        Get the type of data.
        
        Args:
            data: Data to check
            
        Returns:
            Type of data as a string
        """
        if data is None:
            return "null"
        elif isinstance(data, list):
            return "array"
        elif isinstance(data, dict):
            return "object"
        elif isinstance(data, str):
            return "string"
        elif isinstance(data, bool):
            return "boolean"
        elif isinstance(data, (int, float)):
            return "number"
        else:
            return type(data).__name__
    
    def _ensure_array(self, data: Any, params: Dict[str, Any]) -> List[Any]:
        """
        Ensure the data is an array.
        
        Args:
            data: Data to ensure is an array
            params: Parameters for array formatting
            
        Returns:
            Data as an array
        """
        wrap_if_not_array = params.get("wrap_if_not_array", True)
        flatten_arrays = params.get("flatten_arrays", False)
        ensure_object_keys = params.get("ensure_object_keys", [])
        
        # Convert to array if not already
        if not isinstance(data, list):
            if data is None:
                result = []
            elif wrap_if_not_array:
                result = [data]
            else:
                raise ValueError("Input data is not an array")
        else:
            result = copy.deepcopy(data)
        
        # Flatten if requested
        if flatten_arrays:
            flattened = []
            for item in result:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            result = flattened
        
        # Ensure object keys if requested
        if ensure_object_keys and isinstance(ensure_object_keys, list) and len(ensure_object_keys) > 0:
            default_values = params.get("default_values", {})
            for i, item in enumerate(result):
                if isinstance(item, dict):
                    for key in ensure_object_keys:
                        if key not in item:
                            item[key] = default_values.get(key, None)
        
        return result
    
    def _ensure_object(self, data: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure the data is an object.
        
        Args:
            data: Data to ensure is an object
            params: Parameters for object formatting
            
        Returns:
            Data as an object
        """
        default_values = params.get("default_values", {})
        remove_keys = params.get("remove_keys", [])
        
        # Convert to object if not already
        if not isinstance(data, dict):
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                # Use the first object in the array
                result = copy.deepcopy(data[0])
            elif data is None:
                result = {}
            else:
                # Try to convert to object
                try:
                    if isinstance(data, str):
                        # Try to parse as JSON
                        result = json.loads(data)
                        if not isinstance(result, dict):
                            result = {"value": data}
                    else:
                        result = {"value": data}
                except json.JSONDecodeError:
                    result = {"value": data}
        else:
            result = copy.deepcopy(data)
        
        # Apply default values
        if default_values:
            for key, value in default_values.items():
                if key not in result:
                    result[key] = value
        
        # Remove keys
        if remove_keys:
            for key in remove_keys:
                if key in result:
                    del result[key]
        
        return result
    
    def _stringify(self, data: Any, params: Dict[str, Any]) -> str:
        """
        Convert data to a string.
        
        Args:
            data: Data to convert to a string
            params: Parameters for string formatting
            
        Returns:
            Data as a string
        """
        escape_quotes = params.get("escape_quotes", False)
        pretty_print = params.get("pretty_print", False)
        indent = params.get("indent", 2)
        
        # Convert to string
        if data is None:
            return ""
        
        if isinstance(data, (dict, list)):
            if pretty_print:
                result = json.dumps(data, indent=indent)
            else:
                result = json.dumps(data)
        else:
            result = str(data)
        
        # Escape quotes if requested
        if escape_quotes:
            result = result.replace('"', '\\"')
        
        return result
    
    def _parse_json(self, data: Any, params: Dict[str, Any]) -> Any:
        """
        Parse JSON string to an object.
        
        Args:
            data: JSON string to parse
            params: Parameters for JSON parsing
            
        Returns:
            Parsed data
        """
        # If already parsed, return as is
        if not isinstance(data, str):
            return data
        
        # Try to parse as JSON
        try:
            result = json.loads(data)
            return result
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {str(e)}")
    
    def _extract_values(self, data: Any, params: Dict[str, Any]) -> Any:
        """
        Extract values from data using path or regex.
        
        Args:
            data: Data to extract values from
            params: Parameters for extraction
            
        Returns:
            Extracted values
        """
        extract_path = params.get("extract_path")
        extract_regex = params.get("extract_regex")
        
        if extract_path:
            # Extract using path
            if isinstance(data, dict):
                return self._extract_from_path(data, extract_path)
            elif isinstance(data, list):
                results = []
                for item in data:
                    if isinstance(item, dict):
                        results.append(self._extract_from_path(item, extract_path))
                return results
            else:
                raise ValueError("Cannot extract values using path from non-object data")
                
        elif extract_regex:
            # Extract using regex
            if isinstance(data, str):
                matches = re.findall(extract_regex, data)
                return matches
            elif isinstance(data, list):
                results = []
                for item in data:
                    if isinstance(item, str):
                        matches = re.findall(extract_regex, item)
                        results.extend(matches)
                return results
            else:
                raise ValueError("Cannot extract values using regex from non-string data")
        
        return data
    
    def _extract_from_path(self, data: Dict[str, Any], path: str) -> Any:
        """
        Extract value from a nested dict using dot notation.
        
        Args:
            data: Dict to extract from
            path: Path in dot notation (e.g., "a.b.c")
            
        Returns:
            Extracted value or None if not found
        """
        parts = path.split(".")
        result = data
        
        for part in parts:
            if isinstance(result, dict) and part in result:
                result = result[part]
            elif isinstance(result, list) and part.isdigit() and int(part) < len(result):
                result = result[int(part)]
            else:
                return None
        
        return result
    
    def _clean_text(self, data: Any, params: Dict[str, Any]) -> str:
        """
        Clean text data.
        
        Args:
            data: Text to clean
            params: Parameters for text cleaning
            
        Returns:
            Cleaned text
        """
        if not isinstance(data, str):
            data = str(data)
        
        remove_html = params.get("remove_html", True)
        remove_extra_whitespace = params.get("remove_extra_whitespace", True)
        max_length = params.get("max_length")
        
        # Clean text
        if remove_html:
            # Remove HTML tags
            data = re.sub(r"<[^>]*>", " ", data)
        
        if remove_extra_whitespace:
            # Replace multiple whitespaces with a single space
            data = re.sub(r"\s+", " ", data)
            # Trim whitespace
            data = data.strip()
        
        if max_length and len(data) > max_length:
            # Truncate to max length
            data = data[:max_length]
        
        return data
    
    def _transform(self, data: Any, params: Dict[str, Any]) -> Any:
        """
        Transform data using a custom function.
        
        Args:
            data: Data to transform
            params: Parameters for transformation
            
        Returns:
            Transformed data
        """
        transform_script = params.get("transform_script")
        
        if not transform_script:
            return data
        
        # For demonstration purposes, we'll use a simple eval
        # In a real implementation, you'd want to use a safer execution environment
        try:
            # Create a local function
            local_vars = {"data": data}
            exec(f"def transform_func(data):\n{transform_script}", globals(), local_vars)
            result = local_vars["transform_func"](data)
            return result
        except Exception as e:
            raise ValueError(f"Failed to execute transform script: {str(e)}")
    
    def _format_messages(self, data: Any, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format data as an array of messages for LLM APIs.
        
        Args:
            data: Data to format as messages
            params: Parameters for message formatting
            
        Returns:
            Array of messages
        """
        message_role = params.get("message_role", "user")
        system_message = params.get("system_message")
        content_key = params.get("content_key", "content")
        
        # Initialize messages array
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        # Format input data as messages
        if isinstance(data, list):
            # Check if data is already in the right format
            if all(isinstance(item, dict) and "role" in item and content_key in item for item in data):
                # Already formatted correctly
                messages.extend(data)
            else:
                # Convert each item in the list to a message
                for item in data:
                    if isinstance(item, dict) and "role" in item and content_key in item:
                        # Already a message
                        messages.append(item)
                    elif isinstance(item, dict) and "role" in item and "content" in item:
                        # Already a message with content key as "content"
                        messages.append(item)
                    elif isinstance(item, dict):
                        # Convert dict to string
                        messages.append({
                            "role": message_role,
                            "content": json.dumps(item)
                        })
                    elif isinstance(item, str):
                        # Already a string
                        messages.append({
                            "role": message_role,
                            "content": item
                        })
                    else:
                        # Convert to string
                        messages.append({
                            "role": message_role,
                            "content": str(item)
                        })
        elif isinstance(data, dict):
            # Check if data is already a message
            if "role" in data and content_key in data:
                # Already a message
                messages.append(data)
            elif "role" in data and "content" in data:
                # Already a message with content key as "content"
                messages.append(data)
            else:
                # Convert dict to string
                messages.append({
                    "role": message_role,
                    "content": json.dumps(data)
                })
        elif isinstance(data, str):
            # Already a string
            messages.append({
                "role": message_role,
                "content": data
            })
        else:
            # Convert to string
            messages.append({
                "role": message_role,
                "content": str(data)
            })
        
        return messages
    
    def _convert_to_template(self, data: Any, params: Dict[str, Any]) -> str:
        """
        Convert data to a template string.
        
        Args:
            data: Data to convert to a template
            params: Parameters for template conversion
            
        Returns:
            Template string
        """
        template_format = params.get("template_format", "handlebars")
        template_custom_prefix = params.get("template_custom_prefix", "{{")
        template_custom_suffix = params.get("template_custom_suffix", "}}")
        
        # Convert to string if not already
        if not isinstance(data, str):
            data = str(data)
        
        # Replace template variables based on format
        if template_format == "handlebars":
            # Already in handlebars format
            return data
        elif template_format == "jinja":
            # Convert handlebars to jinja
            data = re.sub(r"{{([^}]+)}}", r"{{ \1 }}", data)
            return data
        elif template_format == "custom":
            # Convert handlebars to custom format
            data = re.sub(r"{{([^}]+)}}", f"{template_custom_prefix}\\1{template_custom_suffix}", data)
            return data
        else:
            return data

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("Dataformatter", DataformatterNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register DataformatterNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")

# Main test suite for DataformatterNode
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== DataformatterNode Test Suite ===")
        
        # Create an instance of the DataformatterNode
        node = DataformatterNode()
        
        # Define test cases
        test_cases = [
            {
                "name": "Ensure Array - Simple",
                "operation": FormatterOperationType.ENSURE_ARRAY,
                "input": "test string",
                "expected_result": ["test string"],
                "expected_format_type": "array"
            },
            {
                "name": "Ensure Array - Already Array",
                "operation": FormatterOperationType.ENSURE_ARRAY,
                "input": ["item1", "item2"],
                "expected_result": ["item1", "item2"],
                "expected_format_type": "array"
            },
            {
                "name": "Ensure Array - Flatten",
                "operation": FormatterOperationType.ENSURE_ARRAY,
                "input": [["item1", "item2"], "item3"],
                "flatten_arrays": True,
                "expected_result": ["item1", "item2", "item3"],
                "expected_format_type": "array"
            },
            {
                "name": "Ensure Object - From String",
                "operation": FormatterOperationType.ENSURE_OBJECT,
                "input": '{"key": "value"}',
                "expected_result": {"key": "value"},
                "expected_format_type": "object"
            },
            {
                "name": "Ensure Object - With Default Values",
                "operation": FormatterOperationType.ENSURE_OBJECT,
                "input": {"key1": "value1"},
                "default_values": {"key1": "default1", "key2": "default2"},
                "expected_result": {"key1": "value1", "key2": "default2"},
                "expected_format_type": "object"
            },
            {
                "name": "Stringify - Object",
                "operation": FormatterOperationType.STRINGIFY,
                "input": {"key": "value"},
                "pretty_print": True,
                "indent": 2,
                "expected_format_type": "string"
            },
            {
                "name": "Parse JSON - Valid",
                "operation": FormatterOperationType.PARSE_JSON,
                "input": '{"key": "value"}',
                "expected_result": {"key": "value"},
                "expected_format_type": "object"
            },
            {
                "name": "Extract Values - Path",
                "operation": FormatterOperationType.EXTRACT_VALUES,
                "input": {"user": {"name": "John", "age": 30}},
                "extract_path": "user.name",
                "expected_result": "John",
                "expected_format_type": "string"
            },
            {"name": "Extract Values - Regex",
                "operation": FormatterOperationType.EXTRACT_VALUES,
                "input": "Email: user@example.com and another@test.com",
                "extract_regex": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "expected_result": ["user@example.com", "another@test.com"],
                "expected_format_type": "array"
            },
            {
                "name": "Clean Text",
                "operation": FormatterOperationType.CLEAN_TEXT,
                "input": "<p>This is a <b>test</b> with   extra   spaces.</p>",
                "remove_html": True,
                "remove_extra_whitespace": True,
                "expected_result": "This is a test with extra spaces.",
                "expected_format_type": "string"
            },
            {
                "name": "Format Messages - String",
                "operation": FormatterOperationType.FORMAT_MESSAGES,
                "input": "This is a test message",
                "message_role": "user",
                "system_message": "You are a helpful assistant.",
                "expected_result": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "This is a test message"}
                ],
                "expected_format_type": "array"
            },
            {
                "name": "Format Messages - Object",
                "operation": FormatterOperationType.FORMAT_MESSAGES,
                "input": {"key": "value"},
                "expected_format_type": "array"
            },
            {
                "name": "Format Messages - Already Formatted",
                "operation": FormatterOperationType.FORMAT_MESSAGES,
                "input": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}],
                "expected_result": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}],
                "expected_format_type": "array"
            },
            {
                "name": "Convert to Template - Handlebars to Jinja",
                "operation": FormatterOperationType.CONVERT_TO_TEMPLATE,
                "input": "Hello {{name}}, your order #{{order_id}} is ready.",
                "template_format": "jinja",
                "expected_result": "Hello {{ name }}, your order #{{ order_id }} is ready.",
                "expected_format_type": "string"
            },
            {
                "name": "Transform - Custom Script",
                "operation": FormatterOperationType.TRANSFORM,
                "input": {"names": ["John", "Jane", "Bob"]},
                "transform_script": "    return {'user_count': len(data['names']), 'users': data['names']}",
                "expected_result": {"user_count": 3, "users": ["John", "Jane", "Bob"]},
                "expected_format_type": "object"
            }
        ]
        
        # Run test cases
        passed = 0
        failed = 0
        
        for test_case in test_cases:
            print(f"\nRunning test: {test_case['name']}")
            
            try:
                # Prepare node data - directly passing test case parameters
                node_data = {**test_case}
                
                # Remove test-specific keys
                for key in ["name", "expected_result", "expected_format_type"]:
                    if key in node_data:
                        node_data.pop(key)
                
                # Execute the node
                result = await node.execute(node_data)
                
                # Check if successful
                if result["status"] != "success":
                    print(f"❌ FAIL: {test_case['name']} - Unexpected error: {result['error']}")
                    failed += 1
                    continue
                
                # Check format type if expected
                if "expected_format_type" in test_case:
                    if result["format_type"] != test_case["expected_format_type"]:
                        print(f"❌ FAIL: {test_case['name']} - Expected format_type {test_case['expected_format_type']}, got {result['format_type']}")
                        failed += 1
                        continue
                
                # Check expected result if provided
                if "expected_result" in test_case:
                    if test_case["operation"] == FormatterOperationType.STRINGIFY:
                        # Special handling for stringify as we can't directly compare strings
                        expected_parsed = None
                        result_parsed = None
                        
                        try:
                            if isinstance(test_case["expected_result"], str):
                                expected_parsed = json.loads(test_case["expected_result"])
                        except:
                            expected_parsed = test_case["expected_result"]
                            
                        try:
                            if isinstance(result["data"], str):
                                result_parsed = json.loads(result["data"])
                        except:
                            result_parsed = result["data"]
                        
                        if expected_parsed is not None and result_parsed is not None:
                            if expected_parsed != result_parsed:
                                print(f"❌ FAIL: {test_case['name']} - Expected {test_case['expected_result']}, got {result['data']}")
                                failed += 1
                                continue
                    else:
                        if result["data"] != test_case["expected_result"]:
                            print(f"❌ FAIL: {test_case['name']} - Expected {test_case['expected_result']}, got {result['data']}")
                            failed += 1
                            continue
                
                print(f"✅ PASS: {test_case['name']}")
                passed += 1
                
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Unexpected exception: {str(e)}")
                failed += 1
        

        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {len(test_cases)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
    
    # Run tests
    import asyncio
    asyncio.run(run_tests())
            