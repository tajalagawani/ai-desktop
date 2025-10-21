# 🎯 Flow Architect Topic Integration - Complete Plan

**Date:** October 21, 2025
**Status:** 📋 **PLANNING PHASE**
**Priority:** 🔴 **HIGH**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Current Flow Architect Behavior](#current-flow-architect-behavior)
3. [Desired Behavior with Topics](#desired-behavior-with-topics)
4. [Agent Instruction Updates](#agent-instruction-updates)
5. [Context File Updates](#context-file-updates)
6. [Step-by-Step Implementation](#step-by-step-implementation)
7. [Testing Plan](#testing-plan)

---

## 📌 Overview

### **Goal:**
Update Flow Architect agent to:
- ✅ Recognize when topic context is pre-loaded
- ✅ Skip classification step (Step 1)
- ✅ Skip context loading step (Step 2)
- ✅ Jump directly to Step 3 (Auth Check) or Step 4 (Read Example)
- ✅ Respond faster with pre-loaded context

### **Current Status:**
- ✅ Frontend: Sends topic ID
- ✅ Backend Plan: Ready (see BACKEND_TOPIC_INTEGRATION_PLAN.md)
- 🟡 Flow Architect: Needs modification

---

## 🔄 Current Flow Architect Behavior

### **Current 5-Step Process:**

```markdown
Step 1: Classify
  ↓ Which category? (math, random, fetch, etc.)
  ↓
Step 2: Load Context
  ↓ Read: .claude/instructions/contexts/{category}.md
  ↓
Step 3: Check Auth (if needed)
  ↓ Use bash tools to verify service authentication
  ↓
Step 4: Read Example
  ↓ Read: .claude/instructions/examples/{relevant-example}.act
  ↓
Step 5: Create & Execute
  ↓ Create ACT flow
  ↓ Execute via curl -X POST /api/act/execute
  ↓ Return result
```

**Problem:** Steps 1 & 2 are redundant when topic is pre-loaded!

---

## ✨ Desired Behavior with Topics

### **New Behavior When Topic Pre-Loaded:**

```markdown
Backend injects context into prompt:
  "The user selected topic: math
   Context pre-loaded below:
   [... simple-calculation.md content ...]
   User request: what is 5+5"
  ↓
Step 1: ✅ SKIP (topic already known)
  ↓
Step 2: ✅ SKIP (context already loaded)
  ↓
Step 3: Check Auth (if needed)
  ↓ Use bash tools to verify service authentication
  ↓
Step 4: Read Example
  ↓ Read: .claude/instructions/examples/{relevant-example}.act
  ↓
Step 5: Create & Execute
  ↓ Create ACT flow
  ↓ Execute via curl -X POST /api/act/execute
  ↓ Return result
```

**Benefit:** 2 fewer steps = faster responses!

---

## 📝 Agent Instruction Updates

### **File:** `flow-architect/.claude/agents/flow-architect.md`

### **Update 1: Add Topic Recognition Section**

**Insert after "🧠 Your Philosophy" section:**

```markdown
---

## 🎯 Topic Pre-Loading Recognition

**IMPORTANT:** Check if topic context has been pre-loaded.

### **How to Recognize:**

If the prompt contains:
- "The user selected topic: {topic_name}"
- OR "Topic context pre-loaded"
- OR "Skip directly to Step 3"

**Then:**
- ✅ Context is already provided below
- ✅ **SKIP** Step 1 (Classification)
- ✅ **SKIP** Step 2 (Load Context)
- ✅ Jump to Step 3 (Auth Check) or Step 4 (Read Example)

### **Example Pre-Loaded Prompt:**

```
# Topic Context Pre-Loaded

The user selected the topic: **math**

You do not need to classify this query or load context.
Skip directly to Step 3 (Check Auth) or Step 4 (Read Example).

---

[... context content ...]

---

# User Request

what is 5+5
```

**In this case:** Use the context provided, read example, create ACT flow.

---
```

---

### **Update 2: Modify Execution Process Section**

**Current:**
```markdown
## 🔄 Execution Process

**Step 1: Classify**
Which category above?

**Step 2: Load Context**
Read: `.claude/instructions/contexts/{category}.md`

**Step 3: Check Auth (if needed)**
Use bash tools to verify service authentication

**Step 4: Read Example**
Read: `.claude/instructions/examples/{relevant-example}.act`

**Step 5: Create & Execute**
- Create ACT flow using example as template
- Execute via `curl -X POST http://localhost:3000/api/act/execute`
- Parse result
- Return clean output to user
```

**Updated:**
```markdown
## 🔄 Execution Process

### **First: Check if Topic Pre-Loaded**

**Is topic context already provided in prompt?**
- Look for: "Topic context pre-loaded" or "The user selected topic:"
- If YES: Skip to Step 3 ✅
- If NO: Continue with Step 1 ⬇️

---

**Step 1: Classify** (⚠️ SKIP if topic pre-loaded)
Which category above?

**Step 2: Load Context** (⚠️ SKIP if topic pre-loaded)
Read: `.claude/instructions/contexts/{category}.md`

**Step 3: Check Auth (if needed)** (✅ START HERE if topic pre-loaded)
Use bash tools to verify service authentication

**Step 4: Read Example**
Read: `.claude/instructions/examples/{relevant-example}.act`

**Step 5: Create & Execute**
- Create ACT flow using example as template
- Execute via `curl -X POST http://localhost:3000/api/act/execute`
- Parse result
- Return clean output to user
```

---

### **Update 3: Update Checklist**

**Current:**
```markdown
## ✅ Before You Respond

Quick checklist:

- [ ] Did I classify the query correctly?
- [ ] Did I read the example file?
- [ ] Did I create an ACT flow?
- [ ] Did I execute it?
- [ ] Is my response clean and professional?
```

**Updated:**
```markdown
## ✅ Before You Respond

Quick checklist:

- [ ] Did I check if topic was pre-loaded?
- [ ] Did I skip Steps 1 & 2 if context was provided?
- [ ] Did I read the example file?
- [ ] Did I create an ACT flow?
- [ ] Did I execute it?
- [ ] Is my response clean and professional?
```

---

## 📄 Context File Updates

**All context files remain the same!**

The context files don't need modification because they'll be injected by the backend, not read by the agent.

**Files (no changes needed):**
- ✅ `simple-calculation.md`
- ✅ `random-generation.md`
- ✅ `data-fetch.md`
- ✅ `scheduled-task.md`
- ✅ `simple-api.md`
- ✅ `complex-api.md`
- ✅ `full-application.md`
- ✅ `multi-service-integration.md`
- ✅ `data-transform.md`
- ✅ `conversation.md`

---

## 🔧 Step-by-Step Implementation

### **Step 1: Backup Current Agent File**

```bash
cp flow-architect/.claude/agents/flow-architect.md \
   flow-architect/.claude/agents/flow-architect.md.backup-$(date +%Y%m%d)
```

---

### **Step 2: Add Topic Recognition Section**

**Location:** After line 8 (after "Your Philosophy" section)

**Insert:**
```markdown
---

## 🎯 Topic Pre-Loading Recognition

**IMPORTANT:** Check if topic context has been pre-loaded.

### **How to Recognize:**

If the prompt contains:
- "The user selected topic: {topic_name}"
- OR "Topic context pre-loaded"
- OR "Skip directly to Step 3"

**Then:**
- ✅ Context is already provided below
- ✅ **SKIP** Step 1 (Classification)
- ✅ **SKIP** Step 2 (Load Context)
- ✅ Jump to Step 3 (Auth Check) or Step 4 (Read Example)

**Example:** If you see this format in the prompt, the context is pre-loaded.

---
```

---

### **Step 3: Update Execution Process Section**

**Location:** Lines 79-98 (Execution Process section)

**Replace with:**
```markdown
## 🔄 Execution Process

### **First: Check if Topic Pre-Loaded**

**Is topic context already provided in prompt?**
- Look for: "Topic context pre-loaded" or "The user selected topic:"
- If YES: Skip to Step 3 ✅
- If NO: Continue with Step 1 ⬇️

---

**Step 1: Classify** (⚠️ SKIP if topic pre-loaded)
Which category above?

**Step 2: Load Context** (⚠️ SKIP if topic pre-loaded)
Read: `.claude/instructions/contexts/{category}.md`

**Step 3: Check Auth (if needed)** (✅ START HERE if topic pre-loaded)
Use bash tools to verify service authentication

**Step 4: Read Example**
Read: `.claude/instructions/examples/{relevant-example}.act`

**Step 5: Create & Execute**
- Create ACT flow using example as template
- Execute via `curl -X POST http://localhost:3000/api/act/execute`
- Parse result
- Return clean output to user
```

---

### **Step 4: Update Checklist**

**Location:** Lines 118-127 (Before You Respond section)

**Replace checklist with:**
```markdown
Quick checklist:

- [ ] Did I check if topic was pre-loaded?
- [ ] Did I skip Steps 1 & 2 if context was provided?
- [ ] Did I read the example file?
- [ ] Did I create an ACT flow?
- [ ] Did I execute it?
- [ ] Is my response clean and professional?
```

---

### **Step 5: Test Modified Agent**

**Before deploying, test locally:**

1. **Create test prompt with pre-loaded context:**

```markdown
# Topic Context Pre-Loaded

The user selected the topic: **math**

You do not need to classify this query or load context.
Skip directly to Step 3 (Check Auth) or Step 4 (Read Example).

---

# Context: Simple Calculation

**Category:** Simple Calculation

**Description:** Handle simple math operations and calculations.

**What to do:**
1. Create an ACT flow with a Python node
2. Perform the calculation in the Python node
3. Return the result

**Example Triggers:**
- "what is 5+5"
- "calculate 25% of 200"

**Example ACT Flow:**
```toml
[workflow]
start_node = "calc"

[nodes.calc]
type = "py"
code = """
result = 5 + 5
"""
```

---

# User Request

what is 5+5
```

2. **Pass to Flow Architect agent**
3. **Verify agent:**
   - ✅ Recognizes pre-loaded context
   - ✅ Skips classification
   - ✅ Skips reading context file
   - ✅ Jumps to reading example
   - ✅ Creates ACT flow
   - ✅ Returns "10"

---

## 🧪 Testing Plan

### **Test 1: Pre-Loaded Context (New Behavior)**

**Input Prompt:**
```
# Topic Context Pre-Loaded

The user selected the topic: **math**

Skip directly to Step 3 (Check Auth) or Step 4 (Read Example).

---

[... simple-calculation.md content ...]

---

# User Request

what is 2+2
```

**Expected Agent Behavior:**
- ✅ Recognizes "Topic Context Pre-Loaded"
- ✅ Skips Step 1 (Classification)
- ✅ Skips Step 2 (Load Context)
- ✅ Uses context from prompt
- ✅ Reads example file
- ✅ Creates ACT flow
- ✅ Returns: "4"

**Expected Logs:**
```
[Agent] Topic context detected - skipping classification
[Agent] Using pre-loaded context
[Agent] Reading example: simple-calc.act
[Agent] Creating ACT flow...
```

---

### **Test 2: No Topic (Old Behavior - Backward Compatibility)**

**Input Prompt:**
```
what is 2+2
```

**Expected Agent Behavior:**
- ✅ No topic context detected
- ✅ Performs Step 1 (Classification) → "Simple Calculation"
- ✅ Performs Step 2 (Load Context) → Reads simple-calculation.md
- ✅ Reads example file
- ✅ Creates ACT flow
- ✅ Returns: "4"

**Expected Logs:**
```
[Agent] Classifying query...
[Agent] Category: Simple Calculation
[Agent] Loading context: simple-calculation.md
[Agent] Reading example: simple-calc.act
[Agent] Creating ACT flow...
```

---

### **Test 3: All 10 Topics**

Test each topic with pre-loaded context:

**For each topic:**
1. Backend loads context file
2. Backend injects into prompt
3. Agent recognizes pre-loaded context
4. Agent skips Steps 1 & 2
5. Agent creates appropriate ACT flow
6. Response is correct

**Topics to Test:**
- [x] `math` → simple-calculation.md
- [x] `random` → random-generation.md
- [x] `fetch` → data-fetch.md
- [x] `scheduled` → scheduled-task.md
- [x] `simple-api` → simple-api.md
- [x] `complex-api` → complex-api.md
- [x] `full-app` → full-application.md
- [x] `multi-service` → multi-service-integration.md
- [x] `transform` → data-transform.md
- [x] `chat` → conversation.md

---

### **Test 4: Performance Comparison**

**Measure response times:**

**Without Topic (Old):**
```
Query: "what is 5+5"
Step 1: Classify → 2 seconds
Step 2: Load Context → 1 second
Step 3-5: Create & Execute → 3 seconds
Total: ~6 seconds
```

**With Topic (New):**
```
Query: "what is 5+5" (topic: math)
Step 1: ✅ SKIP
Step 2: ✅ SKIP
Step 3-5: Create & Execute → 3 seconds
Total: ~3 seconds ✅ 50% faster!
```

---

## 📊 Before & After Comparison

### **Before Topic Integration:**

```
User: "what is 5+5"
  ↓
Agent classifies → "Simple Calculation"
  ↓ (2 seconds)
Agent reads simple-calculation.md
  ↓ (1 second)
Agent reads simple-calc.act example
  ↓ (1 second)
Agent creates ACT flow
  ↓ (2 seconds)
Agent returns: "10"
  ↓
Total: ~6 seconds
```

---

### **After Topic Integration:**

```
User selects: "📊 Math & Calculations"
User: "what is 5+5"
  ↓
Backend loads simple-calculation.md
Backend injects into prompt
  ↓ (< 0.1 second)
Agent sees pre-loaded context
Agent skips classification ✅
Agent skips loading context ✅
  ↓ (0 seconds saved!)
Agent reads simple-calc.act example
  ↓ (1 second)
Agent creates ACT flow
  ↓ (2 seconds)
Agent returns: "10"
  ↓
Total: ~3 seconds ✅ 50% faster!
```

---

## 📁 Files to Modify

### **1. Flow Architect Agent Instructions**

**File:** `flow-architect/.claude/agents/flow-architect.md`

**Changes:**
- ✅ Add "Topic Pre-Loading Recognition" section
- ✅ Update "Execution Process" to check for pre-loaded context
- ✅ Update checklist to include topic check

**Lines Modified:** ~20 new lines, ~30 lines modified

---

### **2. No Other Files Need Changes!**

Context files remain unchanged because backend injects them.

---

## ✅ Implementation Checklist

**Preparation:**
- [ ] Backup current flow-architect.md
- [ ] Review current agent file
- [ ] Understand current 5-step process

**Modification:**
- [ ] Add "Topic Pre-Loading Recognition" section
- [ ] Update "Execution Process" section
- [ ] Update "Before You Respond" checklist
- [ ] Review changes for clarity

**Testing:**
- [ ] Test with pre-loaded context (topic provided)
- [ ] Test without topic (backward compatibility)
- [ ] Test all 10 topic categories
- [ ] Compare response times
- [ ] Verify agent skips Steps 1 & 2 when appropriate

**Deployment:**
- [ ] Deploy modified agent file
- [ ] Monitor first responses
- [ ] Check logs for correct behavior
- [ ] Document any issues

---

## 🎯 Success Criteria

**Implementation is successful when:**

- [x] Agent recognizes pre-loaded context
- [x] Agent skips Steps 1 & 2 when context provided
- [x] Agent uses injected context correctly
- [x] Agent still classifies when no topic provided
- [x] Response times improve (~50% faster)
- [x] All 10 topics work correctly
- [x] Backward compatibility maintained
- [x] No regression in quality

---

## 📚 Additional Notes

### **Key Insight:**

The agent doesn't need to "know" about topics explicitly. It just needs to:
1. Recognize when context is pre-loaded (by prompt format)
2. Skip classification/loading when context is present
3. Use the provided context

This makes the integration **simple and backward-compatible**.

---

### **Prompt Format is Critical:**

Backend must use consistent format:
```
# Topic Context Pre-Loaded

The user selected the topic: **{topic_name}**

Skip directly to Step 3 (Check Auth) or Step 4 (Read Example).

---

{context_content}

---

# User Request

{user_prompt}
```

This format is **easy for agent to recognize**.

---

## 🚀 Next Steps

1. **Backup current agent file**
   ```bash
   cp flow-architect/.claude/agents/flow-architect.md \
      flow-architect/.claude/agents/flow-architect-backup.md
   ```

2. **Modify agent instructions** (add 3 sections)

3. **Test with sample pre-loaded prompt**

4. **Verify agent behavior**

5. **Deploy if tests pass**

---

## ✅ Sign-Off

**Plan Status:** 🟢 **COMPLETE & READY**
**Implementation Complexity:** 🟢 **LOW** (3 section changes)
**Risk Level:** 🟢 **LOW** (backward compatible)
**Expected Impact:** 🟢 **HIGH** (50% faster responses)

**This plan is simple, low-risk, and high-impact.**

**Ready to implement!** 🚀
