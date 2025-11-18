#!/bin/bash

echo "Installing ACT Agent SDK Integration..."

cd "$(dirname "$0")"

npm install

if [ ! -f .env ]; then
  echo "Creating .env file..."
  cp .env.example .env
  echo "⚠️  Edit .env and add your ANTHROPIC_API_KEY"
fi

echo "✅ Installation complete"
echo ""
echo "Usage:"
echo "  1. Generate flows:    node index.js 'Build a GitHub to Slack sync'"
echo "  2. Autonomous agent:  node autonomous-agent.js 'Analyze my GitHub repos'"
echo "  3. Execute with AI:   node agent-executor.js ../flows/myflow.flow"
