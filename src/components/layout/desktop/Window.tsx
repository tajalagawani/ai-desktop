"use client"

import React, { useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"

interface WindowProps {
  id: string
  title: string
  children: React.ReactNode
  isActive: boolean
  isMinimized: boolean
  isMaximized: boolean
  position: { x: number; y: number }
  size: { width: number; height: number }
  onClose: (id: string) => void
  onMinimize: (id: string) => void
  onMaximize: (id: string) => void
  onDragStart: (e: React.MouseEvent, id: string) => void
  onResizeStart: (e: React.MouseEvent, id: string, handle: string) => void
  onFocus: (id: string) => void
}

export function Window({
  id,
  title,
  children,
  isActive,
  isMinimized,
  isMaximized,
  position,
  size,
  onClose,
  onMinimize,
  onMaximize,
  onDragStart,
  onResizeStart,
  onFocus
}: WindowProps) {
  const windowRef = useRef<HTMLDivElement>(null)

  if (isMinimized) {
    return null
  }

  return (
    <motion.div
      ref={windowRef}
      className={`absolute glass-effect rounded-2xl overflow-hidden select-none border border-border dark:border-transparent ${
        isActive ? "z-50" : "z-40"
      }`}
      style={{
        left: position.x,
        top: position.y,
        width: size.width,
        height: size.height,
      }}
      onClick={() => onFocus(id)}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.9, opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      {!isMaximized && (
        <>
          {/* Resize handles */}
          <div
            className="absolute top-0 left-0 w-3 h-3 cursor-nw-resize z-10"
            onMouseDown={(e) => onResizeStart(e, id, "top-left")}
          />
          <div
            className="absolute top-0 right-0 w-3 h-3 cursor-ne-resize z-10"
            onMouseDown={(e) => onResizeStart(e, id, "top-right")}
          />
          <div
            className="absolute bottom-0 left-0 w-3 h-3 cursor-sw-resize z-10"
            onMouseDown={(e) => onResizeStart(e, id, "bottom-left")}
          />
          <div
            className="absolute bottom-0 right-0 w-3 h-3 cursor-se-resize z-10"
            onMouseDown={(e) => onResizeStart(e, id, "bottom-right")}
          />
          <div
            className="absolute top-0 left-3 right-3 h-1 cursor-n-resize z-10"
            onMouseDown={(e) => onResizeStart(e, id, "top")}
          />
          <div
            className="absolute bottom-0 left-3 right-3 h-1 cursor-s-resize z-10"
            onMouseDown={(e) => onResizeStart(e, id, "bottom")}
          />
          <div
            className="absolute left-0 top-3 bottom-3 w-1 cursor-w-resize z-10"
            onMouseDown={(e) => onResizeStart(e, id, "left")}
          />
          <div
            className="absolute right-0 top-3 bottom-3 w-1 cursor-e-resize z-10"
            onMouseDown={(e) => onResizeStart(e, id, "right")}
          />
        </>
      )}

      {/* Window Header */}
      <div
        className="flex items-center justify-between p-3 bg-muted cursor-grab active:cursor-grabbing"
        onMouseDown={(e) => onDragStart(e, id)}
      >
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <button
              className="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 transition-colors duration-200"
              onClick={(e) => {
                e.stopPropagation()
                onClose(id)
              }}
            />
            <button
              className="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 transition-colors duration-200"
              onClick={(e) => {
                e.stopPropagation()
                onMinimize(id)
              }}
            />
            <button
              className="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 transition-colors duration-200"
              onClick={(e) => {
                e.stopPropagation()
                onMaximize(id)
              }}
            />
          </div>
          <span className="text-sm font-normal ml-2">{title}</span>
        </div>
      </div>

      {/* Window Content */}
      <div className="h-full overflow-hidden bg-muted" style={{ height: "calc(100% - 48px)" }}>
        {children}
      </div>
    </motion.div>
  )
}