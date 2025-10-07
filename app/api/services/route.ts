import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import { INSTALLABLE_SERVICES } from '@/data/installable-services'

const execAsync = promisify(exec)

// UFW profile mapping for services
const UFW_PROFILES: Record<string, string> = {
  'mysql': 'AI-Desktop-MySQL',
  'mysql57': 'AI-Desktop-MySQL57',
  'mariadb': 'AI-Desktop-MariaDB',
  'postgresql': 'AI-Desktop-PostgreSQL',
  'timescaledb': 'AI-Desktop-TimescaleDB',
  'mongodb': 'AI-Desktop-MongoDB',
  'redis': 'AI-Desktop-Redis',
  'keydb': 'AI-Desktop-KeyDB',
  'couchdb': 'AI-Desktop-CouchDB',
  'arangodb': 'AI-Desktop-ArangoDB',
  'memcached': 'AI-Desktop-Memcached',
  'neo4j': 'AI-Desktop-Neo4j',
  'influxdb': 'AI-Desktop-InfluxDB',
  'questdb': 'AI-Desktop-QuestDB',
  'victoriametrics': 'AI-Desktop-VictoriaMetrics',
  'cassandra': 'AI-Desktop-Cassandra',
  'scylladb': 'AI-Desktop-ScyllaDB',
  'clickhouse': 'AI-Desktop-ClickHouse',
  'elasticsearch': 'AI-Desktop-Elasticsearch',
  'nginx': 'AI-Desktop-Nginx',
  'phpmyadmin': 'AI-Desktop-PHPMyAdmin',
  'adminer': 'AI-Desktop-Adminer',
  'rabbitmq': 'AI-Desktop-RabbitMQ',
  'mssql': 'AI-Desktop-MSSQL',
  'cockroachdb': 'AI-Desktop-CockroachDB'
}

// Check if Docker is installed
async function checkDocker(): Promise<boolean> {
  try {
    await execAsync('docker --version')
    return true
  } catch {
    return false
  }
}

// Check if UFW is installed and enabled
async function checkUFW(): Promise<{installed: boolean, enabled: boolean}> {
  try {
    await execAsync('which ufw')
    try {
      const { stdout } = await execAsync('sudo ufw status')
      const enabled = stdout.includes('Status: active')
      return { installed: true, enabled }
    } catch {
      return { installed: true, enabled: false }
    }
  } catch {
    return { installed: false, enabled: false }
  }
}

// Open firewall port using UFW profile or raw port with rate limiting
async function openFirewallPort(serviceId: string, ports: number[]): Promise<{success: boolean, method: string, message: string}> {
  const ufwStatus = await checkUFW()

  if (!ufwStatus.installed) {
    return { success: false, method: 'none', message: 'UFW not installed' }
  }

  if (!ufwStatus.enabled) {
    return { success: false, method: 'none', message: 'UFW not enabled' }
  }

  // Try UFW application profile first
  const profileName = UFW_PROFILES[serviceId]
  if (profileName) {
    try {
      await execAsync(`sudo ufw allow '${profileName}' comment 'AI Desktop - ${profileName}'`)
      return { success: true, method: 'profile', message: `Opened using profile: ${profileName}` }
    } catch (error: any) {
      console.log(`Profile ${profileName} not found, falling back to raw ports`)
    }
  }

  // Fallback to raw ports with rate limiting for security
  try {
    for (const port of ports) {
      // Add rate limiting to prevent brute force attacks
      await execAsync(`sudo ufw limit ${port}/tcp comment 'AI Desktop - ${serviceId}'`)
    }
    return { success: true, method: 'port', message: `Opened ports ${ports.join(', ')} with rate limiting` }
  } catch (error: any) {
    return { success: false, method: 'error', message: `Failed to open ports: ${error.message}` }
  }
}

// Close firewall port
async function closeFirewallPort(serviceId: string, ports: number[]): Promise<void> {
  const ufwStatus = await checkUFW()
  if (!ufwStatus.installed || !ufwStatus.enabled) return

  // Try to delete by profile first
  const profileName = UFW_PROFILES[serviceId]
  if (profileName) {
    try {
      await execAsync(`sudo ufw delete allow '${profileName}'`)
      return
    } catch {}
  }

  // Fallback to deleting by port
  for (const port of ports) {
    try {
      await execAsync(`sudo ufw delete limit ${port}/tcp`)
    } catch {
      try {
        await execAsync(`sudo ufw delete allow ${port}/tcp`)
      } catch {}
    }
  }
}

// Get list of installed services
async function getInstalledServices() {
  try {
    const { stdout } = await execAsync('docker ps -a --format "{{.Names}}" --filter "label=ai-desktop-service=true"')
    return stdout.trim().split('\n').filter(Boolean)
  } catch {
    return []
  }
}

// Get service status
async function getServiceStatus(serviceName: string) {
  try {
    const { stdout } = await execAsync(`docker inspect --format='{{.State.Status}}' ${serviceName}`)
    return stdout.trim()
  } catch {
    return 'not-found'
  }
}

// GET - List all services and their status
export async function GET(request: NextRequest) {
  try {
    const dockerInstalled = await checkDocker()

    if (!dockerInstalled) {
      return NextResponse.json({
        error: 'Docker is not installed. Please install Docker first.',
        dockerInstalled: false
      }, { status: 400 })
    }

    const installedContainers = await getInstalledServices()

    const servicesWithStatus = await Promise.all(
      INSTALLABLE_SERVICES.map(async (service) => {
        const containerName = `ai-desktop-${service.id}`
        const isInstalled = installedContainers.includes(containerName)
        const status = isInstalled ? await getServiceStatus(containerName) : 'not-installed'

        return {
          ...service,
          installed: isInstalled,
          status,
          containerName
        }
      })
    )

    return NextResponse.json({
      dockerInstalled: true,
      services: servicesWithStatus
    })
  } catch (error: any) {
    console.error('Error listing services:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to list services' },
      { status: 500 }
    )
  }
}

// POST - Install, start, stop, or remove a service
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, serviceId } = body

    const service = INSTALLABLE_SERVICES.find(s => s.id === serviceId)
    if (!service) {
      return NextResponse.json({ error: 'Service not found' }, { status: 404 })
    }

    const containerName = `ai-desktop-${service.id}`

    if (action === 'install') {
      // Build Docker run command
      // IMPORTANT: Bind to 0.0.0.0 to expose on all network interfaces
      const ports = service.ports?.map(p => `-p 0.0.0.0:${p}:${p}`).join(' ') || ''

      // Create named volumes for data persistence
      const volumes = service.volumes?.map(v => {
        const volumeName = `${containerName}-${v.replace(/\//g, '-')}`
        return `-v ${volumeName}:${v}`
      }).join(' ') || ''

      const env = Object.entries(service.environment || {})
        .map(([key, val]) => `-e "${key}=${val}"`)
        .join(' ')

      const command = `docker run -d --name ${containerName} --label ai-desktop-service=true --restart unless-stopped ${ports} ${volumes} ${env} ${service.dockerImage}`

      console.log('Installing service:', command)

      try {
        // Open firewall ports BEFORE installing container
        let firewallResult = { success: false, method: 'none', message: 'No firewall' }
        if (service.ports && service.ports.length > 0) {
          firewallResult = await openFirewallPort(service.id, service.ports)
          console.log('Firewall result:', firewallResult)
        }

        // Now install the Docker container
        const { stdout, stderr } = await execAsync(command, { timeout: 300000 }) // 5 min timeout for large images

        return NextResponse.json({
          success: true,
          message: `${service.name} installed successfully. ${firewallResult.message}`,
          output: stdout,
          containerName,
          accessUrl: service.ports?.[0] ? `http://YOUR_VPS_IP:${service.ports[0]}` : null,
          firewall: firewallResult
        })
      } catch (error: any) {
        // Clean up failed container
        try {
          await execAsync(`docker rm -f ${containerName}`)
        } catch {}

        throw new Error(`Installation failed: ${error.message}`)
      }
    }

    if (action === 'start') {
      await execAsync(`docker start ${containerName}`)
      return NextResponse.json({
        success: true,
        message: `${service.name} started`
      })
    }

    if (action === 'stop') {
      await execAsync(`docker stop ${containerName}`)
      return NextResponse.json({
        success: true,
        message: `${service.name} stopped`
      })
    }

    if (action === 'restart') {
      await execAsync(`docker restart ${containerName}`)
      return NextResponse.json({
        success: true,
        message: `${service.name} restarted`
      })
    }

    if (action === 'remove') {
      try {
        // 1. Stop and remove Docker container
        await execAsync(`docker rm -f ${containerName}`)

        // 2. Remove all associated volumes to free up disk space
        const volumePrefix = `${containerName}-`
        try {
          const { stdout: volumeList } = await execAsync(`docker volume ls -q --filter "name=${volumePrefix}"`)
          const volumes = volumeList.trim().split('\n').filter(Boolean)

          if (volumes.length > 0) {
            console.log(`Removing volumes for ${containerName}:`, volumes)
            for (const volume of volumes) {
              await execAsync(`docker volume rm ${volume}`)
            }
          }
        } catch (volError: any) {
          console.warn('Error removing volumes:', volError.message)
        }

        // 3. Remove Docker image to free up space - FORCE remove all related images
        try {
          // Force remove the image even if it has stopped containers
          await execAsync(`docker rmi -f ${service.dockerImage}`)
          console.log(`Removed Docker image: ${service.dockerImage}`)
        } catch (imgError: any) {
          console.warn('Could not remove image:', imgError.message)
        }

        // Also remove any dangling images to free up space
        try {
          await execAsync(`docker image prune -f`)
          console.log('Cleaned up dangling images')
        } catch (pruneError: any) {
          console.warn('Could not prune dangling images:', pruneError.message)
        }

        // 4. Close firewall ports for security
        if (service.ports && service.ports.length > 0) {
          await closeFirewallPort(service.id, service.ports)
        }

        return NextResponse.json({
          success: true,
          message: `${service.name} completely removed (container, volumes, Docker images, and firewall ports)`
        })
      } catch (error: any) {
        throw new Error(`Failed to remove service: ${error.message}`)
      }
    }

    if (action === 'logs') {
      const { stdout } = await execAsync(`docker logs --tail 100 ${containerName}`)
      return NextResponse.json({
        success: true,
        logs: stdout
      })
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
  } catch (error: any) {
    console.error('Error managing service:', error)
    return NextResponse.json(
      { error: error.message || 'Service operation failed' },
      { status: 500 }
    )
  }
}
