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

### Step 1: Read Service Catalog

**File:** `catalogs/service-catalog.json`

**Check for:**
- Available database (Neon PostgreSQL, MongoDB, etc.)
- Connection strings
- Service status

**Example:**
```json
{
  "id": "neon-postgres-primary",
  "type": "database",
  "connection": {
    "string": "postgresql://user:pass@host:5432/dbname"
  }
}
```

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

**Check existing ports:**
```bash
grep "^port = " flows/*.flow | sort -t= -k2 -n | tail -1
```

**Output example:** `port = 9002`

**Next port:** 9003

**Default if no flows exist:** 9001

### Step 5: Create Workflow Header

```toml
[workflow]
name = "[Resource] API"
description = "[Description]"
start_node = Create[Resource]Table

[settings]
debug_mode = true
max_retries = 3
timeout_seconds = 600
log_level = "info"

[configuration]
agent_enabled = true
agent_name = "[resource]-api-agent"
agent_version = "1.0.0"

[server]
host = "0.0.0.0"
port = [PORT]
cors = {enabled = true, origins = ["*"]}
environment = "development"
auto_restart = true

[deployment]
environment = "production"

[service_catalog]
register = true
service_name = "[Resource] API"
service_type = "api"
description = "[What it does]"
icon = "[emoji]"
category = "utility"
endpoints = [
  {path = "/api/[resource]", method = "GET", description = "Get all [resources]"},
  {path = "/api/[resource]", method = "POST", description = "Add new [resource]"}
]

[parameters]
database_url = "{{.env.DATABASE_URL}}"

[env]
DATABASE_URL = "postgresql://connection-string"
```

### Step 6: Create Table Creation Node

```toml
[node:Create[Resource]Table]
type = "neon"
label = "Create [resource] table"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = """
CREATE TABLE IF NOT EXISTS [resources] (
    id SERIAL PRIMARY KEY,
    [field1] [TYPE],
    [field2] [TYPE],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
```

### Step 7: Create GET Endpoint (List All)

**ACI Node (Route Definition):**
```toml
[node:DefineGet[Resources]Route]
type = "aci"
mode = "server"
label = "GET /api/[resources]"
operation = "add_route"
route_path = "/api/[resources]"
methods = ["GET"]
handler = "Fetch[Resources]"
description = "Get all [resources]"
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
type = "aci"
mode = "server"
label = "POST /api/[resources]"
operation = "add_route"
route_path = "/api/[resources]"
methods = ["POST"]
handler = "Add[Resource]"
description = "Add new [resource]"
```

**Handler Node:**
```toml
[node:Add[Resource]]
type = "neon"
label = "Insert [resource]"
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

```toml
[edges]
Create[Resource]Table = DefineGet[Resources]Route
Create[Resource]Table = DefineAdd[Resource]Route
DefineGet[Resources]Route = Fetch[Resources]
DefineAdd[Resource]Route = Add[Resource]
```

**CRITICAL PATTERN:**
- Table creation connects to ALL route definitions
- Each route connects ONLY to its specific handler
- DO NOT chain routes together

### Step 11: Save to Permanent Location

**Path:** `flows/[resource]-api.flow`

**Example:** `flows/quotes-api.flow`

**NOT temp/** - This is a persistent service

### Step 12: Deploy and Respond

**Execute the flow** - It will deploy as a running service

**Response Pattern:**
```
"✓ [Resource] API active at http://[machine]:[port]

Endpoints:
• POST /api/[resource] - Create [resource]
• GET /api/[resource] - List [resources]
[Additional endpoints if applicable]

Try it: curl http://[machine]:[port]/api/[resource]"
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

## Port Assignment Strategy

**Auto-increment from 9001:**

1. Check existing flows:
```bash
grep "^port = " flows/*.flow | sort -t= -k2 -n | tail -1
```

2. If output is `port = 9002`, next is 9003
3. If no output (no flows), use 9001

**Use in both places:**
```toml
[server]
port = 9003

[deployment]
port = 9003  # Must match!
```

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
3. **Read Catalogs:**
   - service-catalog.json → Neon database available
   - node-catalog.json → neon, aci nodes available
4. **Read Example:** examples/quotes-api.flow
5. **Design:**
   - Table: quotes (id, text, author, created_at)
   - Endpoints: POST /api/quotes, GET /api/quotes
   - Port: 9001 (first service)
6. **Create Flow:** (see example file)
7. **Deploy:** Execute flow
8. **Respond:**
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

- [ ] Did I read service-catalog.json?
- [ ] Did I read node-catalog.json?
- [ ] Did I read the example file?
- [ ] Did I design the database schema?
- [ ] Did I create table creation node?
- [ ] Did I create 2-5 API endpoint pairs (ACI + handler)?
- [ ] Did I include full server configuration?
- [ ] Did I assign a port (9001+)?
- [ ] Did I register in service catalog?
- [ ] Did I save as permanent .flow file?
- [ ] Did I execute the flow?
- [ ] Does each route connect ONLY to its handler?
- [ ] Did I respond with access URL and endpoint list?

**If any checkbox is unchecked, DO NOT RESPOND YET.**

---

## Remember

**Simple API = Database + 2-5 Endpoints + Server**

- Read catalogs
- Design schema
- Create table
- Define routes (ACI nodes)
- Create handlers (Neon nodes)
- Full server config
- Register in catalog
- Deploy
- Provide access info

**That's it.**
