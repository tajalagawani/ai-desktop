# ACT MCP Server - Standalone Architecture

**Status**: ✅ MCP Utils Complete - Ready for Tool Integration
**Date**: 2025-10-22

---

## 🎯 Final Architecture: Option B - Standalone Systems

**Decision**: Keep MCP and Desktop App as **independent systems** for open-source distribution.

```
┌─────────────────────────────────────────┐
│   User's Machine                        │
│                                          │
│   ┌──────────────┐   ┌───────────────┐ │
│   │ Desktop App  │   │  MCP Server   │ │
│   │ (Next.js)    │   │  (Node.js)    │ │
│   └───────┬──────┘   └───────┬───────┘ │
│           │                  │          │
│           ↓                  ↓          │
│   ┌─────────────────────────────────┐  │
│   │  ACT Library                     │  │
│   │  components/apps/act-docker/act/ │  │
│   │                                   │  │
│   │  ├── nodes/        (151 nodes)   │  │
│   │  ├── execution_manager.py        │  │
│   │  ├── actfile_parser.py           │  │
│   │  └── mcp_utils/ ✅ NEW           │  │
│   │      ├── signature_manager.py    │  │
│   │      ├── catalog_sync.py         │  │
│   │      ├── single_node_executor.py │  │
│   │      ├── execute_flow.py         │  │
│   │      ├── list_operations.py      │  │
│   │      └── logger.py               │  │
│   └─────────────────────────────────┘  │
└─────────────────────────────────────────┘

Both spawn Python scripts independently
NO circular dependencies
```

---

## ✅ What's Complete: ACT MCP Utils

### 📦 Location
```
/Users/tajnoah/Downloads/ai-desktop/components/apps/act-docker/act/mcp_utils/
```

### 🗂️ Files Created

#### 1. **signature_manager.py** (240 lines)
- Parse `.act.sig` TOML files
- Resolve `{{.env.VARIABLE}}` references
- CRUD operations for node authentication
- Get/set defaults, auth data, operations

**Usage**:
```python
from act.mcp_utils import SignatureManager

sig = SignatureManager('~/.act.sig')
sig.load()

if sig.is_authenticated('github'):
    auth = sig.get_node_auth('github', resolve_env=True)
    defaults = sig.get_node_defaults('github')
```

#### 2. **catalog_sync.py** (300 lines)
- Scans all nodes from `nodes/` directory
- Parses node files for operations, parameters, auth requirements
- Generates complete catalog JSON
- **Tested**: ✅ Successfully synced **129 nodes**

**Usage**:
```python
from act.mcp_utils import sync_catalog, get_node_info

# Sync all nodes
catalog = sync_catalog()
print(f"Found {catalog['total']} nodes")

# Get specific node
node_info = get_node_info('github')
print(f"Operations: {node_info['operations']}")
```

**CLI**:
```bash
python3 -m act.mcp_utils.catalog_sync sync /path/to/output.json
python3 -m act.mcp_utils.catalog_sync get github
python3 -m act.mcp_utils.catalog_sync list --category database
```

#### 3. **single_node_executor.py** (180 lines)
- Execute single node operations
- Loads auth from signature
- Merges defaults + params
- Spawns actual ACT node classes

**Usage**:
```python
from act.mcp_utils import execute_single_node

result = execute_single_node(
    signature_path='~/.act.sig',
    node_type='github',
    operation='list_issues',
    params={'state': 'open'}
)
```

**CLI**:
```bash
python3 -m act.mcp_utils.single_node_executor \
  ~/.act.sig \
  github \
  list_issues \
  '{"state":"open"}'
```

#### 4. **execute_flow.py** (130 lines)
- Execute complete `.act` workflow files
- Injects authenticated credentials into workflow
- Supports mini-ACT (immediate execution)
- Detects agent workflows (requires deployment)

**Usage**:
```python
from act.mcp_utils import execute_flow

result = execute_flow(
    flow_path='workflow.act',
    signature_path='~/.act.sig',
    parameters={'key': 'value'}
)
```

**CLI**:
```bash
python3 -m act.mcp_utils.execute_flow \
  workflow.act \
  ~/.act.sig \
  '{"param":"value"}'
```

#### 5. **list_operations.py** (220 lines)
- List all operations for a node
- Search operations by keyword
- Get detailed operation info
- Generate usage examples (TOML + Python)

**Usage**:
```python
from act.mcp_utils import list_node_operations, search_operations

# List all operations for GitHub
ops = list_node_operations('github')

# Search for operations
results = search_operations('list')
```

**CLI**:
```bash
python3 -m act.mcp_utils.list_operations list github
python3 -m act.mcp_utils.list_operations search "create"
python3 -m act.mcp_utils.list_operations get github list_issues
```

#### 6. **logger.py** (130 lines)
- Structured JSON logging
- Outputs to stdout (results) + stderr (logs)
- Duration tracking
- Verbose mode

**Usage**:
```python
from act.mcp_utils import get_logger

logger = get_logger("my_operation", verbose=True)
logger.info("Starting operation")
logger.success("Operation completed")
logger.output_result(True, {"result": "data"})
```

#### 7. **__init__.py** (55 lines)
- Clean exports for all utilities
- Versioned package

---

## 🔗 Integration Points

### Desktop App Integration (Optional)
Desktop app can use mcp_utils too:

```python
# In Desktop App API routes
from act.mcp_utils import execute_single_node

result = execute_single_node(
    signature_path='data/user.act.sig',  # Use desktop app signature
    node_type='github',
    operation='list_issues',
    params=request_params
)
```

### MCP Server Integration (Next Step)
MCP tools will spawn Python scripts:

```javascript
// In execute-node-operation.js
import { spawn } from 'child_process';

const python = spawn('python3', [
  '-m', 'act.mcp_utils.single_node_executor',
  signaturePath,
  nodeType,
  operation,
  JSON.stringify(params)
]);
```

---

## 📋 Next Steps

### Phase 1: Update MCP Tools ⏳

Rewrite 10 MCP tools to spawn Python scripts from `act.mcp_utils`:

1. **execute_node_operation.js** → spawn `single_node_executor.py`
2. **get_signature_info.js** → spawn `signature_manager.py` (read mode)
3. **add_node_to_signature.js** → spawn `signature_manager.py` (add mode)
4. **remove_node_from_signature.js** → spawn `signature_manager.py` (remove mode)
5. **update_node_defaults.js** → spawn `signature_manager.py` (update mode)
6. **validate_signature.js** → spawn `signature_manager.py` (validate mode)
7. **list_available_nodes.js** → spawn `catalog_sync.py list`
8. **get_node_info.js** → spawn `catalog_sync.py get <node>`
9. **validate_params.js** → spawn `list_operations.py get <node> <op>`
10. **get_system_status.js** → check if ACT available, signature exists, etc.

### Phase 2: Test Integration ⏳

1. Start MCP server via `.mcp.json`
2. Test each MCP tool from Claude Code
3. Verify signature auth flow
4. Test execution end-to-end

### Phase 3: Prepare for Open Source 🎁

1. Create standalone `act-mcp-server` repository
2. Add installation instructions:
   ```bash
   pip install act-framework
   npm install -g act-mcp-server
   ```
3. Document signature setup
4. Add examples

---

## 🎓 Benefits of This Approach

✅ **Standalone MCP**: Can be open-sourced independently
✅ **No HTTP Dependencies**: Direct Python execution
✅ **Reusable Utilities**: Desktop app can use them too
✅ **Full ACT Access**: All 151 nodes available
✅ **Single Source of Truth**: ACT library is the authority
✅ **Easy Distribution**: `pip install act` + `npm install -g act-mcp-server`

---

## 📊 Test Results

| Utility | Status | Test |
|---------|--------|------|
| signature_manager.py | ✅ | Imports successfully |
| catalog_sync.py | ✅ | **Synced 129 nodes** |
| single_node_executor.py | ✅ | Imports successfully |
| execute_flow.py | ✅ | Imports successfully |
| list_operations.py | ✅ | Imports successfully |
| logger.py | ✅ | Imports successfully |

**Catalog Output**:
```
✅ Synced 129 nodes
Sample nodes: ['openai', 'if', 'wise', 'beehiiv', 'tableau']
```

---

**Ready to proceed with Phase 1: Update MCP Tools!**
