#!/bin/bash

################################################################################
# AI Desktop - Complete VPS Installation Script
# One script to handle EVERYTHING from cleanup to full deployment
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
BRANCH="lightweight-client"

echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 AI Desktop - Complete VPS Installation               ║
║                                                           ║
║   ✅ Full Cleanup & Fresh Install                         ║
║   ✅ No PostgreSQL - JSON Storage                         ║
║   ✅ Auto-configured & Production Ready                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

################################################################################
# Step 1: COMPLETE CLEANUP - Remove EVERYTHING
################################################################################
echo -e "${YELLOW}[1/12] COMPLETE CLEANUP - Removing ALL old installations...${NC}"

# Stop and remove ALL PM2 processes
echo "  → Stopping all PM2 processes..."
pm2 delete all 2>/dev/null || true
pm2 kill 2>/dev/null || true

# Remove PM2 configs
rm -rf /root/.pm2

# Remove AI Desktop
rm -rf $APP_DIR

# Remove VS Code configs
rm -rf /root/.config/code-server

# Clean up repositories
echo "  → Cleaning repository storage..."
rm -rf /var/www/repositories/*
rm -rf /var/www/github/*

# Clean up deployment artifacts
rm -rf /var/www/ai-desktop

# Clean up logs
rm -rf /var/log/ai-desktop

# Clean up nginx configs
rm -f /etc/nginx/sites-enabled/ai-desktop
rm -f /etc/nginx/sites-available/ai-desktop
rm -rf /etc/nginx/vscode-projects

echo -e "${GREEN}✓ Complete cleanup finished${NC}"

################################################################################
# Step 2: Install System Dependencies
################################################################################
echo -e "${YELLOW}[2/12] Installing system dependencies...${NC}"

apt update -qq
apt install -y curl git nginx ufw -qq

# Install Node.js 18.x
if ! command -v node &> /dev/null || [[ $(node -v | cut -d'v' -f2 | cut -d'.' -f1) -lt 18 ]]; then
    echo "  → Installing Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - > /dev/null 2>&1
    apt install -y nodejs -qq
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
mkdir -p /var/www/ai-desktop/logs
mkdir -p /var/www/ai-desktop/data
mkdir -p /etc/nginx/vscode-projects

# Set permissions
chmod 755 /var/www
chmod 755 /var/www/repositories
chmod 755 /var/www/github
chmod 755 /var/www/ai-desktop
chmod 755 /etc/nginx/vscode-projects

echo -e "${GREEN}✓ Directory structure created${NC}"

################################################################################
# Step 4: Clone Repository
################################################################################
echo -e "${YELLOW}[4/12] Cloning AI Desktop repository...${NC}"

cd /root

# Clone with specific branch
if git clone -b $BRANCH https://github.com/tajalagawani/ai-desktop.git 2>/dev/null; then
    echo -e "${GREEN}✓ Cloned from $BRANCH branch${NC}"
elif git clone https://github.com/tajalagawani/ai-desktop.git 2>/dev/null; then
    echo -e "${GREEN}✓ Cloned from main branch${NC}"
else
    echo -e "${RED}✗ Failed to clone repository${NC}"
    exit 1
fi

cd $APP_DIR

################################################################################
# Step 5: Install Backend Dependencies
################################################################################
echo -e "${YELLOW}[5/12] Installing backend dependencies...${NC}"

cd $APP_DIR/backend
npm install --production > /dev/null 2>&1

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

################################################################################
# Step 6: Configure Backend Environment
################################################################################
echo -e "${YELLOW}[6/12] Configuring backend environment...${NC}"

VPS_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

cat > $APP_DIR/backend/.env << EOF
# Server Configuration
PORT=$BACKEND_PORT
NODE_ENV=production

# Client Configuration
CLIENT_URL=http://$VPS_IP
CORS_ORIGINS=http://$VPS_IP,http://$VPS_IP:80,http://localhost:$FRONTEND_PORT

# Logging
LOG_LEVEL=info

# File Manager - VPS Paths
FILE_MANAGER_ROOT=/var/www
SHOW_HIDDEN_FILES=false

# Data Storage
DATA_DIR=/var/www/ai-desktop/data
EOF

# Initialize empty data files
cat > /var/www/ai-desktop/data/repositories.json << 'EOF'
{
  "repositories": []
}
EOF

cat > /var/www/ai-desktop/data/deployments.json << 'EOF'
{
  "deployments": []
}
EOF

cat > /var/www/ai-desktop/data/mcp-servers.json << 'EOF'
{
  "servers": []
}
EOF

chmod 644 /var/www/ai-desktop/data/*.json

echo -e "${GREEN}✓ Backend configured for VPS${NC}"

################################################################################
# Step 7: Configure Frontend Environment
################################################################################
echo -e "${YELLOW}[7/12] Configuring frontend environment...${NC}"

cat > $APP_DIR/.env << EOF
# Server Configuration
PORT=$FRONTEND_PORT

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:$BACKEND_PORT

# Environment
NODE_ENV=production

# File Manager - VPS Paths (NOT Mac paths!)
FILE_MANAGER_ROOT=/var/www

# Anthropic API (for Flow Builder)
ANTHROPIC_API_KEY=
USE_CLAUDE_CLI_AUTH=false

# Flow Builder / ACT Integration (optional - set if using Flow Builder)
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act

# Security
ENCRYPTION_KEY=$(openssl rand -hex 16)
SHOW_HIDDEN_FILES=false
EOF

echo -e "${GREEN}✓ Frontend configured for VPS${NC}"

################################################################################
# Step 8: Install Frontend Dependencies
################################################################################
echo -e "${YELLOW}[8/12] Installing frontend dependencies...${NC}"

cd $APP_DIR
npm install > /dev/null 2>&1

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

################################################################################
# Step 9: Build Frontend
################################################################################
echo -e "${YELLOW}[9/12] Building frontend application...${NC}"

cd $APP_DIR
npm run build > /dev/null 2>&1

echo -e "${GREEN}✓ Frontend built successfully${NC}"

################################################################################
# Step 10: Start Services with PM2
################################################################################
echo -e "${YELLOW}[10/12] Starting services with PM2...${NC}"

# Start backend
cd $APP_DIR/backend
pm2 start server.js --name ai-desktop-backend --time
pm2 save > /dev/null 2>&1

# Start frontend
cd $APP_DIR
pm2 start npm --name ai-desktop-frontend -- start --time
pm2 save > /dev/null 2>&1

sleep 3

echo -e "${GREEN}✓ Services started${NC}"

################################################################################
# Step 11: Configure Nginx
################################################################################
echo -e "${YELLOW}[11/12] Configuring Nginx reverse proxy...${NC}"

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
# Step 12: Configure Firewall
################################################################################
echo -e "${YELLOW}[12/12] Configuring firewall...${NC}"

# Allow HTTP
ufw allow 80/tcp > /dev/null 2>&1

# Allow SSH (just in case)
ufw allow 22/tcp > /dev/null 2>&1

echo -e "${GREEN}✓ Firewall configured${NC}"

################################################################################
# Setup PM2 Auto-start on Reboot
################################################################################
echo -e "${YELLOW}Setting up PM2 auto-start...${NC}"

pm2 startup systemd -u root --hp /root > /dev/null 2>&1 || true
pm2 save > /dev/null 2>&1

echo -e "${GREEN}✓ PM2 will auto-start on reboot${NC}"

################################################################################
# Installation Complete
################################################################################
sleep 2

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
echo -e "  ✅ Backend API:        http://localhost:$BACKEND_PORT"
echo -e "  ✅ Frontend:           http://localhost:$FRONTEND_PORT"
echo -e "  ✅ Public URL:         ${GREEN}http://$VPS_IP${NC}"
echo -e "  ✅ Health Check:       http://$VPS_IP/health"
echo ""

echo -e "${BLUE}📁 Storage Locations:${NC}"
echo -e "  App Directory:     $APP_DIR"
echo -e "  Data Files:        /var/www/ai-desktop/data/"
echo -e "  Repositories:      /var/www/repositories/"
echo -e "  GitHub Clones:     /var/www/github/"
echo -e "  Deployment Logs:   /var/www/ai-desktop/logs/"
echo ""

echo -e "${BLUE}🔍 Useful Commands:${NC}"
echo -e "  View status:       ${GREEN}pm2 status${NC}"
echo -e "  View logs:         ${GREEN}pm2 logs${NC}"
echo -e "  View backend logs: ${GREEN}pm2 logs ai-desktop-backend${NC}"
echo -e "  View frontend logs:${GREEN}pm2 logs ai-desktop-frontend${NC}"
echo -e "  Restart all:       ${GREEN}pm2 restart all${NC}"
echo -e "  Restart backend:   ${GREEN}pm2 restart ai-desktop-backend${NC}"
echo -e "  Restart frontend:  ${GREEN}pm2 restart ai-desktop-frontend${NC}"
echo ""

echo -e "${BLUE}🧹 Data Management:${NC}"
echo -e "  Clear repositories: ${GREEN}rm -rf /var/www/repositories/* /var/www/github/*${NC}"
echo -e "  Reset data:         ${GREEN}echo '{\"repositories\":[]}' > /var/www/ai-desktop/data/repositories.json${NC}"
echo -e "  View deployments:   ${GREEN}cat /var/www/ai-desktop/data/deployments.json${NC}"
echo ""

# Test installation
echo -e "${YELLOW}🧪 Testing installation...${NC}"
sleep 3

# Test backend health
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend health check: PASSED${NC}"
else
    echo -e "${RED}⚠ Backend health check: FAILED${NC}"
    echo -e "  Run: ${YELLOW}pm2 logs ai-desktop-backend${NC} to debug"
fi

# Test frontend
if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
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
echo -e "${GREEN}🎉 Enjoy AI Desktop!${NC}"
echo ""
