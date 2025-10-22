"""
ACT Catalog Sync

Scans ACT nodes directory and generates complete catalog.
"""

import os
import re
import json
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime


def sync_catalog(nodes_dir: Optional[str] = None, output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Sync catalog by scanning all node files

    Args:
        nodes_dir: Path to nodes directory (defaults to ../nodes relative to this file)
        output_path: Optional path to save catalog JSON

    Returns:
        Complete catalog dictionary
    """
    if nodes_dir is None:
        # Default to ../nodes relative to this file
        current_dir = Path(__file__).parent
        nodes_dir = str(current_dir.parent / 'nodes')

    if not os.path.exists(nodes_dir):
        raise FileNotFoundError(f"Nodes directory not found: {nodes_dir}")

    # Find all node files
    node_files = [f for f in os.listdir(nodes_dir) if f.endswith('Node.py')]

    nodes = []
    for node_file in node_files:
        try:
            node_path = os.path.join(nodes_dir, node_file)
            node_info = parse_node_file(node_path)
            if node_info:
                nodes.append(node_info)
        except Exception as e:
            print(f"Warning: Failed to parse {node_file}: {e}", file=sys.stderr)
            continue

    catalog = {
        'nodes': nodes,
        'total': len(nodes),
        'generated': datetime.utcnow().isoformat() + 'Z',
        'version': '2.0.0'
    }

    # Save to file if output_path provided
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(catalog, f, indent=2)

    return catalog


def parse_node_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single node file

    Args:
        file_path: Path to node Python file

    Returns:
        Node info dictionary or None if parsing failed
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(file_path)
    node_id = extract_node_id(content, filename)

    return {
        'id': node_id,
        'displayName': format_display_name(node_id),
        'description': extract_description(content),
        'operations': extract_operations(content),
        'parameters': extract_parameters(content),
        'authRequired': detect_auth_required(content),
        'authFields': extract_auth_fields(content),
        'tags': infer_tags(node_id, content),
        'sourceFile': filename
    }


def extract_node_id(content: str, filename: str) -> str:
    """Extract node ID from content or filename"""
    # Try to find node_type in code
    match = re.search(r'node_type\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)

    # Fall back to filename
    return filename.replace('Node.py', '').lower()


def extract_description(content: str) -> str:
    """Extract description from docstring"""
    # Try class docstring
    match = re.search(r'class\s+\w+Node[^:]*:\s*"""([^"]+)"""', content)
    if match:
        return match.group(1).strip().split('\n')[0]

    # Try module docstring
    match = re.search(r'^"""([^"]+)"""', content, re.MULTILINE)
    if match:
        return match.group(1).strip().split('\n')[0]

    return 'No description available'


def extract_operations(content: str) -> List[Dict[str, str]]:
    """Extract operations from OPERATIONS dict or Operation class"""
    operations = []

    # First, try to find OPERATIONS dictionary (UniversalRequestNode pattern)
    ops_dict_match = re.search(r'OPERATIONS\s*=\s*\{([\s\S]*?)(?=\n    \}\s*$|\n\n    def )', content, re.MULTILINE)

    if ops_dict_match:
        ops_block = ops_dict_match.group(1)

        # Find all operation keys in the dictionary (must have "method" field to be valid)
        for match in re.finditer(r'^\s{8}"([a-z_]+)":\s*\{[^}]*"method":', ops_block, re.MULTILINE):
            op_name = match.group(1)

            # Try to extract display_name and description for this operation
            op_content_match = re.search(
                rf'"{op_name}":\s*\{{([^}}]*?"display_name":[^}}]+)',
                ops_block,
                re.DOTALL
            )

            display_name = format_display_name(op_name)
            description = ''

            if op_content_match:
                op_content = op_content_match.group(1)

                # Extract display_name
                display_match = re.search(r'"display_name":\s*"([^"]+)"', op_content)
                if display_match:
                    display_name = display_match.group(1)

                # Extract description
                desc_match = re.search(r'"description":\s*"([^"]+)"', op_content)
                if desc_match:
                    description = desc_match.group(1)

            operations.append({
                'name': op_name,
                'displayName': display_name,
                'description': description,
                'category': infer_operation_category(op_name)
            })

    # Fallback: Find Operation class (old pattern)
    if not operations:
        op_class_match = re.search(r'class\s+\w*Operation[^:]*:([\s\S]*?)(?=\n\nclass|\nclass \w+:|$)', content)

        if op_class_match:
            op_block = op_class_match.group(1)

            # Find all operation constants
            for match in re.finditer(r'^\s*([A-Z_]+)\s*=\s*["\']([a-z_]+)["\']', op_block, re.MULTILINE):
                operations.append({
                    'name': match.group(2),
                    'displayName': format_display_name(match.group(2)),
                    'description': '',
                    'category': infer_operation_category(match.group(2))
                })

    # If still no operations found, default to 'execute'
    if not operations:
        operations.append({
            'name': 'execute',
            'displayName': 'Execute',
            'description': '',
            'category': 'execute'
        })

    return operations


def extract_parameters(content: str) -> List[Dict[str, Any]]:
    """Extract parameters from NodeParameter definitions"""
    parameters = []

    # Find all NodeParameter definitions
    for match in re.finditer(r'NodeParameter\s*\(([\s\S]*?)\)', content):
        param_block = match.group(1)

        param = {
            'name': extract_param_value(param_block, 'name'),
            'type': extract_param_type(param_block),
            'description': extract_param_value(param_block, 'description') or '',
            'required': extract_param_value(param_block, 'required') == 'True'
        }

        if param['name']:
            parameters.append(param)

    return parameters


def extract_auth_fields(content: str) -> List[Dict[str, Any]]:
    """Extract authentication field requirements"""
    auth_fields = []

    # Look for SECRET type parameters
    for match in re.finditer(r'NodeParameter\s*\(\s*name\s*=\s*["\']([^"\']+)["\'][^)]*type\s*=\s*NodeParameterType\.SECRET', content):
        field_name = match.group(1)
        param_block = content[match.start():match.start() + 500]

        desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', param_block)
        req_match = re.search(r'required\s*=\s*(True|False)', param_block)

        auth_fields.append({
            'field': field_name,
            'type': 'secret',
            'description': desc_match.group(1) if desc_match else f'{field_name} for authentication',
            'required': req_match.group(1) == 'True' if req_match else False,
            'sensitive': True
        })

    # Look for common auth parameter names
    common_auth = ['api_key', 'token', 'password', 'secret', 'credential', 'auth_token', 'access_token']
    for match in re.finditer(r'NodeParameter\s*\(\s*name\s*=\s*["\']([^"\']+)["\']', content):
        field_name = match.group(1)
        if any(auth in field_name.lower() for auth in common_auth):
            if not any(f['field'] == field_name for f in auth_fields):
                auth_fields.append({
                    'field': field_name,
                    'type': 'secret',
                    'description': f'{field_name} for authentication',
                    'required': False,
                    'sensitive': True
                })

    return auth_fields


def detect_auth_required(content: str) -> bool:
    """Detect if node requires authentication"""
    # Check for SECRET parameters
    if 'NodeParameterType.SECRET' in content:
        return True

    # Check for common auth keywords
    auth_keywords = ['api_key', 'token', 'password', 'credential', 'auth']
    return any(keyword in content.lower() for keyword in auth_keywords)


def infer_operation_category(operation: str) -> str:
    """Infer category from operation name"""
    op = operation.lower()

    if re.search(r'insert|create|add|post|save|put', op):
        return 'create'
    elif re.search(r'find|get|read|select|list|fetch|query|search', op):
        return 'read'
    elif re.search(r'update|modify|patch|replace|edit|set', op):
        return 'update'
    elif re.search(r'delete|remove|drop|destroy|clear', op):
        return 'delete'
    elif re.search(r'aggregate|group|sum|count|analyze', op):
        return 'aggregation'

    return 'other'


def infer_tags(node_id: str, content: str) -> List[str]:
    """Infer tags from node ID and content"""
    tags = set()
    id_lower = node_id.lower()

    # Database tags
    if re.search(r'mongo|postgres|mysql|redis|neo4j|sqlite', id_lower):
        tags.add('database')
    if 'sql' in id_lower:
        tags.add('sql')
    if re.search(r'mongo|redis|neo4j', id_lower):
        tags.add('nosql')

    # Service tags
    if re.search(r'api|http|request', id_lower):
        tags.add('api')
    if re.search(r'email|smtp|mail', id_lower):
        tags.add('email')
    if re.search(r'file|storage|s3', id_lower):
        tags.add('storage')
    if re.search(r'openai|anthropic|ai|gpt', id_lower):
        tags.add('ai')
    if re.search(r'github|gitlab|git', id_lower):
        tags.add('developer')

    return list(tags) if tags else ['general']


def extract_param_value(param_block: str, key: str) -> Optional[str]:
    """Extract parameter value by key"""
    match = re.search(f'{key}\\s*=\\s*["\']([^"\']+)["\']', param_block)
    return match.group(1) if match else None


def extract_param_type(param_block: str) -> str:
    """Extract parameter type"""
    match = re.search(r'type\s*=\s*NodeParameterType\.(\w+)', param_block)
    return match.group(1).lower() if match else 'string'


def format_display_name(name: str) -> str:
    """Format name for display (snake_case to Title Case)"""
    return ' '.join(word.capitalize() for word in name.split('_'))


def get_node_info(node_type: str, nodes_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get detailed info for a specific node

    Args:
        node_type: Node type (e.g., "github")
        nodes_dir: Path to nodes directory

    Returns:
        Node info dictionary or None if not found
    """
    catalog = sync_catalog(nodes_dir)

    for node in catalog['nodes']:
        if node['id'].lower() == node_type.lower():
            return node

    return None


def list_all_nodes(nodes_dir: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all available nodes

    Args:
        nodes_dir: Path to nodes directory
        category: Optional category filter

    Returns:
        List of node info dictionaries
    """
    catalog = sync_catalog(nodes_dir)
    nodes = catalog['nodes']

    if category:
        nodes = [n for n in nodes if category in n.get('tags', [])]

    return nodes


# CLI entry point
if __name__ == '__main__':
    import sys
    from datetime import datetime

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'sync':
            output = sys.argv[2] if len(sys.argv) > 2 else None
            catalog = sync_catalog(output_path=output)
            print(json.dumps(catalog, indent=2))

        elif command == 'get':
            if len(sys.argv) < 3:
                print('Usage: catalog_sync.py get <node_type>')
                sys.exit(1)
            node_info = get_node_info(sys.argv[2])
            print(json.dumps(node_info, indent=2))

        elif command == 'list':
            category = sys.argv[2] if len(sys.argv) > 2 else None
            nodes = list_all_nodes(category=category)
            print(json.dumps(nodes, indent=2))

    else:
        print('Usage: catalog_sync.py [sync|get|list] [args...]')
        sys.exit(1)
