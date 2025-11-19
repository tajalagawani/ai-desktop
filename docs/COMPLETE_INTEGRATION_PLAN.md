# Complete ACT Integration Plan - Full Picture

## 🎯 The Full Picture

### Current Situation

You have **TWO separate repositories**:

1. **`actwith-mcp`** (https://github.com/tajalagawani/actwith-mcp)
   - Contains: ACT Python Engine + MCP Server + agent-sdk
   - This is the **COMPLETE ACT SYSTEM**
   - Currently at: `/Users/tajnoah/act/`

2. **`ai-desktop`** (https://github.com/tajalagawani/ai-desktop)
   - Contains: Desktop App (Next.js)
   - Has agent-sdk **copied** into it at `/Users/tajnoah/Downloads/ai-desktop/agent-sdk/`
   - Currently at: `/Users/tajnoah/Downloads/ai-desktop/`

### The Problem

We have **redundancy**:
- agent-sdk exists in BOTH places
- Desktop app points to external ACT at `/Users/tajnoah/act/`
- On VPS, we need to clone BOTH repositories

---

## 🏗️ Correct Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         LOCAL MAC                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  /Users/tajnoah/act/                ← actwith-mcp repo         │
│  ├── mcp/                           ← MCP Server               │
│  ├── act/                           ← Python Engine            │
│  ├── agent-sdk/                     ← Agent SDK (ORIGINAL)     │
│  ├── flows/                         ← Generated workflows      │
│  └── flow_manager_api.py                                       │
│                                                                 │
│  /Users/tajnoah/Downloads/ai-desktop/  ← ai-desktop repo      │
│  ├── server.js                      ← Desktop App              │
│  ├── components/                                               │
│  ├── lib/flow-builder/                                         │
│  │   └── agent-manager.js           ← Spawns agent             │
│  └── agent-sdk/                     ← POINTS TO /act/agent-sdk │
│      (symlink or git submodule)                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                           VPS                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  /var/www/act/                      ← actwith-mcp repo         │
│  ├── mcp/                           ← MCP Server               │
│  ├── act/                           ← Python Engine            │
│  ├── agent-sdk/                     ← Agent SDK (ORIGINAL)     │
│  ├── flows/                         ← Generated workflows      │
│  └── flow_manager_api.py                                       │
│                                                                 │
│  /var/www/ai-desktop/               ← ai-desktop repo          │
│  ├── server.js                      ← Desktop App              │
│  ├── components/                                               │
│  ├── lib/flow-builder/                                         │
│  │   └── agent-manager.js           ← Spawns agent             │
│  └── agent-sdk/                     ← POINTS TO /var/www/act/  │
│      (symlink or configured path)       agent-sdk              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Correct Approach: Git Submodule

### Why Submodule?

The `agent-sdk` in `ai-desktop` should be a **git submodule** pointing to the agent-sdk in `actwith-mcp`.

**Benefits:**
- Single source of truth
- No duplication
- Easy updates
- Proper version tracking

### Implementation

```bash
# In ai-desktop repository
cd /Users/tajnoah/Downloads/ai-desktop

# Remove current agent-sdk (if it exists)
rm -rf agent-sdk

# Add as submodule pointing to actwith-mcp's agent-sdk
git submodule add https://github.com/tajalagawani/actwith-mcp.git external/actwith-mcp

# Create symlink to agent-sdk
ln -s external/actwith-mcp/agent-sdk agent-sdk
```

**Result:**
```
ai-desktop/
├── external/
│   └── actwith-mcp/          ← Full ACT repo as submodule
│       ├── mcp/
│       ├── act/
│       ├── agent-sdk/        ← Original agent-sdk
│       └── flows/
├── agent-sdk/                ← Symlink to external/actwith-mcp/agent-sdk
└── [rest of desktop app]
```

---

## 🚀 VPS Fresh Installation Script

### Updated Installation Flow

```bash
#!/bin/bash
# VPS Fresh Install with ACT Integration

# Step 1: Install system dependencies
apt update && apt upgrade -y
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs git python3 python3-pip build-essential
npm install -g pm2

# Step 2: Clone ACT Repository (actwith-mcp)
echo "Cloning ACT repository..."
mkdir -p /var/www
cd /var/www
git clone https://github.com/tajalagawani/actwith-mcp.git act
cd act

# Install ACT dependencies
echo "Installing ACT dependencies..."
cd mcp && npm install && cd ..
pip3 install -r requirements.txt
mkdir -p flows mcp/signatures

# Step 3: Clone Desktop App Repository
echo "Cloning Desktop App..."
cd /var/www
git clone https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop

# Initialize submodules (if configured)
git submodule update --init --recursive

# Install desktop app dependencies
npm install
npm run build
mkdir -p logs data

# Step 4: Configure Environment
echo "Configuring environment..."

# Desktop app .env
cat > .env << 'EOF'
PORT=3005
NODE_ENV=production
ANTHROPIC_API_KEY=your-api-key-here
SESSION_SECRET=generate-with-openssl
ENCRYPTION_KEY=32-byte-key
FILE_MANAGER_ROOT=/var/www
USE_CLAUDE_CLI_AUTH=false
EOF

# Agent SDK .env (if using symlink approach)
if [ -L "agent-sdk" ]; then
  # Symlink exists, configure at source
  cat > /var/www/act/agent-sdk/.env << 'EOF'
ANTHROPIC_API_KEY=your-api-key-here
ACT_ROOT=/var/www/act
MCP_SERVER_PATH=/var/www/act/mcp/index.js
FLOWS_DIR=/var/www/act/flows
SIGNATURE_PATH=/var/www/act/mcp/signatures/user.act.sig
DEFAULT_MODEL=claude-sonnet-4-5-20250929
VERBOSE=true
EOF
else
  # Direct agent-sdk folder
  cat > agent-sdk/.env << 'EOF'
ANTHROPIC_API_KEY=your-api-key-here
ACT_ROOT=/var/www/act
MCP_SERVER_PATH=/var/www/act/mcp/index.js
FLOWS_DIR=/var/www/act/flows
SIGNATURE_PATH=/var/www/act/mcp/signatures/user.act.sig
DEFAULT_MODEL=claude-sonnet-4-5-20250929
VERBOSE=true
EOF
fi

# Step 5: Create ACT service scripts
echo "Creating service management scripts..."
cd /var/www/act

cat > start-services.sh << 'EOF'
#!/bin/bash
echo "Starting ACT Services..."
cd /var/www/act

# Start MCP Server
pm2 start mcp/index.js --name "act-mcp-server" \
  --log /var/www/ai-desktop/logs/act-mcp.log

# Start Python API (optional)
if [ -f flow_manager_api.py ]; then
  pm2 start flow_manager_api.py --name "act-flow-api" \
    --interpreter python3 \
    --log /var/www/ai-desktop/logs/act-api.log
fi

pm2 save
echo "ACT Services Started!"
EOF

cat > stop-services.sh << 'EOF'
#!/bin/bash
echo "Stopping ACT Services..."
pm2 delete act-mcp-server 2>/dev/null || true
pm2 delete act-flow-api 2>/dev/null || true
pm2 save
echo "ACT Services Stopped."
EOF

chmod +x start-services.sh stop-services.sh

# Step 6: Start Services
echo "Starting services..."

# Start ACT services
./start-services.sh

# Start Desktop App
cd /var/www/ai-desktop
pm2 start npm --name "ai-desktop" -- start
pm2 save

# Setup PM2 startup
pm2 startup systemd

# Step 7: Configure Firewall
echo "Configuring firewall..."
ufw allow 3005/tcp
ufw allow 8000/tcp
ufw reload

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Desktop App: http://YOUR_VPS_IP:3005"
echo "Flow API: http://localhost:8000"
echo ""
echo "Check status: pm2 status"
echo "View logs: pm2 logs"
echo ""
```

---

## 🔧 Agent Manager Configuration

### Current Issue

`lib/flow-builder/agent-manager.js` has:
```javascript
const agentSdkPath = path.join(__dirname, '../../agent-sdk');
```

### Two Solutions

#### Option 1: Use Symlink (Recommended)
```javascript
// agent-sdk is a symlink to external/actwith-mcp/agent-sdk
const agentSdkPath = path.join(__dirname, '../../agent-sdk');
const debugScript = path.join(agentSdkPath, 'debug-run.sh');

// Works! Symlink resolves to real path
```

#### Option 2: Environment Variable
```javascript
const agentSdkPath = process.env.AGENT_SDK_PATH || path.join(__dirname, '../../agent-sdk');
const debugScript = path.join(agentSdkPath, 'debug-run.sh');
```

Then in `.env`:
```bash
# Local Mac
AGENT_SDK_PATH=/Users/tajnoah/act/agent-sdk

# VPS
AGENT_SDK_PATH=/var/www/act/agent-sdk
```

---

## 📦 Repository Structure Recommendation

### Option A: Submodule (Recommended for Separate Repos)

```
ai-desktop/
├── .git/
├── .gitmodules              ← Submodule config
├── external/
│   └── actwith-mcp/         ← Git submodule
│       ├── mcp/
│       ├── act/
│       ├── agent-sdk/
│       └── flows/
├── agent-sdk/               ← Symlink → external/actwith-mcp/agent-sdk
├── components/
├── lib/
│   └── flow-builder/
│       └── agent-manager.js ← Uses agent-sdk/ (via symlink)
└── server.js
```

**Commands:**
```bash
# Clone desktop with ACT
git clone --recursive https://github.com/tajalagawani/ai-desktop.git

# Update ACT
cd ai-desktop
git submodule update --remote external/actwith-mcp
```

### Option B: Monorepo (Alternative)

Merge both repos:
```
ai-desktop-monorepo/
├── packages/
│   ├── desktop/             ← Desktop app
│   └── act/                 ← ACT system
├── lerna.json
└── package.json
```

---

## 🎯 Recommended Implementation

### For Current Setup (2 Separate Repos)

1. **Keep repos separate** (ai-desktop, actwith-mcp)
2. **Use environment variable** for agent-sdk path
3. **Document clearly** in both repos

### Local Mac Setup

```bash
# 1. ACT repository at /Users/tajnoah/act
cd /Users/tajnoah
git clone https://github.com/tajalagawani/actwith-mcp.git act

# 2. Desktop repository
cd /Users/tajnoah/Downloads
git clone https://github.com/tajalagawani/ai-desktop.git ai-desktop

# 3. Configure desktop to use external ACT
cd ai-desktop
cat > .env << 'EOF'
AGENT_SDK_PATH=/Users/tajnoah/act/agent-sdk
ACT_ROOT=/Users/tajnoah/act
EOF
```

### VPS Setup

```bash
# 1. ACT repository at /var/www/act
cd /var/www
git clone https://github.com/tajalagawani/actwith-mcp.git act

# 2. Desktop repository
git clone https://github.com/tajalagawani/ai-desktop.git

# 3. Configure desktop to use external ACT
cd ai-desktop
cat > .env << 'EOF'
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
EOF
```

---

## 🔄 Updated agent-manager.js

```javascript
const { spawn } = require('child_process');
const path = require('path');

class AgentProcessManager {
  constructor() {
    this.processes = new Map();
    this.sockets = new Map();
  }

  async startAgent(sessionId, request, socket, conversationHistory) {
    this.stopAgent(sessionId);

    console.log(`[AgentManager] Starting agent for session ${sessionId}`);

    // Use environment variable or fallback to local
    const agentSdkPath = process.env.AGENT_SDK_PATH ||
                         path.join(__dirname, '../../agent-sdk');

    const debugScript = path.join(agentSdkPath, 'debug-run.sh');

    console.log(`[AgentManager] Agent SDK Path: ${agentSdkPath}`);
    console.log(`[AgentManager] Debug Script: ${debugScript}`);

    // Prepare context data
    const contextData = {
      request,
      conversationHistory: conversationHistory || [],
      sessionId,
    };

    // Spawn the debug-run.sh script
    const agentProcess = spawn('bash', [debugScript, request], {
      cwd: agentSdkPath,
      env: {
        ...process.env,
        PATH: process.env.PATH,
        HOME: process.env.HOME,
        USER: process.env.USER,
        NODE_ENV: process.env.NODE_ENV,
        SESSION_ID: sessionId,
        DEBUG: 'true',
        VERBOSE: 'true',
        CONVERSATION_CONTEXT: JSON.stringify(contextData),
      },
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    // ... rest of the code
  }
}
```

---

## 📝 Updated .env.example

### Desktop App

```bash
# ========================================
# AI Desktop Environment Configuration
# ========================================

# -----------------
# App Configuration
# -----------------
NODE_ENV=production
PORT=3005

# -----------------
# ACT Integration
# -----------------
# Path to agent-sdk (auto-detected if not set)
# Local: /Users/tajnoah/act/agent-sdk
# VPS: /var/www/act/agent-sdk
AGENT_SDK_PATH=

# Path to ACT root (auto-detected if not set)
# Local: /Users/tajnoah/act
# VPS: /var/www/act
ACT_ROOT=

# -----------------
# API Keys
# -----------------
ANTHROPIC_API_KEY=

# -----------------
# Security
# -----------------
SESSION_SECRET=
ENCRYPTION_KEY=

# -----------------
# File Manager
# -----------------
# Local: /Users/tajnoah
# VPS: /var/www
FILE_MANAGER_ROOT=/var/www
```

---

## ✅ Complete VPS Installation Steps

### Step-by-Step

1. **Install System Dependencies**
   ```bash
   apt update && apt upgrade -y
   curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
   apt install -y nodejs git python3 python3-pip
   npm install -g pm2
   ```

2. **Clone ACT Repository**
   ```bash
   cd /var/www
   git clone https://github.com/tajalagawani/actwith-mcp.git act
   cd act
   cd mcp && npm install && cd ..
   pip3 install -r requirements.txt
   mkdir -p flows mcp/signatures
   ```

3. **Clone Desktop App**
   ```bash
   cd /var/www
   git clone https://github.com/tajalagawani/ai-desktop.git
   cd ai-desktop
   npm install
   npm run build
   mkdir -p logs data
   ```

4. **Configure Environment**
   ```bash
   # Desktop .env
   cat > .env << 'EOF'
   PORT=3005
   AGENT_SDK_PATH=/var/www/act/agent-sdk
   ACT_ROOT=/var/www/act
   ANTHROPIC_API_KEY=your-key-here
   EOF

   # Agent SDK .env
   cat > /var/www/act/agent-sdk/.env << 'EOF'
   ANTHROPIC_API_KEY=your-key-here
   ACT_ROOT=/var/www/act
   MCP_SERVER_PATH=/var/www/act/mcp/index.js
   FLOWS_DIR=/var/www/act/flows
   SIGNATURE_PATH=/var/www/act/mcp/signatures/user.act.sig
   EOF
   ```

5. **Create Service Scripts**
   ```bash
   cd /var/www/act
   # Create start-services.sh and stop-services.sh
   # (as shown in previous sections)
   chmod +x *.sh
   ```

6. **Start Everything**
   ```bash
   /var/www/act/start-services.sh
   cd /var/www/ai-desktop
   pm2 start npm --name "ai-desktop" -- start
   pm2 save
   pm2 startup systemd
   ```

7. **Configure Firewall**
   ```bash
   ufw allow 3005/tcp
   ufw allow 8000/tcp
   ufw reload
   ```

---

## 🎯 Summary

### What We Have

1. **actwith-mcp** repository contains:
   - ACT Python Engine
   - MCP Server
   - agent-sdk (original)
   - Flow Manager API

2. **ai-desktop** repository contains:
   - Desktop App (Next.js)
   - Flow Builder UI
   - agent-manager.js (spawns agent)

### How They Connect

- Desktop app **references** ACT via environment variable
- agent-manager.js spawns agent-sdk from ACT repository
- Agent SDK uses MCP server from ACT repository
- Generated flows saved in ACT repository

### Key Benefits

- ✅ Single source of truth for ACT
- ✅ Easy updates (just `git pull` in ACT repo)
- ✅ No duplication
- ✅ Works on both local and VPS
- ✅ Clean separation of concerns

---

## 🚀 Next Steps

1. **Update agent-manager.js** to use `AGENT_SDK_PATH` env var
2. **Update .env.example** with ACT paths
3. **Create VPS installation script** that clones both repos
4. **Update documentation** with correct paths
5. **Test on VPS** with fresh installation

This is the COMPLETE picture! 🎉
