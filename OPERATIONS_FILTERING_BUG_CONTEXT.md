# Operations Filtering Bug - Complete Context

## THE CRITICAL BUG

**User selects 1 operation in UI → Signature file contains ALL operations**

## What Should Happen

1. User opens Security Center
2. User clicks "Add Node to Signature"
3. User selects a node type (e.g., "actionnetwork")
4. User fills in auth credentials
5. Operations auto-load in Configuration tab
6. User selects ONLY 1 operation (e.g., "list_people")
7. User clicks "Add to Signature"
8. **EXPECTED**: Signature file should contain ONLY "list_people" operation
9. **ACTUAL**: Signature file contains ALL 23 operations!

## The Data Flow

### Frontend → Backend Request

**File**: `/Users/tajnoah/Downloads/ai-desktop/components/apps/security-center.tsx`

UI sends this to `/api/signature`:
```json
{
  "node_type": "actionnetwork",
  "auth": {
    "parameters": "vdfsd",
    "api_key": "fdsfds"
  },
  "defaults": {},
  "operations": ["list_people"]  // ← ONLY 1 OPERATION SELECTED
}
```

### Backend API Endpoint

**File**: `/Users/tajnoah/Downloads/ai-desktop/app/api/signature/route.ts`

This endpoint receives the request and calls MCP tool:
```typescript
const result = await executeMCPTool('add_node_to_signature', {
  node_type: body.node_type,
  auth: body.auth,
  defaults: body.defaults || {},
  operations: body.operations, // ← Passes operations array
  signature_path: body.signature_path || 'signatures/user.act.sig'
});
```

### MCP Tool Execution

**File**: `/Users/tajnoah/Downloads/ai-desktop/signature-system/mcp/index.js`

Routes to the add-node tool.

### Add Node Tool (THE BUG LOCATION)

**File**: `/Users/tajnoah/Downloads/ai-desktop/signature-system/mcp/tools/signature/add-node.js`

This is where the bug exists. The tool:

1. **Receives**: `operations: ["list_people"]`
2. **Base64 Encodes**: To avoid JSON escaping issues
3. **Generates Python Code**: Embeds the base64 string in Python
4. **Python Executes**: Decodes and filters operations
5. **Problem**: Despite filtering logic, ALL operations end up in signature

## The Bug History

### Original Code (BUGGY)
```javascript
// Lines 84-103 - Original version
operations = {}
for op in node_info.get('operations', []):
    operations[op['name']] = {
        "description": f"{op['displayName']} operation",
        "category": op.get('category', 'other')
    }
```

**Problem**: Ignored the `operations` parameter completely, always added ALL operations.

### First Fix Attempt (BUGGY - JSON Escaping)
```javascript
const operationsJson = operations ? JSON.stringify(operations) : null;

// Python:
selected_operations = ${operationsJson} if ${operationsJson} else None

if selected_operations:
    # Only include selected operations
    for op in all_operations:
        if op['name'] in selected_operations:
            operations[op['name']] = {...}
```

**Problem**: JSON escaping broke the string interpolation.

### Second Fix Attempt (BUGGY - Base64 Null)
```javascript
const operationsJson = operations ? Buffer.from(JSON.stringify(operations)).toString('base64') : null;

// Python:
selected_operations = json.loads(base64.b64decode('${operationsJson}').decode('utf-8')) if '${operationsJson}' else None
```

**Problem**: When `operationsJson` is `null`, it becomes string `'null'` in Python, and `if 'null'` is True (non-empty string), so it tries to decode 'null' as base64 → UnicodeDecodeError.

### Third Fix Attempt (BUGGY - Undefined)
```javascript
const hasOperations = operations && operations.length > 0;
const operationsJson = hasOperations ? Buffer.from(JSON.stringify(operations)).toString('base64') : '';

// Python:
selected_operations = json.loads(base64.b64decode('${operationsJson}').decode('utf-8')) if ${hasOperations} else None
```

**Problem**: `${hasOperations}` becomes JavaScript literal `undefined` instead of Python boolean `False` → NameError: name 'undefined' is not defined.

### Fourth Fix (CURRENT - Should Work)
```javascript
const hasOperations = operations && operations.length > 0;
const operationsJson = hasOperations ? Buffer.from(JSON.stringify(operations)).toString('base64') : '';

// Python:
has_operations = ${hasOperations ? 'True' : 'False'}
selected_operations = json.loads(base64.b64decode('${operationsJson}').decode('utf-8')) if has_operations else None

if selected_operations:
    # Only include selected operations
    for op in all_operations:
        if op['name'] in selected_operations:
            operations[op['name']] = {
                "description": f"{op['displayName']} operation",
                "category": op.get('category', 'other')
            }
else:
    # Include all operations (default)
    for op in all_operations:
        operations[op['name']] = {
            "description": f"{op['displayName']} operation",
            "category": op.get('category', 'other')
        }
```

**Expected**: Should work! When user selects 1 operation:
- `hasOperations = true`
- `operationsJson = "WyJsaXN0X3Blb3BsZSJd"` (base64 of `["list_people"]`)
- `has_operations = True` in Python
- `selected_operations = ["list_people"]` after decoding
- Loop only adds operations where `op['name'] in ["list_people"]`

## The Python Filtering Logic

**Critical Section** (lines 89-103 in add-node.js):

```python
if selected_operations:
    # Only include selected operations
    for op in all_operations:
        if op['name'] in selected_operations:
            operations[op['name']] = {
                "description": f"{op['displayName']} operation",
                "category": op.get('category', 'other')
            }
else:
    # Include all operations (default)
    for op in all_operations:
        operations[op['name']] = {
            "description": f"{op['displayName']} operation",
            "category": op.get('category', 'other')
        }
```

**What Should Happen**:
- If `selected_operations = ["list_people"]`
- Loop through `all_operations` (all 23 operations from catalog)
- Check: `if "list_people" in ["list_people"]` → True, add it
- Check: `if "create_event" in ["list_people"]` → False, skip
- Check: `if "update_person" in ["list_people"]` → False, skip
- Result: `operations` dict should have only 1 key: `"list_people"`

## Files Involved

1. **Frontend UI**: `/Users/tajnoah/Downloads/ai-desktop/components/apps/security-center.tsx`
   - Collects user input
   - Sends POST to `/api/signature`
   - Has comprehensive logging (see console)

2. **API Endpoint**: `/Users/tajnoah/Downloads/ai-desktop/app/api/signature/route.ts`
   - Receives POST request
   - Calls MCP tool via `executeMCPTool()`
   - NO LOGGING (needs to be added)

3. **MCP Index**: `/Users/tajnoah/Downloads/ai-desktop/signature-system/mcp/index.js`
   - Routes tool calls
   - NO LOGGING (needs to be added)

4. **Add Node Tool**: `/Users/tajnoah/Downloads/ai-desktop/signature-system/mcp/tools/signature/add-node.js`
   - THE BUG IS HERE
   - Generates Python code
   - NO LOGGING (needs to be added)

5. **Python Executor**: `/Users/tajnoah/Downloads/ai-desktop/signature-system/mcp/lib/python-executor.js`
   - Executes Python code
   - Returns stdout/stderr
   - NO LOGGING (needs to be added)

6. **Signature File**: `/Users/tajnoah/Downloads/ai-desktop/signature-system/signatures/user.act.sig`
   - Final output - should contain ONLY selected operations
   - Currently contains ALL operations (the bug!)

## What Needs Logging

### In add-node.js:
```javascript
console.log('[ADD-NODE] Received args:', JSON.stringify(args, null, 2));
console.log('[ADD-NODE] hasOperations:', hasOperations);
console.log('[ADD-NODE] operationsJson (base64):', operationsJson);
console.log('[ADD-NODE] Generated Python code:', pythonCode);
console.log('[ADD-NODE] Python execution result:', JSON.stringify(result, null, 2));
```

### In Python code (embedded):
```python
print(f"[PYTHON] selected_operations: {selected_operations}", file=sys.stderr)
print(f"[PYTHON] all_operations count: {len(all_operations)}", file=sys.stderr)
print(f"[PYTHON] Filtering: {selected_operations is not None}", file=sys.stderr)
print(f"[PYTHON] Final operations count: {len(operations)}", file=sys.stderr)
print(f"[PYTHON] Final operations keys: {list(operations.keys())}", file=sys.stderr)
```

### In API route:
```javascript
console.log('[API /signature] Received request:', JSON.stringify(body, null, 2));
console.log('[API /signature] Calling MCP tool with:', { node_type, auth: '***', defaults, operations });
console.log('[API /signature] MCP result:', JSON.stringify(result, null, 2));
```

## How to Test

1. Open Security Center
2. Click "Add Node to Signature"
3. Select "Actionnetwork" node
4. Fill in dummy auth: `parameters: test`, `api_key: test`
5. Wait for operations to auto-load
6. Select ONLY "list_people" operation (uncheck all others or select only this one)
7. Click "Add to Signature"
8. Open `/Users/tajnoah/Downloads/ai-desktop/signature-system/signatures/user.act.sig`
9. **EXPECTED**: Should see only `[node:actionnetwork.operations.list_people]`
10. **ACTUAL (BUG)**: Seeing all 23+ operations

## Expected Signature File Output

```toml
[signature]
version = "1.0.0"
created_at = "2025-10-22T..."
updated_at = "2025-10-22T..."

[metadata]
authenticated_nodes = 1
last_updated = "2025-10-22T..."

["node:actionnetwork"]
type = "actionnetwork"
enabled = true
authenticated = true
display_name = "Actionnetwork"
description = "..."
added_at = "2025-10-22T..."

["node:actionnetwork.auth"]
parameters = "test"
api_key = "test"

["node:actionnetwork.operations".list_people]  # ← ONLY THIS ONE!
description = "List People operation"
category = "read"
```

## Current Signature File Output (BUG)

```toml
# ... same header ...

["node:actionnetwork.operations".list_people]
description = "List People operation"
category = "read"

["node:actionnetwork.operations".create_event]  # ← SHOULD NOT BE HERE!
description = "Create Event operation"
category = "write"

["node:actionnetwork.operations".update_person]  # ← SHOULD NOT BE HERE!
description = "Update Person operation"
category = "write"

# ... ALL OTHER OPERATIONS (should not be here!)
```

## Next Steps

1. Add comprehensive logging to backend
2. Test with 1 operation selected
3. Check logs to see:
   - What `operations` array is received
   - What `selected_operations` is after decoding
   - What the filtering loop does
   - What the final `operations` dict contains
4. Find where the filtering is failing
5. Fix it!

## User's Frustration Level

**CRITICAL** - User has said:
- "i select only 1 operation i see several! in th sig"
- "i restart all the app and i deleted all the node form sig and i pick new one and select single operation and i open it i find all the operations of that node"

This is the #1 priority bug to fix. Everything else in Security Center works, but this filtering is broken.
