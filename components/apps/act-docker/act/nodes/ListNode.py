"""
List Node - Manipulates lists with various operations like filtering, mapping, and aggregation.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Callable, Union
import asyncio
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

class ListOperationType:
    """List operation types."""
    FILTER = "filter"
    MAP = "map"
    REDUCE = "reduce"
    SORT = "sort"
    SLICE = "slice"
    APPEND = "append"
    MERGE = "merge"
    UNIQUE = "unique"
    FLATTEN = "flatten"
    GROUP = "group"
    COUNT = "count"
    JOIN = "join"
    SPLIT = "split"
    REVERSE = "reverse"
    ZIP = "zip"
    ENUMERATE = "enumerate"

class ListNode(BaseNode):
    """
    Node for performing operations on lists.
    Provides functionality for filtering, mapping, reducing, sorting, etc.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
    
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the list node."""
        return NodeSchema(
            node_type="list",
            version="1.0.0",
            description="Performs operations on lists including filtering, mapping, reducing, sorting, etc.",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform on the list",
                    required=True,
                    enum=[
                        ListOperationType.FILTER, ListOperationType.MAP, ListOperationType.REDUCE,
                        ListOperationType.SORT, ListOperationType.SLICE, ListOperationType.APPEND,
                        ListOperationType.MERGE, ListOperationType.UNIQUE, ListOperationType.FLATTEN,
                        ListOperationType.GROUP, ListOperationType.COUNT, ListOperationType.JOIN,
                        ListOperationType.SPLIT, ListOperationType.REVERSE, ListOperationType.ZIP,
                        ListOperationType.ENUMERATE
                    ]
                ),
                NodeParameter(
                    name="input_list",
                    type=NodeParameterType.ARRAY,
                    description="Input list to operate on",
                    required=True
                ),
                NodeParameter(
                    name="second_list",
                    type=NodeParameterType.ARRAY,
                    description="Second list for operations that require two lists (merge, zip)",
                    required=False
                ),
                NodeParameter(
                    name="filter_expression",
                    type=NodeParameterType.STRING,
                    description="Expression for filtering elements (for filter operation)",
                    required=False
                ),
                NodeParameter(
                    name="map_expression",
                    type=NodeParameterType.STRING,
                    description="Expression for mapping elements (for map operation)",
                    required=False
                ),
                NodeParameter(
                    name="reduce_expression",
                    type=NodeParameterType.STRING,
                    description="Expression for reducing elements (for reduce operation)",
                    required=False
                ),
                NodeParameter(
                    name="reduce_initial",
                    type=NodeParameterType.ANY,
                    description="Initial value for reduce operation",
                    required=False
                ),
                NodeParameter(
                    name="sort_key",
                    type=NodeParameterType.STRING,
                    description="Key to sort by (for sort operation)",
                    required=False
                ),
                NodeParameter(
                    name="sort_reverse",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to sort in reverse order (for sort operation)",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="start_index",
                    type=NodeParameterType.NUMBER,
                    description="Start index for slice operation",
                    required=False,
                    default=0
                ),
                NodeParameter(
                    name="end_index",
                    type=NodeParameterType.NUMBER,
                    description="End index for slice operation",
                    required=False
                ),
                NodeParameter(
                    name="group_key",
                    type=NodeParameterType.STRING,
                    description="Key to group by (for group operation)",
                    required=False
                ),
                NodeParameter(
                    name="join_delimiter",
                    type=NodeParameterType.STRING,
                    description="Delimiter for joining strings (for join operation)",
                    required=False,
                    default=","
                ),
                NodeParameter(
                    name="split_delimiter",
                    type=NodeParameterType.STRING,
                    description="Delimiter for splitting string (for split operation)",
                    required=False,
                    default=","
                ),
                NodeParameter(
                    name="use_javascript",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to use JavaScript for expressions (more powerful but less secure)",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="javascript_code",
                    type=NodeParameterType.STRING,
                    description="JavaScript code for more complex operations",
                    required=False
                )
            ],

            outputs={
                "result": NodeParameterType.ANY,
                "count": NodeParameterType.NUMBER,
                "status": NodeParameterType.STRING,
                "error": NodeParameterType.STRING
            },
            
            # Add metadata
            tags=["data-processing", "list", "array", "transformation"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the selected operation."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
        
        if not params.get("input_list"):
            raise NodeValidationError("Input list is required")
        
        # Validate based on operation
        if operation == ListOperationType.FILTER:
            if not params.get("filter_expression"):
                raise NodeValidationError("Filter expression is required for filter operation")
                
        elif operation == ListOperationType.MAP:
            if not params.get("map_expression"):
                raise NodeValidationError("Map expression is required for map operation")
                
        elif operation == ListOperationType.REDUCE:
            if not params.get("reduce_expression"):
                raise NodeValidationError("Reduce expression is required for reduce operation")
                
        elif operation == ListOperationType.SORT:
            # sort_key is optional - if not provided, we sort based on the element itself
            pass
            
        elif operation == ListOperationType.MERGE:
            if not params.get("second_list"):
                raise NodeValidationError("Second list is required for merge operation")
                
        elif operation == ListOperationType.GROUP:
            if not params.get("group_key"):
                raise NodeValidationError("Group key is required for group operation")
                
        elif operation == ListOperationType.ZIP:
            if not params.get("second_list"):
                raise NodeValidationError("Second list is required for zip operation")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the list node operation."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get parameters
            operation = validated_data["operation"]
            input_list = validated_data["input_list"]
            
            # Ensure input_list is actually a list
            if not isinstance(input_list, list):
                raise NodeValidationError("Input list must be a list")
            
            # Execute the appropriate operation based on the operation type
            if operation == ListOperationType.FILTER:
                result = await self.operation_filter_list_async(input_list, validated_data)
            elif operation == ListOperationType.MAP:
                result = await self.operation_map_list_async(input_list, validated_data)
            elif operation == ListOperationType.REDUCE:
                result = await self.operation_reduce_list_async(input_list, validated_data)
            elif operation == ListOperationType.SORT:
                result = self.operation_sort_list(input_list, validated_data)
            elif operation == ListOperationType.SLICE:
                result = self.operation_slice_list(input_list, validated_data)
            elif operation == ListOperationType.APPEND:
                result = self.operation_append_to_list(input_list, validated_data)
            elif operation == ListOperationType.MERGE:
                result = self.operation_merge_lists(input_list, validated_data)
            elif operation == ListOperationType.UNIQUE:
                result = self.operation_get_unique(input_list)
            elif operation == ListOperationType.FLATTEN:
                result = self.operation_flatten_list(input_list)
            elif operation == ListOperationType.GROUP:
                result = self.operation_group_list(input_list, validated_data)
            elif operation == ListOperationType.COUNT:
                result = self.operation_count_items(input_list)
            elif operation == ListOperationType.JOIN:
                result = self.operation_join_list(input_list, validated_data)
            elif operation == ListOperationType.SPLIT:
                result = self.operation_split_string(input_list, validated_data)
            elif operation == ListOperationType.REVERSE:
                result = self.operation_reverse_list(input_list)
            elif operation == ListOperationType.ZIP:
                result = self.operation_zip_lists(input_list, validated_data)
            elif operation == ListOperationType.ENUMERATE:
                result = self.operation_enumerate_list(input_list)
            else:
                raise NodeValidationError(f"Unknown operation: {operation}")
            
            # Calculate result count for list results
            count = len(result) if isinstance(result, list) else 1
            
            return {
                "result": result,
                "count": count,
                "status": "success",
                "error": None
            }
            
        except Exception as e:
            error_message = f"Error in list node: {str(e)}"
            logger.error(error_message)
            return {
                "result": None,
                "count": 0,
                "status": "error",
                "error": error_message
            }
    
    # -------------------------
    # Operation Methods
    # -------------------------
    
    async def operation_filter_list_async(self, input_list: List[Any], params: Dict[str, Any]) -> List[Any]:
        """
        Async implementation of filter_list operation.
        
        Args:
            input_list: The list to filter
            params: Parameters including the filter expression
            
        Returns:
            Filtered list
        """
        return self.operation_filter_list(input_list, params)
    
    def operation_filter_list(self, input_list: List[Any], params: Dict[str, Any]) -> List[Any]:
        """
        Filter a list based on an expression.
        
        Args:
            input_list: The list to filter
            params: Parameters including the filter expression
            
        Returns:
            Filtered list
        """
        filter_expression = params["filter_expression"]
        use_javascript = params.get("use_javascript", False)
        
        if use_javascript:
            # Use JavaScript for more complex filtering
            js_code = params.get("javascript_code")
            if not js_code:
                raise NodeValidationError("JavaScript code is required when use_javascript is true")
            
            # Check if we have an expression engine resource
            expression_engine = self.resources.get("expression_engine")
            if expression_engine and hasattr(expression_engine, 'evaluate_js'):
                try:
                    return expression_engine.evaluate_js(js_code, {"input_list": input_list})
                except Exception as e:
                    logger.error(f"Error executing JavaScript with engine: {str(e)}")
                    return []
            
            # Fallback if no engine available
            logger.warning("JavaScript execution is not implemented without expression_engine resource")
            return input_list
        else:
            # Use simple expression evaluation
            result = []
            
            for item in input_list:
                try:
                    # Create evaluation context with 'item' variable
                    context = {"item": item}
                    # Add any additional context data
                    if "context_data" in self.resources:
                        context.update(self.resources["context_data"])
                    
                    # Check if we have an expression engine resource
                    expression_engine = self.resources.get("expression_engine")
                    if expression_engine and hasattr(expression_engine, 'evaluate_expression'):
                        if expression_engine.evaluate_expression(filter_expression, context):
                            result.append(item)
                    else:
                        # Fallback to built-in eval
                        if eval(filter_expression, {"__builtins__": {}}, context):
                            result.append(item)
                except Exception as e:
                    logger.error(f"Error evaluating filter expression: {str(e)}")
            
            return result
    
    async def operation_map_list_async(self, input_list: List[Any], params: Dict[str, Any]) -> List[Any]:
        """
        Async implementation of map_list operation.
        
        Args:
            input_list: The list to map
            params: Parameters including the map expression
            
        Returns:
            Mapped list
        """
        return self.operation_map_list(input_list, params)
    
    def operation_map_list(self, input_list: List[Any], params: Dict[str, Any]) -> List[Any]:
        """
        Map a list using an expression.
        
        Args:
            input_list: The list to map
            params: Parameters including the map expression
            
        Returns:
            Mapped list
        """
        map_expression = params["map_expression"]
        use_javascript = params.get("use_javascript", False)
        
        if use_javascript:
            # Use JavaScript for more complex mapping
            js_code = params.get("javascript_code")
            if not js_code:
                raise NodeValidationError("JavaScript code is required when use_javascript is true")
            
            # Check if we have an expression engine resource
            expression_engine = self.resources.get("expression_engine")
            if expression_engine and hasattr(expression_engine, 'evaluate_js'):
                try:
                    return expression_engine.evaluate_js(js_code, {"input_list": input_list})
                except Exception as e:
                    logger.error(f"Error executing JavaScript with engine: {str(e)}")
                    return input_list
            
            # Fallback if no engine available
            logger.warning("JavaScript execution is not implemented without expression_engine resource")
            return input_list
        else:
            # Use simple expression evaluation
            result = []
            
            for item in input_list:
                try:
                    # Create evaluation context with 'item' variable
                    context = {"item": item}
                    # Add any additional context data
                    if "context_data" in self.resources:
                        context.update(self.resources["context_data"])
                    
                    # Check if we have an expression engine resource
                    expression_engine = self.resources.get("expression_engine")
                    if expression_engine and hasattr(expression_engine, 'evaluate_expression'):
                        mapped_value = expression_engine.evaluate_expression(map_expression, context)
                    else:
                        # Fallback to built-in eval
                        mapped_value = eval(map_expression, {"__builtins__": {}}, context)
                    
                    result.append(mapped_value)
                except Exception as e:
                    logger.error(f"Error evaluating map expression: {str(e)}")
                    # Add None for failed expressions to maintain list length
                    result.append(None)
            
            return result
    
    async def operation_reduce_list_async(self, input_list: List[Any], params: Dict[str, Any]) -> Any:
        """
        Async implementation of reduce_list operation.
        
        Args:
            input_list: The list to reduce
            params: Parameters including the reduce expression and initial value
            
        Returns:
            Reduced value
        """
        return self.operation_reduce_list(input_list, params)
    
    def operation_reduce_list(self, input_list: List[Any], params: Dict[str, Any]) -> Any:
        """
        Reduce a list using an expression.
        
        Args:
            input_list: The list to reduce
            params: Parameters including the reduce expression and initial value
            
        Returns:
            Reduced value
        """
        if not input_list:
            return params.get("reduce_initial")
            
        reduce_expression = params["reduce_expression"]
        initial = params.get("reduce_initial")
        use_javascript = params.get("use_javascript", False)
        
        if use_javascript:
            # Use JavaScript for more complex reducing
            js_code = params.get("javascript_code")
            if not js_code:
                raise NodeValidationError("JavaScript code is required when use_javascript is true")
            
            # Check if we have an expression engine resource
            expression_engine = self.resources.get("expression_engine")
            if expression_engine and hasattr(expression_engine, 'evaluate_js'):
                try:
                    return expression_engine.evaluate_js(js_code, {
                        "input_list": input_list,
                        "initial": initial
                    })
                except Exception as e:
                    logger.error(f"Error executing JavaScript with engine: {str(e)}")
                    return input_list[0] if input_list else initial
            
            # Fallback if no engine available
            logger.warning("JavaScript execution is not implemented without expression_engine resource")
            return input_list[0] if input_list else initial
        else:
            # Use simple expression evaluation
            if initial is not None:
                result = initial
            else:
                result = input_list[0]
                input_list = input_list[1:]
            
            for item in input_list:
                try:
                    # Create evaluation context with 'acc' and 'item' variables
                    context = {"acc": result, "item": item}
                    # Add any additional context data
                    if "context_data" in self.resources:
                        context.update(self.resources["context_data"])
                    
                    # Check if we have an expression engine resource
                    expression_engine = self.resources.get("expression_engine")
                    if expression_engine and hasattr(expression_engine, 'evaluate_expression'):
                        result = expression_engine.evaluate_expression(reduce_expression, context)
                    else:
                        # Fallback to built-in eval
                        result = eval(reduce_expression, {"__builtins__": {}}, context)
                except Exception as e:
                    logger.error(f"Error evaluating reduce expression: {str(e)}")
            
            return result
    
    def operation_sort_list(self, input_list: List[Any], params: Dict[str, Any]) -> List[Any]:
        """
        Sort a list based on a key.
        
        Args:
            input_list: The list to sort
            params: Parameters including the sort key and sort direction
            
        Returns:
            Sorted list
        """
        if not input_list:
            return []
            
        sort_key = params.get("sort_key")
        sort_reverse = params.get("sort_reverse", False)
        
        if sort_key:
            # Sort based on the provided key
            try:
                result = sorted(
                    input_list,
                    key=lambda x: x[sort_key] if isinstance(x, dict) and sort_key in x else getattr(x, sort_key, None),
                    reverse=sort_reverse
                )
            except Exception as e:
                logger.error(f"Error sorting list: {str(e)}")
                result = input_list  # Return unsorted on error
        else:
            # Sort the list directly
            try:
                result = sorted(input_list, reverse=sort_reverse)
            except Exception as e:
                logger.error(f"Error sorting list: {str(e)}")
                result = input_list  # Return unsorted on error
        
        return result
    
    def operation_slice_list(self, input_list: List[Any], params: Dict[str, Any]) -> List[Any]:
        """
        Slice a list from start_index to end_index.
        
        Args:
            input_list: The list to slice
            params: Parameters including start and end indices
            
        Returns:
            Sliced list
        """
        start_index = params.get("start_index", 0)
        end_index = params.get("end_index", len(input_list))
        
        # Ensure indices are integers
        try:
            start_index = int(start_index)
        except (ValueError, TypeError):
            start_index = 0
            
        try:
            end_index = int(end_index) if end_index is not None else len(input_list)
        except (ValueError, TypeError):
            end_index = len(input_list)
        
        # Slice the list
        return input_list[start_index:end_index]
    
    def operation_append_to_list(self, input_list: List[Any], params: Dict[str, Any]) -> List[Any]:
        """
        Append items to a list.
        
        Args:
            input_list: The list to append to
            params: Parameters including items to append
            
        Returns:
            Extended list
        """
        second_list = params.get("second_list", [])
        
        # Make a copy of the input list
        result = input_list.copy()
        
        # Append items from second list
        if isinstance(second_list, list):
            result.extend(second_list)
        else:
            result.append(second_list)
        
        return result
    
    def operation_merge_lists(self, input_list: List[Any], params: Dict[str, Any]) -> List[Any]:
        """
        Merge two lists.
        
        Args:
            input_list: The first list
            params: Parameters including the second list
            
        Returns:
            Merged list
        """
        second_list = params.get("second_list", [])
        
        if not isinstance(second_list, list):
            raise NodeValidationError("Second list must be a list")
        
        # Merge the lists
        return input_list + second_list
    
    def operation_get_unique(self, input_list: List[Any]) -> List[Any]:
        """
        Remove duplicates from a list.
        
        Args:
            input_list: The list to make unique
            
        Returns:
            List with duplicates removed
        """
        # Handle different item types
        try:
            # Try to use set to remove duplicates (works for hashable types)
            return list(dict.fromkeys(input_list))  # Preserves order in Python 3.7+
        except:
            # Fall back to manual deduplication
            result = []
            for item in input_list:
                if item not in result:
                    result.append(item)
            return result
    
    def operation_flatten_list(self, input_list: List[Any]) -> List[Any]:
        """
        Flatten a nested list.
        
        Args:
            input_list: The list to flatten
            
        Returns:
            Flattened list
        """
        result = []
        
        for item in input_list:
            if isinstance(item, list):
                result.extend(self.operation_flatten_list(item))
            else:
                result.append(item)
        
        return result
    
    def operation_group_list(self, input_list: List[Any], params: Dict[str, Any]) -> Dict[str, List[Any]]:
        """
        Group a list by a key.
        
        Args:
            input_list: The list to group
            params: Parameters including the group key
            
        Returns:
            Dictionary with groups
        """
        group_key = params["group_key"]
        result = {}
        
        for item in input_list:
            # Extract the key value from the item
            if isinstance(item, dict):
                key_value = item.get(group_key, "None")
            else:
                key_value = getattr(item, group_key, "None")
            
            # Convert key_value to string for dict key
            key_str = str(key_value)
            
            # Add item to the appropriate group
            if key_str not in result:
                result[key_str] = []
            result[key_str].append(item)
        
        return result
    
    def operation_count_items(self, input_list: List[Any]) -> int:
        """
        Count items in a list.
        
        Args:
            input_list: The list to count
            
        Returns:
            Number of items in the list
        """
        return len(input_list)
    
    def operation_join_list(self, input_list: List[Any], params: Dict[str, Any]) -> str:
        """
        Join a list of strings.
        
        Args:
            input_list: The list to join
            params: Parameters including the join delimiter
            
        Returns:
            Joined string
        """
        delimiter = params.get("join_delimiter", ",")
        
        # Convert all items to strings
        string_list = [str(item) for item in input_list]
        
        # Join the strings
        return delimiter.join(string_list)
    
    def operation_split_string(self, input_list: List[Any], params: Dict[str, Any]) -> List[List[str]]:
        """
        Split strings in a list.
        
        Args:
            input_list: The list containing strings to split
            params: Parameters including the split delimiter
            
        Returns:
            List of split strings
        """
        delimiter = params.get("split_delimiter", ",")
        result = []
        
        for item in input_list:
            if isinstance(item, str):
                result.append(item.split(delimiter))
            else:
                # Non-string items are wrapped in a list
                result.append([item])
        
        return result
    
    def operation_reverse_list(self, input_list: List[Any]) -> List[Any]:
        """
        Reverse a list.
        
        Args:
            input_list: The list to reverse
            
        Returns:
            Reversed list
        """
        return list(reversed(input_list))
    
    def operation_zip_lists(self, input_list: List[Any], params: Dict[str, Any]) -> List[tuple]:
        """
        Zip two lists together.
        
        Args:
            input_list: The first list
            params: Parameters including the second list
            
        Returns:
            Zipped list of tuples
        """
        second_list = params.get("second_list", [])
        
        if not isinstance(second_list, list):
            raise NodeValidationError("Second list must be a list")
        
        # Zip the lists
        return list(zip(input_list, second_list))
    
    def operation_enumerate_list(self, input_list: List[Any]) -> List[tuple]:
        """
        Enumerate a list, adding indices.
        
        Args:
            input_list: The list to enumerate
            
        Returns:
            List of (index, value) tuples
        """
        return list(enumerate(input_list))

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("list", ListNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register ListNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")