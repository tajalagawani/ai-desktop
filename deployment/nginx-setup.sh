#!/bin/bash
set -e

echo "========================================="
echo "Setting up Nginx for AI Desktop"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root${NC}"
   exit 1
fi

echo -e "${YELLOW}[1/5] Installing Nginx...${NC}"
# Install Nginx and netcat (for port checking)
apt update
apt install -y nginx netcat

echo -e "${YELLOW}[2/5] Creating directories...${NC}"
# Create directories for dynamic VS Code project configs
mkdir -p /etc/nginx/vscode-projects
mkdir -p /var/www/vscode-workspaces

# Set permissions
chmod 755 /etc/nginx/vscode-projects
chmod 755 /var/www/vscode-workspaces

echo -e "${YELLOW}[3/5] Creating main Nginx configuration...${NC}"
# Create main Nginx config for AI Desktop
cat > /etc/nginx/sites-available/ai-desktop <<'EOF'
server {
    listen 80;
    server_name _;

    # Main Next.js app
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;

        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }

    # Include all dynamic VS Code project configs
    include /etc/nginx/vscode-projects/*.conf;

    # Increase max body size for file uploads
    client_max_body_size 500M;
}
EOF

echo -e "${YELLOW}[4/5] Enabling site and disabling default...${NC}"
# Enable site and disable default
ln -sf /etc/nginx/sites-available/ai-desktop /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo -e "${YELLOW}[5/5] Testing and reloading Nginx...${NC}"
# Test Nginx configuration
if nginx -t; then
    echo -e "${GREEN}✓ Nginx configuration test passed${NC}"
    systemctl enable nginx
    systemctl restart nginx
    echo -e "${GREEN}✓ Nginx restarted successfully${NC}"
else
    echo -e "${RED}✗ Nginx configuration test failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Nginx setup complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "Configuration details:"
echo -e "  • Main config: /etc/nginx/sites-available/ai-desktop"
echo -e "  • Dynamic configs: /etc/nginx/vscode-projects/"
echo -e "  • Workspaces: /var/www/vscode-workspaces/"
echo ""
echo -e "Next steps:"
echo -e "  1. Build and start the Next.js app with PM2"
echo -e "  2. VS Code instances will automatically get Nginx configs"
echo -e "  3. Access VS Code at: http://YOUR_IP/vscode/project-name/"
echo ""
