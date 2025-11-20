# WebSocket Architecture

## Overview

AI Desktop now uses a standalone WebSocket server for all real-time communications. This separates concerns and provides better scalability and maintainability.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Browser                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Frontend   │  │  REST APIs   │  │  WebSockets  │     │
│  │  (Next.js)   │  │              │  │  (Socket.IO) │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │ HTTP             │ HTTP             │ WS
          │ :3005            │ :3006            │ :3007
          ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Frontend      │  │   Backend       │  │   WebSocket     │
│   Server        │  │   API Server    │  │   Server        │
│                 │  │                 │  │                 │
│   Next.js 14    │  │   Express.js    │  │   Socket.IO     │
│   Port: 3005    │  │   Port: 3006    │  │   Port: 3007    │
└─────────────────┘  └────────┬────────┘  └─────────────────┘
                              │
                              │ HTTP
                              ▼
                     ┌─────────────────┐
                     │  WS HTTP API    │
                     │  /emit endpoint │
                     └─────────────────┘
```

## Services

### 1. Frontend Server (Port 3005)
- **Technology**: Next.js 14 with App Router
- **Purpose**: Serves the React application
- **Environment Variables**:
  - `PORT=3005`
  - `NEXT_PUBLIC_API_URL=http://localhost:3006`
  - `NEXT_PUBLIC_WS_URL=http://localhost:3007`

### 2. Backend API Server (Port 3006)
- **Technology**: Express.js
- **Purpose**: REST API endpoints for all features
- **Environment Variables**:
  - `PORT=3006`
  - `WS_SERVER_URL=http://localhost:3007`
  - `NODE_ENV=production` or `development`
- **WebSocket Communication**: Uses HTTP client to emit events to WS server

### 3. WebSocket Server (Port 3007)
- **Technology**: Socket.IO on standalone HTTP server
- **Purpose**: Handles ALL real-time communications
- **Environment Variables**:
  - `WS_PORT=3007`
  - `NODE_ENV=production` or `development`
  - `VPS_IP=<your-vps-ip>` (only on VPS)

## WebSocket Namespaces

The WebSocket server organizes real-time features into namespaces:

### `/services` - Docker Services
- **Purpose**: Docker container logs and stats
- **Events**:
  - Client → Server: `subscribe:logs`, `unsubscribe:logs`
  - Server → Client: `logs`, `connected`, `error`, `stream:closed`

### `/deployments` - PM2 Deployments
- **Purpose**: PM2 process logs and management
- **Events**:
  - Client → Server: `subscribe:logs`, `unsubscribe:logs`
  - Server → Client: `logs`, `connected`, `error`, `stream:closed`

### `/system` - System Stats
- **Purpose**: Real-time system statistics
- **Events**:
  - Client → Server: `subscribe:stats`, `unsubscribe:stats`
  - Server → Client: `stats`, `connected`, `error`

### `/mcp` - MCP Servers
- **Purpose**: Model Context Protocol server events
- **Events**:
  - Client → Server: `join`, `leave`
  - Server → Client: `joined`, custom MCP events

### `/files` - File System
- **Purpose**: File system watch events
- **Events**:
  - Client → Server: `watch`
  - Server → Client: `change`, `connected`

## Usage

### Frontend (Components)

```typescript
import { servicesWS, deploymentsWS, systemWS } from '@/lib/ws-client'

// Subscribe to service logs
const cleanup = servicesWS.subscribeLogs(
  'service-id',
  'container-name',
  (data) => {
    console.log('Log:', data.data)
  }
)

// Cleanup when unmounting
cleanup()
```

### Backend (API Routes)

```javascript
const wsClient = require('./lib/ws-client')

// Emit to services namespace
await wsClient.emitToService('service-id', 'status', {
  status: 'running'
})

// Emit to deployments namespace
await wsClient.emitToDeployment('deployment-id', 'deployed', {
  version: '1.0.0'
})
```

## Environment Detection

The WebSocket server automatically detects the environment:

```javascript
const IS_MAC = process.platform === 'darwin'
const IS_VPS = NODE_ENV === 'production' && !IS_MAC
```

**Mac Development**:
- CORS origins: `localhost:3005`, `localhost:3006`
- No VPS-specific configurations

**VPS Production**:
- CORS origins: `localhost:3005`, `localhost:3006`, `http://<VPS_IP>`, `http://<VPS_IP>:80`, etc.
- Full production setup with PM2

## Deployment

### Development (Mac)

```bash
# Install dependencies
npm install
cd backend && npm install

# Start all services
./dev-start.sh

# Or manually with PM2
pm2 start ecosystem.config.js --env development
```

### Production (VPS)

```bash
# Fresh installation
./vps-install.sh

# Or manual update
cd /root/ai-desktop
git pull origin vps-install-fixes
npm install
cd backend && npm install
npm run build
pm2 restart all
```

## PM2 Management

```bash
# View all services
pm2 list

# View logs
pm2 logs                          # All services
pm2 logs ai-desktop-websocket    # WebSocket server only
pm2 logs ai-desktop-backend      # Backend only
pm2 logs ai-desktop-frontend     # Frontend only

# Restart services
pm2 restart all
pm2 restart ai-desktop-websocket

# Stop services
pm2 stop all
```

## Health Checks

### WebSocket Server
```bash
curl http://localhost:3007/health
```

Response:
```json
{
  "success": true,
  "status": "healthy",
  "connections": {
    "services": 2,
    "deployments": 1,
    "system": 1,
    "mcp": 0,
    "files": 0
  },
  "activeStreams": 3
}
```

### Backend API
```bash
curl http://localhost:3006/health
```

## Nginx Configuration (VPS)

```nginx
# Frontend
location / {
    proxy_pass http://localhost:3005;
    # ... headers
}

# Backend API
location /api/ {
    proxy_pass http://localhost:3006;
    # ... headers
}

# WebSocket Server
location /socket.io/ {
    proxy_pass http://localhost:3007;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    # ... other headers
}
```

## Benefits

1. **Separation of Concerns**: Each service has a single responsibility
2. **Scalability**: Services can be scaled independently
3. **Environment Flexibility**: Works seamlessly on Mac and VPS
4. **Better Error Handling**: Isolated error handling per service
5. **Easier Debugging**: Clear separation makes debugging simpler
6. **Independent Deployment**: Update one service without affecting others

## Troubleshooting

### WebSocket Connection Failed

1. Check WebSocket server is running:
   ```bash
   pm2 list | grep websocket
   ```

2. Check WebSocket server logs:
   ```bash
   pm2 logs ai-desktop-websocket
   ```

3. Verify environment variables:
   ```bash
   # Frontend
   echo $NEXT_PUBLIC_WS_URL

   # Backend
   echo $WS_SERVER_URL
   ```

### CORS Errors

1. Check VPS_IP is set correctly (VPS only):
   ```bash
   echo $VPS_IP
   ```

2. Verify WebSocket server CORS origins in logs:
   ```bash
   pm2 logs ai-desktop-websocket | grep "CORS Origins"
   ```

### Service Not Starting

1. Check PM2 status:
   ```bash
   pm2 status
   ```

2. Check for port conflicts:
   ```bash
   lsof -i :3007  # WebSocket
   lsof -i :3006  # Backend
   lsof -i :3005  # Frontend
   ```

3. Restart all services:
   ```bash
   pm2 restart all
   ```
