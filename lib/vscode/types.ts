/**
 * VS Code Manager Type Definitions
 */

export interface VSCodeRepository {
  id: string
  name: string
  path: string
  type: 'git' | 'folder'
  branch?: string
  addedAt: string

  // Runtime status (determined by checking processes)
  running: boolean
  port: number | null
  pid: number | null
  url: string | null
  uptime: string | null

  // Git status
  changes?: number
  ahead?: number
  behind?: number
  added?: number
  modified?: number
  deleted?: number
}

export interface RunningInstance {
  pid: number
  port: number
  repoPath: string
  repoId?: string
  cpu: string
  memory: string
  uptime: string
  command: string
}

export interface StartResult {
  success: boolean
  url: string
  port: number
  pid: number
  message: string
}

export interface StopResult {
  success: boolean
  message: string
}

export interface StatusResult {
  instances: RunningInstance[]
  totalRunning: number
  availablePorts: number
}
