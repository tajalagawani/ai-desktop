/**
 * WebSocket Client - Real-time communication with VPS backend
 * Uses Socket.IO for reliable bidirectional streaming
 */

import { io, Socket } from 'socket.io-client'

export type MessageCallback = (data: any) => void
export type ErrorCallback = (error: Error) => void

export interface WSClientOptions {
  autoConnect?: boolean
  reconnection?: boolean
  reconnectionDelay?: number
  reconnectionAttempts?: number
}

class WSClient {
  private socket: Socket | null = null
  private baseURL: string
  private connected: boolean = false
  private listeners: Map<string, Set<MessageCallback>> = new Map()
  private connectionCallbacks: Set<() => void> = new Set()
  private disconnectionCallbacks: Set<() => void> = new Set()
  private errorCallbacks: Set<ErrorCallback> = new Set()

  constructor(options: WSClientOptions = {}) {
    // Determine WebSocket URL based on environment
    if (typeof window !== 'undefined') {
      this.baseURL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:3007'
    } else {
      this.baseURL = process.env.WS_SERVER_URL || 'http://localhost:3007'
    }

    // Initialize socket if autoConnect is true
    if (options.autoConnect !== false) {
      this.connect(options)
    }
  }

  /**
   * Connect to WebSocket server
   */
  connect(options: WSClientOptions = {}) {
    if (this.socket?.connected) {
      console.warn('WebSocket already connected')
      return
    }

    const {
      reconnection = true,
      reconnectionDelay = 1000,
      reconnectionAttempts = 10,
    } = options

    this.socket = io(this.baseURL, {
      reconnection,
      reconnectionDelay,
      reconnectionAttempts,
      transports: ['websocket', 'polling'],
      withCredentials: true,
    })

    // Connection event handlers
    this.socket.on('connect', () => {
      this.connected = true
      console.log('[WS] Connected to server')
      this.connectionCallbacks.forEach(cb => cb())
    })

    this.socket.on('disconnect', (reason) => {
      this.connected = false
      console.log('[WS] Disconnected from server:', reason)
      this.disconnectionCallbacks.forEach(cb => cb())
    })

    this.socket.on('connect_error', (error) => {
      console.error('[WS] Connection error:', error.message)
      this.errorCallbacks.forEach(cb => cb(error))
    })

    this.socket.on('error', (error) => {
      console.error('[WS] Socket error:', error)
      this.errorCallbacks.forEach(cb => cb(new Error(error)))
    })

    // Restore event listeners
    this.listeners.forEach((callbacks, event) => {
      callbacks.forEach(callback => {
        this.socket?.on(event, callback)
      })
    })
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.connected = false
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.connected
  }

  /**
   * Subscribe to an event
   */
  on(event: string, callback: MessageCallback): () => void {
    // Store callback
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)

    // Register with socket if connected
    if (this.socket) {
      this.socket.on(event, callback)
    }

    // Return unsubscribe function
    return () => this.off(event, callback)
  }

  /**
   * Unsubscribe from an event
   */
  off(event: string, callback: MessageCallback) {
    // Remove from local storage
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.delete(callback)
      if (callbacks.size === 0) {
        this.listeners.delete(event)
      }
    }

    // Remove from socket
    if (this.socket) {
      this.socket.off(event, callback)
    }
  }

  /**
   * Subscribe to connection events
   */
  onConnect(callback: () => void): () => void {
    this.connectionCallbacks.add(callback)
    return () => this.connectionCallbacks.delete(callback)
  }

  /**
   * Subscribe to disconnection events
   */
  onDisconnect(callback: () => void): () => void {
    this.disconnectionCallbacks.add(callback)
    return () => this.disconnectionCallbacks.delete(callback)
  }

  /**
   * Subscribe to error events
   */
  onError(callback: ErrorCallback): () => void {
    this.errorCallbacks.add(callback)
    return () => this.errorCallbacks.delete(callback)
  }

  /**
   * Emit an event to server
   */
  emit(event: string, data?: any) {
    if (!this.socket) {
      throw new Error('WebSocket not connected')
    }
    this.socket.emit(event, data)
  }

  /**
   * Emit an event and wait for acknowledgment
   */
  async emitWithAck<T = any>(event: string, data?: any, timeout: number = 5000): Promise<T> {
    if (!this.socket) {
      throw new Error('WebSocket not connected')
    }

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error('Acknowledgment timeout'))
      }, timeout)

      this.socket!.emit(event, data, (response: T) => {
        clearTimeout(timer)
        resolve(response)
      })
    })
  }

  /**
   * Subscribe to a specific Flow Builder agent stream
   */
  subscribeToAgent(agentId: string, onMessage: MessageCallback): () => void {
    return this.on(`agent:${agentId}:message`, onMessage)
  }

  /**
   * Subscribe to MCP server logs
   */
  subscribeToMCPLogs(serverId: string, onLog: MessageCallback): () => void {
    return this.on(`mcp:${serverId}:log`, onLog)
  }

  /**
   * Subscribe to service status updates
   */
  subscribeToServiceStatus(serviceId: string, onStatus: MessageCallback): () => void {
    return this.on(`service:${serviceId}:status`, onStatus)
  }

  /**
   * Subscribe to deployment logs
   */
  subscribeToDeploymentLogs(deploymentId: string, onLog: MessageCallback): () => void {
    return this.on(`deployment:${deploymentId}:log`, onLog)
  }

  /**
   * Update base URL (useful for testing or switching environments)
   */
  setBaseURL(url: string) {
    const wasConnected = this.connected
    if (wasConnected) {
      this.disconnect()
    }
    this.baseURL = url
    if (wasConnected) {
      this.connect()
    }
  }

  /**
   * Get current base URL
   */
  getBaseURL(): string {
    return this.baseURL
  }
}

// Export singleton instance
export const wsClient = new WSClient({ autoConnect: false }) // Don't auto-connect, let components decide

// Export class for testing
export { WSClient }
