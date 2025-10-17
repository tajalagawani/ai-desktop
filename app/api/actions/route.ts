import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import crypto from 'crypto';

export async function GET() {
  try {
    const actionsPath = path.join(process.cwd(), 'flow-architect', 'actions');

    // Check if actions directory exists
    try {
      await fs.access(actionsPath);
    } catch {
      // Directory doesn't exist, return empty list
      return NextResponse.json({ actions: [] });
    }

    const entries = await fs.readdir(actionsPath, { withFileTypes: true });
    const actions = [];

    for (const entry of entries) {
      if (entry.isDirectory()) {
        // New folder-based action
        const actionPath = path.join(actionsPath, entry.name);
        const actionActPath = path.join(actionPath, 'action.act');
        const metadataPath = path.join(actionPath, 'metadata.json');

        try {
          // Check if action.act exists in folder
          await fs.access(actionActPath);

          // Try to read metadata
          let metadata = null;
          try {
            const metadataContent = await fs.readFile(metadataPath, 'utf8');
            metadata = JSON.parse(metadataContent);

            // Generate UUID if missing
            if (!metadata.id) {
              metadata.id = crypto.randomUUID();
              // Save updated metadata
              try {
                await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2), 'utf8');
              } catch (writeErr) {
                console.error('Failed to update metadata with UUID:', writeErr);
              }
            }
          } catch {
            // No metadata, that's okay - generate minimal metadata
            metadata = {
              id: crypto.randomUUID(),
              name: entry.name,
              created: new Date().toISOString(),
              author: 'Action Builder'
            };
          }

          actions.push({
            name: entry.name,
            type: 'folder',
            metadata,
            path: `actions/${entry.name}/`
          });
        } catch {
          // No action.act in this folder, skip
        }
      } else if (entry.name.endsWith('.act')) {
        // Legacy flat .act file - generate deterministic ID from filename
        const legacyId = crypto.createHash('md5').update(entry.name).digest('hex');
        actions.push({
          name: entry.name,
          type: 'file',
          metadata: {
            id: legacyId,
            name: entry.name.replace('.act', ''),
            type: 'legacy'
          },
          path: `actions/${entry.name}`
        });
      }
    }

    return NextResponse.json({ actions });
  } catch (error: any) {
    console.error('[API] Error fetching actions:', error);
    return NextResponse.json({ actions: [] });
  }
}
