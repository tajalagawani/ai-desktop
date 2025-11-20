/**
 * WebSocket handler for Docker service logs streaming
 * Provides real-time log streaming from Docker containers
 */

const { exec } = require('child_process')
const { URL } = require('url')

/**
 * Handle service logs WebSocket connections
 * Routes: /api/services/logs/ws?container=xxx
 */
function handleServiceLogsConnection(ws, request) {
  console.log('[Service Logs] New WebSocket connection')

  const url = new URL(request.url, `http://${request.headers.host}`)
  const containerName = url.searchParams.get('container')

  if (!containerName) {
    ws.send(JSON.stringify({ type: 'error', message: 'Container name required' }))
    ws.close()
    return
  }

  console.log(`[Service Logs] Streaming logs for container: ${containerName}`)

  let logsProcess = null

  try {
    // Docker logs command with follow
    const command = `docker logs -f --tail=100 ${containerName}`

    logsProcess = exec(command)

    // Send stdout
    logsProcess.stdout.on('data', (data) => {
      try {
        if (ws.readyState === 1) { // OPEN
          ws.send(JSON.stringify({ type: 'log', data: data.toString() }))
        }
      } catch (error) {
        console.error('[Service Logs] Error sending stdout:', error)
      }
    })

    // Send stderr
    logsProcess.stderr.on('data', (data) => {
      try {
        if (ws.readyState === 1) { // OPEN
          ws.send(JSON.stringify({ type: 'log', data: data.toString() }))
        }
      } catch (error) {
        console.error('[Service Logs] Error sending stderr:', error)
      }
    })

    // Handle process errors
    logsProcess.on('error', (error) => {
      console.error('[Service Logs] Process error:', error)
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'error', message: error.message }))
        }
      } catch {}
    })

    // Handle process exit
    logsProcess.on('exit', (code) => {
      console.log(`[Service Logs] Process exited with code ${code}`)
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({
            type: 'info',
            message: code === 0 ? 'Container stopped' : `Process exited with code ${code}`
          }))
        }
      } catch {}
    })

  } catch (error) {
    console.error('[Service Logs] Setup error:', error)
    try {
      if (ws.readyState === 1) {
        ws.send(JSON.stringify({ type: 'error', message: error.message }))
      }
    } catch {}
  }

  // Handle WebSocket close
  ws.on('close', () => {
    console.log('[Service Logs] WebSocket closed')
    if (logsProcess) {
      logsProcess.kill()
    }
  })

  // Handle WebSocket errors
  ws.on('error', (error) => {
    console.error('[Service Logs] WebSocket error:', error)
    if (logsProcess) {
      logsProcess.kill()
    }
  })

  // Send connection success
  ws.send(JSON.stringify({
    type: 'connected',
    message: `Streaming logs for ${containerName}`
  }))
}

module.exports = { handleServiceLogsConnection }
