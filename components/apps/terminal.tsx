"use client"

import { useEffect, useRef, useState } from "react"
import { Terminal as XTerm } from "@xterm/xterm"
import { FitAddon } from "@xterm/addon-fit"
import { WebLinksAddon } from "@xterm/addon-web-links"
import "@xterm/xterm/css/xterm.css"

export function Terminal() {
  const terminalRef = useRef<HTMLDivElement>(null)
  const xtermRef = useRef<XTerm | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const fitAddonRef = useRef<FitAddon | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!terminalRef.current) return

    // Create terminal instance
    const term = new XTerm({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      theme: {
        background: '#1a1a1a',
        foreground: '#ffffff',
        cursor: '#ffffff',
        black: '#000000',
        red: '#ff5555',
        green: '#50fa7b',
        yellow: '#f1fa8c',
        blue: '#bd93f9',
        magenta: '#ff79c6',
        cyan: '#8be9fd',
        white: '#bfbfbf',
        brightBlack: '#4d4d4d',
        brightRed: '#ff6e67',
        brightGreen: '#5af78e',
        brightYellow: '#f4f99d',
        brightBlue: '#caa9fa',
        brightMagenta: '#ff92d0',
        brightCyan: '#9aedfe',
        brightWhite: '#e6e6e6',
      },
      rows: 24,
      cols: 80,
    })

    // Add addons
    const fitAddon = new FitAddon()
    const webLinksAddon = new WebLinksAddon()

    term.loadAddon(fitAddon)
    term.loadAddon(webLinksAddon)

    // Open terminal
    term.open(terminalRef.current)
    fitAddon.fit()

    xtermRef.current = term
    fitAddonRef.current = fitAddon

    // Connect to WebSocket
    connectWebSocket(term)

    // Handle resize
    const handleResize = () => {
      fitAddon.fit()
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'resize',
            cols: term.cols,
            rows: term.rows,
          })
        )
      }
    }

    window.addEventListener('resize', handleResize)

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize)
      if (wsRef.current) {
        wsRef.current.close()
      }
      term.dispose()
    }
  }, [])

  const connectWebSocket = (term: XTerm) => {
    try {
      // Determine WebSocket URL based on environment
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/api/terminal/ws`

      term.writeln('\x1b[1;32mConnecting to terminal...\x1b[0m')

      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('[Terminal] WebSocket connected')
        setIsConnected(true)
        setError(null)
        term.writeln('\x1b[1;32mConnected!\x1b[0m')
        term.writeln('')

        // Send input to WebSocket
        term.onData((data) => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'input', data }))
          }
        })
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)

          if (message.type === 'output') {
            term.write(message.data)
          } else if (message.type === 'connected') {
            console.log('[Terminal] Session established:', message.sessionId)
          } else if (message.type === 'exit') {
            term.writeln(`\n\n\x1b[1;31mTerminal session ended (exit code: ${message.exitCode})\x1b[0m`)
            setIsConnected(false)
          }
        } catch (error) {
          console.error('[Terminal] Error parsing message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('[Terminal] WebSocket error:', error)
        setError('Connection error')
        term.writeln('\n\x1b[1;31mConnection error!\x1b[0m')
      }

      ws.onclose = () => {
        console.log('[Terminal] WebSocket closed')
        setIsConnected(false)
        term.writeln('\n\x1b[1;33mConnection closed. Refresh to reconnect.\x1b[0m')
      }
    } catch (error) {
      console.error('[Terminal] Error connecting:', error)
      setError('Failed to connect')
      term.writeln('\n\x1b[1;31mFailed to connect to terminal!\x1b[0m')
    }
  }

  return (
    <div className="h-full w-full bg-[#1a1a1a] p-4">
      {error && (
        <div className="mb-2 text-sm text-red-500">
          {error}
        </div>
      )}
      {!isConnected && (
        <div className="mb-2 text-sm text-yellow-500">
          Connecting to terminal...
        </div>
      )}
      <div ref={terminalRef} className="h-full w-full" />
    </div>
  )
}
