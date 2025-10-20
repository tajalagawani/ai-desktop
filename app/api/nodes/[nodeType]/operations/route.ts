import { NextRequest, NextResponse } from 'next/server';
import { getNodeCatalog } from '@/lib/node-parser';

export async function GET(
  request: NextRequest,
  { params }: { params: { nodeType: string } }
) {
  try {
    const { nodeType } = params;

    const catalog = getNodeCatalog();
    const nodes = catalog.nodes;

    // Find the requested node
    const node = nodes.find((n: any) =>
      n.id === nodeType || n.id.toLowerCase() === nodeType.toLowerCase()
    );

    if (!node) {
      return NextResponse.json(
        { error: `Node type '${nodeType}' not found` },
        { status: 404 }
      );
    }

    // Return operations list with categories
    return NextResponse.json({
      nodeType: node.id,
      displayName: node.displayName,
      operations: node.operations,
      operationCategories: node.operationCategories,
      totalOperations: node.operations.length
    });

  } catch (error: any) {
    console.error(`Error getting operations for ${params.nodeType}:`, error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
