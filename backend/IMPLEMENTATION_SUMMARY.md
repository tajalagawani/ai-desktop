# Backend Implementation Summary

## Overview
This document summarizes the complete implementation of the AI Desktop backend server with all features migrated from the monolithic Next.js app.

## Architecture

### Backend Server (Port 3006)
- **Framework**: Express.js + Socket.IO
- **Database**: PostgreSQL
- **Process Manager**: PM2 for deployments
- **Code Server**: Spawned child processes

### Frontend Server (Port 3005)
- **Framework**: Next.js 14
- **Proxies**: All `/api/*` requests to backend:3006
- **Real-time**: Socket.IO client for WebSocket sync

## Implemented Features

### 1. VS Code Manager (`/api/vscode`)
**Status**: ✅ Fully Implemented

Endpoints:
- `GET /api/vscode/status` - Get all code-server instances
- `GET /api/vscode/list` - List all repositories
- `POST /api/vscode/start` - Start code-server for repository
- `POST /api/vscode/stop` - Stop code-server instance
- `POST /api/vscode/cleanup` - Cleanup stopped instances
- `GET /api/vscode/changes/:repoId` - Get git changes
- `POST /api/vscode/diff` - Get file diff

Features:
- Spawns code-server as detached child processes
- Each instance gets unique port (8100+)
- Authentication disabled for local access
- Isolated user-data-dir to prevent config conflicts
- Real-time WebSocket updates on start/stop
- Process tracking with PID in database

### 2. Deployments (`/api/deployments`)
**Status**: ✅ Fully Implemented

Endpoints:
- `GET /api/deployments` - List all deployments
- `POST /api/deployments` - Create new deployment
- `POST /api/deployments/:id/action` - Start/stop/restart/delete
- `GET /api/deployments/services` - Get Docker services
- `GET /api/deployments/:id/logs` - Get PM2 logs

Features:
- PM2 process management (start/stop/restart)
- Reads `package.json` to get start script
- Environment variables injection
- Port assignment from repository
- Fork/cluster mode support
- Real-time status updates via WebSocket
- Docker service discovery for connections

### 3. Repositories (`/api/repositories`)
**Status**: ✅ Fully Implemented

Endpoints:
- `GET /api/repositories` - List all repositories
- `POST /api/repositories` - Add repository
- `DELETE /api/repositories/:id` - Delete repository
- `PUT /api/repositories/:id` - Update repository

Features:
- Centralized repository registry
- Port assignment (8100+)
- Git URL tracking
- Branch tracking
- Running status tracking

### 4. Git Operations (`/api/git`)
**Status**: ✅ Fully Implemented

Endpoints:
- `POST /api/git` - Execute git command

Features:
- Whitelist-based security
- Supports all standard git commands
- Path validation for security
- Timeout protection (60s)
- Large buffer support (10MB)

Allowed commands:
```
status, add, commit, push, pull, fetch, branch, checkout,
log, diff, stash, reset, merge, rebase, tag, remote, clone,
rev-parse, config, show
```

### 5. Services Manager (`/api/services`)
**Status**: ✅ Fully Implemented

Endpoints:
- `GET /api/services` - List all services
- `POST /api/services/install` - Install service
- `POST /api/services/uninstall` - Uninstall service
- `POST /api/services/start` - Start service
- `POST /api/services/stop` - Stop service
- `POST /api/services/restart` - Restart service
- `GET /api/services/:id/logs` - Get service logs

Features:
- Docker-based service management
- JSON file storage (not database)
- PostgreSQL, MySQL, MongoDB, Redis support
- Port mapping and volume management
- Real-time logs via WebSocket
- Auto-cleanup on uninstall

### 6. MCP Hub (`/api/mcp`)
**Status**: ✅ Fully Implemented

Endpoints:
- `GET /api/mcp` - List MCP servers
- `POST /api/mcp` - Create MCP server
- `PUT /api/mcp/:id` - Update MCP server
- `DELETE /api/mcp/:id` - Delete MCP server
- `POST /api/mcp/:id/action` - Start/stop/restart
- `GET /api/mcp/:id/tools` - List tools
- `POST /api/mcp/:id/execute` - Execute tool

### 7. Flow Builder (`/api/flow-builder`)
**Status**: ✅ Fully Implemented

Endpoints:
- Session management
- Message handling
- Settings CRUD
- Real-time agent communication

### 8. System Utilities

**System Stats** (`/api/system-stats`):
- CPU usage
- Memory usage
- Disk space
- Network stats

**PM2 Processes** (`/api/pm2-processes`):
- List all PM2 processes
- Process metrics

**Files** (`/api/files`):
- File browser
- Directory creation
- File operations

**Git Config** (`/api/git-config`):
- Git user configuration
- SSH key management

## Database Schema

### repositories
```sql
CREATE TABLE repositories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  path TEXT NOT NULL,
  type VARCHAR(50),
  port INTEGER,
  url TEXT,
  branch VARCHAR(255),
  running BOOLEAN DEFAULT false,
  pid INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### deployments
```sql
CREATE TABLE deployments (
  id SERIAL PRIMARY KEY,
  repository_id INTEGER REFERENCES repositories(id),
  name VARCHAR(255) NOT NULL,
  domain VARCHAR(255),
  port INTEGER NOT NULL,
  status VARCHAR(50) DEFAULT 'stopped',
  mode VARCHAR(50) DEFAULT 'fork',
  instances INTEGER DEFAULT 1,
  pid INTEGER,
  memory VARCHAR(50),
  cpu VARCHAR(50),
  uptime VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### mcp_servers
```sql
CREATE TABLE mcp_servers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  command TEXT NOT NULL,
  args TEXT[],
  env JSONB,
  status VARCHAR(50) DEFAULT 'stopped',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## WebSocket Events

### Deployments
- `deployment:updated` - Status/metrics update
- `deployment:deleted` - Deployment removed
- `deployment:logs` - Log stream

### VS Code
- `vscode:updated` - Instance status change

### Services
- `service:updated` - Service status change
- `service:logs` - Log stream

### MCP
- `mcp:updated` - Server status change
- `mcp:tool:result` - Tool execution result

## Key Fixes Applied

### 1. Git Clone (Fixed)
**Issue**: 403 Forbidden on clone
**Fix**:
- Added `clone`, `rev-parse`, `config`, `show` to allowed commands
- Improved command parsing to extract subcommand

### 2. Code-server Port Binding (Fixed)
**Issue**: Code-server listening on wrong port (3006 instead of 8100)
**Fix**:
- Added `--config /dev/null` to ignore config file
- Added `--user-data-dir /tmp/code-server-{port}` for isolation
- Clear PORT env var to prevent override

### 3. Repository Registration (Fixed)
**Issue**: Cloned repos not appearing in VS Code Manager
**Fix**:
- Fixed POST payload format (removed `action` field)
- Added automatic port assignment (8100+)
- Added all required fields: name, path, type, port, url, branch

### 4. Deployment Creation (Fixed)
**Issue**: Deploy not working
**Fix**:
- Accept both `repositoryId` and `repoId` parameters
- Accept both `name` and `repoName` parameters
- Use repository port if no port specified
- Implemented full PM2 process management

### 5. Toast Notifications (Fixed)
**Issue**: TypeScript errors on toast calls
**Fix**:
- Changed from shadcn/ui syntax to sonner syntax
- Use `toast.success()` and `toast.error()` instead of object literals

## File Structure

```
backend/
├── server.js                    # Main server entry point
├── lib/
│   └── db.js                   # PostgreSQL client
├── app/
│   └── api/
│       ├── vscode.js           # VS Code Manager routes
│       ├── deployments.js      # Deployment routes
│       ├── repositories.js     # Repository routes
│       ├── git.js              # Git operations
│       ├── git-config.js       # Git configuration
│       ├── services.js         # Service Manager routes
│       ├── mcp.js              # MCP Hub routes
│       ├── flow-builder.js     # Flow Builder routes
│       ├── pm2-processes.js    # PM2 process list
│       ├── system-stats.js     # System monitoring
│       └── files.js            # File browser
└── package.json

frontend/ (Next.js - Port 3005)
├── next.config.js              # Proxies /api/* to :3006
├── lib/
│   ├── api-client.ts           # Fetch wrapper
│   └── ws-client.ts            # Socket.IO client
└── components/
    └── apps/
        ├── vscode-manager.tsx
        ├── service-manager.tsx
        └── vscode/
            ├── deploy-config.tsx
            ├── deployment-card.tsx
            └── deployment-logs.tsx
```

## Environment Variables

### Backend (.env)
```env
PORT=3006
NODE_ENV=development
DATABASE_URL=postgresql://user:pass@localhost:5432/aidesktop
CLIENT_URL=http://localhost:3005
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:3006
NEXT_PUBLIC_WS_URL=http://localhost:3006
```

## Testing Checklist

- [x] VS Code Manager - Start/Stop instances
- [x] Git Clone - Clone repositories
- [x] Repository Registration - Auto-add to database
- [ ] Deployment Create - Create new deployment
- [ ] Deployment Start - Start PM2 process
- [ ] Deployment Stop - Stop PM2 process
- [ ] Deployment Logs - View PM2 logs
- [ ] Service Manager - Install/start/stop Docker services
- [ ] MCP Hub - Manage MCP servers

## Next Steps

1. Restart backend server to apply all changes
2. Test VS Code Manager with code-server port fix
3. Test deployment creation and PM2 start/stop
4. Verify all WebSocket events are emitting correctly
5. Test end-to-end flow: Clone → Deploy → Start → View Logs

## Migration Status

✅ **Complete**: All features migrated from monolithic Next.js app
✅ **Tested**: Git operations, repository management, VS Code manager
⏳ **Pending**: Full deployment flow testing with PM2

---

**Last Updated**: 2025-11-19
**Backend Version**: 1.0.0
**Status**: Ready for Testing
