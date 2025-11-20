import { useEffect, useCallback, useRef, useState } from 'react'
import { io, Socket } from 'socket.io-client'
import { apiFetch } from '@/lib/utils/api'

interface Service {
  id: string
  name: string
  icon: string
  iconType?: 'lucide' | 'image'
  ports?: number[]
  status: string
  installed: boolean
  category: string
  description: string
  dockerImage?: string
  containerName?: string
  defaultCredentials?: any
  volumes?: string[]
  environment?: Record<string, string>
  windowComponent?: string
  defaultWidth?: number
  defaultHeight?: number
}

interface ServicesData {
  success: boolean
  dockerInstalled: boolean
  services: Service[]
  count: number
}

/**
 * Custom hook for real-time service synchronization
 * Provides automatic WebSocket connection and service data updates
 */
export function useServicesSync() {
  const [services, setServices] = useState<Service[]>([])
  const [dockerInstalled, setDockerInstalled] = useState(false)
  const [loading, setLoading] = useState(true)
  const [connected, setConnected] = useState(false)

  const socketRef = useRef<Socket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  // Fetch services from API
  const fetchServices = useCallback(async (silent = false) => {
    if (!silent) {
      setLoading(true)
    }

    try {
      const response = await apiFetch('/api/services', {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache'
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch services')
      }

      const data: ServicesData = await response.json()
      setServices(data.services || [])
      setDockerInstalled(data.dockerInstalled)
    } catch (error) {
      console.error('[ServicesSync] Failed to fetch services:', error)
    } finally {
      if (!silent) {
        setLoading(false)
      }
    }
  }, [])

  // Initialize WebSocket connection
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3006'

    console.log('[ServicesSync] Connecting to:', apiUrl)

    const socket = io(apiUrl, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
    })

    socketRef.current = socket

    // Connection handlers
    socket.on('connect', () => {
      console.log('[ServicesSync] WebSocket connected')
      setConnected(true)

      // Clear any pending reconnect timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }

      // Fetch initial data
      fetchServices(true)
    })

    socket.on('disconnect', (reason) => {
      console.log('[ServicesSync] WebSocket disconnected:', reason)
      setConnected(false)

      // Auto-reconnect after 2 seconds if not manually disconnected
      if (reason === 'io server disconnect') {
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('[ServicesSync] Attempting to reconnect...')
          socket.connect()
        }, 2000)
      }
    })

    socket.on('connect_error', (error) => {
      console.error('[ServicesSync] Connection error:', error.message)
      setConnected(false)
    })

    // Listen for service updates
    socket.on('services:updated', (data: { serviceId: string; action: string }) => {
      console.log('[ServicesSync] Service updated:', data)
      // Fetch latest services data
      fetchServices(true)
    })

    // Cleanup
    return () => {
      console.log('[ServicesSync] Cleaning up WebSocket connection')
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      socket.off('connect')
      socket.off('disconnect')
      socket.off('connect_error')
      socket.off('services:updated')
      socket.close()
    }
  }, [fetchServices])

  // Initial load
  useEffect(() => {
    fetchServices(false)
  }, [fetchServices])

  // Manual refresh function
  const refresh = useCallback(() => {
    fetchServices(false)
  }, [fetchServices])

  return {
    services,
    dockerInstalled,
    loading,
    connected,
    refresh,
  }
}
