/**
 * Update Node Defaults Tool
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { executePythonCode } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function updateNodeDefaults(args) {
  try {
    ErrorHandler.validateParams(args, ['node_type', 'defaults']);

    const {
      node_type,
      defaults,
      signature_path = 'signatures/user.act.sig'
    } = args;

    const sigPath = path.resolve(__dirname, '../../../', signature_path);
    const defaultsJson = JSON.stringify(defaults).replace(/'/g, "\\\\'");

    const pythonCode = `
import json
import os
from act.mcp_utils import SignatureManager

signature_path = '${sigPath}'
node_type = '${node_type}'
defaults_data = json.loads('${defaultsJson}')

try:
    sig = SignatureManager(signature_path)
    sig.load()

    sig.update_defaults(node_type, defaults_data)
    sig.save()

    print(json.dumps({
        "success": True,
        "node_type": node_type,
        "defaults": defaults_data,
        "message": "Defaults updated successfully"
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
