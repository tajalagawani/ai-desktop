import { NextRequest, NextResponse } from 'next/server';
import { getNodeCatalog } from '@/lib/node-parser';
import { saveNodeAuth, getNodeAuth, deleteNodeAuth } from '@/lib/auth-db';

// Save/Enable node authentication
export async function POST(
  request: NextRequest,
  { params }: { params: { nodeType: string } }
) {
  try {
    const { nodeType } = params;
    const body = await request.json();
    const { authData } = body;

    if (!authData || typeof authData !== 'object') {
      return NextResponse.json(
        { error: 'authData is required and must be an object' },
        { status: 400 }
      );
    }

    // Verify node exists and requires auth
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

    // Validate required fields
    const requiredFields = node.authInfo.authFields.filter(f => f.required);
    const missingFields = requiredFields.filter(f => !authData[f.field]);

    if (missingFields.length > 0) {
      return NextResponse.json(
        {
          error: 'Missing required fields',
          missing: missingFields.map(f => f.field)
        },
        { status: 400 }
      );
    }

    // Save to database (encrypted)
    const result = saveNodeAuth(node.id, authData);

    return NextResponse.json({
      success: true,
      nodeType: node.id,
      enabled: true,
      message: 'Authentication saved successfully'
    });

  } catch (error: any) {
    console.error(`Error saving auth for ${params.nodeType}:`, error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// Get node authentication status
export async function GET(
  request: NextRequest,
  { params }: { params: { nodeType: string } }
) {
  try {
    const { nodeType } = params;

    const authData = getNodeAuth(nodeType);

    return NextResponse.json({
      nodeType,
      enabled: !!authData,
      hasAuth: !!authData
    });

  } catch (error: any) {
    console.error(`Error getting auth for ${params.nodeType}:`, error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// Delete node authentication
export async function DELETE(
  request: NextRequest,
  { params }: { params: { nodeType: string } }
) {
  try {
    const { nodeType } = params;

    const result = deleteNodeAuth(nodeType);

    return NextResponse.json({
      success: true,
      nodeType,
      enabled: false,
      message: 'Authentication removed successfully'
    });

  } catch (error: any) {
    console.error(`Error deleting auth for ${params.nodeType}:`, error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
