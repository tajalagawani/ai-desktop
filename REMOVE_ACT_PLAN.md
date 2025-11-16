# Complete ACT/Workflow Removal Plan

## Files to Remove

### 1. ACT Docker Components
```bash
rm -rf ./components/apps/act-docker/
rm -rf ./temp-act-executions/
rm -rf ./.act-workflows/
```

### 2. Workflow/Flow Components
```bash
rm -f ./components/apps/flow-list-item.tsx
rm -f ./components/apps/flow-list.tsx
rm -f ./components/apps/flow-manager.tsx
rm -f ./components/apps/workflow-canvas.tsx
```

### 3. API Routes
```bash
rm -rf ./app/api/flows/
```

### 4. Signature System (ACT related)
```bash
rm -rf ./signature-system/
```

### 5. Data Files to Clean
- Remove workflow/flow apps from desktop-apps.ts
- Remove workflow-related services from all-services.ts

### 6. Update Files
- components/desktop/desktop.tsx (remove workflow component mapping)
- data/desktop-apps.ts (remove workflows and flow-manager from dock)
- server.js (already clean - no ACT references)

## Apps to Keep
- Terminal
- Claude CLI
- System Monitor
- File Manager
- Service Manager
- System Widgets
- Desktop Settings
- Changelog

## Apps to Remove
- Workflows (canvas)
- Flow Manager
