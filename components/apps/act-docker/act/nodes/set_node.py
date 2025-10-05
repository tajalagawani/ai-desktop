# === File: act/nodes/set_node.py ===

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
# Example: logger = logging.getLogger("act.nodes.SetNode")

# --- Node Implementation ---

class SetNode(BaseNode):
    """
    Sets a specific key to a given value in the workflow context.
    The value can be static or resolved from placeholders by the ExecutionManager.
    The primary output is the key-value pair itself under the 'result' key.
    """

    def get_schema(self) -> NodeSchema:
        """Returns the schema definition for the SetNode."""
        return NodeSchema(
            node_type="set", # Or "SetNode"
            version="1.0.0",
            description="Assigns a given value to a specified key, making it available via this node's result.",
            parameters=[
                NodeParameter(
                    name="key",
                    type=NodeParameterType.STRING,
                    description="The name (key) under which the value will be outputted.",
                    required=True
                ),
                NodeParameter(
                    name="value",
                    type=NodeParameterType.ANY, # Accepts any data type after resolution
                    description="The value to assign to the key. Can be static or use placeholders (e.g., {{node.result.data}}).",
                    required=True # A value must be provided to be set
                ),
                # Potential future extension:
                # NodeParameter(name="operation", type=NodeParameterType.STRING, enum=["overwrite", "append_list", "merge_dict"], default="overwrite", required=False, description="How to handle existing data if merging results.")
            ],
            outputs={
                # The result structure makes the key/value accessible
                "key": NodeParameterType.STRING, # The key that was set
                "value": NodeParameterType.ANY,   # The value that was set
                # Consider if just outputting the value itself under a dynamic key is better?
                # e.g., if key="user_name", output is {"user_name": "some value"}
                # Current approach outputs {"key": "user_name", "value": "some value"}
                # Let's stick to key/value output for now for simplicity.
            },
            tags=["utility", "data", "variable", "assignment"],
            author="ACT Framework"
        )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assigns the resolved value to the specified key in the output."""
        node_name = node_data.get('__node_name', 'SetNode')
        logger.debug(f"Executing SetNode: {node_name}")

        try:
            # 1. Extract Parameters
            params = node_data.get("params", {})
            key_to_set = params.get("key")
            # Value should be resolved by the ExecutionManager before getting here
            value_to_set = params.get("value")

            # 2. Validate Input
            if not key_to_set or not isinstance(key_to_set, str):
                raise NodeValidationError("Missing or invalid required parameter 'key' (must be a non-empty string).")

            # Check if 'value' key exists in params (even if value is None)
            if "value" not in params:
                 # This case should ideally be caught by schema validation if param is required
                 raise NodeValidationError("Missing required parameter 'value'.")

            logger.info(f"{node_name} - Setting key '{key_to_set}' to value: '{str(value_to_set)[:100]}...' (type: {type(value_to_set).__name__})")

            # 3. Perform "Set" Action (which is just structuring the output)
            # The ExecutionManager makes this available via self.node_results[node_name]
            return {
                "status": "success",
                "message": f"Value successfully prepared for key '{key_to_set}'.",
                "result": {
                    "key": key_to_set,
                    "value": value_to_set
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
        print("\n--- Testing SetNode Standalone ---")
        set_node = SetNode()

        test_cases = [
            {"id": "T1_String", "params": {"key": "user_greeting", "value": "Hello World!"}, "expected_value": "Hello World!"},
            {"id": "T2_Number", "params": {"key": "item_count", "value": 123}, "expected_value": 123},
            {"id": "T3_Boolean", "params": {"key": "is_active", "value": True}, "expected_value": True},
            {"id": "T4_List", "params": {"key": "tags", "value": ["alpha", "beta", 1]}, "expected_value": ["alpha", "beta", 1]},
            {"id": "T5_Dict", "params": {"key": "config", "value": {"timeout": 60, "retries": 3}}, "expected_value": {"timeout": 60, "retries": 3}},
            {"id": "T6_None", "params": {"key": "optional_feature", "value": None}, "expected_value": None},
            # Error Cases
            {"id": "E1_MissingKey", "params": {"value": "some value"}, "expected_status": "error", "expected_msg_part": "Missing or invalid required parameter 'key'"},
            {"id": "E2_EmptyKey", "params": {"key": "", "value": "some value"}, "expected_status": "error", "expected_msg_part": "Missing or invalid required parameter 'key'"},
            {"id": "E3_MissingValue", "params": {"key": "a_key"}, "expected_status": "error", "expected_msg_part": "Missing required parameter 'value'"}, # Note: This depends on BaseNode/Schema validation enforcing 'required' strictly before execute
        ]

        passed = 0
        failed = 0
        for test in test_cases:
            print(f"\n--- Running Test Case: {test['id']} ---")
            test_node_data = {
                "params": test["params"],
                "__node_name": f"set_test_{test['id']}"
            }
            print(f"Input Params: {test['params']}")
            result = await set_node.execute(test_node_data)
            print(f"Result: {json.dumps(result, indent=2)}")

            status_ok = False
            detail_ok = False
            expected_status = test.get("expected_status", "success")

            if result.get("status") == expected_status:
                status_ok = True
                if expected_status == "success":
                    res_data = result.get("result", {})
                    if res_data.get("key") == test["params"]["key"] and res_data.get("value") == test.get("expected_value"):
                        detail_ok = True
                    else:
                        print(f"🛑 FAIL: Output mismatch. Expected key '{test['params']['key']}' with value '{test.get('expected_value')}', Got: {res_data}")
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