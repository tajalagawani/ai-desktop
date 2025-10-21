#!/bin/bash
# flow-architect/tools/get-deployed-flows.sh
#
# Get all deployed ACT flows on the VPS
#
# Usage:
#   ./get-deployed-flows.sh [status]
#
# Parameters:
#   status (optional): Filter by status (all|running|stopped)
#                     Default: all
#
# Output: JSON array of deployed flows with their endpoints
#
# Examples:
#   ./get-deployed-flows.sh          # All deployed flows
#   ./get-deployed-flows.sh running  # Only running flows
#   ./get-deployed-flows.sh stopped  # Only stopped flows

STATUS=${1:-all}

# Call API
response=$(curl -s http://localhost:3000/api/catalog 2>/dev/null)

# Check if curl failed
if [ $? -ne 0 ]; then
  echo "[]"
  exit 0
fi

# Filter flows based on status
if [ "$STATUS" = "all" ]; then
  echo "$response" | jq '.services // []'
elif [ "$STATUS" = "running" ]; then
  echo "$response" | jq '.services // [] | map(select(.status == "running"))'
elif [ "$STATUS" = "stopped" ]; then
  echo "$response" | jq '.services // [] | map(select(.status == "stopped"))'
else
  # Invalid status, return all
  echo "$response" | jq '.services // []'
fi
