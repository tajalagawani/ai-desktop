"use client"

import React from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Play, Square, RotateCw, Circle, Zap, Network } from "lucide-react"
import { cn } from "@/lib/utils"

interface FlowConfig {
  name: string
  port: number
  mode: "agent" | "miniact" | "waiting"
  agent_name?: string
  description?: string
  file: string
  auto_assigned?: boolean
  container?: {
    running: boolean
    status: string
    started_at?: string
    pid?: number
  }
  health?: {
    status: string
    port?: number
  }
}

interface FlowListItemProps {
  flow: FlowConfig
  actionLoading: string | null
  onSelect: (flow: FlowConfig) => void
  onAction: (flowName: string, action: string) => void
}

export const FlowListItem = React.memo(({ flow, actionLoading, onSelect, onAction }: FlowListItemProps) => {
  return (
    <div
      onClick={() => onSelect(flow)}
      className="flex items-center gap-4 p-4 rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 flex-shrink-0">
        {flow.mode === 'agent' ? (
          <Network className="w-6 h-6 text-primary" />
        ) : (
          <Zap className="w-6 h-6 text-primary" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="font-normal">{flow.agent_name || flow.name}</h3>
          {flow.auto_assigned && (
            <Badge className="text-[10px] bg-foreground text-background border-0 px-1.5 py-0.5">Auto</Badge>
          )}
        </div>
        {flow.description && (
          <p className="text-sm text-muted-foreground mb-1 max-w-md">
            {flow.description}
          </p>
        )}
        <div className="flex items-center gap-1.5">
          <Badge className="text-[10px] font-normal bg-foreground text-background border-0 px-1.5 py-0.5">
            {flow.mode === 'agent' ? 'Agent Mode' : flow.mode === 'miniact' ? 'MiniACT Mode' : 'Waiting'}
          </Badge>
          <Badge className="text-[10px] font-normal bg-foreground text-background border-0 px-1.5 py-0.5">
            Port {flow.port}
          </Badge>
        </div>
      </div>

      {/* Status Badge & Action Buttons */}
      <div className="flex items-center gap-2 flex-shrink-0">
        {flow.container?.running ? (
          <>
            {flow.health?.status === 'healthy' ? (
              <Badge className="bg-primary text-primary-foreground hover:bg-primary/90">
                <Circle className="mr-1 h-2 w-2 fill-green-500 text-green-500" />
                Running
              </Badge>
            ) : (
              <Badge variant="secondary">
                <Circle className="mr-1 h-2 w-2 fill-red-500 text-red-500" />
                Unhealthy
              </Badge>
            )}
            <Button
              size="sm"
              variant="outline"
              onClick={(e) => {
                e.stopPropagation()
                onAction(flow.name, 'stop')
              }}
              disabled={actionLoading === flow.name}
              title="Stop flow"
            >
              {actionLoading === flow.name ? (
                <RotateCw className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Square className="h-3.5 w-3.5" />
              )}
            </Button>
          </>
        ) : (
          <>
            <Badge variant="secondary">
              <Circle className="mr-1 h-2 w-2 fill-gray-400 text-gray-400" />
              Stopped
            </Badge>
            <Button
              size="sm"
              variant="outline"
              onClick={(e) => {
                e.stopPropagation()
                onAction(flow.name, 'start')
              }}
              disabled={actionLoading === flow.name}
              title="Start flow"
            >
              {actionLoading === flow.name ? (
                <RotateCw className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Play className="h-3.5 w-3.5" />
              )}
            </Button>
          </>
        )}
        <Button
          size="sm"
          variant="outline"
          onClick={(e) => {
            e.stopPropagation()
            onAction(flow.name, 'restart')
          }}
          disabled={actionLoading === flow.name}
          title="Restart flow"
        >
          <RotateCw className={cn("h-3.5 w-3.5", actionLoading === flow.name && "animate-spin")} />
        </Button>
      </div>
    </div>
  )
})

FlowListItem.displayName = 'FlowListItem'
