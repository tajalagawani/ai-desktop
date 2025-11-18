# Deployment System Documentation

Last Updated: 2025-11-18

## Overview

The AI Desktop Deployment System provides a complete solution for deploying web applications directly from cloned Git repositories to your VPS. It features automatic framework detection, service integration, PM2 process management, real-time logs, and automatic firewall configuration.

## Architecture

### Components

1. **Framework Detector** (`/lib/deployment/detector.ts`)
   - Auto-detects 17+ framework types
   - Analyzes package.json, requirements.txt, composer.json
   - Determines build commands, start commands, and default ports

2. **Service Integration** (`/lib/deployment/services.ts`)
   - Discovers running Docker services from Service Manager
   - Generates connection strings for databases
   - Auto-injects environment variables

3. **Deployment API** (`/app/api/deployments/route.ts`)
   - Creates and manages deployments
   - Handles async build process
   - Updates deployment status in real-time

4. **Deployment Actions** (`/app/api/deployments/[id]/action/route.ts`)
   - Start/Stop/Restart deployments
   - Delete deployments with cleanup
   - Manages PM2 processes

5. **WebSocket Log Streaming** (`/server.js`)
   - Real-time build logs
   - Real-time runtime logs
   - Supports both fork and cluster mode

6. **UI Components**
   - DeployConfig: Inline deployment configuration
   - DeploymentCard: Deployment status and controls
   - DeploymentLogs: Real-time log viewer
   - VS Code Manager: Integrated tabbed interface

## Supported Frameworks

### JavaScript/Node.js
- **Next.js** - Full-stack React framework
- **Nuxt.js** - Vue.js framework
- **React (Vite)** - React with Vite bundler
- **React (CRA)** - Create React App
- **Vue.js** - Progressive JavaScript framework
- **Angular** - TypeScript-based framework
- **Svelte** - Compiler-based framework
- **Astro** - Static site generator
- **NestJS** - Progressive Node.js framework
- **Express** - Minimal Node.js framework
- **Node.js** - Generic Node.js application

### Python
- **Django** - High-level Python web framework
- **Flask** - Lightweight WSGI framework
- **FastAPI** - Modern API framework

### PHP
- **Laravel** - PHP web application framework
- **Symfony** - PHP framework and components
- **Generic PHP** - Standard PHP applications

### Other
- **Static Sites** - HTML/CSS/JS static websites

## Data Storage

### Deployment Registry
**Location**: `/var/www/ai-desktop/data/deployments.json`

**Structure**:
```json
{
  "deployments": [
    {
      "id": "delange-1763425794591",
      "repoId": "delange",
      "repoName": "delange",
      "repoPath": "/var/www/github/delange",
      "framework": "nextjs",
      "buildCommand": "npm run build",
      "startCommand": "npm start",
      "port": 3059,
      "domain": null,
      "services": ["ai-desktop-mysql"],
      "envVars": {
        "PORT": "3059",
        "NODE_ENV": "production",
        "DATABASE_URL": "mysql://root:password@localhost:3306/"
      },
      "status": "running",
      "pm2Name": "deployment-delange-1763425794591",
      "deployedAt": "2025-11-18T00:15:00.667Z",
      "lastDeployedAt": "2025-11-18T00:15:49.317Z",
      "buildLogs": "/var/www/ai-desktop/logs/delange-1763425794591.log"
    }
  ]
}
```

### Repository Registry
**Location**: `/var/www/ai-desktop/data/repositories.json`

Links deployments to cloned repositories from GitHub Desktop.

### Log Files
**Location**: `/var/www/ai-desktop/logs/`

**Types**:
- `{deploymentId}.log` - Build logs
- `{deploymentId}-out.log` - Runtime stdout (fork mode)
- `{deploymentId}-out-N.log` - Runtime stdout (cluster mode)
- `{deploymentId}-error.log` - Runtime stderr

## Deployment Flow

### 1. User Initiates Deployment

User navigates to VS Code Manager → Repository → Deploy tab and:
1. Selects running services (MySQL, PostgreSQL, Redis, etc.)
2. Adds custom environment variables
3. Optionally specifies custom domain
4. Clicks "Deploy to VPS"

### 2. Framework Detection

System analyzes repository structure:

```typescript
// Check package.json
if (deps.next) → Next.js
if (deps.nuxt) → Nuxt.js
if (deps.vite && deps.react) → React (Vite)
if (deps['react-scripts']) → Create React App
// ... etc

// Check requirements.txt
if (manage.py exists) → Django
if (flask import in app.py) → Flask
if (fastapi import in main.py) → FastAPI

// Check composer.json
if (laravel/framework) → Laravel
if (symfony/framework-bundle) → Symfony
```

### 3. Service Discovery

System finds running Docker containers:

```bash
docker ps --filter "label=ai-desktop-service=true"
```

Generates connection strings:
- MySQL: `mysql://root:password@localhost:3306/`
- PostgreSQL: `postgresql://postgres:password@localhost:5432/postgres`
- MongoDB: `mongodb://localhost:27017`
- Redis: `redis://localhost:6379`

### 4. Port Allocation

Assigns available port from range **3050-3999**:
- Checks existing deployments
- Finds first available port
- Adds to deployment config

### 5. Build Process (Async)

Executed in background with real-time logging:

```bash
# 1. Install dependencies
npm install

# 2. Build application (if needed)
npm run build

# 3. Create .env.production
# Writes all environment variables

# 4. Create PM2 ecosystem config
# ecosystem.{deploymentId}.config.js

# 5. Start with PM2
pm2 start ecosystem.{deploymentId}.config.js

# 6. Save PM2 config
pm2 save

# 7. Open firewall port
ufw allow {port}/tcp
```

### 6. PM2 Process Management

**Ecosystem Config**:
```javascript
module.exports = {
  apps: [{
    name: "deployment-delange-1763425794591",
    script: "npm",
    args: "start",
    cwd: "/var/www/github/delange",
    env: {
      PORT: "3059",
      NODE_ENV: "production",
      DATABASE_URL: "mysql://root:password@localhost:3306/"
    },
    exec_mode: "fork", // Prevents log file suffix
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: "1G",
    error_file: "/var/www/ai-desktop/logs/delange-1763425794591-error.log",
    out_file: "/var/www/ai-desktop/logs/delange-1763425794591-out.log"
  }]
}
```

### 7. Firewall Configuration

Automatically opens port in UFW firewall:

```bash
# On deploy
ufw allow 3059/tcp

# On delete
ufw delete allow 3059/tcp
```

### 8. Status Updates

Deployment status tracked through lifecycle:
- `building` - Installing dependencies and building
- `running` - Application is live
- `stopped` - Application stopped by user
- `failed` - Build or runtime error

## User Interface

### VS Code Manager Integration

**Location**: Components → Apps → VS Code Manager

**Tabs Structure**:
1. **Overview Tab**
   - Connection information (when code-server running)
   - Repository information
   - Path, type, branch, added date

2. **Deploy Tab**
   - **Active Deployments** section (top)
     - Shows existing deployments for current repo
     - Deployment cards with status, URL, controls
   - **New Deployment** section (bottom)
     - Service selection checkboxes
     - Environment variable management
     - Custom domain input
     - Deploy button

3. **Changes Tab** (Git repos only)
   - Live git changes
   - File diff viewer

**Sidebar Categories**:
- Repositories
- **Deployments** (all deployments across all repos)

### Deployment Card Features

Each deployment card displays:

**Header**:
- Repository name
- Status badge (Running/Stopped/Building/Failed)
- Framework type
- Port number
- Connected services count

**Deployment URL Box** (prominent):
- Label: "Deployment URL"
- Clickable link with external icon
- Copy to clipboard button
- Format: `http://92.112.181.127:3059` or custom domain

**Action Buttons**:
- 🔗 **Open** - Opens deployment in new browser tab
- ⏹️ **Stop** - Stops PM2 process
- 🔄 **Restart** - Restarts PM2 process
- 🗑️ **Delete** - Removes deployment and cleans up

**Logs**:
- **Build Logs** - Shows npm install, build output
- **Runtime Logs** - Shows application stdout (real-time WebSocket)

### Deployment Configuration

**Service Integration**:
```
┌─────────────────────────────────────┐
│ Connect to Services                  │
├─────────────────────────────────────┤
│ ☑ MySQL 8.0                         │
│   mysql://root:***@localhost:3306/  │
│                                      │
│ ☐ PostgreSQL 16                     │
│   postgresql://postgres:***@local...│
│                                      │
│ ☑ Redis 7                           │
│   redis://localhost:6379             │
└─────────────────────────────────────┘
```

**Environment Variables**:
```
┌─────────────────────────────────────┐
│ Environment Variables                │
├─────────────────────────────────────┤
│ API_KEY=sk-1234567890              │
│ NEXT_PUBLIC_URL=https://...        │
│                                     │
│ [KEY]  [value]  [Add]              │
└─────────────────────────────────────┘
```

**Custom Domain** (Optional):
```
┌─────────────────────────────────────┐
│ Custom Domain (Optional)             │
├─────────────────────────────────────┤
│ example.com                         │
│ Leave empty to use default port access
└─────────────────────────────────────┘
```

## LocalStorage Persistence

Configuration saved per repository to prevent data loss when switching tabs:

**Storage Key**: `deploy-config-{repoId}`

**Saved Data**:
- Selected services
- Environment variables
- Custom domain
- Custom port
- Build/start commands
- Instance count
- Memory limit
- Auto-restart setting
- Node environment

**Behavior**:
- Auto-saves on every change
- Auto-loads when opening Deploy tab
- Persists after deployment (no reset)

## Real-time Log Streaming

### WebSocket Implementation

**Endpoint**: `ws://host/api/deployments/logs/ws`

**Query Parameters**:
- `deploymentId` - Deployment ID
- `type` - `build` or `runtime`

**Message Format**:
```json
{
  "type": "log",
  "data": "Installing dependencies...\n"
}
```

**Features**:
- Streams existing content first
- Tails file in real-time using `Tail` library
- Auto-reconnect on connection loss
- Handles both fork and cluster mode log files

**Log File Detection**:
```javascript
// Try fork mode first
if exists: /logs/{deploymentId}-out.log
  → use it
else
  // Search for cluster mode
  find: /logs/{deploymentId}-out-*.log
  → use first match
```

## API Endpoints

### GET /api/deployments
Lists all deployments with PM2 status updates.

**Response**:
```json
{
  "success": true,
  "deployments": [...]
}
```

### POST /api/deployments
Creates new deployment.

**Request**:
```json
{
  "repoId": "delange",
  "repoName": "delange",
  "repoPath": "/var/www/github/delange",
  "selectedServices": ["ai-desktop-mysql"],
  "customEnvVars": {
    "API_KEY": "..."
  },
  "domain": "example.com"
}
```

**Response**:
```json
{
  "success": true,
  "deployment": {...},
  "message": "Deployment started"
}
```

### POST /api/deployments/[id]/action
Performs action on deployment.

**Request**:
```json
{
  "action": "start" | "stop" | "restart" | "delete"
}
```

**Actions**:
- `start` - Starts stopped deployment
- `stop` - Stops running deployment
- `restart` - Restarts deployment
- `delete` - Removes deployment, stops PM2, closes firewall port

### GET /api/deployments/services
Lists running Docker services available for connection.

**Response**:
```json
{
  "success": true,
  "services": [
    {
      "id": "mysql",
      "name": "MySQL 8.0",
      "containerName": "ai-desktop-mysql",
      "port": 3306,
      "type": "database",
      "connectionString": "mysql://root:password@localhost:3306/"
    }
  ]
}
```

## Error Handling

### Build Failures

When build fails:
1. Status set to `failed`
2. Error message stored in deployment config
3. Build logs show full error output
4. PM2 process not started

**User Actions**:
- View build logs to diagnose
- Fix code in repository
- Delete failed deployment
- Deploy again

### Runtime Failures

When application crashes:
1. PM2 auto-restarts (if enabled)
2. Error logged to error log file
3. Status updates to `stopped` if can't restart

### Missing Log Files

WebSocket handles gracefully:
- Shows "Waiting for logs..." message
- Continues attempting to tail file
- Works for both cluster and fork mode

## Advanced Features

### Custom Commands

Users can override auto-detected commands:
- Custom build command
- Custom start command
- Custom port

### PM2 Configuration

Configurable options:
- Instance count (cluster mode)
- Memory limit (max_memory_restart)
- Auto-restart on crash
- Node environment (production/development)

### Multiple Deployments

Same repository can have multiple deployments:
- Different ports
- Different service configurations
- Different environment variables

Each shows in Deploy tab for easy management.

## File Structure

```
/var/www/ai-desktop/
├── data/
│   ├── deployments.json       # Deployment registry
│   └── repositories.json      # Repository registry
├── logs/
│   ├── {id}.log              # Build logs
│   ├── {id}-out.log          # Runtime logs (fork)
│   ├── {id}-out-N.log        # Runtime logs (cluster)
│   └── {id}-error.log        # Error logs
└── app/
    └── api/
        └── deployments/
            ├── route.ts              # List/Create
            ├── [id]/action/route.ts  # Actions
            └── services/route.ts     # Service list

/var/www/github/
└── {repo-name}/
    ├── ecosystem.{id}.config.js  # PM2 config
    └── .env.production           # Environment variables
```

## Security Considerations

### Firewall Management
- Automatically opens only required ports
- Closes ports when deployment deleted
- Uses UFW for security

### Environment Variables
- Stored in .env.production (not committed)
- Injected via PM2 ecosystem config
- Saved in deployments.json (server-side only)

### Service Access
- Services bound to localhost only
- Connection via localhost for security
- No external exposure of database ports

## Troubleshooting

### Deployment Stuck in "Building"
1. Check build logs for errors
2. Verify repository has required files
3. Check disk space on VPS
4. Restart deployment system

### Port Already in Use
- System auto-assigns from range 3050-3999
- If range exhausted, delete unused deployments

### Runtime Logs Not Showing
- System auto-detects fork/cluster mode
- Check /var/www/ai-desktop/logs/ for file existence
- Refresh browser to reconnect WebSocket

### Service Not Connecting
- Verify service is running in Service Manager
- Check service port matches deployment env vars
- Verify Docker container has ai-desktop-service=true label

## Best Practices

1. **Use Environment Variables** for sensitive data (API keys, secrets)
2. **Delete Unused Deployments** to free ports and resources
3. **Monitor Logs** during first deployment to catch issues early
4. **Test Locally** before deploying to VPS
5. **Use Meaningful Env Var Names** for clarity

## Maintenance

### Viewing All Deployments
```bash
pm2 list
```

### Checking Deployment Logs
```bash
tail -f /var/www/ai-desktop/logs/{deploymentId}-out.log
```

### Manually Stopping Deployment
```bash
pm2 stop deployment-{id}
pm2 delete deployment-{id}
pm2 save
```

### Clearing Failed Deployments
```bash
pm2 delete all
pm2 save
# Then use UI to remove from deployments.json
```

## Future Enhancements

Potential improvements:
- [ ] NGINX reverse proxy integration
- [ ] SSL certificate auto-provisioning
- [ ] Custom domain DNS management
- [ ] Deployment rollback capability
- [ ] Resource usage monitoring
- [ ] Auto-scaling based on load
- [ ] Deployment templates
- [ ] CI/CD webhook integration

## Support

For issues or questions:
- Check build logs first
- Review this documentation
- Check GitHub issues: https://github.com/anthropics/claude-code/issues
