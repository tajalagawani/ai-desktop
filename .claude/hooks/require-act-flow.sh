#!/bin/bash
# .claude/hooks/require-act-flow.sh
#
# Ensures Flow Architect ALWAYS creates ACT flows for actions
# Runs on user message submission
#
# This hook reminds the agent to create flows instead of answering directly

USER_MESSAGE="$1"

# Keywords that indicate user wants an ACTION (not conversation)
ACTION_KEYWORDS=(
  "calculate" "compute" "what's" "what is" "whats"
  "get" "fetch" "retrieve" "find" "show"
  "generate" "create" "make" "build"
  "random" "pick" "select" "choose"
  "check" "monitor" "watch" "track"
  "send" "notify" "alert" "email"
  "process" "transform" "convert"
  "add" "plus" "minus" "times" "divide"
  "sum" "total" "average" "mean"
  "current" "now" "today" "latest"
)

# Check if message contains action keywords
MESSAGE_LOWER=$(echo "$USER_MESSAGE" | tr '[:upper:]' '[:lower:]')

for keyword in "${ACTION_KEYWORDS[@]}"; do
  if echo "$MESSAGE_LOWER" | grep -q "\b$keyword\b"; then
    # ACTION DETECTED - Remind agent to create flow
    echo "════════════════════════════════════════════════════════════"
    echo "⚠️  ACTION DETECTED: '$keyword'"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Flow Architect must create an ACT flow for this action."
    echo ""
    echo "MANDATORY PROCESS:"
    echo "  1. Create .act or .flow file in flow-architect/temp/"
    echo "  2. Execute via POST to http://localhost:3000/api/act/execute"
    echo "  3. Parse the execution result"
    echo "  4. THEN respond to user with the answer"
    echo ""
    echo "Do NOT answer directly without creating and executing a flow!"
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo ""

    # Allow but with strong reminder
    exit 0
  fi
done

# No action keywords detected - likely conversation
# Still allow but no reminder needed
exit 0
