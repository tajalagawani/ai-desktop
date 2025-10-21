#!/bin/bash
# Auto-generated status checker for ACT Multi-Flow
# Shows health status of all running flows

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ACT Multi-Flow Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""


echo "🔍 clinic-management (Port 9009)"
curl -s http://localhost:9009/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "🔍 iss-weather-api (Port 9000)"
curl -s http://localhost:9000/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Docker Container Status:"
docker-compose ps
