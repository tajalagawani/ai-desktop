/**
 * Files API Routes
 * File manager - browse, create, delete files/folders
 */

const express = require('express')
const router = express.Router()
const fs = require('fs').promises
const path = require('path')

const SAFE_ROOT = process.env.FILE_MANAGER_ROOT || '/var/www'
const SHOW_HIDDEN_DEFAULT = process.env.SHOW_HIDDEN_FILES === 'true'

/**
 * Validate and normalize path
 */
function validatePath(filePath) {
  if (filePath === '/' || filePath === '') {
    return SAFE_ROOT
  }

  const normalizedPath = path.normalize(filePath)

  // If path is absolute and starts with SAFE_ROOT, use it
  if (path.isAbsolute(normalizedPath) && normalizedPath.startsWith(SAFE_ROOT)) {
    return normalizedPath
  }

  // Treat as relative to SAFE_ROOT
  const relativePath = normalizedPath.startsWith('/')
    ? normalizedPath.slice(1)
    : normalizedPath

  const absolutePath = path.join(SAFE_ROOT, relativePath)

  // Security check
  if (!absolutePath.startsWith(SAFE_ROOT)) {
    throw new Error('Access denied: Path is outside allowed directory')
  }

  return absolutePath
}

/**
 * GET /api/files
 * List files in directory
 */
router.get('/', async (req, res) => {
  try {
    const dirPath = req.query.path || '/'
    const showHidden = req.query.showHidden === 'true' || SHOW_HIDDEN_DEFAULT
    const pattern = req.query.pattern // For glob pattern matching (e.g., *.flow)

    const safePath = validatePath(dirPath)

    // Check if directory exists
    const stats = await fs.stat(safePath)
    if (!stats.isDirectory()) {
      return res.status(400).json({
        success: false,
        error: `Path is not a directory: ${dirPath}`
      })
    }

    const entries = await fs.readdir(safePath, { withFileTypes: true })

    const items = await Promise.all(
      entries.map(async (entry) => {
        try {
          // Filter hidden files
          if (!showHidden && entry.name.startsWith('.')) {
            return null
          }

          // Filter by pattern if provided
          if (pattern) {
            const regex = new RegExp(pattern.replace(/\*/g, '.*'))
            if (!regex.test(entry.name)) {
              return null
            }
          }

          const fullPath = path.join(safePath, entry.name)
          const itemStats = await fs.stat(fullPath)

          // Display path relative to SAFE_ROOT
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
      if (a.type !== b.type) return a.type === 'folder' ? -1 : 1
      return a.name.localeCompare(b.name)
    })

    res.json({
      success: true,
      items: sorted,
      files: sorted, // Alias for backwards compatibility
      currentPath: dirPath,
      showHidden
    })
  } catch (error) {
    console.error('[API Files GET] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/files
 * Create folder or delete file/folder
 */
router.post('/', async (req, res) => {
  try {
    const { action, path: itemPath, name } = req.body

    if (action === 'create-folder') {
      if (!itemPath || !name) {
        return res.status(400).json({
          success: false,
          error: 'path and name are required'
        })
      }

      const safePath = validatePath(path.join(itemPath, name))
      await fs.mkdir(safePath, { recursive: true })

      res.json({
        success: true,
        message: 'Folder created',
        path: safePath
      })
    } else if (action === 'delete') {
      if (!itemPath) {
        return res.status(400).json({
          success: false,
          error: 'path is required'
        })
      }

      const safePath = validatePath(itemPath)
      const stats = await fs.stat(safePath)

      if (stats.isDirectory()) {
        await fs.rm(safePath, { recursive: true })
      } else {
        await fs.unlink(safePath)
      }

      res.json({
        success: true,
        message: 'Deleted successfully'
      })
    } else {
      res.status(400).json({
        success: false,
        error: 'Invalid action'
      })
    }
  } catch (error) {
    console.error('[API Files POST] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

module.exports = router
