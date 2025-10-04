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
import { getAuthorizationUrl } from "@/lib/mcp/oauth-client"
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
  Settings,
  Trash2,
  Shield,
  PackageOpen,
  ExternalLink,
  CheckCircle2
} from "lucide-react"
import { cn } from "@/lib/utils"

interface MCPServerWithStatus extends MCPServerConfig {
  enabled: boolean
  status: string
  hasOAuthToken?: boolean
  oauthConnected?: boolean
  containerName?: string
}

interface ACPAgentProps {}

export function ACPAgent(_props: ACPAgentProps) {
  const [servers, setServers] = useState<MCPServerWithStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [dockerInstalled, setDockerInstalled] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedServer, setSelectedServer] = useState<MCPServerWithStatus | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [secretsForm, setSecretsForm] = useState<Record<string, string>>({})

  const loadServers = useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/mcp')
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to load MCP servers')
      }

      setDockerInstalled(data.dockerInstalled)
      setServers(data.servers || [])
    } catch (error) {
      console.error('Failed to load MCP servers:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadServers()

    // Listen for OAuth success messages from popup
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'oauth_success') {
        console.log('OAuth success:', event.data.provider)
        // Reload servers to update OAuth status
        loadServers()
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
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
        // Check if OAuth is required
        if (data.requiresOAuth) {
          alert(`${data.error}\n\nClick the "Connect ${data.provider}" button first.`)
          setActionLoading(null)
          return
        }
        throw new Error(data.error || 'Server action failed')
      }

      await loadServers()

      // Update selected server
      if (selectedServer?.id === serverId) {
        const updatedServer = servers.find(s => s.id === serverId)
        if (updatedServer) {
          setSelectedServer({ ...updatedServer, enabled: action === 'start' })
        }
      }

      // Success notification
      console.log('✓', data.message)
    } catch (error: any) {
      console.error('Server action error:', error)
      alert(error.message || 'Failed to perform action')
    } finally {
      setActionLoading(null)
    }
  }

  const handleOAuthConnect = async (provider: string) => {
    try {
      const authUrl = await getAuthorizationUrl(provider)

      // Open OAuth in popup
      const width = 600
      const height = 700
      const left = window.screenX + (window.outerWidth - width) / 2
      const top = window.screenY + (window.outerHeight - height) / 2

      window.open(
        authUrl,
        `oauth-${provider}`,
        `width=${width},height=${height},left=${left},top=${top},toolbar=no,location=no,status=no,menubar=no`
      )
    } catch (error: any) {
      alert(`OAuth error: ${error.message}`)
    }
  }

  const handleSetSecrets = async (serverId: string) => {
    const server = servers.find(s => s.id === serverId)
    if (!server || !server.defaultSecrets) return

    const secrets = Object.fromEntries(
      Object.entries(secretsForm).filter(([_, value]) => value)
    )

    if (Object.keys(secrets).length === 0) {
      alert('Please fill in at least one secret')
      return
    }

    setActionLoading(serverId)
    try {
      await handleServerAction(serverId, 'start', { config: { secrets } })
      setSecretsForm({})
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
      running: servers.filter(s => s.enabled).length,
      stopped: servers.filter(s => !s.enabled).length,
      oauthConnected: servers.filter(s => s.hasOAuthToken).length
    }
  }, [servers])

  if (loading) {
    return (
      <div className="h-full bg-background">
        <div className="grid h-full grid-cols-[320px_1fr]">
          <div className="border-r p-6 flex flex-col">
            <Skeleton className="h-8 w-48 mb-6" />
            <div className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          </div>
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
              Docker is required to run MCP servers on your VPS.
              Please install Docker Engine.
            </p>
            <div className="space-y-2">
              <p className="font-normal">Installation:</p>
              <pre className="bg-muted p-3 rounded text-xs overflow-x-auto">
{`curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
sudo systemctl enable docker`}
              </pre>
            </div>
            <Button asChild className="w-full sm:w-auto">
              <a href="https://docs.docker.com/engine/install/" target="_blank" rel="noopener noreferrer">
                <PackageOpen className="mr-2 h-4 w-4" />
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
        {/* Left Panel - Stats & Info */}
        <div className="relative overflow-hidden border-r bg-background p-6 h-full flex flex-col">
          <div className="mb-6">
            <h2 className="text-lg font-normal mb-2">ACP Agent</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              AI Context Protocol - Manage MCP servers with browser OAuth.
            </p>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-2 gap-2 mb-6">
            <Card className="p-3 border">
              <div className="text-xl font-normal">{stats.total}</div>
              <div className="text-xs text-muted-foreground">Total</div>
            </Card>

            <Card className="p-3 border">
              <div className="text-xl font-normal text-green-500">{stats.running}</div>
              <div className="text-xs text-muted-foreground">Running</div>
            </Card>

            <Card className="p-3 border">
              <div className="text-xl font-normal">{stats.stopped}</div>
              <div className="text-xs text-muted-foreground">Stopped</div>
            </Card>

            <Card className="p-3 border">
              <div className="text-xl font-normal text-blue-500">{stats.oauthConnected}</div>
              <div className="text-xs text-muted-foreground">OAuth</div>
            </Card>
          </div>

          {/* Info Box */}
          <Card className="p-4 mb-4 border bg-muted/50">
            <h3 className="font-normal text-sm mb-2 flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Browser OAuth
            </h3>
            <p className="text-xs text-muted-foreground">
              OAuth happens in your browser. Click "Connect" buttons to authorize MCP servers.
            </p>
          </Card>

          <div className="flex-1" />

          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={loadServers} className="flex-1">
              <RotateCw className="h-3 w-3" />
            </Button>
            <Button size="sm" className="flex-1">
              <Settings className="h-3 w-3" />
            </Button>
          </div>
        </div>

        {/* Right Panel - Servers List/Detail */}
        <div className="bg-background p-8 h-full overflow-hidden flex flex-col">
          {selectedServer ? (
            // Server Detail View
            <ServerDetailView
              server={selectedServer}
              onBack={() => setSelectedServer(null)}
              onAction={handleServerAction}
              onOAuthConnect={handleOAuthConnect}
              onSetSecrets={handleSetSecrets}
              actionLoading={actionLoading}
              secretsForm={secretsForm}
              setSecretsForm={setSecretsForm}
            />
          ) : (
            // Servers List View
            <div>
              <div className="mb-6 flex items-start justify-between gap-4">
                <div className="flex-1">
                  <h2 className="mb-2 text-lg font-normal">MCP Servers</h2>
                  <p className="text-sm text-muted-foreground">
                    Manage containerized AI tools with OAuth
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
                              <Badge variant="outline" className="text-xs flex items-center gap-1">
                                {server.hasOAuthToken ? (
                                  <><CheckCircle2 className="h-3 w-3 text-green-500" />OAuth</>
                                ) : (
                                  <>OAuth</>
                                )}
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-1">
                            {server.description}
                          </p>
                        </div>

                        {/* Status & Action */}
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {server.enabled ? (
                            <>
                              <Badge className="bg-green-500 hover:bg-green-600">
                                <Check className="mr-1 h-3 w-3" />
                                Running
                              </Badge>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleServerAction(server.id, 'stop')
                                }}
                                disabled={actionLoading === server.id}
                                title="Stop"
                              >
                                <Square className="h-3.5 w-3.5" />
                              </Button>
                            </>
                          ) : (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleServerAction(server.id, 'start')
                              }}
                              disabled={actionLoading === server.id}
                            >
                              {actionLoading === server.id ? 'Starting...' : 'Start'}
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

// Server Detail View Component
function ServerDetailView({
  server,
  onBack,
  onAction,
  onOAuthConnect,
  onSetSecrets,
  actionLoading,
  secretsForm,
  setSecretsForm
}: {
  server: MCPServerWithStatus
  onBack: () => void
  onAction: (serverId: string, action: string, data?: any) => Promise<void>
  onOAuthConnect: (provider: string) => void
  onSetSecrets: (serverId: string) => void
  actionLoading: string | null
  secretsForm: Record<string, string>
  setSecretsForm: (form: Record<string, string>) => void
}) {
  const Icon = server.iconType === 'image' ? null : getIcon(server.icon)

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <Button
        variant="ghost"
        size="sm"
        className="mb-4 -ml-2 w-fit"
        onClick={onBack}
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to MCP servers
      </Button>

      <div className="mb-4 flex items-start gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 shadow-sm flex-shrink-0">
          {server.iconType === 'image' ? (
            <img src={server.icon} alt={server.name} className="h-10 w-10 object-contain" />
          ) : Icon && (
            <Icon className="h-8 w-8 text-primary" />
          )}
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-2xl font-normal">{server.name}</h2>
            {server.enabled ? (
              <Badge className="bg-green-500 hover:bg-green-600">
                <Check className="mr-1 h-3 w-3" />
                Running
              </Badge>
            ) : (
              <Badge variant="secondary">Stopped</Badge>
            )}
            <Badge variant="outline">
              {server.type === 'local' ? '🔒 Local' : '🌐 Remote'}
            </Badge>
            {server.hasOAuthToken && (
              <Badge className="bg-blue-500 hover:bg-blue-600">
                <CheckCircle2 className="mr-1 h-3 w-3" />
                OAuth Connected
              </Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground">
            {MCP_CATEGORIES.find(c => c.id === server.category)?.name || server.category}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-2 items-center flex-shrink-0">
          {server.enabled ? (
            <>
              <Button
                size="sm"
                variant="outline"
                onClick={() => onAction(server.id, 'restart')}
                disabled={actionLoading === server.id}
              >
                <RotateCw className="h-3.5 w-3.5 mr-1.5" />
                Restart
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => onAction(server.id, 'stop')}
                disabled={actionLoading === server.id}
              >
                <Square className="h-3.5 w-3.5 mr-1.5" />
                Stop
              </Button>
            </>
          ) : (
            <Button
              size="sm"
              onClick={() => onAction(server.id, 'start')}
              disabled={actionLoading === server.id}
            >
              <Play className="h-3.5 w-3.5 mr-1.5" />
              Start
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            onClick={() => onAction(server.id, 'remove')}
            disabled={actionLoading === server.id}
            title="Remove container"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      {/* Description */}
      <Card className="p-4 mb-4">
        <p className="text-sm">{server.description}</p>
      </Card>

      {/* OAuth / Secrets Setup */}
      {(server.requiresOAuth || server.defaultSecrets) && (
        <Card className="p-4 mb-4">
          <h3 className="font-normal text-sm mb-3 flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Configuration
          </h3>

          {server.requiresOAuth && (
            <div className="mb-3">
              <Label className="text-xs text-muted-foreground mb-2 block">
                OAuth Authorization ({server.oauthProvider})
              </Label>
              {server.hasOAuthToken ? (
                <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                  <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                  <span className="text-sm text-green-700 dark:text-green-300">
                    Connected to {server.oauthProvider}
                  </span>
                </div>
              ) : (
                <Button
                  size="sm"
                  onClick={() => onOAuthConnect(server.oauthProvider!)}
                  className="w-full"
                >
                  <Key className="h-3.5 w-3.5 mr-2" />
                  Connect {server.oauthProvider}
                </Button>
              )}
            </div>
          )}

          {server.defaultSecrets && server.defaultSecrets.length > 0 && (
            <div>
              <Label className="text-xs text-muted-foreground mb-2 block">Secrets</Label>
              <div className="space-y-2">
                {server.defaultSecrets.map((secret) => (
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
                  onClick={() => onSetSecrets(server.id)}
                  disabled={actionLoading === server.id}
                  className="w-full"
                >
                  <Key className="h-3.5 w-3.5 mr-2" />
                  Start with Secrets
                </Button>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Tabs */}
      <Tabs defaultValue="tools" className="flex-1 flex flex-col min-h-0">
        <TabsList className="mb-2 justify-start w-auto flex-shrink-0">
          {server.tools && server.tools.length > 0 && (
            <TabsTrigger value="tools">Tools ({server.tools.length})</TabsTrigger>
          )}
          <TabsTrigger value="config">Configuration</TabsTrigger>
        </TabsList>

        {/* Tools Tab */}
        {server.tools && server.tools.length > 0 && (
          <TabsContent value="tools" className="flex-1 overflow-auto mt-0 min-h-0">
            <Card className="p-4">
              <h3 className="font-normal mb-3 text-sm">Available Tools</h3>
              <div className="space-y-2">
                {server.tools.map((tool, index) => (
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
                <code className="text-xs">{server.id}</code>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-muted-foreground">Docker Image:</span>
                <code className="text-xs">{server.dockerImage}</code>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-muted-foreground">Container:</span>
                <code className="text-xs">{server.containerName}</code>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-muted-foreground">Type:</span>
                <Badge variant="outline" className="text-xs">
                  {server.type === 'local' ? 'Local (Offline)' : 'Remote (Online)'}
                </Badge>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-muted-foreground">OAuth Required:</span>
                <Badge variant={server.requiresOAuth ? "default" : "secondary"} className="text-xs">
                  {server.requiresOAuth ? 'Yes' : 'No'}
                </Badge>
              </div>
              {server.documentation && (
                <div className="flex justify-between py-2">
                  <span className="text-muted-foreground">Documentation:</span>
                  <a
                    href={server.documentation}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-primary hover:underline flex items-center gap-1"
                  >
                    View Docs <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              )}
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
