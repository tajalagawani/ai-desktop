import { NextRequest, NextResponse } from 'next/server';
import { saveServiceAuth, getServiceAuth, deleteServiceAuth } from '@/lib/auth-db';

interface RouteContext {
  params: {
    serviceId: string;
  };
}

/**
 * GET /api/services/[serviceId]/auth
 * Get stored authentication for a service
 */
export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  try {
    const { serviceId } = context.params;
    const authData = getServiceAuth(serviceId);

    if (!authData) {
      return NextResponse.json(
        { error: 'No authentication data found for this service' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      serviceId,
      authData
    });
  } catch (error: any) {
    console.error('Error getting service auth:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to get service auth' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/services/[serviceId]/auth
 * Save authentication credentials for a service
 */
export async function POST(
  request: NextRequest,
  context: RouteContext
) {
  try {
    const { serviceId } = context.params;
    const body = await request.json();
    const { authData } = body;

    if (!authData || typeof authData !== 'object') {
      return NextResponse.json(
        { error: 'Invalid auth data provided' },
        { status: 400 }
      );
    }

    const result = saveServiceAuth(serviceId, authData);

    return NextResponse.json({
      success: true,
      message: 'Service authentication saved successfully',
      ...result
    });
  } catch (error: any) {
    console.error('Error saving service auth:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to save service auth' },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/services/[serviceId]/auth
 * Delete stored authentication for a service
 */
export async function DELETE(
  request: NextRequest,
  context: RouteContext
) {
  try {
    const { serviceId } = context.params;
    const result = deleteServiceAuth(serviceId);

    return NextResponse.json({
      success: true,
      message: 'Service authentication deleted successfully',
      ...result
    });
  } catch (error: any) {
    console.error('Error deleting service auth:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to delete service auth' },
      { status: 500 }
    );
  }
}
