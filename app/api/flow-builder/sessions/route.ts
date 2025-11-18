import { NextRequest, NextResponse } from 'next/server';
import { createSession, getUserSessions } from '@/lib/flow-builder/db';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get('userId') || 'default-user';
  const limit = parseInt(searchParams.get('limit') || '50', 10);

  try {
    const sessions = getUserSessions(userId, limit);
    console.log('[API Sessions GET] Retrieved', sessions.length, 'sessions for user:', userId);
    return NextResponse.json({ success: true, sessions });
  } catch (error) {
    console.error('[API Sessions GET] Error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch sessions' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { userId, title } = body;

    const sessionData = {
      id: `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      userId: userId || 'default-user',
      title: title || 'New Flow',
    };

    const session = createSession(sessionData);
    console.log('[API Sessions POST] Created session:', session.id);

    return NextResponse.json({ success: true, session });
  } catch (error) {
    console.error('[API Sessions POST] Error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to create session' },
      { status: 500 }
    );
  }
}
