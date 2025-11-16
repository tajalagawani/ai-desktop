import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const SIGNATURE_FILE = path.join(process.cwd(), 'signature-system/signatures/user.act.sig');

// Parse operations from signature file for a specific node
function parseNodeOperations(content: string, nodeType: string) {
  const lines = content.split('\n');
  let inTargetNode = false;
  const operations: any[] = [];

  for (const line of lines) {
    const trimmed = line.trim();

    // Check if we're entering the target node section
    if (trimmed === `[node:${nodeType}]`) {
      inTargetNode = true;
      continue;
    }

    // Check if we're leaving the node section
    if (inTargetNode && trimmed.startsWith('[') && trimmed.endsWith(']')) {
      break; // Exit when we hit another section
    }

    // Parse operations array
    if (inTargetNode && trimmed.startsWith('operations = ')) {
      const opsString = trimmed.replace('operations = ', '').trim();
      // Parse array: ["op1", "op2", "op3"]
      const opsMatch = opsString.match(/\[([^\]]+)\]/);
      if (opsMatch) {
        const opsArray = opsMatch[1]
          .split(',')
          .map(op => op.trim().replace(/"/g, ''));

        opsArray.forEach(opName => {
          operations.push({
            name: opName,
            displayName: formatDisplayName(opName),
            description: `${opName} operation`
          });
        });
      }
      break; // Found operations, exit
    }
  }

  return operations;
}

// Format operation name to display name
function formatDisplayName(name: string): string {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// GET - Get operations for an authenticated node from signature file
export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const nodeType = searchParams.get('node_type');

    if (!nodeType) {
      return NextResponse.json(
        { error: 'Missing node_type parameter' },
        { status: 400 }
      );
    }

    // Check if signature file exists
    try {
      await fs.access(SIGNATURE_FILE);
    } catch {
      return NextResponse.json({ operations: [] });
    }

    const content = await fs.readFile(SIGNATURE_FILE, 'utf-8');

    // Check if node exists in signature
    if (!content.includes(`[node:${nodeType}]`)) {
      return NextResponse.json(
        { error: `Node '${nodeType}' not found in signature` },
        { status: 404 }
      );
    }

    const operations = parseNodeOperations(content, nodeType);

    return NextResponse.json({ operations });
  } catch (error: any) {
    console.error('Error reading signature operations:', error);
    return NextResponse.json(
      { error: 'Failed to read signature operations', details: error.message },
      { status: 500 }
    );
  }
}
