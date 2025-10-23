import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

const MCP_INDEX = path.join(process.cwd(), 'signature-system/mcp/index.js');
const ACT_PARENT = path.join(process.cwd(), 'components/apps/act-docker');

/**
 * Execute MCP tool via CLI
 */
async function executeMCPTool(toolName: string, params: any): Promise<any> {
  console.log('[MCP] Calling tool:', toolName);
  if (params.operations) {
    console.log('[MCP] Operations param:', params.operations);
  }

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
          if (result.operations_count !== undefined) {
            console.log('[MCP] Result operations_count:', result.operations_count);
          }
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
 * GET /api/signature - Get signature info
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const nodeType = searchParams.get('node_type');

    const result = await executeMCPTool('get_signature_info', {
      node_type: nodeType || undefined,
      signature_path: 'signatures/user.act.sig'
    });

    return NextResponse.json(result);
  } catch (error: any) {
    console.error('[Signature API] Error:', error);
    return NextResponse.json(
      {
        status: 'error',
        error: error.message || 'Failed to get signature info'
      },
      { status: 500 }
    );
  }
}

/**
 * POST /api/signature - Add or update node
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { node_type, auth, defaults = {}, operations } = body;

    console.log('[API POST /api/signature]', node_type, operations ? `with ${operations.length} operations` : 'with all operations');

    if (!node_type || !auth) {
      return NextResponse.json(
        {
          status: 'error',
          error: 'Missing required fields: node_type and auth'
        },
        { status: 400 }
      );
    }

    const result = await executeMCPTool('add_node_to_signature', {
      node_type,
      auth,
      defaults,
      operations, // ← Pass operations to MCP tool
      signature_path: 'signatures/user.act.sig'
    });

    return NextResponse.json(result);
  } catch (error: any) {
    console.error('[API /signature POST] Error:', error.message);
    return NextResponse.json(
      {
        status: 'error',
        error: error.message || 'Failed to add node to signature'
      },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/signature - Remove node
 */
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const node_type = searchParams.get('node_type');

    if (!node_type) {
      return NextResponse.json(
        {
          status: 'error',
          error: 'Missing required parameter: node_type'
        },
        { status: 400 }
      );
    }

    const result = await executeMCPTool('remove_node_from_signature', {
      node_type,
      signature_path: 'signatures/user.act.sig'
    });

    return NextResponse.json(result);
  } catch (error: any) {
    console.error('[Signature API] Error removing node:', error);
    return NextResponse.json(
      {
        status: 'error',
        error: error.message || 'Failed to remove node from signature'
      },
      { status: 500 }
    );
  }
}
