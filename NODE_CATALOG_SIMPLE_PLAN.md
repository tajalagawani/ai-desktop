# Simple Node Catalog Plan

## 🎯 Goal
Parse 164 Python node files directly from filesystem to create a comprehensive, LLM-friendly catalog.

## 📁 Where Are The Files?
**Path:** `components/apps/act-docker/act/nodes/*.py`
**Count:** 164 node files

## 🔍 What We Need To Extract

For each node file, extract:

### 1. Basic Info
- **Node ID**: From filename (e.g., `MongoDBNode.py` → `mongodb`)
- **Display Name**: Format the ID nicely
- **Description**: From class docstring or `get_schema().description`

### 2. Operations
- Look for `class XyzOperation:` with constants
- Example: `INSERT_ONE = "insert_one"`
- Categorize: create, read, update, delete, other

### 3. Parameters
- From `get_schema().parameters` definitions
- Extract: name, type, required, description, default

### 4. Capabilities
- Infer from operation names:
  - `canRead`: has find/get/read operations
  - `canWrite`: has insert/create/write operations
  - `canUpdate`: has update/modify operations
  - `canDelete`: has delete/remove operations

### 5. Authentication
- Find parameters with: auth, token, key, password, credential
- Mark as secret parameters

## 🛠️ Implementation Strategy

### Step 1: Simple File Reader (TypeScript)
```typescript
// lib/node-parser.ts

import fs from 'fs';
import path from 'path';

const NODES_DIR = 'components/apps/act-docker/act/nodes';

function getAllNodeFiles(): string[] {
  return fs.readdirSync(NODES_DIR)
    .filter(f => f.endsWith('Node.py'))
    .map(f => path.join(NODES_DIR, f));
}
```

### Step 2: Simple Text Parser
Parse Python files as text - look for patterns:

```typescript
function parseNodeFile(filePath: string) {
  const content = fs.readFileSync(filePath, 'utf-8');

  return {
    id: extractNodeId(content),
    operations: extractOperations(content),
    description: extractDescription(content),
    // ...
  };
}
```

### Step 3: Pattern Matching

**Find Operation Classes:**
```python
# Pattern to find:
class MongoDBOperation:
    INSERT_ONE = "insert_one"
    FIND = "find"
    UPDATE_ONE = "update_one"
```

**Find Parameters:**
```python
# Pattern to find:
NodeParameter(
    name="connection_string",
    type=NodeParameterType.STRING,
    description="MongoDB connection URI",
    required=True
)
```

**Find Node Type:**
```python
# Pattern to find:
def get_schema(self) -> NodeSchema:
    return NodeSchema(
        node_type="mongodb",
        description="..."
    )
```

## 📊 Output Structure

```json
{
  "nodes": [
    {
      "id": "mongodb",
      "displayName": "MongoDB",
      "description": "NoSQL database operations",
      "operations": [
        {
          "name": "insert_one",
          "category": "create"
        },
        {
          "name": "find",
          "category": "read"
        }
      ],
      "parameters": [
        {
          "name": "connection_string",
          "type": "string",
          "required": true,
          "secret": true
        }
      ],
      "capabilities": {
        "canRead": true,
        "canWrite": true,
        "canDelete": true
      }
    }
  ]
}
```

## 🔗 API Endpoints

### 1. GET /api/nodes
- Returns all nodes
- Filter by: `?search=mongo&capability=canWrite`

### 2. GET /api/nodes/[nodeId]
- Returns complete info for one node

### 3. GET /api/nodes/[nodeId]/operations
- Returns list of operations for a node

## 📝 Parsing Strategies

### Strategy A: Regex Patterns
Simple string matching for common patterns.

**Pros:** Fast, no dependencies
**Cons:** Might miss some complex cases

### Strategy B: AST Parser
Use a Python AST parser in JavaScript.

**Pros:** Accurate
**Cons:** More complex, needs library

### Recommended: Start with A, upgrade to B if needed

## 🚀 Implementation Steps

### Phase 1: Basic File Parser (30 min)
1. Read all node files from disk
2. Extract node IDs from filenames
3. Extract descriptions from docstrings
4. Test on 5 sample files

### Phase 2: Operation Extraction (1 hour)
1. Find Operation classes with regex
2. Extract operation constants
3. Categorize operations
4. Test on 10 sample files

### Phase 3: Parameter Extraction (1 hour)
1. Find NodeParameter definitions
2. Extract name, type, required
3. Mark secret parameters
4. Test on all files

### Phase 4: API Layer (30 min)
1. Create /api/nodes endpoint
2. Add filtering capabilities
3. Add caching (5 min TTL)
4. Test with Flow Architect

### Phase 5: Complete Catalog (30 min)
1. Run on all 164 files
2. Generate complete JSON
3. Cache results
4. Update Flow Architect to use it

## ⚡ Quick Implementation

```typescript
// lib/node-parser.ts
import fs from 'fs';
import path from 'path';

const NODES_DIR = 'components/apps/act-docker/act/nodes';

export interface NodeInfo {
  id: string;
  displayName: string;
  description: string;
  operations: Array<{name: string; category: string}>;
  parameters: Array<{name: string; type: string; required: boolean}>;
  capabilities: {
    canRead: boolean;
    canWrite: boolean;
    canUpdate: boolean;
    canDelete: boolean;
  };
}

export function parseAllNodes(): NodeInfo[] {
  const files = fs.readdirSync(NODES_DIR)
    .filter(f => f.endsWith('Node.py'));

  return files.map(file => {
    const content = fs.readFileSync(path.join(NODES_DIR, file), 'utf-8');
    return parseNode(content, file);
  });
}

function parseNode(content: string, filename: string): NodeInfo {
  const id = filename.replace('Node.py', '').toLowerCase();

  return {
    id,
    displayName: formatName(id),
    description: extractDescription(content),
    operations: extractOperations(content),
    parameters: extractParameters(content),
    capabilities: inferCapabilities(content)
  };
}

function extractOperations(content: string) {
  const operations = [];

  // Find: OPERATION_NAME = "operation_value"
  const regex = /^\s*([A-Z_]+)\s*=\s*["']([a-z_]+)["']/gm;
  let match;

  while ((match = regex.exec(content)) !== null) {
    const name = match[2];
    operations.push({
      name,
      category: inferCategory(name)
    });
  }

  return operations;
}

function inferCategory(operation: string): string {
  if (/insert|create|add|post/.test(operation)) return 'create';
  if (/find|get|read|select|list/.test(operation)) return 'read';
  if (/update|modify|put|patch/.test(operation)) return 'update';
  if (/delete|remove|drop/.test(operation)) return 'delete';
  return 'other';
}

// ... more helper functions
```

## 🎯 Success Criteria

- [ ] Reads all 164 node files
- [ ] Extracts operations for 90%+ of nodes
- [ ] Extracts parameters for 80%+ of nodes
- [ ] API responds in < 100ms (cached)
- [ ] LLM can find any node by search
- [ ] LLM can see all operations for a node

## ⏱️ Time Estimate

- Total: **3-4 hours**
- Basic parser: 30 min
- Operation extraction: 1 hour
- Parameter extraction: 1 hour
- API + testing: 1 hour
- Integration: 30 min

## 🔄 Next Steps

1. Create `lib/node-parser.ts` with file reader
2. Test on 5 sample nodes
3. Add operation extraction
4. Add parameter extraction
5. Create API endpoints
6. Update Flow Architect to use dynamic catalog
7. Remove hardcoded node-catalog.json

---

**Simple. Direct. No Docker. Just read files and parse them.**
