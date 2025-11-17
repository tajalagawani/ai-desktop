import { NextRequest, NextResponse } from 'next/server'
import { VSCodeManager } from '@/lib/vscode/manager'

export const dynamic = 'force-dynamic'

export async function POST(request: NextRequest) {
  try {
    const { repoId } = await request.json()

    if (!repoId) {
      return NextResponse.json({
        success: false,
        error: 'Repository ID is required'
      }, { status: 400 })
    }

    console.log(`[API] Starting code-server for: ${repoId}`)

    const manager = new VSCodeManager()
    const result = await manager.startCodeServer(repoId)

    return NextResponse.json(result)
  } catch (error: any) {
    console.error('[API] Failed to start code-server:', error)
    return NextResponse.json({
      success: false,
      error: error.message || 'Failed to start code-server'
    }, { status: 500 })
  }
}
