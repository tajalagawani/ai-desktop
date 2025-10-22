# Desktop App Integration TODO

## 🎯 Priority 1: Core Signature Management

### Task 1.1: Signature File Manager Component
**Location**: Desktop app frontend

**UI Components Needed:**
- [ ] Signature file selector/creator
- [ ] Node authentication form
  - Input: Node type (dropdown from 129 nodes)
  - Input: Auth fields (dynamic based on node)
  - Input: Default parameters (optional)
- [ ] Authenticated nodes list view
- [ ] Remove authentication button
- [ ] Edit defaults button

**Backend API:**
```javascript
// Use act.mcp_utils.signature_manager
POST /api/signature/auth/add
GET /api/signature/auth/list
DELETE /api/signature/auth/:nodeType
PATCH /api/signature/auth/:nodeType/defaults
```

---

## 🎯 Priority 2: Node & Operation Browser

### Task 2.1: Node Catalog View
**Location**: Desktop app frontend

**Features:**
- [ ] Grid/List view of 129 nodes
- [ ] Category filter (ai, database, api, developer, storage)
- [ ] Search by name/description
- [ ] Node card showing:
  - Display name
  - Description
  - Auth status (authenticated ✅ or not ❌)
  - Category tags

**Data Source:**
```javascript
// Use cached catalog or call Python
const nodes = await fetch('/api/catalog/nodes');
// Or: python3 -m act.mcp_utils.catalog_sync list
```

### Task 2.2: Operation Browser
**Location**: Desktop app - node detail page

**Features:**
- [ ] List operations for selected node (16+ per node)
- [ ] Operation card showing:
  - Display name
  - Method (GET/POST/PUT/DELETE)
  - Endpoint
  - Required params count
  - Description
- [ ] Click operation → show full details

**Data Source:**
```javascript
const ops = await fetch(`/api/catalog/nodes/${nodeType}/operations`);
// Or: python3 -m act.mcp_utils.list_operations list github
```

### Task 2.3: Operation Details View
**Location**: Desktop app - operation detail modal

**Display:**
- [ ] Operation name & description
- [ ] HTTP method & endpoint
- [ ] Required parameters (with types)
- [ ] Optional parameters (with types)
- [ ] Body parameters
- [ ] Response type
- [ ] Rate limit cost
- [ ] Example usage
- [ ] "Execute Now" button → execution form

**Data Source:**
```javascript
const details = await fetch(`/api/catalog/nodes/${nodeType}/operations/${operation}`);
// Or: python3 -m act.mcp_utils.list_operations get github get_repo
```

---

## 🎯 Priority 3: Operation Execution

### Task 3.1: Execution Form
**Location**: Desktop app - execution modal

**Features:**
- [ ] Pre-populate parameters from signature defaults
- [ ] Dynamic form based on operation parameters
- [ ] Parameter type validation (string, number, boolean, array)
- [ ] Required field indicators
- [ ] "Execute" button
- [ ] Loading state during execution
- [ ] Result display

**Backend:**
```javascript
POST /api/nodes/execute
Body: {
  node_type: "github",
  operation: "get_repo",
  params: { owner: "octocat", repo: "hello-world" }
}

// Uses: python3 -m act.mcp_utils.single_node_executor
```

### Task 3.2: Result Viewer
**Features:**
- [ ] JSON formatted output
- [ ] Syntax highlighting
- [ ] Copy to clipboard
- [ ] Export as JSON file
- [ ] Error display with helpful messages
- [ ] Execution duration
- [ ] Timestamp

---

## 🎯 Priority 4: Workflow Builder Integration

### Task 4.1: Update Node Picker
**Current**: Hardcoded node list
**New**: Dynamic from catalog (129 nodes)

**Changes:**
- [ ] Replace static list with catalog API call
- [ ] Show all 129 nodes in picker
- [ ] Category-based grouping
- [ ] Search/filter in picker

### Task 4.2: Update Operation Selector
**Current**: Hardcoded operations
**New**: Dynamic from catalog (16+ operations per node)

**Changes:**
- [ ] When node selected, fetch operations
- [ ] Show all available operations
- [ ] Display: method, description, params

### Task 4.3: Parameter Auto-fill
**Feature**: Pre-fill params from signature

**Changes:**
- [ ] When operation selected, check if node is authenticated
- [ ] Load default parameters from signature
- [ ] Pre-fill form fields
- [ ] Show which params are from signature defaults
- [ ] Allow override

---

## 🎯 Priority 5: Environment Variables

### Task 5.1: Environment Variable Manager
**Location**: Desktop app settings

**Features:**
- [ ] List all environment variables
- [ ] Add new variable
- [ ] Edit variable
- [ ] Delete variable
- [ ] Mark as sensitive (hide value)
- [ ] Used in signatures as: `{{.env.VARIABLE_NAME}}`

**Implementation:**
```javascript
// Store in .env file or app config
// act.mcp_utils.signature_manager resolves {{.env.VAR}} automatically
```

### Task 5.2: Signature Editor with Env Var Support
**Feature**: When adding auth, suggest using env vars

**UI:**
```
Access Token: [input field]
              [ ] Use environment variable
                  {{.env.GITHUB_TOKEN}}
```

---

## 📝 Implementation Checklist

### Backend Integration
- [ ] Create HTTP API routes for signature management
- [ ] Create HTTP API routes for catalog access
- [ ] Create HTTP API route for node execution
- [ ] Add error handling & logging
- [ ] Add rate limiting for execution endpoint
- [ ] Add execution history/audit log

### Frontend Components
- [ ] SignatureManager component
- [ ] NodeBrowser component
- [ ] OperationBrowser component
- [ ] OperationDetails component
- [ ] ExecutionForm component
- [ ] ResultViewer component
- [ ] EnvironmentVariableManager component

### Testing
- [ ] Test signature CRUD operations
- [ ] Test node browsing & search
- [ ] Test operation execution with real APIs
- [ ] Test error handling
- [ ] Test with multiple authenticated nodes
- [ ] Test environment variable resolution

### Documentation
- [ ] User guide for signature system
- [ ] API documentation
- [ ] Example workflows using signatures
- [ ] Troubleshooting guide

---

## 🚧 Known Limitations & Future Work

### Current Limitations
- Signature file is local only (not synced across devices)
- No multi-user support
- No signature encryption at rest
- No credential rotation
- No audit log for executed operations

### Future Enhancements
- [ ] Cloud sync for signatures
- [ ] Team signature sharing
- [ ] Signature encryption with master password
- [ ] Credential expiration & rotation reminders
- [ ] Execution audit log with search
- [ ] Usage analytics per node
- [ ] Cost tracking for paid APIs
- [ ] Batch operation execution
- [ ] Scheduled operations (cron-like)

---

## 📊 Estimated Timeline

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Signature Management | 1.1 | 4-6 hours |
| Phase 2: Node Browser | 2.1, 2.2, 2.3 | 8-10 hours |
| Phase 3: Execution | 3.1, 3.2 | 6-8 hours |
| Phase 4: Workflow Integration | 4.1, 4.2, 4.3 | 6-8 hours |
| Phase 5: Env Variables | 5.1, 5.2 | 4-6 hours |
| Testing & Polish | All | 8-10 hours |
| **Total** | | **36-48 hours** |

---

**Next Session**: Start with Priority 1 (Signature Management UI)
