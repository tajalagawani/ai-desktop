# Data Transformation Context

## When to Load This

**Query Patterns:**
- "process [data] and convert to [format]"
- "transform [input] into [output]"
- "parse [file/data] and extract [information]"
- "analyze [data] and calculate [metrics]"
- "clean [data] and remove [issues]"
- "merge [data1] and [data2]"
- User wants to process/transform data
- Focus on computation, not storage or APIs

**User Intent:**
- Data processing
- Format conversion
- Data cleaning/validation
- Calculations and analysis
- Aggregations and summaries
- Data enrichment
- One-time or repeated processing

## Complexity Level: MINIMAL to MEDIUM

**Flow Requirements:**
- Python nodes (processing logic)
- Optional: Input nodes (read data)
- Optional: Output nodes (write results)
- Optional: Database nodes (if storing results)
- Usually: Temp .act file (unless repeated)
- No server (unless exposing as API)
- No external API calls (unless data enrichment)

---

## Example Patterns

✅ **Matches:**
- "convert this CSV to JSON"
- "parse this log file and extract errors"
- "calculate average, min, max from these numbers"
- "clean this data and remove duplicates"
- "merge user data with order data"
- "analyze text and count word frequency"
- "validate email addresses in this list"

❌ **Does NOT Match:**
- "fetch weather data" → data-fetch-once.md (external API)
- "create API to process data" → simple-api.md (needs server)
- "process data every hour" → scheduled-task.md (recurring)

---

## Build Process (7 Steps)

### Step 1: Identify Input Source

**Where does the data come from?**
- **Direct input:** User provides data in request
- **File:** Read from uploaded file
- **Database:** Query existing data
- **HTTP:** Fetch from URL
- **Previous node:** Output from another operation

### Step 2: Identify Transformation Logic

**What processing is needed?**

**Common operations:**
- **Format conversion:** CSV ↔ JSON ↔ XML ↔ YAML
- **Data cleaning:** Remove nulls, trim whitespace, deduplicate
- **Validation:** Check formats, ranges, required fields
- **Extraction:** Parse structured data (logs, HTML, etc.)
- **Calculation:** Sum, average, min, max, percentiles
- **Aggregation:** Group by, count, summarize
- **Enrichment:** Add derived fields, lookup values
- **Filtering:** Remove unwanted records
- **Sorting:** Order by criteria
- **Merging:** Combine multiple datasets

### Step 3: Identify Output Destination

**Where should results go?**
- **Return to user:** Display result
- **File:** Write to file
- **Database:** Store in table
- **HTTP:** POST to API
- **Email:** Send as attachment

### Step 4: Design Data Flow

**Pattern:**
```
[Input] → [Transform] → [Output]
```

**Examples:**
```
Read CSV → Parse → Convert to JSON → Return

Fetch Data → Clean → Validate → Calculate Stats → Return

Read Log File → Extract Errors → Filter by Date → Store in DB
```

### Step 5: Create Python Processing Node

```toml
[workflow]
name = "[Transformation] Processor"
description = "[What it does]"
start_node = ProcessData

[node:ProcessData]
type = "py"
label = "[Processing description]"
code = """
import json
import csv
from datetime import datetime

def process(**kwargs):
    # Get input data
    input_data = kwargs.get('request_data', {}).get('data', [])

    # Transform logic
    results = []
    for item in input_data:
        transformed = {
            'field1': item.get('old_field1'),
            'field2': process_field(item.get('old_field2')),
            'calculated': item['a'] + item['b']
        }
        results.append(transformed)

    # Return results
    return {"result": results}

def process_field(value):
    # Helper function
    return value.strip().upper()
"""
function = "process"
```

### Step 6: Add Input/Output Nodes (If Needed)

**Reading from database:**
```toml
[node:ReadData]
type = "neon"
query = "SELECT * FROM raw_data"

[node:ProcessData]
type = "py"
code = """
def process(**kwargs):
    data = kwargs.get('ReadData', {}).get('result', [])
    # Process data
    ...
"""

[edges]
ReadData = ProcessData
```

**Writing to database:**
```toml
[node:StoreResults]
type = "neon"
query = "INSERT INTO processed_data (field1, field2) VALUES (%s, %s)"
parameters = ["{{ProcessData.result.field1}}", "{{ProcessData.result.field2}}"]

[edges]
ProcessData = StoreResults
```

### Step 7: Execute and Return

**For one-time transformation:**
- Save as temp .act file
- Execute via `/api/act/execute`
- Return processed result

**For repeated transformation:**
- Add timer node (scheduled)
- Save as permanent .flow
- Register in service catalog

---

## Common Transformation Patterns

### Pattern 1: CSV to JSON

```toml
[node:ConvertCSVtoJSON]
type = "py"
code = """
import csv
import json

def convert(**kwargs):
    csv_data = kwargs.get('request_data', {}).get('csv', '')

    # Parse CSV
    lines = csv_data.strip().split('\\n')
    reader = csv.DictReader(lines)

    # Convert to JSON
    results = [row for row in reader]

    return {"result": results}
"""
function = "convert"
```

### Pattern 2: Data Cleaning

```toml
[node:CleanData]
type = "py"
code = """
def clean(**kwargs):
    data = kwargs.get('request_data', {}).get('data', [])

    cleaned = []
    seen = set()

    for item in data:
        # Remove nulls
        if not item:
            continue

        # Trim whitespace
        if isinstance(item, str):
            item = item.strip()

        # Remove duplicates
        if item in seen:
            continue
        seen.add(item)

        cleaned.append(item)

    return {"result": cleaned}
"""
function = "clean"
```

### Pattern 3: Statistical Analysis

```toml
[node:CalculateStats]
type = "py"
code = """
def calculate(**kwargs):
    numbers = kwargs.get('request_data', {}).get('numbers', [])

    if not numbers:
        return {"error": "No numbers provided"}

    return {
        "result": {
            "count": len(numbers),
            "sum": sum(numbers),
            "average": sum(numbers) / len(numbers),
            "min": min(numbers),
            "max": max(numbers),
            "range": max(numbers) - min(numbers)
        }
    }
"""
function = "calculate"
```

### Pattern 4: Log Parsing

```toml
[node:ParseLogs]
type = "py"
code = """
import re

def parse_logs(**kwargs):
    log_text = kwargs.get('request_data', {}).get('log', '')

    # Regex to match error lines
    error_pattern = r'\\[(ERROR|FATAL)\\]\\s+(.+)'

    errors = []
    for line in log_text.split('\\n'):
        match = re.search(error_pattern, line)
        if match:
            errors.append({
                'level': match.group(1),
                'message': match.group(2)
            })

    return {"result": {"errors": errors, "count": len(errors)}}
"""
function = "parse_logs"
```

### Pattern 5: Data Validation

```toml
[node:ValidateData]
type = "py"
code = """
import re

def validate(**kwargs):
    data = kwargs.get('request_data', {}).get('users', [])

    valid = []
    invalid = []

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'

    for user in data:
        errors = []

        # Validate email
        if not re.match(email_pattern, user.get('email', '')):
            errors.append('Invalid email format')

        # Validate age
        age = user.get('age', 0)
        if age < 18 or age > 120:
            errors.append('Invalid age')

        if errors:
            invalid.append({'user': user, 'errors': errors})
        else:
            valid.append(user)

    return {
        "result": {
            "valid": valid,
            "invalid": invalid,
            "valid_count": len(valid),
            "invalid_count": len(invalid)
        }
    }
"""
function = "validate"
```

### Pattern 6: Data Merging

```toml
[node:MergeData]
type = "py"
code = """
def merge(**kwargs):
    users = kwargs.get('request_data', {}).get('users', [])
    orders = kwargs.get('request_data', {}).get('orders', [])

    # Create lookup dict
    user_lookup = {user['id']: user for user in users}

    # Merge orders with user data
    merged = []
    for order in orders:
        user_id = order.get('user_id')
        user = user_lookup.get(user_id, {})

        merged.append({
            **order,
            'user_name': user.get('name'),
            'user_email': user.get('email')
        })

    return {"result": merged}
"""
function = "merge"
```

---

## Response Pattern

### Simple Transformation

**User:** "convert this CSV to JSON: [data]"

**Internal:**
1. Create Python node with CSV parsing
2. Execute transformation
3. Return JSON result

**Response:**
```json
{
  "result": [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
  ]
}
```

### Data Analysis

**User:** "calculate stats for these numbers: [1, 5, 3, 9, 2]"

**Response:**
```
"📊 **Statistics**

Count: 5
Sum: 20
Average: 4.0
Min: 1
Max: 9
Range: 8"
```

### Data Validation

**User:** "validate these email addresses: [list]"

**Response:**
```
"✓ **Validation Results**

Valid: 8 addresses
Invalid: 2 addresses

**Invalid:**
• john@invalid - Invalid domain
• @missing.com - Missing username"
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Not Handling Edge Cases

```python
def process(**kwargs):
    data = kwargs['data']  # ❌ KeyError if missing
    result = sum(data) / len(data)  # ❌ ZeroDivisionError if empty
```

**Fix:**
```python
def process(**kwargs):
    data = kwargs.get('request_data', {}).get('data', [])
    if not data:
        return {"error": "No data provided"}
    result = sum(data) / len(data)
```

### ❌ Mistake 2: Memory Issues with Large Data

```python
# Load entire 1GB file into memory ❌
all_data = read_entire_file()
```

**Fix:** Use streaming/chunking for large datasets

### ❌ Mistake 3: Not Returning Result

```python
def process(**kwargs):
    result = transform_data(kwargs['data'])
    # ❌ Missing return statement
```

**Fix:**
```python
return {"result": result}
```

### ❌ Mistake 4: Modifying Input Data

```python
def process(**kwargs):
    data = kwargs.get('data')
    data.sort()  # ❌ Mutates input
```

**Fix:**
```python
data = kwargs.get('data', [])
sorted_data = sorted(data)  # ✅ Creates copy
```

---

## Success Criteria

✅ **Requirements Met When:**

1. Input source identified
2. Transformation logic implemented
3. Edge cases handled
4. Data validated
5. Results formatted
6. Temp .act file (if one-time)
7. ACT execution completed
8. Result returned to user

---

## Checklist Before Responding

- [ ] Did I identify input source?
- [ ] Did I identify transformation logic?
- [ ] Did I create Python processing node?
- [ ] Did I handle edge cases (empty data, nulls)?
- [ ] Did I validate input data?
- [ ] Did I return result correctly?
- [ ] Did I save as temp .act (if one-time)?
- [ ] Did I execute via API?
- [ ] Did I parse result?
- [ ] Did I format response appropriately?

**If any checkbox is unchecked, DO NOT RESPOND YET.**

---

## Remember

**Data Transformation = Input → Process → Output**

- Python for logic
- Handle edge cases
- Validate data
- Format output
- Usually temp execution
- Return processed result

**That's it.**
