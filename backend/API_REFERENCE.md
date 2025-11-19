# AI Desktop Backend - API Reference

## Base URL

```
http://92.112.181.127/api
```

## Authentication

Currently, no authentication is required. Authentication middleware will be added in Phase 2.

---

## VS Code Manager API

### List Repositories

```http
GET /api/vscode/list
```

**Response:**
```json
{
  "success": true,
  "repositories": [
    {
      "id": "uuid",
      "name": "my-project",
      "path": "/path/to/repo",
      "type": "git",
      "port": 8080,
      "url": "https://github.com/user/repo",
      "branch": "main",
      "running": true,
      "pid": 12345,
      "created_at": "2025-11-19T00:00:00Z",
      "updated_at": "2025-11-19T00:00:00Z"
    }
  ]
}
```

### Get Status

```http
GET /api/vscode/status
```

Returns status of all code-server instances, repositories, deployments, and flows.

### Start Code Server

```http
POST /api/vscode/start
Content-Type: application/json

{
  "repoId": "uuid"
}
```

### Stop Code Server

```http
POST /api/vscode/stop
Content-Type: application/json

{
  "repoId": "uuid"
}
```

### Get Changes

```http
GET /api/vscode/changes/:repoId
```

Returns git changes for a repository.

### Get Diff

```http
POST /api/vscode/diff
Content-Type: application/json

{
  "repoId": "uuid",
  "file": "path/to/file.ts"
}
```

### Cleanup

```http
POST /api/vscode/cleanup
```

Cleans up stopped repositories.

---

## MCP Hub API

### List MCP Servers

```http
GET /api/mcp
```

**Response:**
```json
{
  "success": true,
  "servers": [
    {
      "id": "uuid",
      "name": "Example MCP",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-example"],
      "env": {},
      "status": "running",
      "pid": 12345,
      "workingDirectory": "/path/to/dir",
      "description": "Example MCP server",
      "createdAt": "2025-11-19T00:00:00Z",
      "updatedAt": "2025-11-19T00:00:00Z"
    }
  ],
  "count": 1
}
```

### Create MCP Server

```http
POST /api/mcp
Content-Type: application/json

{
  "id": "my-mcp",
  "name": "My MCP Server",
  "description": "Custom MCP server",
  "command": "node",
  "args": ["server.js"],
  "cwd": "/path/to/server",
  "env": {
    "API_KEY": "..."
  }
}
```

### Get MCP Server

```http
GET /api/mcp/:id
```

### Perform Action on MCP Server

```http
POST /api/mcp/:id/action
Content-Type: application/json

{
  "action": "start" | "stop" | "restart" | "delete"
}
```

### Get MCP Tools

```http
GET /api/mcp/:id/tools
```

Returns list of tools available on the MCP server.

### Execute MCP Tool

```http
POST /api/mcp/:id/execute
Content-Type: application/json

{
  "tool": "tool_name",
  "parameters": {
    "param1": "value1"
  }
}
```

---

## Service Manager API

### List Services

```http
GET /api/services
```

**Response:**
```json
{
  "success": true,
  "dockerInstalled": true,
  "services": [
    {
      "id": "uuid",
      "name": "PostgreSQL",
      "type": "docker",
      "status": "running",
      "port": 5432,
      "containerId": "ai-desktop-postgresql",
      "image": "postgres:15",
      "memory": 52428800,
      "cpu": 2.5,
      "uptime": 86400,
      "autoRestart": true,
      "createdAt": "2025-11-19T00:00:00Z",
      "updatedAt": "2025-11-19T00:00:00Z"
    }
  ],
  "count": 1
}
```

### Manage Service

```http
POST /api/services
Content-Type: application/json

{
  "serviceId": "postgresql",
  "action": "install" | "start" | "stop" | "restart" | "remove" | "logs"
}
```

**Actions:**
- `install`: Install and start Docker container
- `start`: Start stopped container
- `stop`: Stop running container
- `restart`: Restart container
- `remove`: Remove container, volumes, and images
- `logs`: Get container logs

---

## Flow Builder API

### List Sessions

```http
GET /api/flow-builder/sessions
```

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "id": "uuid",
      "status": "completed",
      "prompt": "Create a workflow for data processing",
      "output": "Generated workflow content...",
      "createdAt": "2025-11-19T00:00:00Z",
      "updatedAt": "2025-11-19T00:00:00Z"
    }
  ],
  "count": 1
}
```

### Create Session

```http
POST /api/flow-builder/sessions
Content-Type: application/json

{
  "prompt": "Create a workflow for data processing"
}
```

### Get Session

```http
GET /api/flow-builder/sessions/:id
```

### Delete Session

```http
DELETE /api/flow-builder/sessions/:id
```

### Get Settings

```http
GET /api/flow-builder/settings
```

**Response:**
```json
{
  "success": true,
  "settings": {
    "model": "claude-3-sonnet",
    "maxTokens": 4096,
    "temperature": 0.7
  }
}
```

### Update Settings

```http
POST /api/flow-builder/settings
Content-Type: application/json

{
  "model": "claude-3-sonnet",
  "maxTokens": 4096,
  "temperature": 0.7
}
```

---

## Deployments API

### List Deployments

```http
GET /api/deployments
```

**Response:**
```json
{
  "success": true,
  "deployments": [
    {
      "id": "uuid",
      "repositoryId": "uuid",
      "repositoryName": "my-app",
      "repositoryPath": "/path/to/repo",
      "name": "production",
      "domain": "example.com",
      "port": 3000,
      "status": "running",
      "mode": "cluster",
      "instances": 4,
      "pid": 12345,
      "memory": 104857600,
      "cpu": 5.2,
      "uptime": 172800,
      "createdAt": "2025-11-19T00:00:00Z",
      "updatedAt": "2025-11-19T00:00:00Z"
    }
  ],
  "count": 1
}
```

### Create Deployment

```http
POST /api/deployments
Content-Type: application/json

{
  "repositoryId": "uuid",
  "name": "production",
  "domain": "example.com",
  "port": 3000,
  "mode": "cluster",
  "instances": 4
}
```

### Perform Action on Deployment

```http
POST /api/deployments/:id/action
Content-Type: application/json

{
  "action": "start" | "stop" | "restart" | "delete"
}
```

### Get Deployment Services

```http
GET /api/deployments/services
```

Returns PM2 processes and Docker containers for deployments.

---

## WebSocket Events

### Connection

```javascript
const socket = io('http://92.112.181.127')

socket.on('connect', () => {
  console.log('Connected:', socket.id)
})
```

### Flow Builder Agent

```javascript
// Join agent room
socket.emit('agent:join', agentId)

// Listen for messages
socket.on(`agent:${agentId}:message`, (data) => {
  console.log('Agent output:', data)
})

// Leave room
socket.emit('agent:leave', agentId)
```

### MCP Server Logs

```javascript
// Join MCP room
socket.emit('mcp:join', serverId)

// Listen for logs
socket.on(`mcp:${serverId}:log`, (log) => {
  console.log('MCP log:', log)
})

// Leave room
socket.emit('mcp:leave', serverId)
```

### Service Status

```javascript
// Join service room
socket.emit('service:join', serviceId)

// Listen for status updates
socket.on(`service:${serviceId}:status`, (status) => {
  console.log('Service status:', status)
})

// Leave room
socket.emit('service:leave', serviceId)
```

### Deployment Logs

```javascript
// Join deployment room
socket.emit('deployment:join', deploymentId)

// Listen for logs
socket.on(`deployment:${deploymentId}:log`, (log) => {
  console.log('Deployment log:', log)
})

// Leave room
socket.emit('deployment:leave', deploymentId)
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

**HTTP Status Codes:**
- `200`: Success
- `400`: Bad request (validation error)
- `404`: Not found
- `500`: Internal server error

---

## Rate Limiting

Currently, no rate limiting is implemented. This will be added in Phase 3.

---

## CORS

CORS is enabled for:
- `http://92.112.181.127`
- `http://localhost:3001`

Additional origins can be configured in `.env`:
```env
CORS_ORIGINS=http://92.112.181.127,http://localhost:3001
```
