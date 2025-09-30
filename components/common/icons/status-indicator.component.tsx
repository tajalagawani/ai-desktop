"use client"

import React from "react"
import { cn } from "@/lib/utils"
import type { AppStatus } from "@/types/app.types"

interface StatusIndicatorProps {
  status: AppStatus
  className?: string
}

const statusColors = {
  running: "bg-green-500",
  updating: "bg-blue-500 animate-pulse",
  stopped: "bg-gray-400",
  installing: "bg-orange-500 animate-pulse",
}

export function StatusIndicator({ status, className }: StatusIndicatorProps) {
  return (
    <div
      className={cn(
        "h-2 w-2 rounded-full",
        statusColors[status],
        className
      )}
      aria-label={`Status: ${status}`}
    />
  )
}