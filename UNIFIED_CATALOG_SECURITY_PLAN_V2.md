# Unified Catalog & Security Center - Revised Plan (Dynamic Auth Extraction)

## 🎯 You're Right!

We need to **dynamically extract** what authentication each node needs from the actual Python files, not hardcode it.

## 📊 Two Node Patterns Discovered

### Pattern 1: Universal Request Nodes (Easy to Parse!)
**Example:** OpenAI, SendGrid, Slack, most API integrations

```python
class OpenAINode(BaseNode):
    CONFIG = {
        "node_info": {
            "name": "openai",
            "display_name": "OpenAI",
        },
        "api_config": {
            "authentication": {
                "type": "bearer_token",  # ← Auth type!
                "header": "Authorization"
            }
        },
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "OpenAI API key",
                "required": True,
                "sensitive": True,  # ← This is auth!
                "group": "Authentication",
                "validation": {
                    "pattern": "^sk-[a-zA-Z0-9-_]+$"
                }
            }
        }
    }
```

**What we extract:**
- Auth type: `bearer_token`
- Auth fields: `api_key` (marked `sensitive: True`)
- Validation rules: Pattern, required, etc.

### Pattern 2: SDK Nodes (NodeParameter pattern)
**Example:** MongoDB, PostgreSQL, Redis

```python
def get_schema(self) -> NodeSchema:
    return NodeSchema(
        node_type="mongodb",
        parameters=[
            NodeParameter(
                name="connection_string",
                type=NodeParameterType.SECRET,  # ← This is auth!
                description="MongoDB connection string",
                required=False
            ),
            NodeParameter(
                name="password",
                type=NodeParameterType.SECRET,  # ← This is auth!
                description="MongoDB password",
                required=False
            )
        ]
    )
```

**What we extract:**
- Auth fields: Any parameter with `NodeParameterType.SECRET`
- Or parameters with names like: `password`, `token`, `key`, `credential`

## 🔧 Enhanced Node Parser

We already have `lib/node-parser.ts`. Now we enhance it to extract auth requirements.

### New Function: `extractAuthRequirements()`

```typescript
// lib/node-parser.ts

interface AuthRequirement {
  field: string;
  type: 'string' | 'secret' | 'object';
  description: string;
  required: boolean;
  pattern?: string;
  example?: string;
  sensitive: boolean;
}

interface NodeAuthInfo {
  requiresAuth: boolean;
  authType?: 'bearer_token' | 'api_key' | 'basic_auth' | 'connection_string' | 'custom';
  authFields: AuthRequirement[];
}

function extractAuthRequirements(content: string): NodeAuthInfo {
  const authFields: AuthRequirement[] = [];
  let authType: string | undefined;

  // Pattern 1: Universal Request Node CONFIG
  const configMatch = content.match(/CONFIG\s*=\s*{([\s\S]*?)^\s*}/m);
  if (configMatch) {
    const configBlock = configMatch[1];

    // Extract auth type
    const authTypeMatch = configBlock.match(/"type":\s*"([^"]+)"/);
    if (authTypeMatch) {
      authType = authTypeMatch[1];
    }

    // Extract parameters with "sensitive": True
    const paramRegex = /"([^"]+)":\s*{([^}]+?"sensitive":\s*True[^}]+)}/g;
    let match;

    while ((match = paramRegex.exec(configBlock)) !== null) {
      const fieldName = match[1];
      const fieldBlock = match[2];

      const descMatch = fieldBlock.match(/"description":\s*"([^"]+)"/);
      const requiredMatch = fieldBlock.match(/"required":\s*(True|False)/);
      const patternMatch = fieldBlock.match(/"pattern":\s*"([^"]+)"/);

      authFields.push({
        field: fieldName,
        type: 'secret',
        description: descMatch ? descMatch[1] : `${fieldName} for authentication`,
        required: requiredMatch ? requiredMatch[1] === 'True' : false,
        pattern: patternMatch ? patternMatch[1] : undefined,
        sensitive: true
      });
    }
  }

  // Pattern 2: NodeParameter with SECRET type
  const secretParamRegex = /NodeParameter\s*\(\s*name\s*=\s*["']([^"']+)["'][^)]*type\s*=\s*NodeParameterType\.SECRET/g;
  let secretMatch;

  while ((secretMatch = secretParamRegex.exec(content)) !== null) {
    const fieldName = secretMatch[1];

    // Try to find description for this parameter
    const paramBlock = content.substring(secretMatch.index, secretMatch.index + 500);
    const descMatch = paramBlock.match(/description\s*=\s*["']([^"']+)["']/);

    authFields.push({
      field: fieldName,
      type: 'secret',
      description: descMatch ? descMatch[1] : `${fieldName} for authentication`,
      required: false,
      sensitive: true
    });
  }

  // Also look for common auth parameter names (even if not marked SECRET)
  const commonAuthParams = ['api_key', 'token', 'password', 'secret', 'credential', 'auth_token'];
  const nodeParamRegex = /NodeParameter\s*\(\s*name\s*=\s*["']([^"']+)["'][^)]+\)/g;
  let paramMatch;

  while ((paramMatch = nodeParamRegex.exec(content)) !== null) {
    const fieldName = paramMatch[1];
    if (commonAuthParams.some(auth => fieldName.toLowerCase().includes(auth))) {
      // Check if we already added this field
      if (!authFields.find(f => f.field === fieldName)) {
        const paramBlock = content.substring(paramMatch.index, paramMatch.index + 500);
        const descMatch = paramBlock.match(/description\s*=\s*["']([^"']+)["']/);

        authFields.push({
          field: fieldName,
          type: 'secret',
          description: descMatch ? descMatch[1] : `${fieldName} for authentication`,
          required: false,
          sensitive: true
        });
      }
    }
  }

  return {
    requiresAuth: authFields.length > 0,
    authType: authType as any,
    authFields
  };
}
```

### Update `parseNode()` to Include Auth Info

```typescript
function parseNode(content: string, filename: string): NodeInfo {
  // ... existing code ...

  const authInfo = extractAuthRequirements(content);

  return {
    id,
    displayName,
    // ... existing fields ...
    authInfo,  // ← New field!
    capabilities: {
      ...capabilities,
      requiresAuth: authInfo.requiresAuth  // ← Update this
    }
  };
}
```

## 🔗 New API Endpoints

### 1. Get Nodes Requiring Auth (with extracted fields!)
```bash
GET /api/nodes/auth-required

Response:
{
  "nodes": [
    {
      "id": "openai",
      "displayName": "OpenAI",
      "authInfo": {
        "requiresAuth": true,
        "authType": "bearer_token",
        "authFields": [
          {
            "field": "api_key",
            "type": "secret",
            "description": "OpenAI API key",
            "required": true,
            "pattern": "^sk-[a-zA-Z0-9-_]+$",
            "sensitive": true
          }
        ]
      },
      "userEnabled": false
    },
    {
      "id": "mongodb",
      "displayName": "MongoDB",
      "authInfo": {
        "requiresAuth": true,
        "authType": "connection_string",
        "authFields": [
          {
            "field": "connection_string",
            "type": "secret",
            "description": "MongoDB connection string",
            "required": false,
            "sensitive": true
          },
          {
            "field": "password",
            "type": "secret",
            "description": "MongoDB password",
            "required": false,
            "sensitive": true
          }
        ]
      },
      "userEnabled": false
    }
  ]
}
```

### 2. Get Auth Requirements for Single Node
```bash
GET /api/nodes/{nodeType}/auth-info

# Example:
curl http://localhost:3000/api/nodes/openai/auth-info

Response:
{
  "nodeType": "openai",
  "displayName": "OpenAI",
  "authInfo": {
    "requiresAuth": true,
    "authType": "bearer_token",
    "authFields": [
      {
        "field": "api_key",
        "type": "secret",
        "description": "OpenAI API key from platform.openai.com",
        "required": true,
        "pattern": "^sk-[a-zA-Z0-9-_]+$",
        "sensitive": true,
        "example": "sk-proj-****"
      }
    ]
  },
  "documentation": "https://platform.openai.com/docs/api-reference",
  "howToGetAuth": "Go to platform.openai.com → API Keys → Create new key"
}
```

## 🎨 Security Center - Dynamic Form Generation

The form is generated **dynamically** based on extracted auth fields!

```tsx
// components/security-center/AddAuthModal.tsx

interface AddAuthModalProps {
  nodeType: string;
  authInfo: NodeAuthInfo;
  onSave: (authData: Record<string, string>) => void;
}

export function AddAuthModal({ nodeType, authInfo, onSave }: AddAuthModalProps) {
  const [formData, setFormData] = useState<Record<string, string>>({});

  return (
    <Modal>
      <h2>Add Authentication: {nodeType}</h2>

      {/* Dynamically generated form fields */}
      {authInfo.authFields.map(field => (
        <div key={field.field} className="form-field">
          <label>{field.description || field.field}</label>

          {field.type === 'secret' ? (
            <input
              type="password"
              value={formData[field.field] || ''}
              onChange={(e) => setFormData({
                ...formData,
                [field.field]: e.target.value
              })}
              required={field.required}
              pattern={field.pattern}
              placeholder={field.example}
            />
          ) : (
            <input
              type="text"
              value={formData[field.field] || ''}
              onChange={(e) => setFormData({
                ...formData,
                [field.field]: e.target.value
              })}
              required={field.required}
            />
          )}

          {field.pattern && (
            <small>Format: {field.pattern}</small>
          )}
        </div>
      ))}

      <button onClick={() => onSave(formData)}>
        Save & Test
      </button>
    </Modal>
  );
}
```

## 🔄 Complete Flow

### 1. System Discovers Nodes
```
Node Parser reads 129 Python files
  ↓
Extracts operations, parameters
  ↓
Extracts auth requirements (NEW!)
  ↓
Stores in catalog with authInfo
```

### 2. User Visits Security Center
```
GET /api/nodes/auth-required
  ↓
Shows list of 50 nodes requiring auth
  ↓
User clicks "OpenAI → Add API Key"
  ↓
GET /api/nodes/openai/auth-info
  ↓
Form renders with extracted fields:
  - api_key (secret, required, pattern: ^sk-)
```

### 3. User Enters Auth
```
User enters: sk-proj-1234567890
  ↓
Clicks "Test Connection"
  ↓
POST /api/nodes/openai/test
  {
    "authData": {
      "api_key": "sk-proj-1234567890"
    }
  }
  ↓
System validates pattern
  ↓
System makes test API call to OpenAI
  ↓
Success! Shows available models
  ↓
User clicks "Save"
  ↓
POST /api/nodes/openai/auth
  ↓
Encrypted and stored in SQLite
```

### 4. Flow Architect Uses It
```
User asks: "Generate an image"
  ↓
Flow Architect calls: GET /api/unified
  ↓
Response includes:
  nodes: [
    { id: "openai", enabled: true, authenticated: true }
  ]
  ↓
Flow Architect builds workflow with OpenAI node
  ↓
Uses stored api_key from database
```

## 📊 Implementation Phases (Revised)

### Phase 1: Enhance Node Parser (4 hours)
- [ ] Add `extractAuthRequirements()` function
- [ ] Handle Universal Request Node CONFIG pattern
- [ ] Handle NodeParameter SECRET pattern
- [ ] Handle common auth parameter names
- [ ] Test on 20 sample nodes
- [ ] Verify auth extraction accuracy

### Phase 2: Auth API Endpoints (3 hours)
- [ ] GET /api/nodes/auth-required
- [ ] GET /api/nodes/{nodeType}/auth-info
- [ ] POST /api/nodes/{nodeType}/auth (save encrypted)
- [ ] DELETE /api/nodes/{nodeType}/auth
- [ ] POST /api/nodes/{nodeType}/test
- [ ] Set up SQLite database

### Phase 3: Security Center UI (6 hours)
- [ ] Create /security-center page
- [ ] List nodes requiring auth
- [ ] Dynamic form generation from authFields
- [ ] Test connection button
- [ ] Save & encrypt auth data
- [ ] Show enabled/disabled status

### Phase 4: Unified Catalog (2 hours)
- [ ] Create GET /api/unified
- [ ] Combine services + nodes + flows
- [ ] Filter nodes by user's enabled list
- [ ] Include auth status for each node

### Phase 5: Flow Architect Integration (2 hours)
- [ ] Update to use /api/unified instead of separate calls
- [ ] Handle nodes that aren't authenticated
- [ ] Suggest enabling nodes in Security Center

### Phase 6: Testing (3 hours)
- [ ] Test auth extraction on all 129 nodes
- [ ] Test enabling OpenAI, SendGrid, MongoDB
- [ ] Test unified catalog filtering
- [ ] Test Flow Architect with limited nodes
- [ ] Test connection testing

**Total: ~20 hours**

## ✅ Benefits of This Approach

1. **Zero Hardcoding**: Auth requirements come from actual node files
2. **Auto-Discovery**: New nodes automatically show auth requirements
3. **Accurate**: Always matches what node actually needs
4. **Dynamic Forms**: UI builds forms based on extracted fields
5. **Validation**: Patterns from node files used in forms
6. **Easy for Universal Nodes**: Most nodes use CONFIG pattern
7. **Works for All**: Handles both patterns (CONFIG + NodeParameter)

## 🎯 Priority Implementation Order

1. **Phase 1** (Enhance parser) - Foundation for everything
2. **Phase 4** (Unified catalog) - Needed by Flow Architect
3. **Phase 2** (Auth APIs) - Backend for Security Center
4. **Phase 3** (Security Center UI) - User-facing feature
5. **Phase 5** (Flow Architect integration) - Complete the loop
6. **Phase 6** (Testing) - Verify everything works

---

**This approach extracts auth requirements dynamically from the 129 node files!**

Ready to start with Phase 1 (enhancing the parser)?
