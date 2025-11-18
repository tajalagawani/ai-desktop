import { NextResponse } from 'next/server';

/**
 * GET /api/flow-builder/settings
 * Returns server-side Flow Builder settings for agent configuration
 */
export async function GET() {
  try {
    // These settings are passed to the agent process
    const settings = {
      // Check if sandbox bypass is allowed from environment variable
      // This can be set in .env for VPS deployments
      allowSandboxBypass: process.env.ALLOW_SANDBOX_BYPASS === 'true',
    };

    return NextResponse.json({ success: true, settings });
  } catch (error) {
    console.error('[API Settings GET] Error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to get settings' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/flow-builder/settings
 * Updates server-side settings (persists to environment or database)
 */
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { allowSandboxBypass } = body;

    // For now, we'll return the setting but note that it needs to be set in .env
    // In a production system, you might want to persist this to a database

    return NextResponse.json({
      success: true,
      message: 'To persist this setting, add ALLOW_SANDBOX_BYPASS=true to your .env file',
      settings: {
        allowSandboxBypass: allowSandboxBypass || false,
      },
    });
  } catch (error) {
    console.error('[API Settings POST] Error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to update settings' },
      { status: 500 }
    );
  }
}
