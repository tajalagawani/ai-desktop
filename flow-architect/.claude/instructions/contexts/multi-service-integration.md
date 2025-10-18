# Multi-Service Integration Context

## When to Load This

**Query Patterns:**
- "monitor [external resource] and alert me"
- "fetch data from [API1] and [API2] and combine them"
- "when [event] happens, do [multiple actions]"
- "integrate [service1], [service2], and [service3]"
- User wants orchestration of multiple external services
- Complex workflows with external dependencies

**User Intent:**
- Connect to multiple external APIs
- Combine data from different sources
- Automated workflows with external triggers
- Monitoring and alerting systems
- ETL (Extract, Transform, Load) pipelines
- Event-driven architectures

## Complexity Level: VERY HIGH

**Flow Requirements:**
- HTTP request nodes (multiple external APIs)
- Timer nodes (scheduled checks)
- Database nodes (store results/history)
- Conditional logic nodes (if/switch)
- Email/webhook notification nodes
- Python nodes (complex data transformation)
- Full server configuration
- API endpoints (access collected data)
- Service catalog registration
- Permanent .flow file

---

## Example Patterns

✅ **Matches:**
- "monitor competitor prices, detect changes, and email me alerts"
- "fetch weather and ISS location, combine them, store daily"
- "when GitHub has new release, post to Slack and create task"
- "scrape news sites, analyze with AI, send summary email"
- "monitor API health, log to database, alert if down"

❌ **Does NOT Match:**
- "get ISS location" → data-fetch-once.md (single API call)
- "check prices every hour" → scheduled-task.md (single source)
- "create order API" → simple-api.md/complex-api.md (no external integration)

---

## Service Integration Patterns

### Pattern 1: Monitor + Alert

**Flow:**
```
Timer → Fetch External Data → Compare with Previous → If Changed → Send Alert + Store
```

**Example:** Price monitoring

### Pattern 2: Multi-Source Aggregation

**Flow:**
```
Timer → [Fetch API1, Fetch API2, Fetch API3] → Combine Data → Process → Store + API
```

**Example:** Market data dashboard

### Pattern 3: Event-Driven Workflow

**Flow:**
```
Webhook → Parse Event → [Action1, Action2, Action3] → Log
```

**Example:** GitHub webhook → Slack + Email + Database

### Pattern 4: ETL Pipeline

**Flow:**
```
Timer → Extract (HTTP) → Transform (Python) → Load (Database) → Notify
```

**Example:** Daily data sync

---

## Build Process (18 Steps)

### Step 1: Read Catalogs

**Files:**
- `catalogs/service-catalog.json` - Available services
- `catalogs/node-catalog.json` - Node types

**Check for:**
- Email service (SMTP)
- Webhook capabilities
- HTTP request capabilities
- Database availability

### Step 2: Identify All External Services

**Extract from user request:**
- **Data sources:** Which APIs to call
- **Actions:** Email, webhook, database
- **Triggers:** Timer, webhook listener, manual API call
- **Logic:** Comparisons, transformations, aggregations

**Example (Price Monitor):**
```
Trigger: Timer (every 4 hours)
Data Source: Competitor API
Storage: PostgreSQL (price history)
Logic: Price change detection
Actions: Email alert, log to database
API: Endpoints to view data/analytics
```

### Step 3: Design Database Schema

**Tables needed:**
- **History table:** Store fetched data over time
- **State table:** Track last known values
- **Alerts table:** Log triggered alerts
- **Config table:** Store monitored resources

**Example:**
```sql
-- Price history
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    competitor_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Competitors config
CREATE TABLE competitors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    api_endpoint VARCHAR(500) NOT NULL,
    active BOOLEAN DEFAULT TRUE
);

-- Price alerts
CREATE TABLE price_alerts (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    old_price DECIMAL(10,2) NOT NULL,
    new_price DECIMAL(10,2) NOT NULL,
    change_percent DECIMAL(5,2),
    alert_sent BOOLEAN DEFAULT FALSE,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 4: Design Workflow Logic

**Map out the flow:**

1. **Trigger** (how it starts)
   - Timer (cron schedule)
   - Webhook (external event)
   - API call (manual trigger)

2. **Fetch** (get data)
   - HTTP requests to external APIs
   - Parallel fetching if multiple sources
   - Error handling and retries

3. **Transform** (process data)
   - Parse responses
   - Combine multiple sources
   - Calculate derived values
   - Compare with previous state

4. **Decide** (conditional logic)
   - If/switch nodes
   - Threshold checks
   - Pattern matching

5. **Act** (take actions)
   - Store to database
   - Send email/webhook
   - Update external system
   - Log events

6. **Expose** (make data accessible)
   - API endpoints for querying
   - Analytics endpoints
   - Status/health checks

### Step 5: Map External API Requirements

**For each external service:**
- **Authentication:** API keys, OAuth, basic auth
- **Rate limits:** How often can you call?
- **Data format:** JSON, XML, CSV?
- **Error handling:** What errors to expect?

**Example:**
```toml
[parameters]
competitor_api_key = "{{.env.COMPETITOR_API_KEY}}"
smtp_host = "{{.env.SMTP_HOST}}"
alert_email = "{{.env.ALERT_EMAIL}}"

[env]
COMPETITOR_API_KEY = "your-api-key"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-password"
ALERT_EMAIL = "alerts@yourcompany.com"
```

### Step 6-10: Create Database Tables

```toml
[node:CreateHistoryTable]
type = "neon"
query = """CREATE TABLE IF NOT EXISTS price_history (...);"""

[node:CreateConfigTable]
type = "neon"
query = """CREATE TABLE IF NOT EXISTS competitors (...);"""

[node:CreateAlertsTable]
type = "neon"
query = """CREATE TABLE IF NOT EXISTS price_alerts (...);"""
```

### Step 11: Create Timer/Trigger Node

```toml
[node:ScheduleMonitoring]
type = "timer"
label = "Check every 4 hours"
schedule = "0 */4 * * *"
mode = "cron"
timezone = "UTC"
handler = "FetchCompetitors"
```

### Step 12: Create External API Fetch Nodes

```toml
[node:FetchCompetitorPrices]
type = "request"
label = "Fetch competitor prices"
method = "GET"
url = "https://api.competitor.com/prices"
headers = {"Authorization": "Bearer {{.Parameter.competitor_api_key}}"}
timeout_seconds = 30
retry_on_failure = true
max_retries = 3
```

### Step 13: Create Data Processing Nodes

```toml
[node:ParseAndCompare]
type = "py"
label = "Detect price changes"
code = """
def detect_changes(**kwargs):
    current_prices = kwargs.get('FetchCompetitorPrices', {}).get('result', {})
    previous_prices = kwargs.get('GetPreviousPrices', {}).get('result', [])

    changes = []
    for product in current_prices.get('products', []):
        # Find previous price
        prev = next((p for p in previous_prices if p['name'] == product['name']), None)

        if prev and prev['price'] != product['price']:
            change_percent = ((product['price'] - prev['price']) / prev['price']) * 100

            changes.append({
                'product': product['name'],
                'old_price': prev['price'],
                'new_price': product['price'],
                'change_percent': round(change_percent, 2)
            })

    return {
        'result': {
            'changes': changes,
            'has_changes': len(changes) > 0
        }
    }
"""
function = "detect_changes"
```

### Step 14: Create Conditional Logic

```toml
[node:CheckIfAlertNeeded]
type = "if"
label = "Check if changes detected"
condition = "{{ParseAndCompare.result.has_changes}} == true"
on_true = "SendAlert"
on_false = "LogNoChanges"
```

### Step 15: Create Action Nodes

**Email notification:**
```toml
[node:SendAlert]
type = "email"
label = "Send price change alert"
smtp_host = "{{.Parameter.smtp_host}}"
smtp_port = "{{.Parameter.smtp_port}}"
smtp_user = "{{.Parameter.smtp_user}}"
smtp_password = "{{.Parameter.smtp_password}}"
from_email = "{{.Parameter.smtp_user}}"
to_email = "{{.Parameter.alert_email}}"
subject = "Price Changes Detected"
body = """
Price changes detected:

{% for change in ParseAndCompare.result.changes %}
Product: {{ change.product }}
Old Price: ${{ change.old_price }}
New Price: ${{ change.new_price }}
Change: {{ change.change_percent }}%
---
{% endfor %}
"""
```

**Database storage:**
```toml
[node:StorePrices]
type = "neon"
label = "Store current prices"
connection_string = "{{.Parameter.database_url}}"
operation = "execute_query"
query = "INSERT INTO price_history (competitor_id, product_name, price) VALUES (%s, %s, %s)"
parameters = ["{{competitor_id}}", "{{product_name}}", "{{price}}"]
```

### Step 16: Create API Endpoints (Access Layer)

```toml
[node:DefineGetCurrentPricesRoute]
type = "aci"
mode = "server"
route_path = "/api/prices/current"
methods = ["GET"]
handler = "GetCurrentPrices"

[node:GetCurrentPrices]
type = "neon"
query = """
SELECT DISTINCT ON (product_name)
    product_name, price, checked_at
FROM price_history
ORDER BY product_name, checked_at DESC
"""

[node:DefineGetAnalyticsRoute]
type = "aci"
route_path = "/api/prices/analytics"
methods = ["GET"]
handler = "GetAnalytics"

[node:GetAnalytics]
type = "neon"
query = """
SELECT
    product_name,
    MIN(price) as lowest,
    MAX(price) as highest,
    AVG(price) as average
FROM price_history
GROUP BY product_name
"""
```

### Step 17: Define Edges

```toml
[edges]
# Table creation chain
CreateHistoryTable = CreateConfigTable
CreateConfigTable = CreateAlertsTable

# Connect to timer and API routes
CreateAlertsTable = ScheduleMonitoring
CreateAlertsTable = DefineGetCurrentPricesRoute
CreateAlertsTable = DefineGetAnalyticsRoute

# Timer flow
ScheduleMonitoring = []  # Timer handles routing
FetchCompetitorPrices = ParseAndCompare
ParseAndCompare = CheckIfAlertNeeded
CheckIfAlertNeeded = []  # Conditional handles routing
SendAlert = StorePrices

# API flows
DefineGetCurrentPricesRoute = GetCurrentPrices
DefineGetAnalyticsRoute = GetAnalytics
```

### Step 18: Deploy and Register

**Port:** Next available (e.g., 9006)

**Service type:** "monitor" or "integration"

**Register:** Full service catalog

---

## Load Example File

**Reference:**
- `.claude/instructions/examples/price-monitor.flow` - Complete multi-service example

---

## Node Types Needed

**Read:**
- `.claude/instructions/node-types/http-request.md`
- `.claude/instructions/node-types/timer.md`
- `.claude/instructions/node-types/email.md`
- `.claude/instructions/node-types/if.md`
- `.claude/instructions/node-types/python.md`
- `.claude/instructions/node-types/neon.md`
- `.claude/instructions/node-types/aci.md`

---

## Common Mistakes to Avoid

### ❌ Mistake 1: No Error Handling on External APIs

```toml
[node:FetchData]
type = "request"
url = "https://external-api.com"
# ❌ No retry or timeout
```

**Fix:**
```toml
timeout_seconds = 30
retry_on_failure = true
max_retries = 3
```

### ❌ Mistake 2: Exposing API Keys

```toml
headers = {"Authorization": "Bearer abc123"}  # ❌ Hardcoded key
```

**Fix:**
```toml
[parameters]
api_key = "{{.env.API_KEY}}"

[node:Fetch]
headers = {"Authorization": "Bearer {{.Parameter.api_key}}"}
```

### ❌ Mistake 3: Not Storing History

```toml
# User: "monitor prices and track changes"
# ❌ Only checking current price, not storing
```

**Fix:** Create history table and store all checks

### ❌ Mistake 4: Synchronous Multi-Fetch

```toml
[edges]
FetchAPI1 = FetchAPI2  # ❌ Sequential
FetchAPI2 = FetchAPI3
```

**Fix:** Parallel fetch
```toml
[edges]
Trigger = [FetchAPI1, FetchAPI2, FetchAPI3]  # ✅ Parallel
[FetchAPI1, FetchAPI2, FetchAPI3] = CombineData
```

### ❌ Mistake 5: Missing Rate Limit Handling

```toml
schedule = "* * * * *"  # ❌ Every minute might hit rate limits
```

**Fix:** Respect API rate limits, use appropriate schedule

---

## Response Pattern

**User:** "monitor competitor prices, detect changes, and alert me"

**Response:**
```
"✓ Price monitoring system created: flows/price-monitor.flow

**Monitoring:**
→ Checks competitor prices every 4 hours
→ Tracks price history in database
→ Detects price changes automatically
→ Sends email alerts when prices change

**Endpoints:**
• GET /api/prices/current - Latest prices
• GET /api/prices/history - Price history
• GET /api/prices/analytics - Price analytics
• GET /api/competitors - Tracked competitors
• POST /api/competitors - Add competitor

**To deploy:** Use the Flow Manager UI to start the service

**Port:** 9006
**Schedule:** Every 4 hours (0 */4 * * *)
**Email:** Configured to send alerts
**Requirements:** API keys and SMTP credentials in environment variables
**Database:** 3 tables (price_history, competitors, price_alerts) created on first run"
```

---

## Success Criteria

✅ **Requirements Met When:**

1. All external APIs identified
2. API authentication configured
3. Error handling and retries on HTTP requests
4. Database tables for history/state
5. Timer for scheduled checks
6. Data fetching nodes created
7. Data transformation/comparison logic
8. Conditional logic for decision-making
9. Action nodes (email, webhook, etc.)
10. API endpoints for data access
11. Full server configuration
12. Service catalog registration
13. Permanent .flow file
14. Service deploys successfully
15. First execution completes
16. User receives confirmation

---

## Checklist Before Responding

- [ ] Did I identify all external services?
- [ ] Did I configure API authentication?
- [ ] Did I add error handling to HTTP requests?
- [ ] Did I create history/state tables?
- [ ] Did I create timer or webhook trigger?
- [ ] Did I create fetch nodes for external APIs?
- [ ] Did I create data processing nodes?
- [ ] Did I add conditional logic?
- [ ] Did I create action nodes (email/webhook)?
- [ ] Did I create API endpoints for access?
- [ ] Did I use environment variables for secrets?
- [ ] Did I include full server config?
- [ ] Did I register in service catalog?
- [ ] Did I save as permanent .flow?
- [ ] Did I NOT execute/deploy (user does this manually)?
- [ ] Did I respond with file location and deployment instructions?

**If any checkbox is unchecked, DO NOT RESPOND YET.**

---

## Remember

**Multi-Service Integration = External APIs + Orchestration + Actions + Monitoring**

- Multiple external services
- Robust error handling
- Data transformation
- Conditional logic
- Actions (email, webhooks)
- History tracking
- API access layer
- Scheduled/event-driven
- Save as .flow file (do NOT execute)
- User deploys when ready

**That's it.**
