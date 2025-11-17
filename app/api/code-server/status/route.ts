import { NextRequest, NextResponse } from 'next/server'
import { PortManager } from '@/lib/vscode/port-manager'
import { CodeServerManager } from '@/lib/vscode/code-server-manager'
import { NginxConfigManager } from '@/lib/vscode/nginx-config'
import { RepositoryManager } from '@/lib/repositories/registry'

export const dynamic = 'force-dynamic'

const portManager = new PortManager()
const codeServerManager = new CodeServerManager()
const nginxManager = new NginxConfigManager()
const repoManager = new RepositoryManager()

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const repoId = searchParams.get('repoId')

    if (repoId) {
      // Get status for specific repository
      const instance = portManager.getInstance(repoId)
      const repo = repoManager.getRepository(repoId)

      if (!instance) {
        return NextResponse.json({
          success: true,
          repoId,
          running: false,
          repository: repo
        })
      }

      const isRunning = codeServerManager.isRunning(instance.pid)
      const safeName = repoId.replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase()

      return NextResponse.json({
        success: true,
        repoId,
        running: isRunning,
        port: instance.port,
        pid: instance.pid,
        url: `/vscode/${safeName}/`,
        startedAt: instance.startedAt,
        repository: repo
      })
    }

    // General status (no specific repo)
    const nginxStatus = nginxManager.checkNginxStatus()
    const codeServerInstalled = codeServerManager.isInstalled()
    const instances = portManager.getAllInstances()
    const runningCount = instances.filter(i => codeServerManager.isRunning(i.pid)).length

    return NextResponse.json({
      success: true,
      nginx: nginxStatus,
      codeServer: {
        installed: codeServerInstalled,
        instances: instances.length,
        running: runningCount
      },
      system: {
        maxInstances: 12,
        availablePorts: 12 - instances.length
      }
    })

  } catch (error: any) {
    console.error('[API] Status error:', error)
    return NextResponse.json({
      error: error.message || 'Failed to get status',
      details: error.stack
    }, { status: 500 })
  }
}
