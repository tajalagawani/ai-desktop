#!/bin/bash
# Dynamic port detection and ACT startup script

# Function to extract port from flow file
get_port_from_flow() {
    if [ -f "/app/flow" ]; then
        # Extract port from flow file
        PORT=$(grep -E "^\s*port\s*=" /app/flow | sed 's/.*=\s*//' | tr -d ' ')
        if [ -n "$PORT" ] && [ "$PORT" -eq "$PORT" ] 2>/dev/null; then
            echo "$PORT"
        else
            echo "8080"  # Default fallback
        fi
    else
        echo "8080"  # Default fallback
    fi
}

# Read port from flow file
FLOW_PORT=$(get_port_from_flow)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 ACT Dynamic Port Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 Flow file: /app/flow"
echo "🔌 Detected port: $FLOW_PORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Export for Python to use
export ACT_PORT=$FLOW_PORT

# Start ACT - pass through to CMD (docker_runner.py)
exec "$@"
