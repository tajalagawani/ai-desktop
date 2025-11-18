#!/usr/bin/env bash
#
# AI Desktop VPS Complete Installation Script
# This script installs everything from scratch on a clean VPS
#
# Usage:
#   SSH_PASSWORD="your_password" ./vps-complete-install.sh root@92.112.181.127 sk-ant-api03-YOUR_KEY_HERE
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST="${1}"
API_KEY="${2}"
SSH_PASSWORD="${SSH_PASSWORD}"

if [ -z "$VPS_HOST" ]; then
    echo -e "${RED}Error: VPS host required${NC}"
    echo "Usage: SSH_PASSWORD='password' $0 root@ip.address sk-ant-api03-..."
    exit 1
fi

if [ -z "$API_KEY" ]; then
    echo -e "${RED}Error: Anthropic API key required${NC}"
    echo "Usage: SSH_PASSWORD='password' $0 root@ip.address sk-ant-api03-..."
    exit 1
fi

if [ -z "$SSH_PASSWORD" ]; then
    echo -e "${RED}Error: SSH_PASSWORD environment variable required${NC}"
    echo "Usage: SSH_PASSWORD='password' $0 root@ip.address sk-ant-api03-..."
    exit 1
fi

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo -e "${RED}Error: sshpass is required but not installed${NC}"
    echo "Install it with: brew install sshpass (macOS) or apt-get install sshpass (Linux)"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AI Desktop VPS Complete Installation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}VPS Host:${NC} $VPS_HOST"
echo -e "${GREEN}API Key:${NC} ${API_KEY:0:20}..."
echo ""

# Helper function to run SSH commands
ssh_exec() {
    sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_HOST" "$@"
}

# Helper function to upload files
ssh_upload() {
    sshpass -p "$SSH_PASSWORD" scp -o StrictHostKeyChecking=no "$@"
}

echo -e "${YELLOW}Step 1/15: Clean VPS (remove old installations)${NC}"
ssh_exec "
    # Stop PM2 if running
    export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH
    pm2 delete all || true
    pm2 save --force || true

    # Remove old installations
    rm -rf /var/www/ai-desktop
    rm -rf /var/www/act
    rm -rf /var/www/act-backup

    # Remove old Docker images/containers to free space
    docker system prune -af || true

    echo '✓ VPS cleaned'
"

echo ""
echo -e "${YELLOW}Step 2/15: Install system dependencies${NC}"
ssh_exec "
    apt-get update
    apt-get install -y git curl build-essential python3 python3-pip python3-venv nginx
    echo '✓ System dependencies installed'
"

echo ""
echo -e "${YELLOW}Step 3/15: Install Node.js 22 via NVM${NC}"
ssh_exec "
    # Install NVM if not already installed
    if [ ! -d /root/.nvm ]; then
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    fi

    # Load NVM
    export NVM_DIR=\"/root/.nvm\"
    [ -s \"\$NVM_DIR/nvm.sh\" ] && . \"\$NVM_DIR/nvm.sh\"

    # Install Node.js 22
    nvm install 22
    nvm use 22
    nvm alias default 22

    # Verify installation
    node --version
    npm --version

    echo '✓ Node.js 22 installed'
"

echo ""
echo -e "${YELLOW}Step 4/15: Install PM2 globally${NC}"
ssh_exec "
    export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH
    npm install -g pm2
    pm2 --version
    echo '✓ PM2 installed'
"

echo ""
echo -e "${YELLOW}Step 5/15: Create directory structure${NC}"
ssh_exec "
    mkdir -p /var/www/ai-desktop
    mkdir -p /var/www/act
    mkdir -p /var/www/act/agent-sdk
    mkdir -p /var/www/act/mcp
    mkdir -p /var/www/act/flows
    echo '✓ Directory structure created'
"

echo ""
echo -e "${YELLOW}Step 6/15: Upload ACT system (from local)${NC}"
# Create tar of ACT from local system
LOCAL_ACT_PATH="/Users/tajnoah/Downloads/potree-develop 2/backend/ceviopro/actwith-mcp"
if [ ! -d "$LOCAL_ACT_PATH" ]; then
    echo -e "${RED}Error: ACT source not found at $LOCAL_ACT_PATH${NC}"
    exit 1
fi

echo "  Creating ACT archive..."
tar -czf /tmp/act-clean.tar.gz -C "$LOCAL_ACT_PATH" .

echo "  Uploading ACT to VPS..."
ssh_upload /tmp/act-clean.tar.gz "$VPS_HOST:/tmp/"

echo "  Extracting ACT on VPS..."
ssh_exec "
    cd /var/www/act
    tar -xzf /tmp/act-clean.tar.gz
    rm /tmp/act-clean.tar.gz
    echo '✓ ACT uploaded and extracted'
"

rm /tmp/act-clean.tar.gz

echo ""
echo -e "${YELLOW}Step 7/15: Install ACT dependencies${NC}"
ssh_exec "
    export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH

    # Install MCP npm dependencies
    cd /var/www/act/mcp
    npm install

    # Install Agent SDK npm dependencies
    cd /var/www/act/agent-sdk
    npm install

    # Install Python dependencies (excluding ML packages to save space)
    cd /var/www/act
    python3 -m pip install --upgrade pip

    # Install only essential Python packages (skip torch, triton, numpy to save 3GB+)
    python3 -m pip install anthropic python-dotenv requests aiohttp

    echo '✓ ACT dependencies installed'
"

echo ""
echo -e "${YELLOW}Step 8/15: Configure ACT environment${NC}"
ssh_exec "
    # Create agent-sdk .env
    cat > /var/www/act/agent-sdk/.env << 'EOF'
ANTHROPIC_API_KEY=${API_KEY}
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

    echo '✓ ACT environment configured'
"

echo ""
echo -e "${YELLOW}Step 9/15: Clone and build AI Desktop${NC}"
ssh_exec "
    export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH

    cd /var/www
    git clone https://github.com/tajalagawani/ai-desktop.git
    cd ai-desktop

    npm install

    echo '✓ AI Desktop cloned and dependencies installed'
"

echo ""
echo -e "${YELLOW}Step 10/15: Upload local modifications${NC}"
echo "  Uploading security settings UI..."
ssh_upload lib/flow-builder/stores/settings-store.ts "$VPS_HOST:/var/www/ai-desktop/lib/flow-builder/stores/"
ssh_upload components/flow-builder/FlowBuilderSettings.tsx "$VPS_HOST:/var/www/ai-desktop/components/flow-builder/"

echo "  Uploading API routes..."
ssh_exec "mkdir -p /var/www/ai-desktop/app/api/flow-builder/settings"
ssh_upload app/api/flow-builder/settings/route.ts "$VPS_HOST:/var/www/ai-desktop/app/api/flow-builder/settings/"
ssh_upload app/api/flow-builder/messages/route.ts "$VPS_HOST:/var/www/ai-desktop/app/api/flow-builder/messages/"

echo "  Uploading agent integration..."
ssh_upload lib/flow-builder/hooks/use-agent.ts "$VPS_HOST:/var/www/ai-desktop/lib/flow-builder/hooks/"
ssh_upload lib/flow-builder/agent-manager.js "$VPS_HOST:/var/www/ai-desktop/lib/flow-builder/"
ssh_upload agent-sdk/index.js "$VPS_HOST:/var/www/ai-desktop/agent-sdk/"
ssh_upload server.js "$VPS_HOST:/var/www/ai-desktop/"

echo "  Uploading utilities..."
ssh_exec "mkdir -p /var/www/ai-desktop/lib/utils"
ssh_upload lib/utils/uuid.ts "$VPS_HOST:/var/www/ai-desktop/lib/utils/"
ssh_upload lib/utils/index.ts "$VPS_HOST:/var/www/ai-desktop/lib/utils/"

echo "✓ Local modifications uploaded"

echo ""
echo -e "${YELLOW}Step 11/15: Configure AI Desktop environment${NC}"
ssh_exec "
    cat > /var/www/ai-desktop/.env << 'EOF'
# Server Configuration
PORT=3005
NODE_ENV=production

# Anthropic API Configuration
ANTHROPIC_API_KEY=${API_KEY}
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

    echo '✓ AI Desktop environment configured'
"

echo ""
echo -e "${YELLOW}Step 12/15: Build AI Desktop${NC}"
ssh_exec "
    export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH
    cd /var/www/ai-desktop

    rm -rf .next
    npm run build

    echo '✓ AI Desktop built'
"

echo ""
echo -e "${YELLOW}Step 13/15: Configure Nginx${NC}"
ssh_exec "
    # Backup default config
    cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup || true

    # Create AI Desktop Nginx config
    cat > /etc/nginx/sites-available/ai-desktop << 'NGINX_EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;
    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # WebSocket support for terminals
    location /api/terminal/ws {
        proxy_pass http://localhost:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_read_timeout 86400;
    }

    # WebSocket support for service logs
    location /api/services/logs/ws {
        proxy_pass http://localhost:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }

    # Socket.IO support for Flow Builder
    location /socket.io/ {
        proxy_pass http://localhost:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
}
NGINX_EOF

    # Enable site
    rm -f /etc/nginx/sites-enabled/default
    ln -sf /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/

    # Test and reload Nginx
    nginx -t
    systemctl reload nginx

    echo '✓ Nginx configured'
"

echo ""
echo -e "${YELLOW}Step 14/15: Start AI Desktop with PM2${NC}"
ssh_exec "
    export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH
    cd /var/www/ai-desktop

    # Start with PM2
    pm2 start npm --name \"ai-desktop\" -- start
    pm2 save

    # Configure PM2 to start on boot
    pm2 startup systemd -u root --hp /root

    echo '✓ AI Desktop started with PM2'
"

echo ""
echo -e "${YELLOW}Step 15/15: Verify installation${NC}"
sleep 5  # Wait for app to start

ssh_exec "
    export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH

    echo ''
    echo '=== PM2 Status ==='
    pm2 status

    echo ''
    echo '=== PM2 Logs (last 10 lines) ==='
    pm2 logs ai-desktop --lines 10 --nostream

    echo ''
    echo '=== Disk Usage ==='
    df -h / | tail -1

    echo ''
    echo '=== Port 3005 Status ==='
    netstat -tulpn | grep 3005 || echo 'Port 3005 not yet listening (may need a few more seconds)'
"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Access your AI Desktop at:${NC}"
echo -e "${GREEN}http://${VPS_HOST#*@}${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Open the URL above in your browser"
echo "2. Click 'Flow Builder' app"
echo "3. Click Settings (gear icon) → API Keys tab"
echo "4. Verify your API key is: ${API_KEY:0:20}..."
echo "5. Click Settings → Security tab"
echo "6. Review warnings and enable 'Allow Sandbox Bypass' if you understand the risks"
echo "7. Save settings"
echo "8. Test creating a flow!"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  pm2 logs ai-desktop              # View logs"
echo "  pm2 restart ai-desktop           # Restart app"
echo "  pm2 stop ai-desktop              # Stop app"
echo "  pm2 status                       # Check status"
echo ""
