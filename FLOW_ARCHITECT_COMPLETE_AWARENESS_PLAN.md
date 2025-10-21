# Flow Architect Complete Awareness Plan (Skills-Based)

## 🎯 Objective

Make Flow Architect agent fully aware of the entire VPS environment using **Skills** and direct API calls:
- All running services (Docker containers)
- All available services (installable from hardcoded list)
- All nodes (with authentication status)
- All flows (deployed and available)
- All APIs (exposed endpoints)

**Approach:** Use Anthropic Skills + Direct API calls in contexts (NO MCP)

---

## 📊 Current API Mapping

### **1. Unified APIs (Main Discovery)**

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `/api/unified` | **Complete unified catalog** | Services + Nodes + Flows summary |
| `/api/catalog` | **Flow services only** | Running ACT flows with endpoints |
| `/api/catalog/flows` | **Flow discovery** | All .flow files parsed |
| `/api/services` | **Infrastructure services** | Docker services from hardcoded list |
| `/api/nodes` | **Node catalog** | All available node types |
| `/api/nodes/auth-required` | **Auth-required nodes** | Nodes needing authentication |
| `/api/docker/ps` | **Live Docker status** | Running containers directly |

### **2. Service Management APIs**

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `/api/services` (GET) | List all services with status | Services array with running status |
| `/api/services` (POST) | Install/start/stop/remove | Operation result |
| `/api/services/[serviceId]/auth` (GET) | Check auth status | 200 if configured, 404 if not |
| `/api/services/[serviceId]/auth` (POST) | Save auth credentials | Encrypted credentials |
| `/api/services/[serviceId]/auth` (DELETE) | Delete auth | Success/failure |

### **3. Node Management APIs**

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `/api/nodes` | List all node types | 129 nodes with operations |
| `/api/nodes/[nodeType]` | Get specific node info | Node details + operations |
| `/api/nodes/[nodeType]/operations` | List node operations | All operations for node type |
| `/api/nodes/[nodeType]/auth-info` | Get auth fields | Required auth fields |
| `/api/nodes/[nodeType]/auth` (GET) | Get stored auth | Decrypted credentials |
| `/api/nodes/[nodeType]/auth` (POST) | Save auth | Encrypted storage |
| `/api/nodes/[nodeType]/test` | Test node auth | Connection test result |

### **4. Flow Execution APIs**

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `/api/act/execute` | Execute ACT flow | Execution results |
| `/api/flows` | List all flows | Flow files |
| `/api/ports` | Get available port | Next available port 9001+ |

### **5. System APIs**

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `/api/system-stats` | System metrics | CPU, memory, disk, network |
| `/api/system-logs` | System logs | Recent log entries |
| `/api/pm2-processes` | PM2 processes | Running PM2 processes |

---

## 🔍 Research Findings

### **1. Claude Code Best Practices**

✅ **CLAUDE.md** - Primary context file (already using)
✅ **Custom Slash Commands** - `.claude/commands/` (not implemented yet)
✅ **Extended Thinking** - "think", "think hard", "think harder", "ultrathink"
✅ **MCP Integration** - Model Context Protocol for tools
✅ **Plan Mode** - Shift+Tab twice (separation of research and execution)

### **2. Model Context Protocol (MCP)**

**What it is:**
- Open standard for connecting AI to data sources
- Like "USB-C for AI applications"
- Provides Tools, Resources, and Prompts

**Key Components:**
- **MCP Servers**: Expose data through protocol
- **MCP Clients**: Connect to servers
- **Primitives**: Tools, Resources, Prompts (server), Roots, Sampling (client)

**Available SDK:**
- Python
- TypeScript
- C#
- Java

**Pre-built Servers:**
- Google Drive
- Slack
- GitHub
- Git
- Postgres
- Puppeteer

### **3. Anthropic Skills**

**What they are:**
- Custom modules in Markdown format
- Located in `~/.claude/skills/` directory
- Simple folder with `SKILL.md` file
- YAML frontmatter + instructions
- Can include pre-written scripts

**How they work:**
- Claude scans available skills to find matches
- Loads only minimal info needed
- Composable (stack together)
- Portable (work across Claude apps, Claude Code, API)

**Requirements:**
- Code Execution Tool beta
- SKILL.md with YAML frontmatter

**Example Structure:**
```
~/.claude/skills/my-skill/
├── SKILL.md          # Main skill definition
├── helper.py         # Optional helper scripts
└── data.json         # Optional data files
```

**GitHub Repository:** `anthropics/skills`

---

## 🏗️ Proposed Architecture

### **Phase 1: MCP Tools for Environment Awareness**

Create MCP tools that Flow Architect can use to discover environment state:

#### **Tool 1: `get_running_services`**
```typescript
{
  name: "get_running_services",
  description: "Get all running Docker services on the VPS",
  inputSchema: {
    type: "object",
    properties: {
      category: { type: "string", enum: ["all", "database", "web-server", "queue", "search"] }
    }
  }
}
// Calls: http://localhost:3000/api/services
// Filters by status === "running"
```

#### **Tool 2: `get_available_services`**
```typescript
{
  name: "get_available_services",
  description: "Get all installable services from catalog",
  inputSchema: {
    type: "object",
    properties: {
      category: { type: "string" },
      installed: { type: "boolean" }
    }
  }
}
// Calls: http://localhost:3000/api/services
// Returns hardcoded installable services
```

#### **Tool 3: `get_node_catalog`**
```typescript
{
  name: "get_node_catalog",
  description: "Get all available node types with operations",
  inputSchema: {
    type: "object",
    properties: {
      authRequired: { type: "boolean" },
      category: { type: "string" }
    }
  }
}
// Calls: http://localhost:3000/api/nodes
// Returns 129 nodes with 3,364 operations
```

#### **Tool 4: `check_node_auth`**
```typescript
{
  name: "check_node_auth",
  description: "Check if node authentication is configured",
  inputSchema: {
    type: "object",
    properties: {
      nodeType: { type: "string", required: true }
    }
  }
}
// Calls: http://localhost:3000/api/nodes/[nodeType]/auth
// Returns: 200 if configured, 404 if not
```

#### **Tool 5: `get_deployed_flows`**
```typescript
{
  name: "get_deployed_flows",
  description: "Get all deployed ACT flows with their endpoints",
  inputSchema: {
    type: "object",
    properties: {
      status: { type: "string", enum: ["running", "stopped", "available"] }
    }
  }
}
// Calls: http://localhost:3000/api/catalog
// Returns flow services with endpoints and capabilities
```

#### **Tool 6: `get_unified_environment`**
```typescript
{
  name: "get_unified_environment",
  description: "Get complete environment snapshot (services + nodes + flows)",
  inputSchema: {
    type: "object",
    properties: {}
  }
}
// Calls: http://localhost:3000/api/unified
// Returns complete unified catalog
```

#### **Tool 7: `check_service_auth`**
```typescript
{
  name: "check_service_auth",
  description: "Check if service authentication is configured",
  inputSchema: {
    type: "object",
    properties: {
      serviceId: { type: "string", required: true }
    }
  }
}
// Calls: http://localhost:3000/api/services/[serviceId]/auth
// Returns: 200 if configured, 404 if not
```

#### **Tool 8: `get_available_port`**
```typescript
{
  name: "get_available_port",
  description: "Get next available port for new flow service",
  inputSchema: {
    type: "object",
    properties: {}
  }
}
// Calls: http://localhost:3000/api/ports
// Returns: available port (9001+)
```

---

### **Phase 2: Skills for Flow Architect Context**

Create Skills that give Flow Architect specialized knowledge:

#### **Skill 1: `infrastructure-services`**

**Location:** `~/.claude/skills/infrastructure-services/SKILL.md`

```yaml
---
name: infrastructure-services
description: Knowledge about VPS infrastructure services (databases, queues, etc.)
version: 1.0.0
---

# Infrastructure Services Skill

This skill provides knowledge about infrastructure services available on the VPS.

## Available Services

Query services using the MCP tool: `get_running_services` or `get_available_services`

## Service Categories

- **Databases**: PostgreSQL, MySQL, MariaDB, MongoDB, Redis, Neo4j, CouchDB, etc.
- **Web Servers**: Nginx, Apache
- **Message Queues**: RabbitMQ, Kafka
- **Search Engines**: Elasticsearch
- **Tools**: phpMyAdmin, Adminer

## Authentication

Before using any service in a flow:
1. Check if service is running: `get_running_services`
2. Check if auth is configured: `check_service_auth`
3. If not configured: Direct user to Security Center

## Connection Strings

Services provide `defaultCredentials` with:
- `username`
- `password`
- `port`

Build connection string:
```
postgresql://{username}:{password}@localhost:{port}/database
```
```

#### **Skill 2: `node-catalog`**

**Location:** `~/.claude/skills/node-catalog/SKILL.md`

```yaml
---
name: node-catalog
description: Knowledge about ACT node types and their capabilities
version: 1.0.0
---

# Node Catalog Skill

This skill provides knowledge about ACT node types available for building flows.

## Node Discovery

Use MCP tool: `get_node_catalog` to get all 129 node types with 3,364 operations.

## Node Categories

- **Python Execution**: `py` - Execute Python code
- **Database**: `neon`, `pg`, `mysql`, `mongo` - Database operations
- **HTTP**: `http`, `axios` - HTTP requests
- **API Creation**: `aci` - Create API endpoints
- **Timer**: `cron`, `timer` - Scheduled execution
- **Email**: `sendgrid`, `smtp` - Email sending
- **And 120+ more...**

## Authentication-Required Nodes

Check using: `get_node_catalog(authRequired: true)`

Common auth-required nodes:
- GitHub (`github`)
- OpenAI (`openai`)
- Slack (`slack`)
- SendGrid (`sendgrid`)
- Stripe (`stripe`)
- And more...

## Before Using Auth-Required Nodes

1. Check auth status: `check_node_auth(nodeType: "github")`
2. If 404: Direct user to Security Center to configure
3. If 200: Proceed with flow creation

## Node Operations

Each node has multiple operations. Get them with:
`get_node_catalog` → find node → check `operations` array

Example: `github` node has operations for:
- `create_issue`
- `create_pr`
- `get_repo`
- `list_issues`
- And more...
```

#### **Skill 3: `flow-services`**

**Location:** `~/.claude/skills/flow-services/SKILL.md`

```yaml
---
name: flow-services
description: Knowledge about deployed ACT flow services
version: 1.0.0
---

# Flow Services Skill

This skill provides knowledge about ACT flows deployed on the VPS.

## Flow Discovery

Use MCP tool: `get_deployed_flows` to get all deployed flows.

## Flow Types

Flows are persistent services that:
- Expose API endpoints
- Run scheduled tasks
- Process data continuously
- Integrate multiple services

## Flow Information

Each flow provides:
- **ID**: Unique identifier
- **Name**: Human-readable name
- **Status**: running | stopped | available
- **Connection**: Host, port, connection string
- **Capabilities**: What the flow can do
- **Endpoints**: API routes exposed

## Endpoint Format

```json
{
  "path": "/api/quotes",
  "method": "GET",
  "description": "Get all quotes"
}
```

## Using Flows in New Flows

You can call other flows as HTTP services:

```toml
[node:CallQuotesAPI]
type = http
url = http://localhost:9001/api/quotes
method = GET
```

## Port Management

- Flows use ports 9001, 9002, 9003, etc.
- Get next available: `get_available_port`
- Never hardcode ports
```

#### **Skill 4: `security-center`**

**Location:** `~/.claude/skills/security-center/SKILL.md`

```yaml
---
name: security-center
description: Knowledge about authentication management
version: 1.0.0
---

# Security Center Skill

This skill provides knowledge about the Security Center and authentication.

## What is Security Center?

Security Center manages authentication for:
- Infrastructure services (PostgreSQL, MySQL, etc.)
- API nodes (GitHub, OpenAI, Slack, etc.)

## When to Direct User to Security Center

**Before creating any flow that uses:**
1. Database services (check: `check_service_auth`)
2. Auth-required nodes (check: `check_node_auth`)

**If auth not configured:**
```
⚠️ PostgreSQL requires authentication.
Please open Security Center from the dock to configure credentials.
```

## Checking Auth Status

**For Services:**
```typescript
check_service_auth(serviceId: "postgresql")
// 200 = configured
// 404 = not configured
```

**For Nodes:**
```typescript
check_node_auth(nodeType: "github")
// 200 = configured
// 404 = not configured
```

## Authentication Storage

- Credentials stored encrypted (AES-256-CBC)
- User-specific (different users have different creds)
- API endpoints: `/api/services/[id]/auth` and `/api/nodes/[type]/auth`

## Never Show Credentials

Do NOT include actual passwords/tokens in flow files.
Use parameter references: `{{.Parameter.connection_string}}`
```

---

### **Phase 3: Update Flow Architect Contexts**

Update all context files to use MCP tools instead of direct API calls:

#### **Current (Wrong):**
```markdown
curl -s http://localhost:3000/api/catalog?type=infrastructure&status=running
```

#### **New (Correct with MCP Tools):**
```markdown
Use MCP tool: `get_running_services(category: "database")`

This will return only running database services.
```

#### **Files to Update:**

1. `flow-architect/.claude/agents/flow-architect.md`
2. `flow-architect/.claude/instructions/contexts/simple-api.md`
3. `flow-architect/.claude/instructions/contexts/complex-api.md`
4. `flow-architect/.claude/instructions/contexts/full-application.md`
5. `flow-architect/.claude/instructions/contexts/multi-service-integration.md`
6. `flow-architect/.claude/instructions/contexts/scheduled-task.md`

---

### **Phase 4: Create Custom Slash Commands**

Create reusable commands for common Flow Architect tasks:

#### **Command 1: `/check-env`**

**File:** `.claude/commands/check-env.md`

```markdown
# Check Environment

Check the complete VPS environment including:
1. Running services
2. Available nodes
3. Deployed flows
4. Authentication status

Use the MCP tool `get_unified_environment` to get a complete snapshot.
```

#### **Command 2: `/verify-auth`**

**File:** `.claude/commands/verify-auth.md`

```markdown
# Verify Authentication

Before building a flow, verify that all required services and nodes have authentication configured.

Steps:
1. Identify services needed (e.g., postgresql, mysql)
2. Check each: `check_service_auth(serviceId: "postgresql")`
3. Identify nodes needed (e.g., github, openai)
4. Check each: `check_node_auth(nodeType: "github")`
5. Report any missing auth to user
```

#### **Command 3: `/discover-flows`**

**File:** `.claude/commands/discover-flows.md`

```markdown
# Discover Flows

Get all deployed ACT flows with their endpoints and capabilities.

Use: `get_deployed_flows(status: "running")`

Show user:
- Flow names
- Ports
- Endpoints
- Status
```

---

## 🛠️ Implementation Plan

### **Step 1: Create MCP Tools** (Priority: HIGH)

**Location:** `.claude/mcp/tools/`

Create 8 MCP tools:
1. ✅ `get_running_services.ts`
2. ✅ `get_available_services.ts`
3. ✅ `get_node_catalog.ts`
4. ✅ `check_node_auth.ts`
5. ✅ `get_deployed_flows.ts`
6. ✅ `get_unified_environment.ts`
7. ✅ `check_service_auth.ts`
8. ✅ `get_available_port.ts`

**Implementation:**
```typescript
// Example: .claude/mcp/tools/get_running_services.ts
export const getRunningServices = {
  name: "get_running_services",
  description: "Get all running Docker services on the VPS",
  inputSchema: {
    type: "object",
    properties: {
      category: {
        type: "string",
        enum: ["all", "database", "web-server", "queue", "search"],
        description: "Filter by service category"
      }
    }
  },
  handler: async (args: { category?: string }) => {
    const response = await fetch('http://localhost:3000/api/services');
    const data = await response.json();

    let services = data.services.filter((s: any) => s.status === 'running');

    if (args.category && args.category !== 'all') {
      services = services.filter((s: any) => s.category === args.category);
    }

    return {
      content: [{
        type: "text",
        text: JSON.stringify(services, null, 2)
      }]
    };
  }
};
```

### **Step 2: Create Skills** (Priority: HIGH)

**Location:** `~/.claude/skills/`

Create 4 skills:
1. ✅ `infrastructure-services/SKILL.md`
2. ✅ `node-catalog/SKILL.md`
3. ✅ `flow-services/SKILL.md`
4. ✅ `security-center/SKILL.md`

### **Step 3: Update Flow Architect Contexts** (Priority: MEDIUM)

**Files to update:** (6 files)
1. ✅ `flow-architect/.claude/agents/flow-architect.md`
2. ✅ `contexts/simple-api.md`
3. ✅ `contexts/complex-api.md`
4. ✅ `contexts/full-application.md`
5. ✅ `contexts/multi-service-integration.md`
6. ✅ `contexts/scheduled-task.md`

**Changes:**
- Replace `curl` commands with MCP tool calls
- Add authentication verification steps
- Update API endpoint references
- Add Security Center guidance

### **Step 4: Create Slash Commands** (Priority: LOW)

**Location:** `.claude/commands/`

Create 3 commands:
1. ✅ `check-env.md`
2. ✅ `verify-auth.md`
3. ✅ `discover-flows.md`

### **Step 5: Test Complete Awareness** (Priority: HIGH)

**Test Scenarios:**

1. **Service Discovery:**
   - Agent should know what services are running
   - Agent should know what services can be installed
   - Agent should direct to Service Manager for installation

2. **Node Awareness:**
   - Agent should know all 129 node types
   - Agent should know which need authentication
   - Agent should direct to Security Center for auth setup

3. **Flow Discovery:**
   - Agent should know deployed flows and their endpoints
   - Agent should be able to reference flows in new flows
   - Agent should assign correct ports

4. **Authentication:**
   - Agent should check auth before building flows
   - Agent should direct to Security Center when needed
   - Agent should never proceed without auth

---

## 📋 Checklist

### **Research** ✅
- [x] Claude Code best practices
- [x] MCP architecture and tools
- [x] Skills feature and structure
- [x] API mapping

### **Design** 🔄
- [ ] MCP tools architecture
- [ ] Skills content structure
- [ ] Context update strategy
- [ ] Testing plan

### **Implementation** ⏳
- [ ] Create 8 MCP tools
- [ ] Create 4 Skills
- [ ] Update 6 context files
- [ ] Create 3 slash commands
- [ ] Test complete awareness

### **Validation** ⏳
- [ ] Service discovery works
- [ ] Node awareness works
- [ ] Flow discovery works
- [ ] Authentication checks work
- [ ] No hardcoded values
- [ ] All contexts use tools

---

## 🎯 Success Criteria

Flow Architect agent should be able to:

1. ✅ **Know running services** without hardcoding
2. ✅ **Know available services** from hardcoded list
3. ✅ **Know all node types** and their operations
4. ✅ **Check authentication** before building flows
5. ✅ **Discover deployed flows** and their endpoints
6. ✅ **Get available ports** dynamically
7. ✅ **Direct users to Security Center** when auth needed
8. ✅ **Direct users to Service Manager** when service install needed
9. ✅ **Build flows** using actual connection strings from API
10. ✅ **Reference other flows** as services in new flows

---

## 📚 References

- **MCP Docs**: https://docs.anthropic.com/en/docs/agents-and-tools/mcp
- **Skills Repo**: https://github.com/anthropics/skills
- **Claude Code Best Practices**: https://www.anthropic.com/engineering/claude-code-best-practices
- **Skills Documentation**: https://support.claude.com/en/articles/12512176-what-are-skills

---

**Created:** 2025-10-20
**Status:** Planning Phase
**Next Step:** Create MCP Tools
