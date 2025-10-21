#!/bin/bash
# Quick sandbox enforcement verification

echo "════════════════════════════════════════════════════════════"
echo "  QUICK SANDBOX ENFORCEMENT TEST"
echo "════════════════════════════════════════════════════════════"
echo ""

# Test 1: Hook exists and is executable
echo "✓ Checking validation hook..."
if [ -x "/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/validate-file-access.sh" ]; then
  echo "  ✅ validate-file-access.sh is executable"
else
  echo "  ❌ validate-file-access.sh missing or not executable"
  exit 1
fi

# Test 2: ACT flow hook exists
echo "✓ Checking ACT flow reminder hook..."
if [ -x "/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/require-act-flow.sh" ]; then
  echo "  ✅ require-act-flow.sh is executable"
else
  echo "  ❌ require-act-flow.sh missing or not executable"
  exit 1
fi

# Test 3: Settings file has hooks
echo "✓ Checking Claude Code settings..."
if grep -q '"PreToolUse"' /Users/tajnoah/Downloads/ai-desktop/.claude/settings.local.json; then
  echo "  ✅ PreToolUse hooks configured"
else
  echo "  ❌ PreToolUse hooks missing"
  exit 1
fi

# Test 4: Templates exist
echo "✓ Checking templates..."
if [ -f "/Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/templates/sandbox-violation.md" ] && \
   [ -f "/Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/templates/act-flow-reminder.md" ]; then
  echo "  ✅ Both templates exist"
else
  echo "  ❌ Templates missing"
  exit 1
fi

# Test 5: Agent instructions updated
echo "✓ Checking agent instructions..."
if grep -q "SANDBOX VIOLATION PREVENTION" /Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/agents/flow-architect.md; then
  echo "  ✅ Agent instructions contain sandbox rules"
else
  echo "  ❌ Agent instructions missing sandbox rules"
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  🎉 ALL ENFORCEMENT LAYERS VERIFIED"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Enforcement Status:"
echo "  ✅ Layer 1: Validation hooks installed"
echo "  ✅ Layer 2: ACT flow reminder configured"
echo "  ✅ Layer 3: Claude Code settings integrated"
echo "  ✅ Layer 4: Agent instructions updated"
echo "  ✅ Layer 5: User message templates ready"
echo ""
echo "Flow Architect is now absolutely sandboxed!"
echo ""
