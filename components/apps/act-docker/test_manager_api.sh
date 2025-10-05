#!/bin/bash
# Test script for Flow Manager API
# Demonstrates beautiful JSON responses

PORT=8001
BASE_URL="http://localhost:$PORT"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Testing ACT Flow Manager API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "1️⃣  API Documentation (GET /)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s $BASE_URL/ | head -30
echo ""
echo ""

echo "2️⃣  Health Check (GET /health)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s $BASE_URL/health
echo ""
echo ""

echo "3️⃣  System Stats (GET /api/system/stats)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s $BASE_URL/api/system/stats | head -40
echo ""
echo ""

echo "4️⃣  List All Flows (GET /api/flows)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s $BASE_URL/api/flows | head -50
echo ""
echo ""

echo "✅ All tests completed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Management API:  $BASE_URL"
echo "📊 System Stats:    $BASE_URL/api/system/stats"
echo "📋 List Flows:      $BASE_URL/api/flows"
echo "🌐 UI Dashboard:    Open management_ui.html"
echo ""
