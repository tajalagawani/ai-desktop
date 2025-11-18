# ACT Services Setup for Flow Builder

The Flow Builder agent requires two ACT services to be running:

## Required Services

### 1. MCP Server (Required)
**Location:** `/Users/tajnoah/act/mcp/`
**Purpose:** Provides Claude Agent SDK with tools to discover nodes, validate operations, and manage signatures

**Start Command:**
```bash
cd /Users/tajnoah/act
node mcp/index.js
```

**What it does:**
- Lists 150+ available workflow nodes
- Searches for operations by keyword
- Validates node parameters
- Manages authentication signatures
- Gets node information and capabilities

### 2. Python Flow Manager API (Optional but Recommended)
**Location:** `/Users/tajnoah/act/flow_manager_api.py`
**Port:** 8000
**Purpose:** Manages flow execution, deployment, and monitoring

**Start Command:**
```bash
cd /Users/tajnoah/act
python3 flow_manager_api.py
```

**What it provides:**
- Flow discovery and listing
- Container status monitoring
- Health checks
- Log viewing
- Start/stop/restart flows

## Quick Start Script

Create this script to start both services easily:

**File:** `/Users/tajnoah/act/start-services.sh`

```bash
#!/bin/bash

echo "Starting ACT Services for Desktop Flow Builder..."
echo ""

# Check if MCP server exists
if [ ! -f /Users/tajnoah/act/mcp/index.js ]; then
  echo "ERROR: MCP server not found at /Users/tajnoah/act/mcp/index.js"
  exit 1
fi

# Check if Python API exists
if [ ! -f /Users/tajnoah/act/flow_manager_api.py ]; then
  echo "WARNING: Flow Manager API not found at /Users/tajnoah/act/flow_manager_api.py"
  echo "Continuing with MCP server only..."
fi

cd /Users/tajnoah/act

# Start MCP server in background
echo "✓ Starting MCP Server..."
node mcp/index.js > /tmp/act-mcp.log 2>&1 &
MCP_PID=$!
echo "  MCP Server PID: $MCP_PID"
echo "  Logs: /tmp/act-mcp.log"

# Start Python API in background (if exists)
if [ -f flow_manager_api.py ]; then
  echo "✓ Starting Flow Manager API on port 8000..."
  python3 flow_manager_api.py > /tmp/act-api.log 2>&1 &
  API_PID=$!
  echo "  API Server PID: $API_PID"
  echo "  Logs: /tmp/act-api.log"
  echo "  URL: http://localhost:8000"
fi

echo ""
echo "ACT Services Started!"
echo ""
echo "To stop services:"
echo "  kill $MCP_PID"
if [ ! -z "$API_PID" ]; then
  echo "  kill $API_PID"
fi
echo ""

# Save PIDs for later
echo "$MCP_PID" > /tmp/act-mcp.pid
if [ ! -z "$API_PID" ]; then
  echo "$API_PID" > /tmp/act-api.pid
fi
```

**Make it executable:**
```bash
chmod +x /Users/tajnoah/act/start-services.sh
```

## Stop Services

**File:** `/Users/tajnoah/act/stop-services.sh`

```bash
#!/bin/bash

echo "Stopping ACT Services..."

# Stop MCP server
if [ -f /tmp/act-mcp.pid ]; then
  MCP_PID=$(cat /tmp/act-mcp.pid)
  if kill -0 $MCP_PID 2>/dev/null; then
    kill $MCP_PID
    echo "✓ Stopped MCP Server (PID: $MCP_PID)"
  fi
  rm /tmp/act-mcp.pid
fi

# Stop Python API
if [ -f /tmp/act-api.pid ]; then
  API_PID=$(cat /tmp/act-api.pid)
  if kill -0 $API_PID 2>/dev/null; then
    kill $API_PID
    echo "✓ Stopped Flow Manager API (PID: $API_PID)"
  fi
  rm /tmp/act-api.pid
fi

echo "All services stopped."
```

**Make it executable:**
```bash
chmod +x /Users/tajnoah/act/stop-services.sh
```

## Integration with Desktop App

The desktop app's agent-sdk will automatically connect to these services when generating flows:

### Agent SDK Configuration
**Location:** `/Users/tajnoah/Downloads/ai-desktop/agent-sdk/index.js:42-44`

```javascript
const ACT_ROOT = join(__dirname, '..');  // Points to /Users/tajnoah/act
const MCP_SERVER_PATH = join(ACT_ROOT, 'mcp/index.js');
const SIGNATURE_PATH = join(ACT_ROOT, 'mcp/signatures/user.act.sig');
```

The agent expects:
- MCP Server at `/Users/tajnoah/act/mcp/index.js`
- Signature file at `/Users/tajnoah/act/mcp/signatures/user.act.sig`
- Flows directory at `/Users/tajnoah/act/flows/`

## Verification

### Check if services are running:

```bash
# Check MCP Server (should see node process)
ps aux | grep "node mcp/index.js"

# Check Python API (should see python process)
ps aux | grep "flow_manager_api.py"

# Test Python API
curl http://localhost:8000/health
```

Expected API response:
```json
{
  "success": true,
  "status": "healthy",
  "service": "Flow Manager API",
  "version": "1.0.0"
}
```

## Troubleshooting

### MCP Server Not Starting
```bash
# Check for errors
cat /tmp/act-mcp.log

# Test manually
cd /Users/tajnoah/act
node mcp/index.js
```

### Python API Not Starting
```bash
# Check for errors
cat /tmp/act-api.log

# Install dependencies
pip install -r /Users/tajnoah/act/requirements.txt

# Test manually
cd /Users/tajnoah/act
python3 flow_manager_api.py
```

### Port 8000 Already in Use
```bash
# Find what's using port 8000
lsof -ti:8000

# Kill the process
lsof -ti:8000 | xargs kill -9
```

## Automatic Startup (Optional)

To automatically start ACT services when desktop app starts, add to desktop app's startup:

**Edit:** `/Users/tajnoah/Downloads/ai-desktop/server.js`

Add before server starts:

```javascript
// Start ACT services
const { spawn } = require('child_process');
const actServicesScript = '/Users/tajnoah/act/start-services.sh';
if (existsSync(actServicesScript)) {
  console.log('[ACT Services] Starting...');
  spawn('bash', [actServicesScript], { detached: true, stdio: 'ignore' });
}
```

## Environment Variables

The agent-sdk reads these from `/Users/tajnoah/Downloads/ai-desktop/agent-sdk/.env`:

```bash
# Required: Anthropic API key
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Override paths
MCP_SERVER_PATH=/Users/tajnoah/act/mcp/index.js
FLOWS_DIR=/Users/tajnoah/act/flows
SIGNATURE_PATH=/Users/tajnoah/act/mcp/signatures/user.act.sig

# Optional: Agent configuration
ACT_AGENT_MODEL=claude-sonnet-4-5-20250929
VERBOSE=true
STREAM_MODE=true
```

## Summary

**Minimum setup to make Flow Builder work:**

1. Start MCP Server:
   ```bash
   cd /Users/tajnoah/act && node mcp/index.js &
   ```

2. Start Desktop App:
   ```bash
   cd /Users/tajnoah/Downloads/ai-desktop && npm run dev
   ```

3. Open Flow Builder in browser and start chatting!

The agent will use the MCP server to discover nodes and generate `.flow` files in `/Users/tajnoah/act/flows/`.
