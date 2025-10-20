# Flow Architect Sandbox Configuration

## 🎯 Purpose
Properly sandbox the Flow Architect agent to prevent system access while maintaining functionality through APIs.

## 📁 File Structure

```
ai-desktop/
├── .claude/settings.local.json          # Main Claude settings (your workspace)
└── flow-architect/
    └── .claude/settings.local.json      # Flow Architect ONLY settings (sandboxed)
```

## 🔑 How It Works

### 1. **Two Separate Settings Files**

**Main Claude** (`/.claude/settings.local.json`):
- Has broader permissions for development
- Can access Docker, npm, git, etc.
- You use this when working on the project

**Flow Architect** (`/flow-architect/.claude/settings.local.json`):
- HIGHLY RESTRICTED
- Only its own folder
- Only specific API calls
- NO Docker access
- NO system commands

### 2. **Settings Precedence**

When Claude processes a request in the Flow Architect context:
1. First checks `flow-architect/.claude/settings.local.json` (most specific)
2. Falls back to project root `.claude/settings.local.json`
3. Falls back to global Claude settings

The most specific settings WIN, so Flow Architect gets sandboxed.

## 🚫 What Flow Architect CANNOT Do

```json
"deny": [
  "Bash(docker*)",           // No Docker commands
  "Read(../**)",             // Cannot read parent directories
  "Read(/etc/**)",           // Cannot read system files
  "Read(.env*)",             // Cannot read environment files
  "Bash(sudo*)",             // No sudo access
  "WebFetch(domain:*)",      // Only localhost API calls
  "WebSearch"                // No web searches
]
```

## ✅ What Flow Architect CAN Do

```json
"allow": [
  "Read(flow-architect/**)",                              // Read its own files
  "Write(flow-architect/**)",                             // Write its own files
  "Bash(curl -s http://localhost:3000/api/catalog*)",    // Call catalog API
  "Bash(curl -s http://localhost:3000/api/ports*)",      // Call ports API
  "Bash(curl -X POST http://localhost:3000/api/act/execute*)", // Execute flows
  "WebFetch(domain:localhost)"                            // Fetch from local APIs
]
```

## 🛡️ Security Layers

### Layer 1: File System Isolation
- **Restricted to:** `/flow-architect/` folder ONLY
- **Cannot access:** Parent directories, system files, other projects

### Layer 2: Command Restrictions
- **Allowed:** Only specific curl commands to localhost APIs
- **Blocked:** Docker, ps, netstat, sudo, rm -rf, etc.

### Layer 3: Network Isolation
- **Allowed:** localhost:3000 APIs only
- **Blocked:** External web access, other domains

### Layer 4: Environment Variables
```json
"env": {
  "FLOW_ARCHITECT_SANDBOX": "true",
  "ALLOWED_PATH": "/Users/tajnoah/Downloads/ai-desktop/flow-architect"
}
```

## 🧪 Testing the Sandbox

### Test 1: Check Service Status
**Ask in Action Builder:** "What services are running?"

**Expected behavior:**
```bash
# SHOULD use:
curl -s http://localhost:3000/api/catalog?status=running

# SHOULD NOT use:
docker ps  # BLOCKED
```

### Test 2: Try to Access Parent Directory
**Ask:** "Read the package.json file in the parent directory"

**Expected:** "Permission denied - cannot access files outside flow-architect/"

### Test 3: Try Docker Command
**Ask:** "Check Docker containers"

**Expected:** "Cannot use Docker commands - must use catalog API instead"

## ⚙️ Configuration Details

### Permission Syntax

**Glob patterns:**
```json
"Read(flow-architect/**)"     // All files in folder
"Read(*.md)"                  // Only markdown files
"Read(contexts/*.md)"         // Specific subfolder
```

**Command patterns:**
```json
"Bash(npm run test:*)"        // npm test commands
"Bash(curl -s http://localhost:3000/*)"  // API calls
```

### Security Flags

```json
"security": {
  "sandbox": true,                    // Enable sandboxing
  "restrictToFolder": "flow-architect", // Lock to folder
  "apiOnly": true,                    // Force API usage
  "noSystemCommands": true,           // Block system access
  "noDockerAccess": true,            // Block Docker
  "noFileSystemNavigation": true     // Block fs navigation
}
```

## 📊 Verification Commands

Check if sandbox is active:
```bash
# In main terminal (you have access):
cat flow-architect/.claude/settings.local.json | jq '.security.sandbox'
# Output: true

# Check denied permissions:
cat flow-architect/.claude/settings.local.json | jq '.permissions.deny | length'
# Output: 29 (many restrictions)
```

## 🔧 Troubleshooting

### Issue: Agent still using Docker commands
**Solution:** Clear Claude cache and restart:
```bash
# Clear any cached settings
rm -rf ~/.claude/cache/*
# Restart Claude Code
```

### Issue: Agent can't access catalog API
**Solution:** Check allow list includes the API:
```json
"allow": [
  "Bash(curl -s http://localhost:3000/api/catalog*)"
]
```

### Issue: Settings not being applied
**Solution:** Ensure file is valid JSON:
```bash
# Validate JSON syntax
jq . flow-architect/.claude/settings.local.json
```

## 🚀 Best Practices

1. **Never put secrets in settings.local.json**
   - Use environment variables instead
   - Settings files can be read by the agent

2. **Test sandbox regularly**
   - Try forbidden commands
   - Verify API-only access
   - Check folder restrictions

3. **Keep deny list comprehensive**
   - Block all Docker commands
   - Block all system paths
   - Block all parent directory access

4. **Use specific allows**
   - Don't use wildcards unnecessarily
   - Be explicit about API endpoints
   - Limit to required operations

## 📝 Maintenance

### Adding New API Access
```json
// Add to allow list:
"Bash(curl -s http://localhost:3000/api/new-endpoint*)"
```

### Blocking New Threat
```json
// Add to deny list:
"Bash(dangerous-command*)"
```

### Updating Folder Path
```json
"env": {
  "ALLOWED_PATH": "/new/path/to/flow-architect"
}
```

## ⚠️ Important Notes

1. **Git ignores settings.local.json**
   - Each developer can have their own
   - Won't be committed to repo
   - Safe for local customization

2. **Settings are hierarchical**
   - Most specific wins
   - Project overrides global
   - Folder overrides project

3. **Sandbox != Perfect Security**
   - Additional layers needed for production
   - Consider Docker containers for true isolation
   - Monitor API access logs

## 🔍 Verification Checklist

- [ ] Flow Architect has its own `.claude/settings.local.json`
- [ ] Deny list blocks Docker commands
- [ ] Deny list blocks parent directory access
- [ ] Allow list only includes necessary APIs
- [ ] Security flags are enabled
- [ ] Test shows agent using APIs, not Docker
- [ ] Agent cannot read .env files
- [ ] Agent cannot access system directories

## 📞 Support

If the sandbox isn't working properly:
1. Check this documentation
2. Verify JSON syntax
3. Clear Claude cache
4. Restart Claude Code
5. Check API endpoints are running

---

**Created:** 2024-10-20
**Version:** 1.0.0
**Status:** Active Sandbox Configuration