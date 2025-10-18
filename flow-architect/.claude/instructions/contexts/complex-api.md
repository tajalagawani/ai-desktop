# Complex API Context

## When to Load This

**Query Patterns:**
- "create API for [multi-entity system]"
- "build [resource] system with [multiple features]"
- "API with [entity1], [entity2], and [entity3]"
- User wants 6-15 endpoints
- Multiple related entities
- CRUD operations across entities

**User Intent:**
- Moderate complexity API
- 2-4 database tables
- 6-15 total endpoints
- Relationships between entities
- Full CRUD on most/all entities
- Production-ready service

## Complexity Level: MEDIUM-HIGH

**Flow Requirements:**
- Multiple database tables (2-4)
- Multiple API route groups (2-4 entities)
- Full CRUD endpoints (6-15 total)
- Full server configuration
- Service catalog registration
- Permanent .flow file
- Proper indexing and constraints

---

## Example Patterns

✅ **Matches:**
- "create todo API with tasks, categories, and tags"
- "build blog API with posts, comments, and categories"
- "API for library system with books, authors, and loans"
- "create invoice system with customers, invoices, and items"
- "build project tracker with projects, tasks, and team members"

❌ **Does NOT Match:**
- "create API to store quotes" → simple-api.md (only 2-5 endpoints)
- "build restaurant management system" → full-application.md (30+ endpoints, 6+ tables)
- "API that calls another API" → multi-service-integration.md (external integrations)

---

## Complexity Indicators

**Simple API (2-5 endpoints):**
- Single entity or simple use case
- Basic CRUD or subset
- 1-2 tables max

**Complex API (6-15 endpoints):**
- 2-4 related entities
- Full CRUD on most entities
- Relationships (foreign keys)
- Multiple table joins

**Full Application (15+ endpoints):**
- 5+ entities
- Complex business logic
- Many-to-many relationships
- Advanced features (search, filters, pagination)

---

## Build Process (14 Steps)

### Step 1: Read Catalogs

**Files:**
- `catalogs/service-catalog.json` - Available databases
- `catalogs/node-catalog.json` - Node types

**Check for:**
- Database availability (Neon PostgreSQL)
- Connection details
- Node capabilities

### Step 2: Identify Entities

**Parse user request to extract:**
- **Main entities** (nouns): posts, comments, categories, etc.
- **Relationships**: post has many comments, post belongs to category
- **Required operations**: create, read, update, delete

**Example:**
```
"blog API with posts, comments, and categories"

Entities:
1. Posts (main entity)
2. Comments (belongs to post)
3. Categories (posts can have one)

Relationships:
- Post → Category (many-to-one)
- Post → Comments (one-to-many)
```

### Step 3: Design Database Schema

**For each entity, determine:**
- **Fields**: id, name, timestamps, etc.
- **Data types**: VARCHAR, TEXT, INTEGER, BOOLEAN, TIMESTAMP
- **Constraints**: NOT NULL, UNIQUE, foreign keys
- **Indexes**: For foreign keys and frequently queried fields

**Example schema:**
```sql
-- Posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    category_id INTEGER,  -- Foreign key
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,  -- Foreign key
    author VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL
);

-- Indexes
CREATE INDEX idx_posts_category_id ON posts(category_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);
```

### Step 4: Design API Endpoints

**Standard CRUD pattern for each entity:**

**Posts (main entity - full CRUD):**
1. `GET /api/posts` - List all posts
2. `GET /api/posts/<id>` - Get single post
3. `POST /api/posts` - Create post
4. `PUT /api/posts/<id>` - Update post
5. `DELETE /api/posts/<id>` - Delete post

**Comments (related entity - create + list):**
6. `GET /api/comments` - List comments (often filtered by post_id)
7. `POST /api/comments` - Add comment

**Categories (simple entity - list + create):**
8. `GET /api/categories` - List categories
9. `POST /api/categories` - Create category

**Total: 9 endpoints for 3 entities**

### Step 5: Find Next Available Port

```bash
grep "^port = " ../components/apps/act-docker/flows/*.flow | sort -t= -k2 -n | tail -1
```

**Output:** `port = 9003`
**Next port:** 9004

### Step 6: Create Workflow Header

```toml
[workflow]
name = "[System] API"
description = "[Description of what it does]"
start_node = Create[FirstEntity]Table

[settings]
debug_mode = true
max_retries = 3
timeout_seconds = 600
log_level = "info"

[configuration]
agent_enabled = true
agent_name = "[system]-api-agent"
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
service_name = "[System] API"
service_type = "api"
description = "[What it manages]"
icon = "[emoji]"
category = "[category]"
endpoints = [
  # List all endpoints here
  {path = "/api/[entity]", method = "GET", description = "..."},
  {path = "/api/[entity]", method = "POST", description = "..."},
  # ... more endpoints
]

[parameters]
database_url = "{{.env.DATABASE_URL}}"

[env]
DATABASE_URL = "postgresql://connection-string"
```

### Step 7: Create Database Tables (Sequential)

Create one node per table, chain them sequentially:

```toml
[node:CreatePostsTable]
type = "neon"
label = "Create posts table"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = """
CREATE TABLE IF NOT EXISTS posts (...);
CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category_id);
"""

[node:CreateCommentsTable]
type = "neon"
label = "Create comments table"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = """
CREATE TABLE IF NOT EXISTS comments (...);
CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id);
"""

[node:CreateCategoriesTable]
type = "neon"
label = "Create categories table"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = """
CREATE TABLE IF NOT EXISTS categories (...);
"""
```

### Step 8-12: Create Endpoint Pairs

For each endpoint, create:
1. **ACI node** (route definition)
2. **Handler node** (database operation)

**Pattern:**
```toml
# Route definition
[node:Define[Operation][Entity]Route]
type = "aci"
mode = "server"
label = "[METHOD] /api/[entity]"
operation = "add_route"
route_path = "/api/[entity]"  # or /api/[entity]/<int:id_from_url>
methods = ["[METHOD]"]
handler = "[HandlerNodeName]"
description = "[What it does]"

# Handler
[node:[HandlerNodeName]]
type = "neon"
label = "[Operation description]"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = "[SQL]"
parameters = [...]  # If parameterized query
```

### Step 13: Define Edges

```toml
[edges]
# Sequential table creation
CreateTable1 = CreateTable2
CreateTable2 = CreateTable3

# Connect last table to all route definitions
CreateTable3 = DefineRoute1
CreateTable3 = DefineRoute2
CreateTable3 = DefineRoute3
# ... etc

# Each route connects to its handler
DefineRoute1 = Handler1
DefineRoute2 = Handler2
DefineRoute3 = Handler3
# ... etc
```

**CRITICAL PATTERN:**
- Tables are created sequentially (chain)
- Last table connects to ALL route definitions (fan-out)
- Each route connects ONLY to its handler
- DO NOT chain routes together

### Step 14: Save (Do NOT Execute)

**Path:** `../components/apps/act-docker/flows/[system]-api.flow`

**Do NOT execute** - User deploys manually via Docker when ready

---

## Load Example Files

**Reference Files:**
- `.claude/instructions/examples/todo-api.flow` - 5 endpoints, full CRUD
- `.claude/instructions/examples/blog-system.flow` - 9 endpoints, 3 entities

Read these for complete working examples.

---

## Node Types Needed

**Read:**
- `.claude/instructions/node-types/aci.md` - API routes
- `.claude/instructions/node-types/neon.md` - Database operations

---

## Common Endpoint Patterns

### Pattern: List All

```toml
[node:DefineGetPostsRoute]
type = "aci"
route_path = "/api/posts"
methods = ["GET"]
handler = "FetchPosts"

[node:FetchPosts]
type = "neon"
query = "SELECT * FROM posts ORDER BY created_at DESC"
```

### Pattern: Get By ID

```toml
[node:DefineGetPostByIdRoute]
type = "aci"
route_path = "/api/posts/<int:id_from_url>"
methods = ["GET"]
handler = "FetchPostById"

[node:FetchPostById]
type = "neon"
query = "SELECT * FROM posts WHERE id = %s"
parameters = ["{{request_data.id_from_url}}"]
```

### Pattern: Create

```toml
[node:DefineCreatePostRoute]
type = "aci"
route_path = "/api/posts"
methods = ["POST"]
handler = "CreatePost"

[node:CreatePost]
type = "neon"
query = "INSERT INTO posts (title, content, category_id) VALUES (%s, %s, %s) RETURNING *"
parameters = ["{{request_data.title}}", "{{request_data.content}}", "{{request_data.category_id}}"]
```

### Pattern: Update

```toml
[node:DefineUpdatePostRoute]
type = "aci"
route_path = "/api/posts/<int:id_from_url>"
methods = ["PUT"]
handler = "UpdatePost"

[node:UpdatePost]
type = "neon"
query = "UPDATE posts SET title = %s, content = %s WHERE id = %s RETURNING *"
parameters = ["{{request_data.title}}", "{{request_data.content}}", "{{request_data.id_from_url}}"]
```

### Pattern: Delete

```toml
[node:DefineDeletePostRoute]
type = "aci"
route_path = "/api/posts/<int:id_from_url>"
methods = ["DELETE"]
handler = "DeletePost"

[node:DeletePost]
type = "neon"
query = "DELETE FROM posts WHERE id = %s RETURNING id"
parameters = ["{{request_data.id_from_url}}"]
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Missing Indexes

```sql
CREATE TABLE comments (
    post_id INTEGER NOT NULL  -- Foreign key without index ❌
);
```

**Why wrong:** Slow queries when filtering by post_id

**Fix:**
```sql
CREATE INDEX idx_comments_post_id ON comments(post_id);
```

### ❌ Mistake 2: Chaining Routes

```toml
[edges]
DefineRoute1 = DefineRoute2  # ❌ WRONG
```

**Why wrong:** Calling route1 executes route2's handler

**Fix:**
```toml
DefineRoute1 = Handler1  # ✅ Each route to its handler
DefineRoute2 = Handler2
```

### ❌ Mistake 3: Not Returning Data After Insert/Update

```sql
INSERT INTO posts (...) VALUES (...)  -- ❌ No RETURNING clause
```

**Why wrong:** Client doesn't get the created resource

**Fix:**
```sql
INSERT INTO posts (...) VALUES (...) RETURNING *  -- ✅ Return created row
```

### ❌ Mistake 4: Missing Service Catalog Endpoints

```toml
[service_catalog]
endpoints = [
  {path = "/api/posts", method = "GET"}
  # ❌ Missing other 8 endpoints
]
```

**Why wrong:** Service catalog incomplete

**Fix:** List ALL endpoints in service catalog

### ❌ Mistake 5: SQL Injection Vulnerability

```sql
query = "SELECT * FROM posts WHERE id = " + request_data.id  -- ❌ Dangerous
```

**Why wrong:** SQL injection attack vector

**Fix:**
```toml
query = "SELECT * FROM posts WHERE id = %s"  -- ✅ Parameterized
parameters = ["{{request_data.id}}"]
```

---

## Response Pattern

**User:** "create todo API with tasks, categories, and tags"

**Response:**
```
"✓ Todo API created: ../components/apps/act-docker/flows/todo-api.flow

**Task Management:**
• GET /api/tasks - List all tasks
• GET /api/tasks/<id> - Get task details
• POST /api/tasks - Create task
• PUT /api/tasks/<id> - Update task
• DELETE /api/tasks/<id> - Delete task

**Categories:**
• GET /api/categories - List categories
• POST /api/categories - Create category

**Tags:**
• GET /api/tags - List tags
• POST /api/tags - Create tag

**To deploy:** Use the Flow Manager UI to start the service

**Port:** 9004
**Database:** 4 tables (tasks, categories, tags, task_tags) created on first run"
```

---

## Success Criteria

✅ **Requirements Met When:**

1. 2-4 database tables created
2. Proper indexes on foreign keys
3. 6-15 API endpoints defined
4. Each route has corresponding handler
5. Full CRUD on main entities
6. Parameterized queries (no SQL injection)
7. RETURNING clauses on INSERT/UPDATE
8. Full server configuration
9. Port assigned correctly
10. All endpoints in service catalog
11. Permanent .flow file
12. Service deploys successfully
13. Response lists all endpoints

---

## Complete Example

**User Query:** "create todo API with tasks and categories"

**Entities:**
- Tasks (main): full CRUD
- Categories: list + create

**Endpoints:** 7 total
- GET/POST/GET{id}/PUT/DELETE /api/tasks (5)
- GET/POST /api/categories (2)

**Database:**
```sql
-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Index
CREATE INDEX idx_tasks_category ON tasks(category_id);
```

**Flow:** See `examples/todo-api.flow`

**Response:**
```
"✓ Todo API created: ../components/apps/act-docker/flows/todo-api.flow

**Tasks:**
• GET /api/tasks - List all tasks
• GET /api/tasks/<id> - Get task details
• POST /api/tasks - Create new task
• PUT /api/tasks/<id> - Update task
• DELETE /api/tasks/<id> - Delete task

**Categories:**
• GET /api/categories - List categories
• POST /api/categories - Create category

**To deploy:** Use the Flow Manager UI to start the service

**Port:** 9004
**Database:** 2 tables (tasks, categories) created on first run"
```

---

## Checklist Before Responding

- [ ] Did I identify all entities (2-4)?
- [ ] Did I design database schema?
- [ ] Did I create proper indexes?
- [ ] Did I design 6-15 endpoints?
- [ ] Did I create table creation nodes?
- [ ] Did I create all ACI route nodes?
- [ ] Did I create all handler nodes?
- [ ] Do routes connect only to handlers?
- [ ] Did I use parameterized queries?
- [ ] Did I include RETURNING clauses?
- [ ] Did I include full server config?
- [ ] Did I list all endpoints in catalog?
- [ ] Did I save as permanent .flow?
- [ ] Did I deploy the service?
- [ ] Did I respond with all endpoint info?

**If any checkbox is unchecked, DO NOT RESPOND YET.**

---

## Remember

**Complex API = Multiple Entities + Full CRUD + Relationships**

- 2-4 database tables
- 6-15 endpoints
- Proper indexes
- Each route → handler
- Parameterized queries
- Service catalog registration
- Save .flow file (do NOT execute)
- List all endpoints and deployment instructions in response

**That's it.**
