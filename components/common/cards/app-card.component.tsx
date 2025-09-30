"use client"

import React from "react"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { AppIcon } from "../icons/app-icon.component"
import { StatusIndicator } from "../icons/status-indicator.component"
import { PinnedBadge } from "../icons/pinned-badge.component"
import { UpdateBadge } from "../badges/update-badge.component"
import { AppActionButton } from "../buttons/app-action-button.component"
import { DropdownActions } from "../menus/dropdown-actions.component"
import type { AppCardProps } from "@/types/app.types"

export function AppCard({
  app,
  isSelected = false,
  onAction,
  onSelect,
  className,
  variant = "default",
}: AppCardProps) {
  const handleClick = (e: React.MouseEvent) => {
    if (e.detail === 2) {
      // Double click
      onAction?.(app, "launch")
    } else {
      // Single click
      onSelect?.(app.id)
    }
  }

  return (
    <Card
      className={cn(
        "relative p-4 transition-all duration-200 cursor-pointer",
        "hover:shadow-lg hover:scale-[1.02]",
        isSelected && "ring-2 ring-primary ring-offset-2",
        variant === "compact" && "p-3",
        className
      )}
      onClick={handleClick}
    >
      <div className="flex flex-col items-center text-center space-y-3">
        {/* App Icon with Status */}
        <div className="relative">
          <AppIcon
            icon={app.icon}
            size={variant === "compact" ? "md" : "lg"}
            className="transition-transform hover:scale-110"
          />
          <StatusIndicator
            status={app.status}
            className="absolute -top-1 -right-1"
          />
          {app.pinned && (
            <PinnedBadge className="absolute -top-2 -left-2" />
          )}
        </div>

        {/* App Info */}
        <div className="flex flex-col items-center space-y-1 min-w-0 w-full">
          <h3 className="font-semibold text-sm truncate w-full">
            {app.displayName}
          </h3>
          {variant !== "compact" && (
            <p className="text-xs text-muted-foreground truncate w-full">
              {app.developer}
            </p>
          )}
        </div>

        {/* Version and Size */}
        {variant !== "compact" && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>v{app.version}</span>
            <span>•</span>
            <span>{app.size}</span>
          </div>
        )}

        {/* Update Badge */}
        {app.updateAvailable && (
          <UpdateBadge version={app.newVersion} className="mb-2" />
        )}

        {/* Actions */}
        <div className="flex gap-1 w-full">
          <AppActionButton
            app={app}
            onAction={onAction}
            className="flex-1"
          />
          <DropdownActions
            app={app}
            onAction={onAction}
            variant="icon"
          />
        </div>
      </div>
    </Card>
  )
}