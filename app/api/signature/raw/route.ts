import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const SIGNATURE_FILE = path.join(process.cwd(), 'signature-system/signatures/user.act.sig');

// GET - View raw signature file content
export async function GET() {
  try {
    // Check if signature file exists
    try {
      await fs.access(SIGNATURE_FILE);
    } catch {
      // File doesn't exist, return empty content
      return new NextResponse('# Signature file not created yet\n', {
        headers: { 'Content-Type': 'text/plain' }
      });
    }

    const content = await fs.readFile(SIGNATURE_FILE, 'utf-8');

    return new NextResponse(content, {
      headers: { 'Content-Type': 'text/plain' }
    });
  } catch (error: any) {
    console.error('Error reading signature file:', error);
    return new NextResponse(
      `# Error reading signature file: ${error.message}`,
      {
        status: 500,
        headers: { 'Content-Type': 'text/plain' }
      }
    );
  }
}
