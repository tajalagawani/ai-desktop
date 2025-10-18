# Flow Architect Modular Agent - Implementation Plan

## Overview

Transform the current monolithic agent (flow-architect/CLAUDE.md ~774 lines) into a **modular, context-aware routing system** that loads only what it needs per query.

**Current Problem:**
- One massive CLAUDE.md file with all instructions
- Agent loads everything every time
- Hard to maintain and update
- Inefficient context usage

**Solution:**
- Tiny routing agent (~150 lines)
- 44 modular instruction files organized by purpose
- Context-specific loading
- Much faster and more maintainable

---

## Architecture Transformation

### Before (Current)
```
flow-architect/
├── CLAUDE.md (774 lines - everything in one file)
└── flows/ (generated flows)
```

### After (Target)
```
flow-architect/
├── .claude/
│   ├── agents/
│   │   └── flow-architect.md         # 150 lines - routing only
│   │
│   └── instructions/
│       ├── contexts/                  # 10 files - query-specific
│       ├── examples/                  # 11 files - working examples
│       ├── node-types/                # 14 files - node references
│       ├── patterns/                  # 5 files - workflow patterns
│       └── common/                    # 4 files - shared knowledge
│
├── catalogs/
│   ├── service-catalog.json           # Runtime services
│   └── node-catalog.json              # Available nodes
│
└── flows/                             # Generated flows
    ├── [user-flows].flow
    └── temp/                          # Temporary executions
```

---

## Implementation Phases

### Phase 1: Foundation (Priority: CRITICAL)
**Goal:** Create directory structure and core routing agent

**Tasks:**
1. ✅ Create directory structure
   ```bash
   mkdir -p flow-architect/.claude/agents
   mkdir -p flow-architect/.claude/instructions/{contexts,examples,node-types,patterns,common}
   mkdir -p flow-architect/catalogs
   mkdir -p flow-architect/flows/temp
   ```

2. ✅ Write core routing agent: `.claude/agents/flow-architect.md` (~150 lines)
   - Identity (AI OS persona)
   - CRITICAL RULE (mandatory ACT execution)
   - Query classification router
   - 5-step process flow
   - Resource locations
   - Execution API
   - Pre-response checklist

3. ✅ Create catalogs with complete JSON schemas

   **`catalogs/service-catalog.json`** - Available runtime services:
   ```json
   {
     "version": "1.0.0",
     "last_updated": "2025-10-18T15:00:00Z",
     "services": [
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
         "documentation_url": ".claude/instructions/node-types/neon.md",
         "max_connections": 100,
         "current_connections": 5
       },
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
         "related_node_type": "mongo",
         "documentation_url": ".claude/instructions/node-types/mongo.md"
       },
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
         "related_node_type": "redis",
         "documentation_url": ".claude/instructions/node-types/redis.md"
       },
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
     ]
   }
   ```

   **`catalogs/node-catalog.json`** - Available node types:
   ```json
   {
     "version": "1.0.0",
     "last_updated": "2025-10-18T15:00:00Z",
     "categories": ["computation", "database", "api", "logic", "notification", "scheduling"],
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
       },
       {
         "type": "neon",
         "name": "Neon PostgreSQL",
         "category": "database",
         "description": "PostgreSQL database operations via Neon",
         "requires_service": true,
         "service_type": "postgresql",
         "documentation_url": ".claude/instructions/node-types/neon.md",
         "parameters": {
           "required": ["connection_string", "operation"],
           "optional": ["query", "parameters", "retry_on_failure", "max_retries"]
         },
         "operations": [
           {
             "name": "execute_query",
             "description": "Execute SQL query",
             "returns": "query results"
           },
           {
             "name": "create_schema",
             "description": "Create database schema",
             "returns": "success status"
           }
         ],
         "example_usage": ".claude/instructions/examples/quotes-api.flow"
       },
       {
         "type": "aci",
         "name": "API Route Definition",
         "category": "api",
         "description": "Define REST API endpoints",
         "requires_service": false,
         "requires_server_config": true,
         "documentation_url": ".claude/instructions/node-types/aci.md",
         "parameters": {
           "required": ["mode", "operation", "route_path", "methods", "handler"],
           "optional": ["description", "auth_required", "rate_limit", "validate_input"]
         },
         "supported_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
         "example_usage": ".claude/instructions/examples/quotes-api.flow"
       },
       {
         "type": "timer",
         "name": "Scheduled Task",
         "category": "scheduling",
         "description": "Execute tasks on a schedule using cron syntax",
         "requires_service": false,
         "documentation_url": ".claude/instructions/node-types/timer.md",
         "parameters": {
           "required": ["schedule", "on_tick"],
           "optional": ["timezone", "enabled"]
         },
         "schedule_format": "cron",
         "example_schedules": {
           "every_5_min": "*/5 * * * *",
           "hourly": "0 * * * *",
           "daily_9am": "0 9 * * *"
         },
         "example_usage": ".claude/instructions/examples/scheduled-random.flow"
       },
       {
         "type": "http_request",
         "name": "HTTP Request",
         "category": "integration",
         "description": "Make outbound HTTP requests to external APIs",
         "requires_service": false,
         "documentation_url": ".claude/instructions/node-types/http-request.md",
         "parameters": {
           "required": ["method", "url"],
           "optional": ["headers", "query_params", "body", "timeout_seconds", "retry_on_failure"]
         },
         "supported_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
         "example_usage": ".claude/instructions/examples/iss-location.act"
       },
       {
         "type": "email",
         "name": "Email Notification",
         "category": "notification",
         "description": "Send email notifications via SMTP",
         "requires_service": true,
         "service_type": "email",
         "documentation_url": ".claude/instructions/node-types/email.md",
         "parameters": {
           "required": ["smtp_host", "smtp_port", "from", "to", "subject", "body"],
           "optional": ["cc", "bcc", "attachments", "body_type"]
         },
         "example_usage": ".claude/instructions/examples/price-monitor.flow"
       },
       {
         "type": "if",
         "name": "Conditional Branch",
         "category": "logic",
         "description": "Branch execution based on boolean condition",
         "requires_service": false,
         "documentation_url": ".claude/instructions/node-types/conditional.md",
         "parameters": {
           "required": ["condition", "on_true", "on_false"],
           "optional": []
         },
         "example_usage": ".claude/instructions/examples/price-monitor.flow"
       }
     ]
   }
   ```

**Deliverable:** Routing skeleton that can classify queries and knows where to load instructions + Complete catalogs

**Estimated Time:** 3-4 hours

---

### Phase 2: Essential Contexts (Priority: HIGH)
**Goal:** Create the 3 most common use cases to test routing

**Tasks:**
1. ✅ `contexts/simple-calculation.md` (~200 lines)
   - When to load: "what's X + Y?", basic math
   - Flow structure: 1 Python node
   - Build process
   - Example reference
   - Success criteria

2. ✅ `contexts/random-generation.md` (~200 lines)
   - When to load: "pick random", "random number"
   - Flow structure: 1 Python node with random.randint()
   - Response pattern: "🎲 **[number]**"

3. ✅ `contexts/simple-api.md` (~300 lines)
   - When to load: "create API", "build endpoint"
   - Flow structure: Database + 2-5 API endpoints
   - Port assignment
   - Service catalog registration

**Deliverable:** Working routing for 3 most common queries + 3 supporting example files

**Estimated Time:** 3-4 hours

**Supporting Examples (build these in Phase 2):**
1. `examples/simple-calc.act` - 47 + 89 calculation
2. `examples/random-number.act` - Random 1-50
3. `examples/quotes-api.flow` - Simple CRUD API

---

### 🚦 CHECKPOINT GATE 1 (CRITICAL)

**Purpose:** Validate core routing before proceeding

**Test 3 queries successfully:**

#### Test 1: Simple Calculation
**Query:** "what's 47 + 89?"

**Expected Behavior:**
- ✅ Must load `contexts/simple-calculation.md`
- ✅ Must create temp .act file with Python node
- ✅ Must execute via `/api/act/execute`
- ✅ Must return `**136**`
- ✅ Must NOT calculate directly

**Validation:**
```bash
# Log the routing decision
echo "Query: what's 47 + 89?"
# Check which context was loaded
# Verify .act file created in flows/temp/
# Verify execution happened
# Check response = 136
```

#### Test 2: Random Number
**Query:** "pick a random number between 1 and 50"

**Expected Behavior:**
- ✅ Must load `contexts/random-generation.md`
- ✅ Must reference `examples/random-number.act`
- ✅ Must create .act with `random.randint()`
- ✅ Must return `🎲 **[number]**`
- ✅ Number must be 1-50

**Validation:**
```bash
# Log the routing decision
echo "Query: pick a random number between 1 and 50"
# Verify random-generation.md loaded
# Check example reference
# Verify number in valid range
```

#### Test 3: Simple API
**Query:** "create an API to store quotes"

**Expected Behavior:**
- ✅ Must load `contexts/simple-api.md`
- ✅ Must reference `examples/quotes-api.flow`
- ✅ Must create .flow with database + ACI nodes
- ✅ Must assign port (9001+)
- ✅ Must register in service catalog

**Validation:**
```bash
# Log the routing decision
echo "Query: create an API to store quotes"
# Verify simple-api.md loaded
# Check .flow file structure
# Verify port assignment
# Check catalog registration
```

**Decision Criteria:**
- **ALL 3 PASS** → ✅ Proceed to Phase 3
- **ANY FAIL** → ❌ Fix routing before continuing

**Log Template:**
```
Test: [Test Name]
Query: [Input Query]
Context Loaded: [File Path]
Examples Referenced: [List]
Output File: [Path]
Execution Result: [Success/Failure]
Response: [Actual Response]
Expected Response: [Expected Response]
Status: [PASS/FAIL]
```

---

### Phase 3: Remaining Examples (Priority: HIGH)

**Goal:** Create remaining 8 examples in priority order

**Note:** 3 examples already built in Phase 2 (simple-calc, random-number, quotes-api)

**Build Order (supports Phase 4 contexts):**

1. ✅ `examples/iss-location.act` - ISS coordinates fetch
   - **Supports:** data-fetch-once.md context
   - **Complexity:** LOW (1-2 nodes, HTTP request)
   - **Pattern:** Fetch external API → Parse → Return

2. ✅ `examples/weather-fetch.act` - Weather API call
   - **Supports:** data-fetch-once.md context
   - **Complexity:** LOW (1-2 nodes, HTTP request)
   - **Pattern:** Alternative data fetch example

3. ✅ `examples/scheduled-random.flow` - Timer + random generation
   - **Supports:** scheduled-task.md context
   - **Complexity:** MEDIUM (Timer + Python)
   - **Pattern:** Timer → Logic (no storage, no API)

4. ✅ `examples/scheduled-iss-tracker.flow` - Timer + ISS + database
   - **Supports:** scheduled-task.md context
   - **Complexity:** MEDIUM (Timer + HTTP + Database)
   - **Pattern:** Timer → Fetch → Store

5. ✅ `examples/todo-api.flow` - Complex multi-entity API
   - **Supports:** complex-api.md context
   - **Complexity:** HIGH (3 tables, 10-15 endpoints)
   - **Pattern:** Tasks + Projects + Tags with relationships

6. ✅ `examples/blog-system.flow` - Posts + comments + categories
   - **Supports:** complex-api.md context
   - **Complexity:** HIGH (3-4 tables, 15-20 endpoints)
   - **Pattern:** Content management with relationships

7. ✅ `examples/restaurant-system.flow` - Full application (40+ endpoints)
   - **Supports:** full-application.md context
   - **Complexity:** VERY HIGH (5-8 tables, 40+ endpoints)
   - **Pattern:** Complete business management system

8. ✅ `examples/price-monitor.flow` - Multi-service integration
   - **Supports:** multi-service-integration.md context
   - **Complexity:** HIGH (Timer + HTTP + Database + Email + Conditional)
   - **Pattern:** Monitor → Compare → Alert → Store

**Deliverable:** 8 additional complete, tested .act/.flow files (total 11)

**Estimated Time:** 4-5 hours

**Priority Rationale:**
- Build simple examples first (iss-location, weather-fetch)
- Then scheduled tasks (scheduled-random, scheduled-iss-tracker)
- Then complex APIs (todo, blog)
- Finally full systems (restaurant, price-monitor)

---

### Phase 4: Remaining Contexts (Priority: MEDIUM)
**Goal:** Complete all 10 context files

**Tasks:**
1. ✅ `contexts/data-fetch-once.md` - One-time API calls
2. ✅ `contexts/scheduled-task.md` - Timer-based tasks
3. ✅ `contexts/complex-api.md` - 10-20 endpoints
4. ✅ `contexts/full-application.md` - 30-50+ endpoints
5. ✅ `contexts/multi-service-integration.md` - HTTP + DB + Email + Timer
6. ✅ `contexts/data-transformation.md` - ETL patterns
7. ✅ `contexts/conversation.md` - Non-execution queries

**Deliverable:** Complete context coverage for all query types

**Estimated Time:** 4-5 hours

---

### 🚦 CHECKPOINT GATE 2 (CRITICAL)

**Purpose:** Validate all 10 context routing paths before proceeding

**Test all context routing with sample queries:**

#### Test 1: Simple Calculation
**Query:** "what's 25 * 4?"
- ✅ Routes to `contexts/simple-calculation.md`
- ✅ Creates temp .act file
- ✅ Returns correct result

#### Test 2: Random Generation
**Query:** "generate a random number from 1 to 100"
- ✅ Routes to `contexts/random-generation.md`
- ✅ Uses random.randint()
- ✅ Returns number in range

#### Test 3: Data Fetch (One-Time)
**Query:** "where is the ISS right now?"
- ✅ Routes to `contexts/data-fetch-once.md`
- ✅ References `examples/iss-location.act`
- ✅ Makes HTTP request
- ✅ Returns current coordinates

#### Test 4: Scheduled Task
**Query:** "check ISS location every hour and save it"
- ✅ Routes to `contexts/scheduled-task.md`
- ✅ References `examples/scheduled-iss-tracker.flow`
- ✅ Includes timer node (cron: "0 * * * *")
- ✅ Includes database storage
- ✅ Creates .flow file (not temp)

#### Test 5: Simple API
**Query:** "create an API for storing notes"
- ✅ Routes to `contexts/simple-api.md`
- ✅ References `examples/quotes-api.flow`
- ✅ Creates 2-5 endpoints
- ✅ Includes database setup
- ✅ Assigns port (9001+)
- ✅ Registers in service catalog

#### Test 6: Complex API
**Query:** "build a blog API with posts, comments, and categories"
- ✅ Routes to `contexts/complex-api.md`
- ✅ References `examples/blog-system.flow`
- ✅ Creates 10-20 endpoints
- ✅ Multiple database tables with relationships
- ✅ Full CRUD for each entity

#### Test 7: Full Application
**Query:** "create a complete restaurant management system"
- ✅ Routes to `contexts/full-application.md`
- ✅ References `examples/restaurant-system.flow`
- ✅ Creates 30-50+ endpoints
- ✅ 5-8 database tables
- ✅ Business logic nodes
- ✅ Comprehensive system

#### Test 8: Multi-Service Integration
**Query:** "monitor competitor prices and alert me when they change"
- ✅ Routes to `contexts/multi-service-integration.md`
- ✅ References `examples/price-monitor.flow`
- ✅ Includes HTTP request nodes
- ✅ Includes database storage
- ✅ Includes conditional logic
- ✅ Includes email/webhook notification
- ✅ May include timer for recurring checks

#### Test 9: Data Transformation
**Query:** "fetch users from API and store only names and emails"
- ✅ Routes to `contexts/data-transformation.md`
- ✅ HTTP request → Python transform → Database insert
- ✅ Transformation logic present

#### Test 10: Conversation
**Query:** "hello, what can you do?"
- ✅ Routes to `contexts/conversation.md`
- ✅ NO .act/.flow file created
- ✅ Conversational response about capabilities
- ✅ No execution attempted

**Success Criteria:**
- **≥90% accuracy (9/10 or 10/10)** → ✅ Proceed to Phase 5
- **<90% accuracy** → ❌ Debug routing logic, fix issues, re-test

**Log Each Test:**
```
Test #: [1-10]
Context: [Name]
Query: [Input]
Expected Route: [Context file]
Actual Route: [Context file]
Examples Referenced: [List]
Output Type: [temp .act / .flow / none]
Validation Checks: [List of assertions]
Status: [PASS/FAIL]
Notes: [Any observations]
```

**Aggregate Results:**
```
Total Tests: 10
Passed: [X]
Failed: [Y]
Accuracy: [X/10 = Z%]
Decision: [PROCEED / DEBUG]
```

---

### Phase 5: Node Type References (Priority: MEDIUM)
**Goal:** Create detailed documentation for each node type

**Tasks:**
1. ✅ `node-types/python.md` - Python execution
2. ✅ `node-types/javascript.md` - JavaScript execution
3. ✅ `node-types/bash.md` - Bash commands
4. ✅ `node-types/neon.md` - PostgreSQL (Neon)
5. ✅ `node-types/mongo.md` - MongoDB
6. ✅ `node-types/neo4j.md` - Neo4j graph database
7. ✅ `node-types/redis.md` - Redis cache
8. ✅ `node-types/aci.md` - API route definition
9. ✅ `node-types/http-request.md` - Outbound HTTP calls
10. ✅ `node-types/timer.md` - Cron scheduling
11. ✅ `node-types/email.md` - Email notifications
12. ✅ `node-types/webhook.md` - Webhook handlers
13. ✅ `node-types/conditional.md` - If/switch logic
14. ✅ `node-types/loop.md` - Iteration
15. ✅ `node-types/claude-ai.md` - Claude AI integration

Each file (~100-150 lines):
- When to use
- Parameters
- Code examples
- Common patterns
- Gotchas
- Best practices

**Deliverable:** Complete node type reference library

**Estimated Time:** 5-6 hours

---

### Phase 6: Patterns & Common (Priority: LOW)
**Goal:** Add reusable patterns and shared knowledge

**Tasks:**

**Patterns (5 files):**
1. ✅ `patterns/crud-api-pattern.md` - Standard CRUD structure
2. ✅ `patterns/scheduled-fetcher-pattern.md` - Timer → HTTP → DB
3. ✅ `patterns/monitor-alert-pattern.md` - Timer → HTTP → Conditional → Email
4. ✅ `patterns/etl-pipeline-pattern.md` - Extract → Transform → Load
5. ✅ `patterns/webhook-handler-pattern.md` - Webhook → Process → Store

**Common (4 files):**
1. ✅ `common/data-access-syntax.md` - How to access data between nodes
2. ✅ `common/edge-patterns.md` - Sequential, parallel, conditional
3. ✅ `common/execution-process.md` - How to execute via API
4. ✅ `common/catalog-usage.md` - How to read catalogs

**Deliverable:** Pattern library and shared knowledge base

**Estimated Time:** 3-4 hours

---

### Phase 7: Testing & Validation (Priority: CRITICAL)
**Goal:** Ensure all routing paths work correctly

**Tasks:**
1. ✅ Test simple calculation routing
   - Query: "what's 47 + 89?"
   - Expected: Load contexts/simple-calculation.md
   - Expected: Create temp .act file
   - Expected: Execute and return "**136**"

2. ✅ Test random number routing
   - Query: "pick a random number between 1 and 50"
   - Expected: Load contexts/random-generation.md
   - Expected: Use examples/random-number.act
   - Expected: Return "🎲 **[number]**"

3. ✅ Test simple API routing
   - Query: "create API for quotes"
   - Expected: Load contexts/simple-api.md
   - Expected: Use examples/quotes-api.flow as reference
   - Expected: Generate new .flow file
   - Expected: Register in service catalog

4. ✅ Test complex API routing
   - Query: "build todo list API with projects and tags"
   - Expected: Load contexts/complex-api.md
   - Expected: Create 10+ endpoints
   - Expected: Multiple database tables

5. ✅ Test full application routing
   - Query: "create restaurant management system"
   - Expected: Load contexts/full-application.md
   - Expected: Use examples/restaurant-system.flow
   - Expected: 30-50+ endpoints

6. ✅ Test scheduled task routing
   - Query: "check ISS location every hour and save it"
   - Expected: Load contexts/scheduled-task.md
   - Expected: Include timer node
   - Expected: Include database storage

7. ✅ Test multi-service integration
   - Query: "monitor competitor prices and alert me"
   - Expected: Load contexts/multi-service-integration.md
   - Expected: HTTP + DB + Email nodes

8. ✅ Test conversation routing
   - Query: "hello, what can you do?"
   - Expected: Load contexts/conversation.md
   - Expected: NO ACT file creation
   - Expected: Conversational response

9. ✅ Verify catalog reading
   - Agent should read catalogs before building flows
   - Agent should use available node types from catalog

10. ✅ Verify example file usage
    - Agent should reference example files
    - Agent should adapt examples to user needs

**Deliverable:** All routing paths validated, bugs fixed

**Estimated Time:** 3-4 hours

---

### Phase 8: Polish & Documentation (Priority: LOW)
**Goal:** Final cleanup and documentation

**Tasks:**
1. ✅ Add comments to all files
2. ✅ Ensure consistent formatting
3. ✅ Create migration guide from old to new system
4. ✅ Update any references to old CLAUDE.md
5. ✅ Performance testing (response times)
6. ✅ Context window usage analysis

**Deliverable:** Production-ready modular agent system

**Estimated Time:** 2-3 hours

---

## File Count Summary

| Category | Files | Lines Each | Total Lines |
|----------|-------|------------|-------------|
| Core Agent | 1 | 150 | 150 |
| Contexts | 10 | 200-300 | ~2,500 |
| Examples | 11 | 50-200 | ~1,200 |
| Node Types | 15 | 100-150 | ~1,800 |
| Patterns | 5 | 150-200 | ~850 |
| Common | 4 | 100-150 | ~500 |
| Catalogs | 2 | 100-200 | ~300 |
| **TOTAL** | **48** | - | **~7,300** |

**Key Benefit:** Agent only loads 150-500 lines per query instead of 774+ lines!

---

## Success Criteria

After implementation, the agent should:
- ✅ Route 100% of queries to correct context
- ✅ Always use ACT execution (never bypass for calculations)
- ✅ Load only relevant files per query (not everything)
- ✅ Respond in <5 seconds for simple queries
- ✅ Create valid .act/.flow files every time
- ✅ Scale appropriately (simple → complex)
- ✅ Maintain AI OS persona throughout
- ✅ Reference correct example files
- ✅ Read catalogs before building flows
- ✅ Register services in catalog when appropriate

---

## Benefits of New Architecture

### 1. **Efficiency**
- Old: Load 774 lines every time
- New: Load 150 (router) + 200-300 (context) = 350-450 lines
- **50% reduction in context usage**

### 2. **Maintainability**
- Old: Edit massive file, risk breaking everything
- New: Edit one context file, isolated changes
- **10x easier to maintain**

### 3. **Scalability**
- Old: Adding new patterns increases file size
- New: Add new context file, no impact on others
- **Infinite scalability**

### 4. **Accuracy**
- Old: Agent sees all instructions, may get confused
- New: Agent sees only relevant instructions
- **Higher accuracy**

### 5. **Speed**
- Old: Agent processes all instructions
- New: Agent processes only what's needed
- **Faster responses**

### 6. **Testability**
- Old: Test entire system at once
- New: Test each context independently
- **Easier debugging**

---

## Migration Strategy

### Step 1: Parallel Development
- Build new system alongside old
- Test thoroughly
- Compare outputs

### Step 2: A/B Testing
- Route 10% of queries to new system
- Monitor accuracy and performance
- Gradually increase to 100%

### Step 3: Deprecation
- Archive old CLAUDE.md
- Update all references
- Document migration

### Step 4: Optimization
- Monitor context usage
- Optimize file sizes
- Add more examples as needed

---

## Risk Mitigation

### Risk 1: Routing Errors
**Mitigation:** Comprehensive test suite covering all query types

### Risk 2: Missing Context
**Mitigation:** Default fallback context for unknown queries

### Risk 3: Example Files Break
**Mitigation:** Validate all examples before deployment

### Risk 4: Catalog Out of Date
**Mitigation:** Auto-sync catalogs with actual services

---

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Foundation | 2-3 hours | None |
| Phase 2: Essential Contexts | 3-4 hours | Phase 1 |
| Phase 3: Examples | 4-5 hours | Phase 1 |
| Phase 4: Remaining Contexts | 4-5 hours | Phase 2, 3 |
| Phase 5: Node Types | 5-6 hours | Phase 1 |
| Phase 6: Patterns | 3-4 hours | Phase 2, 3 |
| Phase 7: Testing | 3-4 hours | All previous |
| Phase 8: Polish | 2-3 hours | All previous |
| **TOTAL** | **26-34 hours** | - |

**Recommended:** 1 week of focused development (4-5 hours/day)

---

## Next Steps

1. ✅ Review and approve this plan
2. ✅ Start Phase 1: Create directory structure
3. ✅ Build core routing agent
4. ✅ Test basic routing
5. ✅ Proceed phase by phase
6. ✅ Validate at each step

**Ready to start? Let's build the modular agent system!** 🚀
