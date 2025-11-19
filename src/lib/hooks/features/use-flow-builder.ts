/**
 * Flow Builder Hooks
 * React hooks for Flow Builder API operations
 */

import { useCallback, useEffect } from 'react'
import { apiClient } from '../api-client'
import { wsClient } from '../ws-client'
import { useFlowBuilderStore } from '../store/flow-builder-store'

/**
 * Hook to manage Flow Builder sessions
 */
export function useFlowBuilder() {
  const {
    sessions,
    currentSession,
    loading,
    error,
    setSessions,
    setCurrentSession,
    setLoading,
    setError,
    updateSession,
    addSession,
    removeSession,
  } = useFlowBuilderStore()

  // Load sessions
  const loadSessions = useCallback(async () => {
    setLoading(true)
    setError(null)

    const response = await apiClient.get('/api/flow-builder/sessions')

    if (response.success) {
      setSessions(response.data?.sessions || [])
    } else {
      setError(response.error || 'Failed to load sessions')
    }

    setLoading(false)
  }, [setSessions, setLoading, setError])

  // Create session
  const createSession = useCallback(async (prompt: string) => {
    const response = await apiClient.post('/api/flow-builder/sessions', { prompt })

    if (response.success && response.data?.session) {
      addSession(response.data.session)
      setCurrentSession(response.data.session)
    }

    return response
  }, [addSession, setCurrentSession])

  // Get session
  const getSession = useCallback(async (id: string) => {
    const response = await apiClient.get(`/api/flow-builder/sessions/${id}`)

    if (response.success && response.data?.session) {
      setCurrentSession(response.data.session)
    }

    return response
  }, [setCurrentSession])

  // Delete session
  const deleteSession = useCallback(async (id: string) => {
    const response = await apiClient.delete(`/api/flow-builder/sessions/${id}`)

    if (response.success) {
      removeSession(id)

      if (currentSession?.id === id) {
        setCurrentSession(null)
      }
    }

    return response
  }, [removeSession, currentSession, setCurrentSession])

  // Subscribe to agent output
  const subscribeToAgent = useCallback((agentId: string, onMessage: (data: any) => void) => {
    return wsClient.subscribeToAgent(agentId, (data) => {
      // Update session with new output
      updateSession(agentId, {
        output: data.content,
        status: data.type === 'complete' ? 'completed' : 'running',
      })

      onMessage(data)
    })
  }, [updateSession])

  // Load on mount
  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  return {
    sessions,
    currentSession,
    loading,
    error,
    loadSessions,
    createSession,
    getSession,
    deleteSession,
    subscribeToAgent,
    setCurrentSession,
  }
}

/**
 * Hook to manage Flow Builder settings
 */
export function useFlowBuilderSettings() {
  const { settings, setSettings, setLoading, setError } = useFlowBuilderStore()

  // Load settings
  const loadSettings = useCallback(async () => {
    setLoading(true)
    setError(null)

    const response = await apiClient.get('/api/flow-builder/settings')

    if (response.success && response.data?.settings) {
      setSettings(response.data.settings)
    } else {
      setError(response.error || 'Failed to load settings')
    }

    setLoading(false)
  }, [setSettings, setLoading, setError])

  // Update settings
  const updateSettings = useCallback(async (newSettings: Partial<typeof settings>) => {
    const response = await apiClient.post('/api/flow-builder/settings', newSettings)

    if (response.success && response.data?.settings) {
      setSettings(response.data.settings)
    }

    return response
  }, [setSettings])

  // Load on mount
  useEffect(() => {
    loadSettings()
  }, [loadSettings])

  return {
    settings,
    loadSettings,
    updateSettings,
  }
}
