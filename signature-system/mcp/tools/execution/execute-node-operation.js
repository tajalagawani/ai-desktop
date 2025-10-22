/**
 * Execute Node Operation Tool
 * Executes single node operations using signature - spawns Python directly
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import { SignatureManager } from '../../lib/signature-manager.js';
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

    // Load signature to verify authentication
    const sigPath = path.resolve(__dirname, '../../../', signature_path);
    const sigManager = new SignatureManager(sigPath);
    await sigManager.load();

    if (!sigManager.isAuthenticated(node_type)) {
      throw Object.assign(
        new Error(`Node '${node_type}' is not authenticated`),
        {
          code: 'NODE_NOT_AUTHENTICATED',
          help: 'Authenticate the node using: add_node_to_signature tool'
        }
      );
    }

    // Verify operation exists
    const operations = sigManager.getOperations(node_type);
    if (!operations[operation]) {
      throw Object.assign(
        new Error(`Operation '${operation}' not found for '${node_type}'`),
        {
          code: 'OPERATION_NOT_FOUND',
          available: Object.keys(operations),
          help: 'List available operations using: get_node_info tool'
        }
      );
    }

    // Execute via Python script
    const result = await executePythonScript(
      sigPath,
      node_type,
      operation,
      params,
      override_defaults
    );

    return ErrorHandler.success({
      node_type,
      operation,
      result: result.result,
      execution_time: result.execution_time || 'N/A'
    });

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}

/**
 * Execute Python single node executor script
 */
function executePythonScript(signaturePath, nodeType, operation, params, overrideDefaults) {
  return new Promise((resolve, reject) => {
    // Path to Python executor
    const pythonScript = path.resolve(
      __dirname,
      '../../../../parser/single_node_executor.py'
    );

    // Prepare arguments
    const args = [
      pythonScript,
      signaturePath,
      nodeType,
      operation,
      JSON.stringify(params)
    ];

    // Spawn Python process
    const python = spawn('python3', args, {
      cwd: path.dirname(pythonScript),
      env: process.env
    });

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        // Try to parse error message from stdout
        try {
          const errorData = JSON.parse(stdout);
          if (errorData.status === 'error') {
            reject(new Error(errorData.error));
            return;
          }
        } catch (e) {
          // Not JSON, use stderr
        }

        reject(new Error(`Python execution failed: ${stderr || stdout}`));
        return;
      }

      // Parse result
      try {
        const result = JSON.parse(stdout);
        if (result.status === 'error') {
          reject(new Error(result.error));
        } else {
          resolve(result);
        }
      } catch (error) {
        reject(new Error(`Failed to parse Python output: ${error.message}`));
      }
    });

    python.on('error', (error) => {
      reject(new Error(`Failed to spawn Python process: ${error.message}`));
    });
  });
}
