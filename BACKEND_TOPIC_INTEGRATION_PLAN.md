# 🎯 Backend Topic-Based Chat Integration - Complete Plan

**Date:** October 21, 2025
**Status:** 📋 **PLANNING PHASE**
**Priority:** 🔴 **HIGH**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Current Architecture](#current-architecture)
3. [What Frontend Sends](#what-frontend-sends)
4. [Backend Changes Required](#backend-changes-required)
5. [Step-by-Step Implementation](#step-by-step-implementation)
6. [Files to Modify](#files-to-modify)
7. [Testing Plan](#testing-plan)
8. [Rollback Plan](#rollback-plan)

---

## 📌 Overview

### **Goal:**
Enable topic-based context pre-loading in Action Builder so the Flow Architect agent:
- ✅ Skips classification step (Step 1)
- ✅ Skips context loading step (Step 2)
- ✅ Gets context injected directly
- ✅ Responds faster with better accuracy

### **Frontend Status:**
✅ **COMPLETE** - Frontend sends topic ID via WebSocket

### **Backend Status:**
🟡 **PENDING** - Need to extract topic and inject context

---

## 🏗️ Current Architecture

### **Flow: User Message → Claude Response**

```
1. User types message in frontend
   ↓
2. Frontend sends via WebSocket:
   {
     type: 'start_chat',
     prompt: 'what is 5+5',
     sessionId: 'session-123',
     topic: 'math'  ← NEW
   }
   ↓
3. Backend receives WebSocket message
   ↓
4. Backend spawns Claude CLI subprocess
   ↓
5. Backend passes:
   - Agent instructions (flow-architect.md)
   - User prompt
   ↓
6. Claude processes and responds
   ↓
7. Backend streams response back to frontend
```

---

## 📨 What Frontend Sends

### **WebSocket Message Structure:**

```json
{
  "type": "start_chat",
  "prompt": "what is 5+5",
  "sessionId": "session-abc-123",
  "resume": false,
  "topic": "math"
}
```

### **Topic ID Mapping:**

| Topic ID | Context File | Description |
|----------|-------------|-------------|
| `math` | `simple-calculation.md` | Math calculations |
| `random` | `random-generation.md` | Random numbers/choices |
| `fetch` | `data-fetch.md` | External API data |
| `scheduled` | `scheduled-task.md` | Cron/scheduled tasks |
| `simple-api` | `simple-api.md` | 2-5 endpoint APIs |
| `complex-api` | `complex-api.md` | 6-15 endpoint APIs |
| `full-app` | `full-application.md` | 30+ endpoint systems |
| `multi-service` | `multi-service-integration.md` | Multi-service workflows |
| `transform` | `data-transform.md` | Data transformation |
| `chat` | `conversation.md` | General conversation |

---

## 🔧 Backend Changes Required

### **Change 1: WebSocket Handler - Extract Topic**
- **Where:** WebSocket message handler (where `start_chat` is received)
- **What:** Extract `topic` field from incoming message
- **Why:** Need to know which context to load

### **Change 2: Context File Loader - New Function**
- **Where:** New utility function or in existing handler
- **What:** Load context markdown file based on topic ID
- **Why:** Need to read the appropriate context file

### **Change 3: Prompt Builder - Inject Context**
- **Where:** Where Claude CLI prompt is constructed
- **What:** Prepend context to user's prompt
- **Why:** Give Claude the context without classification

### **Change 4: Agent Instructions - Optional Enhancement**
- **Where:** flow-architect.md loading
- **What:** Modify agent instructions to skip classification when topic provided
- **Why:** Make agent aware that context is pre-loaded

---

## 📝 Step-by-Step Implementation

### **Step 1: Locate WebSocket Handler**

**File to Find:**
- Look for file handling WebSocket connections in Action Builder
- Likely in: `components/apps/act-docker/act/` or backend WebSocket route
- Search for: `'start_chat'` message type handler

**Action:**
```bash
# Find the WebSocket handler
grep -r "start_chat" components/apps/act-docker/act/
# OR
grep -r "type.*start_chat" .
```

**What to Look For:**
```python
# Example of what you're looking for:
async def handle_websocket_message(message):
    message_type = message.get('type')

    if message_type == 'start_chat':
        prompt = message.get('prompt')
        session_id = message.get('sessionId')
        # Add: topic = message.get('topic')
```

---

### **Step 2: Extract Topic from Message**

**Modification:**
```python
# Before:
async def handle_start_chat(message):
    prompt = message.get('prompt', '')
    session_id = message.get('sessionId')
    resume = message.get('resume', False)

    # ... rest of code

# After:
async def handle_start_chat(message):
    prompt = message.get('prompt', '')
    session_id = message.get('sessionId')
    resume = message.get('resume', False)
    topic_id = message.get('topic')  # NEW: Extract topic

    # Log for debugging
    logger.info(f"[Action Builder] Received message with topic: {topic_id}")

    # ... rest of code
```

---

### **Step 3: Create Context Loader Function**

**Create New Function:**

```python
import os
import logging

logger = logging.getLogger(__name__)

# Topic ID to context file mapping
TOPIC_CONTEXT_MAP = {
    'math': 'simple-calculation.md',
    'random': 'random-generation.md',
    'fetch': 'data-fetch.md',
    'scheduled': 'scheduled-task.md',
    'simple-api': 'simple-api.md',
    'complex-api': 'complex-api.md',
    'full-app': 'full-application.md',
    'multi-service': 'multi-service-integration.md',
    'transform': 'data-transform.md',
    'chat': 'conversation.md'
}

def load_topic_context(topic_id: str, project_root: str) -> str:
    """
    Load the context file for the selected topic.

    Args:
        topic_id: The topic identifier (e.g., 'math', 'random')
        project_root: Root directory of the project

    Returns:
        str: The context file content, or empty string if not found
    """
    if not topic_id or topic_id not in TOPIC_CONTEXT_MAP:
        logger.debug(f"No topic provided or invalid topic: {topic_id}")
        return ""

    context_filename = TOPIC_CONTEXT_MAP[topic_id]
    context_path = os.path.join(
        project_root,
        'flow-architect',
        '.claude',
        'instructions',
        'contexts',
        context_filename
    )

    try:
        if not os.path.exists(context_path):
            logger.warning(f"Context file not found: {context_path}")
            return ""

        with open(context_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"Loaded context for topic '{topic_id}' from {context_filename}")
            return content

    except Exception as e:
        logger.error(f"Error loading context file: {e}", exc_info=True)
        return ""
```

---

### **Step 4: Build Enhanced Prompt**

**Create Prompt Builder Function:**

```python
def build_enhanced_prompt(
    user_prompt: str,
    topic_id: str = None,
    project_root: str = None
) -> str:
    """
    Build enhanced prompt with topic context pre-loaded.

    Args:
        user_prompt: The user's original message
        topic_id: Optional topic identifier
        project_root: Project root directory

    Returns:
        str: Enhanced prompt with context, or original prompt
    """
    # If no topic provided, return original prompt
    if not topic_id:
        return user_prompt

    # Load topic context
    topic_context = load_topic_context(topic_id, project_root)

    # If context not found, return original prompt
    if not topic_context:
        logger.warning(f"Could not load context for topic '{topic_id}', using original prompt")
        return user_prompt

    # Build enhanced prompt with context pre-loaded
    enhanced_prompt = f"""# Topic Context Pre-Loaded

The user selected the topic: **{topic_id}**

You do not need to classify this query or load context - it has been pre-loaded below.

Skip directly to Step 3 (Check Auth) or Step 4 (Read Example) as appropriate.

---

{topic_context}

---

# User Request

{user_prompt}
"""

    logger.debug(f"Built enhanced prompt with {len(topic_context)} chars of context")
    return enhanced_prompt
```

---

### **Step 5: Integrate into Claude CLI Spawn**

**Find Claude CLI Spawn Location:**

```bash
# Search for where Claude CLI is spawned
grep -r "claude" components/apps/act-docker/act/ | grep -i spawn
# OR
grep -r "subprocess" components/apps/act-docker/act/
```

**Modify Spawn Logic:**

```python
# Before:
def spawn_claude_cli(prompt, session_id):
    # ... setup code

    # Pass prompt to Claude
    process = subprocess.Popen([
        'claude',
        '--agent', agent_file_path,
        '--prompt', prompt  # Original prompt
    ])

    # ... rest

# After:
def spawn_claude_cli(prompt, session_id, topic_id=None, project_root=None):
    # ... setup code

    # Build enhanced prompt if topic provided
    enhanced_prompt = build_enhanced_prompt(prompt, topic_id, project_root)

    logger.info(f"[Claude CLI] Using {'enhanced' if topic_id else 'standard'} prompt")

    # Pass enhanced prompt to Claude
    process = subprocess.Popen([
        'claude',
        '--agent', agent_file_path,
        '--prompt', enhanced_prompt  # Enhanced prompt with context
    ])

    # ... rest
```

---

### **Step 6: Update WebSocket Handler - Complete Integration**

**Full Integration Example:**

```python
async def handle_start_chat(message, project_root='/path/to/project'):
    """
    Handle start_chat WebSocket message with topic support.
    """
    # Extract message fields
    prompt = message.get('prompt', '')
    session_id = message.get('sessionId')
    resume = message.get('resume', False)
    topic_id = message.get('topic')  # NEW

    # Log incoming request
    logger.info(f"[Action Builder] Start chat - Session: {session_id}, Topic: {topic_id or 'none'}")

    # Build enhanced prompt with topic context
    enhanced_prompt = build_enhanced_prompt(prompt, topic_id, project_root)

    # Spawn Claude CLI with enhanced prompt
    await spawn_claude_cli(
        prompt=enhanced_prompt,
        session_id=session_id,
        topic_id=topic_id,
        project_root=project_root
    )

    logger.info(f"[Action Builder] Claude CLI spawned for session {session_id}")
```

---

## 📁 Files to Modify

### **1. WebSocket Handler**

**File:** (To be determined - likely in `components/apps/act-docker/act/`)

**Changes:**
- Extract `topic` field from message
- Call `build_enhanced_prompt()` with topic
- Pass enhanced prompt to Claude CLI

---

### **2. Create New Utility File**

**File:** `components/apps/act-docker/act/topic_context_loader.py` (NEW)

**Contents:**
```python
# Topic context loading utilities
# - TOPIC_CONTEXT_MAP
# - load_topic_context()
# - build_enhanced_prompt()
```

---

### **3. Import in WebSocket Handler**

**Add import:**
```python
from topic_context_loader import build_enhanced_prompt, load_topic_context
```

---

## 🧪 Testing Plan

### **Test 1: No Topic Provided (Backward Compatibility)**

**Input:**
```json
{
  "type": "start_chat",
  "prompt": "what is 5+5",
  "sessionId": "test-1"
}
```

**Expected:**
- ✅ Works as before (no topic)
- ✅ Agent classifies query
- ✅ Agent loads context
- ✅ Agent creates ACT flow
- ✅ Returns: "10"

---

### **Test 2: Topic Provided (New Behavior)**

**Input:**
```json
{
  "type": "start_chat",
  "prompt": "what is 5+5",
  "sessionId": "test-2",
  "topic": "math"
}
```

**Expected:**
- ✅ Backend extracts topic: "math"
- ✅ Backend loads: `simple-calculation.md`
- ✅ Backend builds enhanced prompt with context
- ✅ Agent receives context pre-loaded
- ✅ Agent skips classification
- ✅ Agent creates ACT flow directly
- ✅ Returns: "10" (faster!)

**Logs to Check:**
```
[Action Builder] Received message with topic: math
[Topic Loader] Loaded context for topic 'math' from simple-calculation.md
[Claude CLI] Using enhanced prompt
```

---

### **Test 3: Invalid Topic**

**Input:**
```json
{
  "type": "start_chat",
  "prompt": "hello",
  "sessionId": "test-3",
  "topic": "invalid-topic"
}
```

**Expected:**
- ✅ Backend recognizes invalid topic
- ✅ Falls back to standard prompt (no context)
- ✅ Works normally
- ⚠️ Warning logged: "Invalid topic: invalid-topic"

---

### **Test 4: Context File Missing**

**Input:**
```json
{
  "type": "start_chat",
  "prompt": "test",
  "sessionId": "test-4",
  "topic": "math"
}
```

**If context file is missing:**

**Expected:**
- ✅ Backend tries to load context
- ✅ File not found
- ✅ Falls back to standard prompt
- ⚠️ Warning logged: "Context file not found: ..."

---

### **Test 5: All 10 Topics**

Test each topic:
1. `math` → simple-calculation.md
2. `random` → random-generation.md
3. `fetch` → data-fetch.md
4. `scheduled` → scheduled-task.md
5. `simple-api` → simple-api.md
6. `complex-api` → complex-api.md
7. `full-app` → full-application.md
8. `multi-service` → multi-service-integration.md
9. `transform` → data-transform.md
10. `chat` → conversation.md

**For Each:**
- ✅ Context loads successfully
- ✅ Agent uses correct context
- ✅ Response is appropriate

---

## 🔄 Rollback Plan

### **If Implementation Fails:**

**Step 1: Check Logs**
```bash
# Check backend logs
tail -f /path/to/backend/logs

# Look for errors in context loading
grep "Topic Loader" logs
grep "Error loading context" logs
```

**Step 2: Disable Topic Loading**
```python
# Quick fix: Always return empty context
def load_topic_context(topic_id: str, project_root: str) -> str:
    return ""  # Temporarily disable
```

**Step 3: Revert to Standard Prompt**
```python
# In WebSocket handler:
# enhanced_prompt = build_enhanced_prompt(prompt, topic_id, project_root)
enhanced_prompt = prompt  # Use original prompt
```

**Step 4: Frontend Still Works**
- Frontend sends topic
- Backend ignores it
- System works as before

---

## 📊 Success Criteria

### **Implementation is successful when:**

- [x] Backend extracts `topic` from WebSocket message
- [x] Context files are loaded correctly
- [x] Enhanced prompt is built with context
- [x] Claude receives enhanced prompt
- [x] Agent skips classification when topic provided
- [x] Agent responds faster
- [x] All 10 topics work correctly
- [x] Backward compatibility maintained (no topic = standard behavior)
- [x] Error handling works (invalid topic, missing file)
- [x] Logs show topic loading activity

---

## 🎯 Implementation Checklist

**Before Starting:**
- [ ] Locate WebSocket handler file
- [ ] Locate Claude CLI spawn location
- [ ] Verify Flow Architect context files exist
- [ ] Create backup of files to modify

**Implementation:**
- [ ] Create `topic_context_loader.py` utility file
- [ ] Add `TOPIC_CONTEXT_MAP` dictionary
- [ ] Implement `load_topic_context()` function
- [ ] Implement `build_enhanced_prompt()` function
- [ ] Modify WebSocket handler to extract topic
- [ ] Modify Claude CLI spawn to use enhanced prompt
- [ ] Add logging statements

**Testing:**
- [ ] Test with no topic (backward compatibility)
- [ ] Test with valid topic (new behavior)
- [ ] Test with invalid topic (error handling)
- [ ] Test all 10 topic categories
- [ ] Verify logs show correct behavior
- [ ] Compare response times (with/without topic)

**Deployment:**
- [ ] Code review
- [ ] Test in staging environment
- [ ] Deploy to production
- [ ] Monitor logs for errors
- [ ] Document changes

---

## 📚 Additional Notes

### **Performance Impact:**
- ✅ **Positive:** Faster responses (skip 2 steps)
- ✅ **Positive:** Better accuracy (correct context guaranteed)
- ⚠️ **Neutral:** Minimal overhead (single file read)

### **Backward Compatibility:**
- ✅ **Maintained:** Works without topic
- ✅ **Maintained:** Old sessions continue working
- ✅ **Maintained:** No breaking changes

### **Security Considerations:**
- ✅ Path traversal prevented (whitelist of files)
- ✅ No user input in file paths
- ✅ Context files are static/trusted

---

## 🚀 Next Steps

1. **Find WebSocket Handler:**
   ```bash
   grep -r "start_chat" components/apps/act-docker/
   ```

2. **Create `topic_context_loader.py`**

3. **Modify WebSocket Handler**

4. **Test with one topic** (e.g., "math")

5. **Test all topics**

6. **Deploy**

---

## ✅ Sign-Off

**Plan Status:** 🟢 **COMPLETE & READY**
**Implementation Status:** 🟡 **PENDING**
**Next Action:** Locate WebSocket handler and begin implementation

**This plan provides everything needed to implement topic-based context loading in the backend.**

**Ready to start implementation!** 🚀
