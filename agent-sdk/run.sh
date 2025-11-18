#!/bin/bash
#
# ACT Agent SDK - Quick Run Script
# Automatically checks setup and runs the agent
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Quick setup check function
check_setup() {
    local needs_setup=false

    # Check node_modules
    if [ ! -d "node_modules" ]; then
        needs_setup=true
        return 0
    fi

    # Check skills
    if [ ! -d "$HOME/.claude/skills/act-flow-architect" ]; then
        needs_setup=true
        return 0
    fi

    # Check .env file
    if [ ! -f ".env" ]; then
        needs_setup=true
        return 0
    fi

    return 1
}

# Check if setup is needed
if check_setup; then
    echo "⚙️  First-time setup required..."
    echo ""
    ./setup.sh
    echo ""
fi

# Check for request argument
if [ $# -eq 0 ]; then
    echo "Usage: ./run.sh \"your flow request\""
    echo ""
    echo "Examples:"
    echo "  ./run.sh \"create a hello world API\""
    echo "  ./run.sh \"build a flow that sends GitHub issues to Slack\""
    echo ""
    echo "Environment Variables:"
    echo "  ACT_AGENT_MODEL=claude-sonnet-4-5-20250929  # Change model"
    echo "  VERBOSE=true                                # Enable debug output"
    echo ""
    exit 1
fi

# Run the agent
REQUEST="$*"
echo "🚀 Running ACT Agent..."
echo ""

node index.js "$REQUEST"
