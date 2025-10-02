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

# Check if running as correct user
if [ "$EUID" -eq 0 ]; then
    print_error "Don't run this script as root. Run as your deployment user."
    exit 1
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
