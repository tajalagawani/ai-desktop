import { NextResponse } from 'next/server';
import { getSessionMessages } from '@/lib/claude/projects';

export async function GET(
  request: Request,
  { params }: { params: { projectName: string; sessionId: string } }
) {
  try {
    const { projectName, sessionId } = params;
    const { searchParams } = new URL(request.url);

    const limit = searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : null;
    const offset = searchParams.get('offset') ? parseInt(searchParams.get('offset')!) : 0;

    console.log('[API] Loading messages for session:', sessionId);
    console.log('[API] Project:', projectName);
    console.log('[API] Limit:', limit, 'Offset:', offset);

    const result = await getSessionMessages(projectName, sessionId, limit, offset);

    // Handle both old and new response formats
    if (Array.isArray(result)) {
      console.log('[API] ✅ Loaded', result.length, 'messages (array format)');
      return NextResponse.json({ messages: result });
    } else {
      console.log('[API] ✅ Loaded', result.messages?.length || 0, 'messages (object format)');
      return NextResponse.json(result);
    }
  } catch (error: any) {
    console.error('[API] ❌ Error loading messages:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to load messages' },
      { status: 500 }
    );
  }
}
