# Full Application Context

## When to Load This

**Query Patterns:**
- "create [complete system] to manage [complex domain]"
- "build [business name] management system"
- "full [domain] application with [many features]"
- User wants 15-40+ endpoints
- 5+ database tables
- Complex business workflows
- Complete operational system

**User Intent:**
- Production-ready application
- Full business domain coverage
- Multiple interconnected features
- Comprehensive CRUD operations
- Complex relationships
- Business logic and validation

## Complexity Level: HIGH

**Flow Requirements:**
- 5+ database tables
- 15-40+ API endpoints
- Complex relationships (foreign keys, many-to-many)
- Full server configuration
- Service catalog registration
- Permanent .flow file
- Comprehensive indexing
- Business logic nodes (if needed)

---

## Example Patterns

✅ **Matches:**
- "create restaurant management system with orders, menu, customers, reservations, and tables"
- "build e-commerce platform with products, orders, customers, inventory, and payments"
- "create school management system with students, teachers, courses, grades, and attendance"
- "build hospital system with patients, doctors, appointments, prescriptions, and billing"
- "create project management system with projects, tasks, team members, time tracking, and invoices"

❌ **Does NOT Match:**
- "create API for quotes" → simple-api.md (2-5 endpoints)
- "build blog with posts and comments" → complex-api.md (6-15 endpoints)
- "API that monitors prices" → multi-service-integration.md (external services)

---

## Complexity Indicators

**Simple API (2-5 endpoints):**
- 1-2 tables
- Single entity focus
- Basic operations

**Complex API (6-15 endpoints):**
- 2-4 tables
- Multiple related entities
- Full CRUD

**Full Application (15-40+ endpoints):**
- 5+ tables
- Many-to-many relationships
- Complex business logic
- Multi-step workflows
- Advanced queries (joins, aggregations)

---

## Build Process (17 Steps)

### Step 1: Check Live Services

**API Calls to make:**
```bash
# Get running infrastructure (databases, etc.)
Use MCP tool: list_available_nodes() or get_node_info()?type=infrastructure&status=running

# Get available flow services
Use MCP tool: list_available_nodes() or get_node_info()/flows

# Check node types (static file is OK for this)
cat catalogs/node-catalog.json
```

**Use actual connection strings from running services!**

### Step 2: Identify All Entities

**Extract from user request:**
- **Core entities** (main business objects)
- **Supporting entities** (lookup tables, categories)
- **Junction entities** (many-to-many relationships)

**Example (Restaurant System):**
```
Core Entities:
1. Orders (main transaction entity)
2. Customers (who places orders)
3. Menu Items (what can be ordered)

Supporting Entities:
4. Tables (restaurant tables)
5. Reservations (table bookings)

Junction Entities:
6. Order Items (many orders, many menu items)
```

### Step 3: Design Complete Database Schema

**For each entity:**
- Primary key (id SERIAL)
- Business fields
- Foreign keys
- Timestamps (created_at, updated_at)
- Status/state fields
- Constraints (NOT NULL, UNIQUE, CHECK)

**Example:**
```sql
-- Core entity
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Main transaction entity
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    table_number INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    total DECIMAL(10,2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Junction table (many-to-many)
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id INTEGER REFERENCES menu_items(id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    notes TEXT
);

-- Indexes for performance
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_menu ON order_items(menu_item_id);
```

### Step 4: Design Comprehensive API

**Endpoint structure:**
```
Main Entities (full CRUD):
- GET /api/[entity]
- GET /api/[entity]/<id>
- POST /api/[entity]
- PUT /api/[entity]/<id>
- DELETE /api/[entity]/<id>

Supporting Entities (list + create):
- GET /api/[entity]
- POST /api/[entity]

Special Operations:
- GET /api/[entity]/[action]
- POST /api/[entity]/<id>/[action]
```

**Example (Restaurant - 11 endpoints):**
```
Menu: GET, POST /api/menu (2)
Orders: GET, GET{id}, POST, PUT{id} /api/orders (4)
Customers: GET, POST /api/customers (2)
Reservations: GET, POST /api/reservations (2)
Tables: GET /api/tables (1)

Total: 11 endpoints
```

### Step 5: Find Next Available Port

**CRITICAL:** You MUST call the port detection API to get an available port.

**API Call:**
```bash
Use MCP tool: get_signature_info() to check available ports
```

**Parse the JSON response and use `available_port`** - this scans all sources to avoid conflicts

### Step 6: Create Workflow Header

**CRITICAL:** Follow exact TOML format - no quotes on values, no [server], no [service_catalog]

```toml
[workflow]
name = [System] Management System
description = Complete [domain] operations
start_node = Create[FirstEntity]Table

[parameters]
connection_string = postgresql://neondb_owner:password@host:5432/db?sslmode=require
```

**That's it for the header!** Footer sections come at the end.

### Step 7-11: Create All Database Tables

**CRITICAL:** No quotes on type/label/operation. Use {{.Parameter.connection_string}}

**Pattern:**
```toml
[node:Create[Entity1]Table]
type = neon
label = 1. Create [entity1] table
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = CREATE TABLE IF NOT EXISTS [entity1] (...); CREATE INDEX IF NOT EXISTS idx_[entity1]_[field] ON [entity1]([field])

[node:Create[Entity2]Table]
type = neon
label = 2. Create [entity2] table
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = CREATE TABLE IF NOT EXISTS [entity2] (...)

# Continue for all 5+ entities
```

**Chain them sequentially:**
```toml
[edges]
CreateTable1 = CreateTable2
CreateTable2 = CreateTable3
CreateTable3 = CreateTable4
CreateTable4 = CreateTable5
CreateTable5 = CreateTable6
```

### Step 12-14: Create All API Endpoints

**CRITICAL:** No quotes on type/mode/operation/handler. Use hierarchical labels.

**For each endpoint (15-40+ total):**

1. ACI route definition node
2. Handler node (database query)

**Example:**
```toml
# ===== Menu Endpoints =====
[node:DefineGetMenuRoute]
type = aci
mode = server
label = API.Menu.1. GET /api/menu
operation = add_route
route_path = /api/menu
methods = ["GET"]
handler = GetMenuHandler
description = Get all menu items

[node:GetMenuHandler]
type = neon
label = API.Menu.1.1. Fetch menu items
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = SELECT * FROM menu_items WHERE available = TRUE

# ===== Orders Endpoints =====
[node:DefineGetOrdersRoute]
type = aci
mode = server
label = API.Orders.1. GET /api/orders
operation = add_route
route_path = /api/orders
methods = ["GET"]
handler = GetOrdersHandler

[node:DefineCreateOrderRoute]
type = aci
mode = server
label = API.Orders.2. POST /api/orders
operation = add_route
route_path = /api/orders
methods = ["POST"]
handler = CreateOrderHandler

# ... Continue for all endpoints
```

### Step 15: Define Edges

```toml
[edges]
# Sequential table creation
CreateTable1 = CreateTable2
CreateTable2 = CreateTable3
# ... all tables chained

# Last table connects to ALL route definitions
CreateTableLast = DefineRoute1
CreateTableLast = DefineRoute2
CreateTableLast = DefineRoute3
# ... (15-40+ route definitions)

# Each route connects to its handler
DefineRoute1 = Handler1
DefineRoute2 = Handler2
# ... (15-40+ handlers)
```

### Step 16: Add Footer Sections

**CRITICAL:** Must be in this EXACT order at the end:

```toml
[env]

[settings]
debug_mode = true
max_retries = 3
timeout_seconds = 600

[configuration]
agent_enabled = true
agent_name = [system]-management-agent
agent_version = 1.0.0
host = 0.0.0.0
port = [PORT]
debug = true
cors_enabled = true

[deployment]
environment = development
```

### Step 17: Save (Do NOT Execute)

**Path:** `../components/apps/act-docker/flows/[system]-management.flow`

**Do NOT execute** - User deploys manually via Docker when ready

---

## Load Example File

**Reference:**
- `.claude/instructions/examples/restaurant-system.flow` - 6 tables, 11 endpoints

---

## Common Entity Patterns

### Pattern 1: User/Customer Entity

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_email ON customers(email);
```

### Pattern 2: Transaction Entity

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    status VARCHAR(20) DEFAULT 'pending',
    total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
```

### Pattern 3: Product/Item Entity

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(50) UNIQUE,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_active ON products(active);
```

### Pattern 4: Junction Table (Many-to-Many)

```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
```

### Pattern 5: Lookup/Category Table

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) UNIQUE,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id),
    active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_categories_parent ON categories(parent_id);
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Missing ON DELETE CASCADE

```sql
CREATE TABLE order_items (
    order_id INTEGER REFERENCES orders(id)  -- ❌ No cascade
);
```

**Why wrong:** Deleting order leaves orphaned items

**Fix:**
```sql
order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE
```

### ❌ Mistake 2: No Indexes on Foreign Keys

```sql
CREATE TABLE orders (
    customer_id INTEGER REFERENCES customers(id)
);
-- ❌ No index on customer_id
```

**Why wrong:** Slow queries when filtering by customer

**Fix:**
```sql
CREATE INDEX idx_orders_customer ON orders(customer_id);
```

### ❌ Mistake 3: Not Using DECIMAL for Money

```sql
price FLOAT NOT NULL  -- ❌ Float loses precision
```

**Why wrong:** Rounding errors with currency

**Fix:**
```sql
price DECIMAL(10,2) NOT NULL  -- ✅ Exact precision
```

### ❌ Mistake 4: Missing updated_at Timestamp

```sql
CREATE TABLE orders (
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    -- ❌ No updated_at
);
```

**Why wrong:** Can't track when record was last modified

**Fix:**
```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

Then in UPDATE handler:
```sql
UPDATE orders SET ..., updated_at = CURRENT_TIMESTAMP WHERE id = %s
```

### ❌ Mistake 5: Including Service Catalog Section

```toml
[service_catalog]
register = true
service_name = "Restaurant Management"
endpoints = [...]
```

**Why wrong:** Service catalog should NOT be in flow files

**Fix:** Remove [service_catalog] section entirely - it's registered automatically

---

## Response Pattern

**User:** "create restaurant management system"

**Response:**
```
"✓ Restaurant Management System created: ../components/apps/act-docker/flows/restaurant-management.flow

**Complete Operations:**
→ Order management (create, track, update)
→ Menu management (items, categories, pricing)
→ Customer database (profiles, history)
→ Table management (availability, assignments)
→ Reservations (booking, scheduling)

**Available Endpoints:**

**Menu:**
• GET /api/menu - View menu items
• POST /api/menu - Add menu item

**Orders:**
• GET /api/orders - List all orders
• GET /api/orders/<id> - Get order details
• POST /api/orders - Create new order
• PUT /api/orders/<id> - Update order status

**Customers:**
• GET /api/customers - List customers
• POST /api/customers - Add customer

**Reservations:**
• GET /api/reservations - List reservations
• POST /api/reservations - Create reservation

**Tables:**
• GET /api/tables - View table availability

**To deploy:** Use the Flow Manager UI to start the service

**Port:** 9005
**Database:** 6 tables created on first run"
```

---

## Success Criteria

✅ **Requirements Met When:**

1. 5+ database tables created
2. All tables have proper indexes
3. Foreign keys with CASCADE rules
4. 15-40+ endpoints defined
5. Full CRUD on main entities
6. Each route has handler (unquoted)
7. Parameterized queries
8. DECIMAL for money fields
9. Timestamps (created_at, updated_at)
10. No quotes on type/mode/operation/handler
11. Hierarchical labels used (API.Entity.Number. Description)
12. connection_string parameter used (not database_url)
13. Footer sections in correct order
14. NO [service_catalog] section included
15. Permanent .flow file
16. Response lists all major features with deployment instructions

---

## Checklist Before Responding

- [ ] Did I identify 5+ entities?
- [ ] Did I design complete schema?
- [ ] Did I add all indexes?
- [ ] Did I use CASCADE on foreign keys?
- [ ] Did I use DECIMAL for money?
- [ ] Did I include updated_at fields?
- [ ] Did I create 15+ endpoints?
- [ ] Did I create all table nodes (no quotes on type/operation)?
- [ ] Did I create all route nodes (no quotes on type/mode/operation)?
- [ ] Did I create all handler nodes (unquoted handler names)?
- [ ] Do routes connect only to handlers?
- [ ] Did I use parameterized queries?
- [ ] Did I use hierarchical labels (API.Entity.Number. Description)?
- [ ] Did I use connection_string parameter (not database_url)?
- [ ] Did I include footer sections in correct order ([env], [settings], [configuration], [deployment])?
- [ ] Did I NOT include [service_catalog] section?
- [ ] Did I save as permanent .flow?
- [ ] Did I NOT execute/deploy (user does this manually)?
- [ ] Did I respond with file location and deployment instructions?

**If any checkbox is unchecked, DO NOT RESPOND YET.**

---

## Remember

**Full Application = Complete Business Domain + Many Entities + Comprehensive API**

- 5+ database tables
- Proper relationships and indexes
- 15-40+ API endpoints
- Full CRUD operations
- No quotes on type/mode/operation/handler
- Hierarchical labels (API.Entity.Number. Description)
- connection_string parameter (not database_url)
- Footer sections: [env], [settings], [configuration], [deployment]
- NO [service_catalog] section
- Save as .flow file (do NOT execute)
- Feature-rich response with deployment instructions

**That's it.**
