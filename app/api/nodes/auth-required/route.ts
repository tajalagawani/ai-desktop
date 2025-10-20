import { NextRequest, NextResponse } from 'next/server';
import { getNodeCatalog } from '@/lib/node-parser';
import { getEnabledNodes } from '@/lib/auth-db';

export async function GET(request: NextRequest) {
  try {
    const catalog = getNodeCatalog();
    const enabledNodes = getEnabledNodes();

    // Filter nodes that require auth
    const authNodes = catalog.nodes
      .filter(n => n.authInfo.requiresAuth)
      .map(node => ({
        id: node.id,
        displayName: node.displayName,
        description: node.description.substring(0, 150) + '...',
        authInfo: node.authInfo,
        userEnabled: enabledNodes.includes(node.id),
        operations: node.operations.length,
        tags: node.tags
      }));

    return NextResponse.json({
      nodes: authNodes,
      total: authNodes.length,
      enabled: enabledNodes.length
    });

  } catch (error: any) {
    console.error('Error in /api/nodes/auth-required:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
