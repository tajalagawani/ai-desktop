# Complete VS Code Multi-Instance Implementation Plan

## Goal
Clean implementation of multiple code-server instances with Nginx routing, where each repository gets its own isolated VS Code server.

## Phase 1: Complete Cleanup (Remove Old System)

### Step 1.1: Kill All Running Processes
```bash
# Kill ALL code-server processes (including old ones)
pkill -9 code-server

# Verify nothing is running
ps aux | grep code-server
```

### Step 1.2: Remove All Temporary Data
```bash
# Remove all temp directories
rm -rf /tmp/code-server-*
rm -rf /tmp/vscode-agent-*
rm -rf /var/www/vscode-workspaces

# Clean up old workspace copies
find /tmp -name "*code-server*" -type d -exec rm -rf {} + 2>/dev/null
```

### Step 1.3: Reset Databases
```bash
# Backup current databases
cd /var/www/ai-desktop/data
cp vscode-ports.json vscode-ports.json.backup 2>/dev/null || true
cp repositories.json repositories.json.backup 2>/dev/null || true

# Clear port allocations
echo '{"instances":[]}' > vscode-ports.json

# Reset vscode status in repositories
# (Keep repo data, just clear vscode running states)
```

### Step 1.4: Clean Nginx Configs
```bash
# Remove all auto-generated VS Code configs
rm -rf /etc/nginx/vscode-projects/*

# Test nginx config is still valid
nginx -t

# Reload nginx
systemctl reload nginx
```

---

## Phase 2: Architecture Design

### How It Will Work

```
User Request → Next.js App (port 80) → Nginx → code-server instance (port 8888-8899)
                                         ↓
                                  /vscode/repo-id/
```

### URL Pattern
- `http://92.112.181.127/vscode/actmcp/` → code-server on port 8888
- `http://92.112.181.127/vscode/pytorch-transformers/` → code-server on port 8889
- Auto-appends `?folder=/var/www/github/repo-name` for correct workspace

### Port Allocation
- Range: 8888-8899 (12 concurrent instances max)
- Managed by PortManager
- Auto-released when server stops

### Process Isolation
Each code-server instance gets:
- Unique port (8888-8899)
- Isolated user-data-dir: `/tmp/code-server-userdata-{repo}-{port}`
- Isolated extensions-dir: `/tmp/code-server-extensions-{repo}-{port}`
- Isolated agent folder: `/tmp/vscode-agent-{repo}-{port}`

### Nginx Configuration
Each repository gets a dedicated Nginx config file:
- Location: `/etc/nginx/vscode-projects/{repo-id}.conf`
- Auto-included in main nginx.conf
- WebSocket support enabled
- Automatic `?folder=` parameter injection

---

## Phase 3: Code Fixes

### Fix 1: Code Server Manager
**File**: `lib/vscode/code-server-manager.ts`

**Issues to Fix**:
1. Port detection timeout (already fixed with Node.js net.Socket)
2. Verify process spawning works correctly
3. Add better error handling for process failures

**What's Already Good**:
- Direct repository path opening (no syncing)
- Complete isolation per instance
- Detached process spawning

### Fix 2: Nginx Config Manager
**File**: `lib/vscode/nginx-config.ts`

**Issues to Fix**:
1. Verify redirect logic doesn't cause infinite loops (already fixed)
2. Test WebSocket proxying works
3. Ensure configs are properly included in main nginx.conf

**What's Already Good**:
- Auto-generates configs per project
- Includes folder parameter redirect
- WebSocket headers configured

### Fix 3: Port Manager
**File**: `lib/vscode/port-manager.ts`

**What to Verify**:
- Port allocation works (8888-8899 range)
- Port release works properly
- Database doesn't get corrupted
- Handles concurrent requests safely

### Fix 4: Start API Route
**File**: `app/api/code-server/start/route.ts`

**Issues to Fix**:
1. Better error handling for startup failures
2. Verify existing instance detection works
3. Add rollback logic if Nginx config fails
4. Test concurrent starts don't conflict

### Fix 5: Stop API Route
**File**: `app/api/code-server/stop/route.ts`

**What to Verify**:
- Process killing works (SIGTERM then SIGKILL)
- Port is released properly
- Nginx config is removed
- Repository status is updated

---

## Phase 4: Testing Plan

### Test 1: Single Instance
1. Start code-server for one repository
2. Verify it starts on correct port
3. Check Nginx config is created
4. Access via browser: `http://IP/vscode/repo-id/`
5. Verify VS Code opens with correct folder
6. Stop the instance
7. Verify process killed, port released, config removed

### Test 2: Multiple Instances (Sequential)
1. Start code-server for repo A
2. Start code-server for repo B
3. Verify both running on different ports
4. Access both via browser
5. Stop repo A
6. Verify repo B still works
7. Stop repo B

### Test 3: Multiple Instances (Concurrent)
1. Start 3 repositories simultaneously
2. Verify all start without conflicts
3. Check port allocation is unique
4. Access all 3 via browser
5. Kill all at once
6. Verify clean shutdown

### Test 4: Process Recovery
1. Start code-server for a repo
2. Manually kill the process (simulate crash)
3. Try to start it again
4. Verify old port is released and new one allocated
5. Verify it starts successfully

### Test 5: Full Cleanup
1. Start several instances
2. Use "Kill All" button
3. Verify all processes killed
4. Verify all temp directories removed
5. Verify all ports released
6. Verify can start fresh instances after cleanup

---

## Phase 5: Deployment Steps

### Step 5.1: Deploy Code Changes
```bash
cd /var/www/ai-desktop
git pull
npm run build
pm2 restart all
```

### Step 5.2: Run Full Cleanup
```bash
# Use the new cleanup API or run manually:
pkill -9 code-server
rm -rf /tmp/code-server-*
rm -rf /tmp/vscode-agent-*
echo '{"instances":[]}' > /var/www/ai-desktop/data/vscode-ports.json
rm -rf /etc/nginx/vscode-projects/*
nginx -t && systemctl reload nginx
```

### Step 5.3: Test One Instance
1. Open AI Desktop
2. Go to VS Code Editor app
3. Click "Start VS Code" on one repository
4. Wait for it to start
5. Click "Open VS Code" button
6. Verify it opens correctly

### Step 5.4: Test Multiple Instances
1. Start 2-3 repositories
2. Verify all show as "Running"
3. Open each one in browser
4. Verify all work independently
5. Stop all cleanly

---

## Phase 6: Monitoring & Maintenance

### Process Manager UI (Already Implemented)
- Shows all running code-server processes
- Auto-refreshes every 5 seconds
- Kill individual processes
- Kill all processes
- See CPU, memory, port usage

### Database Files to Monitor
```bash
# Port allocations
cat /var/www/ai-desktop/data/vscode-ports.json

# Repository status
cat /var/www/ai-desktop/data/repositories.json
```

### Nginx Configs to Check
```bash
# List all VS Code project configs
ls -la /etc/nginx/vscode-projects/

# View specific config
cat /etc/nginx/vscode-projects/actmcp.conf
```

### Log Files to Watch
```bash
# PM2 logs
pm2 logs ai-desktop --lines 100

# Nginx error log
tail -f /var/log/nginx/error.log

# Nginx access log
tail -f /var/log/nginx/access.log
```

---

## Known Issues & Solutions

### Issue: Port Timeout Errors
**Symptom**: "Timeout waiting for port XXXX to open"
**Solution**: Already fixed - using Node.js net.Socket() instead of netcat

### Issue: VS Code Opens Wrong Folder
**Symptom**: Shows /var/www instead of specific repo
**Solution**: Already fixed - Nginx auto-appends `?folder=` parameter

### Issue: Can't Kill Old Processes
**Symptom**: Old code-servers keep running
**Solution**: Use Process Manager UI or "Kill All" button

### Issue: Port Already in Use
**Symptom**: Can't start because port is taken
**Solution**: Kill old process, database will auto-update

### Issue: Nginx Config Not Loading
**Symptom**: 404 error when accessing /vscode/repo-id/
**Solution**: Check `/etc/nginx/vscode-projects/` has config file, run `nginx -t` and reload

---

## Success Criteria

✅ **Clean State**
- No old processes running
- No orphaned temp directories
- Clean port database
- Clean Nginx configs

✅ **Multiple Instances Work**
- Can start 3+ repositories simultaneously
- Each gets unique port
- Each accessible via Nginx URL
- No port conflicts

✅ **Proper Isolation**
- Each repo opens correct folder
- Extensions don't conflict
- Settings are independent

✅ **Clean Shutdown**
- Stop button kills process
- Port is released
- Nginx config removed
- Repository status updated

✅ **Process Recovery**
- Can restart after crash
- Old ports properly released
- Can start fresh after "Kill All"

✅ **User Experience**
- Process list shows real-time status
- Auto-refresh works
- Clear error messages
- Easy to manage multiple instances

---

## Next Steps

1. **Deploy current changes** to VPS
2. **Run full cleanup** (Phase 1)
3. **Test single instance** thoroughly
4. **Test multiple instances**
5. **Fix any remaining issues**
6. **Document final working state**

This plan provides a complete path from messy state to clean, working multi-instance VS Code setup.
