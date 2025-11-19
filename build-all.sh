
#!/bin/bash

################################################################################
# AI Desktop - Build Script
# Builds both client and backend for production
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                               ║${NC}"
echo -e "${BLUE}║   AI Desktop - Build All                      ║${NC}"
echo -e "${BLUE}║                                               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

################################################################################
# Build Backend
################################################################################
echo -e "${GREEN}[1/2] Building Backend...${NC}"
cd backend

if [ ! -d "node_modules" ]; then
    echo "Installing backend dependencies..."
    npm install --production
fi

echo -e "${GREEN}✅ Backend built successfully${NC}"
cd ..

################################################################################
# Build Client
################################################################################
echo -e "${GREEN}[2/2] Building Client...${NC}"
cd client

if [ ! -d "node_modules" ]; then
    echo "Installing client dependencies..."
    npm install
fi

echo "Building static export..."
npm run build

# Calculate bundle size
if [ -d "out" ]; then
    BUNDLE_SIZE=$(du -sh out | cut -f1)
    echo -e "${GREEN}✅ Client built successfully${NC}"
    echo -e "${YELLOW}📦 Bundle size: ${BUNDLE_SIZE}${NC}"
else
    echo -e "${RED}❌ Build failed - out/ directory not found${NC}"
    exit 1
fi

cd ..

################################################################################
# Summary
################################################################################
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}║   🎉 Build Complete!                          ║${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}║   Backend: backend/                           ║${NC}"
echo -e "${GREEN}║   Client:  client/out/                        ║${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}║   Ready for deployment!                       ║${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""
