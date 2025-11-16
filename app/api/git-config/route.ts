import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

export const dynamic = 'force-dynamic'

const execAsync = promisify(exec)

export async function POST(request: NextRequest) {
  try {
    const { userName, userEmail } = await request.json()

    if (!userName || !userEmail) {
      return NextResponse.json(
        { success: false, error: 'userName and userEmail are required' },
        { status: 400 }
      )
    }

    // Set global git config
    await execAsync(`git config --global user.name "${userName}"`)
    await execAsync(`git config --global user.email "${userEmail}"`)

    return NextResponse.json({
      success: true,
      message: 'Git config updated successfully'
    })
  } catch (error: any) {
    console.error('[Git Config] Error:', error)

    return NextResponse.json({
      success: false,
      error: error.message
    }, { status: 500 })
  }
}
