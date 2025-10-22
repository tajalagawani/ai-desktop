"""
ACT Flow Executor

Execute complete ACT workflow files (.act files) with signature authentication.
"""

import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path

# Import ACT execution manager (relative import from parent)
import sys
from pathlib import Path
# Add parent directory to path to import ACT modules
act_dir = Path(__file__).parent.parent
if str(act_dir) not in sys.path:
    sys.path.insert(0, str(act_dir))

from execution_manager import ExecutionManager

# Import MCP utilities
from .signature_manager import SignatureManager
from .logger import get_logger


def execute_flow(flow_path: str, signature_path: str, parameters: Optional[Dict[str, Any]] = None,
                 verbose: bool = False) -> Dict[str, Any]:
    """
    Execute an ACT workflow file

    Args:
        flow_path: Path to .act workflow file
        signature_path: Path to .act.sig signature file
        parameters: Initial workflow parameters
        verbose: Enable verbose logging

    Returns:
        Execution result dictionary
    """
    logger = get_logger("execute_flow", verbose)
    logger.info(f"Executing workflow: {flow_path}")

    try:
        # Load signature for authenticated nodes
        sig_manager = SignatureManager(signature_path)
        sig_manager.load()
        logger.debug(f"Loaded signature from {signature_path}")

        # Initialize execution manager
        execution_manager = ExecutionManager(flow_path)
        logger.debug(f"Initialized execution manager")

        # Inject authenticated credentials into workflow
        authenticated_nodes = sig_manager.get_authenticated_nodes()
        logger.info(f"Found {len(authenticated_nodes)} authenticated nodes")

        for node_type in authenticated_nodes:
            auth_data = sig_manager.get_node_auth(node_type, resolve_env=True)
            defaults = sig_manager.get_node_defaults(node_type)

            # Inject into execution manager's context
            # This allows workflow nodes to use pre-authenticated credentials
            if hasattr(execution_manager, 'set_node_auth'):
                execution_manager.set_node_auth(node_type, {**defaults, **auth_data})
                logger.debug(f"Injected auth for {node_type}")

        # Check if this is an agent workflow (API workflow)
        if execution_manager.has_agent_config():
            config = execution_manager.get_agent_config()

            logger.info("Detected agent workflow (API mode)")
            result = {
                "mode": "agent",
                "workflow_name": config.get('agent_name', 'Unknown'),
                "port": config.get('port', 9000),
                "message": "API workflow detected - requires deployment",
                "requires_deployment": True
            }

        else:
            # Execute mini-ACT workflow
            logger.info("Executing mini-ACT workflow")
            execution_result = execution_manager.execute_workflow(initial_input=parameters)

            result = {
                "mode": "miniact",
                "message": "Workflow executed successfully",
                "result": execution_result
            }

        logger.success("Workflow execution completed")
        logger.output_result(True, result)
        return result

    except FileNotFoundError as e:
        error_msg = f"File not found: {e}"
        logger.error(error_msg)
        logger.output_result(False, error=error_msg)
        raise

    except Exception as e:
        error_msg = f"Execution failed: {e}"
        logger.error(error_msg, exception_type=type(e).__name__)
        logger.output_result(False, error=error_msg)
        raise


# CLI entry point
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: execute_flow.py <flow_path> <signature_path> [params_json] [--verbose]')
        print('Example: execute_flow.py workflow.act ~/.act.sig \'{"key":"value"}\'')
        sys.exit(1)

    flow_path = sys.argv[1]
    signature_path = sys.argv[2]
    params_json = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else None
    verbose = '--verbose' in sys.argv

    # Parse params
    params = None
    if params_json:
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
        execute_flow(flow_path, signature_path, params, verbose)
    except Exception:
        sys.exit(1)
