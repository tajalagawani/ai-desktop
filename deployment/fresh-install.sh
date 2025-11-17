#!/bin/bash
set -e

echo "========================================="
echo "AI Desktop - Fresh Installation Script"
echo "========================================="
echo ""
echo "⚠️  WARNING: This will DELETE everything and start fresh!"
echo ""

# Check if running with --yes flag or piped (auto-confirm)
if [[ "$1" == "--yes" ]] || [[ ! -t 0 ]]; then
    echo "Auto-confirming installation..."
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

echo -e "${YELLOW}[1/10] Stopping and removing old installations...${NC}"
# Change to safe directory first to avoid "directory not found" errors
cd /root
pm2 delete all 2>/dev/null || true
pm2 kill 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
apt remove --purge nginx nginx-common -y 2>/dev/null || true
apt autoremove -y
rm -rf /var/www/ai-desktop
rm -rf /var/www/github
rm -rf /var/www/vscode-workspaces
rm -rf /etc/nginx/vscode-projects
rm -rf /root/.pm2
rm -rf /root/.config/code-server
echo -e "${GREEN}✓ Old installations removed${NC}"

echo -e "${YELLOW}[2/10] Updating system...${NC}"
apt update && apt upgrade -y
echo -e "${GREEN}✓ System updated${NC}"

echo -e "${YELLOW}[3/10] Installing Node.js...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs git python3 python3-pip
npm install -g pm2
echo -e "${GREEN}✓ Node.js installed${NC}"

echo -e "${YELLOW}[4/10] Installing Nginx and utilities...${NC}"
apt install -y nginx netcat-openbsd
echo -e "${GREEN}✓ Nginx installed${NC}"

echo -e "${YELLOW}[5/10] Installing Docker...${NC}"
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

echo -e "${YELLOW}[6/10] Cloning AI Desktop...${NC}"
mkdir -p /var/www
cd /var/www
git clone https://github.com/tajalagawani/ai-desktop.git
cd ai-desktop
echo -e "${GREEN}✓ Repository cloned${NC}"

echo -e "${YELLOW}[7/10] Installing dependencies and building...${NC}"
npm install
npm run build
mkdir -p logs
mkdir -p data
echo -e "${GREEN}✓ Build completed${NC}"

echo -e "${YELLOW}[8/10] Setting up Nginx for VS Code...${NC}"
bash deployment/nginx-setup.sh
echo -e "${GREEN}✓ Nginx configured${NC}"

echo -e "${YELLOW}[9/10] Installing code-server...${NC}"
if ! command -v code-server &> /dev/null; then
    curl -fsSL https://code-server.dev/install.sh | sh
    echo -e "${GREEN}✓ code-server installed${NC}"
else
    echo -e "${GREEN}✓ code-server already installed${NC}"
fi

echo -e "${YELLOW}[10/10] Setting up ACT Docker flows...${NC}"
cd /var/www/ai-desktop/components/apps/act-docker
pip3 install flask flask-cors requests
mkdir -p flows
python3 docker-compose-generator.py
docker-compose up -d --build

# Start Flow Manager API in background
nohup python3 flow_manager_api.py > /var/www/ai-desktop/logs/flow-manager-api.log 2>&1 &
echo -e "${GREEN}✓ ACT Docker flows started${NC}"

echo -e "${YELLOW}[Final] Starting AI Desktop with PM2...${NC}"
cd /var/www/ai-desktop
pm2 start deployment/ecosystem.config.js
pm2 save

# Setup PM2 startup
echo -e "${YELLOW}Setting up PM2 to start on boot...${NC}"
pm2 startup systemd -u root --hp /root | tail -n 1 | bash

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "AI Desktop is now running!"
echo ""
echo -e "Access your AI Desktop at: ${GREEN}http://$(hostname -I | awk '{print $1}')${NC}"
echo ""
echo -e "System Status:"
pm2 status
echo ""
echo -e "Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo -e "Nginx Status:"
systemctl status nginx --no-pager | head -3
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Open AI Desktop in your browser"
echo "2. Clone a repository in GitHub Desktop"
echo "3. Open it in VS Code Editor"
echo "4. Access VS Code at: http://YOUR_IP/vscode/repo-name/"
echo ""
echo -e "${GREEN}Enjoy your AI Desktop! 🚀${NC}"
