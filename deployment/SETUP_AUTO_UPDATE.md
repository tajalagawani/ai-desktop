.# Update System Guide

This guide shows you how to use the update system for your AI Desktop deployment on VPS.

## How It Works

1. **User-Triggered Updates**: Updates are triggered manually by clicking "Update Now" button in the app
2. **Version Detection**: App compares deployed commit SHA with latest GitHub commit
3. **One-Click Deploy**: Button triggers script to pull, build, and restart automatically
4. **In-App Changelog**: View recent updates and version info from Power menu → Recent Updates
5. **No SSH Keys Required**: Works with public repositories without storing sensitive credentials

## Version Display

- **Primary Version**: Commit SHA (e.g., `abc1234`) - shown prominently as main version
- **Semantic Version**: v1.0.0 - shown as secondary badge
- **Last Updated**: Timestamp of last deployment

## Setup Instructions

### Step 1: SSH into Your VPS

```bash
ssh root@your-vps-ip
cd /var/www/ai-desktop
```

### Step 2: Make Update Script Executable

```bash
chmod +x deployment/auto-update.sh
```

### Step 3: Test the Script (Optional)

```bash
# Run manually to test
./deployment/auto-update.sh
```

You should see output like:
```
[2025-10-02 12:00:00] 🔍 Checking for updates...
[2025-10-02 12:00:01] ✅ Already up to date: abc1234
```

### Step 4: Using In-App Updates

**No cron setup needed!** Updates are triggered from the app:

1. Open the app in your browser
2. Click **Power button** (top-right) → **"Recent Updates"**
3. View current version (commit SHA) and available updates
4. If update available, click **"Update Now"** button
5. App automatically pulls latest code, builds, and restarts
6. Page reloads with new version after 3 seconds

Save and exit (Ctrl+X, then Y, then Enter in nano).

### Step 5: Verify Cron Job

```bash
# List all cron jobs
crontab -l

# You should see the auto-update job
```

### Step 6: Monitor Auto-Updates

```bash
# Watch the auto-update log in real-time
tail -f /var/www/ai-desktop/logs/auto-update.log

# View recent update activity
tail -n 50 /var/www/ai-desktop/logs/auto-update.log
```

## How to Use In-App Changelog

Users can view recent updates from within the application:

1. Click the **Power** button in the top-right taskbar
2. Select **"Recent Updates"** from the menu
3. See the latest 10 commits in a clean timeline layout with:
   - Commit date
   - Commit message (large, bold title)
   - Author and relative time
   - Commit SHA badge
   - Direct link to GitHub

The changelog features a minimalist design inspired by modern changelog templates, with a vertical timeline layout for easy scanning.

## Update Behavior

When a new commit is pushed to GitHub:

1. **Within 5 minutes**: Cron job detects the update
2. **Auto-deploy starts**: Script pulls latest code
3. **Dependencies install**: `npm ci` runs
4. **Build process**: `npm run build` executes
5. **App restarts**: PM2 restarts the application
6. **Zero downtime**: PM2 handles graceful restart

## Logs and Monitoring

### Check Auto-Update Status
```bash
# View last 20 log entries
tail -n 20 /var/www/ai-desktop/logs/auto-update.log

# Search for successful updates
grep "✅ Update completed" /var/www/ai-desktop/logs/auto-update.log

# Search for errors
grep "❌" /var/www/ai-desktop/logs/auto-update.log
```

### Check PM2 Status
```bash
pm2 status
pm2 logs ai-desktop --lines 50
```

### Manual Update Trigger
```bash
# Force update check now
/var/www/ai-desktop/deployment/auto-update.sh
```

## Troubleshooting

### Auto-update not running

**Check if cron job exists:**
```bash
crontab -l
```

**Check cron service:**
```bash
systemctl status cron
```

**Check script permissions:**
```bash
ls -la /var/www/ai-desktop/deployment/auto-update.sh
# Should show -rwxr-xr-x (executable)
```

### Updates detected but not deploying

**Check script logs:**
```bash
tail -f /var/www/ai-desktop/logs/auto-update.log
```

**Test script manually:**
```bash
cd /var/www/ai-desktop
./deployment/auto-update.sh
```

**Check git status:**
```bash
cd /var/www/ai-desktop
git status
git log --oneline -5
```

### Build failures during auto-update

**Check build logs:**
```bash
pm2 logs ai-desktop --lines 100 --err
```

**Fix and retry:**
```bash
cd /var/www/ai-desktop
npm install
npm run build
pm2 restart ai-desktop
```

### Changelog not loading in app

**Check API route:**
```bash
curl http://localhost/api/changelog
# Should return JSON with commits
```

**Check GitHub API:**
```bash
curl -s https://api.github.com/repos/tajalagawani/ai-desktop/commits?per_page=10
```

**GitHub rate limit:**
If you see rate limit errors, the API allows 60 requests/hour for unauthenticated requests. This is usually sufficient.

## Disable Auto-Updates

If you need to disable auto-updates:

```bash
# Remove cron job
crontab -e
# Delete the auto-update line, save and exit
```

Or comment it out:
```bash
# */5 * * * * /var/www/ai-desktop/deployment/auto-update.sh >> /var/www/ai-desktop/logs/auto-update.log 2>&1
```

## Best Practices

1. **Monitor logs regularly**: Check auto-update logs weekly
2. **Test before pushing**: Always test major changes locally first
3. **Backup before updates**: Consider automated backups
4. **Use semantic commits**: Write clear commit messages (they appear in changelog)
5. **Deploy during low traffic**: For major updates, consider manual deployment

## Advanced: Custom Update Frequency

To change update frequency, edit the cron schedule:

```bash
crontab -e
```

**Examples:**
- Every minute: `* * * * *`
- Every 5 minutes: `*/5 * * * *` (default)
- Every 15 minutes: `*/15 * * * *`
- Every hour: `0 * * * *`
- Twice daily (8am, 8pm): `0 8,20 * * *`

## Security Notes

- ✅ No SSH keys stored in GitHub (public repo safe)
- ✅ Uses HTTPS for git operations
- ✅ Read-only GitHub API access
- ✅ Runs as limited user (not root)
- ✅ Logs all update activity

## Summary

Your VPS now:
- ✅ Checks GitHub for updates every 5 minutes
- ✅ Auto-deploys new commits
- ✅ Shows changelog in the app
- ✅ Logs all update activity
- ✅ Works with public repositories
- ✅ Zero configuration needed for users

Each user can deploy their own VPS instance using the same setup!
