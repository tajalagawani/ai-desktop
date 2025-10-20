# Scheduled Task Context

## When to Load This

**Query Patterns:**
- "run [task] every [interval]"
- "schedule [action] to happen [frequency]"
- "[do something] every hour/day/week"
- "check [resource] periodically"
- "automated [task]"

**User Intent:**
- Recurring execution
- Time-based triggers
- Automated monitoring
- Data collection over time
- Background processes

## Complexity Level: MEDIUM

**Flow Requirements:**
- Timer node (cron schedule)
- Task logic nodes (Python, HTTP, etc.)
- Usually: Database (store results)
- Minimal server (no API endpoints unless requested)
- Permanent .flow file
- Service catalog registration

---

## Example Patterns

✅ **Matches:**
- "generate random number every hour"
- "check ISS location every 5 minutes and store it"
- "fetch Bitcoin price daily"
- "send me weather report every morning at 8am"
- "backup database every night at midnight"

❌ **Does NOT Match:**
- "what's the ISS location?" → data-fetch-once.md (one-time fetch)
- "create API to get weather" → simple-api.md (needs HTTP endpoints)
- "track prices and alert on changes" → multi-service-integration.md (complex logic)

---

## Build Process (11 Steps)

### Step 1: Extract Schedule Requirements

**Parse the query to determine:**
- **Interval:** Every hour, daily, weekly, etc.
- **Specific time:** 8am, midnight, etc.
- **Timezone:** UTC, user's local time

**Common patterns:**
- "every hour" → `0 * * * *`
- "every 5 minutes" → `*/5 * * * *`
- "daily at 8am" → `0 8 * * *`
- "every Monday at 9am" → `0 9 * * 1`
- "first day of month" → `0 0 1 * *`

### Step 2: Check Live Services

**API Calls to make:**
```bash
# Get running infrastructure (databases if needed)
curl -s http://localhost:3000/api/catalog?type=infrastructure&status=running

# Check node types (static file is OK for this)
cat catalogs/node-catalog.json
```

**Use actual connection strings from running services!**

### Step 3: Design the Task Flow

**Determine what the task does:**
1. **Data collection** → HTTP request + database storage
2. **Computation** → Python logic + database storage
3. **Notification** → Logic + email/webhook
4. **Monitoring** → HTTP + comparison + alert

**Most scheduled tasks have this pattern:**
```
Timer → [Task Logic] → [Store Result] → [Optional: Notify/Log]
```

### Step 4: Find Next Available Port

Even if no API endpoints, scheduled services need server config.

**CRITICAL:** You MUST call the port detection API to get an available port.

**API Call:**
```bash
curl -s http://localhost:3000/api/ports
```

**Parse the JSON response and use `available_port`** - this prevents port conflicts

### Step 5: Create Workflow Header

**CRITICAL:** Follow exact TOML format - no quotes, no [server], no [service_catalog]

```toml
[workflow]
name = [Task] Scheduler
description = [What it does] on schedule
start_node = CreateDataTable

[parameters]
connection_string = postgresql://neondb_owner:password@host:5432/db?sslmode=require
```

**That's it for the header!** Footer sections come at the end.

### Step 6: Create Database Table (If Storing Results)

**CRITICAL:** No quotes on type/label/operation. Use {{.Parameter.connection_string}}

```toml
[node:CreateDataTable]
type = neon
label = 1. Create [table] table
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = CREATE TABLE IF NOT EXISTS [table_name] (id SERIAL PRIMARY KEY, [data_fields], created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

### Step 7: Create Timer Node

**CRITICAL:** No quotes on type/mode/handler. Timer uses `handler` parameter, not edges!

```toml
[node:ScheduleTask]
type = timer
label = 2. Trigger every [interval]
schedule = [CRON_EXPRESSION]
mode = cron
timezone = UTC
handler = [NextNodeName]
```

### Step 8: Create Task Logic Nodes

**CRITICAL:** No quotes on type/method/function

**Example: Data fetching**
```toml
[node:FetchData]
type = request
label = 3. Fetch [resource]
method = GET
url = [API_URL]
timeout_seconds = 10
retry_on_failure = true
```

**Example: Computation**
```toml
[node:ProcessData]
type = py
label = 4. Process data
code = """
def process(**kwargs):
    # Your logic here
    result = compute_something()
    return {"result": result}
"""
function = process
```

### Step 9: Store Results (If Applicable)

**CRITICAL:** No quotes on type/operation. Use {{.Parameter.connection_string}}

```toml
[node:StoreResult]
type = neon
label = 5. Store in database
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = INSERT INTO [table] ([fields]) VALUES (%s, %s) RETURNING id
parameters = [{{PreviousNode.result.field1}}, {{PreviousNode.result.field2}}]
```

### Step 10: Define Edges

```toml
[edges]
CreateDataTable = ScheduleTask  # Connect table creation to timer
ScheduleTask = []  # Timer handles its own routing via 'handler' parameter!
FetchData = ProcessData  # Task flow
ProcessData = StoreResult  # Store result
StoreResult = LogSuccess  # Optional logging
```

**CRITICAL PATTERN:**
- Table creation connects to timer (initialization)
- Timer has `handler` parameter pointing to first task node
- Timer edge is `= []` (empty, timer handles routing internally)
- Task nodes connect sequentially

### Step 11: Add Footer Sections

**CRITICAL:** Must be in this EXACT order at the end:

```toml
[env]

[settings]
debug_mode = true
max_retries = 3
timeout_seconds = 600

[configuration]
agent_enabled = true
agent_name = [task]-scheduler-agent
agent_version = 1.0.0
host = 0.0.0.0
port = [PORT]
debug = true
cors_enabled = true

[deployment]
environment = development
```

---

## Cron Expression Quick Reference

**Format:** `minute hour day month weekday`

**Common patterns:**
```
*/5 * * * *    # Every 5 minutes
0 * * * *      # Every hour (on the hour)
0 */2 * * *    # Every 2 hours
0 0 * * *      # Every day at midnight
0 8 * * *      # Every day at 8am
0 9 * * 1      # Every Monday at 9am
0 0 1 * *      # First day of every month
0 0 * * 0      # Every Sunday at midnight
```

**Interactive generator:** https://crontab.guru/

---

## Load Example Files

**Reference Files:**
- `.claude/instructions/examples/scheduled-random.flow` - Simple scheduled task
- `.claude/instructions/examples/scheduled-iss-tracker.flow` - Complex (HTTP + DB + API)

---

## Node Types Needed

**Read these:**
- `.claude/instructions/node-types/timer.md` - Scheduled triggers
- `.claude/instructions/node-types/python.md` - Task logic
- `.claude/instructions/node-types/http-request.md` - Data fetching
- `.claude/instructions/node-types/neon.md` - Data storage
- `.claude/instructions/node-types/email.md` - Notifications (if needed)

---

## Common Patterns

### Pattern 1: Simple Scheduled Computation

**User:** "generate random number every hour and store it"

**Flow Structure:**
```
CreateTable → Timer (hourly)
              ↓ (via handler)
           Generate → Store → Log
```

**Code:**
```toml
[node:ScheduleGeneration]
type = timer
schedule = 0 * * * *
handler = GenerateNumber

[node:GenerateNumber]
type = py
code = """
import random
def generate(**kwargs):
    number = random.randint(1, 100)
    return {"result": {"value": number}}
"""
function = generate

[node:StoreNumber]
type = neon
query = INSERT INTO numbers (value) VALUES (%s)
parameters = [{{GenerateNumber.result.value}}]

[edges]
CreateTable = ScheduleGeneration
ScheduleGeneration = []  # Timer handles routing
GenerateNumber = StoreNumber
```

---

### Pattern 2: Scheduled Data Collection

**User:** "check ISS location every 5 minutes and save it"

**Flow Structure:**
```
CreateTable → Timer (5 min)
              ↓ (via handler)
           Fetch → Parse → Store → Log
```

**Code:**
```toml
[node:ScheduleTracking]
type = timer
schedule = */5 * * * *
handler = FetchLocation

[node:FetchLocation]
type = request
url = http://api.open-notify.org/iss-now.json

[node:ParseData]
type = py
code = """..."""

[node:StoreLocation]
type = neon
query = INSERT INTO iss_tracking (lat, lon) VALUES (%s, %s)

[edges]
CreateTable = ScheduleTracking
ScheduleTracking = []
FetchLocation = ParseData
ParseData = StoreLocation
```

---

### Pattern 3: Daily Report/Summary

**User:** "send me Bitcoin price every day at 8am"

**Flow Structure:**
```
CreateTable → Timer (daily 8am)
              ↓ (via handler)
           Fetch → Parse → Store → Email
```

**Code:**
```toml
[node:DailySchedule]
type = timer
schedule = 0 8 * * *
handler = FetchPrice

[node:FetchPrice]
type = request
url = https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd

[node:SendEmail]
type = email
subject = Daily Bitcoin Price
body = Current price: ${{FetchPrice.result.bitcoin.usd}}

[edges]
DailySchedule = []
FetchPrice = SendEmail
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Wrong Timer Edge Pattern

```toml
[edges]
ScheduleTask = ProcessData  # ❌ WRONG
```

**Why wrong:** Timer node routes via `handler` parameter, not edges

**Fix:**
```toml
[node:ScheduleTask]
handler = "ProcessData"  # ✅ Correct

[edges]
ScheduleTask = []  # ✅ Empty edge for timer
```

---

### ❌ Mistake 2: Invalid Cron Expression

```toml
schedule = every 5 minutes  # ❌ Not cron format
```

**Why wrong:** Must use cron syntax

**Fix:**
```toml
schedule = */5 * * * *  # ✅ Correct cron format
```

---

### ❌ Mistake 3: No Database for Data Collection

```toml
# User: "check prices every hour and track them"

[node:FetchPrice]
type = "request"
# ❌ Missing database storage
```

**Why wrong:** User wants to "track" (store history)

**Fix:** Add database table and store node

---

### ❌ Mistake 4: Wrong Connection Parameter Name

```toml
[parameters]
database_url = {{.env.DATABASE_URL}}  # ❌ Wrong parameter name
```

**Why wrong:** Should use connection_string, not database_url

**Fix:**
```toml
[parameters]
connection_string = postgresql://connection-string  # ✅ Correct
```

---

### ❌ Mistake 5: Not Handling Failures

```toml
[node:FetchData]
type = "request"
url = "https://unreliable-api.com"
# Missing retry logic  ❌
```

**Why wrong:** Scheduled tasks run unattended, need resilience

**Fix:**
```toml
[node:FetchData]
retry_on_failure = true
max_retries = 3
timeout_seconds = 30
```

---

## Response Pattern

### Simple Scheduled Task

**User:** "generate random number every hour"

**Response:**
```
"✓ Random number generator created: ../components/apps/act-docker/flows/random-scheduler.flow

Generates a random number every hour and stores results.

**To deploy:** Use the Flow Manager UI to start the service

**Port:** 9001
**Schedule:** Every hour (0 * * * *)
**Database:** numbers table created on first run"
```

---

### Scheduled Data Collection

**User:** "track ISS location every 5 minutes"

**Response:**
```
"✓ ISS tracking created: ../components/apps/act-docker/flows/iss-tracker.flow

Checks location every 5 minutes and stores history.

**To deploy:** Use the Flow Manager UI to start the service

**Port:** 9002
**Schedule:** Every 5 minutes (*/5 * * * *)
**API:** GET /api/iss/history - View tracking data
**Database:** iss_tracking table created on first run"
```

---

### Daily Report

**User:** "email me weather every morning at 8am"

**Response:**
```
"✓ Daily weather reports created: ../components/apps/act-docker/flows/weather-scheduler.flow

Sends email every day at 8:00 AM UTC with current weather.

**To deploy:** Use the Flow Manager UI to start the service

**Port:** 9003
**Schedule:** Daily at 8:00 AM UTC (0 8 * * *)
**Email:** Configured to send to your email
**Requirements:** SMTP credentials in environment variables"
```

---

## When to Include API Endpoints

**Include API endpoints when:**
- User wants to query collected data: "and let me view the history"
- Natural to access results: ISS tracking, price history
- Data is useful for other integrations

**Don't include API endpoints when:**
- Pure automation: "just run this task"
- Only notifications: "email me the results"
- Simple logging: "track this for my records"

**Example WITH API:**
```
"track Bitcoin price every hour"
→ Include GET /api/prices/history endpoint
```

**Example WITHOUT API:**
```
"backup database every night"
→ No API needed, just run the backup
```

---

## Success Criteria

✅ **Requirements Met When:**

1. Timer node created with correct cron schedule
2. Timer uses `handler` parameter (not edges)
3. Task logic nodes implemented
4. Database table created (if storing data)
5. Results stored (if applicable)
6. Full server configuration included
7. Port assigned (9001+)
8. Service registered in catalog
9. Permanent .flow file used
10. Service deploys successfully
11. First execution happens
12. User sees confirmation

---

## Complete Example Flow

**User Query:** "generate random number every hour and store it"

**Internal Process:**

1. **Classify:** Scheduled task (recurring)
2. **Load:** This context (scheduled-task.md)
3. **Extract:** Schedule = every hour (0 * * * *)
4. **Read Catalogs:** Timer node, Python node, Neon database
5. **Read Example:** examples/scheduled-random.flow
6. **Design:**
   - Timer (hourly trigger)
   - Python (generate random)
   - Database (store results)
   - Port 9001
7. **Create Flow:** (see example file)
8. **Deploy:** Execute flow
9. **Respond:**

```
"✓ Random number generator created: ../components/apps/act-docker/flows/random-scheduler.flow

Generates a random number every hour and stores results.

**To deploy:** Use the Flow Manager UI to start the service

**Port:** 9001
**Schedule:** Every hour (0 * * * *)
**Database:** numbers table created on first run"
```

---

## Checklist Before Responding

- [ ] Did I extract the schedule correctly?
- [ ] Did I convert to cron format?
- [ ] Did I create timer node with `handler` parameter (no quotes)?
- [ ] Did I set timer edge to `[]`?
- [ ] Did I create task logic nodes (no quotes on type)?
- [ ] Did I create database table (if storing)?
- [ ] Did I create storage node (if applicable)?
- [ ] Did I include retry logic?
- [ ] Did I use connection_string parameter (not database_url)?
- [ ] Did I include footer sections in correct order ([env], [settings], [configuration], [deployment])?
- [ ] Did I NOT include [service_catalog] section?
- [ ] Did I assign a port?
- [ ] Did I save as permanent .flow file?
- [ ] Did I NOT execute the flow (user deploys manually)?
- [ ] Did I respond with file location and deployment instructions?

**If any checkbox is unchecked, DO NOT RESPOND YET.**

---

## Remember

**Scheduled Task = Timer + Task Logic + Storage + Deployment**

- Convert interval to cron format
- Timer uses `handler` (unquoted), not edges
- Timer edge is `[]`
- No quotes on type/mode/operation/handler
- Store results if tracking data
- Use connection_string parameter (not database_url)
- Footer sections: [env], [settings], [configuration], [deployment]
- NO [service_catalog] section
- Save as .flow file (do NOT execute)
- Provide deployment instructions to user

**That's it.**
