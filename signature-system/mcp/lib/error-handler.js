/**
 * Error Handler
 * Standardized error handling for MCP server
 */

export class ErrorHandler {
  /**
   * Format error for MCP response
   */
  static format(error) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          status: 'error',
          code: error.code || 'UNKNOWN_ERROR',
          message: error.message || 'An unknown error occurred',
          help: error.help,
          available_options: error.available,
          timestamp: new Date().toISOString()
        }, null, 2)
      }]
    };
  }

  /**
   * Handle common errors and convert to user-friendly messages
   */
  static handle(error) {
    // File not found
    if (error.code === 'ENOENT') {
      return this.format({
        code: 'FILE_NOT_FOUND',
        message: error.message || 'File not found',
        help: 'Ensure the signature file exists or run initialization'
      });
    }

    // TOML parse error
    if (error.message?.includes('TOML') || error.message?.includes('parse')) {
      return this.format({
        code: 'INVALID_SIGNATURE',
        message: 'Signature file has invalid syntax',
        help: 'Validate signature using: validate_signature tool'
      });
    }

    // Node not authenticated
    if (error.message?.includes('not authenticated')) {
      return this.format({
        code: 'NODE_NOT_AUTHENTICATED',
        message: error.message,
        help: 'Authenticate the node using: add_node_to_signature tool'
      });
    }

    // Operation not found
    if (error.message?.includes('Operation') && error.message?.includes('not found')) {
      return this.format({
        code: 'OPERATION_NOT_FOUND',
        message: error.message,
        help: 'List available operations using: get_node_info tool'
      });
    }

    // Network errors
    if (error.code === 'ECONNREFUSED' || error.message?.includes('connect')) {
      return this.format({
        code: 'API_CONNECTION_ERROR',
        message: 'Failed to connect to backend API',
        help: 'Ensure the Flow Architect backend is running on http://localhost:3000'
      });
    }

    // Timeout errors
    if (error.code === 'ETIMEDOUT' || error.message?.includes('timeout')) {
      return this.format({
        code: 'API_TIMEOUT',
        message: 'API request timed out',
        help: 'The operation took too long. Try again or check backend logs.'
      });
    }

    // Permission errors
    if (error.code === 'EACCES' || error.code === 'EPERM') {
      return this.format({
        code: 'PERMISSION_DENIED',
        message: 'Permission denied',
        help: 'Check file permissions for signature file and .env'
      });
    }

    // Generic error
    return this.format({
      code: 'UNKNOWN_ERROR',
      message: error.message || String(error),
      stack: error.stack
    });
  }

  /**
   * Create success response
   */
  static success(data) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          status: 'success',
          ...data,
          timestamp: new Date().toISOString()
        }, null, 2)
      }]
    };
  }

  /**
   * Validate required parameters
   */
  static validateParams(params, required) {
    const missing = required.filter(param => !(param in params));

    if (missing.length > 0) {
      throw Object.assign(
        new Error(`Missing required parameters: ${missing.join(', ')}`),
        { code: 'MISSING_PARAMETERS', missing }
      );
    }
  }
}
