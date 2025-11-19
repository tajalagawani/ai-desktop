/**
 * Service Manager API Routes
 * Handles Docker services installation and management
 * Uses the SAME logic as frontend - reads from Docker, not database
 */

const express = require('express')
const router = express.Router()
const { exec } = require('child_process')
const { promisify } = require('util')
const fs = require('fs').promises
const path = require('path')

const execAsync = promisify(exec)

// Load installable services from JSON file
const DATA_FILE = path.join(__dirname, '../../../data/installable-services.json')

async function getInstallableServices() {
  try {
    const content = await fs.readFile(DATA_FILE, 'utf8')
    return JSON.parse(content)
  } catch (error) {
    console.warn('[Services] Could not load installable services:', error.message)
    return []
  }
}

/**
 * GET /api/services
 * List all installable services and their running status
 */
router.get('/', async (req, res) => {
  try {
    // Check Docker availability
    let dockerInstalled = false
    try {
      await execAsync('docker --version')
      dockerInstalled = true
    } catch {
      dockerInstalled = false
    }

    // Get all installable services
    const installableServices = await getInstallableServices()

    // Get running Docker containers with our label
    let runningContainers = []
    if (dockerInstalled) {
      try {
        const { stdout } = await execAsync(
          'docker ps --filter "label=ai-desktop-service=true" --format "{{.Names}}|{{.Ports}}|{{.Status}}"'
        )
        if (stdout.trim()) {
          runningContainers = stdout.trim().split('\n').map(line => {
            const [containerName, ports, status] = line.split('|')
            const serviceId = containerName.replace('ai-desktop-', '')
            const portMatch = ports.match(/0\.0\.0\.0:(\d+)/)
            const port = portMatch ? parseInt(portMatch[1]) : null

            return { serviceId, containerName, port, status }
          })
        }
      } catch (error) {
        console.warn('[Services] Could not get running containers:', error.message)
      }
    }

    // Get all containers (including stopped ones) to check installed status
    let allContainers = []
    if (dockerInstalled) {
      try {
        const { stdout } = await execAsync(
          'docker ps -a --filter "label=ai-desktop-service=true" --format "{{.Names}}|{{.Status}}"'
        )
        if (stdout.trim()) {
          allContainers = stdout.trim().split('\n').map(line => {
            const [containerName, status] = line.split('|')
            const serviceId = containerName.replace('ai-desktop-', '')
            const isRunning = status.toLowerCase().includes('up')
            return { serviceId, containerName, isRunning }
          })
        }
      } catch (error) {
        console.warn('[Services] Could not get all containers:', error.message)
      }
    }

    // Combine installable services with running status
    const services = installableServices.map(serviceConfig => {
      const container = allContainers.find(c => c.serviceId === serviceConfig.id)
      const running = runningContainers.find(c => c.serviceId === serviceConfig.id)

      return {
        id: serviceConfig.id,
        name: serviceConfig.name,
        category: serviceConfig.category,
        description: serviceConfig.description,
        icon: serviceConfig.icon,
        iconType: serviceConfig.iconType,
        installMethod: serviceConfig.installMethod,
        dockerImage: serviceConfig.dockerImage,
        ports: serviceConfig.ports,
        volumes: serviceConfig.volumes,
        environment: serviceConfig.environment,
        installed: !!container,
        status: running ? 'running' : 'stopped',
        containerName: container?.containerName || `ai-desktop-${serviceConfig.id}`,
        port: running?.port || (serviceConfig.ports?.[0] || null),
        defaultCredentials: serviceConfig.defaultCredentials,
        windowComponent: serviceConfig.windowComponent,
        defaultWidth: serviceConfig.defaultWidth,
        defaultHeight: serviceConfig.defaultHeight,
      }
    })

    res.json({
      success: true,
      dockerInstalled,
      services,
      count: services.length
    })
  } catch (error) {
    console.error('[API Services GET] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/services
 * Perform service actions (install, start, stop, restart, remove, logs)
 */
router.post('/', async (req, res) => {
  try {
    const { action, serviceId } = req.body

    if (!action) {
      return res.status(400).json({
        success: false,
        error: 'Action is required'
      })
    }

    if (!serviceId) {
      return res.status(400).json({
        success: false,
        error: 'Service ID is required'
      })
    }

    console.log(`[API Services] Action: ${action} for service: ${serviceId}`)

    const containerName = `ai-desktop-${serviceId}`
    const installableServices = await getInstallableServices()
    const serviceConfig = installableServices.find(s => s.id === serviceId)

    if (!serviceConfig) {
      return res.status(404).json({
        success: false,
        error: 'Service not found'
      })
    }

    // Handle install action
    if (action === 'install') {
      try {
        // Build docker run command
        let dockerCmd = `docker run -d --name ${containerName} --label ai-desktop-service=true`

        // Add port mappings
        if (serviceConfig.ports && serviceConfig.ports.length > 0) {
          for (const port of serviceConfig.ports) {
            dockerCmd += ` -p ${port}:${port}`
          }
        }

        // Add environment variables
        if (serviceConfig.environment) {
          for (const [key, value] of Object.entries(serviceConfig.environment)) {
            dockerCmd += ` -e ${key}="${value}"`
          }
        }

        // Add volumes
        if (serviceConfig.volumes && serviceConfig.volumes.length > 0) {
          for (const volume of serviceConfig.volumes) {
            const volumeName = `${containerName}-${volume.replace(/\//g, '-').replace(/^-+/, '')}`
            dockerCmd += ` -v ${volumeName}:${volume}`
          }
        }

        // Add restart policy
        dockerCmd += ` --restart unless-stopped`

        // Add image
        dockerCmd += ` ${serviceConfig.dockerImage}`

        console.log(`[Install] Running: ${dockerCmd}`)

        // Pull image first
        await execAsync(`docker pull ${serviceConfig.dockerImage}`)

        // Run container
        await execAsync(dockerCmd)

        // Broadcast service update to all connected clients
        if (global.socketIO && global.socketIO.io) {
          global.socketIO.io.emit('services:updated', { serviceId, action: 'install' })
        }

        return res.json({
          success: true,
          message: `${serviceConfig.name} installed and started successfully`
        })
      } catch (error) {
        console.error('[Install] Error:', error)
        return res.status(500).json({
          success: false,
          error: `Failed to install service: ${error.message}`
        })
      }
    }

    // Handle different actions
    switch (action) {
      case 'start':
        try {
          await execAsync(`docker start ${containerName}`)

          // Broadcast service update
          if (global.socketIO && global.socketIO.io) {
            global.socketIO.io.emit('services:updated', { serviceId, action: 'start' })
          }

          res.json({
            success: true,
            message: `${serviceConfig.name} started`
          })
        } catch (error) {
          throw new Error(`Failed to start service: ${error.message}`)
        }
        break

      case 'stop':
        try {
          await execAsync(`docker stop ${containerName}`)

          // Broadcast service update
          if (global.socketIO && global.socketIO.io) {
            global.socketIO.io.emit('services:updated', { serviceId, action: 'stop' })
          }

          res.json({
            success: true,
            message: `${serviceConfig.name} stopped`
          })
        } catch (error) {
          throw new Error(`Failed to stop service: ${error.message}`)
        }
        break

      case 'restart':
        try {
          await execAsync(`docker restart ${containerName}`)

          // Broadcast service update
          if (global.socketIO && global.socketIO.io) {
            global.socketIO.io.emit('services:updated', { serviceId, action: 'restart' })
          }

          res.json({
            success: true,
            message: `${serviceConfig.name} restarted`
          })
        } catch (error) {
          throw new Error(`Failed to restart service: ${error.message}`)
        }
        break

      case 'remove':
        try {
          // Stop and remove container
          await execAsync(`docker rm -f ${containerName}`)

          // Remove volumes
          const volumePrefix = `${containerName}-`
          try {
            const { stdout: volumeList } = await execAsync(`docker volume ls -q --filter "name=${volumePrefix}"`)
            const volumes = volumeList.trim().split('\n').filter(Boolean)
            for (const volume of volumes) {
              await execAsync(`docker volume rm ${volume}`)
            }
          } catch (volError) {
            console.warn('Error removing volumes:', volError.message)
          }

          // Broadcast service update
          if (global.socketIO && global.socketIO.io) {
            global.socketIO.io.emit('services:updated', { serviceId, action: 'remove' })
          }

          res.json({
            success: true,
            message: `${serviceConfig.name} completely removed`
          })
        } catch (error) {
          throw new Error(`Failed to remove service: ${error.message}`)
        }
        break

      case 'logs':
        try {
          const { stdout } = await execAsync(`docker logs --tail 100 ${containerName}`)
          res.json({
            success: true,
            logs: stdout
          })
        } catch (error) {
          throw new Error(`Failed to get logs: ${error.message}`)
        }
        break

      default:
        res.status(400).json({
          success: false,
          error: `Invalid action: ${action}`
        })
    }
  } catch (error) {
    console.error('[API Services POST] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

module.exports = router
