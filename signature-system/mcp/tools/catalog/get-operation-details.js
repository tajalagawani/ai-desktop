/**
 * Get Operation Details Tool
 * Get detailed information about a specific operation
 */

import { getOperationDetails } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

export async function getOperationDetailsTool(args) {
  try {
    ErrorHandler.validateParams(args, ['node_type', 'operation']);

    const { node_type, operation } = args;

    // Get operation details from Python
    const result = await getOperationDetails(node_type, operation);

    return ErrorHandler.success(result);

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
