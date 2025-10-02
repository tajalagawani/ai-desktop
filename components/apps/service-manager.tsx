"use client"

import React, { useEffect, useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
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
}

export function ServiceManager({ openWindow }: ServiceManagerProps) {
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredServices.map(service => {
              const Icon = getIcon(service.icon)
              const isLoading = actionLoading === service.id

              return (
                <Card key={service.id} className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold">{service.name}</h3>
                        {getStatusBadge(service.status)}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">{service.description}</p>

                      {service.installed && service.defaultCredentials && (
                        <div className="mt-2 text-xs text-muted-foreground">
                          {service.defaultCredentials.port && (
                            <div>Port: {service.defaultCredentials.port}</div>
                          )}
                          {service.defaultCredentials.username && (
                            <div>User: {service.defaultCredentials.username}</div>
                          )}
                        </div>
                      )}

                      <Separator className="my-3" />

                      <div className="flex items-center gap-2 flex-wrap">
                        {!service.installed ? (
                          <Button
                            size="sm"
                            onClick={() => handleServiceAction(service.id, 'install')}
                            disabled={isLoading}
                          >
                            <Download className="h-3 w-3 mr-2" />
                            Install
                          </Button>
                        ) : (
                          <>
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => {
                                if (openWindow) {
                                  openWindow(
                                    `service-${service.id}`,
                                    service.name,
                                    <ServiceViewer service={service} />
                                  )
                                }
                              }}
                            >
                              <Eye className="h-3 w-3 mr-2" />
                              Open
                            </Button>

                            {service.status === 'running' ? (
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => handleServiceAction(service.id, 'stop')}
                                disabled={isLoading}
                              >
                                <Square className="h-3 w-3 mr-2" />
                                Stop
                              </Button>
                            ) : (
                              <Button
                                size="sm"
                                variant="default"
                                onClick={() => handleServiceAction(service.id, 'start')}
                                disabled={isLoading}
                              >
                                <Play className="h-3 w-3 mr-2" />
                                Start
                              </Button>
                            )}

                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleServiceAction(service.id, 'restart')}
                              disabled={isLoading}
                            >
                              <RotateCw className="h-3 w-3" />
                            </Button>

                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleServiceAction(service.id, 'remove')}
                              disabled={isLoading}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
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
