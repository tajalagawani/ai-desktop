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

    console.log(`[API] Starting code-server for repository: ${repoId}`)

    // Get repository from registry
    const repo = repoManager.getRepository(repoId)
    if (!repo) {
      return NextResponse.json({ error: 'Repository not found' }, { status: 404 })
    }

    console.log(`[API] Repository details:`, {
      id: repo.id,
      name: repo.name,
      path: repo.path,
      type: repo.type
    })

    // Check if code-server is installed
    if (!codeServerManager.isInstalled()) {
      return NextResponse.json({
        error: 'code-server is not installed. Please install it first.',
        installUrl: 'https://github.com/coder/code-server#install'
      }, { status: 503 })
    }

    // Check if already running
    const existingInstance = portManager.getInstance(repo.id)
    if (existingInstance && codeServerManager.isRunning(existingInstance.pid)) {
      const safeName = repo.id
      console.log(`[API] Instance already running for ${repo.id}`)
      return NextResponse.json({
        message: 'Instance already running',
        url: `/vscode/${safeName}/`,
        port: existingInstance.port,
        pid: existingInstance.pid
      })
    }

    // If instance exists in port DB but process is dead, clean it up
    if (existingInstance && !codeServerManager.isRunning(existingInstance.pid)) {
      console.log(`[API] Cleaning up dead instance for ${repo.id}`)
      portManager.releasePort(repo.id)
      repoManager.markVSCodeStopped(repo.id)
    }

    // Allocate port
    const port = portManager.allocatePort(repo.id)
    if (!port) {
      return NextResponse.json({
        error: 'No available ports. Maximum 12 concurrent VS Code instances allowed.',
        hint: 'Please stop an existing instance before starting a new one.'
      }, { status: 503 })
    }

    console.log(`[API] Allocated port ${port} for ${repo.id}`)

    // Start code-server
    let pid: number
    try {
      const result = await codeServerManager.startServer(repo.name, repo.path, port)
      pid = result.pid
      console.log(`[API] code-server started with PID ${pid}`)
    } catch (error: any) {
      // Rollback port allocation
      portManager.releasePort(repo.id)
      throw new Error(`Failed to start code-server: ${error.message}`)
    }

    // Register instance in port manager
    portManager.registerInstance(repo.id, port, pid, repo.path)

    // Generate and write Nginx config with repository path
    try {
      nginxManager.writeConfig(repo.id, port, repo.path)
      console.log(`[API] Nginx config written for ${repo.id} with path ${repo.path}`)
    } catch (error: any) {
      // Rollback: stop code-server and release port
      codeServerManager.stopServer(repo.id, pid)
      portManager.releasePort(repo.id)
      throw new Error(`Failed to write Nginx config: ${error.message}`)
    }

    // Reload Nginx
    const reloaded = nginxManager.reload()
    if (!reloaded) {
      // Rollback: stop code-server, remove config, release port
      codeServerManager.stopServer(repo.id, pid)
      nginxManager.removeConfig(repo.id)
      portManager.releasePort(repo.id)
      return NextResponse.json({
        error: 'Nginx reload failed. Please check Nginx configuration.',
        hint: 'Run "sudo nginx -t" to see the error.'
      }, { status: 500 })
    }

    console.log(`[API] Nginx reloaded successfully`)

    // Update repository registry
    repoManager.markVSCodeRunning(repo.id, port)

    const safeName = repo.id
    const hostname = request.headers.get('host') || 'localhost'

    return NextResponse.json({
      success: true,
      message: 'code-server started successfully',
      url: `/vscode/${safeName}/`,
      fullUrl: `http://${hostname}/vscode/${safeName}/`,
      port,
      pid,
      repository: repo
    })

  } catch (error: any) {
    console.error('[API] Start error:', error)
    return NextResponse.json({
      error: error.message || 'Failed to start code-server',
      details: error.stack
    }, { status: 500 })
  }
}
