#!/bin/bash

echo "=================================="
echo "Flow Builder Setup Verification"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SUCCESS=0
WARNINGS=0
ERRORS=0

# 1. Check agent-sdk exists
echo -n "1. Checking agent-sdk directory... "
if [ -d "/Users/tajnoah/Downloads/ai-desktop/agent-sdk" ]; then
  echo -e "${GREEN}✓${NC}"
  ((SUCCESS++))
else
  echo -e "${RED}✗${NC} Not found"
  ((ERRORS++))
fi

# 2. Check agent-sdk dependencies
echo -n "2. Checking agent-sdk dependencies... "
if [ -d "/Users/tajnoah/Downloads/ai-desktop/agent-sdk/node_modules" ]; then
  echo -e "${GREEN}✓${NC}"
  ((SUCCESS++))
else
  echo -e "${YELLOW}⚠${NC} Run: cd agent-sdk && npm install"
  ((WARNINGS++))
fi

# 3. Check agent-sdk .env
echo -n "3. Checking agent-sdk .env file... "
if [ -f "/Users/tajnoah/Downloads/ai-desktop/agent-sdk/.env" ]; then
  if grep -q "ANTHROPIC_API_KEY=sk-" /Users/tajnoah/Downloads/ai-desktop/agent-sdk/.env; then
    echo -e "${GREEN}✓${NC}"
    ((SUCCESS++))
  else
    echo -e "${YELLOW}⚠${NC} API key not set"
    ((WARNINGS++))
  fi
else
  echo -e "${RED}✗${NC} Not found"
  ((ERRORS++))
fi

# 4. Check ACT directory
echo -n "4. Checking ACT installation... "
if [ -d "/Users/tajnoah/act" ]; then
  echo -e "${GREEN}✓${NC}"
  ((SUCCESS++))
else
  echo -e "${RED}✗${NC} ACT not found at /Users/tajnoah/act"
  ((ERRORS++))
fi

# 5. Check MCP server
echo -n "5. Checking MCP server... "
if [ -f "/Users/tajnoah/act/mcp/index.js" ]; then
  echo -e "${GREEN}✓${NC}"
  ((SUCCESS++))
else
  echo -e "${RED}✗${NC} Not found"
  ((ERRORS++))
fi

# 6. Check MCP dependencies
echo -n "6. Checking MCP dependencies... "
if [ -d "/Users/tajnoah/act/mcp/node_modules" ]; then
  echo -e "${GREEN}✓${NC}"
  ((SUCCESS++))
else
  echo -e "${YELLOW}⚠${NC} Run: cd /Users/tajnoah/act/mcp && npm install"
  ((WARNINGS++))
fi

# 7. Check Python API
echo -n "7. Checking Python Flow Manager API... "
if [ -f "/Users/tajnoah/act/flow_manager_api.py" ]; then
  echo -e "${GREEN}✓${NC}"
  ((SUCCESS++))
else
  echo -e "${YELLOW}⚠${NC} Optional - not found"
  ((WARNINGS++))
fi

# 8. Check flows directory
echo -n "8. Checking flows directory... "
if [ -d "/Users/tajnoah/act/flows" ]; then
  echo -e "${GREEN}✓${NC}"
  ((SUCCESS++))
else
  echo -e "${YELLOW}⚠${NC} Creating flows directory..."
  mkdir -p /Users/tajnoah/act/flows
  ((WARNINGS++))
fi

# 9. Check signatures directory
echo -n "9. Checking signatures directory... "
if [ -d "/Users/tajnoah/act/mcp/signatures" ]; then
  echo -e "${GREEN}✓${NC}"
  ((SUCCESS++))
else
  echo -e "${YELLOW}⚠${NC} Creating signatures directory..."
  mkdir -p /Users/tajnoah/act/mcp/signatures
  ((WARNINGS++))
fi

# 10. Check if MCP server is running
echo -n "10. Checking if MCP server is running... "
if pgrep -f "node.*mcp/index.js" > /dev/null; then
  PID=$(pgrep -f "node.*mcp/index.js")
  echo -e "${GREEN}✓${NC} (PID: $PID)"
  ((SUCCESS++))
else
  echo -e "${YELLOW}⚠${NC} Not running - start with: /Users/tajnoah/act/start-services.sh"
  ((WARNINGS++))
fi

# 11. Check if Python API is running
echo -n "11. Checking if Python API is running... "
if pgrep -f "flow_manager_api.py" > /dev/null; then
  PID=$(pgrep -f "flow_manager_api.py")
  echo -e "${GREEN}✓${NC} (PID: $PID)"
  ((SUCCESS++))
else
  echo -e "${YELLOW}⚠${NC} Not running (optional)"
  ((WARNINGS++))
fi

# 12. Check desktop app
echo -n "12. Checking desktop app... "
if [ -f "/Users/tajnoah/Downloads/ai-desktop/package.json" ]; then
  echo -e "${GREEN}✓${NC}"
  ((SUCCESS++))
else
  echo -e "${RED}✗${NC} Not found"
  ((ERRORS++))
fi

echo ""
echo "=================================="
echo "Summary"
echo "=================================="
echo -e "${GREEN}Success: $SUCCESS${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${RED}Errors: $ERRORS${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
  echo -e "${GREEN}✓ Setup is complete!${NC}"
  echo ""
  echo "Next steps:"
  echo "1. Start ACT services (if not running):"
  echo "   /Users/tajnoah/act/start-services.sh"
  echo ""
  echo "2. Start desktop app:"
  echo "   cd /Users/tajnoah/Downloads/ai-desktop && npm run dev"
  echo ""
  echo "3. Open http://localhost:3005 and test Flow Builder"
else
  echo -e "${RED}✗ Setup has errors - please fix them first${NC}"
  exit 1
fi
