import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs/promises'
import path from 'path'

const execAsync = promisify(exec)

const FLOWS_DIR = path.join(process.cwd(), '../../act/flows')
const ACT_DOCKER_DIR = path.join(process.cwd(), '../../act')

interface FlowConfig {
  name: string
  port: number
  mode: string
  agent_name?: string
  description?: string
  file: string
  auto_assigned?: boolean
  metadata?: {
    sessionId?: string
    projectName?: string
    createdAt?: string
    [key: string]: any
  }
  container?: any
  health?: any
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
    let inWorkflowSection = false
    let inMetadataSection = false
    let inOtherSection = false
    let metadata: any = {}

    for (const line of lines) {
      const trimmed = line.trim()

      // Track which section we're in
      if (trimmed.startsWith('[')) {
        inWorkflowSection = trimmed === '[workflow]'
        inMetadataSection = trimmed === '[metadata]'
        inOtherSection = !inWorkflowSection && !inMetadataSection && (trimmed.startsWith('[node:') || trimmed.startsWith('[deployment]') || trimmed.startsWith('[parameters]') || trimmed.startsWith('[agent]'))
      }

      // Parse metadata section
      if (inMetadataSection && !inOtherSection) {
        const metaMatch = trimmed.match(/^(\w+)\s*=\s*(.+)$/)
        if (metaMatch) {
          const [, key, value] = metaMatch
          metadata[key] = value.replace(/['"]/g, '').trim()
        }
      }

      // Parse description ONLY from [workflow] section
      if (inWorkflowSection && !inOtherSection && (trimmed.startsWith('description =') || trimmed.startsWith('description='))) {
        const descMatch = trimmed.match(/^description\s*=\s*(.+)$/)
        if (descMatch) {
          description = descMatch[1].replace(/['"]/g, '').trim()
        }
      }

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

    return {
      port,
      agent_name,
      description,
      mode,
      metadata: Object.keys(metadata).length > 0 ? metadata : undefined
    }
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
        auto_assigned: !config.port,
        metadata: config.metadata
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
        console.log(`[Flow Manager] Container ${flow.name} 
          
          
          
          `)
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

// Regenerate docker-compose.yml from flows
async function regenerateDockerCompose(): Promise<{ success: boolean, error?: string }> {
  try {
    console.log('[Flow Manager] 🔄 Regenerating docker-compose.yml...')

    const { stdout, stderr } = await execAsync(
      `cd ${ACT_DOCKER_DIR} && python3 docker-compose-generator.py`,
      { timeout: 30000 }
    )

    console.log('[Flow Manager] ✅ Docker compose regenerated successfully')
    if (stdout) console.log('[Flow Manager] Generator output:', stdout)
    if (stderr) console.log('[Flow Manager] Generator stderr:', stderr)

    return { success: true }
  } catch (error: any) {
    console.error('[Flow Manager] ❌ Failed to regenerate docker-compose.yml:', error.message)
    return { success: false, error: error.message }
  }
}

// POST handler - Control flows (start, stop, restart, etc.)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, flowName } = body

    console.log('[Flow Manager] ========================================')
    console.log('[Flow Manager] POST /api/flows')
    console.log('[Flow Manager]   Action:', action)
    console.log('[Flow Manager]   Flow:', flowName)
    console.log('[Flow Manager] ========================================')

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
        console.log('[Flow Manager] 🚀 Starting flow:', flowName)
        console.log('[Flow Manager] Service name:', serviceName)

        // Regenerate docker-compose.yml to ensure flow is included
        console.log('[Flow Manager] Step 1: Regenerating docker-compose.yml...')
        const regenerateResult = await regenerateDockerCompose()
        if (!regenerateResult.success) {
          console.error('[Flow Manager] ❌ Failed to regenerate compose file')
          return NextResponse.json(
            { error: `Failed to regenerate docker-compose.yml: ${regenerateResult.error}` },
            { status: 500 }
          )
        }

        console.log('[Flow Manager] Step 2: Starting Docker service...')
        // Try to start, if it fails, try up -d to create and start
        result = await dockerComposeCommand('start', serviceName)
        console.log('[Flow Manager] Start result:', result)

        if (!result.success && result.error?.includes('has no container')) {
          console.log('[Flow Manager] Container does not exist, creating with up -d...')
          // Container doesn't exist, create it
          result = await dockerComposeCommand('up -d', serviceName)
          console.log('[Flow Manager] Up -d result:', result)
        }

        if (result.success) {
          console.log('[Flow Manager] ✅ Flow started successfully:', flowName)
        } else {
          console.error('[Flow Manager] ❌ Failed to start flow:', result.error)
        }
        break

      case 'stop':
        console.log('[Flow Manager] 🛑 Stopping flow:', flowName)
        result = await dockerComposeCommand('stop', serviceName)
        console.log('[Flow Manager] Stop result:', result)
        break

      case 'restart':
        console.log('[Flow Manager] 🔄 Restarting flow:', flowName)
        result = await dockerComposeCommand('restart', serviceName)
        console.log('[Flow Manager] Restart result:', result)
        break

      case 'remove':
        console.log('[Flow Manager] 🗑️  Removing flow:', flowName)
        result = await dockerComposeCommand('rm -f', serviceName)
        console.log('[Flow Manager] Remove result:', result)
        break

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        )
    }

    if (!result.success) {
      console.error('[Flow Manager] ========================================')
      console.error('[Flow Manager] ❌ Action failed:', result.error)
      console.error('[Flow Manager] ========================================')
      return NextResponse.json(
        { error: result.error || 'Action failed' },
        { status: 500 }
      )
    }

    console.log('[Flow Manager] ========================================')
    console.log('[Flow Manager] ✅ Action completed successfully')
    console.log(`[Flow Manager] Flow '${flowName}' ${action}ed`)
    console.log('[Flow Manager] ========================================')

    return NextResponse.json({
      success: true,
      message: `Flow '${flowName}' ${action}ed successfully`
    })

  } catch (error: any) {
    console.error('[Flow Manager] ========================================')
    console.error('[Flow Manager] ❌ Exception in POST /api/flows:', error)
    console.error('[Flow Manager] Error message:', error.message)
    console.error('[Flow Manager] Error stack:', error.stack)
    console.error('[Flow Manager] ========================================')
    return NextResponse.json(
      { error: error.message || 'Failed to perform action' },
      { status: 500 }
    )
  }
}
