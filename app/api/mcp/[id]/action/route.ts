// API Route: /api/mcp/[id]/action
// Handles MCP server lifecycle actions (start/stop/restart)

import { NextRequest, NextResponse } from 'next/server';
import { getManager } from '@/lib/mcp-hub/manager';

const manager = getManager();

// POST /api/mcp/[id]/action - Execute server action
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const body = await request.json();
    const { action } = body;

    if (!action) {
      return NextResponse.json(
        { success: false, error: 'Action is required' },
        { status: 400 }
      );
    }

    let result;

    switch (action) {
      case 'start':
        result = await manager.startServer(id);
        break;

      case 'stop':
        result = await manager.stopServer(id);
        break;

      case 'restart':
        result = await manager.restartServer(id);
        break;

      default:
        return NextResponse.json(
          { success: false, error: `Unknown action: ${action}` },
          { status: 400 }
        );
    }

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
    console.error('[API MCP Action] Error:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
