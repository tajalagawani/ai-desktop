#!/bin/bash

################################################################################
# AI Desktop - Lightweight One-Command Installation
# No PostgreSQL - JSON File Storage Only
################################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/root/ai-desktop"
BACKEND_PORT=3006
FRONTEND_PORT=3005
NGINX_PORT=80

echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 AI Desktop - Lightweight Installation                ║
║                                                           ║
║   ✅ No PostgreSQL Required                               ║
║   ✅ JSON File Storage                                    ║
║   ✅ Auto-configured & Ready                              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Ask about Flow Builder
echo -e "${YELLOW}Do you want to install Flow Builder (ACT integration)?${NC}"
echo "  1) No  - Core features only (recommended for most users)"
echo "  2) Yes - Include Flow Builder with ACT workflow engine"
read -p "Choice (1-2) [1]: " -n 1 -r INSTALL_FLOW_BUILDER
echo ""
INSTALL_FLOW_BUILDER=${INSTALL_FLOW_BUILDER:-1}

################################################################################
# Step 1: Clean Up Old Installation
################################################################################
echo -e "${YELLOW}[1/10] Cleaning up old installation...${NC}"
pm2 delete all 2>/dev/null || true
pm2 kill 2>/dev/null || true
rm -rf $APP_DIR
rm -rf /root/.pm2
rm -rf /root/.config/code-server
echo -e "${GREEN}✓ Cleanup complete${NC}"

################################################################################
# Step 2: Install System Dependencies
################################################################################
echo -e "${YELLOW}[2/10] Installing system dependencies...${NC}"
apt update -qq
apt install -y curl git nginx > /dev/null 2>&1

# Install Node.js 18.x
if ! command -v node &> /dev/null || [[ $(node -v | cut -d'v' -f2 | cut -d'.' -f1) -lt 18 ]]; then
    echo "Installing Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - > /dev/null 2>&1
    apt install -y nodejs > /dev/null 2>&1
fi

# Install PM2
npm install -g pm2 > /dev/null 2>&1

# Install code-server
if ! command -v code-server &> /dev/null; then
    echo "Installing code-server..."
    curl -fsSL https://code-server.dev/install.sh | sh > /dev/null 2>&1
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo "  Node: $(node --version)"
echo "  NPM: $(npm --version)"
echo "  PM2: $(pm2 --version)"
if command -v code-server &> /dev/null; then
    echo "  code-server: $(code-server --version | head -n 1)"
fi

################################################################################
# Step 3: Clone Repository
################################################################################
echo -e "${YELLOW}[3/10] Cloning repository...${NC}"
mkdir -p $(dirname $APP_DIR)
cd $(dirname $APP_DIR)

# Try lightweight-client branch first, fallback to main
if git clone -b lightweight-client https://github.com/tajalagawani/ai-desktop.git 2>/dev/null; then
    echo -e "${GREEN}✓ Cloned from lightweight-client branch${NC}"
elif git clone https://github.com/tajalagawani/ai-desktop.git 2>/dev/null; then
    echo -e "${GREEN}✓ Cloned from main branch${NC}"
else
    echo -e "${RED}✗ Failed to clone repository${NC}"
    exit 1
fi

cd $APP_DIR

################################################################################
# Step 4: Install Backend Dependencies
################################################################################
echo -e "${YELLOW}[4/10] Installing backend dependencies...${NC}"
cd $APP_DIR/backend
npm install --production > /dev/null 2>&1
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

################################################################################
# Step 5: Configure Backend Environment
################################################################################
echo -e "${YELLOW}[5/10] Configuring backend environment...${NC}"
cat > $APP_DIR/backend/.env << EOF
PORT=$BACKEND_PORT
NODE_ENV=production
CLIENT_URL=http://$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
CORS_ORIGINS=http://$(curl -s ifconfig.me 2>/dev/null || echo "localhost"),http://$(curl -s ifconfig.me 2>/dev/null || echo "localhost"):80
LOG_LEVEL=info
FILE_MANAGER_ROOT=/var/www
SHOW_HIDDEN_FILES=false
DATA_DIR=./data
EOF

# Create data directory
mkdir -p $APP_DIR/backend/data
echo -e "${GREEN}✓ Backend configured${NC}"

################################################################################
# Step 6: Start Backend with PM2
################################################################################
echo -e "${YELLOW}[6/10] Starting backend service...${NC}"
cd $APP_DIR/backend
pm2 start server.js --name ai-desktop-backend
pm2 save > /dev/null 2>&1
echo -e "${GREEN}✓ Backend started on port $BACKEND_PORT${NC}"

################################################################################
# Step 7: Install Frontend Dependencies
################################################################################
echo -e "${YELLOW}[7/10] Installing frontend dependencies...${NC}"
cd $APP_DIR
npm install > /dev/null 2>&1
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

################################################################################
# Step 8: Configure Frontend Environment
################################################################################
echo -e "${YELLOW}[8/10] Configuring frontend environment...${NC}"
cat > $APP_DIR/.env << EOF
PORT=$FRONTEND_PORT
NEXT_PUBLIC_API_URL=http://localhost:$BACKEND_PORT
NODE_ENV=production
EOF
echo -e "${GREEN}✓ Frontend configured${NC}"

################################################################################
# Step 9: Build and Start Frontend
################################################################################
echo -e "${YELLOW}[9/10] Building and starting frontend...${NC}"
cd $APP_DIR
npm run build > /dev/null 2>&1
pm2 start npm --name ai-desktop-frontend -- start
pm2 save > /dev/null 2>&1
echo -e "${GREEN}✓ Frontend started on port $FRONTEND_PORT${NC}"

################################################################################
# Step 10: Configure Nginx
################################################################################
echo -e "${YELLOW}[10/10] Configuring Nginx...${NC}"

cat > /etc/nginx/sites-available/ai-desktop << 'NGINX_EOF'
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        proxy_pass http://localhost:3005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
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
    }

    # WebSocket
    location /socket.io/ {
        proxy_pass http://localhost:3006;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:3006;
        access_log off;
    }
}
NGINX_EOF

# Enable site and restart nginx
ln -sf /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t > /dev/null 2>&1 && systemctl restart nginx
echo -e "${GREEN}✓ Nginx configured${NC}"

################################################################################
# Step 11: Setup PM2 Startup
################################################################################
echo -e "${YELLOW}Setting up PM2 auto-start...${NC}"
pm2 startup systemd -u root --hp /root > /dev/null 2>&1 || true
pm2 save > /dev/null 2>&1

################################################################################
# Optional: Install Flow Builder
################################################################################
if [ "$INSTALL_FLOW_BUILDER" == "2" ]; then
    echo -e "${YELLOW}[OPTIONAL] Installing Flow Builder with ACT...${NC}"

    ACT_REPO_URL="https://github.com/tajalagawani/actservice.git"
    ACT_DIR="/var/www/act"

    if [ ! -d "$ACT_DIR" ]; then
        echo "Cloning ACT repository..."
        mkdir -p /var/www
        cd /var/www
        git clone $ACT_REPO_URL act > /dev/null 2>&1

        if [ -d "$ACT_DIR" ]; then
            # Install MCP dependencies
            echo "Installing MCP dependencies..."
            if [ -d "$ACT_DIR/mcp" ]; then
                cd $ACT_DIR/mcp
                npm install > /dev/null 2>&1
            fi

            # Install Agent SDK dependencies
            echo "Installing Agent SDK dependencies..."
            if [ -d "$ACT_DIR/agent-sdk" ]; then
                cd $ACT_DIR/agent-sdk
                npm install > /dev/null 2>&1
            fi

            # Install Python dependencies
            echo "Installing Python dependencies..."
            python3 -m pip install --quiet --break-system-packages anthropic python-dotenv requests aiohttp 2>/dev/null || \
            pip3 install anthropic python-dotenv requests aiohttp > /dev/null 2>&1

            # Create necessary directories
            mkdir -p $ACT_DIR/flows
            mkdir -p $ACT_DIR/mcp/signatures

            # Configure ACT environment
            echo "Configuring ACT..."
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

            # Configure AI Desktop to use ACT
            echo "Linking ACT to AI Desktop..."
            cat >> $APP_DIR/.env << ACT_DESKTOP_ENV

# Flow Builder / ACT Integration
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
ALLOW_SANDBOX_BYPASS=true
ACT_DESKTOP_ENV

            echo -e "${GREEN}✓ Flow Builder with ACT installed${NC}"
        else
            echo -e "${YELLOW}⚠ ACT clone failed, continuing without Flow Builder${NC}"
        fi
    else
        echo -e "${GREEN}✓ ACT already installed${NC}"

        # Still configure the link
        cat >> $APP_DIR/.env << ACT_DESKTOP_ENV

# Flow Builder / ACT Integration
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
ALLOW_SANDBOX_BYPASS=true
ACT_DESKTOP_ENV
    fi
fi

################################################################################
# Installation Complete
################################################################################

VPS_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_VPS_IP")

echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎉 Installation Complete!                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}📊 Installation Summary:${NC}"
echo -e "  ✅ Backend API:    http://localhost:$BACKEND_PORT"
echo -e "  ✅ Frontend:       http://localhost:$FRONTEND_PORT"
echo -e "  ✅ Public URL:     http://$VPS_IP"
echo -e "  ✅ Health Check:   http://$VPS_IP/health"
echo ""

echo -e "${BLUE}🔍 Quick Commands:${NC}"
echo -e "  View status:   ${GREEN}pm2 status${NC}"
echo -e "  View logs:     ${GREEN}pm2 logs${NC}"
echo -e "  Restart all:   ${GREEN}pm2 restart all${NC}"
echo ""

echo -e "${BLUE}📁 Data Storage:${NC}"
echo -e "  Backend data:  $APP_DIR/backend/data/"
echo -e "  Format:        JSON files (no database)"
echo ""

echo -e "${YELLOW}🚀 Opening in browser...${NC}"
echo -e "Visit: ${GREEN}http://$VPS_IP${NC}"
echo ""

# Test backend health
echo -e "${YELLOW}Testing installation...${NC}"
sleep 3
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}⚠ Backend might still be starting. Check: pm2 logs ai-desktop-backend${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All done! Enjoy AI Desktop!${NC}"
echo ""
