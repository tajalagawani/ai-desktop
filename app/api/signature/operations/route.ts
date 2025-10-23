import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * GET /api/signature/operations?node_type=xxx
 * Get operations for an authenticated node from the signature file
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const nodeType = searchParams.get('node_type');

    if (!nodeType) {
      return NextResponse.json(
        { error: 'Missing node_type parameter' },
        { status: 400 }
      );
    }

    const sigPath = path.join(process.cwd(), 'signature-system/signatures/user.act.sig');

    if (!fs.existsSync(sigPath)) {
      return NextResponse.json(
        { error: 'Signature file not found' },
        { status: 404 }
      );
    }

    const sigContent = fs.readFileSync(sigPath, 'utf-8');

    // Parse operations directly from TOML text using regex
    const operations: any[] = [];
    const nodeKey = `node:${nodeType}`;

    // Match patterns like: ["node:activecampaign.operations".list_contacts]
    const opRegex = new RegExp(`\\["${nodeKey}\\.operations"\\.(\\w+)\\]`, 'g');
    let match;

    while ((match = opRegex.exec(sigContent)) !== null) {
      const opName = match[1];

      // Extract description and category for this operation
      const opSectionStart = match.index;
      const nextSectionMatch = sigContent.indexOf('[', opSectionStart + 1);
      const opSection = nextSectionMatch > 0
        ? sigContent.substring(opSectionStart, nextSectionMatch)
        : sigContent.substring(opSectionStart);

      const descMatch = opSection.match(/description = "(.+)"/);
      const catMatch = opSection.match(/category = "(.+)"/);

      operations.push({
        name: opName,
        displayName: opName.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
        description: descMatch ? descMatch[1] : '',
        category: catMatch ? catMatch[1] : 'other'
      });
    }

    console.log(`[API /signature/operations] Found ${operations.length} operations for ${nodeType}`);

    return NextResponse.json({
      success: true,
      node_type: nodeType,
      operations,
      count: operations.length
    });
  } catch (error: any) {
    console.error('[API /signature/operations] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to get operations from signature' },
      { status: 500 }
    );
  }
}
