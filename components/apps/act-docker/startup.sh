#!/bin/bash
# ACT Multi-Flow Startup Script
# Auto-discovers flows and starts all containers

set -e

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 ACT Multi-Flow Startup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if flows directory exists
if [ ! -d "flows" ]; then
    echo "❌ Error: flows/ directory not found"
    echo "   Create flows/ and add your .flow files"
    exit 1
fi

# Count flow files
FLOW_COUNT=$(find flows -name "*.flow" -type f | wc -l | tr -d ' ')

if [ "$FLOW_COUNT" -eq 0 ]; then
    echo "❌ Error: No .flow files found in flows/"
    echo "   Add at least one .flow file to get started"
    exit 1
fi

echo "📦 Found $FLOW_COUNT flow file(s)"
echo ""

# Generate docker-compose.yml
echo "🔨 Generating docker-compose.yml..."
python3 docker-compose-generator.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to generate docker-compose.yml"
    echo "   Check for errors above"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐳 Starting Docker Containers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start containers
if [ "$1" == "--build" ] || [ "$1" == "-b" ]; then
    echo "🔨 Building and starting containers..."
    docker-compose up --build -d
else
    echo "🚀 Starting containers..."
    docker-compose up -d
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to start containers"
    exit 1
fi

echo ""
echo "⏳ Waiting for containers to be ready..."
sleep 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All Flows Started!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show status
docker-compose ps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Access Points:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Parse ports from docker-compose.yml
python3 -c "
import re
from pathlib import Path

content = Path('docker-compose.yml').read_text()
services = re.findall(r'act-(\w+):', content)
ports = re.findall(r'\"(\d+):\d+\"', content)

for service, port in zip(services, ports):
    print(f'   🌐 {service:15} http://localhost:{port}')
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Check status:  ./status.sh"
echo "📋 View logs:     docker-compose logs -f"
echo "🛑 Stop all:      docker-compose down"
echo "🔄 Restart:       docker-compose restart"
echo ""
echo "💡 Use Makefile for shortcuts:"
echo "   make start, make stop, make logs, make status"
echo ""
