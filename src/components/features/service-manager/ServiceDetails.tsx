"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Check,
  Square,
  Play,
  Trash2,
  RotateCw,
  Key,
  TerminalIcon,
  Globe,
  Copy,
  ExternalLink,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { getIcon } from "@/lib/utils/icon-mapper"
import { SERVICE_CATEGORIES } from "@/data/installable-services"

interface ServiceDetailsProps {
  serviceId: string
}

export function ServiceDetails({ serviceId }: ServiceDetailsProps) {
  const [service, setService] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [logs, setLogs] = useState<string>("")
  const [logsLoading, setLogsLoading] = useState(false)
  const [logsWs, setLogsWs] = useState<WebSocket | null>(null)
  const logsConnectedRef = React.useRef<string | null>(null)

  // Fetch service details
  useEffect(() => {
    const fetchService = async () => {
      try {
        const response = await fetch('/api/services')
        if (response.ok) {
          const data = await response.json()
          const foundService = data.services?.find((s: any) => s.id === serviceId)
          setService(foundService || null)
        }
      } catch (error) {
        console.error('Error fetching service:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchService()
    const interval = setInterval(fetchService, 2000)
    return () => {
      clearInterval(interval)
      // Cleanup WebSocket on unmount
      if (logsWs) {
        logsWs.close()
      }
    }
  }, [serviceId])

  // WebSocket for logs
  const connectLogsWebSocket = (containerName: string) => {
    if (logsWs) {
      logsWs.close()
    }

    setLogsLoading(true)
    setLogs("")

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/services/logs/ws?container=${containerName}`

    console.log('[Service Details] Connecting to logs:', wsUrl)

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setLogsLoading(false)
    }

    ws.onmessage = (event) => {
      setLogs((prev) => prev + event.data)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setLogsLoading(false)
      setLogs((prev) => prev + '\n[Error: Failed to connect to log stream. Service may not be running or logs API is unavailable.]')
    }

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
      setLogsLoading(false)
      if (event.code !== 1000 && event.code !== 1001) {
        // Abnormal closure
        setLogs((prev) => prev + '\n[Connection closed. Click Reconnect to retry.]')
      }
    }

    setLogsWs(ws)
  }

  // Auto-connect logs when service is running - only connect once per container
  useEffect(() => {
    if (service?.status === 'running' && service?.containerName) {
      // Only connect if not already connected to this container
      if (logsConnectedRef.current !== service.containerName) {
        // Close previous connection if exists
        if (logsWs) {
          logsWs.close()
        }
        connectLogsWebSocket(service.containerName)
        logsConnectedRef.current = service.containerName
      }
    } else if (service?.status !== 'running' && logsWs) {
      // Close logs if service stopped
      logsWs.close()
      setLogsWs(null)
      logsConnectedRef.current = null
      setLogs('')
    }
  }, [service?.status, service?.containerName])

  const handleServiceAction = async (action: string) => {
    setActionLoading(true)
    try {
      await fetch('/api/services', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, serviceId: service.id })
      })
    } catch (error) {
      console.error('Error performing action:', error)
    } finally {
      setActionLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const getAccessUrl = () => {
    const port = service?.ports?.[0]
    if (!port) return null
    return `http://${window.location.hostname}:${port}`
  }

  const getConnectionString = () => {
    if (!service?.defaultCredentials) return null
    const { username, password, port } = service.defaultCredentials

    if (service.id.includes('mysql')) {
      return `mysql -h ${window.location.hostname} -P ${port} -u ${username || 'root'} -p${password || ''}`
    } else if (service.id.includes('postgres')) {
      return `psql -h ${window.location.hostname} -p ${port} -U ${username || 'postgres'}`
    } else if (service.id.includes('mongo')) {
      return `mongo ${window.location.hostname}:${port}`
    } else if (service.id.includes('redis')) {
      return `redis-cli -h ${window.location.hostname} -p ${port}`
    }
    return null
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <RotateCw className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!service) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">Service not found</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full p-6 overflow-hidden">
      {/* Header */}
      <div className="mb-4 flex items-start gap-4 flex-shrink-0">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 shadow-sm flex-shrink-0">
          {service.iconType === 'image' ? (
            <img src={service.icon} alt={service.name} className="h-10 w-10 object-contain" />
          ) : (
            (() => {
              const Icon = getIcon(service.icon)
              return <Icon className="h-8 w-8 text-primary" />
            })()
          )}
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-2xl font-normal">{service.name}</h2>
            {service.status === 'running' ? (
              <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                <Check className="mr-1 h-3 w-3" />
                Running
              </Badge>
            ) : service.installed ? (
              <Badge variant="secondary">Stopped</Badge>
            ) : null}
          </div>
          <p className="text-sm text-muted-foreground">
            {SERVICE_CATEGORIES.find(c => c.id === service.category)?.name || service.category}
          </p>
        </div>

        {/* Action Buttons */}
        {service.installed && (
          <div className="flex gap-2 items-center flex-shrink-0">
            {service.status === 'running' ? (
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleServiceAction('stop')}
                disabled={actionLoading}
              >
                {actionLoading ? (
                  <RotateCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Square className="h-3.5 w-3.5" />
                )}
              </Button>
            ) : (
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleServiceAction('start')}
                disabled={actionLoading}
              >
                {actionLoading ? (
                  <RotateCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Play className="h-3.5 w-3.5" />
                )}
              </Button>
            )}
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleServiceAction('restart')}
              disabled={actionLoading}
            >
              <RotateCw className={cn("h-3.5 w-3.5", actionLoading && "animate-spin")} />
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleServiceAction('remove')}
              disabled={actionLoading}
            >
              {actionLoading ? (
                <RotateCw className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Trash2 className="h-3.5 w-3.5" />
              )}
            </Button>
          </div>
        )}
      </div>

      {/* Connection Details */}
      <div className="space-y-3 flex-shrink-0 mb-4">
        {service.installed && (
          <div className="p-3 bg-muted/50 rounded-lg space-y-2.5">
            {service.defaultCredentials && (
              <>
                <h3 className="font-normal text-sm flex items-center gap-2">
                  <Key className="h-3.5 w-3.5" />
                  Connection Details
                </h3>
                <div className="space-y-1.5">
                  {service.defaultCredentials.port && (
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Port:</span>
                      <div className="flex items-center gap-1.5">
                        <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                          {service.defaultCredentials.port}
                        </code>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0"
                          onClick={() => copyToClipboard(service.defaultCredentials.port.toString())}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  )}
                  {service.defaultCredentials.username && (
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Username:</span>
                      <div className="flex items-center gap-1.5">
                        <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                          {service.defaultCredentials.username}
                        </code>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0"
                          onClick={() => copyToClipboard(service.defaultCredentials.username)}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  )}
                  {service.defaultCredentials.password && (
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Password:</span>
                      <div className="flex items-center gap-1.5">
                        <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                          {service.defaultCredentials.password}
                        </code>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0"
                          onClick={() => copyToClipboard(service.defaultCredentials.password)}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}

            {getConnectionString() && (
              <>
                <div className="border-t pt-2.5" />
                <h3 className="font-normal text-sm flex items-center gap-2">
                  <TerminalIcon className="h-3.5 w-3.5" />
                  CLI Connection
                </h3>
                <div className="flex items-center gap-1.5">
                  <code className="flex-1 px-2 py-1 bg-background rounded text-xs font-mono overflow-x-auto">
                    {getConnectionString()}
                  </code>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-6 w-6 p-0"
                    onClick={() => copyToClipboard(getConnectionString()!)}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </>
            )}

            {getAccessUrl() && (
              <>
                <div className="border-t pt-2.5" />
                <h3 className="font-normal text-sm flex items-center gap-2">
                  <Globe className="h-3.5 w-3.5" />
                  Web Access
                </h3>
                <div className="flex items-center gap-1.5">
                  <input
                    type="text"
                    value={getAccessUrl()!}
                    readOnly
                    className="flex-1 px-2 py-1 bg-background rounded text-xs"
                  />
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-6 w-6 p-0"
                    onClick={() => copyToClipboard(getAccessUrl()!)}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-6 w-6 p-0"
                    onClick={() => window.open(getAccessUrl()!, '_blank')}
                  >
                    <ExternalLink className="h-3 w-3" />
                  </Button>
                </div>
              </>
            )}
          </div>
        )}

        {service.environment && Object.keys(service.environment).length > 0 && (
          <div className="p-3 bg-muted/50 rounded-lg">
            <h3 className="mb-2 font-normal text-sm">Environment Variables</h3>
            <div className="space-y-1">
              {Object.entries(service.environment).map(([key, value]: [string, any]) => (
                <div key={key} className="flex items-center justify-between py-1 text-sm">
                  <code className="font-normal text-xs">{key}</code>
                  <code className="text-muted-foreground text-xs">{value}</code>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      {service.installed && (
        <Tabs defaultValue="logs" className="flex-1 flex flex-col min-h-0">
          <TabsList className="mb-2 justify-start w-auto flex-shrink-0">
            {service.status === 'running' && (
              <TabsTrigger value="logs">Logs</TabsTrigger>
            )}
            <TabsTrigger value="config">Configuration</TabsTrigger>
          </TabsList>

          {/* Configuration Tab */}
          <TabsContent value="config" className="flex-1 overflow-auto mt-0 min-h-0">
            <Card className="p-3">
              <h3 className="font-normal mb-2 text-sm">Docker Configuration</h3>
              <div className="space-y-1.5 text-sm">
                <div className="flex justify-between py-1.5 border-b">
                  <span className="text-muted-foreground">Container Name:</span>
                  <code className="text-xs">{service.containerName}</code>
                </div>
                <div className="flex justify-between py-1.5 border-b">
                  <span className="text-muted-foreground">Image:</span>
                  <code className="text-xs">{service.dockerImage}</code>
                </div>
                <div className="flex justify-between py-1.5 border-b">
                  <span className="text-muted-foreground">Volumes:</span>
                  <code className="text-xs">{service.volumes?.join(', ') || 'None'}</code>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-muted-foreground">Method:</span>
                  <code className="text-xs">{service.installMethod}</code>
                </div>
              </div>
            </Card>
          </TabsContent>

          {/* Logs Tab */}
          <TabsContent value="logs" className="flex-1 flex flex-col mt-0 min-h-0">
            <Card className="p-3 flex-1 flex flex-col min-h-0 overflow-hidden">
              <div className="flex items-center justify-between mb-2 flex-shrink-0">
                <h3 className="font-normal text-sm">Container Logs (Live Stream)</h3>
                <Button
                  size="sm"
                  onClick={() => connectLogsWebSocket(service.containerName)}
                  disabled={logsLoading}
                >
                  <RotateCw className={cn("h-3 w-3 mr-1.5", logsLoading && "animate-spin")} />
                  Reconnect
                </Button>
              </div>
              <div className="flex-1 min-h-0 bg-black rounded overflow-hidden">
                <pre className="h-full w-full p-3 text-green-400 font-mono text-xs overflow-y-scroll overflow-x-hidden whitespace-pre-wrap break-words scrollbar-thin will-change-scroll">
                  {logs || 'Connecting to log stream...'}
                </pre>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
