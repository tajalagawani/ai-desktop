#!/bin/bash
# flow-architect/tools/get-node-catalog.sh
#
# Get all available node types with their operations
#
# Usage:
#   ./get-node-catalog.sh [auth_required]
#
# Parameters:
#   auth_required (optional): Filter by authentication requirement (all|true|false)
#                            Default: all
#
# Output: JSON array of nodes with operations
#
# Examples:
#   ./get-node-catalog.sh        # All nodes (129 total)
#   ./get-node-catalog.sh true   # Only nodes requiring auth (GitHub, OpenAI, etc.)
#   ./get-node-catalog.sh false  # Only nodes NOT requiring auth (py, http, timer, etc.)

AUTH_REQUIRED=${1:-all}

# Call API
response=$(curl -s http://localhost:3000/api/nodes 2>/dev/null)

# Check if curl failed
if [ $? -ne 0 ]; then
  echo "[]"
  exit 0
fi

# Filter nodes based on auth requirement
if [ "$AUTH_REQUIRED" = "all" ]; then
  echo "$response" | jq '.nodes // []'
elif [ "$AUTH_REQUIRED" = "true" ]; then
  echo "$response" | jq '.nodes // [] | map(select(.capabilities.requiresAuth == true))'
else
  echo "$response" | jq '.nodes // [] | map(select(.capabilities.requiresAuth == false or .capabilities.requiresAuth == null))'
fi
