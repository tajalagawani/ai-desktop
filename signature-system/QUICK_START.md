# ACT Signature System - Quick Start Guide

**Get started with the signature system in 5 minutes!**

---

## ✅ Prerequisites

- ✅ Node.js 18+ installed
- ✅ Python 3.8+ installed
- ✅ Claude Code CLI

---

## 🚀 Setup (Already Done!)

The signature system is already configured and ready to use:

1. ✅ **MCP Server**: Located at `signature-system/mcp/`
2. ✅ **Python Parser**: Located at `signature-system/parser/`
3. ✅ **Dependencies**: Installed (`npm install` complete)
4. ✅ **Config**: `.mcp.json` created in project root

---

## 🎯 Usage

### **Step 1: Start Using in Claude**

The MCP server is now available in Claude Code with **10 tools**:

**Execution**: execute_node_operation
**Signature**: get_signature_info, add_node_to_signature, remove_node_from_signature, update_node_defaults, validate_signature
**Catalog**: list_available_nodes, get_node_info
**Validation**: validate_params
**Utility**: get_system_status

#### **Tool 1: View Authenticated Nodes**
```
Can you check what nodes I have authenticated?
```

Claude will use: `get_signature_info()`

#### **Tool 2: Authenticate a New Node**

**Example: Authenticate GitHub**
```
Can you authenticate GitHub for me?
Access token: ghp_xxxxxxxxxxxxx
Default owner: myusername
Default repo: myrepo
```

Claude will use:
```javascript
add_node_to_signature({
  node_type: "github",
  auth: {access_token: "ghp_xxxxxxxxxxxxx"},
  defaults: {owner: "myusername", repo: "myrepo"}
})
```

**Behind the scenes**:
1. ✅ Validates token with GitHub API
2. ✅ Saves to `.env`: `GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxxx`
3. ✅ Writes signature: `access_token = "{{.env.GITHUB_ACCESS_TOKEN}}"`
4. ✅ Loads operations from catalog

#### **Tool 3: Execute Operations**

**Example: List GitHub Issues**
```
Can you list all open issues from my GitHub repo?
```

Claude will use:
```javascript
execute_node_operation({
  node_type: "github",
  operation: "list_issues",
  params: {state: "open"}
})
```

**✅ NO APPROVAL PROMPTS!** Instant execution using your signature.

---

## 📝 Manual Testing

### **Test MCP Server Directly**

```bash
# Run MCP server manually
cd signature-system/mcp
node index.js

# Should output:
# Flow Architect MCP Server running
# Tools available: execute_node_operation, get_signature_info, add_node_to_signature
```

### **Test Python Executor Directly**

```bash
# First create a test signature
cd signature-system/mcp/signatures
cp user.act.sig.example user.act.sig

# Edit user.act.sig to add your real tokens
# Then test execution:
cd ../../parser
python3 single_node_executor.py \
  ../mcp/signatures/user.act.sig \
  github \
  list_issues \
  '{"state":"open"}'
```

---

## 🔐 Security Notes

**Tokens are stored securely:**
- ✅ Actual tokens: `.env` file (gitignored)
- ✅ Signature file: Only has references like `{{.env.GITHUB_TOKEN}}`
- ✅ Never commit actual tokens to git

**Example `.env`:**
```bash
# GitHub Node
GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxxx

# OpenAI Node
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

**Example `.act.sig`:**
```toml
[node:github.auth]
access_token = "{{.env.GITHUB_ACCESS_TOKEN}}"

[node:openai.auth]
api_key = "{{.env.OPENAI_API_KEY}}"
```

---

## 📊 Available Nodes

Currently supported node types (extend as needed):
- **github** - GitHub API operations
- **openai** - OpenAI API operations
- **postgresql** - Database operations
- **stripe** - Payment processing
- **sendgrid** - Email sending
- **...** - 129+ nodes available in ACT library

---

## 🔧 Troubleshooting

### **Issue: MCP Server not found**

**Solution**: Restart Claude Code to reload `.mcp.json`

### **Issue: Python execution fails**

**Check**:
1. Python 3 installed: `python3 --version`
2. Dependencies installed: `pip3 list | grep toml`
3. ACT library accessible: `ls ../components/apps/act-docker/act/`

### **Issue: Authentication validation fails**

**Check**:
1. Token is valid (try in browser/curl)
2. Token has correct permissions
3. Internet connection working

---

## 📚 Next Steps

1. **Authenticate your first node** (GitHub recommended)
2. **Execute a simple operation** (list issues, repos, etc.)
3. **Explore more nodes** (OpenAI, databases, etc.)
4. **Build complex workflows** (coming soon with execute_flow tool)

---

## 🎉 You're Ready!

Start using Claude with pre-authenticated nodes - no more approval prompts!

**Try saying:**
- "Authenticate my GitHub account"
- "List my GitHub repositories"
- "What nodes do I have authenticated?"
- "Create a GitHub issue for bug X"

---

## 📖 Additional Resources

- `README.md` - System overview
- `IMPLEMENTATION_STATUS.md` - Current progress
- `COMPLETE-ACT-SIGNATURE-IMPLEMENTATION.md` - Full specification
- `MCP-SERVER-COMPLETE-ARCHITECTURE.md` - MCP details

---

**Need help?** Check the documentation or ask Claude!
