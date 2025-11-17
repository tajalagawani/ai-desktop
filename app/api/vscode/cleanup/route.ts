import { NextResponse } from 'next/server'
import { VSCodeManager } from '@/lib/vscode/manager'

/**
 * Cleanup orphaned VS Code processes
 * Called on app startup to clean up any processes from previous sessions
 */
export async function POST() {
  try {
    const manager = new VSCodeManager()

    // Get all running instances
    const instances = await manager.getRunningInstances()

    console.log(`[VSCode Cleanup] Found ${instances.length} running instances`)

    // Get all known repositories
    const repos = await manager.getAllRepositories()
    const knownRepoIds = new Set(repos.map(r => r.id))

    // Kill orphaned processes (instances not in repository list)
    let cleaned = 0
    for (const instance of instances) {
      if (!instance.repoId || !knownRepoIds.has(instance.repoId)) {
        console.log(`[VSCode Cleanup] Killing orphaned process PID ${instance.pid}`)
        try {
          process.kill(instance.pid, 'SIGTERM')
          cleaned++
        } catch (error: any) {
          console.error(`[VSCode Cleanup] Failed to kill PID ${instance.pid}:`, error.message)
        }
      }
    }

    console.log(`[VSCode Cleanup] Cleaned up ${cleaned} orphaned processes`)

    return NextResponse.json({
      success: true,
      cleaned,
      total: instances.length
    })
  } catch (error: any) {
    console.error('[VSCode Cleanup] Error:', error)
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    )
  }
}
