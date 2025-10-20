# Dynamic Catalog Adoption Plan for Flow Architect

## 🎯 Mission
Replace all static catalog references in Flow Architect instructions with dynamic catalog API calls, enabling real-time service awareness and accurate connection string generation.

## 📊 Current State Analysis

### Files That Need Updates

#### 1. **Core Agent File**
- `flow-architect/.claude/agents/flow-architect.md`
- Currently: Points to static catalogs
- Change: Use live API endpoints

#### 2. **Context Files That Read Catalogs**
- `flow-architect/.claude/instructions/contexts/simple-api.md`
- `flow-architect/.claude/instructions/contexts/complex-api.md`
- `flow-architect/.claude/instructions/contexts/full-application.md`
- `flow-architect/.claude/instructions/contexts/scheduled-task.md`
- `flow-architect/.claude/instructions/contexts/multi-service-integration.md`
- `flow-architect/.claude/instructions/contexts/data-fetch-once.md`

#### 3. **Static Catalog Files (To Be Deprecated)**
- `flow-architect/catalogs/service-catalog.json` → Replace with `/api/catalog`
- `flow-architect/catalogs/node-catalog.json` → Keep (node types don't change dynamically)

## 🔄 Migration Strategy

### Phase 1: Update Core Agent Instructions

**File:** `flow-architect/.claude/agents/flow-architect.md`

**Current Pattern:**
```markdown
### Step 3: Read Catalogs (if needed)
- Read `catalogs/service-catalog.json` for available services
- Read `catalogs/node-catalog.json` for available node types
```

**New Pattern:**
```markdown
### Step 3: Read Catalogs (if needed)
- Fetch `http://localhost:3000/api/catalog/flows` for available flow services
- Fetch `http://localhost:3000/api/catalog?type=infrastructure` for infrastructure services
- Read `catalogs/node-catalog.json` for available node types (static is OK)
```

### Phase 2: Update Each Context File

#### A. Simple/Complex/Full API Contexts

**Current Pattern:**
```markdown
### Step 2: Read Catalogs
**Files:**
- `catalogs/service-catalog.json`
- `catalogs/node-catalog.json`
```

**New Pattern:**
```markdown
### Step 2: Check Available Services
**Dynamic Catalog API:**
```bash
# Check running database services
curl -s http://localhost:3000/api/catalog?type=infrastructure&category=database&status=running

# Parse response to get connection strings
# Example: PostgreSQL at postgresql://user:pass@localhost:5432/db
```

**Static Node Types:**
- Still read `catalogs/node-catalog.json` for node types
```

#### B. Multi-Service Integration Context

**Current Pattern:**
```markdown
### Step 1: Read Catalogs
**Files:**
- `catalogs/service-catalog.json` - Available services
- `catalogs/node-catalog.json` - Node types

**Check for:**
- Email service (SMTP)
- Webhook capabilities
- HTTP request capabilities
- Database availability
```

**New Pattern:**
```markdown
### Step 1: Check Live Services
**Query Running Services:**
```bash
# Get all running services with their connection info
curl -s http://localhost:3000/api/catalog?status=running

# Check for specific capabilities
curl -s http://localhost:3000/api/catalog | jq '.services[] | select(.capabilities | contains(["email"]))'
```

**Verify Available:**
- Database service running? Get live connection string
- Email service configured? Get SMTP settings
- External APIs accessible? Check endpoints
```

### Phase 3: Connection String Generation

**Old Approach:**
```toml
[parameters]
connection_string = postgresql://neondb_owner:password@host:5432/db?sslmode=require
```

**New Dynamic Approach:**
```markdown
### Generate Connection String from Live Services

1. **Query for running PostgreSQL:**
```bash
curl -s http://localhost:3000/api/catalog?type=infrastructure&category=database&status=running | \
  jq '.services[] | select(.id | contains("postgres")) | .connection.string'
```

2. **Use actual connection in flow:**
```toml
[parameters]
# Dynamically obtained from running service
connection_string = {{ACTUAL_CONNECTION_FROM_API}}
```
```

### Phase 4: Service Discovery Instructions

**Add New Section to Each Context:**
```markdown
### Dynamic Service Discovery

Before building any flow, check what's actually available:

1. **List all running services:**
```bash
curl -s http://localhost:3000/api/catalog?status=running
```

2. **Check if required service is running:**
```bash
# Example: Check if PostgreSQL is running
curl -s http://localhost:3000/api/catalog | \
  jq '.services[] | select(.id == "postgresql" and .status == "running")'
```

3. **If service not running, inform user:**
"PostgreSQL is not currently running. To use database features, start PostgreSQL first:
- Via Service Manager UI
- Or: POST /api/services {action: 'install', serviceId: 'postgresql'}"

4. **Get actual connection details:**
- Use the live connection string from the API
- Don't hardcode credentials
- Adapt to actual port numbers
```

## 📝 Implementation Checklist

### Step 1: Update Agent Router
- [ ] Edit `flow-architect/.claude/agents/flow-architect.md`
- [ ] Replace static catalog paths with API endpoints
- [ ] Add connection string fetching logic
- [ ] Add service availability checking

### Step 2: Update Context Files
- [ ] `simple-api.md` - Add live catalog querying
- [ ] `complex-api.md` - Add multi-service discovery
- [ ] `full-application.md` - Add comprehensive service check
- [ ] `scheduled-task.md` - Add timer service validation
- [ ] `multi-service-integration.md` - Add external service discovery
- [ ] `data-fetch-once.md` - Add API endpoint discovery

### Step 3: Add Helper Instructions
- [ ] Create `common/dynamic-catalog.md` - Shared catalog querying patterns
- [ ] Create `common/connection-strings.md` - Dynamic connection generation
- [ ] Create `common/service-availability.md` - Check if services are running

### Step 4: Update Examples
- [ ] Add comments showing where connection strings come from
- [ ] Show dynamic port detection
- [ ] Include service availability checks

### Step 5: Deprecation Strategy
- [ ] Keep `service-catalog.json` as fallback initially
- [ ] Add deprecation notice
- [ ] Log when static catalog is used
- [ ] Remove after testing period

## 🔧 Code Patterns to Add

### Pattern 1: Service Availability Check
```javascript
// Check if PostgreSQL is available before building flow
async function checkPostgresAvailable() {
  const response = await fetch('http://localhost:3000/api/catalog?type=infrastructure&status=running')
  const data = await response.json()

  const postgres = data.services.find(s =>
    s.id.includes('postgres') && s.status === 'running'
  )

  if (!postgres) {
    return {
      available: false,
      message: "PostgreSQL not running. Please start it first."
    }
  }

  return {
    available: true,
    connectionString: postgres.connection.string,
    port: postgres.connection.port
  }
}
```

### Pattern 2: Dynamic Flow Discovery
```javascript
// Find flows that have specific endpoints
async function findFlowsWithEndpoint(path) {
  const response = await fetch('http://localhost:3000/api/catalog/flows')
  const data = await response.json()

  return data.flows.filter(flow =>
    flow.endpoints.some(ep => ep.path.includes(path))
  )
}
```

### Pattern 3: Integration Check
```javascript
// Check if flow can integrate with another
async function canIntegrate(flowId) {
  const response = await fetch('http://localhost:3000/api/catalog/flows')
  const data = await response.json()

  const flow = data.flows.find(f => f.id === flowId)
  if (!flow) return false

  // Check if flow has API endpoints we can call
  return flow.endpoints.length > 0 && flow.status === 'running'
}
```

## 🚀 Benefits After Adoption

1. **Real-time Awareness**
   - Agent knows what's actually running
   - No more connection failures
   - Accurate port numbers

2. **Dynamic Integration**
   - Flows can discover each other
   - Auto-generate integration code
   - Chain flows together

3. **Better Error Messages**
   - "PostgreSQL not running" instead of connection timeout
   - "Port 5432 already in use" prevented
   - "No email service configured" upfront

4. **Smart Suggestions**
   - "I see you have MySQL running, want to use it?"
   - "clinic-management API is available at port 9009"
   - "3 flows have user endpoints you can integrate"

## 📅 Timeline

### Day 1: Core Updates
- Update agent router file
- Test with simple queries
- Verify catalog API responses

### Day 2: Context Files
- Update all 6 context files
- Add dynamic patterns
- Test flow generation

### Day 3: Helper Files
- Create common patterns
- Document best practices
- Add error handling

### Day 4: Testing
- Test with no services running
- Test with all services running
- Test flow integration

### Day 5: Documentation
- Update main README
- Create migration guide
- Record demo video

## ⚠️ Backward Compatibility

### Transition Period
1. **Check dynamic first, fallback to static:**
```javascript
let catalog;
try {
  // Try dynamic catalog
  const response = await fetch('http://localhost:3000/api/catalog')
  catalog = await response.json()
} catch (error) {
  // Fallback to static
  catalog = require('./catalogs/service-catalog.json')
  console.warn('Using static catalog (dynamic unavailable)')
}
```

2. **Gradual rollout:**
- Week 1: Add dynamic, keep static
- Week 2: Prefer dynamic, log static usage
- Week 3: Dynamic only, static as emergency backup
- Week 4: Remove static references

## 🔍 Testing Scenarios

### Scenario 1: No Services Running
- Agent should detect this
- Provide clear instructions to start services
- Suggest mock/test data

### Scenario 2: Multiple Databases
- Agent should list all options
- Let user choose
- Use chosen service's connection

### Scenario 3: Flow Integration
- Flow A wants to call Flow B
- Agent discovers Flow B's endpoints
- Generates correct HTTP calls

### Scenario 4: Port Conflicts
- Agent detects port already used
- Suggests next available port
- Updates configuration

## 📊 Success Metrics

1. **Zero Hardcoded Connections**
   - All connection strings from API
   - No static passwords
   - No fixed ports

2. **100% Service Discovery**
   - Every flow checks availability
   - Every integration verified
   - Every endpoint discovered

3. **Improved User Experience**
   - Clear error messages
   - Helpful suggestions
   - No mysterious failures

## 🛠️ Tools Needed

### Utility Functions Library
Create `flow-architect/lib/catalog-utils.js`:
```javascript
export async function getRunningServices(type = null) {
  const url = type
    ? `http://localhost:3000/api/catalog?type=${type}&status=running`
    : `http://localhost:3000/api/catalog?status=running`

  const response = await fetch(url)
  return response.json()
}

export async function getServiceConnection(serviceId) {
  const response = await fetch('http://localhost:3000/api/catalog')
  const data = await response.json()

  const service = data.services.find(s => s.id === serviceId)
  return service?.connection
}

export async function getFlowEndpoints(flowId) {
  const response = await fetch(`http://localhost:3000/api/catalog/flows`)
  const data = await response.json()

  const flow = data.flows.find(f => f.id === flowId)
  return flow?.endpoints || []
}
```

## 🎯 Final Goal

**Every Flow Architect instruction should:**
1. Query live services before building
2. Use actual connection strings
3. Verify service availability
4. Discover integration opportunities
5. Provide helpful feedback

**No instruction should:**
1. Hardcode connection strings
2. Assume services are running
3. Use static catalog files
4. Guess at port numbers
5. Ignore actual system state

---

## Quick Start Commands

```bash
# Test if catalog is accessible
curl -s http://localhost:3000/api/catalog | jq '.stats'

# Get all running services
curl -s 'http://localhost:3000/api/catalog?status=running' | jq

# Get PostgreSQL connection if running
curl -s http://localhost:3000/api/catalog | \
  jq '.services[] | select(.id == "postgresql" and .status == "running") | .connection'

# Find flows with database nodes
curl -s http://localhost:3000/api/catalog/flows | \
  jq '.flows[] | select(.nodeTypes | contains(["neon"]))'
```

---

**Created:** 2024-10-20
**Version:** 1.0.0
**Status:** Ready for Implementation