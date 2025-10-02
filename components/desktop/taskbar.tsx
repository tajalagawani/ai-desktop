"use client"

import React, { useState } from "react"
import { Tabs } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { motion, AnimatePresence } from "framer-motion"
import { 
  Minimize2, 
  Maximize2, 
  X, 
  Monitor,
  Grid3X3,
  ChevronUp
} from "lucide-react"

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

interface TaskbarProps {
  windows: Window[]
  activeWindow: string | null
  onWindowAction: (windowId: string, action: "minimize" | "maximize" | "close" | "activate") => void
}

export function Taskbar({ windows, activeWindow, onWindowAction }: TaskbarProps) {
  const [showTaskbar, setShowTaskbar] = useState(false)

  // Filter out closed windows and create tabs data
  const openWindows = windows.filter(window => window)
  
  const tabsData = openWindows.map((window) => ({
    title: window.title,
    value: window.id,
    content: (
      <div className="w-full overflow-hidden relative h-full rounded-3xl p-8 md:p-12 bg-gray-100 dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h3 className="text-4xl md:text-6xl font-bold mb-2 text-neutral-700 dark:text-white">{window.title}</h3>
            <p className="text-xl md:text-2xl text-neutral-500 dark:text-neutral-400">
              Status: {window.isMinimized ? "Minimized" : window.isMaximized ? "Maximized" : "Windowed"}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Button
              size="lg"
              variant="ghost"
              className="text-neutral-500 dark:text-neutral-400 hover:bg-gray-200 dark:hover:bg-neutral-700 h-12 w-12"
              onClick={() => onWindowAction(window.id, "minimize")}
            >
              <Minimize2 className="h-6 w-6" />
            </Button>
            <Button
              size="lg"
              variant="ghost"
              className="text-neutral-500 dark:text-neutral-400 hover:bg-gray-200 dark:hover:bg-neutral-700 h-12 w-12"
              onClick={() => onWindowAction(window.id, "maximize")}
            >
              <Maximize2 className="h-6 w-6" />
            </Button>
            <Button
              size="lg"
              variant="ghost"
              className="text-neutral-500 dark:text-neutral-400 hover:bg-gray-200 dark:hover:bg-neutral-700 h-12 w-12"
              onClick={() => onWindowAction(window.id, "close")}
            >
              <X className="h-6 w-6" />
            </Button>
          </div>
        </div>
        
        <div className="bg-gray-50 dark:bg-neutral-900 rounded-2xl p-4 h-[calc(100%-200px)] overflow-hidden border border-gray-200 dark:border-neutral-700">
          <div className="w-full h-full bg-white dark:bg-neutral-800 rounded-xl overflow-hidden">
            {window.component}
          </div>
        </div>
        
        <div className="mt-8 flex justify-center">
          <Button
            size="lg"
            className="bg-gray-200 dark:bg-neutral-800 hover:bg-gray-300 dark:hover:bg-neutral-700 text-neutral-700 dark:text-white border-gray-300 dark:border-neutral-600 px-8 py-4 text-lg"
            onClick={() => {
              onWindowAction(window.id, "activate")
              setShowTaskbar(false)
            }}
          >
            Switch to Window
          </Button>
        </div>
      </div>
    ),
  }))

  if (openWindows.length === 0) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          variant="outline"
          size="sm"
          className="bg-gray-50 dark:bg-neutral-900 border-gray-200 dark:border-neutral-800"
          disabled
        >
          <Grid3X3 className="h-4 w-4 mr-2" />
          No Open Windows
        </Button>
      </div>
    )
  }

  return (
    <>
      {/* Taskbar Toggle Button */}
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          variant="outline"
          size="sm"
          className="bg-gray-50 dark:bg-neutral-900 border-gray-200 dark:border-neutral-800 hover:bg-gray-100 dark:hover:bg-neutral-800"
          onClick={() => setShowTaskbar(!showTaskbar)}
        >
          <Grid3X3 className="h-4 w-4 mr-2" />
          <span className="hidden sm:inline">Apps</span>
          <span className="sm:hidden">{openWindows.length}</span>
          {openWindows.length > 0 && (
            <span className="ml-1 px-1.5 py-0.5 text-xs bg-blue-500 text-white rounded-full">
              {openWindows.length}
            </span>
          )}
          <ChevronUp className={`h-3 w-3 ml-1 transition-transform ${showTaskbar ? 'rotate-180' : ''}`} />
        </Button>
      </div>

      {/* Taskbar Overlay */}
      <AnimatePresence>
        {showTaskbar && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
              onClick={() => setShowTaskbar(false)}
            />
            
            {/* Fullscreen Taskbar Panel */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ type: "spring", damping: 20, stiffness: 300 }}
              className="fixed inset-0 z-50 bg-gray-50/98 dark:bg-neutral-900/98 backdrop-blur-xl"
            >
              <div className="h-full w-full p-8">
                <div className="flex items-center justify-between mb-8">
                  <h1 className="text-3xl font-bold text-neutral-700 dark:text-white">
                    Open Applications
                  </h1>
                  <Button
                    variant="ghost"
                    size="lg"
                    onClick={() => setShowTaskbar(false)}
                    className="hover:bg-gray-100 dark:hover:bg-neutral-800 text-neutral-500 dark:text-neutral-400"
                  >
                    <X className="h-6 w-6" />
                  </Button>
                </div>
                
                <div className="h-[calc(100vh-120px)]">
                  <Tabs 
                    tabs={tabsData}
                    containerClassName="mb-4"
                    activeTabClassName="bg-gray-50 dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800"
                    tabClassName="text-base font-medium transition-all duration-200 hover:bg-gray-100 dark:hover:bg-neutral-700 px-6 py-3 text-neutral-700 dark:text-neutral-300"
                    contentClassName="mt-4 h-[calc(100%-80px)]"
                  />
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}