/**
 * Validate Parameters Tool
 */

import { getOperationDetails } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

export async function validateParams(args) {
  try {
    ErrorHandler.validateParams(args, ['node_type', 'operation', 'params']);

    const {
      node_type,
      operation,
      params
    } = args;

    // Get operation details from catalog
    const opDetails = await getOperationDetails(node_type, operation);

    if (!opDetails || opDetails.success === false) {
      throw new Error(`Operation '${operation}' not found for node '${node_type}'`);
    }

    // Validate parameters
    const requiredParams = (opDetails.parameters || [])
      .filter(p => p.required)
      .map(p => p.name);

    const providedParams = Object.keys(params);
    const missingParams = requiredParams.filter(p => !providedParams.includes(p));

    const valid = missingParams.length === 0;

    return ErrorHandler.success({
      valid,
      required_params: requiredParams,
      provided_params: providedParams,
      missing_params: missingParams,
      node_type,
      operation
    });

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
