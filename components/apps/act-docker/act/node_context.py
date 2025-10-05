import os
import importlib
from typing import Dict, Any, List, Type
from dataclasses import dataclass

@dataclass
class NodeContext:
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    node_type: str
    node_name: str


class NodeDiscovery:
    @staticmethod
    def find_all_nodes(directory: str, base_package: str) -> Dict[str, Type]:
        """
        Dynamically find and load all node classes in the specified directory.

        Args:
            directory (str): The directory to search for node modules.
            base_package (str): The base package for imports (e.g., "act.nodes").

        Returns:
            Dict[str, Type]: A dictionary mapping node types to their classes.
        """
        nodes = {}
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith("_node.py"):  # Identify node modules by naming convention
                    module_name = file[:-3]  # Remove ".py"
                    node_type = module_name.replace("_node", "").capitalize()

                    # Import the module dynamically
                    module_path = f"{base_package}.{module_name}"
                    try:
                        module = importlib.import_module(module_path)
                        node_class = getattr(module, f"{node_type}Node", None)
                        if node_class:
                            nodes[node_type] = node_class
                    except Exception as e:
                        print(f"Error loading node {module_name}: {e}")

        return nodes
