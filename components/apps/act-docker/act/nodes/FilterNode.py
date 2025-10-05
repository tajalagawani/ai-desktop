"""
FilterNode - Data filtering node for workflows.
Filters collection items based on specified criteria.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union, Callable
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

class FilterMode:
    """Filter modes for collection processing."""
    INCLUDE = "include"
    EXCLUDE = "exclude"

class FilterNode(BaseNode):
    """
    Node for filtering collections in workflows.
    Filters items from a collection based on specified criteria.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
    
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the filter node."""
        return NodeSchema(
            node_type="filter",
            version="1.0.0",
            description="Filters items from a collection based on specified criteria",
            # Define all parameters
            parameters=[
                # Input collection parameter
                NodeParameter(
                    name="collection",
                    type=NodeParameterType.ARRAY,
                    description="The collection to filter",
                    required=True
                ),
                
                # Filter mode parameter
                NodeParameter(
                    name="mode",
                    type=NodeParameterType.STRING,
                    description="Filter mode - include or exclude matching items",
                    required=True,
                    enum=[FilterMode.INCLUDE, FilterMode.EXCLUDE],
                    default=FilterMode.INCLUDE
                ),
                
                # Filter criteria parameters
                NodeParameter(
                    name="filter_type",
                    type=NodeParameterType.STRING,
                    description="Type of filter to apply",
                    required=True,
                    enum=["property", "condition", "expression", "script"]
                ),
                
                # Property filter parameters
                NodeParameter(
                    name="property_path",
                    type=NodeParameterType.STRING,
                    description="JSON path to the property to filter on (for property filter)",
                    required=False
                ),
                NodeParameter(
                    name="operator",
                    type=NodeParameterType.STRING,
                    description="Comparison operator (for property filter)",
                    required=False,
                    enum=[
                        "equals", "not_equals", "greater_than", "less_than",
                        "greater_than_or_equals", "less_than_or_equals",
                        "contains", "not_contains", "starts_with", "ends_with",
                        "matches_regex", "is_null", "is_not_null", "is_empty",
                        "is_not_empty", "in", "not_in"
                    ]
                ),
                NodeParameter(
                    name="value",
                    type=NodeParameterType.ANY,
                    description="Value to compare against (for property filter)",
                    required=False
                ),
                
                # Condition filter parameters
                NodeParameter(
                    name="conditions",
                    type=NodeParameterType.ARRAY,
                    description="List of conditions to combine (for condition filter)",
                    required=False
                ),
                NodeParameter(
                    name="logical_operator",
                    type=NodeParameterType.STRING,
                    description="Logical operator to combine conditions (for condition filter)",
                    required=False,
                    enum=["and", "or", "not"],
                    default="and"
                ),
                
                # Expression filter parameters
                NodeParameter(
                    name="expression",
                    type=NodeParameterType.STRING,
                    description="Expression to evaluate for each item (for expression filter)",
                    required=False
                ),
                
                # Script filter parameters
                NodeParameter(
                    name="script",
                    type=NodeParameterType.STRING,
                    description="Script to evaluate for each item (for script filter)",
                    required=False
                ),
                NodeParameter(
                    name="script_language",
                    type=NodeParameterType.STRING,
                    description="Language of the script (for script filter)",
                    required=False,
                    enum=["javascript", "python"],
                    default="python"
                ),
                
                # Limit and offset parameters
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,  # Changed from INTEGER to NUMBER
                    description="Maximum number of items to return",
                    required=False
                ),
                NodeParameter(
                    name="offset",
                    type=NodeParameterType.NUMBER,  # Changed from INTEGER to NUMBER
                    description="Number of items to skip",
                    required=False,
                    default=0
                ),
                
                # Sorting parameters
                NodeParameter(
                    name="sort_by",
                    type=NodeParameterType.STRING,
                    description="Property to sort by",
                    required=False
                ),
                NodeParameter(
                    name="sort_direction",
                    type=NodeParameterType.STRING,
                    description="Sort direction",
                    required=False,
                    enum=["asc", "desc"],
                    default="asc"
                ),
                
                # Output transformation parameters
                NodeParameter(
                    name="transform_output",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to transform the output",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="output_mapping",
                    type=NodeParameterType.OBJECT,
                    description="Mapping for output transformation",
                    required=False
                )
            ],

            # Define outputs for the node
            outputs={
                "filtered_collection": NodeParameterType.ARRAY,
                "item_count": NodeParameterType.NUMBER,  # Changed from INTEGER to NUMBER
                "status": NodeParameterType.STRING,
                "error": NodeParameterType.STRING
            },
            
            # Add metadata
            tags=["data-processing", "filtering", "collection"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the filter type."""
        params = node_data.get("params", {})
        filter_type = params.get("filter_type")
        
        if not filter_type:
            raise NodeValidationError("Filter type is required")
        
        # Validate required collection
        if "collection" not in params or params["collection"] is None:
            raise NodeValidationError("Collection is required")
            
        # Validate based on filter type
        if filter_type == "property":
            if not params.get("property_path"):
                raise NodeValidationError("Property path is required for property filter")
                
            if not params.get("operator"):
                raise NodeValidationError("Operator is required for property filter")
                
            # Value is optional for some operators (is_null, is_not_null, etc.)
            if params.get("operator") not in [
                "is_null", "is_not_null", "is_empty", "is_not_empty"
            ] and params.get("value") is None:
                raise NodeValidationError("Value is required for this operator")
                
        elif filter_type == "condition":
            if not params.get("conditions") or not isinstance(params.get("conditions"), list):
                raise NodeValidationError("Conditions array is required for condition filter")
                
            if not params.get("logical_operator"):
                raise NodeValidationError("Logical operator is required for condition filter")
                
        elif filter_type == "expression":
            if not params.get("expression"):
                raise NodeValidationError("Expression is required for expression filter")
                
        elif filter_type == "script":
            if not params.get("script"):
                raise NodeValidationError("Script is required for script filter")
                
            if not params.get("script_language"):
                raise NodeValidationError("Script language is required for script filter")
        
        # Validate sorting parameters if provided
        if params.get("sort_by") and not isinstance(params.get("sort_by"), str):
            raise NodeValidationError("Sort by must be a string")
            
        # Validate limit and offset if provided
        if params.get("limit") is not None and (
            not isinstance(params.get("limit"), (int, float)) or params.get("limit") < 0
        ):
            raise NodeValidationError("Limit must be a non-negative number")
            
        if params.get("offset") is not None and (
            not isinstance(params.get("offset"), (int, float)) or params.get("offset") < 0
        ):
            raise NodeValidationError("Offset must be a non-negative number")
            
        # Validate output mapping if transform_output is true
        if params.get("transform_output") and not params.get("output_mapping"):
            raise NodeValidationError("Output mapping is required when transform_output is true")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the filter node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # First operation: Apply filter
            filtered_items = await self.operation_apply_filter(validated_data, node_data)
            
            # Second operation: Apply sorting if specified
            if validated_data.get("sort_by"):
                filtered_items = self.operation_sort_items(filtered_items, validated_data)
            
            # Apply limit and offset if specified
            filtered_items = self._apply_limit_offset(filtered_items, validated_data)
            
            # Third operation: Transform output if specified
            if validated_data.get("transform_output"):
                transformed_items = self.operation_transform_output(filtered_items, validated_data, node_data)
                output_items = transformed_items
            else:
                output_items = filtered_items
            
            # Return the result
            return {
                "status": "success",
                "filtered_collection": output_items,
                "item_count": len(output_items),
                "error": None
            }
            
        except Exception as e:
            error_message = f"Error in filter node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "filtered_collection": [],
                "item_count": 0,
                "error": error_message
            }
    
    # -------------------------
    # Operation Implementations
    # -------------------------
    
    async def operation_apply_filter(self, validated_data: Dict[str, Any], node_data: Dict[str, Any]) -> List[Any]:
        """
        Implementation of apply_filter operation.
        
        Args:
            validated_data: Validated parameters
            node_data: Full node data for context
            
        Returns:
            Filtered list of items
        """
        collection = validated_data["collection"]
        filter_type = validated_data["filter_type"]
        mode = validated_data.get("mode", FilterMode.INCLUDE)
        
        # Use appropriate filter function based on filter_type
        if filter_type == "property":
            filter_func = lambda item: self._evaluate_property_filter(item, validated_data)
        elif filter_type == "condition":
            filter_func = lambda item: self._evaluate_condition_filter(item, validated_data, node_data)
        elif filter_type == "expression":
            filter_func = lambda item: self._evaluate_expression_filter(item, validated_data, node_data)
        elif filter_type == "script":
            filter_func = lambda item: self._evaluate_script_filter(item, validated_data, node_data)
        else:
            raise NodeValidationError(f"Unknown filter type: {filter_type}")
        
        # Apply the filter
        result = []
        for item in collection:
            try:
                # Handle both sync and async filter functions
                if asyncio.iscoroutinefunction(filter_func):
                    matches = await filter_func(item)
                else:
                    matches = filter_func(item)
                
                # Include or exclude based on mode
                if (mode == FilterMode.INCLUDE and matches) or (mode == FilterMode.EXCLUDE and not matches):
                    result.append(item)
            except Exception as e:
                logger.error(f"Error filtering item: {str(e)}")
                # Skip items that cause errors
                continue
        
        return result
    
    def operation_sort_items(self, items: List[Any], validated_data: Dict[str, Any]) -> List[Any]:
        """
        Implementation of sort_items operation.
        
        Args:
            items: Items to sort
            validated_data: Validated parameters
            
        Returns:
            Sorted list of items
        """
        sort_by = validated_data["sort_by"]
        sort_direction = validated_data.get("sort_direction", "asc")
        
        # Create sort function
        def sort_func(item):
            # Handle nested properties with dot notation
            if "." in sort_by:
                parts = sort_by.split(".")
                value = item
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return None
                return value
            
            # Handle simple properties
            if isinstance(item, dict) and sort_by in item:
                return item[sort_by]
            
            # Handle array index
            try:
                if isinstance(item, (list, tuple)) and sort_by.isdigit():
                    index = int(sort_by)
                    if index < len(item):
                        return item[index]
            except (ValueError, IndexError):
                pass
            
            return None
        
        # Sort the items
        reverse = sort_direction == "desc"
        return sorted(items, key=sort_func, reverse=reverse)
    
    def operation_transform_output(self, items: List[Any], validated_data: Dict[str, Any], node_data: Dict[str, Any]) -> List[Any]:
        """
        Implementation of transform_output operation.
        
        Args:
            items: Items to transform
            validated_data: Validated parameters
            node_data: Full node data
            
        Returns:
            Transformed list of items
        """
        output_mapping = validated_data.get("output_mapping", {})
        
        if not output_mapping:
            return items
        
        # Apply mapping to each item
        transformed_items = []
        for item in items:
            transformed_item = {}
            for output_key, source_path in output_mapping.items():
                # Resolve the source path value from the item
                value = self._resolve_path(item, source_path)
                transformed_item[output_key] = value
            
            transformed_items.append(transformed_item)
        
        return transformed_items
    
    # -------------------------
    # Helper Methods for Operations
    # -------------------------
    
    def _evaluate_property_filter(self, item: Any, params: Dict[str, Any]) -> bool:
        """
        Evaluate a property filter against an item.
        
        Args:
            item: The item to filter
            params: Validated parameters
            
        Returns:
            True if the item matches, False otherwise
        """
        property_path = params["property_path"]
        operator = params["operator"]
        
        # Get the property value
        property_value = self._resolve_path(item, property_path)
        
        # Handle operators that don't need a comparison value
        if operator == "is_null":
            return property_value is None
        elif operator == "is_not_null":
            return property_value is not None
        elif operator == "is_empty":
            if property_value is None:
                return True
            elif isinstance(property_value, (str, list, dict)):
                return len(property_value) == 0
            return False
        elif operator == "is_not_empty":
            if property_value is None:
                return False
            elif isinstance(property_value, (str, list, dict)):
                return len(property_value) > 0
            return True
        
        # Get the comparison value
        comparison_value = params["value"]
        
        # Evaluate based on operator
        if operator == "equals":
            return property_value == comparison_value
        elif operator == "not_equals":
            return property_value != comparison_value
        elif operator == "greater_than":
            return property_value > comparison_value
        elif operator == "less_than":
            return property_value < comparison_value
        elif operator == "greater_than_or_equals":
            return property_value >= comparison_value
        elif operator == "less_than_or_equals":
            return property_value <= comparison_value
        elif operator == "contains":
            if property_value is None:
                return False
            if isinstance(property_value, str) and isinstance(comparison_value, str):
                return comparison_value in property_value
            elif isinstance(property_value, (list, tuple, set)):
                return comparison_value in property_value
            elif isinstance(property_value, dict):
                return comparison_value in property_value or comparison_value in property_value.values()
            return False
        elif operator == "not_contains":
            if property_value is None:
                return True
            if isinstance(property_value, str) and isinstance(comparison_value, str):
                return comparison_value not in property_value
            elif isinstance(property_value, (list, tuple, set)):
                return comparison_value not in property_value
            elif isinstance(property_value, dict):
                return comparison_value not in property_value and comparison_value not in property_value.values()
            return True
        elif operator == "starts_with":
            return isinstance(property_value, str) and isinstance(comparison_value, str) and property_value.startswith(comparison_value)
        elif operator == "ends_with":
            return isinstance(property_value, str) and isinstance(comparison_value, str) and property_value.endswith(comparison_value)
        elif operator == "matches_regex":
            if not isinstance(property_value, str) or not isinstance(comparison_value, str):
                return False
            try:
                pattern = re.compile(comparison_value)
                return bool(pattern.match(property_value))
            except re.error:
                logger.error(f"Invalid regex pattern: {comparison_value}")
                return False
        elif operator == "in":
            if comparison_value is None:
                return False
            if isinstance(comparison_value, (list, tuple, set)):
                return property_value in comparison_value
            elif isinstance(comparison_value, dict):
                return property_value in comparison_value
            elif isinstance(comparison_value, str) and isinstance(property_value, str):
                return property_value in comparison_value
            return False
        elif operator == "not_in":
            if comparison_value is None:
                return True
            if isinstance(comparison_value, (list, tuple, set)):
                return property_value not in comparison_value
            elif isinstance(comparison_value, dict):
                return property_value not in comparison_value
            elif isinstance(comparison_value, str) and isinstance(property_value, str):
                return property_value not in comparison_value
            return True
        
        logger.warning(f"Unknown operator: {operator}")
        return False
    
    async def _evaluate_condition_filter(self, item: Any, params: Dict[str, Any], node_data: Dict[str, Any]) -> bool:
        """
        Evaluate a condition filter against an item.
        
        Args:
            item: The item to filter
            params: Validated parameters
            node_data: Full node data for context
            
        Returns:
            True if the item matches, False otherwise
        """
        conditions = params["conditions"]
        logical_operator = params["logical_operator"]
        
        if not conditions:
            return False
        
        # Evaluate all conditions
        results = []
        for condition in conditions:
            # Create a nested filter node to evaluate the condition
            nested_filter_node = FilterNode()
            
            # Create a collection with just this item
            nested_node_data = {
                "params": {
                    "collection": [item],
                    "filter_type": condition.get("filter_type", "property"),
                    "mode": FilterMode.INCLUDE
                }
            }
            
            # Add condition-specific parameters
            if condition.get("filter_type") == "property":
                nested_node_data["params"]["property_path"] = condition.get("property_path")
                nested_node_data["params"]["operator"] = condition.get("operator")
                nested_node_data["params"]["value"] = condition.get("value")
            elif condition.get("filter_type") == "expression":
                nested_node_data["params"]["expression"] = condition.get("expression")
            elif condition.get("filter_type") == "script":
                nested_node_data["params"]["script"] = condition.get("script")
                nested_node_data["params"]["script_language"] = condition.get("script_language", "python")
            
            # Execute the nested filter node asynchronously
            try:
                nested_result = await nested_filter_node.execute(nested_node_data)
                # Check if the item was included in the result
                results.append(len(nested_result.get("filtered_collection", [])) > 0)
            except Exception as e:
                logger.error(f"Error evaluating nested condition: {str(e)}")
                results.append(False)
        
        # Combine results based on logical operator
        if logical_operator == "and":
            return all(results)
        elif logical_operator == "or":
            return any(results)
        elif logical_operator == "not":
            # NOT applies to the first condition only
            return not results[0] if results else False
        
        logger.warning(f"Unknown logical operator: {logical_operator}")
        return False
    
    def _evaluate_expression_filter(self, item: Any, params: Dict[str, Any], node_data: Dict[str, Any]) -> bool:
        """
        Evaluate an expression filter against an item.
        
        Args:
            item: The item to filter
            params: Validated parameters
            node_data: Full node data for context
            
        Returns:
            True if the item matches, False otherwise
        """
        expression = params["expression"]
        
        try:
            # Create a context with item data
            context = {
                "item": item,
                "input": node_data.get("input", {}),
                "params": node_data.get("params", {}),
                "resources": node_data.get("resources", {})
            }
            
            # Check if we have a script engine resource
            script_engine = self.resources.get("script_engine")
            if script_engine and hasattr(script_engine, "eval_expression"):
                return bool(script_engine.eval_expression(expression, context))
            
            # Fall back to built-in eval if no script engine
            # Warning: This is not secure! In a real system, use a sandbox
            result = eval(expression, {"__builtins__": {}}, context)
            return bool(result)
        except Exception as e:
            logger.error(f"Error evaluating expression: {str(e)}")
            return False
    
    def _evaluate_script_filter(self, item: Any, params: Dict[str, Any], node_data: Dict[str, Any]) -> bool:
        """
        Evaluate a script filter against an item.
        
        Args:
            item: The item to filter
            params: Validated parameters
            node_data: Full node data for context
            
        Returns:
            True if the item matches, False otherwise
        """
        script = params["script"]
        script_language = params["script_language"]
        
        # Check if we have a script engine resource
        script_engine = self.resources.get("script_engine")
        if script_engine and hasattr(script_engine, "eval_script"):
            try:
                # Create a context with item data
                context = {
                    "item": item,
                    "input": node_data.get("input", {}),
                    "params": node_data.get("params", {}),
                    "resources": node_data.get("resources", {})
                }
                
                # Execute the script using the engine
                result = script_engine.eval_script(script, script_language, context)
                return bool(result)
            except Exception as e:
                logger.error(f"Error executing script with engine: {str(e)}")
                return False
        
        # Fall back to built-in eval for Python scripts if no engine
        logger.warning(f"No script engine found for {script_language}, using built-in eval for Python only")
        
        try:
            # Create a context with item data
            context = {
                "item": item,
                "input": node_data.get("input", {}),
                "params": node_data.get("params", {}),
                "resources": node_data.get("resources", {})
            }
            
            # Execute the script
            if script_language == "python":
                # Warning: This is not secure! In a real system, use a sandbox
                result = eval(script, {"__builtins__": {}}, context)
                return bool(result)
            else:
                # For JavaScript and other languages, we just return False
                logger.warning(f"Execution of {script_language} scripts not implemented")
                return False
        except Exception as e:
            logger.error(f"Error executing script: {str(e)}")
            return False
    
    def _resolve_path(self, item: Any, path: str) -> Any:
        """
        Resolve a property path from an item.
        
        Args:
            item: The item to get the property from
            path: The property path, using dot notation
            
        Returns:
            The property value, or None if not found
        """
        if not path:
            return None
        
        # Handle simple property
        if "." not in path:
            if isinstance(item, dict) and path in item:
                return item[path]
            
            # Handle array index
            try:
                if isinstance(item, (list, tuple)) and path.isdigit():
                    index = int(path)
                    if index < len(item):
                        return item[index]
            except (ValueError, IndexError):
                pass
            
            return None
        
        # Handle nested properties
        parts = path.split(".")
        current = item
        
        for part in parts:
            # Handle dictionary
            if isinstance(current, dict) and part in current:
                current = current[part]
            # Handle array index
            elif isinstance(current, (list, tuple)) and part.isdigit():
                try:
                    index = int(part)
                    if index < len(current):
                        current = current[index]
                    else:
                        return None
                except (ValueError, IndexError):
                    return None
            else:
                return None
        
        return current
    
    def _apply_limit_offset(self, items: List[Any], params: Dict[str, Any]) -> List[Any]:
        """
        Apply limit and offset to a list of items.
        
        Args:
            items: The items to limit
            params: Parameters containing limit and offset
            
        Returns:
            Limited list of items
        """
        offset = params.get("offset", 0)
        limit = params.get("limit")
        
        # Convert to int to ensure proper slicing
        if offset is not None:
            offset = int(offset)
        
        # Apply offset
        if offset > 0:
            items = items[offset:]
        
        # Apply limit
        if limit is not None:
            limit = int(limit)
            items = items[:limit]
        
        return items

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("filter", FilterNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register FilterNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")