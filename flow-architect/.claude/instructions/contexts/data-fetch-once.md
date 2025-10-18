# Data Fetch Once Context

## When to Load This

**Query Patterns:**
- "get current [data]"
- "fetch [resource] from [API]"
- "what is the [thing]?"
- "show me [external data]"
- User wants one-time data retrieval
- No storage needed
- No repeated execution

**User Intent:**
- Fetch external data once
- Display result immediately
- No persistence required
- No API endpoints needed

## Complexity Level: MINIMAL

**Flow Requirements:**
- HTTP request node (fetch data)
- Optional: Python node (parse/format)
- No database
- No server configuration
- No API endpoints
- Temp .act file execution

---

## Example Patterns

✅ **Matches:**
- "what's the current ISS location?"
- "get the weather in London"
- "fetch Bitcoin price"
- "show me top Hacker News posts"
- "what's the exchange rate for USD to EUR?"

❌ **Does NOT Match:**
- "track ISS location every hour" → scheduled-task.md (needs timer)
- "create API to get weather" → simple-api.md (needs server)
- "store Bitcoin prices" → needs database

---

## Build Process (6 Steps)

### Step 1: Identify the Data Source

**Determine:**
- API endpoint URL
- HTTP method (usually GET)
- Required parameters
- Authentication needs (API key, etc.)

**Common free APIs:**
- ISS Location: `http://api.open-notify.org/iss-now.json`
- Weather: `https://api.openweathermap.org/data/2.5/weather`
- Cryptocurrency: `https://api.coingecko.com/api/v3/simple/price`
- GitHub: `https://api.github.com/users/{username}`
- Hacker News: `https://hacker-news.firebaseio.com/v0/topstories.json`

### Step 2: Create HTTP Request Node

```toml
[workflow]
name = "[Resource] Fetcher"
description = "Fetch [what data]"
start_node = FetchData

[node:FetchData]
type = "request"
label = "Get [resource] data"
method = "GET"
url = "[API_ENDPOINT]"
headers = {"Accept": "application/json"}  # Optional
timeout_seconds = 10
retry_on_failure = true
max_retries = 2
```

**With API Key:**
```toml
[parameters]
api_key = "{{.env.API_KEY}}"

[env]
API_KEY = "your-api-key-here"

[node:FetchData]
type = "request"
url = "[API_ENDPOINT]"
headers = {"Authorization": "Bearer {{.Parameter.api_key}}"}
```

### Step 3: (Optional) Parse/Format Data

If the API response needs processing:

```toml
[node:ParseData]
type = "py"
label = "Extract relevant data"
code = """
def parse(**kwargs):
    response = kwargs.get('FetchData', {}).get('result', {})

    # Extract what you need
    extracted = {
        "field1": response.get('field1'),
        "field2": response.get('nested', {}).get('field2')
    }

    return {"result": extracted}
"""
function = "parse"

[edges]
FetchData = ParseData
```

### Step 4: Save to Temp Location

**Path:** `flows/temp/fetch-[resource]-[timestamp].act`

**Example:** `flows/temp/fetch-iss-1729267890.act`

**NOT permanent** - This is a one-time execution

### Step 5: Execute via API

```bash
curl -X POST http://localhost:3000/api/act/execute \
  -H "Content-Type: application/json" \
  -d '{
    "flowContent": "[TOML content]",
    "flowName": "fetch-[resource]-[timestamp].act"
  }'
```

### Step 6: Parse Result & Respond

**Extract data from response:**
```
response.result.results.ParseData.result.result
```

**Response Pattern:**
```
"[Icon] **[Key Info]**

[Additional details formatted nicely]"
```

**Example (ISS Location):**
```
"🛰️ **ISS Current Location**

Latitude: 45.23°
Longitude: -12.45°
Timestamp: 2024-10-18 14:30:22 UTC"
```

---

## Load Example Files

**Reference Files:**
- `.claude/instructions/examples/iss-location.act` - ISS tracking
- `.claude/instructions/examples/weather-fetch.act` - Weather data

Read these files to see complete working examples.

---

## Node Types Needed

**Read these:**
- `.claude/instructions/node-types/http-request.md` - HTTP operations
- `.claude/instructions/node-types/python.md` - Data parsing (if needed)

**Key HTTP Request Parameters:**
- `method`: "GET", "POST", "PUT", "DELETE"
- `url`: Full API endpoint
- `headers`: Object with header key-value pairs
- `timeout_seconds`: Max wait time
- `retry_on_failure`: true/false
- `max_retries`: Number of retry attempts

---

## Common API Examples

### Example 1: ISS Location

**User:** "where is the ISS right now?"

**Flow:**
```toml
[workflow]
name = "ISS Location Tracker"
description = "Fetch current International Space Station location"
start_node = FetchLocation

[node:FetchLocation]
type = "request"
label = "Get ISS coordinates"
method = "GET"
url = "http://api.open-notify.org/iss-now.json"
timeout_seconds = 10
retry_on_failure = true

[node:ParseLocation]
type = "py"
label = "Extract coordinates"
code = """
def parse(**kwargs):
    data = kwargs.get('FetchLocation', {}).get('result', {})
    lat = data['iss_position']['latitude']
    lon = data['iss_position']['longitude']

    return {
        "result": {
            "latitude": float(lat),
            "longitude": float(lon)
        }
    }
"""
function = "parse"

[edges]
FetchLocation = ParseLocation
```

**Response:**
```
"🛰️ **ISS Current Location**

Latitude: 45.23°
Longitude: -12.45°"
```

---

### Example 2: Cryptocurrency Price

**User:** "what's the Bitcoin price?"

**Flow:**
```toml
[workflow]
name = "Crypto Price Fetcher"
description = "Get current Bitcoin price"
start_node = FetchPrice

[node:FetchPrice]
type = "request"
label = "Get BTC price"
method = "GET"
url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
timeout_seconds = 10

[node:ExtractPrice]
type = "py"
label = "Extract price"
code = """
def extract(**kwargs):
    data = kwargs.get('FetchPrice', {}).get('result', {})
    price = data.get('bitcoin', {}).get('usd', 0)

    return {"result": {"price": price}}
"""
function = "extract"

[edges]
FetchPrice = ExtractPrice
```

**Response:**
```
"₿ **Bitcoin Price**

$43,250 USD"
```

---

### Example 3: GitHub User Info

**User:** "show me info about GitHub user octocat"

**Flow:**
```toml
[workflow]
name = "GitHub User Info"
description = "Fetch GitHub user details"
start_node = FetchUser

[parameters]
username = "octocat"

[node:FetchUser]
type = "request"
label = "Get user data"
method = "GET"
url = "https://api.github.com/users/{{.Parameter.username}}"
headers = {"Accept": "application/vnd.github.v3+json"}
timeout_seconds = 10

[node:ParseUser]
type = "py"
label = "Extract user info"
code = """
def parse(**kwargs):
    user = kwargs.get('FetchUser', {}).get('result', {})

    return {
        "result": {
            "name": user.get('name'),
            "bio": user.get('bio'),
            "public_repos": user.get('public_repos'),
            "followers": user.get('followers')
        }
    }
"""
function = "parse"

[edges]
FetchUser = ParseUser
```

**Response:**
```
"👤 **octocat**

Bio: GitHub mascot
Public Repos: 8
Followers: 5,241"
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Not Handling API Errors

```toml
[node:ParseData]
code = """
def parse(**kwargs):
    data = kwargs['FetchData']['result']  # ❌ KeyError if missing
    return {"result": data['field']}       # ❌ KeyError if missing
"""
```

**Why wrong:** API might fail or return unexpected structure

**Fix:**
```toml
code = """
def parse(**kwargs):
    data = kwargs.get('FetchData', {}).get('result', {})  # ✅ Safe access

    if 'field' not in data:
        return {"error": "Missing field in response"}

    return {"result": data['field']}
"""
```

### ❌ Mistake 2: Forgetting Timeout

```toml
[node:FetchData]
type = "request"
url = "https://slow-api.com/data"
# Missing timeout_seconds  ❌
```

**Why wrong:** Request might hang forever

**Fix:**
```toml
[node:FetchData]
type = "request"
url = "https://slow-api.com/data"
timeout_seconds = 15  # ✅ Always set timeout
retry_on_failure = true
max_retries = 2
```

### ❌ Mistake 3: Hardcoding API Keys

```toml
[node:FetchData]
url = "https://api.example.com/data?key=abc123"  # ❌ Exposed key
```

**Why wrong:** API key is visible in flow file

**Fix:**
```toml
[parameters]
api_key = "{{.env.API_KEY}}"

[env]
API_KEY = "abc123"

[node:FetchData]
url = "https://api.example.com/data?key={{.Parameter.api_key}}"  # ✅ Secure
```

### ❌ Mistake 4: Creating Server for One-Time Fetch

```toml
[configuration]
agent_enabled = true  # ❌ Not needed for one-time fetch

[server]
port = 9001  # ❌ No server needed
```

**Why wrong:** Over-engineering a simple request

**Fix:** Don't include `[configuration]` or `[server]` sections

### ❌ Mistake 5: Storing in Database

```toml
[node:StoreData]
type = "neon"  # ❌ User didn't ask to store
```

**Why wrong:** User wants one-time fetch, not persistence

**Fix:** Only fetch and return - no storage

---

## Response Formatting

### Pattern 1: Location Data

**Format:**
```
"[Icon] **[Location Name]**

Latitude: [value]°
Longitude: [value]°"
```

**Example:**
```
"🛰️ **ISS**

Latitude: 45.23°
Longitude: -12.45°"
```

### Pattern 2: Price Data

**Format:**
```
"[Icon] **[Asset Name]**

[Currency Symbol][Price] [Currency]"
```

**Example:**
```
"₿ **Bitcoin**

$43,250 USD"
```

### Pattern 3: Weather Data

**Format:**
```
"[Weather Icon] **[City]**

Temperature: [value]°C
Conditions: [description]
Humidity: [value]%"
```

**Example:**
```
"☁️ **London**

Temperature: 15°C
Conditions: Partly cloudy
Humidity: 72%"
```

### Pattern 4: User/Profile Data

**Format:**
```
"[Icon] **[Name]**

[Key Detail 1]
[Key Detail 2]
[Key Detail 3]"
```

**Example:**
```
"👤 **octocat**

Bio: GitHub mascot
Repos: 8
Followers: 5,241"
```

---

## Success Criteria

✅ **Requirements Met When:**

1. HTTP request node created
2. API endpoint correct
3. Timeout configured
4. Retry logic added
5. Data parsing (if needed)
6. Temp file used
7. Result extracted correctly
8. Response formatted nicely
9. No server created
10. No database used
11. No persistent file
12. ACT execution completed

---

## Complete Example Flow

**User Query:** "what's the current ISS location?"

**Internal Process:**

1. **Classify:** Data fetch (one-time)
2. **Load:** This context (data-fetch-once.md)
3. **Read Example:** examples/iss-location.act
4. **Create Flow:**
```toml
[workflow]
name = "ISS Location Tracker"
start_node = FetchLocation

[node:FetchLocation]
type = "request"
method = "GET"
url = "http://api.open-notify.org/iss-now.json"
timeout_seconds = 10
retry_on_failure = true

[node:ParseLocation]
type = "py"
code = """
def parse(**kwargs):
    data = kwargs.get('FetchLocation', {}).get('result', {})
    lat = data['iss_position']['latitude']
    lon = data['iss_position']['longitude']
    return {"result": {"lat": float(lat), "lon": float(lon)}}
"""
function = "parse"

[edges]
FetchLocation = ParseLocation
```

5. **Execute:** POST to `/api/act/execute`
6. **Parse Response:** Extract lat/lon
7. **Respond:**
```
"🛰️ **ISS Current Location**

Latitude: 45.23°
Longitude: -12.45°"
```

---

## When to Use This vs Other Contexts

**Use data-fetch-once.md when:**
- ✅ One-time data retrieval
- ✅ External API call
- ✅ Immediate display
- ✅ No storage needed

**Use scheduled-task.md when:**
- Repeated fetching (every X minutes)
- Data should be stored
- Historical tracking needed

**Use simple-api.md when:**
- User wants API endpoint to fetch data
- External access needed
- Data should be cached

---

## Checklist Before Responding

- [ ] Did I identify the correct API endpoint?
- [ ] Did I create HTTP request node?
- [ ] Did I add timeout and retry logic?
- [ ] Did I parse the response data?
- [ ] Did I save to temp location?
- [ ] Did I execute via `/api/act/execute`?
- [ ] Did I extract the actual result?
- [ ] Did I format the response nicely?
- [ ] Did I avoid creating server?
- [ ] Did I avoid creating database?
- [ ] Did I avoid persistent storage?

**If any checkbox is unchecked, DO NOT RESPOND YET.**

---

## Remember

**Data Fetch Once = HTTP Request → Parse → Display**

- External API call
- One-time execution
- Temp file
- No server
- No database
- Immediate result
- Formatted output

**That's it.**
