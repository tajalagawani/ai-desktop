#!/bin/bash
# flow-architect/tools/get-running-services.sh
#
# Get all running Docker services on the VPS
#
# Usage:
#   ./get-running-services.sh [category]
#
# Parameters:
#   category (optional): Filter by category (all|database|web-server|queue|search)
#                       Default: all
#
# Output: JSON array of running services
#
# Examples:
#   ./get-running-services.sh           # All running services
#   ./get-running-services.sh database  # Only running databases
#   ./get-running-services.sh web-server # Only running web servers

CATEGORY=${1:-all}

# Call API
response=$(curl -s http://localhost:3000/api/services 2>/dev/null)

# Check if curl failed
if [ $? -ne 0 ]; then
  echo "[]"
  exit 0
fi

# Filter running services
if [ "$CATEGORY" = "all" ]; then
  echo "$response" | jq '.services // [] | map(select(.status == "running"))'
else
  echo "$response" | jq --arg cat "$CATEGORY" '.services // [] | map(select(.status == "running" and .category == $cat))'
fi
