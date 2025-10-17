import { NextResponse } from 'next/server';
import { addProjectManually } from '@/lib/claude/projects';

export async function POST(request: Request) {
  try {
    const { path } = await request.json();

    console.log('[API] Creating project manually');
    console.log('[API] Path:', path);

    if (!path) {
      return NextResponse.json(
        { error: 'Path is required' },
        { status: 400 }
      );
    }

    await addProjectManually(path);

    console.log('[API] ✅ Project created successfully');
    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('[API] ❌ Error creating project:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to create project' },
      { status: 500 }
    );
  }
}
