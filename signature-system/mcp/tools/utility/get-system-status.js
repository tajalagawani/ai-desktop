/**
 * Get System Status Tool
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { spawn, execSync } from 'child_process';
import { ErrorHandler } from '../../lib/error-handler.js';
import fs from 'fs/promises';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Get Python path
let PYTHON_PATH = 'python3';
try {
  PYTHON_PATH = execSync('which python3', { encoding: 'utf-8' }).trim();
} catch (error) {
  PYTHON_PATH = '/opt/homebrew/bin/python3'; // Fallback for macOS Homebrew
}

export async function getSystemStatus(args) {
  try {
    const {
      signature_path = 'signatures/user.act.sig'
    } = args || {};

    const sigPath = path.resolve(__dirname, '../../../', signature_path);

    // Check Python availability
    const pythonAvailable = await checkPython();

    // Check ACT library
    const actAvailable = await checkACT();

    // Check signature file
    let signatureStatus = {
      exists: false,
      authenticated_nodes: 0,
      last_updated: null
    };

    try {
      const stats = await fs.stat(sigPath);
      signatureStatus.exists = true;
      signatureStatus.last_updated = stats.mtime.toISOString();

      // Try to count authenticated nodes
      const content = await fs.readFile(sigPath, 'utf-8');
      const nodeMatches = content.match(/\[node:/g);
      signatureStatus.authenticated_nodes = nodeMatches ? nodeMatches.length : 0;
    } catch (error) {
      // File doesn't exist
    }

    return ErrorHandler.success({
      mcp_server: {
        version: '1.0.0',
        status: 'healthy'
      },
      python: {
        available: pythonAvailable.available,
        version: pythonAvailable.version
      },
      act_library: {
        available: actAvailable.available,
        path: actAvailable.path
      },
      signature: signatureStatus
    });

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}

async function checkPython() {
  return new Promise((resolve) => {
    const python = spawn(PYTHON_PATH, ['--version']);
    let output = '';

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0) {
        resolve({ available: true, version: output.trim() });
      } else {
        resolve({ available: false });
      }
    });

    python.on('error', () => {
      resolve({ available: false });
    });

    setTimeout(() => {
      python.kill();
      resolve({ available: false });
    }, 2000);
  });
}

async function checkACT() {
  return new Promise((resolve) => {
    const actPath = path.resolve(__dirname, '../../../../components/apps/act-docker/act');

    const python = spawn(PYTHON_PATH, ['-c', 'import sys; sys.path.insert(0, "' + actPath + '"); from act.mcp_utils import SignatureManager; print("OK")']);
    let output = '';

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0 && output.includes('OK')) {
        resolve({ available: true, path: actPath });
      } else {
        resolve({ available: false, path: actPath });
      }
    });

    python.on('error', () => {
      resolve({ available: false, path: actPath });
    });

    setTimeout(() => {
      python.kill();
      resolve({ available: false, path: actPath });
    }, 3000);
  });
}
