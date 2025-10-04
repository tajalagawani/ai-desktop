"use client"

import React, { useEffect, useState, useCallback, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MCP_CATEGORIES, MCPServerConfig } from "@/data/mcp-servers"
import { getIcon } from "@/utils/icon-mapper"
import {
  Play,
  Square,
  RotateCw,
  ArrowLeft,
  AlertCircle,
  Check,
  Key,
  Copy,
  Search,
  Power,
  PowerOff,
  Settings,
  Trash2,
  Shield,
  PackageOpen
} from "lucide-react"
import { cn } from "@/lib/utils"

interface MCPServerWithStatus extends MCPServerConfig {
  enabled: boolean
  status: string
}

interface ACPAgentProps {
  // Props available for future use
}

// Main Component
export function ACPAgent(_props: ACPAgentProps) {
  const [servers, setServers] = useState<MCPServerWithStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [mcpInstalled, setMcpInstalled] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedServer, setSelectedServer] = useState<MCPServerWithStatus | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [gatewayStatus, setGatewayStatus] = useState<string>("stopped")
  const [gatewayPort, setGatewayPort] = useState<number>(8080)
  const [secretsForm, setSecretsForm] = useState<Record<string, string>>({})
  const [showSecretsDialog, setShowSecretsDialog] = useState(false)

  const loadServers = useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/mcp')
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to load MCP servers')
      }

      setMcpInstalled(data.mcpInstalled)
      setServers(data.servers || [])
      setGatewayStatus(data.gatewayStatus || 'stopped')
    } catch (error) {
      console.error('Failed to load MCP servers:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadServers()
  }, [loadServers])

  const handleServerAction = async (serverId: string, action: string, additionalData?: any) => {
    setActionLoading(serverId)
    try {
      const response = await fetch('/api/mcp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, serverId, ...additionalData })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Server action failed')
      }

      await loadServers()

      // Refresh selected server if it's currently selected
      if (selectedServer?.id === serverId) {
        const updatedServer = servers.find(s => s.id === serverId)
        if (updatedServer) {
          setSelectedServer({ ...updatedServer })
        }
      }

      // Show success message
      alert(data.message || 'Action completed successfully')
    } catch (error: any) {
      console.error('Server action error:', error)
      alert(error.message || 'Failed to perform action')
    } finally {
      setActionLoading(null)
    }
  }

  const handleGatewayAction = async (action: 'start' | 'stop') => {
    setActionLoading('gateway')
    try {
      const response = await fetch('/api/mcp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: action === 'start' ? 'start-gateway' : 'stop-gateway',
          port: gatewayPort
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Gateway action failed')
      }

      await loadServers()
      alert(data.message)
    } catch (error: any) {
      console.error('Gateway action error:', error)
      alert(error.message || 'Failed to control gateway')
    } finally {
      setActionLoading(null)
    }
  }

  const handleAuthorizeOAuth = async (serverId: string) => {
    const server = servers.find(s => s.id === serverId)
    if (!server || !server.requiresOAuth) return

    setActionLoading(serverId)
    try {
      const response = await fetch('/api/mcp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'authorize-oauth', serverId })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'OAuth authorization failed')
      }

      alert(data.message)
    } catch (error: any) {
      console.error('OAuth error:', error)
      alert(error.message || 'Failed to authorize OAuth')
    } finally {
      setActionLoading(null)
    }
  }

  const handleSetSecrets = async (serverId: string) => {
    const server = servers.find(s => s.id === serverId)
    if (!server || !server.defaultSecrets) return

    const secrets = server.defaultSecrets.map(secret => ({
      key: secret.key,
      value: secretsForm[secret.key] || ''
    })).filter(s => s.value)

    if (secrets.length === 0) {
      alert('Please fill in at least one secret')
      return
    }

    setActionLoading(serverId)
    try {
      const response = await fetch('/api/mcp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'set-secrets', serverId, secrets })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to set secrets')
      }

      alert(data.message)
      setSecretsForm({})
      setShowSecretsDialog(false)
    } catch (error: any) {
      console.error('Set secrets error:', error)
      alert(error.message || 'Failed to set secrets')
    } finally {
      setActionLoading(null)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  // Filtered servers
  const filteredServers = useMemo(() => {
    let filtered = selectedCategory === 'all'
      ? servers
      : servers.filter(s => s.category === selectedCategory)

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
  }, [servers, selectedCategory, searchQuery])

  // Statistics
  const stats = useMemo(() => {
    return {
      total: servers.length,
      enabled: servers.filter(s => s.enabled).length,
      available: servers.filter(s => !s.enabled).length,
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

  if (!mcpInstalled) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <Alert className="max-w-2xl">
          <AlertCircle className="h-5 w-5" />
          <AlertTitle className="text-xl font-normal mb-2">Docker MCP Toolkit Required</AlertTitle>
          <AlertDescription className="space-y-4">
            <p>
              Docker MCP Toolkit is required to manage AI Context Protocol servers.
              Please install Docker Desktop 4.42.0+ and enable MCP Toolkit.
            </p>
            <div className="space-y-2">
              <p className="font-normal">Installation steps:</p>
              <ol className="list-decimal list-inside space-y-1 text-sm">
                <li>Install Docker Desktop 4.42.0 or later</li>
                <li>Open Docker Desktop → Settings</li>
                <li>Go to Beta features</li>
                <li>Enable "Docker MCP Toolkit"</li>
                <li>Restart Docker Desktop</li>
              </ol>
            </div>
            <Button asChild className="w-full sm:w-auto bg-primary text-primary-foreground hover:bg-primary/90">
              <a href="https://docs.docker.com/desktop/" target="_blank" rel="noopener noreferrer">
                <PackageOpen className="mr-2 h-4 w-4" />
                Install Docker Desktop
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
            <h2 className="text-lg font-normal mb-2">ACP Agent</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              AI Context Protocol - Manage MCP servers on your VPS.
            </p>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-2 gap-2 mb-6">
            <Card className="p-3 border bg-card">
              <div className="text-xl font-normal text-foreground">{stats.total}</div>
              <div className="text-xs text-muted-foreground">Total</div>
            </Card>

            <Card className="p-3 border bg-card">
              <div className="text-xl font-normal text-foreground">{stats.enabled}</div>
              <div className="text-xs text-muted-foreground">Enabled</div>
            </Card>

            <Card className="p-3 border bg-card">
              <div className="text-xl font-normal text-foreground">{stats.available}</div>
              <div className="text-xs text-muted-foreground">Available</div>
            </Card>

            <Card className="p-3 border bg-card">
              <div className={cn(
                "text-xl font-normal",
                gatewayStatus === 'running' ? "text-green-500" : "text-muted-foreground"
              )}>
                {gatewayStatus === 'running' ? '●' : '○'}
              </div>
              <div className="text-xs text-muted-foreground">Gateway</div>
            </Card>
          </div>

          {/* Gateway Control */}
          <div className="mb-6">
            <Card className="p-3 border bg-card">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-normal text-sm">MCP Gateway</h3>
                <Badge variant={gatewayStatus === 'running' ? "default" : "secondary"} className="text-xs">
                  {gatewayStatus}
                </Badge>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Label className="text-xs">Port:</Label>
                  <Input
                    type="number"
                    value={gatewayPort}
                    onChange={(e) => setGatewayPort(parseInt(e.target.value) || 8080)}
                    className="h-7 text-xs flex-1"
                    disabled={gatewayStatus === 'running'}
                  />
                </div>
                {gatewayStatus === 'running' ? (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleGatewayAction('stop')}
                    disabled={actionLoading === 'gateway'}
                    className="w-full bg-transparent"
                  >
                    <PowerOff className="h-3 w-3 mr-2" />
                    Stop Gateway
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    onClick={() => handleGatewayAction('start')}
                    disabled={actionLoading === 'gateway'}
                    className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    <Power className="h-3 w-3 mr-2" />
                    Start Gateway
                  </Button>
                )}
              </div>
            </Card>
          </div>

          <div className="flex-1" />

          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={loadServers} className="flex-1 bg-transparent">
              <RotateCw className="h-3 w-3" />
            </Button>
            <Button size="sm" className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90">
              <Settings className="h-3 w-3" />
            </Button>
          </div>
        </div>

        {/* Right Panel - Dynamic Content */}
        <div className="bg-background p-8 h-full overflow-hidden flex flex-col">
          {selectedServer ? (
            // Server Detail View
            <div className="flex flex-col flex-1 min-h-0">
              <Button
                variant="ghost"
                size="sm"
                className="mb-4 -ml-2 w-fit"
                onClick={() => setSelectedServer(null)}
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to MCP servers
              </Button>

              <div className="mb-4 flex items-start gap-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 shadow-sm flex-shrink-0">
                  {selectedServer.iconType === 'image' ? (
                    <img src={selectedServer.icon} alt={selectedServer.name} className="h-10 w-10 object-contain" />
                  ) : (
                    (() => {
                      const Icon = getIcon(selectedServer.icon)
                      return <Icon className="h-8 w-8 text-primary" />
                    })()
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h2 className="text-2xl font-normal">{selectedServer.name}</h2>
                    {selectedServer.enabled ? (
                      <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                        <Check className="mr-1 h-3 w-3" />
                        Enabled
                      </Badge>
                    ) : (
                      <Badge variant="secondary">Disabled</Badge>
                    )}
                    <Badge variant="outline">
                      {selectedServer.type === 'local' ? '🔒 Local' : '🌐 Remote'}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {MCP_CATEGORIES.find(c => c.id === selectedServer.category)?.name || selectedServer.category}
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 items-center flex-shrink-0">
                  {selectedServer.enabled ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleServerAction(selectedServer.id, 'disable')}
                      disabled={actionLoading === selectedServer.id}
                      title="Disable server"
                    >
                      <Square className="h-3.5 w-3.5 mr-1.5" />
                      Disable
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => handleServerAction(selectedServer.id, 'enable')}
                      disabled={actionLoading === selectedServer.id}
                      className="bg-primary text-primary-foreground hover:bg-primary/90"
                      title="Enable server"
                    >
                      <Play className="h-3.5 w-3.5 mr-1.5" />
                      Enable
                    </Button>
                  )}
                </div>
              </div>

              {/* Description */}
              <Card className="p-4 mb-4">
                <p className="text-sm">{selectedServer.description}</p>
              </Card>

              {/* OAuth / Secrets Setup */}
              {(selectedServer.requiresOAuth || selectedServer.defaultSecrets) && (
                <Card className="p-4 mb-4">
                  <h3 className="font-normal text-sm mb-3 flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    Configuration Required
                  </h3>

                  {selectedServer.requiresOAuth && (
                    <div className="mb-3">
                      <Label className="text-xs text-muted-foreground mb-2 block">
                        OAuth Authorization ({selectedServer.oauthProvider})
                      </Label>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAuthorizeOAuth(selectedServer.id)}
                        disabled={actionLoading === selectedServer.id}
                        className="w-full"
                      >
                        <Key className="h-3.5 w-3.5 mr-2" />
                        Authorize {selectedServer.oauthProvider}
                      </Button>
                    </div>
                  )}

                  {selectedServer.defaultSecrets && selectedServer.defaultSecrets.length > 0 && (
                    <div>
                      <Label className="text-xs text-muted-foreground mb-2 block">Secrets</Label>
                      <div className="space-y-2">
                        {selectedServer.defaultSecrets.map((secret) => (
                          <div key={secret.key}>
                            <Label className="text-xs mb-1 block">
                              {secret.description}
                              {secret.required && <span className="text-red-500">*</span>}
                            </Label>
                            <Input
                              type="password"
                              placeholder={secret.placeholder || `Enter ${secret.description}`}
                              value={secretsForm[secret.key] || ''}
                              onChange={(e) => setSecretsForm({ ...secretsForm, [secret.key]: e.target.value })}
                              className="h-8 text-xs"
                            />
                          </div>
                        ))}
                        <Button
                          size="sm"
                          onClick={() => handleSetSecrets(selectedServer.id)}
                          disabled={actionLoading === selectedServer.id}
                          className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
                        >
                          <Key className="h-3.5 w-3.5 mr-2" />
                          Save Secrets
                        </Button>
                      </div>
                    </div>
                  )}
                </Card>
              )}

              {/* Tabs */}
              <Tabs defaultValue="tools" className="flex-1 flex flex-col min-h-0">
                <TabsList className="mb-2 justify-start w-auto flex-shrink-0">
                  {selectedServer.tools && selectedServer.tools.length > 0 && (
                    <TabsTrigger value="tools">Tools ({selectedServer.tools.length})</TabsTrigger>
                  )}
                  <TabsTrigger value="config">Configuration</TabsTrigger>
                </TabsList>

                {/* Tools Tab */}
                {selectedServer.tools && selectedServer.tools.length > 0 && (
                  <TabsContent value="tools" className="flex-1 overflow-auto mt-0 min-h-0">
                    <Card className="p-4">
                      <h3 className="font-normal mb-3 text-sm">Available Tools</h3>
                      <div className="space-y-2">
                        {selectedServer.tools.map((tool, index) => (
                          <div key={index} className="p-3 bg-muted/50 rounded-lg">
                            <div className="font-mono text-xs font-normal mb-1">{tool.name}</div>
                            <div className="text-xs text-muted-foreground">{tool.description}</div>
                          </div>
                        ))}
                      </div>
                    </Card>
                  </TabsContent>
                )}

                {/* Configuration Tab */}
                <TabsContent value="config" className="flex-1 overflow-auto mt-0 min-h-0">
                  <Card className="p-4">
                    <h3 className="font-normal mb-3 text-sm">Server Configuration</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between py-2 border-b">
                        <span className="text-muted-foreground">Server ID:</span>
                        <code className="text-xs">{selectedServer.id}</code>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span className="text-muted-foreground">Docker Image:</span>
                        <code className="text-xs">{selectedServer.dockerImage}</code>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span className="text-muted-foreground">Type:</span>
                        <Badge variant="outline" className="text-xs">
                          {selectedServer.type === 'local' ? 'Local (Offline)' : 'Remote (Online)'}
                        </Badge>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span className="text-muted-foreground">OAuth Required:</span>
                        <Badge variant={selectedServer.requiresOAuth ? "default" : "secondary"} className="text-xs">
                          {selectedServer.requiresOAuth ? 'Yes' : 'No'}
                        </Badge>
                      </div>
                      {selectedServer.documentation && (
                        <div className="flex justify-between py-2">
                          <span className="text-muted-foreground">Documentation:</span>
                          <a
                            href={selectedServer.documentation}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-primary hover:underline"
                          >
                            View Docs →
                          </a>
                        </div>
                      )}
                    </div>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>
          ) : (
            // MCP Servers List View
            <div>
              <div className="mb-6 flex items-start justify-between gap-4">
                <div className="flex-1">
                  <h2 className="mb-2 text-lg font-normal">MCP Servers</h2>
                  <p className="text-sm text-muted-foreground">
                    Model Context Protocol servers for AI agent capabilities
                  </p>
                </div>
                <div className="relative w-80">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search servers..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full h-9 pl-9 pr-3 rounded-md border border-input bg-background text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  />
                </div>
              </div>

              {/* Category Tabs */}
              <div className="mb-6 flex gap-2 border-b overflow-x-auto">
                {MCP_CATEGORIES.map((cat) => (
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

              {/* Servers List */}
              <ScrollArea className="h-[calc(100vh-280px)]">
                <div className="space-y-3 pr-4">
                  {filteredServers.map((server) => {
                    const Icon = server.iconType === 'image' ? null : getIcon(server.icon)
                    return (
                      <div
                        key={server.id}
                        onClick={() => setSelectedServer(server)}
                        className="flex items-center gap-4 p-4 rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                      >
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 flex-shrink-0">
                          {server.iconType === 'image' ? (
                            <img src={server.icon} alt={server.name} className="h-8 w-8 object-contain" />
                          ) : Icon && (
                            <Icon className="w-6 h-6 text-primary" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-normal">{server.name}</h3>
                            {server.type === 'local' && (
                              <Badge variant="outline" className="text-xs">Local</Badge>
                            )}
                            {server.requiresOAuth && (
                              <Badge variant="outline" className="text-xs">OAuth</Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-1">
                            {server.description}
                          </p>
                        </div>

                        {/* Status Badge & Action */}
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {server.enabled ? (
                            <>
                              <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                                <Check className="mr-1 h-3 w-3" />
                                Enabled
                              </Badge>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleServerAction(server.id, 'disable')
                                }}
                                disabled={actionLoading === server.id}
                                title="Disable"
                              >
                                <Square className="h-3.5 w-3.5" />
                              </Button>
                            </>
                          ) : (
                            <Button
                              size="sm"
                              variant="outline"
                              className="bg-transparent"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleServerAction(server.id, 'enable')
                              }}
                              disabled={actionLoading === server.id}
                            >
                              {actionLoading === server.id ? 'Enabling...' : 'Enable'}
                            </Button>
                          )}
                        </div>
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
