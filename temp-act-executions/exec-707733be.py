import sys
import os
import json
from pathlib import Path

# Add ACT docker directory to path
sys.path.insert(0, '/Users/tajnoah/Downloads/act')

try:
    # Import ACT ExecutionManager
    from act.execution_manager import ExecutionManager

    # Initialize execution manager with the ACT file
    execution_manager = ExecutionManager('/Users/tajnoah/Downloads/ai-desktop/temp-act-executions/iss-location.act')

    # Check if this is an agent workflow (has ACI routes)
    if execution_manager.has_agent_config():
        # This is an API workflow - needs deployment
        config = execution_manager.get_agent_config()
        deployment = execution_manager.get_deployment_config() if hasattr(execution_manager, 'get_deployment_config') else {}

        result = {
            "success": True,
            "mode": "agent",
            "workflow_name": config.get('agent_name', 'Unknown'),
            "port": config.get('port', deployment.get('port', 9000)),
            "message": "API workflow detected - requires deployment to Docker",
            "requires_deployment": True,
            "flow_file": 'iss-location.act'
        }
    else:
        # This is a mini-ACT - execute it immediately
        execution_result = execution_manager.execute_workflow(initial_input=None)

        result = {
            "success": True,
            "mode": "miniact",
            "message": "Flow executed successfully",
            "result": execution_result
        }

    print(json.dumps(result, default=str))

except Exception as e:
    import traceback
    result = {
        "success": False,
        "error": str(e),
        "error_type": type(e).__name__,
        "traceback": traceback.format_exc()
    }
    print(json.dumps(result))
