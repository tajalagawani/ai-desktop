"use client"

import React, { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Copy, ExternalLink, Terminal, Database, Key, Globe } from "lucide-react"
import { ServiceConfig } from "@/data/installable-services"

interface ServiceViewerProps {
  service: ServiceConfig & {
    installed: boolean
    status: string
    containerName: string
  }
}

export function ServiceViewer({ service }: ServiceViewerProps) {
  const [logs, setLogs] = useState<string>("")
  const [loading, setLoading] = useState(false)

  const loadLogs = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/services', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'logs', serviceId: service.id })
      })
      const data = await response.json()
      if (data.success) {
        setLogs(data.logs)
      }
    } catch (error) {
      console.error('Failed to load logs:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (service.status === 'running') {
      loadLogs()
    }
  }, [service.status])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const getAccessUrl = () => {
    const port = service.ports?.[0]
    if (!port) return null
    return `http://${window.location.hostname}:${port}`
  }

  const getConnectionString = () => {
    const { id, defaultCredentials } = service
    const host = window.location.hostname
    const port = defaultCredentials?.port || service.ports?.[0]
    const user = defaultCredentials?.username || 'root'
    const pass = defaultCredentials?.password || 'changeme'

    switch (id) {
      case 'mysql':
      case 'mariadb':
        return `mysql -h ${host} -P ${port} -u ${user} -p${pass}`
      case 'postgresql':
        return `psql -h ${host} -p ${port} -U ${user} -d postgres`
      case 'mongodb':
        return `mongodb://${host}:${port}`
      case 'redis':
        return `redis-cli -h ${host} -p ${port}`
      case 'neo4j':
        return `bolt://${host}:7687`
      default:
        return null
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Database className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-normal">{service.name}</h1>
              <p className="text-sm text-muted-foreground">{service.description}</p>
            </div>
          </div>
          <Badge className={service.status === 'running' ? 'bg-green-500' : 'bg-gray-500'}>
            {service.status}
          </Badge>
        </div>
      </div>

      <Tabs defaultValue="access" className="flex-1 flex flex-col">
        <div className="border-b px-6">
          <TabsList>
            <TabsTrigger value="access">Access Info</TabsTrigger>
            <TabsTrigger value="config">Configuration</TabsTrigger>
            <TabsTrigger value="logs">Logs</TabsTrigger>
            {getAccessUrl() && <TabsTrigger value="ui">Web UI</TabsTrigger>}
          </TabsList>
        </div>

        {/* Access Info Tab */}
        <TabsContent value="access" className="flex-1 overflow-auto p-6 space-y-4">
          {/* Connection Details */}
          <Card className="p-4">
            <h3 className="font-normal mb-3 flex items-center gap-2">
              <Key className="h-4 w-4" />
              Connection Details
            </h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-muted rounded">
                <span className="text-sm">Host:</span>
                <div className="flex items-center gap-2">
                  <code className="text-sm">{window.location.hostname}</code>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-6 w-6 p-0"
                    onClick={() => copyToClipboard(window.location.hostname)}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </div>

              {service.ports?.map(port => (
                <div key={port} className="flex items-center justify-between p-2 bg-muted rounded">
                  <span className="text-sm">Port:</span>
                  <div className="flex items-center gap-2">
                    <code className="text-sm">{port}</code>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-6 w-6 p-0"
                      onClick={() => copyToClipboard(port.toString())}
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}

              {service.defaultCredentials?.username && (
                <div className="flex items-center justify-between p-2 bg-muted rounded">
                  <span className="text-sm">Username:</span>
                  <div className="flex items-center gap-2">
                    <code className="text-sm">{service.defaultCredentials.username}</code>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-6 w-6 p-0"
                      onClick={() => copyToClipboard(service.defaultCredentials!.username!)}
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              )}

              {service.defaultCredentials?.password && (
                <div className="flex items-center justify-between p-2 bg-muted rounded">
                  <span className="text-sm">Password:</span>
                  <div className="flex items-center gap-2">
                    <code className="text-sm">{service.defaultCredentials.password}</code>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-6 w-6 p-0"
                      onClick={() => copyToClipboard(service.defaultCredentials!.password!)}
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* CLI Command */}
          {getConnectionString() && (
            <Card className="p-4">
              <h3 className="font-normal mb-3 flex items-center gap-2">
                <Terminal className="h-4 w-4" />
                CLI Connection
              </h3>
              <div className="flex items-center gap-2 p-3 bg-muted rounded font-mono text-sm">
                <code className="flex-1">{getConnectionString()}</code>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => copyToClipboard(getConnectionString()!)}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </Card>
          )}

          {/* Access URL */}
          {getAccessUrl() && (
            <Card className="p-4">
              <h3 className="font-normal mb-3 flex items-center gap-2">
                <Globe className="h-4 w-4" />
                Web Access
              </h3>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={getAccessUrl()!}
                  readOnly
                  className="flex-1 p-2 bg-muted rounded text-sm"
                />
                <Button
                  size="sm"
                  onClick={() => copyToClipboard(getAccessUrl()!)}
                >
                  <Copy className="h-4 w-4 mr-2" />
                  Copy
                </Button>
                <Button
                  size="sm"
                  onClick={() => window.open(getAccessUrl()!, '_blank')}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open
                </Button>
              </div>
            </Card>
          )}

          {/* Environment Variables */}
          {service.environment && Object.keys(service.environment).length > 0 && (
            <Card className="p-4">
              <h3 className="font-normal mb-3">Environment Variables</h3>
              <div className="space-y-2">
                {Object.entries(service.environment).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between p-2 bg-muted rounded">
                    <code className="text-sm font-normal">{key}</code>
                    <code className="text-sm text-muted-foreground">{value}</code>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </TabsContent>

        {/* Configuration Tab */}
        <TabsContent value="config" className="flex-1 overflow-auto p-6 space-y-4">
          <Card className="p-4">
            <h3 className="font-normal mb-3">Docker Configuration</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between py-2 border-b">
                <span className="text-muted-foreground">Container Name:</span>
                <code>{service.containerName}</code>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-muted-foreground">Image:</span>
                <code>{service.dockerImage}</code>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-muted-foreground">Volumes:</span>
                <code>{service.volumes?.join(', ') || 'None'}</code>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Method:</span>
                <code>{service.installMethod}</code>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs" className="flex-1 overflow-auto p-6">
          <Card className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-normal">Container Logs</h3>
              <Button size="sm" onClick={loadLogs} disabled={loading}>
                Refresh
              </Button>
            </div>
            <pre className="p-4 bg-black text-green-400 rounded font-mono text-xs overflow-auto max-h-96">
              {logs || 'No logs available'}
            </pre>
          </Card>
        </TabsContent>

        {/* Web UI Tab */}
        {getAccessUrl() && (
          <TabsContent value="ui" className="flex-1 p-0">
            <iframe
              src={getAccessUrl()!}
              className="w-full h-full border-0"
              title={`${service.name} Web UI`}
            />
          </TabsContent>
        )}
      </Tabs>
    </div>
  )
}
