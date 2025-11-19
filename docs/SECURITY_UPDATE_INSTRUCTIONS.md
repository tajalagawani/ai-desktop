# Flow Builder Security Update - Manual Deployment Guide

## Overview

This update adds a proper security settings UI that requires user consent before enabling sandbox bypass for the AI agent. This is critical for VPS deployments running as root.

## What Changed

### 1. Security Settings Store
- **File**: `lib/flow-builder/stores/settings-store.ts`
- **Change**: Added `allowSandboxBypass: boolean` setting (defaults to `false`)

### 2. Settings UI with Warning Dialog
- **File**: `components/flow-builder/FlowBuilderSettings.tsx`
- **Change**: Added new "Security" tab with:
  - Red warning alerts
  - Clear explanation of risks
  - Confirmation dialog before enabling
  - Environment detection (local vs VPS)

### 3. Agent SDK Security Check
- **File**: `agent-sdk/index.js`
- **Change**: Only enables `dangerouslyDisableSandbox` if `ALLOW_SANDBOX_BYPASS=true` in `.env`

### 4. Settings API Endpoint
- **File**: `app/api/flow-builder/settings/route.ts` (NEW)
- **Purpose**: Provides API to check/update security settings

### 5. Improved Error Logging
- **File**: `app/api/flow-builder/messages/route.ts`
- **Change**: Better error logging and validation for debugging 500 errors

## Deployment Steps for VPS

### Step 1: Upload Modified Files

Upload these 5 files to your VPS at `/var/www/ai-desktop/`:

```bash
lib/flow-builder/stores/settings-store.ts
components/flow-builder/FlowBuilderSettings.tsx
app/api/flow-builder/settings/route.ts
app/api/flow-builder/messages/route.ts
agent-sdk/index.js
```

You can use SCP:

```bash
scp lib/flow-builder/stores/settings-store.ts root@92.112.181.127:/var/www/ai-desktop/lib/flow-builder/stores/
scp components/flow-builder/FlowBuilderSettings.tsx root@92.112.181.127:/var/www/ai-desktop/components/flow-builder/
scp app/api/flow-builder/settings/route.ts root@92.112.181.127:/var/www/ai-desktop/app/api/flow-builder/settings/
scp app/api/flow-builder/messages/route.ts root@92.112.181.127:/var/www/ai-desktop/app/api/flow-builder/messages/
scp agent-sdk/index.js root@92.112.181.127:/var/www/ai-desktop/agent-sdk/
```

### Step 2: Update Environment Variable

SSH into your VPS:

```bash
ssh root@92.112.181.127
```

Add the security setting to `/var/www/ai-desktop/.env`:

```bash
cd /var/www/ai-desktop

# Add to .env file
echo "" >> .env
echo "# Security: Allow sandbox bypass for root execution (VPS only)" >> .env
echo "ALLOW_SANDBOX_BYPASS=true" >> .env
```

### Step 3: Rebuild the Application

```bash
export PATH=/root/.nvm/versions/node/v22.11.0/bin:$PATH
cd /var/www/ai-desktop

# Clean old build
rm -rf .next

# Build with new changes
npm run build
```

### Step 4: Restart PM2

```bash
pm2 restart ai-desktop
pm2 save
pm2 status
```

## Using the New Security Settings

### For VPS Users (Running as Root):

1. Open http://92.112.181.127
2. Click "Flow Builder" app
3. Click the Settings icon (gear) in top-right
4. Navigate to the **Security** tab
5. Read all the warnings carefully
6. Click the toggle for "Allow Sandbox Bypass"
7. Confirm the security warning dialog
8. Click "Save Changes"
9. Test creating a flow

### For Local Development Users:

**DO NOT enable sandbox bypass!** The agent will work fine without it on local machines.

## Security Features

### 1. User Must Explicitly Consent
- Setting defaults to `false` (SECURE)
- UI shows red warnings and "DANGEROUS" badge
- Requires confirmation dialog with explicit risks
- User must click through TWO warnings

### 2. Environment Detection
- UI detects if running on localhost vs remote server
- Shows appropriate recommendations
- Warns local users to keep it disabled

### 3. Backend Validation
- Agent SDK only enables bypass if `ALLOW_SANDBOX_BYPASS=true` in `.env`
- Logs security status on every agent run
- Frontend setting must match backend configuration

## Security Warnings in the UI

The UI displays:

**Enable this ONLY if:**
- You are running on a dedicated VPS server
- The server is running as root user
- You trust the AI agent with full system access

**DO NOT enable if:**
- Running on your local development machine
- Running in a shared hosting environment
- You are unsure about the security implications

## Troubleshooting

### Agent Still Fails with "cannot use --dangerously-skip-permissions"

1. Check `.env` has `ALLOW_SANDBOX_BYPASS=true`
2. Restart PM2: `pm2 restart ai-desktop`
3. Check agent logs for security status message

### Database 500 Errors

The updated messages API now has better error logging. Check PM2 logs:

```bash
pm2 logs ai-desktop --lines 50
```

Look for detailed error messages with stack traces.

### Build Fails

If build fails, try:

```bash
cd /var/www/ai-desktop
rm -rf .next node_modules
npm install
npm run build
```

## Verification

After deployment, verify:

1. **Settings UI loads**: Go to Flow Builder → Settings → Security tab
2. **Warning dialog works**: Try toggling sandbox bypass
3. **Backend recognizes setting**: Check PM2 logs when agent starts
4. **Agent runs successfully**: Create a test flow

Look for this in agent logs:

```
⚠️  [SECURITY] Sandbox bypass enabled - running with unrestricted access
```

Or if disabled:

```
🔒 [SECURITY] Sandbox enabled - running with normal security restrictions
```

## Rollback

If issues occur, rollback by:

1. Remove `ALLOW_SANDBOX_BYPASS=true` from `.env`
2. Restart PM2
3. The agent will run in secure mode (but may fail as root)

## Summary

This update ensures users:
- Understand the security implications
- Explicitly consent to bypass sandbox
- See clear warnings about risks
- Can easily enable/disable the setting

The system is now secure by default, with clear opt-in for VPS deployments.
