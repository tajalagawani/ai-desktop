import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs/promises'
import path from 'path'
import { exec } from 'child_process'
import { promisify } from 'util'
import { DeploymentConfig } from '@/lib/deployment/types'
import { detectFramework, getFrameworkDisplayName } from '@/lib/deployment/detector'
import { getRunningServices, generateEnvVarsFromServices } from '@/lib/deployment/services'

const execAsync = promisify(exec)

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
async function loadDeployments(): Promise<DeploymentConfig[]> {
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
async function saveDeployments(deployments: DeploymentConfig[]): Promise<void> {
  await ensureDataDir()
  await fs.writeFile(
    DEPLOYMENTS_FILE,
    JSON.stringify({ deployments }, null, 2),
    'utf-8'
  )
}

// Find available port
async function findAvailablePort(deployments: DeploymentConfig[]): Promise<number> {
  const usedPorts = new Set(deployments.map(d => d.port))
  for (let port = PORT_RANGE_START; port <= PORT_RANGE_END; port++) {
    if (!usedPorts.has(port)) {
      return port
    }
  }
  throw new Error('No available ports in range 3050-3999')
}

// GET - List all deployments
export async function GET(request: NextRequest) {
  try {
    const deployments = await loadDeployments()

    // Get PM2 status for each deployment
    try {
      const { stdout } = await execAsync('pm2 jlist')
      const pm2List = JSON.parse(stdout)

      for (const deployment of deployments) {
        const pm2App = pm2List.find((app: any) => app.name === deployment.pm2Name)
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

    return NextResponse.json({
      success: true,
      deployments
    })
  } catch (error: any) {
    console.error('Error listing deployments:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to list deployments' },
      { status: 500 }
    )
  }
}

// POST - Create new deployment
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      repoId,
      repoName,
      repoPath,
      selectedServices = [],
      customEnvVars = {},
      domain
    } = body

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
    const deployment: DeploymentConfig = {
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

    return NextResponse.json({
      success: true,
      deployment,
      message: 'Deployment started'
    })
  } catch (error: any) {
    console.error('Error creating deployment:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to create deployment' },
      { status: 500 }
    )
  }
}

// Deploy app (async function)
async function deployApp(deployment: DeploymentConfig) {
  const logStream = await fs.open(deployment.buildLogs!, 'w')

  try {
    await logStream.writeFile(`[${new Date().toISOString()}] Starting deployment for ${deployment.repoName}\n`)
    await logStream.writeFile(`[${new Date().toISOString()}] Framework: ${getFrameworkDisplayName(deployment.framework)}\n`)
    await logStream.writeFile(`[${new Date().toISOString()}] Port: ${deployment.port}\n\n`)

    // Install dependencies
    await logStream.writeFile(`[${new Date().toISOString()}] Installing dependencies...\n`)
    const { stdout: installOutput, stderr: installError } = await execAsync(
      'npm install',
      { cwd: deployment.repoPath, timeout: 600000 } // 10 min timeout
    )
    await logStream.writeFile(installOutput)
    if (installError) await logStream.writeFile(installError)

    // Build if needed
    if (deployment.buildCommand) {
      await logStream.writeFile(`\n[${new Date().toISOString()}] Building application...\n`)
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
    await logStream.writeFile(`\n[${new Date().toISOString()}] Starting application with PM2...\n`)
    const { stdout: pm2Output } = await execAsync(
      `pm2 start ${ecosystemPath}`,
      { cwd: deployment.repoPath }
    )
    await logStream.writeFile(pm2Output)

    // Save PM2 config
    await execAsync('pm2 save')

    // Update deployment status
    const deployments = await loadDeployments()
    const index = deployments.findIndex(d => d.id === deployment.id)
    if (index !== -1) {
      deployments[index].status = 'running'
      deployments[index].lastDeployedAt = new Date().toISOString()
      await saveDeployments(deployments)
    }

    await logStream.writeFile(`\n[${new Date().toISOString()}] ✅ Deployment completed successfully!\n`)
    await logStream.writeFile(`[${new Date().toISOString()}] Application running on http://localhost:${deployment.port}\n`)

  } catch (error: any) {
    await logStream.writeFile(`\n[${new Date().toISOString()}] ❌ Deployment failed: ${error.message}\n`)
    await logStream.writeFile(error.stack || '')

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
