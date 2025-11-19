# Agent SDK Integration

## Overview

The ACT Flow Architect agent SDK is now integrated locally in the `/agent-sdk` directory. The desktop app calls it as an external process for workflow generation.

## Architecture

```
Desktop App (Next.js)
    ↓
lib/flow-builder/agent-manager.js
    ↓ spawn bash process
agent-sdk/debug-run.sh
    ↓
agent-sdk/index.js (Claude Agent SDK)
    ↓
Generates .flow files
```

## Key Changes

### 1. Updated Path Resolution
**File:** `lib/flow-builder/agent-manager.js:16-21`

```javascript
// Use AGENT_SDK_PATH from environment, fallback to local copy
const agentSdkPath = process.env.AGENT_SDK_PATH ||
                     path.join(__dirname, '../../agent-sdk');
const debugScript = path.join(agentSdkPath, 'debug-run.sh');

console.log(`[AgentManager] Agent SDK Path: ${agentSdkPath}`);
```

Uses environment variable to point to external ACT repository, with local fallback.

### 2. Environment Variables (Required for Production)
**File:** `.env` and `.env.example`

```bash
# Path to ACT agent-sdk (points to external actwith-mcp repository)
# Local Mac:  AGENT_SDK_PATH=/Users/tajnoah/act/agent-sdk
# VPS:        AGENT_SDK_PATH=/var/www/act/agent-sdk
AGENT_SDK_PATH=

# Path to ACT root directory
# Local Mac:  ACT_ROOT=/Users/tajnoah/act
# VPS:        ACT_ROOT=/var/www/act
ACT_ROOT=
```

If `AGENT_SDK_PATH` is not set, the app falls back to the local agent-sdk copy at `/ai-desktop/agent-sdk/`.

## Directory Structure

```
ai-desktop/
├── agent-sdk/                    # ACT Flow Architect Agent (standalone)
│   ├── index.js                  # Main agent entry point
│   ├── debug-run.sh              # Debug wrapper script
│   ├── package.json              # ES Module dependencies
│   ├── node_modules/             # Agent dependencies (separate from app)
│   └── ...
├── lib/
│   └── flow-builder/
│       └── agent-manager.js      # Spawns agent process
└── components/
    └── flow-builder/
        └── ChatInterface.tsx     # Flow Builder UI
```

## Why External Process?

The agent-sdk is kept as a separate process (not imported as a module) because:

1. **Module System Incompatibility**
   - agent-sdk: ES Modules (`"type": "module"`)
   - Desktop app: CommonJS/Next.js
   - Cannot be directly imported without breaking one or the other

2. **Independent Dependencies**
   - agent-sdk has its own node_modules
   - Uses `@anthropic-ai/claude-agent-sdk`
   - Keeps bundle size separate

3. **Process Isolation**
   - Agent runs in isolated process with own environment
   - Can be killed/restarted independently
   - Cleaner error handling and logging

4. **CLI Compatibility**
   - Maintains standalone CLI functionality
   - Can be used independently via `npm run build-flow`
   - Easier to test and debug

## Usage

### From Desktop App
1. Open Flow Builder in the desktop UI
2. Enter a workflow request
3. Agent automatically starts and streams output
4. Generated .flow file is saved to ACT directory

### Standalone CLI
```bash
cd agent-sdk
npm run build-flow "Create a workflow that sends a Slack notification"
```

## Configuration

The agent reads these environment variables when spawned:

- `SESSION_ID` - Current chat session ID
- `DEBUG` - Enable debug logging (set by agent-manager)
- `VERBOSE` - Enable verbose output (set by agent-manager)
- `CONVERSATION_CONTEXT` - JSON with conversation history

## Troubleshooting

### Agent Not Starting
1. Check agent-sdk dependencies are installed:
   ```bash
   cd agent-sdk && npm install
   ```

2. Verify debug-run.sh is executable:
   ```bash
   chmod +x agent-sdk/debug-run.sh
   ```

3. Check server logs for spawn errors:
   ```
   [AgentManager] Starting agent for session <id>
   [AgentManager] Running debug script: <path>
   ```

### No Output Streaming
1. Check WebSocket connection in browser console
2. Verify Socket.IO is running on port 3005
3. Check agent-sdk stdout/stderr in server logs

### Wrong Path Errors
If you see errors about `/Users/tajnoah/act/agent-sdk`:
- Clear localStorage: `localStorage.removeItem('flow-builder-settings')`
- Restart the server
- The path is now hard-coded to use local agent-sdk

## Required ACT Services

The agent needs two ACT services to be running:

### 1. MCP Server (Required)
The Model Context Protocol server provides tools for node discovery and validation.

**Start Command:**
```bash
cd /Users/tajnoah/act && node mcp/index.js &
```

Or use the convenience script:
```bash
/Users/tajnoah/act/start-services.sh
```

### 2. Python Flow Manager API (Optional)
Provides flow management and monitoring on port 8000.

**Start Command:**
```bash
cd /Users/tajnoah/act && python3 flow_manager_api.py &
```

**Stop All Services:**
```bash
/Users/tajnoah/act/stop-services.sh
```

**Verify Services:**
```bash
# Check MCP server is running
ps aux | grep "node mcp/index.js"

# Check Python API is running
curl http://localhost:8000/health
```

See **ACT_SERVICES_SETUP.md** for complete setup guide.

## Development Notes

- The agent-sdk is version-controlled with the desktop app
- Both can be updated independently
- No build step needed - agent runs directly with Node.js
- Hot reload doesn't affect running agent processes
- Agent requires MCP server to be running to function
- Generated flows are saved to `/Users/tajnoah/act/flows/`
