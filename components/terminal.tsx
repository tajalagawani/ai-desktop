"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Input } from "@/components/ui/input"

interface TerminalLine {
  id: string
  content: string
  type: "command" | "output" | "error"
}

export function Terminal() {
  const [lines, setLines] = useState<TerminalLine[]>([
    {
      id: "1",
      content: "Welcome to AI Desktop Terminal",
      type: "output",
    },
    {
      id: "2",
      content: "Type 'help' for available commands",
      type: "output",
    },
  ])
  const [currentCommand, setCurrentCommand] = useState("")
  const [commandHistory, setCommandHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const terminalRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [lines])

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  const executeCommand = (command: string) => {
    const cmd = command.trim().toLowerCase()

    // Add command to history
    setCommandHistory((prev) => [...prev, command])
    setHistoryIndex(-1)

    // Add command line
    setLines((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        content: `$ ${command}`,
        type: "command",
      },
    ])

    // Process command
    let output = ""
    let type: "output" | "error" = "output"

    switch (cmd) {
      case "help":
        output = `Available commands:
  help        - Show this help message
  clear       - Clear terminal
  ls          - List files and directories
  pwd         - Show current directory
  whoami      - Show current user
  date        - Show current date and time
  echo <text> - Echo text
  node --version - Show Node.js version
  npm --version  - Show npm version`
        break
      case "clear":
        setLines([])
        return
      case "ls":
        output = "workflows/  nodes/  config/  logs/  README.md"
        break
      case "pwd":
        output = "/Users/ai-desktop"
        break
      case "whoami":
        output = "ai-desktop-user"
        break
      case "date":
        output = new Date().toString()
        break
      case "node --version":
        output = "v20.10.0"
        break
      case "npm --version":
        output = "10.2.3"
        break
      default:
        if (cmd.startsWith("echo ")) {
          output = command.substring(5)
        } else {
          output = `Command not found: ${command}. Type 'help' for available commands.`
          type = "error"
        }
    }

    // Add output
    setTimeout(() => {
      setLines((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          content: output,
          type,
        },
      ])
    }, 100)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      if (currentCommand.trim()) {
        executeCommand(currentCommand)
      }
      setCurrentCommand("")
    } else if (e.key === "ArrowUp") {
      e.preventDefault()
      if (commandHistory.length > 0) {
        const newIndex = historyIndex === -1 ? commandHistory.length - 1 : Math.max(0, historyIndex - 1)
        setHistoryIndex(newIndex)
        setCurrentCommand(commandHistory[newIndex])
      }
    } else if (e.key === "ArrowDown") {
      e.preventDefault()
      if (historyIndex !== -1) {
        const newIndex = historyIndex + 1
        if (newIndex >= commandHistory.length) {
          setHistoryIndex(-1)
          setCurrentCommand("")
        } else {
          setHistoryIndex(newIndex)
          setCurrentCommand(commandHistory[newIndex])
        }
      }
    }
  }

  return (
    <div className="h-full flex flex-col bg-card terminal-bg">
      {/* Terminal Content */}
      <div ref={terminalRef} className="flex-1 p-4 overflow-y-auto font-mono text-sm space-y-1">
        {lines.map((line) => (
          <div
            key={line.id}
            className={`${
              line.type === "command"
                ? "text-primary font-semibold"
                : line.type === "error"
                  ? "text-destructive"
                  : "text-foreground"
            }`}
          >
            {line.content.split("\n").map((text, index) => (
              <div key={index}>{text}</div>
            ))}
          </div>
        ))}

        {/* Current input line */}
        <div className="flex items-center gap-2">
          <span className="text-primary font-semibold">$</span>
          <Input
            ref={inputRef}
            value={currentCommand}
            onChange={(e) => setCurrentCommand(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 border-none bg-transparent p-0 font-mono text-sm focus-visible:ring-0 focus-visible:ring-offset-0"
            placeholder="Enter command..."
          />
        </div>
      </div>
    </div>
  )
}
