"use client"

import { useEffect, useRef, useState } from "react"
import { XTermConsole, type XTermConsoleHandle } from "@/components/shared/xterm-console"

export function ClaudeCLI() {
  const consoleRef = useRef<XTermConsoleHandle>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  const handleData = (data: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'input',
          data,
        })
      )
    }
  }

  const handleResize = (cols: number, rows: number) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'resize',
          cols,
          rows,
        })
      )
    }
  }

  const connectWebSocket = () => {
    try {
      console.log('[Claude CLI] Connecting to WebSocket...')
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/api/terminal/ws`

      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('[Claude CLI] WebSocket connected')
        setIsConnected(true)

        // Auto-run claude command when connected
        setTimeout(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
              type: 'input',
              data: 'claude\n'
            }))
          }
        }, 500)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)

          if (message.type === 'output' && consoleRef.current) {
            consoleRef.current.write(message.data)
          } else if (message.type === 'connected') {
            console.log('[Claude CLI] Session established:', message.sessionId)
          } else if (message.type === 'exit') {
            console.log('[Claude CLI] Process exited')
            setIsConnected(false)
            if (consoleRef.current) {
              consoleRef.current.write('\r\n\x1b[1;33mProcess exited. Refresh to reconnect.\x1b[0m\r\n')
            }
          }
        } catch (error) {
          console.error('[Claude CLI] Error parsing message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('[Claude CLI] WebSocket error:', error)
        setIsConnected(false)
      }

      ws.onclose = () => {
        console.log('[Claude CLI] WebSocket closed')
        setIsConnected(false)
        if (consoleRef.current) {
          consoleRef.current.write('\r\n\x1b[1;33mConnection closed. Refresh to reconnect.\x1b[0m\r\n')
        }
      }
    } catch (error) {
      console.error('[Claude CLI] Error connecting:', error)
      if (consoleRef.current) {
        consoleRef.current.write('\r\n\x1b[1;31mFailed to connect to terminal!\x1b[0m\r\n')
      }
    }
  }

  useEffect(() => {
    // Small delay to ensure console is mounted
    const timer = setTimeout(() => {
      connectWebSocket()
    }, 100)

    return () => {
      clearTimeout(timer)
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  return (
    <div className="h-full w-full bg-[#1a1625] flex flex-col">
      {!isConnected && (
        <div className="px-4 py-2 text-sm text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-b border-yellow-200 dark:border-yellow-900/30">
          Connecting to Claude CLI...
        </div>
      )}
      <div className="flex-1 w-full overflow-hidden">
        <XTermConsole
          ref={consoleRef}
          onData={handleData}
          onResize={handleResize}
          backgroundColor="#1a1625"
          foregroundColor="#e0def4"
          cursorColor="#f6c177"
          fontFamily='Menlo, Monaco, "Courier New", monospace'
          fontSize={13}
          theme={{
            background: '#1a1625',
            foreground: '#e0def4',
            cursor: '#f6c177',
            cursorAccent: '#1a1625',
            selectionBackground: 'rgba(246, 193, 119, 0.3)',
            black: '#26233a',
            red: '#eb6f92',
            green: '#31748f',
            yellow: '#f6c177',
            blue: '#9ccfd8',
            magenta: '#c4a7e7',
            cyan: '#ebbcba',
            white: '#e0def4',
            brightBlack: '#6e6a86',
            brightRed: '#eb6f92',
            brightGreen: '#31748f',
            brightYellow: '#f6c177',
            brightBlue: '#9ccfd8',
            brightMagenta: '#c4a7e7',
            brightCyan: '#ebbcba',
            brightWhite: '#e0def4',
          }}
        />
      </div>
    </div>
  )
}
