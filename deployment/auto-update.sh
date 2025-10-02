#!/bin/bash

# Auto-update script for AI Desktop
# This script checks GitHub for new commits and auto-deploys

APP_NAME="ai-desktop"
APP_DIR="/var/www/ai-desktop"
REPO_URL="https://api.github.com/repos/tajalagawani/ai-desktop/commits/main"
STATE_FILE="/var/www/ai-desktop/.last-commit"
LOG_FILE="/var/www/ai-desktop/logs/auto-update.log"

# Create logs directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Get the latest commit SHA from GitHub
get_latest_commit() {
  curl -s "$REPO_URL" | grep -o '"sha": "[^"]*' | head -1 | cut -d'"' -f4
}

# Get the current commit SHA from local
get_current_commit() {
  if [ -f "$STATE_FILE" ]; then
    cat "$STATE_FILE"
  else
    echo ""
  fi
}

# Update the application
update_app() {
  log "🔄 New update detected! Starting deployment..."

  cd "$APP_DIR" || exit 1

  # Pull latest changes
  log "📥 Pulling latest code from GitHub..."
  git fetch origin main
  git reset --hard origin/main

  # Install dependencies
  log "📦 Installing dependencies..."
  npm ci --production=false

  # Build application
  log "🔨 Building application..."
  npm run build

  # Restart PM2
  log "🔄 Restarting application..."
  pm2 restart "$APP_NAME"

  # Save new commit SHA
  LATEST=$(get_latest_commit)
  echo "$LATEST" > "$STATE_FILE"

  log "✅ Update completed successfully! Latest commit: $LATEST"

  # Notify via PM2 logs
  pm2 sendSignal SIGUSR2 "$APP_NAME" 2>/dev/null || true
}

# Main logic
log "🔍 Checking for updates..."

CURRENT=$(get_current_commit)
LATEST=$(get_latest_commit)

if [ -z "$LATEST" ]; then
  log "❌ Failed to fetch latest commit from GitHub"
  exit 1
fi

if [ -z "$CURRENT" ]; then
  log "📝 First run - saving current commit: $LATEST"
  echo "$LATEST" > "$STATE_FILE"
  exit 0
fi

if [ "$CURRENT" != "$LATEST" ]; then
  log "🆕 Update available: $CURRENT -> $LATEST"
  update_app
else
  log "✅ Already up to date: $CURRENT"
fi
