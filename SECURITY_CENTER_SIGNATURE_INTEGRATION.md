# Security Center ↔ Signature System Integration Plan

**Date**: 2025-10-22
**Goal**: Use Security Center UI for node authentication that automatically syncs with `.act.sig` files

---

## 🎯 Current State

### Security Center (UI)
- **Location**: `/app/security-center` page
- **Components**: `NodesAuthSection`, `NodeAuthForm`, `NodeSelector`
- **API**: `/api/nodes/[nodeType]/auth` (POST/GET/DELETE)
- **Storage**: `auth-db.ts` - Local SQLite-like storage

### Signature System (Backend)
- **Location**: `signature-system/mcp/`
- **Tools**: 13 MCP tools for signature management
- **Storage**: `.act.sig` files (TOML format)
- **Used by**: Flow execution, MCP server

### The Problem
❌ **TWO separate systems** for authentication:
- Security Center saves to `auth-db`
- Signature system uses `.act.sig` files
- They don't talk to each other!

---

## 🔄 Integration Architecture

### Option A: Security Center → Signature (RECOMMENDED)

**Flow**:
```
User authenticates in Security Center
  ↓
POST /api/nodes/[nodeType]/auth
  ↓
1. Validate auth data
2. Save to auth-db (existing)
3. Call MCP tool: add_node_to_signature()  ← NEW!
  ↓
Signature file updated
  ↓
Flow execution uses authenticated node
```

**Benefits**:
- ✅ Single UI for authentication
- ✅ Signature file stays in sync
- ✅ No breaking changes to existing Security Center
- ✅ MCP tools handle signature format

---

## 📝 Implementation Steps

### Step 1: Add Signature Sync to Auth API

**File**: `app/api/nodes/[nodeType]/auth/route.ts`

**Changes**:
```typescript
import { executeMCPTool } from '@/lib/mcp-executor'; // NEW

export async function POST(request, { params }) {
  // ... existing validation ...

  // Save to database (existing)
  const result = saveNodeAuth(node.id, authData);

  // NEW: Sync with signature file
  try {
    await executeMCPTool('add_node_to_signature', {
      node_type: node.id,
      auth: authData,
      defaults: {} // Optional
    });
    console.log(`✅ Synced ${node.id} to signature file`);
  } catch (error) {
    console.error(`⚠️  Failed to sync to signature:`, error);
    // Don't fail the request - auth is still saved in DB
  }

  return NextResponse.json({
    success: true,
    nodeType: node.id,
    enabled: true,
    message: 'Authentication saved and synced to signature'
  });
}
```

**For DELETE**:
```typescript
export async function DELETE(request, { params }) {
  // ... existing deletion ...

  const result = deleteNodeAuth(nodeType);

  // NEW: Remove from signature file
  try {
    await executeMCPTool('remove_node_from_signature', {
      node_type: nodeType
    });
    console.log(`✅ Removed ${nodeType} from signature file`);
  } catch (error) {
    console.error(`⚠️  Failed to remove from signature:`, error);
  }

  return NextResponse.json({
    success: true,
    nodeType,
    enabled: false,
    message: 'Authentication removed and signature updated'
  });
}
```

---

### Step 2: Create MCP Tool Executor

**File**: `lib/mcp-executor.ts` (NEW)

```typescript
import { spawn } from 'child_process';
import path from 'path';

const MCP_INDEX = path.join(process.cwd(), 'signature-system/mcp/index.js');

export async function executeMCPTool(toolName: string, params: any): Promise<any> {
  return new Promise((resolve, reject) => {
    // Spawn Node.js to run MCP tool
    const child = spawn('node', [MCP_INDEX, toolName, JSON.stringify(params)], {
      cwd: process.cwd(),
      env: {
        ...process.env,
        NODE_ENV: 'production'
      }
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    child.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          reject(new Error(`Failed to parse MCP output: ${stdout}`));
        }
      } else {
        reject(new Error(`MCP tool failed: ${stderr}`));
      }
    });

    child.on('error', reject);
  });
}
```

---

### Step 3: Update MCP Index for Direct Execution

**File**: `signature-system/mcp/index.js`

Add command-line execution mode:

```javascript
// At the bottom of the file, add:

// Allow direct execution from command line
if (require.main === module) {
  const [toolName, paramsJson] = process.argv.slice(2);

  if (!toolName || !paramsJson) {
    console.error('Usage: node index.js <toolName> <paramsJson>');
    process.exit(1);
  }

  try {
    const params = JSON.parse(paramsJson);

    // Map tool names to functions
    const tools = {
      add_node_to_signature: require('./tools/signature/add-node').addNodeToSignature,
      remove_node_from_signature: require('./tools/signature/remove-node').removeNodeFromSignature,
      get_signature_info: require('./tools/signature/get-signature-info').getSignatureInfo,
      // ... other tools
    };

    if (!tools[toolName]) {
      throw new Error(`Unknown tool: ${toolName}`);
    }

    const result = await tools[toolName](params);
    console.log(JSON.stringify(result, null, 2));
    process.exit(0);
  } catch (error) {
    console.error(JSON.stringify({ error: error.message }));
    process.exit(1);
  }
}
```

---

### Step 4: Update Flow Execution to Check Signature FIRST

**File**: `app/api/act/execute/route.ts`

Before executing flows, check signature:

```typescript
// Add at the top of POST handler
import { executeMCPTool } from '@/lib/mcp-executor';

export async function POST(request: NextRequest) {
  // ... existing code ...

  // NEW: Check if flow uses authenticated nodes
  const signatureInfo = await executeMCPTool('get_signature_info', {});
  const authenticatedNodes = signatureInfo.authenticated_nodes || {};

  // Parse flow content to find node types used
  const nodesInFlow = extractNodesFromFlow(flowContent);

  // Check if all required nodes are authenticated
  for (const nodeType of nodesInFlow) {
    if (requiresAuth(nodeType) && !authenticatedNodes[nodeType]?.authenticated) {
      return NextResponse.json({
        success: false,
        error: `Node ${nodeType} requires authentication. Please configure it in Security Center.`,
        nodeType,
        requiresAuth: true
      }, { status: 403 });
    }
  }

  // ... continue with execution ...
}
```

---

## 🎨 UI Updates (Optional)

### Add Signature Status Indicator

**File**: `components/security-center/NodesAuthSection.tsx`

Add badge showing if node is in signature:

```tsx
{nodes.map(node => (
  <Card key={node.id}>
    <CardHeader>
      <div className="flex items-center justify-between">
        <h3>{node.displayName}</h3>
        <div className="flex gap-2">
          {node.userEnabled && (
            <Badge variant="success">Authenticated</Badge>
          )}
          {node.inSignature && (
            <Badge variant="outline">In Signature</Badge>
          )}
        </div>
      </div>
    </CardHeader>
  </Card>
))}
```

---

## 🧪 Testing Plan

### Test 1: Add Authentication
1. Open Security Center
2. Click "Add Authentication"
3. Select GitHub node
4. Enter access token
5. Click Save
6. ✅ Check: `signatures/user.act.sig` contains GitHub section
7. ✅ Check: Can execute GitHub operations without approval prompt

### Test 2: Remove Authentication
1. Open Security Center
2. Find authenticated node
3. Click "Remove"
4. ✅ Check: Node removed from signature file
5. ✅ Check: Flow execution asks for authentication

### Test 3: Flow Execution
1. Create flow using authenticated GitHub node
2. Execute flow
3. ✅ Check: No approval prompts
4. ✅ Check: Operation executes successfully

---

## 📊 Benefits

### For Users
- ✅ Single UI for all node authentication
- ✅ Visual management in Security Center
- ✅ No manual `.act.sig` file editing
- ✅ No approval prompts after authentication

### For System
- ✅ Signature file is single source of truth
- ✅ Security Center and flow execution stay in sync
- ✅ MCP tools used for all signature operations
- ✅ Consistent authentication across desktop app

---

## 🚀 Next Steps

1. **Create `lib/mcp-executor.ts`** - Helper to execute MCP tools from Node.js
2. **Update `app/api/nodes/[nodeType]/auth/route.ts`** - Add signature sync on POST/DELETE
3. **Update `signature-system/mcp/index.js`** - Add CLI mode for direct execution
4. **Test integration** - Verify auth flows from Security Center to signature
5. **Update `useNodeAuth` hook** - Add signature status checking
6. **Add UI indicators** - Show which nodes are in signature

---

**Estimated Time**: 4-6 hours
**Priority**: High
**Status**: Ready to implement

---

**Alternative Approach**: Read signature file directly instead of using auth-db, making signature the ONLY storage. This would be cleaner but requires more refactoring.
