const { createServer } = require('http')
const { parse } = require('url')
const next = require('next')
const { WebSocketServer } = require('ws')
const { spawn } = require('node-pty')

const dev = process.env.NODE_ENV !== 'production'
const hostname = 'localhost'
const port = parseInt(process.env.PORT || '3000', 10)

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

  // Create WebSocket server
  const wss = new WebSocketServer({ noServer: true })

  // Handle WebSocket upgrade
  server.on('upgrade', (request, socket, head) => {
    const { pathname } = parse(request.url, true)
    console.log('[WebSocket] Upgrade request received for:', pathname)

    if (pathname === '/api/terminal/ws' || pathname === '/api/services/logs/ws') {
      console.log('[WebSocket] ✅ Valid WebSocket path, handling upgrade...')
      wss.handleUpgrade(request, socket, head, (ws) => {
        console.log('[WebSocket] Connection established for:', pathname)
        wss.emit('connection', ws, request, pathname)
      })
    } else {
      // Let Next.js handle other WebSocket requests (like HMR in dev mode)
      console.log('[WebSocket] Passing to Next.js handler:', pathname)
    }
  })

  // Handle WebSocket connections
  wss.on('connection', (ws, request, pathname) => {
    if (pathname === '/api/services/logs/ws') {
      console.log('[WebSocket] Routing to logs handler')
      handleLogsConnection(ws, request)
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

  server.listen(port, async (err) => {
    if (err) throw err

    console.log(`> Ready on http://${hostname}:${port}`)
    console.log(`> WebSocket terminal available on ws://${hostname}:${port}/api/terminal/ws`)
    console.log(`> WebSocket logs available on ws://${hostname}:${port}/api/services/logs/ws`)
  })
})
