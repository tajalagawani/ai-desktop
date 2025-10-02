"use client"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Power, RotateCcw, Moon, LogOut } from "lucide-react"

interface SystemControlMenuProps {
  onLogout: () => void
}

export function SystemControlMenu({ onLogout }: SystemControlMenuProps) {
  const handleSleep = () => {
    // Simulate sleep mode
    document.body.style.filter = "brightness(0.1)"
    setTimeout(() => {
      document.body.style.filter = "brightness(1)"
    }, 2000)
  }

  const handleRestart = () => {
    // Simulate restart
    window.location.reload()
  }

  const handleShutdown = () => {
    // Simulate shutdown
    document.body.style.transition = "opacity 1s"
    document.body.style.opacity = "0"
    setTimeout(() => {
      document.body.innerHTML =
        '<div style="background: black; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; font-family: monospace;">System Shutdown</div>'
    }, 1000)
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button 
          className="h-full px-2 hover:bg-white/10 flex items-center justify-center cursor-pointer"
        >
          <Power className="h-3 w-3" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48 mb-1">
        <DropdownMenuItem onClick={handleSleep} className="cursor-pointer">
          <Moon className="mr-2 h-4 w-4" />
          Sleep
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleRestart} className="cursor-pointer">
          <RotateCcw className="mr-2 h-4 w-4" />
          Restart
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleShutdown} className="cursor-pointer text-red-600">
          <Power className="mr-2 h-4 w-4" />
          Shut Down
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onLogout} className="cursor-pointer">
          <LogOut className="mr-2 h-4 w-4" />
          Log Out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
