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

    if (pathname === '/api/terminal/ws') {
      wss.handleUpgrade(request, socket, head, (ws) => {
        wss.emit('connection', ws, request)
      })
    } else {
      socket.destroy()
    }
  })

  // Handle WebSocket connections
  wss.on('connection', (ws) => {
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
  })

  server.listen(port, (err) => {
    if (err) throw err
    console.log(`> Ready on http://${hostname}:${port}`)
    console.log(`> WebSocket terminal available on ws://${hostname}:${port}/api/terminal/ws`)
  })
})
