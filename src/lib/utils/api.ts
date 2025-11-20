/**
 * API Utilities - Simple wrapper for backend API calls
 *
 * Use this instead of fetch('/api/...') to ensure calls go to the backend server
 */

import { apiClient } from '@/lib/api/client'

// Re-export the API client for advanced usage
export { apiClient }

/**
 * Simple fetch wrapper that automatically uses the correct backend URL
 *
 * @example
 * // Before:
 * const res = await fetch('/api/services')
 *
 * // After:
 * const res = await apiFetch('/api/services')
 */
export async function apiFetch(endpoint: string, options?: RequestInit): Promise<Response> {
  const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3006'

  // Ensure endpoint starts with /
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`

  const url = `${baseURL}${cleanEndpoint}`

  return fetch(url, options)
}

/**
 * Get the base API URL
 */
export function getApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3006'
}
