# AI Desktop Backend

Lightweight Express + Socket.IO backend server with JSON file storage.

## Features

✅ **No Database Required** - Uses lightweight JSON file storage
✅ **Real-time Updates** - Socket.IO for live WebSocket connections
✅ **REST API** - Clean API endpoints for all operations
✅ **Process Management** - PM2 for deployments, code-server for VS Code
✅ **Docker Integration** - Service manager for Docker containers
✅ **MCP Support** - Model Context Protocol server management

## Quick Start

### Development (Mac)

```bash
# 1. Run setup script
./setup.sh

# 2. Start development server
npm run dev

# 3. Test
curl http://localhost:3006/health
```

### Production (VPS)

```bash
# 1. Run setup script
./setup.sh

# 2. Start with PM2
npm run pm2:start

# 3. Test
curl http://localhost:3000/health
```

## Storage

All data is stored in JSON files in the `data/` directory:

- `data/repositories.json` - VS Code repositories and instances
- `data/deployments.json` - PM2 deployment configurations
- `data/flow-sessions.json` - Flow Builder AI sessions
- `data/mcp-servers.json` - MCP server configurations

## Environment Variables

Create a `.env` file (or run `./setup.sh`):

```env
# Server
PORT=3006                      # Mac: 3006, VPS: 3000
NODE_ENV=development           # or production

# Client URL
CLIENT_URL=http://localhost:3005

# CORS
CORS_ORIGINS=http://localhost:3005,http://localhost:3001
```

## API Endpoints

### Health & Status
- `GET /health` - Server health check
- `GET /api` - API information
- `GET /api/status` - Server status

### Repositories
- `GET /api/repositories` - List all repositories
- `POST /api/repositories` - Create repository
- `PUT /api/repositories` - Update repository
- `DELETE /api/repositories` - Delete repository

### VS Code Manager
- `GET /api/vscode/status` - Get all instances
- `GET /api/vscode/list` - List repositories
- `POST /api/vscode/start` - Start code-server
- `POST /api/vscode/stop` - Stop code-server

### Deployments
- `GET /api/deployments` - List deployments
- `POST /api/deployments` - Create deployment
- `POST /api/deployments/:id/action` - Start/stop/restart/delete
- `GET /api/deployments/:id/logs` - View PM2 logs
- `GET /api/deployments/services` - List Docker services

### MCP Hub
- `GET /api/mcp` - List MCP servers
- `POST /api/mcp/:id/action` - Start/stop/restart/delete MCP server
- `GET /api/mcp/:id/tools` - List available tools
- `POST /api/mcp/:id/execute` - Execute tool

### Flow Builder
- `GET /api/flow-builder/sessions` - List sessions
- `POST /api/flow-builder/sessions` - Create session
- `GET /api/flow-builder/sessions/:id` - Get session
- `PATCH /api/flow-builder/sessions/:id` - Update session
- `DELETE /api/flow-builder/sessions/:id` - Delete session
- `GET /api/flow-builder/messages` - List messages
- `POST /api/flow-builder/messages` - Create message

### Services Manager
- `GET /api/services` - List Docker services
- `POST /api/services/install` - Install service (PostgreSQL, MySQL, etc.)
- `POST /api/services/uninstall` - Uninstall service
- `POST /api/services/start` - Start service
- `POST /api/services/stop` - Stop service

### Git Operations
- `POST /api/git` - Execute git command
- `GET /api/git-config` - Get git config
- `POST /api/git-config` - Set git config

### System
- `GET /api/system-stats` - CPU, memory, disk usage
- `GET /api/pm2-processes` - List all PM2 processes
- `GET /api/files` - File browser

## WebSocket Events

The server emits real-time events via Socket.IO:

### Deployments
- `deployment:updated` - Deployment status changed
- `deployment:deleted` - Deployment removed

### VS Code
- `vscode:updated` - Code-server instance status changed

### Services
- `service:updated` - Docker service status changed

### MCP
- `mcp:updated` - MCP server status changed
- `mcp:deleted` - MCP server removed
- `mcp:{id}:log` - Real-time MCP server logs

### Flow Builder
- `agent:{sessionId}:message` - New message in session

## Backup & Restore

### Backup
```bash
# Backup all data
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Or copy to another location
cp -r data/ /path/to/backup/
```

### Restore
```bash
# Restore from tar
tar -xzf backup-20251119.tar.gz

# Or copy back
cp -r /path/to/backup/data/ .
```

## Scripts

```bash
# Development
npm run dev          # Start with nodemon (auto-reload)
npm start           # Start without auto-reload

# Production (PM2)
npm run pm2:start    # Start with PM2
npm run pm2:stop     # Stop PM2 process
npm run pm2:restart  # Restart PM2 process
npm run pm2:delete   # Delete PM2 process
npm run pm2:logs     # View logs
npm run pm2:monit    # Monitor processes
```

## Architecture

```
Backend (Port 3006 on Mac, 3000 on VPS)
├── Express Server
│   ├── REST API endpoints
│   ├── CORS middleware
│   └── Error handling
├── Socket.IO Server
│   ├── Real-time events
│   ├── Room-based broadcasting
│   └── Connection management
└── JSON Storage
    ├── Read/write operations
    ├── Auto-directory creation
    └── Pretty-printed JSON
```

## Dependencies

### Production
- `express` - Web framework
- `socket.io` - WebSocket library
- `cors` - CORS middleware
- `dotenv` - Environment variables
- `uuid` - Unique ID generation

### Development
- `nodemon` - Auto-reload on changes

## Migration from PostgreSQL

This backend previously used PostgreSQL but has been converted to lightweight JSON file storage. See `POSTGRESQL_REMOVED.md` for details.

If you have existing data in PostgreSQL:
1. Export data to CSV
2. Convert to JSON format
3. Place in `data/` directory

## Troubleshooting

### Port already in use
```bash
# Find process using port
lsof -i :3006

# Kill the process
kill -9 <PID>
```

### Permission errors on data directory
```bash
# Fix permissions
chmod 755 data/
chown -R $USER:$USER data/
```

### PM2 not starting
```bash
# Check PM2 status
pm2 status

# View logs
pm2 logs ai-desktop-backend

# Restart PM2
pm2 restart ai-desktop-backend
```

## Development Tips

### Hot Reload
Use `npm run dev` for automatic server restart on file changes.

### Debug Logging
Set `LOG_LEVEL=debug` in `.env` for detailed logs.

### Testing API
```bash
# Health check
curl http://localhost:3006/health

# Create repository
curl -X POST http://localhost:3006/api/repositories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "path": "/path/to/project",
    "type": "git",
    "port": 8100
  }'

# List repositories
curl http://localhost:3006/api/repositories
```

## License

MIT
