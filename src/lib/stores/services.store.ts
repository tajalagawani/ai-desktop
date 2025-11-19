/**
 * Service Manager Store
 * Global state management for Docker services
 */

import { create } from 'zustand'

export interface Service {
  id: string
  name: string
  type: 'docker' | 'pm2' | 'systemd'
  status: 'running' | 'stopped' | 'error'
  port?: number
  containerId?: string
  image?: string
  pid?: number
  memory?: number
  cpu?: number
  uptime?: number
  autoRestart?: boolean
  createdAt: string
  updatedAt: string
}

interface ServicesStore {
  // State
  services: Service[]
  dockerInstalled: boolean
  loading: boolean
  error: string | null

  // Actions
  setServices: (services: Service[]) => void
  setDockerInstalled: (installed: boolean) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // Update single service
  updateService: (id: string, updates: Partial<Service>) => void

  // Add service
  addService: (service: Service) => void

  // Remove service
  removeService: (id: string) => void
}

export const useServicesStore = create<ServicesStore>((set) => ({
  // Initial state
  services: [],
  dockerInstalled: false,
  loading: false,
  error: null,

  // Actions
  setServices: (services) => set({ services }),
  setDockerInstalled: (dockerInstalled) => set({ dockerInstalled }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  updateService: (id, updates) =>
    set((state) => ({
      services: state.services.map((service) =>
        service.id === id ? { ...service, ...updates } : service
      ),
    })),

  addService: (service) =>
    set((state) => ({
      services: [...state.services, service],
    })),

  removeService: (id) =>
    set((state) => ({
      services: state.services.filter((service) => service.id !== id),
    })),
}))
