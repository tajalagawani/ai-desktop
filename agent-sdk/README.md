# ACT Flow Architect Agent

**AI Agent powered by Claude Agent SDK that autonomously generates complete ACT workflow files.**

## What It Does

Describe what you want in plain English, and the agent will:

1. 🔍 Discover the right nodes from 150+ available integrations
2. 🔐 Check which nodes are authenticated in your signature
3. 🏗️ Design the workflow architecture
4. 📝 Generate complete .flow file (custom TOML-like format)
5. 💾 Save directly without parsing/validation (preserves exact format)
6. ✨ No token limits - generate flows of any size

## Installation

```bash
cd agent-sdk
npm install
```

## Quick Start

### Generate a Flow

```bash
# Simple generation
node index.js "Build a flow that sends GitHub issues to Slack daily"

# Using the CLI
node cli.js generate "Create an API that fetches weather data and stores in PostgreSQL"

# With options
node cli.js generate "Process customer feedback with AI" \
  --output custom-flow.flow \
  --model claude-opus-4-20250514
```

### Examples

```bash
# Data sync
node index.js "Sync Monday.com tasks to Asana every hour"

# AI-powered
node index.js "Analyze customer emails with OpenAI and create support tickets"

# ETL pipeline
node index.js "Extract data from API, transform it, and load to PostgreSQL"

# Scheduled automation
node index.js "Backup database to S3 every night at 2 AM"
```

### See Example Requests

```bash
node cli.js examples
```

### Check Available Nodes

```bash
node cli.js list-nodes
```

### Check Authentication Status

```bash
node cli.js check-auth
```

## How It Works

### Architecture

```
User Request → Claude Agent SDK → Flow Architect Agent
                                         ↓
                    ┌────────────────────────────────┐
                    │ 1. list_available_nodes()      │
                    │ 2. get_signature_info()        │
                    │ 3. search_operations()         │
                    │ 4. Design workflow graph       │
                    │ 5. Generate .flow file         │
                    │ 6. Save DIRECTLY (no parsing)  │
                    └────────────────────────────────┘
                                         ↓
                            Generated Flow File (.flow)
                            (Saved exactly as generated)
```

### Agent Process

The agent autonomously:

**Step 1: Discovery**
- Calls `list_available_nodes()` to see all 150+ integrations
- Uses `search_operations()` to find relevant nodes
- Calls `get_node_info()` for detailed node capabilities

**Step 2: Authentication Check**
- Calls `get_signature_info()` to see authenticated nodes
- Plans to use authenticated nodes directly
- Notes which nodes need authentication

**Step 3: Design**
- Maps user requirements to ACT nodes
- Designs the workflow graph (node connections)
- Plans parameter flow between nodes
- Considers error handling and retries

**Step 4: Generation**
- Generates complete .flow file (custom format: TOML-like with JSON elements)
- Includes all required sections:
  - `[workflow]` - Metadata
  - `[parameters]` - User inputs
  - `[node:*]` - Node definitions
  - `[edges]` - Workflow graph
  - `[configuration]` - API settings (if needed)

**Step 5: Save**
- Removes only markdown code fences if present
- Strips any explanatory text before `[workflow]`
- Saves flow EXACTLY as Claude generated it
- NO parsing, NO validation, NO modifications
- Generates filename from workflow name
- Saves to `flows/` directory
- Returns path

## Example Output

**Request:**
```bash
node index.js "Create a daily GitHub to Slack sync"
```

**Agent Process:**
```
🤖 Flow Architect Agent Starting...

📝 Request: Create a daily GitHub to Slack sync

🔍 Agent analyzing requirements...

💭 Agent: I'll create a workflow that fetches GitHub issues daily and posts...
🔧 Using tool: list_available_nodes
🔧 Using tool: get_signature_info
🔧 Using tool: search_operations
🔧 Using tool: get_operation_details
💭 Agent: I've found the github and slack nodes. Let me design the flow...

✅ Flow generation complete!

💾 Flow saved to: /path/to/act/flows/daily-github-to-slack-sync.flow

🎉 Success! Flow is ready to use.

Run it with:
  python act/miniact_executor.py /path/to/flows/daily-github-to-slack-sync.flow
```

**Generated Flow:**
```toml
[workflow]
name = "Daily GitHub to Slack Sync"
description = "Syncs GitHub issues to Slack daily"
start_node = "Schedule"

[parameters]
github_token = { type = "secret", required = true }
slack_channel = { type = "string", default = "#github-updates" }

[node:Schedule]
type = "timer"
schedule = "0 9 * * *"  # 9 AM daily
mode = "cron"
timezone = "UTC"
handler = "FetchIssues"

[node:FetchIssues]
type = "github"
operation = "list_issues"
owner = "myorg"
repo = "myrepo"
state = "open"
token = "{{.Parameter.github_token}}"

[node:FormatMessage]
type = "py"
operation = "execute"
code = """
def format(**kwargs):
    issues = kwargs.get('FetchIssues', {}).get('result', [])

    message = f"📊 Daily GitHub Update: {len(issues)} open issues\\n\\n"

    for issue in issues[:5]:  # Top 5
        message += f"• #{issue['number']}: {issue['title']}\\n"

    return {'result': message}
"""
function = "format"

[node:PostToSlack]
type = "slack"
operation = "post_message"
channel = "{{.Parameter.slack_channel}}"
text = "{{FormatMessage.result}}"

[edges]
Schedule = []
FetchIssues = "FormatMessage"
FormatMessage = "PostToSlack"
PostToSlack = []

[settings]
max_retries = 3
timeout_seconds = 300
```

## CLI Reference

### Generate Flow

```bash
node cli.js generate <request> [options]

Options:
  -o, --output <path>     Output file path
  -m, --model <model>     Claude model (default: claude-sonnet-4-20250514)
  --no-validate           Skip validation
  --dry-run              Generate but don't save
  -v, --verbose          Verbose output
```

### List Nodes

```bash
node cli.js list-nodes [options]

Options:
  -c, --category <cat>   Filter by category
```

### Check Authentication

```bash
node cli.js check-auth
```

### Examples

```bash
node cli.js examples
```

## Configuration

### Environment Variables

Create `.env` in the ACT root directory:

```bash
# Claude API (for Agent SDK)
ANTHROPIC_API_KEY=sk-ant-...

# Paths (optional, auto-detected)
ACT_ROOT=/path/to/act
MCP_SERVER_PATH=/path/to/act/mcp/index.js
FLOWS_DIR=/path/to/act/flows
SIGNATURE_PATH=/path/to/act/mcp/signatures/user.act.sig
```

### Agent Options

```javascript
import FlowArchitectAgent from './index.js';

const agent = new FlowArchitectAgent({
  model: 'claude-opus-4-20250514',  // or 'claude-sonnet-4-20250514'
  mcpServerPath: '/custom/path/to/mcp/index.js',
  flowsDir: '/custom/flows/directory',
  signaturePath: '/custom/signature.sig',
  verbose: true
});

const result = await agent.generateFlow('Your request here');
```

## Programmatic Usage

```javascript
import FlowArchitectAgent from './index.js';

const agent = new FlowArchitectAgent();

// Generate flow
const result = await agent.generateFlow(
  'Build a customer support AI agent',
  {
    outputPath: 'custom-flow.flow',
    validate: true,
    dryRun: false
  }
);

console.log('Flow saved to:', result.path);
console.log('Metadata:', result.metadata);
```

## Use Cases

### 🔄 Integration Workflows
```bash
node index.js "Sync Salesforce leads to HubSpot CRM"
node index.js "Import Stripe payments to PostgreSQL daily"
```

### 🤖 AI-Powered Automation
```bash
node index.js "Auto-respond to support emails with Claude"
node index.js "Analyze customer feedback and categorize with OpenAI"
```

### 📊 Data Pipelines
```bash
node index.js "ETL pipeline: extract from API, transform, load to database"
node index.js "Generate daily analytics reports and email them"
```

### 🚨 Monitoring & Alerts
```bash
node index.js "Monitor website uptime and alert on Slack if down"
node index.js "Track database metrics and notify if thresholds exceeded"
```

### 📅 Scheduled Tasks
```bash
node index.js "Backup PostgreSQL to S3 every night at 2 AM"
node index.js "Send weekly newsletter from blog RSS feed"
```

## Advanced Features

### Custom Models

```bash
# Use Claude Opus for complex flows
node cli.js generate "Complex multi-step AI pipeline" \
  --model claude-opus-4-20250514

# Use Sonnet for simple flows (faster, cheaper)
node cli.js generate "Simple API wrapper" \
  --model claude-sonnet-4-20250514
```

### Dry Run (Preview Only)

```bash
node cli.js generate "Test flow" --dry-run
# Generates flow but doesn't save
```

### Custom Output Path

```bash
node cli.js generate "My flow" \
  --output /custom/path/my-flow.flow
```

## Troubleshooting

### Agent Not Finding Nodes

**Problem:** Agent says "node type not found"

**Solution:**
```bash
# Check available nodes
node cli.js list-nodes

# Check MCP server is running
node ../mcp/index.js
```

### Authentication Errors

**Problem:** "Node requires authentication"

**Solution:**
```bash
# Check auth status
node cli.js check-auth

# Authenticate via Claude CLI
claude "add openai to signature with api_key=sk-..."
```

### Invalid TOML Generated

**Problem:** Flow has TOML syntax errors

**Solution:**
- The agent should auto-validate
- If it fails, try a simpler request
- Use `--verbose` to see agent thinking
- Try a different model (Opus vs Sonnet)

### MCP Server Not Found

**Problem:** "Cannot find MCP server"

**Solution:**
```bash
# Check path in .env or pass explicitly
export MCP_SERVER_PATH=/absolute/path/to/act/mcp/index.js

# Or pass in code
const agent = new FlowArchitectAgent({
  mcpServerPath: '/absolute/path/to/mcp/index.js'
});
```

## Key Design Decisions

### Why No Parsing/Validation?

**The Problem:**
ACT workflows use a **custom format** that looks like TOML but contains JSON-like elements. Standard TOML parsers reject this syntax, causing validation to fail even though the flows are perfectly valid for ACT.

**The Solution:**
The agent saves flows **exactly as Claude generates them** without any parsing or validation:

```javascript
// ✅ What we do now
const flow = claudeResponse.trim();
flow = stripMarkdownFences(flow);
flow = stripTextBefore('[workflow]');
saveFile(flow);  // Save as-is!

// ❌ What we DON'T do anymore
const parsed = tomlParse(flow);  // Would fail on custom syntax!
validate(parsed);                // Not needed
transform(parsed);               // Would break the format
```

**Why This Works:**
- Claude generates valid ACT flows directly
- We trust Claude's output
- The ACT Python engine validates at runtime
- Preserves exact formatting and custom syntax

**What We Still Clean:**
1. Markdown code fences (```)
2. Explanatory text before `[workflow]`
3. Nothing else!

## Architecture Details

### Technologies Used

- **Claude Agent SDK** - Autonomous agent framework
- **MCP (Model Context Protocol)** - Tool integration
- **Custom Format** - TOML-like with JSON elements (ACT-specific)
- **Node.js** - Runtime environment

### Integration with ACT

```
┌─────────────────────────────────────────┐
│     Flow Architect Agent (TypeScript)   │
│                                          │
│  Uses Claude Agent SDK to:               │
│  - Query MCP tools                       │
│  - Discover nodes                        │
│  - Check authentication                  │
│  - Generate TOML flows                   │
└──────────────┬──────────────────────────┘
               │
               ↓ (MCP Protocol)
┌──────────────────────────────────────────┐
│     ACT MCP Server (Node.js)             │
│                                          │
│  Provides 13 tools:                      │
│  - list_available_nodes                  │
│  - get_node_info                         │
│  - get_signature_info                    │
│  - execute_node_operation                │
│  - etc.                                  │
└──────────────┬───────────────────────────┘
               │
               ↓ (Subprocess)
┌──────────────────────────────────────────┐
│     ACT Python Engine                    │
│                                          │
│  Executes:                               │
│  - 150+ nodes                            │
│  - Workflow orchestration                │
│  - Generated flows                       │
└──────────────────────────────────────────┘
```

## Roadmap

- [ ] Multi-flow generation (split complex requests into multiple flows)
- [ ] Flow editing (modify existing flows)
- [ ] Flow testing (auto-generate test cases)
- [ ] Flow optimization (improve performance)
- [ ] Visual flow preview (ASCII art graph)
- [ ] Template library (common flow patterns)
- [ ] Flow marketplace integration
- [ ] CI/CD integration

## Contributing

Contributions welcome! The agent is designed to be extensible.

## License

MIT

---

**Built with ❤️ using Claude Agent SDK**
