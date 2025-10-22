# Flow Architect MCP Server - Complete Architecture

**Deep dive into the MCP Server: structure, tools, and data flow**

---

## 🎯 Table of Contents

1. [MCP Server Overview](#mcp-server-overview)
2. [File Structure](#file-structure)
3. [All MCP Tools](#all-mcp-tools)
4. [Tool Categories](#tool-categories)
5. [Internal Libraries](#internal-libraries)
6. [Data Flow Per Tool](#data-flow-per-tool)
7. [Tool Implementation Examples](#tool-implementation-examples)
8. [Error Handling](#error-handling)
9. [Configuration](#configuration)
10. [Integration Points](#integration-points)

---

## 🎯 1. MCP Server Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                   FLOW ARCHITECT MCP SERVER                         │
│                      (Node.js/TypeScript)                           │
│                                                                     │
│  Purpose: Provide Claude with tools to interact with Flow Architect│
│  Protocol: Model Context Protocol (MCP) via stdio                  │
│  Language: JavaScript/TypeScript                                    │
│  Runtime: Node.js 18+                                              │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    TOOL CATEGORIES                          │  │
│  │                                                             │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │  EXECUTION  │  │  SIGNATURE  │  │  VALIDATION │       │  │
│  │  │    TOOLS    │  │    TOOLS    │  │    TOOLS    │       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  │                                                             │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │   CATALOG   │  │ MANAGEMENT  │  │   UTILITY   │       │  │
│  │  │    TOOLS    │  │    TOOLS    │  │    TOOLS    │       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                   INTERNAL LIBRARIES                        │  │
│  │                                                             │  │
│  │  • SignatureManager    - Read/write/query signatures       │  │
│  │  • TomlParser          - Parse TOML files                  │  │
│  │  • ApiClient           - HTTP client for backend API       │  │
│  │  • FlowValidator       - Validate .act files               │  │
│  │  │  CatalogCache        - Cache node catalog               │  │
│  │  • EnvManager          - Manage environment variables      │  │
│  │  • ErrorHandler        - Standardized error handling       │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                   FILE SYSTEM ACCESS                        │  │
│  │                                                             │  │
│  │  Read:                                                      │  │
│  │  • signatures/user.act.sig                                 │  │
│  │  • flows/library/*.act                                     │  │
│  │  • .env                                                     │  │
│  │  • node_catalog.json (cached)                              │  │
│  │                                                             │  │
│  │  Write:                                                     │  │
│  │  • signatures/user.act.sig                                 │  │
│  │  • .env                                                     │  │
│  │  • flows/user/*.act (if user requests)                     │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                   EXTERNAL CONNECTIONS                      │  │
│  │                                                             │  │
│  │  → Flow Architect API (HTTP)                               │  │
│  │    • POST /api/node/execute                                │  │
│  │    • POST /api/act/execute                                 │  │
│  │    • GET /api/nodes/catalog                                │  │
│  │                                                             │  │
│  │  → External APIs (for token validation)                    │  │
│  │    • GitHub API (validate GitHub tokens)                   │  │
│  │    • OpenAI API (validate OpenAI keys)                     │  │
│  │    • etc.                                                   │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 2. File Structure

```
flow-architect/mcp-server/
│
├── package.json                      # Dependencies
├── tsconfig.json                     # TypeScript config
├── index.js                          # Main entry point
│
├── lib/                              # Internal libraries
│   ├── signature-manager.js          # SignatureManager class
│   ├── toml-parser.js                # TOML parsing utilities
│   ├── api-client.js                 # HTTP client for API
│   ├── flow-validator.js             # Validate .act files
│   ├── catalog-cache.js              # Node catalog caching
│   ├── env-manager.js                # Environment variable management
│   └── error-handler.js              # Error handling utilities
│
├── tools/                            # MCP tool implementations
│   ├── execution/
│   │   ├── execute-node-operation.js # Execute single node
│   │   └── execute-flow.js           # Execute workflow
│   │
│   ├── signature/
│   │   ├── get-signature-info.js     # Read signature
│   │   ├── add-node.js               # Add node to signature
│   │   ├── remove-node.js            # Remove node from signature
│   │   ├── update-node-defaults.js   # Update node defaults
│   │   └── validate-signature.js     # Validate signature file
│   │
│   ├── catalog/
│   │   ├── list-available-nodes.js   # List all nodes
│   │   ├── get-node-info.js          # Get specific node info
│   │   └── search-nodes.js           # Search node catalog
│   │
│   ├── validation/
│   │   ├── validate-flow.js          # Validate .act file
│   │   ├── check-dependencies.js     # Check node dependencies
│   │   └── validate-params.js        # Validate parameters
│   │
│   ├── management/
│   │   ├── list-flows.js             # List saved flows
│   │   ├── save-flow.js              # Save .act file
│   │   ├── delete-flow.js            # Delete .act file
│   │   └── get-flow-info.js          # Get flow metadata
│   │
│   └── utility/
│       ├── resolve-placeholders.js   # Preview placeholder resolution
│       ├── test-connection.js        # Test API connection
│       └── get-system-info.js        # Get system status
│
├── signatures/                       # Signature files
│   ├── user.act.sig                  # User's signature
│   ├── team.act.sig                  # Optional: team signature
│   └── templates/                    # Signature templates
│       ├── github.template.toml
│       ├── openai.template.toml
│       └── ...
│
├── cache/                            # Cached data
│   ├── node-catalog.json             # Cached node catalog
│   └── flow-metadata.json            # Cached flow metadata
│
└── logs/                             # MCP server logs
    └── mcp-server.log
```

---

## 🎯 3. All MCP Tools

### **Complete Tool List (15 tools):**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EXECUTION TOOLS (2)                         │
├─────────────────────────────────────────────────────────────────────┤
│ 1. execute_node_operation     Execute single node using signature  │
│ 2. execute_flow               Execute full .act workflow           │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         SIGNATURE TOOLS (5)                         │
├─────────────────────────────────────────────────────────────────────┤
│ 3. get_signature_info         Get signature data                   │
│ 4. add_node_to_signature      Add/authenticate node                │
│ 5. remove_node_from_signature Remove node                          │
│ 6. update_node_defaults       Update default parameters            │
│ 7. validate_signature          Validate signature format            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         CATALOG TOOLS (3)                           │
├─────────────────────────────────────────────────────────────────────┤
│ 8. list_available_nodes       List all 129+ nodes                  │
│ 9. get_node_info              Get details for specific node        │
│ 10. search_nodes              Search nodes by keyword              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         VALIDATION TOOLS (2)                        │
├─────────────────────────────────────────────────────────────────────┤
│ 11. validate_flow             Validate .act file syntax/structure  │
│ 12. validate_params           Check if params match operation      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         MANAGEMENT TOOLS (2)                        │
├─────────────────────────────────────────────────────────────────────┤
│ 13. list_flows                List saved .act files                │
│ 14. save_flow                 Save .act file to library            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         UTILITY TOOLS (1)                           │
├─────────────────────────────────────────────────────────────────────┤
│ 15. get_system_status         Get MCP server status/health         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 4. Tool Categories

### **Category 1: Execution Tools**

```
┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: execute_node_operation                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Execute single node operation using signature             │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     node_type: "github",                                            │
│     operation: "list_issues",                                       │
│     params: {state: "open"},                                        │
│     override_defaults: false                                        │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Read signature file (user.act.sig)                            │
│   2. Verify node is authenticated                                  │
│   3. Verify operation exists                                       │
│   4. Get node defaults                                             │
│   5. Get node auth from signature                                  │
│   6. Resolve {{.env.VARIABLE}} references                          │
│   7. Merge: defaults + auth + runtime params                       │
│   8. Call API: POST /api/node/execute                              │
│   9. Return result                                                 │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     status: "success",                                              │
│     result: {...},                                                  │
│     execution_time: "2.1s"                                          │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - Simple single operations                                        │
│   - "List my GitHub issues"                                         │
│   - "Query the database"                                            │
│   - "Send an email"                                                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: execute_flow                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Execute full .act workflow                                 │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     flow_path: "/path/to/workflow.act",                             │
│     parameters: {key: "value"},                                     │
│     signature_path: "signatures/user.act.sig"                      │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Validate .act file exists                                     │
│   2. Read signature file                                           │
│   3. Validate all nodes in workflow are authenticated              │
│   4. Call API: POST /api/act/execute                               │
│   5. Stream progress updates (if supported)                        │
│   6. Return final result                                           │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     status: "success",                                              │
│     workflow_name: "Restaurant System",                             │
│     executed_nodes: ["Node1", "Node2", ...],                        │
│     node_results: {...},                                            │
│     execution_time: "5.3s"                                          │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - Complex multi-step workflows                                    │
│   - Multiple services orchestrated                                  │
│   - "Build a restaurant system"                                     │
│   - "Create deployment pipeline"                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

### **Category 2: Signature Tools**

```
┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: get_signature_info                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Get information about user's signature                     │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     node_type: "github" (optional - for specific node)             │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Read user.act.sig file                                        │
│   2. Parse TOML                                                    │
│   3. If node_type provided:                                        │
│      - Return info for that node only                              │
│   4. Else:                                                          │
│      - Return all authenticated nodes                               │
│   5. Include operation counts, metadata                            │
│                                                                     │
│ Output (all nodes):                                                 │
│   {                                                                 │
│     version: "1.0.0",                                               │
│     user_id: "user123",                                             │
│     authenticated_nodes: [                                          │
│       {                                                             │
│         type: "github",                                             │
│         display_name: "GitHub",                                     │
│         category: "developer",                                      │
│         operations: ["list_issues", ...],                           │
│         operation_count: 16,                                        │
│         defaults: {owner: "myuser", repo: "myrepo"}                │
│       },                                                            │
│       ...                                                           │
│     ],                                                              │
│     total_authenticated: 3                                          │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - "What nodes do I have authenticated?"                           │
│   - "Show me my GitHub configuration"                               │
│   - Checking capabilities before executing                          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: add_node_to_signature                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Add/authenticate a node in signature                       │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     node_type: "github",                                            │
│     auth: {                                                         │
│       access_token: "ghp_xxxxxxxxxxxx"                              │
│     },                                                              │
│     defaults: {                                                     │
│       owner: "myuser",                                              │
│       repo: "myrepo"                                                │
│     }                                                               │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Validate node_type exists in catalog                          │
│   2. Test authentication:                                           │
│      - For GitHub: GET https://api.github.com/user                 │
│      - For OpenAI: GET https://api.openai.com/v1/models            │
│      - Verify token works                                           │
│   3. If valid:                                                      │
│      a. Save to .env file:                                          │
│         GITHUB_TOKEN=ghp_xxxxxxxxxxxx                               │
│      b. Update user.act.sig:                                        │
│         [node:github]                                               │
│         authenticated = true                                        │
│         access_token = "{{.env.GITHUB_TOKEN}}"                     │
│         [node:github.defaults]                                      │
│         owner = "myuser"                                            │
│         repo = "myrepo"                                             │
│         [node:github.operations]                                    │
│         ... (load from catalog)                                     │
│      c. Update metadata counts                                      │
│   4. Return success                                                 │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     status: "success",                                              │
│     node_type: "github",                                            │
│     authenticated: true,                                            │
│     operations_available: 16                                        │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - User says "authenticate GitHub"                                 │
│   - Setting up new integrations                                     │
│   - (Usually triggered from UI, but can be CLI)                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: remove_node_from_signature                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Remove node authentication from signature                  │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     node_type: "github"                                             │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Read user.act.sig                                             │
│   2. Remove all sections for this node:                            │
│      - [node:github]                                                │
│      - [node:github.auth]                                           │
│      - [node:github.defaults]                                       │
│      - [node:github.operations]                                     │
│      - [node:github.metadata]                                       │
│   3. Update metadata counts                                         │
│   4. Write back to file                                             │
│   5. Optionally remove from .env                                    │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     status: "success",                                              │
│     removed: "github"                                               │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - "Remove GitHub authentication"                                  │
│   - User wants to revoke access                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: update_node_defaults                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Update default parameters for a node                       │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     node_type: "github",                                            │
│     defaults: {                                                     │
│       owner: "newuser",                                             │
│       repo: "newrepo",                                              │
│       per_page: 100                                                 │
│     }                                                               │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Read user.act.sig                                             │
│   2. Verify node exists and is authenticated                       │
│   3. Update [node:github.defaults] section                         │
│   4. Write back to file                                             │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     status: "success",                                              │
│     node_type: "github",                                            │
│     updated_defaults: {...}                                         │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - "Change my default GitHub repo to X"                            │
│   - User wants different default parameters                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: validate_signature                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Validate signature file format and content                 │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     signature_path: "signatures/user.act.sig" (optional)           │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Read signature file                                           │
│   2. Parse TOML (check syntax)                                     │
│   3. Validate structure:                                            │
│      - [signature] section exists                                   │
│      - Required fields present                                      │
│      - Node sections well-formed                                    │
│   4. Validate auth references:                                      │
│      - {{.env.VARIABLE}} all resolvable                            │
│   5. Return validation result                                       │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     valid: true,                                                    │
│     errors: [],                                                     │
│     warnings: ["NODE_X_TOKEN not in .env"],                        │
│     authenticated_nodes: 3                                          │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - Troubleshooting signature issues                                │
│   - Before executing operations                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### **Category 3: Catalog Tools**

```
┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: list_available_nodes                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: List all available nodes (129+)                            │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     category: "developer" (optional filter),                        │
│     authenticated_only: false                                       │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Check cache: cache/node-catalog.json                          │
│   2. If cache expired:                                              │
│      - Call API: GET /api/nodes/catalog                            │
│      - Update cache                                                 │
│   3. Read signature to mark authenticated nodes                    │
│   4. Filter by category if provided                                │
│   5. Return list                                                    │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     total_nodes: 129,                                               │
│     nodes: [                                                        │
│       {                                                             │
│         type: "github",                                             │
│         display_name: "GitHub",                                     │
│         description: "Repository management...",                    │
│         category: "developer",                                      │
│         requires_auth: true,                                        │
│         authenticated: true,  // From signature                     │
│         operation_count: 16,                                        │
│         icon: "https://...",                                        │
│         tags: ["github", "git", "vcs"]                             │
│       },                                                            │
│       ...                                                           │
│     ]                                                               │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - "What nodes are available?"                                     │
│   - "Show me all database nodes"                                    │
│   - Exploring capabilities                                          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: get_node_info                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Get detailed information about specific node               │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     node_type: "github"                                             │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Load node catalog                                             │
│   2. Get node entry                                                │
│   3. Check if authenticated in signature                           │
│   4. Return detailed info                                           │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     type: "github",                                                 │
│     display_name: "GitHub",                                         │
│     description: "Comprehensive GitHub API integration...",         │
│     category: "developer",                                          │
│     vendor: "github",                                               │
│     version: "1.0.0",                                               │
│     requires_auth: true,                                            │
│     authenticated: true,                                            │
│     auth_method: "personal_access_token",                           │
│     operations: [                                                   │
│       {                                                             │
│         name: "list_issues",                                        │
│         description: "List repository issues",                      │
│         parameters: ["owner", "repo", "state", "labels"],          │
│         required_params: ["owner", "repo"]                         │
│       },                                                            │
│       ...                                                           │
│     ],                                                              │
│     documentation_url: "https://docs.github.com/rest",             │
│     examples: [...]                                                 │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - "Tell me about the GitHub node"                                 │
│   - "What operations does GitHub support?"                          │
│   - Learning about capabilities                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: search_nodes                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Search nodes by keyword                                    │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     query: "email",                                                 │
│     search_in: ["name", "description", "tags"]                     │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Load node catalog                                             │
│   2. Search in specified fields                                    │
│   3. Rank by relevance                                             │
│   4. Return matches                                                 │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     query: "email",                                                 │
│     results: [                                                      │
│       {                                                             │
│         type: "sendgrid",                                           │
│         display_name: "SendGrid",                                   │
│         description: "Email delivery service",                      │
│         relevance: 0.95                                             │
│       },                                                            │
│       {                                                             │
│         type: "gmail",                                              │
│         display_name: "Gmail",                                      │
│         description: "Gmail API integration",                       │
│         relevance: 0.87                                             │
│       },                                                            │
│       ...                                                           │
│     ],                                                              │
│     total_results: 5                                                │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - "Find nodes for sending email"                                  │
│   - "What nodes work with databases?"                               │
│   - Discovering relevant nodes                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### **Category 4: Validation Tools**

```
┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: validate_flow                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Validate .act file syntax and structure                    │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     flow_path: "/path/to/workflow.act",                             │
│     check_authentication: true                                      │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Read .act file                                                │
│   2. Parse TOML (syntax check)                                     │
│   3. Validate structure:                                            │
│      - [workflow] section exists                                    │
│      - start_node defined                                           │
│      - All nodes have type                                          │
│      - All edges reference valid nodes                              │
│   4. If check_authentication:                                       │
│      - Load signature                                               │
│      - Verify all nodes are authenticated                           │
│   5. Check for cycles in graph                                     │
│   6. Return validation result                                       │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     valid: true,                                                    │
│     errors: [],                                                     │
│     warnings: ["Node X has no successors"],                        │
│     nodes: ["Node1", "Node2", ...],                                │
│     unauthenticated_nodes: []                                       │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - Before executing flow                                           │
│   - "Check if this workflow is valid"                               │
│   - Troubleshooting flow issues                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: validate_params                                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Validate parameters match operation requirements           │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     node_type: "github",                                            │
│     operation: "list_issues",                                       │
│     params: {state: "open", owner: "myuser"}                       │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Get node info from catalog                                    │
│   2. Get operation definition                                      │
│   3. Check required parameters present                             │
│   4. Check parameter types                                         │
│   5. Check valid values (enums)                                    │
│   6. Return validation result                                       │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     valid: true,                                                    │
│     missing_required: [],                                           │
│     invalid_types: [],                                              │
│     warnings: ["Param 'repo' not provided, will use default"],     │
│     merged_params: {                                                │
│       state: "open",                                                │
│       owner: "myuser",                                              │
│       repo: "myrepo"  // From defaults                              │
│     }                                                               │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - Before executing operation                                      │
│   - "Check if these parameters are correct"                         │
│   - Parameter validation                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

### **Category 5: Management Tools**

```
┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: list_flows                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: List saved .act workflow files                             │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     directory: "library" or "user" (default: both)                 │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Scan flows/library/*.act                                      │
│   2. Scan flows/user/*.act                                         │
│   3. Read each file's [workflow] section                           │
│   4. Extract metadata                                              │
│   5. Return list                                                    │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     library_flows: [                                                │
│       {                                                             │
│         name: "Restaurant System",                                  │
│         path: "flows/library/restaurant-system.act",               │
│         description: "Full restaurant management...",               │
│         nodes: ["CreateTables", "ProcessOrder", ...],              │
│         node_count: 7                                               │
│       },                                                            │
│       ...                                                           │
│     ],                                                              │
│     user_flows: [...]                                               │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - "What workflows do I have?"                                     │
│   - "Show me saved flows"                                           │
│   - Browsing available workflows                                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: save_flow                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Save .act workflow file                                    │
│                                                                     │
│ Input:                                                              │
│   {                                                                 │
│     name: "my-workflow",                                            │
│     content: "...",  // TOML content                                │
│     directory: "user" or "library",                                │
│     overwrite: false                                                │
│   }                                                                 │
│                                                                     │
│ Process:                                                            │
│   1. Validate content (TOML syntax)                                │
│   2. Check if file exists                                          │
│   3. If overwrite=false and exists, error                          │
│   4. Write to flows/{directory}/{name}.act                         │
│   5. Return success                                                 │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     status: "success",                                              │
│     path: "flows/user/my-workflow.act",                            │
│     name: "my-workflow"                                             │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - Saving generated workflows                                      │
│   - "Save this workflow as X"                                       │
│   - Persisting complex flows                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

### **Category 6: Utility Tools**

```
┌─────────────────────────────────────────────────────────────────────┐
│ TOOL: get_system_status                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Purpose: Get MCP server status and health                           │
│                                                                     │
│ Input: (none)                                                       │
│                                                                     │
│ Process:                                                            │
│   1. Check MCP server status                                       │
│   2. Check signature file exists                                   │
│   3. Check API connectivity                                        │
│   4. Count authenticated nodes                                     │
│   5. Check cache status                                            │
│   6. Return status                                                  │
│                                                                     │
│ Output:                                                             │
│   {                                                                 │
│     status: "healthy",                                              │
│     mcp_server: {                                                   │
│       version: "1.0.0",                                             │
│       uptime: "2h 15m"                                              │
│     },                                                              │
│     signature: {                                                    │
│       exists: true,                                                 │
│       authenticated_nodes: 3,                                       │
│       last_updated: "2025-01-22T10:15:00Z"                         │
│     },                                                              │
│     api: {                                                          │
│       connected: true,                                              │
│       response_time: "45ms"                                         │
│     },                                                              │
│     cache: {                                                        │
│       catalog_age: "1h 30m",                                        │
│       needs_refresh: false                                          │
│     }                                                               │
│   }                                                                 │
│                                                                     │
│ Used by Claude when:                                                │
│   - "Is the system working?"                                        │
│   - "Check MCP server status"                                       │
│   - Troubleshooting connectivity                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 5. Internal Libraries

### **SignatureManager**

```javascript
// lib/signature-manager.js

class SignatureManager {
  constructor(signaturePath) {
    this.signaturePath = signaturePath;
    this.signature = null;
  }

  async load() {
    const content = await fs.readFile(this.signaturePath, 'utf-8');
    this.signature = toml.parse(content);
    return this.signature;
  }

  isAuthenticated(nodeType) {
    const nodeKey = `node:${nodeType}`;
    return this.signature[nodeKey]?.authenticated === true;
  }

  getNodeAuth(nodeType) {
    const authKey = `node:${nodeType}.auth`;
    const auth = this.signature[authKey];
    
    // Resolve environment variables
    return this.resolveEnvVars(auth);
  }

  getNodeDefaults(nodeType) {
    const defaultsKey = `node:${nodeType}.defaults`;
    return this.signature[defaultsKey] || {};
  }

  getOperations(nodeType) {
    const opsKey = `node:${nodeType}.operations`;
    return this.signature[opsKey] || {};
  }

  resolveEnvVars(obj) {
    // Convert {{.env.VARIABLE}} to actual values
    const resolved = {};
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'string' && value.includes('{{.env.')) {
        const varName = value.match(/\{\{\.env\.(\w+)\}\}/)[1];
        resolved[key] = process.env[varName];
      } else {
        resolved[key] = value;
      }
    }
    return resolved;
  }

  async addNode(nodeType, authData, defaults) {
    // 1. Validate auth with external API
    await this.validateAuth(nodeType, authData);

    // 2. Save to .env
    await this.saveToEnv(nodeType, authData);

    // 3. Update signature
    this.signature[`node:${nodeType}`] = {
      type: nodeType,
      enabled: true,
      authenticated: true,
      auth_configured_at: new Date().toISOString()
    };

    this.signature[`node:${nodeType}.auth`] = {
      // Store as env reference, not actual value
      ...this.toEnvReferences(authData)
    };

    this.signature[`node:${nodeType}.defaults`] = defaults;

    // 4. Load operations from catalog
    const catalog = await this.loadCatalog();
    const nodeInfo = catalog.nodes.find(n => n.type === nodeType);
    this.signature[`node:${nodeType}.operations`] = nodeInfo.operations;
    this.signature[`node:${nodeType}.metadata`] = nodeInfo.metadata;

    // 5. Update metadata
    this.signature.metadata.authenticated_nodes += 1;
    this.signature.metadata.unauthenticated_nodes -= 1;
    this.signature.signature.updated_at = new Date().toISOString();

    // 6. Save
    await this.save();
  }

  async removeNode(nodeType) {
    // Remove all sections for this node
    delete this.signature[`node:${nodeType}`];
    delete this.signature[`node:${nodeType}.auth`];
    delete this.signature[`node:${nodeType}.defaults`];
    delete this.signature[`node:${nodeType}.operations`];
    delete this.signature[`node:${nodeType}.metadata`];

    // Update metadata
    this.signature.metadata.authenticated_nodes -= 1;
    this.signature.metadata.unauthenticated_nodes += 1;

    await this.save();
  }

  async save() {
    const content = toml.stringify(this.signature);
    await fs.writeFile(this.signaturePath, content, 'utf-8');
  }

  async validateAuth(nodeType, authData) {
    // Test authentication by calling external API
    if (nodeType === 'github') {
      const response = await fetch('https://api.github.com/user', {
        headers: {
          'Authorization': `Bearer ${authData.access_token}`
        }
      });
      if (!response.ok) throw new Error('Invalid GitHub token');
    }
    // ... similar for other nodes
  }
}
```

---

## 🎯 6. Data Flow Per Tool

### **execute_node_operation Flow:**

```
Claude
  │
  │ execute_node_operation(github, list_issues, {state: "open"})
  │
  ▼
MCP Server (index.js)
  │
  │ 1. Receive tool call
  │
  ▼
tools/execution/execute-node-operation.js
  │
  │ 2. Load SignatureManager
  │
  ▼
lib/signature-manager.js
  │
  │ 3. Read user.act.sig
  │ 4. Parse TOML
  │ 5. Verify authentication
  │ 6. Get defaults
  │ 7. Get auth (resolve env vars)
  │
  ▼
lib/api-client.js
  │
  │ 8. Call POST /api/node/execute
  │    Body: {node_type, operation, params}
  │
  ▼
Backend API
  │
  │ 9. Spawn Python process
  │ 10. Execute node
  │ 11. Return result
  │
  ▼
lib/api-client.js
  │
  │ 12. Receive response
  │
  ▼
tools/execution/execute-node-operation.js
  │
  │ 13. Format result
  │
  ▼
MCP Server (index.js)
  │
  │ 14. Return to Claude
  │
  ▼
Claude
  │
  │ 15. Format for user
  │
  ▼
User sees result ✅
```

---

### **add_node_to_signature Flow:**

```
Claude
  │
  │ add_node_to_signature(github, {access_token: "xxx"}, {owner: "myuser"})
  │
  ▼
MCP Server (index.js)
  │
  │ 1. Receive tool call
  │
  ▼
tools/signature/add-node.js
  │
  │ 2. Load SignatureManager
  │
  ▼
lib/signature-manager.js
  │
  │ 3. validateAuth()
  │    ↓
  │    Call GitHub API: GET /user
  │    Verify token works
  │    ✅ Valid
  │
  │ 4. saveToEnv()
  │    ↓
  │    Append to .env:
  │    GITHUB_TOKEN=ghp_xxx
  │
  │ 5. Load node catalog
  │    ↓
  │    Get operations for github node
  │
  │ 6. Update signature object
  │    [node:github]
  │    authenticated = true
  │    ...
  │
  │ 7. save()
  │    ↓
  │    Write to user.act.sig
  │
  ▼
tools/signature/add-node.js
  │
  │ 8. Return success
  │
  ▼
MCP Server (index.js)
  │
  │ 9. Return to Claude
  │
  ▼
Claude
  │
  │ 10. Confirm to user
  │
  ▼
User: "✅ GitHub authenticated!" ✅
```

---

## 🎯 7. Tool Implementation Example

### **Complete Tool Implementation:**

```javascript
// tools/execution/execute-node-operation.js

import { SignatureManager } from '../../lib/signature-manager.js';
import { ApiClient } from '../../lib/api-client.js';
import { ErrorHandler } from '../../lib/error-handler.js';

export async function executeNodeOperation({ node_type, operation, params = {}, override_defaults = false }) {
  try {
    // 1. Load signature
    const sigManager = new SignatureManager('signatures/user.act.sig');
    await sigManager.load();

    // 2. Verify node authenticated
    if (!sigManager.isAuthenticated(node_type)) {
      return ErrorHandler.format({
        code: 'NODE_NOT_AUTHENTICATED',
        message: `Node '${node_type}' is not authenticated`,
        help: `Authenticate ${node_type} using: add_node_to_signature`
      });
    }

    // 3. Verify operation exists
    const operations = sigManager.getOperations(node_type);
    if (!operations[operation]) {
      return ErrorHandler.format({
        code: 'OPERATION_NOT_FOUND',
        message: `Operation '${operation}' not found for '${node_type}'`,
        available: Object.keys(operations)
      });
    }

    // 4. Get defaults and auth
    const defaults = override_defaults ? {} : sigManager.getNodeDefaults(node_type);
    const auth = sigManager.getNodeAuth(node_type); // Resolves env vars

    // 5. Merge parameters
    const finalParams = {
      ...defaults,
      ...auth,
      ...params,
      operation // Add operation to params
    };

    // 6. Call API
    const apiClient = new ApiClient();
    const result = await apiClient.post('/api/node/execute', {
      node_type,
      operation,
      params: finalParams
    });

    // 7. Return success
    return {
      type: 'text',
      text: JSON.stringify({
        status: 'success',
        node_type,
        operation,
        result: result.data,
        execution_time: result.execution_time
      }, null, 2)
    };

  } catch (error) {
    return ErrorHandler.handle(error);
  }
}
```

---

## 🎯 8. Error Handling

```javascript
// lib/error-handler.js

export class ErrorHandler {
  static format(error) {
    return {
      type: 'text',
      text: JSON.stringify({
        status: 'error',
        code: error.code,
        message: error.message,
        help: error.help,
        available_options: error.available,
        timestamp: new Date().toISOString()
      }, null, 2)
    };
  }

  static handle(error) {
    // Map common errors to user-friendly messages
    if (error.code === 'ENOENT') {
      return this.format({
        code: 'FILE_NOT_FOUND',
        message: 'Signature file not found',
        help: 'Run setup or create signature file'
      });
    }

    if (error.message.includes('TOML parse error')) {
      return this.format({
        code: 'INVALID_SIGNATURE',
        message: 'Signature file has invalid syntax',
        help: 'Validate signature using: validate_signature'
      });
    }

    // Generic error
    return this.format({
      code: 'UNKNOWN_ERROR',
      message: error.message,
      stack: error.stack
    });
  }
}
```

---

## 🎯 9. Configuration

```javascript
// index.js - Main MCP Server

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

// Import all tools
import { executeNodeOperation } from './tools/execution/execute-node-operation.js';
import { executeFlow } from './tools/execution/execute-flow.js';
import { getSignatureInfo } from './tools/signature/get-signature-info.js';
import { addNodeToSignature } from './tools/signature/add-node.js';
// ... import all 15 tools

// Create MCP server
const server = new Server(
  {
    name: 'flow-architect-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Register all tools
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'execute_node_operation',
        description: 'Execute single node operation using signature',
        inputSchema: {
          type: 'object',
          properties: {
            node_type: { type: 'string' },
            operation: { type: 'string' },
            params: { type: 'object' },
            override_defaults: { type: 'boolean', default: false }
          },
          required: ['node_type', 'operation']
        }
      },
      // ... all 15 tools
    ]
  };
});

// Register tool handlers
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'execute_node_operation':
      return await executeNodeOperation(args);
    
    case 'execute_flow':
      return await executeFlow(args);
    
    case 'get_signature_info':
      return await getSignatureInfo(args);
    
    case 'add_node_to_signature':
      return await addNodeToSignature(args);
    
    // ... all 15 tools
    
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);

console.error('Flow Architect MCP Server running on stdio');
```

---

## 🎯 10. Integration Points

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INTEGRATION MAP                              │
└─────────────────────────────────────────────────────────────────────┘

MCP Server connects to:

1. FILE SYSTEM (Direct access)
   └─ signatures/user.act.sig         (Read/Write)
   └─ flows/library/*.act             (Read)
   └─ flows/user/*.act                (Read/Write)
   └─ .env                            (Read/Write)
   └─ cache/node-catalog.json         (Read/Write)

2. FLOW ARCHITECT API (HTTP)
   └─ POST /api/node/execute          (Execute single node)
   └─ POST /api/act/execute           (Execute workflow)
   └─ GET /api/nodes/catalog          (Get node list)

3. EXTERNAL APIs (HTTP - for validation)
   └─ GitHub: GET /user               (Validate token)
   └─ OpenAI: GET /v1/models          (Validate API key)
   └─ Stripe: GET /v1/account         (Validate secret key)
   └─ ... (for each node type)

4. CLAUDE (via MCP Protocol)
   └─ Stdio communication
   └─ JSON-RPC messages
   └─ Tool requests/responses
```

---

## 🎯 Summary

**MCP Server is the interface layer that:**

1. ✅ **Receives tool calls from Claude** (via stdio)
2. ✅ **Reads/writes signature files directly** (no API needed)
3. ✅ **Manages authentication** (validates tokens, stores in .env)
4. ✅ **Calls backend API** (only when Python execution needed)
5. ✅ **Returns results to Claude** (formatted responses)

**15 Tools across 6 categories:**
- Execution (2) - Execute nodes and workflows
- Signature (5) - Manage authentication
- Catalog (3) - Browse available nodes
- Validation (2) - Validate flows and params
- Management (2) - Manage saved flows
- Utility (1) - System status

**Key Libraries:**
- SignatureManager - Core signature operations
- ApiClient - HTTP communication
- TomlParser - TOML file handling
- ErrorHandler - Standardized errors

**This is the complete MCP Server architecture!** 🚀
