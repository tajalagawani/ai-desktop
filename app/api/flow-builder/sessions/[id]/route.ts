import { NextRequest, NextResponse } from 'next/server';
import { getSession, getSessionMessages, deleteSession } from '@/lib/flow-builder/db';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = getSession(params.id);

    if (!session) {
      console.log('[API Sessions GET [id]] Session not found:', params.id);
      return NextResponse.json(
        { success: false, error: 'Session not found' },
        { status: 404 }
      );
    }

    // Get messages for this session
    const messages = getSessionMessages(params.id);
    console.log('[API Sessions GET [id]] Session found:', params.id, 'with', messages.length, 'messages');

    // Return session with messages
    const sessionWithMessages = {
      ...session,
      messages,
    };

    return NextResponse.json({ success: true, session: sessionWithMessages });
  } catch (error) {
    console.error('[API Sessions GET [id]] Error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch session' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const deleted = deleteSession(params.id);

    if (!deleted) {
      console.log('[API Sessions DELETE] Session not found:', params.id);
      return NextResponse.json(
        { success: false, error: 'Session not found' },
        { status: 404 }
      );
    }

    console.log('[API Sessions DELETE] Session deleted:', params.id);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('[API Sessions DELETE] Error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to delete session' },
      { status: 500 }
    );
  }
}
