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
  Play,
  Pause,
  Edit3,
  Trash2,
  Copy,
  Info,
  Settings,
  Pin,
  PinOff,
  Download
} from "lucide-react"

interface DesktopIconContextMenuProps {
  children: React.ReactNode
  onAction: (action: string, appId: string) => void
  appId: string
  appName: string
  isRunning?: boolean
  isPinned?: boolean
}

export function DesktopIconContextMenu({ 
  children, 
  onAction, 
  appId, 
  appName, 
  isRunning = false,
  isPinned = false 
}: DesktopIconContextMenuProps) {
  return (
    <ContextMenu>
      <ContextMenuTrigger asChild>
        {children}
      </ContextMenuTrigger>
      <ContextMenuContent className="w-56">
        <ContextMenuItem onSelect={() => onAction("open", appId)}>
          <Play className="mr-2 h-4 w-4" />
          Open
          <ContextMenuShortcut>Enter</ContextMenuShortcut>
        </ContextMenuItem>
        
        {isRunning ? (
          <ContextMenuItem onSelect={() => onAction("pause", appId)}>
            <Pause className="mr-2 h-4 w-4" />
            Pause
          </ContextMenuItem>
        ) : (
          <ContextMenuItem onSelect={() => onAction("resume", appId)}>
            <Play className="mr-2 h-4 w-4" />
            Resume
          </ContextMenuItem>
        )}
        
        <ContextMenuSeparator />
        
        <ContextMenuItem onSelect={() => onAction("rename", appId)}>
          <Edit3 className="mr-2 h-4 w-4" />
          Rename
          <ContextMenuShortcut>F2</ContextMenuShortcut>
        </ContextMenuItem>
        
        <ContextMenuItem onSelect={() => onAction("copy", appId)}>
          <Copy className="mr-2 h-4 w-4" />
          Copy
          <ContextMenuShortcut>Ctrl+C</ContextMenuShortcut>
        </ContextMenuItem>
        
        <ContextMenuSeparator />
        
        {isPinned ? (
          <ContextMenuItem onSelect={() => onAction("unpin", appId)}>
            <PinOff className="mr-2 h-4 w-4" />
            Unpin from Desktop
          </ContextMenuItem>
        ) : (
          <ContextMenuItem onSelect={() => onAction("pin", appId)}>
            <Pin className="mr-2 h-4 w-4" />
            Pin to Desktop
          </ContextMenuItem>
        )}
        
        <ContextMenuItem onSelect={() => onAction("add-to-dock", appId)}>
          <Download className="mr-2 h-4 w-4" />
          Add to Dock
        </ContextMenuItem>
        
        <ContextMenuSeparator />
        
        <ContextMenuItem onSelect={() => onAction("settings", appId)}>
          <Settings className="mr-2 h-4 w-4" />
          App Settings
        </ContextMenuItem>
        
        <ContextMenuItem onSelect={() => onAction("properties", appId)}>
          <Info className="mr-2 h-4 w-4" />
          Properties
        </ContextMenuItem>
        
        <ContextMenuSeparator />
        
        <ContextMenuItem 
          onSelect={() => onAction("delete", appId)} 
          variant="destructive"
        >
          <Trash2 className="mr-2 h-4 w-4" />
          Delete
          <ContextMenuShortcut>Del</ContextMenuShortcut>
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  )
}