# VS Code Manager - Complete Implementation Plan

## 🎯 Goal
Create a VS Code Manager with the **EXACT same UI/UX as Service Manager**, where each cloned repository can have its own code-server instance, accessed through clean Nginx URLs.

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      VS Code Manager UI                          │
│  (Same layout as Service Manager - Left Panel + Right Panel)    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Next.js API Routes                             │
│  /api/vscode/list     - Get all repositories                    │
│  /api/vscode/start    - Start code-server for a repo            │
│  /api/vscode/stop     - Stop code-server                        │
│  /api/vscode/status   - Get status of all instances             │
│  /api/vscode/logs     - Get code-server logs (WebSocket)        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    code-server Processes                         │
│  actmcp          → localhost:8880 → /vscode/actmcp/             │
│  pytorch         → localhost:8881 → /vscode/pytorch/            │
│  transformers    → localhost:8882 → /vscode/transformers/       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         Nginx Proxy                              │
│  User accesses: http://92.112.181.127/vscode/actmcp/            │
│  Nginx proxies to: http://localhost:8880                        │
│  Clean URL - no ports visible!                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 UI Design (Exactly Like Service Manager)

### Left Panel (320px wide)
```
┌─────────────────────────────┐
│ VS Code Manager             │
│ Manage code editors         │
├─────────────────────────────┤
│                             │
│ 📊 Statistics               │
│   Total: 5                  │
│   Running: 2                │
│   Stopped: 3                │
│   Available: 0              │
│                             │
├─────────────────────────────┤
│                             │
│ 🔍 Search                   │
│   [Search repos...]         │
│                             │
├─────────────────────────────┤
│                             │
│ 📂 Categories               │
│   ● All (5)                 │
│   ● Git Repos (4)           │
│   ● Folders (1)             │
│                             │
├─────────────────────────────┤
│       [Refresh] [→]         │
└─────────────────────────────┘
```

### Right Panel (Main Content Area)

#### View 1: Repository List (Default)
```
┌──────────────────────────────────────────────────────────┐
│ Repositories                                              │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  📁 actmcp                         ● Running   [Stop]    │
│     /var/www/github/actmcp         Port: 8880           │
│     Git repository • main branch   [Open Editor]         │
│                                                           │
│  📁 pytorch-transformers           ○ Stopped   [Start]   │
│     /var/www/github/pytorch-transformers                │
│     Git repository • master branch                       │
│                                                           │
│  📁 my-project                     ○ Stopped   [Start]   │
│     /var/www/github/my-project                          │
│     Git repository • dev branch                          │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

#### View 2: Repository Detail (When clicked)
```
┌──────────────────────────────────────────────────────────┐
│ ← Back to repositories                                    │
│                                                           │
│  📁                                                       │
│     actmcp                      ● Running                │
│     Git Repository                                        │
│                                     [⏹] [↻] [🗑️]        │
├──────────────────────────────────────────────────────────┤
│ Tabs: [Overview] [Logs] [Settings]                       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ 🔗 Access Information                                    │
│    Editor URL:   /vscode/actmcp/      [Copy] [Open]     │
│    Port:         8880                  [Copy]            │
│    Path:         /var/www/github/actmcp [Copy]          │
│    Branch:       main                                    │
│    Status:       Running since 2min ago                  │
│                                                           │
│ 📝 Repository Info                                       │
│    Type:         Git Repository                          │
│    Added:        Nov 17, 2025                           │
│    Last Opened:  Today at 8:20 PM                       │
│                                                           │
│ ⚡ Quick Actions                                         │
│    [Open in New Window]                                  │
│    [Restart Code Server]                                 │
│    [View Repository Files]                               │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 📂 File Structure

```
app/api/vscode/
├── list/
│   └── route.ts          # GET - List all repositories with status
├── start/
│   └── route.ts          # POST - Start code-server for repo
├── stop/
│   └── route.ts          # POST - Stop code-server
├── status/
│   └── route.ts          # GET - Get status of all instances
└── logs/
    └── route.ts          # GET - Get logs (WebSocket support)

lib/vscode/
└── manager.ts            # VSCodeManager class - handles all logic

components/apps/
└── vscode-manager.tsx    # Main UI component (copy of service-manager style)

data/
└── vscode-config.ts      # Configuration constants
```

---

## 🔧 Implementation Details

### 1. Configuration (`lib/vscode/config.ts`)

```typescript
export const VSCODE_CONFIG = {
  PORT_RANGE_START: 8880,  // Start from 8880 (separate from services)
  PORT_RANGE_END: 8899,    // Allow 20 concurrent instances
  NGINX_CONFIG_DIR: '/etc/nginx/vscode-repos',
  BASE_URL_PATH: '/vscode',
}
```

### 2. VSCodeManager Class (`lib/vscode/manager.ts`)

**Core Methods:**
```typescript
class VSCodeManager {
  // Get all repos with their code-server status
  async getAllRepositories(): Promise<VSCodeRepository[]>

  // Find next available port by checking running processes
  private findAvailablePort(): number | null

  // Start code-server for a repository
  async startCodeServer(repoId: string): Promise<StartResult>

  // Stop code-server for a repository
  async stopCodeServer(repoId: string): Promise<void>

  // Get status of a specific repository
  async getRepositoryStatus(repoId: string): Promise<VSCodeStatus>

  // Get all running code-server processes from system
  async getRunningInstances(): Promise<RunningInstance[]>

  // Generate Nginx config for a repository
  private generateNginxConfig(repoId: string, port: number, repoPath: string): string

  // Write Nginx config file
  private writeNginxConfig(repoId: string, config: string): Promise<void>

  // Remove Nginx config file
  private removeNginxConfig(repoId: string): Promise<void>

  // Reload Nginx
  private reloadNginx(): Promise<void>
}
```

**How it Works:**
1. **No Database** - Everything is dynamic by checking:
   - Repository list from RepositoryManager
   - Running processes from `ps aux | grep code-server`
   - Port allocation by checking which ports are in use

2. **Port Allocation:**
   ```typescript
   findAvailablePort() {
     const running = this.getRunningInstances()
     const usedPorts = running.map(i => i.port)

     for (let port = 8880; port <= 8899; port++) {
       if (!usedPorts.includes(port)) {
         return port
       }
     }
     return null // All ports in use
   }
   ```

3. **Starting Code Server:**
   ```typescript
   async startCodeServer(repoId: string) {
     // 1. Get repository info
     const repo = await repoManager.getRepository(repoId)

     // 2. Check if already running
     const existing = await this.getRepositoryStatus(repoId)
     if (existing.running) {
       return { success: true, url: `/vscode/${repoId}/`, port: existing.port }
     }

     // 3. Find available port
     const port = this.findAvailablePort()
     if (!port) throw new Error('No available ports')

     // 4. Start code-server process
     const process = spawn('code-server', [
       repo.path,
       '--bind-addr', `127.0.0.1:${port}`,
       '--auth', 'none',
       '--disable-telemetry',
     ], {
       detached: true,
       stdio: 'ignore'
     })

     process.unref()

     // 5. Generate Nginx config
     const config = this.generateNginxConfig(repoId, port, repo.path)
     await this.writeNginxConfig(repoId, config)

     // 6. Reload Nginx
     await this.reloadNginx()

     // 7. Wait for port to open
     await this.waitForPort(port, 30000)

     return {
       success: true,
       url: `/vscode/${repoId}/`,
       port,
       pid: process.pid
     }
   }
   ```

4. **Nginx Config Generation:**
   ```nginx
   # Auto-generated for repository: actmcp
   # Port: 8880
   # Path: /var/www/github/actmcp

   location /vscode/actmcp/ {
       proxy_pass http://127.0.0.1:8880/;
       proxy_http_version 1.1;

       # WebSocket support (CRITICAL for VS Code)
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection 'upgrade';
       proxy_cache_bypass $http_upgrade;

       # Headers
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;

       # Timeouts
       proxy_read_timeout 86400s;
       proxy_send_timeout 86400s;

       # File uploads
       client_max_body_size 500M;
   }
   ```

---

## 🌐 Nginx Setup

### Main Nginx Config (`/etc/nginx/nginx.conf`)

Add this line to include all VS Code configs:
```nginx
http {
    # ... other config ...

    # Include VS Code repository configs
    include /etc/nginx/vscode-repos/*.conf;
}
```

### Auto-Generated Configs
Each repository gets its own config file:
```
/etc/nginx/vscode-repos/
├── actmcp.conf
├── pytorch-transformers.conf
└── my-project.conf
```

---

## 📡 API Routes

### GET `/api/vscode/list`
**Purpose:** Get all repositories with their code-server status

**Response:**
```json
{
  "repositories": [
    {
      "id": "actmcp",
      "name": "actmcp",
      "path": "/var/www/github/actmcp",
      "type": "git",
      "branch": "main",
      "running": true,
      "port": 8880,
      "pid": 12345,
      "url": "/vscode/actmcp/",
      "uptime": "2m 30s",
      "addedAt": "2025-11-17T20:00:00Z"
    },
    {
      "id": "pytorch-transformers",
      "name": "pytorch-transformers",
      "path": "/var/www/github/pytorch-transformers",
      "type": "git",
      "branch": "master",
      "running": false,
      "port": null,
      "pid": null,
      "url": null,
      "uptime": null,
      "addedAt": "2025-11-16T15:30:00Z"
    }
  ]
}
```

### POST `/api/vscode/start`
**Purpose:** Start code-server for a repository

**Request:**
```json
{
  "repoId": "actmcp"
}
```

**Response:**
```json
{
  "success": true,
  "url": "/vscode/actmcp/",
  "port": 8880,
  "pid": 12345,
  "message": "Code server started successfully"
}
```

### POST `/api/vscode/stop`
**Purpose:** Stop code-server

**Request:**
```json
{
  "repoId": "actmcp"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Code server stopped successfully"
}
```

### GET `/api/vscode/status`
**Purpose:** Get real-time status of all instances

**Response:**
```json
{
  "instances": [
    {
      "repoId": "actmcp",
      "pid": 12345,
      "port": 8880,
      "cpu": "2.5",
      "memory": "145MB",
      "uptime": "2m 30s"
    }
  ],
  "totalRunning": 1,
  "availablePorts": 19
}
```

---

## 🎯 Key Features

### 1. **No Database - Pure Process Detection**
- Check running processes: `ps aux | grep code-server`
- Extract port from command line arguments
- Match process to repository by path

### 2. **Clean URLs**
- User sees: `http://92.112.181.127/vscode/actmcp/`
- No ports visible!
- Nginx handles routing internally

### 3. **Automatic Nginx Management**
- Generate config when starting code-server
- Remove config when stopping
- Auto-reload Nginx after changes

### 4. **Real-time Status**
- Auto-refresh every 5 seconds (silent, no flashing)
- Show CPU/memory usage
- Show uptime
- Show if code-server is responding

### 5. **WebSocket Support**
- Live logs streaming
- Real-time file watching
- Terminal support in VS Code

---

## 📋 Implementation Steps

### Phase 1: Backend Foundation
1. ✅ Create `lib/vscode/config.ts` with constants
2. ✅ Create `lib/vscode/manager.ts` with VSCodeManager class
3. ✅ Implement process detection (findRunningInstances)
4. ✅ Implement port allocation (findAvailablePort)
5. ✅ Implement Nginx config generation

### Phase 2: API Routes
6. ✅ Create `/api/vscode/list/route.ts`
7. ✅ Create `/api/vscode/start/route.ts`
8. ✅ Create `/api/vscode/stop/route.ts`
9. ✅ Create `/api/vscode/status/route.ts`
10. ✅ Create `/api/vscode/logs/route.ts` (WebSocket)

### Phase 3: UI Components
11. ✅ Create `components/apps/vscode-manager.tsx`
12. ✅ Copy Service Manager layout (left panel + right panel)
13. ✅ Add repository list view
14. ✅ Add repository detail view with tabs
15. ✅ Add real-time status updates
16. ✅ Add action buttons (Start/Stop/Restart/Delete)

### Phase 4: Desktop Integration
17. ✅ Add VS Code Manager to desktop apps
18. ✅ Add window configuration
19. ✅ Add icon mapping

### Phase 5: VPS Deployment
20. ✅ Create Nginx config directory: `/etc/nginx/vscode-repos/`
21. ✅ Update main Nginx config to include VS Code configs
22. ✅ Set proper permissions for config directory
23. ✅ Test Nginx reload

### Phase 6: Testing
24. ✅ Test starting single instance
25. ✅ Test starting multiple instances
26. ✅ Test stopping instances
27. ✅ Test Nginx routing works
28. ✅ Test WebSocket connections
29. ✅ Test logs streaming
30. ✅ Test cleanup on restart

---

## 🔒 Security Considerations

1. **No Authentication** (for now)
   - code-server runs with `--auth none`
   - Only accessible from server's IP
   - Could add basic auth later via Nginx

2. **Process Isolation**
   - Each code-server runs as same user
   - Each has separate workspace
   - No shared extensions or settings

3. **Resource Limits**
   - Max 20 concurrent instances (ports 8880-8899)
   - Could add CPU/memory limits via systemd

---

## 🚀 Success Criteria

✅ **UI matches Service Manager exactly**
✅ **All cloned repos visible in list**
✅ **Can start/stop multiple instances**
✅ **Clean URLs without ports**
✅ **Real-time status updates**
✅ **WebSocket/logs working**
✅ **Nginx auto-configured**
✅ **No database required**
✅ **Survives server restart** (processes persist)

---

## 📝 Next Steps

After reviewing this plan, we'll implement in order:
1. Backend (lib + API routes)
2. UI (VSCodeManager component)
3. Integration (desktop apps)
4. VPS setup (Nginx)
5. Testing

**Ready to start?** Let me know and I'll begin with Phase 1!
