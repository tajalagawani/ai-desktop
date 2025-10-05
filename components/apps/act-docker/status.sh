#!/bin/bash
# Auto-generated status checker for ACT Multi-Flow
# Shows health status of all running flows

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ACT Multi-Flow Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""


echo "🔍 math (Port 9000)"
curl -s http://localhost:9000/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "🔍 restaurant (Port 5544)"
curl -s http://localhost:5544/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "🔍 restaurant2 (Port 8081)"
curl -s http://localhost:8081/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "🔍 risk (Port 8088)"
curl -s http://localhost:8088/health 2>/dev/null | jq . || echo "   ❌ Not responding"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Docker Container Status:"
docker-compose ps
