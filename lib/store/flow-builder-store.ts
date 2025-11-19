/**
 * Flow Builder Store
 * Global state management for Flow Builder sessions
 */

import { create } from 'zustand'

export interface FlowSession {
  id: string
  status: 'idle' | 'running' | 'completed' | 'error'
  prompt?: string
  output?: string
  createdAt: string
  updatedAt: string
}

export interface FlowSettings {
  model: string
  maxTokens: number
  temperature: number
}

interface FlowBuilderStore {
  // State
  sessions: FlowSession[]
  currentSession: FlowSession | null
  settings: FlowSettings
  loading: boolean
  error: string | null

  // Actions
  setSessions: (sessions: FlowSession[]) => void
  setCurrentSession: (session: FlowSession | null) => void
  setSettings: (settings: FlowSettings) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // Update single session
  updateSession: (id: string, updates: Partial<FlowSession>) => void

  // Add session
  addSession: (session: FlowSession) => void

  // Remove session
  removeSession: (id: string) => void
}

export const useFlowBuilderStore = create<FlowBuilderStore>((set) => ({
  // Initial state
  sessions: [],
  currentSession: null,
  settings: {
    model: 'claude-3-sonnet',
    maxTokens: 4096,
    temperature: 0.7,
  },
  loading: false,
  error: null,

  // Actions
  setSessions: (sessions) => set({ sessions }),
  setCurrentSession: (currentSession) => set({ currentSession }),
  setSettings: (settings) => set({ settings }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  updateSession: (id, updates) =>
    set((state) => ({
      sessions: state.sessions.map((session) =>
        session.id === id ? { ...session, ...updates } : session
      ),
      currentSession:
        state.currentSession?.id === id
          ? { ...state.currentSession, ...updates }
          : state.currentSession,
    })),

  addSession: (session) =>
    set((state) => ({
      sessions: [session, ...state.sessions],
    })),

  removeSession: (id) =>
    set((state) => ({
      sessions: state.sessions.filter((session) => session.id !== id),
      currentSession:
        state.currentSession?.id === id ? null : state.currentSession,
    })),
}))
