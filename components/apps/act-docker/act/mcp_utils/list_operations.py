"""
ACT Operations Lister

List all available operations for nodes with their parameters and descriptions.
"""

import sys
import json
import importlib
from typing import Dict, List, Any, Optional

# Import catalog sync
from .catalog_sync import sync_catalog, get_node_info


def list_node_operations(node_type: str) -> Dict[str, Any]:
    """
    List all operations for a specific node

    Args:
        node_type: Node type (e.g., "github")

    Returns:
        Dictionary with operations, parameters, and metadata
    """
    # Get node info from catalog
    node_info = get_node_info(node_type)

    if not node_info:
        raise ValueError(f"Node '{node_type}' not found")

    return {
        "node_type": node_type,
        "display_name": node_info['displayName'],
        "description": node_info['description'],
        "operations": node_info['operations'],
        "parameters": node_info['parameters'],
        "auth_required": node_info['authRequired'],
        "auth_fields": node_info['authFields'],
        "tags": node_info['tags']
    }


def list_all_operations(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List operations for all nodes

    Args:
        category: Optional category filter (e.g., "database", "api")

    Returns:
        List of node operation dictionaries
    """
    catalog = sync_catalog()
    nodes = catalog['nodes']

    if category:
        nodes = [n for n in nodes if category in n.get('tags', [])]

    result = []
    for node in nodes:
        result.append({
            "node_type": node['id'],
            "display_name": node['displayName'],
            "operations_count": len(node['operations']),
            "operations": node['operations'],
            "auth_required": node['authRequired'],
            "tags": node['tags']
        })

    return result


def search_operations(query: str) -> List[Dict[str, Any]]:
    """
    Search for operations matching query

    Args:
        query: Search query (searches in node names, operation names, descriptions)

    Returns:
        List of matching operations
    """
    catalog = sync_catalog()
    query_lower = query.lower()
    results = []

    for node in catalog['nodes']:
        # Check if node matches
        node_matches = (
            query_lower in node['id'].lower() or
            query_lower in node['displayName'].lower() or
            query_lower in node['description'].lower()
        )

        # Check if any operation matches
        matching_ops = [
            op for op in node['operations']
            if query_lower in op['name'].lower() or query_lower in op['displayName'].lower()
        ]

        if node_matches or matching_ops:
            results.append({
                "node_type": node['id'],
                "display_name": node['displayName'],
                "description": node['description'],
                "operations": matching_ops if matching_ops else node['operations'],
                "auth_required": node['authRequired'],
                "tags": node['tags']
            })

    return results


def get_operation_details(node_type: str, operation: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific operation including all parameters,
    method, endpoint, examples, etc. by parsing the OPERATIONS dictionary directly.

    Args:
        node_type: Node type (e.g., "github")
        operation: Operation name (e.g., "get_repo")

    Returns:
        Detailed operation information with all metadata
    """
    # Get node info
    node_info = get_node_info(node_type)

    if not node_info:
        raise ValueError(f"Node '{node_type}' not found")

    # Load the node file to parse OPERATIONS dictionary
    from pathlib import Path
    import re

    # Find the node file
    nodes_dir = Path(__file__).parent.parent / 'nodes'
    node_file = nodes_dir / f"{node_type.capitalize()}Node.py"

    if not node_file.exists():
        # Try other capitalization patterns
        for f in nodes_dir.glob("*Node.py"):
            if f.stem.lower().replace('node', '') == node_type.lower():
                node_file = f
                break

    if not node_file.exists():
        raise ValueError(f"Node file not found for '{node_type}'")

    # Read and parse the file
    content = node_file.read_text()

    # Find OPERATIONS dictionary
    ops_dict_match = re.search(r'OPERATIONS\s*=\s*\{([\s\S]*?)(?=\n    \}\s*$|\n\n    def )', content, re.MULTILINE)

    if not ops_dict_match:
        raise ValueError(f"OPERATIONS dictionary not found in {node_file.name}")

    ops_block = ops_dict_match.group(1)

    # Find the specific operation
    op_pattern = rf'"{operation}":\s*\{{([\s\S]*?)(?=\n        \}},|\n        \}}\n    \}})'
    op_match = re.search(op_pattern, ops_block)

    if not op_match:
        raise ValueError(f"Operation '{operation}' not found in OPERATIONS dictionary")

    op_content = op_match.group(1)

    # Extract all fields
    def extract_field(field_name: str, default=None):
        """Extract a field value from operation content"""
        # Try string value
        match = re.search(rf'"{field_name}":\s*"([^"]*)"', op_content)
        if match:
            return match.group(1)
        # Try array value
        match = re.search(rf'"{field_name}":\s*\[([\s\S]*?)\]', op_content)
        if match:
            items_str = match.group(1)
            items = re.findall(r'"([^"]+)"', items_str)
            return items
        # Try number
        match = re.search(rf'"{field_name}":\s*(\d+)', op_content)
        if match:
            return int(match.group(1))
        return default

    # Extract examples
    examples = []
    examples_match = re.search(r'"examples":\s*\[([\s\S]*?)\]', op_content)
    if examples_match:
        examples_str = examples_match.group(1)
        for ex_match in re.finditer(r'\{([\s\S]*?)\}', examples_str):
            ex_content = ex_match.group(1)
            name_match = re.search(r'"name":\s*"([^"]+)"', ex_content)
            input_match = re.search(r'"input":\s*\{([\s\S]*?)\}', ex_content)
            if name_match and input_match:
                input_str = input_match.group(1)
                input_dict = {}
                for param_match in re.finditer(r'"([^"]+)":\s*"([^"]*)"', input_str):
                    input_dict[param_match.group(1)] = param_match.group(2)
                examples.append({
                    "name": name_match.group(1),
                    "input": input_dict
                })

    return {
        "node_type": node_type,
        "operation": operation,
        "display_name": extract_field("display_name", operation.replace('_', ' ').title()),
        "description": extract_field("description", ""),
        "method": extract_field("method", ""),
        "endpoint": extract_field("endpoint", ""),
        "group": extract_field("group", "General"),
        "required_params": extract_field("required_params", []),
        "optional_params": extract_field("optional_params", []),
        "body_parameters": extract_field("body_parameters", []),
        "response_type": extract_field("response_type", "object"),
        "rate_limit_cost": extract_field("rate_limit_cost", 1),
        "cache_ttl": extract_field("cache_ttl"),
        "examples": examples,
        "auth_required": True if node_info.get('authRequired') else False
    }


def generate_example(node_type: str, operation: str, parameters: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generate example usage for an operation"""

    # TOML example
    toml_lines = [
        f"[node:{node_type}]",
        f"type = {node_type}",
        f"operation = {operation}"
    ]

    # Add required parameters
    required_params = [p for p in parameters if p.get('required', False)]
    for param in required_params[:3]:  # Show max 3 params
        if param['type'] == 'string':
            toml_lines.append(f"{param['name']} = \"example_value\"")
        elif param['type'] == 'number':
            toml_lines.append(f"{param['name']} = 100")
        elif param['type'] == 'boolean':
            toml_lines.append(f"{param['name']} = true")

    # Python example
    python_example = f"""from act.mcp_utils import execute_single_node

result = execute_single_node(
    signature_path='~/.act.sig',
    node_type='{node_type}',
    operation='{operation}',
    params={{}}
)"""

    return {
        "toml": "\n".join(toml_lines),
        "python": python_example
    }


# CLI entry point
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: list_operations.py [list|search|get] [args...]')
        print('  list <node_type>           - List operations for a node')
        print('  list --all [category]      - List all nodes')
        print('  search <query>             - Search for operations')
        print('  get <node_type> <operation> - Get operation details')
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == 'list':
            if len(sys.argv) < 3:
                print('Error: node_type required')
                sys.exit(1)

            if sys.argv[2] == '--all':
                category = sys.argv[3] if len(sys.argv) > 3 else None
                result = list_all_operations(category)
            else:
                result = list_node_operations(sys.argv[2])

            print(json.dumps(result, indent=2))

        elif command == 'search':
            if len(sys.argv) < 3:
                print('Error: query required')
                sys.exit(1)

            result = search_operations(sys.argv[2])
            print(json.dumps(result, indent=2))

        elif command == 'get':
            if len(sys.argv) < 4:
                print('Error: node_type and operation required')
                sys.exit(1)

            result = get_operation_details(sys.argv[2], sys.argv[3])
            print(json.dumps(result, indent=2))

        else:
            print(f'Unknown command: {command}')
            sys.exit(1)

    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }))
        sys.exit(1)
