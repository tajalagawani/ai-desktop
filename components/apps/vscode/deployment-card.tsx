"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Play,
  Square,
  RotateCw,
  Trash2,
  ExternalLink,
  FileText,
  AlertCircle,
  Check,
  Loader2,
  Database
} from "lucide-react"
import { DeploymentConfig } from "@/lib/deployment/types"
import { DeploymentLogs } from "./deployment-logs"
import { cn } from "@/lib/utils"
import { getFrameworkDisplayName } from "@/lib/deployment/detector"
import { toast } from "sonner"

interface DeploymentCardProps {
  deployment: DeploymentConfig
  onUpdate: () => void
}

export function DeploymentCard({ deployment, onUpdate }: DeploymentCardProps) {
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [showBuildLogs, setShowBuildLogs] = useState(false)
  const [showRuntimeLogs, setShowRuntimeLogs] = useState(false)

  const handleAction = async (action: string) => {
    setActionLoading(action)
    try {
      const response = await fetch(`/api/deployments/${deployment.id}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action })
      })

      const result = await response.json()

      if (!result.success) {
        throw new Error(result.error || "Action failed")
      }

      toast.success(result.message)
      onUpdate()
    } catch (error: any) {
      toast.error(error.message || `Failed to ${action}`)
    } finally {
      setActionLoading(null)
    }
  }

  const getStatusBadge = () => {
    switch (deployment.status) {
      case 'running':
        return (
          <Badge className="bg-green-600 hover:bg-green-700">
            <Check className="mr-1 h-3 w-3" />
            Running
          </Badge>
        )
      case 'stopped':
        return (
          <Badge variant="secondary">
            <Square className="mr-1 h-3 w-3" />
            Stopped
          </Badge>
        )
      case 'building':
      case 'deploying':
        return (
          <Badge className="bg-blue-600 hover:bg-blue-700">
            <Loader2 className="mr-1 h-3 w-3 animate-spin" />
            {deployment.status === 'building' ? 'Building' : 'Deploying'}
          </Badge>
        )
      case 'failed':
        return (
          <Badge variant="destructive">
            <AlertCircle className="mr-1 h-3 w-3" />
            Failed
          </Badge>
        )
      default:
        return <Badge variant="outline">{deployment.status}</Badge>
    }
  }

  const accessUrl = deployment.domain
    ? `https://${deployment.domain}`
    : `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:${deployment.port}`

  return (
    <Card className="p-4">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-medium">{deployment.repoName}</h3>
              {getStatusBadge()}
            </div>
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <span>{getFrameworkDisplayName(deployment.framework)}</span>
              <span>•</span>
              <span>Port {deployment.port}</span>
              {deployment.services.length > 0 && (
                <>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Database className="h-3 w-3" />
                    {deployment.services.length} service{deployment.services.length > 1 ? 's' : ''}
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-1.5">
            {deployment.status === 'running' && (
              <>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => window.open(accessUrl, '_blank')}
                  title="Open in browser"
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleAction('stop')}
                  disabled={actionLoading === 'stop'}
                  title="Stop"
                >
                  {actionLoading === 'stop' ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Square className="h-3.5 w-3.5" />
                  )}
                </Button>
              </>
            )}

            {deployment.status === 'stopped' && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleAction('start')}
                disabled={actionLoading === 'start'}
                title="Start"
              >
                {actionLoading === 'start' ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Play className="h-3.5 w-3.5" />
                )}
              </Button>
            )}

            {(deployment.status === 'running' || deployment.status === 'stopped') && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleAction('restart')}
                disabled={actionLoading === 'restart'}
                title="Restart"
              >
                <RotateCw className={cn("h-3.5 w-3.5", actionLoading === 'restart' && "animate-spin")} />
              </Button>
            )}

            <Button
              size="sm"
              variant="outline"
              onClick={() => handleAction('delete')}
              disabled={actionLoading === 'delete'}
              title="Delete"
            >
              {actionLoading === 'delete' ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Trash2 className="h-3.5 w-3.5" />
              )}
            </Button>
          </div>
        </div>

        {/* Error Message */}
        {deployment.error && (
          <div className="p-2 bg-destructive/10 border border-destructive/20 rounded text-xs text-destructive">
            {deployment.error}
          </div>
        )}

        {/* Access URL */}
        {deployment.status === 'running' && (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground">Access:</span>
            <code className="flex-1 px-2 py-1 bg-muted rounded text-xs">
              {accessUrl}
            </code>
          </div>
        )}

        {/* Logs Buttons */}
        <div className="flex gap-2">
          <Button
            size="sm"
            variant={showBuildLogs ? "default" : "outline"}
            onClick={() => {
              setShowBuildLogs(!showBuildLogs)
              setShowRuntimeLogs(false)
            }}
            className="flex-1"
          >
            <FileText className="mr-1.5 h-3.5 w-3.5" />
            Build Logs
          </Button>
          {(deployment.status === 'running' || deployment.status === 'stopped') && (
            <Button
              size="sm"
              variant={showRuntimeLogs ? "default" : "outline"}
              onClick={() => {
                setShowRuntimeLogs(!showRuntimeLogs)
                setShowBuildLogs(false)
              }}
              className="flex-1"
            >
              <FileText className="mr-1.5 h-3.5 w-3.5" />
              Runtime Logs
            </Button>
          )}
        </div>

        {/* Logs Viewer */}
        {showBuildLogs && (
          <div className="h-64">
            <DeploymentLogs
              deploymentId={deployment.id}
              type="build"
              onClose={() => setShowBuildLogs(false)}
            />
          </div>
        )}

        {showRuntimeLogs && (
          <div className="h-64">
            <DeploymentLogs
              deploymentId={deployment.id}
              type="runtime"
              onClose={() => setShowRuntimeLogs(false)}
            />
          </div>
        )}
      </div>
    </Card>
  )
}
