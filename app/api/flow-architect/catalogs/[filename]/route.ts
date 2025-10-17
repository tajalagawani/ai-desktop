import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export async function GET(
  request: Request,
  { params }: { params: { filename: string } }
) {
  try {
    const { filename } = params;

    // Security check: ensure filename doesn't contain path traversal
    if (filename.includes('..') || filename.includes('/')) {
      return NextResponse.json(
        { error: 'Invalid filename' },
        { status: 400 }
      );
    }

    const catalogPath = path.join(process.cwd(), 'flow-architect', 'catalogs', filename);

    console.log('[API] Catalog request:', filename);
    console.log('[API] Full path:', catalogPath);

    const content = await fs.readFile(catalogPath, 'utf8');
    const catalog = JSON.parse(content);

    return NextResponse.json(catalog);
  } catch (error: any) {
    console.error('[API] Catalog read error:', error);
    return NextResponse.json(
      { error: 'Catalog not found' },
      { status: 404 }
    );
  }
}
