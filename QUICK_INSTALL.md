# AI Desktop VPS - Quick Install

## One-Command Installation

```bash
SSH_PASSWORD='your_vps_password' \
  ./deployment/vps-complete-install.sh \
  root@YOUR_VPS_IP \
  sk-ant-api03-YOUR_API_KEY
```

**Installation Time:** ~10-15 minutes

## What Gets Installed

- ✅ Node.js 22 (via NVM)
- ✅ PM2 (process manager)
- ✅ Nginx (reverse proxy, port 80 → 3005)
- ✅ ACT System (150+ workflow nodes)
- ✅ AI Desktop (with Flow Builder)
- ✅ Security Settings UI
- ✅ API Key Management

## After Installation

### Access Your Desktop
**URL:** http://YOUR_VPS_IP

### Configure Flow Builder
1. Open Flow Builder app
2. Click Settings (gear icon)
3. Go to **API Keys** tab - verify your key
4. Go to **Security** tab - enable sandbox bypass
5. Save settings

### Test It
Create a flow:
```
Create a weather tracking API that stores data in PostgreSQL
```

## Key Files

### On VPS

```
/var/www/ai-desktop/          # Main application
/var/www/ai-desktop/.env      # Desktop configuration
/var/www/act/                 # ACT workflow system
/var/www/act/agent-sdk/.env   # Agent configuration
/var/www/act/flows/           # Generated workflow files
```

### Environment Variables

**Agent SDK** (`/var/www/act/agent-sdk/.env`):
```bash
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY
ALLOW_SANDBOX_BYPASS=true
IS_SANDBOX=true
```

**Desktop** (`/var/www/ai-desktop/.env`):
```bash
PORT=80
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
ALLOW_SANDBOX_BYPASS=true
```

## Useful Commands

```bash
# View logs
pm2 logs ai-desktop

# Restart app
pm2 restart ai-desktop

# Check status
pm2 status

# Check disk space
df -h /

# Check memory
free -h

# Test agent directly
cd /var/www/act/agent-sdk
node index.js "Create a test flow"
```

## Security Settings

The installation includes **Security Settings UI** with:

- ✅ Warning dialogs before enabling sandbox bypass
- ✅ Clear explanation of risks
- ✅ Environment detection (local vs VPS)
- ✅ Confirmation prompts

**IMPORTANT:** Sandbox bypass is required for VPS but should NEVER be enabled on local machines.

## API Key Flow

1. **User saves API key** in Flow Builder settings (browser)
2. **Frontend sends key** via Socket.IO when starting agent
3. **Backend passes key** to agent as environment variable
4. **Agent uses key** for Claude API calls

**Fallback:** If no key in settings, uses `.env` file

## Troubleshooting

### Agent fails with sandbox error
```bash
# Check environment variables
cat /var/www/act/agent-sdk/.env | grep -E "ALLOW_SANDBOX_BYPASS|IS_SANDBOX"

# Should show:
# ALLOW_SANDBOX_BYPASS=true
# IS_SANDBOX=true
```

### Wrong API key used
Check PM2 logs:
```bash
pm2 logs ai-desktop | grep "API key"
```

Should show: `API key from settings: sk-ant-api03-YOUR_KEY...`

### Database errors
```bash
# Check database file
ls -la /var/www/ai-desktop/data/flow-builder.db

# Fix permissions if needed
chmod 777 /var/www/ai-desktop/data
```

## Full Documentation

See `VPS_COMPLETE_INSTALLATION_GUIDE.md` for:
- Manual step-by-step installation
- Detailed troubleshooting
- Maintenance procedures
- Security notes
- Backup procedures

---

**Ready?** Run the one-command installation above!
