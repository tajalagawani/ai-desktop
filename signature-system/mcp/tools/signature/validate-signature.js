/**
 * Validate Signature Tool
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { executePythonCode } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function validateSignature(args) {
  try {
    const {
      signature_path = 'signatures/user.act.sig'
    } = args || {};

    const sigPath = path.resolve(__dirname, '../../../', signature_path);

    const pythonCode = `
import json
import os
import toml
from act.mcp_utils import SignatureManager

signature_path = '${sigPath}'

try:
    if not os.path.exists(signature_path):
        print(json.dumps({
            "success": True,
            "valid": False,
            "errors": ["Signature file does not exist"]
        }))
        exit(0)

    # Try to load signature
    sig = SignatureManager(signature_path)
    sig.load()

    errors = []
    warnings = []

    # Validate structure
    if 'signature' not in sig.signature:
        errors.append("Missing [signature] section")

    if 'metadata' not in sig.signature:
        warnings.append("Missing [metadata] section")

    # Validate authenticated nodes
    authenticated = sig.get_authenticated_nodes()
    for node_type in authenticated:
        auth = sig.get_node_auth(node_type, resolve_env=False)
        if not auth:
            warnings.append(f"Node '{node_type}' has no auth data")

    print(json.dumps({
        "success": True,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "authenticated_nodes": len(authenticated)
    }))

except Exception as e:
    print(json.dumps({
        "success": True,
        "valid": False,
        "errors": [str(e)]
    }))
`;

    const result = await executePythonCode(pythonCode);

    return ErrorHandler.success(result);

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
