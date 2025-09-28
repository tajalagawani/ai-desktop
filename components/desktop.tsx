"use client"

import React, { useState, useRef, useCallback, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Monitor,
  Store,
  Activity,
  Workflow,
  Cpu,
  Clock,
  MessageSquare,
  Minimize2,
  X,
  Maximize2,
  Sun,
  Moon,
  TerminalIcon,
  Folder,
  AlertCircle,
  Bell,
  Github,
  Brain,
  Slack,
} from "lucide-react"
import { MacAppStore } from "@/components/mac-app-store"
import { InstalledApps } from "@/components/installed-apps"
import { WorkflowCanvas } from "@/components/workflow-canvas"
import { SystemMonitor } from "@/components/system-monitor"
import { ChatInterface } from "@/components/chat-interface"
import { Terminal } from "@/components/terminal"
import { BackgroundBeams } from "@/components/ui/background-beams"
import { TwoFactorAuth } from "@/components/two-factor-auth"
import { SystemControlMenu } from "@/components/system-control-menu"
import { FloatingDockDemo } from "@/components/floating-dock-demo"
import { DesktopContextMenu } from "@/components/desktop-context-menu"
import { DesktopIconContextMenu } from "@/components/desktop-icon-context-menu"

interface Window {
  id: string
  title: string
  component: React.ReactNode
  isMinimized: boolean
  isMaximized: boolean
  position: { x: number; y: number }
  size: { width: number; height: number }
  minSize: { width: number; height: number }
}

interface DragState {
  isDragging: boolean
  isResizing: boolean
  dragStart: { x: number; y: number }
  windowStart: { x: number; y: number; width: number; height: number }
  resizeHandle: string | null
}

export function Desktop() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [windows, setWindows] = useState<Window[]>([])
  const [activeWindow, setActiveWindow] = useState<string | null>(null)
  const [isDarkMode, setIsDarkMode] = useState(true)
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [dragState, setDragState] = useState<DragState>({
    isDragging: false,
    isResizing: false,
    dragStart: { x: 0, y: 0 },
    windowStart: { x: 0, y: 0, width: 0, height: 0 },
    resizeHandle: null,
  })
  const [screenSize, setScreenSize] = useState({ width: 0, height: 0 })
  const [isMouseActive, setIsMouseActive] = useState(true)
  const [dockApps, setDockApps] = useState([
    { id: "app-store", name: "App Store", icon: "Store" },
    { id: "installed", name: "Installed", icon: "Folder" },
    { id: "workflows", name: "Workflows", icon: "Workflow" },
    { id: "terminal", name: "Terminal", icon: "TerminalIcon" },
    { id: "monitor", name: "Monitor", icon: "Activity" },
  ])
  const [installedApps] = useState([
    { id: "github", name: "GitHub Desktop", icon: "Github" },
    { id: "chatgpt", name: "ChatGPT", icon: "Brain" },
    { id: "slack", name: "Slack", icon: "Slack" },
  ])
  const [draggedApp, setDraggedApp] = useState<{ id: string; name: string; icon: string } | null>(null)
  const [desktopFolders, setDesktopFolders] = useState<{ id: string; name: string; x: number; y: number }[]>([])
  const dragWindowId = useRef<string | null>(null)
  const mouseTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    const updateScreenSize = () => {
      setScreenSize({ width: window.innerWidth, height: window.innerHeight })
    }

    updateScreenSize()
    window.addEventListener("resize", updateScreenSize)
    return () => window.removeEventListener("resize", updateScreenSize)
  }, [])

  useEffect(() => {
    // Apply theme to document
    if (isDarkMode) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [isDarkMode])

  // Mouse activity detection
  useEffect(() => {
    const handleMouseMove = () => {
      setIsMouseActive(true)
      
      // Clear existing timeout
      if (mouseTimeoutRef.current) {
        clearTimeout(mouseTimeoutRef.current)
      }
      
      // Set new timeout for 3 seconds
      mouseTimeoutRef.current = setTimeout(() => {
        setIsMouseActive(false)
      }, 3000)
    }

    document.addEventListener('mousemove', handleMouseMove)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      if (mouseTimeoutRef.current) {
        clearTimeout(mouseTimeoutRef.current)
      }
    }
  }, [])

  // Handle context menu actions
  const handleContextMenuAction = (action: string) => {
    switch (action) {
      case "refresh":
        window.location.reload()
        break
      case "new-folder":
        const newFolder = {
          id: `folder-${Date.now()}`,
          name: "New Folder",
          x: 100,
          y: 100
        }
        setDesktopFolders(prev => [...prev, newFolder])
        break
      case "sort-name":
        // Sort logic would go here
        console.log("Sort by name")
        break
      case "sort-date":
        console.log("Sort by date")
        break
      case "view-large":
        console.log("Large icons view")
        break
      case "view-grid":
        console.log("Grid view")
        break
      case "settings":
        openWindow("settings", "Desktop Settings", <div>Desktop Settings</div>)
        break
      case "properties":
        openWindow("properties", "Desktop Properties", <div>Desktop Properties</div>)
        break
      default:
        console.log("Action:", action)
    }
  }

  const getResponsiveWindowSize = (baseWidth: number, baseHeight: number) => {
    const maxWidth = Math.min(screenSize.width - 100, baseWidth)
    const maxHeight = Math.min(screenSize.height - 150, baseHeight)
    return {
      width: Math.max(320, maxWidth),
      height: Math.max(240, maxHeight),
    }
  }

  const openWindow = (id: string, title: string, component: React.ReactNode) => {
    const existingWindow = windows.find((w) => w.id === id)
    if (existingWindow) {
      setActiveWindow(id)
      return
    }

    const responsiveSize = getResponsiveWindowSize(800, 600)
    const isMobile = screenSize.width < 768

    const newWindow: Window = {
      id,
      title,
      component,
      isMinimized: false,
      isMaximized: isMobile,
      position: {
        x: isMobile ? 0 : Math.max(20, 100 + windows.length * 30),
        y: isMobile ? 0 : Math.max(20, 100 + windows.length * 30),
      },
      size: isMobile ? { width: screenSize.width, height: screenSize.height - 64 } : responsiveSize,
      minSize: { width: 320, height: 240 },
    }

    setWindows((prev) => [...prev, newWindow])
    setActiveWindow(id)
  }

  const closeWindow = (id: string) => {
    setWindows((prev) => prev.filter((w) => w.id !== id))
    if (activeWindow === id) {
      setActiveWindow(null)
    }
  }

  const minimizeWindow = (id: string) => {
    setWindows((prev) => prev.map((w) => (w.id === id ? { ...w, isMinimized: true } : w)))
    if (activeWindow === id) {
      setActiveWindow(null)
    }
  }

  const toggleMaximizeWindow = (id: string) => {
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
      }),
    )
  }

  const restoreWindow = (id: string) => {
    setWindows((prev) => prev.map((w) => (w.id === id ? { ...w, isMinimized: false } : w)))
    setActiveWindow(id)
  }

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
    [windows],
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
            const newX = Math.max(0, Math.min(screenSize.width - window.size.width, dragState.windowStart.x + deltaX))
            const newY = Math.max(
              0,
              Math.min(screenSize.height - 100 - window.size.height, dragState.windowStart.y + deltaY),
            )

            return {
              ...window,
              position: { x: newX, y: newY },
            }
          }

          if (dragState.isResizing && dragState.resizeHandle) {
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
              ...window,
              position: { x: newX, y: newY },
              size: { width: newWidth, height: newHeight },
            }
          }

          return window
        }),
      )
    },
    [dragState, screenSize],
  )

  const handleMouseUp = useCallback(() => {
    setDragState({
      isDragging: false,
      isResizing: false,
      dragStart: { x: 0, y: 0 },
      windowStart: { x: 0, y: 0, width: 0, height: 0 },
      resizeHandle: null,
    })
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

  const handleLogout = () => {
    setIsAuthenticated(false)
  }

  const handleIconContextMenuAction = (action: string, appId: string) => {
    switch (action) {
      case "open":
        const app = installedApps.find(a => a.id === appId)
        if (app) {
          openWindow(app.id, app.name, null)
        }
        break
      case "pause":
        // Pause app logic
        console.log(`Pausing app: ${appId}`)
        break
      case "resume":
        // Resume app logic
        console.log(`Resuming app: ${appId}`)
        break
      case "rename":
        // Rename app logic
        const newName = prompt("Enter new name:")
        if (newName) {
          console.log(`Renaming ${appId} to ${newName}`)
        }
        break
      case "copy":
        // Copy app logic
        console.log(`Copying app: ${appId}`)
        break
      case "pin":
        // Pin to desktop logic
        console.log(`Pinning app: ${appId}`)
        break
      case "unpin":
        // Unpin from desktop logic
        console.log(`Unpinning app: ${appId}`)
        break
      case "add-to-dock":
        // Add to dock logic
        const appToAdd = installedApps.find(a => a.id === appId)
        if (appToAdd && !dockApps.find(d => d.id === appId)) {
          setDockApps(prev => [...prev, appToAdd])
        }
        break
      case "settings":
        // App settings logic
        console.log(`Opening settings for: ${appId}`)
        break
      case "properties":
        // Properties logic
        console.log(`Opening properties for: ${appId}`)
        break
      case "delete":
        // Delete app logic
        if (confirm(`Are you sure you want to delete this app?`)) {
          console.log(`Deleting app: ${appId}`)
          // Could remove from installedApps if needed
        }
        break
      default:
        console.log(`Unknown icon action: ${action} for app: ${appId}`)
    }
  }

  if (!isAuthenticated) {
    return <TwoFactorAuth onAuthenticated={() => setIsAuthenticated(true)} />
  }

  return (
    <DesktopContextMenu onAction={handleContextMenuAction}>
      <div 
        className="h-screen w-full bg-background relative antialiased overflow-hidden"
      >
       

      {/* Desktop Icons - positioned absolutely */}
      <div className="absolute top-4 left-4 md:top-8 md:left-8 grid grid-cols-1 gap-3 md:gap-4 z-20">
        <div className="flex flex-col items-center gap-2">
          <button
            className="w-10 h-10 rounded-full bg-gray-200 dark:bg-neutral-800 flex items-center justify-center hover:scale-[1.2] transition-transform duration-200"
            onClick={() => {
              const newWindow = {
                id: "app-store",
                title: "App Store", 
                component: <MacAppStore />,
                isMinimized: false,
                isMaximized: true,
                position: { x: 0, y: 0 },
                size: { width: window.innerWidth, height: window.innerHeight },
                minSize: { width: 800, height: 600 }
              };
              setWindows(prev => {
                const exists = prev.find(w => w.id === "app-store");
                if (exists) return prev;
                return [...prev, newWindow];
              });
              setActiveWindow("app-store");
            }}
          >
            <Store className="h-6 w-6 text-neutral-600 dark:text-neutral-300" />
          </button>
          <span className="text-xs text-foreground font-medium">App Store</span>
        </div>

        <div className="flex flex-col items-center gap-2">
          <button
            className="w-10 h-10 rounded-full bg-gray-200 dark:bg-neutral-800 flex items-center justify-center hover:scale-[1.2] transition-transform duration-200"
            onClick={() => openWindow("installed", "Installed Apps", <InstalledApps />)}
          >
            <Folder className="h-6 w-6 text-neutral-600 dark:text-neutral-300" />
          </button>
          <span className="text-xs text-foreground font-medium">Installed</span>
        </div>

        <div className="flex flex-col items-center gap-2">
          <button
            className="w-10 h-10 rounded-full bg-gray-200 dark:bg-neutral-800 flex items-center justify-center hover:scale-[1.2] transition-transform duration-200"
            onClick={() => openWindow("workflows", "Workflow Canvas", <WorkflowCanvas />)}
          >
            <Workflow className="h-6 w-6 text-neutral-600 dark:text-neutral-300" />
          </button>
          <span className="text-xs text-foreground font-medium">Workflows</span>
        </div>

        <div className="flex flex-col items-center gap-2">
          <button
            className="w-10 h-10 rounded-full bg-gray-200 dark:bg-neutral-800 flex items-center justify-center hover:scale-[1.2] transition-transform duration-200"
            onClick={() => openWindow("terminal", "Terminal", <Terminal />)}
          >
            <TerminalIcon className="h-6 w-6 text-neutral-600 dark:text-neutral-300" />
          </button>
          <span className="text-xs text-foreground font-medium">Terminal</span>
        </div>

        <div className="flex flex-col items-center gap-2">
          <button
            className="w-10 h-10 rounded-full bg-gray-200 dark:bg-neutral-800 flex items-center justify-center hover:scale-[1.2] transition-transform duration-200"
            onClick={() => openWindow("monitor", "System Monitor", <SystemMonitor />)}
          >
            <Activity className="h-6 w-6 text-neutral-600 dark:text-neutral-300" />
          </button>
          <span className="text-xs text-foreground font-medium">Monitor</span>
        </div>
      </div>

      {/* Installed Apps - positioned absolutely */}
      <div className="absolute top-4 right-4 md:top-8 md:right-80 grid grid-cols-1 gap-3 md:gap-4 z-20">
        {installedApps.map((app) => {
          const IconComponent = app.icon === "Github" ? Github : app.icon === "Brain" ? Brain : Slack;
          const isRunning = windows.some(w => w.id === app.id);
          return (
            <DesktopIconContextMenu
              key={app.id}
              appId={app.id}
              appName={app.name}
              isRunning={isRunning}
              isPinned={true}
              onAction={handleIconContextMenuAction}
            >
              <div 
                className="flex flex-col items-center gap-2"
                draggable
                onDragStart={(e) => {
                  setDraggedApp(app);
                  e.dataTransfer.effectAllowed = "copy";
                  e.dataTransfer.setData("application/json", JSON.stringify(app));
                }}
                onDragEnd={() => setDraggedApp(null)}
              >
                <button
                  className="w-10 h-10 rounded-full bg-gray-50 dark:bg-neutral-900 flex items-center justify-center hover:scale-110 transition-transform duration-200 cursor-move"
                  onClick={() => openWindow(app.id, app.name, null)}
                >
                  <IconComponent className="h-6 w-6 text-neutral-500 dark:text-neutral-300" />
                </button>
                <span className="text-xs text-foreground font-medium">{app.name}</span>
              </div>
            </DesktopIconContextMenu>
          );
        })}
      </div>

      {/* System Widgets - positioned absolutely */}
      <div className="hidden lg:block absolute top-8 right-8 space-y-4 z-20">
        <Card className="bg-gray-50 dark:bg-neutral-900 border-gray-200 dark:border-neutral-800 p-4 w-64 rounded-2xl">
          <div className="flex items-center gap-2 mb-2">
            <Cpu className="h-4 w-4 text-neutral-500 dark:text-neutral-300" />
            <span className="text-sm font-medium text-neutral-700 dark:text-white">System Status</span>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-neutral-500 dark:text-neutral-400">CPU Usage</span>
              <span className="text-neutral-700 dark:text-white">23%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-500 dark:text-neutral-400">Active Workflows</span>
              <Badge variant="secondary" className="text-xs bg-neutral-200 dark:bg-neutral-800 text-neutral-700 dark:text-white">
                3
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-500 dark:text-neutral-400">Apps Installed</span>
              <span className="text-neutral-700 dark:text-white">12</span>
            </div>
          </div>
        </Card>

        <Card className="bg-gray-50 dark:bg-neutral-900 border-gray-200 dark:border-neutral-800 p-4 w-64 rounded-2xl">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4 text-neutral-500 dark:text-neutral-300" />
            <span className="text-sm font-medium text-neutral-700 dark:text-white">Recent Activity</span>
          </div>
          <div className="space-y-2 text-xs">
            <div className="text-neutral-500 dark:text-neutral-400">Slack node executed - 2m ago</div>
            <div className="text-neutral-500 dark:text-neutral-400">GitHub workflow started - 5m ago</div>
            <div className="text-neutral-500 dark:text-neutral-400">OpenAI node installed - 12m ago</div>
          </div>
        </Card>

        <Card className="bg-gray-50 dark:bg-neutral-900 border-gray-200 dark:border-neutral-800 p-4 w-64 rounded-2xl">
          <div className="flex items-center gap-2 mb-2">
            <MessageSquare className="h-4 w-4 text-neutral-500 dark:text-neutral-300" />
            <span className="text-sm font-medium text-neutral-700 dark:text-white">AI Assistant</span>
          </div>
          <div className="text-xs text-neutral-500 dark:text-neutral-400 mb-2">Ready to assist with workflow automation</div>
          <Button
            size="sm"
            variant="outline"
            className="w-full text-xs bg-white dark:bg-neutral-800 border-gray-200 dark:border-neutral-700 text-neutral-700 dark:text-white hover:bg-gray-100 dark:hover:bg-neutral-700"
            onClick={() => setIsChatOpen(true)}
          >
            Chat with AI
          </Button>
        </Card>
      </div>

      {/* Windows */}
      {windows.map((window) => (
        <div
          key={window.id}
          className={`absolute glass-effect rounded-lg overflow-hidden shadow-2xl select-none ${
            window.isMinimized ? "hidden" : "block"
          } ${activeWindow === window.id ? "z-50" : "z-40"}`}
          style={{
            left: window.position.x,
            top: window.position.y,
            width: window.size.width,
            height: window.size.height,
          }}
          onClick={() => setActiveWindow(window.id)}
        >
          {!window.isMaximized && (
            <>
              {/* Resize handles */}
              <div
                className="absolute top-0 left-0 w-3 h-3 cursor-nw-resize z-10"
                onMouseDown={(e) => handleMouseDown(e, window.id, "resize", "top-left")}
              />
              <div
                className="absolute top-0 right-0 w-3 h-3 cursor-ne-resize z-10"
                onMouseDown={(e) => handleMouseDown(e, window.id, "resize", "top-right")}
              />
              <div
                className="absolute bottom-0 left-0 w-3 h-3 cursor-sw-resize z-10"
                onMouseDown={(e) => handleMouseDown(e, window.id, "resize", "bottom-left")}
              />
              <div
                className="absolute bottom-0 right-0 w-3 h-3 cursor-se-resize z-10"
                onMouseDown={(e) => handleMouseDown(e, window.id, "resize", "bottom-right")}
              />
              <div
                className="absolute top-0 left-3 right-3 h-1 cursor-n-resize z-10"
                onMouseDown={(e) => handleMouseDown(e, window.id, "resize", "top")}
              />
              <div
                className="absolute bottom-0 left-3 right-3 h-1 cursor-s-resize z-10"
                onMouseDown={(e) => handleMouseDown(e, window.id, "resize", "bottom")}
              />
              <div
                className="absolute left-0 top-3 bottom-3 w-1 cursor-w-resize z-10"
                onMouseDown={(e) => handleMouseDown(e, window.id, "resize", "left")}
              />
              <div
                className="absolute right-0 top-3 bottom-3 w-1 cursor-e-resize z-10"
                onMouseDown={(e) => handleMouseDown(e, window.id, "resize", "right")}
              />
            </>
          )}

          {/* Window Header */}
          <div
            className="flex items-center justify-between p-3 border-b border-border/50 bg-card/50 cursor-grab active:cursor-grabbing"
            onMouseDown={(e) => handleMouseDown(e, window.id, "drag")}
          >
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-green-500/80" />
              </div>
              <span className="text-sm font-medium ml-2">{window.title}</span>
            </div>
            <div className="flex items-center gap-1">
              <Button
                size="sm"
                variant="ghost"
                className="h-6 w-6 p-0"
                onClick={(e) => {
                  e.stopPropagation()
                  minimizeWindow(window.id)
                }}
              >
                <Minimize2 className="h-3 w-3" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="h-6 w-6 p-0"
                onClick={(e) => {
                  e.stopPropagation()
                  toggleMaximizeWindow(window.id)
                }}
              >
                <Maximize2 className="h-3 w-3" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="h-6 w-6 p-0"
                onClick={(e) => {
                  e.stopPropagation()
                  closeWindow(window.id)
                }}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          </div>

          {/* Window Content */}
          <div className="h-full overflow-auto" style={{ height: "calc(100% - 57px)" }}>
            {window.component}
          </div>
        </div>
      ))}

      {/* Chat Interface */}
      <ChatInterface isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />

      {/* Apple-style Floating Dock - Bottom */}
      <div className="absolute bottom-[35px] left-1/2 transform -translate-x-1/2 pointer-events-auto z-20">
        <FloatingDockDemo 
          openWindow={(id, title, component) => {
            // Find the proper component for each app
            let appComponent;
            switch(id) {
              case "app-store":
                appComponent = <MacAppStore />;
                break;
              case "installed":
                appComponent = <InstalledApps />;
                break;
              case "workflows":
                appComponent = <WorkflowCanvas />;
                break;
              case "terminal":
                appComponent = <Terminal />;
                break;
              case "monitor":
                appComponent = <SystemMonitor />;
                break;
              case "github":
                appComponent = <div>GitHub Desktop</div>;
                break;
              case "chatgpt":
                appComponent = <div>ChatGPT</div>;
                break;
              case "slack":
                appComponent = <div>Slack</div>;
                break;
              default:
                appComponent = component;
            }
            openWindow(id, title, appComponent);
          }}
          openWindows={windows.map(w => w.id)}
          dockApps={dockApps}
          onDrop={(app) => {
            // Add app to dock if not already there
            if (!dockApps.find(dockApp => dockApp.id === app.id)) {
              setDockApps(prev => [...prev, app]);
            }
          }}
        />
      </div>

      {/* VS Code-style Footer */}
      <div className="absolute bottom-0 left-0 right-0 h-[28px] bg-gray-200/0 dark:bg-black/0 z-30 select-none">
        <div className="flex items-center justify-between h-full text-[11px] text-black dark:text-white px-2">
          {/* Left side */}
          <div className="flex items-center h-full">
            {/* Branch indicator */}
            <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10 flex items-center gap-1">
              <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 16 16">
                <path d="M5 3.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm0 2.122a2.25 2.25 0 10-1.5 0v.878A2.25 2.25 0 005.75 8.5h1.5v2.128a2.251 2.251 0 101.5 0V8.5h1.5a2.25 2.25 0 002.25-2.25v-.878a2.25 2.25 0 10-1.5 0v.878a.75.75 0 01-.75.75h-4.5A.75.75 0 015 6.25v-.878zm3.75 7.378a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm3-8.75a.75.75 0 100-1.5.75.75 0 000 1.5z"/>
              </svg>
              <span>main</span>
            </button>

            {/* Sync status */}
            <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10 flex items-center gap-1">
              <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 16 16">
                <path fillRule="evenodd" d="M1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0zM8 0a8 8 0 100 16A8 8 0 008 0zM6.379 5.227A.25.25 0 006 5.442v5.117a.25.25 0 00.379.214l4.264-2.559a.25.25 0 000-.428L6.379 5.227z"/>
              </svg>
            </button>

            {/* Problems/warnings */}
            <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10 flex items-center gap-1">
              <X className="h-3 w-3" />
              <span>0</span>
              <AlertCircle className="h-3 w-3 ml-1" />
              <span>0</span>
            </button>

            {/* Active Window */}
            {activeWindow && (
              <div className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10 flex items-center">
                <span>{windows.find((w) => w.id === activeWindow)?.title}</span>
              </div>
            )}
          </div>

          {/* Right side - moved power button away from edge */}
          <div className="flex items-center h-full">
            {/* Language mode */}
            <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10">
              TypeScript React
            </button>

            {/* Encoding */}
            <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10">
              UTF-8
            </button>

            {/* End of line */}
            <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10">
              LF
            </button>

            {/* Spaces */}
            <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10">
              Spaces: 2
            </button>

            {/* Windows counter */}
            <div className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10 flex items-center">
              <Folder className="h-3 w-3 mr-1" />
              <span>{windows.length}</span>
            </div>

            {/* Notifications */}
            <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10">
              <Bell className="h-3 w-3" />
            </button>

            {/* Theme Toggle */}
            <button 
              className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10"
              onClick={() => setIsDarkMode(!isDarkMode)}
            >
              {isDarkMode ? <Sun className="h-3 w-3" /> : <Moon className="h-3 w-3" />}
            </button>

            {/* System Control Menu */}
            <div className="h-full hover:bg-black/10 dark:hover:bg-white/10">
              <SystemControlMenu onLogout={handleLogout} />
            </div>
          </div>
        </div>
      </div>

      {/* Desktop Folders */}
      {desktopFolders.map((folder) => (
        <div
          key={folder.id}
          className="absolute z-20 flex flex-col items-center gap-2"
          style={{ left: folder.x, top: folder.y }}
        >
          <button
            className="w-10 h-10 rounded-full bg-gray-50 dark:bg-neutral-900 flex items-center justify-center hover:scale-110 transition-transform duration-200"
            onDoubleClick={() => openWindow(`folder-${folder.id}`, folder.name, <div>Folder: {folder.name}</div>)}
          >
            <Folder className="h-6 w-6 text-neutral-500 dark:text-neutral-300" />
          </button>
          <span className="text-xs text-foreground font-medium">{folder.name}</span>
        </div>
      ))}

      <BackgroundBeams paused={isMouseActive} />

      </div>
    </DesktopContextMenu>
  )
}
