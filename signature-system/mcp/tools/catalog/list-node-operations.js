/**
 * List Node Operations Tool
 * Lists all operations for a specific node
 */

import { listOperations } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

export async function listNodeOperations(args) {
  try {
    ErrorHandler.validateParams(args, ['node_type']);

    const { node_type } = args;

    // Get operations from Python
    const result = await listOperations(node_type);

    // Result should have node_type, operations, parameters, etc.
    return ErrorHandler.success(result);

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
