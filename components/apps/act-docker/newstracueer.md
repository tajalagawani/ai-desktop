# Complete Modular Agent Architecture Plan

## 📁 Directory Structure

```
flow-architect/
├── catalogs/
│   ├── service-catalog.json          # Runtime services (Docker, DBs)
│   └── node-catalog.json             # Available node types
│
├── flows/                             # Generated .act/.flow files
│   ├── [user-generated-flows].flow
│   └── temp/                          # Temporary executions
│
├── .claude/
│   ├── agents/
│   │   └── flow-architect.md         # CORE: Tiny routing agent (150 lines)
│   │
│   └── instructions/                  # MODULAR INSTRUCTIONS
│       │
│       ├── 📁 contexts/               # Query-type specific instructions
│       │   ├── simple-calculation.md
│       │   ├── random-generation.md
│       │   ├── data-fetch-once.md
│       │   ├── scheduled-task.md
│       │   ├── simple-api.md
│       │   ├── complex-api.md
│       │   ├── full-application.md
│       │   ├── multi-service-integration.md
│       │   ├── data-transformation.md
│       │   └── conversation.md
│       │
│       ├── 📁 examples/               # Complete working examples
│       │   ├── simple-calc.act
│       │   ├── random-number.act
│       │   ├── iss-location.act
│       │   ├── weather-fetch.act
│       │   ├── scheduled-random.flow
│       │   ├── scheduled-iss-tracker.flow
│       │   ├── quotes-api.flow
│       │   ├── todo-api.flow
│       │   ├── blog-system.flow
│       │   ├── restaurant-system.flow
│       │   └── price-monitor.flow
│       │
│       ├── 📁 node-types/             # Node type references
│       │   ├── python.md
│       │   ├── javascript.md
│       │   ├── bash.md
│       │   ├── neon.md
│       │   ├── mongo.md
│       │   ├── neo4j.md
│       │   ├── redis.md
│       │   ├── aci.md
│       │   ├── http-request.md
│       │   ├── timer.md
│       │   ├── email.md
│       │   ├── webhook.md
│       │   ├── conditional.md
│       │   ├── loop.md
│       │   └── claude-ai.md
│       │
│       ├── 📁 patterns/               # Common workflow patterns
│       │   ├── crud-api-pattern.md
│       │   ├── scheduled-fetcher-pattern.md
│       │   ├── monitor-alert-pattern.md
│       │   ├── etl-pipeline-pattern.md
│       │   └── webhook-handler-pattern.md
│       │
│       └── 📁 common/                 # Shared knowledge
│           ├── data-access-syntax.md
│           ├── edge-patterns.md
│           ├── execution-process.md
│           └── catalog-usage.md
```

---

## 🎯 Core Agent File (flow-architect.md)

**Size: ~150 lines**
**Purpose: Routing + Identity only**

### Structure:

```markdown
# Flow Architect Agent

## 🔴 CRITICAL RULE
[Mandatory ACT execution enforcement - 20 lines]

## Identity
[Who you are - AI OS persona - 15 lines]

## Query Classification Router
[Map user intent → context file - 40 lines]

## Process Flow
[5-step execution process - 20 lines]

## Resource Locations
[Where to find catalogs, examples, contexts - 10 lines]

## Execution API
[How to call /api/act/execute - 15 lines]

## Output Paths
[Where to save flows - 10 lines]

## Checklist
[Pre-response validation - 20 lines]
```

---

## 📋 Context Files (10 files, each ~200-300 lines)

### 1. `contexts/simple-calculation.md`

```markdown
# Simple Calculation Context

## When to Load This
- User asks: "what's X + Y?", "calculate", "solve"
- Math operations: +, -, *, /, %, **
- Single calculation, no storage

## Complexity Level: MINIMAL

## Flow Structure
- 1 Python node
- No database
- No server config
- Quick execution (temp file)

## Example Patterns
- "what's 47 + 89?"
- "calculate 15 * 23"
- "what's 100 / 4?"
- "solve 2^8"

## Build Process
1. Create Python node with calculation
2. Save to flows/temp/calc-[timestamp].act
3. Execute via /api/act/execute
4. Parse result
5. Respond with number

## Load Example
Read: .claude/instructions/examples/simple-calc.act

## Node Types Needed
Read: .claude/instructions/node-types/python.md

## Response Pattern
"**[number]**"

(No explanation unless asked)

## Common Mistakes to Avoid
- ❌ Don't answer without ACT execution
- ❌ Don't create API server for simple calc
- ❌ Don't add database storage
- ❌ Don't over-engineer

## Success Criteria
- ✅ ACT flow created
- ✅ Executed through API
- ✅ Correct result returned
- ✅ User sees just the answer
```

---

### 2. `contexts/random-generation.md`

```markdown
# Random Generation Context

## When to Load This
- User asks: "pick random", "generate random", "random number"
- Between two numbers or from range

## Complexity Level: MINIMAL

## Flow Structure
- 1 Python node with random.randint()
- No database
- No server config
- Quick execution

## Example Patterns
- "pick a random number between 1 and 50"
- "generate random number from 1-100"
- "give me a random number"

## Build Process
1. Create Python node with random.randint(min, max)
2. Save to flows/temp/random-[timestamp].act
3. Execute
4. Parse result
5. Respond with emoji + number

## Load Example
Read: .claude/instructions/examples/random-number.act

## Response Pattern
"🎲 **[number]**"

## Success Criteria
- ✅ Used random.randint() in Python
- ✅ Result is truly random (not hardcoded)
- ✅ Within specified range
```

---

### 3. `contexts/data-fetch-once.md`

```markdown
# One-Time Data Fetch Context

## When to Load This
- User asks: "where is", "what is current", "get [data]"
- Single fetch, no persistence needed
- External API call

## Complexity Level: LOW

## Flow Structure
- 1-2 nodes (HTTP request + optional Python processing)
- No database
- No server config
- Quick execution

## Example Patterns
- "where is the ISS right now?"
- "what's the current weather in Paris?"
- "get bitcoin price"

## Build Process
1. HTTP request node to fetch data
2. Optional: Python node to parse/format
3. Save to flows/temp/fetch-[name]-[timestamp].act
4. Execute
5. Respond with data

## Load Examples
- .claude/instructions/examples/iss-location.act
- .claude/instructions/examples/weather-fetch.act

## Node Types Needed
- .claude/instructions/node-types/http-request.md
- .claude/instructions/node-types/python.md

## Response Pattern
"The ISS is currently at Latitude: [X]°, Longitude: [Y]°"

## Common APIs
- ISS Location: http://api.open-notify.org/iss-now.json
- Weather: https://api.open-meteo.com/v1/forecast
- Crypto: https://api.coingecko.com/api/v3/simple/price
```

---

### 4. `contexts/scheduled-task.md`

```markdown
# Scheduled Task Context

## When to Load This
- User asks: "every X minutes", "repeatedly", "check hourly"
- Recurring execution needed
- May or may not need storage

## Complexity Level: MEDIUM

## Flow Structure
- Timer node (cron schedule)
- Logic node(s) (Python/HTTP)
- Optional: Database for history
- Optional: API to view results
- Minimal server config (no API endpoints unless requested)

## Example Patterns
- "generate random number every 10 minutes"
- "check ISS location every hour and save it"
- "fetch weather every 4 hours"

## Decision Tree
1. Does user want to store history?
   - YES → Add database + maybe API
   - NO → Just timer + logic

2. Does user want to access results?
   - YES → Add API endpoints
   - NO → Just run in background

## Build Process
1. Read node-types/timer.md for schedule syntax
2. Create timer node with cron expression
3. Add logic nodes
4. If storage needed: Add database nodes
5. If API needed: Add ACI nodes
6. Save to flows/scheduled-[name].flow
7. Deploy with minimal server config
8. Register in catalog if API included

## Load Examples
- .claude/instructions/examples/scheduled-random.flow
- .claude/instructions/examples/scheduled-iss-tracker.flow

## Cron Expression Reference
- Every 5 min: "*/5 * * * *"
- Every hour: "0 * * * *"
- Every 4 hours: "0 */4 * * *"
- Daily at 9 AM: "0 9 * * *"

## Response Pattern
"✓ [Task name] active

Running every [interval]
[Storage status if applicable]
[Access info if API exists]

First execution: [result if immediate run]"
```

---

### 5. `contexts/simple-api.md`

```markdown
# Simple API Context

## When to Load This
- User asks: "create API", "build endpoint"
- 2-5 endpoints
- Single entity or simple use case
- Basic CRUD operations

## Complexity Level: MEDIUM

## Flow Structure
- Database table(s): 1-2
- API endpoints: 2-5
- ACI nodes for routes
- Handler nodes (Neon/Python)
- Full server configuration
- Service catalog registration

## Example Patterns
- "create API to store and get quotes"
- "build API for tracking my expenses"
- "make endpoint to save notes"

## Build Process
1. Read catalogs/service-catalog.json for database
2. Design database schema (1-2 tables)
3. Create table creation nodes
4. Create CRUD endpoints:
   - POST to create
   - GET to retrieve
   - Optional: PUT to update
   - Optional: DELETE to remove
5. Add ACI nodes for each route
6. Add handler nodes
7. Full server config
8. Find next available port (9001+)
9. Register in service catalog
10. Save to flows/[name]-api.flow

## Load Example
Read: .claude/instructions/examples/quotes-api.flow

## Node Types Needed
- .claude/instructions/node-types/aci.md
- .claude/instructions/node-types/neon.md
- .claude/instructions/node-types/python.md

## Port Assignment
Check existing ports:
```bash
grep "^port = " flows/*.flow | sort -t= -k2 -n | tail -1
```
Next port = last port + 1

## Response Pattern
"✓ [Name] API active at http://[machine]:[port]

Endpoints:
• POST /api/[resource] - Create [resource]
• GET /api/[resource] - List [resources]
[Additional endpoints...]

Try it: curl http://[machine]:[port]/api/[resource]"

## Service Catalog Entry
Always include:
- service_name
- service_type: "api"
- description
- icon (relevant emoji)
- category
- endpoints list
```

---

### 6. `contexts/complex-api.md`

```markdown
# Complex API Context

## When to Load This
- User asks for API with 10+ endpoints
- Multiple related entities
- Business logic required
- Relationships between entities

## Complexity Level: HIGH

## Flow Structure
- Database tables: 3-5+
- API endpoints: 10-20+
- Complex relationships
- Business logic nodes
- Full server configuration
- Comprehensive catalog registration

## Example Patterns
- "build a todo list API with tasks, projects, tags"
- "create blog API with posts, comments, categories"
- "make inventory system with products, suppliers, orders"

## Build Process
1. Read catalogs for available services
2. Design complete database schema
   - Identify entities
   - Define relationships
   - Plan indexes
3. Create all tables with foreign keys
4. Create CRUD for each entity (4-5 endpoints per entity)
5. Add relationship endpoints (get posts with comments, etc.)
6. Add business logic (calculations, validations)
7. Optional: Add analytics endpoints
8. Full server config with proper port
9. Comprehensive catalog registration
10. Save to flows/[name]-system.flow

## Load Examples
- .claude/instructions/examples/todo-api.flow
- .claude/instructions/examples/blog-system.flow

## Entity Planning Template
For each entity:
- POST /api/[entity] - Create
- GET /api/[entity] - List all
- GET /api/[entity]/{id} - Get one
- PUT /api/[entity]/{id} - Update
- DELETE /api/[entity]/{id} - Delete

## Response Pattern
"✓ [System Name] ready

I've built:
→ [Entity 1] management
→ [Entity 2] management
→ [Entity 3] management

Access: http://[machine]:[port]

Available operations:
• [Entity 1]: GET, POST, PUT, DELETE /api/[entity1]
• [Entity 2]: GET, POST, PUT, DELETE /api/[entity2]
[Additional entities...]

Relationships:
• GET /api/[entity1]/{id}/[entity2] - Get related items

[Sample data status if any]"
```

---

### 7. `contexts/full-application.md`

```markdown
# Full Application Context

## When to Load This
- User asks: "complete system", "management system", "platform"
- 5+ entities
- 30-50+ endpoints
- Complex business logic
- May include: scheduled tasks, notifications, analytics

## Complexity Level: VERY HIGH

## Flow Structure
- Database tables: 5-10+
- API endpoints: 30-50+
- Business logic: 10-20+ Python nodes
- Maybe: Timer nodes for scheduled tasks
- Maybe: Email/webhook nodes for notifications
- Maybe: Analytics/reporting endpoints
- Full server configuration
- Comprehensive catalog registration

## Example Patterns
- "build complete restaurant management system"
- "create e-commerce platform"
- "make project management system"
- "build CRM system"

## Build Process
1. **Planning Phase**
   - Read both catalogs
   - List all entities (5-10+)
   - Map relationships
   - Identify business logic
   - Plan scheduled tasks
   - Plan notifications

2. **Database Phase**
   - Create all tables
   - Set up foreign keys
   - Create indexes
   - Load sample data (optional)

3. **CRUD Phase**
   - Create full CRUD for each entity
   - 5 endpoints per entity minimum

4. **Business Logic Phase**
   - Order calculations
   - Inventory management
   - Status workflows
   - Validations

5. **Advanced Features**
   - Analytics endpoints
   - Search/filter endpoints
   - Reporting

6. **Automation** (if needed)
   - Scheduled tasks
   - Email notifications
   - Webhook handlers

7. **Deployment**
   - Full server config
   - Next available port
   - Comprehensive catalog entry
   - Save to flows/[name]-platform.flow

## Load Example
Read: .claude/instructions/examples/restaurant-system.flow

## Response Pattern
"✓ [System Name] ready

I've built a complete system with:

**Data Structure:**
→ [Entity 1] (with [fields])
→ [Entity 2] (with [fields])
→ [Entity 3] (with [fields])
[... all entities]

**API Access:** http://[machine]:[port]

**Core Operations:**
• [Entity 1]: Full CRUD at /api/[entity1]
• [Entity 2]: Full CRUD at /api/[entity2]
[... all entities]

**Business Features:**
→ [Business logic 1]
→ [Business logic 2]
→ [Calculations/workflows]

**Advanced Features:**
→ Analytics at /api/analytics
→ Reports at /api/reports
[If scheduled tasks: → Automated [task] every [interval]]
[If notifications: → Email alerts for [events]]

[Sample data status]

Try it: curl http://[machine]:[port]/api/[resource]"
```

---

### 8. `contexts/multi-service-integration.md`

```markdown
# Multi-Service Integration Context

## When to Load This
- User asks to combine multiple actions
- Keywords: "monitor and alert", "fetch and store", "process and notify"
- Requires: HTTP + Database + Email/Webhook + Maybe Timer

## Complexity Level: HIGH

## Flow Structure
- HTTP request nodes (external data)
- Database nodes (storage)
- Conditional nodes (logic)
- Email/webhook nodes (notifications)
- Timer nodes (if scheduled)
- Optional: API for access
- Full server configuration
- Service catalog registration

## Example Patterns
- "monitor competitor prices, alert me on changes, store history"
- "fetch crypto prices hourly, if drops alert me, show analytics"
- "check website status every 5 min, alert if down, track uptime"

## Build Process
1. **Identify Components**
   - What to monitor? → HTTP request
   - When to check? → Timer (if recurring)
   - What to store? → Database
   - When to notify? → Conditional logic
   - How to notify? → Email/Webhook

2. **Read Required Catalogs**
   - Service catalog for database
   - Node catalog for all node types

3. **Build Monitoring**
   - HTTP request nodes
   - Parsing/processing nodes

4. **Build Storage**
   - Database tables for history
   - Insert nodes

5. **Build Logic**
   - Comparison nodes
   - Conditional branching

6. **Build Alerting**
   - Email/webhook nodes
   - Alert conditions

7. **Build Access** (optional)
   - API endpoints to view history
   - Analytics endpoints

8. **Deploy**
   - Full server config
   - Port assignment
   - Catalog registration
   - Save to flows/[name]-monitor.flow

## Load Example
Read: .claude/instructions/examples/price-monitor.flow

## Node Types Needed
- .claude/instructions/node-types/http-request.md
- .claude/instructions/node-types/timer.md
- .claude/instructions/node-types/neon.md
- .claude/instructions/node-types/email.md
- .claude/instructions/node-types/conditional.md

## Response Pattern
"✓ [Monitor Name] active

I'm now tracking:
→ [What's being monitored]
→ [Check frequency]
→ [Storage details]

Alert conditions:
→ [When notifications trigger]
→ [How you'll be notified]

Dashboard: http://[machine]:[port]
• GET /api/current - Current status
• GET /api/history - Historical data
• GET /api/analytics - Trends

First check: [immediate result if applicable]"
```

---

### 9. `contexts/data-transformation.md`

```markdown
# Data Transformation Context

## When to Load This
- User asks: "convert", "transform", "process data"
- Input → Process → Output pattern
- No long-term storage typically

## Complexity Level: LOW-MEDIUM

## Flow Structure
- Input node (HTTP/database/file)
- Processing node(s) (Python)
- Output node (database/API/file)
- Optional: API to trigger transformation

## Example Patterns
- "fetch users from API and store only names and emails"
- "convert CSV to JSON"
- "get orders from database and calculate totals"

## Build Process
1. Identify input source
2. Identify transformation logic
3. Identify output destination
4. Build flow:
   - Input node
   - Transform node (Python usually)
   - Output node
5. Save appropriately based on use (temp vs persistent)

## Response Pattern
"✓ Data transformation ready

Input: [source]
Processing: [what transformations]
Output: [destination]

[If API: Access at http://[machine]:[port]/api/transform]
[If immediate: Processed [X] items]"
```

---

### 10. `contexts/conversation.md`

```markdown
# Conversation Context

## When to Load This
- User is chatting, not requesting action
- Questions about capabilities
- Clarifications
- Greetings

## NO ACT FLOW NEEDED

## Example Patterns
- "hey, what can you do?"
- "hello"
- "how does this work?"
- "what's an ACT flow?"
- "can you help me with..."

## Response Strategy
Be conversational, helpful, and natural.

Explain capabilities:
- Handle simple calculations to complete systems
- Create APIs and scheduled tasks
- Monitor and alert
- Process and transform data
- Integrate multiple services

Ask clarifying questions if needed:
- "What would you like to accomplish?"
- "What data do you need to track?"
- "How often should this run?"

## When User Asks "How It Works"
Explain in OS terms first:
- "I have persistent memory (databases)"
- "I can schedule routines (timers)"
- "I can expose interfaces (APIs)"

Only show technical details if they ask:
- "Want to see the actual workflow structure?"
```

---

## 📝 Example Files (11 files)

### 1. `examples/simple-calc.act`

```toml
[workflow]
name = "Simple Calculation"
description = "Calculate 47 + 89"
start_node = Calculate

[node:Calculate]
type = "py"
label = "Perform calculation"
code = """
def calculate():
    result = 47 + 89
    return {"result": result}
"""
function = "calculate"
```

---

### 2. `examples/random-number.act`

```toml
[workflow]
name = "Random Number Generator"
description = "Generate random number between 1 and 50"
start_node = Generate

[node:Generate]
type = "py"
label = "Generate random number"
code = """
import random

def generate():
    number = random.randint(1, 50)
    return {"result": number}
"""
function = "generate"
```

---

### 3. `examples/iss-location.act`

```toml
[workflow]
name = "ISS Location Fetcher"
description = "Get current ISS location"
start_node = FetchISS

[node:FetchISS]
type = "py"
label = "Fetch ISS coordinates"
code = """
import urllib.request
import json

def fetch_iss():
    url = 'http://api.open-notify.org/iss-now.json'
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    
    latitude = data['iss_position']['latitude']
    longitude = data['iss_position']['longitude']
    
    return {
        "result": {
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": data['timestamp']
        }
    }
"""
function = "fetch_iss"
```

---

### 4. `examples/scheduled-random.flow`

```toml
[workflow]
name = "Scheduled Random Number"
description = "Generate random number every 10 minutes"
start_node = Timer

[settings]
debug_mode = true
max_retries = 3
timeout_seconds = 300

[configuration]
agent_enabled = true
agent_name = "random-scheduler"
agent_version = "1.0.0"

[node:Timer]
type = "timer"
label = "Every 10 minutes"
schedule = "*/10 * * * *"
timezone = "UTC"
on_tick = "Generate"

[node:Generate]
type = "py"
label = "Generate random number"
code = """
import random
from datetime import datetime

def generate():
    number = random.randint(1, 100)
    timestamp = datetime.now().isoformat()
    
    print(f"Generated {number} at {timestamp}")
    
    return {"result": {"number": number, "timestamp": timestamp}}
"""
function = "generate"

[edges]
Timer = Generate
```

---

### 5. `examples/quotes-api.flow`

```toml
[workflow]
name = "Quotes API"
description = "Simple API to store and retrieve quotes"
start_node = CreateQuotesTable

[settings]
debug_mode = true
max_retries = 3
timeout_seconds = 600

[configuration]
agent_enabled = true
agent_name = "quotes-api"
agent_version = "1.0.0"

[server]
host = "0.0.0.0"
port = 9001
cors = {enabled = true, origins = ["*"]}
environment = "development"
auto_restart = true

[deployment]
environment = "production"

[service_catalog]
register = true
service_name = "Quotes API"
service_type = "api"
description = "Store and retrieve favorite quotes"
icon = "💬"
category = "utility"
endpoints = [
  {path = "/api/quotes", method = "GET", description = "Get all quotes"},
  {path = "/api/quotes", method = "POST", description = "Add new quote"}
]

[parameters]
database_url = "{{.env.DATABASE_URL}}"

[env]
DATABASE_URL = "postgresql://connection-string"

[node:CreateQuotesTable]
type = "neon"
label = "Create quotes table"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = """
CREATE TABLE IF NOT EXISTS quotes (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    author VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

[node:DefineGetQuotesRoute]
type = "aci"
mode = "server"
label = "GET /api/quotes"
operation = "add_route"
route_path = "/api/quotes"
methods = ["GET"]
handler = "GetQuotes"
description = "Get all quotes"

[node:GetQuotes]
type = "neon"
label = "Fetch all quotes"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = "SELECT id, text, author, created_at FROM quotes ORDER BY created_at DESC"

[node:DefineAddQuoteRoute]
type = "aci"
mode = "server"
label = "POST /api/quotes"
operation = "add_route"
route_path = "/api/quotes"
methods = ["POST"]
handler = "AddQuote"
description = "Add new quote"

[node:AddQuote]
type = "neon"
label = "Insert quote"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = "INSERT INTO quotes (text, author) VALUES (%s, %s) RETURNING id, text, author, created_at"
parameters = ["{{request_data.text}}", "{{request_data.author}}"]

[edges]
CreateQuotesTable = DefineGetQuotesRoute
CreateQuotesTable = DefineAddQuoteRoute
DefineGetQuotesRoute = GetQuotes
DefineAddQuoteRoute = AddQuote
```

---

## 📚 Node Type Reference Files (14 files)

Each file ~100-150 lines explaining:
- When to use
- Parameters
- Examples
- Common patterns
- Gotchas

I'll create summaries for key ones:

### `node-types/python.md`
- Execution of Python code
- Function definition pattern
- Return structure
- Accessing kwargs
- Timeout settings
- Error handling

### `node-types/aci.md`
- API route definition
- Methods supported
- Handler connection
- Request data access
- Validation
- Auth options

### `node-types/neon.md`
- PostgreSQL operations
- Connection strings
- Query execution
- Parameters/placeholders
- Schema operations
- Transaction handling

### `node-types/timer.md`
- Cron syntax
- Schedule patterns
- Timezone handling
- On-tick handlers
- Common schedules reference

### `node-types/http-request.md`
- Outbound HTTP calls
- Methods (GET/POST/PUT/DELETE)
- Headers
- Query params
- Body formats
- Retry logic
- Timeout settings

---

## 🎨 Pattern Files (5 files)

### `patterns/crud-api-pattern.md`
Standard CRUD API structure template

### `patterns/scheduled-fetcher-pattern.md`
Timer → HTTP → Database pattern

### `patterns/monitor-alert-pattern.md`
Timer → HTTP → Conditional → Email pattern

### `patterns/etl-pipeline-pattern.md`
Extract → Transform → Load pattern

### `patterns/webhook-handler-pattern.md`
Webhook → Process → Store pattern

---

## 🔧 Common Files (4 files)

### `common/data-access-syntax.md`
How to access data between nodes

### `common/edge-patterns.md`
Sequential, parallel, conditional edges

### `common/execution-process.md`
How to execute flows via API

### `common/catalog-usage.md`
How to read and use catalogs

---

## 🚀 Implementation Plan

### Phase 1: Core Structure (Day 1)
1. Create directory structure
2. Write core `flow-architect.md` (routing agent)
3. Write 3 most common contexts:
   - simple-calculation.md
   - random-generation.md
   - simple-api.md
4. Write 3 corresponding examples
5. Test basic routing

### Phase 2: Essential Contexts (Day 2)
6. Write remaining 7 context files
7. Write all 11 example files
8. Test each context path

### Phase 3: Node References (Day 3)
9. Write 14 node-type reference files
10. Test agent reading references

### Phase 4: Patterns & Common (Day 4)
11. Write 5 pattern files
12. Write 4 common files
13. Integration testing

### Phase 5: Polish & Test (Day 5)
14. Test all 10 context paths
15. Verify example files work
16. Check routing logic
17. Performance testing
18. Documentation

---

## ✅ Benefits of This Architecture

1. **Small Context Window** - Agent only loads what it needs
2. **Fast Responses** - Less processing per query
3. **Maintainable** - Edit one file without breaking others
4. **Scalable** - Add new contexts easily
5. **Accurate** - Context-specific guidance
6. **Testable** - Test each context independently
7. **Clear** - One file = one purpose
8. **Flexible** - Mix and match components

---

## 🎯 Success Metrics

After implementation, agent should:
- ✅ Route 100% of queries to correct context
- ✅ Always use ACT execution (never bypass)
- ✅ Load only relevant files per query
- ✅ Respond in <5 seconds for simple queries
- ✅ Create valid .act/.flow files every time
- ✅ Scale appropriately (simple → complex)
- ✅ Maintain AI OS persona throughout

---

**Ready to start building? Which phase should we tackle first?** 🚀