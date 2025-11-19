# AI Desktop VPS Complete Installation Guide

This guide provides step-by-step instructions to install AI Desktop with Flow Builder on a clean VPS from scratch.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start (Automated)](#quick-start-automated)
3. [Manual Installation](#manual-installation)
4. [Post-Installation Setup](#post-installation-setup)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance](#maintenance)

---

## Prerequisites

### VPS Requirements
- **OS**: Ubuntu 20.04 or 22.04 LTS
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk**: Minimum 10GB free space
- **Access**: Root SSH access
- **Network**: Public IP address

### Local Machine Requirements
- macOS or Linux
- `sshpass` installed (`brew install sshpass` on macOS)
- SSH access to VPS

### Required Information
- VPS IP address and SSH password
- Anthropic API key (starts with `sk-ant-api03-...`)

---

## Quick Start (Automated)

### Step 1: Prepare the Installation Script

```bash
cd /Users/tajnoah/Downloads/ai-desktop
chmod +x deployment/vps-complete-install.sh
```

### Step 2: Run the Installation

```bash
SSH_PASSWORD='your_vps_password' \
  ./deployment/vps-complete-install.sh \
  root@92.112.181.127 \
  sk-ant-api03-YOUR_API_KEY_HERE
```

**Replace:**
- `your_vps_password` - Your VPS root password
- `92.112.181.127` - Your VPS IP address
- `sk-ant-api03-YOUR_API_KEY_HERE` - Your Anthropic API key

### Step 3: Wait for Completion

The script will:
1. Clean old installations (if any)
2. Install system dependencies
3. Install Node.js 22
4. Install PM2
5. Upload and install ACT system
6. Clone and build AI Desktop
7. Configure Nginx
8. Start the application

**Total time:** ~10-15 minutes

### Step 4: Access Your Installation

Open your browser to: `http://YOUR_VPS_IP`

---

## Manual Installation

If you prefer to install step by step manually, follow these instructions:

### 1. Connect to VPS

```bash
ssh root@YOUR_VPS_IP
```

### 2. Clean Old Installations (if any)

```bash
pm2 delete all || true
rm -rf /var/www/ai-desktop
rm -rf /var/www/act
docker system prune -af || true
```

### 3. Install System Dependencies

```bash
apt-get update
apt-get install -y git curl build-essential python3 python3-pip python3-venv nginx
```

### 4. Install Node.js 22 via NVM

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

export NVM_DIR="/root/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

nvm install 22
nvm use 22
nvm alias default 22
```

### 5. Install PM2

```bash
export PATH=/root/.nvm/versions/node/v22.11.0/bin:$PATH
npm install -g pm2
```

### 6. Create Directory Structure

```bash
mkdir -p /var/www/ai-desktop
mkdir -p /var/www/act/{agent-sdk,mcp,flows}
```

### 7. Upload and Extract ACT System

**On your local machine:**

```bash
cd /Users/tajnoah/Downloads/potree-develop\ 2/backend/ceviopro/actwith-mcp
tar -czf /tmp/act-clean.tar.gz .
scp /tmp/act-clean.tar.gz root@YOUR_VPS_IP:/tmp/
```

**On VPS:**

```bash
cd /var/www/act
tar -xzf /tmp/act-clean.tar.gz
rm /tmp/act-clean.tar.gz
```

### 8. Install ACT Dependencies

```bash
export PATH=/root/.nvm/versions/node/v22.11.0/bin:$PATH

# MCP dependencies
cd /var/www/act/mcp
npm install

# Agent SDK dependencies
cd /var/www/act/agent-sdk
npm install

# Python dependencies (essential only)
cd /var/www/act
python3 -m pip install anthropic python-dotenv requests aiohttp
```

### 9. Configure ACT Environment

```bash
cat > /var/www/act/agent-sdk/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
ACT_ROOT=/var/www/act
MCP_SERVER_PATH=/var/www/act/mcp/index.js
FLOWS_DIR=/var/www/act/flows
SIGNATURE_PATH=/var/www/act/mcp/signatures/user.act.sig
DEFAULT_MODEL=claude-sonnet-4-5-20250929
VERBOSE=true
STREAM_MODE=true

# Security: Allow sandbox bypass for root execution (VPS only)
ALLOW_SANDBOX_BYPASS=true
IS_SANDBOX=true
EOF
```

### 10. Clone AI Desktop

```bash
cd /var/www
git clone https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop
npm install
```

### 11. Upload Local Modifications

**On your local machine, upload the security-enhanced files:**

```bash
cd /Users/tajnoah/Downloads/ai-desktop

# Upload settings store
scp lib/flow-builder/stores/settings-store.ts root@YOUR_VPS:/var/www/ai-desktop/lib/flow-builder/stores/

# Upload settings UI
scp components/flow-builder/FlowBuilderSettings.tsx root@YOUR_VPS:/var/www/ai-desktop/components/flow-builder/

# Upload API routes
ssh root@YOUR_VPS "mkdir -p /var/www/ai-desktop/app/api/flow-builder/settings"
scp app/api/flow-builder/settings/route.ts root@YOUR_VPS:/var/www/ai-desktop/app/api/flow-builder/settings/
scp app/api/flow-builder/messages/route.ts root@YOUR_VPS:/var/www/ai-desktop/app/api/flow-builder/messages/

# Upload agent integration
scp lib/flow-builder/hooks/use-agent.ts root@YOUR_VPS:/var/www/ai-desktop/lib/flow-builder/hooks/
scp lib/flow-builder/agent-manager.js root@YOUR_VPS:/var/www/ai-desktop/lib/flow-builder/
scp agent-sdk/index.js root@YOUR_VPS:/var/www/ai-desktop/agent-sdk/
scp server.js root@YOUR_VPS:/var/www/ai-desktop/

# Upload utilities
ssh root@YOUR_VPS "mkdir -p /var/www/ai-desktop/lib/utils"
scp lib/utils/uuid.ts root@YOUR_VPS:/var/www/ai-desktop/lib/utils/
scp lib/utils/index.ts root@YOUR_VPS:/var/www/ai-desktop/lib/utils/
```

### 12. Configure AI Desktop Environment

**On VPS:**

```bash
cat > /var/www/ai-desktop/.env << 'EOF'
# Server Configuration
PORT=3005
NODE_ENV=production

# Anthropic API Configuration
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
USE_CLAUDE_CLI_AUTH=false

# Security Center - Encryption Key
ENCRYPTION_KEY=b7e3f8a2d9c4e1f6a8b3d7c2e9f4a1b6

# File Manager Configuration
FILE_MANAGER_ROOT=/var/www
SHOW_HIDDEN_FILES=false

# Flow Builder / ACT Integration
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act

# Security: Allow sandbox bypass for root execution (VPS only)
ALLOW_SANDBOX_BYPASS=true
EOF
```

### 13. Build AI Desktop

```bash
export PATH=/root/.nvm/versions/node/v22.11.0/bin:$PATH
cd /var/www/ai-desktop
rm -rf .next
npm run build
```

### 14. Configure Nginx

```bash
cat > /etc/nginx/sites-available/ai-desktop << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;
    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # WebSocket support for terminals
    location /api/terminal/ws {
        proxy_pass http://localhost:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # WebSocket support for service logs
    location /api/services/logs/ws {
        proxy_pass http://localhost:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Socket.IO support for Flow Builder
    location /socket.io/ {
        proxy_pass http://localhost:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
}
EOF

# Enable site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/

# Test and reload
nginx -t
systemctl reload nginx
```

### 15. Start with PM2

```bash
export PATH=/root/.nvm/versions/node/v22.11.0/bin:$PATH
cd /var/www/ai-desktop

pm2 start npm --name "ai-desktop" -- start
pm2 save
pm2 startup systemd -u root --hp /root
```

---

## Post-Installation Setup

### 1. Access the Application

Open your browser to: `http://YOUR_VPS_IP`

### 2. Configure Flow Builder Settings

1. Click **"Flow Builder"** app
2. Click the **Settings** icon (gear) in the top-right
3. Go to **"API Keys"** tab
4. Enter your Anthropic API key
5. Go to **"Security"** tab
6. **READ ALL WARNINGS CAREFULLY**
7. Enable **"Allow Sandbox Bypass"** (required for VPS)
8. Confirm the security dialog
9. Click **"Save Changes"**

### 3. Test Flow Builder

1. In the Flow Builder chat, enter a request:
   ```
   Create a simple weather tracking API
   ```
2. Watch the agent generate your workflow!
3. Check the generated `.flow` file in the output

---

## Troubleshooting

### Issue: Agent fails with "cannot use --dangerously-skip-permissions"

**Solution:** Ensure both environment variables are set in `/var/www/act/agent-sdk/.env`:

```bash
ALLOW_SANDBOX_BYPASS=true
IS_SANDBOX=true
```

Then restart PM2:
```bash
pm2 restart ai-desktop
```

### Issue: Wrong API key being used

**Solution:** Check the Flow Builder settings UI:

1. Go to Settings → API Keys
2. Verify your API key is entered
3. Save settings
4. Restart the agent

The agent will log which API key it's using in PM2 logs:
```bash
pm2 logs ai-desktop | grep "API key"
```

### Issue: 500 errors when saving messages

**Solution:** Check database permissions:

```bash
chmod 777 /var/www/ai-desktop/data
ls -la /var/www/ai-desktop/data/flow-builder.db
```

### Issue: Port 80 not accessible

**Solution:** Check Nginx status:

```bash
systemctl status nginx
nginx -t
netstat -tulpn | grep :80
```

### Issue: Out of disk space

**Solution:** Clean up Docker and old logs:

```bash
docker system prune -af
pm2 flush
journalctl --vacuum-time=7d
```

---

## Maintenance

### View Logs

```bash
# PM2 logs
pm2 logs ai-desktop

# Last 50 lines
pm2 logs ai-desktop --lines 50

# Follow logs in real-time
pm2 logs ai-desktop --lines 0
```

### Restart Application

```bash
pm2 restart ai-desktop
```

### Update Application

```bash
cd /var/www/ai-desktop
git pull
npm install
npm run build
pm2 restart ai-desktop
```

### Check Status

```bash
# PM2 status
pm2 status

# Nginx status
systemctl status nginx

# Disk usage
df -h

# Memory usage
free -h
```

### Backup Configuration

```bash
# Backup .env files
cp /var/www/ai-desktop/.env /root/ai-desktop.env.backup
cp /var/www/act/agent-sdk/.env /root/act-agent.env.backup

# Backup database
cp /var/www/ai-desktop/data/flow-builder.db /root/flow-builder.db.backup

# Backup flows
tar -czf /root/flows-backup.tar.gz /var/www/act/flows/
```

---

## Security Notes

### Sandbox Bypass

The `IS_SANDBOX=true` and `ALLOW_SANDBOX_BYPASS=true` settings are **required** for VPS deployments running as root. This:

- Allows the agent to execute with full system access
- Is **necessary** for workflow automation
- Should **ONLY** be used on trusted VPS servers
- Should **NEVER** be used on local development machines

### API Key Security

- API keys are stored in browser localStorage (client-side)
- For production, use environment variables in `.env` files
- Never commit `.env` files to version control
- Rotate API keys regularly

### Firewall

Consider adding firewall rules:

```bash
ufw allow 80/tcp
ufw allow 22/tcp
ufw enable
```

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/tajalagawani/ai-desktop/issues
- Check PM2 logs: `pm2 logs ai-desktop`
- Check Nginx logs: `tail -f /var/log/nginx/error.log`

---

**Last Updated:** November 2025
**Version:** 1.0.0
