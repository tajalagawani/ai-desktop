export interface Repository {
  id: string              // Unique identifier (sanitized repo name)
  name: string            // Display name
  path: string            // Full path on VPS
  type: 'git' | 'folder'  // Repository type
  addedAt: string         // ISO timestamp
  lastOpened?: string     // Last opened in VS Code
  vscodePort?: number     // Port if code-server is running
  vscodeRunning: boolean  // Is code-server active
  branch?: string         // Current git branch (if git repo)
}

export interface RepositoryRegistry {
  repositories: Repository[]
}

export interface VSCodeInstance {
  port: number
  pid: number
  projectName: string
  repoPath: string
  startedAt: string
}

export interface PortDatabase {
  instances: Record<string, VSCodeInstance>
  availablePorts: number[]
}
