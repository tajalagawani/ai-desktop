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

export function SystemMonitor() {
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const workflows = [
    { id: "1", name: "PR → Slack Notification", status: "running", lastRun: "2 min ago" },
    { id: "2", name: "Daily Report Generator", status: "success", lastRun: "1 hour ago" },
    { id: "3", name: "Error Alert System", status: "idle", lastRun: "3 hours ago" },
  ]

  const logs = [
    { time: "14:32:15", level: "info", message: "Slack node executed successfully" },
    { time: "14:31:45", level: "info", message: "GitHub webhook received" },
    { time: "14:30:22", level: "warn", message: "OpenAI rate limit approaching" },
    { time: "14:28:10", level: "error", message: "Database connection timeout" },
    { time: "14:25:33", level: "info", message: 'Workflow "PR → Slack" started' },
  ]

  const fetchStats = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('/api/system-stats')
      if (!response.ok) {
        throw new Error('Failed to fetch system stats')
      }
      const data = await response.json()
      setStats(data)
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
      {/* System Resources */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Cpu className="h-5 w-5 text-primary" />
            <span className="font-medium">CPU Usage</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Current</span>
              <span className="font-mono">23%</span>
            </div>
            <Progress value={23} className="h-2" />
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
              <span className="font-mono">1.2GB / 4GB</span>
            </div>
            <Progress value={30} className="h-2" />
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
              <span className="font-mono">45GB / 100GB</span>
            </div>
            <Progress value={45} className="h-2" />
          </div>
        </Card>
      </div>

      {/* Active Workflows */}
      <Card className="p-4">
        <h3 className="font-semibold mb-4">Active Workflows</h3>
        <div className="space-y-3">
          {workflows.map((workflow) => (
            <div key={workflow.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <div className="flex items-center gap-3">
                {getStatusIcon(workflow.status)}
                <div>
                  <div className="font-medium text-sm">{workflow.name}</div>
                  <div className="text-xs text-muted-foreground">Last run: {workflow.lastRun}</div>
                </div>
              </div>
              <Badge variant={workflow.status === "running" ? "default" : "secondary"}>{workflow.status}</Badge>
            </div>
          ))}
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
