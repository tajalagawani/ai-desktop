#!/bin/bash
# Auto-generated status checker for ACT Multi-Flow
# Shows health status of all running flows

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ACT Multi-Flow Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""


echo "🔍 action-builder (Port 9002)"
curl -s http://localhost:9002/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "🔍 iss-location (Port 9001)"
curl -s http://localhost:9001/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Docker Container Status:"
docker-compose ps
