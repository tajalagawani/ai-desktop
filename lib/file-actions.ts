"use server"

import fs from 'fs/promises'
import path from 'path'
import { stat } from 'fs/promises'

const SAFE_ROOT = process.env.FILE_MANAGER_ROOT || '/home'

// Ensure path is within safe directory
function validatePath(filePath: string): string {
  const normalizedPath = path.normalize(filePath)
  const absolutePath = path.isAbsolute(normalizedPath)
    ? normalizedPath
    : path.join(SAFE_ROOT, normalizedPath)

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
    const entries = await fs.readdir(safePath, { withFileTypes: true })

    const items = await Promise.all(
      entries.map(async (entry) => {
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
      })
    )

    // Sort: folders first, then files, alphabetically
    return items.sort((a, b) => {
      if (a.type !== b.type) return a.type === 'folder' ? -1 : 1
      return a.name.localeCompare(b.name)
    })
  } catch (error) {
    console.error('Error listing files:', error)
    throw new Error('Failed to list files')
  }
}

export async function createFolder(dirPath: string, folderName: string): Promise<void> {
  try {
    const safePath = validatePath(path.join(dirPath, folderName))
    await fs.mkdir(safePath, { recursive: true })
  } catch (error) {
    console.error('Error creating folder:', error)
    throw new Error('Failed to create folder')
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
  } catch (error) {
    console.error('Error deleting item:', error)
    throw new Error('Failed to delete item')
  }
}

export async function renameItem(oldPath: string, newName: string): Promise<void> {
  try {
    const safeOldPath = validatePath(oldPath)
    const newPath = path.join(path.dirname(safeOldPath), newName)
    const safeNewPath = validatePath(newPath)

    await fs.rename(safeOldPath, safeNewPath)
  } catch (error) {
    console.error('Error renaming item:', error)
    throw new Error('Failed to rename item')
  }
}

export async function readFile(filePath: string): Promise<string> {
  try {
    const safePath = validatePath(filePath)
    const content = await fs.readFile(safePath, 'utf-8')
    return content
  } catch (error) {
    console.error('Error reading file:', error)
    throw new Error('Failed to read file')
  }
}

export async function writeFile(filePath: string, content: string): Promise<void> {
  try {
    const safePath = validatePath(filePath)
    await fs.writeFile(safePath, content, 'utf-8')
  } catch (error) {
    console.error('Error writing file:', error)
    throw new Error('Failed to write file')
  }
}
