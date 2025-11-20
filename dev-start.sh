#!/bin/bash

################################################################################
# AI Desktop - Development Start Script (Mac/Local)
# Starts all three services for development
################################################################################

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

clear
echo ""
echo -e "${BLUE}AI Desktop - Development Mode${NC}"
echo ""

# Check if running on Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${YELLOW}Warning: This script is designed for Mac development${NC}"
    echo "For VPS deployment, use: ./vps-install.sh"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if .env files exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
fi

if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}Creating backend/.env from backend/.env.example...${NC}"
    cp backend/.env.example backend/.env
fi

echo -e "${GREEN}Starting services...${NC}"
echo ""

# Start with PM2 using ecosystem config
pm2 start ecosystem.config.js --env development

echo ""
echo -e "${GREEN}✓ All services started!${NC}"
echo ""
echo "Services:"
echo -e "  ${BLUE}•${NC} Frontend:  http://localhost:3005"
echo -e "  ${BLUE}•${NC} Backend:   http://localhost:3006"
echo -e "  ${BLUE}•${NC} WebSocket: http://localhost:3007"
echo ""
echo "Commands:"
echo "  pm2 logs            # View all logs"
echo "  pm2 logs ai-desktop-frontend"
echo "  pm2 logs ai-desktop-backend"
echo "  pm2 logs ai-desktop-websocket"
echo "  pm2 stop all        # Stop all services"
echo "  pm2 restart all     # Restart all services"
echo ""
