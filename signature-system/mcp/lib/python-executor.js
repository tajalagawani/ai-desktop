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

// HARDCODED PATHS - Direct paths for reliability
const ACT_PATH = '/Users/tajnoah/Downloads/ai-desktop/components/apps/act-docker/act';
const ACT_PARENT = '/Users/tajnoah/Downloads/ai-desktop/components/apps/act-docker'; // For PYTHONPATH
const PYTHON_PATH = '/opt/homebrew/bin/python3';

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
      shell: true,
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
      if (code !== 0) {
        reject(new Error(`Python execution failed (exit ${code}): ${stderr}`));
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
 */
export async function executePythonCode(code) {
  return new Promise((resolve, reject) => {
    const python = spawn(PYTHON_PATH, ['-c', code], {
      cwd: ACT_PARENT,
      shell: true,
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
      if (code !== 0) {
        reject(new Error(`Python code execution failed: ${stderr}`));
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
      reject(new Error(`Failed to spawn Python: ${error.message}`));
    });
  });
}
