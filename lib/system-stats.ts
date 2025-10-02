import os from 'os'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export interface SystemStats {
  cpu: {
    usage: number
    cores: number
    model: string
  }
  memory: {
    total: number
    used: number
    free: number
    usagePercent: number
  }
  disk: {
    total: number
    used: number
    free: number
    usagePercent: number
  }
  uptime: number
  platform: string
  hostname: string
}

// Calculate CPU usage
async function getCPUUsage(): Promise<number> {
  const cpus = os.cpus()

  // Get CPU usage at two points in time
  const startMeasure = cpus.map(cpu => {
    const total = Object.values(cpu.times).reduce((acc, time) => acc + time, 0)
    const idle = cpu.times.idle
    return { total, idle }
  })

  // Wait 100ms
  await new Promise(resolve => setTimeout(resolve, 100))

  const endMeasure = os.cpus().map(cpu => {
    const total = Object.values(cpu.times).reduce((acc, time) => acc + time, 0)
    const idle = cpu.times.idle
    return { total, idle }
  })

  // Calculate average CPU usage across all cores
  let totalUsage = 0
  for (let i = 0; i < startMeasure.length; i++) {
    const totalDiff = endMeasure[i].total - startMeasure[i].total
    const idleDiff = endMeasure[i].idle - startMeasure[i].idle
    const usage = 100 - (100 * idleDiff / totalDiff)
    totalUsage += usage
  }

  const avgUsage = totalUsage / startMeasure.length
  return Math.min(Math.round(avgUsage), 100)
}

// Get disk usage (works on Linux/Unix)
async function getDiskUsage(): Promise<{ total: number; used: number; free: number; usagePercent: number }> {
  try {
    // Try df command (Linux/Unix)
    const { stdout } = await execAsync('df -k /')
    const lines = stdout.trim().split('\n')

    if (lines.length >= 2) {
      const parts = lines[1].split(/\s+/)
      const total = parseInt(parts[1]) * 1024 // Convert KB to bytes
      const used = parseInt(parts[2]) * 1024
      const free = parseInt(parts[3]) * 1024
      const usagePercent = Math.round((used / total) * 100)

      return { total, used, free, usagePercent }
    }
  } catch (error) {
    console.error('Error getting disk usage:', error)
  }

  // Fallback if df command fails
  return { total: 0, used: 0, free: 0, usagePercent: 0 }
}

export async function getSystemStats(): Promise<SystemStats> {
  // Get CPU info
  const cpuUsage = await getCPUUsage()
  const cpus = os.cpus()
  const cpuModel = cpus[0]?.model || 'Unknown'

  // Get memory info
  const totalMem = os.totalmem()
  const freeMem = os.freemem()
  const usedMem = totalMem - freeMem
  const memUsagePercent = Math.round((usedMem / totalMem) * 100)

  // Get disk info
  const diskInfo = await getDiskUsage()

  // Get system info
  const uptime = os.uptime()
  const platform = os.platform()
  const hostname = os.hostname()

  return {
    cpu: {
      usage: cpuUsage,
      cores: cpus.length,
      model: cpuModel
    },
    memory: {
      total: totalMem,
      used: usedMem,
      free: freeMem,
      usagePercent: memUsagePercent
    },
    disk: {
      total: diskInfo.total,
      used: diskInfo.used,
      free: diskInfo.free,
      usagePercent: diskInfo.usagePercent
    },
    uptime,
    platform,
    hostname
  }
}
