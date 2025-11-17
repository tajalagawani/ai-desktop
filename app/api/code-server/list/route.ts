import { NextResponse } from 'next/server'
import { PortManager } from '@/lib/vscode/port-manager'
import { CodeServerManager } from '@/lib/vscode/code-server-manager'
import { RepositoryManager } from '@/lib/repositories/registry'

export const dynamic = 'force-dynamic'

const portManager = new PortManager()
const codeServerManager = new CodeServerManager()
const repoManager = new RepositoryManager()

export async function GET() {
  try {
    const instances = portManager.getAllInstances()

    // Check which instances are actually running and enrich with repository info
    const activeInstances = instances.map(instance => {
      const isRunning = codeServerManager.isRunning(instance.pid)
      const repo = repoManager.getRepository(instance.projectName)
      const safeName = instance.projectName.replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase()

      return {
        ...instance,
        isRunning,
        url: `/vscode/${safeName}/`,
        repository: repo
      }
    })

    // Count running instances
    const runningCount = activeInstances.filter(i => i.isRunning).length

    // Get system-wide running code-server processes
    const systemInstances = codeServerManager.findRunningInstances()

    return NextResponse.json({
      success: true,
      instances: activeInstances,
      total: activeInstances.length,
      running: runningCount,
      systemInstances: systemInstances.length,
      maxInstances: 12
    })

  } catch (error: any) {
    console.error('[API] List error:', error)
    return NextResponse.json({
      error: error.message || 'Failed to list instances',
      details: error.stack
    }, { status: 500 })
  }
}
