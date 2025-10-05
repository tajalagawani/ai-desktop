#!/bin/bash
# Sync port from flow file to .env file for Docker Compose

FLOW_FILE="./flow"
ENV_FILE="./.env"

if [ ! -f "$FLOW_FILE" ]; then
    echo "❌ Error: flow file not found at $FLOW_FILE"
    exit 1
fi

# Extract port from flow file
PORT=$(grep -E "^\s*port\s*=" "$FLOW_FILE" | sed 's/.*=\s*//' | tr -d ' ')

if [ -z "$PORT" ] || ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "⚠️  Warning: Could not find valid port in flow file, using default 8080"
    PORT=8080
fi

# Update .env file
if [ -f "$ENV_FILE" ]; then
    # Update existing ACT_PORT line
    sed -i.bak "s/^ACT_PORT=.*/ACT_PORT=$PORT/" "$ENV_FILE"
    rm -f "$ENV_FILE.bak"
else
    # Create new .env file
    cat > "$ENV_FILE" << EOF
# ACT Docker Environment Configuration
# Port configuration for the agent server
# This will be automatically synced with the flow file's [configuration] port setting
ACT_PORT=$PORT
EOF
fi

echo "✅ Port synchronized!"
echo "📄 Flow file port: $PORT"
echo "🐳 Docker will expose: $PORT:$PORT"
echo ""
echo "Run: docker-compose up --build -d"
