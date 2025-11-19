/**
 * Service Manager Hooks
 * React hooks for Service Manager API operations
 */

import { useCallback, useEffect } from 'react'
import { apiClient } from '../api-client'
import { wsClient } from '../ws-client'
import { useServicesStore } from '../store/services-store'

/**
 * Hook to manage services
 */
export function useServices() {
  const {
    services,
    dockerInstalled,
    loading,
    error,
    setServices,
    setDockerInstalled,
    setLoading,
    setError,
    updateService,
    addService,
    removeService,
  } = useServicesStore()

  // Load services
  const loadServices = useCallback(async (silent = false) => {
    if (!silent) {
      setLoading(true)
    }
    setError(null)

    const response = await apiClient.get('/api/services')

    if (response.success) {
      setServices(response.data?.services || [])
      setDockerInstalled(response.data?.dockerInstalled || false)
    } else {
      setError(response.error || 'Failed to load services')
    }

    if (!silent) {
      setLoading(false)
    }
  }, [setServices, setDockerInstalled, setLoading, setError])

  // Perform action
  const performAction = useCallback(async (serviceId: string, action: string) => {
    const response = await apiClient.post('/api/services', { serviceId, action })

    if (response.success) {
      if (action === 'remove') {
        removeService(serviceId)
      } else if (action === 'install') {
        // Reload to get the new service
        loadServices(true)
      } else {
        const newStatus = action === 'start' ? 'running' : action === 'stop' ? 'stopped' : 'running'
        updateService(serviceId, { status: newStatus as any })
      }
    }

    return response
  }, [updateService, removeService, loadServices])

  // Subscribe to service status
  const subscribeToStatus = useCallback((serviceId: string, onStatus: (status: any) => void) => {
    return wsClient.subscribeToServiceStatus(serviceId, onStatus)
  }, [])

  // Get logs
  const getLogs = useCallback(async (serviceId: string) => {
    return await apiClient.post('/api/services', { serviceId, action: 'logs' })
  }, [])

  // Auto-refresh every 10 seconds
  useEffect(() => {
    loadServices(false)

    const interval = setInterval(() => {
      loadServices(true) // Silent refresh
    }, 10000)

    return () => clearInterval(interval)
  }, []) // Empty deps - only run once

  return {
    services,
    dockerInstalled,
    loading,
    error,
    loadServices,
    performAction,
    subscribeToStatus,
    getLogs,
  }
}
