/**
 * VS Code Manager Store
 * Global state management for repositories and code-server instances
 */

import { create } from 'zustand'

export interface Repository {
  id: string
  name: string
  path: string
  type: 'git' | 'local'
  port: number
  url?: string
  branch?: string
  running: boolean
  pid?: number
  created_at: string
  updated_at: string
}

export interface Deployment {
  id: string
  repository_id: string
  repository_name?: string
  repository_path?: string
  name: string
  domain: string
  port: number
  status: 'running' | 'stopped' | 'error'
  mode: 'cluster' | 'fork'
  instances?: number
  pid?: number
  memory?: number
  cpu?: number
  uptime?: number
  created_at: string
  updated_at: string
}

export interface Flow {
  name: string
  path: string
  size: number
  modifiedAt: string
}

interface VSCodeStore {
  // State
  repositories: Repository[]
  deployments: Deployment[]
  flows: Flow[]
  loading: boolean
  error: string | null

  // Actions
  setRepositories: (repositories: Repository[]) => void
  setDeployments: (deployments: Deployment[]) => void
  setFlows: (flows: Flow[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // Update single repository
  updateRepository: (id: string, updates: Partial<Repository>) => void

  // Update single deployment
  updateDeployment: (id: string, updates: Partial<Deployment>) => void
}

export const useVSCodeStore = create<VSCodeStore>((set) => ({
  // Initial state
  repositories: [],
  deployments: [],
  flows: [],
  loading: false,
  error: null,

  // Actions
  setRepositories: (repositories) => set({ repositories }),
  setDeployments: (deployments) => set({ deployments }),
  setFlows: (flows) => set({ flows }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  updateRepository: (id, updates) =>
    set((state) => ({
      repositories: state.repositories.map((repo) =>
        repo.id === id ? { ...repo, ...updates } : repo
      ),
    })),

  updateDeployment: (id, updates) =>
    set((state) => ({
      deployments: state.deployments.map((dep) =>
        dep.id === id ? { ...dep, ...updates } : dep
      ),
    })),
}))
