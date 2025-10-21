# Simple API Context

## When to Load This

**Query Patterns:**
- "create API"
- "build endpoint"
- "make API for [resource]"
- "API to store/get [data]"
- User wants 2-5 endpoints
- Single entity or simple use case

**User Intent:**
- Persistent API service
- Basic CRUD operations
- External access needed
- 1-2 database tables
- RESTful endpoints

## Complexity Level: MEDIUM

**Flow Requirements:**
- Database node(s) - create tables
- ACI nodes - define API routes (2-5 routes)
- Handler nodes - process requests
- Full server configuration
- Service catalog registration
- Permanent .flow file

---

## Example Patterns

✅ **Matches:**
- "create API to store and get quotes"
- "build API for tracking my expenses"
- "make endpoint to save notes"
- "API for todo items"
- "create endpoints for bookmarks"

❌ **Does NOT Match:**
- "what's 5 + 10?" → simple-calculation.md
- "build blog API with posts, comments, categories" → complex-api.md (10+ endpoints)
- "create restaurant management system" → full-application.md (30+ endpoints)

---

## Build Process (12 Steps)

### Step 1: Check Available Services

**Use Bash Tools (NOT curl):**

```bash
# Check for running database services
./flow-architect/tools/get-running-services.sh database

# Returns JSON array of running databases with connection info
```

**If no database running:**
- Inform user: "No database service is currently running. Please start PostgreSQL via Service Manager."
- Suggest: "Open Service Manager from the Dock to install and start PostgreSQL."
- DO NOT suggest Docker commands - use the Service Manager UI only

### Step 1.5: Verify Authentication

**CRITICAL - Check database authentication before proceeding:**

```bash
# Check if PostgreSQL has auth configured
./flow-architect/tools/check-service-auth.sh postgresql
```

**If returns `"configured":false`:**
- STOP - Do not proceed with building the flow
- Direct user to Service Manager to configure PostgreSQL credentials
- Wait for user to configure, then re-check

**Only proceed when authentication is verified!**

### Step 2: Design Database Schema

**For simple API:** Usually 1-2 tables

**Example (Quotes API):**
```sql
CREATE TABLE IF NOT EXISTS quotes (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    author VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Identify fields:**
- Primary key (id)
- Required fields (NOT NULL)
- Optional fields
- Timestamps

### Step 3: Design API Endpoints

**Standard CRUD pattern:**

1. **POST /api/[resource]** - Create new item
2. **GET /api/[resource]** - List all items
3. **GET /api/[resource]/{id}** - Get one item (optional for simple)
4. **PUT /api/[resource]/{id}** - Update item (optional for simple)
5. **DELETE /api/[resource]/{id}** - Delete item (optional for simple)

**Minimum for simple API:** POST + GET (2 endpoints)
**Typical for simple API:** POST + GET + GET{id} (3-4 endpoints)
**Maximum for simple API:** Full CRUD (5 endpoints)

### Step 4: Find Next Available Port

**CRITICAL:** You MUST call the port detection tool to get an available port.

**Use Bash Tool:**
```bash
./flow-architect/tools/get-available-port.sh
```

**Parse the JSON response:**
```json
{
  "success": true,
  "available_port": 9001,
  "used_ports": [9009, ...],
  "sources": {"flows": [9009], "service_catalog": [], "docker_compose": [9009]}
}
```

**Use the `available_port` value** or **use `{{.AvailablePort}}`** in the flow file
- This scans all flows, service catalog, and docker-compose to avoid conflicts
- Prefer using `{{.AvailablePort}}` for dynamic allocation

### Step 5: Create Workflow Header

**CRITICAL:** Follow exact TOML format and use environment variables

```toml
[workflow]
name = "[Resource] API"
description = "[Description of what it does]"
start_node = Create[Resource]Table

[settings]
debug_mode = true
max_retries = 3
timeout_seconds = 600
log_level = "info"

[server]
host = "0.0.0.0"
port = {{.AvailablePort}}
cors = {enabled = true, origins = ["*"]}
environment = "development"
auto_restart = true

[service_catalog]
register = true
service_name = "[Resource] API"
service_type = "api"
description = "[What this API does]"
icon = "📊"
category = "data"
endpoints = [
  {path = "/api/[resources]", method = "GET", description = "List all [resources]"},
  {path = "/api/[resources]", method = "POST", description = "Create [resource]"}
]

[parameters]
database_url = "{{.env.DATABASE_URL}}"

[env]
DATABASE_URL = "postgresql://connection-string-here"
```

**Key changes:**
- Use `{{.AvailablePort}}` for dynamic port allocation
- Database connection via `{{.Parameter.database_url}}`
- Service catalog registration included
- NO hardcoded connection strings!

### Step 6: Create Table Creation Node

**CRITICAL:** Use correct parameter reference

```toml
[node:Create[Resource]Table]
type = "neon"
label = "Create [resource] table"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = """
CREATE TABLE IF NOT EXISTS [resources] (
    id SERIAL PRIMARY KEY,
    [field1] [TYPE] NOT NULL,
    [field2] [TYPE],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
```

**Key:** Use `{{.Parameter.database_url}}` not `connection_string`

### Step 7: Create GET Endpoint (List All)

**CRITICAL:** type, mode, operation are NOT quoted. Handler is NOT quoted. Use hierarchical label format.

**ACI Node (Route Definition):**
```toml
[node:DefineGet[Resources]Route]
type = aci
mode = server
label = API.[Resource].1. GET /api/[resources]
operation = add_route
route_path = /api/[resources]
methods = ["GET"]
handler = Get[Resources]Handler
description = Get all [resources]
```

**Handler Node (Database Query):**
```toml
[node:Fetch[Resources]]
type = "neon"
label = "Fetch all [resources]"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = "SELECT * FROM [resources] ORDER BY created_at DESC"
```

### Step 8: Create POST Endpoint (Create New)

**ACI Node:**
```toml
[node:DefineAdd[Resource]Route]
type = aci
mode = server
label = API.[Resource].2. POST /api/[resources]
operation = add_route
route_path = /api/[resources]
methods = ["POST"]
handler = Add[Resource]Handler
description = Add new [resource]
```

**Handler Node:**
```toml
[node:Insert[Resource]]
type = "neon"
label = "Insert new [resource]"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = "INSERT INTO [resources] ([field1], [field2]) VALUES (%s, %s) RETURNING *"
parameters = ["{{request_data.field1}}", "{{request_data.field2}}"]
```

**Key:** Use `request_data` to access POST body fields

### Step 9: Create Optional GET{id} Endpoint

**ACI Node:**
```toml
[node:DefineGet[Resource]ByIdRoute]
type = "aci"
mode = "server"
label = "GET /api/[resources]/{id}"
operation = "add_route"
route_path = "/api/[resources]/<int:id_from_url>"
methods = ["GET"]
handler = "Fetch[Resource]ById"
description = "Get [resource] by ID"
```

**Handler Node:**
```toml
[node:Fetch[Resource]ById]
type = "neon"
label = "Fetch [resource] by ID"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = "SELECT * FROM [resources] WHERE id = %s"
parameters = ["{{request_data.id_from_url}}"]
```

**Key:** URL parameter `<int:id_from_url>` becomes `request_data.id_from_url`

### Step 10: Define Edges

**CRITICAL:** Edges come AFTER all nodes, BEFORE footer sections

```toml
[edges]
Create[Resource]Table = DefineGet[Resources]Route
Create[Resource]Table = DefineAdd[Resource]Route
DefineGet[Resources]Route = Fetch[Resources]
DefineAdd[Resource]Route = Insert[Resource]
```

### Step 11: Verify Complete Structure

**Ensure your flow file has all sections in this order:**

1. `[workflow]` - Name, description, start_node
2. `[settings]` - Debug, retries, timeouts
3. `[server]` - Host, port, CORS
4. `[service_catalog]` - Registration info
5. `[parameters]` - database_url
6. `[env]` - DATABASE_URL placeholder
7. `[node:...]` - All your nodes
8. `[edges]` - All connections

**All sections are now in Step 5 header - no separate footer needed!**

### Step 12: Save to Permanent Location

**Path:** `../components/apps/act-docker/flows/[resource]-api.flow`

**Example:** `../components/apps/act-docker/flows/quotes-api.flow`

**NOT temp/** - This is a persistent service

### Step 13: Save and Respond

**Save the .flow file** - Do NOT execute it

**User deploys manually** via Docker if they want to run it

**Response Pattern:**
```
"✓ [Resource] API created: ../components/apps/act-docker/flows/[resource]-api.flow

**Endpoints defined:**
• POST /api/[resource] - Create [resource]
• GET /api/[resource] - List [resources]
[Additional endpoints if applicable]

**To deploy:** Navigate to the Flow Manager UI to start the service.
(DO NOT use Docker commands - everything through UI or API)

**Port:** [PORT]
**Database:** PostgreSQL tables created on first run"
```

---

## Load Example

**Reference File:** `.claude/instructions/examples/quotes-api.flow`

Read this file to see a complete working example.

---

## Node Types Needed

**Read these:**
- `.claude/instructions/node-types/aci.md` - API route definition
- `.claude/instructions/node-types/neon.md` - PostgreSQL operations
- `.claude/instructions/node-types/python.md` - If business logic needed

**Key ACI Parameters:**
- `mode`: "server"
- `operation`: "add_route"
- `route_path`: URL path
- `methods`: ["GET"], ["POST"], etc.
- `handler`: Name of handler node

**Key Neon Parameters:**
- `connection_string`: From parameters
- `operation`: "execute_query"
- `query`: SQL statement
- `parameters`: Array of values (for parameterized queries)

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Chaining Routes

```toml
[edges]
DefineRoute1 = DefineRoute2  # ❌ WRONG
DefineRoute2 = Handler1
```

**Why wrong:** Calling Route1 executes Handler1's logic, returns wrong data

**Fix:**
```toml
[edges]
DefineRoute1 = Handler1  # ✅ Correct
DefineRoute2 = Handler2  # ✅ Correct
```

### ❌ Mistake 2: Missing Server Configuration

```toml
[configuration]
agent_enabled = true
# Missing server config!
```

**Why wrong:** No API endpoints will be exposed

**Fix:** Always include `[server]` section

### ❌ Mistake 3: Wrong URL Parameter Syntax

```toml
route_path = "/api/quotes/:id"  # ❌ Wrong syntax
```

**Why wrong:** Should use `<int:id_from_url>` not `:id`

**Fix:**
```toml
route_path = "/api/quotes/<int:id_from_url>"  # ✅ Correct
```

### ❌ Mistake 4: Not Using Parameterized Queries

```toml
query = "INSERT INTO quotes (text) VALUES ('" + request_data.text + "')"  # ❌ SQL injection!
```

**Why wrong:** SQL injection vulnerability

**Fix:**
```toml
query = "INSERT INTO quotes (text) VALUES (%s)"
parameters = ["{{request_data.text}}"]  # ✅ Parameterized
```

### ❌ Mistake 5: Forgetting Service Catalog Registration

```toml
# Missing [service_catalog] section
```

**Why wrong:** Service won't be discoverable

**Fix:** Always include `[service_catalog]` with:
- `register = true`
- `service_name`
- `endpoints` list

---

## Success Criteria

✅ **Requirements Met When:**

1. Database table(s) created
2. 2-5 API endpoints defined
3. Each route has proper handler
4. Full server configuration included
5. Port assigned (9001+)
6. Service registered in catalog
7. Saved as permanent .flow file
8. Deployed and running
9. User sees access URL and endpoints

---

## Complete Example (Quotes API)

**User Query:** "create an API to store and get quotes"

**Internal Process:**

1. **Classify:** Simple API (2 endpoints needed)
2. **Load:** This context (simple-api.md)
3. **Check Environment:**
   - `./flow-architect/tools/get-running-services.sh database` → Check PostgreSQL
   - `./flow-architect/tools/check-service-auth.sh postgresql` → Verify auth
   - `./flow-architect/tools/get-available-port.sh` → Get port
4. **Verify Auth:** If PostgreSQL not configured, direct to Service Manager and STOP
5. **Read Example:** `examples/quotes-api.flow`
6. **Design:**
   - Table: quotes (id, text, author, created_at)
   - Endpoints: POST /api/quotes, GET /api/quotes
   - Port: Use `{{.AvailablePort}}`
7. **Create Flow:** (see example file)
8. **Save:** Save .flow file
9. **Respond:**
```
"✓ Quotes API active at http://localhost:9001

Endpoints:
• POST /api/quotes - Add new quote
• GET /api/quotes - Get all quotes

Try it: curl http://localhost:9001/api/quotes"
```

---

## Variations

### Variation 1: With GET{id}

Add 3rd endpoint for fetching by ID:

```toml
[node:DefineGetQuoteByIdRoute]
type = "aci"
mode = "server"
label = "GET /api/quotes/{id}"
operation = "add_route"
route_path = "/api/quotes/<int:id_from_url>"
methods = ["GET"]
handler = "FetchQuoteById"
description = "Get quote by ID"

[node:FetchQuoteById]
type = "neon"
label = "Fetch quote by ID"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = "SELECT * FROM quotes WHERE id = %s"
parameters = ["{{request_data.id_from_url}}"]

[edges]
CreateQuotesTable = DefineGetQuoteByIdRoute
DefineGetQuoteByIdRoute = FetchQuoteById
```

### Variation 2: With DELETE

Add DELETE endpoint:

```toml
[node:DefineDeleteQuoteRoute]
type = "aci"
mode = "server"
label = "DELETE /api/quotes/{id}"
operation = "add_route"
route_path = "/api/quotes/<int:id_from_url>"
methods = ["DELETE"]
handler = "DeleteQuote"
description = "Delete quote"

[node:DeleteQuote]
type = "neon"
label = "Delete quote"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = "DELETE FROM quotes WHERE id = %s RETURNING id"
parameters = ["{{request_data.id_from_url}}"]

[edges]
CreateQuotesTable = DefineDeleteQuoteRoute
DefineDeleteQuoteRoute = DeleteQuote
```

### Variation 3: With Business Logic

Add Python node for processing before saving:

```toml
[node:ProcessQuote]
type = "py"
label = "Process quote data"
code = """
def process(**kwargs):
    request_data = kwargs.get('request_data', {})
    text = request_data.get('text', '')
    author = request_data.get('author', 'Unknown')

    # Capitalize author name
    author = author.title()

    # Trim whitespace
    text = text.strip()

    return {
        "result": {
            "text": text,
            "author": author
        }
    }
"""
function = "process"

[node:SaveProcessedQuote]
type = "neon"
label = "Save processed quote"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = "INSERT INTO quotes (text, author) VALUES (%s, %s) RETURNING *"
parameters = ["{{ProcessQuote.result.text}}", "{{ProcessQuote.result.author}}"]

[edges]
DefineAddQuoteRoute = ProcessQuote
ProcessQuote = SaveProcessedQuote
```

---

## Checklist Before Responding

**Authentication & Environment:**
- [ ] Did I check running services with `./flow-architect/tools/get-running-services.sh database`?
- [ ] Did I verify database authentication with `./flow-architect/tools/check-service-auth.sh postgresql`?
- [ ] Did I get available port with `./flow-architect/tools/get-available-port.sh`?
- [ ] If auth missing, did I direct user to Service Manager (NOT proceed)?

**Flow Design:**
- [ ] Did I read the example file (`examples/quotes-api.flow`)?
- [ ] Did I design the database schema?
- [ ] Did I create table creation node?
- [ ] Did I create 2-5 API endpoint pairs (ACI route + handler)?
- [ ] Did I use `{{.Parameter.database_url}}` for all database connections?
- [ ] Did I use `{{.AvailablePort}}` for port allocation?
- [ ] Did I include full server configuration in header?
- [ ] Did I register in service catalog?

**File & Deployment:**
- [ ] Did I save as permanent .flow file?
- [ ] Does each route connect ONLY to its handler (no chaining)?
- [ ] Did I use parameterized queries (NOT string concatenation)?
- [ ] Did I respond with file location and deployment instructions?

**If any checkbox is unchecked, DO NOT RESPOND YET.**

---

## Remember

**Simple API = Auth Check + Database + 2-5 Endpoints + Server**

**Process:**
1. Check services with bash tools
2. Verify authentication (CRITICAL!)
3. If auth missing → Direct to Service Manager, STOP
4. Design schema
5. Create table node
6. Define routes (ACI nodes)
7. Create handlers (Neon nodes)
8. Use `{{.AvailablePort}}` and `{{.Parameter.database_url}}`
9. Register in catalog
10. Save as .flow file
11. Provide deployment instructions

**Never skip authentication checks. Never use hardcoded values.**
