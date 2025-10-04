import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import { MCP_SERVERS } from '@/data/mcp-servers'
import { getToken, getAllTokens, hasValidToken } from '@/lib/mcp/token-store'

const execAsync = promisify(exec)

// Container name prefix for MCP servers
const CONTAINER_PREFIX = 'mcp-'

// Check if Docker is available
async function checkDocker(): Promise<boolean> {
  try {
    await execAsync('docker --version')
    return true
  } catch {
    return false
  }
}

// Get list of running MCP containers
async function getRunningContainers() {
  try {
    const { stdout } = await execAsync(`docker ps --filter "name=${CONTAINER_PREFIX}" --format "{{.Names}}"`)
    const containerNames = stdout.trim().split('\n').filter(Boolean)
    return containerNames.map(name => name.replace(CONTAINER_PREFIX, ''))
  } catch {
    return []
  }
}

// Check if container is running
async function isContainerRunning(serverId: string): Promise<boolean> {
  try {
    const { stdout } = await execAsync(`docker ps -q --filter "name=${CONTAINER_PREFIX}${serverId}"`)
    return stdout.trim().length > 0
  } catch {
    return false
  }
}

// GET - List all MCP servers with status and OAuth info
export async function GET(request: NextRequest) {
  try {
    const dockerInstalled = await checkDocker()

    if (!dockerInstalled) {
      return NextResponse.json({
        error: 'Docker is not installed. Please install Docker on your VPS.',
        dockerInstalled: false
      }, { status: 400 })
    }

    const runningContainers = await getRunningContainers()
    const allTokens = await getAllTokens()

    const serversWithStatus = await Promise.all(
      MCP_SERVERS.map(async (server) => {
        const isRunning = runningContainers.includes(server.id)

        // Check if OAuth token exists for this server
        let hasToken = false
        if (server.requiresOAuth && server.oauthProvider) {
          hasToken = await hasValidToken(server.oauthProvider, server.id)
        }

        return {
          ...server,
          enabled: isRunning,
          status: isRunning ? 'running' : 'stopped',
          containerName: `${CONTAINER_PREFIX}${server.id}`,
          hasOAuthToken: hasToken,
          oauthConnected: hasToken
        }
      })
    )

    return NextResponse.json({
      dockerInstalled: true,
      servers: serversWithStatus,
      tokens: allTokens.map(t => ({
        provider: t.provider,
        serverId: t.serverId,
        createdAt: t.createdAt,
        expiresAt: t.expiresAt
      })),
      stats: {
        total: MCP_SERVERS.length,
        running: serversWithStatus.filter(s => s.enabled).length,
        stopped: serversWithStatus.filter(s => !s.enabled).length,
        oauthConnected: serversWithStatus.filter(s => s.hasOAuthToken).length
      }
    })
  } catch (error: any) {
    console.error('Error listing MCP servers:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to list MCP servers' },
      { status: 500 }
    )
  }
}

// POST - Start, stop, manage MCP containers
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, serverId, config } = body

    const server = MCP_SERVERS.find(s => s.id === serverId)

    if ((action === 'start' || action === 'stop' || action === 'remove' || action === 'restart') && !server) {
      return NextResponse.json({ error: 'Server not found' }, { status: 404 })
    }

    const containerName = `${CONTAINER_PREFIX}${serverId}`

    // START - Run MCP container
    if (action === 'start') {
      try {
        // Check if already running
        const running = await isContainerRunning(serverId!)
        if (running) {
          return NextResponse.json({
            success: true,
            message: `${server!.name} is already running`,
            alreadyRunning: true
          })
        }

        // Build docker run command
        let dockerCmd = `docker run -d --name ${containerName} --restart unless-stopped`

        // Add OAuth token if server requires it
        if (server!.requiresOAuth && server!.oauthProvider) {
          const token = await getToken(server!.oauthProvider, server!.id)

          if (!token) {
            return NextResponse.json({
              error: `OAuth authorization required. Please connect your ${server!.oauthProvider} account first.`,
              requiresOAuth: true,
              provider: server!.oauthProvider
            }, { status: 400 })
          }

          // Add token as environment variable
          const tokenEnvVar = `${server!.oauthProvider.toUpperCase()}_TOKEN`
          dockerCmd += ` -e ${tokenEnvVar}="${token.accessToken}"`

          // Also add as ACCESS_TOKEN (common convention)
          dockerCmd += ` -e ACCESS_TOKEN="${token.accessToken}"`
        }

        // Add secrets from config
        if (config?.secrets) {
          for (const [key, value] of Object.entries(config.secrets)) {
            if (value) {
              // Convert secret key to env var (e.g., "grafana.url" -> "GRAFANA_URL")
              const envKey = key.replace(/\./g, '_').toUpperCase()
              dockerCmd += ` -e ${envKey}="${value}"`
            }
          }
        }

        // Add environment variables from config
        if (config?.environment) {
          for (const [key, value] of Object.entries(config.environment)) {
            dockerCmd += ` -e ${key}="${value}"`
          }
        }

        // Add label
        dockerCmd += ` --label mcp-server=${serverId}`

        // Add the Docker image
        dockerCmd += ` ${server!.dockerImage}`

        console.log('[MCP] Starting container:', containerName)

        const { stdout, stderr } = await execAsync(dockerCmd)

        return NextResponse.json({
          success: true,
          message: `${server!.name} started successfully`,
          output: stdout || stderr,
          containerName
        })
      } catch (error: any) {
        // If container exists but stopped, start it
        if (error.message.includes('is already in use') || error.message.includes('already exists')) {
          try {
            await execAsync(`docker start ${containerName}`)
            return NextResponse.json({
              success: true,
              message: `${server!.name} restarted successfully`
            })
          } catch {
            throw error
          }
        }
        throw new Error(`Failed to start ${serverId}: ${error.message}`)
      }
    }

    // STOP - Stop MCP container
    if (action === 'stop') {
      try {
        await execAsync(`docker stop ${containerName}`)

        return NextResponse.json({
          success: true,
          message: `${server!.name} stopped`
        })
      } catch (error: any) {
        throw new Error(`Failed to stop ${serverId}: ${error.message}`)
      }
    }

    // REMOVE - Remove MCP container
    if (action === 'remove') {
      try {
        // Stop first
        try {
          await execAsync(`docker stop ${containerName}`)
        } catch {
          // Already stopped
        }

        // Remove container
        await execAsync(`docker rm ${containerName}`)

        return NextResponse.json({
          success: true,
          message: `${server!.name} removed`
        })
      } catch (error: any) {
        throw new Error(`Failed to remove ${serverId}: ${error.message}`)
      }
    }

    // RESTART - Restart container
    if (action === 'restart') {
      try {
        await execAsync(`docker restart ${containerName}`)

        return NextResponse.json({
          success: true,
          message: `${server!.name} restarted`
        })
      } catch (error: any) {
        throw new Error(`Failed to restart ${serverId}: ${error.message}`)
      }
    }

    // LOGS - Get container logs
    if (action === 'logs') {
      try {
        const lines = config?.lines || 100
        const { stdout } = await execAsync(`docker logs --tail ${lines} ${containerName}`)

        return NextResponse.json({
          success: true,
          logs: stdout
        })
      } catch (error: any) {
        throw new Error(`Failed to get logs: ${error.message}`)
      }
    }

    // INSPECT - Get container details
    if (action === 'inspect') {
      try {
        const { stdout } = await execAsync(`docker inspect ${containerName}`)
        const details = JSON.parse(stdout)

        return NextResponse.json({
          success: true,
          details: details[0]
        })
      } catch (error: any) {
        throw new Error(`Failed to inspect container: ${error.message}`)
      }
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
  } catch (error: any) {
    console.error('[MCP] Error:', error)
    return NextResponse.json(
      { error: error.message || 'MCP operation failed' },
      { status: 500 }
    )
  }
}
