# 🚀 START HERE - Lightweight Client Migration

## ✅ Setup Complete!

All libraries have been copied to the main app. Ready to start!

---

## How to Start (Mac)

### Step 1: Start Backend Server (Port 3006)

```bash
# Terminal 1
cd backend
cp .env.local .env
npm install
npm run dev
```

You should see:
```
🚀 AI Desktop Backend Server
Port: 3006
```

### Step 2: Start Frontend (Port 3005)

```bash
# Terminal 2 (from root directory)
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3005
```

### Step 3: Open Browser

```bash
open http://localhost:3005
```

---

## Verify Setup

### 1. Check Backend is Running

```bash
curl http://localhost:3006/health
```

Should return:
```json
{
  "success": true,
  "status": "healthy",
  ...
}
```

### 2. Check Frontend is Running

Open: http://localhost:3005

Should see your AI Desktop app (EXACTLY the same UI!)

---

## What's Different Now?

**NOTHING visible!** The UI is **EXACTLY the same**.

Behind the scenes:
- Old: API calls go to Next.js API routes (port 3005)
- New: API calls will go to Express backend (port 3006) **after migration**

---

## Migration Process

**Do ONE component at a time:**

1. **MCP Hub** (start here)
   - Update to use `useMCPServers()` hook
   - Test thoroughly
   - Delete old API route

2. **VS Code Manager**
   - Update to use `useRepositories()` hook
   - Test thoroughly
   - Delete old API routes

3. **Continue one by one...**

**See `MIGRATION_STEPS.md` for detailed instructions**

---

## Current Status

✅ Backend server ready (port 3006)
✅ All API endpoints implemented (36 endpoints)
✅ Libraries copied to main app (`lib/`)
✅ Environment configured
✅ Ready to start migration!

---

## Quick Commands

```bash
# Check what's running
lsof -i :3005  # Frontend
lsof -i :3006  # Backend

# Test backend endpoint
curl http://localhost:3006/api/mcp

# Test database
psql -d ai_desktop_dev -U postgres -c "SELECT COUNT(*) FROM mcp_servers;"
```

---

## ⚠️ Important Rules

1. **ZERO UI changes** - Everything must look and work EXACTLY the same
2. **One at a time** - Complete one component before next
3. **Test thoroughly** - Before deleting old files
4. **Keep old files** - Until new version works perfectly

---

## Need Help?

1. Check backend is running: `curl http://localhost:3006/health`
2. Check frontend is running: `open http://localhost:3005`
3. Check browser console for errors
4. Check backend terminal for logs

---

**Ready? Both servers running? Open http://localhost:3005 and let's start!** 🎉
