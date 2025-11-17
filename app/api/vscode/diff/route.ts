import { NextRequest, NextResponse } from 'next/server'
import { execSync } from 'child_process'
import { RepositoryManager } from '@/lib/repositories/registry'

export async function POST(request: NextRequest) {
  try {
    const { repoId, filePath } = await request.json()

    const repoManager = new RepositoryManager()
    const repo = repoManager.getRepository(repoId)

    if (!repo) {
      return NextResponse.json(
        { success: false, error: 'Repository not found' },
        { status: 404 }
      )
    }

    // Get diff for the file
    const diffOutput = execSync(`git diff HEAD -- "${filePath}"`, {
      cwd: repo.path,
      encoding: 'utf-8'
    })

    return NextResponse.json({
      success: true,
      diff: diffOutput
    })
  } catch (error: any) {
    console.error('[VSCode Diff] Error:', error)
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    )
  }
}
