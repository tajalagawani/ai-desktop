# Flow Architect Project

This is the working directory for the **Flow Architect** agent - a specialized Claude agent for creating UTA workflow files.

## Directory Structure

```
flow-architect/
├── CLAUDE.md              # This file - project instructions
├── catalogs/              # Service and node catalogs (JSON)
│   ├── service-catalog.json
│   └── node-catalog.json
├── flows/                 # Generated .act workflow files
├── examples/              # Example workflows
├── templates/             # Workflow templates
└── tools/                 # Helper scripts
```

## What This Project Does

The Flow Architect agent uses this directory to:

1. **Read Catalogs**: Check available services and nodes from `catalogs/`
2. **Create Workflows**: Generate .act files in TOML format in `flows/`
3. **Match Services**: Verify service availability before creating flows
4. **Validate Flows**: Ensure all node types and edges are correct

## Agent Restrictions

The Flow Architect agent can ONLY:
- ✅ Read catalog files
- ✅ Create .act workflow files in `flows/` directory
- ✅ Use Read, Write, and Bash tools

The agent CANNOT:
- ❌ Write other code (Python, JavaScript, TypeScript)
- ❌ Modify application code
- ❌ Create files outside `flows/` directory
- ❌ Install packages or dependencies

## Catalogs

### Service Catalog (`catalogs/service-catalog.json`)
Lists all running services (databases, APIs, etc.) that workflows can use.

### Node Catalog (`catalogs/node-catalog.json`)
Defines all available node types and their parameters.

## Creating Workflows

Users request workflows like:
> "Create a flow to fetch users from MongoDB, analyze with Claude AI, and save to Neo4j"

The agent will:
1. Read both catalogs
2. Verify MongoDB and Neo4j services are running
3. Find matching nodes (mongo, claude, neo4j)
4. Create complete .act file in `flows/` directory

## Files Generated

All .act files follow UTA (Universal Task Agent) TOML format with:
- `[workflow]` section with metadata
- `[node:Name]` definitions
- `[edges]` connecting nodes
- `[parameters]` and `[env]` as needed

## Example Flow

```toml
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
api_key = "${CLAUDE_API_KEY}"
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
```

## Auto-Setup

This directory and catalogs are auto-created by the backend server if they don't exist.
The Flow Architect agent file is auto-installed to `~/.claude/agents/flow-architect.md`.

## Usage

From the Action Builder UI:
1. User describes what workflow they need
2. Backend spawns Claude CLI with Flow Architect agent
3. Agent reads catalogs, creates .act file
4. File saved to `flows/` directory
5. User can download or execute the workflow

---

**Agent Name**: flow-architect
**Tools**: Read, Write, Bash
**Model**: sonnet
**Purpose**: Create UTA workflow files only
