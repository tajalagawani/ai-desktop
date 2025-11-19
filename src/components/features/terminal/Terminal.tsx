"use client"

import { useEffect, useRef, useState } from "react"
import { XTermConsole, type XTermConsoleHandle } from "@/components/shared/xterm-console"

export function Terminal() {
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
      console.log('[Terminal] Connecting to WebSocket...')
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/api/terminal/ws`

      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('[Terminal] WebSocket connected')
        setIsConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)

          if (message.type === 'output' && consoleRef.current) {
            consoleRef.current.write(message.data)
          } else if (message.type === 'connected') {
            console.log('[Terminal] Session established:', message.sessionId)
          } else if (message.type === 'exit') {
            console.log('[Terminal] Process exited')
            setIsConnected(false)
            if (consoleRef.current) {
              consoleRef.current.write('\r\n\x1b[1;33mProcess exited. Refresh to reconnect.\x1b[0m\r\n')
            }
          }
        } catch (error) {
          console.error('[Terminal] Error parsing message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('[Terminal] WebSocket error:', error)
        setIsConnected(false)
      }

      ws.onclose = () => {
        console.log('[Terminal] WebSocket closed')
        setIsConnected(false)
        if (consoleRef.current) {
          consoleRef.current.write('\r\n\x1b[1;33mConnection closed. Refresh to reconnect.\x1b[0m\r\n')
        }
      }
    } catch (error) {
      console.error('[Terminal] Error connecting:', error)
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
    <div className="h-full w-full bg-black flex flex-col">
      {!isConnected && (
        <div className="px-4 py-2 text-sm text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-b border-yellow-200 dark:border-yellow-900/30">
          Connecting to terminal...
        </div>
      )}
      <div className="flex-1 w-full overflow-hidden">
        <XTermConsole
          ref={consoleRef}
          onData={handleData}
          onResize={handleResize}
          backgroundColor="#000000"
          foregroundColor="#ffffff"
          cursorColor="#ffffff"
          fontFamily='Menlo, Monaco, "Courier New", monospace'
          fontSize={13}
          theme={{
            background: '#000000',
            foreground: '#ffffff',
            cursor: '#ffffff',
            cursorAccent: '#000000',
            selectionBackground: 'rgba(255, 255, 255, 0.3)',
            black: '#000000',
            red: '#c23621',
            green: '#25bc24',
            yellow: '#adad27',
            blue: '#492ee1',
            magenta: '#d338d3',
            cyan: '#33bbc8',
            white: '#cbcccd',
            brightBlack: '#818383',
            brightRed: '#fc391f',
            brightGreen: '#31e722',
            brightYellow: '#eaec23',
            brightBlue: '#5833ff',
            brightMagenta: '#f935f8',
            brightCyan: '#14f0f0',
            brightWhite: '#e9ebeb',
          }}
        />
      </div>
    </div>
  )
}
