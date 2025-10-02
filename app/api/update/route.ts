import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export async function POST() {
  try {
    // Execute the auto-update script
    const scriptPath = '/var/www/ai-desktop/deployment/auto-update.sh'

    const { stdout, stderr } = await execAsync(`bash ${scriptPath}`)

    return NextResponse.json({
      success: true,
      message: 'Update triggered successfully',
      output: stdout,
      errors: stderr || null,
    })
  } catch (error: any) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to trigger update',
        message: error.message
      },
      { status: 500 }
    )
  }
}
