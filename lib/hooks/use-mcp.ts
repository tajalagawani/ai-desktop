/**
 * MCP Hub Hooks
 * React hooks for MCP Hub API operations
 */

import { useCallback, useEffect } from 'react'
import { apiClient } from '../api-client'
import { wsClient } from '../ws-client'
import { useMCPStore } from '../store/mcp-store'

/**
 * Hook to manage MCP servers
 */
export function useMCPServers() {
  const {
    servers,
    selectedServer,
    loading,
    error,
    setServers,
    setSelectedServer,
    setLoading,
    setError,
    updateServer,
    addServer,
    removeServer,
  } = useMCPStore()

  // Load servers
  const loadServers = useCallback(async (silent = false) => {
    if (!silent) {
      setLoading(true)
    }
    setError(null)

    const response = await apiClient.get('/api/mcp')

    if (response.success) {
      setServers(response.data?.servers || [])

      // Update selected server if it exists
      if (selectedServer) {
        const updated = response.data?.servers?.find((s: any) => s.id === selectedServer.id)
        if (updated) {
          setSelectedServer(updated)
        }
      }
    } else {
      setError(response.error || 'Failed to load MCP servers')
    }

    if (!silent) {
      setLoading(false)
    }
  }, [setServers, setLoading, setError, selectedServer, setSelectedServer])

  // Create server
  const createServer = useCallback(async (data: any) => {
    const response = await apiClient.post('/api/mcp', data)

    if (response.success && response.data?.server) {
      addServer(response.data.server)
    }

    return response
  }, [addServer])

  // Perform action
  const performAction = useCallback(async (id: string, action: string) => {
    const response = await apiClient.post(`/api/mcp/${id}/action`, { action })

    if (response.success) {
      if (action === 'delete') {
        removeServer(id)
      } else {
        const newStatus = action === 'start' ? 'running' : action === 'stop' ? 'stopped' : 'running'
        updateServer(id, { status: newStatus as any })
      }
    }

    return response
  }, [updateServer, removeServer])

  // Subscribe to MCP logs
  const subscribeToLogs = useCallback((serverId: string, onLog: (log: any) => void) => {
    return wsClient.subscribeToMCPLogs(serverId, onLog)
  }, [])

  // Auto-refresh every 5 seconds
  useEffect(() => {
    loadServers(false)

    const interval = setInterval(() => {
      loadServers(true) // Silent refresh
    }, 5000)

    return () => clearInterval(interval)
  }, []) // Empty deps - only run once

  return {
    servers,
    selectedServer,
    loading,
    error,
    loadServers,
    createServer,
    performAction,
    subscribeToLogs,
    setSelectedServer,
  }
}

/**
 * Hook to manage MCP tools
 */
export function useMCPTools(serverId: string | null) {
  const { tools, setTools, setLoading, setError } = useMCPStore()

  // Load tools
  const loadTools = useCallback(async () => {
    if (!serverId) {
      setTools([])
      return
    }

    setLoading(true)
    setError(null)

    const response = await apiClient.get(`/api/mcp/${serverId}/tools`)

    if (response.success) {
      setTools(response.data?.tools || [])
    } else {
      setError(response.error || 'Failed to load tools')
    }

    setLoading(false)
  }, [serverId, setTools, setLoading, setError])

  // Execute tool
  const executeTool = useCallback(async (tool: string, parameters: any) => {
    if (!serverId) {
      return { success: false, error: 'No server selected' }
    }

    return await apiClient.post(`/api/mcp/${serverId}/execute`, { tool, parameters })
  }, [serverId])

  // Load tools when server changes
  useEffect(() => {
    loadTools()
  }, [loadTools])

  return {
    tools,
    loadTools,
    executeTool,
  }
}
