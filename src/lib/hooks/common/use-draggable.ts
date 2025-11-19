import { useState, useEffect, useCallback, RefObject } from 'react'

interface Position {
  x: number
  y: number
}

interface UseDraggableProps {
  elementRef: RefObject<HTMLElement>
  handleRef: RefObject<HTMLElement>
  enabled?: boolean
  defaultPosition?: Position
  bounds?: 'parent' | 'window' | DOMRect
  onDragStart?: (position: Position) => void
  onDrag?: (position: Position) => void
  onDragEnd?: (position: Position) => void
}

export function useDraggable({
  elementRef,
  handleRef,
  enabled = true,
  defaultPosition = { x: 0, y: 0 },
  bounds = 'window',
  onDragStart,
  onDrag,
  onDragEnd,
}: UseDraggableProps) {
  const [position, setPosition] = useState<Position>(defaultPosition)
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState<Position>({ x: 0, y: 0 })

  const handleMouseDown = useCallback((e: MouseEvent) => {
    if (!enabled || !elementRef.current) return
    
    e.preventDefault()
    setIsDragging(true)
    
    const rect = elementRef.current.getBoundingClientRect()
    setDragStart({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    })
    
    onDragStart?.(position)
  }, [enabled, elementRef, position, onDragStart])

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !elementRef.current) return
    
    let newX = e.clientX - dragStart.x
    let newY = e.clientY - dragStart.y
    
    // Apply bounds
    if (bounds === 'window') {
      const rect = elementRef.current.getBoundingClientRect()
      newX = Math.max(0, Math.min(window.innerWidth - rect.width, newX))
      newY = Math.max(0, Math.min(window.innerHeight - rect.height, newY))
    } else if (bounds === 'parent' && elementRef.current.parentElement) {
      const parentRect = elementRef.current.parentElement.getBoundingClientRect()
      const rect = elementRef.current.getBoundingClientRect()
      newX = Math.max(0, Math.min(parentRect.width - rect.width, newX))
      newY = Math.max(0, Math.min(parentRect.height - rect.height, newY))
    }
    
    const newPosition = { x: newX, y: newY }
    setPosition(newPosition)
    onDrag?.(newPosition)
  }, [isDragging, dragStart, elementRef, bounds, onDrag])

  const handleMouseUp = useCallback(() => {
    if (!isDragging) return
    setIsDragging(false)
    onDragEnd?.(position)
  }, [isDragging, position, onDragEnd])

  useEffect(() => {
    const handle = handleRef.current
    if (!handle || !enabled) return

    handle.addEventListener('mousedown', handleMouseDown)
    
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.body.style.userSelect = 'none'
    }

    return () => {
      handle.removeEventListener('mousedown', handleMouseDown)
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.body.style.userSelect = ''
    }
  }, [handleRef, enabled, isDragging, handleMouseDown, handleMouseMove, handleMouseUp])

  return {
    position,
    isDragging,
    setPosition,
  }
}