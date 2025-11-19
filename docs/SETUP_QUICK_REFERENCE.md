# Setup Quick Reference - ACT Integration

## 🎯 Overview

The AI Desktop now integrates with the **actwith-mcp** repository for Flow Builder functionality.

## 📦 Two Repositories

1. **actwith-mcp** (https://github.com/tajalagawani/actwith-mcp)
   - ACT Python Engine
   - MCP Server (150+ nodes)
   - agent-sdk
   - Flow Manager API

2. **ai-desktop** (https://github.com/tajalagawani/ai-desktop)
   - Desktop App
   - Flow Builder UI
   - References external ACT

---

## 🖥️ Local Mac Setup

### Step 1: Clone ACT Repository
```bash
cd /Users/tajnoah
git clone https://github.com/tajalagawani/actwith-mcp.git act
cd act
cd mcp && npm install && cd ..
pip3 install -r requirements.txt
```

### Step 2: Desktop App Already Configured
Your desktop app at `/Users/tajnoah/Downloads/ai-desktop` is already configured:

```bash
# .env already has:
AGENT_SDK_PATH=/Users/tajnoah/act/agent-sdk
ACT_ROOT=/Users/tajnoah/act
```

### Step 3: Start ACT Services
```bash
cd /Users/tajnoah/act
./start-services.sh
```

### Step 4: Start Desktop App
```bash
cd /Users/tajnoah/Downloads/ai-desktop
npm run dev
```

### Step 5: Test Flow Builder
Open http://localhost:3005 → Flow Builder → Test it! 🎉

---

## 🌐 VPS Setup

### One-Command Installation

```bash
curl -fsSL https://raw.githubusercontent.com/tajalagawani/ai-desktop/main/deployment/vps-with-act-install.sh | bash
```

This installs EVERYTHING:
- ✅ System dependencies
- ✅ ACT at `/var/www/act`
- ✅ Desktop App at `/var/www/ai-desktop`
- ✅ MCP Server (PM2)
- ✅ Flow Manager API (PM2)
- ✅ Desktop App (PM2)

### After Installation

1. **Add API Keys:**
   ```bash
   nano /var/www/ai-desktop/.env
   # Add ANTHROPIC_API_KEY

   nano /var/www/act/agent-sdk/.env
   # Add ANTHROPIC_API_KEY
   ```

2. **Generate Secrets:**
   ```bash
   # SESSION_SECRET
   openssl rand -base64 32

   # ENCRYPTION_KEY
   openssl rand -hex 16
   ```

3. **Restart:**
   ```bash
   pm2 restart all
   ```

4. **Access:**
   ```
   http://YOUR_VPS_IP:3005
   ```

---

## 📁 File Locations

### Local Mac
| Component | Path |
|-----------|------|
| ACT Repo | `/Users/tajnoah/act/` |
| Desktop App | `/Users/tajnoah/Downloads/ai-desktop/` |
| Agent SDK (external) | `/Users/tajnoah/act/agent-sdk/` |
| Agent SDK (fallback) | `/Users/tajnoah/Downloads/ai-desktop/agent-sdk/` |
| Flows | `/Users/tajnoah/act/flows/` |
| MCP Server | `/Users/tajnoah/act/mcp/` |

### VPS
| Component | Path |
|-----------|------|
| ACT Repo | `/var/www/act/` |
| Desktop App | `/var/www/ai-desktop/` |
| Agent SDK | `/var/www/act/agent-sdk/` |
| Flows | `/var/www/act/flows/` |
| MCP Server | `/var/www/act/mcp/` |
| Logs | `/var/www/ai-desktop/logs/` |

---

## 🔧 Environment Variables

### Desktop App `.env`

```bash
# Server
PORT=3005
NODE_ENV=production

# API Key
ANTHROPIC_API_KEY=your-key-here

# ACT Integration (IMPORTANT!)
AGENT_SDK_PATH=/var/www/act/agent-sdk    # VPS
# or
AGENT_SDK_PATH=/Users/tajnoah/act/agent-sdk    # Local

ACT_ROOT=/var/www/act    # VPS
# or
ACT_ROOT=/Users/tajnoah/act    # Local

# Security
SESSION_SECRET=generated-secret
ENCRYPTION_KEY=generated-key

# File Manager
FILE_MANAGER_ROOT=/var/www    # VPS
# or
FILE_MANAGER_ROOT=/Users/tajnoah    # Local
```

### Agent SDK `.env`

```bash
# API Key
ANTHROPIC_API_KEY=your-key-here

# Paths
ACT_ROOT=/var/www/act    # or /Users/tajnoah/act
MCP_SERVER_PATH=/var/www/act/mcp/index.js
FLOWS_DIR=/var/www/act/flows
SIGNATURE_PATH=/var/www/act/mcp/signatures/user.act.sig

# Config
DEFAULT_MODEL=claude-sonnet-4-5-20250929
VERBOSE=true
STREAM_MODE=true
```

---

## 🚀 Common Commands

### Local Development

```bash
# Start ACT services
cd /Users/tajnoah/act
./start-services.sh

# Stop ACT services
./stop-services.sh

# Start desktop app
cd /Users/tajnoah/Downloads/ai-desktop
npm run dev

# View desktop logs
tail -f logs/*.log

# Update ACT
cd /Users/tajnoah/act
git pull
cd mcp && npm install && cd ..
pip3 install -r requirements.txt
```

### VPS Production

```bash
# Check status
pm2 status

# View logs
pm2 logs
pm2 logs ai-desktop
pm2 logs act-mcp-server
pm2 logs act-flow-api

# Restart services
pm2 restart all
pm2 restart ai-desktop
pm2 restart act-mcp-server

# Update desktop app
cd /var/www/ai-desktop
git pull
npm install
npm run build
pm2 restart ai-desktop

# Update ACT
cd /var/www/act
git pull
cd mcp && npm install && cd ..
pip3 install -r requirements.txt
pm2 restart act-mcp-server
pm2 restart act-flow-api

# Start/Stop ACT services
cd /var/www/act
./start-services.sh
./stop-services.sh
```

---

## 🧪 Testing

### Test MCP Server
```bash
# Should start without errors
cd /var/www/act/mcp    # or /Users/tajnoah/act/mcp
node index.js
# Ctrl+C to exit (PM2 will manage it)
```

### Test Flow Manager API
```bash
curl http://localhost:8000/health
# Should return: {"success": true, "status": "healthy", ...}
```

### Test Desktop App
```bash
curl http://localhost:3005
# Should return HTML
```

### Test Flow Builder
1. Open browser: `http://localhost:3005` (or VPS IP)
2. Click Flow Builder icon
3. Send message: "Create a hello world workflow"
4. Should see agent output streaming
5. Check flows: `ls /var/www/act/flows/` (or `/Users/tajnoah/act/flows/`)

---

## 🐛 Troubleshooting

### Flow Builder Not Working

**Check agent-sdk path:**
```bash
# Should see: [AgentManager] Agent SDK Path: /var/www/act/agent-sdk
pm2 logs ai-desktop | grep "Agent SDK Path"
```

**Check MCP server:**
```bash
pm2 list | grep act-mcp-server
# Should be "online"
```

**Check flows directory:**
```bash
ls -la /var/www/act/flows/
# Should exist and be writable
```

### No Flows Generated

**Check API key:**
```bash
grep ANTHROPIC_API_KEY /var/www/act/agent-sdk/.env
# Should have valid key
```

**Check logs:**
```bash
pm2 logs ai-desktop --lines 50 | grep -i error
```

### Services Not Starting

**Check PM2:**
```bash
pm2 status
pm2 logs
```

**Restart everything:**
```bash
pm2 delete all
cd /var/www/act && ./start-services.sh
cd /var/www/ai-desktop
pm2 start npm --name "ai-desktop" -- start
pm2 save
```

---

## 📝 Important Notes

1. **API Keys Required**: Both desktop `.env` and agent-sdk `.env` need `ANTHROPIC_API_KEY`

2. **AGENT_SDK_PATH**: Must point to external ACT repository (not the fallback copy)

3. **Fallback**: If `AGENT_SDK_PATH` not set, app uses local copy at `/ai-desktop/agent-sdk/`

4. **PM2 Startup**: Run `pm2 startup systemd` and execute the generated command for auto-start on boot

5. **Firewall**: Open ports 3005 (desktop) and 8000 (flow API) on VPS

6. **Updates**: Update both repos separately (`git pull` in each)

---

## ✅ Verification Checklist

### Local Mac
- [ ] ACT cloned at `/Users/tajnoah/act/`
- [ ] Desktop app has `AGENT_SDK_PATH=/Users/tajnoah/act/agent-sdk` in `.env`
- [ ] MCP server running (check with `ps aux | grep mcp`)
- [ ] Desktop app accessible at `http://localhost:3005`
- [ ] Flow Builder generates workflows

### VPS
- [ ] ACT cloned at `/var/www/act/`
- [ ] Desktop app cloned at `/var/www/ai-desktop/`
- [ ] API keys set in both `.env` files
- [ ] PM2 shows 3 processes running (ai-desktop, act-mcp-server, act-flow-api)
- [ ] Desktop accessible at `http://VPS_IP:3005`
- [ ] Flow Builder generates workflows
- [ ] PM2 startup configured

---

## 🆘 Quick Help

**Everything broken?**
```bash
# Nuclear option - restart everything
pm2 delete all
pm2 kill
cd /var/www/act && ./start-services.sh
cd /var/www/ai-desktop
pm2 start npm --name "ai-desktop" -- start
pm2 save
```

**Check integration:**
```bash
# Should show external path
echo $AGENT_SDK_PATH

# Check .env
cat /var/www/ai-desktop/.env | grep AGENT_SDK_PATH

# Test agent manually
cd /var/www/act/agent-sdk
node index.js "test message"
```

---

## 📚 Documentation

- **Complete Integration Plan**: `COMPLETE_INTEGRATION_PLAN.md`
- **Architecture Diagram**: `FLOW_BUILDER_ARCHITECTURE.md`
- **VPS Setup**: `VPS_FLOW_BUILDER_SETUP.md`
- **Agent SDK Details**: `AGENT_SDK_INTEGRATION.md`
- **MCP Hub Plan**: `MCP_HUB_PLAN.md`
