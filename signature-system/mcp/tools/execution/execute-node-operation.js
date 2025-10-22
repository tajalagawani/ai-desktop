/**
 * Execute Node Operation Tool
 * Executes single node operations using signature - spawns Python from ACT mcp_utils
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { executeNode } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function executeNodeOperation(args) {
  try {
    // Validate required parameters
    ErrorHandler.validateParams(args, ['node_type', 'operation']);

    const {
      node_type,
      operation,
      params = {},
      override_defaults = false,
      signature_path = 'signatures/user.act.sig'
    } = args;

    // Resolve signature path
    const sigPath = path.resolve(__dirname, '../../../', signature_path);

    // Execute via Python (act.mcp_utils.single_node_executor)
    const result = await executeNode(sigPath, node_type, operation, params, {
      noDefaults: override_defaults,
      verbose: false
    });

    // Check if Python returned an error
    if (!result.success) {
      throw Object.assign(
        new Error(result.error || 'Execution failed'),
        {
          code: result.code || 'EXECUTION_ERROR',
          help: result.help
        }
      );
    }

    return ErrorHandler.success({
      node_type: result.result?.node_type || node_type,
      operation: result.result?.operation || operation,
      result: result.result?.result || result.result,
      duration: result.duration,
      timestamp: result.timestamp
    });

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
