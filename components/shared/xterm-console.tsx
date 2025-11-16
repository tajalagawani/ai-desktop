"use client"

import { useEffect, useRef, useState, useImperativeHandle, forwardRef } from "react"

export interface XTermConsoleHandle {
  write: (data: string) => void
  clear: () => void
  focus: () => void
}

interface XTermConsoleProps {
  onData?: (data: string) => void
  onResize?: (cols: number, rows: number) => void
  backgroundColor?: string
  foregroundColor?: string
  cursorColor?: string
  fontFamily?: string
  fontSize?: number
  padding?: string
  theme?: {
    background?: string
    foreground?: string
    cursor?: string
    cursorAccent?: string
    selectionBackground?: string
    black?: string
    red?: string
    green?: string
    yellow?: string
    blue?: string
    magenta?: string
    cyan?: string
    white?: string
    brightBlack?: string
    brightRed?: string
    brightGreen?: string
    brightYellow?: string
    brightBlue?: string
    brightMagenta?: string
    brightCyan?: string
    brightWhite?: string
  }
}

export const XTermConsole = forwardRef<XTermConsoleHandle, XTermConsoleProps>(
  (
    {
      onData,
      onResize,
      backgroundColor = '#000000',
      foregroundColor = '#ffffff',
      cursorColor = '#ffffff',
      fontFamily = 'Menlo, Monaco, "Courier New", monospace',
      fontSize = 13,
      padding = '0',
      theme
    },
    ref
  ) => {
    const terminalRef = useRef<HTMLDivElement>(null)
    const xtermRef = useRef<any>(null)
    const fitAddonRef = useRef<any>(null)
    const [isLoading, setIsLoading] = useState(true)

    // Expose methods to parent
    useImperativeHandle(ref, () => ({
      write: (data: string) => {
        if (xtermRef.current) {
          xtermRef.current.write(data)
        }
      },
      clear: () => {
        if (xtermRef.current) {
          xtermRef.current.clear()
        }
      },
      focus: () => {
        if (xtermRef.current) {
          xtermRef.current.focus()
        }
      }
    }))

    useEffect(() => {
      if (!terminalRef.current) return

      let term: any = null
      let fitAddon: any = null

      const loadTerminal = async () => {
        try {
          const { Terminal: XTerm } = await import('@xterm/xterm')
          const { FitAddon } = await import('@xterm/addon-fit')
          const { WebLinksAddon } = await import('@xterm/addon-web-links')

          await import('@xterm/xterm/css/xterm.css')

          if (!terminalRef.current) return

          // Create terminal with custom theme
          term = new XTerm({
            cursorBlink: true,
            cursorStyle: 'block',
            fontSize,
            fontFamily,
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
            theme: theme || {
              background: backgroundColor,
              foreground: foregroundColor,
              cursor: cursorColor,
              cursorAccent: backgroundColor,
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
            },
          })

          fitAddon = new FitAddon()
          const webLinksAddon = new WebLinksAddon()

          term.loadAddon(fitAddon)
          term.loadAddon(webLinksAddon)

          term.open(terminalRef.current)

          await new Promise(resolve => setTimeout(resolve, 10))

          // Remove xterm default padding
          const xtermElement = terminalRef.current.querySelector('.xterm')
          if (xtermElement) {
            ;(xtermElement as HTMLElement).style.padding = '0'
          }
          const xtermScreen = terminalRef.current.querySelector('.xterm-screen')
          if (xtermScreen) {
            ;(xtermScreen as HTMLElement).style.padding = '0'
          }

          fitAddon.fit()

          xtermRef.current = term
          fitAddonRef.current = fitAddon

          // Handle user input
          if (onData) {
            term.onData((data: string) => {
              onData(data)
            })
          }

          // Handle resize
          if (onResize) {
            term.onResize(({ cols, rows }: { cols: number; rows: number }) => {
              onResize(cols, rows)
            })
          }

          setIsLoading(false)

          // Handle window resize
          const handleResize = () => {
            if (fitAddon) {
              try {
                fitAddon.fit()
              } catch (err) {
                console.error('[XTermConsole] Error fitting terminal:', err)
              }
            }
          }

          window.addEventListener('resize', handleResize)

          return () => {
            window.removeEventListener('resize', handleResize)
            if (term) {
              term.dispose()
            }
          }
        } catch (error) {
          console.error('[XTermConsole] Error loading terminal:', error)
          setIsLoading(false)
        }
      }

      loadTerminal()

      return () => {
        if (term) {
          term.dispose()
        }
      }
    }, [onData, onResize, backgroundColor, foregroundColor, cursorColor, fontFamily, fontSize, theme])

    return (
      <div
        ref={terminalRef}
        className="h-full w-full xterm-container"
        style={{
          display: isLoading ? 'none' : 'block',
          backgroundColor,
          padding: 0,
          margin: 0,
        }}
      />
    )
  }
)

XTermConsole.displayName = 'XTermConsole'
