import { NextRequest, NextResponse } from 'next/server'
import { ServiceMetadata } from '@/lib/service-registry'
import fs from 'fs/promises'
import path from 'path'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

// Flow file directory
const FLOWS_DIR = path.join(process.cwd(), 'components', 'apps', 'act-docker', 'flows')

// Parse flow file to extract metadata and ACI routes
async function parseFlowFile(flowPath: string): Promise<Partial<ServiceMetadata>> {
  try {
    const content = await fs.readFile(flowPath, 'utf-8')
    const lines = content.split('\n')

    let workflowName = ''
    let description = ''
    let port: number | undefined
    let agentName = ''
    const endpoints: ServiceMetadata['endpoints'] = []
    const capabilities: string[] = []

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

      // Track current node
      if (trimmed.startsWith('[node:')) {
        currentNode = trimmed
        currentRouteInfo = {}
      }

      // Parse ACI node properties
      if (currentNode.includes('[node:') && trimmed.includes('type = aci')) {
        // This is an ACI node - add capability only once
        if (!capabilities.includes('api-endpoint')) {
          capabilities.push('api-endpoint')
        }
      }

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
          // Parse methods array like ["GET", "POST"]
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
      name: workflowName,
      description,
      endpoints,
      capabilities,
      connection: port ? {
        host: 'localhost',
        port,
        string: `http://localhost:${port}`
      } : undefined
    }
  } catch (error) {
    console.error(`Failed to parse flow file ${flowPath}:`, error)
    return {}
  }
}

// Get all flow services
async function getFlowServices(): Promise<ServiceMetadata[]> {
  try {
    const files = await fs.readdir(FLOWS_DIR)
    const flowFiles = files.filter(f => f.endsWith('.flow'))

    const flows: ServiceMetadata[] = []

    for (const file of flowFiles) {
      const flowPath = path.join(FLOWS_DIR, file)
      const flowId = path.basename(file, '.flow')
      const flowMetadata = await parseFlowFile(flowPath)

      // Check if flow container is running
      const containerName = `act-${flowId}`
      let status: 'running' | 'stopped' | 'available' = 'available'

      try {
        const { stdout } = await execAsync(`docker inspect --format='{{.State.Status}}' ${containerName}`)
        status = stdout.trim() === 'running' ? 'running' : 'stopped'
      } catch {
        // Container doesn't exist
        status = 'available'
      }

      flows.push({
        id: flowId,
        name: flowMetadata.name || flowId,
        type: 'flow',
        category: 'flow',
        description: flowMetadata.description || 'ACT Flow',
        status,
        containerName,
        source: 'flow-file',
        ...flowMetadata
      })
    }

    return flows
  } catch (error) {
    console.error('Failed to get flow services:', error)
    return []
  }
}

// GET /api/catalog - Unified service catalog
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const status = searchParams.get('status') // running | stopped | available | all

    // Only return flow services (infrastructure services use /api/services)
    let flowServices: ServiceMetadata[] = []

    try {
      flowServices = await getFlowServices()
    } catch (error) {
      console.error('Failed to get flow services:', error)
    }

    // Apply status filter
    if (status && status !== 'all') {
      flowServices = flowServices.filter(s => s.status === status)
    }

    // Format for Flow Architect agent compatibility
    const catalogFormat = {
      version: '2.0.0',
      last_updated: new Date().toISOString(),
      services: flowServices.map(service => ({
        id: service.id,
        name: service.name,
        type: 'flow',
        subtype: service.category,
        status: service.status,
        connection: service.connection ? {
          string: service.connection.string,
          host: service.connection.host,
          port: service.connection.port,
          username: service.connection.username,
          password: service.connection.password
        } : undefined,
        capabilities: service.capabilities || [],
        endpoints: service.endpoints || [],
        docker: {
          image: service.dockerImage,
          container: service.containerName,
          ports: service.ports,
          volumes: service.volumes
        },
        resources: service.resources,
        source: service.source
      })),
      stats: {
        total: flowServices.length,
        flows: flowServices.length,
        running: flowServices.filter(s => s.status === 'running').length,
        stopped: flowServices.filter(s => s.status === 'stopped').length,
        available: flowServices.filter(s => s.status === 'available').length
      }
    }

    return NextResponse.json(catalogFormat)

  } catch (error: any) {
    console.error('Error fetching unified catalog:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to fetch catalog' },
      { status: 500 }
    )
  }
}

// POST /api/catalog/refresh - Refresh flow services
export async function POST(request: NextRequest) {
  try {
    // Just refresh flow services by returning success
    // The GET endpoint will fetch latest flow services on next request
    return NextResponse.json({
      success: true,
      message: 'Catalog refreshed'
    })

  } catch (error: any) {
    console.error('Error refreshing catalog:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to refresh catalog' },
      { status: 500 }
    )
  }
}