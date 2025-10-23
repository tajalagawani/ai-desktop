/**
 * Add Node to Signature Tool
 * Authenticates a node and adds to signature file
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { executePythonCode } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function addNodeToSignature(args) {
  try {
    ErrorHandler.validateParams(args, ['node_type', 'auth']);

    const {
      node_type,
      auth,
      defaults = {},
      operations = undefined, // Optional: specific operations to include
      signature_path = 'signatures/user.act.sig'
    } = args;

    // Validate auth data
    if (typeof auth !== 'object' || Object.keys(auth).length === 0) {
      throw Object.assign(
        new Error('auth must be a non-empty object'),
        { code: 'INVALID_AUTH_DATA' }
      );
    }

    // Resolve signature path
    const sigPath = path.resolve(__dirname, '../../../', signature_path);

    // Escape strings for Python - using base64 to avoid escaping issues
    const authJson = Buffer.from(JSON.stringify(auth)).toString('base64');
    const defaultsJson = Buffer.from(JSON.stringify(defaults)).toString('base64');
    const hasOperations = operations && operations.length > 0;
    const operationsJson = hasOperations ? Buffer.from(JSON.stringify(operations)).toString('base64') : '';

    // Python code to add node
    const pythonCode = `
import json
import os
import sys
import base64
from act.mcp_utils import SignatureManager, get_node_info

signature_path = '${sigPath}'
node_type = '${node_type}'
has_operations = ${hasOperations ? 'True' : 'False'}
auth_data = json.loads(base64.b64decode('${authJson}').decode('utf-8'))
defaults_data = json.loads(base64.b64decode('${defaultsJson}').decode('utf-8'))
selected_operations = json.loads(base64.b64decode('${operationsJson}').decode('utf-8')) if has_operations else None

print(f"[PYTHON] has_operations: {has_operations}", file=sys.stderr)
print(f"[PYTHON] selected_operations: {selected_operations}", file=sys.stderr)
print(f"[PYTHON] selected_operations type: {type(selected_operations)}", file=sys.stderr)
print(f"[PYTHON] selected_operations length: {len(selected_operations) if selected_operations else 'N/A'}", file=sys.stderr)

try:
    # Get node info from catalog to validate
    node_info = get_node_info(node_type)

    if not node_info:
        print(json.dumps({
            "success": False,
            "error": f"Node '{node_type}' not found in catalog"
        }))
        exit(0)

    # Load or create signature
    sig = SignatureManager(signature_path)

    if os.path.exists(signature_path):
        sig.load()
    else:
        # Initialize new signature
        sig.signature = {
            "signature": {
                "version": "1.0.0",
                "created_at": "${new Date().toISOString()}"
            },
            "metadata": {
                "authenticated_nodes": 0
            }
        }
        sig._loaded = True

    # Extract operations from node info
    # If specific operations selected, only include those
    operations = {}
    all_operations = node_info.get('operations', [])

    print(f"[PYTHON] all_operations count: {len(all_operations)}", file=sys.stderr)
    print(f"[PYTHON] Will filter operations: {selected_operations is not None}", file=sys.stderr)

    if selected_operations:
        # Only include selected operations
        print(f"[PYTHON] Filtering to selected operations only...", file=sys.stderr)
        for op in all_operations:
            op_name = op['name']
            is_selected = op_name in selected_operations
            print(f"[PYTHON]   - Checking '{op_name}': {is_selected}", file=sys.stderr)
            if is_selected:
                operations[op['name']] = {
                    "description": f"{op['displayName']} operation",
                    "category": op.get('category', 'other')
                }
    else:
        # Include all operations (default)
        print(f"[PYTHON] Including ALL operations (no filter)...", file=sys.stderr)
        for op in all_operations:
            operations[op['name']] = {
                "description": f"{op['displayName']} operation",
                "category": op.get('category', 'other')
            }

    print(f"[PYTHON] Final operations count: {len(operations)}", file=sys.stderr)
    print(f"[PYTHON] Final operations keys: {list(operations.keys())}", file=sys.stderr)

    # Add node to signature - Store ACTUAL credentials, not env vars
    metadata = {
        "display_name": node_info.get('displayName', node_type),
        "description": node_info.get('description', ''),
        "added_at": "${new Date().toISOString()}"
    }

    # Instead of using add_node which converts to env vars, manually add to signature
    node_key = f"node:{node_type}"
    sig.signature[node_key] = {
        "type": node_type,
        "enabled": True,
        "authenticated": True,
        **metadata
    }

    # Add auth section with ACTUAL values (not env references)
    auth_key = f"{node_key}.auth"
    sig.signature[auth_key] = auth_data

    # Add defaults section
    if defaults_data:
        defaults_key = f"{node_key}.defaults"
        sig.signature[defaults_key] = defaults_data

    # Add operations section
    if operations:
        ops_key = f"{node_key}.operations"
        sig.signature[ops_key] = operations

    # Update metadata
    if 'metadata' not in sig.signature:
        sig.signature['metadata'] = {}

    sig.signature['metadata']['authenticated_nodes'] = len(sig.get_authenticated_nodes()) + 1
    sig.signature['metadata']['last_updated'] = "${new Date().toISOString()}"

    sig._loaded = True
    sig.save()

    result = {
        "success": True,
        "node_type": node_type,
        "authenticated": True,
        "operations_count": len(operations),
        "message": f"Node '{node_type}' authenticated successfully"
    }

    print(json.dumps(result))

except Exception as e:
    import traceback
    print(json.dumps({
        "success": False,
        "error": str(e),
        "traceback": traceback.format_exc()
    }))
`;

    const result = await executePythonCode(pythonCode);

    if (!result.success) {
      throw new Error(result.error || 'Failed to add node to signature');
    }

    return ErrorHandler.success(result);

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
