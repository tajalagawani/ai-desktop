import si from 'systeminformation'

export interface SystemStats {
  cpu: {
    usage: number
    cores: number
    model: string
    speed: number
    temperature?: number
    loadPerCore: number[]
  }
  memory: {
    total: number
    used: number
    free: number
    usagePercent: number
    available: number
    active: number
  }
  disk: {
    total: number
    used: number
    free: number
    usagePercent: number
    readSpeed?: number
    writeSpeed?: number
  }
  network?: {
    rx: number  // received bytes
    tx: number  // transmitted bytes
    rxSec: number  // received per second
    txSec: number  // transmitted per second
  }
  processes?: {
    all: number
    running: number
    blocked: number
    sleeping: number
  }
  uptime: number
  platform: string
  hostname: string
}

export async function getSystemStats(): Promise<SystemStats> {
  try {
    // Fetch all stats in parallel for maximum performance
    const [
      cpuLoad,
      cpuInfo,
      mem,
      fsSize,
      currentLoad,
      osInfo,
      networkStats,
      processes,
      cpuTemp
    ] = await Promise.all([
      si.currentLoad(),
      si.cpu(),
      si.mem(),
      si.fsSize(),
      si.currentLoad(),
      si.osInfo(),
      si.networkStats().catch(() => null), // Optional, may fail
      si.processes().catch(() => null),     // Optional, may fail
      si.cpuTemperature().catch(() => null) // Optional, may fail on some systems
    ])

    // CPU stats
    const cpuUsage = Math.round(currentLoad.currentLoad)
    const loadPerCore = currentLoad.cpus.map(cpu => Math.round(cpu.load))

    // Memory stats
    const memUsagePercent = Math.round((mem.used / mem.total) * 100)

    // Disk stats (use root filesystem)
    const rootDisk = fsSize.find(disk => disk.mount === '/') || fsSize[0]
    const diskUsagePercent = Math.round(rootDisk ? rootDisk.use : 0)

    // Network stats (sum of all interfaces)
    let networkData = undefined
    if (networkStats && Array.isArray(networkStats)) {
      const totalRx = networkStats.reduce((sum, iface) => sum + (iface.rx_bytes || 0), 0)
      const totalTx = networkStats.reduce((sum, iface) => sum + (iface.tx_bytes || 0), 0)
      const totalRxSec = networkStats.reduce((sum, iface) => sum + (iface.rx_sec || 0), 0)
      const totalTxSec = networkStats.reduce((sum, iface) => sum + (iface.tx_sec || 0), 0)

      networkData = {
        rx: totalRx,
        tx: totalTx,
        rxSec: totalRxSec,
        txSec: totalTxSec
      }
    }

    // Process stats
    let processData = undefined
    if (processes) {
      processData = {
        all: processes.all || 0,
        running: processes.running || 0,
        blocked: processes.blocked || 0,
        sleeping: processes.sleeping || 0
      }
    }

    const stats: SystemStats = {
      cpu: {
        usage: cpuUsage,
        cores: cpuInfo.cores,
        model: cpuInfo.brand,
        speed: cpuInfo.speed,
        temperature: cpuTemp?.main || undefined,
        loadPerCore
      },
      memory: {
        total: mem.total,
        used: mem.used,
        free: mem.free,
        usagePercent: memUsagePercent,
        available: mem.available,
        active: mem.active
      },
      disk: {
        total: rootDisk?.size || 0,
        used: rootDisk?.used || 0,
        free: rootDisk?.available || 0,
        usagePercent: diskUsagePercent
      },
      network: networkData,
      processes: processData,
      uptime: osInfo.uptime,
      platform: osInfo.platform,
      hostname: osInfo.hostname
    }

    return stats
  } catch (error) {
    console.error('Error fetching system stats:', error)
    throw error
  }
}
 