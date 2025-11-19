/**
 * Shared Types - Used by both client and backend
 */

// ============================================
// API Response Types
// ============================================

export interface APIResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

// ============================================
// VS Code Manager Types
// ============================================

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
  createdAt: string
  updatedAt: string
}

export interface Deployment {
  id: string
  repositoryId: string
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
  createdAt: string
  updatedAt: string
}

export interface Flow {
  name: string
  path: string
  size: number
  modifiedAt: string
}

// ============================================
// MCP Hub Types
// ============================================

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

export interface MCPPlaygroundRequest {
  tool: string
  parameters: Record<string, any>
}

export interface MCPPlaygroundResponse {
  success: boolean
  result?: any
  error?: string
  executionTime?: number
}

// ============================================
// Service Manager Types
// ============================================

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

// ============================================
// Flow Builder Types
// ============================================

export interface FlowBuilderAgent {
  id: string
  status: 'idle' | 'running' | 'completed' | 'error'
  prompt?: string
  output?: string
  createdAt: string
}

export interface FlowBuilderMessage {
  id: string
  agentId: string
  type: 'user' | 'assistant' | 'system' | 'tool'
  content: string
  timestamp: string
}

// ============================================
// WebSocket Event Types
// ============================================

export interface WSAgentMessage {
  agentId: string
  type: 'output' | 'error' | 'complete'
  content: string
  timestamp: string
}

export interface WSMCPLog {
  serverId: string
  level: 'info' | 'warn' | 'error' | 'debug'
  message: string
  timestamp: string
}

export interface WSServiceStatus {
  serviceId: string
  status: 'running' | 'stopped' | 'error'
  memory?: number
  cpu?: number
  timestamp: string
}

export interface WSDeploymentLog {
  deploymentId: string
  type: 'stdout' | 'stderr'
  message: string
  timestamp: string
}

// ============================================
// Database Models (for PostgreSQL migration)
// ============================================

export interface DBRepository {
  id: string
  name: string
  path: string
  type: 'git' | 'local'
  port: number
  url: string | null
  branch: string | null
  running: boolean
  pid: number | null
  created_at: Date
  updated_at: Date
}

export interface DBDeployment {
  id: string
  repository_id: string
  name: string
  domain: string
  port: number
  status: 'running' | 'stopped' | 'error'
  mode: 'cluster' | 'fork'
  instances: number | null
  pid: number | null
  memory: number | null
  cpu: number | null
  uptime: number | null
  created_at: Date
  updated_at: Date
}

export interface DBMCPServer {
  id: string
  name: string
  command: string
  args: string[]
  env: Record<string, string> | null
  status: 'running' | 'stopped' | 'error'
  pid: number | null
  working_directory: string | null
  description: string | null
  created_at: Date
  updated_at: Date
}

export interface DBService {
  id: string
  name: string
  type: 'docker' | 'pm2' | 'systemd'
  status: 'running' | 'stopped' | 'error'
  port: number | null
  container_id: string | null
  image: string | null
  pid: number | null
  memory: number | null
  cpu: number | null
  uptime: number | null
  auto_restart: boolean
  created_at: Date
  updated_at: Date
}
