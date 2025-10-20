# Unified Catalog & Security Center - Complete Plan

## 🎯 Core Concept

**Problem:** Flow Architect has access to ALL 129 nodes, but user may not have authenticated them yet.

**Solution:**
1. **Security Center** - UI where user manages authentication for nodes/services
2. **Unified Catalog** - Single API that combines services + nodes + flows, filtered by what user enabled
3. **Flow Architect** - Uses unified catalog, only sees what user authenticated

## 📊 Current State

### Three Separate Catalogs:

1. **Services Catalog** (`/api/catalog`)
   - Docker services (PostgreSQL, MongoDB, Redis, etc.)
   - Status: running/stopped
   - Connection strings

2. **Nodes Catalog** (`/api/nodes`)
   - 129 ACT nodes
   - Operations, parameters
   - Some require authentication

3. **Flows Catalog** (`/api/catalog/flows`)
   - User-created flows
   - Deployed services from flows

## 🏗️ New Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DESKTOP APP (Port 80)                   │
│                  Accessed via VPS IP from web               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌─────────────────┐   ┌──────────────┐
│    Services   │    │ Security Center │   │ Flow Manager │
│    Manager    │    │   (NEW!)        │   │              │
│               │    │                 │   │              │
│ Install/run   │    │ Manage auth for │   │ View/manage  │
│ Docker svcs   │    │ nodes & services│   │ flows        │
└───────────────┘    └─────────────────┘   └──────────────┘
                              │
                              │ Reads/Writes
                              ▼
                    ┌─────────────────┐
                    │  User Preferences│
                    │   Database       │
                    │  - Enabled nodes │
                    │  - Auth tokens   │
                    │  - Connections   │
                    └─────────────────┘
                              │
                              │ Used by
                              ▼
                    ┌─────────────────┐
                    │ Unified Catalog │
                    │      API        │
                    │ /api/unified    │
                    └─────────────────┘
                              │
                              │ Used by
                              ▼
                    ┌─────────────────┐
                    │ Flow Architect  │
                    │     Agent       │
                    │ Only sees what  │
                    │ user enabled    │
                    └─────────────────┘
```

## 🔐 Security Center (New Feature)

### Purpose
Central place where user manages authentication for all services and nodes.

### Features

#### 1. Docker Services Section
```
╔════════════════════════════════════════════════╗
║  DOCKER SERVICES                               ║
╠════════════════════════════════════════════════╣
║                                                ║
║  🟢 PostgreSQL (neon-postgres-primary)        ║
║     Status: Running                            ║
║     Connection: postgresql://user:pass@...    ║
║     [👁️ Show] [📋 Copy] [🔄 Restart]          ║
║                                                ║
║  🟢 Redis (redis-cache)                        ║
║     Status: Running                            ║
║     Connection: redis://localhost:6379         ║
║     [👁️ Show] [📋 Copy] [🔄 Restart]          ║
║                                                ║
║  🔴 MongoDB (mongodb-local)                    ║
║     Status: Stopped                            ║
║     [▶️ Start]                                 ║
║                                                ║
╚════════════════════════════════════════════════╝
```

#### 2. Nodes Requiring Authentication Section
```
╔════════════════════════════════════════════════╗
║  NODES REQUIRING AUTHENTICATION                ║
╠════════════════════════════════════════════════╣
║                                                ║
║  ✅ OpenAI                                     ║
║     Status: Enabled                            ║
║     API Key: sk-***************                ║
║     [✏️ Edit] [🗑️ Remove]                     ║
║                                                ║
║  ❌ SendGrid (Email)                           ║
║     Status: Not Configured                     ║
║     [➕ Add API Key]                           ║
║                                                ║
║  ✅ MongoDB                                     ║
║     Status: Enabled                            ║
║     Connection: mongodb://***                  ║
║     [✏️ Edit] [🗑️ Remove]                     ║
║                                                ║
║  ❌ Slack                                       ║
║     Status: Not Configured                     ║
║     [➕ Add Webhook]                           ║
║                                                ║
╚════════════════════════════════════════════════╝
```

#### 3. Add Authentication Form
```
┌────────────────────────────────────────┐
│  Add Authentication for: OpenAI        │
├────────────────────────────────────────┤
│                                        │
│  Node Type: openai                     │
│  Operations: 15 available              │
│                                        │
│  Required Fields:                      │
│  ┌──────────────────────────────────┐ │
│  │ API Key                          │ │
│  │ sk-**************************   │ │
│  └──────────────────────────────────┘ │
│                                        │
│  Optional:                             │
│  ┌──────────────────────────────────┐ │
│  │ Organization ID (optional)       │ │
│  │                                  │ │
│  └──────────────────────────────────┘ │
│                                        │
│  [Test Connection] [Save] [Cancel]    │
│                                        │
└────────────────────────────────────────┘
```

## 💾 User Preferences Database

Store user's enabled nodes and authentication.

### Schema

```typescript
// Table: user_node_auth
interface UserNodeAuth {
  id: string;
  userId: string;  // For multi-user support later
  nodeType: string; // "openai", "sendgrid", etc.
  enabled: boolean;
  authData: {
    // Encrypted JSON with auth fields
    api_key?: string;
    token?: string;
    connection_string?: string;
    // ... any auth fields node needs
  };
  createdAt: Date;
  updatedAt: Date;
  lastTested?: Date; // When user last tested connection
  testResult?: boolean; // Did test pass?
}

// Table: user_preferences
interface UserPreferences {
  userId: string;
  settings: {
    showAllNodes: boolean; // Debug mode: show all nodes even if not auth'd
    autoEnableDockerServices: boolean; // Auto-enable services when started
  };
}
```

### Storage Options

**Option 1: SQLite (Recommended)**
- Simple, file-based
- No external database needed
- Perfect for single-user desktop app

**Option 2: JSON File**
- Simplest
- Good for prototype
- `/data/user-preferences.json`

**Option 3: PostgreSQL**
- If already using for other data
- Overkill for preferences

**Recommendation: Start with SQLite**

## 🔗 New API Endpoints

### 1. Get Unified Catalog
```bash
GET /api/unified

Response:
{
  "services": [
    {
      "id": "postgres",
      "type": "docker",
      "status": "running",
      "connection": "postgresql://...",
      "enabled": true
    }
  ],
  "nodes": [
    {
      "id": "openai",
      "type": "node",
      "operations": 15,
      "enabled": true,
      "authenticated": true
    },
    {
      "id": "sendgrid",
      "type": "node",
      "operations": 8,
      "enabled": false,
      "authenticated": false
    }
  ],
  "flows": [
    {
      "id": "clinic-management",
      "type": "flow",
      "status": "running",
      "endpoints": [...]
    }
  ]
}
```

### 2. Get Nodes Requiring Auth
```bash
GET /api/nodes/require-auth

Response:
{
  "nodes": [
    {
      "id": "openai",
      "displayName": "OpenAI",
      "authenticated": true,
      "authFields": [
        {
          "name": "api_key",
          "type": "secret",
          "required": true,
          "description": "OpenAI API key from platform.openai.com"
        }
      ]
    },
    {
      "id": "sendgrid",
      "displayName": "SendGrid",
      "authenticated": false,
      "authFields": [...]
    }
  ]
}
```

### 3. Enable Node with Auth
```bash
POST /api/nodes/{nodeType}/auth

Body:
{
  "authData": {
    "api_key": "sk-****"
  }
}

Response:
{
  "success": true,
  "nodeType": "openai",
  "enabled": true,
  "testResult": true // Connection tested successfully
}
```

### 4. Disable Node
```bash
DELETE /api/nodes/{nodeType}/auth

Response:
{
  "success": true,
  "nodeType": "openai",
  "enabled": false
}
```

### 5. Test Node Connection
```bash
POST /api/nodes/{nodeType}/test

Body:
{
  "authData": {
    "api_key": "sk-****"
  }
}

Response:
{
  "success": true,
  "message": "Connection successful",
  "details": {
    "organization": "org-****",
    "available_models": ["gpt-4", "gpt-3.5-turbo"]
  }
}
```

### 6. Get All Connection Strings (Docker Services)
```bash
GET /api/services/connections

Response:
{
  "services": [
    {
      "id": "postgres",
      "name": "PostgreSQL",
      "status": "running",
      "connection": "postgresql://user:pass@localhost:5432/db",
      "masked": "postgresql://user:***@localhost:5432/db"
    }
  ]
}
```

## 🔄 Flow Architect Integration

### Before (Current)
```markdown
Flow Architect checks:
1. /api/catalog - Services
2. /api/nodes - ALL 129 nodes
3. /api/catalog/flows - Flows

Problem: Sees ALL nodes even if user hasn't authenticated
```

### After (New)
```markdown
Flow Architect checks:
1. /api/unified - Single endpoint with everything user has enabled

Response:
{
  "services": [...only running services...],
  "nodes": [...only authenticated nodes...],
  "flows": [...all flows...]
}

Flow Architect only builds workflows with what's available!
```

### Updated Flow Architect Instructions
```markdown
## Step 3: Check Available Resources

**Single API call:**
```bash
curl -s http://localhost:3000/api/unified
```

**Response contains:**
- **services**: Running Docker services (databases, caches, etc.)
- **nodes**: Nodes user has authenticated (OpenAI, SendGrid, etc.)
- **flows**: Deployed flow services

**IMPORTANT:**
- Only use nodes that appear in unified catalog
- If user hasn't authenticated a node, don't use it
- Suggest to user: "To use [node], please add authentication in Security Center"
```

## 🎨 Security Center UI

### Page: `/security-center`

```typescript
// components/security-center/SecurityCenter.tsx

export default function SecurityCenter() {
  return (
    <div className="security-center">
      <h1>Security Center</h1>

      {/* Docker Services Section */}
      <section className="docker-services">
        <h2>Docker Services</h2>
        <ServicesList />
      </section>

      {/* Nodes Authentication Section */}
      <section className="nodes-auth">
        <h2>Nodes Requiring Authentication</h2>
        <NodesAuthList />
      </section>

      {/* Quick Stats */}
      <section className="stats">
        <div className="stat">
          <span>Enabled Nodes</span>
          <strong>12 / 129</strong>
        </div>
        <div className="stat">
          <span>Running Services</span>
          <strong>3 / 5</strong>
        </div>
      </section>
    </div>
  );
}
```

### Components Needed

1. **ServicesList** - Show Docker services with connections
2. **NodesAuthList** - Show nodes requiring auth
3. **AddAuthModal** - Form to add authentication
4. **TestConnectionButton** - Test if auth works
5. **ConnectionStringDisplay** - Show/hide connection strings

## 📦 Implementation Phases

### Phase 1: Database Setup (2 hours)
- [ ] Create SQLite database schema
- [ ] Create migration for user_node_auth table
- [ ] Create helper functions for CRUD operations
- [ ] Add encryption for auth data

### Phase 2: API Endpoints (4 hours)
- [ ] GET /api/nodes/require-auth
- [ ] POST /api/nodes/{nodeType}/auth
- [ ] DELETE /api/nodes/{nodeType}/auth
- [ ] POST /api/nodes/{nodeType}/test
- [ ] GET /api/services/connections
- [ ] GET /api/unified

### Phase 3: Security Center UI (6 hours)
- [ ] Create /security-center page
- [ ] Build ServicesList component
- [ ] Build NodesAuthList component
- [ ] Build AddAuthModal component
- [ ] Add connection testing
- [ ] Add copy-to-clipboard for connections

### Phase 4: Flow Architect Integration (2 hours)
- [ ] Update Flow Architect to use /api/unified
- [ ] Add logic to suggest enabling nodes
- [ ] Update context files to reference unified catalog

### Phase 5: Testing (2 hours)
- [ ] Test enabling/disabling nodes
- [ ] Test connection testing
- [ ] Test Flow Architect with limited nodes
- [ ] Test unified catalog filtering

**Total: ~16 hours**

## 🔐 Security Considerations

### 1. Encryption
```typescript
import crypto from 'crypto';

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY; // 32 bytes

function encrypt(text: string): string {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', ENCRYPTION_KEY, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

function decrypt(text: string): string {
  const parts = text.split(':');
  const iv = Buffer.from(parts[0], 'hex');
  const encrypted = parts[1];
  const decipher = crypto.createDecipheriv('aes-256-cbc', ENCRYPTION_KEY, iv);
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}
```

### 2. Connection String Masking
```typescript
function maskConnectionString(conn: string): string {
  // postgresql://user:password@host:5432/db
  // -> postgresql://user:***@host:5432/db
  return conn.replace(/:([^@]+)@/, ':***@');
}
```

### 3. API Key Masking
```typescript
function maskApiKey(key: string): string {
  // sk-1234567890abcdef
  // -> sk-***************
  if (key.length <= 10) return '***';
  return key.substring(0, 3) + '*'.repeat(key.length - 6) + key.substring(key.length - 3);
}
```

## 📊 Example Flow

### User Wants to Use OpenAI

1. **User visits Security Center**
2. **Sees "OpenAI - Not Configured"**
3. **Clicks "Add API Key"**
4. **Modal opens with form**
5. **User enters API key**
6. **Clicks "Test Connection"**
7. **System calls POST /api/nodes/openai/test**
8. **Test succeeds, shows available models**
9. **User clicks "Save"**
10. **System calls POST /api/nodes/openai/auth**
11. **API key encrypted and stored in database**
12. **OpenAI now appears in unified catalog**
13. **Flow Architect can now use OpenAI nodes**

## 🎯 Benefits

1. **User Control**: User decides what's enabled
2. **Security**: Auth tokens encrypted, masked in UI
3. **Simplicity**: One unified catalog for Flow Architect
4. **Clarity**: Clear view of what's configured
5. **Testing**: Test connections before saving
6. **Management**: Easy enable/disable of nodes
7. **Discovery**: See all nodes requiring auth

## 📝 Database Schema (SQLite)

```sql
-- User node authentication
CREATE TABLE user_node_auth (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL DEFAULT 'default',
  node_type TEXT NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT 1,
  auth_data TEXT NOT NULL, -- Encrypted JSON
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_tested DATETIME,
  test_result BOOLEAN,
  UNIQUE(user_id, node_type)
);

-- User preferences
CREATE TABLE user_preferences (
  user_id TEXT PRIMARY KEY DEFAULT 'default',
  show_all_nodes BOOLEAN DEFAULT 0,
  auto_enable_docker_services BOOLEAN DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_user_node_auth_enabled ON user_node_auth(enabled);
CREATE INDEX idx_user_node_auth_user ON user_node_auth(user_id);
```

## 🚀 Quick Start After Implementation

```bash
# 1. User visits Security Center
open http://localhost:80/security-center

# 2. Add OpenAI authentication
# (via UI)

# 3. Flow Architect now sees OpenAI in unified catalog
curl http://localhost:3000/api/unified | jq '.nodes[] | select(.id == "openai")'

# 4. User can now ask agent to use OpenAI
"Generate an image using DALL-E"
# Agent checks unified catalog, sees OpenAI enabled, builds flow
```

---

**Status:** Ready to Implement
**Priority:** High (Core security feature)
**Time Estimate:** 16 hours
**Dependencies:** SQLite, Crypto module, Node catalog
