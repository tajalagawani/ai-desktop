/**
 * MCP Hub Store
 * Global state management for MCP servers
 */

import { create } from 'zustand'

export interface MCPServer {
  id: string
  name: string
  command: string
  args: string[]
  env?: Record<string, string>
  status: 'running' | 'stopped' | 'error'
  pid?: number
  workingDirectory?: string
  description?: string
  createdAt: string
  updatedAt: string
}

export interface MCPTool {
  name: string
  description: string
  inputSchema: {
    type: string
    properties: Record<string, any>
    required?: string[]
  }
}

interface MCPStore {
  // State
  servers: MCPServer[]
  selectedServer: MCPServer | null
  tools: MCPTool[]
  loading: boolean
  error: string | null

  // Actions
  setServers: (servers: MCPServer[]) => void
  setSelectedServer: (server: MCPServer | null) => void
  setTools: (tools: MCPTool[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // Update single server
  updateServer: (id: string, updates: Partial<MCPServer>) => void

  // Add server
  addServer: (server: MCPServer) => void

  // Remove server
  removeServer: (id: string) => void
}

export const useMCPStore = create<MCPStore>((set) => ({
  // Initial state
  servers: [],
  selectedServer: null,
  tools: [],
  loading: false,
  error: null,

  // Actions
  setServers: (servers) => set({ servers }),
  setSelectedServer: (selectedServer) => set({ selectedServer }),
  setTools: (tools) => set({ tools }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  updateServer: (id, updates) =>
    set((state) => ({
      servers: state.servers.map((server) =>
        server.id === id ? { ...server, ...updates } : server
      ),
      selectedServer:
        state.selectedServer?.id === id
          ? { ...state.selectedServer, ...updates }
          : state.selectedServer,
    })),

  addServer: (server) =>
    set((state) => ({
      servers: [...state.servers, server],
    })),

  removeServer: (id) =>
    set((state) => ({
      servers: state.servers.filter((server) => server.id !== id),
      selectedServer:
        state.selectedServer?.id === id ? null : state.selectedServer,
    })),
}))
