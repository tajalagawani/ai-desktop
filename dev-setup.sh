#!/bin/bash

################################################################################
# AI Desktop - Mac Development Setup Script
# Sets up local development environment similar to VPS
################################################################################

set -e

# Colors
ACCENT='\033[38;5;111m'
SUCCESS='\033[38;5;108m'
WARNING='\033[38;5;179m'
ERROR='\033[38;5;167m'
MUTED='\033[38;5;244m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

clear
echo ""
echo -e "${ACCENT}${BOLD}AI Desktop - Mac Development Setup${RESET}"
echo ""
echo -e "${WARNING}⚠  This will:${RESET}"
echo ""
echo -e "${MUTED}Actions:${RESET}"
echo -e "  ${DIM}• Stop all PM2 processes${RESET}"
echo -e "  ${DIM}• Clean build directories${RESET}"
echo -e "  ${DIM}• Install dependencies${RESET}"
echo -e "  ${DIM}• Set up development environment${RESET}"
echo -e "  ${DIM}• Start services with PM2${RESET}"
echo ""
read -p "$(echo -e ${DIM}Continue? Type 'yes': ${RESET})" -r CONFIRM
if [[ ! $CONFIRM == "yes" ]]; then
    echo -e "${MUTED}Cancelled${RESET}"
    exit 1
fi

echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

################################################################################
# Step 1: Cleanup
################################################################################
echo -e "${MUTED}[1/10]${RESET} Cleaning up..."
pm2 delete all 2>/dev/null || true
pm2 kill 2>/dev/null || true
rm -rf .next
rm -rf node_modules/.cache
rm -rf backend/node_modules/.cache
echo -e "${SUCCESS}  ✓${RESET} Cleanup complete"

################################################################################
# Step 2: Check Dependencies
################################################################################
echo -e "${MUTED}[2/10]${RESET} Checking dependencies..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${ERROR}  ✗${RESET} Node.js not found. Please install Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [[ $NODE_VERSION -lt 18 ]]; then
    echo -e "${ERROR}  ✗${RESET} Node.js 18+ required (found v$NODE_VERSION)"
    exit 1
fi

# Check PM2
if ! command -v pm2 &> /dev/null; then
    echo -e "${MUTED}Installing PM2...${RESET}"
    npm install -g pm2
fi

echo -e "${SUCCESS}  ✓${RESET} Dependencies OK"
echo -e "${DIM}    Node $(node --version) • NPM $(npm --version) • PM2 $(pm2 --version)${RESET}"

################################################################################
# Step 3: Create Storage Directory
################################################################################
echo -e "${MUTED}[3/10]${RESET} Setting up storage..."
mkdir -p storage/{data,logs,flows}

# Only create files if they don't exist
if [ ! -f storage/data/repositories.json ]; then
    cat > storage/data/repositories.json << 'EOF'
{"repositories": []}
EOF
fi

if [ ! -f storage/data/deployments.json ]; then
    cat > storage/data/deployments.json << 'EOF'
{"deployments": []}
EOF
fi

if [ ! -f storage/data/mcp-servers.json ]; then
    cat > storage/data/mcp-servers.json << 'EOF'
{"servers": []}
EOF
fi

if [ ! -f storage/data/flow-sessions.json ]; then
    cat > storage/data/flow-sessions.json << 'EOF'
{"sessions": []}
EOF
fi

if [ ! -f storage/data/mcp-tokens.json ]; then
    cat > storage/data/mcp-tokens.json << 'EOF'
{}
EOF
fi

# Copy installable services if doesn't exist
if [ ! -f storage/data/installable-services.json ]; then
    cp src/data/installable-services.json storage/data/installable-services.json
fi

chmod -R 755 storage/
echo -e "${SUCCESS}  ✓${RESET} Storage ready"

################################################################################
# Step 4: Install Backend Dependencies
################################################################################
echo -e "${MUTED}[4/10]${RESET} Installing backend..."
cd backend
npm install
cd ..
echo -e "${SUCCESS}  ✓${RESET} Backend dependencies installed"

################################################################################
# Step 5: Configure Backend Environment
################################################################################
echo -e "${MUTED}[5/10]${RESET} Configuring backend..."

if [ ! -f backend/.env ]; then
    cat > backend/.env << 'EOF'
PORT=3006
NODE_ENV=development
CLIENT_URL=http://localhost:3005
CORS_ORIGINS=http://localhost:3005,http://localhost:3001
LOG_LEVEL=info
FILE_MANAGER_ROOT=/var/www
DATA_DIR=../storage/data
LOGS_DIR=../storage/logs
FLOWS_DIR=../storage/flows
EOF
    echo -e "${SUCCESS}  ✓${RESET} Backend environment created"
else
    echo -e "${SUCCESS}  ✓${RESET} Backend environment exists"
fi

################################################################################
# Step 6: Install Frontend Dependencies
################################################################################
echo -e "${MUTED}[6/10]${RESET} Installing frontend..."
npm install
echo -e "${SUCCESS}  ✓${RESET} Frontend dependencies installed"

################################################################################
# Step 7: Configure Frontend Environment
################################################################################
echo -e "${MUTED}[7/10]${RESET} Configuring frontend..."

if [ ! -f .env.local ]; then
    cat > .env.local << 'EOF'
# Development Environment
PORT=3005
NEXT_PUBLIC_API_URL=http://localhost:3006
NEXT_PUBLIC_WS_URL=http://localhost:3006
NODE_ENV=development
FILE_MANAGER_ROOT=/var/www

# Optional: Add your Anthropic API key
ANTHROPIC_API_KEY=

# Security
USE_CLAUDE_CLI_AUTH=false
ENCRYPTION_KEY=dev-encryption-key-change-in-production
SHOW_HIDDEN_FILES=false

# Optional: ACT/Flow Builder paths (if installed)
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
ALLOW_SANDBOX_BYPASS=true
EOF
    echo -e "${SUCCESS}  ✓${RESET} Frontend environment created"
else
    echo -e "${SUCCESS}  ✓${RESET} Frontend environment exists"
fi

################################################################################
# Step 8: Create /var/www directories (for file manager)
################################################################################
echo -e "${MUTED}[8/10]${RESET} Setting up working directories..."
if [ ! -d /var/www ]; then
    echo -e "${WARNING}  ⚠${RESET} /var/www doesn't exist, creating with sudo..."
    sudo mkdir -p /var/www/repositories
    sudo mkdir -p /var/www/github
    sudo chown -R $(whoami) /var/www
else
    mkdir -p /var/www/repositories
    mkdir -p /var/www/github
fi
echo -e "${SUCCESS}  ✓${RESET} Working directories ready"

################################################################################
# Step 9: Build Frontend
################################################################################
echo -e "${MUTED}[9/10]${RESET} Building frontend..."
npm run build
echo -e "${SUCCESS}  ✓${RESET} Frontend built"

################################################################################
# Step 10: Start Services with PM2
################################################################################
echo -e "${MUTED}[10/10]${RESET} Starting services..."

# Start backend
cd backend
pm2 start server.js --name ai-desktop-backend --time --watch
cd ..

# Start frontend
pm2 start npm --name ai-desktop-frontend -- start --time

pm2 save
sleep 2
echo -e "${SUCCESS}  ✓${RESET} Services running"

################################################################################
# Installation Complete
################################################################################
echo ""
echo -e "${SUCCESS}${BOLD}Development setup complete!${RESET}"
echo ""
echo -e "${DIM}───────────────────────────────────────────${RESET}"
echo -e "  ${ACCENT}http://localhost:3005${RESET}"
echo -e "${DIM}───────────────────────────────────────────${RESET}"
echo ""
echo -e "${MUTED}Services${RESET}"
echo -e "  Frontend         ${DIM}http://localhost:3005${RESET}"
echo -e "  Backend API      ${DIM}http://localhost:3006${RESET}"
echo -e "  Backend Health   ${DIM}http://localhost:3006/health${RESET}"
echo ""
echo -e "${MUTED}Storage${RESET}"
echo -e "  Data             ${DIM}$SCRIPT_DIR/storage/data${RESET}"
echo -e "  Logs             ${DIM}$SCRIPT_DIR/storage/logs${RESET}"
echo -e "  Flows            ${DIM}$SCRIPT_DIR/storage/flows${RESET}"
echo ""
echo -e "${MUTED}File Manager Root${RESET}"
echo -e "  Working dir      ${DIM}/var/www${RESET}"
echo ""
echo -e "${MUTED}Commands${RESET}"
echo -e "  ${DIM}pm2 status${RESET}           View services status"
echo -e "  ${DIM}pm2 logs${RESET}             View all logs"
echo -e "  ${DIM}pm2 logs backend${RESET}     View backend logs"
echo -e "  ${DIM}pm2 logs frontend${RESET}    View frontend logs"
echo -e "  ${DIM}pm2 restart all${RESET}      Restart all services"
echo -e "  ${DIM}pm2 stop all${RESET}         Stop all services"
echo ""

# Test services
echo -e "${MUTED}Testing services...${RESET}"
sleep 3

BACKEND_OK=false
FRONTEND_OK=false

for i in {1..5}; do
    if curl -s http://localhost:3006/health > /dev/null 2>&1; then
        BACKEND_OK=true
        break
    fi
    sleep 1
done

for i in {1..5}; do
    if curl -s http://localhost:3005 > /dev/null 2>&1; then
        FRONTEND_OK=true
        break
    fi
    sleep 1
done

if [ "$BACKEND_OK" = true ]; then
    echo -e "${SUCCESS}  ✓${RESET} Backend ${DIM}healthy${RESET}"
else
    echo -e "${WARNING}  ⚠${RESET} Backend ${DIM}check failed - check logs: pm2 logs backend${RESET}"
fi

if [ "$FRONTEND_OK" = true ]; then
    echo -e "${SUCCESS}  ✓${RESET} Frontend ${DIM}healthy${RESET}"
else
    echo -e "${WARNING}  ⚠${RESET} Frontend ${DIM}check failed - check logs: pm2 logs frontend${RESET}"
fi

echo ""
pm2 status
echo ""
echo -e "${DIM}───────────────────────────────────────────${RESET}"
echo -e "${SUCCESS}Ready!${RESET} Open ${ACCENT}http://localhost:3005${RESET} in your browser"
echo -e "${DIM}───────────────────────────────────────────${RESET}"
echo ""
echo -e "${MUTED}Tip: Backend is watching for changes. Frontend requires restart after code changes.${RESET}"
echo ""
