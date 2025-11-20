"use client"

import React, { useState, useEffect, useCallback, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Play,
  Square,
  RotateCw,
  ArrowLeft,
  AlertCircle,
  Check,
  Plus,
  ChevronDown,
  Search,
  Server,
  PlayCircle,
  PauseCircle,
  Layers,
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { MCPServer, MCPServerStatus } from "@/lib/mcp-hub/types"
import { MCPDetail } from "./mcp-detail"
import { apiFetch } from "@/lib/utils/api"

export default function MCPHub() {
  const [servers, setServers] = useState<MCPServer[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedServer, setSelectedServer] = useState<MCPServer | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  // Store last data to compare
  const lastDataRef = React.useRef<string>("")

  const loadServers = useCallback(async (silent = false) => {
    if (!silent) {
      setLoading(true)
    }
    try {
      const response = await apiFetch('/api/mcp', {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache'
        }
      })
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to load MCP servers')
      }

      // Only update if data actually changed
      const newDataString = JSON.stringify(data.servers)
      const hasChanged = newDataString !== lastDataRef.current

      if (hasChanged || !silent) {
        lastDataRef.current = newDataString
        setServers(data.servers || [])

        // Update selected server if it exists - use functional update to avoid dependency
        setSelectedServer(prev => {
          if (!prev) return null
          const updated = data.servers.find((s: MCPServer) => s.id === prev.id)
          return updated || prev
        })

        if (!silent) {
          setLoading(false)
        }
      }
    } catch (error) {
      console.error('Failed to load MCP servers:', error)
      if (!silent) {
        setLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    loadServers(false)
    // Silent background refresh every 5 seconds
    const interval = setInterval(() => loadServers(true), 5000)
    return () => clearInterval(interval)
  }, [])

  const handleAction = async (serverId: string, action: 'start' | 'stop' | 'restart') => {
    setActionLoading(serverId)
    try {
      const response = await fetch(`/api/mcp/${serverId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      })
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to perform action')
      }

      await loadServers(false)
    } catch (error: any) {
      console.error('Action error:', error)
      alert(error.message || 'Failed to perform action')
    } finally {
      setActionLoading(null)
    }
  }

  const getStatusBadge = (status: MCPServerStatus) => {
    switch (status) {
      case 'running':
        return (
          <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
            <Check className="mr-1 h-3 w-3" />
            Running
          </Badge>
        )
      case 'stopped':
        return <Badge variant="secondary">Stopped</Badge>
      case 'error':
        return <Badge variant="destructive">Error</Badge>
      case 'starting':
        return <Badge className="bg-yellow-500">Starting</Badge>
    }
  }

  // Filtered servers
  const filteredServers = useMemo(() => {
    let filtered = selectedCategory === 'all'
      ? servers
      : selectedCategory === 'running'
      ? servers.filter(s => s.status === 'running')
      : selectedCategory === 'stopped'
      ? servers.filter(s => s.status === 'stopped')
      : selectedCategory === 'built-in'
      ? servers.filter(s => s.type === 'built-in')
      : servers.filter(s => s.type === 'custom')

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(query) ||
        s.description.toLowerCase().includes(query)
      )
    }

    return filtered
  }, [servers, selectedCategory, searchQuery])

  // Statistics
  const stats = useMemo(() => {
    return {
      total: servers.length,
      running: servers.filter(s => s.status === 'running').length,
      stopped: servers.filter(s => s.status === 'stopped').length,
      builtIn: servers.filter(s => s.type === 'built-in').length,
    }
  }, [servers])

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
          </div>
          {/* Right side skeleton */}
          <div className="p-8">
            <Skeleton className="h-8 w-48 mb-6" />
            <div className="space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-20 w-full" />
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-background">
      <div className="grid h-full grid-cols-[320px_1fr]">
        {/* Left Panel - Sidebar */}
        <div className="border-r p-6 flex flex-col bg-muted/30">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-1">
              <h1 className="text-2xl font-normal">MCP Hub</h1>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add
                    <ChevronDown className="h-3 w-3 ml-1" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>
                    <Server className="h-4 w-4 mr-2" />
                    Add MCP Server
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => loadServers(false)}>
                    <RotateCw className="h-4 w-4 mr-2" />
                    Refresh Server List
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
            <p className="text-sm text-muted-foreground">Manage Model Context Protocol servers</p>
          </div>

          {/* Statistics */}
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
              <div className="text-xl font-normal text-foreground">{stats.stopped}</div>
              <div className="text-xs text-muted-foreground">Stopped</div>
            </Card>

            <Card className="p-3 bg-muted/50">
              <div className="text-xl font-normal text-foreground">{stats.builtIn}</div>
              <div className="text-xs text-muted-foreground">Built-in</div>
            </Card>
          </div>

          {/* Search */}
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search MCP servers..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-background border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          {/* Categories */}
          <div className="mb-6">
            <h3 className="text-sm font-medium mb-3 text-muted-foreground">Filter by Status</h3>
            <div className="space-y-1">
              <button
                onClick={() => setSelectedCategory('all')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors",
                  selectedCategory === 'all'
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                )}
              >
                All ({servers.length})
              </button>
              <button
                onClick={() => setSelectedCategory('running')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors",
                  selectedCategory === 'running'
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                )}
              >
                Running ({stats.running})
              </button>
              <button
                onClick={() => setSelectedCategory('stopped')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors",
                  selectedCategory === 'stopped'
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                )}
              >
                Stopped ({stats.stopped})
              </button>
              <button
                onClick={() => setSelectedCategory('built-in')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors",
                  selectedCategory === 'built-in'
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                )}
              >
                Built-in ({stats.builtIn})
              </button>
              <button
                onClick={() => setSelectedCategory('custom')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors",
                  selectedCategory === 'custom'
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                )}
              >
                Custom ({servers.length - stats.builtIn})
              </button>
            </div>
          </div>

          <div className="flex-1" />

          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => loadServers(false)} className="flex-1 bg-transparent">
              <RotateCw className="h-3 w-3" />
            </Button>
            <Button size="sm" className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90">
              <span>→</span>
            </Button>
          </div>
        </div>

        {/* Right Panel - Main Content */}
        <div className="bg-background p-8 h-full overflow-auto">
          {selectedServer ? (
            // Server Detail View
            <MCPDetail
              server={selectedServer}
              onClose={() => setSelectedServer(null)}
              onAction={(action) => handleAction(selectedServer.id, action)}
              loading={actionLoading === selectedServer.id}
            />
          ) : (
            // Server List View
            <>
              <h2 className="text-xl font-normal mb-6">MCP Servers</h2>

              {filteredServers.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    No MCP servers found. Add a server to get started.
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="space-y-3">
                  {filteredServers.map((server) => (
                    <div
                      key={server.id}
                      className="border rounded-lg p-4 hover:border-primary/50 transition-colors bg-card cursor-pointer"
                      onClick={() => setSelectedServer(server)}
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 flex-shrink-0">
                          <Server className="h-6 w-6 text-primary" />
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-medium truncate">{server.name}</h3>
                            {getStatusBadge(server.status)}
                          </div>
                          <p className="text-sm text-muted-foreground truncate">
                            {server.description}
                          </p>
                          <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                            <span>Type: {server.type}</span>
                            <span>Tools: {server.toolCount}</span>
                          </div>
                        </div>

                        <div className="flex gap-2 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                          {server.status === 'running' ? (
                            <>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleAction(server.id, 'stop')}
                                disabled={actionLoading === server.id}
                              >
                                {actionLoading === server.id ? (
                                  <RotateCw className="h-3.5 w-3.5 animate-spin" />
                                ) : (
                                  <Square className="h-3.5 w-3.5" />
                                )}
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleAction(server.id, 'restart')}
                                disabled={actionLoading === server.id}
                              >
                                <RotateCw className={cn("h-3.5 w-3.5", actionLoading === server.id && "animate-spin")} />
                              </Button>
                            </>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => handleAction(server.id, 'start')}
                              disabled={actionLoading === server.id}
                            >
                              {actionLoading === server.id ? (
                                <>
                                  <RotateCw className="mr-2 h-3.5 w-3.5 animate-spin" />
                                  Starting...
                                </>
                              ) : (
                                <>
                                  <Play className="mr-2 h-3.5 w-3.5" />
                                  Start
                                </>
                              )}
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
