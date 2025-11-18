# Flow Builder Quick Start

## Complete Setup (3 Steps)

### Step 1: Start ACT Services
```bash
/Users/tajnoah/act/start-services.sh
```

This starts:
- **MCP Server** - Provides 150+ workflow nodes to the agent
- **Python API** (optional) - Flow management on port 8000

### Step 2: Start Desktop App
```bash
cd /Users/tajnoah/Downloads/ai-desktop
npm run dev
```

Desktop app starts on: http://localhost:3005

### Step 3: Use Flow Builder
1. Open http://localhost:3005
2. Click the **Flow Builder** icon in the desktop
3. Type a workflow request like:
   - "Create a workflow that sends GitHub issues to Slack"
   - "Build a flow that monitors a URL and sends alerts"
   - "Make a flow that processes data from an API"

The agent will:
1. Discover available nodes from MCP server
2. Generate a complete `.flow` file
3. Save it to `/Users/tajnoah/act/flows/`
4. Stream progress in real-time

## Verify Setup

Run the verification script:
```bash
/Users/tajnoah/Downloads/ai-desktop/test-flow-builder-setup.sh
```

Should show:
- ✓ Success: 10+
- ⚠ Warnings: 0-2 (if services not running)
- ✗ Errors: 0

## Stop Services

```bash
/Users/tajnoah/act/stop-services.sh
```

## Troubleshooting

### Services not starting
```bash
# View MCP server logs
tail -f /tmp/act-mcp.log

# View Python API logs
tail -f /tmp/act-api.log
```

### Agent not responding
1. Check MCP server is running: `ps aux | grep "node.*mcp/index.js"`
2. Check agent-sdk .env has API key: `cat agent-sdk/.env`
3. Check server logs for errors

### No flows being generated
- Check `/Users/tajnoah/act/flows/` directory exists
- Check permissions: `ls -la /Users/tajnoah/act/flows/`
- Look for errors in desktop app logs

## Architecture Overview

```
User → Desktop App (Next.js)
         ↓
    agent-manager.js
         ↓
    agent-sdk/debug-run.sh
         ↓
    agent-sdk/index.js
         ↓
    Claude Agent SDK ← → MCP Server (150+ nodes)
         ↓
    Generate .flow file
         ↓
    Save to /Users/tajnoah/act/flows/
```

## What Each Service Does

### Desktop App (Port 3005)
- Provides UI for Flow Builder
- Manages chat sessions and messages
- Spawns agent process when user sends request
- Streams agent output via WebSocket

### Agent SDK (agent-sdk/)
- Autonomous AI agent using Claude Agent SDK
- Connects to MCP server for node discovery
- Generates complete workflow files
- Validates and saves `.flow` files

### MCP Server (/Users/tajnoah/act/mcp/)
- Provides 150+ workflow node types
- Handles node discovery and search
- Validates parameters and operations
- Manages authentication signatures

### Python API (Port 8000) - Optional
- Flow management and monitoring
- Container status and health checks
- Flow execution and deployment
- Log viewing and debugging

## Example Session

```
User: "Create a workflow that checks GitHub for new issues every hour and posts them to Slack"

Agent:
1. Discovering nodes... (calls MCP server)
2. Found: github, slack, scheduler nodes
3. Generating workflow...
4. Validating parameters...
5. Saving to: /Users/tajnoah/act/flows/github-slack-monitor.flow
6. ✓ Complete!
```

## Environment Variables

### Desktop App (.env)
```bash
PORT=3005
FILE_MANAGER_ROOT=/Users/tajnoah
ANTHROPIC_API_KEY=sk-ant-...
```

### Agent SDK (agent-sdk/.env)
```bash
ANTHROPIC_API_KEY=sk-ant-...
ACT_ROOT=/Users/tajnoah/act
MCP_SERVER_PATH=/Users/tajnoah/act/mcp/index.js
FLOWS_DIR=/Users/tajnoah/act/flows
SIGNATURE_PATH=/Users/tajnoah/act/mcp/signatures/user.act.sig
```

## Documentation Files

- **ACT_SERVICES_SETUP.md** - Complete service setup guide
- **AGENT_SDK_INTEGRATION.md** - Technical integration details
- **FLOW_BUILDER_README.md** - Flow Builder features and API
- **QUICK_START_FLOW_BUILDER.md** - This file

## Support

If you encounter issues:
1. Run verification script: `./test-flow-builder-setup.sh`
2. Check service logs: `/tmp/act-mcp.log` and `/tmp/act-api.log`
3. Verify paths in `agent-sdk/.env`
4. Ensure MCP server is running
