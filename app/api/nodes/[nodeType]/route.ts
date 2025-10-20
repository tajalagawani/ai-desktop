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

    // Find the requested node (case-insensitive)
    const node = nodes.find((n: any) =>
      n.id === nodeType || n.id.toLowerCase() === nodeType.toLowerCase()
    );

    if (!node) {
      return NextResponse.json(
        {
          error: `Node type '${nodeType}' not found`,
          available: nodes.slice(0, 10).map((n: any) => n.id)
        },
        { status: 404 }
      );
    }

    // Return complete node information
    return NextResponse.json(node);

  } catch (error: any) {
    console.error(`Error getting node ${params.nodeType}:`, error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
