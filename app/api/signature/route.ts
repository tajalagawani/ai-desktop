import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const SIGNATURE_FILE = path.join(process.cwd(), 'signature-system/signatures/user.act.sig');

// Parse TOML signature file (simple parser)
function parseSignature(content: string) {
  const lines = content.split('\n');
  const authenticatedNodes: string[] = [];

  let currentSection = '';

  for (const line of lines) {
    const trimmed = line.trim();

    // Section header
    if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
      currentSection = trimmed.slice(1, -1);

      // If section is a node (e.g., [node:github])
      if (currentSection.startsWith('node:')) {
        const nodeType = currentSection.replace('node:', '');
        authenticatedNodes.push(nodeType);
      }
    }
  }

  return authenticatedNodes;
}

// GET - List authenticated nodes
export async function GET(req: NextRequest) {
  try {
    // Check if signature file exists
    try {
      await fs.access(SIGNATURE_FILE);
    } catch {
      // File doesn't exist, return empty list
      return NextResponse.json({ authenticated_nodes: [] });
    }

    const content = await fs.readFile(SIGNATURE_FILE, 'utf-8');
    const authenticatedNodes = parseSignature(content);

    return NextResponse.json({ authenticated_nodes: authenticatedNodes });
  } catch (error: any) {
    console.error('Error reading signature file:', error);
    return NextResponse.json(
      { error: 'Failed to read signature file', details: error.message },
      { status: 500 }
    );
  }
}

// POST - Add node authentication
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { node_type, auth, defaults = {}, operations = [] } = body;

    if (!node_type || !auth) {
      return NextResponse.json(
        { error: 'Missing required fields: node_type, auth' },
        { status: 400 }
      );
    }

    // Read existing signature
    let content = '';
    try {
      content = await fs.readFile(SIGNATURE_FILE, 'utf-8');
    } catch {
      // Create new signature file
      content = `[signature]
version = "1.0.0"
created_at = "${new Date().toISOString()}"
updated_at = "${new Date().toISOString()}"

[metadata]
authenticated_nodes = 0
last_updated = "${new Date().toISOString()}"
`;
    }

    // Check if node already exists
    if (content.includes(`[node:${node_type}]`)) {
      return NextResponse.json(
        { error: `Node '${node_type}' already authenticated` },
        { status: 409 }
      );
    }

    // Build node section
    let nodeSection = `\n[node:${node_type}]\n`;
    nodeSection += `authenticated = true\n`;
    nodeSection += `added_at = "${new Date().toISOString()}"\n`;

    // Add auth fields
    for (const [key, value] of Object.entries(auth)) {
      nodeSection += `${key} = "${value}"\n`;
    }

    // Add operations if provided
    if (operations.length > 0) {
      nodeSection += `operations = [${operations.map((op: string) => `"${op}"`).join(', ')}]\n`;
    }

    // Append to signature file
    const updatedContent = content + nodeSection;

    // Write back
    await fs.writeFile(SIGNATURE_FILE, updatedContent, 'utf-8');

    return NextResponse.json({
      status: 'success',
      message: `Node '${node_type}' authenticated successfully`,
      authenticated: true,
      node_type
    });
  } catch (error: any) {
    console.error('Error adding node:', error);
    return NextResponse.json(
      { error: 'Failed to add node', details: error.message },
      { status: 500 }
    );
  }
}

// DELETE - Remove node authentication
export async function DELETE(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const nodeType = searchParams.get('node_type');

    if (!nodeType) {
      return NextResponse.json(
        { error: 'Missing node_type parameter' },
        { status: 400 }
      );
    }

    // Read signature file
    const content = await fs.readFile(SIGNATURE_FILE, 'utf-8');
    const lines = content.split('\n');

    // Remove node section
    const newLines: string[] = [];
    let inNodeSection = false;
    let nodeFound = false;

    for (const line of lines) {
      const trimmed = line.trim();

      // Check if entering the target node section
      if (trimmed === `[node:${nodeType}]`) {
        inNodeSection = true;
        nodeFound = true;
        continue; // Skip this line
      }

      // Check if entering a new section (end of current node section)
      if (inNodeSection && trimmed.startsWith('[') && trimmed.endsWith(']')) {
        inNodeSection = false;
      }

      // Keep line if not in target node section
      if (!inNodeSection) {
        newLines.push(line);
      }
    }

    if (!nodeFound) {
      return NextResponse.json(
        { error: `Node '${nodeType}' not found in signature` },
        { status: 404 }
      );
    }

    // Write updated content
    await fs.writeFile(SIGNATURE_FILE, newLines.join('\n'), 'utf-8');

    return NextResponse.json({
      status: 'success',
      message: `Node '${nodeType}' removed successfully`
    });
  } catch (error: any) {
    console.error('Error removing node:', error);
    return NextResponse.json(
      { error: 'Failed to remove node', details: error.message },
      { status: 500 }
    );
  }
}
