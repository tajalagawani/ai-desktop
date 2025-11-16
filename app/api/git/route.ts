import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

export const dynamic = 'force-dynamic'

const execAsync = promisify(exec)

export async function POST(request: NextRequest) {
  try {
    const { repoPath, command } = await request.json()

    if (!repoPath || !command) {
      return NextResponse.json(
        { success: false, error: 'repoPath and command are required' },
        { status: 400 }
      )
    }

    // Security: Validate repo path (must be under /var/www or safe directory)
    const SAFE_PATHS = ['/var/www', '/root', '/home']
    const isSafePath = SAFE_PATHS.some(safePath => repoPath.startsWith(safePath))

    if (!isSafePath) {
      return NextResponse.json(
        { success: false, error: 'Invalid repository path' },
        { status: 403 }
      )
    }

    console.log(`[Git] Executing: ${command} in ${repoPath}`)

    const { stdout, stderr } = await execAsync(command, {
      cwd: repoPath,
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer for large diffs
      env: { ...process.env, LANG: 'en_US.UTF-8' } // Ensure consistent output
    })

    return NextResponse.json({
      success: true,
      output: stdout,
      error: stderr
    })
  } catch (error: any) {
    console.error('[Git] Error:', error)

    return NextResponse.json({
      success: false,
      error: error.message,
      output: error.stdout || '',
      stderr: error.stderr || ''
    }, { status: 500 })
  }
}
