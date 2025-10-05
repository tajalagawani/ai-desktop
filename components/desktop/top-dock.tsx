"use client"

import { useEffect, useState } from "react"
import { Moon, Sun, Wifi, Battery, Bell } from "lucide-react"
import { cn } from "@/lib/utils"

interface TopDockProps {
  className?: string
}

export function TopDock({ className }: TopDockProps) {
  const [currentTime, setCurrentTime] = useState("")
  const [isDark, setIsDark] = useState(true)

  useEffect(() => {
    // Update time every second
    const updateTime = () => {
      const now = new Date()
      const hours = now.getHours().toString().padStart(2, "0")
      const minutes = now.getMinutes().toString().padStart(2, "0")
      setCurrentTime(`${hours}:${minutes}`)
    }

    updateTime()
    const interval = setInterval(updateTime, 1000)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    // Check initial theme
    const isDarkMode = document.documentElement.classList.contains("dark")
    setIsDark(isDarkMode)
  }, [])

  const toggleTheme = () => {
    const html = document.documentElement
    if (html.classList.contains("dark")) {
      html.classList.remove("dark")
      setIsDark(false)
    } else {
      html.classList.add("dark")
      setIsDark(true)
    }
  }

  return (
    <div
      className={cn(
        "fixed top-4 left-1/2 -translate-x-1/2 z-50",
        "flex items-center gap-3 h-10 px-4 rounded-2xl",
        "bg-muted",
        className
      )}
    >
      {/* Clock */}
      <div className="text-sm font-normal text-foreground tabular-nums">
        {currentTime || "00:00"}
      </div>

      <div className="w-px h-5 bg-border" />

      {/* Theme Toggle */}
      <button
        onClick={toggleTheme}
        className="p-1.5 rounded-lg hover:bg-dock-hover transition-colors"
        title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      >
        {isDark ? (
          <Sun className="h-4 w-4 text-foreground" />
        ) : (
          <Moon className="h-4 w-4 text-foreground" />
        )}
      </button>

      <div className="w-px h-5 bg-border" />

      {/* WiFi Status */}
      <button
        className="p-1.5 rounded-lg hover:bg-dock-hover transition-colors"
        title="WiFi connected"
      >
        <Wifi className="h-4 w-4 text-foreground" />
      </button>

      {/* Battery Status */}
      <button
        className="p-1.5 rounded-lg hover:bg-dock-hover transition-colors"
        title="Battery status"
      >
        <Battery className="h-4 w-4 text-foreground" />
      </button>

      {/* Notifications */}
      <button
        className="p-1.5 rounded-lg hover:bg-dock-hover transition-colors"
        title="Notifications"
      >
        <Bell className="h-4 w-4 text-foreground" />
      </button>
    </div>
  )
}
