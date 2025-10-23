# Flow Architect Instruction Flow - Complete Analysis

**Created**: 2025-10-23
**Branch**: `fix/agent-workflow-and-inspection`
**Purpose**: Document all instruction files, loading order, and identify where instructions might be getting overridden

---

## 🎯 Executive Summary

### The Problem
The Flow Architect agent was:
1. ❌ Using `curl` via Bash instead of MCP tools
2. ❌ Getting UNKNOWN_OPERATION errors by guessing operation names
3. ❌ Taking 64 turns / 108 seconds for simple queries
4. ❌ **CRITICAL**: Showing auth form BEFORE creating workflow (should be workflow first, form last)

### Root Causes Identified
1. **Agent file not updating**: `setup-agent.js` was skipping copy if file existed in `~/.claude/agents/`
2. **No node inspection**: Agent wasn't calling `list_node_operations()` to see available operations
3. **Context files overriding**: Old instructions in context files loaded after main agent file
4. **Curl not blocked**: No explicit warnings about curl/wget being blocked
5. **Complex workflow**: Instructions were too complicated, needed simple TODO-based approach
6. **Form timing issue**: ❌ **STILL UNRESOLVED** - Agent calls `request_parameters` before creating workflow file

---

## 📚 Instruction Loading Order

When Claude CLI processes a query, it loads instructions in this exact order:

### 1️⃣ Global Claude CLI Config
**Location**: `~/.claude/CLAUDE.md` (empty file)
**When Loaded**: First, always
**Priority**: Lowest (can be overridden by everything else)
**Current Status**: Empty (0 bytes)

### 2️⃣ Project Root CLAUDE.md
**Location**: `/Users/tajnoah/Downloads/ai-desktop/CLAUDE.md`
**When Loaded**: Second, when in project directory
**Priority**: Medium-Low
**Key Content**:
```markdown
🚨🚨🚨 **MANDATORY TODO WORKFLOW** 🚨🚨🚨

**FOR EVERY USER QUERY:**

1. **Create TODO list** with TodoWrite:
   - Check signature (get_signature_info)
   - [Based on signature results, add more todos]

2. **Execute first TODO**: Call `get_signature_info()`

3. **Based on signature, update TODO list** with one of:
   - If nodes authenticated → Add todo: "Inspect node operations" → "Create workflow" → "Execute"
   - If nodes not authenticated → Add todo: "Authenticate node X" → "Inspect operations" → "Create workflow"
   - If nodes missing → Add todo: "Check catalog for node" → "Authenticate" → "Inspect" → "Create workflow"
```

**Purpose**: Sets CRITICAL rules before any other instructions load
- Blocks curl/wget via Bash
- Enforces TODO workflow
- Requires python node for API calls

### 3️⃣ Flow Architect Project CLAUDE.md
**Location**: `/Users/tajnoah/Downloads/ai-desktop/flow-architect/CLAUDE.md`
**When Loaded**: Third, when working in flow-architect directory
**Priority**: Medium
**Key Content**:
```markdown
## 🔴 CRITICAL - Your Instructions Are Modular

**DO NOT use the instructions in this file for actual execution.**

Instead, **immediately read and follow** the modular routing agent:

📍 **Primary Instructions:** `.claude/agents/flow-architect.md`
```

**Purpose**: Delegates to the modular routing agent system

### 4️⃣ Flow Architect Routing Agent (PRIMARY INSTRUCTIONS)
**Location**: `/Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/agents/flow-architect.md`
**Also Copied To**: `~/.claude/agents/flow-architect.md` (by setup-agent.js)
**When Loaded**: Fourth, when agent is invoked
**Priority**: HIGHEST
**Size**: ~600 lines (previously 1,345 lines in monolithic version)

**Critical Sections**:

#### Section 1: TODO Workflow (Lines 3-31)
```markdown
🚨🚨🚨 **STOP! TODO-BASED WORKFLOW REQUIRED!** 🚨🚨🚨

**FOR EVERY USER QUERY:**

1. **Create TODO list** (TodoWrite):
   - Check signature
   - [Add more after seeing signature]

2. **Call get_signature_info()** and mark todo complete

3. **Update TODO list** based on signature:
   - Add todos for: inspect nodes → create workflow → execute

4. **Work through each TODO**, marking complete as you go
```

#### Section 2: Mandatory Node Inspection (Lines 35-157)
```markdown
## 🚨 MANDATORY INSPECTION BEFORE EXECUTION!

**BEFORE YOU DO ANYTHING ELSE:**

🔴 **YOU MUST INSPECT EVERY NODE BEFORE USING IT!**

**Required steps for EVERY node operation:**

1. ✅ `list_node_operations({ node_type: "py" })` - See all operations
2. ✅ `get_operation_details({ node_type: "py", operation: "number" })` - See exact parameters
3. ✅ `execute_node_operation({ node_type: "py", operation: "number", params: {...} })` - Execute with exact params
```

#### Section 3: Available MCP Tools (Lines 161-176)
```javascript
// 13 MCP tools available:
- get_signature_info()
- list_available_nodes()
- get_node_info()
- list_node_operations()        // CRITICAL: Must use before any node!
- get_operation_details()        // CRITICAL: Must use before executing!
- search_operations()
- execute_node_operation()       // ONLY way to execute nodes!
- add_node_to_signature()
- remove_node_from_signature()
- update_node_defaults()
- validate_signature()
- validate_params()
- request_parameters()           // For showing forms in chat
```

#### Section 4: Query Classification (Lines 178-209)
```markdown
## 📍 Step 1: Classify User Query

10 categories:
1. Simple Calculation (1+1, 47*89)
2. Random Generation (random number)
3. Data Fetch Once (ISS location, weather)
4. Scheduled Task (every 5 min, daily)
5. Simple API (2-5 endpoints)
6. Complex API (10-20 endpoints)
7. Full Application (30+ endpoints)
8. Multi-Service Integration (HTTP + DB + Email)
9. Data Transformation (ETL, processing)
10. Conversation (questions, non-action)
```

#### Section 5: Case Handlers (Lines 211-472)

**Case A: Direct MCP Execution** (Lines 211-242)
- For Categories 1, 2, 3
- Execute immediately with MCP tools
- No .act or .flow file needed

**Case B: Simple ACT File** (Lines 244-282)
- For single-node, single-operation tasks
- Check signature first
- If auth needed: show inline form
- Create .act file
- Execute

**Case C: Multi-Node ACT File** (Lines 284-340)
- For 2-5 node tasks
- Check signature first
- Flag unauthenticated nodes
- Create .act file
- Show ONE form with all auth + runtime params

**Case D: Complex FLOW File** (Lines 341-472) ⚠️ **CRITICAL - WORKFLOW TIMING ISSUE HERE**
```markdown
## Case D: Complex Workflow (.flow file)

**For Categories 5-8 (APIs, applications, integrations)**

**STEP-BY-STEP PROCESS:**

1️⃣ **CHECK SIGNATURE & FLAG UNAUTHENTICATED NODES**
   get_signature_info()

2️⃣ **CREATE THE COMPLETE WORKFLOW FILE**
   Write({
     file_path: "flow-architect/flows/github-pr-reviewer.flow",
     content: workflowContent
   })

3️⃣ **SHOW ONE FORM WITH AUTH + RUNTIME PARAMS**
   request_parameters({
     title: "🚀 GitHub PR Reviewer - Complete Setup",
     fields: [
       // Auth fields for unauthenticated nodes
       { name: "github_access_token", type: "password", ... },
       // Runtime params
       { name: "repository", type: "text", ... }
     ]
   })
```

**❌ PROBLEM**: Despite instructions saying "CREATE THE COMPLETE WORKFLOW FILE" first, agent is calling `request_parameters()` BEFORE creating the file!

### 5️⃣ Context Files (Load After Agent File)
**Location**: `/Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/instructions/contexts/`
**When Loaded**: Fifth, AFTER main agent file, based on query classification
**Priority**: Medium-High (can override agent file!)

**Available Contexts**:
1. `simple-calculation.md` (Category 1)
2. `random-generation.md` (Category 2)
3. `data-fetch-once.md` (Category 3)
4. `scheduled-task.md` (Category 4)
5. `simple-api.md` (Category 5)
6. `complex-api.md` (Category 6)
7. `full-application.md` (Category 7)
8. `multi-service-integration.md` (Category 8)
9. `data-transformation.md` (Category 9)
10. `conversation.md` (Category 10)

**⚠️ ISSUE**: These context files had OLD instructions using `type = "request"` (which doesn't exist). They were recently updated to use MCP tools, but they load AFTER the main agent file and could potentially override TODO workflow instructions.

**Recent Fix**: All context files were updated to:
- Use `execute_node_operation()` instead of direct ACT execution
- Include TODO workflow reminders
- Reference MCP tools

---

## 🔍 Where Instructions Get "Fucked" (Overridden)

### Issue #1: Context Files Override Agent File ⚠️
**Problem**: Context files load AFTER the main agent file, so their instructions can override the TODO workflow.

**Example** (in `data-fetch-once.md`):
```markdown
## Approach

1. Identify the data source
2. Call execute_node_operation directly
3. Return result
```

This could override the TODO workflow that says "Check signature first!"

**Fix Applied**:
- Added TODO reminders to each context file
- Added "Check signature first!" to each context file
- But context files still load AFTER agent file, so they have higher priority

**Potential Solution**: Move TODO workflow to root CLAUDE.md (✅ already done!) so it loads FIRST and has highest priority.

### Issue #2: Setup Script Was Skipping Agent File Updates ✅ FIXED
**Problem**: `lib/utils/claude/setup-agent.js` was checking if `~/.claude/agents/flow-architect.md` existed, and if it did, it would SKIP copying the updated version.

**Before** (lines 24-27):
```javascript
try {
  await fs.access(targetAgentFile);
  console.log('[Setup] ✅ Agent file already exists:', targetAgentFile);
  return { success: true, existed: true };
} catch (error) {
  console.log('[Setup] Agent file not found, creating...');
}
```

**After** (lines 24-26):
```javascript
// Always update the agent file to ensure latest version
// (Don't skip if it exists - we want to overwrite with latest)
```

**Fix**: Now ALWAYS overwrites the agent file, ensuring latest instructions are used.

### Issue #3: Agent Guessing Operation Names ✅ FIXED
**Problem**: Agent was guessing operation names like "request", "fetch", "http" which don't exist, leading to UNKNOWN_OPERATION errors.

**Fix**:
- Added MANDATORY INSPECTION section requiring `list_node_operations()` before any node usage
- Added triple enforcement (3 places in the file)
- Added examples showing exact workflow

**Example**:
```javascript
// ❌ WRONG (guessing):
execute_node_operation({
  node_type: "py",
  operation: "request",  // ❌ Doesn't exist!
  params: { url: "..." }
})

// ✅ CORRECT (inspecting first):
list_node_operations({ node_type: "py" })
// Returns: ["number", "execute", "text", ...]

execute_node_operation({
  node_type: "py",
  operation: "execute",  // ✅ Actually exists!
  params: { code: "import requests; ..." }
})
```

### Issue #4: Curl Not Blocked ✅ FIXED
**Problem**: Agent was using `Bash({ command: "curl http://..." })` for API calls instead of MCP tools.

**Fix**: Added warnings in 3 places:
1. Root CLAUDE.md (lines 44-66):
```markdown
## 🚨 BASH CURL/WGET IS BLOCKED - USE MCP ONLY!

**CRITICAL SECURITY RULE:**
- ❌ **NEVER** use `curl` via Bash - IT IS BLOCKED
- ❌ **NEVER** use `wget` via Bash - IT IS BLOCKED

**✅ FOR ALL API CALLS:**
1. Use MCP tool `execute_node_operation`
2. Use `python` node with `request` operation
```

2. flow-architect/CLAUDE.md (same warning)
3. flow-architect/.claude/agents/flow-architect.md (lines 9)

### Issue #5: Form Showing Before Workflow Creation ❌ **STILL UNRESOLVED**
**Problem**: Agent calls `request_parameters()` to show auth form BEFORE creating the workflow file, despite instructions saying:

```markdown
2️⃣ **CREATE THE COMPLETE WORKFLOW FILE**
   Write({ file_path: "...", content: "..." })

3️⃣ **SHOW ONE FORM WITH AUTH + RUNTIME PARAMS**
   request_parameters({ ... })
```

**Why This Happens** (Hypothesis):
1. Agent sees signature has unauthenticated nodes
2. Agent's default behavior is to ask for missing info immediately
3. Agent prioritizes "I need auth to continue" over "create file first"
4. The TODO workflow says "Check signature" as first step, which might trigger immediate auth request

**Potential Fixes** (Not Yet Implemented):
1. ✅ Add explicit rule in Case D: "DO NOT call request_parameters until AFTER Write tool"
2. ✅ Add to TODO workflow: "Create workflow file" as a separate TODO BEFORE "Show auth form"
3. ❌ Modify `request_parameters` MCP tool to check if workflow file exists first
4. ❌ Add blocking rule in root CLAUDE.md: "NEVER call request_parameters before Write"

**Where to Add the Fix**:
- **Location 1**: Root CLAUDE.md (lines 5-40) - Add to TODO workflow
- **Location 2**: flow-architect/.claude/agents/flow-architect.md Case D (lines 341-472)
- **Location 3**: Each context file that creates workflows

**Suggested Addition to TODO Workflow**:
```markdown
3. **Based on signature, update TODO list:**
   - If workflow needed → Add todos: "Create workflow file" → "Show form" → "Execute"
   - NEVER add "Show form" todo BEFORE "Create workflow file"
   - NEVER call request_parameters() until workflow file is written
```

---

## 📊 Instruction Priority Hierarchy

From **HIGHEST to LOWEST priority** (what can override what):

1. **Context Files** (`.claude/instructions/contexts/*.md`) - Load LAST, highest priority
2. **Agent File** (`~/.claude/agents/flow-architect.md`) - Load FOURTH
3. **Flow Architect CLAUDE.md** (`flow-architect/CLAUDE.md`) - Load THIRD
4. **Project Root CLAUDE.md** (`/Users/tajnoah/Downloads/ai-desktop/CLAUDE.md`) - Load SECOND
5. **Global Claude CLI Config** (`~/.claude/CLAUDE.md`) - Load FIRST, lowest priority

**Implication**: To ensure instructions are NEVER overridden:
- ✅ Put critical rules in ROOT CLAUDE.md (done for TODO workflow, curl blocking)
- ✅ Repeat critical rules in AGENT FILE (done for node inspection)
- ⚠️ Context files can still override - need to add rules there too

---

## 🔧 MCP Tools Reference

### Signature Management
```javascript
// Get all nodes and their auth status
get_signature_info()

// Add node authentication
add_node_to_signature({
  node_type: "github",
  auth: { access_token: "ghp_..." },
  defaults: { owner: "user" }
})

// Remove node
remove_node_from_signature({ node_type: "github" })

// Update defaults
update_node_defaults({
  node_type: "github",
  defaults: { owner: "newuser" }
})

// Validate signature file
validate_signature()
```

### Node Discovery
```javascript
// List all available nodes
list_available_nodes()

// Get info about specific node
get_node_info({ node_type: "github" })

// List all operations for a node
list_node_operations({ node_type: "github" })

// Get details for specific operation
get_operation_details({
  node_type: "github",
  operation: "list_repositories"
})

// Search for operations by keyword
search_operations({ query: "list" })
```

### Execution
```javascript
// Execute node operation
execute_node_operation({
  node_type: "github",
  operation: "list_repositories",
  params: { owner: "user" }
})

// Validate params before execution
validate_params({
  node_type: "github",
  operation: "list_repositories",
  params: { owner: "user" }
})
```

### UI Interaction
```javascript
// Show interactive form in chat
request_parameters({
  title: "GitHub Setup",
  description: "Enter your GitHub credentials",
  fields: [
    {
      name: "access_token",
      type: "password",
      label: "Access Token",
      required: true
    },
    {
      name: "repository",
      type: "text",
      label: "Repository Name",
      placeholder: "owner/repo"
    }
  ],
  submit_label: "Authenticate & Execute"
})
```

---

## 🚀 Expected Workflow (After Fixes)

### Example: "Get ISS weather"

**Step 1: Create TODO List**
```
TodoWrite([
  { content: "Check signature", status: "in_progress" },
  { content: "TBD based on signature", status: "pending" }
])
```

**Step 2: Check Signature**
```javascript
get_signature_info()
// Returns: py node authenticated, no issues
```

**Step 3: Update TODO List**
```
TodoWrite([
  { content: "Check signature", status: "completed" },
  { content: "Inspect py node operations", status: "in_progress" },
  { content: "Create workflow", status: "pending" },
  { content: "Execute workflow", status: "pending" }
])
```

**Step 4: Inspect py Node**
```javascript
list_node_operations({ node_type: "py" })
// Returns: ["number", "execute", "text", ...]

get_operation_details({ node_type: "py", operation: "execute" })
// Returns: { parameters: { code: { type: "string", required: true } } }
```

**Step 5: Execute**
```javascript
execute_node_operation({
  node_type: "py",
  operation: "execute",
  params: {
    code: "import requests; data = requests.get('http://api.open-notify.org/iss-now.json').json(); print(data)"
  }
})
```

**Total Expected Time**: ~7-10 turns, ~10 seconds

---

## 🐛 Known Issues & Status

| Issue | Status | Fix Applied | Verified |
|-------|--------|-------------|----------|
| Agent using curl instead of MCP | ✅ Fixed | Blocked curl in 3 places | ❌ Not tested |
| Agent guessing operation names | ✅ Fixed | Mandatory inspection added | ❌ Not tested |
| Agent file not updating | ✅ Fixed | setup-agent.js always overwrites | ✅ Verified |
| Context files using old syntax | ✅ Fixed | All updated to MCP tools | ❌ Not tested |
| Agent taking 64 turns/108s | ⚠️ Should be fixed | Node inspection should reduce | ❌ Not tested |
| Form showing before workflow | ❌ **UNRESOLVED** | Instructions added but not working | ❌ Still happening |

---

## 📝 Testing Checklist

After deploying these changes, test:

- [ ] Simple calculation: "what's 47 + 89?"
  - Should take ~3-4 turns
  - Should call `list_node_operations("py")`
  - Should call `execute_node_operation` with correct params
  - Should NOT use curl

- [ ] Data fetch: "get ISS location"
  - Should take ~7-10 turns
  - Should inspect py node first
  - Should use python node with execute operation
  - Should NOT create ACT file (use MCP directly)

- [ ] Simple API: "create quotes API"
  - Should check signature first
  - Should create workflow file BEFORE showing form
  - Should show ONE form with all params
  - Should NOT stop mid-workflow for auth

- [ ] Complex workflow: "create GitHub PR reviewer"
  - Should check signature first
  - Should inspect github node operations
  - Should create .flow file FIRST
  - Should show form LAST (after file created)
  - Should take <20 turns

---

## 🔄 File Update Mechanism

When changes are made to `flow-architect/.claude/agents/flow-architect.md`:

1. **Development**: Edit `/Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/agents/flow-architect.md`

2. **Automatic Copy** (on server start):
   - `server.js` calls `ensureAgentFile()` from `lib/utils/claude/setup-agent.js`
   - Copies from project to `~/.claude/agents/flow-architect.md`
   - **Now ALWAYS overwrites** (no skip if exists)

3. **Manual Copy** (if needed):
   ```bash
   cp flow-architect/.claude/agents/flow-architect.md ~/.claude/agents/flow-architect.md
   ```

4. **Verification**:
   ```bash
   diff flow-architect/.claude/agents/flow-architect.md ~/.claude/agents/flow-architect.md
   # Should show no differences
   ```

---

## 🎓 Summary: Why Things Were "Fucked"

1. **Agent file wasn't updating** → Fixed by making setup script always overwrite
2. **Context files had old syntax** → Fixed by updating all context files
3. **Agent was guessing** → Fixed by mandatory inspection requirement
4. **Curl wasn't blocked** → Fixed by adding warnings in 3 places
5. **Instructions were complex** → Fixed by TODO-based workflow
6. **Form showing too early** → ❌ **STILL NEEDS FIX** - Root cause unclear

## 🚦 Next Steps

1. ✅ Test the branch with simple queries
2. ✅ Monitor turn count and execution time
3. ✅ Verify node inspection is happening
4. ❌ **Fix form timing issue** - Add explicit blocking rule
5. ✅ Merge to main if all tests pass

---

## 📞 Contact

For questions about this analysis, refer to:
- Branch: `fix/agent-workflow-and-inspection`
- Commit: `0373129`
- Files changed: 85 files, 15,856 insertions, 5,273 deletions
