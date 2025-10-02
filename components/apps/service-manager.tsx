"use client"

import React, { useEffect, useState, useCallback, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { SERVICE_CATEGORIES, ServiceConfig } from "@/data/installable-services"
import { getIcon } from "@/utils/icon-mapper"
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
  Copy
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
  const [services, setServices] = useState<ServiceWithStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [dockerInstalled, setDockerInstalled] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedService, setSelectedService] = useState<ServiceWithStatus | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [logs, setLogs] = useState<string>("")
  const [logsLoading, setLogsLoading] = useState(false)

  const loadServices = useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/services')
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to load services')
      }

      setDockerInstalled(data.dockerInstalled)
      setServices(data.services || [])
    } catch (error) {
      console.error('Failed to load services:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadServices()
  }, [loadServices])

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

      await loadServices()

      // Refresh selected service if it's currently selected
      if (selectedService?.id === serviceId) {
        const updatedService = services.find(s => s.id === serviceId)
        if (updatedService) {
          setSelectedService({ ...updatedService })
        }
      }
    } catch (error: any) {
      console.error('Service action error:', error)
      alert(error.message || 'Failed to perform action')
    } finally {
      setActionLoading(null)
    }
  }


  const loadLogs = async (serviceId: string) => {
    setLogsLoading(true)
    try {
      const response = await fetch('/api/services', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'logs', serviceId })
      })
      const data = await response.json()
      if (data.success) {
        setLogs(data.logs)
      }
    } catch (error) {
      console.error('Failed to load logs:', error)
    } finally {
      setLogsLoading(false)
    }
  }

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
    return selectedCategory === 'all'
      ? services
      : services.filter(s => s.category === selectedCategory)
  }, [services, selectedCategory])

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
          <AlertTitle className="text-xl font-bold mb-2">Docker Required</AlertTitle>
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
            <h2 className="text-lg font-semibold mb-2">Service Manager</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Install and manage Docker services on your VPS.
            </p>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-2 gap-2 mb-6">
            <Card className="p-3 border bg-card">
              <div className="text-xl font-bold text-foreground">{stats.total}</div>
              <div className="text-xs text-muted-foreground">Total</div>
            </Card>

            <Card className="p-3 border bg-card">
              <div className="text-xl font-bold text-foreground">{stats.running}</div>
              <div className="text-xs text-muted-foreground">Running</div>
            </Card>

            <Card className="p-3 border bg-card">
              <div className="text-xl font-bold text-foreground">{stats.installed}</div>
              <div className="text-xs text-muted-foreground">Installed</div>
            </Card>

            <Card className="p-3 border bg-card">
              <div className="text-xl font-bold text-foreground">{stats.available}</div>
              <div className="text-xs text-muted-foreground">Available</div>
            </Card>
          </div>

          <div className="flex-1" />

          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={loadServices} className="flex-1 bg-transparent">
              <RotateCw className="h-3 w-3" />
            </Button>
            <Button size="sm" className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90">
              <span>→</span>
            </Button>
          </div>
        </div>

        {/* Right Panel - Dynamic Content */}
        <div className="bg-background p-8 h-full overflow-y-auto">
          {selectedService ? (
            // Service Detail View with Tabs
            <div className="flex flex-col h-full">
              <Button
                variant="ghost"
                size="sm"
                className="mb-4 -ml-2"
                onClick={() => setSelectedService(null)}
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to services
              </Button>

              <div className="mb-4 flex items-start gap-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 shadow-sm">
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
                    <h2 className="text-2xl font-semibold">{selectedService.name}</h2>
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
              </div>

              {/* Tabs for Overview, Config, Logs, Web UI */}
              <Tabs defaultValue="overview" className="flex-1 flex flex-col min-h-0">
                <TabsList className="mb-4">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  {selectedService.installed && <TabsTrigger value="config">Configuration</TabsTrigger>}
                  {selectedService.installed && selectedService.status === 'running' && (
                    <TabsTrigger value="logs" onClick={() => loadLogs(selectedService.id)}>Logs</TabsTrigger>
                  )}
                  {selectedService.installed && getAccessUrl(selectedService) && (
                    <TabsTrigger value="ui">Web UI</TabsTrigger>
                  )}
                </TabsList>

                {/* Overview Tab */}
                <TabsContent value="overview" className="flex-1 overflow-auto space-y-4 mt-0">
                  {selectedService.installed && selectedService.defaultCredentials && (
                    <div className="p-4 bg-muted/50 rounded-lg space-y-2">
                      <h3 className="font-medium text-sm mb-2 flex items-center gap-2">
                        <Key className="h-4 w-4" />
                        Connection Details
                      </h3>
                      {selectedService.defaultCredentials.port && (
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-muted-foreground">Port:</span>
                          <div className="flex items-center gap-2">
                            <code className="font-mono bg-background px-3 py-1 rounded">
                              {selectedService.defaultCredentials.port}
                            </code>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-7 w-7 p-0"
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
                          <div className="flex items-center gap-2">
                            <code className="font-mono bg-background px-3 py-1 rounded">
                              {selectedService.defaultCredentials.username}
                            </code>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-7 w-7 p-0"
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
                          <div className="flex items-center gap-2">
                            <code className="font-mono bg-background px-3 py-1 rounded">
                              {selectedService.defaultCredentials.password}
                            </code>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-7 w-7 p-0"
                              onClick={() => copyToClipboard(selectedService.defaultCredentials!.password!)}
                            >
                              <Copy className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* CLI Connection */}
                  {selectedService.installed && getConnectionString(selectedService) && (
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <h3 className="font-medium text-sm mb-2 flex items-center gap-2">
                        <TerminalIcon className="h-4 w-4" />
                        CLI Connection
                      </h3>
                      <div className="flex items-center gap-2">
                        <code className="flex-1 p-2 bg-background rounded text-sm font-mono overflow-x-auto">
                          {getConnectionString(selectedService)}
                        </code>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(getConnectionString(selectedService)!)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Web Access */}
                  {selectedService.installed && getAccessUrl(selectedService) && (
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <h3 className="font-medium text-sm mb-2 flex items-center gap-2">
                        <Globe className="h-4 w-4" />
                        Web Access
                      </h3>
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={getAccessUrl(selectedService)!}
                          readOnly
                          className="flex-1 p-2 bg-background rounded text-sm"
                        />
                        <Button
                          size="sm"
                          onClick={() => copyToClipboard(getAccessUrl(selectedService)!)}
                        >
                          <Copy className="h-4 w-4 mr-2" />
                          Copy
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => window.open(getAccessUrl(selectedService)!, '_blank')}
                        >
                          <ExternalLink className="h-4 w-4 mr-2" />
                          Open
                        </Button>
                      </div>
                    </div>
                  )}

                  <div>
                    <h3 className="mb-2 font-medium">About</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {selectedService.description}
                    </p>
                  </div>

                  {/* Environment Variables */}
                  {selectedService.environment && Object.keys(selectedService.environment).length > 0 && (
                    <div>
                      <h3 className="mb-3 font-medium">Environment Variables</h3>
                      <div className="space-y-2">
                        {Object.entries(selectedService.environment).map(([key, value]) => (
                          <div key={key} className="flex items-center justify-between p-2 bg-muted/50 rounded text-sm">
                            <code className="font-semibold">{key}</code>
                            <code className="text-muted-foreground">{value}</code>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  {!selectedService.installed ? (
                    <Button
                      size="sm"
                      className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
                      onClick={() => handleServiceAction(selectedService.id, 'install')}
                      disabled={actionLoading === selectedService.id}
                    >
                      <Download className="mr-2 h-3 w-3" />
                      {actionLoading === selectedService.id ? 'Installing...' : 'Install'}
                    </Button>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex gap-2">
                        {selectedService.status === 'running' ? (
                          <Button
                            size="sm"
                            variant="secondary"
                            className="flex-1"
                            onClick={() => handleServiceAction(selectedService.id, 'stop')}
                            disabled={actionLoading === selectedService.id}
                          >
                            <Square className="mr-2 h-3 w-3" />
                            Stop
                          </Button>
                        ) : (
                          <Button
                            size="sm"
                            className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                            onClick={() => handleServiceAction(selectedService.id, 'start')}
                            disabled={actionLoading === selectedService.id}
                          >
                            <Play className="mr-2 h-3 w-3" />
                            Start
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleServiceAction(selectedService.id, 'restart')}
                          disabled={actionLoading === selectedService.id}
                        >
                          <RotateCw className="h-3 w-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleServiceAction(selectedService.id, 'remove')}
                          disabled={actionLoading === selectedService.id}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  )}
                </TabsContent>

                {/* Configuration Tab */}
                {selectedService.installed && (
                  <TabsContent value="config" className="flex-1 overflow-auto space-y-4 mt-0">
                    <Card className="p-4">
                      <h3 className="font-semibold mb-3">Docker Configuration</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between py-2 border-b">
                          <span className="text-muted-foreground">Container Name:</span>
                          <code>{selectedService.containerName}</code>
                        </div>
                        <div className="flex justify-between py-2 border-b">
                          <span className="text-muted-foreground">Image:</span>
                          <code>{selectedService.dockerImage}</code>
                        </div>
                        <div className="flex justify-between py-2 border-b">
                          <span className="text-muted-foreground">Volumes:</span>
                          <code>{selectedService.volumes?.join(', ') || 'None'}</code>
                        </div>
                        <div className="flex justify-between py-2">
                          <span className="text-muted-foreground">Method:</span>
                          <code>{selectedService.installMethod}</code>
                        </div>
                      </div>
                    </Card>
                  </TabsContent>
                )}

                {/* Logs Tab */}
                {selectedService.installed && selectedService.status === 'running' && (
                  <TabsContent value="logs" className="flex-1 overflow-auto mt-0">
                    <Card className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold">Container Logs</h3>
                        <Button size="sm" onClick={() => loadLogs(selectedService.id)} disabled={logsLoading}>
                          <RotateCw className={cn("h-3 w-3 mr-2", logsLoading && "animate-spin")} />
                          Refresh
                        </Button>
                      </div>
                      <pre className="p-4 bg-black text-green-400 rounded font-mono text-xs overflow-auto max-h-96">
                        {logs || 'No logs available. Click Refresh to load logs.'}
                      </pre>
                    </Card>
                  </TabsContent>
                )}

                {/* Web UI Tab */}
                {selectedService.installed && getAccessUrl(selectedService) && (
                  <TabsContent value="ui" className="flex-1 p-0 m-0 h-full">
                    <iframe
                      src={getAccessUrl(selectedService)!}
                      className="w-full h-full border-0 rounded"
                      title={`${selectedService.name} Web UI`}
                    />
                  </TabsContent>
                )}
              </Tabs>
            </div>
          ) : (
            // Services List View
            <div>
              <div className="mb-6">
                <h2 className="mb-2 text-lg font-semibold">Available Services</h2>
                <p className="text-sm text-muted-foreground">
                  Choose from a variety of services to install on your VPS.
                </p>
              </div>

              {/* Category Tabs */}
              <div className="mb-6 flex gap-2 border-b overflow-x-auto">
                <button
                  onClick={() => setSelectedCategory('all')}
                  className={cn(
                    "px-4 py-2 text-sm font-medium whitespace-nowrap transition-colors border-b-2 -mb-px",
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
                      "px-4 py-2 text-sm font-medium whitespace-nowrap transition-colors border-b-2 -mb-px",
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
              <ScrollArea className="h-[calc(100vh-280px)]">
                <div className="space-y-3 pr-4">
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
                            <h3 className="font-medium">{service.name}</h3>
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-1">
                            {service.description}
                          </p>
                        </div>
                        {service.status === 'running' ? (
                          <Badge className="bg-primary text-primary-foreground hover:bg-primary/90 flex-shrink-0">
                            <Check className="mr-1 h-3 w-3" />
                            Running
                          </Badge>
                        ) : service.installed ? (
                          <Badge variant="secondary" className="flex-shrink-0">
                            Stopped
                          </Badge>
                        ) : (
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-shrink-0 bg-transparent"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleServiceAction(service.id, 'install')
                            }}
                            disabled={actionLoading === service.id}
                          >
                            {actionLoading === service.id ? 'Installing...' : 'Install'}
                          </Button>
                        )}
                      </div>
                    )
                  })}
                </div>
              </ScrollArea>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
