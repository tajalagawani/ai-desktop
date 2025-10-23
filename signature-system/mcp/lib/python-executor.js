/**
 * Python Executor
 * Helper for spawning Python scripts from ACT mcp_utils
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Resolve paths relative to this file - works from any context
const ACT_PARENT = path.resolve(__dirname, '../../../components/apps/act-docker');
const ACT_PATH = path.join(ACT_PARENT, 'act');

// Try to find Python 3
let PYTHON_PATH = 'python3'; // Default to system python3
try {
  PYTHON_PATH = execSync('which python3', { encoding: 'utf-8' }).trim();
} catch (e) {
  // Fallback to common locations
  if (fs.existsSync('/opt/homebrew/bin/python3')) {
    PYTHON_PATH = '/opt/homebrew/bin/python3';
  } else if (fs.existsSync('/usr/local/bin/python3')) {
    PYTHON_PATH = '/usr/local/bin/python3';
  }
}

console.error(`[MCP] ACT Path: ${ACT_PATH}`);
console.error(`[MCP] PYTHONPATH: ${ACT_PARENT}`);
console.error(`[MCP] Python Path: ${PYTHON_PATH}`);

/**
 * Execute a Python script from act.mcp_utils
 *
 * @param {string} script - Script name (e.g., 'single_node_executor')
 * @param {Array<string>} args - Arguments to pass to script
 * @param {Object} options - Options
 * @returns {Promise<Object>} - Parsed JSON result
 */
export async function executePython(script, args = [], options = {}) {
  return new Promise((resolve, reject) => {
    const pythonArgs = [
      '-m',
      `act.mcp_utils.${script}`,
      ...args
    ];

    const python = spawn(PYTHON_PATH, pythonArgs, {
      cwd: ACT_PARENT,
      shell: false,  // Disable shell to avoid JSON argument parsing issues
      env: {
        PYTHONPATH: ACT_PARENT,
        PATH: '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin',
        HOME: '/Users/tajnoah'
      },
      ...options
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
      // Filter out warnings from stderr - only real errors should fail
      const errorLines = stderr.split('\n').filter(line => {
        const trimmed = line.trim();
        return trimmed !== '' &&
          !line.includes('Warning:') &&
          !line.includes('WARNING') &&
          !line.includes('RuntimeWarning') &&
          !line.includes('[PYTHON]') &&
          !line.includes('Unclosed') &&
          !line.includes('asyncio - ERROR - Unclosed') &&
          !line.includes('client_session:') &&
          !line.includes('connector:') &&
          !line.includes('connections:');
      });

      if (code !== 0 && errorLines.length > 0) {
        reject(new Error(`Python execution failed (exit ${code}): ${errorLines.join('\n')}`));
        return;
      }

      try {
        // Remove warnings from output
        const lines = stdout.split('\n');
        const jsonLines = lines.filter(line =>
          !line.startsWith('Warning:') &&
          !line.includes('not found') &&
          line.trim() !== ''
        );
        const cleanOutput = jsonLines.join('\n');

        // Try to parse JSON from stdout (match both objects {} and arrays [])
        const jsonMatch = cleanOutput.match(/[\{\[][\s\S]*[\}\]]/);
        if (jsonMatch) {
          const result = JSON.parse(jsonMatch[0]);
          resolve(result);
        } else {
          reject(new Error(`No JSON found in output: ${stdout}`));
        }
      } catch (error) {
        reject(new Error(`Failed to parse JSON: ${error.message}\nOutput: ${stdout}`));
      }
    });

    python.on('error', (error) => {
      reject(new Error(`Failed to spawn Python: ${error.message}`));
    });
  });
}

/**
 * Execute single node operation
 */
export async function executeNode(signaturePath, nodeType, operation, params, options = {}) {
  const paramsJson = JSON.stringify(params);
  const args = [signaturePath, nodeType, operation, paramsJson];

  if (options.noDefaults) {
    args.push('--no-defaults');
  }

  if (options.verbose) {
    args.push('--verbose');
  }

  return executePython('single_node_executor', args);
}

/**
 * Execute workflow
 */
export async function executeFlow(flowPath, signaturePath, params = null, verbose = false) {
  const args = [flowPath, signaturePath];

  if (params) {
    args.push(JSON.stringify(params));
  }

  if (verbose) {
    args.push('--verbose');
  }

  return executePython('execute_flow', args);
}

/**
 * Sync catalog
 */
export async function syncCatalog(outputPath = null) {
  const args = ['sync'];

  if (outputPath) {
    args.push(outputPath);
  }

  return executePython('catalog_sync', args);
}

/**
 * Get node info
 */
export async function getNodeInfo(nodeType) {
  return executePython('catalog_sync', ['get', nodeType]);
}

/**
 * List nodes
 */
export async function listNodes(category = null) {
  const args = ['list'];

  if (category) {
    args.push(category);
  }

  return executePython('catalog_sync', args);
}

/**
 * List operations for a node
 */
export async function listOperations(nodeType) {
  return executePython('list_operations', ['list', nodeType]);
}

/**
 * Search operations
 */
export async function searchOperations(query) {
  return executePython('list_operations', ['search', query]);
}

/**
 * Get operation details
 */
export async function getOperationDetails(nodeType, operation) {
  return executePython('list_operations', ['get', nodeType, operation]);
}

/**
 * Execute Python code directly (for signature management)
 * Writes code to a temp file and executes it to avoid shell escaping issues
 */
export async function executePythonCode(code) {
  return new Promise((resolve, reject) => {
    // Write Python code to a temporary file
    const tempFile = path.join(ACT_PARENT, `.temp_mcp_${Date.now()}.py`);

    try {
      fs.writeFileSync(tempFile, code, 'utf-8');
    } catch (error) {
      reject(new Error(`Failed to write temp Python file: ${error.message}`));
      return;
    }

    const python = spawn(PYTHON_PATH, [tempFile], {
      cwd: ACT_PARENT,
      env: {
        PYTHONPATH: ACT_PARENT,
        PATH: '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin',
        HOME: '/Users/tajnoah'
      }
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
      // Clean up temp file
      try {
        fs.unlinkSync(tempFile);
      } catch (e) {
        console.error(`Warning: Failed to delete temp file ${tempFile}:`, e.message);
      }

      // Filter out warnings from stderr - only real errors should fail
      const errorLines = stderr.split('\n').filter(line =>
        line.trim() !== '' &&
        !line.includes('Warning:') &&
        !line.includes('[PYTHON]')
      );

      if (code !== 0 && errorLines.length > 0) {
        reject(new Error(`Python code execution failed: ${errorLines.join('\n')}`));
        return;
      }

      try {
        const jsonMatch = stdout.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const result = JSON.parse(jsonMatch[0]);
          resolve(result);
        } else {
          // Return raw output if no JSON
          resolve({ output: stdout.trim() });
        }
      } catch (error) {
        resolve({ output: stdout.trim() });
      }
    });

    python.on('error', (error) => {
      // Clean up temp file on error
      try {
        fs.unlinkSync(tempFile);
      } catch (e) {
        // Ignore cleanup errors
      }
      reject(new Error(`Failed to spawn Python: ${error.message}`));
    });
  });
}
