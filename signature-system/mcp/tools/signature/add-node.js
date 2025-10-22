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

    // Escape strings for Python
    const authJson = JSON.stringify(auth).replace(/'/g, "\\\\'");
    const defaultsJson = JSON.stringify(defaults).replace(/'/g, "\\\\'");

    // Python code to add node
    const pythonCode = `
import json
import os
from act.mcp_utils import SignatureManager, get_node_info

signature_path = '${sigPath}'
node_type = '${node_type}'
auth_data = json.loads('${authJson}')
defaults_data = json.loads('${defaultsJson}')

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
    operations = {}
    for op in node_info.get('operations', []):
        operations[op['name']] = {
            "description": f"{op['displayName']} operation",
            "category": op.get('category', 'other')
        }

    # Add node to signature
    metadata = {
        "display_name": node_info.get('displayName', node_type),
        "description": node_info.get('description', ''),
        "added_at": "${new Date().toISOString()}"
    }

    sig.add_node(node_type, auth_data, defaults_data, operations, metadata)
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
