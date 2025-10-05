# === File: act/nodes/data_node.py ===

import logging
import json
from typing import Dict, Any, Optional, List, Union

# Assuming base_node.py is in the same directory or accessible via the package structure
from .base_node import (
    BaseNode, NodeSchema, NodeParameter, NodeParameterType,
    NodeValidationError, NodeExecutionError
)

# --- Node Logger ---
logger = logging.getLogger(__name__)
# Example: logger = logging.getLogger("act.nodes.DataNode")

# --- Node Implementation ---

class DataNode(BaseNode):
    node_type = "data"
    """
    Defines and outputs static data specified within its parameters.
    Useful for injecting configuration or initial data directly into the workflow.
    All parameters defined in the Actfile (except metadata like type, label)
    will be included in the output 'data' dictionary.
    """

    def get_schema(self) -> NodeSchema:
        """Returns the schema definition for the DataNode."""
        return NodeSchema(
            node_type="data", # Or "DataNode"
            version="1.0.0",
            description="Outputs a dictionary containing the data defined in its parameters.",
            parameters=[
                # No *required* parameters defined in the schema itself.
                # All key-value pairs defined in the Actfile node section
                # (other than type, label, description, position_*)
                # will become parameters for this node instance.
                NodeParameter(
                    name="*", # Indicate wildcard parameters allowed
                    type=NodeParameterType.ANY,
                    description="Any key-value pairs defined here will be outputted.",
                    required=False
                ),
            ],
            outputs={
                "data": NodeParameterType.OBJECT, # Outputs a dictionary containing all defined params
            },
            tags=["utility", "data", "static", "config", "input"],
            author="ACT Framework"
        )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Outputs the parameters defined for this node."""
        node_name = node_data.get('__node_name', 'DataNode')
        logger.debug(f"Executing DataNode: {node_name}")

        try:
            # Parameters are already resolved and processed by the ExecutionManager
            # The 'params' dictionary contains all the key-value pairs defined
            # in the Actfile for this node (excluding metadata).
            output_data = node_data.get("params", {})

            logger.info(f"{node_name} - Outputting defined data.")
            logger.debug(f"{node_name} - Data content: {json.dumps(output_data, default=str)}")

            # Return the parameters as the main result data
            return {
                "status": "success",
                "message": f"Data outputted successfully.",
                "result": {
                    "data": output_data
                }
            }

        except Exception as e:
            # Catch any unexpected errors
            logger.error(f"Unexpected Error in {node_name} execute method: {e}", exc_info=True)
            return self.handle_error(e, context=f"{node_name} Execution")

# --- Main Block for Standalone Testing ---
if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s')

    async def main():
        print("\n--- Testing DataNode Standalone ---")
        node = DataNode()

        # Simulate data passed by ExecutionManager after parsing/processing Actfile node
        test_node_data = {
            "type": "data",
            "label": "Test Config Data",
            "params": { # These would come from the Actfile definition
                "api_endpoint": "https://api.example.com/v1",
                "timeout_seconds": 30,
                "feature_flags": ["new_ui", "beta_access"],
                "user_details": {
                    "id": 123,
                    "role": "admin"
                },
                "is_enabled": True,
                "threshold": None # Test None value
            },
            "__node_name": "TestDataConfig"
        }

        print(f"Simulated Input Node Data:\n{json.dumps(test_node_data, indent=2)}")

        result = await node.execute(test_node_data)
        print(f"\nExecution Result:\n{json.dumps(result, indent=2)}")

        assert result["status"] == "success"
        assert "data" in result["result"]
        assert result["result"]["data"] == test_node_data["params"] # Output data should match input params
        assert result["result"]["data"]["timeout_seconds"] == 30
        assert result["result"]["data"]["feature_flags"] == ["new_ui", "beta_access"]
        assert result["result"]["data"]["threshold"] is None

        print("\n✅ DataNode test passed!")

    asyncio.run(main())