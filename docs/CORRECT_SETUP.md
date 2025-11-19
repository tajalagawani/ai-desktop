# CORRECT Setup - How Everything Works

## Current Architecture (What You Have Now)

```
ai-desktop/ (Main App)
├── app/ (Next.js)
│   └── api/ (API routes running in Next.js)
├── components/ (React components)
├── lib/ (Libraries)
├── server.js (Custom Next.js server on port 3005)
└── package.json (Main app)
```

**Current:** Everything runs in ONE app on port 3005

---

## New Lightweight Architecture (What We're Building)

```
ai-desktop/ (Main App - Frontend Only)
├── app/ (Next.js)
├── components/ (React components) ← UPDATE THESE
├── lib/
│   ├── api-client.ts ← ADD THIS
│   ├── ws-client.ts ← ADD THIS
│   ├── store/ ← ADD THIS (Zustand stores)
│   └── hooks/ ← ADD THIS (React hooks)
├── server.js (Keep for development)
└── package.json (Main app)

backend/ (Separate Backend Server)
├── app/api/ (All API routes) ✅ DONE
├── lib/db.js ✅ DONE
├── migrations/ ✅ DONE
├── server.js (Express server) ✅ DONE
└── package.json ✅ DONE
```

**New:**
- **Frontend** (main app) on port 3005
- **Backend** (separate server) on port 3006

---

## Correct Setup Steps

### Step 1: Copy New Libraries to Main App

```bash
# Copy API client
cp client/lib/api-client.ts lib/

# Copy WebSocket client
cp client/lib/ws-client.ts lib/

# Copy stores
cp -r client/lib/store lib/

# Copy hooks
cp -r client/lib/hooks lib/
```

### Step 2: Update Port Configuration

**Backend runs on 3006** (not 3005!)
**Frontend stays on 3005** (main app)

Update `backend/.env.local`:
```env
PORT=3006  # Backend port
CLIENT_URL=http://localhost:3005  # Frontend URL
```

Update API client default in `lib/api-client.ts`:
```typescript
this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3006'
```

### Step 3: Add Environment Variable to Main App

Create `.env.local` in root:
```env
NEXT_PUBLIC_API_URL=http://localhost:3006
NEXT_PUBLIC_WS_URL=http://localhost:3006
```

### Step 4: Start Both Servers

**Terminal 1 - Backend (port 3006):**
```bash
cd backend
npm install
npm run dev
```

**Terminal 2 - Frontend (port 3005):**
```bash
# In root directory
npm run dev
```

**Browser:**
```
http://localhost:3005
```

---

## Migration Process

### For Each Component:

1. **Update imports** - Add hooks
2. **Replace fetch()** - Use hooks
3. **Test** - Verify it works
4. **Delete old API route** - Remove from `app/api/`

### Example: MCP Hub

**Before:**
```typescript
// components/apps/mcp-hub.tsx
const [servers, setServers] = useState([])

useEffect(() => {
  fetch('/api/mcp')  // ← Goes to Next.js API route
    .then(res => res.json())
    .then(data => setServers(data.servers))
}, [])
```

**After:**
```typescript
// components/apps/mcp-hub.tsx
import { useMCPServers } from '@/lib/hooks'

const { servers, loading } = useMCPServers()
// ← Uses API client → Goes to backend on 3006
// Auto-loads, auto-refreshes every 5 seconds
```

---

## What Happens Behind the Scenes

### Old Way (Current):
```
Browser → http://localhost:3005/api/mcp
        → Next.js API route (app/api/mcp/route.ts)
        → Response
```

### New Way (Lightweight):
```
Browser → Component uses useMCPServers()
        → Hook calls apiClient.get('/api/mcp')
        → apiClient sends to http://localhost:3006/api/mcp
        → Backend Express server (backend/app/api/mcp.js)
        → PostgreSQL database
        → Response
        → Hook updates Zustand store
        → Component re-renders with new data
```

---

## Directory Structure After Setup

```
ai-desktop/
├── lib/
│   ├── api-client.ts ← COPIED FROM client/
│   ├── ws-client.ts ← COPIED FROM client/
│   ├── store/ ← COPIED FROM client/
│   │   ├── vscode-store.ts
│   │   ├── mcp-store.ts
│   │   ├── services-store.ts
│   │   └── flow-builder-store.ts
│   └── hooks/ ← COPIED FROM client/
│       ├── use-vscode.ts
│       ├── use-mcp.ts
│       ├── use-services.ts
│       └── use-flow-builder.ts
├── components/apps/
│   ├── mcp-hub.tsx ← UPDATE THIS
│   ├── vscode-manager.tsx ← UPDATE THIS
│   ├── service-manager.tsx ← UPDATE THIS
│   └── flow-builder.tsx ← UPDATE THIS
├── app/api/ ← DELETE ONE BY ONE AFTER MIGRATION
└── .env.local ← CREATE THIS
```

---

## Ports Summary

| Service | Port | Purpose |
|---------|------|---------|
| Frontend (Main App) | 3005 | Next.js app (existing) |
| Backend API | 3006 | Express server (new) |
| Client (for testing) | 3001 | Standalone client (optional) |

---

## Ready Checklist

Before starting migration:

- [ ] Backend server running on port 3006
- [ ] Frontend app running on port 3005
- [ ] Can access http://localhost:3005
- [ ] Backend health check works: `curl http://localhost:3006/health`
- [ ] Libraries copied to main app `lib/` folder
- [ ] `.env.local` created in root with NEXT_PUBLIC_API_URL

---

**Next: Let me copy the libraries to the correct location!**
