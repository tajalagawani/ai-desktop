"use client"

import React from "react"
import { Pin } from "lucide-react"
import { cn } from "@/lib/utils"

interface PinnedBadgeProps {
  className?: string
}

export function PinnedBadge({ className }: PinnedBadgeProps) {
  return (
    <div
      className={cn(
        "flex h-4 w-4 items-center justify-center rounded-full bg-primary text-primary-foreground",
        className
      )}
    >
      <Pin className="h-2.5 w-2.5" />
    </div>
  )
}