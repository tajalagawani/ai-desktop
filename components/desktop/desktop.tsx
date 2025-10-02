"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Cpu,
  Clock,
  MessageSquare,
  X,
  Sun,
  Moon,
  Folder,
  AlertCircle,
  Bell,
  MemoryStick as Memory,
  HardDrive,
} from "lucide-react"
import { MacAppStore } from "@/components/apps/mac-app-store"
import { InstalledApps } from "@/components/apps/installed-apps"
import { WorkflowCanvas } from "@/components/apps/workflow-canvas"
import { SystemMonitor } from "@/components/apps/system-monitor"
import { ChatInterface } from "@/components/apps/chat-interface"
import { Terminal } from "@/components/apps/terminal"
import { Changelog } from "@/components/apps/changelog"
import { BackgroundBeams } from "@/components/ui/background-beams"
import { TwoFactorAuth } from "@/components/auth/two-factor-auth"
import { SystemControlMenu } from "@/components/desktop/system-control-menu"
import { FloatingDockDemo } from "@/components/desktop/floating-dock-demo"
import { DesktopContextMenu } from "@/components/desktop/desktop-context-menu"
import { DesktopIconContextMenu } from "@/components/desktop/desktop-icon-context-menu"
import { Taskbar } from "@/components/desktop/taskbar"
import { FileManager } from "@/components/apps/file-manager"
import { Window } from "@/components/desktop/window"
import { Widget } from "@/components/desktop/widget"
import type { SystemStats } from "@/lib/system-stats"

// Import data and utilities
import {
  DOCK_APPS,
  INSTALLED_APPS,
  SYSTEM_STATUS,
  RECENT_ACTIVITY
} from "@/data/desktop-apps"
import { useDesktop, useMouseActivity, useTheme, useDockApps } from "@/hooks/use-desktop"
import { getIcon, getIconProps } from "@/utils/icon-mapper"

// Component map for dynamic loading
const getAppComponent = (id: string): React.ReactNode => {
  const componentMap: Record<string, React.ReactNode> = {
    "app-store": <MacAppStore />,
    "installed": <InstalledApps />,
    "workflows": <WorkflowCanvas />,
    "terminal": <Terminal />,
    "changelog": <Changelog />,
    "monitor": <SystemMonitor />,
    "file-manager": <FileManager />,
    "github": <div>GitHub Desktop</div>,
    "chatgpt": <div>ChatGPT</div>,
    "slack": <div>Slack</div>,
  }
  return componentMap[id] || null
}

export function Desktop() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [draggedApp, setDraggedApp] = useState<any>(null)
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null)

  // Custom hooks for clean state management
  const {
    windows,
    activeWindow,
    screenSize,
    desktopFolders,
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
  } = useDesktop()

  const isMouseActive = useMouseActivity(3000)
  const { isDarkMode, toggleTheme } = useTheme()
  const { dockApps, addToDock, removeFromDock } = useDockApps(DOCK_APPS)

  // Fetch system stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/system-stats')
        if (response.ok) {
          const data = await response.json()
          setSystemStats(data)
        }
      } catch (error) {
        console.error('Error fetching system stats:', error)
      }
    }

    if (isAuthenticated) {
      fetchStats()
      // Update every 3 seconds
      const interval = setInterval(fetchStats, 3000)
      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  // Handle window operations
  const handleOpenWindow = (id: string, title: string) => {
    const component = getAppComponent(id)
    openWindow(id, title, component)

    // Auto-maximize changelog window
    if (id === "changelog") {
      setTimeout(() => toggleMaximizeWindow(id), 100)
    }
  }

  const handleTaskbarAction = (windowId: string, action: string) => {
    const actions: Record<string, () => void> = {
      minimize: () => minimizeWindow(windowId),
      maximize: () => toggleMaximizeWindow(windowId),
      close: () => closeWindow(windowId),
      activate: () => restoreWindow(windowId),
    }
    actions[action]?.()
  }

  // Handle context menu actions
  const handleContextMenuAction = (action: string) => {
    const actions: Record<string, () => void> = {
      refresh: () => window.location.reload(),
      "new-folder": () => createFolder("New Folder", 100, 100),
      "sort-name": () => console.log("Sort by name"),
      "sort-date": () => console.log("Sort by date"),
      "view-large": () => console.log("Large icons view"),
      "view-grid": () => console.log("Grid view"),
      settings: () => handleOpenWindow("settings", "Desktop Settings"),
      properties: () => handleOpenWindow("properties", "Desktop Properties"),
    }
    actions[action]?.()
  }

  const handleIconContextMenuAction = (action: string, appId: string) => {
    const app = INSTALLED_APPS.find(a => a.id === appId)
    
    const actions: Record<string, () => void> = {
      open: () => app && handleOpenWindow(app.id, app.name),
      pause: () => console.log(`Pausing app: ${appId}`),
      resume: () => console.log(`Resuming app: ${appId}`),
      rename: () => {
        const newName = prompt("Enter new name:")
        if (newName) console.log(`Renaming ${appId} to ${newName}`)
      },
      copy: () => console.log(`Copying app: ${appId}`),
      pin: () => console.log(`Pinning app: ${appId}`),
      unpin: () => console.log(`Unpinning app: ${appId}`),
      "add-to-dock": () => app && addToDock(app),
      settings: () => console.log(`Opening settings for: ${appId}`),
      properties: () => console.log(`Opening properties for: ${appId}`),
      delete: () => {
        if (confirm(`Delete this app?`)) {
          console.log(`Deleting app: ${appId}`)
        }
      },
    }
    actions[action]?.()
  }

  if (!isAuthenticated) {
    return <TwoFactorAuth onAuthenticated={() => setIsAuthenticated(true)} />
  }

  return (
    <DesktopContextMenu onAction={handleContextMenuAction}>
      <div className="h-screen w-full bg-background relative antialiased overflow-hidden">
        {/* Desktop Icons */}
        <DesktopIcons 
          onOpenWindow={handleOpenWindow}
          installedApps={INSTALLED_APPS}
          windows={windows}
          onIconContextMenuAction={handleIconContextMenuAction}
          setDraggedApp={setDraggedApp}
        />

        {/* System Widgets */}
        <SystemWidgets
          systemStatus={SYSTEM_STATUS}
          recentActivity={RECENT_ACTIVITY}
          systemStats={systemStats}
        />

        {/* Windows */}
        {windows.map((window) => (
          <Window
            key={window.id}
            id={window.id}
            title={window.title}
            isActive={activeWindow === window.id}
            isMinimized={window.isMinimized}
            isMaximized={window.isMaximized}
            position={window.position}
            size={window.size}
            onClose={closeWindow}
            onMinimize={minimizeWindow}
            onMaximize={toggleMaximizeWindow}
            onDragStart={(e, id) => handleMouseDown(e, id, "drag")}
            onResizeStart={(e, id, handle) => handleMouseDown(e, id, "resize", handle)}
            onFocus={setActiveWindow}
          >
            {window.component}
          </Window>
        ))}

        {/* Chat Interface */}
        <ChatInterface isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />

        {/* Floating Dock */}
        <div className="absolute bottom-[35px] left-1/2 transform -translate-x-1/2 pointer-events-auto z-20">
          <FloatingDockDemo 
            openWindow={handleOpenWindow}
            openWindows={windows.map(w => w.id)}
            dockApps={dockApps}
            onDrop={addToDock}
          />
        </div>

        {/* Footer Bar */}
        <FooterBar
          isDarkMode={isDarkMode}
          onToggleTheme={toggleTheme}
          activeWindow={activeWindow}
          windows={windows}
          onLogout={() => setIsAuthenticated(false)}
          handleOpenWindow={handleOpenWindow}
        />

        {/* Desktop Folders */}
        {desktopFolders.map((folder) => (
          <DesktopFolder
            key={folder.id}
            folder={folder}
            onOpen={() => handleOpenWindow(`folder-${folder.id}`, folder.name)}
          />
        ))}

        <BackgroundBeams paused={isMouseActive} />

        {/* Taskbar */}
        <Taskbar 
          windows={windows}
          activeWindow={activeWindow}
          onWindowAction={handleTaskbarAction}
        />
      </div>
    </DesktopContextMenu>
  )
}

// Sub-components
function DesktopIcons({ 
  onOpenWindow, 
  installedApps, 
  windows, 
  onIconContextMenuAction,
  setDraggedApp 
}: any) {
  return (
    <>
      {/* System Icons */}
      <div className="absolute top-4 left-4 md:top-8 md:left-8 grid grid-cols-1 gap-3 md:gap-4 z-20">
        {DOCK_APPS.filter(app => app.isSystem).map(app => {
          const IconComponent = getIcon(app.icon)
          return (
            <div key={app.id} className="flex flex-col items-center gap-2">
              <button
                className="w-10 h-10 rounded-full bg-gray-200 dark:bg-neutral-800 flex items-center justify-center hover:scale-[1.2] transition-transform duration-200"
                onClick={() => onOpenWindow(app.id, app.name)}
              >
                <IconComponent className="h-6 w-6 text-neutral-600 dark:text-neutral-300" />
              </button>
              <span className="text-xs text-foreground font-medium">{app.name}</span>
            </div>
          )
        })}
      </div>

      {/* Installed Apps */}
      <div className="absolute top-4 right-4 md:top-8 md:right-80 grid grid-cols-1 gap-3 md:gap-4 z-20">
        {installedApps.map((app: any) => {
          const IconComponent = getIcon(app.icon)
          const isRunning = windows.some((w: any) => w.id === app.id)
          
          return (
            <DesktopIconContextMenu
              key={app.id}
              appId={app.id}
              appName={app.name}
              isRunning={isRunning}
              isPinned={true}
              onAction={onIconContextMenuAction}
            >
              <div 
                className="flex flex-col items-center gap-2"
                draggable
                onDragStart={(e) => {
                  setDraggedApp(app)
                  e.dataTransfer.effectAllowed = "copy"
                  e.dataTransfer.setData("application/json", JSON.stringify(app))
                }}
                onDragEnd={() => setDraggedApp(null)}
              >
                <button
                  className="w-10 h-10 rounded-full bg-gray-50 dark:bg-neutral-900 flex items-center justify-center hover:scale-110 transition-transform duration-200 cursor-move"
                  onClick={() => onOpenWindow(app.id, app.name)}
                >
                  <IconComponent className="h-6 w-6 text-neutral-500 dark:text-neutral-300" />
                </button>
                <span className="text-xs text-foreground font-medium">{app.name}</span>
              </div>
            </DesktopIconContextMenu>
          )
        })}
      </div>
    </>
  )
}

function SystemWidgets({ systemStatus, recentActivity, systemStats }: any) {
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
  }

  return (
    <div className="hidden lg:block absolute top-8 right-8 space-y-4 z-20">
      {/* CPU Widget */}
      <Widget icon={Cpu} title="CPU">
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-neutral-500 dark:text-neutral-400">Usage</span>
            <span className="text-neutral-700 dark:text-white font-mono">
              {systemStats?.cpu.usage ?? systemStatus.cpu.usage}%
            </span>
          </div>
          {systemStats && (
            <>
              <div className="flex justify-between">
                <span className="text-neutral-500 dark:text-neutral-400">Cores</span>
                <span className="text-neutral-700 dark:text-white">{systemStats.cpu.cores}</span>
              </div>
              <div className="text-xs text-neutral-500 dark:text-neutral-400 truncate" title={systemStats.cpu.model}>
                {systemStats.cpu.model}
              </div>
            </>
          )}
        </div>
      </Widget>

      {/* Memory Widget */}
      <Widget icon={Memory} title="Memory">
        <div className="space-y-2 text-sm">
          {systemStats ? (
            <>
              <div className="flex justify-between">
                <span className="text-neutral-500 dark:text-neutral-400">Usage</span>
                <span className="text-neutral-700 dark:text-white font-mono">
                  {systemStats.memory.usagePercent}%
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-neutral-500 dark:text-neutral-400">Used</span>
                <span className="text-neutral-700 dark:text-white font-mono">
                  {formatBytes(systemStats.memory.used)}
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-neutral-500 dark:text-neutral-400">Total</span>
                <span className="text-neutral-700 dark:text-white font-mono">
                  {formatBytes(systemStats.memory.total)}
                </span>
              </div>
            </>
          ) : (
            <div className="text-xs text-neutral-500 dark:text-neutral-400">Loading...</div>
          )}
        </div>
      </Widget>

      {/* Storage Widget */}
      <Widget icon={HardDrive} title="Storage">
        <div className="space-y-2 text-sm">
          {systemStats && systemStats.disk.total > 0 ? (
            <>
              <div className="flex justify-between">
                <span className="text-neutral-500 dark:text-neutral-400">Usage</span>
                <span className="text-neutral-700 dark:text-white font-mono">
                  {systemStats.disk.usagePercent}%
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-neutral-500 dark:text-neutral-400">Used</span>
                <span className="text-neutral-700 dark:text-white font-mono">
                  {formatBytes(systemStats.disk.used)}
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-neutral-500 dark:text-neutral-400">Total</span>
                <span className="text-neutral-700 dark:text-white font-mono">
                  {formatBytes(systemStats.disk.total)}
                </span>
              </div>
            </>
          ) : (
            <div className="text-xs text-neutral-500 dark:text-neutral-400">Loading...</div>
          )}
        </div>
      </Widget>

      {/* Recent Activity Widget */}
      <Widget icon={Clock} title="Recent Activity">
        <div className="space-y-2 text-xs">
          {recentActivity.slice(0, 3).map((activity: any) => (
            <div key={activity.id} className="text-neutral-500 dark:text-neutral-400">
              {activity.action} - {activity.time}
            </div>
          ))}
        </div>
      </Widget>

      {/* AI Assistant Widget */}
      <Widget icon={MessageSquare} title="AI Assistant">
        <div className="text-xs text-neutral-500 dark:text-neutral-400 mb-2">
          Ready to assist with workflow automation
        </div>
        <Button
          size="sm"
          variant="outline"
          className="w-full text-xs bg-white dark:bg-neutral-800 border-gray-200 dark:border-neutral-700 text-neutral-700 dark:text-white hover:bg-gray-100 dark:hover:bg-neutral-700"
          onClick={() => window.dispatchEvent(new CustomEvent('trigger-dock-chat'))}
        >
          Chat with AI
        </Button>
      </Widget>
    </div>
  )
}

function FooterBar({ isDarkMode, onToggleTheme, activeWindow, windows, onLogout, handleOpenWindow }: any) {
  return (
    <div className="absolute bottom-0 left-0 right-0 h-[28px] bg-gray-200/0 dark:bg-black/0 z-30 select-none">
      <div className="flex items-center justify-between h-full text-[11px] text-black dark:text-white px-2">
        {/* Left side */}
        <div className="flex items-center h-full">
          <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10 flex items-center gap-1">
            <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 16 16">
              <path d="M5 3.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm0 2.122a2.25 2.25 0 10-1.5 0v.878A2.25 2.25 0 005.75 8.5h1.5v2.128a2.251 2.251 0 101.5 0V8.5h1.5a2.25 2.25 0 002.25-2.25v-.878a2.25 2.25 0 10-1.5 0v.878a.75.75 0 01-.75.75h-4.5A.75.75 0 015 6.25v-.878zm3.75 7.378a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm3-8.75a.75.75 0 100-1.5.75.75 0 000 1.5z"/>
            </svg>
            <span>main</span>
          </button>
          
          <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10 flex items-center gap-1">
            <X className="h-3 w-3" />
            <span>0</span>
            <AlertCircle className="h-3 w-3 ml-1" />
            <span>0</span>
          </button>
          
          {activeWindow && (
            <div className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10 flex items-center">
              <span>{windows.find((w: any) => w.id === activeWindow)?.title}</span>
            </div>
          )}
        </div>

        {/* Right side */}
        <div className="flex items-center h-full">
          <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10">
            TypeScript React
          </button>
          
          <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10">
            UTF-8
          </button>
          
          <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10">
            LF
          </button>
          
          <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10">
            Spaces: 2
          </button>
          
          <div className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10 flex items-center">
            <Folder className="h-3 w-3 mr-1" />
            <span>{windows.length}</span>
          </div>
          
          <button className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10">
            <Bell className="h-3 w-3" />
          </button>
          
          <button 
            className="h-full px-2 hover:bg-black/10 dark:hover:bg-white/10"
            onClick={onToggleTheme}
          >
            {isDarkMode ? <Sun className="h-3 w-3" /> : <Moon className="h-3 w-3" />}
          </button>
          
          <div className="h-full hover:bg-black/10 dark:hover:bg-white/10">
            <SystemControlMenu onLogout={onLogout} openWindow={handleOpenWindow} />
          </div>
        </div>
      </div>
    </div>
  )
}

function DesktopFolder({ folder, onOpen }: any) {
  return (
    <div
      className="absolute z-20 flex flex-col items-center gap-2"
      style={{ left: folder.x, top: folder.y }}
    >
      <button
        className="w-10 h-10 rounded-full bg-gray-50 dark:bg-neutral-900 flex items-center justify-center hover:scale-110 transition-transform duration-200"
        onDoubleClick={onOpen}
      >
        <Folder className="h-6 w-6 text-neutral-500 dark:text-neutral-300" />
      </button>
      <span className="text-xs text-foreground font-medium">{folder.name}</span>
    </div>
  )
}