// API Route: /api/mcp/[id]/execute
// Execute a tool from an MCP server

import { NextRequest, NextResponse } from 'next/server';
import { getRegistry } from '@/lib/mcp-hub/registry';
import { executeTool } from '@/lib/mcp-hub/mcp-client';

const registry = getRegistry();

// POST /api/mcp/[id]/execute - Execute a tool
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const body = await request.json();
    const { toolName, parameters } = body;

    if (!toolName) {
      return NextResponse.json(
        { success: false, error: 'Tool name is required' },
        { status: 400 }
      );
    }

    const server = registry.getServer(id);

    if (!server) {
      return NextResponse.json(
        { success: false, error: 'Server not found' },
        { status: 404 }
      );
    }

    console.log(`[API MCP Execute] Executing tool ${toolName} on ${id}...`);

    const startTime = Date.now();
    const result = await executeTool(server, toolName, parameters || {});
    const duration = Date.now() - startTime;

    return NextResponse.json({
      success: true,
      result,
      duration,
      executedAt: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error('[API MCP Execute] Error:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
