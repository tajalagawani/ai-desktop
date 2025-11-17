import { NextRequest, NextResponse } from 'next/server'
import { execSync } from 'child_process'
import { PortManager } from '@/lib/vscode/port-manager'
import { RepositoryManager } from '@/lib/repositories/registry'

export const dynamic = 'force-dynamic'

const portManager = new PortManager()
const repoManager = new RepositoryManager()

export async function POST(request: NextRequest) {
  try {
    const { action, pid } = await request.json()

    if (action === 'kill-all') {
      // Kill ALL code-server processes
      try {
        execSync('pkill -9 code-server', { stdio: 'pipe' })
        console.log('[Cleanup] Killed all code-server processes')
      } catch (error) {
        // Ignore error if no processes found
      }

      // Clean up temporary directories
      try {
        execSync('rm -rf /tmp/code-server-*', { stdio: 'pipe' })
        execSync('rm -rf /tmp/vscode-agent-*', { stdio: 'pipe' })
        console.log('[Cleanup] Removed temporary directories')
      } catch (error) {
        console.error('[Cleanup] Failed to remove temp dirs:', error)
      }

      // Clean up all port allocations
      const instances = portManager.getAllInstances()
      for (const instance of instances) {
        portManager.releasePort(instance.projectName)
      }

      // Mark all repos as stopped
      const repos = repoManager.getAllRepositories()
      for (const repo of repos) {
        if (repo.vscodeRunning) {
          repoManager.markVSCodeStopped(repo.id)
        }
      }

      return NextResponse.json({
        success: true,
        message: 'All code-server processes killed and cleaned up'
      })
    }

    if (action === 'kill-pid' && pid) {
      // Kill specific PID
      try {
        process.kill(pid, 'SIGKILL')
        console.log(`[Cleanup] Killed process ${pid}`)

        // Try to find and clean up port allocation
        const instances = portManager.getAllInstances()
        for (const instance of instances) {
          if (instance.pid === pid) {
            portManager.releasePort(instance.projectName)
            repoManager.markVSCodeStopped(instance.projectName)
            break
          }
        }

        return NextResponse.json({
          success: true,
          message: `Process ${pid} killed`
        })
      } catch (error: any) {
        return NextResponse.json({
          success: false,
          error: `Failed to kill process ${pid}: ${error.message}`
        }, { status: 400 })
      }
    }

    if (action === 'list-processes') {
      // List all code-server processes
      try {
        const output = execSync('ps aux | grep code-server | grep -v grep', { encoding: 'utf-8' })
        const lines = output.trim().split('\n').filter(l => l.length > 0)

        const processes = lines.map(line => {
          const parts = line.trim().split(/\s+/)
          const pid = parseInt(parts[1], 10)
          const cpu = parts[2]
          const mem = parts[3]
          const command = parts.slice(10).join(' ')

          // Extract port from command
          let port = null
          const portMatch = command.match(/--port[=\s]+(\d+)|:(\d+)/)
          if (portMatch) {
            port = parseInt(portMatch[1] || portMatch[2], 10)
          }

          return { pid, cpu, mem, port, command }
        })

        return NextResponse.json({
          success: true,
          processes
        })
      } catch (error) {
        // No processes found
        return NextResponse.json({
          success: true,
          processes: []
        })
      }
    }

    return NextResponse.json({
      error: 'Invalid action'
    }, { status: 400 })

  } catch (error: any) {
    console.error('[Cleanup] Error:', error)
    return NextResponse.json({
      error: error.message || 'Cleanup failed'
    }, { status: 500 })
  }
}
