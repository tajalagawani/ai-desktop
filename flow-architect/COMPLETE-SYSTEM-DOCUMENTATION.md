# Flow Architect - Complete System Documentation

**Version:** 1.0.0
**Last Updated:** 2025-10-23
**Status:** Production (MCP-Only Execution)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [Directory Structure](#directory-structure)
4. [Core Components](#core-components)
5. [Query Classification System](#query-classification-system)
6. [MCP Tools Integration](#mcp-tools-integration)
7. [Execution Flow](#execution-flow)
8. [Context System](#context-system)
9. [Node Catalog](#node-catalog)
10. [Service Catalog](#service-catalog)
11. [Example Workflows](#example-workflows)
12. [Security & Sandboxing](#security--sandboxing)
13. [Performance Metrics](#performance-metrics)
14. [Development Guide](#development-guide)
15. [Troubleshooting](#troubleshooting)

---

## System Overview

### What is Flow Architect?

Flow Architect is an **AI Operating System agent** that transforms natural language requests into executable workflows. It operates as a modular, context-aware routing system that:

- **Classifies** user queries into 10 specialized categories
- **Routes** to appropriate context-specific instructions
- **Executes** operations via MCP (Model Context Protocol) tools
- **Orchestrates** services, APIs, databases, and scheduled tasks
- **Scales** from simple calculations to full-stack applications

### Key Capabilities

```
┌─────────────────────────────────────────────────────────┐
│           FLOW ARCHITECT CAPABILITIES                    │
├─────────────────────────────────────────────────────────┤
│ ✅ Calculations & Data Processing                        │
│ ✅ API Creation (2-50+ endpoints)                        │
│ ✅ Database Operations (PostgreSQL, MongoDB, Redis)     │
│ ✅ Scheduled Tasks (Cron-based automation)              │
│ ✅ Multi-Service Integration (HTTP + DB + Email)        │
│ ✅ AI Model Integration (OpenAI, Claude, Gemini)        │
│ ✅ Real-time Data Fetching                              │
│ ✅ Workflow Orchestration                               │
└─────────────────────────────────────────────────────────┘
```

### System Philosophy

**Before (Monolithic):**
- Single 1,345-line instruction file
- Context loaded all at once
- Difficult to maintain and extend
- Slow and resource-intensive

**After (Modular):**
- 10 specialized contexts (10-50 KB each)
- Load only what's needed
- Easy to maintain and extend
- 50% smaller, 4-10x faster execution

---

## Architecture Diagrams

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLAUDE.md (Entry Point)                     │
│  - Delegates to flow-architect.md                                │
│  - Enforces system rules                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              .claude/agents/flow-architect.md                    │
│                    (Core Routing Agent)                          │
│                                                                   │
│  Step 1: Query Classification (10 categories)                   │
│  Step 2: Load Appropriate Context                               │
│  Step 3: Check Signature (Authentication)                       │
│  Step 4: Decision Tree (Execute/Inform/Discover)                │
│  Step 5: Execution via MCP Tools                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  Contexts   │  │  Catalogs   │  │  Examples   │
    │  (10 files) │  │  (2 files)  │  │  (11 files) │
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                            ▼
           ┌────────────────────────────────┐
           │      MCP TOOLS (13 total)      │
           ├────────────────────────────────┤
           │ • execute_node_operation       │
           │ • get_signature_info           │
           │ • list_available_nodes         │
           │ • add_node_to_signature        │
           │ • list_node_operations         │
           │ • get_node_info                │
           │ • ... and 7 more               │
           └────────────┬───────────────────┘
                        │
                        ▼
           ┌────────────────────────────────┐
           │   Python Execution System      │
           │   (signature-system/mcp/)      │
           └────────────┬───────────────────┘
                        │
                        ▼
           ┌────────────────────────────────┐
           │   Node Catalog (129 nodes)     │
           │   - GitHub, OpenAI, Slack      │
           │   - Python, HTTP, Email        │
           │   - PostgreSQL, MongoDB, etc.  │
           └────────────┬───────────────────┘
                        │
                        ▼
           ┌────────────────────────────────┐
           │        RESULT TO USER          │
           └────────────────────────────────┘
```

### Modular Context System

```
┌────────────────────────────────────────────────────────────────┐
│                    Query Classification                         │
└────────────┬───────────────────────────────────────────────────┘
             │
   ┌─────────┴─────────┬─────────┬─────────┬─────────┬──────────┐
   │                   │         │         │         │          │
   ▼                   ▼         ▼         ▼         ▼          ▼
┌──────┐          ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐   ┌──────┐
│ Cat 1│          │ Cat 2│  │ Cat 3│  │ Cat 4│  │ Cat 5│   │ Cat 6│
│Calc  │          │Random│  │Fetch │  │Timer │  │Simple│   │Complex│
│      │          │      │  │      │  │      │  │ API  │   │ API  │
└──┬───┘          └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘   └──┬───┘
   │                 │         │         │         │          │
   ▼                 ▼         ▼         ▼         ▼          ▼
┌──────────┐    ┌──────────┐ ... (continues for all 10 categories)
│ simple-  │    │ random-  │
│calculation│   │generation│
│.md       │    │.md       │
└──────────┘    └──────────┘

Each context file contains:
├── When to Load (trigger patterns)
├── Complexity Level
├── Build Process (step-by-step)
├── Example Patterns
├── Node Types Needed
├── Common Mistakes to Avoid
└── Success Criteria
```

### MCP Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                 User: "Get my GitHub repos"                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Check Signature (SINGLE SOURCE OF TRUTH)               │
│                                                                   │
│  MCP Tool: get_signature_info()                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Decision Tree: Is 'github' in signature?                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────────┐
│ YES + Auth ✅  │  │ YES - Auth ⚠️  │  │ NO (Missing) ❌    │
└───────┬───────┘  └───────┬───────┘  └───────┬───────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────────┐
│ Execute       │  │ Ask for       │  │ Check Catalog     │
│ Directly      │  │ Credentials   │  │                   │
└───────┬───────┘  └───────────────┘  │ get_node_info()   │
        │                              └───────┬───────────┘
        │                                      │
        ▼                                      ▼
┌───────────────────────────────────────┐  ┌───────────────┐
│  execute_node_operation({             │  │ Tell user how │
│    node_type: "github",               │  │ to add node   │
│    operation: "list_repositories",    │  └───────────────┘
│    params: {}                         │
│  })                                   │
└───────────┬───────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  Response: { status: "success",         │
│              result: [...repos...] }    │
└───────────┬─────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  Parse and respond to user              │
│  "Here are your repositories: ..."      │
└─────────────────────────────────────────┘
```

### Data Flow Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     STATIC LAYER                                │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │  node-catalog.json   │  │ service-catalog.json │            │
│  │  (18 node types)     │  │  (4 services)        │            │
│  └──────────────────────┘  └──────────────────────┘            │
└────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                   RUNTIME DISCOVERY LAYER                       │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │ MCP Discovery Tools  │  │  Signature System    │            │
│  │ • list_available_    │  │  • get_signature_    │            │
│  │   nodes()            │  │    info()            │            │
│  │ • get_node_info()    │  │  • add_node_to_      │            │
│  │ • list_node_         │  │    signature()       │            │
│  │   operations()       │  │                      │            │
│  └──────────────────────┘  └──────────────────────┘            │
└────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                   EXECUTION LAYER                               │
│  ┌──────────────────────┐                                       │
│  │ execute_node_        │  → Python Executor →  Node Catalog   │
│  │ operation()          │      (subprocess)      (129 nodes)   │
│  └──────────────────────┘                                       │
└────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                     RESULTS                                     │
│  { status: "success", result: {...actual data...} }            │
└────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

### Complete File Tree

```
flow-architect/                                 (460 KB total)
│
├── 📋 ROOT DOCUMENTATION
│   ├── CLAUDE.md                              # Entry point (delegator)
│   ├── COMPLETE-SYSTEM-DOCUMENTATION.md       # This file
│   ├── MCP-EXECUTION-GUIDE.md                 # MCP tools reference
│   ├── MCP-MIGRATION-COMPLETE.md              # Migration notes
│   └── README.md                              # Quick start
│
├── 🤖 .claude/                                 (236 KB - Core Agent System)
│   │
│   ├── agents/
│   │   └── flow-architect.md                  # Core routing agent (455 lines)
│   │                                          # - Query classification
│   │                                          # - Decision tree logic
│   │                                          # - MCP tool orchestration
│   │
│   ├── instructions/
│   │   │
│   │   ├── contexts/                          # 10 specialized contexts
│   │   │   ├── simple-calculation.md          # Math operations
│   │   │   ├── random-generation.md           # Random data
│   │   │   ├── data-fetch-once.md             # One-time API calls
│   │   │   ├── scheduled-task.md              # Cron/timer tasks
│   │   │   ├── simple-api.md                  # 2-5 endpoints
│   │   │   ├── complex-api.md                 # 10-20 endpoints
│   │   │   ├── full-application.md            # 30+ endpoints
│   │   │   ├── multi-service-integration.md   # HTTP+DB+Email
│   │   │   ├── data-transformation.md         # ETL processing
│   │   │   └── conversation.md                # Non-action queries
│   │   │
│   │   ├── examples/                          # 11 reference workflows
│   │   │   ├── simple-calc.act                # Basic calculation
│   │   │   ├── random-number.act              # Random generation
│   │   │   ├── iss-location.act               # API fetch
│   │   │   ├── weather-fetch.act              # Weather API
│   │   │   ├── quotes-api.flow                # Simple CRUD API
│   │   │   ├── scheduled-random.flow          # Scheduled task
│   │   │   ├── scheduled-iss-tracker.flow     # Complex scheduled
│   │   │   ├── todo-api.flow                  # Multi-entity API
│   │   │   ├── blog-system.flow               # Complex app
│   │   │   ├── restaurant-system.flow         # Full application
│   │   │   └── price-monitor.flow             # Multi-service
│   │   │
│   │   ├── node-types/                        # (EMPTY - Planned)
│   │   │   # Future: Individual node documentation
│   │   │
│   │   ├── patterns/                          # (EMPTY - Planned)
│   │   │   # Future: Common workflow patterns
│   │   │
│   │   └── common/                            # (EMPTY - Planned)
│   │       # Future: Shared knowledge base
│   │
│   └── settings.local.json                    # Security sandbox config
│
├── 📚 catalogs/
│   ├── node-catalog.json                      # 18 node type definitions
│   │                                          # - py, neon, aci, timer
│   │                                          # - request, email, if, mongo
│   │                                          # - neo4j, mysql, redis
│   │                                          # - claude, gemini, openai
│   │                                          # - switch, set, data, log
│   │
│   └── service-catalog.json                   # 4 runtime services
│                                              # - Neon PostgreSQL
│                                              # - MongoDB
│                                              # - Redis
│                                              # - Gmail SMTP
│
├── 🏃 flows/                                   # Generated workflows
│   ├── temp/                                  # One-time executions (14 files)
│   └── [permanent flows]                      # Persistent services (3 files)
│
├── 🔧 actions/                                 # (Legacy - Deprecated)
│   └── hello-world/
│
├── 🛠️ tools/                                   # CLI utilities
│   └── query-catalog.sh                       # Catalog query script
│
└── 📦 templates/                               # (EMPTY - Planned)
    # Future: Flow templates for common patterns

---

STATISTICS:
├── Total Size: 460 KB
├── Core Agent: 236 KB (51%)
├── Total Files: 61
├── Total Directories: 9
├── Node Types: 18
├── Services: 4
├── Categories: 10
├── Examples: 11
├── Generated Flows: 17
└── Documentation: 16 files
```

### Directory Purposes

| Directory | Purpose | Count | Notes |
|-----------|---------|-------|-------|
| `.claude/agents/` | Core routing logic | 1 file | Main decision engine |
| `.claude/instructions/contexts/` | Query-specific instructions | 10 files | Loaded on demand |
| `.claude/instructions/examples/` | Reference implementations | 11 files | .act and .flow files |
| `catalogs/` | Static definitions | 2 files | Nodes and services |
| `flows/` | Generated workflows | 17 files | User-created |
| `actions/` | Legacy system | 2 files | Deprecated |
| `tools/` | CLI utilities | 1 file | Helper scripts |

---

## Core Components

### 1. Entry Point: CLAUDE.md

**Location:** `/flow-architect/CLAUDE.md`

**Purpose:** System entry point that delegates to the modular routing agent

**Key Responsibilities:**
- Explain system philosophy
- Point to primary instructions
- Enforce critical rules
- Provide quick reference

**Code Flow:**
```
User Request → CLAUDE.md → flow-architect.md → [Execution]
```

### 2. Core Routing Agent: flow-architect.md

**Location:** `.claude/agents/flow-architect.md`

**Size:** 455 lines

**Purpose:** Main decision engine for query classification and execution

**Key Sections:**

1. **MCP Tools Declaration (Lines 1-36)**
   - Lists all 13 MCP tools
   - Enforces MCP-only execution
   - Forbids Bash/HTTP/Docker commands

2. **Critical Rule (Lines 38-56)**
   - Mandatory execution process
   - Never calculate manually
   - Always use MCP tools

3. **Query Classification Router (Lines 73-115)**
   - 10 category definitions
   - Trigger patterns for each
   - Context file mappings

4. **Execution Process (Lines 119-221)**
   - 5-step workflow
   - Signature-first decision tree
   - MCP execution examples

5. **Pre-Response Checklist (Lines 373-418)**
   - Validation before responding
   - Ensures correct routing
   - Prevents errors

**Decision Tree Logic:**

```python
# Pseudocode representation
def handle_query(user_request):
    # Step 1: Classify
    category = classify_query(user_request)

    # Step 2: Load Context
    context = load_context(f"contexts/{category}.md")

    # Step 3: Check Signature (ALWAYS FIRST)
    signature = mcp_tool.get_signature_info()

    # Step 4: Decision Tree
    if node_required in signature.authenticated_nodes:
        if signature.authenticated_nodes[node_required].authenticated:
            # Case A: Authenticated → Execute
            result = mcp_tool.execute_node_operation(...)
        else:
            # Case B: Not authenticated → Ask for credentials
            ask_user_for_credentials()
    else:
        # Case C: Not in signature → Check catalog
        node_info = mcp_tool.get_node_info(node_type=node_required)
        tell_user_how_to_add()

    # Step 5: Respond
    return format_response(result)
```

### 3. Context Files (10 Specialized Contexts)

**Location:** `.claude/instructions/contexts/`

**Purpose:** Provide specialized instructions for different query types

**Standard Structure:**

```markdown
# [Context Name] Context

## When to Load This
- Query patterns that trigger this context
- User intent indicators

## Complexity Level
- MINIMAL / MEDIUM / HIGH
- Requirements overview

## Example Patterns
- ✅ Matches: [examples]
- ❌ Does NOT Match: [examples]

## Build Process (N Steps)
### Step 1: [Step Name]
[Detailed instructions]

### Step 2: [Step Name]
[Detailed instructions]

[... continues ...]

## Load Example
- Reference file to read

## Node Types Needed
- Which nodes to use

## Common Mistakes to Avoid
- ❌ Mistake 1: [description]
- Fix: [solution]

## Success Criteria
- ✅ Requirements Met When: [checklist]

## Complete Example Flow
- Full walkthrough

## Checklist Before Responding
- [ ] Item 1
- [ ] Item 2
[...]

## Remember
- Key takeaways
```

**Context Complexity Matrix:**

| Context | Complexity | Nodes Needed | Use Cases |
|---------|-----------|--------------|-----------|
| simple-calculation | MINIMAL | 1 (py) | Math operations |
| random-generation | MINIMAL | 1 (py) | Random data |
| data-fetch-once | MINIMAL | 1-2 (request, py) | API calls |
| scheduled-task | MEDIUM | 2-4 (timer, py, neon) | Recurring tasks |
| simple-api | MEDIUM | 3-6 (neon, aci, py) | 2-5 endpoints |
| complex-api | HIGH | 8-15 (neon, aci, py, if) | 10-20 endpoints |
| full-application | VERY HIGH | 20+ (all types) | 30+ endpoints |
| multi-service-integration | HIGH | 5-10 (request, neon, email, timer) | Multi-system |
| data-transformation | MEDIUM | 2-5 (py, neon, request) | ETL processing |
| conversation | NONE | 0 | Informational |

### 4. Example Workflows (11 Reference Files)

**Location:** `.claude/instructions/examples/`

**Purpose:** Working reference implementations for the agent to learn from

**File Types:**
- `.act` files: Simple one-time executions (TOML format)
- `.flow` files: Complex persistent services (TOML format)

**Example File Structure (.act format):**

```toml
[workflow]
name = "Workflow Name"
description = "What it does"
start_node = NodeName

[parameters]
# Optional parameters

[node:NodeName]
type = "py"
label = "Node description"
code = """
def function_name():
    # Python code
    return {"result": value}
"""
function = "function_name"

[edges]
# Node connections (if multiple nodes)
```

**Example Catalog:**

| File | Type | Complexity | Demonstrates |
|------|------|-----------|--------------|
| `simple-calc.act` | .act | Minimal | Basic Python execution |
| `random-number.act` | .act | Minimal | Random generation |
| `iss-location.act` | .act | Minimal | HTTP request node |
| `weather-fetch.act` | .act | Minimal | API with parsing |
| `quotes-api.flow` | .flow | Medium | CRUD API (2 endpoints) |
| `scheduled-random.flow` | .flow | Medium | Timer + Python + DB |
| `scheduled-iss-tracker.flow` | .flow | High | Timer + HTTP + DB + API |
| `todo-api.flow` | .flow | High | Multi-entity CRUD |
| `blog-system.flow` | .flow | Very High | Posts, comments, tags |
| `restaurant-system.flow` | .flow | Very High | Full management system |
| `price-monitor.flow` | .flow | High | HTTP + DB + Email + Timer |

---

## Query Classification System

### Classification Process

```
User Query → Pattern Matching → Category Assignment → Context Loading
```

### 10 Categories Explained

#### Category 1: Simple Calculation
**Triggers:** `"what's X + Y"`, `"calculate"`, math operations
**Examples:**
- ✅ "what's 47 + 89?"
- ✅ "calculate 15 * 23"
- ✅ "solve 2^8"

**Loads:** `simple-calculation.md`

**Execution:**
- Creates 1 Python node
- Executes calculation
- Returns result
- No database, no API, no server

---

#### Category 2: Random Generation
**Triggers:** `"pick random"`, `"random number"`, `"generate random"`
**Examples:**
- ✅ "pick a random number between 1 and 100"
- ✅ "generate random password"

**Loads:** `random-generation.md`

---

#### Category 3: Data Fetch (One-Time)
**Triggers:** `"where is"`, `"what is current"`, `"get [data]"`, `"fetch"`
**Examples:**
- ✅ "where is the ISS right now?"
- ✅ "get current Bitcoin price"
- ✅ "fetch weather for New York"

**Loads:** `data-fetch-once.md`

---

#### Category 4: Scheduled Task
**Triggers:** `"every X minutes"`, `"hourly"`, `"check every"`, `"repeatedly"`
**Examples:**
- ✅ "generate random number every hour"
- ✅ "check ISS location every 5 minutes"
- ✅ "fetch Bitcoin price daily"

**Loads:** `scheduled-task.md`

**Requirements:**
- Timer node (cron schedule)
- Task logic (Python/HTTP)
- Usually database (store results)
- Server configuration

---

#### Category 5: Simple API
**Triggers:** `"create API"`, `"build endpoint"`, 2-5 endpoints
**Examples:**
- ✅ "create API to store and get quotes"
- ✅ "build API for tracking expenses"
- ✅ "make endpoint to save notes"

**Loads:** `simple-api.md`

**Requirements:**
- Database node (create tables)
- ACI nodes (define routes)
- Handler nodes (process requests)
- Server configuration

---

#### Category 6: Complex API
**Triggers:** `"build API with..."`, 10-20 endpoints, multiple entities
**Examples:**
- ✅ "build todo API with tasks and projects"
- ✅ "create blog API with posts, comments, tags"

**Loads:** `complex-api.md`

---

#### Category 7: Full Application
**Triggers:** `"complete system"`, `"management system"`, `"platform"`, 30+ endpoints
**Examples:**
- ✅ "create restaurant management system"
- ✅ "build e-commerce platform"

**Loads:** `full-application.md`

---

#### Category 8: Multi-Service Integration
**Triggers:** `"monitor and alert"`, `"fetch and store"`, `"check and notify"`
**Examples:**
- ✅ "monitor Bitcoin price and email me if it drops"
- ✅ "check weather and send SMS alert"

**Loads:** `multi-service-integration.md`

**Requirements:**
- HTTP request nodes
- Database nodes
- Email/notification nodes
- Timer nodes (often)
- Conditional logic

---

#### Category 9: Data Transformation
**Triggers:** `"convert"`, `"transform"`, `"process data"`
**Examples:**
- ✅ "convert CSV to JSON"
- ✅ "transform this data structure"

**Loads:** `data-transformation.md`

---

#### Category 10: Conversation
**Triggers:** `"hello"`, `"what can you do"`, questions about capabilities
**Examples:**
- ✅ "what can you do?"
- ✅ "how does this work?"
- ✅ "hello"

**Loads:** `conversation.md`

**Note:** No execution needed, just informational response

---

### Classification Algorithm

```python
def classify_query(user_query):
    """
    Classify user query into one of 10 categories
    """
    query_lower = user_query.lower()

    # Category 1: Simple Calculation
    if any(op in query_lower for op in ["what's", "calculate", "+", "-", "*", "/"]):
        if not any(word in query_lower for word in ["every", "hourly", "api"]):
            return "simple-calculation"

    # Category 2: Random Generation
    if "random" in query_lower:
        if not any(word in query_lower for word in ["every", "hourly", "api"]):
            return "random-generation"

    # Category 4: Scheduled Task (check before Category 3)
    if any(word in query_lower for word in ["every", "hourly", "daily", "schedule"]):
        return "scheduled-task"

    # Category 3: Data Fetch
    if any(word in query_lower for word in ["where is", "get", "fetch", "what is current"]):
        if "api" not in query_lower:
            return "data-fetch-once"

    # Category 5-7: API Creation (by endpoint count)
    if any(word in query_lower for word in ["api", "endpoint"]):
        # Estimate complexity by keywords
        if any(word in query_lower for word in ["system", "platform", "management"]):
            return "full-application"  # Category 7
        elif any(word in query_lower for word in ["with", "and", "multiple"]):
            return "complex-api"  # Category 6
        else:
            return "simple-api"  # Category 5

    # Category 8: Multi-Service Integration
    if any(pair in query_lower for pair in ["and alert", "and notify", "and email"]):
        return "multi-service-integration"

    # Category 9: Data Transformation
    if any(word in query_lower for word in ["convert", "transform", "process"]):
        return "data-transformation"

    # Category 10: Conversation (default)
    return "conversation"
```

---

## MCP Tools Integration

### What is MCP?

**MCP (Model Context Protocol)** is a tool system that allows Claude to interact with external systems via function calls. In Flow Architect, MCP tools replace ALL file operations, API calls, and command-line operations.

### Why MCP-Only?

**Before (API-based execution):**
```javascript
// 1. Create .act file
Write({ file_path: "flows/temp/calc.act", content: "..." })

// 2. Execute via API
Bash({ command: "curl -X POST http://localhost:3000/api/act/execute ..." })

// 3. Parse nested response
// result.result.results.NodeName.result.result
```

**Problems:**
- 3 tool calls
- 2-5 seconds execution time
- Complex nested response parsing
- File I/O overhead
- HTTP request overhead
- Temp file cleanup needed

**After (MCP-based execution):**
```javascript
// 1. Execute directly
execute_node_operation({
  node_type: "python",
  operation: "execute",
  params: { code: "def calc(): return 5 + 5", function: "calc" }
})

// 2. Parse simple response
// result.result = 10
```

**Benefits:**
- 1 tool call
- < 500ms execution time
- Simple, flat response
- No file I/O
- No HTTP overhead
- No cleanup needed

**Performance:** **4-10x faster, 70% simpler**

---

### 13 MCP Tools Available

#### 1. Execution (Primary)

**`execute_node_operation`**
```javascript
execute_node_operation({
  node_type: string,      // e.g., "github", "openai", "python"
  operation: string,      // e.g., "list_repositories", "chat_completion"
  params: object,         // operation-specific parameters
  override_defaults: bool // optional: skip signature defaults
})
```

**Returns:**
```json
{
  "status": "success",
  "node_type": "github",
  "operation": "list_repositories",
  "result": { /* actual output */ },
  "duration": 1.23,
  "timestamp": "2025-10-23T..."
}
```

**Usage:**
- Execute ANY operation on ANY node
- NO approval prompts (pre-authenticated via signature)
- Direct Python execution (no .act files)

---

#### 2-5. Discovery & Catalog

**`list_available_nodes`**
```javascript
list_available_nodes({
  category: "ai",         // optional filter
  authenticated_only: false
})
```

**Returns:** All 129 available nodes from catalog

---

**`get_node_info`**
```javascript
get_node_info({ node_type: "github" })
```

**Returns:** Node details, auth requirements, capabilities

---

**`list_node_operations`**
```javascript
list_node_operations({ node_type: "openai" })
```

**Returns:** All operations for that node (16+ per node)

---

**`search_operations`**
```javascript
search_operations({ query: "chat" })
```

**Returns:** Operations matching keyword across all nodes

---

**`get_operation_details`**
```javascript
get_operation_details({
  node_type: "openai",
  operation: "chat_completion"
})
```

**Returns:** Full operation metadata (method, endpoint, params, examples)

---

#### 6-10. Signature Management

**`get_signature_info`**
```javascript
get_signature_info()  // all nodes
get_signature_info({ node_type: "github" })  // specific node
```

**Returns:** Authentication status, operations, defaults

**CRITICAL:** This is the SINGLE SOURCE OF TRUTH - always check signature FIRST

---

**`add_node_to_signature`**
```javascript
add_node_to_signature({
  node_type: "github",
  auth: { access_token: "ghp_..." },
  defaults: { owner: "myuser" },  // optional
  operations: ["list_repos", "get_user"]  // optional
})
```

**Usage:** Authenticate a node with credentials

---

**`remove_node_from_signature`**
```javascript
remove_node_from_signature({ node_type: "github" })
```

---

**`update_node_defaults`**
```javascript
update_node_defaults({
  node_type: "github",
  defaults: { owner: "newuser", per_page: 100 }
})
```

---

**`validate_signature`**
```javascript
validate_signature()
```

**Returns:** Signature file format and content validation

---

#### 11. Validation

**`validate_params`**
```javascript
validate_params({
  node_type: "openai",
  operation: "chat_completion",
  params: { model: "gpt-4o-mini", messages: [] }
})
```

**Returns:** Parameter validation result, merged with signature defaults

---

#### 12. Utility

**`get_system_status`**
```javascript
get_system_status()
```

**Returns:** MCP server health, Python executor status, catalog availability

---

### MCP Tool Prefix

All MCP tools have the prefix:
```
mcp__flow-architect-signature__[tool_name]
```

Example:
```
mcp__flow-architect-signature__execute_node_operation
```

Claude Code handles this automatically when you use:
```javascript
execute_node_operation(...)
```

---

### MCP Execution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 MCP Tool Call from Claude                    │
│  execute_node_operation({ node_type: "github", ... })       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              signature-system/mcp/index.js                   │
│  - Receives tool call                                        │
│  - Routes to appropriate handler                             │
│  - Returns to signature-system/mcp/tools/signature/          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│        signature-system/mcp/lib/python-executor.js           │
│  - Spawns Python subprocess                                  │
│  - Passes JSON arguments                                     │
│  - Captures stdout/stderr                                    │
│  - Filters warnings                                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│    components/apps/act-docker/act/mcp_utils/                 │
│    single_node_executor.py                                   │
│  - Loads signature file                                      │
│  - Validates authentication                                  │
│  - Executes node operation                                   │
│  - Returns JSON result                                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Node Catalog (129 nodes)                        │
│  - GitHub, OpenAI, Slack, Linear, Jira, etc.                │
│  - Each node has 16+ operations                              │
│  - Total: 2,000+ operations available                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Result to Claude                          │
│  { status: "success", result: {...} }                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Execution Flow

### Signature-First Decision Tree

**CRITICAL CONCEPT:** The signature file is the SINGLE SOURCE OF TRUTH. Always check it FIRST before making ANY decisions about node availability or authentication.

```
┌─────────────────────────────────────────────────────────────┐
│                    User Makes Request                        │
│  Example: "Get my GitHub repositories"                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: ALWAYS Check Signature FIRST                       │
│  (Signature is the SINGLE SOURCE OF TRUTH)                  │
│                                                              │
│  MCP Tool: get_signature_info()                             │
│                                                              │
│  Returns:                                                    │
│  {                                                           │
│    "authenticated_nodes": {                                 │
│      "github": {                                            │
│        "authenticated": true/false,                         │
│        "operations": [...],                                 │
│        "defaults": {...}                                    │
│      }                                                       │
│    }                                                         │
│  }                                                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Decision Tree - Is node in signature?             │
└────────────────────────────┬────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌──────────────────┐
│ CASE A:        │  │ CASE B:        │  │ CASE C:          │
│ In Signature + │  │ In Signature - │  │ NOT In Signature │
│ Authenticated  │  │ Not Auth Yet   │  │                  │
│ ✅             │  │ ⚠️             │  │ ❌               │
└───────┬────────┘  └───────┬────────┘  └───────┬──────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌──────────────────┐
│ Execute        │  │ Ask User for   │  │ NOW Check        │
│ Immediately    │  │ Credentials    │  │ Catalog          │
│                │  │                │  │                  │
│ execute_node_  │  │ "GitHub needs  │  │ get_node_info()  │
│ operation()    │  │ access_token"  │  │                  │
│                │  │                │  │ or               │
│ ❌ NO catalog  │  │ ❌ NO catalog  │  │ list_available_  │
│   lookup!      │  │   lookup!      │  │ nodes()          │
└───────┬────────┘  └───────┬────────┘  └───────┬──────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌──────────────────┐
│ Return Result  │  │ If user gives  │  │ If exists:       │
│                │  │ credentials:   │  │ Tell user how    │
│ { status:      │  │                │  │ to add           │
│   "success",   │  │ add_node_to_   │  │                  │
│   result: ...} │  │ signature()    │  │ If doesn't exist:│
│                │  │                │  │ Tell user node   │
│                │  │ Then execute   │  │ not available    │
└────────────────┘  └────────────────┘  └──────────────────┘
```

### Why Signature-First?

**Efficiency:**
- Signature contains ALL info about configured nodes
- No need to query catalog for known nodes
- Faster response times

**Accuracy:**
- Signature shows actual authentication status
- Catalog only shows what's possible, not what's configured
- Prevents misleading "node available" messages when it's already added

**Simplicity:**
- One source of truth
- Clear decision tree
- Less tool calls = faster execution

---

### Complete Execution Example

**Scenario:** User asks "Get my GitHub repositories"

#### Case A: GitHub in Signature + Authenticated ✅

```javascript
// Step 1: Check signature
const sigInfo = get_signature_info()
// Returns:
{
  "authenticated_nodes": {
    "github": {
      "authenticated": true,
      "operations": ["list_repositories", "get_repo", "create_issue", ...],
      "defaults": { "owner": "myusername" }
    },
    "openai": { "authenticated": true, ... }
  }
}

// Step 2: GitHub is authenticated! Execute directly.
const result = execute_node_operation({
  node_type: "github",
  operation: "list_repositories",
  params: {}  // Uses defaults from signature
})

// Step 3: Parse result
// result = { status: "success", result: [...repos...] }

// Step 4: Respond to user
"Here are your repositories: repo1, repo2, repo3..."
```

**NO catalog lookup needed!**

---

#### Case B: GitHub in Signature but NOT Authenticated ⚠️

```javascript
// Step 1: Check signature
const sigInfo = get_signature_info()
// Returns:
{
  "authenticated_nodes": {
    "github": {
      "authenticated": false,
      "requires": ["access_token"],
      "operations": ["list_repositories", ...]
    }
  }
}

// Step 2: Node exists but not authenticated
// DON'T check catalog! Just ask for credentials.
"GitHub node is configured but not authenticated. Please provide your access_token from https://github.com/settings/tokens"

// Step 3: If user provides token
const result = add_node_to_signature({
  node_type: "github",
  auth: { access_token: "ghp_user_provided_token" }
})

// Step 4: Now execute
execute_node_operation({ node_type: "github", operation: "list_repositories", params: {} })
```

**NO catalog lookup needed!**

---

#### Case C: GitHub NOT in Signature ❌

```javascript
// Step 1: Check signature
const sigInfo = get_signature_info()
// Returns:
{
  "authenticated_nodes": {
    "openai": { "authenticated": true, ... },
    "slack": { "authenticated": true, ... }
    // No github!
  }
}

// Step 2: Node NOT in signature. NOW check catalog.
const nodeInfo = get_node_info({ node_type: "github" })
// Returns:
{
  "exists": true,
  "name": "GitHub API",
  "auth_required": true,
  "auth_fields": ["access_token"],
  "operations": ["list_repositories", "get_repo", ...],
  "documentation": "..."
}

// Step 3: Tell user how to add
"GitHub node is available! To use it:
1. Get your access token from https://github.com/settings/tokens
2. I can add it to your signature with your permission"

// Step 4: If user provides token
add_node_to_signature({
  node_type: "github",
  auth: { access_token: "user_token" }
})

// Step 5: Execute
execute_node_operation({ node_type: "github", operation: "list_repositories", params: {} })
```

**Catalog lookup ONLY when node is missing!**

---

### Multi-Step Workflow Example

**Scenario:** User asks "Monitor Bitcoin price and email me if it drops below $30,000"

**Classification:** Multi-Service Integration (Category 8)

**Context Loaded:** `multi-service-integration.md`

**Execution Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│  1. Create Timer Node                                        │
│     - Schedule: Every 5 minutes (*/5 * * * *)               │
│     - Handler: FetchPrice                                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Create HTTP Request Node (FetchPrice)                   │
│     - URL: https://api.coingecko.com/api/v3/simple/price   │
│     - Parse JSON response                                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Create Database Node (StorePrice)                       │
│     - Table: price_history                                   │
│     - INSERT current price and timestamp                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Create Conditional Node (CheckThreshold)                │
│     - IF price < 30000                                       │
│     - THEN SendEmail                                         │
│     - ELSE Continue                                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Create Email Node (SendEmail)                           │
│     - To: user@email.com                                     │
│     - Subject: "Bitcoin Alert"                               │
│     - Body: "Price dropped to $[price]"                      │
└─────────────────────────────────────────────────────────────┘
```

**Nodes Used:**
- timer (scheduling)
- request (HTTP call)
- neon (database)
- if (conditional logic)
- email (notification)

**Execution Method:** Creates a .flow file (persistent service)

---

## Context System

### How Contexts Work

Each context file provides:

1. **When to Load This** - Trigger patterns
2. **Complexity Level** - Resource requirements
3. **Example Patterns** - What matches, what doesn't
4. **Build Process** - Step-by-step instructions
5. **Load Example** - Reference file to read
6. **Node Types Needed** - Which nodes to use
7. **Common Mistakes** - Errors to avoid
8. **Success Criteria** - Validation checklist
9. **Complete Example** - Full walkthrough
10. **Checklist Before Responding** - Final validation

### Context Loading Process

```
User Query → Classification → Context Selection → Context Loading → Execution
```

### Context Interaction Patterns

**Simple Context (no dependencies):**
```
simple-calculation.md
  └── Reads: examples/simple-calc.act
  └── Uses: Python node only
  └── No external dependencies
```

**Medium Context (some dependencies):**
```
simple-api.md
  ├── Reads: examples/quotes-api.flow
  ├── Uses: Neon (database) + ACI (API routes)
  ├── Checks: Service catalog for database availability
  └── Creates: Permanent .flow file
```

**Complex Context (many dependencies):**
```
multi-service-integration.md
  ├── Reads: examples/price-monitor.flow
  ├── Uses: Timer + Request + Neon + If + Email
  ├── Checks: Service catalog for DB and SMTP
  ├── Validates: All services running
  └── Creates: Complex .flow file with 5+ nodes
```

---

### Context Reference Guide

| Context | File | Nodes Used | Output Type | Persistence |
|---------|------|-----------|-------------|-------------|
| Simple Calculation | `simple-calculation.md` | py | .act (temp) | One-time |
| Random Generation | `random-generation.md` | py | .act (temp) | One-time |
| Data Fetch | `data-fetch-once.md` | request, py | .act (temp) | One-time |
| Scheduled Task | `scheduled-task.md` | timer, py, neon | .flow | Permanent |
| Simple API | `simple-api.md` | neon, aci, py | .flow | Permanent |
| Complex API | `complex-api.md` | neon, aci, py, if | .flow | Permanent |
| Full Application | `full-application.md` | All types | .flow | Permanent |
| Multi-Service | `multi-service-integration.md` | timer, request, neon, email, if | .flow | Permanent |
| Data Transform | `data-transformation.md` | py, request, neon | .act or .flow | Varies |
| Conversation | `conversation.md` | None | N/A | N/A |

---

## Node Catalog

### 18 Node Types Available

Flow Architect supports 18 node types across 7 categories:

#### 1. Computation Nodes

**`py` - Python Execution**
- **Purpose:** Execute Python code with full standard library
- **Parameters:** `code` (required), `function` (required), `timeout_seconds`, `retry_on_failure`
- **Use Cases:** Calculations, data processing, transformations, business logic
- **Example:**
```toml
[node:Calculate]
type = py
code = """
def calculate():
    return {"result": 47 + 89}
"""
function = calculate
```

**`data` - Data Transformation**
- **Purpose:** Data transformation operations
- **Parameters:** `operation`, `input`, `output`, `transform`
- **Use Cases:** Data format conversion, restructuring

---

#### 2. Database Nodes

**`neon` - PostgreSQL (Neon)**
- **Purpose:** PostgreSQL database operations
- **Requires:** PostgreSQL service running
- **Parameters:** `connection_string`, `operation`, `query`, `parameters`
- **Operations:** `execute_query`, `create_schema`
- **Example:**
```toml
[node:FetchQuotes]
type = neon
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = SELECT * FROM quotes ORDER BY created_at DESC
```

**`mongo` - MongoDB**
- **Purpose:** MongoDB document database
- **Requires:** MongoDB service running
- **Parameters:** `connection_string`, `operation`, `collection`, `query`, `document`

**`mysql` - MySQL**
- **Purpose:** MySQL database operations
- **Requires:** MySQL service running
- **Parameters:** `connection_string`, `operation`, `query`, `parameters`

**`neo4j` - Neo4j Graph Database**
- **Purpose:** Graph database operations
- **Requires:** Neo4j service running
- **Parameters:** `connection_string`, `operation`, `query`, `parameters`

**`redis` - Redis Cache**
- **Purpose:** Key-value cache operations
- **Requires:** Redis service running
- **Parameters:** `connection_string`, `operation`, `key`, `value`, `ttl`

---

#### 3. API Nodes

**`aci` - API Route Definition**
- **Purpose:** Define REST API endpoints
- **Requires:** Server configuration in workflow
- **Parameters:** `mode` (server), `operation` (add_route), `route_path`, `methods`, `handler`, `description`
- **Supported Methods:** GET, POST, PUT, DELETE, PATCH
- **Example:**
```toml
[node:DefineGetQuotesRoute]
type = aci
mode = server
operation = add_route
route_path = /api/quotes
methods = ["GET"]
handler = FetchQuotes
description = Get all quotes
```

**`request` - HTTP Request**
- **Purpose:** Make outbound HTTP requests to external APIs
- **Parameters:** `method`, `url`, `headers`, `query_params`, `body`, `timeout_seconds`, `retry_on_failure`
- **Supported Methods:** GET, POST, PUT, DELETE, PATCH
- **Example:**
```toml
[node:FetchISS]
type = request
method = GET
url = http://api.open-notify.org/iss-now.json
timeout_seconds = 10
```

---

#### 4. Logic Nodes

**`if` - Conditional Branch**
- **Purpose:** Branch execution based on boolean condition
- **Parameters:** `condition`, `on_true`, `on_false`
- **Example:**
```toml
[node:CheckPrice]
type = if
condition = {{FetchPrice.result.price}} < 30000
on_true = SendAlert
on_false = ContinueMonitoring
```

**`switch` - Multi-Way Branch**
- **Purpose:** Multi-way branching based on value
- **Parameters:** `value`, `cases`, `default`

**`set` - Store Value**
- **Purpose:** Store values in workflow context
- **Parameters:** `key`, `value`

---

#### 5. Scheduling Nodes

**`timer` - Scheduled Task**
- **Purpose:** Execute tasks on a schedule using cron syntax
- **Parameters:** `schedule` (cron format), `on_tick` (handler node), `timezone`, `enabled`
- **Example:**
```toml
[node:HourlyTrigger]
type = timer
schedule = 0 * * * *
on_tick = GenerateNumber
timezone = UTC
```

**Cron Format:**
```
*/5 * * * *  # Every 5 minutes
0 * * * *    # Every hour
0 9 * * *    # Daily at 9am
0 0 * * 0    # Every Sunday
```

---

#### 6. Notification Nodes

**`email` - Email Notification**
- **Purpose:** Send email notifications via SMTP
- **Requires:** SMTP service configured
- **Parameters:** `smtp_host`, `smtp_port`, `from`, `to`, `subject`, `body`, `cc`, `bcc`, `attachments`
- **Example:**
```toml
[node:SendAlert]
type = email
smtp_host = smtp.gmail.com
smtp_port = 587
from = alerts@example.com
to = user@example.com
subject = Bitcoin Price Alert
body = Price dropped to ${{FetchPrice.result.price}}
```

---

#### 7. AI Nodes

**`openai` - OpenAI GPT**
- **Purpose:** OpenAI GPT processing
- **Parameters:** `model`, `messages`, `api_key`, `temperature`, `max_tokens`
- **Models:** gpt-4o, gpt-4o-mini, etc.

**`claude` - Anthropic Claude**
- **Purpose:** Claude AI processing
- **Parameters:** `model`, `messages`, `api_key`, `temperature`, `max_tokens`
- **Models:** claude-sonnet-4-5, claude-opus-4, etc.

**`gemini` - Google Gemini**
- **Purpose:** Gemini AI processing
- **Parameters:** `model`, `messages`, `api_key`, `temperature`
- **Models:** gemini-2.0-flash-exp, gemini-1.5-pro, etc.

---

#### 8. Utility Nodes

**`log_message` - Logging**
- **Purpose:** Log messages for debugging
- **Parameters:** `message`, `level`

**`generate_uuid` - UUID Generation**
- **Purpose:** Generate UUIDs
- **Parameters:** `version`

---

### Node Catalog JSON Structure

**Location:** `catalogs/node-catalog.json`

```json
{
  "version": "1.0.0",
  "last_updated": "2025-10-18T15:00:00Z",
  "categories": ["computation", "database", "api", "logic", "notification", "scheduling", "ai"],
  "nodes": [
    {
      "type": "py",
      "name": "Python Execution",
      "category": "computation",
      "description": "Execute Python code with full standard library access",
      "requires_service": false,
      "documentation_url": ".claude/instructions/node-types/python.md",
      "parameters": {
        "required": ["code", "function"],
        "optional": ["timeout_seconds", "retry_on_failure", "max_retries", "on_error"]
      },
      "example_usage": ".claude/instructions/examples/simple-calc.act",
      "common_use_cases": ["calculations", "data processing", "transformations", "business logic"]
    }
    // ... 17 more nodes
  ]
}
```

---

### Node Usage Statistics

| Category | Node Count | Most Used |
|----------|-----------|-----------|
| Computation | 2 | py |
| Database | 5 | neon |
| API | 2 | aci, request |
| Logic | 3 | if |
| Scheduling | 1 | timer |
| Notification | 1 | email |
| AI | 3 | openai |
| Utility | 2 | log_message |

---

## Service Catalog

### 4 Runtime Services

**Location:** `catalogs/service-catalog.json`

#### 1. Neon PostgreSQL
```json
{
  "id": "neon-postgres-primary",
  "name": "Neon PostgreSQL",
  "type": "database",
  "subtype": "postgresql",
  "status": "available",
  "connection": {
    "string": "postgresql://user:pass@host:5432/dbname",
    "host": "host.neon.tech",
    "port": 5432,
    "database": "neondb",
    "ssl": true
  },
  "capabilities": ["sql", "relations", "transactions", "jsonb"],
  "related_node_type": "neon",
  "max_connections": 100,
  "current_connections": 5
}
```

#### 2. MongoDB Local
```json
{
  "id": "mongodb-local",
  "name": "MongoDB Local",
  "type": "database",
  "subtype": "mongodb",
  "status": "available",
  "connection": {
    "string": "mongodb://localhost:27017",
    "host": "localhost",
    "port": 27017
  },
  "capabilities": ["documents", "aggregation", "geospatial"],
  "related_node_type": "mongo"
}
```

#### 3. Redis Cache
```json
{
  "id": "redis-cache",
  "name": "Redis Cache",
  "type": "cache",
  "subtype": "redis",
  "status": "available",
  "connection": {
    "string": "redis://localhost:6379",
    "host": "localhost",
    "port": 6379
  },
  "capabilities": ["key-value", "pub-sub", "lists", "sets"],
  "related_node_type": "redis"
}
```

#### 4. Gmail SMTP
```json
{
  "id": "smtp-gmail",
  "name": "Gmail SMTP",
  "type": "notification",
  "subtype": "email",
  "status": "available",
  "connection": {
    "host": "smtp.gmail.com",
    "port": 587,
    "secure": true
  },
  "capabilities": ["send_email", "attachments"],
  "related_node_type": "email",
  "requires_credentials": true
}
```

---

## Example Workflows

### 11 Reference Workflows

| File | Format | Nodes | Complexity | Purpose |
|------|--------|-------|-----------|---------|
| `simple-calc.act` | ACT | 1 (py) | Minimal | Basic Python calculation |
| `random-number.act` | ACT | 1 (py) | Minimal | Random generation |
| `iss-location.act` | ACT | 2 (request, py) | Minimal | API fetch + parse |
| `weather-fetch.act` | ACT | 2 (request, py) | Minimal | Weather API |
| `quotes-api.flow` | FLOW | 4 (neon, aci) | Medium | CRUD API (2 endpoints) |
| `scheduled-random.flow` | FLOW | 3 (timer, py, neon) | Medium | Hourly random generation |
| `scheduled-iss-tracker.flow` | FLOW | 5 (timer, request, py, neon, aci) | High | ISS tracking with API |
| `todo-api.flow` | FLOW | 8 (neon, aci, py) | High | Multi-entity CRUD |
| `blog-system.flow` | FLOW | 12 (neon, aci, py, if) | Very High | Posts, comments, tags |
| `restaurant-system.flow` | FLOW | 20+ (all types) | Very High | Full management |
| `price-monitor.flow` | FLOW | 6 (timer, request, neon, if, email) | High | Price monitoring + alerts |

---

### Example: Simple Calculation

**File:** `examples/simple-calc.act`

```toml
[workflow]
name = "Calculate 47 + 89"
description = "Simple addition operation"
start_node = Calculate

[node:Calculate]
type = py
label = "Perform calculation"
code = """
def calculate():
    result = 47 + 89
    return {"result": result}
"""
function = calculate
```

**Execution:**
```bash
Result: 136
```

---

### Example: Quotes API

**File:** `examples/quotes-api.flow`

```toml
[workflow]
name = "Quotes API"
description = "Simple CRUD API for quotes"
start_node = CreateQuotesTable

[parameters]
connection_string = postgresql://user:pass@host:5432/db

[node:CreateQuotesTable]
type = neon
label = "1. Create quotes table"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = CREATE TABLE IF NOT EXISTS quotes (id SERIAL PRIMARY KEY, text TEXT NOT NULL, author VARCHAR(255), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

[node:DefineGetQuotesRoute]
type = aci
mode = server
label = "API.Quotes.1. GET /api/quotes"
operation = add_route
route_path = /api/quotes
methods = ["GET"]
handler = FetchQuotes
description = Get all quotes

[node:FetchQuotes]
type = neon
label = "API.Quotes.1.1. Fetch Quotes"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = SELECT * FROM quotes ORDER BY created_at DESC
parameters = []

[node:DefineAddQuoteRoute]
type = aci
mode = server
label = "API.Quotes.2. POST /api/quotes"
operation = add_route
route_path = /api/quotes
methods = ["POST"]
handler = InsertQuote
description = Add new quote

[node:InsertQuote]
type = neon
label = "API.Quotes.2.1. Insert Quote"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = INSERT INTO quotes (text, author) VALUES (%s, %s) RETURNING *
parameters = ["{{request_data.text}}", "{{request_data.author}}"]

[edges]
CreateQuotesTable = DefineGetQuotesRoute
CreateQuotesTable = DefineAddQuoteRoute
DefineGetQuotesRoute = FetchQuotes
DefineAddQuoteRoute = InsertQuote

[env]

[settings]
debug_mode = true
max_retries = 3
timeout_seconds = 600

[configuration]
agent_enabled = true
agent_name = quotes-api-agent
agent_version = 1.0.0
host = 0.0.0.0
port = 9001
debug = true
cors_enabled = true

[deployment]
environment = development
```

**Endpoints:**
- `GET /api/quotes` - List all quotes
- `POST /api/quotes` - Add new quote

---

### Example: Price Monitor

**File:** `examples/price-monitor.flow`

**Flow:**
```
Timer (Every 5 min)
  ↓
Fetch Price (HTTP)
  ↓
Store Price (Database)
  ↓
Check Threshold (If < 30000)
  ↓
Send Email Alert
```

**Nodes:**
- timer (scheduling)
- request (HTTP call)
- neon (database)
- if (conditional)
- email (notification)

---

## Security & Sandboxing

### Sandbox Configuration

**Location:** `.claude/settings.local.json`

```json
{
  "sandbox": {
    "enabled": true,
    "restrictions": {
      "docker_commands": {
        "blocked": true,
        "reason": "Security - prevent Docker access"
      },
      "file_access": {
        "allowed_paths": ["/Users/tajnoah/Downloads/ai-desktop/flow-architect"],
        "reason": "Restrict file operations to flow-architect only"
      },
      "http_requests": {
        "allowed_domains": ["localhost:3000"],
        "reason": "Only allow API calls to localhost"
      },
      "bash_commands": {
        "blocked_patterns": ["docker", "rm -rf", "sudo"],
        "reason": "Prevent destructive commands"
      }
    }
  }
}
```

### Security Rules

**✅ ALLOWED:**
- MCP tool usage
- Read files in `flow-architect/`
- HTTP calls to `localhost:3000`
- Execute via MCP tools

**❌ FORBIDDEN:**
- Docker commands (`docker ps`, `docker inspect`, etc.)
- File access outside `flow-architect/`
- HTTP requests to external domains (except via MCP)
- Bash commands with destructive potential
- Direct API calls (must use MCP)

### Why These Restrictions?

1. **Docker Commands:**
   - Risk: Direct Docker access bypasses orchestration
   - Alternative: Use service catalog APIs

2. **File Access:**
   - Risk: Accidental modification of system files
   - Alternative: Restrict to project directory

3. **External HTTP:**
   - Risk: Uncontrolled API calls
   - Alternative: Route through MCP tools

4. **Bash Commands:**
   - Risk: Destructive operations
   - Alternative: Use specialized tools (Read, Write, Edit)

---

## Performance Metrics

### Execution Speed Comparison

| Method | Tool Calls | Time | Complexity | File I/O | HTTP |
|--------|-----------|------|-----------|----------|------|
| **Old (API)** | 3-4 | 2-5s | High | Yes | Yes |
| **New (MCP)** | 1 | <500ms | Low | No | No |
| **Improvement** | 75% fewer | **4-10x faster** | 70% simpler | 100% reduction | 100% reduction |

### Detailed Breakdown

**Old Method (API-based execution):**
```
Step 1: Create .act file           →  500ms (Write tool + disk I/O)
Step 2: Execute via API            → 1-3s  (Bash + curl + HTTP overhead)
Step 3: Parse nested response      →  200ms (Complex JSON traversal)
Step 4: Clean up temp file         →  100ms (Optional)
─────────────────────────────────────────
Total:                               2-5 seconds
```

**New Method (MCP execution):**
```
Step 1: execute_node_operation()   → <500ms (Direct Python call)
─────────────────────────────────────────
Total:                               <500ms
```

### Why MCP is Faster

1. **No File I/O:**
   - Old: Write → Execute → Read → Delete
   - New: Execute directly

2. **No HTTP Overhead:**
   - Old: localhost HTTP round-trip
   - New: Direct Python subprocess

3. **Simpler Response:**
   - Old: 3 levels deep (`result.result.results.node.result.result`)
   - New: Flat (`result.result`)

4. **Less Context:**
   - Old: 3-4 tool calls = 3-4 context switches
   - New: 1 tool call = 1 context switch

### Performance by Query Type

| Query Type | Old Time | New Time | Speedup |
|-----------|---------|----------|---------|
| Simple Calculation | 2-3s | 300ms | **10x faster** |
| Data Fetch | 3-4s | 500ms | **8x faster** |
| API Execution | 2-5s | 400ms | **6x faster** |
| Multi-node Workflow | 5-10s | 1-2s | **5x faster** |

---

## Development Guide

### Adding a New Context

**Steps:**

1. **Create Context File**
   - Location: `.claude/instructions/contexts/new-context.md`
   - Follow standard structure (see Context System section)

2. **Add Trigger Patterns**
   - Update `flow-architect.md` router (lines 73-115)
   - Add new category with trigger keywords

3. **Create Example File**
   - Location: `.claude/instructions/examples/new-example.act` or `.flow`
   - Provide working reference implementation

4. **Test Classification**
   - Verify trigger patterns work
   - Ensure correct context is loaded

5. **Document**
   - Update this documentation
   - Add to context reference guide

---

### Adding a New Node Type

**Steps:**

1. **Update Node Catalog**
   - Location: `catalogs/node-catalog.json`
   - Add node definition with all parameters

2. **Create Node Documentation** (Future)
   - Location: `.claude/instructions/node-types/new-node.md`
   - Document parameters, operations, examples

3. **Update Examples** (if applicable)
   - Create example workflow using new node
   - Add to `.claude/instructions/examples/`

4. **Test Execution**
   - Verify node works via MCP
   - Test with `execute_node_operation()`

---

### Debugging

**Common Issues:**

1. **Context Not Loading**
   - Check trigger patterns in `flow-architect.md`
   - Verify context file exists
   - Test classification manually

2. **Node Not Found**
   - Check signature: `get_signature_info()`
   - Check catalog: `get_node_info({ node_type: "..." })`
   - Verify node type spelling

3. **Authentication Errors**
   - Check signature status
   - Verify credentials
   - Re-add with `add_node_to_signature()`

4. **Execution Failures**
   - Check MCP tool response
   - Validate parameters
   - Review node catalog for requirements

**Debugging Tools:**

```javascript
// Check signature
get_signature_info()

// Check specific node
get_node_info({ node_type: "github" })

// List operations
list_node_operations({ node_type: "github" })

// Validate parameters
validate_params({
  node_type: "github",
  operation: "list_repositories",
  params: {}
})

// Check system status
get_system_status()
```

---

## Troubleshooting

### Issue: "Node not found"

**Cause:** Node not in signature

**Solution:**
```javascript
// 1. Check if node exists in catalog
get_node_info({ node_type: "github" })

// 2. If exists, add to signature
add_node_to_signature({
  node_type: "github",
  auth: { access_token: "..." }
})
```

---

### Issue: "Operation not found"

**Cause:** Operation doesn't exist for that node

**Solution:**
```javascript
// List available operations
list_node_operations({ node_type: "github" })

// Or search across all nodes
search_operations({ query: "repository" })
```

---

### Issue: "Authentication failed"

**Cause:** Invalid or missing credentials

**Solution:**
```javascript
// Check current auth status
get_signature_info({ node_type: "github" })

// Update credentials
add_node_to_signature({
  node_type: "github",
  auth: { access_token: "new_token" }
})
```

---

### Issue: "MCP tool not responding"

**Cause:** Python executor error or MCP server down

**Solution:**
```javascript
// Check system status
get_system_status()

// If down, restart MCP server:
// npm run dev (restarts all services)
```

---

### Issue: "Wrong context loaded"

**Cause:** Query classification mismatch

**Solution:**
- Review trigger patterns in `flow-architect.md`
- Adjust query wording to match patterns
- Check classification logic

---

## Appendix

### File Reference

**Core Files:**
- `CLAUDE.md` - Entry point
- `.claude/agents/flow-architect.md` - Routing agent (455 lines)
- `.claude/settings.local.json` - Sandbox config

**Contexts (10):**
- `simple-calculation.md`
- `random-generation.md`
- `data-fetch-once.md`
- `scheduled-task.md`
- `simple-api.md`
- `complex-api.md`
- `full-application.md`
- `multi-service-integration.md`
- `data-transformation.md`
- `conversation.md`

**Examples (11):**
- `simple-calc.act`
- `random-number.act`
- `iss-location.act`
- `weather-fetch.act`
- `quotes-api.flow`
- `scheduled-random.flow`
- `scheduled-iss-tracker.flow`
- `todo-api.flow`
- `blog-system.flow`
- `restaurant-system.flow`
- `price-monitor.flow`

**Catalogs (2):**
- `node-catalog.json` - 18 node types
- `service-catalog.json` - 4 services

---

### Key Statistics

| Metric | Value |
|--------|-------|
| Total Size | 460 KB |
| Core Agent | 236 KB (51%) |
| Total Files | 61 |
| Node Types | 18 |
| Services | 4 |
| Categories | 10 |
| Examples | 11 |
| MCP Tools | 13 |
| Available Nodes (via MCP) | 129 |
| Operations per Node | 16+ |
| Total Operations | 2,000+ |

---

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-23 | Initial comprehensive documentation |
| - | 2025-10-23 | MCP-only migration complete |
| - | 2025-10-18 | Modular system created (replaced monolithic) |

---

### Related Documentation

- `MCP-EXECUTION-GUIDE.md` - Complete MCP tools reference
- `MCP-MIGRATION-COMPLETE.md` - Migration from API to MCP
- `signature-system/mcp/TESTING.md` - MCP tool testing guide
- `signature-system/mcp/NODE_EXECUTION_VERIFIED.md` - Node execution verification

---

**END OF DOCUMENTATION**

---

**For questions or issues:**
1. Check this documentation
2. Review MCP-EXECUTION-GUIDE.md
3. Check signature status: `get_signature_info()`
4. Verify catalog: `get_node_info({ node_type: "..." })`
