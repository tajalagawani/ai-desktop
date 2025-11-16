import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export async function POST(request: NextRequest) {
  try {
    const { method } = await request.json()

    let installCommand: string

    switch (method) {
      case 'script':
        installCommand = 'curl -fsSL https://code-server.dev/install.sh | sh'
        break
      case 'homebrew':
        installCommand = 'brew install code-server'
        break
      case 'npm':
        installCommand = 'npm install -g code-server'
        break
      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid installation method'
        }, { status: 400 })
    }

    // Run installation in background and stream output
    const { stdout, stderr } = await execAsync(installCommand, {
      timeout: 300000, // 5 minutes timeout
      maxBuffer: 10 * 1024 * 1024 // 10MB buffer
    })

    // Verify installation
    try {
      await execAsync('which code-server')

      return NextResponse.json({
        success: true,
        message: 'code-server installed successfully!',
        output: stdout,
        method
      })
    } catch (error) {
      return NextResponse.json({
        success: false,
        error: 'Installation completed but code-server not found in PATH',
        output: stdout,
        stderr: stderr
      }, { status: 500 })
    }

  } catch (error: any) {
    console.error('Installation error:', error)
    return NextResponse.json({
      success: false,
      error: error.message || 'Installation failed',
      stderr: error.stderr
    }, { status: 500 })
  }
}
