"use client"

import { useEffect, useRef, useState } from "react"

export function Terminal() {
  const terminalRef = useRef<HTMLDivElement>(null)
  const xtermRef = useRef<any>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const fitAddonRef = useRef<any>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!terminalRef.current) return

    let cleanup: (() => void) | null = null
    let term: any = null
    let fitAddon: any = null

    // Dynamically import xterm to avoid SSR issues
    const loadTerminal = async () => {
      try {
        // Import xterm and addons dynamically (browser-only)
        const { Terminal: XTerm } = await import('@xterm/xterm')
        const { FitAddon } = await import('@xterm/addon-fit')
        const { WebLinksAddon } = await import('@xterm/addon-web-links')

        // Import CSS
        await import('@xterm/xterm/css/xterm.css')

        if (!terminalRef.current) return

        // Create terminal instance with optimal settings (macOS Terminal colors)
        term = new XTerm({
          cursorBlink: true,
          cursorStyle: 'block',
          fontSize: 13,
          fontFamily: 'Menlo, Monaco, "Courier New", monospace',
          fontWeight: 'normal',
          fontWeightBold: 'bold',
          letterSpacing: 0,
          lineHeight: 1.0,
          allowProposedApi: true,
          allowTransparency: false,
          convertEol: false,
          disableStdin: false,
          scrollback: 1000,
          tabStopWidth: 8,
          theme: {
            // macOS Terminal (Basic profile) exact colors
            background: '#000000',
            foreground: '#ffffff',
            cursor: '#ffffff',
            cursorAccent: '#000000',
            selectionBackground: 'rgba(255, 255, 255, 0.3)',
            // ANSI Colors - macOS Terminal Basic
            black: '#000000',
            red: '#c23621',
            green: '#25bc24',
            yellow: '#adad27',
            blue: '#492ee1',
            magenta: '#d338d3',
            cyan: '#33bbc8',
            white: '#cbcccd',
            // Bright ANSI Colors - macOS Terminal Basic
            brightBlack: '#818383',
            brightRed: '#fc391f',
            brightGreen: '#31e722',
            brightYellow: '#eaec23',
            brightBlue: '#5833ff',
            brightMagenta: '#f935f8',
            brightCyan: '#14f0f0',
            brightWhite: '#e9ebeb',
          },
        })

        // Create and load addons
        fitAddon = new FitAddon()
        const webLinksAddon = new WebLinksAddon()

        term.loadAddon(fitAddon)
        term.loadAddon(webLinksAddon)

        // Open terminal in the container
        term.open(terminalRef.current)

        // Wait for terminal to be fully mounted
        await new Promise(resolve => setTimeout(resolve, 10))

        // Fit terminal to container
        fitAddon.fit()

        xtermRef.current = term
        fitAddonRef.current = fitAddon

        setIsLoading(false)

        // Connect to WebSocket
        connectWebSocket(term)

        // Handle window resize with debouncing
        let resizeTimeout: NodeJS.Timeout
        const handleResize = () => {
          clearTimeout(resizeTimeout)
          resizeTimeout = setTimeout(() => {
            try {
              fitAddon.fit()
              if (wsRef.current?.readyState === WebSocket.OPEN && term) {
                wsRef.current.send(
                  JSON.stringify({
                    type: 'resize',
                    cols: term.cols,
                    rows: term.rows,
                  })
                )
              }
            } catch (error) {
              console.error('[Terminal] Resize error:', error)
            }
          }, 100)
        }

        window.addEventListener('resize', handleResize)

        // Initial resize after a short delay
        setTimeout(() => {
          fitAddon.fit()
          if (wsRef.current?.readyState === WebSocket.OPEN && term) {
            wsRef.current.send(
              JSON.stringify({
                type: 'resize',
                cols: term.cols,
                rows: term.rows,
              })
            )
          }
        }, 200)

        // Set cleanup function
        cleanup = () => {
          clearTimeout(resizeTimeout)
          window.removeEventListener('resize', handleResize)
          if (wsRef.current) {
            wsRef.current.close()
          }
          if (term) {
            term.dispose()
          }
        }
      } catch (error) {
        console.error('[Terminal] Error loading terminal:', error)
        setIsLoading(false)
      }
    }

    loadTerminal()

    // Cleanup
    return () => {
      if (cleanup) cleanup()
    }
  }, [])

  const connectWebSocket = (term: any) => {
    try {
      // Determine WebSocket URL based on environment
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/api/terminal/ws`

      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('[Terminal] WebSocket connected')
        setIsConnected(true)

        // Send initial terminal size
        if (term) {
          ws.send(
            JSON.stringify({
              type: 'resize',
              cols: term.cols,
              rows: term.rows,
            })
          )
        }

        // Handle data from terminal (user input)
        term.onData((data: string) => {
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
            term.write(`\r\n\x1b[1;31mTerminal session ended (exit code: ${message.exitCode})\x1b[0m\r\n`)
            setIsConnected(false)
          }
        } catch (error) {
          console.error('[Terminal] Error parsing message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('[Terminal] WebSocket error:', error)
        term.write('\r\n\x1b[1;31mConnection error!\x1b[0m\r\n')
        setIsConnected(false)
      }

      ws.onclose = () => {
        console.log('[Terminal] WebSocket closed')
        setIsConnected(false)
        term.write('\r\n\x1b[1;33mConnection closed. Refresh to reconnect.\x1b[0m\r\n')
      }
    } catch (error) {
      console.error('[Terminal] Error connecting:', error)
      term.write('\r\n\x1b[1;31mFailed to connect to terminal!\x1b[0m\r\n')
    }
  }

  return (
    <div className="h-full w-full bg-black flex flex-col">
      {isLoading && (
        <div className="flex items-center justify-center h-full text-white">
          <div className="text-sm">Initializing terminal...</div>
        </div>
      )}
      {!isLoading && !isConnected && (
        <div className="px-4 py-2 text-sm text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-b border-yellow-200 dark:border-yellow-900/30">
          Connecting to terminal...
        </div>
      )}
      <div
        ref={terminalRef}
        className="flex-1 w-full"
        style={{
          display: isLoading ? 'none' : 'block',
          height: '100%',
          width: '100%',
          overflow: 'hidden'
        }}
      />
    </div>
  )
}
