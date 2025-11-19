#!/bin/bash

################################################################################
# Orcha - Complete Fresh Installation Script
# Cleans everything and installs from scratch
################################################################################

set -e

# Modern Minimal Color Palette (Claude Code inspired)
ACCENT='\033[38;5;111m'      # Soft Blue
SUCCESS='\033[38;5;108m'     # Sage Green
WARNING='\033[38;5;179m'     # Muted Orange
ERROR='\033[38;5;167m'       # Soft Red
MUTED='\033[38;5;244m'       # Gray
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

clear
echo ""
echo -e "${ERROR}${BOLD}"
 
echo -e "${RESET}"

echo -e "${WARNING}⚠  This will delete everything and start fresh${RESET}"
echo ""
echo -e "${MUTED}What gets removed:${RESET}"
echo -e "  ${DIM}• All PM2 processes${RESET}"
echo -e "  ${DIM}• /root/ai-desktop${RESET}"
echo -e "  ${DIM}• All data and logs${RESET}"
echo -e "  ${DIM}• Nginx configurations${RESET}"
echo ""
read -p "$(echo -e ${DIM}Continue? Type 'yes': ${RESET})" -r CONFIRM
if [[ ! $CONFIRM == "yes" ]]; then
    echo -e "${MUTED}Cancelled${RESET}"
    exit 1
fi

echo ""

################################################################################
# Step 1: COMPLETE CLEANUP
################################################################################
echo -e "${MUTED}[1/12]${RESET} Complete cleanup..."
pm2 delete all 2>/dev/null || true
pm2 kill 2>/dev/null || true
rm -rf /root/ai-desktop
rm -rf /root/.pm2
rm -rf /root/.config/code-server
rm -rf /var/www/repositories/*
rm -rf /var/www/github/*
rm -rf /var/www/ai-desktop
rm -f /etc/nginx/sites-enabled/ai-desktop
rm -f /etc/nginx/sites-available/ai-desktop
rm -rf /etc/nginx/vscode-projects/*
echo -e "${SUCCESS}  ✓${RESET} Cleanup complete"

################################################################################
# Step 2: Install System Dependencies
################################################################################
echo -e "${MUTED}[2/12]${RESET} Installing dependencies..."
apt update -qq
apt install -y curl git nginx ufw -qq > /dev/null 2>&1

# Install Node.js 18.x
if ! command -v node &> /dev/null || [[ $(node -v | cut -d'v' -f2 | cut -d'.' -f1) -lt 18 ]]; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - > /dev/null 2>&1
    apt install -y nodejs -qq > /dev/null 2>&1
fi

npm install -g pm2 > /dev/null 2>&1

# Install code-server
if ! command -v code-server &> /dev/null; then
    curl -fsSL https://code-server.dev/install.sh | sh > /dev/null 2>&1
fi

echo -e "${SUCCESS}  ✓${RESET} Dependencies installed"
echo -e "${DIM}    Node $(node --version) • NPM $(npm --version) • PM2 $(pm2 --version)${RESET}"
if command -v code-server &> /dev/null; then
    echo -e "${DIM}    code-server $(code-server --version | head -n 1)${RESET}"
fi

################################################################################
# Step 3: Setup Directory Structure
################################################################################
echo -e "${MUTED}[3/12]${RESET} Setting up directories..."
mkdir -p /var/www/repositories
mkdir -p /var/www/github
mkdir -p /etc/nginx/vscode-projects
chmod 755 /var/www /var/www/repositories /var/www/github /etc/nginx/vscode-projects
echo -e "${SUCCESS}  ✓${RESET} Directories created"

################################################################################
# Step 4: Clone Repository
################################################################################
echo -e "${MUTED}[4/12]${RESET} Cloning repository..."
cd /root

if git clone -b lightweight-client https://github.com/tajalagawani/ai-desktop.git 2>/dev/null; then
    echo -e "${SUCCESS}  ✓${RESET} Repository cloned ${DIM}(lightweight-client)${RESET}"
elif git clone https://github.com/tajalagawani/ai-desktop.git 2>/dev/null; then
    echo -e "${SUCCESS}  ✓${RESET} Repository cloned ${DIM}(main)${RESET}"
else
    echo -e "${ERROR}  ✗${RESET} Failed to clone repository"
    exit 1
fi

cd /root/ai-desktop

################################################################################
# Step 5: Create Storage Directory
################################################################################
echo -e "${MUTED}[5/12]${RESET} Creating storage..."
mkdir -p storage/{data,logs,flows}

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
echo -e "${SUCCESS}  ✓${RESET} Storage initialized"

################################################################################
# Step 6: Install Backend Dependencies
################################################################################
echo -e "${MUTED}[6/12]${RESET} Installing backend..."
cd /root/ai-desktop/backend
npm install --production > /dev/null 2>&1
echo -e "${SUCCESS}  ✓${RESET} Backend ready"

################################################################################
# Step 7: Configure Backend Environment
################################################################################
echo -e "${MUTED}[7/12]${RESET} Configuring backend..."
VPS_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

cat > /root/ai-desktop/backend/.env << EOF
PORT=3006
NODE_ENV=production
CLIENT_URL=http://$VPS_IP
CORS_ORIGINS=http://$VPS_IP,http://$VPS_IP:80,http://localhost:3005
LOG_LEVEL=info
FILE_MANAGER_ROOT=/var/www
DATA_DIR=../storage/data
LOGS_DIR=../storage/logs
FLOWS_DIR=../storage/flows
EOF

echo -e "${SUCCESS}  ✓${RESET} Backend configured"

################################################################################
# Step 8: Install Frontend Dependencies
################################################################################
echo -e "${MUTED}[8/12]${RESET} Installing frontend..."
cd /root/ai-desktop
npm install > /dev/null 2>&1
echo -e "${SUCCESS}  ✓${RESET} Frontend ready"

################################################################################
# Step 9: Configure Frontend Environment
################################################################################
echo -e "${MUTED}[9/12]${RESET} Configuring frontend..."
cat > /root/ai-desktop/.env << EOF
PORT=3005
NEXT_PUBLIC_API_URL=http://localhost:3006
NODE_ENV=production
FILE_MANAGER_ROOT=/var/www
ANTHROPIC_API_KEY=
USE_CLAUDE_CLI_AUTH=false
ENCRYPTION_KEY=$(openssl rand -hex 16)
SHOW_HIDDEN_FILES=false
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
EOF

echo -e "${SUCCESS}  ✓${RESET} Frontend configured"

################################################################################
# Step 10: Build Frontend
################################################################################
echo -e "${MUTED}[10/12]${RESET} Building frontend..."
cd /root/ai-desktop
npm run build > /dev/null 2>&1
echo -e "${SUCCESS}  ✓${RESET} Frontend built"

################################################################################
# Step 11: Start Services with PM2
################################################################################
echo -e "${MUTED}[11/12]${RESET} Starting services..."
cd /root/ai-desktop/backend
pm2 start server.js --name ai-desktop-backend --time
pm2 save > /dev/null 2>&1

cd /root/ai-desktop
pm2 start npm --name ai-desktop-frontend -- start --time
pm2 save > /dev/null 2>&1

pm2 startup systemd -u root --hp /root > /dev/null 2>&1 || true
pm2 save > /dev/null 2>&1
sleep 3
echo -e "${SUCCESS}  ✓${RESET} Services running"

################################################################################
# Step 12: Configure Nginx
################################################################################
echo -e "${MUTED}[12/12]${RESET} Configuring proxy..."
cat > /etc/nginx/sites-available/ai-desktop << 'NGINX_EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 500M;

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
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }

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

    location /health {
        proxy_pass http://localhost:3006;
        access_log off;
    }

    include /etc/nginx/vscode-projects/*.conf;
}
NGINX_EOF

ln -sf /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

if nginx -t > /dev/null 2>&1; then
    systemctl restart nginx
    echo -e "${SUCCESS}  ✓${RESET} Nginx configured"
else
    echo -e "${ERROR}  ✗${RESET} Nginx config failed"
    nginx -t
    exit 1
fi

################################################################################
# Configure Firewall
################################################################################
ufw allow 80/tcp > /dev/null 2>&1 || true
ufw allow 22/tcp > /dev/null 2>&1 || true

################################################################################
# Installation Complete
################################################################################
sleep 2
echo ""
echo -e "${SUCCESS}${BOLD}Fresh installation complete${RESET}"
echo ""
echo -e "${DIM}───────────────────────────────────────────${RESET}"
echo -e "  ${ACCENT}http://$VPS_IP${RESET}"
echo -e "${DIM}───────────────────────────────────────────${RESET}"
echo ""
echo -e "${MUTED}Services${RESET}"
echo -e "  Backend          ${DIM}localhost:3006${RESET}"
echo -e "  Frontend         ${DIM}localhost:3005${RESET}"
echo -e "  Health check     ${DIM}/health${RESET}"
echo ""
echo -e "${MUTED}Locations${RESET}"
echo -e "  App              ${DIM}/root/ai-desktop${RESET}"
echo -e "  Storage          ${DIM}/root/ai-desktop/storage${RESET}"
echo -e "  Repositories     ${DIM}/var/www/repositories${RESET}"
echo ""
echo -e "${MUTED}Commands${RESET}"
echo -e "  ${DIM}pm2 status${RESET}       View services"
echo -e "  ${DIM}pm2 logs${RESET}         View logs"
echo -e "  ${DIM}pm2 restart all${RESET}  Restart"
echo ""

# Test installation
echo -e "${MUTED}Testing...${RESET}"
sleep 2

if curl -s http://localhost:3006/health > /dev/null 2>&1; then
    echo -e "${SUCCESS}  ✓${RESET} Backend ${DIM}healthy${RESET}"
else
    echo -e "${WARNING}  ⚠${RESET} Backend ${DIM}starting...${RESET}"
fi

if curl -s http://localhost:3005 > /dev/null 2>&1; then
    echo -e "${SUCCESS}  ✓${RESET} Frontend ${DIM}healthy${RESET}"
else
    echo -e "${WARNING}  ⚠${RESET} Frontend ${DIM}starting...${RESET}"
fi

if curl -s http://localhost:80 > /dev/null 2>&1; then
    echo -e "${SUCCESS}  ✓${RESET} Proxy ${DIM}healthy${RESET}"
else
    echo -e "${WARNING}  ⚠${RESET} Proxy ${DIM}check failed${RESET}"
fi

echo ""
pm2 status
echo ""

################################################################################
# Optional: Install Flow Builder
################################################################################
echo -e "${DIM}───────────────────────────────────────────${RESET}"
echo -e "${MUTED}Optional: Flow Builder${RESET}"
echo -e "${DIM}───────────────────────────────────────────${RESET}"
echo ""
echo -e "${DIM}Provides:${RESET}"
echo -e "  ${DIM}• Visual workflow automation${RESET}"
echo -e "  ${DIM}• 150+ workflow nodes${RESET}"
echo -e "  ${DIM}• ACT workflow engine${RESET}"
echo ""
read -p "$(echo -e ${DIM}Install Flow Builder? Type 'yes': ${RESET})" -r INSTALL_ACT

if [[ $INSTALL_ACT == "yes" ]]; then
    echo ""
    echo -e "${MUTED}Installing Flow Builder...${RESET}"

    ACT_REPO_URL="https://github.com/tajalagawani/actservice.git"
    ACT_DIR="/var/www/act"

    if [ ! -d "$ACT_DIR" ]; then
        mkdir -p /var/www
        cd /var/www
        git clone $ACT_REPO_URL act > /dev/null 2>&1

        if [ -d "$ACT_DIR" ]; then
            if [ -d "$ACT_DIR/mcp" ]; then
                cd $ACT_DIR/mcp
                npm install > /dev/null 2>&1
            fi

            if [ -d "$ACT_DIR/agent-sdk" ]; then
                cd $ACT_DIR/agent-sdk
                npm install > /dev/null 2>&1
            fi

            python3 -m pip install --quiet --break-system-packages anthropic python-dotenv requests aiohttp 2>/dev/null || \
            pip3 install anthropic python-dotenv requests aiohttp > /dev/null 2>&1

            mkdir -p $ACT_DIR/flows
            mkdir -p $ACT_DIR/mcp/signatures

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

            cat >> /root/ai-desktop/.env << ACT_DESKTOP_ENV

# Flow Builder / ACT Integration
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
ALLOW_SANDBOX_BYPASS=true
ACT_DESKTOP_ENV

            pm2 restart ai-desktop-frontend > /dev/null 2>&1

            echo -e "${SUCCESS}  ✓${RESET} Flow Builder installed"
            echo -e "${DIM}    Location: /var/www/act${RESET}"
        else
            echo -e "${WARNING}  ⚠${RESET} ACT clone failed, skipping"
        fi
    else
        cat >> /root/ai-desktop/.env << ACT_DESKTOP_ENV

# Flow Builder / ACT Integration
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
ALLOW_SANDBOX_BYPASS=true
ACT_DESKTOP_ENV
        pm2 restart ai-desktop-frontend > /dev/null 2>&1
        echo -e "${SUCCESS}  ✓${RESET} ACT already installed"
    fi
else
    echo -e "${MUTED}  Skipped${RESET}"
fi

echo ""
echo -e "${DIM}───────────────────────────────────────────${RESET}"
echo -e "${SUCCESS}All done!${RESET} Access Orcha at ${ACCENT}http://$VPS_IP${RESET}"
echo -e "${DIM}───────────────────────────────────────────${RESET}"
echo ""
echo -e "${MUTED}Next steps:${RESET}"
echo -e "  ${DIM}1${RESET} Open ${ACCENT}http://$VPS_IP${RESET} in browser"
echo -e "  ${DIM}2${RESET} Clone a repository"
echo -e "  ${DIM}3${RESET} Deploy your first app"
echo ""
echo -e "${DIM}To add API key:${RESET}"
echo -e "  ${DIM}nano /root/ai-desktop/.env${RESET}"
echo -e "  ${DIM}Set: ANTHROPIC_API_KEY=your_key${RESET}"
echo -e "  ${DIM}pm2 restart ai-desktop-frontend${RESET}"
echo ""