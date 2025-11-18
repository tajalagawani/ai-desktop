# MCP Hub - Universal MCP Server Manager

## 🎯 Concept

An app that works exactly like **Service Manager** and **VS Code Manager**, but for **MCP servers**.

### Inspiration
- **Service Manager**: Manages Docker services (MySQL, Redis, etc.)
- **VS Code Manager**: Manages code repositories and deployments
- **MCP Hub**: Manages MCP servers and their tools

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         MCP HUB APP                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SIDEBAR                          MAIN PANEL                │
│  ┌──────────────────┐            ┌─────────────────────┐   │
│  │ 📦 All MCPs      │            │  MCP Details        │   │
│  │ ⚡ Running (3)   │            │  ┌───────────────┐  │   │
│  │ ⏸  Stopped (1)   │            │  │ ACT Workflow  │  │   │
│  ├──────────────────┤            │  │ ✓ Running     │  │   │
│  │ Built-in:        │            │  │ 150+ Tools    │  │   │
│  │ • ACT Workflow ✓ │            │  └───────────────┘  │   │
│  │                  │            │                     │   │
│  │ Custom:          │            │  [Tabs]             │   │
│  │ • Filesystem     │            │  • Overview         │   │
│  │ • Database       │            │  • Tools (13)       │   │
│  │ • GitHub         │            │  • Test Playground  │   │
│  │ [+ Add MCP]      │            │  • Logs             │   │
│  └──────────────────┘            └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Features (Mirror of Service Manager)

### Sidebar Categories
1. **All MCPs** - Shows all configured MCP servers
2. **Running** - Active MCP servers
3. **Stopped** - Inactive MCP servers
4. **Built-in** - Pre-configured MCPs (ACT is default)
5. **Custom** - User-added MCPs

### MCP Card (Like Service Card)
```
┌──────────────────────────────────────┐
│ 🔧 ACT Workflow MCP                  │
│ ✓ Running    Port: stdio    13 Tools │
├──────────────────────────────────────┤
│ Location: /var/www/act/mcp          │
│ Type: Node.js                        │
│ Tools: list_nodes, execute_op, ...  │
├──────────────────────────────────────┤
│ [⏹️ Stop] [🔄 Restart] [📊 Stats]    │
└──────────────────────────────────────┘
```

### Detail View Tabs (Like VS Code Manager)

#### 1. **Overview Tab**
- MCP server information
- Status (running/stopped)
- Connection type (stdio/http)
- Path to server
- Number of tools available
- Start/Stop/Restart buttons

#### 2. **Tools Tab** (Main Feature!)
Shows all available tools from this MCP:

```
┌─────────────────────────────────────────────┐
│ Search tools...               [🔍]          │
├─────────────────────────────────────────────┤
│ Tool Discovery (3 tools)                    │
│ • list_available_nodes                      │
│   📝 Get all 150+ workflow nodes            │
│                                              │
│ • search_operations                         │
│   📝 Search nodes by keyword                │
│                                              │
│ • get_node_info                            │
│   📝 Get detailed node information          │
├─────────────────────────────────────────────┤
│ Execution (1 tool)                          │
│ • execute_node_operation                    │
│   📝 Run a workflow operation               │
├─────────────────────────────────────────────┤
│ Signature Management (4 tools)              │
│ • get_signature_info                        │
│ • add_node_to_signature                     │
│ • remove_node_from_signature                │
│ • validate_signature                        │
└─────────────────────────────────────────────┘
```

#### 3. **Test Playground Tab** (Interactive!)
Like Claude Desktop's MCP testing, but in the UI:

```
┌─────────────────────────────────────────────┐
│ Select Tool:                                │
│ [list_available_nodes        ▼]            │
├─────────────────────────────────────────────┤
│ Parameters (JSON):                          │
│ {                                           │
│   "category": "integration"                 │
│ }                                           │
├─────────────────────────────────────────────┤
│ [▶️ Execute Tool]                           │
├─────────────────────────────────────────────┤
│ Response:                                   │
│ {                                           │
│   "nodes": [                                │
│     {"type": "github", "ops": 10},          │
│     {"type": "slack", "ops": 8},            │
│     ...                                     │
│   ]                                         │
│ }                                           │
└─────────────────────────────────────────────┘
```

#### 4. **Logs Tab** (Real-time WebSocket)
Shows MCP server output in real-time:
```
[2025-11-18 20:00:00] MCP Server started
[2025-11-18 20:00:01] Loaded 150 nodes
[2025-11-18 20:00:02] Tool called: list_available_nodes
[2025-11-18 20:00:03] Returned 150 nodes
```

#### 5. **Settings Tab**
- Edit MCP configuration
- Environment variables
- Command override
- Args customization

---

## 🔧 Built-in MCPs

### ACT Workflow (Default, Always Available)
```json
{
  "id": "act-workflow",
  "name": "ACT Workflow MCP",
  "description": "150+ workflow automation nodes",
  "type": "built-in",
  "command": "node",
  "args": ["/var/www/act/mcp/index.js"],
  "env": {},
  "tools": 13,
  "category": "workflow"
}
```

### More Built-in MCPs (Future)
- **Filesystem MCP** - File operations
- **Database MCP** - SQL queries
- **GitHub MCP** - Git operations
- **Fetch MCP** - HTTP requests

---

## 🎨 UI Components Structure

```typescript
// Main Component
components/apps/mcp-hub.tsx

// Sub-components (like VS Code Manager structure)
components/apps/mcp/
├── mcp-card.tsx              // Like service card
├── mcp-detail.tsx            // Detail view with tabs
├── add-mcp-dialog.tsx        // Add custom MCP
├── delete-mcp-dialog.tsx     // Delete confirmation
├── tool-list.tsx             // Shows all tools
├── tool-playground.tsx       // Interactive testing
├── tool-execution.tsx        // Execute tool UI
└── mcp-logs.tsx              // Real-time logs

// API Routes
app/api/mcp/
├── route.ts                  // List MCPs, Create MCP
├── [id]/route.ts             // Get/Update/Delete MCP
├── [id]/action/route.ts      // Start/Stop/Restart
├── [id]/tools/route.ts       // List tools
├── [id]/execute/route.ts     // Execute tool
└── logs/ws/route.ts          // WebSocket logs
```

---

## 💾 Data Storage

### MCP Registry
**Location**: `/var/www/ai-desktop/data/mcp-servers.json`

```json
{
  "servers": [
    {
      "id": "act-workflow",
      "name": "ACT Workflow MCP",
      "description": "150+ workflow automation nodes",
      "type": "built-in",
      "command": "node",
      "args": ["/var/www/act/mcp/index.js"],
      "cwd": "/var/www/act/mcp",
      "env": {},
      "status": "running",
      "pm2Name": "mcp-act-workflow",
      "toolCount": 13,
      "addedAt": "2025-11-18T00:00:00.000Z",
      "lastStarted": "2025-11-18T00:05:00.000Z"
    },
    {
      "id": "filesystem",
      "name": "Filesystem MCP",
      "description": "File system operations",
      "type": "custom",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/tajnoah"],
      "cwd": null,
      "env": {},
      "status": "stopped",
      "pm2Name": "mcp-filesystem",
      "toolCount": 8,
      "addedAt": "2025-11-18T01:00:00.000Z"
    }
  ]
}
```

---

## 🔄 MCP Lifecycle Management

### Start MCP
```bash
# Via PM2 (for persistence)
pm2 start node --name "mcp-act-workflow" -- /var/www/act/mcp/index.js

# Store in registry with status="running"
```

### Stop MCP
```bash
pm2 stop mcp-act-workflow
# Update registry status="stopped"
```

### Restart MCP
```bash
pm2 restart mcp-act-workflow
```

### Delete MCP
```bash
pm2 delete mcp-act-workflow
# Remove from registry
```

---

## 🛠️ Tool Discovery & Execution

### How It Works

1. **MCP Server Starts** → Connect via stdio
2. **Send Initialization** → MCP returns capabilities
3. **List Tools** → `list_tools` request
4. **MCP Responds** → Tool schemas
5. **Store in Cache** → Fast UI updates
6. **User Executes** → `call_tool` request
7. **MCP Processes** → Returns result
8. **Display in UI** → Show result with syntax highlighting

### Tool Execution Flow

```
User clicks "Execute" in UI
  ↓
POST /api/mcp/{id}/execute
  ↓
MCP Manager spawns temp connection
  ↓
Sends tool_call via MCP protocol
  ↓
MCP server processes
  ↓
Returns result
  ↓
Format and return to UI
  ↓
Display with syntax highlighting
```

---

## 🎯 Key Features

### 1. **One-Click ACT MCP** (Pre-configured)
- No setup needed
- Already connected to /var/www/act/mcp
- All 150+ nodes available immediately
- Can test tools directly in UI

### 2. **Add Any MCP Server**
```
[+ Add MCP Server]

Name: My Custom MCP
Command: npx
Args: -y @org/server-name /path
Environment Variables:
  API_KEY=...

[Add]
```

### 3. **Interactive Tool Testing**
- Select any tool
- Enter parameters (JSON editor with autocomplete)
- Execute and see results
- Copy result to clipboard
- Share tool configurations

### 4. **Real-time Logs**
- WebSocket connection to MCP stdout/stderr
- Filter by level (info/warn/error)
- Search logs
- Download logs

### 5. **Tool Documentation**
- Auto-generated from MCP schema
- Parameter descriptions
- Example requests/responses
- Copy example to playground

---

## 🎨 UI/UX Details

### MCP Status Badges
```tsx
{status === 'running' && <Badge className="bg-green-500">✓ Running</Badge>}
{status === 'stopped' && <Badge className="bg-gray-500">⏸ Stopped</Badge>}
{status === 'error' && <Badge className="bg-red-500">✗ Error</Badge>}
{status === 'starting' && <Badge className="bg-yellow-500">⏳ Starting...</Badge>}
```

### Tool Categories
- 🔍 Discovery
- ⚡ Execution
- 🔐 Authentication
- ✅ Validation
- 📦 Data
- 🔧 Utility

### Quick Actions
- ▶️ Start
- ⏹️ Stop
- 🔄 Restart
- 🗑️ Delete
- 📊 View Stats
- ⚙️ Settings

---

## 🚀 Implementation Plan

### Phase 1: Core Infrastructure
- [ ] Create MCP registry storage
- [ ] Build MCP manager (start/stop/restart)
- [ ] API routes for MCP operations
- [ ] PM2 integration

### Phase 2: UI Components
- [ ] Main MCP Hub component
- [ ] Sidebar with categories
- [ ] MCP cards
- [ ] Detail view with tabs

### Phase 3: Tool Management
- [ ] Tool discovery from MCP
- [ ] Tool list display
- [ ] Tool documentation view
- [ ] Tool execution playground

### Phase 4: Built-in MCPs
- [ ] ACT Workflow MCP (default)
- [ ] Auto-detect /var/www/act/mcp
- [ ] Pre-configure on first launch
- [ ] Auto-start with desktop app

### Phase 5: Custom MCPs
- [ ] Add custom MCP dialog
- [ ] Validate MCP command
- [ ] Test connection
- [ ] Save to registry

### Phase 6: Advanced Features
- [ ] Real-time logs (WebSocket)
- [ ] Tool execution history
- [ ] Export/Import MCP configs
- [ ] MCP marketplace

---

## 📊 Comparison with Other Apps

| Feature | Service Manager | VS Code Manager | MCP Hub |
|---------|----------------|-----------------|---------|
| **Manages** | Docker services | Git repositories | MCP servers |
| **Categories** | Database, Cache, Queue | All, Git, Deployments | Built-in, Custom, Running |
| **Actions** | Start/Stop/Restart | Start/Stop/Deploy | Start/Stop/Restart/Test |
| **Detail View** | Overview, Logs, Terminal | Overview, Deploy, Changes | Overview, Tools, Playground, Logs |
| **Real-time** | WebSocket logs | Git changes | Tool execution, Logs |
| **Built-in** | 20+ services | None | ACT Workflow |

---

## 🎯 Use Cases

### 1. **Flow Builder Development**
- ACT MCP always available
- Test node operations before using in flows
- Debug signature issues
- View available nodes

### 2. **Multi-MCP Workflows**
- Use ACT for workflows
- Use GitHub MCP for repo access
- Use Database MCP for queries
- All managed in one place

### 3. **MCP Server Development**
- Test your own MCP server
- Debug tool responses
- Monitor logs in real-time
- Iterate quickly

### 4. **Claude Desktop Alternative**
- Manage MCPs without editing JSON
- Visual tool browser
- Interactive testing
- Better debugging

---

## 🔐 Security

- MCP servers run in isolated PM2 processes
- Environment variables stored server-side only
- Tool execution requires confirmation for destructive actions
- Rate limiting on tool execution
- Logs sanitized (no secrets)

---

## 🎉 Benefits

1. **No More JSON Editing** - Visual MCP management
2. **ACT Always Ready** - Pre-configured and running
3. **Test Tools Instantly** - No need for Claude CLI
4. **Debug Easily** - Real-time logs and execution history
5. **Unified Interface** - All MCPs in one place
6. **Production Ready** - PM2 process management
7. **VPS Compatible** - Works on server and local

---

## 🚀 Getting Started (After Implementation)

### Local Mac
```bash
# Desktop app auto-detects /Users/tajnoah/act/mcp
# ACT MCP starts automatically
# Open MCP Hub → ACT Workflow → ✓ Running
```

### VPS
```bash
# Desktop app auto-detects /var/www/act/mcp
# ACT MCP starts automatically via PM2
# Access at http://VPS_IP:3005 → MCP Hub
```

---

## 💡 Future Enhancements

- [ ] MCP Marketplace (browse and install)
- [ ] Tool composition (chain multiple tools)
- [ ] Scheduled tool execution
- [ ] Tool result caching
- [ ] MCP analytics (most used tools)
- [ ] Share MCP configurations
- [ ] Tool templates
- [ ] Integration with Flow Builder (drag tools into flows)

---

## 🎬 Demo Flow

1. User opens MCP Hub
2. Sees ACT Workflow MCP running
3. Clicks on it → Detail view opens
4. Goes to "Tools" tab → Sees 13 tools
5. Clicks on "list_available_nodes"
6. Tool detail opens with description
7. Clicks "Test in Playground"
8. Playground opens with empty params: `{}`
9. Clicks "Execute"
10. Result shows: 150+ nodes with categories
11. Copies result → Uses in Flow Builder
12. Success! 🎉

---

## 🎯 Why This is Brilliant

1. **Solves ACT Integration** - ACT MCP is always available
2. **Mirrors Existing UX** - Users already know how to use it
3. **Extensible** - Can add any MCP server
4. **Visual** - No more JSON config files
5. **Powerful** - Test tools without Claude
6. **Production Ready** - PM2 management built-in
7. **Universal** - Works everywhere (Mac, VPS)

This makes MCP servers as easy to use as Docker services! 🚀
