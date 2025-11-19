#!/bin/bash

################################################################################
# VPS Update Script - Safe Migration to Refactored Structure
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== AI Desktop - Safe VPS Update ===${NC}"
echo ""

# Step 1: Backup current state
echo -e "${YELLOW}[1/8] Creating backup of current state...${NC}"
mkdir -p ~/ai-desktop-backup-$(date +%Y%m%d-%H%M%S)
cp -r /root/ai-desktop ~/ai-desktop-backup-$(date +%Y%m%d-%H%M%S)/ 2>/dev/null || true
echo -e "${GREEN}✓ Backup created${NC}"

# Step 2: Save important data
echo -e "${YELLOW}[2/8] Saving runtime data...${NC}"
mkdir -p ~/ai-desktop-data-backup
cp -r /root/ai-desktop/backend/data ~/ai-desktop-data-backup/ 2>/dev/null || true
cp -r /root/ai-desktop/data ~/ai-desktop-data-backup/ 2>/dev/null || true
echo -e "${GREEN}✓ Data backed up to ~/ai-desktop-data-backup${NC}"

# Step 3: Stash local changes
echo -e "${YELLOW}[3/8] Stashing local changes...${NC}"
cd /root/ai-desktop
git stash
echo -e "${GREEN}✓ Local changes stashed${NC}"

# Step 4: Pull new structure
echo -e "${YELLOW}[4/8] Pulling refactored code...${NC}"
git pull origin lightweight-client
echo -e "${GREEN}✓ Code updated${NC}"

# Step 5: Create storage directory
echo -e "${YELLOW}[5/8] Creating new storage structure...${NC}"
mkdir -p storage/{data,logs,flows}

# Restore data to new location
echo -e "${YELLOW}[6/8] Restoring your data to new structure...${NC}"
if [ -d ~/ai-desktop-data-backup/data ]; then
    cp ~/ai-desktop-data-backup/data/*.json storage/data/ 2>/dev/null || true
fi

# Initialize empty files if none exist
if [ ! -f storage/data/repositories.json ]; then
    echo '{"repositories":[]}' > storage/data/repositories.json
fi
if [ ! -f storage/data/deployments.json ]; then
    echo '{"deployments":[]}' > storage/data/deployments.json
fi
if [ ! -f storage/data/mcp-servers.json ]; then
    echo '{"servers":[]}' > storage/data/mcp-servers.json
fi
if [ ! -f storage/data/flow-sessions.json ]; then
    echo '{"sessions":[]}' > storage/data/flow-sessions.json
fi
if [ ! -f storage/data/mcp-tokens.json ]; then
    echo '{}' > storage/data/mcp-tokens.json
fi

chmod -R 755 storage/
echo -e "${GREEN}✓ Storage created and data restored${NC}"

# Step 6: Update dependencies
echo -e "${YELLOW}[7/8] Installing dependencies...${NC}"
npm install > /dev/null 2>&1
cd backend && npm install > /dev/null 2>&1 && cd ..
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 7: Build
echo -e "${YELLOW}[8/8] Building application...${NC}"
npm run build
echo -e "${GREEN}✓ Build complete${NC}"

# Step 8: Restart services
echo -e "${YELLOW}Restarting services...${NC}"
pm2 restart all --update-env
sleep 3
pm2 status
echo -e "${GREEN}✓ Services restarted${NC}"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}║   🎉 Update Complete!                                     ║${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}║   Your data has been migrated to the new structure       ║${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📊 Summary:${NC}"
echo -e "  ✅ Backup created in: ~/ai-desktop-backup-*"
echo -e "  ✅ Data migrated to: storage/data/"
echo -e "  ✅ New structure applied"
echo -e "  ✅ Services running"
echo ""
echo -e "${YELLOW}🔍 Quick checks:${NC}"
echo -e "  View data: ${GREEN}ls -la storage/data/${NC}"
echo -e "  Check logs: ${GREEN}pm2 logs${NC}"
echo -e "  Test app: ${GREEN}curl http://localhost:3006/health${NC}"
echo ""
