#!/bin/bash
# .claude/hooks/validate-file-access.sh
#
# Pre-execution hook to validate file access
# Runs BEFORE any Read/Edit/Write tool execution
# This ensures Flow Architect NEVER accesses files outside its sandbox

TOOL_NAME=$1
FILE_PATH=$2
ALLOWED_PREFIX="/Users/tajnoah/Downloads/ai-desktop/flow-architect/"
SKILLS_PREFIX="/Users/tajnoah/.claude/skills/flow-architect/"

# Normalize path (resolve relative paths, symlinks)
NORMALIZED_PATH=$(realpath -s "$FILE_PATH" 2>/dev/null || echo "$FILE_PATH")

# Check if file path starts with allowed prefixes
if [[ "$NORMALIZED_PATH" =~ ^$ALLOWED_PREFIX ]] || [[ "$NORMALIZED_PATH" =~ ^$SKILLS_PREFIX ]]; then
  # Within sandbox - allow
  exit 0
fi

# SANDBOX VIOLATION DETECTED - BLOCK IT
echo "════════════════════════════════════════════════════════════"
echo "⛔ SANDBOX VIOLATION BLOCKED"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Tool:     $TOOL_NAME"
echo "Path:     $FILE_PATH"
echo "Resolved: $NORMALIZED_PATH"
echo ""
echo "Flow Architect can ONLY access files in:"
echo "  ✅ flow-architect/"
echo "  ✅ ~/.claude/skills/flow-architect/"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "⚠️  TO ACHIEVE YOUR GOAL:"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Create an ACT flow instead of modifying application files."
echo ""
echo "Example:"
echo "  ❌ Don't: Edit app/api/route.ts"
echo "  ✅ Do:    Create flow-architect/flows/my-solution.flow"
echo ""
echo "Flow-based solutions run in isolated containers and don't"
echo "modify your application code."
echo ""
echo "════════════════════════════════════════════════════════════"

# Block the operation
exit 1
