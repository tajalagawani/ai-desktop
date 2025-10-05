# === File: test.py (Runner for specific Actfile) ===

import os
import sys
import json
from pathlib import Path
import argparse # Keep argparse in case you want to switch back easily

# --- Add the project root to the Python path ---
# Adjust this if test.py is located elsewhere relative to the 'act' package
script_dir = Path(__file__).parent.resolve()
# Assuming test.py is in act_workflow, and 'act' is inside act_workflow
project_root = script_dir
# If 'act' is one level up: project_root = script_dir.parent
sys.path.insert(0, str(project_root))
# -----------------------------------------------------------

try:
    # Now try importing the ExecutionManager
    from act.execution_manager import ExecutionManager
except ImportError as e:
    print(f"Error importing ExecutionManager: {e}")
    print("Please ensure:")
    print("1. You are running this script from a directory where Python can find the 'act' package (e.g., the project root).")
    print("2. The 'act' package directory exists and contains '__init__.py'.")
    print(f"Current sys.path includes: {project_root}")
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

    # --- No external input loading needed (assuming DataNode is used) ---
    print("Assuming initial data/config is provided by a 'DataNode' within the workflow.")
    initial_data = None # Set to None as we are not passing external input

    # --- Initialize and Execute ---
    try:
        # Optional: Check for OpenAI key if needed by the workflow
        try:
            if "openai" in actfile_path.read_text(encoding='utf-8'):
                 if not os.environ.get("OPENAI_API_KEY"):
                      print("\n⚠️ WARNING: Workflow might use OpenAI, but OPENAI_API_KEY environment variable is not set.")
        except Exception as read_err:
             print(f"Warning: Could not read Actfile to check for OpenAI usage: {read_err}")


        execution_manager = ExecutionManager(str(actfile_path))

        print("\n--- Executing Workflow ---")
        # Execute without passing initial_input, assuming DataNode provides it
        result = execution_manager.execute_workflow(initial_input=initial_data) # Pass None or {}

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
