import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export async function DELETE(
  request: Request,
  { params }: { params: { actionName: string } }
) {
  try {
    const { actionName } = params;
    const actionsPath = path.join(process.cwd(), 'flow-architect', 'actions');

    console.log('[API] Deleting action:', actionName);

    // Security check
    if (actionName.includes('..') || actionName.includes('/')) {
      return NextResponse.json({ error: 'Invalid action name' }, { status: 400 });
    }

    // Check if it's a folder-based action
    const folderPath = path.join(actionsPath, actionName);
    try {
      const stats = await fs.stat(folderPath);
      if (stats.isDirectory()) {
        // Delete folder and all contents
        await fs.rm(folderPath, { recursive: true, force: true });
        console.log('[API] ✅ Deleted action folder:', actionName);
      } else {
        // Legacy flat file
        const filePath = path.join(actionsPath, actionName);
        await fs.unlink(filePath);
        console.log('[API] ✅ Deleted action file:', actionName);
      }
    } catch (error: any) {
      if (error.code === 'ENOENT') {
        // Try as flat file
        const filePath = path.join(actionsPath, actionName);
        await fs.unlink(filePath);
        console.log('[API] ✅ Deleted action file:', actionName);
      } else {
        throw error;
      }
    }

    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('[API] ❌ Error deleting action:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to delete action' },
      { status: 500 }
    );
  }
}
