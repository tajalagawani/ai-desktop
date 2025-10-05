"use client"

import React, { useEffect, useState, useCallback, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { getIcon } from "@/utils/icon-mapper"
import {
  Play,
  Square,
  RotateCw,
  Trash2,
  ArrowLeft,
  AlertCircle,
  Check,
  ExternalLink,
  Terminal as TerminalIcon,
  Globe,
  Copy,
  Search,
  Zap,
  Network,
  Circle
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface FlowConfig {
  name: string
  port: number
  mode: "agent" | "miniact" | "waiting"
  agent_name?: string
  description?: string
  file: string
  auto_assigned?: boolean
  container?: {
    running: boolean
    status: string
    started_at?: string
    pid?: number
  }
  health?: {
    status: string
    port?: number
  }
}

interface FlowManagerProps {
  // Props are available for future use
}

interface RouteInfo {
  path: string
  method: string
  node?: string
  description?: string
}

// ACI Routes Tab Component
function ACIRoutesTab({ flow }: { flow: FlowConfig }) {
  const [routes, setRoutes] = useState<RouteInfo[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchRoutes = async () => {
      setLoading(true)
      try {
        const response = await fetch(`http://localhost:${flow.port}/api/routes`)
        if (response.ok) {
          const data = await response.json()

          // Parse the routes object format
          if (data.routes && typeof data.routes === 'object') {
            const parsedRoutes: RouteInfo[] = Object.entries(data.routes).map(([key, value]: [string, any]) => {
              // Parse "METHOD /path" format
              const [method, ...pathParts] = key.split(' ')
              const path = pathParts.join(' ')

              return {
                path: path || key,
                method: method || 'GET',
                node: value.aci_node_id || value.handler_name,
                description: value.description
              }
            })
            setRoutes(parsedRoutes)
          } else if (Array.isArray(data)) {
            setRoutes(data)
          }
        }
      } catch (error) {
        console.error('Failed to fetch routes:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchRoutes()
  }, [flow.port])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const getMethodColor = (method: string) => {
    switch (method.toUpperCase()) {
      case 'GET':
        return 'bg-blue-600 text-white'
      case 'POST':
        return 'bg-green-600 text-white'
      case 'PUT':
        return 'bg-yellow-600 text-white'
      case 'DELETE':
        return 'bg-red-600 text-white'
      case 'PATCH':
        return 'bg-purple-600 text-white'
      default:
        return 'bg-gray-600 text-white'
    }
  }

  return (
    <TabsContent value="aci" className="flex-1 overflow-auto mt-0 min-h-0">
      <Card className="p-3">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-normal text-sm">ACI Routes</h3>
          <Badge variant="outline" className="text-xs">
            {routes.length} {routes.length === 1 ? 'route' : 'routes'}
          </Badge>
        </div>

        {loading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        ) : routes.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground text-sm">
            No ACI routes found for this flow
          </div>
        ) : (
          <div className="space-y-2">
            {routes.map((route, index) => (
              <div
                key={index}
                className="p-3 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <Badge className={cn("text-xs font-mono", getMethodColor(route.method))}>
                    {route.method}
                  </Badge>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <code className="text-sm font-mono">
                        {route.path}
                      </code>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-6 w-6 p-0"
                        onClick={() => copyToClipboard(`http://localhost:${flow.port}${route.path}`)}
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-6 w-6 p-0"
                        onClick={() => window.open(`http://localhost:${flow.port}${route.path}`, '_blank')}
                      >
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                    </div>
                    {route.node && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Node: {route.node}
                      </p>
                    )}
                    {route.description && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {route.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </TabsContent>
  )
}

// Main Component
export function FlowManager(_props: FlowManagerProps) {
  const [flows, setFlows] = useState<FlowConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [actInstalled, setActInstalled] = useState(false)
  const [selectedFlow, setSelectedFlow] = useState<FlowConfig | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [logs, setLogs] = useState<string>("")
  const [logsLoading, setLogsLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState<string>("")

  const loadFlows = useCallback(async (silent = false) => {
    if (!silent) {
      setLoading(true)
    }
    try {
      const response = await fetch('/api/flows')
      const data = await response.json()

      // Check if ACT/Docker is installed
      if (data.actInstalled === false) {
        setActInstalled(false)
        setFlows([])
        if (!silent) {
          setLoading(false)
        }
        return
      }

      if (!response.ok) {
        throw new Error(data.error || 'Failed to load flows')
      }

      setActInstalled(true)

      // Normalize health status - some flows return "ready", some return "healthy"
      const normalizedFlows = (data.flows || []).map((flow: FlowConfig) => {
        if (flow.health?.status === 'ready') {
          return {
            ...flow,
            health: { ...flow.health, status: 'healthy' }
          }
        }
        return flow
      })

      setFlows(normalizedFlows)
    } catch (error) {
      console.error('Failed to load flows:', error)
      // Don't change actInstalled state on network errors, just clear flows
      setFlows([])
    } finally {
      if (!silent) {
        setLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    loadFlows(false)
    // Silent background refresh
    const interval = setInterval(() => {
      if (!actionLoading) {
        loadFlows(true) // Silent refresh to avoid flashing
      }
    }, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [loadFlows, actionLoading])

  const handleFlowAction = async (flowName: string, action: string) => {
    setActionLoading(flowName)
    try {
      const response = await fetch('/api/flows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, flowName })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Flow action failed')
      }

      await loadFlows()

      // Refresh selected flow if it's currently selected
      if (selectedFlow?.name === flowName) {
        const updatedFlow = flows.find(f => f.name === flowName)
        if (updatedFlow) {
          setSelectedFlow({ ...updatedFlow })
        }
      }
    } catch (error: any) {
      console.error('Flow action error:', error)
      alert(error.message || 'Failed to perform action')
    } finally {
      setActionLoading(null)
    }
  }

  const loadLogs = useCallback(async (flowName: string, silent = false) => {
    if (!silent) {
      setLogsLoading(true)
    }
    try {
      const response = await fetch(`/api/flows?flowName=${flowName}&action=logs&lines=100`)
      const data = await response.json()

      if (response.ok && data.logs) {
        setLogs(data.logs)
      }
    } catch (error) {
      console.error('Failed to load logs:', error)
    } finally {
      if (!silent) {
        setLogsLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    if (selectedFlow && selectedFlow.container?.running) {
      loadLogs(selectedFlow.name, false)
      // Silent background refresh for logs
      const interval = setInterval(() => {
        loadLogs(selectedFlow.name, true) // Silent refresh
      }, 5000)
      return () => clearInterval(interval)
    } else {
      setLogs('')
    }
  }, [selectedFlow, loadLogs])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const getAccessUrl = (flow: FlowConfig) => {
    if (typeof window !== 'undefined') {
      return `http://${window.location.hostname}:${flow.port}`
    }
    return null
  }

  // Filtered flows
  const filteredFlows = useMemo(() => {
    if (!searchQuery.trim()) return flows

    const query = searchQuery.toLowerCase()
    return flows.filter(f =>
      f.name.toLowerCase().includes(query) ||
      f.agent_name?.toLowerCase().includes(query) ||
      f.mode.toLowerCase().includes(query) ||
      f.file.toLowerCase().includes(query)
    )
  }, [flows, searchQuery])

  // Statistics
  const stats = useMemo(() => {
    return {
      total: flows.length,
      running: flows.filter(f => f.container?.running).length,
      healthy: flows.filter(f => f.health?.status === 'healthy').length,
      stopped: flows.filter(f => !f.container?.running).length,
    }
  }, [flows])

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

  if (!actInstalled) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <Alert className="max-w-2xl">
          <AlertCircle className="h-5 w-5" />
          <AlertTitle className="text-xl font-normal mb-2">ACT Docker Required</AlertTitle>
          <AlertDescription className="space-y-4">
            <p>
              ACT Docker is required to run workflow automation flows. The setup is already in components/apps/act-docker.
            </p>
            <p className="text-sm text-muted-foreground">
              Please ensure the flow manager API is running and accessible.
            </p>
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
            <h2 className="text-lg font-normal mb-2">Flow Manager</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Manage ACT workflow automation flows running in Docker containers.
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
              <div className="text-xl font-normal text-foreground">{stats.healthy}</div>
              <div className="text-xs text-muted-foreground">Healthy</div>
            </Card>

            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.stopped}</div>
              <div className="text-xs text-muted-foreground">Stopped</div>
            </Card>
          </div>

          <div className="flex-1" />

          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={loadFlows} className="flex-1 bg-transparent">
              <RotateCw className="h-3 w-3" />
            </Button>
            <Button size="sm" className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90">
              <span>→</span>
            </Button>
          </div>
        </div>

        {/* Right Panel - Dynamic Content */}
        <div className="bg-background p-8 h-full overflow-hidden flex flex-col">
          {selectedFlow ? (
            // Flow Detail View with Tabs
            <div className="flex flex-col flex-1 min-h-0">
              <Button
                variant="ghost"
                size="sm"
                className="mb-4 -ml-2 w-fit"
                onClick={() => setSelectedFlow(null)}
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to flows
              </Button>

              <div className="mb-4 flex items-start gap-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 shadow-sm flex-shrink-0">
                  {selectedFlow.mode === 'agent' ? (
                    <Network className="h-8 w-8 text-primary" />
                  ) : (
                    <Zap className="h-8 w-8 text-primary" />
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h2 className="text-2xl font-normal">{selectedFlow.agent_name || selectedFlow.name}</h2>
                    {selectedFlow.container?.running ? (
                      selectedFlow.health?.status === 'healthy' ? (
                        <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                          <Circle className="mr-1 h-2 w-2 fill-green-500 text-green-500" />
                          Running
                        </Badge>
                      ) : (
                        <Badge variant="secondary">
                          <Circle className="mr-1 h-2 w-2 fill-red-500 text-red-500" />
                          Unhealthy
                        </Badge>
                      )
                    ) : (
                      <Badge variant="secondary">
                        <Circle className="mr-1 h-2 w-2 fill-gray-400 text-gray-400" />
                        Stopped
                      </Badge>
                    )}
                  </div>
                  {selectedFlow.description && (
                    <p className="text-base text-muted-foreground mb-2 max-w-2xl">
                      {selectedFlow.description}
                    </p>
                  )}
                  <p className="text-sm text-muted-foreground">
                    {selectedFlow.mode === 'agent' ? 'Agent Mode' : selectedFlow.mode === 'miniact' ? 'MiniACT Mode' : 'Waiting'}
                    {' • '}
                    Port {selectedFlow.port}
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 items-center flex-shrink-0">
                  {selectedFlow.container?.running ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleFlowAction(selectedFlow.name, 'stop')}
                      disabled={actionLoading === selectedFlow.name}
                      title="Stop flow"
                    >
                      <Square className="h-3.5 w-3.5" />
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleFlowAction(selectedFlow.name, 'start')}
                      disabled={actionLoading === selectedFlow.name}
                      title="Start flow"
                    >
                      <Play className="h-3.5 w-3.5" />
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleFlowAction(selectedFlow.name, 'restart')}
                    disabled={actionLoading === selectedFlow.name}
                    title="Restart flow"
                  >
                    <RotateCw className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>

              {/* Overview Content */}
              <div className="space-y-3 flex-shrink-0">
                {/* Connection Info Card */}
                <div className="p-3 bg-muted/50 rounded-lg space-y-2.5">
                  <h3 className="font-normal text-sm flex items-center gap-2">
                    <Globe className="h-3.5 w-3.5" />
                    Access Details
                  </h3>
                  <div className="space-y-1.5">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Port:</span>
                      <div className="flex items-center gap-1.5">
                        <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                          {selectedFlow.port}
                        </code>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0"
                          onClick={() => copyToClipboard(selectedFlow.port.toString())}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Mode:</span>
                      <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                        {selectedFlow.mode}
                      </code>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">File:</span>
                      <code className="font-mono bg-background px-2 py-0.5 rounded text-xs">
                        {selectedFlow.file}
                      </code>
                    </div>
                  </div>

                  {/* Web Access */}
                  {selectedFlow.container?.running && (
                    <>
                      <div className="border-t pt-2.5" />
                      <h3 className="font-normal text-sm flex items-center gap-2">
                        <TerminalIcon className="h-3.5 w-3.5" />
                        API Endpoints
                      </h3>
                      <div className="flex items-center gap-1.5">
                        <input
                          type="text"
                          value={getAccessUrl(selectedFlow)!}
                          readOnly
                          className="flex-1 px-2 py-1 bg-background rounded text-xs"
                        />
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0"
                          onClick={() => copyToClipboard(getAccessUrl(selectedFlow)!)}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0"
                          onClick={() => window.open(getAccessUrl(selectedFlow)! + '/health', '_blank')}
                        >
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Tabs for Logs, Info, ACI */}
              {selectedFlow.container?.running && (
                <Tabs defaultValue="logs" className="flex-1 flex flex-col mt-2 min-h-0">
                  <TabsList className="mb-2 justify-start w-auto flex-shrink-0">
                    <TabsTrigger value="logs">Logs</TabsTrigger>
                    <TabsTrigger value="info">Flow Info</TabsTrigger>
                    {selectedFlow.mode === 'agent' && (
                      <TabsTrigger value="aci">ACI Routes</TabsTrigger>
                    )}
                  </TabsList>

                  {/* Logs Tab */}
                  <TabsContent value="logs" className="flex-1 flex flex-col mt-0 min-h-0">
                    <Card className="p-3 flex-1 flex flex-col min-h-0">
                      <div className="flex items-center justify-between mb-2 flex-shrink-0">
                        <h3 className="font-normal text-sm">Container Logs (Live)</h3>
                        <Button size="sm" onClick={() => loadLogs(selectedFlow.name, false)} disabled={logsLoading}>
                          <RotateCw className={cn("h-3 w-3 mr-1.5", logsLoading && "animate-spin")} />
                          Refresh
                        </Button>
                      </div>
                      <pre className="flex-1 min-h-0 p-3 bg-black text-green-400 rounded font-mono text-xs overflow-auto whitespace-pre-wrap">
                        {logs || 'Loading logs...'}
                      </pre>
                    </Card>
                  </TabsContent>

                  {/* Info Tab */}
                  <TabsContent value="info" className="flex-1 overflow-auto mt-0 min-h-0">
                    <Card className="p-3">
                      <h3 className="font-normal mb-2 text-sm">Flow Configuration</h3>
                      <div className="space-y-1.5 text-sm">
                        <div className="flex justify-between py-1.5 border-b">
                          <span className="text-muted-foreground">Container Name:</span>
                          <code className="text-xs">act-{selectedFlow.name}</code>
                        </div>
                        <div className="flex justify-between py-1.5 border-b">
                          <span className="text-muted-foreground">Status:</span>
                          <code className="text-xs">{selectedFlow.container?.status || 'unknown'}</code>
                        </div>
                        {selectedFlow.container?.started_at && (
                          <div className="flex justify-between py-1.5 border-b">
                            <span className="text-muted-foreground">Started At:</span>
                            <code className="text-xs">{new Date(selectedFlow.container.started_at).toLocaleString()}</code>
                          </div>
                        )}
                        <div className="flex justify-between py-1.5">
                          <span className="text-muted-foreground">Auto-assigned Port:</span>
                          <code className="text-xs">{selectedFlow.auto_assigned ? 'Yes' : 'No'}</code>
                        </div>
                      </div>
                    </Card>
                  </TabsContent>

                  {/* ACI Routes Tab */}
                  {selectedFlow.mode === 'agent' && (
                    <ACIRoutesTab flow={selectedFlow} />
                  )}
                </Tabs>
              )}
            </div>
          ) : (
            // Flows List View
            <div className="flex flex-col flex-1 min-h-0">
              <div className="mb-6 flex items-start justify-between gap-4 flex-shrink-0">
                <div className="flex-1">
                  <h2 className="mb-2 text-lg font-normal">Available Flows</h2>
                  <p className="text-sm text-muted-foreground">
                    Manage your ACT workflow automation flows.
                  </p>
                </div>
                <div className="relative w-80">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search flows..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full h-9 pl-9 pr-3 rounded-md border border-input bg-background text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  />
                </div>
              </div>

              {/* Flows List */}
              <div className="flex-1 min-h-0 overflow-auto pr-4">
                <div className="space-y-3">
                  {filteredFlows.map((flow) => (
                    <div
                      key={flow.name}
                      onClick={() => setSelectedFlow(flow)}
                      className="flex items-center gap-4 p-4 rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                    >
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 flex-shrink-0">
                        {flow.mode === 'agent' ? (
                          <Network className="w-6 h-6 text-primary" />
                        ) : (
                          <Zap className="w-6 h-6 text-primary" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h3 className="font-normal">{flow.agent_name || flow.name}</h3>
                          {flow.auto_assigned && (
                            <Badge variant="outline" className="text-xs">Auto</Badge>
                          )}
                        </div>
                        {flow.description && (
                          <p className="text-sm text-muted-foreground mb-1 max-w-md">
                            {flow.description}
                          </p>
                        )}
                        <p className="text-xs text-muted-foreground/70 line-clamp-1">
                          {flow.mode === 'agent' ? 'Agent Mode' : flow.mode === 'miniact' ? 'MiniACT Mode' : 'Waiting'} • Port {flow.port}
                        </p>
                      </div>

                      {/* Status Badge & Action Buttons */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {flow.container?.running ? (
                          <>
                            {flow.health?.status === 'healthy' ? (
                              <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                                <Circle className="mr-1 h-2 w-2 fill-green-500 text-green-500" />
                                Running
                              </Badge>
                            ) : (
                              <Badge variant="secondary">
                                <Circle className="mr-1 h-2 w-2 fill-red-500 text-red-500" />
                                Unhealthy
                              </Badge>
                            )}
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleFlowAction(flow.name, 'stop')
                              }}
                              disabled={actionLoading === flow.name}
                              title="Stop flow"
                            >
                              <Square className="h-3.5 w-3.5" />
                            </Button>
                          </>
                        ) : (
                          <>
                            <Badge variant="secondary">
                              <Circle className="mr-1 h-2 w-2 fill-gray-400 text-gray-400" />
                              Stopped
                            </Badge>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleFlowAction(flow.name, 'start')
                              }}
                              disabled={actionLoading === flow.name}
                              title="Start flow"
                            >
                              <Play className="h-3.5 w-3.5" />
                            </Button>
                          </>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleFlowAction(flow.name, 'restart')
                          }}
                          disabled={actionLoading === flow.name}
                          title="Restart flow"
                        >
                          <RotateCw className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
