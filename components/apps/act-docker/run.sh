#!/bin/bash
# Complete ACT Docker Runner with Automatic Port Detection
# This script syncs the port from flow file and rebuilds Docker automatically

set -e  # Exit on error

FLOW_FILE="./flow"
ENV_FILE="./.env"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 ACT Auto-Port Docker Runner"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Check flow file exists
if [ ! -f "$FLOW_FILE" ]; then
    echo "❌ Error: flow file not found at $FLOW_FILE"
    exit 1
fi

# Step 2: Extract port from flow file
PORT=$(grep -E "^\s*port\s*=" "$FLOW_FILE" | sed 's/.*=\s*//' | tr -d ' ')

if [ -z "$PORT" ] || ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "⚠️  Warning: Could not find valid port in flow file, using default 8080"
    PORT=8080
fi

echo "📄 Flow file: $FLOW_FILE"
echo "🔌 Detected port: $PORT"
echo ""

# Step 3: Update .env file
if [ -f "$ENV_FILE" ]; then
    # Update existing ACT_PORT line
    sed -i.bak "s/^ACT_PORT=.*/ACT_PORT=$PORT/" "$ENV_FILE"
    rm -f "$ENV_FILE.bak"
    echo "✅ Updated .env file: ACT_PORT=$PORT"
else
    # Create new .env file
    cat > "$ENV_FILE" << EOF
# ACT Docker Environment Configuration
# Auto-synced with flow file port
ACT_PORT=$PORT
EOF
    echo "✅ Created .env file: ACT_PORT=$PORT"
fi

# Step 4: Stop existing containers
echo ""
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Step 5: Rebuild and start
echo ""
echo "🔨 Building Docker image..."
docker-compose build --quiet

echo ""
echo "🚀 Starting container with port $PORT..."
docker-compose up -d

# Step 6: Wait a moment for container to start
sleep 2

# Step 7: Show status
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ACT is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access your server at:"
echo "   📊 Dashboard:   http://localhost:$PORT/admin/dashboard"
echo "   💚 Health:      http://localhost:$PORT/health"
echo "   🚀 API Status:  http://localhost:$PORT/api/status"
echo ""
echo "📋 Useful commands:"
echo "   View logs:      docker logs -f act-docker-act-1"
echo "   Stop server:    docker-compose down"
echo "   Restart:        ./run.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 8: Show recent logs
echo "📝 Recent logs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker logs --tail 15 act-docker-act-1 2>&1 | grep -E "Port|Agent|Server|ERROR|WARNING" || echo "Container starting..."
echo ""
