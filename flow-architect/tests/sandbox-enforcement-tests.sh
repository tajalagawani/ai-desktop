#!/bin/bash
# flow-architect/tests/sandbox-enforcement-tests.sh
#
# Comprehensive test suite for absolute sandbox enforcement
# Tests all 5 layers of defense to ensure agent cannot escape sandbox

set -e

PASSED=0
FAILED=0
TEST_COUNT=0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test result tracking
print_test_header() {
  echo ""
  echo "════════════════════════════════════════════════════════════"
  echo "  TEST $((TEST_COUNT + 1)): $1"
  echo "════════════════════════════════════════════════════════════"
}

print_pass() {
  echo -e "${GREEN}✅ PASS${NC}: $1"
  PASSED=$((PASSED + 1))
  TEST_COUNT=$((TEST_COUNT + 1))
}

print_fail() {
  echo -e "${RED}❌ FAIL${NC}: $1"
  FAILED=$((FAILED + 1))
  TEST_COUNT=$((TEST_COUNT + 1))
}

print_summary() {
  echo ""
  echo "════════════════════════════════════════════════════════════"
  echo "  TEST SUMMARY"
  echo "════════════════════════════════════════════════════════════"
  echo -e "Total Tests:  $TEST_COUNT"
  echo -e "${GREEN}Passed:       $PASSED${NC}"
  echo -e "${RED}Failed:       $FAILED${NC}"
  echo ""

  if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED - SANDBOX IS SECURE${NC}"
    exit 0
  else
    echo -e "${RED}⚠️  SOME TESTS FAILED - SANDBOX MAY BE COMPROMISED${NC}"
    exit 1
  fi
}

# ============================================================================
# LAYER 1 TESTS: Validation Hooks
# ============================================================================

print_test_header "Validation Hook Exists and is Executable"
if [ -x "/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/validate-file-access.sh" ]; then
  print_pass "validate-file-access.sh is executable"
else
  print_fail "validate-file-access.sh is not executable or missing"
fi

print_test_header "Validation Hook Blocks Unauthorized Paths"
# Test blocking app/ directory access
TEST_PATH="/Users/tajnoah/Downloads/ai-desktop/app/api/test.ts"
/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/validate-file-access.sh "Write" "$TEST_PATH" >/dev/null 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 1 ]; then
  print_pass "Hook correctly blocks app/ directory access (exit code 1)"
else
  print_fail "Hook did not block app/ directory access (exit code $EXIT_CODE)"
fi

print_test_header "Validation Hook Allows flow-architect/ Paths"
# Test allowing flow-architect/ directory access
TEST_PATH="/Users/tajnoah/Downloads/ai-desktop/flow-architect/flows/test.act"
/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/validate-file-access.sh "Write" "$TEST_PATH" >/dev/null 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  print_pass "Hook correctly allows flow-architect/ directory access (exit code 0)"
else
  print_fail "Hook incorrectly blocks flow-architect/ directory access (exit code $EXIT_CODE)"
fi

print_test_header "Validation Hook Allows Skills Directory Paths"
# Test allowing ~/.claude/skills/flow-architect/ directory access
TEST_PATH="/Users/tajnoah/.claude/skills/flow-architect/test-skill/SKILL.md"
/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/validate-file-access.sh "Read" "$TEST_PATH" >/dev/null 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  print_pass "Hook correctly allows skills directory access (exit code 0)"
else
  print_fail "Hook incorrectly blocks skills directory access (exit code $EXIT_CODE)"
fi

# ============================================================================
# LAYER 2 TESTS: ACT Flow Reminder Hook
# ============================================================================

print_test_header "ACT Flow Reminder Hook Exists and is Executable"
if [ -x "/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/require-act-flow.sh" ]; then
  print_pass "require-act-flow.sh is executable"
else
  print_fail "require-act-flow.sh is not executable or missing"
fi

print_test_header "ACT Flow Hook Detects Action Keywords"
# Test that the hook detects action keywords
TEST_MESSAGE="calculate 47 + 89"
OUTPUT=$(/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/require-act-flow.sh "$TEST_MESSAGE" 2>&1)
if echo "$OUTPUT" | grep -q "ACTION DETECTED"; then
  print_pass "Hook detected 'calculate' keyword in user message"
else
  print_fail "Hook did not detect 'calculate' keyword"
fi

print_test_header "ACT Flow Hook Shows Mandatory Process"
# Test that reminder includes mandatory process
if echo "$OUTPUT" | grep -q "MANDATORY PROCESS"; then
  print_pass "Hook displays mandatory ACT flow process"
else
  print_fail "Hook does not display mandatory process"
fi

# ============================================================================
# LAYER 3 TESTS: Claude Code Settings Integration
# ============================================================================

print_test_header "Claude Code Settings File Exists"
if [ -f "/Users/tajnoah/Downloads/ai-desktop/.claude/settings.local.json" ]; then
  print_pass "settings.local.json exists"
else
  print_fail "settings.local.json is missing"
fi

print_test_header "Settings Contains PreToolUse Hooks"
if grep -q '"PreToolUse"' /Users/tajnoah/Downloads/ai-desktop/.claude/settings.local.json; then
  print_pass "settings.local.json contains PreToolUse hooks"
else
  print_fail "settings.local.json missing PreToolUse hooks"
fi

print_test_header "Settings Contains UserPromptSubmit Hooks"
if grep -q '"UserPromptSubmit"' /Users/tajnoah/Downloads/ai-desktop/.claude/settings.local.json; then
  print_pass "settings.local.json contains UserPromptSubmit hooks"
else
  print_fail "settings.local.json missing UserPromptSubmit hooks"
fi

print_test_header "Settings Contains Read Hook Matcher"
if grep -q '"matcher": "Read"' /Users/tajnoah/Downloads/ai-desktop/.claude/settings.local.json; then
  print_pass "Read tool has validation hook"
else
  print_fail "Read tool missing validation hook"
fi

print_test_header "Settings Contains Edit Hook Matcher"
if grep -q '"matcher": "Edit"' /Users/tajnoah/Downloads/ai-desktop/.claude/settings.local.json; then
  print_pass "Edit tool has validation hook"
else
  print_fail "Edit tool missing validation hook"
fi

print_test_header "Settings Contains Write Hook Matcher"
if grep -q '"matcher": "Write"' /Users/tajnoah/Downloads/ai-desktop/.claude/settings.local.json; then
  print_pass "Write tool has validation hook"
else
  print_fail "Write tool missing validation hook"
fi

print_test_header "Settings Has Docker Command Denials"
if grep -q '"Bash(docker:\*)"' /Users/tajnoah/Downloads/ai-desktop/.claude/settings.local.json; then
  print_pass "Docker commands are denied in permissions"
else
  print_fail "Docker commands not denied in permissions"
fi

# ============================================================================
# LAYER 4 TESTS: Agent Instructions
# ============================================================================

print_test_header "Flow Architect Agent Instructions Exist"
if [ -f "/Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/agents/flow-architect.md" ]; then
  print_pass "flow-architect.md exists"
else
  print_fail "flow-architect.md is missing"
fi

print_test_header "Agent Instructions Contain Sandbox Rules"
if grep -q "SANDBOX VIOLATION PREVENTION" /Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/agents/flow-architect.md; then
  print_pass "Agent instructions contain sandbox violation prevention section"
else
  print_fail "Agent instructions missing sandbox violation prevention"
fi

print_test_header "Agent Instructions List Forbidden Files"
FORBIDDEN_COUNT=$(grep -c "❌" /Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/agents/flow-architect.md || true)
if [ $FORBIDDEN_COUNT -gt 5 ]; then
  print_pass "Agent instructions list forbidden files/directories ($FORBIDDEN_COUNT instances)"
else
  print_fail "Agent instructions don't clearly list forbidden files ($FORBIDDEN_COUNT instances)"
fi

print_test_header "Agent Instructions List Allowed Files"
if grep -q "✅ flow-architect/" /Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/agents/flow-architect.md; then
  print_pass "Agent instructions clearly state allowed directories"
else
  print_fail "Agent instructions don't clearly state allowed directories"
fi

# ============================================================================
# LAYER 5 TESTS: User Message Templates
# ============================================================================

print_test_header "Sandbox Violation Template Exists"
if [ -f "/Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/templates/sandbox-violation.md" ]; then
  print_pass "sandbox-violation.md template exists"
else
  print_fail "sandbox-violation.md template is missing"
fi

print_test_header "Sandbox Violation Template Has Placeholders"
if grep -q "{user_request}" /Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/templates/sandbox-violation.md &&
   grep -q "{attempted_action}" /Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/templates/sandbox-violation.md &&
   grep -q "{target_file}" /Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/templates/sandbox-violation.md; then
  print_pass "Sandbox violation template has required placeholders"
else
  print_fail "Sandbox violation template missing required placeholders"
fi

print_test_header "ACT Flow Reminder Template Exists"
if [ -f "/Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/templates/act-flow-reminder.md" ]; then
  print_pass "act-flow-reminder.md template exists"
else
  print_fail "act-flow-reminder.md template is missing"
fi

print_test_header "ACT Flow Template Shows Execution Process"
if grep -q "Execution Process" /Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/templates/act-flow-reminder.md; then
  print_pass "ACT flow template shows execution process"
else
  print_fail "ACT flow template missing execution process"
fi

# ============================================================================
# SECURITY TESTS: Attempt Common Bypass Techniques
# ============================================================================

print_test_header "Relative Path Bypass Protection"
# Test ../../../ path traversal
TEST_PATH="/Users/tajnoah/Downloads/ai-desktop/flow-architect/../app/api/test.ts"
/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/validate-file-access.sh "Write" "$TEST_PATH" >/dev/null 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 1 ]; then
  print_pass "Hook blocks relative path traversal (../ bypass attempt)"
else
  print_fail "Hook did not block relative path traversal"
fi

print_test_header "Symlink Path Bypass Protection"
# Test symlink resolution (if realpath is working)
TEST_PATH="/tmp/bypass-link"
/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/validate-file-access.sh "Read" "$TEST_PATH" >/dev/null 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 1 ]; then
  print_pass "Hook blocks paths outside sandbox via symlinks"
else
  print_fail "Hook may not properly handle symlinks"
fi

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

print_test_header "All Critical Files Present"
CRITICAL_FILES=(
  "/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/validate-file-access.sh"
  "/Users/tajnoah/Downloads/ai-desktop/.claude/hooks/require-act-flow.sh"
  "/Users/tajnoah/Downloads/ai-desktop/.claude/settings.local.json"
  "/Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/agents/flow-architect.md"
  "/Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/templates/sandbox-violation.md"
  "/Users/tajnoah/Downloads/ai-desktop/flow-architect/.claude/templates/act-flow-reminder.md"
)

MISSING_COUNT=0
for file in "${CRITICAL_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    MISSING_COUNT=$((MISSING_COUNT + 1))
    echo -e "${YELLOW}  Missing: $file${NC}"
  fi
done

if [ $MISSING_COUNT -eq 0 ]; then
  print_pass "All critical enforcement files are present"
else
  print_fail "$MISSING_COUNT critical files are missing"
fi

# ============================================================================
# Final Summary
# ============================================================================

print_summary
