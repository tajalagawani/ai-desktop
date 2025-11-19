/**
 * VS Code Manager API Routes
 * Handles code-server instances and repositories
 * Storage: data/repositories.json
 */

const express = require('express')
const router = express.Router()
const { readJSON, writeJSON, getDataPath } = require('../../lib/json-storage')

const REPOS_FILE = getDataPath('repositories.json')

/**
 * Get all repositories from JSON file
 */
async function getRepositories() {
  const data = await readJSON(REPOS_FILE)
  return data?.repositories || []
}

/**
 * Save repositories to JSON file
 */
async function saveRepositories(repositories) {
  await writeJSON(REPOS_FILE, { repositories })
}

/**
 * GET /api/vscode/status
 * Get status of all code-server instances
 */
router.get('/status', async (req, res) => {
  try {
    const repositories = await getRepositories()

    const status = {
      repositories,
      deployments: [],
      flows: []
    }

    res.json({
      success: true,
      ...status
    })
  } catch (error) {
    console.error('[API] Failed to get status:', error)
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to get status'
    })
  }
})

/**
 * POST /api/vscode/start
 * Start a code-server instance
 */
router.post('/start', async (req, res) => {
  try {
    const { repoId } = req.body

    if (!repoId) {
      return res.status(400).json({
        success: false,
        error: 'Repository ID is required'
      })
    }

    const { spawn } = require('child_process')

    const repositories = await getRepositories()

    // Get repository details
    const repoIndex = repositories.findIndex(r => r.id === parseInt(repoId))
    if (repoIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Repository not found'
      })
    }

    const repo = repositories[repoIndex]

    // Check if already running
    if (repo.running && repo.pid) {
      try {
        process.kill(repo.pid, 0) // Check if process exists
        return res.json({
          success: true,
          message: 'Code-server already running',
          url: repo.url,
          port: repo.port
        })
      } catch {
        // Process doesn't exist, continue with start
      }
    }

    console.log(`[VSCode] Starting code-server for ${repo.name} on port ${repo.port}`)
    console.log(`[VSCode] Repository path: ${repo.path}`)

    // Check if path exists
    const fs = require('fs').promises
    try {
      await fs.access(repo.path)
    } catch (error) {
      throw new Error(`Repository path does not exist: ${repo.path}`)
    }

    // Start code-server with explicit config to override defaults
    const codeServer = spawn('code-server', [
      '--bind-addr', `127.0.0.1:${repo.port}`,
      '--auth', 'none',
      '--disable-telemetry',
      '--disable-update-check',
      '--ignore-last-opened',
      '--config', '/dev/null',  // Ignore config file
      '--user-data-dir', `/tmp/code-server-${repo.port}`,  // Use temp dir to avoid config conflicts
      repo.path
    ], {
      detached: true,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: {
        ...process.env,
        PASSWORD: undefined,  // Clear any password env var
        PORT: undefined,  // Clear any port env var
        VSCODE_PROXY_URI: undefined  // Clear proxy settings
      }
    })

    // Log output for debugging
    codeServer.stdout.on('data', (data) => {
      console.log(`[VSCode ${repo.port}] ${data.toString().trim()}`)
    })

    codeServer.stderr.on('data', (data) => {
      console.error(`[VSCode ${repo.port}] ERROR: ${data.toString().trim()}`)
    })

    codeServer.on('error', (error) => {
      console.error(`[VSCode ${repo.port}] Failed to start:`, error)
    })

    codeServer.on('exit', async (code, signal) => {
      console.log(`[VSCode ${repo.port}] Exited with code ${code}, signal ${signal}`)
      // Update JSON file to mark as stopped
      try {
        const repos = await getRepositories()
        const idx = repos.findIndex(r => r.id === parseInt(repoId))
        if (idx !== -1) {
          repos[idx].running = false
          repos[idx].pid = null
          await saveRepositories(repos)
        }
      } catch (err) {
        console.error('Failed to update JSON after exit:', err)
      }
    })

    codeServer.unref()

    const url = `http://localhost:${repo.port}`

    // Wait longer for server to start
    await new Promise(resolve => setTimeout(resolve, 3000))

    // Update JSON file
    repo.running = true
    repo.pid = codeServer.pid
    repo.url = url
    repo.updated_at = new Date().toISOString()

    repositories[repoIndex] = repo
    await saveRepositories(repositories)

    // Broadcast update via WebSocket
    if (global.socketIO && global.socketIO.io) {
      global.socketIO.io.emit('vscode:updated', { repoId: parseInt(repoId), action: 'start', url, port: repo.port })
    }

    res.json({
      success: true,
      message: `Code-server started on port ${repo.port}`,
      url,
      port: repo.port,
      pid: codeServer.pid,
      repoId: parseInt(repoId)
    })
  } catch (error) {
    console.error('[API] Failed to start code-server:', error)
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to start code-server'
    })
  }
})

/**
 * POST /api/vscode/stop
 * Stop a code-server instance
 */
router.post('/stop', async (req, res) => {
  try {
    const { repoId } = req.body

    if (!repoId) {
      return res.status(400).json({
        success: false,
        error: 'Repository ID is required'
      })
    }

    const repositories = await getRepositories()

    // Get repository details
    const repoIndex = repositories.findIndex(r => r.id === parseInt(repoId))
    if (repoIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Repository not found'
      })
    }

    const repo = repositories[repoIndex]

    console.log(`[VSCode] Stopping code-server for ${repo.name} (PID: ${repo.pid})`)

    // Kill the process
    if (repo.pid) {
      try {
        process.kill(repo.pid, 'SIGTERM')

        // Wait a bit then force kill if still running
        setTimeout(() => {
          try {
            process.kill(repo.pid, 0) // Check if still running
            process.kill(repo.pid, 'SIGKILL') // Force kill
          } catch {
            // Already stopped
          }
        }, 2000)
      } catch (error) {
        // Process might already be stopped
        console.log(`[VSCode] Process ${repo.pid} not found (already stopped)`)
      }
    }

    // Update JSON file
    repo.running = false
    repo.pid = null
    repo.url = null
    repo.updated_at = new Date().toISOString()

    repositories[repoIndex] = repo
    await saveRepositories(repositories)

    // Broadcast update via WebSocket
    if (global.socketIO && global.socketIO.io) {
      global.socketIO.io.emit('vscode:updated', { repoId: parseInt(repoId), action: 'stop' })
    }

    res.json({
      success: true,
      message: 'Code-server stopped'
    })
  } catch (error) {
    console.error('[API] Failed to stop code-server:', error)
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to stop code-server'
    })
  }
})

/**
 * GET /api/vscode/list
 * List all repositories with git stats
 */
router.get('/list', async (req, res) => {
  try {
    const { exec } = require('child_process')
    const { promisify } = require('util')
    const execAsync = promisify(exec)

    const repositories = await getRepositories()

    // Add git stats to each repository
    const repositoriesWithStats = await Promise.all(
      repositories.map(async (repo) => {
        // Only add stats for git repositories
        if (repo.type !== 'git') {
          return repo
        }

        try {
          // Get git status
          const { stdout } = await execAsync('git status --porcelain', {
            cwd: repo.path,
            timeout: 5000
          })

          // Count changes
          let modified = 0, added = 0, deleted = 0, untracked = 0

          const lines = stdout.trim().split('\n').filter(line => line)
          for (const line of lines) {
            if (!line) continue
            const status = line.substring(0, 2)

            if (status === '??') {
              untracked++
            } else if (status.includes('M')) {
              modified++
            } else if (status.includes('A')) {
              added++
            } else if (status.includes('D')) {
              deleted++
            }
          }

          return {
            ...repo,
            modified,
            added: added + untracked, // Combine added and untracked
            deleted
          }
        } catch (error) {
          // If git command fails, return repo without stats
          return repo
        }
      })
    )

    res.json({
      success: true,
      repositories: repositoriesWithStats
    })
  } catch (error) {
    console.error('[API] Failed to list repositories:', error)
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to list repositories'
    })
  }
})

/**
 * POST /api/vscode/cleanup
 * Cleanup stopped repositories
 */
router.post('/cleanup', async (req, res) => {
  try {
    const result = {
      success: true,
      message: 'Cleanup completed',
      cleaned: 0
    }

    res.json(result)
  } catch (error) {
    console.error('[API] Failed to cleanup:', error)
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to cleanup'
    })
  }
})

/**
 * GET /api/vscode/changes/:repoId
 * Get git changes for a repository
 */
router.get('/changes/:repoId', async (req, res) => {
  try {
    const { repoId } = req.params
    const { exec } = require('child_process')
    const { promisify } = require('util')
    const execAsync = promisify(exec)

    const repositories = await getRepositories()
    const repo = repositories.find(r => r.id === parseInt(repoId))

    if (!repo) {
      return res.status(404).json({
        success: false,
        error: 'Repository not found'
      })
    }

    // Get git status with porcelain format
    try {
      const { stdout } = await execAsync('git status --porcelain', {
        cwd: repo.path,
        timeout: 10000
      })

      const changes = {
        modified: [],
        added: [],
        deleted: [],
        untracked: []
      }

      // Parse git status output
      const lines = stdout.trim().split('\n').filter(line => line)

      for (const line of lines) {
        if (!line) continue

        const status = line.substring(0, 2)
        const file = line.substring(3)

        if (status === '??') {
          changes.untracked.push(file)
        } else if (status.includes('M')) {
          changes.modified.push(file)
        } else if (status.includes('A')) {
          changes.added.push(file)
        } else if (status.includes('D')) {
          changes.deleted.push(file)
        } else if (status.trim() === 'M') {
          changes.modified.push(file)
        } else if (status.trim() === 'A') {
          changes.added.push(file)
        } else if (status.trim() === 'D') {
          changes.deleted.push(file)
        }
      }

      res.json({
        success: true,
        changes
      })
    } catch (gitError) {
      // Not a git repository or git error
      res.json({
        success: true,
        changes: {
          modified: [],
          added: [],
          deleted: [],
          untracked: []
        },
        error: gitError.message
      })
    }
  } catch (error) {
    console.error('[API] Failed to get changes:', error)
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to get changes'
    })
  }
})

/**
 * POST /api/vscode/diff
 * Get diff for a file
 */
router.post('/diff', async (req, res) => {
  try {
    const { repoId, file } = req.body

    if (!repoId || !file) {
      return res.status(400).json({
        success: false,
        error: 'Repository ID and file are required'
      })
    }

    const { exec } = require('child_process')
    const { promisify } = require('util')
    const execAsync = promisify(exec)

    const repositories = await getRepositories()
    const repo = repositories.find(r => r.id === parseInt(repoId))

    if (!repo) {
      return res.status(404).json({
        success: false,
        error: 'Repository not found'
      })
    }

    try {
      // First check if file is untracked
      const { stdout: statusOutput } = await execAsync(`git status --porcelain -- "${file}"`, {
        cwd: repo.path,
        timeout: 5000
      })

      const status = statusOutput.trim().substring(0, 2)

      // If file is untracked (??), show the entire file as new
      if (status === '??') {
        const fs = require('fs')
        const path = require('path')
        const filePath = path.join(repo.path, file)

        try {
          const content = fs.readFileSync(filePath, 'utf-8')
          const lines = content.split('\n')
          const diff = lines.map((line, i) => `+${line}`).join('\n')
          const header = `diff --git a/${file} b/${file}\nnew file\n--- /dev/null\n+++ b/${file}\n@@ -0,0 +1,${lines.length} @@\n`

          res.json({
            success: true,
            diff: header + diff
          })
          return
        } catch (fsError) {
          res.json({
            success: true,
            diff: 'File not found or cannot be read',
            error: fsError.message
          })
          return
        }
      }

      // For tracked files, get diff vs HEAD
      const { stdout } = await execAsync(`git diff HEAD -- "${file}"`, {
        cwd: repo.path,
        timeout: 10000,
        maxBuffer: 5 * 1024 * 1024 // 5MB buffer for large diffs
      })

      // If no diff vs HEAD, try diff vs index (staged changes)
      if (!stdout) {
        const { stdout: stagedDiff } = await execAsync(`git diff --cached -- "${file}"`, {
          cwd: repo.path,
          timeout: 10000,
          maxBuffer: 5 * 1024 * 1024
        })

        res.json({
          success: true,
          diff: stagedDiff || 'No changes'
        })
      } else {
        res.json({
          success: true,
          diff: stdout
        })
      }
    } catch (gitError) {
      // Git error or file not tracked
      res.json({
        success: true,
        diff: '',
        error: gitError.message
      })
    }
  } catch (error) {
    console.error('[API] Failed to get diff:', error)
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to get diff'
    })
  }
})

module.exports = router
