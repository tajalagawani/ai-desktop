"use client"

import { useEffect, useRef, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RotateCw, X } from "lucide-react"
import { cn } from "@/lib/utils"

interface DeploymentLogsProps {
  deploymentId: string
  type: 'build' | 'runtime'
  onClose?: () => void
}

export function DeploymentLogs({ deploymentId, type, onClose }: DeploymentLogsProps) {
  const [logs, setLogs] = useState<string>("")
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    connectWebSocket()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [deploymentId, type])

  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/deployments/logs/ws?deploymentId=${deploymentId}&type=${type}`

    console.log('[Deployment Logs] Connecting to:', wsUrl)

    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('[Deployment Logs] WebSocket connected')
      setConnected(true)
      setError(null)
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)

        if (message.type === 'log') {
          setLogs(prev => prev + message.data)
          scrollToBottom()
        } else if (message.type === 'error') {
          setError(message.message)
        } else if (message.type === 'info') {
          setLogs(prev => prev + `[INFO] ${message.message}\n`)
        } else if (message.type === 'connected') {
          console.log('[Deployment Logs] Connected:', message.message)
        }
      } catch (error) {
        console.error('[Deployment Logs] Error parsing message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('[Deployment Logs] WebSocket error:', error)
      setError('WebSocket connection error')
      setConnected(false)
    }

    ws.onclose = () => {
      console.log('[Deployment Logs] WebSocket closed')
      setConnected(false)
    }
  }

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleReconnect = () => {
    if (wsRef.current) {
      wsRef.current.close()
    }
    setLogs("")
    setError(null)
    connectWebSocket()
  }

  return (
    <Card className="flex flex-col h-full min-h-0">
      <div className="flex items-center justify-between p-3 border-b flex-shrink-0">
        <div className="flex items-center gap-2">
          <h3 className="font-medium text-sm">
            {type === 'build' ? 'Build Logs' : 'Runtime Logs'}
          </h3>
          <div className={cn(
            "h-2 w-2 rounded-full",
            connected ? "bg-green-500" : "bg-red-500"
          )} />
        </div>
        <div className="flex items-center gap-1">
          <Button size="sm" variant="ghost" onClick={handleReconnect} className="h-7 px-2">
            <RotateCw className={cn("h-3 w-3", !connected && "animate-spin")} />
          </Button>
          {onClose && (
            <Button size="sm" variant="ghost" onClick={onClose} className="h-7 px-2">
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>

      <div className="flex-1 min-h-0 bg-black overflow-hidden">
        <pre className="h-full w-full px-3 pt-3 pb-1 text-green-400 font-mono text-xs overflow-y-auto overflow-x-hidden whitespace-pre-wrap break-words scrollbar-thin">
          {logs || (connected ? 'Waiting for logs...' : 'Connecting...')}
          {error && <div className="text-red-400">[ERROR] {error}</div>}
          <div ref={logsEndRef} />
        </pre>
      </div>
    </Card>
  )
}
