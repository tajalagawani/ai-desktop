/**
 * Backend Server - Express + Socket.IO
 * Handles all API routes and real-time WebSocket connections
 */

const express = require('express')
const { createServer} = require('http')
const { Server } = require('socket.io')
const cors = require('cors')
const path = require('path')
require('dotenv').config()

// Environment configuration
const PORT = process.env.PORT || 3006
const NODE_ENV = process.env.NODE_ENV || 'development'
const CLIENT_URL = process.env.CLIENT_URL || 'http://localhost:3005'

// Initialize Express app
const app = express()
const httpServer = createServer(app)

// Initialize Socket.IO
const io = new Server(httpServer, {
  cors: {
    origin: [CLIENT_URL, 'http://92.112.181.127', 'http://localhost:3005', 'http://localhost:3001'],
    credentials: true,
  },
  transports: ['websocket', 'polling'],
})

// Middleware
app.use(cors({
  origin: [CLIENT_URL, 'http://92.112.181.127', 'http://localhost:3005', 'http://localhost:3001'],
  credentials: true,
}))
app.use(express.json({ limit: '50mb' }))
app.use(express.urlencoded({ extended: true, limit: '50mb' }))

// Request logging
app.use((req, res, next) => {
  const timestamp = new Date().toISOString()
  console.log(`[${timestamp}] ${req.method} ${req.path}`)
  next()
})

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    success: true,
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
  })
})

// API root endpoint
app.get('/api', (req, res) => {
  res.json({
    success: true,
    message: 'AI Desktop Backend API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      status: '/api/status',
      vscode: '/api/vscode',
      mcp: '/api/mcp',
      services: '/api/services',
      flowBuilder: '/api/flow-builder',
      deployments: '/api/deployments',
      repositories: '/api/repositories',
      pm2Processes: '/api/pm2-processes',
      git: '/api/git',
      gitConfig: '/api/git-config',
      systemStats: '/api/system-stats',
      files: '/api/files',
    },
  })
})

// API status endpoint
app.get('/api/status', (req, res) => {
  res.json({
    success: true,
    data: {
      status: 'running',
      version: '1.0.0',
      environment: NODE_ENV,
      socketConnections: io.engine.clientsCount,
    },
  })
})

// Mount API routes
const vscodeRoutes = require('./app/api/vscode')
const mcpRoutes = require('./app/api/mcp')
const servicesRoutes = require('./app/api/services')
const flowBuilderRoutes = require('./app/api/flow-builder')
const deploymentsRoutes = require('./app/api/deployments')
const repositoriesRoutes = require('./app/api/repositories')
const pm2ProcessesRoutes = require('./app/api/pm2-processes')
const gitRoutes = require('./app/api/git')
const gitConfigRoutes = require('./app/api/git-config')
const systemStatsRoutes = require('./app/api/system-stats')
const filesRoutes = require('./app/api/files')

app.use('/api/vscode', vscodeRoutes)
app.use('/api/mcp', mcpRoutes)
app.use('/api/services', servicesRoutes)
app.use('/api/flow-builder', flowBuilderRoutes)
app.use('/api/deployments', deploymentsRoutes)
app.use('/api/repositories', repositoriesRoutes)
app.use('/api/pm2-processes', pm2ProcessesRoutes)
app.use('/api/git', gitRoutes)
app.use('/api/git-config', gitConfigRoutes)
app.use('/api/system-stats', systemStatsRoutes)
app.use('/api/files', filesRoutes)

// Socket.IO connection handling
io.on('connection', (socket) => {
  const clientId = socket.id
  console.log(`[WS] Client connected: ${clientId}`)

  // Join room for specific agent
  socket.on('agent:join', (agentId) => {
    socket.join(`agent:${agentId}`)
    console.log(`[WS] Client ${clientId} joined agent room: ${agentId}`)
  })

  // Leave agent room
  socket.on('agent:leave', (agentId) => {
    socket.leave(`agent:${agentId}`)
    console.log(`[WS] Client ${clientId} left agent room: ${agentId}`)
  })

  // Join MCP server room
  socket.on('mcp:join', (serverId) => {
    socket.join(`mcp:${serverId}`)
    console.log(`[WS] Client ${clientId} joined MCP room: ${serverId}`)
  })

  // Leave MCP server room
  socket.on('mcp:leave', (serverId) => {
    socket.leave(`mcp:${serverId}`)
    console.log(`[WS] Client ${clientId} left MCP room: ${serverId}`)
  })

  // Join service room
  socket.on('service:join', (serviceId) => {
    socket.join(`service:${serviceId}`)
    console.log(`[WS] Client ${clientId} joined service room: ${serviceId}`)
  })

  // Leave service room
  socket.on('service:leave', (serviceId) => {
    socket.leave(`service:${serviceId}`)
    console.log(`[WS] Client ${clientId} left service room: ${serviceId}`)
  })

  // Join deployment room
  socket.on('deployment:join', (deploymentId) => {
    socket.join(`deployment:${deploymentId}`)
    console.log(`[WS] Client ${clientId} joined deployment room: ${deploymentId}`)
  })

  // Leave deployment room
  socket.on('deployment:leave', (deploymentId) => {
    socket.leave(`deployment:${deploymentId}`)
    console.log(`[WS] Client ${clientId} left deployment room: ${deploymentId}`)
  })

  // Handle disconnection
  socket.on('disconnect', (reason) => {
    console.log(`[WS] Client disconnected: ${clientId} (${reason})`)
  })

  // Handle errors
  socket.on('error', (error) => {
    console.error(`[WS] Socket error for ${clientId}:`, error)
  })
})

// Utility function to emit to specific rooms
const emitToAgent = (agentId, event, data) => {
  io.to(`agent:${agentId}`).emit(`agent:${agentId}:${event}`, data)
}

const emitToMCP = (serverId, event, data) => {
  io.to(`mcp:${serverId}`).emit(`mcp:${serverId}:${event}`, data)
}

const emitToService = (serviceId, event, data) => {
  io.to(`service:${serviceId}`).emit(`service:${serviceId}:${event}`, data)
}

const emitToDeployment = (deploymentId, event, data) => {
  io.to(`deployment:${deploymentId}`).emit(`deployment:${deploymentId}:${event}`, data)
}

// Export emit functions for use in API routes
global.socketIO = {
  io,
  emitToAgent,
  emitToMCP,
  emitToService,
  emitToDeployment,
}

// WebSocket Routes - Commented out to avoid conflict with Socket.IO
// These routes used express-ws which conflicts with socket.io on the same HTTP server
// TODO: Convert these to Socket.IO namespaces if needed
// const { handleDeploymentLogsConnection } = require('./app/websocket/deployment-logs')
// const { handleServiceLogsConnection } = require('./app/websocket/service-logs')

// app.ws('/api/deployments/logs/ws', (ws, req) => {
//   handleDeploymentLogsConnection(ws, req)
// })

// app.ws('/api/services/logs/ws', (ws, req) => {
//   handleServiceLogsConnection(ws, req)
// })

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('[ERROR]', err)
  res.status(err.status || 500).json({
    success: false,
    error: err.message || 'Internal server error',
  })
})

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
  })
})

// Start server
httpServer.listen(PORT, async () => {
  console.log(`
╔═══════════════════════════════════════════════╗
║                                               ║
║   🚀 AI Desktop Backend Server                ║
║                                               ║
║   Environment: ${NODE_ENV.padEnd(31)} ║
║   Port: ${String(PORT).padEnd(37)} ║
║   Health: http://localhost:${PORT}/health${' '.repeat(11)} ║
║   API: http://localhost:${PORT}/api${' '.repeat(15)} ║
║                                               ║
║   Socket.IO: ✅ Ready                          ║
║   CORS: ✅ Configured                          ║
║   Storage: ✅ JSON Files (Lightweight)         ║
║   MCP: ✅ Reading from config files            ║
║                                               ║
╚═══════════════════════════════════════════════╝
  `)
})

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('[SERVER] SIGTERM received, closing server...')
  httpServer.close(() => {
    console.log('[SERVER] Server closed')
    process.exit(0)
  })
})

process.on('SIGINT', () => {
  console.log('[SERVER] SIGINT received, closing server...')
  httpServer.close(() => {
    console.log('[SERVER] Server closed')
    process.exit(0)
  })
})
