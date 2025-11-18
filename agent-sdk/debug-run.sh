#!/bin/bash

# Debug runner for Flow Architect Agent
# Captures ALL logs and saves to file

LOGFILE="agent-debug-$(date +%Y%m%d-%H%M%S).log"
REQUEST="$1"

if [ -z "$REQUEST" ]; then
  REQUEST="Build a simple hello world API flow"
fi

echo "======================================" | tee "$LOGFILE"
echo "ACT Agent SDK Debug Run" | tee -a "$LOGFILE"
echo "======================================" | tee -a "$LOGFILE"
echo "Request: $REQUEST" | tee -a "$LOGFILE"
echo "Log file: $LOGFILE" | tee -a "$LOGFILE"
echo "Started: $(date)" | tee -a "$LOGFILE"
echo "======================================" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"

# Set debug environment
export DEBUG=true
export VERBOSE=true

# Run the agent and capture EVERYTHING
node index.js "$REQUEST" 2>&1 | tee -a "$LOGFILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "" | tee -a "$LOGFILE"
echo "======================================" | tee -a "$LOGFILE"
echo "Finished: $(date)" | tee -a "$LOGFILE"
echo "Exit code: $EXIT_CODE" | tee -a "$LOGFILE"
echo "Log saved to: $LOGFILE" | tee -a "$LOGFILE"
echo "======================================" | tee -a "$LOGFILE"

# Show log location
echo ""
echo "📝 Full log saved to: $(pwd)/$LOGFILE"
echo ""
echo "View with: cat $LOGFILE"
echo "Search: grep 'ERROR' $LOGFILE"

exit $EXIT_CODE
