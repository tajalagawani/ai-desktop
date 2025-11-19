# AI Desktop - Lightweight Client Architecture

## Overview

This is the **lightweight client migration** of AI Desktop, separating the application into:

- **Client** (<5MB): Static Next.js frontend that runs in the browser
- **Backend**: Express + Socket.IO API server running on VPS (92.112.181.127)
- **Shared**: Common TypeScript types used by both client and backend

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User's Browser                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Lightweight Client (<5MB)                     │  │
│  │  - Static HTML/CSS/JS                                 │  │
│  │  - React Components                                   │  │
│  │  - API Client (apiClient)                            │  │
│  │  - WebSocket Client (wsClient)                       │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP/WebSocket
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                   VPS (92.112.181.127)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Backend Server (Node.js)                 │  │
│  │  - Express HTTP API                                   │  │
│  │  - Socket.IO WebSocket Server                        │  │
│  │  - PostgreSQL Database                               │  │
│  │  - PM2 Process Manager                               │  │
│  │  - Docker Services                                   │  │
│  │  - MCP Servers                                       │  │
│  │  - Code-Server Instances                             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
ai-desktop/
├── client/                    # Lightweight frontend (<5MB)
│   ├── app/                   # Next.js app router
│   ├── components/            # React components
│   ├── lib/
│   │   ├── api-client.ts     # ✅ API communication
│   │   ├── ws-client.ts      # ✅ WebSocket client
│   │   └── store/            # Zustand state management
│   ├── public/               # Static assets
│   ├── next.config.js        # ✅ Static export config
│   ├── package.json          # ✅ Dependencies
│   └── .env.example          # ✅ Environment template
│
├── backend/                   # API server on VPS
│   ├── app/api/              # All API routes (TODO: migrate)
│   ├── lib/
│   │   └── db.js             # ✅ PostgreSQL connection
│   ├── migrations/           # Database migrations
│   │   ├── 001_initial_schema.sql  # ✅ Schema
│   │   └── migrate.js        # ✅ Migration runner
│   ├── server.js             # ✅ Express + Socket.IO
│   ├── package.json          # ✅ Dependencies
│   └── .env.example          # ✅ Environment template
│
├── shared/                    # Shared types/utils
│   └── types/
│       └── index.ts          # ✅ TypeScript types
│
└── docs/                      # Documentation
    ├── TECHNICAL_REVIEW.md
    ├── LIGHTWEIGHT_CLIENT_ARCHITECTURE.md
    └── MIGRATION_PLAN.md
```

## Setup Instructions

### Prerequisites

- Node.js >= 18.0.0
- PostgreSQL >= 14
- PM2 (for production)
- Access to VPS (92.112.181.127)

### 1. Database Setup

SSH into VPS:
```bash
ssh root@92.112.181.127
```

Install PostgreSQL:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

Create database and user:
```bash
sudo -u postgres psql

-- In PostgreSQL shell:
CREATE DATABASE ai_desktop;
CREATE USER ai_desktop_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_desktop TO ai_desktop_user;
\q
```

### 2. Backend Setup

Navigate to backend directory:
```bash
cd /root/ai-desktop/backend
```

Install dependencies:
```bash
npm install
```

Create `.env` file:
```bash
cp .env.example .env
nano .env
```

Configure environment variables:
```env
PORT=3000
NODE_ENV=production
CLIENT_URL=http://92.112.181.127
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_desktop
DB_USER=ai_desktop_user
DB_PASSWORD=your_secure_password
```

Run database migrations:
```bash
node migrations/migrate.js
```

Start backend server:
```bash
# Development
npm run dev

# Production with PM2
npm run pm2:start
```

### 3. Client Setup

Navigate to client directory:
```bash
cd /root/ai-desktop/client
```

Install dependencies:
```bash
npm install
```

Create `.env` file:
```bash
cp .env.example .env
nano .env
```

Configure environment variables:
```env
NEXT_PUBLIC_API_URL=http://92.112.181.127
NEXT_PUBLIC_WS_URL=http://92.112.181.127
NEXT_PUBLIC_ENV=production
```

Build static export:
```bash
npm run build
```

This creates an `out/` directory with static files.

### 4. Nginx Configuration

Create nginx config for both client and backend:
```nginx
# /etc/nginx/sites-available/ai-desktop
server {
    listen 80;
    server_name 92.112.181.127;

    # Client - Static files
    location / {
        root /root/ai-desktop/client/out;
        try_files $uri $uri/ /index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /socket.io/ {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:3000;
    }
}
```

Enable site and restart nginx:
```bash
sudo ln -s /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Development Workflow

### Local Development

**Terminal 1 - Backend:**
```bash
cd backend
npm run dev
```

**Terminal 2 - Client:**
```bash
cd client
npm run dev
```

Access at: http://localhost:3001

### Production Deployment

**Deploy Backend:**
```bash
cd backend
npm run pm2:restart
```

**Deploy Client:**
```bash
cd client
npm run build
# Copy out/ directory to nginx root
sudo rm -rf /var/www/ai-desktop
sudo cp -r out /var/www/ai-desktop
```

## API Client Usage

Replace direct API calls with `apiClient`:

**Before:**
```typescript
const response = await fetch('/api/vscode/repositories')
const data = await response.json()
```

**After:**
```typescript
import { apiClient } from '@/lib/api-client'

const response = await apiClient.get('/api/vscode/repositories')
if (response.success) {
  const repositories = response.data
}
```

## WebSocket Client Usage

Subscribe to real-time events:

```typescript
import { wsClient } from '@/lib/ws-client'

// Connect to WebSocket
wsClient.connect()

// Subscribe to Flow Builder agent output
const unsubscribe = wsClient.subscribeToAgent(agentId, (data) => {
  console.log('Agent output:', data)
})

// Subscribe to MCP server logs
wsClient.subscribeToMCPLogs(serverId, (log) => {
  console.log('MCP log:', log)
})

// Cleanup
unsubscribe()
wsClient.disconnect()
```

## Database Access

Query the database from backend:

```javascript
const db = require('./lib/db')

// Simple query
const result = await db.query('SELECT * FROM repositories WHERE running = $1', [true])

// Transaction
await db.transaction(async (client) => {
  await client.query('INSERT INTO repositories ...')
  await client.query('INSERT INTO deployments ...')
})
```

## Migration Status

### ✅ Completed
- Branch created (`lightweight-client`)
- Project structure set up
- API client library
- WebSocket client
- Backend server with Socket.IO
- PostgreSQL schema and migrations
- Database connection pool
- Environment configuration
- Next.js static export config

### 🔄 In Progress
- Migrating API routes from `app/api/` to `backend/app/api/`
- Updating components to use `apiClient`
- State management with Zustand

### ⏳ Pending
- Component migration (VS Code Manager, MCP Hub, Service Manager, Flow Builder)
- End-to-end testing
- Performance optimization
- Production deployment

## Size Comparison

**Current (main branch):**
- Total: ~1.8GB
- node_modules: ~1.5GB
- Next.js: ~323MB

**Lightweight (this branch):**
- Client (built): <5MB (<1MB gzipped)
- Backend: runs on VPS
- **99.7% size reduction** for end users

## Next Steps

1. **Migrate API Routes**: Move all `/app/api/*` routes to `/backend/app/api/`
2. **Update Components**: Replace `fetch()` calls with `apiClient`
3. **Add State Management**: Implement Zustand stores for global state
4. **Test Everything**: Ensure all features work identically
5. **Deploy to VPS**: Use PM2 for backend, nginx for client

## Rollback Plan

If issues occur, switch back to `vps-deployment` branch:
```bash
git checkout vps-deployment
pm2 restart all
```

## Support

For questions or issues with this migration:
1. Check `LIGHTWEIGHT_CLIENT_ARCHITECTURE.md` for detailed architecture
2. Check `TECHNICAL_REVIEW.md` for system overview
3. Check `MIGRATION_PLAN.md` for progress tracking
