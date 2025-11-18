import { NextRequest, NextResponse } from 'next/server';
import { upsertMessage } from '@/lib/flow-builder/db';

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();

    // Upsert the message (update if exists, create if not)
    const result = upsertMessage({
      id: params.id,
      ...body,
    });

    console.log('[API Messages PATCH] Upserted message:', params.id, '- created:', result.created);

    return NextResponse.json({
      success: true,
      created: result.created,
      message: result.message
    });
  } catch (error) {
    console.error('[API Messages PATCH] Error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to upsert message' },
      { status: 500 }
    );
  }
}
