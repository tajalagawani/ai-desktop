/**
 * Get Signature Info Tool
 * Gets information about authenticated nodes from signature file
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { executePythonCode } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function getSignatureInfo(args) {
  try {
    const {
      signature_path = 'signatures/user.act.sig',
      node_type = null
    } = args || {};

    // Resolve signature path
    const sigPath = path.resolve(__dirname, '../../../', signature_path);

    // Python code to read signature
    const pythonCode = `
import json
import os
from act.mcp_utils import SignatureManager

signature_path = '${sigPath}'

try:
    sig = SignatureManager(signature_path)

    if not os.path.exists(signature_path):
        result = {
            "success": True,
            "exists": False,
            "authenticated_nodes": [],
            "total": 0
        }
    else:
        sig.load()
        authenticated = sig.get_authenticated_nodes()

        result = {
            "success": True,
            "exists": True,
            "authenticated_nodes": authenticated,
            "total": len(authenticated)
        }

        # Get details for specific node if requested
        node_type = '${node_type}'
        if node_type and node_type != 'null':
            if sig.is_authenticated(node_type):
                result["node"] = {
                    "type": node_type,
                    "authenticated": True,
                    "defaults": sig.get_node_defaults(node_type)
                }
            else:
                result["node"] = {
                    "type": node_type,
                    "authenticated": False
                }

    print(json.dumps(result))

except Exception as e:
    print(json.dumps({
        "success": False,
        "error": str(e)
    }))
`;

    const result = await executePythonCode(pythonCode);

    if (!result.success) {
      throw new Error(result.error || 'Failed to read signature');
    }

    return ErrorHandler.success(result);

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
