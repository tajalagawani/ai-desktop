# === File: act/nodes/if_node.py ===

import logging
import json
import re
import asyncio
import numbers # For checking numeric types
from typing import Dict, Any, Optional, List
from datetime import datetime

# Assuming base_node.py is in the same directory or accessible via the package structure
try:
    from .base_node import (
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
    class NodeValidationError(Exception): pass
    class NodeExecutionError(Exception): pass
    class NodeParameterType: # Dummy enum/types
        ANY = "any"; STRING = "string"; BOOLEAN = "boolean"; NUMBER = "number"
    class NodeParameter:
        def __init__(self, name, type, description, required=True, default=None, enum=None): pass
    class NodeSchema:
         def __init__(self, node_type, version, description, parameters, outputs, tags=None, author=None): pass
    class BaseNode:
        def get_schema(self): raise NotImplementedError
        async def execute(self, data): raise NotImplementedError
        def validate_schema(self, data): return data.get("params", {}) # Simplistic
        def handle_error(self, error, context=""):
             return {"status": "error", "message": f"Error in {context}: {error}"}

logger = logging.getLogger(__name__)

class IfNode(BaseNode):
    node_type = "if"
    """
    Compares two values based on a specified operator and returns a boolean result.
    Prioritizes comparing values with the types received from the ExecutionManager.
    Uses limited type conversion only as a fallback for potential string mis-types.
    """

    def get_schema(self) -> NodeSchema:
        """Returns the schema definition for the IfNode."""
        return NodeSchema(
            node_type="if",
            version="1.2.0", # Version bump for behavior change
            description="Compares two resolved values based on an operator, respecting types. Returns a boolean result.",
            # --- Parameters remain the same as before ---
            parameters=[
                NodeParameter(name="value1", type=NodeParameterType.ANY, description="The first value for comparison (already resolved).", required=True),
                NodeParameter(name="operator", type=NodeParameterType.STRING, description="The comparison operator.", required=True,
                              enum=["==", "eq", "!=", "ne", ">", "gt", "<", "lt", ">=", "ge", "<=", "le",
                                    "contains", "not contains", "starts_with", "ends_with", "is_true", "is_false",
                                    "is_empty", "is_not_empty"]),
                NodeParameter(name="value2", type=NodeParameterType.ANY, description="The second value for comparison (already resolved). Not required for unary operators.", required=False, default=None),
                NodeParameter(name="case_sensitive", type=NodeParameterType.BOOLEAN, description="Perform case-sensitive string comparisons (default: True).", required=False, default=True)
            ],
            # --- Outputs remain the same ---
            outputs={"result": NodeParameterType.BOOLEAN, "value1_resolved": NodeParameterType.ANY, "value2_resolved": NodeParameterType.ANY},
            tags=["control flow", "logic", "conditional"],
            author="ACT Framework"
        )

    def _check_and_convert_string(self, value: Any) -> Any:
        """
        Checks if a value is a string that looks like a bool/number and converts it.
        Returns the original value otherwise. Less aggressive than _try_convert_type.
        """
        if isinstance(value, str):
            # Try boolean (case-insensitive)
            if value.lower() == 'true': return True
            if value.lower() == 'false': return False
            # Try int
            if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                try: return int(value)
                except ValueError: pass # Should not happen
            # Try float
            is_maybe_float = False
            if '.' in value and value.replace('.', '', 1).isdigit(): is_maybe_float = True
            # Don't convert pure integers here, only strings that look like floats
            # if value.isdigit(): is_maybe_float = True
            if 'e' in value.lower():
                 parts = value.lower().split('e')
                 if len(parts) == 2:
                     try: float(parts[0]); int(parts[1]); is_maybe_float = True
                     except ValueError: pass
            if value.startswith('-') and value[1:].replace('.', '', 1).isdigit() and value.count('.') <= 1: is_maybe_float = True

            if is_maybe_float:
                try: return float(value)
                except ValueError: pass
        return value # Return original if not a convertible string


    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the comparison logic, respecting incoming types more strictly."""
        node_name = node_data.get('__node_name', 'if_node')
        logger.debug(f"Executing IfNode: {node_name}")
        try:
            # --- 1. Validation and Parameter Extraction ---
            params = node_data.get("params", {})
            val1 = params.get("value1")
            op = params.get("operator")
            val2 = params.get("value2") # Might be None
            case_sensitive = params.get("case_sensitive", True)

            if not op or not isinstance(op, str):
                 raise NodeValidationError("Missing or invalid 'operator' parameter.")

            logger.info(f"{node_name} - Received Values: value1='{val1}' ({type(val1)}), op='{op}', value2='{val2}' ({type(val2)}), case_sensitive={case_sensitive}")

            # --- 2. Perform Comparison (Using original types primarily) ---
            condition_met = False
            error_msg = None

            try:
                # Prepare string versions mainly for case-insensitivity checks
                str_val1 = str(val1)
                str_val2 = str(val2) if val2 is not None else None
                str_val1_cmp = str_val1.lower() if not case_sensitive and isinstance(val1, str) else str_val1
                str_val2_cmp = str_val2.lower() if not case_sensitive and isinstance(val2, str) and str_val2 is not None else str_val2

                # --- Handle Operators ---
                unary_ops = ["is_true", "is_false", "is_empty", "is_not_empty"]
                binary_ops_req_val2 = ["==", "eq", "!=", "ne", ">", "gt", "<", "lt", ">=", "ge", "<=", "le",
                                       "contains", "not contains", "starts_with", "ends_with"]

                if op in unary_ops:
                    # For unary ops, try converting potential string bools/numbers first for intuitive results
                    # e.g., is_true on "true" should be True, is_empty on "" should be True
                    conv_val1 = self._check_and_convert_string(val1)
                    logger.debug(f"{node_name} - Unary op '{op}' using value: '{conv_val1}' ({type(conv_val1)})")

                    if op == "is_true": condition_met = bool(conv_val1)
                    elif op == "is_false": condition_met = not bool(conv_val1)
                    elif op == "is_empty": condition_met = conv_val1 is None or (hasattr(conv_val1, '__len__') and len(conv_val1) == 0)
                    elif op == "is_not_empty": condition_met = conv_val1 is not None and (not hasattr(conv_val1, '__len__') or len(conv_val1) > 0)

                elif op in binary_ops_req_val2:
                    if val2 is None:
                         raise ValueError(f"Operator '{op}' requires value2, but it was None.")

                    # --- Equality / Inequality (Strict Python Comparison) ---
                    # Let Python handle type differences (e.g., 5 == '5' is False)
                    # Only apply case-insensitivity if *both* are strings
                    elif op in ["==", "eq"]:
                         if not case_sensitive and isinstance(val1, str) and isinstance(val2, str):
                             condition_met = str_val1_cmp == str_val2_cmp
                         else:
                             condition_met = val1 == val2 # Direct comparison
                    elif op in ["!=", "ne"]:
                         if not case_sensitive and isinstance(val1, str) and isinstance(val2, str):
                              condition_met = str_val1_cmp != str_val2_cmp
                         else:
                              condition_met = val1 != val2 # Direct comparison

                    # --- Numeric Comparisons ---
                    # Attempt conversion *only if direct comparison raises TypeError*
                    elif op in [">", "gt", "<", "lt", ">=", "ge", "<=", "le"]:
                         try:
                             # Try direct comparison first
                             if op in [">", "gt"]: condition_met = val1 > val2
                             elif op in ["<", "lt"]: condition_met = val1 < val2
                             elif op in [">=", "ge"]: condition_met = val1 >= val2
                             elif op in ["<=", "le"]: condition_met = val1 <= val2
                         except TypeError:
                             # Fallback: Try converting string-like numbers if a TypeError occurred
                             logger.debug(f"{node_name} - TypeError on direct numeric compare, attempting conversion...")
                             conv_val1 = self._check_and_convert_string(val1)
                             conv_val2 = self._check_and_convert_string(val2)
                             logger.debug(f"{node_name} - Converted for fallback compare: '{conv_val1}' ({type(conv_val1)}), '{conv_val2}' ({type(conv_val2)})")
                             # Retry comparison only if *both* converted to numbers
                             if isinstance(conv_val1, numbers.Number) and isinstance(conv_val2, numbers.Number):
                                 if op in [">", "gt"]: condition_met = conv_val1 > conv_val2
                                 elif op in ["<", "lt"]: condition_met = conv_val1 < conv_val2
                                 elif op in [">=", "ge"]: condition_met = conv_val1 >= conv_val2
                                 elif op in ["<=", "le"]: condition_met = conv_val1 <= conv_val2
                             else:
                                 # If conversion didn't result in two numbers, re-raise original error
                                 raise TypeError(f"Numeric comparison failed even after conversion attempt for types {type(val1)} and {type(val2)}")

                    # --- String/Container Operations ---
                    elif op == "contains":
                         container = str_val1_cmp if isinstance(val1, str) and not case_sensitive else val1
                         item_to_check = str_val2_cmp if isinstance(val1, str) and isinstance(val2, str) and not case_sensitive else val2
                         if isinstance(container, (str, list, tuple, dict)):
                             try: condition_met = item_to_check in container
                             except TypeError as e_in: # e.g., checking if list is in string
                                 error_msg = f"'contains' check failed: {e_in}"
                         else: error_msg = f"'contains' is not supported on type {type(container)}"
                    elif op == "not contains":
                         container = str_val1_cmp if isinstance(val1, str) and not case_sensitive else val1
                         item_to_check = str_val2_cmp if isinstance(val1, str) and isinstance(val2, str) and not case_sensitive else val2
                         if isinstance(container, (str, list, tuple, dict)):
                             try: condition_met = item_to_check not in container
                             except TypeError as e_in:
                                 error_msg = f"'not contains' check failed: {e_in}"
                         else: error_msg = f"'not contains' is not supported on type {type(container)}"
                    elif op == "starts_with":
                         if isinstance(val1, str) and isinstance(val2, str):
                             condition_met = str_val1_cmp.startswith(str_val2_cmp)
                         else: error_msg = f"'starts_with' requires string types (got {type(val1)}, {type(val2)})"
                    elif op == "ends_with":
                         if isinstance(val1, str) and isinstance(val2, str):
                             condition_met = str_val1_cmp.endswith(str_val2_cmp)
                         else: error_msg = f"'ends_with' requires string types (got {type(val1)}, {type(val2)})"

                else:
                    error_msg = f"Unsupported operator: {op}"

                if error_msg:
                    raise NodeExecutionError(error_msg)

            except TypeError as e:
                error_message = f"Type error during comparison for operator '{op}': {e}. Comparing '{val1}' ({type(val1)}) and '{val2}' ({type(val2)})"
                logger.error(f"{node_name} - {error_message}")
                return self.handle_error(NodeExecutionError(error_message), context=f"{node_name} Comparison")
            except ValueError as e:
                 logger.error(f"{node_name} - Value error during comparison: {e}")
                 return self.handle_error(NodeExecutionError(str(e)), context=f"{node_name} Setup")
            except NodeExecutionError as e:
                 logger.error(f"{node_name} - Execution error during comparison: {e}")
                 return self.handle_error(e, context=f"{node_name} Comparison Logic")
            except Exception as e:
                logger.error(f"{node_name} - Unexpected error during comparison: {e}", exc_info=True)
                return self.handle_error(e, context=f"{node_name} Comparison")

            # --- 4. Return Result ---
            logger.info(f"{node_name} - Condition '{op}' evaluated to: {condition_met}")
            return {
                "status": "success",
                "result": {
                    "result": condition_met,
                    "value1_resolved": val1, # Return the original resolved value
                    "value2_resolved": val2, # Return the original resolved value
                },
                "message": f"Condition evaluated to {condition_met}"
            }

        except NodeValidationError as e:
            logger.error(f"Validation Error in {node_name}: {e}")
            return self.handle_error(e, context=f"{node_name} Validation")
        except Exception as e:
            logger.error(f"Unexpected Error in {node_name} execute method: {e}", exc_info=True)
            return self.handle_error(e, context=f"{node_name} Execution")


# --- Main Block for Standalone Testing ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s')

    async def main():
        print("\n--- Testing IfNode Standalone (v1.2.0 - Stricter Types) ---")
        if_node = IfNode()

        # Test cases, note adjusted expectations for T05
        test_cases = [
            # == Tests
            {"id": "T01", "params": {"value1": 10, "operator": "==", "value2": 10}, "expected": True},
            {"id": "T02", "params": {"value1": "hello", "operator": "eq", "value2": "hello"}, "expected": True},
            {"id": "T03", "params": {"value1": "Hello", "operator": "==", "value2": "hello"}, "expected": False},
            {"id": "T04", "params": {"value1": "Hello", "operator": "==", "value2": "hello", "case_sensitive": False}, "expected": True},
            {"id": "T05", "params": {"value1": 5, "operator": "==", "value2": "5"}, "expected": False}, # EXPECT FALSE NOW (int != str)
            {"id": "T06", "params": {"value1": True, "operator": "==", "value2": True}, "expected": True},
            # != Tests
            {"id": "T07", "params": {"value1": 10, "operator": "!=", "value2": 5}, "expected": True},
            {"id": "T08", "params": {"value1": "hello", "operator": "ne", "value2": "world"}, "expected": True},
            {"id": "T09", "params": {"value1": "Hello", "operator": "!=", "value2": "hello", "case_sensitive": False}, "expected": False},
            {"id": "T09b", "params": {"value1": 5, "operator": "!=", "value2": "5"}, "expected": True}, # EXPECT TRUE NOW (int != str)
            # > Tests
            {"id": "T10", "params": {"value1": 11, "operator": ">", "value2": 10}, "expected": True},
            {"id": "T11", "params": {"value1": 10, "operator": "gt", "value2": 10}, "expected": False},
            {"id": "T11b", "params": {"value1": "11", "operator": ">", "value2": "10"}, "expected": True}, # String comparison
            {"id": "T11c", "params": {"value1": "11", "operator": ">", "value2": 10}, "expected_status": "success", "expected": True}, # Fallback conversion triggers
            {"id": "T11d", "params": {"value1": 11, "operator": ">", "value2": "10"}, "expected_status": "success", "expected": True}, # Fallback conversion triggers
            # < Tests
            {"id": "T12", "params": {"value1": 9, "operator": "<", "value2": 10}, "expected": True},
            {"id": "T13", "params": {"value1": 10, "operator": "lt", "value2": 10}, "expected": False},
            # >= Tests
            {"id": "T14", "params": {"value1": 10, "operator": ">=", "value2": 10}, "expected": True},
            {"id": "T15", "params": {"value1": 11, "operator": "ge", "value2": 10}, "expected": True},
            # <= Tests
            {"id": "T16", "params": {"value1": 10, "operator": "<=", "value2": 10}, "expected": True},
            {"id": "T17", "params": {"value1": 9, "operator": "le", "value2": 10}, "expected": True},
            # Contains Tests
            {"id": "T18", "params": {"value1": "hello world", "operator": "contains", "value2": "world"}, "expected": True},
            {"id": "T19", "params": {"value1": "Hello World", "operator": "contains", "value2": "world", "case_sensitive": False}, "expected": True},
            {"id": "T20", "params": {"value1": ["a", "b", "c"], "operator": "contains", "value2": "b"}, "expected": True},
            {"id": "T21", "params": {"value1": ["a", "b", "c"], "operator": "contains", "value2": "d"}, "expected": False},
            {"id": "T22", "params": {"value1": {"key": "val"}, "operator": "contains", "value2": "key"}, "expected": True},
            # Not Contains Tests
            {"id": "T23", "params": {"value1": "hello world", "operator": "not contains", "value2": "planet"}, "expected": True},
            # Starts With Tests
            {"id": "T24", "params": {"value1": "hello world", "operator": "starts_with", "value2": "hello"}, "expected": True},
            {"id": "T25", "params": {"value1": "Hello world", "operator": "starts_with", "value2": "hello", "case_sensitive": False}, "expected": True},
             # Ends With Tests
            {"id": "T26", "params": {"value1": "hello world", "operator": "ends_with", "value2": "world"}, "expected": True},
            {"id": "T27", "params": {"value1": "hello World", "operator": "ends_with", "value2": "world", "case_sensitive": False}, "expected": True},
            # Boolean / Empty Tests (using conversion)
            {"id": "T28", "params": {"value1": True, "operator": "is_true"}, "expected": True},
            {"id": "T29", "params": {"value1": "true", "operator": "is_true"}, "expected": True}, # Converted
            {"id": "T30", "params": {"value1": 1, "operator": "is_true"}, "expected": True},
            {"id": "T31", "params": {"value1": "0", "operator": "is_false"}, "expected": True}, # Converted
            {"id": "T32", "params": {"value1": "", "operator": "is_empty"}, "expected": True},
            {"id": "T33", "params": {"value1": None, "operator": "is_empty"}, "expected": True},
            {"id": "T34", "params": {"value1": [], "operator": "is_empty"}, "expected": True},
            {"id": "T35", "params": {"value1": {}, "operator": "is_empty"}, "expected": True},
            {"id": "T36", "params": {"value1": " ", "operator": "is_not_empty"}, "expected": True},
            {"id": "T37", "params": {"value1": 0, "operator": "is_not_empty"}, "expected": True},
             # Error Cases
            {"id": "E01", "params": {"value1": 10, "operator": ">", "value2": "a"}, "expected_status": "error", "expected_msg_part": "Type error"}, # Direct compare fails, conversion fails
            {"id": "E02", "params": {"value1": [1,2], "operator": "==", "value2": None}, "expected_status": "error", "expected_msg_part": "requires value2"},
            {"id": "E03", "params": {"value1": "hello", "operator": "invalid_op", "value2": "world"}, "expected_status": "error", "expected_msg_part": "Unsupported operator"},
            {"id": "E04", "params": {"value1": 10, "operator": "contains", "value2": 1}, "expected_status": "error", "expected_msg_part": "not supported on type"},
            {"id": "E05", "params": {"value1": "abc", "operator": "starts_with", "value2": 123}, "expected_status": "error", "expected_msg_part": "requires string types"},
        ]

        passed = 0
        failed = 0
        for test in test_cases:
            print(f"\n--- Running Test Case: {test['id']} ---")
            test_node_data = {
                "params": test["params"],
                "__node_name": f"if_test_{test['id']}",
                "__execution_id": "test_exec_123"
            }
            print(f"Input Params: {test['params']}")
            result = await if_node.execute(test_node_data)
            print(f"Result: {json.dumps(result, indent=2)}")

            status_ok = False
            detail_ok = False
            expected_status = test.get("expected_status", "success")

            if result.get("status") == expected_status:
                status_ok = True
                if expected_status == "success":
                    if result.get("result", {}).get("result") == test.get("expected"):
                        detail_ok = True
                    else:
                        print(f"🛑 FAIL: Expected result value {test.get('expected')} but got {result.get('result', {}).get('result')}")
                elif expected_status == "error":
                    expected_msg = test.get("expected_msg_part")
                    if expected_msg and expected_msg in result.get("message", ""):
                        detail_ok = True
                    elif expected_msg:
                        print(f"🛑 FAIL: Expected error message containing '{expected_msg}' but got '{result.get('message', '')}'")
                    else:
                        detail_ok = True
            else:
                 print(f"🛑 FAIL: Expected status {expected_status} but got {result.get('status')}")

            if status_ok and detail_ok:
                print(f"✅ PASS: Test Case {test['id']}")
                passed += 1
            else:
                print(f"🛑 FAIL: Test Case {test['id']}")
                failed += 1

        print("\n--- Test Summary ---")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print("--------------------\n")

    asyncio.run(main())