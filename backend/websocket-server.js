/**
 * Standalone WebSocket Server
 * Handles ALL real-time communications for AI Desktop
 * Port: 3007
 */

const { Server } = require('socket.io')
const { createServer } = require('http')
const { spawn } = require('child_process')
const fs = require('fs').promises
const path = require('path')

// Configuration
const WS_PORT = process.env.WS_PORT || 3007
const NODE_ENV = process.env.NODE_ENV || 'development'
const IS_MAC = process.platform === 'darwin'
const IS_VPS = NODE_ENV === 'production' && !IS_MAC

// Dynamic CORS configuration based on environment
const CLIENT_URL = process.env.CLIENT_URL || 'http://localhost:3005'
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:3006'
const VPS_IP = process.env.VPS_IP || ''

// Build CORS origins array
const corsOrigins = [
  CLIENT_URL,
  BACKEND_URL,
  'http://localhost:3005',
  'http://localhost:3006',
]

// Add VPS origins if in production
if (IS_VPS && VPS_IP) {
  corsOrigins.push(
    `http://${VPS_IP}`,
    `http://${VPS_IP}:80`,
    `http://${VPS_IP}:3005`,
    `http://${VPS_IP}:3006`
  )
}

console.log(`[WS Server] Environment: ${NODE_ENV}`)
console.log(`[WS Server] Platform: ${process.platform} (${IS_MAC ? 'Mac' : 'VPS'})`)
console.log(`[WS Server] CORS Origins:`, corsOrigins)

// Create HTTP server for Socket.IO
const httpServer = createServer()

// Initialize Socket.IO with dynamic CORS
const io = new Server(httpServer, {
  cors: {
    origin: corsOrigins,
    credentials: true,
    methods: ['GET', 'POST']
  },
  transports: ['websocket', 'polling'],
  path: '/socket.io/',
  pingTimeout: 60000,
  pingInterval: 25000,
})

// Store active log streams
const activeStreams = new Map()

// Namespaces for different features
const servicesNS = io.of('/services')
const deploymentsNS = io.of('/deployments')
const systemNS = io.of('/system')
const mcpNS = io.of('/mcp')
const filesNS = io.of('/files')

/**
 * Services Namespace - Docker container logs and stats
 */
servicesNS.on('connection', (socket) => {
  console.log(`[Services WS] Client connected: ${socket.id}`)

  // Subscribe to service logs
  socket.on('subscribe:logs', async ({ serviceId, containerName }) => {
    console.log(`[Services WS] Subscribe to logs: ${containerName}`)

    const streamKey = `service:${containerName}`

    // Close existing stream if any
    if (activeStreams.has(streamKey)) {
      activeStreams.get(streamKey).kill()
      activeStreams.delete(streamKey)
    }

    try {
      // Start docker logs stream
      const dockerLogs = spawn('docker', ['logs', '-f', '--tail', '100', containerName])

      activeStreams.set(streamKey, dockerLogs)

      dockerLogs.stdout.on('data', (data) => {
        socket.emit('logs', {
          serviceId,
          containerName,
          data: data.toString(),
          timestamp: new Date().toISOString()
        })
      })

      dockerLogs.stderr.on('data', (data) => {
        socket.emit('logs', {
          serviceId,
          containerName,
          data: data.toString(),
          timestamp: new Date().toISOString(),
          type: 'error'
        })
      })

      dockerLogs.on('error', (error) => {
        socket.emit('error', {
          serviceId,
          containerName,
          message: error.message
        })
        activeStreams.delete(streamKey)
      })

      dockerLogs.on('close', (code) => {
        console.log(`[Services WS] Docker logs closed for ${containerName} (code: ${code})`)
        activeStreams.delete(streamKey)
        socket.emit('stream:closed', { serviceId, containerName, code })
      })

      socket.emit('connected', { serviceId, containerName })
    } catch (error) {
      socket.emit('error', {
        serviceId,
        containerName,
        message: error.message
      })
    }
  })

  // Unsubscribe from service logs
  socket.on('unsubscribe:logs', ({ containerName }) => {
    const streamKey = `service:${containerName}`
    if (activeStreams.has(streamKey)) {
      activeStreams.get(streamKey).kill()
      activeStreams.delete(streamKey)
      console.log(`[Services WS] Unsubscribed from ${containerName}`)
    }
  })

  socket.on('disconnect', () => {
    console.log(`[Services WS] Client disconnected: ${socket.id}`)
    // Clean up any streams this socket created
    activeStreams.forEach((stream, key) => {
      if (key.startsWith('service:')) {
        stream.kill()
        activeStreams.delete(key)
      }
    })
  })
})

/**
 * Deployments Namespace - PM2 deployment logs
 */
deploymentsNS.on('connection', (socket) => {
  console.log(`[Deployments WS] Client connected: ${socket.id}`)

  // Subscribe to deployment logs
  socket.on('subscribe:logs', async ({ deploymentId, pm2Name }) => {
    console.log(`[Deployments WS] Subscribe to logs: ${pm2Name}`)

    const streamKey = `deployment:${pm2Name}`

    // Close existing stream if any
    if (activeStreams.has(streamKey)) {
      activeStreams.get(streamKey).kill()
      activeStreams.delete(streamKey)
    }

    try {
      // Start PM2 logs stream
      const pm2Logs = spawn('pm2', ['logs', pm2Name, '--raw', '--lines', '100'])

      activeStreams.set(streamKey, pm2Logs)

      pm2Logs.stdout.on('data', (data) => {
        socket.emit('logs', {
          deploymentId,
          pm2Name,
          data: data.toString(),
          timestamp: new Date().toISOString()
        })
      })

      pm2Logs.stderr.on('data', (data) => {
        socket.emit('logs', {
          deploymentId,
          pm2Name,
          data: data.toString(),
          timestamp: new Date().toISOString(),
          type: 'error'
        })
      })

      pm2Logs.on('error', (error) => {
        socket.emit('error', {
          deploymentId,
          pm2Name,
          message: error.message
        })
        activeStreams.delete(streamKey)
      })

      pm2Logs.on('close', (code) => {
        console.log(`[Deployments WS] PM2 logs closed for ${pm2Name} (code: ${code})`)
        activeStreams.delete(streamKey)
        socket.emit('stream:closed', { deploymentId, pm2Name, code })
      })

      socket.emit('connected', { deploymentId, pm2Name })
    } catch (error) {
      socket.emit('error', {
        deploymentId,
        pm2Name,
        message: error.message
      })
    }
  })

  // Unsubscribe from deployment logs
  socket.on('unsubscribe:logs', ({ pm2Name }) => {
    const streamKey = `deployment:${pm2Name}`
    if (activeStreams.has(streamKey)) {
      activeStreams.get(streamKey).kill()
      activeStreams.delete(streamKey)
      console.log(`[Deployments WS] Unsubscribed from ${pm2Name}`)
    }
  })

  socket.on('disconnect', () => {
    console.log(`[Deployments WS] Client disconnected: ${socket.id}`)
    // Clean up any streams this socket created
    activeStreams.forEach((stream, key) => {
      if (key.startsWith('deployment:')) {
        stream.kill()
        activeStreams.delete(key)
      }
    })
  })
})

/**
 * System Namespace - System stats, PM2 processes, etc.
 */
systemNS.on('connection', (socket) => {
  console.log(`[System WS] Client connected: ${socket.id}`)

  let statsInterval = null

  // Subscribe to system stats updates
  socket.on('subscribe:stats', ({ interval = 3000 }) => {
    console.log(`[System WS] Subscribe to stats (interval: ${interval}ms)`)

    // Clear existing interval
    if (statsInterval) {
      clearInterval(statsInterval)
    }

    // Send stats immediately
    emitSystemStats(socket)

    // Then send at intervals
    statsInterval = setInterval(() => {
      emitSystemStats(socket)
    }, interval)

    socket.emit('connected')
  })

  // Unsubscribe from stats
  socket.on('unsubscribe:stats', () => {
    if (statsInterval) {
      clearInterval(statsInterval)
      statsInterval = null
      console.log(`[System WS] Unsubscribed from stats`)
    }
  })

  socket.on('disconnect', () => {
    if (statsInterval) {
      clearInterval(statsInterval)
    }
    console.log(`[System WS] Client disconnected: ${socket.id}`)
  })
})

/**
 * MCP Namespace - MCP server events
 */
mcpNS.on('connection', (socket) => {
  console.log(`[MCP WS] Client connected: ${socket.id}`)

  // Join MCP server room
  socket.on('join', ({ serverId }) => {
    socket.join(`mcp:${serverId}`)
    console.log(`[MCP WS] Client ${socket.id} joined server: ${serverId}`)
    socket.emit('joined', { serverId })
  })

  // Leave MCP server room
  socket.on('leave', ({ serverId }) => {
    socket.leave(`mcp:${serverId}`)
    console.log(`[MCP WS] Client ${socket.id} left server: ${serverId}`)
  })

  socket.on('disconnect', () => {
    console.log(`[MCP WS] Client disconnected: ${socket.id}`)
  })
})

/**
 * Files Namespace - File system watch events
 */
filesNS.on('connection', (socket) => {
  console.log(`[Files WS] Client connected: ${socket.id}`)

  // Subscribe to directory changes
  socket.on('watch', async ({ path: dirPath }) => {
    console.log(`[Files WS] Watch directory: ${dirPath}`)
    // TODO: Implement file watcher
    socket.emit('connected', { path: dirPath })
  })

  socket.on('disconnect', () => {
    console.log(`[Files WS] Client disconnected: ${socket.id}`)
  })
})

/**
 * Helper Functions
 */

async function emitSystemStats(socket) {
  const os = require('os')
  const { exec } = require('child_process')
  const { promisify } = require('util')
  const execAsync = promisify(exec)

  try {
    // Get PM2 list
    let pm2Processes = []
    try {
      const { stdout } = await execAsync('pm2 jlist')
      pm2Processes = JSON.parse(stdout)
    } catch (error) {
      // PM2 not available
    }

    const stats = {
      cpu: {
        count: os.cpus().length,
        usage: os.loadavg()[0] * 100 / os.cpus().length,
        loadAvg: os.loadavg()
      },
      memory: {
        total: os.totalmem(),
        free: os.freemem(),
        used: os.totalmem() - os.freemem(),
        usagePercent: ((os.totalmem() - os.freemem()) / os.totalmem()) * 100
      },
      uptime: os.uptime(),
      platform: os.platform(),
      hostname: os.hostname(),
      pm2Processes: pm2Processes.length,
      timestamp: new Date().toISOString()
    }

    socket.emit('stats', stats)
  } catch (error) {
    socket.emit('error', { message: error.message })
  }
}

/**
 * HTTP API for backend to emit events
 */
const express = require('express')
const app = express()
app.use(express.json())

// Emit event to specific namespace/room
app.post('/emit', (req, res) => {
  const { namespace, room, event, data } = req.body

  try {
    const ns = io.of(`/${namespace}`)
    if (room) {
      ns.to(room).emit(event, data)
    } else {
      ns.emit(event, data)
    }
    res.json({ success: true })
  } catch (error) {
    res.status(500).json({ success: false, error: error.message })
  }
})

// Health check
app.get('/health', (req, res) => {
  res.json({
    success: true,
    status: 'healthy',
    connections: {
      services: servicesNS.sockets.size,
      deployments: deploymentsNS.sockets.size,
      system: systemNS.sockets.size,
      mcp: mcpNS.sockets.size,
      files: filesNS.sockets.size
    },
    activeStreams: activeStreams.size
  })
})

// Attach express to httpServer
httpServer.on('request', app)

// Start server
httpServer.listen(WS_PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════╗
║                                               ║
║   🔌 WebSocket Server                         ║
║                                               ║
║   Port: ${String(WS_PORT).padEnd(37)} ║
║   Health: http://localhost:${WS_PORT}/health${' '.repeat(10)} ║
║                                               ║
║   Namespaces:                                 ║
║   - /services     (Docker logs & stats)       ║
║   - /deployments  (PM2 logs)                  ║
║   - /system       (System stats)              ║
║   - /mcp          (MCP events)                ║
║   - /files        (File watching)             ║
║                                               ║
╚═══════════════════════════════════════════════╝
  `)
})

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('[WS Server] SIGTERM received, closing server...')

  // Kill all active streams
  activeStreams.forEach((stream) => stream.kill())
  activeStreams.clear()

  httpServer.close(() => {
    console.log('[WS Server] Server closed')
    process.exit(0)
  })
})

process.on('SIGINT', () => {
  console.log('[WS Server] SIGINT received, closing server...')

  // Kill all active streams
  activeStreams.forEach((stream) => stream.kill())
  activeStreams.clear()

  httpServer.close(() => {
    console.log('[WS Server] Server closed')
    process.exit(0)
  })
})

module.exports = { io, servicesNS, deploymentsNS, systemNS, mcpNS, filesNS }
