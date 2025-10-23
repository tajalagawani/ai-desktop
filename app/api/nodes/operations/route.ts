import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

const MCP_INDEX = path.join(process.cwd(), 'signature-system/mcp/index.js');
const ACT_PARENT = path.join(process.cwd(), 'components/apps/act-docker');

/**
 * Execute MCP tool via CLI
 */
async function executeMCPTool(toolName: string, params: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const child = spawn('node', [MCP_INDEX, toolName, JSON.stringify(params)], {
      cwd: ACT_PARENT,
      env: {
        ...process.env,
        PYTHONPATH: ACT_PARENT,
        NODE_ENV: 'production',
      },
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    child.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          reject(new Error(`Failed to parse MCP output: ${stdout}`));
        }
      } else {
        reject(new Error(`MCP tool failed: ${stderr}`));
      }
    });

    child.on('error', reject);
  });
}

/**
 * GET /api/nodes/operations?node_type=github
 * Get all operations for a specific node type using MCP
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const nodeType = searchParams.get('node_type');

    if (!nodeType) {
      return NextResponse.json(
        { error: 'Missing node_type parameter' },
        { status: 400 }
      );
    }

    // Use MCP tool to list operations for this node
    const result = await executeMCPTool('list_node_operations', {
      node_type: nodeType
    });

    return NextResponse.json(result);
  } catch (error: any) {
    console.error('[Node Operations API] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to get operations' },
      { status: 500 }
    );
  }
}
