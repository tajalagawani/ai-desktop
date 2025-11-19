/**
 * Git Config API Routes
 * Manage global git configuration
 */

const express = require('express')
const router = express.Router()
const { exec } = require('child_process')
const { promisify } = require('util')

const execAsync = promisify(exec)

/**
 * POST /api/git-config
 * Set global git configuration
 */
router.post('/', async (req, res) => {
  try {
    const { userName, userEmail } = req.body

    if (!userName || !userEmail) {
      return res.status(400).json({
        success: false,
        error: 'userName and userEmail are required'
      })
    }

    // Set global git config
    await execAsync(`git config --global user.name "${userName}"`)
    await execAsync(`git config --global user.email "${userEmail}"`)

    console.log(`[GIT CONFIG] Set user: ${userName} <${userEmail}>`)

    res.json({
      success: true,
      message: 'Git config updated',
      userName,
      userEmail
    })
  } catch (error) {
    console.error('[API Git Config] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * GET /api/git-config
 * Get current git configuration
 */
router.get('/', async (req, res) => {
  try {
    const { stdout: userName } = await execAsync('git config --global user.name').catch(() => ({ stdout: '' }))
    const { stdout: userEmail } = await execAsync('git config --global user.email').catch(() => ({ stdout: '' }))

    res.json({
      success: true,
      userName: userName.trim(),
      userEmail: userEmail.trim()
    })
  } catch (error) {
    console.error('[API Git Config GET] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

module.exports = router
