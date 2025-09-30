"use client"

import React from "react"
import { Button } from "@/components/ui/button"
import { Play, Square, Download, RotateCw } from "lucide-react"
import type { AppActionButtonProps } from "@/types/app.types"

export function AppActionButton({ app, onAction, className }: AppActionButtonProps) {
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    const action = getAction(app.status)
    onAction?.(app, action)
  }

  const getAction = (status: string) => {
    switch (status) {
      case "running":
        return "stop"
      case "stopped":
        return "launch"
      case "updating":
        return "cancel"
      case "installing":
        return "cancel"
      default:
        return "launch"
    }
  }

  const getButtonContent = () => {
    switch (app.status) {
      case "running":
        return (
          <>
            <Square className="mr-1 h-3 w-3" />
            Stop
          </>
        )
      case "updating":
        return (
          <>
            <RotateCw className="mr-1 h-3 w-3 animate-spin" />
            Updating
          </>
        )
      case "installing":
        return (
          <>
            <Download className="mr-1 h-3 w-3 animate-bounce" />
            Installing
          </>
        )
      default:
        return (
          <>
            <Play className="mr-1 h-3 w-3" />
            Launch
          </>
        )
    }
  }

  return (
    <Button
      size="sm"
      variant={app.status === "running" ? "secondary" : "default"}
      onClick={handleClick}
      disabled={app.status === "updating" || app.status === "installing"}
      className={className}
    >
      {getButtonContent()}
    </Button>
  )
}