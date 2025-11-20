/**
 * WebSocket Client Library
 * Connects frontend to standalone WebSocket server (port 3007)
 */

import { io, Socket } from 'socket.io-client'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:3007'

/**
 * Create connection to a specific namespace
 */
export function createWSConnection(namespace: string): Socket {
  const socket = io(`${WS_URL}/${namespace}`, {
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: 5,
  })

  socket.on('connect', () => {
    console.log(`[WS Client] Connected to /${namespace}`)
  })

  socket.on('disconnect', (reason) => {
    console.log(`[WS Client] Disconnected from /${namespace}:`, reason)
  })

  socket.on('error', (error) => {
    console.error(`[WS Client] Error on /${namespace}:`, error)
  })

  return socket
}

/**
 * Services namespace client
 */
export class ServicesWSClient {
  private socket: Socket | null = null

  connect() {
    if (!this.socket) {
      this.socket = createWSConnection('services')
    }
    return this.socket
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  subscribeLogs(serviceId: string, containerName: string, onLogs: (data: any) => void) {
    const socket = this.connect()

    socket.emit('subscribe:logs', { serviceId, containerName })

    socket.on('logs', onLogs)
    socket.on('connected', (data: any) => {
      console.log('[Services WS] Subscribed to logs:', data)
    })
    socket.on('error', (error: any) => {
      console.error('[Services WS] Error:', error)
    })

    return () => {
      socket.emit('unsubscribe:logs', { containerName })
      socket.off('logs', onLogs)
    }
  }
}

/**
 * Deployments namespace client
 */
export class DeploymentsWSClient {
  private socket: Socket | null = null

  connect() {
    if (!this.socket) {
      this.socket = createWSConnection('deployments')
    }
    return this.socket
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  subscribeLogs(deploymentId: string, pm2Name: string, onLogs: (data: any) => void) {
    const socket = this.connect()

    socket.emit('subscribe:logs', { deploymentId, pm2Name })

    socket.on('logs', onLogs)
    socket.on('connected', (data: any) => {
      console.log('[Deployments WS] Subscribed to logs:', data)
    })
    socket.on('error', (error: any) => {
      console.error('[Deployments WS] Error:', error)
    })

    return () => {
      socket.emit('unsubscribe:logs', { pm2Name })
      socket.off('logs', onLogs)
    }
  }
}

/**
 * System namespace client
 */
export class SystemWSClient {
  private socket: Socket | null = null

  connect() {
    if (!this.socket) {
      this.socket = createWSConnection('system')
    }
    return this.socket
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  subscribeStats(interval: number = 3000, onStats: (data: any) => void) {
    const socket = this.connect()

    socket.emit('subscribe:stats', { interval })

    socket.on('stats', onStats)
    socket.on('connected', () => {
      console.log('[System WS] Subscribed to stats')
    })
    socket.on('error', (error: any) => {
      console.error('[System WS] Error:', error)
    })

    return () => {
      socket.emit('unsubscribe:stats')
      socket.off('stats', onStats)
    }
  }
}

/**
 * MCP namespace client
 */
export class MCPWSClient {
  private socket: Socket | null = null

  connect() {
    if (!this.socket) {
      this.socket = createWSConnection('mcp')
    }
    return this.socket
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  join(serverId: string) {
    const socket = this.connect()
    socket.emit('join', { serverId })
  }

  leave(serverId: string) {
    if (this.socket) {
      this.socket.emit('leave', { serverId })
    }
  }

  on(event: string, handler: (data: any) => void) {
    const socket = this.connect()
    socket.on(event, handler)
    return () => socket.off(event, handler)
  }
}

/**
 * Files namespace client
 */
export class FilesWSClient {
  private socket: Socket | null = null

  connect() {
    if (!this.socket) {
      this.socket = createWSConnection('files')
    }
    return this.socket
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  watch(path: string, onChange: (data: any) => void) {
    const socket = this.connect()

    socket.emit('watch', { path })
    socket.on('change', onChange)
    socket.on('connected', (data: any) => {
      console.log('[Files WS] Watching:', data)
    })

    return () => {
      socket.off('change', onChange)
    }
  }
}

// Singleton instances
export const servicesWS = new ServicesWSClient()
export const deploymentsWS = new DeploymentsWSClient()
export const systemWS = new SystemWSClient()
export const mcpWS = new MCPWSClient()
export const filesWS = new FilesWSClient()
