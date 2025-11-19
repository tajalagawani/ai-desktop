// API Route: /api/mcp/[id]
// Handles getting, updating, and deleting individual MCP servers

import { NextRequest, NextResponse } from 'next/server';
import { getRegistry } from '@/lib/mcp-hub/registry';
import { getManager } from '@/lib/mcp-hub/manager';

const registry = getRegistry();
const manager = getManager();

// GET /api/mcp/[id] - Get single MCP server
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

    // Sync status with PM2
    const status = await manager.getServerStatus(id);
    if (status !== server.status) {
      registry.updateServer(id, { status });
    }

    return NextResponse.json({
      success: true,
      server: registry.getServer(id),
    });
  } catch (error: any) {
    console.error('[API MCP GET] Error:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// PATCH /api/mcp/[id] - Update MCP server
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const body = await request.json();

    const server = registry.getServer(id);
    if (!server) {
      return NextResponse.json(
        { success: false, error: 'Server not found' },
        { status: 404 }
      );
    }

    // Don't allow updating certain fields for built-in servers
    if (server.type === 'built-in') {
      const allowedFields = ['env', 'status'];
      const updates = Object.keys(body);
      const disallowedUpdates = updates.filter((key) => !allowedFields.includes(key));

      if (disallowedUpdates.length > 0) {
        return NextResponse.json(
          {
            success: false,
            error: `Cannot update fields for built-in servers: ${disallowedUpdates.join(', ')}`,
          },
          { status: 400 }
        );
      }
    }

    const updatedServer = registry.updateServer(id, body);

    return NextResponse.json({
      success: true,
      server: updatedServer,
    });
  } catch (error: any) {
    console.error('[API MCP PATCH] Error:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// DELETE /api/mcp/[id] - Delete MCP server
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;

    const result = await manager.deleteServer(id);

    if (!result.success) {
      return NextResponse.json(
        { success: false, error: result.message },
        { status: 400 }
      );
    }

    return NextResponse.json({
      success: true,
      message: result.message,
    });
  } catch (error: any) {
    console.error('[API MCP DELETE] Error:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
