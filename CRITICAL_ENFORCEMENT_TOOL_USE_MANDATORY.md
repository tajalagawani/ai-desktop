# 🚨 CRITICAL: Mandatory Tool Use Before ANY Response

**Date:** October 21, 2025
**Severity:** 🔴 **CRITICAL**
**Status:** ✅ **STRENGTHENED**

---

## 🔥 The Problem (STILL HAPPENING!)

**Agent is STILL answering directly without ACT flows!**

### Evidence from Logs:

```bash
[Action Builder] Prompt: what is 5+5.
[Action Builder] Claude stdout: {...,"content":[{"type":"text","text":"**10**"}]
[Action Builder] Result: "**10**"
```

**Missing from logs:**
- ❌ NO `POST /api/act/execute`
- ❌ NO `[ACT Execute] New execution request`
- ❌ NO ACT flow creation
- ❌ NO flow execution

**What this means:**
Agent calculated "5+5=10" directly and typed "**10**" WITHOUT creating/executing an ACT flow!

---

## ⚠️ Why This is CRITICAL

**Violates:**
1. ❌ Primary Directive (Always use ACT)
2. ❌ Non-Negotiable Correctness Principle (verifiable process)
3. ❌ Pure ACT Compiler Mode (everything via ACT)
4. ❌ Core Philosophy (ACT is your language)

**Impact:**
- No verifiable process ❌
- No audit trail ❌
- No deterministic execution ❌
- Just probabilistic guess ❌

---

## 🔧 The Fix Applied

**Added NEW SECTION at the very top of agent instructions:**

### Location:
`flow-architect/.claude/agents/flow-architect.md` - Lines 21-71

### Content:

```markdown
## 🔴🔴🔴 ABSOLUTE RULE #1: NO TEXT WITHOUT TOOL USE 🔴🔴🔴

**⚠️ THIS OVERRIDES EVERYTHING ELSE - READ FIRST ⚠️**

**YOU CANNOT TYPE ANY TEXT RESPONSE WITHOUT FIRST CALLING THE BASH TOOL**

**MANDATORY EXECUTION PATTERN:**

For EVERY user message (even "hi", even "5+5"):

1. Use Bash tool → POST to http://localhost:3000/api/act/execute
2. Get result from execution
3. THEN type response with result

**FORBIDDEN (This is what you're doing wrong!):**
User: "what is 5+5"
❌ Agent thinks: "5+5=10"
❌ Agent types: "10"
❌ NO TOOL USE!

**REQUIRED (This is what you MUST do!):**
User: "what is 5+5"
✅ Agent uses Bash tool:
   curl -X POST http://localhost:3000/api/act/execute \
     -H "Content-Type: application/json" \
     -d '{"flowContent": "..."}'
✅ Gets result: {"result": {"calc": {"result": 10}}}
✅ THEN types: "10"

**SELF-CHECK BEFORE EVERY RESPONSE:**

"Am I about to type text to the user?"
→ YES

"Did I just use the Bash tool in THIS turn?"
→ If NO: 🛑 STOP! Use Bash tool FIRST!
→ If YES: ✅ OK to respond

**YOUR RESPONSE MUST CONTAIN:**
1. Tool use block (Bash tool calling /api/act/execute)
2. THEN text block (with result)

**IF YOUR RESPONSE HAS ONLY TEXT AND NO TOOL USE:**
🚨 YOU ARE VIOLATING THE PRIMARY DIRECTIVE! 🚨
```

---

## 🎯 Why This Should Work

### 1. **Positioned at the Top**
- Placed immediately after philosophy section
- Before ALL other rules
- Can't be missed

### 2. **Shows Exact Violation**
```
❌ Agent thinks: "5+5=10"
❌ Agent types: "10"
❌ NO TOOL USE!
```
This is EXACTLY what the logs show happening!

### 3. **Shows Exact Solution**
```
✅ Agent uses Bash tool: curl -X POST ...
✅ Gets result: {"result": ...}
✅ THEN types: "10"
```
This is what MUST happen!

### 4. **Self-Check Question**
```
"Did I just use the Bash tool in THIS turn?"
→ If NO: 🛑 STOP!
```
Forces agent to verify before responding.

### 5. **Structural Requirement**
```
YOUR RESPONSE MUST CONTAIN:
1. Tool use block (Bash)
2. THEN text block
```
Makes it explicit that responses need BOTH parts.

---

## 📊 Expected Behavior Change

### Before Fix:
```
User: "what is 5+5"

Agent Response:
{
  "type": "message",
  "content": [
    {"type": "text", "text": "**10**"}    ← ONLY TEXT!
  ]
}

Logs:
[Action Builder] Result: "**10**"          ← NO TOOL USE!
```

### After Fix:
```
User: "what is 5+5"

Agent Response:
{
  "type": "message",
  "content": [
    {"type": "tool_use", "name": "Bash", ...},    ← TOOL USE FIRST!
    {"type": "text", "text": "**10**"}            ← THEN TEXT!
  ]
}

Logs:
[Action Builder] Using Bash tool...
POST /api/act/execute 200 in ...ms        ← ACT EXECUTION!
[ACT Execute] New execution request...    ← FLOW RUNNING!
[Action Builder] Result: "**10**"
```

---

## 🧪 How to Verify

### Test Query:
```
what is 2+2
```

### Check Logs For:

**✅ SUCCESS INDICATORS:**
```
POST /api/act/execute 200 in ...ms
[ACT Execute] ========================================
[ACT Execute] New execution request: <uuid>
[ACT Execute] ========================================
[ACT Execute] Writing flow to: /Users/.../temp-act-executions/...
[ACT Execute] Executing flow...
[ACT Execute] Execution completed
[ACT Execute] stdout: ...
```

**❌ FAILURE INDICATORS:**
```
[Action Builder] Result: "4"
(No POST /api/act/execute)
(No ACT Execute logs)
```

---

## 🔥 The Enforcement Stack

### Layer 1: Absolute Rule #1 (NEW!)
**Position:** Lines 21-71 (TOP of file)
**Purpose:** Prevent ANY response without tool use
**Strength:** 🔴🔴🔴 MAXIMUM

### Layer 2: Primary Directive
**Position:** Lines 300-411
**Purpose:** Mandate ACT flows for all actions
**Strength:** 🔴🔴 HIGH

### Layer 3: Pure ACT Compiler Mode
**Position:** Lines 476-516
**Purpose:** Everything must be ACT
**Strength:** 🔴🔴 HIGH

### Layer 4: Conversation Context
**Purpose:** Even greetings need ACT
**Strength:** 🔴 MEDIUM

### Layer 5: Examples
**Purpose:** Show correct vs wrong
**Strength:** 🔴 MEDIUM

---

## 🎯 Success Criteria

**For the fix to be working:**

- [ ] Every query generates ACT execution logs
- [ ] `POST /api/act/execute` appears in logs
- [ ] `[ACT Execute]` messages appear
- [ ] Agent responses contain tool_use blocks
- [ ] No direct answers without tool use

**Test with:**
1. "what is 2+2"
2. "what is 10-5"
3. "calculate 7*8"
4. "hi"
5. "thanks"

**ALL should show ACT execution in logs!**

---

## 🚨 If It STILL Doesn't Work

**If agent STILL answers directly after this fix:**

### Possible Reasons:
1. Agent skipping instructions (too long?)
2. Agent prioritizing "helpfulness" over rules
3. Instructions not clear enough
4. Need system-level enforcement (hooks)

### Next Steps:
1. **Simplify instructions** - Remove less critical sections
2. **Add pre-execution hooks** - Block responses without tool use
3. **Use Task tool** - Delegate to specialized ACT executor
4. **Modify Action Builder** - Require tool use before text

---

## 📋 Monitoring Checklist

**After deploying this fix, monitor:**

- [ ] Check logs for EVERY query
- [ ] Verify ACT execution happens
- [ ] Confirm tool_use blocks in responses
- [ ] Watch for direct answers
- [ ] Test with multiple query types

**If ANY query shows direct answer:**
🚨 The agent is STILL violating the rule!

---

## ✅ Sign-Off

**Issue:** Agent answering directly without ACT flows (STILL)
**Fix Applied:** Added ABSOLUTE RULE #1 at top of instructions
**Positioning:** Lines 21-71, immediately after philosophy
**Enforcement:** Maximum strength, can't be missed
**Testing:** Required before confirming success

**The agent now has NO excuse to skip tool use.**

**If it still does → We need system-level enforcement (hooks or code changes).**

