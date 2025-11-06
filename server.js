const { createServer } = require('http')
const { parse } = require('url')
const next = require('next')
const { WebSocketServer } = require('ws')
const { spawn } = require('node-pty')
const path = require('path')
const { spawnSync } = require('child_process')
const { ensureAgentFile } = require('./lib/utils/claude/setup-agent')
const { ensureFlowArchitectProject } = require('./lib/utils/claude/setup-flow-architect')

const dev = process.env.NODE_ENV !== 'production'
const hostname = 'localhost'
const port = parseInt(process.env.PORT || '3000', 10)

const app = next({ dev, hostname, port })
const handle = app.getRequestHandler()

// Store active terminal sessions
const terminals = new Map()

app.prepare().then(() => {
  const server = createServer(async (req, res) => {
    try {
      const parsedUrl = parse(req.url, true)
      await handle(req, res, parsedUrl)
    } catch (err) {
      console.error('Error occurred handling', req.url, err)
      res.statusCode = 500
      res.end('internal server error')
    }
  })

  // Create WebSocket server
  const wss = new WebSocketServer({ noServer: true })

  // Handle WebSocket upgrade
  server.on('upgrade', (request, socket, head) => {
    const { pathname } = parse(request.url, true)
    console.log('[WebSocket] Upgrade request received for:', pathname)
    console.log('[WebSocket] Request URL:', request.url)
    console.log('[WebSocket] Request headers:', JSON.stringify(request.headers, null, 2))

    if (pathname === '/api/terminal/ws' || pathname === '/api/services/logs/ws' || pathname === '/api/action-builder/ws') {
      console.log('[WebSocket] ✅ Valid WebSocket path, handling upgrade...')
      wss.handleUpgrade(request, socket, head, (ws) => {
        console.log('[WebSocket] Upgrade successful, emitting connection event')
        wss.emit('connection', ws, request, pathname)
      })
    } else {
      console.log('[WebSocket] ❌ Invalid WebSocket path, destroying socket:', pathname)
      socket.destroy()
    }
  })

  // Handle WebSocket connections
  wss.on('connection', (ws, request, pathname) => {
    console.log('[WebSocket] Connection established for:', pathname)
    console.log('[WebSocket] Client address:', request.socket.remoteAddress)

    if (pathname === '/api/services/logs/ws') {
      console.log('[WebSocket] Routing to logs handler')
      handleLogsConnection(ws, request)
    } else if (pathname === '/api/action-builder/ws') {
      console.log('[WebSocket] Routing to Action Builder handler')
      handleActionBuilderConnection(ws, request)
    } else {
      console.log('[WebSocket] Routing to terminal handler')
      handleTerminalConnection(ws)
    }
  })

  // Handle Action Builder WebSocket connections
  function handleActionBuilderConnection(ws, request) {
    console.log('[Action Builder] ========================================')
    console.log('[Action Builder] New WebSocket connection established')
    console.log('[Action Builder] ========================================')

    let claudeProcess = null
    let claudeSessionId = null

    // Handle messages from client
    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message.toString())
        console.log('[Action Builder] ----------------------------------------')
        console.log('[Action Builder] Message received:', data.type)
        console.log('[Action Builder] Full message:', JSON.stringify(data, null, 2))
        console.log('[Action Builder] ----------------------------------------')

        if (data.type === 'start_chat') {
          const { prompt, sessionId, resume } = data

          console.log('[Action Builder] Start chat request...')
          console.log('[Action Builder]   - Prompt:', prompt)
          console.log('[Action Builder]   - Session ID:', sessionId || 'NEW')
          console.log('[Action Builder]   - Resume:', resume || false)

          // If client provides sessionId (from previous session), use it
          if (sessionId && !claudeSessionId) {
            claudeSessionId = sessionId
            console.log('[Action Builder] ✅ Using client-provided session ID:', claudeSessionId)
          }

          // If Claude process already exists, send message to its stdin
          if (claudeProcess && claudeProcess.stdin && !claudeProcess.stdin.destroyed) {
            console.log('[Action Builder] ✅ Using existing Claude process, sending message to stdin')
            const stdinMessage = JSON.stringify({
              type: 'user',
              message: {
                role: 'user',
                content: prompt
              }
            }) + '\n'
            claudeProcess.stdin.write(stdinMessage)
            console.log('[Action Builder] Message sent to Claude stdin')
            return
          }

          // Otherwise, spawn new Claude process with streaming I/O
          console.log('[Action Builder] Spawning new Claude process with streaming I/O...')

          // Get working directory - use process.cwd() for Next.js compatibility
          const workingDir = path.join(process.cwd(), 'flow-architect')

          // Build Claude CLI command
          const args = []

          // Add resume flag if we have a session ID
          if (claudeSessionId) {
            args.push('--resume', claudeSessionId)
            console.log('[Action Builder] Resuming session:', claudeSessionId)
          }

          // Add streaming I/O format (enables interactive communication)
          args.push('--input-format', 'stream-json')
          args.push('--output-format', 'stream-json')
          args.push('--verbose')

          // Add MCP config if available
          try {
            const fs = require('fs')
            const os = require('os')

            // Priority 1: Check for project-local .mcp.json
            const projectMcpConfigPath = path.join(process.cwd(), '.mcp.json')
            console.log('[Action Builder] Checking for MCP config:', projectMcpConfigPath)

            let mcpConfigPath = null

            if (fs.existsSync(projectMcpConfigPath)) {
              try {
                const projectMcpConfig = JSON.parse(fs.readFileSync(projectMcpConfigPath, 'utf8'))
                if (projectMcpConfig.mcpServers && Object.keys(projectMcpConfig.mcpServers).length > 0) {
                  console.log(`[Action Builder] ✅ Found ${Object.keys(projectMcpConfig.mcpServers).length} MCP servers in .mcp.json`)
                  mcpConfigPath = projectMcpConfigPath
                }
              } catch (e) {
                console.log('[Action Builder] Failed to parse .mcp.json:', e.message)
              }
            }

            // Priority 2: Check ~/.claude.json
            if (!mcpConfigPath) {
              const claudeConfigPath = path.join(os.homedir(), '.claude.json')
              if (fs.existsSync(claudeConfigPath)) {
                try {
                  const claudeConfig = JSON.parse(fs.readFileSync(claudeConfigPath, 'utf8'))
                  if (claudeConfig.mcpServers && Object.keys(claudeConfig.mcpServers).length > 0) {
                    console.log(`[Action Builder] ✅ Found MCP servers in ~/.claude.json`)
                    mcpConfigPath = claudeConfigPath
                  }
                } catch (e) {
                  console.log('[Action Builder] Failed to parse ~/.claude.json:', e.message)
                }
              }
            }

            if (mcpConfigPath) {
              args.push('--mcp-config', mcpConfigPath)
              console.log('[Action Builder] Added MCP config:', mcpConfigPath)
            }
          } catch (error) {
            console.log('[Action Builder] MCP config check failed:', error.message)
          }

          // Add model
          args.push('--model', 'sonnet')

          // IMPORTANT: Bypass permissions so Claude can write actions without approval
          args.push('--permission-mode', 'bypassPermissions')
          console.log('[Action Builder] Permission mode: bypassPermissions')

          // Grant access to flow-architect directory
          args.push('--add-dir', workingDir)
          console.log('[Action Builder] Granted access to directory:', workingDir)

          // Note: No --agents flag needed! Claude reads CLAUDE.md from working directory
          // Note: NO prompt in args! We send it via stdin after spawning

          console.log('[Action Builder] ========================================')
          console.log('[Action Builder] SPAWNING CLAUDE CLI')
          console.log('[Action Builder] ========================================')
          console.log('[Action Builder] Process cwd:', process.cwd())
          console.log('[Action Builder] Working directory:', workingDir)
          console.log('[Action Builder] Working dir exists:', require('fs').existsSync(workingDir))
          console.log('[Action Builder] Flows dir:', path.join(workingDir, 'flows'))
          console.log('[Action Builder] Flows dir exists:', require('fs').existsSync(path.join(workingDir, 'flows')))
          console.log('[Action Builder] CLAUDE.md exists:', require('fs').existsSync(path.join(workingDir, 'CLAUDE.md')))
          console.log('[Action Builder] Claude CLI command:', 'claude', args.join(' '))
          console.log('[Action Builder] API Key present:', !!process.env.ANTHROPIC_API_KEY)
          console.log('[Action Builder] ========================================')

          // Spawn Claude CLI process
          const { spawn: spawnChild } = require('child_process')
          console.log('[Action Builder] Spawning Claude process...')

          // Check if user wants to use Claude CLI auth instead of API key
          const useClaudeAuth = process.env.USE_CLAUDE_CLI_AUTH === 'true'

          // Build clean environment without Node debug flags
          const cleanEnv = { ...process.env }
          delete cleanEnv.NODE_OPTIONS // Remove any Node debugging flags

          if (useClaudeAuth) {
            // Use Claude CLI authentication (from `claude login`)
            console.log('[Action Builder] Using Claude CLI authentication (no API key)')
            // Remove ANTHROPIC_API_KEY to force Claude to use CLI auth
            delete cleanEnv.ANTHROPIC_API_KEY
          } else {
            // Use API key from environment
            console.log('[Action Builder] Using ANTHROPIC_API_KEY from environment')
            cleanEnv.ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY
          }

          claudeProcess = spawnChild('claude', args, {
            cwd: workingDir,
            stdio: ['pipe', 'pipe', 'pipe'],
            env: cleanEnv,
            detached: false,
            shell: false
          })

          console.log('[Action Builder] ✅ Claude process spawned, PID:', claudeProcess.pid)

          // Send initial message to stdin
          console.log('[Action Builder] Sending initial message to Claude stdin...')
          const initialMessage = JSON.stringify({
            type: 'user',
            message: {
              role: 'user',
              content: prompt
            }
          }) + '\n'
          claudeProcess.stdin.write(initialMessage)
          console.log('[Action Builder] ✅ Initial message sent')

          // Keep stdin open for follow-up messages (don't close it!)

          // Stream stdout to WebSocket
          claudeProcess.stdout.on('data', (data) => {
            try {
              const output = data.toString()
              console.log('[Action Builder] Claude stdout (first 200 chars):', output.substring(0, 200))

              if (ws.readyState === 1) {
                console.log('[Action Builder] WebSocket ready, parsing output...')
                // Parse each line as JSON and send
                const lines = output.split('\n').filter(l => l.trim())
                console.log('[Action Builder] Found', lines.length, 'lines to process')
                for (const line of lines) {
                  try {
                    const parsed = JSON.parse(line)
                    console.log('[Action Builder] Parsed JSON, type:', parsed.type)

                    // Capture session ID from system init message
                    if (parsed.type === 'system' && parsed.subtype === 'init' && parsed.session_id) {
                      claudeSessionId = parsed.session_id
                      console.log('[Action Builder] ✅ Captured session ID:', claudeSessionId)

                      // Send session-created message to client for sidebar
                      ws.send(JSON.stringify({
                        type: 'session-created',
                        sessionId: claudeSessionId
                      }))
                      console.log('[Action Builder] ✅ Sent session-created message to client')
                    }

                    ws.send(JSON.stringify({
                      type: 'claude_output',
                      data: parsed,
                      sessionId: claudeSessionId // Include session ID in every message
                    }))
                    console.log('[Action Builder] ✅ Sent to WebSocket')

                    // Kill process when Claude completes (sends result message)
                    if (parsed.type === 'result') {
                      console.log('[Action Builder] Claude completed, killing process for next message')
                      if (claudeProcess) {
                        claudeProcess.kill()
                        claudeProcess = null
                      }
                    }
                  } catch (e) {
                    console.log('[Action Builder] Line is not JSON, skipping:', line.substring(0, 50))
                  }
                }
              } else {
                console.warn('[Action Builder] ⚠️ WebSocket not ready, readyState:', ws.readyState)
              }
            } catch (error) {
              console.error('[Action Builder] ❌ Error sending data:', error)
            }
          })

          // Handle stderr
          claudeProcess.stderr.on('data', (data) => {
            const errorOutput = data.toString()
            console.error('[Action Builder] ❌ Claude stderr:', errorOutput)
            console.error('[Action Builder] stderr length:', errorOutput.length, 'bytes')
          })

          // Handle process exit
          claudeProcess.on('exit', (code) => {
            console.log('[Action Builder] ========================================')
            console.log('[Action Builder] Claude process exited with code:', code)

            // List files in ACT flows directory (where flows are actually saved)
            const actDockerFlowsDir = '/Users/tajnoah/act/flows'
            try {
              const fs = require('fs')
              if (fs.existsSync(actDockerFlowsDir)) {
                const files = fs.readdirSync(actDockerFlowsDir).filter(f => f.endsWith('.flow'))
                console.log('[Action Builder] Deployed flows in ACT:', files.length)
                files.forEach(file => {
                  const filePath = path.join(actDockerFlowsDir, file)
                  const stats = fs.statSync(filePath)
                  console.log('[Action Builder]   -', file, `(${(stats.size / 1024).toFixed(1)} KB)`)
                })
              } else {
                console.log('[Action Builder] ACT Docker flows directory does not exist!')
              }
            } catch (err) {
              console.error('[Action Builder] Error listing flows:', err.message)
            }

            console.log('[Action Builder] ========================================')
            if (ws.readyState === 1) {
              ws.send(JSON.stringify({
                type: 'complete',
                data: { exitCode: code }
              }))
            }
            claudeProcess = null
          })

          // Handle process error
          claudeProcess.on('error', (error) => {
            console.error('[Action Builder] ========================================')
            console.error('[Action Builder] ❌ Claude process error:', error.message)
            console.error('[Action Builder] Error code:', error.code)
            console.error('[Action Builder] Error stack:', error.stack)
            console.error('[Action Builder] ========================================')
            if (ws.readyState === 1) {
              ws.send(JSON.stringify({
                type: 'error',
                data: error.message
              }))
            }
          })

        } else if (data.type === 'stop_chat') {
          console.log('[Action Builder] Stop chat requested')
          if (claudeProcess) {
            console.log('[Action Builder] Killing Claude process:', claudeProcess.pid)
            claudeProcess.kill()
            claudeProcess = null
            console.log('[Action Builder] ✅ Process killed')
          } else {
            console.log('[Action Builder] No active process to kill')
          }
        }
      } catch (error) {
        console.error('[Action Builder] ========================================')
        console.error('[Action Builder] ❌ Error handling message:', error.message)
        console.error('[Action Builder] Error stack:', error.stack)
        console.error('[Action Builder] ========================================')
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({
            type: 'error',
            data: error.message
          }))
        }
      }
    })

    // Handle WebSocket close
    ws.on('close', (code, reason) => {
      console.log('[Action Builder] ========================================')
      console.log('[Action Builder] WebSocket closed')
      console.log('[Action Builder]   - Code:', code)
      console.log('[Action Builder]   - Reason:', reason.toString())
      console.log('[Action Builder] ========================================')
      if (claudeProcess) {
        console.log('[Action Builder] Killing Claude process on close:', claudeProcess.pid)
        claudeProcess.kill()
      }
    })

    // Handle WebSocket errors
    ws.on('error', (error) => {
      console.error('[Action Builder] ========================================')
      console.error('[Action Builder] ❌ WebSocket error:', error.message)
      console.error('[Action Builder] Error code:', error.code)
      console.error('[Action Builder] ========================================')
      if (claudeProcess) {
        console.log('[Action Builder] Killing Claude process on error:', claudeProcess.pid)
        claudeProcess.kill()
      }
    })

    // Send connection success
    console.log('[Action Builder] Sending connection success message...')
    ws.send(JSON.stringify({
      type: 'connected',
      message: 'Action Builder WebSocket connected'
    }))
    console.log('[Action Builder] ✅ Connection success message sent')
    console.log('[Action Builder] Waiting for messages from client...')
  }

  // Handle terminal WebSocket connections
  function handleTerminalConnection(ws) {
    console.log('[Terminal] New WebSocket connection')

    const sessionId = Date.now().toString()

    // Spawn a new terminal process
    const shell = process.env.SHELL || '/bin/bash'
    const ptyProcess = spawn(shell, [], {
      name: 'xterm-color',
      cols: 80,
      rows: 24,
      cwd: process.env.HOME || '/root',
      env: process.env
    })

    // Store the terminal session
    terminals.set(sessionId, ptyProcess)

    console.log(`[Terminal] Spawned shell: ${shell}`)

    // Forward terminal output to WebSocket
    ptyProcess.onData((data) => {
      try {
        if (ws.readyState === 1) { // OPEN
          ws.send(JSON.stringify({ type: 'output', data }))
        }
      } catch (error) {
        console.error('[Terminal] Error sending data:', error)
      }
    })

    // Handle terminal process exit
    ptyProcess.onExit(({ exitCode, signal }) => {
      console.log(`[Terminal] Process exited: ${exitCode}, signal: ${signal}`)
      terminals.delete(sessionId)
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'exit', exitCode }))
          ws.close()
        }
      } catch (error) {
        console.error('[Terminal] Error closing WebSocket:', error)
      }
    })

    // Handle messages from WebSocket
    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message.toString())

        if (data.type === 'input') {
          ptyProcess.write(data.data)
        } else if (data.type === 'resize') {
          ptyProcess.resize(data.cols || 80, data.rows || 24)
        }
      } catch (error) {
        console.error('[Terminal] Error handling message:', error)
      }
    })

    // Handle WebSocket close
    ws.on('close', () => {
      console.log(`[Terminal] WebSocket closed: ${sessionId}`)
      ptyProcess.kill()
      terminals.delete(sessionId)
    })

    // Handle WebSocket errors
    ws.on('error', (error) => {
      console.error('[Terminal] WebSocket error:', error)
      ptyProcess.kill()
      terminals.delete(sessionId)
    })

    // Send initial connection success
    ws.send(JSON.stringify({
      type: 'connected',
      sessionId,
      message: 'Terminal session established'
    }))
  }

  // Handle logs WebSocket connections
  function handleLogsConnection(ws, request) {
    console.log('[Logs] New WebSocket connection')

    const { exec } = require('child_process')
    const url = new URL(request.url, `http://${request.headers.host}`)
    const containerName = url.searchParams.get('container')

    if (!containerName) {
      ws.send(JSON.stringify({ type: 'error', message: 'Container name required' }))
      ws.close()
      return
    }

    console.log(`[Logs] Streaming logs for container: ${containerName}`)

    // Stream docker logs with follow flag
    const logsProcess = exec(`docker logs -f --tail 100 ${containerName}`)

    // Send stdout
    logsProcess.stdout.on('data', (data) => {
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'log', data: data.toString() }))
        }
      } catch (error) {
        console.error('[Logs] Error sending stdout:', error)
      }
    })

    // Send stderr
    logsProcess.stderr.on('data', (data) => {
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'log', data: data.toString() }))
        }
      } catch (error) {
        console.error('[Logs] Error sending stderr:', error)
      }
    })

    // Handle process errors
    logsProcess.on('error', (error) => {
      console.error('[Logs] Process error:', error)
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'error', message: error.message }))
        }
      } catch {}
    })

    // Handle process exit
    logsProcess.on('exit', (code) => {
      console.log(`[Logs] Process exited with code: ${code}`)
      try {
        if (ws.readyState === 1) {
          ws.send(JSON.stringify({ type: 'exit', code }))
        }
      } catch {}
    })

    // Handle WebSocket close
    ws.on('close', () => {
      console.log('[Logs] WebSocket closed, killing process')
      logsProcess.kill()
    })

    // Handle WebSocket errors
    ws.on('error', (error) => {
      console.error('[Logs] WebSocket error:', error)
      logsProcess.kill()
    })

    // Send connection success
    ws.send(JSON.stringify({
      type: 'connected',
      message: `Streaming logs for ${containerName}`
    }))
  }

  server.listen(port, async (err) => {
    if (err) throw err

    // Initialize Action Builder
    console.log('[Action Builder] Initializing...')
    try {
      await ensureAgentFile()
      await ensureFlowArchitectProject()
      console.log('[Action Builder] ✅ Initialization complete')
    } catch (error) {
      console.error('[Action Builder] ❌ Initialization failed:', error)
    }

    console.log(`> Ready on http://${hostname}:${port}`)
    console.log(`> WebSocket terminal available on ws://${hostname}:${port}/api/terminal/ws`)
    console.log(`> WebSocket Action Builder available on ws://${hostname}:${port}/api/action-builder/ws`)
  })
})
