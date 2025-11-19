#!/bin/bash

################################################################################
# AI Desktop - Complete Fresh Installation Script
# Cleans everything and installs from scratch
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 AI Desktop - Fresh Installation                      ║
║                                                           ║
║   ⚠️  WARNING: This will DELETE everything!               ║
║   ✅ Creates a completely fresh installation              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Confirmation
echo -e "${YELLOW}This script will:${NC}"
echo "  1. Stop all PM2 processes"
echo "  2. Delete /root/ai-desktop completely"
echo "  3. Clean up all data and logs"
echo "  4. Install fresh from GitHub"
echo "  5. Set up everything from scratch"
echo ""
read -p "Are you sure you want to continue? (yes/no): " -r CONFIRM
if [[ ! $CONFIRM == "yes" ]]; then
    echo -e "${RED}Installation cancelled.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Starting fresh installation...${NC}"
echo ""

################################################################################
# Step 1: COMPLETE CLEANUP
################################################################################
echo -e "${YELLOW}[1/12] Cleaning up old installation...${NC}"

# Stop all PM2 processes
pm2 delete all 2>/dev/null || true
pm2 kill 2>/dev/null || true

# Remove AI Desktop directory
rm -rf /root/ai-desktop

# Remove PM2 configs
rm -rf /root/.pm2

# Remove code-server configs
rm -rf /root/.config/code-server

# Clean up repositories
rm -rf /var/www/repositories/*
rm -rf /var/www/github/*

# Clean up old deployment artifacts
rm -rf /var/www/ai-desktop

# Clean up nginx configs
rm -f /etc/nginx/sites-enabled/ai-desktop
rm -f /etc/nginx/sites-available/ai-desktop
rm -rf /etc/nginx/vscode-projects/*

echo -e "${GREEN}✓ Complete cleanup done${NC}"

################################################################################
# Step 2: Install System Dependencies
################################################################################
echo -e "${YELLOW}[2/12] Installing system dependencies...${NC}"

apt update -qq
apt install -y curl git nginx ufw -qq > /dev/null 2>&1

# Install Node.js 18.x
if ! command -v node &> /dev/null || [[ $(node -v | cut -d'v' -f2 | cut -d'.' -f1) -lt 18 ]]; then
    echo "  → Installing Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - > /dev/null 2>&1
    apt install -y nodejs -qq > /dev/null 2>&1
fi

# Install PM2
npm install -g pm2 > /dev/null 2>&1

# Install code-server
if ! command -v code-server &> /dev/null; then
    echo "  → Installing code-server..."
    curl -fsSL https://code-server.dev/install.sh | sh > /dev/null 2>&1
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo "    Node: $(node --version)"
echo "    NPM: $(npm --version)"
echo "    PM2: $(pm2 --version)"
if command -v code-server &> /dev/null; then
    echo "    code-server: $(code-server --version | head -n 1)"
fi

################################################################################
# Step 3: Setup Directory Structure
################################################################################
echo -e "${YELLOW}[3/12] Setting up directory structure...${NC}"

# Create necessary directories
mkdir -p /var/www/repositories
mkdir -p /var/www/github
mkdir -p /etc/nginx/vscode-projects

# Set permissions
chmod 755 /var/www
chmod 755 /var/www/repositories
chmod 755 /var/www/github
chmod 755 /etc/nginx/vscode-projects

echo -e "${GREEN}✓ Directory structure created${NC}"

################################################################################
# Step 4: Clone Repository
################################################################################
echo -e "${YELLOW}[4/12] Cloning AI Desktop repository...${NC}"

cd /root

# Clone with specific branch
if git clone -b lightweight-client https://github.com/tajalagawani/ai-desktop.git 2>/dev/null; then
    echo -e "${GREEN}✓ Cloned from lightweight-client branch${NC}"
elif git clone https://github.com/tajalagawani/ai-desktop.git 2>/dev/null; then
    echo -e "${GREEN}✓ Cloned from main branch${NC}"
else
    echo -e "${RED}✗ Failed to clone repository${NC}"
    exit 1
fi

cd /root/ai-desktop

################################################################################
# Step 5: Create Storage Directory
################################################################################
echo -e "${YELLOW}[5/12] Creating storage directory for runtime data...${NC}"

mkdir -p storage/{data,logs,flows}

# Initialize empty data files
cat > storage/data/repositories.json << 'EOF'
{"repositories": []}
EOF

cat > storage/data/deployments.json << 'EOF'
{"deployments": []}
EOF

cat > storage/data/mcp-servers.json << 'EOF'
{"servers": []}
EOF

cat > storage/data/flow-sessions.json << 'EOF'
{"sessions": []}
EOF

cat > storage/data/mcp-tokens.json << 'EOF'
{}
EOF

chmod -R 755 storage/

echo -e "${GREEN}✓ Storage directory created${NC}"

################################################################################
# Step 6: Install Backend Dependencies
################################################################################
echo -e "${YELLOW}[6/12] Installing backend dependencies...${NC}"

cd /root/ai-desktop/backend
npm install --production > /dev/null 2>&1

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

################################################################################
# Step 7: Configure Backend Environment
################################################################################
echo -e "${YELLOW}[7/12] Configuring backend environment...${NC}"

VPS_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

cat > /root/ai-desktop/backend/.env << EOF
# Production Environment (VPS)
PORT=3006
NODE_ENV=production

# Client Configuration
CLIENT_URL=http://$VPS_IP
CORS_ORIGINS=http://$VPS_IP,http://$VPS_IP:80,http://localhost:3005

# Logging
LOG_LEVEL=info

# File Manager
FILE_MANAGER_ROOT=/var/www

# Data Storage (NEW: storage directory)
DATA_DIR=../storage/data
LOGS_DIR=../storage/logs
FLOWS_DIR=../storage/flows
EOF

echo -e "${GREEN}✓ Backend configured for VPS${NC}"

################################################################################
# Step 8: Install Frontend Dependencies
################################################################################
echo -e "${YELLOW}[8/12] Installing frontend dependencies...${NC}"

cd /root/ai-desktop
npm install > /dev/null 2>&1

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

################################################################################
# Step 9: Configure Frontend Environment
################################################################################
echo -e "${YELLOW}[9/12] Configuring frontend environment...${NC}"

cat > /root/ai-desktop/.env << EOF
# AI Desktop - Frontend Configuration

# Server Configuration
PORT=3005

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:3006

# Environment
NODE_ENV=production

# File Manager - VPS Paths
FILE_MANAGER_ROOT=/var/www

# Anthropic API (Optional - for Flow Builder)
# Get your API key from: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=

# Claude CLI Authentication Mode
USE_CLAUDE_CLI_AUTH=false

# Security
ENCRYPTION_KEY=$(openssl rand -hex 16)
SHOW_HIDDEN_FILES=false

# Flow Builder / ACT Integration (Optional)
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
EOF

echo -e "${GREEN}✓ Frontend configured for VPS${NC}"

################################################################################
# Step 10: Build Frontend
################################################################################
echo -e "${YELLOW}[10/12] Building frontend application...${NC}"

cd /root/ai-desktop
npm run build > /dev/null 2>&1

echo -e "${GREEN}✓ Frontend built successfully${NC}"

################################################################################
# Step 11: Start Services with PM2
################################################################################
echo -e "${YELLOW}[11/12] Starting services with PM2...${NC}"

# Start backend
cd /root/ai-desktop/backend
pm2 start server.js --name ai-desktop-backend --time
pm2 save > /dev/null 2>&1

# Start frontend
cd /root/ai-desktop
pm2 start npm --name ai-desktop-frontend -- start --time
pm2 save > /dev/null 2>&1

# Setup PM2 startup
pm2 startup systemd -u root --hp /root > /dev/null 2>&1 || true
pm2 save > /dev/null 2>&1

sleep 3

echo -e "${GREEN}✓ Services started${NC}"

################################################################################
# Step 12: Configure Nginx
################################################################################
echo -e "${YELLOW}[12/12] Configuring Nginx reverse proxy...${NC}"

cat > /etc/nginx/sites-available/ai-desktop << 'NGINX_EOF'
server {
    listen 80;
    server_name _;

    # Increase max body size for file uploads
    client_max_body_size 500M;

    # Frontend - Next.js app
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
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:3006;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long-running operations
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }

    # WebSocket - Socket.io
    location /socket.io/ {
        proxy_pass http://localhost:3006;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:3006;
        access_log off;
    }

    # Include dynamic VS Code project configs (created by deployment system)
    include /etc/nginx/vscode-projects/*.conf;
}
NGINX_EOF

# Enable site
ln -sf /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart nginx
if nginx -t > /dev/null 2>&1; then
    systemctl restart nginx
    echo -e "${GREEN}✓ Nginx configured and restarted${NC}"
else
    echo -e "${RED}✗ Nginx configuration test failed${NC}"
    nginx -t
    exit 1
fi

################################################################################
# Configure Firewall
################################################################################
echo -e "${YELLOW}Configuring firewall...${NC}"

# Allow HTTP
ufw allow 80/tcp > /dev/null 2>&1 || true

# Allow SSH (just in case)
ufw allow 22/tcp > /dev/null 2>&1 || true

echo -e "${GREEN}✓ Firewall configured${NC}"

################################################################################
# Installation Complete
################################################################################
sleep 2

echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎉 Fresh Installation Complete!                         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}📊 Installation Summary:${NC}"
echo -e "  ✅ Backend API:        http://localhost:3006"
echo -e "  ✅ Frontend:           http://localhost:3005"
echo -e "  ✅ Public URL:         ${GREEN}http://$VPS_IP${NC}"
echo -e "  ✅ Health Check:       http://$VPS_IP/health"
echo ""

echo -e "${BLUE}📁 Installation Locations:${NC}"
echo -e "  App Directory:     /root/ai-desktop"
echo -e "  Source Code:       /root/ai-desktop/src"
echo -e "  Runtime Data:      /root/ai-desktop/storage"
echo -e "  Repositories:      /var/www/repositories"
echo -e "  GitHub Clones:     /var/www/github"
echo ""

echo -e "${BLUE}🔍 Useful Commands:${NC}"
echo -e "  View status:       ${GREEN}pm2 status${NC}"
echo -e "  View logs:         ${GREEN}pm2 logs${NC}"
echo -e "  View backend logs: ${GREEN}pm2 logs ai-desktop-backend${NC}"
echo -e "  View frontend logs:${GREEN}pm2 logs ai-desktop-frontend${NC}"
echo -e "  Restart all:       ${GREEN}pm2 restart all${NC}"
echo ""

echo -e "${BLUE}📂 Directory Structure:${NC}"
echo -e "  ${GREEN}/root/ai-desktop/${NC}"
echo -e "    ├── src/           # Source code (from git)"
echo -e "    ├── storage/       # Runtime data (gitignored)"
echo -e "    │   ├── data/      # JSON database"
echo -e "    │   ├── logs/      # Deployment logs"
echo -e "    │   └── flows/     # Generated workflows"
echo -e "    ├── backend/       # Backend server"
echo -e "    ├── public/        # Static assets"
echo -e "    └── docs/          # Documentation"
echo ""

# Test installation
echo -e "${YELLOW}🧪 Testing installation...${NC}"
sleep 3

# Test backend health
if curl -s http://localhost:3006/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend health check: PASSED${NC}"
else
    echo -e "${RED}⚠ Backend health check: FAILED${NC}"
    echo -e "  Run: ${YELLOW}pm2 logs ai-desktop-backend${NC} to debug"
fi

# Test frontend
if curl -s http://localhost:3005 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend check: PASSED${NC}"
else
    echo -e "${RED}⚠ Frontend check: FAILED${NC}"
    echo -e "  Run: ${YELLOW}pm2 logs ai-desktop-frontend${NC} to debug"
fi

# Test nginx
if curl -s http://localhost:80 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Nginx proxy check: PASSED${NC}"
else
    echo -e "${RED}⚠ Nginx proxy check: FAILED${NC}"
    echo -e "  Run: ${YELLOW}nginx -t${NC} to check nginx config"
fi

# Show PM2 status
echo ""
echo -e "${YELLOW}📊 PM2 Process Status:${NC}"
pm2 status

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 AI Desktop is now running at: ${BLUE}http://$VPS_IP${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo -e "  1. Open ${BLUE}http://$VPS_IP${NC} in your browser"
echo -e "  2. Try cloning a repository through the GitHub app"
echo -e "  3. Deploy your first application!"
echo ""
echo -e "${YELLOW}⚙️  Optional - Set API Key:${NC}"
echo -e "  To use Flow Builder, add your Anthropic API key:"
echo -e "  ${GREEN}nano /root/ai-desktop/.env${NC}"
echo -e "  Then set: ANTHROPIC_API_KEY=your_key_here"
echo -e "  And restart: ${GREEN}pm2 restart ai-desktop-frontend${NC}"
echo ""
echo -e "${GREEN}🎉 Enjoy AI Desktop!${NC}"
echo ""

################################################################################
# Optional: Install Flow Builder (ACT)
################################################################################
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Optional: Flow Builder Installation${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Flow Builder provides:${NC}"
echo "  • Visual workflow automation with Claude AI"
echo "  • 150+ workflow nodes for integrations, databases, APIs"
echo "  • ACT workflow engine"
echo ""
read -p "Do you want to install Flow Builder? (yes/no): " -r INSTALL_ACT

if [[ $INSTALL_ACT == "yes" ]]; then
    echo ""
    echo -e "${YELLOW}[OPTIONAL] Installing Flow Builder with ACT...${NC}"

    ACT_REPO_URL="https://github.com/tajalagawani/actservice.git"
    ACT_DIR="/var/www/act"

    if [ ! -d "$ACT_DIR" ]; then
        echo "  → Cloning ACT repository..."
        mkdir -p /var/www
        cd /var/www
        git clone $ACT_REPO_URL act > /dev/null 2>&1

        if [ -d "$ACT_DIR" ]; then
            # Install MCP dependencies
            echo "  → Installing MCP dependencies..."
            if [ -d "$ACT_DIR/mcp" ]; then
                cd $ACT_DIR/mcp
                npm install > /dev/null 2>&1
            fi

            # Install Agent SDK dependencies
            echo "  → Installing Agent SDK dependencies..."
            if [ -d "$ACT_DIR/agent-sdk" ]; then
                cd $ACT_DIR/agent-sdk
                npm install > /dev/null 2>&1
            fi

            # Install Python dependencies
            echo "  → Installing Python dependencies..."
            python3 -m pip install --quiet --break-system-packages anthropic python-dotenv requests aiohttp 2>/dev/null || \
            pip3 install anthropic python-dotenv requests aiohttp > /dev/null 2>&1

            # Create necessary directories
            mkdir -p $ACT_DIR/flows
            mkdir -p $ACT_DIR/mcp/signatures

            # Configure ACT environment
            echo "  → Configuring ACT..."
            cat > $ACT_DIR/agent-sdk/.env << 'ACT_ENV'
ACT_ROOT=/var/www/act
MCP_SERVER_PATH=/var/www/act/mcp/index.js
FLOWS_DIR=/var/www/act/flows
SIGNATURE_PATH=/var/www/act/mcp/signatures/user.act.sig
DEFAULT_MODEL=claude-sonnet-4-5-20250929
VERBOSE=true
STREAM_MODE=true
ALLOW_SANDBOX_BYPASS=true
IS_SANDBOX=true
ACT_ENV

            # Update AI Desktop .env to include ACT paths
            echo "  → Linking ACT to AI Desktop..."
            cat >> /root/ai-desktop/.env << ACT_DESKTOP_ENV

# Flow Builder / ACT Integration (Installed)
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
ALLOW_SANDBOX_BYPASS=true
ACT_DESKTOP_ENV

            # Restart frontend to load new env vars
            pm2 restart ai-desktop-frontend > /dev/null 2>&1

            echo -e "${GREEN}✓ Flow Builder with ACT installed${NC}"
            echo -e "${BLUE}  ACT Location: /var/www/act${NC}"
            echo -e "${BLUE}  Flows Directory: /var/www/act/flows${NC}"
        else
            echo -e "${YELLOW}⚠ ACT clone failed, continuing without Flow Builder${NC}"
        fi
    else
        echo -e "${GREEN}✓ ACT already installed${NC}"

        # Still configure the link
        cat >> /root/ai-desktop/.env << ACT_DESKTOP_ENV

# Flow Builder / ACT Integration
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
ALLOW_SANDBOX_BYPASS=true
ACT_DESKTOP_ENV

        # Restart frontend
        pm2 restart ai-desktop-frontend > /dev/null 2>&1
    fi
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ Flow Builder Installation Complete${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
else
    echo -e "${BLUE}✓ Skipping Flow Builder installation${NC}"
    echo -e "${YELLOW}  You can install it later by running this script again${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All installations complete!${NC}"
echo ""
