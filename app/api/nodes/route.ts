import { NextRequest, NextResponse } from 'next/server';
import { getNodeCatalog } from '@/lib/node-parser';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);

    // Check if force refresh is requested
    const forceRefresh = searchParams.get('refresh') === 'true';

    // Get catalog (cached unless forceRefresh)
    const catalog = getNodeCatalog(forceRefresh);
    let nodes = catalog.nodes;

    // Filter by capability
    const capability = searchParams.get('capability');
    if (capability) {
      nodes = nodes.filter((n: any) => n.capabilities && n.capabilities[capability]);
    }

    // Filter by category/tag
    const category = searchParams.get('category');
    if (category) {
      nodes = nodes.filter((n: any) => n.tags?.includes(category));
    }

    // Filter by type
    const type = searchParams.get('type');
    if (type) {
      nodes = nodes.filter((n: any) =>
        n.tags?.includes(type) || n.id.toLowerCase().includes(type.toLowerCase())
      );
    }

    // Search by keyword (searches in id, displayName, description, tags)
    const search = searchParams.get('search');
    if (search) {
      const term = search.toLowerCase();
      nodes = nodes.filter((n: any) =>
        n.id?.toLowerCase().includes(term) ||
        n.displayName?.toLowerCase().includes(term) ||
        n.description?.toLowerCase().includes(term) ||
        n.tags?.some((t: string) => t.toLowerCase().includes(term))
      );
    }

    // Extract available filters for response
    const allNodes = catalog.nodes;
    const allTags = new Set<string>();
    allNodes.forEach(n => n.tags.forEach(t => allTags.add(t)));

    const filters = {
      categories: Array.from(allTags).sort(),
      capabilities: Object.keys(allNodes[0]?.capabilities || {}),
      total: allNodes.length
    };

    return NextResponse.json({
      nodes: nodes.map(n => ({
        id: n.id,
        displayName: n.displayName,
        description: n.description.substring(0, 200) + (n.description.length > 200 ? '...' : ''),
        operations: n.operations.length,
        parameters: n.parameters.length,
        tags: n.tags,
        capabilities: n.capabilities
      })),
      total: nodes.length,
      filters,
      cached: !forceRefresh,
      generated: catalog.generated
    });

  } catch (error: any) {
    console.error('Error in /api/nodes:', error);
    return NextResponse.json(
      {
        error: error.message,
        stack: error.stack
      },
      { status: 500 }
    );
  }
}

// Force refresh endpoint
export async function POST(request: NextRequest) {
  try {
    const catalog = getNodeCatalog(true);
    return NextResponse.json({
      success: true,
      message: 'Node catalog refreshed',
      total: catalog.nodes.length,
      generated: catalog.generated
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
