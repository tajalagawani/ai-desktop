# === File: act/nodes/log_message_node.py ===

import logging
import json
from typing import Dict, Any, Optional, List

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
             logger = logging.getLogger(__name__) # Need logger in fallback too
             logger.error(f"Error in {context}: {error}", exc_info=True)
             return {"status": "error", "message": f"Error in {context}: {error}"}

# Use a logger specific to this module
logger = logging.getLogger(__name__)
# Example of getting a logger specific to ACT nodes:
# logger = logging.getLogger("act.nodes.LogMessageNode")


class LogMessageNode(BaseNode):
    node_type = "log_message"
    """
    Logs a message to the standard Python logging system at a specified level.
    Expects the message content (including any placeholders) to be resolved
    by the ExecutionManager before execution.
    """

    # Define valid logging levels corresponding to Python's logging module
    _VALID_LOG_LEVELS = ["debug", "info", "warning", "error", "critical"]

    def get_schema(self) -> NodeSchema:
        """Returns the schema definition for the LogMessageNode."""
        return NodeSchema(
            node_type="log_message",
            version="1.0.0",
            description="Logs a specified message using the Python logging framework.",
            parameters=[
                NodeParameter(
                    name="message",
                    type=NodeParameterType.STRING,
                    description="The message content to log (placeholders should be pre-resolved).",
                    required=True
                ),
                NodeParameter(
                    name="level",
                    type=NodeParameterType.STRING,
                    description="The logging level (debug, info, warning, error, critical).",
                    required=False, # Not strictly required, will use default
                    default="info", # Default log level if not specified
                    enum=self._VALID_LOG_LEVELS # Use the defined valid levels for validation/UI hint
                )
            ],
            outputs={
                # Primarily signals success/failure via status/message
                "logged_level": NodeParameterType.STRING, # The actual level used for logging
                "logged_message": NodeParameterType.STRING, # The actual message logged
            },
            tags=["utility", "logging", "debug", "output"],
            author="ACT Framework" # Or your name/org
        )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Logs the message using the specified level."""
        node_name = node_data.get('__node_name', 'LogMessageNode') # Get context if manager provides it
        logger.debug(f"Executing LogMessageNode: {node_name}")

        try:
            # 1. Extract Parameters (assuming validation happened if BaseNode provides it)
            params = node_data.get("params", {})
            # The message received here should already have placeholders resolved by the manager
            message_to_log = params.get("message")
            level_str_input = params.get("level", "info") # Get provided level or default to 'info'

            # 2. Validate Input
            if message_to_log is None: # Check even if schema requires it
                raise NodeValidationError("Required parameter 'message' is missing.")

            # Ensure message is a string (it should be after resolution, but check)
            if not isinstance(message_to_log, str):
                 logger.warning(f"{node_name} - Received 'message' is not a string (type: {type(message_to_log)}), converting to string.")
                 message_to_log = str(message_to_log)

            # Validate and normalize the log level
            level_str = str(level_str_input).lower() # Normalize to lower case
            if level_str not in self._VALID_LOG_LEVELS:
                logger.warning(f"{node_name} - Invalid log level '{level_str_input}' provided. Defaulting to 'info'.")
                level_str = "info" # Fallback to default level

            # 3. Perform Logging Action
            # Get the appropriate logging function from the logger
            # Use getattr for dynamic dispatch based on the level string
            log_function = getattr(logger, level_str, logger.info) # Default to info if getattr fails

            # Log the message, adding node name for context in the logs
            log_output = f"[{node_name}] {message_to_log}"
            log_function(log_output)
            logger.debug(f"{node_name} - Logged message at level '{level_str}'.")

            # 4. Return Success Result
            return {
                "status": "success",
                "message": f"Message logged successfully at level '{level_str}'.",
                # Include actual logged info in the result for potential downstream use
                "result": {
                    "logged_level": level_str,
                    "logged_message": message_to_log
                }
            }

        except NodeValidationError as e:
             logger.error(f"Validation Error in {node_name}: {e}")
             # Use handle_error from BaseNode if available and appropriate
             if hasattr(self, 'handle_error'):
                 return self.handle_error(e, context=f"{node_name} Validation")
             else:
                 return {"status": "error", "message": f"Validation Error: {e}"}
        except Exception as e:
            # Catch any other unexpected errors during execution
            logger.error(f"Unexpected Error in {node_name} execute method: {e}", exc_info=True)
            # Use handle_error from BaseNode if available and appropriate
            if hasattr(self, 'handle_error'):
                 return self.handle_error(e, context=f"{node_name} Execution")
            else:
                 return {"status": "error", "message": f"Unexpected Error: {e}"}


# --- Main Block for Standalone Testing ---
# === Register Node with Registry (happens during module import) ===
logger.debug("🔍 About to register node type 'log_message'")
try:
    from base_node import NodeRegistry
    NodeRegistry.register("log_message", LogMessageNode)
    logger.debug("✅ REGISTERED LogMessageNode as 'log_message' at module level")
except Exception as e:
    logger.error(f"❌ ERROR registering LogMessageNode at module level: {str(e)}")

if __name__ == "__main__":
    import asyncio

    # Configure logging for direct script execution testing
    # Set level to DEBUG to see all log levels from the node itself
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
    )

    async def main():
        print("\n--- Testing LogMessageNode Standalone ---")
        log_node = LogMessageNode()

        # Test Case 1: Basic Info Log
        print("\n--- Test Case 1: INFO level ---")
        test_data_1 = {
            "params": {"message": "This is an informational message.", "level": "info"},
            "__node_name": "TestNodeInfo" # Simulate context
        }
        result_1 = await log_node.execute(test_data_1)
        print(f"Node Result 1: {json.dumps(result_1, indent=2)}")
        assert result_1["status"] == "success"
        assert result_1["result"]["logged_level"] == "info"

        # Test Case 2: Warning Log
        print("\n--- Test Case 2: WARNING level ---")
        test_data_2 = {
            "params": {"message": "This is a warning!", "level": "warning"},
            "__node_name": "TestNodeWarn"
        }
        result_2 = await log_node.execute(test_data_2)
        print(f"Node Result 2: {json.dumps(result_2, indent=2)}")
        assert result_2["status"] == "success"
        assert result_2["result"]["logged_level"] == "warning"

        # Test Case 3: Default Level (info)
        print("\n--- Test Case 3: Default level ---")
        test_data_3 = {
            "params": {"message": "Logging with the default level."},
            "__node_name": "TestNodeDefault"
        }
        result_3 = await log_node.execute(test_data_3)
        print(f"Node Result 3: {json.dumps(result_3, indent=2)}")
        assert result_3["status"] == "success"
        assert result_3["result"]["logged_level"] == "info"

        # Test Case 4: Invalid Level (should default to info)
        print("\n--- Test Case 4: Invalid level ---")
        test_data_4 = {
            "params": {"message": "This level is not valid.", "level": "verbose"},
            "__node_name": "TestNodeInvalidLevel"
        }
        result_4 = await log_node.execute(test_data_4)
        print(f"Node Result 4: {json.dumps(result_4, indent=2)}")
        assert result_4["status"] == "success" # Still succeeds, but logs warning and uses default
        assert result_4["result"]["logged_level"] == "info"

        # Test Case 5: Error Log
        print("\n--- Test Case 5: ERROR level ---")
        test_data_5 = {
            "params": {"message": "Something went wrong!", "level": "error"},
            "__node_name": "TestNodeErrorLog"
        }
        result_5 = await log_node.execute(test_data_5)
        print(f"Node Result 5: {json.dumps(result_5, indent=2)}")
        assert result_5["status"] == "success"
        assert result_5["result"]["logged_level"] == "error"

        # Test Case 6: Missing Message (should fail)
        print("\n--- Test Case 6: Missing message ---")
        test_data_6 = {
            "params": {"level": "info"}, # Message is missing
             "__node_name": "TestNodeMissingMsg"
        }
        result_6 = await log_node.execute(test_data_6)
        print(f"Node Result 6: {json.dumps(result_6, indent=2)}")
        assert result_6["status"] == "error"
        assert "missing" in result_6["message"].lower()


    # Run the async main function for testing
    asyncio.run(main())

