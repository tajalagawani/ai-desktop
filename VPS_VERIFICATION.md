# VPS Deployment Verification Guide

After pulling the refactored code to your VPS, follow these steps to ensure everything works correctly.

## 1. Pull Latest Changes

```bash
# SSH into your VPS
ssh root@92.112.181.127

# Navigate to project directory
cd /root/ai-desktop

# Pull latest changes
git pull origin lightweight-client

# You'll see the refactored structure
```

## 2. Update Dependencies

```bash
# Frontend dependencies
npm install

# Backend dependencies
cd backend
npm install
cd ..
```

## 3. Update Environment Variables

The `.env` files now use the new `storage/` directory. Update your VPS `.env` files:

### Frontend `.env`:
```bash
cat > .env << 'EOF'
PORT=3005
ANTHROPIC_API_KEY=your_api_key_here
ENCRYPTION_KEY=your_encryption_key_here
USE_CLAUDE_CLI_AUTH=false
FILE_MANAGER_ROOT=/var/www
SHOW_HIDDEN_FILES=false
AGENT_SDK_PATH=/var/www/act/agent-sdk
ACT_ROOT=/var/www/act
EOF
```

### Backend `.env`:
```bash
cat > backend/.env << 'EOF'
PORT=3006
NODE_ENV=production
CLIENT_URL=http://YOUR_VPS_IP
CORS_ORIGINS=http://YOUR_VPS_IP,http://YOUR_VPS_IP:80
LOG_LEVEL=info
FILE_MANAGER_ROOT=/var/www
DATA_DIR=../storage/data
LOGS_DIR=../storage/logs
FLOWS_DIR=../storage/flows
EOF
```

## 4. Create Storage Directory

The `storage/` directory is gitignored, so create it on the VPS:

```bash
# Create storage structure
mkdir -p storage/{data,logs,flows}

# Initialize empty data files
cat > storage/data/repositories.json << 'EOF'
{"repositories": []}
EOF

cat > storage/data/deployments.json << 'EOF'
{"deployments": []}
EOF

cat > storage/data/mcp-servers.json << 'EOF'
{"servers": []}
EOF

cat > storage/data/flow-sessions.json << 'EOF'
{"sessions": []}
EOF

cat > storage/data/mcp-tokens.json << 'EOF'
{}
EOF

# Set permissions
chmod -R 755 storage/
```

## 5. Rebuild Frontend

```bash
# Build with new structure
npm run build
```

## 6. Restart Services

```bash
# Restart all PM2 processes
pm2 restart all --update-env

# Check status
pm2 status
```

## 7. Verify Build

Check that everything compiled successfully:

```bash
# Check frontend logs
pm2 logs ai-desktop-frontend --lines 50

# Check backend logs
pm2 logs ai-desktop-backend --lines 50

# Should see no errors related to missing files or imports
```

## 8. Test the Application

### 8.1 Health Check

```bash
# Test backend
curl http://localhost:3006/health

# Should return: {"status":"ok"}
```

### 8.2 Test Frontend

```bash
# Test frontend
curl http://localhost:3005

# Should return HTML (Next.js app)
```

### 8.3 Test Nginx Proxy

```bash
# Test public access
curl http://YOUR_VPS_IP

# Should return the application
```

## 9. Verify Features

Access the application in your browser: `http://YOUR_VPS_IP`

Test each feature:

- ✅ **Desktop** - Can you see the desktop interface?
- ✅ **File Manager** - Can you browse /var/www?
- ✅ **Terminal** - Can you open a terminal?
- ✅ **GitHub App** - Can you clone a repository?
- ✅ **VS Code** - Can you create a VS Code instance?
- ✅ **Deployments** - Can you deploy an app?
- ✅ **System Monitor** - Do stats display correctly?

## 10. Check Data Persistence

```bash
# After creating some data (repos, deployments, etc.)
# Check that data is being saved to storage/

ls -la storage/data/
cat storage/data/repositories.json
cat storage/data/deployments.json
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: The import paths changed. Make sure you:
1. Pulled latest code
2. Ran `npm install`
3. Restarted PM2 with `--update-env`

### Issue: "Cannot find storage/data"

**Solution**: Create the storage directory manually (Step 4 above)

### Issue: Frontend build fails

**Solution**:
```bash
# Clear Next.js cache
rm -rf .next
rm -rf node_modules/.cache

# Rebuild
npm run build
```

### Issue: Backend can't find data files

**Solution**: Check `DATA_DIR` in `backend/.env`:
```bash
# Should be relative path
DATA_DIR=../storage/data

# Or absolute path
DATA_DIR=/root/ai-desktop/storage/data
```

### Issue: PM2 shows old file paths in errors

**Solution**: Restart PM2 with fresh environment:
```bash
pm2 delete all
pm2 start backend/server.js --name ai-desktop-backend
pm2 start npm --name ai-desktop-frontend -- start
pm2 save
```

## Expected File Structure on VPS

After setup, your VPS should have:

```
/root/ai-desktop/
├── src/                    # Source code (from git)
├── storage/                # Runtime data (created manually, gitignored)
│   ├── data/
│   ├── logs/
│   └── flows/
├── backend/
├── public/
├── docs/
├── .env
├── backend/.env
└── ... (other files)
```

## Performance Checks

```bash
# Check memory usage
pm2 status

# Check process uptime
pm2 list

# Monitor logs in real-time
pm2 logs --lines 100

# Check Nginx status
systemctl status nginx
```

## Success Indicators

✅ PM2 shows both processes as "online"
✅ No errors in PM2 logs
✅ Application accessible at http://YOUR_VPS_IP
✅ All features working correctly
✅ Data persisting to storage/data/
✅ Deployments creating logs in storage/logs/

---

## Quick Verification Script

Run this script to check everything:

```bash
#!/bin/bash

echo "=== AI Desktop VPS Verification ==="
echo ""

echo "1. Checking PM2 processes..."
pm2 status

echo ""
echo "2. Checking storage directory..."
ls -la storage/

echo ""
echo "3. Checking data files..."
ls -la storage/data/

echo ""
echo "4. Testing backend health..."
curl -s http://localhost:3006/health

echo ""
echo "5. Testing frontend..."
curl -s http://localhost:3005 | head -n 5

echo ""
echo "6. Checking logs for errors..."
pm2 logs --nostream --lines 20 | grep -i error || echo "No errors found"

echo ""
echo "=== Verification Complete ==="
```

Save this as `verify.sh`, make it executable (`chmod +x verify.sh`), and run it!

---

**Everything should work perfectly after following these steps!** 🚀
