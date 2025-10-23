"""
ACT Single Node Executor

Execute single node operations using authenticated credentials from signature.
"""

import sys
import json
import importlib
from typing import Dict, Any
from pathlib import Path

# Add parent directory to path for ACT imports
act_dir = Path(__file__).parent.parent
if str(act_dir) not in sys.path:
    sys.path.insert(0, str(act_dir))

# Import ACT utilities
from .signature_manager import SignatureManager
from .logger import get_logger


class SingleNodeExecutor:
    """Execute single node operations"""

    def __init__(self, signature_path: str):
        """
        Initialize executor

        Args:
            signature_path: Path to .act.sig file
        """
        self.signature_manager = SignatureManager(signature_path)
        self.signature_manager.load()

    def execute(self, node_type: str, operation: str, params: Dict[str, Any],
                override_defaults: bool = False) -> Dict[str, Any]:
        """
        Execute a single node operation

        Args:
            node_type: Node type (e.g., "github")
            operation: Operation name (e.g., "list_issues")
            params: Operation parameters
            override_defaults: Skip merging with default parameters

        Returns:
            Execution result dictionary

        Raises:
            ValueError: If node not authenticated or not found
        """
        # Check authentication
        if not self.signature_manager.is_authenticated(node_type):
            raise ValueError(f"Node '{node_type}' is not authenticated")

        # Get auth data
        auth_data = self.signature_manager.get_node_auth(node_type, resolve_env=True)

        # Get defaults and merge with params
        if not override_defaults:
            defaults = self.signature_manager.get_node_defaults(node_type)
            params = {**defaults, **params}

        # Merge auth data into params
        params.update(auth_data)

        # Execute using ACT node
        result = self._execute_with_act(node_type, operation, params)

        return result

    def _execute_with_act(self, node_type: str, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute node using ACT's node system

        Args:
            node_type: Node type
            operation: Operation name
            params: Parameters including auth

        Returns:
            Execution result
        """
        try:
            # Import the module first, then find the correct class dynamically
            # This handles cases where file name != class name (e.g., OpenaiNode.py contains OpenAINode)
            import inspect

            # Try common file name patterns
            possible_module_names = []

            # Pattern 1: Exact capitalization (e.g., "github" -> "GithubNode")
            possible_module_names.append(f"act.nodes.{node_type.capitalize()}Node")

            # Pattern 2: Special cases with internal caps (e.g., "github" -> "GitHubNode")
            special_cases = {
                'github': 'GitHub',
                'gitlab': 'GitLab',
                'clickup': 'ClickUp',
                'hubspot': 'HubSpot',
                'linkedin': 'LinkedIn',
                'openai': 'OpenAI',
                'youtube': 'YouTube',
            }
            if node_type.lower() in special_cases:
                possible_module_names.insert(0, f"act.nodes.{special_cases[node_type.lower()]}Node")

            # Try to import module
            node_module = None
            module_name = None
            for mod_name in possible_module_names:
                try:
                    node_module = importlib.import_module(mod_name)
                    module_name = mod_name
                    break
                except (ImportError, ModuleNotFoundError):
                    continue

            if not node_module:
                raise ImportError(f"Could not find module for node type '{node_type}'. Tried: {possible_module_names}")

            # Find the Node class in the module (the one that ends with 'Node' and is a class)
            NodeClass = None
            for name, obj in inspect.getmembers(node_module, inspect.isclass):
                if name.endswith('Node') and obj.__module__ == node_module.__name__:
                    NodeClass = obj
                    break

            if not NodeClass:
                raise ValueError(f"No Node class found in module '{module_name}'")

            # Create node instance
            node_instance = NodeClass()

            # Set parameters
            for key, value in params.items():
                if hasattr(node_instance, key):
                    setattr(node_instance, key, value)

            # Execute operation
            if hasattr(node_instance, operation):
                # Direct operation method exists
                operation_method = getattr(node_instance, operation)
                result = operation_method()
            elif hasattr(node_instance, 'execute'):
                # Use execute method with node_data format
                node_data = {
                    "params": {
                        "operation": operation,
                        **params
                    }
                }
                # Check if execute is async
                import asyncio
                import inspect
                execute_method = getattr(node_instance, 'execute')
                if inspect.iscoroutinefunction(execute_method):
                    result = asyncio.run(execute_method(node_data))
                else:
                    result = execute_method(node_data)
            else:
                raise ValueError(f"Operation '{operation}' not found on node '{node_type}'")

            return {
                "status": "success",
                "node_type": node_type,
                "operation": operation,
                "result": result
            }

        except ImportError as e:
            raise ValueError(f"Node '{node_type}' not found in ACT library: {e}")
        except Exception as e:
            raise RuntimeError(f"Execution failed: {e}")


def execute_single_node(signature_path: str, node_type: str, operation: str,
                        params: Dict[str, Any], override_defaults: bool = False,
                        verbose: bool = False) -> Dict[str, Any]:
    """
    Execute a single node operation (convenience function)

    Args:
        signature_path: Path to .act.sig file
        node_type: Node type
        operation: Operation name
        params: Parameters
        override_defaults: Skip defaults merge
        verbose: Enable verbose logging

    Returns:
        Execution result
    """
    logger = get_logger(f"execute_{node_type}.{operation}", verbose)
    logger.info(f"Executing {node_type}.{operation}")

    try:
        executor = SingleNodeExecutor(signature_path)
        result = executor.execute(node_type, operation, params, override_defaults)

        logger.success(f"Execution completed")
        logger.output_result(True, result)
        return result

    except Exception as e:
        logger.error(f"Execution failed", error=str(e))
        logger.output_result(False, error=str(e))
        raise


# CLI entry point
if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage: single_node_executor.py <signature_path> <node_type> <operation> <params_json> [--no-defaults] [--verbose]')
        print('Example: single_node_executor.py ~/.act.sig github list_issues \'{"state":"open"}\'')
        sys.exit(1)

    signature_path = sys.argv[1]
    node_type = sys.argv[2]
    operation = sys.argv[3]
    params_json = sys.argv[4]

    # Parse flags
    override_defaults = '--no-defaults' in sys.argv
    verbose = '--verbose' in sys.argv

    # Parse params
    try:
        params = json.loads(params_json)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"Invalid JSON params: {e}"
        }))
        sys.exit(1)

    # Execute
    try:
        execute_single_node(signature_path, node_type, operation, params, override_defaults, verbose)
    except Exception as e:
        # Error already output by logger
        sys.exit(1)
