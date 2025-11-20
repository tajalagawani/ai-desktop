/**
 * WebSocket Client - Backend → WebSocket Server Communication
 * Allows the Express backend to emit events to Socket.IO namespaces
 */

const WS_SERVER_URL = process.env.WS_SERVER_URL || 'http://localhost:3007'

/**
 * Emit event to WebSocket server namespace
 * @param {string} namespace - The namespace (services, deployments, system, mcp, files)
 * @param {string} event - The event name
 * @param {object} data - The data to emit
 * @param {string} room - Optional room to emit to
 */
async function emitToWS(namespace, event, data, room = null) {
  try {
    const response = await fetch(`${WS_SERVER_URL}/emit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        namespace,
        event,
        data,
        room,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to emit to WebSocket server')
    }

    return await response.json()
  } catch (error) {
    console.error(`[WS Client] Failed to emit to ${namespace}:`, error.message)
    throw error
  }
}

/**
 * Helper functions for specific namespaces
 */

// Services namespace
async function emitToService(serviceId, event, data) {
  return emitToWS('services', event, data, `service:${serviceId}`)
}

// Deployments namespace
async function emitToDeployment(deploymentId, event, data) {
  return emitToWS('deployments', event, data, `deployment:${deploymentId}`)
}

// System namespace
async function emitToSystem(event, data) {
  return emitToWS('system', event, data)
}

// MCP namespace
async function emitToMCP(serverId, event, data) {
  return emitToWS('mcp', event, data, `mcp:${serverId}`)
}

// Files namespace
async function emitToFiles(path, event, data) {
  return emitToWS('files', event, data, `files:${path}`)
}

/**
 * Health check for WebSocket server
 */
async function checkWSHealth() {
  try {
    const response = await fetch(`${WS_SERVER_URL}/health`)
    return await response.json()
  } catch (error) {
    console.error('[WS Client] Health check failed:', error.message)
    return { success: false, error: error.message }
  }
}

module.exports = {
  emitToWS,
  emitToService,
  emitToDeployment,
  emitToSystem,
  emitToMCP,
  emitToFiles,
  checkWSHealth,
}
