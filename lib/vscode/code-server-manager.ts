import { spawn, ChildProcess, execSync } from 'child_process'
import fs from 'fs'

export class CodeServerManager {
  private processes: Map<string, ChildProcess> = new Map()

  /**
   * Start a code-server instance for a project
   */
  async startServer(
    projectName: string,
    repoPath: string,
    port: number
  ): Promise<{ pid: number; port: number }> {
    const safeName = projectName.replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase()

    console.log(`[code-server] ====================================`)
    console.log(`[code-server] Starting server for ${projectName}`)
    console.log(`[code-server] Repository Path: "${repoPath}"`)
    console.log(`[code-server] Repository Path Length: ${repoPath?.length || 0}`)
    console.log(`[code-server] Port: ${port}`)
    console.log(`[code-server] ====================================")`)

    // Verify repository path exists
    if (!repoPath || !fs.existsSync(repoPath)) {
      throw new Error(`Repository path does not exist: ${repoPath}`)
    }

    // Extra safety: verify this is not /var/www root
    if (repoPath === '/var/www' || repoPath === '/var/www/') {
      throw new Error(`Invalid repository path - cannot open /var/www root directory. Path must be a specific repository like /var/www/github/repo-name`)
    }

    // Log directory contents to verify we're opening the right folder
    try {
      const files = fs.readdirSync(repoPath).slice(0, 5)
      console.log(`[code-server] First 5 files in ${repoPath}:`, files)
    } catch (err) {
      console.error(`[code-server] Could not read directory:`, err)
    }

    // Check if code-server is installed
    try {
      execSync('which code-server', { stdio: 'pipe' })
    } catch {
      throw new Error('code-server is not installed. Please install it first.')
    }

    // Start code-server directly on the repository path (no copying/syncing)
    const userDataDir = `/tmp/code-server-userdata-${safeName}-${port}`
    const extensionsDir = `/tmp/code-server-extensions-${safeName}-${port}`

    console.log(`[code-server] User data dir: ${userDataDir}`)
    console.log(`[code-server] Extensions dir: ${extensionsDir}`)
    console.log(`[code-server] Spawning code-server with args:`, [
      repoPath,
      '--bind-addr', `127.0.0.1:${port}`,
      '--auth', 'none',
      '--disable-telemetry',
      '--disable-update-check',
      '--disable-workspace-trust',
      '--user-data-dir', userDataDir,
      '--extensions-dir', extensionsDir,
    ])

    const codeServer = spawn('code-server', [
      repoPath,
      '--bind-addr', `127.0.0.1:${port}`,
      '--auth', 'none',
      '--disable-telemetry',
      '--disable-update-check',
      '--disable-workspace-trust',
      '--user-data-dir', userDataDir,
      '--extensions-dir', extensionsDir,
    ], {
      detached: true,
      stdio: ['ignore', 'pipe', 'pipe'],
      cwd: repoPath,
      env: {
        ...process.env,
        DONT_PROMPT_WSL_INSTALL: '1',
        VSCODE_AGENT_FOLDER: `/tmp/vscode-agent-${safeName}-${port}`,
      }
    })

    codeServer.unref()

    if (!codeServer.pid) {
      throw new Error('Failed to start code-server - no PID')
    }

    this.processes.set(projectName, codeServer)

    console.log(`[code-server] Started for ${projectName} on port ${port} (PID: ${codeServer.pid})`)

    // Wait for server to be ready (check if port is listening)
    await this.waitForPort(port, 30000)

    return {
      pid: codeServer.pid,
      port
    }
  }

  /**
   * Stop a code-server instance
   */
  stopServer(projectName: string, pid: number): void {
    try {
      // Kill the process
      process.kill(pid, 'SIGTERM')

      // Remove from tracking
      this.processes.delete(projectName)

      console.log(`[code-server] Stopped ${projectName} (PID: ${pid})`)
    } catch (error: any) {
      console.error(`[code-server] Failed to stop ${projectName}:`, error.message)

      // Try forceful kill
      try {
        process.kill(pid, 'SIGKILL')
        this.processes.delete(projectName)
        console.log(`[code-server] Force killed ${projectName} (PID: ${pid})`)
      } catch {
        console.error(`[code-server] Process ${pid} may not exist`)
      }
    }
  }

  /**
   * Check if a process is running
   */
  isRunning(pid: number): boolean {
    try {
      // Signal 0 checks if process exists without actually sending a signal
      process.kill(pid, 0)
      return true
    } catch {
      return false
    }
  }

  /**
   * Get process info by project name
   */
  getProcess(projectName: string): ChildProcess | undefined {
    return this.processes.get(projectName)
  }

  /**
   * Wait for a port to become available
   */
  private async waitForPort(port: number, timeout: number): Promise<void> {
    const startTime = Date.now()

    while (Date.now() - startTime < timeout) {
      try {
        // Try to connect to the port
        execSync(`nc -z 127.0.0.1 ${port}`, { stdio: 'pipe' })
        console.log(`[code-server] Port ${port} is now open`)
        return // Port is open
      } catch {
        // Port not ready yet, wait and retry
        await new Promise(resolve => setTimeout(resolve, 500))
      }
    }

    throw new Error(`Timeout waiting for port ${port} to open after ${timeout}ms`)
  }

  /**
   * Find all running code-server processes on the system
   */
  findRunningInstances(): Array<{ pid: number; port: number }> {
    try {
      const output = execSync('ps aux | grep code-server | grep -v grep', { encoding: 'utf-8' })
      const lines = output.trim().split('\n').filter(l => l.length > 0)

      const instances: Array<{ pid: number; port: number }> = []

      for (const line of lines) {
        const parts = line.trim().split(/\s+/)
        const pid = parseInt(parts[1], 10)

        // Extract port from command line args
        const portMatch = line.match(/--bind-addr\s+[^:]+:(\d+)/)
        if (portMatch) {
          const port = parseInt(portMatch[1], 10)
          instances.push({ pid, port })
        }
      }

      return instances
    } catch {
      return []
    }
  }

  /**
   * Check if code-server is installed
   */
  isInstalled(): boolean {
    try {
      execSync('which code-server', { stdio: 'pipe' })
      return true
    } catch {
      return false
    }
  }
}
