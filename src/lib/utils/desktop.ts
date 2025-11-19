import { WindowState } from "@/lib/hooks/features/use-desktop"
import { WINDOW_CONFIGS, WindowConfig } from "@/data/desktop-apps"

export interface Position {
  x: number
  y: number
}

export interface Size {
  width: number
  height: number
}

export interface DragState {
  isDragging: boolean
  isResizing: boolean
  dragStart: Position
  windowStart: {
    x: number
    y: number
    width: number
    height: number
  }
  resizeHandle: string | null
}

export const createDragState = (): DragState => ({
  isDragging: false,
  isResizing: false,
  dragStart: { x: 0, y: 0 },
  windowStart: { x: 0, y: 0, width: 0, height: 0 },
  resizeHandle: null,
})

export const getWindowConfig = (appId: string): WindowConfig => {
  return WINDOW_CONFIGS[appId] || WINDOW_CONFIGS.default
}

export const getResponsiveWindowSize = (
  baseWidth: number,
  baseHeight: number,
  screenSize: Size
): Size => {
  const maxWidth = Math.min(screenSize.width - 100, baseWidth)
  const maxHeight = Math.min(screenSize.height - 150, baseHeight)
  return {
    width: Math.max(320, maxWidth),
    height: Math.max(240, maxHeight),
  }
}

export const calculateWindowPosition = (
  windowIndex: number,
  screenSize: Size,
  isMobile: boolean
): Position => {
  if (isMobile) {
    return { x: 0, y: 0 }
  }
  return {
    x: Math.max(20, 100 + windowIndex * 30),
    y: Math.max(20, 100 + windowIndex * 30),
  }
}

export const createNewWindow = (
  id: string,
  title: string,
  component: React.ReactNode,
  windowIndex: number,
  screenSize: Size
): WindowState => {
  const config = getWindowConfig(id)
  const isMobile = screenSize.width < 768
  const shouldMaximize = isMobile || config.openMaximized
  const responsiveSize = getResponsiveWindowSize(
    config.defaultWidth,
    config.defaultHeight,
    screenSize
  )

  return {
    id,
    title,
    component,
    isMinimized: false,
    isMaximized: shouldMaximize,
    position: shouldMaximize
      ? { x: 0, y: 0 }
      : calculateWindowPosition(windowIndex, screenSize, isMobile),
    size: shouldMaximize
      ? { width: screenSize.width, height: screenSize.height - 64 }
      : responsiveSize,
    minSize: { width: config.minWidth, height: config.minHeight },
  }
}

export const constrainWindowPosition = (
  position: Position,
  size: Size,
  screenSize: Size
): Position => {
  return {
    x: Math.max(0, Math.min(screenSize.width - size.width, position.x)),
    y: Math.max(0, Math.min(screenSize.height - 100 - size.height, position.y)),
  }
}

export const calculateResizedWindow = (
  window: WindowState,
  dragState: DragState,
  deltaX: number,
  deltaY: number,
  screenSize: Size
): Partial<WindowState> => {
  if (!dragState.resizeHandle) return {}

  let newWidth = dragState.windowStart.width
  let newHeight = dragState.windowStart.height
  let newX = dragState.windowStart.x
  let newY = dragState.windowStart.y

  const handle = dragState.resizeHandle

  if (handle.includes("right")) {
    newWidth = Math.max(window.minSize.width, dragState.windowStart.width + deltaX)
  }
  if (handle.includes("left")) {
    newWidth = Math.max(window.minSize.width, dragState.windowStart.width - deltaX)
    newX = dragState.windowStart.x + deltaX
  }
  if (handle.includes("bottom")) {
    newHeight = Math.max(window.minSize.height, dragState.windowStart.height + deltaY)
  }
  if (handle.includes("top")) {
    newHeight = Math.max(window.minSize.height, dragState.windowStart.height - deltaY)
    newY = dragState.windowStart.y + deltaY
  }

  newWidth = Math.min(newWidth, screenSize.width - newX)
  newHeight = Math.min(newHeight, screenSize.height - 64 - newY)

  return {
    position: { x: newX, y: newY },
    size: { width: newWidth, height: newHeight },
  }
}

export const getAppComponent = async (appId: string) => {
  const componentMap: Record<string, () => Promise<any>> = {
    "terminal": () => import("@/components/features/terminal/Terminal"),
    "monitor": () => import("@/components/features/system-monitor/SystemMonitor"),
    "file-manager": () => import("@/components/features/file-manager/FileManager"),
  }

  if (componentMap[appId]) {
    const module = await componentMap[appId]()
    return module.default || module[Object.keys(module)[0]]
  }

  return null
}

export const formatFileSize = (bytes: number): string => {
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
  if (bytes === 0) return "0 Bytes"
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + " " + sizes[i]
}

export const formatTime = (timestamp: number | string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) return `${days}d ago`
  if (hours > 0) return `${hours}h ago`
  if (minutes > 0) return `${minutes}m ago`
  return `${seconds}s ago`
}

export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): T => {
  let inThrottle: boolean
  let lastFunc: ReturnType<typeof setTimeout>
  let lastRan: number

  return ((...args) => {
    if (!inThrottle) {
      func.apply(null, args)
      lastRan = Date.now()
      inThrottle = true
    } else {
      clearTimeout(lastFunc)
      lastFunc = setTimeout(() => {
        if (Date.now() - lastRan >= limit) {
          func.apply(null, args)
          lastRan = Date.now()
        }
      }, limit - (Date.now() - lastRan))
    }
  }) as T
}

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): T => {
  let timeout: ReturnType<typeof setTimeout>
  
  return ((...args) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func.apply(null, args), wait)
  }) as T
}

export const getIconComponent = (iconName: string) => {
  const iconMap: Record<string, any> = {
    Store: "Store",
    Folder: "Folder",
    Workflow: "Workflow",
    TerminalIcon: "TerminalIcon",
    Activity: "Activity",
    Github: "Github",
    Slack: "Slack",
    Brain: "Brain",
  }
  
  return iconMap[iconName] || "Folder"
}