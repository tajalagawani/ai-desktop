const { createServer } = require('http')
const { parse } = require('url')
const next = require('next')
const { WebSocketServer } = require('ws')
const { Server } = require('socket.io')
const { spawn } = require('node-pty')

const dev = process.env.NODE_ENV !== 'production'
const hostname = 'localhost'
const port = parseInt(process.env.PORT || '3005', 10)

const app = next({ dev, hostname, port })
const handle = app.getRequestHandler()

// Store active terminal sessions
const terminals = new Map()

app.prepare().then(() => {
  const server = createServer(async (req, res) => {
    try {
      const parsedUrl = parse(req.url, true)
      await handle(req, res, parsedUrl)
    } catch (err) {
      console.error('Error occurred handling', req.url, err)
      res.statusCode = 500
      res.end('internal server error')
    }
  })

  // Create WebSocket server for terminals
  const wss = new WebSocketServer({ noServer: true })

  // Create Socket.IO server for Flow Builder
  const io = new Server(server, {
    cors: {
      origin: process.env.NEXT_PUBLIC_APP_URL || `http://localhost:3005`,
      methods: ['GET', 'POST'],
    },
    path: '/socket.io/'
  })

  // Initialize Flow Builder agent manager (will be created)
  let flowAgentManager = null
  try {
    const { getFlowAgentManager } = require('./lib/flow-builder/agent-manager')
    flowAgentManager = getFlowAgentManager()
    console.log('[Flow Builder] Agent manager initialized')
  } catch (error) {
    console.log('[Flow Builder] Agent manager not yet available:', error.message)
  }

  // Handle Socket.IO connections for Flow Builder
  io.on('connection', (socket) => {
    console.log(`[Socket.IO] Flow Builder client connected: ${socket.id}`)

    if (!flowAgentManager) {
      socket.emit('error', {
        message: 'Flow Builder agent manager not initialized',
        code: 'INIT_ERROR',
      })
      return
    }

    // Handle agent start request
    socket.on('agent:start', async ({ sessionId, request, conversationHistory, apiKey }) => {
      console.log(`[Socket.IO] Starting agent for session ${sessionId}`)
      console.log(`[Socket.IO] API key from client:`, apiKey ? apiKey.substring(0, 20) + '...' : 'NOT PROVIDED')
      try {
        await flowAgentManager.startAgent(sessionId, request, socket, conversationHistory, apiKey)
      } catch (error) {
        console.error('[Socket.IO] Error starting agent:', error)
        socket.emit('error', {
          message: error instanceof Error ? error.message : 'Failed to start agent',
          code: 'START_ERROR',
        })
      }
    })

    // Handle agent stop request
    socket.on('agent:stop', ({ sessionId }) => {
      console.log(`[Socket.IO] Stopping agent for session ${sessionId}`)
      flowAgentManager.stopAgent(sessionId)
    })

    socket.on('disconnect', () => {
      console.log(`[Socket.IO] Flow Builder client disconnected: ${socket.id}`)
    })
  })

  // CRITICAL: Override the upgrade event handler COMPLETELY
  // We need to handle it before Next.js's internal router sees it
  const originalEmit = server.emit.bind(server)
  server.emit = function(event, ...args) {
    if (event === 'upgrade') {
      const [request, socket, head] = args
      const { pathname } = parse(request.url, true)

      if (pathname === '/api/terminal/ws' || pathname === '/api/services/logs/ws' || pathname === '/api/deployments/logs/ws') {
        console.log('[WebSocket] Intercepted upgrade for:', pathname)

        wss.handleUpgrade(request, socket, head, (ws) => {
          wss.emit('connection', ws, request, pathname)
        })

        // Don't call Next.js's upgrade handler
        return true
      }
    }

    // For all other events, call original emit
    return originalEmit(event, ...args)
  }

  // Handle WebSocket connections
  wss.on('connection', (ws, request, pathname) => {
    if (pathname === '/api/services/logs/ws') {
      console.log('[WebSocket] Routing to service logs handler')
      handleLogsConnection(ws, request)
    } else if (pathname === '/api/deployments/logs/ws') {
      console.log('[WebSocket] Routing to deployment logs handler')
      handleDeploymentLogsConnection(ws, request)
    } else {
      console.log('[WebSocket] Routing to terminal handler')
      handleTerminalConnection(ws)
    }
  })

  // Handle terminal WebSocket connections
  function handleTerminalConnection(ws) {
    console.log('[Terminal] New WebSocket connection')

    const sessionId = Date.now().toString()

    // Spawn a new terminal process
    const shell = process.env.SHELL || '/bin/bash'
    const ptyProcess = spawn(shell, [], {
      name: 'xterm-color',
      cols: 80,
      rows: 24,
      cwd: process.env.HOME || '/root',
      env: process.env
    })

    // Store the terminal session
    terminals.set(sessionId, ptyProcess)

    console.log(`[Terminal] Spawned shell: ${shell}`)

    // Forward terminal output to WebSocket
    ptyProcess.onData((data) => {
      try {
        if (ws.readyState === 1) { // OPEN
          ws.send(JSON.stringify({ type: 'output', data }))
        }
      } catch (error) {
        console.error('[Terminal] Error sending data:', error)
      }
    })

    // Handle terminal process exit
    ptyProcess.onExit(({ exitCode, signal }) => {
      console.log(`[Terminal] Process exited: ${exitCode}, signal: ${signal}`)
      terminals.delete(sessionId)
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'exit', exitCode }))
          ws.close()
        }
      } catch (error) {
        console.error('[Terminal] Error closing WebSocket:', error)
      }
    })

    // Handle messages from WebSocket
    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message.toString())

        if (data.type === 'input') {
          ptyProcess.write(data.data)
        } else if (data.type === 'resize') {
          ptyProcess.resize(data.cols || 80, data.rows || 24)
        }
      } catch (error) {
        console.error('[Terminal] Error handling message:', error)
      }
    })

    // Handle WebSocket close
    ws.on('close', () => {
      console.log(`[Terminal] WebSocket closed: ${sessionId}`)
      ptyProcess.kill()
      terminals.delete(sessionId)
    })

    // Handle WebSocket errors
    ws.on('error', (error) => {
      console.error('[Terminal] WebSocket error:', error)
      ptyProcess.kill()
      terminals.delete(sessionId)
    })

    // Send initial connection success
    ws.send(JSON.stringify({
      type: 'connected',
      sessionId,
      message: 'Terminal session established'
    }))
  }

  // Handle logs WebSocket connections
  function handleLogsConnection(ws, request) {
    console.log('[Logs] New WebSocket connection')

    const { exec } = require('child_process')
    const url = new URL(request.url, `http://${request.headers.host}`)
    const containerName = url.searchParams.get('container')

    if (!containerName) {
      ws.send(JSON.stringify({ type: 'error', message: 'Container name required' }))
      ws.close()
      return
    }

    console.log(`[Logs] Streaming logs for container: ${containerName}`)

    // Stream docker logs with follow flag
    const logsProcess = exec(`docker logs -f --tail 100 ${containerName}`)

    // Send stdout
    logsProcess.stdout.on('data', (data) => {
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'log', data: data.toString() }))
        }
      } catch (error) {
        console.error('[Logs] Error sending stdout:', error)
      }
    })

    // Send stderr
    logsProcess.stderr.on('data', (data) => {
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'log', data: data.toString() }))
        }
      } catch (error) {
        console.error('[Logs] Error sending stderr:', error)
      }
    })

    // Handle process errors
    logsProcess.on('error', (error) => {
      console.error('[Logs] Process error:', error)
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'error', message: error.message }))
        }
      } catch {}
    })

    // Handle process exit
    logsProcess.on('exit', (code) => {
      console.log(`[Logs] Process exited with code: ${code}`)
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'exit', code }))
        }
      } catch {}
    })

    // Handle WebSocket close
    ws.on('close', () => {
      console.log('[Logs] WebSocket closed, killing process')
      logsProcess.kill()
    })

    // Handle WebSocket errors
    ws.on('error', (error) => {
      console.error('[Logs] WebSocket error:', error)
      logsProcess.kill()
    })

    // Send connection success
    ws.send(JSON.stringify({
      type: 'connected',
      message: `Streaming logs for ${containerName}`
    }))
  }

  // Handle deployment logs WebSocket connections
  function handleDeploymentLogsConnection(ws, request) {
    console.log('[Deployment Logs] New WebSocket connection')

    const { Tail } = require('tail')
    const fs = require('fs')
    const url = new URL(request.url, `http://${request.headers.host}`)
    const deploymentId = url.searchParams.get('deploymentId')
    const logType = url.searchParams.get('type') || 'build' // 'build' or 'runtime'

    if (!deploymentId) {
      ws.send(JSON.stringify({ type: 'error', message: 'Deployment ID required' }))
      ws.close()
      return
    }

    console.log(`[Deployment Logs] Streaming ${logType} logs for deployment: ${deploymentId}`)

    let tail = null

    try {
      let logFile
      if (logType === 'build') {
        logFile = `/var/www/ai-desktop/logs/${deploymentId}.log`
      } else {
        // Runtime logs from PM2 - handle both fork mode (-out.log) and cluster mode (-out-N.log)
        const baseLogFile = `/var/www/ai-desktop/logs/${deploymentId}-out.log`
        if (fs.existsSync(baseLogFile)) {
          logFile = baseLogFile
        } else {
          // Check for cluster mode log files (-out-0.log, -out-1.log, etc.)
          const logDir = '/var/www/ai-desktop/logs'
          const files = fs.readdirSync(logDir)
          const clusterLogFile = files.find(f => f.startsWith(`${deploymentId}-out-`) && f.endsWith('.log'))
          if (clusterLogFile) {
            logFile = `${logDir}/${clusterLogFile}`
          } else {
            logFile = baseLogFile // fallback
          }
        }
      }

      // Check if file exists
      if (!fs.existsSync(logFile)) {
        ws.send(JSON.stringify({ type: 'info', message: `Waiting for logs...` }))
      }

      // Send existing content first
      if (fs.existsSync(logFile)) {
        const existingContent = fs.readFileSync(logFile, 'utf-8')
        if (existingContent) {
          ws.send(JSON.stringify({ type: 'log', data: existingContent }))
        }
      }

      // Start tailing the file
      tail = new Tail(logFile, {
        fromBeginning: false,
        follow: true,
        useWatchFile: true
      })

      tail.on('line', (data) => {
        try {
          if (ws.readyState === 1) {
            ws.send(JSON.stringify({ type: 'log', data: data + '\n' }))
          }
        } catch (error) {
          console.error('[Deployment Logs] Error sending data:', error)
        }
      })

      tail.on('error', (error) => {
        console.error('[Deployment Logs] Tail error:', error)
        try {
          if (ws.readyState === 1) {
            ws.send(JSON.stringify({ type: 'error', message: error.message }))
          }
        } catch {}
      })

    } catch (error) {
      console.error('[Deployment Logs] Setup error:', error)
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'error', message: error.message }))
        }
      } catch {}
    }

    // Handle WebSocket close
    ws.on('close', () => {
      console.log('[Deployment Logs] WebSocket closed')
      if (tail) {
        tail.unwatch()
      }
    })

    // Handle WebSocket errors
    ws.on('error', (error) => {
      console.error('[Deployment Logs] WebSocket error:', error)
      if (tail) {
        tail.unwatch()
      }
    })

    // Send connection success
    ws.send(JSON.stringify({
      type: 'connected',
      message: `Streaming ${logType} logs for ${deploymentId}`
    }))
  }

  // Cleanup on process exit
  process.on('SIGTERM', () => {
    console.log('[Server] SIGTERM received, cleaning up...')
    if (flowAgentManager) {
      flowAgentManager.stopAll()
    }
    server.close()
  })

  process.on('SIGINT', () => {
    console.log('[Server] SIGINT received, cleaning up...')
    if (flowAgentManager) {
      flowAgentManager.stopAll()
    }
    process.exit(0)
  })

  server.listen(port, async (err) => {
    if (err) throw err

    console.log(`> Ready on http://${hostname}:${port}`)
    console.log(`> WebSocket terminal available on ws://${hostname}:${port}/api/terminal/ws`)
    console.log(`> WebSocket logs available on ws://${hostname}:${port}/api/services/logs/ws`)
    console.log(`> WebSocket deployment logs available on ws://${hostname}:${port}/api/deployments/logs/ws`)
    console.log(`> Socket.IO Flow Builder available on http://${hostname}:${port}/socket.io/`)
  })
})
