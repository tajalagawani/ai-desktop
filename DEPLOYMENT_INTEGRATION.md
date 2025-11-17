# VS Code Manager - Deployment Integration Guide

## Changes to `/components/apps/vscode-manager.tsx`

### 1. Add Imports (at top of file, after existing imports)
```typescript
import { DeploymentCard } from "./vscode/deployment-card"
import type { DeploymentConfig } from "@/lib/deployment/types"
import { Rocket } from "lucide-react" // Add to existing lucide imports
```

### 2. Add State Variables (after existing useState declarations around line 67)
```typescript
const [deployments, setDeployments] = useState<DeploymentConfig[]>([])
const [showDeployConfig, setShowDeployConfig] = useState(false)
```

### 3. Add loadDeployments Function (after loadRepositories function around line 110)
```typescript
const loadDeployments = useCallback(async () => {
  try {
    const response = await fetch('/api/deployments')
    const data = await response.json()
    if (data.success) {
      setDeployments(data.deployments || [])
    }
  } catch (error) {
    console.error('Failed to load deployments:', error)
  }
}, [])

// Load deployments on mount and refresh
useEffect(() => {
  loadDeployments()
  const interval = setInterval(() => loadDeployments(), 10000) // Refresh every 10s
  return () => clearInterval(interval)
}, [loadDeployments])
```

### 4. Update Stats (around line 269-276)
```typescript
const stats = useMemo(() => {
  return {
    total: repositories.length,
    running: repositories.filter(r => r.running).length,
    stopped: repositories.filter(r => !r.running).length,
    git: repositories.filter(r => r.type === 'git').length,
    deployments: deployments.length, // ADD THIS LINE
    deploymentsRunning: deployments.filter(d => d.status === 'running').length, // ADD THIS LINE
  }
}, [repositories, deployments]) // ADD deployments to dependency array
```

### 5. Add Deployments Category Button (after the "folder" button around line 430)
```typescript
<button
  onClick={() => setSelectedCategory('deployments')}
  className={cn(
    "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2",
    selectedCategory === 'deployments'
      ? "bg-primary text-primary-foreground"
      : "hover:bg-muted"
  )}
>
  <Rocket className="h-4 w-4" />
  <span>Deployments ({stats.deployments})</span>
</button>
```

### 6. Add Deploy Button in Repository Detail View (around line 547, after the Play/Stop buttons)
```typescript
{selectedRepo.type === 'git' && (
  <Button
    size="sm"
    variant="outline"
    onClick={() => setShowDeployConfig(!showDeployConfig)}
    title="Deploy to VPS"
  >
    <Rocket className="h-3.5 w-3.5" />
  </Button>
)}
```

### 7. Replace Repository List Section (the entire section that shows repository cards)

Find the section that starts with `{/* Repository List */}` and shows repository cards.
Replace the ENTIRE right panel content (starting around line 440) with this:

```typescript
        {/* Right Panel - Content */}
        <div className="bg-background p-8 h-full overflow-hidden flex flex-col">
          {selectedCategory === 'deployments' ? (
            // Deployments View
            <div className="flex flex-col flex-1 min-h-0">
              <div className="mb-6 flex-shrink-0">
                <h2 className="mb-2 text-lg font-normal">Active Deployments</h2>
                <p className="text-sm text-muted-foreground">
                  Manage deployed applications on your VPS
                </p>
              </div>

              <div className="flex-1 min-h-0 overflow-y-auto space-y-4">
                {deployments.length === 0 ? (
                  <Alert>
                    <Rocket className="h-4 w-4" />
                    <AlertDescription>
                      No deployments yet. Select a repository and click Deploy to get started.
                    </AlertDescription>
                  </Alert>
                ) : (
                  deployments.map((deployment) => (
                    <DeploymentCard
                      key={deployment.id}
                      deployment={deployment}
                      onUpdate={loadDeployments}
                    />
                  ))
                )}
              </div>
            </div>
          ) : selectedRepo ? (
            // EXISTING Repository Detail View code stays here
            // ... (keep all the existing selectedRepo code)
          ) : (
            // EXISTING Repository List View code stays here
            // ... (keep all the existing repository list code)
          )}
        </div>
```

## Files Already Created

These files are already created and ready:
- ✅ `/lib/deployment/types.ts` - TypeScript types
- ✅ `/lib/deployment/detector.ts` - Framework detection
- ✅ `/lib/deployment/services.ts` - Service discovery
- ✅ `/app/api/deployments/route.ts` - Deployment API
- ✅ `/app/api/deployments/[id]/action/route.ts` - Deployment actions
- ✅ `/app/api/deployments/services/route.ts` - Services API
- ✅ `/components/apps/vscode/deployment-card.tsx` - Deployment UI card
- ✅ `/components/apps/vscode/deployment-logs.tsx` - Logs viewer
- ✅ `/server.js` - WebSocket log streaming (updated)

## Deployment Dialog Component (Optional - for inline deployment config)

The DeployDialog component was created but you said no dialogs. Instead, we can create an inline deployment configuration panel that appears in the repo detail view when "Deploy" button is clicked.

Would you like me to:
1. Just add the "Deployments" tab that shows existing deployments?
2. Also add an inline deployment configuration section in the repo detail view?
