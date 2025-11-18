#!/usr/bin/env bash
#
# AI Desktop VPS Installation - FROM GITHUB ONLY
# No local file uploads - everything from GitHub
#
# Usage:
#   SSH_PASSWORD="your_password" ./vps-install-from-github.sh root@92.112.181.127 sk-ant-api03-YOUR_KEY
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

if ! command -v sshpass &> /dev/null; then
    echo -e "${RED}Error: sshpass required. Install: brew install sshpass${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AI Desktop VPS Installation (GitHub)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

ssh_exec() {
    sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_HOST" "$@"
}

echo -e "${YELLOW}Installing on VPS...${NC}"

ssh_exec "bash -s" << REMOTE_SCRIPT
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\${YELLOW}Step 1: Clean old installations\${NC}"
export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH
pm2 delete all 2>/dev/null || true
rm -rf /var/www/ai-desktop
rm -rf /var/www/act
docker system prune -af 2>/dev/null || true
echo "✓ Cleaned"

echo -e "\${YELLOW}Step 2: Install system dependencies\${NC}"
apt-get update -qq
apt-get install -y -qq git curl build-essential python3 python3-pip nginx >/dev/null 2>&1
echo "✓ Dependencies installed"

echo -e "\${YELLOW}Step 3: Install Node.js 22\${NC}"
if [ ! -d /root/.nvm ]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh 2>/dev/null | bash >/dev/null 2>&1
fi
export NVM_DIR="/root/.nvm"
[ -s "\$NVM_DIR/nvm.sh" ] && . "\$NVM_DIR/nvm.sh"
nvm install 22 >/dev/null 2>&1
nvm use 22
nvm alias default 22
echo "✓ Node.js 22 installed"

echo -e "\${YELLOW}Step 4: Install PM2\${NC}"
export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH
npm install -g pm2 >/dev/null 2>&1
echo "✓ PM2 installed"

echo -e "\${YELLOW}Step 5: Clone ACT from GitHub\${NC}"
mkdir -p /var/www
cd /var/www
if [ -d "act" ]; then
    cd act && git pull
else
    git clone https://github.com/tajalagawani/actservice.git act
fi
echo "✓ ACT cloned"

echo -e "\${YELLOW}Step 6: Install ACT dependencies\${NC}"
export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH
echo "  Installing MCP dependencies..."
cd /var/www/act/mcp
npm install --silent
echo "  Installing Agent SDK dependencies..."
cd /var/www/act/agent-sdk
npm install --silent
echo "  Installing Python dependencies..."
python3 -m pip install --quiet --break-system-packages anthropic python-dotenv requests aiohttp
echo "✓ ACT dependencies installed"

echo -e "\${YELLOW}Step 7: Configure ACT\${NC}"
cat > /var/www/act/agent-sdk/.env << 'EOF'
ANTHROPIC_API_KEY=${API_KEY}
ACT_ROOT=/var/www/act
MCP_SERVER_PATH=/var/www/act/mcp/index.js
FLOWS_DIR=/var/www/act/flows
SIGNATURE_PATH=/var/www/act/mcp/signatures/user.act.sig
DEFAULT_MODEL=claude-sonnet-4-5-20250929
VERBOSE=true
STREAM_MODE=true
ALLOW_SANDBOX_BYPASS=true
IS_SANDBOX=true
EOF
echo "✓ ACT configured"

echo -e "\${YELLOW}Step 8: Clone AI Desktop from GitHub\${NC}"
cd /var/www
if [ -d "ai-desktop" ]; then
    echo "  Pulling latest changes..."
    cd ai-desktop && git checkout vps-deployment && git pull
    echo "  Installing dependencies..."
    npm install --silent
else
    echo "  Cloning repository (vps-deployment branch)..."
    git clone -b vps-deployment https://github.com/tajalagawani/ai-desktop.git
    cd ai-desktop
    echo "  Installing dependencies..."
    npm install --silent
fi
echo "✓ AI Desktop cloned and dependencies installed"

echo -e "\${YELLOW}Step 9: Configure AI Desktop\${NC}"
cat > /var/www/ai-desktop/.env << 'EOF'
PORT=80
NODE_ENV=production
ANTHROPIC_API_KEY=${API_KEY}
USE_CLAUDE_CLI_AUTH=false
ENCRYPTION_KEY=b7e3f8a2d9c4e1f6a8b3d7c2e9f4a1b6
FILE_MANAGER_ROOT=/var/www
SHOW_HIDDEN_FILES=false
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
ALLOW_SANDBOX_BYPASS=true
EOF
echo "✓ AI Desktop configured"

echo -e "\${YELLOW}Step 10: Build AI Desktop\${NC}"
export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH
cd /var/www/ai-desktop
rm -rf .next
echo "  Building Next.js application (this may take a few minutes)..."
npm run build
echo "✓ Built"

echo -e "\${YELLOW}Step 11: Stop Nginx (not needed)\${NC}"
systemctl stop nginx || true
systemctl disable nginx || true
echo "✓ Nginx disabled (app runs directly on port 80)"

echo -e "\${YELLOW}Step 12: Start with PM2\${NC}"
export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH
cd /var/www/ai-desktop
pm2 start npm --name "ai-desktop" -- start
pm2 save
pm2 startup systemd -u root --hp /root >/dev/null 2>&1 || true
echo "✓ Started"

echo ""
echo -e "\${GREEN}========================================\${NC}"
echo -e "\${GREEN}✅ Installation Complete!\${NC}"
echo -e "\${GREEN}========================================\${NC}"
echo ""
echo "Access: http://\$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_VPS_IP')"
echo ""
pm2 status

REMOTE_SCRIPT

echo ""
echo -e "${GREEN}✅ Done! Access your desktop at: http://${VPS_HOST#*@}${NC}"
echo ""
