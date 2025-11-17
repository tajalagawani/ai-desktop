export interface DeploymentConfig {
  id: string
  repoId: string
  repoName: string
  repoPath: string
  framework: FrameworkType
  buildCommand: string | null
  startCommand: string
  port: number
  domain?: string
  services: string[] // Container names like "ai-desktop-mysql"
  envVars: Record<string, string>
  status: 'deploying' | 'running' | 'stopped' | 'failed' | 'building'
  pm2Name: string
  nginxConfig?: string
  deployedAt: string
  lastDeployedAt?: string
  buildLogs?: string
  error?: string
}

export interface FrameworkDetection {
  type: FrameworkType
  version?: string
  buildCommand: string | null
  startCommand: string
  installCommand: string
  outputDir?: string
  port: number
}

export type FrameworkType =
  | 'nextjs'
  | 'react-vite'
  | 'react-cra'
  | 'vue'
  | 'nuxt'
  | 'angular'
  | 'svelte'
  | 'astro'
  | 'node'
  | 'express'
  | 'nestjs'
  | 'django'
  | 'flask'
  | 'fastapi'
  | 'laravel'
  | 'symfony'
  | 'static'

export interface RunningService {
  id: string
  name: string
  containerName: string
  port: number
  type: 'database' | 'cache' | 'queue' | 'search' | 'tool' | 'other'
  category: string
  connectionString: string
  credentials?: {
    username?: string
    password?: string
    port?: number
  }
}

export interface DeploymentAction {
  action: 'start' | 'stop' | 'restart' | 'delete' | 'rebuild'
  deploymentId: string
}

export interface DeploymentLog {
  timestamp: string
  type: 'build' | 'runtime' | 'error' | 'info'
  message: string
}
