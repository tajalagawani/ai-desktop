# Topic-Based Chat System - Backend Integration Guide

**Date:** October 21, 2025
**Status:** ✅ **FRONTEND COMPLETE** - Backend integration needed

---

## 📋 What Was Implemented (Frontend)

### 1. **Topic Selection Modal**
- File: `components/action-builder/TopicSelector.tsx`
- Shows 10 topic categories when user clicks "New Session"
- Uses Item UI component for clean presentation
- Topics match Flow Architect categories exactly

### 2. **Store Updates**
- File: `lib/action-builder/stores/chatStore.ts`
- Added `selectedTopic` state
- Added `showTopicSelector` modal control
- Updated `createNewSession()` to show topic selector
- Updated `sendMessage()` to include topic ID on first message

### 3. **WebSocket Updates**
- File: `lib/action-builder/websocket.ts`
- Added `topicId` parameter to `sendUserMessage()`
- Sends topic in WebSocket message: `{ type: 'start_chat', prompt, sessionId, topic }`

### 4. **Type Definitions**
- File: `types/index.ts`
- Added `topic` to Session interface
- Added `topic`, `prompt`, `resume` to WebSocketMessage interface

---

## 🎯 How It Works (User Flow)

1. **User clicks "New Session" button** (Plus icon in header)
2. **Topic selector modal appears** with 10 categories
3. **User selects a topic** (e.g., "📊 Math & Calculations")
4. **Modal closes**, topic is stored in `selectedTopic` state
5. **User types first message** in input area
6. **Message sent via WebSocket** with topic ID included
7. **Backend receives:** `{ type: 'start_chat', prompt: "what is 5+5", topic: "math" }`

---

## 🔧 Backend Integration Required

### **Location: Where Claude CLI is Spawned**

You need to find where the Action Builder backend:
1. Receives WebSocket messages
2. Extracts the user's prompt
3. Spawns the Claude CLI subprocess

This is likely in one of these files:
- `components/apps/act-docker/act/websocket_handler.py` (if exists)
- Backend WebSocket route handler
- Claude CLI spawn logic

---

## 📝 Backend Implementation Steps

### **Step 1: Extract Topic from WebSocket Message**

When receiving a `start_chat` message, extract the topic:

```python
# Example WebSocket handler
async def handle_start_chat(message_data):
    prompt = message_data.get('prompt', '')
    session_id = message_data.get('sessionId')
    topic_id = message_data.get('topic')  # NEW: Extract topic

    # ... rest of logic
```

---

### **Step 2: Load Context File Based on Topic**

Map topic ID to context file and load it:

```python
# Map topic IDs to context files
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

def load_topic_context(topic_id: str) -> str:
    """Load the context file for the selected topic."""
    if not topic_id or topic_id not in TOPIC_CONTEXT_MAP:
        return ""

    context_filename = TOPIC_CONTEXT_MAP[topic_id]
    context_path = f"/path/to/flow-architect/.claude/instructions/contexts/{context_filename}"

    try:
        with open(context_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"Context file not found: {context_path}")
        return ""
    except Exception as e:
        logger.error(f"Error loading context: {e}")
        return ""
```

---

### **Step 3: Build Enhanced Prompt with Context**

Inject the context before the user's prompt:

```python
async def handle_start_chat(message_data):
    prompt = message_data.get('prompt', '')
    topic_id = message_data.get('topic')

    # Load topic-specific context
    topic_context = load_topic_context(topic_id) if topic_id else ""

    # Build enhanced prompt
    if topic_context:
        enhanced_prompt = f"""# Topic Context Pre-loaded

The user selected the "{topic_id}" topic. Follow the instructions below for this type of request.

---

{topic_context}

---

# User Request

{prompt}
"""
    else:
        enhanced_prompt = prompt

    # Continue with spawning Claude CLI using enhanced_prompt
    await spawn_claude_cli(enhanced_prompt, session_id)
```

---

### **Step 4: Alternative - Modify Agent Instructions Dynamically**

Instead of modifying the prompt, you can modify the agent instructions:

```python
def build_agent_instructions(topic_id: str) -> str:
    """Build agent instructions with topic context pre-loaded."""

    # Load base Flow Architect agent
    base_agent_path = "/path/to/flow-architect/.claude/agents/flow-architect.md"
    with open(base_agent_path, 'r') as f:
        base_agent = f.read()

    # Load topic context if provided
    topic_context = load_topic_context(topic_id) if topic_id else ""

    if topic_context:
        # Inject context after philosophy section
        enhanced_agent = f"""{base_agent}

---

## 🎯 Pre-loaded Topic Context

The user selected a specific topic. The relevant context has been loaded below:

{topic_context}

**Follow the instructions above for this request.**

---
"""
        return enhanced_agent
    else:
        return base_agent

# When spawning Claude CLI:
agent_instructions = build_agent_instructions(topic_id)
# Pass agent_instructions to Claude CLI
```

---

## 🎯 Expected Behavior After Integration

### **Without Topic (Old Behavior):**
```
User: "what is 5+5"
  ↓
Agent reads flow-architect.md
  ↓
Agent classifies as "Simple Calculation"
  ↓
Agent reads simple-calculation.md
  ↓
Agent creates ACT flow
  ↓
Returns: "10"
```

### **With Topic (New Behavior):**
```
User selects: "📊 Math & Calculations"
User: "what is 5+5"
  ↓
Backend receives topic: "math"
  ↓
Backend loads simple-calculation.md
  ↓
Backend injects context into prompt/agent
  ↓
Agent SKIPS classification (context already loaded)
  ↓
Agent creates ACT flow directly
  ↓
Returns: "10"
```

**Benefits:**
- ✅ Agent skips Step 1 (Classification)
- ✅ Agent skips Step 2 (Load Context)
- ✅ Faster responses (2 fewer steps)
- ✅ More accurate (context is exactly what user intended)

---

## 📁 Files Modified (Frontend)

```
✅ components/action-builder/TopicSelector.tsx (NEW)
✅ components/action-builder/ui/item.tsx (NEW)
✅ components/action-builder/ChatInterface.tsx (MODIFIED)
✅ lib/action-builder/stores/chatStore.ts (MODIFIED)
✅ lib/action-builder/websocket.ts (MODIFIED)
✅ types/index.ts (MODIFIED)
```

---

## 🔍 Testing the Frontend

1. **Start the Action Builder**
2. **Click "New Session" button** (Plus icon)
3. **Verify modal appears** with 10 topics
4. **Select a topic** (e.g., "Math & Calculations")
5. **Modal closes**
6. **Type a message:** "what is 2+2"
7. **Check browser console:**
   ```
   [WebSocket Client] sendUserMessage called
   [WebSocket Client]   - Content: what is 2+2
   [WebSocket Client]   - Topic ID: math
   ```
8. **Check backend logs** to see if topic is received

---

## 🎨 UI Component Details

### **Item Component** (used for topics)
- Path: `components/action-builder/ui/item.tsx`
- Variants: `default`, `outline`, `ghost`
- Sizes: `sm`, `default`, `lg`
- Parts: `ItemMedia`, `ItemContent`, `ItemTitle`, `ItemDescription`, `ItemActions`

### **Topic Structure:**
```typescript
{
  id: 'math',
  icon: '📊',
  name: 'Math & Calculations',
  context: 'simple-calculation.md',
  description: 'Simple calculations and math operations',
  example: '"what is 5+5", "calculate 25% of 200"'
}
```

---

## 🚀 Next Steps

1. **Find WebSocket handler** in backend (where `start_chat` is received)
2. **Extract `topic` field** from message
3. **Load context file** using `TOPIC_CONTEXT_MAP`
4. **Inject context** into prompt or agent instructions
5. **Test with different topics** to verify behavior

---

## 📊 Topic ID → Context File Mapping

| Topic ID | Context File | Category |
|----------|-------------|----------|
| `math` | `simple-calculation.md` | Simple Calculation |
| `random` | `random-generation.md` | Random Generation |
| `fetch` | `data-fetch.md` | Data Fetch |
| `scheduled` | `scheduled-task.md` | Scheduled Tasks |
| `simple-api` | `simple-api.md` | Simple API (2-5 endpoints) |
| `complex-api` | `complex-api.md` | Complex API (6-15 endpoints) |
| `full-app` | `full-application.md` | Full Application (30+ endpoints) |
| `multi-service` | `multi-service-integration.md` | Multi-Service Integration |
| `transform` | `data-transform.md` | Data Transform |
| `chat` | `conversation.md` | Conversation |

---

## ✅ Sign-Off

**Frontend Implementation:** 🟢 COMPLETE
**Backend Integration:** 🟡 PENDING
**Testing:** 🟡 PENDING (after backend integration)

**All frontend files ready. Backend needs to:**
1. Extract `topic` from WebSocket message
2. Load corresponding context file
3. Inject context into agent prompt/instructions

**Ready for backend integration!** 🚀
