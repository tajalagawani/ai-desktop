import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs/promises'
import path from 'path'

const SAFE_ROOT = process.env.FILE_MANAGER_ROOT || '/var/www'
const SHOW_HIDDEN_DEFAULT = process.env.SHOW_HIDDEN_FILES === 'true'

function validatePath(filePath: string): string {
  if (filePath === '/' || filePath === '') {
    return SAFE_ROOT
  }

  const normalizedPath = path.normalize(filePath)

  // If the path is already absolute and starts with SAFE_ROOT, use it directly
  if (path.isAbsolute(normalizedPath) && normalizedPath.startsWith(SAFE_ROOT)) {
    return normalizedPath
  }

  // Treat paths as relative to SAFE_ROOT by default
  // Strip leading slash and join with SAFE_ROOT
  const relativePath = normalizedPath.startsWith('/')
    ? normalizedPath.slice(1)
    : normalizedPath

  const absolutePath = path.join(SAFE_ROOT, relativePath)

  // Allow access to paths under SAFE_ROOT
  if (!absolutePath.startsWith(SAFE_ROOT)) {
    throw new Error('Access denied: Path is outside allowed directory')
  }

  return absolutePath
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const dirPath = searchParams.get('path') || '/'
    const showHidden = searchParams.get('showHidden') === 'true' || SHOW_HIDDEN_DEFAULT

    const safePath = validatePath(dirPath)

    // Check if directory exists
    const stats = await fs.stat(safePath)
    if (!stats.isDirectory()) {
      return NextResponse.json(
        { error: `Path is not a directory: ${dirPath}` },
        { status: 400 }
      )
    }

    const entries = await fs.readdir(safePath, { withFileTypes: true })

    const items = await Promise.all(
      entries.map(async (entry) => {
        try {
          // Filter hidden files (starting with .) unless showHidden is true
          if (!showHidden && entry.name.startsWith('.')) {
            return null
          }

          const fullPath = path.join(safePath, entry.name)
          const itemStats = await fs.stat(fullPath)

          // Create path for display - always relative to SAFE_ROOT
          let displayPath = fullPath
          if (fullPath.startsWith(SAFE_ROOT)) {
            displayPath = fullPath.replace(SAFE_ROOT, '')
            if (!displayPath.startsWith('/')) {
              displayPath = '/' + displayPath
            }
          }

          return {
            id: fullPath,
            name: entry.name,
            type: entry.isDirectory() ? 'folder' : 'file',
            size: itemStats.size,
            modified: itemStats.mtime.toISOString(),
            path: displayPath
          }
        } catch {
          return null
        }
      })
    )

    const validItems = items.filter(item => item !== null)
    const sorted = validItems.sort((a, b) => {
      if (a!.type !== b!.type) return a!.type === 'folder' ? -1 : 1
      return a!.name.localeCompare(b!.name)
    })

    return NextResponse.json({
      items: sorted,
      currentPath: dirPath,
      showHidden
    })
  } catch (error: any) {
    console.error('Error listing files:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to list files' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, path: itemPath, name } = body

    if (action === 'create-folder') {
      const safePath = validatePath(path.join(itemPath, name))
      await fs.mkdir(safePath, { recursive: true })
      return NextResponse.json({ success: true })
    }

    if (action === 'delete') {
      const safePath = validatePath(itemPath)
      const stats = await fs.stat(safePath)

      if (stats.isDirectory()) {
        await fs.rm(safePath, { recursive: true })
      } else {
        await fs.unlink(safePath)
      }
      return NextResponse.json({ success: true })
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
  } catch (error: any) {
    console.error('Error in file operation:', error)
    return NextResponse.json(
      { error: error.message || 'File operation failed' },
      { status: 500 }
    )
  }
}
