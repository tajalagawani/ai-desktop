import { useState, useRef, useCallback, useEffect } from "react"
import {
  createDragState,
  createNewWindow,
  constrainWindowPosition,
  calculateResizedWindow,
  DragState,
  Size,
} from "@/utils/desktop-utils"
import { AppConfig, DesktopFolder } from "@/data/desktop-apps"

export interface WindowState {
  id: string
  title: string
  component: React.ReactNode
  isMinimized: boolean
  isMaximized: boolean
  position: { x: number; y: number }
  size: { width: number; height: number }
  minSize: { width: number; height: number }
}

export const useDesktop = () => {
  const [windows, setWindows] = useState<WindowState[]>([])
  const [activeWindow, setActiveWindow] = useState<string | null>(null)
  const [dragState, setDragState] = useState<DragState>(createDragState())
  const [screenSize, setScreenSize] = useState<Size>({ width: 0, height: 0 })
  const [desktopFolders, setDesktopFolders] = useState<DesktopFolder[]>([])
  const dragWindowId = useRef<string | null>(null)

  useEffect(() => {
    const updateScreenSize = () => {
      setScreenSize({ width: window.innerWidth, height: window.innerHeight })
    }

    updateScreenSize()
    window.addEventListener("resize", updateScreenSize)
    return () => window.removeEventListener("resize", updateScreenSize)
  }, [])

  const openWindow = useCallback(
    (id: string, title: string, component: React.ReactNode) => {
      const existingWindow = windows.find((w) => w.id === id)
      if (existingWindow) {
        if (existingWindow.isMinimized) {
          restoreWindow(id)
        } else {
          setActiveWindow(id)
        }
        return
      }

      const newWindow = createNewWindow(id, title, component, windows.length, screenSize)
      setWindows((prev) => [...prev, newWindow])
      setActiveWindow(id)
    },
    [windows, screenSize]
  )

  const closeWindow = useCallback((id: string) => {
    setWindows((prev) => prev.filter((w) => w.id !== id))
    if (activeWindow === id) {
      setActiveWindow(null)
    }
  }, [activeWindow])

  const minimizeWindow = useCallback((id: string) => {
    setWindows((prev) => prev.map((w) => (w.id === id ? { ...w, isMinimized: true } : w)))
    if (activeWindow === id) {
      setActiveWindow(null)
    }
  }, [activeWindow])

  const toggleMaximizeWindow = useCallback((id: string) => {
    setWindows((prev) =>
      prev.map((w) => {
        if (w.id === id) {
          if (w.isMaximized) {
            return { ...w, isMaximized: false }
          } else {
            return {
              ...w,
              isMaximized: true,
              position: { x: 0, y: 0 },
              size: { width: screenSize.width, height: screenSize.height - 64 },
            }
          }
        }
        return w
      })
    )
  }, [screenSize])

  const restoreWindow = useCallback((id: string) => {
    setWindows((prev) => prev.map((w) => (w.id === id ? { ...w, isMinimized: false } : w)))
    setActiveWindow(id)
  }, [])

  const handleMouseDown = useCallback(
    (e: React.MouseEvent, windowId: string, action: "drag" | "resize", resizeHandle?: string) => {
      e.preventDefault()
      e.stopPropagation()

      const window = windows.find((w) => w.id === windowId)
      if (!window || window.isMaximized) return

      dragWindowId.current = windowId
      setActiveWindow(windowId)

      setDragState({
        isDragging: action === "drag",
        isResizing: action === "resize",
        dragStart: { x: e.clientX, y: e.clientY },
        windowStart: {
          x: window.position.x,
          y: window.position.y,
          width: window.size.width,
          height: window.size.height,
        },
        resizeHandle: resizeHandle || null,
      })
    },
    [windows]
  )

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!dragState.isDragging && !dragState.isResizing) return
      if (!dragWindowId.current) return

      const deltaX = e.clientX - dragState.dragStart.x
      const deltaY = e.clientY - dragState.dragStart.y

      setWindows((prev) =>
        prev.map((window) => {
          if (window.id !== dragWindowId.current) return window

          if (dragState.isDragging) {
            const newPosition = constrainWindowPosition(
              {
                x: dragState.windowStart.x + deltaX,
                y: dragState.windowStart.y + deltaY,
              },
              window.size,
              screenSize
            )

            return {
              ...window,
              position: newPosition,
            }
          }

          if (dragState.isResizing) {
            const resized = calculateResizedWindow(window, dragState, deltaX, deltaY, screenSize)
            return {
              ...window,
              ...resized,
            }
          }

          return window
        })
      )
    },
    [dragState, screenSize]
  )

  const handleMouseUp = useCallback(() => {
    setDragState(createDragState())
    dragWindowId.current = null
  }, [])

  useEffect(() => {
    if (dragState.isDragging || dragState.isResizing) {
      document.addEventListener("mousemove", handleMouseMove)
      document.addEventListener("mouseup", handleMouseUp)
      document.body.style.cursor = dragState.isDragging ? "grabbing" : "nw-resize"

      return () => {
        document.removeEventListener("mousemove", handleMouseMove)
        document.removeEventListener("mouseup", handleMouseUp)
        document.body.style.cursor = "default"
      }
    }
  }, [dragState.isDragging, dragState.isResizing, handleMouseMove, handleMouseUp])

  const createFolder = useCallback((name: string, x: number, y: number) => {
    const newFolder: DesktopFolder = {
      id: `folder-${Date.now()}`,
      name,
      x,
      y,
      items: [],
    }
    setDesktopFolders((prev) => [...prev, newFolder])
    return newFolder
  }, [])

  const deleteFolder = useCallback((id: string) => {
    setDesktopFolders((prev) => prev.filter((f) => f.id !== id))
  }, [])

  const renameFolder = useCallback((id: string, newName: string) => {
    setDesktopFolders((prev) =>
      prev.map((f) => (f.id === id ? { ...f, name: newName } : f))
    )
  }, [])

  return {
    windows,
    activeWindow,
    screenSize,
    desktopFolders,
    dragState,
    openWindow,
    closeWindow,
    minimizeWindow,
    toggleMaximizeWindow,
    restoreWindow,
    handleMouseDown,
    setActiveWindow,
    createFolder,
    deleteFolder,
    renameFolder,
  }
}

export const useMouseActivity = (timeout = 3000) => {
  const [isMouseActive, setIsMouseActive] = useState(true)
  const mouseTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    const handleMouseMove = () => {
      setIsMouseActive(true)
      
      if (mouseTimeoutRef.current) {
        clearTimeout(mouseTimeoutRef.current)
      }
      
      mouseTimeoutRef.current = setTimeout(() => {
        setIsMouseActive(false)
      }, timeout)
    }

    document.addEventListener("mousemove", handleMouseMove)

    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      if (mouseTimeoutRef.current) {
        clearTimeout(mouseTimeoutRef.current)
      }
    }
  }, [timeout])

  return isMouseActive
}

export const useTheme = () => {
  const [isDarkMode, setIsDarkMode] = useState(true)

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [isDarkMode])

  return { isDarkMode, setIsDarkMode, toggleTheme: () => setIsDarkMode(!isDarkMode) }
}

export const useDockApps = (initialApps: AppConfig[]) => {
  const [dockApps, setDockApps] = useState<AppConfig[]>(initialApps)

  const addToDock = useCallback((app: AppConfig) => {
    setDockApps((prev) => {
      if (prev.find((a) => a.id === app.id)) return prev
      return [...prev, app]
    })
  }, [])

  const removeFromDock = useCallback((appId: string) => {
    setDockApps((prev) => prev.filter((a) => a.id !== appId))
  }, [])

  const reorderDock = useCallback((dragIndex: number, dropIndex: number) => {
    setDockApps((prev) => {
      const newApps = [...prev]
      const [draggedApp] = newApps.splice(dragIndex, 1)
      newApps.splice(dropIndex, 0, draggedApp)
      return newApps
    })
  }, [])

  return { dockApps, addToDock, removeFromDock, reorderDock }
}