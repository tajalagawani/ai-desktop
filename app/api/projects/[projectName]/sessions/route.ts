import { NextResponse } from 'next/server';
import { getSessions } from '@/lib/claude/projects';

export async function GET(
  request: Request,
  { params }: { params: { projectName: string } }
) {
  try {
    const { projectName } = params;
    const { searchParams } = new URL(request.url);

    const limit = searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : 5;
    const offset = searchParams.get('offset') ? parseInt(searchParams.get('offset')!) : 0;

    console.log('[API] Loading sessions for project:', projectName);
    console.log('[API] Limit:', limit, 'Offset:', offset);

    const result = await getSessions(projectName, limit, offset);

    console.log('[API] ✅ Loaded sessions:', result.sessions?.length || 0);
    return NextResponse.json(result);
  } catch (error: any) {
    console.error('[API] ❌ Error loading sessions:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to load sessions' },
      { status: 500 }
    );
  }
}
