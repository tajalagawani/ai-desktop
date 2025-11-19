# AI Desktop - Testing Guide

Complete testing procedures for the lightweight client architecture.

---

## Prerequisites

- Node.js >= 18.0.0
- PostgreSQL >= 14
- Docker (for Service Manager)
- PM2 (for deployments)

---

## Local Development Setup

### 1. Database Setup

```bash
# Start PostgreSQL
# macOS (Homebrew)
brew services start postgresql@14

# Ubuntu/Debian
sudo systemctl start postgresql

# Create development database
psql postgres
CREATE DATABASE ai_desktop_dev;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE ai_desktop_dev TO postgres;
\q
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
npm install

# Copy environment file
cp .env.local .env

# Run migrations
node migrations/migrate.js

# Start backend server
npm run dev
```

Backend will run on: `http://localhost:3000`

### 3. Client Setup

```bash
# Open new terminal
cd client

# Install dependencies
npm install

# Copy environment file
cp .env.local .env.local

# Start development server
npm run dev
```

Client will run on: `http://localhost:3001`

---

## Testing Procedures

### Backend API Tests

#### 1. Health Check

```bash
curl http://localhost:3000/health
```

**Expected:**
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2025-11-19T...",
  "uptime": 123.45,
  "memory": {...}
}
```

#### 2. API Status

```bash
curl http://localhost:3000/api/status
```

**Expected:**
```json
{
  "success": true,
  "data": {
    "status": "running",
    "version": "1.0.0",
    "environment": "development",
    "socketConnections": 0
  }
}
```

#### 3. VS Code Manager

**List Repositories:**
```bash
curl http://localhost:3000/api/vscode/list
```

**Start Code Server:**
```bash
curl -X POST http://localhost:3000/api/vscode/start \
  -H "Content-Type: application/json" \
  -d '{"repoId": "test-id"}'
```

#### 4. MCP Hub

**List Servers:**
```bash
curl http://localhost:3000/api/mcp
```

**Create Server:**
```bash
curl -X POST http://localhost:3000/api/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-mcp",
    "name": "Test MCP",
    "command": "node",
    "args": ["server.js"],
    "description": "Test server"
  }'
```

**Perform Action:**
```bash
curl -X POST http://localhost:3000/api/mcp/test-mcp/action \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

#### 5. Service Manager

**List Services:**
```bash
curl http://localhost:3000/api/services
```

**Perform Action:**
```bash
curl -X POST http://localhost:3000/api/services \
  -H "Content-Type: application/json" \
  -d '{
    "serviceId": "postgresql",
    "action": "start"
  }'
```

#### 6. Flow Builder

**List Sessions:**
```bash
curl http://localhost:3000/api/flow-builder/sessions
```

**Create Session:**
```bash
curl -X POST http://localhost:3000/api/flow-builder/sessions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a data processing workflow"}'
```

#### 7. Deployments

**List Deployments:**
```bash
curl http://localhost:3000/api/deployments
```

**Create Deployment:**
```bash
curl -X POST http://localhost:3000/api/deployments \
  -H "Content-Type: application/json" \
  -d '{
    "repositoryId": "repo-id",
    "name": "production",
    "domain": "example.com",
    "port": 3000,
    "mode": "cluster",
    "instances": 4
  }'
```

---

### WebSocket Tests

#### 1. Connection Test

Create `test-websocket.js`:

```javascript
const io = require('socket.io-client')

const socket = io('http://localhost:3000', {
  transports: ['websocket', 'polling']
})

socket.on('connect', () => {
  console.log('✅ Connected:', socket.id)
})

socket.on('disconnect', (reason) => {
  console.log('❌ Disconnected:', reason)
})

socket.on('connect_error', (error) => {
  console.error('❌ Connection error:', error.message)
})

// Test joining a room
socket.emit('mcp:join', 'test-server-id')
console.log('Joined MCP room: test-server-id')

// Listen for events
socket.on('mcp:test-server-id:log', (log) => {
  console.log('📝 MCP Log:', log)
})

// Keep connection alive
setTimeout(() => {
  console.log('Closing connection')
  socket.disconnect()
  process.exit(0)
}, 5000)
```

Run:
```bash
node test-websocket.js
```

---

### Frontend Component Tests

#### 1. VS Code Manager

**Test Steps:**
1. Open browser to `http://localhost:3001`
2. Navigate to VS Code Manager
3. Verify repositories load
4. Click "Start" on a repository
5. Verify status changes to "Running"
6. Click "Stop"
7. Verify status changes to "Stopped"

**Expected Behavior:**
- ✅ No console errors
- ✅ Data loads on mount
- ✅ Actions trigger API calls
- ✅ State updates after actions
- ✅ Loading states visible

#### 2. MCP Hub

**Test Steps:**
1. Navigate to MCP Hub
2. Verify servers load automatically
3. Click on a server card
4. Verify detail view opens
5. Check "Tools" tab loads
6. Try "Playground" tab
7. Check "Logs" tab
8. Check "Settings" tab
9. Test start/stop/restart actions

**Expected Behavior:**
- ✅ Auto-refresh every 5 seconds
- ✅ No infinite loops
- ✅ Selected server persists
- ✅ All tabs work

#### 3. Service Manager

**Test Steps:**
1. Navigate to Service Manager
2. Verify services load
3. Check Docker status indicator
4. Try installing a service
5. Check start/stop/restart
6. Try viewing logs
7. Test remove action

**Expected Behavior:**
- ✅ Docker detection works
- ✅ Install progress shows
- ✅ Actions trigger correctly
- ✅ Logs display properly

#### 4. Flow Builder

**Test Steps:**
1. Navigate to Flow Builder
2. Enter a prompt
3. Click "Generate"
4. Verify session creates
5. Check output appears
6. Test WebSocket streaming (if implemented)
7. Try viewing past sessions
8. Test delete session

**Expected Behavior:**
- ✅ Session creates successfully
- ✅ Output displays
- ✅ History persists
- ✅ Delete works

---

### Database Tests

#### Check Tables

```bash
psql -d ai_desktop_dev -U postgres

-- List all tables
\dt

-- Check repositories
SELECT * FROM repositories;

-- Check MCP servers
SELECT * FROM mcp_servers;

-- Check services
SELECT * FROM services;

-- Check deployments
SELECT * FROM deployments;

-- Check flow sessions
SELECT * FROM flow_sessions;

\q
```

#### Verify Data Persistence

1. Create an MCP server via API
2. Check it exists in database
3. Restart backend
4. Verify server still exists
5. Delete server
6. Verify removed from database

---

### Integration Tests

#### End-to-End Flow

**Scenario: Create and deploy a repository**

1. **Add Repository** (via VS Code Manager)
   - Create repository record
   - Verify appears in list

2. **Start Code Server**
   - Click "Start"
   - Verify status changes
   - Check running in PM2: `pm2 list`

3. **Create Deployment**
   - Configure deployment settings
   - Start deployment
   - Verify nginx config
   - Test domain access

4. **Monitor Logs**
   - Check deployment logs
   - Verify WebSocket streaming
   - Watch real-time updates

5. **Cleanup**
   - Stop deployment
   - Remove repository
   - Verify all cleaned up

---

### Performance Tests

#### Bundle Size

```bash
cd client
npm run build
du -sh out
```

**Target:** < 5MB (< 1MB gzipped)

#### API Latency

```bash
# Install Apache Bench
# macOS: brew install httpd

# Test API endpoint
ab -n 1000 -c 10 http://localhost:3000/api/mcp
```

**Target:** < 100ms (p95)

#### Load Test

```bash
# Install artillery
npm install -g artillery

# Create load-test.yml
cat > load-test.yml << EOF
config:
  target: "http://localhost:3000"
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - flow:
      - get:
          url: "/api/mcp"
      - get:
          url: "/api/vscode/list"
      - get:
          url: "/api/services"
EOF

# Run load test
artillery run load-test.yml
```

**Target:** No errors, response time < 200ms

---

### Production Deployment Test

#### VPS Deployment

1. **Build:**
```bash
./build-all.sh
```

2. **Deploy:**
```bash
./deploy-lightweight.sh
# Select option 1 (Full deployment)
```

3. **Verify:**
```bash
# Check backend
ssh root@92.112.181.127 "pm2 list"

# Check nginx
curl http://92.112.181.127/health

# Check client
curl -I http://92.112.181.127/
```

4. **Test All Features:**
- Visit `http://92.112.181.127`
- Test all components
- Verify real-time updates
- Check WebSocket connection

---

## Troubleshooting

### Backend won't start

```bash
# Check PostgreSQL
psql -d ai_desktop_dev -U postgres -c "SELECT 1"

# Check port 3000
lsof -i :3000

# Check logs
tail -f /var/log/ai-desktop/backend.log
```

### Client won't connect

```bash
# Check environment
cat client/.env.local

# Verify API URL
curl $NEXT_PUBLIC_API_URL/health

# Check browser console for errors
```

### WebSocket not connecting

```bash
# Check Socket.IO
curl http://localhost:3000/socket.io/

# Check CORS
curl -H "Origin: http://localhost:3001" -I http://localhost:3000/health
```

### Database connection fails

```bash
# Check PostgreSQL running
pg_isready

# Check credentials
psql -d ai_desktop_dev -U postgres

# Check database exists
psql -l | grep ai_desktop
```

---

## Success Criteria

### ✅ All Tests Pass

- [ ] Backend health check returns 200
- [ ] All API endpoints return valid responses
- [ ] WebSocket connection successful
- [ ] Frontend loads without errors
- [ ] All components render correctly
- [ ] Actions trigger and state updates
- [ ] Database persistence works
- [ ] Real-time updates via WebSocket
- [ ] Production deployment successful
- [ ] Client bundle < 5MB
- [ ] API latency < 100ms (p95)
- [ ] Zero functional regressions

### ✅ Zero Breaking Changes

User experience must be **identical** to original version:
- Same features
- Same UI
- Same workflows
- Same performance or better

---

## Automated Testing (Future)

### Unit Tests

```bash
# Backend
cd backend
npm test

# Client
cd client
npm test
```

### E2E Tests

```bash
# Using Playwright
cd client
npx playwright test
```

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
      - name: Run tests
        run: |
          cd backend && npm test
          cd client && npm test
```

---

## Reporting Issues

If tests fail, provide:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Console logs
5. Environment details
6. Screenshots (if UI issue)

---

**Happy Testing! 🧪**
