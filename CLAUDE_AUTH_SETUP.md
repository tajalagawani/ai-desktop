# Claude Authentication Setup Guide

This guide explains how to configure Claude authentication for Action Builder on your machine.

---

## 🔑 **Two Authentication Methods**

### **Method 1: API Key (Default - For All Users)**
Best for: Most users, VPS deployments, team environments

**Setup:**
1. Get your API key from https://console.anthropic.com/settings/keys
2. Add to `.env` file:
   ```env
   ANTHROPIC_API_KEY=sk-ant-your-actual-api-key
   USE_CLAUDE_CLI_AUTH=false
   ```
3. Restart the app: `npm run dev`

**Pros:**
- Simple setup
- Works on any machine
- Easy to share with team
- Good for VPS deployments

**Cons:**
- Requires API key management
- Need to rotate keys periodically

---

### **Method 2: Claude CLI Auth (Advanced - Your Machine Only)**
Best for: Your local development machine

**Setup:**
1. Install Claude CLI (if not already):
   ```bash
   npm install -g @anthropic-ai/claude-cli
   ```

2. Login to Claude:
   ```bash
   claude login
   ```
   This will open a browser and authenticate via Anthropic

3. Verify authentication:
   ```bash
   claude auth whoami
   ```
   You should see your account info

4. Update `.env` file:
   ```env
   # Leave API key blank or remove it
   # ANTHROPIC_API_KEY=

   # Enable Claude CLI auth
   USE_CLAUDE_CLI_AUTH=true
   ```

5. Restart the app: `npm run dev`

**Pros:**
- No API key needed
- Uses your Claude account authentication
- More secure (credentials stored in `~/.claude/`)
- Easier for personal use

**Cons:**
- Only works on machines where you've run `claude login`
- Not suitable for VPS/team deployments
- Requires Claude CLI to be installed

---

## 🔄 **How It Works**

### **When `USE_CLAUDE_CLI_AUTH=true`:**
```javascript
// server.js removes API key from environment
delete claudeEnv.ANTHROPIC_API_KEY

// Claude CLI uses authentication from ~/.claude/
claudeProcess = spawn('claude', args, { env: claudeEnv })
```

### **When `USE_CLAUDE_CLI_AUTH=false` (or not set):**
```javascript
// server.js passes API key to Claude CLI
claudeEnv.ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY

claudeProcess = spawn('claude', args, { env: claudeEnv })
```

---

## 📋 **Quick Decision Guide**

**Choose API Key if:**
- ✅ You're deploying to VPS
- ✅ Multiple people use the app
- ✅ You want simple setup
- ✅ You're okay managing API keys

**Choose Claude CLI Auth if:**
- ✅ This is your personal dev machine
- ✅ You've already run `claude login`
- ✅ You don't want to manage API keys
- ✅ You want more secure auth

---

## 🧪 **Testing Your Setup**

After configuring, test it:

1. **Start the app:**
   ```bash
   npm run dev
   ```

2. **Open Action Builder** from desktop

3. **Create a new session** and send a message

4. **Check the console logs** - you should see:
   - `Using Claude CLI authentication` (if Method 2)
   - `Using ANTHROPIC_API_KEY from environment` (if Method 1)

5. **If it works:** Claude responds normally ✅

6. **If it fails:**
   - Method 1: Check your API key is valid
   - Method 2: Run `claude auth whoami` to verify login

---

## 🔒 **Security Notes**

### **API Key Method:**
- Store `.env` in `.gitignore` (already done)
- Never commit API keys to git
- Rotate keys periodically
- Use environment variables on VPS

### **Claude CLI Auth Method:**
- Authentication stored in `~/.claude/`
- Tied to your Anthropic account
- Can logout with: `claude logout`
- Only affects your local machine

---

## 🌐 **VPS Deployment**

**For VPS, ALWAYS use API Key method:**

```bash
# On your VPS
cd /var/www/ai-desktop

# Create .env file
cat > .env <<EOF
ANTHROPIC_API_KEY=sk-ant-your-actual-key
USE_CLAUDE_CLI_AUTH=false
NODE_ENV=production
PORT=3000
EOF

# Start with PM2
pm2 start ecosystem.config.js
```

**Why not Claude CLI auth on VPS?**
- VPS may not have browser for `claude login`
- Multiple users can't share one authentication
- API keys are easier to manage in server environments

---

## 🆘 **Troubleshooting**

### **"Claude command not found"**
```bash
npm install -g @anthropic-ai/claude-cli
```

### **"Authentication failed"**
```bash
# Logout and login again
claude logout
claude login
```

### **"API key invalid"**
1. Check `.env` file has correct key
2. Verify key at https://console.anthropic.com/settings/keys
3. Make sure no extra spaces in `.env`

### **"Still using API key when USE_CLAUDE_CLI_AUTH=true"**
1. Restart the app completely
2. Check `.env` file syntax (no quotes needed)
3. Check console logs for which auth method is being used

---

## 📞 **Need Help?**

If you're stuck:
1. Check console logs in terminal
2. Run `claude auth whoami` to verify CLI auth
3. Try switching between methods to isolate the issue
4. Check GitHub issues: https://github.com/anthropics/claude-code/issues

---

## ✅ **Recommended Setup**

**For Taj (Your Machine):**
```env
USE_CLAUDE_CLI_AUTH=true
# No API key needed
```

**For Other Users:**
```env
USE_CLAUDE_CLI_AUTH=false
ANTHROPIC_API_KEY=sk-ant-their-api-key
```

**For VPS Deployment:**
```env
USE_CLAUDE_CLI_AUTH=false
ANTHROPIC_API_KEY=sk-ant-production-key
NODE_ENV=production
```

---

**That's it!** Your authentication is now flexible and secure. 🎉
