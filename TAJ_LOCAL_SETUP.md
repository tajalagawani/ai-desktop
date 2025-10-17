# 🔑 Taj's Local Machine Setup

Quick setup to use Claude CLI authentication on your machine.

---

## ✅ **Step-by-Step Setup**

### **1. Login to Claude CLI** (if not already)
```bash
claude login
```
This opens your browser for authentication.

### **2. Verify Authentication**
```bash
claude auth whoami
```
Should show your account info.

### **3. Update Your `.env` File**
```bash
# Edit .env file
nano .env
```

Add/modify these lines:
```env
# Enable Claude CLI auth (YOUR MACHINE ONLY)
USE_CLAUDE_CLI_AUTH=true

# You can leave API key blank or remove it entirely
# ANTHROPIC_API_KEY=
```

### **4. Restart the App**
```bash
npm run dev
```

### **5. Test It**
1. Open Action Builder from desktop
2. Send a message
3. Check terminal logs - should see: `Using Claude CLI authentication (no API key)`

---

## 🌐 **Important: VPS Deployment**

**When deploying to VPS, use this `.env` instead:**

```env
# VPS uses API key, NOT Claude CLI auth
USE_CLAUDE_CLI_AUTH=false
ANTHROPIC_API_KEY=sk-ant-your-production-key
NODE_ENV=production
PORT=3000
```

**Why?** VPS can't use `claude login` (no browser), and API keys are easier for servers.

---

## 🔄 **Switching Back to API Key** (if needed)

If you ever want to use API key instead:

1. Update `.env`:
   ```env
   USE_CLAUDE_CLI_AUTH=false
   ANTHROPIC_API_KEY=sk-ant-your-api-key
   ```

2. Restart: `npm run dev`

---

## ✅ **Done!**

Your machine now uses Claude CLI auth, while other users (and VPS) will use API keys from `.env`. No changes to code, just environment configuration!

**Files Modified:**
- `.env.example` - Added `USE_CLAUDE_CLI_AUTH` variable
- `server.js` - Added conditional auth logic
- `CLAUDE_AUTH_SETUP.md` - Full documentation
- `TAJ_LOCAL_SETUP.md` - This quick guide

**How It Works:**
- Your machine: `USE_CLAUDE_CLI_AUTH=true` → Uses `~/.claude/` authentication
- Other machines: `USE_CLAUDE_CLI_AUTH=false` → Uses `ANTHROPIC_API_KEY`
- No code changes needed!
