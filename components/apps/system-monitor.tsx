"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Cpu, MemoryStick as Memory, HardDrive, Activity, Clock, CheckCircle, XCircle, AlertCircle, RefreshCw } from "lucide-react"

interface SystemStats {
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

interface PM2Process {
  id: string
  name: string
  status: 'running' | 'stopped' | 'error' | 'idle'
  uptime: string
  cpu: string
  memory: string
  restarts: number
}

interface LogEntry {
  time: string
  level: 'info' | 'warn' | 'error'
  message: string
}

export function SystemMonitor() {
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [processes, setProcesses] = useState<PM2Process[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch all data in parallel
      const [statsRes, processesRes, logsRes] = await Promise.all([
        fetch('/api/system-stats'),
        fetch('/api/pm2-processes'),
        fetch('/api/system-logs')
      ])

      if (!statsRes.ok) throw new Error('Failed to fetch system stats')

      const statsData = await statsRes.json()
      setStats(statsData)

      // Process PM2 data (don't throw error if it fails)
      if (processesRes.ok) {
        const processesData = await processesRes.json()
        if (processesData.success) {
          setProcesses(processesData.processes)
        }
      }

      // Process logs data (don't throw error if it fails)
      if (logsRes.ok) {
        const logsData = await logsRes.json()
        if (logsData.success) {
          setLogs(logsData.logs)
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Error fetching system stats:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()

    // Auto-refresh every 3 seconds
    const interval = setInterval(fetchStats, 3000)

    return () => clearInterval(interval)
  }, [])

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
  }

  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)

    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else {
      return `${minutes}m`
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running":
        return <Activity className="h-4 w-4 text-yellow-500" />
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "error":
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />
    }
  }

  const getLogIcon = (level: string) => {
    switch (level) {
      case "error":
        return <XCircle className="h-3 w-3 text-red-500" />
      case "warn":
        return <AlertCircle className="h-3 w-3 text-yellow-500" />
      default:
        return <CheckCircle className="h-3 w-3 text-green-500" />
    }
  }

  return (
    <div className="h-full p-6 space-y-6 overflow-auto">
      {/* System Info Header */}
      {stats && (
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h2 className="text-2xl font-bold">System Monitor</h2>
            <p className="text-sm text-muted-foreground">
              {stats.hostname} • {stats.platform} • Uptime: {formatUptime(stats.uptime)}
            </p>
          </div>
          <button
            onClick={fetchStats}
            disabled={loading}
            className="p-2 rounded-lg hover:bg-muted transition-colors"
            title="Refresh stats"
          >
            <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      )}

      {/* Error State */}
      {error && (
        <Card className="p-4 bg-red-500/10 border-red-500/20">
          <div className="flex items-center gap-2 text-red-500">
            <XCircle className="h-5 w-5" />
            <span className="font-medium">Error: {error}</span>
          </div>
        </Card>
      )}

      {/* Loading State */}
      {!stats && loading && (
        <Card className="p-4">
          <div className="flex items-center gap-2 text-muted-foreground">
            <RefreshCw className="h-5 w-5 animate-spin" />
            <span>Loading system stats...</span>
          </div>
        </Card>
      )}

      {/* System Resources */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <Cpu className="h-5 w-5 text-primary" />
              <span className="font-medium">CPU Usage</span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Current</span>
                <span className="font-mono">{stats.cpu.usage}%</span>
              </div>
              <Progress value={stats.cpu.usage} className="h-2" />
              <div className="text-xs text-muted-foreground">
                {stats.cpu.cores} cores • {stats.cpu.model}
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <Memory className="h-5 w-5 text-accent" />
              <span className="font-medium">Memory</span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Used</span>
                <span className="font-mono">
                  {formatBytes(stats.memory.used)} / {formatBytes(stats.memory.total)}
                </span>
              </div>
              <Progress value={stats.memory.usagePercent} className="h-2" />
              <div className="text-xs text-muted-foreground">
                {formatBytes(stats.memory.free)} free
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <HardDrive className="h-5 w-5 text-green-500" />
              <span className="font-medium">Storage</span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Used</span>
                <span className="font-mono">
                  {stats.disk.total > 0
                    ? `${formatBytes(stats.disk.used)} / ${formatBytes(stats.disk.total)}`
                    : 'N/A'
                  }
                </span>
              </div>
              <Progress value={stats.disk.usagePercent} className="h-2" />
              {stats.disk.total > 0 && (
                <div className="text-xs text-muted-foreground">
                  {formatBytes(stats.disk.free)} free
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* PM2 Processes */}
      <Card className="p-4">
        <h3 className="font-semibold mb-4">PM2 Processes</h3>
        <div className="space-y-3">
          {processes.length > 0 ? (
            processes.map((process) => (
              <div key={process.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <div className="flex items-center gap-3">
                  {getStatusIcon(process.status)}
                  <div>
                    <div className="font-medium text-sm">{process.name}</div>
                    <div className="text-xs text-muted-foreground">
                      Uptime: {process.uptime} • CPU: {process.cpu} • RAM: {process.memory} • Restarts: {process.restarts}
                    </div>
                  </div>
                </div>
                <Badge variant={process.status === "running" ? "default" : "secondary"}>{process.status}</Badge>
              </div>
            ))
          ) : (
            <div className="text-sm text-muted-foreground text-center py-4">
              No PM2 processes running
            </div>
          )}
        </div>
      </Card>

      {/* System Logs */}
      <Card className="p-4">
        <h3 className="font-semibold mb-4">System Logs</h3>
        <div className="space-y-2 max-h-64 overflow-auto">
          {logs.map((log, index) => (
            <div key={index} className="flex items-start gap-3 p-2 rounded text-sm font-mono">
              {getLogIcon(log.level)}
              <span className="text-muted-foreground min-w-[60px]">{log.time}</span>
              <span className="flex-1">{log.message}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
