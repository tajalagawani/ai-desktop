/**
 * API Client - Centralized backend communication
 * Handles all HTTP requests to the VPS backend
 */

export interface APIResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  body?: any
  headers?: Record<string, string>
  timeout?: number
  retry?: number
}

class APIClient {
  private baseURL: string
  private defaultTimeout: number = 30000 // 30 seconds
  private maxRetries: number = 3
  private retryDelay: number = 1000 // 1 second

  constructor() {
    // Determine backend URL based on environment
    if (typeof window !== 'undefined') {
      // Client-side: Use environment variable or default to backend on 3006
      this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3006'
    } else {
      // Server-side: Use environment variable or backend on 3006
      this.baseURL = process.env.API_URL || 'http://localhost:3006'
    }
  }

  /**
   * Make HTTP request with retry logic
   */
  private async request<T = any>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<APIResponse<T>> {
    const {
      method = 'GET',
      body,
      headers = {},
      timeout = this.defaultTimeout,
      retry = this.maxRetries,
    } = options

    const url = `${this.baseURL}${endpoint}`
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers,
    }

    let lastError: Error | null = null

    // Retry loop
    for (let attempt = 0; attempt <= retry; attempt++) {
      try {
        // Create abort controller for timeout
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), timeout)

        const response = await fetch(url, {
          method,
          headers: requestHeaders,
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal,
          credentials: 'include', // Include cookies for authentication
        })

        clearTimeout(timeoutId)

        // Parse response
        let data: any
        const contentType = response.headers.get('content-type')

        if (contentType && contentType.includes('application/json')) {
          data = await response.json()
        } else {
          const text = await response.text()
          data = { success: response.ok, data: text }
        }

        // Return response
        if (response.ok) {
          return {
            success: true,
            ...data,
          }
        } else {
          // Don't retry on client errors (4xx)
          if (response.status >= 400 && response.status < 500) {
            return {
              success: false,
              error: data.error || `HTTP ${response.status}: ${response.statusText}`,
            }
          }

          // Retry on server errors (5xx)
          throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`)
        }
      } catch (error: any) {
        lastError = error

        // Don't retry on abort (user cancelled)
        if (error.name === 'AbortError') {
          return {
            success: false,
            error: 'Request timeout',
          }
        }

        // Last attempt failed
        if (attempt === retry) {
          break
        }

        // Wait before retry (exponential backoff)
        await new Promise(resolve =>
          setTimeout(resolve, this.retryDelay * Math.pow(2, attempt))
        )
      }
    }

    // All retries failed
    return {
      success: false,
      error: lastError?.message || 'Network error',
    }
  }

  /**
   * GET request
   */
  async get<T = any>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  /**
   * POST request
   */
  async post<T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'POST', body })
  }

  /**
   * PUT request
   */
  async put<T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body })
  }

  /**
   * DELETE request
   */
  async delete<T = any>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }

  /**
   * PATCH request
   */
  async patch<T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PATCH', body })
  }

  /**
   * Update base URL (useful for testing or switching environments)
   */
  setBaseURL(url: string) {
    this.baseURL = url
  }

  /**
   * Get current base URL
   */
  getBaseURL(): string {
    return this.baseURL
  }
}

// Export singleton instance
export const apiClient = new APIClient()

// Export class for testing
export { APIClient }
