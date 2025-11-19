/**
 * PM2 Processes API Routes
 * List and manage PM2 processes
 */

const express = require('express')
const router = express.Router()
const { exec } = require('child_process')
const { promisify } = require('util')

const execAsync = promisify(exec)

/**
 * GET /api/pm2-processes
 * List all PM2 processes
 */
router.get('/', async (req, res) => {
  try {
    // Get PM2 processes list in JSON format
    const { stdout } = await execAsync('pm2 jlist')
    const processes = JSON.parse(stdout || '[]')

    const formattedProcesses = processes.map(proc => ({
      id: String(proc.pm_id || proc.pm2_env?.pm_id || ''),
      name: proc.name || '',
      status: proc.pm2_env?.status || 'unknown',
      uptime: proc.pm2_env?.pm_uptime ? new Date(proc.pm2_env.pm_uptime).toISOString() : '',
      cpu: proc.monit?.cpu || 0,
      memory: proc.monit?.memory || 0,
      restarts: proc.pm2_env?.restart_time || 0,
      pid: proc.pid || null,
      mode: proc.pm2_env?.exec_mode || 'fork',
      instances: proc.pm2_env?.instances || 1,
    }))

    res.json({
      success: true,
      processes: formattedProcesses,
      count: formattedProcesses.length
    })
  } catch (error) {
    // PM2 might not be running or no processes
    if (error.message.includes('daemon not launched') || error.message.includes('No processes')) {
      return res.json({
        success: true,
        processes: [],
        count: 0
      })
    }

    console.error('[API PM2 Processes] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

module.exports = router
