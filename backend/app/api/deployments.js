/**
 * Deployments API Routes - EXACT replica of old Next.js deployment system
 * Converted from app/api/deployments/route.ts
 */

const express = require('express')
const router = express.Router()
const fs = require('fs').promises
const fsSync = require('fs')
const path = require('path')
const { exec, spawn } = require('child_process')
const { promisify } = require('util')

const execAsync = promisify(exec)

// Helper to emit logs to WebSocket
function emitLog(deploymentId, message) {
  if (global.socketIO && global.socketIO.emitToDeployment) {
    global.socketIO.emitToDeployment(deploymentId, 'log', { data: message })
  }
}

// Helper to run command with real-time output
function runCommandWithLogs(command, options, deploymentId) {
  return new Promise((resolve, reject) => {
    const parts = command.split(' ')
    const cmd = parts[0]
    const args = parts.slice(1)

    const process = spawn(cmd, args, {
      ...options,
      shell: true
    })

    let stdout = ''
    let stderr = ''

    process.stdout.on('data', (data) => {
      const text = data.toString()
      stdout += text
      emitLog(deploymentId, text)
    })

    process.stderr.on('data', (data) => {
      const text = data.toString()
      stderr += text
      emitLog(deploymentId, text)
    })

    process.on('close', (code) => {
      if (code === 0) {
        resolve({ stdout, stderr })
      } else {
        reject(new Error(`Command failed with code ${code}: ${stderr}`))
      }
    })

    process.on('error', (error) => {
      reject(error)
    })
  })
}

const DEPLOYMENTS_FILE = '/var/www/ai-desktop/data/deployments.json'
const LOGS_DIR = '/var/www/ai-desktop/logs'
const PORT_RANGE_START = 3050
const PORT_RANGE_END = 3999

// Ensure data directory exists
async function ensureDataDir() {
  const dataDir = path.dirname(DEPLOYMENTS_FILE)
  try {
    await fs.access(dataDir)
  } catch {
    await fs.mkdir(dataDir, { recursive: true })
  }

  try {
    await fs.access(LOGS_DIR)
  } catch {
    await fs.mkdir(LOGS_DIR, { recursive: true })
  }
}

// Load deployments from file
async function loadDeployments() {
  await ensureDataDir()
  try {
    const data = await fs.readFile(DEPLOYMENTS_FILE, 'utf-8')
    const parsed = JSON.parse(data)
    return parsed.deployments || []
  } catch {
    return []
  }
}

// Save deployments to file
async function saveDeployments(deployments) {
  await ensureDataDir()
  await fs.writeFile(
    DEPLOYMENTS_FILE,
    JSON.stringify({ deployments }, null, 2),
    'utf-8'
  )
}

// Find available port
async function findAvailablePort(deployments) {
  const usedPorts = new Set(deployments.map(d => d.port))
  for (let port = PORT_RANGE_START; port <= PORT_RANGE_END; port++) {
    if (!usedPorts.has(port)) {
      return port
    }
  }
  throw new Error('No available ports in range 3050-3999')
}

// Framework detection (from lib/deployment/detector.ts)
async function detectFramework(repoPath) {
  try {
    // Check for package.json (Node.js projects)
    const packageJsonPath = path.join(repoPath, 'package.json')
    if (await fileExists(packageJsonPath)) {
      const packageJson = JSON.parse(await fs.readFile(packageJsonPath, 'utf-8'))
      return detectNodeFramework(packageJson)
    }

    // Default to Node.js
    return {
      type: 'node',
      buildCommand: null,
      startCommand: 'npm start',
      installCommand: 'npm install',
      port: 3000
    }
  } catch (error) {
    console.error('Error detecting framework:', error)
    throw new Error('Failed to detect project framework')
  }
}

function detectNodeFramework(packageJson) {
  const deps = { ...packageJson.dependencies, ...packageJson.devDependencies }
  const scripts = packageJson.scripts || {}

  // Next.js
  if (deps.next) {
    return {
      type: 'nextjs',
      version: deps.next,
      buildCommand: '', // Skip build for dev mode
      startCommand: 'npm run dev',
      installCommand: 'npm install',
      outputDir: '.next',
      port: 3000
    }
  }

  // Nuxt.js
  if (deps.nuxt) {
    return {
      type: 'nuxt',
      version: deps.nuxt,
      buildCommand: 'npm run build',
      startCommand: 'npm start',
      installCommand: 'npm install',
      outputDir: '.nuxt',
      port: 3000
    }
  }

  // Vite (React, Vue, Svelte)
  if (deps.vite) {
    if (deps.react) {
      return {
        type: 'react-vite',
        buildCommand: 'npm run build',
        startCommand: 'npx serve -s dist -l 3000',
        installCommand: 'npm install',
        outputDir: 'dist',
        port: 3000
      }
    }
    if (deps.vue) {
      return {
        type: 'vue',
        buildCommand: 'npm run build',
        startCommand: 'npx serve -s dist -l 3000',
        installCommand: 'npm install',
        outputDir: 'dist',
        port: 3000
      }
    }
    if (deps.svelte) {
      return {
        type: 'svelte',
        buildCommand: 'npm run build',
        startCommand: 'npx serve -s dist -l 3000',
        installCommand: 'npm install',
        outputDir: 'dist',
        port: 3000
      }
    }
  }

  // Create React App
  if (deps['react-scripts']) {
    return {
      type: 'react-cra',
      buildCommand: 'npm run build',
      startCommand: 'npx serve -s build -l 3000',
      installCommand: 'npm install',
      outputDir: 'build',
      port: 3000
    }
  }

  // Angular
  if (deps['@angular/core']) {
    return {
      type: 'angular',
      buildCommand: 'npm run build',
      startCommand: 'npx serve -s dist -l 3000',
      installCommand: 'npm install',
      outputDir: 'dist',
      port: 3000
    }
  }

  // Astro
  if (deps.astro) {
    return {
      type: 'astro',
      buildCommand: 'npm run build',
      startCommand: 'npm start',
      installCommand: 'npm install',
      outputDir: 'dist',
      port: 3000
    }
  }

  // NestJS
  if (deps['@nestjs/core']) {
    return {
      type: 'nestjs',
      buildCommand: 'npm run build',
      startCommand: 'npm run start:prod',
      installCommand: 'npm install',
      outputDir: 'dist',
      port: 3000
    }
  }

  // Express
  if (deps.express) {
    return {
      type: 'express',
      buildCommand: null,
      startCommand: scripts.start || 'node server.js',
      installCommand: 'npm install',
      port: 3000
    }
  }

  // Generic Node.js
  return {
    type: 'node',
    buildCommand: scripts.build || null,
    startCommand: scripts.start || 'node index.js',
    installCommand: 'npm install',
    port: 3000
  }
}

async function fileExists(filePath) {
  try {
    await fs.access(filePath)
    return true
  } catch {
    return false
  }
}

function getFrameworkDisplayName(type) {
  const names = {
    nextjs: 'Next.js',
    'react-vite': 'React (Vite)',
    'react-cra': 'React (CRA)',
    vue: 'Vue.js',
    nuxt: 'Nuxt.js',
    angular: 'Angular',
    svelte: 'Svelte',
    astro: 'Astro',
    node: 'Node.js',
    express: 'Express',
    nestjs: 'NestJS'
  }
  return names[type] || type
}

// Get running Docker services (from lib/deployment/services.ts)
async function getRunningServices() {
  try {
    const { stdout } = await execAsync(
      'docker ps --filter "label=ai-desktop-service=true" --format "{{.Names}}|{{.Ports}}" || docker ps --format "{{.Names}}|{{.Ports}}"'
    )

    if (!stdout.trim()) {
      return []
    }

    const services = []

    for (const line of stdout.trim().split('\n')) {
      const [containerName, ports] = line.split('|')
      const serviceId = containerName.replace('ai-desktop-', '')

      // Extract port number
      const portMatch = ports.match(/0\.0\.0\.0:(\d+)/)
      const port = portMatch ? parseInt(portMatch[1]) : 0

      if (!port) continue

      // Generate connection string
      const connectionString = generateConnectionString(serviceId, port)

      services.push({
        id: serviceId,
        name: serviceId,
        containerName,
        port,
        type: 'database',
        category: 'database',
        connectionString
      })
    }

    return services
  } catch (error) {
    console.error('Error getting running services:', error)
    return []
  }
}

function generateConnectionString(serviceId, port) {
  const host = 'localhost'

  if (serviceId.includes('mysql') || serviceId.includes('mariadb')) {
    return `mysql://root@${host}:${port}/`
  } else if (serviceId.includes('postgres') || serviceId.includes('timescale')) {
    return `postgresql://root@${host}:${port}/postgres`
  } else if (serviceId.includes('mongo')) {
    return `mongodb://${host}:${port}`
  } else if (serviceId.includes('redis') || serviceId.includes('keydb')) {
    return `redis://${host}:${port}`
  } else if (serviceId.includes('neo4j')) {
    return `bolt://${host}:${port}`
  }

  return `http://${host}:${port}`
}

function generateEnvVarsFromServices(services, customEnvVars = {}) {
  const envVars = { ...customEnvVars }

  for (const service of services) {
    const prefix = getEnvPrefix(service.id)

    envVars[`${prefix}_URL`] = service.connectionString
    envVars[`${prefix}_HOST`] = 'localhost'
    envVars[`${prefix}_PORT`] = service.port.toString()
  }

  return envVars
}

function getEnvPrefix(serviceId) {
  if (serviceId.includes('mysql') || serviceId.includes('mariadb')) return 'MYSQL'
  if (serviceId.includes('postgres') || serviceId.includes('timescale')) return 'POSTGRES'
  if (serviceId.includes('mongo')) return 'MONGO'
  if (serviceId.includes('redis') || serviceId.includes('keydb')) return 'REDIS'
  if (serviceId.includes('neo4j')) return 'NEO4J'
  return serviceId.toUpperCase().replace(/-/g, '_')
}

/**
 * GET /api/deployments
 * List all deployments with PM2 status
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
      console.error('Error getting PM2 status:', error)
    }

    await saveDeployments(deployments)

    res.json({
      success: true,
      deployments
    })
  } catch (error) {
    console.error('Error listing deployments:', error)
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to list deployments'
    })
  }
})

/**
 * POST /api/deployments
 * Create new deployment - EXACT replica of old POST handler
 */
router.post('/', async (req, res) => {
  try {
    const {
      repoId,
      repoName,
      repoPath,
      selectedServices = [],
      customEnvVars = {},
      domain
    } = req.body

    // Detect framework
    const framework = await detectFramework(repoPath)
    console.log(`Detected framework: ${getFrameworkDisplayName(framework.type)}`)

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
      console.error('Deployment error:', error)
    })

    res.json({
      success: true,
      deployment,
      message: 'Deployment started'
    })
  } catch (error) {
    console.error('Error creating deployment:', error)
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to create deployment'
    })
  }
})

/**
 * Deploy app - Real-time streaming via WebSocket
 */
async function deployApp(deployment) {
  const logStream = await fs.open(deployment.buildLogs, 'w')

  // Helper to log both to file and WebSocket
  async function log(message) {
    await logStream.writeFile(message)
    emitLog(deployment.id, message)
  }

  try {
    await log(`[${new Date().toISOString()}] Starting deployment for ${deployment.repoName}\n`)
    await log(`[${new Date().toISOString()}] Framework: ${getFrameworkDisplayName(deployment.framework)}\n`)
    await log(`[${new Date().toISOString()}] Port: ${deployment.port}\n\n`)

    // Install dependencies
    await log(`[${new Date().toISOString()}] Installing dependencies...\n`)
    await runCommandWithLogs(
      'npm install',
      { cwd: deployment.repoPath, timeout: 600000 },
      deployment.id
    )

    // Build if needed
    if (deployment.buildCommand) {
      await log(`\n[${new Date().toISOString()}] Building application...\n`)
      await runCommandWithLogs(
        deployment.buildCommand,
        { cwd: deployment.repoPath, timeout: 600000 },
        deployment.id
      )
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
    await log(`\n[${new Date().toISOString()}] Starting application with PM2...\n`)
    await runCommandWithLogs(
      `pm2 start ${ecosystemPath}`,
      { cwd: deployment.repoPath },
      deployment.id
    )

    // Save PM2 config
    await execAsync('pm2 save')

    // Open firewall port
    await log(`\n[${new Date().toISOString()}] Opening firewall port ${deployment.port}...\n`)
    try {
      await execAsync(`ufw allow ${deployment.port}/tcp comment 'Deployment: ${deployment.repoName}'`)
      await log(`[${new Date().toISOString()}] ✓ Port ${deployment.port} opened in firewall\n`)
    } catch (error) {
      await log(`[${new Date().toISOString()}] ⚠ Warning: Could not open firewall port: ${error.message}\n`)
    }

    // Update deployment status
    const deployments = await loadDeployments()
    const index = deployments.findIndex(d => d.id === deployment.id)
    if (index !== -1) {
      deployments[index].status = 'running'
      deployments[index].lastDeployedAt = new Date().toISOString()
      await saveDeployments(deployments)
    }

    await log(`\n[${new Date().toISOString()}] ✅ Deployment completed successfully!\n`)
    await log(`[${new Date().toISOString()}] Application running on http://localhost:${deployment.port}\n`)

  } catch (error) {
    await log(`\n[${new Date().toISOString()}] ❌ Deployment failed: ${error.message}\n`)
    await log(error.stack || '')

    // Update deployment status to failed
    const deployments = await loadDeployments()
    const index = deployments.findIndex(d => d.id === deployment.id)
    if (index !== -1) {
      deployments[index].status = 'failed'
      deployments[index].error = error.message
      await saveDeployments(deployments)
    }
  } finally {
    await logStream.close()
  }
}

/**
 * POST /api/deployments/:id/action
 * Deployment actions (start, stop, restart, delete, rebuild)
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

    switch (action) {
      case 'start':
        await execAsync(`pm2 start ${deployment.pm2Name}`)
        deployment.status = 'running'
        await saveDeployments(deployments)
        return res.json({ success: true, message: `${deployment.repoName} started` })

      case 'stop':
        await execAsync(`pm2 stop ${deployment.pm2Name}`)
        deployment.status = 'stopped'
        await saveDeployments(deployments)
        return res.json({ success: true, message: `${deployment.repoName} stopped` })

      case 'restart':
        await execAsync(`pm2 restart ${deployment.pm2Name}`)
        deployment.status = 'running'
        await saveDeployments(deployments)
        return res.json({ success: true, message: `${deployment.repoName} restarted` })

      case 'delete':
        // Stop and delete PM2 process
        try {
          await execAsync(`pm2 delete ${deployment.pm2Name}`)
          await execAsync('pm2 save')
        } catch {}

        // Delete ecosystem config
        try {
          const ecosystemPath = path.join(deployment.repoPath, `ecosystem.${deployment.id}.config.js`)
          await fs.unlink(ecosystemPath)
        } catch {}

        // Remove from deployments array
        const newDeployments = deployments.filter(d => d.id !== id)
        await saveDeployments(newDeployments)

        return res.json({ success: true, message: `${deployment.repoName} deployment deleted` })

      case 'rebuild':
        // Stop current deployment
        try {
          await execAsync(`pm2 stop ${deployment.pm2Name}`)
        } catch {}

        deployment.status = 'building'
        await saveDeployments(deployments)

        // Trigger rebuild
        deployApp(deployment).catch(error => {
          console.error('Rebuild error:', error)
        })

        return res.json({ success: true, message: `${deployment.repoName} rebuild started` })

      default:
        return res.status(400).json({ success: false, error: 'Invalid action' })
    }
  } catch (error) {
    console.error('Deployment action error:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

/**
 * GET /api/deployments/services
 * Get running Docker services
 */
router.get('/services', async (req, res) => {
  try {
    const services = await getRunningServices()
    res.json({ success: true, services })
  } catch (error) {
    console.error('Error getting services:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

/**
 * GET /api/deployments/:id/logs
 * Get deployment logs
 */
router.get('/:id/logs', async (req, res) => {
  try {
    const { id } = req.params
    const { type = 'build', lines = 100 } = req.query

    const deployments = await loadDeployments()
    const deployment = deployments.find(d => d.id === id)

    if (!deployment) {
      return res.status(404).json({ success: false, error: 'Deployment not found' })
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
        const recentLogs = logLines.slice(-lines).join('\n')
        res.json({ success: true, logs: recentLogs })
      } else {
        res.json({ success: true, logs: 'No logs available yet' })
      }
    } catch {
      res.json({ success: true, logs: 'No logs available yet' })
    }
  } catch (error) {
    console.error('Error getting logs:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

module.exports = router
