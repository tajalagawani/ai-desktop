"use client"

import { Card } from "@/components/ui/card"
import { Cpu, MemoryStick as Memory, HardDrive, Network, Activity as ProcessIcon, Clock, MessageSquare } from "lucide-react"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import type { SystemStats } from "@/lib/system-stats"

interface WidgetCardProps {
  icon: React.ComponentType<{ className?: string }>
  title: string
  children: React.ReactNode
  className?: string
}

function WidgetCard({ icon: Icon, title, children, className = "" }: WidgetCardProps) {
  return (
    <Card className={`bg-muted border-border p-4 rounded-2xl ${className}`}>
      <div className="flex items-center gap-2 mb-2">
        <Icon className="h-4 w-4 text-foreground" />
        <span className="text-sm font-normal text-foreground">{title}</span>
      </div>
      <div className="widget-content">
        {children}
      </div>
    </Card>
  )
}

export function WidgetWindow() {
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null)

  // Fetch system stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/system-stats')
        if (response.ok) {
          const data = await response.json()
          setSystemStats(data)
        }
      } catch (error) {
        console.error('Error fetching system stats:', error)
      }
    }

    fetchStats()
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

  const formatBytesPerSec = (bytesPerSec: number): string => {
    return `${formatBytes(bytesPerSec)}/s`
  }

  const recentActivity = [
    { id: 1, action: "Service started", time: "2 min ago" },
    { id: 2, action: "Workflow deployed", time: "5 min ago" },
    { id: 3, action: "File uploaded", time: "10 min ago" }
  ]

  return (
    <div className="h-full w-full bg-muted p-6 overflow-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* CPU Widget */}
        <WidgetCard icon={Cpu} title="CPU">
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-neutral-500 dark:text-neutral-400">Usage</span>
              <span className="text-neutral-700 dark:text-white font-mono">
                {systemStats?.cpu.usage ?? '...'}%
              </span>
            </div>
            {systemStats && (
              <>
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">Cores</span>
                  <span className="text-neutral-700 dark:text-white">{systemStats.cpu.cores}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">Speed</span>
                  <span className="text-neutral-700 dark:text-white">{systemStats.cpu.speed} GHz</span>
                </div>
                {systemStats.cpu.temperature && (
                  <div className="flex justify-between text-xs">
                    <span className="text-neutral-500 dark:text-neutral-400">Temp</span>
                    <span className="text-neutral-700 dark:text-white">{systemStats.cpu.temperature}°C</span>
                  </div>
                )}
              </>
            )}
          </div>
        </WidgetCard>

        {/* Memory Widget */}
        <WidgetCard icon={Memory} title="Memory">
          <div className="space-y-2 text-sm">
            {systemStats ? (
              <>
                <div className="flex justify-between">
                  <span className="text-neutral-500 dark:text-neutral-400">Usage</span>
                  <span className="text-neutral-700 dark:text-white font-mono">
                    {systemStats.memory.usagePercent}%
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">Used</span>
                  <span className="text-neutral-700 dark:text-white font-mono">
                    {formatBytes(systemStats.memory.used)}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">Total</span>
                  <span className="text-neutral-700 dark:text-white font-mono">
                    {formatBytes(systemStats.memory.total)}
                  </span>
                </div>
              </>
            ) : (
              <div className="text-xs text-neutral-500 dark:text-neutral-400">Loading...</div>
            )}
          </div>
        </WidgetCard>

        {/* Storage Widget */}
        <WidgetCard icon={HardDrive} title="Storage">
          <div className="space-y-2 text-sm">
            {systemStats && systemStats.disk.total > 0 ? (
              <>
                <div className="flex justify-between">
                  <span className="text-neutral-500 dark:text-neutral-400">Usage</span>
                  <span className="text-neutral-700 dark:text-white font-mono">
                    {systemStats.disk.usagePercent}%
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">Used</span>
                  <span className="text-neutral-700 dark:text-white font-mono">
                    {formatBytes(systemStats.disk.used)}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">Total</span>
                  <span className="text-neutral-700 dark:text-white font-mono">
                    {formatBytes(systemStats.disk.total)}
                  </span>
                </div>
              </>
            ) : (
              <div className="text-xs text-neutral-500 dark:text-neutral-400">Loading...</div>
            )}
          </div>
        </WidgetCard>

        {/* Network Widget */}
        <WidgetCard icon={Network} title="Network">
          <div className="space-y-2 text-sm">
            {systemStats?.network ? (
              <>
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">↓ Down</span>
                  <span className="text-neutral-700 dark:text-white font-mono">
                    {formatBytesPerSec(systemStats.network.rxSec)}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">↑ Up</span>
                  <span className="text-neutral-700 dark:text-white font-mono">
                    {formatBytesPerSec(systemStats.network.txSec)}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">Total RX</span>
                  <span className="text-neutral-700 dark:text-white font-mono">
                    {formatBytes(systemStats.network.rx)}
                  </span>
                </div>
              </>
            ) : (
              <div className="text-xs text-neutral-500 dark:text-neutral-400">Loading...</div>
            )}
          </div>
        </WidgetCard>

        {/* Processes Widget */}
        <WidgetCard icon={ProcessIcon} title="Processes">
          <div className="space-y-2 text-sm">
            {systemStats?.processes ? (
              <>
                <div className="flex justify-between">
                  <span className="text-neutral-500 dark:text-neutral-400">Total</span>
                  <span className="text-neutral-700 dark:text-white font-mono">
                    {systemStats.processes.all}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">Running</span>
                  <span className="text-neutral-700 dark:text-white">{systemStats.processes.running}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">Sleeping</span>
                  <span className="text-neutral-700 dark:text-white">{systemStats.processes.sleeping}</span>
                </div>
              </>
            ) : (
              <div className="text-xs text-neutral-500 dark:text-neutral-400">Loading...</div>
            )}
          </div>
        </WidgetCard>

        {/* Recent Activity Widget */}
        <WidgetCard icon={Clock} title="Recent Activity">
          <div className="space-y-2 text-xs">
            {recentActivity.slice(0, 3).map((activity) => (
              <div key={activity.id} className="text-neutral-500 dark:text-neutral-400">
                {activity.action} - {activity.time}
              </div>
            ))}
          </div>
        </WidgetCard>

        {/* AI Assistant Widget */}
        <WidgetCard icon={MessageSquare} title="AI Assistant">
          <div className="text-xs text-neutral-500 dark:text-neutral-400 mb-2">
            Ready to assist with workflow automation
          </div>
          <Button
            size="sm"
            variant="outline"
            className="w-full text-xs bg-white dark:bg-neutral-800 border-gray-200 dark:border-neutral-700 text-neutral-700 dark:text-white hover:bg-gray-100 dark:hover:bg-neutral-700"
            onClick={() => window.dispatchEvent(new CustomEvent('trigger-dock-chat'))}
          >
            Chat with AI
          </Button>
        </WidgetCard>
      </div>
    </div>
  )
}
