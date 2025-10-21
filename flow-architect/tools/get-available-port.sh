#!/bin/bash
# flow-architect/tools/get-available-port.sh
#
# Get next available port for deploying new flow services
#
# Usage:
#   ./get-available-port.sh
#
# Output: JSON object with available port information
#   {"success":true,"available_port":9001,"used_ports":[3000,3001,9000]}
#
# Examples:
#   ./get-available-port.sh

# Call API
response=$(curl -s http://localhost:3000/api/ports 2>/dev/null)

# Check if curl failed
if [ $? -ne 0 ]; then
  echo '{"success":false,"available_port":9001,"used_ports":[]}'
  exit 0
fi

# Return the response as-is (API already returns proper JSON)
echo "$response"
