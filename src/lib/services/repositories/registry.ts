import fs from 'fs'
import path from 'path'
import { Repository, RepositoryRegistry } from './types'

const REGISTRY_FILE = path.join(process.cwd(), 'data', 'repositories.json')

export class RepositoryManager {
  private loadRegistry(): RepositoryRegistry {
    try {
      if (!fs.existsSync(REGISTRY_FILE)) {
        const initialData: RepositoryRegistry = { repositories: [] }
        this.saveRegistry(initialData)
        return initialData
      }
      const content = fs.readFileSync(REGISTRY_FILE, 'utf-8')
      return JSON.parse(content)
    } catch (error) {
      console.error('[RepositoryManager] Failed to load registry:', error)
      return { repositories: [] }
    }
  }

  private saveRegistry(data: RepositoryRegistry): void {
    try {
      const dir = path.dirname(REGISTRY_FILE)
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true })
      }
      fs.writeFileSync(REGISTRY_FILE, JSON.stringify(data, null, 2), 'utf-8')
    } catch (error) {
      console.error('[RepositoryManager] Failed to save registry:', error)
      throw error
    }
  }

  addRepository(name: string, repoPath: string, type: 'git' | 'folder' = 'git', branch?: string): Repository {
    const registry = this.loadRegistry()
    const id = name.replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase()

    // Check if already exists
    const existing = registry.repositories.find(r => r.path === repoPath)
    if (existing) {
      return existing
    }

    const repo: Repository = {
      id,
      name,
      path: repoPath,
      type,
      addedAt: new Date().toISOString(),
      branch
    }

    registry.repositories.push(repo)
    this.saveRegistry(registry)
    console.log(`[RepositoryManager] Added repository: ${name} at ${repoPath}`)
    return repo
  }

  removeRepository(repoPath: string): void {
    const registry = this.loadRegistry()
    const before = registry.repositories.length
    registry.repositories = registry.repositories.filter(r => r.path !== repoPath)
    const after = registry.repositories.length

    if (before !== after) {
      this.saveRegistry(registry)
      console.log(`[RepositoryManager] Removed repository: ${repoPath}`)
    }
  }

  getRepository(idOrPath: string): Repository | null {
    const registry = this.loadRegistry()
    return registry.repositories.find(r => r.id === idOrPath || r.path === idOrPath) || null
  }

  getAllRepositories(): Repository[] {
    const registry = this.loadRegistry()
    return registry.repositories
  }

  updateRepository(id: string, updates: Partial<Repository>): void {
    const registry = this.loadRegistry()
    const repo = registry.repositories.find(r => r.id === id)
    if (repo) {
      Object.assign(repo, updates)
      this.saveRegistry(registry)
      console.log(`[RepositoryManager] Updated repository: ${id}`)
    }
  }

  // Check if repository path still exists on filesystem
  async validateRepository(repoPath: string): Promise<boolean> {
    try {
      const stats = await fs.promises.stat(repoPath)
      return stats.isDirectory()
    } catch {
      return false
    }
  }

  // Clean up repositories that no longer exist
  async cleanupInvalidRepositories(): Promise<string[]> {
    const registry = this.loadRegistry()
    const removed: string[] = []

    for (const repo of registry.repositories) {
      const exists = await this.validateRepository(repo.path)
      if (!exists) {
        removed.push(repo.path)
        this.removeRepository(repo.path)
      }
    }

    return removed
  }
}
