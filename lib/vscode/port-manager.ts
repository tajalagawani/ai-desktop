import fs from 'fs'
import path from 'path'
import { VSCodeInstance, PortDatabase } from '../repositories/types'

const PORTS_FILE = path.join(process.cwd(), 'data', 'vscode-ports.json')

export class PortManager {
  private loadDatabase(): PortDatabase {
    try {
      if (!fs.existsSync(PORTS_FILE)) {
        const initial: PortDatabase = {
          instances: {},
          availablePorts: Array.from({ length: 12 }, (_, i) => 8888 + i)
        }
        this.saveDatabase(initial)
        return initial
      }
      return JSON.parse(fs.readFileSync(PORTS_FILE, 'utf-8'))
    } catch (error) {
      console.error('[PortManager] Failed to load database:', error)
      return {
        instances: {},
        availablePorts: Array.from({ length: 12 }, (_, i) => 8888 + i)
      }
    }
  }

  private saveDatabase(db: PortDatabase): void {
    try {
      const dir = path.dirname(PORTS_FILE)
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true })
      }
      fs.writeFileSync(PORTS_FILE, JSON.stringify(db, null, 2), 'utf-8')
    } catch (error) {
      console.error('[PortManager] Failed to save database:', error)
      throw error
    }
  }

  allocatePort(projectName: string): number | null {
    const db = this.loadDatabase()

    // Check if project already has a port
    if (db.instances[projectName]) {
      console.log(`[PortManager] Project ${projectName} already has port ${db.instances[projectName].port}`)
      return db.instances[projectName].port
    }

    // Allocate next available port
    if (db.availablePorts.length === 0) {
      console.error('[PortManager] No available ports')
      return null // All ports in use
    }

    const port = db.availablePorts.shift()!
    this.saveDatabase(db)
    console.log(`[PortManager] Allocated port ${port} for ${projectName}`)
    return port
  }

  registerInstance(projectName: string, port: number, pid: number, repoPath: string): void {
    const db = this.loadDatabase()
    db.instances[projectName] = {
      port,
      pid,
      projectName,
      repoPath,
      startedAt: new Date().toISOString()
    }
    this.saveDatabase(db)
    console.log(`[PortManager] Registered instance: ${projectName} on port ${port} (PID: ${pid})`)
  }

  releasePort(projectName: string): void {
    const db = this.loadDatabase()
    const instance = db.instances[projectName]

    if (instance) {
      db.availablePorts.push(instance.port)
      db.availablePorts.sort((a, b) => a - b)
      delete db.instances[projectName]
      this.saveDatabase(db)
      console.log(`[PortManager] Released port ${instance.port} for ${projectName}`)
    }
  }

  getInstance(projectName: string): VSCodeInstance | null {
    const db = this.loadDatabase()
    return db.instances[projectName] || null
  }

  getAllInstances(): VSCodeInstance[] {
    const db = this.loadDatabase()
    return Object.values(db.instances)
  }

  getPortByProjectName(projectName: string): number | null {
    const instance = this.getInstance(projectName)
    return instance ? instance.port : null
  }

  isPortInUse(port: number): boolean {
    const db = this.loadDatabase()
    return Object.values(db.instances).some(inst => inst.port === port)
  }
}
