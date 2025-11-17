"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2, Database, Server, Rocket } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { toast } from "sonner"
import { Checkbox } from "@/components/ui/checkbox"
import { Card } from "@/components/ui/card"

interface DeployConfigProps {
  repoId: string
  repoName: string
  repoPath: string
  onDeployComplete: () => void
}

interface RunningService {
  id: string
  name: string
  containerName: string
  port: number
  type: string
  connectionString: string
}

export function DeployConfig({
  repoId,
  repoName,
  repoPath,
  onDeployComplete
}: DeployConfigProps) {
  const [deploying, setDeploying] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [services, setServices] = useState<RunningService[]>([])
  const [selectedServices, setSelectedServices] = useState<string[]>([])
  const [envVars, setEnvVars] = useState<Record<string, string>>({})
  const [newEnvKey, setNewEnvKey] = useState("")
  const [newEnvValue, setNewEnvValue] = useState("")
  const [domain, setDomain] = useState("")
  const [loadingServices, setLoadingServices] = useState(true)

  // Load running services
  useEffect(() => {
    loadServices()
  }, [])

  const loadServices = async () => {
    setLoadingServices(true)
    try {
      const response = await fetch('/api/deployments/services')
      const data = await response.json()
      if (data.success) {
        setServices(data.services || [])
      }
    } catch (error) {
      console.error('Error loading services:', error)
    } finally {
      setLoadingServices(false)
    }
  }

  const handleServiceToggle = (containerName: string) => {
    setSelectedServices(prev =>
      prev.includes(containerName)
        ? prev.filter(s => s !== containerName)
        : [...prev, containerName]
    )
  }

  const addEnvVar = () => {
    if (newEnvKey && newEnvValue) {
      setEnvVars(prev => ({ ...prev, [newEnvKey]: newEnvValue }))
      setNewEnvKey("")
      setNewEnvValue("")
    }
  }

  const removeEnvVar = (key: string) => {
    setEnvVars(prev => {
      const updated = { ...prev }
      delete updated[key]
      return updated
    })
  }

  const handleDeploy = async () => {
    setDeploying(true)
    setError(null)

    try {
      const response = await fetch("/api/deployments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repoId,
          repoName,
          repoPath,
          selectedServices,
          customEnvVars: envVars,
          domain: domain || undefined
        }),
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.error || "Failed to deploy")
      }

      toast.success(`Deployment started for ${repoName}!`)
      onDeployComplete()

      // Reset form
      setSelectedServices([])
      setEnvVars({})
      setDomain("")
    } catch (error: any) {
      setError(error.message || "Failed to deploy")
      toast.error(error.message || "Failed to deploy")
    } finally {
      setDeploying(false)
    }
  }

  return (
    <Card className="p-4">
      <div className="space-y-4">
        {/* Running Services */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            <Label className="font-medium text-sm">Connect to Services</Label>
          </div>

          {loadingServices ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading services...
            </div>
          ) : services.length === 0 ? (
            <Alert>
              <AlertDescription className="text-xs">
                No running services found. Start a database or service from the Service Manager first.
              </AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-1.5 border rounded-lg p-2 bg-muted/30 max-h-48 overflow-y-auto">
              {services.map((service) => (
                <div key={service.containerName} className="flex items-center space-x-2 p-1.5 hover:bg-muted/50 rounded">
                  <Checkbox
                    id={service.containerName}
                    checked={selectedServices.includes(service.containerName)}
                    onCheckedChange={() => handleServiceToggle(service.containerName)}
                  />
                  <div className="flex-1">
                    <Label htmlFor={service.containerName} className="font-normal cursor-pointer flex items-center gap-1.5 text-xs">
                      <Server className="h-3 w-3" />
                      {service.name}
                    </Label>
                    <p className="text-xs text-muted-foreground truncate">
                      {service.connectionString}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Environment Variables */}
        <div className="space-y-2">
          <Label className="font-medium text-sm">Environment Variables</Label>

          {Object.keys(envVars).length > 0 && (
            <div className="space-y-1 border rounded-lg p-2 bg-muted/30 max-h-32 overflow-y-auto">
              {Object.entries(envVars).map(([key, value]) => (
                <div key={key} className="flex items-center gap-2 text-xs">
                  <code className="flex-1 px-2 py-1 bg-background rounded font-mono text-xs truncate">
                    {key}={value}
                  </code>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeEnvVar(key)}
                    className="h-6 px-2 text-xs"
                  >
                    Remove
                  </Button>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2">
            <Input
              placeholder="KEY"
              value={newEnvKey}
              onChange={(e) => setNewEnvKey(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addEnvVar()}
              className="font-mono text-xs h-8"
            />
            <Input
              placeholder="value"
              value={newEnvValue}
              onChange={(e) => setNewEnvValue(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addEnvVar()}
              className="font-mono text-xs h-8"
            />
            <Button variant="outline" size="sm" onClick={addEnvVar} disabled={!newEnvKey || !newEnvValue} className="h-8">
              Add
            </Button>
          </div>
        </div>

        {/* Domain (Optional) */}
        <div className="space-y-2">
          <Label htmlFor="domain" className="text-sm">Custom Domain (Optional)</Label>
          <Input
            id="domain"
            placeholder="example.com"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="text-xs h-8"
          />
          <p className="text-xs text-muted-foreground">
            Leave empty to use default port access
          </p>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertDescription className="text-xs">{error}</AlertDescription>
          </Alert>
        )}

        <Button onClick={handleDeploy} disabled={deploying} className="w-full" size="sm">
          {deploying && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          <Rocket className="mr-2 h-3.5 w-3.5" />
          {deploying ? "Deploying..." : "Deploy to VPS"}
        </Button>
      </div>
    </Card>
  )
}
