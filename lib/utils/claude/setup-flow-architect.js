import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Default service catalog structure
 */
const DEFAULT_SERVICE_CATALOG = {
  version: "1.0.0",
  last_updated: new Date().toISOString(),
  services: [],
  description: "Service catalog for Flow Architect. Add your running services here."
};

/**
 * Default node catalog structure
 */
const DEFAULT_NODE_CATALOG = {
  version: "1.0.0",
  last_updated: new Date().toISOString(),
  nodes: [
    {
      type: "mongo",
      name: "MongoDB Node",
      description: "MongoDB database operations",
      requires_service: "mongodb",
      parameters: ["connection_string", "operation", "collection", "query"]
    },
    {
      type: "neo4j",
      name: "Neo4j Node",
      description: "Neo4j graph database operations",
      requires_service: "neo4j",
      parameters: ["connection_string", "operation", "query"]
    },
    {
      type: "neon",
      name: "Neon PostgreSQL Node",
      description: "Neon PostgreSQL database operations",
      requires_service: "postgresql",
      parameters: ["connection_string", "operation", "query"]
    },
    {
      type: "mysql",
      name: "MySQL Node",
      description: "MySQL database operations",
      requires_service: "mysql",
      parameters: ["connection_string", "operation", "query"]
    },
    {
      type: "redis",
      name: "Redis Node",
      description: "Redis cache operations",
      requires_service: "redis",
      parameters: ["connection_string", "operation", "key", "value"]
    },
    {
      type: "claude",
      name: "Claude AI Node",
      description: "Anthropic Claude AI processing",
      requires_service: null,
      parameters: ["api_key", "model", "messages", "temperature", "max_tokens"]
    },
    {
      type: "gemini",
      name: "Gemini AI Node",
      description: "Google Gemini AI processing",
      requires_service: null,
      parameters: ["api_key", "model", "messages"]
    },
    {
      type: "openai",
      name: "OpenAI Node",
      description: "OpenAI GPT processing",
      requires_service: null,
      parameters: ["api_key", "model", "messages", "temperature", "max_tokens"]
    },
    {
      type: "py",
      name: "Python Node",
      description: "Execute Python code",
      requires_service: null,
      parameters: ["code", "packages"]
    },
    {
      type: "if",
      name: "If Node",
      description: "Boolean conditional branching",
      requires_service: null,
      parameters: ["condition", "true_path", "false_path"]
    },
    {
      type: "switch",
      name: "Switch Node",
      description: "Multi-way branching",
      requires_service: null,
      parameters: ["value", "cases"]
    },
    {
      type: "set",
      name: "Set Node",
      description: "Store values",
      requires_service: null,
      parameters: ["key", "value"]
    },
    {
      type: "data",
      name: "Data Node",
      description: "Data transformation",
      requires_service: null,
      parameters: ["operation", "input", "output"]
    },
    {
      type: "aci",
      name: "ACI Node",
      description: "Define REST API routes",
      requires_service: null,
      parameters: ["method", "path", "handler"]
    },
    {
      type: "log_message",
      name: "Log Message Node",
      description: "Logging operations",
      requires_service: null,
      parameters: ["message", "level"]
    },
    {
      type: "generate_uuid",
      name: "Generate UUID Node",
      description: "UUID generation",
      requires_service: null,
      parameters: []
    }
  ],
  description: "Node catalog for Flow Architect. Defines all available node types."
};

/**
 * Default CLAUDE.md project instructions
 */
const DEFAULT_CLAUDE_MD = `# Flow Architect Project

This is the working directory for the **Flow Architect** agent - a specialized Claude agent for creating UTA workflow files.

## Directory Structure

\`\`\`
flow-architect/
├── CLAUDE.md              # This file - project instructions
├── catalogs/              # Service and node catalogs (JSON)
│   ├── service-catalog.json
│   └── node-catalog.json
├── flows/                 # Generated .act workflow files
├── examples/              # Example workflows
├── templates/             # Workflow templates
└── tools/                 # Helper scripts
\`\`\`

## What This Project Does

The Flow Architect agent uses this directory to:

1. **Read Catalogs**: Check available services and nodes from \`catalogs/\`
2. **Create Workflows**: Generate .act files in TOML format in \`flows/\`
3. **Match Services**: Verify service availability before creating flows
4. **Validate Flows**: Ensure all node types and edges are correct

## Agent Restrictions

The Flow Architect agent can ONLY:
- ✅ Read catalog files
- ✅ Create .act workflow files in \`flows/\` directory
- ✅ Use Read, Write, and Bash tools

The agent CANNOT:
- ❌ Write other code (Python, JavaScript, TypeScript)
- ❌ Modify application code
- ❌ Create files outside \`flows/\` directory
- ❌ Install packages or dependencies

## Catalogs

### Service Catalog (\`catalogs/service-catalog.json\`)
Lists all running services (databases, APIs, etc.) that workflows can use.

### Node Catalog (\`catalogs/node-catalog.json\`)
Defines all available node types and their parameters.

## Creating Workflows

Users request workflows like:
> "Create a flow to fetch users from MongoDB, analyze with Claude AI, and save to Neo4j"

The agent will:
1. Read both catalogs
2. Verify MongoDB and Neo4j services are running
3. Find matching nodes (mongo, claude, neo4j)
4. Create complete .act file in \`flows/\` directory

## Files Generated

All .act files follow UTA (Universal Task Agent) TOML format with:
- \`[workflow]\` section with metadata
- \`[node:Name]\` definitions
- \`[edges]\` connecting nodes
- \`[parameters]\` and \`[env]\` as needed

## Example Flow

\`\`\`toml
[workflow]
name = "User Analysis Pipeline"
description = "Fetch, analyze, and save users"
start_node = FetchUsers

[node:FetchUsers]
type = mongo
label = "Fetch users from MongoDB"
connection_string = "mongodb://localhost:27017"
operation = find
collection = users
query = {"age": {"$gt": 25}}

[node:AnalyzeUsers]
type = claude
label = "Analyze users with Claude AI"
api_key = "\${CLAUDE_API_KEY}"
model = "claude-3-5-sonnet-20240620"
messages = [
  {
    "role": "user",
    "content": "Analyze: {{FetchUsers.data}}"
  }
]

[node:SaveToNeo4j]
type = neo4j
label = "Save to Neo4j"
connection_string = "bolt://localhost:7687"
operation = create_nodes
nodes = "{{AnalyzeUsers.result.content.0.text}}"

[edges]
FetchUsers = AnalyzeUsers
AnalyzeUsers = SaveToNeo4j

[env]
CLAUDE_API_KEY
\`\`\`

## Auto-Setup

This directory and catalogs are auto-created by the backend server if they don't exist.
The Flow Architect agent file is auto-installed to \`~/.claude/agents/flow-architect.md\`.

## Usage

From the Action Builder UI:
1. User describes what workflow they need
2. Backend spawns Claude CLI with Flow Architect agent
3. Agent reads catalogs, creates .act file
4. File saved to \`flows/\` directory
5. User can download or execute the workflow

---

**Agent Name**: flow-architect
**Tools**: Read, Write, Bash
**Model**: sonnet
**Purpose**: Create UTA workflow files only
`;

/**
 * Ensures the flow-architect project directory structure exists
 */
export async function ensureFlowArchitectProject() {
  try {
    // Get the flow-architect project path (in root directory, not lib/)
    const projectRoot = path.join(__dirname, '../../../flow-architect');

    console.log('[Setup] Checking flow-architect project structure...');

    // Ensure main directory exists
    await fs.mkdir(projectRoot, { recursive: true });

    // Define all required subdirectories
    const subdirs = ['catalogs', 'flows', 'examples', 'templates', 'tools'];

    // Create all subdirectories
    for (const subdir of subdirs) {
      const subdirPath = path.join(projectRoot, subdir);
      await fs.mkdir(subdirPath, { recursive: true });
      console.log('[Setup] ✅ Ensured directory:', subdirPath);
    }

    // Create catalog files if they don't exist
    const serviceCatalogPath = path.join(projectRoot, 'catalogs', 'service-catalog.json');
    const nodeCatalogPath = path.join(projectRoot, 'catalogs', 'node-catalog.json');
    const claudeMdPath = path.join(projectRoot, 'CLAUDE.md');

    // Service catalog
    try {
      await fs.access(serviceCatalogPath);
      console.log('[Setup] ✅ Service catalog already exists');
    } catch (error) {
      await fs.writeFile(
        serviceCatalogPath,
        JSON.stringify(DEFAULT_SERVICE_CATALOG, null, 2),
        'utf8'
      );
      console.log('[Setup] ✅ Created service catalog:', serviceCatalogPath);
    }

    // Node catalog
    try {
      await fs.access(nodeCatalogPath);
      console.log('[Setup] ✅ Node catalog already exists');
    } catch (error) {
      await fs.writeFile(
        nodeCatalogPath,
        JSON.stringify(DEFAULT_NODE_CATALOG, null, 2),
        'utf8'
      );
      console.log('[Setup] ✅ Created node catalog:', nodeCatalogPath);
    }

    // CLAUDE.md
    try {
      await fs.access(claudeMdPath);
      console.log('[Setup] ✅ CLAUDE.md already exists');
    } catch (error) {
      await fs.writeFile(claudeMdPath, DEFAULT_CLAUDE_MD, 'utf8');
      console.log('[Setup] ✅ Created CLAUDE.md:', claudeMdPath);
    }

    console.log('[Setup] ✅ Flow Architect project structure ready');

    return {
      success: true,
      projectPath: projectRoot
    };

  } catch (error) {
    console.error('[Setup] ❌ Error in ensureFlowArchitectProject:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Validates the flow-architect project structure
 */
export async function validateFlowArchitectProject() {
  try {
    const projectRoot = path.join(__dirname, '../../flow-architect');

    // Check all required directories exist
    const requiredDirs = ['catalogs', 'flows', 'examples', 'templates', 'tools'];
    const requiredFiles = [
      'catalogs/service-catalog.json',
      'catalogs/node-catalog.json',
      'CLAUDE.md'
    ];

    for (const dir of requiredDirs) {
      const dirPath = path.join(projectRoot, dir);
      await fs.access(dirPath);
    }

    for (const file of requiredFiles) {
      const filePath = path.join(projectRoot, file);
      await fs.access(filePath);
    }

    console.log('[Setup] ✅ Flow Architect project validated');
    return { valid: true };

  } catch (error) {
    console.error('[Setup] ❌ Project validation failed:', error.message);
    return { valid: false, error: error.message };
  }
}
