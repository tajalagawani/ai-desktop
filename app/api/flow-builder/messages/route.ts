import { NextRequest, NextResponse } from 'next/server';
import { createMessage } from '@/lib/flow-builder/db';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log('[API Messages POST] Received body:', JSON.stringify(body, null, 2));

    const {
      id,
      sessionId,
      role,
      content,
      type,
      streaming,
      error,
      metadata,
      inputTokens,
      outputTokens,
    } = body;

    // Validate required fields
    if (!sessionId) {
      console.error('[API Messages POST] Missing sessionId');
      return NextResponse.json(
        { success: false, error: 'Missing sessionId' },
        { status: 400 }
      );
    }

    if (!role) {
      console.error('[API Messages POST] Missing role');
      return NextResponse.json(
        { success: false, error: 'Missing role' },
        { status: 400 }
      );
    }

    if (!content) {
      console.error('[API Messages POST] Missing content');
      return NextResponse.json(
        { success: false, error: 'Missing content' },
        { status: 400 }
      );
    }

    const messageData = {
      id: id || `msg-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`,
      sessionId,
      role,
      content,
      type,
      streaming,
      error,
      metadata,
      inputTokens,
      outputTokens,
    };

    console.log('[API Messages POST] Creating message with data:', JSON.stringify(messageData, null, 2));

    const message = createMessage(messageData);
    console.log('[API Messages POST] Created message:', message.id);

    return NextResponse.json({ success: true, message });
  } catch (error) {
    console.error('[API Messages POST] Error:', error);
    console.error('[API Messages POST] Error stack:', (error as Error).stack);
    console.error('[API Messages POST] Error message:', (error as Error).message);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to create message',
        details: (error as Error).message
      },
      { status: 500 }
    );
  }
}
