# Simple Calculation Context

## When to Load This

**Query Patterns:**
- "what's X + Y?"
- "calculate X * Y"
- "solve X - Y"
- "what is X / Y?"
- Math operations: +, -, *, /, %, **

**User Intent:**
- Single mathematical calculation
- No data storage needed
- No recurring execution
- Just want the answer

## Complexity Level: MINIMAL

**Flow Requirements:**
- 1 Python node only
- No database
- No server configuration
- No API endpoints
- Quick execution (temp file)

---

## Example Patterns

✅ **Matches:**
- "what's 47 + 89?"
- "calculate 15 * 23"
- "what's 100 / 4?"
- "solve 2^8" (or "2**8")
- "what is 25% of 200?"

❌ **Does NOT Match:**
- "calculate this every hour" → scheduled-task.md
- "create API for calculations" → simple-api.md
- "store calculation results" → needs database context

---

## Build Process (5 Steps)

### Step 1: Extract Values
Parse the user's query to get:
- Operation: +, -, *, /, %, **
- Operand 1: First number
- Operand 2: Second number

**Example:**
- Query: "what's 47 + 89?"
- Operand 1: 47
- Operand 2: 89
- Operation: +

### Step 2: Create Python Node

```toml
[workflow]
name = "Simple Calculation"
description = "Calculate [operation] of [operand1] and [operand2]"
start_node = Calculate

[node:Calculate]
type = "py"
label = "Perform calculation"
code = """
def calculate():
    result = [operand1] [operation] [operand2]
    return {"result": result}
"""
function = "calculate"
```

### Step 3: Save to Temp Location

**Path:** `flows/temp/calc-[timestamp].act`

**Example:** `flows/temp/calc-1729267890.act`

**Why temp?**
- One-time execution
- No need to persist
- Will be auto-cleaned

### Step 4: Execute via API

```bash
curl -X POST http://localhost:3000/api/act/execute \
  -H "Content-Type: application/json" \
  -d '{
    "flowContent": "[TOML content as string]",
    "flowName": "calc-[timestamp].act"
  }'
```

### Step 5: Parse Result & Respond

**Extract:**
```
response.result.results.Calculate.result.result
```

**Response Pattern:**
```
"**[number]**"
```

**Example:**
- User: "what's 47 + 89?"
- You: "**136**"

---

## Load Example

**Reference File:** `.claude/instructions/examples/simple-calc.act`

Read this file to see the exact structure.

---

## Node Types Needed

**Read:** `.claude/instructions/node-types/python.md`

**Key Parameters:**
- `code` (required): Python code as string
- `function` (required): Function name to execute
- `timeout_seconds` (optional): Default 60
- `retry_on_failure` (optional): Default false

---

## Response Pattern

### ✅ Correct

**User:** "what's 5 + 10?"
**You (internal):** Create flow → Execute → Parse result = 15
**You (to user):** "**15**"

**No explanation unless asked.**

### ❌ Wrong

**User:** "what's 5 + 10?"
**You:** "**15**" ← WITHOUT executing ACT flow

**This violates the CRITICAL RULE.**

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Answering Without Execution
```
User: "what's 47 + 89?"
You: "**136**"  ← You calculated it yourself
```

**Why wrong:** No ACT execution = no audit trail, breaks system architecture

**Fix:** ALWAYS create flow → execute → parse → respond

### ❌ Mistake 2: Over-Engineering
```toml
# DON'T add unnecessary sections
[configuration]  ← Not needed for simple calc
agent_enabled = true

[server]  ← Not needed for simple calc
port = 9001
```

**Why wrong:** Adds complexity, creates server unnecessarily

**Fix:** Keep it minimal (workflow + node only)

### ❌ Mistake 3: Creating API Endpoints
```toml
[node:DefineRoute]  ← Not needed for simple calc
type = "aci"
```

**Why wrong:** User just wants an answer, not an API

**Fix:** Only add API if explicitly requested

### ❌ Mistake 4: Adding Database Storage
```toml
[node:StoreResult]  ← Not needed for simple calc
type = "neon"
```

**Why wrong:** User doesn't need to store "47 + 89"

**Fix:** Only add persistence if explicitly needed

---

## Success Criteria

✅ **Requirements Met When:**

1. ACT flow was created
2. Flow was executed through `/api/act/execute`
3. Correct result was extracted from response
4. User sees just the answer (no technical details)
5. No server was created
6. No database was used
7. No API endpoints were defined
8. Temp file was used (not permanent .flow)

---

## Edge Cases

### Case 1: Division by Zero
**Query:** "what's 10 / 0?"

**Handle in Python:**
```python
def calculate():
    try:
        result = 10 / 0
        return {"result": result}
    except ZeroDivisionError:
        return {"result": "Error: Cannot divide by zero"}
```

**Response:** "Error: Cannot divide by zero"

### Case 2: Very Large Numbers
**Query:** "what's 999999999999 * 999999999999?"

**Python handles this fine.**

**Response:** "**999999999998000000000001**"

### Case 3: Float Precision
**Query:** "what's 0.1 + 0.2?"

**Result:** 0.30000000000000004 (Python float precision)

**Response:** "**0.30000000000000004**"

(User asked for calculation, give exact result)

---

## Complete Example Flow

**User Query:** "what's 47 + 89?"

**Internal Process:**

1. **Classify:** Simple calculation
2. **Load:** This context (simple-calculation.md)
3. **Extract:** operand1=47, operation=+, operand2=89
4. **Create Flow:**
```toml
[workflow]
name = "Calculate 47 + 89"
description = "Add 47 and 89"
start_node = Calculate

[node:Calculate]
type = "py"
label = "Perform addition"
code = """
def calculate():
    result = 47 + 89
    return {"result": result}
"""
function = "calculate"
```

5. **Execute:**
```bash
curl -X POST http://localhost:3000/api/act/execute \
  -H "Content-Type: application/json" \
  -d '{"flowContent": "...", "flowName": "calc-1729267890.act"}'
```

6. **Parse Response:**
```json
{
  "success": true,
  "result": {
    "results": {
      "Calculate": {
        "result": {
          "result": 136
        }
      }
    }
  }
}
```

7. **Extract:** 136

8. **Respond:** "**136**"

---

## Checklist Before Responding

- [ ] Did I create the ACT flow?
- [ ] Did I execute via `/api/act/execute`?
- [ ] Did I parse the actual result?
- [ ] Is my response just the number?
- [ ] Did I avoid creating a server?
- [ ] Did I avoid creating API endpoints?
- [ ] Did I avoid adding a database?
- [ ] Did I use a temp file path?

**If any checkbox is unchecked, DO NOT RESPOND YET.**

---

## Remember

**Simple calculations = Simple flows**

- 1 node
- No server
- No API
- No database
- Temp file
- Execute
- Parse
- Answer

**That's it.**
