import { NextRequest, NextResponse } from 'next/server';
import { getNodeCatalog } from '@/lib/node-parser';
import { getNodeAuth, getEnabledNodes } from '@/lib/auth-db';

export async function GET(
  request: NextRequest,
  { params }: { params: { nodeType: string } }
) {
  try {
    const { nodeType } = params;

    const catalog = getNodeCatalog();
    const node = catalog.nodes.find(n => n.id === nodeType || n.id.toLowerCase() === nodeType.toLowerCase());

    if (!node) {
      return NextResponse.json(
        { error: `Node type '${nodeType}' not found` },
        { status: 404 }
      );
    }

    if (!node.authInfo.requiresAuth) {
      return NextResponse.json(
        { error: `Node type '${nodeType}' does not require authentication` },
        { status: 400 }
      );
    }

    const enabledNodes = getEnabledNodes();
    const isEnabled = enabledNodes.includes(node.id);

    return NextResponse.json({
      nodeType: node.id,
      displayName: node.displayName,
      description: node.description,
      authInfo: node.authInfo,
      userEnabled: isEnabled,
      operations: node.operations.length,
      tags: node.tags
    });

  } catch (error: any) {
    console.error(`Error getting auth info for ${params.nodeType}:`, error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
