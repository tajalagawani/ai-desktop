/**
 * List Available Nodes Tool
 * Lists all available nodes from catalog
 */

import { listNodes } from '../../lib/python-executor.js';
import { ErrorHandler } from '../../lib/error-handler.js';

export async function listAvailableNodes(args) {
  try {
    const {
      category = null,
      authenticated_only = false,
      signature_path = 'signatures/user.act.sig'
    } = args || {};

    // Get all nodes from catalog
    const result = await listNodes(category);

    // Result is an array directly
    let nodes = Array.isArray(result) ? result : (result.nodes || result);

    if (!Array.isArray(nodes) || nodes.length === 0) {
      throw new Error('Failed to load node catalog');
    }

    // Convert to proper format
    if (Array.isArray(nodes)) {
      nodes = nodes.map(n => ({
        type: n.id || n.type,
        display_name: n.displayName || n.display_name,
        category: n.tags?.[0] || n.category || 'unknown',
        description: n.description,
        authenticated: false,
        requires_auth: n.authRequired || n.requires_auth
      }));
    }

    // TODO: If authenticated_only, filter by signature

    return ErrorHandler.success({
      total_nodes: nodes.length,
      nodes,
      categories: [...new Set(nodes.map(n => n.category))].filter(Boolean)
    });

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
