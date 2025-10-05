"""
AggregateNode - Data aggregation node for workflows.
Performs aggregation operations (count, sum, average, min, max, etc.) on collections.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union, Callable
import statistics
from datetime import datetime
import asyncio

# Import only what's available in the base_node module
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

class AggregationOperator:
    """Aggregation operators for data processing."""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    MODE = "mode"
    FIRST = "first"
    LAST = "last"
    DISTINCT = "distinct"
    CONCAT = "concat"
    GROUP = "group"
    CUSTOM = "custom"

class AggregateNode(BaseNode):
    """
    Node for performing aggregation operations on collections in workflows.
    Supports various aggregation functions like count, sum, average, min, max, etc.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
    
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the aggregate node."""
        return NodeSchema(
            node_type="aggregate",
            version="1.0.0",
            description="Performs aggregation operations on collections",
            # Define all parameters
            parameters=[
                # Input collection parameter
                NodeParameter(
                    name="collection",
                    type=NodeParameterType.ARRAY,
                    description="The collection to aggregate",
                    required=True
                ),
                
                # Aggregation type parameter
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Aggregation operation to perform",
                    required=True,
                    enum=[
                        AggregationOperator.COUNT, AggregationOperator.SUM,
                        AggregationOperator.AVERAGE, AggregationOperator.MIN,
                        AggregationOperator.MAX, AggregationOperator.MEDIAN,
                        AggregationOperator.MODE, AggregationOperator.FIRST,
                        AggregationOperator.LAST, AggregationOperator.DISTINCT,
                        AggregationOperator.CONCAT, AggregationOperator.GROUP,
                        AggregationOperator.CUSTOM
                    ]
                ),
                
                # Field specification
                NodeParameter(
                    name="field",
                    type=NodeParameterType.STRING,
                    description="Field to aggregate (for object collections)",
                    required=False
                ),
                
                # Group by parameters
                NodeParameter(
                    name="group_by",
                    type=NodeParameterType.STRING,
                    description="Field to group by (for GROUP operation)",
                    required=False
                ),
                
                # Concat separator
                NodeParameter(
                    name="separator",
                    type=NodeParameterType.STRING,
                    description="Separator for concatenating values (for CONCAT operation)",
                    required=False,
                    default=", "
                ),
                
                # Custom expression
                NodeParameter(
                    name="expression",
                    type=NodeParameterType.STRING,
                    description="Custom expression for aggregation (for CUSTOM operation)",
                    required=False
                ),
                
                # Output format
                NodeParameter(
                    name="output_format",
                    type=NodeParameterType.STRING,
                    description="Format of the output results",
                    required=False,
                    enum=["value", "object", "array"],
                    default="value"
                ),
                
                # Filter parameters
                NodeParameter(
                    name="filter_nulls",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to filter out null values before aggregation",
                    required=False,
                    default=True
                ),
                
                # Date format for date operations
                NodeParameter(
                    name="date_format",
                    type=NodeParameterType.STRING,
                    description="Format string for date parsing (for date operations)",
                    required=False,
                    default="%Y-%m-%dT%H:%M:%S"
                ),
                
                # Result key name
                NodeParameter(
                    name="result_key",
                    type=NodeParameterType.STRING,
                    description="Key name for the result value in object output format",
                    required=False,
                    default="result"
                )
            ],
            
            # Define outputs for the node - following the same pattern as your IfNode
            outputs={
                "result": NodeParameterType.ANY,
                "count": NodeParameterType.NUMBER,
                "status": NodeParameterType.STRING,
                "error": NodeParameterType.STRING
            },
            
            # Add metadata
            tags=["data-processing", "aggregation", "analytics"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the aggregation operation."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Aggregation operation is required")
        
        # Validate required collection
        if "collection" not in params or params["collection"] is None:
            raise NodeValidationError("Collection is required")
            
        # Validate field parameter for operations that require it
        if operation in [
            AggregationOperator.SUM, AggregationOperator.AVERAGE,
            AggregationOperator.MIN, AggregationOperator.MAX,
            AggregationOperator.MEDIAN, AggregationOperator.MODE,
            AggregationOperator.CONCAT
        ] and not params.get("field") and all(isinstance(item, dict) for item in params.get("collection", [])) and len(params.get("collection", [])) > 0:
            # Only require field if collection contains dictionaries
            raise NodeValidationError(f"Field parameter is required for {operation} operation on object collections")
            
        # Validate group_by parameter for GROUP operation
        if operation == AggregationOperator.GROUP and not params.get("group_by"):
            raise NodeValidationError("Group by field is required for GROUP operation")
            
        # Validate expression for CUSTOM operation
        if operation == AggregationOperator.CUSTOM and not params.get("expression"):
            raise NodeValidationError("Expression is required for CUSTOM operation")
            
        # Validate output format
        if params.get("output_format") not in ["value", "object", "array", None]:
            raise NodeValidationError("Invalid output format. Must be 'value', 'object', or 'array'")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the aggregate node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Perform aggregation
            result = await self._perform_aggregation(validated_data, node_data)
            
            # Format output
            formatted_result = self._format_output(result, validated_data)
            
            # Count of items processed (before filtering)
            collection = validated_data.get("collection", [])
            
            # Return the result
            return {
                "status": "success",
                "result": formatted_result,
                "count": len(collection),
                "error": None
            }
            
        except Exception as e:
            error_message = f"Error in aggregate node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "count": 0,
                "error": error_message
            }
    
    # -------------------------
    # Core Implementation Methods
    # -------------------------
    
    async def _perform_aggregation(self, validated_data: Dict[str, Any], node_data: Dict[str, Any]) -> Any:
        """
        Perform the specified aggregation operation.
        
        Args:
            validated_data: Validated parameters
            node_data: Full node data for context
            
        Returns:
            Aggregation result
        """
        collection = validated_data["collection"]
        operation = validated_data["operation"]
        field = validated_data.get("field")
        filter_nulls = validated_data.get("filter_nulls", True)
        
        # If collection is empty, return appropriate default value
        if not collection:
            if operation in [AggregationOperator.COUNT, AggregationOperator.SUM]:
                return 0
            elif operation == AggregationOperator.AVERAGE:
                return 0
            elif operation == AggregationOperator.MIN:
                return None
            elif operation == AggregationOperator.MAX:
                return None
            elif operation == AggregationOperator.MEDIAN:
                return None
            elif operation == AggregationOperator.MODE:
                return None
            elif operation == AggregationOperator.CONCAT:
                return ""
            elif operation == AggregationOperator.DISTINCT:
                return []
            elif operation == AggregationOperator.GROUP:
                return {}
            elif operation in [AggregationOperator.FIRST, AggregationOperator.LAST]:
                return None
            else:
                return None
        
        # Extract values if field is specified
        values = []
        if field:
            for item in collection:
                if isinstance(item, dict):
                    value = self._resolve_field(item, field)
                    # Skip null values if filter_nulls is True
                    if filter_nulls and value is None:
                        continue
                    values.append(value)
                else:
                    # Skip non-dict items when field is specified
                    continue
        else:
            values = [item for item in collection if not (filter_nulls and item is None)]
        
        # Perform the aggregation operation
        if operation == AggregationOperator.COUNT:
            return len(values)
            
        elif operation == AggregationOperator.SUM:
            # Filter out non-numeric values
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if not numeric_values:
                return 0
            return sum(numeric_values)
            
        elif operation == AggregationOperator.AVERAGE:
            # Filter out non-numeric values
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if not numeric_values:
                return 0
            return sum(numeric_values) / len(numeric_values)
            
        elif operation == AggregationOperator.MIN:
            if not values:
                return None
            
            # Handle different types of values
            if all(isinstance(v, (int, float)) for v in values if v is not None):
                # Numeric min
                return min((v for v in values if v is not None), default=None)
            elif all(isinstance(v, str) for v in values if v is not None):
                # String min (alphabetical)
                return min((v for v in values if v is not None), default=None)
            elif all(isinstance(v, datetime) for v in values if v is not None):
                # DateTime min
                return min((v for v in values if v is not None), default=None)
            else:
                # Try to find min or return None
                try:
                    return min((v for v in values if v is not None), default=None)
                except TypeError:
                    logger.warning("Cannot compare mixed types for MIN operation")
                    return None
            
        elif operation == AggregationOperator.MAX:
            if not values:
                return None
            
            # Handle different types of values
            if all(isinstance(v, (int, float)) for v in values if v is not None):
                # Numeric max
                return max((v for v in values if v is not None), default=None)
            elif all(isinstance(v, str) for v in values if v is not None):
                # String max (alphabetical)
                return max((v for v in values if v is not None), default=None)
            elif all(isinstance(v, datetime) for v in values if v is not None):
                # DateTime max
                return max((v for v in values if v is not None), default=None)
            else:
                # Try to find max or return None
                try:
                    return max((v for v in values if v is not None), default=None)
                except TypeError:
                    logger.warning("Cannot compare mixed types for MAX operation")
                    return None
            
        elif operation == AggregationOperator.MEDIAN:
            # Filter out non-numeric values
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if not numeric_values:
                return None
            return statistics.median(numeric_values)
            
        elif operation == AggregationOperator.MODE:
            if not values:
                return None
            
            # Filter out None values
            filtered_values = [v for v in values if v is not None]
            if not filtered_values:
                return None
                
            # Find most common value
            try:
                return statistics.mode(filtered_values)
            except statistics.StatisticsError:
                # If no unique mode, return the first value
                return filtered_values[0]
            
        elif operation == AggregationOperator.FIRST:
            if not values:
                return None
            return values[0]
            
        elif operation == AggregationOperator.LAST:
            if not values:
                return None
            return values[-1]
            
        elif operation == AggregationOperator.DISTINCT:
            # Get unique values while preserving order
            unique_values = []
            for value in values:
                if value not in unique_values:
                    unique_values.append(value)
            return unique_values
            
        elif operation == AggregationOperator.CONCAT:
            separator = validated_data.get("separator", ", ")
            # Convert all values to strings
            string_values = [str(v) if v is not None else "" for v in values]
            return separator.join(string_values)
            
        elif operation == AggregationOperator.GROUP:
            group_by = validated_data.get("group_by")
            if not group_by:
                raise NodeValidationError("Group by field is required for GROUP operation")
                
            # Group items by the group_by field
            grouped = {}
            for item in collection:
                if isinstance(item, dict):
                    group_key = self._resolve_field(item, group_by)
                    # Convert to string to ensure it can be used as a key
                    group_key_str = str(group_key) if group_key is not None else "null"
                    
                    if group_key_str not in grouped:
                        grouped[group_key_str] = []
                    
                    grouped[group_key_str].append(item)
            
            return grouped
            
        elif operation == AggregationOperator.CUSTOM:
            expression = validated_data.get("expression")
            if not expression:
                raise NodeValidationError("Expression is required for CUSTOM operation")
                
            # Evaluate custom expression
            try:
                # Create context with collection and values
                context = {
                    "collection": collection,
                    "values": values,
                    "input": node_data.get("input", {}),
                    "params": node_data.get("params", {}),
                    # Add built-in functions to context
                    "sum": sum,
                    "len": len,
                    "min": min,
                    "max": max,
                    "sorted": sorted,
                    "range": range,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "filter": filter,
                    "map": map
                }
                
                # Use built-in eval
                # Warning: This is not secure! In a real system, use a sandbox
                result = eval(expression, {"__builtins__": {}}, context)
                return result
            except Exception as e:
                logger.error(f"Error evaluating custom expression: {str(e)}")
                raise Exception(f"Error in custom expression: {str(e)}")
        
        logger.warning(f"Unknown aggregation operation: {operation}")
        return None
    
    def _format_output(self, result: Any, validated_data: Dict[str, Any]) -> Any:
        """
        Format the aggregation results.
        
        Args:
            result: Aggregation result
            validated_data: Validated parameters
            
        Returns:
            Formatted result
        """
        output_format = validated_data.get("output_format", "value")
        result_key = validated_data.get("result_key", "result")
        operation = validated_data.get("operation")
        
        if output_format == "value":
            return result
            
        elif output_format == "object":
            return {
                result_key: result,
                "operation": operation,
                "timestamp": datetime.now().isoformat()
            }
            
        elif output_format == "array":
            # If result is already an array, wrap it in metadata
            if isinstance(result, list):
                return {
                    "items": result,
                    "count": len(result),
                    "operation": operation,
                    "timestamp": datetime.now().isoformat()
                }
            # If result is a dict with arrays (from GROUP operation)
            elif isinstance(result, dict) and operation == AggregationOperator.GROUP:
                return {
                    "groups": result,
                    "group_count": len(result),
                    "operation": operation,
                    "timestamp": datetime.now().isoformat()
                }
            # Otherwise convert single value to array
            else:
                return [result]
        
        # Default to value
        return result
    
    # -------------------------
    # Helper Methods
    # -------------------------
    
    def _resolve_field(self, item: Dict[str, Any], field: str) -> Any:
        """
        Resolve a field from an item.
        
        Args:
            item: The item to get the field from
            field: The field path, using dot notation
            
        Returns:
            The field value, or None if not found
        """
        if not field:
            return None
        
        # Handle simple field
        if "." not in field:
            return item.get(field)
        
        # Handle nested fields
        parts = field.split(".")
        current = item
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current


# Main test suite for AggregateNode
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Sample test data
    test_data = {
        "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "mixed": [1, 2, "three", 4, None, 6, 7.5, "eight", 9, 10],
        "objects": [
            {"id": 1, "name": "Alice", "age": 30, "department": "Engineering", "salary": 100000},
            {"id": 2, "name": "Bob", "age": 35, "department": "Engineering", "salary": 110000},
            {"id": 3, "name": "Carol", "age": 28, "department": "Marketing", "salary": 90000},
            {"id": 4, "name": "Dave", "age": 42, "department": "Marketing", "salary": 95000},
            {"id": 5, "name": "Eve", "age": 25, "department": "Engineering", "salary": 85000},
            {"id": 6, "name": "Frank", "age": 50, "department": "Management", "salary": 150000},
            {"id": 7, "name": "Grace", "age": 38, "department": "Engineering", "salary": 120000},
            {"id": 8, "name": "Heidi", "age": 29, "department": "Marketing", "salary": 92000},
            {"id": 9, "name": "Ivan", "age": 33, "department": "Engineering", "salary": 105000},
            {"id": 10, "name": "Judy", "age": 45, "department": "Management", "salary": 140000}
        ],
        "empty": []
    }
    
    # Create async test runner
    async def run_tests():
        print("=== AggregateNode Test Suite ===")
        
        # Create an instance of the AggregateNode
        node = AggregateNode()
        
        # Test all operations with different data types
        test_cases = [
            # Basic operations on numbers
            {
                "name": "Count Numbers",
                "params": {
                    "operation": AggregationOperator.COUNT,
                    "collection": test_data["numbers"]
                },
                "expected_result": 10
            },
            {
                "name": "Sum Numbers",
                "params": {
                    "operation": AggregationOperator.SUM,
                    "collection": test_data["numbers"]
                },
                "expected_result": 55
            },
            {
                "name": "Average Numbers",
                "params": {
                    "operation": AggregationOperator.AVERAGE,
                    "collection": test_data["numbers"]
                },
                "expected_result": 5.5
            },
            {
                "name": "Min Numbers",
                "params": {
                    "operation": AggregationOperator.MIN,
                    "collection": test_data["numbers"]
                },
                "expected_result": 1
            },
            {
                "name": "Max Numbers",
                "params": {
                    "operation": AggregationOperator.MAX,
                    "collection": test_data["numbers"]
                },
                "expected_result": 10
            },
            {
                "name": "Median Numbers",
                "params": {
                    "operation": AggregationOperator.MEDIAN,
                    "collection": test_data["numbers"]
                },
                "expected_result": 5.5
            },
            
            # Operations on mixed data
            {
                "name": "Count Mixed",
                "params": {
                    "operation": AggregationOperator.COUNT,
                    "collection": test_data["mixed"]
                },
                "expected_result": 9  # Excluding None when filter_nulls=True
            },
            {
                "name": "Count Mixed (with nulls)",
                "params": {
                    "operation": AggregationOperator.COUNT,
                    "collection": test_data["mixed"],
                    "filter_nulls": False
                },
                "expected_result": 10
            },
            {
                "name": "Sum Mixed",
                "params": {
                    "operation": AggregationOperator.SUM,
                    "collection": test_data["mixed"]
                },
                "expected_result": 39.5  # Sum of numeric values only
            },
            
            # Operations on object collections
            {
                "name": "Count Objects",
                "params": {
                    "operation": AggregationOperator.COUNT,
                    "collection": test_data["objects"]
                },
                "expected_result": 10
            },
            {
                "name": "Sum Object Field",
                "params": {
                    "operation": AggregationOperator.SUM,
                    "collection": test_data["objects"],
                    "field": "salary"
                },
                "expected_result": 1097000
            },
            {
                "name": "Average Object Field",
                "params": {
                    "operation": AggregationOperator.AVERAGE,
                    "collection": test_data["objects"],
                    "field": "age"
                },
                "expected_result": 35.5
            },
            {
                "name": "Min Object Field",
                "params": {
                    "operation": AggregationOperator.MIN,
                    "collection": test_data["objects"],
                    "field": "age"
                },
                "expected_result": 25
            },
            {
                "name": "Max Object Field",
                "params": {
                    "operation": AggregationOperator.MAX,
                    "collection": test_data["objects"],
                    "field": "salary"
                },
                "expected_result": 150000
            },
            
            # Distinct operation
            {
                "name": "Distinct Department",
                "params": {
                    "operation": AggregationOperator.DISTINCT,
                    "collection": test_data["objects"],
                    "field": "department"
                },
                "expected_result": ["Engineering", "Marketing", "Management"]
            },
            
            # Concat operation
            {
                "name": "Concat Names",
                "params": {
                    "operation": AggregationOperator.CONCAT,
                    "collection": test_data["objects"],
                    "field": "name",
                    "separator": ", "
                },
                "expected_result": "Alice, Bob, Carol, Dave, Eve, Frank, Grace, Heidi, Ivan, Judy"
            },
            
            # Group operation
            {
                "name": "Group by Department",
                "params": {
                    "operation": AggregationOperator.GROUP,
                    "collection": test_data["objects"],
                    "group_by": "department"
                },
                "expected_result_type": dict
            },
            
            # First/Last operations
            {
                "name": "First Object",
                "params": {
                    "operation": AggregationOperator.FIRST,
                    "collection": test_data["objects"]
                },
                "expected_result": test_data["objects"][0]
            },
            {
                "name": "Last Object",
                "params": {
                    "operation": AggregationOperator.LAST,
                    "collection": test_data["objects"]
                },
                "expected_result": test_data["objects"][-1]
            },
            
            # Custom operation
            {
                "name": "Custom Expression",
                "params": {
                    "operation": AggregationOperator.CUSTOM,
                    "collection": test_data["numbers"],
                    "expression": "sum([x for x in values if x % 2 == 0])"  # Sum of even numbers
                },
                "expected_result": 30  # 2 + 4 + 6 + 8 + 10
            },
            
            # Empty collection tests
            {
                "name": "Count Empty",
                "params": {
                    "operation": AggregationOperator.COUNT,
                    "collection": test_data["empty"]
                },
                "expected_result": 0
            },
            {
                "name": "Sum Empty",
                "params": {
                    "operation": AggregationOperator.SUM,
                    "collection": test_data["empty"]
                },
                "expected_result": 0
            },
            
            # Output format tests
            {
                "name": "Output as Value",
                "params": {
                    "operation": AggregationOperator.SUM,
                    "collection": test_data["numbers"],
                    "output_format": "value"
                },
                "expected_result": 55
            },
            {
                "name": "Output as Object",
                "params": {
                    "operation": AggregationOperator.SUM,
                    "collection": test_data["numbers"],
                    "output_format": "object",
                    "result_key": "total"
                },
                "expected_result_type": dict
            },
            {
                "name": "Output as Array",
                "params": {
                    "operation": AggregationOperator.DISTINCT,
                    "collection": test_data["objects"],
                    "field": "department",
                    "output_format": "array"
                },
                "expected_result_type": dict
            }
        ]
        
        # Run all test cases
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
                
                # Check the result
                if "expected_result" in test_case:
                    expected = test_case["expected_result"]
                    actual = result["result"]
                    
                    if expected == actual:
                        print(f"✅ PASS: Got expected result: {actual}")
                        passed_tests += 1
                    else:
                        print(f"❌ FAIL: Expected {expected}, got {actual}")
                elif "expected_result_type" in test_case:
                    expected_type = test_case["expected_result_type"]
                    actual = result["result"]
                    
                    if isinstance(actual, expected_type):
                        print(f"✅ PASS: Got expected result type: {type(actual).__name__}")
                        print(f"Result preview: {str(actual)[:100]}...")
                        passed_tests += 1
                    else:
                        print(f"❌ FAIL: Expected type {expected_type.__name__}, got {type(actual).__name__}")
                else:
                    print(f"⚠️ WARN: No expected result specified, actual result: {result['result']}")
                    passed_tests += 1
                    
            except Exception as e:
                print(f"❌ FAIL: Test threw an exception: {str(e)}")
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")
        
        # Additional manual tests
        print("\n=== Manual Test: Group and Aggregate ===")
        # Group by department and calculate average salary
        group_result = await node.execute({
            "params": {
                "operation": AggregationOperator.GROUP,
                "collection": test_data["objects"],
                "group_by": "department"
            }
        })
        
        # Now calculate average salary for each department
        grouped_data = group_result["result"]
        print("Department salary averages:")
        for dept, members in grouped_data.items():
            avg_result = await node.execute({
                "params": {
                    "operation": AggregationOperator.AVERAGE,
                    "collection": members,
                    "field": "salary"
                }
            })
            avg_salary = avg_result["result"]
            print(f"  {dept}: ${avg_salary:,.2f}")
        
        print("\n=== Manual Test: Advanced Custom Aggregation ===")
        # Find employees with above-average salaries
        avg_result = await node.execute({
            "params": {
                "operation": AggregationOperator.AVERAGE,
                "collection": test_data["objects"],
                "field": "salary"
            }
        })
        avg_salary = avg_result["result"]
        
        # Custom filter to get high earners
        high_earners = await node.execute({
            "params": {
                "operation": AggregationOperator.CUSTOM,
                "collection": test_data["objects"],
                "expression": f"[item for item in collection if item.get('salary', 0) > {avg_salary}]"
            }
        })
        
        print(f"Employees with above-average salary (>${avg_salary:,.2f}):")
        for employee in high_earners["result"]:
            print(f"  {employee['name']}: ${employee['salary']:,.2f}")
        
        print("\n=== Manual Test: Multi-level Aggregation ===")
        # First group by department
        departments = await node.execute({
            "params": {
                "operation": AggregationOperator.GROUP,
                "collection": test_data["objects"],
                "group_by": "department"
            }
        })
        
        # For each department, calculate min, max, and average ages
        dept_stats = {}
        for dept, members in departments["result"].items():
            min_age = await node.execute({
                "params": {
                    "operation": AggregationOperator.MIN,
                    "collection": members,
                    "field": "age"
                }
            })
            
            max_age = await node.execute({
                "params": {
                    "operation": AggregationOperator.MAX,
                    "collection": members,
                    "field": "age"
                }
            })
            
            avg_age = await node.execute({
                "params": {
                    "operation": AggregationOperator.AVERAGE,
                    "collection": members,
                    "field": "age"
                }
            })
            
            dept_stats[dept] = {
                "count": len(members),
                "min_age": min_age["result"],
                "max_age": max_age["result"],
                "avg_age": avg_age["result"]
            }
        
        print("Department age statistics:")
        for dept, stats in dept_stats.items():
            print(f"  {dept}:")
            print(f"    Count: {stats['count']} employees")
            print(f"    Age Range: {stats['min_age']} to {stats['max_age']} years")
            print(f"    Average Age: {stats['avg_age']:.1f} years")
        
        print("\n=== Performance Test: Large Collection ===")
        # Generate a large collection
        import random
        large_collection = [random.randint(1, 1000) for _ in range(10000)]
        
        # Measure performance
        import time
        start_time = time.time()
        
        large_result = await node.execute({
            "params": {
                "operation": AggregationOperator.AVERAGE,
                "collection": large_collection
            }
        })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Processed 10,000 items in {execution_time:.4f} seconds")
        print(f"Average value: {large_result['result']:.2f}")
        
        print("\n=== Testing Error Handling ===")
        # Test with invalid operation
        try:
            invalid_result = await node.execute({
                "params": {
                    "operation": "invalid_operation",
                    "collection": test_data["numbers"]
                }
            })
            print(f"Result with invalid operation: {invalid_result}")
        except Exception as e:
            print(f"Caught exception with invalid operation: {str(e)}")
        
        # Test with missing required parameter
        try:
            missing_param_result = await node.execute({
                "params": {
                    "operation": AggregationOperator.SUM
                    # Missing collection parameter
                }
            })
            print(f"Result with missing parameter: {missing_param_result}")
        except Exception as e:
            print(f"Caught exception with missing parameter: {str(e)}")
        
        # Test with invalid expression
        try:
            invalid_expr_result = await node.execute({
                "params": {
                    "operation": AggregationOperator.CUSTOM,
                    "collection": test_data["numbers"],
                    "expression": "this is not valid Python code"
                }
            })
            print(f"Result with invalid expression: {invalid_expr_result}")
        except Exception as e:
            print(f"Caught exception with invalid expression: {str(e)}")
            
        print("\nAll tests completed!")

    # Run the async tests
    asyncio.run(run_tests())
    
# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("aggregate", AggregateNode)
    logger.debug("Node registered with registry")
except ImportError:
    pass  # NodeRegistry not available
except Exception as e:
    pass  # Registration failed