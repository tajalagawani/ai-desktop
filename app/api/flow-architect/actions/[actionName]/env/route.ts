import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export async function GET(
  request: Request,
  { params }: { params: { actionName: string } }
) {
  try {
    const { actionName } = params;
    const actionsPath = path.join(process.cwd(), 'flow-architect', 'actions');

    console.log('[API] Parse env for action:', actionName);

    // Security check
    if (actionName.includes('..') || actionName.includes('/')) {
      return NextResponse.json({ error: 'Invalid action name' }, { status: 400 });
    }

    let actFilePath: string;
    let actionFolder: string | null = null;

    // Check if it's a folder-based action
    const folderPath = path.join(actionsPath, actionName);
    try {
      const stats = await fs.stat(folderPath);
      if (stats.isDirectory()) {
        // Folder-based action
        actFilePath = path.join(folderPath, 'action.act');
        actionFolder = actionName;
      } else {
        // Legacy flat file
        actFilePath = path.join(actionsPath, actionName);
      }
    } catch {
      // Assume it's a flat file if stat fails
      actFilePath = path.join(actionsPath, actionName);
    }

    // Read the .act file
    const content = await fs.readFile(actFilePath, 'utf8');

    // Parse [env] section using regex
    const envMatch = content.match(/\[env\]([\s\S]*?)(?=\n\[|\n*$)/);

    if (!envMatch) {
      console.log('[API] No [env] section found');
      return NextResponse.json({ env: {}, actionName, actionFolder });
    }

    // Parse key-value pairs
    const envSection = envMatch[1];
    const envVars: Record<string, string> = {};
    const lines = envSection.split('\n');

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const match = trimmed.match(/^([A-Z_][A-Z0-9_]*)\s*=\s*"?([^"]*)"?/);
        if (match) {
          const [, key, value] = match;
          envVars[key] = value;
        }
      }
    }

    console.log('[API] ✅ Parsed', Object.keys(envVars).length, 'env variables');
    return NextResponse.json({ env: envVars, actionName, actionFolder });
  } catch (error: any) {
    console.error('[API] ❌ Parse env error:', error);
    return NextResponse.json(
      { error: 'Failed to parse env variables' },
      { status: 500 }
    );
  }
}
