import { NextRequest, NextResponse } from 'next/server'
import { PortManager } from '@/lib/vscode/port-manager'
import { NginxConfigManager } from '@/lib/vscode/nginx-config'
import { CodeServerManager } from '@/lib/vscode/code-server-manager'
import { RepositoryManager } from '@/lib/repositories/registry'

export const dynamic = 'force-dynamic'

const portManager = new PortManager()
const nginxManager = new NginxConfigManager()
const codeServerManager = new CodeServerManager()
const repoManager = new RepositoryManager()

export async function POST(request: NextRequest) {
  try {
    const { repoId } = await request.json()

    if (!repoId) {
      return NextResponse.json({ error: 'Repository ID is required' }, { status: 400 })
    }

    console.log(`[API] Stopping code-server for repository: ${repoId}`)

    // Get instance info
    const instance = portManager.getInstance(repoId)
    if (!instance) {
      return NextResponse.json({
        error: 'Instance not found',
        hint: 'This code-server instance may have already been stopped.'
      }, { status: 404 })
    }

    // Stop code-server process
    codeServerManager.stopServer(repoId, instance.pid)
    console.log(`[API] code-server process stopped`)

    // Remove Nginx config
    try {
      nginxManager.removeConfig(repoId)
      console.log(`[API] Nginx config removed`)
    } catch (error: any) {
      console.error('[API] Failed to remove Nginx config:', error)
      // Continue anyway
    }

    // Reload Nginx
    const reloaded = nginxManager.reload()
    if (!reloaded) {
      console.warn('[API] Nginx reload failed after removing config')
      // Continue anyway, port cleanup is more important
    } else {
      console.log(`[API] Nginx reloaded`)
    }

    // Release port
    portManager.releasePort(repoId)
    console.log(`[API] Port released`)

    // Update repository registry
    repoManager.markVSCodeStopped(repoId)
    console.log(`[API] Repository registry updated`)

    return NextResponse.json({
      success: true,
      message: 'code-server stopped successfully',
      repoId
    })

  } catch (error: any) {
    console.error('[API] Stop error:', error)
    return NextResponse.json({
      error: error.message || 'Failed to stop code-server',
      details: error.stack
    }, { status: 500 })
  }
}
