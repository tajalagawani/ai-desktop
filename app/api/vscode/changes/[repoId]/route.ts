import { NextRequest, NextResponse } from 'next/server'
import { execSync } from 'child_process'
import { RepositoryManager } from '@/lib/repositories/registry'

interface GitChange {
  path: string
  status: 'modified' | 'added' | 'deleted' | 'renamed'
  additions?: number
  deletions?: number
}

export async function GET(
  request: NextRequest,
  { params }: { params: { repoId: string } }
) {
  try {
    const repoId = params.repoId
    const repoManager = new RepositoryManager()
    const repo = repoManager.getRepository(repoId)

    if (!repo) {
      return NextResponse.json(
        { success: false, error: 'Repository not found' },
        { status: 404 }
      )
    }

    // Get git status
    const statusOutput = execSync('git status --porcelain', {
      cwd: repo.path,
      encoding: 'utf-8'
    })

    const changes: GitChange[] = []
    const lines = statusOutput.trim().split('\n').filter(l => l.length > 0)

    for (const line of lines) {
      const statusCode = line.substring(0, 2)
      const filePath = line.substring(3)

      let status: GitChange['status'] = 'modified'
      if (statusCode.includes('A')) status = 'added'
      else if (statusCode.includes('D')) status = 'deleted'
      else if (statusCode.includes('R')) status = 'renamed'
      else if (statusCode.includes('M')) status = 'modified'

      // Get diff stats for the file
      let additions = 0
      let deletions = 0
      try {
        const diffOutput = execSync(`git diff --numstat HEAD -- "${filePath}"`, {
          cwd: repo.path,
          encoding: 'utf-8'
        })
        const [addStr, delStr] = diffOutput.trim().split('\t')
        additions = parseInt(addStr, 10) || 0
        deletions = parseInt(delStr, 10) || 0
      } catch {
        // File might be new/untracked
      }

      changes.push({
        path: filePath,
        status,
        additions,
        deletions
      })
    }

    return NextResponse.json({
      success: true,
      changes
    })
  } catch (error: any) {
    console.error('[VSCode Changes] Error:', error)
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    )
  }
}
