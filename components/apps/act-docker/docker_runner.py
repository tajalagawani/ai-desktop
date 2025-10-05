# === File: test.py (Runner for specific Actfile) ===

import os
import sys
import json
from pathlib import Path
import argparse

# --- Add the project root to the Python path ---
# Adjust this if test.py is located elsewhere relative to the 'act' package
script_dir = Path(__file__).parent.resolve()
# Assuming test.py is in act_workflow, and 'act' is inside act_workflow
project_root = script_dir
# If 'act' is one level up: project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# --- Add the 'act/nodes' directory to Python path for direct node discovery ---
# This is a common workaround if the ExecutionManager's internal discovery isn't robust
# for standalone scripts, or if __init__.py files are missing.
# Assumes your nodes are in 'langmvp/act_workflow/act/nodes/'
nodes_path = project_root / "act" / "nodes"
if nodes_path.is_dir():
    sys.path.insert(0, str(nodes_path))
else:
    print(f"WARNING: Node modules path not found at {nodes_path}. Please ensure it exists.")

# -----------------------------------------------------------------------------

try:
    # Now try importing the ExecutionManager and AgentServer
    from act.execution_manager import ExecutionManager
    from act.agent_server import AgentServer
except ImportError as e:
    print(f"Error importing ACT components: {e}")
    print("Please ensure:")
    print("1. You are running this script from a directory where Python can find the 'act' package (e.g., the project root).")
    print("2. The 'act' package directory (e.g., 'act_workflow/act') exists and contains '__init__.py'.")
    print("3. The 'act/nodes' directory exists and contains '__init__.py' and your node Python files.")
    print(f"Current sys.path includes: {project_root} and potentially {nodes_path}")
    exit(1)


def main():
    # --- Hardcode the Actfile Path ---
    # Use Docker-compatible path if running in container, otherwise use local path
    if os.path.exists("/app/flow"):
        actfile_path_str = "/app/flow"
    else:
        actfile_path_str = "/Users/tajnoah/Desktop/langmvp/act_workflow/flow"

    actfile_path = Path(actfile_path_str)

    print(f"Attempting to run Actfile: {actfile_path.resolve()}")
    if not actfile_path.is_file():
        print(f"Error: Actfile not found at {actfile_path.resolve()}")
        return

    # --- Initialize ExecutionManager ---
    try:
        # Optional: Check for OpenAI key if needed by the workflow
        try:
            if "openai" in actfile_path.read_text(encoding='utf-8'):
                if not os.environ.get("OPENAI_API_KEY"):
                    print("\n⚠️ WARNING: Workflow might use OpenAI, but OPENAI_API_KEY environment variable is not set.")
        except Exception as read_err:
            print(f"Warning: Could not read Actfile to check for OpenAI usage: {read_err}")

        execution_manager = ExecutionManager(str(actfile_path))

        # --- Check if this is an Agent workflow ---
        if execution_manager.has_agent_config():
            print("\n🤖 Agent Mode Detected - Starting Agent Server")
            
            # Get agent configuration
            config = execution_manager.get_agent_config()
            deployment = execution_manager.get_deployment_config()
            
            print(f"📋 Agent Name: {config.get('agent_name', 'ACT Agent')}")
            print(f"🌐 Host: {config.get('host', 'localhost')}")
            print(f"🚀 Port: {config.get('port', 8080)}")
            
            # Print usage info
            host = config.get('host', 'localhost')
            port = config.get('port', 8080)
            print(f"\n🌐 Agent Server URLs:")
            print(f"   📊 Dashboard:     http://{host}:{port}/admin/dashboard")
            print(f"   🔍 API Status:    http://{host}:{port}/api/status")
            print(f"   🚀 ACI Routes:    http://{host}:{port}/aci")
            print(f"   💚 Health Check:  http://{host}:{port}/health")
            print(f"\n🧪 Test your ACI routes:")
            print(f"   curl http://{host}:{port}/aci/users")
            print(f"   curl -X POST http://{host}:{port}/aci/users -H \"Content-Type: application/json\" -d '{{\"name\":\"John\",\"email\":\"john@example.com\"}}'")
            print(f"   curl -X POST http://{host}:{port}/aci/users/get -H \"Content-Type: application/json\" -d '{{\"user_id\":\"123\"}}'")
            print(f"\n🛑 Stop the agent: Press Ctrl+C")
            
            # Create and run agent server
            try:
                agent = AgentServer(execution_manager, config, deployment)
                agent.run()  # This will block and run the Flask server
            except KeyboardInterrupt:
                print("\n🛑 Agent stopped by user (Ctrl+C)")
            except Exception as agent_error:
                print(f"\n❌ Error running agent: {agent_error}")
                import traceback
                traceback.print_exc()
        else:
            print("\n--- Standard Workflow Mode ---")
            print("No agent configuration found - running workflow once")
            
            # --- No external input loading needed (assuming DataNode is used) ---
            print("Assuming initial data/config is provided by a 'DataNode' within the workflow.")
            initial_data = None  # Set to None as we are not passing external input

            print("\n--- Executing Workflow ---")
            # Execute without passing initial_input, assuming DataNode provides it
            result = execution_manager.execute_workflow(initial_input=initial_data)  # Pass None or {}

            print("\n--- Workflow Final Result ---")
            # Use the safe logger from the manager for potentially large/sensitive results
            print(execution_manager.log_safe_node_data(result))

    except FileNotFoundError as e:
        print(f"Error during execution setup: {e}")
    except Exception as e:
        print(f"\n--- An unexpected error occurred during execution ---")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()