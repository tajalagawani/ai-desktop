# === File: act/nodes/switch_node.py ===

import logging
import json
from typing import Dict, Any, Optional, List, Union

# Assuming base_node.py is in the same directory or accessible via the package structure
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
    # Define dummy classes if BaseNode cannot be imported
    class NodeValidationError(Exception): pass
    class NodeExecutionError(Exception): pass
    class NodeParameterType: ANY="any"; STRING="string"; BOOLEAN="boolean"; NUMBER="number"; ARRAY="array"; OBJECT="object"; SECRET="secret"
    class NodeParameter:
        def __init__(self, name, type, description, required=True, default=None, enum=None):
            self.name = name; self.type = type; self.description = description; self.required = required; self.default = default; self.enum = enum
    class NodeSchema:
        def __init__(self, node_type, version, description, parameters, outputs, tags=None, author=None):
            self.node_type=node_type; self.version=version; self.description=description; self.parameters=parameters; self.outputs=outputs; self.tags=tags; self.author=author
    class BaseNode:
        def get_schema(self): raise NotImplementedError
        async def execute(self, data): raise NotImplementedError
        def validate_schema(self, data): return data.get("params", {}) # Simplistic
        def handle_error(self, error, context=""):
             logger = logging.getLogger(__name__) # Need logger in fallback too
             logger.error(f"Error in {context}: {error}", exc_info=True)
             return {"status": "error", "message": f"Error in {context}: {error}", "error_type": type(error).__name__}

# --- Node Logger ---
logger = logging.getLogger(__name__)
# Example: logger = logging.getLogger("act.nodes.SwitchNode")

# --- Node Implementation ---

class SwitchNode(BaseNode):
    node_type = "switch"
    """
    Routes workflow execution to different downstream nodes based on matching
    an input value against predefined cases. Includes an optional default path.
    """

    def get_schema(self) -> NodeSchema:
        """Returns the schema definition for the SwitchNode."""
        return NodeSchema(
            node_type="switch",
            version="1.0.0",
            description="Evaluates an input value and routes execution to the node associated with the first matching case value, or to a default node.",
            parameters=[
                NodeParameter(
                    name="input_value",
                    type=NodeParameterType.ANY,
                    description="The value to evaluate and match against cases (resolved from placeholders).",
                    required=True
                ),
                NodeParameter(
                    name="cases",
                    type=NodeParameterType.ARRAY,
                    # Example structure for Actfile:
                    # cases = [
                    #   {"case_value": "admin", "next_node": "AdminPathNode"},
                    #   {"case_value": "user", "next_node": "UserPathNode"},
                    #   {"case_value": 100, "next_node": "NumericPathNode"},
                    #   {"case_value": true, "next_node": "BooleanPathNode"},
                    #   {"case_value": null, "next_node": "NullPathNode"}
                    # ]
                    description="An array of case objects. Each object must have 'case_value' (the value to match) and 'next_node' (the name of the node to execute if matched). Order matters - the first match is used.",
                    required=True # Typically needs at least one case, or only default makes sense
                ),
                NodeParameter(
                    name="default_node",
                    type=NodeParameterType.STRING,
                    description="Optional. The name of the node to execute if none of the 'cases' match the 'input_value'.",
                    required=False,
                    default=None
                )
            ],
            outputs={
                # Output indicates which path was chosen
                "matched_case_value": NodeParameterType.ANY, # The value from 'cases' that matched, or null if default taken
                "selected_node": NodeParameterType.STRING # The name of the node selected for the next step (can be null if no match and no default)
            },
            tags=["control flow", "logic", "conditional", "routing", "switch", "case"],
            author="ACT Framework"
        )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates the input value against cases and determines the next node."""
        node_name = node_data.get('__node_name', 'SwitchNode')
        logger.debug(f"Executing SwitchNode: {node_name}")

        try:
            # 1. Extract Parameters (Values should be resolved by ExecutionManager)
            params = node_data.get("params", {})
            input_value = params.get("input_value") # The actual resolved value
            cases = params.get("cases")
            default_node = params.get("default_node") # Can be None

            logger.info(f"{node_name} - Evaluating input value: '{str(input_value)[:50]}...' ({type(input_value).__name__})")

            # 2. Validate Parameters Structure
            if not isinstance(cases, list):
                raise NodeValidationError("'cases' parameter must be a list (array).")
            if default_node is not None and not isinstance(default_node, str):
                 raise NodeValidationError("'default_node' parameter must be a string (node name).")

            # Validate structure of each case object
            for i, case_item in enumerate(cases):
                if not isinstance(case_item, dict):
                    raise NodeValidationError(f"Item at index {i} in 'cases' is not a dictionary (object).")
                if "case_value" not in case_item: # Key must exist, value can be None
                    raise NodeValidationError(f"Item at index {i} in 'cases' is missing the required 'case_value' key.")
                if not case_item.get("next_node") or not isinstance(case_item.get("next_node"), str):
                    raise NodeValidationError(f"Item at index {i} in 'cases' is missing or has an invalid 'next_node' (must be a non-empty string).")

            # 3. Find Matching Case
            selected_node: Optional[str] = None
            matched_case_value: Any = None
            match_found = False

            logger.debug(f"{node_name} - Checking {len(cases)} cases...")
            for case_dict in cases:
                case_value = case_dict["case_value"]
                next_node_for_case = case_dict["next_node"]

                # Perform strict equality check (respecting types)
                if input_value == case_value:
                    selected_node = next_node_for_case
                    matched_case_value = case_value
                    match_found = True
                    logger.info(f"{node_name} - Match found! Input '{str(input_value)[:50]}...' == Case '{str(case_value)[:50]}...'. Selecting node: '{selected_node}'")
                    break # Stop on first match

            # 4. Handle Default Case (if no match found)
            if not match_found:
                if default_node:
                    selected_node = default_node
                    matched_case_value = None # Explicitly None for default path
                    logger.info(f"{node_name} - No case matched. Using default node: '{selected_node}'")
                else:
                    selected_node = None # No match and no default means this path ends
                    matched_case_value = None
                    logger.info(f"{node_name} - No case matched and no default node provided. Workflow path ends here.")

            # 5. Return Result (signaling the chosen path)
            message = f"Selected node '{selected_node}'." if selected_node else "No matching case or default node found."
            if match_found:
                 message = f"Input matched case '{str(matched_case_value)[:50]}...'. " + message

            return {
                "status": "success",
                "message": message,
                "result": {
                    "matched_case_value": matched_case_value,
                    "selected_node": selected_node
                }
            }

        except NodeValidationError as e:
             logger.error(f"Validation Error in {node_name}: {e}")
             return self.handle_error(e, context=f"{node_name} Validation")
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected Error in {node_name} execute method: {e}", exc_info=True)
            return self.handle_error(e, context=f"{node_name} Execution")


# --- Main Block for Standalone Testing ---
if __name__ == "__main__":
    import asyncio

    # Configure logging for direct script execution testing
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
    )

    async def main():
        print("\n--- Testing SwitchNode Standalone ---")
        node = SwitchNode()

        # Define common cases for tests
        test_cases_config = [
            {"case_value": "admin", "next_node": "AdminNode"},
            {"case_value": "user", "next_node": "UserNode"},
            {"case_value": 100, "next_node": "NumberNode"},
            {"case_value": True, "next_node": "BoolNode"},
            {"case_value": None, "next_node": "NullNode"} # Test matching None
        ]
        default_node_name = "DefaultNode"

        # Test scenarios
        tests = [
            {"id": "T1_Admin", "input": "admin", "cases": test_cases_config, "default": default_node_name, "expected_node": "AdminNode", "expected_value": "admin"},
            {"id": "T2_User", "input": "user", "cases": test_cases_config, "default": default_node_name, "expected_node": "UserNode", "expected_value": "user"},
            {"id": "T3_Number", "input": 100, "cases": test_cases_config, "default": default_node_name, "expected_node": "NumberNode", "expected_value": 100},
            {"id": "T4_Bool", "input": True, "cases": test_cases_config, "default": default_node_name, "expected_node": "BoolNode", "expected_value": True},
            {"id": "T5_Null", "input": None, "cases": test_cases_config, "default": default_node_name, "expected_node": "NullNode", "expected_value": None},
            {"id": "T6_Default", "input": "guest", "cases": test_cases_config, "default": default_node_name, "expected_node": "DefaultNode", "expected_value": None},
            {"id": "T7_NoMatchNoDefault", "input": "other", "cases": test_cases_config, "default": None, "expected_node": None, "expected_value": None},
            {"id": "T8_FirstMatchWins", "input": "admin", "cases": [{"case_value": "admin", "next_node": "FirstAdmin"}, {"case_value": "admin", "next_node": "SecondAdmin"}], "default": None, "expected_node": "FirstAdmin", "expected_value": "admin"},
            # Error cases
            {"id": "E1_CasesNotList", "input": "val", "cases": {"a":1}, "default": None, "expected_status": "error", "expected_msg_part": "must be a list"},
            {"id": "E2_CaseItemNotDict", "input": "val", "cases": ["string"], "default": None, "expected_status": "error", "expected_msg_part": "not a dictionary"},
            {"id": "E3_MissingCaseValue", "input": "val", "cases": [{"next_node": "A"}], "default": None, "expected_status": "error", "expected_msg_part": "missing the required 'case_value'"},
            {"id": "E4_MissingNextNode", "input": "val", "cases": [{"case_value": "a"}], "default": None, "expected_status": "error", "expected_msg_part": "missing or has an invalid 'next_node'"},
            {"id": "E5_InvalidDefaultNode", "input": "val", "cases": test_cases_config, "default": 123, "expected_status": "error", "expected_msg_part": "must be a string"},
        ]

        passed = 0
        failed = 0
        for test in tests:
            print(f"\n--- Running Test Case: {test['id']} ---")
            test_node_data = {
                "params": {
                    "input_value": test["input"],
                    "cases": test["cases"],
                    "default_node": test.get("default") # Use .get as default might be missing
                },
                "__node_name": f"switch_test_{test['id']}"
            }
            print(f"Input Value: {test['input']}")
            print(f"Cases: {test['cases']}")
            print(f"Default: {test.get('default')}")

            result = await node.execute(test_node_data)
            print(f"Result: {json.dumps(result, indent=2)}")

            status_ok = False
            detail_ok = False
            expected_status = test.get("expected_status", "success")

            if result.get("status") == expected_status:
                status_ok = True
                if expected_status == "success":
                    res_data = result.get("result", {})
                    if res_data.get("selected_node") == test.get("expected_node") and \
                       res_data.get("matched_case_value") == test.get("expected_value"):
                        detail_ok = True
                    else:
                        print(f"🛑 FAIL: Output mismatch. Expected node '{test.get('expected_node')}' with value '{test.get('expected_value')}', Got node '{res_data.get('selected_node')}' with value '{res_data.get('matched_case_value')}'")
                elif expected_status == "error":
                    expected_msg = test.get("expected_msg_part")
                    if expected_msg and expected_msg in result.get("message", ""):
                        detail_ok = True
                    elif expected_msg:
                        print(f"🛑 FAIL: Expected error message containing '{expected_msg}' but got '{result.get('message', '')}'")
                    else:
                        detail_ok = True # Status is error, no specific message check needed
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

    # Run the async main function for testing
    asyncio.run(main())