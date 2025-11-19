# VPS Flow Builder Setup Guide

This guide explains how to set up the Flow Builder on your VPS with full ACT integration.

---

## 🎯 Overview

The VPS setup includes:
1. **AI Desktop** - Main application at `/var/www/ai-desktop`
2. **ACT Installation** - Workflow system at `/var/www/act`
3. **MCP Server** - Node discovery at `/var/www/act/mcp`
4. **Flow Manager API** - Flow management at port 8000

---

## 📋 Architecture on VPS

```
VPS Server (Ubuntu)
├── /var/www/ai-desktop/          ← Desktop App (Port 3005)
│   ├── server.js
│   ├── agent-sdk/                ← Local Agent
│   │   ├── .env                  ← Points to /var/www/act
│   │   └── index.js
│   └── data/
│       └── flow-builder.db
│
└── /var/www/act/                 ← ACT Installation
    ├── mcp/                      ← MCP Server
    │   ├── index.js
    │   ├── tools/
    │   └── signatures/
    ├── flows/                    ← Generated Workflows
    ├── flow_manager_api.py       ← Python API (Port 8000)
    ├── start-services.sh         ← Service launcher
    └── stop-services.sh          ← Service stopper
```

---

## 🚀 Fresh Installation

### Option 1: Automated Installation (Recommended)

Run this single command on your VPS:

```bash
curl -fsSL https://raw.githubusercontent.com/tajalagawani/ai-desktop/main/deployment/vps-flow-builder-install.sh | bash
```

This will:
- Install AI Desktop
- Clone and setup ACT
- Configure MCP server
- Install Python dependencies
- Create service scripts
- Start everything with PM2

### Option 2: Manual Installation

Follow these steps if you prefer manual control:

#### Step 1: Install AI Desktop (Existing Script)

```bash
cd /var/www
git clone https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop
npm install
npm run build
```

#### Step 2: Clone ACT Repository

```bash
cd /var/www
git clone https://github.com/YOUR_ACT_REPO/act.git
cd act
```

#### Step 3: Install ACT Dependencies

```bash
# Install MCP server dependencies
cd /var/www/act/mcp
npm install
cd ..

# Install Python dependencies
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p flows
mkdir -p mcp/signatures
```

#### Step 4: Configure Agent SDK

```bash
cd /var/www/ai-desktop/agent-sdk

# Create .env file
cat > .env << 'EOF'
# Claude API Key (Required for Agent SDK)
ANTHROPIC_API_KEY=your-api-key-here

# Paths (Point to VPS ACT installation)
ACT_ROOT=/var/www/act
MCP_SERVER_PATH=/var/www/act/mcp/index.js
FLOWS_DIR=/var/www/act/flows
SIGNATURE_PATH=/var/www/act/mcp/signatures/user.act.sig

# Agent Configuration
DEFAULT_MODEL=claude-sonnet-4-5-20250929
VERBOSE=true
EOF

# Replace with your actual API key
nano .env
```

#### Step 5: Create Service Management Scripts

```bash
cd /var/www/act

# Create start-services.sh
cat > start-services.sh << 'EOF'
#!/bin/bash
echo "Starting ACT Services..."

cd /var/www/act

# Start MCP server
echo "✓ Starting MCP Server..."
pm2 start mcp/index.js --name "act-mcp-server" --log /var/www/ai-desktop/logs/act-mcp.log

# Start Python API
if [ -f flow_manager_api.py ]; then
  echo "✓ Starting Flow Manager API on port 8000..."
  pm2 start flow_manager_api.py --name "act-flow-api" --interpreter python3 --log /var/www/ai-desktop/logs/act-api.log
fi

pm2 save
echo "ACT Services Started!"
EOF

# Create stop-services.sh
cat > stop-services.sh << 'EOF'
#!/bin/bash
echo "Stopping ACT Services..."
pm2 delete act-mcp-server 2>/dev/null || true
pm2 delete act-flow-api 2>/dev/null || true
pm2 save
echo "ACT Services Stopped."
EOF

# Make executable
chmod +x start-services.sh stop-services.sh
```

#### Step 6: Start Services

```bash
# Start ACT services
/var/www/act/start-services.sh

# Start Desktop App
cd /var/www/ai-desktop
pm2 start npm --name "ai-desktop" -- start
pm2 save

# Setup PM2 to start on boot
pm2 startup systemd
# Run the command PM2 outputs
```

#### Step 7: Configure Firewall

```bash
# Allow port 3005 (Desktop App)
ufw allow 3005/tcp

# Allow port 8000 (Flow Manager API) - Optional
ufw allow 8000/tcp

# Reload firewall
ufw reload
```

---

## 🔧 Environment Variables

### Desktop App .env
**Location**: `/var/www/ai-desktop/.env`

```bash
# Server Configuration
PORT=3005
NODE_ENV=production

# API Key
ANTHROPIC_API_KEY=sk-ant-...

# Security
SESSION_SECRET=generate-with-openssl-rand-base64-32
ENCRYPTION_KEY=32-byte-key-here

# File Manager
FILE_MANAGER_ROOT=/var/www

# Claude CLI Auth
USE_CLAUDE_CLI_AUTH=false
```

### Agent SDK .env
**Location**: `/var/www/ai-desktop/agent-sdk/.env`

```bash
# Claude API Key
ANTHROPIC_API_KEY=sk-ant-...

# ACT Paths (VPS)
ACT_ROOT=/var/www/act
MCP_SERVER_PATH=/var/www/act/mcp/index.js
FLOWS_DIR=/var/www/act/flows
SIGNATURE_PATH=/var/www/act/mcp/signatures/user.act.sig

# Agent Configuration
DEFAULT_MODEL=claude-sonnet-4-5-20250929
VERBOSE=true
STREAM_MODE=true
```

### ACT .env (Optional)
**Location**: `/var/www/act/.env`

```bash
# ACT Configuration (if needed by specific nodes)
# Most nodes use signature-based authentication
```

---

## 📊 Service Management

### Check Status

```bash
# Check all PM2 processes
pm2 status

# Should see:
# - ai-desktop (running)
# - act-mcp-server (running)
# - act-flow-api (running) [optional]
```

### View Logs

```bash
# Desktop app logs
pm2 logs ai-desktop

# MCP server logs
pm2 logs act-mcp-server

# Flow API logs
pm2 logs act-flow-api

# All logs
pm2 logs
```

### Restart Services

```bash
# Restart desktop app
pm2 restart ai-desktop

# Restart ACT services
/var/www/act/stop-services.sh
/var/www/act/start-services.sh

# Restart all
pm2 restart all
```

### Stop Services

```bash
# Stop desktop app
pm2 stop ai-desktop

# Stop ACT services
/var/www/act/stop-services.sh

# Stop all
pm2 stop all
```

---

## 🧪 Verification

### Test MCP Server

```bash
cd /var/www/act/mcp
node index.js
```

Should start without errors (Ctrl+C to exit, PM2 will manage it)

### Test Python API

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "success": true,
  "status": "healthy",
  "service": "Flow Manager API",
  "version": "1.0.0"
}
```

### Test Desktop App

```bash
curl http://localhost:3005
```

Should return HTML content.

### Test Flow Builder

1. Open browser: `http://YOUR_VPS_IP:3005`
2. Click Flow Builder icon
3. Send a test message: "Create a simple hello world workflow"
4. Should see agent output streaming
5. Check `/var/www/act/flows/` for generated .flow file

---

## 🔄 Updates

### Update Desktop App

```bash
cd /var/www/ai-desktop
git pull origin main
npm install
npm run build
pm2 restart ai-desktop
```

### Update ACT

```bash
cd /var/www/act
git pull origin main

# Update MCP dependencies
cd mcp && npm install && cd ..

# Update Python dependencies
pip3 install -r requirements.txt

# Restart ACT services
/var/www/act/stop-services.sh
/var/www/act/start-services.sh
```

### Update Agent SDK

```bash
cd /var/www/ai-desktop/agent-sdk
npm install
pm2 restart ai-desktop
```

---

## 🚨 Troubleshooting

### Flow Builder Not Working

**Check MCP Server:**
```bash
pm2 logs act-mcp-server
```

If not running:
```bash
cd /var/www/act
./start-services.sh
```

**Check Agent SDK .env:**
```bash
cat /var/www/ai-desktop/agent-sdk/.env
```

Ensure paths point to `/var/www/act`.

### No Flows Generated

**Check flows directory:**
```bash
ls -la /var/www/act/flows/
```

If directory doesn't exist:
```bash
mkdir -p /var/www/act/flows
chmod 755 /var/www/act/flows
```

**Check agent logs in desktop app:**
```bash
pm2 logs ai-desktop | grep -A 10 "Agent"
```

### MCP Server Won't Start

**Check dependencies:**
```bash
cd /var/www/act/mcp
npm install
```

**Check for port conflicts:**
```bash
# MCP server uses stdio, no port conflicts
# But check if another instance is running
ps aux | grep "mcp/index.js"
```

### API Key Issues

**Verify API key in both locations:**
```bash
grep ANTHROPIC_API_KEY /var/www/ai-desktop/.env
grep ANTHROPIC_API_KEY /var/www/ai-desktop/agent-sdk/.env
```

Both should have valid keys starting with `sk-ant-`.

### Permission Errors

**Fix permissions:**
```bash
chown -R root:root /var/www/act
chmod -R 755 /var/www/act
chmod +x /var/www/act/*.sh
```

---

## 🔐 Security Considerations

### Firewall Rules

```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 3005/tcp  # Desktop App
ufw allow 8000/tcp  # Flow API (optional)
ufw enable
```

### API Key Protection

- Store API keys in .env files (not committed to git)
- Use environment variables in production
- Consider using secrets management for production

### Service Isolation

- ACT services run as separate PM2 processes
- Each service has its own log file
- Failures are isolated

---

## 📈 Monitoring

### Resource Usage

```bash
# PM2 monitoring dashboard
pm2 monit

# System resources
htop

# Disk usage
df -h /var/www

# Memory usage
free -h
```

### Log Rotation

PM2 automatically handles log rotation. Configure in:

```bash
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
```

---

## 🎯 Performance Tips

1. **Use Production Mode**: Set `NODE_ENV=production` in .env
2. **Enable Caching**: Configure nginx caching for static assets
3. **Limit Log Size**: Use pm2-logrotate
4. **Monitor Resources**: Use `pm2 monit` regularly
5. **Update Regularly**: Keep dependencies up to date

---

## 📚 Quick Reference

### File Locations

| Component | Location |
|-----------|----------|
| Desktop App | `/var/www/ai-desktop` |
| Agent SDK | `/var/www/ai-desktop/agent-sdk` |
| ACT Installation | `/var/www/act` |
| MCP Server | `/var/www/act/mcp` |
| Generated Flows | `/var/www/act/flows` |
| Desktop Logs | `/var/www/ai-desktop/logs` |
| Flow Builder DB | `/var/www/ai-desktop/data/flow-builder.db` |

### Service Commands

| Action | Command |
|--------|---------|
| Start ACT | `/var/www/act/start-services.sh` |
| Stop ACT | `/var/www/act/stop-services.sh` |
| Restart Desktop | `pm2 restart ai-desktop` |
| View Logs | `pm2 logs` |
| Check Status | `pm2 status` |
| Monitor | `pm2 monit` |

### Port Reference

| Service | Port | Access |
|---------|------|--------|
| Desktop App | 3005 | http://VPS_IP:3005 |
| Flow Manager API | 8000 | http://localhost:8000 |
| MCP Server | N/A | stdio only |

---

## ✅ Post-Installation Checklist

- [ ] Desktop app running on port 3005
- [ ] MCP server running in PM2
- [ ] Flow Manager API running (optional)
- [ ] Firewall configured
- [ ] API keys set in .env files
- [ ] Flows directory exists with correct permissions
- [ ] Test Flow Builder generates a workflow
- [ ] PM2 configured to start on boot
- [ ] Logs are accessible and rotating

---

## 🆘 Support

**Check logs first:**
```bash
pm2 logs
```

**Restart everything:**
```bash
/var/www/act/stop-services.sh
pm2 restart all
/var/www/act/start-services.sh
```

**Fresh start:**
```bash
pm2 delete all
pm2 kill
# Then run installation again
```

For issues, check:
- GitHub Issues
- System logs: `journalctl -xe`
- Disk space: `df -h`
- Memory: `free -h`
