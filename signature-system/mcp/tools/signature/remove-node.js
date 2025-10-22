/**
 * Remove Node from Signature Tool
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { executePythonCode } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function removeNodeFromSignature(args) {
  try {
    ErrorHandler.validateParams(args, ['node_type']);

    const {
      node_type,
      signature_path = 'signatures/user.act.sig'
    } = args;

    const sigPath = path.resolve(__dirname, '../../../', signature_path);

    const pythonCode = `
import json
import os
from act.mcp_utils import SignatureManager

signature_path = '${sigPath}'
node_type = '${node_type}'

try:
    if not os.path.exists(signature_path):
        print(json.dumps({
            "success": False,
            "error": "Signature file does not exist"
        }))
        exit(0)

    sig = SignatureManager(signature_path)
    sig.load()

    if not sig.is_authenticated(node_type):
        print(json.dumps({
            "success": False,
            "error": f"Node '{node_type}' is not authenticated"
        }))
        exit(0)

    sig.remove_node(node_type)
    sig.save()

    print(json.dumps({
        "success": True,
        "node_type": node_type,
        "message": f"Node '{node_type}' removed successfully"
    }))

except Exception as e:
    print(json.dumps({
        "success": False,
        "error": str(e)
    }))
`;

    const result = await executePythonCode(pythonCode);

    if (!result.success) {
      throw new Error(result.error);
    }

    return ErrorHandler.success(result);

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
