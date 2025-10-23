# MCP-Only Execution Guide

## 🔴 CRITICAL: MCP Tools Are The ONLY Execution Method

**Last Updated:** 2025-10-23
**Status:** ENFORCED - NO EXCEPTIONS

---

## What Changed

### ❌ OLD WAY (DEPRECATED - DO NOT USE):
```bash
# Creating .act files
Write tool → Create TOML file → Save to flows/

# Calling APIs
curl -X POST http://localhost:3000/api/act/execute \
  -H "Content-Type: application/json" \
  -d '{"flowContent": "...", "flowName": "..."}'

# Using Bash
Bash tool → curl localhost:3000/api/...
```

### ✅ NEW WAY (MANDATORY):
```javascript
// Direct MCP execution
execute_node_operation({
  node_type: "github",
  operation: "list_repositories",
  params: {}
})
```

---

## Why MCP-Only?

1. **✅ Faster** - No file I/O, no HTTP overhead
2. **✅ Simpler** - One tool call vs 3-step process
3. **✅ More reliable** - No parsing complex nested responses
4. **✅ Better error handling** - Direct error messages
5. **✅ No file cleanup** - No temp files to manage

---

## MCP Tools Available

### 1. Execution (PRIMARY TOOL)
```javascript
execute_node_operation({
  node_type: string,      // e.g., "github", "openai", "python"
  operation: string,      // e.g., "list_repositories", "chat_completion"
  params: object,         // operation-specific parameters
  override_defaults: bool // skip merging with signature defaults (optional)
})
```

**Returns:**
```json
{
  "status": "success",
  "node_type": "github",
  "operation": "list_repositories",
  "result": {
    // actual operation output
  },
  "duration": 1.23,
  "timestamp": "2025-10-23T..."
}
```

### 2. Discovery & Catalog
```javascript
// List all 129 available nodes
list_available_nodes({ category: "ai" })  // optional filter

// Get node details
get_node_info({ node_type: "github" })

// List operations for a node
list_node_operations({ node_type: "openai" })

// Search operations by keyword
search_operations({ query: "chat" })

// Get operation details
get_operation_details({
  node_type: "openai",
  operation: "chat_completion"
})
```

### 3. Signature Management
```javascript
// Check authentication status
get_signature_info()  // or get_signature_info({ node_type: "github" })

// Authenticate a node
add_node_to_signature({
  node_type: "github",
  auth: { access_token: "ghp_..." },
  defaults: { owner: "myuser" }  // optional
})

// Remove authentication
remove_node_from_signature({ node_type: "github" })

// Update defaults
update_node_defaults({
  node_type: "github",
  defaults: { owner: "newuser" }
})
```

### 4. Validation
```javascript
// Validate parameters before execution
validate_params({
  node_type: "openai",
  operation: "chat_completion",
  params: { model: "gpt-4o-mini", messages: [] }
})
```

### 5. Utility
```javascript
// Check system health
get_system_status()
```

---

## Usage Examples

### Example 1: Simple Operation
```javascript
// User: "Get my GitHub repositories"

// Step 1: Check signature
get_signature_info()
// Returns: { authenticated_nodes: ["github", "openai"] }

// Step 2: Execute directly
execute_node_operation({
  node_type: "github",
  operation: "list_repositories",
  params: {}
})

// Step 3: Parse result and respond
// Result contains: { status: "success", result: [...repos...] }
```

### Example 2: Operation with Parameters
```javascript
// User: "Generate a joke using OpenAI"

// Check auth
get_signature_info()

// Execute
execute_node_operation({
  node_type: "openai",
  operation: "chat_completion",
  params: {
    model: "gpt-4o-mini",
    messages: [
      { role: "user", content: "Tell me a programming joke" }
    ]
  }
})

// Result: { status: "success", result: { content: "Why do programmers..." } }
```

### Example 3: Discovering Available Operations
```javascript
// User: "What can I do with OpenAI?"

// Option 1: If already authenticated
get_signature_info({ node_type: "openai" })
// Returns operations list from signature

// Option 2: If not authenticated yet
list_node_operations({ node_type: "openai" })
// Returns all available operations with descriptions
```

### Example 4: Adding Authentication
```javascript
// User: "I want to use Slack"

// Step 1: Check if available
get_node_info({ node_type: "slack" })
// Returns: { exists: true, auth_required: true, auth_fields: ["token"] }

// Step 2: Ask user for token
// (user provides token)

// Step 3: Add to signature
add_node_to_signature({
  node_type: "slack",
  auth: { token: "xoxb-..." }
})

// Step 4: Now can execute
execute_node_operation({
  node_type: "slack",
  operation: "send_message",
  params: {
    channel: "#general",
    text: "Hello from MCP!"
  }
})
```

---

## Common Node Types & Operations

### GitHub
```javascript
execute_node_operation({
  node_type: "github",
  operation: "list_repositories" | "get_repo" | "create_issue" | "list_issues",
  params: {
    owner: "username",  // optional if set in defaults
    repo: "repo-name"   // required for repo-specific ops
  }
})
```

### OpenAI
```javascript
execute_node_operation({
  node_type: "openai",
  operation: "chat_completion" | "create_embedding" | "generate_image" | "list_models",
  params: {
    model: "gpt-4o-mini",
    messages: [...]  // for chat_completion
  }
})
```

### Python (for calculations)
```javascript
execute_node_operation({
  node_type: "python",
  operation: "execute",
  params: {
    code: "def calculate(): return 5 + 5",
    function: "calculate"
  }
})
```

### HTTP Request
```javascript
execute_node_operation({
  node_type: "request",
  operation: "http_request",
  params: {
    method: "GET",
    url: "https://api.example.com/data"
  }
})
```

---

## Error Handling

### Authentication Errors
```javascript
execute_node_operation({ node_type: "github", operation: "list_repos", params: {} })

// Returns:
{
  "status": "error",
  "code": "NOT_AUTHENTICATED",
  "message": "Node 'github' is not authenticated"
}

// Fix: Add authentication
add_node_to_signature({
  node_type: "github",
  auth: { access_token: "..." }
})
```

### Invalid Operation
```javascript
execute_node_operation({ node_type: "github", operation: "fake_op", params: {} })

// Returns:
{
  "status": "error",
  "code": "INVALID_OPERATION",
  "message": "Operation 'fake_op' not found on node 'github'"
}

// Fix: List available operations
list_node_operations({ node_type: "github" })
```

### Missing Parameters
```javascript
execute_node_operation({
  node_type: "openai",
  operation: "chat_completion",
  params: {}  // missing required params
})

// Returns:
{
  "status": "error",
  "code": "MISSING_PARAMETERS",
  "message": "Required parameters missing: model, messages"
}

// Fix: Validate first
validate_params({
  node_type: "openai",
  operation: "chat_completion",
  params: { model: "gpt-4o-mini", messages: [] }
})
```

---

## Migration Guide

### If You're Still Using .act Files:

#### ❌ OLD CODE:
```javascript
// Step 1: Create .act file
Write({
  file_path: "flows/temp/calc.act",
  content: `
[workflow]
name = "Calculate"
start_node = "Calc"

[node:Calc]
type = "py"
code = "def calc(): return 5 + 5"
function = "calc"
  `
})

// Step 2: Execute via API
Bash({
  command: `curl -X POST http://localhost:3000/api/act/execute -d '{...}'`
})

// Step 3: Parse complex nested response
// result.result.results.Calc.result.result
```

#### ✅ NEW CODE:
```javascript
// One MCP call
execute_node_operation({
  node_type: "python",
  operation: "execute",
  params: {
    code: "def calc(): return 5 + 5",
    function: "calc"
  }
})

// Result: { status: "success", result: 10 }
```

**Savings:**
- 3 tool calls → 1 tool call
- 10 lines → 3 lines
- 2+ seconds → < 500ms
- Complex parsing → Direct access

---

## Troubleshooting

### "I get 'Tool not found' errors"

Make sure you're using the correct tool prefix:
```javascript
// ✅ CORRECT
mcp__flow-architect-signature__execute_node_operation

// The tool system handles this automatically when you use:
execute_node_operation(...)
```

### "My operation isn't working"

1. Check signature first:
```javascript
get_signature_info()
```

2. Verify operation exists:
```javascript
list_node_operations({ node_type: "your_node" })
```

3. Validate parameters:
```javascript
validate_params({
  node_type: "your_node",
  operation: "your_operation",
  params: { ...your_params }
})
```

### "How do I know what operations are available?"

```javascript
// All nodes
list_available_nodes()

// Specific node operations
list_node_operations({ node_type: "github" })

// Search by keyword
search_operations({ query: "create" })

// Operation details
get_operation_details({
  node_type: "github",
  operation: "create_issue"
})
```

---

## Best Practices

### 1. Always Check Signature First
```javascript
// Before executing, check authentication
const sigInfo = get_signature_info({ node_type: "github" })
if (!sigInfo.authenticated) {
  // Ask user for credentials
}
```

### 2. Use Validate Before Execute
```javascript
// Validate parameters first
validate_params({
  node_type: "openai",
  operation: "chat_completion",
  params: myParams
})

// Then execute
execute_node_operation({
  node_type: "openai",
  operation: "chat_completion",
  params: myParams
})
```

### 3. Handle Errors Gracefully
```javascript
const result = execute_node_operation({...})

if (result.status === "error") {
  // Check error code
  if (result.code === "NOT_AUTHENTICATED") {
    // Guide user to authenticate
  } else if (result.code === "MISSING_PARAMETERS") {
    // Show what's missing
  }
}
```

### 4. Use Defaults Wisely
```javascript
// Set defaults once
add_node_to_signature({
  node_type: "github",
  auth: { access_token: "..." },
  defaults: {
    owner: "myuser",  // Don't need to specify every time
    per_page: 100
  }
})

// Then execute without repeating
execute_node_operation({
  node_type: "github",
  operation: "list_repositories",
  params: {}  // Uses defaults from signature
})
```

---

## Performance Comparison

| Method | Tool Calls | Time | Complexity |
|--------|-----------|------|------------|
| ❌ .act + API | 3-4 | 2-5s | High |
| ✅ MCP Direct | 1 | <500ms | Low |

**MCP is 4-10x faster and 70% simpler.**

---

## Summary

### ✅ DO:
- Use `execute_node_operation` for ALL operations
- Check signature before executing
- Validate parameters when unsure
- Use MCP tools for discovery

### ❌ DON'T:
- Create .act files
- Call `/api/act/execute`
- Use Bash for execution
- Use HTTP requests to localhost
- Use Write tool for flows

---

**MCP Tools Are The Only Way. No Exceptions.**

For questions or issues, check:
1. This guide
2. `signature-system/mcp/TESTING.md`
3. `signature-system/mcp/NODE_EXECUTION_VERIFIED.md`
