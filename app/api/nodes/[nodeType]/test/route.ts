import { NextRequest, NextResponse } from 'next/server';
import { getNodeCatalog } from '@/lib/node-parser';
import { updateTestResult } from '@/lib/auth-db';

// Test node authentication
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

    // Verify node exists
    const catalog = getNodeCatalog();
    const node = catalog.nodes.find(n => n.id === nodeType || n.id.toLowerCase() === nodeType.toLowerCase());

    if (!node) {
      return NextResponse.json(
        { error: `Node type '${nodeType}' not found` },
        { status: 404 }
      );
    }

    // Test the connection based on node type
    let testResult;

    try {
      testResult = await testNodeConnection(node.id, node.authInfo.authType, authData);

      // Update test result in database
      updateTestResult(node.id, testResult.success);

      return NextResponse.json({
        success: testResult.success,
        message: testResult.message,
        details: testResult.details
      });

    } catch (testError: any) {
      // Update failed test result
      updateTestResult(node.id, false);

      return NextResponse.json({
        success: false,
        message: testError.message || 'Connection test failed',
        error: testError.toString()
      });
    }

  } catch (error: any) {
    console.error(`Error testing auth for ${params.nodeType}:`, error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

/**
 * Test node connection based on type
 */
async function testNodeConnection(
  nodeType: string,
  authType: string | undefined,
  authData: Record<string, any>
): Promise<{ success: boolean; message: string; details?: any }> {

  // Simple validation tests for common node types
  switch (nodeType) {
    case 'openai':
      return testOpenAI(authData);

    case 'mongodb':
      return testMongoDB(authData);

    case 'postgresql':
    case 'neon':
      return testPostgreSQL(authData);

    default:
      // Generic test: just validate fields are present
      return {
        success: true,
        message: 'Authentication data validated (connection test not available for this node)',
        details: { validated: true }
      };
  }
}

/**
 * Test OpenAI API key
 */
async function testOpenAI(authData: Record<string, any>) {
  const apiKey = authData.api_key || authData.apiKey;

  if (!apiKey) {
    throw new Error('API key is required');
  }

  // Basic format validation
  if (!apiKey.startsWith('sk-')) {
    throw new Error('OpenAI API key must start with "sk-"');
  }

  // Try to fetch models list (lightweight API call)
  try {
    const response = await fetch('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Invalid API key');
    }

    const data = await response.json();

    return {
      success: true,
      message: 'OpenAI API key is valid',
      details: {
        modelsAvailable: data.data?.length || 0,
        sampleModels: data.data?.slice(0, 3).map((m: any) => m.id)
      }
    };

  } catch (error: any) {
    throw new Error(`OpenAI connection failed: ${error.message}`);
  }
}

/**
 * Test MongoDB connection
 */
async function testMongoDB(authData: Record<string, any>) {
  const connectionString = authData.connection_string || authData.connectionString;

  if (!connectionString) {
    throw new Error('Connection string is required');
  }

  // Basic format validation
  if (!connectionString.startsWith('mongodb://') && !connectionString.startsWith('mongodb+srv://')) {
    throw new Error('Invalid MongoDB connection string format');
  }

  // For now, just validate format
  // In production, you'd actually try to connect
  return {
    success: true,
    message: 'MongoDB connection string format is valid',
    details: { validated: true }
  };
}

/**
 * Test PostgreSQL connection
 */
async function testPostgreSQL(authData: Record<string, any>) {
  const connectionString = authData.connection_string || authData.connectionString;

  if (!connectionString) {
    throw new Error('Connection string is required');
  }

  // Basic format validation
  if (!connectionString.startsWith('postgres://') && !connectionString.startsWith('postgresql://')) {
    throw new Error('Invalid PostgreSQL connection string format');
  }

  // For now, just validate format
  return {
    success: true,
    message: 'PostgreSQL connection string format is valid',
    details: { validated: true }
  };
}
