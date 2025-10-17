import { NextResponse } from 'next/server';
import { deleteSession } from '@/lib/claude/projects';

export async function DELETE(
  request: Request,
  { params }: { params: { projectName: string; sessionId: string } }
) {
  try {
    const { projectName, sessionId } = params;

    console.log('[API] Deleting session:', sessionId);
    console.log('[API] Project:', projectName);

    await deleteSession(projectName, sessionId);

    console.log('[API] ✅ Session deleted successfully');
    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('[API] ❌ Error deleting session:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to delete session' },
      { status: 500 }
    );
  }
}
