# AI Desktop - Component Migration Steps (One at a Time!)

## 🚨 Important Rules

1. **One component at a time** - Migrate, test, then move to next
2. **Don't delete old files until new one works** - Keep both during testing
3. **Test thoroughly before moving on** - Each component must work perfectly
4. **Mac port: 3005** - Backend runs on localhost:3005
5. **VPS port: 80** - Nginx proxies to backend on port 3000

---

## Port Configuration ✅ DONE

- ✅ Mac backend: `localhost:3005`
- ✅ Mac client: `localhost:3001`
- ✅ VPS backend: Internal port 3000, nginx proxies to port 80
- ✅ Updated all .env files
- ✅ Updated api-client.ts default
- ✅ Updated ws-client.ts default

---

## Component Migration Order

### Step 1: MCP Hub (Start Here!) ⏳

**Why first?** Already has some fixes, infinite loop resolved

**Files to update:**
1. `components/apps/mcp-hub.tsx` (main component)
2. `components/apps/mcp/mcp-detail.tsx` (detail view)

**What to do:**

1. **Update MCP Hub Main Component**
   ```bash
   # Open the file
   code components/apps/mcp-hub.tsx
   ```

   Replace this:
   ```typescript
   const [servers, setServers] = useState([])
   const [loading, setLoading] = useState(false)

   useEffect(() => {
     fetch('/api/mcp')...
   }, [])
   ```

   With this:
   ```typescript
   import { useMCPServers } from '@/lib/hooks'

   const { servers, loading, performAction, setSelectedServer } = useMCPServers()
   // That's it! Auto-loads and auto-refreshes every 5 seconds
   ```

2. **Test MCP Hub**
   ```bash
   # Terminal 1 - Start backend
   cd backend
   npm install  # First time only
   npm run dev  # Should run on port 3005

   # Terminal 2 - Start client
   cd client
   npm install  # First time only
   npm run dev  # Should run on port 3001

   # Open browser
   open http://localhost:3001
   ```

3. **Verify MCP Hub Works**
   - [ ] Servers list loads
   - [ ] Auto-refresh works (5 seconds)
   - [ ] Can click on server card
   - [ ] Detail view opens
   - [ ] Can start/stop server
   - [ ] Status updates correctly
   - [ ] No console errors
   - [ ] No infinite loops

4. **Only After Testing - Delete Old API Route**
   ```bash
   # ONLY delete after confirming new one works!
   rm -rf app/api/mcp
   ```

---

### Step 2: VS Code Manager

**Files to update:**
1. `components/apps/vscode-manager.tsx`
2. `components/apps/vscode/deployment-card.tsx`
3. `components/apps/vscode/deployment-logs.tsx`

**What to do:**

1. **Update VS Code Manager**
   ```typescript
   import { useRepositories, useDeployments, useFlows } from '@/lib/hooks'

   const { repositories, startCodeServer, stopCodeServer } = useRepositories()
   const { deployments, performAction } = useDeployments()
   const { flows } = useFlows()
   ```

2. **Test VS Code Manager**
   - [ ] Repositories list loads
   - [ ] Can start/stop code-server
   - [ ] Deployments list loads
   - [ ] Can start/stop/restart deployments
   - [ ] Flows list loads
   - [ ] No console errors

3. **Delete Old API Routes**
   ```bash
   rm -rf app/api/vscode
   rm -rf app/api/repositories
   rm -rf app/api/deployments
   ```

---

### Step 3: Service Manager

**Files to update:**
1. `components/apps/service-manager.tsx`

**What to do:**

1. **Update Service Manager**
   ```typescript
   import { useServices } from '@/lib/hooks'

   const { services, dockerInstalled, performAction } = useServices()
   ```

2. **Test Service Manager**
   - [ ] Services list loads
   - [ ] Docker status shows correctly
   - [ ] Can install service
   - [ ] Can start/stop service
   - [ ] Can remove service
   - [ ] No console errors

3. **Delete Old API Route**
   ```bash
   rm -rf app/api/services
   ```

---

### Step 4: Flow Builder

**Files to update:**
1. `components/apps/flow-builder.tsx`

**What to do:**

1. **Update Flow Builder**
   ```typescript
   import { useFlowBuilder, useFlowBuilderSettings } from '@/lib/hooks'
   import { wsClient } from '@/lib/ws-client'

   const { sessions, createSession, subscribeToAgent } = useFlowBuilder()
   const { settings } = useFlowBuilderSettings()
   ```

2. **Test Flow Builder**
   - [ ] Can create new session
   - [ ] Sessions list loads
   - [ ] Can view session output
   - [ ] WebSocket streaming works (if implemented)
   - [ ] No console errors

3. **Delete Old API Routes**
   ```bash
   rm -rf app/api/flow-builder
   ```

---

### Step 5: File Manager (if exists)

**Files to update:**
1. `components/apps/file-manager.tsx` (if exists)

**What to do:**

1. **Update File Manager**
   - Use apiClient directly (no hook yet)
   ```typescript
   import { apiClient } from '@/lib/api-client'

   const loadFiles = async (path) => {
     const response = await apiClient.get(`/api/files?path=${path}`)
     if (response.success) {
       setFiles(response.data.files)
     }
   }
   ```

2. **Test File Manager**
   - [ ] Files list loads
   - [ ] Can navigate folders
   - [ ] Can create folder
   - [ ] Can delete file/folder
   - [ ] No console errors

3. **Delete Old API Route**
   ```bash
   rm -rf app/api/files
   ```

---

### Step 6: System Monitor (if exists)

**Files to update:**
1. `components/apps/system-monitor.tsx` (if exists)

**What to do:**

1. **Update System Monitor**
   ```typescript
   import { apiClient } from '@/lib/api-client'

   const loadStats = async () => {
     const response = await apiClient.get('/api/system-stats')
     if (response.success) {
       setStats(response.data)
     }
   }
   ```

2. **Test System Monitor**
   - [ ] System stats load
   - [ ] CPU/RAM/Disk show correctly
   - [ ] Auto-refresh works
   - [ ] No console errors

3. **Delete Old API Routes**
   ```bash
   rm -rf app/api/system-stats
   rm -rf app/api/system-logs
   rm -rf app/api/pm2-processes
   ```

---

### Step 7: GitHub/Git Manager (if exists)

**Files to update:**
1. `components/apps/github.tsx` (if exists)

**What to do:**

1. **Update Git Manager**
   ```typescript
   import { apiClient } from '@/lib/api-client'

   const executeGit = async (command) => {
     const response = await apiClient.post('/api/git', { repoPath, command })
     if (response.success) {
       console.log(response.data.stdout)
     }
   }
   ```

2. **Test Git Manager**
   - [ ] Git commands execute
   - [ ] Output displays correctly
   - [ ] Errors handled properly
   - [ ] No console errors

3. **Delete Old API Routes**
   ```bash
   rm -rf app/api/git
   rm -rf app/api/git-config
   ```

---

### Step 8: Terminal (optional)

**Files to update:**
1. `components/apps/terminal.tsx` (if exists)

**What to do:**

**Note:** Terminal WebSocket is NOT implemented yet.
- Either skip this component
- Or keep old implementation
- Or implement WebSocket terminal later

---

## Final Cleanup (ONLY AFTER ALL COMPONENTS WORK!)

```bash
# Delete remaining old API files
rm -rf app/api/changelog
rm -rf app/api/terminal

# Verify nothing left
ls app/api/  # Should be empty or only have necessary files
```

---

## Testing Checklist (After Each Component)

Before moving to next component, verify:

- [ ] Component renders without errors
- [ ] Data loads correctly
- [ ] Actions (start/stop/create/delete) work
- [ ] State updates after actions
- [ ] No console errors
- [ ] No network errors in DevTools
- [ ] Backend logs show API calls
- [ ] Database updates (check with psql)

---

## Quick Start Commands

### Local Development (Mac)

```bash
# Terminal 1 - Backend
cd backend
cp .env.local .env  # First time only
npm install  # First time only
npm run dev  # Runs on port 3005

# Terminal 2 - Client
cd client
cp .env.local .env.local  # First time only
npm install  # First time only
npm run dev  # Runs on port 3001

# Browser
open http://localhost:3001
```

### Check Backend is Running

```bash
# Should return health status
curl http://localhost:3005/health

# Should return API status
curl http://localhost:3005/api/status

# Test MCP endpoint
curl http://localhost:3005/api/mcp
```

### Check Database

```bash
# Connect to database
psql -d ai_desktop_dev -U postgres

# List tables
\dt

# Check MCP servers
SELECT * FROM mcp_servers;

# Exit
\q
```

---

## Current Status

- ✅ Port configuration fixed (Mac: 3005, VPS: 80)
- ✅ All backend API routes created
- ✅ All hooks created
- ✅ All stores created
- ⏳ **NEXT: Start with MCP Hub migration**

---

## Important Notes

1. **Don't rush** - Take time to test each component thoroughly
2. **Keep both versions** - Old and new, until new works perfectly
3. **Check console** - Watch for errors in browser console
4. **Check network** - Watch API calls in DevTools Network tab
5. **Check backend** - Watch backend terminal for logs
6. **One at a time** - Complete one component before moving to next
7. **Ask questions** - If something doesn't work, debug before moving on

---

**Ready to start? Begin with MCP Hub (Step 1)!**
