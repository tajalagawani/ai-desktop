/**
 * Search Operations Tool
 * Search for operations across all nodes
 */

import { searchOperations } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

export async function searchOperationsTool(args) {
  try {
    ErrorHandler.validateParams(args, ['query']);

    const { query } = args;

    // Search operations from Python
    const result = await searchOperations(query);

    // Result is array of matches
    return ErrorHandler.success({
      query,
      total_results: result.length,
      results: result
    });

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
