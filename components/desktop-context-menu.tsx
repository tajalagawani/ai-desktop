"use client"

import * as React from "react"
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuSub,
  ContextMenuSubContent,
  ContextMenuSubTrigger,
  ContextMenuTrigger,
} from "@/components/ui/context-menu"
import { 
  RotateCcw, 
  FolderPlus, 
  SortAsc, 
  SortDesc, 
  Grid3X3, 
  List, 
  Settings,
  Info,
  Calendar,
  Type,
  Folder
} from "lucide-react"

interface DesktopContextMenuProps {
  children: React.ReactNode
  onAction: (action: string) => void
}

export function DesktopContextMenu({ children, onAction }: DesktopContextMenuProps) {
  return (
    <ContextMenu>
      <ContextMenuTrigger className="block">
        {children}
      </ContextMenuTrigger>
      <ContextMenuContent className="w-64">
        <ContextMenuItem onSelect={() => onAction("refresh")}>
          <RotateCcw className="mr-2 h-4 w-4" />
          Refresh
          <ContextMenuShortcut>F5</ContextMenuShortcut>
        </ContextMenuItem>
        
        <ContextMenuSeparator />
        
        <ContextMenuItem onSelect={() => onAction("new-folder")}>
          <FolderPlus className="mr-2 h-4 w-4" />
          New Folder
          <ContextMenuShortcut>Ctrl+Shift+N</ContextMenuShortcut>
        </ContextMenuItem>
        
        <ContextMenuSeparator />
        
        <ContextMenuSub>
          <ContextMenuSubTrigger>
            <SortAsc className="mr-2 h-4 w-4" />
            Sort by
          </ContextMenuSubTrigger>
          <ContextMenuSubContent className="w-48" sideOffset={2} alignOffset={-5}>
            <ContextMenuItem onSelect={() => onAction("sort-name")}>
              <Type className="mr-2 h-4 w-4" />
              Name
            </ContextMenuItem>
            <ContextMenuItem onSelect={() => onAction("sort-date")}>
              <Calendar className="mr-2 h-4 w-4" />
              Date modified
            </ContextMenuItem>
            <ContextMenuItem onSelect={() => onAction("sort-type")}>
              <Folder className="mr-2 h-4 w-4" />
              Type
            </ContextMenuItem>
            <ContextMenuSeparator />
            <ContextMenuItem onSelect={() => onAction("sort-asc")}>
              <SortAsc className="mr-2 h-4 w-4" />
              Ascending
            </ContextMenuItem>
            <ContextMenuItem onSelect={() => onAction("sort-desc")}>
              <SortDesc className="mr-2 h-4 w-4" />
              Descending
            </ContextMenuItem>
          </ContextMenuSubContent>
        </ContextMenuSub>
        
        <ContextMenuSub>
          <ContextMenuSubTrigger>
            <Grid3X3 className="mr-2 h-4 w-4" />
            View
          </ContextMenuSubTrigger>
          <ContextMenuSubContent className="w-48" sideOffset={2} alignOffset={-5}>
            <ContextMenuItem onSelect={() => onAction("view-large")}>
              Large icons
            </ContextMenuItem>
            <ContextMenuItem onSelect={() => onAction("view-medium")}>
              Medium icons
            </ContextMenuItem>
            <ContextMenuItem onSelect={() => onAction("view-small")}>
              Small icons
            </ContextMenuItem>
            <ContextMenuSeparator />
            <ContextMenuItem onSelect={() => onAction("view-list")}>
              <List className="mr-2 h-4 w-4" />
              List
            </ContextMenuItem>
            <ContextMenuItem onSelect={() => onAction("view-grid")}>
              <Grid3X3 className="mr-2 h-4 w-4" />
              Grid
            </ContextMenuItem>
          </ContextMenuSubContent>
        </ContextMenuSub>
        
        <ContextMenuSeparator />
        
        <ContextMenuItem onSelect={() => onAction("settings")}>
          <Settings className="mr-2 h-4 w-4" />
          Desktop Settings
        </ContextMenuItem>
        
        <ContextMenuItem onSelect={() => onAction("properties")}>
          <Info className="mr-2 h-4 w-4" />
          Properties
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  )
}