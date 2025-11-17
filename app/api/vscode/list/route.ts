import { NextResponse } from 'next/server'
import { VSCodeManager } from '@/lib/vscode/manager'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const manager = new VSCodeManager()
    const repositories = await manager.getAllRepositories()

    return NextResponse.json({
      success: true,
      repositories
    })
  } catch (error: any) {
    console.error('[API] Failed to list repositories:', error)
    return NextResponse.json({
      success: false,
      error: error.message || 'Failed to list repositories'
    }, { status: 500 })
  }
}
