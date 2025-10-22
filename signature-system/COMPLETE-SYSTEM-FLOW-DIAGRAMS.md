# ACT Signature System - Complete Flow Diagram

**Visual representation of the entire system from user to execution**

---

## ⚠️ CRITICAL CORRECTION: MCP Tools, Not API Calls!

**IMPORTANT:** Signature operations (get, add, remove) should be **MCP tools**, NOT API calls!

**Why?**
- ✅ MCP Server can read/write files directly
- ✅ No unnecessary HTTP layer
- ✅ Faster and simpler
- ✅ Everything Claude needs should be an MCP tool

**Corrected Architecture:**
```
Claude → MCP Tool (get_signature_info) → Direct file read → Response
  (NOT: Claude → MCP → API Call → API Handler → Response → Response)
```

**All signature operations are MCP tools:**
- `get_signature_info()` - Read signature file directly
- `add_node_to_signature()` - Write to signature file directly
- `remove_node_from_signature()` - Modify signature file directly
- `list_available_nodes()` - Read node catalog directly
- `validate_signature()` - Validate signature format directly

**API calls are ONLY used when we need Python execution** (for node operations and workflows).

---

## 🎯 Table of Contents

1. [High-Level System Overview](#high-level-system-overview)
2. [Detailed Flow: Simple Operation](#detailed-flow-simple-operation)
3. [Detailed Flow: Complex Workflow](#detailed-flow-complex-workflow)
4. [Signature Creation Flow](#signature-creation-flow)
5. [Node Authentication Flow](#node-authentication-flow)
6. [Execution Manager Flow](#execution-manager-flow)
7. [Data Flow Architecture](#data-flow-architecture)
8. [File System Architecture](#file-system-architecture)
9. [API Layer Architecture](#api-layer-architecture)
10. [Complete System Interaction](#complete-system-interaction)

---

## 🎯 1. High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER LAYER                                 │
│                                                                         │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐  │
│  │   Web UI     │         │  Claude CLI  │         │   Claude     │  │
│  │  (Settings)  │         │  (Terminal)  │         │  (Chat AI)   │  │
│  └──────┬───────┘         └──────┬───────┘         └──────┬───────┘  │
│         │                        │                        │           │
└─────────┼────────────────────────┼────────────────────────┼───────────┘
          │                        │                        │
          │ Authenticate Nodes     │ Execute Commands       │ Read Signature
          │                        │                        │
┌─────────▼────────────────────────▼────────────────────────▼───────────┐
│                          INTERFACE LAYER                               │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              Flow Architect MCP Server                       │    │
│  │                                                              │    │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │    │
│  │  │ execute_node_  │  │ execute_flow   │  │ manage_      │ │    │
│  │  │ operation      │  │                │  │ signature    │ │    │
│  │  └────────┬───────┘  └────────┬───────┘  └──────┬───────┘ │    │
│  └───────────┼──────────────────┼──────────────────┼─────────┘    │
│              │                  │                  │               │
└──────────────┼──────────────────┼──────────────────┼───────────────┘
               │                  │                  │
               │ Single Node      │ Full Workflow    │ CRUD Operations
               │                  │                  │
┌──────────────▼──────────────────▼──────────────────▼───────────────┐
│                        SIGNATURE LAYER                              │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              user.act.sig (TOML)                           │   │
│  │                                                            │   │
│  │  [node:github]                                            │   │
│  │  authenticated = true                                     │   │
│  │  access_token = "{{.env.GITHUB_TOKEN}}"                  │   │
│  │  operations = [list_issues, create_repo, ...]           │   │
│  │                                                            │   │
│  │  [node:openai]                                            │   │
│  │  authenticated = true                                     │   │
│  │  api_key = "{{.env.OPENAI_API_KEY}}"                    │   │
│  │  operations = [chat, completion, ...]                    │   │
│  │                                                            │   │
│  │  [node:neon]                                              │   │
│  │  authenticated = true                                     │   │
│  │  connection_string = "{{.env.DATABASE_URL}}"            │   │
│  └────────────────┬───────────────────────────────────────────┘   │
│                   │                                               │
└───────────────────┼───────────────────────────────────────────────┘
                    │
                    │ Parse & Validate
                    │
┌───────────────────▼───────────────────────────────────────────────┐
│                      PARSING LAYER                                │
│                                                                   │
│  ┌──────────────────┐         ┌──────────────────┐              │
│  │ SignatureParser  │         │  ActfileParser   │              │
│  │  (.act.sig)      │         │  (.act files)    │              │
│  └────────┬─────────┘         └────────┬─────────┘              │
│           │                            │                         │
│           │ Node Config                │ Workflow Config         │
│           │                            │                         │
└───────────┼────────────────────────────┼─────────────────────────┘
            │                            │
            │                            │
┌───────────▼────────────────────────────▼─────────────────────────┐
│                    EXECUTION LAYER                               │
│                                                                  │
│  ┌──────────────────────┐       ┌──────────────────────┐       │
│  │ SingleNodeExecutor   │       │  ExecutionManager    │       │
│  │ (Simple Operations)  │       │  (Full Workflows)    │       │
│  └──────────┬───────────┘       └──────────┬───────────┘       │
│             │                              │                    │
│             │ Single Node                  │ Multiple Nodes     │
│             │                              │ Parallel/Sequential│
│             │                              │                    │
└─────────────┼──────────────────────────────┼────────────────────┘
              │                              │
              │                              │
┌─────────────▼──────────────────────────────▼────────────────────┐
│                       NODE LAYER                                │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ GitHub   │  │ OpenAI   │  │   Neon   │  │  Stripe  │      │
│  │  Node    │  │  Node    │  │   Node   │  │   Node   │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │             │             │             │
│       │ Uses        │ Uses        │ Uses        │ Uses        │
│       ▼             ▼             ▼             ▼             │
│  ┌──────────────────────────────────────────────────────┐    │
│  │       UniversalRequestNode                           │    │
│  │       (HTTP/Auth/Retry/RateLimit)                    │    │
│  └────────────────────────┬─────────────────────────────┘    │
│                           │                                   │
└───────────────────────────┼───────────────────────────────────┘
                            │
                            │ HTTP Requests
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                     EXTERNAL APIS                             │
│                                                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ GitHub  │  │ OpenAI  │  │  Neon   │  │ Stripe  │        │
│  │   API   │  │   API   │  │   API   │  │   API   │        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 🎯 2. Detailed Flow: Simple Operation

### **User Request: "List my GitHub issues"**

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: User Input                                                  │
└─────────────────────────────────────────────────────────────────────┘

User: "List my open GitHub issues"
  │
  │ (types command in Claude CLI or chat)
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Claude Analyzes Request                                     │
└─────────────────────────────────────────────────────────────────────┘

Claude:
  1. Parses request: "list", "github", "issues", "open"
  2. Identifies: This is a SIMPLE operation (single API call)
  3. Checks: Is user.act.sig available? ✅
  4. Reads: user.act.sig
  │
  │ File Contents:
  │ [node:github]
  │ authenticated = true
  │ operations = ["list_issues", ...]
  │
  5. Confirms: GitHub is authenticated ✅
  6. Confirms: list_issues operation available ✅
  7. Gets defaults: owner="myuser", repo="myrepo"
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Claude Calls MCP Tool                                       │
└─────────────────────────────────────────────────────────────────────┘

Claude executes:
  execute_node_operation({
    node_type: "github",
    operation: "list_issues",
    params: {
      state: "open"  // Runtime parameter from user request
    }
  })
  │
  │ (MCP tool call via stdio)
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: MCP Server Processes Request (DIRECT FILE ACCESS)           │
└─────────────────────────────────────────────────────────────────────┘

Flow Architect MCP Server:
  │
  1. Receives tool call
  │
  2. Reads signature file DIRECTLY (no API call!)
  │  const fs = require('fs/promises')
  │  const toml = require('@iarna/toml')
  │  const content = await fs.readFile('signatures/user.act.sig', 'utf-8')
  │  const signature = toml.parse(content)
  │
  3. Validates node authentication
  │  const nodeKey = `node:${node_type}`
  │  if (!signature[nodeKey]?.authenticated) {
  │    return error
  │  }
  │
  4. Validates operation
  │  const operations = signature[`${nodeKey}.operations`]
  │  if (!operations[operation]) {
  │    return error
  │  }
  │
  5. Gets node defaults
  │  defaults = signature[`${nodeKey}.defaults`]
  │  // {owner: "myuser", repo: "myrepo"}
  │
  6. Gets node auth
  │  auth = signature[`${nodeKey}.auth`]
  │  // {access_token: "{{.env.GITHUB_TOKEN}}"}
  │  // Resolve env var:
  │  auth.access_token = process.env.GITHUB_TOKEN
  │
  7. Merges parameters
  │  finalParams = {
  │    ...defaults,        // owner, repo
  │    ...auth,            // access_token (resolved)
  │    ...runtimeParams    // state: "open"
  │  }
  │
  8. Calls Flow Architect API (ONLY for Python execution)
  │  POST /api/node/execute
  │  {
  │    node_type: "github",
  │    operation: "list_issues",
  │    params: finalParams
  │  }
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: API Layer Processes Request                                 │
└─────────────────────────────────────────────────────────────────────┘

Flow Architect API (/api/node/execute):
  │
  1. Receives HTTP POST
  │
  2. Validates request body
  │
  3. Spawns Python process
  │  python execute_single_node.py \
  │    --node-type github \
  │    --operation list_issues \
  │    --params '{"state":"open","owner":"myuser",...}'
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: Python Execution Layer                                      │
└─────────────────────────────────────────────────────────────────────┘

SingleNodeExecutor (Python):
  │
  1. Parses command line arguments
  │
  2. Loads signature parser
  │  parser = ActSignatureParser('user.act.sig')
  │  parser.parse()
  │
  3. Validates authentication (again for security)
  │  if not parser.is_node_authenticated('github'):
  │    return error
  │
  4. Gets node class from registry
  │  node_class = NodeRegistry.get('github')
  │  // Returns: GitHubNode
  │
  5. Creates node instance
  │  node = GitHubNode()
  │
  6. Prepares execution data
  │  execution_data = {
  │    "params": {
  │      "operation": "list_issues",
  │      "access_token": os.environ['GITHUB_TOKEN'],
  │      "owner": "myuser",
  │      "repo": "myrepo",
  │      "state": "open"
  │    }
  │  }
  │
  7. Executes node
  │  result = await node.execute(execution_data)
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 7: GitHub Node Execution                                       │
└─────────────────────────────────────────────────────────────────────┘

GitHubNode.execute():
  │
  1. Receives execution data
  │
  2. Validates operation
  │  operation = params['operation']  // "list_issues"
  │  if operation not in OPERATIONS:
  │    return error
  │
  3. Gets operation config
  │  op_config = OPERATIONS['list_issues']
  │  {
  │    "method": "GET",
  │    "endpoint": "/repos/{owner}/{repo}/issues",
  │    "query_params": ["state", "labels", "sort", ...]
  │  }
  │
  4. Prepares request data
  │  request_data = self._prepare_request_data(operation, params)
  │
  5. Calls UniversalRequestNode
  │  universal_node = UniversalRequestNode()
  │  result = await universal_node.execute({
  │    "base_url": "https://api.github.com",
  │    "endpoint": "/repos/myuser/myrepo/issues",
  │    "method": "GET",
  │    "headers": {
  │      "Authorization": "Bearer ghp_xxx",
  │      "Accept": "application/vnd.github.v3+json"
  │    },
  │    "params": {"state": "open"}
  │  })
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 8: UniversalRequestNode                                        │
└─────────────────────────────────────────────────────────────────────┘

UniversalRequestNode.execute():
  │
  1. Creates HTTP session
  │  session = aiohttp.ClientSession()
  │
  2. Builds full URL
  │  url = "https://api.github.com/repos/myuser/myrepo/issues"
  │
  3. Adds authentication headers
  │  headers["Authorization"] = "Bearer ghp_xxx"
  │
  4. Applies rate limiting
  │  await self.rate_limiter.acquire()
  │
  5. Makes HTTP request with retry logic
  │  for attempt in range(max_retries):
  │    try:
  │      response = await session.get(url, headers=headers, params=params)
  │      if response.status == 200:
  │        break
  │      elif response.status in [429, 500, 502, 503]:
  │        await exponential_backoff(attempt)
  │        continue
  │      else:
  │        return error
  │    except Exception:
  │      await exponential_backoff(attempt)
  │
  6. Parses response
  │  data = await response.json()
  │
  7. Returns result
  │  return {
  │    "status": "success",
  │    "data": data,  // List of issues
  │    "status_code": 200,
  │    "headers": response.headers
  │  }
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 9: Response Propagation (Upstream)                             │
└─────────────────────────────────────────────────────────────────────┘

UniversalRequestNode → GitHubNode:
  {
    "status": "success",
    "data": [
      {"number": 123, "title": "Bug in login", "state": "open"},
      {"number": 124, "title": "Feature request", "state": "open"}
    ]
  }
  │
  ▼
GitHubNode → SingleNodeExecutor:
  {
    "status": "success",
    "node_type": "github",
    "operation": "list_issues",
    "result": {...}
  }
  │
  ▼
SingleNodeExecutor → API:
  Prints JSON to stdout:
  {
    "status": "success",
    "node_type": "github",
    "operation": "list_issues",
    "result": [...]
  }
  │
  ▼
API → MCP Server:
  Returns HTTP 200:
  {
    "status": "success",
    "data": {...}
  }
  │
  ▼
MCP Server → Claude:
  Returns tool result:
  {
    "type": "text",
    "text": "{\"status\":\"success\",\"result\":[...]}"
  }
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 10: Claude Formats Response                                    │
└─────────────────────────────────────────────────────────────────────┘

Claude:
  1. Receives tool result
  2. Parses JSON
  3. Formats for user:
  
  "Here are your open GitHub issues:
  
  1. #123: Bug in login
  2. #124: Feature request
  
  Would you like me to help with any of these?"
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 11: User Sees Result                                           │
└─────────────────────────────────────────────────────────────────────┘

User sees:
  "Here are your open GitHub issues:
  
  1. #123: Bug in login
  2. #124: Feature request
  
  Would you like me to help with any of these?"

Total Time: ~2 seconds ⚡
```

---

## 🎯 3. Detailed Flow: Complex Workflow

### **User Request: "Build a restaurant management system"**

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: User Input                                                  │
└─────────────────────────────────────────────────────────────────────┘

User: "Build a restaurant management system with database, AI menu 
       suggestions, and payment processing"
  │
  │ (complex multi-service request)
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Claude Analyzes Request                                     │
└─────────────────────────────────────────────────────────────────────┘

Claude:
  1. Identifies: COMPLEX workflow (multiple services)
  2. Determines: Need full .act file
  3. Checks signature for available nodes
  4. Decides to create .act workflow
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Claude Creates .act File                                    │
└─────────────────────────────────────────────────────────────────────┘

Claude generates: restaurant-system.act

[workflow]
name = "Restaurant Management System"
description = "Full system with DB, AI, and payments"
start_node = CreateTables

[settings]
debug_mode = true
max_retries = 3

# Database Setup
[node:CreateTables]
type = neon                    # Auth from signature ✅
operation = execute_query
query = '''
  CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_name TEXT,
    items JSONB,
    total DECIMAL,
    status TEXT
  );
  CREATE TABLE IF NOT EXISTS menu (
    id SERIAL PRIMARY KEY,
    name TEXT,
    price DECIMAL,
    category TEXT
  );
'''

# API Endpoints
[node:DefineOrderAPI]
type = aci
mode = server
operation = add_route
route_path = "/api/orders"
methods = ["GET", "POST"]
handler = "ProcessOrder"

# AI Menu Suggestions
[node:MenuAI]
type = openai                  # Auth from signature ✅
operation = chat
model = "gpt-4"
messages = [
  {role = "system", content = "You are a restaurant menu expert"},
  {role = "user", content = "Suggest 5 seasonal menu items"}
]

# Process Order with AI
[node:ProcessOrder]
type = openai                  # Auth from signature ✅
operation = chat
model = "gpt-4"
messages = [
  {role = "user", content = "Analyze order: {{.Parameter.order}}"}
]

# Save to Database
[node:SaveOrder]
type = neon                    # Auth from signature ✅
operation = execute_query
query = "INSERT INTO orders (customer_name, items, total, status) VALUES ($1, $2, $3, $4)"
parameters = ["{{ProcessOrder.result.customer}}", "{{ProcessOrder.result.items}}", "{{ProcessOrder.result.total}}", "pending"]

# Process Payment
[node:ProcessPayment]
type = stripe                  # Auth from signature ✅
operation = create_charge
amount = "{{SaveOrder.result.total}}"
currency = "usd"
source = "{{.Parameter.payment_token}}"

# Send Confirmation
[node:SendNotification]
type = slack                   # Auth from signature ✅
operation = send_message
channel = "#orders"
message = "New order #{{SaveOrder.result.id}} - ${{SaveOrder.result.total}}"

# Workflow Edges (Orchestration)
[edges]
CreateTables = [DefineOrderAPI, MenuAI]
DefineOrderAPI = []
MenuAI = []
ProcessOrder = SaveOrder
SaveOrder = [ProcessPayment, SendNotification]
ProcessPayment = []
SendNotification = []
  │
  │ Saves file to: /tmp/restaurant-system.act
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: Claude Calls MCP Tool                                       │
└─────────────────────────────────────────────────────────────────────┘

Claude executes:
  execute_flow({
    flow_path: "/tmp/restaurant-system.act",
    parameters: {
      order: "2 pizzas, 1 salad",
      payment_token: "tok_visa"
    }
  })
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: MCP Server Processes Request                                │
└─────────────────────────────────────────────────────────────────────┘

Flow Architect MCP Server:
  │
  1. Receives execute_flow tool call
  │
  2. Validates .act file exists
  │
  3. Calls Flow Architect API
  │  POST /api/act/execute
  │  {
  │    "act_file_path": "/tmp/restaurant-system.act",
  │    "parameters": {...}
  │  }
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: API Layer Spawns Python Process                             │
└─────────────────────────────────────────────────────────────────────┘

API:
  python execute_workflow.py \
    --act-file /tmp/restaurant-system.act \
    --signature user.act.sig \
    --params '{"order":"2 pizzas, 1 salad",...}'
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 7: Execution Manager Takes Over                                │
└─────────────────────────────────────────────────────────────────────┘

ExecutionManager:
  │
  1. Parses .act file
  │  parser = ActfileParser('restaurant-system.act')
  │  workflow_data = parser.parse()
  │
  2. Loads signature for auth
  │  sig_parser = ActSignatureParser('user.act.sig')
  │  signature = sig_parser.parse()
  │
  3. Builds execution graph
  │  Graph:
  │    CreateTables
  │    ├── DefineOrderAPI
  │    └── MenuAI
  │    ProcessOrder
  │    └── SaveOrder
  │        ├── ProcessPayment
  │        └── SendNotification
  │
  4. Validates all nodes are authenticated
  │  for node in workflow_data['nodes']:
  │    node_type = node['type']
  │    if not signature.is_node_authenticated(node_type):
  │      return error: f"{node_type} not authenticated"
  │
  5. Starts execution from start_node
  │  start_node = workflow_data['workflow']['start_node']
  │  // "CreateTables"
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 8: Execute CreateTables Node                                   │
└─────────────────────────────────────────────────────────────────────┘

ExecutionManager.execute_node('CreateTables'):
  │
  1. Gets node config
  │  node_config = {
  │    type: "neon",
  │    operation: "execute_query",
  │    query: "CREATE TABLE ..."
  │  }
  │
  2. Resolves placeholders (none in this node)
  │
  3. Merges with signature auth
  │  auth = signature.get_node_auth('neon')
  │  // {connection_string: "postgres://..."}
  │
  4. Gets node class from registry
  │  node_class = NodeRegistry.get('neon')
  │
  5. Creates node instance
  │  node = NeonNode()
  │
  6. Executes node
  │  result = await node.execute({
  │    "params": {
  │      "operation": "execute_query",
  │      "query": "CREATE TABLE ...",
  │      "connection_string": "postgres://..."
  │    }
  │  })
  │
  7. Stores result
  │  node_results['CreateTables'] = result
  │  node_status['CreateTables'] = 'success'
  │
  8. Gets successors from graph
  │  successors = ['DefineOrderAPI', 'MenuAI']
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 9: Execute Parallel Nodes                                      │
└─────────────────────────────────────────────────────────────────────┘

ExecutionManager (parallel execution):
  │
  Parallel Task 1: DefineOrderAPI
  │  node_type = "aci"
  │  operation = "add_route"
  │  Execute → Create API endpoint
  │  Result: {"status": "success", "route": "/api/orders"}
  │
  Parallel Task 2: MenuAI  
  │  node_type = "openai"
  │  operation = "chat"
  │  Signature auth: api_key from env
  │  Execute → Call OpenAI
  │  Result: {"suggestions": ["Pizza Margherita", ...]}
  │
  await asyncio.gather(
    execute_node('DefineOrderAPI'),
    execute_node('MenuAI')
  )
  │
  Both complete ✅
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 10: Continue Workflow Execution                                │
└─────────────────────────────────────────────────────────────────────┘

ExecutionManager:
  │
  Workflow continues:
  │
  → ProcessOrder (OpenAI node)
  │  Uses signature auth ✅
  │  Analyzes order
  │  Result: {"customer": "John", "total": 45.99}
  │
  → SaveOrder (Neon node)
  │  Uses signature auth ✅
  │  Uses placeholder: {{ProcessOrder.result.customer}}
  │  Resolved to: "John"
  │  Saves to database
  │  Result: {"id": 123, "status": "saved"}
  │
  → [ProcessPayment, SendNotification] (parallel)
  │  
  │  ProcessPayment (Stripe node):
  │    Uses signature auth ✅
  │    Uses placeholder: {{SaveOrder.result.total}}
  │    Processes payment
  │    Result: {"charge_id": "ch_xxx", "status": "succeeded"}
  │  
  │  SendNotification (Slack node):
  │    Uses signature auth ✅
  │    Uses placeholder: {{SaveOrder.result.id}}
  │    Sends message
  │    Result: {"ts": "1234567890.123456"}
  │
  All nodes complete ✅
  │
  ▼

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 11: Execution Manager Returns Result                           │
└─────────────────────────────────────────────────────────────────────┘

ExecutionManager:
  │
  Workflow Summary:
  {
    "status": "success",
    "workflow_name": "Restaurant Management System",
    "executed_nodes": [
      "CreateTables",
      "DefineOrderAPI", 
      "MenuAI",
      "ProcessOrder",
      "SaveOrder",
      "ProcessPayment",
      "SendNotification"
    ],
    "node_results": {
      "CreateTables": {...},
      "ProcessOrder": {...},
      "SaveOrder": {"id": 123},
      "ProcessPayment": {"charge_id": "ch_xxx"},
      "SendNotification": {...}
    },
    "execution_time": "5.2 seconds",
    "nodes_executed": 7,
    "parallel_executions": 2
  }
  │
  Prints to stdout (JSON)
  │
  ▼

API → MCP Server → Claude → User:
  "✅ Restaurant management system built successfully!
  
  Created:
  - Database tables (orders, menu)
  - API endpoint: /api/orders
  - AI menu suggestions (5 items)
  - Order processing pipeline
  - Payment integration
  - Slack notifications
  
  Order #123 processed:
  - Customer: John
  - Total: $45.99
  - Payment: Succeeded
  - Notification sent
  
  System is live! 🚀"

Total Time: ~5 seconds ⚡
```

---

## 🎯 4. Signature Creation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ New User First Time Setup                                           │
└─────────────────────────────────────────────────────────────────────┘

User opens Settings → Nodes
  │
  │ No signature exists yet
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ System Creates Empty Signature                                      │
└─────────────────────────────────────────────────────────────────────┘

SignatureParser.create_signature(
  path = "mcp-server/signatures/user.act.sig",
  user_id = "user_abc123"
)

Creates file:
[signature]
version = "1.0.0"
user_id = "user_abc123"
created_at = "2025-01-22T10:00:00Z"
updated_at = "2025-01-22T10:00:00Z"

[metadata]
total_nodes_available = 129
authenticated_nodes = 0
unauthenticated_nodes = 129
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ UI Shows Available Nodes                                            │
└─────────────────────────────────────────────────────────────────────┘

Loads from: /api/nodes/catalog

Displays:
┌──────────────────────────────────────────────────────┐
│ Available Nodes (129)                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│ 🔓 GitHub           (Not authenticated)             │
│    Repository management, issues, PRs               │
│    [Authenticate]                                    │
│                                                      │
│ 🔓 OpenAI           (Not authenticated)             │
│    AI chat, completion, embeddings                  │
│    [Authenticate]                                    │
│                                                      │
│ 🔓 Stripe           (Not authenticated)             │
│    Payment processing                                │
│    [Authenticate]                                    │
│                                                      │
│ ... (126 more nodes)                                │
└──────────────────────────────────────────────────────┘
```

---

## 🎯 5. Node Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ User Clicks "Authenticate" on GitHub Node                           │
└─────────────────────────────────────────────────────────────────────┘

UI shows dialog:
┌────────────────────────────────────────┐
│ Authenticate GitHub                    │
├────────────────────────────────────────┤
│                                        │
│ Method: Personal Access Token          │
│                                        │
│ Token: [_________________________]     │
│                                        │
│ Default Owner: [myusername_______]     │
│ Default Repo:  [myrepo___________]     │
│                                        │
│        [Cancel]  [Save]                │
└────────────────────────────────────────┘
  │
  │ User enters token and defaults
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Frontend Sends to API                                                │
└─────────────────────────────────────────────────────────────────────┘

POST /api/signature/add-node
{
  "node_type": "github",
  "auth": {
    "access_token": "ghp_xxxxxxxxxxxxx"
  },
  "defaults": {
    "owner": "myusername",
    "repo": "myrepo"
  }
}
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ API Validates Token                                                  │
└─────────────────────────────────────────────────────────────────────┘

1. Test GitHub API with token
   GET https://api.github.com/user
   Authorization: Bearer ghp_xxxxxxxxxxxxx
   
2. If successful:
   ✅ Token is valid
   
3. If failed:
   ❌ Return error: "Invalid token"
  │
  ▼ (Token valid)
┌─────────────────────────────────────────────────────────────────────┐
│ API Stores in Environment                                            │
└─────────────────────────────────────────────────────────────────────┘

1. Add to .env file
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
   
2. Reload environment
   process.env.GITHUB_TOKEN = "ghp_xxxxxxxxxxxxx"
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ API Updates Signature File                                           │
└─────────────────────────────────────────────────────────────────────┘

SignatureParser:
  1. Load current signature
  2. Add GitHub node:
  
[node:github]
type = "github"
enabled = true
authenticated = true
auth_method = "personal_access_token"
auth_configured_at = "2025-01-22T10:15:00Z"

[node:github.auth]
access_token = "{{.env.GITHUB_TOKEN}}"  # Reference, not value!

[node:github.defaults]
owner = "myusername"
repo = "myrepo"
per_page = 50

[node:github.operations]
list_issues = {
    description = "List repository issues",
    parameters = ["owner", "repo", "state"],
    requires_auth = true
}
create_issue = {...}
list_repos = {...}
# ... (16 total operations from GitHubNode.OPERATIONS)

[node:github.metadata]
display_name = "GitHub"
category = "developer"
vendor = "github"
icon = "https://..."

  3. Update metadata:
  
[metadata]
authenticated_nodes = 1      # Was 0
unauthenticated_nodes = 128  # Was 129

[signature]
updated_at = "2025-01-22T10:15:00Z"

  4. Save file
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ UI Updates                                                           │
└─────────────────────────────────────────────────────────────────────┘

Shows:
┌──────────────────────────────────────────────────────┐
│ Authenticated Nodes (1)                              │
├──────────────────────────────────────────────────────┤
│                                                      │
│ ✅ GitHub           (Authenticated)                  │
│    16 operations available                           │
│    [View] [Remove]                                   │
│                                                      │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ Available Nodes (128)                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│ 🔓 OpenAI           (Not authenticated)             │
│    [Authenticate]                                    │
│                                                      │
│ 🔓 Stripe           (Not authenticated)             │
│    [Authenticate]                                    │
│                                                      │
│ ... (126 more)                                      │
└──────────────────────────────────────────────────────┘
  │
  │ User can now use GitHub operations immediately!
  │
  ▼

User in Claude: "List my GitHub issues"
  → Works instantly! ✅
```

---

## 🎯 6. Execution Manager Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ Execution Manager Architecture                                      │
└─────────────────────────────────────────────────────────────────────┘

                    ExecutionManager
                           │
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  Parse .act file    Build DAG Graph    Execute Nodes
        │                  │                  │
        │                  │                  │
┌───────▼────────┐  ┌──────▼───────┐  ┌──────▼───────┐
│ ActfileParser  │  │ Topological  │  │ Node         │
│                │  │ Sort         │  │ Registry     │
│ - Parse TOML   │  │              │  │              │
│ - Extract      │  │ - Detect     │  │ - Get node   │
│   nodes        │  │   cycles     │  │   class      │
│ - Extract      │  │ - Order      │  │ - Create     │
│   edges        │  │   execution  │  │   instance   │
│ - Validate     │  │ - Find       │  │ - Execute    │
│                │  │   parallel   │  │              │
└────────────────┘  └──────────────┘  └──────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│ Execution Flow Detailed                                             │
└─────────────────────────────────────────────────────────────────────┘

1. Initialize:
   ├─ Load .act file
   ├─ Load signature file
   ├─ Validate all nodes authenticated
   └─ Build execution graph

2. Build Graph:
   Example:
   
   A ──→ B ──→ D
   └──→ C ──→ D
   
   Topological Sort: [A, B, C, D]
   Parallel Opportunities: B and C can run together

3. Execute:
   
   Layer 0: Execute A
   ├─ Get node config
   ├─ Resolve placeholders (static)
   ├─ Get signature auth
   ├─ Execute node
   └─ Store result
   
   Wait for A to complete ✅
   
   Layer 1: Execute B and C in parallel
   ├─ Task 1: Execute B
   │  ├─ Resolve placeholders (use A's result)
   │  ├─ Execute node
   │  └─ Store result
   │
   ├─ Task 2: Execute C
   │  ├─ Resolve placeholders (use A's result)
   │  ├─ Execute node
   │  └─ Store result
   │
   └─ await asyncio.gather(task1, task2)
   
   Wait for B and C to complete ✅
   
   Layer 2: Execute D
   ├─ Resolve placeholders (use B and C results)
   ├─ Execute node
   └─ Store result
   
   Wait for D to complete ✅

4. Return Results:
   {
     "status": "success",
     "executed_nodes": ["A", "B", "C", "D"],
     "node_results": {...},
     "execution_time": "3.5s",
     "parallel_executions": 1
   }


┌─────────────────────────────────────────────────────────────────────┐
│ Placeholder Resolution                                               │
└─────────────────────────────────────────────────────────────────────┘

Node D config:
  type = openai
  prompt = "Analyze: {{NodeB.result}} and {{NodeC.result}}"

Resolution Process:
  1. Find all placeholders: {{NodeB.result}}, {{NodeC.result}}
  
  2. For each placeholder:
     - Extract node name: "NodeB"
     - Extract path: "result"
     
  3. Check node has executed:
     - NodeB in executed_nodes? ✅
     - NodeC in executed_nodes? ✅
     
  4. Get results:
     - NodeB.result = {"data": "value1"}
     - NodeC.result = {"data": "value2"}
     
  5. Replace:
     Original: "Analyze: {{NodeB.result}} and {{NodeC.result}}"
     Resolved: "Analyze: {\"data\": \"value1\"} and {\"data\": \"value2\"}"
     
  6. Execute Node D with resolved prompt


┌─────────────────────────────────────────────────────────────────────┐
│ Error Handling                                                       │
└─────────────────────────────────────────────────────────────────────┘

If Node B fails:
  1. Mark NodeB status = "error"
  2. Store error message
  3. Check dependent nodes:
     - Node D depends on B → Skip D
     - Node C independent → Continue C
  4. Continue workflow with remaining nodes
  5. Return partial results:
     {
       "status": "partial_success",
       "executed_nodes": ["A", "C"],
       "failed_nodes": ["B"],
       "skipped_nodes": ["D"],
       "errors": {
         "B": "Connection timeout"
       }
     }


┌─────────────────────────────────────────────────────────────────────┐
│ Retry Logic                                                          │
└─────────────────────────────────────────────────────────────────────┘

[settings]
max_retries = 3
retry_backoff = "exponential"

Node execution with retry:
  attempt = 1
  while attempt <= max_retries:
    try:
      result = await node.execute(...)
      if result.status == "success":
        break
      else:
        attempt += 1
        await sleep(2 ** attempt)  # Exponential backoff
    except Exception as e:
      attempt += 1
      if attempt > max_retries:
        return error
      await sleep(2 ** attempt)
```

---

## 🎯 7. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ Data Flow Through System                                            │
└─────────────────────────────────────────────────────────────────────┘

USER INPUT
    │
    │ "List GitHub issues"
    │
    ▼
┌─────────────────────┐
│ Claude AI           │  Interprets natural language
│ (LLM)               │  Converts to structured request
└──────────┬──────────┘
           │
           │ {node_type: "github", operation: "list_issues"}
           │
           ▼
┌─────────────────────┐
│ MCP Protocol        │  Stdio communication
│ (Tool Call)         │  JSON-RPC format
└──────────┬──────────┘
           │
           │ Tool: execute_node_operation
           │ Args: {node_type, operation, params}
           │
           ▼
┌─────────────────────┐
│ MCP Server          │  Node.js process
│ (JavaScript)        │  Handles tool dispatch
└──────────┬──────────┘
           │
           │ 1. Parse signature file (TOML)
           │ 2. Validate authentication
           │ 3. Merge parameters
           │
           ▼
┌─────────────────────┐
│ HTTP API            │  Express server
│ (REST)              │  POST /api/node/execute
└──────────┬──────────┘
           │
           │ HTTP Request Body:
           │ {node_type, operation, params}
           │
           ▼
┌─────────────────────┐
│ API Handler         │  TypeScript
│ (Node.js)           │  Spawns Python process
└──────────┬──────────┘
           │
           │ child_process.spawn(
           │   "python execute_single_node.py",
           │   args
           │ )
           │
           ▼
┌─────────────────────┐
│ Python Executor     │  Python script
│ (SingleNodeExecutor)│  Loads signature & node
└──────────┬──────────┘
           │
           │ 1. Load signature (TOML → dict)
           │ 2. Get node class from registry
           │ 3. Create node instance
           │
           ▼
┌─────────────────────┐
│ Node Class          │  Python class (e.g., GitHubNode)
│ (GitHubNode)        │  Handles specific service logic
└──────────┬──────────┘
           │
           │ 1. Map operation to HTTP request
           │ 2. Prepare request data
           │ 3. Call UniversalRequestNode
           │
           ▼
┌─────────────────────┐
│ UniversalRequest    │  Generic HTTP client
│ Node                │  Handles auth, retry, rate limit
└──────────┬──────────┘
           │
           │ HTTP Request:
           │ GET https://api.github.com/repos/owner/repo/issues
           │ Headers: Authorization: Bearer <token>
           │
           ▼
┌─────────────────────┐
│ External API        │  Third-party service
│ (GitHub API)        │  Returns data
└──────────┬──────────┘
           │
           │ HTTP Response:
           │ [{issue1}, {issue2}, ...]
           │
           ▼
┌─────────────────────┐
│ UniversalRequest    │  Parse response
│ Node                │  Return formatted result
└──────────┬──────────┘
           │
           │ {"status": "success", "data": [...]}
           │
           ▼
┌─────────────────────┐
│ Node Class          │  Process result
│ (GitHubNode)        │  Add metadata
└──────────┬──────────┘
           │
           │ {"status": "success", "result": [...]}
           │
           ▼
┌─────────────────────┐
│ Python Executor     │  JSON.dumps()
│ (SingleNodeExecutor)│  Print to stdout
└──────────┬──────────┘
           │
           │ stdout: {"status": "success", ...}
           │
           ▼
┌─────────────────────┐
│ API Handler         │  Capture stdout
│ (Node.js)           │  Parse JSON
└──────────┬──────────┘
           │
           │ HTTP Response:
           │ 200 OK
           │ Body: {"status": "success", ...}
           │
           ▼
┌─────────────────────┐
│ MCP Server          │  Format for MCP protocol
│ (JavaScript)        │  
└──────────┬──────────┘
           │
           │ Tool Result:
           │ {type: "text", text: JSON.stringify(...)}
           │
           ▼
┌─────────────────────┐
│ MCP Protocol        │  Stdio communication
│ (Tool Response)     │  JSON-RPC format
└──────────┬──────────┘
           │
           │ Tool result sent back to Claude
           │
           ▼
┌─────────────────────┐
│ Claude AI           │  Parse result
│ (LLM)               │  Format for user
└──────────┬──────────┘
           │
           │ "Here are your GitHub issues:
           │  1. Bug in login
           │  2. Feature request"
           │
           ▼
        USER OUTPUT
```

---

## 🎯 8. File System Architecture

```
flow-architect/
│
├── mcp-server/                          # MCP Server (Node.js)
│   ├── index.js                         # Main entry point
│   ├── package.json
│   │
│   ├── lib/
│   │   ├── api-client.js                # HTTP client for Flow Architect API
│   │   ├── signature-manager.js         # Load/parse/query signatures
│   │   ├── signature-parser.js          # TOML parser for .sig files
│   │   ├── flow-validator.js            # Validate .act files
│   │   └── catalog-cache.js             # Cache node catalog
│   │
│   ├── tools/
│   │   ├── execution.js                 # execute_flow tool
│   │   ├── node-operations.js           # execute_node_operation tool
│   │   ├── signature-tools.js           # Signature management tools
│   │   ├── validation.js
│   │   ├── catalog.js
│   │   └── helpers.js
│   │
│   └── signatures/                      # User signatures
│       ├── user.act.sig                 # User's authenticated nodes
│       ├── team.act.sig                 # Optional: Team signature
│       └── templates/
│           ├── github.sig.template      # Template for GitHub auth
│           ├── openai.sig.template
│           └── ...
│
├── act/                                 # Python Core
│   ├── __init__.py
│   ├── actfile_parser.py                # Parse .act files (TOML)
│   ├── execution_manager.py             # Execute full workflows
│   ├── signature_parser.py              # Parse .sig files (TOML)
│   ├── single_node_executor.py          # Execute single operations
│   │
│   └── nodes/                           # Node implementations
│       ├── __init__.py
│       ├── base_node.py                 # Base class + Registry
│       ├── universal_request_node.py    # Generic HTTP client
│       │
│       ├── github_node.py               # GitHub integration
│       ├── openai_node.py               # OpenAI integration
│       ├── neon_node.py                 # PostgreSQL integration
│       ├── stripe_node.py               # Stripe integration
│       └── ... (129 total nodes)
│
├── app/                                 # Next.js App
│   ├── api/
│   │   ├── act/
│   │   │   └── execute/
│   │   │       └── route.ts             # POST /api/act/execute
│   │   │
│   │   ├── node/
│   │   │   └── execute/
│   │   │       └── route.ts             # POST /api/node/execute
│   │   │
│   │   ├── signature/
│   │   │   ├── route.ts                 # GET /api/signature
│   │   │   ├── add-node/
│   │   │   │   └── route.ts             # POST /api/signature/add-node
│   │   │   └── remove-node/
│   │   │       └── route.ts             # DELETE /api/signature/remove-node
│   │   │
│   │   └── nodes/
│   │       └── catalog/
│   │           └── route.ts             # GET /api/nodes/catalog
│   │
│   └── settings/
│       └── nodes/
│           └── page.tsx                 # Settings UI
│
├── scripts/                             # Python scripts
│   ├── execute_workflow.py              # Execute full .act workflow
│   ├── execute_single_node.py           # Execute single node operation
│   └── validate_signature.py            # Validate .sig file
│
├── flows/                               # .act workflow files
│   ├── library/                         # Shared workflows
│   │   ├── github-operations.act
│   │   ├── ai-analysis.act
│   │   ├── restaurant-system.act
│   │   └── ...
│   │
│   └── user/                            # User's custom workflows
│       ├── my-workflow.act
│       └── ...
│
└── .env                                 # Environment variables
    GITHUB_TOKEN=ghp_xxx
    OPENAI_API_KEY=sk_xxx
    DATABASE_URL=postgres://...
    STRIPE_SECRET_KEY=sk_xxx


Data Flow Between Files:
─────────────────────────

User Request
    ↓
mcp-server/index.js (receives tool call)
    ↓
mcp-server/tools/node-operations.js (processes tool)
    ↓
mcp-server/lib/signature-parser.js (reads user.act.sig)
    ↓
mcp-server/signatures/user.act.sig (signature data)
    ↓
mcp-server/lib/api-client.js (HTTP request)
    ↓
app/api/node/execute/route.ts (API handler)
    ↓
scripts/execute_single_node.py (spawned process)
    ↓
act/signature_parser.py (loads signature)
    ↓
act/single_node_executor.py (executes operation)
    ↓
act/nodes/github_node.py (specific node logic)
    ↓
act/nodes/universal_request_node.py (HTTP request)
    ↓
External API (GitHub, OpenAI, etc.)
    ↓
Response flows back up the chain
    ↓
User sees result
```

---

## 🎯 9. API Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         API ROUTES                                  │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ POST /api/node/execute                                           │
├──────────────────────────────────────────────────────────────────┤
│ Execute single node operation using signature                    │
│                                                                  │
│ Request:                                                         │
│   {                                                              │
│     "node_type": "github",                                       │
│     "operation": "list_issues",                                  │
│     "params": {                                                  │
│       "state": "open"                                            │
│     }                                                            │
│   }                                                              │
│                                                                  │
│ Response:                                                        │
│   {                                                              │
│     "status": "success",                                         │
│     "result": [...],                                             │
│     "execution_time": "2.1s"                                     │
│   }                                                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ POST /api/act/execute                                            │
├──────────────────────────────────────────────────────────────────┤
│ Execute full .act workflow                                       │
│                                                                  │
│ Request:                                                         │
│   {                                                              │
│     "act_file_path": "/path/to/workflow.act",                    │
│     "parameters": {                                              │
│       "key": "value"                                             │
│     }                                                            │
│   }                                                              │
│                                                                  │
│ Response:                                                        │
│   {                                                              │
│     "status": "success",                                         │
│     "workflow_name": "My Workflow",                              │
│     "executed_nodes": [...],                                     │
│     "node_results": {...},                                       │
│     "execution_time": "5.3s"                                     │
│   }                                                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ MCP TOOL: get_signature_info                                     │
├──────────────────────────────────────────────────────────────────┤
│ Get current user signature info (NO API CALL - Direct file read)│
│                                                                  │
│ Input:                                                           │
│   {                                                              │
│     "node_type": "github" (optional - for specific node)        │
│   }                                                              │
│                                                                  │
│ MCP Server:                                                      │
│   1. Read user.act.sig directly (TOML file)                     │
│   2. Parse signature                                             │
│   3. Return info                                                 │
│                                                                  │
│ Response:                                                        │
│   {                                                              │
│     "version": "1.0.0",                                          │
│     "user_id": "user123",                                        │
│     "authenticated_nodes": [                                     │
│       {                                                          │
│         "type": "github",                                        │
│         "display_name": "GitHub",                                │
│         "operations": ["list_issues", ...],                      │
│         "operation_count": 16                                    │
│       },                                                         │
│       ...                                                        │
│     ]                                                            │
│   }                                                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ MCP TOOL: add_node_to_signature                                  │
├──────────────────────────────────────────────────────────────────┤
│ Authenticate and add node to signature (NO API - Direct write)  │
│                                                                  │
│ Input:                                                           │
│   {                                                              │
│     "node_type": "github",                                       │
│     "auth": {                                                    │
│       "access_token": "ghp_xxx"                                  │
│     },                                                           │
│     "defaults": {                                                │
│       "owner": "myuser",                                         │
│       "repo": "myrepo"                                           │
│     }                                                            │
│   }                                                              │
│                                                                  │
│ MCP Server:                                                      │
│   1. Validate token (call GitHub API to test)                   │
│   2. Save token to .env file                                     │
│   3. Update user.act.sig directly (add node section)            │
│   4. Return success                                              │
│                                                                  │
│ Response:                                                        │
│   {                                                              │
│     "status": "success",                                         │
│     "node_type": "github",                                       │
│     "authenticated": true,                                       │
│     "operations_available": 16                                   │
│   }                                                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ MCP TOOL: remove_node_from_signature                             │
├──────────────────────────────────────────────────────────────────┤
│ Remove node from signature (NO API - Direct file modification)  │
│                                                                  │
│ Input:                                                           │
│   {                                                              │
│     "node_type": "github"                                        │
│   }                                                              │
│                                                                  │
│ MCP Server:                                                      │
│   1. Read user.act.sig                                          │
│   2. Remove [node:github] section                               │
│   3. Update metadata (authenticated_nodes count)                │
│   4. Write back to file                                          │
│   5. Remove from .env (optional)                                 │
│                                                                  │
│ Response:                                                        │
│   {                                                              │
│     "status": "success",                                         │
│     "removed": "github"                                          │
│   }                                                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ GET /api/nodes/catalog                                           │
├──────────────────────────────────────────────────────────────────┤
│ Get all available nodes (from registry)                          │
│                                                                  │
│ Response:                                                        │
│   {                                                              │
│     "total_nodes": 129,                                          │
│     "nodes": [                                                   │
│       {                                                          │
│         "type": "github",                                        │
│         "display_name": "GitHub",                                │
│         "description": "Repository management...",               │
│         "category": "developer",                                 │
│         "requires_auth": true,                                   │
│         "operations": ["list_issues", ...],                      │
│         "icon": "https://...",                                   │
│         "documentation_url": "https://..."                       │
│       },                                                         │
│       ...                                                        │
│     ]                                                            │
│   }                                                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎯 10. Complete System Interaction

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE SYSTEM END-TO-END                               │
└─────────────────────────────────────────────────────────────────────────────┘

SCENARIO: User wants to list GitHub issues and analyze them with AI

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Setup (One-time, done in UI)                                       │
└─────────────────────────────────────────────────────────────────────────────┘

User → Settings → Nodes → Authenticate GitHub
  ├─ Enter token: ghp_xxx
  ├─ Enter defaults: owner=myuser, repo=myrepo
  └─ Click Save
      │
      ▼
API saves to .env and updates user.act.sig
      │
      ▼
user.act.sig now contains:
  [node:github]
  authenticated = true
  access_token = "{{.env.GITHUB_TOKEN}}"
  defaults = {owner = "myuser", repo = "myrepo"}
  operations = [list_issues, ...]

User → Settings → Nodes → Authenticate OpenAI
  ├─ Enter API key: sk_xxx
  └─ Click Save
      │
      ▼
user.act.sig now contains:
  [node:openai]
  authenticated = true
  api_key = "{{.env.OPENAI_API_KEY}}"
  operations = [chat, completion, ...]

Setup complete ✅

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: User Request (In Claude CLI or Chat)                               │
└─────────────────────────────────────────────────────────────────────────────┘

User: "List my GitHub issues and analyze them with AI"

Claude thinks:
  1. This needs TWO operations:
     a) List issues (GitHub)
     b) Analyze (OpenAI)
  2. Both are SIMPLE operations
  3. Can use signature for both
  4. Will chain them

Claude executes:
  Step 1: execute_node_operation(github, list_issues)
  Step 2: Wait for result
  Step 3: execute_node_operation(openai, chat, {messages: [...]})

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: First Operation (List Issues)                                      │
└─────────────────────────────────────────────────────────────────────────────┘

MCP Server receives: execute_node_operation(github, list_issues)
  │
  ├─ Load signature: user.act.sig
  ├─ Verify: GitHub authenticated ✅
  ├─ Verify: list_issues available ✅
  ├─ Get defaults: owner=myuser, repo=myrepo
  ├─ Get auth: access_token={{.env.GITHUB_TOKEN}}
  │
  └─ Call API: POST /api/node/execute
      {
        node_type: "github",
        operation: "list_issues",
        params: {owner: "myuser", repo: "myrepo", state: "all"}
      }

API spawns Python:
  python execute_single_node.py \
    --node-type github \
    --operation list_issues \
    --params '{"owner":"myuser","repo":"myrepo"}'

Python executes:
  SingleNodeExecutor
    → Load signature
    → Get GitHubNode from registry
    → Create instance
    → Execute
      → UniversalRequestNode
        → HTTP GET https://api.github.com/repos/myuser/myrepo/issues
        → Return: [{issue1}, {issue2}, {issue3}]

Result flows back:
  Python → API → MCP → Claude

Claude receives:
  {
    "status": "success",
    "result": [
      {"number": 1, "title": "Bug in login", "body": "Users can't login..."},
      {"number": 2, "title": "Add dark mode", "body": "Feature request..."},
      {"number": 3, "title": "Performance issue", "body": "App is slow..."}
    ]
  }

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: Second Operation (AI Analysis)                                     │
└─────────────────────────────────────────────────────────────────────────────┘

Claude prepares AI prompt:
  issues = result from step 1
  prompt = "Analyze these GitHub issues and categorize them:\n"
  for issue in issues:
    prompt += f"#{issue.number}: {issue.title} - {issue.body}\n"

Claude executes:
  execute_node_operation(
    openai,
    chat,
    {
      messages: [
        {role: "system", content: "You are a code analyst"},
        {role: "user", content: prompt}
      ]
    }
  )

MCP Server receives: execute_node_operation(openai, chat, {...})
  │
  ├─ Load signature: user.act.sig
  ├─ Verify: OpenAI authenticated ✅
  ├─ Verify: chat available ✅
  ├─ Get auth: api_key={{.env.OPENAI_API_KEY}}
  │
  └─ Call API: POST /api/node/execute
      {
        node_type: "openai",
        operation: "chat",
        params: {
          model: "gpt-4",
          messages: [...]
        }
      }

Python executes:
  SingleNodeExecutor
    → OpenAINode
      → UniversalRequestNode
        → HTTP POST https://api.openai.com/v1/chat/completions
        → Return: AI analysis

Result:
  {
    "status": "success",
    "result": {
      "analysis": "Based on these issues:\n
                   - 1 bug (login issue) - HIGH PRIORITY\n
                   - 1 feature request (dark mode) - MEDIUM\n
                   - 1 performance issue - HIGH PRIORITY\n
                   Recommendation: Fix bugs first..."
    }
  }

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: Claude Formats Final Response                                      │
└─────────────────────────────────────────────────────────────────────────────┘

Claude combines both results:

  "I found 3 issues in your repository:
  
  🔴 High Priority:
     #1: Bug in login
     #3: Performance issue
  
  🟡 Medium Priority:
     #2: Add dark mode (feature request)
  
  AI Analysis:
  You should fix the bugs first (login and performance) before 
  adding new features. The login bug is critical as it prevents 
  users from accessing the app.
  
  Would you like me to help create a fix for the login bug?"

User sees this response in ~3 seconds total ⚡

┌─────────────────────────────────────────────────────────────────────────────┐
│ KEY POINTS                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

✅ No .act file needed (simple operations)
✅ Authentication handled by signature
✅ Defaults from signature (no repetition)
✅ Claude orchestrates multiple operations
✅ Fast execution (2-3 seconds per operation)
✅ Clean, readable result

This demonstrates the POWER of ACT Signature:
- Simple operations are instant
- No configuration overhead
- Claude can chain operations naturally
- User experience is seamless
```

---

## 🎯 Summary

**The Complete Flow:**

1. **One-time Setup**: User authenticates nodes in UI → Signature created
2. **Simple Operations**: Claude uses signature → Instant execution
3. **Complex Workflows**: Claude creates .act file → Full orchestration
4. **Result**: Fast, clean, powerful system with minimal friction

**Total Architecture:**
- User Layer (Web UI, Claude CLI, Chat)
- Interface Layer (MCP Server)
- Signature Layer (user.act.sig)
- Parsing Layer (SignatureParser, ActfileParser)
- Execution Layer (SingleNodeExecutor, ExecutionManager)
- Node Layer (GitHubNode, OpenAINode, etc.)
- External APIs (GitHub, OpenAI, etc.)

**Key Innovation:**
- Signature provides authentication + defaults
- Simple ops use signature directly
- Complex workflows use .act files (which reference signature)
- One MCP server handles everything
- Progressive complexity for users

---

## 🔥 WHEN TO USE WHAT

### **Use MCP Tools (Direct File Access):**

✅ **Signature Operations:**
- `get_signature_info()` - Read signature
- `add_node_to_signature()` - Add node
- `remove_node_from_signature()` - Remove node
- `list_available_nodes()` - List catalog
- `validate_signature()` - Validate format

**Why?** MCP server has direct file system access. No need for HTTP!

```javascript
// MCP Server can just:
const fs = require('fs/promises');
const signature = await fs.readFile('signatures/user.act.sig', 'utf-8');
// Done! No API needed!
```

---

### **Use API Calls (Python Execution Needed):**

✅ **Node Execution:**
- `execute_node_operation()` - MCP tool → API → Python
- `execute_flow()` - MCP tool → API → Python

**Why?** These need Python execution (nodes are Python classes).

```
MCP Tool (JS) → API (TS) → Python Script → Node Execution
```

**Can't avoid API here because:**
- MCP server is Node.js
- Nodes are Python classes
- Need to spawn Python process
- API layer handles process management

---

### **Architecture Decision:**

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP SERVER (Node.js)                     │
│                                                             │
│  Can do directly (no API):                                  │
│  ✅ Read/write files                                        │
│  ✅ Parse TOML                                              │
│  ✅ Validate data                                           │
│  ✅ Query signature                                         │
│  ✅ Manage catalog                                          │
│                                                             │
│  Must use API (needs Python):                               │
│  ⚠️ Execute Python nodes                                    │
│  ⚠️ Run workflows                                           │
│  ⚠️ Use Python-based execution engine                       │
└─────────────────────────────────────────────────────────────┘
```

---

**This is the complete system.** 🚀
