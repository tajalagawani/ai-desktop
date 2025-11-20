/**
 * Backend Server - Express REST API
 * Handles all API routes. WebSocket communications delegated to standalone WS server (port 3007)
 */

const express = require('express')
const { createServer} = require('http')
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

// WebSocket client for communicating with standalone WS server
const wsClient = require('./lib/ws-client')

// Export WebSocket client for use in API routes (replaces old global.socketIO)
global.socketIO = wsClient

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
app.get('/api/status', async (req, res) => {
  // Get WebSocket server health
  let wsHealth = { connections: 0 }
  try {
    wsHealth = await wsClient.checkWSHealth()
  } catch (error) {
    // WebSocket server not available
  }

  res.json({
    success: true,
    data: {
      status: 'running',
      version: '1.0.0',
      environment: NODE_ENV,
      websocketServer: wsHealth.success ? 'connected' : 'disconnected',
      websocketConnections: wsHealth.connections || 0,
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
