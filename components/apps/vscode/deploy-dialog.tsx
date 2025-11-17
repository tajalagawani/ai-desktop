"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2, Rocket, Database, Server } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { toast } from "sonner"
import { Checkbox } from "@/components/ui/checkbox"

interface DeployDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onDeployComplete: () => void
  repoId: string
  repoName: string
  repoPath: string
}

interface RunningService {
  id: string
  name: string
  containerName: string
  port: number
  type: string
  connectionString: string
}

export function DeployDialog({
  open,
  onOpenChange,
  onDeployComplete,
  repoId,
  repoName,
  repoPath
}: DeployDialogProps) {
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
    if (open) {
      loadServices()
    }
  }, [open])

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
      onOpenChange(false)

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
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Rocket className="h-5 w-5" />
            Deploy {repoName}
          </DialogTitle>
          <DialogDescription>
            Configure deployment settings and connect to services
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Running Services */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              <Label className="font-medium">Connect to Services</Label>
            </div>

            {loadingServices ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading services...
              </div>
            ) : services.length === 0 ? (
              <Alert>
                <AlertDescription className="text-sm">
                  No running services found. Start a database or service from the Service Manager first.
                </AlertDescription>
              </Alert>
            ) : (
              <div className="space-y-2 border rounded-lg p-3 bg-muted/30">
                {services.map((service) => (
                  <div key={service.containerName} className="flex items-center space-x-3 p-2 hover:bg-muted/50 rounded">
                    <Checkbox
                      id={service.containerName}
                      checked={selectedServices.includes(service.containerName)}
                      onCheckedChange={() => handleServiceToggle(service.containerName)}
                    />
                    <div className="flex-1">
                      <Label htmlFor={service.containerName} className="font-medium cursor-pointer flex items-center gap-2">
                        <Server className="h-3.5 w-3.5" />
                        {service.name}
                      </Label>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {service.connectionString}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Environment Variables */}
          <div className="space-y-3">
            <Label className="font-medium">Environment Variables</Label>

            {Object.keys(envVars).length > 0 && (
              <div className="space-y-1.5 border rounded-lg p-3 bg-muted/30">
                {Object.entries(envVars).map(([key, value]) => (
                  <div key={key} className="flex items-center gap-2 text-sm">
                    <code className="flex-1 px-2 py-1 bg-background rounded font-mono text-xs">
                      {key}={value}
                    </code>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeEnvVar(key)}
                      className="h-7 px-2"
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
                className="font-mono text-sm"
              />
              <Input
                placeholder="value"
                value={newEnvValue}
                onChange={(e) => setNewEnvValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addEnvVar()}
                className="font-mono text-sm"
              />
              <Button variant="outline" onClick={addEnvVar} disabled={!newEnvKey || !newEnvValue}>
                Add
              </Button>
            </div>
          </div>

          {/* Domain (Optional) */}
          <div className="space-y-2">
            <Label htmlFor="domain">Custom Domain (Optional)</Label>
            <Input
              id="domain"
              placeholder="example.com"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Leave empty to use default port access
            </p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={deploying}>
            Cancel
          </Button>
          <Button onClick={handleDeploy} disabled={deploying}>
            {deploying && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {deploying ? "Deploying..." : "Deploy"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
