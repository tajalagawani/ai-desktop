"use client"

import React, { useState, useEffect, useCallback } from "react"
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
  Network,
  Thermometer,
  Activity as ProcessIcon,
} from "lucide-react"
import { SystemMonitor } from "@/components/apps/system-monitor"
import { ChatInterface } from "@/components/apps/chat-interface"
import { Terminal } from "@/components/apps/terminal"
import { ClaudeCLI } from "@/components/apps/claude-cli"
import { Changelog } from "@/components/apps/changelog"
import { FileManager } from "@/components/apps/file-manager"
import { ServiceManager } from "@/components/apps/service-manager"
import { ServiceDetails } from "@/components/apps/service-details"
import { DesktopSettings } from "@/components/apps/desktop-settings"
import { WidgetWindow } from "@/components/apps/widget-window"
import { GitHubApp } from "@/components/apps/github"

import { BackgroundBeams } from "@/components/ui/background-beams"
import { TwoFactorAuth } from "@/components/auth/two-factor-auth"
import { SystemControlMenu } from "@/components/desktop/system-control-menu"
import { FloatingDockDemo } from "@/components/desktop/floating-dock-demo"
import { TopDock } from "@/components/desktop/top-dock"
import { DesktopContextMenu } from "@/components/desktop/desktop-context-menu"
import { ServiceIconContextMenu } from "@/components/desktop/service-icon-context-menu"
import { Taskbar } from "@/components/desktop/taskbar"
import { Window } from "@/components/desktop/window"
import { Widget } from "@/components/desktop/widget"
import type { SystemStats } from "@/lib/system-stats"

// Import data and utilities
import {
  DOCK_APPS,
  SYSTEM_STATUS,
  RECENT_ACTIVITY
} from "@/data/desktop-apps"
import { useDesktop, useMouseActivity, useTheme, useDockApps } from "@/hooks/use-desktop"
import { getIcon, getIconProps } from "@/utils/icon-mapper"

// Component map for dynamic loading
const getAppComponent = (
  id: string,
  openWindowFn?: (id: string, title: string, component: React.ReactNode) => void,
  toggleMaximizeFn?: (id: string) => void,
  bringToFrontFn?: (id: string) => void,
  currentBackground?: string,
  onBackgroundChange?: (bg: string) => void
): React.ReactNode => {
  const componentMap: Record<string, React.ReactNode> = {
    "terminal": <Terminal />,
    "claude-cli": <ClaudeCLI />,
    "changelog": <Changelog />,
    "monitor": <SystemMonitor />,
    "file-manager": <FileManager />,
    "service-manager": <ServiceManager openWindow={openWindowFn} toggleMaximizeWindow={toggleMaximizeFn} bringToFront={bringToFrontFn} />,
    "system-widgets": <WidgetWindow />,
    "desktop-settings": <DesktopSettings currentBackground={currentBackground || 'image-abstract'} onBackgroundChange={onBackgroundChange || (() => {})} />,
    "github-desktop": <GitHubApp />,
  }
  return componentMap[id] || null
}

interface InstalledService {
  id: string
  name: string
  icon: string
  iconType?: 'lucide' | 'image'
  ports?: number[]
  status: string
}

// Background configurations
const BACKGROUNDS: Record<string, { light: string; dark: string; type: 'gradient' | 'image' | 'component' }> = {
  'component-beams': {
    type: 'component',
    light: 'bg-[oklch(0.97_0.00_0)]',
    dark: 'bg-[oklch(0.20_0.00_0)]'
  },
  'image-abstract': {
    type: 'image',
    light: 'url(/backgrounds/abstract-art.jpg) no-repeat center / cover',
    dark: 'url(/backgrounds/abstract-art.jpg) no-repeat center / cover'
  },
  'image-blue': {
    type: 'image',
    light: 'url(/backgrounds/blue-abstract.avif) no-repeat center / cover',
    dark: 'url(/backgrounds/blue-abstract.avif) no-repeat center / cover'
  }
}

export function Desktop() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null)
  const [installedServices, setInstalledServices] = useState<InstalledService[]>([])
  const [currentBackground, setCurrentBackground] = useState<string>('image-abstract')

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

  const { isDarkMode, toggleTheme } = useTheme()
  const { dockApps, addToDock, removeFromDock } = useDockApps(DOCK_APPS)
  const isMouseActive = useMouseActivity(3000)

  // Load background from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('desktop-background')
    if (saved && BACKGROUNDS[saved]) {
      setCurrentBackground(saved)
    }
  }, [])

  // Handle background change
  const handleBackgroundChange = (bgId: string) => {
    console.log('Background changing to:', bgId)
    setCurrentBackground(bgId)
    localStorage.setItem('desktop-background', bgId)
  }

  // Get current background style
  const bg = BACKGROUNDS[currentBackground] || BACKGROUNDS['image-abstract']
  const isComponentBg = bg.type === 'component'
  const backgroundStyle = isComponentBg ? '' : (isDarkMode ? bg.dark : bg.light)
  const backgroundClass = isComponentBg ? (isDarkMode ? bg.dark : bg.light) : ''

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

  // Fetch installed services
  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await fetch('/api/services')
        if (response.ok) {
          const data = await response.json()
          const installed = data.services?.filter((s: InstalledService) =>
            s.status !== 'not-installed' && s.ports && s.ports.length > 0
          ) || []
          setInstalledServices(installed)
        }
      } catch (error) {
        console.error('Error fetching services:', error)
      }
    }

    if (isAuthenticated) {
      fetchServices()
      // Update every 2 seconds for faster UI updates
      const interval = setInterval(fetchServices, 2000)
      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  // Handle window operations
  const handleOpenWindow = useCallback((id: string, title: string) => {
    const component = getAppComponent(id, openWindow, toggleMaximizeWindow, setActiveWindow, currentBackground, handleBackgroundChange)
    openWindow(id, title, component)

    // Auto-maximize changelog window
    if (id === "changelog") {
      setTimeout(() => toggleMaximizeWindow(id), 100)
    }
  }, [openWindow, toggleMaximizeWindow, setActiveWindow, currentBackground, handleBackgroundChange])

  // Listen for open-security-center event from NodeAuthRequest component
  useEffect(() => {
    const handleOpenSecurityCenter = (event: CustomEvent) => {
      const { nodeType } = event.detail || {};

      // Check if Security Center is already open
      const existingWindow = windows.find(w => w.id === 'security-center');
      if (existingWindow) {
        // Already open, just bring to front
        setActiveWindow('security-center');
      } else {
        // Open new window
        handleOpenWindow('security-center', 'Security Center');
        // Bring to front after opening
        setTimeout(() => {
          setActiveWindow('security-center');
        }, 100);
      }
      // TODO: Pass nodeType to SecurityCenter to pre-select the node
    };

    window.addEventListener('open-security-center', handleOpenSecurityCenter as EventListener);
    return () => {
      window.removeEventListener('open-security-center', handleOpenSecurityCenter as EventListener);
    };
  }, [handleOpenWindow, windows, setActiveWindow])

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
      settings: () => handleOpenWindow("desktop-settings", "Desktop Settings"),
      properties: () => handleOpenWindow("properties", "Desktop Properties"),
    }
    actions[action]?.()
  }

  if (!isAuthenticated) {
    return <TwoFactorAuth onAuthenticated={() => setIsAuthenticated(true)} />
  }

  return (
    <DesktopContextMenu onAction={handleContextMenuAction}>
      <div
        className={`h-screen w-full relative antialiased overflow-hidden ${backgroundClass}`}
        style={backgroundStyle ? {
          background: backgroundStyle
        } : undefined}
      >
        {/* Top Dock */}
        <TopDock />

        {/* Desktop Icons */}
        <DesktopIcons
          onOpenWindow={handleOpenWindow}
          openWindow={openWindow}
          installedServices={installedServices}
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

        {/* Background Component (if component type) */}
        {isComponentBg && <BackgroundBeams paused={isMouseActive} />}

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
  openWindow,
  installedServices,
}: any) {

  const handleServiceClick = (service: any) => {
    if (service.status !== 'running') return // Only open if running
    const port = service.ports?.[0]
    if (!port) return
    const url = `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:${port}`
    window.open(url, '_blank', 'noopener,noreferrer')
  }

  const handleServiceAction = async (action: string, service: any) => {
    const actions: Record<string, () => Promise<void>> = {
      details: async () => {
        // Open service details window
        const component = <ServiceDetails serviceId={service.id} />
        openWindow(`service-${service.id}`, service.name, component)
      },
      open: async () => {
        if (service.status === 'running') {
          handleServiceClick(service)
        }
      },
      start: async () => {
        await fetch('/api/services', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'start', serviceId: service.id })
        })
      },
      stop: async () => {
        await fetch('/api/services', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'stop', serviceId: service.id })
        })
      },
      restart: async () => {
        await fetch('/api/services', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'restart', serviceId: service.id })
        })
      },
      remove: async () => {
        if (confirm(`Delete ${service.name}?\n\nThis will:\n• Stop and remove the container\n• Delete all volumes\n• Delete Docker images\n• Close firewall ports\n\nThis action cannot be undone.`)) {
          await fetch('/api/services', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'remove', serviceId: service.id })
          })
        }
      },
      logs: async () => {
        // Open service details window (it shows logs)
        const component = <ServiceDetails serviceId={service.id} />
        openWindow(`service-${service.id}`, service.name, component)
      },
      properties: async () => {
        // Open service details window (it shows properties)
        const component = <ServiceDetails serviceId={service.id} />
        openWindow(`service-${service.id}`, service.name, component)
      }
    }
    await actions[action]?.()
  }

  return (
    <>
      {/* System Icons */}
      <div className="absolute top-4 left-4 md:top-8 md:left-8 grid grid-cols-1 gap-3 md:gap-4 z-20">
        {DOCK_APPS.filter(app => app.isSystem).map(app => {
          const isImageIcon = app.iconType === "image"
          const IconComponent = !isImageIcon ? getIcon(app.icon) : null

          return (
            <div key={app.id} className="flex flex-col items-center gap-2">
              <button
                className="w-10 h-10 rounded-full bg-muted flex items-center justify-center hover:scale-[1.2] transition-transform duration-200 overflow-hidden"
                onClick={() => onOpenWindow(app.id, app.name)}
              >
                {isImageIcon ? (
                  <img src={app.icon} alt={app.name} className="h-8 w-8 object-contain" />
                ) : (
                  IconComponent && <IconComponent className="h-6 w-6 text-foreground" />
                )}
              </button>
              <span className="text-xs text-foreground font-normal">{app.name}</span>
            </div>
          )
        })}
      </div>

      {/* Installed Services */}
      <div className="absolute top-4 right-4 md:top-8 md:right-80 grid grid-cols-1 gap-3 md:gap-4 z-20">
        {installedServices.map((service: any) => {
          const isImageIcon = service.iconType === "image"
          const IconComponent = !isImageIcon ? getIcon(service.icon) : null
          const isInstalling = service.status === 'installing'
          const isRunning = service.status === 'running'
          const isStopped = service.status === 'stopped' || service.status === 'exited'

          return (
            <ServiceIconContextMenu
              key={service.id}
              serviceName={service.name}
              isRunning={isRunning}
              isStopped={isStopped}
              isInstalling={isInstalling}
              onAction={(action) => handleServiceAction(action, service)}
            >
              <div className="flex flex-col items-center gap-1 relative">
                <button
                  className={`w-10 h-10 rounded-full bg-muted flex items-center justify-center transition-all duration-200 overflow-hidden ${
                    isRunning ? 'hover:scale-[1.2] cursor-pointer' : 'cursor-default'
                  } ${
                    isStopped || isInstalling ? 'opacity-50' : ''
                  }`}
                  onClick={() => handleServiceClick(service)}
                  disabled={!isRunning}
                >
                  {isImageIcon ? (
                    <img
                      src={service.icon}
                      alt={service.name}
                      className={`h-8 w-8 object-contain ${isInstalling ? 'animate-pulse' : ''}`}
                    />
                  ) : (
                    IconComponent && <IconComponent className={`h-6 w-6 text-foreground ${isInstalling ? 'animate-pulse' : ''}`} />
                  )}
                </button>

                {/* Status indicator */}
                {isInstalling && (
                  <div className="w-10 h-1 bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-primary animate-pulse w-full" />
                  </div>
                )}

                <span className={`text-xs font-normal ${isRunning ? 'text-foreground' : 'text-muted-foreground'}`}>
                  {service.name}
                </span>
              </div>
            </ServiceIconContextMenu>
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

  const formatBytesPerSec = (bytesPerSec: number): string => {
    return `${formatBytes(bytesPerSec)}/s`
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
              <div className="flex justify-between text-xs">
                <span className="text-neutral-500 dark:text-neutral-400">Cores</span>
                <span className="text-neutral-700 dark:text-white">{systemStats.cpu.cores}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-neutral-500 dark:text-neutral-400">Speed</span>
                <span className="text-neutral-700 dark:text-white">{systemStats.cpu.speed} GHz</span>
              </div>
              {systemStats.cpu.temperature && (
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-500 dark:text-neutral-400">Temp</span>
                  <span className="text-neutral-700 dark:text-white">{systemStats.cpu.temperature}°C</span>
                </div>
              )}
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

      {/* Network Widget */}
      {systemStats?.network && (
        <Widget icon={Network} title="Network">
          <div className="space-y-2 text-sm">
            <div className="flex justify-between text-xs">
              <span className="text-neutral-500 dark:text-neutral-400">↓ Down</span>
              <span className="text-neutral-700 dark:text-white font-mono">
                {formatBytesPerSec(systemStats.network.rxSec)}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-neutral-500 dark:text-neutral-400">↑ Up</span>
              <span className="text-neutral-700 dark:text-white font-mono">
                {formatBytesPerSec(systemStats.network.txSec)}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-neutral-500 dark:text-neutral-400">Total RX</span>
              <span className="text-neutral-700 dark:text-white font-mono">
                {formatBytes(systemStats.network.rx)}
              </span>
            </div>
          </div>
        </Widget>
      )}

      {/* Processes Widget */}
      {systemStats?.processes && (
        <Widget icon={ProcessIcon} title="Processes">
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-neutral-500 dark:text-neutral-400">Total</span>
              <span className="text-neutral-700 dark:text-white font-mono">
                {systemStats.processes.all}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-neutral-500 dark:text-neutral-400">Running</span>
              <span className="text-neutral-700 dark:text-white">{systemStats.processes.running}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-neutral-500 dark:text-neutral-400">Sleeping</span>
              <span className="text-neutral-700 dark:text-white">{systemStats.processes.sleeping}</span>
            </div>
          </div>
        </Widget>
      )}

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
        className="w-10 h-10 rounded-full bg-muted flex items-center justify-center hover:scale-110 transition-transform duration-200"
        onDoubleClick={onOpen}
      >
        <Folder className="h-6 w-6 text-foreground" />
      </button>
      <span className="text-xs text-foreground font-normal">{folder.name}</span>
    </div>
  )
}