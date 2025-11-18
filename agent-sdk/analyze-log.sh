#!/bin/bash

# Analyze agent log file

LOGFILE="$1"

if [ -z "$LOGFILE" ]; then
  LOGFILE=$(ls -t agent-debug-*.log trace-*.log 2>/dev/null | head -1)
fi

if [ ! -f "$LOGFILE" ]; then
  echo "❌ No log file found"
  echo "Usage: ./analyze-log.sh <logfile>"
  exit 1
fi

echo "📊 Analyzing: $LOGFILE"
echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Total lines: $(wc -l < "$LOGFILE")"
echo "File size: $(du -h "$LOGFILE" | cut -f1)"
echo ""

echo "=========================================="
echo "ERRORS"
echo "=========================================="
grep -i "error" "$LOGFILE" | head -20

echo ""
echo "=========================================="
echo "WARNINGS"
echo "=========================================="
grep -i "warning" "$LOGFILE" | head -10

echo ""
echo "=========================================="
echo "AGENT ACTIVITY"
echo "=========================================="
echo "Agent thinking: $(grep -c '💭 Agent' "$LOGFILE")"
echo "Tool uses: $(grep -c '🔧 Tool:' "$LOGFILE")"
echo "Tool results: $(grep -c '✓ Tool result' "$LOGFILE")"
echo ""
echo "Tools used:"
grep '🔧 Tool:' "$LOGFILE" | sed 's/.*🔧 Tool: /  - /' | sort | uniq -c

echo ""
echo "=========================================="
echo "MCP SERVER STATUS"
echo "=========================================="
grep -i "mcp" "$LOGFILE" | grep -i "status\|failed\|success" | head -5

echo ""
echo "=========================================="
echo "FLOW GENERATION"
echo "=========================================="
if grep -q "Flow generation complete" "$LOGFILE"; then
  echo "✅ Flow generated successfully"
  grep -A 5 "Flow Summary" "$LOGFILE" || echo "No summary found"
else
  echo "❌ Flow generation did not complete"
fi

echo ""
echo "=========================================="
echo "COST"
echo "=========================================="
grep -i "cost\|tokens\|usage" "$LOGFILE" | tail -5

echo ""
echo "=========================================="
echo "TIMELINE"
echo "=========================================="
echo "Started: $(head -30 "$LOGFILE" | grep "Started:" || echo "Unknown")"
echo "Finished: $(tail -30 "$LOGFILE" | grep "Finished:" || echo "Unknown")"

echo ""
echo "Full log: $LOGFILE"
