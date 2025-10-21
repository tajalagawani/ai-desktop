# Flow Architect Tools & Skills - Comprehensive Implementation Plan

**Version:** 1.0
**Date:** 2025-10-20
**Status:** Awaiting Approval

---

## 📋 Table of Contents

1. [Problem Statement](#problem-statement)
2. [Solution Architecture](#solution-architecture)
3. [Bash Tools Specification](#bash-tools-specification)
4. [Skills Specification](#skills-specification)
5. [Context Files Update Plan](#context-files-update-plan)
6. [Complete Workflow Examples](#complete-workflow-examples)
7. [Implementation Steps](#implementation-steps)
8. [Testing Strategy](#testing-strategy)
9. [Success Criteria](#success-criteria)

---

## 1. Problem Statement

### Current Issues

**Issue 1: Wrong API Endpoints**
```markdown
# Current in contexts (WRONG):
curl -s http://localhost:3000/api/catalog?type=infrastructure&status=running

# This endpoint doesn't exist anymore!
# /api/catalog now only returns flow services
```

**Issue 2: No Environment Awareness**
- Agent doesn't know what services are running
- Agent hardcodes connection strings
- Agent doesn't check authentication
- Agent doesn't know about Security Center

**Issue 3: No ACT Knowledge Persistence**
- ACT syntax and best practices repeated in every context file
- No central place for ACT examples
- Agent reinvents patterns every time

**Issue 4: Repetitive Code**
- Same `curl | jq` commands in 6 different context files
- API changes require updating 6 files
- Error handling duplicated everywhere

---

## 2. Solution Architecture

### Two-Part Solution

```
┌─────────────────────────────────────────────────────┐
│              Flow Architect Agent                   │
└─────────────────────────────────────────────────────┘
                        │
          ┌─────────────┴─────────────┐
          │                           │
          ▼                           ▼
┌─────────────────┐          ┌──────────────────┐
│   Bash Tools    │          │     Skills       │
│  (Environment)  │          │  (ACT Knowledge) │
└─────────────────┘          └──────────────────┘
          │                           │
          │                           │
          ▼                           ▼
┌─────────────────┐          ┌──────────────────┐
│  Discovery APIs │          │  Documentation   │
│  - /api/services│          │  - Syntax        │
│  - /api/nodes   │          │  - Examples      │
│  - /api/catalog │          │  - Patterns      │
│  - /api/unified │          │  - Best Practices│
└─────────────────┘          └──────────────────┘
```

### Part 1: Bash Tools (Environment Discovery)

**Purpose:** Abstract API calls into reusable tools

**Location:** `flow-architect/tools/`

**What they do:**
- Call REST APIs internally
- Handle errors
- Format output (JSON)
- Return consistent data structure

**Used by:**
- Flow Architect contexts (simple-api.md, complex-api.md, etc.)
- Agent can call directly instead of raw `curl` commands

### Part 2: Skills (ACT Knowledge)

**Purpose:** Provide persistent knowledge about ACT flows

**Location:** `~/.claude/skills/flow-architect/`

**What they contain:**
- ACT TOML syntax rules
- Complete working examples
- Node types documentation
- Flow patterns (API, scheduled, integration)
- Best practices and common mistakes

**Used by:**
- Claude automatically loads relevant Skills when needed
- Provides "memory" about ACT without repeating in every context

---

## 3. Bash Tools Specification

### Overview

**Total Tools:** 6
**Location:** `flow-architect/tools/`
**Language:** Bash
**Dependencies:** `curl`, `jq`

---

### Tool 1: `get-running-services.sh`

**Purpose:** Get all running Docker services on the VPS

**Signature:**
```bash
./get-running-services.sh [category]
```

**Parameters:**
- `category` (optional): Filter by category
  - `all` (default) - Return all running services
  - `database` - Only databases (PostgreSQL, MySQL, MongoDB, etc.)
  - `web-server` - Only web servers (Nginx, Apache)
  - `queue` - Only message queues (RabbitMQ, Kafka)
  - `search` - Only search engines (Elasticsearch)

**Internal API Call:**
```bash
curl -s http://localhost:3000/api/services
```

**Output Format:**
```json
[
  {
    "id": "postgresql",
    "name": "PostgreSQL 16",
    "status": "running",
    "category": "database",
    "containerName": "ai-desktop-postgresql",
    "defaultCredentials": {
      "username": "postgres",
      "password": "changeme",
      "port": 5432
    },
    "ports": [5432],
    "dockerImage": "postgres:16",
    "icon": "/icons/services/postgresql.svg"
  }
]
```

**Error Handling:**
- If API fails: Return empty array `[]`
- If no services running: Return empty array `[]`
- If invalid category: Return empty array `[]`

**Example Usage:**
```bash
# Get all running services
./get-running-services.sh

# Get only running databases
./get-running-services.sh database

# Get only web servers
./get-running-services.sh web-server
```

**Implementation:**
```bash
#!/bin/bash
# flow-architect/tools/get-running-services.sh

CATEGORY=${1:-all}

# Call API
response=$(curl -s http://localhost:3000/api/services 2>/dev/null)

# Check if curl failed
if [ $? -ne 0 ]; then
  echo "[]"
  exit 0
fi

# Filter running services
if [ "$CATEGORY" = "all" ]; then
  echo "$response" | jq '.services // [] | map(select(.status == "running"))'
else
  echo "$response" | jq --arg cat "$CATEGORY" '.services // [] | map(select(.status == "running" and .category == $cat))'
fi
```

---

### Tool 2: `get-node-catalog.sh`

**Purpose:** Get all available node types with their operations

**Signature:**
```bash
./get-node-catalog.sh [auth_required]
```

**Parameters:**
- `auth_required` (optional): Filter by authentication requirement
  - `all` (default) - Return all nodes
  - `true` - Only nodes requiring auth (GitHub, OpenAI, Slack, etc.)
  - `false` - Only nodes NOT requiring auth (py, http, timer, etc.)

**Internal API Call:**
```bash
curl -s http://localhost:3000/api/nodes
```

**Output Format:**
```json
[
  {
    "id": "github",
    "displayName": "GitHub",
    "type": "github",
    "category": "integration",
    "requiresAuth": true,
    "operations": [
      {
        "id": "create_issue",
        "displayName": "Create Issue",
        "description": "Create a new issue in a repository",
        "authFields": ["token"]
      },
      {
        "id": "create_pr",
        "displayName": "Create Pull Request",
        "description": "Create a pull request"
      }
    ]
  }
]
```

**Error Handling:**
- If API fails: Return empty array `[]`
- If no nodes found: Return empty array `[]`

**Example Usage:**
```bash
# Get all nodes
./get-node-catalog.sh

# Get only nodes requiring auth
./get-node-catalog.sh true

# Get only nodes NOT requiring auth
./get-node-catalog.sh false
```

**Implementation:**
```bash
#!/bin/bash
# flow-architect/tools/get-node-catalog.sh

AUTH_REQUIRED=${1:-all}

response=$(curl -s http://localhost:3000/api/nodes 2>/dev/null)

if [ $? -ne 0 ]; then
  echo "[]"
  exit 0
fi

if [ "$AUTH_REQUIRED" = "all" ]; then
  echo "$response" | jq '.nodes // []'
elif [ "$AUTH_REQUIRED" = "true" ]; then
  echo "$response" | jq '.nodes // [] | map(select(.requiresAuth == true))'
else
  echo "$response" | jq '.nodes // [] | map(select(.requiresAuth == false or .requiresAuth == null))'
fi
```

---

### Tool 3: `check-service-auth.sh`

**Purpose:** Check if a service has authentication configured

**Signature:**
```bash
./check-service-auth.sh <service_id>
```

**Parameters:**
- `service_id` (required): Service ID (e.g., `postgresql`, `mysql`, `mongodb`)

**Internal API Call:**
```bash
curl -s -w "%{http_code}" http://localhost:3000/api/services/$service_id/auth
```

**Output Format:**
```json
{
  "serviceId": "postgresql",
  "configured": true,
  "statusCode": 200
}
```
OR
```json
{
  "serviceId": "postgresql",
  "configured": false,
  "statusCode": 404
}
```

**Error Handling:**
- If service ID missing: Exit with error message
- If API unreachable: Return `configured: false`

**Example Usage:**
```bash
# Check if PostgreSQL auth is configured
./check-service-auth.sh postgresql
# Returns: {"serviceId":"postgresql","configured":true,"statusCode":200}

# Check if MySQL auth is configured
./check-service-auth.sh mysql
# Returns: {"serviceId":"mysql","configured":false,"statusCode":404}
```

**Implementation:**
```bash
#!/bin/bash
# flow-architect/tools/check-service-auth.sh

SERVICE_ID=$1

if [ -z "$SERVICE_ID" ]; then
  echo '{"error":"service_id parameter is required"}' >&2
  exit 1
fi

# Call API and capture HTTP status code
http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/services/$SERVICE_ID/auth 2>/dev/null)

if [ $? -ne 0 ]; then
  echo "{\"serviceId\":\"$SERVICE_ID\",\"configured\":false,\"statusCode\":0}"
  exit 0
fi

if [ "$http_code" = "200" ]; then
  echo "{\"serviceId\":\"$SERVICE_ID\",\"configured\":true,\"statusCode\":200}"
else
  echo "{\"serviceId\":\"$SERVICE_ID\",\"configured\":false,\"statusCode\":$http_code}"
fi
```

---

### Tool 4: `check-node-auth.sh`

**Purpose:** Check if a node type has authentication configured

**Signature:**
```bash
./check-node-auth.sh <node_type>
```

**Parameters:**
- `node_type` (required): Node type (e.g., `github`, `openai`, `slack`)

**Internal API Call:**
```bash
curl -s -w "%{http_code}" http://localhost:3000/api/nodes/$node_type/auth
```

**Output Format:**
```json
{
  "nodeType": "github",
  "configured": true,
  "statusCode": 200
}
```
OR
```json
{
  "nodeType": "github",
  "configured": false,
  "statusCode": 404
}
```

**Error Handling:**
- If node type missing: Exit with error message
- If API unreachable: Return `configured: false`

**Example Usage:**
```bash
# Check if GitHub auth is configured
./check-node-auth.sh github
# Returns: {"nodeType":"github","configured":true,"statusCode":200}

# Check if OpenAI auth is configured
./check-node-auth.sh openai
# Returns: {"nodeType":"openai","configured":false,"statusCode":404}
```

**Implementation:**
```bash
#!/bin/bash
# flow-architect/tools/check-node-auth.sh

NODE_TYPE=$1

if [ -z "$NODE_TYPE" ]; then
  echo '{"error":"node_type parameter is required"}' >&2
  exit 1
fi

http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/nodes/$NODE_TYPE/auth 2>/dev/null)

if [ $? -ne 0 ]; then
  echo "{\"nodeType\":\"$NODE_TYPE\",\"configured\":false,\"statusCode\":0}"
  exit 0
fi

if [ "$http_code" = "200" ]; then
  echo "{\"nodeType\":\"$NODE_TYPE\",\"configured\":true,\"statusCode\":200}"
else
  echo "{\"nodeType\":\"$NODE_TYPE\",\"configured\":false,\"statusCode\":$http_code}"
fi
```

---

### Tool 5: `get-deployed-flows.sh`

**Purpose:** Get all deployed ACT flows with their endpoints

**Signature:**
```bash
./get-deployed-flows.sh [status]
```

**Parameters:**
- `status` (optional): Filter by status
  - `all` (default) - Return all flows
  - `running` - Only running flows
  - `stopped` - Only stopped flows
  - `available` - Only available (not deployed) flows

**Internal API Call:**
```bash
curl -s http://localhost:3000/api/catalog
```

**Output Format:**
```json
[
  {
    "id": "quotes-api",
    "name": "Quotes API",
    "type": "flow",
    "status": "running",
    "connection": {
      "string": "http://localhost:9001",
      "host": "localhost",
      "port": 9001
    },
    "capabilities": ["api-endpoint"],
    "endpoints": [
      {
        "path": "/api/quotes",
        "method": "GET",
        "description": "Get all quotes"
      },
      {
        "path": "/api/quotes",
        "method": "POST",
        "description": "Create new quote"
      }
    ]
  }
]
```

**Error Handling:**
- If API fails: Return empty array `[]`
- If no flows found: Return empty array `[]`

**Example Usage:**
```bash
# Get all flows
./get-deployed-flows.sh

# Get only running flows
./get-deployed-flows.sh running

# Get only stopped flows
./get-deployed-flows.sh stopped
```

**Implementation:**
```bash
#!/bin/bash
# flow-architect/tools/get-deployed-flows.sh

STATUS=${1:-all}

response=$(curl -s http://localhost:3000/api/catalog 2>/dev/null)

if [ $? -ne 0 ]; then
  echo "[]"
  exit 0
fi

if [ "$STATUS" = "all" ]; then
  echo "$response" | jq '.services // []'
else
  echo "$response" | jq --arg status "$STATUS" '.services // [] | map(select(.status == $status))'
fi
```

---

### Tool 6: `get-available-port.sh`

**Purpose:** Get next available port for new flow service

**Signature:**
```bash
./get-available-port.sh
```

**Parameters:** None

**Internal API Call:**
```bash
curl -s http://localhost:3000/api/ports
```

**Output Format:**
```json
{
  "success": true,
  "available_port": 9004,
  "used_ports": [9001, 9002, 9003]
}
```

**Error Handling:**
- If API fails: Return default port 9001
- If response invalid: Return default port 9001

**Example Usage:**
```bash
# Get next available port
./get-available-port.sh
# Returns: {"success":true,"available_port":9004,"used_ports":[9001,9002,9003]}
```

**Implementation:**
```bash
#!/bin/bash
# flow-architect/tools/get-available-port.sh

response=$(curl -s http://localhost:3000/api/ports 2>/dev/null)

if [ $? -ne 0 ]; then
  echo '{"success":false,"available_port":9001,"used_ports":[]}'
  exit 0
fi

echo "$response"
```

---

## 4. Skills Specification

### Overview

**Total Skills:** 4
**Location:** `~/.claude/skills/flow-architect/`
**Format:** Markdown with YAML frontmatter

---

### Skill 1: `act-syntax`

**File:** `~/.claude/skills/flow-architect/act-syntax/SKILL.md`

**Purpose:** Complete ACT TOML syntax reference

**Contents:**

```yaml
---
name: act-syntax
description: Complete ACT flow TOML syntax and formatting rules
version: 1.0.0
category: flow-architect
---

# ACT Flow Syntax

## File Structure

Every ACT flow follows this structure:

```toml
[workflow]
name = Flow Name
description = What this flow does
start_node = FirstNode

[parameters]
connection_string = postgresql://user:pass@localhost:5432/db
api_key = {{ENV.API_KEY}}

[node:NodeName]
type = node_type
label = Human readable label
operation = operation_name
# ... node-specific parameters

[edges]
Node1 = Node2
Node2 = Node3

[env]

[settings]
debug_mode = true
max_retries = 3
timeout_seconds = 600

[configuration]
agent_enabled = true
agent_name = flow-name-agent
host = 0.0.0.0
port = 9001
debug = true

[deployment]
environment = development
```

## Critical Rules

### 1. NO QUOTES (except in arrays and strings with special chars)

❌ WRONG:
```toml
type = "neon"
label = "Create table"
operation = "execute_query"
```

✅ CORRECT:
```toml
type = neon
label = Create table
operation = execute_query
```

### 2. String arrays USE quotes

✅ CORRECT:
```toml
methods = ["GET", "POST"]
parameters = ["{{request_data.name}}", "{{request_data.email}}"]
```

### 3. Parameter references USE double curly braces

✅ CORRECT:
```toml
connection_string = {{.Parameter.connection_string}}
api_key = {{.Parameter.api_key}}
user_input = {{request_data.username}}
previous_node_result = {{PreviousNode.result.data}}
```

### 4. Node names: No spaces, PascalCase

❌ WRONG:
```toml
[node:create table]
[node:fetch-data]
```

✅ CORRECT:
```toml
[node:CreateTable]
[node:FetchData]
```

### 5. Labels: Use hierarchical format for APIs

✅ CORRECT for APIs:
```toml
label = API.Quotes.1. GET /api/quotes
label = API.Quotes.2. POST /api/quotes
label = API.Quotes.2.1. Insert Quote
```

✅ CORRECT for other flows:
```toml
label = 1. Fetch ISS location
label = 2. Store in database
```

## Node Types Quick Reference

- `py` - Python code execution
- `neon` / `pg` - PostgreSQL operations
- `mysql` - MySQL operations
- `mongo` - MongoDB operations
- `http` / `axios` - HTTP requests
- `aci` - API creation (routes)
- `timer` / `cron` - Scheduled execution
- `sendgrid` / `smtp` - Email sending
- `github` - GitHub operations
- `openai` - OpenAI API
- `slack` - Slack integration

Use `get-node-catalog.sh` to see all 129 available nodes.

## Common Patterns

### Pattern 1: Database Table Creation
```toml
[node:CreateTable]
type = neon
label = 1. Create table
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = CREATE TABLE IF NOT EXISTS items (id SERIAL PRIMARY KEY, name TEXT)
```

### Pattern 2: API Endpoint
```toml
[node:DefineGetRoute]
type = aci
mode = server
label = API.Items.1. GET /api/items
operation = add_route
route_path = /api/items
methods = ["GET"]
handler = FetchItems
description = Get all items

[node:FetchItems]
type = neon
label = API.Items.1.1. Fetch Items
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = SELECT * FROM items
parameters = []
```

### Pattern 3: HTTP Request
```toml
[node:FetchAPI]
type = http
label = Fetch external API
url = https://api.example.com/data
method = GET
headers = {"Authorization": "Bearer {{.Parameter.api_key}}"}
```

### Pattern 4: Timer/Scheduled Task
```toml
[node:ScheduledTask]
type = timer
label = Run every hour
schedule = 0 * * * *
trigger_node = DoSomething
```
```

---

### Skill 2: `act-examples`

**File:** `~/.claude/skills/flow-architect/act-examples/SKILL.md`

**Purpose:** Complete working ACT flow examples

**Contents:**

```yaml
---
name: act-examples
description: Complete working examples of ACT flows for different use cases
version: 1.0.0
category: flow-architect
---

# ACT Flow Examples

## Example 1: Simple API (Quotes API)

**Use case:** 2-5 endpoints, single database table, basic CRUD

**File:** See `flow-architect/.claude/instructions/examples/quotes-api.flow`

**Key features:**
- PostgreSQL database
- 2 endpoints (GET + POST)
- API server on port 9001
- Service catalog registration

## Example 2: Complex API (Todo API)

**Use case:** 6-15 endpoints, 2-3 tables, full CRUD

**File:** See `flow-architect/.claude/instructions/examples/todo-api.flow`

**Key features:**
- Multiple tables (tasks, categories)
- 7 endpoints
- Foreign keys and relationships
- Full CRUD operations

## Example 3: Full Application (Restaurant System)

**Use case:** 15-40+ endpoints, 5+ tables, complex relationships

**File:** See `flow-architect/.claude/instructions/examples/restaurant-system.flow`

**Key features:**
- 6 tables (orders, menu, customers, reservations, tables, order_items)
- 25+ endpoints
- Many-to-many relationships
- Business logic

## Example 4: Scheduled Task (ISS Tracker)

**Use case:** Recurring background task with database storage

**File:** See `flow-architect/.claude/instructions/examples/scheduled-iss-tracker.flow`

**Key features:**
- Timer node (every 5 minutes)
- HTTP request to external API
- Database storage
- No API endpoints (background only)

## Example 5: Multi-Service Integration (Price Monitor)

**Use case:** Multiple external APIs, monitoring, alerts

**File:** See `flow-architect/.claude/instructions/examples/price-monitor.flow`

**Key features:**
- HTTP requests to multiple APIs
- Python processing
- Database comparison
- Email alerts on changes
- Timer for periodic checks

## Quick Start Templates

### Template: Simple Calculation
```toml
[workflow]
name = Simple Calculation
description = Calculate something
start_node = Calculate

[node:Calculate]
type = py
label = Calculate result
code = """
def calculate(**kwargs):
    result = 47 + 89
    return {"result": result}
"""
function = calculate

[edges]

[env]

[settings]
debug_mode = true

[deployment]
environment = development
```

### Template: One-Time API Fetch
```toml
[workflow]
name = Fetch Data
description = Fetch data from external API
start_node = FetchAPI

[node:FetchAPI]
type = http
label = Fetch ISS location
url = http://api.open-notify.org/iss-now.json
method = GET

[edges]

[env]

[settings]
debug_mode = true

[deployment]
environment = development
```
```

---

### Skill 3: `flow-patterns`

**File:** `~/.claude/skills/flow-architect/flow-patterns/SKILL.md`

**Purpose:** Common flow patterns and architecture

**Contents:**

```yaml
---
name: flow-patterns
description: Common flow architecture patterns and when to use them
version: 1.0.0
category: flow-architect
---

# Flow Architecture Patterns

## Pattern 1: Simple API

**When to use:**
- User wants 2-5 endpoints
- Single entity or simple use case
- Basic CRUD operations
- 1-2 database tables

**Structure:**
```
Database Setup → API Routes → Handlers → Server Config
```

**Example:**
- Quotes API (GET + POST quotes)
- Notes API (store/retrieve notes)
- Bookmarks API (save/list bookmarks)

**Template:**
1. Create table node (neon)
2. Define GET route (aci)
3. Define POST route (aci)
4. Fetch handler (neon)
5. Insert handler (neon)
6. Server configuration

## Pattern 2: Complex API

**When to use:**
- User wants 6-15 endpoints
- 2-4 related entities
- Full CRUD on multiple tables
- Foreign key relationships

**Structure:**
```
Multiple Tables → Multiple Route Groups → Full CRUD Handlers → Server Config
```

**Example:**
- Todo API (tasks + categories)
- Blog API (posts + comments + categories)
- Library API (books + authors + loans)

**Template:**
1. Create multiple tables (sequential)
2. Define routes for each entity
3. Create handlers for each operation
4. Connect with foreign keys

## Pattern 3: Full Application

**When to use:**
- User wants 15-40+ endpoints
- 5+ database tables
- Complex business logic
- Many-to-many relationships

**Structure:**
```
Schema Design → Table Creation → Entity Routes → Business Logic → Server Config
```

**Example:**
- Restaurant management (orders, menu, customers, reservations)
- E-commerce (products, orders, inventory, payments)
- School system (students, teachers, courses, grades)

## Pattern 4: Scheduled Task

**When to use:**
- User wants recurring execution
- "Every X minutes/hours/days"
- Background data collection
- Monitoring tasks

**Structure:**
```
Timer Node → Task Logic → Database Storage (optional) → No API Server
```

**Example:**
- Fetch Bitcoin price every hour
- Check ISS location every 5 minutes
- Send daily report at 8am

**Template:**
1. Timer node with cron schedule
2. HTTP fetch or Python logic
3. Optional database storage
4. No [configuration] section needed (unless exposing API)

## Pattern 5: Multi-Service Integration

**When to use:**
- Multiple external APIs
- Data aggregation
- Monitoring + alerting
- ETL pipelines

**Structure:**
```
Timer → [Fetch API1, Fetch API2, Fetch API3] → Combine → Process → Alert/Store
```

**Example:**
- Monitor competitor prices → email on change
- Fetch weather + ISS location → combine → store
- Scrape news → analyze → send summary

**Template:**
1. Timer for recurring check
2. Multiple HTTP nodes (parallel)
3. Python node for processing
4. Database storage
5. Email/webhook for alerts

## Decision Tree

```
Does user want API endpoints?
├─ YES → Is it 2-5 endpoints?
│   ├─ YES → Simple API Pattern
│   └─ NO → Is it 6-15 endpoints?
│       ├─ YES → Complex API Pattern
│       └─ NO → Full Application Pattern
│
└─ NO → Does it run on schedule?
    ├─ YES → Scheduled Task Pattern
    └─ NO → Does it integrate multiple services?
        ├─ YES → Multi-Service Integration Pattern
        └─ NO → Simple Calculation/Fetch Pattern
```
```

---

### Skill 4: `security-awareness`

**File:** `~/.claude/skills/flow-architect/security-awareness/SKILL.md`

**Purpose:** Security Center awareness and authentication guidance

**Contents:**

```yaml
---
name: security-awareness
description: Security Center and authentication management for Flow Architect
version: 1.0.0
category: flow-architect
---

# Security Center Awareness

## What is Security Center?

Security Center is a desktop app that manages authentication for:
1. **Infrastructure Services** (PostgreSQL, MySQL, MongoDB, etc.)
2. **API Nodes** (GitHub, OpenAI, Slack, SendGrid, etc.)

Location: Dock → Shield icon

## When to Check Authentication

**BEFORE building ANY flow that uses:**

### 1. Database Services
- PostgreSQL (`neon` / `pg` node)
- MySQL (`mysql` node)
- MongoDB (`mongo` node)
- Any service from `get-running-services.sh`

**Check with:**
```bash
./flow-architect/tools/check-service-auth.sh postgresql
```

**Response:**
```json
{"serviceId":"postgresql","configured":true,"statusCode":200}
```

If `configured: false`, tell user:
```
⚠️ PostgreSQL requires authentication.
Please open Security Center from the dock to configure credentials first.
```

### 2. API Nodes
- GitHub (`github` node)
- OpenAI (`openai` node)
- Slack (`slack` node)
- SendGrid (`sendgrid` node)
- Stripe (`stripe` node)
- Any node with `requiresAuth: true` from `get-node-catalog.sh true`

**Check with:**
```bash
./flow-architect/tools/check-node-auth.sh github
```

**Response:**
```json
{"nodeType":"github","configured":true,"statusCode":200}
```

If `configured: false`, tell user:
```
⚠️ GitHub node requires authentication.
Please open Security Center to configure your GitHub token.
```

## Authentication Check Workflow

```
User requests flow
  ↓
Identify services/nodes needed
  ↓
For each service:
  └─ ./check-service-auth.sh <service_id>
      ├─ 200 → ✅ Proceed
      └─ 404 → ❌ Direct to Security Center
  ↓
For each auth-required node:
  └─ ./check-node-auth.sh <node_type>
      ├─ 200 → ✅ Proceed
      └─ 404 → ❌ Direct to Security Center
  ↓
If all auth OK:
  └─ Build flow
Else:
  └─ Stop and inform user
```

## Connection Strings

**DON'T hardcode:**
```toml
❌ connection_string = postgresql://postgres:hardcoded@localhost:5432/db
```

**DO use parameters:**
```toml
✅ connection_string = {{.Parameter.connection_string}}
```

The actual credentials come from Security Center's encrypted storage.

## Service Manager vs Security Center

**Service Manager** (Package icon in dock):
- Install/uninstall services
- Start/stop services
- View service status

**Security Center** (Shield icon in dock):
- Configure authentication
- Store credentials (encrypted)
- Manage API tokens

## Common Scenarios

### Scenario 1: User wants PostgreSQL API but PostgreSQL not running
```bash
services=$(./get-running-services.sh database)
if [ "$(echo $services | jq '. | length')" -eq 0 ]; then
  echo "No database service is running."
  echo "Please use Service Manager to install and start PostgreSQL."
  exit 1
fi
```

### Scenario 2: PostgreSQL running but no auth configured
```bash
auth_status=$(./check-service-auth.sh postgresql)
configured=$(echo $auth_status | jq -r '.configured')
if [ "$configured" = "false" ]; then
  echo "PostgreSQL is running but authentication is not configured."
  echo "Please open Security Center to configure credentials."
  exit 1
fi
```

### Scenario 3: User wants GitHub integration but no token
```bash
auth_status=$(./check-node-auth.sh github)
configured=$(echo $auth_status | jq -r '.configured')
if [ "$configured" = "false" ]; then
  echo "GitHub node requires authentication."
  echo "Please open Security Center to configure your GitHub token."
  exit 1
fi
```
```

---

## 5. Context Files Update Plan

### Files to Update

**Total:** 6 context files
**Location:** `flow-architect/.claude/instructions/contexts/`

1. `simple-api.md`
2. `complex-api.md`
3. `full-application.md`
4. `multi-service-integration.md`
5. `scheduled-task.md`
6. Main agent: `flow-architect/.claude/agents/flow-architect.md`

---

### Update Pattern (Same for all 6 files)

#### Change 1: Replace API Discovery Section

**BEFORE:**
```markdown
### Step 1: Check Available Services

```bash
# Check for running database services
curl -s http://localhost:3000/api/catalog?type=infrastructure&category=database&status=running

# Get PostgreSQL connection if available
curl -s http://localhost:3000/api/catalog | \
  jq '.services[] | select(.id == "postgresql" and .status == "running") | .connection'
```
```

**AFTER:**
```markdown
### Step 1: Check Available Services

Use the bash tool:

```bash
# Check for running database services
./flow-architect/tools/get-running-services.sh database

# Get all running services
./flow-architect/tools/get-running-services.sh
```

Response format:
```json
[
  {
    "id": "postgresql",
    "name": "PostgreSQL 16",
    "status": "running",
    "category": "database",
    "defaultCredentials": {
      "username": "postgres",
      "password": "changeme",
      "port": 5432
    },
    "ports": [5432]
  }
]
```

Build connection string from response:
```
postgresql://{username}:{password}@localhost:{port}/database
```
```

#### Change 2: Add Authentication Verification

**ADD THIS SECTION (after Step 1):**

```markdown
### Step 1.5: Verify Authentication

Before proceeding, verify authentication for all services:

```bash
# Check PostgreSQL auth
./flow-architect/tools/check-service-auth.sh postgresql
```

If response shows `"configured": false`:
```
⚠️ PostgreSQL requires authentication.
Please open Security Center from the dock to configure credentials.
```

**DO NOT proceed** until authentication is configured.
```

#### Change 3: Update Node Discovery

**BEFORE:**
```markdown
cat catalogs/node-catalog.json
```

**AFTER:**
```markdown
Use the bash tool:

```bash
# Get all nodes
./flow-architect/tools/get-node-catalog.sh

# Get only auth-required nodes
./flow-architect/tools/get-node-catalog.sh true

# Get only non-auth nodes
./flow-architect/tools/get-node-catalog.sh false
```

For auth-required nodes, verify authentication:
```bash
./flow-architect/tools/check-node-auth.sh github
```
```

#### Change 4: Update Port Discovery

**BEFORE:**
```markdown
grep "^port = " flows/*.flow | sort -t= -k2 -n | tail -1
```

**AFTER:**
```markdown
Use the bash tool:

```bash
./flow-architect/tools/get-available-port.sh
```

Response:
```json
{"success":true,"available_port":9004,"used_ports":[9001,9002,9003]}
```

Use the `available_port` value in your flow configuration.
```

#### Change 5: Update Flow Discovery (for multi-service-integration.md)

**BEFORE:**
```markdown
curl -s http://localhost:3000/api/catalog/flows
```

**AFTER:**
```markdown
Use the bash tool:

```bash
# Get all deployed flows
./flow-architect/tools/get-deployed-flows.sh

# Get only running flows
./flow-architect/tools/get-deployed-flows.sh running
```

Response includes endpoints for each flow, allowing you to reference them in new flows.
```

---

## 6. Complete Workflow Examples

### Example 1: User Asks "Create quotes API"

**Step-by-step flow:**

```bash
# 1. Flow Architect classifies query
Classification: Simple API (2-5 endpoints)
Context loaded: simple-api.md

# 2. Check running services
./flow-architect/tools/get-running-services.sh database
# Returns: [{"id":"postgresql","status":"running","defaultCredentials":{...}}]
# Result: ✅ PostgreSQL is running

# 3. Check authentication
./flow-architect/tools/check-service-auth.sh postgresql
# Returns: {"configured":true,"statusCode":200}
# Result: ✅ Auth configured

# 4. Get available port
./flow-architect/tools/get-available-port.sh
# Returns: {"available_port":9001}
# Result: ✅ Use port 9001

# 5. Build connection string
connection_string = postgresql://postgres:changeme@localhost:5432/neondb

# 6. Create flow file
File: flow-architect/flows/quotes-api.flow
Content: (see example in act-examples Skill)

# 7. Save flow
Saved to: ../components/apps/act-docker/flows/quotes-api.flow

# 8. Respond to user
"✓ Quotes API created at ../components/apps/act-docker/flows/quotes-api.flow

Endpoints:
• POST /api/quotes - Create quote
• GET /api/quotes - Get all quotes

To deploy: Use Flow Manager UI to start the service
Port: 9001
Database: PostgreSQL (table created on first run)"
```

---

### Example 2: User Asks "Create GitHub issue tracker API" (auth required)

**Step-by-step flow:**

```bash
# 1. Classify
Classification: Simple API + GitHub integration
Context loaded: simple-api.md

# 2. Check PostgreSQL
./flow-architect/tools/get-running-services.sh database
# Returns: [{"id":"postgresql",...}]
# Result: ✅ PostgreSQL running

# 3. Check PostgreSQL auth
./flow-architect/tools/check-service-auth.sh postgresql
# Returns: {"configured":true}
# Result: ✅ Auth OK

# 4. Check GitHub node availability
./flow-architect/tools/get-node-catalog.sh true
# Returns: [..., {"id":"github","requiresAuth":true}]
# Result: ✅ GitHub node exists

# 5. Check GitHub auth
./flow-architect/tools/check-node-auth.sh github
# Returns: {"configured":false,"statusCode":404}
# Result: ❌ GitHub auth NOT configured

# 6. Stop and inform user
Response:
"⚠️ GitHub node requires authentication.

Before I can create this flow, you need to configure your GitHub token.

Please:
1. Open Security Center from the dock (Shield icon)
2. Navigate to Nodes Authentication
3. Configure GitHub authentication with your GitHub token

Once configured, I can proceed with creating the flow."

# Flow creation STOPPED until auth is ready
```

---

### Example 3: User Asks "Monitor Bitcoin price every hour"

**Step-by-step flow:**

```bash
# 1. Classify
Classification: Scheduled Task
Context loaded: scheduled-task.md

# 2. Check if database needed (user wants to store data)
./flow-architect/tools/get-running-services.sh database
# Returns: []
# Result: ❌ No database running

# 3. Inform user
Response:
"To store Bitcoin price history, you'll need a database.

Please:
1. Open Service Manager from the dock
2. Install and start PostgreSQL
3. Open Security Center to configure authentication

Alternatively, I can create a simpler version that just fetches the price without storing it."

# Wait for user decision
```

---

## 7. Implementation Steps

### Phase 1: Create Bash Tools

**Step 1:** Create tools directory
```bash
mkdir -p flow-architect/tools
```

**Step 2:** Create 6 tool scripts
```bash
# Create each script
touch flow-architect/tools/get-running-services.sh
touch flow-architect/tools/get-node-catalog.sh
touch flow-architect/tools/check-service-auth.sh
touch flow-architect/tools/check-node-auth.sh
touch flow-architect/tools/get-deployed-flows.sh
touch flow-architect/tools/get-available-port.sh

# Make executable
chmod +x flow-architect/tools/*.sh
```

**Step 3:** Implement each script (use specifications from section 3)

**Step 4:** Test each tool independently
```bash
# Test get-running-services.sh
./flow-architect/tools/get-running-services.sh
./flow-architect/tools/get-running-services.sh database

# Test check-service-auth.sh
./flow-architect/tools/check-service-auth.sh postgresql

# Test get-node-catalog.sh
./flow-architect/tools/get-node-catalog.sh
./flow-architect/tools/get-node-catalog.sh true

# etc.
```

---

### Phase 2: Create Skills

**Step 1:** Create Skills directory
```bash
mkdir -p ~/.claude/skills/flow-architect/act-syntax
mkdir -p ~/.claude/skills/flow-architect/act-examples
mkdir -p ~/.claude/skills/flow-architect/flow-patterns
mkdir -p ~/.claude/skills/flow-architect/security-awareness
```

**Step 2:** Create SKILL.md files
```bash
# Create each Skill file with content from section 4
cat > ~/.claude/skills/flow-architect/act-syntax/SKILL.md << 'EOF'
(content from section 4)
EOF

# Repeat for other 3 Skills
```

**Step 3:** Verify Skills are loadable
```bash
# Skills should be automatically discovered by Claude
# Check that ~/.claude/skills/flow-architect/ exists
ls -la ~/.claude/skills/flow-architect/
```

---

### Phase 3: Update Context Files

**Step 1:** Update simple-api.md
- Replace API calls with tool calls
- Add authentication verification
- Update examples

**Step 2:** Update complex-api.md
- Same changes as simple-api.md
- Adjust for multiple entities

**Step 3:** Update full-application.md
- Same changes
- Adjust for larger scope

**Step 4:** Update multi-service-integration.md
- Add flow discovery tool usage
- Add multiple auth checks

**Step 5:** Update scheduled-task.md
- Conditional database check
- Optional auth verification

**Step 6:** Update main agent file (flow-architect.md)
- Update discovery section
- Reference new tools
- Update examples

---

### Phase 4: Testing

**Test 1:** Service Discovery
```bash
# Ensure all tools work
./flow-architect/tools/get-running-services.sh
./flow-architect/tools/get-node-catalog.sh
./flow-architect/tools/get-deployed-flows.sh
./flow-architect/tools/get-available-port.sh
```

**Test 2:** Authentication Checks
```bash
# Test with configured service
./flow-architect/tools/check-service-auth.sh postgresql

# Test with unconfigured service
./flow-architect/tools/check-service-auth.sh mysql
```

**Test 3:** Flow Creation
- Ask Flow Architect to create simple API
- Verify it uses tools instead of curl
- Verify it checks authentication
- Verify it gets correct port

**Test 4:** Error Handling
- Stop all services, try to create API
- Remove auth, try to create flow with auth-required node
- Verify proper error messages

---

## 8. Testing Strategy

### Unit Tests (Tools)

**Test each tool independently:**

| Tool | Test Case | Expected Result |
|------|-----------|-----------------|
| get-running-services.sh | No services running | `[]` |
| get-running-services.sh | PostgreSQL running | Array with PostgreSQL object |
| get-running-services.sh database | Filter works | Only databases |
| check-service-auth.sh postgresql | Auth configured | `{"configured":true,"statusCode":200}` |
| check-service-auth.sh postgresql | No auth | `{"configured":false,"statusCode":404}` |
| check-node-auth.sh github | Auth configured | `{"configured":true,"statusCode":200}` |
| get-node-catalog.sh | All nodes | Array of 129 nodes |
| get-node-catalog.sh true | Auth-required only | Filtered array |
| get-deployed-flows.sh | No flows | `[]` |
| get-deployed-flows.sh running | Running flows only | Filtered array |
| get-available-port.sh | First flow | `{"available_port":9001}` |

---

### Integration Tests (Complete Workflows)

**Test 1: Simple API Creation (Happy Path)**
```
User: "Create quotes API"
Expected:
✅ Checks running services
✅ Finds PostgreSQL
✅ Checks PostgreSQL auth (200)
✅ Gets available port (9001)
✅ Creates flow file
✅ Responds with deployment instructions
```

**Test 2: Auth Missing (Unhappy Path)**
```
User: "Create quotes API"
Scenario: PostgreSQL running, auth NOT configured
Expected:
✅ Checks running services
✅ Finds PostgreSQL
✅ Checks PostgreSQL auth (404)
❌ Stops and directs to Security Center
```

**Test 3: Service Not Running (Unhappy Path)**
```
User: "Create quotes API"
Scenario: No database running
Expected:
✅ Checks running services
✅ Finds no database
❌ Stops and directs to Service Manager
```

**Test 4: GitHub Integration (Auth Required)**
```
User: "Create GitHub issue tracker"
Scenario: GitHub auth configured
Expected:
✅ Checks PostgreSQL (running + auth OK)
✅ Checks GitHub node (exists)
✅ Checks GitHub auth (200)
✅ Creates flow with GitHub node
```

**Test 5: Scheduled Task (No Auth Required)**
```
User: "Fetch Bitcoin price every hour"
Scenario: No database, just HTTP fetch
Expected:
✅ No auth checks needed (HTTP node doesn't require auth)
✅ Creates flow with timer + HTTP node
✅ No database setup
```

---

## 9. Success Criteria

### ✅ Tools Work Correctly

- [ ] All 6 tools executable
- [ ] All tools return valid JSON
- [ ] All tools handle errors gracefully
- [ ] All tools work with API endpoints

### ✅ Skills Load Properly

- [ ] All 4 Skills in `~/.claude/skills/flow-architect/`
- [ ] YAML frontmatter valid
- [ ] Content comprehensive
- [ ] Claude can reference Skills

### ✅ Contexts Updated

- [ ] All 6 context files updated
- [ ] No more wrong API endpoints
- [ ] All use bash tools instead of curl
- [ ] Auth checks added
- [ ] Examples updated

### ✅ Flow Architect Awareness

- [ ] Agent knows running services
- [ ] Agent knows available services
- [ ] Agent knows all node types
- [ ] Agent checks authentication before building
- [ ] Agent knows deployed flows
- [ ] Agent gets correct ports
- [ ] Agent directs to Security Center when needed
- [ ] Agent directs to Service Manager when needed

### ✅ No Hardcoding

- [ ] No hardcoded connection strings
- [ ] No hardcoded ports
- [ ] No hardcoded service lists
- [ ] Everything discovered dynamically

---

## 📋 Final Checklist

Before marking this complete:

### Research & Planning ✅
- [x] Understand current problems
- [x] Research Anthropic Skills
- [x] Map all APIs
- [x] Design architecture
- [x] Create comprehensive plan

### Implementation ⏳
- [ ] Create 6 bash tools
- [ ] Test each tool independently
- [ ] Create 4 Skills
- [ ] Verify Skills load
- [ ] Update 6 context files
- [ ] Test contexts use tools correctly

### Validation ⏳
- [ ] Unit test all tools
- [ ] Integration test workflows
- [ ] Test auth scenarios
- [ ] Test error handling
- [ ] Verify no hardcoding

### Documentation ⏳
- [ ] Tools documented
- [ ] Skills documented
- [ ] Update README if needed
- [ ] Add usage examples

---

## 🎯 Expected Outcome

After implementation, Flow Architect will be fully aware of the VPS environment:

**Before (Current State):**
```bash
# Context file hardcodes:
curl -s http://localhost:3000/api/catalog?type=infrastructure
# ❌ Wrong endpoint
# ❌ No auth check
# ❌ Hardcoded connection strings
```

**After (Desired State):**
```bash
# Context file uses tools:
./flow-architect/tools/get-running-services.sh database
./flow-architect/tools/check-service-auth.sh postgresql
# ✅ Correct endpoints
# ✅ Auth verification
# ✅ Dynamic discovery
```

**Agent becomes:**
- 🧠 Environment-aware (knows what's running)
- 🔒 Security-aware (checks auth before building)
- 📚 Knowledge-rich (Skills provide ACT expertise)
- 🛠️ Tool-equipped (uses bash tools instead of raw commands)
- 🚀 Production-ready (proper error handling and user guidance)

---

**END OF COMPREHENSIVE PLAN**

**Status:** Ready for Review
**Next Step:** Await approval to begin implementation
