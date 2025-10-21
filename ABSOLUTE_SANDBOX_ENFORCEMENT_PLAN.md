# Absolute Sandbox Enforcement Plan
## Zero Tolerance: Flow Architect NEVER Leaves Its Folder

**Goal:** Ensure Flow Architect agent:
1. **NEVER** accesses files outside `flow-architect/` - NO EXCEPTIONS
2. **ALWAYS** creates ACT flows for EVERY action - even simple ones

---

## 🎯 Current Situation

### What We Have
✅ Agent instructions with sandbox rules
✅ Explicit refusal patterns added
✅ Examples of wrong vs. right behavior

### What We Need
❌ System-level file path blocking
❌ Pre-execution validation hooks
❌ Automatic flow creation enforcement
❌ User-facing error messages
❌ Comprehensive testing

---

## 🔒 Multi-Layer Enforcement Strategy

We'll implement **5 defensive layers** to ensure absolute compliance:

```
Layer 1: Agent Instructions     [Already implemented ✅]
Layer 2: Tool Permissions       [Need to implement ⏳]
Layer 3: Validation Hooks       [Need to implement ⏳]
Layer 4: User Messaging         [Need to implement ⏳]
Layer 5: Testing & Monitoring   [Need to implement ⏳]
```

---

## 📋 Layer 1: Agent Instructions (DONE ✅)

**File:** `flow-architect/.claude/agents/flow-architect.md`

**What We Added:**
- 61 lines of explicit sandbox enforcement
- Forbidden file/folder lists
- Allowed file/folder lists
- Wrong vs. right examples
- Self-check mechanisms

**Status:** ✅ Complete

---

## 📋 Layer 2: Tool Permissions (System-Level Blocking)

**Goal:** Make it technically impossible for the agent to edit files outside `flow-architect/`

### Implementation Steps

#### Step 1: Update Claude Code Settings
**File:** `.claude/settings.local.json`

**Add tool permission restrictions:**
```json
{
  "toolPermissions": {
    "Read": {
      "allowedPaths": [
        "/Users/tajnoah/Downloads/ai-desktop/flow-architect/**",
        "/Users/tajnoah/.claude/skills/flow-architect/**"
      ],
      "blockedPaths": [
        "/Users/tajnoah/Downloads/ai-desktop/app/**",
        "/Users/tajnoah/Downloads/ai-desktop/components/**",
        "/Users/tajnoah/Downloads/ai-desktop/lib/**",
        "/Users/tajnoah/Downloads/ai-desktop/package.json",
        "/Users/tajnoah/Downloads/ai-desktop/package-lock.json",
        "/Users/tajnoah/Downloads/ai-desktop/next.config.js",
        "/Users/tajnoah/Downloads/ai-desktop/tsconfig.json"
      ]
    },
    "Edit": {
      "allowedPaths": [
        "/Users/tajnoah/Downloads/ai-desktop/flow-architect/**/*.md",
        "/Users/tajnoah/Downloads/ai-desktop/flow-architect/**/*.act",
        "/Users/tajnoah/Downloads/ai-desktop/flow-architect/**/*.flow",
        "/Users/tajnoah/Downloads/ai-desktop/flow-architect/**/*.toml"
      ],
      "blockedPaths": [
        "/Users/tajnoah/Downloads/ai-desktop/app/**",
        "/Users/tajnoah/Downloads/ai-desktop/components/**",
        "/Users/tajnoah/Downloads/ai-desktop/lib/**",
        "/Users/tajnoah/Downloads/ai-desktop/*.json",
        "/Users/tajnoah/Downloads/ai-desktop/*.js",
        "/Users/tajnoah/Downloads/ai-desktop/*.ts"
      ],
      "autoReject": true,
      "errorMessage": "⛔ SANDBOX VIOLATION: Cannot edit files outside flow-architect/"
    },
    "Write": {
      "allowedPaths": [
        "/Users/tajnoah/Downloads/ai-desktop/flow-architect/**/*.md",
        "/Users/tajnoah/Downloads/ai-desktop/flow-architect/**/*.act",
        "/Users/tajnoah/Downloads/ai-desktop/flow-architect/**/*.flow",
        "/Users/tajnoah/Downloads/ai-desktop/flow-architect/**/*.toml"
      ],
      "blockedPaths": [
        "/Users/tajnoah/Downloads/ai-desktop/app/**",
        "/Users/tajnoah/Downloads/ai-desktop/components/**",
        "/Users/tajnoah/Downloads/ai-desktop/lib/**",
        "/Users/tajnoah/Downloads/ai-desktop/*.json",
        "/Users/tajnoah/Downloads/ai-desktop/*.js",
        "/Users/tajnoah/Downloads/ai-desktop/*.ts"
      ],
      "autoReject": true,
      "errorMessage": "⛔ SANDBOX VIOLATION: Cannot create files outside flow-architect/"
    }
  }
}
```

**What This Does:**
- ✅ Blocks Read/Edit/Write outside allowed paths
- ✅ Auto-rejects with clear error message
- ✅ Works at system level (agent can't bypass)

#### Step 2: Add Tool Execution Validation
**File:** Create new `.claude/hooks/validate-file-access.sh`

```bash
#!/bin/bash
# .claude/hooks/validate-file-access.sh
#
# Pre-execution hook to validate file access
# Runs BEFORE any Read/Edit/Write tool execution

TOOL_NAME=$1
FILE_PATH=$2
ALLOWED_PREFIX="/Users/tajnoah/Downloads/ai-desktop/flow-architect/"

# Check if file path starts with allowed prefix
if [[ ! "$FILE_PATH" =~ ^$ALLOWED_PREFIX ]]; then
  echo "⛔ SANDBOX VIOLATION BLOCKED"
  echo ""
  echo "Tool: $TOOL_NAME"
  echo "Path: $FILE_PATH"
  echo ""
  echo "Flow Architect can ONLY access files in:"
  echo "  flow-architect/"
  echo ""
  echo "To achieve your goal, create an ACT flow instead."
  exit 1
fi

# Allow if within sandbox
exit 0
```

**Register Hook:**
Add to `.claude/settings.local.json`:
```json
{
  "hooks": {
    "beforeToolExecution": {
      "Read": ".claude/hooks/validate-file-access.sh Read",
      "Edit": ".claude/hooks/validate-file-access.sh Edit",
      "Write": ".claude/hooks/validate-file-access.sh Write"
    }
  }
}
```

**What This Does:**
- ✅ Intercepts tool calls BEFORE execution
- ✅ Validates file path
- ✅ Blocks with clear message if outside sandbox
- ✅ Cannot be bypassed by agent

---

## 📋 Layer 3: Pre-Execution Validation Hooks

**Goal:** Automatically enforce ACT flow creation for EVERY action

### Implementation Steps

#### Step 1: Create ACT Flow Requirement Hook
**File:** `.claude/hooks/require-act-flow.sh`

```bash
#!/bin/bash
# .claude/hooks/require-act-flow.sh
#
# Ensures agent ALWAYS creates ACT flows for actions
# Runs on user message submission

USER_MESSAGE=$1

# Keywords that trigger "action" requirement
ACTION_KEYWORDS=(
  "calculate" "compute" "what's" "what is"
  "get" "fetch" "retrieve" "find"
  "generate" "create" "make" "build"
  "random" "pick" "select" "choose"
  "check" "monitor" "watch" "track"
  "send" "notify" "alert" "email"
  "process" "transform" "convert"
)

# Check if message contains action keywords
for keyword in "${ACTION_KEYWORDS[@]}"; do
  if echo "$USER_MESSAGE" | grep -qi "\b$keyword\b"; then
    # Action detected - require flow creation
    echo "⚠️ ACTION DETECTED: '$keyword'"
    echo ""
    echo "Flow Architect must create an ACT flow for this action."
    echo "Do NOT answer directly. Create and execute a .act file first."
    echo ""
    # Allow but remind
    exit 0
  fi
done

# Not an action - allow
exit 0
```

**Register Hook:**
```json
{
  "hooks": {
    "userPromptSubmit": ".claude/hooks/require-act-flow.sh"
  }
}
```

#### Step 2: Add ACT Flow Validation
**File:** `.claude/hooks/validate-act-execution.sh`

```bash
#!/bin/bash
# .claude/hooks/validate-act-execution.sh
#
# Ensures flows are created in correct location and executed

FLOW_PATH=$1

# Must be in flow-architect/flows/ or flow-architect/temp/
ALLOWED_FLOWS="flow-architect/(flows|temp)/"

if [[ ! "$FLOW_PATH" =~ $ALLOWED_FLOWS ]]; then
  echo "⛔ INVALID FLOW LOCATION"
  echo ""
  echo "ACT flows must be created in:"
  echo "  flow-architect/flows/     (permanent flows)"
  echo "  flow-architect/temp/      (temporary actions)"
  echo ""
  echo "Current path: $FLOW_PATH"
  exit 1
fi

echo "✅ Flow location validated: $FLOW_PATH"
exit 0
```

---

## 📋 Layer 4: User-Facing Messaging

**Goal:** Clear communication when sandbox is enforced

### Implementation Steps

#### Step 1: Create Sandbox Violation Response Template
**File:** `flow-architect/.claude/templates/sandbox-violation.md`

```markdown
# ⛔ Sandbox Violation Prevented

I cannot access files outside my `flow-architect/` directory.

**You asked me to:** {user_request}

**I attempted to:** {attempted_action}

**This is forbidden because:** I can only modify files within flow-architect/

---

## ✅ What I Can Do Instead

{flow_based_alternative}

Would you like me to create this flow-based solution?
```

#### Step 2: Create ACT Flow Reminder Template
**File:** `flow-architect/.claude/templates/act-flow-reminder.md`

```markdown
# 🔄 Creating ACT Flow

Your request requires execution. I'm creating an ACT flow to handle this.

**Task:** {task_description}

**Flow Location:** flow-architect/temp/{flow_name}.act

**Steps:**
1. Create flow file
2. Execute via /api/act/execute
3. Parse results
4. Respond with answer

---

**Flow Creation in Progress...**
```

#### Step 3: Update Agent Instructions
Add to `flow-architect/.claude/agents/flow-architect.md`:

```markdown
## 📢 USER COMMUNICATION TEMPLATES

When sandbox violation is detected, use:
→ flow-architect/.claude/templates/sandbox-violation.md

When creating ACT flow for action, announce:
→ flow-architect/.claude/templates/act-flow-reminder.md

**Never execute actions without flows. Always announce flow creation.**
```

---

## 📋 Layer 5: Testing & Monitoring

**Goal:** Verify enforcement and catch violations

### Implementation Steps

#### Step 1: Create Sandbox Test Suite
**File:** `flow-architect/tests/sandbox-enforcement.test.sh`

```bash
#!/bin/bash
# flow-architect/tests/sandbox-enforcement.test.sh
#
# Test that sandbox enforcement works

echo "🧪 Testing Sandbox Enforcement"
echo ""

# Test 1: Cannot read outside sandbox
echo "Test 1: Read outside sandbox should fail"
if claude-code read "app/page.tsx" 2>&1 | grep -q "SANDBOX VIOLATION"; then
  echo "✅ PASS: Read blocked"
else
  echo "❌ FAIL: Read not blocked!"
fi

# Test 2: Cannot edit outside sandbox
echo "Test 2: Edit outside sandbox should fail"
if claude-code edit "package.json" "old" "new" 2>&1 | grep -q "SANDBOX VIOLATION"; then
  echo "✅ PASS: Edit blocked"
else
  echo "❌ FAIL: Edit not blocked!"
fi

# Test 3: Cannot write outside sandbox
echo "Test 3: Write outside sandbox should fail"
if claude-code write "lib/test.ts" "content" 2>&1 | grep -q "SANDBOX VIOLATION"; then
  echo "✅ PASS: Write blocked"
else
  echo "❌ FAIL: Write not blocked!"
fi

# Test 4: Can read inside sandbox
echo "Test 4: Read inside sandbox should succeed"
if claude-code read "flow-architect/README.md" 2>&1 | grep -qv "VIOLATION"; then
  echo "✅ PASS: Read allowed"
else
  echo "❌ FAIL: Read blocked incorrectly!"
fi

# Test 5: Can write inside sandbox
echo "Test 5: Write inside sandbox should succeed"
if claude-code write "flow-architect/temp/test.act" "[workflow]" 2>&1 | grep -qv "VIOLATION"; then
  echo "✅ PASS: Write allowed"
  rm -f flow-architect/temp/test.act
else
  echo "❌ FAIL: Write blocked incorrectly!"
fi

echo ""
echo "🧪 Sandbox Enforcement Tests Complete"
```

#### Step 2: Create ACT Flow Enforcement Test
**File:** `flow-architect/tests/act-flow-enforcement.test.sh`

```bash
#!/bin/bash
# flow-architect/tests/act-flow-enforcement.test.sh
#
# Test that agent creates flows for actions

echo "🧪 Testing ACT Flow Enforcement"
echo ""

# Test actions that should trigger flow creation
ACTIONS=(
  "what's 5 + 10"
  "generate random number"
  "get ISS location"
  "calculate 47 * 89"
)

for action in "${ACTIONS[@]}"; do
  echo "Testing: $action"

  # Check if agent creates a flow file
  if claude-code "$action" --dry-run 2>&1 | grep -q "Creating ACT flow"; then
    echo "✅ PASS: Flow creation triggered"
  else
    echo "❌ FAIL: Direct answer (no flow)!"
  fi
done

echo ""
echo "🧪 ACT Flow Enforcement Tests Complete"
```

#### Step 3: Add Monitoring Script
**File:** `flow-architect/monitor-violations.sh`

```bash
#!/bin/bash
# flow-architect/monitor-violations.sh
#
# Monitor for sandbox violations in real-time

echo "🔍 Monitoring for sandbox violations..."
echo "Press Ctrl+C to stop"
echo ""

# Watch Claude Code logs for violations
tail -f ~/.claude/logs/*.log | grep --line-buffered "SANDBOX VIOLATION" | while read line; do
  echo "⚠️  VIOLATION DETECTED:"
  echo "$line"
  echo ""

  # Optional: Send alert
  # notify-send "Sandbox Violation" "$line"
done
```

---

## 🚀 Implementation Roadmap

### Phase 1: Immediate (Today)
- [x] Add agent instruction enforcement ✅ (Already done)
- [ ] Create validation hooks
- [ ] Create user messaging templates
- [ ] Test basic enforcement

**Time:** 30 minutes

### Phase 2: System-Level (Tomorrow)
- [ ] Add tool permission restrictions
- [ ] Create pre-execution validation hooks
- [ ] Register hooks in settings
- [ ] Test system-level blocking

**Time:** 1-2 hours

### Phase 3: Testing (After Phase 2)
- [ ] Create test suite
- [ ] Run sandbox enforcement tests
- [ ] Run ACT flow enforcement tests
- [ ] Fix any failures

**Time:** 30 minutes

### Phase 4: Monitoring (Ongoing)
- [ ] Set up violation monitoring
- [ ] Review logs weekly
- [ ] Update enforcement as needed

**Time:** 15 minutes/week

---

## ✅ Success Criteria

The implementation is successful when:

### Sandbox Enforcement
- [ ] Agent cannot Read outside flow-architect/
- [ ] Agent cannot Edit outside flow-architect/
- [ ] Agent cannot Write outside flow-architect/
- [ ] System blocks attempts with clear message
- [ ] All test cases pass

### ACT Flow Enforcement
- [ ] Agent creates flow for "calculate X + Y"
- [ ] Agent creates flow for "generate random number"
- [ ] Agent creates flow for "get [external data]"
- [ ] Agent announces flow creation to user
- [ ] Agent never answers actions directly

### User Experience
- [ ] Clear messages when sandbox blocks action
- [ ] Flow-based alternatives offered
- [ ] User understands boundaries
- [ ] No confusion or frustration

---

## 🎯 Expected Behavior After Implementation

### Example 1: User Asks for Calculation

**User:** "What's 47 + 89?"

**Agent Response:**
```
🔄 Creating ACT Flow

Task: Calculate 47 + 89
Flow Location: flow-architect/temp/calculate-47-plus-89.act

[Creates flow]
[Executes via /api/act/execute]
[Parses result]

**Result: 136**
```

**Not:** Direct answer "136"

### Example 2: User Asks to Modify App

**User:** "Add logging to the API"

**Agent Response:**
```
⛔ Sandbox Violation Prevented

I cannot access files outside my flow-architect/ directory.

You asked me to: Add logging to the API

I attempted to: Edit app/api/*/route.ts files

This is forbidden because: I can only modify files within flow-architect/

---

✅ What I Can Do Instead

I can create a Logging Flow that:
- Monitors your API endpoints via HTTP
- Stores logs in PostgreSQL
- Provides a dashboard to view logs
- Runs as an isolated service

Would you like me to create this flow-based solution?
```

**Not:** Edit app files

### Example 3: User Asks for Random Number

**User:** "Pick a random number between 1 and 100"

**Agent Response:**
```
🔄 Creating ACT Flow

Task: Generate random number between 1 and 100
Flow Location: flow-architect/temp/random-1-100.act

[Creates flow]
[Executes]

**Random Number: 42**
```

**Not:** Direct answer "42"

---

## 🔧 Maintenance Plan

### Weekly
- [ ] Review violation logs
- [ ] Check if any violations occurred
- [ ] Verify all flows created in correct location

### Monthly
- [ ] Run full test suite
- [ ] Update enforcement rules if needed
- [ ] Review user feedback

### Quarterly
- [ ] Audit all flow files
- [ ] Clean up temp/ folder
- [ ] Update documentation

---

## 📊 Monitoring Dashboard (Future)

**Metrics to Track:**
- Sandbox violations attempted
- Sandbox violations blocked
- ACT flows created (by type)
- Direct answers prevented
- User satisfaction

**Goals:**
- 0 violations bypassed
- 100% ACT flow creation for actions
- 0 direct answers to action requests

---

## 🎯 Final Notes

**This plan ensures:**

1. **Absolute Folder Restriction**
   - System-level blocking (can't bypass)
   - Pre-execution validation (catches attempts)
   - Clear error messages (user understands)

2. **Mandatory ACT Flow Creation**
   - All actions require flows
   - User sees flow creation
   - No direct answers allowed

3. **Multiple Defense Layers**
   - Layer 1: Agent instructions ✅
   - Layer 2: Tool permissions ⏳
   - Layer 3: Validation hooks ⏳
   - Layer 4: User messaging ⏳
   - Layer 5: Testing & monitoring ⏳

4. **User Experience**
   - Clear boundaries
   - Alternative solutions offered
   - Transparent process

**Result:** Flow Architect becomes a true "AI Operating System" that:
- Executes EVERYTHING via ACT flows
- NEVER touches the host application
- Operates within strict boundaries
- Provides isolated, containerized solutions

---

## 🚀 Next Steps

**Ready to implement?**

1. Start with **Phase 1** (validation hooks + templates)
2. Continue with **Phase 2** (system-level blocking)
3. Finish with **Phase 3** (testing)
4. Monitor with **Phase 4** (ongoing)

**Time to complete:** 2-3 hours total
**Impact:** Absolute security and compliance

---

**Let's lock down this agent and make it impossible to break the sandbox! 🔒**
