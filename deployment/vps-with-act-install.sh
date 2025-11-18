#!/bin/bash
set -e

echo "========================================="
echo "AI Desktop + ACT - Fresh VPS Installation"
echo "========================================="
echo ""
echo "⚠️  WARNING: This will DELETE everything and start fresh!"
echo ""

# Check if running with --yes flag or if STDIN is not a terminal (piped from curl)
if [[ "$1" == "--yes" ]]; then
    echo "Auto-confirming installation..."
elif [[ ! -t 0 ]]; then
    # Script is piped from curl, auto-confirm
    echo "Auto-confirming installation (piped from curl)..."
else
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]
    then
        echo "Installation cancelled."
        exit 1
    fi
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[1/12] Stopping and removing old installations...${NC}"
cd /root
pm2 delete all 2>/dev/null || true
pm2 kill 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
apt remove --purge nginx nginx-common -y 2>/dev/null || true
apt autoremove -y
rm -rf /var/www/ai-desktop
rm -rf /var/www/act
rm -rf /var/www/github
rm -rf /var/www/vscode-workspaces
rm -rf /etc/nginx/vscode-projects
rm -rf /root/.pm2
rm -rf /root/.config/code-server
echo -e "${GREEN}✓ Old installations removed${NC}"

echo -e "${YELLOW}[2/12] Updating system...${NC}"
apt update && apt upgrade -y
echo -e "${GREEN}✓ System updated${NC}"

echo -e "${YELLOW}[3/12] Installing Node.js...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs git python3 python3-pip build-essential
npm install -g pm2
echo -e "${GREEN}✓ Node.js installed${NC}"

echo -e "${YELLOW}[4/12] Installing Nginx and utilities...${NC}"
apt install -y nginx netcat-openbsd rsync
echo -e "${GREEN}✓ Nginx and utilities installed${NC}"

echo -e "${YELLOW}[5/12] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl start docker
    systemctl enable docker
    apt install docker-compose-plugin -y
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

echo -e "${YELLOW}[6/12] Cloning ACT Repository (actwith-mcp)...${NC}"
mkdir -p /var/www
cd /var/www
git clone https://github.com/tajalagawani/actwith-mcp.git act
cd act
echo -e "${GREEN}✓ ACT Repository cloned${NC}"

echo -e "${YELLOW}[7/12] Installing ACT dependencies...${NC}"
# Install MCP server dependencies
cd /var/www/act/mcp
npm install
cd /var/www/act

# Install Python dependencies
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p flows
mkdir -p mcp/signatures
mkdir -p app
echo -e "${GREEN}✓ ACT dependencies installed${NC}"

echo -e "${YELLOW}[8/12] Cloning AI Desktop...${NC}"
cd /var/www
git clone https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop
echo -e "${GREEN}✓ Repository cloned${NC}"

echo -e "${YELLOW}[9/12] Installing desktop dependencies and building...${NC}"
npm install
npm run build
mkdir -p logs
mkdir -p data
echo -e "${GREEN}✓ Build completed${NC}"

echo -e "${YELLOW}[10/12] Configuring environment files...${NC}"

# Configure Desktop App .env
cat > /var/www/ai-desktop/.env << 'EOFENV'
# =============================================================================
# AI Desktop VPS Configuration
# =============================================================================

# Server Configuration
PORT=3005
NODE_ENV=production

# IMPORTANT: Set your API keys below
ANTHROPIC_API_KEY=

# Security (IMPORTANT: Generate with: openssl rand -base64 32)
SESSION_SECRET=
ENCRYPTION_KEY=

# File Manager
FILE_MANAGER_ROOT=/var/www

# Claude CLI Auth
USE_CLAUDE_CLI_AUTH=false

# =============================================================================
# FLOW BUILDER / ACT INTEGRATION
# =============================================================================

# Path to ACT agent-sdk (points to external actwith-mcp repository)
AGENT_SDK_PATH=/var/www/act/agent-sdk

# Path to ACT root directory
ACT_ROOT=/var/www/act
EOFENV

# Configure Agent SDK .env
cat > /var/www/act/agent-sdk/.env << 'EOFAGENT'
# Claude API Key (Required for Agent SDK)
ANTHROPIC_API_KEY=

# Paths (Point to VPS ACT installation)
ACT_ROOT=/var/www/act
MCP_SERVER_PATH=/var/www/act/mcp/index.js
FLOWS_DIR=/var/www/act/flows
SIGNATURE_PATH=/var/www/act/mcp/signatures/user.act.sig

# Agent Configuration
DEFAULT_MODEL=claude-sonnet-4-5-20250929
VERBOSE=true
STREAM_MODE=true
EOFAGENT

echo -e "${GREEN}✓ Environment files created${NC}"
echo -e "${YELLOW}⚠ IMPORTANT: Edit /var/www/ai-desktop/.env and add your API keys!${NC}"

echo -e "${YELLOW}[11/12] Creating ACT service management scripts...${NC}"
cd /var/www/act

cat > start-services.sh << 'EOFSTART'
#!/bin/bash
echo "Starting ACT Services..."
cd /var/www/act

# Start MCP Server
echo "✓ Starting MCP Server..."
pm2 start mcp/index.js --name "act-mcp-server" \
  --log /var/www/ai-desktop/logs/act-mcp.log

# Start Python API (optional)
if [ -f flow_manager_api.py ]; then
  echo "✓ Starting Flow Manager API on port 8000..."
  pm2 start flow_manager_api.py --name "act-flow-api" \
    --interpreter python3 \
    --log /var/www/ai-desktop/logs/act-api.log
fi

pm2 save
echo ""
echo "ACT Services Started!"
echo "  - MCP Server: ✓"
echo "  - Flow API: ✓ (port 8000)"
echo ""
EOFSTART

cat > stop-services.sh << 'EOFSTOP'
#!/bin/bash
echo "Stopping ACT Services..."
pm2 delete act-mcp-server 2>/dev/null || true
pm2 delete act-flow-api 2>/dev/null || true
pm2 save
echo "ACT Services Stopped."
EOFSTOP

chmod +x start-services.sh stop-services.sh
echo -e "${GREEN}✓ Service scripts created${NC}"

echo -e "${YELLOW}[12/12] Setting up services...${NC}"

# Setup Nginx for VS Code
cd /var/www/ai-desktop
bash deployment/nginx-setup.sh

# Install code-server
if ! command -v code-server &> /dev/null; then
    curl -fsSL https://code-server.dev/install.sh | sh
    echo -e "${GREEN}✓ code-server installed${NC}"
else
    echo -e "${GREEN}✓ code-server already installed${NC}"
fi

# Start ACT services
echo -e "${YELLOW}Starting ACT services...${NC}"
cd /var/www/act
./start-services.sh

# Start Desktop App
echo -e "${YELLOW}Starting Desktop App...${NC}"
cd /var/www/ai-desktop
pm2 start npm --name "ai-desktop" -- start
pm2 save

# Setup PM2 to start on boot
echo -e "${YELLOW}Setting up PM2 startup...${NC}"
pm2 startup systemd

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo -e "${GREEN}✓ AI Desktop installed at: /var/www/ai-desktop${NC}"
echo -e "${GREEN}✓ ACT installed at: /var/www/act${NC}"
echo ""
echo "🌐 Access:"
echo "  Desktop App: http://YOUR_VPS_IP:3005"
echo "  Flow API: http://localhost:8000"
echo ""
echo "📊 Status:"
echo "  Check: pm2 status"
echo "  Logs: pm2 logs"
echo ""
echo "⚙️ Next Steps:"
echo "  1. Edit /var/www/ai-desktop/.env and add your ANTHROPIC_API_KEY"
echo "  2. Edit /var/www/act/agent-sdk/.env and add your ANTHROPIC_API_KEY"
echo "  3. Generate SESSION_SECRET: openssl rand -base64 32"
echo "  4. Generate ENCRYPTION_KEY: openssl rand -hex 16"
echo "  5. Restart: pm2 restart all"
echo ""
echo "🔥 PM2 Startup Command:"
echo "  Run the command shown above to enable auto-start on boot"
echo ""
echo "🎉 Ready to use Flow Builder!"
echo ""
