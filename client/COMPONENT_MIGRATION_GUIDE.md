## Component Migration Guide

This guide shows how to update existing components to use the new lightweight client architecture with API client, WebSocket client, and Zustand stores.

---

## Overview

**Old Architecture:**
- Components call `/api/*` endpoints directly with `fetch()`
- State managed locally with `useState`
- No real-time updates

**New Architecture:**
- Components use React hooks (`useMCPServers`, `useRepositories`, etc.)
- Global state managed with Zustand stores
- Real-time updates via WebSocket subscriptions
- All API calls go to VPS backend

---

## Migration Steps

### 1. Import the Hooks

```typescript
// OLD - Direct API calls
import { useState, useEffect } from 'react'

// NEW - Use custom hooks
import { useMCPServers } from '@/lib/hooks'
```

### 2. Replace State Management

```typescript
// OLD - Local state
const [servers, setServers] = useState([])
const [loading, setLoading] = useState(false)

// NEW - Use hook (state managed globally)
const { servers, loading, loadServers, performAction } = useMCPServers()
```

### 3. Replace API Calls

```typescript
// OLD - Direct fetch
const response = await fetch('/api/mcp')
const data = await response.json()
setServers(data.servers)

// NEW - Hook handles everything
// Just call: loadServers()
// The hook automatically updates the global state
```

### 4. Remove useEffect for Loading

```typescript
// OLD - Manual loading
useEffect(() => {
  fetch('/api/mcp')
    .then(res => res.json())
    .then(data => setServers(data.servers))
}, [])

// NEW - Hook auto-loads on mount
// No useEffect needed! The hook handles it
```

---

## Example: MCP Hub Migration

### Before (Old Code)

```typescript
'use client'

import React, { useState, useEffect, useCallback } from 'react'

export function MCPHub() {
  const [servers, setServers] = useState([])
  const [selectedServer, setSelectedServer] = useState(null)
  const [loading, setLoading] = useState(false)

  const loadServers = useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/mcp')
      const data = await response.json()
      if (data.success) {
        setServers(data.servers)
      }
    } catch (error) {
      console.error('Failed to load servers:', error)
    }
    setLoading(false)
  }, [])

  useEffect(() => {
    loadServers()
    const interval = setInterval(loadServers, 5000)
    return () => clearInterval(interval)
  }, [loadServers])

  const handleStart = async (id: string) => {
    const response = await fetch(`/api/mcp/${id}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'start' })
    })
    if (response.ok) {
      loadServers() // Reload
    }
  }

  return (
    <div>
      {loading && <p>Loading...</p>}
      {servers.map(server => (
        <div key={server.id}>
          <h3>{server.name}</h3>
          <button onClick={() => handleStart(server.id)}>Start</button>
        </div>
      ))}
    </div>
  )
}
```

### After (New Code)

```typescript
'use client'

import React from 'react'
import { useMCPServers } from '@/lib/hooks'

export function MCPHub() {
  // All state and API logic handled by the hook
  const {
    servers,
    selectedServer,
    loading,
    performAction,
    setSelectedServer
  } = useMCPServers()

  // Hook auto-loads and auto-refreshes every 5 seconds!

  const handleStart = async (id: string) => {
    await performAction(id, 'start')
    // State automatically updated!
  }

  return (
    <div>
      {loading && <p>Loading...</p>}
      {servers.map(server => (
        <div key={server.id}>
          <h3>{server.name}</h3>
          <button onClick={() => handleStart(server.id)}>Start</button>
        </div>
      ))}
    </div>
  )
}
```

**Lines of code reduced: 30 → 20 (33% reduction!)**

---

## Example: VS Code Manager Migration

### Before

```typescript
const [repositories, setRepositories] = useState([])

useEffect(() => {
  fetch('/api/vscode/list')
    .then(res => res.json())
    .then(data => setRepositories(data.repositories))
}, [])

const handleStart = async (repoId: string) => {
  await fetch('/api/vscode/start', {
    method: 'POST',
    body: JSON.stringify({ repoId })
  })
  // Reload list
  const res = await fetch('/api/vscode/list')
  const data = await res.json()
  setRepositories(data.repositories)
}
```

### After

```typescript
const { repositories, startCodeServer } = useRepositories()

// Auto-loads on mount!

const handleStart = async (repoId: string) => {
  await startCodeServer(repoId)
  // State automatically updated!
}
```

---

## Example: Service Manager Migration

### Before

```typescript
const [services, setServices] = useState([])

const performAction = async (serviceId: string, action: string) => {
  const response = await fetch('/api/services', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ serviceId, action })
  })

  if (response.ok) {
    // Reload services
    loadServices()
  }
}
```

### After

```typescript
const { services, performAction } = useServices()

// Hook handles API call AND state update
const handleAction = async (serviceId: string, action: string) => {
  await performAction(serviceId, action)
  // Done! State auto-updated
}
```

---

## Example: Flow Builder with WebSocket

### Before

```typescript
const [output, setOutput] = useState('')

useEffect(() => {
  // No WebSocket support in old version
}, [])
```

### After

```typescript
import { wsClient } from '@/lib/ws-client'
import { useFlowBuilder } from '@/lib/hooks'

const { currentSession, subscribeToAgent } = useFlowBuilder()
const [output, setOutput] = useState('')

useEffect(() => {
  if (!currentSession) return

  // Subscribe to real-time agent output
  const unsubscribe = subscribeToAgent(currentSession.id, (data) => {
    setOutput(prev => prev + data.content)
  })

  return () => unsubscribe()
}, [currentSession, subscribeToAgent])
```

---

## Available Hooks

### VS Code Manager

```typescript
import { useRepositories, useDeployments, useFlows } from '@/lib/hooks'

// Repositories
const {
  repositories,
  loading,
  error,
  loadRepositories,
  startCodeServer,
  stopCodeServer,
  getChanges,
  getDiff,
  cleanup
} = useRepositories()

// Deployments
const {
  deployments,
  loadDeployments,
  createDeployment,
  performAction,
  subscribeToLogs
} = useDeployments()

// Flows
const { flows, loadFlows } = useFlows()
```

### MCP Hub

```typescript
import { useMCPServers, useMCPTools } from '@/lib/hooks'

// Servers
const {
  servers,
  selectedServer,
  loading,
  error,
  loadServers,
  createServer,
  performAction,
  subscribeToLogs,
  setSelectedServer
} = useMCPServers()

// Tools
const { tools, loadTools, executeTool } = useMCPTools(serverId)
```

### Service Manager

```typescript
import { useServices } from '@/lib/hooks'

const {
  services,
  dockerInstalled,
  loading,
  error,
  loadServices,
  performAction,
  subscribeToStatus,
  getLogs
} = useServices()
```

### Flow Builder

```typescript
import { useFlowBuilder, useFlowBuilderSettings } from '@/lib/hooks'

// Sessions
const {
  sessions,
  currentSession,
  loading,
  error,
  loadSessions,
  createSession,
  getSession,
  deleteSession,
  subscribeToAgent,
  setCurrentSession
} = useFlowBuilder()

// Settings
const {
  settings,
  loadSettings,
  updateSettings
} = useFlowBuilderSettings()
```

---

## WebSocket Integration

### Connecting to WebSocket

```typescript
import { wsClient } from '@/lib/ws-client'

// In root layout or _app.tsx
useEffect(() => {
  wsClient.connect()

  return () => {
    wsClient.disconnect()
  }
}, [])
```

### Subscribing to Events

```typescript
// Flow Builder agent output
const unsubscribe = wsClient.subscribeToAgent(agentId, (data) => {
  console.log('Agent output:', data)
})

// MCP server logs
const unsubscribe = wsClient.subscribeToMCPLogs(serverId, (log) => {
  console.log('MCP log:', log)
})

// Service status updates
const unsubscribe = wsClient.subscribeToServiceStatus(serviceId, (status) => {
  console.log('Service status:', status)
})

// Deployment logs
const unsubscribe = wsClient.subscribeToDeploymentLogs(deploymentId, (log) => {
  console.log('Deployment log:', log)
})

// Cleanup
return () => unsubscribe()
```

---

## Accessing Stores Directly

If you need direct access to stores (for advanced use cases):

```typescript
import { useMCPStore, useVSCodeStore } from '@/lib/store'

// Get state
const servers = useMCPStore(state => state.servers)
const loading = useMCPStore(state => state.loading)

// Call actions
const { setServers, updateServer } = useMCPStore()
```

---

## Environment Configuration

Update `.env.local` for local development:

```env
NEXT_PUBLIC_API_URL=http://localhost:3000
NEXT_PUBLIC_WS_URL=http://localhost:3000
```

For production (client build):

```env
NEXT_PUBLIC_API_URL=http://92.112.181.127
NEXT_PUBLIC_WS_URL=http://92.112.181.127
```

---

## Testing Checklist

After migrating a component:

- [ ] Component loads data on mount
- [ ] Loading states work correctly
- [ ] Actions (start/stop/create/delete) work
- [ ] State updates after actions
- [ ] WebSocket events are received (if applicable)
- [ ] No console errors
- [ ] UI matches original exactly

---

## Common Pitfalls

### ❌ DON'T: Use fetch directly

```typescript
const response = await fetch('/api/mcp')
```

### ✅ DO: Use apiClient

```typescript
const response = await apiClient.get('/api/mcp')
```

### ❌ DON'T: Manage state locally when global state exists

```typescript
const [servers, setServers] = useState([])
```

### ✅ DO: Use the store hook

```typescript
const { servers } = useMCPServers()
```

### ❌ DON'T: Manually reload after actions

```typescript
await fetch('/api/mcp/123/action', { method: 'POST', ... })
loadServers() // Manual reload
```

### ✅ DO: Let the hook handle it

```typescript
await performAction('123', 'start')
// Hook automatically updates state!
```

---

## Benefits of New Architecture

1. **Less Code**: 30-50% reduction in component code
2. **Global State**: Share state across components easily
3. **Real-time Updates**: WebSocket support built-in
4. **Better UX**: Optimistic updates, no manual reloads
5. **Type Safety**: Full TypeScript support
6. **Easier Testing**: Hooks can be tested independently
7. **Scalable**: Easy to add new features

---

## Need Help?

Check these files for reference:
- `client/lib/hooks/` - All React hooks
- `client/lib/store/` - All Zustand stores
- `client/lib/api-client.ts` - API client
- `client/lib/ws-client.ts` - WebSocket client
- `backend/API_REFERENCE.md` - Complete API documentation
