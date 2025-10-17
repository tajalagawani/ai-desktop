import { NextResponse } from 'next/server';
import { deleteProject, renameProject } from '@/lib/claude/projects';

export async function DELETE(
  request: Request,
  { params }: { params: { projectName: string } }
) {
  try {
    const { projectName } = params;

    console.log('[API] Deleting project:', projectName);

    await deleteProject(projectName);

    console.log('[API] ✅ Project deleted successfully');
    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('[API] ❌ Error deleting project:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to delete project' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: Request,
  { params }: { params: { projectName: string } }
) {
  try {
    const { projectName } = params;
    const { displayName } = await request.json();

    console.log('[API] Renaming project:', projectName);
    console.log('[API] New display name:', displayName);

    await renameProject(projectName, displayName);

    console.log('[API] ✅ Project renamed successfully');
    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('[API] ❌ Error renaming project:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to rename project' },
      { status: 500 }
    );
  }
}
