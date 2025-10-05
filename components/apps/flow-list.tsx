"use client"

import React from "react"
import { FlowListItem } from "./flow-list-item"

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

interface FlowListProps {
  flows: FlowConfig[]
  actionLoading: string | null
  onSelectFlow: (flow: FlowConfig) => void
  onFlowAction: (flowName: string, action: string) => void
}

export const FlowList = React.memo(({ flows, actionLoading, onSelectFlow, onFlowAction }: FlowListProps) => {
  return (
    <div className="flex-1 min-h-0 overflow-y-scroll overflow-x-hidden pr-4 scrollbar-thin will-change-scroll">
      <div className="space-y-3">
        {flows.map((flow) => (
          <FlowListItem
            key={flow.name}
            flow={flow}
            actionLoading={actionLoading}
            onSelect={onSelectFlow}
            onAction={onFlowAction}
          />
        ))}
      </div>
    </div>
  )
})

FlowList.displayName = 'FlowList'
