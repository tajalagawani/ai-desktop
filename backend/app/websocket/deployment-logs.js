/**
 * WebSocket handler for deployment logs streaming
 * Provides real-time log streaming during build and runtime
 */

const { Tail } = require('tail')
const fs = require('fs')
const path = require('path')
const { URL } = require('url')

const LOGS_DIR = path.join(__dirname, '../../../logs')

/**
 * Handle deployment logs WebSocket connections
 * Routes: /api/deployments/logs/ws?deploymentId=xxx&type=build|runtime
 */
function handleDeploymentLogsConnection(ws, request) {
  console.log('[Deployment Logs] New WebSocket connection')

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
      logFile = path.join(LOGS_DIR, `${deploymentId}.log`)
    } else {
      // Runtime logs from PM2
      logFile = path.join(LOGS_DIR, `${deploymentId}-out.log`)
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
        if (ws.readyState === 1) { // OPEN
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

module.exports = { handleDeploymentLogsConnection }
