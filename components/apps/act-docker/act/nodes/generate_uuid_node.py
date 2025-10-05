# === File: act/nodes/generate_uuid_node.py ===

import logging
import uuid  # Standard library for UUID generation
from typing import Dict, Any, Optional

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
# Example: logger = logging.getLogger("act.nodes.GenerateUUIDNode")

# --- Node Implementation ---

class GenerateUUIDNode(BaseNode):
    node_type = "generate_uuid"
    """
    Generates a Version 4 (random) Universally Unique Identifier (UUID).
    """

    def get_schema(self) -> NodeSchema:
        """Returns the schema definition for the GenerateUUIDNode."""
        return NodeSchema(
            node_type="generate_uuid",
            version="1.0.0",
            description="Generates a standard Version 4 (random) UUID.",
            parameters=[
                NodeParameter(
                    name="hyphens",
                    type=NodeParameterType.BOOLEAN,
                    description="If true (default), includes hyphens in the output string (e.g., '123e4567-e89b-12d3-a456-426614174000'). If false, returns the hex representation without hyphens.",
                    required=False,
                    default=True
                )
                # Add version parameter later if needed, e.g., to support uuid1 or uuid5
                # NodeParameter(name="version", type=NodeParameterType.NUMBER, enum=[1, 4, 5], default=4, required=False)
            ],
            outputs={
                "uuid": NodeParameterType.STRING, # The generated UUID string
                "version": NodeParameterType.NUMBER # The UUID version generated (currently always 4)
            },
            tags=["utility", "id", "uuid", "generator", "identifier"],
            author="ACT Framework"
        )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates the UUID and formats it based on parameters."""
        node_name = node_data.get('__node_name', 'GenerateUUIDNode')
        logger.debug(f"Executing GenerateUUIDNode: {node_name}")

        try:
            # 1. Extract Parameters
            params = node_data.get("params", {})
            include_hyphens = params.get("hyphens", True) # Default to True if not provided

            # Validate parameter type (ExecutionManager might do this, but good practice)
            if not isinstance(include_hyphens, bool):
                 logger.warning(f"{node_name} - Parameter 'hyphens' received non-boolean value ({type(include_hyphens).__name__}). Using default True.")
                 include_hyphens = True

            logger.info(f"{node_name} - Generating UUID v4 (hyphens={include_hyphens}).")

            # 2. Generate UUID (Version 4)
            new_uuid: uuid.UUID = uuid.uuid4()

            # 3. Format Output String
            if include_hyphens:
                uuid_str = str(new_uuid)
            else:
                uuid_str = new_uuid.hex # Get 32-character hexadecimal string

            logger.debug(f"{node_name} - Generated UUID: {uuid_str}")

            # 4. Return Success Result
            return {
                "status": "success",
                "message": f"UUID (v4, hyphens={include_hyphens}) generated successfully.",
                "result": {
                    "uuid": uuid_str,
                    "version": 4 # Explicitly state version 4 was generated
                }
            }

        except Exception as e:
            # Catch any unexpected errors during generation (highly unlikely for uuid4)
            logger.error(f"Unexpected Error in {node_name} execute method: {e}", exc_info=True)
            return self.handle_error(e, context=f"{node_name} Execution")


# --- Main Block for Standalone Testing ---
if __name__ == "__main__":
    import asyncio
    import re # For testing format

    # Configure logging for direct script execution testing
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
    )

    async def main():
        print("\n--- Testing GenerateUUIDNode Standalone ---")
        node = GenerateUUIDNode()

        # Test Case 1: Default (hyphens=True)
        print("\n--- Test Case 1: Default (hyphens=True) ---")
        test_data_1 = {"params": {}, "__node_name": "TestUUIDDefault"}
        result_1 = await node.execute(test_data_1)
        print(f"Result 1: {json.dumps(result_1, indent=2)}")
        assert result_1["status"] == "success"
        assert "uuid" in result_1["result"]
        assert isinstance(result_1["result"]["uuid"], str)
        assert result_1["result"]["version"] == 4
        # Check format with hyphens (8-4-4-4-12)
        assert re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$', result_1["result"]["uuid"])

        # Test Case 2: Explicitly hyphens=True
        print("\n--- Test Case 2: hyphens=True ---")
        test_data_2 = {"params": {"hyphens": True}, "__node_name": "TestUUIDHyphensTrue"}
        result_2 = await node.execute(test_data_2)
        print(f"Result 2: {json.dumps(result_2, indent=2)}")
        assert result_2["status"] == "success"
        assert "uuid" in result_2["result"]
        assert isinstance(result_2["result"]["uuid"], str)
        assert result_2["result"]["version"] == 4
        assert re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$', result_2["result"]["uuid"])

        # Test Case 3: Explicitly hyphens=False
        print("\n--- Test Case 3: hyphens=False ---")
        test_data_3 = {"params": {"hyphens": False}, "__node_name": "TestUUIDHyphensFalse"}
        result_3 = await node.execute(test_data_3)
        print(f"Result 3: {json.dumps(result_3, indent=2)}")
        assert result_3["status"] == "success"
        assert "uuid" in result_3["result"]
        assert isinstance(result_3["result"]["uuid"], str)
        assert result_3["result"]["version"] == 4
        # Check format without hyphens (32 hex chars)
        assert re.match(r'^[a-f0-9]{32}$', result_3["result"]["uuid"])
        assert '-' not in result_3["result"]["uuid"]

        # Test Case 4: Invalid type for hyphens (should default to True)
        print("\n--- Test Case 4: Invalid type for hyphens ---")
        test_data_4 = {"params": {"hyphens": "yes"}, "__node_name": "TestUUIDInvalidType"} # Pass string instead of bool
        result_4 = await node.execute(test_data_4)
        print(f"Result 4: {json.dumps(result_4, indent=2)}")
        assert result_4["status"] == "success" # Node handles gracefully
        assert "uuid" in result_4["result"]
        assert result_4["result"]["version"] == 4
        # Should have defaulted to hyphens=True
        assert re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$', result_4["result"]["uuid"])

        print("\n--- All GenerateUUIDNode tests completed ---")

    # Run the async main function for testing
    asyncio.run(main())