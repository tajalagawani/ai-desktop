# VS Code Editor Setup

This document explains the VS Code Editor integration with dynamic Nginx proxying.

## Architecture Overview

The VS Code Editor app allows you to open multiple GitHub repositories in separate VS Code instances, each accessible via a clean URL without visible ports.

### How It Works

```
User clones repo in GitHub Desktop
  ↓
Repository saved to /var/www/github/repo-name
  ↓
Added to centralized repository registry (data/repositories.json)
  ↓
Visible in File Manager at /var/www/github/repo-name
  ↓
VS Code Editor shows repo in dropdown
  ↓
User selects repo and clicks "Start VS Code"
  ↓
code-server starts on port 8888-8899 (automatic allocation)
  ↓
Nginx config generated: /vscode/repo-name/ → localhost:PORT
  ↓
Nginx reloaded automatically
  ↓
User accesses: http://92.112.181.127/vscode/repo-name/
  ↓
No port visible! ✅
```

## System Components

### 1. **Repository Registry** (`data/repositories.json`)
Centralized database tracking all repositories:
```json
{
  "repositories": [
    {
      "id": "ai-desktop",
      "name": "ai-desktop",
      "path": "/var/www/github/ai-desktop",
      "type": "git",
      "addedAt": "2025-01-17T10:30:00Z",
      "lastOpened": "2025-01-17T12:00:00Z",
      "vscodePort": 8888,
      "vscodeRunning": true
    }
  ]
}
```

### 2. **Port Manager** (`lib/vscode/port-manager.ts`)
- Allocates ports 8888-8899 (12 concurrent instances max)
- Tracks running code-server processes
- Automatically releases ports when instances stop

### 3. **Nginx Config Manager** (`lib/vscode/nginx-config.ts`)
- Generates Nginx location blocks dynamically
- Writes configs to `/etc/nginx/vscode-projects/`
- Tests and reloads Nginx safely

### 4. **Code-Server Manager** (`lib/vscode/code-server-manager.ts`)
- Starts code-server processes
- Syncs repositories to workspaces
- Manages process lifecycle

## File Structure

```
/var/www/
├── ai-desktop/                    # Next.js app
│   ├── data/
│   │   ├── repositories.json      # Centralized repository registry
│   │   └── vscode-ports.json      # Port allocation database
│   ├── lib/
│   │   ├── repositories/
│   │   │   ├── types.ts
│   │   │   └── registry.ts        # Repository manager
│   │   └── vscode/
│   │       ├── port-manager.ts    # Port allocation
│   │       ├── nginx-config.ts    # Nginx configuration
│   │       └── code-server-manager.ts  # Process management
│   └── app/api/
│       ├── repositories/          # Repository CRUD
│       └── code-server/
│           ├── start/             # Start VS Code instance
│           ├── stop/              # Stop VS Code instance
│           ├── list/              # List all instances
│           └── status/            # Get status
├── github/                        # GitHub repos cloned here
│   ├── ai-desktop/
│   ├── project-2/
│   └── project-3/
└── vscode-workspaces/             # Code-server workspaces
    ├── ai-desktop/
    ├── project-2/
    └── project-3/

/etc/nginx/
├── sites-available/
│   └── ai-desktop.conf            # Main Nginx config
└── vscode-projects/               # Dynamic VS Code configs
    ├── ai-desktop.conf
    ├── project-2.conf
    └── project-3.conf
```

## API Endpoints

### Repository Management

**GET /api/repositories**
```bash
# List all repositories
curl http://localhost/api/repositories
```

**POST /api/repositories** (action: add)
```bash
# Add repository
curl -X POST http://localhost/api/repositories \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add",
    "name": "my-project",
    "path": "/var/www/github/my-project",
    "type": "git"
  }'
```

**POST /api/repositories** (action: remove)
```bash
# Remove repository
curl -X POST http://localhost/api/repositories \
  -H "Content-Type: application/json" \
  -d '{
    "action": "remove",
    "path": "/var/www/github/my-project"
  }'
```

### Code-Server Management

**POST /api/code-server/start**
```bash
# Start VS Code for a repository
curl -X POST http://localhost/api/code-server/start \
  -H "Content-Type: application/json" \
  -d '{"repoId": "ai-desktop"}'

# Response:
# {
#   "success": true,
#   "url": "/vscode/ai-desktop/",
#   "fullUrl": "http://92.112.181.127/vscode/ai-desktop/",
#   "port": 8888,
#   "pid": 12345
# }
```

**POST /api/code-server/stop**
```bash
# Stop VS Code instance
curl -X POST http://localhost/api/code-server/stop \
  -H "Content-Type: application/json" \
  -d '{"repoId": "ai-desktop"}'
```

**GET /api/code-server/list**
```bash
# List all running instances
curl http://localhost/api/code-server/list

# Response:
# {
#   "instances": [
#     {
#       "projectName": "ai-desktop",
#       "port": 8888,
#       "pid": 12345,
#       "isRunning": true,
#       "url": "/vscode/ai-desktop/"
#     }
#   ],
#   "total": 1,
#   "running": 1,
#   "maxInstances": 12
# }
```

**GET /api/code-server/status**
```bash
# Get general status
curl http://localhost/api/code-server/status

# Get status for specific repository
curl "http://localhost/api/code-server/status?repoId=ai-desktop"
```

## Manual Operations

### Manually Start Code-Server
```bash
# Start code-server on specific port
code-server /var/www/github/ai-desktop \
  --bind-addr 127.0.0.1:8888 \
  --auth none \
  --disable-telemetry
```

### Manually Create Nginx Config
```bash
# Create config file
cat > /etc/nginx/vscode-projects/my-project.conf <<'EOF'
location /vscode/my-project/ {
    proxy_pass http://localhost:8888/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_cache_bypass $http_upgrade;
    proxy_set_header Host $host;
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
}
EOF

# Test and reload
nginx -t && systemctl reload nginx
```

### Check Running Instances
```bash
# List all code-server processes
ps aux | grep code-server

# Check which ports are in use
cat /var/www/ai-desktop/data/vscode-ports.json

# Check repository registry
cat /var/www/ai-desktop/data/repositories.json

# List Nginx configs
ls -la /etc/nginx/vscode-projects/
```

### Cleanup Stale Instances
```bash
# Kill all code-server processes
pkill -f code-server

# Remove all Nginx configs
rm -f /etc/nginx/vscode-projects/*.conf
nginx -t && systemctl reload nginx

# Reset port database
echo '{"instances":{},"availablePorts":[8888,8889,8890,8891,8892,8893,8894,8895,8896,8897,8898,8899]}' > /var/www/ai-desktop/data/vscode-ports.json
```

## Troubleshooting

### Issue: Port already in use
```bash
# Find process using port
lsof -i :8888

# Kill process
kill -9 <PID>
```

### Issue: Nginx reload fails
```bash
# Test configuration
nginx -t

# View Nginx error log
tail -f /var/log/nginx/error.log

# Check if config syntax is valid
cat /etc/nginx/vscode-projects/*.conf
```

### Issue: VS Code not accessible
```bash
# Check if code-server is running
ps aux | grep code-server

# Check if port is listening
nc -zv 127.0.0.1 8888

# Check Nginx config
cat /etc/nginx/vscode-projects/ai-desktop.conf

# Test URL directly
curl -I http://localhost:8888
```

### Issue: Repository not showing in VS Code Editor
```bash
# Check repository registry
cat /var/www/ai-desktop/data/repositories.json

# Add repository manually
curl -X POST http://localhost/api/repositories \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add",
    "name": "my-project",
    "path": "/var/www/github/my-project",
    "type": "git"
  }'
```

## Security Considerations

1. **code-server runs with `--auth none`** - Only accessible from localhost
2. **Nginx proxies on port 80** - No direct access to code-server ports
3. **Port range limited to 8888-8899** - Maximum 12 concurrent instances
4. **Workspaces isolated** - Each project in separate directory
5. **Nginx config validation** - Always tests before reload

## Limits and Quotas

- **Maximum concurrent instances**: 12 (ports 8888-8899)
- **Maximum file upload size**: 500MB (configurable in Nginx)
- **WebSocket timeout**: 24 hours
- **Request timeout**: 24 hours

## Performance Tips

1. Stop unused instances to free up ports
2. Keep workspaces clean (auto-synced from repos)
3. Monitor memory usage with System Monitor app
4. Use File Manager to clean up old repositories

## Integration with Other Apps

### GitHub Desktop
- Cloned repos automatically added to registry
- Deleted repos automatically removed from registry

### File Manager
- All repos visible at `/var/www/github/`
- Can browse workspace files at `/var/www/vscode-workspaces/`

### System Monitor
- Track code-server CPU/memory usage
- Monitor port allocation
- View running processes
