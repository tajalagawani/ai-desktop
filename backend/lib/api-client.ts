/**
 * API Client for Backend Communication
 * Handles HTTP requests to Express backend on port 3006
 */

interface RequestOptions extends RequestInit {
  timeout?: number
}

interface APIResponse<T = any> {
  success: boolean
  data?: any
  error?: string
}

class APIClient {
  private baseURL: string
  private defaultTimeout: number = 30000

  constructor() {
    if (typeof window !== 'undefined') {
      this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3006'
    } else {
      this.baseURL = process.env.API_URL || 'http://localhost:3006'
    }
  }

  private async request<T = any>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<APIResponse<T>> {
    const { timeout = this.defaultTimeout, ...fetchOptions } = options
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const url = `${this.baseURL}${endpoint}`
      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...fetchOptions.headers,
        },
      })

      clearTimeout(timeoutId)
      const data = await response.json()

      if (!response.ok) {
        return {
          success: false,
          error: data.error || `HTTP ${response.status}`,
        }
      }

      return data
    } catch (error: any) {
      clearTimeout(timeoutId)
      return {
        success: false,
        error: error.name === 'AbortError' ? 'Request timeout' : error.message,
      }
    }
  }

  async get<T = any>(endpoint: string, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  async post<T = any>(endpoint: string, body?: any, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(body),
    })
  }

  async put<T = any>(endpoint: string, body?: any, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(body),
    })
  }

  async delete<T = any>(endpoint: string, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }
}

const apiClient = new APIClient()
export default apiClient
