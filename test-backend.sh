#!/bin/bash

# Action Builder Backend Test Script
# Tests all API endpoints to verify backend is running correctly

BASE_URL="http://localhost:3000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Testing Action Builder Backend"
echo "=================================="
echo ""

# Test 1: Projects API
echo -n "📦 Testing /api/projects ... "
PROJECTS=$(curl -s ${BASE_URL}/api/projects)
if [ $? -eq 0 ] && [[ $PROJECTS == *"flow-architect"* ]]; then
    echo -e "${GREEN}✓ OK${NC}"
    PROJECT_COUNT=$(echo $PROJECTS | jq -r '. | length' 2>/dev/null)
    echo "   Found $PROJECT_COUNT project(s)"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Response: $PROJECTS"
fi
echo ""

# Test 2: Actions API
echo -n "🎬 Testing /api/actions ... "
ACTIONS=$(curl -s ${BASE_URL}/api/actions)
if [ $? -eq 0 ] && [[ $ACTIONS == *"actions"* ]]; then
    echo -e "${GREEN}✓ OK${NC}"
    ACTION_COUNT=$(echo $ACTIONS | jq -r '.actions | length' 2>/dev/null)
    echo "   Found $ACTION_COUNT action(s)"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Response: $ACTIONS"
fi
echo ""

# Test 3: Flow Architect Actions API
echo -n "🎯 Testing /api/flow-architect/actions ... "
FA_ACTIONS=$(curl -s ${BASE_URL}/api/flow-architect/actions)
if [ $? -eq 0 ] && [[ $FA_ACTIONS == *"actions"* ]]; then
    echo -e "${GREEN}✓ OK${NC}"
    FA_ACTION_COUNT=$(echo $FA_ACTIONS | jq -r '.actions | length' 2>/dev/null)
    echo "   Found $FA_ACTION_COUNT action(s)"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Response: $FA_ACTIONS"
fi
echo ""

# Test 4: Service Catalog API
echo -n "📋 Testing /api/flow-architect/catalogs/service-catalog.json ... "
SERVICE_CAT=$(curl -s ${BASE_URL}/api/flow-architect/catalogs/service-catalog.json)
if [ $? -eq 0 ] && [[ $SERVICE_CAT == *"services"* ]]; then
    echo -e "${GREEN}✓ OK${NC}"
    SERVICE_COUNT=$(echo $SERVICE_CAT | jq -r '.services | length' 2>/dev/null)
    echo "   Found $SERVICE_COUNT service(s) in catalog"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Response: $SERVICE_CAT"
fi
echo ""

# Test 5: Node Catalog API
echo -n "📋 Testing /api/flow-architect/catalogs/node-catalog.json ... "
NODE_CAT=$(curl -s ${BASE_URL}/api/flow-architect/catalogs/node-catalog.json)
if [ $? -eq 0 ] && [[ $NODE_CAT == *"nodes"* ]]; then
    echo -e "${GREEN}✓ OK${NC}"
    NODE_COUNT=$(echo $NODE_CAT | jq -r '.nodes | length' 2>/dev/null)
    echo "   Found $NODE_COUNT node type(s) in catalog"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Response: $NODE_CAT"
fi
echo ""

# Test 6: WebSocket endpoint (basic check)
echo -n "🔌 Testing WebSocket endpoint availability ... "
WS_CHECK=$(curl -s -I ${BASE_URL}/api/action-builder/ws 2>&1 | head -1)
if [[ $WS_CHECK == *"426"* ]] || [[ $WS_CHECK == *"Upgrade Required"* ]]; then
    echo -e "${GREEN}✓ OK${NC}"
    echo "   WebSocket endpoint is available (426 = correct WebSocket upgrade response)"
elif [[ $WS_CHECK == *"200"* ]] || [[ $WS_CHECK == *"101"* ]]; then
    echo -e "${GREEN}✓ OK${NC}"
    echo "   WebSocket endpoint is available"
else
    echo -e "${YELLOW}⚠ WARNING${NC}"
    echo "   Could not verify WebSocket endpoint: $WS_CHECK"
fi
echo ""

# Summary
echo "=================================="
echo -e "${GREEN}✅ Backend is running!${NC}"
echo ""
echo "📍 Base URL: ${BASE_URL}"
echo "🌐 Open: ${BASE_URL}"
echo ""
echo "Next steps:"
echo "  1. Open ${BASE_URL} in your browser"
echo "  2. Click the 'Action Builder' icon in the dock"
echo "  3. Start chatting with Claude to create workflows!"
