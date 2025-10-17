import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export async function POST(request: Request) {
  try {
    const { envVars, actionFolder } = await request.json();
    const flowArchitectPath = path.join(process.cwd(), 'flow-architect');

    console.log('[API] Save env variables');
    console.log('[API] Action folder:', actionFolder || 'global');
    console.log('[API] Variables:', Object.keys(envVars || {}).join(', '));

    // Determine where to save the .env file
    let envFilePath: string;
    if (actionFolder) {
      // Save to action-specific folder
      envFilePath = path.join(flowArchitectPath, 'actions', actionFolder, '.env');
    } else {
      // Save to global flow-architect/.env (for legacy actions)
      envFilePath = path.join(flowArchitectPath, '.env');
    }

    // Read existing .env file if it exists
    let existingEnv: Record<string, string> = {};
    try {
      const content = await fs.readFile(envFilePath, 'utf8');
      content.split('\n').forEach(line => {
        const trimmed = line.trim();
        if (trimmed && !trimmed.startsWith('#')) {
          const [key, ...valueParts] = trimmed.split('=');
          if (key) {
            existingEnv[key.trim()] = valueParts.join('=').trim();
          }
        }
      });
    } catch {
      // File doesn't exist, start fresh
      console.log('[API] No existing .env file, creating new one');
    }

    // Merge with new values
    const merged = { ...existingEnv, ...envVars };

    // Generate .env content
    const envContent = Object.entries(merged)
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');

    // Write to .env file
    await fs.writeFile(envFilePath, envContent + '\n', 'utf8');

    console.log('[API] ✅ Saved env file to:', envFilePath);
    return NextResponse.json({ success: true, path: envFilePath, vars: merged });
  } catch (error: any) {
    console.error('[API] ❌ Save env error:', error);
    return NextResponse.json(
      { error: 'Failed to save env variables' },
      { status: 500 }
    );
  }
}
