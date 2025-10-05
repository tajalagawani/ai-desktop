import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs/promises'
import path from 'path'

const execAsync = promisify(exec)

const FLOWS_DIR = path.join(process.cwd(), 'components/apps/act-docker/flows')
const ACT_DOCKER_DIR = path.join(process.cwd(), 'components/apps/act-docker')

interface FlowConfig {
  name: string
  port: number
  mode: string
  agent_name?: string
  description?: string
  file: string
  auto_assigned?: boolean
}

// Parse .flow file to extract configuration
async function parseFlowFile(filePath: string): Promise<Partial<FlowConfig>> {
  try {
    const content = await fs.readFile(filePath, 'utf-8')
    const lines = content.split('\n')

    let port: number | undefined
    let agent_name = ''
    let description = ''
    let mode = 'miniact' // Default to miniact
    let hasAciNode = false
    let hasWorkflow = false

    for (const line of lines) {
      const trimmed = line.trim()

      // Parse port
      if (trimmed.startsWith('port =') || trimmed.startsWith('port=')) {
        const portMatch = trimmed.match(/port\s*=\s*(\d+)/)
        if (portMatch) {
          port = parseInt(portMatch[1], 10)
        }
      }

      // Parse agent name
      if (trimmed.startsWith('agent_name =') || trimmed.startsWith('agent_name=')) {
        const nameMatch = trimmed.match(/agent_name\s*=\s*(.+)/)
        if (nameMatch) {
          agent_name = nameMatch[1].replace(/['"]/g, '').trim()
        }
      }

      // Parse description
      if (trimmed.startsWith('description =') || trimmed.startsWith('description=')) {
        const descMatch = trimmed.match(/description\s*=\s*(.+)/)
        if (descMatch) {
          description = descMatch[1].replace(/['"]/g, '').trim()
        }
      }

      // Detect ACI nodes (agent mode indicator)
      if (trimmed.includes('type = aci') || trimmed.includes('type=aci') ||
          trimmed.includes('type = aci_node') || trimmed.includes('type=aci_node')) {
        hasAciNode = true
      }

      // Detect workflow section
      if (trimmed === '[workflow]') {
        hasWorkflow = true
      }
    }

    // Determine mode based on what we found
    if (hasAciNode) {
      mode = 'agent'
    } else if (hasWorkflow) {
      mode = 'miniact'
    }

    return { port, agent_name, description, mode }
  } catch (error) {
    console.error('Error parsing flow file:', error)
    return {}
  }
}

// Discover all flows in the flows directory
async function discoverFlows(): Promise<FlowConfig[]> {
  try {
    const files = await fs.readdir(FLOWS_DIR)
    const flowFiles = files.filter(f => f.endsWith('.flow'))

    const flows: FlowConfig[] = []

    for (const file of flowFiles) {
      const name = file.replace('.flow', '')
      const filePath = path.join(FLOWS_DIR, file)
      const config = await parseFlowFile(filePath)

      flows.push({
        name,
        file,
        port: config.port || 9999,
        mode: config.mode || 'waiting',
        agent_name: config.agent_name,
        description: config.description,
        auto_assigned: !config.port
      })
    }

    return flows
  } catch (error) {
    console.error('Error discovering flows:', error)
    return []
  }
}

// Get container status and actual port
async function getContainerStatus(flowName: string) {
  try {
    const containerName = `act-${flowName}`

    // Get container state
    const { stdout: stateOutput } = await execAsync(
      `docker inspect ${containerName} --format '{{json .State}}' 2>/dev/null || echo '{}'`
    )

    if (stateOutput.trim() && stateOutput.trim() !== '{}') {
      const state = JSON.parse(stateOutput)

      // Get actual port mapping
      const { stdout: portOutput } = await execAsync(
        `docker port ${containerName} 2>/dev/null || echo ''`
      )

      // Parse port output like "9000/tcp -> 0.0.0.0:9000"
      let actualPort: number | undefined
      const portMatch = portOutput.match(/(\d+)\/tcp -> [\d.:]+:(\d+)/)
      if (portMatch) {
        actualPort = parseInt(portMatch[2], 10)
      }

      return {
        running: state.Running || false,
        status: state.Status || 'unknown',
        started_at: state.StartedAt,
        pid: state.Pid || 0,
        actualPort
      }
    }

    return { running: false, status: 'not_found' }
  } catch (error) {
    return { running: false, status: 'error' }
  }
}

// Get flow health
async function getFlowHealth(port: number) {
  try {
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 3000)

    const response = await fetch(`http://localhost:${port}/health`, {
      signal: controller.signal
    })

    clearTimeout(timeout)

    if (response.ok) {
      const data = await response.json()
      // Normalize status - some flows return "ready", some return "healthy"
      const normalizedStatus = (data.status === 'ready' || data.status === 'healthy') ? 'healthy' : data.status
      return { ...data, status: normalizedStatus }
    }

    return { status: 'unhealthy', code: response.status }
  } catch (error: any) {
    if (error.name === 'AbortError') {
      return { status: 'timeout' }
    }
    return { status: 'unreachable', error: error.message }
  }
}

// Get container logs
async function getContainerLogs(flowName: string, lines: number = 100) {
  try {
    const containerName = `act-${flowName}`
    const { stdout, stderr } = await execAsync(
      `docker logs --tail ${lines} ${containerName} 2>&1`
    )
    return stdout + stderr
  } catch (error: any) {
    return `Error fetching logs: ${error.message}`
  }
}

// Docker compose command (supports both v1 and v2)
async function dockerComposeCommand(command: string, service?: string) {
  try {
    // Try docker compose (v2) first, fallback to docker-compose (v1)
    let composeCmd = 'docker compose'

    // Check if docker compose v2 is available
    try {
      await execAsync('docker compose version', { timeout: 5000 })
    } catch {
      // Fallback to v1
      composeCmd = 'docker-compose'
    }

    const cmd = service
      ? `cd ${ACT_DOCKER_DIR} && ${composeCmd} ${command} ${service}`
      : `cd ${ACT_DOCKER_DIR} && ${composeCmd} ${command}`

    const { stdout, stderr } = await execAsync(cmd, {
      timeout: 30000
    })

    return {
      success: true,
      stdout,
      stderr
    }
  } catch (error: any) {
    return {
      success: false,
      error: error.message
    }
  }
}

// Check if Docker is installed
async function checkDockerInstalled(): Promise<boolean> {
  try {
    await execAsync('docker --version')
    return true
  } catch {
    return false
  }
}

// GET handler - List all flows or get flow details
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const flowName = searchParams.get('flowName')
    const action = searchParams.get('action')

    // Check if Docker is installed
    const dockerInstalled = await checkDockerInstalled()

    if (!dockerInstalled) {
      return NextResponse.json({
        success: false,
        actInstalled: false,
        flows: [],
        error: 'Docker is not installed'
      }, { status: 200 }) // Return 200 so the client can handle it properly
    }

    // Get logs for specific flow
    if (flowName && action === 'logs') {
      const lines = parseInt(searchParams.get('lines') || '100', 10)
      const logs = await getContainerLogs(flowName, lines)

      return NextResponse.json({
        flow: flowName,
        lines,
        logs
      })
    }

    // Discover all flows
    const flows = await discoverFlows()

    // Enrich with runtime status
    for (const flow of flows) {
      const containerStatus = await getContainerStatus(flow.name)
      flow.container = containerStatus as any

      // Use actual port from Docker if available, otherwise use parsed port
      const actualPort = (containerStatus as any).actualPort || flow.port
      flow.port = actualPort

      if (containerStatus.running) {
        console.log(`[Flow Manager] Checking health for ${flow.name} on port ${actualPort}`)
        const health = await getFlowHealth(actualPort)
        console.log(`[Flow Manager] Health result for ${flow.name}:`, health)
        flow.health = health as any
      } else {
        console.log(`[Flow Manager] Container ${flow.name} is not running`)
        flow.health = { status: 'stopped' } as any
      }
    }

    return NextResponse.json({
      success: true,
      actInstalled: true,
      total: flows.length,
      flows,
      timestamp: new Date().toISOString()
    })

  } catch (error: any) {
    console.error('Error in GET /api/flows:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to fetch flows' },
      { status: 500 }
    )
  }
}

// POST handler - Control flows (start, stop, restart, etc.)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, flowName } = body

    if (!flowName) {
      return NextResponse.json(
        { error: 'Flow name is required' },
        { status: 400 }
      )
    }

    const serviceName = `act-${flowName}`
    let result

    switch (action) {
      case 'start':
        // Try to start, if it fails, try up -d to create and start
        result = await dockerComposeCommand('start', serviceName)
        if (!result.success && result.error?.includes('has no container')) {
          // Container doesn't exist, create it
          result = await dockerComposeCommand('up -d', serviceName)
        }
        break

      case 'stop':
        result = await dockerComposeCommand('stop', serviceName)
        break

      case 'restart':
        result = await dockerComposeCommand('restart', serviceName)
        break

      case 'remove':
        result = await dockerComposeCommand('rm -f', serviceName)
        break

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        )
    }

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || 'Action failed' },
        { status: 500 }
      )
    }

    return NextResponse.json({
      success: true,
      message: `Flow '${flowName}' ${action}ed successfully`
    })

  } catch (error: any) {
    console.error('Error in POST /api/flows:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to perform action' },
      { status: 500 }
    )
  }
}
