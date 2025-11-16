import { NextRequest, NextResponse } from 'next/server'
import { spawn, exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

// Store running code-server processes
const runningServers = new Map<string, any>()

export async function POST(request: NextRequest) {
  try {
    const { action, folder, port } = await request.json()

    if (action === 'start') {
      // Check if code-server is installed
      try {
        await execAsync('which code-server')
      } catch (error) {
        return NextResponse.json({
          success: false,
          error: 'code-server not installed. Install with: curl -fsSL https://code-server.dev/install.sh | sh'
        }, { status: 400 })
      }

      const serverPort = port || 8080

      // Check if server already running for this folder
      if (runningServers.has(folder)) {
        return NextResponse.json({
          success: true,
          url: `http://localhost:${serverPort}`,
          message: 'Server already running'
        })
      }

      // Start code-server
      const server = spawn('code-server', [
        folder || process.cwd(),
        '--auth', 'none',
        '--port', serverPort.toString(),
        '--disable-telemetry',
        '--disable-update-check',
        '--bind-addr', `127.0.0.1:${serverPort}`
      ])

      runningServers.set(folder, { process: server, port: serverPort })

      server.stdout?.on('data', (data) => {
        console.log(`code-server: ${data}`)
      })

      server.stderr?.on('data', (data) => {
        console.error(`code-server error: ${data}`)
      })

      server.on('close', (code) => {
        console.log(`code-server exited with code ${code}`)
        runningServers.delete(folder)
      })

      // Wait a bit for server to start
      await new Promise(resolve => setTimeout(resolve, 2000))

      return NextResponse.json({
        success: true,
        url: `http://localhost:${serverPort}`,
        message: 'code-server started successfully'
      })
    }

    if (action === 'stop') {
      const serverInfo = runningServers.get(folder)
      if (serverInfo) {
        serverInfo.process.kill()
        runningServers.delete(folder)
        return NextResponse.json({
          success: true,
          message: 'Server stopped'
        })
      }
      return NextResponse.json({
        success: false,
        error: 'No server running for this folder'
      }, { status: 404 })
    }

    if (action === 'status') {
      return NextResponse.json({
        success: true,
        running: runningServers.has(folder),
        servers: Array.from(runningServers.keys())
      })
    }

    return NextResponse.json({
      success: false,
      error: 'Invalid action'
    }, { status: 400 })

  } catch (error: any) {
    console.error('Error managing code-server:', error)
    return NextResponse.json({
      success: false,
      error: error.message || 'Failed to manage code-server'
    }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  // Get list of running servers
  return NextResponse.json({
    success: true,
    servers: Array.from(runningServers.entries()).map(([folder, info]) => ({
      folder,
      port: info.port,
      url: `http://localhost:${info.port}`
    }))
  })
}
