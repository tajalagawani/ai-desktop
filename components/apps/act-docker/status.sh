#!/bin/bash
# Auto-generated status checker for ACT Multi-Flow
# Shows health status of all running flows

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ACT Multi-Flow Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""


echo "🔍 github-pr-reviewer (Port 9002)"
curl -s http://localhost:9002/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "🔍 iss-weather-api (Port 9003)"
curl -s http://localhost:9003/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "🔍 price-monitor-simple (Port 9007)"
curl -s http://localhost:9007/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "🔍 price-monitor (Port 9004)"
curl -s http://localhost:9004/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "🔍 syria-weather-api (Port 9001)"
curl -s http://localhost:9001/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "🔍 todo-api (Port 9006)"
curl -s http://localhost:9006/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "🔍 vix-filter-api (Port 9005)"
curl -s http://localhost:9005/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Docker Container Status:"
docker-compose ps
