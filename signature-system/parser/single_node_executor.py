"""
Single Node Executor
Executes single node operations using signature authentication and existing ACT library
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Add ACT library to path
ACT_LIB_PATH = Path(__file__).parent.parent.parent / "components/apps/act-docker/act"
sys.path.insert(0, str(ACT_LIB_PATH.parent))

from act.execution_manager import ExecutionManager
from .signature_parser import ActSignatureParser


class SingleNodeExecutor:
    """Executor for single node operations using ACT signatures and ExecutionManager"""

    def __init__(self, signature_path: str):
        """
        Initialize executor

        Args:
            signature_path: Path to .act.sig file
        """
        self.signature_path = signature_path
        self.parser = ActSignatureParser(signature_path)

    async def execute(
        self,
        node_type: str,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
        override_defaults: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a single node operation using existing ACT library

        Args:
            node_type: Node type (e.g., "github")
            operation: Operation name (e.g., "list_issues")
            params: Runtime parameters
            override_defaults: If True, don't merge with defaults

        Returns:
            Execution result dictionary

        Raises:
            ValueError: If node not authenticated or operation invalid
            RuntimeError: If execution fails
        """
        # Load signature
        self.parser.load()

        # Verify node is authenticated
        if not self.parser.is_authenticated(node_type):
            raise ValueError(
                f"Node '{node_type}' is not authenticated. "
                f"Please authenticate it first using add_node_to_signature."
            )

        # Verify operation exists
        operations = self.parser.get_operations(node_type)
        if operation not in operations:
            available = list(operations.keys())
            raise ValueError(
                f"Operation '{operation}' not found for node '{node_type}'. "
                f"Available operations: {', '.join(available)}"
            )

        # Get node configuration
        auth = self.parser.get_node_auth(node_type, resolve_env=True)
        defaults = {} if override_defaults else self.parser.get_node_defaults(node_type)

        # Merge parameters: defaults < auth < runtime params
        final_params = {
            **defaults,
            **auth,
            **(params or {}),
            'operation': operation
        }

        # Execute using ACT's ExecutionManager
        result = await self._execute_with_act(node_type, final_params)

        return result

    async def _execute_with_act(
        self,
        node_type: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute node using ACT's ExecutionManager

        Args:
            node_type: Node type
            params: Merged parameters (including operation)

        Returns:
            Execution result

        Raises:
            RuntimeError: If execution fails
        """
        try:
            # Import the specific node class
            node_module = f"act.nodes.{node_type}_node"
            node_class_name = f"{node_type.capitalize()}Node"

            # Dynamically import the node
            import importlib
            module = importlib.import_module(node_module)
            NodeClass = getattr(module, node_class_name)

            # Create node instance
            node_instance = NodeClass()

            # Set parameters
            for key, value in params.items():
                if hasattr(node_instance, key):
                    setattr(node_instance, key, value)

            # Execute the node
            if asyncio.iscoroutinefunction(node_instance.run):
                result = await node_instance.run()
            else:
                result = node_instance.run()

            return {
                'status': 'success',
                'node_type': node_type,
                'operation': params.get('operation'),
                'result': result,
                'timestamp': datetime.now().isoformat()
            }

        except ImportError as e:
            raise RuntimeError(f"Failed to load node '{node_type}': {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Node execution failed: {str(e)}")

    def validate_params(
        self,
        node_type: str,
        operation: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate parameters before execution

        Args:
            node_type: Node type
            operation: Operation name
            params: Parameters to validate

        Returns:
            Validation result
        """
        # Load signature
        self.parser.load()

        errors = []
        warnings = []

        # Check node authenticated
        if not self.parser.is_authenticated(node_type):
            errors.append(f"Node '{node_type}' is not authenticated")
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings
            }

        # Check operation exists
        operations = self.parser.get_operations(node_type)
        if operation not in operations:
            errors.append(f"Operation '{operation}' not found for '{node_type}'")
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings,
                'available_operations': list(operations.keys())
            }

        # Get operation info
        op_info = operations[operation]

        # Check required parameters
        required_params = op_info.get('required_params', [])
        defaults = self.parser.get_node_defaults(node_type)
        auth = self.parser.get_node_auth(node_type, resolve_env=False)

        # Merge params to check what's available
        merged = {
            **defaults,
            **{k: v for k, v in auth.items() if not ('{{.env.' in str(v))},
            **params
        }

        missing = [p for p in required_params if p not in merged]
        if missing:
            errors.append(f"Missing required parameters: {', '.join(missing)}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'merged_params': merged
        }


# CLI interface
async def main():
    """CLI interface for single node execution"""
    if len(sys.argv) < 4:
        print(json.dumps({
            'status': 'error',
            'error': 'Usage: python single_node_executor.py <signature_path> <node_type> <operation> [params_json]'
        }))
        sys.exit(1)

    signature_path = sys.argv[1]
    node_type = sys.argv[2]
    operation = sys.argv[3]
    params = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}

    executor = SingleNodeExecutor(signature_path)

    try:
        result = await executor.execute(node_type, operation, params)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'error': str(e),
            'node_type': node_type,
            'operation': operation
        }, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    from datetime import datetime
    asyncio.run(main())
