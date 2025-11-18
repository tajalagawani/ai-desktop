#!/bin/bash

# Detailed trace runner with step-by-step logging

LOGFILE="trace-$(date +%Y%m%d-%H%M%S).log"
REQUEST="$1"

if [ -z "$REQUEST" ]; then
  REQUEST="Build a simple hello world API flow"
fi

echo "🔍 Starting detailed trace..."
echo "📝 Log: $LOGFILE"
echo ""

{
  echo "=========================================="
  echo "TRACE LOG - $(date)"
  echo "=========================================="
  echo "Request: $REQUEST"
  echo "PWD: $(pwd)"
  echo "Node version: $(node --version)"
  echo "NPM packages:"
  npm list --depth=0 2>&1 || echo "Could not list packages"
  echo ""
  echo "=========================================="
  echo "ENVIRONMENT"
  echo "=========================================="
  env | grep -E "(ANTHROPIC|DEBUG|VERBOSE|NODE|PATH)" | sort
  echo ""
  echo "=========================================="
  echo ".env file check"
  echo "=========================================="
  if [ -f .env ]; then
    echo ".env exists"
    echo "API Key set: $(grep -q ANTHROPIC_API_KEY .env && echo 'YES' || echo 'NO')"
  else
    echo ".env NOT FOUND"
  fi
  echo ""
  echo "=========================================="
  echo "MCP Server check"
  echo "=========================================="
  if [ -f ../mcp/index.js ]; then
    echo "MCP server exists at: ../mcp/index.js"
  else
    echo "MCP server NOT FOUND"
  fi
  echo ""
  echo "=========================================="
  echo "STARTING AGENT"
  echo "=========================================="
  echo ""

  # Run with Node.js trace
  NODE_OPTIONS="--trace-warnings" node index.js "$REQUEST" 2>&1

  EXIT_CODE=$?

  echo ""
  echo "=========================================="
  echo "EXECUTION COMPLETE"
  echo "=========================================="
  echo "Exit code: $EXIT_CODE"
  echo "Finished: $(date)"
  echo "=========================================="

} 2>&1 | tee "$LOGFILE"

echo ""
echo "📊 Trace complete!"
echo "📁 Full log: $(pwd)/$LOGFILE"
echo ""
echo "Quick analysis:"
echo "  Lines: $(wc -l < "$LOGFILE")"
echo "  Errors: $(grep -i error "$LOGFILE" | wc -l)"
echo "  Warnings: $(grep -i warning "$LOGFILE" | wc -l)"
echo "  Agent messages: $(grep -i 'Agent:' "$LOGFILE" | wc -l)"
echo "  Tool uses: $(grep -i 'Tool:' "$LOGFILE" | wc -l)"
echo ""
echo "View errors: grep -i error $LOGFILE"
echo "View full: cat $LOGFILE"
