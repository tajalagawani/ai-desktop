import { NextRequest, NextResponse } from 'next/server';
import { getNodeCatalog } from '@/lib/node-parser';
import { getEnabledNodes } from '@/lib/auth-db';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';

const execAsync = promisify(exec);

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const includeDisabled = searchParams.get('includeDisabled') === 'true';

    // Get enabled nodes from database
    const enabledNodeTypes = getEnabledNodes();

    // Get all nodes (cached, fast)
    const nodeCatalog = getNodeCatalog();

    // Filter nodes based on enabled status
    let availableNodes = nodeCatalog.nodes;

    if (!includeDisabled) {
      // Only show nodes that don't require auth OR are enabled
      availableNodes = availableNodes.filter(node =>
        !node.authInfo.requiresAuth || enabledNodeTypes.includes(node.id)
      );
    }

    // Get running Docker services - DIRECT, no HTTP call
    let services: any[] = [];
    try {
      const { stdout } = await execAsync('docker ps --format "{{.Names}}|{{.Status}}|{{.Image}}"');
      services = stdout
        .trim()
        .split('\n')
        .filter(line => line)
        .map(line => {
          const [name, status, image] = line.split('|');
          return {
            id: name,
            name,
            status: status.toLowerCase().includes('up') ? 'running' : 'stopped',
            category: 'docker',
            type: 'docker'
          };
        });
    } catch (error) {
      console.error('Error fetching Docker services:', error);
    }

    // Get deployed flows - DIRECT, no HTTP call
    let flows: any[] = [];
    try {
      const flowsDir = path.join(process.cwd(), 'components/apps/act-docker/flows');
      const files = await fs.readdir(flowsDir);
      flows = files
        .filter(f => f.endsWith('.flow'))
        .map(f => ({
          id: f.replace('.flow', ''),
          name: f.replace('.flow', ''),
          type: 'flow',
          status: 'deployed'
        }));
    } catch (error) {
      console.error('Error fetching flows:', error);
    }

    return NextResponse.json({
      services: services.map(s => ({
        id: s.id,
        name: s.name,
        type: 'docker',
        status: s.status,
        category: s.category,
        connection: s.connection
      })),
      nodes: availableNodes.map(n => ({
        id: n.id,
        displayName: n.displayName,
        type: 'node',
        description: n.description.substring(0, 150),
        operations: n.operations.length,
        requiresAuth: n.authInfo.requiresAuth,
        enabled: !n.authInfo.requiresAuth || enabledNodeTypes.includes(n.id),
        authenticated: enabledNodeTypes.includes(n.id),
        tags: n.tags,
        capabilities: n.capabilities
      })),
      flows: flows.map(f => ({
        id: f.id,
        name: f.name,
        type: 'flow',
        status: f.status,
        endpoints: f.endpoints
      })),
      summary: {
        totalServices: services.length,
        totalNodes: availableNodes.length,
        totalFlows: flows.length,
        enabledNodes: enabledNodeTypes.length
      },
      generated: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Error in /api/unified:', error);
    return NextResponse.json(
      { error: error.message, stack: error.stack },
      { status: 500 }
    );
  }
}
