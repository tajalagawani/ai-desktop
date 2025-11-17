import { NextRequest, NextResponse } from 'next/server'
import { RepositoryManager } from '@/lib/repositories/registry'

export const dynamic = 'force-dynamic'

const repoManager = new RepositoryManager()

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const id = searchParams.get('id')

    if (id) {
      // Get specific repository
      const repo = repoManager.getRepository(id)
      if (!repo) {
        return NextResponse.json({ error: 'Repository not found' }, { status: 404 })
      }
      return NextResponse.json({ success: true, repository: repo })
    }

    // Get all repositories
    const repositories = repoManager.getAllRepositories()
    return NextResponse.json({
      success: true,
      repositories,
      total: repositories.length
    })

  } catch (error: any) {
    console.error('[API] Get repositories error:', error)
    return NextResponse.json({
      error: error.message || 'Failed to get repositories',
      details: error.stack
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, name, path: repoPath, type, branch, id, updates } = body

    console.log(`[API] Repository action: ${action}`, { name, repoPath, type })

    if (action === 'add') {
      if (!name || !repoPath) {
        return NextResponse.json({
          error: 'Name and path are required for adding repository'
        }, { status: 400 })
      }

      const repo = repoManager.addRepository(name, repoPath, type || 'git', branch)
      return NextResponse.json({
        success: true,
        message: 'Repository added successfully',
        repository: repo
      })
    }

    if (action === 'remove') {
      if (!repoPath) {
        return NextResponse.json({
          error: 'Path is required for removing repository'
        }, { status: 400 })
      }

      repoManager.removeRepository(repoPath)
      return NextResponse.json({
        success: true,
        message: 'Repository removed successfully'
      })
    }

    if (action === 'update') {
      if (!id || !updates) {
        return NextResponse.json({
          error: 'ID and updates are required'
        }, { status: 400 })
      }

      repoManager.updateRepository(id, updates)
      const updated = repoManager.getRepository(id)

      return NextResponse.json({
        success: true,
        message: 'Repository updated successfully',
        repository: updated
      })
    }

    if (action === 'cleanup') {
      const removed = await repoManager.cleanupInvalidRepositories()
      return NextResponse.json({
        success: true,
        message: `Cleaned up ${removed.length} invalid repositories`,
        removed
      })
    }

    return NextResponse.json({
      error: 'Invalid action. Supported: add, remove, update, cleanup'
    }, { status: 400 })

  } catch (error: any) {
    console.error('[API] Repository action error:', error)
    return NextResponse.json({
      error: error.message || 'Repository action failed',
      details: error.stack
    }, { status: 500 })
  }
}
