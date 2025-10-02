import { NextRequest } from 'next/server'
import { spawn } from 'node-pty'
import { WebSocketServer } from 'ws'

// Store active terminal sessions
const terminals = new Map<string, any>()

export async function GET(req: NextRequest) {
  // Check if this is a WebSocket upgrade request
  const upgradeHeader = req.headers.get('upgrade')

  if (upgradeHeader !== 'websocket') {
    return new Response('Expected WebSocket', { status: 426 })
  }

  // For Next.js, we need to return a Response
  // The actual WebSocket handling will be done in server.js
  return new Response('WebSocket endpoint - use custom server', {
    status: 200,
    headers: {
      'Content-Type': 'text/plain',
    }
  })
}

// Export function to handle WebSocket connections
export function handleTerminalWebSocket(ws: any, sessionId: string) {
  console.log(`[Terminal] New session: ${sessionId}`)

  // Spawn a new terminal process
  const shell = process.env.SHELL || '/bin/bash'
  const ptyProcess = spawn(shell, [], {
    name: 'xterm-color',
    cols: 80,
    rows: 24,
    cwd: process.env.HOME || '/tmp',
    env: process.env as { [key: string]: string }
  })

  // Store the terminal session
  terminals.set(sessionId, ptyProcess)

  // Forward terminal output to WebSocket
  ptyProcess.onData((data: string) => {
    try {
      ws.send(JSON.stringify({ type: 'output', data }))
    } catch (error) {
      console.error('[Terminal] Error sending data:', error)
    }
  })

  // Handle terminal process exit
  ptyProcess.onExit(({ exitCode, signal }: { exitCode: number; signal?: number }) => {
    console.log(`[Terminal] Process exited: ${exitCode}, signal: ${signal}`)
    terminals.delete(sessionId)
    try {
      ws.send(JSON.stringify({ type: 'exit', exitCode }))
      ws.close()
    } catch (error) {
      console.error('[Terminal] Error closing WebSocket:', error)
    }
  })

  // Handle messages from WebSocket
  ws.on('message', (message: Buffer) => {
    try {
      const data = JSON.parse(message.toString())

      if (data.type === 'input') {
        ptyProcess.write(data.data)
      } else if (data.type === 'resize') {
        ptyProcess.resize(data.cols, data.rows)
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
  ws.on('error', (error: Error) => {
    console.error('[Terminal] WebSocket error:', error)
    ptyProcess.kill()
    terminals.delete(sessionId)
  })

  // Send initial connection success
  ws.send(JSON.stringify({ type: 'connected', sessionId }))
}
