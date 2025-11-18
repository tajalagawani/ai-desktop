# Flow Builder Architecture Diagram

This document explains how all the pieces fit together when you use the Flow Builder.

---

## 🎯 The Big Picture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         YOUR BROWSER                                │
│                     http://localhost:3005                           │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │                    Desktop UI (React)                      │    │
│  │  - File Manager                                            │    │
│  │  - Terminal                                                │    │
│  │  - Flow Builder  ← YOU CLICK HERE                         │    │
│  └───────────────────────────────────────────────────────────┘    │
│                              ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │            Flow Builder Chat Interface                     │    │
│  │  ┌─────────────────────────────────────────────────┐      │    │
│  │  │ You type: "Create a GitHub to Slack workflow"  │      │    │
│  │  └─────────────────────────────────────────────────┘      │    │
│  │                                                            │    │
│  │  ┌─────────────────────────────────────────────────┐      │    │
│  │  │ Agent: Discovering nodes...                     │      │    │
│  │  │ Agent: Generating workflow...                   │      │    │
│  │  │ Agent: ✓ Saved to github-slack.flow            │      │    │
│  │  └─────────────────────────────────────────────────┘      │    │
│  └───────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              ↕ WebSocket
┌─────────────────────────────────────────────────────────────────────┐
│                    DESKTOP APP SERVER                               │
│                 /Users/tajnoah/Downloads/ai-desktop                 │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │              Next.js Server (Port 3005)                   │     │
│  │  - Serves the desktop UI                                 │     │
│  │  - Handles API routes (/api/flow-builder/*)             │     │
│  │  - Manages WebSocket connections (Socket.IO)            │     │
│  │  - Stores sessions & messages in SQLite database        │     │
│  └──────────────────────────────────────────────────────────┘     │
│                              ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │         lib/flow-builder/agent-manager.js                │     │
│  │  - Receives your message                                 │     │
│  │  - Spawns agent process                                  │     │
│  │  - Streams output back via WebSocket                     │     │
│  └──────────────────────────────────────────────────────────┘     │
│                              ↓                                      │
│                      spawn('bash', [                                │
│                        'agent-sdk/debug-run.sh',                    │
│                        'your message'                               │
│                      ])                                             │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      AGENT SDK PROCESS                              │
│              /Users/tajnoah/Downloads/ai-desktop/agent-sdk          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │              debug-run.sh (Bash Script)                   │     │
│  │  - Wrapper script that adds logging                      │     │
│  │  - Calls: node index.js "your message"                   │     │
│  └──────────────────────────────────────────────────────────┘     │
│                              ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │              index.js (ES Module)                         │     │
│  │  - Main agent entry point                                │     │
│  │  - Uses @anthropic-ai/claude-agent-sdk                   │     │
│  │  - Loads .env file with:                                 │     │
│  │    • ANTHROPIC_API_KEY                                   │     │
│  │    • ACT_ROOT=/Users/tajnoah/act                         │     │
│  │    • MCP_SERVER_PATH=/Users/tajnoah/act/mcp/index.js    │     │
│  └──────────────────────────────────────────────────────────┘     │
│                              ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │         Claude Agent SDK (Autonomous Agent)               │     │
│  │  - Sends your request to Claude API                      │     │
│  │  - Claude decides what tools to call                     │     │
│  │  - Loops until workflow is complete                      │     │
│  └──────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                              ↕
                    Claude API (Anthropic)
                    api.anthropic.com
                              ↕
┌─────────────────────────────────────────────────────────────────────┐
│                    ACT MCP SERVER (External)                        │
│                      /Users/tajnoah/act/mcp                         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │               index.js (MCP Server)                       │     │
│  │  - Runs as separate process                              │     │
│  │  - Must be started BEFORE using Flow Builder             │     │
│  │  - Start: /Users/tajnoah/act/start-services.sh          │     │
│  └──────────────────────────────────────────────────────────┘     │
│                              ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │            MCP Tools (13 Available Tools)                 │     │
│  │                                                           │     │
│  │  1. list_available_nodes                                 │     │
│  │     Returns: 150+ node types (github, slack, etc.)       │     │
│  │                                                           │     │
│  │  2. search_operations                                    │     │
│  │     Query: "slack"                                       │     │
│  │     Returns: send_message, upload_file, etc.             │     │
│  │                                                           │     │
│  │  3. get_node_info                                        │     │
│  │     Input: "github"                                      │     │
│  │     Returns: All operations, parameters, auth needed     │     │
│  │                                                           │     │
│  │  4. get_signature_info                                   │     │
│  │     Returns: Which nodes are authenticated               │     │
│  │                                                           │     │
│  │  5. validate_params                                      │     │
│  │     Checks if parameters are correct                     │     │
│  │                                                           │     │
│  │  ... and 8 more tools                                    │     │
│  └──────────────────────────────────────────────────────────┘     │
│                              ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │         Node Catalog (150+ Workflow Nodes)                │     │
│  │                                                           │     │
│  │  Integration Nodes:                                      │     │
│  │    - github (10+ operations)                             │     │
│  │    - slack (8+ operations)                               │     │
│  │    - openai (5+ operations)                              │     │
│  │    - postgresql (12+ operations)                         │     │
│  │    - redis (15+ operations)                              │     │
│  │    - stripe (10+ operations)                             │     │
│  │    - sendgrid (4+ operations)                            │     │
│  │    ... 143 more nodes                                    │     │
│  │                                                           │     │
│  │  Logic Nodes:                                            │     │
│  │    - py (execute Python code)                            │     │
│  │    - condition (if/else logic)                           │     │
│  │    - loop (iterate over data)                            │     │
│  │    - transform (data manipulation)                       │     │
│  │                                                           │     │
│  │  Utility Nodes:                                          │     │
│  │    - http (API requests)                                 │     │
│  │    - json (parse/stringify)                              │     │
│  │    - text (string operations)                            │     │
│  │    - scheduler (cron jobs)                               │     │
│  └──────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     GENERATED OUTPUT                                │
│                                                                     │
│  File: /Users/tajnoah/act/flows/github-slack-monitor.flow         │
│                                                                     │
│  [workflow]                                                        │
│  name = "GitHub to Slack Monitor"                                 │
│  start_node = "FetchIssues"                                       │
│                                                                     │
│  [node:FetchIssues]                                               │
│  type = "github"                                                  │
│  operation = "list_issues"                                        │
│  repository = "owner/repo"                                        │
│  state = "open"                                                   │
│  next = "SendToSlack"                                             │
│                                                                     │
│  [node:SendToSlack]                                               │
│  type = "slack"                                                   │
│  operation = "send_message"                                       │
│  channel = "#alerts"                                              │
│  message = "New issues: {{FetchIssues.result}}"                  │
│                                                                     │
│  [node:Schedule]                                                  │
│  type = "scheduler"                                               │
│  operation = "cron"                                               │
│  schedule = "0 * * * *"  # Every hour                            │
│  trigger = "FetchIssues"                                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Step-by-Step Flow

### Step 1: User Sends Message
```
Browser → WebSocket → Desktop Server
"Create a GitHub to Slack workflow"
```

### Step 2: Desktop Server Spawns Agent
```
server.js
  ↓
agent-manager.js
  ↓
spawn('bash', ['agent-sdk/debug-run.sh', 'your message'])
```

### Step 3: Agent Process Starts
```
debug-run.sh (bash wrapper)
  ↓
node index.js "your message"
  ↓
Loads .env file (API key, paths)
  ↓
Creates Claude Agent SDK instance
```

### Step 4: Agent Calls Claude API
```
Agent SDK sends to Claude:
{
  model: "claude-sonnet-4-5",
  messages: [{
    role: "user",
    content: "Create a GitHub to Slack workflow"
  }],
  tools: [
    // 13 MCP tools from ACT server
    "list_available_nodes",
    "search_operations",
    "get_node_info",
    ...
  ]
}
```

### Step 5: Claude Decides What to Do
```
Claude thinks:
"I need to:
1. Find out what nodes are available
2. Search for GitHub and Slack operations
3. Get their parameters
4. Generate the workflow file"

Claude calls tools:
  Tool 1: list_available_nodes()
  Tool 2: search_operations({query: "github"})
  Tool 3: get_node_info({node_type: "github"})
  Tool 4: search_operations({query: "slack"})
  Tool 5: get_node_info({node_type: "slack"})
```

### Step 6: MCP Server Responds
```
MCP Server returns:
{
  github: {
    operations: [
      "list_issues",
      "create_issue",
      "list_repos",
      ...
    ],
    parameters: {
      list_issues: ["repository", "state", "labels"]
    }
  },
  slack: {
    operations: [
      "send_message",
      "upload_file",
      ...
    ],
    parameters: {
      send_message: ["channel", "message", "thread_ts"]
    }
  }
}
```

### Step 7: Agent Generates Workflow
```
Agent SDK (index.js):
  ↓
parseActFlow() - Validates TOML format
  ↓
Generates complete .flow file
  ↓
Saves to: /Users/tajnoah/act/flows/github-slack-monitor.flow
  ↓
Returns success message
```

### Step 8: Output Streams to Browser
```
Agent stdout/stderr
  ↓
agent-manager.js captures output
  ↓
Emits via Socket.IO: socket.emit('stream:chunk', {chunk: line})
  ↓
Browser receives and displays in chat
  ↓
User sees real-time progress!
```

---

## 🔄 Data Flow

### Message Flow
```
User Input (Browser)
  ↓ HTTP POST
Next.js API (/api/flow-builder/messages)
  ↓ Save to DB
SQLite Database (data/flow-builder.db)
  ↓ Trigger
agent-manager.js
  ↓ Spawn
Agent SDK Process
  ↓ Stream
Socket.IO WebSocket
  ↓ Display
Browser Chat Interface
```

### Tool Call Flow
```
Claude API
  ↓ Tool Call Request
Agent SDK (receives tool use block)
  ↓ Execute via MCP
MCP Server at /Users/tajnoah/act/mcp/index.js
  ↓ Query Catalog
Node Catalog (150+ nodes in lib/)
  ↓ Return Results
Back to Claude API
  ↓ Claude processes
Generates workflow content
```

---

## 🗂️ File System Structure

```
/Users/tajnoah/
│
├── Downloads/ai-desktop/          ← Desktop App
│   ├── server.js                  ← Next.js server (port 3005)
│   ├── lib/flow-builder/
│   │   ├── agent-manager.js       ← Spawns agent
│   │   └── db.ts                  ← SQLite database
│   │
│   ├── components/flow-builder/   ← React UI
│   │   ├── ChatInterface.tsx
│   │   ├── ChatInput.tsx
│   │   └── ChatMessage.tsx
│   │
│   ├── app/api/flow-builder/      ← API Routes
│   │   ├── sessions/
│   │   └── messages/
│   │
│   ├── agent-sdk/                 ← Local Agent (ES Module)
│   │   ├── index.js               ← Main agent
│   │   ├── debug-run.sh           ← Wrapper script
│   │   ├── package.json           ← Dependencies
│   │   ├── node_modules/          ← Agent dependencies
│   │   └── .env                   ← API key & paths
│   │
│   └── data/                      ← Database
│       └── flow-builder.db
│
└── act/                           ← ACT Installation (External)
    ├── mcp/                       ← MCP Server
    │   ├── index.js               ← MCP server entry
    │   ├── tools/                 ← 13 MCP tools
    │   ├── lib/                   ← Node catalog
    │   ├── signatures/            ← Auth credentials
    │   └── node_modules/          ← MCP dependencies
    │
    ├── flows/                     ← Generated Workflows
    │   ├── github-slack.flow
    │   ├── api-monitor.flow
    │   └── ...
    │
    ├── flow_manager_api.py        ← Python API (port 8000)
    ├── start-services.sh          ← Start MCP & API
    └── stop-services.sh           ← Stop services
```

---

## 🔌 Network Ports

| Port | Service | Purpose |
|------|---------|---------|
| **3005** | Desktop App (Next.js) | Main UI, WebSocket, API routes |
| **8000** | Python Flow Manager API | Flow management (optional) |
| **N/A** | MCP Server | Runs via stdio (no network port) |

---

## 🧠 Key Concepts

### 1. Why External Agent Process?
```
Desktop App (Next.js - CommonJS)
  ↓ Cannot directly import
Agent SDK (ES Modules)
  ✓ Solution: Spawn as separate process
```

**Benefits:**
- Module system compatibility
- Process isolation
- Independent crash recovery
- Easier debugging

### 2. Why MCP Server?
```
Agent needs to know:
  - What nodes exist? (150+ types)
  - What operations? (1000+ operations)
  - What parameters? (Complex validation)

Without MCP: Agent would need to guess or hardcode
With MCP: Agent queries dynamically, always up-to-date
```

### 3. Why Two Different Agents?
```
Claude Agent SDK (in agent-sdk/)
  - Autonomous workflow generation
  - Uses MCP tools
  - Generates .flow files

Claude CLI (user's terminal)
  - Interactive chat
  - Uses same MCP server
  - Can execute operations directly
```

They share the MCP server but serve different purposes!

### 4. Data Persistence
```
Sessions & Messages
  ↓ Stored in
SQLite Database (data/flow-builder.db)
  ↓ Schema
- sessions table (id, user_id, title, created_at)
- messages table (id, session_id, role, content, created_at)
```

Survives server restarts!

---

## 🚀 Complete Request Lifecycle

```
1. USER TYPES MESSAGE
   Browser: "Create GitHub to Slack workflow"

2. SAVE TO DATABASE
   POST /api/flow-builder/messages
   SQLite: INSERT INTO messages (role='USER', content='...')

3. SPAWN AGENT
   agent-manager.js: spawn('bash', ['agent-sdk/debug-run.sh', message])

4. AGENT STARTS
   debug-run.sh → node index.js
   Loads ANTHROPIC_API_KEY from .env

5. AGENT CALLS CLAUDE
   POST https://api.anthropic.com/v1/messages
   {
     model: "claude-sonnet-4-5",
     messages: [...],
     tools: [13 MCP tools]
   }

6. CLAUDE THINKS
   "I need to discover nodes first"
   Tool use: list_available_nodes()

7. MCP SERVER RESPONDS
   Returns: [github, slack, openai, ...] (150+ nodes)

8. CLAUDE SEARCHES
   Tool use: search_operations({query: "github"})
   MCP returns: ["list_issues", "create_issue", ...]

9. CLAUDE GETS DETAILS
   Tool use: get_node_info({node_type: "github"})
   MCP returns: Full operation specs

10. CLAUDE GENERATES
    Creates complete .flow file content in TOML format

11. AGENT SAVES FILE
    writeFile('/Users/tajnoah/act/flows/github-slack.flow', content)

12. AGENT OUTPUTS
    stdout: "✓ Saved to github-slack.flow"

13. STREAM TO BROWSER
    agent-manager.js captures stdout
    socket.emit('stream:chunk', {chunk: line})

14. BROWSER DISPLAYS
    ChatMessage component renders:
    "✓ Workflow saved to github-slack.flow"

15. SAVE AGENT RESPONSE
    POST /api/flow-builder/messages
    SQLite: INSERT INTO messages (role='ASSISTANT', content='...')

16. DONE!
    User sees completed workflow
    File exists on disk
    Session saved in database
```

---

## 🎬 Analogy

Think of it like ordering food delivery:

- **Browser (You)**: Customer who orders food
- **Desktop Server**: Restaurant that takes your order
- **Agent Manager**: Kitchen manager who assigns chefs
- **Agent SDK**: Chef who cooks your food
- **Claude API**: Recipe database the chef consults
- **MCP Server**: Pantry with all ingredients (150+ nodes)
- **Generated .flow File**: Your completed meal

The restaurant doesn't cook the food itself—it has a dedicated chef (agent) who:
1. Checks what ingredients are available (MCP)
2. Consults recipes (Claude API)
3. Cooks the meal (generates workflow)
4. Delivers it (saves .flow file)

---

## 🛠️ Troubleshooting Map

```
Problem: Agent not responding
  ↓
Check: Is MCP server running?
  → No: Run /Users/tajnoah/act/start-services.sh
  → Yes: Check logs at /tmp/act-mcp.log

Problem: "API key not found"
  ↓
Check: agent-sdk/.env has ANTHROPIC_API_KEY?
  → No: Add your API key
  → Yes: Restart desktop server

Problem: "Node not found"
  ↓
Check: MCP server running?
  → No: Start it
  → Yes: Check MCP logs for errors

Problem: No output streaming
  ↓
Check: WebSocket connected in browser console?
  → No: Refresh browser
  → Yes: Check agent-manager.js logs

Problem: File not saved
  ↓
Check: /Users/tajnoah/act/flows/ exists?
  → No: mkdir -p /Users/tajnoah/act/flows
  → Yes: Check file permissions
```

---

## 📚 Summary

**The Flow Builder works like this:**

1. You type a message in the browser
2. Desktop server spawns a local agent
3. Agent asks Claude to generate a workflow
4. Claude calls MCP server to discover available nodes
5. MCP server returns node catalog (150+ types)
6. Claude generates complete workflow file
7. Agent saves file to disk
8. Output streams back to your browser in real-time
9. You see the completed workflow!

**All running locally on your Mac, with Claude API calls for intelligence!**
