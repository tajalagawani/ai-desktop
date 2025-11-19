"use client"

import React, { useEffect, useState, useCallback, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { SERVICE_CATEGORIES, ServiceConfig } from "@/data/installable-services"
import { useServicesSync } from "@/lib/hooks/features/use-services-sync"
import { getIcon } from "@/lib/utils/icon-mapper"
import {
  Play,
  Square,
  RotateCw,
  Trash2,
  Download,
  ArrowLeft,
  AlertCircle,
  Check,
  ExternalLink,
  Terminal as TerminalIcon,
  Key,
  Globe,
  Copy,
  Search
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface ServiceWithStatus extends ServiceConfig {
  installed: boolean
  status: string
  containerName: string
}

interface ServiceManagerProps {
  // Props are available for future use
}

// Main Component
export function ServiceManager(_props: ServiceManagerProps) {
  // Use real-time services sync
  const { services: syncedServices, dockerInstalled, loading: servicesLoading, connected } = useServicesSync()
  const [services, setServices] = useState<ServiceWithStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedService, setSelectedService] = useState<ServiceWithStatus | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [logs, setLogs] = useState<string>("")
  const [logsLoading, setLogsLoading] = useState(false)
  const [logsWs, setLogsWs] = useState<WebSocket | null>(null)
  const [searchQuery, setSearchQuery] = useState<string>("")

  // Update services when synced data changes
  useEffect(() => {
    setServices(syncedServices as ServiceWithStatus[])
    setLoading(servicesLoading)
  }, [syncedServices, servicesLoading])

  // Log connection status
  useEffect(() => {
    console.log('[ServiceManager] WebSocket:', connected ? 'Connected ✅' : 'Disconnected ❌')
  }, [connected])

  const handleServiceAction = async (serviceId: string, action: string) => {
    setActionLoading(serviceId)
    try {
      const response = await fetch('/api/services', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, serviceId })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Service action failed')
      }

      // WebSocket will automatically update services in real-time
      // Just clear the loading state after a brief delay
      setTimeout(() => {
        setActionLoading(null)
      }, 500)
    } catch (error: any) {
      console.error('Service action error:', error)
      alert(error.message || 'Failed to perform action')
      setActionLoading(null)
    }
  }


  const connectLogsWebSocket = useCallback((containerName: string) => {
    // Close existing connection
    if (logsWs) {
      logsWs.close()
    }

    setLogsLoading(true)
    setLogs('')

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/api/services/logs/ws?container=${containerName}`

      console.log('[Logs] Connecting to:', wsUrl)

      const ws = new WebSocket(wsUrl)
      setLogsWs(ws)

      ws.onopen = () => {
        console.log('[Logs] WebSocket connected')
        setLogsLoading(false)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)

          if (message.type === 'log') {
            setLogs(prev => prev + message.data)
          } else if (message.type === 'error') {
            console.error('[Logs] Error:', message.message)
            setLogs(prev => prev + `\n[ERROR] ${message.message}\n`)
          } else if (message.type === 'connected') {
            console.log('[Logs] Connected:', message.message)
          }
        } catch (error) {
          console.error('[Logs] Error parsing message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('[Logs] WebSocket error:', error)
        setLogsLoading(false)
      }

      ws.onclose = () => {
        console.log('[Logs] WebSocket closed')
        setLogsLoading(false)
      }
    } catch (error) {
      console.error('[Logs] Failed to connect:', error)
      setLogsLoading(false)
    }
  }, [logsWs])

  // Auto-connect logs WebSocket when a running service is selected
  useEffect(() => {
    if (selectedService && selectedService.installed && selectedService.status === 'running') {
      connectLogsWebSocket(selectedService.containerName)
    } else {
      // Close WebSocket if service is not running
      if (logsWs) {
        logsWs.close()
        setLogsWs(null)
      }
      setLogs('')
    }

    // Cleanup on unmount or service change
    return () => {
      if (logsWs) {
        logsWs.close()
        setLogsWs(null)
      }
    }
  }, [selectedService])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const getAccessUrl = (service: ServiceWithStatus) => {
    const port = service.ports?.[0]
    if (!port) return null
    if (typeof window !== 'undefined') {
      return `http://${window.location.hostname}:${port}`
    }
    return null
  }

  const getConnectionString = (service: ServiceWithStatus) => {
    const { id, defaultCredentials } = service
    const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
    const port = defaultCredentials?.port || service.ports?.[0]
    const user = defaultCredentials?.username || 'root'
    const pass = defaultCredentials?.password || 'changeme'

    switch (id) {
      case 'mysql':
      case 'mysql57':
      case 'mariadb':
        return `mysql -h ${host} -P ${port} -u ${user} -p${pass}`
      case 'postgresql':
        return `psql -h ${host} -p ${port} -U ${user} -d postgres`
      case 'mongodb':
        return `mongodb://${host}:${port}`
      case 'redis':
      case 'keydb':
        return `redis-cli -h ${host} -p ${port}`
      case 'neo4j':
        return `bolt://${host}:7687`
      default:
        return null
    }
  }

  // Filtered services
  const filteredServices = useMemo(() => {
    let filtered = selectedCategory === 'all'
      ? services
      : services.filter(s => s.category === selectedCategory)

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(query) ||
        s.description.toLowerCase().includes(query) ||
        s.id.toLowerCase().includes(query)
      )
    }

    return filtered
  }, [services, selectedCategory, searchQuery])

  // Statistics
  const stats = useMemo(() => {
    return {
      total: services.length,
      installed: services.filter(s => s.installed).length,
      running: services.filter(s => s.status === 'running').length,
      available: services.filter(s => !s.installed).length,
    }
  }, [services])

  if (loading) {
    return (
      <div className="h-full bg-background">
        <div className="grid h-full grid-cols-[320px_1fr]">
          {/* Left side skeleton */}
          <div className="border-r p-6 flex flex-col">
            <Skeleton className="h-8 w-48 mb-6" />
            <div className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
            <div className="flex-1" />
            <div className="flex flex-col gap-3">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          </div>
          {/* Right side skeleton */}
          <div className="p-8">
            <Skeleton className="h-8 w-48 mb-6" />
            <div className="space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="flex items-center gap-4 p-4">
                  <Skeleton className="h-12 w-12 rounded-xl" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-48" />
                  </div>
                  <Skeleton className="h-9 w-24" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!dockerInstalled) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <Alert className="max-w-2xl">
          <AlertCircle className="h-5 w-5" />
          <AlertTitle className="text-xl font-normal mb-2">Docker Required</AlertTitle>
          <AlertDescription className="space-y-4">
            <p>
              Docker is required to install and manage services. Please install Docker on your VPS first.
            </p>
            <Button asChild className="w-full sm:w-auto bg-primary text-primary-foreground hover:bg-primary/90">
              <a href="https://docs.docker.com/engine/install/" target="_blank" rel="noopener noreferrer">
                <Download className="mr-2 h-4 w-4" />
                Install Docker
              </a>
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="h-full bg-background">
      <div className="grid h-full grid-cols-[320px_1fr]">
        {/* Left Panel - Static Info */}
        <div className="relative overflow-hidden border-r bg-background p-6 h-full flex flex-col">
          <div className="mb-6">
            <h2 className="text-lg font-normal mb-2">Service Manager</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Install and manage Docker services on your VPS.
            </p>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-2 gap-2 mb-6">
            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.total}</div>
              <div className="text-xs text-muted-foreground">Total</div>
            </Card>

            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.running}</div>
              <div className="text-xs text-muted-foreground">Running</div>
            </Card>

            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.installed}</div>
              <div className="text-xs text-muted-foreground">Installed</div>
            </Card>

            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.available}</div>
              <div className="text-xs text-muted-foreground">Available</div>
            </Card>
          </div>

          <div className="flex-1" />

          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 px-3 py-2 bg-muted/50 rounded-lg">
              <div className={cn(
                "w-2 h-2 rounded-full",
                connected ? "bg-green-500 animate-pulse" : "bg-red-500"
              )} />
              <span className="text-xs text-muted-foreground">
                {connected ? 'Live' : 'Offline'}
              </span>
            </div>
          </div>
        </div>

        {/* Right Panel - Dynamic Content */}
        <div className="bg-background p-8 h-full overflow-hidden flex flex-col">
          {selectedService ? (
            // Service Detail View with Tabs
            <div className="flex flex-col flex-1 min-h-0">
              <Button
                variant="ghost"
                size="sm"
                className="mb-4 -ml-2 w-fit"
                onClick={() => setSelectedService(null)}
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to services
              </Button>

              <div className="mb-4 flex items-start gap-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 shadow-sm flex-shrink-0">
                  {selectedService.iconType === 'image' ? (
                    <img src={selectedService.icon} alt={selectedService.name} className="h-10 w-10 object-contain" />
                  ) : (
                    (() => {
                      const Icon = getIcon(selectedService.icon)
                      return <Icon className="h-8 w-8 text-primary" />
                    })()
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h2 className="text-2xl font-normal">{selectedService.name}</h2>
                    {selectedService.status === 'running' ? (
                      <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                        <Check className="mr-1 h-3 w-3" />
                        Running
                      </Badge>
                    ) : selectedService.installed ? (
                      <Badge variant="secondary">Stopped</Badge>
                    ) : null}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {SERVICE_CATEGORIES.find(c => c.id === selectedService.category)?.name || selectedService.category}
                  </p>
                </div>

                {/* Action Buttons - Right side of header */}
                {selectedService.installed && (
                  <div className="flex gap-2 items-center flex-shrink-0">
                    {selectedService.status === 'running' ? (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleServiceAction(selectedService.id, 'stop')}
                        disabled={actionLoading === selectedService.id}
                        title="Stop service"
                      >
                        {actionLoading === selectedService.id ? (
                          <RotateCw className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                          <Square className="h-3.5 w-3.5" />
                        )}
                      </Button>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleServiceAction(selectedService.id, 'start')}
                        disabled={actionLoading === selectedService.id}
                        title="Start service"
                      >
                        {actionLoading === selectedService.id ? (
                          <RotateCw className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                          <Play className="h-3.5 w-3.5" />
                        )}
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleServiceAction(selectedService.id, 'restart')}
                      disabled={actionLoading === selectedService.id}
                      title="Restart service"
                    >
                      <RotateCw className={cn("h-3.5 w-3.5", actionLoading === selectedService.id && "animate-spin")} />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleServiceAction(selectedService.id, 'remove')}
                      disabled={actionLoading === selectedService.id}
                      title="Delete service"
                    >
                      {actionLoading === selectedService.id ? (
                        <RotateCw className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Trash2 className="h-3.5 w-3.5" />
                      )}
                    </Button>
                  </div>
                )}
              </div>

              {/* Overview Content - Always Visible */}
              <div className="space-y-3 flex-shrink-0">
                  {/* Unified Connection Info Card */}
                  {selectedService.installed && (
                    <div className="p-3 bg-muted/50 rounded-lg space-y-2.5">
                      {selectedService.defaultCredentials && (
                        <>
                          <h3 className="font-normal text-sm flex items-center gap-2">
                            <Key className="h-3.5 w-3.5" />
                            Connection Details
                          </h3>
                          <div className="space-y-1.5">
                            {selectedService.defaultCredentials.port && (
                              <div className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">Port:</span>
                                <div className="flex items-center gap-1.5">
                                  <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                                    {selectedService.defaultCredentials.port}
                                  </code>
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    className="h-6 w-6 p-0"
                                    onClick={() => copyToClipboard(selectedService.defaultCredentials!.port!.toString())}
                                  >
                                    <Copy className="h-3 w-3" />
                                  </Button>
                                </div>
                              </div>
                            )}
                            {selectedService.defaultCredentials.username && (
                              <div className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">Username:</span>
                                <div className="flex items-center gap-1.5">
                                  <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                                    {selectedService.defaultCredentials.username}
                                  </code>
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    className="h-6 w-6 p-0"
                                    onClick={() => copyToClipboard(selectedService.defaultCredentials!.username!)}
                                  >
                                    <Copy className="h-3 w-3" />
                                  </Button>
                                </div>
                              </div>
                            )}
                            {selectedService.defaultCredentials.password && (
                              <div className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">Password:</span>
                                <div className="flex items-center gap-1.5">
                                  <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                                    {selectedService.defaultCredentials.password}
                                  </code>
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    className="h-6 w-6 p-0"
                                    onClick={() => copyToClipboard(selectedService.defaultCredentials!.password!)}
                                  >
                                    <Copy className="h-3 w-3" />
                                  </Button>
                                </div>
                              </div>
                            )}
                          </div>
                        </>
                      )}

                      {/* CLI Connection */}
                      {getConnectionString(selectedService) && (
                        <>
                          <div className="border-t pt-2.5" />
                          <h3 className="font-normal text-sm flex items-center gap-2">
                            <TerminalIcon className="h-3.5 w-3.5" />
                            CLI Connection
                          </h3>
                          <div className="flex items-center gap-1.5">
                            <code className="flex-1 px-2 py-1 bg-background rounded text-xs font-mono overflow-x-auto">
                              {getConnectionString(selectedService)}
                            </code>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-6 w-6 p-0"
                              onClick={() => copyToClipboard(getConnectionString(selectedService)!)}
                            >
                              <Copy className="h-3 w-3" />
                            </Button>
                          </div>
                        </>
                      )}

                      {/* Web Access */}
                      {getAccessUrl(selectedService) && (
                        <>
                          <div className="border-t pt-2.5" />
                          <h3 className="font-normal text-sm flex items-center gap-2">
                            <Globe className="h-3.5 w-3.5" />
                            Web Access
                          </h3>
                          <div className="flex items-center gap-1.5">
                            <input
                              type="text"
                              value={getAccessUrl(selectedService)!}
                              readOnly
                              className="flex-1 px-2 py-1 bg-background rounded text-xs"
                            />
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-6 w-6 p-0"
                              onClick={() => copyToClipboard(getAccessUrl(selectedService)!)}
                            >
                              <Copy className="h-3 w-3" />
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-6 w-6 p-0"
                              onClick={() => window.open(getAccessUrl(selectedService)!, '_blank')}
                            >
                              <ExternalLink className="h-3 w-3" />
                            </Button>
                          </div>
                        </>
                      )}
                    </div>
                  )}

                  {/* Environment Variables */}
                  {selectedService.environment && Object.keys(selectedService.environment).length > 0 && (
                    <div className="p-3 bg-muted/50 rounded-lg">
                      <h3 className="mb-2 font-normal text-sm">Environment Variables</h3>
                      <div className="space-y-1">
                        {Object.entries(selectedService.environment).map(([key, value]) => (
                          <div key={key} className="flex items-center justify-between py-1 text-sm">
                            <code className="font-normal text-xs">{key}</code>
                            <code className="text-muted-foreground text-xs">{value}</code>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Tabs for Config, Logs, Web UI */}
                {selectedService.installed && (
                  <Tabs defaultValue="logs" className="flex-1 flex flex-col mt-2 min-h-0">
                    <TabsList className="mb-2 justify-start w-auto flex-shrink-0">
                      {selectedService.status === 'running' && (
                        <TabsTrigger value="logs">
                          Logs
                        </TabsTrigger>
                      )}
                      <TabsTrigger value="config">Configuration</TabsTrigger>
                      {getAccessUrl(selectedService) && (
                        <TabsTrigger value="ui">Web UI</TabsTrigger>
                      )}
                    </TabsList>

                    {/* Configuration Tab */}
                    <TabsContent value="config" className="flex-1 overflow-auto mt-0 min-h-0">
                      <Card className="p-3">
                        <h3 className="font-normal mb-2 text-sm">Docker Configuration</h3>
                        <div className="space-y-1.5 text-sm">
                          <div className="flex justify-between py-1.5 border-b">
                            <span className="text-muted-foreground">Container Name:</span>
                            <code className="text-xs">{selectedService.containerName}</code>
                          </div>
                          <div className="flex justify-between py-1.5 border-b">
                            <span className="text-muted-foreground">Image:</span>
                            <code className="text-xs">{selectedService.dockerImage}</code>
                          </div>
                          <div className="flex justify-between py-1.5 border-b">
                            <span className="text-muted-foreground">Volumes:</span>
                            <code className="text-xs">{selectedService.volumes?.join(', ') || 'None'}</code>
                          </div>
                          <div className="flex justify-between py-1.5">
                            <span className="text-muted-foreground">Method:</span>
                            <code className="text-xs">{selectedService.installMethod}</code>
                          </div>
                        </div>
                      </Card>
                    </TabsContent>

                    {/* Logs Tab */}
                    <TabsContent value="logs" className="flex-1 flex flex-col mt-0 min-h-0">
                      <Card className="p-3 flex-1 flex flex-col min-h-0 overflow-hidden">
                        <div className="flex items-center justify-between mb-2 flex-shrink-0">
                          <h3 className="font-normal text-sm">Container Logs (Live Stream)</h3>
                          <Button size="sm" onClick={() => connectLogsWebSocket(selectedService.containerName)} disabled={logsLoading}>
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

                    {/* Web UI Tab */}
                    <TabsContent value="ui" className="flex-1 p-0 m-0 h-full">
                      <iframe
                        src={getAccessUrl(selectedService)!}
                        className="w-full h-full border-0 rounded"
                        title={`${selectedService.name} Web UI`}
                      />
                    </TabsContent>
                  </Tabs>
                )}
            </div>
          ) : (
            // Services List View
            <div className="flex flex-col flex-1 min-h-0">
              <div className="mb-6 flex items-start justify-between gap-4 flex-shrink-0">
                <div className="flex-1">
                  <h2 className="mb-2 text-lg font-normal">Available Services</h2>
                  <p className="text-sm text-muted-foreground">
                    Choose from a variety of services to install on your VPS.
                  </p>
                </div>
                <div className="relative w-80">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search services..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full h-9 pl-9 pr-3 rounded-md border border-input bg-background text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  />
                </div>
              </div>

              {/* Category Tabs */}
              <div className="mb-6 flex gap-2 border-b overflow-x-auto flex-shrink-0">
                <button
                  onClick={() => setSelectedCategory('all')}
                  className={cn(
                    "px-4 py-2 text-sm font-normal whitespace-nowrap transition-colors border-b-2 -mb-px",
                    selectedCategory === 'all'
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  )}
                >
                  View all
                </button>
                {SERVICE_CATEGORIES.map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id)}
                    className={cn(
                      "px-4 py-2 text-sm font-normal whitespace-nowrap transition-colors border-b-2 -mb-px",
                      selectedCategory === cat.id
                        ? "border-primary text-primary"
                        : "border-transparent text-muted-foreground hover:text-foreground"
                    )}
                  >
                    {cat.name}
                  </button>
                ))}
              </div>

              {/* Services List */}
              <div className="flex-1 min-h-0 overflow-y-scroll overflow-x-hidden pr-4 scrollbar-thin will-change-scroll">
                <div className="space-y-3">
                  {filteredServices.map((service) => {
                    const Icon = service.iconType === 'image' ? null : getIcon(service.icon)
                    return (
                      <div
                        key={service.id}
                        onClick={() => setSelectedService(service)}
                        className="flex items-center gap-4 p-4 rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                      >
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 flex-shrink-0">
                          {service.iconType === 'image' ? (
                            <img src={service.icon} alt={service.name} className="h-8 w-8 object-contain" />
                          ) : Icon && (
                            <Icon className="w-6 h-6 text-primary" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h3 className="font-normal">{service.name}</h3>
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-1">
                            {service.description}
                          </p>
                        </div>

                        {/* Status Badge & Action Buttons */}
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {service.installed ? (
                            <>
                              {service.status === 'running' ? (
                                <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                                  <Check className="mr-1 h-3 w-3" />
                                  Running
                                </Badge>
                              ) : (
                                <Badge variant="secondary">Stopped</Badge>
                              )}
                              {service.status === 'running' ? (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleServiceAction(service.id, 'stop')
                                  }}
                                  disabled={actionLoading === service.id}
                                  title="Stop service"
                                >
                                  {actionLoading === service.id ? (
                                    <RotateCw className="h-3.5 w-3.5 animate-spin" />
                                  ) : (
                                    <Square className="h-3.5 w-3.5" />
                                  )}
                                </Button>
                              ) : (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleServiceAction(service.id, 'start')
                                  }}
                                  disabled={actionLoading === service.id}
                                  title="Start service"
                                >
                                  {actionLoading === service.id ? (
                                    <RotateCw className="h-3.5 w-3.5 animate-spin" />
                                  ) : (
                                    <Play className="h-3.5 w-3.5" />
                                  )}
                                </Button>
                              )}
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleServiceAction(service.id, 'remove')
                                }}
                                disabled={actionLoading === service.id}
                                title="Delete service"
                              >
                                {actionLoading === service.id ? (
                                  <RotateCw className="h-3.5 w-3.5 animate-spin" />
                                ) : (
                                  <Trash2 className="h-3.5 w-3.5" />
                                )}
                              </Button>
                            </>
                          ) : (
                            <Button
                              size="sm"
                              variant="outline"
                              className="bg-transparent"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleServiceAction(service.id, 'install')
                              }}
                              disabled={actionLoading === service.id}
                            >
                              {actionLoading === service.id ? (
                                <>
                                  <RotateCw className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                                  Installing...
                                </>
                              ) : (
                                'Install'
                              )}
                            </Button>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
