// API Route: /api/mcp
// Handles listing all MCP servers and creating new ones

import { NextRequest, NextResponse } from 'next/server';
import { getRegistry } from '@/lib/mcp-hub/registry';
import { getManager } from '@/lib/mcp-hub/manager';
import { MCPServer } from '@/lib/mcp-hub/types';

const registry = getRegistry();
const manager = getManager();

// GET /api/mcp - List all MCP servers
export async function GET() {
  try {
    // Sync statuses with PM2 before returning
    await manager.syncStatuses();

    const servers = registry.getServers();

    return NextResponse.json({
      success: true,
      servers,
      count: servers.length,
    });
  } catch (error: any) {
    console.error('[API MCP GET] Error:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// POST /api/mcp - Create a new custom MCP server
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const {
      id,
      name,
      description,
      command,
      args,
      cwd,
      env,
    } = body;

    // Validation
    if (!id || !name || !command || !args) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields: id, name, command, args' },
        { status: 400 }
      );
    }

    // Check if ID already exists
    if (registry.getServer(id)) {
      return NextResponse.json(
        { success: false, error: 'Server with this ID already exists' },
        { status: 400 }
      );
    }

    // Create new server
    const newServer: Omit<MCPServer, 'addedAt'> = {
      id,
      name,
      description: description || '',
      type: 'custom',
      command,
      args: Array.isArray(args) ? args : [args],
      cwd,
      env: env || {},
      status: 'stopped',
      pm2Name: `mcp-${id}`,
      toolCount: 0, // Will be updated after first connection
    };

    const server = registry.addServer(newServer);

    return NextResponse.json({
      success: true,
      server,
    });
  } catch (error: any) {
    console.error('[API MCP POST] Error:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
