import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import { INSTALLABLE_SERVICES } from '@/data/installable-services'

const execAsync = promisify(exec)

// Check if Docker is installed
async function checkDocker(): Promise<boolean> {
  try {
    await execAsync('docker --version')
    return true
  } catch {
    return false
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
      const volumes = service.volumes?.map(v => `-v ${containerName}${v}:${v}`).join(' ') || ''
      const env = Object.entries(service.environment || {})
        .map(([key, val]) => `-e ${key}="${val}"`)
        .join(' ')

      const command = `docker run -d --name ${containerName} --label ai-desktop-service=true --restart unless-stopped ${ports} ${volumes} ${env} ${service.dockerImage}`

      console.log('Installing service:', command)
      const { stdout, stderr } = await execAsync(command)

      return NextResponse.json({
        success: true,
        message: `${service.name} installed successfully. Access it at http://YOUR_VPS_IP:${service.ports?.[0] || 'PORT'}`,
        output: stdout,
        containerName,
        accessUrl: service.ports?.[0] ? `http://YOUR_VPS_IP:${service.ports[0]}` : null
      })
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
      await execAsync(`docker rm -f ${containerName}`)
      return NextResponse.json({
        success: true,
        message: `${service.name} removed`
      })
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
