// API Route: /api/mcp/[id]/tools
// List tools available from an MCP server

import { NextRequest, NextResponse } from 'next/server';
import { getRegistry } from '@/lib/mcp-hub/registry';
import { discoverTools } from '@/lib/mcp-hub/mcp-client';

const registry = getRegistry();

// GET /api/mcp/[id]/tools - List tools from MCP server
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const server = registry.getServer(id);

    if (!server) {
      return NextResponse.json(
        { success: false, error: 'Server not found' },
        { status: 404 }
      );
    }

    console.log(`[API MCP Tools] Discovering tools for ${id}...`);

    const tools = await discoverTools(server);

    // Update tool count in registry
    registry.updateServer(id, { toolCount: tools.length });

    return NextResponse.json({
      success: true,
      tools,
      count: tools.length,
    });
  } catch (error: any) {
    console.error('[API MCP Tools] Error:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
