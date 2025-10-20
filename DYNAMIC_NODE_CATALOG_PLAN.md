# Dynamic Node Catalog System - Implementation Plan

## 🎯 Objective
Create a fully dynamic node catalog that parses actual Python node files to provide real-time, LLM-friendly information about available nodes, their parameters, and operations.

## 📊 Node Analysis

### Current State
- **164 node files** in `/components/apps/act-docker/act/nodes/`
- Mix of node types:
  - **Universal Request Nodes**: HTTP-based API integrations
  - **SDK Nodes**: Using specific libraries (MongoDB, OpenAI, etc.)
  - **Logic Nodes**: Python, conditional, transformation
  - **Infrastructure Nodes**: Database, file system, etc.

### Node Structure Pattern

#### 1. Schema Definition
Every node inherits from `BaseNode` and implements:
```python
def get_schema(self) -> NodeSchema:
    return NodeSchema(
        node_type="node_name",
        version="1.0.0",
        description="What this node does",
        parameters=[
            NodeParameter(
                name="param_name",
                type=NodeParameterType.STRING,
                description="Parameter description",
                required=True,
                default=None,
                enum=["option1", "option2"]  # Optional
            )
        ],
        outputs={
            "result": NodeParameterType.ANY,
            "status": NodeParameterType.STRING
        },
        tags=["category", "feature"],
        author="ACT Framework"
    )
```

#### 2. Operation-Based Nodes
Many nodes support multiple operations:
```python
class MongoDBOperation:
    INSERT_ONE = "insert_one"
    FIND = "find"
    UPDATE_ONE = "update_one"
    # ... 50+ operations
```

## 🏗️ Architecture Design

### 1. Node Parser Service
**Location:** `/lib/node-parser.ts`

**Responsibilities:**
- Parse Python files to extract schemas
- Handle different node patterns
- Cache parsed results
- Support hot-reload for development

**Key Methods:**
```typescript
interface NodeParser {
  parseNodeFile(filePath: string): Promise<ParsedNode>
  parseAllNodes(): Promise<NodeCatalog>
  getNodeSchema(nodeType: string): Promise<NodeSchema>
  getOperationDetails(nodeType: string, operation: string): Promise<OperationDetails>
}
```

### 2. Dynamic Node Catalog API
**Endpoints:**

#### `/api/nodes` - List All Nodes
```json
GET /api/nodes?category=database&search=mongo

Response:
{
  "nodes": [
    {
      "type": "mongodb",
      "displayName": "MongoDB",
      "description": "NoSQL database operations",
      "categories": ["database", "nosql"],
      "operations": ["insert_one", "find", "update_one"],
      "complexity": "sdk",
      "authRequired": true
    }
  ],
  "total": 164,
  "categories": ["database", "api", "logic", "utility"]
}
```

#### `/api/nodes/[nodeType]` - Get Node Details
```json
GET /api/nodes/mongodb

Response:
{
  "type": "mongodb",
  "version": "2.0.0",
  "description": "Comprehensive MongoDB integration",
  "parameters": [
    {
      "name": "connection_string",
      "type": "string",
      "description": "MongoDB connection URI",
      "required": true,
      "pattern": "mongodb://",
      "example": "mongodb://localhost:27017"
    }
  ],
  "operations": {
    "insert_one": {
      "description": "Insert a single document",
      "parameters": [
        {
          "name": "document",
          "type": "object",
          "description": "Document to insert"
        }
      ],
      "returns": {
        "inserted_id": "string"
      }
    }
  },
  "examples": [
    {
      "operation": "insert_one",
      "toml": "[node:SaveUser]\ntype = mongodb\noperation = insert_one\ndocument = {name = \"John\", age = 30}"
    }
  ]
}
```

#### `/api/nodes/[nodeType]/operations` - List Operations
```json
GET /api/nodes/mongodb/operations

Response:
{
  "operations": [
    {
      "name": "insert_one",
      "category": "create",
      "description": "Insert a single document"
    },
    {
      "name": "find",
      "category": "read",
      "description": "Query documents"
    }
  ],
  "categories": {
    "create": ["insert_one", "insert_many"],
    "read": ["find", "find_one"],
    "update": ["update_one", "update_many"],
    "delete": ["delete_one", "delete_many"]
  }
}
```

#### `/api/nodes/[nodeType]/operations/[operation]` - Operation Details
```json
GET /api/nodes/mongodb/operations/insert_one

Response:
{
  "operation": "insert_one",
  "description": "Insert a single document into collection",
  "parameters": [
    {
      "name": "collection",
      "type": "string",
      "required": true
    },
    {
      "name": "document",
      "type": "object",
      "required": true
    }
  ],
  "returns": {
    "inserted_id": "string",
    "acknowledged": "boolean"
  },
  "example": {
    "toml": "[node:CreateUser]\ntype = mongodb\noperation = insert_one\ncollection = \"users\"\ndocument = {name = \"Alice\", email = \"alice@example.com\"}",
    "description": "Insert a new user into the users collection"
  }
}
```

### 3. Parser Implementation Strategy

#### Phase 1: AST Parsing (Python → JSON)
Create Python script to extract schemas:
```python
# /components/apps/act-docker/scripts/extract_schemas.py
import ast
import json
import importlib.util
from pathlib import Path

def extract_node_schema(file_path):
    # Parse Python AST
    # Find get_schema method
    # Extract NodeSchema constructor
    # Convert to JSON
    return schema_json
```

#### Phase 2: Runtime Introspection
Use Python's import system:
```python
def get_node_info(node_type):
    module = importlib.import_module(f"act.nodes.{node_type}")
    node_class = getattr(module, f"{node_type}Node")
    instance = node_class()
    schema = instance.get_schema()
    return schema.dict()
```

#### Phase 3: Hybrid Approach
- Static analysis for basic info (fast)
- Runtime introspection for detailed schemas (accurate)
- Cache results with TTL
- Background refresh for changes

### 4. LLM-Friendly Features

#### Smart Categorization
```json
{
  "categories": {
    "data_sources": {
      "databases": ["mongodb", "postgresql", "redis"],
      "apis": ["openai", "slack", "github"],
      "files": ["csv", "json", "excel"]
    },
    "transformations": {
      "logic": ["if", "switch", "loop"],
      "data": ["transform", "aggregate", "filter"]
    },
    "integrations": {
      "communication": ["email", "sms", "webhook"],
      "monitoring": ["datadog", "prometheus"]
    }
  }
}
```

#### Semantic Search
```json
GET /api/nodes/search?q=send+email

Response:
{
  "matches": [
    {"node": "smtp", "score": 0.95},
    {"node": "sendgrid", "score": 0.92},
    {"node": "mailgun", "score": 0.88}
  ]
}
```

#### Capability Matrix
```json
{
  "capabilities": {
    "can_read_files": ["csv", "json", "excel"],
    "can_write_database": ["mongodb", "postgresql"],
    "can_send_notifications": ["email", "slack", "webhook"],
    "can_process_data": ["python", "javascript", "transform"]
  }
}
```

## 🔄 Implementation Phases

### Phase 1: Basic Parser (Week 1)
- [ ] Create Python schema extractor
- [ ] Build basic Node Parser service
- [ ] Implement /api/nodes endpoint
- [ ] Test with 10 common nodes

### Phase 2: Operation Support (Week 2)
- [ ] Parse operation enums/classes
- [ ] Add operation-specific parameters
- [ ] Implement operation detail endpoints
- [ ] Create operation examples

### Phase 3: Advanced Features (Week 3)
- [ ] Add semantic search
- [ ] Implement capability matrix
- [ ] Create smart categorization
- [ ] Build caching layer

### Phase 4: Integration (Week 4)
- [ ] Update Flow Architect to use dynamic catalog
- [ ] Remove hardcoded node-catalog.json
- [ ] Add hot-reload for development
- [ ] Create comprehensive tests

## 📝 API Examples for LLM

### "What nodes can connect to databases?"
```bash
curl http://localhost:3000/api/nodes?capability=database
```

### "Show me how to use MongoDB insert"
```bash
curl http://localhost:3000/api/nodes/mongodb/operations/insert_one
```

### "Find nodes that can send emails"
```bash
curl http://localhost:3000/api/nodes/search?q=email
```

### "What parameters does OpenAI node need?"
```bash
curl http://localhost:3000/api/nodes/openai
```

## 🎯 Success Criteria

1. **Complete Discovery**: All 164 nodes automatically discovered
2. **Real-time Updates**: Changes to nodes reflected immediately
3. **LLM Usability**: Agent can easily find and use any node
4. **Operation Details**: Full parameter info for each operation
5. **Examples**: Working TOML examples for common uses
6. **Performance**: < 100ms response time for queries
7. **Accuracy**: 100% match between actual node and catalog

## 🚀 Next Steps

1. Create Python schema extractor script
2. Build TypeScript Node Parser service
3. Implement catalog API endpoints
4. Update Flow Architect to use dynamic catalog
5. Test with all 164 nodes
6. Document API for LLM usage

## 📊 Benefits

- **Zero Hardcoding**: Catalog always matches actual nodes
- **Auto-discovery**: New nodes appear automatically
- **Rich Metadata**: Full parameter and operation details
- **LLM Optimized**: Easy for AI to find and use nodes
- **Version Safe**: Changes tracked automatically
- **Developer Friendly**: Hot-reload during development

---

**Status:** Ready for Implementation
**Priority:** High (blocks true dynamic system)
**Estimated Time:** 4 weeks
**Dependencies:** ACT node files, Next.js API routes