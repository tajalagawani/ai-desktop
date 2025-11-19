#!/bin/bash

################################################################################
# AI Desktop - Lightweight Client Deployment Script
# Deploys backend server and static frontend to VPS
################################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST="92.112.181.127"
VPS_USER="root"
DEPLOY_DIR="/root/ai-desktop"
BACKEND_PORT="3000"
CLIENT_PORT="80"

echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}║   AI Desktop - Lightweight Deployment         ║${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're on the correct branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "lightweight-client" ]; then
    echo -e "${YELLOW}⚠️  Warning: You are on branch '$CURRENT_BRANCH', not 'lightweight-client'${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Ask for deployment mode
echo -e "${YELLOW}Select deployment mode:${NC}"
echo "1) Full deployment (backend + client)"
echo "2) Backend only"
echo "3) Client only"
read -p "Enter choice (1-3): " -n 1 -r DEPLOY_MODE
echo ""

################################################################################
# Function: Deploy Backend
################################################################################
deploy_backend() {
    echo -e "${GREEN}[1/5] Building backend...${NC}"
    cd backend

    # Install dependencies
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi

    cd ..

    echo -e "${GREEN}[2/5] Uploading backend to VPS...${NC}"
    ssh $VPS_USER@$VPS_HOST "mkdir -p $DEPLOY_DIR"
    rsync -avz --exclude 'node_modules' --exclude '.env' backend/ $VPS_USER@$VPS_HOST:$DEPLOY_DIR/backend/

    echo -e "${GREEN}[3/5] Installing backend dependencies on VPS...${NC}"
    ssh $VPS_USER@$VPS_HOST "cd $DEPLOY_DIR/backend && npm install --production"

    echo -e "${GREEN}[4/5] Creating data directory for JSON storage...${NC}"
    ssh $VPS_USER@$VPS_HOST "mkdir -p $DEPLOY_DIR/backend/data"

    echo -e "${GREEN}[5/5] Starting backend with PM2...${NC}"
    ssh $VPS_USER@$VPS_HOST "cd $DEPLOY_DIR/backend && pm2 delete ai-desktop-backend 2>/dev/null || true"
    ssh $VPS_USER@$VPS_HOST "cd $DEPLOY_DIR/backend && pm2 start server.js --name ai-desktop-backend"
    ssh $VPS_USER@$VPS_HOST "pm2 save"

    echo -e "${GREEN}✅ Backend deployed successfully!${NC}"
}

################################################################################
# Function: Deploy Client
################################################################################
deploy_client() {
    echo -e "${GREEN}[1/4] Building client...${NC}"
    cd client

    # Install dependencies
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi

    # Build static export
    echo "Building Next.js static export..."
    npm run build

    cd ..

    echo -e "${GREEN}[2/4] Uploading client to VPS...${NC}"
    ssh $VPS_USER@$VPS_HOST "mkdir -p /var/www/ai-desktop"
    rsync -avz --delete client/out/ $VPS_USER@$VPS_HOST:/var/www/ai-desktop/

    echo -e "${GREEN}[3/4] Configuring nginx...${NC}"

    # Create nginx config
    ssh $VPS_USER@$VPS_HOST "cat > /etc/nginx/sites-available/ai-desktop << 'EOF'
server {
    listen 80;
    server_name $VPS_HOST;

    # Client - Static files
    location / {
        root /var/www/ai-desktop;
        try_files \$uri \$uri/ /index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
            expires 1y;
            add_header Cache-Control \"public, immutable\";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:$BACKEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /socket.io/ {
        proxy_pass http://localhost:$BACKEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:$BACKEND_PORT;
    }
}
EOF"

    # Enable site
    ssh $VPS_USER@$VPS_HOST "ln -sf /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/"

    echo -e "${GREEN}[4/4] Restarting nginx...${NC}"
    ssh $VPS_USER@$VPS_HOST "nginx -t && systemctl restart nginx"

    echo -e "${GREEN}✅ Client deployed successfully!${NC}"
}

################################################################################
# Execute based on mode
################################################################################

case $DEPLOY_MODE in
    1)
        echo -e "${YELLOW}=== Full Deployment ===${NC}"
        deploy_backend
        deploy_client
        ;;
    2)
        echo -e "${YELLOW}=== Backend Deployment ===${NC}"
        deploy_backend
        ;;
    3)
        echo -e "${YELLOW}=== Client Deployment ===${NC}"
        deploy_client
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

################################################################################
# Completion
################################################################################

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}║   🎉 Deployment Complete!                     ║${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}║   URL: http://$VPS_HOST${NC}"
echo -e "${GREEN}║   Health: http://$VPS_HOST/health${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""
