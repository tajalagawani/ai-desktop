import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import { MCP_SERVERS } from '@/data/mcp-servers'

const execAsync = promisify(exec)

// Check if Docker MCP CLI is installed
async function checkDockerMCP(): Promise<boolean> {
  try {
    await execAsync('docker mcp --version')
    return true
  } catch {
    return false
  }
}

// Get list of enabled MCP servers
async function getEnabledServers() {
  try {
    const { stdout } = await execAsync('docker mcp server ls')
    // Parse the output - format is typically: NAME STATUS
    const lines = stdout.trim().split('\n').slice(1) // Skip header
    const servers = lines.map(line => {
      const parts = line.trim().split(/\s+/)
      return {
        name: parts[0],
        status: parts[1] || 'unknown'
      }
    })
    return servers
  } catch {
    return []
  }
}

// Get gateway status
async function getGatewayStatus() {
  try {
    // Check if gateway process is running
    await execAsync('pgrep -f "docker mcp gateway"')
    return 'running'
  } catch {
    return 'stopped'
  }
}

// Get MCP configuration
async function getMCPConfig() {
  try {
    const { stdout } = await execAsync('docker mcp config read')
    return stdout
  } catch {
    return null
  }
}

// GET - List all MCP servers and their status
export async function GET(request: NextRequest) {
  try {
    const mcpInstalled = await checkDockerMCP()

    if (!mcpInstalled) {
      return NextResponse.json({
        error: 'Docker MCP CLI is not installed. Please install Docker Desktop 4.42.0+ and enable MCP Toolkit in Settings → Beta features.',
        mcpInstalled: false
      }, { status: 400 })
    }

    const enabledServers = await getEnabledServers()
    const gatewayStatus = await getGatewayStatus()
    const config = await getMCPConfig()

    const serversWithStatus = MCP_SERVERS.map((server) => {
      const enabledServer = enabledServers.find((s: any) => s.name === server.id)
      const isEnabled = !!enabledServer

      return {
        ...server,
        enabled: isEnabled,
        status: isEnabled ? 'enabled' : 'disabled'
      }
    })

    return NextResponse.json({
      mcpInstalled: true,
      gatewayStatus,
      config,
      servers: serversWithStatus,
      stats: {
        total: MCP_SERVERS.length,
        enabled: serversWithStatus.filter(s => s.enabled).length,
        available: serversWithStatus.filter(s => !s.enabled).length
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

// POST - Enable, disable, configure MCP servers
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, serverId, secrets, port } = body

    const server = MCP_SERVERS.find(s => s.id === serverId)

    if (action === 'enable' && !server) {
      return NextResponse.json({ error: 'Server not found' }, { status: 404 })
    }

    if (action === 'enable') {
      try {
        const { stdout, stderr } = await execAsync(`docker mcp server enable ${serverId}`)

        return NextResponse.json({
          success: true,
          message: `${server!.name} enabled successfully`,
          output: stdout || stderr
        })
      } catch (error: any) {
        throw new Error(`Failed to enable ${serverId}: ${error.message}`)
      }
    }

    if (action === 'disable') {
      try {
        const { stdout } = await execAsync(`docker mcp server disable ${serverId}`)

        return NextResponse.json({
          success: true,
          message: `${server!.name} disabled`,
          output: stdout
        })
      } catch (error: any) {
        throw new Error(`Failed to disable ${serverId}: ${error.message}`)
      }
    }

    if (action === 'authorize-oauth') {
      if (!server || !server.requiresOAuth || !server.oauthProvider) {
        return NextResponse.json({ error: 'This server does not require OAuth' }, { status: 400 })
      }

      try {
        const { stdout } = await execAsync(`docker mcp oauth authorize ${server.oauthProvider}`)

        return NextResponse.json({
          success: true,
          message: `OAuth authorization initiated for ${server.oauthProvider}. Please complete the authorization in your browser.`,
          output: stdout
        })
      } catch (error: any) {
        throw new Error(`OAuth authorization failed: ${error.message}`)
      }
    }

    if (action === 'set-secrets') {
      if (!secrets || !Array.isArray(secrets)) {
        return NextResponse.json({ error: 'Invalid secrets format' }, { status: 400 })
      }

      try {
        for (const { key, value } of secrets) {
          await execAsync(`docker mcp secret set "${key}=${value}"`)
        }

        return NextResponse.json({
          success: true,
          message: `Configured ${secrets.length} secret(s) successfully`
        })
      } catch (error: any) {
        throw new Error(`Failed to set secrets: ${error.message}`)
      }
    }

    if (action === 'delete-secret') {
      const { key } = body
      if (!key) {
        return NextResponse.json({ error: 'Secret key required' }, { status: 400 })
      }

      try {
        await execAsync(`docker mcp secret delete ${key}`)

        return NextResponse.json({
          success: true,
          message: `Secret ${key} deleted successfully`
        })
      } catch (error: any) {
        throw new Error(`Failed to delete secret: ${error.message}`)
      }
    }

    if (action === 'start-gateway') {
      const gatewayPort = port || 8080

      try {
        // Start gateway in background with nohup
        exec(`nohup docker mcp gateway run --port ${gatewayPort} --verbose > /tmp/mcp-gateway.log 2>&1 &`)

        // Give it a moment to start
        await new Promise(resolve => setTimeout(resolve, 2000))

        return NextResponse.json({
          success: true,
          message: `MCP Gateway started on port ${gatewayPort}`,
          port: gatewayPort
        })
      } catch (error: any) {
        throw new Error(`Failed to start gateway: ${error.message}`)
      }
    }

    if (action === 'stop-gateway') {
      try {
        await execAsync('pkill -f "docker mcp gateway"')

        return NextResponse.json({
          success: true,
          message: 'MCP Gateway stopped'
        })
      } catch (error: any) {
        // If no process found, consider it success
        return NextResponse.json({
          success: true,
          message: 'MCP Gateway was not running'
        })
      }
    }

    if (action === 'get-config') {
      try {
        const { stdout } = await execAsync('docker mcp config read')

        return NextResponse.json({
          success: true,
          config: stdout
        })
      } catch (error: any) {
        throw new Error(`Failed to read config: ${error.message}`)
      }
    }

    if (action === 'reset-config') {
      try {
        const { stdout } = await execAsync('docker mcp config reset')

        return NextResponse.json({
          success: true,
          message: 'Configuration reset to defaults',
          output: stdout
        })
      } catch (error: any) {
        throw new Error(`Failed to reset config: ${error.message}`)
      }
    }

    if (action === 'list-secrets') {
      try {
        const { stdout } = await execAsync('docker mcp secret list')

        return NextResponse.json({
          success: true,
          secrets: stdout
        })
      } catch (error: any) {
        throw new Error(`Failed to list secrets: ${error.message}`)
      }
    }

    if (action === 'inspect-server') {
      try {
        const { stdout } = await execAsync(`docker mcp server inspect ${serverId}`)

        return NextResponse.json({
          success: true,
          details: stdout
        })
      } catch (error: any) {
        throw new Error(`Failed to inspect server: ${error.message}`)
      }
    }

    if (action === 'init-catalog') {
      try {
        const { stdout } = await execAsync('docker mcp catalog init')

        return NextResponse.json({
          success: true,
          message: 'Docker MCP Catalog initialized',
          output: stdout
        })
      } catch (error: any) {
        throw new Error(`Failed to initialize catalog: ${error.message}`)
      }
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
  } catch (error: any) {
    console.error('Error managing MCP server:', error)
    return NextResponse.json(
      { error: error.message || 'MCP operation failed' },
      { status: 500 }
    )
  }
}
