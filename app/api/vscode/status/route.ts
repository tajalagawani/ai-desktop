import { NextResponse } from 'next/server'
import { VSCodeManager } from '@/lib/vscode/manager'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const manager = new VSCodeManager()
    const status = await manager.getStatus()

    return NextResponse.json({
      success: true,
      ...status
    })
  } catch (error: any) {
    console.error('[API] Failed to get status:', error)
    return NextResponse.json({
      success: false,
      error: error.message || 'Failed to get status'
    }, { status: 500 })
  }
}
