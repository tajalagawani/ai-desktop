# ACT Flow Troubleshooting

## Common Issues

### 1. Node Type Not Found

**Problem:** `Node type 'xyz' not found`

**Solution:**
- Use `mcp__act-workflow__list_available_nodes` to see all available nodes
- Check spelling of node type
- Verify node exists in the catalog

### 2. Authentication Required

**Problem:** `Node requires authentication`

**Solution:**
- Use `mcp__act-workflow__get_signature_info` to check authenticated nodes
- Use authenticated nodes when possible
- Document which nodes need authentication in metadata

### 3. Invalid TOML Syntax

**Problem:** `TOML parse error`

**Solution:**
- Check all strings are quoted properly
- Ensure proper escaping in multi-line strings
- Validate bracket matching in sections
- Use triple quotes for Python code blocks

### 4. Placeholder Not Resolved

**Problem:** `Could not resolve placeholder {{...}}`

**Solution:**
- Verify node name matches exactly (case-sensitive)
- Check the referenced node executed before this one
- Use correct syntax: `{{NodeName.result.field}}`
- For parameters: `{{.Parameter.param_name}}`

### 5. Missing Required Parameters

**Problem:** `Missing required parameter: xyz`

**Solution:**
- Use `mcp__act-workflow__get_operation_details` to see required params
- Check parameter names match exactly
- Ensure all required fields are provided

## Best Practices

### 1. Always Check Authentication First

```python
# Use this MCP tool first
mcp__act-workflow__get_signature_info
```

### 2. Validate Node Types

```python
# Search for nodes before using
mcp__act-workflow__search_operations(query="your keyword")
```

### 3. Use Meaningful Names

```toml
# Good
[node.FetchGitHubIssues]
[node.ProcessDataAndFormat]

# Bad
[node.Node1]
[node.Process]
```

### 4. Include Error Handling

```toml
[settings]
max_retries = 3
retry_delay = 1
timeout_seconds = 300
```

### 5. Test with Simple Flows First

Start with a single node, verify it works, then add complexity.
