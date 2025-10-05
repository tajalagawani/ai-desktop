# UTA Flow Creation Guide

## Overview

This comprehensive guide covers the rules, patterns, and best practices for creating new flows in the Universal Task Agent (UTA) system. Based on analysis of existing flows and the core parser/execution engine, this document provides all necessary information to create robust, maintainable workflows.

## Table of Contents

1. [Flow File Structure](#flow-file-structure)
2. [Required Sections](#required-sections)
3. [Parser Rules and Validation](#parser-rules-and-validation)
4. [Node Types and Patterns](#node-types-and-patterns)
5. [Advanced Placeholder System](#advanced-placeholder-system)
6. [Parameter System](#parameter-system)
7. [Data Flow and References](#data-flow-and-references)
8. [Database Operations](#database-operations)
9. [API Route Definitions](#api-route-definitions)
10. [AI Integration](#ai-integration)
11. [Execution Engine Constraints](#execution-engine-constraints)
12. [Error Handling and Validation](#error-handling-and-validation)
13. [Performance and Optimization](#performance-and-optimization)
14. [Flow Examples by Category](#flow-examples-by-category)
15. [Common Patterns and Templates](#common-patterns-and-templates)this m
16. [Best Practices](#best-practices)
17. [Troubleshooting](#troubleshooting)

---

## Flow File Structure

### Basic TOML Structure
```toml
# =====================================================
# Flow Title and Description
# =====================================================
[workflow]
name = "Flow Name"
description = "Clear description of what this flow does"
start_node = FirstNodeName

[parameters]
# Global parameters accessible throughout the flow
param_name = value

# =============================================
# Node Definitions
# =============================================

[node:NodeName]
type = node_type
label = "Human-readable description"
# ... node-specific parameters

# =============================================
# Edges: Defining the Flow
# =============================================
[edges]
NodeA = NodeB
NodeB = NodeC

# =============================================
# Environment Variables
# =============================================
[env]
API_KEY_NAME

# =============================================
# Configuration Settings
# =============================================
[settings]
debug_mode = true
max_retries = 3
timeout_seconds = 300

[configuration]
agent_enabled = true
agent_name = "AgentName"
host = "0.0.0.0"
port = 8081
```

---

## Required Sections

### 1. Workflow Section (MANDATORY)
```toml
[workflow]
name = "Descriptive Flow Name"
description = "What this flow accomplishes"
start_node = StartingNodeName
```

**Rules:**
- `name`: Must be unique and descriptive
- `description`: Should explain the flow's purpose and scope
- `start_node`: Must match an existing node name exactly

### 2. Parameters Section (RECOMMENDED)
```toml
[parameters]
connection_string = "database_connection_url"
api_endpoint = "https://api.example.com"
batch_size = 1000
```

**Rules:**
- Use for values that might change between environments
- Reference with `{{.Parameter.param_name}}`
- Keep sensitive data in environment variables, not parameters

### 3. Environment Variables Section (AS NEEDED)
```toml
[env]
DATABASE_PASSWORD
API_KEY
SECRET_TOKEN
```

**Rules:**
- List only the variable names (no values)
- Reference with `${VAR_NAME}` syntax
- Use for sensitive information

---

## Parser Rules and Validation

### Supported Sections
The parser recognizes these sections (from `actfile_parser.py:502-505`):
```toml
SUPPORTED_SECTIONS = [
    'workflow', 'parameters', 'nodes', 'edges',
    'dependencies', 'env', 'settings', 'configuration', 'deployment'
]
```

### Critical Validation Rules

#### 1. Workflow Section Validation
- **MANDATORY**: `start_node` must be present
- **MANDATORY**: `start_node` must reference an existing node
- `name` is recommended but not required
```toml
[workflow]
name = "Required for clarity"
start_node = MustExistInNodes  # Critical validation check
```

#### 2. Node Definition Requirements
- Every node **MUST** have a `type` field
- Node names must be valid identifiers
- Circular references in edges will cause execution errors

#### 3. Edge Validation
- All source nodes in edges must exist in `[nodes]`
- All target nodes in edges must exist in `[nodes]`
- Edges define execution flow and are strictly validated

#### 4. Section Parsing Rules
```toml
# Comments using # or ; are supported
[section]  # Comments allowed after section headers
key = value  # Comments allowed after values

# Multiline code blocks supported with triple quotes
code = """
Multi-line content
preserved exactly
"""

# JSON structures parsed automatically
data = {"key": "value", "list": [1, 2, 3]}

# File references supported for Python code
path = "relative/path/to/script.py"  # Will load file content
```

---

## Node Types and Patterns

### Core Node Types

#### 1. Python Execution Nodes
```toml
[node:NodeName]
type = py
label = "Description of what this Python code does"
code = """
def function_name():
    # Python code here
    return {'result': value}
"""
function = function_name
```

**Rules:**
- Function must return a dictionary
- Use `{{NodeName.result.result.key}}` to access returned values
- Keep code focused and single-purpose

#### 2. Database Nodes (Neon/PostgreSQL)
```toml
[node:NodeName]
type = neon
label = "Database operation description"
connection_string = {{.Parameter.connection_string}}
operation = execute_query  # or create_schema
query = "SELECT * FROM table WHERE condition = %s"
parameters = ["{{previous_node.result.value}}"]
```

**Operations:**
- `execute_query`: Run SQL queries
- `create_schema`: Create database schema

#### 3. API Route Definition Nodes
```toml
[node:NodeName]
type = aci
mode = server
label = "API endpoint description"
operation = add_route
route_path = /api/resource/<int:id>
methods = ["GET", "POST"]
handler = HandlerName
description = "Endpoint description"
```

**Rules:**
- Always include `mode = server` for API routes
- Use descriptive handler names
- Support standard HTTP methods

#### 4. AI/LLM Nodes
```toml
[node:NodeName]
type = claude  # or gemini
label = "AI task description"
api_key = "${API_KEY}"
model = "claude-3-5-sonnet-20240620"
temperature = 0.2
max_tokens = 2000
messages = [
  {
    "role": "user", 
    "content": "AI prompt with {{dynamic.data}}"
  }
]
```

**Supported AI Types:**
- `claude`: Anthropic Claude models
- `gemini`: Google Gemini models

#### 5. Special Node Types

**Conditional Nodes:**
```toml
# If Node - Boolean branching
[node:CheckCondition]
type = if
# Result must return {'result': boolean}
# First edge = true path, second edge = false path

# Switch Node - Multi-way branching  
[node:RouteToDestination]
type = switch
# Result must return {'selected_node': 'target_node_name'}
```

**Set Node - Store Values:**
```toml
[node:StoreValue]
type = set
# Result: {'key': 'storage_key', 'value': any_value}
# Accessible later via {{key:storage_key}}
```

#### 6. Utility Nodes
```toml
# UUID Generation
[node:NodeName]
type = generate_uuid
label = "Generate unique identifier"
hyphens = true  # or false

# Logging
[node:NodeName]
type = log_message
label = "Log important information"
level = info  # debug, info, warn, error
message = "Status: {{previous_node.result}}"

# Data Transformation
[node:NodeName]
type = data
label = "Prepare data for next step"
field_name = "{{source_node.result.value}}"
```

---

## Advanced Placeholder System

### Overview
The UTA system includes a sophisticated placeholder resolution engine supporting dot notation, filters, conditionals, loops, and caching. Understanding this system is crucial for effective flow creation.

### Placeholder Types

#### 1. Environment Variables
```toml
# Environment variable resolution
api_key = "${API_KEY}"
database_url = "${DATABASE_URL}"

# Fallback to empty string if not found
connection = "${DB_HOST}" # Resolves at parse time
```

#### 2. Parameter References
```toml
[parameters]
base_url = "https://api.example.com"
max_retries = 3

[node:ApiCall]
endpoint = "{{.Parameter.base_url}}/data"
retries = {{.Parameter.max_retries}}
```

#### 3. Node Result References
```toml
# Basic dot notation
user_id = "{{UserLogin.result.user_id}}"

# Array access with indices
first_item = "{{DataFetch.result.items.0.name}}"

# Deep nesting
nested_data = "{{ProcessData.result.analysis.summary.conclusion}}"
```

#### 4. Input Data References
```toml
# Access initial workflow input data
user_input = "{{input.user_name}}"
request_id = "{{input.request_metadata.id}}"
```

#### 5. Set Node References (Key-Based Storage)
```toml
[node:StoreConfig]
type = set
# This stores value with key 'app_config'

[node:UseConfig]
type = py
config_data = "{{key:app_config}}"  # Retrieves stored value
```

### Advanced Placeholder Features

#### 1. Filter Chain System
```toml
# String manipulation
title = "{{article.title|upper|truncate(50)}}"
tags = "{{article.tags|join(' | ')}}"

# Numeric operations
average = "{{scores|sum|divide({{scores|length}})}}"
rounded = "{{price|round(2)}}"

# Array operations
sorted_items = "{{items|sort|reverse}}"
unique_tags = "{{all_tags|unique|join(', ')}}"

# Type conversions
count_str = "{{item_count|str}}"
is_valid = "{{validation_result|bool}}"
data_json = "{{results|json}}"
```

**Available Filters:**
- **String**: `upper`, `lower`, `capitalize`, `strip`, `truncate(n)`
- **Array**: `join(sep)`, `first`, `last`, `sort`, `reverse`, `unique`, `length`
- **Numeric**: `round(digits)`, `abs`, `sum`, `max`, `min`
- **Type**: `int`, `float`, `str`, `bool`, `json`
- **Logic**: `default(fallback)`, `length`, `len`

#### 2. Conditional Expressions
```toml
# Ternary conditional
status = "{{order.paid if order.total > 0 else 'free'}}"

# Complex conditions
message = "{{success_msg if result.status == 'ok' else error_msg}}"
```

#### 3. Template Blocks

**Conditional Blocks:**
```toml
prompt = """
Process this data: {{data.name}}
{{#if data.priority > 5}}
HIGH PRIORITY: Immediate attention required!
{{else}}
Standard processing workflow.
{{/if}}

Status: {{data.status}}
"""
```

**Loop Blocks:**
```toml
report = """
Summary of items:
{{#each items}}
- Item {{index}}: {{this.name}} ({{this.status}})
{{/each}}

Total items: {{items|length}}
"""
```

**Loop Context Variables:**
- `{{this}}` - Current item
- `{{index}}` - Zero-based index
- `{{first}}` - True if first item
- `{{last}}` - True if last item
- `{{length}}` - Total array length

#### 4. Fallback Values
```toml
# Simple fallback
name = "{{user.name | 'Anonymous'}}"

# Complex fallback
config = "{{remote_config.settings | local_config | {\"default\": true}}}"

# Multiple fallback levels
endpoint = "{{custom_endpoint | default_endpoint | 'http://localhost:8080'}}"
```

### Path Resolution Strategies

The system uses multiple strategies to resolve paths (from `execution_manager.py:1340-1408`):

#### Strategy 1: Direct Path Resolution
```toml
# Direct access to nested data
value = "{{NodeName.result.data.field}}"
```

#### Strategy 2: Skip 'result' Wrapper
```toml
# If path fails, tries without 'result' prefix
# {{NodeName.result.field}} → {{NodeName.field}}
```

#### Strategy 3: Add 'result' Prefix
```toml
# If path fails, tries with 'result' prefix
# {{NodeName.field}} → {{NodeName.result.field}}
```

#### Strategy 4: Direct Result Field Access
```toml
# For PyNode results, direct field access
# Handles nested result structures automatically
```

### Placeholder Resolution Caching

The system includes advanced caching to prevent redundant resolution:

```toml
# Cache hit example - resolved once, reused everywhere
base_url = "{{config.api.base_url}}"  # Resolved and cached
endpoint1 = "{{config.api.base_url}}/users"  # Cache hit
endpoint2 = "{{config.api.base_url}}/orders"  # Cache hit
```

### Circular Reference Detection

The parser detects and prevents infinite loops:
```toml
# This would cause an error - circular reference
[node:A]
value = "{{B.result}}"

[node:B] 
value = "{{A.result}}"  # Circular reference detected!
```

### Debug Mode

Enable detailed placeholder resolution logging:
```toml
[settings]
resolution_debug_mode = true  # Shows detailed resolution steps
fail_on_unresolved = false    # Continue on unresolved placeholders
```

### Complex Examples

#### Multi-Strategy Resolution
```toml
[node:DataProcessor]
type = py
# These all work due to multiple resolution strategies
direct_access = "{{DataFetch.result.items.0.name}}"
wrapper_skip = "{{DataFetch.items.0.name}}"  # Skips 'result' wrapper
auto_prefix = "{{DataFetch.items}}"  # Adds 'result' prefix if needed
```

#### Advanced Filter Chains
```toml
[node:ReportGenerator]
type = gemini
prompt = """
Analysis Report:

Top Users: {{users|sort(by='score')|reverse|first(5)|join(', ')}}
Average Score: {{users|map('score')|sum|divide({{users|length}})|round(2)}}
Status Summary: {{#each statuses|unique}}{{this}}: {{parent|filter(status=this)|length}}{{/each}}
"""
```

#### Conditional Template Logic
```toml
[node:EmailTemplate]
type = py  
template = """
Hello {{user.name|default('Valued Customer')}},

{{#if order.total > 100}}
🎉 Thank you for your premium order!
You qualify for free shipping.
{{else}}
Thank you for your order.
{{#if order.total > 50}}
You're {{100 - order.total|round}} away from free shipping!
{{/if}}
{{/if}}

{{#each order.items}}
- {{this.name}}: ${{this.price|round(2)}}
{{/each}}

Total: ${{order.total|round(2)}}
"""
```

---

## Parameter System

### Parameter Definition
```toml
[parameters]
database_url = "postgresql://user:pass@host/db"
api_version = "v1"
retry_count = 3
enable_debug = true
```

### Parameter Access Patterns
```toml
# In node configurations
connection_string = {{.Parameter.database_url}}
endpoint = "https://api.com/{{.Parameter.api_version}}/data"
max_retries = {{.Parameter.retry_count}}
```

### Dynamic Parameter Generation
```toml
[node:SetDynamicParam]
type = py
code = """
def calculate_params():
    return {
        'calculated_limit': 1000,
        'timestamp': '2025-01-01'
    }
"""
function = calculate_params

# Use in later nodes
[node:UseParam]
type = neon
query = "SELECT * FROM table LIMIT {{SetDynamicParam.result.result.calculated_limit}}"
```

---

## Data Flow and References

### Node Output Reference Patterns

#### Python Node Results
```toml
# Python function returns: {'result': {'count': 42, 'status': 'success'}}
# Reference as: {{NodeName.result.result.count}}
```

#### Database Query Results
```toml
# Database returns array of objects
# Reference as: {{NodeName.data.0.column_name}}
# For multiple rows: {{NodeName.data.1.column_name}}
```

#### AI Model Results
```toml
# Claude/Gemini response
# Reference as: {{NodeName.result.content.0.text}}
```

#### UUID Generation Results
```toml
# UUID node output
# Reference as: {{NodeName.result.uuid}}
```

### Complex Data References
```toml
# JSON transformation
json_data = "{{to_json .NodeName.data}}"

# Array operations
array_element = "{{NodeName.data | jsonpath '$.[*].field'}}"

# Conditional references
value = "{{NodeName.result.field | default 'fallback_value'}}"
```

---

## Database Operations

### Schema Creation Pattern
```toml
[node:CreateSchema]
type = neon
label = "Create database schema"
connection_string = {{.Parameter.connection_string}}
operation = create_schema
schema_name = my_schema

[node:CreateTable]
type = neon
label = "Create table with proper constraints"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = """
CREATE TABLE my_schema.table_name (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
```

### Data Insertion Patterns
```toml
[node:InsertData]
type = neon
label = "Insert data with parameterized query"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = "INSERT INTO table (col1, col2) VALUES (%s, %s) RETURNING id"
parameters = ["{{input_node.result.value1}}", "{{input_node.result.value2}}"]
```

### Complex Query Patterns
```toml
[node:ComplexQuery]
type = neon
label = "Complex analytical query"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = """
WITH cte AS (
    SELECT 
        column1,
        COUNT(*) as count,
        AVG(numeric_column) as average
    FROM my_table 
    WHERE date_column >= %s
    GROUP BY column1
)
SELECT * FROM cte WHERE count > %s
ORDER BY average DESC
"""
parameters = ["{{.Parameter.start_date}}", "10"]
```

---

## API Route Definitions

### Standard CRUD Patterns

#### GET Route
```toml
[node:DefineGetRoute]
type = aci
mode = server
label = "GET /api/resource"
operation = add_route
route_path = /api/resource
methods = ["GET"]
handler = GetResourceHandler
description = "Retrieve all resources"

[node:HandleGetRequest]
type = neon
label = "Fetch resources from database"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = "SELECT * FROM resources ORDER BY created_at DESC"
parameters = []
```

#### POST Route with Parameters
```toml
[node:DefinePostRoute]
type = aci
mode = server
label = "POST /api/resource"
operation = add_route
route_path = /api/resource
methods = ["POST"]
handler = CreateResourceHandler
description = "Create new resource"

[node:HandlePostRequest]
type = neon
label = "Insert new resource"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = "INSERT INTO resources (name, data) VALUES (%s, %s) RETURNING *"
parameters = ["{{request_data.name}}", "{{request_data.data}}"]
```

#### Dynamic Route Parameters
```toml
[node:DefineGetByIdRoute]
type = aci
mode = server
label = "GET /api/resource/{id}"
operation = add_route
route_path = /api/resource/<int:resource_id_from_url>
methods = ["GET"]
handler = GetResourceByIdHandler
description = "Get specific resource by ID"

[node:HandleGetByIdRequest]
type = neon
label = "Fetch specific resource"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = "SELECT * FROM resources WHERE id = %s"
parameters = ["{{request_data.resource_id_from_url}}"]
```

---

## AI Integration

### Claude Integration Pattern
```toml
[node:AnalyzeWithClaude]
type = claude
label = "AI analysis of data"
api_key = "${CLAUDE_API_KEY}"
operation = messages
model = "claude-3-5-sonnet-20240620"
temperature = 0.2
max_tokens = 2000
messages = [
  {
    "role": "user",
    "content": """
    Analyze the following data and provide insights:
    
    Data: {{previous_node.result}}
    
    Please provide:
    1. Summary of key findings
    2. Recommendations
    3. Risk assessment
    """
  }
]
```

### Gemini Integration Pattern
```toml
[node:GenerateWithGemini]
type = gemini
label = "Content generation with Gemini"
api_key = ${GEMINI_API_KEY}
model = "gemini-1.5-pro-latest"
temperature = 0.3
max_output_tokens = 1500
prompt = """
Generate a report based on:
- Metric 1: {{data_node.result.metric1}}
- Metric 2: {{data_node.result.metric2}}

Format as structured markdown.
"""
mime_type = "text/plain"
```

### AI Response Processing
```toml
[node:ProcessAIResponse]
type = py
label = "Process and store AI response"
code = """
def process_ai_response():
    ai_text = "{{AnalyzeWithClaude.result.content.0.text}}"
    
    # Extract key information
    summary = ai_text.split('Summary:')[1].split('Recommendations:')[0].strip()
    
    return {
        'processed_summary': summary,
        'full_response': ai_text,
        'analysis_timestamp': '2025-01-01T12:00:00Z'
    }
"""
function = process_ai_response
```

---

## Error Handling and Validation

### Input Validation Pattern
```toml
[node:ValidateInput]
type = py
label = "Validate input parameters"
code = """
def validate_inputs():
    # Get input from previous node
    data = {{input_node.result}}
    errors = []
    
    # Validation rules
    if not data.get('email'):
        errors.append('Email is required')
    elif '@' not in data['email']:
        errors.append('Invalid email format')
    
    if not data.get('age') or data['age'] < 0:
        errors.append('Valid age is required')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'validated_data': data if len(errors) == 0 else None
    }
"""
function = validate_inputs
```

### Error Handling in Database Operations
```toml
[node:SafeDatabaseOperation]
type = neon
label = "Database operation with error handling"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = """
INSERT INTO table (column1, column2) 
VALUES (%s, %s) 
ON CONFLICT (unique_column) 
DO UPDATE SET 
    column2 = EXCLUDED.column2,
    updated_at = CURRENT_TIMESTAMP
RETURNING id, created_at, updated_at
"""
parameters = ["{{data.value1}}", "{{data.value2}}"]
```

### Conditional Flow Control
```toml
[node:ConditionalLogic]
type = py
label = "Conditional processing"
code = """
def conditional_processing():
    success = {{previous_node.result.success}}
    
    if success:
        return {'next_action': 'continue', 'message': 'Processing successful'}
    else:
        return {'next_action': 'error_handling', 'message': 'Processing failed'}
"""
function = conditional_processing

# Use conditions in edges
[edges]
ConditionalLogic = ContinueProcessing  # Only if success
ConditionalLogic = ErrorHandling       # Only if failure
```

---

## Performance and Optimization

### Batch Processing Pattern
```toml
[node:BatchProcessor]
type = py
label = "Process data in batches"
code = """
def process_in_batches():
    data = {{large_dataset.result}}
    batch_size = {{.Parameter.batch_size}}
    
    batches = []
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        batches.append(batch)
    
    return {
        'total_batches': len(batches),
        'batch_size': batch_size,
        'total_items': len(data)
    }
"""
function = process_in_batches
```

### Async Operations
```toml
[node:AsyncOperation]
type = py
label = "Asynchronous processing"
code = """
import asyncio
import aiohttp

async def async_api_calls():
    urls = {{url_list.result}}
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = session.get(url)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
    return {
        'completed_requests': len(responses),
        'results': [r.status for r in responses]
    }
"""
function = async_api_calls
```

## Execution Engine Constraints

### Node Execution Requirements

#### 1. Node Result Structure
Every node executor **MUST** return a dictionary with specific structure:
```python
# REQUIRED structure for all node results
{
    "status": "success|error|warning",  # MANDATORY
    "message": "Description of what happened",  # Optional but recommended
    "result": any_data  # The actual result data
}
```

#### 2. Status Validation
- Valid statuses: `"success"`, `"error"`, `"warning"` (from `execution_manager.py:875`)
- Invalid statuses are automatically converted to `"warning"`
- Missing status field causes result wrapping

#### 3. Node Discovery Rules
Node executors are discovered using these patterns (from `execution_manager.py:435-451`):
```python
# 1. Explicit node_type class attribute (preferred)
class MyCustomNode(BaseNode):
    node_type = "my_custom"  # Explicit type definition

# 2. Class name conversion (fallback)
class SqlQueryNode(BaseNode):  # Becomes "sql_query"
class DataFetchNode(BaseNode):  # Becomes "data_fetch"
```

#### 4. Execution Flow Constraints

**Sequential Execution:**
- Nodes execute one at a time in order defined by edges
- Each node waits for predecessor completion
- No parallel execution within a single flow

**Loop Prevention:**
- Simple loop detection prevents infinite execution
- Nodes can only execute once per workflow run
- Circular edge detection at parse time

**Timeout Management:**
```toml
[settings]
sandbox_timeout = 600  # Maximum workflow execution time (seconds)
max_retries = 3        # Node retry attempts on failure
```

#### 5. Conditional Node Execution Rules

**If Node Requirements:**
```toml
[node:ConditionalCheck]
type = if
# MUST implement: result = {"result": boolean}
# Edge order matters: [0] = true path, [1] = false path

[edges]
ConditionalCheck = TruePath, FalsePath  # Order is critical!
```

**Switch Node Requirements:**
```toml
[node:MultiPathRouter]
type = switch
# MUST implement: result = {"selected_node": "target_name"}
# selected_node must be in successor edges

[edges]
MultiPathRouter = PathA, PathB, PathC  # All potential targets
```

#### 6. Special Node Behaviors

**Set Node Storage:**
```python
# Set nodes store values in execution context
result = {
    "status": "success",
    "result": {
        "key": "storage_key",      # How to access later
        "value": any_python_object # What gets stored
    }
}
# Access later: {{key:storage_key}}
```

**ACI Node Integration:**
```python
# ACI nodes register with agent server automatically
# Only works when agent_server is configured
if self.agent_server and node_type == 'aci':
    # Automatic route registration happens
    self.agent_server.register_aci_route(route_path, route_config)
```

### Data Structure Processing

#### 1. Parameter Type Conversion
The execution engine automatically converts string values (from `execution_manager.py:972-1022`):

```toml
# Automatic conversions applied:
boolean_true = "true"     # → True (boolean)
boolean_false = "false"   # → False (boolean)
integer_val = "42"        # → 42 (int)
float_val = "3.14"        # → 3.14 (float)
json_data = '{"key": "value"}'  # → {"key": "value"} (dict)

# JSON conversion triggered by key names:
messages = '[{"role": "user", "content": "test"}]'  # Auto-parsed
data = '{"items": [1, 2, 3]}'  # Auto-parsed
```

#### 2. Execution Context Structure
```python
# Context available to all nodes during execution
executor_data = {
    'params': {
        # All node parameters after type conversion
        'param1': 'value1',
        'param2': 42
    },
    'type': 'node_type',
    'label': 'Human readable description',
    '__node_name': 'current_node_name',
    '__execution_id': 'unique_execution_id'
}
```

### Error Handling Constraints

#### 1. Node Execution Errors
```python
# Error categories and handling:
NodeExecutionError       # Node-specific execution failures
NodeValidationError      # Parameter validation failures  
PlaceholderResolutionError  # Placeholder resolution failures
ActfileParserError       # Flow definition parsing errors
```

#### 2. Error Propagation
- Any node returning `status: "error"` stops workflow execution
- Unhandled exceptions are caught and converted to error status
- Error messages are preserved and logged
- Partial results may be available depending on failure point

#### 3. Status Callback System
```python
# Status callbacks receive updates during execution
def status_callback(node_name, status, message, all_status):
    # Called for each node status change
    # status: "pending", "running", "success", "error", "warning"
    pass

execution_manager.register_status_callback(status_callback)
```

### Agent Configuration Integration

#### 1. Agent Server Requirements
```toml
[configuration]
agent_enabled = true      # Required for agent features
host = "0.0.0.0"         # Server host
port = 8080              # Server port
cors_enabled = true      # Enable CORS
debug = true             # Debug mode

[deployment]
environment = "development"  # Environment setting
workers = 1              # Worker processes (future use)
```

#### 2. ACI Node Requirements
```toml
[node:DefineRoute]
type = aci
mode = server            # REQUIRED for API routes
operation = add_route    # Supported operations
route_path = /api/test   # URL path
methods = ["GET"]        # HTTP methods
handler = TestHandler    # Handler name
```

### Memory Optimization
```toml
[node:MemoryEfficientProcessing]
type = py
label = "Memory-efficient data processing"
code = """
def process_large_dataset():
    # Stream processing instead of loading everything
    total_processed = 0
    chunk_size = 1000
    
    # Simulate streaming processing
    for chunk_start in range(0, 1000000, chunk_size):
        # Process chunk
        total_processed += min(chunk_size, 1000000 - chunk_start)
    
    return {
        'total_processed': total_processed,
        'memory_efficient': True
    }
"""
function = process_large_dataset
```

---

## Flow Examples by Category

### 1. Simple Data Processing Flow
```toml
[workflow]
name = "Simple Data Processor"
description = "Process and validate incoming data"
start_node = ReceiveData

[node:ReceiveData]
type = py
label = "Receive input data"
code = """
def receive_data():
    return {'data': [1, 2, 3, 4, 5], 'timestamp': '2025-01-01'}
"""
function = receive_data

[node:ProcessData]
type = py
label = "Process the data"
code = """
def process_data():
    data = {{ReceiveData.result.result.data}}
    processed = [x * 2 for x in data]
    return {'processed': processed, 'count': len(processed)}
"""
function = process_data

[node:LogResults]
type = log_message
label = "Log processing results"
level = info
message = "Processed {{ProcessData.result.result.count}} items"

[edges]
ReceiveData = ProcessData
ProcessData = LogResults
```

### 2. Database-Driven API Flow
```toml
[workflow]
name = "User Management API"
description = "Complete user management with database backend"
start_node = CreateUserTable

[parameters]
db_connection = "postgresql://user:pass@host/db"

[node:CreateUserTable]
type = neon
label = "Create users table"
connection_string = {{.Parameter.db_connection}}
operation = execute_query
query = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

[node:DefineCreateUserRoute]
type = aci
mode = server
label = "POST /api/users"
operation = add_route
route_path = /api/users
methods = ["POST"]
handler = CreateUserHandler
description = "Create new user"

[node:CreateUser]
type = neon
label = "Insert new user"
connection_string = {{.Parameter.db_connection}}
operation = execute_query
query = "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING *"
parameters = ["{{request_data.username}}", "{{request_data.email}}"]

[edges]
CreateUserTable = DefineCreateUserRoute
DefineCreateUserRoute = CreateUser

[configuration]
port = 8080
host = "0.0.0.0"
```

### 3. AI-Enhanced Analysis Flow
```toml
[workflow]
name = "AI Data Analysis Pipeline"
description = "Analyze data with AI and generate reports"
start_node = LoadData

[parameters]
data_source = "/path/to/data.json"

[node:LoadData]
type = py
label = "Load data for analysis"
code = """
def load_data():
    # Simulate data loading
    data = {
        'sales': [100, 150, 200, 180, 220],
        'regions': ['North', 'South', 'East', 'West', 'Central'],
        'period': 'Q1 2025'
    }
    return data
"""
function = load_data

[node:AnalyzeWithAI]
type = claude
label = "AI analysis of sales data"
api_key = "${CLAUDE_API_KEY}"
model = "claude-3-5-sonnet-20240620"
temperature = 0.1
max_tokens = 1500
messages = [
  {
    "role": "user",
    "content": """
    Analyze this sales data and provide insights:
    
    Sales by Region: {{LoadData.result.result.sales}}
    Regions: {{LoadData.result.result.regions}}
    Period: {{LoadData.result.result.period}}
    
    Provide:
    1. Performance summary
    2. Top performing regions
    3. Recommendations
    """
  }
]

[node:SaveAnalysis]
type = py
label = "Save analysis results"
code = """
def save_analysis():
    analysis = "{{AnalyzeWithAI.result.content.0.text}}"
    return {
        'saved': True,
        'analysis_length': len(analysis),
        'timestamp': '2025-01-01T12:00:00Z'
    }
"""
function = save_analysis

[edges]
LoadData = AnalyzeWithAI
AnalyzeWithAI = SaveAnalysis

[env]
CLAUDE_API_KEY
```

---

## Common Patterns and Templates

### 1. Database Setup Template
```toml
# Standard database initialization pattern
[node:CleanupDatabase]
type = neon
label = "Cleanup previous data"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = "DROP SCHEMA IF EXISTS {{schema_name}} CASCADE"

[node:CreateSchema]
type = neon
label = "Create fresh schema"
connection_string = {{.Parameter.connection_string}}
operation = create_schema
schema_name = {{schema_name}}

[node:CreateTables]
type = neon
label = "Create application tables"
connection_string = {{.Parameter.connection_string}}
operation = execute_query
query = """
CREATE TABLE {{schema_name}}.main_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

[edges]
CleanupDatabase = CreateSchema
CreateSchema = CreateTables
```

### 2. API Route Collection Template
```toml
# Standard CRUD API pattern
[node:DefineGetAllRoute]
type = aci
mode = server
operation = add_route
route_path = /api/resource
methods = ["GET"]
handler = GetAllHandler

[node:DefineGetByIdRoute]
type = aci
mode = server
operation = add_route
route_path = /api/resource/<int:id>
methods = ["GET"]
handler = GetByIdHandler

[node:DefineCreateRoute]
type = aci
mode = server
operation = add_route
route_path = /api/resource
methods = ["POST"]
handler = CreateHandler

[node:DefineUpdateRoute]
type = aci
mode = server
operation = add_route
route_path = /api/resource/<int:id>
methods = ["PUT"]
handler = UpdateHandler

[node:DefineDeleteRoute]
type = aci
mode = server
operation = add_route
route_path = /api/resource/<int:id>
methods = ["DELETE"]
handler = DeleteHandler

# Corresponding database handlers
[node:GetAllResources]
type = neon
operation = execute_query
query = "SELECT * FROM resources ORDER BY created_at DESC"

[node:GetResourceById]
type = neon
operation = execute_query
query = "SELECT * FROM resources WHERE id = %s"
parameters = ["{{request_data.id}}"]

# ... etc for other operations
```

### 3. AI Processing Template
```toml
# Standard AI analysis pattern
[node:PrepareAIPrompt]
type = py
label = "Prepare data for AI analysis"
code = """
def prepare_prompt():
    data = {{input_node.result}}
    prompt = f"Analyze this data: {data}"
    return {'prompt': prompt, 'data_summary': len(str(data))}
"""
function = prepare_prompt

[node:CallAI]
type = claude
api_key = "${CLAUDE_API_KEY}"
model = "claude-3-5-sonnet-20240620"
temperature = 0.2
messages = [{"role": "user", "content": "{{PrepareAIPrompt.result.result.prompt}}"}]

[node:ProcessAIResponse]
type = py
label = "Process AI response"
code = """
def process_response():
    response = "{{CallAI.result.content.0.text}}"
    return {
        'response': response,
        'word_count': len(response.split()),
        'processed_at': '2025-01-01T12:00:00Z'
    }
"""
function = process_response

[edges]
PrepareAIPrompt = CallAI
CallAI = ProcessAIResponse
```

---

## Best Practices

### 1. Naming Conventions
- **Flows**: Use descriptive names that indicate purpose
- **Nodes**: Use PascalCase for node names, descriptive prefixes
- **Labels**: Always include human-readable descriptions
- **Parameters**: Use snake_case for parameter names

### 2. Code Organization
- Group related nodes together with comments
- Use consistent indentation and formatting
- Include header comments explaining flow sections
- Keep node code focused and single-purpose

### 3. Error Handling
- Always include validation for external inputs
- Use parameterized queries to prevent SQL injection
- Implement graceful fallbacks for API failures
- Log important operations and errors

### 4. Performance Considerations
- Use batch processing for large datasets
- Implement proper database indexing strategies
- Cache frequently accessed data
- Use async operations where appropriate

### 5. Security Guidelines
- Never hardcode sensitive information
- Use environment variables for secrets
- Validate all external inputs
- Implement proper authentication and authorization

### 6. Testing and Validation
- Include validation nodes for critical operations
- Test with realistic data volumes
- Verify database constraints and relationships
- Test error conditions and edge cases

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Parameter Reference Errors
**Problem**: `{{.Parameter.name}}` returns empty
**Solution**: Ensure parameter is defined in `[parameters]` section
```toml
[parameters]
database_url = "actual_url_here"

[node:UseParam]
connection_string = {{.Parameter.database_url}}  # Correct
```

#### 2. Node Data Access Issues
**Problem**: Cannot access node results
**Solution**: Use correct reference pattern based on node type
```toml
# Python node: {{NodeName.result.result.key}}
# Database node: {{NodeName.data.0.column}}
# AI node: {{NodeName.result.content.0.text}}
```

#### 3. Edge Definition Problems
**Problem**: Flow doesn't execute in correct order
**Solution**: Verify all edges are properly defined
```toml
[edges]
StartNode = MiddleNode
MiddleNode = EndNode
# Not: StartNode = EndNode (skips MiddleNode)
```

#### 4. Database Connection Issues
**Problem**: Database operations fail
**Solution**: Check connection string format and permissions
```toml
[parameters]
# Correct format
connection_string = "postgresql://user:password@host:port/database"
```

#### 5. API Route Conflicts
**Problem**: Routes not working
**Solution**: Ensure unique route paths and proper handler names
```toml
[node:DefineRoute]
type = aci
mode = server  # Don't forget this!
route_path = /api/unique/path
handler = UniqueHandlerName
```

#### 6. Execution Engine Issues

**Problem**: Node executor not found
**Solution**: Check node type spelling and ensure node class exists
```python
# Node class must extend BaseNode and define node_type
class MyCustomNode(BaseNode):
    node_type = "my_custom"  # Must match flow definition
```

**Problem**: Circular reference errors
**Solution**: Check placeholder dependencies and edge definitions
```toml
# Avoid circular placeholder references
[node:A]
data = "{{B.result}}"  # OK

[node:B] 
data = "{{A.result}}"  # ERROR: Circular reference!
```

**Problem**: Conditional nodes not branching correctly
**Solution**: Ensure proper result structure and edge order
```toml
[node:IfNode]
type = if
# MUST return: {"result": boolean}

[edges]
IfNode = TruePath, FalsePath  # Order matters: [0]=true, [1]=false
```

**Problem**: Placeholder resolution failures
**Solution**: Enable debug mode to trace resolution steps
```toml
[settings]
resolution_debug_mode = true
fail_on_unresolved = false  # Continue on failures
```

**Problem**: Node results not accessible
**Solution**: Check result structure and path strategies
```toml
# Multiple strategies tried automatically:
direct = "{{NodeName.result.field}}"      # Strategy 1
skip_wrapper = "{{NodeName.field}}"       # Strategy 2
add_prefix = "{{NodeName.result.data}}"   # Strategy 3
```

#### 7. Type Conversion Issues

**Problem**: Parameters not converting to expected types
**Solution**: Understand automatic conversion rules
```toml
# Automatic conversions (from execution_manager.py:972-1022):
boolean_val = "true"      # → True (boolean)
integer_val = "42"        # → 42 (int)  
float_val = "3.14"        # → 3.14 (float)
json_array = '[1,2,3]'    # → [1,2,3] (list)

# JSON keys trigger automatic parsing:
messages = '["hello"]'    # Auto-parsed due to key name
data = '{"test": true}'   # Auto-parsed due to key name
config = '{"x": 1}'       # Auto-parsed due to key name
```

**Problem**: Placeholder not resolving despite value existing
**Solution**: Use multi-strategy resolution awareness
```python
# The system tries 4 strategies automatically:
# 1. Direct: NodeName.result.field
# 2. Skip wrapper: NodeName.field (if starts with 'result')  
# 3. Add prefix: result.NodeName.field (if doesn't start with 'result')
# 4. Direct result access: Look in result dict directly

# Enable debug to see which strategy succeeds:
[settings]
resolution_debug_mode = true
```

### Advanced Debugging Techniques

#### 1. Resolution Debug Mode
```toml
[settings]
resolution_debug_mode = true  # Detailed placeholder resolution
fail_on_unresolved = false    # Continue on unresolved placeholders
```

Debug output shows:
- Cache hits/misses
- Resolution strategy attempts
- Path traversal steps
- Circular reference detection
- Final resolved values

#### 2. Execution Status Monitoring
```python
# Monitor node execution in real-time
def status_monitor(node_name, status, message, all_status):
    print(f"Node {node_name}: {status} - {message}")

execution_manager.register_status_callback(status_monitor)
```

#### 3. Node Loading Status
The system provides detailed node loading information:
- Which node types are required
- Whether node classes were found
- Loading success/failure with reasons
- Case-insensitive fallback attempts

### Debugging Tips

1. **Enable Debug Mode**
   ```toml
   [settings]
   debug_mode = true
   resolution_debug_mode = true
   ```

2. **Add Logging Nodes**
   ```toml
   [node:DebugLog]
   type = log_message
   level = debug
   message = "Debug info: {{node_result.data}}"
   ```

3. **Use Data Inspection Nodes**
   ```toml
   [node:InspectData]
   type = py
   code = """
   def inspect():
       data = {{previous_node.result}}
       print(f"Data type: {type(data)}")
       print(f"Data content: {data}")
       return {'inspected': True}
   """
   function = inspect
   ```

4. **Validate Parameter Access**
   ```toml
   [node:ValidateParams]
   type = py
   code = """
   def validate_params():
       param = "{{.Parameter.test_param}}"
       return {'param_value': param, 'param_type': type(param)}
   """
   function = validate_params
   ```

---

## Configuration Reference

### Server Configuration
```toml
[configuration]
agent_enabled = true
agent_name = "FlowAgent"
agent_version = "1.0.0"
host = "0.0.0.0"
port = 8080
debug = true
cors_enabled = true

[deployment]
environment = "development"  # or "production"
```

### Performance Settings
```toml
[settings]
debug_mode = true
max_retries = 3
timeout_seconds = 300
batch_size = 1000
concurrent_limit = 10
```

### Environment Variables
```toml
[env]
# Database
DATABASE_URL
DATABASE_PASSWORD

# API Keys
CLAUDE_API_KEY
GEMINI_API_KEY
OPENAI_API_KEY

# External Services
STRIPE_SECRET_KEY
SENDGRID_API_KEY
```

---

## Quick Reference

### Critical Requirements Checklist

**MANDATORY Flow Elements:**
- [ ] `[workflow]` section with `start_node`
- [ ] `start_node` references existing node in `[nodes]`
- [ ] All nodes have `type` field
- [ ] All edge sources/targets exist in `[nodes]`

**Node Result Structure:**
```python
# REQUIRED for all node executors
{
    "status": "success|error|warning",  # MANDATORY
    "message": "Description",           # Recommended
    "result": actual_data              # The payload
}
```

**Placeholder Syntax:**
```toml
# Parameter reference
value = "{{.Parameter.param_name}}"

# Node result reference (multiple strategies tried automatically)
data = "{{NodeName.result.field}}"

# Environment variable
key = "${ENV_VAR_NAME}"

# Key-based storage (from set nodes)
stored = "{{key:storage_key}}"

# With filters and fallbacks
processed = "{{data.items|length|default(0)}}"

# Conditional blocks
text = """
{{#if condition}}
Content when true
{{else}}
Content when false
{{/if}}
"""

# Loop blocks
list = """
{{#each items}}
- {{index}}: {{this.name}}
{{/each}}
"""
```

**Special Node Types:**
```toml
# Conditional branching
[node:IfCheck]
type = if
# Must return: {"result": boolean}
# Edges: [0] = true path, [1] = false path

# Multi-way branching
[node:SwitchRoute]
type = switch  
# Must return: {"selected_node": "target_name"}

# Value storage
[node:SetValue]
type = set
# Must return: {"key": "name", "value": data}

# API route definition
[node:DefineAPI]
type = aci
mode = server  # REQUIRED
operation = add_route
```

**Configuration Sections:**
```toml
[configuration]
agent_enabled = true    # Enable agent features
host = "0.0.0.0"       # Server host
port = 8080            # Server port

[settings]
debug_mode = true              # Enable debug logging
resolution_debug_mode = true   # Trace placeholder resolution
sandbox_timeout = 600          # Max execution time (seconds)
fail_on_unresolved = false     # Continue on placeholder failures

[deployment]
environment = "development"    # Environment setting
```

### Common Error Patterns

1. **Missing `mode = server`** in ACI nodes
2. **Incorrect conditional node result structure** (must return `{"result": boolean}` for if nodes)
3. **Edge order issues** for conditional nodes (true/false path order matters)
4. **Circular placeholder references**
5. **Missing `type` field** in node definitions
6. **Invalid `start_node`** reference

### Performance Tips

1. Use **placeholder caching** - identical placeholders resolved once
2. Enable **resolution debug mode** only during development
3. Use **parameter section** for repeated values
4. Minimize **nested placeholder resolution** depth
5. Use **set nodes** for complex calculated values used multiple times

### Advanced Features

- **Multi-strategy path resolution** (4 fallback strategies)
- **Filter chain system** with 20+ built-in filters
- **Template blocks** with conditionals and loops
- **Automatic type conversion** for strings
- **Circular reference detection**
- **Node discovery** with case-insensitive fallbacks
- **Status callback system** for monitoring
- **Agent server integration** with automatic route registration

---

