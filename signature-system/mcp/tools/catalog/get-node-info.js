/**
 * Get Node Info Tool
 * Gets detailed information about a specific node
 */

import { getNodeInfo } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

export async function getNodeInfoTool(args) {
  try {
    ErrorHandler.validateParams(args, ['node_type']);

    const { node_type } = args;

    // Get node info from catalog
    const result = await getNodeInfo(node_type);

    if (!result || (result.success === false)) {
      throw Object.assign(
        new Error(`Node '${node_type}' not found in catalog`),
        { code: 'NODE_NOT_FOUND' }
      );
    }

    return ErrorHandler.success(result);

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}

// Export with different name to avoid conflict
export { getNodeInfoTool as getNodeInfo };
