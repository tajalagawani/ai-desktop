import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * GET /api/signature/raw - Get raw signature file content
 */
export async function GET(request: NextRequest) {
  try {
    const signaturePath = path.join(
      process.cwd(),
      'signature-system/signatures/user.act.sig'
    );

    if (!fs.existsSync(signaturePath)) {
      return new NextResponse('Signature file not found', {
        status: 404,
        headers: {
          'Content-Type': 'text/plain',
        },
      });
    }

    const content = fs.readFileSync(signaturePath, 'utf-8');

    return new NextResponse(content, {
      status: 200,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
      },
    });
  } catch (error: any) {
    console.error('[Signature Raw API] Error:', error);
    return new NextResponse(`Error reading signature file: ${error.message}`, {
      status: 500,
      headers: {
        'Content-Type': 'text/plain',
      },
    });
  }
}
