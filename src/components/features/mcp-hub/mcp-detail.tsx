"use client"

import React, { useState, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  ArrowLeft,
  Play,
  Square,
  RotateCw,
  Check,
  Server,
  Wrench,
  PlayCircle,
  Terminal as TerminalIcon,
  Settings,
  Copy,
  Search,
  AlertCircle,
  Trash2,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { MCPServer } from "@/lib/mcp-hub/types"

interface MCPDetailProps {
  server: MCPServer
  onClose: () => void
  onAction: (action: 'start' | 'stop' | 'restart') => void
  loading: boolean
}

interface MCPTool {
  name: string
  description?: string
  inputSchema?: {
    type: string
    properties?: Record<string, any>
    required?: string[]
  }
}

interface ToolExecution {
  toolName: string
  parameters: Record<string, any>
  result: any
  duration: number
  executedAt: string
  error?: string
}

export function MCPDetail({ server, onClose, onAction, loading }: MCPDetailProps) {
  const [tools, setTools] = useState<MCPTool[]>([])
  const [toolsLoading, setToolsLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTool, setSelectedTool] = useState<MCPTool | null>(null)
  const [parameters, setParameters] = useState('{}')
  const [executing, setExecuting] = useState(false)
  const [executions, setExecutions] = useState<ToolExecution[]>([])
  const [logs, setLogs] = useState<string>('')
  const [autoScroll, setAutoScroll] = useState(true)
  const logsEndRef = React.useRef<HTMLDivElement>(null)

  const loadTools = useCallback(async () => {
    if (server.status !== 'running') return

    setToolsLoading(true)
    try {
      const response = await fetch(`/api/mcp/${server.id}/tools`)
      const data = await response.json()

      if (data.success) {
        setTools(data.tools || [])
      } else {
        console.error('Failed to load tools:', data.error)
      }
    } catch (error) {
      console.error('Failed to load tools:', error)
    } finally {
      setToolsLoading(false)
    }
  }, [server.id])

  useEffect(() => {
    // Only load tools once when component mounts or when explicitly refreshed
    if (server.status === 'running' && tools.length === 0) {
      loadTools()
    }
  }, [server.id])

  // Auto-scroll logs to bottom
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, autoScroll])

  // Simulate log streaming (in production, this would be WebSocket or SSE)
  useEffect(() => {
    if (server.status !== 'running') {
      setLogs('')
      return
    }

    // Add initial log message
    const timestamp = new Date().toISOString()
    setLogs(`[${timestamp}] MCP Server started: ${server.name}\n[${timestamp}] Command: ${server.command} ${server.args?.join(' ') || ''}\n[${timestamp}] Working directory: ${server.cwd || 'N/A'}\n[${timestamp}] Server is ready and accepting connections\n`)

    // Simulate periodic log updates
    const interval = setInterval(() => {
      const ts = new Date().toISOString()
      const messages = [
        `[${ts}] Heartbeat check passed`,
        `[${ts}] Tool registry: ${tools.length} tools available`,
        `[${ts}] Server health: OK`,
      ]
      const randomMsg = messages[Math.floor(Math.random() * messages.length)]
      setLogs(prev => prev + randomMsg + '\n')
    }, 10000) // Add log every 10 seconds

    return () => clearInterval(interval)
  }, [server.status, server.id, tools.length])

  const executeTool = async () => {
    if (!selectedTool) return

    setExecuting(true)
    try {
      const params = JSON.parse(parameters)
      const response = await fetch(`/api/mcp/${server.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          toolName: selectedTool.name,
          parameters: params,
        }),
      })
      const data = await response.json()

      const execution: ToolExecution = {
        toolName: selectedTool.name,
        parameters: params,
        result: data.result,
        duration: data.duration || 0,
        executedAt: data.executedAt || new Date().toISOString(),
        error: data.success ? undefined : data.error,
      }

      setExecutions([execution, ...executions])
    } catch (error: any) {
      const execution: ToolExecution = {
        toolName: selectedTool.name,
        parameters: {},
        result: null,
        duration: 0,
        executedAt: new Date().toISOString(),
        error: error.message,
      }
      setExecutions([execution, ...executions])
    } finally {
      setExecuting(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const filteredTools = tools.filter((tool) => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      tool.name.toLowerCase().includes(query) ||
      (tool.description && tool.description.toLowerCase().includes(query))
    )
  })

  return (
    <div className="flex flex-col flex-1">
      <div className="flex items-center justify-between mb-4">
        <Button
          variant="ghost"
          size="sm"
          className="-ml-2 w-fit"
          onClick={onClose}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to servers
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="text-destructive hover:text-destructive"
        >
          <Trash2 className="mr-2 h-4 w-4" />
          Delete Server
        </Button>
      </div>

      <div className="mb-4 flex items-start gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 shadow-sm flex-shrink-0">
          <Server className="h-8 w-8 text-primary" />
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-2xl font-normal">{server.name}</h2>
            {server.status === 'running' ? (
              <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                <Check className="mr-1 h-3 w-3" />
                Running
              </Badge>
            ) : (
              <Badge variant="secondary">Stopped</Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground">
            {server.type === 'built-in' ? 'Built-in MCP Server' : 'Custom MCP Server'}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 items-center flex-shrink-0">
          {server.status === 'running' ? (
            <>
              <Button
                size="sm"
                variant="outline"
                onClick={() => onAction('stop')}
                disabled={loading}
                title="Stop server"
              >
                {loading ? (
                  <RotateCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Square className="h-3.5 w-3.5" />
                )}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => onAction('restart')}
                disabled={loading}
                title="Restart server"
              >
                <RotateCw className={cn("h-3.5 w-3.5", loading && "animate-spin")} />
              </Button>
            </>
          ) : (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onAction('start')}
              disabled={loading}
              title="Start server"
            >
              {loading ? (
                <RotateCw className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Play className="h-3.5 w-3.5" />
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="flex-1 flex flex-col mt-2 min-h-0">
        <TabsList className="mb-2 justify-start w-auto flex-shrink-0">
          <TabsTrigger value="overview" className="text-xs">Overview</TabsTrigger>
          <TabsTrigger value="tools" className="text-xs">
            <Wrench className="h-3 w-3 mr-1" />
            Tools ({tools.length})
          </TabsTrigger>
          <TabsTrigger value="playground" className="text-xs">
            <PlayCircle className="h-3 w-3 mr-1" />
            Playground
          </TabsTrigger>
          <TabsTrigger value="logs" className="text-xs">
            <TerminalIcon className="h-3 w-3 mr-1" />
            Logs
          </TabsTrigger>
          <TabsTrigger value="settings" className="text-xs">
            <Settings className="h-3 w-3 mr-1" />
            Settings
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="flex-1 overflow-auto mt-0 min-h-0 space-y-4">
          <div className="p-4 bg-muted/50 rounded-lg space-y-3">
            <h3 className="font-normal text-sm flex items-center gap-2">
              <Server className="h-3.5 w-3.5" />
              Server Information
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Server ID:</span>
                <div className="flex items-center gap-2">
                  <code className="font-mono bg-background px-2 py-1 rounded text-xs">
                    {server.id}
                  </code>
                  <Button size="sm" variant="ghost" onClick={() => copyToClipboard(server.id)}>
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Type:</span>
                <span className="text-xs">{server.type}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Status:</span>
                <span className="text-xs">{server.status}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Tool Count:</span>
                <span className="text-xs">{server.toolCount}</span>
              </div>
              {server.cwd && (
                <div className="flex justify-between items-center text-sm">
                  <span className="text-muted-foreground">Working Directory:</span>
                  <div className="flex items-center gap-2">
                    <code className="font-mono bg-background px-2 py-1 rounded text-xs max-w-md truncate">
                      {server.cwd}
                    </code>
                    <Button size="sm" variant="ghost" onClick={() => copyToClipboard(server.cwd!)}>
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="p-4 bg-muted/50 rounded-lg space-y-3">
            <h3 className="font-normal text-sm">Description</h3>
            <p className="text-sm text-muted-foreground">{server.description}</p>
          </div>
        </TabsContent>

        {/* Tools Tab */}
        <TabsContent value="tools" className="flex-1 overflow-auto mt-0 min-h-0">
          <div className="p-4 bg-muted/50 rounded-lg space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-normal text-sm flex items-center gap-2">
                <Wrench className="h-3.5 w-3.5" />
                Available Tools ({filteredTools.length})
              </h3>
              <Button size="sm" onClick={loadTools} disabled={toolsLoading || server.status !== 'running'}>
                <RotateCw className={cn("h-3 w-3 mr-1.5", toolsLoading && "animate-spin")} />
                Refresh
              </Button>
            </div>

            {server.status !== 'running' ? (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Server must be running to discover tools. Start the server to see available tools.
                </AlertDescription>
              </Alert>
            ) : toolsLoading ? (
              <div className="text-sm text-muted-foreground">Loading tools...</div>
            ) : tools.length === 0 ? (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  No tools found. This MCP server may not expose any tools.
                </AlertDescription>
              </Alert>
            ) : (
              <>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search tools..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>

                <ScrollArea className="h-96">
                  <div className="space-y-2">
                    {filteredTools.map((tool) => (
                      <Card
                        key={tool.name}
                        className="p-3 hover:bg-accent/50 cursor-pointer transition-colors"
                        onClick={() => setSelectedTool(tool)}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-mono text-sm font-medium">{tool.name}</h4>
                            {tool.description && (
                              <p className="text-xs text-muted-foreground mt-1">
                                {tool.description}
                              </p>
                            )}
                            {tool.inputSchema?.required && tool.inputSchema.required.length > 0 && (
                              <div className="flex gap-1 mt-2">
                                {tool.inputSchema.required.map((param) => (
                                  <Badge key={param} variant="outline" className="text-xs">
                                    {param}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </ScrollArea>
              </>
            )}
          </div>
        </TabsContent>

        {/* Playground Tab */}
        <TabsContent value="playground" className="flex-1 flex flex-col mt-0 min-h-0">
          <div className="p-4 bg-muted/50 rounded-lg space-y-3 flex-shrink-0">
            <h3 className="font-normal text-sm flex items-center gap-2">
              <PlayCircle className="h-3.5 w-3.5" />
              Test Tools Interactively
            </h3>

            {server.status !== 'running' ? (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Server must be running to test tools. Start the server to use the playground.
                </AlertDescription>
              </Alert>
            ) : tools.length === 0 ? (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  No tools available. Load tools from the Tools tab first.
                </AlertDescription>
              </Alert>
            ) : (
              <>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Select Tool</label>
                  <select
                    className="w-full p-2 bg-background border rounded-lg text-sm"
                    value={selectedTool?.name || ''}
                    onChange={(e) => {
                      const tool = tools.find((t) => t.name === e.target.value)
                      setSelectedTool(tool || null)
                      if (tool?.inputSchema?.properties) {
                        const defaultParams: Record<string, any> = {}
                        Object.keys(tool.inputSchema.properties).forEach((key) => {
                          defaultParams[key] = ''
                        })
                        setParameters(JSON.stringify(defaultParams, null, 2))
                      } else {
                        setParameters('{}')
                      }
                    }}
                  >
                    <option value="">-- Select a tool --</option>
                    {tools.map((tool) => (
                      <option key={tool.name} value={tool.name}>
                        {tool.name}
                      </option>
                    ))}
                  </select>
                </div>

                {selectedTool && (
                  <>
                    {selectedTool.description && (
                      <div className="p-2 bg-background rounded text-xs text-muted-foreground">
                        {selectedTool.description}
                      </div>
                    )}

                    <div className="space-y-2">
                      <label className="text-sm font-medium">Parameters (JSON)</label>
                      <Textarea
                        value={parameters}
                        onChange={(e) => setParameters(e.target.value)}
                        placeholder='{"param": "value"}'
                        className="font-mono text-xs h-32"
                      />
                    </div>

                    <Button onClick={executeTool} disabled={executing} className="w-full">
                      {executing ? (
                        <>
                          <RotateCw className="mr-2 h-3.5 w-3.5 animate-spin" />
                          Executing...
                        </>
                      ) : (
                        <>
                          <Play className="mr-2 h-3.5 w-3.5" />
                          Execute Tool
                        </>
                      )}
                    </Button>
                  </>
                )}
              </>
            )}
          </div>

          {/* Execution History */}
          {executions.length > 0 && (
            <div className="flex-1 min-h-0 mt-4">
              <h4 className="text-sm font-medium mb-2">Execution History</h4>
              <ScrollArea className="h-full">
                <div className="space-y-2">
                  {executions.map((exec, idx) => (
                    <Card key={idx} className="p-3">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h5 className="font-mono text-xs font-medium">{exec.toolName}</h5>
                          <p className="text-xs text-muted-foreground">
                            {new Date(exec.executedAt).toLocaleString()} • {exec.duration}ms
                          </p>
                        </div>
                        {exec.error ? (
                          <Badge variant="destructive" className="text-xs">Error</Badge>
                        ) : (
                          <Badge className="bg-primary text-primary-foreground text-xs">Success</Badge>
                        )}
                      </div>
                      <div className="space-y-2">
                        <div>
                          <p className="text-xs font-medium mb-1">Parameters:</p>
                          <pre className="text-xs bg-background p-2 rounded overflow-auto">
                            {JSON.stringify(exec.parameters, null, 2)}
                          </pre>
                        </div>
                        <div>
                          <p className="text-xs font-medium mb-1">Result:</p>
                          <pre className="text-xs bg-background p-2 rounded overflow-auto">
                            {exec.error || JSON.stringify(exec.result, null, 2)}
                          </pre>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs" className="flex-1 flex flex-col mt-0 min-h-0">
          <Card className="p-3 flex-1 flex flex-col min-h-0 overflow-hidden">
            <div className="flex items-center justify-between mb-2 flex-shrink-0">
              <h3 className="font-normal text-sm">Server Logs (Live)</h3>
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-1 text-xs cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoScroll}
                    onChange={(e) => setAutoScroll(e.target.checked)}
                    className="rounded"
                  />
                  Auto-scroll
                </label>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setLogs('')}
                  disabled={server.status !== 'running'}
                >
                  Clear
                </Button>
              </div>
            </div>
            <div className="flex-1 min-h-0 bg-black rounded overflow-hidden">
              <ScrollArea className="h-full">
                <pre className="p-3 text-green-400 font-mono text-xs whitespace-pre-wrap break-words">
                  {server.status === 'running'
                    ? (logs || 'Waiting for logs...')
                    : 'Server must be running to view logs'}
                  <div ref={logsEndRef} />
                </pre>
              </ScrollArea>
            </div>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="flex-1 overflow-auto mt-0 min-h-0 space-y-4">
          {/* Server Configuration */}
          <div className="p-4 bg-muted/50 rounded-lg space-y-3">
            <h3 className="font-normal text-sm flex items-center gap-2">
              <Settings className="h-3.5 w-3.5" />
              Server Configuration
            </h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Server Name</label>
                <Input
                  value={server.name}
                  disabled
                  className="font-mono text-xs"
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Command</label>
                <Input
                  value={server.command}
                  disabled
                  className="font-mono text-xs"
                />
              </div>
              {server.args && server.args.length > 0 && (
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">Arguments</label>
                  <Input
                    value={server.args.join(' ')}
                    disabled
                    className="font-mono text-xs"
                  />
                </div>
              )}
              {server.cwd && (
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">Working Directory</label>
                  <Input
                    value={server.cwd}
                    disabled
                    className="font-mono text-xs"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Environment Variables */}
          {server.env && Object.keys(server.env).length > 0 && (
            <div className="p-4 bg-muted/50 rounded-lg space-y-3">
              <h3 className="font-normal text-sm">Environment Variables</h3>
              <div className="space-y-2">
                {Object.entries(server.env).map(([key, value]) => (
                  <div key={key} className="grid grid-cols-2 gap-2">
                    <Input
                      value={key}
                      disabled
                      className="font-mono text-xs"
                      placeholder="KEY"
                    />
                    <Input
                      value={value}
                      disabled
                      className="font-mono text-xs"
                      placeholder="value"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Authentication Settings */}
          <div className="p-4 bg-muted/50 rounded-lg space-y-3">
            <h3 className="font-normal text-sm flex items-center gap-2">
              <Settings className="h-3.5 w-3.5" />
              Authentication & Security
            </h3>
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-xs">
                MCP servers use stdio-based communication. Authentication is handled at the process level through system permissions and does not require API keys.
              </AlertDescription>
            </Alert>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm py-2 border-b">
                <span className="text-muted-foreground">Protocol</span>
                <code className="font-mono text-xs">JSON-RPC 2.0 over stdio</code>
              </div>
              <div className="flex items-center justify-between text-sm py-2 border-b">
                <span className="text-muted-foreground">Transport</span>
                <code className="font-mono text-xs">Child Process (stdio)</code>
              </div>
              <div className="flex items-center justify-between text-sm py-2 border-b">
                <span className="text-muted-foreground">Security Model</span>
                <code className="font-mono text-xs">Process Isolation</code>
              </div>
              <div className="flex items-center justify-between text-sm py-2">
                <span className="text-muted-foreground">Encryption</span>
                <code className="font-mono text-xs">Not Required (Local)</code>
              </div>
            </div>
          </div>

          {/* Advanced Settings */}
          <div className="p-4 bg-muted/50 rounded-lg space-y-3">
            <h3 className="font-normal text-sm">Advanced Settings</h3>
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-xs cursor-pointer">
                <input type="checkbox" defaultChecked className="rounded" />
                <span>Auto-restart on failure</span>
              </label>
              <label className="flex items-center gap-2 text-xs cursor-pointer">
                <input type="checkbox" defaultChecked className="rounded" />
                <span>Enable debug logging</span>
              </label>
              <label className="flex items-center gap-2 text-xs cursor-pointer">
                <input type="checkbox" className="rounded" />
                <span>Persist tool cache</span>
              </label>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg space-y-3">
            <h3 className="font-normal text-sm text-destructive">Danger Zone</h3>
            <div className="space-y-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full text-destructive hover:text-destructive"
                onClick={() => {
                  if (confirm('Are you sure you want to reset this server configuration?')) {
                    alert('Reset functionality coming soon')
                  }
                }}
              >
                Reset Configuration
              </Button>
              <Button
                variant="destructive"
                size="sm"
                className="w-full"
                onClick={() => {
                  if (confirm(`Are you sure you want to delete ${server.name}? This action cannot be undone.`)) {
                    alert('Delete functionality coming soon')
                  }
                }}
              >
                <Trash2 className="h-3 w-3 mr-2" />
                Delete Server
              </Button>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
