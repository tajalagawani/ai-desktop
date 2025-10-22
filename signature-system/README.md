# ACT Signature System

**Universal Execution Layer: Single Operations + Full Workflows**

## 🎯 Overview

The ACT Signature System provides pre-authenticated node access for instant execution of operations without approval prompts. Users authenticate nodes once in Settings, and Claude can execute operations immediately using the signature.

## 📁 Structure

```
signature-system/
├── parser/                          # Python signature parser
│   ├── signature_parser.py          # ActSignatureParser class
│   ├── single_node_executor.py      # SingleNodeExecutor
│   ├── requirements.txt             # Python dependencies
│   └── __init__.py
│
├── mcp/                             # MCP Server (Node.js)
│   ├── index.js                     # Main entry point
│   ├── package.json                 # Dependencies
│   │
│   ├── lib/                         # Internal libraries
│   │   ├── signature-manager.js     # SignatureManager class
│   │   ├── toml-parser.js           # TOML utilities
│   │   ├── api-client.js            # HTTP client
│   │   ├── error-handler.js         # Error handling
│   │   └── env-manager.js           # .env management
│   │
│   ├── tools/                       # MCP tool implementations
│   │   ├── execution/
│   │   │   ├── execute-node-operation.js
│   │   │   └── execute-flow.js
│   │   ├── signature/
│   │   │   ├── get-signature-info.js
│   │   │   ├── add-node.js
│   │   │   ├── remove-node.js
│   │   │   ├── update-node-defaults.js
│   │   │   └── validate-signature.js
│   │   ├── catalog/
│   │   │   ├── list-available-nodes.js
│   │   │   ├── get-node-info.js
│   │   │   └── search-nodes.js
│   │   ├── validation/
│   │   │   ├── validate-flow.js
│   │   │   └── validate-params.js
│   │   ├── management/
│   │   │   ├── list-flows.js
│   │   │   └── save-flow.js
│   │   └── utility/
│   │       └── get-system-status.js
│   │
│   ├── signatures/                  # Signature files
│   │   ├── user.act.sig             # User's authenticated nodes
│   │   └── templates/               # Templates for each node
│   │
│   └── cache/                       # Cached data
│       └── node-catalog.json
│
├── api/                             # API routes (Next.js)
│   └── node-execute.ts              # POST /api/node/execute
│
├── ui/                              # UI components
│   ├── settings-nodes.tsx           # Settings → Nodes page
│   └── auth-dialog.tsx              # Authentication dialog
│
├── types/                           # TypeScript types
│   └── signature.types.ts
│
└── examples/                        # Example signatures & workflows
    ├── example-signature.toml
    └── example-workflow.act
```

## 🔑 Key Concepts

### **ACT Signature File (.act.sig)**
TOML file containing authenticated nodes and their operations:
```toml
[signature]
version = "1.0.0"
user_id = "user123"

[node:github]
authenticated = true
access_token = "{{.env.GITHUB_TOKEN}}"

[node:github.operations]
list_issues = {description = "List issues", requires_auth = true}
```

### **15 MCP Tools**
- **Execution (2)**: execute_node_operation, execute_flow
- **Signature (5)**: get/add/remove/update/validate signature
- **Catalog (3)**: list/info/search nodes
- **Validation (2)**: validate_flow, validate_params
- **Management (2)**: list/save flows
- **Utility (1)**: get_system_status

### **Two Execution Modes**
1. **Simple Operations**: Use signature directly via `execute_node_operation()`
2. **Complex Workflows**: Use .act files via `execute_flow()`

## 🚀 Usage

### Authenticate a Node (once)
```javascript
// User in Settings UI or Claude CLI
add_node_to_signature({
  node_type: "github",
  auth: {access_token: "ghp_xxx"},
  defaults: {owner: "myuser", repo: "myrepo"}
})
```

### Execute Single Operation
```javascript
// Claude uses signature automatically
execute_node_operation({
  node_type: "github",
  operation: "list_issues",
  params: {state: "open"}
})
// ✅ Executes instantly - no approval needed!
```

### Execute Complex Workflow
```javascript
// For multi-service orchestration
execute_flow({
  flow_path: "/path/to/workflow.act",
  parameters: {key: "value"}
})
// All nodes use signature for authentication
```

## 📦 Installation

```bash
# Install MCP server dependencies
cd mcp
npm install

# Install Python dependencies
cd ../parser
pip install -r requirements.txt
```

## 🧪 Testing

```bash
# Test MCP server
cd mcp
npm test

# Test Python parser
cd ../parser
pytest
```

## 📚 Documentation

See the complete documentation files:
- `COMPLETE-ACT-SIGNATURE-IMPLEMENTATION.md` - Full implementation guide
- `COMPLETE-SYSTEM-FLOW-DIAGRAMS.md` - Visual flow diagrams
- `MCP-SERVER-COMPLETE-ARCHITECTURE.md` - MCP server architecture

## 🎯 Implementation Status

Track progress: See root todo list for all 50 implementation tasks.

## 🔐 Security

- Tokens stored in `.env` (never in signature file directly)
- Signature uses `{{.env.VARIABLE}}` references
- Token validation before storing
- Direct file access (no HTTP layer for signatures)
