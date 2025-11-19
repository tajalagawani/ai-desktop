/**
 * VS Code Manager Hooks
 * React hooks for VS Code Manager API operations
 */

import { useCallback, useEffect } from 'react'
import { apiClient } from '../api-client'
import { wsClient } from '../ws-client'
import { useVSCodeStore } from '../store/vscode-store'

/**
 * Hook to manage repositories
 */
export function useRepositories() {
  const { repositories, loading, error, setRepositories, setLoading, setError, updateRepository } = useVSCodeStore()

  // Load repositories
  const loadRepositories = useCallback(async () => {
    setLoading(true)
    setError(null)

    const response = await apiClient.get('/api/vscode/list')

    if (response.success) {
      setRepositories(response.data?.repositories || [])
    } else {
      setError(response.error || 'Failed to load repositories')
    }

    setLoading(false)
  }, [setRepositories, setLoading, setError])

  // Start code-server
  const startCodeServer = useCallback(async (repoId: string) => {
    const response = await apiClient.post('/api/vscode/start', { repoId })

    if (response.success) {
      updateRepository(repoId, { running: true })
    }

    return response
  }, [updateRepository])

  // Stop code-server
  const stopCodeServer = useCallback(async (repoId: string) => {
    const response = await apiClient.post('/api/vscode/stop', { repoId })

    if (response.success) {
      updateRepository(repoId, { running: false })
    }

    return response
  }, [updateRepository])

  // Get changes
  const getChanges = useCallback(async (repoId: string) => {
    return await apiClient.get(`/api/vscode/changes/${repoId}`)
  }, [])

  // Get diff
  const getDiff = useCallback(async (repoId: string, file: string) => {
    return await apiClient.post('/api/vscode/diff', { repoId, file })
  }, [])

  // Cleanup
  const cleanup = useCallback(async () => {
    return await apiClient.post('/api/vscode/cleanup')
  }, [])

  // Load on mount
  useEffect(() => {
    loadRepositories()
  }, [loadRepositories])

  return {
    repositories,
    loading,
    error,
    loadRepositories,
    startCodeServer,
    stopCodeServer,
    getChanges,
    getDiff,
    cleanup,
  }
}

/**
 * Hook to manage deployments
 */
export function useDeployments() {
  const { deployments, setDeployments, setLoading, setError, updateDeployment } = useVSCodeStore()

  // Load deployments
  const loadDeployments = useCallback(async () => {
    setLoading(true)
    setError(null)

    const response = await apiClient.get('/api/deployments')

    if (response.success) {
      setDeployments(response.data?.deployments || [])
    } else {
      setError(response.error || 'Failed to load deployments')
    }

    setLoading(false)
  }, [setDeployments, setLoading, setError])

  // Create deployment
  const createDeployment = useCallback(async (data: any) => {
    return await apiClient.post('/api/deployments', data)
  }, [])

  // Perform action
  const performAction = useCallback(async (id: string, action: string) => {
    const response = await apiClient.post(`/api/deployments/${id}/action`, { action })

    if (response.success) {
      const newStatus = action === 'start' ? 'running' : action === 'stop' ? 'stopped' : 'running'
      updateDeployment(id, { status: newStatus as any })
    }

    return response
  }, [updateDeployment])

  // Subscribe to deployment logs
  const subscribeToLogs = useCallback((deploymentId: string, onLog: (log: any) => void) => {
    return wsClient.subscribeToDeploymentLogs(deploymentId, onLog)
  }, [])

  // Load on mount
  useEffect(() => {
    loadDeployments()
  }, [loadDeployments])

  return {
    deployments,
    loadDeployments,
    createDeployment,
    performAction,
    subscribeToLogs,
  }
}

/**
 * Hook to manage flows
 */
export function useFlows() {
  const { flows, setFlows } = useVSCodeStore()

  // Load flows
  const loadFlows = useCallback(async () => {
    const response = await apiClient.get('/api/files?path=flows&pattern=*.flow')

    if (response.success) {
      setFlows(response.data?.files || [])
    }
  }, [setFlows])

  // Load on mount
  useEffect(() => {
    loadFlows()
  }, [loadFlows])

  return {
    flows,
    loadFlows,
  }
}
