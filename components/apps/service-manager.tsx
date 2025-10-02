"use client"

import React, { useEffect, useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Widget } from "@/components/desktop/widget"
import { INSTALLABLE_SERVICES, SERVICE_CATEGORIES, ServiceConfig } from "@/data/installable-services"
import { getIcon } from "@/utils/icon-mapper"
import { Play, Square, RotateCw, Trash2, Download, ExternalLink, Terminal, Eye } from "lucide-react"
import { ServiceViewer } from "./service-viewer"

interface ServiceWithStatus extends ServiceConfig {
  installed: boolean
  status: string
  containerName: string
}

interface ServiceManagerProps {
  openWindow?: (id: string, title: string, component: React.ReactNode) => void
  toggleMaximizeWindow?: (id: string) => void
  bringToFront?: (id: string) => void
}

export function ServiceManager({ openWindow, toggleMaximizeWindow, bringToFront }: ServiceManagerProps) {
  const [services, setServices] = useState<ServiceWithStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [dockerInstalled, setDockerInstalled] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [actionLoading, setActionLoading] = useState<string | null>(null)

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

      // Reload services to update status
      await loadServices()
    } catch (error: any) {
      console.error('Service action error:', error)
      alert(error.message || 'Failed to perform action')
    } finally {
      setActionLoading(null)
    }
  }

  const filteredServices = selectedCategory === 'all'
    ? services
    : services.filter(s => s.category === selectedCategory)

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return <Badge className="bg-green-500">Running</Badge>
      case 'exited':
        return <Badge variant="secondary">Stopped</Badge>
      case 'not-installed':
        return <Badge variant="outline">Not Installed</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">Loading services...</p>
      </div>
    )
  }

  if (!dockerInstalled) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <h2 className="text-2xl font-bold mb-4">Docker Required</h2>
        <p className="text-muted-foreground mb-6 text-center max-w-md">
          Docker is required to install and manage services. Please install Docker on your VPS first.
        </p>
        <Button asChild>
          <a href="https://docs.docker.com/engine/install/" target="_blank" rel="noopener noreferrer">
            Install Docker
          </a>
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Service Manager</h1>
            <p className="text-sm text-muted-foreground">Install and manage VPS services</p>
          </div>
          <Button onClick={loadServices} variant="outline" size="sm">
            <RotateCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Category Tabs */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="flex-1 flex flex-col">
        <div className="border-b px-6">
          <TabsList className="w-full justify-start">
            <TabsTrigger value="all">All Services</TabsTrigger>
            {SERVICE_CATEGORIES.map(cat => (
              <TabsTrigger key={cat.id} value={cat.id}>
                {cat.name}
              </TabsTrigger>
            ))}
          </TabsList>
        </div>

        <TabsContent value={selectedCategory} className="flex-1 overflow-auto p-6 mt-0">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredServices.map(service => {
              const Icon = getIcon(service.icon)
              const isLoading = actionLoading === service.id

              return (
                <Widget key={service.id} icon={Icon} title={service.name}>
                  <div className="space-y-3">
                    {/* Status Badge */}
                    <div className="flex items-center justify-between">
                      {getStatusBadge(service.status)}
                      <span className="text-xs text-muted-foreground">
                        {service.category}
                      </span>
                    </div>

                    {/* Description */}
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {service.description}
                    </p>

                    {/* Credentials (if installed) */}
                    {service.installed && service.defaultCredentials && (
                      <div className="text-xs space-y-1 p-2 bg-muted/50 rounded">
                        {service.defaultCredentials.port && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Port:</span>
                            <span className="font-mono">{service.defaultCredentials.port}</span>
                          </div>
                        )}
                        {service.defaultCredentials.username && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">User:</span>
                            <span className="font-mono">{service.defaultCredentials.username}</span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex flex-col gap-2 pt-2">
                      {!service.installed ? (
                        <Button
                          size="sm"
                          className="w-full"
                          onClick={() => handleServiceAction(service.id, 'install')}
                          disabled={isLoading}
                        >
                          <Download className="h-3 w-3 mr-2" />
                          {isLoading ? 'Installing...' : 'Install'}
                        </Button>
                      ) : (
                        <>
                          <Button
                            size="sm"
                            variant="secondary"
                            className="w-full"
                            onClick={() => {
                              if (openWindow && toggleMaximizeWindow && bringToFront) {
                                const windowId = `service-${service.id}`
                                openWindow(
                                  windowId,
                                  service.name,
                                  <ServiceViewer service={service} />
                                )
                                // Maximize and bring to front after a short delay
                                setTimeout(() => {
                                  toggleMaximizeWindow(windowId)
                                  bringToFront(windowId)
                                }, 100)
                              }
                            }}
                          >
                            <Eye className="h-3 w-3 mr-2" />
                            Open Dashboard
                          </Button>

                          <div className="flex gap-2">
                            {service.status === 'running' ? (
                              <Button
                                size="sm"
                                variant="destructive"
                                className="flex-1"
                                onClick={() => handleServiceAction(service.id, 'stop')}
                                disabled={isLoading}
                              >
                                <Square className="h-3 w-3 mr-1" />
                                Stop
                              </Button>
                            ) : (
                              <Button
                                size="sm"
                                variant="default"
                                className="flex-1"
                                onClick={() => handleServiceAction(service.id, 'start')}
                                disabled={isLoading}
                              >
                                <Play className="h-3 w-3 mr-1" />
                                Start
                              </Button>
                            )}

                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleServiceAction(service.id, 'restart')}
                              disabled={isLoading}
                              title="Restart"
                            >
                              <RotateCw className="h-3 w-3" />
                            </Button>

                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleServiceAction(service.id, 'remove')}
                              disabled={isLoading}
                              title="Remove"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </Widget>
              )
            })}
          </div>

          {filteredServices.length === 0 && (
            <div className="flex items-center justify-center h-64">
              <p className="text-muted-foreground">No services in this category</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
