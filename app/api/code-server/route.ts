import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

// Store running code-server processes (port -> folder mapping)
const runningServers = new Map<number, string>()

export async function POST(request: NextRequest) {
  try {
    const { action, folder, port } = await request.json()

    if (action === 'start') {
      const serverPort = port || 8080
      const targetFolder = folder || '/var/www'

      // Check if code-server is installed
      try {
        await execAsync('which code-server')
      } catch (error) {
        return NextResponse.json({
          success: false,
          error: 'code-server not installed. Install with: curl -fsSL https://code-server.dev/install.sh | sh',
          installInstructions: {
            script: 'curl -fsSL https://code-server.dev/install.sh | sh',
            homebrew: 'brew install code-server',
            npm: 'npm install -g code-server'
          }
        }, { status: 400 })
      }

      // Check if port is already in use
      try {
        const { stdout } = await execAsync(`lsof -ti:${serverPort} || echo ""`)
        if (stdout.trim()) {
          return NextResponse.json({
            success: true,
            port: serverPort,
            folder: runningServers.get(serverPort) || targetFolder,
            message: 'code-server already running on this port'
          })
        }
      } catch (error) {
        // Port is free, continue
      }

      // Start code-server in background with proper headers for iframe embedding
      // Create config file to allow iframe embedding
      const configDir = `/tmp/code-server-config-${serverPort}`
      await execAsync(`mkdir -p ${configDir}`)

      // Create config.yaml to disable X-Frame-Options
      const configContent = `bind-addr: 0.0.0.0:${serverPort}
auth: none
disable-telemetry: true
disable-update-check: true`

      await execAsync(`echo '${configContent}' > ${configDir}/config.yaml`)

      // Start code-server with config
      const startCommand = `nohup code-server "${targetFolder}" \
        --config ${configDir}/config.yaml \
        > /tmp/code-server-${serverPort}.log 2>&1 &`

      try {
        await execAsync(startCommand)

        // Wait for server to start
        await new Promise(resolve => setTimeout(resolve, 3000))

        // Verify it started
        const { stdout } = await execAsync(`lsof -ti:${serverPort} || echo ""`)
        if (!stdout.trim()) {
          // Check logs for error
          const { stdout: logs } = await execAsync(`tail -20 /tmp/code-server-${serverPort}.log`)
          throw new Error(`Failed to start code-server. Logs: ${logs}`)
        }

        runningServers.set(serverPort, targetFolder)

        return NextResponse.json({
          success: true,
          port: serverPort,
          folder: targetFolder,
          message: 'code-server started successfully'
        })
      } catch (error: any) {
        return NextResponse.json({
          success: false,
          error: `Failed to start code-server: ${error.message}`
        }, { status: 500 })
      }
    }

    if (action === 'stop') {
      const serverPort = port || 8080

      try {
        // Find process on port and kill it
        const { stdout } = await execAsync(`lsof -ti:${serverPort} || echo ""`)
        const pid = stdout.trim()

        if (pid) {
          await execAsync(`kill ${pid}`)
          runningServers.delete(serverPort)

          return NextResponse.json({
            success: true,
            message: 'code-server stopped'
          })
        } else {
          return NextResponse.json({
            success: false,
            error: 'No server running on this port'
          }, { status: 404 })
        }
      } catch (error: any) {
        return NextResponse.json({
          success: false,
          error: `Failed to stop code-server: ${error.message}`
        }, { status: 500 })
      }
    }

    if (action === 'status') {
      const serverPort = port || 8080

      try {
        const { stdout } = await execAsync(`lsof -ti:${serverPort} || echo ""`)
        const isRunning = !!stdout.trim()

        return NextResponse.json({
          success: true,
          running: isRunning,
          port: serverPort,
          folder: runningServers.get(serverPort)
        })
      } catch (error: any) {
        return NextResponse.json({
          success: true,
          running: false,
          port: serverPort
        })
      }
    }

    return NextResponse.json({
      success: false,
      error: 'Invalid action. Use: start, stop, or status'
    }, { status: 400 })

  } catch (error: any) {
    console.error('Error managing code-server:', error)
    return NextResponse.json({
      success: false,
      error: error.message || 'Failed to manage code-server'
    }, { status: 500 })
  }
}

export async function GET() {
  try {
    // Get all running code-server instances
    const servers = []

    for (const [port, folder] of runningServers.entries()) {
      try {
        const { stdout } = await execAsync(`lsof -ti:${port} || echo ""`)
        if (stdout.trim()) {
          servers.push({
            port,
            folder,
            pid: stdout.trim()
          })
        } else {
          // Clean up if process died
          runningServers.delete(port)
        }
      } catch (error) {
        runningServers.delete(port)
      }
    }

    return NextResponse.json({
      success: true,
      servers
    })
  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error.message
    }, { status: 500 })
  }
}
