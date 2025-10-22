# ACT Signature System - Complete Implementation Plan

**The Universal Execution Layer: One MCP + Signatures + Full Flows**

---

## 🎯 System Overview

### **The Complete Picture:**

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                         │
│  Settings → Add Nodes → Authenticate → Auto-generate .sig  │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                   ACT SIGNATURE FILE                        │
│  user.act.sig - User's authenticated nodes & operations    │
│  - GitHub (authenticated, list_issues, create_repo, ...)   │
│  - OpenAI (authenticated, chat, completion, ...)           │
│  - Stripe (authenticated, create_charge, ...)              │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE CLI                          │
│  User: "List my GitHub issues"                             │
│  Claude reads user.act.sig → GitHub authenticated ✅       │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│              FLOW ARCHITECT MCP SERVER                      │
│  Tool: execute_node_operation()                            │
│  Tool: execute_flow()                                       │
│  Tool: manage_signature()                                   │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                   EXECUTION MANAGER                         │
│  - Single node execution (from signature)                   │
│  - Full workflow execution (from .act file)                 │
│  - Parallel/Sequential/Conditional execution                │
└─────────────────────────────────────────────────────────────┘
                             ↓
                         RESULT ✅
```

---

## 📁 File Structure

```
flow-architect/
├── mcp-server/
│   ├── index.js                    # Main MCP server
│   ├── package.json                # Dependencies
│   │
│   ├── lib/
│   │   ├── api-client.js          # API wrapper for Flow Architect
│   │   ├── signature-manager.js    # NEW: Signature CRUD operations
│   │   ├── signature-parser.js     # NEW: Parse .act.sig files
│   │   ├── flow-validator.js       # Validate .act files
│   │   └── catalog-cache.js        # Cache node catalog
│   │
│   ├── tools/
│   │   ├── execution.js            # execute_flow (existing)
│   │   ├── node-operations.js      # NEW: execute_node_operation
│   │   ├── signature-tools.js      # NEW: Signature management tools
│   │   ├── validation.js           # Validation tools
│   │   ├── catalog.js              # Catalog tools
│   │   ├── management.js           # Flow management
│   │   ├── fetching.js             # Data fetching
│   │   └── helpers.js              # Helpers
│   │
│   └── signatures/
│       ├── user.act.sig            # User's signature file
│       ├── team.act.sig            # Optional: Team signature
│       └── templates/              # Signature templates
│           ├── github.sig.template
│           ├── openai.sig.template
│           └── ...
│
├── act/
│   ├── actfile_parser.py           # Existing ACT parser
│   ├── execution_manager.py        # Existing execution manager
│   ├── signature_parser.py         # NEW: Signature parser
│   └── nodes/
│       ├── github_node.py          # Existing GitHub node
│       └── ...
│
└── api/
    └── routes/
        ├── act-execute.js          # POST /api/act/execute
        ├── node-execute.js         # NEW: POST /api/node/execute
        └── signature-manage.js     # NEW: Signature CRUD API
```

---

## 🎯 Part 1: ACT Signature Format

### **File:** `user.act.sig` (TOML format)

```toml
# ACT Signature File
# Auto-generated from user authentication in UI
# Contains all authenticated nodes and their operations

[signature]
version = "1.0.0"
user_id = "user123"
created_at = "2025-01-22T10:00:00Z"
updated_at = "2025-01-22T15:30:00Z"
schema_version = "1.0"

# ============================================
# GitHub Node (Authenticated)
# ============================================

[node:github]
type = "github"
enabled = true
authenticated = true
auth_method = "personal_access_token"
auth_configured_at = "2025-01-22T10:00:00Z"

# Authentication (references environment variable)
[node:github.auth]
access_token = "{{.env.GITHUB_TOKEN}}"

# Default parameters (user preferences)
[node:github.defaults]
owner = "myusername"
repo = "myrepo"
per_page = 50

# Available operations (from node CONFIG)
[node:github.operations]
list_issues = {
    description = "List repository issues",
    parameters = ["owner", "repo", "state", "labels", "sort"],
    requires_auth = true
}
create_issue = {
    description = "Create a new issue",
    parameters = ["owner", "repo", "title", "body", "labels"],
    requires_auth = true
}
list_repos = {
    description = "List user repositories",
    parameters = ["type", "sort", "direction"],
    requires_auth = true
}
create_repo = {
    description = "Create a new repository",
    parameters = ["name", "description", "private", "auto_init"],
    requires_auth = true
}
get_file_content = {
    description = "Get file content from repository",
    parameters = ["owner", "repo", "path", "ref"],
    requires_auth = true
}
# ... all 16 GitHub operations

# Node metadata (from node CONFIG)
[node:github.metadata]
display_name = "GitHub"
category = "developer"
vendor = "github"
version = "1.0.0"
icon = "https://cdn.jsdelivr.net/npm/simple-icons@v9/github.svg"
color = "#181717"
documentation_url = "https://docs.github.com/rest"
tags = ["github", "git", "repository", "issues", "pull-requests"]

# ============================================
# OpenAI Node (Authenticated)
# ============================================

[node:openai]
type = "openai"
enabled = true
authenticated = true
auth_method = "api_key"
auth_configured_at = "2025-01-22T10:15:00Z"

[node:openai.auth]
api_key = "{{.env.OPENAI_API_KEY}}"

[node:openai.defaults]
model = "gpt-4"
temperature = 0.7
max_tokens = 1000

[node:openai.operations]
chat = {
    description = "Chat completion",
    parameters = ["messages", "model", "temperature", "max_tokens"],
    requires_auth = true
}
completion = {
    description = "Text completion",
    parameters = ["prompt", "model", "temperature", "max_tokens"],
    requires_auth = true
}
embedding = {
    description = "Create embeddings",
    parameters = ["input", "model"],
    requires_auth = true
}

[node:openai.metadata]
display_name = "OpenAI"
category = "ai"
vendor = "openai"
version = "1.0.0"

# ============================================
# PostgreSQL/Neon Node (Authenticated)
# ============================================

[node:neon]
type = "neon"
enabled = true
authenticated = true
auth_method = "connection_string"
auth_configured_at = "2025-01-22T10:30:00Z"

[node:neon.auth]
connection_string = "{{.env.DATABASE_URL}}"

[node:neon.defaults]
timeout = 30
pool_size = 10

[node:neon.operations]
execute_query = {
    description = "Execute SQL query",
    parameters = ["query", "parameters"],
    requires_auth = true
}
transaction = {
    description = "Execute transaction",
    parameters = ["queries"],
    requires_auth = true
}
batch = {
    description = "Batch operations",
    parameters = ["operations"],
    requires_auth = true
}

[node:neon.metadata]
display_name = "PostgreSQL (Neon)"
category = "database"
vendor = "neon"
version = "1.0.0"

# ============================================
# Unauthenticated Nodes (Available but not configured)
# ============================================

[node:stripe]
type = "stripe"
enabled = false
authenticated = false
requires_auth = true
# Operations available but not accessible until authenticated

[node:slack]
type = "slack"
enabled = false
authenticated = false
requires_auth = true

# ============================================
# Signature Metadata
# ============================================

[metadata]
total_nodes_available = 129
authenticated_nodes = 3
unauthenticated_nodes = 126
last_sync = "2025-01-22T15:30:00Z"
```

---

## 🎯 Part 2: Signature Parser (Python)

### **File:** `act/signature_parser.py`

```python
#!/usr/bin/env python3
"""
ACT Signature Parser - Parse .act.sig files
Similar to actfile_parser.py but for signature files
"""

import toml
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class SignatureParserError(Exception):
    """Custom exception for signature parsing errors."""
    pass

class ActSignatureParser:
    """
    Parse ACT Signature files (.act.sig)
    
    Signature files contain:
    - User's authenticated nodes
    - Available operations per node
    - Default parameters
    - Auth configuration references
    """
    
    def __init__(self, signature_path: str):
        self.signature_path = Path(signature_path)
        self.parsed_data = {}
        
        if not self.signature_path.exists():
            raise SignatureParserError(f"Signature file not found: {signature_path}")
    
    def parse(self) -> Dict[str, Any]:
        """Parse the signature file and return structured data."""
        try:
            with open(self.signature_path, 'r') as f:
                self.parsed_data = toml.load(f)
            
            self._validate()
            logger.info(f"Successfully parsed signature: {self.signature_path}")
            
            return self.parsed_data
            
        except toml.TomlDecodeError as e:
            raise SignatureParserError(f"Invalid TOML syntax in signature file: {e}")
        except Exception as e:
            raise SignatureParserError(f"Error parsing signature file: {e}")
    
    def _validate(self):
        """Validate signature structure."""
        if 'signature' not in self.parsed_data:
            raise SignatureParserError("Missing [signature] section")
        
        required_fields = ['version', 'user_id', 'created_at']
        for field in required_fields:
            if field not in self.parsed_data['signature']:
                raise SignatureParserError(f"Missing required field in [signature]: {field}")
        
        logger.debug("Signature validation passed")
    
    # Query Methods
    
    def get_authenticated_nodes(self) -> List[str]:
        """Get list of authenticated node types."""
        authenticated = []
        
        for key in self.parsed_data.keys():
            if key.startswith('node:'):
                node_name = key.replace('node:', '')
                node_data = self.parsed_data[key]
                
                if node_data.get('authenticated', False):
                    authenticated.append(node_name)
        
        return authenticated
    
    def is_node_authenticated(self, node_type: str) -> bool:
        """Check if a node type is authenticated."""
        node_key = f"node:{node_type}"
        
        if node_key not in self.parsed_data:
            return False
        
        return self.parsed_data[node_key].get('authenticated', False)
    
    def get_node_operations(self, node_type: str) -> Dict[str, Any]:
        """Get available operations for a node."""
        node_key = f"node:{node_type}"
        
        if node_key not in self.parsed_data:
            raise SignatureParserError(f"Node '{node_type}' not found in signature")
        
        node_data = self.parsed_data[node_key]
        
        if not node_data.get('authenticated', False):
            raise SignatureParserError(f"Node '{node_type}' is not authenticated")
        
        operations_key = f"{node_key}.operations"
        
        if operations_key not in self.parsed_data:
            return {}
        
        return self.parsed_data[operations_key]
    
    def get_node_defaults(self, node_type: str) -> Dict[str, Any]:
        """Get default parameters for a node."""
        defaults_key = f"node:{node_type}.defaults"
        
        if defaults_key not in self.parsed_data:
            return {}
        
        return self.parsed_data[defaults_key]
    
    def get_node_auth(self, node_type: str) -> Dict[str, Any]:
        """Get auth configuration for a node."""
        auth_key = f"node:{node_type}.auth"
        
        if auth_key not in self.parsed_data:
            raise SignatureParserError(f"No auth configuration for node '{node_type}'")
        
        return self.parsed_data[auth_key]
    
    def get_node_metadata(self, node_type: str) -> Dict[str, Any]:
        """Get metadata for a node."""
        metadata_key = f"node:{node_type}.metadata"
        
        if metadata_key not in self.parsed_data:
            return {}
        
        return self.parsed_data[metadata_key]
    
    def can_execute_operation(self, node_type: str, operation: str) -> bool:
        """Check if a specific operation can be executed."""
        if not self.is_node_authenticated(node_type):
            return False
        
        operations = self.get_node_operations(node_type)
        
        return operation in operations
    
    def get_operation_info(self, node_type: str, operation: str) -> Dict[str, Any]:
        """Get information about a specific operation."""
        operations = self.get_node_operations(node_type)
        
        if operation not in operations:
            raise SignatureParserError(
                f"Operation '{operation}' not found for node '{node_type}'"
            )
        
        return operations[operation]
    
    # Signature Management
    
    def add_node(self, node_type: str, node_config: Dict[str, Any]):
        """Add a new node to the signature."""
        node_key = f"node:{node_type}"
        
        self.parsed_data[node_key] = node_config
        self.parsed_data['signature']['updated_at'] = datetime.now().isoformat()
        
        self._save()
    
    def remove_node(self, node_type: str):
        """Remove a node from the signature."""
        node_key = f"node:{node_type}"
        
        if node_key in self.parsed_data:
            del self.parsed_data[node_key]
            
            # Remove related sections
            for key in list(self.parsed_data.keys()):
                if key.startswith(f"{node_key}."):
                    del self.parsed_data[key]
            
            self.parsed_data['signature']['updated_at'] = datetime.now().isoformat()
            self._save()
    
    def update_node_auth(self, node_type: str, auth_config: Dict[str, Any]):
        """Update auth configuration for a node."""
        auth_key = f"node:{node_type}.auth"
        node_key = f"node:{node_type}"
        
        self.parsed_data[auth_key] = auth_config
        
        if node_key in self.parsed_data:
            self.parsed_data[node_key]['authenticated'] = True
            self.parsed_data[node_key]['auth_configured_at'] = datetime.now().isoformat()
        
        self.parsed_data['signature']['updated_at'] = datetime.now().isoformat()
        self._save()
    
    def _save(self):
        """Save changes back to the signature file."""
        try:
            with open(self.signature_path, 'w') as f:
                toml.dump(self.parsed_data, f)
            
            logger.info(f"Signature saved: {self.signature_path}")
            
        except Exception as e:
            raise SignatureParserError(f"Error saving signature: {e}")
    
    @staticmethod
    def create_signature(
        signature_path: str,
        user_id: str,
        version: str = "1.0.0"
    ) -> 'ActSignatureParser':
        """Create a new signature file."""
        signature_data = {
            'signature': {
                'version': version,
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'schema_version': '1.0'
            },
            'metadata': {
                'total_nodes_available': 129,
                'authenticated_nodes': 0,
                'unauthenticated_nodes': 129,
                'last_sync': datetime.now().isoformat()
            }
        }
        
        signature_path = Path(signature_path)
        signature_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(signature_path, 'w') as f:
            toml.dump(signature_data, f)
        
        logger.info(f"Created new signature: {signature_path}")
        
        return ActSignatureParser(signature_path)


# Usage Example
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    # Create a new signature
    parser = ActSignatureParser.create_signature(
        "/tmp/user.act.sig",
        user_id="user123"
    )
    
    # Add GitHub node
    parser.add_node('github', {
        'type': 'github',
        'enabled': True,
        'authenticated': True,
        'auth_method': 'personal_access_token'
    })
    
    # Check authentication
    print(f"GitHub authenticated: {parser.is_node_authenticated('github')}")
    print(f"Authenticated nodes: {parser.get_authenticated_nodes()}")
```

---

## 🎯 Part 3: MCP Tool - execute_node_operation

### **File:** `mcp-server/tools/node-operations.js`

```javascript
import fs from "fs/promises";
import path from "path";

export function createNodeOperationTools(api, signatureParser) {
  return {
    execute_node_operation: {
      name: "execute_node_operation",
      description:
        "Execute a SINGLE node operation using ACT Signature. No .act file needed! Perfect for simple operations like 'list GitHub issues', 'query database', 'call AI', etc. The signature provides authentication and default parameters automatically.",
      inputSchema: {
        type: "object",
        properties: {
          node_type: {
            type: "string",
            description: "Node type from signature (e.g., 'github', 'openai', 'neon')",
            examples: ["github", "openai", "neon", "stripe", "slack"],
          },
          operation: {
            type: "string",
            description: "Operation to execute (e.g., 'list_issues', 'chat', 'execute_query')",
            examples: [
              "list_issues",
              "create_issue",
              "chat",
              "execute_query",
              "send_message",
            ],
          },
          params: {
            type: "object",
            description:
              "Runtime parameters for the operation. Default parameters from signature are auto-applied.",
            examples: [
              { state: "open", labels: "bug" },
              { query: "SELECT * FROM users" },
              { messages: [{ role: "user", content: "Hello" }] },
            ],
          },
          override_defaults: {
            type: "boolean",
            description: "If true, ignore signature defaults and use only provided params",
            default: false,
          },
        },
        required: ["node_type", "operation"],
      },
      handler: async ({
        node_type,
        operation,
        params = {},
        override_defaults = false,
      }) => {
        try {
          // 1. Load user signature
          const signaturePath = path.join(
            process.cwd(),
            "flow-architect/mcp-server/signatures/user.act.sig"
          );

          const signatureContent = await fs.readFile(signaturePath, "utf-8");
          const signature = parseSignature(signatureContent); // TOML parser

          // 2. Verify node is authenticated
          const nodeKey = `node:${node_type}`;

          if (!signature[nodeKey]) {
            return {
              type: "text",
              text: JSON.stringify(
                {
                  error: `Node '${node_type}' not found in signature`,
                  available_nodes: Object.keys(signature)
                    .filter((k) => k.startsWith("node:"))
                    .map((k) => k.replace("node:", "")),
                  help: "Go to Settings → Add Node to authenticate",
                },
                null,
                2
              ),
            };
          }

          const nodeConfig = signature[nodeKey];

          if (!nodeConfig.authenticated) {
            return {
              type: "text",
              text: JSON.stringify(
                {
                  error: `Node '${node_type}' is not authenticated`,
                  help: `Authenticate ${node_type} in Settings → Nodes`,
                },
                null,
                2
              ),
            };
          }

          // 3. Verify operation exists
          const operationsKey = `${nodeKey}.operations`;

          if (!signature[operationsKey]) {
            return {
              type: "text",
              text: JSON.stringify({
                error: `No operations found for node '${node_type}'`,
              }),
            };
          }

          const operations = signature[operationsKey];

          if (!operations[operation]) {
            return {
              type: "text",
              text: JSON.stringify(
                {
                  error: `Operation '${operation}' not found for node '${node_type}'`,
                  available_operations: Object.keys(operations),
                },
                null,
                2
              ),
            };
          }

          // 4. Merge parameters (signature defaults + runtime params)
          const defaultsKey = `${nodeKey}.defaults`;
          const defaults = signature[defaultsKey] || {};
          const authKey = `${nodeKey}.auth`;
          const auth = signature[authKey] || {};

          const finalParams = override_defaults
            ? { ...auth, ...params }
            : { ...defaults, ...auth, ...params };

          // 5. Call Flow Architect API to execute single node
          const result = await api.executeSingleNode({
            node_type,
            operation,
            params: finalParams,
          });

          return {
            type: "text",
            text: JSON.stringify(
              {
                status: "success",
                node_type,
                operation,
                result: result.data,
                execution_time: result.execution_time,
              },
              null,
              2
            ),
          };
        } catch (error) {
          return {
            type: "text",
            text: JSON.stringify(
              {
                error: error.message,
                stack: error.stack,
                node_type,
                operation,
              },
              null,
              2
            ),
          };
        }
      },
    },

    get_signature_info: {
      name: "get_signature_info",
      description: "Get information about current user signature (authenticated nodes, available operations)",
      inputSchema: {
        type: "object",
        properties: {
          node_type: {
            type: "string",
            description: "Optional: Get info for specific node only",
          },
        },
      },
      handler: async ({ node_type }) => {
        const signaturePath = path.join(
          process.cwd(),
          "flow-architect/mcp-server/signatures/user.act.sig"
        );

        const signatureContent = await fs.readFile(signaturePath, "utf-8");
        const signature = parseSignature(signatureContent);

        if (node_type) {
          // Return info for specific node
          const nodeKey = `node:${node_type}`;
          const nodeConfig = signature[nodeKey];
          const operations = signature[`${nodeKey}.operations`] || {};
          const defaults = signature[`${nodeKey}.defaults`] || {};
          const metadata = signature[`${nodeKey}.metadata`] || {};

          return {
            type: "text",
            text: JSON.stringify(
              {
                node_type,
                authenticated: nodeConfig?.authenticated || false,
                available_operations: Object.keys(operations),
                defaults,
                metadata,
              },
              null,
              2
            ),
          };
        }

        // Return all authenticated nodes
        const authenticatedNodes = [];

        for (const key of Object.keys(signature)) {
          if (key.startsWith("node:")) {
            const type = key.replace("node:", "");
            const config = signature[key];

            if (config.authenticated) {
              const operations = signature[`${key}.operations`] || {};

              authenticatedNodes.push({
                type,
                display_name: signature[`${key}.metadata`]?.display_name || type,
                category: signature[`${key}.metadata`]?.category || "other",
                operation_count: Object.keys(operations).length,
                operations: Object.keys(operations),
              });
            }
          }
        }

        return {
          type: "text",
          text: JSON.stringify(
            {
              signature_version: signature.signature?.version,
              user_id: signature.signature?.user_id,
              authenticated_nodes: authenticatedNodes,
              total_authenticated: authenticatedNodes.length,
            },
            null,
            2
          ),
        };
      },
    },
  };
}

// Helper function to parse TOML signature
function parseSignature(content) {
  // Use a TOML parser library (e.g., @iarna/toml)
  const toml = require("@iarna/toml");
  return toml.parse(content);
}
```

---

## 🎯 Part 4: Flow Architect API - Single Node Execution

### **File:** `act/single_node_executor.py`

```python
#!/usr/bin/env python3
"""
Single Node Executor - Execute a single node operation from signature
"""

import logging
from typing import Dict, Any
from .nodes.base_node import NodeRegistry
from .signature_parser import ActSignatureParser

logger = logging.getLogger(__name__)

class SingleNodeExecutor:
    """
    Execute single node operations using ACT Signature.
    
    This is different from ExecutionManager which executes full workflows.
    SingleNodeExecutor is for on-the-fly single operation execution.
    """
    
    def __init__(self, signature_path: str):
        self.signature_parser = ActSignatureParser(signature_path)
        self.signature_parser.parse()
    
    async def execute_operation(
        self,
        node_type: str,
        operation: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single node operation.
        
        Args:
            node_type: Node type (e.g., 'github', 'openai')
            operation: Operation name (e.g., 'list_issues')
            params: Runtime parameters
        
        Returns:
            Execution result
        """
        try:
            # 1. Verify authentication
            if not self.signature_parser.is_node_authenticated(node_type):
                return {
                    "status": "error",
                    "error": f"Node '{node_type}' is not authenticated",
                    "help": "Authenticate this node in Settings"
                }
            
            # 2. Verify operation exists
            if not self.signature_parser.can_execute_operation(node_type, operation):
                available_ops = list(self.signature_parser.get_node_operations(node_type).keys())
                return {
                    "status": "error",
                    "error": f"Operation '{operation}' not available for '{node_type}'",
                    "available_operations": available_ops
                }
            
            # 3. Get node class from registry
            node_class = NodeRegistry.get(node_type)
            
            if not node_class:
                return {
                    "status": "error",
                    "error": f"Node type '{node_type}' not found in registry"
                }
            
            # 4. Create node instance
            node_instance = node_class()
            
            # 5. Prepare execution data
            execution_data = {
                "params": {
                    "operation": operation,
                    **params
                }
            }
            
            # 6. Execute node
            result = await node_instance.execute(execution_data)
            
            return {
                "status": "success",
                "node_type": node_type,
                "operation": operation,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing single node operation: {e}")
            return {
                "status": "error",
                "error": str(e),
                "node_type": node_type,
                "operation": operation
            }
```

---

## 🎯 Part 5: API Routes

### **File:** `app/api/node/execute/route.ts`

```typescript
import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { node_type, operation, params = {} } = body;

    if (!node_type || !operation) {
      return NextResponse.json(
        { error: "node_type and operation are required" },
        { status: 400 }
      );
    }

    // Execute Python script for single node execution
    const pythonScript = path.join(
      process.cwd(),
      "flow-architect/scripts/execute_single_node.py"
    );

    const pythonProcess = spawn("python3", [
      pythonScript,
      "--node-type",
      node_type,
      "--operation",
      operation,
      "--params",
      JSON.stringify(params),
      "--signature",
      path.join(
        process.cwd(),
        "flow-architect/mcp-server/signatures/user.act.sig"
      ),
    ]);

    let output = "";
    let errorOutput = "";

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      errorOutput += data.toString();
    });

    await new Promise((resolve, reject) => {
      pythonProcess.on("close", (code) => {
        if (code === 0) {
          resolve(output);
        } else {
          reject(new Error(errorOutput || `Process exited with code ${code}`));
        }
      });
    });

    const result = JSON.parse(output);

    return NextResponse.json(result);
  } catch (error: any) {
    console.error("Node execution error:", error);
    return NextResponse.json(
      {
        error: "Node execution failed",
        details: error.message,
      },
      { status: 500 }
    );
  }
}
```

---

## 🎯 Part 6: Usage Examples

### **Example 1: Simple Operation (List GitHub Issues)**

**Claude Code:**
```
User: "List my open GitHub issues"

Claude reads signature:
  - GitHub is authenticated ✅
  - Has list_issues operation ✅
  - Default owner/repo from signature ✅

Claude calls MCP:
  execute_node_operation({
    node_type: "github",
    operation: "list_issues",
    params: {state: "open"}
  })

Result in 2 seconds ⚡
```

### **Example 2: AI Analysis**

**Claude Code:**
```
User: "Analyze my latest code changes with AI"

Claude:
  1. execute_node_operation("github", "list_commits", {per_page: 1})
  2. execute_node_operation("github", "get_file_content", {path: "..."})
  3. execute_node_operation("openai", "chat", {
       messages: [{role: "user", content: "Analyze: " + code}]
     })

All operations use signature for auth
No .act file needed!
```

### **Example 3: Complex Workflow (Still use .act file)**

**For multi-service orchestration:**

```toml
# restaurant-system.act
[workflow]
name = "Restaurant System"

[node:CreateTables]
type = neon  # Auth from signature
operation = execute_query

[node:ProcessOrder]
type = openai  # Auth from signature

[node:SendNotification]
type = slack  # Auth from signature

[edges]
CreateTables = ProcessOrder
ProcessOrder = SendNotification
```

**Execute:**
```
execute_flow("restaurant-system.act")
```

---

## 🎯 Part 7: Signature Management UI

### **Settings Page (React):**

```typescript
// components/settings/node-management.tsx

import { useState, useEffect } from "react";

export function NodeManagement() {
  const [signature, setSignature] = useState(null);
  const [availableNodes, setAvailableNodes] = useState([]);

  useEffect(() => {
    // Load current signature
    fetch("/api/signature")
      .then((r) => r.json())
      .then(setSignature);

    // Load available nodes from catalog
    fetch("/api/nodes/catalog")
      .then((r) => r.json())
      .then((data) => setAvailableNodes(data.nodes));
  }, []);

  const authenticateNode = async (nodeType: string) => {
    // Open OAuth or show API key input
    const authData = await showAuthDialog(nodeType);

    // Save to signature
    await fetch("/api/signature/add-node", {
      method: "POST",
      body: JSON.stringify({
        node_type: nodeType,
        auth: authData,
      }),
    });

    // Reload signature
    window.location.reload();
  };

  return (
    <div className="node-management">
      <h2>Authenticated Nodes</h2>

      {signature?.authenticated_nodes.map((node) => (
        <div key={node.type} className="node-card">
          <img src={node.icon} alt={node.display_name} />
          <h3>{node.display_name}</h3>
          <p>{node.operation_count} operations available</p>
          <button onClick={() => removeNode(node.type)}>Remove</button>
        </div>
      ))}

      <h2>Available Nodes (Not Authenticated)</h2>

      {availableNodes
        .filter(
          (n) => !signature?.authenticated_nodes.some((a) => a.type === n.type)
        )
        .map((node) => (
          <div key={node.type} className="node-card unauthenticated">
            <h3>{node.type}</h3>
            <p>{node.description}</p>
            <button onClick={() => authenticateNode(node.type)}>
              Authenticate
            </button>
          </div>
        ))}
    </div>
  );
}
```

---

## 🎯 Final Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                          USER                                │
│  "List my GitHub issues"                                     │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                      CLAUDE CODE                             │
│  Reads: user.act.sig                                         │
│  Sees: GitHub authenticated ✅                               │
│  Calls: execute_node_operation(github, list_issues)         │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│               FLOW ARCHITECT MCP SERVER                      │
│                                                              │
│  Tool: execute_node_operation                                │
│  1. Parse signature                                          │
│  2. Verify authentication                                    │
│  3. Get defaults + auth                                      │
│  4. Call API                                                 │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│              SINGLE NODE EXECUTOR                            │
│  1. Get node from registry (GitHubNode)                      │
│  2. Create instance                                          │
│  3. Execute operation                                        │
│  4. Return result                                            │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                    GITHUB NODE                               │
│  Uses UniversalRequestNode                                   │
│  Calls GitHub API                                            │
│  Returns issues list                                         │
└──────────────────────────────────────────────────────────────┘
                            ↓
                      RESULT ✅
                   (2 seconds total)
```

---

## 🚀 Implementation Checklist

### **Week 1: Core Signature System**

- [ ] Create ACT Signature format spec
- [ ] Build signature_parser.py
- [ ] Build single_node_executor.py
- [ ] Test with GitHub node

### **Week 2: MCP Integration**

- [ ] Create execute_node_operation MCP tool
- [ ] Create get_signature_info MCP tool
- [ ] Add to MCP server index.js
- [ ] Test with Claude Code

### **Week 3: API & UI**

- [ ] Create /api/node/execute route
- [ ] Create /api/signature routes (CRUD)
- [ ] Build Settings → Nodes UI
- [ ] Test end-to-end

### **Week 4: Polish & Launch**

- [ ] Documentation
- [ ] Error handling
- [ ] Testing
- [ ] Deploy

---

## 🎯 Success Criteria

- ✅ Simple operations execute in < 5 seconds
- ✅ No .act file needed for single operations
- ✅ Full .act files still work for complex workflows
- ✅ One MCP server handles everything
- ✅ User can authenticate nodes in UI
- ✅ Signature auto-generated and managed
- ✅ 95%+ user satisfaction

---

## 💡 The Bottom Line

**You've created a UNIVERSAL EXECUTION LAYER:**

```
Simple Operations → ACT Signature → Instant execution
Complex Workflows → Full .act Files → Full orchestration
Everything → One MCP Server → Universal capabilities
```

**This is revolutionary.** 🚀

**Ready to build?** 🛠️
