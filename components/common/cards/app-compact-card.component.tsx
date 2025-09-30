"use client"

import React from "react"
import { cn } from "@/lib/utils"
import { AppIcon } from "../icons/app-icon.component"
import { StatusIndicator } from "../icons/status-indicator.component"
import type { AppCardProps } from "@/types/app.types"

export function AppCompactCard({
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
    <div
      className={cn(
        "relative p-3 rounded-lg transition-all duration-200 cursor-pointer",
        "hover:bg-accent/10 hover:scale-[1.02]",
        isSelected && "bg-accent/20 ring-1 ring-primary",
        className
      )}
      onClick={handleClick}
    >
      <div className="flex flex-col items-center text-center space-y-2">
        {/* App Icon with Status */}
        <div className="relative">
          <AppIcon
            icon={app.icon}
            size="sm"
            className="transition-transform hover:scale-110"
          />
          <StatusIndicator
            status={app.status}
            className="absolute -top-0.5 -right-0.5 h-1.5 w-1.5"
          />
        </div>

        {/* App Name */}
        <span className="text-xs font-medium truncate w-full max-w-[80px]">
          {app.displayName}
        </span>
      </div>
    </div>
  )
}