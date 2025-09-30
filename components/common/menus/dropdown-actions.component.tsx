"use client"

import React from "react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { 
  MoreVertical, 
  Info, 
  Settings, 
  Trash2, 
  Pin, 
  FolderOpen,
  RefreshCw,
  Share2 
} from "lucide-react"
import type { DropdownActionsProps } from "@/types/app.types"

export function DropdownActions({ app, onAction, variant = "icon" }: DropdownActionsProps) {
  const handleAction = (action: string) => (e: Event) => {
    e.stopPropagation()
    onAction?.(app, action)
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          size={variant === "icon" ? "icon" : "sm"}
          onClick={(e) => e.stopPropagation()}
        >
          <MoreVertical className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
        <DropdownMenuItem onSelect={handleAction("info")}>
          <Info className="mr-2 h-4 w-4" />
          App Info
        </DropdownMenuItem>
        <DropdownMenuItem onSelect={handleAction("settings")}>
          <Settings className="mr-2 h-4 w-4" />
          Settings
        </DropdownMenuItem>
        <DropdownMenuItem onSelect={handleAction("openFolder")}>
          <FolderOpen className="mr-2 h-4 w-4" />
          Open Folder
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onSelect={handleAction("pin")}>
          <Pin className="mr-2 h-4 w-4" />
          {app.pinned ? "Unpin" : "Pin"} App
        </DropdownMenuItem>
        <DropdownMenuItem onSelect={handleAction("update")}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Check for Updates
        </DropdownMenuItem>
        <DropdownMenuItem onSelect={handleAction("share")}>
          <Share2 className="mr-2 h-4 w-4" />
          Share
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem 
          onSelect={handleAction("uninstall")}
          className="text-destructive"
        >
          <Trash2 className="mr-2 h-4 w-4" />
          Uninstall
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}