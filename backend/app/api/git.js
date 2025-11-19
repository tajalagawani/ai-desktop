/**
 * Git API Routes
 * Execute git commands in repositories
 */

const express = require('express')
const router = express.Router()
const { exec } = require('child_process')
const { promisify } = require('util')
const path = require('path')

const execAsync = promisify(exec)

// Security: Allowed git commands
const ALLOWED_COMMANDS = [
  'status',
  'add',
  'commit',
  'push',
  'pull',
  'fetch',
  'branch',
  'checkout',
  'log',
  'diff',
  'stash',
  'reset',
  'merge',
  'rebase',
  'tag',
  'remote',
  'clone',
  'rev-parse',  // For checking git directory
  'config',     // For git configuration
  'show'        // For showing commits/objects
]

/**
 * POST /api/git
 * Execute git command in repository
 */
router.post('/', async (req, res) => {
  try {
    const { repoPath, command } = req.body

    if (!repoPath || !command) {
      return res.status(400).json({
        success: false,
        error: 'repoPath and command are required'
      })
    }

    // Security: Validate command
    // Command format is "git <subcommand> [args]" or just "<subcommand> [args]"
    const commandParts = command.trim().split(' ')
    let gitCommand = commandParts[0]

    // If command starts with "git", extract the actual git subcommand
    if (gitCommand.toLowerCase() === 'git' && commandParts.length > 1) {
      gitCommand = commandParts[1]
    }

    if (!ALLOWED_COMMANDS.includes(gitCommand)) {
      return res.status(403).json({
        success: false,
        error: `Git command '${gitCommand}' is not allowed`
      })
    }

    // Security: Validate path (must be absolute and not contain ..)
    const normalizedPath = path.normalize(repoPath)
    if (normalizedPath.includes('..') || !path.isAbsolute(normalizedPath)) {
      return res.status(403).json({
        success: false,
        error: 'Invalid repository path'
      })
    }

    // Execute git command
    // If command doesn't start with "git", prepend it
    const fullCommand = command.trim().toLowerCase().startsWith('git ')
      ? command
      : `git ${command}`
    console.log(`[GIT] Executing in ${repoPath}: ${fullCommand}`)

    // For git clone, use parent directory as cwd since target doesn't exist yet
    let workingDir = repoPath
    if (gitCommand === 'clone') {
      workingDir = path.dirname(repoPath)
      // Ensure parent directory exists
      const fs = require('fs').promises
      await fs.mkdir(workingDir, { recursive: true })
    }

    const { stdout, stderr } = await execAsync(fullCommand, {
      cwd: workingDir,
      timeout: 60000, // 1 minute timeout
      maxBuffer: 10 * 1024 * 1024 // 10MB buffer
    })

    res.json({
      success: true,
      stdout: stdout || '',
      stderr: stderr || '',
      command: fullCommand
    })
  } catch (error) {
    console.error('[API Git] Error:', error)

    // Return git error output
    res.status(500).json({
      success: false,
      error: error.message,
      stdout: error.stdout || '',
      stderr: error.stderr || ''
    })
  }
})

module.exports = router
