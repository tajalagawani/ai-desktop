"use client"

import React, { useState, useRef, useCallback } from "react"
import { cn } from "@/lib/utils"
import { X, Minus, Maximize2, Minimize2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useDraggable } from "@/hooks/use-draggable"
import { useResizable } from "@/hooks/use-resizable"

export interface WindowProps {
  id: string
  title: string
  children: React.ReactNode
  isOpen?: boolean
  isMaximized?: boolean
  isMinimized?: boolean
  canClose?: boolean
  canMaximize?: boolean
  canMinimize?: boolean
  canResize?: boolean
  canDrag?: boolean
  defaultPosition?: { x: number; y: number }
  defaultSize?: { width: number; height: number }
  minSize?: { width: number; height: number }
  maxSize?: { width: number; height: number }
  zIndex?: number
  onClose?: () => void
  onMaximize?: () => void
  onMinimize?: () => void
  onFocus?: () => void
  className?: string
  headerClassName?: string
  contentClassName?: string
  icon?: React.ReactNode
}

export function Window({
  id,
  title,
  children,
  isOpen = true,
  isMaximized = false,
  isMinimized = false,
  canClose = true,
  canMaximize = true,
  canMinimize = true,
  canResize = true,
  canDrag = true,
  defaultPosition = { x: 100, y: 100 },
  defaultSize = { width: 800, height: 600 },
  minSize = { width: 400, height: 300 },
  maxSize = { width: 1600, height: 1200 },
  zIndex = 100,
  onClose,
  onMaximize,
  onMinimize,
  onFocus,
  className,
  headerClassName,
  contentClassName,
  icon,
}: WindowProps) {
  const windowRef = useRef<HTMLDivElement>(null)
  const headerRef = useRef<HTMLDivElement>(null)
  const [localMaximized, setLocalMaximized] = useState(isMaximized)

  const { position, isDragging } = useDraggable({
    elementRef: windowRef,
    handleRef: headerRef,
    enabled: canDrag && !localMaximized,
    defaultPosition,
  })

  const { size, isResizing } = useResizable({
    elementRef: windowRef,
    enabled: canResize && !localMaximized,
    defaultSize,
    minSize,
    maxSize,
  })

  const handleMaximize = useCallback(() => {
    setLocalMaximized(!localMaximized)
    onMaximize?.()
  }, [localMaximized, onMaximize])

  if (!isOpen || isMinimized) return null

  return (
    <div
      ref={windowRef}
      className={cn(
        "absolute flex flex-col bg-background border rounded-lg shadow-xl overflow-hidden",
        localMaximized && "!inset-0 !w-full !h-full",
        isDragging && "cursor-move",
        isResizing && "cursor-nwse-resize",
        className
      )}
      style={{
        left: localMaximized ? 0 : position.x,
        top: localMaximized ? 0 : position.y,
        width: localMaximized ? "100%" : size.width,
        height: localMaximized ? "100%" : size.height,
        zIndex,
      }}
      onMouseDown={onFocus}
    >
      {/* Window Header */}
      <div
        ref={headerRef}
        className={cn(
          "flex items-center justify-between px-4 py-2 bg-muted/50 border-b select-none",
          canDrag && !localMaximized && "cursor-move",
          headerClassName
        )}
      >
        <div className="flex items-center gap-2">
          {icon && <div className="w-4 h-4">{icon}</div>}
          <h2 className="text-sm font-semibold truncate">{title}</h2>
        </div>
        
        <div className="flex items-center gap-1">
          {canMinimize && (
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={onMinimize}
            >
              <Minus className="h-3 w-3" />
            </Button>
          )}
          {canMaximize && (
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={handleMaximize}
            >
              {localMaximized ? (
                <Minimize2 className="h-3 w-3" />
              ) : (
                <Maximize2 className="h-3 w-3" />
              )}
            </Button>
          )}
          {canClose && (
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 hover:bg-destructive hover:text-destructive-foreground"
              onClick={onClose}
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>

      {/* Window Content */}
      <div className={cn("flex-1 overflow-auto", contentClassName)}>
        {children}
      </div>

      {/* Resize Handle */}
      {canResize && !localMaximized && (
        <div className="absolute bottom-0 right-0 w-4 h-4 cursor-nwse-resize" />
      )}
    </div>
  )
}