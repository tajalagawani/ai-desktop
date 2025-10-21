#!/bin/bash
# flow-architect/tools/check-service-auth.sh
#
# Check if a service has authentication configured
#
# Usage:
#   ./check-service-auth.sh <service_id>
#
# Parameters:
#   service_id (required): Service ID (e.g., postgresql, mysql, mongodb)
#
# Output: JSON object with auth status
#   {"serviceId":"postgresql","configured":true,"statusCode":200}
#   {"serviceId":"postgresql","configured":false,"statusCode":404}
#
# Examples:
#   ./check-service-auth.sh postgresql
#   ./check-service-auth.sh mysql

SERVICE_ID=$1

# Check if service ID provided
if [ -z "$SERVICE_ID" ]; then
  echo '{"error":"service_id parameter is required"}' >&2
  exit 1
fi

# Call API and capture HTTP status code
http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/services/$SERVICE_ID/auth 2>/dev/null)

# Check if curl failed
if [ $? -ne 0 ]; then
  echo "{\"serviceId\":\"$SERVICE_ID\",\"configured\":false,\"statusCode\":0}"
  exit 0
fi

# Return result based on HTTP code
if [ "$http_code" = "200" ]; then
  echo "{\"serviceId\":\"$SERVICE_ID\",\"configured\":true,\"statusCode\":200}"
else
  echo "{\"serviceId\":\"$SERVICE_ID\",\"configured\":false,\"statusCode\":$http_code}"
fi
