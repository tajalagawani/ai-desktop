/**
 * Site-wide configuration
 * Centralized configuration for the AI Desktop application
 */

export const siteConfig = {
  name: "AI Desktop",
  description: "Web-based AI desktop environment for managing workflows and integrations",
  url: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  author: "Your Name",
  links: {
    github: "https://github.com/yourusername/ai-desktop",
  },
}

export const appConfig = {
  // Feature flags
  features: {
    workflows: true,
    terminal: true,
    fileManager: true,
    appStore: true,
    systemMonitor: true,
    chatInterface: true,
  },

  // Default window settings
  windows: {
    defaultWidth: 800,
    defaultHeight: 600,
    minWidth: 320,
    minHeight: 240,
  },

  // Pagination
  pagination: {
    defaultPageSize: 20,
    maxPageSize: 100,
  },
}

export const apiConfig = {
  // API endpoints (for future backend)
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "/api",
  timeout: 30000, // 30 seconds
}
