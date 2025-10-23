# Random Generation Context

## When to Load This

**Query Patterns:**
- "pick random"
- "random number"
- "generate random"
- "give me a random number"
- "random between X and Y"

**User Intent:**
- Generate a random number
- Within a specified range (or default 1-100)
- No storage needed
- One-time generation

## Complexity Level: MINIMAL

**Flow Requirements:**
- 1 Python node with `random.randint()`
- No database
- No server configuration
- No API endpoints
- Quick execution (temp file)

---

## Example Patterns

✅ **Matches:**
- "pick a random number between 1 and 50"
- "generate random number from 1-100"
- "give me a random number"
- "random between 5 and 20"

❌ **Does NOT Match:**
- "generate random number every 10 minutes" → scheduled-task.md
- "create API to get random numbers" → simple-api.md
- "store random numbers" → needs database

---

## Build Process (5 Steps)

### Step 1: Extract Range

**Parse the query to get:**
- Min value (default: 1)
- Max value (default: 100)

**Examples:**
- "pick random between 1 and 50" → min=1, max=50
- "random number from 5-20" → min=5, max=20
- "give me a random number" → min=1, max=100 (default)

### Step 2: Create Python Node with random.randint()

```toml
[workflow]
name = "Random Number Generator"
description = "Generate random number between [min] and [max]"
start_node = Generate

[node:Generate]
type = "py"
label = "Generate random number"
code = """
import random

def generate():
    number = random.randint([min], [max])
    return {"result": number}
"""
function = "generate"
```

**Key Points:**
- Must import `random` module
- Use `random.randint(min, max)` (inclusive on both ends)
- Return `{"result": number}`

### Step 3: Save to Temp Location

**Path:** `flows/temp/random-[timestamp].act`

**Example:** `flows/temp/random-1729267890.act`

### Step 4: Execute via API

```bash
curl -X MCP execute_node_operation \
  -H "Content-Type: application/json" \
  -d '{
    "flowContent": "[TOML content as string]",
    "flowName": "random-[timestamp].act"
  }'
```

### Step 5: Parse Result & Respond

**Extract:**
```
response.result.results.Generate.result.result
```

**Response Pattern:**
```
"🎲 **[number]**"
```

**Example:**
- User: "pick a random number between 1 and 50"
- You: "🎲 **27**"

---

## Load Example

**Reference File:** `.claude/instructions/examples/random-number.act`

Read this file to see the exact structure.

---

## Node Types Needed

**Read:** `.claude/instructions/node-types/python.md`

**Key Info:**
- Python standard library is available (includes `random`)
- No need to install packages
- Use `import random` at the top of code

---

## Response Pattern

### ✅ Correct

**User:** "pick a random number between 1 and 50"
**You (internal):** Create flow → Execute → Parse result = 27
**You (to user):** "🎲 **27**"

**Include the dice emoji (🎲) for random numbers.**

### ❌ Wrong

**User:** "pick a random number between 1 and 50"
**You:** "🎲 **27**" ← WITHOUT executing ACT flow

**This violates the CRITICAL RULE.**

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Using a Hardcoded Number
```python
def generate():
    return {"result": 27}  # ❌ Not random!
```

**Why wrong:** Result isn't actually random

**Fix:** Always use `random.randint(min, max)`

### ❌ Mistake 2: Not Importing random
```python
def generate():
    number = random.randint(1, 50)  # ❌ random not imported
    return {"result": number}
```

**Why wrong:** Code will fail with NameError

**Fix:** Add `import random` at the top

### ❌ Mistake 3: Wrong Range Method
```python
import random

def generate():
    number = random.random() * 50  # ❌ Returns float
    return {"result": number}
```

**Why wrong:** Returns float (0.0-50.0), not integer (1-50)

**Fix:** Use `random.randint(1, 50)` for integers

### ❌ Mistake 4: Off-by-One Range Error
```python
import random

def generate():
    number = random.randrange(1, 50)  # ❌ Excludes 50
    return {"result": number}
```

**Why wrong:** `randrange(1, 50)` gives 1-49, not 1-50

**Fix:** Use `randint(1, 50)` which is inclusive on both ends

---

## Success Criteria

✅ **Requirements Met When:**

1. ACT flow was created
2. Flow was executed through `MCP execute_node_operation`
3. Result is truly random (uses `random.randint()`)
4. Result is within specified range
5. User sees just the number with dice emoji
6. No server was created
7. No database was used
8. No API endpoints were defined
9. Temp file was used

---

## Edge Cases

### Case 1: Same Min and Max
**Query:** "random number between 5 and 5"

**Python handles this:**
```python
random.randint(5, 5)  # Always returns 5
```

**Response:** "🎲 **5**"

### Case 2: Min Greater Than Max
**Query:** "random between 50 and 1"

**Fix in code:**
```python
import random

def generate():
    min_val = 50
    max_val = 1
    # Swap if min > max
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    number = random.randint(min_val, max_val)
    return {"result": number}
```

**Response:** "🎲 **[number between 1-50]**"

### Case 3: No Range Specified
**Query:** "give me a random number"

**Default range:** 1-100

```python
import random

def generate():
    number = random.randint(1, 100)
    return {"result": number}
```

**Response:** "🎲 **[number between 1-100]**"

---

## Complete Example Flow

**User Query:** "pick a random number between 1 and 50"

**Internal Process:**

1. **Classify:** Random generation
2. **Load:** This context (random-generation.md)
3. **Extract:** min=1, max=50
4. **Create Flow:**
```toml
[workflow]
name = "Random Number Generator"
description = "Generate random number between 1 and 50"
start_node = Generate

[node:Generate]
type = "py"
label = "Generate random number"
code = """
import random

def generate():
    number = random.randint(1, 50)
    return {"result": number}
"""
function = "generate"
```

5. **Execute:**
```bash
curl -X MCP execute_node_operation \
  -H "Content-Type: application/json" \
  -d '{"flowContent": "...", "flowName": "random-1729267890.act"}'
```

6. **Parse Response:**
```json
{
  "success": true,
  "result": {
    "results": {
      "Generate": {
        "result": {
          "result": 27
        }
      }
    }
  }
}
```

7. **Extract:** 27

8. **Respond:** "🎲 **27**"

---

## Variations

### Variation 1: Multiple Random Numbers
**Query:** "give me 3 random numbers between 1 and 100"

**Modified code:**
```python
import random

def generate():
    numbers = [random.randint(1, 100) for _ in range(3)]
    return {"result": numbers}
```

**Response:** "🎲 **[42, 7, 83]**"

### Variation 2: Random Float
**Query:** "random decimal between 0 and 1"

**Modified code:**
```python
import random

def generate():
    number = random.random()
    return {"result": number}
```

**Response:** "🎲 **0.7234567**"

---

## Checklist Before Responding

- [ ] Did I create the ACT flow?
- [ ] Did I use `random.randint()`?
- [ ] Did I import random module?
- [ ] Did I execute via `MCP execute_node_operation`?
- [ ] Did I parse the actual result?
- [ ] Is the number within the specified range?
- [ ] Did I include the dice emoji (🎲)?
- [ ] Did I avoid creating a server?
- [ ] Did I avoid creating API endpoints?
- [ ] Did I use a temp file path?

**If any checkbox is unchecked, DO NOT RESPOND YET.**

---

## Remember

**Random generation = Simple Python flow with random.randint()**

- Import random
- Use randint(min, max)
- Execute through ACT
- Return with dice emoji 🎲
- Keep it minimal

**That's it.**
