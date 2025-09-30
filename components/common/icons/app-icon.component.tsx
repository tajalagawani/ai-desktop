"use client"

import React from "react"
import { getIcon } from "@/utils/icon-mapper"
import { cn } from "@/lib/utils"

interface AppIconProps {
  icon: string
  size?: "xs" | "sm" | "md" | "lg" | "xl"
  className?: string
  gradient?: boolean
}

const sizeClasses = {
  xs: "h-6 w-6 p-1",
  sm: "h-8 w-8 p-1.5",
  md: "h-10 w-10 p-2",
  lg: "h-12 w-12 p-2.5",
  xl: "h-16 w-16 p-3",
}

const iconSizeClasses = {
  xs: "h-4 w-4",
  sm: "h-5 w-5",
  md: "h-6 w-6",
  lg: "h-8 w-8",
  xl: "h-10 w-10",
}

export function AppIcon({
  icon,
  size = "md",
  className,
  gradient = true,
}: AppIconProps) {
  const Icon = getIcon(icon)

  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-2xl",
        gradient && "bg-gradient-to-br from-primary/10 to-accent/10",
        !gradient && "bg-muted",
        sizeClasses[size],
        className
      )}
    >
      <Icon className={cn("text-primary", iconSizeClasses[size])} />
    </div>
  )
}