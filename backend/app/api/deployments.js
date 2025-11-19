/**
 * Deployments API Routes
 * Handles PM2 deployments for repositories
 * Storage: data/deployments.json
 */

const express = require('express')
const router = express.Router()
const { readJSON, writeJSON, getDataPath } = require('../../lib/json-storage')

const DEPLOYMENTS_FILE = getDataPath('deployments.json')
const REPOS_FILE = getDataPath('repositories.json')

/**
 * Get all deployments from JSON file
 */
async function getDeployments() {
  const data = await readJSON(DEPLOYMENTS_FILE)
  return data?.deployments || []
}

/**
 * Save deployments to JSON file
 */
async function saveDeployments(deployments) {
  await writeJSON(DEPLOYMENTS_FILE, { deployments })
}

/**
 * Get repositories from JSON file
 */
async function getRepositories() {
  const data = await readJSON(REPOS_FILE)
  return data?.repositories || []
}

/**
 * GET /api/deployments
 * List all deployments
 */
router.get('/', async (req, res) => {
  try {
    const deployments = await getDeployments()
    const repositories = await getRepositories()

    // Enrich deployments with repository info
    const enrichedDeployments = deployments.map(d => {
      const repo = repositories.find(r => r.id === d.repositoryId)
      return {
        ...d,
        repositoryName: repo?.name || 'Unknown',
        repositoryPath: repo?.path || null,
      }
    })

    res.json({
      success: true,
      deployments: enrichedDeployments,
      count: enrichedDeployments.length
    })
  } catch (error) {
    console.error('[API Deployments GET] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/deployments
 * Create a new deployment
 */
router.post('/', async (req, res) => {
  try {
    const {
      repositoryId,
      repoId,
      name,
      repoName,
      domain,
      port,
      mode,
      instances,
      selectedServices,
      customEnvVars
    } = req.body

    // Accept both repositoryId and repoId
    const finalRepoId = repositoryId || repoId
    const finalName = name || repoName

    // Validation
    if (!finalRepoId) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: repositoryId or repoId'
      })
    }

    const repositories = await getRepositories()

    // Check if repository exists
    const repo = repositories.find(r => r.id === finalRepoId)
    if (!repo) {
      return res.status(404).json({
        success: false,
        error: 'Repository not found'
      })
    }

    const deploymentPort = port || repo.port
    const deployments = await getDeployments()

    // Generate new ID
    const newId = deployments.length > 0
      ? Math.max(...deployments.map(d => d.id)) + 1
      : 1

    // Create deployment
    const deployment = {
      id: newId,
      repositoryId: finalRepoId,
      name: finalName || repo.path.split('/').pop(),
      domain: domain || null,
      port: deploymentPort,
      status: 'stopped',
      mode: mode || 'fork',
      instances: instances || 1,
      pid: null,
      memory: null,
      cpu: null,
      uptime: null,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    deployments.push(deployment)
    await saveDeployments(deployments)

    console.log(`[API Deployments] Created deployment: ${deployment.name} on port ${deployment.port}`)

    res.json({
      success: true,
      deployment,
      message: `Deployment created successfully for ${deployment.name}`
    })
  } catch (error) {
    console.error('[API Deployments POST] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/deployments/:id/action
 * Perform action on deployment (start/stop/restart/delete)
 */
router.post('/:id/action', async (req, res) => {
  try {
    const { id } = req.params
    const { action } = req.body

    if (!action || !['start', 'stop', 'restart', 'delete'].includes(action)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid action. Must be: start, stop, restart, or delete'
      })
    }

    console.log(`[API Deployments ACTION] ${action} deployment: ${id}`)

    const { exec } = require('child_process')
    const { promisify } = require('util')
    const execAsync = promisify(exec)

    const deployments = await getDeployments()
    const repositories = await getRepositories()

    // Get deployment
    const deploymentIndex = deployments.findIndex(d => d.id === parseInt(id))
    if (deploymentIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Deployment not found'
      })
    }

    const deployment = deployments[deploymentIndex]
    const repo = repositories.find(r => r.id === deployment.repositoryId)

    if (!repo) {
      return res.status(404).json({
        success: false,
        error: 'Repository not found for this deployment'
      })
    }

    const appName = `deploy-${id}-${deployment.name.replace(/[^a-zA-Z0-9]/g, '-')}`

    // Handle delete
    if (action === 'delete') {
      try {
        // Stop and delete PM2 process
        await execAsync(`pm2 delete ${appName}`).catch(() => {
          // Ignore error if process doesn't exist
        })
      } catch (error) {
        console.error(`[Deployments] Error deleting PM2 process:`, error)
      }

      const filteredDeployments = deployments.filter(d => d.id !== parseInt(id))
      await saveDeployments(filteredDeployments)

      // Broadcast update via WebSocket
      if (global.socketIO && global.socketIO.io) {
        global.socketIO.io.emit('deployment:deleted', { id: parseInt(id) })
      }

      return res.json({
        success: true,
        message: 'Deployment deleted'
      })
    }

    // Handle start
    if (action === 'start') {
      try {
        // Check if package.json exists
        const fs = require('fs').promises
        const packageJsonPath = `${repo.path}/package.json`

        try {
          await fs.access(packageJsonPath)
        } catch {
          throw new Error('package.json not found in repository')
        }

        // Read package.json to get start script
        const packageJson = JSON.parse(await fs.readFile(packageJsonPath, 'utf-8'))
        const startScript = packageJson.scripts?.start || 'node index.js'

        // Build PM2 ecosystem config
        const pm2Config = {
          name: appName,
          cwd: repo.path,
          script: startScript.includes('npm') ? 'npm' : startScript.split(' ')[0],
          args: startScript.includes('npm') ? 'start' : startScript.split(' ').slice(1).join(' '),
          instances: deployment.instances || 1,
          exec_mode: deployment.mode || 'fork',
          env: {
            PORT: deployment.port,
            NODE_ENV: 'production'
          }
        }

        // Start with PM2
        const configPath = `/tmp/pm2-${appName}.json`
        await fs.writeFile(configPath, JSON.stringify(pm2Config))

        const { stdout, stderr } = await execAsync(`pm2 start ${configPath}`)
        console.log(`[Deployments] PM2 start output:`, stdout)

        // Get process info
        const { stdout: processInfo } = await execAsync(`pm2 jlist`)
        const processes = JSON.parse(processInfo)
        const process = processes.find(p => p.name === appName)

        if (process) {
          // Update deployment with process info
          deployment.status = 'running'
          deployment.pid = process.pid
          deployment.updatedAt = new Date().toISOString()

          deployments[deploymentIndex] = deployment
          await saveDeployments(deployments)

          // Broadcast update via WebSocket
          if (global.socketIO && global.socketIO.io) {
            global.socketIO.io.emit('deployment:updated', {
              id: parseInt(id),
              action: 'start',
              status: 'running',
              pid: process.pid
            })
          }

          return res.json({
            success: true,
            message: `Deployment started on port ${deployment.port}`,
            deployment: {
              id: parseInt(id),
              status: 'running',
              pid: process.pid,
              port: deployment.port
            }
          })
        } else {
          throw new Error('Failed to start PM2 process')
        }
      } catch (error) {
        console.error(`[Deployments] Start error:`, error)
        deployment.status = 'error'
        deployment.updatedAt = new Date().toISOString()
        deployments[deploymentIndex] = deployment
        await saveDeployments(deployments)
        throw error
      }
    }

    // Handle stop
    if (action === 'stop') {
      try {
        await execAsync(`pm2 stop ${appName}`)

        deployment.status = 'stopped'
        deployment.pid = null
        deployment.updatedAt = new Date().toISOString()

        deployments[deploymentIndex] = deployment
        await saveDeployments(deployments)

        // Broadcast update via WebSocket
        if (global.socketIO && global.socketIO.io) {
          global.socketIO.io.emit('deployment:updated', {
            id: parseInt(id),
            action: 'stop',
            status: 'stopped'
          })
        }

        return res.json({
          success: true,
          message: 'Deployment stopped'
        })
      } catch (error) {
        console.error(`[Deployments] Stop error:`, error)
        throw error
      }
    }

    // Handle restart
    if (action === 'restart') {
      try {
        await execAsync(`pm2 restart ${appName}`)

        // Get updated process info
        const { stdout: processInfo } = await execAsync(`pm2 jlist`)
        const processes = JSON.parse(processInfo)
        const process = processes.find(p => p.name === appName)

        deployment.status = 'running'
        deployment.pid = process?.pid || null
        deployment.updatedAt = new Date().toISOString()

        deployments[deploymentIndex] = deployment
        await saveDeployments(deployments)

        // Broadcast update via WebSocket
        if (global.socketIO && global.socketIO.io) {
          global.socketIO.io.emit('deployment:updated', {
            id: parseInt(id),
            action: 'restart',
            status: 'running'
          })
        }

        return res.json({
          success: true,
          message: 'Deployment restarted'
        })
      } catch (error) {
        console.error(`[Deployments] Restart error:`, error)
        throw error
      }
    }
  } catch (error) {
    console.error('[API Deployments ACTION] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * GET /api/deployments/services
 * Get Docker/PM2 services status for deployments
 */
router.get('/services', async (req, res) => {
  try {
    const { exec } = require('child_process')
    const { promisify } = require('util')
    const execAsync = promisify(exec)

    // Get running services from Docker
    const services = []

    try {
      const { stdout } = await execAsync('docker ps --format "{{.Names}}\t{{.Ports}}\t{{.Image}}"')
      const lines = stdout.trim().split('\n').filter(line => line)

      for (const line of lines) {
        const [name, ports, image] = line.split('\t')

        // Parse port mapping
        let port = null
        let connectionString = ''

        if (ports) {
          const portMatch = ports.match(/0\.0\.0\.0:(\d+)/)
          if (portMatch) {
            port = parseInt(portMatch[1])
          }
        }

        // Determine service type and connection string
        let type = 'unknown'
        if (image.includes('postgres')) {
          type = 'postgresql'
          connectionString = `postgresql://localhost:${port}/db`
        } else if (image.includes('mysql')) {
          type = 'mysql'
          connectionString = `mysql://localhost:${port}/db`
        } else if (image.includes('mongo')) {
          type = 'mongodb'
          connectionString = `mongodb://localhost:${port}/db`
        } else if (image.includes('redis')) {
          type = 'redis'
          connectionString = `redis://localhost:${port}`
        }

        services.push({
          id: name,
          name,
          containerName: name,
          port,
          type,
          connectionString
        })
      }
    } catch (error) {
      console.log('[Deployments] No Docker services found or Docker not running')
    }

    res.json({
      success: true,
      services
    })
  } catch (error) {
    console.error('[API Deployments Services] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * GET /api/deployments/:id/logs
 * Get PM2 logs for a deployment
 */
router.get('/:id/logs', async (req, res) => {
  try {
    const { id } = req.params
    const { lines = 100 } = req.query

    const { exec } = require('child_process')
    const { promisify } = require('util')
    const execAsync = promisify(exec)

    const deployments = await getDeployments()

    // Get deployment
    const deployment = deployments.find(d => d.id === parseInt(id))
    if (!deployment) {
      return res.status(404).json({
        success: false,
        error: 'Deployment not found'
      })
    }

    const appName = `deploy-${id}-${deployment.name.replace(/[^a-zA-Z0-9]/g, '-')}`

    try {
      // Get PM2 logs
      const { stdout } = await execAsync(`pm2 logs ${appName} --lines ${lines} --nostream --raw`)

      res.json({
        success: true,
        logs: stdout || 'No logs available'
      })
    } catch (error) {
      // Process might not exist
      res.json({
        success: true,
        logs: 'No logs available - deployment not running'
      })
    }
  } catch (error) {
    console.error('[API Deployments Logs] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

module.exports = router
