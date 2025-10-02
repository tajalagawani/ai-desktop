"use server"

import fs from 'fs/promises'
import path from 'path'
import { stat } from 'fs/promises'

// Default to /tmp for safety - it always exists and is world-writable
const SAFE_ROOT = process.env.FILE_MANAGER_ROOT || '/tmp'

// Ensure path is within safe directory
function validatePath(filePath: string): string {
  // If path is just '/', use SAFE_ROOT
  if (filePath === '/' || filePath === '') {
    return SAFE_ROOT
  }

  const normalizedPath = path.normalize(filePath)

  // Strip leading slash if absolute, then join with SAFE_ROOT
  // path.join ignores first arg if second is absolute
  const relativePath = normalizedPath.startsWith('/')
    ? normalizedPath.slice(1)
    : normalizedPath

  const absolutePath = path.join(SAFE_ROOT, relativePath)

  if (!absolutePath.startsWith(SAFE_ROOT)) {
    throw new Error('Access denied: Path is outside allowed directory')
  }

  return absolutePath
}

export interface FileItem {
  id: string
  name: string
  type: 'file' | 'folder'
  size: number
  modified: string
  path: string
}

export async function listFiles(dirPath: string = '/'): Promise<FileItem[]> {
  try {
    const safePath = validatePath(dirPath)

    // Check if directory exists and is accessible
    try {
      const stats = await stat(safePath)
      if (!stats.isDirectory()) {
        throw new Error(`Path is not a directory: ${safePath}`)
      }
    } catch (err: any) {
      console.error('Directory access error:', err)
      throw new Error(`Cannot access directory: ${err.message}`)
    }

    const entries = await fs.readdir(safePath, { withFileTypes: true })

    const items = await Promise.all(
      entries.map(async (entry) => {
        try {
          const fullPath = path.join(safePath, entry.name)
          const stats = await stat(fullPath)

          return {
            id: fullPath,
            name: entry.name,
            type: entry.isDirectory() ? 'folder' as const : 'file' as const,
            size: stats.size,
            modified: stats.mtime.toISOString(),
            path: fullPath.replace(SAFE_ROOT, '') || '/'
          }
        } catch (err) {
          // Skip files we can't access
          return null
        }
      })
    )

    // Filter out null items and sort
    const validItems = items.filter(item => item !== null) as FileItem[]
    return validItems.sort((a, b) => {
      if (a.type !== b.type) return a.type === 'folder' ? -1 : 1
      return a.name.localeCompare(b.name)
    })
  } catch (error: any) {
    console.error('Error listing files:', error)
    throw new Error(`Failed to list files: ${error.message}`)
  }
}

export async function createFolder(dirPath: string, folderName: string): Promise<void> {
  try {
    const safePath = validatePath(path.join(dirPath, folderName))
    await fs.mkdir(safePath, { recursive: true })
  } catch (error: any) {
    console.error('Error creating folder:', error)
    throw new Error(`Failed to create folder: ${error.message}`)
  }
}

export async function deleteItem(itemPath: string): Promise<void> {
  try {
    const safePath = validatePath(itemPath)
    const stats = await stat(safePath)

    if (stats.isDirectory()) {
      await fs.rm(safePath, { recursive: true })
    } else {
      await fs.unlink(safePath)
    }
  } catch (error: any) {
    console.error('Error deleting item:', error)
    throw new Error(`Failed to delete item: ${error.message}`)
  }
}

export async function renameItem(oldPath: string, newName: string): Promise<void> {
  try {
    const safeOldPath = validatePath(oldPath)
    const newPath = path.join(path.dirname(safeOldPath), newName)
    const safeNewPath = validatePath(newPath)

    await fs.rename(safeOldPath, safeNewPath)
  } catch (error: any) {
    console.error('Error renaming item:', error)
    throw new Error(`Failed to rename item: ${error.message}`)
  }
}

export async function readFile(filePath: string): Promise<string> {
  try {
    const safePath = validatePath(filePath)
    const content = await fs.readFile(safePath, 'utf-8')
    return content
  } catch (error: any) {
    console.error('Error reading file:', error)
    throw new Error(`Failed to read file: ${error.message}`)
  }
}

export async function writeFile(filePath: string, content: string): Promise<void> {
  try {
    const safePath = validatePath(filePath)
    await fs.writeFile(safePath, content, 'utf-8')
  } catch (error: any) {
    console.error('Error writing file:', error)
    throw new Error(`Failed to write file: ${error.message}`)
  }
}
