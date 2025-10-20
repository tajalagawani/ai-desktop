import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs/promises'
import path from 'path'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

// Flow file directory
const FLOWS_DIR = path.join(process.cwd(), 'components', 'apps', 'act-docker', 'flows')

interface FlowEndpoint {
  path: string
  method: string
  description: string
}

interface FlowService {
  id: string
  name: string
  description: string
  port?: number
  status: 'running' | 'stopped' | 'not-deployed'
  containerName: string
  endpoints: FlowEndpoint[]
  nodeTypes: string[]
  totalNodes: number
  aciNodes: number
  file: string
  lastModified: string
}

// Parse flow file to extract complete metadata and ACI routes
async function parseFlowFile(flowPath: string): Promise<Partial<FlowService>> {
  try {
    const content = await fs.readFile(flowPath, 'utf-8')
    const lines = content.split('\n')
    const stats = await fs.stat(flowPath)

    let workflowName = ''
    let description = ''
    let port: number | undefined
    let agentName = ''
    const endpoints: FlowEndpoint[] = []
    const nodeTypes = new Set<string>()
    let totalNodes = 0
    let aciNodes = 0

    let currentNode = ''
    let currentRouteInfo: any = {}

    for (const line of lines) {
      const trimmed = line.trim()

      // Parse workflow metadata
      if (trimmed.startsWith('name =')) {
        const value = trimmed.split('=')[1]
        if (value) {
          workflowName = value.trim().replace(/["']/g, '')
        }
      }
      if (trimmed.startsWith('description =')) {
        const value = trimmed.split('=')[1]
        if (value) {
          description = value.trim().replace(/["']/g, '')
        }
      }
      if (trimmed.startsWith('port =')) {
        const value = trimmed.split('=')[1]
        if (value) {
          port = parseInt(value.trim())
        }
      }
      if (trimmed.startsWith('agent_name =')) {
        const value = trimmed.split('=')[1]
        if (value) {
          agentName = value.trim().replace(/["']/g, '')
        }
      }

      // Track nodes
      if (trimmed.startsWith('[node:')) {
        currentNode = trimmed
        currentRouteInfo = {}
        totalNodes++
      }

      // Track node types
      if (currentNode && trimmed.startsWith('type =')) {
        const value = trimmed.split('=')[1]
        if (value) {
          const nodeType = value.trim().replace(/["']/g, '')
          nodeTypes.add(nodeType)

          if (nodeType === 'aci') {
            aciNodes++
          }
        }
      }

      // Parse ACI node properties
      if (currentNode.includes('[node:') && trimmed.startsWith('route_path =')) {
        const value = trimmed.split('=')[1]
        if (value) {
          currentRouteInfo.path = value.trim().replace(/["']/g, '')
        }
      }

      if (currentNode.includes('[node:') && trimmed.startsWith('methods =')) {
        const value = trimmed.split('=')[1]
        if (value) {
          const methodsStr = value.trim()
          const methods = methodsStr
            .replace(/[\[\]]/g, '')
            .split(',')
            .map(m => m.trim().replace(/["']/g, ''))
          currentRouteInfo.methods = methods
        }
      }

      if (currentNode.includes('[node:') && trimmed.startsWith('description =')) {
        const value = trimmed.split('=')[1]
        if (value) {
          currentRouteInfo.description = value.trim().replace(/["']/g, '')
        }
      }

      // When we have complete route info, add it
      if (currentRouteInfo.path && currentRouteInfo.methods) {
        for (const method of currentRouteInfo.methods) {
          endpoints.push({
            path: currentRouteInfo.path,
            method,
            description: currentRouteInfo.description || ''
          })
        }
        currentRouteInfo = {} // Reset for next node
      }
    }

    return {
      name: workflowName || path.basename(flowPath, '.flow'),
      description: description || 'ACT Flow',
      port,
      endpoints,
      nodeTypes: Array.from(nodeTypes),
      totalNodes,
      aciNodes,
      lastModified: stats.mtime.toISOString()
    }
  } catch (error) {
    console.error(`Failed to parse flow file ${flowPath}:`, error)
    return {}
  }
}

// Get container status for a flow
async function getFlowStatus(flowId: string): Promise<'running' | 'stopped' | 'not-deployed'> {
  try {
    const containerName = `act-${flowId}`
    const { stdout } = await execAsync(`docker inspect --format='{{.State.Status}}' ${containerName}`)
    return stdout.trim() === 'running' ? 'running' : 'stopped'
  } catch {
    return 'not-deployed'
  }
}

// GET /api/catalog/flows - Get all ACT flows with metadata
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const status = searchParams.get('status') // running | stopped | not-deployed | all
    const hasEndpoints = searchParams.get('has_endpoints') // true | false

    // Read all flow files
    const files = await fs.readdir(FLOWS_DIR)
    const flowFiles = files.filter(f => f.endsWith('.flow'))

    const flows: FlowService[] = []

    // Process each flow file
    for (const file of flowFiles) {
      const flowPath = path.join(FLOWS_DIR, file)
      const flowId = path.basename(file, '.flow')
      const flowMetadata = await parseFlowFile(flowPath)
      const flowStatus = await getFlowStatus(flowId)

      const flow: FlowService = {
        id: flowId,
        name: flowMetadata.name || flowId,
        description: flowMetadata.description || '',
        port: flowMetadata.port,
        status: flowStatus,
        containerName: `act-${flowId}`,
        endpoints: flowMetadata.endpoints || [],
        nodeTypes: flowMetadata.nodeTypes || [],
        totalNodes: flowMetadata.totalNodes || 0,
        aciNodes: flowMetadata.aciNodes || 0,
        file,
        lastModified: flowMetadata.lastModified || ''
      }

      flows.push(flow)
    }

    // Apply filters
    let filteredFlows = flows

    if (status && status !== 'all') {
      filteredFlows = filteredFlows.filter(f => f.status === status)
    }

    if (hasEndpoints === 'true') {
      filteredFlows = filteredFlows.filter(f => f.endpoints.length > 0)
    } else if (hasEndpoints === 'false') {
      filteredFlows = filteredFlows.filter(f => f.endpoints.length === 0)
    }

    // Calculate statistics
    const stats = {
      total: filteredFlows.length,
      running: filteredFlows.filter(f => f.status === 'running').length,
      stopped: filteredFlows.filter(f => f.status === 'stopped').length,
      notDeployed: filteredFlows.filter(f => f.status === 'not-deployed').length,
      withEndpoints: filteredFlows.filter(f => f.endpoints.length > 0).length,
      totalEndpoints: filteredFlows.reduce((sum, f) => sum + f.endpoints.length, 0),
      totalNodes: filteredFlows.reduce((sum, f) => sum + f.totalNodes, 0),
      totalAciNodes: filteredFlows.reduce((sum, f) => sum + f.aciNodes, 0)
    }

    return NextResponse.json({
      success: true,
      flows: filteredFlows,
      stats
    })

  } catch (error: any) {
    console.error('Error fetching flow catalog:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to fetch flow catalog' },
      { status: 500 }
    )
  }
}

// GET /api/catalog/flows/[id] - Get specific flow details
export async function GET_FLOW(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const flowFile = `${params.id}.flow`
    const flowPath = path.join(FLOWS_DIR, flowFile)

    // Check if flow exists
    try {
      await fs.access(flowPath)
    } catch {
      return NextResponse.json(
        { error: 'Flow not found' },
        { status: 404 }
      )
    }

    const flowMetadata = await parseFlowFile(flowPath)
    const flowStatus = await getFlowStatus(params.id)

    // Get container logs if running
    let logs: string | null = null
    if (flowStatus === 'running') {
      try {
        const { stdout } = await execAsync(`docker logs --tail 50 act-${params.id}`)
        logs = stdout
      } catch {}
    }

    const flow: FlowService = {
      id: params.id,
      name: flowMetadata.name || params.id,
      description: flowMetadata.description || '',
      port: flowMetadata.port,
      status: flowStatus,
      containerName: `act-${params.id}`,
      endpoints: flowMetadata.endpoints || [],
      nodeTypes: flowMetadata.nodeTypes || [],
      totalNodes: flowMetadata.totalNodes || 0,
      aciNodes: flowMetadata.aciNodes || 0,
      file: flowFile,
      lastModified: flowMetadata.lastModified || ''
    }

    return NextResponse.json({
      success: true,
      flow,
      logs
    })

  } catch (error: any) {
    console.error('Error fetching flow details:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to fetch flow details' },
      { status: 500 }
    )
  }
}