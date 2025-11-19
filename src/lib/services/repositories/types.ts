export interface Repository {
  id: string              // Unique identifier (sanitized repo name)
  name: string            // Display name
  path: string            // Full path on VPS
  type: 'git' | 'folder'  // Repository type
  addedAt: string         // ISO timestamp
  branch?: string         // Current git branch (if git repo)
}

export interface RepositoryRegistry {
  repositories: Repository[]
}
