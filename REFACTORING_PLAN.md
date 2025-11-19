# AI Desktop - Code Organization Refactoring Plan
## Making it a Masterpiece 🎨

---

## Current Issues

### 1. **Duplicate Files & Folders**
- ❌ `/client` folder exists but seems unused (has its own package.json)
- ❌ `/lib/api-client.ts` duplicated in `/client/lib/api-client.ts` and `/backend/lib/api-client.ts`
- ❌ Multiple `.env` files (`.env`, `.env.local`, `.env.example`, `.env.production`)
- ❌ Backend has 8 markdown docs that should be in `/docs`
- ❌ `server.js` in root when there's already `backend/server.js`

### 2. **Poor Folder Organization**
- ❌ `/components` mixes everything (apps, ui, features, flow-builder, desktop)
- ❌ `/lib` has mixed concerns (flow-builder, deployment, hooks, stores, utils)
- ❌ `/data` folder has both runtime data and source code
- ❌ No clear separation between source code and runtime data

### 3. **Backup & Unnecessary Files**
- ❌ `.DS_Store` files
- ❌ `.env.backup.1763570094` in backend
- ❌ `all-services.ts.backup`
- ❌ `components/apps/service-manager-OLD.tsx`
- ❌ `installable-services.backup.ts`

### 4. **Inconsistent Structure**
- ❌ Some features in `/components/apps`, some in `/components/features`
- ❌ Hooks scattered in `/hooks` and `/lib/hooks`
- ❌ Stores scattered in `/lib/store` and `/lib/flow-builder/stores`

---

## Proposed Refactored Structure

```
ai-desktop/
├── README.md
├── package.json
├── next.config.mjs
├── tsconfig.json
├── .gitignore
├── .env.example                    # Example config only
│
├── docs/                            # Documentation
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── FLOW_BUILDER.md
│   └── SECURITY.md
│
├── src/                             # All source code
│   ├── app/                         # Next.js app directory
│   │   ├── (auth)/
│   │   ├── (desktop)/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   │
│   ├── components/                  # React components (organized by feature)
│   │   ├── ui/                      # Base UI components (shadcn/ui)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/                  # Layout components
│   │   │   ├── desktop/
│   │   │   │   ├── Desktop.tsx
│   │   │   │   ├── Window.tsx
│   │   │   │   ├── Dock.tsx
│   │   │   │   └── Taskbar.tsx
│   │   │   ├── sidebar/
│   │   │   └── navigation/
│   │   │
│   │   ├── features/                # Feature components
│   │   │   ├── file-manager/
│   │   │   │   ├── FileManager.tsx
│   │   │   │   ├── FileTree.tsx
│   │   │   │   └── FileViewer.tsx
│   │   │   ├── terminal/
│   │   │   │   ├── Terminal.tsx
│   │   │   │   └── XTermConsole.tsx
│   │   │   ├── vscode/
│   │   │   │   ├── VSCodeManager.tsx
│   │   │   │   ├── DeploymentCard.tsx
│   │   │   │   └── DeploymentLogs.tsx
│   │   │   ├── github/
│   │   │   │   ├── GitHubApp.tsx
│   │   │   │   ├── CloneDialog.tsx
│   │   │   │   └── RepositoryList.tsx
│   │   │   ├── mcp-hub/
│   │   │   │   ├── MCPHub.tsx
│   │   │   │   ├── ServerCard.tsx
│   │   │   │   └── SecurityCenter.tsx
│   │   │   ├── flow-builder/
│   │   │   │   ├── FlowBuilder.tsx
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── ChatMessage.tsx
│   │   │   │   ├── Settings.tsx
│   │   │   │   └── TodoList.tsx
│   │   │   ├── service-manager/
│   │   │   │   ├── ServiceManager.tsx
│   │   │   │   ├── ServiceCard.tsx
│   │   │   │   └── ServiceDetails.tsx
│   │   │   └── system-monitor/
│   │   │       ├── SystemMonitor.tsx
│   │   │       └── StatCard.tsx
│   │   │
│   │   ├── shared/                  # Shared/common components
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   └── ThemeProvider.tsx
│   │   │
│   │   └── auth/                    # Auth components
│   │       └── TwoFactorAuth.tsx
│   │
│   ├── lib/                         # Core utilities & logic
│   │   ├── api/                     # API clients
│   │   │   ├── client.ts
│   │   │   └── websocket.ts
│   │   │
│   │   ├── hooks/                   # All React hooks
│   │   │   ├── common/
│   │   │   │   ├── use-mobile.ts
│   │   │   │   ├── use-toast.ts
│   │   │   │   └── use-outside-click.ts
│   │   │   ├── features/
│   │   │   │   ├── use-desktop.ts
│   │   │   │   ├── use-file-manager.ts
│   │   │   │   ├── use-flow-builder.ts
│   │   │   │   ├── use-mcp.ts
│   │   │   │   ├── use-services.ts
│   │   │   │   └── use-vscode.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── stores/                  # State management (Zustand)
│   │   │   ├── flow-builder.store.ts
│   │   │   ├── mcp.store.ts
│   │   │   ├── services.store.ts
│   │   │   ├── vscode.store.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── services/                # Business logic services
│   │   │   ├── deployment/
│   │   │   │   ├── detector.ts
│   │   │   │   ├── framework-services.ts
│   │   │   │   ├── types.ts
│   │   │   │   └── utils.ts
│   │   │   ├── mcp/
│   │   │   │   ├── manager.ts
│   │   │   │   ├── client.ts
│   │   │   │   ├── registry.ts
│   │   │   │   └── types.ts
│   │   │   ├── vscode/
│   │   │   │   ├── manager.ts
│   │   │   │   ├── config.ts
│   │   │   │   └── types.ts
│   │   │   ├── repositories/
│   │   │   │   ├── registry.ts
│   │   │   │   └── types.ts
│   │   │   ├── flow-builder/
│   │   │   │   ├── agent-manager.js
│   │   │   │   ├── agent.ts
│   │   │   │   ├── db.ts
│   │   │   │   └── types.ts
│   │   │   └── system/
│   │   │       └── stats.service.ts
│   │   │
│   │   ├── utils/                   # Utility functions
│   │   │   ├── cn.ts
│   │   │   ├── date.ts
│   │   │   ├── uuid.ts
│   │   │   ├── desktop.ts
│   │   │   └── icon-mapper.ts
│   │   │
│   │   └── config/                  # Configuration
│   │       └── site.ts
│   │
│   ├── data/                        # Static data & configs (NOT runtime data)
│   │   ├── desktop-apps.ts
│   │   ├── mcp-servers.ts
│   │   └── services.ts
│   │
│   ├── types/                       # TypeScript types
│   │   ├── app.types.ts
│   │   ├── api.types.ts
│   │   └── index.ts
│   │
│   └── styles/                      # Global styles
│       └── globals.css
│
├── backend/                         # Backend server
│   ├── .env.example
│   ├── package.json
│   ├── server.js
│   │
│   ├── app/                         # Backend application
│   │   ├── api/                     # API routes
│   │   │   ├── deployments.js
│   │   │   ├── file-manager.js
│   │   │   ├── flow-builder.js
│   │   │   ├── github.js
│   │   │   ├── mcp.js
│   │   │   ├── repositories.js
│   │   │   ├── services.js
│   │   │   └── vscode.js
│   │   │
│   │   ├── websocket/               # WebSocket handlers
│   │   │   ├── deployment-logs.js
│   │   │   └── terminal.js
│   │   │
│   │   └── lib/                     # Backend utilities
│   │       └── json-storage.js
│   │
│   └── docs/                        # Backend-specific docs
│       └── API_REFERENCE.md
│
├── storage/                         # Runtime data (gitignored)
│   ├── data/                        # JSON database files
│   │   ├── repositories.json
│   │   ├── deployments.json
│   │   ├── mcp-servers.json
│   │   ├── mcp-tokens.json
│   │   └── flow-sessions.json
│   ├── logs/                        # Log files
│   └── flows/                       # Generated workflow files
│
├── public/                          # Static assets
│   ├── icons/
│   │   ├── claude.png
│   │   └── services/
│   └── backgrounds/
│       ├── abstract-art.jpg
│       └── blue-abstract.avif
│
└── .github/                         # GitHub configs
    └── workflows/
        └── deploy.yml
```

---

## Refactoring Steps

### Phase 1: Clean Up (Remove Duplicates & Backups)

1. **Delete Duplicate/Unused Folders:**
   ```bash
   rm -rf client/                    # Unused client folder
   rm -f server.js                   # Duplicate (use backend/server.js)
   rm -f ecosystem.config.js          # Not needed with PM2
   ```

2. **Delete Backup Files:**
   ```bash
   find . -name "*.backup*" -delete
   find . -name "*-OLD*" -delete
   find . -name ".DS_Store" -delete
   rm -f backend/.env.backup.1763570094
   ```

3. **Move Backend Docs:**
   ```bash
   mv backend/API_REFERENCE.md docs/
   mv backend/COMPLETE_IMPLEMENTATION.md docs/
   # Delete other backend .md files (already documented elsewhere)
   ```

### Phase 2: Reorganize Source Code

1. **Create `src/` directory:**
   ```bash
   mkdir -p src/{components,lib,data,types,styles}
   ```

2. **Move components into `src/components`:**
   ```bash
   mv components/* src/components/
   ```

3. **Reorganize components by feature:**
   ```bash
   mkdir -p src/components/{ui,layout,features,shared,auth}

   # Move UI components
   mv src/components/ui src/components/ui

   # Move layout components
   mkdir -p src/components/layout/{desktop,sidebar,navigation}
   mv src/components/desktop/* src/components/layout/desktop/
   mv src/components/app-sidebar.tsx src/components/layout/sidebar/
   mv src/components/nav-*.tsx src/components/layout/navigation/

   # Move feature components
   mv src/components/apps/* src/components/features/
   mv src/components/flow-builder src/components/features/

   # Move shared components
   mv src/components/shared/* src/components/shared/
   mv src/components/theme-provider.tsx src/components/shared/
   ```

4. **Reorganize lib into `src/lib`:**
   ```bash
   mkdir -p src/lib/{api,hooks,stores,services,utils,config}

   # Move API clients
   mv lib/api-client.ts src/lib/api/client.ts
   mv lib/ws-client.ts src/lib/api/websocket.ts

   # Consolidate hooks
   mv hooks/* src/lib/hooks/common/
   mv lib/hooks/* src/lib/hooks/features/

   # Move stores
   mv lib/store/* src/lib/stores/
   mv lib/flow-builder/stores/* src/lib/stores/

   # Reorganize services
   mv lib/deployment src/lib/services/deployment
   mv lib/mcp-hub src/lib/services/mcp
   mv lib/vscode src/lib/services/vscode
   mv lib/repositories src/lib/services/repositories
   mv lib/flow-builder src/lib/services/flow-builder
   mv lib/services src/lib/services/system

   # Move utils
   mv lib/utils/* src/lib/utils/
   mv utils/* src/lib/utils/

   # Move config
   mv config/site.ts src/lib/config/
   ```

5. **Move other files:**
   ```bash
   # Move app directory
   mv app src/app

   # Move types
   mv types src/types
   mv shared/types/* src/types/

   # Move globals.css
   mkdir -p src/styles
   mv src/app/globals.css src/styles/

   # Move data (only source data, not runtime data)
   mv data/desktop-apps.ts src/data/
   mv data/mcp-servers.ts src/data/
   mv data/all-services.ts src/data/services.ts
   ```

### Phase 3: Create Storage Directory for Runtime Data

1. **Create storage directory (gitignored):**
   ```bash
   mkdir -p storage/{data,logs,flows}
   ```

2. **Move runtime data files:**
   ```bash
   # Move JSON files to storage
   mv data/*.json storage/data/
   mv backend/data/*.json storage/data/
   mv flows/* storage/flows/
   ```

3. **Update .gitignore:**
   ```gitignore
   # Runtime data
   /storage
   ```

4. **Create empty template files for storage:**
   ```bash
   cat > storage/data/repositories.json << 'EOF'
   {"repositories": []}
   EOF

   cat > storage/data/deployments.json << 'EOF'
   {"deployments": []}
   EOF

   cat > storage/data/mcp-servers.json << 'EOF'
   {"servers": []}
   EOF
   ```

### Phase 4: Update Import Paths

1. **Update tsconfig.json paths:**
   ```json
   {
     "compilerOptions": {
       "paths": {
         "@/*": ["./src/*"],
         "@/components/*": ["./src/components/*"],
         "@/lib/*": ["./src/lib/*"],
         "@/types/*": ["./src/types/*"],
         "@/data/*": ["./src/data/*"]
       }
     }
   }
   ```

2. **Run find-and-replace for imports:**
   ```bash
   # This will be automated with a script
   # Examples:
   # "@/components/ui" stays the same
   # "../../lib/hooks" → "@/lib/hooks"
   # "../../../components/apps" → "@/components/features"
   ```

### Phase 5: Update Backend Paths

1. **Update backend to use storage directory:**
   ```javascript
   // backend/app/lib/json-storage.js
   const DATA_DIR = path.join(__dirname, '../../../storage/data')
   ```

2. **Update environment variables:**
   ```bash
   # backend/.env
   DATA_DIR=/var/www/ai-desktop/storage/data
   LOGS_DIR=/var/www/ai-desktop/storage/logs
   FLOWS_DIR=/var/www/ai-desktop/storage/flows
   ```

### Phase 6: Documentation Cleanup

1. **Consolidate docs:**
   ```bash
   # Keep only essential docs in /docs
   docs/
   ├── README.md                          # Main documentation
   ├── ARCHITECTURE.md                    # System architecture
   ├── API_REFERENCE.md                   # Backend API reference
   ├── FLOW_BUILDER.md                    # Flow Builder guide
   └── SECURITY.md                        # Security best practices
   ```

2. **Delete redundant backend docs**

---

## Benefits After Refactoring

### ✅ **Clear Separation of Concerns**
- Source code in `/src`
- Runtime data in `/storage` (gitignored)
- Backend in `/backend`
- Documentation in `/docs`

### ✅ **Feature-based Component Organization**
- All file-manager components together
- All VS Code components together
- All flow-builder components together
- Easy to find and maintain

### ✅ **Unified Library Structure**
- All hooks in one place
- All stores in one place
- All services organized by feature
- All utils in one place

### ✅ **No Duplicates**
- Single source of truth for each file
- No backup files
- No old/unused code

### ✅ **Scalable Architecture**
- Easy to add new features
- Clear where each file belongs
- Consistent patterns throughout

---

## Automated Refactoring Script

A shell script will be created to automate most of these changes safely:

```bash
#!/bin/bash
# refactor.sh - Automated refactoring script

# 1. Cleanup phase
# 2. Create new structure
# 3. Move files
# 4. Update imports (using codemod or sed)
# 5. Verify build still works
# 6. Commit changes
```

---

## Estimated Timeline

- **Phase 1 (Cleanup)**: 30 minutes
- **Phase 2 (Reorganize)**: 2 hours
- **Phase 3 (Storage)**: 30 minutes
- **Phase 4 (Update Imports)**: 2 hours
- **Phase 5 (Backend)**: 1 hour
- **Phase 6 (Docs)**: 30 minutes

**Total**: ~7 hours of careful refactoring

---

## Next Steps

Would you like me to:
1. **Create the automated refactoring script** to execute this plan?
2. **Start Phase 1 (Cleanup)** manually?
3. **Review and adjust the plan** before proceeding?

This refactoring will make the codebase look like a professional, enterprise-level project! 🚀
