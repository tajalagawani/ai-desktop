/**
 * MCP Hub API Routes
 * Handles Model Context Protocol servers
 */

const express = require('express')
const router = express.Router()

/**
 * GET /api/mcp
 * List all MCP servers from config files
 */
router.get('/', async (req, res) => {
  try {
    const fs = require('fs').promises
    const path = require('path')
    const servers = []

    // Load from .mcp.json
    try {
      const mcpConfigPath = path.join(__dirname, '../../../.mcp.json')
      const content = await fs.readFile(mcpConfigPath, 'utf-8')
      const mcpConfig = JSON.parse(content)

      for (const [serverId, config] of Object.entries(mcpConfig.mcpServers || {})) {
        if (config.disabled) continue

        servers.push({
          id: serverId,
          name: config.name || serverId,
          description: config.description || '',
          command: config.command,
          args: config.args || [],
          env: config.env || {},
          workingDirectory: config.cwd || null,
          status: 'available',
          type: 'mcp',
          source: '.mcp.json'
        })
      }
    } catch (error) {
      console.log('[MCP] No .mcp.json found')
    }

    // Load from data/mcp-servers.json
    try {
      const dataConfigPath = path.join(__dirname, '../../../data/mcp-servers.json')
      const content = await fs.readFile(dataConfigPath, 'utf-8')
      const dataConfig = JSON.parse(content)

      for (const server of dataConfig.servers || []) {
        servers.push({
          id: server.id,
          name: server.name,
          description: server.description || '',
          command: server.command,
          args: server.args || [],
          env: server.env || {},
          workingDirectory: server.cwd || null,
          status: 'available',
          type: 'mcp',
          source: 'data/mcp-servers.json',
          toolCount: server.toolCount
        })
      }
    } catch (error) {
      console.log('[MCP] No data/mcp-servers.json found')
    }

    res.json({
      success: true,
      servers,
      count: servers.length,
    })
  } catch (error) {
    console.error('[API MCP GET] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/mcp/sync
 * Sync MCP servers from .mcp.json file to database
 */
router.post('/sync', async (req, res) => {
  try {
    const fs = require('fs').promises
    const path = require('path')

    // Read .mcp.json from project root
    const mcpConfigPath = path.join(__dirname, '../../../.mcp.json')

    let mcpConfig
    try {
      const content = await fs.readFile(mcpConfigPath, 'utf-8')
      mcpConfig = JSON.parse(content)
    } catch (error) {
      return res.status(404).json({
        success: false,
        error: '.mcp.json file not found or invalid JSON'
      })
    }

    const db = require('../../lib/db')
    const synced = []
    const errors = []

    // Sync each server from config
    for (const [serverId, config] of Object.entries(mcpConfig.mcpServers || {})) {
      if (config.disabled) {
        console.log(`[MCP Sync] Skipping disabled server: ${serverId}`)
        continue
      }

      try {
        // Check if server exists
        const existing = await db.query('SELECT id FROM mcp_servers WHERE id = $1', [serverId])

        if (existing.rows.length > 0) {
          // Update existing
          await db.query(`
            UPDATE mcp_servers
            SET command = $1, args = $2, env = $3, working_directory = $4, updated_at = NOW()
            WHERE id = $5
          `, [
            config.command,
            JSON.stringify(config.args || []),
            JSON.stringify(config.env || {}),
            config.cwd || null,
            serverId
          ])
          console.log(`[MCP Sync] Updated server: ${serverId}`)
        } else {
          // Insert new
          await db.query(`
            INSERT INTO mcp_servers (id, name, description, command, args, working_directory, env, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
          `, [
            serverId,
            config.name || serverId,
            config.description || '',
            config.command,
            JSON.stringify(config.args || []),
            config.cwd || null,
            JSON.stringify(config.env || {}),
            'stopped'
          ])
          console.log(`[MCP Sync] Added server: ${serverId}`)
        }

        synced.push(serverId)
      } catch (error) {
        console.error(`[MCP Sync] Error syncing ${serverId}:`, error)
        errors.push({ serverId, error: error.message })
      }
    }

    res.json({
      success: true,
      message: `Synced ${synced.length} MCP server(s) from .mcp.json`,
      synced,
      errors
    })
  } catch (error) {
    console.error('[API MCP Sync] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/mcp
 * Create a new custom MCP server
 */
router.post('/', async (req, res) => {
  try {
    const {
      id,
      name,
      description,
      command,
      args,
      cwd,
      env,
    } = req.body

    // Validation
    if (!id || !name || !command || !args) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: id, name, command, args'
      })
    }

    // Check if ID already exists
    const db = require('../../lib/db')
    const existing = await db.query('SELECT id FROM mcp_servers WHERE id = $1', [id])

    if (existing.rows.length > 0) {
      return res.status(400).json({
        success: false,
        error: 'Server with this ID already exists'
      })
    }

    // Insert new server
    const result = await db.query(`
      INSERT INTO mcp_servers (id, name, description, command, args, working_directory, env, status)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      RETURNING *
    `, [
      id,
      name,
      description || '',
      command,
      JSON.stringify(Array.isArray(args) ? args : [args]),
      cwd || null,
      JSON.stringify(env || {}),
      'stopped'
    ])

    const server = {
      id: result.rows[0].id,
      name: result.rows[0].name,
      description: result.rows[0].description,
      command: result.rows[0].command,
      args: result.rows[0].args,
      workingDirectory: result.rows[0].working_directory,
      env: result.rows[0].env,
      status: result.rows[0].status,
      createdAt: result.rows[0].created_at,
    }

    res.json({
      success: true,
      server,
    })
  } catch (error) {
    console.error('[API MCP POST] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * GET /api/mcp/:id
 * Get a specific MCP server from config files
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params
    const fs = require('fs').promises
    const path = require('path')

    // Check .mcp.json
    try {
      const mcpConfigPath = path.join(__dirname, '../../../.mcp.json')
      const content = await fs.readFile(mcpConfigPath, 'utf-8')
      const mcpConfig = JSON.parse(content)

      if (mcpConfig.mcpServers && mcpConfig.mcpServers[id]) {
        const config = mcpConfig.mcpServers[id]
        return res.json({
          success: true,
          server: {
            id,
            name: config.name || id,
            description: config.description || '',
            command: config.command,
            args: config.args || [],
            env: config.env || {},
            workingDirectory: config.cwd || null,
            status: 'available',
            type: 'mcp',
            source: '.mcp.json'
          }
        })
      }
    } catch (error) {
      // Continue to next source
    }

    // Check data/mcp-servers.json
    try {
      const dataConfigPath = path.join(__dirname, '../../../data/mcp-servers.json')
      const content = await fs.readFile(dataConfigPath, 'utf-8')
      const dataConfig = JSON.parse(content)

      const server = (dataConfig.servers || []).find(s => s.id === id)
      if (server) {
        return res.json({
          success: true,
          server: {
            id: server.id,
            name: server.name,
            description: server.description || '',
            command: server.command,
            args: server.args || [],
            env: server.env || {},
            workingDirectory: server.cwd || null,
            status: 'available',
            type: 'mcp',
            source: 'data/mcp-servers.json',
            toolCount: server.toolCount
          }
        })
      }
    } catch (error) {
      // Continue
    }

    return res.status(404).json({
      success: false,
      error: 'Server not found'
    })
  } catch (error) {
    console.error('[API MCP GET/:id] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/mcp/:id/action
 * Perform action on MCP server (start/stop/restart/delete)
 */
router.post('/:id/action', async (req, res) => {
  try {
    const { id } = req.params
    const { action } = req.body

    if (!action || !['start', 'stop', 'restart', 'delete'].includes(action)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid action. Must be: start, stop, restart, or delete'
      })
    }

    console.log(`[API MCP ACTION] ${action} server: ${id}`)

    const fs = require('fs').promises
    const path = require('path')
    let server = null

    // Find server in config files
    try {
      const mcpConfigPath = path.join(__dirname, '../../../.mcp.json')
      const content = await fs.readFile(mcpConfigPath, 'utf-8')
      const mcpConfig = JSON.parse(content)
      if (mcpConfig.mcpServers && mcpConfig.mcpServers[id]) {
        const config = mcpConfig.mcpServers[id]
        server = {
          id,
          name: config.name || id,
          description: config.description || '',
          command: config.command,
          args: config.args || [],
          env: config.env || {},
          working_directory: config.cwd || null
        }
      }
    } catch (error) {
      // Continue
    }

    if (!server) {
      try {
        const dataConfigPath = path.join(__dirname, '../../../data/mcp-servers.json')
        const content = await fs.readFile(dataConfigPath, 'utf-8')
        const dataConfig = JSON.parse(content)
        const found = (dataConfig.servers || []).find(s => s.id === id)
        if (found) {
          server = {
            id: found.id,
            name: found.name,
            description: found.description || '',
            command: found.command,
            args: found.args || [],
            env: found.env || {},
            working_directory: found.cwd || null
          }
        }
      } catch (error) {
        // Continue
      }
    }

    if (!server) {
      return res.status(404).json({
        success: false,
        error: 'Server not found'
      })
    }

    // Handle delete
    if (action === 'delete') {
      // Stop process if running
      if (server.pid) {
        try {
          process.kill(server.pid, 'SIGTERM')
          setTimeout(() => {
            try {
              process.kill(server.pid, 0)
              process.kill(server.pid, 'SIGKILL')
            } catch {
              // Already stopped
            }
          }, 2000)
        } catch {
          // Process already stopped
        }
      }

      await db.query('DELETE FROM mcp_servers WHERE id = $1', [id])

      // Broadcast update via WebSocket
      if (global.socketIO && global.socketIO.io) {
        global.socketIO.io.emit('mcp:deleted', { id })
      }

      return res.json({
        success: true,
        message: 'Server deleted'
      })
    }

    // Handle start/stop/restart
    // MCP servers using stdio transport are always "available"
    // They are invoked by MCP clients when needed, not run as standalone processes

    if (action === 'start') {
      return res.json({
        success: true,
        message: `${server.name} is ready to use`,
        status: 'available'
      })
    }

    if (action === 'stop') {
      return res.json({
        success: true,
        message: `${server.name} is available`,
        status: 'available'
      })
    }

    if (action === 'restart') {
      return res.json({
        success: true,
        message: `${server.name} is available`,
        status: 'available'
      })
    }
  } catch (error) {
    console.error('[API MCP ACTION] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * GET /api/mcp/:id/tools
 * Get tools for a specific MCP server
 */
router.get('/:id/tools', async (req, res) => {
  try {
    const { id } = req.params
    const fs = require('fs').promises
    const path = require('path')
    const { spawn } = require('child_process')
    let server = null

    // Find server in config files
    try {
      const mcpConfigPath = path.join(__dirname, '../../../.mcp.json')
      const content = await fs.readFile(mcpConfigPath, 'utf-8')
      const mcpConfig = JSON.parse(content)
      if (mcpConfig.mcpServers && mcpConfig.mcpServers[id]) {
        const config = mcpConfig.mcpServers[id]
        server = {
          command: config.command,
          args: config.args || [],
          env: config.env || {},
          working_directory: config.cwd || null
        }
      }
    } catch (error) {
      // Continue
    }

    if (!server) {
      try {
        const dataConfigPath = path.join(__dirname, '../../../data/mcp-servers.json')
        const content = await fs.readFile(dataConfigPath, 'utf-8')
        const dataConfig = JSON.parse(content)
        const found = (dataConfig.servers || []).find(s => s.id === id)
        if (found) {
          server = {
            command: found.command,
            args: found.args || [],
            env: found.env || {},
            working_directory: found.cwd || null
          }
        }
      } catch (error) {
        // Continue
      }
    }

    if (!server) {
      return res.status(404).json({
        success: false,
        error: 'Server not found'
      })
    }

    const args = server.args
    const env = server.env

    // Spawn MCP server to fetch tools
    const mcpProcess = spawn(server.command, args, {
      cwd: server.working_directory || process.cwd(),
      env: { ...process.env, ...env },
      stdio: ['pipe', 'pipe', 'pipe']
    })

    let stdoutData = ''
    let stderrData = ''
    let toolsList = []

    mcpProcess.stdout.on('data', (data) => {
      stdoutData += data.toString()
      // Try to parse JSON-RPC responses
      const lines = stdoutData.split('\n')
      for (const line of lines) {
        if (line.trim()) {
          try {
            const msg = JSON.parse(line)
            if (msg.result && msg.result.tools) {
              toolsList = msg.result.tools
            }
          } catch {
            // Not JSON, ignore
          }
        }
      }
    })

    mcpProcess.stderr.on('data', (data) => {
      stderrData += data.toString()
    })

    // Send list_tools request
    const request = {
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/list',
      params: {}
    }
    mcpProcess.stdin.write(JSON.stringify(request) + '\n')
    mcpProcess.stdin.end()

    // Wait for response
    await new Promise((resolve) => {
      setTimeout(() => {
        mcpProcess.kill()
        resolve()
      }, 3000) // 3 second timeout
    })

    res.json({
      success: true,
      tools: toolsList,
      count: toolsList.length
    })
  } catch (error) {
    console.error('[API MCP TOOLS] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/mcp/:id/execute
 * Execute a tool on a specific MCP server
 */
router.post('/:id/execute', async (req, res) => {
  try {
    const { id } = req.params
    const { tool, parameters } = req.body

    if (!tool) {
      return res.status(400).json({
        success: false,
        error: 'Tool name is required'
      })
    }

    console.log(`[API MCP EXECUTE] Tool: ${tool} on server: ${id}`)

    // TODO: Connect to MCP server and execute tool
    const result = {
      success: true,
      message: 'Tool execution not yet implemented'
    }

    res.json(result)
  } catch (error) {
    console.error('[API MCP EXECUTE] Error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

module.exports = router
