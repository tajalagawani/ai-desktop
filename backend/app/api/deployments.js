/**
 * Deployments API Routes - Complete Deployment System
 * Handles PM2 deployments with framework detection, build process, and WebSocket logs
 * Restored from original comprehensive deployment system
 */

const express = require('express')
const router = express.Router()
const { readJSON, writeJSON, getDataPath } = require('../../lib/json-storage')
const { exec } = require('child_process')
const { promisify } = require('util')
const fs = require('fs').promises
const fsSync = require('fs')
const path = require('path')

const execAsync = promisify(exec)

const DEPLOYMENTS_FILE = getDataPath('deployments.json')
const LOGS_DIR = path.join(__dirname, '../../../logs')
const PORT_RANGE_START = 3050
const PORT_RANGE_END = 3999

// Ensure directories exist
async function ensureDirs() {
  try {
    await fs.access(LOGS_DIR)
  } catch {
    await fs.mkdir(LOGS_DIR, { recursive: true })
  }
}

/**
 * Load deployments from JSON file
 */
async function loadDeployments() {
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
 * Find available port in range
 */
async function findAvailablePort(deployments) {
  const usedPorts = new Set(deployments.map(d => d.port))
  for (let port = PORT_RANGE_START; port <= PORT_RANGE_END; port++) {
    if (!usedPorts.has(port)) {
      return port
    }
  }
  throw new Error(`No available ports in range ${PORT_RANGE_START}-${PORT_RANGE_END}`)
}

/**
 * Detect framework from package.json
 */
async function detectFramework(repoPath) {
  try {
    const packageJsonPath = path.join(repoPath, 'package.json')
    const packageJson = JSON.parse(await fs.readFile(packageJsonPath, 'utf-8'))
    const deps = { ...packageJson.dependencies, ...packageJson.devDependencies }

    // Next.js
    if (deps.next) {
      return {
        type: 'nextjs',
        buildCommand: 'npm run build',
        startCommand: 'npm start',
        installCommand: 'npm install'
      }
    }

    // Nuxt
    if (deps.nuxt) {
      return {
        type: 'nuxt',
        buildCommand: 'npm run build',
        startCommand: 'npm start',
        installCommand: 'npm install'
      }
    }

    // Vite (React, Vue, etc.)
    if (deps.vite) {
      return {
        type: 'react-vite',
        buildCommand: 'npm run build',
        startCommand: 'npx serve -s dist',
        installCommand: 'npm install'
      }
    }

    // NestJS
    if (deps['@nestjs/core']) {
      return {
        type: 'nestjs',
        buildCommand: 'npm run build',
        startCommand: 'npm run start:prod',
        installCommand: 'npm install'
      }
    }

    // Express
    if (deps.express) {
      return {
        type: 'express',
        buildCommand: null,
        startCommand: packageJson.scripts?.start || 'node index.js',
        installCommand: 'npm install'
      }
    }

    // Default Node.js
    return {
      type: 'node',
      buildCommand: null,
      startCommand: packageJson.scripts?.start || 'node index.js',
      installCommand: 'npm install'
    }
  } catch (error) {
    console.error('[Framework Detection] Error:', error)
    return {
      type: 'node',
      buildCommand: null,
      startCommand: 'node index.js',
      installCommand: 'npm install'
    }
  }
}

/**
 * Get running Docker services
 */
async function getRunningServices() {
  const services = []
  try {
    const { stdout } = await execAsync('docker ps --format "{{.Names}}\\t{{.Ports}}\\t{{.Image}}"')
    const lines = stdout.trim().split('\n').filter(line => line)

    for (const line of lines) {
      const [name, ports, image] = line.split('\t')
      let port = null
      if (ports) {
        const portMatch = ports.match(/0\.0\.0\.0:(\d+)/)
        if (portMatch) {
          port = parseInt(portMatch[1])
        }
      }

      let type = 'unknown'
      let connectionString = ''

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
    console.log('[Services] No Docker services found')
  }
  return services
}

/**
 * Generate environment variables from selected services
 */
function generateEnvVarsFromServices(services, customEnvVars = {}) {
  const envVars = { ...customEnvVars }

  for (const service of services) {
    const prefix = service.type.toUpperCase().replace('-', '_')
    envVars[`${prefix}_URL`] = service.connectionString
    if (service.port) {
      envVars[`${prefix}_PORT`] = service.port.toString()
    }
  }

  return envVars
}

/**
 * GET /api/deployments
 * List all deployments with current PM2 status
 */
router.get('/', async (req, res) => {
  try {
    const deployments = await loadDeployments()

    // Get PM2 status for each deployment
    try {
      const { stdout } = await execAsync('pm2 jlist')
      const pm2List = JSON.parse(stdout)

      for (const deployment of deployments) {
        const pm2App = pm2List.find(app => app.name === deployment.pm2Name)
        if (pm2App) {
          deployment.status = pm2App.pm2_env.status === 'online' ? 'running' : 'stopped'
        } else {
          deployment.status = 'stopped'
        }
      }
    } catch (error) {
      console.error('[Deployments] Error getting PM2 status:', error)
    }

    await saveDeployments(deployments)

    res.json({
      success: true,
      deployments
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
 * Create new deployment with full build process
 */
router.post('/', async (req, res) => {
  try {
    await ensureDirs()

    const {
      repoId,
      repoName,
      repoPath,
      selectedServices = [],
      customEnvVars = {},
      domain
    } = req.body

    console.log(`[Deployments] Creating deployment for ${repoName} at ${repoPath}`)

    // Detect framework
    const framework = await detectFramework(repoPath)
    console.log(`[Deployments] Detected framework: ${framework.type}`)

    // Get running services
    const runningServices = await getRunningServices()
    const services = runningServices.filter(s =>
      selectedServices.includes(s.containerName)
    )

    // Generate environment variables
    const envVars = generateEnvVarsFromServices(services, customEnvVars)

    // Find available port
    const deployments = await loadDeployments()
    const port = await findAvailablePort(deployments)

    // Create deployment ID
    const deploymentId = `${repoId}-${Date.now()}`
    const pm2Name = `deployment-${deploymentId}`
    const logFile = path.join(LOGS_DIR, `${deploymentId}.log`)

    // Add PORT to env vars
    envVars.PORT = port.toString()
    envVars.NODE_ENV = 'production'

    // Create deployment config
    const deployment = {
      id: deploymentId,
      repoId,
      repoName,
      repoPath,
      framework: framework.type,
      buildCommand: framework.buildCommand,
      startCommand: framework.startCommand,
      port,
      domain,
      services: services.map(s => s.containerName),
      envVars,
      status: 'building',
      pm2Name,
      deployedAt: new Date().toISOString(),
      buildLogs: logFile
    }

    // Save deployment
    deployments.push(deployment)
    await saveDeployments(deployments)

    // Start deployment process (async - don't wait)
    deployApp(deployment).catch(error => {
      console.error('[Deployments] Deployment error:', error)
    })

    res.json({
      success: true,
      deployment,
      message: 'Deployment started'
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
 * Deploy app (async background process)
 */
async function deployApp(deployment) {
  let logStream
  try {
    logStream = await fs.open(deployment.buildLogs, 'w')

    const log = async (message) => {
      const timestamp = new Date().toISOString()
      await logStream.writeFile(`[${timestamp}] ${message}\n`)
    }

    await log(`Starting deployment for ${deployment.repoName}`)
    await log(`Framework: ${deployment.framework}`)
    await log(`Port: ${deployment.port}`)
    await log('')

    // Install dependencies
    await log('Installing dependencies...')
    const { stdout: installOutput, stderr: installError } = await execAsync(
      'npm install',
      { cwd: deployment.repoPath, timeout: 600000 }
    )
    await logStream.writeFile(installOutput)
    if (installError) await logStream.writeFile(installError)

    // Build if needed
    if (deployment.buildCommand) {
      await log('')
      await log('Building application...')
      const { stdout: buildOutput, stderr: buildError } = await execAsync(
        deployment.buildCommand,
        { cwd: deployment.repoPath, timeout: 600000 }
      )
      await logStream.writeFile(buildOutput)
      if (buildError) await logStream.writeFile(buildError)
    }

    // Create .env file
    const envContent = Object.entries(deployment.envVars)
      .map(([key, val]) => `${key}=${val}`)
      .join('\n')
    await fs.writeFile(
      path.join(deployment.repoPath, '.env.production'),
      envContent
    )

    // Create PM2 ecosystem config
    const ecosystemConfig = {
      apps: [{
        name: deployment.pm2Name,
        script: deployment.startCommand.split(' ')[0],
        args: deployment.startCommand.split(' ').slice(1).join(' '),
        cwd: deployment.repoPath,
        env: deployment.envVars,
        instances: 1,
        autorestart: true,
        watch: false,
        max_memory_restart: '1G',
        error_file: path.join(LOGS_DIR, `${deployment.id}-error.log`),
        out_file: path.join(LOGS_DIR, `${deployment.id}-out.log`)
      }]
    }

    const ecosystemPath = path.join(deployment.repoPath, `ecosystem.${deployment.id}.config.js`)
    await fs.writeFile(
      ecosystemPath,
      `module.exports = ${JSON.stringify(ecosystemConfig, null, 2)}`
    )

    // Start with PM2
    await log('')
    await log('Starting application with PM2...')
    const { stdout: pm2Output } = await execAsync(
      `pm2 start ${ecosystemPath}`,
      { cwd: deployment.repoPath }
    )
    await logStream.writeFile(pm2Output)

    // Save PM2 config
    await execAsync('pm2 save')

    // Open firewall port
    await log('')
    await log(`Opening firewall port ${deployment.port}...`)
    try {
      await execAsync(`ufw allow ${deployment.port}/tcp comment 'Deployment: ${deployment.repoName}'`)
      await log(`✓ Port ${deployment.port} opened in firewall`)
    } catch (error) {
      await log(`⚠ Warning: Could not open firewall port: ${error.message}`)
    }

    // Update deployment status
    const deployments = await loadDeployments()
    const index = deployments.findIndex(d => d.id === deployment.id)
    if (index !== -1) {
      deployments[index].status = 'running'
      deployments[index].lastDeployedAt = new Date().toISOString()
      await saveDeployments(deployments)
    }

    await log('')
    await log('✅ Deployment completed successfully!')
    await log(`Application running on http://localhost:${deployment.port}`)

  } catch (error) {
    if (logStream) {
      const timestamp = new Date().toISOString()
      await logStream.writeFile(`\n[${timestamp}] ❌ Deployment failed: ${error.message}\n`)
      await logStream.writeFile(error.stack || '')
    }

    // Update deployment status to failed
    const deployments = await loadDeployments()
    const index = deployments.findIndex(d => d.id === deployment.id)
    if (index !== -1) {
      deployments[index].status = 'failed'
      deployments[index].error = error.message
      await saveDeployments(deployments)
    }
  } finally {
    if (logStream) {
      await logStream.close()
    }
  }
}

/**
 * POST /api/deployments/:id/action
 * Perform actions on deployment (start, stop, restart, delete, rebuild)
 */
router.post('/:id/action', async (req, res) => {
  try {
    const { id } = req.params
    const { action } = req.body

    const deployments = await loadDeployments()
    const deployment = deployments.find(d => d.id === id)

    if (!deployment) {
      return res.status(404).json({
        success: false,
        error: 'Deployment not found'
      })
    }

    console.log(`[Deployments] Action: ${action} for deployment ${id}`)

    switch (action) {
      case 'start':
        await execAsync(`pm2 start ${deployment.pm2Name}`)
        deployment.status = 'running'
        await saveDeployments(deployments)
        return res.json({
          success: true,
          message: `${deployment.repoName} started`
        })

      case 'stop':
        await execAsync(`pm2 stop ${deployment.pm2Name}`)
        deployment.status = 'stopped'
        await saveDeployments(deployments)
        return res.json({
          success: true,
          message: `${deployment.repoName} stopped`
        })

      case 'restart':
        await execAsync(`pm2 restart ${deployment.pm2Name}`)
        deployment.status = 'running'
        await saveDeployments(deployments)
        return res.json({
          success: true,
          message: `${deployment.repoName} restarted`
        })

      case 'delete':
        // Stop and delete from PM2
        try {
          await execAsync(`pm2 delete ${deployment.pm2Name}`)
          await execAsync('pm2 save')
        } catch (error) {
          console.error('[Deployments] Error deleting from PM2:', error)
        }

        // Delete ecosystem config
        try {
          const ecosystemPath = path.join(deployment.repoPath, `ecosystem.${deployment.id}.config.js`)
          await fs.unlink(ecosystemPath)
        } catch (error) {
          console.error('[Deployments] Error deleting ecosystem config:', error)
        }

        // Remove from deployments
        const index = deployments.findIndex(d => d.id === id)
        if (index !== -1) {
          deployments.splice(index, 1)
          await saveDeployments(deployments)
        }

        return res.json({
          success: true,
          message: `${deployment.repoName} deployment deleted`
        })

      case 'rebuild':
        // Stop current deployment
        try {
          await execAsync(`pm2 stop ${deployment.pm2Name}`)
        } catch {}

        deployment.status = 'building'
        await saveDeployments(deployments)

        // Trigger rebuild
        deployApp(deployment).catch(error => {
          console.error('[Deployments] Rebuild error:', error)
        })

        return res.json({
          success: true,
          message: `${deployment.repoName} rebuild started`
        })

      default:
        return res.status(400).json({
          success: false,
          error: 'Invalid action'
        })
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
 * GET /api/deployments/:id/logs
 * Get deployment logs (for non-WebSocket clients)
 */
router.get('/:id/logs', async (req, res) => {
  try {
    const { id } = req.params
    const { type = 'build', lines = 100 } = req.query

    const deployments = await loadDeployments()
    const deployment = deployments.find(d => d.id === id)

    if (!deployment) {
      return res.status(404).json({
        success: false,
        error: 'Deployment not found'
      })
    }

    let logFile
    if (type === 'build') {
      logFile = deployment.buildLogs
    } else {
      logFile = path.join(LOGS_DIR, `${deployment.id}-out.log`)
    }

    try {
      if (fsSync.existsSync(logFile)) {
        const content = await fs.readFile(logFile, 'utf-8')
        const logLines = content.split('\n')
        const lastLines = logLines.slice(-lines).join('\n')

        res.json({
          success: true,
          logs: lastLines
        })
      } else {
        res.json({
          success: true,
          logs: 'No logs available yet'
        })
      }
    } catch (error) {
      res.json({
        success: true,
        logs: `Error reading logs: ${error.message}`
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

/**
 * GET /api/deployments/services
 * Get running Docker services available for deployment configuration
 */
router.get('/services', async (req, res) => {
  try {
    const services = await getRunningServices()
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

module.exports = router
