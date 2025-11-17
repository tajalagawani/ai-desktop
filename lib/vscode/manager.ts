import { spawn, execSync } from 'child_process'
import fs from 'fs'
import path from 'path'
import { VSCODE_CONFIG } from './config'
import { RepositoryManager } from '@/lib/repositories/registry'
import type { VSCodeRepository, RunningInstance, StartResult, StopResult, StatusResult } from './types'

export class VSCodeManager {
  private repoManager: RepositoryManager

  constructor() {
    this.repoManager = new RepositoryManager()
  }

  /**
   * Get all running code-server instances from system processes
   */
  async getRunningInstances(): Promise<RunningInstance[]> {
    try {
      const output = execSync('ps aux | grep code-server | grep -v grep', { encoding: 'utf-8' })
      const lines = output.trim().split('\n').filter(l => l.length > 0)

      const instances: RunningInstance[] = []

      for (const line of lines) {
        const parts = line.trim().split(/\s+/)
        const pid = parseInt(parts[1], 10)
        const cpu = parts[2]
        const memory = parts[3]
        const command = parts.slice(10).join(' ')

        // Extract port from command: --bind-addr 127.0.0.1:8880
        let port = 0
        const portMatch = command.match(/--bind-addr\s+[^:]+:(\d+)/)
        if (portMatch) {
          port = parseInt(portMatch[1], 10)
        }

        // Extract repository path from command (first argument after code-server)
        let repoPath = ''
        const pathMatch = command.match(/code-server\s+([^\s]+)/)
        if (pathMatch) {
          repoPath = pathMatch[1]
        }

        // Try to match to a known repository
        let repoId: string | undefined
        if (repoPath) {
          const repo = this.repoManager.getRepository(repoPath)
          if (repo) {
            repoId = repo.id
          }
        }

        instances.push({
          pid,
          port,
          repoPath,
          repoId,
          cpu,
          memory: `${memory}%`,
          uptime: this.calculateUptime(pid),
          command
        })
      }

      return instances
    } catch {
      // No processes found or error running ps
      return []
    }
  }

  /**
   * Calculate process uptime from PID
   */
  private calculateUptime(pid: number): string {
    try {
      const output = execSync(`ps -o etime= -p ${pid}`, { encoding: 'utf-8' })
      return output.trim()
    } catch {
      return 'Unknown'
    }
  }

  /**
   * Find next available port in the range
   */
  private async findAvailablePort(): Promise<number | null> {
    const runningInstances = await this.getRunningInstances()
    const usedPorts = runningInstances.map(i => i.port)

    for (let port = VSCODE_CONFIG.PORT_RANGE_START; port <= VSCODE_CONFIG.PORT_RANGE_END; port++) {
      if (!usedPorts.includes(port)) {
        return port
      }
    }

    return null // All ports in use
  }

  /**
   * Get all repositories with their code-server status
   */
  async getAllRepositories(): Promise<VSCodeRepository[]> {
    const repos = this.repoManager.getAllRepositories()
    const runningInstances = await this.getRunningInstances()

    return repos.map(repo => {
      // Find if this repo has a running instance
      const instance = runningInstances.find(i => i.repoId === repo.id || i.repoPath === repo.path)

      return {
        id: repo.id,
        name: repo.name,
        path: repo.path,
        type: repo.type,
        branch: repo.branch,
        addedAt: repo.addedAt,
        running: !!instance,
        port: instance?.port || null,
        pid: instance?.pid || null,
        url: instance ? `${VSCODE_CONFIG.BASE_URL_PATH}/${repo.id}/` : null,
        uptime: instance?.uptime || null,
      }
    })
  }

  /**
   * Get status of a specific repository
   */
  async getRepositoryStatus(repoId: string): Promise<VSCodeRepository | null> {
    const repos = await this.getAllRepositories()
    return repos.find(r => r.id === repoId) || null
  }

  /**
   * Wait for a port to become available
   */
  private async waitForPort(port: number, timeout: number): Promise<void> {
    const net = require('net')
    const startTime = Date.now()

    while (Date.now() - startTime < timeout) {
      try {
        await new Promise<void>((resolve, reject) => {
          const client = new net.Socket()
          client.setTimeout(1000)

          client.on('connect', () => {
            client.destroy()
            resolve()
          })

          client.on('timeout', () => {
            client.destroy()
            reject(new Error('Timeout'))
          })

          client.on('error', (err: any) => {
            client.destroy()
            reject(err)
          })

          client.connect(port, '127.0.0.1')
        })

        console.log(`[VSCode] Port ${port} is now open`)
        return // Port is open
      } catch {
        // Port not ready yet, wait and retry
        await new Promise(resolve => setTimeout(resolve, VSCODE_CONFIG.PORT_CHECK_INTERVAL))
      }
    }

    throw new Error(`Timeout waiting for port ${port} to open after ${timeout}ms`)
  }

  /**
   * Generate Nginx configuration for a repository
   */
  private generateNginxConfig(repoId: string, port: number, repoPath: string): string {
    const safeName = repoId.replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase()

    return `# Auto-generated config for repository: ${repoId}
# Generated at: ${new Date().toISOString()}
# Port: ${port}
# Path: ${repoPath}

location ${VSCODE_CONFIG.BASE_URL_PATH}/${safeName}/ {
    proxy_pass http://127.0.0.1:${port}/;
    proxy_http_version 1.1;

    # WebSocket support (CRITICAL for VS Code)
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_cache_bypass $http_upgrade;

    # Headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Timeouts for long-running operations
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;

    # Allow large file uploads
    client_max_body_size 500M;
}
`
  }

  /**
   * Write Nginx configuration file
   */
  private async writeNginxConfig(repoId: string, config: string): Promise<void> {
    const safeName = repoId.replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase()
    const configPath = path.join(VSCODE_CONFIG.NGINX_CONFIG_DIR, `${safeName}.conf`)

    try {
      // Ensure directory exists
      if (!fs.existsSync(VSCODE_CONFIG.NGINX_CONFIG_DIR)) {
        console.log(`[VSCode] Creating Nginx config directory: ${VSCODE_CONFIG.NGINX_CONFIG_DIR}`)
        fs.mkdirSync(VSCODE_CONFIG.NGINX_CONFIG_DIR, { recursive: true })
      }

      fs.writeFileSync(configPath, config, 'utf-8')
      console.log(`[VSCode] Nginx config written: ${configPath}`)
    } catch (error) {
      console.error('[VSCode] Failed to write Nginx config:', error)
      throw error
    }
  }

  /**
   * Remove Nginx configuration file
   */
  private async removeNginxConfig(repoId: string): Promise<void> {
    const safeName = repoId.replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase()
    const configPath = path.join(VSCODE_CONFIG.NGINX_CONFIG_DIR, `${safeName}.conf`)

    try {
      if (fs.existsSync(configPath)) {
        fs.unlinkSync(configPath)
        console.log(`[VSCode] Nginx config removed: ${configPath}`)
      }
    } catch (error) {
      console.error('[VSCode] Failed to remove Nginx config:', error)
      throw error
    }
  }

  /**
   * Reload Nginx to apply configuration changes
   */
  private async reloadNginx(): Promise<void> {
    try {
      // Test config first
      execSync('nginx -t', { stdio: 'pipe' })
      console.log('[VSCode] Nginx config test passed')

      // Reload Nginx
      execSync('systemctl reload nginx', { stdio: 'pipe' })
      console.log('[VSCode] Nginx reloaded successfully')
    } catch (error: any) {
      console.error('[VSCode] Nginx reload failed:', error.message)
      throw new Error(`Failed to reload Nginx: ${error.message}`)
    }
  }

  /**
   * Check if code-server is installed
   */
  isCodeServerInstalled(): boolean {
    try {
      execSync('which code-server', { stdio: 'pipe' })
      return true
    } catch {
      return false
    }
  }

  /**
   * Start code-server for a repository
   */
  async startCodeServer(repoId: string): Promise<StartResult> {
    console.log(`[VSCode] ====================================`)
    console.log(`[VSCode] Starting code-server for ${repoId}`)

    // 1. Get repository info
    const repo = this.repoManager.getRepository(repoId)
    if (!repo) {
      throw new Error(`Repository not found: ${repoId}`)
    }

    console.log(`[VSCode] Repository path: ${repo.path}`)

    // 2. Verify repository path exists
    if (!fs.existsSync(repo.path)) {
      throw new Error(`Repository path does not exist: ${repo.path}`)
    }

    // 3. Check if code-server is installed
    if (!this.isCodeServerInstalled()) {
      throw new Error('code-server is not installed. Please install it first.')
    }

    // 4. Check if already running
    const existing = await this.getRepositoryStatus(repoId)
    if (existing?.running) {
      console.log(`[VSCode] Already running on port ${existing.port}`)
      return {
        success: true,
        url: existing.url!,
        port: existing.port!,
        pid: existing.pid!,
        message: 'Code server is already running'
      }
    }

    // 5. Find available port
    const port = await this.findAvailablePort()
    if (!port) {
      throw new Error('No available ports. Maximum instances reached.')
    }

    console.log(`[VSCode] Allocated port: ${port}`)

    // 6. Create temporary config file to override default config
    const tempConfigPath = `/tmp/code-server-config-${port}.yaml`
    const configContent = `bind-addr: 127.0.0.1:${port}
auth: none
disable-telemetry: true
disable-update-check: true
`
    fs.writeFileSync(tempConfigPath, configContent, 'utf-8')
    console.log(`[VSCode] Wrote temp config: ${tempConfigPath}`)

    // 7. Start code-server process with custom config
    const args = [
      `--config=${tempConfigPath}`,
      '--disable-workspace-trust',
      repo.path,
    ]

    console.log(`[VSCode] Starting code-server with args:`, args)

    const codeServer = spawn('code-server', args, {
      detached: true,
      stdio: ['ignore', 'pipe', 'pipe'],
      cwd: repo.path,
      env: {
        ...process.env,
        DONT_PROMPT_WSL_INSTALL: '1',
        CODE_SERVER_BIND_ADDR: `127.0.0.1:${port}`, // Also set via env var
      }
    })

    // Log stdout and stderr for debugging
    codeServer.stdout?.on('data', (data) => {
      console.log(`[VSCode][stdout] ${data.toString()}`)
    })

    codeServer.stderr?.on('data', (data) => {
      console.error(`[VSCode][stderr] ${data.toString()}`)
    })

    codeServer.on('error', (error) => {
      console.error(`[VSCode] Process error:`, error)
    })

    codeServer.on('exit', (code, signal) => {
      console.log(`[VSCode] Process exited with code ${code}, signal ${signal}`)
    })

    codeServer.unref()

    if (!codeServer.pid) {
      throw new Error('Failed to start code-server - no PID')
    }

    console.log(`[VSCode] Process started with PID: ${codeServer.pid}`)

    // 7. Generate and write Nginx config
    const nginxConfig = this.generateNginxConfig(repoId, port, repo.path)
    await this.writeNginxConfig(repoId, nginxConfig)

    // 8. Reload Nginx
    await this.reloadNginx()

    // 9. Wait for port to open
    console.log(`[VSCode] Waiting for port ${port} to open...`)
    await this.waitForPort(port, VSCODE_CONFIG.STARTUP_TIMEOUT)

    const url = `${VSCODE_CONFIG.BASE_URL_PATH}/${repoId}/`
    console.log(`[VSCode] Code server started successfully!`)
    console.log(`[VSCode] URL: ${url}`)
    console.log(`[VSCode] ====================================`)

    return {
      success: true,
      url,
      port,
      pid: codeServer.pid,
      message: 'Code server started successfully'
    }
  }

  /**
   * Stop code-server for a repository
   */
  async stopCodeServer(repoId: string): Promise<StopResult> {
    console.log(`[VSCode] Stopping code-server for ${repoId}`)

    // 1. Get current status
    const status = await this.getRepositoryStatus(repoId)
    if (!status?.running || !status.pid) {
      return {
        success: true,
        message: 'Code server is not running'
      }
    }

    // 2. Kill the process
    try {
      process.kill(status.pid, 'SIGTERM')
      console.log(`[VSCode] Sent SIGTERM to PID ${status.pid}`)

      // Give it 5 seconds to gracefully shutdown
      await new Promise(resolve => setTimeout(resolve, 5000))

      // Check if still running, force kill if needed
      try {
        process.kill(status.pid, 0) // Check if process exists
        console.log(`[VSCode] Process still running, sending SIGKILL`)
        process.kill(status.pid, 'SIGKILL')
      } catch {
        // Process already dead
      }
    } catch (error: any) {
      console.error(`[VSCode] Error killing process:`, error.message)
    }

    // 3. Remove Nginx config
    await this.removeNginxConfig(repoId)

    // 4. Reload Nginx
    await this.reloadNginx()

    console.log(`[VSCode] Code server stopped successfully`)

    return {
      success: true,
      message: 'Code server stopped successfully'
    }
  }

  /**
   * Get overall status of all instances
   */
  async getStatus(): Promise<StatusResult> {
    const instances = await this.getRunningInstances()
    const usedPorts = instances.length
    const availablePorts = VSCODE_CONFIG.MAX_INSTANCES - usedPorts

    return {
      instances,
      totalRunning: instances.length,
      availablePorts
    }
  }
}
