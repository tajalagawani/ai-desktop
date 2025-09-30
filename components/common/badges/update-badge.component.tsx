"use client"

import React from "react"
import { ArrowUp } from "lucide-react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

interface UpdateBadgeProps {
  version?: string
  className?: string
}

export function UpdateBadge({ version, className }: UpdateBadgeProps) {
  return (
    <Badge 
      variant="secondary" 
      className={cn("text-xs", className)}
    >
      <ArrowUp className="mr-1 h-3 w-3" />
      {version ? `Update to ${version}` : "Update available"}
    </Badge>
  )
}