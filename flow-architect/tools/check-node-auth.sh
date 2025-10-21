#!/bin/bash
# flow-architect/tools/check-node-auth.sh
#
# Check if a node type has authentication configured
#
# Usage:
#   ./check-node-auth.sh <node_type>
#
# Parameters:
#   node_type (required): Node type (e.g., github, openai, slack, sendgrid)
#
# Output: JSON object with auth status
#   {"nodeType":"github","configured":true,"statusCode":200}
#   {"nodeType":"github","configured":false,"statusCode":404}
#
# Examples:
#   ./check-node-auth.sh github
#   ./check-node-auth.sh openai
#   ./check-node-auth.sh slack

NODE_TYPE=$1

# Check if node type provided
if [ -z "$NODE_TYPE" ]; then
  echo '{"error":"node_type parameter is required"}' >&2
  exit 1
fi

# Call API and capture HTTP status code
http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/nodes/$NODE_TYPE/auth 2>/dev/null)

# Check if curl failed
if [ $? -ne 0 ]; then
  echo "{\"nodeType\":\"$NODE_TYPE\",\"configured\":false,\"statusCode\":0}"
  exit 0
fi

# Return result based on HTTP code
if [ "$http_code" = "200" ]; then
  echo "{\"nodeType\":\"$NODE_TYPE\",\"configured\":true,\"statusCode\":200}"
else
  echo "{\"nodeType\":\"$NODE_TYPE\",\"configured\":false,\"statusCode\":$http_code}"
fi
