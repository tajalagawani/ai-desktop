#!/bin/bash

##############################################
# AI Desktop - VPS Deployment Script
# This script automates deployment on your VPS
##############################################

set -e # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="ai-desktop"
APP_DIR="/var/www/ai-desktop"  # Update this to your actual path
REPO_URL="https://github.com/tajnoah/ai-desktop.git"
BRANCH="main"

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if running as correct user (allow root for now, just warn)
if [ "$EUID" -eq 0 ]; then
    print_info "Running as root. For production, consider using a dedicated deployment user."
fi

print_info "Starting deployment of $APP_NAME..."

# Step 1: Navigate to app directory
print_info "Navigating to $APP_DIR..."
cd "$APP_DIR" || {
    print_error "Directory $APP_DIR not found. Please clone the repo first."
    exit 1
}
print_success "In app directory"

# Step 2: Pull latest changes
print_info "Pulling latest changes from $BRANCH branch..."
git fetch origin
git reset --hard origin/$BRANCH
print_success "Code updated"

# Step 3: Install dependencies
print_info "Installing dependencies..."
npm ci --production=false
print_success "Dependencies installed"

# Step 4: Build the application
print_info "Building Next.js application..."
npm run build
print_success "Build completed"

# Step 5: Create logs directory if it doesn't exist
print_info "Setting up logs directory..."
mkdir -p logs
print_success "Logs directory ready"

# Step 5.5: Setup ACT Docker flows
print_info "Setting up ACT Docker flows..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    print_success "Docker installed"
fi

# Ensure Docker daemon is running
if ! systemctl is-active --quiet docker; then
    print_info "Starting Docker daemon..."
    systemctl start docker
    systemctl enable docker
    print_success "Docker daemon started"
fi

# Check if docker compose is available (v2 plugin or v1 standalone)
if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Installing plugin..."
    apt update
    apt install docker-compose-plugin -y
    print_success "Docker Compose plugin installed"
fi

# Setup ACT Docker
ACT_DIR="$APP_DIR/components/apps/act-docker"
if [ -d "$ACT_DIR" ]; then
    print_info "Setting up ACT flows..."
    cd "$ACT_DIR"

    # Install Python dependencies if needed
    if command -v pip3 &> /dev/null; then
        pip3 install --quiet flask flask-cors requests 2>/dev/null || true
    fi

    # Create flows directory if it doesn't exist
    mkdir -p flows

    # Generate docker-compose.yml if python script exists
    if [ -f "docker-compose-generator.py" ]; then
        python3 docker-compose-generator.py
        print_success "Docker compose generated"
    fi

    # Start/restart Docker containers
    if [ -f "docker-compose.yml" ]; then
        docker-compose down 2>/dev/null || true
        docker-compose up -d --build
        print_success "ACT Docker flows started"

        # Show running containers
        print_info "Running flow containers:"
        docker ps --filter "name=act-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    fi

    # Start Flow Manager API (optional - for direct API access)
    if [ -f "flow_manager_api.py" ]; then
        # Kill existing Flow Manager API if running
        pkill -f "flow_manager_api.py" 2>/dev/null || true

        # Start Flow Manager API in background
        nohup python3 flow_manager_api.py > "$APP_DIR/logs/flow-manager-api.log" 2>&1 &
        print_success "Flow Manager API started on port 8000"
    fi

    cd "$APP_DIR"
else
    print_info "ACT Docker directory not found, skipping flow setup"
fi

# Step 6: Restart PM2 process
print_info "Restarting PM2 process..."
if pm2 describe $APP_NAME > /dev/null 2>&1; then
    pm2 restart $APP_NAME
    print_success "PM2 process restarted"
else
    print_info "PM2 process not found. Starting new instance..."
    pm2 start deployment/ecosystem.config.js
    pm2 save
    print_success "PM2 process started and saved"
fi

# Step 7: Show PM2 status
print_info "Current PM2 status:"
pm2 status

# Step 8: Show recent logs
print_info "Recent logs (last 20 lines):"
pm2 logs $APP_NAME --lines 20 --nostream

print_success "Deployment completed successfully!"
print_info "App is running at http://localhost:3000"
print_info "Check logs with: pm2 logs $APP_NAME"
print_info "Monitor with: pm2 monit"
