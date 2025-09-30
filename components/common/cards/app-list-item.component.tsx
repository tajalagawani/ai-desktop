"use client"

import React from "react"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { AppIcon } from "../icons/app-icon.component"
import { StatusIndicator } from "../icons/status-indicator.component"
import { UpdateBadge } from "../badges/update-badge.component"
import { AppActionButton } from "../buttons/app-action-button.component"
import { DropdownActions } from "../menus/dropdown-actions.component"
import { Badge } from "@/components/ui/badge"
import type { AppCardProps } from "@/types/app.types"

export function AppListItem({
  app,
  isSelected = false,
  onAction,
  onSelect,
  className,
}: AppCardProps) {
  const handleClick = (e: React.MouseEvent) => {
    if (e.detail === 2) {
      onAction?.(app, "launch")
    } else {
      onSelect?.(app.id)
    }
  }

  return (
    <Card
      className={cn(
        "p-4 transition-all duration-200 cursor-pointer",
        "hover:shadow-md hover:bg-accent/5",
        isSelected && "ring-2 ring-primary ring-offset-2",
        className
      )}
      onClick={handleClick}
    >
      <div className="flex items-center gap-4">
        {/* App Icon with Status */}
        <div className="relative">
          <AppIcon
            icon={app.icon}
            size="md"
            className="transition-transform hover:scale-110"
          />
          <StatusIndicator
            status={app.status}
            className="absolute -top-1 -right-1"
          />
        </div>

        {/* App Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold truncate">{app.displayName}</h3>
            {app.pinned && (
              <Badge variant="secondary" className="text-xs">
                Pinned
              </Badge>
            )}
            {app.updateAvailable && <UpdateBadge />}
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
            <span>{app.developer}</span>
            <span>•</span>
            <span>v{app.version}</span>
            <span>•</span>
            <span>{app.size}</span>
            <span>•</span>
            <span className="capitalize">{app.category}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <AppActionButton app={app} onAction={onAction} />
          <DropdownActions app={app} onAction={onAction} />
        </div>
      </div>
    </Card>
  )
}