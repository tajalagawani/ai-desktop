/**
 * System Stats API Routes
 * Get system statistics (CPU, RAM, Disk)
 */

const express = require('express')
const router = express.Router()
const os = require('os')
const { exec } = require('child_process')
const { promisify } = require('util')

const execAsync = promisify(exec)

/**
 * Get disk usage
 */
async function getDiskUsage() {
  try {
    const { stdout } = await execAsync('df -h /')
    const lines = stdout.trim().split('\n')
    if (lines.length >= 2) {
      const parts = lines[1].split(/\s+/)
      return {
        total: parts[1] || '0',
        used: parts[2] || '0',
        available: parts[3] || '0',
        percentage: parseInt(parts[4]) || 0
      }
    }
  } catch (error) {
    console.error('Error getting disk usage:', error)
  }

  return {
    total: '0',
    used: '0',
    available: '0',
    percentage: 0
  }
}

/**
 * Get CPU usage
 */
function getCPUUsage() {
  const cpus = os.cpus()
  let totalIdle = 0
  let totalTick = 0

  cpus.forEach(cpu => {
    for (let type in cpu.times) {
      totalTick += cpu.times[type]
    }
    totalIdle += cpu.times.idle
  })

  const idle = totalIdle / cpus.length
  const total = totalTick / cpus.length
  const usage = 100 - ~~(100 * idle / total)

  return {
    usage,
    cores: cpus.length,
    model: cpus[0]?.model || 'Unknown'
  }
}

/**
 * Get memory usage
 */
function getMemoryUsage() {
  const total = os.totalmem()
  const free = os.freemem()
  const used = total - free
  const percentage = (used / total) * 100

  return {
    total: (total / 1024 / 1024 / 1024).toFixed(2) + ' GB',
    used: (used / 1024 / 1024 / 1024).toFixed(2) + ' GB',
    free: (free / 1024 / 1024 / 1024).toFixed(2) + ' GB',
    percentage: percentage.toFixed(1)
  }
}

/**
 * Get system uptime
 */
function getUptime() {
  const uptimeSeconds = os.uptime()
  const days = Math.floor(uptimeSeconds / 86400)
  const hours = Math.floor((uptimeSeconds % 86400) / 3600)
  const minutes = Math.floor((uptimeSeconds % 3600) / 60)

  return {
    seconds: uptimeSeconds,
    formatted: `${days}d ${hours}h ${minutes}m`
  }
}

/**
 * GET /api/system-stats
 * Get all system statistics
 */
router.get('/', async (req, res) => {
  try {
    const [disk, cpu, memory, uptime] = await Promise.all([
      getDiskUsage(),
      Promise.resolve(getCPUUsage()),
      Promise.resolve(getMemoryUsage()),
      Promise.resolve(getUptime())
    ])

    const stats = {
      success: true,
      timestamp: new Date().toISOString(),
      system: {
        platform: os.platform(),
        arch: os.arch(),
        hostname: os.hostname(),
        uptime
      },
      cpu,
      memory,
      disk,
      loadAverage: os.loadavg()
    }

    res.json(stats)
  } catch (error) {
    console.error('[API System Stats] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

module.exports = router
