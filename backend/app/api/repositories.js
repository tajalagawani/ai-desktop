/**
 * Repositories API Routes
 * Full CRUD operations for repository management
 * Storage: data/repositories.json
 */

const express = require('express')
const router = express.Router()
const { readJSON, writeJSON, getDataPath } = require('../../lib/json-storage')

const REPOS_FILE = getDataPath('repositories.json')

/**
 * Get all repositories from JSON file
 */
async function getRepositories() {
  const data = await readJSON(REPOS_FILE)
  return data?.repositories || []
}

/**
 * Save repositories to JSON file
 */
async function saveRepositories(repositories) {
  await writeJSON(REPOS_FILE, { repositories })
}

/**
 * GET /api/repositories
 * List all repositories or get specific repository
 */
router.get('/', async (req, res) => {
  try {
    const { id } = req.query
    const repositories = await getRepositories()

    if (id) {
      // Get specific repository
      const repo = repositories.find(r => r.id === parseInt(id))

      if (!repo) {
        return res.status(404).json({
          success: false,
          error: 'Repository not found'
        })
      }

      return res.json({
        success: true,
        repository: repo
      })
    }

    // List all repositories
    res.json({
      success: true,
      repositories
    })
  } catch (error) {
    console.error('[API Repositories GET] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/repositories
 * Add a new repository
 */
router.post('/', async (req, res) => {
  try {
    const { name, path, type, port, url, branch } = req.body

    // Validation
    if (!name || !path || !type || !port) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: name, path, type, port'
      })
    }

    if (!['git', 'local'].includes(type)) {
      return res.status(400).json({
        success: false,
        error: 'Type must be "git" or "local"'
      })
    }

    const repositories = await getRepositories()

    // Check if port is already in use
    const portInUse = repositories.find(r => r.port === port)
    if (portInUse) {
      return res.status(400).json({
        success: false,
        error: `Port ${port} is already in use`
      })
    }

    // Generate new ID
    const newId = repositories.length > 0
      ? Math.max(...repositories.map(r => r.id)) + 1
      : 1

    // Create repository
    const repository = {
      id: newId,
      name,
      path,
      type,
      port,
      url: url || null,
      branch: branch || null,
      running: false,
      pid: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    repositories.push(repository)
    await saveRepositories(repositories)

    res.json({
      success: true,
      repository
    })
  } catch (error) {
    console.error('[API Repositories POST] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * PUT /api/repositories
 * Update a repository
 */
router.put('/', async (req, res) => {
  try {
    const { id, name, path, url, branch } = req.body

    if (!id) {
      return res.status(400).json({
        success: false,
        error: 'Repository ID is required'
      })
    }

    const repositories = await getRepositories()

    // Find repository
    const repoIndex = repositories.findIndex(r => r.id === parseInt(id))
    if (repoIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Repository not found'
      })
    }

    // Update fields
    const repo = repositories[repoIndex]
    if (name !== undefined) repo.name = name
    if (path !== undefined) repo.path = path
    if (url !== undefined) repo.url = url
    if (branch !== undefined) repo.branch = branch
    repo.updated_at = new Date().toISOString()

    repositories[repoIndex] = repo
    await saveRepositories(repositories)

    res.json({
      success: true,
      repository: repo
    })
  } catch (error) {
    console.error('[API Repositories PUT] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * DELETE /api/repositories
 * Delete a repository
 */
router.delete('/', async (req, res) => {
  try {
    const { id } = req.query

    if (!id) {
      return res.status(400).json({
        success: false,
        error: 'Repository ID is required'
      })
    }

    const repositories = await getRepositories()

    // Find repository
    const repo = repositories.find(r => r.id === parseInt(id))
    if (!repo) {
      return res.status(404).json({
        success: false,
        error: 'Repository not found'
      })
    }

    if (repo.running) {
      return res.status(400).json({
        success: false,
        error: 'Cannot delete running repository. Stop it first.'
      })
    }

    // Delete repository
    const filteredRepos = repositories.filter(r => r.id !== parseInt(id))
    await saveRepositories(filteredRepos)

    res.json({
      success: true,
      message: 'Repository deleted'
    })
  } catch (error) {
    console.error('[API Repositories DELETE] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

module.exports = router
