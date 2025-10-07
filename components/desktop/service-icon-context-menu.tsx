"use client"

import React from "react"
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuTrigger,
} from "@/components/ui/context-menu"
import {
  ExternalLink,
  Play,
  Square,
  RotateCw,
  Trash2,
  Info,
  FileText,
} from "lucide-react"

interface ServiceIconContextMenuProps {
  children: React.ReactNode
  onAction: (action: string) => void
  serviceName: string
  isRunning?: boolean
  isStopped?: boolean
  isInstalling?: boolean
}

export function ServiceIconContextMenu({
  children,
  onAction,
  serviceName,
  isRunning = false,
  isStopped = false,
  isInstalling = false
}: ServiceIconContextMenuProps) {
  return (
    <ContextMenu>
      <ContextMenuTrigger asChild>
        {children}
      </ContextMenuTrigger>
      <ContextMenuContent className="w-56">
        <ContextMenuItem
          onSelect={() => onAction("open")}
          disabled={!isRunning}
        >
          <ExternalLink className="mr-2 h-4 w-4" />
          Open in New Tab
          <ContextMenuShortcut>Enter</ContextMenuShortcut>
        </ContextMenuItem>

        <ContextMenuSeparator />

        {isRunning ? (
          <ContextMenuItem onSelect={() => onAction("stop")}>
            <Square className="mr-2 h-4 w-4" />
            Stop Service
          </ContextMenuItem>
        ) : (
          <ContextMenuItem
            onSelect={() => onAction("start")}
            disabled={isInstalling}
          >
            <Play className="mr-2 h-4 w-4" />
            Start Service
          </ContextMenuItem>
        )}

        <ContextMenuItem
          onSelect={() => onAction("restart")}
          disabled={!isRunning}
        >
          <RotateCw className="mr-2 h-4 w-4" />
          Restart Service
        </ContextMenuItem>

        <ContextMenuSeparator />

        <ContextMenuItem onSelect={() => onAction("logs")}>
          <FileText className="mr-2 h-4 w-4" />
          View Logs
        </ContextMenuItem>

        <ContextMenuItem onSelect={() => onAction("properties")}>
          <Info className="mr-2 h-4 w-4" />
          Properties
        </ContextMenuItem>

        <ContextMenuSeparator />

        <ContextMenuItem
          onSelect={() => onAction("remove")}
          variant="destructive"
        >
          <Trash2 className="mr-2 h-4 w-4" />
          Remove Service
          <ContextMenuShortcut>Del</ContextMenuShortcut>
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  )
}
