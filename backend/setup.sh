#!/bin/bash

################################################################################
# Backend Setup Script
# Works on both Mac (development) and VPS (production)
# Lightweight - No Database Required!
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                               ║${NC}"
echo -e "${BLUE}║   AI Desktop Backend - Setup                  ║${NC}"
echo -e "${BLUE}║   (Lightweight - JSON Storage)                ║${NC}"
echo -e "${BLUE}║                                               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Detect environment
if [[ "$OSTYPE" == "darwin"* ]]; then
    ENV_TYPE="development"
    echo -e "${GREEN}Detected: macOS (Development Environment)${NC}"
else
    ENV_TYPE="production"
    echo -e "${GREEN}Detected: Linux (Production Environment)${NC}"
fi

################################################################################
# Step 1: Check Node.js
################################################################################
echo -e "${YELLOW}[1/3] Checking Node.js...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found!${NC}"
    echo "Please install Node.js >= 18.0.0"
    echo "Visit: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.js version must be >= 18.0.0${NC}"
    echo "Current version: $(node -v)"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node -v)${NC}"

################################################################################
# Step 2: Install Dependencies
################################################################################
echo -e "${YELLOW}[2/3] Installing dependencies...${NC}"

npm install

echo -e "${GREEN}✅ Dependencies installed${NC}"

################################################################################
# Step 3: Create .env File
################################################################################
echo -e "${YELLOW}[3/3] Creating environment file...${NC}"

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists, backing up...${NC}"
    cp .env .env.backup.$(date +%s)
fi

if [[ "$ENV_TYPE" == "development" ]]; then
    # Development environment (Mac)
    cat > .env << EOF
# Development Environment (Mac)
PORT=3006
NODE_ENV=development

# Client URL
CLIENT_URL=http://localhost:3005

# CORS Configuration
CORS_ORIGINS=http://localhost:3005,http://localhost:3001

# Logging
LOG_LEVEL=debug
EOF

    echo -e "${GREEN}✅ Development .env created${NC}"
    echo -e "${BLUE}Backend will run on: http://localhost:3006${NC}"
else
    # Production environment (VPS)
    # Get VPS IP
    VPS_IP=$(curl -s ifconfig.me || echo "YOUR_VPS_IP")

    cat > .env << EOF
# Production Environment (VPS)
PORT=3000
NODE_ENV=production

# Client URL
CLIENT_URL=http://$VPS_IP

# JWT Configuration (for future authentication)
JWT_SECRET=$(openssl rand -base64 64)
JWT_EXPIRES_IN=7d

# CORS Configuration
CORS_ORIGINS=http://$VPS_IP

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/ai-desktop/backend.log
EOF

    echo -e "${GREEN}✅ Production .env created${NC}"
    echo -e "${BLUE}Backend will run on: http://localhost:3000 (internal)${NC}"
    echo -e "${BLUE}Public access via nginx on port 80${NC}"

    # Create log directory
    sudo mkdir -p /var/log/ai-desktop
    sudo chown $USER:$USER /var/log/ai-desktop
fi

# Create data directory for JSON storage
echo -e "${YELLOW}Creating data directory for JSON storage...${NC}"
mkdir -p data
echo -e "${GREEN}✅ Data directory created${NC}"

################################################################################
# Success
################################################################################
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}║   ✅ Backend Setup Complete!                  ║${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""

if [[ "$ENV_TYPE" == "development" ]]; then
    echo -e "${BLUE}Development Mode:${NC}"
    echo "  Start backend: npm run dev"
    echo "  Or: npm start"
    echo "  Backend URL: http://localhost:3006"
    echo ""
    echo -e "${BLUE}Storage:${NC}"
    echo "  Type: JSON Files (Lightweight)"
    echo "  Location: ./data/"
    echo "  No database setup required!"
else
    echo -e "${BLUE}Production Mode:${NC}"
    echo "  Start with PM2: npm run pm2:start"
    echo "  View logs: npm run pm2:logs"
    echo "  Monitor: npm run pm2:monit"
    echo "  Stop: npm run pm2:stop"
    echo ""
    echo -e "${BLUE}Storage:${NC}"
    echo "  Type: JSON Files (Lightweight)"
    echo "  Location: ./data/"
    echo "  Backup: tar -czf backup.tar.gz data/"
fi

echo ""
echo -e "${GREEN}Next steps:${NC}"
if [[ "$ENV_TYPE" == "development" ]]; then
    echo "  1. npm run dev"
    echo "  2. Test: curl http://localhost:3006/health"
else
    echo "  1. npm run pm2:start"
    echo "  2. Configure nginx (see nginx.conf.example)"
    echo "  3. Test: curl http://localhost:3000/health"
fi
echo ""
echo -e "${BLUE}Features:${NC}"
echo "  ✅ No database required"
echo "  ✅ Lightweight JSON storage"
echo "  ✅ Easy backup and restore"
echo "  ✅ Portable between machines"
echo ""
